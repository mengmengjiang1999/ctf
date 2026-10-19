# 文前漫谈

学习漏洞千万步，学会调试第一步。

# Java Remote Debug 原理简述

Java远程调试的原理是 **两个JVM之间** 通过Java debug协议 **JDWP（Java Debug Wire Protocol）**
进行通信，必须保证本地的Java的源代码与目标应用程序 **一致**
才可以成功下断点调试，我们通常认为远程JVM是debug服务器，本地JVM是debug客户端。

IDEA为我们提供了方便的远程JVM调试服务，只要简单运行配置远程JVM就可以连接远程JVM进行调试，而且IDEA会帮我们自动生成命令行，可以为远程JVM运行提供参考命令。

![](./img/4668993503297884391.png)

选择调试器模式：

  1. 附加到远程JVM 
  2. 侦听远程JVM

这两种就好比正向、反向连接一样。附加到远程JVM是远程JVM开启监听的情况下主动连接远程，侦听就是等待远程JVM主动连接IDEA客户端，对应的远程JVM命令行实参不同。

一般使用附加到远程到JVM的情况比较多。生成的 `远程JVM的命令行实参` 就是运行远程Jar包时需要加上的参数，举个例子

    
    
    java -jar pool.jar //普通模式启动
    java -jar -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 pool.jar //debug模式启动，调试端口是5005

不同的JDK版本，JVM命令行参数可能不同，这里仅介绍下JDK 5-8的命令行参数。

# 魔改Vulhub进行docker远程调试

很多师傅都对用Vulhub进行漏洞调试垂涎已久，理解了上面的debug原理就知道，只要在启动jar包时加一行代码就能方便的进行Remote调试了

    
    
    -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005

可能也是由于Vulhub项目太方便了，导致大家很少看Vulhub的项目文件。Vulhub每一个漏洞项目的源代码和Dockerfile文件都放在
`/base` 目录下对应的文件夹里，它是完全开源的：）。

![](./img/3925586737427903955.png)

So，不用去翻dockerhub里的记录，然后拖jar包，直接去Dockerfile里加上远程调试的命令就OK了。

# 基于Vulhub制作方便调试的Dockerfile

起初打算直接Dockerfile里加一条调试启动命令，实践下来发现本地docker里maven打jar包太慢了。想要方便一点，必须推到dockerhub上的镜像才可能，最后解决办法就是直接把源码打成jar包，用docker直接启动了。

不需要打jar包的就更方便了，直接用Vulhub的项目改改就Ok。

成果展示：[P001water/Vulhub-For-DebugJavaVul: A project to debug java
vulnerabilities easily，Thank you for the vulhub project
(github.com)](https://github.com/P001water/Vulhub-For-DebugJavaVul)

# 演示

用Vulhub-For-DebugJavaVul项目方便的调试fastjson

和vulhub一样，进入对应文件夹，直接

    
    
    docker-compose up

![](./img/7621256150471995130.png)

进入 base 目录对应漏洞的源码文件夹，IDEA打开项目源码，配置远程JVM调试即可，ip换成自己虚拟机的，端口是默认的5005。

![](./img/2031615311461029578.png)

直接浏览器访问，本地下断点即可拦截

![](./img/3431880316773761062.png)

还是挺方便的，拉起一次镜像后之后几乎是秒构建。源码和Jar包都在，也适合自个儿研究。`base`目录下还是项目源码。欢迎师傅们共建 : )

项目地址：

只传了我自个儿调过的几个，以后再更新吧

[P001water/Vulhub-For-DebugJavaVul: A project to debug java vulnerabilities
easily，Thank you for the vulhub project
(github.com)](https://github.com/P001water/Vulhub-For-DebugJavaVul/tree/main)

# Learn from

[Java 漏洞分析之远程调试方法总结 (seebug.org)](https://paper.seebug.org/1316/#_2)

