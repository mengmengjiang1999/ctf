原创： Lee2dog 合天智汇

## Docker快速入门  

## 0、环境构建  

![v2-c9b3f682846c671e59c066550b7091a6_hd.j](https://pic4.zhimg.com/80/v2-c9b3f682846c671e59c066550b7091a6_hd.jpg)

虚拟机下载地址：

https://sourceforge.net/projects/defcon-26-container-security/

下载完，导入虚拟机就能用了。（VirtualBox或VMware都可以）

账号和登录信息在描述信息中可用看到

![v2-2425fac1b392b2e5a168e25cc4614d5b_hd.j](https://pic2.zhimg.com/80/v2-2425fac1b392b2e5a168e25cc4614d5b_hd.jpg)

可用使用SSH软件登录到机器进行操作

### 1、Docker基础  

> 1.1 简介  
>

容器是一个标准的软件单元，它将代码及其所有依赖打包，以便应用程序从一个计算环境快速可靠地运行到另一个计算环境。Docker容器镜像是一个轻量级，独立的可执行软件包，包含运行应用程序所需的一切：代码，运行时，系统工具，系统库和设置。容器镜像在运行时成为容器，在Docker容器的情况下-镜像在Docker
Engine上运行时成为容器。适用于基于Linux和Windows的应用程序，无论基础架构如何，容器化软件都将始终运行相同。容器将软件与其环境隔离开来，并确保它可以统一工作，尽管开发和演示之间存在差异。

> 1.2 运行你的第一个docker 容器  
>

student@debian:~$ docker run hello-world Hello from Docker!This message shows
that your installation appears to be working correctly.

当你执行 docker run命令的时候发生了什么：

1、Docker引擎会检查镜像是否存在

2、如果不存在，则会从docker镜像仓库获取

3、如果镜像存在，则会直接运行一个容器

> 1.3 Docker是如何工作的  
>

Docker是实现容器built、shipped和run的程序

Docker引擎使用Linux内核的namespace和control groups

![v2-48c446bf901a6d5dbd9e41ba5c59f9fb_hd.j](https://pic3.zhimg.com/80/v2-48c446bf901a6d5dbd9e41ba5c59f9fb_hd.jpg)

图片来源： https://docs.docker.com/engine/docker-overview/

> 1.4 名词解释  
>

Docker Images

包含只读的OS，库和应用程序

任何人都可以创建docker镜像

镜像可以存储在公共镜像仓库或私有镜像仓库

Docker Container

由镜像创建的具有可写层的有状态实例

容器包含运行应用程序所需的所有内容

基于一个或多个镜像

Docker Registry

存储镜像的仓库

Docker Hub

公共docker镜像仓库

![v2-a03e7701ddd56d268ff146a357908879_hd.j](https://pic1.zhimg.com/80/v2-a03e7701ddd56d268ff146a357908879_hd.jpg)

合天网安实验室实验推荐：centos7上体验docker（复制链接做实验！）

![v2-313889506c411704be2271d47883294f_hd.j](https://pic2.zhimg.com/80/v2-313889506c411704be2271d47883294f_hd.jpg)

http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015050611052100001

> 1.5 Docker Search  
>

你可以通过docker search命令从docker hub里面搜索想要的镜像

student@debian:~$ docker search wpscanNAME DESCRIPTION STARS OFFICIAL
AUTOMATEDwpscanteam/wpscan WPScan 50 [OK]doctorcmd/wpscan Kali Linux 2.0 with
working wpscan 1 clevertodayinc/wpscan-server A web server running WP Scan and
rendering t… 1 [OK]opendevsecops/wpscan 1 [OK]alferez/wpscan Scan Wordpress
Vulnerability 0 [OK]

> 1.6 Docker run  
>

运行一个docker容器

示例：

通过执行一条命令的方式运行一个ubuntu容器

student@debian:~$ docker run ubuntu:latest echo "Welcome to Ubuntu"Welcome to
Ubuntu

通过执行一个可交互的bash shell来运行一个容器

student@debian:~$ docker run --name container01 -it ubuntu:latest
/bin/bashroot@d4d6f90ee585:/# iduid=0(root) gid=0(root)
groups=0(root)root@d4d6f90ee585:/# exitexitstudent@debian:~$

> 1.7 查找/管理容器  
>

列出所有运行中的容器：docker ps

student@debian:~$ docker psCONTAINER ID IMAGE COMMAND CREATED STATUS PORTS
NAMESf707ebc6694b registry:2 "/entrypoint.sh /etc…" 15 months ago Up 10 hours
0.0.0.0:5000->5000/tcp registrystudent@debian:~$

列出所有容器：docker ps -a

student@debian:~$ docker ps -aCONTAINER ID IMAGE COMMAND CREATED STATUS PORTS
NAMESd4d6f90ee585 ubuntu:latest "/bin/bash" 2 minutes ago Exited (0) 2 minutes
ago container01e91e3a6fef51 ubuntu:latest "echo 'Welcome to Ub…" 5 minutes ago
Exited (0) 5 minutes ago thirsty_liskov58ad549bbdd9 hello-world "/hello" 35
minutes ago Exited (0) 35 minutes ago nifty_roentgenf707ebc6694b registry:2
"/entrypoint.sh /etc…" 15 months ago Up 10 hours 0.0.0.0:5000->5000/tcp
registrystudent@debian:~$

> 1.8 列出docker 镜像  
>

使用docker images

student@debian:~$ docker imagesREPOSITORY TAG IMAGE ID CREATED SIZEcustom-htop
latest 5aed0e1b7a7b 15 months ago 7.21MBr.j3ss.co/amicontained latest
da636cbc14c6 15 months ago 2.09MBjess/htop latest a728567cf176 15 months ago
7.21MBwordpress latest 5db349700f3a 15 months ago 408MBmysql 5.7 75576f90a779
15 months ago 372MBportainer/portainer latest 6827bc26a94d 15 months ago
58.5MBubuntu latest 735f80812f90 15 months ago 83.5MBnginx alpine 36f3464a2197
15 months ago 18.6MBnginx latest c82521676580 15 months ago 109MBhello-world
latest 2cb0d9787c4d 16 months ago 1.85kBregistry 2 b2b03e9146e1 16 months ago
33.3MBalpine latest 11cd0b38bc3c 16 months ago 4.41MB

看完上面的内容，我们的实验推荐又来了：docker之容器的管理

![v2-1186596183e2d4373718a8c056a1b8b1_hd.j](https://pic2.zhimg.com/80/v2-1186596183e2d4373718a8c056a1b8b1_hd.jpg)

http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015052011243700001

> 1.9 以后台模式运行容器  
>

以后台的方式运行一个 alpine 容器：-d参数

student@debian:~$ docker run --name ping_container -d alpine:latest ping
127.0.0.1 -c
5004020fd195d584dcccaa55b3a8e6c56380b18ec8b6a4d0aa10d8173d924c7327

查看容器日志（标准输出）：docker logs -f

student@debian:~$ docker logs -f ping_containerPING 127.0.0.1 (127.0.0.1): 56
data bytes64 bytes from 127.0.0.1: seq=0 ttl=64 time=0.075 ms64 bytes from
127.0.0.1: seq=1 ttl=64 time=0.051 ms64 bytes from 127.0.0.1: seq=2 ttl=64
time=0.048 ms64 bytes from 127.0.0.1: seq=3 ttl=64 time=0.063 ms64 bytes from
127.0.0.1: seq=4 ttl=64 time=0.050 ms

运行一个 Nginx 容器并访问这个服务

student@debian:~$ docker run -d --name nginxserver -p 7777:80
nginx:alpinee54554f154e2f083416ad25290979895bb0f38aac68a0c62ff01c6b3a5ee77f5student@debian:~$

在宿主机上通过映射的端口访问Nginx服务

student@debian:~$ curl localhost:7777<!DOCTYPE html><html><head><title>Welcome
to nginx!</title>

在容器内通过IP和端口访问服务

student@debian:~$ docker exec -it nginxserver sh/ # ip a s1: lo:
<LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 inet 127.0.0.1/8 scope
host lo valid_lft forever preferred_lft forever19: eth0@if20:
<BROADCAST,MULTICAST,UP,LOWER_UP,M-DOWN> mtu 1500 qdisc noqueue state UP
link/ether 02:42:ac:11:00:03 brd ff:ff:ff:ff:ff:ff inet 172.17.0.3/16 brd
172.17.255.255 scope global eth0 valid_lft forever preferred_lft forever/ #
curl 172.17.0.3:80/ # exitstudent@debian:~$ curl 172.17.0.3:80<!DOCTYPE
html><html><head><title>Welcome to nginx!</title>

2、Docker管理

学习一些命令更好的管理镜像和容器

> 2.1 Inspecting container or images  
>

docker inspect : 获取容器/镜像的元数据。

示例：

获取镜像的元信息：

student@debian:~$ docker inspect nginx:alpine[ { "Id":
"sha256:36f3464a21975e5779d081a9e8a78a024c549d1895fc9981d6bd8b67075ebd7b",
"RepoTags": [ "nginx:alpine" ], "RepoDigests": [
"nginx@sha256:23e4dacbc60479fa7f23b3b8e18aad41bd8445706d0538b25ba1d575a6e2410b"
], "Parent": "", "Comment": "", "Created": "2018-07-24T17:23:57.546619301Z",
"Container":
"81a6e6f4720cfd043878819d52287c4c1ff8c225d45853196781e5302140915a",
"ContainerConfig": { "Hostname": "81a6e6f4720c",

获取容器的元信息：

student@debian:~$ docker inspect nginxserver[ { "Id":
"e54554f154e2f083416ad25290979895bb0f38aac68a0c62ff01c6b3a5ee77f5", "Created":
"2019-11-15T02:30:31.620961201Z", "Path": "nginx", "Args": [ "-g", "daemon
off;" ], "State": { "Status": "running", "Running": true,

> 2.2 Docker history  
>

docker history <image name>：查看镜像的创建历史记录

student@debian:~$ docker history nginx:alpineIMAGE CREATED CREATED BY SIZE
COMMENT36f3464a2197 15 months ago /bin/sh -c #(nop) CMD ["nginx" "-g" "daemon…
0B <missing> 15 months ago /bin/sh -c #(nop) STOPSIGNAL [SIGTERM] 0B <missing>
15 months ago /bin/sh -c #(nop) EXPOSE 80/tcp 0B <missing> 15 months ago
/bin/sh -c #(nop) COPY file:1d1ac3b9a14c94a7… 1.09kB <missing> 15 months ago
/bin/sh -c #(nop) COPY file:af94db45bb7e4b8f… 643B <missing> 15 months ago
/bin/sh -c GPG_KEYS=B0F4253373F8F6F510D42178… 14.4MB <missing> 15 months ago
/bin/sh -c #(nop) ENV NGINX_V

> 2.3 Stopping and removing container  
>

docker stop <container_id/container_name>：停止一个运行中的容器

docker rm <container_id/container_name>：删除一个停止的容器

示例：

先运行一个容器：

student@debian:~$ docker run --name nginx01 -d
nginx:alpinec6f43bf3858c42a776446c9d723b6067e4eb25293e7a3157aaec95210a317d3bstudent@debian:~$
docker psCONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMESc6f43bf3858c
nginx:alpine "nginx -g 'daemon of…" 10 seconds ago Up 10 seconds 80/tcp
nginx01

停止它：

student@debian:~$ docker stop nginx01nginx01student@debian:~$ docker ps
-aCONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMESc6f43bf3858c
nginx:alpine "nginx -g 'daemon of…" 24 seconds ago Exited (0) 3 seconds ago
nginx01

删除它：

student@debian:~$ docker rm nginx01nginx01student@debian:~$ docker ps
-aCONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMESstudent@debian:~$

### 3、 Docker 数据卷和网络  

> 3.1 使用docker-compose配置一个wordpress站点  
>

Compose 是用于定义和运行多容器 Docker 应用程序的工具。你可以方便快捷的使用Compose配置你的应用服务。

示例：

使用docker-compose这一个wordpress站点

student@debian:~$ cd /opt/wordpress/student@debian:/opt/wordpress$ cat docker-compose.yml #查看docker-compose配置文件version: '3.3' services: db: image: mysql:5.7
volumes: - db_data:/var/lib/mysql restart: always environment:

在docker-compose.yml配置文件中详细描述了创建容器所需的各种配置和参数。

启动它：

student@debian:/opt/wordpress$ docker-compose up -dCreating wordpress_db_1 ...
doneCreating wordpress_wordpress_1 ... donestudent@debian:/opt/wordpress$

访问这个服务：http://student-VMip:8000

![v2-7ed6db5f052b79a664d7ce1f74b8dcec_hd.j](https://pic4.zhimg.com/80/v2-7ed6db5f052b79a664d7ce1f74b8dcec_hd.jpg)

> 3.2 检查docker 数据卷  
>

docker volume ls：列出docker数据卷

student@debian:/opt/wordpress$ docker volume lsDRIVER VOLUME NAMElocal
1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67local
9159b373c0d298cb2fdc2bfe1c2f650e8a115d8c54fa4c94106b8f9405c20526local
d9af2c81173f9a49ffa343d8f195bc03578cff8b5690c498acbb9bedfc0168eblocal
wordpress_db_data

基于docker三步搭建WordPress：

http://www.hetianlab.com/expc.do?ec=ECID172.19.104.182015070915180900001

> 3.3 检查docker网络  
>

docker network ls：列出docker网络

student@debian:/opt/wordpress$ docker network lsNETWORK ID NAME DRIVER
SCOPEad816ae1f31a bridge bridge local208a8324cfc4 docker_gwbridge bridge
localf2e1e0c88ec1 host host local2035d107fc5a none null local068b477b3311
wordpress_default bridge localstudent@debian:/opt/wordpress$

至于docker的网络类型可以自己去官网看文档

> 3.4 图形化管理Docker  
>

使用portainer管理Docker

Portainer 是一种简单的 Docker 管理解决方案。通过 Portainer web 用户界面轻松管理您的 Docker主机和 Docker集群。

示例：

启动：

student@debian:~$ docker run -d -p 9000:9000 --name portainer \> \--restart
always -v /var/run/docker.sock:/var/run/docker.sock \> -v /opt/portainer:/data
portainer/portainerb1e0815d66e07b6f4923c6dbe8d826d19b172575696acaba4b624ec469aad65cstudent@debian:~$

访问：http://student-VMip:9000

![v2-1ee1b956e26afe71aa6595eeac3f8e3b_hd.j](https://pic1.zhimg.com/80/v2-1ee1b956e26afe71aa6595eeac3f8e3b_hd.jpg)

第一次访问要自己设置一个密码，然后点Create user

选择管理本地容器

![v2-d0cc0a075acf1ab32393f90345a15f3b_hd.j](https://pic3.zhimg.com/80/v2-d0cc0a075acf1ab32393f90345a15f3b_hd.jpg)

然后就能对镜像，容器进行管理了

![v2-9d9ee6382904712b86c34f4ca0bde5c6_hd.j](https://pic1.zhimg.com/80/v2-9d9ee6382904712b86c34f4ca0bde5c6_hd.jpg)

### References  

DEF CON 26 Workshop - Attacking & Auditing Docker Containers Using Open Source
https://github.com/appsecco/defcon-26-workshop-attacking-and-auditing-docker-containers

实验推荐：docker之使用网络

  
实验:Docker之使用网络(合天网安实验室)​www.hetianlab.com![图标](https://pic2.zhimg.com/v2-0eee1371377026272639d8b2fd330473_180x120.jpg)

### 备注：  

本文由作者原创翻译

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

