# 从外网到域控（vulnstack靶机实战3）

阅读量 **945993**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-12 11:30:52

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01b1ecef973b4c4fc7.jpg)

## 前言

大家好，我是鸿鹄实验室的lengyi，团队小伙伴发来的一个靶机，说是根据红日靶机改得，让我打一下，于是便有了该文。整个流程为黑盒测试，只有一个目标Ip：192.168.0.108，

## 外网渗透

下面开搞：

访问目标Ip发现却发现是空页面：

![](https://p4.ssl.qhimg.com/t016da7218d3fefc9a4.png)

估计是作者改了端口，尝试常见的8080、8000、8888、8090等，在8080找到了目标站点,一个信呼oa：

![](https://p3.ssl.qhimg.com/t01c998cdee43c0c1ad.png)

因为是靶机系统，估计也不会很难，果然admin、123456弱口令进入后台。

![](https://p3.ssl.qhimg.com/t0171bd2c5bb8427599.png)

且系统版本较低：

![](https://p3.ssl.qhimg.com/t011edb415a3be71d69.png)

因为之前做的项目中，曾经遇到过这个oa知道它存在注入漏洞（<https://www.seebug.org/appdir/rockoa>)
且后台上传较难突破，于是便考虑使用注入进行下一步攻击，若是root则直接getshell，使用sqlmap进行如下操作：

    
    
    sqlmap -u 'http://192.168.0.108:8080/index.php?a=movefile&m=word|system/word&ajaxbool=true' --data="fid=1" 
    --cookie "PHPSESSID=369fdatmhlacnkfkudg8bd7106; deviceid=1580038026865; xinhu_mo_adminid=1; xinhu_ca_adminuser=admin; xinhu_ca_rempass=0" 
    --level 5 --risk 3 --technique=T --current-db --current-user -p 'fid'
    

即可成功注入，但是发现并不是root权限，这条路暂时就死掉了。俗话说，遇事不绝扫目录，拿上dirsearch进行简单的目录遍历，发现了一些敏感目录：

![](https://p5.ssl.qhimg.com/t011c5b51a6538eea62.png)

访问upload发现了jquery上传组件：

![](https://p3.ssl.qhimg.com/t015d7cd388ddd94430.png)

关于这个组建网上有比较流行的三个漏洞，具体介绍可以看（[https://blog.csdn.net/niexinming/article/details/86268694）](https://blog.csdn.net/niexinming/article/details/86268694%EF%BC%89)
右键查看到版本之后，发现应该存在CVE-2018-9206，使用poc进行测试：

![](https://p1.ssl.qhimg.com/t01456b49f0a05bb585.png)

蚁剑连接成功，成功getshell.

![](https://p1.ssl.qhimg.com/t0166836061ae39ad9b.png)

简单查看了一下，发现并无杀软，msf生成木马，蚁剑传马，执行上线：

![](https://p4.ssl.qhimg.com/t017bb52397db821444.png)

## 内网初探

发现为域环境，添加路由，进行主机发现

![](https://p0.ssl.qhimg.com/t01874c9e61e028391d.png)

![](https://p0.ssl.qhimg.com/t018785728d4ad90f1f.png)

得到三台加入test域的windows主机

  * 192.168.93.20 windows server 2008
  * 192.168.93.30 windows 7
  * 192.168.93.10 windows server 2012

我们先来抓一下08的密码，万一可以使用相同的密码渗透win7呢，我个人喜欢msf交互式运行mimikatz进行密码抓取,具体操作参考（[https://lengjibo.github.io/rt/）](https://lengjibo.github.io/rt/%EF%BC%89)

![](https://p3.ssl.qhimg.com/t012b76e7e2acc142c1.png)

获得密码为123qwe!然后使用socks将目标代理出来，nmap扫描发现没有开启3389。

使用抓到的08的密码登录smb也失败了，尝试使用msf进行爆破登录，竟然成功了…

![](https://p3.ssl.qhimg.com/t013cc8b5dc8a394ee5.png)

尝试psexec反弹正向shell

![](https://p0.ssl.qhimg.com/t01b4210003961a3d42.png)

发现执行失败，猜测可能有像applocker类的防护，使用wmiexec执行命令，发现可以成功执行：

![](https://p1.ssl.qhimg.com/t0155b1353a3b454971.png)

先来试以绕过applocker的方法能不能成功，关于applocker后续我会出一个系列文章讲解，我这里使用CMSTP的方法，使用msf生成dll，inf包含的方法进行绕过

大体的inf写法如下：

    
    
    [version]
    Signature=$chicago$
    AdvancedINF=2.5
    [DefaultInstall_SingleUser]
    RegisterOCXs=RegisterOCXSection
    [RegisterOCXSection]
    C:Userstest.PENTESTLABpentestlab.dll
    [Strings]
    AppAct = "SOFTWAREMicrosoftConnection Manager"
    ServiceName="Pentestlab"
    ShortSvcName="Pentestlab"
    

将生成的文件传到08上面，再使用wmiexec使用certutil进行下载，

![](https://p3.ssl.qhimg.com/t0119eb829689471ef3.png)

然后使用cmstp执行，msf获得shell

![](https://p3.ssl.qhimg.com/t01928e6902746b149f.png)

![](https://p1.ssl.qhimg.com/t0139150848883f0ab1.png)

且直接为system权限：

![](https://p2.ssl.qhimg.com/t011c6162287bba27b9.png)

## 进攻域控

下面开始进攻域控，经过ping域控得知域控ip 192.168.93.10。

![](https://p0.ssl.qhimg.com/t010c8fe749d9d07d00.png)

初步查看域控上没有什么服务，只能在其他机器上找突破，后来发现08上有域控的进程。

![](https://p4.ssl.qhimg.com/t014a6798f68eb99110.png)

使用mimikatz抓取到域控密码，最后全部上线：

![](https://p5.ssl.qhimg.com/t01e5014e3965ba1f46.png)

当然域环境有些问题，不过倒也是没有影响这次渗透。

![](https://p2.ssl.qhimg.com/t01d5a3e838117985e2.png)

## 总结

总的来说，靶机较为基础，考察点也还不错，希望各位能够喜欢吧。有域靶机的可以私我哦，在线出writeup。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197651](/post/id/197651)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [内网渗透](/tag/内网渗透)

 **+1** __15赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=2hg9QXf8DckJiaJsCgrkSvA&s=40) 安

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

