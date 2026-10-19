作者：阿甫哥哥

原文来自：[https://bbs.ichunqiu.com/thread-43500-1-1.html](https://bbs.ichunqiu.com/thread-43500-1-1.html?from=beef)

前言  
我是差不多先生，作为一个不打游戏的人来说，游戏带来不了多大的快感....

> 我过着差不多的日子，吹着差不多的牛逼，写着差不多的代码，有着差不多的朋友圈，花着差不多的闲钱，差不多的又过了一天，skrskr  
>

我正准备过着差不多的夜生活，收到一个我同学差不多的信息，说是绝地求生差不多的活动，我作为一个差不多的伪[白帽](http://bbs.ichunqiu.com/forum-41-1.html?from=beef)，我关了那个差不多的窗口，But，作为他差不多的同学，我点了那差不多的钓鱼，又玩起了那差不多的套路，skrskr

  
![image.png](https://image.3001.net/images/20180731/1533022111_5b600f9f8c589.png!small)  

  

正文

打开那个短网址<http://dwz.cn/O>*****Mm,跳转到了一个域名上<http://www.>**qq.com/

  
![image.png](https://image.3001.net/images/20180731/1533022122_5b600faa208e2.png!small)  

首先，先来一波差不多的信息收集，对，没错，我先查了他的whois，很幸运，他没有开启隐私保护，他的姓名，吴*财(从名字就可以看出来，很缺钱)，邮箱：2******[email]22@qq.com[/email]

  
![image.png](https://image.3001.net/images/20180731/1533022128_5b600fb0b6234.png!small)  

有木有CDN，验证一波？？香港服务器....这种非法站，用香港的很正常....

  
![image.png](https://image.3001.net/images/20180731/1533022187_5b600feb4d343.png!small)  

端口开放检测

  
![image.png](https://image.3001.net/images/20180731/1533022193_5b600ff1d05e5.png!small)  

目录扫描，找一波后台，cool，找到了后台，

![image.png](https://image.3001.net/images/20180731/1533022200_5b600ff8a616d.png!small)  

其他的文件卵用都没有,所以，只好从后台下手了/*admin/index.php

  
![image.png](https://image.3001.net/images/20180731/1533022206_5b600ffea069f.png!small)  

看他这个后台，我心里活动是这样的

  
![image.png](https://image.3001.net/images/20180731/1533022214_5b6010061f818.png!small)  

看到了客服的qq，就是之前whois上的那个qq：2*****22

我慌了，POST注入尝试一波

  
![image.png](https://image.3001.net/images/20180731/1533022220_5b60100cf13e0.png!small)  

不存在注入？？XSS盲打走一波，把能插的地方，全插一遍

  
![image.png](https://image.3001.net/images/20180731/1533022227_5b6010137863c.png!small)  

What？？应该是有差不多的安全软件在网站上

但是我不好受，我也不能让他好受，所以，上Python

  
![image.png](https://image.3001.net/images/20180731/1533022241_5b601021a29a9.png!small)  

在登录处，我发现，只要是数字就行

  
![image.png](https://image.3001.net/images/20180731/1533022250_5b60102af1735.png!small)  

Burp抓包，发现就3个参数u,p,bianhao

  
![image.png](https://image.3001.net/images/20180731/1533022257_5b60103149bc3.png!small)  

所以，我用Python生成一堆随机的qq号跟密码，然后利用requests来循环 POST
垃圾数据到对方的服务器，让他也找不到哪个是真的号，哪个是假的，啊哈哈哈

![image.png](https://image.3001.net/images/20180731/1533022262_5b601036e574f.png!small)  

好了，想不到了，决定去看中国新说唱，让我炸起来，skrskr

啊哈哈，突然想到了，备份文件.....

站长可能没有删备份文件，于是我换了一个扫这个的字典，又是一波乱扫

  
![image.png](https://image.3001.net/images/20180731/1533022269_5b60103de1a53.png!small)  

这就很cool了，下载了这个data.zip发现里面竟然是install.sql

  
![image.png](https://image.3001.net/images/20180731/1533022275_5b601043ea3b3.png!small)  

打开，翻翻数据

  
![image.png](https://image.3001.net/images/20180731/1533022282_5b60104a67f3f.png!small)  

Md5解密

  
![image.png](https://image.3001.net/images/20180731/1533022288_5b601050b375c.png!small)  

密码coolboy，卧槽，Are you kidding me??

额，好吧，找到safecode了，而且没有加密，开心

啊哈哈，这个safecode我第一眼看，身份证号，但是数了一下，14位，不够

352**020***527

不管了，先登录了后台再说

![image.png](https://image.3001.net/images/20180731/1533022296_5b601058dbbcc.png!small)

![image.png](https://image.3001.net/images/20180731/1533022312_5b6010682148d.png!small)

  

除了我批量提交的100000条，至多有73名受害者，不算太多....

批量提交的效果是这样的

  
![image.png](https://image.3001.net/images/20180731/1533022317_5b60106d5b1e6.png!small)  

数据太多了，涉及其他受害者的隐私，所以其他的我就不截图了...

看他没导出数据，所以接下来做的就是立马删除数据

  
![image.png](https://image.3001.net/images/20180731/1533022322_5b6010728fc48.png!small)

![image.png](https://image.3001.net/images/20180731/1533022327_5b60107739d92.png!small)

  

准备修改密码的时候，发现

  
![image.png](https://image.3001.net/images/20180731/1533022333_5b60107d723bc.png!small)  

坑逼，改不了密码，卧槽，心态崩了

既然改不了密码，那行吧，我认了..想办法，getshell

没有上传的地方，任意执行啥的也搞不到...

  
![image.png](https://image.3001.net/images/20180731/1533022344_5b60108833a69.png!small)  

想到了3306,21端口还没有用到

3306貌似不允许远程连接，放弃

21端口，FTP服务走一波

用字典生成，生成了一波很差不多的用户名，很差不多的密码

  
![image.png](https://image.3001.net/images/20180731/1533022350_5b60108e49336.png!small)![image.png](https://image.3001.net/images/20180731/1533022353_5b601091c462a.png!small)![image.png](https://image.3001.net/images/20180731/1533022357_5b601095064ad.png!small)

用户名就是ftp加qq号

密码就是他名字简称加那个safecode

![image.png](https://image.3001.net/images/20180731/1533022366_5b60109e5da60.png!small)  

定位，必须定位一波！！

所以，我又用了阿釉的方法

把xss代码插到了后台那

![image.png](https://image.3001.net/images/20180731/1533022372_5b6010a4636c0.png!small)  

加他qq，了解一波，并开始一波套路

![image.png](https://image.3001.net/images/20180731/1533022378_5b6010aa082c6.png!small)  

空间关闭，百度qq号，只有一些网站类似这样的黑页...

![image.png](https://image.3001.net/images/20180731/1533022383_5b6010af521a6.png!small)  

说实话，我觉得这html写的还没有txt好看，啊哈哈

开始套路他登录后台

  
![image.png](https://image.3001.net/images/20180731/1533022391_5b6010b70cbfc.png!small)  

现在的年轻人真的是，可以，很牛逼，上来就是打技术

  
![image.png](https://image.3001.net/images/20180731/1533022396_5b6010bc5b1ef.png!small)![image.png](https://image.3001.net/images/20180731/1533022398_5b6010beb3a97.png!small)![image.png](https://image.3001.net/images/20180731/1533022404_5b6010c49550f.png!small)

  

然后打到了，现在的人真的是离不开手机了...

![image.png](https://image.3001.net/images/20180731/1533022411_5b6010cb52b8a.png!small)  

![image.png](https://image.3001.net/images/20180731/1533022421_5b6010d555426.png!small)  

丢到经纬度查询的地方

![image.png](https://image.3001.net/images/20180731/1533022427_5b6010dbe8767.png!small)  

定位到了这

福建省宁德市**区****村

过了一会，他又来找我了，真的是年少轻狂

  
![image.png](https://image.3001.net/images/20180731/1533022437_5b6010e56eb5a.png!small)![image.png](https://image.3001.net/images/20180731/1533022441_5b6010e968b2a.png!small)![image.png](https://image.3001.net/images/20180731/1533022448_5b6010f04cbd6.png!small)![image.png](https://image.3001.net/images/20180731/1533022454_5b6010f689d03.png!small)![image.png](https://image.3001.net/images/20180731/1533022466_5b6011026bb26.png!small)![image.png](https://image.3001.net/images/20180731/1533022471_5b6011071df2a.png!small)![image.png](https://image.3001.net/images/20180731/1533022474_5b60110a5af00.png!small)

  

气炸了，写黑页，挂上去，卧槽，这种人必须教训

  
![image.png](https://image.3001.net/images/20180731/1533022486_5b60111607908.png!small)  

我忽然有了一个很大胆的猜测，我怀疑啊，

他的safecode就是身份证的前14位

我既然知道他的姓名，所以来一波爆破，我用了Crazyman_Army表哥的接口

前14位+从0000到9999，验证与名字是否符合，符合就返回，于是我写了一个python程序，这个接口较敏感，就不公开了

爆破了出来，太cool了

![image.png](https://image.3001.net/images/20180731/1533022493_5b60111d1331e.png!small)  

接着，去查身份证照片

  
![image.png](https://image.3001.net/images/20180731/1533022498_5b601122d3b98.png!small)  

卧槽，简直是完美了，接下来，我要找个最炫的黑页，去装逼，啊哈哈哈

![image.png](https://image.3001.net/images/20180731/1533022504_5b60112828ee7.png!small)  

等不到空格表哥炫酷炫到超过最炫民族风的黑页了，只好用这个了

另外把服务器上其他的东西删了，再挂上黑页

  
![image.png](https://image.3001.net/images/20180731/1533022511_5b60112f879ab.png!small)  

去教育一下这个小黑客吧

  
![image.png](https://image.3001.net/images/20180731/1533022517_5b601135d4f79.png!small)![image.png](https://image.3001.net/images/20180731/1533022521_5b601139e3116.png!small)![image.png](https://image.3001.net/images/20180731/1533022534_5b601146ae44f.png!small)

  

这态度转变的，卧槽，简直就是720度托马斯全旋

  
![image.png](https://image.3001.net/images/20180731/1533022542_5b60114e59bce.png!small)![image.png](https://image.3001.net/images/20180731/1533022551_5b6011573a1a0.png!small)![image.png](https://image.3001.net/images/20180731/1533022560_5b60116032a3a.png!small)

反思与总结

小黑客，不公布啥信息了，我还是有着peace and love的，作为祖国的一棵绿萝，我还是得好好的保护未来祖国的花朵的，啊哈哈哈

大家在互联网上行走，还是要做好自己的个人信息保护..最好不要用同一套密码，不要把自己的隐私数据(身份证号之类的)放在互联网上

  

点击[“阅读原文”](https://bbs.ichunqiu.com/thread-43500-1-1.html?from=beef)即可下载文章中所用工具哦~  

