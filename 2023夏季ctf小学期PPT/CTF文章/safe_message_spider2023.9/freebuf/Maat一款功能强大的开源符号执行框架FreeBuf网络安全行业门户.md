## 关于Maat

Maat是一款功能强大的开源动态符号执行和二进制源码分析框架，在该工具的帮助下，广大研究人员可以轻松实现符号执行、污染分析、约束求解、二进制加载和环境模拟等操作，并利用Ghidra的sleigh库进行汇编操作。

## 工具特性

> 1、快速&便捷&灵活性：该工具能够轻松扩展至现实场景中的应用程序，基于纯C++开发，运行性能良好，运行时几乎不需要其他依赖组件。
>
> 2、用户友好：Maat提供了一个灵活性强的类似调试器的API，其功能可配置以适应许多不同的用例。和很多现代框架一样，该工具也支持嵌入Python库。
>
> 3、多架构支持：基于Ghidra的sleigh库实现了模拟功能，能够模拟多种架构的应用程序。

## 工具安装

我们可以使用下列命令来安装Maat的Python模块：

    
    
    python3 -m pip install pymaat

## Python API使用

    
    
    from maat import *
    # 针对Linux X86-32位平台创建一个符号引擎
    engine = MaatEngine(ARCH.X86, OS.LINUX)
    # 使用一个命令行参数加载代码
    engine.load("./some_binary", BIN.ELF32, args=[engine.vars.new_symbolic_buffer("password", 20)])
    # 获取当前eax值
    engine.cpu.eax
    # 读取栈顶的四个字节
    engine.mem.read(engine.cpu.esp, 4)
    # 设置一个回调来显示每一个读取的内存数据
    def show_mem_access(engine):
        mem_access = engine.info.mem_access
        print(f"Inst at {engine.info.addr} reads {mem_access.size} bytes at {mem_access.addr}")
    engine.hooks.add(EVENT.MEM_R, WHEN.BEFORE, callbacks=[show_mem_access])
    # 获取并存储快照
    snap = engine.take_snapshot()
    engine.restore_snapshot(snap)
    # 运行代码
    engine.run()

## C++ API使用

    
    
    #include "maat.hpp"
    using namespace maat;
    using namespace maat::loader;
    using namespace maat::event;
    // 针对Linux X86-32位平台创建一个符号引擎
    MaatEngine engine(Arch::Type::X86, env::OS::LINUX);
    // 使用一个20个字符的符号命令行参数在偏移量0x08001000处加载代码
    vector args{
        CmdlineArg(engine.vars->new_symbolic_buffer("some_arg", 20))
    };
    engine.load("./some_binary", Format::ELF32, 0x08001000, args, "", {}, {});
    // 获取当前eax值
    engine.cpu.ctx().get(X86::EAX);
    // 读取栈顶的四个字节
    engine.mem->read(engine.cpu.ctx().get(X86::ESP), 4)
    // 设置一个回调来显示每一个读取的内存数据
    Action show_mem_access(MaatEngine& engine)
    {
        cout << *(engine->info.mem_access);
        return Action::CONTINUE;
    }
    engine.hooks.add(Event::MEM_R, When::BEFORE, EventCallback(show_mem_access))
    // 获取并存储快照
    auto snap = engine.take_snapshot()
    engine.restore_snapshot(snap)
    // 运行代码
    maat.run()

## 工具使用样例

    
    
    from maat import *
    # 针对Linux X86-32位平台创建一个符号引擎
    engine = MaatEngine(ARCH.X86, OS.LINUX)
    # 使用一个命令行参数加载代码
    engine.load("./some_binary", BIN.ELF32, args=[engine.vars.new_symbolic_buffer("some_arg", 20)])
    # 获取当前eax值
    engine.cpu.eax
    # 读取栈顶的四个字节
    engine.mem.read(engine.cpu.esp, 4)
    # 设置一个回调来显示每一个读取的内存数据
    def show_mem_access(engine):
        mem_access = engine.info.mem_access
        print(f"Instruction at {engine.info.addr} reads {mem_access.size} bytes at {mem_access.addr}")
    engine.hooks.add(EVENT.MEM_R, WHEN.BEFORE, callbacks=[show_mem_access])
     # 获取并存储快照
    snap = engine.take_snapshot()
    engine.restore_snapshot(snap)
    # 运行代码
    engine.run()

## 许可证协议

本项目的开发与发布遵循[
_LGPLv3_](https://github.com/trailofbits/maat/blob/master/LICENCE)开源许可证协议。

## 项目地址

 **Maat：** 【[ _GitHub传送门_](https://github.com/trailofbits/maat)】

## 参考资料

> [ _https://maat.re/﻿_](https://maat.re/)

