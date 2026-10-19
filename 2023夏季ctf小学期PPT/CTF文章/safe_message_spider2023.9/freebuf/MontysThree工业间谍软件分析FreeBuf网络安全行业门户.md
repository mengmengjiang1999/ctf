2020年夏季发现了针对性较强的工业间谍软件的活动，工具集中包含未知的C++模块。恶意软件作者将工具集命名为“ MT3”，研究人员将工具集命名为“
MontysThree”。

该恶意软件包括一组用于持久控制的C
++模块，使用隐写术从位图中获取数据，解密配置任务（屏幕截图，获取目标指纹，获取文件等）等。该恶意软件使用自定义隐写术，基于XOR的自定义加密，3DES和RSA算法进行解密和通信。

## 传播方式

初始加载程序模块在RAR自解压文件中，只有PE文件（伪装.pdf或.doc文件）， 其中一个（MD5
da49fea229dd2dedab2b909f24fb24ab）名为“Списоктелефоновсотрудников2019.doc”（“员工电话清单”，俄语），另外还有“
Tech task.pdf”和“ invitro-106650152-1.pdf”。 后者是俄罗斯医学实验室的名称。 SFX脚本如下：

> Path=%TEMP%\  
> SavePath  
> Setup=rundll32.exe "invitro-106650152-1.pdf",Open  
> Silent=1  
> Overwrite=1  
> Update=U  
> Delete=invitro-106650152-1.pdf

执行后，SFX脚本会调用％TEMP％目录中已解压缩的可执行文件，并将其删除。

## 技术分析

执行流程如下：

