# 1 概述

近期，安天应急响应中心（安天CERT）在梳理攻击活动时发现CNC组织使用的两个下载器，其中一个下载器具有摆渡攻击的能力，利用移动存储设备作为“渡船”，间接从隔离网中窃取攻击者感兴趣的文件；另一个下载器使用欺骗性的具有不可信数字证书的C2节点进行通信。

CNC组织目前已知最早于2019年被发现，当时由于其使用的远控木马的PDB路径信息中包含了cnc_client，因此该组织被命名为CNC。该组织主要针对军工和教育行业进行攻击。

## 2 样本分析

### 2.1 PrivateImage.png.exe（下载器1）

 **2.1.1 样本概述**

PrivateImage.png.exe会根据该文件是否在%localappdata%路径下选择两种方式执行。

  1. 如果在%localappdata%路径下，不断检测是否有新设备接入；若有，则将文件本身复制到新设备中，以便通过可移动设备传播。
  2. 如果不在%localappdata%路径下，首先判断%localappdata%\ImageEditor.exe是否存在：
    1. 如果存在，跳过后续操作退出。
    2. 如果不存在，判断互联网连接状态：
      1. 如果可连网，下载后续下载器。
      2. 如果不可连网，从Recent文件夹下的快捷方式中获取.docx或.pptx后缀的文件，复制文件到当前目录下新建的以用户名命名的隐藏文件夹中，并以符号替换后的文件路径命名。

### 2.1.2 详细分析

表 2‑1 PrivateImage.png.exe

 **病毒名称**

|

