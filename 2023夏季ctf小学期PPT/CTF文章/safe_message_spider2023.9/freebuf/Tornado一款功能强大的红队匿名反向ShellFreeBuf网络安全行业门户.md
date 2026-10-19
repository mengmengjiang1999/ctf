![](https://image.3001.net/images/20220605/1654435844_629cb0043380f030c5c81.png!small)

## 关于Tornado

Tornado是一款功能强大的红蓝队安全研究工具，同时也一款功能强大的匿名反向Shell。该工具基于隐藏服务实现其功能，并且没有使用端口转发技术。简而言之，Tornado是一款完全无法被检测到的反向Shell工具，可以帮助广大研究人员实现渗透测试等安全分析任务。

Tornado通过Metasploit和msfvenom模块实现其功能，可以轻松为本地主机创建隐藏服务。整个过程不会涉及到跟.onion域名的端口转发。如果你使用过其他远程管理工具的话，你就知道这意味着什么了。值得一提的是，Tornado能够基于相关技术提供安全研究过程中的匿名信，而且不会暴露测试设备的具体信息。

## 功能介绍

> 1、创建隐藏服务；
>
> 2、使用完全无法被检测到的Shellcode生成跨平台msfvenom Payload；
>
> 3、匿名反向Shell连接；

## 工具特性

> 1、支持与Windows操作系统整合；
>
> 2、反向Shell无需Tor2web，工作机制基于Payload注入实现；

## 工具下载

该工具的下载和使用非常简单，由于该工具基于Python 3开发，因此我们首先需要在 本地设备上安装并配置好Python 3环境。

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/samet-g/tornado.git

代码库克隆完成后，切换到项目目录中，并使用下列命令安装该工具所需的依赖组件：

    
    
    $ sudo python3 setup.py install

最后，别忘了使用sudo权限来运行Tornado：

    
    
    $ sudo tornado

## 工具使用

下列命令可以使用sudo权限和“-start”参数来运行Tornado：

    
    
    $ sudo tornado -start

## 工具运行截图

![](https://image.3001.net/images/20220605/1654435881_629cb0297971f6f801dd4.png!small)

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **Tornado：** 【[ _GitHub传送门_](https://github.com/samet-g/tornado)】

## 参考资料

> [ _https://www.torproject.org/_](https://www.torproject.org/)
>
> [ _https://www.metasploit.com/_](https://www.metasploit.com/)
>
> [ _https://www.tor2web.org/_](https://www.tor2web.org/)

