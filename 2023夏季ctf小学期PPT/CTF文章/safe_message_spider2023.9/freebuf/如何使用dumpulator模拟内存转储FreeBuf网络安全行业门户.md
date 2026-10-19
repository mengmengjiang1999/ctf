![](https://image.3001.net/images/20230629/1688053930_649da8aa3cc60db7490fe.png!small)  

## 关于dumpulator

dumpulator是一款功能强大且易于使用的代码库，广大研究人员可以使用dumpulator来模拟内存转储，并将该技术用于恶意软件分析和动态代码分析等场景。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mrexodia/dumpulator.git

或者直接访问该项目的【[
_Releases页面_](https://github.com/mrexodia/dumpulator/releases/tag/v0.2.5)】下载该工具的预编译版本。

除此之外，我们也可以直接通过PyPI安装：

    
    
    python -m pip install dumpulator

然后执行安装脚本：

    
    
    python setup.py install

## 工具使用

### 调用函数

    
    
    from dumpulator import Dumpulator
    
     
    
    dp = Dumpulator("StringEncryptionFun_x64.dmp")
    
    temp_addr = dp.allocate(256)
    
    dp.call(0x140001000, [temp_addr, 0x140017000])
    
    decrypted = dp.read_str(temp_addr)
    
    print(f"decrypted: '{decrypted}'")

### 执行跟踪

    
    
    from dumpulator import Dumpulator
    
     
    
    dp = Dumpulator("StringEncryptionFun_x64.dmp", trace=True)
    
    dp.start(dp.regs.rip)

### 读取UTF-16字符串

    
    
    from dumpulator import Dumpulator
    
     
    
    dp = Dumpulator("my.dmp")
    
    buf = dp.call(0x140001000)
    
    dp.read_str(buf, encoding='utf-16')

### 自定义syscall实现

我们可以使用@syscall修饰符来实现syscall：

    
    
    from dumpulator import *
    
    from dumpulator.native import *
    
    from dumpulator.handles import *
    
    from dumpulator.memory import *
    
     
    
    @syscall
    
    def ZwQueryVolumeInformationFile(dp: Dumpulator,
    
                                     FileHandle: HANDLE,
    
                                     IoStatusBlock: P[IO_STATUS_BLOCK],
    
                                     FsInformation: PVOID,
    
                                     Length: ULONG,
    
                                     FsInformationClass: FSINFOCLASS
    
                                     ):
    
    return STATUS_NOT_IMPLEMENTED

所有的syscall函数原型都可以在[ _ntsyscalls_
_.py_](https://github.com/mrexodia/dumpulator/blob/main/src/dumpulator/ntsyscalls.py)中找到。

如需给一个现有的syscall实现一个钩子，可以参照下列例子：

    
    
    import dumpulator.ntsyscalls as ntsyscalls
    
     
    
    @syscall
    
    def ZwOpenProcess(dp: Dumpulator,
    
                      ProcessHandle: Annotated[P[HANDLE], SAL("_Out_")],
    
                      DesiredAccess: Annotated[ACCESS_MASK, SAL("_In_")],
    
                      ObjectAttributes: Annotated[P[OBJECT_ATTRIBUTES], SAL("_In_")],
    
                      ClientId: Annotated[P[CLIENT_ID], SAL("_In_opt_")]
    
                      ):
    
        process_id = ClientId.read_ptr()
    
        assert process_id == dp.parent_process_id
    
        ProcessHandle.write_ptr(0x1337)
    
        return STATUS_SUCCESS
    
     
    
    @syscall
    
    def ZwQueryInformationProcess(dp: Dumpulator,
    
                                  ProcessHandle: Annotated[HANDLE, SAL("_In_")],
    
                                  ProcessInformationClass: Annotated[PROCESSINFOCLASS, SAL("_In_")],
    
                                  ProcessInformation: Annotated[PVOID, SAL("_Out_writes_bytes_(ProcessInformationLength)")],
    
                                  ProcessInformationLength: Annotated[ULONG, SAL("_In_")],
    
                                  ReturnLength: Annotated[P[ULONG], SAL("_Out_opt_")]
    
                                  ):
    
        if ProcessInformationClass == PROCESSINFOCLASS.ProcessImageFileNameWin32:
    
            if ProcessHandle == dp.NtCurrentProcess():
    
                main_module = dp.modules[dp.modules.main]
    
                image_path = main_module.path
    
            elif ProcessHandle == 0x1337:
    
                image_path = R"C:\Windows\explorer.exe"
    
            else:
    
                raise NotImplementedError()
    
            buffer = UNICODE_STRING.create_buffer(image_path, ProcessInformation)
    
            assert ProcessInformationLength >= len(buffer)
    
            if ReturnLength.ptr:
    
                dp.write_ulong(ReturnLength.ptr, len(buffer))
    
            ProcessInformation.write(buffer)
    
            return STATUS_SUCCESS
    
        return ntsyscalls.ZwQueryInformationProcess(dp,
    
                                                    ProcessHandle,
    
                                                    ProcessInformationClass,
    
                                                    ProcessInformation,
    
                                                    ProcessInformationLength,
    
                                                    ReturnLength
    
                                                    )

### 自定义结构体

该工具支持声明你自己的结构体：

    
    
    from dumpulator.native import *
    
     
    
    class PROCESS_BASIC_INFORMATION(Struct):
    
        ExitStatus: ULONG
    
        PebBaseAddress: PVOID
    
        AffinityMask: KAFFINITY
    
        BasePriority: KPRIORITY
    
        UniqueProcessId: ULONG_PTR
    
    InheritedFromUniqueProcessId: ULONG_PTR

如需初始化这些结构体，则需要使用到一个Dumpulator实例：

    
    
    pbi = PROCESS_BASIC_INFORMATION(dp)
    
    assert ProcessInformationLength == Struct.sizeof(pbi)
    
    pbi.ExitStatus = 259  # STILL_ACTIVE
    
    pbi.PebBaseAddress = dp.peb
    
    pbi.AffinityMask = 0xFFFF
    
    pbi.BasePriority = 8
    
    pbi.UniqueProcessId = dp.process_id
    
    pbi.InheritedFromUniqueProcessId = dp.parent_process_id
    
    ProcessInformation.write(bytes(pbi))
    
    if ReturnLength.ptr:
    
        dp.write_ulong(ReturnLength.ptr, Struct.sizeof(pbi))
    
    return STATUS_SUCCESS

如果你将一个指针值作为第二个参数传递，那么结构体将会从内存中被读取。我们可以使用myptr:
P[MY_STRUCT]声明指针并使用myptr[0]来引用他们。

### 收集转储

从2022年10月10日起[ _minidump_](https://help.x64dbg.com/en/latest/commands/memory-operations/minidump.html)命令就整合进了x64dbg中，如需创建一个转储，可以暂停工具的执行，并运行下列命令命令。

    
    
    MiniDump my.dmp

## 许可证协议

本项目的开发与发布遵循[ _BSL_
_-1.0_](https://github.com/mrexodia/dumpulator/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **dumpulator** ：【[ _GitHub传送门_](https://github.com/mrexodia/dumpulator)】

## 参考资料

> [ _https://oalabs.openanalysis.net/_](https://oalabs.openanalysis.net/)
>
> [ _https://youtu.be/4Pfu98Xx9Yo_](https://youtu.be/4Pfu98Xx9Yo)
>
> [ _https://rioasmara.com/2022/07/23/emulating-malware-with-> dumpulator/_](https://rioasmara.com/2022/07/23/emulating-malware-with-> dumpulator/)
>
> [
> _https://research.openanalysis.net/emotet/emulation/config/dumpulator/malware/2022/05/19/emotet_x64_emulation.html_](https://research.openanalysis.net/emotet/emulation/config/dumpulator/malware/2022/05/19/emotet_x64_emulation.html)
>
> [ _https://research.checkpoint.com/2022/native-function-and-assembly-code-> invocation/_](https://research.checkpoint.com/2022/native-function-and-> assembly-code-invocation/)
>
> [
> _https://research.openanalysis.net/guloader/emulation/dumpulator/veh/exceptions/2023/01/15/dumpulator-> veh.html_](https://research.openanalysis.net/guloader/emulation/dumpulator/veh/exceptions/2023/01/15/dumpulator-> veh.html)
>
> [
> _https://research.openanalysis.net/rhadamanthys/config/ida/shifted%20pointers/peb/_list_entry/_ldr_data_table_entry/2023/01/19/rhadamanthys.html_](https://research.openanalysis.net/rhadamanthys/config/ida/shifted%20pointers/peb/_list_entry/_ldr_data_table_entry/2023/01/19/rhadamanthys.html)
>
> [ _https://kienmanowar.wordpress.com/2023/05/22/case-study-decrypt-strings-> using-dumpulator/_](https://kienmanowar.wordpress.com/2023/05/22/case-study-> decrypt-strings-using-dumpulator/)

