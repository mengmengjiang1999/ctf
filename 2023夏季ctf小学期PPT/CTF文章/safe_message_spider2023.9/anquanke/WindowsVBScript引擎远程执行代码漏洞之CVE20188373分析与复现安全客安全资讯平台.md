# Windows VBScript引擎远程执行代码漏洞 之CVE-2018-8373分析与复现

阅读量 **259987**

发布时间 : 2018-11-27 15:35:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/dm/1024_672_/t017e3d93f08be9d4a5.jpg)

## 一、 漏洞简介

VBScript引擎处理内存中对象的方式中存在一个远程执行代码漏洞。该漏洞可能以一种攻击者可以在当前用户的上下文中执行任意代码的方式来破坏内存。成功利用此漏洞的攻击者可以获得与当前用户相同的用户权限。如果当前用户使用管理用户权限登录，则成功利用此漏洞的攻击者可以控制受影响的系统。然后攻击者可以安装程序;
查看，更改或删除数据; 或创建具有完全用户权限的新帐户。

在基于Web的攻击情形中，攻击者能通过Internet
Explorer利用此漏洞的特定网站，然后诱使用户查看该网站。攻击者还可以在承载IE呈现引擎的应用程序或Microsoft
Office文档中嵌入标记为“安全初始化”的ActiveX控件。攻击者还可以利用受到破坏的网站和接受或托管用户提供的内容或广告的网站。这些网站可能包含可能利用此漏洞的特制内容。

2018年8月14日，微软发布了安全补丁，影响流行的大部分系统版本。

漏洞基本信息

漏洞ID： CVE-2018-8373

漏洞名称： Microsoft VBScript引擎远程执行代码漏洞

漏洞类型： 远程代码执行

威胁类型： UAF

影响系统版本： IE9 WS 2008 32/64、IE10 Windows Server2012、IE11大部分版本

## 二、 漏洞测试

系统环境 Win7 32/64

IE版本 IE10

EXP <https://github.com/B1eed/VulRec/blob/master/CVE-2018-8373>

## 三、 漏洞原理

由于样本混淆严重，部分代码见图1，这里采用简化POC进行分析，代码见图2。

