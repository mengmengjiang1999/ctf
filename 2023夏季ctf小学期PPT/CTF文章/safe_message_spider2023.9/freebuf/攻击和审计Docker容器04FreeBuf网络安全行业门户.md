原创：Lee2dog合天智汇

## 一、安全加固之Linux安全模型  

### 1、LSM  

LSM
是Linux内核的一个轻量级通用访问控制框架。用户可以根据其需求选择适合的安全模块加载到Linux内核中，从而大大提高了Linux安全访问控制机制的灵活性和易用性。

LSM框架的设计初衷是为了在Linux Kernel中实现一个MAC(Mandat-ory Access Control，强制访问控制)
Hook框架，LSM已经作为Linux
Kernel的一部分随着内核一起发布了，使用框架的好处就在于，安全人员可以直接基于LSM框架进行上层审计模块的开发，专注于业务逻辑，而不需要关注底层的内核差异兼
容性和稳定性，这是相对于sys_call hook方式最大的优势。它提供了全面的安全策略：比如SELinux、Smack、Tomoyo和AppArmor。

### 2、LSM 演示  

### 2.1 运行一个容器  

student@debian:~$ docker run --rm -it --name lsm-before -p 4321:80 nginx
bashroot@6ecbf1e837e9:/# sh# dash# bashroot@6ecbf1e837e9:/# exitexit# exit#
exitroot@6ecbf1e837e9:/# exitexit

### 2.2 添加安全选项  

Apparmor简介

由于SELinux使用复杂，适用于对安全要求特别高的企业或者组织，为了简化操作，就推出了Apparmor，所以可以说Apparmor脱胎于SELinux，但与SELinux基于角色的MAC不同的是，Apparmor是与程序绑定的基于路径的MAC，也就是说如果路径发生改变，策略就会失效。

现在我们添加apparmor安全选项，再执行sh或者dash试试

student@debian:~$ cd /opt/docker-nginx/student@debian:/opt/docker-nginx$ sudo
bane sample.toml Profile installed successfully you can now run the profile
with`docker run --security-opt="apparmor:docker-nginx-sample"`student@debian:/opt/docker-nginx$ docker run --rm -it --name lsm-after
\> \--security-opt="apparmor:docker-nginx-sample" -p 4320:80 nginx
bashroot@0bd1bb6f98b4:/# shbash: /bin/sh: Permission
deniedroot@0bd1bb6f98b4:/# dashbash: /bin/dash: Permission
deniedroot@0bd1bb6f98b4:/# bashroot@0bd1bb6f98b4:/#

发现执行命令会提示权限限制。

### 2.3 查看安全配置  

我们来看看使用bane创建的apparmor配置文件：/opt/docker-nginx/docker-nginx-sample

