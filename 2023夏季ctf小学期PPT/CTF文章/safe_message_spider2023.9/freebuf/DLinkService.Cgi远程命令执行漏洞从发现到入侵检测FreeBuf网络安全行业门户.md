***本文作者：cloud4986，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**  

## 摘要

 **本文以D-link
无线路由器615/645/815路由器service.cgi远程命令执行漏洞为例，给出了智能设备命令注入类漏洞的静态分析发现漏洞的方法。根据漏洞分析进行了615/645/815路由器service.cgi远程命令的利用实验，并提取了漏洞利用入侵检测规则。**

## 1\. D-Link service.cgi远程命令执行漏洞简介

Dlink无线路由器615/645/815路由器1.03及之前的固件版本存在远程命令执行漏洞。该漏洞由路由器cgibin程序在处理service.cgi服务post请求EVENT
form域值时产生。

## 2\. 实验环境介绍

> 1) attifyOS:智能设备固件分析环境（下载：<https://github.com/adi0x90/attifyos>）
>
> 2) firmadyne：智能设备固件分析框架
>
> 3) binwalk、IDAPro:固件逆向工具
>
> 4) 固件二进制文件DIR-645_FIRMWARE_1.03.ZIP
> (下载：ftp://ftp2.dlink.com/PRODUCTS/DIR-645/REVA/DIR-645_FIRMWARE_1.03.ZIP)
>
> 5) Burpsuite:web渗透测试工具

## 3\. 智能设备漏洞分析

### 3.1. 命令注入漏洞静态分析方法

命令注入漏洞是指：用户可以通过用户输入数据执行一个或多个系统命令的漏洞。这类漏洞一般是由输入处理程序，将用户输入未做合适的处理就传给了system、exec等函数而产生的。漏洞的静态检测方法一般为：

> 1) 逆向提取固件对应的二进制文件。
>
> 2) 使用反汇编工具将二进制文件反汇编（一般用IDA）。
>
> 3) 在IDA中查找system\exec等执行命令的函数。
>
> 4) 查看调用这些函数的函数及执行流程，确定漏洞入口点。

### 3.2. dir645命令注入漏洞静态分析

 **3.2.1. 逆向cgibin文件**

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205738794872.png!small)  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205739125969.png!small)  

**3.2.2. 静态分析查找命令执行函数**

根据IDA中servicecgi_main的graph_view图我们可以看到servicecgi_main调用了lxmldbc_system函数，此函数调用了system函数。

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205739433219.png!small)  

然后在servicecgi_main的text
view窗口可以看到具体逻辑。在servicecgi_main中会判断请求的方式及请求Form表单参数域，在servicecgi_main中可以处理EVENT,SERVICE,ACTION三个类型的form表单参数域。servicecgi_main会把这三个表单域参数存储在特定区域，然后进行event,service,action的处理。

判断请求方式  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205739916524.png!small)  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205740114328.png!small)  

判断表单域，并进行响应值读取

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205740843912.png!small)  

在处理event请求时没有对EVENT值做必要的处理，然后进入loc_40D038模块，在模块中调用了lxmldbc_system函数，进而调用了system函数。传给lxmldbc_system函数的参数为：”
event %s > /dev/null” 字符串,而这个字符串是post请求中的form内容，其中event是post
form域，而%s里替换内容为event值。

lxmldbc_system函数调用及参数赋值

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205741552258.png!small)  

然后我们查看lxmldbc_system函数，发现lxmldbc_system函数调用了system函数，system函数直接执行了传入的EVENT值。如果将event内容注入命令，并用分隔符分割命令，将可以执行我们注入的命令，如：eventtt
%26 ls %26>/dev/null（此处%26是&的urlencode编码，因为&在http请求中是请求域分隔符）,此时system将能执行ls命令。  
lxmldbc_system函数,画红线部分是system调用，注意mips的流水线效应，这里因为流水线效应，jalr跳转到sysem的分支执行时，move
a0 ,s0装载envent值的语句早已执行。  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205742582237.png!small)

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205743135482.png!small)  

将以上mips汇编代码转化为C代码将更容易查看lxmldbc_system函数逻辑，可以看到主要就是使用vsnprintf将外部输入字符串格式化到局部变量str,然后调用system执行str。

    
    
    int32_tlxmldbc_system(char * format, int32_t a2, int32_t a3, int32_t a4, int32_t a5,int32_t a6, int32_t a7) {
    
        int32_t v1; // 0x4133d4
    
        int32_t system_rc; // 0x4133ec
    
        int32_t str; // bp-1036
    
        int32_t v2;
    
        ….
    
        int32_t v18;
    
        ….
    
        // 0x413394
    
        str = v2;
    
        v18 = a2;
    
        vsnprintf((char *)&str, 1024, format,(int32_t)&v18);
    
        system_rc = system((char *)&str);
    
        return system_rc;
    
    }

