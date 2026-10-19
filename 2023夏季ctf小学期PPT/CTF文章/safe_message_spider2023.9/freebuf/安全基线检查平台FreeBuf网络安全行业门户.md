## 0x01 介绍

**最近在做安全基线检查相关的，网上有一些代码比较零散；也有一些比较完整的项目，比如owasp中的安全基线检查项目，但是收费；还有一些开源且完整的，比如lynis，但是不符合我的要求。**

我的要求如下：

> 能够对操作系统、中间件和数据库进行基线检查
>
> 脚本在系统上进行基线检查后的结果或者收集到的数据能够传输到一个服务端
>
> 服务端要做可视化展示

最终的效果是什么呢？最好能够达到阿里云里的安全基线检查的样子，差一点的话也没关系啦。本篇文章是代码中在centos7和win2012系统中将要检查的项目，参考CIS标准而来。客户端基线搜集与检查代码在[SecurityBaselineCheck](https://github.com/chroblert/SecurityBaselineCheck)现在完成了Centos和Windows2012基线检查的编写，脚本(简称agent)只在要检查的服务器上运行并显示检查结果。之后会将检查的结果以json串的形式上传到基于django搭建的后端上，后端可视化图形界面代码在
[AssetManage](https://github.com/chroblert/assetmanage),AssetManage也生成了docker镜像，存放在[AssetManage
docker镜像](https://www.freebuf.com/wp-admin/registry.cn-hangzhou.aliyuncs.com/jc0o0l/assetmanage).

## 0x02 相关技术

Agent用到的技术：

> Shell脚本
>
> Powershell脚本

后端服务器用到的技术：

> python3
>
> django2.2
>
> bootstrap
>
> html

存储所用：

> sqlite3 3.30

## 0x03 项目效果

Linux Agent：

![](https://image.3001.net/images/20200113/1578896959_5e1c0e3f264ff.jpg!small)

Windows Agent：

![](https://image.3001.net/images/20200113/1578896980_5e1c0e54ef9e8.png!small)

后端展示效果：

![](https://image.3001.net/images/20200113/1578896994_5e1c0e62184f8.png!small)

![](https://image.3001.net/images/20200113/1578897003_5e1c0e6b4f98b.png!small)

## 0x04 使用步骤

### 1\. 下载AssetManage这个后端展示项目,

源码地址位于：[AssetManage](https://github.com/chroblert/AssetManage)

docker镜像位于：[docker in aliyun](http://registry.cn-hangzhou.aliyuncs.com/jc0o0l/assetmanage)

    
    
    # 一、使用源码安装后端 
    
    # 提前安装最新版SQLite3.30,python3.6 
    
    # git clone项目 
    
    # author: JC0o0l 
    
    # wechat: 信安札记 
    
    git clone https://github.com/chroblert/assetmanage.git 
    
    cd AssetManage 
    
    # 使用python3安装依赖包 
    
    python3 -m pip install -r requirements 
    
    python3 manage.py makemigrations 
    
    python3 manage.py migrate 
    
    python3 manage.py runserver 0.0.0.0:8888 
    
    # 假定该服务器的IP未112.112.112.112 
    
    # 二、使用docker进行部署 
    
    # 1\. 某服务器（假定IP为112.112.112.112），安装docker 
    
    # 2\. docker pull registry.cn-hangzhou.aliyuncs.com/jc0o0l/assetmanage:2.0 
    
    # 3\. docker images 查看记住刚刚pull下来的image id 
    
    # 4\. docker run -it -p 8888:8888 <ImageID> /bin/bash 
    
    # 5\. cd assetManage\AssetManage\ 
    
    # 6\. python3 manage.py runserver 0.0.0.0:8888 
    
    # 7\. 退出而不停止容器 按CTRL+P+Q

2\. 更改agent中后端服务器的ip和端口为上一步中服务器的IP112.112.112.112和端口8888

对于Windows：

![](https://image.3001.net/images/20200113/1578897095_5e1c0ec706227.png!small)

对于Linux：

![](https://image.3001.net/images/20200113/1578897100_5e1c0ecc5fe82.png!small)

3\. 将Agent拖到要进行基线检查的服务器上，以管理员权限运行agent

4\.
访问后端服务器可视化展示界面：[[http://112.112.112.112:8888](http://112.112.112.112:8888/)]([http://112.112.112.112:8888](http://112.112.112.112:8888/)),

点击基线检查，查看扫描记录

![](https://image.3001.net/images/20200113/1578897111_5e1c0ed7b452b.png!small)

点击Click Me查看检查结果

![](https://image.3001.net/images/20200113/1578897119_5e1c0edfad2ca.png!small)

该页面会显示进行检查的每一项的扫描结果与检查结果，并根据相应计算得出相应的分数。

0x05 总结

这个项目可以只将agent放在要进行检查的目标服务器上运行，并且以红色字体显示出不和基线规范的条目；如果要上传的话，需要先运行后端服务器，然后修改agent脚本中后面服务器的ip和端口号。这个项目目前可以针对Linux和Windows的部分操作系统进行基线检查，不适用于全部系统。

基线检查比较容易，只需要根据规范收集信息进行比较即可，而系统加固涉及的面就比较多了，不同的环境有不同的配置，系统加固一不小心就容易对系统环境造成损坏，所以这个项目不准备添加系统加固的功能

该项目的详细地址：

> agent: <https://github.com/chroblert/securitybaselinecheck>
>
> 后端：<https://github.com/chroblert/assetmanage>

 ***本文作者：jerrybird，转载请注明来自FreeBuf.COM**

