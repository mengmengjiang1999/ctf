本期斗哥带来Java代码审计的一些环境和工具准备。

Java这个语言相对于PHP来说还是比较复杂的，所以一开始接触到Java源码审计的时候会遇到一些关于环境和配置上一些困难，本文记录斗哥在开始去审计Java代码的一些准备，希望能够帮助到刚入门的新手朋友们。

  

 **0x00 Java环境说明**

 **1\. 安装Java环境**

首先是要安装JAVA相应的JDK安装包和相应的环境变量的配置。

![配置.webp.jpg](https://image.3001.net/images/20180703/1530598514820.jpg!small)

安装完成后默认的安装目录：

![目录.webp.jpg](https://image.3001.net/images/20180703/1530598538902.jpg!small)

环境变量的配置，环境变量配置主要是告诉我们自己的电脑Java安装完后几个关键文件的路径。

●JDK的安装路径在哪里？——JAVA_HOME

![home.webp.jpg](https://image.3001.net/images/20180703/15305985632018.jpg!small)

●JDK命令文件位置（bin文件夹路径）——PATH

![path.webp.jpg](https://image.3001.net/images/20180703/15305985843508.jpg!small)

●类库文件的位置（lib文件夹路径）—— CLASSPATH

![class.webp.jpg](https://image.3001.net/images/20180703/15305986079411.jpg!small)

 **2\. 运行Java程序**

Java的代码要执行前是需要事先编译的，编译器先将Java源文件编译成二进制的文件，而进一步解析器在解析成二进制的文件。

HelloWorld.java

public class HelloWorld {

public static void main(String[] args){

System.out.println("Hello World,This is a test");

}

}

一般java源码文件没有办法像PHP或者Python那样直接解析，所以不借助IDE的话，我们需要通过javac这个命令去进行编译。

![bianyi.webp.jpg](https://image.3001.net/images/20180703/15305986676058.jpg!small)

编译完后得到.class相应的字节码文件，这是可以用java直接解析。

![解析.webp.jpg](https://image.3001.net/images/20180703/1530598690394.jpg!small)![啊.webp.jpg](https://image.3001.net/images/20180703/15305987102175.jpg!small)

 **3\. Java反编译**

由于很多时候我们得到并不是java的源码文件，而是.class结尾的字节码文件。所以我们需要一个工具帮助我们反编译看到相应的源代码。那这里推荐大家使用jd-gui这个工具。

![工具.webp.jpg](https://image.3001.net/images/20180703/15305987506135.jpg!small)

下图描述的上述过程：

![过程.webp.jpg](https://image.3001.net/images/20180703/15305987749064.jpg!small)

 **4\. Java平台**

刚接触到Java平台的时候，会接触到几个名词，如JavaSE，JavaEE，JavaME等等名词。简单来理解：

●Java SE —— 开发电脑软件

●Java EE —— 开发WEB网站

●Java ME —— 开发手机软件

 **Java SE（Java Platform，Standard Edition）：** 允许开发和部署在桌面、服务器、嵌入式环境和实时环境中使用的
Java 应用程序。Java SE 包含了支持 Java Web 服务开发的类。

**Java EE（Java Platform，Enterprise Edition）：** Java EE 是在 Java SE 的基础上构建的，它提供
Web 服务、组件模型、管理和通信 API，用来实现企业级的面向服务体系结构和 Web 2.0应用程序。

**Java ME（Java Platform，Micro Edition）：**
为在移动设备和嵌入式设备（比如手机、PDA、电视机顶盒和打印机）上运行的应用程序提供一个健壮且灵活的环境。

  

 **0x02 Tomcat的安装和使用**

 **1\. Tomcat简介**

常见的Java服务器：Tomcat、Weblogic、JBoss、GlassFish、Jetty、Resin、IBM Websphere等。

Tomcat服务器是一个免费的开放源代码的Web应用服务器，属于轻量级应用服务器，在中小型系统和并发访问等很多的场合下被普遍使用，是开发和调试JSP程序的首选。

Tomcat安装包可以去到apache的官网去下载，解压后它的目录结构如下：

![如下.webp.jpg](https://image.3001.net/images/20180703/15305988912600.jpg!small)

 **2.Tomcat部署源码**

例子：javapms公测版源码部署

![部署
1.webp.jpg](https://image.3001.net/images/20180703/15305989413284.jpg!small)

![部署
2.webp.jpg](https://image.3001.net/images/20180703/15305989577507.jpg!small)  

将ROOT目录重命名为javapms1.4拷贝到tomcat的webapp目录下。

![目录下.webp.jpg](https://image.3001.net/images/20180703/15305990112120.jpg!small)

访问<http://127.0.0.1:8080/javapms1.4/>

![4
1.webp.jpg](https://image.3001.net/images/20180703/15305990529130.jpg!small)![4
2.webp.jpg](https://image.3001.net/images/20180703/15305990668587.jpg!small)

 **0x03 IDE的使用**

 **1.选择适合自己的IDE**

个人比较习惯使用IDEA，除了IDEA以外，myeclipse也是一个不错的选择。

![选择.webp.jpg](https://image.3001.net/images/20180703/15305991206283.jpg!small)

 **2.IDEA上部署WEB项目**

因为在IDE上部署项目的话，更方便我们去调试代码和代码跟踪。

例子：javapms公测版源码部署。

![公测
1.webp.jpg](https://image.3001.net/images/20180703/15305992231342.jpg!small)![公测
2.webp.jpg](https://image.3001.net/images/20180703/15305992425079.jpg!small)![公测
3.webp.jpg](https://image.3001.net/images/20180703/15305992619672.jpg!small)![公测
4.webp.jpg](https://image.3001.net/images/20180703/15305992666533.jpg!small)

配置运行程序，如配置tomcat。

![cat
1.webp.jpg](https://image.3001.net/images/20180703/15305993787206.jpg!small)![cat
2.webp.jpg](https://image.3001.net/images/20180703/15305993943146.jpg!small)![cat
3.webp.jpg](https://image.3001.net/images/20180703/1530599399225.jpg!small)![cat
4.webp.jpg](https://image.3001.net/images/20180703/15305994043000.jpg!small)![cat
5.webp.jpg](https://image.3001.net/images/20180703/15305994324667.jpg!small)![cat
6.webp.jpg](https://image.3001.net/images/20180703/15305994379483.jpg!small)![cat
7.webp.jpg](https://image.3001.net/images/20180703/15305994442747.jpg!small)

安装：<http://127.0.0.1:8080/javapms1.4>

![安装.webp.jpg](https://image.3001.net/images/20180703/15305994821774.jpg!small)

 **3.IDEA上调试功能**

这里主要用到的是IDEA的Debug功能。

![功能.webp.jpg](https://image.3001.net/images/20180703/15305996227594.jpg!small)

下面是几个调试中会用到的几个快捷键：

●F7 ，进入下一步，如果当前断点是一个方法，进入方法体。

●F8 ，进入下一步，但不会进入方法体内。

●Alt+Shift+F7 ， 进入下一步，如果当前断点是一个方法，方法还有方法则循环进入。

●Shift+F8 ，跳出到下一个断点，也可以按F9来实现。

●Drop Frame ，当进入一个方法体想回退到方法体外可以使用该键。

  

 **0x04 Maven——项目管理和构建工具**

 **1.Maven介绍**

Maven是一种自动构建项目的方式，可以帮助我们自动从本地和远程仓库拉取关联jar包。

官网地址：

![地址.webp.jpg](https://image.3001.net/images/20180703/15305997975695.jpg!small)

maven 远程仓库：

![仓库.webp.jpg](https://image.3001.net/images/20180703/15305998287492.jpg!small)

之前审计的WebGoat就是使用Maven部署起来的。

![部署.webp.jpg](https://image.3001.net/images/20180703/15305998635195.jpg!small)

 **2.Maven部署项目**

在IDEA上部署Maven项目，这边以部署WebGoat源码为例。

![例1.webp.jpg](https://image.3001.net/images/20180703/15306000159387.jpg!small)![例2.webp.jpg](https://image.3001.net/images/20180703/15306000327256.jpg!small)![例3.webp.jpg](https://image.3001.net/images/20180703/15306000365281.jpg!small)![例子4.webp.jpg](https://image.3001.net/images/20180703/15306000451049.jpg!small)![例5.webp.jpg](https://image.3001.net/images/20180703/15306000514413.jpg!small)![例6.webp.jpg](https://image.3001.net/images/20180703/15306000567373.jpg!small)![例7.webp.jpg](https://image.3001.net/images/20180703/15306000618325.jpg!small)![例8.webp.jpg](https://image.3001.net/images/20180703/15306000678603.jpg!small)![例9.webp.jpg](https://image.3001.net/images/20180703/1530600072593.jpg!small)![例10.webp.jpg](https://image.3001.net/images/20180703/15306000771123.jpg!small)![例11.webp.jpg](https://image.3001.net/images/20180703/15306000826799.jpg!small)

 **3.部署完成，运行与排错**

如果使用旧版的IDEA，那么程序的兼容性比较高，直接运行StartWebGoat.java文件，该文件的完整路径是\WebGoat\webgoat-server\src\main\java\org\owasp\webgoat\StartWebGoat.java

然而不幸的是，使用最新版的IDEA报错了，报错信息如下：

![如下.webp.jpg](https://image.3001.net/images/20180703/15306001701407.jpg!small)

这是由于WebGoat的代码编写不够规范，在项目下的pom.xml没有规范书写程序包com.beust.jcommander.internal的相关信息，需要补充完整，补充如下：

<dependency>

<groupId>com.beust</groupId>

<artifactId>jcommander</artifactId>

<version>1.35</version>

</dependency>

pom.xml的完整路径为\WebGoat\webgoat-container\pom.xml。

修改完成后，重新运行StartWebGoat.java，如果没有出错，看到控制台的Spring Boot运行界面说明编译和运行成功。

访问<http://127.0.0.1:8080/WebGoat>，即可看到WebGoat的登陆页面。

 **0x05 Fortify 代码审计工具**

Fortify是一个自动化的代码审计工具，斗哥这里使用的是在FreeBuf上前辈们的2009年版的一款，框架是eclipse+规则库。而他的收费版本费用实在惊人。2009版的规则库都比较早期了，它允许我们自定义规则，所以可以在这个版本基础上增加审计规则。

![规则.webp.jpg](https://image.3001.net/images/20180703/1530600440556.jpg!small)

ps:回复 Java审计工具，即可获得工具下载链接。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180703/15306005006080.jpg!small)

