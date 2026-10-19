# 应急响应入门篇-Linux分析排查技术（上）

阅读量 **211251**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-22 16:30:45

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t015bc3fad101be7f66.jpg)

## 前言：

当企业发生黑客入侵、系统崩溃或其它影响业务正常运行的安全事件时，急需第一时间进行处理，使企业的网络信息系统在最短时间内恢复正常工作，进一步查找入侵来源，还原入侵事故过程，同时给出解决方案与防范措施，为企业挽回或减少经济损失。  
针对常见的攻击事件，结合工作中应急响应事件分析和解决的方法，总结了一些 **Linux** 服务器入侵排查的思路。

## 01文件分析-敏感文件信息

在linux系统下一切都是文件，其中/tmp是一个特别的临时目录文件。每个用户都可以对它进行读写操作。因此一个普通用户可以对/tmp目录执行读写操作。

查看敏感目录文件，如 tmp目录、可执行程序目录/usr/bin ，/usr/sbin等

1.使用la -alt / 查找tmp目录

![](https://p0.ssl.qhimg.com/t01a0de731bf2f454a7.png)

2.使用ls —help 查看帮助信息

![](https://p1.ssl.qhimg.com/t013b54cc957fc45692.png)

3.ls的常用用法：  
ls 用来显示目录列表

-a 显示所有档案及目录

-l 以长格式显示目录下的内容列表

-t 用文件和目录的更改时间排序

![](https://p0.ssl.qhimg.com/t016ec1497a2c0c4e8b.png)

4.进入tmp目录，查找最近新添加的可疑文件。

![](https://p4.ssl.qhimg.com/t01a676aef9efe0ae60.png)

## 02文件分分析-敏感文件信息

查看开机启动项内容/etc/init.d/，恶意代码很有可能设置在开机启动的位置。

查看指定目录下文件时间顺序的排序：ls -alt | head -n 10

查看文件时间属性: stat 文件名

使用ls -alh /etc/init.d // 查看开机启动项

![](https://p3.ssl.qhimg.com/t01633f8dafe706d237.png)

![](https://p1.ssl.qhimg.com/t010a006cdb0369df68.png)

进入开机启动项目录，对其进行筛选。

![](https://p4.ssl.qhimg.com/t0147208eaafec0ab92.png)

针对可以文件可以使用 **stat** 进行创建修改时间、访问时间的详细查看，若修改时间距离时间日期接近，有线性关联，说明可以被篡改。

如：stat apache2 查看文件详细信息。

![](https://p2.ssl.qhimg.com/t0156ade2ba69475a93.png)

## 03文件分析-敏感文件信息

主要针对 **新增文件** 分析：

查找24h内被修改的文件

find ./ -mtime 0 -name “*.php”

查找72h内新增的文件

find ./ -ctime -2 -name “‘*.php”

权限查找，在linux系统中，如果具有777权限，那么文件就很可疑。

find ./ -iname “*.php” -perm 777 其中 -iname忽略大小写，-perm用于设定筛选文件权限

![](https://p0.ssl.qhimg.com/t014b532a606b7041de.png)

find ./ -ctime -2 -name “‘*.txt” //查找72h内新增的txt文件。

![](https://p0.ssl.qhimg.com/t01bcfc50f9c32b93ad.png)

find ./ -iname “*.php” -perm 777 //查找最近新建的含.php文件的，具有最高权限的文件。

![](https://p1.ssl.qhimg.com/t01fed98c2d87be665d.png)

新建立一个z.php文件，给予最高权限。

![](https://p2.ssl.qhimg.com/t0153aa150b3dc14bd2.png)

再次进行筛选。

![](https://p3.ssl.qhimg.com/t012c22fd2ad707ce5a.png)

## 04-网络连接分析

**在linux中可以使用netstat进行网络连接查看**

netstat -Print network connections，rounting tables，interface
statistics，masquerade connections，and multicast memberships

具体帮助信息查看 man netstat

常用命令 **netstat -pantl** 查看处于tcp网络套接字相关信息

关闭未知连接使用 **kill -9 pid** 既可关闭。

使用：netstat -pantl 查看处于tcp网络套接字相关信息

![](https://p5.ssl.qhimg.com/t0175147d0ebaf855ee.png)

ip a 查看网络信息

![](https://p2.ssl.qhimg.com/t01ed87345b926f20b8.png)

发现可疑进程，使用 kill -9 + pid值，然后关闭进程。

![](https://p0.ssl.qhimg.com/t011d16221890477287.png)

## 05-进程分析-进程所对文件

使用ps命令，分析进程。根据netstat 定位出pid ，使用ps命令，分析进程

使用ps aux 查看你所有进程信息

![](https://p0.ssl.qhimg.com/t01c9b6cc17cd60f0a9.png)

ps aux | grep “22” 查看最近使用了22端口的进程。

![](https://p2.ssl.qhimg.com/t016d7e40dc24d27538.png)

使用pid进行筛选

![](https://p5.ssl.qhimg.com/t01c90f86dba0aa27b4.png)

![](https://p1.ssl.qhimg.com/t01c30924c4161c67d2.png)

![](https://p3.ssl.qhimg.com/t012b899b43263b921c.png)

筛选 pid为647的 进程。

![](https://p1.ssl.qhimg.com/t01f31498953c0c5a2b.png)

![](https://p5.ssl.qhimg.com/t011a7e6bf60f5aeed5.png)

查看端口未22的隐藏进程

![](https://p1.ssl.qhimg.com/t01e920a7f6b2953649.png)

## 06-登录分析-筛选异常登录

在Linux做的操作都会被记录到系统日志中，对于登录也可以查看日志信息查看是否有异常登录

last命令记录着所有用户登录系统的日志，可以用来查找非授权用户的登录事件，而last命令的输出结果来源于 **/var/log/wtmp**
文件，稍有经验的入侵者都会删掉  
/var/log/wtmp以清除自己行踪，但是还是会露出蛛丝马迹在此文件中的

last -i grep -h 0.0.0.0 查看登录日志，筛选非本地登录

![](https://p1.ssl.qhimg.com/t01d251661dc327eba8.png)

last -i //查看登录日志，含登录ip地址。

![](https://p2.ssl.qhimg.com/t01d534423c0a5be758.png)

last -i grep -v 0.0.0.0 查看登录日志，筛选非本地登录

![](https://p3.ssl.qhimg.com/t01a33a2cf105453593.png)

![](https://p2.ssl.qhimg.com/t01d526d92d9d66800a.png)

**常见的用法** ：  
who 查看当前登录用户（tty本地登陆 pts远程登录）  
w 查看某一时刻用户的行为  
uptime 查看有多少用户，以此确定是否存在异常用户  
lastb 显示登录失败次数，判断是存在ssh爆破  
last 显示用户最近登录信息。  
lastlog 登录成功记录

## 总结：

本文主要总结了在遇到了Linux系统时，应急响应先从对敏感文件分析、敏感文件信息、网络连接分析、进程分析、异常登录记录进行分析。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Arthur** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/259764](/post/id/259764)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [应急响应](/tag/应急响应)

 **+1** __10赞

 __收藏

![](https://p3.ssl.qhimg.com/t010857340ce46bb672.jpg) Arthur

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

