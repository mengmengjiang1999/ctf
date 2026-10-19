***本文原创作者：nekoyansu，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 前言

**近年来，各类恶意软件层出不穷，反病毒软件也更新了各种检测方案以提高检测率。其中比较有效的方案是动态沙箱检测技术，即通过在沙箱中运行程序并观察程序行为来判断程序是否为恶意程序。**

与此同时，安全人员也在各类虚拟机中运行程序进行分析。为了逃避沙箱/安全人员的检测，恶意软件使用了各类识别沙箱/虚拟机的技术，用于判断自身程序是否运行在沙箱/虚拟机中。文中介绍了几种检测虚拟机和沙箱的技术，如果有错误之处请各位dalao指正。

## 一、常用虚拟机检测

很多安全人员使用VMware和VirtualBox运行程序，以下介绍几种办法检测vmware和vbox特征。

### 1.通过进程名检测VMware&VirtualBox

以下是Vmware和VirtualBox可能存在的进程，我们可以使用Process32First，Process32Next等WINAPI列举进程并且检测是否存以下内容。

Vmware：

> Vmtoolsd.exe
>
> Vmwaretrat.exe
>
> Vmwareuser.exe
>
> Vmacthlp.exe

VirtualBox：

> vboxservice.exe
>
> vboxtray.exe

以下是示例代码：

