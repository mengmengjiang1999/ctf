> 适用于白盒fuzzing

# input corpus

## 收集语料库

对于模糊测试工具而言，我们需要为其准备一个或多个起始的输入案例，这些案例通常能够很好的测试目标程序的预期功能，这样我们就可以尽可能多的覆盖目标程序。  
收集语料的来源多种多样。通常目标程序会包含一些测试用例，我们可以将其做位我们初始语料的一部分，此外互联网上也有些公开的语料库你可以收集他们做为你的需要。  
关于语料库的主动性选择，这个更多需要你对fuzzing
目标内部结构的了解。例如你当你要fuzzing的目标对随着输入的规模内存变化非常敏感，那么制作一批很大的文件与较小的文件可能是一个策略，具体是否是否有效取决于你经验、以及对目标的理解。  
此外，需要注意控制语料库的规模，太过庞大的语料库并不是好的选择，太过潘达的语料库会拖慢fuzzing的效率，尽可能用相对较小的语料覆盖更多目标代码的预期功能即可。

## 语料库唯一化

我们在上一小节最后提到一点，太过庞大的语料库会因为有太多的测试用例重复相同的路径覆盖，这会减慢fuzzing的效率。因此人们制作了一个工具，能够使语料库覆盖的路径唯一化，简单的说就算去除重复的种子输入，缩减语料库的规模，同时保持相当的测试路径效果。  
在AFL++中可以使用工具`afl-cmin`从语料库中去除不会产生新路径和覆盖氛围的重复输入，并且AFL++官方提示强烈建议我们对语料库唯一化，这是一个几乎不会产生坏处的友谊操作。  
具体的使用如下：

  1. 将收集到的所有种子文件放入一个目录中，例如 INPUTS

  2. 运行 afl-cmin：

## 字典

其实将字典放到这一个大节下面不是很合适，因为字典可以归类为一种辅助技巧，不过因为字典影响输入，所以我就将其划到这里了。  
关于是否使用字典，取决于fuzzing的目的与目标。例如fuzzing的目标是ftp服务器，我们fuzzing的目的是站在用户的视角仅能输入命令，因此我们的输入其中很大一部分可以规范到ftp提供的命令，我们更多的是通过重复测试各种命令的组合来测试目标ftp服务器在各种场景都能正确运行。  
又比如，当你fuzzing一个很复杂的目标时，它通常提供一个非常非常丰富的命令行参数，每一次运行时组合不同的参数可能会有更好的覆盖效果，因此可以将你需要启用的参数标记为字典添加进命令行参数列表中。  
最后，目标程序可能经常有常量的比较和验证，而这些环节通常会使得fuzzing停滞在此，因为模糊器的变异策略通常对应常量的猜测是非常低效的。我们可以收集目标程序中使用到的常量，定义为一个字典提供给模糊器。但目前对于AFL++来说有更好的方法解决这种需求，而无需定义字典，后面我们会介绍这些方法。

    
    
    # 模糊器默认的变异策略通常难以命中if分支为true的情况，因为input做为64位，其值的空间太大了，根本难以猜测。
    if (input = 0x1122336644587) {
    	crash();
    }
    else {
    	OK();
    }
    

# 编译前的准备

## 选择最佳的编译器

如我们上一节中谈到收集程序常量定义字典时，事实上收集常量并生成字典这个事情，在编译时完全可以顺便将其解决。没错，功能强大的编译器可以使我们在编译期间获得非常多有用的功能。对于AFL++的编译器选择，官方提供了一个简单的选择流程，如下

    
    
    +--------------------------------+
    | clang/clang++ 11+ is available | --> use LTO mode (afl-clang-lto/afl-clang-lto++)
    +--------------------------------+     see [https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.lto.md](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.lto.md)
        |
        | if not, or if the target fails with LTO afl-clang-lto/++
        |
        v
    +---------------------------------+
    | clang/clang++ 3.8+ is available | --> use LLVM mode (afl-clang-fast/afl-clang-fast++)
    +---------------------------------+     see [https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.llvm.md](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.llvm.md)
        |
        | if not, or if the target fails with LLVM afl-clang-fast/++
        |
        v
     +--------------------------------+
     | gcc 5+ is available            | -> use GCC_PLUGIN mode (afl-gcc-fast/afl-g++-fast)
     +--------------------------------+    see [https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.gcc_plugin.md](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.gcc_plugin.md) and
                                           [https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.instrument_list.md](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.instrument_list.md)
        |
        | if not, or if you do not have a gcc with plugin support
        |
        v
       use GCC mode (afl-gcc/afl-g++) (or afl-clang/afl-clang++ for clang)
    

