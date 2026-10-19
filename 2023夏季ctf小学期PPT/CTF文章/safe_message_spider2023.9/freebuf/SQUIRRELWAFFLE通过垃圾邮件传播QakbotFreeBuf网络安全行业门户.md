最近，一种名为 SQUIRRELWAFFLE 的恶意家族正在通过垃圾邮件进行传播，这个家族可能将要成为垃圾邮件领域的下一个主导者。

SQUIRRELWAFFLE 在获取立足点后可以根据攻击者的意图来进一步进行感染。大多数情况下，它会分发 Qakbot 恶意软件或者 Cobalt
Strike。

## 垃圾邮件

电子邮件的威胁一直不断变化，不断有新兴的威胁出现。过去的几年中 Emotet 一直是该领域的主要威胁，但在 Emotet
家族被多国政府执法铲除后，尚未有组织能够填补这一空缺。

从 2021 年 9 月开始，研究人员发现许多带有恶意 Office 文档附件的垃圾邮件在大量传播。与 Emotet
类似，这些攻击活动利用被盗的电子邮件地址进行分发，内容看起来是对已有邮件的回复，通常还包含下载恶意 ZIP 文件的超链接。

![image.png-27kB](https://image.3001.net/images/20211113/1636808798_618fb85e58cee1c905778.png!small)

邮件的语言和原始邮件使用的语言是一致的，尽管大多数邮件都是英文的，但也有其他语言存在。根据分析，前五种语言分别是英语、法语、德语、荷兰语和波兰语。

![image.png-109.2kB](https://image.3001.net/images/20211113/1636808798_618fb85e9b295d0623a25.png!small)

自从 SQUIRRELWAFFLE 出现，与该威胁相关的垃圾邮件就保持着稳定传播，如下所示：

![image.png-147.5kB](https://image.3001.net/images/20211113/1636808799_618fb85f009c54dedd901.png!small)

尽管它的数量和 Emotet 相比还相差甚远，但随着攻击者的攻击范围扩展，僵尸网络的规模会进一步扩大。

## 感染流程

电子邮件中包含的恶意链接会下载恶意 ZIP 压缩包，解压缩所得到的恶意 Office 文件中 Word 文档和 Excel 电子表格各占一半。

![image.png-91.1kB](https://image.3001.net/images/20211113/1636808799_618fb85f643bd677f492b.png!small)

部署恶意 ZIP 文件的 URL 中包含拉丁文词汇，且路径结构如下所示：

> abogados-en-medellin[.]com/odit-error/assumenda[.]zip

同一个域名的不同路径下有不同的 ZIP 文件，其中的恶意 Office 文档命名如下所示：

> chart-1187900052.xls
>
> diagram-127.doc
>
> diagram_1017101088.xls
>
> specification-1001661454.xls

攻击链经过几次变更，目前几乎完全使用 Excel 实现攻击，本次描述最常见的两个感染链。

## 恶意 Word 文档

早期通常使用恶意 Word 文档完成攻击，看起来与 DocuSign 有关（DocuSign 是一个常见的文档共享和签名平台，通常用于交易等行为）。

![image.png-91.6kB](https://image.3001.net/images/20211113/1636808799_618fb85fc26e6c46ed3f7.png!small)

文档中包含恶意宏代码，受害者执行会触发 AutoOpen() 函数执行：

![image.png-140.2kB](https://image.3001.net/images/20211113/1636808800_618fb8602ebb9776e0ce6.png!small)

宏代码经过混淆，将 VBS 脚本写入 %PROGRAMDATA% 路径下并执行。

![image.png-538.7kB](https://image.3001.net/images/20211113/1636808800_618fb86092e9f1eef10c5.png!small)

脚本从硬编码的 5 个 URL 中下载 SQUIRRELWAFFLE 到本地存为 DLL 再调用 rundll32.exe 执行。

## 恶意 Excel 文档

另外一些使用 Excel 文档的攻击：

![image.png-163.4kB](https://image.3001.net/images/20211113/1636808802_618fb86272180470e7039.png!small)

文档中包含 Excel4 宏可以检索执行 SQUIRRELWAFFLE，整理后部分宏代码如下所示：

![image.png-386.6kB](https://image.3001.net/images/20211113/1636808802_618fb862d99760554ae22.png!small)

与 Word 文档类似，宏代码中也包含 3 个硬编码的 URL。下载的 DLL 文件通过 ShellExecuteA 和 regsvr-32.exe 执行。

## 攻击活动

最早在 2021 年 9 月 10 日这些恶意文件就出现在公众视野中，从 2021 年 9 月 13 日开始活动逐渐增强。

SQUIRRELWAFFLE 分发的 URL 结构与其日常活动有关，并且每隔几天就轮换一次：

![image.png-136.6kB](https://image.3001.net/images/20211113/1636808804_618fb8644b1b821c73199.png!small)

这种轮换逻辑在宏代码中也存在，宏函数名和哈希值都在轮换。下图显示了一些宏行数名和哈希值与攻击活动的对应关系：

![image.png-294.6kB](https://image.3001.net/images/20211113/1636808805_618fb865220089a656bf2.png!small)

这表明这些恶意文档可能都是使用自动构建工具制作而来。最近使用的 Excel 文件也经过精心设计，以降低通过 XLMDeobfuscator
等分析工具的静态分析效果。

## 基础设施

恶意软件的分发利用了之前的失陷主机，这些服务器很多都运行着 WordPress，最常见的是 WordPress 5.8.1。

在其中一个 SQUIRRELWAFFLE 的 C&C 服务器还发现了 AZORult
的控制面板。当然，这种易受攻击的服务器千疮百孔，尚不清楚这二者是不是由同一个攻击者管理的还只是被多个攻击者入侵了。

![image.png-126kB](https://image.3001.net/images/20211113/1636808805_618fb865ddc342d49cd1f.png!small)

2021 年 9 月 8 日，该服务器开始分发 SQUIRRELWAFFLE 之前，另一个服务器也被发现传播 ANTIBOT。

ANTIBOT 是网络钓鱼工具包，可以帮助攻击者规避分析。如果通过 IP、ASN
等方法确定访问请求来自安全分析平台、安全研究组织等需要逃避的对象，该工具将会响应 HTTP 404。该处理逻辑如下所示：

![image.png-296.3kB](https://image.3001.net/images/20211113/1636808806_618fb8665f04bf502f37d.png!small)

结合在 SQUIRRELWAFFLE 的 DLL 中的 IP
名单来看，攻击者努力要使攻击基础设施更难以被分析。通过各种限制措施，攻击者可能有效对抗大规模自动化分析。随着攻击者的更新运营，攻击基础设施在限制对恶意软件的访问上变得越来越多，并且基于地理位置等条件阻碍分析和跟踪。

## SQUIRRELWAFFLE

投递的 SQUIRRELWAFFLE 是一个 DLL 文件，通过 rundll32.exe 或 regsvr-32.exe 来执行，方法示例如下：

> cmd.exe /c rundll32.exe C:\ProgramData\\[DLL FILENAME],ldr

不指定参数直接运行 DLL 文件不会成功执行，攻击者以此来逃避沙盒的检测分析。

DLL 作为恶意软件的 Loader，已经发现 SQUIRRELWAFFLE 传播 Qakbot 和 Cobalt Strike。DLL
本身的逻辑十分简单，比较值得关注的是编码/解码 C&C 通信的部分：

![image.png-167.4kB](https://image.3001.net/images/20211113/1636808807_618fb8678ced43dffb31a.png!small)

## C&C 通信

恶意软件尝试通过包含混淆数据的 POST 请求与 C&C 服务器进行通信：

![image.png-111.3kB](https://image.3001.net/images/20211113/1636808808_618fb8684cc8a597eae4c.png!small)

发送的数据通过异或混淆后再进行 base64 编码。发送 POST 数据的 URL 由随机 1-28 个字符的字符串加上受害者的 IP
地址构成，其中一个反混淆如下所示：

![image.png-86.5kB](https://image.3001.net/images/20211113/1636808808_618fb868cd66b136fd256.png!small)

HTTP POST 请求的正文中包含失陷主机的相关信息：

  * 主机名
  * 用户名
  * Workstation 配置
  * %APPDATA% 配置

这四个信息分别通过 getenv()、GetComputerNameW()、GetUserNameW() 和 NetWkstaGetInfo()
获取，其中一个反混淆如下所示：

![image.png-129.9kB](https://image.3001.net/images/20211113/1636808809_618fb869394557e5a21bf.png!small)

C&C 服务器响应的混淆方法与发送相同，将状态码和其他内容作为响应返回，其中一个反混淆如下所示：

![image.png-185kB](https://image.3001.net/images/20211113/1636808809_618fb869ba6aa9e215f05.png!small)

## 结论

最近发现的 SQUIRRELWAFFLE 主要通过垃圾邮件进行传播，被观测到在野分发的包括 Qakbot 和 Cobalt
Strike，攻击者也在努力维护攻击基础设施的安全性。对此，组织应该加强纵深防御，确保对威胁能够预防并检测。

## 参考来源

>
> [TalosIntelligence](https://blog.talosintelligence.com/2021/10/squirrelwaffle-> emerges.html)

  

