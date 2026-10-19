**作者: Yenn_  
原文链接: [Wei's Blog](https://0xdf1001f.github.io/2020/11/12/Turla-Kazuar-Backdoor/) **

## 简介

Turla，也被称为Venomous
Bear、Waterbug和Uroboros，是迄今为止最为高级的威胁组织之一，并被认为隶属于俄罗斯政府（该组织成员均说俄语）。虽然该组织被认为至少在2007年就已经成立，但直到2014年它才被卡巴斯基实验室发现。

## Kazuar

### Kazuar backdoor -e888b93f4d5f28699b29271a95ccad55ca937977d442228637ad9a7c037d3a6a4

#### 基本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
DebugView.exe | 137,728 Byte | BackDoor | 277f2d8e682f7ffc071560f44af4ab41  
  
#### 样本分析

##### 初始化

样本似乎伪造为Windows下的SysInternal套件

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-1uvggy.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101446.png)

样本内的类和函数命名都是由两位字符组成

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-2mamco.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101459.png)

设置样本中的异常处理，将异常发送到ThreadException

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-3ppzer.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101509.png)

通过字符串“”gGYJ\YwJ1sggs1YBg31GjGg14\dd0d}w}ds4””解密出一串GUID

“169739e7-2112-9514-6a61-d300c0fef02d”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-4nkmcf.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101539.png)

根据Gethostid返回的值与13取余，根据余数来决定在哪个文件夹释放创建新文件夹释放文件，在这里取到的路径为“C:\Users\sam\AppData\Local\Microsoft\Network\3DDC94D8”，得到路径后创建文件夹

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-5ncozc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101558.png)

获取计算机信息、解密加载出后续操作使用的内容，并通过前面解密出的”169739e7-2112-9514-6a61-d300c0fef02d”创建一个新GUID

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-6lqwlp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101608.png)

创建互斥量，互斥量都是由Username+固定字符串解密内容，根据UserName不同，生成的互斥量也不同，格式为Global\\+生成的与GUID同一格式的内容

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-7rzyaz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101620.png)

#####
[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-8keldc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101630.png)Rijndael加密

在文件夹“C:\Users\sam\AppData\Local\Microsoft\Network\3DDC94D8\3F515151”创建文件，写入程序运行的日志，写入的日志由Rijndael加密，KEY值由当前时间计算得出，通过KEY与文件的内容可以解密出样本的日志文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-9jrdvv.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101642.png)

加密：

[![img](https://images.seebug.org/content/images/2021/03/17/1615971617000-10cnvlp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101654.png)

##### 判断样本运行状态

判断样本运行状态，进行不同的操作，主入口点有4种不同的路径：

  1. 如果恶意软件是使用“ install”命令行参数执行的，则该参数使用.NET Framwork的InstallHelper方法将恶意软件作为服务安装。
  2. 如果恶意软件是在非用户交互环境（没有用户界面）中启动的，则该恶意软件会自己安装为服务。
  3. 如果未提供任何参数，并且恶意软件确定其在Windows环境中运行，则会将DLL注入到窗口“Shell_TrayWnd”中，执行DLL中的内容
  4. 如果恶意软件是使用“单个”命令行参数执行的，或者恶意软件确定其在Mac或Unix环境中运行，则它将运行包含Kazuar功能代码的方法。

##### 注入到explorer

调试过程中进入了流程3，样本先提权到SeDebugPrivilege权限

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-11cpbpo.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101705.png)

为Shell_TrayWnd窗口设置WindowsHook，注入DLL到explorer.exe中

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-12hwhzn.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101719.png)

注入后的explorer.exe

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-13kqisz.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101731.png)

##### CLR Runtime Loader

在explorer.exe中注入的DLL实际是一个CLR RUNTIME LOADER，负责加载执行先前样本中的内容

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-14xiupj.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101743.png)

