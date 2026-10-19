# honggfuzz漏洞挖掘技术原理分析

阅读量 **571679**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-17 14:30:27

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01e2a900685841d9ec.jpg)

作者：[houjingyi](https://github.com/houjingyi "@houjingyi") @360CERT

## 前言

Google开发的AFL(WinAFL)、libfuzzer和honggfuzz是最著名的三大基于代码覆盖率的fuzzer。网上关于AFL(WinAFL)的分析文章较多，而关于后两者的分析文章较少。之前泉哥已经写过关于honggfuzz的文章：[honggfuzz漏洞挖掘技术深究系列](https://bbs.pediy.com/thread-247954.htm)。本文是自己学习期间的一个笔记，读者也可当成对泉哥文章的一点补充。建议读者先阅读泉哥的文章，本文不会再涉及重复的内容。

相比其它的fuzzer，honggfuzz有以下特点：

1.含有多个fuzz真实程序(Apache/OpenSSL等等)的示例

2.支持持久型fuzzing(Persistent Fuzzing)模式，即长生命周期进程重复调用被fuzz的API

3.支持Linux/FreeBSD/NetBSD/MacOS/Windows(CygWin)/Android等几乎所有主流操作系统

4.支持基于软件和基于硬件(分支计数(branch counting)，指令计数(instruction counting)，Intel
BTS(Branch Trace Store)，Intel PT(Processor Tracing))的反馈驱动(Feedback-Driven)

![](https://p3.ssl.qhimg.com/t01dc378048d8c95a77.png)

5.使用底层接口监视进程(linux和NetBSD下使用ptrace)，与其它fuzzer相比更有可能从crash中发现并报告被劫持/忽略的信号(被fuzz的程序可能截获并隐藏)

## 整体结构

我们首先还是来看一下代码的整体目录。

android&mac&linux&netbsd&posix&arch.h：对不同操作系统的支持，头文件统一在arch.h，接下来分析的代码以linux为例。该目录下有这些文件：

  * arch.c：arch.h中函数的实现
  * bfd.c：基于bfd(Binary File Descriptor)实现解析符号/反汇编等功能
  * perf.c/pt.c：通过perf来使用PT，跟基于硬件的反馈驱动有关
  * trace.c：子进程暂停/终止时分析记录
  * unwind.c：基于libunwind实现栈回溯
  * docs：文档
  * examples：使用honggfuzz进行fuzz的一些例子
  * hfuzz_cc&libhfuzz：hfuzz_cc编译被fuzz程序的源代码，添加libhfuzz.a库。libhfuzz目录下有这些文件：
  * instrument.c：实现各种SanitizerCoverage需要的回调函数
  * linux.c：封装了libhfcommon/ns.c中的nsEnter/nsIfaceUp/nsMountTmpfs等函数
  * memorycmp.c：对libc/Apache/SSL/libXML/Samba等程序中涉及比较的函数封装，添加instrumentUpdateCmpMap函数，两个参数分别是函数的返回地址和第一次出现不相等字符的位置。第一次出现不相等字符的位置越靠后两个值越接近相等，越有可能走到新的路径

![](https://p3.ssl.qhimg.com/t0120e11a7db5ed817b.png)

  * fetch.c/persistent.c：这里面的代码主要是用于持久型fuzzing模式的，有两种方法使用该模式：

一是把被fuzz的API放在LLVMFuzzerTestOneInput中，然后使用`hfuzz_cc/hfuzz_clang test.c -o
test`命令编译，`honggfuzz -P -- ./test`运行fuzzer

![](https://p3.ssl.qhimg.com/t01adf05d7a2927f724.png)

二是在调用被fuzz的API之前添加HF_ITER获取输入，然后使用`hfuzz_cc/hfuzz_clang test.c -o test
~/honggfuzz/libfuzz/libfuzz.a`命令编译，`honggfuzz -P -- ./test`运行fuzzer

![](https://p1.ssl.qhimg.com/t017240cfd74e40b881.png)

  * libhfcommon：一些通用操作
  * libhfnetdriver：fuzz socket类程序的库
  * (libhfcommon和libhfnetdriver中的代码都不太重要，所以不再详细讲解了)
  * third_party：第三方文件
  * tools：创建黑名单，防止重复fuzz存在相同漏洞的文件
  * display.c：显示统计信息
  * honggfuzz.c&cmdline.c&fuzz.c：honggfuzz.c是程序的入口，调用cmdline.c中的函数设置处理命令行参数，调用fuzz.c中的函数启动fuzz
  * input.c：处理输入文件
  * mangle.c：实现各种变异策略
  * report.c：生成报告
  * sanitizers.c：设置ASAN等sanitizer的一些标志
  * socketfuzzer.c&socketfuzzer：socketfuzzer.c 用来fuzz网络服务器，socketfuzzer文件夹中给出了一个存在漏洞的vulnserver_cov.c作为例子
  * subproc.c：子进程相关

先给大家举一个使用honggfuzz的例子，以对[mpv-player](https://github.com/mpv-player/mpv)进行fuzz为例。下载好源代码之后我们首先修改wscript增加一些编译选项。

![](https://p2.ssl.qhimg.com/t016827c6876ae5ca3a.png)

这个时候直接去编译的话链接这一步会出错，我们还没有编写插入的回调函数。

![](https://p3.ssl.qhimg.com/t01ff3a44d97c8918dd.png)

再下载并编译honggfuzz，把libhfuzz目录下编译好的含有回调函数的库链接进来，命令应该像下面这样。

`cc -rdynamic -Wl-znoexecstack -pthread -rdynamic -Wl-version-script
-Wlmpv.def ……(中间是之前编译好的.o文件) -u HonggfuzzNetDriver_main -u
LIBHFUZZ_module_instrument -u LIBHFUZZ_module_memorycmp
/home/hjy/Desktop/honggfuzz/libhfnetdriver/libhfnetdriver.a
/home/hjy/Desktop/honggfuzz/libhfuzz/libhfuzz.a
/home/hjy/Desktop/honggfuzz/libhfuzz/libhfuzz.a
/home/hjy/Desktop/honggfuzz/libhfcommon/libhfcommon.a ……(剩下的命令省略)`

链接成功之后我们再确认一下。

![](https://p0.ssl.qhimg.com/t016668683fba8a217b.png)

准备一些种子文件就可以开始fuzz了，并且应该可以看到统计的edge/pc/cmp等信息。

![](https://p2.ssl.qhimg.com/t01f8e294d17cfb9caf.png)

上面的一些步骤可能有些读者还不太理解，下面会详细说明，这里先有一个初步的印象。

## SanitizerCoverage

在泉哥的文章中已经介绍了反馈驱动的概念和基于Intel
PT的反馈驱动。这里我们重点聊一聊使用SanitizerCoverage对有源码的程序插桩统计代码覆盖率。SanitizerCoverage内置在LLVM中，可以在函数、基本块和边界这些级别上插入对用户定义函数的回调。默认的回调实现了简单的覆盖率报告和可视化。hfuzz_cc是实现了编译时添加`-fsanitize-coverage=……`标志并链接回调函数库libhfuzz的，只不过上面的例子中mpv是用waf编译的(是一个编译系统，不是web防火墙那个waf)，所以这两个步骤我们是手动实现的。honggfuzz中反馈代码覆盖率信息的结构体feedback_t如下所示。

![](https://p2.ssl.qhimg.com/t0199f84d380f31f234.png)

###  -fsanitize-coverage=trace-pc-guard

如果编译源代码时含有`-fsanitize-coverage=trace-pc-guard`标志，编译器在每条边界插入下面的代码，每条边界的guard都不同。

    
    
    if(*guard)
    __sanitizer_cov_trace_pc_guard(uint32_t* guard);
    

如果是一个较大的函数则只会插入`__sanitizer_cov_trace_pc_guard(uint32_t*
guard);`。在IDA中看起来像下面这样。`__sanitizer_cov_trace_pc_guard`函数中一般会先double
check一下`*guard`的值，如果为0就直接返回了。

![](https://p3.ssl.qhimg.com/t018fbdecfaa0bdc0b8.png)

编译器还会在模块的构造函数中插入下面的代码，guard的范围在start和stop之间，`__sanitizer_cov_trace_pc_guard_init`函数中一般会从1开始设置`*guard`的值。

    
    
    __sanitizer_cov_trace_pc_guard_init(uint32_t* start, uint32_t* stop)
    

在IDA中看起来像下面这样。

![](https://p3.ssl.qhimg.com/t01b370a41c9d6b2df1.png)

![](https://p2.ssl.qhimg.com/t015d042da6213e0085.png)

来做个简单的实验。首先准备下面的代码。

example.cc:

![](https://p1.ssl.qhimg.com/t018e7716223ed12853.png)

trace-pc-guard.cc:

![](https://p2.ssl.qhimg.com/t017bcb30ae65763fdf.png)

编译链接之后分别带命令行参数和不带命令行参数执行程序观察输出结果。

    
    
    clang++ -g  -fsanitize-coverage=trace-pc-guard example.cc -c
    clang++ trace-pc-guard.cc example.o -fsanitize=address
    

![](https://p1.ssl.qhimg.com/t01f685985871fa1c06.png)

honggfuzz中的`__sanitizer_cov_trace_pc_guard_init`函数首先将`guards_initialized`标记为true，如果`feedback->pcGuardMap[*guard]`标记为true说明该边界已经命中，将`*guard`设置为0。

![](https://p4.ssl.qhimg.com/t015e15a27956b406d8.png)

`__sanitizer_cov_trace_pc_guard`函数中对于android系统如果`guards_initialized`为false则强制`*SAN`初始化。如果`feedback->pcGuardMap[*guard]`标记为false说明该边界还没有被命中过，`feedback->pidFeedbackEdge[my_thread_no]`加1，并将`feedback->pcGuardMap[*guard]`标记为true。

![](https://p5.ssl.qhimg.com/t017eaa20774ed48050.png)

###  -fsanitize-coverage=indirect-calls

如果编译源代码时含有`-fsanitize-coverage=indirect-calls`标志，编译器在每个非间接跳转之前插入下面的代码。

    
    
    __sanitizer_cov_trace_pc_indir(void *callee)
    

我们接着实验。修改一下原来的代码。

example.cc:

![](https://p1.ssl.qhimg.com/t010899e28c6b3ec5f7.png)

trace-pc-indir.cc:

![](https://p1.ssl.qhimg.com/t01a9770e7b7d92422b.png)

运行程序观察输出结果。

![](https://p4.ssl.qhimg.com/t01cfaee24cde2d2bb1.png)

honggfuzz中的`__sanitizer_cov_trace_pc_indir`函数首先取`__sanitizer_cov_trace_pc_indir返回地址<<12`得pos1，然后取间接跳转的地址&0xfff得pos2，将pos1|pos2之后&0x7FFFFFF。

![](https://p3.ssl.qhimg.com/t01155af7b852a54485.png)

在我们上面的例子中`__sanitizer_cov_trace_pc_indir`返回地址是0x516E99，间接跳转调用的foo函数的地址是0x516E60，所以最后得到的是0x6E99E60。

![](https://p5.ssl.qhimg.com/t01c12d0cb5bd587d20.png)

连续八个这样计算出的addr对应`feedback->bbMapPc[addr]`，每个地址对应1位。取出对应的位中的值，和1做或运算并更新。如果该值为0说明这里的非间接跳转还没有执行，`feedback->pidFeedbackPc[my_thread_no]`加1。

![](https://p2.ssl.qhimg.com/t016184ec43f83fa415.png)

![](https://p1.ssl.qhimg.com/t01aea405176f37280d.png)

###  -fsanitize-coverage=trace-cmp

如果含有`-fsanitize-coverage=trace-cmp`标志，编译器在比较指令之前和switch指令之前插入下面的代码。

    
    
    void __sanitizer_cov_trace_(const)_cmp1(uint8_t Arg1, uint8_t Arg2);
    void __sanitizer_cov_trace_(const)_cmp2(uint16_t Arg1, uint16_t Arg2);
    void __sanitizer_cov_trace_(const)_cmp4(uint32_t Arg1, uint32_t Arg2);
    void __sanitizer_cov_trace_(const)_cmp8(uint64_t Arg1, uint64_t Arg2);
    // Val是switch操作数
    // Cases[0]是case常量的数目
    // Cases[1]是Val的位数
    // Cases[2:]是case常量
    void __sanitizer_cov_trace_switch(uint64_t Val, uint64_t *Cases);
    

instrument.c中的回调函数如下。`__builtin_popcount(x)`会计算x中1的位数，所以v的值表示Arg1和Arg2有多少位相同。和memorycmp.c基本含义是相同的。

![](https://p4.ssl.qhimg.com/t0153cdc62d3684bff8.png)

还有一些标志用的不多或者原理类似，就不再赘述了。

## fuzz流程

说完了关于SanitizerCoverage的问题我们从honggfuzz.c的main函数开始分析fuzz流程。经过一系列初始化之后调用了`fuzz_threadsStart`函数。

![](https://p0.ssl.qhimg.com/t01e2da75b485c5c62e.png)

hfuzz是一个包含各种fuzz所需信息的结构体，各个结构体的含义根据名称应该很容易理解。

![](https://p4.ssl.qhimg.com/t01bf8e8927c3390e73.png)

在前面解析命令行参数的cmdlineParse函数中，`hfuzz.feedback.dynFileMethod`默认设置为`_HF_DYNFILE_SOFT`，即基于软件的反馈驱动fuzz。如果命令行中有-x选项，表示采用static/dry mode，即不采用反馈驱动。

![](https://p1.ssl.qhimg.com/t016c94bca7036e3a5a.png)

![](https://p3.ssl.qhimg.com/t019737cea338dc7df0.png)

`fuzz_threadsStart`函数中不是static/dry
mode设置当前state为`_HF_STATE_DYNAMIC_DRY_RUN`，进入第一阶段Dry Run。

![](https://p4.ssl.qhimg.com/t012a1ccc5f327171b5.png)

接下来调用了`subproc_runThread`->`pthread_create`->`fuzz_threadNew`->`fuzz_fuzzLoop`函数。`fuzz_fuzzLoop`函数如下所示。

![](https://p0.ssl.qhimg.com/t01387a276fe5d20e5e.png)

`fuzz_fuzzLoop`函数首先调用了`fuzz_fetchInput`函数，因为当前的state是`_HF_STATE_DYNAMIC_DRY_RUN`，所以接着调用了`input_prepareStaticFile`函数取得一个文件并返回。

![](https://p2.ssl.qhimg.com/t01b2252b455e684233.png)

接下来调用了`subproc_Run`函数。

![](https://p2.ssl.qhimg.com/t013d1f8f7be3fdfe35.png)

`subproc_Run`函数首先调用了`subproc_New`函数，在`subproc_New`函数中clone出一个子进程调用`arch_launchChild`函数，在`arch_launchChild`函数中运行了被fuzz的程序。

![](https://p2.ssl.qhimg.com/t01926fb43c9f821735.png)

`subproc_New`函数返回后调用`arch_reapChild`函数，`arch_reapChild`函数中调用了`arch_checkWait`函数。`arch_checkWait`函数等待子进程返回并调用`arch_traceAnalyze`函数。如果子进程返回状态为暂停，并且是我们感兴趣的信号时，如果是fuzz进程则调用`arch_traceSaveData`函数(`fuzz_fuzzLoop`函数调用`subproc_Run`函数的情况，下文同)；如果是其它进程则调用`arch_traceAnalyzeData`函数(`fuzz_fuzzLoop`函数调用`fuzz_runVerifier`函数的情况，下文同)。前者进行的是完整的分析，后者仅仅栈回溯然后计算stack
hash。

![](https://p5.ssl.qhimg.com/t014280198d3af07981.png)

如果子进程返回状态为退出，并且是sanitizer中定义的exitcode时，调用`arch_traceExitAnalyze`函数。在`arch_traceExitAnalyze`函数中如果是fuzz进程调用`arch_traceExitSaveData`函数；如果是其它进程调用`arch_traceExitAnalyzeData`函数。在`arch_traceExitSaveData`函数中首先增加全局crash计数，调用`arch_parseAsanReport`函数解析asan报告。

![](https://p2.ssl.qhimg.com/t01a4fb2ef6b36b3a1d.png)

如果设置ignoreAddr，忽略crash地址小于ignoreAddr的情况。

![](https://p2.ssl.qhimg.com/t01797f06004963a510.png)

计算stack hash和crash PC，忽略stack hash在黑名单上的情况。

![](https://p2.ssl.qhimg.com/t01e92ce8c90eec6dcc.png)

根据得到的信息将crash保存为固定文件名的格式，生成报告。在`arch_traceExitAnalyzeData`函数中只会解析asan报告和计算stack
hash。

![](https://p0.ssl.qhimg.com/t015e8144588f53971b.png)

回到`fuzz_fuzzLoop`函数，最后调用`fuzz_perfFeedback`函数更新代码覆盖率相关信息，`fuzz_runVerifier`函数指示是否应该使用当前验证的crash更新report。在`fuzz_perfFeedback`函数中如果当前的文件增加了代码覆盖率调用`fuzz_addFileToFileQ`函数将它加到语料库中。

![](https://p1.ssl.qhimg.com/t01c5ea3220f11b02ed.png)

经过多次调用，当`fuzz_fetchInput`函数调用`input_prepareStaticFile`函数无法再得到新的文件返回false之后调用`fuzz_setDynamicMainState`函数设置当前state为`_HF_STATE_DYNAMIC_SWITCH_TO_MAIN`，进入第二阶段Switching
to Dynamic Main(Feedback Driven
Mode)。当所有的线程都进入第二阶段以后设置当前state为`_HF_STATE_DYNAMIC_MAIN`，进入第三阶段Dynamic
Main(Feedback Driven Mode)。

![](https://p5.ssl.qhimg.com/t010613617029fdc81c.png)

返回到`fuzz_fetchInput`函数，调用`input_prepareDynamicInput`函数准备输入数据并变异。文件的来源为之前`fuzz_addFileToFileQ`函数添加的。

![](https://p0.ssl.qhimg.com/t01fe0d4d601de4e2e3.png)

至此honggfuzz的fuzz流程我们就大致分析完了。作者水平有限，文章若有不当之处还望各位指正。

## 参考资料

1.[Clang 9 documentation](https://clang.llvm.org/docs/SanitizerCoverage.html)  
2.[honggfuzz漏洞挖掘技术深究系列](https://bbs.pediy.com/thread-247954.htm)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **houjingyi** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181936](/post/id/181936)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Fuzz](/tag/Fuzz)

 **+1** __17赞

 __收藏

![](https://p2.ssl.qhimg.com/t0163f39acdec94f17a.png) houjingyi

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

