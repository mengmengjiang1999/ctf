## 概述

2月初，奇安信病毒响应中心在日常样本监控过程中发现了一款名为“RobbinHood”的勒索软件通过使用“另类”的方式关闭并删除杀软，经分析，在执行过程中会释放并加载带有漏洞的技嘉驱动程序，之后会对该驱动程序进行漏洞利用，关闭Windows
DSE机制，一旦利用成功便会迅速加载没有签名的Rootkit，Rootkit主要功能为结束并删除指定的进程和杀软，上述操作完成后开始加密。

## 威胁细节

在以往的勒索软件中，Nemty勒索使用Taskkill来结束指定的进程和服务，Snatch勒索会进入安全模式来加密文件，Sodinokibi勒索会使用CVE-2018-8453内核提权漏洞来提升自己的权限结束相关进程和服务。而本文的主角“RobbinHood”结束进程和服务的方式要比上述“残暴”不少。

RobbinHood勒索执行流程如下：

![图片.png](https://image.3001.net/images/20200226/1582686255_5e55e02f1c23c.png!small)

### CVE-2018-19320分析

漏洞出现在GIGABYTE（技嘉）主板相关驱动程序程序中，在处理特定的IOCTL时，由于没有对输入的参数进行相关的校验，导致驱动程序在内核中执行memcpy的操作，从而实现内核任意地址读写。驱动的数字签名如下:

![图片.png](https://image.3001.net/images/20200226/1582686275_5e55e043d7455.png!small)

驱动功能较为简单，问题出在IRP派遣函数中，首先会获取从用户层传来的IOCTL，并与固定值进行比较:

![图片.png](https://image.3001.net/images/20200226/1582686284_5e55e04ce87fc.png!small)

通过调试POC发现当IOCTL等于0xC3502808时会进入问题函数：

![图片.png](https://image.3001.net/images/20200226/1582686292_5e55e05463a1e.png!small)

在问题函数中不做任何校验直接对从用户层传来的数据进行操作：

![图片.png](https://image.3001.net/images/20200226/1582686297_5e55e05996b0f.png!small)

且Dest、Src、Size三个内核memcpy的参数在用户层均可控：

![图片.png](https://image.3001.net/images/20200226/1582686306_5e55e0625a519.png!small)

从而实现任意地址读写的功能

![图片.png](https://image.3001.net/images/20200226/1582686311_5e55e06771baa.png!small)

### DSE ByPass

样本在执行过程中会释放名为ROBNR.EXE的可执行程序，该程序的主要功能是释放并加载带有漏洞的技嘉驱动，通过利用CVE-2018-19320禁用DSE签名机制，并迅速加载没有签名的恶意驱动。

以win7 x64为例，CodeIntegrity初始化简要过程如下，在系统初始化过程中会调用SepInitializeCodeIntegrity：

![图片.png](https://image.3001.net/images/20200226/1582686319_5e55e06f36fd2.png!small)

通过系统是否进入安全模式来给g_CiEnabled赋值，g_CiOptions代表签名策略状态的标志默认开启完成性检查值为6，禁用完整性检查时CiOptions等于0，处于测试模式时值为8，最后会调用ci.dll的导出函数CiInitialize给g_CiCallbacks函数数组进行初始化，至此初始化结束。

当有驱动加载入内核时会调用g_CiCallbacks数组中的函数进行校验，最终会调用SeValidateImageHeader：

![图片.png](https://image.3001.net/images/20200226/1582686328_5e55e0786a777.png!small)

如果g_CiEnabled等于0时则直接返回STATUS_SUCCESS，所以可以通过CVE-2018-19320将g_CiEnabled的值置位0从而绕过代码完成性检验。

在Win7以上版本时，修复了SeValidateImageHeader逻辑问题。

在win7以上的版本时需要对g_CiOptions置0，表示“DISABLE_INTEGRITY_CHECKS”，所以如果想要Bypass
DSE需要对操作系统版本进行判断，体现在样本中的代码如下：

![图片.png](https://image.3001.net/images/20200226/1582686386_5e55e0b2c8b1c.png!small)

在Find_g_CiEnabled_Or_g_CiOptions_Address函数中会跟据不同版本的操作系统取相关地址。

![图片.png](https://image.3001.net/images/20200226/1582686412_5e55e0cc38adc.png!small)  

当系统为win7或win7以下时，通过获取ntoskrnl.exe的基址，在内核中遍历寻找立即数，最终获取g_CiEnabled的地址。获取内核地址代码如下：

![图片.png](https://image.3001.net/images/20200226/1582686427_5e55e0dbe1492.png!small)

当系统为win8或win8以上时，获取CI.DLL的基址，通过对导出表进行解析获取CiInitialize函数地址，再对该函数进行反汇编以此寻找jmp
CipInitialize和mov cs:g_CiOptions, ecx指令。

![图片.png](https://image.3001.net/images/20200226/1582686442_5e55e0ea68f85.png!small)

之所以要这么找这是因为g_CiOptions地址在CipInitialize中，而CipInitialize会在CiInitialize中被调用：

![图片.png](https://image.3001.net/images/20200226/1582686450_5e55e0f26562e.png!small)

找到相关地址后，加载带有漏洞的技嘉驱动，开始漏洞利用：![图片.png](https://image.3001.net/images/20200226/1582686458_5e55e0fa36edd.png!small)

利用成功后加载未签名的驱动rbnl.sys：

![图片.png](https://image.3001.net/images/20200226/1582686463_5e55e0ffa78bd.png!small)

由于内核中的PatchGuard机制触发时间不缺定，所以加载完Rootkit之后再次进行漏洞利用恢复被修改的内核全局变量的值以防止PatchGuard导致系统BSOD。

### Rootkit分析

PDB：C:\Users\Mikhail\Desktop\Robnhold\x64\Win7Release\Robbnhold.pdb

通过PDB可以看出Rookit并非出自第三方分发商，而是黑客自己编写，主要功能为结束杀软进程，删除相关文件。

核心逻辑在IRP派遣函数中：

![图片.png](https://image.3001.net/images/20200226/1582686476_5e55e10cb1ac0.png!small)

调用ZwTerminateProcess结束进程，由于有些系统级别的软件不会被轻易的结束，所以该驱动提供了至少四种强制删除相关文件的方法。在执行过程中会顺序运行。

第一种，直接调用ZwDeleteFile。

![图片.png](https://image.3001.net/images/20200226/1582686492_5e55e11c9acd8.png!small)
****

第二种，向Ntfs.sys发送IRP，首先设置文件属性，去掉只读属性，之后删除文件，在删除文件时获取Ntfs.sys派发例程，将SECTION_OBJECT_POINTER结构置零，由于在Ntfs的NtfsFsdSetInformation例程中会调用MmFlushImageSection函数对SECTION_OBJECT_POINTER进行判断，如果为零，说明该文件在内存中没有被映射，可以被删除。故通过欺骗文件系统的方式达到强制删除正在运行程序文件的效果。

![图片.png](https://image.3001.net/images/20200226/1582686501_5e55e125941c9.png!small)

第三种，与2019年Banload银行木马删除AV的手法一致。

![图片.png](https://image.3001.net/images/20200226/1582686510_5e55e12ed8bba.png!small)

第四种，通过IoCreateFileSpecifyDeviceObjectHint添加文件对象删除的访问权限，之后调用ZwDeleteFile删除文件。

![图片.png](https://image.3001.net/images/20200226/1582686517_5e55e13597991.png!small)

当Rootkit删除指定的文件后，加密程序开始删除卷影，清除日志，禁用windows自动修复，在加密过程中，使用RSA和AES来加密文件，以下格式作为加密后的文件后缀：Encrypted_[randomstring]
.enc_robbinhood，排除如下目录。

![图片.png](https://image.3001.net/images/20200226/1582686524_5e55e13c890db.png!small)

加密完成后弹出勒索信：

![图片.png](https://image.3001.net/images/20200226/1582686531_5e55e143195fc.png!small)

在勒索信中该团伙炫耀起了自己的“战绩”：

![图片.png](https://image.3001.net/images/20200226/1582686538_5e55e14a6c771.png!small)

## 总结

RobbinHood勒索软件利用了第三驱动的漏洞绕过Windows的安全机制，技术上算比较有特色。相比于使用系统内核漏洞，第三方驱动漏洞更加稳定和方便，除了本文分析的CVE-2018-19320漏洞之外。技嘉驱动还有另外三个漏洞可以利用，严重的能够在内核执行任意代码，危害较大。

该家族主要通过RDP爆破登录获取控制，目前对国内用户影响不大，但不排除进一步扩散的可能。因此，奇安信病毒响应中心提醒用户，疫情在家远程办公，不要点击来源不明的邮件和可执行文件，同时提高个人的安全意识，从而可以防止用户隐私信息被盗取的风险，奇安信病毒响应中心会持续对上述家族进行持续跟踪，目前奇安信勒索病毒搜索引擎（lesuobingdu.qianxin.com）已支持上述勒索样本查询。

![图片.png](https://image.3001.net/images/20200226/1582686545_5e55e1517a83a.png!small)

同时基于奇安信威胁情报中心的威胁情报数据的全线产品，包括奇安信威胁情报平台（TIP）、天擎、天眼高级威胁检测系统、奇安信NGSOC等，都已经支持对该家族的精确检测。

## IOC

文件Hash

69fb9c6c2bdc17f24599efb21f3f9f90

afd10dd86b8b4f43c50c***6fb729342

666ccebbb45539c94361503b9d02d39a

## 参考链接

[1]<https://blog.malwarebytes.com/threat-spotlight/2020/02/threat-spotlight-robbinhood-ransomware-takes-the-drivers-seat/>

[2] <https://labs.sentinelone.com/cybercrime-banload-banking-malware-fraud/>

[3]<https://www.secureauth.com/labs/advisories/gigabyte-drivers-elevation-privilege-vulnerabilities>

[4] <https://j00ru.vexillium.org/2012/11/defeating-windows-driver-signature-enforcement-part-1-default-drivers/>

