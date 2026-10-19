## **一、** ** **前言****

近日，身边有一些朋友想转行做二进制漏洞技术研究，纠结于好不好入门？笔者本着抛砖引玉、共同进步的想法，分析一个老的二进制漏洞来帮助大家了解一下入门需要具备的一些基础知识和基本技能。比如逆向分析（汇编语言、动态调试、静态分析）、代码审计等。另一方面也督促自己“业精于勤”，多思考，多分享。

##  **二、** ** **漏洞背景****

2016年，tcpdump4.5.1版本爆出拒绝服务漏洞。漏洞产生的原因是在函数hex_and_anscii_print_with_offset()没有对无符号型变量caplength进行检查，导致在运算过程中，整数溢出，内存访问越界。

##  **三、** ** **漏洞分析****

###  **（一）** ** **漏洞环境搭建****

调试环境：os : ubuntu 18.04.1 lts

tcpdump version: 4.5.1

Libpcap version: 1.7.4

libpcap和tcpdump的下载和安装参考网上资料，下载链接附在文章最后，下载对应版本源码后， ./configure ,然后make && make
install
就可以了。安装过程中需要注意系统openssh和tcpdump可能存在的版本不兼容的问题，老版本中的接口在新版本下使用会报错，根据错误提示进行修改，重新编译安装即可。

###  **（二）** ** **pcap文件格式分析****

pcap文件格式比较简单，结构如图1所示：

