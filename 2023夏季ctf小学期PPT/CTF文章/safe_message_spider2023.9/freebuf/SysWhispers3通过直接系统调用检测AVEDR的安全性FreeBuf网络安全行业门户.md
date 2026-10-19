![](https://image.3001.net/images/20220331/1648732229_6245a8454f375c9a7b631.jpeg!small)

## 关于SysWhispers3

SysWhispers3是一款功能强大的AV/EDR安全检测工具，该工具可以生成能够发起直接系统调用的Header或ASM文件植入程序，并通过这些程序来尝试绕过AV/EDR，以检测目标AV/EDR的安全性能。

AV和EDR等安全产品通常会在用户模式API函数中放置钩子，以分析目标应用程序的执行流，从而检查出潜在的恶意活动。

SysWhispers3构建在SysWhispers2之上，支持生成一些分析模式，而这些模式可以包含在签名中，或可以帮助广大研究人员在运行时检测到某些恶意行为。除此之外，该工具还集成了大量实用功能以绕过这类形式的检测。

## 工具安装

该工具基于Python开发，因此我们需要在本地设备上安装并配置好Python环境。

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    C:\> git clone https://github.com/klezVirus/SysWhispers3.git

然后使用下列命令查看该工具的帮助信息：

    
    
    C:\> cd SysWhispers3
    
    C:\> python .\syswhispers.py --help

## 工具使用

下面给出的是该工具的帮助信息以及支持的选项参数：

    
    
    C:\>python syswhispers.py -h
    
     
    
    usage: syswhispers.py [-h] [-p PRESET] [-a {x86,x64}] [-m {embedded,egg_hunter,jumper,jumper_randomized}] [-f FUNCTIONS] -o OUT_FILE [--int2eh] [--wow64] [-v] [-d]
    
     
    
    SysWhispers3 - SysWhispers on steroids
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -p PRESET, --preset PRESET
    
                            Preset ("all", "common")
    
      -a {x86,x64}, --arch {x86,x64}
    
                            Architecture
    
      -c {msvc,mingw,all}, --compiler {msvc,mingw,all}
    
                            Compiler
    
      -m {embedded,egg_hunter,jumper,jumper_randomized}, --method {embedded,egg_hunter,jumper,jumper_randomized}
    
                            Syscall recovery method
    
      -f FUNCTIONS, --functions FUNCTIONS
    
                            Comma-separated functions
    
      -o OUT_FILE, --out-file OUT_FILE
    
                            Output basename (w/o extension)
    
      --int2eh              Use the old `int 2eh` instruction in place of `syscall`
    
      --wow64               Use Wow64 to run x86 on x64 (only usable with x86 architecture)
    
      -v, --verbose         Enable debug output
    
      -d, --debug           Enable syscall debug (insert software breakpoint)

### 命令行使用

导出支持所有Windows版本的兼容性功能：

    
    
    py .\syswhispers.py --preset all -o syscalls_all

仅导出常用功能：

    
    
    py .\syswhispers.py --preset common -o syscalls_common

导出支持所有版本的NtProtectVirtualMemory 和NtWriteVirtualMemory：

    
    
    py .\syswhispers.py --functions NtProtectVirtualMemory,NtWriteVirtualMemory -o syscalls_mem

常规32位模式：

    
    
    py .\syswhispers.py --preset all -o syscalls_all -m jumper --arch x86

常规32位模式（使用WOW64）:

    
    
    py .\syswhispers.py --functions NtProtectVirtualMemory,NtWriteVirtualMemory -o syscalls_mem --arch x86 --wow64

绕过“mark of the syscall”（常用）：

    
    
    py .\syswhispers.py --preset common -o syscalls_common -m jumper

使用MinGW作为编译器绕过动态RIP验证：

    
    
    py .\syswhispers.py --preset all -o syscalls_all -m jumper -c mingw

### 脚本输出结果

    
    
    PS C:\Projects\SysWhispers2> py .\syswhispers.py --preset common --out-file temp\syscalls_common -v
    
                                                           
    
                      .                         ,--.
    
    ,-. . . ,-. . , , |-. o ,-. ,-. ,-. ,-. ,-.  __/
    
    `-. | | `-. |/|/  | | | `-. | | |-' |   `-. .  \
    
    `-' `-| `-' ' '   ' ' ' `-' |-' `-' '   `-'  '''
    
         /|                     |  @Jackson_T
    
        `-'                     '  @modexpblog, 2021
    
     
    
                          Edits by @klezVirus,  2022
    
    SysWhispers3: Why call the kernel when you can whisper?
    
     
    
     
    
    Common functions selected.
    
     
    
    Complete! Files written to:
    
            temp\syscalls_common.h
    
            temp\syscalls_common.c
    
            temp\syscalls_common_.asm
    
    Press a key to continue...

## 导入至Visual Studio

> 1、将生成的H/C/ASM文件拷贝到项目目录中；
>
> 2、在Visual Studio中，点击“Project->Build Customizations...”，然后启用MASM；
>
> 3、在“Solution Exlorer”中，将.h和.c/.asm文件分别以Header和源文件的形式添加到项目中；
>
> 4、点击ASM文件的属性，将“Item Type”设置为“Microsoft Macro Assembler”；

## 在Visual Studio外部编译

### Windows

 **64位Makefile：**

    
    
    Makefile.msvc
    
    
    OPTIONS = -Zp8 -c -nologo -Gy -Os -O1 -GR- -EHa -Oi -GS-    
    LIBS = libvcruntime.lib libcmt.lib ucrt.lib kernel32.lib
    
     
    
    program:
    
      ML64 /c syscalls-asm.x64.asm /link /NODEFAULTLIB /RELEASE /MACHINE:X64
    
      cl.exe $(OPTIONS) syscalls.c  program.c
    
      link.exe /OUT:program.x64.exe -nologo $(LIBS) /MACHINE:X64 -subsystem:console -nodefaultlib syscalls-asm.x64.obj syscalls.obj program.obj

 **32位Makefile：**

    
    
    Makefile.msvc
    
    
    OPTIONS = -Zp8 -c -nologo -Gy -Os -O1 -GR- -EHa -Oi -GS-    
    LIBS = libvcruntime.lib libcmt.lib ucrt.lib kernel32.lib
    
     
    
    program:
    
      ML /c syscalls-asm.x86.asm /link /NODEFAULTLIB /RELEASE /MACHINE:X86
    
      cl.exe $(OPTIONS) syscalls.c  program.c
    
      link.exe /OUT:program.x86.exe -nologo $(LIBS) /MACHINE:X86 -subsystem:console -nodefaultlib syscalls-asm.x86.obj syscalls.obj program.obj

 **nmake编译：**

    
    
    nmake -f Makefile.msvc

### Linux

 **32位和64位Makefile：**

    
    
    Makefile.mingw
    
    
    CC_x64 := x86_64-w64-mingw32-gcc
    
    CC_x86 := i686-w64-mingw32-gcc
    
    OPTIONS := -masm=intel -Wall
    
     
    
    program:
    
      $(CC_x64) syscalls.c program.c -o program.x64.exe $(OPTIONS)
    
      $(CC_x86) syscalls.c program.c -o program.x86.exe $(OPTIONS)

 **make编译：**

    
    
    make -f Makefile.mingw

## 许可证协议

本项目的开发与发布遵循[ _Apache_ _-2_ _._
_0_](https://github.com/klezVirus/SysWhispers3/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **SysWhispers：** 【[ _GitHub传送门_](https://github.com/klezVirus/SysWhispers3)】

## 参考资料

> [
> _https://github.com/klezVirus/inceptor_](https://github.com/klezVirus/inceptor)
>
> [
> _https://github.com/jthuraisamy/SysWhispers2_](https://github.com/jthuraisamy/SysWhispers2)
>
> [
> _https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/_](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/)

