**情报背景**

近期，Mandiant团队捕获了COLDDRAW新的勒索软件样本。在该样本中，可以看到勒索软件的攻击技术在攻防对抗过程中不断升级。该样本释放杀毒软件Avast的驱动程序并加载，利用该驱动在内核级别终止安全产品相关进程，达到防御削弱的效果。本文将通过对相关样本的逆向分析和复现，对该技术点进行分析阐述。

 **组织名称**

|

UNC2596  
  
---|---  
  
 **相关工具**

|

Cuba Ransomware  
  
 **战术标签**

|

  

防御规避 执行

  
  
  
 **技术标签**

|

  

勒索 驱动安全 进程查杀

  
  
  
 **情报来源**

|

  

  

https://www.mandiant.com/resources/unc2596-cuba-ransomware

  
  
  
##  **01** 攻击技术分析

 **亮点:** 利用杀毒软件驱动终止进程

对样本进行逆向分析可知利用驱动终止进程的实现过程：

1\. 使用CreateFile 调用安装的Avast驱动程序。如果调用有效，则进行进程的查找和终止。

![1650781701_6264ee05601affdfbcadb.png!small?1650781701622](https://image.3001.net/images/20220424/1650781701_6264ee05601affdfbcadb.png!small?1650781701622)

2\.
使用CreateToolhelp32Snapshot对进程进行快照，并用Process32FirstW和Process32Next逐一匹配要终止的进程。

![1650781722_6264ee1aa155635f09b38.png!small?1650781722758](https://image.3001.net/images/20220424/1650781722_6264ee1aa155635f09b38.png!small?1650781722758)![1650781729_6264ee21f1e504f9e20cb.png!small?1650781730052](https://image.3001.net/images/20220424/1650781729_6264ee21f1e504f9e20cb.png!small?1650781730052)

3\. 如果匹配成功，则调用Avast终止函数。调用DeveiceIoControl API，该函数将 IOCTL代码 0x9988c094 和
要终止的进程ID发送给Avast驱动程序，使得Avast驱动程序在内核级别终止进程。

![1650781970_6264ef125339a2c5164f2.png!small?1650781970456](https://image.3001.net/images/20220424/1650781970_6264ef125339a2c5164f2.png!small?1650781970456)

对驱动进行逆向分析，可以发现当IOCTL代码为0x9988c094
时，该驱动调用KStackeAttachProcess和ZwTerminateProcess，进而从内核级别终止代码。

![1650781984_6264ef20c9205bc560712.png!small?1650781984904](https://image.3001.net/images/20220424/1650781984_6264ef20c9205bc560712.png!small?1650781984904)

IOCT代码 0x9988c094

![1650782012_6264ef3c68c2671b6c121.png!small?1650782012670](https://image.3001.net/images/20220424/1650782012_6264ef3c68c2671b6c121.png!small?1650782012670)

函数内执行KStackeAttachProcess和ZwTerminateProcess

对该样本实现进行复现，实现终止Windows Defender进程：

![1650782130_6264efb21c7f131209c47.png!small?1650782130213](https://image.3001.net/images/20220424/1650782130_6264efb21c7f131209c47.png!small?1650782130213)

由此可见，该攻击技术在防御削弱上效果显著，Windows Defender重启间隔时间较长，足够攻击者执行相关的恶意操作，完成阶段性的攻击目的。

在该样本中终止的进程主要是AV/EDR相关的进程，即在内核级别终止AV/EDR相关进程，进而绕过AV/EDR的保护和检测，起到防御削弱的效果。

SentinelHelperService.exe

|

iptray.exe

|

dsa-connect.exe  
  
---|---|---  
  
SentinelServiceHost.exe

|

ccSvcHst.exe

|

ResponseService.exe  
  
SentinelStaticEngineScanner.exe

|

sepWscSvc64.exe

|

...  
  
作为有数字签名的杀毒软件的驱动:

1\. 驱动本身是无毒无害的，且具有签名的驱动程序可信度更高，因此在安装和落地时不会被查杀。

2\. 通过驱动去终止进程，可以有效绕过AV/EDR 在驱动层面对进程终止操作的过滤，起到了良好的防御削弱效果。

3\. 通过调用驱动的方式终止进程，避免进程终止行为和恶意软件自身的直接关联，达到隐匿效果。

##  **02** 总结

作为杀毒软件却成为恶意软件的刀刃，值得我们反思杀毒软件的驱动在功能实现上是否足够安全，是否也有其他驱动有沦为攻击者的武器的可能性。

从内核层发起的攻击对宿主机而言更加难以防御，更具攻击性。

勒索软件在绕过安全机制的创新和想法上也是不断增加和进步，值得我们借鉴和学习。

