![](https://image.3001.net/images/20220324/1648129502_623c75deb121e7fab6b31.png!small)

## 关于RefleXXion

RefleXXion是一款针对用户模式钩子的安全研究工具，该工具可以通过绕过AV、EPP和EDR等安全解决方案使用的用户模式钩子，来研究安全解决方案的安全性。

## 工具运行机制

该工具首先会收集在LdrpThunkSignature数组中寻找到的NtOpenFile、NtCreateSection、NtOpenSection和NtMapViewOfSection的系统调用编号。接下来，广大研究人员就可以选择使用两种方法来尝试绕过用户模式钩子了。

### 技术一

将NTDLL作为文件从“C:\Windows\System32\ntdll.dll”路径中读取出来。经过解析之后，内存中已加载的NTDLL（执行挂钩的地方）的.TEXT字段将会被替换为干净NTDLL文件的.TEXT字段内容。

### 技术二

将NTDLL从KnownDll（\KnownDlls\ntdll.dll）中以字段形式读取出来（因为KnownDll中的DLL文件是以字段形式缓存的）。经过解析之后，内存中已加载的NTDLL（执行挂钩的地方）的.TEXT字段将会被替换为干净NTDLL文件的.TEXT字段内容。

下图中显示的是RefleXXion所采用技术的详细架构和执行流程信息：

![](https://image.3001.net/images/20220324/1648129517_623c75ed2d91e4fd9b384.png!small)

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hlldz/RefleXXion.git

## 工具使用

接下来，我们需要使用Visual Studio打开并编译项目。无论是调试模式或发布模式，该项目都支持x64体系结构。

RefleXXion-EXE解决方案将能够生成用于PoC目的的EXE，并且包含了上述技术一和技术二中定义的主要功能。请注意，你在使用其中一个技术时，一定要注释掉另一个技术的相关代码，请不要同时使用这两种技术功能。

RefleXXion-DLL解决方案可以生成用于注入至目标进程中的DLL，以实现绕过用户模式钩子。在main.cpp文件的开头部分，可以定义需要使用哪一种技术，我们可以选择其中一个并进行编译。不过别忘了，不要同时设置所有的值，只使用其中一种即可。下面给出的是配置示例：

    
    
    // Techniques configuration section
    
    #define FROM_DISK 1 // If you set it to 1, the Technique-1 will be used. For more information; https://github.com/hlldz/RefleXXion
    
    #define FROM_KNOWNDLLS 0 // If you set it to 1, the Technique-2 will be used. For more information; https://github.com/hlldz/RefleXXion

## 工具使用

当前版本的RefleXXion仅支持x64体系结构。

RefleXXion只能处理NTDLL函数，如果需要处理其他DLL（kernel32.dll、advapi32.dll等）的话，还需要对项目进行相应的配置。

RefleXXion在.TEXT字段重写过程开始的时候，只会使用RWX内存区域，针对这个过程，并不会创建一个新的内存区域。现有的内存区域为RWXed，接下来会被转换为RX：

    
    
    ULONG oldProtection;
    
    ntStatus = NtProtectVirtualMemory(NtCurrentProcess(), &lpBaseAddress, &uSize, PAGE_EXECUTE_READWRITE, &oldProtection);
    
    memcpy()...
    
    ntStatus = NtProtectVirtualMemory(NtCurrentProcess(), &lpBaseAddress, &uSize, oldProtection, &oldProtection);

我们可以从硬盘读取并将RefleXXion DLL加载到目标进程中。当然了，我们还可以使用sRDI来将RefleXXion
DLL转换为Shellcode，或者直接将RefleXXion的代码整合到我们自己的加载器或项目中。

即使NTDLL已经以文件或字段的形式重新加载到注入的内存中，它也不会保持加载状态，RefleXXion会关闭所有已打开的句柄。

## 项目地址

 **RefleXXion：** 【[ _GitHub传送门_](https://github.com/hlldz/RefleXXion)】

## 参考资料

> [ _https://stackoverflow.com/questions/6734095/how-to-get-module-handle-> from-func-ptr-in-win32_](https://stackoverflow.com/questions/6734095/how-to-> get-module-handle-from-func-ptr-in-win32)
>
> [ _https://www.mdsec.co.uk/2022/01/edr-parallel-asis-through-> analysis/_](https://www.mdsec.co.uk/2022/01/edr-parallel-asis-through-> analysis/)
>
> [ _https://blogs.blackberry.com/en/2017/10/windows-10-parallel-loading-> breakdown_](https://blogs.blackberry.com/en/2017/10/windows-10-parallel-> loading-breakdown)
>
> [ _https://stackoverflow.com/questions/42789199/why-there-are-three-> unexpected-worker-threads-when-a-win32-console-application-> s_](https://stackoverflow.com/questions/42789199/why-there-are-three-> unexpected-worker-threads-when-a-win32-console-application-s)
>
> [
> _https://github.com/slaeryan/AQUARMOURY/tree/master/Shellycoat_](https://github.com/slaeryan/AQUARMOURY/tree/master/Shellycoat)

