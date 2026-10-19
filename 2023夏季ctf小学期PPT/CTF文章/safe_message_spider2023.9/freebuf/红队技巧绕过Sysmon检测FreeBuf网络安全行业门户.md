**一言不合就上[GitHub地址](https://github.com/bats3c/Ghost-In-The-Logs)**

[Sysmon](https://docs.microsoft.com/en-us/windows/win32/wes/windows-event-log)和[Windows事件日志](https://docs.microsoft.com/en-us/windows/win32/wes/windows-event-log)都是防御者中极为强大的工具。它们非常灵活的[配置](https://github.com/SwiftOnSecurity/sysmon-config)使他们可以深入了解设备上的活动，从而使检测攻击者的过程变得更加容易。出于这个原因，我将带领您完成击败他们的旅程；）

[xpn](https://blog.xpnsec.com/hiding-your-dotnet-etw/)和[matterpreter](https://posts.specterops.io/shhmon-silencing-sysmon-via-driver-unload-682b5be57650)对此进行了一些出色的研究。他们的解决方案都不错，但是不能完全满足我的需求。Metterpreter的卸载驱动程序的方法在技术上是可以做到的，但是卸载驱动程序感觉很不ok。特别是触发了很多非常明显的事件。

为了弄清楚如何绕过它，至关重要的是首先了解它是如何工作的。

启动Ghidra并启动sysmon64.exe，我们可以看到它使用ReportEventWWindows API调用来报告事件。

![](https://image.3001.net/images/20200409/1586393753_5e8e7299dfc2e.jpg!small)

现在我们知道了，可以hook 该调用并从那里阻止事件……然鹅这有什么卵用呢？我们仍然需要管理员权限来做到这一点，我认为我们可以更好地利用它们。

深入调用链并查看ReportEventWADVAPI32.dll，我们可以看到它实质上EtwEventWriteTransfer是在NTDLL.dll中定义的包装器。

![](https://image.3001.net/images/20200409/1586393739_5e8e728b1ae89.jpg!small)

通过检查，EtwEventWriteTransfer我们可以看到它调用了NtTraceEventntoskrnl.exe内部定义的内核函数。

![](https://image.3001.net/images/20200409/1586393740_5e8e728ce9b28.jpg!small)

现在我们知道，任何要报告事件的用户模式进程都将调用此函数，太棒了！这是可视化此过程的快速图表。

![](https://image.3001.net/images/20200409/1586393739_5e8e728b9d539.jpg!small)

现在我们知道了要定位的内核功能，让我们集中精力进行测试以查看其是否真正起作用。为此，我将使用WinDBG内核调试，有关更多信息，请参见[此处](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-up-kernel-mode-debugging-in-windbg--cdb--or-ntsd)。

我将从设置一个断点开始，nt!NtTraceEvent然后在该断点被击中时，我将使用修补函数的开始ret。这将迫使函数在运行任何事件报告代码之前立即返回。

![](https://image.3001.net/images/20200409/1586393741_5e8e728dd0dd3.png!small)

而且有效！如果您在下面看，您将看到我能够启动Powershell提示而不会触发任何sysmon事件。

因此，现在我们可以使用来开始编写PoC代码了。我们想要编写的代码将需要hook
，NtTraceEvent并为我们提供是否报告事件的选择。由于我们要定位的函数是内核函数，因此我们也需要使hook
代码在内核空间中运行。尝试执行此操作时，我们将遇到两个主要问题。

> [Kernel driver signing enforcement](https://docs.microsoft.com/en-> us/windows-hardware/drivers/install/kernel-mode-code-signing-policy--> windows-vista-and-later-)
>
>
> [PatchGuard](https://en.%2A%2A%2A%2A%2A%2A%2A%2A%2A.org/wiki/Kernel_Patch_Protection)

幸运的是，为了实现，已经有两个超酷的项目，[@
hFireF0x](https://twitter.com/hfiref0x)和[InfinityHook](https://github.com/everdox/InfinityHook)。我不会详细介绍它们的工作原理，因为它们各自的链接上有很多信息。但是我很高兴，因为这省了我很多时间，因为我不需要编写自己的bypass。

我将首先编写要在内核中运行的代码，所有链接都可以在[此处](https://github.com/bats3c/Ghost-In-The-Logs/blob/master/Source/InfinityHook/src/kinfinityhook/entry.cpp)找到。就在的开始DriverEntry，我们将需要找到两者的出口NtTraceEvent和IoCreateDriver。我们需要找到的原因IoCreateDriver是由于KDU。它会通过加载和利用签名的驱动程序，然后引导我们到内核空间加载我们的driver，装载我们的driver
的这种方法将意味着，无论是DriverObject和RegistryPath传递给DriverEntry将是不正确的。但是因为我们需要能够与用户模式过程进行通信（因此我们知道何时报告和阻止事件），所以我们需要创建一个有效的DriverObject。为此，我们可以调用IoCreateDriver它的DriverInitialize例程地址并将其提供给我们DriverInitialize然后将调用并传递一个有效值DriverObject，该有效值可最终用于创建IOCTL，让我们与用户模式进行交流。此代码段如下。

    
    
    NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath)
    {
    NTSTATUS        status;
    UNICODE_STRING  drvName;
    UNREFERENCED_PARAMETER(DriverObject);
    UNREFERENCED_PARAMETER(RegistryPath);
    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[+] infinityhook: Loaded.\r\n");
    OriginalNtTraceEvent = (NtTraceEvent_t)MmGetSystemRoutineAddress(&StringNtTraceEvent);
    OriginalIoCreateDriver = (IoCreateDriver_t)MmGetSystemRoutineAddress(&StringIoCreateDriver);
    if (!OriginalIoCreateDriver)
    {
    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to locate export: %wZ.\n", StringIoCreateDriver);
    return STATUS_ENTRYPOINT_NOT_FOUND;
    }
    if (!OriginalNtTraceEvent)
    {
    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to locate export: %wZ.\n", StringNtTraceEvent);
    return STATUS_ENTRYPOINT_NOT_FOUND;
    }
    RtlInitUnicodeString(&drvName, L"\\Driver\\ghostinthelogs");
    status = OriginalIoCreateDriver(&drvName, &DriverInitialize);
    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[+] Called OriginalIoCreateDriver status: 0x%X\n", status);
    NTSTATUS Status = IfhInitialize(SyscallStub);
    if (!NT_SUCCESS(Status))
    {
    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "[-] infinityhook: Failed to initialize with status: 0x%lx.\n", Status);
    }
    return Status;
    }

找到出口并获得有效的出口后，DriverObject我们现在可以使用InfinityHook初始化NtTraceEvent钩子。该功能IfhInitialize执行此操作。我调用IfhInitialize并将其传递给我的回调的指针。每次进行系统调用时都会命中此回调。给回调函数提供了指向将要调用的函数地址的指针。可以访问该指针意味着我们可以将其更改为指向钩子函数的地址。回调代码如下所示。

    
    
    void __fastcall SyscallStub(
    _In_ unsigned int SystemCallIndex,
    _Inout_ void** SystemCallFunction)
    {
    UNREFERENCED_PARAMETER(SystemCallIndex);
    if (*SystemCallFunction == OriginalNtTraceEvent)
    {
    *SystemCallFunction = DetourNtTraceEvent;
    }
    }

此代码会将每个调用重定向NtTraceEvent到我们的DetourNtTraceEvent。的代码DetourNtTraceEvent如下所示。

    
    
    NTSTATUS DetourNtTraceEvent(
    _In_ PHANDLE TraceHandle,
    _In_ ULONG Flags,
    _In_ ULONG FieldSize,
    _In_ PVOID Fields)
    {
    if (HOOK_STATUS == 0)
    {
    return OriginalNtTraceEvent(TraceHandle, Flags, FieldSize, Fields);
    }
    return STATUS_SUCCESS;
    }

这段代码非常简单。它将检查HOOK_STATUS（由用户模式进程通过IOCTL设置）是否为0，如果为0，则它将执行调用NtTraceEvent，从而报告事件。如果HOOK_STATUS非零，它将返回以STATUS_SUCCESS表明该事件已成功报告，当然不是。如果有人能弄清楚如何解析该Fields参数，那么可以对所报告的事件应用过滤器，这很酷；如果您联系我，我将为您提供我所拥有的所有信息，告诉你我还有多远，我们也许可以解决;）

因为我想将所有驱动程序都保留为一个可执行文件，所以我将这个驱动程序嵌入到可执行文件中，因此当需要使用它时，它将被解压缩，然后KDU会将其加载到内核中。

我不会详细介绍其余的代码，因为它主要是KDU并从用户模式与驱动程序进行交互，但是如果您有兴趣，可以在[这里](https://github.com/bats3c/Ghost-In-The-Logs/tree/master/Source/src)找到。

##  这样有效吗？

是的：）好吧，在我测试过的所有东西上，如果您发现它无法正常工作，或者有任何一般性的错误让我知道，我会尝试修复它们。另外，我不是程序员，所以我的代码将远非完美，但可以使用任何您能想到的很棒的功能随意发出请求！

这是它运行及其各种功能的一些示例。

###  加载驱动程序并设置挂钩

![](https://image.3001.net/images/20200409/1586393742_5e8e728e5c97d.jpg!small)

###  启用挂钩（禁用所有日志记录）

![](https://image.3001.net/images/20200409/1586393742_5e8e728ea6193.jpg!small)

###  获取挂钩的状态

![](https://image.3001.net/images/20200409/1586393743_5e8e728f2e009.jpg!small)

###  禁用挂钩（启用所有日志记录）

![](https://image.3001.net/images/20200409/1586393743_5e8e728f74284.jpg)

***参考来源:[dylan](https://blog.dylan.codes/evading-sysmon-and-windows-event-logging/)，FB小编周大涛编译，转载请注明来自FreeBuf.COM**

  

