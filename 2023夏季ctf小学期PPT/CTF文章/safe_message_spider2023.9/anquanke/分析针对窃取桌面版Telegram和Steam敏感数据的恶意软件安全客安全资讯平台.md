# 分析针对窃取桌面版Telegram和Steam敏感数据的恶意软件

阅读量 **189270**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-05-21 11:00:07

 **x**

##### 译文声明

本文是翻译文章，文章来源：https://blog.talosintelligence.com/

原文地址：<https://blog.talosintelligence.com/2018/05/telegrab.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01292822ff6cfa7e5f.png)

## 概述

在过去的近六周时间里，Talos团队监测到一种恶意软件的出现，该恶意软件会收集来自端到端加密即时消息服务Telegram的缓存和密钥文件。该恶意软件最早于2018年4月4日发布，在4月10日出现第二个变种。  
该恶意软件的最初版本只能窃取浏览器凭证、Cookie以及在系统上找到的所有文本文件。然而在第二个版本中，增加了收集Telegram缓存和密钥文件的功能，同时还会收集Steam网站的登录信息。  
根据Talos团队进行的情报研究，我们非常确信地识别出了该恶意软件的作者。该作者曾发布过几个YouTube视频，其中包含如何借助收集Telegram相关文件的方式劫持Telegram
Session，还包括如何将该恶意软件打包发布的说明。  
该恶意软件的使用者将窃取到的信息存放在几个pcloud.com账户上，账户信息以硬编码的形式保存在恶意软件之中。这些窃取到的信息没有经过任何加密，也就是意味着任何有权访问该账户的人都能够自由查看到已经泄露的信息。  
该恶意软件主要针对使用俄语的用户，并且有意规避了与匿名服务相关的IP地址。  
本分析文章由Talos团队的Vitor Ventura和Azim Khodjibaev撰写。

## 受恶意软件影响的版本和影响方式

该恶意软件不会破坏Telegram的基本功能，也不会利用Telegram中存在的任何漏洞。恶意软件只针对于Telegram的桌面版本，该版本不支持秘密聊天，并且其默认设置的安全性较低。  
  
上图截取自Telegram的官网，我们可以看到，官网明确指出，Telegram的桌面版和网页版不支持Secret
Chats（秘密聊天）功能。由于这些版本是基于云服务的，因此不会在本地存储聊天内容。该恶意软件利用了桌面版Telegram不包含秘密聊天的特性，同时利用了桌面版默认情况下无法超时自动注销登陆的设置，从而实现对Session的劫持，进而可以继续用户原有的对话。  
需要说明的是，该恶意软件从原理上没有使用Telegram的漏洞。此外，该恶意软件所使用的方法也无法用于移动版的秘密交谈功能。

## 对Telegram桌面版的数据收集

该恶意软件会收集Telegram所有的缓存数据，将这些数据压缩后上传到指定位置。  
  
经过调查，我们在网上发现了关于如何访问和使用这些信息来劫持Telegram会话的视频教程（ <https://youtu.be/fdwNm33-YJk>
）。总体来说，在打开会话后，将缓存和映射文件恢复到一个已有的Telegram桌面版安装包中，就可以实现对这些信息的访问。通过这种方式，可以查看被感染用户的会话、联系人和以前的聊天记录。Talos团队认为，该视频的发布者与恶意软件作者为同一个人。  
根据我们所掌握的信息，目前没有任何工具能够对缓存信息进行解密。在GitHub的TelegramDesktop资源库中，有一个讨论（
<https://github.com/telegramdesktop/tdesktop/issues/3545>
），其中提及到可以开发一个工具来解密缓存信息。  
在Telegram桌面版中，用于对文件进行加密的秘钥存储在map*文件中，这些文件会以用户的密码作为密钥进行加密。  
  
假设攻击者没有掌握这些文件的密码，他们其实可以采取暴力破解的方式以查看这些文件，这样的过程并不困难。上面的代码展示了如何借助已有组件来实现这一过程。由于Telegram使用了AES进行加密，因此我们可以使用OpenCL，或者为HashCat创建一个插件（
<https://hashcat.net/hashcat/> ）。  
攻击者只能访问本地缓存的数据。因此，我们要知道的是，在本地存储的所有内容都不具有安全性保证，唯一具有保证的是存储在云端的聊天记录。

## 恶意软件作者追溯

