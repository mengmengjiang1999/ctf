## **情报背景**

近期来自ESET与AhnLab的研究人员发布了关于Lazarus攻击团伙恶意Rootkit的分析报告，在两个攻击链中利用了不同的合法驱动突破防御，在Ring0级完成一系列防御削弱操作，最终加载Rootkit达成攻击目的。本文将对Lazarus在本次攻击事件中的BYOVD技术与防御削弱技术进行分析研判。

 **组织名称**

|

Lazarus  
  
---|---  
  
 **战术标签**

|

防御规避  
  
 **技术标签**

|

BYOVD、Rootkit、Windows Prefetch  
  
 **情报来源**

|

https://www.bleepingcomputer.com

/news/security/lazarus-hackers-abuse

-dell-driver-bug-using-new-fudmodule-
rootkit/  
https://www.virusbulletin.com/

uploads/pdf/conference/vb2022

/VB2022-Kalnai-Havranek.pdf

https://asec.ahnlab.com/

wp-content/uploads/2022/10/

Analysis-Report-on-Lazarus-Groups-Rootkit-
Attack-Using-BYOVD_Oct-05-2022-3.pdf  
  
##  **01** 攻击技术分析

 **亮点一：BYOVD利用技术**

BYOVD是将存在漏洞的合法驱动投递至目标系统，借助其完成恶意操作的攻击技术。借助滥用的合法驱动签名，攻击者得以绕过DSE（强制驱动签名）机制的限制，在Ring0空间完成各种攻击操作。

![1669882319_638861cf0556620567646.png!small?1669882320518](https://image.3001.net/images/20221201/1669882319_638861cf0556620567646.png!small?1669882320518)

图1 典型BYOVD利用过程

 **驱动文件**

|

 **利用类型**

|

 **厂商**  
  
---|---|---  
  
DBUtil_2_3.sys

|

虚拟内存读写

|

DELL(CVE-2021-21551)  
  
ene.sys

|

物理内存读写

|

ENE Technology  
  
攻击者在两次攻击活动中滥用了不同的驱动文件来作为敲门砖，但是漏洞利用效果与利用链构造上如出一辙：利用内存写入类漏洞篡改内核线程对象的PreviousMode属性，达到从用户态访问内核空间的攻击效果。

 **亮点二：PreviousMode篡改，开启“上帝模式”**

    
    
    typedef enum _MODE {  
    KernelMode = 0,  
    UserMode = 1,  
    } MODE;

ETHREAD内核数据结构中的PreviousMode原本用于指示函数的调用方，当系统调用来自用户态线程中时，系统调用的处理函数会在线程对象中设置其PreviousMode属性为1（UserMode），若调用方为内核或系统进程则将其置于0（KernelMode）。该值标识了调用源是否来自可信的环境。

![1669882337_638861e1423c19da05f7b.png!small?1669882338869](https://image.3001.net/images/20221201/1669882337_638861e1423c19da05f7b.png!small?1669882338869)

图2 借助物理内存映射修改PreviousMode值

若该值被置为0，类似于NtWriteVirtualMemory这样的函数可同时读写用户态与内核态的内存空间，开启“上帝模式”。攻击者正是利用这样的方式，对内核数据结构执行了一系列篡改，以达成防御削弱的战术目的。

 **亮点三：Ring0级防御削弱技术**

攻击者在成功利用BYOVD利用技术突破到Ring0级权限，并获取内核空间的读写权限后采取了一系列防御削弱的攻击手段，禁用了一系列内核回调函数以及检测基础设施，达到致盲安全产品的目的。

按照一定顺序对于一些系统回调函数进行了Patch，实现破坏针对进程、线程、模块和注册表等检测能力。为了保证保证不会有通知发往现存的回调函数，攻击者首先对PspNotifyEnableMask结构加以patch。

 **内核数据结构**

|

 **说明**  
  
---|---  
  
nt!PspNotifyEnableMask

|

表征回调函数是否安装  
  
nt!PspLoadImageNotifyRoutine

|

禁用模块加载（驱动加载）检测  
  
nt!PspCreateThreadNotifyRoutine

|

禁用线程创建/终止检测  
  
nt!PspCreateProcessNotifyRoutine

|

禁用进程创建/终止检测  
  
nt!CallbackListHead

|

禁用注册表修改检测  
  
nt!ObTypeIndexTable

|

禁用Object Callback  
  
除此之外攻击者禁用了白名单之外的Mini File
Filter与WFP驱动程序，破坏安全产品对于文件系统和网络流量的检测能力。ETW是Windows操作系统提供的安全事件日志采集的基础设施，帮助EDR等安全产品捕获恶意行为，攻击者通过对于ETW相关的一系列句柄与参数的覆写破坏了ETW的可用性。

篡改的ETW相关数据结构

  * nt!EtwpEventTracingProvRegHandle

  * nt!EtwKernelProvRegHandle

  * nt!EtwpPsProvRegHandle

  * nt!EtwpNetProvRegHandle

  * nt!EtwpDiskProvRegHandle

  * nt!EtwpFileProvRegHandle

  * nt!EtwSecurityMitigationsRegHandle

  * nt!EtwpHostSiloState

 **亮点四：反取证-禁用Windows Prefetch文件创建**

Windows
Prefetch（预读取）文件被设计以加速程序的打开速度，其中存储了近期执行程序的记录。进程路径、文件创建/修改/执行时间等信息，也为恶意程序执行的分析取证提供了机会。

![1669882354_638861f262a549b5755ff.png!small?1669882355744](https://image.3001.net/images/20221201/1669882354_638861f262a549b5755ff.png!small?1669882355744)

图3 查看Prefetch文件中存储的程序执行信息

攻击者通过内核中nt!PfSnNumActiveTraces数据结构的篡改，禁用了Windows
Prefetch文件的创建，达到反取证的目的。当该数据结构的值被篡改后，生成Prefetch文件的关键函数PfSnBeginTrace将永远返回-1，达到破坏生成的目的。

![1669882362_638861fab51ba0a4718b3.png!small?1669882364064](https://image.3001.net/images/20221201/1669882362_638861fab51ba0a4718b3.png!small?1669882364064)

图4 篡改数据结构以破坏Prefetch文件生成

##  **02** 总结

本次攻击事件是借助BYOVD利用技术突破系统安全防护，进而利用Ring0级防御削弱技术对抗EDR等现代端点防护的典型案例。本次案例中出现的较新的漏洞驱动利用（DELL驱动的CVE-2021-21551权限提升漏洞）说明攻击者一直在进行新的可利用驱动的挖掘探索，完善驱动黑名单机制可有效应对这类已知BYOVD驱动的滥用。攻击者在Ring0级的权限提升与防御削弱操作达到驾轻就熟的地步，破坏内核回调与ETW等检测基础设施、致盲安全产品、反取证的手段，对于攻击者具有极强的战术价值。

