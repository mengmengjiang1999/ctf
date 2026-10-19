**在过去的几个月时间里，研究人员观察到了多个新型的恶意垃圾邮件活动。在这些攻击活动中，攻击者使用了一种多阶段恶意软件加载器来传播GootKit银行木马，而这个新出现的恶意软件名叫JasperLoader。**

![](https://image.3001.net/images/20190519/1558277750_5ce16e76409d0.jpg!small)

这个恶意软件加载器是思科Talos安全研究团队自2018年7月份至今，监测到的第三种加载工具了，而另外两款分别是[SmokeLoader](https://www.bleepingcomputer.com/news/security/400k-malware-outbreak-caused-by-backdoored-russian-torrenting-client/)和Brushaloader。SmokeLoader，又名[Dofoil](https://www.bleepingcomputer.com/news/security/microsoft-stops-malware-campaign-that-tried-to-infect-400-000-users-in-12-hours/)，网络犯罪分子在去年主要使用它来传播勒索软件或恶意挖矿Payload；
[Brushaloader](https://blog.talosintelligence.com/2019/02/combing-through-brushaloader.html)发现于2019年年初，它可以使用类似PowerShell脚本这样的LotL工具来隐藏自己的攻击&感染痕迹。

恶意软件加载器对于那些想把恶意Payload安插到目标用户设备中的网络攻击者来说，绝对是必不可少的工具，因为他们可以通过将恶意软件安装至符合攻击条件的计算机设备来实现自己的犯罪利益最大化。

思科Talos安全研究团队目前正在跟踪的恶意软件加载程序名叫JasperLoader，这款恶意软件的活动在过去的几个月内一直非常频繁，而且影响范围也越来越大。在此攻击活动中，主要的攻击目标为中欧地区的用户，而且其中大部分受害者都来自意大利和德国。

![](https://image.3001.net/images/20190519/1558277764_5ce16e841f3dd.png!small)

[研究人员表示](https://blogs.cisco.com/security/talos/jasperloader-emerges-targets-italy-with-gootkit-banking-trojan)：”JasperLoader使用了多阶段感染的攻击机制，并配合了多种代码混淆技术来增加安全检测和分析的难度。从感染过程的后期阶段来看，这款恶意软件的设计者既考虑到了软件弹性，也考虑到的可扩展性。”

在过去的几个月里，攻击者进行了多次恶意垃圾邮件活动来传播JasperLoader，并使用Gootkit银行木马（之前使用的是[DanaBot](https://www.bleepingcomputer.com/news/security/danabot-banking-trojan-gets-into-spam-business/)、[Neutrino漏洞利用工具](https://www.bleepingcomputer.com/news/security/former-major-player-neutrino-exploit-kit-has-gone-dark/)和
[Emotet](https://www.welivesecurity.com/2018/11/23/black-friday-special-emotet-filling-inboxes-infected-xml-macros/)来实现传播和感染）来感染目标设备，最终窃取目标用户的敏感信息。

而且在此攻击活动中，恶意软件和Payload等攻击组件都经过了本地化处理，以匹配其攻击目标（欧洲地区的国家）。除此之外，用于实现JasperLoader初步感染的恶意附件还包含有VBS脚本以及DOCM文档，其中还嵌入有恶意VBA宏，它们主要负责初始化恶意Payload的下载进程。

研究人员还发现了包含恶意JS下载器的消息，这些消息大部分都伪装成了合法邮件或恶意文件附件。比如说，某些活动中攻击者会在垃圾邮件内嵌入ZIP文件，而这些文件标题一般是“发票”等字样，但其中包含的却是恶意JavaScript文件和XML文件。

![](https://image.3001.net/images/20190519/1558277783_5ce16e974992d.png!small)

这些恶意垃圾邮件活动之所以非常危险，主要是因为攻击者使用了合法认证的电子邮件服务，比如说PEC电子认证服务，意大利、瑞士和香港等地区都回使用这个服务来对电子邮件进行签名认证，以帮助用户识别邮件的合法性。

JasperLoader恶意软件加载器在成功感染了目标设备之后，它会检测目标设备的地理位置，如果设备位于俄罗斯、乌克兰、白俄罗斯或中国的话，恶意软件将会立即停止运行。接下来，它会将自己的LNK快捷方式添加到受感染系统的启动项中，以此来实现持久化感染。

它还会生成一个BOT标识符，并根据这个标识符来向C2服务器发送或接收信息。当这个设备在攻击者的僵尸网络中完成注册之后，受感染设备会进入待机状态，并等待来自攻击者的控制命令。

JasperLoader还允许攻击者更新恶意软件加载程序，并运行基于PowerShell的任意系统命令。更重要的是，它会下载最终的Gootkit恶意软件Payload。

![](https://image.3001.net/images/20190519/1558277789_5ce16e9d36af2.png!small)

 ***
参考来源：[bleepingcomputer](https://www.bleepingcomputer.com/news/security/europeans-hit-with-multi-stage-malware-loader-via-signed-malspam/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**  

