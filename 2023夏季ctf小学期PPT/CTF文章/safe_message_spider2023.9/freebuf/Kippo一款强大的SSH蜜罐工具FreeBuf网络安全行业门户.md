## 0x00 前言

**首先给大家介绍一下蜜罐，蜜罐最为重要的功能是对系统中所有操作和行为进行监视和记录，他可以帮助我们追踪溯源。简单的说蜜罐就是一个“假目标”，故意暴露一个网络中的弱点给攻击者，攻击者会对这个“假目标”发起攻击，在攻击的过程中殊不知自己的IP地址和操作等信息都被一一记录下来。过研究和分析这些信息，可以分析出攻击者采用的攻击工具、攻击手段、攻击目的和攻击水平等信息。在企业内部在不同网络内搭建多个蜜罐诱捕节点可以大大帮助我们提高攻击追踪溯源的能力。蜜罐的作用大小取决于蜜罐的真实性，越“真”越能欺骗到攻击者“上当”。**

Kippo是一款强大的SSH蜜罐工具，它具有很强的互动性，当攻击者拿到了蜜罐的SSH口令后可以登录到蜜罐服务器执行一些常见的Linux命令。

## 0x01 搭建

在搭建Kippo之前首先给大家介绍一个蜜罐系统——HoneyDrive，HoneyDrive是一个运行在linux下的蜜罐系统，在HoneyDrive上具有几十个各种各样的蜜罐程序，如Dionaea、Amun
malware honeypots，Wordpot等
，Kippo是HoneyDrive上比较典型的蜜罐。HoneyDrive就是一个Xubuntu的虚拟机系统，把虚拟机导入到vmware或VMbox中就可以运行了。

![](https://image.3001.net/images/20190617/1560773581_5d0783cdd8f57.png!small)

我们可以在HoneyDrive中运行以下命令来运行Kippo。

    
    
    /honeydrive/kippo/start.sh

![](https://image.3001.net/images/20190617/1560773690_5d07843a550c3.png!small)

当运行成功后，我们可以使用SSH工具，如XSHELL来连接我们创建的蜜罐。

![](https://image.3001.net/images/20190617/1560773851_5d0784db50faa.png!small)

在蜜罐中可以执行基本的Linux的命令，他都会有回复，如ifconfig、ps等命令。如下如，当然了，这个显示的IP地址是虚假的地址。

![](https://image.3001.net/images/20190617/1560773952_5d078540d4ffa.png!small)

我们如何查看是谁连接我的蜜罐呢？执行了什么操作呢？可以在HoneyDrive中使用这个命令来查看：

    
    
    cat /honeydrive/kippo/log/kippo.log

![](https://image.3001.net/images/20190617/1560774330_5d0786ba58c95.png!small)

## 0x02 图形化界面

Kippo还带有图形化界面，可以在浏览器中查看登录的IP、操作、及统计报表。可在浏览器中使用以下URL进行访问：

    
    
    http://IP/kippo-graph/

![](https://image.3001.net/images/20190617/1560774882_5d0788e2046f0.png!small)

![](https://image.3001.net/images/20190617/1560774928_5d07891014631.png!small)

![](https://image.3001.net/images/20190617/1560774999_5d078957915d6.png!small)

## 0x03 总结

本文介绍了Kippo这款SSH蜜罐的搭建和简单使用方法，这款蜜罐软件很强大，还有更强大的使用方法需要摸索，新人第一次写文章，希望大家能够多多支持。

 ***本文作者：Jaleni，转载请注明来自FreeBuf.COM**