类似样本中CLR Runtime Loader的源码，加载CLR Runtime到Target中执行

    
    
    __declspec(dllexport) HRESULT LoadDNA(_In_ LPCTSTR lpCommand) {
      HRESULT hr;
      ICLRMetaHost * pMetaHost = NULL;
      ICLRRuntimeInfo * pRuntimeInfo = NULL;
      ICLRRuntimeHost * pClrRuntimeHost = NULL;
      // Load .NET Runtime
      hr = CLRCreateInstance(CLSID_CLRMetaHost, IID_PPV_ARGS( & pMetaHost));
      hr = pMetaHost - >GetRuntime(L "v4.0.30319", IID_PPV_ARGS( & pRuntimeInfo));
      hr = pRuntimeInfo - >GetInterface(CLSID_CLRRuntimeHost, IID_PPV_ARGS( & pClrRuntimeHost));
      // Start Runtime
      hr = pClrRuntimeHost - >Start();
      // Parse Arguments
      ClrLoaderArgs args(lpCommand);
      // Execute Loaded .NET Code
      DWORD pReturnValue;
      hr = pClrRuntimeHost - >ExecuteInDefaultAppDomain(
          args.pwzAssemblyPath.c_str(), 
          args.pwzTypeName.c_str(), 
          args.pwzMethodName.c_str(), 
          args.pwzArgument.c_str(), 
          &pReturnValue);
      // Release and Free Resources
      pMetaHost - >Release();
      pRuntimeInfo - >Release();
      pClrRuntimeHost - >Release();
      // Return .NET Code Result
      return hr;
    }

加载完成后执行流程又回到了DbgView.exe中,调用了dbgview中的W.s()方法

设置异常处理

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-15smhlk.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101759.png)

##### 自启创建

查询当前的进程名是否为被注入的进程，可以看出程序会注入的程序包含“iexplore”,”firefox”,”browser”,”outlook”,”chrome”,”nlnotes”,”notes2”,”opera”,”msimn”

根据查询的结果会创建不同的线程

当注入的不是上述进程时：

与样本最开始相同会查询系统信息，然后尝试持久化操作，但在调试过程中创建自启动没有成功，返回字符串“DISABLE”，尝试的注册表路径

  * SOFTWARE\Microsoft\Windows\CurrentVersion\Run
  * SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
  * SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run
  * SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell
  * SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\load

或尝试添加自启动.lnk到启动目录

##### 远程连接

创建了一个IPC远程通道

“ipc://5728912222233c6860fe9a5a2ae45a7e/d22f298e18a16a3175ea1a78b5419c91”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-16pbnlq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101824.png)

从样本向日志中写入的内容来看，样本将C2下发的命令操作称为”Task”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-17ccvtl.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101836.png)

功能还带有注入到其他进程中的功能

当当前进程为“iexplore”,”firefox”,”browser”,”outlook”,”chrome”,”nlnotes”,”notes2”,”opera”,”msimn”时

尝试与C2链接，C2的地址由

“C:\Users\sam\AppData\Local\Microsoft\Network"下文件取出，当文件不存在时，样本还存在default
server

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-18dzubf.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101857.png)

解密出的两个Default Server:

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-19zqqes.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101905.png)

“<https://www.bombheros.com/wp-content/languages/index.php>"
“<https://www.simplifiedhomesales.com/wp-includes/images/index.php>"

与C2通信支持的协议类型包含”http”.”https”,”ftp”,”ftps”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-20mzwvi.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101934.png)

查询窗口，检测抓包软件，包括

“megadumper”,”smartsniff”,”snoopypro”,”wireshark”,”ethereal”,”tcpview”,”tcpdump”,”windump”,”portmon”,”dsniff”,

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-21fisjr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101945.png)

向C2发送HTTP请求,cookie字段为GUID的base64编码，用于标识被感染主机

