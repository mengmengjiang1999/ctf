![](https://image.3001.net/images/20201114/1605283365_5faeae25956ae8aacf440.jpg!small)

## Croc

Croc是一款安全性极强的点对点数据传输工具，该工具允许两台计算机设备以一种简单和安全的方式来传输文件或文件夹。简而言之，Croc是一款命令行接口工具，在Croc的帮助下，广大研究人员可以通过命令行工具来实现文件传输。

## 工具特性

  * 该工具允许任意两台计算机设备直接进行数据传输；
  * 提供了端到端加密支持（PAKE）；
  * 支持跨平台传输（Windows、Linux和macOS）；
  * 支持多文件传输；
  * 允许断线后的文件续传；
  * 不需要本地服务器或端口转发；
  * 支持IPv6和IPv4；
  * 支持使用Tor之类的代理；

## 工具安装

首先，我们需要将最新版本的[
_Croc_](https://github.com/schollz/croc/releases/latest)下载到我们的电脑中，或者直接使用下列命令进行在线安装：

    
    
    $ curl https://getcroc.schollz.com | bash

在macOS平台上，我们可以直接使用[ _Homebrew_](https://brew.sh/)来安装最新版本的Croc：

    
    
    $ brew install croc

在macOS平台上，我们还可以使用[ _MacPorts_](https://macports.org/)来安装最新版本的Croc：

    
    
    $ sudo port selfupdate
    
    $ sudo port install croc

在Windows平台上，我们可以使用[ _Scoop_](https://scoop.sh/)或[
_Chocolatey_](https://chocolatey.org/)来安装最新版本的Croc：

    
    
    $ scoop install croc

或

    
    
    $ choco install croc

在Unix平台上，我们可以使用[ _Nix_](https://nixos.org/nix)来安装最新版本的Croc：

    
    
    $ nix-env -i croc

在Arch Linux平台上，我们可以使用pacman来安装最新版本的Croc：

    
    
    $ pacman -S croc

在Ubuntu平台上，我们可以使用snap来安装最新版本的Croc：

    
    
    $ snap install croc

在Gentoo平台上，我们可以使用portage来安装最新版本的Croc：

    
    
    $ emerge net-misc/croc

在Termux平台上，我们可以使用pkg来安装最新版本的Croc：

    
    
    $ pkg install croc

在FreeBSD平台上，我们可以使用pkg来安装最新版本的Croc：

    
    
    $ pkg install croc

或者说，我们可以在计算机上安装好[ _Go环境_](https://golang.org/dl/)（Go v1.12+），然后通过源码构建工具：

    
    
    $ GO111MODULE=on go get -v github.com/schollz/croc/v8

## 工具使用

如需发送文件，可以直接运行下列命令：

    
    
    $ croc send [file(s)-or-folder]
    
    Sending 'file-or-folder' (X MB)
    
    Code is: code-phrase

接下来，在另一台电脑上使用下列命令来进行文件或目录接收：

    
    
    $ croc code-phrase

这里的code-phrase即密码短语，用于建立密码认证密钥协议（PAKE），该协议将生成一个密钥供发送方和接收方用于端到端加密。

## 自定义密码短语

我们可以使用下列方式来配置自己的密码短语，必须是4个字符以上：

    
    
    $ croc send --code [code-phrase] [file(s)-or-folder]

## 使用管道-stdin和stdout

我们可以通过管道来向Croc传递文件：

    
    
    $ cat [filename] | croc send

此时，Croc将会自动使用stdin数据，并发送和分配一个类似“croc-stdin-123456789”的文件名。如需接收stdout，可以直接使用--yes选项来自动接收文件：

    
    
    $ croc --yes [code-phrase] > out

## 发送文字消息

有些时候，我们可能只需要发送URL地址或简短的文字消息，此时可以通过下列命令实现发送：

    
    
    $ croc send --text "hello world"

## 使用代理

我们还可以使用代理链接来进行传输中继，比如说，我们可以使用下列命令来将Tor作为代理中继：

    
    
    $ croc --socks5 "127.0.0.1:9050" send SOMEFILE

## 工具使用样例

![](https://image.3001.net/images/20201114/1605283559_5faeaee7552857e9096d9.gif)

## 许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

Croc：【[ _GitHub传送门_](https://github.com/schollz/croc)】

  

