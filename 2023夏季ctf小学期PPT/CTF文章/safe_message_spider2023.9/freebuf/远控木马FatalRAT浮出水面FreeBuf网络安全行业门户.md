近期，AT&T 的研究人员发现了一种新的远控木马正在通过论坛和 Telegram 进行分发，该恶意软件隐藏在下载链接中，透过软件或者新闻来引诱用户下载。

## 分析

FatalRAT
是一种远控木马，在完全感染系统之前会运行多次测试（[T1497.001](https://attack.mitre.org/techniques/T1497/001/)），检查是否存在虚拟机中、检查硬盘空间大小、检查物理处理器数量等。

![](https://image.3001.net/images/20210826/1629957933_61272f2dbf9d957d7cae5.jpg!small)

检测虚拟机服务是否存在：

![](https://image.3001.net/images/20210826/1629957937_61272f318afc16bfbf48c.jpg!small)

检测特定注册表是否存在：

![](https://image.3001.net/images/20210826/1629957940_61272f345596cdd682502.jpg!small)

如果通过了虚拟机检测，FatalRAT 就会开始进行恶意活动。首先，解密配置字符串，得到 C&C 地址、恶意软件文件名、服务名和其他设置。

![](https://image.3001.net/images/20210826/1629957942_61272f367fe43cf7a8963.jpg!small)

解密字符串的方式如下所示：

![](https://image.3001.net/images/20210826/1629957945_61272f39f00f3612939d6.jpg!small)

FatalRAT 通过修改注册表禁用 CTRL+ALT+DELETE 锁定计算机：

![](https://image.3001.net/images/20210826/1629957948_61272f3c4d89e859f4ed4.jpg!small)

随后激活 Keylogger：

![](https://image.3001.net/images/20210826/1629957950_61272f3e6b9809f54f089.jpg!small)

FatalRAT
修改注册表（Software\Microsoft\Windows\CurrentVersion\Run\SVP7）并创建新服务来进行持久化：

![](https://image.3001.net/images/20210826/1629957952_61272f40d46272af1e5c6.jpg!small)

恶意软件收集失陷主机的信息并发送到 C&C 服务器，包括公网 IP 地址、用户名和受害者的其他信息。

![](https://image.3001.net/images/20210826/1629957955_61272f430eb8a3960cfe8.jpg!small)

作为一种检测逃避技术，FatalRAT 通过遍历所有正在运行的进程是否存在安全产品：

![](https://image.3001.net/images/20210826/1629957957_61272f456cbfda93441e9.jpg!small)

进程名称会被转换为安全产品名称发送到 C&C 服务器：

![](https://image.3001.net/images/20210826/1629957961_61272f490acac9d42e85b.jpg!small)

C&C 通信的加密方式（异或加常数值）如下所示：

![](https://image.3001.net/images/20210826/1629957963_61272f4b80d4817f08925.jpg!small)

加密信息会通过 8081 端口发送到 C&C 服务器：

![](https://image.3001.net/images/20210826/1629957965_61272f4da8b2964f7b2f7.jpg!small)

攻击会下发执行的命令，例如删除特定浏览器（Edge、360Secure Browser、QQBrowser、SogouBrowser 和 Firefox）。

![](https://image.3001.net/images/20210826/1629957968_61272f5036b8ddf1b1ecc.jpg!small)

执行的命令如通过 IPC$ 进行爆破，进行横向移动。

![](https://image.3001.net/images/20210826/1629957971_61272f5338d887645b250.jpg!small)

攻击成功后会在指定位置（%Folder%\hackshen.exe）拷贝传播：

![](https://image.3001.net/images/20210826/1629957973_61272f55e26405b334084.jpg!small)

窃取软件相关数据：

![](https://image.3001.net/images/20210826/1629957976_61272f587b67df5b39f5a.jpg!small)

其他命令包括卸载 UltraViewer、下载并安装 AnyDesk、下载并执行文件等：

![](https://image.3001.net/images/20210826/1629957979_61272f5b02b15af31b9cc.jpg!small)

## 结论

新发现的 FatalRAT 使用多种方式进行检测逃避，窃取用户相关隐私数据，通信也做了加密处理。在过去的几个月里，活动较为频繁。

## IOC

> e52af19dce25d51f9cf258613988b8edc583f7c7e134d3e1b834d9aab9c7c4c4  
> dc026cd76891d1f84f44f6789ac0145a458e2c704a7bc50590ec08966578edb3  
> cb450f82c49eadd597a87645f9f30c52c03c6ed9425386af5b321664fe3a6da0  
> 210990e36122e0facc7c74373569f052fa0651ab06644330fe00b685793ee0fd  
> 34f37327a0154d644854a723e0557c733931e2366a19bdb4cfe6f6ae6770c50f  
> ec0dcfe2d8380a4bafadb3ed73b546cbf73ef78f893e32202042a5818b67ce56  
> b01719e59675236df1a0e1a78cdd97455c0cf18426c7ec0f52df1f3a78209f65  
> 72cd668d9bc442f522556807390d4f7e32966bef20ef1a831bf36a5ab213191e  
> 1cabdb7ab1cbd0526498d15839c780850a41a8c917b65581fad9e7dbdedd5e0f  
> 5453911d6f597d65ab542ec25723a7d87b2292c2e2a52a40d3a32032f6117acd  
> 826d07108a1223140e6a58b44722404009ac2e82df0acfd7d1f5bf29b56526b6  
> 337841b5ade52ba853a30eb8ab04dede64d89808893fb6e04122479502951528  
> 17075832426b085743c2ba811690b525cf8d486da127edc030f28bb3e10e0734  
> 103.119.44.152  
> 103.119.44.93  
> 103.119.44.100

## 参考来源

> [AT&T CyberSecurity](https://cybersecurity.att.com/blogs/labs-research/new-> sophisticated-rat-in-town-fatalrat-analysis)

