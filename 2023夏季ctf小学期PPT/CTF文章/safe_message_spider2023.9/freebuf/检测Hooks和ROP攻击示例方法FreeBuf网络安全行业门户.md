**翻译稿件：** ******原始文章：**

 ******<https://www.apriorit.com/dev-blog/536-detecting-hook-and-rop-attacks>**

虽然有许多创新系统可确保软件安全。 但是许多应用程序仍然容易受到hooks和return-oriented programming(ROP)的攻击。
虽然不可能摆脱应用程序中的所有漏洞，但开发人员应该在编码阶段考虑可执行空间保护。
本文介绍了一些有效的方法，用于检测我们用于保护自身程序的hooks和ROP攻击。

**简介**

有时，我们的应用程序遭受网络罪犯使用hooks或ROP攻击，因此我们必须找到有效的方法来保护它们。
在本文中，我描述了一个案例，当我设法检测到局外人（第三方应用程序，恶意软件或逆向工程师）在我们的应用程序中拦截系统调用来改变软件行为或监视其性能时。

我还描述了对以下类型的攻击保护的方法有两种：

*需要将第三方代码注入任何目标应用程序以更改内存页面权限和重写代码的hooks

*不需要任何代码注入的ROP攻击

您可以使用这些方法来保护自己的应用程序或设计主动防御系统以防止刚才提到的各种攻击，甚至是0day攻击。

**HOOKS**

hooks用于许多目的，但网络罪犯通常使用它们来改变应用程序或操作系统的行为并监视它们的执行。 有各种各样的hooks，但在本文的范围内我只考虑两种类型：

修改导入地址表（IAT）

