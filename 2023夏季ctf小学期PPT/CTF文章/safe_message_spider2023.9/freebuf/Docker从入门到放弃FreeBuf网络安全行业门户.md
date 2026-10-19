本文将以比较简单的的方式让大家理解docker，以平时常用到的测试环境为主，从用开始，慢慢理解docker。

 **目录**

> 0x00 用docker进行漏洞测试
>
> 0x01 docker运行busybox
>
> 0x02 Docker 搭建运行apache-php环境
>
> 0x03 用Dockerfile自动化构建可ssh登陆的镜像
>
> 0x04 Docker搭建一个wordpress博客
>
> 0x05 Docker容器互联
>
> 0x06 Docker安全

##  **0x00 用docker进行漏洞测试**

vulhub是一个开源的漏洞环境靶场(膜拜p牛一波)

接下来我们用docker来搭建一个jboss反序列漏洞的环境吧。

准备：Docker Docke-compose

以上环境安装方法：[Docker安装](https://docs.docker.com/install/)[Docker-compose安装](https://docs.docker.com/compose/install/#install-compose)

什么？一开始就学这么难的？其实docker边用边学是比较合适的，用到什么学什么，没有必要从一大堆原理开始学。既然要学docker，那就先装一个啦，边学边用。

那接下来就开始吧，其实也就一条命令。

<https://raw.githubusercontent.com/vulhub/vulhub/master/jboss/CVE-2017-12149/docker-compose.yml>

复制如上链接，然后保存到文件docker-compose.yml，结果如下：![Docker从入门到放弃](https://image.3001.net/images/20180807/1533642903_5b698897dab51.png!small)接下来，我们只需要

    
    
    docker-compose up -d

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533644031_5b698cffae3dd.png!small)好了我们的靶场搭建完毕,访问localhost:8080

接下来就可以进行漏洞复现了，步骤见：

<https://github.com/vulhub/vulhub/blob/master/jboss/CVE-2017-12149/README.md>

##  **0x01 docker运行busybox**

接下来我们边搭建环境边学习简单的docker命令

Busybox是一个集成了三百多个最常用Linux命令和工具的软件，简单的cat ls
echo等命令都集成在内，当然也有很多复杂的命令，我们就先来试试使用docker安装一个busybox吧

  

    
    
    docker pull busybox
    

  

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533644399_5b698e6f4ea14.png!small)

好了，我们 从docker官方库中得到了一个镜像

可以通过 docker images 查看到id以及其他信息，这里可以看到busybox镜像大小只有1mb左右

那接下来我们用这个id为8c811b4aec35的busybox镜像运行一下命令吧

先用来看下ifconfig命令

  

    
    
    docker run 8c811b4aec35 ifconfig

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533646298_5b6995da10f32.png!small)

可以看到，docker使用busybox镜像创建了一个busybox容器，并且运行了我们的测试命令，而且docker运行的容器有自己的ip地址，这说明容器是一个相对独立的环境。

## 0x02 Docker 搭建运行apache-php环境

首先搜索下有哪些现成的apache-php环境

  

    
    
    docker search apache-php

这里我们选择别人已经构建好的start数目较多的镜像：eboraas/apache-php

  

  

    
    
    dockerpull eboraas/apache-php  
    

  

![1.png](https://image.3001.net/images/20180810/15338991293386.png!small)

部署完成还是用docker images查看我们pull到本地的镜像

  

    
    
    docker images

![2.png](https://image.3001.net/images/20180810/15338991534816.png!small)

接下来我们进入到id为1e9f5e13fb38的容器

和之前的命令有些区别，因为我们运行的是web服务，所以我们需要把容器内部端口映射出来这样我们才能用外部的浏览器访问它。

  

    
    
    docker run -itd -p 80:80 1e9f5e13fb38

  

好了，一个apache+php的容器就可以搭建成功，我们可以在上面搭建其他服务了。

我们可以在宿主机curl测试一下我们是否搭建成功(将容器放入后台可以使用ctrl p+q）

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533649099_5b69a0cb8c32d.png!small)

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533649243_5b69a15ba1f75.png!small)那我们php环境怎么样了呢？那就写一个phpinfo页面试试吧

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533649537_5b69a2811ff49.png!small)php页面创建好了，接下来我们需要将他放在docker容器的web根目录里，这里需要用到docker
cp命令

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533649784_5b69a378df45a.png!small)使用dockercp命令复制到容器的web根目录/var/www/html/，这里指定容器我直接简写了开头的标识
4c1

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533649841_5b69a3b15c6d6.png!small)

可以看到，环境已经搭建好了。

