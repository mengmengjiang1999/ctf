## 关于FaPro

FaPro是一个网络协议服务端模拟工具，通过输出请求日志，可以实现对客户端的识别与分析。目前已支持20多种协议，支持使用web界面进行服务的配置与启停。还可以模拟虚拟网络，实现在网络中为不同的ip提供不同的服务。

  

## 下载&安装

下载最新版本的[程序包](https://github.com/fofapro/fapro/releases)，解压即可使用。

> ./fapro -h  
> Usage:  
> fapro [OPTIONS] <command>
>
> Application Options:  
> -v, --verbose Show verbose debug message
>
> Help Options:  
> -h, --help Show this help message
>
> Available commands:  
> dumpWeb dump web site  
> genConfig generate network config file  
> listProtocols list supported protocols  
> run run fapro server  
> test test protocol  
> version show version

  

第一次使用先生成配置文件:

> ./fapro genConfig > fapro.json

## 工具使用

使用默认配置启动支持的所有协议的模拟，并在本地8888端口启动web界面:

> sudo ./fapro run -v -l :8888

日志默认输出到本地文件fapro.log, 可以配置输出到mysql, elasticsearch进行日志分析。

## 工具运行截图

![1632986743_615566773fe88f00dd047.png!small?1632986716542](https://image.3001.net/images/20210930/1632986743_615566773fe88f00dd047.png!small?1632986716542)

## 协议交互展示

![rdp展示图片](https://image.3001.net/images/20210930/1632986995_61556773cac0ff107c404.gif)
**RDP交互演示**

  

![邮件协议展示](https://image.3001.net/images/20210930/1632987118_615567ee22c1a6287f752.gif)
**邮件交互演示**

  

![mysql协议演示](https://image.3001.net/images/20210930/1632987168_61556820073fecd8a6ae9.gif)
**mysql交互演示**

  

![ssh交互演示](https://image.3001.net/images/20210930/1632987217_615568511d6f341fea260.gif)
**SSH交互演示**

## 项目地址

 **Fapro** : 【 **[ _GitHub传送门_](https://github.com/fofapro/fapro)** 】

