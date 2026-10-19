## 一、背景介绍

**国外某安全厂商捕获到了一例KillDisk最新的变种样本，此样本已经感染了国外某家银行系统，数千台电脑及服务器系统被破坏，导致银行的SWIFT转帐系统无法正常使用。**  

KillDisk是由一个叫[TeleBots]的黑客团伙开发的，是一款破坏性的恶意程序，它专门用于擦除受害者硬盘上的文件，最近几年发展为勒索软件的功能，2015年被利用于针对乌克兰进行的APT攻击之中，旨在破坏乌克兰的电力和能源系统，去年曾发现它的一个变种用于Linux下的勒索病毒，最近又被发现利用攻击某国银行的转帐系统的主机。

深信服EDR安全团队，密切关注此破坏性病毒的最新进展，并第一时间拿到相关的恶意样本，进行了深入的分析研究，并能有效检测防御此类恶意样本。

## 二、样本分析

(1)样本图标如下：

![图片.png](https://image.3001.net/images/20180614/15289401032949.png!small)

(2)通过查壳，发现它使用了VMProtect v.2.07 - X.X进行加壳了，如下：

![图片.png](https://image.3001.net/images/20180614/15289401089084.png!small)

(3)样本加载之后，如下所示：

![图片.png](https://image.3001.net/images/20180614/15289401128337.png!small)

(4)样本使用VMP2.0.7版本的壳，对VMP进行动态跟踪，可以到达加壳程序的内部，如下：

![图片.png](https://image.3001.net/images/20180614/15289401188723.png!small)

(6)查看程序中的相关字符串信息，如下：

![图片.png](https://image.3001.net/images/20180614/15289401238480.png!small)

(7)查看反汇编代码，可以看到一些关于MBR Kill Setup的代码段，如下：

![图片.png](https://image.3001.net/images/20180614/15289401272339.png!small)

(8)动态调试，跟踪安装感染MBR的代码，如下：

![图片.png](https://image.3001.net/images/20180614/15289401318236.png!small)

(9)通过调用释放在临时目录下的System.dll导出函数Call进行安装感染，如下：

![图片.png](https://image.3001.net/images/20180614/15289401358986.png!small)

System.dll导出函数Call，如下：

![图片.png](https://image.3001.net/images/20180614/15289401406713.png!small)

(10)通过遍历\\\\.\PHYSICALDRIVE%d进行修改感染，如下：

![图片.png](https://image.3001.net/images/20180614/15289401449739.png!small)

(11)通过System.dll中的Call函数，调度CreatFileA读取MBR扇区，获取MBR扇区的文件句柄，如下：

![图片.png](https://image.3001.net/images/20180614/15289401481668.png!small)

(12)通过WriteFile函数修改MBR，如下:

![图片.png](https://image.3001.net/images/20180614/15289401527058.png!small)

(13)遍历磁盘完成之后，然后通过ExitWindowsEx函数来重启主机。

![图片.png](https://image.3001.net/images/20180614/15289401564613.png!small)

## 三、预防措施

同时深信服EDR安全团队提醒用户：

> 1.不要点击来源不明的邮件以及附件
>
> 2.及时给电脑打补丁，修复漏洞
>
> 3.不从垃圾网站或不明网站下载软件
>
> 4.安装专业的终端/服务器安全防护软件

## 四、相关IOC

### MD5

> C1831BAA5505F5A557380E0AB3F60F48
>
> 9E33143916F648EC338F209EB0BD4789

***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

