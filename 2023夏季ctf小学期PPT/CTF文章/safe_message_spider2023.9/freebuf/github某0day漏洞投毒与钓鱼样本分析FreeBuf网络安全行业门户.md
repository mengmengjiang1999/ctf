## **前言**

近日，烽火台实验室监测到多起针对安全人员的钓鱼攻击。其中一例利用MS Office Word
0DAY进行钓鱼，在github.com和Telegram群组中公开0DAY利用程序，其中并没有包含真正的利用程序，但是却捆绑了木马。运行后下载和执行木马程序，木马使用TOR匿名网络连接黑客控制服务器，接受黑客控制。平时下载运行网络上的漏洞利用程序时要多加小心，避免成为黑客的“肉鸡”。

##  **样本信息**

 **钓鱼地址：**<https://github.com/researchkendra91>（目前已无法访问）

 **钓鱼地址：**<https://github.com/octosec45/ms-word-rce-0day-poc-2023>（目前仍存活）

 **样本名：** poc.py

MD5:70182e6523bf1d9106055881b5c93e49

SHA256:c2bcda29fed175e127bf4ba66de7144509ad7d34627020444a36466b39ffcd9f

 **样本名：** cveswindows.exe

MD5:1daf1ae4b628a3a2dabacfe41a81b893

SHA256:01055e217335489d11bfba457b0ced01a06afe2270e4eec442347c93794df578

 **样本名：** cveslinux

MD5:f9b1f07ce6c2cd4a26461124a483ae46

SHA256:e582650a3e9db2f77022317db1c2c9f01411ef5333d83bd52fd9b11102a3cdfd

##  **poc.py分析**

在github.com上的钓鱼页面中，包含了MS Office Word 0DAY利用程序poc.py和一段使用帮助，如下图所示：

