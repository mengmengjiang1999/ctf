![](https://image.3001.net/images/20211128/1638087558_61a33b86129a89e65db44.jpg!small)  

## 关于pwncat

pwncat是一款功能强大的反向Shell&BindShell处理工具，同时也是一个针对Linux系统为测试目标的后渗透漏洞利用开发平台。该工具可以帮助广大红队研究人员简化常见的任务操作，同时可以转移来自攻击者机器（而非目标）的代码。

之前版本的pwncat仅支持Linux平台，但开发人员近期在增加支持平台方面做出了大量的努力。目前，针对Windows目标廷加了Alpha版本支持。

pwncat可以拦截目标与远程shell的原始通信，并允许用户在远程主机上执行自动操作，包括枚举、植入可执行程序甚至实现权限提升等。

接收到通信连接之后，pwncat将会设置一些用于处理远程Shell的常见配置：

  * 禁用远程Shell中的历史记录功能；
  * 规范化Shell提示符；
  * 定位需要使用的二进制文件；
  * 尝试为完整交互式会话生成pty；

pwncat知道如何使用一些不同的方法生成pty，并将这些方法与之前枚举的可执行文件交叉引用。生成pty后，它将在raw模式下设置控制终端，因此我们可以通过与SSH类似的方式来跟它进行交互。pwncat还会同步本地和远程pty的设置（如行、列、TERM环境变量），以确保Shell在交互应用程序（如vim或nano）中正常运行。

![](https://image.3001.net/images/20211128/1638087571_61a33b939c28b35b89d46.png!small)

## 功能介绍

  * 自动配置远程pty；
  * 完整SSH会话支持；
  * 文件上传和下载；
  * 自动化提权枚举；
  * 自动化提权执行；
  * 自动化持久化安装/移除；
  * 自动化跟踪文件的创建和修改；
  * 自动化恢复远程“篡改”操作；

## 工具要求

pwncat需要在Linux系统上安装并配置好Python 3环境。

## 模块化

pwncat框架基于模块化架构实现，所有的功能都以模块的形式实现，其中包括信息枚举、持久化感染和权限提升等等，我们可以直接使用熟悉的run、search或info等命令来跟平台进行交互，或使用use命令进入模块上下文。

## 工具安装

pwncat以标准Python包的形式进行了封装（distutils），广大研究人员可以直接使用下列命令将该项目源码克隆至本地，并自动执行安装：

    
    
    pip install git+https://github.com/calebstewart/pwncat.git

或者，我们也可以使用下列命令实现工具的下载和安装：

    
    
    git clone https://github.com/calebstewart/pwncat.git
    
    python setup.py install

我们建议大家在一个虚拟环境中安装和运行pwncat：

    
    
    python3 -m venv pwncat-env
    
    source pwncat-env/bin/activate
    
    python setup.py install

## 工具使用

### 连接至Bindshell

    
    
    pwncat connect://10.10.10.10:4444
    
    pwncat 10.10.10.10:4444
    
    pwncat 10.10.10.10 4444

### 监听反向Shell

    
    
    pwncat bind://0.0.0.0:4444
    
    pwncat 0.0.0.0:4444
    
    pwncat :4444
    
    pwncat -lp 4444

### 通过SSH连接

    
    
    pwncat ssh://user:password@10.10.10.10
    
    pwncat user@10.10.10.10
    
    pwncat user:password@10.10.10.10
    
    pwncat -i id_rsa user@10.10.10.10

### SSH w/非标准端口

    
    
    pwncat -p 2222 user@10.10.10.10
    
    pwncat user@10.10.10.10:2222

### 重新连接并实现持久化

    
    
    pwncat reconnect://user@10.10.10.10
    
    pwncat reconnect://user@c228fc49e515628a0c13bdc4759a12bf
    
    pwncat user@10.10.10.10
    
    pwncat c228fc49e515628a0c13bdc4759a12bf
    
    pwncat 10.10.10.10

### 连接Windows反向Shell或Bindshell

    
    
    pwncat -m windows 10.10.10.10 4444
    
    pwncat -m windows -lp 4444

## 工具演示视频

 **视频地址：** 【[ _点我观看_](https://asciinema.org/a/417930)】

## 项目地址

 **pwncat：** 【[ _GitHub传送门_](https://github.com/calebstewart/pwncat)】

## 参考资料

  * [ _https://pwncat.readthedocs.io/en/latest_](https://pwncat.readthedocs.io/en/latest)
  * [ _https://github.com/calebstewart/pwncat-windows-c2_](https://github.com/calebstewart/pwncat-windows-c2)
  * [ _https://github.com/calebstewart/pwncat-badpotato_](https://github.com/calebstewart/pwncat-badpotato)

