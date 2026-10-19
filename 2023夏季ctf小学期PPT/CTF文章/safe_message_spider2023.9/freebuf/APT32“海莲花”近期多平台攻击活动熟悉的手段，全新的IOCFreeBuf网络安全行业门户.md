## 前言

**“海莲花”，又名APT32和OceanLotus，是越南背景的黑客组织。该组织至少自2012年开始活跃，长期针对中国能源相关行业、海事机构、海域建设部门、科研院所和航运企业等进行网络攻击。除中国外，“海莲花”的目标还包含全球的政府、军事机构和大型企业，以及本国的媒体、人权和公民社会等相关的组织和个人。**

2017年下半年至今，微步在线发布了《“海莲花”团伙的最新动向分析》、《“海莲花”团伙专用后门Denis最新变种分析》、《微步在线发现“海莲花”团伙最新macOS后门》和《“海莲花”团伙本月利用Office漏洞发起高频攻击》等多篇报告，披露了APT32的相关攻击活动。近期，微步在线黑客画像系统监控到该组织多平台的攻击活动，经分析发现：

> APT32的攻击活动仍在持续，近期中国、韩国、美国和柬埔寨等国金融、政府和体育等行业相关目标遭到定向攻击。

>
> 攻击平台包含Windows和macOS，攻击手法相比之前变化不大，除都使用了伪装Word文档的可执行程序之外，针对Windows平台的还利用了CVE-2017-11882漏洞。

>
> 针对Windows平台的木马部分利用了白加黑技术，部分利用了Regsvr32.exe加载执行OCX可执行文件。此外，相比之前多利用Symantec公司签名的程序进行白加黑利用来投递Denis木马，APT32近期增加了对Intel和Adobe公司签名程序的白加黑利用。

> 针对macOS平台的木马相较之前其Dropper和Payload加了壳和虚拟机检测。

微步在线通过对相关样本、IP和域名的溯源分析，共提取22条相关IOC，可用于威胁情报检测。微步在线的威胁情报平台（TIP）、威胁情报订阅、API等均已支持此次攻击事件和团伙的检测。

## 详情

微步在线长期跟踪全球150多个黑客组织。近期，微步在线监测到APT32针对中国、韩国、美国和柬埔寨等国金融、政府和体育等行业相关目标的多平台攻击活动。
该组织近期手法与之前相比变化不大，其中针对Windows平台的攻击主要利用包含CVE-2017-11882漏洞的doc文档结合白加黑利用和图标伪装为Word的RAR自解压文件来投递其特种木马Denis，针对macOS平台的亦同样是将macOS应用程序伪装为Word文档进行木马投递。

与此前一样，诱饵文档内容都是模糊图片，例如Scanned Investment Report-July 2018.ⅾocx：

