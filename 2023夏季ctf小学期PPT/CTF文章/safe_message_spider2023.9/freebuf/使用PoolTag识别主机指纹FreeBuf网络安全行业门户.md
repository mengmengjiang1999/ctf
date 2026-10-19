## 写在前面的话

**通常情况下，恶意软件会对它所在的主机进行指纹识别，以便发现更多的信息。这个过程会分析一些特定的数据，用来判断恶意软件是否在VM中运行，除此之外，还会检测其他软件的存在。例如，恶意软件经常试图找出系统监控工具是否在运行(procmon,
sysmon等)和安装了哪些AV软件。在本文中，我们将介绍另一种被恶意软件滥用的主机进行指纹识别的方法。**

## 指纹识别的常用方法

首先，我们介绍几种恶意软件检测VM环境的常见方法：

1.枚举进程

2.枚举加载的模块

3.枚举文件

4.从Windows注册表中提取的数据（硬盘，BIOS等）

5.枚举加载的驱动程序

6.打开特定设备对象的句柄

7.枚举系统资源（CPU内核，RAM，屏幕分辨率等）

## PoolTag了解一下

如果您对Windows内核驱动程序的开发和分析有一定的经验，那么我想您应该熟悉`ExAllocatePoolWithTag`函数，该函数用于在内核级别上分配内存块。这里的关键部分是`Tag'`参数，用于为特定的分配提供某种标识。如果出现错误，例如由于内存损坏这种问题，我们可以使用指定的标记(最多4个字符)来将缓冲区与分配内存块的内核驱动程序中的代码路径关联起来。这种方法可以检测内核驱动程序的存在，因此，在内核中加载模块的软件可能会绕过上面提到的指纹方法，这些方法依赖于驱动程序可能更改的信息。换句话说，从恶意软件作者的角度来看，它是用来检测某些真正重要的东西很好选择。例如，安全或监控软件可能试图通过在内核级别注册回调过滤器来隐藏其进程和文件。分析师可能会试图通过从注册表中删除恶意软件通常搜索的东西来强化虚拟机环境。但是，安全软件供应商或分析人员可能并不会修改他们自己的程序或系统中VM环境使用的特定内核驱动程序，从而修改内核池分配的标记。

## 获取PoolTag信息

