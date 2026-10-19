## **概述**

WIRTE 组织至少在2018年8月开始进行间谍活动，最早是由 S2 Grupo
安全人员在取证中所发现，活动一直持续针对中东地区目标，涉及约旦、巴勒斯坦等不同国家的国防、外交、司法等部门。此外，根据思科的调查，攻击者通常在早晨（中欧时区）活跃，这意味着攻击目标可能与该地区的地缘政治环境有关。

该组织攻击者十分注重资产的隐蔽，攻击者使用信誉良好的 CloudFlare
系统来隐藏其基础架构的性质和位置。根据国外安全厂商的取证研究，攻击者通常在攻击阶段部署多个侦查脚本，以检查受害者计算机的有效性，从而阻止了不符合其条件的系统。

该组织通常在攻击活动中投递携带有恶意宏代码的表格文档诱饵，在目标受害者触发宏代码后广泛使用脚本语言（VBScript、PowerShell、VBA）作为攻击的一部分，最终通过
Empire 框架进行下一阶段的攻击。除此之外，该组织早期也曾投递过 VBS 类型的诱饵，加载后会释放出 DOC 文档迷惑受害者。

微步情报局近期通过威胁狩猎系统捕获到 WIRTE 组织再次针对中东地区的攻击活动，分析有如下发现：

> 攻击者以“国家社会保障基金-原始和非专利药品相同的清单-药品品牌（B）和普通药品（G）-2020-12-17”为诱饵进行鱼叉攻击；
>
> 投诱饵文档采用“Excel 4.0 Macros”方法将宏代码隐藏在表格之中，此方法使得宏代码难以被发现并且在部分 office
> 版本中“禁止启用宏”依旧可以正常执行；
>
> 宏代码执行后的下一阶段，攻击使用 VBScript、PowerShell、VBA 作为后门的编写语言，并且最新的攻击中加入了检测杀软的代码逻辑；
>
> 微步在线通过对相关样本、IP 和域名的溯源分析，共提取5条相关
> IOC，可用于威胁情报检测。微步在线威胁感知平台TDP、本地威胁情报管理平台TIP、威胁情报云API、互联网安全接入服务OneDNS
> 等均已支持对此次攻击事件和团伙的检测。

##  **详情**

微步在线最近捕获到一起以“国家社会保障基金-原始和非专利药品相同的清单-药品品牌（B）和普通药品（G）-2020-12-17”作为诱饵内容的攻击。

###  **诱饵截图**

