
    只有奋斗才能改变命运！

## KALI安装Docker+Vulhub

在学习网络安全的过程中，少不了的就是做漏洞复现，而漏洞复现一般比较常用的方式就是使用docker-vulhub进行环境搭建，我近期也遇到了这个问题，但是网上的教程特别混乱，根本起不到帮助作用，即使有可以看的，也不是很完整，所以我写了一篇关于安装docker和vulhub的总结

### Docker简介

Docker是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流行的Linux或Windows机器上，也可以实现虚拟化。容器是完全使用沙箱机制，互相之间不会有任何接口。Docker集装箱化的有点：灵活、轻量级、便携式、可扩展性、可堆叠。个人理解为就是Docker就是一个容器，或者说一个’盒子‘，里面可以放一些别人搭建好的环境，进行操作。

### Docker-compose简介

docker-compose是一个用python写的一个docker容器管理工具，可以更加方便的对docker容器进行管理，可以一键启动多个容器

### Vulhub简介

vulhub是一个基于docker和docker-compose的漏洞环境集合，进入对应目录并执行一条语句即可启动一个全新的漏洞环境，让漏洞复现会变得很简单。

## Docker安装

### 安装https协议、CA证书、dirmngr

    
    
    apt-get update  
    ​  
    apt-get install -y apt -transport-https ca-certificates  
    ​  
    apt-get install dirmngr

