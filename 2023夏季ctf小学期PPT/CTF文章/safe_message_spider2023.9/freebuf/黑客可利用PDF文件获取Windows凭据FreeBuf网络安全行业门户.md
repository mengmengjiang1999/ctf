**Check Point安全研究员Assaf Baharav透露，PDF文件可以被恶意行为者武装化，以窃取Windows凭证（NTLM
hashes）而无需任何用户交互，只需打开一个文件即可。**

![PDF-NTLM.png](https://image.3001.net/images/20180428/15248953141194.png!small)  

本周，Baharav发表了一项研究报告，展示了恶意行为者如何利用PDF标准中原生存在的功能来窃取NTLM
Hashes，这是Windows存储用户凭证的格式。

“PDF规范允许为GoToE＆GoToR加载远程内容”，Baharav告诉媒体称。

## 通过PDF和SMB窃取Windows凭据

对于他的研究，Baharav 创建了一个PDF文档，可以利用这两个PDF功能。当有人打开此文件时，PDF文档会自动向远程恶意SMB服务器发出请求。

按照设计，所有SMB请求还包含用于身份验证目的的NTLM hashes。这个NTLM
hashes将被记录在远程SMB服务器的日志中。可用的工具能够破解这个散列并恢复原始密码。

这种类型的攻击根本不算新鲜，而且过去是通过从Office文档，Outlook，浏览器，Windows快捷方式文件，共享文件夹和其他Windows操作系统内部函数启动SMB请求来执行的。

## 所有的PDF阅读器都可能存在漏洞

现在，Baharav 已经表明PDF文件同样危险。Check Point研究人员告诉媒体，他只对Adobe Acrobat和FoxIT
Reader的攻击进行了实地测试。

![pdf-readers-best.jpg](https://image.3001.net/images/20180428/15248967774948.jpg!small)  

“我们选择测试这两个比较普及的PDF阅读器，”Baharav 告诉我们。“关于其他人，我们更加怀疑其他阅读器也存在同样的弱点。”

“我们遵循90天的披露政策，只通知Adobe和福昕公司关于这些问题的信息，”Baharav 说。

虽然FoxIT没有回复，但Adobe表示它不打算修改其软件，而是推迟到Windows操作系统级缓解。Adobe工程师指的是2017年10月发布的Microsoft安全通报ADV170014。

微软发布了ADV170014，为用户如何在Windows操作系统上禁用NTLM
SSO身份验证提供技术机制和说明，希望利用向本地网络之外的服务器发出SMB请求来阻止NTLM hash的窃取。

Baharav 表示，“目前，最佳方法是遵循微软可选的安全增强措施。”

***参考来源：[BleepingComputer](https://www.bleepingcomputer.com/news/security/pdf-files-can-be-abused-to-steal-windows-credentials/)，由Andy编译，转载请注明来自FreeBuf.COM**