可以通过调用`NtQuerySystemInformation`函数并为`SysteminformationClass`参数选择`SystemPoolTagInformation
(0x16 )`来获取此信息
。MSDN上记录了部分上述功能和相关的`SysteminformationClass`可能值，幸运的是，通过一些研究，我们找到研究人员完成的一些文档。Alex
Ionescu在他的NDK项目中记录了许多关于Windows内容。为了证明这个，我们编写了一个可以自己的获取和解析PoolTag信息的小工具，但是如果你想用GUI方式，推荐使用PoolMonEx这个工具。源代码如下：  
![1.png](https://image.3001.net/images/20180827/1535363967_5b83cb7f61031.png!small)您可以将其与`Nbtk`标记的`PoolMonEx`分配结果进行比较，如下所示。  
![2.png](https://image.3001.net/images/20180827/1535363973_5b83cb85c9cd0.png!small)

### QueryPoolTagInfo.cpp

    
    
    #include "Defs.h"
    #include <iostream>
     
    using namespace std;
     
    int main()
    {
        NTSTATUS NtStatus = STATUS_SUCCESS;
        BYTE * InfoBuf = nullptr;
        ULONG ReturnLength = 0;
        
        _ZwQuerySystemInformation ZwQuerySystemInformation = (_ZwQuerySystemInformation)GetProcAddress(GetModuleHandleA("ntdll.dll"), "ZwQuerySystemInformation");
     
        do{
            NtStatus = ZwQuerySystemInformation(SystemPoolTagInformation, InfoBuf, ReturnLength, &ReturnLength);
     
            if (NtStatus == STATUS_INFO_LENGTH_MISMATCH)
            { 
                if (InfoBuf != nullptr)
                {
                    delete[] InfoBuf;
                    InfoBuf = nullptr;
                }
     
                InfoBuf = new (nothrow) BYTE[ReturnLength];
     
                if (InfoBuf != nullptr)
                    memset(InfoBuf, 0, ReturnLength);
                else
                    goto Exit;
            }
     
        } while (NtStatus != STATUS_SUCCESS);
     
     
        PSYSTEM_POOLTAG_INFORMATION pSysPoolTagInfo = (PSYSTEM_POOLTAG_INFORMATION)InfoBuf;
        PSYSTEM_POOLTAG psysPoolTag = (PSYSTEM_POOLTAG)&pSysPoolTagInfo->TagInfo->Tag;
     
        ULONG count = pSysPoolTagInfo->Count;
        cout << "Count: " << count << endl << endl;
     
        for (ULONG i = 0; i < count; i++)
        {
            cout << "PoolTag: ";
     
            for (int k = 0; k < sizeof(ULONG); k++)
                cout << psysPoolTag->Tag[k];
     
            cout << endl;
     
            if (psysPoolTag->NonPagedAllocs != 0)
            {
                cout << "NonPaged Allocs: " << psysPoolTag->NonPagedAllocs << endl;
                cout << "NonPaged Frees: " << psysPoolTag->NonPagedFrees << endl;
                cout << "NonPaged Pool Bytes Used: " << psysPoolTag->NonPagedUsed << endl;
            }
            else
            {
                cout << "Paged Allocs: " << psysPoolTag->PagedAllocs << endl;
                cout << "Paged Frees: " << psysPoolTag->PagedFrees << endl;
                cout << "Paged Pool Bytes Used: " << psysPoolTag->PagedUsed << endl;
            }
     
            psysPoolTag++;
            cout << endl << "-------------------------------" << endl;
            cout << endl << "-------------------------------" << endl << endl;
     
        }
     
        if (InfoBuf != nullptr)
            delete[] InfoBuf;
     
    Exit:
        cin.get();
        return 0;
    }
    

### Defs.h

    
    
    #include <Windows.h>
     
    #define SystemPoolTagInformation (DWORD)0x16
     
    #define STATUS_SUCCESS 0
    #define STATUS_INFO_LENGTH_MISMATCH 0xC0000004
     
    typedef DWORD SYSTEM_INFORMATION_CLASS;
     
    typedef struct _SYSTEM_POOLTAG
    {
        union
        {
            UCHAR Tag[4];
            ULONG TagUlong;
        };
        ULONG PagedAllocs;
        ULONG PagedFrees;
        SIZE_T PagedUsed;
        ULONG NonPagedAllocs;
        ULONG NonPagedFrees;
        SIZE_T NonPagedUsed;
     
    }SYSTEM_POOLTAG, *PSYSTEM_POOLTAG;
     
    typedef struct _SYSTEM_POOLTAG_INFORMATION
    {
        ULONG Count;
        SYSTEM_POOLTAG TagInfo[ANYSIZE_ARRAY];
     
    }SYSTEM_POOLTAG_INFORMATION, *PSYSTEM_POOLTAG_INFORMATION;
     
     
    typedef NTSTATUS(WINAPI *_ZwQuerySystemInformation)(
        _In_      SYSTEM_INFORMATION_CLASS SystemInformationClass,
        _Inout_   PVOID                    SystemInformation,
        _In_      ULONG                    SystemInformationLength,
        _Out_opt_ PULONG                   ReturnLength
        );
    

## 目标PoolTag信息

为了更好的了解获取的`PoolTag`信息，有必要进行分析。通过搜索对`locatepoolwithtag`函数的调用，我们可以记录这些驱动程序使用的特定标签，并将它们保留在我们的列表中。我们知道任何驱动程序都可以随意使用任何标记，那么，尝试找到一些不太常见的、标准Windows内核驱动程序或对象没有使用的标记是有非常意义的。话虽如此，但这种检测特定驱动因素的方法可能会产生误报。

## PoolTag示例列表

>为了进一步证明，我们从特定的驱动程序中收集了一些PoolTag信息。

### VMWare

>vm3dmp.sys（标签：VM3D）vmci.sys（标签：CTGC，CTMM，QPMM等......）vmhgfs.sys（标签：HGCC，HGAC，HGVS，HGCD等......）vmmemctl.sys（标签：VMBL）vsock.sys（标签：vskg，vskd，vsks等...）

### Process Explorer

>procexp152.sys（标签：PEOT，PrcX等...）

### 进程监视器

>procmon23.sys（标签：Pmn）

### SYSMON

>sysmondrv.sys（标签：Sys1，Sys2，Sys3，SysA，SysD，SysE等...）

### Avast Internet Security

> aswsnx.sys（标签：'Snx'，Aw ++）（我们在第一个中使用单引号，因为它以空格字符结尾）aswsp.sys（标签：pSsA，AsDr）

## 结论

就像其他方法一样，这个方法也有优缺点。比如这种方法不容易被规避，特别是在64位Windows中，内核补丁保护（Patch
Guard）不允许我们修改内核函数等，因此可以直接挂钩`NtQuerySystemInformation`。此外，此方法不受来自用户空间进程的特定进程，文件和注册表项的访问的驱动程序的影响。所以该方法可以用于识别指纹主机。通过搜索操作系统中引入的Windows对象的特定标记，我们可以确定其主要版本。例如，通过比较不同版本的Windbg附带的`poolTag`信息`（pooltag.txt）`，在本例中为`Windows
8.1 x64`和`Windows 10 x64（Build 10.0.15063）`，我们能够找到 Windows 10中使用的`PoolTag`通过
`netio.sys`内核驱动程序，如 `Nrsd`， `Nrtr`， `Nrtw`，但不在Windows
8.1中我们后来使用两个虚拟机进行了验证，我们确实可以在Windows 10中找到至少有两个上述标签的池分配，而我们的Windows
8.1虚拟机中没有这些。话虽这么说，内核驱动程序开发使用基于分配它们的模块及其用途有意义的标记是一种常见且良好的做法。另一方面，如前所述，
`PoolTag`可以随便用，因此我们必须小心使用。最后要提到的是
`PoolTag`信息一直在变化，换句话说，内存块经常被分配和解除分配，因此我们在选择要搜索的`PoolTag`时应该记住这一点 。

 ***参考来源labs，由周大涛编译，转载请注明来自FreeBuf.COM**

