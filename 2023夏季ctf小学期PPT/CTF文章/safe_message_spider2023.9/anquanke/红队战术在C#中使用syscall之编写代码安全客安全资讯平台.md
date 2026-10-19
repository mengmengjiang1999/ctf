# 红队战术：在C#中使用syscall之编写代码

阅读量 **228073**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-01 11:30:35

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Jack Halon，文章来源：jhalon.github.io

原文地址：<https://jhalon.github.io/utilizing-syscalls-in-csharp-2/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0130b4360a2c04a3f6.png)

## 前言

本文专注于实际编写代码，利用在上一篇文章中学到的内容，实现一个有效的syscall。除了编写代码外，也会介绍如何对“工具”代码进行管理，以及如何为之后与其他工具的集成做准备。

* * *

在上一篇文章中，我们介绍了一些在C#中使用syscall需要了解的基本概念，其中触及了一些比较深入的主题，例如Windows内部结构及系统调用的概念。还讨论了.NET
框架的工作原理以及如何在C#中利用非托管代码执行syscall汇编代码。

在阅读本文之前，我 **强烈**
建议你先阅读上一篇文章，否则你可能无法理解本文介绍的部分主题。当然，我会尽力对其进行解释并为其中的部分主题提供外部资源链接，但本文要讨论的几乎所有内容都能在上一篇文章中找到解释！
😁

