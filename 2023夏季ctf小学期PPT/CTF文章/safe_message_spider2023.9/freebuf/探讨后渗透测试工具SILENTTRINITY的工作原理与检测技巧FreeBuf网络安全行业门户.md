## 介绍

 **SILENTTRINITY 是最近发布的一款基于IronPython和c#的工具。这篇文章将深入探讨它的工作原理和检测技术。
.NET由于其强大的功能、易于开发以及在现代Windows平台上的默认存在的特点，已经成为安全领域中的一个重要组件。由于蓝队检测恶意PowerShell的能力不断增强，它开始取代PowerShell(最初出于类似的原因使用它)。
IronPython本质上是与.NET框架紧密结合的Python。这意味着攻击者能够利用简单的Python脚本与.NET库的强大功能，更轻松地在Windows平台上开发。**

## DLR

.NET语言变量类型和方法在编译时绑定，而Python是一种解释型脚本语言。因此，如何在.NET环境中执行Python代码？答案就在于DLR(dynamic
language runtime)。下图显示了DLR的架构视图（Microsoft 2017）。  
![1.png](https://image.3001.net/images/20190217/1550375709_5c68db1d7e8f3.png!small)DLR是一个运行时环境，允许像Python这样的动态语言在.NET上运行，并最终编译成相应的通用中间语言（CIL）格式。使这成为可能的DLR组件之一是“动态对象互操作性”。
Python的一个关键特性是它不必在编译时声明其变量类型。相反，变量类型解析在运行时执行，这与标准.NET语言（如C＃）的运行方式不同。为了解决这个问题，DLR提供了一种称为“动态”的数据类型。分配有“动态”数据类型的变量在运行时而不是编译时解析，从而允许Python保持其动态特性并仍然能够在.NET环境中运行。
在SILENTTRINITY中，IronPython代码嵌入并在C＃对象中执行，并且通过扩展，在.NET环境中执行。这意味着它将首先编译为CIL代码，随后通过使用JIT引擎成为本机代码。我们之前已经在博客中对此进行了更详细的讨论（
[第1 ](a%20href=)[部分](a%20href=)和[第2部分](a%20href=)）。

## SILENTTRINITY的工作原理

SILENTTRINITY由运行Python的C2服务器和C＃后门组成，使用动态.NET程序集在受害者的机器上执行。下面的图片显示了SILENTTRINITY如何工作的。我们将使用msbuild
stager机制作为示例。  
  
1.首先将包含c#后门的xml文件放入受害者。2.通过MsBuild.exe执行，C＃后门被反序列化并加载到内存中。3.一旦植入到内存中，后门将连接回SILENTTRINITY
C2服务器并将名为staged.zip的zip文件下载到内存中。该zip文件实际上由IronPython的.NET程序集和一个名为stage.py的Python脚本组成。4.随后，.NET程序集通过使用.NET的库加载到内存中。一旦加载了程序集，就能够调用IronPython引擎来执行stage.py.5.C2服务器现在可以向受害者推送Python编码的模块。

## 检测SILENTTRINITY

现在我们已经了解了SILENTTRINITY的工作原理，让我们来看看如何检测它。我们将通过发布的Python脚本使用. NET
ETW提供程序来跟踪CLR底层使用的行为。

## 动态装配加载

C＃implant实际上是“ST”类型的C＃类，它的一个实例是在运行时动态创建的。这可以通过.NET的“Reflection”和“Activator”库来实现，如下面的代码片段所示。  
![3.png](https://image.3001.net/images/20190217/1550375778_5c68db6296977.png!small)因此，我们可以尝试使用Python脚本跟踪此类函数调用的存在，如下图所示。  
![4.png](https://image.3001.net/images/20190217/1550375930_5c68dbfa536c7.png!small)如图所示，我们可以观察到“GetType”和“CreateInstance”函数的JIT-Inlining失败，因此表明这些函数至少执行了一次。但是，我们也看到内存中的程序集负载与实例创建和SILENTTRINITY程序集本身相关:  
![5.png](https://image.3001.net/images/20190217/1550375947_5c68dc0bcb3a0.png!small)

## IronPython程序集

C＃后门如果想要使用python引擎执行python代码,那么在这之前，它必须首先在运行时导入一组程序集，即：

    
    
    •IronPython.dll
    •IronPython.Modules.dll
    •Microsoft.Dynamic.dll
    •Microsoft.Scripting.dll
    

这可以通过利用“ResolveAssembly”事件的回调方法来完成（Richter，2010）。下面的代码片段显示了如何实现这一目标。
![6.png](https://image.3001.net/images/20190217/1550375964_5c68dc1c4fff3.png!small)一旦正确加载了程序集，C＃后门就能够利用IronPython引擎来执行Python代码，如下面的代码片段所示。  
![7.png](https://image.3001.net/images/20190217/1550375978_5c68dc2a8b790.png!small)由于上述DLL的加载是SILENTTRINITY的关键部分，我们也可以尝试寻找这些装配负载的证据：  
![8.png](https://image.3001.net/images/20190217/1550375995_5c68dc3b0644c.png!small)在这个例子中，我们可以通过“DomainModuleDCStart_V1”和“ModuleDCStart_V2”事件来观察正在加载的dll，从而表明IronPython的存在。它们也在内存中加载，没有文件支持。但是，重要的是要注意这些程序集的存在并不表示任何恶意行为本身。使用IronPython引擎的合法.NET应用程序也会加载这些，，不过它更有可能从磁盘加载这些文件。但是，在大多数企业环境中，很多应用程序不太可能合法地使用IronPython。与其他IronPython用法的另一个重要区别是，这里涉及的程序集用于SILENTTRINITY使用的IronPython的嵌入式使用。如果IronPython被用作一个独立的python解释器来运行在。net框架上调用的python脚本，那么可以看到ipy.exe独立解释器正在使用。

## SafetyKatz模块

SILENTTRINITY包含一些后期开发阶段的模块。我们将看看其中一个模块SafetyKatz。这很像同名的GhostPack模块，它会转储lsass的进程内存，然后在内存中加载Mimikatz来提取凭据。下面的代码片段显示了Python中SafetyKatz的实现：  
![9.png](https://image.3001.net/images/20190217/1550376009_5c68dc49e75bc.png!small)正如在动态语言运行时一节中提到的，可以通过使用.NET
ETW提供程序来跟踪JIT和Interop事件来检测这一点。  
![10.png](https://image.3001.net/images/20190217/1550376030_5c68dc5e15e3a.png!small)正如所料，我们能够观察到来自SharpSploit模块的VirtualAlloc和MinDumpWrite函数调用的互操作事件所关注的事件。

## 流程活动

除了查看.NET ETW事件，我们还可以跟踪可疑的流程活动。由于我们在此示例中使用了msbuild
stager，因此我们显然会看到msbuild进程执行事件。  
![11.png](https://image.3001.net/images/20190217/1550376042_5c68dc6aeb124.png!small)由于MSBuild负责执行xml文件，我们可以寻找由MSBuild执行的xml执行的迹象。大多数MSBuild事件遵循术语或父和参数的通用格式，因此在整个企业中，可以基线正常活动和点偏差。我们还可以寻找源自MSBuild的连接。C＃后门必须定期连接回C2服务器以检查待处理的操作，如下面的代码所示。  
![12.png](https://image.3001.net/images/20190217/1550376058_5c68dc7add428.png!small)因此，即使没有挂起的作业，c#后门也必须定期与C2通信，或者直到MSBuild进程终止。因此，我们可以搜索流量，如下图所示。  
![13.png](https://image.3001.net/images/20190217/1550376075_5c68dc8b7664b.png!small)![14.png](https://image.3001.net/images/20190217/1550376092_5c68dc9c29704.png!small)

## 结论

作为维护者，当我们确定IOC时，这也是正确的。这篇文章提出了几个IOC来检测SILENTTRINITY的存在。一些IOC，例如检测IronPython装配加载，本身就是低保真度指标，但当你将所有活动结合起来时，SILENTRINITY的行为变得越来越具体，这有助于寻找它。在调查期间，维护者通常必须得出一个假设，并且有几个不同的IOC通常可以加强这个假设。例如，如果我们要检测动态程序集加载，结合IronPython程序集加载，结合MSBuild.exe的XML参数和常规网络连接，那么即使在像Safetykatz这样的恶意模块运行之前，我们也有更多的妥协证据。
。 我们要感谢byt3bl33d3r创建这样一个令人印象深刻的工具。

## 参考

> <https://github.com/byt3bl33d3r/SILENTTRINITY>
>
> <https://docs.microsoft.com/en-us/dotnet/framework/reflection-and-> codedom/dynamic-language-runtime-overview>
>
> <https://blogs.msdn.microsoft.com/microsoft_press/2010/02/03/jeffrey-> richter-excerpt-2-from-clr-via-c-third-edition/>

***参考来源：[countercept](https://countercept.com/blog/hunting-for-silenttrinity/)，由周大涛编译，转载请注明来自FreeBuf.COM**  

