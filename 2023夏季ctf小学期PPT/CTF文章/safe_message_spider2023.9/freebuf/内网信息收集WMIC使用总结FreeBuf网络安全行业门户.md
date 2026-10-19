> 当你的领导去安排你完成一项任务，其实是让你完成任务的同时，学习不懂的领域和知识 --大余

## 使用WMIC进行内网信息收集

渗透测试的本质就是信息收集

比cmd更加强大的命令行----WMIC

在攻击渗透当中，在后渗透阶段，更适合使用WMIC。当攻击者已经穿透外网，进入内网，在远程pc上拿到meterpreter会话或者Cobalt
Strike上线后，可以枚举收集大量的系统信息，在内网遨游。说到内网渗透，最重要的还是内网的信息收集，在内网中要知道，我是谁，这是哪，我在哪，这三个方面，利用WMIC命令行工具可以进行更深程度的操作

## WMIC

可以查看WMIC命令的全局选项，WMIC全局选项可以用来设置WMIC环境的各种属性，通过结合各种全局选项以及参数，我们就可以通过WMIC环境来管理整个系统了。

    
    
    wmic /?

![1](https://image.3001.net/images/20210722/1626931778_60f90242e46587b297156.png!small)

## 手动收集

### 获取系统角色、用户名和制造商

根据WMIC命令的操作系统指令，我们可以枚举出大量关于目标系统的信息，包括主机名、域名、制造商以及设备型号

我们还可以添加下列过滤器来获取更精确的扫描结果：

> Roles：它可以给我们提供目标设备在整个网络系统中所扮演的角色，例如工作站、服务器或个人PC等
>
>
> Manufacturer：它可以给我们提供目标系统的制造商和设备型号，因为某些特定制造商所生产的特定型号设备会存在特定的漏洞，因此我们可以利用者部分信息来寻找存在漏洞的设备。
>
> UserName：它可以给我们返回系统的用户名，我们可以利用这部分信息来区分谁是管理员谁是普通用户

[/format:list]：以列表格式输出数据并排列

    
    
    wmic computersystem get Name, Domain, Manufacturer, Model, Username, Roles/format:list

![2](https://image.3001.net/images/20210722/1626931780_60f9024468793230bb034.png!small)

### 获取SID

为了枚举出SID，我们需要用到WMIC中的group选项：

    
    
    wmic group get Caption,InstallDate,LocalAccount,Domain,SID,Status

如下图所示，我们以及查找到了账户名、域名、本地组成员状态、SID以及相应的状态：

![3](https://image.3001.net/images/20210722/1626931781_60f90245638b13ce7952d.png!small)

### 创建一个进程

WMIC命令的process选项可以帮助我们在目标用户的系统中创建各种进程。这种功能可以帮助我们创建后门，或占用大量目标系统的内存：

    
    
    wmic process call create "[Process Name]"  
    wmic process call create "taskmgr.exe"

这个命令不仅会创建一个进程，还会赋予相应的进程ID，所以我们可以根据我们的需要来修改进程信息。

![4](https://image.3001.net/images/20210722/1626931782_60f902465b77c76253db0.png!small)

注意：如果进程创建了一个类似任务管理器和CMD这样的窗口，那么这条命令将会在目标系统中打开这个窗口，这样会引起目标用户的怀疑。

### 修改进程优先级

WMIC命令的process选项还可以帮我们修改目标系统中运行进程的优先级，这是一个非常有用的功能。降低某个进程的优先级可能会导致特定的应用程序发生崩溃，从而提升某个进程的优先级甚至还会导致整个系统发生崩溃。

    
    
    wmic process where name="explorer.exe" call set priority 64

### 终止进程

WMIC命令还可以帮助我们终止目标系统正在运行的进程：

    
    
    wmic process where name="explorer.exe" call terminate

### 获取可执行文件列表

下面的命令可以枚举出整个系统中多有可执行文件的路径地址：

    
    
    wmic process where “NOT ExecutablePath LIKE ‘%Windows%’” GET ExecutablePath

### 获取目录属性

WMIC命令的fsdir选项可以提取文件目录的基本信息，其中包括压缩方法、创建日期、文件大小、是否可读写、是否为系统文件、加密状态以及加密类型等

    
    
    wmic fsdir where="drive='c:' and filename='test' " get /format:list'

### 获取文件属性

WMIC命令的datafile选项可以获取目标系统中文件的基本信息，其中包括压缩方法、创建日期、文件大小、是否可读写、是否为系统文件、加密状态以及加密类型等等：

    
    
    wmic datafile where=’[Path of File]’ get /format:list  
    wmic datafile where name=’c:\\windows\\system32\\demo\\demo.txt’ get /format:list

### 定位系统文件

WMIC可以提取出所有重要系统文件的路径，例如temp目录和win目录等：

    
    
    wmic environment get Description, VariableValue

![5](https://image.3001.net/images/20210722/1626931783_60f9024704b4a92985d53.png!small)

### 获取已安装的应用程序列表

    
    
    wmic product get name

![6](https://image.3001.net/images/20210722/1626931783_60f902479b2e34a23cc52.png!small)

### 获取正在运行的服务列表

获取到正在运行的服务列表后，WMIC还可以提供服务的启动模式，例如：自动、手动和运行中。

    
    
    wmic service where (state=”running”) get caption, name, startmode

![7](https://image.3001.net/images/20210722/1626931784_60f902487bcc2624b74df.png!small)

### 获取系统驱动详情

sysdrive选项可以枚举出驱动的名称、路径和服务类型等数据：

    
    
    wmic sysdriver get Caption, Name, PathName, ServiceType, State, Status /format:list

![8](https://image.3001.net/images/20210722/1626931785_60f9024947d0506546b71.png!small)

### 获取操作系统详情

os选项可以列举出目标系统的上一次启动时间、注册的用户数量、处理器数量、物理/虚拟内存信息和安装的操作系统类型等：

    
    
    wmic os get CurrentTimeZone, FreePhysicalMemory, FreeVirtualMemory, LastBootUpdate,NumberofProcesses, NumberofUsers, Organization, RegisteredUsers, Status/format:list

![9](https://image.3001.net/images/20210722/1626931786_60f9024a087f36a54d9b6.png!small)

部分变量有错误，可以一个一个查询

### 获取主板信息和BIOS序列号

    
    
    wmic baseboard, get Manufacturer, Product, SerialNumber, Version  
    wmic bios, get serialNumber

### 获取内存缓存数据

memcache选项可以获取到内存缓存名和块大小等信息：

    
    
    wmic memcache get Name, BlockSize, Purpose, MaxCacheSize, Status

![10](https://image.3001.net/images/20210722/1626931786_60f9024a8cc371fde7d62.png!small)

### 获取内存芯片信息

memorychip选项可以获取到RAM的相关信息，例如序列号等等：

    
    
    wmic memorychip get PartNumber, SerialNumber

![11](https://image.3001.net/images/20210722/1626931787_60f9024b2b6fad1104c70.png!small)

### 判断目标系统是否为虚拟机

我们可以根据onboarddevice选项返回的信息来判断目标系统到底是真实的主机操作系统，还是一台虚拟机（VMware或Virtual Box）：

    
    
    wmic onboarddevice get Desciption, DeviceType, Enabled, Status /format:list

### 锁定用户账号

我们可以使用useraccount选项来锁定本地用户账号：

    
    
    wmic useraccount where name=’demo’ set disabled=false

### 用户账号重命名

    
    
    wmic useraccount where name=’demo’ rename hacker

### 限制用户修改密码

还可以限制本地用户的密码修改操作：

    
    
    wmic useraccount where name=’hacker’ set passwordchangeable=false

### 获取反病毒产品详情

我们可以枚举出目标系统安装的反病毒产品信息，包括安装位置和版本：

    
    
    wmic /namespace:\\root\securitycenter2 path antivirusproduct GET displayName,productState, pathToSignedProductExe

![12](https://image.3001.net/images/20210722/1626931787_60f9024bb94177e5fac1d.png!small)

### 清理系统日志

WMIC命令的nteventlog选项还可以清除系统的日志记录，当你入侵了某个系统之后，这个命令可以帮助你掩盖攻击痕迹：

    
    
    wmic nteventlog where filename='[logfilename]’ cleareventlog  
    wmic nteventlog where filename=’system’ cleareventlog

## 自动收集

### 使用WMIC脚本自动收集信息

为了简化操作，可以创建一个脚本，在目标机器上完成流程、服务、用户账户、用户组、网时区等信息的查询工作，网上有很多类似脚本，当然也可以自己定制，推荐一个利用wmic收集目标机器信息的脚本
WMIC（管理工具命令行）是最有用的windows命令行工具。默认情况下，任何版本的Windows
xp的低权限用户不能访问WMIC，windows7以上版本的低权限用户允许访问wmic并执行相关查询操作

wmic脚本

    
    
    for /f "delims=" %%A in ('dir /s /b %WINDIR%\system32\*htable.xsl') do set "var=%%A"wmic process get CSName,Description,ExecutablePath,ProcessId /format:"%var%">> out.h tml   
    wmic service get Caption,Name,PathName,ServiceType,Started,StartMode,StartName /forma t:"%var%" >> out.html   
    wmic USERACCOUNT list full /format:"%var%" >> out.html   
    wmic group list full /format:"%var%" >> out.html  
    wmic nicconfig where IPEnabled='true' get Caption,DefaultIPGateway,Description,DHCPEnabled,DHCPServer,IPAddress,IPSubnet,MACAddress /format:"%var%" >> out.html   
    wmic volume get Label,DeviceID,DriveLetter,FileSystem,Capacity,FreeSpace /format:"%var%" >> out.html   
    wmic netuse list full /format:"%var%" >> out.html   
    wmic qfe get Caption,Description,HotFixID,InstalledOn /format:"%var%" >> out.html   
    wmic startup get Caption,Command,Location,User /format:"%var%" >> out.html   
    wmic PRODUCT get Description,InstallDate,InstallLocation,PackageCache,Vendor,Version/format:"%var%" >> out.html   
    wmic os get name,version,InstallDate,LastBootUpTime,LocalDateTime,Manufacturer,RegisteredUser,ServicePackMajorVersion,SystemDirectory /format:"%var%" >> out.html   
    wmic Timezone get DaylightName,Description,StandardName /format:"%var%" >> dayu.html

将该文本复制进txt，然后修改后缀为bat打开即可

执行完，打开out.html文件

![13](https://image.3001.net/images/20210722/1626931788_60f9024c61f96b89495f9.png!small)

![14](https://image.3001.net/images/20210722/1626931789_60f9024d1c7107f87be77.png!small)

![15](https://image.3001.net/images/20210722/1626931789_60f9024dca61944c98428.png!small)

![16](https://image.3001.net/images/20210722/1626931790_60f9024ea6074f0802b7c.png!small)

