***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  一 漏洞背景

 **2月12日，微软发布2月份月度例行安全公告，修复了多个高危漏洞，其中包括Windows DHCP
Server远程代码执行漏洞CVE-2019-0626。当攻击者向DHCP服务器发送精心设计的数据包并成功利用后，就可以在DHCP服务中执行任意代码，漏洞影响范围较大。针对此漏洞，启明星辰ADLab第一时间对其进行了详细分析。**

## 二 漏洞影响版本

> Windows 7
>
> Windows 8.1
>
> Windows 10
>
> Windows Server 2008
>
> Windows Server 2012
>
> Windows Server 2016
>
> Windows Server 2019

## 三 协议简介

DHCP，动态主机配置协议，前身是BOOTP协议，是一个局域网的网络协议。DHCP通常用于集中管理分配IP地址，使client动态地获得IP地址、Gateway地址、DNS[服务器](https://www.baidu.com/s?wd=%E6%9C%8D%E5%8A%A1%E5%99%A8&tn=24004469_oem_dg&rsv_dl=gh_pl_sl_csd)地址等信息。DHCP客户端和DHCP服务端的交互过程如下图所示。

![image.png](https://image.3001.net/images/20190305/1551763313_5c7e0771a19df.png!small)

传输的DHCP协议报文需遵循以下格式：

![image.png](https://image.3001.net/images/20190305/1551763342_5c7e078ea81f7.png!small)

DHCP包含许多类型的Option，每个Option由Type、Length和Data三个字段组成。

![image.png](https://image.3001.net/images/20190305/1551763366_5c7e07a6a3911.png!small)

Type取值范围1~255，部分Type类型如下图所示。

![image.png](https://image.3001.net/images/20190305/1551763384_5c7e07b89b3c1.png!small)

DHCP服务在处理VendorSpecific 类型（Type=43）的Option结构存在安全漏洞。首先看下DHCP服务程序对Option的处理过程，
ProcessMessage函数负责处理收到的DHCP报文，调用ExtractOptions函数处理DHCP的Option字段，传入函数ExtractOptions的参数1（v7）为DHCP报文指针，参数3（*(unsigned
int *)(v5 + 16)）对应指针偏移位置+16的数据，即Len字段。

![image.png](https://image.3001.net/images/20190305/1551763461_5c7e0805ca35d.png!small)

ExtractOption函数如下所示。 v6 = (unsigned__int64)&a1[a3 -1];指向报文末尾位置；v10=a1+240;指向报文中Option结构。在for循环中处理不同类型的Option结构，当type=43（Vendor
Specific Information），传入指针v10和指针v6作为参数，调用ParseVendorSpecific函数进行处理。

![image.png](https://image.3001.net/images/20190305/1551763642_5c7e08bad998c.png!small)![image.png](https://image.3001.net/images/20190305/1551763675_5c7e08db9f30e.png!small)

ParseVendorSpecific函数内部调用UncodeOption函数。UncodeOption函数参数a1指向option起始位置，a2指向报文的末尾位置。UncodeOption函数存在安全漏洞，下面结合POC和补丁比对进行分析。

## 四 漏洞分析

构造一个DHCP
Discovery报文，POC如下所示，POC包含两个vendor_specific类型的Option结构。vendor_specific1是合法的Option结构，Length取值0x0a等于Data的实际长度（0x0a），vendor_specific2是不合法的Option结构，
Length取值0x0f大于Data的实际长度（0x0a）。

![image.png](https://image.3001.net/images/20190305/1551763703_5c7e08f73dbe8.png!small)

（1）DHCP服务器收到Discovery请求报文，对数据包进行处理。首先执行ExtractOptions处理Options，当处理vendor_specific类型的Option时，进入到ParseVendorSpecific进行处理。POC中构造一个合法的vendor_specific1，目的是为了绕过84~85行的校验代码，使程序顺利执行到ParseVendorSpecific函数。

![image.png](https://image.3001.net/images/20190305/1551763726_5c7e090ec393d.png!small)

（2）ParseVendorSpecific调用UncodeOption函数。

a. 32~43行在do-while循环中计算Option结构的
Length值之和，保存到v13，作为分配堆内存长度。POC中包含两个vendor_specific结构，首先处理vendor_specific1，计算v13，即vendor_specific1长度a，并且使v12指向下一个Option结构vendor_specific2，当进入43行while条件判断，由于vendor_specific2长度不合法，do-while循环结束。

b. 48行调用HeapAlloc分配堆内存，分配的内存大小v13=a。

c.
51~58行在for循环中依次将vendor_specific结构中的Data拷贝到分配的堆内存中。进入第一次循环时，v1指向vendor_specific1，v8指向末尾位置，满足条件v1<v8，55行调用memcpy将vendor_specific1的Data字段拷贝到分配的堆内存，拷贝长度Length=a。进入第二次循环，v1指向vendor_specific2，v8指向末尾位置，仍然满足条件v1<v8，再次调用memcpy将vendor_specific2的Data字段拷贝到分配的堆内存，拷贝长度Length=0xf。由于分配的堆内存大小只有a个字节，而拷贝的总长度=0x0a+0x0f，从而导致堆溢出。

![image.png](https://image.3001.net/images/20190305/1551763860_5c7e09944c13b.png!small)

## 五 补丁比对

补丁后的版本添加了对Length字段的有效性判断。

![image.png](https://image.3001.net/images/20190305/1551763884_5c7e09ace749f.png!small)

## 六 安全建议

及时安装安全补丁：<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2019-0626>

 ***本文作者：ADLab，转载请注明来自FreeBuf.COM**

