# 前言

> 博客文章地址 [芜风](https://drun1baby.github.io/)

> 因为最近在专攻Java安全，而WebGoat的搭建也是必经之路。
>
> 之前在电脑里面安装了java 11，又不想只安装到WebGoat的M14靶场，于是就有了这篇笔记。

  * 机器环境：一台是Centos机器，一台是Debian机器，搭建方式基本相同。

## 0x01 环境准备

我们这里选择WebGoat的jar版本，由于WebGoat
8的jar文件已自带了tomcat和数据库，所以不需要再另外安装tomcat和mysql这种东西，只需要安装jdk用于运行jar文件即可。

WebGoat的所有版本都是依赖于Java 8的，如果之前安装是Java 11的小伙伴，不想卸载。 **本篇文章教你在Linux下安装JDK(多个版本)
切换** ~

##### 1.1首先，先把自己服务器里面的jdk版本全部卸载掉

  * 完全卸载jdk

在bash界面下：  
 **1.移除所有 Java相关包Sun, Oracle, OpenJDK, IcedTea plugins, GIJ)**

    
    
    sudo apt-cache search java | awk '{print($1)}' | grep -E -e '^(ia32-)?(sun|oracle)-java' -e '^openjdk-' -e '^icedtea' -e '^(default|gcj)-j(re|dk)' -e '^gcj-(.*)-j(re|dk)' -e 'java-common' | xargs sudo apt-get -y remove
    
    
    
    sudo apt-get -y autoremove
    

再更新一下apt源

    
    
    sudo apt-get update
    

**2.清除配置信息**

    
    
    sudo dpkg -l | grep ^rc | awk '{print($2)}' | xargs sudo apt-get -y purge
    

**3.清除java配置及缓存**

    
    
    sudo bash -c 'ls -d /home/*/.java' | xargs sudo rm -rf
    

**4.清除jvm文件夹里面的文件**

    
    
    sudo rm -rf /usr/lib/jvm/*
    

至此，旧版本的Java已经全部卸载完毕，不知道为什么，有股特别舒坦的感觉~

## 0x02多版本Java环境搭建

之前也看了网上很多关于Java多版本环境搭建的文章，用的最多的还是下载OpenJDK的版本，然后设置一堆环境变量的，太麻烦了。

> 思维转换，极为简便地搭建Java多版本

##### 2.1直接安装Java，选择安装最主流的Java 8、Java 11、Java 17

  * Java8的安装

    
    
    // Centos:
    sudo yum install -y java-1.8.0-openjdk-devel.x86_64
    
    // Debian:
    看了很多教程，较为麻烦
    

安装完毕之后查看Java版本  
![image](https://image.3001.net/images/20220311/1646978888_622ae748daf9777a30dd0.png!small)

  * Java11的安装

    
    
    // Centos:
    sudo yum install java-11-openjdk -y
    
    // Debian:
    sudo apt install openjdk-11-jdk
    sudo apt install openjdk-11-jre
    

然而我们在查看Java版本：java -version的时候，跳出来的变成了Java 11。可是搭建WebGoat的时候，是只支持Java
8的，如果用Java 11搭建的话，我们会得到如图所示的报错。

![image](https://image.3001.net/images/20220311/1646978902_622ae75689613041464b7.png!small)

那也就是说，我们要将Java版本切换至Java 8，才可以搭建WebGoat。  
bash输入切换Java版本的命令：

    
    
    sudo alternatives --config java
    

![image](https://image.3001.net/images/20220311/1646978916_622ae764211158c2cf561.png!small)  
我们在框内输入数字即可切换Java版本，同理，如果有Java 17的版本，也同样可以被切换。  
至此，如果想搭建**WebGoat（v8.0.0.M14）**的伙伴们已经可以直接搭建了。毕竟搭建WebGoat的主要目的是代码审计嘛~

  * Java 17的安装

    
    
    // Centos:相对麻烦，需要配置环境变量// Debian:sudo apt install openjdk-17-jdksudo apt install openjdk-17-jre
    

## 0x03搭建WebGoat

  * 下载WebGoat的链接：  
`https:``//github.com/WebGoat/WebGoat/releases`

Centos小白建议安装 **WebGoat（v8.0.0.M14）** ，我当时在调试的时候安装最新版本，与Java 8、Java
11都不适配，而WebGoat又是主代码审计的靶场，所以还是建议安装最稳定的版本，少踩点坑。

安装好Java 17的朋友们可以选择安装最新版本： **WebGoat 8.2.2**

> 下载好WebGoat后，直接开跑就完事儿咯~！

##### 3.1启动WebGoat，这里以M

  * 1.默认监听127.0.0.10:8080地址

    
    
    java -jar webgoat-server-8.0.0.M14.jar
    

  * 2.自定义ip和端口可在启动时指定相应参数，这里的server.address只要设置成0.0.0.0即可，不要自作聪明设置成公网IP，当时这里踩了个坑。

    
    
    java -jar webgoat-server-8.0.0.M14.jar --server.port=8000 --server.address=0.0.0.0
    

  * 3.访问地址  
如果是服务器搭建的：`http://服务器的公网IP:端口/WebGoat/ 如果是虚拟机: `http://127.0.0.1"端口/WebGoat/`

成功访问

![image](https://image.3001.net/images/20220311/1646978927_622ae76f693843283f769.png!small)

* * *

* * *

* * *

* * *

## 0x04 Windows下用IDEA打开WebGoat并部署

##### 1\. WebGoat源码下载地址：https://github.com/WebGoat/WebGoat

##### 2\. 代码运行先决条件：java17 , Maven> 3.2.1 ,自己喜欢的IDE

##### 3\. **修改maven中的setting.xml的配置文件**

3.1）将localRepository改为本地的地址

![image](https://image.3001.net/images/20220311/1646978946_622ae782cb36970caded3.png!small)

如果没有也不必配置

3.2）将mirror改为阿里云的maven

    
    
    <mirror>      <id>aliyun</id>      <mirrorOf>central</mirrorOf>      <name>aliyun maven</name>      <url>http://maven.aliyun.com/nexus/content/group/public</url></mirror>
    

![image](https://image.3001.net/images/20220311/1646978959_622ae78fc593c9b07316e.png!small)

##### 4\. 在IDE里面配置本地的maven地址

file->settings->maven目录下maven地址改为本地的maven地址

![image](https://image.3001.net/images/20220311/1646978964_622ae794bf001a7fa128c.png!small)

##### 5\. 引入符合项目版本的jdk17

file ->project structure 引入jdk17,最好选择本地的

![image](https://image.3001.net/images/20220311/1646978969_622ae799bac5a764c1b29.png!small)

##### 6\. IDEA中运行StartWebGoat即可

## 0x05 Webwolf 的搭建

也是在 WebGoat 的 GitHub 地址中下载 WebWolf 即可。

运行命令

    
    
    java -jar webwolf-8.2.2.jar --server.port=9001 --server.address=0.0.0.0
    

接着，直接访问 对应的 IP 加上 8999 端口即可。

