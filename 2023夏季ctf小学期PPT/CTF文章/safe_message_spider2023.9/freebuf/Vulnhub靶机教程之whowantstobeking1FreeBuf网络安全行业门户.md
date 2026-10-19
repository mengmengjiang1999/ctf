# 靶机概况

下载地址

    
    
    https://www.vulnhub.com/entry/who-wants-to-be-king-1,610/
    

## 靶机描述

### Description

    
    
    Google Is Your Friend
    
    Difficulty: Begginer
    
    "Remember using 'strings'"
    
    Twitter: @ArmBjorn
    
    Work in Virtualbox.
    
    Get root permissions
    谷歌是你的朋友
    
    难度：初学者
    
    “记住使用‘字符串’”
    
    推特：@ArmBjorn
    
    在 Virtualbox 中工作。
    
    获取root权限
    

## 靶机信息

### 靶机界面

网卡信息

网卡信息| 说明  
---|---  
网卡模式| 桥接模式  
MAC 地址| 00:0C:29:79:56:FF  
  
# 信息收集

### 主机发现

    
    
    sudo arp-scan -I eth0 192.168.68.0/24
    
    
    
    sudo arp-scan -I eth0 192.168.68.0/24
    Interface: eth0, type: EN10MB, MAC: 00:0c:29:52:65:df, IPv4: 192.168.68.203
    Starting arp-scan 1.9.7 with 256 hosts (https://github.com/royhills/arp-scan)
    192.168.68.3    00:0c:29:79:56:ff       VMware, Inc.
    192.168.68.199  78:0c:b8:83:de:2a       Intel Corporate
    
    2 packets received by filter, 0 packets dropped by kernel
    Ending arp-scan 1.9.7: 256 hosts scanned in 2.027 seconds (126.30 hosts/sec). 2 responded
    

主机为192.168.68.3

### 端口扫描

命令过程

    
    
    sudo nmap -A -sS -p- -T4 -sC 192.168.68.3
    
    
    
    sudo nmap -A -sS -p- -T4 -sC 192.168.68.3
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-05-28 12:22 EDT
    Nmap scan report for 192.168.68.3
    Host is up (0.00056s latency).
    Not shown: 65533 closed tcp ports (reset)
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
    | ssh-hostkey: 
    |   3072 7f:55:2d:63:a8:86:4f:90:1f:05:3c:c9:9f:40:b3:f2 (RSA)
    |   256 e9:71:11:ed:17:fa:48:06:a7:6b:5b:b6:0e:1b:11:b8 (ECDSA)
    |_  256 db:74:42:c4:37:c3:ae:a0:5c:30:26:cb:1a:ef:76:52 (ED25519)
    80/tcp open  http    Apache httpd 2.4.41
    |_http-title: Index of /
    | http-ls: Volume /
    | SIZE  TIME              FILENAME
    | 31K   2020-12-01 11:23  skeylogger
    |_
    |_http-server-header: Apache/2.4.41 (Ubuntu)
    MAC Address: 00:0C:29:79:56:FF (VMware)
    Device type: general purpose
    Running: Linux 4.X|5.X
    OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
    OS details: Linux 4.15 - 5.6
    Network Distance: 1 hop
    Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    TRACEROUTE
    HOP RTT     ADDRESS
    1   0.56 ms 192.168.68.3
    

### 端口详情

PORT| STATE| SERVICE| VERSION  
---|---|---|---  
22/tcp| open| ssh| OpenSSH 8.2p1 Ubuntu 4  
80/tcp| open| http| Apache httpd 2.4.41  
  
### 网站信息

网站首页

![image](https://image.3001.net/images/20220529/1653758429_629259dda35f9fef495df.png!small)

### 下载文件查看

    
    
    file skeylogger //查看文件类型
    
    
    
    skeylogger: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ba22a62cfb23e5f98841e89718b9d3f5e76bdf94, for GNU/Linux 3.2.0, with debug_info, not stripped
    

官网提示"Remember using 'strings'"，用strings打开strings skeylogger

![image](https://image.3001.net/images/20220529/1653758447_629259ef0113167791fe1.png!small)

发现一行ZHJhY2FyeXMK像base64编码的，解码一下为dracarys

## 渗透过程

### SSH 登录

尝试使用ssh登录一下，用户名daenerys（打开靶机就能获得），密码dracarys

    
    
    ssh daenerys@192.168.68.3                                         130 ⨯
    daenerys@192.168.68.3's password: 
    Last login: Tue Dec  1 11:38:40 2020 from 192.168.0.105
    daenerys@osboxes:~$
    

### 权限提升

    
    
    daenerys@osboxes:~$ whoami
    daenerys
    daenerys@osboxes:~$ id
    uid=1001(daenerys) gid=1001(daenerys) groups=1001(daenerys)
    

查看此用户可以执行哪些sudo命令

    
    
    daenerys@osboxes:~$ sudo -l
    Matching Defaults entries for daenerys on osboxes:
        env_reset, mail_badpass,
        secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
        pwfeedback
    
    User daenerys may run the following commands on osboxes:
        (root) NOPASSWD: /usr/bin/mint-refresh-cache
        (root) NOPASSWD: /usr/lib/linuxmint/mintUpdate/synaptic-workaround.py
        (root) NOPASSWD: /usr/lib/linuxmint/mintUpdate/dpkg_lock_check.sh
    

进入该目录后，没有发现两个可执行脚本

    
    
    daenerys@osboxes:/$ cd /usr/lib/linuxmint/mintUpdate/
    daenerys@osboxes:/usr/lib/linuxmint/mintUpdate$ ls
    aliases                checkWarnings.py   mintUpdate.py        rel_upgrades
    automatic_upgrades.py  Classes.py         proxygsettings.py
    checkAPT.py            kernelwindow.py    rel_upgrade.py
    checkKernels.py        mintupdate-cli.py  rel_upgrade_root.py
    daenerys@osboxes:/usr/lib/linuxmint/mintUpdate$ ls -al
    total 240
    drwxr-xr-x  3 root root   4096 Dec  1  2020 .
    drwxr-xr-x 13 root root   4096 Jun 24  2020 ..
    -rw-r--r--  1 root root   2525 Jun 24  2020 aliases
    -rwxr-xr-x  1 root root   1475 Jun 24  2020 automatic_upgrades.py
    -rwxr-xr-x  1 root root  19146 Jun 24  2020 checkAPT.py
    -rwxr-xr-x  1 root root   4659 Jun 24  2020 checkKernels.py
    -rwxr-xr-x  1 root root   1362 Jun 24  2020 checkWarnings.py
    -rw-r--r--  1 root root   9376 Jun 24  2020 Classes.py
    -rwxr-xr-x  1 root root  30413 Jun 24  2020 kernelwindow.py
    -rwxr-xr-x  1 root root   4541 Jun 24  2020 mintupdate-cli.py
    -rwxr-xr-x  1 root root 107438 Jun 24  2020 mintUpdate.py
    -rw-r--r--  1 root root   4479 Jun 24  2020 proxygsettings.py
    -rwxr-xr-x  1 root root  13605 Jun 24  2020 rel_upgrade.py
    -rwxr-xr-x  1 root root   3002 Jun 24  2020 rel_upgrade_root.py
    drwxr-xr-x  2 root root   4096 Jun 24  2020 rel_upgrades
    

进入~目录的.local/share目录中，发现一个账号名的压缩包，解压之后得到一个写着路径的文件，查看note.txt文件，得到一句话I'm
khal.....

    
    
    daenerys@osboxes:~$ cd .local
    daenerys@osboxes:~/.local$ cd share/
    daenerys@osboxes:~/.local/share$ ls
    daenerys.zip  evolution  flatpak  gnote  nano
    daenerys@osboxes:~/.local/share$ unzip daenerys.zip 
    Archive:  daenerys.zip
     extracting: djkdsnkjdsn
    daenerys@osboxes:~/.local/share$ ls
    daenerys.zip  djkdsnkjdsn  evolution  flatpak  gnote  nano
    daenerys@osboxes:~/.local/share$ cat djkdsnkjdsn 
    /usr/share/sounds/note.txt
    
    daenerys@osboxes:~/.local/share$ cat /usr/share/sounds/note.txt 
    I'm khal.....
    daenerys@osboxes:~/.local/share$
    

Google搜索一下I'm khal.....，得到khal的全名

![image](https://image.3001.net/images/20220529/1653758468_62925a040571a31cd1115.png!small)

使用命令su root，密码输入khaldrogo，成功提权，进入root目录，得到flag

    
    
    daenerys@osboxes:~/.local/share$ su root
    Password: 
    root@osboxes:/home/daenerys/.local/share# ls
    daenerys.zip  djkdsnkjdsn  evolution  flatpak  gnote  nano
    root@osboxes:/home/daenerys/.local/share# cd
    root@osboxes:~# ls
    nice.txt
    root@osboxes:~# cat nice.txt 
    ¡Congratulation!
    
    
    You have a good day!
    
    
    
    aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1nTjhZRjBZZmJFawo=
    

最后一个彩蛋aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj1nTjhZRjBZZmJFawo=

base64解码得到

![image](https://image.3001.net/images/20220529/1653758490_62925a1a7d410be28744e.png!small)

