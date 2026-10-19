## **恶意文件概述**

新型窃密软件伪装成一款图形编辑软件，运行后持续窃取用户信息，并发送给攻击者服务器。

##  **恶意文件分析**

###  **1.恶意文件描述**

近期，深信服深盾终端实验室在运营工作中捕获到一款功能复杂的新型信息窃取软件， **该病毒由 C++ 语言编写，套用了开源软件 ZLMediaKit
的部分代码并在其基础上开发恶意模块。该程序的释放的文件包含具有数字签名的正常的库文件，以及没有数字签名但伪装成正常系统文件的 exe 程序。**

该软件疑似为 Gitee 上的一个私人的名称为 Aps
的项目，其所释放的自行开发或二次开发的文件中，仍然存在部分调试信息。攻击者在开发时采用强链接的方式，将库函数的代码尽可能多的链接到程序中，增加程序的兼容性。

###  **2.恶意文件分析**

 **一、程序运行流程**

进程启动后，会正常显示安装程序结束后的界面。同时，进程会执行 cmd 命令，结束系统安全服务。

![](https://image.3001.net/images/20220823/1661223795_6304437373eda8e1afa7f.png!small)

同时，程序开始释放大量的文件，路径分别为：C:\Users\Sangfor\AppData\Roaming\Microsoft\Network、C:\Windows\SysWOW64\security。其中包含众多有数字签名正常文件，以及用于进行恶意行为的
NetworkService.exe 、SearchIndexerService.exe 。

![](https://image.3001.net/images/20220823/1661223812_6304438499441357e42fc.png!small)![](https://image.3001.net/images/20220823/1661223822_6304438eb09f1f6b5298c.png!small)

plugin 目录下为病毒要加载的重要 DLL 文件。

DreamApslop.dll 主要功能为搜集主机信息、反调试以及向攻击者服务器发送窃取到的主机信息。

libssl-3.dll 、 libcrypto-3.dll 为通信过程中对数据加密时所需要调用的导出函数的库文件。

mk_api.dll 为开源软件 ZLMediaKit 所提供的导出函数库文件，攻击者基于此开源库再开发，增加了恶意代码模块。

使用释放的NetworkService.exe 启动进程。

![](https://image.3001.net/images/20220823/1661223847_630443a74849e4725ae1c.png!small)

 **二、释放的程序的运行流程**

创建互斥量，防止进程重复运行。

![](https://image.3001.net/images/20220823/1661223868_630443bc274125605876c.png!small)

使用不同的命令行再次启动，第二个参数为当前进程的窗口句柄，用于接收窗口消息，后续将用此接收消息并循环运行：

![](https://image.3001.net/images/20220823/1661223884_630443cc4eedca2e3ae2e.png!small)

如果 Network 目录下不存在 para.ini 文件，则创建一个该名称的配置文件。

![](https://image.3001.net/images/20220823/1661223894_630443d683201b7aafc57.png!small)

拼接字符串，调用开源软件的导出函数，并第一次发送网络请求给攻击者服务器，此处的 mk_http_requester_call为攻击者自行编写。

![](https://image.3001.net/images/20220823/1661223908_630443e41024ffd9657cf.png!small)

在此函数执行过程中，将会创建诸多线程，大多数线程为进程的辅助线程或 TPPworker，其中一个特殊的线程会调 CreateProcess
函数，再次运行一个 NetworkService.exe，参数与本进程相同但传入的CreationFlags 中含有 Suspend
属性。也就意味着，每次调用该函数都会向攻击者发送搜集的信息。

随后向服务器发送一个网络请求，并将接收到的数据存储到同目录下的 index.ini 文件下。

![](https://image.3001.net/images/20220823/1661223940_63044404d6e31bf25f1dc.png!small)

![](https://image.3001.net/images/20220823/1661223952_630444102b7bc540252f7.png!small)  
![](https://image.3001.net/images/20220823/1661223962_6304441a0119bd1cdcc1c.png!small)

查找 plugin 目录下的文件，并将查找到的文件路径存储在结构体中。

![](https://image.3001.net/images/20220823/1661223978_6304442adb115c9a81e52.png!small)

  

![](https://image.3001.net/images/20220823/1661223997_6304443dd313f141b38b3.png!small)

加载 plugin 目录下所有的 DLL 文件，并尝试调用每一个DLL 文件的导出函数 Plugin_Create，并调用目标 DLL 的其它导出函数。

![](https://image.3001.net/images/20220823/1661224011_6304444ba8f8bd1061e94.png!small)该导出函数会尝试加载四个
DLL
文件，分别为：plugin\\\libcrypto-3.dll、plugin\\\sqlite3.dll、plugin\\\mk_api.dll、plugin\\\libssl-3.dll。

随后获取磁盘序列号，加密并将数据转为 base64 后，发送给目标服务器。

![](https://image.3001.net/images/20220823/1661224021_63044455b3d975221962d.png!small)

![](https://image.3001.net/images/20220823/1661224037_630444652cd9b0cc5dc2c.png!small)服务器返回的数据解码后得到：

![](https://image.3001.net/images/20220823/1661224047_6304446f17bc903d6b807.png!small)

同时还搜集如下信息：

1\. 通过 "cmd.exe /c ipconfig /all" 搜集所有的网卡信息。

2\. 通过 "Process32Next"、"GetNativeSystemInfo" 获取当前系统运行的所有进程。

![](https://image.3001.net/images/20220823/1661224058_6304447ab04d09cd17f91.png!small)

3\. 通过 "cmd.exe /c whoami" 获取当前登录的用户名称。

4\. 通过 "cmd.exe /c netsh wlan show profiles" 获取无线网卡配置信息。

![](https://image.3001.net/images/20220823/1661224070_63044486a8cda9d88e979.png!small)

向服务器发送的数据包如下：

![](https://image.3001.net/images/20220823/1661224107_630444ab6caa43fdf64ec.png!small)

