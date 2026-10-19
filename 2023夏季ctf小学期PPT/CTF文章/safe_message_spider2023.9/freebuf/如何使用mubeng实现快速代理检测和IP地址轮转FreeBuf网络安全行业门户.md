![](https://image.3001.net/images/20210519/1621405986_60a4b122a657960fa4c12.png!small)

## 关于mubeng

mubeng是一款功能强大的代理检查和IP地址轮转工具。该工具具备以下几种功能特性：

> 代理IP轮换：在每次发送请求之后变更你的IP地址。
>
> 代理检测：检测你的代理IP是否仍然可用。
>
> 支持所有的HTTP/S方法。
>
> 支持传递所有的参数和URI。
>
> 支持HTTP&Socksv5代理协议。
>
> 易于使用：你可以直接使用自己的代理文件来配置和运行mubeng，并选择需要执行的操作。
>
> 跨平台特性：无论你使用的是Windows、Linux、macOS或是树莓派，你都可以正常使用mubeng。

## 工具安装

### 预编译源码安装

广大研究人员可以直接访问该项目的【[
_Releases页面_](https://github.com/kitabisa/mubeng/releases)】来获取预编译好的项目代码，下载之后即可直接运行。

### Docker安装

直接运行下列命令即可将mubeng的[ _Docker镜像_](https://docs.docker.com/get-docker/)拉取到本地：

    
    
    ▶ docker pull kitabisa/mubeng

### 源码安装

这里需要使用Go编译器（[ _v1.15+_](https://golang.org/doc/install)）：

    
    
    ▶ GO111MODULE=on go get -u ktbs.dev/mubeng/cmd/mubeng

注意：上述命令也适用于工具更新。

或者，你也可以使用下列命令将源代码手动构建为可执行程序：

    
    
    ▶ git clone https://github.com/kitabisa/mubeng
    
    ▶ cd mubeng
    
    ▶ make build
    
    ▶ (sudo) mv ./bin/mubeng /usr/local/bin
    
    ▶ make clean

## 工具使用

该工具要求我们提供自己的代理列表，可以是需要检测的代理，或是用于代理IP轮转的代理地址池：

    
    
    ▶ mubeng [-c|-a :8080] -f file.txt [options...]

### 工具选项

下面给出的是该工具所有支持的选项参数：

    
    
    ▶ mubeng -h

 ** **参数选项****

|

 ** **描述****  
  
---|---  
  
-f, --file <FILE>

|

代理文件  
  
-a, --address <ADDR>:<PORT>

|

运行代理服务器  
  
-d, --daemon

|

代理服务器守护程序  
  
-c, --check

|

执行代理状态检测  
  
-t, --timeout

|

代理服务器检测最大超时（默认为30s）  
  
-r, --rotate <AFTER>

|

每次请求后轮转代理IP地址（默认为1）  
  
-v, --verbose

|

导出HTTP请求/响应，或显示无响应的代理服务器  
  
-o, --output

|

日志输出  
  
-u, --update

|

更新mubeng 至最新稳定版本  
  
-V, --version

|

显示当前mubeng版本  
  
## 工具使用样例

比如说，你有一个如下所示的代理列表：

    
    
    http://127.0.0.1:8080
    
    https://127.0.0.1:3128
    
    socks5://127.0.0.1:2121
    
    ...
    
    ...

### 代理检测

你可以在命令中传递--check选项来执行代理检测：

    
    
    ▶ mubeng -f proxies.txt --check --output live.txt

上述命令中还是用了--output选项来将可用代理存储至live.txt文件中：

![](https://image.3001.net/images/20210519/1621406036_60a4b154af6188e30f2e5.png!small)

### 代理IP轮转

如果你想轮转代理服务器IP地址的话，可以直接从live.txt中获取可用代理，此时你必须使用-a选项来运行代理服务器：

    
    
    ▶ mubeng -a localhost:8089 -f live.txt -r 10

![](https://image.3001.net/images/20210519/1621406047_60a4b15f7d14630cd0716.jpg!small)

### BurpSuite代理

如果你想将mubeng作为BurpSuite中的上游代理使用的话，仅需按下图配置即可：

![](https://image.3001.net/images/20210519/1621406057_60a4b169b6accea6f7e0e.jpg!small)

## 项目地址

mubeng：【[ _GitHub传送门_](https://github.com/kitabisa/mubeng)】

## 许可证协议

本项目的开发与发布遵循[
_Apache_](https://github.com/kitabisa/mubeng/blob/master/LICENSE)开源许可证协议。

## 参考资料

[ _https://golang.org/doc/install_](https://golang.org/doc/install)

[
_https://pkg.go.dev/ktbs.dev/mubeng/pkg/mubeng#Transport_](https://pkg.go.dev/ktbs.dev/mubeng/pkg/mubeng#Transport)

[ _https://portswigger.net/burp/documentation/desktop/getting-started/installing-burp_](https://portswigger.net/burp/documentation/desktop/getting-started/installing-burp)

[ _https://www.zaproxy.org/download/_](https://www.zaproxy.org/download/)

[
_https://github.com/kitabisa/mubeng/blob/master/.github/CONTRIBUTING.md﻿_](https://github.com/kitabisa/mubeng/blob/master/.github/CONTRIBUTING.md)

