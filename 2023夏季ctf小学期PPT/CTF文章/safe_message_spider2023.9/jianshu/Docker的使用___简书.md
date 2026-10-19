Docker的使用

[ 可能性之兽](https://www.jianshu.com/u/7850941fa1a4)关注赞赏支持

# Docker的使用

>
> Docker其实就是一种封装的迷你的操作系统，比如一个软件需要依赖很多东西才能运行，那么就可以把这个软件的整个依赖系统一起打包进一个docker。由于docker里面已经封装了这个软件的很多操作依赖，从而在迁移到其他系统给别人用的时候而无需考虑新的操作环境的差别，所以让别人用就很方便。

> 当然docker从出现到现在起码有十年了，所以也有一些新的可以替代docker的，减少了docker的一些缺陷的新的容器方式出现。  
>  [2022 年要考虑的 7 种 Docker 替代方案_开源_Sudip
> Sengupta_InfoQ精选文章](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.infoq.cn%2Farticle%2Fggimepmcvdqw4eos2cig)

### 安装

[CentOS Docker 安装 | 菜鸟教程
(runoob.com)](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.runoob.com%2Fdocker%2Fcentos-
docker-install.html)

### 使用

[Docker 容器使用 | 菜鸟教程
(runoob.com)](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.runoob.com%2Fdocker%2Fdocker-
container-usage.html)

    
    
    (base) [lp@localhost run]$ docker
    
    Usage:  docker COMMAND
    
    A self-sufficient runtime for containers
    
    Options:
          --config string      Location of client config files (default "/home/maolp/.docker")
      -D, --debug              Enable debug mode
          --help               Print usage
      -H, --host list          Daemon socket(s) to connect to (default [])
      -l, --log-level string   Set the logging level ("debug", "info", "warn", "error", "fatal") (default "info")
          --tls                Use TLS; implied by --tlsverify
          --tlscacert string   Trust certs signed only by this CA (default "/home/maolp/.docker/ca.pem")
          --tlscert string     Path to TLS certificate file (default "/home/maolp/.docker/cert.pem")
          --tlskey string      Path to TLS key file (default "/home/maolp/.docker/key.pem")
          --tlsverify          Use TLS and verify the remote
      -v, --version            Print version information and quit
    
    Management Commands:
      container   Manage containers
      image       Manage images
      network     Manage networks
      node        Manage Swarm nodes
      plugin      Manage plugins
      secret      Manage Docker secrets
      service     Manage services
      stack       Manage Docker stacks
      swarm       Manage Swarm
      system      Manage Docker
      volume      Manage volumes
    
    Commands:
      attach      Attach to a running container
      build       Build an image from a Dockerfile
      commit      Create a new image from a container's changes
      cp          Copy files/folders between a container and the local filesystem
      create      Create a new container
      diff        Inspect changes on a container's filesystem
      events      Get real time events from the server
      exec        Run a command in a running container
      export      Export a container's filesystem as a tar archive
      history     Show the history of an image
      images      List images
      import      Import the contents from a tarball to create a filesystem image
      info        Display system-wide information
      inspect     Return low-level information on Docker objects
      kill        Kill one or more running containers
      load        Load an image from a tar archive or STDIN
      login       Log in to a Docker registry
      logout      Log out from a Docker registry
      logs        Fetch the logs of a container
      pause       Pause all processes within one or more containers
      port        List port mappings or a specific mapping for the container
      ps          List containers
      pull        Pull an image or a repository from a registry
      push        Push an image or a repository to a registry
      rename      Rename a container
      restart     Restart one or more containers
      rm          Remove one or more containers
      rmi         Remove one or more images
      run         Run a command in a new container
      save        Save one or more images to a tar archive (streamed to STDOUT by default)
      search      Search the Docker Hub for images
      start       Start one or more stopped containers
      stats       Display a live stream of container(s) resource usage statistics
      stop        Stop one or more running containers
      tag         Create a tag TARGET_IMAGE that refers to SOURCE_IMAGE
      top         Display the running processes of a container
      unpause     Unpause all processes within one or more containers
      update      Update configuration of one or more containers
      version     Show the Docker version information
      wait        Block until one or more containers stop, then print their exit codes
    
    Run 'docker COMMAND --help' for more information on a command.
    
    

检验docker是否安装成功。  
启动docker服务

    
    
    service docker start
    

列出已经存在的docker镜像

    
    
    docker images
    

运行hello-world镜像

    
    
    docker run hello-world
    

镜像加速网址写入daemon.json文件中,如果不存在就新建此文件。

    
    
    vim /etc/docker/daemon.json
    #新建
    # touch /etc/docker/daemon.json
    
    systemctl restart docker
    
    
    
    docker info
    

设置docker开启自启动

    
    
    systemctl enable docker
    

#### docker的常用命令

    
    
    systemctl start docker
    systemctl restart docker
    systemctl stop docker
    systemctl enable docker #设置docker开机自启
    

### 基本命令

    
    
    docker info
    docker version
    docker --help
    

### 镜像命令

    
    
    docker images #查看docker镜像列表
    docker images -a #列出本地所有镜像
    docker images --digests #显示镜像的摘要信息
    docker search redis #从docker hub上搜索redis镜像
    docker pull redis #从docker hub上下载redis镜像
    docker rmi 123456 #删除image id为123456的镜像
    

### 运行命令

    
    
    docker run -d -p 1234:5678 --name myredis redis:latest #根据镜像创建并运行容器
    -p 1234:5678 #端口映射：前面为主机部分，后面为容器部分
    -d #在后台运行容器并打印容器名称/容器id
    --name myredis #表示自定义容器名称为myredis
    

### 容器命令

    
    
    docker container ls 或者 docker ps #查看正在运行的容器
    docker container ls -a 或者 docker ps -a #列出所有容器
    docker container start 容器ID 或者 容器名称 #启动容器
    docker start 容器ID 或者 容器名称
    docker container stop 容器ID 或者 容器名称 #停止容器
    docker stop 容器ID 或者 容器名称
    docker container rm 容器ID 或者 容器名称 #删除容器
    docker rm 容器ID 或者 容器名称
    docker container logs -f 容器ID 或者 容器名称 #查看容器日志
    docker exec -it name /bin/bash #进入name（容器ID或者容器名称）中开启交互式终端，使用exit退出
    
    

#### 使用新的系统

    
    
    docker run -t -i ubuntu:14.04 /bin/bash
    exit ###退出
    docker stop 
    docker images
    docker rmi 13b66b487594 --force  ##强制删除
    docker images
    

[docker安装&使用教程
(qq.com)](https://links.jianshu.com/go?to=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FYShazEnOOof7GttV8qxQ2A)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [Docker使用](https://www.jianshu.com/p/8a21e9a85aa8)

Docker Docker简介 简介： Docker[docker.com] 是一个开源的应用容器引擎，基于 Go...

[doinb1517](https://www.jianshu.com/u/c908001878a5)阅读 362评论 0赞 1

  * [Docker使用教程](https://www.jianshu.com/p/291746f7535b)

■ 简介 Docker 是一个开源的应用容器引擎，基于 Go 语言并遵从 Apache2.0 协议开源。 Dock...

[枫子奉](https://www.jianshu.com/u/727718302c42)阅读 445评论 0赞 0

  * [Docker使用及部署CTF题目](https://www.jianshu.com/p/472af122bd32)

Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流...

[简言之_](https://www.jianshu.com/u/b55a93447b80)阅读 2,246评论 0赞 2

  * [mac 下docker使用](https://www.jianshu.com/p/1d7806cb8989)

1.参考链接 http://www.runoob.com/docker/docker-architecture.h...

[低调_0c1d](https://www.jianshu.com/u/5cf85e784a0a)阅读 1,758评论 2赞 1

  * [Linux服务器之二 : Docker使用lnmp镜像创建容器](https://www.jianshu.com/p/f2c9a265bb27)

1.获取镜像 安装docker之后 , 使用命令获取指定镜像, 这里使用的是duckll/lnmp更多docker...

[阿里里啊嘞嘞](https://www.jianshu.com/u/0c0a1009af51)阅读 457评论 0赞 0

 