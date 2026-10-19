***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

**今天给大家介绍的是一款名叫Dockernymous的脚本，广大研究人员可以利用Dockernymous在Docker容器中创建一个类似Whonix的网关/工作站环境。**

![1.png](https://image.3001.net/images/20190728/1564282835_5d3d0fd328529.png!small)

## 注意

Dockernymous目前仍处于开发的前期阶段，该项目仅供研究学习使用，请不要将其用于恶意目的。

### 版本提醒

开发人员对脚本的功能逻辑进行了完整修改，以提升脚本的可用性和稳定性，外观功能菜单也进行了相应的升级。

### 新功能包括：

> 1、 提供了容器环境运行和存储的选项，可在退出脚本后保持容器的运行状态。
>
> 2、 可在菜单中开启Tor服务。
>
> 3、 可在菜单中停止Tor服务。

将网关镜像/容器由Debian修改为了Alpine，修改后最终的镜像大小约为23MB（Alpine），之前的Debian为200MB。

## 工具介绍

Dockernymous是一款针对Docker的启动脚本，可以单独运行和配置两台单独的Linux容器以配置匿名工作站-网关，该工具主要针对的是经验丰富的Linux/Docker用户、安全专家以及渗透测试人员。

网关容器以匿名中间件的形式工作（具体请参考<https://trac.torproject.org/projects/tor/wiki/doc/TransparentProxy>），可以通过Tor网络来传输和路由工作站容器的所有网络通信流量。

该脚本会创建一个类似Whonix的操作系统，而这种系统无法有效地运行两台硬件虚拟化设备并且不具备虚拟化功能。

![2.png](https://image.3001.net/images/20190728/1564282870_5d3d0ff639d7a.png!small)

## 工具要求

### 主机（Linux）：

    
    
    docker
    
    vncviewer
    
    xterm
    
    curl

### 网关镜像：

    
    
    Linux(例如 Alpine,Debian )
    
    tor
    
    procps
    
    ncat
    
    iptables

### 工作站镜像：

    
    
    Linux(例如 Kali)
    
    ‎xfce4或其他桌面环境 (用于VNC访问)
    
    Tightvncserver

## 工具安装&使用指南

### 1、 主机

使用git命令将项目代码克隆至本地：

    
    
    git clone https://github.com/bcapptain/dockernymous.git

Dockernymous需要一个正在运行的Docker环境以及非默认配置的Docker网络。我们可以使用下列命令来创建一个：

    
    
    dockernetwork create --driver=bridge --subnet=192.168.0.0/24 docker_internal

### 2、 网关（Alpine）

首先，获取一个轻量级网关镜像！比如说Alpine：

    
    
    docker pull alpine

运行镜像，更新包列表，安装iptables以及Tor：

    
    
    docker run -it alpine /bin/sh
    
    apkadd --update tor iptables iproute2
    
    exit

当然了，你也可以根据自己的需要来使用自定义网关。如果你需要长期使用的话，你还可以在网关容器中创建一个新的镜像，这样你就可以每次都利用镜像来启动新的容器环境了：

    
    
    docker commit [Container ID] my_gateway

通过运行下列命令即可获取容器的Container ID：

    
    
    dockerps –a

### 3、 工作站（Kali Linux）

获取工作站镜像，如果你主要工作是进行渗透测试，我们就以Kali Linux为例：

docker pull kalilinux/kali-linux-docker

更新并安装你所需要使用的工具（具体请参考<https://www.kali.org/news/kali-linux-metapackages/>）：

    
    
    docker run -it kalilinux/kali-linux-docker /bin/bash
    
    apt-get update
    
    apt-get dist-upgrade
    
    apt install kali-linux-top10

确保已安装了tightvncserver和curl包：

    
    
    apt-get install tightvncserver
    
    apt-get install curl

安装xfce4精简图形化桌面：

    
    
    $apt-get install xfce4 
    
    $apt-get clean
    
    $exit

如果你需要长期使用网关系统，你可以针对自定义容器创建一个镜像文件，这样你就可以每次都利用镜像来启动新的容器环境了：

    
    
    $docker commit [Container ID] my_workstation

通过运行下列命令获取容器的Container ID：

    
    
    $docker ps –a

### 4、 运行Dockernymous

如果你修改了镜像名称，你需要打开dockernymous.sh并修改对应的配置项。

此时，一切已准备就绪。可能你需要先给脚本提供可执行权限：

    
    
    chmod +x dockernymous.sh

接下来，我们可以使用下列命令运行Dockernymous：

    
    
    bash dockernymous.sh

或

    
    
    ./dockernymous.sh

## 项目地址

> Dockernymous：【[GitHub传送门](https://github.com/bcapptain/dockernymous)】

 ***
参考来源：[bcapptain](https://github.com/bcapptain/dockernymous)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