通过对该恶意软件众多变种的分析，我们最终追溯到了一个名为Racoon Hacker，也自称为Eyenot（Енот / Enot）或Racoon
Pogoromist的人，认定其为这一系列恶意软件的作者。  
根据对视频的大致分析，我们认为Racoon
Hacker是以俄语为母语，并且对Python编程语言有深入理解的人。尽管他并没有发布过太多帖子和视频，但他发布过的所有材料，都涉及到对用户账户的劫持或Payload的装载。在这些视频中，经常会提到与恶意软件变种所使用的相同的平台或技术。  
基于西里尔语的用户路径：  
  
在上图中代码的第一行，可以清楚地体现出，恶意软件作者使用的是基于西里尔的语言。用户主目录的解码使用CP-1251字符编码方案进行，而该方案主要用于俄语或乌克兰语。  
在Racoon Hacker发布的如何窃取Telegram会话的YouTube视频中（上文曾提到），我们发现有两个地方出现了用户enot。  
  
在lolzteam.net，一个自2017年秋季以来就一直活跃的中型俄罗斯黑客论坛上，有一个名为Racoon
Progoromist的用户发表了一篇题目为“2018年针对Telegram的破解”的文章，该文章主要讲述了恶意软件的自定义化过程。  
关于Telegram会话劫持工具的博客文章截图：  
  
在另一个中型黑客论坛sft.st中，出现了相同软件的广告信息，该广告包含了一个到GitHub中Python脚本和其他工具的链接，可以通过该脚本和工具复现演示视频中的过程。  
  
该GitHub账户的用户名为Enot272，目前已经删除了Python脚本，但我们有能力检索到该GitHub的内容列表。  
  
在该资源库中，还包含与视频相同文件名的文件，以及视频的链接。这样一来，我们就认为Racoon
Hacker与enot272具有较强的关联性。尽管Stealer_for_Telegram_Desktop资源库已被删除，但我们在撰写这篇文章时，enot272这一账户仍处于活跃状态。通过查看账户详情，我们发现了另外两个该恶意软件的变种。  
  
另外，这个GitHub账户使用的头像与YouTube账户所使用的头像相同，该账户只获得了两个Star，其中一个与恶意软件的变种之一使用了相同的API，同样将数据上传至pcloud.com云存储服务。这个API不是很流行，总共只获得了8个Star。  
在他发布的一个视频中（ <https://www.youtube.com/watch?v%3DX_RkraFAB9w>
），介绍了使用Autolt创建加载程序的方法，视频中展示了一个恶意软件样本，体现了与Racoon Hacker的关联。  
在视频的3分06秒，展示的是网站testytest1enot.ucoz.net的内容。在这里，我们看到dist1.txt和sdadasda.txt这两个文件名，与我们所掌握的两个样本完全一致，此外这个网址也与Dropper中找到的准确URL相符合。  
  
尽管加载工具是由另一个人编写的，但Telegrab也在使用相同的加载工具、投放工具进行分发。  
下图是从enotproject.exe逆向出的代码：  
  
最后，我们还在恶意软件的白名单URL列表中，发现了enot272这个关键词。

## 恶意软件详细分析

该恶意软件使用以不同语言编写而成的下载程序进行分发。经过我们的统计，发现至少使用了Go、AutoIT、Python和DotNet这四种不同的语言，其中DotNet语言只有其原型。其中，我们发现了一个编译成可执行文件的AutoIT脚本。  
  
在对AutoIT脚本进行反编译之后，我们发现该脚本可能是用于确认名为whiteproblem.exe的可执行文件finder是否已经成功下载，该可执行文件只是我们找到的文件名之一，更多请详见文末的IoC。  
一旦该文件下载之后，恶意软件存在两种基于可执行文件finder.exe的变种，是以Go语言编写而成的。第一个变种只使用finder.exe。第二个变种位于RAR自解压文件中，除了finder.exe之外，还具有一个Python
Stub可执行文件，其名称为enotproject.exe或dpapi.exe。  
自解压RAR文件的头部如下所示：  
  
在完成解压之后，finder.exe就会启动，在上图中可以看到其设置的变量。  
可执行文件finder.exe负责在默认用户的硬盘上搜索Chrome浏览器凭据和会话Cookie。在搜索硬盘的过程中，它还会收集系统上的所有文本文件（.txt）。第二个变种在执行期间，还会启动第二个可执行文件enotproject.exe或dpapi.exe。  
这个可执行文件负责收集信息。收集到的数据会使用GitHub的开源库（ <https://github.com/yanmhlv/pcloud>
）上传到pcloud.com网站上。  
下图为对pCouldClint.Login()的调用过程：  
  
