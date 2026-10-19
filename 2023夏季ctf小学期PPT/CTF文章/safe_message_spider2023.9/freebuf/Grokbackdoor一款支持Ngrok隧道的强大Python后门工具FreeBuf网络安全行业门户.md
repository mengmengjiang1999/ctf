![](https://image.3001.net/images/20230704/1688477011_64a41d53e8b45d63f5832.jpg!small)  

## 关于Grok-backdoor

Grok-backdoor是一款支持Ngrok隧道的强大Python后门工具，该工具基于Python开发，使用了Ngrok隧道来实现C&C通信。值得一提的是，当前版本的Grok-backdoor支持使用Pyinstaller生成Windows、Linux和Mac后门源码。

## 功能介绍

> 1、多平台支持，无需交叉编译：Linux、Windows、macOS；
>
> 2、经过认证授权的Bind Shell；
>
> 3、随机输出后门代码；
>
> 4、Ngrok隧道支持绕过防火墙和代理限制；

## 工作机制

Ngrok通过安全隧道将NAT和防火墙后面的本地服务器暴露给公共互联网。

![](https://image.3001.net/images/20230704/1688477025_64a41d61f3a50296fa87f.jpg!small)

接下来，Ngrok将通过唯一的端口号在恶意软件本地侦听器端口和Ngrok服务器公共IP之间建立隧道。随后，安全研究人员可以将Ngrok的公共IP和唯一端口连接到内部恶意软件侦听器。

## 工具依赖

> Python 2.7
>
> Pyinstaller 3.21
>
> python-pip 9.0.1

## 工具安装

由于该工具基于Python 2.7开发，因此我们首先需要在本地设备上安装并配置好Python
2.7环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/deepzec/Grok-backdoor.git

下载完成后，在命令行终端中切换到项目目录中，并使用pip命令和项目提供的requirements.txt文件安装并配置该项目所需的其他依赖组件：

    
    
    cd Grok-backdoor
    
    pip install -r requirements.txt

## 工具使用

在使用该工具之前，我们首先需要一个ngrok.com帐户才能使用此后门，我们可以在配置Grok-backdoor时提供Ngrok身份验证码。在目标设备上执行了Grok-backdoor服务器后，我们将能够在Ngrok状态面板中看到创建的新的TCP隧道。

下列命令可以直接创建后门源码：

    
    
    python grok-backdoor.py

 **Linux** ：

![](https://image.3001.net/images/20230704/1688477071_64a41d8fcb3c636f135f9.png!small)

 **Windows** ：

![](https://image.3001.net/images/20230704/1688477078_64a41d968ee5ec8ed6038.png!small)

此时，我们将会在grok-backdoor/dist/目录中查看到输出的后门源码：

![](https://image.3001.net/images/20230704/1688477085_64a41d9d6d16c66d6a5c1.png!small)

在目标设备上运行输出的Grok-backdoor代码后，并登录到Ngrok.com控制面板，此时就能够看到建立好的隧道URL链接了：

![](https://image.3001.net/images/20230704/1688477091_64a41da31bb17abeeca16.png!small)

通过Telnet连接隧道URL即可拿到shell：

![](https://image.3001.net/images/20230704/1688477097_64a41da94c72f32cf5ce5.png!small)

## 许可证协议

本项目的开发与发布遵循GPL-3.0开源许可证协议。

## 项目地址

 **Grok-backdoor** ：【[ _GitHub传送门_](https://github.com/deepzec/Grok-backdoor)】

