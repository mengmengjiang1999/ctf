**作者：启明星辰ADLab**  
**文章来源：[Advantech
WebAccess多个漏洞分析](https://mp.weixin.qq.com/s?__biz=MzAwNTI1NDI3MQ==&mid=2649614384&idx=1&sn=c7eaaff26938d4dc92ef32cd851a1e2d&chksm=83063520b471bc36368de15bf0f195de8bffc6fbb4a6c4cb3648ad4b213872e0d50c2bc5e508&mpshare=1&scene=1&srcid=0820HxxoMQBWllPfsWNVO438&sharer_sharetime=1566286107538&sharer_shareid=bafb2678ed1f77a340809d0b35c3d277&key=7ee95d8bb7f7df5e0ccef7fc7d673498c302f1bdab2a86012a7d8089b909ae048f03157897237ed81df7815c273a5d06c2264855be26ba29e24dfacc861b80fe16153913f8a97555cc072752458ea482&ascene=1&uin=MzM5ODEzOTY3MQ%3D%3D&devicetype=Windows+10&version=62060833&lang=zh_CN&pass_ticket=eT1pa5S9ibxZcgeIuAzHzpptuOANeJIpacaA65vpHM2sqJemoxAAfF9pdrsRUzQI
"外出")**

Advantech
WebAccess是研华科技开发的完全基于IE浏览器的HMI/SCADA监控软件，其最大特点就是全部的工程项目、数据库设置、画面制作和软件管理都可以通过使用标准的浏览器完成，不仅可以实现系统的远程控制而且还能进行工程的开发和维护。近日ZDI公布了多个WebAccess的漏洞预警(CVE-2019-10985、CVE-2019-10993、CVE-2019-1099、
CVE-2019-6550以及ZDI-19-584 ~ ZDI-19-623、ZDI-19-691)，其中包括多个内存破坏漏洞（ZDI-19-595~
ZDI-19-614）以及栈溢出漏洞（ZDI-19-585、ZDI-19-327~ZDI-19-330、ZDI-19-325、ZDI-19-323、ZDI-19-592、ZDI-19-594、ZDI-19-589、ZDI-19-588、ZDI-19-586)，部分内存破坏漏洞可以在受影响的系统中执行任意代码，但是大部分内存破坏漏洞利用条件较为苛刻。同时，由于Advantech
WebAccess许多模块并没有开启ASLR、DEP等系统相关安全机制，使得栈溢出等漏洞在受影响的系统中容易造成代码执行。

### Advantech WebAccess历史漏洞统计情况

通过追踪CVE漏洞数据库中的Advantech
WebAccess历史漏洞，启明星辰ADLab发现从2011年到2019年合计有134个漏洞被披露。图1是我们统计的每一年的漏洞披露数量：

