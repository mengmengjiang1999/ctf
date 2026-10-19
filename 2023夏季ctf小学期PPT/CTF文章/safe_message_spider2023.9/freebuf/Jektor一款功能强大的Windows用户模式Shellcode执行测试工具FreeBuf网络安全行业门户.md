![](https://image.3001.net/images/20220106/1641464584_61d6c308541e96b09bf0f.jpg!small)

## 关于Jektor

Jektor是一款功能强大的Windows用户模式Shellcode执行测试工具，该工具可以帮助广大研究人员了解和测试恶意软件所使用的各种不同技术。

该工具主要针对的是Shellcode注入技术，可以演示恶意软件在目标系统上执行Shellcode时所使用的技术方法，其中包括：

> 动态解析API函数以避免IAT包含
>
> 使用未记录的NT Windows API函数
>
> 通过CreateThread执行本地Shellcode
>
> 通过CreateRemoteThread执行远程Shellcode
>
> 通过QueueUserAPC支持本地Shellcode注入
>
> 通过EnumTimeFormatsEx支持本地Shellcode注入
>
> 通过CreateFiber进行本地Shellcode注入

![](https://image.3001.net/images/20220106/1641464596_61d6c314607a77e025e16.png!small)

## 反病毒检测

在使用动态函数地址解析时，将一组NOP预挂起到Msfvenom异或加密Shellcode Payload后，可以绕过Windows Defender。

## IAT导入规避

Jektor利用了动态函数地址解析，并使用了LoadLibrary和GetProcessAddress来增加了静态分析的难度。

除此之外，很多恶意软件也不会直接调用类似VirtualAlloc这样的重要函数，这也会使得调试和通过断点转储Shellcode变得更加困难。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/FULLSHADE/Jektor.git

## 通过CreateThread实现本地Shellcode执行

在Windows上，当你想要在当前进程中创建一个新的线程，需要调用CreateThread函数，这是在一个进程中执行恶意代码或Shellcode时会使用的一个最基本的技术了。此时，我们只需要为Shellcode分配一个内存区域，然后将Shellcode移动到分配的内存区域中，并使用指向该区域地址的指针来调用CreateThread即可。调用CreateThread时，需传递lpStartAddress
参数，而该参数是一个指向由新创建线程所执行的应用程序定义函数的指针。

![](https://image.3001.net/images/20220106/1641464612_61d6c324d67a836180e8e.png!small)

## 通过EnumTimeFormatsEx实现本地Shellcode执行

EnumTimeFormatsEx是一个Windows
API函数，可以枚举提供的时间格式，能够用于执行Shellcode，因为第一个参数可以接收用户定义的指针：

    
    
    BOOL EnumTimeFormatsEx(
    
      [in]           TIMEFMT_ENUMPROCEX lpTimeFmtEnumProcEx,
    
      [in, optional] LPCWSTR            lpLocaleName,
    
      [in]           DWORD              dwFlags,
    
      [in]           LPARAM             lParam
    
    );

> 1、使用VirtualAlloc为Shellcode Payload分配本地内存。
>
> 2、使用memcpy/RtlCopyMemory将Shellcode Payload移动到新分配的内存区域。
>
> 3、将Shellcode作为EnumTimeFormatsEx的lpTimeFmtEnumProcEx参数来传递，并触发Shellcode。

## 通过QueueUserAPC实现本地Shellcode执行

> 1、使用VirtualAlloc为Shellcode分配内存缓冲区。
>
> 2、使用GetCurrentProcess获取当前进程的句柄。
>
> 3、使用WriteProcessMemory向新分配的内存区域写入Shellcode Payload。
>
> 4、使用GetCurrentThread获取当前线程的句柄。
>
> 5、将分配的内存区域以pfnAPC参数的形式提供给QueueUserAPC，并将新创建的APC程序加入队列。
>
> 6、通过调用未记录的NtTestAlert函数触发Shellcode Payload，该函数将清除当前线程的APC队列。
>
> 7、通过关闭当前线程和当前进程的句柄来执行清理任务。

![](https://image.3001.net/images/20220106/1641464637_61d6c33dea3a1ae1f4f07.png!small)

## 项目地址

 **Jektor：** 【[ _GitHub传送门_](https://github.com/FULLSHADE/Jektor)】