![图片.png](https://image.3001.net/images/20190505/1557054454_5ccec3f682f40.png!small)如上图，我们使用了CreateToolhelp32Snapshot给进程来个快照，然后使用Process32First，Process32Next枚举进程，并将进程名传入check函数中检测是否匹配数组中的名字，如果匹配到其中的一个，说明在VirtualBox中运行，CheckProcess函数将返回false。

![图片.png](https://image.3001.net/images/20190505/1557054464_5ccec400431f4.png!small)

以下是在VirtualBox中运行的例子：

![图片.png](https://image.3001.net/images/20190505/1557054475_5ccec40bf0ed2.png!small)

备注：许多分析虚拟机中没有安装常用软件，我们也可以使用类似的办法检测系统中的IM、浏览器等常用程序，来判断程序是否运行在虚拟机中。

### 2.检测注册表

以下是vbox和vmware存在的一些注册表：

    
    
    HKLM\SOFTWARE\Vmware Inc\Vmware Tools
    
    HKLM\HARDWARE\DEVICEMAP\Scsi\Scsi Port 2\Scsi Bus 0\Target Id 0\Logical Unit Id 0\Identifier
    
    HKEY_CLASSES_ROOT\Applications\VMwareHostOpen.exe
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Oracle\VirtualBox Guest Additions

通过检测指定注册表键值是否存在来判断程序是否在虚拟机中运行：

![图片.png](https://image.3001.net/images/20190505/1557054507_5ccec42bc84ff.png!small)

如上图使用RegOpenKey WINAPI打开指定键，如果成功代表存在该键，由此程序判断是否在虚拟机中。

### 3.检测硬盘中的文件

下面搜集来了一些vmware和vbox存在的文件特征。可以用多种方法检测文件是否存在，如：WMIC，WINAPI和CMD。

 **VMware**

    
    
     C:\windows\System32\Drivers\Vmmouse.sys
    
    C:\windows\System32\Drivers\vmtray.dll
    
    C:\windows\System32\Drivers\VMToolsHook.dll
    
    C:\windows\System32\Drivers\vmmousever.dll
    
    C:\windows\System32\Drivers\vmhgfs.dll
    
    C:\windows\System32\Drivers\vmGuestLib.dll

 **VirtualBox**

    
    
     C:\windows\System32\Drivers\VBoxMouse.sys
    
    C:\windows\System32\Drivers\VBoxGuest.sys
    
    C:\windows\System32\Drivers\VBoxSF.sys
    
    C:\windows\System32\Drivers\VBoxVideo.sys
    
    C:\windows\System32\vboxdisp.dll
    
    C:\windows\System32\vboxhook.dll
    
    C:\windows\System32\vboxoglerrorspu.dll
    
    C:\windows\System32\vboxoglpassthroughspu.dll
    
    C:\windows\System32\vboxservice.exe
    
    C:\windows\System32\vboxtray.exe
    
    C:\windows\System32\VBoxControl.exe

例：使用cmd命令检测文件是否存在：

    
    
    if exist "C:\windows\System32\vboxtray.exe" echo exist

![图片.png](https://image.3001.net/images/20190505/1557054560_5ccec4600d7f0.png!small)

例：使用c语言中的access函数判断文件是否存在：

    
    
    if ( !access("C:\\windows\\System32\\vboxtray.exe",0) )
    
    printf(“在虚拟机中”)
    
    else
    
    printf(“不在虚拟机中”)

### 4.判断运行中的服务

下面列表中的服务如果存在，很可能运行在虚拟机中，我们可以使用wmic或命令sc.exe query等方式判断是否存在以下服务。

> VMTools
>
> Vmrawdsk
>
> Vmusbmouse
>
> Vmvss
>
> Vmscsi
>
> Vmxnet
>
> vmx_svga
>
> Vmware Tools

例：在vbox虚拟机中使用sc query获取服务名。

![图片.png](https://image.3001.net/images/20190505/1557054594_5ccec4822ba7b.png!small)

上图黄色标记的VBoxService就是有可能携带的vbox虚拟机特征之一。

### 5.检测mac地址前缀

以下列出了几个vmware和vbox可能出现的默认MAC地址前缀，可以逐一判断来确认程序是否运行在虚拟机中：

> 00:05:69 (Vmware)
>
> 00:0C:29 (Vmware)
>
> 00:1C:14 (Vmware)
>
> 00:50:56 (Vmware)
>
> 08:00:27 (VirtualBox)

![图片.png](https://image.3001.net/images/20190505/1557054647_5ccec4b7f15c1.png!small)

如图在vbox虚拟机中使用ipconfig /all命令得到MAC地址，前缀08-00-27在列表中，可以判断是vbox虚拟机。

我们可以使用c中的pipe来获取ipconfig /all的结果，并且判断指定MAC是否存在，来判断是否在虚拟机中运行。

![图片.png](https://image.3001.net/images/20190505/1557054654_5ccec4bea4902.png!small)

下图是在vbox中运行的结果：

![图片.png](https://image.3001.net/images/20190505/1557054663_5ccec4c714a7a.png!small)

下图是普通运行：

![图片.png](https://image.3001.net/images/20190505/1557054671_5ccec4cfb0418.png!small)

### 6.使用CPUID指令检测虚拟机

CPUID是一个面向x86架构的处理器补充指令，它的名称派生自CPU识别，作用是允许软件发现处理器的详细信息。EFLAGS中的bit
21可以识别CPU是否支持CPUID指令，如下图：

![图片.png](https://image.3001.net/images/20190505/1557054687_5ccec4df36d94.png!small)

现在的cpu都是支持此指令的。cpuid 指令由 eax 寄存器获得输入，执行 cpuid 指令前，需要将功能号传给 eax 寄存器。

![图片.png](https://image.3001.net/images/20190505/1557054698_5ccec4ea13dcf.png!small)

在上图中EAX=0：获取CPU的Vendor ID。

用下面的方法执行该功能：

    
    
    mov eax, 0
    
    cpuid

执行CPUID指令后，返回的Vendor ID固定为12个ASCII字符，依次存放在EBX、EDX、ECX中。

EAX=1部分：处理器签名（Processor Signiture）和功能（Feature）位。

    
    
    mov eax, 1
    
    cpuid

执行完成后，处理器签名放在EAX中，功能位及其它的内容分别放在EBX、ECX和EDX中。

将EAX置为1，运行CPUID指令后获取ECX中的值并判断。

下图为示例代码：

![图片.png](https://image.3001.net/images/20190505/1557054710_5ccec4f6d9b1c.png!small)

注：可以通过设置eax中不同的功能号自由获取cpu信息。

## 二、在线分析沙箱检测

在线沙箱通过记录程序运行情况进行判定，下面介绍一些小技巧来检测程序是否在沙箱里运行。

### 1.延迟运行

在各类检测沙箱中，检测运行的时间往往是比较短的，因为其没有过多资源可以供程序长时间运行，所以我们可以延迟等待一会儿后再进行真实的操作。

![图片.png](https://image.3001.net/images/20190505/1557054735_5ccec50f8dda3.png!small)

std::sleep_for()：线程调用该方法时，同样会让出CPU，并且休眠一段时间，从而让其他线程有机会运行。等到休眠结束时，才参与CPU调度。

我们使用this_thread::sleep_for()来延迟当前线程，此方法比使用Sleep()更不容易被沙箱使用模拟方法绕过。

### 2.检测开机时间

许多沙箱检测完毕后会重置系统，我们可以检测开机时间来判断是否为真实的运行状况。

我们使用WINAPI
GetTickCount()来获取机器已运行的时间（以秒为单位）。然后判断开机运行时间是否大于1个小时，如果开机时间小于1小时就返回false。

下图是示例代码：

![图片.png](https://image.3001.net/images/20190505/1557054749_5ccec51d2d956.png!small)

### 3.检测物理内存

当今大多数pc具有4GB以上的RAM,我们可以检测RAM是否大于4GB来判断是否是真实的运行机器。

内存大小可能会大于4GB的情况下我们需要用GlobalMemoryStatusEx获取内存信息，查看MSDN会发现MEMORYSTATUSEX的成员值所占的字节数比MEMORYSTATUS成员值占用的字节数大，其中的成员ullTotalPhys为物理内存大小。

下图代码使用GlobalMemoryStatusEx()来获得一个DWORDLONG类型的内存大小，然后与4GB比较，小于4GB返回false，大于4GB返回true。![图片.png](https://image.3001.net/images/20190505/1557054763_5ccec52b908a7.png!small)

### 4.检测CPU核心数

大多数pc拥有4核心cpu，许多在线检测的虚拟机沙盘是2核心，我们可以通过核心数来判断是否为真实机器或检测用的虚拟沙箱。

使用winapi函数GetSystemInfo()将系统信息写入类型为SYSTEM_INFO的结构体，其中成员dwNumberOfProcessors就是CPU核心数（超线程技术也算入核心），如果其小于4，CheckCPU()将返回false，检测不通过。

![图片.png](https://image.3001.net/images/20190505/1557054777_5ccec5398e746.png!small)

### 5.检测临时文件数

正常使用的系统，其中用户的临时文件夹中有一定数量的临时文件，可以通过判断临时文件夹内的文件数量来检测是否在沙箱中运行。

先使用GetEnvironmentVariable()获取temp路径，再利用FindFirstFile()与FindNextFile()枚举temp文件夹内的文件数量，如果小于30，就返回false，代表检测失败。

![图片.png](https://image.3001.net/images/20190505/1557054792_5ccec54890aaa.png!small)

## 总结与备注

当前有部分检测沙箱使用了Intel Processor
Tracing技术，可以高效追踪程序的分支，在实际使用过程中，需要对if分支进行一定程度的代码混淆，防止分支模拟技术。并且现代检测沙箱正在不断提高拟真度，单独使用几个判断方法可能无法得出正确的判断，要多种方法结合使用，才能发挥出良好的效果。

## 参考链接：

[ _https://docs.microsoft.com/zh-cn/windows/desktop/api/_](https://docs.microsoft.com/zh-cn/windows/desktop/api/)

[
_http://blog.chinaunix.net/uid-20729583-id-1884599.html_](http://blog.chinaunix.net/uid-20729583-id-1884599.html)

 ***本文原创作者：nekoyansu，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