[函数头跳转(detour)](https://www.apriorit.com/dev-blog/235-splicing-to-hide-files-and-processes)

为了hook函数，攻击者需要在更改内存加载的初始化代码。为了打补丁，他们必须重写IAT中的地址。对于detour，他们需要在的函数开头更改为JMP指令。结果就是这个程序执行将被更改。

因此，为了检测代码被更改，您可以使用FunctionForChecking（必需的API）替换所有函数调用。在这里，您可以应用各种方法来验证
“必需的API” 是否是真实的API地址，或者是否已由第三方替换。下面你要求做到的：

检查函数的开头的字节，有效识别为异常行为的控制转移指令。

检查函数的所有校验和。校验和改变了表示指令已经被替换。

确保跳转控制的地址是在自身加载的模块中，该模块应该是函数，但不在第三方加载的模块中。

在没有修改原始代码的情况下就很难做到这一点。此外，对于hooks检测，您可以将被分析进程中加载的模块与原始模块进行比较。这里有一个[例子](https://www.apriorit.com/dev-blog/236-simple-anti-splicer)。然而，这种钩子检测并不是主动的，因此只能检测已被安装的钩子。

要执行 **hooks** ，第三方程序需要对内存进行写操作。但是，要做到这一点，它应该获得写入内存页面的权限。只有在恶意软件代码调用
**VirtualProtect** 函数后才能拥有这些权限。换句话说，为了在我们的应用程序中拦截对 **WinAPI** 的调用，第三方代码需要使用
**WinAPI** 本身。

因此，我们也可以拦截 **VirtualProtect** 并进行检查。 如果 **VirtualProtect** 由一个已知模块调用，那么我们调用原始的
**VirtualProtect** 。 我们可以通过在应用程序启动时保存所有模块的开头和结尾的地址并检查调用模块是否在我们的模块列表中来实现。
但是，去定义一个已经被加载的模块是非常困难的。 此方法仅防止使用远程线程进行DLL注入。
但也可以通过注册[AppInit_DLLs](https://www.apriorit.com/dev-blog/160-apihooks)和[KnownDlls](https://www.apriorit.com/dev-blog/257-dll-injection)键来执行注入。

出于攻击检测的目的，我们可以假设在模块加载到进程的地址空间后，不能更改内存页面的权限。

**保护的实现**

通过一个DLL实例来注入代码，这需要创建远程线程。 在此过程中，DLL尝试hook **MessageBox** 。 在我们的例子中，我使用
**mhook** 进行挂钩安装。 您可以在另外一个[文章](https://www.apriorit.com/dev-blog/160-apihooks)中了解有关 **mhook** 的更多信息。 但是，当我尝试使用IAT注入钩子时，此方法也还需要调用
**VirtualProtect** 。 安装钩子后，我们的应用程序将显示不同于下面的 **MessageBox** 消息。

 __

 _std::cout << "after pressingENTER MessageBox will be shown\n";_

 _getchar();_

 _MessageBox(NULL, L"text",L"caption", 0);_

 __

我实现了对hook的保护之后，以下是代码：

 __

 _HookDef hookDef;_

 _if_ _(hookDef.Init())ret_

 _{ /* three lines above */_ _}_

**Init** 拦截 **VirtualProtect** 和 **VirtualProtectEx** 。 当我使用 **mhook**
挂钩所提到的函数时，我得到了无限的递归，因为 **mhook** 本身使用了 **VirtualProtectEx** 来挂钩。
因此，我必须添加一个检查，如果挂钩函数是 **VirtualProtectEx** ，那么我使用 **VirtualProtect** 来应用
**mhook** 。

之后，钩子通过调用 **CaptureStackBackTrace** 来定义返回地址，以便了解调用从哪个模块启动。 如果它检测到传输到
**VirtualProtect** 的地址已经属于加载到内存的模块，则有人试图挂钩我们的应用程序。

_if_ _(GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS,_

 _reinterpret_cast <LPCTSTR>(vpAddr),_

 _ &hmodule))_

 _{_

 _InformAboutHook(callerAddress);_

 _}_

 __

 __

最终我们得到下面的结果：

  
![image.png](https://image.3001.net/images/20181010/1539149768_5bbd8fc8644a8.png!small)  

**ROP attack**

 ****

在另外一篇[文章](https://en.wikipedia.org/wiki/Return-oriented_programming)中，我已经解释过如何执行ROP攻击。
在这种情况下，我使用了一个现成的漏洞，它允许我在msvcp140.dll的小工具链中调用 **VirtualProtect** 。
您还可以在这篇[文章](https://www.apriorit.com/dev-blog/434-rop-exploit-protection)中了解此漏洞执行利用方式。 为了执行它，我改变了msvcp140.dll加载地址，它的地址与初始化地址的不同，

  
![image.png](https://image.3001.net/images/20181010/1539149783_5bbd8fd7e2718.png!small)  

gadget中地址的更改在上图中标记为红色。 地址以little-endian编写，每个地址为4个字节。 因此，您可以看到我20个偏移的gadget。

让我们假设在我们的应用程序中，使用上面的ROP链重写堆栈。 漏洞利用执行从指令链开始，每条指令链都以ret指令结束，以便随时调用
**VirtualProtect** 。 跳转到 **VirtualProtect** 最后一个ret指令处被执行的。

**防止** **ROP** **攻击**

开发人员如何检测应用程序中的ROP攻击？ 很明显，他们的执行需要操纵堆栈。 因此，对于检测基于堆栈改变的ROP攻击要有一定的范围选择。 接下来我们来看看：

[**Shadow
Stack**](https://en.wikipedia.org/wiki/Shadow_stack)是一种基于创建第二个堆栈的方法，其返回地址从原始堆栈复制而来，并且在返回函数之前，从两个调用堆栈加载返回地址去比较它们：如果记录不同，则其中一个已被重写。
有趣的是，这种方法已经在处理器级别实现（[文档](https://software.intel.com/sites/default/files/managed/4d/2a/control-flow-enforcement-technology-preview.pdf)）了。

跳转调用：

 _push %table_index%_

 _jmp %function%_

返回:

 _popebx_

 _jmp table[%table_index%]_

 __

但是，这种方法无法检测到攻击; 它可以防止攻击并使其无法进行。

[
**G-Free**](http://www.s3.eurecom.fr/docs/acsac10_gfree.pdf)方法添加了序言和结尾，而不是更改指令。
如果在序言中的加密的返回地址和在结尾中解密后的返回地址不匹配，则ret指令将不会执行或将执行不正确。

[
**Stack**](https://en.wikipedia.org/wiki/Buffer_overflow_protection#Canaries)[
**canaries**](https://en.wikipedia.org/wiki/Buffer_overflow_protection#Canaries)方法将已知值放在堆栈上的缓冲区和控制数据之间。
返回前会检查这些值。 如果返回地址已更改，则这些值也会更改。 这是
**[StackGuard](https://www.usenix.net/legacy/publications/library/proceedings/sec98/full_papers/cowan/cowan.pdf)**
中堆栈canary实现的一个示例。

无论如何，这些解决方案需要二进制重编译。 在本文中，我想思考了另一种方法：Last Branch Recording（LBR）。

使用 **gadgets** ，攻击者可以调用任何系统函数。 但是，单个函数调用通常是不够的; 有必要用更多的逻辑来执行一些事情。
但是，创建具有更复杂逻辑的ROP链需要更多时间，并且还受到 **ASLR** 的限制。 这就是为什么ROP经常被用作绕过某些保护然后执行恶意代码。
例如，您可以创建一个ROP链，用于为 **shellcode** 分配内存，然后调用 **VirtualProtect** ，为shell转移控制。

因此，为了检测ROP攻击，我们可以拦截对系统函数的调用，并尝试检查控制流如何转移到这一点：通过调用指令（正常行为）或获取ret指令（异常行为）。

但是我们怎样才能获得跳转地址？ 现代处理器嵌入了一种称为Last Branch Recording的机制。 激活后，处理器将跳转地址记录到MSR寄存器中。
记录的分支数（CPU从哪里跳过）取决于处理器的类型。 例如，英特尔酷睿i5-6200U记录了31个分支机构。
在任何情况下，您仍然可以拥有最后一个分支的索引。

您可以发现运行LBR的MSR地址并读取最后一个分支的索引并在[此处分支](http://sorami-chi.hateblo.jp/entry/2017/12/17/230000)。
该文章中提到的硬编码值来自英特尔的手册，第[1381](https://xem.github.io/minix86/manual/intel-x86-and-64-manual-vol3/o_fe12b1e2a880e0ce.html)页。此外，英特尔处理器已经为分支存储应用了一项改进的[特性](https://software.intel.com/en-us/blogs/2013/09/18/processor-tracing)，我在本文中没有介绍。

**LBR** **实现**

我必须使用内核模块才能使用MSR。
我还尝试通过安装Dr7寄存器字节来创建[调试进程](https://www.codeproject.com/Articles/517466/Last-branch-records-and-branch-tracing)，从用户模式激活MSR，但这种方法非常不稳定且有限。

我使用__writemsr和__readmsr函数进行MSR输入输出。 通过将第一个字节安装到地址0x1d9来执行LBR激活。
我在用户模式下使用调用DeviceIoControl（[更多关于DeviceIoControl](https://www.codeproject.com/Articles/9575/Driver-Development-Part-Introduction-to-Implemen)）与驱动程序进行进一步通信：

_IOCTL_ROPPROT_FN fn { (unsigned long_ _long)addr };_

 _IOCTL_ROPPROT_FN fromFnCalled { 0 };_

 _DeviceIoControl(hDriverDevice, IOCTL_ROPPROT_CHECK_LBR, &fn,sizeof(fn),
&fromFnCalled, sizeof(fromFnCalled), &dwReturn, NULL);_

 __

返回到FnCalled后，将记录执行跳转的指令地址。

简单指令搜索实例如下所示：

 __

 _do_

 _{_

 _toBr = __readmsr(MSR_LASTBRANCH_0_TO_IP + lastLbrIdx);_

 _lastBr= __readmsr(MSR_LASTBRANCH_0_FROM_IP + lastLbrIdx);_

 _if_ _(toBr == checkedAddr)_

 _{_

 _*fromAddr= lastBr;_

 _return_ _ROPPROT_SUCCESS;_

 _}_

 _} while_ _(lastLbrIdx--);_

 __

 __

之后，调用者将返回地址的第一个字节与ret指令的操作码（在钩子函数内）进行比较。

__

_unsigned char_ _byte = *(unsigned char*)fromFnCalled.addr;_

 _if_ _(IsRet(byte))_

 _{_

 _MessageBox(NULL,L"ROP attack detected!", L"Alert", 0);_

 _Return false;_

 _}_

 __

 _// call the original function_

以下是查找调用者：

  
![image.png](https://image.3001.net/images/20181010/1539149811_5bbd8ff358802.png!small)

在检测到被挂钩的 **VirtualProtect** 之后，系统通过使用带有指令 **IOCTL_ROPPROT_CHECK_LBR** 的调用
**DeviceIoControl** 来请求驱动程序。 您可以在DebugView窗口中看到驱动程序消息。
它从最后记录的那个开始经过分支，并通过我们的钩子 **VirtualProtect** （0x402a60）搜索传送给它的地址。
当它找到地址时，它定义了执行跳转的位置：0x77696930（ **VirtualProtectStub** ）。
因为它只是一个jmp指令，它会查看执行跳转VirtualProtectStub - 0x6b7a22fc的位置并返回该地址。
我们的应用程序检查该地址的指令，如果是ret指令，则发送警告。  

![image.png](https://image.3001.net/images/20181010/1539149823_5bbd8fffe1ca9.png!small)

在上面，您可以看到将esp中的地址更改为eax中的地址VirtualProtectStub的最后一个gadget。
之后，ret指令重定向到VirtualProtectStub。 右边是关于ROP链中这个gadget的记录，它在溢出后得到自己的堆栈。

 **如果你想运行驱动**

如果要运行驱动程序，则应考虑以下几个方面。
对于驱动程序开发，我使用了[Windows驱动程序工具包](https://docs.microsoft.com/en-us/windows-hardware/drivers/other-wdk-downloads)。 另外，我使用Visual Studio 2015进行驱动程序编译。

虽然驱动程序很可能是经过测试签名的，但您需要允许从命令行运行此类驱动程序，然后重新启动计算机：

bcdedit /settestsigning on

此外，您可能需要事先在BIOS中停用安全启动。
此外，您可能需要在寄存器中添加一个[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SessionManager\Debug
Print Filter](https://docs.microsoft.com/ru-ru/windows-hardware/drivers/devtest/reading-and-filtering-debugging-messages#setting-the-component-filter-mask)记录，以便在 **DebugView** 中查看驱动程序输出。

 **结论**  

以上所描述的方法不是最佳 **hooks** 和 **ROP** 检测解决方案。它们只是可能的方法。例如，如果您使用jmp指令而不是ret选择最后一个
**gadget** ，则实施的保护将不会检测到攻击。在这种情况下，您需要对记录的分支执行更详细的分析，或者还要考虑ret指令的频率。

此外，我的防御仅仅基于使用 **VirtualProtect** ，但您还需要保护一系列关键函数，如 **LoadLibrary**
，ROP攻击可用于动态加载。所描述的ROP攻击检测方法的思想来自于[kBounce](https://www1.cs.columbia.edu/~angelos/Papers/2013/kbouncer.pdf)，它包含在MicrosoftEMET中。

至于hook，您需要考虑到所描述的保护可能会干扰使用 **VirtualProtect** 的保护器的性能。至于 **Microsoft EMET**
，它还在其内存保护特性中使用 **VirtualProtect** **hook** 。

您可以下载 **hook** 和 **ROP** 攻击检测的示例：

[hookdef_src](https://www.apriorit.com/downloads/hookdef_src.zip)

[opprot_src](https://www.apriorit.com/downloads/ropprot_src.zip)

  