![](https://image.3001.net/images/20210225/1614245741_60376f6d49ea463f402b8.png!small)

###  **手法流程图**

![](https://image.3001.net/images/20210225/1614245753_60376f7945097f913bf42.png!small)

##  **样本分析**

###  **基本信息**

样本名称| .xls（国籍规定.xls）  
---|---  
样本格式| Microsoft Excel sheet  
SHA256| 8bd23bbab513e03ea1eb2adae09f56b08c53cacd2a3e8134ded5ef8a741a12a5  
SHA1| d5aaa419e24acbc15df58f2eb978a8137396b750  
MD5| ecaaab9e2fc089eefb6accae9750ac60  
C2|
[http://stgeorgebankers.com](https://link.zhihu.com/?target=http%3A//stgeorgebankers.com)  
  
###  **样本分析**

1\. 样本使用了“Excel 4.0 Macros”的方法将宏代码存放在表格的单元中，通过编辑 XLS 文件的二进制数据将表格去除隐藏属性后，宏代码如下：

![](https://image.3001.net/images/20210225/1614245821_60376fbd9a745cbbdfcb6.png!small)

2\.
宏代码检测了包括：“AVG”、“Avast”和“360TotalSecurity”三种杀软，如检测到三种杀软，则打开文件“winrm.txt”；如没有检测到，则打开文件“winrm.vbs”。两个文件写入的内容均为“VB”代码。

![](https://image.3001.net/images/20210225/1614245836_60376fcc4d4856c857ddc.png!small)

3\.
文件写入完成后，在执行方法中也有所不同。如果是“winrm.txt”，则调用“cscript.exe”进程执行。如果是“winrm.vbs”则调用“explorer.exe”进程执行。

![](https://image.3001.net/images/20210225/1614245845_60376fd55af1655d5f726.png!small)

4\. 宏代码执行完上述动作后延时5S，最后将自启动代码写入到“winrm.txt\ winrm.vbs”，并覆盖之前写入的脚本代码，如下图：

![](https://image.3001.net/images/20210225/1614245854_60376fde3ebb1094c93ad.png!small)

5\. “winrm.txt\winrm.vbs”文件为之前宏代码所写入的 VBS 代码，基本信息如下：

样本名称| winrm.txt\ winrm.vbs  
---|---  
样本格式| VB Script  
SHA256| dc64d8ff8343df76d2a0b93d2392b5fafcc5bae905a1ae59ea0670284e25a89f  
SHA1| c5d0c437e1dfb4a5c952d8eae44f5f259d0431e3  
MD5| 07b09929a7d4c8c50bfdf60b97349c0d  
  
6\. “winrm.txt\winrm.vbs”文件执行后会将一段 PowerShell
代码写入到“laquelleg.txt”文件中，然后将自身的文件路径通过“add”的方法添加到注册表中，实现后门持久化的能力。具体代码如下：

![](https://image.3001.net/images/20210225/1614245863_60376fe7e1fab40089dbe.png!small)

7\. “laquelleg.txt” 文件基本信息：

样本名称| laquelleg.txt  
---|---  
样本格式| PowerShell  
SHA256| 9febe610949b5b9518c98103da1ccc3ef32b5ab1ded31e0d5403cd64a023c15b  
SHA1| b0899d2a78421f21737a78804c067d15a8aa226e  
MD5| 168f259dd8830facb5f979fc571bb020  
  
8\. “laquelleg.txt”代码实现的是加载器功能，访问 URL
“[https://stgeorgebankers.com/](https://link.zhihu.com/?target=https%3A//stgeorgebankers.com/)”将其网页携带的
Payload 解析并执行，网页中通过“<p>Payload</p>”方式嵌入 Payload。

![](https://image.3001.net/images/20210225/1614245873_60376ff17e60f68894d9b.png!small)

9\. 根据历史披露文章，最终后门疑似为 Empire 框架生成的载荷。

##  **关联分析**

通过对宏代码相似度和文件释放特点进行关联，我们发现，该组织的曾在2019年11月至2020年2月期间较为活跃。

###  **部分历史活动**

1\. 2020年1月，以“2019年1月和2020年1月主要部门和组的每月消费者物价指数数字和百分比变化”为诱饵标题，针对目标单位进行攻击。

![](https://image.3001.net/images/20210225/1614245884_60376ffcee7d0bcce92f0.png!small)

2\. 2020年1月，伪装成伊拉克司法部的相关文件，针对某些单位进行攻击。

![](https://image.3001.net/images/20210225/1614245896_60377008340950b17d303.png!small)

3\. 2020年1月，以“执行委员会执行委员 Mohamed Al-Nashashibi ”追悼会为诱饵，针对特定人群攻击。

![](https://image.3001.net/images/20210225/1614245912_60377018eae20d89f61c3.png!small)

###  **历史手法对比**

1\. 我们对2020年1月期间的攻击活动中，诱饵标题为 “2019年1月和2020年1月主要部门和组的每月消费者物价指数数字和百分比变化”的样本进行对比。

2\. 该文件基本信息如下：

样本名称| Book1.xls  
---|---  
样本格式| Microsoft Excel sheet  
SHA256| 38a9fb95ce22e3595e6bcab16043630cc3dfed65d2d8588f80da8148827af475  
SHA1| d920262b69870f9aaa8714dbd325ee66f78b6579  
MD5| a06401aa5808e5c202630098d73b260b  
C2|
[http://omegaeyehospital.com](https://link.zhihu.com/?target=http%3A//omegaeyehospital.com)  
  
3\. 该诱饵的宏代码如下：

![](https://image.3001.net/images/20210225/1614245924_60377024d8cbf60676aca.png!small)

4\. 该历史诱饵和最新投递的诱饵对比，新投递的诱饵宏代码中增加了杀软检测代码。

![](https://image.3001.net/images/20210225/1614245933_6037702d4bc3b441003fe.png!small)

5\. 释放的 PowerShell 脚本中，POST 请求头中的 UserAgent 变为更新的版本号，并且 Payload
由直接存放变成嵌入到网页中的标签之中。

![](https://image.3001.net/images/20210225/1614245941_60377035d6ceca3a9ef23.png!small)

6\. 此外，国外安全厂商曾披露过 WIRTE 组织的手法，从投递的诱饵、释放的文件、资产特点（使用 CloudFlare
IP、域名相似度）、攻击地域和后门相似度等，判研此次捕获到的诱饵文档很可能为 WIRTE 组织所投递。

## 附录 - IOC

### C2

[http://dentalmatrix.net](https://link.zhihu.com/?target=http%3A//dentalmatrix.net)

[http://unitedfamilyhealth.net](https://link.zhihu.com/?target=http%3A//unitedfamilyhealth.net)

[http://office365-update.com](https://link.zhihu.com/?target=http%3A//office365-update.com)

[http://stgeorgebankers.com](https://link.zhihu.com/?target=http%3A//stgeorgebankers.com)

[http://omegaeyehospital.com](https://link.zhihu.com/?target=http%3A//omegaeyehospital.com)

### Hash

c1388b7a84a0cf3cc41047ff68bd5905cc29bf4611fd3d76e021744f00617b6d

8bd23bbab513e03ea1eb2adae09f56b08c53cacd2a3e8134ded5ef8a741a12a5

d0234d56dac17481704ac5aa9c1fc4b5813949f577c50406a95050c2317a78ea

c5a4c456d4d3e8c4786d8f82860d8d6884ede6c035d6be7ba491676018844c10

a710fb9dc78caf76a7819358e9b0af965a3728f6a12ef1179652d5895468045d

81d8657b41dc70a4f92b952833684d3f2ad26ea073ce72807e4e03bf9a9818eb

7133ef4361d0955e9f07ec2cb092aa54de438141c405d3739263e509d951b64a

38a9fb95ce22e3595e6bcab16043630cc3dfed65d2d8588f80da8148827af475

6024d10dd4a8e7efe0c81d6cfcf0f6b6833bf2728dfb2590485adb483a78d3ff

b2849a4c2216d24cf211dab992d298c752e5f81f184fe1d576a9adc61277ff9a

a162826a4fb9a0627066ecbdae4f7481d3acd0dbd879b37abc2cf69a4f55ca60

2fb915b60bd6990c757a748fe5e6d4d28e5fd555e131862c416efa7ce5131788

8a0501372165361b80a8063826c78f61608637194ed884787a9a5e9f837f33ed

65f5a412170067c6b2e4d62daab83b651ebcbb72f17e88265caea3e1c675d586

86afdc1e034deab844b250f89a285848d8632f7e5496b1de00ecbc2dc48153b3

3c963878c7d0103ba2c2b7576f470024e990d82294867d694781d0c482abb5fa

##  **参考链接**

<https://blog.talosintelligence.com/2018/02/targeted-attacks-in-middle-east.html>

<https://www.securityartwork.es/2019/01/25/wirte-group-attacking-the-middle-east/>

  

  

