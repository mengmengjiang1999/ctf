****

**首先，在这里我要向大家道声抱歉！原本在去年圣诞节时，我就承诺要为大家做这个分享的。但由于一直忙于手头的各种琐事，所以一直拖到了现在。话不多说，我们直切正题！**

## 什么是XML/XXE注入？

 **外部实体注入攻击：**
XML文件的解析依赖libxml库，而libxml2.9以前的版本默认支持并开启了外部实体的引用，服务端解析用户提交的xml文件时未对xml文件引用的外部实体（含外部普通实体和外部参数实体）做合适的处理，并且实体的URL支持file://和php://等协议，攻击者可以在xml文件中声明URI指向服务器本地的实体，从而就会发生这种攻击。

例如，以下是一个用于漏洞利用的PoC代码：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741694_5b5bc83e63da8.png!small)

## 任务：

在渗透测试期间，我需要对一个托管文档和文件的Web应用程（如SharePoint）进行审计，以将其分享给其他的同事使用。经过一番测试，我找到了一些XSS/CSRF漏洞，并成功绕过防护机制。这个应用有一个特性引起了我的关注，它可以上传Microsoft文档格式，如.Docx。

我记得，我的一个朋友当时通过一个嵌入的XML代码就成功拿下了Facebook的服务器。

感谢[@bbuerhaus](http://twitter.com/bbuerhaus) 和
[@nahamsec](http://twitter.com/nahamsec)托管XXE服务（一个可以通过XXE预定义payload生成Microsoft文件的服务）。

以下是我的第一个payload：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741711_5b5bc84fd10ca.png!small)

可以看到通过NC，172.28.1.116成功与我建立了连接！

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741731_5b5bc863ec786.png!small)

现在，我们能做些什么呢？

由于我知道当前我处理的系统为Windows，因此不能像在Linux中那样读取像/etc/passwd这样的敏感文件路径。我唯一想到的就是，Windows的系统配置文件/windows/win.ini。还好当时坐在我旁边的同事提醒我：“关于Windows最重要的是NTLM哈希”。

这一次我修改了我的payload，并将其指向了我的共享IP地址：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741793_5b5bc8a115810.png!small)

B00M :D

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741812_5b5bc8b485cbb.png!small)

我能够从SSL证书扫描中识别其他服务器（处理不同环境的相同角色），以及最重要的是SMB消息没有签名！

这些信息足以让我们对其发起SMB中继攻击：

首先，让我们尝试做一些基本的RCE :( Ping）

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180730/15329227863262.png!small)

通过抓包工具可以清楚的看到ping的完整过程：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741846_5b5bc8d6034b4.png!small)

让我们来创建一个用户：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741862_5b5bc8e68fdce.png!small)

将他添加到管理员组后，我可以在服务器上做一个RDP远程桌面连接。

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741878_5b5bc8f642582.png!small)

好吧，我承认当时我还并不知道Impacket有一个很nice的用于转储SAM文件的功能。如果我们只是想指向中继服务器的IP，则不需要添加任何其它参数：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741899_5b5bc90ba1fb8.png!small)

现在我们获取到了管理员的哈希。让我们在网络中删除哈希，看看会有什么结果。

使用Metasploit中的smb扫描模块，我命中了41个扫描结果。真的是太棒了！

在对这些服务器使用PSExec exploit后，其中一个引起了我的关注：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532741922_5b5bc922c4d41.png!small)

B00M !!

![12_yT-OLE利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限KbeWTbc0vDvKDk4Q.png](https://image.3001.net/images/20180728/1532742037_5b5bc9957f7ae.png!small)

此帐户是域管理员的成员，让我们通过创建另一个用户来模拟该会话，但这次是：域管理员的成员；

![13_wgON8Rl4Mw0MYF0Hj95OXw.png](https://image.3001.net/images/20180728/1532742053_5b5bc9a57eaa7.png!small)![利用Windows上的XXE漏洞窃取用户NetNTLM
Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532742054_5b5bc9a67eb21.png!small)

让我们来验证下：

![利用Windows上的XXE漏洞窃取用户NetNTLM Hash并通过smb
relay获取权限](https://image.3001.net/images/20180728/1532742084_5b5bc9c4cc015.png!small)

使用此帐户，我可以访问所有DC，PC，甚至转储包含用户所有哈希值的NTDS.DIT文件 :D

## 总结

XXE漏洞对于企业内部网络来说破坏性不可小觑，特别是在满足所有条件的情况下（解析外部XML实体+SMB消息未签名）。

如果你正在处理JAVA，.NET，下面的链接内容可能会对你有所帮助

> <http://10-99.blogspot.fr/2013/02/definition-xml-external-entityxxe-is.html>
>
> <https://www.owasp.org/index.php/XML_External_Entity_%28XXE%29_Processing>

 ** *参考来源：[medium](https://medium.com/@canavaroxum/xxe-on-windows-system-then-what-76d571d66745)，FB小编 secist 编译，转载请注明来自FreeBuf.COM**

