# 0x00 前言

Docker是渗透测试中必学不可的一个容器工具，在其中，我们能够快速创建、运行、测试以及部署应用程序。如，我们对一些漏洞进行本地复现时，可以使用Docker快速搭建漏洞环境，完成复现学习。

 **注：本教程仅供学习参考，请勿用在非法途径上，违者后果自负，与笔者无关。**

# 0x01 Docker的安装

###
1、Linux内核版本查看![](https://image.3001.net/images/20211105/1636110741_618511959c55c0619a018.png!small)

### 2、更新apt源满足下载要求

    
    
    #新重写sources.list中内容，一个个字母删除太久了
    cho > /etc/apt/sources.list
    #进入sources.lis重新编辑apt源
    vim /etc/apt/sources.list
    #直接CV大法写入下面的apt源
    
    
    #其他apt源
    #此处，笔者仅添加中科达和阿里的，其他注释掉
    #中科大
    deb http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
    deb-src http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
    #阿里云
    deb http://mirrors.aliyun.com/kali kali-rolling main non-free contrib
    deb-src http://mirrors.aliyun.com/kali kali-rolling main non-free contrib
    #清华大学
    #deb http://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main contrib non-free
    #deb-src https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main contrib non-free
    #浙大
    #deb http://mirrors.zju.edu.cn/kali kali-rolling main contrib non-free
    #deb-src http://mirrors.zju.edu.cn/kali kali-rolling main contrib non-free
    #东软大学
    #deb http://mirrors.neusoft.edu.cn/kali kali-rolling/main non-free contribp.kali.org/kali kali-rolling main non-free contrib
    #重庆大学
    #deb http://http.kali.org/kali kali-rolling main non-free contrib
    #deb-src http://http.kali.org/kali kali-rolling main non-free contrib

### 3、进行系统或工具的更新

    
    
    #进行系统或工具的更新（有丢丢就，先上把王者）
    #注：当出现正在设定软件包界面时，直接按tab+enter进行确认
    apt-get update && apt-get upgrade && apt-get dist-upgrade
    #礼貌性清除更新缓存
    apt-get clean

### 4、采用apt安装Docker

    
    
    #为什么采用apt安装？因为之后采用apt源安装Docker的其他组件时，新组件与已安装的Docker容器最为匹配。
    apt-get install docker docker-compose
    #或
    apt-get install docker.io

![](https://image.3001.net/images/20211105/1636110742_6185119660fe6368bc244.png!small)

### 5、检验Docker成功安装

    
    
    #启动docker服务
    service docker start
    #列出docker现有镜像
    docker images
    #运行hello-world镜像
    #但apt安装的docker没带有hello-world默认镜像呀，所以下面的命令不成功，它会帮你拉去该镜像下来
    docker run hello-world

![](https://image.3001.net/images/20211105/1636110743_61851197799bf2dee52fd.png!small)

![](https://image.3001.net/images/20211105/1636110744_61851198316270b7f9ddc.png!small)

# 0x02 Docker的其他配置

### 1、配置阿里云镜像加速

Docker建议配备一个镜像加速器来解决国内用户访问DockerHub缓慢的问题。此处笔者推荐使用阿里云的镜像加速器来优化，提升下载速度。

注：配置镜像加速器，仅针对Docker客户端版本大于 1.10.0 的用户

    
    
    #阿里云镜像加速器获取网址（需注册）：https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
    #镜像加速器网址写入/etc/docker/daemon.json文件(可能不存在)中
    vim /etc/docker/daemon.jsp
    #新建daemon.jsp文件
    touch /etc/docker/daemon.json
    #写入内容
    {
    	"registry-mirrors": ["https://xxx.mirror.aliyuncs.com"]
    }
    #退出daemon.jsp,并重启docker
    ESC --> :wq!
    systemctl restart docker
    #其他公开Docker镜像加速源（不需注册）
    https://docker.mirrors.ustc.edu.cn	#中科大
    http://hub-mirror.c.163.com/		#网易

![](https://image.3001.net/images/20211105/1636110745_618511990ccc5981d3153.png!small)

![](https://image.3001.net/images/20211105/1636110745_61851199b79e373379e4e.png!small)

![](https://image.3001.net/images/20211105/1636110746_6185119aa3bea7365c98e.png!small)

![](https://image.3001.net/images/20211105/1636110748_6185119ca7bd84dd1f234.png!small)

### 2、设置Docker开机自启

    
    
    #设置docker开机自启
    systemctl enable docker

![](https://image.3001.net/images/20211105/1636110749_6185119dbde74d5c73d8b.png!small)

# 0x03 Docker的简单使用

    
    
    #笔者以拉取 CVE-2017-7504 的漏洞环境为例。
    docker search testjboss    							#搜索漏洞环境
    docker pull testjboss/jboss							#拉取漏洞环境
    docker run -d -p 80:8080 testjboss/jboss:latest		#根据testjboss/jboss镜像创建并运行容器
    ifconfig																						#查看已运行容器ip
    #kali中，使用浏览器访问http://IP						#IP可为127.0.0.1
    docker ps																						#查看正在运行的容器
    docker exec -it e8f4844aabc1 /bin/bash				#进入容器(id:e8f4844aabc1)
    exit																								#退出容器到宿主机（容器不会停止运行）
    docker stop 3b41c0c08430							#关闭容器(id唯一标识，建议使用id)

![](https://image.3001.net/images/20211105/1636110750_6185119e65e0ae1ee9905.png!small)

![](https://image.3001.net/images/20211105/1636110751_6185119f470cd271a3692.png!small)

![](https://image.3001.net/images/20211105/1636110753_618511a1307946ffe24a0.png!small)

![](https://image.3001.net/images/20211105/1636110754_618511a248a3e7e5db8d3.png!small)

# 0x04 Docker的常用命令

    
    
    #系统命令
    systemctl start docker				#启动docker
    systemctl stop docker				#停止docker
    systemctl restart docker			#重启docker
    systemctl enable docker				#设置docker开机自启
    #基本命令
    docker version						#查看docker版本
    docker info							#查看docker详细信息
    docker --help						#查看docker命令
    #镜像命令
    docker images						#查看docker镜像列表
    docker images -a					#列出本地所有镜像
    docker images --digests				#显示镜像的摘要信息
    docker search redis					#从Docker Hub上查找redis镜像
    docker pull redis					#从Docker Hub上下载redis镜像
    docker rmi 373f0984b070				#删除IMAGE ID 为373f0984b070的镜像
    #运行命令
    #-p 6379:6379	端口映射：前表示主机部分,后表示容器部分
    #-d	在后台运行容器（不进入终端）并打印容器ID/容器名
    #--name myredis表示自定义容器名为myredis
    docker run -d -p 6379:6379 --name myredis redis:latest		#根据镜像创建并运行容器
    #容器命令
    docker container ls 或 docker ps				#查看正在运行的容器
    docker container ls -a 或 docker ps -a			#列出所有容器
    docker container start 容器ID 或 容器名称		#启动容器
    docker start 容器ID 或 容器名称					#启动容器
    docker container stop 容器ID 或 容器名称			#停止容器
    docker stop 容器ID 或 容器名称					#停止容器
    docker container rm 容器ID 或 容器名称			#删除容器
    docker rm 容器ID 或 容器名称						#删除容器
    docker container logs -f 容器ID 或 容器名称		#查看容器日志
    docker exec -it name /bin/bash 					#进入name（容器名/id）中开启交互式的终端，exit退出

# 0x05 docker —help中文译解

    
    
    Usage:
    docker [OPTIONS] COMMAND [arg...]
           docker daemon [ --help | ... ]
           docker [ --help | -v | --version ]
    A
    self-sufficient runtime for containers.
    
    Options:
      --config=~/.docker              Location of client config files  #客户端配置文件的位置
      -D, --debug=false               Enable debug mode  #启用Debug调试模式
      -H, --host=[]                   Daemon socket(s) to connect to  #守护进程的套接字（Socket）连接
      -h, --help=false                Print usage  #打印使用
      -l, --log-level=info            Set the logging level  #设置日志级别
      --tls=false                     Use TLS; implied by--tlsverify  #
      --tlscacert=~/.docker/ca.pem    Trust certs signed only by this CA  #信任证书签名CA
      --tlscert=~/.docker/cert.pem    Path to TLS certificate file  #TLS证书文件路径
      --tlskey=~/.docker/key.pem      Path to TLS key file  #TLS密钥文件路径
      --tlsverify=false               Use TLS and verify the remote  #使用TLS验证远程
      -v, --version=false             Print version information and quit  #打印版本信息并退出
    Commands:
        attach    Attach to a running container  #当前shell下attach连接指定运行镜像
        build     Build an image from a Dockerfile  #通过Dockerfile定制镜像
        commit    Create a new image from a container's changes  #提交当前容器为新的镜像
        cp    	  Copy files/folders from a container to a HOSTDIR or to STDOUT  #从容器中拷贝指定文件或者目录到宿主机中
        create    Create a new container  #创建一个新的容器，同run 但不启动容器
        diff      Inspect changes on a container's filesystem  #查看docker容器变化
        events    Get real time events from the server#从docker服务获取容器实时事件
        exec      Run a command in a running container#在已存在的容器上运行命令
        export    Export a container's filesystem as a tar archive  #导出容器的内容流作为一个tar归档文件(对应import)
        history   Show the history of an image  #展示一个镜像形成历史
        images    List images  #列出系统当前镜像
        import    Import the contents from a tarball to create a filesystem image  #从tar包中的内容创建一个新的文件系统映像(对应export)
        info      Display system-wide information  #显示系统相关信息
        inspect   Return low-level information on a container or image  #查看容器详细信息
        kill      Kill a running container  #kill指定docker容器
        load      Load an image from a tar archive or STDIN  #从一个tar包中加载一个镜像(对应save)
        login     Register or log in to a Docker registry#注册或者登陆一个docker源服务器
        logout    Log out from a Docker registry  #从当前Docker registry退出
        logs   	  Fetch the logs of a container  #输出当前容器日志信息
        pause     Pause all processes within a container#暂停容器
        port      List port mappings or a specific mapping for the CONTAINER  #查看映射端口对应的容器内部源端口
        ps    	  List containers  #列出容器列表
        pull      Pull an image or a repository from a registry  #从docker镜像源服务器拉取指定镜像或者库镜像
        push      Push an image or a repository to a registry  #推送指定镜像或者库镜像至docker源服务器
        rename    Rename a container  #重命名容器
        restart   Restart a running container  #重启运行的容器
        rm    	  Remove one or more containers  #移除一个或者多个容器
        rmi    	  Remove one or more images  #移除一个或多个镜像(无容器使用该镜像才可以删除，否则需要删除相关容器才可以继续或者-f强制删除)
        run   	  Run a command in a new container  #创建一个新的容器并运行一个命令
        save      Save an image(s) to a tar archive#保存一个镜像为一个tar包(对应load)
        search    Search the Docker Hub for images  #在docker
    hub中搜索镜像
        start     Start one or more stopped containers#启动容器
        stats     Display a live stream of container(s) resource usage statistics  #统计容器使用资源
        stop      Stop a running container  #停止容器
        tag       Tag an image into a repository  #给源中镜像打标签
        top       Display the running processes of a container #查看容器中运行的进程信息
        unpause   Unpause all processes within a container  #取消暂停容器
        version   Show the Docker version information#查看容器版本号
        wait      Block until a container stops, then print its exit code  #截取容器停止时的退出状态值

# 0x06 后记

通过查找资料，对Docker的理解又加深了，我心甚慰，喜欢这样的自己。 --涂寐

# 0x07 知识链接

> [kali下对Docker的详细安装_柠鹿的轨迹-> CSDN博客](https://blog.csdn.net/weixin_46318141/article/details/121168812)
>
> [两小时入门
> Docker（快速入门docker）](https://mp.weixin.qq.com/s?__biz=MzI2NjY5NzI0NA==&mid=2247503927&idx=4&sn=965bfa949efabcdc00623846b5430c54&chksm=ea88bf44ddff365281a99dabc1ce4045c2e4a1a464767cc41157e5402016c4ddbd1598d4e25b&mpshare=1&scene=23&srcid=1104UFEN08kUe8zc4TN8L1tK&sharer_sharetime=1636022562934&sharer_shareid=f392cc266ef9fa5f3024edf5fd5135ee#rd
> "两小时入门 Docker（快速入门docker）")
>
> [工具篇|kali
> linux中docker安装及应用﻿](https://mp.weixin.qq.com/s?__biz=Mzg3OTU4MDQ0Nw==&mid=2247484156&idx=1&sn=ebcc8f7c1659f67c00b02795e1d0d95b&chksm=cf03068cf8748f9aa6d677a9cdc25618cc6a1fabaa942b4561f08981565bdb084925109d218a&mpshare=1&scene=23&srcid=11045CxASpR3mALNpaNPImCt&sharer_sharetime=1636022780005&sharer_shareid=f392cc266ef9fa5f3024edf5fd5135ee#rd
> "工具篇|kali linux中docker安装及应用")