![1](https://image.3001.net/images/20210728/1627485865_610176a915aeab7697143.png!small)

![2](https://image.3001.net/images/20210728/1627485866_610176aae99d08194fd2c.png!small)

![3](https://image.3001.net/images/20210728/1627485868_610176ac5938c57d176d2.png!small)

### 添加GPG密钥并添加更新源

    
    
    curl -fsSL https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/gpg | sudo apt-key add -  
    ​  
    echo 'deb https://mirrors.tuna.tsinghua.edu.cn/docker-ce/linux/debian/ buster stable' | sudo tee /etc/apt/sources.list.d/docker.list

![4](https://image.3001.net/images/20210728/1627485869_610176ada87a80367efb3.png!small)

成功添加GPG密钥并添加更新源

### 系统更新以及安装docker

    
    
    apt-get update  
    ​  
    apt install docker-ce

![5](https://image.3001.net/images/20210728/1627485871_610176af021bba5d43ed2.png!small)

![6](https://image.3001.net/images/20210728/1627485872_610176b068bc18d19a621.png!small)

### 启动docker服务器

    
    
    service docker start

![7](https://image.3001.net/images/20210728/1627485873_610176b18f8e7a58bb550.png!small)

### 安装compose

    
    
    apt install docker-compose

![8](https://image.3001.net/images/20210728/1627485874_610176b2c35076cc7c20e.png!small)

### docker安装测试

    
    
    docker version    查看docker的版本信息  
    ​  
    docker images    查看拥有的images  
    ​  
    docker ps    查看docker container

![9](https://image.3001.net/images/20210728/1627485876_610176b4644f5a2eab6d6.png!small)

docker到此安装完成

## Docker安装sqli-labs

很多同学入门刷sqli-labs来学习sql注入漏洞，但是sqli-labs刷到30关左右的时候就需要使用linux下的环境了，windows本地搭建的环境会出问题，所以在此顺带讲解使用docker安装sqli-labs

    
    
    docker search     sqli-labs  查找sqli-labs镜像  
    docker pull     acgpiano/sqli-labs  拉取镜像到本地  
    docker images  查看已有的镜像  
    docker run -dt --name sqli -p     80:80 --rm acgpiano/sqli-labs  
    -dt  让其在后台运行  
    --name  给其命名  
    -p  本地端口：docker中的端口是将docker的端口映射到本地端口  
    --rm  当其关闭后将删除开启的资源  
    docker ps -a 显示容器container容器的id image 命令 端口等信息  
    docker exec -it （id号）     /bin/bash  进入id号的shell

## Docker的基本使用

    
    
    docker images    查看存在的镜像  
    docker image rm <id>    删除镜像  
    docker run -dt --name sqli -p 80:80 --rm acgpiano/sqli-labs    运行存在的镜像  
    docker exec -it <container ID> /bin/bash    进入运行中的容器  
    docker run -it --rm ubuntu /bin/bash    运行存在的镜像，并以交互的方式进入容器，运行完删除容器  
    docker ps    docker container ls    查看运行中的容器  
    docker stop <container ID>    停止指定的容器，不指定为停止所有容器  
    docker rm    删除所有的容器  
    docker container [stop/start/restart]    停止/开启/重启容器  
    docker container kall <container ID>    强制停止容器  
    docker commit -p <container ID> container-backup    创建Docker的快照  
    ​  
    把宿主机文件拷到容器里面  
    docker cp 要拷贝的文件路径 容器名: 要拷贝到容器里面对应的路径  
    ​  
    容器里面拷文件到主机  
    docker cp 容器名: 要拷贝的文件在容器中的路径 要拷贝到宿主机器的响应路径

## Docker配置镜像加速

默认的docker镜像下载慢，这里使用阿里云的镜像加速

首先访问阿里云（没有账号的注册一个），进入控制台，找到产品与服务中的容器镜像服务，进入其中的镜像加速器

![12](https://image.3001.net/images/20210728/1627485877_610176b5a371769d48b19.png!small)

    
    
    sudo mkdir -p /etc/docker  
    sudo tee /etc/docker/daemon.json <<-'EOF'  
    {  
    "registry-mirrors": ["自己的加速器地址"]  
    }  
    EOF  
    sudo systemctl daemon-reload  
    sudo systemctl restart docker

![13](https://image.3001.net/images/20210728/1627485878_610176b69a239a5ef195f.png!small)

## 安装vulhub

### 下载vulhub

<https://github.com/vulhub/vulhub>

![10](https://image.3001.net/images/20210728/1627485879_610176b7ced7b782c115e.png!small)

![11](https://image.3001.net/images/20210728/1627485881_610176b90d966f84bacd4.png!small)

    
    
    git clone https://github.com/vulhub/vulhub.git

![14](https://image.3001.net/images/20210728/1627485882_610176ba5d999c8e076dd.png!small)

下载完成后，进入目录下

    
    
    cd vulhub

![15](https://image.3001.net/images/20210728/1627485884_610176bcddc74d309f06d.png!small)

### 拉取漏洞环境

可以看到很多子文件夹，就是不同的漏洞

此处举例搭建struts2漏洞环境

    
    
    cd struts2

![16](https://image.3001.net/images/20210728/1627485887_610176bf9148c42c55a6d.png!small)

举例一个S2-057

    
    
    cd s2-057

![17](https://image.3001.net/images/20210728/1627485888_610176c097874657ca087.png!small)

然后执行命令，开启struts2-057漏洞

    
    
    sudo docker-compose up -d

![18](https://image.3001.net/images/20210728/1627485889_610176c1c1586549e14ca.png!small)

    
    
    sudo docker ps    查看运行中的容器环境

![19](https://image.3001.net/images/20210728/1627485891_610176c30ff8d82511045.png!small)

![20](https://image.3001.net/images/20210728/1627485891_610176c3f1688d3081239.png!small)

### 访问漏洞环境

访问 ip地址:8080

![21](https://image.3001.net/images/20210728/1627485893_610176c509bd3bc770f0c.png!small)

注意：如果没有回显可以加一些参数比如index

![22](https://image.3001.net/images/20210728/1627485894_610176c623d8c73e80640.png!small)

环境运行结束后要及时停止进程

    
    
    docker stop （id号）

![23](https://image.3001.net/images/20210728/1627485895_610176c72e063e075ebbb.png!small)

如果想要再次执行，可以输入

docker run -d -p 8080:8080 medicean/vulapps:s_struts2_s2-057

至此，漏洞复现环境就全部搭建完成

