**SharPyShell是一个用于C＃Web应用程序的小型混淆版ASP.NET
webshell，执行由加密信道接收的命令，并在运行时将它们编译到内存中。**

 **![](https://image.3001.net/images/20190315/1552627264292.png!small)**

SharPyShell仅支持在.NET Framework >= 2.0上运行的C＃Web应用程序。当前不支持VB。

## 使用

    
    
    python SharPyShell.py generate -p somepassword
    python SharPyShell.py interact -u http://target.url/sharpyshell.aspx -p somepassword

## 安装条件

Python version >= 2.7

以及

    
    
    pip install -r requirements.txt

## 简介

SharPyShell是一个由Python编写的后渗透框架，它能够：

> 生成混淆的webshell（generate）;
>
> 模拟Windows终端作为webshell的交互（interact）。

该框架的主要目的是为渗透测试人员提供一系列工具，以便在对 IIS webserver成功利用后简化后期利用阶段。

此工具不能替代C2
Server的框架（如Meterpreter，Empire等），但它非常适用于入站和出站连接完全受限的服务器环境。它包含了你在目标服务器cmd中将可能用到的所有有关privesc，netdiscovery以及横向渗透的工具。

除此之外，该框架还旨在尽可能做到隐蔽的在内存中执行c＃代码和powershell模块。

SharPyShell中实现的混淆，旨在躲避文件签名和网络签名检测。对于网络签名检测的躲避，已经开发了用于发送命令和接收输出的完全加密的信道。

通过对负责运行时编译c#代码的预编译DLL进行反射，可以躲避文件签名检测。

## 技术实现流程图

以下流程图是使用asciiflow.com生成的：

    
    
    +-------------------------------------------+                      +--------------------------------------------+
    | SharPyShell Client (Local)                |                      | Target Server (Remote)                     |
    +-------------------------------------------+   +--------------+   +--------------------------------------------+
    |                                           |   |  Encrypted   |   |                                            |
    |   +--------+-----------------^-----------<---->     HTTP     <---->-----------+-----------------^--------+    |
    |            |                 |            |   |   Channel    |   |            |                 |             |
    |            |4-Receive        |1-Send      |   +--------------+   |            |2-Receive        |3-Send       |
    |            |                 |            |                      |            |                 |             |
    |   +--------v-----------------+--------+   |                      |   +--------v-----------------+--------+    |
    |   |              Module               |   |                      |   |           Webshell URL            |    |
    |   +--------+-----------------^--------+   |                      |   +--------+-----------------^--------+    |
    |   |        |Parse            |Generate|   |                      |   |        |Parse            |Generate|    |
    |   | +------v------+   +------+------+ |   |                      |   | +------v------+   +------+------+ |    |
    |   | |Base64 Resp  |   |Base64 Req   | |   |                      |   | |Base64 Req   |   |Base64 Resp  | |    |
    |   | +------+------+   +------^------+ |   |                      |   | +------+------+   +------^------+ |    |
    |   |        |Decode           |Encode  |   |                      |   |        |Decode           |Encode  |    |
    |   | +------v------+   +------+------+ |   |                      |   | +------v------+   +------+------+ |    |
    |   | |Xor/Aes Data |   |Xor/Aes Data | |   |                      |   | |Xor/Aes Data |   |Xor/Aes Data | |    |
    |   | +------+------+   +------^------+ |   |                      |   | +------+------+   +------^------+ |    |
    |   |        |Decrypt          |Encrypt |   |                      |   |        |Decrypt          |Encrypt |    |
    |   | +------v------+   +------+------+ |   |                      |   | +------v------+   +------+------+ |    |
    |   | |Response     |   |C# Code      | |   |                      |   | |C# Code      |   |Output       | |    |
    |   | +------+------+   +------+------+ |   |                      |   | +------+------+   +------+------+ |    |
    |   |        |                 ^        |   |                      |   |        |                 ^        |    |
    |   |        v                 |        |   |                      |   |        v                 |        |    |
    |   |        +--------+--------+        |   |                      |   |        +--------+--------+        |    |
    |   |                 |                 |   |                      |   |                 |                 |    |
    |   +---------------- ^ ----------------+   |                      |   +---------------- ^ ----------------+    |
    |                     |                     |                      |                     |                      |
    |                     |Run&Parse            |                      |                     |Compile&Run           |
    |                     |                     |                      |                     |                      |
    |             +------ v ------+             |                      |             +------ v ------+              |
    |             |Terminal       |             |                      |             |csc.exe        |              |
    |             +---------------+             |                      |             +---------------+              |
    |             |Modules:       |             |                      |             |System.dll     |              |
    |             |#exec_cmd      |             |                      |             |Compile in Mem |              |
    |             |#exec_ps       |             |                      |             |No exe output  |              |
    |             |#runas         |             |                      |             |               |              |
    |             |.....          |             |                      |             |               |              |
    |             |               |             |                      |             |               |              |
    |             +---------------+             |                      |             +---------------+              |
    |                                           |                      |                                            |
    +-------------------------------------------+                      +--------------------------------------------+

## 模块

    
    
    #download              从服务器下载文件                                      
    #exec_cmd              在服务器上运行cmd.exe /c命令                                
    #exec_ps               在服务器上运行powershell.exe -nop -noni -enc'base64command'    
    #invoke_ps_module      在目标服务器上运行ps1脚本                                 
    #invoke_ps_module_as   以特定用户身份在目标服务器上运行ps1脚本              
    #lateral_psexec        运行psexec二进制文件（横向渗透）                                   
    #lateral_wmi           运行内置WMI命令（横向渗透）                            
    #mimikatz              直接在内存中运行mimikatz的离线版本                 
    #net_portscan          使用常规套接字运行端口扫描 
    #privesc_juicy_potato  发起Juicy Potato攻击，冒充NT AUTHORITY\SYSTEM用户 
    #privesc_powerup       运行Powerup模块评估privesc的所有错误配置         
    #runas                 运行cmd.exe /c命令，以特定用户的身份生成新进程    
    #runas_ps              运行powershell.exe -enc以特定用户形式生成新进程  
    #upload                将文件上传到服务器  

## 已测试的 Windows 版本

Windows Server 2019 Standard

    
    
    系统名称：Microsoft Windows Server 2019 Standard Evaluation
    
    系统版本：10.0.17763 N/A Build 17763

Windows Server 2016 Standard

    
    
    系统名称：Microsoft Windows Server 2016 Standard Evaluation
    
    系统版本：10.0.14393 N/A Build 14393

Windows Server 2012 R2 Standard

    
    
    系统名称：Microsoft Windows Server 2012 R2 Standard
    
    系统版本：6.3.9600 N/A Build 9600

Windows server 2012 Standard

    
    
    系统名称：Microsoft Windows Server 2012 Standard Evaluation
    
    系统版本：6.2.9200 N/A Build 9200

Windows Server 2008 R2 Standard

    
    
    系统名称：Microsoft Windows Server 2008 R2 Standard
    
    系统版本：6.1.7601 Service Pack 1 Build 7601

Windows Server 2008 Standard x64

    
    
    系统名称：Microsoft© Windows Server© 2008 Standard
    
    系统版本：6.0.6001 Service Pack 1 Build 6001

Windows Server 2003 Standard x64 (部分工作)

    
    
    系统名称：Microsoft(R) Windows(R) Server 2003 Standard x64 Edition
    
    系统版本：5.2.3790 Service Pack 2 Build 3790

*参考来源：[GitHub](https://github.com/antonioCoco/SharPyShell/blob/master/SharPyShell.py)，FB小编secist编译，转载请注明来自FreeBuf.COM   

