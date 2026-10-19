##  **前言**

 **在Win10
x64环境下替换正常的进程，是一个比较高超的技术。使用该技术，可以内存执行病毒、木马。在文件层面实现免杀。可以把一个木马使用DES加密，放在资源里。执行时，从资源里释放出来，在内存里进行DES解密，注入到一个系统的进程中。**

![](https://image.3001.net/images/20180531/15277635985792.png!small)

##  **环境**

> 1\. VisualStudio 2015 企业版
>
> 2\. 普通程序 Notepad.exe (C:\windows\system32\Notepad.exe)
>
> 3\. 木马程序 MalWare.exe
>
> 4\. 源码下载地址，<http://www.isafe.cc/article.asp?id=77>
>
> 5\. EXE下载地址，<http://www.isafe.cc/article.asp?id=77>

##  **步骤**

创建一个挂起的进程notepad.exe->读取线程上下文->读取进程内存->读取Notepad.exe原始入口点->卸载Notepad.exe占用的内存->将MalWare.exe二进制放入内存缓冲区->在Notepad.exe进程中分配一个内存空间->将MalWare.exe注入到Notepad.exe的进程里->修改Notepad.exe的区段->修改Notepad.exe的入口点->恢复主线程->成功注入。

![](https://image.3001.net/images/20180531/15277636584909.png!small)

##  **代码实现**

###  **一.** 创建一个挂起的进程notepad.exe

    
    
    BOOL WINAPI CreateProcess(  _In_opt_    LPCTSTR              lpApplicationName,  _Inout_opt_ LPTSTR               lpCommandLine, _In_opt_    LPSECURITY_ATTRIBUTESlpProcessAttributes, _In_opt_    LPSECURITY_ATTRIBUTESlpThreadAttributes, _In_        BOOL                 bInheritHandles, _In_        DWORD                dwCreationFlags,  _In_opt_    LPVOID               lpEnvironment,  _In_opt_    LPCTSTR              lpCurrentDirectory, _In_        LPSTARTUPINFO        lpStartupInfo, _Out_       LPPROCESS_INFORMATIONlpProcessInformation);

> a.) lpApplicationName 这个参数是可执行文件的路径。例如
>
> c:\programfiles\sub dir\program.exe
>
> c:\program files\a.exe
>
> netstat
>
> b.) lpCommandLine 这个表示应用程序的参数。例如 -an
>
> c.) lpProcessAttributes 进程属性结构体变量
>
> d.) lpThreadAttributes 线程属性结构体变量
>
> e.) bInheritHandles 指定当前进程内句柄不可以被子进程继承
>
> f.) dwCreationFlags 进程创建标识符，CREATE_SUSPENEDE 表示创建一个挂起的进程。
>
> g.) lpEnvironment 指向一个新进程的环境块。如果此参数为空，新进程使用调用 进程的环境。
>
> h.) lpCurrentDirectory 指向一个以NULL结尾的字符串，这个字符串用来指定子进程的
> 工作路径。这个字符串必须是一个包含驱动器名的绝对路径。如果这个参数为NULL，新进程将使用与调用进程相同的驱动器和目录。
>
> i.) lpStartupInfo 指向一个用于决定新进程的主窗体如何显示的STARTUPINFO结 构体。
>
> j.) lpProcessInformation保存进程所有信息的结构体变量。

CreateProcess函数用于创建一个进程，cAppName为C:\\\Windows\\\notepad.exe，是程序文件的路径，第6个参数为CREATE_SUSPENDED，表示创建一个挂起的进程。最后2个参数si，pi保存了进程的相关信息(进程的句柄，线程的句柄等)。

###  二. 读取线程上下文

GetThreadContext函数用于获取线程上下文。

Pi.hThread为线程句柄，

context线程信息结构体。

###  三. 读取Notepad.exe原始入口点

ReadProcessMemory函数用于读取另一个进程的内存。这里dwVictimBaseAddr存放读取的数据，大小为4个字节。

原型

    
    
    BOOL ReadProcessMemory(HANDLE hProcess,LPCVOIDlpBaseAddress,LPVOID lpBuffer,DWORD nSize,LPDWORDlpNumberOfBytesRead);

