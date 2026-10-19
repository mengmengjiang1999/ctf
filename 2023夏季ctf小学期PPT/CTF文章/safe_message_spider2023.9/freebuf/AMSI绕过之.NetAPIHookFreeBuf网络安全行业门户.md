![](https://image.3001.net/images/20230508/1683513631_6458611fc6057f2b69c5a.jpg!small)

## 简介

反恶意软件扫描接口 (AMSI) 是对动态恶意脚本执行进行深入检查的 Microsoft Windows 组件。AMSI
可以被不同的防病毒软件调用，提供对PowerShell 脚本、JavaScript 和 VBA 宏等恶意脚本的扫描。Practical Security
Analytics提出了一种通过Hook .Net Api绕过AMSI的新技术，本文主要对此技术进行分析与复现。

## 0x01 背景

反恶意软件扫描接口 (AMSI) 的开发旨在为 Windows
环境中执行恶意脚本提供安全防护支持。目前，主流对抗AMSI的技术主要有编码混淆、内存补丁、强制AMSI初始化失败、amsi.dll劫持、修改注册表项等。其中，内存补丁通过Hook
windows API AmsiScanBuffer()
函数，使其始终返回AMSI_RESULT_CLEAN值以达到绕过的目的。而目前Hook的实现多针对于asmi.dl中的AmsiScanBuffer函数，实际上，powershell是.Net程序集，在执行命令或脚本之前，powershell会调用AmsiUtils.ScanCotent静态方法，该方法将命令发送到amsi接口进行检查，如下图所示。AmsiUtils是一个内部类，位于System.Management.Automation.dll中。如果修补ScanCotent方法，就可以阻止对amsi.dll中
AmsiScanBuffer 的调用，从而实现asmi绕过。

    
    
    AmsiUtils.AmsiNativeMethods.AMSI_RESULT result = AmsiUtils.AmsiNativeMethods.AMSI_RESULT.AMSI_RESULT_CLEAN;
    fixed (char* chPtr = content) {
        IntPtr buffer = new IntPtr((void*)chPtr);
        hresult = AmsiUtils.AmsiNativeMethods.AmsiScanBuffer(AmsiUtils.amsiContext, buffer, (uint)(content.Length * 2), sourceMetadata, AmsiUtils.amsiSession, ref result);
    }  
    

## 0x02 技术分析

该技术的核心是Hook .Net API。由于.Net程序集运行在CLR环境中，因此.Net API Hook 与常规windows API
Hook不一样。

.Net API Hook 的步骤有6步:

1、确定要hook的目标函数

2、定义具有相同函数签名的函数

3、利用反射找到函数

4、编译目标函数和自定义函数

5、找到目标函数和自定义函数在内存中的地址

6、修补目标函数，该步骤与Hook windows API一致

可以看到，与windows hook相比，重点在于编译函数和定位函数地址，这是由.Net的特性决定的。.NET
编写的代码经编译后，会得到一个由通用中间语言（CIL）构成的二进制文件，CIL构成的二进制文件会交由CLR进行接管， **只有在运行时**
才会由CLR进行编译（JIT），生成可以直接运行的native code。

我们可以通过RuntimeMethodHandle.GetFunctionPointer()方法获取编译后的native
code地址。但在.Net中，如果函数没有实际被调用，那么该函数可能不会被编译，也就无法定位到函数地址。幸运的是，RuntimeHelpers类可以手动触发JIT编译。如下代码所示。

    
    
    //反射找到函数
    MethodInfo ori = typeof(CmdletInfo).Assembly.GetType("System.Management.Automation.A"+"ms"+"i"+"Ut"+"ils").GetMethod("ScanC"+"ontent", BindingFlags.NonPublic | BindingFlags.Static);
    MethodInfo rep = typeof(Program).GetMethod("ScacnConte"+"ntStub", BindingFlags.NonPublic | BindingFlags.Static);
    
    //JIT 编译函数
    RuntimeHelpers.PrepareMethod(ori.MethodHandle);
    RuntimeHelpers.PrepareMethod(rep.MethodHandle);
    
    //获取函数地址
    IntPtr originalSite = original.MethodHandle.GetFunctionPointer();
    IntPtr replacementSite = replacement.MethodHandle.GetFunctionPointer();
    
    //修补目标函数
    .....

这里多说一句，未编译前MethodHandle.GetFunctionPointer()获得的地址指向PreJitStub块，大小为5个字节，该块的作用是调用JIT进行编译。

另外，在自定义函数这一步，由于函数总是返回1，因此c#编译器认为函数不是完整的函数调用，从而优化整个函数代码，无法hook。可以通过向函数添加属性来告诉编译器不要优化或内联该方法。

    
    
    [MethodImpl(MethodImplOptions.NoOptimization | MethodImplOptions.NoInlining)]
    private static int ScanContentStub(string content, string metadata) {
        return 1; //AMSI_RESULT_NOTDETECTED
    }

## 0x03利用

为了在 PowerShell 中安装Hook，需要把程序集加载到powershell中，作者提出了两种方法，一是使用Add-Type动态编译c#代码并加载到session中；二是将已编译的程序集作为 Base64 嵌入脚本中，并以反射方式将该
DLL加载到内存中；还有其他的利用思路，比如未托管代码使用CLR Hosting技术来加载Hook程序集，未托管代码可以做持久化，注入到启动项当中。

该技术针对.Net
API进行Hook，可以较好规避杀软，但需要对代码中的一些静态特征做混淆,如"System.Management.Automation.Amsiutils"字符串。

## 0x04总结

本文介绍了利用Hook .Net API进行amsi绕过的一种新技术，对其中关键技术点进行了分析，并简要介绍了Hook .Net API的其他利用思路。

## 参考链接

<https://practicalsecurityanalytics.com/new-amsi-bypass-using-clr-hooking/>

<https://learn.microsoft.com/en-us/archive/msdn-magazine/2005/may/net-framework-internals-how-the-clr-creates-runtime-objects>

## 关于我们

更多高级攻防对抗热点技术，欢迎关注公众号：M01N Team。

