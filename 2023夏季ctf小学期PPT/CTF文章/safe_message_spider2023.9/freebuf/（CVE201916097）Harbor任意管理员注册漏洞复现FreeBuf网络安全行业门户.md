***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、简介

Harbor，是一个英文单词，意思是港湾，港湾是干什么的呢，就是停放货物的，而货物呢，是装在集装箱中的，说到集装箱，就不得不提到Docker容器，因为docker容器的技术正是借鉴了集装箱的原理。所以，Harbor正是一个用于存储Docker镜像的企业级Registry服务。

Registry是Dcoker官方的一个私有仓库镜像，可以将本地的镜像打标签进行标记然后push到以Registry起的容器的私有仓库中。企业可以根据自己的需求，使用Dokcerfile生成自己的镜像，并推到私有仓库中，这样可以大大提高拉取镜像的效率。

## 二、漏洞描述

CVE-2019-16097是Harbor的一个任意管理员注册漏洞，顾名思义，该漏洞存在于网站的注册页面，该注册功能默认开放，攻击者可以构造请求包，加上poc参数后添加一个管理员账户，目前poc已经公布，建议装载了旧版harbor的客户尽快更新。

## 三、影响范围

 **漏洞影响**  
Harbor 1.7.6之前版本 Harbor 1.8.3之前版本

## 四、 复现

下载地址:

> https://github.com/mai-lang-chai/Middleware-Vulnerability-> detection/tree/master/Harbor/CVE-2019-16097%20%E4%BB%BB%E6%84%8F%E7%AE%A1%E7%90%86%E5%91%98%E6%B3%A8%E5%86%8C%E6%BC%8F%E6%B4%9E

Poc:注册页面数据包添加参数”has_admin_role”:true

![1620735833_609a77596f5570399ffc2.png!small](https://image.3001.net/images/20210511/1620735833_609a77596f5570399ffc2.png!small)

![1620735839_609a775f0c61fed5fb195.png!small](https://image.3001.net/images/20210511/1620735839_609a775f0c61fed5fb195.png!small)

![1620735845_609a77651764c21fcc81c.png!small](https://image.3001.net/images/20210511/1620735845_609a77651764c21fcc81c.png!small)

![1620735854_609a776e7ac919c1489a3.png!small](https://image.3001.net/images/20210511/1620735854_609a776e7ac919c1489a3.png!small)

## 五、漏洞防御

升级版本至已修复此漏洞的版本，或者关闭注册功能。

