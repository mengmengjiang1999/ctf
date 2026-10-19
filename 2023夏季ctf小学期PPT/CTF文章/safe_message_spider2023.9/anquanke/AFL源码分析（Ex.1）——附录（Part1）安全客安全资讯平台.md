# AFL源码分析（Ex.1）——附录（Part 1）

阅读量 **169574**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-08 15:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0\. 写在前面

此文章主要是对`AFL`仓库中`doc`目录下的所有文档进行翻译。

  * [x] env_variables.txt(环境变量手册) —— 本文
  * [ ] historical_notes.txt(历史记录)
  * [ ] INSTALL(安装说明)
  * [x] life_pro_tips.txt(使用技巧) —— 本文
  * [ ] notes_for_asan.txt
  * [ ] parallel_fuzzing.txt
  * [ ] perf_tips.txt
  * [ ] QuickStartGuide.txt
  * [ ] sister_projects.txt
  * [ ] status_screen.txt
  * [ ] technical_details.txt

后续附录将继续翻译以上列表中的文章。

## 1\. life_pro_tips.txt(使用技巧)

  1. 此文档是为那些了解基础知识但又懒得阅读或记住`AFL` 的所有其他文档的人提供的小建议。
  2. 通过使用模糊字典获得更多的有效测试结果。请参阅`dictionaries/README.dictionaries`了解如何操作。
  3. 为了充分使用电脑的硬件资源，可以使用`AFL`的并行作业模式(多进程模式)。(详见`docs/parallel_fuzzing.txt`了解如何操作)
  4. 通过使用`libdislocator.so`获得更多的有关内存损坏的测试结果。请参阅`libdislocator/README.dislocator`了解如何操作。
  5. 如果您想了解`fuzz`器是如何解析输入样本的，请使用`afl-analyze`工具，此工具将通过彩色输出的方式为您展示。
  6. 您可以直观的监控`fuzz`测试的进度，请使用`afl-plot`工具，此工具将生成浏览器友好的监控GUI。
  7. 您也可以通过编程的方式来监控`fuzz`测试的进度，请使用`afl-whatsup`工具或者直接操作`AFL`输出目录中的`fuzzer_stats`文件。
  8. 对`AFL`实时结果中显示为红色或紫色的重要信息感到困惑，请查阅`docs/status_screen.txt`获取进一步解释！
  9. 您可以将您的测试目标转换为持续模式以获得巨大的性能提升！请参阅`llvm_mode/README.llvm`中的第`5`部分以获取提示。
  10. 如果您使用`clang`语言，查看`llvm_mode/`下的文件以获取`afl-gcc`的更快替代方案！
  11. 您知道`AFL`可以对闭源代码、黑/灰盒文件、跨平台/跨架构文件进行模糊测试吗？查看`qemu_mode/README.qemu`了解更多信息。
  12. 您知道`afl-fuzz`可以帮您将任何测试用例最小化吗？试试随`AFL`项目提供的`afl-tmin`工具，他能帮您快速获得小型目标文件！
  13. 不确定`fuzz`出的导致样例`crash`的输入样本是否可利用？`AFL`可以帮助您解决问题。指定`-C`以启用崩溃探索模式。有关更多信息，请参阅自述文件中的第 10 节。
  14. Trouble dealing with a machine uprising? Relax, we’ve all been there.Find essential survival tips at <http://lcamtuf.coredump.cx/prep/>.译者注：此条`Tips`总感觉像是`AFL`项目组开的一个小玩笑，翻译过来是如何应对关于机器毁灭人类的问题，由于此条`Tip`过于无厘头，因此不做翻译，直接附上原文，喜欢科幻的读者可以随便看看(？
  15. `AFL`生成的语料库可用于为其他测试过程提供参考。请参阅`README`文件中的第`2`节以获取灵感 – 这往往会产生意料外的结果！
  16. 想要自动化的发现不会导致崩溃的内存处理错误？尝试通过`ASAN`、`MSAN`或`Valgrind`运行`AFL`生成的语料库。
  17. 正确选择输入文件对于成功的模糊测试工作至关重要。如果需要此方面的专业提示，请参阅自述文件(或`docs/perf_tips.txt`)中的第`5`部分。
  18. 您可以手动设置相关选项以提高`AFL`自动化发现堆栈损坏问题的几率，您可以在环境中指定`AFL_HARDEN=1`以启用强化标志。
  19. 遇到了不可重现的崩溃问题？此类问题往往会发生，但通常不难诊断。如果您想获得有关提示，请参阅自述文件中的第`7`节。
  20. 模糊测试不仅仅可以找到关于代码库中的内存损坏问题。您可以添加一些健全性检查，例如`assert()/abort()` 语句以轻松捕获逻辑错误。
  21. 如果你想弄清楚`AFL`是如何真正运作的，查看`docs/technical_details.txt`以了解所有细节！
  22. 有大量旨在与`AFL`配合使用的第三方帮助工具！在编写自己的第三方工具之前，请务必查看`docs/sister_projects.txt`。
  23. 需要对特定程序的命令行参数进行模糊测试？您可以在`Experiment/argv_fuzzing`中找到一个简单的解决方案。
  24. 您的测试目标使用校验和的格式？删除校验和检查代码或使用后处理器！有关更多信息，请参阅`experimental/post_library/`。
  25. 处理一个非常缓慢的目标但是希望立即获得结果？调用`afl-fuzz`时指定`-d`！
  26. 