**[Trojan[Downloader]/Win32.APT](https://www.virustotal.com/gui/search/entity%253Aundefined%2520antiy_avl%253ATrojan%255BDownloader%255D%252FWin32.APT)**  
  
---|---  
  
 **原始文件名**

|

PrivateImage.png .exe(空格很长，伪装成图片)  
  
 **MD5**

|

da3d305d1b47c8934d5e1f3296a8efe0  
  
 **处理器架构**

|

AMD AMD64  
  
 **文件大小**

|

[1.16 MB (1216000
bytes)](https://www.virustotal.com/gui/search/size%253A1216000)  
  
 **文件格式**

|

Win32 EXE  
  
 **时间戳**

|

[2022:02:23
21:30:27](https://www.virustotal.com/gui/search/metadata%253A%25222022%253A02%253A23%252021%253A30%253A27%252B00%253A00%2522)UTC  
  
 **数字签名**

|

无  
  
 **加壳类型**

|

无  
  
 **编译语言**

|

[Compiler: Microsoft Visual C/C++ (2017
v.15.9)](https://www.virustotal.com/gui/search/detectiteasy%253A%2522Compiler%253A%2520Microsoft%2520Visual%2520C%252FC%252B%252B%2520\(2017%2520v.15.9\)%2522)  
  
 **VT** **首次上传时间**

|

2022-03-26 10:51:26 UTC  
  
 **VT** **检测结果**

|

12/70  
  
样本运行后，首先会获取当前用户名，用在后续路径拼接的操作中。

![](https://image.3001.net/images/20221231/1672458605_63afb16dcaaf99fba59fb.png!small)

图 2‑1 获取当前用户名

获取当前文件的路径，并判断是否在%localappdata%目录下。

![](https://image.3001.net/images/20221231/1672458647_63afb197af0f82c8b5baa.png!small)

图 2‑2 判断路径中是否包含appdata\local

如果在%localappdata%目录下，则会获取系统中的所有驱动器字符串。

![](https://image.3001.net/images/20221231/1672458739_63afb1f3eaf05cfc04853.png!small)

图 2‑3 获取系统中的所有驱动器字符串

通过判断前一次的驱动器字符串与本次获取到的驱动器字符串是否相同，来确定是否有新设备接入。

![](https://image.3001.net/images/20221231/1672458764_63afb20c43d64d352886a.png!small)

图 2‑4 判断是否有新设备接入

如果存在新设备，获取新设备的名称，若新设备中不存在当前文件，则将当前文件复制到新设备。然后将指示单词“-firstcry”拼接到主机名后，用于同攻击者控制的设备通信。若新设备中已存在当前文件，则将指示单词“-alleat”拼接到主机名后。

![](https://image.3001.net/images/20221231/1672458791_63afb2272f05604ae8206.png!small)

图 2‑5 将样本自身复制到新设备中

样本与攻击者控制的设备通信。

![](https://image.3001.net/images/20221231/1672458821_63afb2450839fa39601a2.png!small)

图 2‑6 将新设备的情况发送回控制端

如果不在%localappdata%目录下，加载样本资源中的图片并将其释放到同目录下打开。

![](https://image.3001.net/images/20221231/1672458843_63afb25b2e5323266266d.png!small)

图 2‑7 加载并打开资源中的图片

资源节中包含的图片。

![](https://image.3001.net/images/20221231/1672458868_63afb2747ea79dac7c358.png!small)

图 2‑8 样本资源中包含的图片

首先进行字符串拼接。

![](https://image.3001.net/images/20221231/1672458889_63afb28990421c7b57646.png!small)

图 2‑9 字符串拼接

然后判断%localappdata%\ImageEditor.exe是否存在，如果存在跳过后续操作，结束进程。

![](https://image.3001.net/images/20221231/1672458913_63afb2a14fa510ff5145f.png!small)

图 2‑10 通过获取文件属性判断文件是否存在

测试与www[.]baidu.com的通信，判断当前环境下互联网连接状况。

![](https://image.3001.net/images/20221231/1672458944_63afb2c03ab01b5c59d4e.png!small)

图 2‑11 测试是否联网

如果互联网不可用，拼接字符串，在样本所在目录创建以当前用户名命名的隐藏文件夹。

![](https://image.3001.net/images/20221231/1672459698_63afb5b2cb7a334f9db14.png!small)

图 2‑12 创建隐藏文件夹

从Recent文件夹下的快捷方式中获取.docx或.pptx后缀的文件，查找最近打开的.docx和.pptx后缀的文件。

![](https://image.3001.net/images/20221231/1672459726_63afb5cec9c2918cd03ba.png!small)

图 2‑13 文件查找

若找到，则将其复制到创建的隐藏文件夹中，文件采用将文件完整路径中的“\”、“：”修改为“_”的方式命名。

![](https://image.3001.net/images/20221231/1672461989_63afbea50995559e8bde1.png!small)

图 2‑14 文件复制

测试机中收集的文件及其命名方式如下。

![](https://image.3001.net/images/20221231/1672462011_63afbebb28eebcffb4d4a.png!small)

图 2‑15 测试机中收集的文件

如果互联网可用，判断C:\ProgramData\USOshared文件夹是否存在，若不存在创建该文件夹。

![](https://image.3001.net/images/20221231/1672462040_63afbed8e466f9c5cf94d.png!small)

图 2‑16 创建文件夹

随后将会从185.25.51.41/control/utility/YodaoCloudMgr处下载恶意的后续的下载器，并将其复制到USOshared文件夹中，随后将会删除%temp%中下载的文件。

![](https://image.3001.net/images/20221231/1672462064_63afbef0277c00a30c362.png!small)

图 2‑17 拼接字符串用于下载后续的下载器

如果成功下载到文件，将其保存到%temp%下的YodaoCloudMgr中。

![](https://image.3001.net/images/20221231/1672462095_63afbf0f5107b59f32d9b.png!small)

图 2‑18 下载并保存到本地

将YodaoCloudMgr从%temp%复制到C:\ProgramData\USOshared\YodaoCloudMgr.exe后删除%temp%下的YodaoCloudMgr文件。

![](https://image.3001.net/images/20221231/1672462118_63afbf26e930b418caca5.png!small)

图 2‑19 复制与删除操作

创建任务计划，将C:\ProgramData\USOshared\YodaoCloudMgr.exe添加到任务计划程序库中，每隔2分钟执行一次。并根据下载和创建任务计划的结果构建回传信息：23Fi45XX代表下载成功，23Fi45NNXX代表下载失败；45tDdd43543代表任务计划创建成功，45tDnn43543代表任务计划创建失败。

![](https://image.3001.net/images/20221231/1672462151_63afbf472fca0656211c8.png!small)

图 2‑20 创建任务计划，定时执行YodaoCloudMgr.exe文件

测试机中创建的任务计划如下。

![](https://image.3001.net/images/20221231/1672462178_63afbf624b915c8820eb7.png!small)

图 2‑21 创建的任务计划

获取当前环境下的进程列表。

![](https://image.3001.net/images/20221231/1672462203_63afbf7b03bbec8df2e06.png!small)

图 2‑22 获取进程列表

将获取到的进程列表同先前构造的回传信息进行拼接，并采用base64编码方法处理拼接后的内容。

![](https://image.3001.net/images/20221231/1672462228_63afbf94c381e975c5472.png!small)

图 2‑23 拼接回传信息

使用URLDownloadToFileW与控制端通信，回传收集的信息。如果任务计划创建失败，则通过CreateProcessA执行C:\ProgramData\USOshared\YodaoCloudMgr.exe。根据静态分析推测，如果YodaoCloudMgr.exe启动失败，删除文件后会从github存储库中获取内容执行。

![](https://image.3001.net/images/20221231/1672462255_63afbfafd717826715369.png!small)

图 2‑24 获取内容执行

### 2.2 YodaoCloudMgr.exe（下载器2）

 **2.2.1 样本概述**

YodaoCloudMgr.exe由PrivateImage.png.exe下载并执行，主要用于下载后续载荷。分析时发现文件内部存在文件搜寻、启动进程等相关代码，同时发现样本在通信时使用的不可信证书。

![](https://image.3001.net/images/20221231/1672462389_63afc035acf8eb0e35ea8.png!small)

图 2‑25 通信使用不可信的证书

 **2.2.2 详细分析**

表 2‑2 YodaoCloudMgr.exe文件

 **病毒名称**

|

**[Trojan[Downloader]/Win32.APT](https://www.virustotal.com/gui/search/entity%253Aundefined%2520antiy_avl%253ATrojan%255BDownloader%255D%252FWin32.APT)**  
  
---|---  
  
 **原始文件名**

|

[yodaocloudmgr.exe_](https://www.virustotal.com/gui/search/name%253Ayodaocloudmgr.exe_)  
  
 **MD5**

|

c024eb3035dd010de98839a2eb90b46b  
  
 **处理器架构**

|

AMD AMD64  
  
 **文件大小**

|

3.22 MB (3378688 bytes)  
  
 **文件格式**

|

Win32 EXE  
  
 **时间戳**

|

2022:01:14 23:47:14 UTC  
  
 **数字签名**

|

无  
  
 **加壳类型**

|

无  
  
 **编译语言**

|

[Microsoft Visual C/C++ (2017
v.15.9)](https://www.virustotal.com/gui/search/detectiteasy%253A%2522Compiler%253A%2520Microsoft%2520Visual%2520C%252FC%252B%252B%2520\(2017%2520v.15.9\)%2522)  
  
 **VT** **首次上传时间**

|

2022-03-28 16:26:44 UTC  
  
 **VT** **检测结果**

|

18/71  
  
样本中存在待解密的字符串。

![](https://image.3001.net/images/20221231/1672462460_63afc07c60c5314cf3627.png!small)

图 2‑26 带解密的字符串

字符串通过对称加密XXTEA算法进行解密操作。

![](https://image.3001.net/images/20221231/1672462482_63afc09289c930c086a44.png!small)

图 2‑27 加密算法

通过stat函数获取文件信息，判断RNGdTMP899是否存在。

![](https://image.3001.net/images/20221231/1672462507_63afc0abeb92dc545050d.png!small)

图 2‑28 判断%temp%路径下是否存在RNGdTMP899文件

如果不存在该文件，则生成15字节的随机字符串，随机字符串用于URL拼接。字节的取值在“ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/”中。

![](https://image.3001.net/images/20221231/1672462531_63afc0c30ea75f5cea93d.png!small)

图 2‑29 生成15字节随机字符串

若当前环境下不存在RNGdTMP899文件，创建RNGdTMP899文件。

![](https://image.3001.net/images/20221231/1672462550_63afc0d64453f71be510f.png!small)

图 2‑30 创建RNGdTMP899文件

而后将随机字符串写入该文件。

![](https://image.3001.net/images/20221231/1672462576_63afc0f0ddf35d55be40f.png!small)

图 2‑31 写入随机字符串

判断RNGdTMP899文件属性，若文件不为隐藏属性则将其设置为隐藏属性。

![](https://image.3001.net/images/20221231/1672462596_63afc10405603466ed496.png!small)

图 2‑32 修改RNGdTMP899文件属性为隐藏

获取RNGdTMP899中的随机字符串，此次生成的随机字符串为RLCTEJddUbAJMJR，并拼接成https[:]//45.86.162.114/query=RLCTEJddUbAJMJR/%20%getting,forum。

![](https://image.3001.net/images/20221231/1672462647_63afc13728489c13bf136.png!small)图
2‑33 URL拼接

根据网络行为观测，样本首先会请求拼接的https[:]//45.86.162.114/query=RLCTEJddUbAJMJR/%20%getting,forum，然后请求https[:]//45.86.162.114/images-css/RLCTEJddUbAJMJR/imagelogo.css获取数据。

![](https://image.3001.net/images/20221231/1672462690_63afc162d0355d70fddac.png!small)

图 2‑34 拼接URL

之后每隔1分钟，循环请求https[:]//raw.githubusercontent.com/yuiopk1456/beutifymyapp/main/LICENSE。通过URL可以看出攻击者有可能在指定IP失效后通过github平台传输数据，猜测传输的数据可能为XXTEA算法加密后的攻击者指定的IP或域名。

![](https://image.3001.net/images/20221231/1672462720_63afc18068e4ae45168eb.png!small)

图 2‑35 循环执行该段代码，间隔时间为1分钟

查找接收到数据的标记位置。

![](https://image.3001.net/images/20221231/1672462738_63afc19297a52c2e36cb5.png!small)

图 2‑36 查找接收到数据的标记位置

对其后数据应存在解密操作。

![](https://image.3001.net/images/20221231/1672462764_63afc1ace99b1169d0739.png!small)

图 2‑37 解密获取到的数据

通过在github上搜索beutifymyapp，关联到疑似该组织的github存储库，存储库的创建者名字也与本次攻击活动中github存储库的创建者名字yuiopk1456相似。仅在2021年11月存在对该存储库的操作，在这之后也未创建其他存储库。

![](https://image.3001.net/images/20221231/1672462783_63afc1bf25efe4001f3c8.png!small)

图 2‑38 github上关联到的相似存储库

在关联到的相似存储库中，发现可疑的字符串，可能为加密后的域名或IP。

![](https://image.3001.net/images/20221231/1672462800_63afc1d072f086727400c.png!small)

图 2‑39 github中的可疑字符串

连接github存储库中存放的IP或域名。

![](https://image.3001.net/images/20221231/1672462824_63afc1e8949e4b7702eea.png!small)

图 2‑40 socket连接

由于域名、IP以及github地址均失效，故无法继续跟进。通过静态分析样本推测，攻击者与控制端通信后可能存在获取指定目录文件列表、启动进程等操作。

获取指定目录文件列表。

![](https://image.3001.net/images/20221231/1672462847_63afc1ffe74411653678f.png!small)

图 2‑41 文件查找相关操作

创建管道。

![](https://image.3001.net/images/20221231/1672462868_63afc214a70c842ef216c.png!small)

图 2‑42 创建管道

启动进程。

![](https://image.3001.net/images/20221231/1672462890_63afc22aea769b03f81a3.png!small)

图 2‑43 启动进程

## 3 归因分析

在先前观测中发现，部分CNC组织人员会在开发环境中集成vcpkg，此次发现的样本中同样存在该特点，且路径也同以往使用的路径一致。

![](https://image.3001.net/images/20221231/1672462940_63afc25c8f0791d48ec90.png!small)

图 3‑1 此次攻击活动中存在的路径信息

![](https://image.3001.net/images/20221231/1672462956_63afc26cf037ffb6fa881.png!small)

图 3‑2 以往攻击活动中存在的路径信息

样本中的部分代码也十分相似。

![](https://image.3001.net/images/20221231/1672462980_63afc28430a6d0c9380e4.png!small)

图 3‑3 此次攻击活动中的部分代码

![](https://image.3001.net/images/20221231/1672462995_63afc2939d34f2a3db621.png!small)

图 3‑4 以往攻击活动中的部分代码

加密函数大致相同。

![](https://image.3001.net/images/20221231/1672463028_63afc2b49c29f1ad4df48.png!small)

图 3‑5 以往攻击活动中加密函数的部分代码

![](https://image.3001.net/images/20221231/1672463050_63afc2cad5947830dc366.png!small)

图 3‑6 此次攻击活动中加密函数的部分代码

综上所述，初步将此次攻击活动归因到CNC组织。

  

## 4 威胁映射框架

本次攻击活动共涉及ATT&CK框架中的8个阶段的15个技术点，具体行为描述如下表：

表 4‑1 近期CNC组织攻击活动的技术行为描述表

 **ATT &CK** **阶段**

|

 **具体行为**

|

 **注释**  
  
---|---|---  
  
执行

|

诱导用户执行

|

PrivateImage.png.exe伪装成图片诱导用户执行  
  
执行

|

利用计划任务/工作

|

YodaoCloudMgr.exe路径被加载到计划任务中执行  
  
持久化

|

利用计划任务/工作

|

YodaoCloudMgr.exe路径被加载到计划任务中执行  
  
防御规避

|

混淆文件或信息

|

回传的进程信息进行base64编码  
  
防御规避

|

去混淆/解码文件或信息

|

样本中的关键字符串通过对称加密算法XXTEA解密  
  
防御规避

|

隐藏行为

|

创建隐藏的文件夹用于收集信息，以及将RNGdTMP899文件设置隐藏属性  
  
发现

|

发现文件和目录

|

发现RECENT目录中的文件，并可能存在指定目录搜寻的操作  
  
发现

|

发现系统信息

|

发现计算机中的驱动器列表  
  
发现

|

系统时间发现

|

可以获取到计算机上的本地时间  
  
横向移动·

|

通过可移动介质复制

|

检测磁盘列表是否有变动，以便复制到可移动介质中  
  
收集

|

自动收集

|

自动收集进程列表、当前用户名、本地时间等信息  
  
收集

|

收集本地系统数据

|

收集进程列表、用户名、本地时间等信息  
  
命令与控制

|

使用应用层协议

|

使用应用层协议通信  
  
命令与控制

|

编码数据

|

回传的进程信息进行base64编码  
  
数据渗出

|

自动渗出

|

收集到的进程列表信息等自动回传到控制端  
  
CNC组织相关攻击活动的行为技术点的ATT&CK框架图谱如下图所示：

![](https://image.3001.net/images/20221231/1672463191_63afc35795b4c6cee6c1b.png!small)

图 4‑1 CNC组织攻击活动对应ATT&CK框架映射图

## 5 总结

近些年，APT组织向隔离网络攻击的意图越发明显，渗透隔离网络的攻击样本不断增多，以Darkhotel[1]、幼象[2][3]为典型代表的攻击组织均自研相关攻击武器并不断更新。此次攻击活动中的CNC组织样本同该组织以往的样本相比也进行了升级，在开发阶段同样集成了vcpkg开发环境，也存在从github存储库中获取内容的行为。在横向移动阶段，在判断是否有新存储设备接入的手法上，与此前通过GetDriveTypeA获取接入设备的类型的判断方法不同，本次攻击活动的样本通过不断获取驱动器列表的方法，一旦发现有新存储设备接入，则将文件复制到新接入的存储设备中，以便达成在隔离网中传播的目的。

## 6 IoC

185.25.51.41  
  
---  
  
45.86.162.114  
  
da3d305d1b47c8934d5e1f3296a8efe0  
  
c024eb3035dd010de98839a2eb90b46b  
  
https://raw.githubusercontent.com/yuiopk1456/beutifymyapp/main/LICENSE  
  
https://raw.githubusercontent.com/gazelter231trivoikpo1/questions/main/beautify.js  
  
  

## 参考资料

  * Darkhotel组织渗透隔离网络的Ramsay组件分析

[https://www.antiy.cn/research/notice&report/research_report/20200522.html](https://www.antiy.cn/research/notice&report/research_report/20200522.html)

  * “幼象”组织针对巴基斯坦国防制造商的攻击活动分析报告

[https://www.antiy.cn/research/notice&report/research_report/20210222.html](https://www.antiy.cn/research/notice&report/research_report/20210222.html)

  * “幼象”组织在南亚地区的网络攻击活动分析

[https://www.antiy.cn/research/notice&report/research_report/20211119.html](https://www.antiy.cn/research/notice&report/research_report/20211119.html)