在本文中，我们会专注于实际编写代码，利用在本文中学到的内容，实现一个有效的syscall。除了编写代码外，我们也会介绍如何对“工具”代码进行管理，以及如何为之后与其他工具的集成做准备。这里集成的意思类似[Ryan
Cobb](https://twitter.com/cobbr_io)编写的[SharpSploit](https://github.com/cobbr/SharpSploit)库文件，该文件被开发用于和其他C#项目集成在一起工作，但我们编写的代码不会有这么广的应用范围。

我最初是想要在本文中引导读者逐步开发出一个真正能在工作时使用的工具，类似[Dumpert](https://github.com/outflanknl/Dumpert)或[SysWhispers](https://github.com/jthuraisamy/SysWhispers)。但是考虑到这么做之后文章的长度以及复杂度，我选择编写一个简单的PoC代码来演示单个syscall的执行。

我相信在阅读完本文及示例代码（会同时发布在[GitHub](https://github.com/jhalon/SharpCall)上）之后，你自己也能编写出一个工具！如果你需要更多信息，我还会在文章末尾提供一些其他工具的链接，这些工具也在C#中使用了相同的syscall概念。

谁知道呢，也许我会直接做一个直播，和大家一起现场编写一个新的工具！ 😏

好了，现在让我们打开Visual Studio或Visual Code，开始敲写代码吧！

## 代码及类结构设计

如果说我在编写红队使用的自定义工具（无论是恶意软件还是其他植入程序）时学到的唯一内容，就是我们一定要组织好代码以及自己的想法，将它们分成不同的类。

[类](https://docs.microsoft.com/en-us/dotnet/csharp/tour-of-csharp/classes-and-objects)是C#中最基本的类型之一。简单来说，类是一种数据结构，它将字段(field)、方法以及其他成员函数组合在一个单元中。同时类还能够用作对象并支持[继承](https://docs.microsoft.com/en-us/dotnet/csharp/tutorials/inheritance)和[多态](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/polymorphism)，该机制可以用于派生类的扩展。

创建完后，只要在源代码文件中添加“[using](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/using-directive)”指令，就能够在代码库的任意位置使用这些类了。这时我们可以直接访问这些类的静态成员以及嵌套类型，而不需要在前面添加类名做限定。

比如说我们有一个叫做“ **Syscalls** ”的新类，其中包含了syscall逻辑。如果我们没有在C#代码中添加 **using**
指令，就需要使用完整的类名对函数进行限定。也就是说，如果该类中包含了一个对 **NtWriteFile**
的syscall汇编代码，如果想要在另一个类中访问该方法，就需要使用`Syscalls.NtWriteFile`这样的形式。这样当然也没问题，但如果使用这个类的次数比较多的话，就会显得很累赘。

现在，你们中的一些人可能会问，“ _为什么我们需要这种简化？_ ”

有两个原因：第一，在组织结构上可以让我们的代码更“干净”；第二，可以让调试及修复代码的过程更加轻松，不需要在大量的文本寻找分号的位置。

现在开始对我们的代码结构进行组织。首先创建一个新的.NET Framework Console App项目，并设置使用3.5 .NET
Framework，像这样：

![](https://p1.ssl.qhimg.com/t0168d4d67c8811b8df.png)

创建完成后，你应该可以访问一个新的文件，叫做`Program.cs`。 如果查看Visual Studio的右侧，应该能够注意到在Solution
Explorer中，解决方案的结构如下所示。

    
    
    +SharpCall SLN (Solution)
    |
    +->Properties
    |
    +->References
    |
    +->Program.cs (Main Program)
    

`Program.cs`文件中会包含程序的主要逻辑。就此次的PoC而言，我们会在该文件中调用并使用我们的syscall代码。之前已经介绍过了，当使用一个有效的syscall标识符调用
**syscall** 指令的时候，CPU中就会发生系统调用。该指令会让CPU从用户模式切换到内核模式，从而执行某些特权操作。

如果我们只用一个syscall，那么只需要把它添加到`Program.cs`文件。但是这么做之后，如果我们接下来想要进一步开发此程序，让其模块化或提高其灵活性，从而更好地和其他程序进行集成，就会出现更多的问题。

所以我们要始终考虑到未来的情况，把所有的syscall汇编代码分离到一个单独的文件中。这样，如果将来需要增加更多的syscall，就可以直接把它们添加到一个类中，然后从程序中对其进行调用。

这也是我们接下来要进行的工作。先在解决方案中添加一个新文件，将其命名为`Syscalls.cs`。现在，解决方案的结构应类似于：

    
    
    +SharpCall SLN (Solution)
    |
    +->Properties
    |
    +->References
    |
    +->Program.cs (Main Program)
    |
    +->Syscalls.cs (Class to Hold our Assembly and Syscall Logic)
    

很好，现在应该可以开始编程了吧？好吧，还不行，我们还忘了一件很重要的事情。 由于我们要使用的是非托管代码，所以还需要实例化Windows
API函数，这样我们就能够在C#程序中调用它们了。为了使用非托管函数，我们需要使用[P/Invoke](https://docs.microsoft.com/en-us/dotnet/standard/managed-code)对其结构、参数以及任何其他相关的标志信息进行声明，。

同样，以上内容也可以在`Program.cs`文件中完成，但是为了让代码更加整洁，应该在一个单独的类中完成所有P/Invoke工作。
因此，在解决方案中新添加一个文件，并将其命名为`Native.cs`，该文件包含了我们的“原生” Windows函数。

现在，解决方案的结构应类似于：

    
    
    +SharpCall SLN (Solution)
    |
    +->Properties
    |
    +->References
    |
    +->Program.cs (Main Program)
    |
    +->Syscalls.cs (Class to Hold our Assembly and Syscall Logic)
    |
    +->Native.cs (Class to Hold our Native Win32 APIs and Structs)
    

现在已经完成了程序的结构组织，并明确了各部分的功能，要开始正式地编程了！

## 编写syscall代码

因为这只是一个PoC，所以我会使用[NtCreateFile](https://docs.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)系统调用在桌面创建一个临时文件。
如果程序能够正常工作，就证明代码中的逻辑是正确的。之后我们就能编写更复杂的工具，并通过其他系统调用扩展我们的syscalls类。

还有一点要注意，下面所有的代码只能在64位系统上工作。

首先，我们需要为 **NtCreateFile** 的syscall编写汇编代码。
正如上一篇文章所述，我们可以使用[WinDBG](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/debugger-download-tools)反汇编并检查 **ntdll**
中NtCreateFile的调用情况。

先获得函数的内存地址，再在该地址处执行反汇编，这时可以获得以下输出。

![](https://p2.ssl.qhimg.com/t01f034cc02c6ba1b71.jpg)

从上图中可以看到syscall的标识符为0x55。
而且如果查看汇编指令的左侧，可以看到syscall指令的十六进制表示形式。由于C#不支持内联汇编，我们会把这些十六进制字符组成shellcode，并放入字节数组中。

该字节数组会放入`Syscalls.cs`文件的Syscalls类中，如图所示，创建一个新的名为`bNtCreateFile`的[静态](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/static)字节数组。

![](https://p1.ssl.qhimg.com/t010435315aeb1fd186.png)

到这里我们就完成了第一个汇编的syscall代码。但我们要如何构建代码来执行这段程序呢？如果你读过我的上一篇文章的话，应该会记得一个叫做[委托(delegate)](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/)的东西。

Delegate类型代表了对具有特定参数列表和返回类型的 **方法的引用** 。在对其进行实例化的时候，可以把具有兼容的签名以及返回类型的 **任意方法**
作为它的实例。然后就能通过该实例调用被委托的方法了。

听起来可能有些混乱，但是如果你记得的话，在上一篇文章中，我们定义了一个名为`EnumWindowsProc`的委托，之后定义了该委托的实现`OutputWindow`。该实现告诉了C#要如何处理传递给此函数引用的数据，不管它是来自托管代码还是非托管代码。

在此处的`Syscall.cs`类中，我们也可以执行同样的操作，为非托管函数( **NtCreateFile**
)定义一个委托。这样我们就能在该委托的实现中，把汇编的syscall转换为一个有效的函数了。

不过还是一步步的来，首先，我们要为该NtCreateFile委托定义签名。为此，在`Syscall`类中创建一个名为`Delegates`的公共的[struct类型](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/struct)。

该结构体中会包含所有的原生函数，也即委托的签名，这样就可以在之后的syscall中使用它们了。

![](https://p2.ssl.qhimg.com/t0191419c3c4deb634d.png)

在定义委托之前，先看一下NtCreateFile在C中的语法。

    
    
    __kernel_entry NTSTATUS NtCreateFile(
      OUT PHANDLE           FileHandle,
      IN ACCESS_MASK        DesiredAccess,
      IN POBJECT_ATTRIBUTES ObjectAttributes,
      OUT PIO_STATUS_BLOCK  IoStatusBlock,
      IN PLARGE_INTEGER     AllocationSize,
      IN ULONG              FileAttributes,
      IN ULONG              ShareAccess,
      IN ULONG              CreateDisposition,
      IN ULONG              CreateOptions,
      IN PVOID              EaBuffer,
      IN ULONG              EaLength
    );
    

在上面的语法结构中，有一些内容是我们之前没看到过的。

首先，NtCreateFile函数的返回类型为[NTSTATUS](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-erref/596a1078-e883-4972-9bbc-49e60bebca55)，该结构体中包含了代表每个消息标识符的无符号32位整数。除此之外，该函数中的部分参数接受的是一组不同的标志或者结构，比如说[ACCESS_MASK](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-dtyp/7a53f60e-e730-4dfe-bbe9-b21b62eb790b)标志，[OBJECT__ATTRIBUTES](https://docs.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes)结构以及[IO_STATUS_BLOCK](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_status_block)结构。

如果再查看一下其他参数的定义，比如说`FileAttributes`还有`CreateOptions`，我们会发现这些参数接受的也是特定的标志。

![](https://p5.ssl.qhimg.com/t0153bf3db1ecb6dd33.png)

![](https://p5.ssl.qhimg.com/t019526a62d461b8c6e.png)

所以如果想要在C#中使用非托管代码，就存在一个关键问题，我们需要 **手动**
创建这些标志的枚举类型以及结构，让其与上述Windows定义的值相同。否则，如果我们传递到syscall的参数与定义不符，就会导致syscall中断或者返回错误信息。

值得庆幸的是，[P/Invoke
wiki](https://www.pinvoke.net/)中包含相关信息。我们可以在这里查找如何实现原生的函数，结构体以及标志。

你也可以在Microsoft的[Reference
Source](https://referencesource.microsoft.com/)上搜索需要的特定结构以及标志信息。这里的内容应该比P/Invoke中的内容更接近原始的Windows参考手册。

下列链接有助于我们实现NtCreateFile函数中所需的必要结构以及标志：

  * [NTSTATUS](https://www.pinvoke.net/default.aspx/Enums/NtStatus.html)
  * [ACCESS_MASK](https://www.pinvoke.net/default.aspx/Enums.ACCESS_MASK)
  * [OBJECT_ATTRIBUTES & IO_STATUS_BLOCK](https://www.pinvoke.net/default.aspx/ntdll.ntcreatefile)
  * [FileAttributes, ShareAccess & CreateDisposition](https://www.pinvoke.net/default.aspx/kernel32.CreateFile)

由于这些值，结构和标志对于Windows来说都是“原生”的，我们把它们添加到`Native.cs`文件下的`Native`类中。

所有内容添加完毕后，下图显示了`Native.cs`文件的部分内容：

![](https://p0.ssl.qhimg.com/t0188f17d2b04123748.png)

注意，上图只显示了一部分已经实现的原生结构与标志。如果要阅读完整内容，请查看我的GitHub上SharpCall项目中的[Native.cs](https://github.com/jhalon/SharpCall/blob/master/Native.cs)文件。

此外，注意到在每个结构以及标志枚举器之前我们都添加了[public](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/public)关键字。这样我们就能从程序的其他文件中访问这些内容了。

实现以上内容后，我们就可以把NtCreateFile中C++形式的数据类型转换为C#形式的数据类型。转换后，该函数在C#中的语法应该为：

    
    
    NTSTATUS NtCreateFile(
      out Microsoft.Win32.SafeHandles.SafeFileHandle FileHadle,
      FileAccess DesiredAcces,
      ref OBJECT_ATTRIBUTES ObjectAttributes,
      ref IO_STATUS_BLOCK IoStatusBlock,
      ref long AllocationSize,
      FileAttributes FileAttributes,
      FileShare ShareAccess,
      CreationDisposition CreateDisposition,
      CreateOption CreateOptions,
      IntPtr EaBuffer,
      uint EaLength
    );
    

在按照该结构定义一个委托之前，我们先简要介绍一下上面的部分数据类型。

之前说过，C++中的指针或句柄在C#中一般都可以转换为[IntPtr](https://docs.microsoft.com/en-us/dotnet/api/system.intptr?view=netframework-4.8)，但在此例中，我把PHANDLE（指向[句柄](https://docs.microsoft.com/en-us/windows/win32/winprog/windows-data-types#handle)的指针）转换成了[SafeFileHandle](https://docs.microsoft.com/en-us/dotnet/api/microsoft.win32.safehandles.safefilehandle?view=netframework-4.8)类型。之所以这么做是因为在C#中
**SafeFileHandle** 代表了一个文件句柄的包装类。

因为我们需要创建文件，并且会通过委托把数据从托管代码传递到非托管代码（或者反向），所以我们要确保C#可以处理并理解它要marshaling的数据类型，否则可能会报错。

其余的数据类型应该很简单，因为`FileAttributes`，`FileShare`这些类型代表的就是我们添加到`Native`类中的结构以及标志枚举器中的变量和值。每次把数据传递给这些参数（无论是值还是描述符）时，都需要与特定的结构或是标志枚举器相对应。

你可能也注意到，我在一些参数中添加了[ref](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/ref)和[out](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/out-parameter-modifier)关键字。这两个关键字表明参数是通过引用而不是值传递。

**ref** 和 **out** 之间的区别在于， **ref** 关键字表示参数在传递之前必须先对其进行初始化，而 **out**
则不需要。另一个区别是， **ref** 关键字表示数据可以双向传递，并且当控制权返回到调用方法时，在被调用方法中对参数的任何修改都会反映到对应的变量中。而
**out** 关键字表示数据仅在单向传递，并且无论调用方法返回的值是什么，最后都会被设置成该引用变量。

所以在NtCreateFile函数中，我们为`FileHandle`添加了 **out** 关键字，因为如果函数执行 **成功** ，该参数会是一个指向用于
**接收** 文件句柄的变量的指针。这就表示数据只会被“传回”给我们。

接下来我们就可以把符合C#语法的NtCreateFile函数添加到`Syscalls`类中的`Delegates`结构中了。

完成后，Syscalls类应该如下所示。

![](https://p5.ssl.qhimg.com/t01b93966275342afae.png)

**注意** ：我在文件顶部添加了`using static
SharpCall.Native`。它告诉了C#使用叫做`Native`的静态类。之前已经解释过了，这么做就可以直接使用原生的函数，结构以及标志，而不需要添加类名的限定了。

在继续下一步之前，还要注意到在Delegates结构中，在设置NtCreateFile的委托类型之前，我还调用了[UnmanagedFunctionPointer](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.unmanagedfunctionpointerattribute?view=netframework-4.8)属性。该属性会控制委托的签名的marshaling行为，在传入或传出非托管代码时，与非托管函数指针类型进行转换。

该属性的添加十分关键，因为我们会使用不安全代码把非托管指针类型从syscall汇编代码marshal到上述函数委托中，正如上一篇文章所述。

太好了，我们已经取得了一些进展，定义了结构，标志枚举器以及函数委托，现在我们需要进一步实现该委托，从而处理传递给该委托的任何参数。这些参数会先被初始化，然后由syscall汇编代码进行处理。

先创建，或者说实例化我们的NtCreateFile函数委托。这部分内容可以直接添加在在syscall汇编代码之后。

创建完成后，`Syscalls.cs`文件应如下所示。

![](https://p5.ssl.qhimg.com/t01c7c6223f15a79183.png)

实例化委托后的`TODO`注释部分，会用来添加对传递于托管与非托管代码之间的数据进行处理的代码。

在上一篇文章中，我解释了[Marshal.GetDelegateForFunctionPointer](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getdelegateforfunctionpointer?view=netframework-4.8#System_Runtime_InteropServices_Marshal_GetDelegateForFunctionPointer_System_IntPtr_System_Type_)允许我们将非托管函数指针转换为指定类型的委托。
如果在[unsafe](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/unsafe)的上下文中使用该方法，我们就能创建一个指向shellcode所在内存位置的指针（即syscall汇编代码），并使用委托在托管代码中执行该汇编代码。

我们会在这里执行同样的操作。先创建一个新的名为`syscall`的[字节数组](https://docs.microsoft.com/en-us/dotnet/api/system.byte?view=netframework-4.8)，并将其设置为`bNtCreateFile`汇编代码的内容。
完成后，设置 **unsafe** 上下文并在大括号中添加不安全的代码。

更新完成后的`Syscalls.cs`文件应如下所示。

![](https://p5.ssl.qhimg.com/t01f00517fd2aa3b782.png)

我在上一篇文章中也解释过，在该不安全上下文中，我们会初始化一个新的名为`ptr`的字节指针，将其设置为`syscall`的内容，也就是汇编代码的字节数组。

之后，如前文所述，我们为指针添加了[fixed](https://docs.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/fixed-statement)语句，这样我们就能防止垃圾回收器在内存中对syscall字节数组进行重新定位。

之后，我们会直接把字节数组指针转换（[cast](https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/types/casting-and-type-conversions)）成一个叫做`memoryAddress`的IntPtr。 这样我们就能在程序执行期间获取到syscall字节数组所处的内存地址了。

更新完成后的`Syscall.cs`文件应如下所示。

![](https://p5.ssl.qhimg.com/t0106bf57a15333d6f2.png)

接下来要格外注意了，下面就是奇迹发生的地方！ 😉

由于我们现在已经拥有了（或将要拥有）程序执行期间syscall汇编代码所在的内存地址，我们需要完成一些操作以确保这部分代码能够在其分配的内存区域内得到正确的执行。

如果你熟悉exploit开发期间shellcode的工作原理——每当我们想要在目标进程或目标内存页中写入，读取或者执行shellcode的时候，首先要确保这部分内存区域具有相应的访问权限。
如果你对此还不熟悉，请阅读有关Windows安全模型对[进程安全及访问权限](//docs.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights))进行控制的内容。

比如说，让我们看看 **NtCreateFile** 函数在记事本中执行时具有怎样的内存保护。

    
    
    0:000> x ntdll!NtCreateFile
    00007ffb`f6b9cb50 ntdll!NtCreateFile (NtCreateFile)
    0:000> !address 00007ffb`f6b9cb50
    
    Usage:                  Image
    Base Address:           00007ffb`f6b01000
    End Address:            00007ffb`f6c18000
    Region Size:            00000000`00117000 (   1.090 MB)
    State:                  00001000          MEM_COMMIT
    Protect:                00000020          PAGE_EXECUTE_READ
    Type:                   01000000          MEM_IMAGE
    Allocation Base:        00007ffb`f6b00000
    Allocation Protect:     00000080          PAGE_EXECUTE_WRITECOPY
    Image Path:             ntdll.dll
    Module Name:            ntdll
    Loaded Image Name:      C:WindowsSYSTEM32ntdll.dll
    Mapped Image Name:      
    More info: lmv m ntdll More info: !lmi ntdll More info: ln 0x7ffbf6b9cb50 More info: !dh 0x7ffbf6b00000 Content source: 1 (target), length: 7b4b0
    

可以看到，记事本在其进程虚拟内存中对NtCreatreFile函数具有读取以及执行权限。这是因为记事本需要确保它可以执行该函数的syscall，同时读取其返回值。

在上一篇文章中，我解释了每个应用程序的虚拟地址空间是私有的，而且一个应用程序无法更改属于另一个应用程序的数据，除非后者对其部分私有地址空间进行共享。

由于我们现在在C＃中使用了不安全的上下文，并且穿过了托管代码和非托管代码之间的边界。所以我们需要在程序的虚拟内存空间对内存的访问进行管理，因为这时候CLR已经不会再为我们完成这项工作了！而且只有这样，我们才能将参数写入syscall，执行该代码，并为委托函数读取其返回的数据！

但我们要如何实现上述内容呢？好吧，接下来我要向你介绍一个新的伙伴——[VirtualProtect](https://docs.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect)函数。

通过 **VritualProtect**
函数，我们就能修改调用进程虚拟地址空间中已提交页中一个区域的保护机制。这就表示，如果在syscall的内存地址（我们刚刚获得）使用该原生函数，我们就能将该虚拟进程内存设置为读-写-执行权限！

我们在`Native.cs`文件中实现该原生函数。这样我们就能在`Syscalls.cs`中使用它修改汇编代码的内存保护机制了。

与往常一样，让我们看一下该函数的C结构。

    
    
    BOOL VirtualProtect(
      LPVOID lpAddress,
      SIZE_T dwSize,
      DWORD  flNewProtect,
      PDWORD lpflOldProtect
    );
    

看起来很简单，
我们只需要把函数中的[flNewProtect](http://pinvoke.net/default.aspx/kernel32/VirtualQueryEx.html)标志添加进行就可以了。

接下来添加该标志。 完成后，Native类中实现的内存保护标志应如下所示。

![](https://p0.ssl.qhimg.com/t0102cdc5858857b07e.png)

VirtualProtect函数应如下所示：

![](https://p3.ssl.qhimg.com/t0126576715a6d89d5f.png)

很好，我们已经有了很大的进展，而且就要结束了！ 好吧，还是有一些事情要做的。

现在我们已经实现了VirtualProtect函数，回到`Syscall.cs`文件，对`memoryAddress`指针执行VirtualProtect函数，赋予其读-写-执行权限。

同时，将该原生函数放入一个 **IF** 语句中。
这样如果函数执行失败，我们就能抛出一个[Win32Exception](https://docs.microsoft.com/en-us/dotnet/api/system.componentmodel.win32exception?view=netframework-4.8)异常，显示错误代码并停止代码的执行。

同时确保在代码的顶部添加了`using System.ComponentModel;`语句。 这样就可以使用`Win32Exception`类了。

完成上述操作后，我们的代码应如下所示：

![](https://p5.ssl.qhimg.com/t0191c744a31a0ab8f0.png)

如果VirtualProtect执行成功，非托管syscall汇编代码的虚拟内存地址（即`memoryAddress`变量所指向的地址）现在应该已经具有了读-写-执行权限。

这就表示我们现在有了一个指向非托管函数的指针。在之前也介绍过了，我们现在需要做的是使用[Marshal.GetDelegateForFunctionPointer](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getdelegateforfunctionpointer?view=netframework-4.8#System_Runtime_InteropServices_Marshal_GetDelegateForFunctionPointer_System_IntPtr_System_Type_)把该非托管函数指针转换为指定类型的委托。在此例中，应该转换为
**NtCreateFile** 委托。

我知道现在你们中的有些人可能会感到困惑，或者想知道我们为什么要这么做。在我解释有关内存保护的概念的时候，你就应该已经明白上述操作的原因了。但无论如何，我还是解释一下，确保在继续之前每个人都处在同一水平。

之所以要把非托管函数指针转换为NtCreateFile委托，是因为这样做之后，在执行syscall汇编代码的时候，就可以把该函数当作一个回调函数进行使用了。你可以回去看一下`Syscalls.cs`文件的第20行。

所以我们之前究竟在干什么呢？如果你的答案是“将参数传递给函数”，那么你是对的！

一旦委托函数接受创建文件需要的参数之后，它进一步把syscall所在内存位置的保护机制更新为读-写-执行。然后，把指向syscall的指针转换为NtCreateFile委托，即将其转换为实际的函数表示形式。

完成后，我们对该初始化的委托以及传递的参数调用return语句。从本质上讲，程序在这里会把参数压入堆栈，执行syscall，然后将结果返回给调用方，也就是`Program.cs`文件中的函数！

现在清楚了吗？很好！你已经是一个syscall学院的毕业生了！ ‍🎓

在解释完所有内容之后，我们就要实现[Marshal.GetDelegateForFunctionPointer](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getdelegateforfunctionpointer?view=netframework-4.8#System_Runtime_InteropServices_Marshal_GetDelegateForFunctionPointer_System_IntPtr_System_Type_)转换了，首先实例化NtCreateFile委托，将其命名为`assembledFunction`。完成后，将非托管指针类型转换为委托类型。

完成后，我们就能使用一个简单的return语句，通过实例化的`assembledFunction`委托返回syscall中的所有参数。

最终的`Syscall.cs`代码应如下所示。

![](https://p5.ssl.qhimg.com/t015220a24dcdce97e0.png)

这样我们就有了函数调用后syscall执行的最终版本！

## 执行syscall

到目前为止我们已经实现了syscall逻辑，现在要做的就是在程序中编写实际的使用 **NtCreateFile**
函数的代码，该函数会执行我们的syscall。

首先，确保已经导入了我们的静态类，这样就能像下图中这样使用所有原生函数和syscall了。

![](https://p2.ssl.qhimg.com/t010097351cfa44667e.png)

完成后，我们就可以初始化[NtCreateFile](https://docs.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntcreatefile)函数需要的结构和变量了，比如说文件句柄以及对象属性。

在此之前，还有一件事。 [OBJECT_ATTRIBUTES](https://docs.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes)，尤其是其中的`ObjectName`属性，要求一个指向[UNICODE_STRING](https://docs.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string)的指针，该结构中包含了句柄要打开的对象的名称。在此例中就是指我们要创建的文件名。

对于非托管代码来说，要初始化此结构，我们需要调用[RtlUnicodeStringInit](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/ntstrsafe/nf-ntstrsafe-rtlunicodestringinit)函数。

所以要确保把这个函数添加到`Native.cs`文件中，以便使用其功能。

![](https://p4.ssl.qhimg.com/t019d925ab8d6faa797.png)

知道了以上内容，我们就可以继续初始化相关结构了。 首先创建文件句柄以及unicode字符串结构。

我们选择把测试文件保存到桌面，所以把filename路径设置为`C:UsersUserDesktop.test.txt`，如下所示。

![](https://p5.ssl.qhimg.com/t0158974940bddd37d8.png)

完成后，我们就能初始化 **OBJECT_ATTRIBUTES** 结构了。

![](https://p2.ssl.qhimg.com/t011b573490d48a0819.png)

最后，剩下要做的就是初始化 **IO_STATUS_BLOCK** 结构，并调用 **NtCreateFile** 委托及其参数从而执行syscall！

完成所有内容后，最终的`Program.cs`文件应如下所示。

![](https://p2.ssl.qhimg.com/t01e5ef935689f5c9b3.png)

太棒了，我们终于完成了所有代码！ 现在就到了最重要的时刻——编译代码！

在Visual Studio中，确保已经把 **Solution Configuration** 修改成了 “ **Release** ”。
之后，在上面的工具栏中选择 **Build** –> **Build Solution** 。

几秒钟后，你就应该能看到以下输出，显示编译成功！

![](https://p2.ssl.qhimg.com/t0181a42d16cec4f053.png)

好吧，先不要太兴奋！ 这个代码可能还会在测试过程中失败，不过我敢肯定不会！ 😁

要测试这个新编译完成的代码，先打开命令提示符并进入到项目的编译位置。我这里是
`C:UsersUserSourceReposSharpCallbinRelease`。

如你所见，我的桌面上并没有`test.txt`文件，如下所示。

![](https://p2.ssl.qhimg.com/t01cc598310269017c0.png)

如果一切顺利，在执行了`SharpCall.exe`后，会执行我们的syscall，并在桌面上创建一个新的`test.txt`文件。

好吧，关键时刻。 让我们执行来看看！

视频在[这里](https://jhalon.github.io/images/syscall-code-21.mp4)。

确实出现了`test.txt`文件，我们的代码能够正常工作，而且成功地执行了我们的syscall！

但我们怎么确定执行的是syscall，而不是来自 **ntdll** 的原生api函数呢？

为了确保执行的是我们的syscall，我们可以再次使用[Process Monitor](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)监控我们的程序。

我们可以在这个软件中查看特定的读/写操作属性及其调用堆栈。

![](https://p4.ssl.qhimg.com/t01747a3a7e1fad21bd.png)

在监视该进程的执行过程后，我们发现里面有一个`test.txt`文件的`CreateFile`操作。如果查看该操作的调用堆栈，可以看到以下内容：

![](https://p3.ssl.qhimg.com/t0128bac0e0c9d5b3ec.png)

可以看到里面没有从 **ntdll** 发出的任何调用，只是一个从 **unknown** 到 **ntoskrnl.exe**
的syscall！我们实现了一个有效的syscall！

使用这种方法就能够绕过在 **NtCreateFile** 函数上的任何API hooking！ 😈

## 结束语

女士们，先生们，到这里我们就完成了此次旅程！我们学习了很多有关Windows
Internals，Syscall以及C＃的知识，现在你应该可以利用这些内容在C＃中创建自己的syscall了！

该项目的最终代码已经添加到了我的Github，位于[SharpCall](https://github.com/jhalon/SharpCall)仓库中。

在本文开头，我提到会提供一些使用相同技术的项目的资源链接。所以如果你觉得仍有问题或者只是想获得更多信息，那么我建议你看一下以下项目。

  * [SharpMiniDump](https://github.com/b4rtik/SharpMiniDump/)
  * [LOLBITS](https://github.com/Kudaes/LOLBITS)
  * [directInjectPOC](https://github.com/badBounty/directInjectorPOC)

好吧，差不多了！非常感谢大家阅读这两篇文章，并且让第一篇文章取得了如此巨大的成功！我没想到它会如此受欢迎。希望你能像阅读第一篇文章一样享受这篇文章，也希望你学到了一些新知识！

感谢阅读的每一个人！谢谢!

本文翻译自jhalon.github.io [原文链接](https://jhalon.github.io/utilizing-syscalls-in-csharp-2/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zoemurmure** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/207047](/post/id/207047)

安全客 - 有思想的安全新媒体

本文转载自: [jhalon.github.io](https://jhalon.github.io/utilizing-syscalls-in-csharp-2/)

如若转载,请注明出处： <https://jhalon.github.io/utilizing-syscalls-in-csharp-2/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [Malware](/tag/Malware)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t0148810f786e0f31fb.png) zoemurmure

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