> 第一个参数hProcess，要读取的进程句柄。
>
> 第二个参数lpBaseAddress，要读取的进程的内存首址。开始地址。
>
> 第三个参数lpBuffer，接收数据内容的缓冲区。
>
> 第四个参数 nSize，从内存中读取的字节数。
>
> 第五个参数lpNumberOfBytesRead，已经读取的字节数。

函数返回0表示调用失败。

###  四. 卸载Notepad.exe占用的内存

pfnNtUnmapViewOfSection函数用于卸载进程占用的内存

###  五. 在Notepad.exe进程中分配一个内存空间

VirtualAllocEx函数用于在指定进程中分配一个内存空间。

函数原型：

    
    
    LPVOIDVirtualAllocEx(HANDLE hProcess,LPVOIDlpAddress,SIZE_T dwSize,DWORDflAllocationType,DWORD flProtect);

> 第一个参数hProcess，需要在其中分配空间的进程的句柄。
>
> 第二个参数lpAddress，分配的内存首址。
>
> 第三个参数 dwSize，分配的内存大小。
>
> 第四个参数flAllocationType，内存区域的类型。
>
> 第五个参数flProtect，内存保护属性。

###  六. 将MalWare.exe注入到Notepad.exe的进程里，修改Notepad.exe的区段和PE文件头

![](https://image.3001.net/images/20180531/15277638122100.png!small)

WriteProcessMemory函数用于向Notepad.exe进程写入任何数据。

函数原型：

    
    
    BOOL WINAPI WriteProcessMemory(
       HANDLE  hProcess,
      LPVOID  lpBaseAddress,
      LPCVOID lpBuffer,
      SIZE_T  nSize,
      SIZE_T  *lpNumberOfBytesWritten
    );

> 第一个参数hProcess，待操作的进程句柄。
>
> 第二个参数 lpBaseAddress，要写入数据的起始地址。
>
> 第三个参数lpBuffer，要写入数据的缓冲区首址。
>
> 第四个参数 nSize， 要写入数据的长度。
>
> 第五个参数lpNumberOfBytesWritten，已写入的数据长度。

###  七. 修改Notepad.exe的入口点 RCX存放的是入口点。

###  八. 恢复主线程

> SetThreadContext()函数用于恢复线程上下文，这里指定了新的入口点地址 Rcx
>
> ResumeThread ()函数用于启动挂起的线程。

##  **编译为EXE**

必须用Visual Studio 2015进行编译。源码下载(<http://www.isafe.cc/article.asp?id=77>)

![](https://image.3001.net/images/20180531/15277638615622.png!small)

在“解决方案资源管理器”中，右键->重新生成

![](https://image.3001.net/images/20180531/15277638791903.png!small)

在输出窗口中看到成功1个(注意这里生成的是一个Release版的64位程序)

![](https://image.3001.net/images/20180531/15277638949424.png!small)

![](https://image.3001.net/images/20180531/15277639034305.png!small)

##  **MalWare.exe** **编译为EXE**

源码下载(<http://www.isafe.cc/article.asp?id=77>)

打开VS2015，点击菜单[文件]->[打开]->[项目/解决方案]。

![](https://image.3001.net/images/20180531/15277639145553.png!small)

打开Malware.vcxproj工程文件，进行编译，模式为Release，平台为x64。

![](https://image.3001.net/images/20180531/15277639244060.png!small)

在输出窗口中，提示成功1个。

![](https://image.3001.net/images/20180531/15277639345891.png!small)

##  **Win10** **平台测试**

将ProcessReplacement.exe拖入虚拟机。

![](https://image.3001.net/images/20180531/15277639471401.png!small)

双击，提示

![](https://image.3001.net/images/20180531/15277639544073.png!small)

看样子是缺少什么文件？将VS2015环境下的文件vcruntime140.dll，复制到虚拟机

![](https://image.3001.net/images/20180531/15277639626408.png!small)

![](https://image.3001.net/images/20180531/1527763972842.png!small)

双击执行ProcessReplacement.exe

![](https://image.3001.net/images/20180531/15277639814848.png!small)

##  **总结**

本文介绍的Win10 x64进程镂空技术，可以在文件层面实现木马免杀。

***本文作者：河马安全网，转载请注明来自FreeBuf.COM**