若你的LLVM和clang版本大于等于11，那么你可以启用LLVM LTO模式，使用afl-clang-lto/afl-clang-lto++，该模式通常是最佳的。随后依次是afl-clang-fast/afl-clang-fast++和afl-gcc-fast/afl-g++-fast。  
关于为什么LTO模式通常是最佳的，其中一个原因是它解决了原版AFL中 **边碰撞** 的情况，提供了 **无碰撞的边(edge)检测**
。在原本AFL中，因为其对边(edge)的标识是随机的，对于AFL默认2^16容量来说，一旦程序足够大，边的标识会重复，这种现象就算边碰撞，它会降低模糊测试的效率。此外LTO模式会自动收集目标代码中的常量制作成为一个字典并自动启用，并且社区提供的一些有用的插件和功能很多时候是要求LLVM模式(clang-fast)甚至是LTO模式(clang-lto)。

> NOTE：此处涉及一点AFL度量覆盖率的工作原理，可以参考我注意的另一篇文章《基于覆盖率的Fuzzer和AFL》，写的很一般（逃

关于编译器的选择，如果可能直接选LTO模式即可。但你需要注意，LTO模式编译代码非常的吃内存，编译时间也会很久，尤其是启用某些Sanitizer的时候。

>
> NOTE：你的计算机配置最好至少由8核心，内存最好不低于16G。请注意8核心，16G仍然不是很够用，最好32G，16核或以上，核心越多越好。因为到时候你会编译很多不同版本的程序，不同的插件、不同的sanitizer、不同策略等等，这些不同的选项往往不能兼并到一个程序上，往往需要编译多分不同配置的程序，并你会经常patch程序再编译测试patch的效果。简言之，你会编译很多次程序，你需要足够大的内存和核心来编译目标，使得你不必经常阻塞等待编译队列和结果。

## 编译的选项

AFL++是一个非常活跃的社区，AFL++会集成社区中、互联网上一些强大的第三方插件，这些集成的插件有一些我们可以通过设置对应的编译选项启用。  
对于LTO模式（afl-clang-fast/afl-clang-lto）进行编译插桩时，可以启用下面两项比较通用的特性，主要用于优化一些固定值的比较和校验。

  * Laf-Intel：能够拆分程序中整数、字符串、浮点数等固定常量的比较和检测。考虑下面一个情况`assert x == 0x11223344`，Laf-Intel会拆分为`assert (x & 0xff) == 0x44 && ((x >> 8) & 0xff) == 0x33 ....`这样形式，每一次只会进行单字节的比较，这样AFL就可以逐个字节的猜测，每当确定一个字节时，就会发现一个新的路径，进而继续在第一个字节的基础上猜测第二个字节，如此使得模糊器可以快速猜出`0x11223344`。如果你没有自己制作好的字典、丰富的语料库，这个功能会非常有用，通常建议至少有一个AFL++实例运行Laf-Intel插件。在编译前设置如下环境使用：`export AFL_LLVM_LAF_ALL=1`

  * CmpLog：这个插件会提取程序中的比较的固定值，这些值会被用于变异算法中。功能与Laf-Intel类似，但效果通常比Laf-Intel。使用该插件需要单独编译一份cmplog版本的程序，在fuzzing时指定该cmplog版本加入到fuzzing中。具体的用法如下：

    
    
    # 编译一份常规常规版本
    cd /target/path
    CC=afl-clang-lto  make -j4
    cp ./program/path/target ./target/target.afl
    
    # 编译cmplog版本
    make clean
    export AFL_LLVM_CMPLOG=1
    CC=afl-clang-lto  make -j4
    cp ./program/path/target ./target/target.cmplog
    unset AFL_LLVM_CMPLOG
    
    # 使用cmplog， 用-c参数指定cmplog版本目标，因为cmplog回申请很多内存做映射因此我们设置
    # -m none，表示不限制afl-fuzz的内存使用。你也可以指定一个值例如 -m 1024，即1GB。
    afl-fuzz -i input -o output -c ./target.cmplog -m none -- ./target.afl @@
    

