# 【漏洞分析】Microsoft Office内存损坏漏洞（CVE–2017–11882)分析

阅读量 **293069**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-11-21 17:05:14

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

**作者** **：**[ **MerJerson,
houjingyi@360CERT**](http://bobao.360.cn/member/contribute?uid=2910463042)

**传送门**

[**【漏洞分析】CVE-2017-11882漏洞分析、利用及动态检测**](http://bobao.360.cn/learning/detail/4753.html)

**0x00背景**

2017年11月，微软在例行系统补丁发布中，修复了一个Office远程代码执行的严重漏洞，编号 **CVE-2017-11882**
。该漏洞类型为缓冲区溢出，位于 **EQNEDT32.EXE** 组件。受害用户打开恶意的office文档时，无需交互，就可能执行恶意代码。

据悉，这个组件是由Design Science Inc.开发的，后来由微软收购。
**该组件于2001年编译嵌入office，之后没有任何进一步的修改。所以该漏洞已存在17年之久。影响现阶段流行的所有office版本。**

360CERT经过分析确认，确定该漏洞存在远程命令执行风险，建议用户尽快更新相应补丁。

**0x01漏洞概述**

**EQNEDT32.EXE** 用于在文档中插入和编辑方程式。插入到文档中的任何公式都是 **OLE对象**
。该组件是在OLE技术规范下设计的。首发于Microsoft Office 2000和Microsoft 2003。从Microsoft Office
2007套件开始，显示和编辑方程的方法发生了变化，虽然EQNEDT32.EXE变得过时，不过，为了保持版本兼容性，它并没有从Office套件中删除。

EQNEDT32.EXE为OLE实现了一组标准的COM接口。

IOleObject

IDataObject

IOleInPlaceObject

IOleInPlaceActiveObject

IpersistStorage

而问题的就在于IpersistStorage:Load这个位置。因为历史久远，该组件开发的时候并没有例如ASLR这样的漏洞缓解措施。利用起来更加的方便。

**0x02 漏洞分析**

检测到VirusTotal上有该漏洞的POC，多家检测机构标注为CVE-2017-11882。（最开始只有微软能检测）

如上所说，通过恶意样本分析，问题出在 **EQNEDT.EXE** 中 **sub_41160F** 函数中。如图所示，
**strcpy函数没有检查复制时的长度造成了溢出。**

通过调试可以猜测在正常情况下eax寄存器也就是第一个参数应该是字体名。

通过rtfobj抽取样本中的OLE对象，发现字体名为cmd.exe……。

在填充的AAA……之后是0x430C12，也就是 **EQNEDT.EXE** 中调用 **WinExec** 的地方。

返回地址被覆盖为0x430C12，从而执行命令。

最后执行效果：

**0x03影响版本**

Office 365

Microsoft Office 2000

Microsoft Office 2003

Microsoft Office 2007 Service Pack 3

Microsoft Office 2010 Service Pack 2

Microsoft Office 2013 Service Pack 1

Microsoft Office 2016

**0x04修复建议**

360CERT建议用户及时更新补丁，以提高系统安全性。

**缓解措施：该问题可通过修改注册表，禁用该模块的方式进行缓解。其中XX.X为版本号。**

    
    
    reg add "HKLMSOFTWAREMicrosoftOfficeXX.XCommonCOM Compatibility{0002CE02-0000- 0000-C000-000000000046}" /v "Compatibility Flags" /t REG_DWORD /d 0x400
    
    
    reg add "HKLMSOFTWAREWow6432NodeMicrosoftOfficeXX.XCommonCOM Compatibility{0002CE02-0000-0000-C000-000000000046}" /v "Compatibility Flags" /t REG_DWORD /d 0x400

**0x05时间线**

2017年11月14日 微软发布安全更新

2017年11月20日 Github放出利用代码

2017年11月21日 360CERT及时跟紧发布预警通报

**0x06参考文档**

<https://github.com/embedi/CVE-2017-11882>

<https://embedi.com/blog/skeleton-closet-ms-office-vulnerability-you-didnt-know-about>

<https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-11882>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87284](/post/id/87284)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

