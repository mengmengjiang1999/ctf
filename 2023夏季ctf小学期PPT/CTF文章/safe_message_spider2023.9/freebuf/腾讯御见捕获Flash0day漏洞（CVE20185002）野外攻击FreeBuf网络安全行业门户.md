***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 0x1 概述

**腾讯御见威胁情报中心近日监控到一例使用Adobe Flash
0day漏洞（CVE-2018-5002）的APT攻击，攻击者疑通过即时聊天工具和邮箱等把恶意Excel文档发送给目标人员，诱骗目标人员打开文档。实际上，该恶意Excel文档经过特别构造，被嵌入了flash对象，用户一旦打开文档电脑就会中毒。**

CVE-2018-5002影响Adobe Flash Player
29.0.0.171及所有之前的版本。Adobe官方于6月7日下午发布安全公告（公告ID：APSB18-19），Adobe Flash
Player的版本已更新到30.0.0.113。具体可参考Adobe
官方安全公告：<https://helpx.adobe.com/security/products/flash-player/apsb18-19.html>

我们及时向Adobe官方上报了漏洞利用样本，并获得了Adobe官方确认和致谢。

![1.png](https://image.3001.net/images/20180607/15283634759396.png!small)

（攻击流程图）

##  **0x2 攻击流程分析**

###  **1\. 漏洞文档行为分析**

此次攻击时使用的诱饵文档文件名为《basic_salary.xlsx》，主要内容为阿拉伯语言撰写的外交部官员基本工资情况。诱饵文档嵌入了一个在线的Flash对象，用户打开文档后，就会自动加载Flash文件。

![2.png](https://image.3001.net/images/20180607/1528363491735.png!small)

（google翻译后的文档内容）

![3.png](https://image.3001.net/images/20180607/15283635066843.png!small)

（诱饵文档内容）

###  **2\. SWF1行为分析**

SWF1文件中的代码高度混淆，后续图片中的源码，均是对混淆代码进行一定优化后截取的。

![4.png](https://image.3001.net/images/20180607/1528363519554.png!small)

（混淆后的SWF1代码）

诱饵文档中嵌入了一个在线swf对象，当打开带漏洞的excel表格时，会加载“Movie”字段所指向的在线Flash文件，这里取名为SWF1。

Excel会将FlashVars指向的文本会以参数的形式传递给SWF1，这里存放的是漏洞利用样本（SWF2文件） 和
ShellCode等URL信息，分别被标记为了stabUrl、encKeyUrl、downloadUrl、imageUrl。

![6.png](https://image.3001.net/images/20180607/15283635349878.png!small)

（SWF1运行时取参数）

SWF1运行后，会以post方式从参数encKeyUrl
指向的WEB服务器得到解密key及加密的swf。使用aes算法解密后，得到漏洞swf文件，取名为SWF2。

![7.png](https://image.3001.net/images/20180607/15283635453520.png!small)

（SWF1以post方式下载加密的SWF2）

![8.png](https://image.3001.net/images/20180607/15283635546036.png!small)

（SWF1使用aes解密SWF2）

SWF1通过LoadBytes将解密后的漏洞利用文件SWF2加载执行，并将downloadUrl等参数传给SWF2。

![9.png](https://image.3001.net/images/20180607/15283635663606.png!small)

（SWF1加载SWF2）

###  **3\. SWF2（0day漏洞）行为分析**

CVE-2018-5002是由于Flash未能正确处理包含特殊字节码序列的SWF文件时产生的栈越界读写漏洞。该漏洞同之前的CVE-2017-11292类似，都需要修改SWF文件的字节码来触发漏洞。同时该漏洞的利用只需要简单的内存布局，不需要复杂的堆喷，一个样本同时在32位和64位系统中稳定运行。  

**1） 漏洞原理分析**

a. 漏洞代码

ASC2(ActionScript 2)引入了一组用于快速操作内存的函数，如li8, si8等等。该组函数的具体含义如下：

![1.jpg](https://image.3001.net/images/20180608/15284241114067.jpg!small)

样本代码经过了恶意混淆，下面是清除混淆后的触发漏洞代码。

![2.png](https://image.3001.net/images/20180608/15284241593270.png!small)

其中包含li8的静态初始化（Static Initializer）代码并没有被完全反编译，下图是根据其字节码得出的伪码：

![3.png](https://image.3001.net/images/20180608/15284241829666.png!small)

实际调试发现，执行li8指令时会触发异常，同时异常会交由当前的catch块来处理。而catch部分的代码可以越界将其调用者的栈上的两个对象指针(local_448,
local_449)互换,从而实现类型混淆。

这里就产生两个重要的问题：

> I li8指令并不在try块中，为什么产生的异常能被当前的catch块捕获？
>
> II catch块正常情况下只能访问local_0和local_1，为什么这里能越界读写？

b. 异常处理

Flash的虚拟机AVM在执行可能会触发异常的字节码前，会记录当前执行的位置previous_bytecode_offset，当发生异常后则根据记录的执行位置从异常处理例程表ExceptionHandlerTable中查找对应的异常处理函数，即AS脚本或字节码中的catch块。

Flash在创建domainMemory时，会为其初始化一个大小为0x400的内存。

![4.jpg](https://image.3001.net/images/20180608/15284242202194.jpg!small)

Flash在执行li8(123456)指令时，首先会检查偏移123456是否超过了domainMemory的大小。由于偏移123456超过了domainMemory的范围0-1023，所以Flash会抛出一个Range
Error的异常，如下图所示，其中0x34为li8的字节码0x35 – 1。

![5.png](https://image.3001.net/images/20180608/1528424242149.png!small)

在执行该段代码前，previous_bytecode_offset被初始化为0。此后一共执行了三个字节码，分别是：jump，push，li8，这三个字节码的执行都没有保存当前执行的位置到previous_bytecode_offset。

这样Flash在处理li8字节码触发的异常时，认为异常发生的位置为0，接下来FindExceptionHandler函数根据异常发生的位置查找对应的异常处理函数，由于异常位置0位于当前的Try块内，FindExceptionHandler函数就认为该异常应该交给当前的catch块来处理。

下图就是调试该过程的截图，FindExceptionHandler的第二个参数就是出现异常的偏移即previous_bytecode_offset，值为0。

![6.png](https://image.3001.net/images/20180608/15284242602789.png!small)

c. 栈越界读写

栈越界读写主要是通过绕过Flash对Catch代码块的检查(Verify)实现的。

Flash在对Try代码块进行检查时，发现当前代码块只有一条jump指令，而jump指令不会抛出异常。

![7.png](https://image.3001.net/images/20180608/15284242808974.png!small)

同时，由于jump目标区域的字节码序列不在Try代码块内， Flash
AVM认为整段代码不会发生异常，对应的catch代码不会被执行到，所以略过了对catch代码块的检查，从而可以在catch代码块内实现越界读写。

![8.png](https://image.3001.net/images/20180608/15284242978019.png!small)

越界读写前：

![9.png](https://image.3001.net/images/20180608/15284243122980.png!small)

触发越界读写，交换local_448和local_449：

![10.png](https://image.3001.net/images/20180608/15284243258960.png!small)

 **2） 行为分析**

SWF2运行后会从downloadUrl指向的WEB服务器下载加密的数据，以得到shellcode。

![10.png](https://image.3001.net/images/20180607/15283635785982.png!small)

（SWF2 取shellcode下载链接）

![11.png](https://image.3001.net/images/20180607/15283635919208.png!small)

（SWF2下载shellcode）

取加密数据的前16个字节作为解密的Key，通过AES解密ShellCode。

![12.png](https://image.3001.net/images/20180607/15283636021223.png!small)

（SWF2解压缩并执行shellcode）

再借助0day漏洞将shellcode执行起来。由于ShellCode服务器已经关闭，已经无法获取ShellCode的具体内容。

![13.png](https://image.3001.net/images/20180607/15283636124628.png!small)

（执行32位或64位shellcode）

![14.png](https://image.3001.net/images/20180607/15283636253258.png!small)

（执行shellcode）

##  **0x3 总结**

该APT组织使用0day漏洞攻击政府相关部门，利用纯shellcode在宿主进程excel中干坏事。而这种0day漏洞加纯shellcode的攻击方式对安全软件的检测和防护能力是一个挑战。  

腾讯御见威胁情报中心判断在此0day漏洞利用方法未被广泛传播之前，该漏洞仍将主要被技术实力强劲的APT组织所掌握。而鉴于Adobe Flash
Player几乎安装在每一台电脑上，且有大量用户未能及时修补安全漏洞，当该漏洞的利用方法被病毒木马黑色产业掌握时，或将会带来大面积的网页挂马威胁。  

腾讯安全专家提醒政府机关、相关企业用户切勿随意打开来历不明的文档，安装安全软件防御攻击。此外，及时升级Adobe Flash
Player到最新版本（30.0.0.113）以防御可能的漏洞攻击威胁，下载地址：<https://get.adobe.com/cn/flashplayer/>

目前，腾讯御界高级威胁检测系统已经可以检测并阻断该轮攻击的连接行为。企业用户通过部署御界高级威胁检测系统，可以及时感知恶意流量，检测钓鱼网址和远控服务器地址在企业网络中的访问情况，保护企业网络安全。（详情见链接<https://s.tencent.com/product/gjwxjc/index.html>）

![15.png](https://image.3001.net/images/20180607/15283636486998.png!small)

###  **附录（IOCs）:**

![16.png](https://image.3001.net/images/20180607/15283636589170.png!small)![17.png](https://image.3001.net/images/20180607/15283636682613.png!small)

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

