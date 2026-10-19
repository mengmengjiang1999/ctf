![](https://image.3001.net/images/20191106/1573008579_5dc234c3bc00f.jpg!small)

**虽然Windows系统的安全机制是不允许任何微软签名的代码注入到进程之中的，但是网络犯罪分子仍然会有很多方法来绕过这种安全机制，比如说通过执行用户态钩子向正在运行的进程注入DLL等等。而本文所介绍的技术也许对于某些反病毒产品、EDR和安全防御人员来说，也许会提供一些有价值的思路。**

##  UpdateProcThreadAttribute

第一种防止恶意第三方DLL注入到进程的方法就是使用[UpdateProcThreadAttribute](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)，这个属性是PROC_THREAD_ATTRIBUTE_MITIGATION_POLICY中一个我们可以自行设置的属性。

下面的代码段显示了如何使用MITIGATION策略来创建一个新的记事本进程，而这个进程将阻止任意非微软签名的代码注入其中。编译并执行下列代码后，将以进程缓解策略执行notepad.exe程序，并防止任意非微软签名的代码注入其中。我们可以使用Process
Hacker来进行检查：

![](https://image.3001.net/images/20191106/1573008586_5dc234cad58ec.png!small)

在下面这张GIF中，MITIGATION策略已经生效，任何非微软签名的代码都将被屏蔽，但是其中有一段微软代码通过并成功执行了：

![](https://image.3001.net/images/20191106/1573009081_5dc236b9e4f51.gif!small)

值得一提的是，这种特性实际上是Cobalt Strike的blockdlls在“作怪”。

##  SetProcessMitigationPolicy

在研究第一种方法的过程中，我偶然发现了一个名叫SetProcessMitigationPolicy的API，这个API将允许我们针对调用进程本身设置缓解策略，而不是像第一种方法那样去为子进程设置缓解策略。mitigationpolicy.cpp的相关代码如下：

    
    
    PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY sp = {};
    
        sp.MicrosoftSignedOnly = 1;
    
        SetProcessMitigationPolicy(ProcessSignaturePolicy, &sp, sizeof(sp));

![](https://image.3001.net/images/20191106/1573008604_5dc234dc7b7bb.png!small)

在我的测试过程中，使用SetProcessMitigationPolicy并不能防止已知的EDR解决方案将其DLL注入到我们的进程中。通过调试会话的分析，我们确认了原因，即在注入DLL之后，缓解策略将会立刻被应用。当一个进程被初始化并且运行之后，任何非微软签名的代码都将无法注入到进程之中。

![](https://image.3001.net/images/20191106/1573009164_5dc2370c771c2.gif!small)

##  检测

这里我有一个更好的办法，就是使用PowerShell的一个“Get-ProcessMitigation”cmdlet命令来枚举出使用了MicrosoftSignedOnly缓解策略的进程，然后对其进行分析调查，并设置基准线：

    
    
    get-process | select -exp processname -Unique | % { Get-ProcessMitigation -ErrorAction SilentlyContinue -RunningProcesses $_ | select processname, Id, @{l="Block non-MS Binaries"; e={$_.BinarySignature|select -exp MicrosoftSignedOnly} } }

下图显示的是notepad.exe，它将允许微软签名的代码注入到其进程中：

![](https://image.3001.net/images/20191106/1573008844_5dc235cce8cce.png!small)

##  参考资料

> 1、<https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-> processthreadsapi-updateprocthreadattribute>
>
> 2、<https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-> processthreadsapi-setprocessmitigationpolicy>
>
> 3、<https://blog.cobaltstrike.com/2019/05/02/cobalt-strike-3-14-post-ex-> omakase-shimasu/>

 *** 参考来源：[ired](https://ired.team/offensive-security/defense-evasion/preventing-3rd-party-dlls-from-injecting-into-your-processes)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