> NOTE：需要注意，两个插件并不是说谁替代谁，往往在实际fuzzing中两者都会用至少一个afl实例启用。

考虑下面两种场景。  
有时候你想要fuzzing的目标中，他自动的集成了很多第三方的库代码，他们会在编译中一并编译，而你并不想fuzzing这些第三方库来，你只想高效、快速的fuzzing目标的代码，额外的fuzzing第三方代码只会拖慢你fuzzing的效率。  
有时候你的目标会非常庞大和复杂，他们的构建往往是模块化的，有时候你只想fuzzing某几个模块。  
这上面两种情况都是我们fuzzing中很常遇见的，所幸AFL++提供了部分插桩编译的功能，即" **partial instrumentation**
"，它允许我们指定应该检测那些内容以及不应该检测那些内容，这个检测的颗粒是代码源文件、函数级两级。具体用法如下：

  * 检测指定部分。创建一个文件(`allowlist.txt`,文件名没有要求)，需要在其中指定应包含检测的源代码文件或者函数。

    * 1.在文件中每行输入一个文件名或函数

    
    
    foo.cpp # 将会匹配所有命名为foo.cpp的文件，注意是所有命名为foo.cpp的文件
    path/foo.cpp # 将会只确定的包含该路径的foo.cpp文件，不会造成意外的包含
    fun:foo_fun # 将会包含所有foo_fun函数
    
    

  *     2. 设置export AFL_LLVM_ALLOWLIST=allowlist.txt 启用选择性检测

  * 排除某些部分。与指定某些部分类似，编写一个文件然后设置环境变量`export AFL_LLVM_DENYLIST=denylist.txt`以启用，这会跳过我们文件中指定的内容。

> Note：有些小函数可能在编译期间被优化，内联到上级调用者，即类似于宏函数展开。这时将会导致指定失效！如果不想受此影响，禁用内联函数优化即可。  
>
> 此外，对于C++由于函数命名粉碎机制，你需要特别的提取粉碎后的函数名。例如函数名为`test`的函数可能会被粉碎重命名为`_Z4testv`。可以用nm提取函数名，创建一个脚本筛选出来。

## 添加Sanitizer检测更多BUG

