## **漏洞介绍：**

北京时间2020年05月20日，Apache官方发布了 Apache Tomcat 远程代码执行 的风险通告，该漏洞编号为 CVE-2020-9484。

## 漏洞影响范围：

Apache Tomcat 10.0.0-M1—10.0.0-M4

Apache Tomcat 9.0.0.M1—9.0.34

Apache Tomcat 8.5.0—8.5.54

Apache Tomcat 7.0.0—7.0.103

## 漏洞修复方式：

  1. 升级tomcat版本
  2. 关闭session持久化

## 漏洞复现环境：

### 服务器：

CentOs7

tomcat9.30

jdk8

### 攻击方：

windows10

### 工具：

Burp

ysoserial (java反序列化漏洞利用工具)

### 插件：

groovy-2.3.9.jar (tomcat插件，ysoserial需要)

## 漏洞复现步骤：

  1. 服务器安装centos7 [安装教程连接](https://blog.csdn.net/qq_44714603/article/details/88829423)  

  2. 安装jdk8 [安装教程连接](https://www.jianshu.com/p/9ec7838411c8)  

  3. 安装tomcat 9.30 [下载地址](https://mirrors.cnnic.cn/apache/tomcat/)  

  4. 服务器中：在/usr/local/下创建一个tomcat目录，将文件解压进去，命令：tar -zxvf tomcat9.30 /usr/local/tomcat9/

  5. 修改conf/context.xlm，如图：
  6. ![](https://image.3001.net/images/20201125/1606273038_5fbdc80e3b0253f391ed1.png!small)下载groovy-2.3.9.jar，然后将groovy-2.3.9.jar 放入/usr/local/tomcat/lib目录下（ysoserial使用Groovy1命令需要的插件）[下载](https://repo1.maven.org/maven2/org/codehaus/groovy/groovy/2.3.9/groovy-2.3.9.jar)  

  7. 运行tomcat：/usr/local/tomcat/bin/catalina.sh start，如图![](https://image.3001.net/images/20201125/1606273153_5fbdc881ad72f28b9de04.png!small)
  8. 下载ysoserial( 一个生成java反序列化 payload 的 .jar 包)生成payload命令：java -jar ysoserial-master-6eca5bc740-1.jar Groovy1 "touch /tmp/hacker" > /tmp/test.session，[下载，](https://github.com/frohoff/ysoserial.git)如图：![](https://image.3001.net/images/20201125/1606273449_5fbdc9a9d01016e628660.png!small)

  9. 攻击方：通过burp抓包，添加cookie字段进行攻击，如图：![](https://image.3001.net/images/20201125/1606273352_5fbdc948698978c63f1c5.png!small)
  10. 服务器的生成了目录，命令执行完成，如图![](https://image.3001.net/images/20201125/1606273510_5fbdc9e6ee61e00d9beaf.png!small)

  

  

  

  

  

  

  

