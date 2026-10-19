# 一、背景介绍

5月中旬ESET披露了其捕获的PDF文档样本中的两枚0-day漏洞,其中包含针对Windows系统的内核提权漏洞。该漏洞的漏洞编号为CVE-2018-8120，Windows已经提供安全更新修复此安全漏洞。天融信阿尔法实验室将以Windows
Server 2003 32位系统为目标，详细介绍该漏洞成因、如何触发漏洞、以及如何使用该漏洞制作“本地应用程序权限提升”工具。

经验证，诸多版本的Windows系统均存在该漏洞，文末同时附带一份利用该漏洞制作的提权工具，以供学习。经测试该工具支持Win2003
x32/x64、WinXP x32、Win7 x32/x64, Win2008 x32/64。

  
![image.png](https://image.3001.net/images/20180607/15283624179560.png!small)  

## 1.1漏洞描述

部分版本Windows系统win32k.sys组件的NtUserSetImeInfoEx()系统服务函数内部未验证内核对象中的空指针对象,普通应用程序可利用该空指针漏洞以内核权限执行任意代码。

## 1.2受影响的系统版本

以下软件版本受到影响。未列出的版本要么超过其支持生命周期，要么不受影响。要确定软件版本或版本的支持生命周期，请查阅Microsoft支持生命周期。

Windows 7 for 32-bit Systems Service Pack 1

Windows 7 for x64-based Systems Service Pack 1

Windows Server 2008 for 32-bit Systems Service Pack 2

Windows Server 2008 for 32-bit Systems Service Pack 2

Windows Server 2008 for Itanium-Based Systems ServicePack 2

Windows Server 2008 for x64-based Systems Service Pack 2

Windows Server 2008 for x64-based Systems Service Pack 2

Windows Server 2008 R2 for Itanium-Based Systems ServicePack 1

Windows Server 2008 R2 for x64-based Systems ServicePack 1

Windows Server 2008 R2 for x64-based Systems ServicePack 1

## 1.3.漏洞编号

CVE-2018-8120

# 二、漏洞细节

## 2.1漏洞位置及形成原因

漏洞函数位于win32k.sys模块的SetImeInfoEx() 函数，
该函数在使用一个内核对象的字段之前并没有进行是否为空的判断，当该值为空时，函数直接读取零地址内存。如果在当前进程环境中没有映射零页面，该函数将触发页面错误异常，导致系统蓝屏发生。

以下是漏洞产生位置的反汇编代码

  
![image.png](https://image.3001.net/images/20180607/15283624457540.png!small)  

可以看到，漏洞所在函数SetImeInfoEx()接收2个参数，漏洞的产生和参数1的结构体指针有关，下面跟踪一下参数1的来源。win32k!NtUserSetImeInfoEx()
系统服务函数调用了SetImeInfoEx()

  
![image.png](https://image.3001.net/images/20180607/15283624501461.png!small)  

_GetProcessWindowStation()返回当前进程的WindowStation内核对象,
当做参数1调用SetImeInfoEx()。以下是WindowStation内核对象的内存结构

  
![image.png](https://image.3001.net/images/20180607/15283624613321.png!small)  

程序可以通过系统提供的接口CreateWindowStation()和SetProcessWindowStation(),新建一个新的WindowStation对象并和当前进程关联起来，值得注意的是，使用CreateWindowStation()
新建的WindowStation对象其偏移0x14位置的spklList字段的值默认是零。

根据SetImeInfoEx()函数的流程，当WindowStation->spklList字段为0，函数继续执行将触发0地址访问异常。

## 2.2漏洞触发验证

前文已经介绍了漏洞所在位置，下面编写漏洞测试代码，测试该漏洞是否能够触发系统蓝屏。

  
![image.png](https://image.3001.net/images/20180607/15283624657033.png!small)  

NtUserSetImeInfoEx()系统服务函数未导出，需要自己在用户进程中调用该系统服务函数，以执行漏洞函数SetImeInfoEx()。

  
![image.png](https://image.3001.net/images/20180607/15283624712726.png!small)  

其中SyscallIndex的计算，根据系统ShadowSSDT表导出序号计算。

  
![image.png](https://image.3001.net/images/20180607/15283624841834.png!small)  

编译生成poc，开始执行

  
![image.png](https://image.3001.net/images/20180607/15283624899551.png!small)  

  
![image.png](https://image.3001.net/images/20180607/15283625023000.png!small)  

系统蓝屏，可以发现错误产生位置为0xBF91B399，下面在IDA中查看对应地址的指令，正是前文指出的SetImeInfoEx()中针对pWindowStation->spklList字段进行内存访问的代码。

  
![image.png](https://image.3001.net/images/20180607/15283625036197.png!small)  

# 三、漏洞利用

## 3.1漏洞利用之任意代码执行

由于SetImeInfoEx()没有正确的处理内存中的空指针对象,
普通应用程序可利用该漏洞以系统权限执行任意代码，下面将详细介绍如何在该漏洞现场实现任意代码执行。

已知漏洞产生的原因是零地址内存访问违例，如果在漏洞函数运行的进程中，零地址处的内存分页完成映射，则函数将继续执行。下面继续看看函数如果继续运行，会发生什么情况。

  
![image.png](https://image.3001.net/images/20180607/15283625511822.png!small)  

如上图所示，漏洞产生函数后续执行过程中会执行内存拷贝，且拷贝源来自于参数2，属于用户可控内容。如果拷贝目标v4可控，则可以实现 **任意内存地址写入**
（且漏洞函数运行在内核权限， 内核空间与用户空间内存均有权限读写）。至此，如果可以实现 **任意内存地址写入** ，则可以通过覆盖系统服务函数指针的方式，
实现 **任意代码执行** 。

现在的目标是使得拷贝目标v4可控，已知v4来自spklList+0x2C，当spklList为零,而零地址分页内存又正好被应用程序映射，一来SetImeInfoEx()可以继续执行不触发异常，二来也是v4是可控的。

通过内核未导出函数可以在部分Windows 系统上成功映射零地址分页的内存，函数原型所示

  
![image.png](https://image.3001.net/images/20180607/15283625608164.png!small)  

映射零地址分页内存后，可以在该地址上进行内核对象的构造，以满足SetImeInfoEx()函数的检查,
通过漏洞函数的memcpy操作覆盖关键系统服务函数指针。
改造漏洞验证代码，尝试覆盖ntoskrnl!HalDispatchTable表中第二项的hal!HaliQuerySystemInformation()
函数指针，NtQueryIntervalProfile()函数在运行过程中会从HalDispatchTable表中调用该函数。使得用户程序在调用系统函数NtQueryIntervalProfile()的时候，执行由应用程序设定的ShellCode。

  
![image.png](https://image.3001.net/images/20180607/15283625684552.png!small)  

  
![image.png](https://image.3001.net/images/20180607/15283625735424.png!small)  

最终验证该代码不能成功覆盖预设的函数指针,原因很简单。目标地址0x8088e07c，无法通过漏洞函数的第二个判断，位置如下图所示

  
![image.png](https://image.3001.net/images/20180607/15283625805128.png!small)  

首先直接这样触发漏洞覆盖该函数指针表0x15C字节大小，造成影响较大，二来由于漏洞函数本身的限制，挑选合适的覆盖位置也比较困难，
下面简要介绍一种流行的方法，用来协助我们进行精准的覆盖。

利用Bitmap内核对象中的pvScan0字段，进行的任意内存地址读写。通过系统API
SetBitMap()和GetBitMap()可以实现指定地址写入/读取功能。该方法已有文章进行详细的分析，下面附一篇文章链接读者可以去查阅，这里不再赘述。

<https://bbs.pediy.com/thread-225436.htm>

下面修改漏洞验证代码，首先利用漏洞覆盖预先创建的BitMap内核对象,
接着再使用BitMap内核对象进行精准覆盖。实现函数指针覆盖，以下是加入使用BitMap进行精准覆盖的代码。

  
![image.png](https://image.3001.net/images/20180607/15283625937082.png!small)  

  
![image.png](https://image.3001.net/images/20180607/15283625997727.png!small)  

成功的覆盖指定的函数指针，应用程序接着调用该系统服务函数接口，操作系统就会执行我们设定的Shellcode，下面是一段使用SYSTEM进程
EPROCESS结构的Token替换当前进程Token的代码，执行过该代码后，本进程具有和SYSTEM进程一样的权限。

  
![image.png](https://image.3001.net/images/20180607/15283626059823.png!small)  

在替换当前进程EPROCESS结构中Token标识后，当前进程后续创建的进程均为SYSTEM权限的进程，成功进行权限提升获得SYSTEM权限。

## 3.2 漏洞利用实例-提权工具

本文演示之漏洞利用代码取自[GitHub](https://github.com/unamer/CVE-2018-8120) 感谢作者@unamer。
该作者开源的代码包含了一份针对Win7及Win 2008系统的提权工具。

笔者根据该代码做了部分修改，增添了针对Windows 2003 sp2（x32 x64）及Windows XP sp2
x32系统的提权支持。主要是漏洞利用代码中自行调用了系统内核服务函数，不同系统其系统服务调用号并不一致。同时还修改了部分结构体偏移，以支持Win2003和WinXP。在WinXP
x64系统上, 由于NtUserSetImeInfoEx() 中对win32k!gpsi结构中标志位进行验证而未能执行含有漏洞的代码，故未能成功利用该漏洞。

修改后的漏洞利用工具源码及Bin下载地址如下：

<https://github.com/alpha1ab/CVE-2018-8120>

# 四、修复建议

目前微软在2018年五月的安全更新中已经包含了针对该漏洞的补丁程序，安装使用即可避免受到该漏洞的影响。

漏洞修复程序下载地址:

<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2018-8120>

  

