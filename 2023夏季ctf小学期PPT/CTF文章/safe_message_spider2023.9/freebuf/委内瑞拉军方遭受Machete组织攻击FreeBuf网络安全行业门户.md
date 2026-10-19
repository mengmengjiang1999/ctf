## 概述

**Machete是一个由西班牙语组织开发的网络间谍工具集，自2010年以来一直处于活动之中。该组织持续为其恶意软件开发新功能。他们长期攻击的重点在拉丁美洲国家，多年来一直收集目标国家情报并改进他们的攻击策略。
近期研究人员发现了一项持续的，针对性很强的攻击活动，其中大多数目标都是军事组织。**

在2019年，已超过50台计算机被Machete攻击。其中约75％属于拉美各国的军事力量，其中一半以上属于委内瑞拉军队。

Machete组织使用鱼叉式钓鱼技术。他们很了解自己的目标，如何与目标进行沟通，以及哪些文件最有价值。
Machete不仅可以处理常见的办公文档，还可以处理地理信息系统（GIS）使用的专用文件。该组织对导航路线的文件也很感兴趣。

Machete组织处于不断的发展之中。主要的后门是基于Python编写的，发展过程中增加了几个新功能，例如更具兼容性的C＆C通信机制，利用Mozilla位置服务来对受感染的计算机进行地理定位，以及盗取可移动存储设备上的文件。

该组织非常活跃。在一些案例中攻击者盗取文件，并在同一天将该文件与恶意软件捆绑使用。

## 简介

2019年上半年委内瑞拉成为人们关注的焦点。从反对总统的起义到军队的密谋，委内瑞拉的局势一直受到国际关注。同时针对委内瑞拉军方的网络间谍案也受到了关注。首先由卡巴斯基在2014年发布报告及后来由Cylance在2017年发布报告，Machete攻击行为被发现，该组织主要针对拉丁美洲国家知名人士和组织。

2018年Machete重新出现并添加了新代码和新功能。截至2019年6月，已发现超过50名受害者被其监视，其中一半以上是属于委内瑞拉军队的计算机。以GB为单位的机密文件和私人信息已被泄露到攻击者控制的服务器上。

Machete主要以拉丁美洲为目标，由一个西班牙语小组开发，利用鱼叉式钓鱼进行攻击活动。

## 传播方式

Machete依靠鱼叉式钓鱼来渗透目标。这些电子邮件包含下载的链接（或附件），附件中为带有恶意软件的压缩文件和用作诱饵的文档。

图1是Machete向潜在受害者发送的PDF文件。 图1是一份军事文件，生成日期为2019年5月21日，在同一天该文件被用作钓鱼附件发送给目标。

