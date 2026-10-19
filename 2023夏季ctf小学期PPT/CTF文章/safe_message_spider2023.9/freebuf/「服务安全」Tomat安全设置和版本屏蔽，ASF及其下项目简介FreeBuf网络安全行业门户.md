![apache.jpg](https://image.3001.net/images/20180224/151945484529.jpg!small)  

  

Apache Tomcat，我们一般简称Tomcat，是著名非盈利开源软件Apache软件基金会（Apache Software
Foundation）的一个免费开源的Java应用服务器,实现了Java Servlet，JavaServer Pages，Java语言表达和Java
WebSocket技术。所有规范基于JCP（Java Community Process）标准，在各大小公司都有广泛地应用，比如BAT。

Tomcat的开发基于Apache License version 2协议的开放参与式环境，有众多的参与者和优秀的开发者。目前维护版本为Tomcat
7、Tomcat 8和Tomcat 9系列版本。笔者写这篇稿子的时候，最新正式版本分别为Tomcat 7.0.85、Tomcat 8.0.50和Tomcat
9.0.5。

笔者所在公司线上平台也是主要Java开发，有大量的Tomcat
服务器需要维护做安全设置，并且对其做版本屏蔽。今天就以Tomcat服务器安全设置和版本屏蔽为主题介绍下。

## Tomcat安全配置

### 1、 删除多余的工程项目

去掉Tomcat默认附带的示例文件、帮助文件、禁止Web后台管理界面（有些自动化部署项目可能需要，这时候根据实际进行配置）。

主要删除webapp目录下，所有非工程目录（ROOT DOCS example manage web-manage）等

### 2、 停止Tomcat shutdown端口

这个端口用于本地放送命令给Tomcat 停止Tomcat的应用服务器，我们可以通过配置禁止才端口启动。方法如下：

配置conf/server.xml文件，修改SHUTDOWN端口为-1

    
    
    <Server port="-1" shutdown="SHUTDOWN">

### 3、 禁止列目录

配置conf/web.xml文件，防止直接访问目录时由于找不到默认主页而列出目录下所有文件,注意本项默认是不列出的。

  
![1.jpg](https://image.3001.net/images/20180224/15194554011919.jpg!small)  

### 4、 禁止使用AJP

配置conf/server.xml文件，注释或删除如下部分：

<Connector port="*" maxThreads="*"

enableLookups="false" redirectPort="*" protocol="AJP/**" />

修改为：

<!--<Connector port="*" maxThreads="*"

enableLookups="false" redirectPort="*" protocol="AJP/**" />\-->

### 5、 tomcat 降权启动

注意一定不要以root特权用户启动tomcat，这样很危险！很危险！很危险！，重要的话说三遍。如果已经用root启动了，请执行以下步骤加固：

    
    
    kill -9 pid

(先停掉tomcat)，注意不要影响业务

    
    
    useradd tomcat

修改 tomcat 目录宿主（目录按照实际工程目录替换）

chown tomcat.tomcat /tomcat目录/apache_tomcat &ampndashR

su tomcat

bin/startup.sh

## Tomcat版本信息屏蔽

为了屏蔽Tomcat版本信息我们要做做两个地方的版本信息，假定我们要把Tomcat版本信息修改为FC CDN
Server，冒充一个CDN的服务器，来用唬人（不要广泛流传哦）。

### 1、 ServerInfo.properties自定义服务版本信息

主要表现在网页错误页等信息中的版本信息。

修改 org/apache/catalina/util/ServerInfo.properties信息，如果没有的话，先创建该文件。

    
    
    server.info=FC CDN Server

### 2、 server.xml自定义服务版本信息

主要表现在Http响应头中的的版本信息。

修改conf/ server.xml 文件

找到这段内容：

<Connection port="8080" protocol="HTTP/1.1"

connectionTimeout="20000"

redirectPort="8443"/>

修改为：

<Connection port="8080" protocol="HTTP/1.1"

connectionTimeout="20000"

redirectPort="8443"

server=" FC CDN Server "/>

好了今天的主题就说完了，最后做个小知识科普，笔者发现好多人傻傻分不清楚。

## 小知识科普  
【不支持外链图片，请上传图片或单独粘贴图片】  

### Apache、Tomcat

  
![2.jpg](https://image.3001.net/images/20180224/15194554867158.jpg!small)  

Apache Httpd，Apache，Apache
Tomcat，Tomcat这几个词（可能还有很多带Apache的软件），可能好多人就知道个Apache，实际上是指Apache HTTP 服务器Apache
Httpd,简称Apache。

Apache
Tomcat就是今天我们说的主角，Java应用服务器和容器，简称Tomcat。他们因为都是Apache软件基金会(ASF)旗下的自由软件项目所以都以Apache起头。

这么多Apache的项目为啥只有Apache Httpd可以简称为Apache呢？

![5.jpg](https://image.3001.net/images/20180224/15194556393312.jpg!small)  

因为这个基金会就是起源于httpd的的嘛，后来在他的基础上，发展出来了如Mod_Perl（在apache中运行perl的项目）、Java
Apache等项目。

### Jakarta项目

  
![3.jpg](https://image.3001.net/images/20180224/15194555393129.jpg!small)  

Jakarta就是Java
Apache项目开始是为了做Java容器的项目，后来在Sun的建议下改名为Jakarta，后来随着Java不断流行，Apache也水涨船高，JSF中容纳了大量的Java项目（大概200多个，是数量最大的）。很多项目于由于使用人数很大又从Jakarta中分离出来成了顶级项目，目前Jakarta也是已经完成使命退役，不复存在了。

以下就是目前SFC中的项目列表，其家族强盛可见一斑。

![4.jpg](https://image.3001.net/images/20180224/15194555559749.jpg!small)  

  
  

