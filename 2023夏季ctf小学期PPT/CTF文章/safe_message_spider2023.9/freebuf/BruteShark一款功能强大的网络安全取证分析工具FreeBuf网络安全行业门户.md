![](https://image.3001.net/images/20220315/1647351849_62309829a9dd917a46fb9.png!small)

## 关于BruteShark

BruteShark是一款功能强大的网络安全取证分析工具（NFAT），在该工具的帮助下，广大研究人员可以轻松地对网络流量（主要是PCAP文件，但也可以从网络接口直接实时捕捉流量）进行深度处理和审查。该工具的功能主要包括密码提取、网络映射构建、TCP回话重建和提取加密密码的哈希等，该工具设置还可以将提取出的加密密码哈希转换为Hashcat格式来执行暴力破解测试。

该工具的主要目标是为负责网络流量分析的安全研究人员和网络管理员提供安全解决方案，同时也可以识别出潜在的网络安全薄弱点。

目前，BruteShark提供了两个可用版本，即一个基于GUI的应用程序（Windows）和一个命令行工具（Windows和Linux）。

除此之外，该项目所提供的解决方案中，有很多项目和组件都可以单独用作分析Linux或Windows网络流量的基础设施。

## 功能介绍

> 1、提取和编码用户名和密码（HTTP、FTP、Telnet、IMAP、SMTP等）；
>
> 2、提取身份验证哈希并使用Hashcat（Kerberos、NTLM、CRAM-MD5、HTTP摘要…）进行破解；
>
> 3、构建可视化网络结构图（包含网络节点、开放端口、域用户等）；
>
> 4、提取DNS查询；
>
> 5、重构所有的TCP & UDP会话；
>
> 6、文件分割；
>
> 7、提取VoIP通话（SIP、RTP）；

## 工具下载

### Windows

首先，我们需要下载并安装下列依赖组件：

> 1、Npcap驱动程序（安装好最新版本的[
> _Wireshark_](https://www.wireshark.org/download.html)后将默认安装好Npcap）；
>
> 2、[ _.NET Core
> Runtime_](https://dotnet.microsoft.com/download/dotnet/3.1/runtime)

桌面版本：[ _BruteSharkDesktop Windows_ _安装包_ _（64
Bit）_](https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkDesktopInstaller_x64.msi)

命令行工具版本：[ _BruteSharkCli Windows 10_
_可执行程序_](https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli.exe)

### Linux

首先，我们需要下载并安装下列依赖组件：

> 1、libpcap驱动程序

接下来，使用下列命令下载BruteSharkCli：

    
    
    wget https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli
    
    ./BruteSharkCli

## 工具使用

BruteSharkDesktop桌面端的使用就比较简单了，大家按照图示界面操作即可。我们主要介绍BruteSharkCli命令行工具的使用。

 **打印帮助菜单：**

    
    
    BruteSharkCli --help

 **从目录中的全部文件获取凭证数据，密码和哈希将会打印至stdout：**

    
    
    BruteSharkCli -m Credentials -d "C:\Users\King\Desktop\Pcap Files"

 **从目录中的全部文件获取凭证数据，并导出提取到的哈希至Hashcat输入文件中：**

    
    
    BruteSharkCli -m Credentials,NetworkMap,FileExtracting -d C:\Users\King\Desktop\Pcap_Examples -o C:\Users\King\Desktop\Results

 **对目录中的全部文件运行多个功能模块，并导出所有结果：**

    
    
    BruteSharkCli -m Credentials,NetworkMap,FileExtracting -d C:\Users\King\Desktop\Pcap_Examples -o C:\Users\King\Desktop\Results

 **嗅探一个名为“Wi-Fi”的接口，运行多个模块，然后将所有结果导出至一个目录（按下CTRL** \+ **C键停止嗅探后，才会生成导出结果）：**

    
    
    BruteSharkCli -l Wi-Fi -m Credentials,NetworkMap,FileExtracting,DNS -o C:\Users\King\Desktop\Test Export

## 工具运行截图

### 哈希提取

![](https://image.3001.net/images/20220315/1647351992_623098b8065fee1abe96f.png!small)

### 构建网络结构图

![](https://image.3001.net/images/20220315/1647352000_623098c01ffa319f7e254.png!small)

![](https://image.3001.net/images/20220315/1647352009_623098c9596c56bba05fc.png!small)![](https://image.3001.net/images/20220315/1647352026_623098da3984667a6554b.gif)

  

### 文件分割

![](https://image.3001.net/images/20220315/1647352066_623099021188443559460.png!small)

### 密码提取

![](https://image.3001.net/images/20220315/1647352079_6230990fb4070c0af62f9.png!small)

### 重构所有TCP会话

![](https://image.3001.net/images/20220315/1647352087_62309917759bd7ac64a43.png!small)

### 提取VoIP通话

![](https://image.3001.net/images/20220315/1647352096_62309920c95c255782cf0.png!small)

## 工具演示视频

 **构建一个网络映射：** 【[ _点我观看_](https://user-images.githubusercontent.com/18364847/131922221-5714f351-85f7-4490-bec9-8da4339b66b3.mp4)】

 **BruteSharkCli使用样例-提取多个密码和哈希：** 【[ _点我观看_](https://user-images.githubusercontent.com/18364847/131924013-8b2aa18b-0941-456e-a09d-799902554166.mp4)】

## 项目地址

 **BruteShark：** 【[ _GitHub传送门_](https://github.com/odedshimon/BruteShark/)】

## 参考资料

> [
> _https://www.wireshark.org/download.html_](https://www.wireshark.org/download.html)
>
> [
> _https://dotnet.microsoft.com/download/dotnet/3.1/runtime_](https://dotnet.microsoft.com/download/dotnet/3.1/runtime)
>
> [
> _https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkDesktopInstaller_x64.msi_](https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkDesktopInstaller_x64.msi)
>
> [
> _https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli.exe_](https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli.exe)
>
> [
> _https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli_](https://github.com/odedshimon/BruteShark/releases/latest/download/BruteSharkCli)

