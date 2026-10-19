![](https://image.3001.net/images/20200205/1580913782_5e3ad47626e2b.png!small)

**Qiling是一款功能强大的高级代码模拟框架，该工具由[ _Unicorn引擎_](http://www.unicorn-engine.org/)驱动，并且拥有下列功能：**

> 1、跨平台支持：Windows、macOS、Linux、BSD；
>
> 2、跨架构支持：x86、x86_64、ARM、ARM64等等；
>
> 3、多文件结构支持：PE、MachO、ELF；
>
> 4、在隔离环境中模拟&沙盒系统代码；
>
> 5、提供高级API来安装和配置沙盒环境；
>
> 6、细粒度显示：允许设置多种级别的钩子（instruction/basic-block/memory-> access/exception/syscall/IO等等）；
>
> 7、允许动态修补运行中的程序代码，包括已加载的库；
>
> 8、Python框架支持，允许构建和定制安全分析工具；

## Qiling与其他模拟器对比

目前，社区有很多开源的模拟器，最接近Qiling的就是Unicorn和Qemu了。

### Qiling vs Unicorn引擎

虽然Qiling 时基于Unicorn实现的，但是它们两个完全不同：

1、Unicorn只是一个CPU模拟器，它主要针对的是模拟CPU指令。Unicorn无法识别高级概念，例如动态库、系统调用、I/O处理或类似PE、MachO或ELF这样的可执行文件格式。因此，Unicorn只能够模拟原始设备指令，无法适用于操作系统上下文场景。

2、Qiling是一个高级框架，它可以利用Unicorn来模拟CPU指令，但是它同样可以理解操作系统上下文，它集成了可执行文件格式加载器、动态链接、系统调用和I/O处理器。更重要的是，Qiling可以在不需要原生操作系统的环境下运行可执行文件源码。

### Qiling vs Qemu用户模式

Qemu用户模式跟我们的Qiling类似，它可以跨架构模拟整个可执行文件的源码。但是，Qiling的不同之处在于：

1、Qiling是一个真正的分析框架，它允许我们构建自己的动态分析工具（使用Python）。除此之外，Qemu只是一款工具，而不是一个框架。

2、Qiling可以执行动态指令，并且能够在运行时进行代码修补，这一点Qemu就无法做到了。

3、Qiling支持跨平台，但是Qemu用户模式只能在与源代码环境相同的操作系统上使用。

4、Qiling支持更多的平台，包括Windows、macOS、Linux&BSD，但Qemu用户模式只支持Linux&BSD。

## 工具安装

广大研究人员可以使用下列命令安装Qiling（注意：安装前请搭建好Python 3环境）：

    
    
    python3 setup.py install

工具使用样例

在下面的例子中，我们将演示如何使用Qiling框架来在一台Linux设备上模拟目标Windows可执行文件：

    
    
    from qiling import *
    
    # sandbox to emulate the EXE
    def my_sandbox(path, rootfs):
        # setup Qiling engine
        ql = Qiling(path, rootfs)
        # now emulate the EXE
        ql.run()
    
    if __name__ == "__main__":
        # execute Windows EXE under our rootfs
        my_sandbox(["examples/rootfs/x86_windows/bin/x86-windows-hello.exe"], "examples/rootfs/x86_windows")

在下面的例子中，我们将演示如何使用Qiling框架对Windows crackme进行动态修复，并在“Congratulation”对话框中显示相关信息：

    
    
    from qiling import *
    
    def force_call_dialog_func(ql):
        # get DialogFunc address
        lpDialogFunc = ql.unpack32(ql.mem_read(ql.sp - 0x8, 4))
        # setup stack memory for DialogFunc
        ql.stack_push(0)
        ql.stack_push(1001)
        ql.stack_push(273)
        ql.stack_push(0)
        ql.stack_push(0x0401018)
        # force EIP to DialogFunc
        ql.pc = lpDialogFunc
    
    
    def my_sandbox(path, rootfs):
        ql = Qiling(path, rootfs)
        # NOP out some code
        ql.patch(0x004010B5, b'\x90\x90')
        ql.patch(0x004010CD, b'\x90\x90')
        ql.patch(0x0040110B, b'\x90\x90')
        ql.patch(0x00401112, b'\x90\x90')
        # hook at an address with a callback
        ql.hook_address(0x00401016, force_call_dialog_func)
        ql.run()
    
    
    if __name__ == "__main__":
        my_sandbox(["rootfs/x86_windows/bin/Easy_CrackMe.exe"], "rootfs/x86_windows")

## 工具演示视频

### Qiling DEMO 1：动态修复Windows crackme

视频地址：<https://v.qq.com/x/page/m3061ozrz3s.html>

### Wannacry DEMO：如何使用Qiling分析Wannacry恶意软件

视频地址：<https://v.qq.com/x/page/h3061l4445g.html>

## Qltool

Qiling还提供了一个名为qltool的强大工具，它可以帮助我们快速模拟出目标Shellcode或可执行文件的源码。

下面这条命令可以直接对目标源码进行模拟：

    
    
    $ ./qltool run -f examples/rootfs/arm_linux/bin/arm32-hello --rootfs examples/rootfs/arm_linux/

如需模拟Shellcode，则需要运行下列命令：

    
    
    $ ./qltool shellcode --os linux --arch x86 --asm -f examples/shellcodes/lin32_execve.asm

## 许可证协议

Qiling项目的开发与发布遵循[
_GPLv2开源许可证协议_](https://github.com/qilingframework/qiling/blob/master/COPYING)。

## 项目地址

> Qiling：【[ _GitHub传送门_](https://github.com/qilingframework/qiling)】

 *** 参考来源：[
_qilingframework_](https://github.com/qilingframework/qiling)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

