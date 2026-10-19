![](https://image.3001.net/images/20230605/1685950929_647d91d1010029756e6b7.jpeg!small)

## 关于SilentMoonwalk

SilentMoonwalk是一个针对完整动态调用栈欺骗技术的PoC实现，该工具所实现的技术可以帮助广大研究人员从调用栈中移除原始的调用者信息，并使用ROP对控制流执行去同步化解绑操作。

## 工具运行机制

该工具使用了去同步栈来完全隐藏原始调用栈，同时从中删除了EXE镜像库。随后，该工具还会调用ROP工具来恢复原始堆栈。在代码中，这个过程会在一个循环中重复10次，以证明其稳定性。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/klezVirus/SilentMoonwalk.git

## 工具构建

接下来，使用Visual Studio加载项目并构建项目代码即可。

如需构建PoC项目代码，请确保检查以下几个条件：

> 1、禁用GS（/GS-）；
>
> 2、禁用代码优化（/Od）；
>
> 3、禁用整个程序优化（移除/GL）；
>
> 4、禁用大小和速度首选项（移除/Os、/Ot）；
>
> 5、启用intrinsic（/Oi）；

## 工具使用

在代码库中，我们可以找到一些关于运行时函数审计的功能代码，可以帮助广大研究人员分析运行时函数条目：

    
    
    UnwindInspector.exe -h
    
     
    
     Unwind Inspector v0.100000
    
     
    
     Mandatory args:
    
       -m <module>: Target DLL
    
       -f <function>: Target Function
    
       -a <function-address>: Target Function Address

样例输出：

    
    
    UnwindInspector.exe -m kernelbase -a 0x7FFAAE12182C
    
    [*] Using function address 0x7ffaae12182c
    
     
    
      Runtime Function (0x000000000000182C, 0x00000000000019ED)
    
      Unwind Info Address: 0x000000000026AA88
    
        Version: 0
    
        Ver + Flags: 00000000
    
        SizeOfProlog: 0x1f
    
        CountOfCodes: 0xc
    
        FrameRegister: 0x0
    
        FrameOffset: 0x0
    
        UnwindCodes:
    
        [00h] Frame: 0x741f - 0x04  - UWOP_SAVE_NONVOL     (RDI, 0x001f)
    
        [01h] Frame: 0x0015 - 0x00  - UWOP_PUSH_NONVOL     (RAX, 0x0015)
    
        [02h] Frame: 0x641f - 0x04  - UWOP_SAVE_NONVOL     (RSI, 0x001f)
    
        [03h] Frame: 0x0014 - 0x00  - UWOP_PUSH_NONVOL     (RAX, 0x0014)
    
        [04h] Frame: 0x341f - 0x04  - UWOP_SAVE_NONVOL     (RBX, 0x001f)
    
        [05h] Frame: 0x0012 - 0x00  - UWOP_PUSH_NONVOL     (RAX, 0x0012)
    
        [06h] Frame: 0xb21f - 0x02  - UWOP_ALLOC_SMALL     (R11, 0x001f)
    
        [07h] Frame: 0xf018 - 0x00  - UWOP_PUSH_NONVOL     (R15, 0x0018)
    
        [08h] Frame: 0xe016 - 0x00  - UWOP_PUSH_NONVOL     (R14, 0x0016)
    
        [09h] Frame: 0xd014 - 0x00  - UWOP_PUSH_NONVOL     (R13, 0x0014)
    
        [0ah] Frame: 0xc012 - 0x00  - UWOP_PUSH_NONVOL     (R12, 0x0012)
    
        [0bh] Frame: 0x5010 - 0x00  - UWOP_PUSH_NONVOL     (RBP, 0x0010)

## 工具运行截图

![](https://image.3001.net/images/20230605/1685951164_647d92bcb38b7aca2ac47.png!small)![](https://image.3001.net/images/20230605/1685951172_647d92c4665960e241fc9.png!small)

![](https://image.3001.net/images/20230605/1685951180_647d92ccede7ecf3ead07.png!small)

  

## 许可证协议

本项目的开发与发布遵循[ _BSD_
_-3-Clause_](https://github.com/klezVirus/SilentMoonwalk/blob/master/LICENSE)开源许可证协议。

## 项目地址

 **SilentMoonwalk** ：【[
_GitHub传送门_](https://github.com/klezVirus/SilentMoonwalk)】

## 参考资料

> [ _https://www.unknowncheats.me/forum/anti-cheat-bypass/268039-x64-return-> address-spoofing-source-> explanation.html_](https://www.unknowncheats.me/forum/anti-cheat-> bypass/268039-x64-return-address-spoofing-source-explanation.html)
>
> [ _https://github.com/waldo-irc/YouMayPasser_](https://github.com/waldo-> irc/YouMayPasser)
>
> [
> _https://github.com/WithSecureLabs/CallStackSpoofer/_](https://github.com/WithSecureLabs/CallStackSpoofer/)
>
> [
> _https://github.com/Kudaes/Unwinder/_](https://github.com/Kudaes/Unwinder/)

