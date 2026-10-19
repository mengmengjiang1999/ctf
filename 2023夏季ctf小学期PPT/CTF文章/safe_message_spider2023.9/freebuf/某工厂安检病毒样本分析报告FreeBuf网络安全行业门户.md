# **一、事件概述**

近期，我公司员工在某工厂安全检查时发现了此病毒样本，由于客户安装的杀软没有识别此样本为恶意代码，但其他安全软件对此样本有响应，所以应客户要求，六方云超弦攻防实验室对此病毒进行收集资料，应急响应分析。

#  **二、影响面和危害分析**

经分析是一个远控木马，类型为Win32/RiskWare.RemoteAdmin.RemoteExec.AC
application，攻击者通过木马连接木马服务器所在的172.217.4.78，可以控制被控者的主机，监控被控主机，窃取被控主机的信息。

远控病毒是一个常见的并且危害比较大的病毒分类，这类病毒从早年的灰鸽子，到如今的黑暗幽灵（DCM）等种类繁多，利用技术也是从传统白加黑，到rootkit等五花八门，病毒作者可以通过远控木马，实现对受害者电脑的控制，监控受害用户的主机，窃取用户信息，让被控主机按照病毒作者的意愿做一些恶意操作，如实现传播病毒。如果再利用上一些比较严重的漏洞，如永恒之蓝，最近的CVE-2019-0708等的话就可以干任何坏事，可以在被控计算机完全不知情的情况下窃取任何资料，把远程计算机配置成代理服务器，以此为跳板再去攻击其他计算机。

#  **三、解决方案及检测与防护建议**

平时注意安装运行安全防护软件，定期及时更新病毒库，以免使电脑受到恶意程序的危害。如果发现自己中毒，使用能查杀此病毒的杀毒引擎，如下图，或者使用根据MD5来清理文件的工具，

