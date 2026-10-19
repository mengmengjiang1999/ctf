***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **思科 Talos 研究员近期披露了在 Adobe Acrobat Reader DC 中的远程代码执行漏洞。 攻击者可以将恶意 JavaScript
代码隐藏在 PDF 文件中。这些代码可以启用文档 ID 来执行未经授权的操作，以在用户打开 PDF 文档时触发堆栈缓冲区溢出问题。**  

 **![adobe-security-patch.png](https://image.3001.net/images/20180301/1519874561784.png!small)  
**

按照 Talos 的说法，漏洞（CVE-2018-4901）在12月7日被披露，Adobe
对此漏洞在2月13日发布了安全更新。研究员随后公开了漏洞细节，漏洞影响的版本为 Adobe Acrobat Reader 的 2018.009.20050
以及 2017.011.30070 更早版本。

## 漏洞详情

> 嵌入在 PDF 文件中的 Javascript 脚本可能导致文档 ID 字段被无限地复制，这样会导致用户在 Adobe Acrobat Reader
> 中打开特定文档时触发一个导致堆栈缓冲区溢出问题。  
>
>
> ——Talos

Adobe Acrobat Reader 是最为流行且功能丰富的 PDF
阅读器。它拥有庞大的用户群，也通常是系统中的默认的PDF阅读器，常作为插件集成在网页浏览器中。
因此，该漏洞在被攻击者利用时也可通过诱导用户访问恶意网页或发送电子邮件附件而触发。

Adobe将该漏洞评为重要，这意味着该漏洞呈现出一定的风险，但目前没有发现已知的在野漏洞利用案例。

![talos.png](https://image.3001.net/images/20180301/1519874656336.png!small)  

更具体的漏洞信息仍可查看
[Talos](https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0505)

 *** 参考来源：[threatpost](https://threatpost.com/remote-code-execution-bug-patched-in-adobe-acrobat-reader-dc/130109/)，编译kylin，转载请注明FreeBuf.COM**

