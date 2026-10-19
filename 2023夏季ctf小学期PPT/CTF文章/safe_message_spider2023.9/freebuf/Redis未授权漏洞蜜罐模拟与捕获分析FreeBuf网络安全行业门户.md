## 1.概述

文章主要分析Redis未授权漏洞的原理及形成原因，使用vulhub靶场进行漏洞复现，在了解漏洞原理并复现的基础上使用golang编写蜜罐代码进行模拟，开放端口在网上捕获真实存在的恶意攻击行为，对恶意样本进行分析，总结出威胁情报。

## 2.漏洞原理与复现

### 2.1 漏洞环境

靶机 unbutu IP： 192.168.145.150  
攻击机 kali IP： 192.168.145.130

### 2.2 漏洞原理

Redis是一个开源的使用ANSI C语言编写、支持网络、可基于内存亦可持久化的日志型、Key-Value数据库，并提供多种语言的API。Redis是由一个键、值映射的字典构成。为高速低负载存储系统提供了一种解决方案。

Redis默认配置是不需要密码认证的，也就是说只要连接的Redis服务器的host和port正确，就可以连接使用。Redis因配置不当可以被未授权访问，被攻击者恶意利用。默认情况下，会绑定在
0.0.0.0:6379，这样将会将 Redis 服务暴露到公网上，如果在没有开启认证的情况下，可以导致任意用户在可以访问目标服务器的情况下未授权访问
Redis 以及读取 Redis的数据。

攻击者无需认证访问到内部数据，可能导致敏感信息泄露，黑客也可以恶意执行flushall来清空所有数据。

攻击者可通过EVAL执行lua代码，或通过数据备份功能往磁盘写入后门文件。

如果Redis以root身份运行，黑客可以给root账户写入SSH公钥文件，直接通过SSH登录受害服务器。

### 2.3 复现

在宿主机上使⽤vulhub搭建漏洞环境，

环境搭建好后进⼊Redis⽬录，

使⽤命令启动环境 docker-compose up -d

