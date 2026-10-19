##  概述

 **axis 全称Apache EXtensible Interaction System 即Apache可扩展交互系统。axis
为创建服务器端、客户端和网关SOAP等操作提供基本框架。axis 目前版本主要面向Java，面向C++的版本正在开发中。axis
并不完全是一个SOAP引擎，还可以作为一个独立的SOAP服务器和一个嵌入Servlet引擎（例如Tomcat）的服务器。**

##  本地漏洞复现

从apache
axis官网下载1.4的[版本](http://archive.apache.org/dist/ws/axis/1_4/%22%3Ehttp://archive.apache.org/dist/ws/axis/1_4/)。

在本地tomcat搭建，可以看到下载下来后的WBE-INF，其中并没有有些文档中写的server-config.wsdd文件  
![axis1.png](https://image.3001.net/images/20191118/1574061837_5dd2470d4b347.png!small)然后去查看web.xml中的文件，也未打开AdminService的注释。  
![axis2.png](https://image.3001.net/images/20191118/1574061846_5dd247160b40c.png!small)

此时我们直接本地利用poc来本地注册服务攻击，发现可以正常注册，并向服务对应的jsp文档里写入shell内容。

![axis3.png](https://image.3001.net/images/20191118/1574061853_5dd2471da2572.png!small)

注册完之后，此时是通过AdminService本地注册了一个RandomService服务，然后绑定了一个日志操作，日志操作将日志输入到一个jsp文件中，于是就可以构造操作去写日志，并执行jsp文件，造成远程命令攻击。

###  诡异的事情

 **阶段一：**

根据漏洞利用的POC，先将本地之前利用的代码生成的webshell文件ha233.jsp删除，再在远程主机利用POC、此时将webshell的名称改为webshell.jsp，居然可以直接生成shell文档，且名称为ha233.jsp

删除本地利用时生成的webshell文件ha233.jsp

![axis4.png](https://image.3001.net/images/20191118/1574061868_5dd2472c0646b.png!small)

再在虚拟机执行利用的exp，此时将webshell文件改名为webshell.jsp

![axis5.png](https://image.3001.net/images/20191118/1574061876_5dd247342fc6b.png!small)

发现此时本地仍然生成了一个ha233.jsp  
![axis6.png](https://image.3001.net/images/20191118/1574061884_5dd2473c9d2f9.png!small)

查看tomcat服务器，日志中表明拒绝了远程IP访问的方式  
![axis12.png](https://image.3001.net/images/20191118/1574061942_5dd2477699d7e.png!small)

通过上述的一系列操作，可以得知本地注册服务，远程是可以调用，但是仅仅如此嘛？

 **阶段二**

与阶段一上边基本一致，但是此时我们将虚拟机里边的exp再次修改一下，将写的文件内容修改，命名仍为webshell.jsp，只是将参数改为hacker，本地的exp为c  
![axis7.png](https://image.3001.net/images/20191118/1574061956_5dd24784ee13c.png!small)  
查看写入到本地的webshell文件，肯定命名是ha233.jsp，但是内容却改变了，此时参数就为hacker  
![axis8.png](https://image.3001.net/images/20191118/1574061965_5dd2478d6357c.png!small)

###  诡异的事情总结

在原生的状态下，可以从本地来注册服务，在注册的服务中绑定日志操作，且日志操作对应的日志文档为jsp文件时，可以从远程直接调用该服务，此时进行的操作都会记录到日志文件中，从而可以将jsp马写入其中。

 **利用前提**

> 1.本地注册服务的名称要知道
>
> 2.本地注册服务有日志记录，且日志记录使用jsp文件格式

##  远程漏洞复现

###  过程

在本地漏洞复现中，我们发下axis下载下来后并没有server-config.wsdd文件，但是在本地注册一个服务后，该文件就会出现  
![axis9.png](https://image.3001.net/images/20191118/1574061979_5dd2479b36278.png!small)

将该文件中的enableRemoteAdmin配置为true  
![axis10.png](https://image.3001.net/images/20191118/1574061987_5dd247a37dd7d.png!small)

此时在虚拟机执行exp，可以看到正常注册一个服务，并写入shell.jsp文件  
![axis11.png](https://image.3001.net/images/20191118/1574061995_5dd247abb3677.png!small)

###  总结

通过我们的测试，发现只需要将server-config.wsdd文件中enableRemoteAdmin配置为true，就可以远程注册服务，并不需要将web.xml中的AdminServlet注释掉

##  漏洞分析

可以先看看Axis使用，基本上就懂得漏洞利用的原理

<https://blog.csdn.net/a5489888/article/details/9010939>

##  参考文章

> <https://blog.csdn.net/a5489888/article/details/9010939>
>
> <https://www.secpulse.com/archives/108937.html>
>
> <https://github.com/KibodWapon/Axis-1.4-RCE-Poc>

***本文原创作者：1u0hun，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

