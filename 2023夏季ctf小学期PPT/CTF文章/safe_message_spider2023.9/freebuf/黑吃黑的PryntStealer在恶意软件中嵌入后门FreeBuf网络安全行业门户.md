窃密对于网络犯罪来说，始终都是不可缺少的一部分。攻击者可以通过窃密获取更多信息，来判断攻击目标的价值高低，从而最大化自己的利益。为了使技术不太高的普通攻击者也能够使用，包括
Prynt Stealer 在内的信息窃取类恶意软件通常都使用构建工具进行配置。然而，Zscaler ThreatLabz 研究人员发现 Prynt
Stealer 构建工具中存在一个秘密后门，监控其他攻击者收集的受害者数据并回传给构建工具开发者的私人 Telegram 聊天，这就是俗称的“黑吃黑”。

Prynt Stealer 是一个新出现的窃密恶意软件家族，是通过 .NET 编写的恶意软件。分析人员确定 Prynt Stealer
与至少两个开源恶意软件家族存在代码共用。

## Prynt Stealer 起源

Prynt Stealer 似乎直接从开源恶意软件的代码中进行复制粘贴，但借用的代码有很多并没有被实际使用。Prynt Stealer 的代码主要源自
AsyncRAT 与 StormKitty，其中 AsyncRAT 的代码作为主模块并随后调用 StormKitty 进行窃密。

Prynt Stealer 中大部分 AsyncRAT 的功能都被禁用了，C&C 服务器 URL 被设置为
127.0.0.1。但恶意软件中嵌入的证书如下所示：