![1603243488_5f8f8de0392da68a8854f.png!small?1603243489329](https://image.3001.net/images/20201021/1603243488_5f8f8de0392da68a8854f.png!small?1603243489329)

下表列出了四个模块及其功能， 这些模块共享通用的通信规范。 当处理诸如配置文件和执行日志之类的共享数据时，该恶意软件会初始化线程本地存储（TLS）中的结构。

入口点DllEntryPoint（）的工作方式类似于构造函数，模块必须导出一个名为Open（）的函数，该函数不带任何参数（但可以解析命令行）并返回一个四字节的错误代码。

![1603244042_5f8f900a1ce3eb7ae1f72.png!small?1603244042705](https://image.3001.net/images/20201021/1603244042_5f8f900a1ce3eb7ae1f72.png!small?1603244042705)

### 加载程序模块

将加密数据的位图文件名作为参数提供给加载程序，加载程序会从像素数组解密下一个程序。 在第一次迭代中，它提取隐写参数数据。

![1603269728_5f8ff4601bf1d5af9ea88.png!small?1603269728710](https://image.3001.net/images/20201021/1603269728_5f8ff4601bf1d5af9ea88.png!small?1603269728710)

IID，IParam和ISize参数保存在像素阵列的前384个字节中，因此仅需要每个像素阵列字节的最后一位。
该模块使用这些字段收集48个字节的配置结构，确定下一个解密阶段。

![1603269815_5f8ff4b74ba867492ef9e.png!small?1603269815740](https://image.3001.net/images/20201021/1603269815_5f8ff4b74ba867492ef9e.png!small?1603269815740)

提取隐写参数后，使用两步算法对下一个程序进行解密。 首先，IParam算法从像素阵列的字节中选择bits。
如果IID等于2，则对收集到的字节使用四字节轮回密钥，前四个字节解密的初始密钥硬编码为0x23041920。 下一个字节的XOR公式为：  
key ^= 8 * (key ^ (key << 20))

解密结果并未注入到某个进程内存中，而是生成名为msgslang32.dll的文件放到磁盘上。 加载程序使用Windows
API函数LoadLibraryW（）和GetProcAddress（）来运行下一个阶段的Open（）函数。

### Kernel模块

内核模块包含三个用于配置解密和C2通信的加密密钥。公用和专用RSA密钥分别以PUBLICKEYBLOB和PRIVATEKEYBLOB的形式存储在.data节中，用于加密C2通信、解密3DES密钥。

第三个3DES密钥也以加密形式存储在.data节中。此密钥用于解密包含XML配置的.cab文件，该模块使用Window的标准程序“
expand.exe”解压缩.cab。

XML配置包含恶意软件的各种“任务”，例如对目标进行指纹识别，捕获屏幕截图，从%USERPROFILE%、
%APPDATA%、%APPDATA%\Microsoft\Office\Последние
файлы中最新目录中获取扩展名为.doc，.docx，.xls，.xlsx，.rtf，.pdf，.odt，.psw，.pwd的文档列表。
Последниефайлы翻译成俄语为“最近文件”。

Config包含任务计划（屏幕截图），访问令牌，感兴趣的目录和扩展：

![1603270344_5f8ff6c841671aeea2700.png!small?1603270344831](https://image.3001.net/images/20201021/1603270344_5f8ff6c841671aeea2700.png!small?1603270344831)

发现俄语字符串，例如“Снимокрабочегостола”（桌面快照），“Системнаяинформация”（系统信息），“Времявыхода”（退出时间）。

![1603270408_5f8ff7089d2d8fc807e6f.png!small?1603270409477](https://image.3001.net/images/20201021/1603270408_5f8ff7089d2d8fc807e6f.png!small?1603270409477)

解密后的配置结构如下：

![1603270440_5f8ff72809c7a2a72652a.png!small?1603270440525](https://image.3001.net/images/20201021/1603270440_5f8ff72809c7a2a72652a.png!small?1603270440525)

处理指令的主要类是CTask。 CTask的IoControl（）方法负责处理相应的任务，并可运行以下方法：

![1603270711_5f8ff837d4ed7f51299c0.png!small?1603270712529](https://image.3001.net/images/20201021/1603270711_5f8ff837d4ed7f51299c0.png!small?1603270712529)

### 通信模块

HttpTransport存在于内核模块.text部分中的四个加密数据块。当内核需要通信时，它会解密该模块，并运行Open（）函数，传递命令行参数。

根据从内核模块传输的参数，该模块可以使用RDP，WebDAV，Citrix和HTTP协议上传或下载内容。
HttpTransport也实现了使用用户令牌从Google和Dropbox公共服务下载数据。在HTTP GET /
POST请求下，该恶意软件将使用Windows API HTTP功能从URL接收隐写位图图片。

上述通信协议本身并未在模块内部实现。恶意软件利用计算机上已安装的Windows程序（例如RDP，Citrix客户端和Internet
Explorer）进行操作。可通过剪贴板将URL粘贴到浏览器中；等待并再次通过剪贴板接收结果。

Dropbox和Google数据的上传和下载依赖于另一个原理：使用自定义类CSimpleHttp进行身份验证并发送HTTP请求。

## 总结

通常恶意软件主要针对政府实体，外交官和电信运营商，像MontysThree这样的工业间谍少见很多。

就传播方式，持续性控制方法而言，其复杂性无法与顶尖APT相提并论。恶意软件开发方面（同时登录RAM和文件，将加密密钥保留在同一文件中，在远程RDP主机上运行不可见的浏览器）还不成熟。

MontysThree中的代码量以及投入的精力是巨大的：在RSA加密下存储3DES密钥，规避IDS的自定义隐写术以及使用合法的云存储隐藏C2流量。

## IOCs

### Loader

1B0EE014DD2D29476DF31BA078A3FF48

0976*42A06D2D8A34E9B6D38D45AE42

A2AA414B30934893864A961B71F91D98

### Kernel

A221671ED8C3956E0B9AF2A5E04BDEE3

3A885062DAA36AE3227F16718A5B2BDB

3AFA43E1BC578460BE002EB58FA7C2DE

### HttpTransport

017539B3D744F7B6C62C94CE4BCA444F

501E91BA1CE1532D9790FCD1229CBBDA

D6FB78D16DFE73E6DD416483A32E1D72

### Domains and IPs

autosport-club.tekcities[.]com

dl10-web-stock[.]ru

dl16-web-eticket[.]ru

dl166-web-eticket[.]ru

dl55-web-yachtbooking[.]xyz

## 原文链接

[securelist](https://securelist.com/montysthree-industrial-espionage/98972/)

  

  

