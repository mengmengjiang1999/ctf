![](https://image.3001.net/images/20230615/1686819982_648ad48e27744b89aae9b.png!small)

## 关于Acheron

Acheron是一款真的Go程序的安全产品绕过工具，该工具受到了[
_SysWhisper3_](https://github.com/klezVirus/SysWhispers3)/[
_FreshyCalls_](https://github.com/crummie5/FreshyCalls)/[
_RecycledGate_](https://github.com/thefLink/RecycledGate)等代码库的启发，其绝大部分功能都采用了Golang来实现。

Acheron工具可以向Golang程序中添加间接系统调用的能力，并以此来绕过使用用户模式钩子和[
_指令回调_](https://winternl.com/detecting-manual-syscalls-from-user-mode/)检测的反病毒产品/EDR。

## 功能特性

> 1、不需要任何其他的依赖组件；
>
> 2、基于纯Go语言或Go程序集开发；
>
> 3、支持自定义字符串加密和哈希函数以对抗静态代码分析；

## 工具运行机制

当创建一个新的系统调用代理实例时，工具将执行下列操作步骤：

> 1、遍历PEB并检索内存中ntdll.dll的基地址；
>
> 2、解析导出目录并检索每一个导出函数的地址；
>
> 3、计算每一个Zw*函数的系统服务数量；
>
> 4、枚举ntdll.dll中干净的syscall;ret工具；
>
> 5、创建代理实例，用于发送间接/直接系统调用；

## 工具下载

由于该工具基于Golang开发，因此我们首先需要在本地设备上安装并配置好Golang环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/f1zm0/acheron.git

或者使用go get命令来下载Acheron：

    
    
    go get -u github.com/f1zm0/acheron

## 工具使用

下载完成后，我们只需要在代码中调用acheron.New()来创建一个系统调用代理实例，并使用acheron.Syscall()来针对Nt*
API发送间接系统调用即可。

 **最简化样例：**

    
    
    package main
    
     
    
    import (
    
        "fmt"
    
        "unsafe"
    
     
    
        "github.com/f1zm0/acheron"
    
    )
    
     
    
    func main() {
    
        var (
    
            baseAddr uintptr
    
            hSelf = uintptr(0xffffffffffffffff)
    
        )
    
     
    
        // creates Acheron instance, resolves SSNs, collects clean trampolines in ntdll.dlll, etc.
    
        ach, err := acheron.New()
    
        if err != nil {
    
            panic(err)
    
        }
    
     
    
        // indirect syscall for NtAllocateVirtualMemory
    
        s1 := ach.HashString("NtAllocateVirtualMemory")
    
        if retcode, err := ach.Syscall(
    
            s1,                                     // function name hash
    
            hSelf,                                  // arg1: _In_     HANDLE ProcessHandle,
    
            uintptr(unsafe.Pointer(&baseAddr)),     // arg2: _Inout_  PVOID *BaseAddress,
    
            uintptr(unsafe.Pointer(nil)),           // arg3: _In_     ULONG_PTR ZeroBits,
    
            0x1000,                                 // arg4: _Inout_  PSIZE_T RegionSize,
    
            windows.MEM_COMMIT|windows.MEM_RESERVE, // arg5: _In_     ULONG AllocationType,
    
            windows.PAGE_EXECUTE_READWRITE,         // arg6: _In_     ULONG Protect
    
        ); err != nil {
    
            panic(err)
    
        }
    
        fmt.Printf(
    
            "allocated memory with NtAllocateVirtualMemory (status: 0x%x)\n",
    
            retcode,
    
        )
    
     
    
        // ...
    
    }

## 工具使用样例

 ** **样例****

|

 ** **描述****  
  
---|---  
  
[sc_inject](https://github.com/f1zm0/acheron/blob/main/examples/sc_inject)

|

进程注入PoC，支持直接/间接系统调用  
  
[process_snapshot](https://github.com/f1zm0/acheron/blob/main/examples/process_snapshot)

|

使用间接系统调用获取进程快照  
  
[custom_hashfunc](https://github.com/f1zm0/acheron/blob/main/examples/custom_hashfunc)

|

自定义加密/哈希函数使用样例  
  
## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/f1zm0/acheron/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Acheron** ：【[ _GitHub传送门_](https://github.com/f1zm0/acheron)】

## 参考资料

> [
> _https://github.com/klezVirus/SysWhispers3_](https://github.com/klezVirus/SysWhispers3)
>
> [
> _https://github.com/crummie5/FreshyCalls_](https://github.com/crummie5/FreshyCalls)
>
> [
> _https://github.com/thefLink/RecycledGate_](https://github.com/thefLink/RecycledGate)
>
> [ _https://winternl.com/detecting-manual-syscalls-from-user-> mode/_](https://winternl.com/detecting-manual-syscalls-from-user-mode/)
>
> [
> _https://www.usenix.org/legacy/events/vee06/full_papers/p154-bhansali.pdf_](https://www.usenix.org/legacy/events/vee06/full_papers/p154-bhansali.pdf)
>
> [ _https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-> low_](https://redops.at/en/blog/direct-syscalls-a-journey-from-high-to-low)

