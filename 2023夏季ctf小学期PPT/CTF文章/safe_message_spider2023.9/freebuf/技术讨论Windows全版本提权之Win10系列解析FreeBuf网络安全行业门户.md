***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **一、** 背景介绍  

 **2018 年 8 月 27 日，境外安全研究人员 SandboxEscaper 在其个人主页上披露了影响 Windows 10 及Windows
Server
2016系统的一个安全漏洞。根据描述，该漏洞存在于Windows的计划任务调度服务中，利用该漏洞攻击者可以从USER提升至SYSTEM权限。**

天融信阿尔法实验室第一时间进行跟进，进行漏洞复现和分析。本文将以Windows 10
X64系统平台为基础，详细介绍该漏洞及漏洞利用方法。同时附带利用该漏洞实现的提权工具及源码。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654926_5b977e4e33c08.png!small)

## 二、漏洞简介

Windows
计划任务调度服务的接口函数（schedsvc!SchRpcSetSecurity()）用于修改计划任务相关文件访问控制属性，未验证调用者身份。攻击者可主动调用该接口函数，配合“硬链接（HardLink）”，达到修改指定系统文件访问控制属性的目的。当一些系统服务的关键模块（EXE/DLL）被篡改，再次调用该服务，攻击者的代码将得以执行，且为SYSTEM权限。

## 三、相关技术

在具体讲解漏洞及其利用方法之前，让我们首先简单了解一些与之相关的知识。介绍这部分内容是为了让不熟悉Windows相关特性的读者对该漏洞有更加清晰的认识，熟悉以下内容的读者可以跳过这一部分。

### Security Descriptor 安全描述符

在Windows系统下，Security Descriptor安全描述符（简称SD）
是包含一个内核对象所有关于安全设置的数据结构。SD中包括用户SID、DACL、SACL。DACL表明了哪些用户可以访问该对象、以什么方式访问该对象（如CreateFile时指定的访问权限）。

系统中每一个文件、进程等等都有对应的内核对象，其中都有一个SD结构，包括每个用户对该文件支持的操作。这里摘取《Windows
安全编程》一书中关于该内容的部分说明，需要详细了解该部分内容的可以读一下这本书。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654946_5b977e62a416b.png!small)
![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654951_5b977e672b852.png!small)

SchRpcSetSecurity()漏洞函数支持调用者修改部分文件的安全属性，其中安全属性通过SDDL字符串描述，Windows会解析SDDL并转换为SD描述符。有需要了解SDDL详细信息的可以参考尾部连接。

###  ALPC (Advanced Local Procedure Call)高级过程调用

ALPC是一种用户模式与内核模式通讯的方式，也支持进程间通讯。该方式被Windows系统大量使用。ALPC允许在系统内运行的客户端进程要求在同一系统中运行的服务器进程提供某些信息或执行某些操作。

其中Windows计划任务就采用了该方式进行管理，schedsvc模块以服务的方式运行，可以看做一个服务提供者。计划任务管理程序可以通过ALPC调用schedsvc的接口进行一些增删改查操作。

###  **硬链接（HardLink）**

硬链接是通过将多于一个的路径引用在单个文件的符号链接。通俗的说，硬链接可以看做特殊的“快捷方式文件”。我们可以通过mklink在指定位置为指定文件创建硬链接，这时候就可以通过这2个路径访问同一个文件。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654960_5b977e70ac9e3.png!small)

当然硬链接有其他很多限制和特点，这里不做太多介绍，只介绍与本文相关的内容。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654966_5b977e768e2a0.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536654972_5b977e7cbd8b8.png!small)

如微软所描述，硬链接并没有单独的SD描述符。更改硬链接的安全描述符，即更改了基础文件的安全描述符。

## 四、漏洞位置

漏洞函数位于Windows计划任务调度服务中，服务名称为 Task
Scheduler，主模块为schedsvc.dll，依靠svchost.exe程序注册为系统服务。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655014_5b977ea677c01.png!small)

该模块接口函数SchRpcSetSecurity()，用于修改计划任务有关文件或目录的安全属性。该函数并没有编码上的安全问题，产生安全问题的原因是该函数没有验证调用者的来源及合法性，即任意程序均可以通过ALPC接口调用该函数修改文件属性。这里贴一下微软针对该函数的说明:![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655022_5b977eae5da94.png!small)

指定文件PATH 和
安全描述SDDL，该函数将为指定的文件设置对应的安全属性，当然PATH并不是指定一个文件全路径，而是指定一个“任务名称”，该函数会根据任务名称补全路径，具体的后面会介绍。下面是IDA反汇编该函数的内容：![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655029_5b977eb537d57.png!small)
![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655034_5b977ebadb68d.png!small)

整个流程其实并不复杂，一些常规操作。这里贴出我们需要了解的相关部分的代码，也就是图中说明的设置文件安全描述符的函数代码：![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655048_5b977ec875522.png!small)

可见该处为一处虚函数调用，这时候IDA中没有很好的描述函数的地址及名称，只好拿起Windbg进行动态调试，使用WinDbg附加到svchost.exe进程（系统中有多个svchost进程，可以根据命令行参数或者已加载模块定位目标进程），最终定位到该函数最终调用了taskcomp!
SetSDNotification
()函数：![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655056_5b977ed0825b9.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655063_5b977ed7e3260.png!small)