[![img](https://images.seebug.org/content/images/2021/03/17/1615971618000-22qzpql.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127101959.png)

##### 命令执行

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-23cgzys.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102015.png)

**Action ID** | **Commands** | **Description**  
---|---|---  
**1** | log | Logs a specified debug message  
**2** | get | Upload files from a specified directory. It appears the actor
can specify which files to upload based on their modified, accessed and
created timestamps as well.  
**3** | put | Writes provided data (referred to as ‘payload’) to a specified
file on the system.  
**4** | cmd | Executes a specified command and writes the output to a
temporary file. The temporary file is uploaded to the C2 server  
**5** | sleep | Trojan sleeps for a specified time  
**6** | upgrade | Upgrades the Trojan by changing the current executable’s
file extension to “.old” and writing a newly provided executable in its place  
**7** | scrshot | Takes a screenshot of the entire visible screen. The
screenshot is saved to a specified filename or using a filename with the
following format:
[year]-[month]-[day]-[hour]-[minute]-[second]-[milisecond].jpg. The file is
uploaded to the C2 server  
**8** | camshot | Creates a Window called “WebCapt” to capture an image from
an attached webcam, which it copies to the clipboard and writes to a specified
file or a file following the same format from the “scrshot” command. The file
is uploaded to the C2 server  
**9** | uuid | Sets the unique agent identifier by providing a specific GUID  
**10** | interval | Sets the transport intervals, specifically the minimum and
maximum time intervals between C2 communications.  
**11** | server | Sets the C2 servers by providing a list of URLs  
**12** | transport | Sets the transport processes by providing a list of
processes that Kazuar will inject its code and execute within.  
**13** | autorun | Sets the autorun type as discussed earlier in this blog.
Kazuar will accept the following strings for this command: DISABLED, WINLOGON,
POLICIES, HKCURUN, RUNONCE, LOADKEY, STARTUP  
**14** | remote | Sets a remote type. We are only aware of one remote type
that instructs Kazuar to act as an HTTP server and allow the threat actor to
interact with the compromised system via inbound HTTP requests.  
**15** | info | Gathers system information, specifically information referred
to as: Agent information, System information, User information, Local groups
and members, Installed software, Special folders, Environment variables,
Network adapters, Active network connections, Logical drives, Running
processes and Opened windows  
**16** | copy | Copies a specified file to a specified location. Also allows
the C2 to supply a flag to overwrite the destination file if it already
exists.  
**17** | move | Moves a specified file to a specified location. Also allows
the C2 to supply a flag to delete the destination file if it exists.  
**18** | remove | Deletes a specified file. Allows the C2 to supply a flag to
securely delete a file by overwriting the file with random data before
deleting the file.  
**19** | finddir | Find a specified directory and list its files, including
the created and modified timestamps, the size and file path for each of the
files within the directory.  
**20** | kill | Kills a process by name or by process identifier (PID)  
**21** | tasklisk | List running processes. Uses a WMI query of “select * from
Win32_Process” for a Windows system, but can also running “ps -eo
comm,pid,ppid,user,start,tty,args” to obtain running processes from a Unix
system.  
**22** | suicide | We believe this command is meant to uninstall the Trojan,
but it is not currently implemented in the known samples.  
**23** | plugin | Installing plugin by loading a provided Assembly, saving it
to a file whose name is the MD5 hash of the Assembly’s name and calling a
method called “Start”.  
**24** | plugout | Removes a plugin based on the Assembly’s name.  
**25** | pluglist | Gets a list of plugins and if they are “working” or
“stopped”  
**26** | run | Runs a specified executable with supplied arguments and saves
its output to a temporary file. The temporary file is up loaded to the C2
server.  
  
##### IOC

“<https://www.bombheros.com/wp-content/languages/index.php>"
“<https://www.simplifiedhomesales.com/wp-includes/images/index.php>"

参考链接：

1.<https://www.accenture.com/us-en/blogs/cyber-defense/turla-belugasturgeon-compromises-government-entity>

2.<https://unit42.paloaltonetworks.com/unit42-kazuar-multiplatform-espionage-backdoor-api-access/>

3.<https://www.epicturla.com/blog/sysinturla>

### Kazuar - 1f7b35e90b5ddf6bfd110181b1b70487011ab29ca5f942170af7e8393a1da763

伪造为Windows下Sysinternas组件中的DebugView

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-24kcshp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102033.png)

