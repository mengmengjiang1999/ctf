**严正声明：本文仅用于教育和讨论目的，请勿用于非法用途。**

## 前言

**受限语言模式是PowerShell限制用户访问高级功能的一种方式，暂且不管微软怎么说的，这个功能本质上是一种安全控制措施，很多防御者可以利用这种功能来阻止类似“Invoke-Mimikatz”这样的工具。**

不管微软方面是怎么看待的，这个功能目前已经被大家当做一种安全控制功能了，因为它可以帮助防御人员阻止类似“Invoke-Mimikatz”这样的工具运行。在这篇文章中，我将告诉大家如何以非管理员用户的身份绕过这种保护机制。

![PowerShell](https://image.3001.net/images/20181121/1542803710_5bf550fe6319c.png!small)

## 直奔主题

我们首先要做的就是在我们的实验环境中启用AppLocker。这篇文章中，在启用脚本限时时，我将使用Windows分配的默认角色。开启了应用程序识别服务之后，我们就可以使用下列命令来确保CLM已成功启用：

    
    
    $ExecutionContext.SessionState.LanguageMode

这里我们可以看到程序返回的值，这表明我们已经处于受限环境了。我们还可以在PowerShell中尝试执行受限命令来二次确认：

    
    
    Add-Type"namespace test { }"

![二次确认](https://image.3001.net/images/20181121/1542803732_5bf5511459c26.png!small)

既然我们已经启用了CLM，那我们应该怎么绕过它呢？

## AppLockerCLM中的New-Object

有趣的是，当我在寻找CLM的攻击面时，我发现当CLM通过AppLocker启用时，会出现一个New-Object，大家看看下面这条命令：

    
    
    New-Object-ComObject WScript.Shell

这样一来，我们好像就可以直接在PowerShell里面修改PowerShell进程了，因为COM对象通过DLL暴露在外，并且能够直接被加载到调用进程中。那么我们如何才能创建一个待加载的COM对象呢？如果我们查看ProcMon调用New-Object -ComObject xpntest的过程，我们就可以看到大量针对HKEY_CURRENT_USER注册表项的请求：

![3.png](https://image.3001.net/images/20181121/1542803753_5bf55129c8580.png!small)

研究了半天之后，我们发现，我们可以在下面这段脚本的帮助下直接在HKCU中创建所需要的注册表键：

![4.png](https://image.3001.net/images/20181121/1542803760_5bf5513047b54.png!small)

现在，如果我们尝试加载我们自己的COM对象，我们会发现自定义的DLL会被加载到PowerShell进程空间中：

![5.png](https://image.3001.net/images/20181121/1542803771_5bf5513b6da46.png!small)![6.png](https://image.3001.net/images/20181121/1542803771_5bf5513b7e92a.png!small)

这就很棒了，现在我们已经可以向PowerShell中注入任意DLL了，无需调用动作太大的CreateRemoteThread或者WriteProcessMemory，而且所有操作都是在受限场景下实现的。但我们的目标是绕过CLM，如何利用我们的非托管DLL加载方式来实现？我们可以利用.NET
CLR，或者更确切一点，我们可以通过非托管DLL加载.NET CLR来调用.NET 工具。

## 非托管DLL->托管DLL->反射

现在我们可以使用Cobalt Strike这样的工具，这款工具提供了Execute-Assembly功能，可以将CLR加载到非托管进程中，我在[GIST](https://gist.githubusercontent.com/xpn/e95a62c6afcf06ede52568fcd8187cc2/raw/f3498245c8309d44af38502a2cc7090c318e8adf/clr_via_native.c)上给大家提供了一份代码，它可以独立完成这个任务：

![7.png](https://image.3001.net/images/20181121/1542803796_5bf551542988e.png!small)

这里我就不详细介绍代码内容了，感兴趣的同学可以参考微软给出的【官方示例】，这段代码可以让DLL加载.NET
CLR，并加载.NET工具，最后将执行权限转移给特定的方法。

完成之后，我们就可以访问.NET了，重要的是，我们可以访问的是.NET的反射功能，接下来我们要做的就是如何启用/禁用CLM了。

System.Management.Automation.Runspaces.RunspaceBase.LanguageMode属性中有一个地方可以识别当前的语言模式。由于我们要使用反射技术，因此需要找到引用Runspace的变量，然后在运行时修改该变量。我觉得[最好的实现方法](https://gist.githubusercontent.com/xpn/e95a62c6afcf06ede52568fcd8187cc2/raw/f3498245c8309d44af38502a2cc7090c318e8adf/clr_via_native.c)就是利用Runspaces.Runspace.DefaultRunspace.SessionStateProxy.LanguageMode：

![8.png](https://image.3001.net/images/20181121/1542803808_5bf551604e6e6.png!small)

编译为.NET工具之后，我们就可以利用反射的方式来禁用CLM了，这里我们只需要创建并运行一个PowerShell脚本【[下载地址](https://gist.githubusercontent.com/xpn/1e9e879fab3e9ebfd236f5e4fdcfb7f1/raw/ceb39a9d5b0402f98e8d3d9723b0bd19a84ac23e/COM_to_registry.ps1)】即可：

![9.png](https://image.3001.net/images/20181121/1542803819_5bf5516b0b2e7.png!small)

这样就搞定啦！

## 演示视频

## 攻击原理

为什么COM可以绕过这种保护机制？PowerShell又是如何处理COM加载的呢？我们可以在SystemPolicy.IsClassInApprovedList方法中找到答案，这个方法可以用来检查程序是否允许我们向New-Object提供CLSID。下面这段代码负责的是核心检测功能：

if(SystemPolicy.WldpNativeMethods.WldpIsClassInApprovedList(ref clsid,
refwldp_HOST_INFORMATION, ref num, 0u) >= 0 && num == 1) { ... }

这个函数调用只是WldpIsClassInApprovedList函数（位于wldp.dll中）的一个封装函数，而后者主要用来检查CLSID是否匹配DeviceGuard（现已更名为Windows
Defender Application Control）策略。由于该方法没有考虑到AppLocker，这意味着任何通过检查的CLSID都可以使用。

## 意外发现

在测试这项技术的过程中，我遇到过一次奇怪的情况，当我们使用如下方法设置CLM时，这项技术就无法正常使用了：

    
    
    $ExecutionContext.SessionState.LanguageMode= "ConstrainedLanguage"

这就很尴尬了，因为之前我都是使用上述命令来测试Payload的，现在有什么区别吗？重新检查了我们的反汇编代码之后，我在Microsoft.Powershell.Commands.Utility.dll那里找到了问题的答案。这个文件的具体路径位于NewObjectCommand类的BeginProcessing方法中：

![aaaaaaaaa.png](https://image.3001.net/images/20181123/1542963012_5bf7bf442208e.png!small)

这里我们可以看到上述的代码中存在两条代码路径，具体使用哪一条取决于CLM的启用方式。如果SystemPolicy.GetSystemLockdownPolicy返回的是Enfore，即执行第一条路径，此时的AppLocker或者DeviceGuard将被启用。如果直接设置这个参数，则会直接进入if
(!flag)…代码段，此时就会抛出异常。实际上，CLM会根据具体的启用方法（是通过AppLocker、DeviceGuard，还是通过LanguageMode属性来启用）而有不同的行为。

本文介绍的方法并不是绕过CLM的唯一方法，即使粗略分析PowerShell，我们也能找到实现类似效果的其他方法。如果大家对这个topic感兴趣的话，可以看看Oddvar
Moe在Debycon大会上的演讲【[传送门](https://docs.google.com/spreadsheets/d/1XCKWHuXrVNcmmL1HsXklMT9ati8WSxGZkV_79Jh7gqA/edit#gid=1460396465)】。

 ***参考来源：[mdsec](https://www.mdsec.co.uk/2018/09/applocker-clm-bypass-via-com/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

