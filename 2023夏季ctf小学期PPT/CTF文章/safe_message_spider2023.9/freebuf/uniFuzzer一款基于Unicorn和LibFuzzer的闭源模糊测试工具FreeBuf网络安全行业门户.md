![](https://image.3001.net/images/20191014/1571056667_5da46c1b5448c.png!small)

##  uniFuzzer

 **uniFuzzer是一款基于[Unicorn](https://github.com/unicorn-engine/unicorn)和LibFuzzer的闭源模糊测试工具，该工具当前支持对ARM/MIPS架构的32位LSB
ELF文件进行模糊测试，而这样的系统架构和平台一般常见于物联网设备上。因此，广大研究人员可以利用uniFuzzer来对物联网设备进行模糊测试。**

##  背景知识

###  Unicorn

提到Unicorn，就不得不说起QEMU。QEMU是一款开源的虚拟机，可以模拟运行多种CPU架构的程序或系统。而Unicorn正是基于QEMU，它提取了QEMU中与CPU模拟相关的核心代码，并在外层进行了包装，提供了多种语言的API接口。

因此，Unicorn的优点很明显。相比QEMU来说，用户可以通过丰富的接口，灵活地调用CPU模拟功能，对任意代码片段进行模拟执行。不过，我们在使用过程中，也发现Unicorn存在了一些不足，最主要的就是Unicorn其实还不是很稳定、完善，存在了大量的坑（可以看Github上的issue），而且似乎作者也没有短期内要填完这些坑的打算。另一方面，由于还有较多的坑，导致Unicorn底层QEMU代码的更新似乎也没有纳入计划：Unicorn最新的release是2017年的1.0.1版本，这是基于QEMU
2的，然而今年QEMU已经发布到QEMU 4了。

不过，虽然存在着坑比较多、QEMU版本比较旧的问题，对我们的模拟执行fuzzing来说其实还好。前者可以在使用过程中用一些临时方法先填上（后面会举一个例子）。后者的影响主要是不支持一些新的架构和指令，这对于许多IoT设备来说问题并不大；而旧版本QEMU存在的安全漏洞，主要也是和驱动相关，而Unicorn并没有包含QEMU的驱动，所以基本不受这些漏洞的影响。

###  QEMU

关于QEMU的CPU模拟原理，读者可以在网上搜到一些专门的介绍，例如这篇。大致来说，QEMU是通过引入一层中间语言，TCG，来实现在主机上模拟执行不同架构的代码。例如，如果在x86服务器上模拟MIPS的代码，QEMU会先以基本块（Basic
Block）为单位，将MIPS指令经由TCG这一层翻译成x86代码，得到TB(Translation Block)，最终在主机上执行。

而为了提高模拟运行的效率，QEMU还加入了TB缓存和链接机制。通过缓存翻译完成的TB，减少了下次执行时的翻译开销，这即就是Unicorn所说的JIT。而TB链接机制，则是把原始代码基本块之间的跳转关系，映射到TB之间，从而尽可能地减少了查找缓存的次数和相关的上下文切换。

值得一提的是，Unicorn所提供的hook功能，就是在目标代码翻译成TCG时，插入相关的TCG指令，从而在最终翻译得到的TB中，于指定位置处回调hook函数。而由于TCG指令和架构无关，因此添加的TCG指令可以直接适用于不同架构。

###  LibFuzzer

LibFuzzer应该许多人都不陌生，这是LLVM项目中内置的一款fuzzing工具，相比我们之前介绍过的AFL，LibFuzzer具有以下优点：

> 1\. 灵活：通过实现接口的方式使用，可以对任意函数进行fuzzing
>
> 2\. 高效：在同一进程中进行fuzzing，无需大量fork()进程
>
> 3\. 便捷：提供了API接口，便于定制化和集成

而且，和AFL一样，LibFuzzer也是基于代码覆盖率来引导变异输入的，因此fuzzing的效率很高。不过，这两者都需要通过编译时插桩的方式，来实现代码覆盖率的跟踪，所以必须要有目标的源代码。接下来，在uniFuzzer的原理中，我们会介绍如何结合Unicorn和LibFuzzer的功能，对闭源程序进行代码覆盖率的跟踪反馈。

##  功能介绍

> 1、项目构建方便，简而易用；
>
> 2、可针对指定函数或代码段进行模糊测试；
>
> 3、使用了基于代码覆盖的模糊测试算法，效率可观；
>
> 4、依赖自解析和加载自动化；
>
> 5、通过PRELOAD覆盖库函数；

##  工具下载

广大用户可以使用git命令直接从该项目的GitHub库拷贝至本地：

    
    
    git clone https://github.com/PAGalaxyLab/uniFuzzer.git

##  项目构建

1、对目标代码进行逆向分析，并寻找目标函数进行模糊测试；

2、在callback目录中创建一个.c文件，其中需包含下列回调：

> void onLibLoad(const char *libName, void *baseAddr, void
> *ucBaseAddr)：每当独立库加载进Unicorn时，便会调用该方法。
>
> int uniFuzzerInit(uc_engine *uc)：在Unicorn加载完所有的源码之后，便会调用这个方法，堆、栈和寄存器均在这里设置。
>
> int uniFuzzerBeforeExec(uc_engine *uc, const uint8_t *data, size_t
> len)：在每轮模糊测试执行之前该方法都会被调用。
>
> int uniFuzzerAfterExec(uc_engine *uc)：在每轮模糊测试执行之后该方法都会被调用。

3、运行make命令，并获取uf模糊测试工具；

##  工具运行

uniFuzzer使用了下列环境变量作为参数：

> UF_TARGET：目标ELF文件的路径；
>
> UF_PRELOAD：预加载库的路径，请确保目标代码库的架构跟目标设备相同；
>
> UF_LIBPATH：所要使用的依赖库路径，使用“:”作为多个路径的分隔符；

广大研究人员可以使用下列命令开始对目标设备进行模糊测试：

    
    
    UF_TARGET=<target> [UF_PRELOAD=<preload>] UF_LIBPATH=<libPath> ./uf

##  工具演示

下面给出的是该工具的一些基础演示样例，demo中包含下列文件：

> 1、demo-vuln.c：这个文件是模糊测试的测试目标，其中包含一个名为vuln()的简单函数，该函数存在堆栈溢出漏洞。
>
> 2、demo-> libcpreload.c：该文件用于设置PRELOAD钩子，它定义了一个空的printf()函数以及一个简化了的malloc()/free()函数。
>
> 3、callback/demo-callback.c：为了对demo中的vuln()函数进行模糊测试，该文件定义了一些必要的回调函数。

首先，为mipsel安装gcc（Debian平台：gcc-mipsel-linux-gnu包）以构建demo：

    
    
    # the target binary
    
        # '-Xlinker --hash-style=sysv' tells gcc to use 'DT_HASH' instead of 'DT_GNU_HASH' for symbol lookup
    
        # since currently uniFuzzer does not support 'DT_GNU_HASH'
    
        mipsel-linux-gnu-gcc demo-vuln.c -Xlinker --hash-style=sysv -no-pie -o demo-vuln
    
        # the preload library
    
        mipsel-linux-gnu-gcc -shared -fPIC -nostdlib -Xlinker --hash-style=sysv demo-libcpreload.c -o demo-libcpreload.so

或者，你也可以使用文件demo-vuln和demo-libcpreload.so，同样可以使用上述命令编译。

接下来，使用make命令构建uniFuzzer，如果你自行编译了MIPS
demo，那么某些地址可能会跟我们提供给大家的预编译demo有些不同，我们需要相应地更新demo-callback.c中的参数。

最后，确保MIPS的libc库已配置完毕。在Debian平台上，安装完成libc6-mipsel-cross包后，libc库就可以在/usr/mipsel-linux-gnu/lib/中找到了。此时的UF_LIBPATH值应为：

    
    
    UF_TARGET=<path to demo-vuln> UF_PRELOAD=<path to demo-libcpreload.so> UF_LIBPATH=<lib path for MIPS> ./uf

##  项目地址

> uniFuzzer：【[GitHub传送门](https://github.com/PAGalaxyLab/uniFuzzer)】

 ***
参考来源：[PAGalaxyLab](https://github.com/PAGalaxyLab/uniFuzzer)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

