## 一、概述  

**加密货币一直以来都是黑客们极为热衷的攻击领域，除了攻击加密货币交易平台以获得巨额的经济利益外，还存在大量以窃取加密货币钱包的攻击，启明星辰ADLab近期发现多起以加密货币机器人为诱饵进行加密货币钱包窃取的攻击案例。起初我们注意到一些行为异常的交易机器人（主要以Bitmex
Bot 、Trade
Bot、UniqueTradingBot为主），这些机器人在安装过程中弹出缺少.NET运行库的错误提示框。而通过调查分析发现，其中多款机器人的官方软件并没有使用.NET进行相关组件的开发。因而进一步分析后，我们发现这些异常的机器人释放并试图执行一些使用C#编写的可执行文件，同时发现一些非官方的网络连接。随后，我们将这些机器人释放的非官方组件一一提取出来做进一步分析和对比，最后确认这是一款新型的具有丰富窃密功能的恶意软件。其中核心组件的大部分类均以“NoiseMe”作为命名空间的起始标志，因而此处我们将该恶意软件命名为“NoiseMe”。其除了具备窃取几乎所有主流加密货币钱包的能力外，还被用于敏感信息（如受害主机的各种登录凭证数据）窃取，进一步黑客还可以利用该恶意软件对受害主机进行定制化的攻击，对不同的受害主机下发不同攻击插件来执行不同的任务，以实现黑客利益的最大化。**

通过我们全面的分析发现，该窃密软件几乎会窃取所有可能窃取的凭证数据，并且涵盖多达10种主流加密货币客户端软件的钱包文件。其中窃取的凭证的数据包含RDP凭证、FTP凭证、
Telegram凭证、Discord凭证、以及浏览器凭证（Cookies、Autofill、CreditCards、Credentials）等。其中涉及的加密货币客户端包含比特币、莱特币、字节币、达世币、以太币、门罗币、Electrum、Exodus等，这里Electrum是比特币的轻量钱包客户端，Exodus是一款用于管理资产和交易数据的数字货币钱包软件，其支持100多种加密货币，如比特币、以太坊、BAT、EOS、Augur、Tezos、Dash等。

此外，该窃密软件为了增加自身的存活时间，提高攻击的隐蔽性，其还大量使用代码混淆、关键字符串加密、高强度代码保护技术（WinLicense）来保护其攻击代码，提高逆向分析的难度和时间成本，同时采用文件内存加载技术来防止取证分析人员获取其核心攻击模块。在我们分析的整个过程中，需要对其采用高强度代码保护技术进行处理，解密出被保护的代码，并动态调试提取出其中被二次加密的字符串方可对其进行完整的逆向分析。

## 二、NoiseMe工作原理分析

在分析完“NoiseMe”恶意软件后，我们对其整个攻击过程进行回溯发现，其攻击载体主要存储在一些合法的下载站点、云盘，通过一些论坛和社交网络诱使特定人员下载恶意软件执行。黑客将这些攻击载体伪装成各种加密货币自动交易机器人，并以交易机器人为幌子发布恶意软件链进行传播。

