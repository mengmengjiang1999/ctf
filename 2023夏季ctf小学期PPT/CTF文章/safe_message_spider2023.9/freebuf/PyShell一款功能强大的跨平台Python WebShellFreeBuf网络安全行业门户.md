![](https://image.3001.net/images/20220315/1647336672_62305ce0d95de1c022ce6.png!small)

## 关于PyShell

PyShell是一款功能强大的跨平台Python
WebShell，该工具可以帮助广大研究人员在Web服务器上获得一个类似于Shell的界面，并允许进行远程访问。该工具与其他WebShell不同的地方就在于，PyShell的主要目标是在服务器端使用尽可能少的代码来实现目标功能，而不用我们去考虑使用的语言或服务器的操作系统。

基于这种功能特性，我们将能够在Windows和Linux系统上使用各种不同类型和语言的Shell，包括aspx、php、jsp、sh和py等。与此同时，PyShell还提供了完整的命令执行历史记录、文件上传和下载，设置还可以允许我们像使用标准Shell一样进行各种文件系统间的切换。

## 工具要求

首先，该工具基于Python 3开发，因此我们需要在本地设备上安装并配置好Python
3环境。接下来，使用该项目提供的requirements.txt安装该工具所需的依赖组件。

## 工具安装

我们建议广大研究人员直接使用下列命令将该项目源码克隆至本地，或直接下载该项目的【[
_Zip文件_](https://github.com/JoelGMSec/PyShell/archive/refs/heads/main.zip)】：

    
    
    git clone https://github.com/JoelGMSec/PyShell
    
    cd PyShell ; pip install -r requirements.txt

## 工具使用

    
    
    ./PyShell.py -h
    
    
      ██████ ▓██   ░██  ██████  ██░ ██ ▓█████  ██▓     ██▓
    
     ▓██░  ██▒██░   ██▒██    ▒ ▓██  ██▒▓██    ▓██▒    ▓██▒
    
     ▓██░  ██▒ ██  ██░░ ▓███   ▒██████░▒████  ▒██░    ▒██░
    
     ▒██████ ▒ ░████▓░  ▒   ██▒░██ ░██ ▒██    ▒██░    ▒██░
    
     ▒██▒ ░  ░ ░ ██▒▓░▒██████▒▒░██▒░██▓░█████▒░██████▒░██████▒
    
     ▒██░ ░  ░  ██▒▒▒ ▒ ▒▓▒ ▒ ░ ▒ ░░▒░▒░░ ▒░ ░░ ▒░▓  ░░ ▒░▓  ░
    
     ░▒ ░     ▓██ ░▒░ ░ ░▒    ░ ▒ ░ ░ ░ ░ ░  ░░ ░ ▒  ░░ ░ ▒  ░
    
     ░░   ░   ▒ ▒ ░░  ░  ░  ░   ░  ░░ ░         ░ ░     ░ ░
    
     ░        ░             ░      ░      ░       ░          ░
    
     
    
      -------------- by @JoelGMSec & @3v4Si0N ---------------    
     
    
    usage: pyshell.py [-h] [-a AUTH] [-c COOKIES] [-p PARAM] [-pi] [-su] [-ps] url method
    
     
    
    positional arguments:
    
      url                   Webshell的URL地址
    
      method              执行命令所使用的HTTP方法 (GET或POST)
    
     
    
    optional arguments:
    
      -h, --help                显示帮助信息和退出
    
      -a AUTH, --auth AUTH    在每一次请求发送时所使用的认证Header
    
      -c COOKIES, --cookies COOKIES
    
                              在每一次请求发送时所使用的Cookie Header
    
      -p PARAM, --param PARAM
    
                             自定义WebShell所使用的参数
    
      -pi, --pipe              传递参数后所有的命令
    
      -su, --sudo             Sudo命令执行（仅适用Linux主机）
    
      -ps, --PowerShell       PowerShell命令执行（仅适用Windows主机）

## 工具使用样例

在项目的Shells文件夹中，我们可以找到各种不同类型的WebShell。比如说，我们可以启动一个PHP服务器并使用GET请求与服务器交互：

![](https://image.3001.net/images/20220315/1647336715_62305d0b6fd8cdf9b5a8e.png!small)

非常简单，我们只需要上传WebShell的地址和想要使用的连接方法即可（GET或POST）。

我们还可以使用文件上传功能：

![](https://image.3001.net/images/20220315/1647336722_62305d129fa1dfdafc1a2.png!small)

或者下载文件：

![](https://image.3001.net/images/20220315/1647336729_62305d19aea15795a163f.png!small)

更多的工具使用方法，请参考这篇【[ _文档_](https://darkbyte.net/pyshell-multiplatform-python-webshell/)】。

## 许可证协议

本项目的开发与发布遵循GNU v3.0开源许可证协议。

## 项目地址

 **PyShell：** 【[ _GitHub传送门_](https://github.com/JoelGMSec/PyShell)】

## 参考资料

> [ _https://darkbyte.net/pyshell-multiplatform-python-> webshell_](https://darkbyte.net/pyshell-multiplatform-python-webshell)

