![](https://image.3001.net/images/20220424/1650789246_62650b7ecdd7ed9538402.png!small)

## 关于Smap

Smap是一款功能强大的被动式网络扫描工具，该工具类似于Nmap的功能，但Smap由Shodan.io驱动，并且使用了Shodan.io的免费API来实现端口扫描，可以作为Nmap的一款替代产品。该工具能够接收和Nmap相同的命令行参数，并生成相同的输出结果。在某些情况下，Smap的适用场景更广。

## 功能介绍

> 1、每秒支持扫描200台主机；
>
> 2、并不需要任何账号或API密钥；
>
> 3、支持扫描和检测安全漏洞；
>
> 4、支持所有的Nmap输出格式；
>
> 5、服务和版本指纹；
>
> 6、不会与目标产生联系；

## 工具安装

### 预构建源码

广大研究人员可以访问该项目的【[
_Releases页面_](https://github.com/s0md3v/Smap/releases)】下载获取该工具的预构建版本，下载后开箱即用。

### 手动构建

首先，我们需要在本地设备上安装并配置好Go环境。接下来，使用下列命令将该项目安装至本地：

    
    
    go install -v github.com/s0md3v/smap/cmd/smap@latest

### AUR包

广大研究人员还可以在AUR上通过[ _smap_ _-git_](https://aur.archlinux.org/packages/smap-git)（预构建）和[ _smap_ _-bin_](https://aur.archlinux.org/packages/smap-bin)（预构建）来下载和安装Samp。

## 工具使用

Smap支持和Nmap相同的参数选项，如果你不熟悉Namp的话，可以先阅读一下Nmap的使用手册。

### 指定扫描目标

    
    
    smap 127.0.0.1 127.0.0.2

我们还可以指定一个目标列表，每一个目标按行分隔：

    
    
    smap -iL targets.txt

 **支持的格式**

    
    
    1.1.1.1         // IPv4地址
    
    example.com     // 主机名称
    
    178.23.56.0/8   // CIDR

### 输出结果

Smap支持六种不同的输出格式，可以使用-o*命令来控制：

    
    
    smap example.com -oX output.xml

如果你想要在命令行终端窗口中打印输出数据，可以使用“-”连字符选项指定文件名。

 **支持的格式**

    
    
    oX    // Nmap的XML格式
    
    oG    // Nmap的greppable 格式
    
    oN    // Nmap的默认格式
    
    oA    // 一次性以上述三种格式输出
    
    oP    // IP:端口，按行分隔
    
    oS    // 自定义Smap格式
    
    oJ    // JSON格式

注意：由于Nmap不会扫描和显示漏洞以及标签，因此这部分数据不会在Nmap的格式中显示，如需查看可使用“-oS”选项。

### 指定端口

Smap默认会扫描[ _1237_
_个端口_](https://gist.githubusercontent.com/s0md3v/3e953e8e15afebc1879a2245e74fc90f/raw/1e20288e9bef43b60f7306b6f7e23044dabd9b8c/shodan_ports.txt)，如果你想查看指定端口的扫描信息，可以使用“-p”选项：

    
    
    smap -p21-30,80,443 -iL targets.txt

## 工具使用样例

![](https://image.3001.net/images/20220424/1650789319_62650bc7b9a6b430068e6.png!small)

## 许可证协议

本项目的开发与发布遵循[ _AGPL_
_-3.0_](https://github.com/s0md3v/Smap/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Smap：** 【[ _GitHub传送门_](https://github.com/s0md3v/Smap)】

## 参考资料

> [ _https://github.com/s0md3v/Smap/wiki/FAQ#how-do-i-install-> smap_](https://github.com/s0md3v/Smap/wiki/FAQ#how-do-i-install-smap)
>
> [ _https://aur.archlinux.org/packages/smap-> git_](https://aur.archlinux.org/packages/smap-git)
>
> [ _https://aur.archlinux.org/packages/smap-> bin_](https://aur.archlinux.org/packages/smap-bin)
>
> [
> _https://gist.githubusercontent.com/s0md3v/3e953e8e15afebc1879a2245e74fc90f/raw/1e20288e9bef43b60f7306b6f7e23044dabd9b8c/shodan_ports.txt_](https://gist.githubusercontent.com/s0md3v/3e953e8e15afebc1879a2245e74fc90f/raw/1e20288e9bef43b60f7306b6f7e23044dabd9b8c/shodan_ports.txt)

