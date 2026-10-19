# 渗透测试实战-DC-1:1靶机入侵+Matrix2靶机入侵

阅读量 **383132**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-13 14:30:36

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0107167204b5bf7c4e.jpg)

## 前言

大家好，靶机更新了爱写靶机实战的我又来了，文章最后有福利哦！！

## 靶机下载安装

DC-1下载地址:<https://pan.baidu.com/s/1BNwbssr5ezL6DP-_6AbB4w>  
Matrix2下载地址：<https://pan.baidu.com/s/1hPqxVYwrC2rygeeAuurFMw>

![](https://p3.ssl.qhimg.com/t011a48afcafa39dab5.png)

![](https://p4.ssl.qhimg.com/t01eee4ae494cbca1ec.png)

## 实战

###  DC-1：1入侵

下面开始第一步的征程了，我们先探测一下IP

![](https://p1.ssl.qhimg.com/t01a33c780e71d2e52d.png)

靶机IP：172.16.24.46

继续使用nmap来开路

可以看到它开放了多个端口，我们看一下80端口是什么情况。。。

![](https://p5.ssl.qhimg.com/t012e93aa1577081101.png)

如图所示，是个 Drupal 的cms网站，

那么我们跑一下目录看一下吧

![](https://p0.ssl.qhimg.com/t0149ca420ec93ab8b5.png)

可以看到目录还是挺多的，其实没必要跑目录，我们只需要看一下 /robots.txt

确认一下Drupal版本

![](https://p5.ssl.qhimg.com/t017a87bc5f4c2e646d.png)

访问 /CHANGELOG.txt 出错，我们可以访问/UPGRADE.txt来确认升级情况一样能判断出版本… 哈哈哈

![](https://p2.ssl.qhimg.com/t01d8fa91c97672948e.png)

通过搜索发现该版本有个RCE漏洞，

![](https://p4.ssl.qhimg.com/t01ce7196d32bf91cf3.png)

这个小弟前面的文章出现过2次了，这次这里就不多做介绍了，直接拿shell吧，我还是一样使用msf完成

![](https://p1.ssl.qhimg.com/t01fa18ef944848bab2.png)

执行直接拿到shell，

![](https://p5.ssl.qhimg.com/t0125b6d9c2e7dd76b7.png)

拿到flag

![](https://p4.ssl.qhimg.com/t0106357e1bc3218fa3.png)

其实这些不是小弟写这个靶机的重点，我们的重点是提权的骚思路

下一步我们提权，老规矩上传个提权辅助脚本看看

![](https://p1.ssl.qhimg.com/t01f06d3f847bf09b1d.png)

我们把关注点放在这里，如图：

![](https://p4.ssl.qhimg.com/t01cf3cfb732ea80c54.png)

（注：这个也可以通过这个命令直接查看，命令：find / -perm -u=s -type f 2>/dev/null

![](https://p2.ssl.qhimg.com/t0177f941b4e86a2210.png)

）在提权的时候千万别忘记使用这个命令哦，有的时候有惊喜。。。。

其实小弟在这里被卡了一段时间，最后的突破口呢，我用到find的命令，

通过搜索find命令，发现可以带入命令，下面我来操作一遍

1.创建一个空文件 叫 anqke

![](https://p2.ssl.qhimg.com/t01848364685e1d8ee9.png)

直接使用命令： find anqke -exec ‘whoami’ ; (注：命令结尾这个“;”必须要加)

参考：<https://www.cnblogs.com/aaronax/p/5618024.html>

![](https://p1.ssl.qhimg.com/t01362c815446f3b2aa.png)

可以看到我们能直接带入命令，且是root权限，最后我们直接执行exp

find anqke -exec ‘/bin/sh’ ;

![](https://p3.ssl.qhimg.com/t017664963c4aee2756.png)

该靶机用find提权，小弟还是第一次见和使用（可能我low，大神们别喷），感觉肯定对大家以后实战中会有帮助，所以分析出来给大家！！

本靶机完！

###  Matrix2靶机入侵

该靶机的1 writeup，小弟投稿被pass了（工作人员：嘤嘤嘤），现在出2了但是没事小弟还是继续投稿！

言归正传，老规矩nmap开路

![](https://p5.ssl.qhimg.com/t01568467639a7dc4bd.png)

可以看到该靶机开放了很多端口，我们逐一查看吧

![](https://p4.ssl.qhimg.com/t017792b4dbbeabce85.png)

![](https://p2.ssl.qhimg.com/t01255fd0d200b74940.png)

![](https://p1.ssl.qhimg.com/t0100f5c3a5858a0efb.png)

![](https://p5.ssl.qhimg.com/t010587bb9c07754f58.png)

我们把目光放在 12322 端口，下面我们对他进行目录爆破

  
拿到一个新文件

![](https://p2.ssl.qhimg.com/t01ee4375be0aa96b05.png)

看到这个文件名，相信小伙伴们就已经知道怎么搞了，没错！以这种靶机的尿性，基本上这种就存在任意文件读取漏洞了，我们试一下

![](https://p0.ssl.qhimg.com/t01987714cf51392bd2.png)

的确存在漏洞，因为它是nginx，所以我们看一下nginx配置文件

![](https://p3.ssl.qhimg.com/t01102b347d5ed1cfd3.png)

发现了 /var/www/p4ss/.htpasswd , 我们进行查看

![](https://p2.ssl.qhimg.com/t01162e7bd9691287bf.png)

拿到加密hash密文，我们保持起来本地破解看看

![](https://p4.ssl.qhimg.com/t0156bf5df2877a8a06.png)

得到密码： Tr1n17y – admin

我们使用破解出来的密码成功登陆 1337 端口，如图：

![](https://p3.ssl.qhimg.com/t01b10123b8884a4cd9.png)

习惯性查看源代码，发现了注释里有个图片链接

![](https://p1.ssl.qhimg.com/t01900e4a244da8baf0.png)

我们下载来，看到这个小伙伴们肯定就知道了，图片隐写。。。 CTF常用套路

![](https://p4.ssl.qhimg.com/t01f2cea2e2f3f0c958.png)

如上图中，我们使用 steghide 命令能分离被隐写的文件，但是需要我们输入密码，这里不知道大家有没有看到刚刚密码登陆成功后首页上 红色的 “n30”,
没错 密码就是它。。。然后我们就分离出来一个名为“n30.txt”,查看一下，如图：

![](https://p1.ssl.qhimg.com/t014395c75e29d320dc.png)

得到密码：P4$$w0rd

得到密码后，我们下一步不知道大家还记不记得12320端口。。。去12320端口登陆吧，

![](https://p0.ssl.qhimg.com/t011b15ff18a0858a86.png)

成功登陆，但是这个shell不怎么好用，会超时，所以我就弹了个shell回来

![](https://p3.ssl.qhimg.com/t01a938f7b76a504f3d.png)

下面就是提权了，这里就省去小弟常见的下载运行提权插件了，直接讲个好用的吧，

我们先切换到该用户的/home目录下面，运行 ls -la，如图：

![](https://p0.ssl.qhimg.com/t01b3ed07dc2cd6c15a.png)

看到很多隐藏文件，大家以后实战的时候，记得一定一定要关注关注 “.bash_history”

这里记录了这个用户执行过的历史命令，相信你肯定会感兴趣，如图：

![](https://p3.ssl.qhimg.com/t0112ac3dee7a3224f6.png)

是不是很惊喜？但是这个 “morpheus” 是什么东西，权限怎么样呢？

这里可以执行运行本文上篇靶机中用到的命令：

find / -perm -u=s -type f 2>/dev/null

![](https://p1.ssl.qhimg.com/t012d8de895a0496f8f.png)

下面那个…… 不好意思搞错了，再来（配音）

![](https://p2.ssl.qhimg.com/t017fb0b1b5329cd7ec.png)

可以看到权限比较高。。（或者直接上传提权脚本，可以看到该程序所属权限）

然后我们就把执行那个命令复制来执行一下吧。。。

![](https://p2.ssl.qhimg.com/t01caf898463f8c14c5.png)

成功拿到root权限，然后就是拿flag了

![](https://p2.ssl.qhimg.com/t013ad5997c1c98319b.png)

本靶机完！！

## 福利

北京网御星云有限公司-广东办招人啦！！！！ 现需多名销售精英、售前工程师、售后工程师、项目经理、安服人员，有意的请联系邮箱
[panhj@leadsec.com.cn](mailto:panhj@leadsec.com.cn) base地址：广州。
也可联系小弟WeChat（在小弟的前面几篇文章里找。。 贱笑表情） 谢谢您的观看和关注

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/173111](/post/id/173111)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [靶机](/tag/靶机)
  * [htb](/tag/htb)

 **+1** __7赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

