## 前言

  * Maven 是一个项目构建和管理工具，利用它可以对 JAVA 项目进行构建和依赖管理。
  * Maven 采用项目对象模型 POM（Project Object Model）来管理项目。
  * Maven 的主要工作就是用来解析一些 XML 文档、管理生命周期与插件。
  * Maven 被设计成将主要的职责委派给一组 Maven 插件，这些插件可以影响 Maven 生命周期，提供对目标的访问。

 **0x01 Maven环境配置**

1\. JDK安装以及系统要求Maven 是一个基于 Java 的工具，所以要做的第一件事情就是安装
JDK（自行百度）。系统要求![](https://image.3001.net/images/20211223/1640228910_61c3e82eaaea3c0ad1b70.png!small)

2\. Maven安装及环境变量配置

Mevan下载：http://maven.apache.org/download.cgi

![图片](https://image.3001.net/images/20211223/1640228926_61c3e83e8b4d134e48716.png!small)对应平台下载Maven包及解压路径

![图片](https://image.3001.net/images/20211223/1640228967_61c3e8679ed915ddbdf0e.png!small)
**设置 Maven 环境变量** **Windows**  
新建系统变量 MAVEN_HOME，变量值：E:Mavenapache-maven-3.3.9![图片](https://image.3001.net/images/20211223/1640228991_61c3e87f784b85ea470fc.png!small)

编辑系统变量Path，添加变量值：;%MAVEN_HOME%bin![图片](https://image.3001.net/images/20211223/1640229002_61c3e88ae2c243336d195.png!small)

 **Linux**  
下载解压：

    
    
      
    

`# wget http://mirrors.hust.edu.cn/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz  
# tar -xvf apache-maven-3.3.9-bin.tar.gz  
# sudo mv -f apache-maven-3.3.9 /usr/local/`

编辑 /etc/profile 文件 sudo vim /etc/profile，在文件末尾添加如下代码：

    
    
      
    

`export MAVEN_HOME=/usr/local/apache-maven-3.3.9  
export PATH=${PATH}:${MAVEN_HOME}/bin`

保存文件，并运行如下命令使环境变量生效：  
在控制台输入如下命令，如果能看到 Maven 相关版本信息，则说明 Maven 已经安装成功：

    
    
      
    

`# source /etc/profile  
# mvn -v`

 **Mac**  
下载解压：

    
    
      
    

`$ curl -O
http://mirrors.hust.edu.cn/apache/maven/maven-3/3.3.9/binaries/apache-maven-3.3.9-bin.tar.gz  
$ tar -xvf apache-maven-3.3.9-bin.tar.gz  
$ sudo mv -f apache-maven-3.3.9 /usr/local/`

编辑 /etc/profile 文件 sudo vim /etc/profile，在文件末尾添加如下代码：

    
    
      
    

`export MAVEN_HOME=/usr/local/apache-maven-3.3.9  
export PATH=${PATH}:${MAVEN_HOME}/bin`

保存文件，并运行如下命令使环境变量生效：

    
    
      
    

`$ source /etc/profile`

在控制台输入如下命令，如果能看到 Maven 相关版本信息，则说明 Maven 已经安装成功：

    
    
      
    

`$ mvn -v  
Apache Maven 3.3.9 (bb52d8502b132ec0a5a3f4c09453c07478323dc5;
2015-11-11T00:41:47+08:00)  
Maven home: /usr/local/apache-maven-3.3.9  
Java version: 1.8.0_31, vendor: Oracle Corporation  
Java home: /Library/Java/JavaVirtualMachines/jdk1.8.0_31.jdk/Contents/Home/jre  
Default locale: zh_CN, platform encoding: ISO8859-1  
OS name: "mac os x", version: "10.13.4", arch: "x86_64", family: "mac"`

 **0x02 Maven引入外部依赖**

 **项目结构**

![图片](https://image.3001.net/images/20211223/1640229041_61c3e8b1913fff813ca7a.png!small)

  

如果我们的项目需要引入外部依赖时，可以在pom.xml文件中添加依赖

    
    
      
    

`eg:sevlet的依赖  
  
<dependency>  
<groupId>javax.servlet</groupId>  
<artifactId>javax.servlet-api</artifactId>  
<version>4.0.1</version>  
<scope>provided</scope>  
</dependency>`

完整的pom.xml文件

    
    
      
    

`<?xml version="1.0" encoding="UTF-8"?>  
<project xmlns="http://maven.apache.org/POM/4.0.0"  
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  
xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
http://maven.apache.org/xsd/maven-4.0.0.xsd">  
<modelVersion>4.0.0</modelVersion>  
  
<groupId>org.example</groupId>  
<artifactId>javaweb-03-jsp</artifactId>  
<packaging>pom</packaging>  
<version>1.0-SNAPSHOT</version>  
<modules>  
<module>servlet-01</module>  
</modules>  
<dependencies>  
<!-- https://mvnrepository.com/artifact/taglibs/standard -->  
<dependency>  
<groupId>taglibs</groupId>  
<artifactId>standard</artifactId>  
<version>1.1.2</version>  
</dependency>  
<!-- https://mvnrepository.com/artifact/javax.servlet/javax.servlet-api -->  
<dependency>  
<groupId>javax.servlet</groupId>  
<artifactId>javax.servlet-api</artifactId>  
<version>4.0.1</version>  
<scope>provided</scope>  
</dependency>  
<!-- https://mvnrepository.com/artifact/javax.servlet.jsp/javax.servlet.jsp-api -->  
<dependency>  
<groupId>javax.servlet.jsp</groupId>  
<artifactId>javax.servlet.jsp-api</artifactId>  
<version>2.3.3</version>  
<scope>provided</scope>  
</dependency>  
<!-- https://mvnrepository.com/artifact/javax.servlet.jsp.jstl/jstl -->  
<dependency>  
<groupId>javax.servlet.jsp.jstl</groupId>  
<artifactId>jstl</artifactId>  
<version>1.2</version>  
</dependency>  
  
</dependencies>  
  
</project>`

在项目中使用到的依赖包在生成war时会在WEB-INF文件夹下的lib文件导入使用

![图片](https://image.3001.net/images/20211223/1640229068_61c3e8cc820cf61e9148c.png!small)
**依赖库：** **https://mvnrepository.com/**

