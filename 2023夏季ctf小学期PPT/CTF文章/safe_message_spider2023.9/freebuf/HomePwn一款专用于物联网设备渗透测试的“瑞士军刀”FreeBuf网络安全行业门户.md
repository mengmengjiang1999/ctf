![](https://image.3001.net/images/20191101/1572544290_5dbb1f2293f9e.png!small)

##  HomePwn

**HomePwn是一款功能强大的物联网渗透测试框架，它可谓是该领域的一把“瑞士军刀”。HomePwn可以提供设备安全审计和渗透测试功能，企业员工可以使用HomePwn来测试同一工作环境中家庭或办公设备的安全性，并利用其中存在的安全漏洞来读取这些设备中的敏感信息，或向这些设备发送控制命令。该工具集成了非常强大的模块库，研究人员可以使用这些模块库来加载更多新的功能，并在各种不同类型的设备中来使用它们。**

HomePwn采用模块化架构开发，任何用户都可以使用不同的技术来扩展HomePwn的知识库。HomePwn由以下两个部分组成：

###  扫描模块

这些模块用于提供设备和漏洞的扫描和发现相关的功能，比如说它们可以用于在监控模式下通过适配器来进行WiFi扫描、BLE设备发现、蓝牙低功耗设备检测，并查看目标设备的连接状态等等。除此之外，它还可以使用SSDP、MDNS或多播DNS来扫描和发现家庭或办公室物联网服务。

###  特殊模块

该模块主要针对的是需要进行审计的技术。HomePwn可以针对类似WiFi、NFC或BLE这样的技术来进行安全审计和渗透测试。换句话说，这些技术都会涉及到各种功能模块，并且这些模块的使用方式也非常多样化，而这些技术在应用到物联网设备中之后，又会产生各种安全问题以及漏洞。因此，这些模块可以评估和设计这些技术在物联网通信设备中的安全等级。

##  依赖组件

> 1、[Python环境](https://www.python.org/download/releases/3.0/)
>
> 2、[Python命令行工具](https://python-prompt-toolkit.readthedocs.io/en/stable/)

##  工具使用

广大研究人员需要将本项目拷贝到本地设备中，然后通过部署之后才可以使用HomePwn生态系统。首先，我们需要完成工具依赖环境的配置。

HomePwn目前仅支持在Linux平台上使用，并且需要安装和配置python 3.6+：

> 1、[Ubuntu](https://ubuntu.com/)、[Debian](https://www.debian.org/)或类Unix平台；
>
> 2、[Python 3.6+](https://www.python.org/downloads/)；

以Ubuntu 18.04为例，首先运行下列命令更新操作系统：

    
    
    sudo apt-get update

运行下列命令将HomePwn项目克隆至本地：

    
    
    git clone https://github.com/ElevenPaths/HomePWN.git

接下来，切换到项目目录，然后运行安装脚本install.sh：

    
    
    cd [path to the HomePWN project]
    
        sudo ./install.sh

基本运行后，会询问用户是否需要创建一个virtualenv虚拟环境，如果输入“y”，那么脚本则会自动在virtualenv环境中安装Python依赖库。

##  工具使用

如果你在虚拟环境中使用HomePwn的话，还需要激活环境：

    
    
    source homePwn/bin/activate

接下来，运行HomePwn脚本：

    
    
    sudo python3 homePwn.py

##  工具使用样例

>
> 低功耗蓝牙渗透PoC：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=JgbIsP7IGxo)】
>
> 蓝牙嗅探：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=o9P1BwlHelM)】
>
> NFC克隆：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=ZLas04ZCTLU)】
>
>
> BLE嗅探（捕捉PCAP文件）：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=vw9nr584PJQ)】
>
> QR选项渗透：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=ta1DbnWOF8M)】
>
> 苹果BLE发现：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=xOU34op7Gls)】
>
>
> 小米物联网设备渗透：【[视频地址](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=Xi7KZibJsfE)】

###  许可证协议

本项目遵循GNU General Public开源许可证协议。

##  项目地址

> HomePwn：【[GitHub主页](https://github.com/ElevenPaths/HomePWN)】

###  参考文档

>
> 1、<https://github.com/ElevenPaths/HomePWN/blob/master/Papers/%5BPAPER%5Dhomepwn_ENG.pdf>

***参考来源：[ElevenPaths](https://github.com/ElevenPaths/HomePWN)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