![](https://image.3001.net/images/20230516/1684231608_646355b8c91b517016c94.png!small)在poc.py的末尾，有段帮助信息，表明这是CVE-2023-40454的利用程序，如下图所示：

![](https://image.3001.net/images/20230516/1684231654_646355e66f46bcafb89c0.png!small)

初步看起来好像没什么问题。但是一查发现，CVE-2023-40454并不存在。如果再仔细点，在poc.py中，还有一段可疑代码，如下图所示：

![](https://image.3001.net/images/20230516/1684231683_6463560368dc99b0ec81c.png!small)

这段代码根据Win或者其他系统，分别访问

<https://github.com/octosec45/ms-word-rce-0day-poc-2023/raw/main/gitignore/cveswindows.zip>

或者

<https://github.com/octosec45/ms-word-rce-0day-poc-2023/raw/main/gitignore/cveslinux.zip>

下载不同的zip文件，然后解压再运行，解压密码为“cVe35364%”。

本次分析Win系统下的木马程序cveswindows.zip，其中包含cveswindows.exe，功能与其他版本（cveslinux.zip）的木马基本相同。

cveswindows.exe在2023-05-05被上传到virustotal.com进行检测，其中有用户表明该样本曾出现在Telegram群组的钓鱼文件中，如下图所示：

![](https://image.3001.net/images/20230516/1684231712_6463562087497b25c3040.png!small)

##  **cveswindows.exe分析**

该样本使用go语言编写，反编译后可以看到大量引用的go模块字符串，原始工程文件名为implant_windows.go，go版本为go1.20.2，如下图所示：

![](https://image.3001.net/images/20230516/1684231744_646356406128ed1efe6fd.png!small)

样本运行后，将执行一个名为port_check的函数，该函数主要检测本地端口1337是否开启，如果没有开启，则继续往下执行；如果开启，则退出程序。该功能可以实现只运行一个实例，如下图所示：

![](https://image.3001.net/images/20230516/1684231771_6463565b970ced7b86e87.png!small)

然后判断是否是管理员，再判断

%ProgramFiles%和%LOCALAPPDATA%路径下是否特定文件夹名，文件夹名包括：WindowsUpdateTaskUAACore、ChromeUpdateTaskMachinCore、ChromeUpdateTaskMachinCore等。如果不存在，则复制自身文件到其中一个文件夹下，再创建任务计划，每天18:00启动木马程序，如下图所示：

![](https://image.3001.net/images/20230516/1684231801_646356792b3cd202ef1d5.png!small)![](https://image.3001.net/images/20230516/1684231808_6463568097bb0dc547cd4.png!small)

接下来访问“https://dist.torproject.org/torbrowser”，下载tor-expert-bundle并解压，然后释放tor.exe、obfs4proxy.exe和TOR网络连接需要的配置文件到创建计划任务时的木马exe路径下，文件夹名为随机命名，然后配置TOR连接，再启动tor.exe，完成TOR网络的连接。如下图所示：

![](https://image.3001.net/images/20230516/1684231850_646356aa697e67020538b.png!small)![](https://image.3001.net/images/20230516/1684231858_646356b2161f049bd70c1.png!small)![](https://image.3001.net/images/20230516/1684231864_646356b8de78aa2c117c4.png!small)

使用TOR网络访问“https://ipinfo.io/json”，获取当前主机的外网IP，归属地，所属国家等信息，如下图所示：![](https://image.3001.net/images/20230516/1684231883_646356cb5726faaae0357.png!small)

然后获取计算机名、用户名、操作系统版本、名称，CPU等基本信息，最后再加密获取的信息，如下图所示：

![](https://image.3001.net/images/20230516/1684231904_646356e0868412641e260.png!small)

将加密的信息通过TOR网络发送到“http://yr7dhedoqr7tacpxt6xdeh6bponmp53rbfaf74iis37v4vf6vfd2vkyd.onion/0011378b1fe87c721bbd4e4e2d3d26111869c51cd37960dbe518aade0b6529aa”，进行上线，如下图所示：

![](https://image.3001.net/images/20230516/1684231934_646356fe4e78e2600f445.png!small)

上线成功后，将接受服务器返回的信息，然后解析数据执行黑客命令，可以实现上传指定文件、下载指定文件、创建cmd.exe或powershell.exe执行程序。笔者调试时，未返回有效数据。

上传指定文件相关代码，如下图所示：

![](https://image.3001.net/images/20230516/1684231961_64635719ae85d5691a444.png!small)

下载指定文件相关代码，如下图所示：

![](https://image.3001.net/images/20230516/1684231978_6463572aa6944a41f5db9.png!small)

创建cmd.exe执行程序相关代码，如下图所示：

![](https://image.3001.net/images/20230516/1684231998_6463573e35f8a48833dd9.png!small)

创建powershell.exe执行程序相关代码，如下图所示：

![](https://image.3001.net/images/20230516/1684232023_64635757d87955d7a5148.png!small)

此外，代码中还包含名为spread_USB的函数，实现USB传播木马的功能，但是还有复杂的逻辑判断后才运行该功能，笔者暂时没有找到启用该功能的条件。如下图所示：

![](https://image.3001.net/images/20230516/1684232041_64635769adedb53b8caca.png!small)

还包含名为spread_Cryptohijack的函数，实现替换剪贴板中的数字货币BTC地址，但是也有复杂的逻辑判断后才运行该功能，笔者暂时没有找到启用该功能的条件。如下图所示：

![](https://image.3001.net/images/20230516/1684232061_6463577dad6184cd66b3a.png!small)

最后监听本地端口1337，对应port_check的函数中的检测端口功能，表明木马已经在运行中。如下图所示：

![](https://image.3001.net/images/20230516/1684232272_646358502849d6e1fa1a3.png!small)

##  **参考链接**

<https://www.virustotal.com/gui/file/01055e217335489d11bfba457b0ced01a06afe2270e4eec442347c93794df578/community>

##  **样本地址**

<https://github.com/webraybtl/vulnerability0DAY>

[原文链接﻿](https://mp.weixin.qq.com/s?__biz=MzkzNjMxNDM0Mg==&mid=2247485969&idx=1&sn=e73e23e8a943e491e24cb69fe7de5021&chksm=c2a1de98f5d6578e3ed3d5e379f40168f35563e8cdc830a0fd4abc405bc23b7ce07e4b24276f&token=77531284&lang=zh_CN#rd)