![](https://image.3001.net/images/20190807/1565165847_5d4a8917a85e5.png!small)

## 主要目标

Machete是一个非常有针对性的组织，多年来一直处于活跃状态。该组织用真实文档作诱饵，因此受害者从未意识到他们受到了攻击。

自从3月底到2019年5月底，有超过50台受害计算机正在与C＆C服务器进行通信，每周上传的千兆字节数据。通过分析确定超过一半的受感染计算机属于委内瑞拉军队，包括委内瑞拉的几个旅和部门。其他受到攻击的计算机与教育，警察和外交事务部门有关。厄瓜多尔军队是另一个被Machete攻击的军方组织。被攻击国家如图所示。

![](https://image.3001.net/images/20190807/1565166000_5d4a89b0dcb58.png!small)

## 技术分析

在2014年至2017年之间，恶意软件以NSIS打包文件形式传播。提取文件后会执行Machete的py2exe组件， py2exe
是将Python转换为Windows可执行文件的工具，这些可执行文件运行不需要Python环境。

新版本Machete首次出现在2018年4月，第一阶段使用了下载器，将Machete的后门组件安装在被攻击的系统上。

![](https://image.3001.net/images/20190807/1565166132_5d4a8a3425184.png!small)

从上图可知，下载器是一个自解压文件（由7z SFX Builder制作）。打开一个PDF或Microsoft
Office文件用作诱饵，然后下载可执行文件，包含实际的下载程序二进制文件（py2exe组件）和一个配置文件，下载程序的目标URL作为加密字符串。

所有下载网址都是Dropbox或Google文档。 这些URL上的文件都是自解压（RAR SFX）存档，包含加密配置和恶意py2exe组件。

### 下载器

下图显示了7z自解压下载器的配置文件示例。

![](https://image.3001.net/images/20190807/1565166299_5d4a8adb32223.png!small)

rar里包含的.exe文件，其结构与最终的Machete有效payload非常相似。包含一个py2exe可执行文件和一个配置文件，配置文件中包含用于下载Machete的URL。

配置文件名为mswe，是AES加密字符串的base64编码文本。

下载程序的执行流程可归纳如下：

> 下载程序的工作目录为：％APPDATA％\ GooDown
>
> 创建计划任务（ChromeDow）以每三到六分钟执行一次下载
>
> 从mswe配置文件中读取和解密（AES）下载URL
>
> 下载Machete
>
> 下载的数据被解密（AES）并重命名为Security.exe
>
> 执行Machete
>
> 删除下载程序任务

### 混淆设置

自2018年8月以来，所有主要Machete后门组件已被混淆，使用pyminifier的-gzip参数生成的混淆。

部分混淆代码如图所示。

![](https://image.3001.net/images/20190807/1565166393_5d4a8b398183d.png!small)

在解混淆之后，仍然存在混淆的代码，包括变量的随机名称和大量垃圾代码。 利用pyobfuscate再一次解除混淆，混淆代码的示例如图所示。

### 后门组件

Machete的后门内含三个py2exe组件：GoogleCrash.exe，Chrome.exe和GoogleUpdate.exe。
首先执行GoogleCrash.exe再启动另外两个。

![](https://image.3001.net/images/20190807/1565166532_5d4a8bc41314c.png!small)

 **GoogleCrash.exe**

是恶意软件的主要组成部分，负责执行其他两个组件并创建Windows任务计划任务以实现持久控制。创建如下任务：

> Spy component 3分钟运行一次
>
> SCHTASKS /create /ST 00:00:01 /SC MINUTE /MO 03 /TR
> “C:\Users\%USERNAME%\AppData\
>
> Roaming\Chrome\Google\Chrome.exe” /TN Chrome
>
> Communication 10分钟运行一次
>
> SCHTASKS /create /ST 00:00:01 /SC MINUTE /MO 10 /TR “C:\Users\%USERNAME%
> \AppData\
>
> Roaming\Chrome\Google\GoogleUpdate.exe” /TN GoogleCrash
>
> Persistence component 30分钟运行一次
>
> SCHTASKS /create /ST 00:00:01 /SC MINUTE /MO 30 /TR “C:\Users\%USERNAME%
> \AppData\
>
> Roaming\Gchrome\GoogleCrash.exe” /TN Googleupdate32
>
> 创建完定时任务后可执行文件会被复制到如下路径：
>
> %APPDATA%\Chrome\Google\
>
> %APPDATA%\Gchrome\
>
>  **Chrome.exe**

该组件负责收集受害者的数据。 下图包含代码基于计时器执行的操作。

![](https://image.3001.net/images/20190807/1565166746_5d4a8c9a4b4ca.png!small)

被盗数据根据数据类型（屏幕截图，击键日志，新存储设备，浏览器存储信息，地理位置信息，wifi信息等）存储在不同的子文件夹中。然后，通信组件将数据发送到远程服务器。

 **GoogleUpdate.exe**

该组件负责与远程服务器通信。从jer.dll文件中读取远程连接配置：域名，用户名和密码。Machete主要通过FTP进行通信，HTTP通信是在2019年实现的。

该组件的主要功能是将文件夹中的加密文件上载到C＆C服务器上的不同子目录。下图显示了如何处理文件夹并上传文档。

该组件还有列目录、更新组件、文件分类等功能。

### 2019新组件

在2019年6月，Machete结构发生了几处变化，但功能保持不变。此版本的恶意软件分为六个组件，不再是py2exe可执行文件。

恶意组件的Python脚本，原始可执行文件以及所有使用的库都打包到一个名为python27.exe的自解压文件中。下图显示了payload的自提取。

![](https://image.3001.net/images/20190807/1565167006_5d4a8d9ebe1f1.png!small)

 **hashlbi.pyw**

此组件设置恶意软件文件夹并以计划任务运行其他组件。文件夹和文件在C：\ Python2.7下创建，其名称与普通Python中的名称相同。

下图为该组件创建的计划任务及其设置循环时间：

![](https://image.3001.net/images/20190807/1565167116_5d4a8e0c83597.png!small)

此组件还将Office文件，.pdf，.jpg / .jpeg和.rar / .zip文件从每个驱动器复制到％LOCALAPPDATA％\
Microsoft \ Dropbox \ Crashpad，并在C：\ Python2.7 \ DLLs \
hhd中创建名称基于SHA-256哈希值的目录文件。 部分代码如图所示

![](https://image.3001.net/images/20190807/1565167194_5d4a8e5ac35d6.png!small)

 **_clypes.pyw**

该组件检查正在运行的进程（每三或四个小时），从中查找Web浏览器。
它会生成一个.zip文件，其中包含每个浏览器的文件数据：Chrome，Firefox，Opera和Internet
Explorer，每个浏览器的文件名都不同。 这些文件保存在％LOCALAPPDATA％\ Microsoft \ Dropbox \
avatar_cache \中。

![](https://image.3001.net/images/20190807/1565167272_5d4a8ea89d683.png!small)

 **_bsdbd.pyw**

此组件执行任务时使用的库不同于我们之前描述的库。它使用ctypes库访问剪贴板，并将内容保存到avatar_cache文件夹中的wwancgf_.html。屏幕截图也保存在该文件夹下。

![](https://image.3001.net/images/20190807/1565167336_5d4a8ee807869.png!small)

 **_elementree.pyw**

此组件会收集地理定位等信息。

 **_mssi.pyw**

键盘记录控件，所有的文件都会保存到avatar_cache文件夹中的 vpr.html。

 **_multiproccessing.pyw**

该控件负责进行通信，从date.dll配置文件中读取两个C＆C服务器：一个是主服务器另一个是备用服务器。
每台受害计算机都在服务器上有一个文件夹，格式为：folder_campaign / MACaddr-HOSTNAME。并不是每个文档都发送到服务器，只有20个最新文档从CrashReports复制到events文件夹准备传输。

![](https://image.3001.net/images/20190807/1565167412_5d4a8f348edf2.png!small)

文件加密使用AES，base64编码，ROT13应用于文件名。

![](https://image.3001.net/images/20190807/1565167657_5d4a9029b0a8e.png!small)

在实际发送之前，文件会从events文件夹复制到instance_db文件夹。通过HTTP协议POST请求发送文件，文件夹名称会被更改，如图所示。

![](https://image.3001.net/images/20190807/1565167467_5d4a8f6bbde5c.png!small)

## 域名

最初，我们在Machete的配置文件中看到了三个域名。
在2019年它们都指向相同的IP地址，但DNS查询显示在2018年期间还有两个其他IP地址处于活动状态。下图显示了有关这些域名的信息。

![](https://image.3001.net/images/20190807/1565167703_5d4a90575cdbf.png!small)

在2019年6月，Machete停止使用FTP通信，并开始为主要通过http与C＆C服务器通信。域名
tobabean[.]expert指向IP地址142.44.236.215。
另一个服务器是u929489355.hostingerapp[.]com，IP地址是156.67.222 .88。

总结

过去针对拉丁美洲的APT攻击通常被忽视，但是这几年中有一些攻击收到了广泛关注，例如针对墨西哥银行和智利银行攻击活动。

即使在研究人员发布了针对此恶意软件解决方案后，Machete组织仍设法继续进行攻击渗透。

Machete通过对代码和基础架构进行更改提升，已可以绕过多款安全产品。
与此同时，目标组织也在提高安全防范意识和应用安全策略，因此目标组织不会第一时间被攻击成功。

关于Machete组织研究白皮书更多内容请见：<https://www.welivesecurity.com/wp-content/uploads/2019/08/ESET_Machete.pdf>

 ***参考来源：[WeLiveSecurity](https://www.welivesecurity.com/wp-content/uploads/2019/08/ESET_Machete.pdf)，由Kriston编译，转载请注明来自FreeBuf.COM**