![](https://p4.ssl.qhimg.com/t0167c278cd65d5008e.jpg)

图1 样本采用了严重混淆

![](https://p5.ssl.qhimg.com/t01aedc91e73a558fec.jpg)

图2 Crash Poc

Crash PoC定义了MyClass类、一个array的成员变量和两个成员函数：Class_Initialize 与Default Property
Get P。Class_Initialize
是一种被弃用的方法，现在已经被新的过程所替代。当对象初始化的时候，会被自动唤醒。在PoC中，Class_Initialize 是重载的，当调用
VBScriptClass::InitializeClass时，处理的是重载的函数。

MyClass：通过new进行创建并赋值给指定变量cls，该操作首先会触发类的创建以及初始化，创建类的函数由vbscript!VBScriptClass::Create函数完成；

![](https://p1.ssl.qhimg.com/t0141ec4ec58e5aad89.jpg)

创建类成功后则会调用vbscript!VBScriptClass::InitializeClass函数对class的内容进行初始化；

![](https://p5.ssl.qhimg.com/t017473852c6a7c9ec7.jpg)

在vbscript!VAR::IsFunction函数中获取class指针；

![](https://p1.ssl.qhimg.com/t010582046d17dc3a64.jpg)

随后调用class的虚函数vbscript!CScriptEntryPoint::Call 进行初始化,最终的调用栈如下：

![](https://p0.ssl.qhimg.com/t01f96dab795be8f8de.jpg)

vbscript!CScriptRunTime::RunNoEH负责对编译后的vbs代码进行解释执行。这里执行类的初始化操作，主要包含了array数组的定义以及Class_Initialize函数的执行。

vbscript中创建数组的函数为vbscript!MakeArray，如下：

![](https://p4.ssl.qhimg.com/t0198808a81c7554e1b.jpg)

ReDim array(2)：会调用vbscript!MakeArray来创建元素数是3的数组，如下图

![](https://p5.ssl.qhimg.com/t019480ec2508624f41.jpg)

cls.array(2)：调用vbscript!Accessarray来获取数组元素的地址。在vbscript!Accessarray
中，首先会检查数组元素的索引是否越界，然后计算元素的地址，保存到栈中。

![](https://p1.ssl.qhimg.com/t01d0544f614145d2ab.jpg)

将元素的地址保存到堆栈上，保存array(2)= 0x12ae6ff0地址到栈上

cls.array(2)=cls：调用vbscript!AssignVar来设置MyClass的默认属性值为
cls.array(2)。获取MyClass的默认属性值后，会调用Public Default Property Get P并执行Public
Default Property Get P中的ReDim array(1)，释放了原来的pvData。

![](https://p4.ssl.qhimg.com/t01422bcf34439fc51b.jpg)

ReDim Preserve
array(1)：重置array内存的操作实际通过函数RedimPreserveArray实现，最终会调用SafeArrayRedim可以看到array对象的pvData已经被修改为0x0818afe0，之前的pvData(0x12ae6fd0)的内存地址已经被释放，包括之前保存在栈上的0x12ae6ff0。

![](https://p4.ssl.qhimg.com/t019a8cacb25d52b10e.jpg)

array(2)的地址仍然保存在栈中， Public Default Property Get P 的返回值会访问释放的内存，最终导致UAF漏洞。

## 四、 EXP调试分析

调试方法同Crash
PoC，跟踪分析如何将二维数组修改长度为0x0FFFFFFF，如何实现任意内存读写以及如何伪造CONTEXT结构来执行Shellcode。

漏洞定义了两个数组，array1和array2。array1就是前面PoC中描述的数组，array2是一个二维数组，其中每个元素的值都是3。然后使用脚本回调函数DefaultPropertyGet释放原来的array1.pvData，设置array2为新的array1.pvData。因为原来array1.pvData的大小和array2.SAFEARRAY结构是相同的，在内存中是0x30字节。array2.SAFEARRAY结构将重用原始array1.pvData中释放的内存。同时，DefaultPropertyGet的返回值0x0FFFFFFFF会覆盖array2.SAFEARRAY的结构SAFEARRAYBOUND，并修改二维数组的长度为0x0FFFFFFF。

![](https://p1.ssl.qhimg.com/t01413c6e673cf69d7c.jpg)

修改二维数组的长度为0x0FFFFFFF

![](https://p4.ssl.qhimg.com/t016461b4afed09f194.jpg)

![](https://p3.ssl.qhimg.com/t01594b046c0941284b.jpg)

将array(index_vul)(index_a,
0)设置为“AAAA”，使下个array2的Data域就变成了8，因为string的VarType类型为8，这样就得到了一组可以混淆的
array(index_vul)(index_a+n, 0)和array(index_b)(0,
n)，通过将array(index_vul)(index_a, 0)处的variant 转化为长整型，令array(index_vul)(index_a,
0)处的variant转化为数组，从而得到了一段泄露的内存util_mem，即可读写内存指定区域。

![](https://p5.ssl.qhimg.com/t014d3f01f0c88100a2.jpg)

![](https://p5.ssl.qhimg.com/t018aaefa7485965e1d.jpg)

执行rw_primit后，指定位置已被覆盖成0x200C，有了一块泄露的内存 util_mem，能够实现 32 位下用户态任意地址读写的一维数组

![](https://p3.ssl.qhimg.com/t01f43e3eab4dbaef66.jpg)

执行Shellcode方法与8174相同，这里不再详细分析。

![](https://p0.ssl.qhimg.com/t010ee28499c7a471c6.jpg)

![](https://p4.ssl.qhimg.com/t017977cda36a46c260.jpg)

![](https://p4.ssl.qhimg.com/t01475c3d7c193a6639.jpg)

在Windows7环境下能够成功利用，以弹出calc为例。

参考：<https://blog.trendmicro.com/trendlabs-security-intelligence/use-after-free-uaf-vulnerability-cve-2018-8373-in-vbscript-engine-affects-internet-explorer-to-run-shellcode/>

更多漏洞播报：物联网实验室

原创文章转载请注明来源：四维创智

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **四维创智** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/166581](/post/id/166581)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [漏洞分析](/tag/漏洞分析)
  * [系统安全](/tag/系统安全)
  * [VBScript](/tag/VBScript)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhimg.com/t01426d25966e6e991f.png) 四维创智

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

