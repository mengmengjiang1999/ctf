# 深入分析Ewon Flexy物联网路由器（上）

阅读量 **275919**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-06-24 11:30:31

 **x**

##### 译文声明

本文是翻译文章，文章原作者 pentestpartners，文章来源：pentestpartners.com

原文地址：<https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01c5aee73101c0f4f0.png)

## 0x00 前言

首先我想感谢PTP技术人员在我研究过程中提供的帮助，有许多知识我并不掌握，因此有时候我会请求外援帮助。

我从这次研究中也学到了很多知识，比如XOR的工作原理、如何使用IDA来更好地分析ARM程序，因此我想与大家一起分享这些心得。我列出了整个过程中的一些要点以及需要避免的坑，可供大家参考。

如果大家觉得本文内容过于冗长，可以参考另一篇[精简版](https://www.pentestpartners.com/security-blog/sharing-the-secrets-pwning-an-industrial-iot-router/)。

此次研究并非付费测试或者专门针对该设备的评估，因此我们在研究过程中也多次披露相关公告。

先前在某次客户评估测试中，我们发现某个产品关联了其中一款设备。虽然该设备不在客户要求的测试范围中，但我还是对这款设备非常感兴趣。

本次“深入分析”完全从黑盒测试角度出发，也就是说，我们并没有得到关于该设备的任何信息以及授权凭据。

## 0x01 Ewon IoT 200 Flexy路由器

![](https://p5.ssl.qhimg.com/t0189a84815ae2d7115.png)

这些设备的分布范围非常广泛，根据Ewon的官方描述，这些设备在全球的部署情况如下图所示：

![](https://p2.ssl.qhimg.com/t015e1cabc0a08d8d6c.png)

Shodan的统计信息如下：

![](https://p5.ssl.qhimg.com/t0116df1f4541d29c97.png)

结果看起来也不错。Shodan虽然不是百分百完美，但也能覆盖到许多地址。

此外，Ewon设备似乎由HMS Industrial Networks制造。HMS Networks
AB是一家工业通信领域的国际公司，其座右铭是“Connecting
Devices”（设备互联）。HMS总部坐落在瑞典哈尔姆斯塔德（Halmstad），已在纳斯达克北欧证券交易所上市，在10个国家拥有500多名员工，2016年的销售额为1.01亿欧元（来源：<https://www.hms-networks.com/products-solutions>）。

现在让我们开始深入分析。

## 0x02 Web接口

准备好设备，插上电源，静待设备进行默认IP配置。

该设备的默认IP地址为`10.0.0.53`，默认账户为：

    
    
    用户名: adm
    密码: adm
    

回头我们再来讨论这一点。

> 备注：撰写本文时我已经更新到最新的固件，这样Ewon就不会找老版本固件的借口。

## 0x03 WEB：基本认证

Ewon web服务使用基本认证（Basic Authentication）来验证用户身份，如下所示：

![](https://p2.ssl.qhimg.com/t01cd3f7e685285ad53.png)

认证流量基于HTTP协议（非HTTPS），后续分析中我们要用到这一点。

> 备注：基本认证并不安全，应用程序不应当使用这种机制。

## 0x04 WEB：XSS

面对符合ISO 27001标准的设备，作为最纯粹的黑客，大家应该猜到接下来我们要尝试哪些操作：

![](https://p5.ssl.qhimg.com/t013d73b41f75a713bd.png)

![](https://p0.ssl.qhimg.com/t015aca135416ca48c8.png)

由于基本认证的base64 cookie比较脆弱，因此，这里我们可以窃取一些凭据信息。

但稍等片刻，貌似Ewn已经知道这些问题（在2015年），实际上Ewon掌握了更多信息，在某次安全公告中，Ewon似乎修复了某些问题：

> **Ewon sa Industrial router – Multiple Vulnerabilities** : Karn Ganeshen
> （@juushya）
>
> 公布时间：2015年12月24日 – <https://seclists.org/fulldisclosure/2015/Dec/118>

Karn在web接口方面发布了许多信息，这里我想换个方向研究。

## 0x05 WEB：敏感数据存储及获取主解密秘钥

研究表明，一旦我们具备该设备的访问权限（不管是通过XSS窃取凭据还是使用默认凭据（`adm:adm`）），我们基本上能执行各种操作。之前我没考虑到的一个点就是管理员账户与较低权限用户账户之间的授权隔离。

在观察web应用或者访问存储敏感信息（如VPN私有证书、秘钥或者用户密码）的文件时，我发现这些数据似乎使用之前没见到过的方式进行加密。这一点很有意思，因此我进一步研究底层原理。

输入敏感信息并保存到配置数据中后，经过身份认证的用户可以看到如下内容：

![](https://p4.ssl.qhimg.com/t0164bc1d4ad06273ca.png)

![](https://p1.ssl.qhimg.com/t01c1cd50c403903898.png)

我们也可以通过POST请求，获取经过加密的VPN私有证书（请记住我们能获取到凭据信息）：

![](https://p4.ssl.qhimg.com/t0161f4d1891c936b04.png)

先别管这么多，让我们分解这个字符串，开始解决问题。

我们首先处理密码字符串，这个字符串目前还比较小，处理方法同样可以应用于更长的VPN证书及密钥字符串。

比如，`admin`用户对应的用户名及已存储的密码输出结果如下：

    
    
    [“ptp”,”#_1_EHyXHCXlKSnkcW2f7kthnIg=”]
    

这里如果大家眼睛亮一点，能看到这段数据由一个前缀和经过base64编码的值所组成，其中：

    
    
    “#_1_” = 前缀
    “EHyXHCXlKSnkcW2f7kthnIg=” 经过Base64编码的值
    

不幸的是，解码后的数据不能直接使用：

![](https://p2.ssl.qhimg.com/t01ebc388771f51a41d.png)

情况不是特别妙，我想知道实际的密码是什么。

其实我已经通过XSS/不安全的HTTP通信数据获取到了密码，但一旦我能解密这个值，我是否也能解密出VPN私钥呢？

我往Ewon路由器中添加了另一个用户，将密码设置为路由器能接受的最短值：`aaa`。

这个测试用户的密码会被加密成`#_1_BXWfyGY=`。删除前缀并解码base64数据后，我们可以得到看起来像是随机的数据：`.u.Èf`。

似乎路由器在解码后的字符串末尾添加了其他字符，因为我们的原始密码只有3个`a`，这是比较奇怪的行为。

在不充分理解加密算法的情况下，我决定将密码修改成`aba`，看是否有什么变化。加密后的结果变成了`#_1_BXafyJY=`。

这里显然有点相关性：

    
    
    “BXWfyGY=” = aaa
    “BXafyJY=” = aba
    

注意到前两个字符相同，这是否意味着路由器会逐个加密每个字符？

让我们再次修改密码，改成`aab`：

    
    
    “BXWfyGY=”-> “.u.Èf” = “aaa”
    “BXafyJY=” -> “.v.È.” = “aba”
    “BXWciGc=” -> “.u..g” = “aab”
    

我在密码方面不够熟练，因此我请求了小伙伴的帮助。经过探讨后，我们一致认为路由器会逐个字符加密，然后在末尾添加一些数据。这里我们提到了一个算法：XOR（异或）。

接下来轮到CyberChef上场了。

我们知道密码长度为`3`，且明文密码为`aaa`，因此我们可以在[CyberChef](https://gchq.github.io/CyberChef/)中输入相应参数，开始操作：

![](https://p1.ssl.qhimg.com/t010780e44d7b078fda.png)

很好！虽然末尾还有两个结尾字符，但先别去管这个。来看看我们是否能用这种方法处理完整的包含22个字符的密码。

答案是肯定的，不过在CyberChef上执行这种操作较为费劲（要计算`9.578097130411805e+52`个值），因此我们写了个python脚本来处理并保持运行：

![](https://p3.ssl.qhimg.com/t012783a358fb672f19.png)

结果不错，这个方法能不能适用于PTP用户的原始密码呢？

![](https://p4.ssl.qhimg.com/t01c0842b22992131a6.png)

的确如此，并且这种方法也能适用于私钥数据：

![](https://p5.ssl.qhimg.com/t013fb5a31dbbde6e58.png)

我们还在（手头上的）许多Ewon Flexy设备上尝试了这种方法，屡试不爽。

这意味着什么？在进一步研究之前，我们可以稍微总结下：

**目前我们可以通过XSS窃取合法用户的凭据，如果我们与目标处于同一个LAN中，我们还能抓取经过加密的敏感数据，然后解密该数据（比如其他用户的密码、VPN私钥以及配置数据）等。我们可以使用存储在配置数据中的私钥和密码来连入已有的VPN链路中（我们配置了一条链路，并且尝试成功）。**

我们将这个信息反馈给Ewon，并且得到了与Karn类似的官方回应。显然我们需要通过身份认证才能让这种方式更有价值（如果不存在XSS点，并且目标使用的是HTTPS时我们就无能为力，因此我同意这个说法）。此外，这些设备也不应该连接到互联网中。

好戏还在后头。

## 0x06 WEB：默认凭据

现在让我们回到默认凭据上，Ewon默认凭据其实可以算是公开的秘密，这在初次安装设备时没有问题。当我们使用设置向导时，系统会预先给我们设置用户名和密码，具体值大家可以猜到：`adm:adm`。

![](https://p1.ssl.qhimg.com/t01bef448b226dd7f2f.png)

我觉得Ewon在这里应该设置一些校验机制，避免人们使用默认凭据，直接无脑下一步。

现在，结合Ewon的产品销量数据以及Shodan.io上的搜索结果，我们可以自己估计一下有多少人修改过默认凭据。

我认为这个数量不会太多。

此外，这些凭据同样适用于运行在同一个节点上的FTP服务：

![](https://p2.ssl.qhimg.com/t013d85778bf0250e52.png)

**默认情况下，web服务和ftp服务对应的端口为80及21，此外，web服务还对应另一个端口（81），后面我们再讨论这一点。**

## 0x07 硬件

现在让我们从硬件角度研究一下这款设备。

这是一款IoT设备，包含各种有用的功能，因此我觉得肯定存在各种各样的问题。

拆解Ewon Flexy设备，将主板剥离出来。这看上去是外围板/子板的一个单控制器，背面插着一个OS板。

![](https://p2.ssl.qhimg.com/t018c6ed74903e0e994.png)

主板上为子板预留了4个插槽，还有一个SD卡槽以及4个ETH口：

![](https://p5.ssl.qhimg.com/t01114dfe27ccf286a8.png)

背面有个OS板槽以及若干个测垫（test pad）。

![](https://p5.ssl.qhimg.com/t01bae85dece5477f25.png)

比较有意思的是OS板上的NAND Flash、OS板左上角的测垫（2×5的圆形焊点）以及主板背板上靠近盒式插槽的3个测垫（靠近TP12）。

## 0x08 硬件：JTAG

当看到2×5的圆形测垫时，我立刻想到了“JTAG”。实话实说，初始测试及开发主板时使用该工具也非常正常。大家可以看到左上角有个2-20插槽连接器，我猜测这个连接器可以用来快速连接到JTAG编程器，烧录设备。

我在每个测垫上焊接导线，启动[JTAGulator](http://www.grandideastudio.com/jtagulator/)。

![](https://p2.ssl.qhimg.com/t019abf590da2aff6d1.png)

这里别在意五颜六色的导线，这是我手头上仅有的材料。

事实证明这就是JTAGulator可用的引脚。

![](https://p2.ssl.qhimg.com/t015a9846794040af1f.png)

提取设备ID，结果如下所示：

    
    
    JTAG > d
    TDI not needed to retrieve Device ID.
    Enter TDO pin [1]:
    Enter TCK pin [4]:
    Enter TMS pin [2]:
    All other channels set to output HIGH.
    Device ID #1: 0000 0001001010000001 00000100001 1 (0x01281043)
    -> Manufacturer ID: 0x021
    -> Part Number: 0x1281
    -> Version: 0x0
    

Google搜索一番后，看起来这是一款莱迪思（Lattice）半导体设备，而不是ATMEL（参考[此处](http://bsdl.info/details.htm?sid=89730f33d939207188ca59b002289d77)详细信息）。

很快JTAG枚举及连接就被中断，我不清楚具体原因。

    
    
    > halt
    halt
    Halt timed out, wake up GDB. timed out while waiting for target halted
    

## 0x09 硬件：串口

接下来我开始分析看上去比较有趣的另一组测垫。看上去这3个测垫像是串口（Serial）或者SWD，因此我首先需要将Saleae Logic
Analyser连接到这3个引脚。

我们可以通过设备底部访问这3个引脚，切开外壳会更方便些。

![](https://p1.ssl.qhimg.com/t01a3e492f41e67df0e.png)

将一些导线焊接到测垫上，连接到Saleae，观察是否能得到一些信息：

![](https://p5.ssl.qhimg.com/t01d38b096b45f861bb.png)

放大后的局部图像如下：

![](https://p4.ssl.qhimg.com/t0197b07eb52c45d9a8.png)

这应该是BootLoader！

现在我需要与设备交互。我拆开了USB转串口连接设备，引出导线，使用终端连接到该设备：

![](https://p1.ssl.qhimg.com/t015174a7182cd7bcd0.png)

这是`Linux-3.2.11`，我们可以尝试停止启动进程，希望能拿到一个shell：

    
    
    MMC: mci: 0
    In: serial
    Out: serial
    Err: serial
    Net: macb0
    Hit any key to stop autoboot: 0
    Net: enable eth switch
    U-Boot> help
    U-boot console is locked
    U-Boot> ?
    U-boot console is locked
    U-Boot>
    

接下来怎么办？试一下运气好不好：

    
    
    U-Boot> unlock pw
    Var pw not def
    U-boot console is locked
    

看上去希望更大了一些，但这里困扰了我一段时间，回头我们再讨论这一点。

## 0x0A 硬件：导出NAND Flash

研究受阻后，我剥离出NAND
Flash，将其与DATAMAN读取器连接。几分钟后，我成功导出了Flash。为了确保数据准确，我执行了两次导出操作，两次导出结果都比较理想。

![](https://p2.ssl.qhimg.com/t01fc2b9eb3397d5be2.png)

拿到NAND转储文件后，我们可以开始深入分析提取出的固件，了解文件结构（希望一切顺利）。

首先我下载如下工具，这是处理NAND转储文件的首选工具：

<https://bitbucket.org/jmichel/tools/src/default/>

我在Google上搜了一下NAND
FLASH芯片组MT29F1G08ABADA。虽然该芯片能够处理1G存储空间，但我们手上的这一款并没有这么大容量，读取器拿到的NAND转储数据只有138.4MB。

这个操作比较繁琐，感谢PTP的Dave（@tautology0）指引我走向正确的方向。

![](https://p0.ssl.qhimg.com/t01e56dd1b51cd51ac1.png)

接下来看Binwalk的处理结果：

![](https://p1.ssl.qhimg.com/t015a05626cd961d357.png)

文件中有许多有趣的点。首先来看一下UBI。我们使用DD从`dump.bin`文件中提取这部分数据：

![](https://p1.ssl.qhimg.com/t01dfcef6f1ac057a8c.png)

非常好，来看一下实际内容：

![](https://p1.ssl.qhimg.com/t011d65df4f4e108c72.png)

内容也正确，继续研究：

![](https://p3.ssl.qhimg.com/t0174cdd04d5517b761.png)

现在我们已经成功提取出固件，看起来我们已经拿到根文件系统以及Ewon Application文件系统。

我准备先分析根文件系统，这样能更好理解Ewon系统的构建方式。

其实只有`init.d`中的一个文件比较有意思，这个文件的功能就是启动Ewon服务。没有其他用户、没有ssh私钥、没有密码哈希。

接着开始分析Ewon SquashFS。

SquashFS文件结构貌似非常贴合Ewon环境，挂载目录为`/opt/ewon`。

我提取出的大多数文件目录都为空，除了`bin/`及`patch/`目录，其中包含一些有价值的信息。`patch/`目录如下：

![](https://p4.ssl.qhimg.com/t0128c8b3d2b22838da.png)

这些文件位于`patch/`目录中，是最近一次固件更新所使用的更新文件，还包含更新的一些二进制文件、程序库等。

![](https://p4.ssl.qhimg.com/t01f16c09717c71c6f4.png)

其他大多数都价值不大，但可以看出设备更新中经常会添加一些linux-arm程序及程序库。

根据Andrew（[cybergibbons](https://twitter.com/cybergibbons)）给的提示，我扫描了文件结构，看是否存在可执行脚本（bash脚本）：

![](https://p3.ssl.qhimg.com/t012f2ec7cb175da13a.png)

这两个文件是基本的bash脚本，只包含版本信息，现在并不是特别有价值。

![](https://p2.ssl.qhimg.com/t0148cfd0531f91dbce.png)

继续查看`bin/`目录：

![](https://p3.ssl.qhimg.com/t0193959eef6c5f3bd7.png)

现在事情变得有趣起来。我们已经拿到二进制文件、一些配置脚本以及一些bash脚本，还有一些貌似是Java程序以及jar文件。我们首先来看一下配置文件，最后再分析Ewon二进制文件。

配置文件非常简单，只适配了几个不同的环境：[At91sam9g](https://www.microchip.com/design-centers/32-bit-mpus/microprocessors/sam9)、QEMU（可能是用来调试）以及RaspberryPi（调试及编译）。

这些配置文件非常相似，大多数值都相同，只有名称和os依赖项有点出入。

`all_config.conf`文件示例如下：

![](https://p4.ssl.qhimg.com/t017c3ce32769cc3948.png)

根据第二行，这是所有产品的共同组件（“Common part to all product”），也列出了Flexy和Cosy
Ewon产品，这是否意味着这两款是同一个产品？

![](https://p5.ssl.qhimg.com/t0194c7c7b0074db7b5.png)

这两个产品有很多相似性，也有一些比较大的差异。

根据网页描述：“（该设备）能通过互联网提供便捷的远程访问”，此外还用到了443端口（HTTPS）。那么为什么Cosy使用https，而Flexy没有呢？

我尝试运行Java程序，虽然运行错误，但也提供了其他一些文件的信息：

![](https://p5.ssl.qhimg.com/t01fd395421222698d6.png)

使用[JD-Gui](https://java-decompiler.github.io/)，我反编译JAR文件进行分析：

![](https://p2.ssl.qhimg.com/t010ca4e6c0d93139f2.png)

后面我们再来研究这个点，现在我们可以先来分析Ewon二进制文件。

本文翻译自pentestpartners.com [原文链接](https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/180831](/post/id/180831)

安全客 - 有思想的安全新媒体

本文转载自: [pentestpartners.com](https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/)

如若转载,请注明出处： <https://www.pentestpartners.com/security-blog/ewon-flexy-iot-router-a-deep-dive/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [物联网](/tag/物联网)
  * [IoT](/tag/IoT)
  * [路由器](/tag/路由器)
  * [Ewon Flexy](/tag/Ewon Flexy)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

