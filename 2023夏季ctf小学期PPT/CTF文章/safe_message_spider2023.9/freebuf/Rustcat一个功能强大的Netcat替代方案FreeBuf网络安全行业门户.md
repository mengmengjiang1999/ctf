![](https://image.3001.net/images/20210716/1626445339_60f1961b7f6d7c7cdeb06.jpeg!small)

## 关于Rustcat

Rustcat是一款功能强打的端口监听工具，可以帮助广大研究人员在进行安全审计的过程中完成针对特定端口的数据监听。Rustcat的功能跟Netcat类似，但支持的选项要更加精简，可以作为Netcat的替代方案。

## 为什么要选择Rustcat？

> 实现针对特定端口的监听和扫描；
>
> 支持命令历史记录；
>
> 易于使用，方便快捷；
>
> 支持UDP通信；
>
> 使用了不同高亮颜色显示；

## 工具安装

### Debian/Ubuntu

    
    
    wget https://github.com/robiot/rustcat/releases/latest/download/rustcat_amd64.deb
    
    sudo apt install ./rustcat_amd64.deb

### Arch

    
    
    git clone https://aur.archlinux.org/rustcat.git
    
    cd rustcat
    
    makepkg -si

### yay安装

    
    
    yay -S rustcat

### 其他发行版系统

通过creates.io安装：

    
    
    cargo install rustcat

如果你不想自己编译项目代码的话，可以直接从本项目的GitHub库中获取到最新版本的编译版本：

    
    
    bash <(curl -s https://raw.githubusercontent.com/robiot/rustcat/main/install.sh)

如果你想要在Windows系统上使用Rustcat的话，你还需要删除所有跟termion相关的内容。

## 自行编译项目

如果你想要自己动手编译项目源码的话，你首先需要将该项目源码克隆至本地：

    
    
    git clone https://github.com/robiot/rustcat

然后使用cd命令切换至项目目录，并运行下列命令：

    
    
    cargo build --release

## 工具使用

    
    
    rc [options] [destination] [port]

## 工具使用样例

 **查看工具帮助信息：**

    
    
    rc --help

 **监听本地主机（localhost）的55660端口：**

    
    
    rc -lp 55660

 **监听本地主机（localhost）的55660端口（包含命令历史记录）：**

    
    
    rc -lpH 55660

 **监听本地主机（localhost）的55660端口（UDP连接）：**

    
    
    rc -lpu 55660

 **监听指定IP地址（192.168.1.10）的55660端口：**

    
    
    rc -l 192.168.1.10 55660

## 工具运行截图

![](https://image.3001.net/images/20210716/1626445579_60f1970b1fa9a27057529.jpeg!small)

## 项目地址

 **Rustcat：** 【[ _GitHub传送门_](https://github.com/robiot/rustcat)】