根据逆向及反编译后的函数分析,因为lxmldbc_system把外部传入的EVENT域内容直接传给了system函数，所以只要EVENT
form域中转入系统命令并用一些分隔符就可执行路由器固件中的任意命令。

而我们根据service.cgi的程序调用图，可以看到漏洞的入口点为/service.cgi路径。因为，servicecgi_main函数直接由service.cgi调用。

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205747509044.png!small)  

### 3.3. 漏洞利用

根据前面的分析结论，漏洞在/service.cgi
post请求中的Form域EVENT中，可以使用“;”,“|”,”&”,”%0a”等分隔符在EVENT值后注入可执行命令。注入命令后需要是“&”符号的urlencode编码(%26)，因为&在http请求中是请求域分隔符,所以必须做编码转换。在其他分隔符使用时也可以进行urlencode编码。

EVENT值域漏洞利用数据构造格式为：事件名+分隔符（可以是分隔符的urlencode编码）+注入命令+“%26”（即&符号的urlencode编码）。

 **3.3.1. 模拟运行环境建立**

我们利用firmadyne模拟路由器固件运行环境，运行Dlink-dir645固件。步骤如下：

1) 提取固件镜像

执行命令：./sources/extractor/extractor.py -b dir645-3 -sql127.0.0.1 -np -nk
"DIR-645_FIRMWARE_1.03.ZIP" images

这个步骤要记住工具给镜像分配的编号，这里是“Database Image ID：1”中的数字“1”。后续操作对象直接用这个编号代替。

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205748394941.png!small)

2) 判断固件CPU架构

执行命令：./scripts/getArch.sh ./images/1.tar.gz

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/1520574857600.png!small)

3) 将固件镜像信息存储的firmadyne数据库

执行命令：./scripts/tar2db.py -i 1 -f ./images/1.tar.gz

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/1520574879173.png!small)

4) 创建firmadyne环境运行的虚拟镜像

执行命令：sudo ./scripts/makeImage.sh 1

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205748994480.png!small)  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205749175163.png!small)

5) 设置网络接口

执行命令：./scripts/inferNetwork.sh 1

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205749351295.png!small)

6) 在firmadyne环境运行路由器固件

执行命令：./scratch/1/run.sh

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205749527514.png!small)

运行效果  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205749712389.png!small)

**3.3.2. 漏洞利用实验**

这里是有burpsuite的repeater模块执行漏洞利用测试。

1) 分隔符使用“&” 号

攻击数据包及利用效果如下图

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205749883994.png!small)

2) 分隔符使用“|”

攻击数据包及利用效果如下图

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205750073405.png!small)

3) 使用“;”号分隔符  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/1520575028986.png!small)

4) 使用“%0a”分隔符  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205750535202.png!small)

## 4\. 漏洞利用特征及入侵检测规则  

### 4.1. 漏洞利用特征

根据3.漏洞分析，漏洞存在于/service.cgi路径以post方式提交EVENT数据请求时。漏洞利用特征为：

请求路径：/service.cgi

请求方式：post

请求form域：EVENT=任意字符串+分隔符（或者分隔符的urlencode编码）+命令+%26

### 4.2. 漏洞入侵检测规则

根据漏洞利用特征分析编写漏洞利用入侵检测规则如下：

    
    
    alert tcp $EXTERNAL_NET any ->$HTTP_SERVERS $HTTP_PORTS (msg:"dlink service.cgi comand injction attempt1- POST parameter"; flow:to_server,established; content:"post";nocase; content:"/service.cgi"; nocase; fast_pattern;pcre:"/event=\w*((\x25\x30\x61)|(\x25\x32\x36)|\x7c|\x3b|(\x25\x7c)|(\x25\x3b))\w*(\x25\x32\x36)/i";classtype:web-application-attack;    sid:2018000011; rev:1;)

### 4.3. 漏洞利用检测试验

实验的主要攻击数据包（整个攻击包由3.3.2章节漏洞利用实验中采用wireshark捕获）如下：

攻击包1  

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205750944524.png!small)  

攻击包2

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205751229579.png!small)

攻击包3

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205751422756.png!small)  

漏洞利用入侵检测效果

![D-Link
service.cgi远程命令执行漏洞从发现到入侵检测](https://image.3001.net/images/20180309/15205751797204.png!small)  

 ***本文作者：cloud4986，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