![](https://image.3001.net/images/20200901/1598926490.png!small)

图1：pcap文件格式

文件头的结构体如图2：

![](https://image.3001.net/images/20200901/1598926549.png!small)

图2：文件头结构体

数据报头结构如图3：

![](https://image.3001.net/images/20200901/1598926582.png!small)

图3：数据报头结构如图

用UE打开一个.pcap文件比对各个字段的含义，可以更清晰、深刻地理解pcap文件格式。或者在linux下用xxd命令也可以查看。

###  **（三）** ** **跟踪调试分析****

####  **1、** ** **漏洞复现****

用tcpdump 运行exploit-db里poc生成的crash。poc链接：

<https://www.exploit-db.com/exploits/39875>

样本文件格式如图4下：

![](https://image.3001.net/images/20200901/1598926616.png!small)

图4：样本文件格式

执行tcpdump -r crash ,结果如图5：

![](https://image.3001.net/images/20200901/1598926640.png!small)

图5：漏洞触发崩溃

漏洞被触发，发生段错误。如果此时用wireshark打开这个crash包，wireshark也会报错，表示pcap文件有一个非常大的数据包，大小已经超过了定义的最大值0x40000。如下图6所示

![](https://image.3001.net/images/20200901/1598926678.png!small)

图6：wireshark报错

####  **2、** ** **跟踪调试****

终端进入gdb,运行到达漏洞触发的位置。由下图的崩溃信息可知，引发程序崩溃的原因是访问了不可访问的地址。错误初步定位在print_ascii.c
文件里的hex_and_anscii_print_with_offset()里。 如图7：

![](https://image.3001.net/images/20200901/1598926727.png!small)

图7：崩溃现场

此时查看内存映射如下图8，发现出错的位置0x5555559fd000正好位于内存里堆的结尾处。结合print_ascii.c源码分析，初步判定该crash是由过多循环导致越界访问而产生的。

![](https://image.3001.net/images/20200901/1598926760.png!small)

图8：内存映射

对应函数部分源码如下图9，程序在执行s2=cp++语句时候崩溃，该语句正好在一个循环里。

![](https://image.3001.net/images/20200901/1598926851.png!small)

图9：漏洞触发现场源码

此时查看栈回溯的情况如下图10：

![](https://image.3001.net/images/20200901/1598926928.png!small)

图10：栈回溯

为了进一步剖析漏洞产生的根本原因，在以上被调用的函数上分别下断点。根据调用链，可以一个个回溯函数被调用时的参数、变量情况。

#####  ** **2.1**** ** **关键函数源码静态分析****

从崩溃信息看， 指针cp在自加的过程中访问到了一个没有权限访问的地址。再次查看这部分代码如图11：

![](https://image.3001.net/images/20200901/1598926976.png!small)

图11：关键代码

指针cp处在while循环里，循环条件是nshorts >=0 ,nshorts 是由 length
/2获得的。所以关键是length长度，也就是对应的文件格式里caplen字段大小。

静态分析调用链

main-->pcap_loop->pcap_offline_read->print_packet-->ieee802_15_4_if_print->hex_and_ascii_print_with_offset

因为开源，可以直接进行源码分析。从后往前看，前面提到hex_and_ascii_print_with_offset（）函数里参数length大小没有控制，导致崩溃。接着看ieee802_15_4_if_print（）函数,
无符号整型变量caplen进行了两次运算, 当capen和hdrlen相减后，发生了整数溢出，使得caplen变成一个非常大的无符号值。如图12：

![](https://image.3001.net/images/20200901/1598927021.png!small)图12：长度计算部分

末尾执行图13：

![](https://image.3001.net/images/20200901/1598927070.png!small)图13：函数调用

函数指针调用声明，如图14：

![](https://image.3001.net/images/20200901/1598927110.png!small)

图14：函数指针调用声明

追溯ndo_default_print（)调用了hex_and_ascii_print()，如图15：

![](https://image.3001.net/images/20200901/1598927172.png!small)

图15：回溯函数调用

继续回溯hex_and_ascii_print()，如图16：

![](https://image.3001.net/images/20200901/1598927225.png!small)

图16：函数回溯

最后回到了hex_and_ascii_print_with_offset（），漏洞触发的位置。为了验证以上的分析，下面通过gdb进行动态调试进一步验证。

#####  ** **2.2 结合gdb动态跟踪****

根据栈回溯的情况，分别在以下关键函数下断点。

pcap_loop

->pcap_offline_read

->print_packet

\-->ieee802_15_4_if_print

->hex_and_ascii_print_with_offset

关键调试点：下图17中caplen是进行运算前caplen = 0x8

![](https://image.3001.net/images/20200901/1598927283.png!small)

图17：运算前的caplen长度

进行两轮运算，如图18和图19：

0x8-0x3=0x5

0x5- 0x12 = -13 =0x FFFFFFF3 (整数溢出）

![](https://image.3001.net/images/20200901/1598927367.png!small)

图18：第一轮运算后的caplen长度

![](https://image.3001.net/images/20200901/1598927407.png!small)图19：第二轮运算后的caplen长度

接着调用ndo_default_print（），如下图20所示：

![](https://image.3001.net/images/20200901/1598927479.png!small)

图20：函数调用

在该函数里调用hex_and_anscii_print()，图21：

![](https://image.3001.net/images/20200901/1598927536.png!small)

图21：函数调用

跟进hex_and_anscii_print()，直接调用hex_and_ascii_print_with_offset（），如图22：

![](https://image.3001.net/images/20200901/1598927584.png!small)

图22：函数调用

最后跟进hex_and_ascii_print_with_offset（），也就是程序崩溃的地方。函数要进行一次运算，得到nshorts值。如图23：

![](https://image.3001.net/images/20200901/1598927640.png!small)

如图23：跟踪到关键位置

运算结束后,nshorts= 0x7ffffff9，依然是一个很大的值。如图24：

![](https://image.3001.net/images/20200901/1598927687.png!small)

如图24：nshorts运算

进入循环时候,如图25：

![](https://image.3001.net/images/20200901/1598927884.png!small)

图25：nshorts循环

执行到结束：

![](https://image.3001.net/images/20200901/1598927942.png!small)

图26：程序结束，崩溃

如上图26，此时程序崩溃。

###  **（四）** ** **漏洞成因****

总结一下整个漏洞触发过程，首先tcpdump会读取恶意构造的pcap包，在构造pcap包的时候，设置一个特定的数据包长度，由于该版本的程序没有对读取的数据包大小进行检查，引起整数溢出。tcpdump会根据caplen长度去读取保存在内存空间数据包的内容，当引用到不可读取内存位置时，造成拒绝服务漏洞。

那么，在构造恶意pcap包的时候，设置多大的caplen不会导致程序直接崩溃？在本文后面扩展部分进行解答。

##  **四、** ** **补丁比较****

对tcpdump进行版本升级，升级到tcpdump 4.7.0-bp。测试环境如图27所示：

![](https://image.3001.net/images/20200901/1598928049.png!small)

图27：补丁版本

跟原始环境相比，libpcap版本不变，只是升级了tcpdump版本。在tcpdump打了补丁的情况下进行poc测试。

###  **1、** ** **原始样本测试****

运行 crash.pcap文件，如图28：

![](https://image.3001.net/images/20200901/1598928083.png!small)

图28：原始样本测试

从运行结果可见，此时程序没有崩溃，而是通过pcap_loop函数输出处理结果。下面结合tcpdump两个版本的源码进行比较。

###  **2、** ** **补丁比较****

如下图所示，相比tcpdump4.5.1而言，在tcpdump-4.7.0-bp版本print-ascii.c文件中对函数hex_print_ascii_print_with_offset关键部分做了修改，添加了对caplength大小的控制。如下图29：

![](https://image.3001.net/images/20200901/1598928132.png!small)

图29：补丁比较

通过运算，使得caplength=0,length=0。此时再处理
nshorts时候就不会无限循环，也不会产生越界访问，自然也不会崩溃。在调试跟踪的过程中，执行完上面函数后，程序会进入下一个数据包的处理，pcap_next_packet(libpcap程序里的sf_pcap.c文件中)进入判断流程。判断caplen
(17001ae0) > buffer_size(0x49) 且caplen(17001ae) >
MAXINUM_SNAPLEN(0x40000),然后进入pcap_loop(),最后snprintf()输出“bogus savefile header”
并退出。

###  **3、** ** **扩展分析****

根据前面分析的漏洞成因，只要使得无符号整形变量caplen在运算后非负，就不会发生整数溢出，程序也就不会崩溃。那么在旧版本tcpdump4.5.1环境下，如果我们通过修改poc样本文件可否缓减漏洞，不会使程序执行poc后崩溃？经过测试，是可以的。通过控制caplen字段大小来实现。它的最小值是多少呢？caplen要经过下面的计算：

caplen -= 3

caplen -= hdrlen (hrdlen=0x12)

所以为了确保caplen为非负数

caplen 最小值为0x3+0x12=0x15 (换算为十进制21）

这样，当caplen 进行两轮运算后，caplen=0,length=0,nshorts=0

不会导致无限循环。（这跟tcpdump4.7.0-bp补丁效果一样）

####  ** **3.1 caplen = 0x15****

如图30所示：

![](https://image.3001.net/images/20200901/1598928187.png!small)

图30：caplen=0x15

当caplen=0x15时， 程序没有崩溃。在执行完运算和循环后，程序会再次进入libpcap
程序sf_pcap.c中的pcap_next_packet（）数据包处理流程，根据新的数据包大小和判断条件，进入不同的判断分支，最后输出结果。

####  ** **3.2 caplen = 0x16****

![](https://image.3001.net/images/20200901/1598928226.png!small)

图31：caplen=0x16

函数调用路径：

pcap_loop--->pcap_offline_read-->pcap_next_packet-->print_packet-->pcap_next_packet-->pcap_offline_read-->
pcap_loop

跟caplen=0x15时候的数据包处理一样，通过读取pcap文件里数据包，获取数据包大小，然后进入函数处理流程，比如用数据包大小和p->buffer比较，再和maxinum_snaplen比较，最后根据比较结果进入不同的输出流程。

如果把libpcap也更新到libpcap1.8.1,那么对测试结果会不同吗？

测试结果如图32：

![](https://image.3001.net/images/20200901/1598928276.png!small)

图32：版本升级后对样本测试结果

执行后，输出结果不同。建议大家运用本文的调试思路进行跟踪分析。

##  **五、** ** **小结****

本文从漏洞分析的角度详细阐述了tcpdump4.5.1拒绝服务漏洞的成因，结合静、动态调试和补丁分析跟踪不同tcpdump和libcap版本对于pcap包的数据处理流程。分析的过程比较枯燥，需要反复的跟踪和调试，所以入行二进制漏洞研究要有苦行僧般的坚持和热爱。另外，所用到的知识也比较杂，具体到某一种类型的漏洞，要熟悉具体的文件格式或者通信协议等。除此，对各种漏洞的利用方法、平台通用性问题及各种保护机制的突破均要有研究。在漏洞分析过程中，笔者认真学习了whereisk0shl.xina1i等大牛对此漏洞分析的文章，获益匪浅。文中若有不当之处，欢迎各位大佬指正。

##  ** **参考：****

[
_https://whereisk0shl.top/post/2016-10-23-1_](https://whereisk0shl.top/post/2016-10-23-1)

[
_https://www.anquanke.com/post/id/166711_](https://www.anquanke.com/post/id/166711)

<https://github.com/the-tcpdump-group>