Sanitizer最初是Google的一个开源项目，它们是一组检测工具。例如AddressSanitizer是一个内存错误检测器，可以检测诸如OOB、UAF、Double-free等到内存错误的场景。现在该项目以及成为LLVM的一部分，相对较高的gcc和clang都默认包含Sanitizer功能。  
由于AFL++基本只会检测到导致Crash的BUG，因此启用一些Sanitizer可以使得我们检测一些并不会导致Crash的错误，例如内存泄露。  
AFL++内置支持下面几种Sanitizer：

  *  **ASAN：AddressSanitizer** ，用于发现内存错误的bug，如`use-after-free`、`空指针解引用（NULL pointer dereference）`、`缓冲区溢出（buffer overruns）`、`Stack And Heap Overflow`、`Double Free/ Wild Free`、`Stack use outside scope`等。若要使用请在 **编译前** 设置环境变量`export AFL_USE_MSAN=1`。更多关于ASAN的信息参与LLVM官网对ASAN：AddressSanitizer的描述(<https://clang.llvm.org/docs/AddressSanitizer.html>)。

  *  **MSAN：MemorySanitizer** ，用于检测对未初始化内存的访问。若要启用，在 **编译前** 设置`export AFL_USE_MSAN=1`以启用。

  *  **UBSAN：Undefined** **Behavior Sanitizer** ，如其名字一般用于检测和查找C和C++语言标的未定义行为。未定义行为是语言标准没有定义的行为，编译器在编译时可能不会报错，然而这些行为导致的结果是不可预测的，对于程序而言是一个极大的隐患。请在 **编译前** ，设置`export AFL_USE_UBSAN=1`环境变量以启用。

  *  **CFISAN：Control Flow Integrity Sanitizer** ，CFI的实现有多种，它们是为了在程序出现未知的危险行为时终止程序，这些危险行为可能导致控制流劫持或破坏，用于预防ROP。在Fuzzing中，CFISAN主要用于检测类型混淆。请在 **编译前** ，设置`export AFL_USE_CFISAN=1`环境变量以启用。

  *  **TSAN：Thread Sanitizer** , 用于多线程环境下数据竞争检测。在目前，计算机通常都是多核，一个进程中通常包含多个进程，常常导致一个问题，即数据竞争。此类错误通常很难通过调试发现，出现也不稳定。当至少两个线程访问同一个变量，并且同时存在读取和写入的行为时，即发送了数据竞争，若读取在写入之后，线程可能读取到非预期的数据，可能导致严重的错误。请在 **编译前** ，设置`export AFL_USE_TSAN=1`环境变量以启用。

  *  **LSAN，Leak Sanitizer** ,用于检测程序中的内存泄露。内存泄露通常并不会导致程序crash，但它是一个不稳定的因素，可能会被利用、也可能没办法被利用，这不是一个严格意义上的漏洞。与其他Sanitizer的使用不同，需要将`__AFL_LEAK_CHECK();`添加到你想要进行内存泄露检查的目标源代码的所有区域。在编译之前启用 ，`export AFL_USE_LSAN=1`。要忽略某些分配的内存泄漏检查，`__AFL_LSAN_OFF(); `可以在分配内存之前和`__AFL_LSAN_ON();`之后使用，LSAN不会检查这两个宏之间区域。

> Note：
>
>   1.
> 一些Sanitizer不能混用，而即使有些可以同时允许的Santizier也可能导致意想不到的行为影响fuzzing，这需要结合你fuzzing的目标情况而定。如果你不熟悉Sanitizer的原理，最好一个编译实例中只启用一个Sanitizer，这样通常不会出问题，而且组合Sanitizer不见得会有好效果，基于对目标的了解正确的使用Sanitizer才是最佳的实践。
>
>   2.
> 有些Sanitizer提供了参数设置的环境变量，如`ASAN_OPTIONS`，如果你有很明确的需求可以设置该变量进一步限制Sanitizer的检测行为，这可能会提高你fuzzing的效率。如果你不熟悉、也没有明确的需求，那么保持默认即可，这通常是最实用的。
>
>   3. 启用CFISAN的实例，可能会检测出很多crash(成百上千)，这是正常的，但大多数是无用的，甚至全是无用的，你需要注意甄别。
>
>   4. 如果你对目标内部结构足够熟悉，你确定那些区域是线程并发的高发区域，那么你可以结合TSAN与 **partial
> instrumentation** 功能提高TSAN的检测效率，因为启用TSAN的实例通常fuzzing速度会大幅减慢。
>
>   5.
> 通常启Sanitizer后，会大幅减慢fuzzing的速度，CPU每秒执行次数会减少，内存也会被大量消耗(AddressSanitizer会大量消耗内存，甚至可能导致计算机内存耗尽)。如果你的计算机配置不行，请斟酌一个合理的搭配。
>
>   6. 一种Sanitizer只应该允许一个实例
> 。在两个实例上允许两个同样的Sanitizer是一种浪费，因为AFL++会同步所有实例的testcase，其他实例的testcase无论如何都会被该实例上的Sanitizer检测一遍，不应该启用两个相同的Sanitizer检测两遍，这会减慢效率。
>
>

暂时只想到这些，以后想到了再补充。

## LLVM Persistent Mode

In-process
fuzzing是一个强大功能，通常比默认常规编译fuzzing的速度快得多，大概快10-20倍，并且基本没有任何缺点。如果可以，请毫不犹豫的使用Persistent
mode。  
众所周知，AFL使用ForkServer来进行每次fuzzing，然而即便不用execve这种巨大的开销，但fork仍然是一笔不小的开。而Persistent
fuzzing即一次fork进程种进行多次fuzzing，而无需每次都fork。  
Persistent mode提供一组AFL++的函数和宏，我们使用下面的形式,用一个while包含我们要进行Persistent
fuzzing的区域。请注意，该区域的代码必须要是无状态的，要么是可以手动可靠的重置为初始状态！这样我们才能再每次fuzzing时重置进而再次fuzzing。  
afl-clang-fast/lto编译的情况下，只需要使用下面的形式即可，但若不是，则复杂一些。  
AFL++官方的仓库对Persistent Mode花了不小的篇幅讲诉，讲的也比较全面，请在此处[Persistent
Mode](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.persistent_mode.md)中查阅，我就不做过多描述了。

    
    
    #include "what_you_need_for_your_target.h"
    
    __AFL_FUZZ_INIT();
    
    int main() {
    
    	// anything else here, e.g. command line arguments, initialization, etc.
    
    	#ifdef __AFL_HAVE_MANUAL_CONTROL
    	__AFL_INIT();
    	#endif
    
    	unsigned char *buf = __AFL_FUZZ_TESTCASE_BUF;  // must be after __AFL_INIT
    	// and before __AFL_LOOP!
    
    	while (__AFL_LOOP(10000)) {
    
    		int len = __AFL_FUZZ_TESTCASE_LEN;  // don't use the macro directly in a
    		// call!
    
    		if (len < 8) continue;  // check for a required/useful minimum input length
    
    		/* Setup function call, e.g. struct target *tmp = libtarget_init() */
    		/* Call function to be fuzzed, e.g.: */
    		target_function(buf, len);
    		/* Reset state. e.g. libtarget_free(tmp) */
    
    	}
    
    	return 0;
    }
    

## Patch

大多数时候，我们fuzzing一个目标想要其达到我们预期的效果，都需要Patch。并且我们在后续fuzzing流程的持续改进中可能还会发现一些影响fuzzing效率的地方，我们又会倒回来patch，编译重新启动fuzzing。  
此外，有时候一些校验、检查，它们往往对于fuzzing的结果没有什么影响，但是却严重影响fuzzing的效率。此时我们通常会审查目标内部代码，将这些严重性fuzzing效率的地方Patch，或者是删除。  
我们都知道Persistent
Mode收益十分巨大，但却要求Persistent循环区域内的代码是无状态的，有时候区域会有一些有状态的函数，但他们却并不重要，这时你可以Patch它们，使它们返回诸如硬编码之类可以，这样就变成无状态的，我们就可以使用Persistent
Mode了。  
例如一个区域的输入可能依赖于socket IO读入，而处理socket IO是很麻烦的，因此我们可以考虑将socket fd替换为文件
fd，并patch那些受socket fd受影响区域，以便我们fuzzing正确运行。  
简言之，Patch最好有明确的理由，随意的Patch对模糊测试来说可能会导致很糟糕的现象，要么你对此处的Patch是基于改进fuzzing效率，要么是为了启用某些有益的fuzzing功能....总之，最好清楚自己的Patch是为了什么。  
但请注意，对于一次模糊测试来说Patch只是可选的，如果你对自己的工具、目标不甚了解，那么Patch对你而言可能不重要。如果你清楚目标的内部结构，并且明确知道要改进fuzzing的流程和目的，那么Patch可能是你定制化自己fuzzing的一个重要手段。

# 后续

目前就先写到着，后面的内容，包括build、fuzzing、评估、流程改进等等就放到下篇，最近的工作可能要忙一些其他的。