我们已经在容器内做了改动了，此时，如果我们停止容器，我们的改动将会消失，如果我们想保存容器，那么就需要将我们的容器提交成镜像。

首先用docker commit提交成新镜像

    
    
    docker commit -a “hayasec” -m "test.php" 4c1 haya/test

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533650646_5b69a6d6055a3.png!small)此时可以查看一下镜像id然后使用docker
save将镜像导出

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533651186_5b69a8f2a85dd.png!small)![Docker从入门到放弃](https://image.3001.net/images/20180807/1533651473_5b69aa11440c4.png!small)接下来我们可以将test.tar放到其他机器上，然后用docker
load命令就可以进行再次部署了。![Docker从入门到放弃](https://image.3001.net/images/20180807/1533651650_5b69aac297430.png!small)这里已经载入镜像了，我们可以用dockertag命令对docker镜像进行命名

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533652344_5b69ad780dc59.png!small)这时候有个小问题，之前我们运行了一个apache-php容器，现在我们已经不需要它了，所以我们用docker ps查看镜像id然后用docker stop 镜像id 来停止它。

##  **0x03 用Dockerfile自动化构建可ssh登陆的镜像**

Dockerfile是由一系列命令和参数构成的脚本，这些命令应用于基础镜像并最终创建一个新的镜像。

接下来就利用之前我们pull下来的apache-php镜像来制作一个可以ssh登陆的镜像吧

这里需要创建三个文件 Dockerfile run.sh sources163.txt，处于同级目录。

dockerfile如下内容如下：

    
    
    FROM eboraas/apache-php #设置基础镜像镜像
    MAINTAINER haya #指定作者
    COPY sources163.txt /etc/apt/sources.list #更换国内源
    RUN apt-get -y update
    RUN apt-get install -y openssh-server --force-yes #安装ssh服务
    RUN mkdir -p /root/.ssh #创建ssh目录
    ADD run.sh /run.sh #将run.sh添加到容器内
    RUN chmod 755 /run.sh
    EXPOSE 22 #为暴漏容器运行时的监听端口给外部
    EXPOSE 80
    EXPOSE 443
    CMD ["/run.sh"] #容器启动时要运行的命令
    

run.sh文件内容如下：

    
    
    #!/bin/bash
    service ssh start
    

sources163.txt内容如下：

    
    
    deb http://mirrors.163.com/ubuntu/ trusty main restricted universe multiverse
    deb http://mirrors.163.com/ubuntu/ trusty-security main restricted universe multiverse
    deb http://mirrors.163.com/ubuntu/ trusty-updates main restricted universe multiverse
    deb http://mirrors.163.com/ubuntu/ trusty-proposed main restricted universe multiverse
    deb http://mirrors.163.com/ubuntu/ trusty-backports main restricted universe multiverse
    deb-src http://mirrors.163.com/ubuntu/ trusty main restricted universe multiverse
    deb-src http://mirrors.163.com/ubuntu/ trusty-security main restricted universe multiverse
    deb-src http://mirrors.163.com/ubuntu/ trusty-updates main restricted universe multiverse
    deb-src http://mirrors.163.com/ubuntu/ trusty-proposed main restricted universe multiverse
    deb-src http://mirrors.163.com/ubuntu/ trusty-backports main restricted universe multiverse
    

然后利用这个dockerfile构建镜像

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533654044_5b69b41c06460.png!small)

镜像构建完毕后，可以看到：

![Docker从入门到放弃](https://image.3001.net/images/20180807/1533654074_5b69b43ad0581.png!small)然后运行镜像

    
    
    docker run -itd -p 22222:22 57b46801d43c

这时候看到，内部容器的ssh服务的22端口已经被映射到本机22222端口了

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533692554_5b6a4a8a30413.png!small)接下来通过ssh服务连接容器

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533692707_5b6a4b233d27f.png!small)这时候有个问题，我们并不知道容器的密码是多少？怎么办呢？

  

  

  

而且这里需要注意一点是ssh的默认配置是不允许root登录的，我们需要添加一个用户或者修改sshd_config，这里进入容器的方法就有很多了

  

  

  

> 第一种：进入容器添加用户
>
>  
>
>
>  
>
>
>  
>
>
> 第二种：最开始build镜像的时候将自己的公钥添加进容器内的~/.ssh/authorized_keys，然后实现免密码ssh登录
>
>  
>
>
>  
>
>
>  
>
>
> 第三：通过docker exec -it 98defd0c6e6b /bin/bash进入容器添加用户修改密码，在通过ssh登录
>
>  
>
>
>  
>
>
>  
>
>
> 第四：修改ssh配置文件

  

  

  

