![](https://image.3001.net/images/20221024/1666620917_63569df568fc9a07b9e12.png!small)

## 关于usbsas

usbsas是一款功能强大的开源（GPLv3）工具&框架，该工具可以帮助广大用户以安全的方式读取不受信任的USB大容量存储设备。

该工具的实现遵循深度防御的概念和最小特权原则，usbsas的目标是减少USB堆栈的攻击面。为了实现这一点，通常在（特权）内核空间中执行的大多数与USB相关的任务（解析USB数据包、SCSI命令、文件系统等）已被移动到用户空间，并在不同的进程（微内核风格）中分离，每个进程都以其自己的受限[
_安全计算模式_](https://en.wikipedia.org/wiki/Seccomp)执行。

该工具基于Rust语言开发，并且支持在GNU/Linux上运行。

## 功能介绍

>
> 1、从不受信任的USB设备读取文件（不使用uas、USB_storage和文件系统等内核模块）。支持的文件系统有FAT、exFat、ext4、NTFS和ISO9660；
>
> 2、使用远程防病毒软件分析文件；
>
> 3、将新文件系统上的文件复制到受信任的USB设备，支持的文件系统有FAT、exFAT和NTFS；
>
> 4、将文件上传到远程服务器；
>
> 5、支持制作USB设备镜像；
>
> 6、擦除USB设备内容；

## usbsas架构

> 1、Web客户端/服务器：作为usbsas的主程序，可以部署一个安全的USB文件传输中转站；
>
> 2、Fuse实现：使用usbsas以只读模式挂载USB设备；
>
> 3、Python：usbsas可以和Python搭配使用，并使用脚本将数据从一台设备拷贝到另一台设备；

## 工具依赖组件

> ntfs3g
>
> FatFs
>
> fontawesome
>
> bootstrap
>
> Lato

## 工具体系架构/运行机制

![](https://image.3001.net/images/20221024/1666620947_63569e1357dce9acc2ee6.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/cea-sec/usbsas.git

## 工具构建

    
    
    $ cargo build --release
    
    $ cargo build --release -p usbsas-analyzer-server
    
    $ cargo build --release -p usbsas-tools
    
    $ cargo build --release --manifest-path=usbsas-hid/hid-user/Cargo.toml
    
    $ cargo build --release --manifest-path=usbsas-hid/hid-dealer/Cargo.toml

## 工具使用

### 内核模式

usbsas最大的一个优势就是在用户空间中运行，因此Linux内核不能有usb_storage和uas模块。在未设置CONFIG_USB_STORAGE和CONFIG_
USB_UAS的情况下编译内核，或者至少阻止加载此模块，因为如果存在，它们将在插入USB设备时自动加载：

    
    
    $ cat << EOF > /etc/modprobe.d/usbsas.conf
    
    install usb_storage /bin/false
    
    blacklist usb_storage
    
    install uas /bin/false
    
    blacklist uas
    
    EOF
    
    $ rmmod usb_storage
    
    $ rmmod uas
    
    $ depmod

### USB权限

usbsas需要USB设备的读写权限，因此我们需要创建一个指定用户，并提供对应权限：

    
    
    ACTION=="add", SUBSYSTEM=="usb", ENV{ID_USB_INTERFACES}=="*:080650:*", MODE="0660", OWNER="usbsas"

### Web客户端/服务器

    
    
    $ ./target/release/usbsas-server
    
    $ ./target/release/usbsas-analyzer-server
    
    $ $BROWSER http://localhost:8080

### Fuse使用

    
    
    $ ./target/release/usbsas-fuse-mount --help
    
    usbsas-fuse-mount 1.0
    
    Mount a (fuse) filesystem with usbsas
    
     
    
    USAGE:
    
        usbsas-fuse-mount [OPTIONS] <busnum> <devnum> <mountpoint>
    
     
    
    ARGS:
    
        <busnum>        设备加载的总线编号
    
        <devnum>        设备加载的Dev编号
    
        <mountpoint>     设备加载的路径
    
     
    
    OPTIONS:
    
        -h, --help                  打印帮助信息
    
        -n, --part-num <PARTNUM>    加载的分区编号 [默认: 1]
    
        -V, --version               打印版本信息

## 工具运行截图

![](https://image.3001.net/images/20221024/1666621001_63569e49311b29dabee60.png!small)

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **usbsas** ：【[ _GitHub传送门_](https://github.com/cea-sec/usbsas)】

## 参考资料

> [
> _https://en.wiki*pedia.org/wiki/Seccomp_](https://en.wikipedia.org/wiki/Seccomp)
>
> [
> _https://en.wiki*pedia.org/wiki/Sheep_dip_(computing)_](https://en.wikipedia.org/wiki/Sheep_dip_\(computing\))

