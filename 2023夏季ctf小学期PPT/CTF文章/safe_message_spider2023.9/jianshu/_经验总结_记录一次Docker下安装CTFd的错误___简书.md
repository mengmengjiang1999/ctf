【经验总结】记录一次Docker下安装CTFd的错误

[ TeamsSix](https://www.jianshu.com/u/23b447f36f98)关注赞赏支持

# 【经验总结】记录一次Docker下安装CTFd的错误

# 0x01 提示错误

根据官方的步骤执行docker-compose up但是我得到了这样的一个错误

  

    
    
    ~/CTFd# docker-compose up
    ERROR: The Compose file './docker-compose.yml' is invalid because:
    networks.internal value Additional properties are not allowed ('internal' was unexpected)
    

经过多次查询后，是因为版本问题导致，因此需要将原来的docker-compose版本卸载，安装新版本。

# 0x02 安装新版本

卸载docker-compose版本

    
    
    pip uninstall docker-compose
    

先升级一下pip

    
    
    pip install –upgrade pip
    

继续安装新版本

    
    
    pip install -U docker-compose
    

也可以使用国内pip源进行加速，我使用的国内源进行的安装

    
    
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -U docker-compose
    

之后再执行docker-compose up就没有问题了

  

平时遇到问题还是需要先根据提示自己一步一步去找解决方法，之后再利用好Google。

> 更多信息欢迎关注微信公众号：TeamsSix  
>
> 参考文章：[https://www.ilanni.com/?p=13371](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.ilanni.com%2F%3Fp%3D13371)  
>
> 原文链接：[https://www.teamssix.com/year/190720-121144.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.teamssix.com%2Fyear%2F190720-121144.html)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [docker-compose教程（安装，使用, 快速入门）](https://www.jianshu.com/p/33f7a3333118)

1.Compose介绍 Docker Compose是一个用来定义和运行复杂应用的Docker工具。一个使用Doc...

[渝味](https://www.jianshu.com/u/98480efe3bc4)阅读 6,879评论 0赞 2

  * [Docker的常规应用手册](https://www.jianshu.com/p/667af381bd76)

一 、什么是 Docker Docker 最初是 dotCloud 公司创始人 Solomon Hykes 在法国...

[Blazzer](https://www.jianshu.com/u/00b4d9b33a54)阅读 3,035评论 0赞 13

  * [Docker基础、Machine、Compose、Swarm入门与实践](https://www.jianshu.com/p/6b19d73c0178)

前言 你是否曾经和我一样，想了解一个新的中间件，如redis、kafka、zookeeper等，发现无论是单点还是...

[后厂村老司机](https://www.jianshu.com/u/fae25aa97716)阅读 5,875评论 5赞 29

  * [docker学习总结](https://www.jianshu.com/p/42d324d60284)

docker学习总结 最近在学习docker,内容比较多也比较简单,所以做一个简单的总结,做为笔记供自己学习 ...

[Lengff](https://www.jianshu.com/u/80f776a537a9)阅读 3,369评论 2赞 4

  * [docker for mac安装](https://www.jianshu.com/p/2d6d18f9dd40)

Docker是一个跨平台的轻量级虚拟机，可移植性非常高，一次部署，终生可用。Docker可以在Linux,Wind...

[风舞柏杨](https://www.jianshu.com/u/9ccaccc18a10)阅读 4,345评论 0赞 8

 