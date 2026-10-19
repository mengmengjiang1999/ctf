**今年年初谷歌的威胁分析小组（TAG）和Project
Zero团队发现了5条提权在野漏洞利用链。这些漏洞链来源不明，且会危害用户的iOS设备。攻击者利用入侵网站对iPhone用户实行水坑攻击，设备几乎覆盖iOS
10和iOS 12之间的所有版本，而且该网站的访问每周达数千次。**

![Apple_Target.jpg](https://image.3001.net/images/20190902/15674227645290.jpg!small)

Project Zero团队的Ian Beer表示，“这表明背后的攻击者至少在两年的时间内持续性地攻击某些社区的iPhone用户。”

##  iOS 0day漏洞和“集体”攻击

总的来说，谷歌安全研究人员发现14个iOS安全漏洞，分布在5条漏洞利用链当中。在这些漏洞中其中五个影响内核，七个影响iPhone网络浏览器，另外两个可以突破沙箱提权。其中一条漏洞利用链利用了0day漏洞CVE-2019-7287和CVE-2019-7286。在今年2月1日研究人员公开他们的发现之后，苹果于2月7日修补了这些漏洞，作为iOS
12.1.4更新的一部分。

以下是五条漏洞利用链的详细分析：

> [iOS Exploit Chain #1](https://googleprojectzero.blogspot.com/2019/08/in-> wild-ios-exploit-chain-1.html)
>
> [iOS Exploit Chain #2](https://googleprojectzero.blogspot.com/2019/08/in-> wild-ios-exploit-chain-2.html)
>
> [iOS Exploit Chain #3](https://googleprojectzero.blogspot.com/2019/08/in-> wild-ios-exploit-chain-3.html)
>
> [iOS Exploit Chain #4](https://googleprojectzero.blogspot.com/2019/08/in-> wild-ios-exploit-chain-4.html)
>
> [iOS Exploit Chain #5](https://googleprojectzero.blogspot.com/2019/08/in-> wild-ios-exploit-chain-5.html)

一旦用户访问这些网站，他们的iPhone设备就会立刻感染并且受到攻击，恶意软件会自动卸载、安装并且在用户的设备中运行。Beer补充说，“来者不拒，只要访问网站就可以让服务器攻击个人设备，如果攻击成功，就可以安装监控植入软件”。

##  以纯文本形式窃取用户数据

攻击成功之后即可在个人iPhone上以root用户身份运行未经过沙箱限制的代码。攻击者利用几个针对默认Safari网络浏览器的JSC
WebKit漏洞来发动攻击，而JSC WebKit漏洞则可以在iPhone上获得初步立足点。

虽然这些漏洞可以规避JIT代码注入缓解措施，但它们无法绕过具备A12处理器的iPhone，因为它们具有PAC新型JIT强化。这意味着iPhone
XS、iPhone XS Max和iPhone XR用户都受到了保护，免受这些攻击，因为如果他们在A12设备上运行，那么攻击者就无法利用JSC漏洞得逞。

![iOS
timeline.png](https://image.3001.net/images/20190902/15674227998801.png!small)

尽管攻击者植入的恶意软件能够实时窃取“信息、照片和GPS位置等私人数据”，但他们使用了硬编码命令，控制（C2）服务器IP地址和将所有数据以纯文本的形式发送到其C2服务器上。这显得攻击者在开发恶意软件时并不是那么老道。

窃取数据没有加密意味着，一旦连接到公共WiFi网络，这些信息将被传播给周围的每个人，包括网络运营商。任何中间网络都会转到命令和控制服务器。

![1.jpg](https://image.3001.net/images/20190902/1567422851809.jpg!small)

##  恶意软件能够进行实时数据泄露

虽然恶意软件将始终上传包含未加密数据（如信息）的容器目录，但对于硬编码第三方应用程序列表（包括但不限于WhatsApp，Telegram，Gmail，Skype和Facebook），也可以命令上传特定应用程序或iPhone上安装的所有应用程序数据。

已被攻击的用户无法检测恶意软件是否在他们的iPhone上运行，因为他们无法访问设备上所有正在运行的进程列表，这使得攻击者无需为恶意软件添加任何隐藏功能。

![Stealing WhatsApp
messages.png](https://image.3001.net/images/20190902/15674228986433.png!small)窃取WhatsApp消息  

虽然恶意软件无法在iPhone上长期存在，并且在设备重启后就会被删除，攻击者也可以窃取设备帐户凭据以获取各种服务，并在他们的恶意软件被清除后依然可以操控它们。

比尔总结道，“我们还要记住，这次对于攻击者来说是失败的。因为他们被揭露出来了，然而这仅仅只是冰山一角”。

***参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/google-warns-iphone-users-of-data-stealing-malware-attacks/)，Sandra1432编译，转载请注明来自FreeBuf.COM**

