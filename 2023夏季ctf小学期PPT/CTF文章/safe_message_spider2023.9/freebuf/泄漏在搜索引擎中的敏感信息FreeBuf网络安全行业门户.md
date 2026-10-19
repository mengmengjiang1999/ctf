## 前言

**很多个人、公司和机构把一些敏感信息暴露在了互联网上而不自知。一些Hacker就利用搜索引擎来获取这些敏感信息，从而进行一些攻击。其中最流行的方式是使用Google
Dorks，从Google搜索引擎来搜索网站信息、漏洞，甚至是已被挂马的后台Webshell。**

## Github搜索

###  邮箱信息

搜索关键字：

    
    
    @gmail.com Python recently indexed

![](https://image.3001.net/images/20191121/1574325738_5dd64dea07a30.png!small)

搜索关键字：

    
    
    @163.com smtp

![](https://image.3001.net/images/20191121/1574325754_5dd64dfaef653.png!small)

关注的商品降价后给自己发邮件，还东哥的兄弟。。。

这里引用了配置文件（config.ini），再打开config.ini，就看到账号密码了。

![](https://image.3001.net/images/20191121/1574325773_5dd64e0dae58b.png!small)

###  数据库信息

搜索关键字：

    
    
    mysql pass

虽然很多都是本地数据库，也有部分是网络数据库。

![](https://image.3001.net/images/20191121/1574325797_5dd64e25778b9.png!small)

**其中使用php和python作为编程语言的用户，暴露的用户名和密码比较多。**

## Google搜索

名称  |  说明  |  例子  
---|---|---  
intitle  |  标题中的关键字  |  intile:"Baidu"  
intext  |  正文中的关键字  |  intext:"web-shell"  
inurl  |  域名  |  inurl:"/gallery.html"  
filetype  |  文件类型  |  filetype:pdf  
  
###  视频类

搜索关键字：

    
    
    intitle:"VB Viewer"
    intitle:"webcam 5"
    intitle:"webcam 7"
    inurl:'/gallery.html'
    intitle:"Yawcam" inurl:8081
    inurl:embed.html inurl:dvr 
    inurl:"/view/view.shtml?id="
    inurl:guestimage.html

![](https://image.3001.net/images/20191121/1574325820_5dd64e3cbb4ac.png!small)

从后缀的jp可以看出是日本某地。

![](https://image.3001.net/images/20191121/1574325853_5dd64e5d1f998.png!small)

瑞典已经下雪了。

许多暴露在互联网上的视频监控网站，甚至都不需要密码就可以进行访问。部分摄像头还可以控制朝向，如果你家的IP摄像头那天自己动了起来，那么有可能坏了，还有可能是被攻破了。

###  文档类

搜索关键字：

    
    
    "Scanned by Camscanner" filetype:pdf

![](https://image.3001.net/images/20191121/1574325864_5dd64e680b820.png!small)

一些扫描件。

###  其他数据

搜索关键字：

    
    
    intitle:"netdata dashboard" AND intext:"Costa Tsaousis"

![](https://image.3001.net/images/20191121/1574325877_5dd64e751e6c8.png!small)

后台监控数据面板

搜索关键字：

    
    
    inurl:7474/browser intitle:Neo4j

Neo4j数据库

![](https://image.3001.net/images/20191121/1574325887_5dd64e7f793d6.png!small)

搜索关键字：

    
    
    intitle:"Namenode information" AND inurl:":50070/dfshealth.html"

![](https://image.3001.net/images/20191121/1574325896_5dd64e883a303.png!small)

hadoop HDFS分布式文件存储数据库。由一台外网NameNode节点和多台内网DataNode节点组成。

## 总结

>
> 很多人在把Github当做自己的私人移动代码存储库（因为没有人关注你的项目，你的代码被淹没在茫茫之中），但请不要忘了，你的库仍然是公开的，把数据库地址、账号密码都写进去很容易被一些自动化工具抓取到。最后导致数据库频频出现问题，还以为是代码的问题，疯狂地修改加固，其实不是代码的漏洞，而是自己的疏忽。
>
>
> 许多物联网设备。如IP摄像头等确实很方便，但它如果暴露在了互联网中，别人就会偷窥你的隐私。使用扫描工具可以发现你的设备，恰好后台又是弱密码或是默认密码，那你的隐私就荡然无存。
>
> 还有一些软件默认就会启动Web服务，虽然方便了管理和操作，也增加了风险。

##  参考

> <https://www.exploit-db.com/google-hacking-database/>

***本文原创作者： 晴雯晴雯晴雯，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  
  

