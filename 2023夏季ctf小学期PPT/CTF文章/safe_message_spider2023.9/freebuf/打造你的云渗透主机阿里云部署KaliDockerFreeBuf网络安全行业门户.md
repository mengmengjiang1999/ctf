##  一、环境

阿里云服务器

注：硬盘剩余空间最好大于45G，因为kali的docker镜像2G+kali所有工具包16G+保存的新镜像19G ≈ 37G……

> **硬盘剩余空间大于50G**
>
> CentOS 7.6
>
> docker 19.03.6

##  二、安装docker

docker最好在CentOS7以上的系统安装，因为它对Linux内核版本有要求，具体可以百度。

###  安装依赖

docker依赖于系统的一些必要的工具，可以提前安装。

    
    
    yum install -y yum-utils device-mapper-persistent-data lvm2

2、添加软件源

    
    
    yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo

###  安装docker-ce

    
    
    yum clean allyum makecache fast
    yum -y install docker-ce

###  docker换源

更新docker源为中国国内源。

在/etc/docker下编辑或新建daemon.json：

    
    
    vi  /etc/docker/daemon.json

添加内容：

    
    
    {
    "registry-mirrors": [
    "https://kfwkfulq.mirror.aliyuncs.com",
    "https://2lqq34jg.mirror.aliyuncs.com",
    "https://pee6w651.mirror.aliyuncs.com",
    "https://registry.docker-cn.com",
    "http://hub-mirror.c.163.com"
    ],
    "dns": ["114.114.114.114","8.8.8.8"]
    }

###  启动服务

通过systemctl启动服务，并设置开机启动docker。

    
    
    systemctl start docker
    systemctl enable docker

5、查看版本

使用docker version查看当前的版本，顺便看看是否启动成功。

    
    
    docker version

##  三、拉取kali镜像

拉取kali镜像保存到本地：

    
    
    docker pull kalilinux/kali-linux-docker

命令说明：

    
    
    docker pull [userName/]<仓库名>[:tag]
    1.拉取一个docker官方的镜像，由于官方的仓库叫顶级仓库，不需要加docker用户名，直接用<仓库名>[:tag]。
    2.tag用以标识不同版本的镜像。如果不加tag，默认拉取最新版本，也就是latest。
    3.拉取某个docker用户自己制作的镜像，需要加用户名以唯一标识出这个镜像。

查看本地镜像：

    
    
    docker images