身份验证过程是使用预先硬编码到finder.exe之中的凭据来完成的。Talos团队在finder.exe样本中找到了5个pcloud.com账户。根据对相关代码的分析，我们发现在上传之前没有对收集到的数据进行任何加密。这也就意味着，拥有云服务凭据的任何人都能够访问收集到的信息，这对于被感染用户来说是非常危险的。  
第二个名为enotproject.exe或dpapi.exe的文件，是使用Python编写的，并且使用pyinstaller将其包装到可执行文件中。通过对时间戳的分析，我们发现dpapi.exe的生成时间比enotproject.exe更早，并且其代码也更加简单，由此可以说明该恶意软件的更新过程。  
针对enotproject.exe可执行文件，它增加了代码用于收集Telegram和Steam数据，同时新增的代码还会检查被感染用户的IP地址是否位于[https://enot272[.]neocities[.]org/IPLogger-output.txt的白名单之中。如果被感染用户的IP在白名单中，该恶意软件会自动退出。在这个白名单列表里，包含中国和俄罗斯的IP地址，以及其他国家的一些匿名服务IP。](https://enot272%5B.%5Dneocities%5B.%5Dorg/IPLogger-output.txt%E7%9A%84%E7%99%BD%E5%90%8D%E5%8D%95%E4%B9%8B%E4%B8%AD%E3%80%82%E5%A6%82%E6%9E%9C%E8%A2%AB%E6%84%9F%E6%9F%93%E7%94%A8%E6%88%B7%E7%9A%84IP%E5%9C%A8%E7%99%BD%E5%90%8D%E5%8D%95%E4%B8%AD%EF%BC%8C%E8%AF%A5%E6%81%B6%E6%84%8F%E8%BD%AF%E4%BB%B6%E4%BC%9A%E8%87%AA%E5%8A%A8%E9%80%80%E5%87%BA%E3%80%82%E5%9C%A8%E8%BF%99%E4%B8%AA%E7%99%BD%E5%90%8D%E5%8D%95%E5%88%97%E8%A1%A8%E9%87%8C%EF%BC%8C%E5%8C%85%E5%90%AB%E4%B8%AD%E5%9B%BD%E5%92%8C%E4%BF%84%E7%BD%97%E6%96%AF%E7%9A%84IP%E5%9C%B0%E5%9D%80%EF%BC%8C%E4%BB%A5%E5%8F%8A%E5%85%B6%E4%BB%96%E5%9B%BD%E5%AE%B6%E7%9A%84%E4%B8%80%E4%BA%9B%E5%8C%BF%E5%90%8D%E6%9C%8D%E5%8A%A1IP%E3%80%82)  
2018年4月10日，我们第一次捕获到带有收集Steam和Telegram信息功能的恶意软件变种版本。  
第三个版本的Python代码也被封装在一个py2exe可执行文件中。该代码类似于第二个变体中的enotproject.exe，但它是独立运行的。由于我们还没有得到这个变体的代码，因此我们暂时不清楚该恶意软件是如何收集信息的。根据时间戳显示，这个变体似乎是正在开发中的最新变体。  
此外，该恶意软件没有持久性相关机制，说明恶意软件使用者似乎只关注如何收集信息。

## 总结

值得注意的是，对Telegram会话进行劫持是该恶意软件最有趣的功能，尽管这种攻击方式受到了一定程度的限制，但还是会对被感染用户的通讯录和以往聊天记录造成风险。尽管该恶意软件在这一功能上没有利用任何漏洞，但收集这类信息的恶意软件并不常见。通过对该恶意软件的分析，我想应该引起加密通讯软件用户的警惕，提醒大家一定要注意软件的使用说明，避免危及自身的隐私安全。  
与大型犯罪组织所使用的大规模Bot网络相比，很多人都会以为这种威胁几乎可以忽略不计。然而，这种小型的恶意行动却在监控下持续进行，并且在不到一个月的时间收集到了成千上万个用户凭据，对被感染用户的隐私产生了巨大的影响。这些收集到的用户凭据和Cookie允许恶意攻击者以被感染用户的身份访问诸如vk.com、yandex.com、gmail.com、google.com这类网站，并获取到更多被感染用户的信息。我们分析的恶意软件样本并不复杂，但它的运行效率非常高。同时，恶意软件没有持久性机制，这意味着被感染用户需要被诱导手动执行恶意软件，但恶意软件不会在重启后自动再次运行。

本文翻译自https://blog.talosintelligence.com/
[原文链接](https://blog.talosintelligence.com/2018/05/telegrab.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/145439](/post/id/145439)

安全客 - 有思想的安全新媒体

本文转载自:
[https://blog.talosintelligence.com/](https://blog.talosintelligence.com/2018/05/telegrab.html)

如若转载,请注明出处： <https://blog.talosintelligence.com/2018/05/telegrab.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [数据收集](/tag/数据收集)
  * [样本分析](/tag/样本分析)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

