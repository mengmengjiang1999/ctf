# 靶机入侵——PumpkinGarden靶机+PumpkinRaising靶机

阅读量 **282435**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-31 11:30:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01b131faeb40156bd2.png)

## 前言

hello大家好，我是d3ckx1 小号扣扣：6114157，最近工作真的是忙到飞起，今天终于有时间给大家更新靶机文章了。

## 靶机下载/安装

PumpkinGarden靶机：<https://pan.baidu.com/s/1PbX73TXWdI6fL3KuY6SrwA>

PumpkinRaising靶机：<https://pan.baidu.com/s/1wK5DxaFgXbBxEN2Sn69EUg>

PumpkinGarden靶机IP：172.16.24.87

PumpkinRaising靶机IP：192.168.6.138

## 实战

###  PumpkinGarden靶机

第一步还是老规矩，nmap开路：

![](https://p1.ssl.qhimg.com/t0187d0f91411bfbd98.png)

可以看到该靶机开放了3个端口，分别是21、1515、3535 端口。

可以看到ftp的21端口，存在匿名登陆，我们试一下

![](https://p2.ssl.qhimg.com/t012a947a312e59f6e3.png)

下载“note.txt”，查看一下：

![](https://p0.ssl.qhimg.com/t017af9a635ac851431.png)

下面我们继续跟进查看1515端口http服务，如图：

![](https://p4.ssl.qhimg.com/t01cb607cc8736edcd1.png)

查看源码

![](https://p2.ssl.qhimg.com/t016e6165c18cda2152.png)

说image里会有帮助，我们使用目录猜解工具跑一下吧，

![](https://p4.ssl.qhimg.com/t01db7e56ae65b80301.png)

出现“/img”目录，我们查看一下

![](https://p0.ssl.qhimg.com/t016fbfbb8f12c51c02.png)

继续跟进“hidden_sercret”

![](https://p3.ssl.qhimg.com/t013465cba94d928f98.png)

拿到base64的加密密文，解密一下看看

![](https://p1.ssl.qhimg.com/t01d43e4aa12bd4d2f7.png)

成功拿到账号密码：scarecrow – 5Qn@$y ，

下一步我们使用ssh登陆

![](https://p1.ssl.qhimg.com/t01f089ae40ad0d582b.png)

成功登陆，下一步就是提权了

![](https://p0.ssl.qhimg.com/t018d01d6a30d3ed41b.png)

拿到“goblin”用户的密码，我们先看一下有没有“goblin”用户

![](https://p5.ssl.qhimg.com/t017f04f6bfa75fe758.png)

在/home 目录下看到有“goblin”目录，说明有这个用户，下一步直接“su goblin”,输入密码就行，成功切换到了“goblin”用户

![](https://p4.ssl.qhimg.com/t013e191926313de3b9.png)

如上图，看到给了我们提权的参考bash文件，我们直接down下来，查看。

![](https://p4.ssl.qhimg.com/t01734c70618a267e19.png)

看到这个小伙伴们肯定有点懵，这个是什么鬼，怎么用。。。

好吧，其实具体操作是这样的，如图：

![](https://p3.ssl.qhimg.com/t0196ab98a9116556a5.png)

其实就是把上面代码复制一下，输入就行了。

然后下一步就是给该文件权限，执行就行。

但是靶机设置了/tmp的清除，所以我测试了好久，都被很快清理掉了，所以我就直接在本地写好，然后在靶机上下载这个文件，

![](https://p0.ssl.qhimg.com/t01ecea5aa0e58b5f62.png)

然后执行，成功拿到root权限

![](https://p4.ssl.qhimg.com/t0150a373586997b1cf.png)

拿到flag

![](https://p2.ssl.qhimg.com/t01ae1fdd90c6cf881a.png)

本靶机完！

###  PumpkinRaising靶机

1.老规矩，nmap探测目标

![](https://p5.ssl.qhimg.com/t015ad603a9694a1b43.png)

如图开放了2个端口，分别是80、22，查看80端口

2.如图：

![](https://p4.ssl.qhimg.com/t0133e704339f5b9d79.png)

获取到可疑用户名“jack”

3.习惯性右击查看源码，有发现

![](https://p2.ssl.qhimg.com/t016d94eaf558be52f7.png)

看到2个敏感信息，逐个查看

![](https://p2.ssl.qhimg.com/t0111f4a1c1ca79afc0.png)

Base64解密该密文，发现就是个介绍说明，下一步继续更加 “pumpkin.html”

![](https://p5.ssl.qhimg.com/t015b5e793589c706f0.png)

我们继续往下拉：

![](https://p3.ssl.qhimg.com/t019959de881a271b95.png)

又是一个密文，先解密第一个

![](https://p3.ssl.qhimg.com/t010ab921daa23755d7.png)

这是个典型的base32密文，小伙伴可以查看该文章地址：“<https://blog.csdn.net/mignonmi/article/details/81877568>
”

下一步继续下载跟进，“/scripts/spy.pcap”

![](https://p0.ssl.qhimg.com/t01a757809e3b888976.png)

![](https://p3.ssl.qhimg.com/t019dc21435bfa1eb04.png)

![](https://p2.ssl.qhimg.com/t0106b976e8313293f9.png)

![](https://p0.ssl.qhimg.com/t0164320df2282205a1.png)

![](https://p5.ssl.qhimg.com/t014c2d940629b5664a.png)

逐个包里是“jack”、“mark”用户的对话信息，我们拿到了敏感ID：“50609”。

继续解密上面的那个密文，玩ctf的朋友肯定一眼就知道了，这是十进制加密

![](https://p1.ssl.qhimg.com/t015d3ba0b82c246581.png)

又得到一个ID，至于干嘛用的，我也不知道。。。。

4.下面继续回来查看“rebots.txt”

![](https://p2.ssl.qhimg.com/t01203a5f7084b161fd.png)

逐个查看

![](https://p3.ssl.qhimg.com/t010a16fba1d8fae169.png)

![](https://p5.ssl.qhimg.com/t01fa2f0746fbee4203.png)

下载该图片，应该是ctf中常见的图片隐写技术，试一下看看

![](https://p1.ssl.qhimg.com/t0114fbef23d2e05c5b.png)

正常，继续，使用strgosuite工具查看

![](https://p4.ssl.qhimg.com/t01cc756b22d5be885b.png)

需要输入密码，那密码哪里等那？我们回到前面的另外文件文本目录查看

![](https://p0.ssl.qhimg.com/t014fa2d47100eca21c.png)

逐一作为密码尝试

![](https://p0.ssl.qhimg.com/t01a85cc05aeba86e3f.png)

成功拿到被隐写在图片内的文件，查看文件

![](https://p3.ssl.qhimg.com/t018da4a26607db73fc.png)

5.下面继续下载查看跟进

![](https://p1.ssl.qhimg.com/t01a6ccc1f079b40b6d.png)

可以看到是个Pretty Good Privacy ，使用命令解密：

![](https://p3.ssl.qhimg.com/t013d84933b28e0187e.png)

但是要密码

![](https://p2.ssl.qhimg.com/t010b67b0d0a09cdf07.png)

这里我被卡了很久，试了好多目标的密码都不行，最后在首页上的

![](https://p1.ssl.qhimg.com/t017d6df02327735bf9.png)

组合起来得到正确的密码：SEEDWATERSUNLIGHT （简直了。。。。）

![](https://p5.ssl.qhimg.com/t01842a776c5ab93812.png)

成功打开后，但是这又是什么密文那？

如果是经常打ctf的 小伙伴肯定就知道了，没错这就是摩斯电码，

![](https://p4.ssl.qhimg.com/t01d4cec402bf9808ea.png)

成功解密

到现在为止一共得到4个ID：“50609”、“96454”、“86568”、“69507”

下一步如果没猜错的话，这个可能跟上面的密码组合一样，几个ID合起来可能是“jack”或者“mark”的密码，结果多次组合尝试，最后的密码是：“69507506099645486568”

![](https://p5.ssl.qhimg.com/t01213ff5687cf0a2e5.png)

下一步提权

![](https://p5.ssl.qhimg.com/t0106062c009d5cc6f1.png)

可以看到 “/usr/bin/strace” 可不需要密码执行，然后我们的提权步骤是这样的，

如图：

![](https://p4.ssl.qhimg.com/t0108d1b9374c40eb6f.png)

成功拿到root权限和flag！

本靶机完！！！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182889](/post/id/182889)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [靶机入侵](/tag/靶机入侵)
  * [靶机](/tag/靶机)

 **+1** __14赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

