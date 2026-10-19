***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**缓冲区溢出算是安全界常见的漏洞，也是一种最初级的漏洞，但是这种漏洞时至今日依旧层出不穷。大部分由于项目庞大，调用逻辑层次复杂，以及测试时测试用例问题，不能及时发现这类漏洞。**  

## 一. 缓冲区溢出的原因。

由于[缓冲区溢出](http://baike.baidu.com/item/%E7%BC%93%E5%86%B2%E5%8C%BA%E6%BA%A2%E5%87%BA)而使得有用的[存储单元](http://baike.baidu.com/item/%E5%AD%98%E5%82%A8%E5%8D%95%E5%85%83)被改写,往往会引发不可预料的后果。程序在运行过程中，为了临时存取数据的需要，一般都要分配一些内存空间，通常称这些空间为缓冲区。如果向缓冲区中写入超过其本身长度的数据，以致于缓冲区无法容纳，就会造成缓冲区以外的存储单元被改写，这种现象就称为缓冲区溢出。缓冲区长度一般与用户自己定义的缓冲变量的类型有关。

总结以上原因，可以获得缓冲区溢出的两个必要条件。

> 1\. 缓冲区。
>
> 2\. 对缓冲区操作造成缓冲区外的存储单元的数据被改写。

找到原因后可以总结代码中出现的情况。

> 缓冲区： 数组，malloc/new 申请, struct和class中数组。
>
> 写入操作：对缓冲写入操作时，没有对长度做校验，导致数据被覆盖改写。（strcpy,strcat，scanf,memcpy, memmove,
> memeccpy Getc(),fgetc(),getchar;read,printf等函数）。

## 二. 常见的代码审计工具弱点

代码审计对复杂项目的审计效果不好：

> 1.函数调用是个复杂的过程，当审计工具找到敏感函数时，回溯函数的调用路径常常会遇到困难。
>
> 2\. 如果程序使用了复杂框架，代码审计工具往往由于缺乏对框架的支持，从而造成误报或漏报。

## 三. 源码中白盒审计分析

本次审计的开源软件为Dmitry1.3a（源码自行下载）.用到的工具sourceinsight，gdb，peda。

使用sourceinsight对源码进行解析。

###  **1\. 查找所有容易产生溢出的函数调用点。**

是否对长度有控制，有控制需要查看控制是否合理，不合理可能会引起溢出。没有长度控制是很大隐患点。

使用sourceinsgiht可以在工程所有文件中查找容易引起溢出的函数的代码和文件。

逐个查看函数调用是否安全。

###  **2\. 逐个分析是否存在可能溢出**

溢出原因对缓冲区操作时没有对缓冲区空间的大小进行校验。

如果使函数的参数，需要查找其调用函数，查看实参参入时长度是否和函数体内长度一致。如果小于实参长度，就容易产生溢出。

找到可疑点，并做记录。

可疑点1.

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249885552467.png!small)

可疑点2：

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/1524988576818.png!small)

可疑点3：函数内部定义fhost最大值为128

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249886399785.png!small)  

但是main函数内部调用时没有检查长度。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249886579814.png!small)  

可疑点4：函数内部定义为hostwww最大长度为64.

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249886774903.png!small)  

但是调用函数main里面。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249887021067.png!small)  

可疑点5：

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249887336723.png!small)  

但是调用函数main里面：

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249887602747.png!small)  

可疑点6：

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249887917451.png!small)  

在main函数里面调用，参数strings被输入时没有长度验证。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249888123088.png!small)  

## 四. 验证可疑点

对源代码做了白盒设计分析后，需要对程序的流程和数据做验证分析，输入引发溢出的数据，查看是否能够引起溢出。

###  **验证可疑点1：**

使用gdb调试程序。

设置其参数：set args
-oBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
aaaaaaaaaaaaaaa（-o选项，当optorg ！= 最后一个参数的时候）执行strcpy(outputfile,optarg);
其中outputfile[64]。参数中104个B。可以引发溢出。

运行查看结果：

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249888888422.png!small)  

可以看到outputfile被写入BBB，超过了64位的长度。 但是没有引发异常。

查看outputfile的定义，是一个全局变量，被写入超长数据覆盖一部分数据，数据并没有使用，所以没有引发异常。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249889137120.png!small)

### 验证可疑点2：

Gdb调试，设置设置参数，使参数超过128个字符即可产生溢出。在strcpy(host_name,argv[argc - 1]);处下断点。

    
    
    set argsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

断下后，查看未执行strcpy前host_name的数据。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249889338526.png!small)

执行后，查看host_name的数据。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249889825716.png!small)

可以看到数据被覆盖，超过了128. 查看寄存器,大部分寄存器都被覆盖为

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249890007836.png!small)  

### 验证可疑点3：

参数长度计算

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249891859557.png!small)

超过128+128+64的长度才能覆盖数据，引发溢出。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249892164563.png!small)

### 验证可疑点4：

查看引发溢出的条件

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249892545317.png!small)

只有输入长度大于64+128+4+4+4+4+4后的长度才能引发异常。但不能超过可疑点3的长度。

超过后会引发可疑点3.

设置参数：

    
    
    set args AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249892838823.png!small)  

可疑点5和可疑点4类似，输入数据容易引发可疑点3和可疑点4的溢出。略过。

###  验证可疑点6：

设置运行参数：

    
    
    set args -o AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

跟踪到函数中,执行完strcat(sendbuff, string2)，可以看到数据被覆盖。

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249893342579.png!small)

![源码审计之缓冲区溢出漏洞](https://image.3001.net/images/20180429/15249893468772.png!small)  

## 五. 总结

本次缓冲区溢出主要讲解的是栈溢出。纯手工审计是为了锻炼自己在代码审计时对漏洞的敏感度。本次用到的Dmitry1.3a是一款信息挖掘的工具。大家在审计或者渗透时用到工具如果是开源的，可以对源码进行审计和分析，可以同时提高审计能力和工具实现的原理。

*本文作者：，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。

