# 应急事件检测 入门篇-Linux信息检测

阅读量 **349043**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-30 15:30:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01642dd9f274998ebd.jpg)

## 一、系统用户信息收集

确定系统中是否有一个看起来可疑的用户

Cat/etc/passwd

![](https://p3.ssl.qhimg.com/t0192283c208ab7f14a.png)

查看用户密码信息，且只有root用户可以查看。

cat /etc/shadow

![](https://p2.ssl.qhimg.com/t01e9bdf58f1e843200.png)

查看用户组信息

cat/etc/group

![](https://p1.ssl.qhimg.com/t01d55595cb8803d70d.png)

快速定位sudo组

![](https://p5.ssl.qhimg.com/t010229251bd8d5c2bd.png)

![](https://p2.ssl.qhimg.com/t01e1eeda09eb21928a.png)

查看当前登录系统用户信息

whoami

w

who

![](https://p0.ssl.qhimg.com/t01ec1123370d5ebc3d.png)

netstat -pantu 查看网络状态

![](https://p4.ssl.qhimg.com/t0129b8d0ad01e6a10c.png)

启动ssh服务。

![](https://p4.ssl.qhimg.com/t01638e424af58e3415.png)

![](https://p5.ssl.qhimg.com/t01de346414e9946c06.png)

使用ssh 127.0.0.1 登录。

last //查看登录记录

lastb //查看登录日志记录

![](https://p1.ssl.qhimg.com/t016345a3142375d929.png)

## 二、linux系统文件信息收集

ls -alh 查看当前路径下的文件信息

![](https://p2.ssl.qhimg.com/t015606ab1180345458.png)

识别系统中任何过大的文件及其权限

find /home/ -type f -size +512k -exec ls -lh {} \; //查看home目录下文件大于512k的文件信息

![](https://p2.ssl.qhimg.com/t01696261bad49e5fbe.png)

找到所有SUID的文件  
find / -perm -u=s -type f 2>/dev/null

![](https://p1.ssl.qhimg.com/t01447d22094291aca2.png)

查找用户有su权限的文件目录。

![](https://p0.ssl.qhimg.com/t012f2721bdda17d777.png)

find命令suid提权  
which find //查看文件路径

chmod u+s /usr/bin/find 给用户添加s的权限

![](https://p0.ssl.qhimg.com/t01f87ae5ef7283fe3b.png)

ls -la /usr/bin/find 查看find的权限

![](https://p4.ssl.qhimg.com/t0190225ecab3d57aff.png)

使用之前的命令，发现他已经被添加到suid文件中。

find / -perm -u=s -type f 2>/dev/null

![](https://p4.ssl.qhimg.com/t01375e86f5d804c0e1.png)

find . -exec “whoami” \; 查看文件权限，权限为root用户的权限

![](https://p3.ssl.qhimg.com/t010089a456f6e78003.png)

创建test文件，查看test的文件权限.

![](https://p3.ssl.qhimg.com/t0165386cad75792d79.png)

## 三、系统资源信息

查看服务器已经运行了多长时间、系统中的当前时间、当前登录了多少用户以及系统的平均负载  
uptime

![](https://p0.ssl.qhimg.com/t0195b27cb55dda4b8d.png)

查看Linux中系统的内存使用情况，系统中使用的物理内存和交换内存，以及内核使用的缓冲区  
free

![](https://p5.ssl.qhimg.com/t01ae121eae003a9c02.png)

检查系统上是否存在未知的挂载  
cat /proc/mounts

![](https://p1.ssl.qhimg.com/t01690694ab7b248b2a.png)

## 四、服务信息

service —status-all //获取当前系统所有服务信息 +开启 -关闭

![](https://p0.ssl.qhimg.com/t01dc3988a47ff21414.png)

cat /etc/crontab 查看计划任务的信息

![](https://p1.ssl.qhimg.com/t0109be946763637b2a.png)

筛选开启的服务

![](https://p4.ssl.qhimg.com/t01f375838ea6279139.png)

more /etc/resolv.conf 查看DNS服务的ip地址

![](https://p4.ssl.qhimg.com/t0162cec3d6c254e332.png)

more /etc/hosts 查看

![](https://p2.ssl.qhimg.com/t0199d473d8934d6ba3.png)

iptables -L -n 查看防火墙规则

![](https://p0.ssl.qhimg.com/t013015637cd1d6aa76.png)

## 五、网络信息收集

arp指令用来管理系统的arp缓冲区，可以显示、删除、添加静态mac地址。  
arp -vn

![](https://p5.ssl.qhimg.com/t015a5b1b48c5f8e100.png)

添加静态映射  
arp -i eth0 -s IP地址 MAC地址

![](https://p5.ssl.qhimg.com/t01b3d5d2c10d2b7801.png)

显示网络连接信息  
netstat -pantu

![](https://p4.ssl.qhimg.com/t0116d1a0e53488bcd6.png)

IP地址信息查看  
ifconfig

    
    
        ip a
    

## 六、应急响应流程

###  01应急响应取证

定义：计算机调查取证，是法医学下的一个分支，与法医相似，计算机调查取证是有关从计算机中获取电子证据并加以分析的过程。  
使调查的结果能够经受法庭的检查。

###  02应急响应根除

    
    
    方法：
        利用杀毒软件、杀毒脚本、手工查杀等方式彻底消除病毒，并检测整个网络系统，以确保不要留下后门。
        针对不同操作系统，使用打补丁、修改安全配置和增加系统带宽的方式，降低安全风险。
    

###  03应急响应恢复

    
    
    方法：
        利用备份文件恢复用户数据和配置信息
        将受到入侵和可能存储漏洞的服务关闭，修改后重启服务
        连接网络，恢复业务，持续监控并进行汇总分析
    

###  04应急响应报告

    
    
    方法：
        1、事情经过
        2、事件成因
        3、评估事件影响
        4、采取措施
        5、事后系统定级、备案、测评等情况
    

## 总结：

本文主要从完整的Linux的应急响应过程出发，主要包括系统用户信息收集、linux系统文件信息收集、系统资源信息、服务信息、网络信息收集，最后梳理整个应急响应流程。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264087](/post/id/264087)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [应急响应](/tag/应急响应)

 **+1** __14赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

