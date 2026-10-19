## 前言

**TrickBot通过不断增加窃取用户凭证的新模块而不断进化，我们已发布的最新进展是关于它的pwgrab32模块。最近，我们又发现了一个新的POS相关的恶意模块，使得该银行木马更加危险。一旦受感染的计算机连接到支持POS服务和设备的网络，新模块将开始活动。**

我们目前正在研究恶意软件的作者是如何利用这些信息的，因为他们已经成功渗透了安装了POS相关服务的网络，但却没有获取信用卡，ATM或其他银行相关的特定数据。在此阶段，他们可能正在收集信息，以便为将来的入侵做准备。

## psfin32模块分析

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware.jpg)

新模块psfin32与其之前的信息收集模块类似，但做了一些修改，仅识别特定网络中POS相关的内容。该模块通过域控制器和基本帐户识别网络中的POS服务，并使用LDAP查询来访问Active
Directory服务（ADS，负责存储有关网络上对象的信息）。LDAP查询在全局编录的DNS主机名中搜索包含以下字符串的计算机：

POS | LANE | BOH  
---|---|---  
**REG** | **STORE** | **ALOHA**  
**CASH** | **RETAIL** | **MICROS**  
  
![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_2.jpg)

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_3.jpg)

如果未查询到任何信息，它还会根据以下内容对网络中的不同帐户或对象执行其他查询：

> sAMAccountName：用于支持旧版Windows操作系统版本，如Windows NT 4.0，Windows 95，Windows 98和LAN
> Manager

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_4.jpg)

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_5.jpg)

网站名称：

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_6.jpg)

组织单位（OU）：

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_7.jpg)

除域控制器外，它还使用UserAccountControl（UAC）8192向网络中具有基本帐户或用户的计算机发送查询。

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_8.jpg)

一旦TrickBot收集到了信息，它就会将信息存储到其预先配置的“Log”文件中，通过POST方式发送到其C＆C服务器Dpost上。如果无法访问C＆C服务器，则会提示“Dpost服务器不可用”，否则提示会显示“报告已成功发送”。

![](https://blog.trendmicro.com/trendlabs-security-intelligence/files/2018/11/trickbot_psfin32_POS-malware_9.jpg)

考虑到模块的部署时间，威胁参与者可能正在利用假期来收集和发送信息，特别是在Brad
Duncan在ISC上发表了相关报告之后，该报告讨论了针对美国的关于TrickBot宏的恶意垃圾邮件活动。虽然当时分析的样本文件和URL已无法访问，但依然对个人和企业起到警告作用：不要打开可疑的电子邮件，文件和附件。

## 防范策略

鉴于TrickBot的模块化特性，我们可以预期它会有更多的变种，使其更难以检测和防御。个人和企业可以通过多层防御使自己免受像TrickBot这样的银行木马侵害。同时确保只安装，下载和浏览白名单下的应用程序和站点。

## Indicator of Compromise

    
    
    SHA256
    
    [TrojanSpy.Win32.TRICKBOT.AL](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/TrojanSpy.Win32.TRICKBOT.AL)
    
    a9b00d12f7fa52209a8ead91bb595522effc0ab5e4dcfa02e0d145ae7ea1cb19

 ***参考来源：[trendmicro.com](http://blog.trendmicro.com/trendlabs-security-intelligence/trickbots-bigger-bag-of-tricks/)，xxx编译整理，转载请注明来自 FreeBuf.COM。**