![image.png](https://image.3001.net/images/20200522/1590132061_5ec77d5d0da2f.png!small)图1
攻击流程图

如图1所示，这些攻击载体一旦被受害人下载执行，“NoiseMe”恶意软件便会在后台偷偷地执行。其中首先启动一个“Dropper”执行，该“Dropper”会从黑客的一个恶意代码存储点去下载“上线”模块（下载自站点ra.pdofan.ru）和“核心窃密”模块（下载自站点v69.pdofan.ru）执行。其中，“上线”模块会收集受害主机的系统状态信息并回传至C&C服务器（45.67.231.23:53623）完成上线任务，同时C&C服务器会指定一个远程组件的地址给该模块执行，以完成特定工作。而“Dropper”下载的“核心窃密”模块主要以窃取受感染主机的加密货币钱包地址和多种登录凭证数据为主，这些数据均会回传给内置的存储服务器（195.161.62.146:2012）使用。

通过对“NoiseMe”攻击载体的收集发现，黑客使用了多种类型的攻击载体以扩大其攻击目标，其中除了包含有三款比较著名的商用加密货币机器人外，还包含有多种用于赚取比特币的自动化辅助工具以及一些使用Autoit脚本实现的伪装器。

**伪装名称** **** |  **伪装版本** **** |  **内置软件** **** |  **内置软件官方网站** **** |
**商业软件** ****  
---|---|---|---|---  
Bitmex Bot  |  3.1  |  MarginClick  |  <https://www.marginclick.com/> |  是  
Trade Bot  |  2.0  |  Automated Trading Bot  |  <http://mitsoft.ru/> |  是  
UniqueTrading Bot  |  2.0.4.2  |  Automated Trading Bot  |
<http://mitsoft.ru/> |  是  
  
表1 攻击载体伪装信息

伪装的商用加密货币机器人中，实际安装的是类似于MarginClick及AutomatedTrading
Bot之类的商业化交易客户端。其中攻击载体伪装成为类似于“BtcClicks
Autoclicker.exe”的辅助工具，经过查证该工具是基于网站[https://btcclicks.com](https://btcclicks.com/)进行模拟观看广告以赚取比特币的自动化工具，可以看出黑客还试图攻击此类灰色收入者以窃取其所得的比特币收入。

此外，还有一些攻击载体以Autoit脚本转EXE的方式存在，不过这类攻击载体似乎大量感染上了Ramnit蠕虫（是一款具备广泛感染能力的蠕虫病毒，其支持感染EXE、DLL、HTML以及HTM等类型的文件）。这很可能是“NoiseMe”在传播过程中受此病毒感染，而并非是黑客刻意为之，因为在“NoiseMe”中加入Ramnit蠕虫极容易暴露自身并且其攻击目的也大相径庭。

最后，我们对“NoiseMe”恶意软件进行了溯源，最终发现一款攻击功能和目标较为相似的恶意软件GrandSteal，通过比对分析还发现他们中出现了完全相同的代码，见图2。

![image.png](https://image.3001.net/images/20200522/1590132441_5ec77ed91ed23.png!small)图
2 代码比对图

但是他们之间大量的代码仍然存在许多差别，我们猜测这两款恶意软件极有可能来自同一个家族的源码改造。“NoiseMe”相较于GrandSteal，其功能更丰富，对抗手段更强，如GrandSteal仅仅使用ConfuserEx混淆工具进行简单的代码混淆，而“NoiseMe”则使用高强度的商业加密工具进行了代码保护；GrandSteal单纯只有窃密功能，而“NoiseMe”却加入了Loader的使用和远程任意组件执行的功能；此外“NoiseMe”使用了更为丰富的攻击载体进行传播。

## 三、详细技术分析

黑客利用Dropper模块下载执行“上线模块”和“核心窃密模块”，达到窃取受感染主机加密货币和隐私凭证数据的目的。为了躲避安全防护软件查杀和对抗安全分析人员逆向分析，黑客使用了字符串加密、内存加载执行以及利用商业保护软件WinLicense加壳等多种技术手段保护“NoiseMe”窃密软件。“NoiseMe”窃密软件各个模块功能如图3所示。

![image.png](https://image.3001.net/images/20200522/1590132554_5ec77f4ae25e3.png!small)图
3 NoiseMe模块功能示意图

### 3.1 Dropper模块分析

Dropper模块的主要任务是下载和执行功能模块。为了对抗逆向分析，黑客将Dropper模块中的关键字符串信息先进行异或加密（异或密钥为“dNwlEXttSqq”），加密的结果再用Base64编码存储到程序中。解密方法为其逆过程。解密代码如图4所示。

![image.png](https://image.3001.net/images/20200522/1590132643_5ec77fa3d6bbf.png!small)

图 4 字符串解密算法

在完成关键字符串解密后，Dropper模块会从2个内置的链接下载并执行功能模块。其中，内置链接“hxxp://ra.pdofan[.]ru/Justmine.exe”下载的是上线模块，该模块以Justmine.exe命名并存储到%USERPROFILE%目录；内置链接“hxxp://v69.pdofan[.]ru/111111111.exe”下载的是核心窃密模块，以111111111.exe命名并保存到%USERPROFILE%目录。下文我们会详细地分析这两个功能模块的具体实现。下载和执行功能模块相关代码如图5所示。

![image.png](https://image.3001.net/images/20200522/1590132691_5ec77fd3eed45.png!small)
图 5 下载文件并执行

从图5中可以看出，Dropper模块中下载功能模块的URL链接是HTTP协议，但是在分析过程中我们发现它在传输功能模块时实际使用的是HTTPS协议。黑客利用了HTTP重定向功能将下载链接重定向到HTTPS网址上，再以HTTPS协议传输数据以达到隐藏恶意模块传递和躲避防火墙侦测的目的。重定向请求和应答的网络数据包如图6所示。

![image.png](https://image.3001.net/images/20200522/1590132799_5ec7803fb32cf.png!small)

图 6 重定向到HTTPS

当Dropper模块完成上线模块和核心窃密模块的下载和执行后，其核心功能使命便已完成，接下来就是清理痕迹以躲避安全分析人员的追踪溯源。清理痕迹功能是利用上文解密出的Remove.bat批处理脚本程序实现，具体由Dropper模块中的“SystemDataDataRowBuilder”函数负责实施。相关代码如图7所示。

![image.png](https://image.3001.net/images/20200522/1590132857_5ec78079baaa8.png!small)

图 7 自删除代码

### 3.2 上线模块

“上线模块”是由Dropper模块下载并命名为Justmine.exe，其将自身伪装成WinRAR应用程序，用于迷惑攻击目标，​获取被感染主机的国家、城市以及系统版本、时区等信息，然后将这些信息上传到C&C服务器。黑客能够根据攻击需求向受感染主机下发并执行任意攻击模块。

 **3.2.1 获取设备信息**

​“上线模块”利用Replace函数过滤掉垃圾数据得到真正的C&C服务器地址“45.67.231.23:53623”。C&C地址的获取代码如图8所示。

![image.png](https://image.3001.net/images/20200522/1590133032_5ec7812897076.png!small)

图 8 C&C地址获取

在获得C&C服务器后，“上线模块”便开始收集受感染主机的设备信息，包括硬件ID、操作系统、公网IP、国家、CPU信息和显卡信息。这些信息会临时存储在内存中，作为上线信息上传到C&C服务器。获取设备信息代码如图9所示。

![image.png](https://image.3001.net/images/20200522/1590133112_5ec781788d13d.png!small)

图 9 获取设备信息

 **3.2.2 安装和持久化**

在获取到设备信息后，“上线模块”接着安装自身并利用计划任务实现持久化，其会先判断当前的执行路径与它预置的“%USERPROFILE%\\\Video\\\Junker”路径是否相同，为了方便描述，下文简称该路径为“安装目录”。

如不相同，“上线模块”会先创建该“安装目录”，然后通过遍历进程杀死在“安装目录”下的PHPmyAdmin.exe进程，接着将自身拷贝到“安装目录”下并命名为PHPmyAdmin.exe，再执行“安装目录”下的PHPmyAdmin.exe，最后退出执行。相关代码如图10所示。

![image.png](https://image.3001.net/images/20200522/1590133185_5ec781c123fb7.png!small)

图 10安装目录

如相同，“上线模块”会判断是否已经安装过，如果安装过就退出执行，否则就调用“Junk”函数向受感染主机安装计划任务以实现持久化。恶意代码利用Windows系统自带的schtasks程序执行安装计划任务，反编译后显示用于安装计划任务的命令字符串被混淆过，见图11。

![image.png](https://image.3001.net/images/20200522/1590133240_5ec781f81c203.png!small)

图 11计划任务

从图11中可以看出，计划任务被安装到“\\\Microsoft”路径下。任务名称以“Php-”字符串开始，后面再拼接一个受感染主机硬件信息（机器名称、当前登录用户名、用户所在域、操作系统版本信息组成的字符串）的HASH值。安装好的计划任务如图12所示。

![image.png](https://image.3001.net/images/20200522/1590133309_5ec7823d1d608.png!small)

图 12 电脑中被安装的计划任务

 **3.2.3 下载执行扩展模块**

“上线模块”在实现持久化后，就利用前面解析的C&C服务器和受感染主机的设备信息构造上线请求，并以SOAP协议每隔60秒与C&C服务器进行一次通信。C&C服务器收到上线请求后会向受感染主机下发配置信息，配置信息包含扩展模块的下载地址和扩展模块的启动方式（显示执行、隐藏执行）等配置信息。“上线模块”会按照配置信息下载并执行扩展模块。利用配置信息下达控制指令，黑客可以十分灵活的控制被感染主机执行任意攻击程序以实现其攻击目的。解析控制指令代码如图13所示。

![image.png](https://image.3001.net/images/20200522/1590133377_5ec782817dc66.png!small)

图 13 解析控制指令

从图13中可以看出，“上线模块”会调用“Drop”函数来下载和执行扩展模块。该函数会判断“%USERPROFILE%\\\Video\\\Junker\\\Lock”目录是否存在，如若不存在则先创建该目录，然后再按照配置信息下载执行扩展模块。相关代码如图14所示。

![image.png](https://image.3001.net/images/20200522/1590133456_5ec782d098ecb.png!small)

图 14下载执行代码

捕获到的上线请求数据包如图15所示。

![image.png](https://image.3001.net/images/20200522/1590133496_5ec782f830adf.png!small)

图 15 上线请求数据包

上线请求数据各字段的含义如表2所示。

**上传字段** **** |  **含义** ****  
---|---  
BuildID  |  黑客定义的标识  
Country  |  国家  
HardwareID  |  硬件ID信息  
IP  |  公网IP  
LastActive  |  上次上线时间  
OS  |  操作系统  
Processor  |  CPU信息  
Videocard  |  显卡信息  
  
表2 上线请求字段含义

C&C服务器返回的控制指令数据包内容如图16所示。

![image.png](https://image.3001.net/images/20200522/1590133591_5ec7835745053.png!small)

图 16 控制指令数据包

图16中各个字段含义如表3所示。

**字段名称** **** |  **字段含义** ****  
---|---  
Action  |  指令含义，目前仅支持Execute  
Current  |  未知，样本中未做判断  
ExecuteHidden  |  是否隐藏执行  
FinalPoint  |  未知  
ID  |  任务ID  
Status  |  状态是否激活  
Target  |  存储扩展模块的URL  
Visible  |  是否可见  
  
表3 上线应答字段含义

在对“Target”字段中的扩展模块进行分析后，我们发现其是一个与Dropper模块类似的功能模块，用于下载核心窃密模块，故不再做过多的介绍。

### 3.3、核心窃密模块

“核心窃密模块”是由Dropper模块下载并命名为11111111.exe，它的核心代码经解密后在内存中执行以达到绕过杀毒软件的效果。

 **3.3.1、自解密执行**

反编译“核心窃密模块”，结果显示该模块仅有2个类，一个是入口函数类（入口点“_0x_u1632184666.Main”），另一个是加密解密类（_0x_u1005254334），类名称和函数名均是被混淆过的，如图17所示。

![image.png](https://image.3001.net/images/20200522/1590133755_5ec783fbc1c2f.png!small)

图 17 入口类和加密解密类

“核心窃密模块”执行后先调用“_0x_u1005254334”函数对内置的字符串进行解密。解密过程是先将字符串转为16进制，然后使用硬编码的密钥“QDAWDfskVf”与该16进制数据进行异或，异或的结果再Base64解码得到最终的可执行程序（Holivar.exe）。相关代码如图18所示。

![image.png](https://image.3001.net/images/20200522/1590133805_5ec7842d72b67.png!small)

图 18解密代码

“核心窃密模块”通过调用“_0x_u956374591”函数实现内存加载并执行Holivar.exe，并向Holivar.exe传递2个参数，分别为存储服务器（“195.161.62.146”）和BuildID
（“MERCEDES”）。代码如图19所示。

![image.png](https://image.3001.net/images/20200522/1590134317_5ec7862dd35a1.png!small)

图 19内存加载执行

 **3.3.2、窃密功能分析**

“核心窃密模块”在内存中加载并执行Holivar.exe，由Holivar.exe负责实施窃取受害人的加密货币财产和隐私数据。为了便于描述，我们在分析窃密功能时均称之为“Holivar模块”。

（1）下载窃密配置

“Holivar模块”启动后会尝试以websocket协议、2012端口与存储服务器（“195.161.62.146”）建立连接，如果不能连接，则一直等待；如果连接成功，则从存储服务器下载配置信息。通过修改配置信息，黑客可以指定要窃取数据的类型。图20为下载和解析窃密配置信息代码。

![image.png](https://image.3001.net/images/20200522/1590134389_5ec786755b647.png!small)

图 20 下载和解析配置信息

图20中各个字段含义如4表所示。

**字段名称** **** |  **字段含义** ****  
---|---  
GrabBrowserCredentials  |  窃取浏览器凭证  
GrabColdWallets  |  窃取数字货币钱包  
GrabDesktopFiles  |  窃取文件  
GrabFtp  |  窃取FTP凭证  
GrabRdp  |  窃取Rdp凭证  
GrabDiscord  |  窃取Discord凭证  
GrabTelegram  |  窃取Telegram凭证  
Extensions  |  窃取文件类型  
  
表4 窃密配置信息字段含义

解析完窃密配置信息后，“Holivar模块”便开始按照配置信息收集受感染主机的隐私数据。

（2）获取客户端信息

“Holivar模块”会收集受感染主机的客户端信息，其中包括该窃密软件的BuildID、显示器屏幕分辨率、受感染主机的时间、时区、用户名、公网IP、国家、城市、操作系统、硬件信息、反病毒软件、操作系统语言信息。利用这些客户端信息，黑客可以区分不同的受感染主机，通过筛选后对特定目标进行攻击。信息收集相关代码如图21所示。

![image.png](https://image.3001.net/images/20200522/1590134478_5ec786ce681c1.png!small)

图 21 获取客户端信息

通过对“Holivar模块”进行二进制分析后，我们发现黑客可能利用了GitHub上的一个开源项目（<https://github.com/chrizator/WMIGatherer>）实现了获取设备的硬件信息和反病毒软件信息。开源代码与“Holivar模块”的代码片段比较如图22所示。

![image.png](https://image.3001.net/images/20200522/1590134529_5ec7870101b07.png!small)

图 22 GitHub开源代码与Holivar模块代码对比

（3）窃取浏览器数据

反汇编代码显示“Holivar模块”能够窃取基于Chromium和Firefox内核的浏览器的数据。“Holivar模块”通过遍历和查找“%USERPROFILE%\\\AppData\\\Local”和“%USERPROFILE%\\\AppData\\\Roaming”两个目录下的LoginData、Web
Data、Cookies文件，获取符合条件的浏览器文件夹。相关代码如图23所示。

![image.png](https://image.3001.net/images/20200522/1590135094_5ec78936de77a.png!small)

图 23获取Profile目录

在得到浏览器的安装路径后，“Holivar模块”通过拼接目录获取Cookies、autofill、Credit
Cards、Credentials的全路径，获得浏览器中存储的隐私数据。反编译后的代码如图24所示。

![image.png](https://image.3001.net/images/20200522/1590135170_5ec78982d6229.png!small)

图 24读取Cookies

（4）窃取加密货币钱包

“Holivar模块”能够窃取10种加密货币客户端软件的钱包文件，其中包括6种加密货币官方客户端钱包，如：比特币、莱特币、字节币、达世币、以太币、门罗币，此外还有比特币的轻量钱包客户端Electrum和加密货币交易软件Exodus的钱包。恶意软件获取受感染主机中数字钱包的信息如表5所示。

**货币名称** **** |  **钱包信息** ****  
---|---  
Bitcoin  |  读取%AppData%\Bitcoin\wallet.dat文件获取钱包信息  
Bitcoin-Qt  |  先查询注册表“HKCU\Software\Bitcoin-Qt\strDataDir”得到安装路径，然后读取该路径下的“wallet.dat”文件  
Bytecoin  |  读取“%AppData%\bytecoin\”路径下的后缀名为“*.wallet”的文件获取钱包信息  
Dash-Qt  |  先查询注册表“HKCU\Software\Dash-Qt\strDataDir”得到安装路径，然后读取该路径下的“wallet.dat”文件  
Electrum  |  遍历“%AppData%\ Electrum\ wallets\”路径下的文件获取钱包信息  
Ethereum  |  遍历“%AppData%\ Ethereum \ wallets\”路径下的文件获取钱包信息  
Exodus  |  遍历“%AppData%\ Exodus\ exodus.wallet\”路径下的文件获取钱包信息  
Litecoin  |  读取“% AppData %\Litecoin\wallet.dat”文件获取钱包信息  
Litecoin-Qt  |  先查询注册表“HKCU\Software\Litecoin-Qt\strDataDir”得到安装路径，然后读取该路径下的“wallet.dat”文件  
Monero  |  恶意代码通过查询注册表“HKCU\Software\ monero-core\wallet_path”得到Monero币钱包文件路径  
  
表5 钱包文件位置信息获取方法

（5）窃取文件  

“Holivar模块”具有窃取受感染主机任意文件的功能，其窃取的文件路径和文件后缀是从上文中“下载窃密配置”获得。黑客可以按照攻击需求灵活的配置要窃取文件的目录以及文件后缀名。通过逆向分析我们发现，“Holivar模块”仅上传小于等于2097152字节的文件。代码如图25所示。

![image.png](https://image.3001.net/images/20200522/1590135429_5ec78a85aa006.png!small)

图 25 窃取文件大小

（6）窃取Discord凭证

Discord是专门为了服务游戏人群而设计出来的即时通信软件，其提供短信、语音和视频通话等功能。此外，它还拥有极高的匿名性，这一特点吸引了很多不法分子（如：“右翼分子”、“非自愿独身者”、
“男权至上主义者”）使用这款应用进行线上交流和线下**。

逆向分析显示“Holivar模块”也对Discord凭证感兴趣，其获取Discord的凭证信息大致流程是：首先找到Discord的进程，然后dump其进程数据，最后解析dump文件，获取到登录凭证信息。相关代码如图26所示。

![image.png](https://image.3001.net/images/20200522/1590136028_5ec78cdcaacb5.png!small)

图 26 查找Discord进程

（7）窃取Ftp凭证

“Holivar模块”能够窃取FileZilla软件的登录凭证，FileZilla是一个免费开源的FTP软件，它的快速连接密码被存储在%userprofile%\AppData\Roaming\FileZilla\recentservers.xml中，文件格式如图27所示。

![image.png](https://image.3001.net/images/20200522/1590136156_5ec78d5c36705.png!small)

图 27 recentservers配置文件

保存的站点密码被存储在%userprofile%\AppData\Roaming\FileZilla\sitemanager.xml中，文件格式如下图所示：

![image.png](https://image.3001.net/images/20200522/1590136226_5ec78da23ff44.png!small)

图 28 sitemanager配置文件

“Holivar模块”只要读取上面的两个文件就能够轻易获取FileZilla登录凭证。图29是恶意软件解析FileZilla登录凭证的部分代码截图。

![image.png](https://image.3001.net/images/20200522/1590136342_5ec78e166699d.png!small)

图 29 解析配置信息

（8）窃取RDP凭证

RDP（远程桌面协议）登录凭证通常是各类黑客软件的攻击目标之一，其在暗网中以3至15美元的价格被出售。逆向分析显示“Holivar模块”也窃取RDP凭证数据，其使用了CredEnumerateW
API读取受感染主机的RDP凭证，然后提取每个RDP凭证保存的主机名、用户名和密码。解析RDP凭证代码如图30所示。

![image.png](https://image.3001.net/images/20200522/1590136439_5ec78e77ce3de.png!small)

图 30 盗取RDP凭证

（9）窃取Telegram凭证

“Holivar模块”通过读取“%AppData%\TelegramDesktop\tdata\D877F783D5D3EF8C\map*”和“%AppData%\TelegramDesktop\tdata\D877F783D5D3EF8*”获取桌面版的Telegram登录凭证，进而实现对Telegram会话的劫持。相关代码如图31所示。​

![image.png](https://image.3001.net/images/20200522/1590136519_5ec78ec76d75b.png!small)

图 31 盗取Telegram数据

（10）获取进程信息

“Holivar模块”会收集受感染主机运行的进程名称和启动参数并将其上传到存储服务器。黑客通过对这些数据进行筛选从而判断目标设备是否存在能够被攻击的进程，以便展开后续的攻击。相关代码如图32所示。

![image.png](https://image.3001.net/images/20200522/1590136589_5ec78f0d07507.png!small)

图 32 遍历进程信息

（11）获取安装应用列表

“Holivar模块”除了窃取当前运行的进程列表，还窃取受感染主机安装的应用程序列表，它通过遍历注册表"SOFTWARE\\\Microsoft\\\Windows\\\CurrentVersion\\\Uninstall"下面的内容获取安装应用的名称。相关代码如图33所示。

![image.png](https://image.3001.net/images/20200522/1590136642_5ec78f426b99c.png!small)

图 33 获取应用列表

（12）获取屏幕截图

“Holivar模块”会向存储服务器发送受感染主机的屏幕截图，它先获取受感染主机的屏幕大小，然后创建一个与屏幕大小相同的Bitmap，最后利用Graphice.CopyFromScreen函数获取当前屏幕的位图信息。屏幕截图实现代码如图34所示：

![image.png](https://image.3001.net/images/20200522/1590136706_5ec78f82babc9.png!small)

图 34 屏幕截图

（13）上传凭证数据

在“Holivar模块”完成隐私数据收集后，其使用websocket协议将这些数据上传到存储服务器，请求路径是“Credentials”。上传数据请求代码如图35所示。​

![image.png](https://image.3001.net/images/20200522/1590136797_5ec78fdd1d989.png!small)

图 35 回传数据

数据上传成功后，
“Holivar模块”会创建"%USERPROFILE%\\\AppData\\\Local\\\Temp\\\Remove.bat"批处理文件，利用此脚本实现自删除功能。

## 四、总结及建议

通过上文的分析可以看出，“NoiseMe”窃密软件是一款同时具备加密货币钱包及主机凭证信息窃取的功能。通过其伪装性的攻击载体来看，其主要针对的是那些期望进行自动化交易的人员，这些人具有交易频繁，交易量大等特点，其中很多是拥有大量加密货币的大户。一旦此类人感染了“NoiseMe”，其受到的损失将是不可估量的。此外，黑客从中窃取的凭证信息也将是黑客进行关联攻击的重要依据，这会大大的扩展黑客的攻击路径，以实现攻击的最大利益化。

从本次攻击的过程来看，“NoiseMe”恶意代码主要以伪装的手段来传播，并在一定程度使用社会工程学来欺骗目标下载恶意代码执行。由于目标的安全意识薄弱，使得这种看似简单的攻击手段依然有效，且在黑客中仍然被大量使用。随着数字货币的应用场景日趋丰富，我们仍然需要做好基础的安全工作包含安全意识的培养、基础安全设置的管理等等。因此，基于本次攻击的分析给出如下几条建议以防御“NoiseMe”恶意代码的入侵：

> （1）不要从第三方下载和运行未知的应用程序，
>
> （2）校验可执行文件的签名以及HASH，
>
> （3）开启防火墙，拦截未知应用网络通信，
>
> （4）及时给电脑打补丁，修复漏洞，
>
> （5）不要使用浏览器的自动填充密码和***功能，
>
> （6）不要使用一些应用程序的保存密码功能。

## 五、IOC

注：以下为收集到的部分NoiseMe家族域名信息

0qe.pdofan.ru  
---  
44jx.seraph15.ru  
4t5zk1.anri44til.ru  
51b6ru.anri44til.ru  
57qy.perfdom.ru  
5fui.anri44til.ru  
5xbv.pdofan.ru  
7xf3z.ogritefit.ru  
9z2f.brizy5.ru  
c.anri44til.ru  
c.chernovik55.ru  
d.seraph15.ru  
e.j990981.ru  
e.pdofan.ru  
g.pdofan.ru  
h.j990981.ru  
jf.perfdom.ru  
k1ristri.ru  
mh.owak-kmyt.ru  
n3.pdofan.ru  
ow.chernovik55.ru  
p6.k1ristri.ru  
pe.pdofan.ru  
ro.pdofan.ru  
s8n.j990981.ru  
u3w.chernovik55.ru  
uhavebullet.ru  
v69.pdofan.ru  
vdd9.ogritefit.ru  
xm6.naabeteru.ru  
ycl.k1ristri.ru  
zvsk.ogritefit.ru

