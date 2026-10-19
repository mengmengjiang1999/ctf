# Donot APT团伙近期针对周边国家和地区的攻击活动分析

阅读量 **574800**

发布时间 : 2020-04-29 10:00:38

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01f0701c2a21678b3b.jpg)

## 概述

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，其主要以周边国家的政府机构为目标进行网络攻击活动，通常以窃密敏感信息为目的。该组织具备针对Windows与Android双平台的攻击能力。

自2017年开始，奇安信威胁情报中心对该组织一直保持着持续跟踪，并多次公开披露过其攻击活动。近期，奇安信红雨滴和奇安信APT实验室在日常的跟踪过程中，再次监测到该组织开展了新一轮攻击活动。此次攻击活动中，该组织采用的技战术手法并未发生大的变化，只是在代码中做了些轻微改动：例如下载器中将字符串简单加密处理、Android样本中将C2等信息简单加密处理等。红雨滴团队对新捕获到的样本进行了详细分析。

## 样本分析

此次捕获的攻击样本均为宏利用样本，基本信息如下

**文件名** | **MD5** | **作者** | **修改时间**  
---|---|---|---  
**22 Apr 2020.xls** | 107d25c7399b17ad6b7c05993b65c18e | Testing | 2020:03:17
10:42:38  
**List of new items.xls** | a9d6d2d93eda11e89ed2ca034b81e6ef | Testing |
2020/02/24 06:00  
**Invoice.xls** | 22be6422e8cc09bda69843acc405f104 | Testing | 2020:01:08
07:07:06  
**RegistrationForm.xls** | 554a72999435c81ceedf79db6a911142 | Testing |
2019:10:18 09:33:17  
  
以”22 Apr 2020.xls”为例，打开文档时便会弹出窗口提示启用宏

