![](https://image.3001.net/images/20200807/1596797016.png!small)

## gTunnel

gTunnel是一款基于Golang和gRPC开发的TCP隧道套件，gTunnel能够管理多个基于单个TCP/HTTPS链接的正向和反向通信隧道。目前，gTunnel的客户端可执行文件已在Windows和Linux上进行了测试，可稳定运行。

### 工具依赖

gTunnel目前已在Docker v19.03.6版本中进行了测试，但理论上支持任何版本的Docker。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地，并按照下列方法来使用该工具：

    
    
    git clone https://github.com/hotnops/gtunnel.git

## 工具使用

项目目录下的start_sever.sh脚本将会构建一个Docker镜像，运行之后不会暴露任何端口。如果你想要使用正向隧道，请确保映射响应端口或修改Docker网络。

    
    
    ./start_server.sh

运行之后，你将会看到如下所视的终端界面：

![](https://image.3001.net/images/20200807/1596797039.png!small)

首先，我们需要生成一个在远程系统中运行的客户端程序。针对Windows系统，生成一个名为“win-client”的Windows客户端：

    
    
    >>> configclient win 172.17.0.1 443 win-client

针对Linux系统，生成一个名为“lclient”的Linux客户端：

    
    
    >>> configclient linux 172.17.0.1 443 lclient

该命令将会在“configured”目录中输出一个预配置的可执行文件，并跟./start_server.sh关联。在远程系统中运行这个可执行文件之后，终端窗口将接收到客户端连接成功的消息：

![](https://image.3001.net/images/20200807/1596797052.png!small)

如需使用新连接的客户端，直接输入“use + 客户端名称”即可，这里支持Tab键补全：

    
    
    >>> use test
    
    (test) >>>  

此时，命令行窗口图表将变成新切换的终端节点，我们可以在这里添加或删除通信隧道：

    
    
    addtunnel (local | remote) listenPort destinationIP destinationPort

比如说，在端口4444打开一个本地隧道，跟远程网络10.10.1.5（端口445）进行连接，然后将其命名为“smbtun”：

    
    
    addtunnel local 4444 10.10.1.5 445 smbtun

类似地，我们也可以在远程系统打开端口666，然后将所有流量转发至本地网络的192.168.1.10（端口443）：

    
    
    addtunnel remote 666 192.168.1.10 443

需要注意的是，隧道名命为可选项，如果不提供该选项，工具将会给隧道生成一个随机名称。如需列出所有活动隧道，可以使用“listtunnels”命令：

    
    
    (test) >>> listtunnels
    
    Tunnel ID: smbtun
    
    Tunnel ID: dVck5Zba

如需删除一个隧道，可以直接使用“deltunnel”命令：

    
    
    (test) >>> deltunnel smbtun
    
    Deleting tunnel : smbtun

如需在目标设备上开启一个socks代理，可以使用“socks”命令。下面的命令将在运行了gClient的主机上，开启一个socks服务器（端口号为1080）.一般来说，我们还需要在gTunnel的命令行接口中使用命令来创建一个信道，并通过该信道来使用socks服务器：

    
    
    socks 1080
    
    addtunnel local 1080 127.0.0.1 1080

如需跟其他远程系统进行交互，可以使用“back”命令：

    
    
    (test) >>> back
    
    >>>  

如需跟客户端或服务器断开连接，可以直接使用“disconnect”命令：

    
    
    (test) >>> disconnect
    
    2020/03/20 22:14:52 Disconnecting test
    
    (test) >>> 2020/03/20 22:14:52 Endpoint disconnected: test
    
    >>>

如需退出服务器端，可直接运行“exit”命令：

    
    
    >>> exit

## 项目地址

gTunnel：【[ _GitHub传送门_](https://github.com/hotnops/gtunnel)】

