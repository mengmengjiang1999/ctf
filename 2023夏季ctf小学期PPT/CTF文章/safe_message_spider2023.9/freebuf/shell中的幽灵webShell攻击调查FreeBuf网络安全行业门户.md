**近期发现某服务器配置错误，攻击者可在web服务器上的多个文件夹中部署webshell，导致服务帐户和域管理帐户被攻击。攻击者使用net.exe执行侦察，使用nbstat.exe扫描其他目标系统，最终使用PsExec横向移动。**

攻击者在其他系统上安装了额外的web shell，并在outlookweb
Access（OWA）服务器上安装了DLL后门。为了在服务器上持久控制，后门将自己注册为服务或Exchange传输代理，从而允许它访问和拦截所有传入和传出的电子邮件，并收集敏感信息。后门程序还执行其他攻击命令以及下载恶意有效载荷。此外，攻击者还发送了特殊电子邮件，DLL后门会将其解释为命令。  

![1.PNG](https://image.3001.net/images/20200206/1580965555_5e3b9eb3f19d5.png!small)  

这起案件是常见的web攻击之一，影响到各个部门的多个组织。常用web开发编程语言（如ASP、PHP、JSP）编写恶意代码，攻击者将其植入web服务器上，可远程访问和代码执行，通过执行命令从Web服务器窃取数据。

## 当前形势下Web Shell攻击

在攻击中观察到包括 [ZINC](https://blogs.microsoft.com/on-the-issues/2017/12/19/microsoft-facebook-disrupt-zinc-malware-attack-protect-customers-internet-ongoing-cyberthreats/),
[KRYPTON](https://www.microsoft.com/security/blog/2017/12/04/windows-defender-atp-machine-learning-and-amsi-unearthing-script-based-attacks-that-live-off-the-land/)和
[GALLIUM](https://www.microsoft.com/security/blog/2019/12/12/gallium-targeting-global-telecom/)多个shell。为了植入webshell，攻击者利用暴露在互联网上的web服务器安全漏洞进行攻击，通常是web应用程序中的漏洞，例如CVE-2019-0604或CVE-2019-16759。  

在对这些类型的攻击的调查中，发现文件中的web shell试图使用web服务器中合法文件名称隐藏或混合，例如：  

> index.aspx
>
> fonts.aspx
>
> css.aspx
>
> global.aspx
>
> default.php
>
> function.php
>
> Fileuploader.php
>
> help.js
>
> write.jsp
>
> 31.jsp

China Chopper是最常用的web shell之一，常见示例如下：  

![1.PNG](https://image.3001.net/images/20200206/1580966480_5e3ba250c33a0.png!small)服务器中发现的jsp恶意代码如下：

![1.PNG](https://image.3001.net/images/20200206/1580966571_5e3ba2ab02503.png!small)php语言编写的China
Chopper变体：

![1.PNG](https://image.3001.net/images/20200206/1580966751_5e3ba35fe9a83.png!small)KRYPTON在一个ASP.NET页面中使用了用C#编写的web
shell：  

![1.PNG](https://image.3001.net/images/20200206/1580966869_5e3ba3d561371.png!small)

一旦web
shell成功插入web服务器，攻击者就可以在web服务器上执行各种任务。Webshell可以窃取数据，漏洞攻击，并运行其他恶意命令进一步进行破坏。

Web
shell已经影响到了很多行业，公共部门组织是最常见的目标部门之一。除了利用web应用程序或web服务器中的漏洞外，攻击者还利用服务器中的其他弱点。例如缺少最新的安全更新、防病毒工具、网络保护、安全配置等。攻击通常发生在周末或休息时间，这时攻击可能不会立即被发现和响应。这些漏洞攻击很普遍，每个月微软（ATP）平均会在46000台不同的机器上检测到77000个webshell相关文件。

![1.PNG](https://image.3001.net/images/20200206/1580967986_5e3ba832cf6d5.png!small)

## 检测与预防

由于webshell是一个多方面的威胁，企业应该从多个攻击面建立全面的防御：身份验证、终端、电子邮件和数据、应用程序和基础架构等。  

了解面向internet的服务器是检测和解决web威胁的关键。可以通过监视web应用程序目录中的文件写入来检测web shell的安装。Outlook
Web Access（OWA）这样的应用程序在安装后很少更改，对这些应用程序目录的写入应该被视为可疑操作。  

通过分析信息服务（IIS）w3wp.exe创建的进程来检测webshell活动。与侦察活动相关联的进程序列，如net.exe、ping.exe、systeminfo.exe和hostname.exe进程序列。w3wp.exe在通常不执行诸如“MSExchangeOWAAppPool”进程的应用程序池中运行的任何cmd.exe进程都应被视为异常并视为潜在的恶意行为。  

![1.PNG](https://image.3001.net/images/20200206/1580969009_5e3bac31eae93.png!small)

![2.PNG](https://image.3001.net/images/20200206/1580969024_5e3bac40ced9e.png!small)

![1.PNG](https://image.3001.net/images/20200206/1580969100_5e3bac8ceb804.png!small)

与大多数安全问题一样，预防至关重要。通过采取以下预防措施可以增强系统抵御webshell攻击的能力：

> 1、识别并修复web应用程序和web服务器中的漏洞或错误配置，并及时进行更新。  
>
>
> 2、经常审核和检查web服务器的日志，注意直接暴露在internet上的所有系统。  
>
>
> 3、尽可能利用Windows Defender防火墙、入侵防御设备和网络防火墙来阻止端点之间的命令执行和与控制服务器通信，限制横向移动和其他攻击活动。  
>
>
> 4、检查外围防火墙和代理以限制对服务的不必要访问，包括通过非标准端口访问服务。  
>
>
> 5、启用云保护以获得最新防御措施。  
>
>
> 6、教育终端用户如何预防恶意软件感染，建立用户是要进行凭据限制。  
>

 ***参考来源：[microsoft](https://www.microsoft.com/security/blog/2020/02/04/ghost-in-the-shell-investigating-web-shell-attacks/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

