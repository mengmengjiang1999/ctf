## 基础知识

Docker Remote API 是一个取代远程命令行界面（rcli）的REST
API，其默认绑定2375端口，如管理员对其配置不当可导致未授权访问漏洞。攻击者利用 docker client 或者 http 直接请求就可以访问这个
API，可导致敏感信息泄露，甚至可进一步利用Docker自身特性，借助容器逃逸，最终完全控制宿主服务器

Docker daemon 是 Docker 引擎的后台进程，也称为 Dockerd。它是一个长时间运行的进程，负责管理 Docker
镜像、容器、网络和存储等各种资源，并提供一个 API 以供 Docker 客户端进行交互

当您在 Docker 主机上使用 Docker 命令时（例如 docker run），Docker 客户端将向 Docker daemon
发送命令请求，并通过 Docker API 进行通信。Docker daemon 接收并解析这些请求，并在其内部管理对象存储中创建、修改或删除相应的
Docker 资源。随后，Docker daemon 将响应结果发送回客户端，然后等待下一个命令请求

另外，Docker daemon 也负责监视 Docker 主机上正在运行的容器和服务，以及处理与 Docker 网络和存储相关的操作。它还可以与其他
Docker daemon 进行通信，以实现跨主机的镜像和容器管理。总之，Docker daemon 是整个 Docker 引擎的核心组件，负责实现
Docker 的各种功能，并将其暴露给用户和其他程序使用。

## 环境搭建

首先我们执行如下的代码将 docker 守护进程监听在 0.0.0.0

    
    
    dockerd -H=0.0.0.0:2375 -H unix:///var/run/docker.sock
    

  * -H=0.0.0.0:2375：指定 Docker daemon 监听的 TCP 端点地址和端口号。0.0.0.0 表示绑定到任何可用网络接口上，即允许从其他主机上的容器或者计算机上运行的 Docker 客户端连接。2375 是 Dockerdaemon 监听的端口号

  * -H unix:///var/run/docker.sock：指定 Docker daemon 监听的 Unix 域套接字路径，即 /var/run/docker.sock

运行这个命令，Docker daemon 将同时监听 TCP 端点和 Unix 域套接字,并且没有安全保护

![图片.png](https://image.3001.net/images/20230823/1692729364_64e500149c4e75ff8eacd.png!small)

执行后出现上面错误是由于当前环境docker已经在运行中了，需要先停止docker

    
    
    systemctl stop docker
    

在执行下面的命令

    
    
    dockerd -H=0.0.0.0:2375 -H unix:///var/run/