![](https://images.seebug.org/content/images/2019/08/13adbd4a-e165-4ec9-9a6b-c75514b63c87.jpg-w331s)

图1 Advantech WebAccess历年CVE漏洞数量情况

从图中可以看出，其漏洞数量总体上随着年份上下波动。2014年出现一次井喷达到26个，而2015年漏洞披露只有5个，随后出现逐年上升趋势。我们对WebAccess的漏洞类型信息进行了梳理，如图2：

![](https://images.seebug.org/content/images/2019/08/08f56076-076e-4f4e-96c7-48d07b3ce7d0.jpg-w331s)

图2 Advantech WebAccess历年漏洞类型比例图

从图中可以看出WebAccess的历史漏洞类型比较丰富，包括了缓冲区溢出、SQL注入、XSS、权限管理不当、敏感信息泄露、代码\命令执行等。其中缓冲区溢出类型漏洞最多，占到漏洞总数的1/3以上；其次是权限管理类漏洞（11.94%）、敏感信息泄露(8.96%)、SQL注入（8.21%）。由此可以看出，WebAccess的漏洞面较为广泛。

为了分析WebAccess漏洞类型的演变趋势，我们对其历年不同漏洞类型的数量进行了梳理，如图3：

![](https://images.seebug.org/content/images/2019/08/70d2b5f1-51e7-448a-82a2-635905b874ba.jpg-w331s)
图3 Advantech WebAccess历年漏洞类型数量

从图中可以看出，WebAccess的漏洞类型趋势没有明显变化，其中缓冲区溢出漏洞和权限管理漏洞在经历2014年井喷后仍然没有得到有效缓解，代码\命令执行漏洞从2018年开始增多。

### Advantech WebAccess Node多个ZDI漏洞分析

在ZDI披露的Advantech WebAccess Node的漏洞中，大部分都存在于webvrpcs.exe中的RPC通讯模块。RPC（Remote
Procedure
Call）即远程过程调用，是一种通过网络从远程计算机程序上请求服务，而不需要了解底层网络技术的协议。RPC协议假定某些传输协议的存在，如TCP或UDP，为通信程序之间携带信息数据。RPC协议屏蔽了编程语言之间的特性差异，广泛应用于分布式系统中，在工业控制DCS系统中也被广泛应用。

对Advantech WebAccess Node分析发现，其采用RPC协议来实现ODBC
和一些控制台命令。但在具体功能实现时缺乏相应的安全检查，导致产生了命令执行、内存破坏等多个漏洞。我们对这些漏洞进行了分析，其中典型漏洞（CVE-2017-16720、CVE-2019-10993、CVE-2019-10991）的分析如下。

#### 1、CVE-2017-16720命令执行漏洞

在该漏洞位于webvrpcs程序的RPC IOCTL code 0x2711功能实现。在一定条件下可利用该漏洞在安装有Advantech
WebAccess的系统上执行任意命令。该漏洞的EXP已被公开，核心代码如图4所示：

![](https://images.seebug.org/content/images/2019/08/76d0b2a4-3532-4c40-906a-b11e62578a4e.jpg-w331s)

图4 CVE-2017-16720利用代码

为了分析该漏洞的代码路径，先用IDA打开webvrpcs.exe，然后通过mida插件提取出其RPC接口，可以看到opcode
0x1对应的处理函数为sub_401260。

![](https://images.seebug.org/content/images/2019/08/8839f1ce-ccb0-424c-a04b-bfb6adc7d324.jpg-w331s)

图5 webvrpcs.exe使用IDA mida插件分析RPC接口

sub_401260（图6所示伪代码）首先对RPC消息的头部数据进行处理，然后调用sub_402c60函数。sub_402c60函数最终调用DsDaqWebService函数（如图7所示），而DsDaqWebService函数源于动态链接库drawsrv.dll。用IDA打开drawsrv.dll并定位到函数DsDaqWebService，DsDaqWebService函数实现了各个不同IOCTL
code的功能，而0x2711对应的处理函数为sub_100017B0。

![](https://images.seebug.org/content/images/2019/08/222b9cd2-579e-4d44-95eb-c16a0f23cf89.jpg-w331s)

图6 函数sub_401260伪代码

![](https://images.seebug.org/content/images/2019/08/e136ab0e-993a-4269-9f7c-e0d6027becdb.jpg-w331s)

图7 函数DsDaqWebService伪代码

分析sub_100017B0（图8所示），该函数中调用了CreateProcessA()函数创建进程。其中lpCommandLine参数由RPC客户端发送，且此处未对此参数进行任何检查。因此，可以通过控制该参数使得CreateProcessA()执行任意命令，从而导致远程命令执行。

![](https://images.seebug.org/content/images/2019/08/b250f8f1-9571-46ca-b60c-f27e348af80e.jpg-w331s)

图8 漏洞函数sub_100017B0执行伪代码

该漏洞在WebAccess Node 8.4中得到修复，如图9所示(case 0x2711为补丁前的分支代码，case 1为补丁后的分支代码)
，修复后的IOCTL增加了sub_100022D0函数对用户的输入内容进行检查。具体的检查方式是同白名单进行比较来判断参数是否合法。

![](https://images.seebug.org/content/images/2019/08/0f083b52-71ca-4011-b020-deb93f4602d2.jpg-w331s)

图9 IOCTL code 0x2711补丁前后伪代码

同样类型的漏洞还有CVE-2019-10985，该漏洞触发点位于IOCTL code
0x2715功能实现。该功能是通过unlink删除指定文件，而文件名可以由RPC客户端任意指定。由于对参数没有任何过滤，可以设置该参数为任意文件路径，从而导致任意文件删除漏洞。

#### 2、CVE-2019-10993指针解引用漏洞

该漏洞同样也是位于webvrpcs处理RPC消息的动态链接库drawsrv.dll中，触发点在处理IOCTL code
0x27DB的代码中。如下图10所示：

![](https://images.seebug.org/content/images/2019/08/2d102436-1cd4-4b3d-99cf-4ac3d743ed27.jpg-w331s)

图10 IOCTL code 0x27DB伪代码

通过分析，Filename变量直接来源于webvrpcs接收的RPC数据，通过修改该Filename的值可以控制SQLFreeConnet的参数。分析SQLFreeConnet函数，其调用了函数FreeIDbc释放连接句柄ConnectionHandle（即SQLFreeConnet参数）。

![](https://images.seebug.org/content/images/2019/08/0f66c7e2-3396-4e55-a3ab-b8da97426066.jpg-w331s)
图11 IOCTL code 0x27DB处理流程

在FreeIDbc函数中，ConnectionHandle会被视为指针类型解引用。因此，通过构造RPC消息可控制指针解引用，从而造成内存访问错误。

![](https://images.seebug.org/content/images/2019/08/d452e2a2-7358-408f-9891-fe92637d3402.jpg-w331s)

图12 FreeIDbc函数处理流程

进一步分析可发现，参数Memory赋值给了v2，在后续的操作中(v2[1]+36)赋值给了v7，后又进行了v7[1]的操作。而Memory受用户输入控制，因此v7[1]写入内存的地址可控，从而形成一个任意地址写漏洞。由于是内存写入操作，精心利用可能造成代码执行。

类似这类指针未校验的漏洞在Advantech WebAccess
Node中还有很多，CVE编号均为CVE-2019-10993，包含多个ZDI漏洞编号(ZDI-19-614 ZDI-19-613 ZDI-19-612
ZDI-19-611 ZDI-19-610 ZDI-19-609 ZDI-19-608 ZDI-19-607 ZDI-19-606 ZDI-19-605
ZDI-19-604 ZDI-19-603 ZDI-19-602 ZDI-19-601 ZDI-19-600 ZDI-19-599 ZDI-19-598
ZDI-19-597 ZDI-19-596
ZDI-19-595)。实际上这类漏洞就是对传入webvrpcs中的DsDaqWebService函数的参数没有进行检查，导致几乎所有的IOCTL code
ODBC类函数都可以产生内存破坏漏洞，如图13所示：

![](https://images.seebug.org/content/images/2019/08/19e63719-036d-459f-85e5-cba59bd959c1.jpg-w331s)

图13 可能造成内存破坏的IOCTL code

该系列漏洞在新版本8.4中得到修复，方式为在调用SQL函数前增加了检验函数(链式校验流程如图15)，判断参数是否合法，如图14所示。

![](https://images.seebug.org/content/images/2019/08/fd65c651-e0e2-4dcc-b7b3-6691accb086a.jpg-w331s)

图14 修复后的DsDaqWebService函数

![](https://images.seebug.org/content/images/2019/08/ef3e6e19-5094-4dcb-8b30-bb24b56163ed.jpg-w331s)

图15 链式校验流程

**3、CVE-2019-10991栈溢出漏洞**

CVE-2019-10991包含了多个栈溢出漏洞，由于这些漏洞的触发条件和产生原因都较为相似，在此仅对其中一个漏洞（ZDI-19-594）进行详细分析。

WebAccess
Node软件包含了一系列小组件程序，bwscrp.exe是其中一个。bwscrp.exe程序入口函数接收两个命令行参数（如图16），随后使用命令行参数lpCmdLine作为函数参数之一调用了函数sub_4061F0。在函数sub_4061F0中，Source即为lpCmdLine，后续执行直接使用strcpy将Source拷贝到栈参数Dest，而没有检查Source的数据长度。由于变量Dest距离栈顶只有400字节，当Source长度超过404字节时，
strcpy函数调用将覆盖栈上的函数返回地址，是一个典型的栈溢出漏洞。

![](https://images.seebug.org/content/images/2019/08/91d7225b-43dc-4348-853b-e3d242cd5653.jpg-w331s)

图16 bwscrp.exe WinMain函数伪代码

![](https://images.seebug.org/content/images/2019/08/3c13dbe7-76e8-4ac6-b655-a417b85ae03c.jpg-w331s)
图17 bwscrp sub_4061F0函数伪代码

此外，CVE-2019-6550 (ZDI-19-585 ZDI-19-330 ZDI-19-329 ZDI-19-328 ZDI-19-327
ZDI-19-325
ZDI-19-323)漏洞原理同CVE-2019-10991也极为类似。CVE-2019-6550(ZDI-19-330)栈溢出漏洞存在于upandpr.exe。该程序主函数中的scanf调用将用户提供的数据拷贝到栈内存，在拷贝之前未对用户提供的数据长度进行验证，如图18所示。

![](https://images.seebug.org/content/images/2019/08/6dc7be3c-be62-434d-b0ab-c8b60947b041.jpg-w331s)
图18 upandpr.exe WinMain函数伪代码

CVE-2019-10991在最新版本的Advantech WebAccess
Node中得到修复，补丁方式大致相同。以图19所示的ZDI-19-594为例(左部分为补丁前代码，右部分为补丁后代码)，修复方式为在strcpy调用之前加入数据长度检查。

![](https://images.seebug.org/content/images/2019/08/ae5fb095-821d-4289-bbaa-32d33402a0be.jpg-w331s)

图19 bwscrp.exe 补丁前后反编译伪代码

CVE-2019-6550在最新版本的Advantech WebAccess
Node中也得到修复，补丁方式大致相同。以图20所示的ZDI-19-330为例(上部分为补丁前代码，下部分为补丁后代码)，修复方式为在sscanf的格式化输出符设置了最大字符长度来防止sscanf函数栈溢出的产生。

![](https://images.seebug.org/content/images/2019/08/b15d46b4-6746-42d3-860a-7cbf5581e759.jpg-w331s)

图20 upandpr.exe 补丁前后反编译伪代码

### Advantech WebAccess Node 漏洞挖掘

在分析ZDI披露的漏洞过程中，我们对Advantech WebAccess进行了初步审计，额外发现了三个漏洞，可导致任意文件删除和远程命令执行。

#### 1、CNVD-2019-23511任意文件删除漏洞（中危）

WebAccess
Node软件会在系统中注册一个动态模块，分析该模块发现其包含一个文件删除函数，但没有对传入参数的进行安全检查过滤，导致存在任意文件删除漏洞。

#### 2、CNVD-2019-23512命令执行漏洞（高危）

WebAccess
Node软件会在系统中注册另一个动态模块，分析该模块发现其包含一个外部程序调用功能，但没有对传入的调用参数进行检查，导致存在任意命令执行漏洞。

#### 3、CNVD-2019-23513命令执行漏洞（高危）

在分析ZDI披露的漏洞过程中，我们对Advantech WebAccess进行了初步审计，额外发现了三个漏洞，可导致任意文件删除和远程命令执行。

### 结 语

通过对这一系列漏洞的分析可以发现，Advantech WebAccess
软件在实现过程中缺乏对程序输入的安全检查代码，对重要操作的认证不足，因此才爆出如此多的漏洞。不同于常规信息化系统，工业控制系统对稳定性的要求极高，工控软件漏洞被利用可能造成严重的后果。希望WebAccess相关用户单位持续关注其漏洞公告，及时安装补丁以修复相关漏洞。

**参考链接：**

1.<https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=webaccess>

2.<https://www.zerodayinitiative.com/advisories/ZDI-18-024/>

3.<https://www.exploit-db.com/exploits/44278>

4.<https://www.zerodayinitiative.com/advisories/ZDI-19-616/>

5.<https://www.zerodayinitiative.com/advisories/ZDI-19-594/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1017/>