#
![](https://image.3001.net/images/20200322/1584859015_5e7707870fefb.png!small)

##  四、创建kali容器

###  用本地镜像创建容器

    
    
    docker run -id  --restart=always --name=kali2020  -p 2222:22 -p 4444:4500   a1765e8e381e

命令说明：

    
    
    docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
    OPTIONS包括：
    -i  保持打开容器的标准输入。由于容器默认执行命令是bash，在-d后台运行时，必须指定-i保持打开标准输入，否则容器无限退出、重启
    -d  容器后台运行，不交互
    --restart=always  docker每次启动，都会启动该容器
    --name=<容器名>  设置该容器名字
    -p <HostPorts>:<containerPorts>  映射宿主机端口到容器端口
    -t  分配一个伪终端并绑定到容器的标准输入
    IMAGE::= [userName/]<仓库名>[:tag] 
             | <local kali image`s ID> 
    COMMAND 容器创建后执行的命令。默认为bash等。
    #如果想直接进入shell交互界面，就用-it参数，去掉-d，最后再加上命令/bin/bash

查看创建的容器的列表：

    
    
    docker ps -a
    # -a 列出所有容器

![](https://image.3001.net/images/20200322/1584859033_5e77079928201.png!small)

附：

    
    
    删除容器
    docker rm -f <容器名|容器ID>
    终止容器
    docker stop <容器名|容器ID>
    启动容器
    docker start <容器名|容器ID>
    查看容器日志，在查错时用
    docker logs <容器名|容器ID>

###  进入容器

    
    
    docker exec -it kali2020 /bin/bash

![](https://image.3001.net/images/20200322/1584859057_5e7707b1e09a8.png!small)

命令说明：

    
    
    docker exec -it <containerName | containerID > <command>
    -i  保持打开容器的标准输入
    -t  分配一个伪终端并绑定到容器的标准输入

附：

    
    
    退出容器终端：
    快捷键CTRL+D 或 exit

##  五、配置kali

###  修改root口令

    
    
    passwd root

![](https://image.3001.net/images/20200322/1584859066_5e7707ba3b04b.png!small)

###  换源

备份源配置文件，然后编辑

    
    
    cp /etc/apt/sources.list /etc/apt/sources.list.bak 
    nano /etc/apt/sources.list

粘贴以下内容：

    
    
    deb http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
    deb-src http://mirrors.ustc.edu.cn/kali kali-rolling main non-free contrib
    deb http://mirrors.ustc.edu.cn/kali kali-rolling main contrib non-free
    deb-src http://mirrors.ustc.edu.cn/kali kali-rolling main contrib non-free
    deb http://mirrors.ustc.edu.cn/kali-security kali-current/updates main contrib non-free
    deb-src http://mirrors.ustc.edu.cn/kali-security kali-current/updates main contrib non-free

更新软件列表：

    
    
    apt-get update

###  安装常用工具

    
    
    apt-get -y install  vim git python net-tools openssh-server

###  配置OpenSSH

    
    
     nano /etc/ssh/sshd_config

添加“PermitRootLogin yes”（允许远程登录root用户）：

    
    
    PermitRootLogin yes

![](https://image.3001.net/images/20200322/1584859077_5e7707c594a37.png!small)

重启服务：

    
    
    service  ssh  restart

**配置云服务器的防火墙**

打开2222、4444-4500端口，这些都是映射到kali容器的端口。

以阿里云为例：

![](https://image.3001.net/images/20200322/1584859087_5e7707cf99680.png!small)

![](https://image.3001.net/images/20200322/1584859097_5e7707d9ec384.png!small)

![](https://image.3001.net/images/20200322/1584859107_5e7707e392edb.png!small)

![](https://image.3001.net/images/20200322/1584859117_5e7707edbe833.png!small)

然后点击克隆这条刚添加的规则，修改为：

![](https://image.3001.net/images/20200322/1584859129_5e7707f96a0b3.png!small)

最终规则列表如图：

![](https://image.3001.net/images/20200322/1584859143_5e77080783205.png!small)

附：安全组策略的说明

    
    
    规则方向：出方向 | 入方向
    授权策略：允许 | 拒绝
    协议类型：全部 | TCP | UDP | ICMP | GRE
    端口范围：1~65535；注意即使是一个端口，也要写成范围，如 22/22，不能只写 22。例如 1/200、80/80、22/22、-1/-1。
    授权类型：地址段访问 | 安全组访问
    授权对象：如果授权类型为地址段访问，授权对象填写 IP 或者 CIDR 网段格式 如：0.0.0.0/0 或者 192.168.0.0/24。仅支持 IPV4。如果授权类型为安全组访问，授权对象从安全组的列表中选择一个安全组。
    优先级：1-100，数值越小，优先级越高。

**检查是否能ssh登录kali**

在xshell里尝试登录kali

![](https://image.3001.net/images/20200322/1584859156_5e770814117fa.png!small)

![](https://image.3001.net/images/20200322/1584859170_5e7708224f1fd.png!small)

成功登录：

![](https://image.3001.net/images/20200322/1584859183_5e77082f4e6ff.png!small)

### 安装kali渗透工具包

大概16G左右。

    
    
    apt-get -y install kali-linux-all

### 保存新镜像

在docker容器中做出的修改如果想维持，则必须保存到新镜像里，否则下次启动时，所做的一切更改都会消失。

    
    
    #先停止运行容器kali2020
    docker stop kali2020
    docker  commit   <containername|ID>  <userName>/<仓库名>[:<tag>] -m "任何说明文字"
    #如果不写tag，默认为latest

创建后，可以docker images查看生成的新镜像。

如果命名错了，可以用docker tag 命令重新 **打标记** ：

    
    
    docker tag <containerID>  <userName>/<仓库名>[:<tag>]

###  删除原镜像

kali的原镜像已经没用了，可以删除，删除前，必须停止或删除基于该镜像的所有容器：

    
    
    docker rm -f <containerID | name>

删除镜像：

    
    
    docker -rmi <imageID>

### 数据持久化

创建数据卷以实现数据持久化。数据卷的概念参见：[1](https://blog.csdn.net/dkfajsldfsdfsd/article/details/88789360)

创建一个数据卷，每次kali容器启动时，可以把host主机某个目录挂载到kali容器的某个目录，在kali中工作时，
**把需要保存的文件都保存到这个目录，这样，即使删除（docker rm）kali容器，这些数据也不会丢失** 。

另外，如果有其他容器需要共享这些数据时，也可以挂载这个数据卷以获得/修改这些数据。

###  创建数据卷

创建一个数据卷，命名为“vol_kali”：

    
    
    docker volume create vol_kali

也可以在创建容器的时候创建数据卷，例如：

    
    
    docker run -id  -v /root/vol_kali:/root  --restart=always --name=kali2020  -p 2222:22 -p 4444:4500   a1765e8e381e

-v参数指定数据卷，该实例表示把host主机的/root/val_kali目录挂载到kali容器的/root目录。

###  查看数据卷列表

查看所有数据卷：

    
    
    docker volume ls

![](https://image.3001.net/images/20200322/1584859300_5e7708a431947.png!small)

###  数据卷在宿主机的路径

查看数据卷在宿主机的保存路径：

    
    
    docker inspect vol_kali

![](https://image.3001.net/images/20200322/1584859308_5e7708acc2c84.png!small)

### 挂载数据卷

我们用自己刚做好的kali镜像创建容器，并在启动容器时挂载kali专用的数据卷（之前创建的vol_kali）到kali的/root目录下。

    
    
    docker run -id  -v vol_kali:/root  --restart=always --name=kali2020  -p 2222:22 -p 4444:4500   a1765e8e381e

##  六、日常运维

不需要容器运行的时候可以pause或stop：

    
    
    docker stop <容器名|ID>

需要启动时，先查看容器列表：

    
    
    docker ps -a

启动：

    
    
    docker start <容器名|ID>

## 七、（可选）上传dockerhub

可以把安装和配置好的自定义的kali容器上传到dockerhub，以后要用拉取就行。

###  注册dockerhub（略）

###  在dockerhub新建一个仓库

这些操作和github较相似。略。

###  基于容器创建一个新的镜像

**如果之前的步骤里保存了新镜像，也可以省略这一步** 。基于kali容器创建新镜像：

    
    
    #先停止运行容器kali2020
    docker stop kali2020
    docker  commit   <containername|ID>  <userName>/<仓库名>[:<tag>] -m "任何说明文字"
    #如果不写tag，默认为latest

创建后，可以docker images查看生成的新镜像。

如果命名错了，可以用docker tag 命令重新 **打标记** ：

    
    
    docker tag <containerID>  <userName>/<仓库名>[:<tag>]

###  登录dockerhub

    
    
    docker login

###  上传

把本地镜像上传到dockerhub。

    
    
    docker push  <userName>/<仓库名>[:<tag>]

支持断点传输。由于网络原因，可能中断。重新执行即可。

 ***本文原创作者：阿哥有鸟无巢，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

  

