![](https://image.3001.net/images/20191010/1570680967_5d9eb087b3ed4.jpg!small)

##  写在前面的话

**近期，ZDI的研究人员“ccpwd”在一个名叫“diskmanagementd”的macOS守护进程中，发现了一个基于堆的缓冲区溢出漏洞。diskmanagementd这个服务主要负责对磁盘驱动器进行管理和分区，用户可以通过磁盘实用工具（Disk
Utility）来与该服务进行交互。该服务将会运行一个[Mach](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html)服务器，并允许客户端使用[Mach
IPC接口](http://web.mit.edu/darwin/src/modules/xnu/osfmk/man/)来与服务器端通信（发送和接收信息）。通过这种RPC机制，客户端可以在Mach服务器中执行各种通过MIG（[Mach接口生成器](https://flylib.com/books/en/3.126.1.108/1/)）生成的功能函数。**

##  漏洞分析

所有的通信数据都需要经过[launchd](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/Launchd)，即macOS的[init](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/Init)初始化实现。关于该进程的更多细节可以通过查看其[信息属性列表文件](https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Introduction/Introduction.html)来了解，文件路径如下：

    
    
    /System/Library/LaunchDaemons/com.apple.diskmanagementd.plist

一开始，守护进程会分配一个调用函数，在之后发送和接收Mach消息时，内部进程通信将需要调用这个函数。

![](https://image.3001.net/images/20191010/1570680983_5d9eb09748f88.png!small)

在这里，[CFMachPortCreateWithPort](https://developer.apple.com/documentation/corefoundation/1400924-cfmachportcreatewithport)会分配一个函数sub_10000C241来作为负责处理Mach消息的回调函数，接收Mach消息的[地址](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html)为0x10000BE1F。根据msgh_id，Mach消息中的某个值会传送一条操作指令或函数ID，sub_10000C241会间接使用这个ID来作为两个远程函数的调度表索引。sub_100001DA2和sub_100002005分别负责启动和移除后续的通信会话。

![](https://image.3001.net/images/20191010/1570680987_5d9eb09baa10f.png!small)

Mach端口是单向通信的，这也就意味着每个发送、接收请求都需要使用单独的端口，[苹果](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html)称之为：

“端口是请求服务的客户端和提供服务的服务器之间单向通信通道的端点。如果要对此类服务请求提供答复，则必须使用第二个端口，这与Unix中的（单向）管道类似。”

![](https://image.3001.net/images/20191010/1570680991_5d9eb09fd557e.png!small)

函数sub_10000CCA9是可以通过sub_100001DA2访问到的，另一个Mach端口通过回调函数sub_10000DACC来创建，端口会保存在一个字典里，键名为“Comms-F2TPort”。缓冲区0x1000字节处用于处理Mach消息的响应，并且信息保存在字典中键名为“﻿Comms-F2T-replyarea”的位置。

![](https://image.3001.net/images/20191010/1570680996_5d9eb0a4076ec.png!small)

其中，setObject:forKey用于向字典中添加键值对：

![](https://image.3001.net/images/20191010/1570681000_5d9eb0a8b68c3.png!small)

当客户端发送一条消息时，sub_10000DACC将会被触发，然后根据msgh_id来访问MIG远程程序调用。接下来，我们将注意力主要放在函数sub_1000087C9的身上：

![](https://image.3001.net/images/20191010/1570681005_5d9eb0ad45fa8.png!small)

缓冲区溢出发生在sub_1000087C9函数中，当用户输入数据长度经过计算后偏移量超过0x1000时，便会发生缓冲区溢出。

![](https://image.3001.net/images/20191010/1570681009_5d9eb0b1b0da7.png!small)

0x1000响应缓冲区基本上为r14，用户输入从偏移量0x38处开始，所以剩下的0xfc8

字节即为用户输入区域，当输入数据填充至0xfc8处时，strlen将会返回相同的值。经过计算之后，最终的值为 0xfcc [ ((0xfc8 + 1) +
3) & 0xfffffffc]。在地址0x100008ABD处，偏移量将会变成0x1004
[0xfcc+0x38]，这里允许泄露4个字节，并写入4个字节数据，因此攻击者就可以利用这种特性来实现攻击了。但是这里的数据泄露效果不是很显著，因为大小仅为0x1000，而写入操作需要在0x1004处完成，这也就意味着程序只能从后续数据块中读取4个字节的数据。

这里有几个限制，首先是输入数据中不能包含空字符，因为这将导致strlen在空字符处停止。另一个限制是在缓冲区结束后写入的数据将始终是var_dc的内容，这部分内容就是sub
b30返回的错误代码。

![](https://image.3001.net/images/20191010/1570681014_5d9eb0b61fda5.png!small)

##  总结

分析这些类型的安全漏洞以及程序错误其实非常有趣，因为我们可以了解到一个非常小的错误如何导致一个严重的安全漏洞出现，并最终允许攻击者在目标设备上实现任意代码执行，这也就是所谓的“蝴蝶效应”吧。目前，苹果方面已经在macOS
Mojave v10.14.5中[修复](https://support.apple.com/en-us/HT210348)了这个漏洞，并于2019年7月22日正式向用户推送。

***参考来源：[zerodayinitiative](https://www.zerodayinitiative.com/blog/2019/10/3/cve-2019-8697-macos-system-escalation-via-disk-management)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

