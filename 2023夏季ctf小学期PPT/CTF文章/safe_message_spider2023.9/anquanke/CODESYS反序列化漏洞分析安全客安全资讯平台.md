# CODESYS反序列化漏洞分析

阅读量 **138435**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-19 10:00:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

CoDeSys是可编程逻辑控制PLC的完整开发环境(CoDeSys是Controlled Development
System的缩写)，它支持IEC61131-3标准IL 、ST、 FBD 、LD、 CFC、 SFC
六种PLC编程语言，用户可以在同一项目中选择不同的语言编辑子程序，功能模块等。在PLC程序员编程时,CoDeSys为强大的IEC语言提供了一个简单的方法，系统的编辑器和调试器的功能是建立在高级编程语言的基础上(如Visual
C++)。

## 0x00 概述

在CODESYS GmbH CODESYS Development System
3.5.16和3.5.17版本中存在反序列化漏洞，如CVE-2021-21864：

根据CVE的漏洞相关描述，下载存在漏洞的CODESYS 3.5.16版本进行漏洞分析与复现。

## 0x01 漏洞复现

通过CVE漏洞的描述，可知此漏洞为BinaryFormatter()函数引起的反序列化漏洞，因为调用了恶意APStartupCulture文件导致执行系统命令。

通过processMonitor查看Codesys.exe进程运行信息，程序尝试查找APStartupCulture和APStartupCulture.xml文件，但是并未找到：

![](https://p2.ssl.qhimg.com/t01608be5ff02acb5ef.png)

使用反序列化工具生成POC并命名为APStartupCulture

![](https://p3.ssl.qhimg.com/t01ddec2ad2c07fb4db.png)

将APStartupCulture文件放入ProgramData目录中

![](https://p4.ssl.qhimg.com/t016c8a59308e93334f.png)

启动程序成功触发反序列化漏洞并执行POC程序

![](https://p1.ssl.qhimg.com/t01a9b43a23da177cc8.png)

## 0x02漏洞分析

找到启动程序Main()函数：

![](https://p5.ssl.qhimg.com/t012d16d613abce0035.png)

跟进到Run()函数中，查看启动UI函数RunUI()：

![](https://p3.ssl.qhimg.com/t018bdea6a833f46448.png)

在RunUI()函数中，没有看到启动参数，继续往下走：

![](https://p3.ssl.qhimg.com/t014019769ec2788980.png)

启动了多个线程，调用了InitializeComponentManager()函数，跟进InitializeComponentManager()函数：

![](https://p5.ssl.qhimg.com/t01dcac27eaa5f41153.png)

此函数中，对配置进行了设置以及初始化配置，此处有一个ComponentManager5()函数，跟进此函数查看：

![](https://p3.ssl.qhimg.com/t01ed9a46091643a51c.png)

ComponentManager5()依次继承最后来到ComponentManager()函数中，当执行到第67行代码时，跟进函数：

![](https://p5.ssl.qhimg.com/t01619f8109d8b4b82a.png)

该函数功能是取出并查找文件APStartupCulture是否存在，然后进行判断：

![](https://p3.ssl.qhimg.com/t012fdc597f610e16b5.png)

随后打开文件并将数据赋值给stream变量，传入BinaryFormatter()函数进行反序列化：

![](https://p5.ssl.qhimg.com/t013435e23f4970a0cf.png)

往下执行之后，成功反序列化并执行我们的POC：

![](https://p2.ssl.qhimg.com/t01e67a1d3944d7fc03.png)

## 0x03 总结

此反序列化漏洞为厂商意料之外的程序恶意调用，从漏洞分析结果来说，此漏洞整个调用链触发过程很简单，就是在某个目录下写个反序列化利用文件即可，还是印证了那句话，用户输入甚至所有外部输入都不可信任。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **博智安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/266095](/post/id/266095)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [工控安全](/tag/工控安全)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t01dc77631201c3445b.png) 博智安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

