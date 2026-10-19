作者：终端安全实验室

发布机构：360威胁情报中心

**![lx_clip1543804030400_lx.jpg](https://image.3001.net/images/20181203/1543804057_5c04949977585.jpg!small)  
**

## **概述**

近日，360终端安全实验室监控到GandCrab勒索病毒有了新动向，和以往相比本次GandCrab传播量有了明显的波动，我们分析了背后原因，发现此次波动是由一种近年较常见的蠕虫病毒引起的，该蠕虫病毒主要通过U盘和压缩文件传播，一直活跃在包括局域网在内的众多终端上。该蠕虫病毒构成的僵尸网络，过去主要传播远控、窃密、挖矿等木马病毒，而现在开始投递GandCrab勒索病毒。由于该病毒感染主机众多，影响较广，因而造成了这次GandCrab的传播波动。在此特提醒大家注意保护好您的数据，当心被勒索病毒袭击从而遭受不可挽回的损失。

我们对该蠕虫病毒的最新变种进行了深入分析。病毒的母体和以往相比没有太大变化，其主要特别之处在于其投递的病毒种类有了新变化，除了新增投递GandCrab勒索病毒外，还发现该病毒的初次投放方式，也即病毒制作者是怎么投放病毒的。一般病毒的初次投放方式包括挂马、捆绑下载、邮件附件、租用僵尸网络、漏洞利用等，而这次该病毒使用了邮件附件作为其初次投放传播的手段之一。

下面首先就其主要技术特点概括如下：

  * 病毒代码具有风格统一的混淆方式，通过内存解密PE并加载执行来绕过杀软的静态扫描查杀，病毒的母体具有一定反沙箱反分析能力；

  * 具备多种传播方式，包括投递恶意邮件、感染Web/FTP服务器目录、U盘/网络磁盘传播、感染压缩文件等；

  * 窃取多种虚拟货币钱包，包括：Exodus、JAXX、MultiBit HD、Monero、Electrum、Electrum-LTC、BitcoinCore等多种货币钱包；

  * 通过劫持Windows剪贴板，替换多种主流虚拟货币钱包地址，包括：BTC、ETH、LTC、XMR、XRP、ZEC、DASH、DOGE等币种；

  * 窃取邮箱账号、Web网站登录账号、WinSCP凭据、Steam游戏平台账号、以及多种即时通讯软件聊天记录；

  * 下载传播多种病毒，包括勒索、窃密、挖矿、母体传播模块等，其母体内嵌的下载链接主要固定为5种，正好印证了“五毒俱全”的特点；

##  **  
**

##  **病毒攻击流程**

  

![image.png](https://image.3001.net/images/20181203/1543803238_5c0491664ade9.png!small)

  

## **病毒详细分析**

###  **母体DownLoader分析**

####  **探测虚拟机/沙箱运行环境**

病毒母体是一个DownLoader，运行时通过遍历进程以及检查加载的模块来探测运行环境是否是虚拟机或沙箱环境，其中特别针对python进程进行了检查（沙箱常用），还通过检查加载的DLL模块来检测sandboxie或sysanalyzer：

  

![image.png](https://image.3001.net/images/20181203/1543803247_5c04916f7bf65.png!small)

####  **  
**

####  **持久化设置**  

病毒会将自身拷贝至windows\自建目录\winsvcs32.exe，并创建注册表开机启动项实现持久化运行：  

  

![image.png](https://image.3001.net/images/20181203/1543803266_5c049182498a7.png!small)

拷贝并重命名为winsvc32.exe

  

![image.png](https://image.3001.net/images/20181203/1543803271_5c049187bca1b.png!small)

创建注册表开机启动项  

  

![image.png](https://image.3001.net/images/20181203/1543803276_5c04918cc1eb4.png!small)

删除自身的Zone.IdentifierNTFS Stream避免运行时出现风险提示

#### **添加防火墙例外以及关闭Windows Defender实时防护等功能**

  

![image.png](https://image.3001.net/images/20181203/1543803283_5c049193f0227.png!small)

防火墙以及WindowsDefender相关设置  

####  **  
**

####  **通过可移动磁盘/网络磁盘进行AUTORUN传播**

  

![image.png](https://image.3001.net/images/20181203/1543803289_5c04919989518.png!small)

针对网络磁盘以及可移动磁盘

  

  

![image.png](https://image.3001.net/images/20181203/1543803294_5c04919e8684e.png!small)

在U盘根目录创建”_”目录以及将自身拷贝并重命名为DeviceManager.exe

  

![image.png](https://image.3001.net/images/20181203/1543803299_5c0491a364580.png!small)

创建指向病毒母体的lnk文件

  

  

![image.png](https://image.3001.net/images/20181203/1543803306_5c0491aae14aa.png!small)

Lnk文件内容

  

![image.png](https://image.3001.net/images/20181203/1543803312_5c0491b029797.png!small)

被感染后的U盘以及AutoRun.inf截图

####  **  
**

####  **通过感染压缩包进行传播**

判断%appdata%\winsvcs.txt是否存在，不存在则创建该文件，该文件起到一个开关作用，用来判断是否对压缩文件进行感染：

  

![image.png](https://image.3001.net/images/20181203/1543803317_5c0491b5cd5ee.png!small)

将自身拷贝至%TEMP%目录，并重命名为“Windows Archive Manager.exe”：

  

![image.png](https://image.3001.net/images/20181203/1543803322_5c0491baaab94.png!small)

  

遍历本地磁盘中的压缩文件，将病毒本体添加到压缩文件，受感染的压缩类型包括zip、rar、7z、tar：  

  

![image.png](https://image.3001.net/images/20181203/1543803326_5c0491be27f0c.png!small)

 ****

这部分代码功能还不太完善，经过测试，压缩格式只支持zip、rar，7z和tar格式的支持有Bug，感染后会破坏原有格式：

  

![image.png](https://image.3001.net/images/20181203/1543803333_5c0491c5189ce.png!small)

  

####  **替换FTP/WEB服务器目录下的EXE文件进行传播**

遍历磁盘文件，判断EXE文件所在路径是否包含如下FTP/WEB服务器目录：

  

![image.png](https://image.3001.net/images/20181203/1543803337_5c0491c98c54a.png!small)

  

如果满足条件，则把目录下的EXE文件替换成病毒自身文件：

  

![image.png](https://image.3001.net/images/20181203/1543803342_5c0491ce9ff71.png!small)

####  **  
**

####  **监控系统剪贴板，劫持替换虚拟货币钱包地址**

监控剪贴板，如果发现有预期的虚拟货币钱包地址，则进行替换，影响的币种包括：

Btc、eth、ltc、xmr、xrp、zec、dash、doge等。

  

![image.png](https://image.3001.net/images/20181203/1543803349_5c0491d515fc1.png!small)

判断各类货币钱包地址特征

  

  

![image.png](https://image.3001.net/images/20181203/1543803353_5c0491d943e0c.png!small)

劫持监控剪贴板

####  **  
**

####  **通过内置C2下载多个恶意模块**

母体内嵌了3个C2服务器以及多个混淆的DNS备用地址用于下载传播其他病毒程序（这些DNS暂时无效，但如果前面3个IP被封或失效，可通过启用这些备用DNS来达到切换C2的目的）:

  

![image.png](https://image.3001.net/images/20181203/1543803358_5c0491de22663.png!small)

将下列5个文件名与上述ULR链接拼接成完整下载链接：  

  

![image.png](https://image.3001.net/images/20181203/1543803362_5c0491e2a7a87.png!small)

此处5个恶意链接用来下载传播其他病毒，可谓“五毒俱全”。

  

下载的多个恶意模块保存在%TEMP%目录下并随机命名，然后删除对应的Zone.Identifier避免运行时出现风险提示：

  

![image.png](https://image.3001.net/images/20181203/1543803367_5c0491e76556a.png!small)

下载成功后创建进程执行该文件：

  

![image.png](https://image.3001.net/images/20181203/1543803372_5c0491ec6d890.png!small)

此次分析时下载的恶意模块包括：传播模块、2个勒索病毒Downloader、窃密模块、挖矿模块（具体推送某类恶意程序随时间以及C2服务器而定）

###  **  
**

###  **挖矿模块分析**

####  **内存解密PE加载执行**

挖矿模块与病毒母体采用了类似代码混淆方式，通过内存解密PE并加载执行：

  

![image.png](https://image.3001.net/images/20181203/1543803377_5c0491f1d7c62.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803383_5c0491f76dadf.png!small)

#### **解密配置文件URL地址、以及矿池地址等数据**

  

![image.png](https://image.3001.net/images/20181203/1543803387_5c0491fbde888.png!small)

  

####  **内存映射NTDLL模块，获取所需API，绕过R3 Hook**

  

![image.png](https://image.3001.net/images/20181203/1543803392_5c0492006b89e.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803396_5c04920437230.png!small)

####  **  
**

####  **通过<http://92.63.197.60/newup.txt>获取挖矿配置相关数据**

分析调试时，上述链接已失效：

  

![image.png](https://image.3001.net/images/20181203/1543803400_5c0492085c383.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803404_5c04920cad5be.png!small)

解析配置数据，包含钱包地址、挖矿端口等配置信息

**构造** **xmrigConfig** **配置文件**

根据前面获取到的钱包地址等信息，构造config文件，并进行base64编码保存。

  

![image.png](https://image.3001.net/images/20181203/1543803409_5c04921131838.png!small)

配置文件格式化

  

![image.png](https://image.3001.net/images/20181203/1543803415_5c04921714b39.png!small)

Base64解码后的配置文件（由于url失效，无法获取有效钱包地址）

####  **  
**

####  **持久化设置**

拷贝自身至“ProgramData\GCxcrhlcfj”目录，并创建r.vbs脚本：

  

![image.png](https://image.3001.net/images/20181203/1543803420_5c04921c1ca99.png!small)

  

通过VBS脚本，在start menu下生成url快捷方式，指向样本自身：  

  

![image.png](https://image.3001.net/images/20181203/1543803425_5c0492213feea.png!small)

调用wscript执行：

  

![image.png](https://image.3001.net/images/20181203/1543803429_5c04922526fb9.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803432_5c049228f018f.png!small)

Url快捷方式负责启动挖矿病毒：

  

![image.png](https://image.3001.net/images/20181203/1543803438_5c04922e1b112.png!small)

####  **解密内嵌的xmrig程序，借壳系统程序作为傀儡进程挖矿**

挂起方式启动wuapp.exe，其命令行参数为挖矿配置文件：

  

![image.png](https://image.3001.net/images/20181203/1543803442_5c04923230576.png!small)

解密xmrig：

  

![image.png](https://image.3001.net/images/20181203/1543803451_5c04923b1a1eb.png!small)

解密xmrig

内存解密出的PE为XMRig 2.8.1版本：

  

![image.png](https://image.3001.net/images/20181203/1543803454_5c04923e8fca8.png!small)

  

在傀儡进程注入代码:

  

![image.png](https://image.3001.net/images/20181203/1543803458_5c04924279ea3.png!small)

傀儡进程注入

#### **监控TaskMgr.exe**

为了隐蔽自身，样本会实时遍历系统进程检查是否有任务管理器进程存在，如果发现则杀掉挖矿进程：  

  

![image.png](https://image.3001.net/images/20181203/1543803465_5c049249153d0.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803469_5c04924dad019.png!small)

杀进程代码

###  **窃密模块分析**

该窃密木马为Delphi编写，窃密内容主要包括即时通讯软件聊天记录、浏览器历史记录、WinSCP凭据、Steam账号、虚拟货币钱包、邮箱、屏幕截图等。

样本尝试与C2服务器通讯拉取配置信息（服务器已失效）

  

![image.png](https://image.3001.net/images/20181203/1543803475_5c0492537637b.png!small)

  

相关窃密功能代码结构：  

  

![image.png](https://image.3001.net/images/20181203/1543803480_5c04925843160.png!small)

涉及的虚拟货币钱包：

  

![image.png](https://image.3001.net/images/20181203/1543803485_5c04925d33668.png!small)

Exodus、JAXX、MultiBit HD

  

![image.png](https://image.3001.net/images/20181203/1543803490_5c0492621c921.png!small)

Monero

  

  

![image.png](https://image.3001.net/images/20181203/1543803501_5c04926d67865.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803505_5c049271702aa.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803509_5c0492753ad22.png!small)

Electrum、Electrum-LTC、BitcoinCore

即时通讯软件：

  

![image.png](https://image.3001.net/images/20181203/1543803513_5c0492795575f.png!small)

Skype聊天记录等数据

  

![image.png](https://image.3001.net/images/20181203/1543803517_5c04927d1fbff.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803521_5c0492818ce20.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803525_5c049285bf6f5.png!small)

Pidgin、PSI、TeleGram

WinSCP：

  

![image.png](https://image.3001.net/images/20181203/1543803529_5c0492895f588.png!small)

Outlook邮箱：

  

![image.png](https://image.3001.net/images/20181203/1543803534_5c04928e17921.png!small)

Steam账号相关：  

  

![image.png](https://image.3001.net/images/20181203/1543803540_5c049294452de.png!small)

  

窃取浏览器的历史记录、Cookie等信息（主要针对火狐浏览器）：

  

![image.png](https://image.3001.net/images/20181203/1543803545_5c049299138d0.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803548_5c04929c6b380.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803552_5c0492a05d4ec.png!small)

火狐浏览器sqlite数据库

### **勒索模块分析**

由母体下载的2个勒索模块是做了静态免杀的DownLoader，其中一个针对“中国”地区，而另一个针对“越南”以及“中国”地区投放GandCrab勒索病毒。以下是针对“中国”和“越南”地区的下载逻辑相关代码，另一个只针对“中国”类似，此处不重复分析。

  

![image.png](https://image.3001.net/images/20181203/1543803557_5c0492a576849.png!small)

地区列表

  

通过访问<http://92.63.197.48/geo.php>从服务器拉取地区代码列表，然后与”CN”以及”VN”相比较，如果满足这两个地区，则开始下载GandCrab勒索病毒：  

  

![image.png](https://image.3001.net/images/20181203/1543803562_5c0492aadba30.png!small)

比较地区列表

  

  

![image.png](https://image.3001.net/images/20181203/1543803566_5c0492ae8397f.png!small)

通过C2下载GandCrab母体并执行  
  

下载的GandCrab母体为5.0.4版本，与常见的版本无差异，这里不再做重复分析：

  

![image.png](https://image.3001.net/images/20181203/1543803571_5c0492b339e61.png!small)

###  

###  **传播模块分析**

传播模块依旧做了静态免杀处理，以及设置持久化运行，并通过SMTP协议发送携带恶意附件的邮件进行传播，邮件附件为带有恶意JS脚本的压缩包，该恶意脚本最终通过Powershell远程下载并执行本次蠕虫母体DownLoader。

####  **持久化设置**

拷贝自身到windows\自建目录下，并重命名为wincfgrmgr32：

  

![image.png](https://image.3001.net/images/20181203/1543803578_5c0492bab71ff.png!small)

通过注册表设置自身为开机启动：  

  

![image.png](https://image.3001.net/images/20181203/1543803581_5c0492bdd7e68.png!small)

#### 通过aol.com获取邮箱服务器地址并测试连通性

  

![image.png](https://image.3001.net/images/20181203/1543803586_5c0492c23294b.png!small)

邮箱服务器：mx-aol.mail.gm0.yahoodns.net

####  

####  **下载并打包JS DownLoader脚本**

通过C2： **<http://ssofhoseuegsgrfnu.ru/m/get.js>** 下载恶意js脚本，该JS是一个
DownLoader，保存在TEMP目录随机文件名.jpg

  

![image.png](https://image.3001.net/images/20181203/1543803591_5c0492c77b26a.png!small)

连接服务器下载js文件

  

![image.png](https://image.3001.net/images/20181203/1543803595_5c0492cbea769.png!small)

经过混淆处理的js代码

接着将js脚本文件压缩成zip格式：

  

![image.png](https://image.3001.net/images/20181203/1543803601_5c0492d115f66.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803604_5c0492d4613eb.png!small)

然后将js文件压缩包进行base64编码并保存在\%TEMP%\随机文件名.jpg：  

  

![image.png](https://image.3001.net/images/20181203/1543803610_5c0492da46a94.png!small)

BASE64编码

####  **  
**

####  **通过SMTP协议随机发送恶意邮件**

通过C2（<http://ssofhoseuegsgrfnu.ru/m/xxx.txt>）获取目标邮箱列表：

  

![image.png](https://image.3001.net/images/20181203/1543803615_5c0492df8e897.png!small)

  

![image.png](https://image.3001.net/images/20181203/1543803618_5c0492e2d4799.png!small)

随机读取该邮箱列表文件，取出邮箱地址，通过SMTP协议发送恶意邮件，其邮件附件会携带前面压缩好的JS脚本的压缩包：

  

![image.png](https://image.3001.net/images/20181203/1543803622_5c0492e6af3de.png!small)

通过SMTP发送恶意邮件

####  **  
**

####  **执行恶意JS脚本**

当恶意js脚本在受害者的终端上运行后，js脚本会通过Powershell下载并执行此次蠕虫母体：

  

![image.png](https://image.3001.net/images/20181203/1543803628_5c0492ecac859.png!small)

进程链信息

## **相关IOCs**

 **MD5** **：**  
c30f72528bb6ab5aab25b33036973b07

48087776645fd9709f09828be7e42f8f

fa940342c3903f54c452a8a2483b1235

24275604649ac0abafe99b981b914fbc

a13d3aef725832752be1605e50b6f7e0

574c8a27fc79939ca1343ccb2722b74f

dfd5be2aeabc2a79c1e64e0b3a6dac73

64e0e23cdec4358354628195ec81a745

**C &C** **：**

92.63.197.60

92.63.197.48

92.63.197.112

92.63.197.60:9090

**URLs** **：**

hxxp:// 92.63.197.48/t.exe

hxxp:// 92.63.197.48/m.exe

hxxp:// 92.63.197.48/p.exe

hxxp:// 92.63.197.48/s.exe

hxxp:// 92.63.197.48/o.exe

hxxp://ssofhoseuegsgrfnu.ru/m/xxx.txt

hxxp://ssofhoseuegsgrfnu.ru/m/get.js

hxxp://92.63.197.48/geo.php

hxxp://92.63.197.60/newup.txt

hxxp://92.63.197.48/index.php

**WalletAddr** **：**

1LdFFaJiM7R5f9WhUEskVCaVokVtHPHxL5  
28VcfDWthf987aBo6ddyGuYnMkwtWo6bBe4j7Q87pDYxEEGZzHseUMvFr6MNqj3PGR4PGXzCGYQw7UemxRoRxCC97qVBups

XfPoiH5ShPQdXC3Kc39XzCaB84eL1w53oA

DPngr3jnAGgKY45vQpt4NmYt3jQCP2smrW

0xa9b717e03cf8f2d792bff807588e50dcea9d0b1c

4BrL51JCc9NGQ71kWhnYoDRffsDZy7m1HUU7MRU4nUMXAHNFBEJhkTZV9HdaL4gfuNBxLPc3BeMkLGaPbF5vWtANQrqWkGbn7jMQVGL3aA

LPuhyFoFggYkXwkkmDbnA19hu1wzuJggHJ

rBkCLqPgHiKt6Hdddnjq27ECehHqCcCHTD

t1aGAy8CBERajaMAKdzddp3WttD5Czji55S

## **总结及安全建议**

通过分析我们可以看到，本次的蠕虫病毒开始传播勒索病毒GandCrab，而且主要针对的是中国和越南地区，病毒扩散渠道从邮件附件到U盘传播等，覆盖范围比起单纯的某一种传播方式要大不少，同时这背后是否也含有病毒传播者认为国人的安全防范意识不够也未可定，总之本次的传播新动向值得引起国人的高度警惕。

针对本次的病毒技术特点以及结合以往的病毒传播方式，我们给出以下安全建议：

  * 不要打开来历不明的邮件附件

  * 在Windows中禁用U盘的“自动运行”功能

  * 打齐操作系统安全补丁，及时升级Web、数据库等服务程序，防止病毒利用漏洞传播

  * 避免使用弱口令，采用复杂密码，设置登录失败次数限制，防止暴力破解攻击

  * 安装杀毒软件，定期扫描电脑，及时升级更新病毒库保持杀毒软件的良好运行

  * 提高安全意识，保持良好的上网习惯，重要数据做好备份

## 关于360终端安全实验室

360终端安全实验室由多名经验丰富的恶意代码研究专家组成，重点着力于常见病毒、木马、蠕虫、勒索软件等恶意代码的原理分析和研究，致力为中国政企客户提供快速的恶意代码预警和处置服务，在曾经流行的WannaCry、Petya、Bad
Rabbit的恶意代码处置过程中表现优异，受到政企客户的广泛好评。

依托360在互联网为13亿用户提供终端安全防护的经验积累，360终端安全实验室以360天擎新一代终端安全管理系统为依托，为客户提供简单有效的终端安全管理理念、完整的终端解决方案和定制化的安全服务，帮助广大政企客户解决内网安全与管理问题，保障政企终端安全。

## **关于360 天擎新一代终端安全管理系统**

360天擎新一代终端安全管理系统是360企业安全集团为解决政企机构终端安全问题而推出的一体化解决方案，是中国政企客户3300万终端的信赖之选。系统以功能一体化、平台一体化、数据一体化为设计理念，以安全防护为核心，以运维管控为重点，以可视化管理为支撑，以可靠服务为保障，能够帮助政企客户构建终端防病毒、入侵防御、安全管理、软件分发、补丁管理、安全U盘、服务器加固、安全准入、非法外联、运维管控、主机审计、移动设备管理、资产发现、身份认证、数据加密、数据防泄露等十六大基础安全能力，帮助政企客户构建终端威胁检测、终端威胁响应、终端威胁鉴定等高级威胁对抗能力，为政企客户提供安全规划、战略分析和安全决策等终端安全治理能力。

  

![image.png](https://image.3001.net/images/20181203/1543803636_5c0492f47e216.png!small)

##  

  

