## 0x01 前言

**Vulhub是一个面向大众的开源漏洞靶场，无需docker知识，简单执行两条命令即可编译、运行一个完整的漏洞靶场镜像。旨在让漏洞复现变得更加简单，让安全研究者更加专注于漏洞原理本身。**

建议安装在云服务器上，腾讯云、阿里云、或者国外的服务器上，这些环境不需要vps即可快速安装好环境，本地搭建需要vps支持，或者下载整个源码。由于第一次使用漏洞环境是在线下载并编译，所以最好使用云服务器或者vps代理，保证下载速度。

## 0x02 安装 docker和 docker-compose后即可开始使用vulhub

一键安装docker

    
    
     curl -s https://get.docker.com/ | sh 

或者使用linux自带的安装源安装

    
    
     sudo apt install docker.io

有时候可能服务未启动，需要启动服务， service start docker

安装docker-compose

    
    
     pip install docker-compose

没有pip 建议先安装pip （python3可选）

    
    
     curl -s https://bootstrap.pypa.io/get-pip.py | python

docker安装中会遇到一些问题：

只能启动client，无法启动server

这需要更改配置文件

    
    
    warning: /var/cache/yum/x86_64/7/docker-ce-edge/packages/docker-ce-18.02.0.ce-1. el7.centos.x86_64.rpm: Header V4 RSA/SHA512 Signature, key ID 621e9f35: NOKEY Public key for docker-ce-18.02.0.ce-1.el7.centos.x86_64.rpm is not installed

意思：docker-ce-18.02.0.ce-1.el7.centos.x86_64.rpm 公钥未安装，key没有导入

解决办法如下：

    
    
    [root@localhost ~]# wget  https://get.docker.com/gpg
    
    [root@localhost ~]# rpmkeys --import ./gpg
    
    [root@localhost ~]# systemctl start docker.service
    
    [root@localhost ~]# docker version

见到以下就是成功了：

![image.png](https://image.3001.net/images/20180313/15209062678080.png!small)  

可以看到docker的客户端和服务端的信息，则docker服务启动成功  

## 0x03下载环境

git clone <https://github.com/vulhub/vulhub.git>

直接下载地址：<https://github.com/vulhub/vulhub/archive/master.zip>

漏洞目录：

![image.png](https://image.3001.net/images/20180313/15209062947907.png!small)  

进入一个目录例如：vulhub/activemq/cve-2016-3088/

运行命令： docker-compose up -d （推荐）或者 docker-compose build

 **PS: 为什么 docker-compose build是可选的？**

docker-compose up
-d运行后，会自动查找当前目录下的配置文件。如果配置文件中包含的环境均已经存在，则不会再次编译；如果配置文件中包含的环境不存在，则会自动进行编译。所以，其实
docker-compose up -d命令是包含了 docker-compose build的。

如果更新了配置文件，你可以手工执行 docker-compose build来重新编译靶场环境。

等待运行结束，即可自动配置好环境，然后运行

下图为已经运行的服务

![image.png](https://image.3001.net/images/20180313/15209063386335.png!small)  

测试完毕之后，使用docker-compose down 即可结束服务，使环境变为初始状态。

上述命令会执行如下几个动作：

> 关闭正在运行的容器
>
> 删除所有相关容器
>
> 移除NAT（docker-compose在运行的时候会创建一个NAT网段）

vulhub网站：<http://vulhub.org/>

 ***本文作者：秃顶的邪念，转载请注明来自FreeBuf.COM**

