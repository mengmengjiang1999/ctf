**译者：知道创宇404实验室翻译组  
原文链接：<https://www.fortinet.com/blog/threat-research/deep-analysis-the-eking-variant-of-phobos-ransomware>**

## 前言

Phobos [勒索软件](https://en.wikipedia.org/wiki/Ransomware)
自2019年初被安全研究人员首先发现后，不断推出新的变型，这些变型不仅进化了攻击方法，还频繁更改过去变型中加密文件的扩展名。

两周前，FortiGuard实验室采集了一个新的威胁样本。这是一个Microsoft
Word文档，它带有一个恶意宏，旨在传播Phobos的EKING变型。在本篇文章中，我将展示此变型如何感染受害者的系统，以及它如何使用AES算法在受害者设备和共享网络文件夹上扫描和加密文件。

## 在MS Office Word中打开捕获的示例

打开Word文档后，它会显示一条警告，指示受害者单击黄色栏中的“enablecont”按钮以启用宏，如图1.1所示。

由于宏可能包含恶意代码，因此默认情况下，MS Office
Word会显示“安全警告”，警告用户该文档可能存在风险。然后，用户可以决定是否执行宏（通过单击“Enable Content”按钮）。

![图1.1  MS Office
Word中的样本内容](https://images.seebug.org/content/images/2020/10/14/1602666610000-1douty.png-w331s)
图1.1 MS Office Word中的样本内容

通过查看宏代码，我发现它具有一个名为Document_Close（）的内置事件函数，当MS Office
Word退出时会自动调用该函数。换句话说，恶意宏代码是在受害者关闭文档时执行的。这还具有绕过某些沙箱解决方案进行检测的好处（[FortiSandbox](https://www.fortinet.com/products/sandbox/fortisandbox.html?utm_source=blog&utm_campaign=2018-q2-fortisandbox-main-page)将该恶意Word附件检测为风险软件。）

它从打开的样本中提取一个base64编码的块到本地文件“ C：\ Users \ Public \ Ksh1.xls”。通过调用命令“ _Certutil
-decode C：\ Users \ Public \ Ksh1.xls C：\ Users \ Public \ Ksh1.pdf_
”将文件解码为另一个文件。“ Ksh1.pdf”是base64解码的文件的PE文件（DLL文件）。 _图1.2_
是宏代码的屏幕截图，显示了将在何处执行将base64文件“ Ksh1.xls”解码为“ Ksh1.pdf”的命令。

![图1.2
宏到base64解码提取的文件](https://images.seebug.org/content/images/2020/10/14/1602666620000-2rzklh.png-w331s)图1.2
宏到base64解码提取的文件

宏的最后一项任务是通过执行命令“ _Rundll32 C：\ Users \ Public \ Ksh1.pdf，In_ ”来执行解码的PE文件“
Ksh1.pdf ”。解码后的PE文件“ Ksh1.pdf”是一个具有导出功能“ _In_ ”的DLL文件，由上述命令行中的“
Rundll32.exe”调用。

![图1.3
导出功能的ASM代码在](https://images.seebug.org/content/images/2020/10/14/1602666622000-3fuspk.png-w331s)图1.3
导出功能的ASM代码在

图1.3显示了“ Ksh1.pdf”的导出功能“ In”的ASM代码。可以很容易地理解它首先在“ C：\ Users \ Public \
cs5”处创建了一个新目录。它通过以下方式将文件从URL“ hxxp：// 178 [.] 62 [.] 19 [.] 66 / campo / v /
v”下载到文件“ C：\ Users \ Public \ cs5 \ cs5.exe”中调用API“
URLDownloadToFile（）”。最后，它通过调用API“ CreateProcessA（）”来运行下载的“
cs5.exe”文件。顺便说一下，下载URL字符串和完整文件路径字符串是硬编码在DLL文件“Ksh1.pdf”中的。有趣的是，下载的文件“
cs5.exe”是Phobos的有效负载文件。

## 查看有效载荷EXE文件

“ C：\ Users \ Public \ cs5 \
cs5.exe”是Phobos的EKING变体的有效载荷，它受到未知包装器的保护，如图2.1中的Exeinfo PE所示。

![图2.1
受保护的Phobos有效载荷EXE文件](https://images.seebug.org/content/images/2020/10/14/1602666650000-4aylxh.png-w331s)图2.1
受保护的Phobos有效载荷EXE文件

Phobos具有AES加密的配置块，其中包含许多配置信息（此变体中为69项）。它们在与索引编号参数一起使用之前在函数中解密。它还包含用于加密文件的新扩展名字符串，用于生成用于加密文件的密钥的数据，文件排除列表，Phobos的版本信息，受害者的赎金信息等。

在图2.2中，我们可以看到解密加密文件“ .id [<< ID >>-2987]。[wiruxa@airmail.cc]
.eking”2新扩展名的示例，其索引号为0x04。根据一个索引号为0x33解密字符串“ [<< ID >>-2987]
v2.9.1”，我们知道此变体的版本为v2.9.1。

![图2.2
从配置块解密新的扩展](https://images.seebug.org/content/images/2020/10/14/1602666654000-5xhruz.png-w331s)图2.2
从配置块解密新的扩展

## 启动第二个进程并执行两组命令

当“ cs5.exe”运行时，它通过调用API
CreateProcessWithTokenW（）以及来自Explorer.exe进程创建自身的第二个进程，以便第二个进程在Explorer.exe令牌的安全上下文中运行。这样，它就具有在受害者的系统上读写更多文件所需的特权。

Phobos在两个创建的线程中执行两组命令。

下面列出了第一组命令以及我添加的注释：

`` `*vssadmin delete shadows / all / quiet* –删除该卷的所有卷影副本。 *wmic shadowcopy
delete* –从本地计算机删除卷影副本。 *bcdedit / set {*default*} bootstatuspolicy
ignoreallfailures bcdedit / set {*default*} recoveryenabled no* –禁用自动启动修复功能。
*wbadmin delete catalog –quiet* –删除备份目录。 *exit*` ``

通过删除Windows系统为系统还原创建的卷影副本，受害者无法使用它来还原加密的文件。它还可以防止受害者从自动启动修复或备份目录中还原文件。

第二组命令关闭了受感染系统上的Windows防火墙，如下所示。

`` `*netsh advfirewall将currentprofile状态设置为off* –针对Windows 7和更高版本。
*netsh防火墙设置opmode模式=禁用* –针对Windows XP，Windows 2003版本。 exit` ``

## 添加自动运行项目

该恶意软件还从加密的配置块中解密字符串“ Software \ Microsoft \ Windows \ CurrentVersion \
Run”（索引号为0x11），这是注册表子密钥路径。然后，它为两个根键HKEY_LOCAL_MACHINE和HKEY_CURRENT_USER的相同子键创建一个自动运行项“
cs5”。图4.1是根键“ HKEY_CURRENT_USER”下添加的自动运行项的屏幕截图。

![图4.1。 添加了自动运行项目“
cs5”](https://images.seebug.org/content/images/2020/10/14/1602666663000-6yeyyb.png-w331s)图4.1添加了自动运行项目“
cs5”

除了将此项添加到系统注册表中的自动运行组之外，它还将“ cs5.exe”复制到两个自动启动文件夹中：“％AppData％\ Microsoft \
Windows \ Start Menu \ Programs \ Startup”和“％ProgramData” ％\ Microsoft \
Windows \开始菜单\程序\启动”。图4.2显示了将“ cs5.exe”复制到两个启动文件夹中的ASM代码片段。

![图4.2。
将有效负载文件复制到启动文件夹中](https://images.seebug.org/content/images/2020/10/14/1602666671000-7ssani.png-w331s)图4.2将有效负载文件复制到启动文件夹中

Windows启动时，这两个文件夹中的可执行文件由Windows系统自动执行。这意味着Windows将在启动时启动四个“
cs5.exe”文件以维护恶意软件的生存。Phobos具有一种使用Mutex对象来确保仅一个进程正在运行的机制。如果存在相同的互斥对象，其他“
cs5.exe”进程将退出。

## Phobos在受害者系统上执行的核心任务

勒索软件的核心任务是加密受害者的文件，然后要求勒索以解密那些加密的文件。在本节中，我将向您展示Phobos的EKING变体如何执行此任务。

为了提高性能，它创建了多个线程来扫描和加密受害者系统上的文件。此外，它使用大量Event对象来控制和同步这些线程的进度。

### 1.终止进程的线程

它从启动线程开始，以防止终止包含列出的41个进程名称的名称列表中的指定进程，如下所示。您可能已经猜到，名称列表也是从配置块中以索引号0x0a解密的。

`` `*msftesql.exe; sqlagent.exe; sqlbrowser.exe; sqlservr.exe; sqlwriter.exe;
oracle.exe; ocssd.exe; dbsnmp.exe; synctime.exe; agntsvc.exe;
mydesktopqos.exe; isqlplussvc.exe; xfssvccon。 exe; mydesktopservice.exe;
ocautoupds.exe; agntsvc.exe; agntsvc.exe; agntsvc.exe; encsvc.exe;
firefoxconfig.exe; tbirdconfig.exe; ocomm.exe; mysqld.exe; mysqld-nt.exe;
mysqld- opt.exe; dbeng50.exe; sqbcoreservice.exe; excel.exe; infopath.exe;
msaccess.exe; mspub.exe; onenote.exe; outlook.exe; powerpnt.exe; steam.exe;
thebat.exe; thebat64。 exe; thunderbird.exe; visio.exe; winword.exe;
wordpad.exe*` ``

这个进程名列表已经被发现多次被其他勒索软件用来做同样的动作。

这些进程属于MS SQL Server、Oracle数据库、VMware、Panda Security、MySql、FireFox、SQL
Anywhere、RedGate SQL Backup、MS Excel、MS Word、MS Access、MS PowerPoint、MS
Publisher、MS OneNote、MS Outlook、Bat等产品、Thunderbird、写字板等。

Phobos会继续终止这些应用程序，以迫使它们释放当前打开的任何文件，以便Phobos可以对其进行加密。

### 2.扫描要加密的文件的线程

该线程的线程函数调用API GetLogicalDrives（）来调用受害系统上的所有逻辑驱动器，例如“ C：\”，“ D：\”，“
E：\”等等。它为每个逻辑驱动器创建两个扫描线程。这意味着每个逻辑驱动器中的文件由两个线程处理。

![图5.1。
忽略两个系统文件夹](https://images.seebug.org/content/images/2020/10/14/1602666678000-8cjqgh.png-w331s)图5.1忽略两个系统文件夹

为了避免破坏受害者的Windows系统，它会忽略对两个系统文件夹及其子文件夹下的加密文件，它们分别是“％WinDir％”（通常是“ C：\
Windows”）和“％ProgramData％\ Microsoft \ Windows \ Caches”
。图5.1显示了Phobos能够检测当前路径（“ \？\ D：”）是否与它需要忽略的两个系统文件夹匹配。

如前所述，它创建了两个线程来扫描每个逻辑驱动器的文件。一个线程用于普通扫描（一个文件接一个文件），另一个线程仅用于与数据库相关的文件的特殊扫描。我可以假设这些文件对受害者来说比其他文件更有价值。然后，它将按以下扩展名扫描数据库文件，扩展名如下（解密索引号为0x06）：

`` `*fdb; sql; 4dd; 4dl; abs; abx; accdb; accdc; accde; adb; adf; ckp; db; db-journal; **db-shm; db-wal; db2; db3; dbc; dbf; dbs; dbt; dbv; dcb; dp1; eco;
edb; epim; fcd; gdb; mdb; mdf; ldf; myd; ndf; nwdb; nyf; sqlitedb; sqlite3;
sqlite;*` ``

除此之外，它还具有两个扩展排除列表。其中一个包含Phobos在其历史记录中使用的加密文件扩展名，如下所示（解密索引号为0x07）：

``
`*eking;actin;Acton;actor;Acuff;Acuna;acute;adage;Adair;Adame;banhu;banjo;Banks;Banta;Barak;Caleb;Cales;Caley;calix;Calle;Calum;Calvo;deuce;Dever;devil;Devoe;Devon;Devos;dewar;eight;eject;eking;Elbie;elbow;elder;phobos;help;blend;bqux;com;mamba;KARLOS;DDoS;phoenix;PLUT;karma;bbc;CAPITAL;WALLET;*`
``

另一个列表包含此变体用来显示其受害者勒索信息的文件，以及一些Windows系统文件，如下所示（解密索引号为0x08）：

`` `*info.hta; info.txt; boot.ini; bootfont.bin; ntldr; ntdetect.com; io.sys;
osen.txt*` ``

扫描线程在回调函数中使用这两个排除列表来过滤文件以根据其规则进行加密。同时，Phobos还在每个扫描线程中创建了一个加密线程，用于对受害者的文件进行加密。扫描线程和加密线程如何协同工作：扫描线程继续扫描文件，并将具有完整路径的文件名复制到公共缓冲区中，并在选择一个文件后设置事件。然后，加密线程可以从公共缓冲区中获取文件名并进行加密。

### 3.加密算法和密钥使用

Pbobos使用AES（[高级加密标准](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard)）CBC（密码块链接）模式作为其加密文件的加密算法。在我的分析中，Phobos的这种变体没有使用Windows提供的用于AES的内置Crypto
API，而是实现了自己的AES功能。

当人们谈论AES CBC加密和解密时，通常会提到“ IV”和“ Key”。

对于其密钥长度，我们知道Phobos使用256位AES密钥（20H字节），这是最强的文件加密。此外，它使用非对称的公私钥密码系统来保护AES密钥。从索引号为0x2的配置块中解密公钥。

![图5.2
AES密钥及其公开密钥已加密](https://images.seebug.org/content/images/2020/10/14/1602666687000-9vyuqw.png-w331s)图5.2
AES密钥及其公开密钥已加密

AES密钥是使用10H字节的随机数据和10H字节的数据从解密的公共密钥生成的。如图5.2所示，它在内存窗口顶部生成了AES密钥（20H字节）。后续信息是加密的AES密钥（80H字节）的相关数据，该数据是使用卷序列号“％systemdrive％”（例如受害者系统上的“
C：\”）和公共密钥生成的，以及函数Sub_401706中的一些解密常量值。加密的AES密钥后的最后四个字节是以上两部分的CRC32的hash值。

只要受害者提供了由Phobos中的API
GetVolumeInformationW（）获取的系统驱动器卷序列号，加密的AES密钥以及其他常量值的数据，攻击者就可以使用其私钥来还原AES密钥。加密的AES密钥将记录在加密的文件中，稍后我将解释加密的文件结构。这就是为什么它要求受害者在勒索信息页面上提供系统驱动器的卷序列号的原因。

IV（初始化向量）数据的长度为10H字节，通常是随机生成的。它也像加密的AES密钥一样记录在加密的文件中。IV与AES密钥一起用于数据加密，就像MD5算法的盐一样。

一旦获得IV数据和AES密钥，它就可以解密加密的文件。

### 4.加密文件的线程

如上所述，这是扫描线程启动的加密线程。扫描线程选择文件后，便会将文件的完整路径复制到加密线程的公用缓冲区，该缓冲区由扫描线程通知（设置事件对象）。

然后，它将配置块中的格式字符串（索引号0x04）解密为那些加密文件的新文件扩展名，如下所示，其中“ << ID >>”将替换为系统驱动器的卷序列号。

`` `*.id [<< ID >>-2987]。[wiruxa@airmail.cc] .eking*` ``

![图5.3具有新扩展名的加密文件](https://images.seebug.org/content/images/2020/10/14/1602666718000-10zrdub.png-w331s)图5.3具有新扩展名的加密文件

这只是带有新扩展名的加密文件的格式化新文件名。这次，由扫描线程选择和过滤的文件为“ \？\ E：\ test_file.txt”，其加密文件名为“ \？\
E：\ test_file.txt.id [[581F1093- 2987]。[wiruxa@airmail.cc] .eking”。

它继续读取所选文件的内容（例如：“ E：\
test_file.txt”）。我们知道AES加密块的大小固定为10H字节。因此，如果要加密的数据大小未与10H对齐，则需要使用填充来附加数据（Phobos使用“
00”作为填充）来解决该问题。

![图5.4调用AES_CBC_Encrypt（）函数来加密文件内容](https://images.seebug.org/content/images/2020/10/14/1602666746000-11bwnbr.png-w331s)图5.4调用AES_CBC_Encrypt（）函数来加密文件内容

图5.4显示了Phobos将要调用AES_CBC_Encrypt（）函数，该函数的arg0是一个密钥对象（AES_CTX
Struct），其中包含用于加密内存窗口中所示文件内容的IV和密钥（附加了三个“ 00”填充元素）。

加密后，Phobos通过调用API WriteFile（）将密文保存到加密文件中（例如，“ E：\ test_file.txt.id
[[581F1093-2987]。[wiruxa@airmail.cc] .eking”），如图5.5所示。

![图5.5将密文保存到加密文件中](https://images.seebug.org/content/images/2020/10/14/1602666760000-12ppria.png-w331s)图5.5将密文保存到加密文件中

加密的文件内容由两部分组成。第一部分是 原始文件内容的 _密文_
。第二部分是一组数据，我称其为decryption_config_block。它用于解密第一部分。图5.6是加密文件内容的屏幕截图。我将解释一下decryption_config_block包含的内容。

![图5.6加密文件内容的示例](https://images.seebug.org/content/images/2020/10/14/1602666769000-13ywdym.png-w331s)图5.6加密文件内容的示例

前10H个字节（用红色包围）是加密的原始文件内容，如图5.5所示。40H字节（由蓝色包围）是一个加密的部分，其中包含一些常量值以及原始文件名，这些文件使用相同的AES密钥和IV进行加密。随后的14H字节“
00”可以视为数据定界符。10H字节（由黑色包围）仅是此文件的IV数据。下一个Dword
0x03告诉原始文件内容附加的填充的大小（再次参考图5.5）。80H数据块（绿色）是加密的AES密钥的相关数据，该数据在扫描线程中生成，并且对于不同的扫描线程而言是不同的。下一个Dword
0xF2是整个decryption_config_block的大小。

Phobos要做的最后一件事是调用API DeleteFileW（）从受害人的系统中擦除原始文件。

### 5.扫描网络共享资源

该线程功能专注于网络共享资源。Phobos使用参数dwScope的不同值多次调用API
WNetOpenEnum（）。这些是RESOURCE_CONNECTED，RESOURCE_RECENT，RESOURCE_CONTEXT，RESOURCE_REMEMBERED和RESOURCE_GLOBALNET。

`` `RESOURCE_CONNECTED：枚举所有当前连接的资源。 RESOURCE_RECENT：枚举所有最近连接的资源。
RESOURCE_CONTEXT：仅枚举调用方的网络上下文中的资源。 RESOURCE_REMEMBERED：枚举所有记住的（持久的）连接。
RESOURCE_GLOBALNET：枚举网络上的所有资源。` ``

这项工作涉及API WNetOpenEnumW（）和WNetEnumResourceW（）来枚举网络共享资源。

成功获取一种资源后，Phobos将使用上面的资源的完整地址（如\？\ UNC \ {resource name} \ {folder
name}）启动我在上面的第 **2** 点中讨论的两个扫描线程 ，以启动该资源。扫描和过滤文件。如我在第 **4**
点中所述，扫描线程然后启动加密线程，并在选择一个文件时注意到加密。

![图5.7准备启动扫描线程的一个共享资源](https://images.seebug.org/content/images/2020/10/14/1602666787000-14yjvil.png-w331s)图5.7准备启动扫描线程的共享资源

上面的图5.7显示了从RESOURCE_CONNECTED获得的共享资源（“ \？\ UNC \ VBoxSvr \
vbox_share_folder”），该资源即将调用Sub_405840函数以在该共享资源上启动新的扫描线程。

### 6.监视和扫描新逻辑驱动器的线程

我已经讨论过Phobos扫描本地逻辑驱动器上的文件，以及扫描网络共享资源，这些都是受害者系统的所有现有资源。

还有另一个线程，其主要任务是监视新的逻辑驱动器。例如，受害者连接了USB闪存驱动器或手机，Windows系统将其视为新的逻辑驱动器。这将被该线程捕获。它每秒运行一次检测，并为检测到的任何新逻辑驱动器启动两个新的扫描线程。图5.8显示的伪代码显示了此线程功能的逻辑结构。

![图5.8用于扫描新逻辑驱动器的伪代码](https://images.seebug.org/content/images/2020/10/14/1602666792000-15ymxji.png-w331s)图5.8用于扫描新逻辑驱动器的伪代码

## 向受害者显示勒索信息

Phobos的主线程等待所有扫描线程和加密线程完成其工作。然后，它将两个文件info.hta（html版本勒索信息）和info.txt（文本版本勒索信息）拖放到桌面以及受害者系统上可用逻辑驱动器的根目录中。还使用命令“
open”调用API ShellExecuteExW（）以在受害者的屏幕上打开html版本的info.hta，如图6.1所示。

![图6.1向受害者显示赎金信息](https://images.seebug.org/content/images/2020/10/14/1602666806000-16xcdqf.png-w331s)图6.1向受害者显示赎金信息

## 对EKING变异深入分析结论

在这篇文章中，我对Phobos勒索软件的EKING变种进行了深入分析。我已经介绍了如何从原始MS
Word文档样本中下载有效负载文件（cs5.exe），以及Phobos如何将其保持在受害者的系统上。

我主要分析了Phobos的核心任务-扫描和加密受害者系统上的文件。通过这篇文章，我们现在知道它不仅扫描逻辑驱动器上的文件，而且还扫描网络共享资源和新连接的逻辑驱动器。我还详细介绍了Phobos的这种变体如何使用多个线程来完成其工作。

最后，我解释了Phobos在完成加密后如何向受害者显示其勒索信息。

为了保护您的设备免受恶意软件的攻击，我们建议不要打开不受信任来源的电子邮件附件。

## Fortinet解决方案

借助FortiGuard的Web过滤，防病毒和CDR（内容撤防和重建）服务，Fortinet客户已免受此Phobos变种的攻击，如下所示：

下载的URL被FortiGuard Web过滤服务评为“ **恶意网站** ”。

Word文档和下载的有效负载文件被检测为“ **VBA / Agent.KBU！tr** ”和“ **W32 /
Phobos.HGAF！tr.ransom** ”，并被FortiGuard AntiVirus服务阻止。

此外，FortiSandbox将Word文档检测为风险软件。

[FortiMail](https://www.fortinet.com/products/email-security/fortimail.html?utm_source=blog&utm_campaign=2018-q2-fortimail-main-page)用户受到FortiGuard AntiVirus的保护，FortiGuard
AntiVirus可以检测到发送Phobos的原始Word文档，并通过CDR服务进一步加以保护，该服务可用于抵消Office文档中所有宏的威胁。

此外，为了防止设备受到这种方式发送的恶意软件的攻击，我们建议用户不要打开不受信任来源的电子邮件附件。强烈建议对最终用户进行有关如何识别和标记潜在恶意电子邮件的培训。

## IOCS

### URLs

hxxp://178[.]62[.]19[.]66/campo/v/v

### Sample SHA-256

[Word Document]  
667F88E8DCD4A15529ED02BB20DA6AE2E5B195717EB630B20B9732C8573C4E83  
[Phobos Payload]  
6E9C9B72D1BDB993184C7AA05D961E706A57B3BECF151CA4F883A80A07FDD955

## 参考文献：

<https://id-ransomware.blogspot.com/2017/10/phobos-ransomware.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1367/>

