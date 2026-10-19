***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **如今，许多攻击技术都在使用Microsoft
Office文档来分发恶意软件。近年来，[文档漏洞利用工具包构建器](https://www.proofpoint.com/us/threat-insight/post/unraveling-ThreadKit-new-document-exploit-builder-distribute-The-Trick-Formbook-Loki-Bot-malware)已经有了很多发展，更不用说红色绕过安全解决方案的[技巧](https://arno0x0x.wordpress.com/2017/11/20/windows-oneliners-to-download-remote-payload-and-execute-arbitrary-code/)。**  

与不需要用户交互的下载相比，基于文档的攻击通常包含某种社交工程组件。从被诱骗开放附件以启用宏，攻击者正在使用各种主题和鱼类网络钓鱼技术来感染他们的受害者。

今天我们来看看LibreOffice中的漏洞，LibreOffice是免费的开源办公套件，OpenOffice（现在是Apache
OpenOffice）可用于Windows，Mac和Linux。这个错误（[CVE-2018-16858](https://access.redhat.com/security/cve/cve-2018-16858)）是由[AlexInführ](https://twitter.com/insertScript/status/1091324665497337856)发现的，他负责地披露了这个错误，然后在他的[博客](https://insert-script.blogspot.com/2019/02/libreoffice-cve-2018-16858-remote-code.html)上发布了结果并附带了一个概念验证。

![LibreOffice套件远程代码执行漏洞](https://image.3001.net/images/20190309/1552108778_5c834cea41d9b.png!small)

攻击者可以利用此漏洞执行远程代码，这可能会导致系统崩溃。该缺陷使用鼠标悬停事件，这意味着必须欺骗用户将鼠标放在文档中的链接上。这会触发Python文件的执行（与LibreOffice一起安装）并允许传递和执行参数。

我们测试了[John
Lambert](https://twitter.com/JohnLaTwC/status/1092828811249410048)共享的几个payload。流程通常如下所示：

`soffice.exe -> soffice.bin -> cmd.exe -> calc.exe`

![LibreOffice套件远程代码执行漏洞](https://image.3001.net/images/20190309/1552108787_5c834cf34c16d.gif!small)

该漏洞已在LibreOffice中修补，但尚未在Apache
OpenOffice中修补。时间会告诉我这个漏洞最终是否会在野外使用。值得注意的是，不是每个人都使用Microsoft
Office，威胁参与者可以将其视为针对他们知道可能使用开源生产力软件的特定受害者。

 ***参考来源[malwarebytes](https://blog.malwarebytes.com/threat-analysis/2019/02/new-critical-vulnerability-open-source-office-suites/)，由周大涛编译，转载请注明来自FreeBuf.COM**  

