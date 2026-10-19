## FRP介绍

FRP (Fast Reverse Proxy) 是一个使用 Go 语言开发的高性能的反向代理应用，可以轻松地进行内网穿透，对外网提供服务。FRP 支持
TCP、UDP、HTTP、HTTPS等协议类型，他支持点对点的转发，还有全流量转发，FRP最大的一个特点是使用SOCKS代理，而SOCKS是加密通信的，类似于做了一个加密的隧道，可以把外网的流量，通过加密隧道穿透到内网。效果有些类似于VPN

FRP下载地址：`https://github.com/fatedier/frp/releases`

![图片.png](https://image.3001.net/images/20230823/1692728063_64e4faffd5697b6ebe3a9.png!small)

FRP使用手册：`https://gofrp.org/docs/`

![图片.png](https://image.3001.net/images/20230823/1692728078_64e4fb0e5527db6ee2965.png!small)

如下，我们将FRP工具下载到本地解压之后，工具内的文件如图所示，FRP主要分为两种文件, frps 和 frpc，frps就是 FRP Server
服务端，frpc就是 FRP Client 客户端，.ini 后缀的就是配置文件，.exe后缀的就是运行文件

![图片.png](https://image.3001.net/images/20230823/1692728092_64e4fb1cddda0857050f2.png!small)

我们这里举个列子，我们现在正在进行渗透攻击内网服务器，我们要将 frps 及 frps.ini 放到具有公网 IP 的机器上也就是黑客的电脑上，将 frpc
及 frpc.ini 放到处于内网环境的机器上，这样我们可以对内网的机器做一些端口映射、转发或者内网穿透，将内网的机器连接到我们位于公网的黑客主机上

![图片.png](https://image.3001.net/images/20230823/1692728106_64e4fb2aef94504360938.png!small)

FRP两个文件，都有两种配置文件，frpc.ini 和 frpc_full.ini，如名字一样，只有.ini 的配置文件比较简单，我们打开frpc.ini
文件发现需要配置的内容参数如下：

![图片.png](https://image.3001.net/images/20230823/1692728119_64e4fb37b377e16a51898.png!small)

frpc_full.ini就如同名字一样，比较全面，可以配置的参数可以说是非常的详细，我们打开frpc_full.ini文件发现可以配置的内容参数如下：

![图片.png](https://image.3001.net/images/20230823/1692728132_64e4fb443fa5596e77365.png!small)

## FRP启动

假设现在我们遇到了攻防场景，需要将一台位于内网的机器B代理到位于官网的黑客机器A上，场景如下：

![图片.png](https://image.3001.net/images/20230823/1692728144_64e4fb50acdfef3c1d632.png!small)

### 服务端启动配置

Frp 默认给出两个服务端配置文件，一个是简版的 frps.ini，另一个是完整版本
frps_full.ini，服务端一般就是搭建在公网的机器上（黑客的机器）

我们打开代理配置文件，配置如下（默认配置中的监听的端口是7000，端口我们可以根据实际情况自己修改）：

![图片.png](https://image.3001.net/images/20230823/1692728157_64e4fb5df348c00413180.png!small)

然后我们使用如下的命令，使用代理配置文件启动工具，使用FRPS 运行 frps.ini 配置文件

`frps.exe -c frps.ini`

![图片.png](https://image.3001.net/images/20230823/1692728204_64e4fb8cd3c4f923728bd.png!small)

### 客户端启动配置

FRP 默认也给出两个客户端配置文件，一个是简版的 frpc.ini，另一个是完整版本 frpc_full.ini。 这里同样以简版的 frpc.ini
文件为例，假设 FRP 服务端所在服务器的公网 IP 为 X.X.X.X（这里我们需要在内网机器上启动）：

那我们需要将配置文件修改如下：

![图片.png](https://image.3001.net/images/20230823/1692728218_64e4fb9ab16bc8523f1c9.png!small)

然后我们使用如下的命令，使用代理配置文件启动工具，使用FRPC 运行 frpc.ini 配置文件：

    
    
    frpc.exe -c frpc.ini
    

![图片.png](https://image.3001.net/images/20230823/1692728229_64e4fba51ab2768083929.png!small)

然后我们的内网机器B就会连接到我们位于官网的机器A上，操作非常便捷简单

## FRP的配置文件介绍

FRP配置文件非常重要，需要什么功能就可以进行不同的配置，来进行代理

FRP配置文件参考文档：`https://gofrp.org/docs/reference/server-configures/`

服务端配置参数：

![图片.png](https://image.3001.net/images/20230823/1692728243_64e4fbb393dd58761fb7b.png!small)

客户端配置参数：

![图片.png](https://image.3001.net/images/20230823/1692728258_64e4fbc22686fc4fd913e.png!small)

## FRP 点对点转发（P2P）

点对点转发（P2P）从功能上讲有点类似于端口转发或者端口映射一类的技术

### 实验扑拓

假设现在我们有如下的场景，我们获得了位于内网的一台主机的权限，并且知道了他的登录用户名和密码。他的3389端口只对内网开放，现在我们需要将该主机的3389端口映射到公网我们的VPS的端口，那样，我们连接我们VPS的端口就相当于连接内网主机的3389端口了：

![图片.png](https://image.3001.net/images/20230823/1692728269_64e4fbcddf132ed46a62a.png!small)

位于内网机器由于防火墙等网络限制无法直接访问我们位于官网VPS机器的端口，我们这时可以通过使用FRP进行端口转发到公网端口，从而连接内网

### 实验环境

现有实验环境如下：

身份| IP  
---|---  
VPS| 192.168.0.112  
内网机器| 192.168.41.133  
  
### 服务端

首先我们需要将 frps.exe 和 frps.ini 文件上传到VPS机器上，修改 frps.ini 文件配置参数如下：

![图片.png](https://image.3001.net/images/20230823/1692728289_64e4fbe1d29f8bb7ac644.png!small)

然后使用以下的命令启动服务端，开始监听位于VPS机器的7000端口

    
    
    frps.exe -c frps.ini
    

![图片.png](https://image.3001.net/images/20230823/1692728302_64e4fbee4a02f2ea41204.png!small)

### 客户端

我们需要将 frpc.exe 和 frpc.ini 文件上传到内网机器上，修改 frpc.ini 文件配置参数如下：

![图片.png](https://image.3001.net/images/20230823/1692728314_64e4fbfae68dbdb410c6e.png!small)

然后使用以下的命令启动客户端，来连接我们位于官网的机器（192.168.0.112）的7000端口

    
    
    frpc.exe -c frpc.ini
    

![图片.png](https://image.3001.net/images/20230823/1692728325_64e4fc055506326aeac4d.png!small)

连接完成后，服务端会传来回显

![图片.png](https://image.3001.net/images/20230823/1692728338_64e4fc120841e2f74009f.png!small)

这时我们就可以在VPS上通过远程桌面连接本地的6000端口去连接位于内网的机器，（这一步

