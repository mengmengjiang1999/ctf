# [i春秋翻译小组-FWorldCodeZ](https://bbs.ichunqiu.com/thread-48301-1-1.html)  

# 源码级调试的XNU内核

无论你是在开发内核扩展，进行漏洞研究，还是还有其他需要进入macOS /
iOS内核，XNU，有时你需要附加调试器。当你这样做时，使用源代码执行它是非常好的。[Damien
DeVille](https://twitter.com/damiendeville)，[Snare](https://twitter.com/snare)和其他人都写过这个过程。以下是他们的一些文章：

  * [使用VMware和GDB调试Mac OS X内核](http://ho.ax/posts/2012/02/debugging-the-mac-os-x-kernel-with-vmware-and-gdb/)
  * [VMware调试二：“硬件”调试](http://ho.ax/posts/2012/02/vmware-hardware-debugging/)
  * [使用VMware Fusion GDB存根与LLDB进行内核调试](http://ddeville.me/2015/08/using-the-vmware-fusion-gdb-stub-for-kernel-debugging-with-lldb)

事情已经发生了一些变化。虽然你可以从以前的工作中完成所有工作，但有些事情没有得到解决。所以让我们从头开始详细介绍。

以下是我们的目标：

  * 从macOS环境调试macOS 10.13.6内核（10.14内核源尚未发布）
  * 使用虚拟机目标，这样我们就不必拖动两个单独的Mac
  * 不仅有内核符号，还有内核源代码
  * 能够从目标机器的内存中漂亮地打印结构
  * 在断点处，显示：
    * 来源清单
    * 注册内容
    * 回溯
    * 当前线程堆栈

## 购物清单

在我们做之前，虽然这里有你需要的东西的购物清单。

  * 来自Mac App Store的Xcode（主要用于lldb）
  * [macOS High Sierra 10.13.6安装程序](https://itunes.apple.com/us/app/macos-high-sierra/id1246284741?mt=12)
  * [Kernel Debug Kit build 17G65](https://developer.apple.com/download/more/)
  * [XNU source code for xnu-4570.71.2](https://opensource.apple.com/release/macos-10136.html)
  * 最近的版本VMware Fusion。其他虚拟化工具可能有效，但我们在这里使用VMware Fusion Pro 11。
  * Snare的excellent [Voltron](https://github.com/snare/voltron) lldb UI
  * lldb 的[x86_64 target definition file](http://llvm.org/svn/llvm-project/lldb/trunk/examples/python/x86_64_target_definition.py)

## 虚拟机

创建你的macOS来宾计算机。

  * 我推荐一个简单的用户名和密码，如“admin”和“a”
  * 你需要启用SSH并可能自动用户登录。
  * 请务必在guest虚拟机中安装VMware工具
  * 检查操作系统版本`sw_vers`。我们正在寻找17G65和xnu版本xnu-4570.71.2：

![image.png](https://image.3001.net/images/20181128/1543395136_5bfe574066deb.png!small)

​ 检查macOS构建和内核版本

为了便于SSH连接到机器，你可能需要使用VMware的DHCP以及主机名来为其提供静态IP地址`/etc/hosts`。这是如何做。

  1. 获取虚拟机网络接口的MAC地址（通常`en0`）。我的是`00:0c:29:a5:fd:3a`
  2. 编辑`/Library/Preferences/VMware Fusion/vmnet8/dhcpd.conf`（`vmnet1`如果你没有使用VMware的NAT，请替换）
  3. 为VM的静态DHCP租约添加一个节：

    
    
    ####### VMNET DHCP Configuration. End of "DO NOT MODIFY SECTION" #######
    
    host gargleblaster{
            hardware ethernet 00:0c:29:a5:fd:3a;
            fixed-address 192.168.44.10;
    }

  1. 将VM的主机名添加到`/etc/hosts`主机上
  2. 如果你愿意，可以在Sharing.prefpane以及命令行中使用设置来宾VM的主机名 `scutil --set HostName`
  3. 使用ssh密钥将ssh密钥复制到vm `ssh-copy-id`
  4. 关闭VM，退出并重新启动VMware，然后启动VM以测试所有内容。
  5. 将VM引导至恢复模式并使用禁用SIP `csrutil`

## VMware的GDB stub

调试XNU的官方方法是使用内置的调试存根，使用内核调试协议或KDP进行通信。它可以在各种传输上工作，包括串行，FireWire，我相信Thunderbolt。但是对于调试VM，你要使用UDP，这对于内核调试来说是超级好的。`lldb`经常不同步或失去与调试服务器的联系，并且内核处于永久停止状态。我认为这是因为调试服务器是内核本身的一部分，结合了UDP不可靠的特性。所以内核停止，停止与调试器通信，然后`lldb`放弃。

更可靠的机制是VMware提供的“硬件”调试工具。这使VM可以模拟内核下的硬件调试器。在这种情况下，内核在自己的调试中不起作用;
它甚至没有“意识到”它正在被调试。这种方法不是100％可靠，但它通常比KDP更稳定。你也可以（通常）使用^
C中断，就好像你已连接到正常的用户空间进程一样。设置很简单：

继续关闭VM。然后编辑`.vmx`在`.vmwarevm`捆绑包中找到的文件。将以下第[1](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:1)行添加到文件中：

    
    
    debugStub.listen.guest32 = "TRUE"
    debugStub.listen.guest64 = "TRUE"

如果要从主机以外的计算机（例如另一个来宾VM）进行调试，则可以添加远程侦听器：

    
    
    debugStub.listen.guest32.remote = "TRUE"
    debugStub.listen.guest64.remote = "TRUE"

## 内核调试工具包

从[Apple Developer
Portal](https://developer.apple.com/download/more/)下载内核调试工具包。下载与VM中的macOS构建相匹配的KDK构建版本至关重要。我相信你需要使用Apple
ID登录开发人员门户网站，但我认为你不需要为开发者帐户付费。

你需要在主机和来宾中安装KDK。从技术上讲，只需将开发内核复制到guest虚拟机即可，但只需简单地安装整个KDK即可。

在guest虚拟机中，将开发内核从KDK位置复制到内核所在的目录：

    
    
    $ sudo cp /Library/Developer/KDKs/KDK_10.13.6_17G65.kdk/System/Library/Kernels/kernel.development /System/Library/Kernels/
    

由于系统实际上并不启动内核，而是预先链接的内核缓存，因此需要使现有内核缓存无效，从而导致重建。该`kextcache`命令执行此操作。它有很多选项，但为了简单起见，你可以告诉它“重新启动你在启动卷上所知道的一切”
[2](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:2)：

    
    
    $ sudo kextcache -i /

值得在KDK中寻找安装它的东西。看看`/Library/Developer/KDKs/KDK_10.13.6_17G65.kdk`。在其中，你会发现很多内核和kexts的符号包，这非常好。不过，你不必担心它们。LLDB将使用Spotlight通过UUID找到它们，并在需要时加载它们。真正有趣的是内核dSYM。其中有大量的Python
lldb宏。LLDB加载其中一些，但大多数不加载。它们大部分都没有记录，但有些非常有用。我们稍后会看几下。

## 引导args

有些指南会让你在访客中设置各种启动参数，例如`kcsuffix`。根据我的经验，你无需执行任何特殊操作即可启动开发内核。只要它存在（或者更重要的是内核缓存存在），它将优先于发布内核。重新启动VM并检查内核版本以确保启动了Development内核：

    
    
    admins-Mac:~ admin$ uname -a
    Darwin admins-Mac.local 17.7.0 Darwin Kernel Version 17.7.0: Thu Jun 21 22:53:14 PDT 2018; root:xnu-4570.71.2~1/DEVELOPMENT_X86_64 x86_64

你还可以在`debug=`引导arg [3 ](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:3)[4中](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:4)设置各种调试标志，但不需要它们。它们不会以任何方式影响VMware的gdb服务器存根。但是，如果你在VMWare的调试存根之外使用kdp，它们可能会很有用。标志是一个位域，其值与OR一起。例如，`debug=0x1`告诉操作系统在启动时暂停并等待调试器。可能一组有用的标志开头是`debug=0x141`。Apple
[在这里](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/build/build.html)有部分调试标志列表，如果找不到满足你需求的调试标志，[`osfmk/kern/debug.c`](https://opensource.apple.com/source/xnu/xnu-4570.71.2/osfmk/kern/debug.c.auto.html)可能是你的下一个最佳参考。你还可以在内核源中检查调试引导arg的其他位置grep其他：

    
    
    -==< zach@endor:~/src/xnu-4570.71.2 >==-     (0) $ grep -rn 'PE_parse_boot_argn\(\"debug\"' .

## 设置LLDB

为了`lldb`理解我们正在调试的东西，我们需要给它一些配置。如果你还没有，请创建一个`~/.lldb`目录来保存某些`lldb`特定文件。`~/.lldbinit`如果你还没有空文件，也要创建一个空文件。

把`x86_64_target_definition.py`你先前下载的内容放在这里。当你进行任何其他一般的lldb调整或python脚本时，你也可以进入这里。然后你可以从你的来源获取它们`.lldbinit`。

有一些构建/内核版本特定的配置，所以它不能都是共同的`.lldbinit`。我喜欢有一个git repo来跟上我的各种lldb
init脚本，但是现在，让我们假设你正在创建`~/.lldb/kernel-debugging`。

首先，我们需要告诉`lldb`我们正在调试x86_64目标。`lldb`非常灵活，可以调试各种目标架构，甚至是之前从未听说过的架构。目标定义文件描述了该体系结构。不应该`lldb`知道开箱即用的x86_64？是的，它通常会，但不幸的是，我们要连接的远程gdb存根不能告诉我们的调试器它正在调试什么架构。所以我们提前告诉调试器。将此添加到特定于内核的lldb
init脚本：

    
    
    settings set plugin.process.gdb-remote.target-definition-file ~/.lldb/x86_64_target_definition.py

说到x86，你可能想要将反汇编的风格设置为英特尔，而不是AT＆T。你懂。因为你是一名专业人士：

    
    
    settings set target.x86-disassembly-flavor intel

还记得dSYM包中的那些python脚本吗？现在我们需要告诉`lldb`他们自动加载它们（或者至少是它所需要的那些加载它们）。

    
    
    settings set target.load-script-from-symbol-file true

KDK参考内核中的dSYM源自Apple构建内核时的任何位置。这通常就像是`/BuildRoot/Library/Caches/com.apple.xbs/something/something`。当然`lldb`无法在该路径上找到内核源代码（除非你把它们放在那里），所以我们需要告诉它要翻译。以下设置适用于此构建，但其他内核的路径可能不同。查找来自的错误消息`lldb`。

    
    
    settings set target.source-map  /BuildRoot/Library/Caches/com.apple.xbs/Sources/xnu/xnu-4570.71.2 /Users/zach/src/xnu-4570.71.2

我们需要`lldb`从内核dSYM加载一些超级有用的宏。应该拿起来`xnu.py`，但还有更多`memory.py`。

    
    
    command script import "/Library/Developer/KDKs/KDK_10.13.6_17G65.kdk/System/Library/Kernels/kernel.development.dSYM/Contents/Resources/Python/lldbmacros/memory.py"

你可以配置许多其他设置`lldb`，其中大多数默认为合理的设置。检查`help
settings`列表。请特别注意名称中带有“darwin”的设置。在某些情况下，可能很难找出可用于设置的可能值。在这种情况下，咨询`lldb`
[来源](https://lldb.llvm.org/source.html)可能是最容易的。

此时，你的`.lldb/kernel-debugging`脚本应该类似于：

    
    
    #帮助lldb弄清楚我们正在调试x86_64
    settings set plugin.process.gdb-remote.target-definition-file ~/.lldb/x86_64_target_definition.py
    
    #使用合理的反汇编语法
    settings set target.x86-disassembly-flavor intel
    
    #告诉加载隐藏在.dSYM文件中的任何lldb脚本和宏
    settings set target.load-script-from-symbol-file true
    
    #告诉lldb源目录到底在哪里
    settings set target.source-map  /BuildRoot/Library/Caches/com.apple.xbs/Sources/xnu/xnu-4570.71.2 /Users/zach/src/xnu-4570.71.2
    
    #这应该在我们设置目标可执行文件时自动加载
    #命令脚本导入
    "/Library/Developer/KDKs/KDK_10.13.6_17G65.kdk/System/Library/Kernels/kernel.development.dSYM/Contents/Resources/Python/lldbmacros/xnu.py"
    
    #这似乎没有自动加载，所以我们在这里加载它。
    command script import "/Library/Developer/KDKs/KDK_10.13.6_17G65.kdk/System/Library/Kernels/kernel.development.dSYM/Contents/Resources/Python/lldbmacros/memory.py"
    
    # 加载我们将要调试的内核二进制文件。
    target create /Library/Developer/KDKs/KDK_10.13.6_17G65.kdk/System/Library/Kernels/kernel.development

启动VM后，如果运行`lldb`（没有目标二进制文件），则会得到基本`(lldb)`提示。现在使用以下内容获取内核调试脚本

    
    
    command source ~/.lldb/kernel-debugging

![image.png](https://image.3001.net/images/20181128/1543395202_5bfe5782a71c4.png!small)

如果你已经正确设置了一切，你应该能够连接`gdb-remote`命令：

    
    
    (lldb) gdb-remote 8864

你应该进入内核，可能是在空闲线程的中间。假设`lldb`发现内核，符号和源代码没问题，你应该在断点处看到一个简短的源代码片段：

![image.png](https://image.3001.net/images/20181128/1543395214_5bfe578ee2a65.png!small)

我不确定是什么决定了调试器进入的线程。我怀疑这只是机会。如果你的计算机繁忙，你可能会进入一个非空闲的线程，甚至可能在内核扩展中执行。在这种情况下，你将在一个没有源代码的地方。尝试在经常调用的内核函数上设置断点，例如`dofileread()`并继续。

    
    
    (lldb) breakpoint set -n dofileread

如果你正确地破坏了内核而不是扩展，那么你应该看到源代码。

此时应冻结VM。试着`c`继续跑步; VM应该再次交互。看看^ C是否中断。

要从VM分离，请执行以下操作：

    
    
    (lldb) c
    Process 1 resuming
    (lldb) detach
    Process 1 detached
    (lldb) target delete
    1 targets deleted.
    (lldb) quit

我发现我的lldb命令历史记录无法可靠地保存[5，](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:5)除非我经历了分离，删除目标和退出的整个过程。在分离之前，你可能希望清除任何断点`breakpoint
delete`。分离应该清除断点，但根据我的经验它并不总是，然后你的目标可以随机挂起。

## 漂亮的Printing 结构

如果你能够按名称打破函数并显示源代码，那么你应该将所有设置为漂亮的Printing结构和来自内核内存的其他对象。这对于具有大量C宏和条件定义的非常大的结构特别有用。打印它们可以`lldb`让你轻松查看结构的实际组成方式。

这是一个简单的例子。设置断点`dofileread()`：

    
    
    (lldb) breakpoint set -n dofileread                                                            
    Breakpoint 1: where = kernel`dofileread + 51 at sys_generic.c:359, address = 0xffffff8015f46eb3
    (lldb) c

调试器应该立即打到你的断点; 文件读取是一种超常用的操作。当它发生时，你应该看到`lldb`函数原型的视图：

    
    
    kernel`dofileread(ctx=0xffffff8ce861bf00, fp=0xffffff8028c332e8, bufp=140465093751296, nbyte=65536, offset=-1, flags=0, retval=<unavailable>)

尝试用`print`命令打印一些函数参数。你会看到它`ctx`是类型`vfs_context_t`（实际上是一个typedefed指针），并且`fp`是类型`fileproc
*`。要打印这些结构，你需要将`lldb`它们作为指针进行解释并取消引用它们：

    
    
    (lldb) print ctx
    (vfs_context_t) $44 = 0xffffff8ce861bf00
    (lldb) print *(vfs_context_t)ctx
    (vfs_context) $45 = {
      vc_thread = 0xffffff802a029a10
      vc_ucred = 0xffffff8024d14520
    }
    (lldb) print fp
    (fileproc *) $46 = 0xffffff8028c332e8
    (lldb) print *(fileproc *)fp
    (fileproc) $47 = {
      f_flags = 0
      f_iocount = 1
      f_fglob = 0xffffff802ffc9960
      f_wset = 0x0000000000000000
    }

这是它的实际截图：

![image.png](https://image.3001.net/images/20181128/1543395245_5bfe57ad25275.png!small)

## 建立Voltron

所以我们用符号和源代码成功调试内核。但是`lldb`并没有给我们太多的用户界面。如果我们能够看到更多的上下文，如寄存器，堆栈，指令指针的反汇编，当前线程的回溯，那就太好了。你懂。调试器做的事情。那么，而不是用户界面，`lldb`为你提供API。我想如果我必须在半实现的用户界面和非常好的API之间做出选择，我会选择后者。这就是我们如何获得Snare的Voltron。

如果你还没有，请从<https://github.com/snare/voltron>获取Voltron
。你很想安装它`pip`，但不要。使用包含的`install.sh`shell脚本代替[6](https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel/#fn:6)。此脚本指出你安装的调试器以及它们使用的Python版本。它还有助于解决Voltron的`six`依赖与使用Python系统安装的依赖之间的冲突。

完成安装后，它应该在你的附加中添加类似于以下内容的行`.lldbinit`：

    
    
    command script import /Users/zach/Library/Python/2.7/lib/python/site-packages/voltron/entry.py

确保它在那里。还要确保将`bin`上面使用的任何Python路径下的目录添加到shell中`$PATH`。例如：

    
    
    export PATH=$PATH:$HOME/Library/Python/2.7/bin

现在，在单独的终端窗口（或`tmux`窗格或其他）中，你可以启动单独的Voltron视图。在主窗格中，`lldb`正常启动。然后根据你的选择配置你的voltron窗格。`voltron
view registers`例如，从shell运行中，可以查看在每个断点处更新的寄存器。这是帮助输出：

    
    
    $ voltron view -h
    usage: voltron view [-h]
                        {backtrace,t,bt,back,registers,r,reg,register,breakpoints,b,bp,break,command,c,cmd,memory,m,mem,disasm,d,dis,stack,s,st}
                        ...
    
    optional arguments:
      -h, --help            show this help message and exit
    
    views:
      valid view types
    
      {backtrace,t,bt,back,registers,r,reg,register,breakpoints,b,bp,break,command,c,cmd,memory,m,mem,disasm,d,dis,stack,s,st}
                            additional help
        backtrace (t,bt,back)
                            backtrace view
        registers (r,reg,register)
                            register values
        breakpoints (b,bp,break)
                            breakpoints view
        command (c,cmd)     run a command each time the debugger host stops
        memory (m,mem)      display a chunk of memory
        disasm (d,dis)      disassembly view
        stack (s,st)        display a chunk of stack memory

这是我的设置。为巨型截图道歉。

![image.png](https://image.3001.net/images/20181128/1543395264_5bfe57c06ced9.png!small)

就是这样。你正在使用符号，源和Voltron调试macOS内核。

务必向我[发推文](https://twitter.com/zcutlip)任何评论或更正。

* * *

  1. 我相信你真的只需要64位调试存根，但我添加了两者。

  2. 如果要卸载开发内核并返回发布内核，则需要：

    1. 删除以下内容/System/Library/
    * `Kernels/kernel.development`
    * `PrelinkedKernels/prelinkedkernel.development`
    * `Caches/com.apple.kext.caches/Startup/kernelcache.development`
    1. 像以前一样使内核缓存失效
  3. 你将尝试启用不可屏蔽中断或NMI调试标志，以便你可以通过按键暂停内核。我会救你的麻烦。它不适用于VM。你的主机每次都会捕获NMI。我惊慌失措地试图解决这个问题。我认为没有办法模拟VM中的NMI。

  4. 调试标志不会以任何方式影响VMware的调试存根。同样，内核甚至都不知道它。它们仅配置内核自己的KDP调试存根。也就是说，它们可以很有用，因为它们为你提供了第二种附加调试器的方法。例如，如果系统在断点之间发生混乱，你通常无法从VMware存根中反省恐慌情境。但是你可以将第二个`lldb`会话附加到KDP存根以查看恐慌情况。

  5. 一旦你弄清楚各种`lldb`咒语，你就不想再想出来了。所以你想要你的命令历史。

  6. 他亲自告诉我这件事。我认为他让Voltron保持在PyPI只是为了搞砸新手。

作者:shadowfile

翻译:i春秋翻译小组-FWorldCodeZ

责任编辑：F0rmat

翻译来源:<https://shadowfile.inode.link/blog/2018/10/source-level-debugging-the-xnu-kernel>

##  