## 2\. env_variables.txt(环境变量手册)

本文档讨论了`American Fuzzy
Lop`使用的环境变量，这些变量可以帮助高级用户或需要进行某些类型的自定义模糊测试的用户，这些环境变量可以用于影响`fuzz`器的函数行为。有关一般说明手册，请参阅自述文件。

### 2.1. `afl-gcc`、 `afl-clang`、 `afl-as`相关的设置

因为它们不能直接接受命令行选项，所以编译时这三个工具相当广泛地使用了环境变量：

  * `AFL_HARDEN`：实际调用下游编译工具时，设置此环境变量将会自动添加代码安全性强化选项。目前包括`-D_FORTIFY_SOURCE=2`和`-fstack-protector-all`。该设置对于捕获不会导致程序崩溃的内存错误很有用，但代价是非常轻微(低于`5%`)的性能损失。译者注：下游编译工具指实际调用的编译工具，例如`afl-gcc`最后实际调用的下游编译工具是`gcc`。
  * `AFL_DONT_OPTIMIZE`：默认情况下，`AFL`将附加`-O3`以优化构建。在极少数情况下，这会导致使用`-Werror`构建的程序出现问题。`-O3`可以进行更彻底的代码分析，并且可以产生额外的警告。要禁用优化，请设置此环境变量。译者注：为了使`FORTIFY`生效，必须同时设置`-O2`以上优化，因此，同时设置以上两个环境变量将有可能导致`FORTIFY`机制失效。
  * `AFL_USE_ASAN`：设置此环境变量会自动启用`ASAN`机制，前提是编译器支持该功能。请注意，使用`ASAN`进行模糊测试具有一定的挑战性 – 请参阅`notes_for_asan.txt`。(您也可以通过`AFL_USE_MSAN`启用`MSAN`；`ASAN`和`MSAN`具有相同的问题；这两种模式是互斥的。`UBSAN`和其他的检测程序尚未得到官方支持，但很容易手动调试并整合进`AFL`)译者注：`MSAN`、`ASAN`、`UBSAN`均是通过代码插桩等方式进行漏洞检测的选项。
  * `AFL_CC`、`AFL_CXX`、`AFL_AS`：设置这些环境变量可让您使用备用的下游编译工具，而不是`$PATH`中的默认`clang`、`gcc`或`as`二进制文件。
  * `AFL_PATH`：此环境变量可用于为`afl-gcc`指定一个`afl-as`的备用位置。一种可能的用途是`experimental/clang_asm_normalize/`，这将允许您在编译`clang`代码时通过将规范化器插入链中来检测手写的汇编码。 (`GCC`中没有类似的功能）
  * `AFL_INST_RATIO`：将此环境变量设置为`0%`到`100%`之间的百分比可控制检测每个分支的概率。这在处理使输出位图饱和的异常复杂的程序时很有用(尽管这种情况很少)。示例包括`v8`、`ffmpeg`和`perl`。(如果发生这种情况，`afl-fuzz`会通过以火红色显示“位图密度”字段来提前警告您。)将`AFL_INST_RATIO`设置为`0`是一个不错的选择。这将只检测函数入口点之间的转换，而不是单个程序分支。
  * `AFL_NO_BUILTIN`：此环境变量使编译器生成适合与`libtokencap.so`一起使用的代码(但运行速度可能比没有此环境变量时慢一些)。
  * `TMPDIR`：此环境变量被`afl-as`用于存放临时文件；如果未设置此变量，则默认为`/tmp`。
  * `AFL_KEEP_ASSEMBLY`：当此环境变量被设置，`afl-as`将保留其生成的中间文件。这有助于解决问题或了解该工具的工作原理。要将它们置于可获取的位置，请尝试以下操作： 
    
        mkdir assembly_here
    TMPDIR=$PWD/assembly_here AFL_KEEP_ASSEMBLY=1 make clean all
    

  * `AFL_QUIET`：当此环境变量被设置，`afl-cc`和`afl-as`的`banner`将不在编译期间显示，以防您被它们分散注意力。

### 2.2. `afl-clang-fast`相关的设置

`native LLVM`检测工具可以使用接受`2.1`中讨论的环境变量，但以下变量除外：

  * `AFL_AS`：因为`afl-clang-fast`不直接调用`GNU as`。
  * `TMPDIR`、`AFL_KEEP_ASSEMBLY`：因为`afl-clang-fast`没有创建临时程序集文件。

请注意， `AFL_INST_RATIO`这个环境变量的效果与`afl-gcc`的行为略有不同，因为函数本来就不是无条件地被检测，因此此环境变量被设置为低值将产生更显着的效果。对于此工具，`0`不是有效选择。

### 2.3. `afl-fuzz`相关的设置

这个工具接受多个环境变量，这些变量将禁用一些完整性检查或更改该工具的一些奇特的语义：

  * `AFL_SKIP_CPUFREQ`：此环境变量被设置会跳过`CPU`扩展策略的检查。如果您无法更改其策略的默认值(例如，没有对系统的`root`访问权限)并且可以承受一些性能损失，这将非常有用。
  * `AFL_NO_FORKSRV`：此环境变量被设置会禁用`forkserver`优化，此优化将在为每个输入样本进行`fork + execve()`调用。这在使用不守规矩的库时非常有用，这些库在初始化时创建线程或做其他疯狂的事情(在`fuzzer`运行之前）。请注意，此设置会禁止在启动`forkserver`时通常会进行的一些用户友好的诊断，并导致相当显着的性能下降。
  * `AFL_EXIT_WHEN_DONE`：此环境变量被设置会导致`afl-fuzz`在所有现有路径都被模糊化并且一段时间内没有新发现时终止。这通常由`UI`中的循环计数器是否变为绿色来指示。此变量对于某些类型的自动化作业可能很方便。
  * `AFL_NO_AFFINITY`：此环境变量被设置会禁止实例尝试绑定到`Linux`系统上的特定`CPU 内核`。这会减慢速度，但可以让您运行更多的`afl-fuzz`实例(如果您真的想要这么做的话)。
  * `AFL_SKIP_CRASHES`：此环境变量被设置会导致`AFL`忽略输入队列中导致程序崩溃的文件。这可以帮助解决程序仅间歇性崩溃的罕见情况，但在正常操作条件下并不真正推荐这样做。
  * `AFL_HANG_TMOUT`：此环境变量允许您指定超时时间用以确定特定测试用例是否“挂起”。默认值为`1`秒或`-t`参数的值，以较大者为准。如果您非常担心缓慢的输入，或者如果您不希望`AFL`花费太多时间对这些输入进行分类，而只是快速地将所有超时输入该测试目标中，则将值调低可能会很有用。
  * `AFL_NO_ARITH`：此环境变量被设置会导致`AFL`跳过大多数确定性算术过程。这对于加速基于文件格式为文本的模糊测试很有用。
  * `AFL_SHUFFLE_QUEUE`：此环境变量被设置会导致`AFL`在启动时随机重新排序输入队列。一些用户要求进行非正统的并行模糊测试设置，但不建议这样做。
  * `AFL_SKIP_BIN_CHECK`：在基于`afl-fuzz`开发自定义检测工具时，您可以使用此环境变量来禁止对非检测二进制文件和 shell 脚本的检查.此选项和`AFL_DUMB_FORKSRV`与`-n`一起设置时，`afl-fuzz` 仍然遵循`forkserver`协议，而不期望任何检测数据返回。
  * `AFL_IMPORT_FIRST`：在`-M`或`-S`模式下运行时，设置此环境变量会导致`fuzzer`在执行任何其他操作之前从其他实例导入测试用例。这使得实时反馈中的`own finds`计数器更加准确。除了反美学之外，没有什么改变。
  * `AFL_POST_LIBRARY`：设置此环境变量允许您为变异文件配置后处理器。例如，修复校验和。有关更多信息，请参阅`experimental/post_library/`。
  * `AFL_FAST_CAL`：设置此环境变量将导致校准阶段加速并保持大约`2.5`倍的速度(尽管此时精度较低)，这在针对慢速目标开始检测时会有所帮助。
  * `AFL_NO_CPU_RED`：屏幕底部显示的`CPU`小部件相当简单，可能会过早地警告您的设备处于高负载模式，尤其是在内核数量较少的系统上。设置此环境变量将使其不再显示为令人紧张的红色。
  * `AFL_PATH`：在`QEMU`模式(`-Q`)中，将在此环境变量中搜索`afl-qemu-trace`。
  * `AFL_PRELOAD`：此环境变量被设置会导致`AFL`为目标二进制文件设置`LD_PRELOAD`而不会中断`afl-fuzz`进程本身。这对于引导 `libdislocator.so`非常有用。
  * `AFL_PRELOAD`：此环境变量被设置会导致`AFL`的`GUI`被禁用，终端中只是定期打印一些基本统计信息。当`afl-fuzz`的输出被重定向到文件或管道时，也会自动触发此行为。
  * `AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES`：如果您是`Jakub`，您可能需要设置此环境变量，其他用户无需设置。
  * `AFL_BENCH_JUST_ONE`：仅基准测试，此环境变量被设置会导致`AFL`在处理第一个队列条目后退出。
  * `AFL_BENCH_UNTIL_CRASH`：仅基准测试，此环境变量被设置会导致`AFL`在发现第一次崩溃后很快退出。

### 2.4. `afl-qemu-trace`相关的设置

用于检测纯二进制文件的`QEMU`包装器支持多种环境变量：

  * `AFL_INST_RATIO`：此环境变量被设置将跳过一些基本块上的检测，这在处理非常复杂的二进制文件时很有用。
  * `AFL_INST_LIBS`：此环境变量被设置将会导致转译器也检测任何动态链接库(特别是包括`glibc`)中的代码。
  * 底层`QEMU`二进制文件将识别任何标准的用户空间模拟变量(例如，`QEMU_STACK_SIZE`)。

### 2.5. `afl-cmin`相关的设置

语料库最小化攻击提供很少的可定制性：

  * `AFL_PATH`：此环境变量用于指定`afl-showmap`和`afl-qemu-trace`位置(后者仅在`-Q`模式下)。
  * `AFL_KEEP_TRACES`：此环境变量被设置将会导致该工具保留用于最小化并通常在退出时删除的跟踪数据和其他元数据。这些文件可以在`<out_dir>/.traces/*`中找到。
  * `AFL_ALLOW_TMP`：此环境变量被设置将会导致该工具允许此脚本和其他一些脚本在`/tmp`中运行。这对于具有流氓用户的多用户系统来说是一个适度的安全风险，但在专用的模糊测试机器上应该是安全的。

### 2.6. `afl-tmin`相关的设置

此工具几乎没有什么可设置的。

  * `AFL_PATH`：在`QEMU`模式(`-Q`)中，将在此环境变量中搜索`afl-qemu-trace`。
  * `TMPDIR`：如果无法在当前工作目录中创建临时文件，则可以使用此环境变量。
  * `AFL_TMIN_EXACT`：如果您希望`afl-tmin`在最小化崩溃文件时要求执行路径匹配，您可以指定此环境变量。这将使最小化的效率大幅减低，但可能会阻止工具在非常有缺陷的软件中从一个崩溃条件“跳”到另一个崩溃条件。您可能希望将它与`-e`标志结合使用。

### 2.7. `afl-analyze`相关的设置

  * `AFL_ANALYZE_HEX`：您可以设置此环境变量以将获取的文件偏移量以十六进制而不是十进制的方式打印。

### 2.8. `libdislocator.so`相关的设置

此库文件有四个环境变量可被设置：

  * `AFL_LD_LIMIT_MB`：此环境变量指定定了库允许的最大堆空间使用的大小，以兆字节为单位。默认值为`1 GB`。一旦超过，分配将返回`NULL`。
  * `AFL_LD_HARD_FAIL`：此环境变量通过在过度分配时调用`abort()`来改变内存分配行为，从而导致`AFL`认为是崩溃。这对于应该保持特定内存占用的程序很有用。
  * `AFL_LD_VERBOSE`：此环境变量使库输出一些诊断消息，这些消息可能有助于查明任何观察到的问题的原因。
  * `AFL_LD_NO_CALLOC_OVER`：此环境变量在`calloc()`溢出时禁止`abort()`调用。大多数常见的分配器会在内部进行检查并返回 `NULL`，因此只有在更奇特的设置中才会存在安全风险。

### 2.9. `afl-fuzz`等工具主动设置的变量

afl-fuzz 不直接解析以下几个变量，但如果环境中尚不存在，则将其设置为最佳值：

  * 默认情况下，`LD_BIND_NOW`将被设置，这是为了通过强制链接器在`fork`服务器启动之前完成所有工作来加速模糊测试。您可以通过预先设置`LD_BIND_LAZY`来覆盖它，但这几乎可以肯定是毫无意义的。
  * 默认情况下，`ASAN_OPTIONS`设置为： 
    
        abort_on_error=1
    detect_leaks=0
    symbolize=0
    allocator_may_return_null=1
    

如果您想设置自己的选项，请确保包含`abort_on_error=1`。否则，模糊器将无法检测到测试目标中的崩溃动作。类似地，请确保包含`symbolize=0`，因为没有它，`AFL`可能难以分辨崩溃和挂起。

  * 默认情况下，`MSAN_OPTIONS`设置为： 
    
        exit_code=86 (出于遗留原因必须设置)    
    abort_on_error=1
    symbolize=0
    msan_track_origins=0
    allocator_may_return_null=1
    

在自定义任何内容时务必包括第一个，因为某些`MSAN`版本不会在出错时调用`abort()`，我们需要一种检测故障的方法。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/245544](/post/id/245544)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Fuzz](/tag/Fuzz)
  * [AFL](/tag/AFL)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