![](https://p2.ssl.qhimg.com/t011de3d763a13b0507.png)

一旦受害者启用宏，恶意宏将故意弹出一个报错窗口，以迷惑受害者

![](https://p3.ssl.qhimg.com/t016dbbcc1908c89ec3.png)

而恶意宏将在释放一个恶意dll以及一个bat到受害者计算机，并通过创建计划任务将bat文件执行起来

![](https://p2.ssl.qhimg.com/t01f7639e2032fade18.png)

创建的计划任务信息如下

![](https://p2.ssl.qhimg.com/t01f8ca91a77d7fb12e.png)

通过计划任务触发执行的bat文件将创建多个目录，并将这些目录属性设置为隐藏

![](https://p4.ssl.qhimg.com/t01a052d4c95f6fbf9d.png)

之后获取计算机名和5位随机数字组成字符串保存到%USERPROFILE%\Printers\Net\profiles\irina，同时将dll文件移到%USERPROFILE%\Check\Netspeed\Data\目录下重命名为inet.dll

![](https://p1.ssl.qhimg.com/t018b071e0685d4471a.png)

最后再创建两个计划任务”Internet”，”Data_log”,其中”Internet”用于执行inet.dll

![](https://p2.ssl.qhimg.com/t0159c5777d7beaffd0.png)

样本运行流程可通过奇安信在线云沙箱运行查看，整体行为流程如图所示

![](https://p3.ssl.qhimg.com/t012731583fad049363.png)

**文件名** | **inet.dll**  
---|---  
**MD5** | D140F63FF050C572398DA196F587775C  
  
该dll是一个downloader,主要用于下载后续木马执行，运行后，首先通过长时间sleep从而使一些沙箱无法执行后续行为

![](https://p1.ssl.qhimg.com/t01f0178f1d666e6783.png)

样本中的关键字符串采用简单的加密处理

![](https://p3.ssl.qhimg.com/t016b697d338b77393a.png)

样本经过长时间的休眠
之后，将尝试从远程服务器supportsession[.]live/192362/x2d34x3获取文件，若成功获取则写入到%USERPROFILE%\\\Look\\\Drive\\\wmi\\\hostcom.exe

![](https://p5.ssl.qhimg.com/t0137fd5f35c60c4779.png)

文件名 | hostcom.exe  
---|---  
MD5 | 8b640d71f6eda4bdddeab75b7a1d2e12  
  
该文件成功获取后，将通过bat创建的计划任务”Data_log”加载执行。

![](https://p1.ssl.qhimg.com/t01432589516f45ac1a.png)

该样本采用了与inet.dll相同的简单加密，执行后，会尝试从\Printers\Net\profiles\irina中获取“计算机名-随机数“

![](https://p0.ssl.qhimg.com/t0112fb869ada3b7bef.png)

之后将以参数orderme/计算机名-随机数与c2: requestupdate.live进行通信

![](https://p4.ssl.qhimg.com/t01f8725355a0e69a46.png)

与c2通信获取信息执行，当返回数据中包含“Content-Type: xDvsds “以及”Content-Type:
Bw11eW”时，将远程获取命令保存到\Printers\Net\net\test.bat中执行

![](https://p2.ssl.qhimg.com/t01b0bf3c2997fd0a94.png)

若都没有，则尝试读取数据写入\Printers\Net\net\wuaupdt.exe执行

![](https://p4.ssl.qhimg.com/t014838193d683ca771.png)

遗憾的是，在分析的过程中，c2服务器已经失效，无法获取到后续木马。

## 溯源关联

奇安信威胁情报中心红雨滴团队通过对宏特征，bat特征，木马特征等信息进行关联分析发现，此次捕获的样本均出自南亚APT组织Donot。

### 与Donot APT团伙的关联

此次捕获样本释放执行的bat文件与奇安信威胁情报中心《Donot（APT-C-35）组织对在华巴基斯坦商务人士的定向攻击活动分析》 **[1]**
一文中的bat文件基本一致，都创建多个隐藏目录，并获取计算机名加随机数组成字符串保存到文件。

![](https://p5.ssl.qhimg.com/t017a21aa9aabfacc0b.png)

hostcom.exe与Plugin-Downloader – wlidsvcc.exe也基本一致，同样以参数”orderme/计算机名-随机数”与c2通信，且下载的后续木马文件名保存为wuaupdt.exe

![](https://p0.ssl.qhimg.com/t01b487b18a93dd03a6.png)

同时，其c2命名方式也与donot基本一致，且奇安信ALPHA威胁分析平台已有Donot相关标签

![](https://p1.ssl.qhimg.com/t010d599da8cb5bba16.png)

### 代码更新

同时，该APT组织也对其攻击武器进行了简单的更新，以逃过一些安全研究人员的追踪，例如之前通过注册表启动项启动后续木马，到如今的利用计划任务实现持久化。

![](https://p2.ssl.qhimg.com/t018481dbd4218b47cb.png)

明文路径等也加上了简单的加密，此方法可能时为了逃避字符串相关规则

![](https://p1.ssl.qhimg.com/t013080c9e06eb43b82.png)

同样的，其Android端也对c2增加了简单的加密处理

![](https://p5.ssl.qhimg.com/t01070110b0ae6182e1.png)

![](https://p1.ssl.qhimg.com/t01d0266fb166b32189.png)

## 总结

APT组织不会因为安全研究人员对其进行披露而停止攻击活动，从Donot组织样本代码更新可以看出，APT组织也会不断改进其攻击武器，改变其攻击手法，更有甚者会模仿其他APT组织展开攻击活动，从而躲避安全研究人员的跟踪。

奇安信威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括威胁情报平台（TIP）、天眼高级威胁检测系统、NGSOC、奇安信态势感知等，都已经支持对此APT攻击团伙攻击活动的精准检测。

## IOC

**MD5**

107d25c7399b17ad6b7c05993b65c18e

fa86464d6fa281d6bec6df62d5f2ba4f

22be6422e8cc09bda69843acc405f104

554a72999435c81ceedf79db6a911142

fa86464d6fa281d6bec6df62d5f2ba4f

22be6422e8cc09bda69843acc405f104

554a72999435c81ceedf79db6a911142

A9D6D2D93EDA11E89ED2CA034B81E6EF

d140f63ff050c572398da196f587775c

428C9AEA62D8988697DB6E96900D5439

a0e985519bf45379495ed9087e0c9e45

**C2**

requestupdate.live

linkrequest.live

supportsession.live

rythemsjoy.club

mailsession.online

## 参考链接：

[1] <https://ti.qianxin.com/blog/articles/donot-group-is-targeting-pakistani-businessman-working-in-china/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204095](/post/id/204095)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [APT](/tag/APT)
  * [恶意活动](/tag/恶意活动)

 **+1** __4赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

