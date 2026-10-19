![](https://image.3001.net/images/20220105/1641352788_61d50e5423b1991a00e67.png!small)

## 关于DLLHijackingScanner

DLLHijackingScanner是一款功能强大的DLL劫持漏洞和受信目录利用检测工具，该工具本质上来说是一个PoC概念验证，可以帮助研究人员通过DLL劫持技术绕过[
_UAC_](https://docs.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works)，来检测目标设备是否容易受到[
_DLL劫持_](https://attack.mitre.org/techniques/T1574/001/)。除此之外，该工具还支持检测针对“受信任目录”的验证滥用。

## 工具下载

该工具基于Python开发，因此我们首先需要在主机环境中安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/SecuProject/DLLHijackingScanner.git

## 从CSV生成Header

项目提供的Python脚本-CsvToHeader.py可以用来生成一个Header文件，该工具默认将使用[
_dll_hijacking_candidates.csv_](https://raw.githubusercontent.com/wietze/windows-dll-hijacking/master/dll_hijacking_candidates.csv)。

 **脚本将会检测每一个PE的下列状态：**

1、PE是否存在于文件系统；

2、在PE的manifest中，requestedExecutionLevel是否被设置为了下列其中一个值：

    
    
    asInvoker
    
    highestAvailable
    
    requireAdministrator

3、manifest中autoElevate的值是否被设置为了true：

    
    
    <autoElevate>true</autoElevate>

4、用户是否设置了-c参数，脚本将会检测PE表中导入的DLL是否存在DLL劫持；

## 工具参数

    
    
    > python .\CsvToHeader.py -h
    
    usage: CsvToHeader.py -f [DLL_PATH] -c
    
     
    
    CsvToHeader can be used to generate a header file from a CSV.
    
     
    
    optional arguments:
    
      -h, --help      show this help message and exit
    
      -f  [DLL_PATH]  Path of the csv to convert (default="dll_hijacking_candidates.csv")
    
      -c              Enable import dll in PE (default=False)
    
      -v, --version   Show program's version number and exit

我们可以使用下列命令可以生成Header文件：

    
    
    python CsvToHeader.py > dll_hijacking_candidates.h

## 生成存在漏洞的PE和DLL

这个过程需要使用到的文件为DLLHijacking.exe和test.dll。

### DLLHijacking.exe

DLLHijacking.exe用于生成存在漏洞的PE列表，它将会执行下列操作：

1、在C:\windows \system32目录下创建伪造的目录；

2、向新创建的目录中拷贝文件：

    
    
    C:\windows\system32\[TARGET.EXE] -> C:\windows \system32\[TARGET.EXE]
    
    [CUSTOM_DLL_PATH] -> C:\windows \system32\[TARGET.DLL]

3、触发器：通过C:\windows \system32\\[TARGET.EXE]运行可执行文件；

4、清除伪造的目录：删除第一步创建的目录和第二步创建的文件；

5、检查漏洞利用：检查C:\ProgramData\exploit.txt的文件内容，并查看漏洞利用是否成功。

### 日志文件

DLLHijacking.exe将使用下列内容生成exploitable.log日志文件：

1、0或1代表漏洞利用（绕过UAC）是否成功。

2、可执行程序名称。

3、DLL文件名，例如：

    
    
    1,computerdefaults.exe,PROPSYS.dll
    
    0,computerdefaults.exe,Secur*32.dll

### DLLHijacking.exe执行

    
    
    DLLHijacking.exe [DLL_PATH]

如果没有指定参数，脚本将直接使用test.dll。

### 运行结果

测试平台为Windows 10专业版（10.0.19043 N/A Build 19043）：

![](https://image.3001.net/images/20220105/1641354213_61d513e53c058bb479ee0.png!small)

### test.dll

test.dll是一个简单的动态库，可以用来判断漏洞利用是否成功。DLL将使用下列内容来创建C:\ProgramData\exploit.txt文件：

> 1、0或1代表漏洞利用（绕过UAC）是否成功。
>
> 2、可执行程序名称。
>
> 3、DLL文件名。

这个文件将会在漏洞利用成功后被删除。

## 项目地址

 **DLLHijackingScanner：** 【[
_GitHub传送门_](https://github.com/SecuProject/DLLHijackingScanner)】

## 参考资料

> [ _https://www.wietzebeukema.nl/blog/hijacking-dlls-in-> windows_](https://www.wietzebeukema.nl/blog/hijacking-dlls-in-windows)
>
> [ _https://github.com/wietze/windows-dll-> hijacking/_](https://github.com/wietze/windows-dll-hijacking/)
>
> [ _https://github.com/wietze/windows-dll-> hijacking/blob/master/dll_hijacking_candidates.csv_](https://github.com/wietze/windows-> dll-hijacking/blob/master/dll_hijacking_candidates.csv)
>
> [ _https://medium.com/tenable-techblog/uac-bypass-by-mocking-trusted-> directories-24a96675f6e_](https://medium.com/tenable-techblog/uac-bypass-by-> mocking-trusted-directories-24a96675f6e)