student@debian:/opt/docker-nginx$ cat docker-nginx-sample #include
<tunables/global> profile docker-nginx-sample
flags=(attach_disconnected,mediate_deleted) { #include <abstractions/base>
network inet tcp, network inet udp, network inet icmp, deny network raw, deny
network packet, file, umount, deny /bin/** wl, deny /boot/** wl, deny /dev/**
wl, deny /etc/** wl, deny /home/** wl, deny /lib/** wl, deny /lib64/** wl,
deny /media/** wl, deny /mnt/** wl, deny /opt/** wl, deny /proc/** wl, deny
/root/** wl, deny /sbin/** wl, deny /srv/** wl, deny /tmp/** wl, deny /sys/**
wl, deny /usr/** wl, audit /** w, /var/run/nginx.pid w, /usr/sbin/nginx ix,
deny /bin/dash mrwklx, deny /bin/sh mrwklx, deny /usr/bin/top mrwklx,

## 二、安全加固之CGroup  

简介：CGroup 是 Control Groups 的缩写，是 Linux 内核提供的一种可以限制、记录、隔离进程组 (process groups)
所使用的物力资源 (如 cpu memory i/o 等等) 的机制。2007 年进入 Linux 2.6.24 内核，CGroups
不是全新创造的，它将进程管理从 cpuset 中剥离出来，作者是 Google 的 Paul Menage。CGroups 也是 LXC
为实现虚拟化所使用的资源管理手段。

更多简介：CGroup 介绍、应用实例及原理描述
https://www.ibm.com/developerworks/cn/linux/1506_cgroup/index.html

### 1、CGroup演示  

### 1.1 运行两个不同CPU资源的容器  

student@debian:~$ docker run -d --name='low_priority' --cpuset-cpus=0 --cpu-shares=10 alpine md5sum
/dev/urandom1ba913c97572ecca172babaed0038abfc35670ae1748ed76db8c1c875e173632student@debian:~$
docker run -d --name='high_priority' --cpuset-cpus=0 --cpu-shares=50 alpine
md5sum
/dev/urandomf3757941e55cab375d672931f026fe0ff986d9d082fc1fea62cacd373b2aeb9cstudent@debian:~$

### 1.2 查看资源占用状态  

![v2-558384500bb77227119d59dfe6a7549f_hd.j](https://pic2.zhimg.com/80/v2-558384500bb77227119d59dfe6a7549f_hd.jpg)

### 1.3 停止并删除容器  

student@debian:~$ docker stop low_priority
high_prioritylow_priorityhigh_prioritystudent@debian:~$ docker rm low_priority
high_prioritylow_priorityhigh_prioritystudent@debian:~$

### 1.4 不指定CPU资源的情况下运行  

student@debian:~$ docker run -d --name='high_priority' alpine md5sum
/dev/urando**6c1ffae0f6e6837b360f6859d013377ad01a14ba69f21b1af36145230541056student@debian:~$
docker run -d --name='low_priority' alpine md5sum
/dev/urandom709b1bf31cf2dee3c27b7b024e2c7e1e11846c75736897decce3104d6608f02astudent@debian:~$

### 1.5 再次查看资源占用  

![v2-***8a8f8402b77cbcdca8adcc3c32a5e_hd.j](https://pic1.zhimg.com/80/v2-***8a8f8402b77cbcdca8adcc3c32a5e_hd.jpg)

可以看到没有限制CPU资源的情况下，CPU资源基本是被平分的。

停止和删除容器。

docker stop low_priority high_prioritydocker rm low_priority high_priority

## 三、利用Cluster Secrets  

在这个场景中，我们将通过利用有漏洞的应用程序来访问 docker swarm cluster secrets数据。

在CTF-VM中运行了一个存在代码执行漏洞的应用程序，且附加了docker secrets数据。

访问http://CTF-VMIP:8080/?domain=;id

![v2-ff700f69fffbb6ab74dbe1e6def31213_hd.j](https://pic3.zhimg.com/80/v2-ff700f69fffbb6ab74dbe1e6def31213_hd.jpg)

我们可以利用printenv命令来访问应用程序容器内的环境变量

![v2-27c68bdbf5b53527fa15a35a69c40458_hd.j](https://pic3.zhimg.com/80/v2-27c68bdbf5b53527fa15a35a69c40458_hd.jpg)

浏览目录

![v2-a58a1816f1ee2f6a06ca4cc27d3f13c6_hd.j](https://pic1.zhimg.com/80/v2-a58a1816f1ee2f6a06ca4cc27d3f13c6_hd.jpg)

查看文件

![v2-5f293fda1e1a4df2098f0bb03c4a014b_hd.j](https://pic2.zhimg.com/80/v2-5f293fda1e1a4df2098f0bb03c4a014b_hd.jpg)

## 四、Contained.af  

docker安全在线挑战网站：https://contained.af，感兴趣的可以去玩玩。

### References  

DEF CON 26 Workshop - Attacking & Auditing Docker Containers Using Open Source
https://github.com/appsecco/defcon-26-workshop-attacking-and-auditing-docker-containers

### 备注：  

本文由作者原创翻译

完结撒花

前面内容回顾：

[攻击和审计Docker容器01](https://mp.weixin.qq.com/s/_9vykBJfKA1K6J-ducLKcA)

[攻击和审计Docker容器02](https://mp.weixin.qq.com/s/UjSGAUIy1KIXa-hDggaLLw)

[攻击和审计Docker容器03](https://mp.weixin.qq.com/s/pMm4X6F39sGjgIzyGpxaMw)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

