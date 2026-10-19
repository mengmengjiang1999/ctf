****

**严正声明：本文仅限于技术讨论，严禁用于其他用途。**

**Seeker是一款可以获取高精度地理和设备信息的工具。其利用HTML5，Javascript，JQuery和PHP来抓取设备信息，以及Geolocation接口实现对设备高精度地理位置的获取。**

Seeker在Apache服务器上托管了一个虚假的站点，并使用Ngrok生成一个SSL链接，询问访客位置权限，如果用户授权允许，我们将可以获取到以下信息：

> 经度
>
> 纬度
>
> 准确率
>
> 海拔高度 - 并非总是可用
>
> 方向 - 仅在用户移动时可用
>
> 速度 - 仅在用户移动时可用

除了位置信息，我们还可以获取到设备的相关信息：

> 操作系统
>
> 平台
>
> CPU核心数
>
> RAM大小 - 近似结果
>
> 屏幕分辨率
>
> GPU信息
>
> 浏览器名称和版本
>
> 公网IP地址

此工具纯粹只是一个概念证明（PoC），仅用于教育目的。其主要目的是告诉大家不要轻易点击来路不明的链接并授予关键权限，否则你将可能暴露你的设备信息甚至你的位置等。

> 有许多工具和服务可以为我们提供IP地理定位，但这都只是大概的范围并不精准。此外，也不会为我们提供用户的位置。
> 但是，一旦用户主动授权定位，则会获取到误差大约只在30米的高精度用户定位。

 **注意：** 在iPhone上由于某种原因定位精度约为65米。

##  **测试系统**

> Kali Linux 2018.2
>
> Ubuntu 18.04

##  **安装要求**

需同时支持Python2和Python3。

Seeker会用到的通用标准python模块：

> os
>
> time
>
> json
>
> requests
>
> subprocess

 **安装**

    
    
    git clone https://github.com/thewhiteh4t/seeker.git
    cd seeker/
    chmod 777 install.sh
    ./install.sh
    
    #After Installation just type seeker in console

 **PoC**

看不到？点[这里](https://v.qq.com/x/page/r0748ln9od8.html)

 **截图**

![Seeker：一款可获取高精度地理和设备信息的工具分析](https://image.3001.net/images/20180803/1533247824_5b6381500bc0b.png!small)![Seeker：一款可获取高精度地理和设备信息的工具分析](https://image.3001.net/images/20180803/1533247824_5b6381501ebcb.png!small)

 ** *参考来源：[github](https://github.com/thewhiteh4t/seeker)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

