**近日，亚信安全截获多个垃圾邮件的攻击活动，这些攻击活动使用的邮件附件通常是伪装成系统镜像ISO文件（亚信安全检测为Mal_GENISO）以及RAR和LZH压缩文档，其中包括使用AutoIt编译和.NET编译的Agent
Tesla间谍木马（也被称为Negasteal），亚信安全命名为TrojanSpy.MSIL.NEGASTEAL.KBE。**

在这些攻击活动中，垃圾邮件内容通常是伪造成装运建议、财务报表、信息咨询和预付款通知单等，利用社会工程学诱骗用户点击邮件附件。特别需要注意的是，有些攻击活动中使用镜像ISO文件来逃避检测，因为ISO镜像文件可用于绕过垃圾邮件过滤器，并且文件格式也更容易安装在最新的Windows版本上。

AutoIt是Windows图形用户界面的基本任务自动化的脚本语言，目前已经被滥用作为混淆的恶意软件二进制文件。对于Agent
Tesla间谍木马，AutoIt混淆技术分为两层：实际的恶意软件二进制文件被混淆为AutoIt脚本（.au3），然后使用Autout编译器（如Aut2Exe）将脚本编译为可执行文件。而通过使用.NET的混淆技术至少需要3层解密和去混淆才可以看到实际的恶意代码。

## 详细分析

近期截获的攻击活动对比：

**攻击时间** | 2019年10月 | 2019年11月--12月  
---|---|---  
**编译方式** | AutoIT编译 | .NET编译  
**传播方式** | 垃圾邮件 | 垃圾邮件  
**恶意行为** | 间谍木马 窃取信息 | 间谍木马 窃取信息  
**检测信息** | TrojanSpy.Win32.NEGASTEAL.DOCGC | TrojanSpy.MSIL.NEGASTEAL.KBE  
  
相关的垃圾邮件样本实例如下：

![](https://image.3001.net/images/20191226/1577348517_5e046da505073.png!small)

## Agent Tesla间谍木马攻击流程

![](https://image.3001.net/images/20191226/1577348527_5e046daf09bc5.png!small)

本次邮件攻击活动是批量生成和分发的，我们收到大量的带有ISO镜像附件的相关垃圾邮件，可以通过直接解压缩ISO镜像文件的方式获取到木马母体文件，具体如下所示：

![](https://image.3001.net/images/20191226/1577348535_5e046db76d25b.png!small)

![](https://image.3001.net/images/20191226/1577348543_5e046dbfd246a.png!small)

该母体文件是通过.NET编译，需要多层解密和去混淆。其中使用了BASE64加密和自行定义的异或加密等方式：

![](https://image.3001.net/images/20191226/1577348560_5e046dd0e3914.png!small)

![](https://image.3001.net/images/20191226/1577348566_5e046dd6bce37.png!small)

![](https://image.3001.net/images/20191226/1577348571_5e046ddbc2d82.png!small)

然后从资源文件获取相关数据并且解密：

![](https://image.3001.net/images/20191226/1577348592_5e046df0b29a4.png!small)

![](https://image.3001.net/images/20191226/1577348604_5e046dfc18ef9.png!small)

通过对相关注册表和文件的判断来检测是否运行在虚拟机中：

![](https://image.3001.net/images/20191226/1577348617_5e046e09037b2.png!small)

![](https://image.3001.net/images/20191226/1577348623_5e046e0f1797f.png!small)

该木马的主要恶意行为是记录用户的击键信息以及获取保存在浏览器中的用户名和密码，窃取用户敏感信息。

![](https://image.3001.net/images/20191226/1577348634_5e046e1aef005.png!small)

![](https://image.3001.net/images/20191226/1577348639_5e046e1fb0309.png!small)

主要窃取的浏览器应用程序为：谷歌浏览器、火狐浏览器、QQ浏览器和苹果的Safari浏览器等。

谷歌浏览器：

![](https://image.3001.net/images/20191226/1577348647_5e046e2749326.png!small)

火狐浏览器：

![](https://image.3001.net/images/20191226/1577348659_5e046e3324892.png!small)

Safari浏览器:

![](https://image.3001.net/images/20191226/1577348672_5e046e40138e2.png!small)

QQ浏览器:

![](https://image.3001.net/images/20191226/1577348682_5e046e4a45b39.png!small)

添加启动项和自删除:

![](https://image.3001.net/images/20191226/1577348694_5e046e56c4f9a.png!small)

![](https://image.3001.net/images/20191226/1577348703_5e046e5fa63d2.png!small)

## 解决方案

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打开系统自动更新，并检测更新进行安装；
>
> 请到正规网站下载应用程序；
>
> 浏览网页的时候不随意下载安装程序；
>
> 请注意备份重要文档。备份的最佳做法是采取3-2-1规则，即至少做三个副本，用两种不同格式保存，并将副本放在异地存储。

## IOC

**SHA-1** | **文件名** | **亚信安全检测名**  
---|---|---  
dda1ffebd498b09d8740d267f5fe452962f8048f | PL& PI.IMG | Mal_GENISO  
77a8e0a0a7bf3388767e17e733dbde7eed3ae638 | proforma inv and Packing list.exe |
TrojanSpy.MSIL.NEGASTEAL.KBE  
  
***本文作者：亚信安全，转载请注明来自FreeBuf.COM**