![image](https://image.3001.net/images/20220808/1659949424_62f0d1708627d4336bbce.png!small)

攻击机kali安装Redis客户端连接靶机。

![image](https://image.3001.net/images/20220808/1659949466_62f0d19add09731c8dc02.png!small)

使用info命令测试是否成功，上图说明靶机存在Redis未授权漏洞，

使用攻击脚本 https://github.com/vulhub/redis-rogue-getshell 进行攻击。

![image](https://image.3001.net/images/20220808/1659949504_62f0d1c0d436e1909560f.png!small)

攻击成功。

## 3\. 蜜罐模拟

### 3.1 简介

蜜罐程序使⽤golang语言编写，本次编写蜜罐程序为低交互蜜罐，低交互蜜罐模拟网络服务响应和攻击者交互，容易部署和控制攻击，但是模拟能力相对较弱，对攻击的捕获能力不强。

有别于高交互蜜罐采用真实系统与服务诱捕恶意攻击，低交互为攻击者展示的所有攻击弱点和攻击对象都不是真正的产品系统，⽽是对系统以及其提供服务的模拟，这样设计的好处是安装和配置非常简单，低交互蜜罐系统⼏乎没有安全⻛险问题，不足之处是不完善的模拟会降低数据捕获的能力，并且容易被攻击者识别。

将编译好的Linux执行文件放在服务器上开放6379端口诱使黑客进行攻击，运行程序，从而捕获网上的恶意攻击数据，记录攻击源和IP。

蜜罐源码已开源：https://github.com/sunhao282/HoneypotCaptureAttack/tree/master

### 3.2 蜜罐流程

首先模拟Redis的set和get命令

![image](https://image.3001.net/images/20220808/1659949571_62f0d2031b8e21bc31bc4.png!small)  
![image](https://image.3001.net/images/20220808/1659949588_62f0d214b6cf863247917.png!small)

模拟info命令

![image](https://image.3001.net/images/20220808/1659949611_62f0d22b8b5cb77c1d655.png!small)

模拟ping命令

![image](https://image.3001.net/images/20220808/1659949630_62f0d23e07ac473baf4b0.png!small)

模拟scan命令

![image](https://image.3001.net/images/20220808/1659949657_62f0d2592e18cefedc3eb.png!small)

模拟client命令

![image](https://image.3001.net/images/20220808/1659949677_62f0d26dd8b14f473bbdb.png!small)

模拟del命令

![image](https://image.3001.net/images/20220808/1659949697_62f0d28165e4799ef75d4.png!small)

模拟slaveof命令

![image](https://image.3001.net/images/20220808/1659949717_62f0d2955efc05673176b.png!small)

通过模拟Redis常用命令来迷惑攻击者，从而诱捕攻击者的恶意攻击行为。

## 4\. 蜜罐捕获分析

查看日志文件发现恶意攻击行为的记录。

捕获的log文件部分截图如下：

![image](https://image.3001.net/images/20220808/1659949741_62f0d2ad22f86a1fa1490.png!small)

### 4.1 下载挖矿程序

程序首先会判断恶意文件的大小是否相同，不相同杀掉并删除，相同则返回not need download。

![image](https://image.3001.net/images/20220808/1659949762_62f0d2c283b4c73880cd4.png!small)  
![image](https://image.3001.net/images/20220808/1659949778_62f0d2d20eade5222e5dd.png!small)

### 4.2 结束竞品

分析恶意样本源码发现了大量删除文件的操作，部分截图如下：

![image](https://image.3001.net/images/20220808/1659949799_62f0d2e789d8a57d9d97e.png!small)

删除⽤户账号：

![image](https://image.3001.net/images/20220808/1659949820_62f0d2fccbf8406fdc498.png!small)

杀掉进程部分截图：

![image](https://image.3001.net/images/20220808/1659949842_62f0d3121ff4850baef76.png!small)

删除docker⽂件：

![image](https://image.3001.net/images/20220808/1659949860_62f0d324274055566e288.png!small)

恶意⽂件通过大量的删除文件，杀掉进程等操作来获取最大的CPU使⽤率，从而获取最大的利益。

### 4.3 卸载安全软件

卸载阿⾥云安骑士文件

![image](https://image.3001.net/images/20220808/1659949879_62f0d337eb60692aad7a8.png!small)

卸载云警

![image](https://image.3001.net/images/20220808/1659949903_62f0d34f2e787765502f4.png!small)

关闭selinux防⽕墙，关闭Linux内核apparmor安全模块，关闭阿里云服务，杀掉阿里云安骑士相关进程。

![image](https://image.3001.net/images/20220808/1659949921_62f0d361bba10ae55fc96.png!small)

### 4.4 建立持久化

将恶意文件的下载地址写入主机，在并/root/.ssh/authorized_keys文件中写入了黑客的ssh公钥，即使客户删除了恶意文件，黑客还是可以通过ssh远程登录该主机。

![image](https://image.3001.net/images/20220808/1659949939_62f0d3731f144f7b55cb4.png!small)

### 4.5 IOC

http://en2an.top/cleanfda/init.sh

● SHA256：8573fd4eaa93912b40abde8c4e504b69ed13534a7474102f90cf7349e964a7c7  
● MD5：224d26d81f5108fce260d550d2b57f4a  
● SHA1：bdfbf5110e9bf1bb5d1b759fddf7127c5f55cf86

http://en2an.top/cleanfda/zzh

● SHA256：58da51f26d9ab2e380d2da7e917150cad2a0320c6a4e8aafd919e044ec52980c  
● MD5：077589a7b6402e6848fc22a54c2216c0  
● SHA1：ef9ccaf397335cbc786e6d8bc3fdab11a5cecd8d

## 5\. 建议

造成漏洞的原因是默认无密码，修改配置文件/etc/redis.conf给Redis设置一个强密码即可。默认端口为6379，也可以修改成其他端口避免被攻击。