这里说一下第一种，我们先用docker exec进入容器，然后添加一个可登录的用户

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693152_5b6a4ce0df98b.png!small)

  

  

  

添加用户、修改完密码之后，我们再次登录

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693172_5b6a4cf403851.png!small)

  

  

  

到这里，我们就完成了利用dockerfile对原镜像添加功能。

  

  

  

随后我们可以通过docker commit将目前我们修改过的容器再次提交成一个新的镜像。

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693185_5b6a4d0118725.png!small)![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693211_5b6a4d1bc1ba7.png!small)

  

  

  

现在一个apache-php-ssh的镜像我们就制作完毕了![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693227_5b6a4d2b04658.png!small)

##  **0x04 Docker搭建一个wordpress博客**

  

最开始我们尽量使用最简单方法部署，这里我们用到的是docker-compose。

  

`Docker Compose`是Docker 官方编排（Orchestration）项目之一，负责快速的部署分布式应用

  

  

  

这里用到的github中的一个开源项目，作者已经编写好用于worfpress的docker-compose文件，接下来我们只需要直接部署就行。

项目地址：<https://github.com/nezhar/wordpress-docker-compose>

  

  

  

我们将项目clone下来

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693391_5b6a4dcf1fae1.png!small)docker-compose.yml是容器运行的关键，具体编写方法可以参考：

  

  

  

<https://docs.docker.com/compose/>

  

  

  

我们clone下来的是别人写好的项目，所以可以直接用了

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693415_5b6a4de76b283.png!small)然后docker-compose up -d启动

  

  

  

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693432_5b6a4df8474d3.png!small)dockerps可以看到容器运行情况，这里启动了wordpress、mysql两个容器，分别映射到了127.0.0.1的80、3306端口![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693443_5b6a4e0397c47.png!small)接下来访问127.0.0.1即可![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693454_5b6a4e0e1f16c.png!small)到这里，wordpress已经搭建完毕,我们结束它吧![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693595_5b6a4e9b1256a.png!small)

##  **0x05 Docker容器互联**

接下来讲解docker容器通信。

网上大量文章采用docker
link进行连接，根据目前[官方文档](https://docs.docker.com/network/links/)\--link是一个被遗弃，最终可能会被删除的命令。

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693604_5b6a4ea464108.png!small)所以这里我们使用docker
networks进行容器连接，我们将启动两个容器，一个apache-php 一个mysql，然后用docker network对容器进行连通。

首先创建一个名为test-net的网络，默认连接方式bridge.

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693612_5b6a4eacd5800.png!small)启动一个mysql容器，映射3306端口，连接到test-net网络，设置别名为db，设置mysql密码为password

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693817_5b6a4f797edf6.png!small)启动一个apache-php容器，映射80端口，连接到test-net网络，设置别名为web![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693637_5b6a4ec5a6b15.png!small)

> tips：遇到容器已经存在的报错
>
> docker停止所有容器 docker stop $(docker ps -q)
>
> docker删除所有容器 docker rm $(docker ps -aq)

接下来我们进入到其中一个容器，初始容器是没有ping命令的，所以我们现在安装ping

更新源

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533693966_5b6a500e2eefb.png!small)然后安装ping

    
    
    apt-get install iputils-ping

接下里我们在apache-php容器ping mysql容器，可以看到mysql容器与apache容器实现互联。

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694061_5b6a506d18bf7.png!small)

##  **0x06 Docker安全**

docker安全主要体现在以下方面

> docker容器的安全性
>
> 镜像的安全性
>
> docker daemon的安全性
>
> \-------摘自 Docker进阶与实战

容器安全性的根源在于，容器和host共用内核，因此受攻击面特别大。

这里就抛砖引玉地讲一下docker虚拟机逃逸。

Docker与宿主机是共享内核的，一旦内核出现漏洞，那么docker容器的安全问题将危机到宿主机。

这里以大名鼎鼎的Dirty COW脏牛为例，演示docker逃逸。

在做这个实验之前，我们先了解下脏牛漏洞。

脏牛是一个linux本地提权漏洞，脏牛漏洞(CVE-2016_5195)是公开后影响范围最广和最深的漏洞之一，这十年来的每一个Linux版本，包括Android、桌面版和服务器版都受到其影响。

具体影响范围见：<https://m.aliyun.com/yunqi/articles/63023>

我们现在一个下载一个ubuntu14.04镜像来对漏洞进行简单地复现

为了试验方便，我选择直接用vmware搭建虚拟机。