tsched!SetJobFileSecurityByName()最终会设置文件安全属性，以下是该函数的关键流程![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655070_5b977ede5070a.png!small)

最后来看看动态调试的情况,在WinDbg中单步跟踪task!SetSDNotification()，该函数接收2个参数。由于是X64汇编环境，函数调用的参数传递采用X64传参方式，前四个参数依次通过RCX
RDX R8
R9进行传递。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655077_5b977ee53eb21.png!small)
![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655085_5b977eed17f9d.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655092_5b977ef41ede1.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655096_5b977ef89e50c.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655104_5b977f0025a68.png!small)

至此漏洞函数关键流程已完毕，关键之处是schedsvc!SchRpcSetSecurity()内部会调用taskcomp!SetSDNotification(),
按照传递的任务名称参数和SDDL安全描述字串，设置%systemdir%\\\Tasks\\\任务名称.job 的安全属性。

单单能修改该目录的一个文件内容和文件属性似乎也没有什么意义，还是没有一段以SYSTEM权限执行的代码，无法有效利用。这时候就要提起前面提起过的Windows符号链接之一的“硬链接”，在
%systemdir%\\\Tasks目录创建一个链接到系统程序A的硬链接，这个时候通过修改安全属性，使得普通用户也有权限修改系统程序A的文件内容，然后通过系统接口启动篡改后的程序A，让我们的代码以高权限运行。举个例子：系统服务均运行在SYSTEM权限下，查找一下哪些系统目录的EXE/DLL被注册为服务，修改该文件后启动该服务，即可获得SYSTEM权限。

## 五、漏洞利用

前文已经介绍过漏洞函数的流程及作用，攻击者通过SchRpcSetSecurity()接口函数可以设置对系统程序的访问属性，使得普通用户权限运行的程序可以修改系统程序及其执行代码。笔者完善了SandboxEscaper提供的POC，制作了支持Windows10
x86/x64 及Windows
Server2016系统的提权工具（[GitHub传送门](https://github.com/alpha1ab/Win2016LPE)），下面将以此为例介绍该漏洞利用的完整流程。

该EXP通过利用漏洞函数，修改系统服务Microsoft XPS DocumentWriter
服务(该服务为XPS打印服务)的关键DLL，然后通过COM接口发送打印任务，最终系统将会启动该服务。

以下代码是定位文件路径以及创建文件硬链接的过程：![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655127_5b977f17ed53b.png!small)

不过有一点需要注意的是，由于硬链接需要在%systemdir%\\\tasks目录创建，普通程序并无法成功创建，所以这个操作需要由有权限的程序去做。SandboxEscaper的DEMO中选择了注入代码到Notepad程序中，以Notepad进程的运行环境是有权限在该目录创建硬链接的。笔者的EXP中，将注入操作顺带实现了，自己创建一个进程并注入。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655136_5b977f2065e3a.png!small)

远程线程方式注入一个DLL到Notepad中，创建硬链接并触发漏洞函数。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655145_5b977f2922fa5.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655148_5b977f2ced179.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655153_5b977f31541be.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655159_5b977f37448ff.png!small)

上面通过RPC方式调用schedsvc!SchRpcSetSecurity()函数，触发漏洞。其中所传递的SDDL安全描述字符串，将目标文件设置为验证用户拥有可写入权限，其格式可以自己解读，MSDN有例子![Windows全版本提权之Win10系列](https://image.3001.net/images/20180912/1536715260_5b9869fc4069a.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180912/1536715264_5b986a00e2798.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655171_5b977f437aea3.png!small)

在触发漏洞之后，理论上目标文件以及可以修改，上面的代码用于修改文件。从资源取出DLL并覆盖。在DLL修改完毕之后，通过COM组件启动该服务进行打印。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655176_5b977f48dfa9c.png!small)

至此漏洞利用完毕。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655184_5b977f502b7a1.png!small)

这里贴上EXP的代码，DLL加载DllMain()函数必被调用，EXP由DLLMain()开始执行漏洞利用代码。该exp通过本地SOCKET接收用户参数并执行，然后通过SOCKET把结果传回给漏洞利用程序展示给用户。![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655197_5b977f5d68d18.png!small)![Windows全版本提权之Win10系列](https://image.3001.net/images/20180911/1536655205_5b977f6519a60.png!small)

## 六、总结

到这里，漏洞分析和漏洞利用都介绍完了，该漏洞属于逻辑漏洞，而并非编码产生的安全漏洞。

目前微软暂未发布相关安全更新，建议用户不要运行来源不明的可执行程序，避免遭受此类漏洞的攻击。

## 七、参考链接

> 1）SchRpcSetSecurity()函数
>
> <https://msdn.microsoft.com/en-us/library/cc248452.aspx>
>
> 2）SDDL安全描述字符串
>
> <https://docs.microsoft.com/en-us/windows-hardware/drivers/kernel/sddl-for-> device-objects>
>
> 3）Access Control Lists
>
> <https://docs.microsoft.com/zh-cn/windows/desktop/SecAuthZ/access-control-> lists>
>
> 4）DACLs and ACEs
>
> <https://docs.microsoft.com/zh-cn/windows/desktop/SecAuthZ/dacls-and-aces>
>
> 5）HardLink 硬链接
>
> <https://docs.microsoft.com/zh-cn/windows/desktop/FileIO/hard-links-and-> junctions>

 ***本文作者：alphalab，转载请注明来自 FreeBuf.COM**

