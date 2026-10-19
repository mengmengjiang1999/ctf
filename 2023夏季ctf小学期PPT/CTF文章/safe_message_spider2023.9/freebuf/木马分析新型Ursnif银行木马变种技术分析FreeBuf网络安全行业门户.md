![](https://image.3001.net/images/20210825/1629880009_6125fec9ca97563024d55.jpg!small)

## 概述

在这篇文章中，我们将跟大家分析一款名叫Ursnif的银行木马，这个木马也被称为Gozi，我们将会详细分析Ursnif银行木马的技术细节，以及它是如何使用[
_Cerberus_](https://www.revelock.com/en/blog/en/labs/new-cerberus-campaign-impersonates-amazon?hsLang=en)功能来自动化实现欺诈性银行交易的。

Ursnif是2007年发现的一种针对Windows系统的银行木马病毒，经过多年的发展，至今仍处于活动状态，它也是世界上传播最为广泛的木马之一，全球各地都有Ursnif银行木马的受害者。

在今年年初，德国银行用户也受到其恶意活动的影响，大约在今年的三月份，研究人员又发现了针对意大利银行的新型木马变种。由此可见，Ursnif银行木马背后的网络犯罪分子可一直没有闲着。

## 木马特性

Ursnif银行木马的不断进化和演变可能是由几种原因造成的，其中一个原因是在2015年左右，该恶意软件的源代码发生了泄漏，并被发布在了GitHub平台上。这样一来，任何网络犯罪分子或恶意软件开发人员都可以随意向其添加功能，并对恶意软件代码进行各种功能性改进，然后将其用于各种恶意攻击活动。

关于其功能，除了通常盗窃银行凭证和此类特洛伊木马中常见的其他类型信息外，我们还发现Ursnif能够收集有关受感染系统的活动信息，以及各种应用程序的用户凭证。除此之外，它甚至还能够跟踪网络和浏览活动、记录击键数据或存储收集到的数据，并将它们发送到攻击者控制的服务器中。

## 传播

关于Ursnif银行木马的传播技术，银行恶意软件一般都会通过恶意垃圾邮件活动来实现有效传播。在这种垃圾邮件活动中，攻击者一般都会制作伪装的钓鱼邮件，并声称邮件来自于官方机构、快递公司或发送发*票的公司等等。

这一切都是为了欺骗用户去下载邮件中的附件，而附件一般都是Microsoft
Office文档，并使其宏功能来继续延展其恶意活动，以便最终感染目标用户的计算机。

![](https://image.3001.net/images/20210825/1629880023_6125fed704a2766ece6a6.png!small)

比如说，研究人员在去年曾发现了一次利用意大利机构INPS（属于公共系统的一个实体）来作为邮件主体的攻击活动。在此次活动中，攻击者尝试欺骗用户打开邮件附件，但必须输入电子邮件中显示的密码。用户一旦点击并输入了相关数据，恶意软件便会与远程服务器建立通信，并将恶意DLL下载到目标用户的计算机上，最终实现感染目标系统的目的。

## 联合攻击

到目前为止，我们已经了解了Gozi过去通常是如何运作的。但正如我们在开始时所讨论的，最近研究人员发现了此银行木马的新版本，它们与Cerberus有关。而Cerberus是一种针对Android平台的银行木马，自2019年被发现以来一直广受网络犯罪分子的欢迎：

![](https://image.3001.net/images/20210825/1629880033_6125fee1e67a397bb3496.png!small)

    
    
    IOc Cerberus + APK: 40b8a8fd2f4743534ad184be95299a8e17d029a7ce5bc9eaeb28c5401152460d

具体来说，我们将讨论Gozi与Cerberus恶意软件之间的关系，以及它的一些功能如何被用于自动化实现针对意大利银行的欺诈性银行转账。

Ursnif除了感染目标用户的桌面操作系统外，还会尝试诱使目标用户在其移动设备上下载欺诈性应用程序，并最终用Android银行木马感染其设备。

 **下面显示的是相关的控制服务器和欺诈域名：**

![](https://image.3001.net/images/20210825/1629880048_6125fef0d7df9d81a101b.png!small)

## 验证代码接收和交易自动化

研究人员在对新版本的Ursnif银行木马进行分析后发现，Ursnif开发者正在使用Cerberus恶意软件的组件来接收银行发送给用户的双因素身份验证消息，以确认账户之间的银行转账。因此，在这一方面和这一阶段，Ursnif使用了Android木马的功能，使得攻击者能够通过银行发送的短信代码逃避验证。

关于欺诈交易自动化，在本文分析的样本中，Ursnif的目的之一是自动化执行受感染Windows系统中浏览器以前曾启动过的事务。这样一来，Ursnif就可以将国际银行账号（IBAN）和银行识别码（BIC）更换为一个攻击者可以控制的账号了。

## 总结

Ursnif是2007年发现的一种针对Windows的银行木马病毒，经过了多次修改并经过多年的演变，目前是传播和影响最为广泛的木马程序之一，影响着世界各地的实体，特别是意大利银行实体的用户。近期，我们又检测到了新版本的Ursnif银行木马，其中还使用了Cerberus恶意软件的功能。

由于Ursnif在将来肯定还会继续不断进化并演变出新的变种版本，我们还将继续关注Ursnif的“一举一动”。

## 参考资料

> [ _https://securityintelligence.com/posts/ursnif-cerberus-android-malware-> bank-transfers-italy_](https://securityintelligence.com/posts/ursnif-> cerberus-android-malware-bank-transfers-italy)
>
> [
> _https://www.f-secure.com/v-descs/trojan_w32_ursnif.shtml_](https://www.f-secure.com/v-descs/trojan_w32_ursnif.shtml)
>
> [ _https://blog.avast.com/ursnif-victim-> data﻿_](https://blog.avast.com/ursnif-victim-data)

