# Moonraker靶机渗透测试

阅读量 **456720**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-25 16:00:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t017bfc4116ef0d2d21.png)

## 前言

近日闲的无聊就找了个靶机玩玩，技术太菜，第一次写这个渗透测试，写的不好还请多多指教。

## 靶机搭建与下载

Moonraker靶机下载地址:<https://pan.baidu.com/s/1Hb8NgDjJiFuygeDrAaWVOA>提取码: 22ja

Monraker靶机ip: 192.168.56.150

kali攻击者ip : 192.168.56.1

说明: 获取目标主机的root权限并读取目录中的flag.txt文件

## 知识点

nmap

dirb

Burp修改Cookies

CouchDB登录凭证

Fauxton web页面的登录

apache2日志的访问

Node.js反序列化漏洞利用

shell的交互

john hash破解

## 开始测试

首先第一步对目标靶机网络端口扫描的信息收集

`nmap -sV -p- -A 192.168.56.150`

![](https://p5.ssl.qhimg.com/t0139e06e146e534713.jpg)

扫描之后发现目标开放了22(ssh),80(http),3000(http),4369(epmd),5984(couchDb)等端口。目标开放了http端口，用web浏览器打开查看

![](https://p3.ssl.qhimg.com/t01eac97cb0774fa225.png)

打开页面是一个视频文件，放完之后跳到另一个页面。

![](https://p0.ssl.qhimg.com/t010282113b080430b5.png)

然后查看了页面的源代码没有什么发现可用信息，于是使用dirb去枚举目标主机的访问目录

`dirb http://192.168.56.150`

![](https://p4.ssl.qhimg.com/t01a3bc0b318167f216.jpg)

看见一个robots.txt觉得会有些重要信息，结果一访问什么都没有。在访问services目录中看见了一个链接,其实这个也可以在上面那个页面进去也行，主要dirb没扫出更多敏感词。

![](https://p3.ssl.qhimg.com/t010f56c316f6b03c5c.png)

![](https://p4.ssl.qhimg.com/t015e29b352e6d8cff7.png)

打开访问，如图所示，一个基于网络服务的查询

![](https://p4.ssl.qhimg.com/t0173d32f21f89b4522.png)

试了一下用带图片标记去查询表单

![](https://p1.ssl.qhimg.com/t01a449563682ad2639.png)

点击提交后显示了查询的信息

![](https://p0.ssl.qhimg.com/t01bfeb3a95832bdf3a.png)

这个点在这我卡了很久，然后是要查看apache2服务的访问日志

使用命令查看日志

`tail -f /var/log/apache2/access.log`

![](https://p0.ssl.qhimg.com/t0128efd0382efcacb5.jpg)

在日志中发现了新的页面，在浏览器打开，但是有一个back的链接,点击看看会带我们去什么页面

![](https://p1.ssl.qhimg.com/t0120f8f5ff9ec65d60.png)

引导进入新的页面

![](https://p1.ssl.qhimg.com/t0120070fc5353189e4.png)

在新的页面里有两个链接里发现了一些重要信息

![](https://p5.ssl.qhimg.com/t01e823b1c43df53949.png)

打开CouchDB Notes在这个页面得到了关于用户的账号密码提示，这个对我们来说是很重要的。

账号密码提示

username: jaws

password: 女朋友名字+x99的组合

![](https://p4.ssl.qhimg.com/t010db8496210242536.png)

我哪知道他女朋友是谁呀，只有百度或者谷歌jaws的女朋友是谁咯。

![](https://p2.ssl.qhimg.com/t014894fd857758bddd.png)

然后根据提示信息，接下来就应该要查看couchdb这个了，这个怎么打开呢，我们在扫描端口时是开放了一个5984端口就是用来访问这个的，于是打开浏览器访问

![](https://p0.ssl.qhimg.com/t017d74cb02c3468353.png)

发现不对劲，加端口不能直接访问，于是在请求一下度娘

![](https://p2.ssl.qhimg.com/t019a0fba4faebd0f1c.png)

再次访问

`http://192.168.56.150:5984/_utils`

![](https://p0.ssl.qhimg.com/t0161d026bdc6bd0013.png)

使用jaws账号密码登录

username: jaws

password: dollyx99

登录成功，发现3个数据库中的文档，其他两个打开说不是admin

![](https://p2.ssl.qhimg.com/t01244285a5415e4770.png)

![](https://p2.ssl.qhimg.com/t0132264fa77cc4856c.png)

在links里发现写信息，访问提示的目录

![](https://p5.ssl.qhimg.com/t016ef7a34f790f42e3.jpg)

![](https://p5.ssl.qhimg.com/t0112fefbae8968ef69.png)

![](https://p2.ssl.qhimg.com/t011eeff357b34e315d.png)

![](https://p2.ssl.qhimg.com/t011bff5f0dc938d63d.png)

其中在HR这个目录发现了重要的信息

![](https://p3.ssl.qhimg.com/t01010cfc2b79a51c1f.png)

访问这个5界面可以得到4个账号和密码

![](https://p0.ssl.qhimg.com/t017ba5eb40b0537db2.png)

我也尝试了这些账号密码去ssh爆破，都无果，难道这些账号是用来混淆的?

其中hugo这个账号正是我们想要的，因为我们在这个页面发现是有node.js反序列化漏洞的

![](https://p5.ssl.qhimg.com/t01e823b1c43df53949.png)

接下来就访问Node.js这个框架.

`http://192.168.56.150:3000`

username: hugo

password: TempleLasersL2K

![](https://p0.ssl.qhimg.com/t01ec417e54e934c275.png)

登录成功后，显示一条信息。

![](https://p1.ssl.qhimg.com/t017dc424d38a0f4aa7.png)

然后就想着访问这个目录，发现访问不了，还以为要get,post请求然而都不是。最后F12看了下，发现了Cookies中的秘密(为什么会一开始不会看这个呢,就是因为node.js反序列化这个漏洞还不知道.手动滑稽)

![](https://p4.ssl.qhimg.com/t01c006276714ba1eb8.png)

接下来使用burp抓包，注意要抓登录的包，然后先发送到repeater,g根据右边setCookies提示设置

![](https://p2.ssl.qhimg.com/t01299f7267e18f2553.png)

开始利用,因为这个应用程序中的漏洞是它从HTTP请求中读取名为profile的cookie,对cookie值执行base64解码,并将其传递给unserialize()函数.由于cookie是不受信任的输入,攻击者可以制作恶意Cookie值从而来以利用此漏洞.

参考[Node.js反序列化漏洞利用](https://www.anquanke.com/post/id/85458)

使用[nodejsshell.py](https://github.com/ajinabraham/Node.Js-Security-Course/blob/master/nodejsshell.py) 用来生成反向shell的payload

![](https://p5.ssl.qhimg.com/t0127591d487a9519ef.png)

再次生成反序列化的 payload

![](https://p4.ssl.qhimg.com/t01d8a67eca05626a13.png)

进行 Base64 编码后,然后在 Cookie 头中加入 Payload，向服务器发送请求.

![](https://p0.ssl.qhimg.com/t01589d6d4f3e9f3459.png)

在向服务器发送之前首先启动监听端口，与生成的payload端口一致,然后就会成功反弹.

`nc -lvp 1337`

![](https://p5.ssl.qhimg.com/t01f2ffc1b155bdf00f.png)

为了方便shell,使用python进行shell交互

`python -c 'import pty; pty.spawn("/bin/bash")'`

![](https://p4.ssl.qhimg.com/t01cca1a42ca66844ad.jpg)

找了许会，没发现有什么重要目录，最后再/var/mail中找到了四个邮箱，但是访问说提示没有权限，看来是找对了，接下来就得找找信息了或者怎么提权了。

![](https://p0.ssl.qhimg.com/t0182f93ea58ee16493.jpg)

在了解CouchDB的配置后，会发现默认的安装目录为/opt/couchdb目录下，所以读取他的配置文件看看成功得到密码.

`tail /opt/couchdb/etc/local.ini`

username: hugo

password: 321Blast0ff!!

![](https://p2.ssl.qhimg.com/t014d7c8c0e3995269c.jpg)

切换用户已hugo身份登录，并读取hugo文件

![](https://p1.ssl.qhimg.com/t0122bee3022c22cedb.png)

信息中提到包括root的密码，又告诉我们在root密码后面+VR00M,和一段hash值，复制到文件进行hash破解

![](https://p2.ssl.qhimg.com/t01647cf89210f284e1.jpg)

利用john工具爆破

username: root

password: cyber

![](https://p2.ssl.qhimg.com/t01994086c400bb4a43.jpg)

然后再次以root身份登录在后面加VR00M,找到flag.txt并读取

![](https://p1.ssl.qhimg.com/t01c1cdba7662fec187.jpg)

看到最后提示一个目录访问

![](https://p1.ssl.qhimg.com/t01889c7c57bb39828c.jpg)

![](https://p1.ssl.qhimg.com/t01f2da633e6694596b.jpg)

看来是结束了,作为单身狗的我又被成功的虐了一次.

jaws和dolly最后幸福的在一起了.

## 总结

一开始做这个靶机时经常掉坑，还是花了几天时间才做出来的，太菜了，留下了没技术的眼泪，最大的坑就是在node.js修改cookies迟迟搞不定。不过收获还是挺大的，学到了很多的知识，以后还得多多训练训练，还请大佬们多多指教.

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mr.Lee** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168484](/post/id/168484)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [靶机](/tag/靶机)

 **+1** __24赞

 __收藏

![](https://p4.ssl.qhimg.com/t01acc4d4e37ad357f0.png) Mr.Lee

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

