**一直以来Buhtrap组织以其针对俄罗斯的金融机构和企业而闻名。** **在我们的跟踪过程中，发现并分析了该组织的主要后门以及其他工具。**

自2015年底以来，该组织变为以经济利益位目的的网络犯罪组织，其恶意软件出现于东欧和中亚进行间谍活动中。

2019年6月我们第一次发现Buhtrap使用0day攻击作。 同时我们发现Buhtrap在攻击过程中使用了本地提权漏洞CVE-2019-1132。  

在Microsoft Windows中的本地权限提升漏洞利用的是win32k.sys组件中的NULL指针取消引用产生的问题。
该漏洞发现后就已经向Microsoft安全响应中心报告，该中心及时修复了漏洞并发布了补丁。  

## 历史活动

下图中的时间表体现了Buhtrap活动中一些最重要的发展节点。  

![Timeline_Buhtrap.jpg](https://image.3001.net/images/20190712/1562916766_5d28379ecc17a.jpg!small)

在他们的工具在网上开源的时期，很难把该组织的活动和网络攻击行为联系在一起。
然而，由于该组织在目标的转变后发生了源代码泄漏的问题，我们迅速高效的分析了该组织攻击的恶意软件，明确了该组织针对的企业和银行目标，同时确认了该组织参与了针对政府机构的攻击。

尽管新的工具已经添加到他们的武器库中并且替换了旧版本，但是不同时期的Buhtrap活动中使用的策略、技术和程序并没有发生显着变化。
他们主要通过恶意文档作为载体，并广泛使用NSIS安装程序作为droppers。
此外，他们的一些工具会使用有效的代码签名证书进行签名，并利用已知的合法应用程序来作为攻击载体。

用于传递攻击载荷的文件通常为设计好的钓鱼文件，以避免在受害者打开时产生怀疑。对这些钓鱼文件为我们的分析提供了可靠的线索。
当Buhtrap目标为企业时，钓鱼文件通常是合同或发票。 下图是该组织在2014年攻击行为中使用的通用发票的示例。

![Fig-2.-decoy1.png](https://image.3001.net/images/20190712/1562917495_5d283a77ca265.png!small)当该组织将目标对准银行时，钓鱼文件通常与金融系统法规或Fincert的咨询有关，Fincert是俄罗斯政府创建的一个组织，为其金融机构提供帮助和指导。

![Fig-3.-decoy2.png](https://image.3001.net/images/20190712/1562917644_5d283b0cce0b8.png!small)因此，当我们第一次看到与政府行动有关的钓鱼文件时，我们立即开始跟踪这些行为。2015年12月，发现了第一批恶意样本，它下载了一个NSIS安装程序，该安装程序的作用是安装buhtrap后门，钓鱼文档如下图：  

![Fig-4.-decoy3.png](https://image.3001.net/images/20190712/1562917774_5d283b8ed84cf.png!small)文本中的URL很有特点，
它与乌克兰国家移民局网站dmsu.gov.ua非常相似。
该文本以乌克兰语要求员工提供他们的联系信息，尤其是他们的电子邮件地址，还试图说服他们点击文本中的恶意链接。  

这是我们遇到众多恶意样本中的第一个，这些样本被Buhtrap组织用于攻击政府机构。
我们认为另一个更近期的钓鱼文件也是由Buhtrap组织设计的，如图所示这个文件可以吸引与政府相关的另一类群体。  

![Fig-5.-decoy4.png](https://image.3001.net/images/20190712/1562917965_5d283c4d3922b.png!small)

## 0day攻击分析

该组织在0day攻击中使用的工具与其用于企业和金融机构的工具非常相似。
我们分析的第一批针对政府组织的恶意样本哈希为2F2640720CCE2F83CA2F0633330F13651384DD6A。
此NSIS安装程序下载包含Buhtrap后门的常规包，并显示如上文提到的2015年12月的钓鱼文档。  

从那以后，我们看到了针对这一政府组织群体的多次攻击。 攻击中经常使用漏洞来提升权限，以便安装恶意软件。
他们利用了旧的漏洞，如CVE-2015-2387。他们最近使用的0day也采用了相同的模式：利用漏洞以最高权限运行恶意软件。  

多年来，该组织使用了具有不同功能的软件包装。 最近，我们发现并详细分析了两个全新软件包，因为它们与该组织典型的工具集相比发生了变化。  

钓鱼文档包含一个恶意宏，启用后会删除NSIS安装程序。NSIS安装程序的任务是安装主后门。 但是此NSIS安装程序与此组织早期使用的版本不同，
它更简单，仅用于设置并启动嵌入其中的两个恶意模块。  

## 后门分析

第一个模块，称为“抓取器”，是一个独立的密码窃取程序。 它尝试从邮件客户端，浏览器中获取密码，并将它们发送到C＆C服务器。 此模块使用标准Windows
API与其C＆C服务器进行通信。  

![Figure-6-Grabber-module-network-capabilities.png](https://image.3001.net/images/20190712/1562919836_5d28439cd6e6d.png!small)第二个模块是我们从Buhtrap操作人员得到的：一个包含合法应用程序的NSIS安装程序，将用来安装Buhtrap主后门。利用的是一种免费的反病毒扫描程序AVZ。  

## Meterpreter和DNS隧道

本文档包含一个恶意宏，启用后会删除NSIS安装程序，该安装程序的任务是准备安装主后门。 安装过程的一部分是设置防火墙规则以允许恶意组件与C＆C服务器通信。
接下来是NSIS安装程序用于设置这些规则的命令示例：  

    
    
    ```
    
    cmd.exe /c netsh advfirewall firewall add rule name=\”Realtek HD Audio Update Utility\” dir=in action=allow program=\”<path>\RtlUpd.exe\” enable=yes profile=any  
    
    
    ```

最终的有效载荷是与Buhtrap传统工具完全不同的东西。 在其正文中加密了两个有效负载。
第一个是一个非常小的shellcode下载器，而第二个是Metasploit的Meterpreter。
Meterpreter是一个反向shell，允许其操作员完全访问被攻击的系统。  

Meterpreter反向shell实际上使用DNS隧道与其C＆C服务器进行通信。对于防御者来说，检测DNS隧道可能很困难，因为所有恶意流量都是通过DNS协议完成的，而不是常规的TCP协议。
以下是此恶意模块的初始通信片段。  

    
    
    ```
    
    7812.reg0.4621.toor.win10.ipv6-microsoft[.]org
    
    7812.reg0.5173.toor.win10.ipv6-microsoft[.]org
    
    7812.reg0.5204.toor.win10.ipv6-microsoft[.]org
    
    7812.reg0.5267.toor.win10.ipv6-microsoft[.]org
    
    7812.reg0.5314.toor.win10.ipv6-microsoft[.]org
    
    7812.reg0.5361.toor.win10.ipv6-microsoft[.]org
    
    […]
    
    ```

此示例中的C＆C服务器域名模仿Microsoft。 事实上攻击者注册了不同的域名，其中大多数都模仿微软域名。  

## 总结

虽然我们不知道为什么该组织突然转变目标，但它是说明了网络间谍团体与网络犯罪之间界限日益模糊。
目前还不清楚该组织中的一个或几个成员出于什么原因改变目标，但未来会有更多的攻击行为出现。  

### ##IOC

 **###ESET检测名称**

    
    
     VBA/TrojanDropper.Agent.ABM
    
    VBA/TrojanDropper.Agent.AGK
    
    Win32/Spy.Buhtrap.W
    
    Win32/Spy.Buhtrap.AK
    
    Win32/RiskWare.Meterpreter.G

 **###恶意软件样本**

Main packages SHA-1：

    
    
    2F2640720CCE2F83CA2F0633330F13651384DD6A  
    E0F3557EA9F2BA4F7074CAA0D0CF3B187C4472FF  
    C17C335B7DDB5C8979444EC36AB668AE8E4E0A72

Grabber SHA-1：

    
    
    9c3434ebdf29e5a4762afb610ea59714d8be2392

 **###C &C服务器**

[](https://hdfilm-seyret)

    
    
    <https://hdfilm-seyret>[.]com/help/index.php  
    <https://redmond.corp-microsoft>[.]com/help/index.php  
    dns://win10.ipv6-microsoft[.]org  
    <https://services-glbdns2>[.]com/FIGm6uJx0MhjJ2ImOVurJQTs0rRv5Ef2UGoSc  
    <https://secure-telemetry>[.]net/wp-login.php

 **###Certificates**

Company name | Fingerprint  
---|---  
YUVA-TRAVEL | 5e662e84b62ca6bdf6d050a1a4f5db6b28fbb7c5  
SET&CO LIMITED | b25def9ac34f31b84062a8e8626b2f0ef589921f  
  
**###MITRE ATT &CK techniques**

Tactic | ID | Name | Description  
---|---|---|---  
Execution | [T1204](https://attack.mitre.org/techniques/T1204/) | User
execution | The user must run the executable.  
[T1106](https://attack.mitre.org/techniques/T1106/) | Execution through API |
Executes additional malware through CreateProcess.  
[T1059](https://attack.mitre.org/techniques/T1059/) | Command-Line Interface |
Some packages provide Meterpreter shell access.  
Persistence | [T1053](https://attack.mitre.org/techniques/T1053/) | Scheduled
Task | Some of the packages create a scheduled task to be executed
periodically.  
Defense evasion | [T1116](https://attack.mitre.org/techniques/T1116/) | Code
Signing | Some of the samples are signed.  
Credential Access | [T1056](https://attack.mitre.org/techniques/T1056/) |
Input Capture | Backdoor contains a keylogger.  
[T1111](https://attack.mitre.org/techniques/T1111/) | Two-Factor
Authentication Interception | Backdoor actively searches for a connected smart
card.  
Collection | [T1115](https://attack.mitre.org/techniques/T1115/) | Clipboard
Data | Backdoor logs clipboard content.  
Exfiltration | [T1020](https://attack.mitre.org/techniques/T1020/) | Automated
Exfiltration | Log files are automatically exfiltrated.  
[T1022](https://attack.mitre.org/techniques/T1022/) | Data Encrypted | Data
sent to C&C is encrypted.  
[T1041](https://attack.mitre.org/techniques/T1041/) | Exfiltration Over
Command and Control Channel | Exfiltrated data is sent to a server.  
Command and Control | [T1043](https://attack.mitre.org/techniques/T1043/) |
Commonly Used Port | Communicates with a server using HTTPS.  
[T1071](https://attack.mitre.org/techniques/T1071/) | Standard Application
Layer Protocol | HTTPS is used.  
[T1094](https://attack.mitre.org/techniques/T1094/) | Custom Command and
Control Protocol | Meterpreter is using DNS tunneling to communicate.  
[T1105](https://attack.mitre.org/techniques/T1105/) | Remote File Copy |
Backdoor can download and execute file from C&C server.  
  
*** 本文作者：Kriston ，转载请注明来自FreeBuf.COM**  

