当你使用Smarter的物联网咖啡机，那么，问题来了。

[2015年](https://www.pentestpartners.com/security-blog/hacking-kettles-extracting-plain-text-wpa-psks-yes-really/)，Smarter产品首次暴露安全问题，研究人员发现他们可以恢复第一代Smarter iKettle咖啡机中使用的Wi-Fi加密密钥。

随后，再次发现第2代iKettle和当时更智能的咖啡机的版本还存在其他问题，比如没有固件签名、ESP8266（构成设备大脑的芯片组）内部没有可信赖的安全区域，导致黑客完全可能用恶意软件替换出厂固件。此外，研究人员EvilSocket还尝试对设备协议[进行了完整的逆向工程](https://www.evilsocket.net/2016/10/09/IoCOFFEE-Reversing-the-Smarter-Coffee-IoT-machine-protocol-to-make-coffee-using-terminal/index.html)，从而可以远程控制设备。

两年前，Smarter发布了iKettle 3和Coffee Maker 2，当时为Pen Test Partners工作的研究员Ken
Munro表示，更新的产品使用了新芯片组解决了之前的漏洞。但Smarter从未发布CVE漏洞称号，也没有公开警告客户不要使用旧版本，而来自[Wigle网络搜索引擎的数据](https://wigle.net/)表明，老式咖啡机仍在使用中。这意味着依然有大量脆弱的设备正在使用中。

为了测试，安全公司Avast的研究人员Martin Hron对其中一台较老的咖啡机进行了逆向工程，以查看风险。经过一周的测试，发现黑客可以做的事情非常多。

比如， **黑客可能会触发咖啡机，打开咖啡机的加热器，加水，旋转磨豆机甚至显示赎金消息，同时反复发出哔哔声。这时候，受害者唯一可以做的是，马上拔掉电源。**

这种情况还出现在其他的物联网设备上。事实上，这是一个典型的开箱即用（out-of-the-box）的问题。

当Martin Hron第一次插上Smarter咖啡机时，他发现它立即充当了Wi-Fi接入点，该接入点使用了不安全的连接来与智能手机应用程序进行通信。该应用程序反过来用于配置设备，如果用户选择，就可以将其连接到家庭Wi-Fi网络。由于没有加密，研究人员可以轻松了解手机如何控制咖啡机，而一个流氓手机应用程序可能会做同样的事情。

接下来，Martin
Hron检查了咖啡机用来接收固件更新的机制，这些更新是从手机接收的，而且没有加密，没有认证，也没有代码签名。这些明显的疏漏创造了新的“机会”。由于最新的固件版本存储在Android应用程序中，攻击者完全可以将其拉到计算机上，并使用IDA进行逆向，找到人类可读的字符串。

为了实际拆解固件（将二进制代码转换为与硬件进行通信的底层汇编语言），Hron必须知道咖啡机使用的CPU。这就需要他拆开设备内部零件，找到电路板，并识别芯片。以下两张图片显示了他的发现：

![](https://image.3001.net/images/20200928/1601271282_5f7175f255b8e360efd4b.png!small)![](https://image.3001.net/images/20200928/1601271324_5f71761c99bb2821e9ff7.png!small)以下是咖啡机主要组件的框图：

![](https://image.3001.net/images/20200928/1601269674_5f716faae86f33c0be627.png!small)

最后，获得了足够的信息，Martin Hron写出了一个python脚本，实现了入侵。

![](https://image.3001.net/images/20200928/1601269696_5f716fc0e67c265a6b52b.png!small)参考链接：

> [arstechnica](https://arstechnica.com/information-technology/2020/09/how-a-> hacker-turned-a-250-coffee-maker-into-ransom-machine/)