流程与前面Kazuar backdoor -e888b93f4d5f28699b29271a95ccad55ca937977d442228637ad9a7c037d3a6a4相同，不过这次样本使用了ConfuserEX混淆字符串，通过工具可以直接解出明文，而前面样本中使用了自定义的加密方法，在使用字符串时通过解密。

通过工具反混淆后可直接查看明文字符串：

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-25nxmke.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102044.png)

同样通过在”Shell_TrayWnd”设置HOOK

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-26tcztd.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102055.png)

释放一个DLL文件在%appdata%..\Local\随机名目录下，释放的DLL同样是一个CLR Runtime Loader

在explorer.exe的进程中可以看见.NET Assemblies中CLR下的样本进程

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-27noatc.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102109.png)

释放出的DLL的混淆代码部分，干扰IDA的F5

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-28juygp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102136.png)

在Explorer.exe中加载MainClass中的EntryPoint

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-29wwvau.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102146.png)

判断是否注入在当前进程下：

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-30ixqph.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102157.png)

创建IPC通道

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-31xynel.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102208.png)

监听HTTP请求

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-32lneyd.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102221.png)

同样的命令执行，26条指令与前面相同

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-33dboio.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102232.png)

#### 总结

样本与Kazuar backdoor
-e888b93f4d5f28699b29271a95ccad55ca937977d442228637ad9a7c037d3a6a4手法一致，在混淆中使用了ConfuserEX，反混淆后可以直接显示明文字符串，在样本e888b93f4d5f28699b29271a95ccad55ca937977d442228637ad9a7c037d3a6a4中则使用了自定义的加密方法，将字符串隐藏。在C2链接过程中，样本并没有设置自己的Default
Server

### Kazuar - 1fca5f41211c800830c5f5c3e355d31a05e4c702401a61f11e25387e25eeb7fa

样本执行流程相同，不使用ConfuserEX混淆字符串，使用自定义的算法混淆，没有C2时使用样本自带的Default C2 Server

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-34qtnyi.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102321.png)

#### IOC

<https://afci-newsoft.fr/wp-content/stmoptimize/optimize.php>  
<https://aviatnetworks.com/wp-includes/images/index.php>  
<https://www.citiquartz.com/wp-includes/fonts/icons/>

## Carbon

### Carbon Installer - 493e5fae191950b901764868b065ddddffa4f4c9b4

97022ee2f998b4a94f0fc2

#### 基本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
| 611,328 Byte | Dropper | a6efd027b121347201a3de769389e6dd  
  
#### 样本分析

样本伪造为Windows系统文件，原始文件名为ESCEBIN.EXE，但是实际上确实一个DLL文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615971619000-35gqxpu.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102338.png)

通过调用RegOpenKey对

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Windows的访问来查询当前是否为管理员权限，当不是管理员的时候会格式化一串字符串“Why the fu*k
not?”，然后退出进程

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-36fivbb.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102358.png)

尝试遍历%Systemroot%\inf文件夹下所有.inf文件，查询键名“DestinationDirs”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-37ytjvx.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102411.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-38wtbkk.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102424.png)

判断Windows系统版本

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-39nwdeq.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102602.png)

格式化字符串

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-40xyenh.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102630.png)

遍历C:\Program Files下所有文件，尝试遍历“windowsapps”文件夹，当不存在时会生成一个随机数，从C:\Program
Files下随机取一个文件夹，然后进行创建文件的测试

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-41vykju.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102642.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-42qxpbb.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102655.png)

读取资源中类型为“BINRARY“，资源名称为“#203”的资源，解密后写入到前面进行写文件测试的文件夹

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-43hwgsk.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102708.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-44mhmmh.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102720.png)

