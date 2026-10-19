## **恶意文件分析**

###  **1.恶意文件描述**

2022年8月19日，深信服深盾终端实验室在运营工作中捕获到一款功能复杂的新型信息窃取病毒， **该病毒由 C++ 语言编写，套用了开源软件
ZLMediaKit 的部分代码并在其基础上开发恶意模块。该程序的释放的文件包含具有数字签名的正常的库文件，以及没有数字签名但伪装成正常系统文件的 exe
程序。**

该软件疑似为 Gitee 上的一个私人的名称为 Aps
的项目，其所释放的自行开发或二次开发的文件中，仍然存在部分调试信息。攻击者在开发时采用强链接的方式，将库函数的代码尽可能多的链接到程序中，增加程序的兼容性。

恶意软件开发者的项目路径如下“D:\Work\Code\gitee\APS\ApsBuild\”。同时，该恶意软件还疑似存在未开发完全的远控功能。

![图片](https://image.3001.net/images/20220921/1663743482_632ab5fae497e9b762018.png!small)

 **自8月19日深盾实验室**[ **《**
**揭开新型窃密软件的面纱：伪装成CDR画图应用安装包》**](http://mp.weixin.qq.com/s?__biz=MzI4NjE2NjgxMQ==&mid=2650263502&idx=1&sn=1abe89cf4191901b9101cf4667a86d7a&chksm=f3e275bac495fcacb34f1971f80dbf40166221a66635d484cac8b367521845483b7d0b4506dc&scene=21#wechat_redirect)
**首次披露该病毒，经过一段时间的运营，发现目前已有万余台设备被感染(数据来源于CNCERT)。**

###  **2.恶意文件分析**

恶意软件存在针对安全软件的对抗手段。下图为恶意软件释放、执行的程序——SearchIndexerService.exe
的主函数代码。该段代码的主要功能为，将识别到的安全软件的进程的 TCP 表项清空，断开对应进程的 TCP
连接。此行为的目的为，防止安全软件将恶意样本上传至云端，防止 EDR 与云端联动查杀该恶意软件。

  

![](https://image.3001.net/images/20220921/1663743664_632ab6b0cc73f4c5da5f0.png!small)

在函数 SearchTcpTableForImageName 中，通过 API 获取到 TCP 表的表项后，获取进程的 PID 并利用该 PID
查询进程的名称，将获取到的进程名称存储在 This 指针的结构体中。此循环遍历 TCP 表的所有表项。

![](https://image.3001.net/images/20220921/1663743680_632ab6c0849fdb5e6ca5c.png!small)

获取到的结构体如下图所示，TCPIP_OWNING_MODULE_SIZE 在 32 位操作系统中为 0x10，因此结构体总大小为 0x28。上图的 for
循环中即遍历获取到的每一个结构体。

![](https://image.3001.net/images/20220921/1663743692_632ab6cceb804985f21dc.png!small)

如下图所示，dwState 设置为 0xC 即代表删除对应的 TCP 表项。

![](https://image.3001.net/images/20220921/1663743705_632ab6d987c8eef026947.png!small)

 **一、程序运行流程**

进程启动后，会正常显示安装程序结束后的界面。同时，进程会执行 cmd 命令，结束系统安全服务。

![](https://image.3001.net/images/20220921/1663743720_632ab6e8d1245adbb8017.png!small)

同时，程序开始释放大量的文件，路径分别为：C:\Users\Sangfor\AppData\Roaming\Microsoft\Network、C:\Windows\SysWOW64\security
。其中包含众多有数字签名正常文件，以及用于进行恶意行为的 NetworkService.exe 、SearchIndexerService.exe。

![](https://image.3001.net/images/20220921/1663743744_632ab70040966cb932d80.png!small)

![](https://image.3001.net/images/20220921/1663743756_632ab70cda31f8433e3e4.png!small)

plugin 目录下为病毒要加载的重要 DLL 文件。

DreamApslop.dll 主要功能为搜集主机信息、反调试以及向攻击者服务器发送窃取到的主机信息。

libssl-3.dll 、 libcrypto-3.dll 为通信过程中对数据加密时所需要调用的导出函数的库文件。

mk_api.dll 为开源软件 ZLMediaKit 所提供的导出函数库文件，攻击者基于此开源库再开发，增加了恶意代码模块。

使用释放的 NetworkService.exe 启动进程。

![](https://image.3001.net/images/20220921/1663743770_632ab71a00b171ff8de24.png!small)

 **二、释放的程序的运行流程**

创建互斥量，防止进程重复运行。

![](https://image.3001.net/images/20220921/1663743782_632ab726523edde4de347.png!small)

使用不同的命令行再次启动，第二个参数为当前进程的窗口句柄，用于接收窗口消息，后续将用此接收消息并循环运行：

![](https://image.3001.net/images/20220921/1663743793_632ab731d8cd4ed0e937a.png!small)

如果 Network 目录下不存在 para.ini 文件，则创建一个该名称的配置文件。

![](https://image.3001.net/images/20220921/1663743806_632ab73e88a65caa51437.png!small)

拼接字符串，调用开源软件的导出函数，并第一次发送网络请求给攻击者服务器，此处的 mk_http_requester_call 为攻击者自行编写。

![](https://image.3001.net/images/20220921/1663743817_632ab749de6d404ac225c.png!small)

在此函数执行过程中，将会创建诸多线程，大多数线程为进程的辅助线程或 TPPworker，其中一个特殊的线程会调用 CreateProcess
函数，再次运行一个 NetworkService.exe，参数与本进程相同但传入的 CreationFlags 中含有 Suspend
属性。也就意味着，每次调用该函数都会向攻击者发送搜集的信息。

随后向服务器发送一个网络请求，并将接收到的数据存储到同目录下的 index.ini 文件下。

![](https://image.3001.net/images/20220921/1663743832_632ab7585c05f01c6b8c8.png!small)  
![](https://image.3001.net/images/20220921/1663743848_632ab768a1d7839937758.png!small)  
![](https://image.3001.net/images/20220921/1663743860_632ab774504c321bfb4c4.png!small)

查找 plugin 目录下的文件，并将查找到的文件路径存储在结构体中。

![](https://image.3001.net/images/20220921/1663743882_632ab78a74dec64180699.png!small)  
![](https://image.3001.net/images/20220921/1663743897_632ab7999bd34ef53a690.png!small)  
![](https://image.3001.net/images/20220921/1663743910_632ab7a69354c7ada1c38.png!small)

加载 plugin 目录下所有的 DLL 文件，并尝试调用每一个 DLL 文件的导出函数 Plugin_Create，并调用目标 DLL 的其它导出函数。

![](https://image.3001.net/images/20220921/1663743926_632ab7b646e685048ea22.png!small)

该导出函数会尝试加载四个 DLL
文件，分别为：plugin\\\libcrypto-3.dll、plugin\\\sqlite3.dll、plugin\\\mk_api.dll、plugin\\\libssl-3.dll。

随后获取磁盘序列号，加密并将数据转为 base64
后，发送给目标服务器。![](https://image.3001.net/images/20220921/1663743941_632ab7c596f540b7c6b46.png!small)![](https://image.3001.net/images/20220921/1663743952_632ab7d029664ea5aaf9d.png!small)

服务器返回的数据解码后得到：

![](https://image.3001.net/images/20220921/1663743962_632ab7da281b2a13f33cc.png!small)

同时还搜集如下信息：

1\. 通过 "cmd.exe /c ipconfig /all" 搜集所有的网卡信息。

2\. 通过 "Process32Next"、"GetNativeSystemInfo"获取当前系统运行的所有进程。

![](https://image.3001.net/images/20220921/1663743973_632ab7e5d04f03acaf2e9.png!small)

3\. 通过 "cmd.exe /c whoami" 获取当前登录的用户名称。

4\. 通过 "cmd.exe /c netsh wlan show profiles" 获取无线网卡配置信息。

![](https://image.3001.net/images/20220921/1663743984_632ab7f0b06fed6aca2c3.png!small)

向服务器发送的数据包如下：

![](https://image.3001.net/images/20220921/1663743998_632ab7fe2a1a3b4731828.png!small)

##  **处置建议**

1.避免打开来历不明的邮件、链接和附件等，如一定要打开未知文件，请先使用杀毒软件进行扫描；

2.定期使用杀毒软件进行全盘扫描。

