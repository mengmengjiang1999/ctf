**原文链接：[The wolf is back](https://blog.talosintelligence.com/2020/05/the-wolf-is-back.html?m=1 "The wolf is back")**  
**译者：知道创宇404实验室翻译组**

泰国Android设备用户正受到“ WolfRAT”的DenDroid升级版的攻击，目前，它主要针对如WhatsApp，Facebook
Messenger和Line等社交软件。该升级版主要由臭名昭著的Wolf
Research进行操作。其操作水平相当业余，主要进行代码重叠，开源项目复制粘贴，类的实例化，不稳定的程序打包和不安全的面板操作。

## 相关背景

思科Talos根据DenDroid恶意软件系列的泄漏发现了一种新的Android恶意软件，由于该恶意软件（其命令和控制（C2）基础结构）与Wolf
Research之间的结构重合以及字符串的引用，因此我们将其命名为“ WolfRAT”。目前该开发团队似乎已经关闭，但黑客们还是非常活跃。

我们发现了一些针对泰国用户及其设备的攻击活动，部分C2服务器就在泰国。它的面板中有着泰文的JavaScript注释、域名还有泰式食品的引用，通过这些策略，诱使用户对这些面板进行访问，其过程并不复杂。

### 运作过程

该恶意软件模仿一些合法服务进程，如Google服务，GooglePlay或Flash更新。其操作主要是对于网络上大量的公共资源进行复制粘贴。

### 造成的后果

在被丹麦的威胁情报公司CSIS Group公开谴责之后，Wolf
Research被关闭但成立了一个名为[LokD](https://cyprusregistry.com/companies/HE/378592)的新组织，该组织致力于Android设备的安全保护。但由于设备的共享以及面板名被遗忘，我们认为该组织的黑客依然活跃而且还在进行开恶意软件的深层开发。此外，在C2面板上我们还发现了Wolf
Research与另一个名为Coralco Tech的塞浦路斯组织之间存在潜在联系，而这个组织还在进行技术拦截研究。

## WOLF INTELLIGENCE相关联系

2018年Virus Bulletin会议上，CSIS研究人员Beno tAncel和Aleksejs Kuprins作了关于[Wolf
Research](https://www.virusbulletin.com/blog/2018/10/wolf-sheeps-clothing-undressed/)和该组织开发的进攻性武器库的演讲。他们提到了Android，iOS和Windows远程访问工具（RAT）。他们在研究中发现Wolf总部位于德国、在塞浦路斯、保加利亚、罗马尼亚、印度和美国（可能）设有办事处，该组织之后被关闭，但管理者在塞浦路斯又创建了一个名为[LokD](https://cyprusregistry.com/companies/HE/378592)的新组织。这个新组织提议创建一种更安全的Android手机应用。在该组织的基础上，它开发了0day漏洞来测试其自己的产品：

![](https://images.seebug.org/content/images/2020/05/db0e0e00-af5c-41d2-a799-a34d66b8e349.png-w331s)

我们可以看到组织所有者对Android设备仍感兴趣。基于基础结构的重叠和泄露的信息，我们可以猜测出本文提到的恶意软件与Wolf Research之前的联系。

其中一个样本（e19823a1ba4a0e40cf459f4a0489fc257720cc0d71ecfb7ad94b3ca86fbd85d1）使用C2服务器
svcws[.]ponethus[.]com。基于我们的研究以及BenoîtAncel的观察得出Wolf Intelligence使用了C2此服务器：

![](https://images.seebug.org/content/images/2020/05/69c89194-94c7-422e-822c-f949f7f75184.png-w331s)

此外，我们在C2服务器上确定了两个面板。新版标题为“Coralco Archimedes”，旧版标题为“Wolf Intelligence”。

![](https://images.seebug.org/content/images/2020/05/21ecd42b-ab85-4866-b7e4-c67f42160bb6.png-w331s)
新面板

![](https://images.seebug.org/content/images/2020/05/aab41bdb-c03f-4824-b815-bf0aae0a3e3f.png-w331s)
旧面板

新面板名称中提到了“Coralco”，Coralco Tech是位于塞浦路斯的黑客组织，主要进行工具拦截。我们不能肯定地说Wolf
Research和Coralco Tech有关系，但根据名称之间的联系，可以说是高度疑似。

![](https://images.seebug.org/content/images/2020/05/d24e3288-16d3-44b9-b55a-e5c7165d3c9a.png-w331s)
Coralco Tech的服务说明

## 攻击活动中的受害者

我们分析针对泰国Android设备的攻击活动

![](https://images.seebug.org/content/images/2020/05/a7f4e7f5-c286-49da-8d0f-48cd4b10f45b.png-w331s)

C2服务器域链接到泰国美食：

  * Nampriknum[.]net: Nam Phrik Num

![](https://images.seebug.org/content/images/2020/05/9a4d94a6-aa42-43a2-ae9a-9313cad97979.png-w331s)

  * Somtum[.]today: Som Tum

![](https://images.seebug.org/content/images/2020/05/b17c944c-777a-40c1-a5bb-2f1975b8f04b.png-w331s)

前一章中提到的对C2基础设施的泰文注释

![](https://images.seebug.org/content/images/2020/05/be5c79d1-9c50-4c5a-8d13-eb43ec3c9075.png-w331s)

## 恶意软件

### DenDroid

Android恶意软件主要基于DenDroid
Android恶意软件，该恶意软件的分析报告于2014年发布，源代码于2015年泄漏，下表显示了操作者在受感染设备上执行任务时可用的命令。

![](https://images.seebug.org/content/images/2020/05/eb6af89a-7da4-47c0-a6d3-87f5dbbadfe2.jpg-w331s)

与某些Android恶意软件相比，该恶意软件过于简单。它没有利用易访问性框架，主要在相关设备上收集信息，这些命令显示了恶意软件所包含的功能。其中一些拍照，摄影录像和图片上载功能都集中在了间谍活动上。

#### 版本1

在我们的调查中，我们确定了RAT的至少四个主要版本。恶意软件第一版的权限奠定了间谍木马的基础。

![](https://images.seebug.org/content/images/2020/05/9a2ad509-e107-4e7f-9a37-04dffc238ff3.png-w331s)
权限

程序包名称遵循DenDroid上的原始样式名称，其代码没有进行打包有些已经混淆，此外该恶意软件还有一个屏幕录像功能。此功能是使用另一个开源软件包实现的，但在此处可以找到，该服务在清单中声明的`com.serenegiant.service.ScreenRecorderService`类中实现。在分析此样本时，我们还注意到该类别本身从未被恶意软件调用，它在源代码中仍然可用，但缺乏使用方法。

#### 版本2

这是第一个版本，显示的代码组织演变还将继续使用在整个恶意软件中。

![](https://images.seebug.org/content/images/2020/05/c275e9a6-44e6-44b1-bb77-76a0e4654095.png-w331s)

代码结构

与以前的版本比较其不会混淆代码，但他们还是相同的代码库。不同的是上一个示例中提到的屏幕录制功能已被删除，此外还添加了一个名为`com.utils.RestClient`的新类,这个类基于属于praeda包的公共代码包-muzikmekan，和上一个版本一样，恶意软件操作者没有使用这个包。

![](https://images.seebug.org/content/images/2020/05/43e183b8-1eae-4647-945c-9e954a8de608.png-w331s)
缺少权限

缺少屏幕录制功能可以证明缺少`READ_FRAME_BUFFER`权限是合理的,`ACCESS_SUPERUSER`可能已被删除，而RAT权限可以仅使用清单上声明的权限来实现，

#### 版本3

由于前两个版本之间存在一些重叠，在结合前两者的情况下得出了一个新的版本，其程序包名称更改为了`com.android.playup`。

此版本恢复了`ACCESS_SUPERUSER和READ_FRAME_BUFFER`权限。

![](https://images.seebug.org/content/images/2020/05/20a98e3c-5e08-40b7-ab2b-1dc335bfa1cd.png-w331s)
WhatsApp消息捕获

ScreenRecorderActivity调用服务`com.serenegiant.service.ScreenRecorderService`。在创建成功后，此服务器将启动一个线程，该线程将每隔50秒循环一次，屏幕会记录开始，在RAT确定WhatsApp未运行时才停止。WhatsApp是否运行决定下一个周期中是否启。

此外还添加了更多的类别。其允许与蓝牙接口进行交互，还有基于UDP的执行系统net/deacon。

![](https://images.seebug.org/content/images/2020/05/083f52fc-dd1a-4658-abfb-ac3771c90345.png-w331s) Android外形

添加了一个新程序包，该程序包允许在Android
Shell中执行命令。同样，此包源代码是公开可用的，可以在[此处](https://github.com/jaredrummler/AndroidShell/tree/master/library/src/main/java/com/jaredrummler/android/shell
"此处")找到。恶意软件提供给此程序包的用途之一是执行命令`dumpsys`，来确定某些活动是否正在运行。

![](https://images.seebug.org/content/images/2020/05/f124ba2e-b8dc-41e3-97ab-03a09162075e.png-w331s)
检查聊天应用程序是否正在运行

上述例子中，恶意软件正在搜索Line，Facebook
Messenger和WhatsApp活动。这是一个名为CaptureService类的一部分，该类在以前的版本中已经存在。

![](https://images.seebug.org/content/images/2020/05/573b957d-9f98-4e4b-a3d9-d69557b15978.png-w331s)
之前的前版本

捕获类赋予会对聊天应用程序拦截。在创建后，该类将开始获取截屏，一旦该服务找不到正在运行的目标应用程序，该截屏将停止并上传到C2服务器。此功能的核心也基于一个开源项目，可以在[这里](https://github.com/mtsahakis/MediaProjectionDemo/blob/master/src/com/mtsahakis/mediaprojectiondemo/ScreenCaptureImageActivity.java
"这里")找到。

另一个新颖之处是与VPN相关的软件包，它基于OrbotVPN。程序包`squareup.otto`也是如此，这是一个专注于Android实现的开源。这两个资源都可以在[这里](https://github.com/guardianproject/OrbotVPN/blob/master/src/org/torproject/android/vpn/OrbotVpnService.java
"这里")和[这里](https://square.github.io/otto/ "这里")找到。

#### 版本4

此版本增加了一些新增功能，一些未使用的功能被删除。首先，新的程序包名称为`com.google.services`，可以很容易将其与合法的Google服务混淆。因为VPN软件包不再存在，我们的想法进一步得到证实。

![](https://images.seebug.org/content/images/2020/05/b147162f-6385-4f0c-abf5-9c64b632138f.png-w331s)
WolfRAT应用程序

Google
GMS和Firebase服务已添加，但未找到任何配置。新类称为NotificationListener，它扩展了NotificationListenerService类，这将允许RAT接收系统通知。

![](https://images.seebug.org/content/images/2020/05/7794c8df-d904-40f5-a50c-9becfb60882f.png-w331s)
通知处理方法

该类仅在调试模式下应用，会将所有捕获的信息推送到日志中。在2020年使用PlusShare
API是一些不专业的开发，因为这是访问Google+的API。该服务连同API于2019年3月完全下线。

此版本添加了一个重要的类—它要求DEVICE_ADMIN特权。

![](https://images.seebug.org/content/images/2020/05/47cd3bff-8128-457b-9a67-768f0d6a85fd.png-w331s)
设备管理政策

查看策略的定义，我们可以得出它所列出的内容，即使大多已在Android 10.0上已被弃用，但使用还是出现访问异常。

### 版本概述

保持DenDroid代码库以及原始的base64编码的密码。

![](https://images.seebug.org/content/images/2020/05/c08c76d2-9cbf-4c69-881a-89812a7e05d4.png-w331s)
原始密码

结构类型与第一个版本相同，反分析功能是原始的，只检查模拟器环境，没有任何包装或混淆。若所有请求权限和设备管理权限被开启，恶意软件将启动自主服务。若没有开启，它将启动一个操作程序来欺骗用户开通权限。

每个样本都包含一个硬编码的`userId`，这意味着每个样本只能在受害用户中使用。由于IMEI与泄漏数据会被一起发送，如果同一受害用户拥有多个设备，恶意软件也可以被重复使用。目前，RAT还处于紧张的开发之中。

## 结论

我们看到操作者不断使用开源平台，代码和程序包来创建自己的软件。有些方法还很好，但有些还是欠缺考虑。我们观察到WolfRAT通过各种迭代演变而来，这表明该操作者在不断改进。

WolfRAT是一种专门针对的RAT，我们猜测它主要针对泰国人，根据Wolf
Research先前的工作，它最有可能用是作为情报收集工具或拦截工具，然后将其打包并以多种不同方式“出售”给客户。对于“商业”或“企业”用户，通常会引用“跟踪工具”或“管理工具”。Wolf
Research声称已关闭了他们的业务，但我们发现并非如此。

在电话上进行这类型的情报收集活动的对运营商而言是巨大的成功。我们看到WolfRAT还针对详细聊天信息，WhatsApp记录，聊天应用程序Line等采取了措施，这表明各类端口用户也会受到影响。

## 相关措施

用户以检测和阻止此威胁的方法如下：

![](https://images.seebug.org/content/images/2020/05/123797c6-e53d-4806-a2c2-36f322d11a63.png-w331s)

恶意软件防护（[AMP](https://www.cisco.com/c/en/us/products/security/advanced-malware-protection/index.html "AMP")）非常适合防止些黑客使用的恶意软件。AMP中的漏洞利用防护可以自动保护客户免受未知攻击的侵害。

思科云网络安全（[CWS](https://www.cisco.com/c/en/us/products/security/web-security-appliance/index.html
"CWS")）以及网络安全设备（[WSA](https://www.cisco.com/c/en/us/products/security/web-security-appliance/index.html "WSA")）扫描可防止恶意网站访问并对恶意软件进行检测。

电子邮件安全可以阻止黑客发送的恶意电子邮件。

[NGFW](https://www.cisco.com/c/en/us/products/security/firewalls/index.html
"NGFW")，[NGIPS](https://www.cisco.com/c/en/us/products/security/ngips/index.html
"NGIPS")，[Cisco ISR](https://www.cisco.com/c/en/us/products/routers/branch-routers/index.html "Cisco ISR")和[Meraki
MX](https://meraki.cisco.com/products/security-sd-wan/ "Meraki
MX")等网络安全设备可以检测与此威胁相关的恶意活动。

[AMP Threat Grid](https://www.cisco.com/c/en/us/products/security/threat-grid/index.html "AMP Threat Grid")可帮助识别恶意二进制文件并在所有Cisco Security产品中建立保护。

不论是公司网络还是私人网络，安全互联网网关（SIG）可以阻止用户连接到恶意域，IP和URL。

开源Snort订户规则集客户可以通过在[Snort.org](https://www.snort.org/products
"Snort.org")上下载最新版本的规则包来保持最新状态。

## IOCS

### Hashes

139edb1bc033725539b117f50786f3d3362ed45845c57fe1f82e7ed72b044367  
e19823a1ba4a0e40cf459f4a0489fc257720cc0d71ecfb7ad94b3ca86fbd85d1  
e19823a1ba4a0e40cf459f4a0489fc257720cc0d71ecfb7ad94b3ca86fbd85d1  
e5f346d8f312cc1f93c2c6af611e2f50805c528934786ea173cabc6a39b14cda  
1849a50a6ac9b3eec51492745eeb14765fe2e78488d476b0336d8e41c2c581d4  
d328fca14c4340fcd4a15e47562a436085e6b1bb5376b5ebd83d3e7218db64e7  
59b9809dba857c5969f23f460a2bf0a337a71622a79671066675ec0acf89c810  
120474682ea439eb0b28274c495d9610a73d892a4b8feeff268c670570db97e2  
ed234e61849dcb95223676abe2312e1378d6130c0b00851d82cda545b946ec83  
27410d4019251a70d38f0635277f931fb73f67ac9f2e1f3b475ce680ebfde12a  
6e6c210535b414c5aa2dd9e67f5153feeb43a8ac8126d8e249e768f501323a3e  
4a32ced20df7001da7d29edc31ca76e13eef0c9b355f62c44888853435e9794f  
ac5abaebd9f516b8b389450f7d27649801d746fb14963b848f9d6dad0a505e66  
3a45d7a16937d4108b5b48f44d72bb319be645cbe15f003dc9e77fd52f45c065

### Domains

cvcws[.]ponethus[.]com  
svc[.]ponethus[.]com  
www[.]ponethus[.]com  
webmail[.]ponethus[.]com  
nampriknum[.]net  
www[.]nampriknum[.]net  
svc[.]nampriknum[.]net  
svcws[.]nampriknum[.]net  
svc[.]somtum[.]today  
svcws[.]somtum[.]today  
www[.]somtum[.]today  
somtum[.]today  
shop[.]databit[.]today  
svc[.]databit[.]today  
test[.]databit[.]today  
www[.]databit[.]today  
admin[.databit[.today  
cendata[.]today  
svc[.]cendata[.]today  
svcws[.]cendata[.]today  
www[.]cendata[.]today

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1215/>

