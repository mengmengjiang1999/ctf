## 一 前言

**Vulnhub是一个提供各种漏洞环境的靶场平台，供安全爱好者学习渗透使用，大部分环境是做好的虚拟机镜像文件，镜像预先设计了多种漏洞，需要使用VMware或者VirtualBox运行。每个镜像会有破解的目标，大多是Boot2root，从启动虚机到获取操作系统的root权限和查看flag。**

 ****网址：<https://www.vulnhub.com> ****

## 二 运行说明

靶机名称：[Os-Bytesec](https://www.vulnhub.com/entry/hacknos-os-bytesec,393/)

靶机难度：初学者/中级

目标：有两个flag，一个user-flag，一个root-flag

攻击机：kali linux，IP地址192.168.199.216

靶机：os-bytesec，IP地址192.168.199.148

## 三 渗透过程

### ip发现

首先打开kali linux，扫描kali网段中目前存活的ip，目前有6个存活ip。

    
    
    nmap -sP 192.168.199.1/24

![](https://image.3001.net/images/20191204/1575426761_5de71ac9ddd71.png!small)

启动ByteSec靶机，界面如下：

![](https://image.3001.net/images/20191204/1575426922_5de71b6aedab6.png!small)

没有直接告诉ip地址，看来需要我们自己探测了。

由于攻击机和虚拟机网络设置均为桥接模式，使用Nmap扫描kali网段C段ip，即可找到靶机ip，命令：

    
    
    nmap -sP 192.168.199.1/24

多出一个ip，和上面6个ip进行比对，获得靶机ip：102.168.199.148

![](https://image.3001.net/images/20191204/1575427061_5de71bf515c74.png!small)

### 端口和服务识别

ip已经有了，我们来看看Ta开了什么端口吧。使用nmap扫描1-65535全端口：

    
    
    nmap -v -A -sS -Pn -T4 -p 1-65535 192.168.199.148

![](https://image.3001.net/images/20191204/1575427164_5de71c5cded15.png!small)

目标开放端口如下：

端口 | 状态 | 服务 | 版本  
---|---|---|---  
80/TCP | open | http | Apache httpd 2.4.18 ((Ubuntu))  
139/TCP | open | smb | Samba smbd 3.X - 4.X  
445/TCP | open | smb | Samba smbd 4.3.11-Ubuntu  
2525/TCP | open | ssh | OpenSSH 7.2p2 Ubuntu  
  
### 网站查看

好了，先看看这个网站有什么线索吧。网站主页如下：

![](https://image.3001.net/images/20191204/1575427305_5de71ce996722.png!small)

导航栏上都点开看看是什么，home是主页，点击gallery，是一些图片，一一查看，没什么有价值的。查看源代码，也没什么有用的线索。

![](https://image.3001.net/images/20191204/1575427683_5de71e63ab77f.png!small)

点击news，也是一张图片，难道它再向我暗示着什么吗？

![](https://image.3001.net/images/20191204/1575427753_5de71ea92f7f3.png!small)

哎，从这些线索看暂时还无头绪。从网站看暂时还不能给我们提供什么有价值的信息。

### 爆破目录

爆个目录看看吧，这里使用dirb进行目录爆破。

    
    
    Dirb<http://192.168.199.148/>

[](http://192.168.199.148/)

![](https://image.3001.net/images/20191204/1575427921_5de71f5148e4b.png!small)

哦！看来也没扫出来什么！看来只能先放下网站，看看smb有什么漏洞可利用吗？

### 测试SMB

一说到smb，诸位表哥第一印象肯定是Windows的MS-17-010了，正当我计划祭出msf准备一梭子收的时候，才猛然想起目标机器是Ubuntu系统。尴尬了！咳咳！smb，Ubuntu系统中smb利用还没接触过，怎么办？

![](https://image.3001.net/images/20191204/1575428634_5de7221a293b8.png!small)

遇到不懂得，首先就百度，哈哈。

![](https://image.3001.net/images/20191204/1575428763_5de7229be2e0d.png!small)

看来有戏，看一下smbclient的用法：

    
    
    smbclient//ip/myshare -U xxxx

一遇见登录，首先肯定要试试弱密码，经过多次尝试，测出账户名为smb，密码为空。

![](https://image.3001.net/images/20191204/1575429332_5de724d436e16.png!small)

ok！接下来要好好看看里面有什么东西了。里面一共就2个文件。

![](https://image.3001.net/images/20191204/1575429540_5de725a437617.png!small)

把safe.zip下载到本地。下载到本地后尝试解压，发现解压需要密码。

![](https://image.3001.net/images/20191204/1575430524_5de7297c34c04.png!small)

有密码？弱口令继续安排上。什么，不行？不行就爆破安排上，没有爆不出来的密码。各位表哥有更好的压缩包爆破工具或自己写的爆破工具都可以自己安排。这里我用的是fcrackzip，如果没有的，使用下列命令安装：

    
    
    apt-get install fcrackzip

爆破使用kali自带的字典，使用fcrackzip爆破如果要使用字典，必须加上-p参数，-u 是指定zip 格式

    
    
    fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u safezip

![](https://image.3001.net/images/20191204/1575431011_5de72b6339fb4.png!small)

解出压缩密码，然后进行解压得到两个文件，secret.jpg和user.cap

![](https://image.3001.net/images/20191204/1575431037_5de72b7d49d8b.png!small)

### user-flag

用Wireshark打开user.cap看了下，是个无线数据包。使用aircrack-ng破解user.cap文件。

![](https://image.3001.net/images/20191204/1575431157_5de72bf5c15c3.png!small)

找到一个用户名 blackjax 和密码 snowflake。然后尝试ssh连接测试，成功连接。

![](https://image.3001.net/images/20191204/1575431198_5de72c1e5d19a.png!small)

查看下当前目录有什么文件，发现当前目录有个user.txt文件。

![](https://image.3001.net/images/20191204/1575431252_5de72c540d2c2.png!small)

查看文件内容：

![](https://image.3001.net/images/20191204/1575431264_5de72c605972c.png!small)

至此发现了第一个user-flag，解码后得abhishek，看来还有一个root的flag，估计是需要提升权限才能看到了。

### 权限提升

查看靶机Ubuntu版本号，根据当前版本搜索有没有可利用的提权方法。

不断查找提权方法，不断测试（由于篇幅原因，测试失败的就不一一列举了），功夫不负有心人，终于找到了一篇讲解各种方法进行Linux提权的的[文章](https://www.anquanke.com/post/id/146799)。

由于目标系统未安装gcc且当前权限也限制安装，需要gcc编译的那一步无法完成。但我们目前情况和作者例子中的一样，同样登录到目标系统，然后进入提权阶段。我们先尝试按文章中作者步骤走，看能否成功？

在find命令的帮助下不浪费时间的搜索具有SUID或4000权限的文件。

    
    
    find / -perm -u=s -type f 2>/dev/null

![](https://image.3001.net/images/20191204/1575431459_5de72d23ed653.png!small)

然后我们进入/usr/bin，看到netscan比较可疑，因为scan，各位表哥应该都懂。所以我们运行这个文件，在这里它看起来像文件netscan试图运行netstat，这是一个真正的在/bin中的文件可以查看端口状态。

![](https://image.3001.net/images/20191204/1575431512_5de72d58e0ebb.png!small)

继续进行下一步

    
    
    cd /tmp 
    
    echo "/bin/sh" > netstat
    
    chmod 777 netstat 
    
    echo $PATH 
    
    export PATH=/tmp:$PATH 
    
    cd /usr/bin 
    
    ./netscan 
    
    whoami

![](https://image.3001.net/images/20191204/1575433442_5de734e27e5e6.png!small)

### root-flag

成功提权至root权限。进入root目录下，有个root.txt文件，查看文件。

![](https://image.3001.net/images/20191204/1575433474_5de7350233df6.png!small)

到此，2个flag：user-flag和root-flag已全部找到。

## 四 总结

主要突破点：

> 通过SMB获取共享文件；
>
> 通过爆破获取密码；
>
> 从user.cap获取账户和密码；
>
> 利用$PATH变量提权。

遇见的坑：

> 未仔细查看靶机介绍，在VMware中打开靶机后，靶机无法自动获取到ip（有表哥可以的话请告诉我怎么设置得）；
>
>
> 在网站上耗费时间较长，爆破目录，fuzz敏感文件等，还是不要死磕到底，一击不中换其他目标，也不是说彻底放弃，暂时没思路小本本先记着，也许哪天有个灵感再返回来测；
>
> 爆破压缩包密码开始先用了-b参数暴力破解，比较耗费时间。

## 参考链接

> fcrackzip 用法：<https://blog.csdn.net/linux_hacher/article/details/78470513>
>
> 利用 PATH 环境变量进行 Linux 提权：<https://www.anquanke.com/post/id/146799>

 ***本文作者：VVhAt2，转载请注明来自FreeBuf.COM**

