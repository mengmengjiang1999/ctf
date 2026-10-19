***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、事件时间线**  

> 2018.1.3 国外安全研究员公开熔断（Meltdown）和幽灵（Spectre）CPU漏洞
>
> 2018.1.3 微软发布CPU漏洞的安全更新补丁KB4056897
>
> 2018.1.5 腾讯安全迅速响应，安全研究员对漏洞进行深入研究
>
> 2018.1.6 电脑管家发布CPU漏洞检测修复工具
>
> 2018.2.13 微软发布包含修复CPU漏洞功能的2月安全补丁KB4074587
>
> 2018.3.13 微软发布包含修复CPU漏洞功能的3月安全补丁KB4088878
>
> 2018.3.27 国外安全研究员公开裂谷（TotalMeltdown）漏洞细节
>
> 2018.3.28 电脑管家对裂谷漏洞迅速响应，安全研究员对漏洞进行深入研究
>
> 2018.3.30 电脑管家发布裂谷漏洞的检测修复工具

 **国外安全研究人员在微软2018年1月和2月的Windows7 x64和Windows Server 2008
R2安全更新中发现了一个致命错误，微软开发人员错误将只限内核访问的PML4（Page Map Level
4）页表设置为用户态可访问，导致任意进程可以对内核进行任意读写。我们称之为“裂谷”漏洞（国外研究人员或称为TotalMeltdown）。攻击者利用这个漏洞可以完全控制受害者的机器。**

##  **二、漏洞分析**

###  **1、漏洞原理**

Intel X64使用的是四级分页模式：PML4（Page Map Level 4）， PDPT（Page Directory
Pointer），PD（Page Directory），PT（Page Table Entry）。如下图所示：

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/15224003021639.png!small)  

Intel X64下的4级分页模式

Windows会在PML4表中存放一个指向PML4自身的入口，也就是将PML4表所在的物理地址映射到一个虚拟地址上。在Windows7
x64和Windows Server 2008 R2中，Windows用PML4表中0x1ED这个固定位置存放指向自己的入口，对应的虚拟地址也就是=
0xFFFF0000`00000000 + (0x1ed<<0n12) + (0x1ed<<0n21) + (0x1ed<<0n30)+
(0x1ed<<0n39) = 0xFFFFF6FB`7DBED000。如下所示：

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/15224003205330.png!small)  

我们在windbg中可以验证，在所有进程的虚拟地址空间中0xFFFFF6FB`7DBED000都映射到PML4基地址，也即是存放在CR3( page
directory base register)的内容。

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/15224003382645.png!small)  

###  **2、漏洞利用分析**

微软将映射到自身的0xFFFFF6FB`7DBED000地址对应的内存的权限错误设置为用户态可读，导致整个PML4所管理的内存均可被用户态可读写，包括整个内核空间的所有地址。

在存在裂谷漏洞的环境中用户态程序读取到PML4的值：

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/15224003546894.png!small)  

该值的具体意义如下，该值中最后一字节'7'表示位0,1,2位被置1，这意味着此PML4的权限为用户态可读可写。

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/15224003659470.png!small)  

利用开源工具pcileech可以实现将整个内存dump出来：

![一文读懂CPU漏洞“裂谷”TotalMeltdown](https://image.3001.net/images/20180330/1522400375156.png!small)  

##  **三、影响范围**

> 受影响的系统： Windows 7 x64，Windows Server 2008 R2

微软3月份的“周二补丁日”解决了此漏洞补丁导致的错误，这意味着只有1月和2月运行修补程序的计算机才会受到攻击。

##  **四、解决方案**

> 1、 已安装电脑防护软件的用户，可直接使用软件中的漏洞修复功能，安装微软3月份安全补丁；
>
> 2、
> 未安装电脑防护软件的用户，可以下载“裂谷（TotalMeltdown）”漏洞检测修复工具，下载地址：<http://dlied6.qq.com/invc/xfspeed/qqpcmgr/other/cpuleak_newfix.exe>
>
> 3、 也可以通过微软官网3月份安全更新解决这个问题
>
> <https://support.microsoft.com/zh-cn/help/4088878/windows-7-update-> kb4088878>

##  **参考资料：**

> <http://blog.frizk.net/2018/03/total-meltdown.html>
>
> <https://www.coresecurity.com/blog/getting-physical-extreme-abuse-of-intel-> based-paging-systems-part-1>
>
> <https://www.coresecurity.com/blog/getting-physical-extreme-abuse-of-intel-> based-paging-systems-part-2-windows>
>
> <https://www.intel.cn/content/www/cn/zh/architecture-and-> technology/64-ia-32-architectures-software-developer-system-programming-> manual-325384.html>
>
> <https://github.com/ufrisk/pcileech>

***本文作者：腾讯电脑管家，转载请注明来自 FreeBuf.COM**

