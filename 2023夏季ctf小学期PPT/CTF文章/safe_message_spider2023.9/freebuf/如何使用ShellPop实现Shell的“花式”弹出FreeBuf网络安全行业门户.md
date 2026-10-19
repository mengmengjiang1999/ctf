![](https://image.3001.net/images/20230906/1693974243_64f7fee31e2d1f7e54c65.png!small)

## 关于ShellPop

ShellPop是一款针对Shell的管理工具，在该工具的帮助下，广大研究人员不仅可以轻松生成各种复杂的反向Shell或Bind
Shell，而且还可以在渗透测试过程中实现Shell的“花式”弹出，这将极大程度地简化大家的渗透测试任务。

简而言之，不要再用.txt文件来存储你的反向Shell了，这简直就是浪费时间，ShellPop绝对是你的不二选择。

## 工具安装

由于该工具基于Python 2.7开发，因此我们首先需要在本地设备上安装并配置好Python 2.7环境。

接下来，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/0x00-0x00/ShellPop.git

然后切换到项目目录中，使用下列命令安装该工具所需的其他依赖组件：

    
    
    root@kali# apt-get install python-argcomplete metasploit-framework -y
    
    root@kali# pip install -r requirements.txt

最后，执行工具安装脚本即可：

    
    
    root@kali# python setup.py install

## 工具使用

查看工具帮助信息：

    
    
    root@kali# shellpop --help

![](https://image.3001.net/images/20230906/1693974269_64f7fefd2c50c6e2c0f19.jpg!small)

查看ShellPop中可用的Shell：

    
    
    root@kali# shellpop --list

![](https://image.3001.net/images/20230906/1693974278_64f7ff068463e506fc4a7.jpg!small)

生成一个Python TCP反向Shell（1.2.3.4:443）：

![](https://image.3001.net/images/20230906/1693974285_64f7ff0d0f55bbaa33371.jpg!small)

生成一个PowerShell TCP Bind Shell（端口1337）：

![](https://image.3001.net/images/20230906/1693974290_64f7ff12e1bb00f4b6bf7.jpg!small)

变量重命名混淆：

![](https://image.3001.net/images/20230906/1693974298_64f7ff1a81d0de996c77b.jpg!small)

IP地址和端口混淆：

![](https://image.3001.net/images/20230906/1693974306_64f7ff222185021c7f8ea.jpg!small)

使用URL 编码生成一个Python TCP 反向Shell（1.2.3.4:443）：

![](https://image.3001.net/images/20230906/1693974313_64f7ff297ac0376daa9a5.jpg!small)

使用Base64编码生成一个Python TCP 反向Shell（1.2.3.4:443），并设置相应的解码器：

![](https://image.3001.net/images/20230906/1693974320_64f7ff3051da847f9993a.jpg!small)

使用URL编码+Base64编码生成一个Python TCP 反向Shell（1.2.3.4:443）：

![](https://image.3001.net/images/20230906/1693974327_64f7ff371c3f1aab634b8.jpg!small)

使用Base64编码生成一个PowerShell Bind Shell（端口1337）：

![](https://image.3001.net/images/20230906/1693974333_64f7ff3d53769d9295988.jpg!small)

使用所有的编码方法生成一个Python TCP反向Shell（1.2.3.4:443）：

![](https://image.3001.net/images/20230906/1693974340_64f7ff44a94d73f594df7.jpg!small)

使用UDP协议生成Shell：

![](https://image.3001.net/images/20230906/1693974347_64f7ff4b4b2a6223d6817.jpg!small)

## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/0x00-0x00/ShellPop/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **ShellPop** ：【[ _GitHub传送门_](https://github.com/0x00-0x00/ShellPop)】

