## 写在前面的话

**在信息安全领域中，“无文件攻击”属于一种影响力非常大的安全威胁。攻击者在利用这种技术实施攻击时，不会在目标主机的磁盘上写入任何的恶意文件，因此而得名“无文件攻击”。然而，为了更好地应对“无文件攻击”，我们必须深刻理解这种攻击方式的底层实现技术，这样才能帮助我们在特定的环境下部署更好的防御策略。**

虽然有的网络系统部署了类似反病毒产品和应用程序白名单之类的安全控制措施，但是无文件攻击仍然可以结合多种其他的攻击策略来入侵你的网络。接下来，我们一起分析一下无文件攻击所采用的攻击方法以及策略，我们会对无文件攻击所涉及到的特定技术进行介绍，并解释为什么这种攻击方式在大多数情况下不会被安全防御系统发现。

## 技术一：恶意文档

其实一开始，很多安全研究专家所称之为的“无文件攻击”实际上是会涉及到文档文件的。在这种场景下，攻击者需要使用到恶意文档（例如电子邮件附件），目的有以下几种：

> 1、 文档作为携带其他文件的容器，灵活性更好。比如说，攻击者可以在Microsoft
> Office文档中嵌入恶意JavaScript文件，喜欢社工技术的攻击者还可以诱导目标用户双击文件后执行嵌入的脚本等等。其他类型的文档还可以携带PDF和RTF等类型的文件，这种功能属于应用程序的一种特性，所以反病毒技术一般不会干扰其使用。
>
> 2、
> 文档还可以携带漏洞利用代码或Payload。如今，文档的复杂程度越来越高，因此提供的攻击面也就越来越广。在这种场景下，漏洞利用代码可以直接在目标设备的内存中运行绑定的Shellcode，并给攻击者提供文件系统的完整读写权限。
>
> 3、 文档还可以执行恶意攻击流程并实现初始感染。现代文档提供了强大的脚本功能支持，比如说Microsoft
> Office能够执行VBA宏文件，这种功能将允许攻击者在不需要编译恶意可执行程序的情况下在目标主机上实现恶意逻辑，而这种技术利用的就是反病毒工具无法区分脚本代码恶意性的缺陷。除此之外，脚本还可以启动程序或下载恶意代码。

![2.png](https://image.3001.net/images/20181128/1543394059_5bfe530be168e.png!small)

只要攻击者制作的文档存储在了目标系统中，攻击者就已经不需要再通过传统方式（在目标主机中运行恶意可执行文件）来进行攻击了。在很多情况下，恶意文档可以直接在内存中执行恶意代码，从某种角度来看，这也算是一种“无文件攻击”了。

### 参考资料

【[参考资料一](https://blog.minerva-labs.com/prevented-by-minerva-labs-new-evasive-malware-technique-exploits-microsoft-dynamic-exchange)】【[参考资料二](https://blog.minerva-labs.com/attackers-insert-themselves-into-the-email-conversation-to-spread-malware)】

## 技术二：恶意脚本

为了不将恶意代码编译成传统的可执行文件，攻击者会在攻击过程中使用具有“无文件”性质的“脚本文件”。除了文档支持脚本之外，像上面提到的Microsoft
Office产品同样支持脚本功能，这就给攻击者提供了以下几个优势：

1、 他们可以在不受某些应用程序限制的情况下与操作系统进行交互。

2、 和恶意可执行程序想必，脚本可以增强反恶意软件产品检测和控制的难度。

3、 脚本可以更加方便攻击者将攻击逻辑分散到多个攻击步骤中实现，以躲避某些基于行为分析的安全检测机制。

4、 可以通过代码混淆来增加安全分析的难度，并绕过反病毒技术。

  
![3.png](https://image.3001.net/images/20181128/1543394099_5bfe5333dabc8.png!small)

MicrosoftWindows提供了针对PowerShell、VBScript、Batch和JavaScript等脚本的支持，这些脚本可以直接在powershell.exe、cscript.exe、cmd.exe和mshta.exe中运行。除此之外，攻击者还可以使用开源框架来对脚本代码进行混淆处理。

### 参考资料

【[参考资料一](https://docs.microsoft.com/en-us/windows/wsl/install-win10)】【[参考资料二](https://blog.minerva-labs.com/confronting-snake-oil-sales-tactics-in-endpoint-security)】【[参考资料三](https://github.com/danielbohannon/Invoke-Obfuscation)】【
[参考资料四](https://github.com/danielbohannon/Invoke-DOSfuscation)】【[参考资料五](https://blog.minerva-labs.com/the-emotet-grinch-is-back)】

## 技术三：无需任何依赖组件

每次谈到无文件攻击，或多或少都会涉及到滥用Microsoft
Windows实用工具的情况。这些工具允许攻击者在不需要编译恶意可执行文件的情况下实现攻击步骤的推进。

只要攻击者的恶意代码能够与目标主机的本地程序交互，他们就可以利用操作系统的内置工具来下载额外的恶意组件，启动脚本、窃取数据、实现横向渗透以及实现持续感染。这些工具包括但不仅限于regsvr32.exe、rundll32.exe、certutil.exe和schtask.exe等等。

值得注意的是，在操作系统的内置工具中，WMI则是重灾区，WMI内置于操作系统中，并允许攻击者通过wmic.exe并配合PowerShell脚本直接跟终端进行交互。

### 参考资料

【[参考资料一](https://github.com/api0cradle/LOLBAS)】【[参考资料二](https://www.blackhat.com/docs/us-15/materials/us-15-Graeber-Abusing-Windows-Management-Instrumentation-WMI-To-Build-A-Persistent%20Asynchronous-And-Fileless-Backdoor-wp.pdf)】【
[参考资料三](https://www.fireeye.com/blog/threat-research/2017/03/dissecting_one_ofap.html)】

## 技术四：内存中的恶意代码

毫无疑问，扫描磁盘文件肯定是反病毒产品必备的“技能”了，但是检测内存中的恶意代码可就不一定了。内存是动态变化的，这也给恶意软件提供了可乘之机。

内存渗透技术允许攻击者绕过大多数反病毒控制策略，包括应用程序白名单。虽然反病毒工具会尝试捕捉内存注入行为，但是攻击者的持续感染能力仍然会限制反病毒工具的效果。

### 参考资料

【[参考资料一](https://blog.minerva-labs.com/coffeeshot-avoid-detection-with-memory-injection)】【[参考资料二](https://blog.minerva-labs.com/analyzing-an-azorult-attack-evasion-in-a-cloak-of-multiple-layers)】【[参考资料三](https://github.com/PowerShellMafia/PowerSploit)】【
[参考资料四](https://securelist.com/synack-targeted-ransomware-uses-the-doppelganging-technique/85431/)】

![4.png](https://image.3001.net/images/20181128/1543394140_5bfe535cbb3c4.png!small)

## 总结

无文件攻击的实现得益于某些应用程序和操作系统所特有的性质，它利用了反恶意软件工具在检测和防御方面的缺陷。虽然在现代网络攻击活动中，无文件攻击只是其中的一种攻击技术，但很多恶意软件一般都会引入一些“无文件攻击”技术来尝试躲避安全产品的检测。对于攻击者来说，与其去思考某种技术是否无懈可击，还不如思考怎么样使用这些技术才能绕过企业的防御策略，这样效率还会更高。

 ***参考来源：[minerva-labs](https://blog.minerva-labs.com/deconstructing-fileless-attacks-into-4-underlying-techniques)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

