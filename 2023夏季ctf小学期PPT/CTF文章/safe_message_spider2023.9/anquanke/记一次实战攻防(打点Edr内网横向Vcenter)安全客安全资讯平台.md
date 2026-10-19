# 记一次实战攻防(打点-Edr-内网-横向-Vcenter)

阅读量 **188022**

发布时间 : 2022-06-23 10:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t016ba10e6881b314ef.png)

## 前言

前不久参加了一场攻防演练，过程既简单也曲折，最后通过横向渗透获取到了vcenter管理控制台权限，成功拿下本次演练目标。

## 寻找目标

目标分配后，面对大范围的目标，首先要做的就是寻找一些容易获取权限的站点，比如shiro、weblogic以及各类反序列化漏洞。之后再将目标锁定到管理后台，使用爆破等手段寻找一些能进后台的账号密码，然后再去找上传点拿shell。

本次渗透在某站注册页面发现了上传身份证的地方，但是上传后发现无返回路径。

![](https://p2.ssl.qhimg.com/t01597ba8d4c2c7c577.jpg)

后通过目录扫描，发现了存在目录遍历漏洞，可以看到不同日期上传的文件

http://IP/upload/Attachment/

![](https://p5.ssl.qhimg.com/t0149cb11e87531f5af.jpg)

然后在对上传点测试时发现存在waf，拦截了非法后缀名、文件内容等。对此进行一些常规的修改和测试例如修改Content-Type、修改boundary前加减空格、多个Content-Disposition字段、分块传输、脏字符最终上传成功。

## 获取webshell

找到上传后的木马获取webshell

![](https://p0.ssl.qhimg.com/t01db11c2bf8c7d45cf.jpg)

拿到webshell发现是IIS权限，通过查看进程发现装有杀软和edr

![](https://p0.ssl.qhimg.com/t0182ef7248de965f1f.jpg)

对木马进行免杀上线CS，然后利用CS插件进行提权时发现失败。

然后通过搜集本机的服务发现开放了1433端口，通过查找配置文件发现了数据库连接地址

![](https://p2.ssl.qhimg.com/t016e8d1b205644e437.jpg)

## 提权system

利用CS开启代理后，登录连接MSSQL数据库，执行命令为system权限

![](https://p3.ssl.qhimg.com/t01486de4bf0fc85cd6.jpg)

最终利用数据库权限执行CS木马上线获取system权限。

## 绕过edr

通过query user查看管理员用户不在线，利用mimikatz获取管理员密码和hash，搭建socks隧道进入目标机远程桌面，发现存在某edr二次验证

![](https://p5.ssl.qhimg.com/t01f33e2e93c81564a6.png)

查询网上资料后发现将该文件删除或重命名即可绕过，成功登录服务器

C:Program Files/Sangfor/EDR/agent/bin/sfrdpverify.exe

登录该管理员主机后，发现阿里云盘，通过搜索阿里云盘文件发现大部分为备份文件，在某一最近更新的项目中发现服务器密码本txt，其中记录的账号密码一台服务器为本机服务器，一台为其它服务器

![](https://p4.ssl.qhimg.com/t0119228968e8ed1165.jpg)

连接密码本中记录的第二台服务器，同时上线CS，有了第二台跳板机后，上传内网扫描工具使用第一台跳板机进行扫描（主要是怕在只有一台跳板机情况下直接扫描容易触发设备告警，造成权限丢失）。同时继续搜集信息，扩大攻击面。

![](https://p0.ssl.qhimg.com/t01070d4a1a13fa2d83.jpg)

## 突破隔离内网横向

最后发现查看本机记录的mstsc发现可连接新网段机器，同时测试发现只有该服务器可访问

![](https://p2.ssl.qhimg.com/t0112db93dd0eb2b186.jpg)

连接该服务器后，继续发现存在套娃服务器xx.xx.xx.7

![](https://p3.ssl.qhimg.com/t016929cc9f3147a864.jpg)

测试发现均不出网，使用CS的中转功能进行中转跳板机上线

![](https://p3.ssl.qhimg.com/t01c810d9a914b5d49c.jpg)

并上传扫描工具对该网段进行扫描，扫描发现该网段存在vcenter管理控制台

![](https://p1.ssl.qhimg.com/t017a5df5bba66202e4.jpg)

## 获取vcenter管理控制权

使用常用的漏洞如CVE-2021-21972、CVE-2021-21985等漏洞进行测试无果后，将目标锁定在该服务器其它端口上，通过全端口扫描发现该服务器还开放41433端口存在MSSQL服务。使用top100弱口令爆破失败后，打算通过搜集拿到的所有服务器、数据库、浏览器等密码进行碰撞。最终运气好碰撞成功，拿到该vcenter服务器权限。

![](https://p3.ssl.qhimg.com/t0192072c2c5dc2522d.jpg)

成功登录该vcenter服务器

![](https://p0.ssl.qhimg.com/t0188050d52e15b32a4.jpg)

最终拿下该目标单位约70余台服务器，20台数据存储等。至此，目标单位出局。

![](https://p5.ssl.qhimg.com/t01d7c1e99dd3e9c6c2.jpg)

## 总结

此次渗透表面看起来丝滑顺畅，实际当中走了不少弯路，尤其是安全防护、安全设备以及蓝队防守人员存在，让打点变得更为困难。同时大量的时间花费在了内网信息搜集上，包括在内网中扫描出不少资产和漏洞，越做越大搜集的信息也越来越多，很容易迷失方向从而会使人变得烦躁，所以在攻防演练中的有限时间内需要根据具体的评分规则进行目的性渗透(刷分)。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/275181](/post/id/275181)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [内网](/tag/内网)
  * [实战](/tag/实战)
  * [横向](/tag/横向)

 **+1** __8赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