修改写入文件的时间为前面获取的explorer的Last Write Time

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-45cnvcr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102734.png)

重复上面的操作，从资源中解密出3个DLL文件

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-46scgga.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102747.png)

创建一个名为“Alerter”的自启动服务

[![img](https://images.seebug.org/content/images/2021/03/17/1615971620000-47sleww.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102756.png)

查询注册表

“HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows
NT\CurrentVersion\Svchost下值“netsvcs”的数据，并用查询到的内容来对比创建的服务“Alerter”是否在其中

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-48wrxgf.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102811.png)

创建注册表“HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\Alerter\Parameters”，并添加三项注册表值，将ServiceDLL修改为%System32%下的alrsvc.dll，alrsvc.dll从资源“#161”中解密释放

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-49ofnvl.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102823.png)

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-50gqcwp.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102833.png)

修改了注册表HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\Alerter\Parameters的ServiceDLL的值为alrsvc.dll，所以在下次服务启动时，会加载起来释放出的alrsvc.dll

### alrsvc.dll

#### 加载调用

注册函数“Service”处理控制请求，创建新线程遍历”C:\Windows\INF\“下所有.inf文件

将前面Carbon Installer 释放的文件移动到文件夹”C:\Program Files\Reference
Assemblies\Microsoft\Framework\v3.0\RedistList”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-51ghtsb.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102848.png)

利用当前alrsvc.dll加载其中的sacril.dll，调用函数”OnDemandStart”

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-52lmwvu.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127102859.png)

释放出的四个文件，应该为Carbon主体、两个通讯模块DLL、一个配置文件。Carbon运行中从配置文件解密出配置信息，包括C2地址也在配置文件中。

### sacril.dll

sacril.dll为Carbon的主体文件

创建了大量的互斥体

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-53fgurr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127103128.png)

MUTEX |  
---|---  
Global\StopDeskIntel | Global\StickLowDrop  
Global\Open.Locked.Session.MBP | Global\NE_full_block_clone  
Global{5279C310-CA22-EAA1-FE49-C3A6A22AFC82} | Global\Central.Orchestrator.E  
Global\ViHyperCPrompt |  
  
在前阶段Drop文件的目录“C:\Program Files\Reference
Assemblies\Microsoft\Framework\v3.0\RedistList”下拼接出大量的路径

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-54jiylr.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127103144.png)

在新建的文件夹\1033下创建一个dbr4as.lte文件，在其中写入日志文件，写入后立马对日志文件进行加密

加密前：

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-55eogxo.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127103202.png)

加密后：

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-56xbjvt.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127103218.png)

#### 配置文件

在样本执行过程中会将配置文件解密，样本执行的操作都来自于配置文件estdlawf.fes。

  * 配置文件中包含object_id，用于识别受害者的唯一uuid
  * 注入代码的进程列表（ipproc）
  * 任务执行的频率和时间/日志备份呢/与C2链接的时间间隔（[TIME]）
  * 网络上其他计算机IP地址（[CW_LOCAL])
  * C2服务器地址([CW_INET])
  * 用于与其他计算机通信的命名管道（TRANSPORT）