Docker利用脏牛逃逸的关键在于宿主机存在脏牛漏洞

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694724_5b6a530405f4b.png!small)这样的内核版本是存在脏牛的，我们可以在主机上创建一个低权限用户(可读权限即可)，然后提权，由于可读即可写，所以利用方式很多，具体见：

POCS：<https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs>

我用到的POC：<https://github.com/gbonacini/CVE-2016-5195>

  * 通过替换/ etc / passwd为用户提供root权限

git clone make编译运行。

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694796_5b6a534c3af8f.png!small)这样就可以直接提权了，这节主要关注docker安全，所以这里不再细讲。

接下来我们给虚拟机安装docker

apt-get install docker.io

然后pull一个带了POC的容器(这样做主要是为了方便，当然也可以用其他的)

POC地址：<https://github.com/scumjr/dirtycow-vdso>

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694842_5b6a537ac4971.png!small)

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694850_5b6a5382d9fc8.png!small)然后运行镜像进入容器make编译POC

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694996_5b6a5414955d0.png!small)运行

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694865_5b6a5391e63ed.png!small)

注意，这里并不是每次都能成功的，失败之后vdso_patch数组也会被填充，payload的内存地址数据不为0，无法再次复现。失败输出：

> [-] failed to win race condition...
>
> [-] failed to restore vDSO

这时候无法再次做实验了，如果用虚拟机的话做之前最好做一个快照。

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533695097_5b6a547913d7f.png!small)这里可以看到，已经完全获得宿主机的权限了。

实际生产环境中，还经常遇到一个问题

docker通过环境变量的方式传递MySQL 存储引擎的密码，所以造成mysql密码是明文

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533694881_5b6a53a1a9be8.png!small)

比较流行的解决办法是

 **第一种**

> 1.创建两个 MySQL 容器 MySQL1 与 MySQL2，MySQL 的 root 密码分别为 daocloud 与 docker；
>
> 2.待 MySQL1 启动完毕，使用docker stop命令停止 MySQL1 容器，并将 MySQL1 容器的 volume1
> 全部拷贝出来，最终使用docker rm命令删除 MySQL1 容器；
>
> 3.待 MySQL2 启动完毕，使用docker stop命令停止 MySQL2 容器，并将 MySQL2 容器 volume2
> 内的文件全部删除，接着将 volume1 的内容拷贝至 volume2 下，最终启动 MySQL2。

![Docker从入门到放弃](https://image.3001.net/images/20180808/1533695299_5b6a554341309.png!small)详见：<https://www.csdn.net/article/2015-12-21/2826519>

 **第二种**

还可以使用docker swarm 提供的 secret 机制，它允许将敏感信息加密后保存到 secret 中，用户可以指定哪些容器可以使用此 secret

详见：[如何使用swarm中的secret](%E8%BF%98%E5%8F%AF%E4%BB%A5%E4%BD%BF%E7%94%A8docker%20swarm%20%E6%8F%90%E4%BE%9B%E7%9A%84%20secret%20%E6%9C%BA%E5%88%B6%EF%BC%8C%E5%AE%83%E5%85%81%E8%AE%B8%E5%B0%86%E6%95%8F%E6%84%9F%E4%BF%A1%E6%81%AF%E5%8A%A0%E5%AF%86%E5%90%8E%E4%BF%9D%E5%AD%98%E5%88%B0%20secret%20%E4%B8%AD%EF%BC%8C%E7%94%A8%E6%88%B7%E5%8F%AF%E4%BB%A5%E6%8C%87%E5%AE%9A%E5%93%AA%E4%BA%9B%E5%AE%B9%E5%99%A8%E5%8F%AF%E4%BB%A5%E4%BD%BF%E7%94%A8%E6%AD%A4%20secret%20%20%E8%AF%A6%E8%A7%81%EF%BC%9Ahttps%3A//www.ibm.com/developerworks/community/blogs/132cfa78-44b0-4376-85d0-d3096cd30d3f/entry/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8_Secret_%E6%AF%8F%E5%A4%A95%E5%88%86%E9%92%9F%E7%8E%A9%E8%BD%AC_Docker_%E5%AE%B9%E5%99%A8%E6%8A%80%E6%9C%AF_108?lang=en)

最后的建议：Docker近几年发展迅速，官方为Docker的发展付出了很大的努力。官方了大量的官方文档可以帮助我们更好地理解和使用Docker，日常阅读官方文档、更新日志是很有必要的。

> [Docker官方文档](https://docs.docker.com/)
>
> [Docker命令文档](https://docs.docker.com/engine/reference/commandline/docker/)

