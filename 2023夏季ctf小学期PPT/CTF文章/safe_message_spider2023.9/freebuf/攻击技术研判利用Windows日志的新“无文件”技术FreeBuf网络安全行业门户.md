## **情报背景**  

近期，卡巴斯基的研究员发现了一种新的“无文件”攻击技术，恶意程序利用Windows事件日志实现Shellcode的存储，并劫持错误报告程序WerFault.exe执行先前嵌入的Shellcode。本文将就其中出现的攻击手法进行解析。

 **组织名称**

|

未知  
  
---|---  
  
 **战术标签**

|

防御规避  
  
 **技术标签**

|

日志利用 顺序搜索劫持  
  
 **情报来源**

|

https://securelist.com/a-new-secret-stash-for-fileless-malware/106393/  
  
##  **01** 攻击技术分析

 **亮点一：利用Windows日志隐藏Shellcode**

样本通过Windows日志API ReportEvent()将shellcode写入事件类别ID为0x4142的日志中进行存储。

日志操作相关API说明如下：

 **API**

|

 **功能说明**  
  
---|---  
  
RegisterEventSourceA

|

创建指定名称的日志  
  
ReportEventA

|

向指定事件中写入日志消息，支持写入文本数据和二进制数据  
  
OpenEventLogA

|

打开指定事件的日志句柄  
  
ReadEventLogA

|

读取指定事件ID的所有日志详情，读取结果存放在EVENTLOGRECORD数组中  
  
写日志流程：

![1654674903_62a055d7bfc0cd047c4ab.png!small?1654674905576](https://image.3001.net/images/20220608/1654674903_62a055d7bfc0cd047c4ab.png!small?1654674905576)

读日志流程：

![1654674922_62a055ea77670970b29f0.png!small?1654674924346](https://image.3001.net/images/20220608/1654674922_62a055ea77670970b29f0.png!small?1654674924346)

在Sysmon中捕获到的日志写入事件：

![1654674933_62a055f54bfc3b8a86605.png!small?1654674935157](https://image.3001.net/images/20220608/1654674933_62a055f54bfc3b8a86605.png!small?1654674935157)

数据读取结果输出：

![1654674943_62a055ffc5c266d5b6977.png!small?1654674945642](https://image.3001.net/images/20220608/1654674943_62a055ffc5c266d5b6977.png!small?1654674945642)

可见，通过合法API调用，可以借助Windows系统日志实现Shellcode的写入。借助日志的载荷存储，一方面可以通过自定义的特殊事件ID实现载荷的分段存储与读取，另一方面也借此很好地在宿主环境中实现了载荷隐藏。

 **亮点二：DLL加载顺序劫持配合入口Patch规避非预期执行**

攻击者利用合法二进制程序WerFault.exe加载恶意wer.dll执行恶意逻辑。WerFault.exe是Windows
的错误报告程序，原本用于上传崩溃报告等信息。攻击者将其副本与恶意载荷wer.dll放置于C:\Windows\Tasks目录，利用DLL加载顺序劫持执行DLL中的攻击代码，读取Windows日志中嵌入的Shellcode并执行。

恶意wer.dll为了阻断WerFault.exe的后续执行流程，在被加载时，首先Patch自身的入口地址代码，通过修改字节为跳转代码，将控制流执行到函数WaitAndExit()中：

![1654674969_62a05619761e7a7ef69fe.png!small?1654674971393](https://image.3001.net/images/20220608/1654674969_62a05619761e7a7ef69fe.png!small?1654674971393)

在函数WaitAndExit()中只会调用WaitForSingleObject()然后退出。这一方面使得恶意逻辑得以执行，另一方面，阻止了原WerFault.exe中其余逻辑的执行，避免了非预期的调用，使得劫持过程更加安静可控。

##  **02** 总结

1.在本次事件中，基于合法调用的日志功能实现载荷的存储与读取，整个过程均通过合法API完成，不易察觉；

2.配合DLL搜索顺序劫持与自身入口代码修改，在加载恶意代码的同时，避免了非预期调用的出现。

  

