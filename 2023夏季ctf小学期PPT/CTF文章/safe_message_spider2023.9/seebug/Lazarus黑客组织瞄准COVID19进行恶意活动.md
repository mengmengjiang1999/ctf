**译者：知道创宇404实验室翻译组  
原文链接：<https://securelist.com/lazarus-covets-covid-19-related-intelligence/99906/>**

### 前言

在跟踪Lazarus组织的活动时，我们发现他们最近瞄准了与COVID-19相关实体。9月底，他们袭击了一家制药公司。此外，他们还袭击了与COVID-19有关的政府部门。而且，每一次攻击都使用了不同的战术、技术和程序（TTP）。

![](https://images.seebug.org/content/images/2020/12/c105641b-64fb-4f6e-adfd-3a087d22756f.png-w331s)

在这篇文章中，我们讲述了两个不同的事件。

第一起事件是针对政府卫生部的攻击：2020年10月27日，卫生部的两台Windows服务器遭到破坏。我们无法识别感染媒介，但攻击者能够在这些服务器上安装一个复杂的恶意软件集。这个恶意软件集名为“wAgent”，它的主要组件只在内存中工作，并从远程服务器获取额外的有效负载。

第二起事件涉及一家制药公司。这家公司在2020年9月25日被入侵。这一次，Lazarus组织通过一家韩国软件公司在供应链攻击中部署了此前由ESET[报告](https://www.welivesecurity.com/2020/11/16/lazarus-supply-chain-attack-south-korea/ "报告")的Bookcode恶意软件。

### wAgent恶意软件集

恶意软件集具有复杂的感染方案：

![](https://images.seebug.org/content/images/2020/12/febdbcc7-c50e-4c7c-a38f-565d7e1b5f5e.png-w331s)
wAgent恶意软件集的感染方案

不幸的是，我们无法获取此攻击中使用的启动程序模块。该模块使用特定的参数执行wAgent。我们收集到的其中一个wAgent样本有伪造的元数据，以使其看起来像合法的压缩实用程序[XZ-Utils](https://tukaani.org/xz/ "XZ-Utils")。

通过调用Thumbs export函数，该恶意软件使用以下参数通过命令行shell直接在受害者机器上执行：

    
    
    c:\windows\system32\rundll32.exe
    C:\Programdata\Oracle\javac.dat, Thumbs 8IZ-VU7-109-S2MY

16字节的字符串参数用作AES密钥，用于解密嵌入的有效负载——Windows
DLL。当嵌入式负载加载到内存中时，它使用给定的解密密钥解密配置信息。配置包含各种信息，包括C2服务器地址，以及稍后使用的文件路径。尽管配置指定了两个C2服务器，但它两次包含同一个C2服务器。有趣的是，这个配置有几个URL路径，用“@”符号分隔。恶意软件试图随机连接到每个URL路径。

![](https://images.seebug.org/content/images/2020/12/4bb8af73-cb55-47bc-ac5b-770b2a9a877f.png-w331s) 配置中的C2地址

首次执行该恶意软件时，它会生成标识符以使用随机的哈希值区分每个受害者。它还会生成一个16字节的随机值并颠倒其顺序。接下来，恶意软件使用“@”作为分隔符将这个随机的16字节值和哈希值连接起来。即：82UKx3vnjQ791PL2
@ 29312663988969

POST参数名称（如下所示）在运行时解密，并在每个C2连接中随机选择。值得注意的是，[Tistory](https://en.wikipedia.org/wiki/Tistory
"Tistory")提供韩国的博客发布服务，这意味着恶意软件攻击者熟悉韩国的互联网环境。

该恶意软件将生成的标识符编码为base64，并将其发布到C2。最后，代理从C2服务器获取下一个有效负载，并将其直接加载到内存中。不幸的是，我们无法获得它的副本，但根据遥测，获取的有效负载是包含后门功能的Windows
DLL。使用此内存后门，恶意软件攻击者执行了许多shell命令以收集受害者信息：

    
    
    cmd.exe /c ping -n 1 -a 192.[redacted]
    cmd.exe /c ping -n 1 -a 192.[redacted]
    cmd.exe /c dir \\192.[redacted]\c$
    cmd.exe /c query user
    cmd.exe /c net user [redacted] /domain
    cmd.exe /c whoami

### wAgent部署

通过使用wAgent后门，操作人员安装了一个额外的wAgent有效负载，它具有持久性机制。在获取这个DLL之后，使用以下命令执行一个名为SagePlug的导出：

    
    
    rundll32.exe 
    c:\programdata\oracle\javac.io,SagePlug4GO-R19-0TQ-HL2A c:\programdata\oracle\~TMP739.TMP

4GO-R19-0TQ-HL2A用作键，文件路径指示保存调试消息的位置。这个wAgent安装程序的工作原理类似于上面描述的wAgent
loader恶意软件。它负责在用命令行中的16字节密钥解密嵌入式有效负载后，再进行加载。在解密的有效负载中，恶意软件会生成一个文件路径来继续感染：

  * C:\Windows\system32[random 2 characters]svc.drv

该文件伪装成名为[SageThumbs Shell Extension](http://sagethumbs.sourceforge.net/
"SageThumbs Shell
Extension")的合法工具。该工具直接在Windows资源管理器中显示图像文件。但是，它内部包含一个附加的恶意例程。

创建此文件时，安装程序模块将使用随机数据填充该文件以增加其大小。恶意软件还会将cmd.exe的创建时间复制到新文件中，使其不那么容易被发现。

为了进行日志记录和调试，恶意软件将信息存储在作为第二个参数提供的文件中（在这种情况下为c:\programdata\oracle\〜TMP739.TMP）。此日志文件包含时间戳和有关感染过程的信息。我们观察到，攻击者正在使用Windows命令手动检查此文件。这些调试消息的结构与以前的恶意软件相同，该恶意软件用于攻击涉及Lazarus组织的加密货币业务。

之后，恶意软件会解密其嵌入的配置。该配置数据具有与上述wAgent恶意软件相似的结构。它还包含具有相同格式的C2地址：

  * hxxps://iski.silogica[.]net/events/serial.jsp@WFRForms.jsp@import.jsp@view.jsp@cookie.jsp 
  * hxxp://sistema.celllab[.]com.br/webrun/Navbar/auth.jsp@cache.jsp@legacy.jsp@chooseIcon.jsp@customZoom.jsp 
  * hxxp://www.bytecortex.com[.]br/eletronicos/digital.jsp@exit.jsp@helpform.jsp@masks.jsp@Functions.jsp 
  * hxxps://sac.najatelecom.com[.]br/sac/Dados/ntlm.jsp@loading.jsp@access.jsp@local.jsp@default.jsp 

该恶意软件会加密配置数据，并将其存储为带有其文件名的预定义注册表项：

  * HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\Emulate – [random 2 characters]svc 

通过将创建的文件路径注册到现有注册表值的末尾，它还利用了Custom Security Support
Provider。该DLL将在下一次启动时由lsass.exe加载。

  * HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Lsa – Security Packages : kerberos msv1_0 schannel wdigest tspkg pku2u [random 2 characters]svc.drv

最后，启动程序模块在远程进程中启动[random 2
characters]svc.drv文件。它搜索第一个svchost.exe进程并执行DLL注入。注入的[random 2
characters]svc.drv恶意软件包含用于解密和加载其嵌入式有效负载的恶意例程。最终的有效负载是wAgent，它负责从C2（可能是功能齐全的后门）中获取其他有效负载，并将其加载到内存中。

### Bookcode恶意软件集

Lazarus组织使用Bookcode恶意软件对制药公司进行攻击。该公司正在开发COVID-19疫苗，并被授权生产和销售COVID-19疫苗。在此之前，Lazarus曾用Bookcode恶意软件攻击了韩国的一家软件公司，可能是针对该公司的源代码或供应链。Lazarus组织在过去进行了鱼叉式网络钓鱼或战略性网站破坏，以传播Bookcode恶意软件。但是，我们无法确定初始的感染媒介。整个感染过程与ESET最新[报道](https://www.welivesecurity.com/2020/11/16/lazarus-supply-chain-attack-south-korea/ "报道")描述的过程非常相似。

![](https://images.seebug.org/content/images/2020/12/d55fed35-3758-459f-8d2d-e4a618befa95.png-w331s)
Bookcode感染程序

尽管我们没有发现负责部署加载程序及其加密的Bookcode有效负载的恶意软件，但我们能够识别出加载程序样本。该文件负责加载位于系统文件夹中的名为gmslogmgr.dat的加密有效负载。解密有效负载后，加载程序会找到带有winmgmt、ProfSvc或Appinfo参数的服务主机进程（svchost.exe），并将有效负载注入其中。不幸的是，我们无法获取加密的有效负载文件，但是我们能够在受害机器上重建恶意软件操作，并将其识别为Bookcode恶意软件。

执行后，Bookcode恶意软件将读取配置文件。虽然先前的Bookcode示例使用文件perf91nc.inf作为配置文件，但此版本从名为C_28705.NLS的文件读取其配置。此Bookcode示例具有与韩国互联网安全局（KISA）最近发布的综合[报告](https://www.boho.or.kr/krcert/publicationView.do?bulletin_writing_sequence=35799
"报告")中所述的恶意软件几乎相同的功能。如该报告第57页所述，一旦恶意软件启动，它就会将有关受害者的信息发送给攻击者。与C2服务器通信后，该恶意软件提供了标准的后门功能。

### 后阶段攻击

Lazarus组织使用Bookcode恶意软件集的活动具有自己独特的TTP，并且在此攻击中使用了相同的作案手法。

  * 从注册表sam转储中提取受感染的主机信息，包括密码哈希。
  * 使用Windows命令以检查网络连接。
  * 使用[WakeMeOnLan](https://www.nirsoft.net/utils/wake_on_lan.html "WakeMeOnLan")工具扫描同一网络中的主机。

在2020年9月25日安装Bookcode之后，攻击者开始从受害者那里收集系统和网络信息。攻击者还收集了包含密码哈希的注册表sam转储：

  * exe /c “reg.exe save hklm\sam %temp%\~reg_sam.save > “%temp%\BD54EA8118AF46.TMP~” 2>&1″
  * exe /c “reg.exe save hklm\system %temp%\~reg_system.save > “%temp%\405A758FA9C3DD.TMP~” 2>&1″

横向移动阶段，攻击者在获取帐户信息后，使用“net”命令连接到另一台主机，并使用“wmic”命令执行了复制的有效负载。

此外，Lazarus使用[ADfind](http://www.joeware.net/freetools/tools/adfind/
"ADfind")以便从Active Directory收集其他信息。攻击者使用此实用程序提取了受害者的用户和计算机的列表。

### Bookcode基础结构

我们发现了另一个配置文件，它包含四台C2服务器，所有这些服务器都是位于韩国的受损Web服务器。

  * hxxps://www.kne.co[.]kr/upload/Customer/BBS.asp
  * hxxp://www.k-kiosk[.]com/bbs/notice_write.asp
  * hxxps://www.gongim[.]com/board/ajax_Write.asp
  * hxxp://www.cometnet[.]biz/framework/common/common.asp

这些C2服务器的其中一个启用了目录列表，因此我们能够了解攻击者如何管理C2服务器：

![](https://images.seebug.org/content/images/2020/12/615c9655-d584-4c89-a8b4-0c320a6c519c.png-w331s)
受到攻击的网站上列出的攻击者文件

我们从受感染的服务器（一个“第一阶段” C2服务器）中发现了几个日志文件和一个脚本。它从后门接收连接，但仅充当攻击者实际存储的“第二阶段”服务器的代理。

File name | Description  
---|---  
_ICEBIRD007.dat | A log file containing the identifier of victims and
timestamps.  
~F05990302ERA.jpg | Second-stage C2 server address:  
hxxps://www.locknlockmall[.]com/common/popup_left.asp |  
Customer_Session.asp | Malware control script.  
  
Customer_Session.asp是第一阶段C2脚本，负责从第二阶段C2服务器传递命令并从植入中执行命令。为了向每个受害者传递适当的命令，将来自植入程序的bbs_code参数用作标识符。该脚本使用此标识符将命令分配给正确的受害者。这是为特定受害者发送命令的过程的工作方式：

  * 1.恶意软件攻击者设置特定植入程序的相应标志（[id] _208）并将命令保存到变量（[id] _210）。
  * 2.植入程序检查相应的标记（[id] _208）并从变量（[id] _210）中检索命令（如果已设置）。
  * 3.执行命令后，植入程序将结果发送到C2服务器并设置相应的标志。
  * 4.恶意软件攻击者检查该标志，并在设置了标志的情况下检索结果。

![](https://images.seebug.org/content/images/2020/12/b7593232-44b1-4cb0-afa5-a845ceb33295.png-w331s)
C2脚本的逻辑

除了植入程序控制功能外，C2脚本还具有其他功能。例如更新下一阶段的C2服务器地址，将植入程序的标识符发送到下一阶段服务器或删除日志文件。

table_nm value | Function name | Description  
---|---|---  
table_qna | qnaview | Set [id]_209 variable to TRUE and save the “content”
parameter value to [id]_211.  
table_recruit | recuritview | If [id]_209 is SET, send contents of [id]_211
and reset it, and set [ID]_209 to FALSE.  
table_notice | notcieview | Set [id]_208 and save the “content” parameter
value to [id]_210.  
table_bVoice | voiceview | If [id]_208 is SET, send contents of [id]_210 and
reset it, and set [id]_208 to FALSE.  
table_bProduct | productview | Update the ~F05990302ERA.jpg file with the URL
passed as the “target_url” parameter.  
table_community | communityview | Save the identifier of the implant to the
log file. Read the second-stage URL from ~F05990302ERA.jpg and send the
current server URL and identifier to the next hop server using the following
format:bbs_type=qnaboard&table_id=[base64ed identifier]
&accept_identity=[base64 encoded current server IP]&redirect_info=[base64ed
current server URL]  
table_free | freeview | Read _ICEBIRD007.dat and send its contents, and delete
it.  
  
Bookcode恶意软件样本之一（MD5
[0e44fcafab066abe99fe64ec6c46c84e](https://opentip.kaspersky.com/0e44fcafab066abe99fe64ec6c46c84e/?utm_source=SL&utm_medium=SL&utm_campaign=SL
"0e44fcafab066abe99fe64ec6c46c84e")）包含许多与旧Manuscrypt变体重叠的代码。

![](https://images.seebug.org/content/images/2020/12/4a23d250-0e27-4b87-b808-5442cacb0fe9.png-w331s)

### 结论

这两个事件表明Lazarus组织对与COVID-19相关的事物感兴趣。我们认为，当前参与疫苗研究或危机处理等活动的所有实体都应高度警惕网络攻击。

### IoC

**wAgent**

[dc3c2663bd9a991e0fbec791c20cbf92](https://opentip.kaspersky.com/dc3c2663bd9a991e0fbec791c20cbf92/?utm_source=SL&utm_medium=SL&utm_campaign=SL
"dc3c2663bd9a991e0fbec791c20cbf92")——%programdata%\oracle\javac.dat  
[26545f5abb70fc32ac62fdab6d0ea5b2](https://opentip.kaspersky.com/26545f5abb70fc32ac62fdab6d0ea5b2/?utm_source=SL&utm_medium=SL&utm_campaign=SL
"26545f5abb70fc32ac62fdab6d0ea5b2")——%programdata%\oracle\javac.dat  
[9c6ba9678ff986bcf858de18a3114ef3](https://opentip.kaspersky.com/9c6ba9678ff986bcf858de18a3114ef3/?utm_source=SL&utm_medium=SL&utm_campaign=SL
"9c6ba9678ff986bcf858de18a3114ef3")——%programdata%\grouppolicy\Policy.DAT

**wAgent Installer**

[4814b06d056950749d07be2c799e8dc2](https://opentip.kaspersky.com/4814b06d056950749d07be2c799e8dc2/?utm_source=SL&utm_medium=SL&utm_campaign=SL
"4814b06d056950749d07be2c799e8dc2")——%programdata%\oracle\javac.io,
%appdata%\ntuser.dat

**wAgent compromised C2 servers**

    
    
    hxxps://iski.silogica[.]net/events/serial.jsp@WFRForms.jsp@import.jsp@view.jsp@cookie.jsp
    hxxp://sistema.celllab[.]com.br/webrun/Navbar/auth.jsp@cache.jsp@legacy.jsp@chooseIcon.jsp@customZoom.jsp
    hxxp://www.bytecortex.com[.]br/eletronicos/digital.jsp@exit.jsp@helpform.jsp@masks.jsp@Functions.jsp
    hxxps://sac.najatelecom.com[.]br/sac/Dados/ntlm.jsp@loading.jsp@access.jsp@local.jsp@default.jsp

**wAgent file path**

    
    
    %SystemRoot%\system32\[random 2 characters]svc.drv

**wAgent registry path**

    
    
    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\Emulate - [random 2 characters]svc

**Bookcode injector**

    
    
    5983db89609d0d94c3bcc88c6342b354%SystemRoot%\system32\scaccessservice.exe,rasprocservice.exe

**Bookcode file path**

    
    
    %SystemRoot%\system32\C_28705.NLS
    
    %SystemRoot%\system32\gmslogmgr.dat

**Bookcode compromised C2 servers**

    
    
    hxxps://www.kne.co[.]kr/upload/Customer/BBS.asp
    hxxp://www.k-kiosk[.]com/bbs/notice_write.asp
    hxxps://www.gongim[.]com/board/ajax_Write.asp
    hxxp://www.cometnet[.]biz/framework/common/common.asp
    hxxps://www.locknlockmall[.]com/common/popup_left.asp

### MITRE ATT&CK Mapping

![](https://images.seebug.org/content/images/2020/12/94f7ec28-3e77-4d53-a66e-774d11cbc5cd.png-w331s)
![](https://images.seebug.org/content/images/2020/12/905e704c-dbb8-4db5-b578-e1774052d539.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1437/>