Carbon解密后的的配置文件：

    
    
    [NAME]
    object_id=APCA1lABkYnaL4eoNL07VAAlmu
    iproc = iexplore.exe,outlook.exe,msimn.exe,firefox.exe,opera.exe,chrome.exe,browser.exe,nlnotes.exe,notes2.exe,spotify.exe,adobeupdater.exe,adobearm.exe,jusched.exe,thunderbird.exe
    ex = #,netscape.exe,mozilla.exe,adobeupdater.exe,chrome.exe
    
    
    [TIME]
    user_winmin = 2400000
    user_winmax = 3600000
    sys_winmin = 3600000
    sys_winmax = 3700000
    task_min = 20000
    task_max = 30000
    checkmin = 60000
    checkmax = 70000
    logmin =  60000
    logmax = 120000
    lastconnect=111
    timestop=
    active_con = 900000
    time2task=3600000
    
    
    [CW_LOCAL]
    quantity = 0
    
    [CW_INET]
    quantity = 2
    address1 = www.berlinguas.com:443:/wp-content/languages/index.php
    address2 = www.balletmaniacs.com:443:/wp-includes/fonts/icons/
    
    [TRANSPORT]
    system_pipe = suplexrpc
    spstatus = yes
    adaptable = no
    
    [RENDEZVOUS_POINT]
    quantity = 1
    address1 = pastebin.com:443:/raw/5qXBPmAZ
    
    [DHCP]
    server = 135
    
    
    [LOG]
    logperiod = 7200
    
    [WORKDATA]
    run_task=
    run_task_system=

其中可以清晰的发现PIPE名”suplexrpc”与三个地址

[www.berlinguas.com:443:/wp-content/languages/index.php](http://www.berlinguas.com:443/wp-content/languages/index.php)

[www.balletmaniacs.com:443:/wp-includes/fonts/icons/](http://www.balletmaniacs.com:443/wp-includes/fonts/icons/)

pastebin.com:443:/raw/5qXBPmAZ

#### 日志文件

Carbon还包含一个日志文件，日志的格式为日期|时间|受害者id|源|消息

    
    
    [LOG]
    start=1
    20/02/17|12:48:24|8hTdJtUBB57ieReZAOSgUYacts|s|OPER|New object ID generated '8hTdJtUBB57ieReZAOSgUYacts'|
    20/02/17|12:48:24|8hTdJtUBB57ieReZAOSgUYacts|s|ST|3/81|0|
    20/02/17|12:48:24|8hTdJtUBB57ieReZAOSgUYacts|s|START OK

#### 通信

Carabon可以与网络中其他计算机进行通信，下发任务。使用了几种类型的传输协议

TCP、b2m、np、frag、m2b

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-57grrxu.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127114042.png)

#### 更新

Carbon还为样本提供了持续更新的功能

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-58elwmk.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127141230.png)

#### 注入

尝试将同时释放出的另两个DLL文件注入到配置文件中的iproc配置项中

在目标进程中创建远线程调用LoadLibrary将DLL加载到目标进程中

[![img](https://images.seebug.org/content/images/2021/03/17/1615971621000-59ducsl.png-w331s)](https://cdn.jsdelivr.net/gh/0xdf1001f/cdn@master/20201127111948.png)

解密Carbon文件：（来自ESET）

    
    
    #!/usr/bin/env python2
    
    from Crypto.Cipher import CAST
    import sys
    import argparse
    
    
    def main():
    
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-e", "--encrypt", help="encrypt carbon file", required=False)
        parser.add_argument("-d", "--decrypt", help="decrypt carbon file", required=False)
    
        try:
            args = parser.parse_args()
        except IOError as e:
            parser.error(e)
            return 0
    
        if len(sys.argv) != 3:
            parser.print_help()
            return 0
    
        key = "\x12\x34\x56\x78\x9A\xBC\xDE\xF0\xFE\xFC\xBA\x98\x76\x54\x32\x10"
        iv = "\x12\x34\x56\x78\x9A\xBC\xDE\xF0"
    
        cipher = CAST.new(key, CAST.MODE_OFB, iv)
    
        if args.encrypt:
            plaintext = open(args.encrypt, "rb").read()
            while len(plaintext) % 8 != 0:
                plaintext += "\x00"
            data = cipher.encrypt(plaintext)
            open(args.encrypt + "_encrypted", "wb").write(data)
        else:
            ciphertext = open(args.decrypt, "rb").read()
            while len(ciphertext) % 8 != 0:
                ciphertext += "\x00"
            data = cipher.decrypt(ciphertext)
            open(args.decrypt + "_decrypted", "wb").write(data)
    
    if __name__ == "__main__":
        main()

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1516/>