![image.png-40.7kB](https://image.3001.net/images/20220910/1662824098_631caea29702615aa71a7.png!small)嵌入证书

值得注意的是，该证书是归属与 WorldWind 窃密恶意软件的，当然该恶意软件也由 Prynt Stealer 的开发者进行出售。

## AsyncRAT/StormKitty 代码比较

Prynt Stealer 作者在 AsyncRAT 的配置中新增了两个字段，用于通过 Telegram 进行数据泄露。

![image.png-340.2kB](https://image.3001.net/images/20220910/1662824099_631caea343b78294abad3.png!small)代码对比

向 Telegram 发送信息的主要代码是从 StormKitty 复制的，如下所示：

![image.png-551.7kB](https://image.3001.net/images/20220910/1662824101_631caea59d4d534e81efe.png!small)代码对比

主要的区别在于字段的名称与顺序，并且在 Prynt Stealer 中缺少与检测色情网站相关的字段。

## 技术细节

### 反检测

Prynt Stealer 创建了一个线程，该线程在 AsyncRAT 的静态构造函数中调用名为 processChecker 的函数，如下所示。

![image.png-230.9kB](https://image.3001.net/images/20220910/1662824102_631caea6b94893bd7a4e4.png!small)processChecker
代码

Prynt Stealer 使用该线程持续监控受害者的进程列表。如果检测到以下任何进程，恶意软件将阻止 Telegram 通信：

> taskmgr
>
> processhacker
>
> netstat
>
> netmon
>
> tcpview
>
> wireshark
>
> filemon
>
> regmon
>
> cain

### Telegram 通信

Prynt Stealer 创建一个线程使用 Telegram getUpdates API 轮询要下载的文件，如下所示。

![image.png-147.2kB](https://image.3001.net/images/20220910/1662824104_631caea82044cb1459890.png!small)下载命令

### 数据窃密

Prynt Stealer 从各种应用程序中窃取数据，并将数据发送到构建工具中配置的 Telegram 通道，如下所示。

![image.png-418.8kB](https://image.3001.net/images/20220910/1662824105_631caea92b1b36d0600ca.png!small)构建工具

Prynt Stealer 的日志会发送到开发者的 Telegram，如下所示。

![image.png-254.7kB](https://image.3001.net/images/20220910/1662824106_631caeaa8fb5c94d2aeb4.png!small)后门回传日志文件

过去也有过免费使用的恶意软件，开发者在其中植入后门实现“黑吃黑”。但 Prynt Stealer
是一个收费的恶意软件，不仅恶意软件要收费还会窃取其他攻击者的劳动成果。

## Prynt Stealer / WorldWind / DarkEye

ThreatLabz 已经确定了至少两个 Prynt Stealer 的变种，被称为 WorldWind 和
DarkEye。这三者非常相似，差别很小，应该是同一个开发者编写的恶意软件。下图显示了过去一年中发现的三类样本的百分比情况：

![image.png-115.4kB](https://image.3001.net/images/20220910/1662824107_631caeaba4bf0ae94a189.png!small)在野分布情况

Prynt 和 WorldWind 均由同一开发者在以下网站上出售：

![image.png-17.6kB](https://image.3001.net/images/20220910/1662824108_631caeac62b14fd1212f6.png!small)销售渠道

网站的截图如下所示：

![image.png-193.5kB](https://image.3001.net/images/20220910/1662824108_631caeace8cb923676522.png!small)销售网站截图

当然，各种地下论坛也都有流传 Prynt Stealer 的破解版，并且源代码也已经上传到 GitHub 上。Prynt Stealer 在犯罪分子常用的
Telegram 频道中也有免费提供的宣传，如下所示：

![image.png-212.3kB](https://image.3001.net/images/20220910/1662824109_631caeadca3e14552171c.png!small)Telegram
频道中的宣传

构建工具中嵌入了 DarkEye Stealer 和 Loda RAT 后门，这些免费版本可能就是开发者故意泄露的，以此实现“黑吃黑”。

## 三者功能比较

Prynt、WorldWind 和 DarkEye 之间的差异非常小，功能基本都相同，如下所示：

![image.png-37.5kB](https://image.3001.net/images/20220910/1662824110_631caeaef3a9065fc7a78.png!small)三者功能对比

StormKitty、Prynt Stealer、WorldWind 和 DarkEye 之间的字段名称比较如下所示：

![image.png-97.1kB](https://image.3001.net/images/20220910/1662824111_631caeaf86cd5d152eabb.png!small)字段名称比较

## Prynt Stealer 构建工具

带有后门的构建工具执行过程如下所示：

![image.png-142.9kB](https://image.3001.net/images/20220910/1662824112_631caeb0841ace682f838.png!small)后门执行流程

Prynt Stealer 构建工具包括以下文件：

> Stub.exe
>
> Prynt Stealer.exe
>
> Prynt Stealer sub.exe
>
> Prynt.exe

### Stub.exe

获取 Prynt Stealer sub.exe中的资源，并根据RCData资源部分中的设置执行操作，如下所示。

![image.png-68.2kB](https://image.3001.net/images/20220910/1662824113_631caeb16e130cb8a85c2.png!small)资源枚举函数

从字符串 `C:\Users\DarkCoderSc\Desktop\Celesty
Binder\Stub\STATIC\Stub.pdb`可见，Prynt Stealer sub.exe 是使用 Celesty Binder 生成的。

该二进制文件以明文形式将嵌入的 Payload 存储在 RBIND 资源下，被配置为在 %TEMP% 文件夹中释放并执行 Payload，如下所示：

![image.png-97.8kB](https://image.3001.net/images/20220910/1662824114_631caeb222654ee7518bc.png!small)资源数据

DROPIN 的其他有效路径包括：

> %APPDATA%
>
> %PROGFILES%
>
> %DEFDRIVE%
>
> %STARTUPDIR%
>
> %LAPPDATA%
>
> %USERDIR%

### Prynt Stealer.exe

Prynt Stealer 构建工具是 AsyncRAT 构建工具的定制化版本，修改了界面并且在 main 函数中添加了一行语句，以从 `{Builder
Path}/Stub/Prynt.exe`运行加载程序。

### Prynt.exe

该文件为 .NET 编写的加载程序，只是通过硬编码的 URL 下载 Payload 并执行，如下所示：

![image.png-336.5kB](https://image.3001.net/images/20220910/1662824115_631caeb3235fbc01c8376.png!small)混淆与去混淆操作

下载的 Payload 为 DarkEye Stealer，也算是 Prynt Stealer 的一个变种。

### DarkEye Stealer

该文件本质上还是 Prynt Stealer，只在代码布局上存在细微差别。其配置相关的信息如下所示：

![image.png-768.7kB](https://image.3001.net/images/20220910/1662824115_631caeb3f0f3ac2c2f8d8.png!small)配置信息

DarkEye 与 Prynt 和 Worldwind 的主要区别在于 AsyncRAT 的部分是通过配置相关设置来填充的，而且有些早期版本的
DarkEye 并没有使用 AsyncRAT。

### Loda RAT

Loda RAT 是一个基于 Autoit 开发的远控木马，在 2017
年被首次发现。此后一直非常活跃，并且多年来一直在持续更新，是一个相当强大的恶意软件。

## 总结

现在互联网上有许多开源的恶意软件源码，这使攻击者开发恶意软件变得非常容易。Prynt Stealer 的开发者将 Telegram Token 与聊天 ID
硬编码到恶意软件中，添加了一个后门来窃取客户的信息。

## IOC

> d8469e32afc3499a04f9bcb0ca34fde63140c3b872c41e898f4e31f2a7c1f61f  
> f15e92c34dd8adfcd471d726e88292d6698217f05f1d2bcce8193eb2536f817c  
> 3b948a0eb0e9bbca72fc363b63ffd3a5983e23c47f14f8296e8559fd98c25094  
> bb96db7406566ec0e9305acde9205763d4e9d7a65f257f3d5c47c15f393628ec  
> e48179c4629b5ab9e53ccb785ab3ee5eeb2e246e1897154a15fec8fd9237f44b  
> 9678ca06068b705da310aa2f76713d2d59905b12b67097364160857cd1f90c58  
> 654f080d5790054f0cd1a0f9b31cd7a82a4722ff3ce5093acdc31ff154f1ae24  
> cb132691793e93ad8065f857b4b1baba92e937cfc3d3a8042ce9109e12d32b4c  
> d37d0ae4c5ced373fe1960af5ea494a6131717d1c400da877d9daa13f55439bb  
> c79aed9551260daf74a2af2ec5b239332f3b89764ede670106389c3078e74d1a  
>
> https://cdn.discordapp.]com/attachments/523238636561629190/890007970207907871/vltn.exe  
> bigdaddy-service.biz:6606  
> bigdaddy-service.biz:7707  
> bigdaddy-service.biz:8808  
> daddy.linkpc.net:1199

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/no-honor-among-> thieves-prynt-stealers-backdoor-exposed)

