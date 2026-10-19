## Sniffglue

**Sniffglue是一款使用Rust开发的网络嗅探工具，该工具使用了线程池来利用所有的CPU核心并对多个网络数据包同时进行解析处理。该工具的主要目标就是帮助研究人员在不受信任的网络中安全稳定地对数据包进行处理，而不会遇到其他异常问题。默认配置下，该工具的输出结果已经足以满足大部分用户的需求了。**

![1.png](https://image.3001.net/images/20190702/1562066000_5d1b3c501de93.png!small)

## 工具使用

    
    
    sniffglue enp0s25

## 工具安装

本工具针对ArchLinux提供了一个官方数据包，可使用下列命令直接获取：

    
    
    pacman -S sniffglue

如果大家想通过源码构建项目，请确保你的设备安装了libpcap和libseccomp。

### Debian/Ubuntu：

    
    
    libpcap-dev libseccomp-dev

### Archlinux：

    
    
    libpcap libseccomp

安装命令如下：

    
    
    cargo install sniffglue

当然了，安装完成之后，别忘了安装构建依赖组件：

    
    
    ci/reprotest.sh

### 支持的协议

![2.png](https://image.3001.net/images/20190702/1562066042_5d1b3c7a883f6.png!small)

## Docker安装

你还可以将Sniffglue以Docker镜像的方式进行安装和使用，镜像大小约为11.1MB。我们强烈建议大家将其配置进注册表中：

    
    
    docker build -t sniffglue .
    
    docker run -it --init --rm --net=host sniffglue eth0  
    

## Seccomp

为了确保被入侵的进程不会影响目标系统，Sniffglue使用了seccomp来限制目标进程的系统调用。整个过程分为两个阶段，首先是在开始的时候，也就是在env_logger初始化完成之后，然后就是在嗅探器配置完成之后，也就是在Sniffglue从网络中读取出数据包之前。

在第二个阶段中，工具还采用了一些增强型安全配置，以确保过滤/禁用掉不需要的系统调用。如果需要针对某些特殊系统进行数据包嗅探，我们还可以直接从etc/sniffglue.conf中读取配置信息。这个配置文件为chroot指定了一个空目录和一个非特权账号，而该工具可以利用这个非特权账号来提升至root权限。

### boxxy-rs

本工具使用了基于boxxy-rs的基础Shell，可用来探测目标系统中的沙盒环境：

    
    
    cargo run --example boxy

### 模糊测试

Sniffglue还可以在数据包处理的过程中使用cargo-fuzz来进行模糊测试，在这个过程中，我们需要用到的东西开发人员都已经在项目目录的fuzz/文件夹中给大家提供了相应的源代码：

    
    
    cargo fuzz run read_packet

## 许可证协议

本项目的开发遵循GPL v3开源许可证协议。

## 项目地址

Sniffglue：【[GitHub传送门](https://github.com/kpcyrd/sniffglue)】

***参考来源：[kpcyrd](https://github.com/kpcyrd/sniffglue)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

