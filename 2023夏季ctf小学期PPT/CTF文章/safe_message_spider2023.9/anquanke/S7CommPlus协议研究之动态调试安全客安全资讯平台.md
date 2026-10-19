# S7CommPlus协议研究之动态调试

阅读量 **331330**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-19 14:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 1、概述

[上一篇文章](https://www.anquanke.com/post/id/206579)对S7comm-Plus协议进行了初步研究，算是理论研究了，本篇以核心通信DLL（OMSp_core_managed.dll）为目标，使用动态调试的方式，对协议的握手、加密认证过程进行动态调试，以对通信过程做进一步探索认识。

基于之前的工作已经知道，更高版本的TIA
Portal软件对应的OMSp_core_managed.dll版本亦更高、更复杂，因此调试工作使用较低版本的DLL为目标（即选择TIA Portal
V13，则PLC只能使用V4.1及以下版本），以便于分析和掌握调试方法。

## 2、环境配置

调试研究的基本环境配置如下：Win7x86虚拟机、

PLC：S7-1200 , 6ES7 212-1BG40-0X0B

Firmware: V4.1.3

Software：TIA Portal V13

S7Comm-Plus Wireshark dissector plugin: V0.0.8

![](https://p0.ssl.qhimg.com/t0155a2953fac53cd23.png)

## 3、通信调试

### 3.1、加密函数入口定位

参考文章均指出PLC实现通信握手、加密认证的功能在模块OMSp_core_managed.dll中实现，由此可知对该文件的分析尤为重要。OMSp_core_managed.dll是一个使用C#和C++混合编写的.net程序，使用dnSpy对其进行反编译：

![](https://p5.ssl.qhimg.com/t0159d0b1bea44abe01.png)

如何定位加密函数的入口呢？此处提供两种思路：

1、直接使用dnSpy对DLL文件进行动态调试

dnSpy加载DLL文件，使用“调试”->“附加到进程”功能，附加TIA的进程：

![](https://p3.ssl.qhimg.com/t01385aa6fe0ee42da1.png)

在DLL中先随便打一个断点，可参考文章中指出的SetServerPublicKey：

![](https://p5.ssl.qhimg.com/t01940fd1f87a4b2b7b.png)

在dnSpy中尝试搜索关键字，结果如下:

![](https://p5.ssl.qhimg.com/t014b2b04eda2263ec3.png)

可见该函数位于“ClientSession”类中,在此函数出设置一个断点,然后操作TIA将PLC“转到上线”，转到上线时TIA与PLC将建立通信连接，此时必然经过三次握手及通信加密过程，可看到函数执行到刚才打的断点位置：

![](https://p4.ssl.qhimg.com/t01d692a0a5f39a2c00.png)

查看“局部变量”中的“key”，发现其已经有值，长度为40的数组：

![](https://p5.ssl.qhimg.com/t01dd380e01c44c8b75.png)

![](https://p3.ssl.qhimg.com/t01b80adb476e0c2c29.png)

此值即为上一篇文章中提到的S7-1200系列的public key的值。

在dnSpy中继续进行单步执行，经过多次调试可以看到，当calli执行完毕之后，TIA与PLC通信建立完成，calli过程即是在C#中调用C++代码：

![](https://p5.ssl.qhimg.com/t0121824d3c0a46b6bd.png)

调试过程中关注指针session_ptr的值，此处为0x2B9E71C0:

![](https://p1.ssl.qhimg.com/t0177c3a6aefb04cb2b.png)

停止dnSpy调试，使用IDA附加TIA进程，由于TIA进程一直处于运行中，其内存加载地址空间将保持不变，通过上述函数指针最终计算得到0x65D77310

![](https://p5.ssl.qhimg.com/t01c182b20c15a30c01.png)

F5查看伪代码发现其调用了三个函数：

![](https://p5.ssl.qhimg.com/t017e4c11e0af481689.png)

继续跟进查看，可以发现函数sub_65D7CD40即为第一部分加密函数。

![](https://p1.ssl.qhimg.com/t01e6255471b972005c.png)

2、使用IDA对DLL文件进行动态调试

参考绿盟的文章可以发现其使用了Windbg进行调试，且留下一些“痕迹”，如下图所示：

![](https://p3.ssl.qhimg.com/t013b3d785e2f81ab4b.png)

因此可以考虑搜索上图中出现的字节码，于是使用IDA附加TIA进程，尝试搜索“e8 9e f9 ff ff”,结果如下：

![](https://p5.ssl.qhimg.com/t01fbd0fe7d91b179b7.png)

![](https://p0.ssl.qhimg.com/t019ac88afc6442de10.png)

此处定位到函数sub_65D793B0,发现与绿盟文章中的截图颇为相似：

![](https://p3.ssl.qhimg.com/t0158e1da99d33828ef.png)

使用0x65D793B0减去DLL函数的base（0x65BA0000）结果刚好为：0x1D93B0,与绿盟文章中的函数sub_1D93B0刚好对应，因此可以推断调试环境与其相同，那么函数sub_65D793B0即为sub_1D93B0，依次类推：sub_65D790B0即为IntegratyPartEncrytion函数。使用类似的方式搜索定位到加密1函数：

![](https://p0.ssl.qhimg.com/t01c50f25e14f3de04b.png)

![](https://p5.ssl.qhimg.com/t01ad9eec70154c8b0c.png)

![](https://p5.ssl.qhimg.com/t01dbfa44e40d7eb3fa.png)

与论文中给出的效果一致：

![](https://p1.ssl.qhimg.com/t01784e41da779b8153.png)

进一步使用参考调用功能，可以追溯到加密函数入口sub_65D77310,与第一种方式得到的结果一致。

### 3.2、加密1内容计算

定位到了负责加密认证的函数之后，便可继续使用动态调试对整个加密算法流程进行验证和计算了。上图绿盟的文章中指出，加密1部分的内容为Value
array（即上一篇文章中提到的20个字节的随机数）经过加密1函数加密之后的结果，加密的过程为一系列XOR运算，而最终加密的结果保存在v13-v16中。于是可以在加密1函数中下一个断点，然后进行单步调试，监控v13-v16的值：

![](https://p2.ssl.qhimg.com/t018c34d65bb7901eb0.png)

同样打开wireshark抓包，操作TIA将PLC“转到上线”，函数执行到刚才打的断点位置。同时可以看到握手的前2步已完成，TIA收到PLC发送的20个字节随机数：

![](https://p5.ssl.qhimg.com/t01f903fc6b2ba8dcd6.png)

继续单步执行，当v13-v16运算完成之后，可从左边变量监控栏得到最终运算结果：

![](https://p2.ssl.qhimg.com/t0101f06a01281956cd.png)

在此先记录v13-v16的值：v13(0x52CF7D4E)、v14(0x9603F213)、v15(0x50639E99)、v16(0xC452A5E3)，待整个握手过程完成之后，在M3数据包中的“SecurityKeyEncryptedKey”字段中去验证：

![](https://p1.ssl.qhimg.com/t014bc94a93b35b57b6.png)

注意大小端模式，由此可见，其值与加密1内容完全吻合。

## 4、总结

基于对西门子最新的S7Comm-Plus通信协议的理解，使用反汇编工具对核心通信DLL进行逆向和动态调试，介绍了两种定位加密函数入口的方法，同时使用IDA动态调试，计算并验证了加密1的结果内容，从动态调试的角度对加密算法进行了进一步理解。后续的加密步骤及算法的验证，可参照类似方法继续进行。

参考资料：

[1] <https://www.blackhat.com/docs/eu-17/materials/eu-17-Lei-The-Spear-To-Break%20-The-Security-Wall-Of-S7CommPlus-wp.pdf>

[2] https://www.blackhat.com/docs/eu-17/materials/eu-17-Lei-The-Spear-To-Break%20-The-Security-Wall-Of-S7CommPlus.pdf

[3] https://i.blackhat.com/USA-19/Thursday/us-19-Bitan-Rogue7-Rogue-Engineering-Station-Attacks-On-S7-Simatic-PLCs-wp.pdf

[4] https://i.blackhat.com/USA-19/Thursday/us-19-Bitan-Rogue7-Rogue-Engineering-Station-Attacks-On-S7-Simatic-PLCs.pdf

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **NonAttack** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/208827](/post/id/208827)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [plc](/tag/plc)
  * [Siemens](/tag/Siemens)
  * [S7CommPlus](/tag/S7CommPlus)
  * [S7](/tag/S7)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) NonAttack

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

