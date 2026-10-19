Cisco Talos的安全专家发现了一个远程代码执行漏洞，这个漏洞会影响2018.009.20050和2017.011.30070以及更早版本的Adobe
Acrobat Reader DC。

Cisco Talos的安全专家分享了追踪CVE_2018_4901远程代码执行漏洞的详细信息，这个漏洞会影响Adobe Acrobat Reader
DC。

一个远程攻击者能够通过漏洞，哄骗受害者打开一个恶意文件或者浏览一个特定的页面。

这个缺陷影响2018.009.20050和2017.011.30070以及更早版本的Adobe Acrobat
Reader。这个漏洞发现于12月7日，Adobe在2月13日才发布。

Talos团队发表的分析表明：“Adobe Acrobat
Reader是最受欢迎同时也拥有最丰富的功能的PDF阅读工具。它拥有非常广泛的用户群，通常是系统中默认的PDF阅读器，也经常作为一个展示PDF的插件整合到浏览器中。因此，通过欺骗用户浏览一个恶意web页面或者发送一个特制的电子邮件附件，就足以触发这个漏洞。”

![Adobe-Acrobat-Reader-DC.jpg](https://image.3001.net/images/20180301/1519874962586.jpg!small)

Adobe把这个缺陷归类到等价于“important”的“priority
2”，这就意味着对于开发而言，存在着“高风险”。好消息是在互联网环境中还没有发现已知的漏洞利用。

研究人员表示，这个缺陷可以被攻击者用于在PDF文件中嵌入恶意JavaScript代码，当打开一个特制的PDF文档时，这段恶意代码就会利用文档ID执行未授权的操作，然后触发一个基于堆栈的缓冲区溢出。

Talos补充道：“嵌入在 PDF 文件中的特定 Javascript 脚本可以使文档 ID 字段在无限的复制操作中使用, 从而在 Adobe
Acrobat 读取器中打开特制的 PDF 文档时导致基于堆栈的缓冲区溢出。”

Talos的研究员也公布了Snort规则45102-3，管理员可以利用该规则检测攻击行为。

*参考来源：[Security Affairs](http://securityaffairs.co/wordpress/69639/hacking/adobe-acrobat-reader-flaw.html),丁牛网安实验室小编EVA编辑,如需转载请注明来源  