![image.png](https://6cloudtech.com/upload/default/20190911/544a56d76f582408e1ec231fc3caf906.png)

针对此类病毒，也可以根据MD5，清理匹配的文件，下面是清理SystemRoot路径下此MD5的脚本代码。

function Get-md5 {

Param($path)

if(Test-Path $path -PathType Leaf ){

$md5file=certutil -hashfile "$path" MD5

[string]$hash=$md5file -match "^[a-f0-9]{32}$"

$retVal = New-Object -TypeName psobject -Property @{

Path = $path

Hash = $hash.ToUpper()

}

$retVal

}else{

}

}

[array]$md5=Get-ChildItem $env:SystemRoot -ErrorAction 0 -Force -recurse
-Filter *.exe | % {Get-md5 $_.FullName}

$md5 | where {($_.Hash -eq "6983F7001DE10F4D19FC2D794C3EB534")} | %{write-host
$_Path}

[array]$md5=@()

#  **四、事件分析**

拿到样本后，为了方便分析，去除随机基址，首先PEID扫描此文件, 根据PEID扫描结果查壳，去壳再查看

![image.png](https://6cloudtech.com/upload/default/20190911/e73ee57a34c9664f32b2ab1838e15f9d.png)

发现连接器版本9.0，是VS2008编写。然后进行分析病毒。

![image.png](https://6cloudtech.com/upload/default/20190911/73ef8b55fa293bf9ac8e289855f1b9b1.png)

根据IDA分析，病毒通过sub_4010F0(&v7)

![image.png](https://6cloudtech.com/upload/default/20190911/7566696ec550ee94e2cca5a410abc88d.png)

病毒通过此函数提高自己的执行权限，达到管理员模式。

然后通过调用StartServiceCtrlDispatcher函数，执行线程。

![image.png](https://6cloudtech.com/upload/default/20190911/5a081d43245d0db788c29e4144d761e6.png)

分析该服务线程可以看出首先通过函数RegisterServiceCtrlHandlerA注册了一个服务控制函数，然后通过SetServiceStatus设置服务从beginning变成running，然后设置一个事件，开始为无信号状态，开启一个线程，回调函数是sub_401830,继续跟踪。

![image.png](https://6cloudtech.com/upload/default/20190911/3b5b5519466c67c3bc5e228b93ff3d83.png)

发现这里是又创建了一个线程，然后设置等待事件，然后执行sub_401000函数，猜测这里是一些清理函数，先分析此函数。  

![image.png](https://6cloudtech.com/upload/default/20190911/6b7d88d1a8fe468345e36c87d53133a7.png)

发现果真就是打开服务管理器，然后打开“RemComSvc”服务，然后删除这个服务，然后运行SetServiceStatus，设置此服务的状态为SERVICE_STOPPED。

然后我们再去看这里创建的线程的回调sub_4017A0.

![image.png](https://6cloudtech.com/upload/default/20190911/4a05ef16d8ccaf01a9b742e09f634d0e.png)

发现这里就是创建安全描述符，然后创建一个命名的双通管道，名字是[\\\\.\pipe\RemCom_communicaton](https://6cloudtech.com/upload/file://pipe/RemCom_communicaton)，然后连接此管道，开启新线程。

分析下新线程的回调函数sub_4016D0

![image.png](https://6cloudtech.com/upload/default/20190911/881316bbc98212fc6c4c9794b750efff.png)

发现就是进行原子操作，读取文件，0x1214大小，然后执行sub_4015A0,然后再写入了文件。

![image.png](https://6cloudtech.com/upload/default/20190911/3662b1ade2069af07da8ab957f8cff67.png)

发现就创建了启动项，调用了函数

![image.png](https://6cloudtech.com/upload/default/20190911/81854145bdef48cf5ca17b7c06621440.png)

发现是在创建输入输出以及错误信息的管道。然后创建了进程，我们可以通过沙箱或者行为监测软件分析做了什么操作。可以看到，进程中进行恶意操作，如联网172.217.4.78：80/
23.49.13.56: 80操作，猜测就是远控的服务器端所在。

![image.png](https://6cloudtech.com/upload/default/20190911/cc188cce67e36c27dca9b4c748194dd7.png)

除此之外，还有实现rpc连接。

####  **其他功能分析**

这个样本有反调试手段比如：首先他有个虚拟机检测

![image.png](https://6cloudtech.com/upload/default/20190911/9a78532782057b18136a62c5532be327.png)

关于系统查询信息结构体MEMORYSTATUSEX写在此处。

![image.png](https://6cloudtech.com/upload/default/20190911/976c7010d2265613d020bb51c4e50177.png)

通过函数GlobalMemoryStatusEx检测运行机器内存大小，还有系统其他属性，检测是否处于在虚拟机运行的状态

此外，使用检测函数IsDebuggerPresent函数，设置异常处理程序的函数来用来反调试。

![image.png](https://6cloudtech.com/upload/default/20190911/2bcc6deef0d679ab7af437c6982c2bcc.png)

用来对抗动态分析

此外通过沙箱分析

经过行为分析，他的相关行为有

读取活动计算机名称

HKLM\SYSTEM\CONTROLSET001\CONTROL \ COMPUTERNAME \ ACTIVECOMPUTERNAME

HKLM \ SOFTWARE \ MICROSOFT \ CRYPTOGRAPHY

读取加密机器GUID

HKLM \ SOFTWARE \ MICROSOFT \ CRYPTOGRAPHY

此外在HTTP出口发送流量

TCP traffic to 172.217.4.78：80

TCP traffic to 23.49.13.56：80

导入了可疑的API

OpenProcessToken

SetSecurityDescriptorDacl

StartServiceCtrlDispatcherA

LoadLibraryA

GetModuleFileNameA

OpenProcess

UnhandledExceptionFilter

GetCommandLineA

GetProcAddress

CreateThread

DisconnectNamedPipe

WriteFile

GetStartupInfoA

ExitThread

GetModuleHandleW

IsDebuggerPresent

TerminateProcess

ConnectNamedPipe

CreateProcessA

Sleep

CreateFileA

GetTickCount

VirtualAlloc

往NSI.DLL下钩子

反动态调试

反虚拟机

通过GlobalMemoryStatusEx

此外还创建了系统服务

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "PERFINIFILE";
Value: "WmiApRpl.ini")

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "LAST
COUNTER"; Value: "A0210000")

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "LAST HELP";
Value: "A1210000")

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "FIRST
COUNTER"; Value: "FA200000")

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "FIRST HELP";
Value: "FB200000")

"WMIADAP.exe" (Access type: "SETVAL"; Path:
"HKLM\SYSTEM\CONTROLSET001\SERVICES\WMIAPRPL\PERFORMANCE"; Key: "OBJECT LIST";
Value: "8442 8448 8458 8468 8488 8532 8542 8580 8586 8602")

也验证了前面的分析结果。

#  **五、参考链接**

1\.
<https://www.virustotal.com/gui/file/3c2fe308c0a563e06263bbacf793bbe9b2259d795fcc36b953793a7e499e7f71/details>

2\.
<https://s.threatbook.cn/report/file/3c2fe308c0a563e06263bbacf793bbe9b2259d795fcc36b953793a7e499e7f71/?env=win7_sp1_enx64_office2013>

# **六、IOCs**

172.217.4.78：80

23.49.13.56

MD5

[6983f7001de10f4d19fc2d794c3eb534](https://6cloudtech.com/portal/admin_article/edit/id/179.html)

