![](https://image.3001.net/images/20200809/1596988349.jpg!small)

## Mística

Mística是一款支持任意协议的应用程序通信工具，该工具允许将数据嵌入至应用层协议字段之中，其目标就是为任意通信建立一个稳定的双向信道。目前，该工具实现了对HTTP、DNS和ICMP协议的封装，在后续版本中Mística还将引入更多的通信协议。

Mística是以模块化的方式构建的，其核心是一个自定义传输协议，该协议名为SOTP，即简单覆盖传输协议。根据该协议的定义，通信数据将会被加密，在完成数据分块后便会被添加至SOTP包中。接下来，SOTP包会被编码并嵌入到应用协议的目标数据域中，然后被发送给通信的另一方。

SOTP层的目标是以最小的开销提供通用的二进制传输协议，SOTP包可以很容易地隐藏或嵌入到合法的应用协议中。另外，SOTP还确保数据包被另一端接收，数据使用了RC-4加密算法，并通过使用轮询机制确保信息可以以两种方式透明传输。

## 工具依赖

该项目的使用需要依赖于下列组件：

> Mística客户端需要Python 3.7环境；
>
> Mística服务器端需要Python 3.7环境和dnslib；

### 配置命令：

    
    
    python3.7 -m pip install pip --user
    
    pip3.7 install dnslib --user

如果你不想在你的系统中安装Python的话，你可以使用绿色版：

-Windows、Linux和macOS：【 _点我获取_】

-仅Windows：【[ _点我获取_](https://github.com/winpython/winpython/releases/tag/2.1.20190928)】

## 工具下载

广大研究人员可以使用下列命令将项目代码克隆至本地：

    
    
    git clone https://github.com/IncideDigital/Mistica.git

## 当前模块

### 通信层模块：

> io：从stdin读取数据，通过SOTP连接发送数据；从SOTP连接读取数据，打印至stdout。
>
> shell：执行通过SOTP连接发送过来的命令，并返回输出，与io模块兼容。
>
> tcpconnect：连接至TCP端口，从socket读取数据，通过SOTP连接发送数据；从SOTP连接读取数据，通过socket发送数据。
>
> tcplisten：绑定至TCP端口，从socket读取数据，通过SOTP连接发送数据；从SOTP连接读取数据，通过socket发送数据。

### 封装器模块：

> dns：使用不同的方法对DNS查询/响应中的数据进行编码/解码。
>
> http：使用不同的方法对HTTP请求/响应中的数据进行编码/解码。
>
> icmp：使用不同的方法对ICMP请求/响应中的数据进行编码/解码。

## 工具使用

### ms.py：Mística服务器

    
    
    usage: ms.py [-h] [-k KEY] [-l LIST] [-m MODULES] [-w WRAPPER_ARGS]
    
                 [-o OVERLAY_ARGS] [-s WRAP_SERVER_ARGS]
    
     
    
    Mistica server. Anything is a tunnel if you're brave enough. Run without
    
    parameters to launch multi-handler mode.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -k KEY, --key KEY     RC-4 key used to encrypt the comunications
    
      -l LIST, --list LIST  Lists modules or parameters. Options are: all,
    
                            overlays, wrappers, <overlay name>, <wrapper name>
    
      -m MODULES, --modules MODULES
    
                            Module pair in single-handler mode. format:
    
                            'overlay:wrapper'
    
      -w WRAPPER_ARGS, --wrapper-args WRAPPER_ARGS
    
                            args for the selected overlay module (Single-handler
    
                            mode)
    
      -o OVERLAY_ARGS, --overlay-args OVERLAY_ARGS
    
                            args for the selected wrapper module (Single-handler
    
                            mode)
    
      -s WRAP_SERVER_ARGS, --wrap-server-args WRAP_SERVER_ARGS
    
                            args for the selected wrap server (Single-handler
    
                            mode)
    
      -v, --verbose         Level of verbosity in logger (no -v None, -v Low, -vv
    
                            Medium, -vvv High)

 **Mística服务器有两种主要工作模式：**

> 单处理器模式：py带参数启动时，它将允许一个单一通信层模块与一个封装器模块进行交互。
>
> 多处理器模式：py不带参数启动时，用户将进入一个交互式终端，此时多通信层模块和封装器模块将会启动，这些模块之间能够进行交互。

### mc.py：Mística客户端

    
    
    usage: mc.py [-h] [-k KEY] [-l LIST] [-m MODULES] [-w WRAPPER_ARGS]
    
                 [-o OVERLAY_ARGS]
    
     
    
    Mistica client.
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -k KEY, --key KEY     RC-4 key used to encrypt the comunications
    
      -l LIST, --list LIST  Lists modules or parameters. Options are: all,
    
                            overlays, wrappers, <overlay name>, <wrapper name>
    
      -m MODULES, --modules MODULES
    
                            Module pair. Format: 'overlay:wrapper'
    
      -w WRAPPER_ARGS, --wrapper-args WRAPPER_ARGS
    
                            args for the selected overlay module
    
      -o OVERLAY_ARGS, --overlay-args OVERLAY_ARGS
    
                            args for the selected wrapper module
    
      -v, --verbose         Level of verbosity in logger (no -v None, -v Low, -vv
    
                            Medium, -vvv High)

## Docker使用

如需在本地主机上使用，可直接创建一个Docker镜像，这样就不需要安装Python或dnslib了。接下来，用户需要按照下列方式进行部署。

首先，使用下列命令进行镜像构建：

    
    
    sudo docker build --tag mistica:latest

接下来，使用下列命令创建网络：

    
    
    sudo docker network create misticanw

创建完成后，使用下列命令运行服务器端：

    
    
    sudo docker run --network misticanw --sysctl net.ipv4.icmp_echo_ignore_all=1 -v $(pwd):/opt/Mistica -it mistica /bin/bash

最后，使用下列命令运行客户端：

    
    
    sudo docker run --network misticanw -v $(pwd):/opt/Mistica -it mistica /bin/bash

## 工具演示视频

视频地址：【[
_点我观看_](https://www.youtube.com/playlist?list=PLyUtb47GNF9wqIwI1DGpX_Fr1IXpXHRqB)】

## 项目地址

Mística：【[ _GitHub传送门_](https://github.com/IncideDigital/Mistica)】

