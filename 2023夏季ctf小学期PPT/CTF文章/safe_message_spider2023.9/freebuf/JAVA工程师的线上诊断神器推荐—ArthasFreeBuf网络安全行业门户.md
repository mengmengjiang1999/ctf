运营JAVA项目的你是否经历过以下情况？

——程序能稳定运营，功能却没有响应。

——已经修复的Bug，在新版本上线后Bug依然存在，根本不知道问题出现在哪里？

——程序稳定运营且功能完备，但跑了一段时间后，发现响应速度变慢了。

碰到这些问题，一般的解决方式都是修改代码、重新上线。但对于大企业，上线流程非常繁琐，如果只是为了多加一行日志而重新发布版本，想想就很折磨。

今天给大家推荐一款开源的JAVA诊断工具——Arthas。

Arthas 是Alibaba公司研发的开源的JAVA诊断工具,采用了命令行交互的方式，进行排查JVM
相关问题的利器。自从开源以来，深受JAVA开发工程师的喜爱。

Arthas在github上的欢迎程度：

![v2-7de13ae370fd1e97ed82161e055382fb_720w.png](https://image.3001.net/images/20220407/1649331186_624ecbf25cc8ce066ff5e.png!small)

Arthas能做哪些事情？

(1) 能够提供性能看板，包括线程、cpu、内存等信息，并且会定时的刷新

(2) 根据各种条件查看线程快照。比如找出cpu占用率最高的n个线程

(3) 输出jvm的各种信息，如gc算法、jdk版本、ClassPath等

(4) 查看/设置sysprop和sysenv

(5) 查看某个类的静态属性，也可以通过ognl语法执行一些语句

(6) 查看已加载的类的详细信息，比如这个类从哪个jar包加载的。也可以查看类的方法的信息

(7) dump某个类的字节码到指定目录

(8) 反编译相关指定的类

(9) 查看类加载器的一些信息

(10) 可以让jvm重新加载某个类

(11) 监控方法的执行，同时能够获取到执行入参、出参以及抛出异常

(12) 追踪方法执行的调用栈和调用的时间

## 一、Arthas运行的工作原理

![v2-a7c0730cfc05976c905753243e29236a_720w.png](https://image.3001.net/images/20220407/1649331186_624ecbf2a507cd59719b1.png!small)

## 二、Arthas常用的命令列表

###
![v2-c51b81e3d0a4f0491256539a5ac7f57d_720w.png](https://image.3001.net/images/20220407/1649331187_624ecbf324a6de3a0eede.png!small)

## 三、Arthas的具体使用和实践

安装：

Arthas在github的地址是https://alibaba.github.io/arthas/

安装arthas的方式有很多种：

1\. 直接下载一个可以启动的jar包然后用java -jar的方式启动

2\. 用官方提供的as.sh脚本一键安装

3\. 用rpm的方式安装

这边建议使用第一种方式，因为它简单而且想迁移的时候也超级方便（毕竟只需要把下载的jar包拷贝走就行了）。

curl -O https://alibaba.github.io/arthas/arthas-boot.jar

如果下载速度太慢，可以用gitee上的源

curl -O https://arthas.gitee.io/arthas-boot.jar

curl命令直接把arthas-boot.jar下载到你想要的目录

[root@localhost ~]# ll -lrt

-rw-r--r--. 1 root root 138880 Jun 22 02:55 arthas-boot.jar

## 四、启动

用java命令直接启动

    
    
    [root@localhost ~]# java -jar arthas-boot.jar --target-ip 10.45.105.248
    [INFO] arthas-boot version: 3.3.3
    [INFO] Can not find java process. Try to passin command line. Please select an available pid.

![v2-5c8639acd9339a16807d2aaedef5ce59_720w.png](https://image.3001.net/images/20220407/1649331187_624ecbf3bd4ed6403d259.png!small)

通过浏览器访问 http://10.45.105.248:8563/：

![v2-1ef44bcd55c4e7a8153f4d50b26060ef_720w.png](https://image.3001.net/images/20220407/1649331188_624ecbf425bac612183d1.png!small)

​通过dashboard命令可以查看当前线程数和jvm内存情况：

![v2-fbef61a6830da1eda2f37b28cc335836_720w.png](https://image.3001.net/images/20220407/1649331188_624ecbf47fbd228ede757.png!small)

​通过watch
命令查看返回的结果![v2-1ea49eddb251bbc4bc46e90d19d82067_720w.png](https://image.3001.net/images/20220407/1649331188_624ecbf4f2e22a24cdac4.png!small)

## 五、Arthas其它命令

Arthas还提供了很多用于监控的命令，比如监控执行时间，反编译线上的class文件，甚至在不重启java应用的情况下直接替换某个类。官方的使用文档已经写得太详细了，这里就不再一一介绍了，大家可以自己尝试。

### 参考：

> https://www.cnblogs.com/spareyaya/p/13177513.html
>
> https://arthas.aliyun.com/doc/

