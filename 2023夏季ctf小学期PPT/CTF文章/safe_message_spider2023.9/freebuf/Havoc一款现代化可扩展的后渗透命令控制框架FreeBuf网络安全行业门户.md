![](https://image.3001.net/images/20221227/1672145252_63aae9641ce35776dc4e4.png!small)

## 关于Havoc

Havoc是一款现代化的、可扩展的后渗透命令控制框架。

Havoc已经在Debian 10/11、Ubuntu 20.04/22/04以及Kali
Linux操作系统上进行过完整测试。我们建议大家使用最新版本的Havoc以避免遇到其他问题。除此之外，建议使用最新版本的Qt和Python
3.10.x来完成代码构建。

注意：当前的Havoc版本还处于早期开发版，随着框架的不断成熟，可能会对Havoc的API和核心结构进行大量更改。

![](https://image.3001.net/images/20221227/1672145263_63aae96f2c02550eff90d.png!small)

![](https://image.3001.net/images/20221227/1672145272_63aae9789c16e13f76131.png!small)

## 功能介绍

### 客户端

Havoc的客户端拥有跨平台UI，使用C++和Qt开发，现代深色主题基于[ _Dracula_](https://draculatheme.com/)实现。

### Teamserver

Havoc的Teamserver基于Golang开发，包含下列功能：

> 1、多用户支持；
>
> 2、Payload生成（exe/shellcode/dll）；
>
> 3、HTTP/HTTPS监听器；
>
> 4、自定义C2；
>
> 5、外部C2；

### 守护进程

Havoc的客户端基于C和ASM开发，包含下列功能：

> 1、通过[ _Ekko_](https://github.com/Cracked5pider/Ekko)或[
> _FOLIAGE_](https://github.com/SecIdiot/FOLIAGE)实现休眠混淆；
>
> 2、x64返回地址欺骗；
>
> 3、Nt* API间接系统调用；
>
> 4、SMB支持；
>
> 5、令牌存储；
>
> 6、各种内置的后渗透命令；

![](https://image.3001.net/images/20221227/1672145292_63aae98ccb1c2043acea7.png!small)

### 可扩展性

> 1、外部C2；
>
> 2、自定义代理支持：Talon；
>
> 3、Python API；
>
> 4、模块化；

## 工具安装

### 本地安装

依赖组件：

    
    
    sudo apt install -y git build-essential apt-utils cmake libfontconfig1 libglu1-mesa-dev libgtest-dev libspdlog-dev libboost-all-dev libncurses5-dev libgdbm-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev mesa-common-dev qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools libqt5websockets5 libqt5websockets5-dev qtdeclarative5-dev golang-go qtbase5-dev libqt5websockets5-dev libspdlog-dev python3-dev libboost-all-dev mingw-w64 nasm

Ubuntu 20.04：

    
    
    sudo apt install build-essential
    
    sudo add-apt-repository ppa:deadsnakes/ppa
    
    sudo apt update
    
    sudo apt install python3.10 python3.10-dev

Debian 10/11：

    
    
    echo 'deb http://ftp.de.debian.org/debian bookworm main' >> /etc/apt/sources.list
    
    sudo apt update
    
    sudo apt install python3-dev python3.10-dev libpython3.10 libpython3.10-dev python3.10

macOS：

    
    
    brew install --cask cmake
    
    brew install python@3.10 qt@5 spdlog golang
    
    brew link --overwrite qt@5

### 客户端构建

项目克隆：

    
    
    git clone https://github.com/HavocFramework/Havoc.git

构建和运行：

    
    
    cd Havoc/Client
    
    make
    
    ./Havoc

### Teamserever构建

安装额外的Go依赖：

    
    
    cd Havoc/Teamserver
    
     
    
    go mod download golang.org/x/sys  
    
    go mod download github.com/ugorji/go

构建和运行：

    
    
    cd Teamserver
    
     
    
    # Install MUSL C Compiler
    
    ./Install.sh
    
     
    
    # Build Binary
    
    make
    
    ./teamserver -h
    
     
    
    # Run the teamserver
    
    sudo ./teamserver server --profile ./profiles/havoc.yaotl -v --debug

## 工具使用

### 客户端

    
    
    cd Havoc/Client
    
    ./Havoc

### Teamserver连接

![](https://image.3001.net/images/20221227/1672145366_63aae9d6593131e77a9cf.png!small)

![](https://image.3001.net/images/20221227/1672145374_63aae9ded0aefd5c8e1a8.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/HavocFramework/Havoc/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Havoc** ：【[ _GitHub传送门_](https://github.com/HavocFramework/Havoc)】

## 参考资料

> [ _https://www.patreon.com/5pider_](https://www.patreon.com/5pider)
>
> [
> _https://github.com/sponsors/Cracked5pider_](https://github.com/sponsors/Cracked5pider)
>
> [ _https://draculatheme.com/_](https://draculatheme.com/)
>
> [
> _https://github.com/Cracked5pider/Ekko_](https://github.com/Cracked5pider/Ekko)
>
> [
> _https://github.com/SecIdiot/FOLIAGE_](https://github.com/SecIdiot/FOLIAGE)
>
> [ _https://discord.gg/z3PF3NRDE5_](https://discord.gg/z3PF3NRDE5)