![诱饵文档内容都是模糊图片](https://image.3001.net/images/20181011/1539258921_5bbf3a2964f70.png!small)

### 样本分析

微步在线在8月份监控到多起APT32的攻击活动，涉及Windows和macOS平台。相关分析如下：

 **Windows样本**

漏洞样本

在Office漏洞利用方面，APT32近期主要利用CVE-2017-11882漏洞投递Denis木马。《“海莲花”团伙本月利用Office漏洞发起高频攻击》对CVE-2017-11882漏洞利用做过详细分析，详情可查阅相关报告。近期相关的部分漏洞样本：

SHA256 | 文件名 | 诱饵内容 | C2 | 攻击手法  
---|---|---|---|---  
e7f997778ca54b87eb4109d6d4bd5a905e8261ad410a088daec7f3f695bb8189 | July ,
2018.doc | 模糊图片 | ourkekwiciver.comdieordaunt.comstraliaenollma.xyz |
CVE-2017-11882加Intel白利用  
0abe0a3b1fd81272417471e7e5cc489b234a9f84909b019d5f63af702b4058c5 | FW Report
on demonstration of former CNRP in Republic of Korea.doc | 模糊图片 |
andreagahuvrauvin.combyronorenstein.comstienollmache.xyz |
CVE-2017-11882加Adobe白利用  
  
以`e7f997778ca54b87eb4109d6d4bd5a905e8261ad410a088daec7f3f695bb8189`为例，该样本在微步在线云沙箱的分析结果如下图所示，从“云沙箱-威胁情报IOC”可发现此样本相关C2已被识别为APT32所有。

![在线云沙箱的分析结果](https://image.3001.net/images/20181011/1539258952_5bbf3a48aae24.png!small)

多引擎检测：

![多引擎检测](https://image.3001.net/images/20181011/1539258991_5bbf3a6f96e55.png!small)

执行流程：

![执行流程](https://image.3001.net/images/20181011/1539259008_5bbf3a808ef23.png!small)

### 威胁情报IOC

 **RAR自解压样本**

APT32经常使用伪装成Word文档的可执行程序作为投递木马的载体，通常还会结合RLO手法迷惑受害者。近期伪装成Word文档的部分RAR自解压文件：

SHA256 | 文件名 | 诱饵内容 | C2 | 攻击手法  
---|---|---|---|---  
58e294513641374ff0b42b7c652d3b4a471e8bde8664a79311e4244be0546df4 | Sum for
July 2018.exe | 模糊图片 |
andreagbridge.comillagedrivestralia.xyzbyronorenstein.com |
RAR自解压，利用regsvr32.exe运行OCX  
78a1f6d9b91334e5435a45b4362f508ae27d7ad784b96621d825c2e966d04064 | feedback,
Rally in USA from July 28-29, 2018.exe | 模糊图片 |
stienollmache.xyzchristienollmache.xyzlauradesnoyers.com |
RAR自解压，利用regsvr32.exe运行OCX  
  
以样本`78a1f6d9b91334e5435a45b4362f508ae27d7ad784b96621d825c2e966d04064`为例。使用WinRAR查看该文件，可发现该自解压文件运行后会通过regsvr32.exe加载执行释放的OCX可执行文件，然后打开诱饵文档迷惑受害者，如下图：

![诱饵文件](https://image.3001.net/images/20181011/1539259025_5bbf3a91b47bb.png!small)

该样本在微步在线云沙箱的分析结果如下图所示，从“云沙箱-威胁情报IOC”亦可发现此样本相关C2已被识别为APT32所有。

![云沙箱分析](https://image.3001.net/images/20181011/1539259041_5bbf3aa1c510c.png!small)

执行流程：

![执行流程](https://image.3001.net/images/20181011/1539259057_5bbf3ab1909a8.png!small)

### 威胁情报IOC

 **macOS样本**

微步在线近期还捕获了多个APT32针对macOS平台的特种木马，下文以“Scanned Investment Report-July
2018.ⅾ[footnoteRef:1]ocx”为例进行分析。

该样本的基本信息如下：

文件类型 | Zip文件，macOS app  
---|---  
文件大小 | 454,967 字节  
文件名 | Scanned Investment Report-July 2018.ⅾocx  
MD5 | a3d09d969df1742a7cc9511f07e9b44b  
SHA1 | 01ad8b20337da00d1d458ba93f98dc996a97a71f  
SHA256 | 68f7ca2f1fa9f0b5151bec686144eafc13a1e2266dcfc95fafc3104f0a96b802  
  
该样本为后缀伪装成为.docx的macOS应用程序，一旦双击运行则会执行\Contents\MacOS\下的Scanned Investment
Report-July
2018可执行文件，导致系统被感染。该可执行文件是一个Dropper，相比此前《微步在线发现“海莲花”团伙最新macOS后门》中分析的样本，该Dropper和其释放的Payload都加了一个简单的壳，Payload相比之前也增加了虚拟机检测。

![虚拟机检测](https://image.3001.net/images/20181011/1539259074_5bbf3ac2410b8.png!small)

样本Scanned Investment Report-July
2018运行后判断启动权限，根据权限释放文件到不同目录，然后设置隐藏属性和修改文件创建时间。其中 mouseevents
和mediaagentd属同一文件，为恶意Payload程序，plist文件的功能是实现对应Payload的开机自启 。

权限 | 释放文件  
---|---  
root |
/Library/Mouse/Primary/mouseevents/Library/LaunchDaemons/com.apple.mouses.event.plist  
非root |
/Users/boy/Library/Video/Download/Updater/mediaagentd/Users/boy/Library/LaunchAgents/com.apple.media.agentd.plist  
  
修改创建时间相关命令如下：

![修改创建时间](https://image.3001.net/images/20181011/1539259092_5bbf3ad439c88.png!small)

com.apple.mouses.event.plist被设置为隐藏属性，其创建时间被修改为2017-11-22 00:33:43，文件内容如下：

![文件内容](https://image.3001.net/images/20181011/1539259105_5bbf3ae1f2e50.png!small)

样本释放的mouseevents属后门程序，其核心功能是接受C2控制执行各种操作，具体包含上传下载和删除文件、执行shell命令等等。相关分析如下：

1、mouseevents首先会通过检测系统信息来做反虚拟机检测。通过内置关键字vmware、virtualbox、parallels来检测程序是否运行在虚拟环境中。使用的shell命令如下：

![使用的shell命令](https://image.3001.net/images/20181011/1539259123_5bbf3af34b2b5.png!small)

![使用的shell命令](https://image.3001.net/images/20181011/1539259136_5bbf3b00794ba.png!small)

2、如检测到运行在虚拟环境中，则通过shell命令删除其父程序所在的目录。但有趣的是，即使检测到自身运行在虚拟机环境中也不会退出，只会不断的循环检测运行环境。使用shell命令如下：

![使用shell命令](https://image.3001.net/images/20181011/1539259149_5bbf3b0db5c82.png!small)

3、如检测到不在虚拟环境中，则会随机休眠一段时间。

![随机休眠一段时间](https://image.3001.net/images/20181011/1539259164_5bbf3b1c0adf7.png!small)

4、然后通过shell命令获取系统版本、用户名、计算机名和系统架构体系等信息。相关代码和指令如下：

![相关代码和指令](https://image.3001.net/images/20181011/1539259182_5bbf3b2ea9717.png!small)

Shell命令 | 功能  
---|---  
ioreg -rd1 -c IOPlatformExpertDevice | awk '/IOPlatformSerialNumber/ {
split($0, line, \"\\\\\"\"); printf(\"%s\", line[4]); }' 2>&1" |
获取IOPlatformUUID  
system_profiler SPHardwareDataType 2>/dev/null | awk '/Memory/ {split($0,line,
\":\"); | 获取系统内存大小  
sw_vers –productVersion | 获取系统版本  
uname –m | 获取处理器架构  
scutil --get ComputerName | 获取用户名  
  
5、在获取系统信息之后，程序会解密出C2并拼接“/store/ads/modal.css”作为上线的URL，拼接的URL具有一定的欺骗性。上线发送的内容包含安装时间、安装路径、PID、是否root权限、Arch、计算机名称、用户名和系统版本等信息。

![获取信息](https://image.3001.net/images/20181011/1539259198_5bbf3b3e4b61d.png!small)

6、该后门内置3个C2域名，执行时按顺序请求连接，若连接失败超过5次，则会解密下一个域名并尝试连接。如第一个域名就上线成功，则不会解密之后的域名。该样本内置的C2域名为web.dalalepredaa.com、p12.alerentice.com和rio.imbandaad.com。C2的解密算法为AES256，解密key如下：

![解密key](https://image.3001.net/images/20181011/1539259213_5bbf3b4d1f28d.png!small)

7、程序通过设置一个全局变量的值来判断选取哪个域名作为上线域名，通过curl模块发送网络连接，通过返回值来判断是否获取下一个C2。

![判断是否获取下一个C2](https://image.3001.net/images/20181011/1539259229_5bbf3b5d8f09d.png!small)

8、一旦上线成功，程序会在随机等待一段时间之后向{C2
domain}/appleauth/static/cssj/N252394295/widget/auth/app.css循环请求控制指令。

![循环请求控制指令](https://image.3001.net/images/20181011/1539259256_5bbf3b7832367.png!small)

9、通过对C2返回的0x2F开始的0x10个字节进行rol 2并异或0x13得到控制指令。

![得到控制指令](https://image.3001.net/images/20181011/1539259276_5bbf3b8c0affb.png!small)

![得到控制指令](https://image.3001.net/images/20181011/1539259416_5bbf3c188c1b5.png!small)  
10、该后门包含7个控制指令，相关指令和对应功能如下表：

指令 | 功能  
---|---  
0xE8 | 结束自身进程  
0xA2 | 将执行控制指令shell命令写入文件，执行，并上传结果  
0xAC | 执行控制指令shell命令，并上传结果  
0x3C | 下载文件  
0x23 | 同0x3C  
0x72 | 上传文件  
0x48 | 删除文件  
0x32 | 设置请求超时的时间  
0x33 | 获取文件信息  
其他 | 不执行有效操作  
  
## **关联分析**

微步在线威胁情报云显示，APT32的攻击仍在持续，近期中国、韩国、美国和柬埔寨相关目标遭到定向攻击。以微步在线狩猎系统捕获的诱饵文档July ,
2018.doc为例，该文件创建时间为2018/08/06，野外发现时间为2018/08/14，结合文件名判断，该样本应是在8月中上旬被攻击者使用。但其最终释放的后门的C2早已被微步在线识别，这侧面体现了威胁情报相较于传统安全产品的优势，可以在攻击者发起攻击之前就识别其攻击资产。如下图：

  
![在线威胁情报云信息](https://image.3001.net/images/20181011/1539259432_5bbf3c285343f.png!small)

由于相关诱饵文档内容均为模糊图片，难以通过文档内容进行受害者分析，此处主要以诱饵文件名结合首次发现地等信息对受害者进行分析。

诱饵“FW Report on demonstration of former CNRP in Republic of
Korea.doc”可译为“关于在韩国的前CNRP示威活动的第一手报告.doc”。CNRP即柬埔寨救国党，该党被柬埔寨最高法院在2017年11月16裁决解散。该党领袖莫淑华在2018年6月24领导在韩务工人员在韩国首尔举行示威活动，要求日本不要承认柬埔寨大选（7月29日举行）结果，以及释放该党主席根索卡。由此可推测，此次攻击的受害者极有可能为柬埔寨政府或关注柬埔寨政事的相关目标。有趣的是，微步在线2017年8月份发布的报告《“海莲花”团伙的最新动向分析》曾披露相关针对柬埔寨选举的攻击活动，结合此前以2018柬埔寨展望会议为主题的攻击，说明APT32持续在针对柬埔寨进行定向攻击。

针对macOS平台的诱饵名为“Scanned Investment Report-July
2018”，可译为“扫描的2018年7月投资报告”，疑似针对金融相关目标。

诱饵“feedback, Rally in USA from July 28-29,
2018”，可译为“从2018年7月28日至29日美国拉力赛的反馈”，疑似针对体育或汽车相关行业目标。

##  **附录**

获取本次报告IOC请访问链接：<https://x.threatbook.cn/nodev4/vb4/article?threatInfoID=785>。

 ***本文作者：Threatbook，转载请注明来自FreeBuf.COM**

