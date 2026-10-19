# 应急响应入门篇-windows分析排查技术（下）

阅读量 **299982**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-15 14:30:26

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01efac09409181d75c.jpg)

> windows应急响应实际分析

## 1-进程分析-可疑进程发现与关闭

**概念** ：  
计算机与外部网络通信是建立在TCP或者UDP协议上的，并且每一次通信都是具有不同的端口（0-65535）。如果计算机被上传木马后，肯定会与外部网络通信，那么此时就可以通过查看网络连接状态，找到对应的进程id，然后关闭进程id并关闭连接状态。

1.netstat -ano | find “ESTABLISHED” //查看网络建立连接状态

![](https://p3.ssl.qhimg.com/t010e7c21f40bde7f7d.png)

2.tasklist /svc | find “PID” 查看具体PID进程对应的程序

![](https://p4.ssl.qhimg.com/t01ba336561e251beac.png)

3.taskkill /PID pid值 /T 关闭进程

![](https://p5.ssl.qhimg.com/t013ce9595e99450bf8.png)

![](https://p1.ssl.qhimg.com/t0197e7a1b83eed6ca7.png)

## 2-异常计划任务排查

**主要是对系统信息的windows计划任务进行排查**

在计算机中可以通过设定计划任务，在固定时间执行固定操作，一般情况下，恶意代码也有可能在

固定的时间设置执行。

使用at命令可以对计划任务进行管理，直接输入at可以查看当前计算机中保存的计划任务。

1.使用at命令查看计算机中保存的计划任务。

![](https://p0.ssl.qhimg.com/t012c77fe88acbb45eb.png)

2.也可以在可视化的任务管理器进行查看。

![](https://p5.ssl.qhimg.com/t01d8e86a4f6cdd5234.png)

3.可以选中运行的任务，然后进行查看详细信息。

![](https://p4.ssl.qhimg.com/t01e415129b8fffce51.png)

4.查看详细内容

![](https://p1.ssl.qhimg.com/t0152ff3d2b776c3eaf.png)

5.可以对异常任务进行停止。

![](https://p2.ssl.qhimg.com/t0173eee41955bd0801.png)

## 3- 隐藏账号发现与删除

隐藏账号，是指“黑客”之后为了能够持久保持对计算机访问，而在计算机系统中加建立的不轻易被发现的计算机账户。

最为简单的隐藏账户建立: net user test$ test /add && net localgroup aministrator test$
/add 其中 $ 符号可以导致管理员在使用net user 时， 无法查看test$用户。

1.使用net user test$ test /add建立临时用户

![](https://p1.ssl.qhimg.com/t01a0db71dd0b75c5bb.png)

2.然后在计算机管理-用户里面查看新建的临时用户。

![](https://p0.ssl.qhimg.com/t013d7fa08e94935923.png)

3.使用net user查看临时用户是否存在。

![](https://p1.ssl.qhimg.com/t01049567240c38403f.png)

4.添加一个新临时用户，然后设置本地组。

![](https://p2.ssl.qhimg.com/t014f48afd43990cb20.png)

5.查看其属性。

![](https://p2.ssl.qhimg.com/t019315ff34bf729667.png)

6.切换用户，然后登录

![](https://p5.ssl.qhimg.com/t01bb1bdf01458fbb3a.png)

7.使用whoami查看用户id。

![](https://p2.ssl.qhimg.com/t014bb4d334209ae439.png)

8.然后在计算机管理查看临时用户属性，发现他隶属于管理员。

![](https://p0.ssl.qhimg.com/t01d68ee632038d8f0f.png)

9.防御措施就是发现临时用户，带有特殊符号的，将其删除。

![](https://p2.ssl.qhimg.com/t01bd8c54d08a5b3855.png)

2.注册表临时用户

![](https://p1.ssl.qhimg.com/t0188a8d476d6ceda67.png)

1.先进入注册表，然后找到SAM，分配权限。

![](https://p3.ssl.qhimg.com/t01516dce2e70f491e0.png)

2.先建立一个临时用户

![](https://p1.ssl.qhimg.com/t010443bbb9f327bf77.png)

3.然后将管理员的文件，加到临时用户上。

![](https://p2.ssl.qhimg.com/t018bed5786f98121fe.png)

![](https://p2.ssl.qhimg.com/t0181232355822532cb.png)

## 4- 恶意进行-发现与关闭

恶意代码在windows系统中运行过程中，将以进程的方式进行展示，其中恶意进程执行着各种恶意行为，对于可执行程序，可以执行使用杀毒软件进行查杀，但是并非所有的恶意程序能够被查杀。此时可以手动查杀，使用工具psexplore，然后利用virustotal.com进行分析。对恶意程序相关的服务进行关闭。

1.使用psexplore进行分析

![](https://p5.ssl.qhimg.com/t0142e475eb876f82e5.png)

2.找到可疑程序，然后查找具体位置。

![](https://p1.ssl.qhimg.com/t016e415522e76dba2e.png)

3.然后在服务里面查看，如果是可疑程序，将它停止。

![](https://p5.ssl.qhimg.com/t01d93f98c2083a4a81.png)

![](https://p2.ssl.qhimg.com/t01734fc0265630275d.png)

## 5- 系统信息 -补丁查看与更新

windows系统支持补丁以修补漏洞。可以使用systeminfo查看系统信息，并展示对应的系统补丁信息
编号，也可以在卸载软件中查看系统补丁和第三方软件补丁。

第一种：使用systeminfo查看具体信息。

![](https://p4.ssl.qhimg.com/t01b8324b9efa88f06b.png)

2.然后在卸载更新里面查看更新补丁。

![](https://p4.ssl.qhimg.com/t01f6d51b77ed5f6c4d.png)

![](https://p5.ssl.qhimg.com/t01524343bebb19ec90.png)

3.win10 更新补丁的方法。

使用win+I快捷键 更新补丁。其他版本的windows也具有windows update的相关操作。

![](https://p2.ssl.qhimg.com/t013d0e8a9d6c2a1364.png)

## 6-webshell发现与查杀

1：D盾专为IIS设计的一个主动防御的保护软件,以内外保护的方式 防止网站和服务器给入侵,在正常运行各类网站的情
况下，越少的功能，服务器越安全的理念而设计！ 限制了常见的入侵方法，让服务器更安全!

<http://www.d99net.net/index.asp>

![](https://p3.ssl.qhimg.com/t019d34a7e49d1fd4a4.png)

![](https://p5.ssl.qhimg.com/t01d584bc120761bc5b.png)

2.河马webshell查杀：<http://www.shellpub.com>

3.深信服Webshell网站后门检测工具：<http://edr.sangfor.com.cn/backdoor_detection.html>

![](https://p0.ssl.qhimg.com/t01f27111cb5e0a13b7.png)

4.Safe3：<http://www.uusec.com/webshell.zip>

![](https://p5.ssl.qhimg.com/t015ffd196a06f46198.png)

## 总结：

本文主要从可疑进程的发现、异常任务的排查、隐藏账户的发现、恶意程序的发现、系统补丁的查看及webshell的查杀来构思。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258955](/post/id/258955)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [windows应急响应](/tag/windows应急响应)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

