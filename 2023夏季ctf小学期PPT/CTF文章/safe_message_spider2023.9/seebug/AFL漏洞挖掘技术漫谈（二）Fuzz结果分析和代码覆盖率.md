**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/WMfCNN095-PpM0VB_pRESg>**

### 一、前言

阿尔法实验在上一篇[文章](https://paper.seebug.org/841/)中向大家介绍了使用AFL开始模糊测试前要做的一些准备工作，以及AFL的几种工作方式，但是并没有提到何时结束测试过程，以及测试完成后又需要做些什么。本文中就继续介绍这些内容，并开始逐步介绍一些AFL相关原理。以下就是本文中主要讨论的问题：

  * 何时结束Fuzzing工作
  * afl-fuzz生成了哪些文件
  * 如何对产生的crash进行验证和分类
  * 用什么来评估Fuzzing的结果
  * 代码覆盖率及相关概念
  * AFL是如何记录代码覆盖率的

### 二、Fuzzer工作状态

因为 _afl-fuzz_ 永远不会停止，所以何时停止测试很多时候就是依靠 _afl-fuzz_ 提供的状态来决定的。除了前面提到过的通过状态窗口、
_afl-whatsup_ 查看 _afl-fuzz_ 状态外，这里再补充几种方法。

#### 1\. afl-stat

_afl-stat_ 是[afl-utils](https://gitlab.com/rc0r/afl-utils)这套工具AFL辅助工具中的一个（这套工具中还有其他更好用的程序，后面用到时会做介绍），该工具类似于 _afl-whatsup_ 的输出结果。

使用前需要一个配置文件，设置每个afl-fuzz实例的输出目录：

    
    
    {
        "fuzz_dirs": [
            "/root/syncdir/SESSION000",
            "/root/syncdir/SESSION001",
            ...
            "/root/syncdir/SESSION00x"
        ]
    }

然后指定配置文件运行即可：

    
    
    $ afl-stats -c afl-stats.conf
    [SESSION000 on fuzzer1]
     Alive:   1/1
     Execs:   64 m
     Speed:   0.3 x/s
     Pend:    6588/249
     Crashes: 101
    [SESSION001 on fuzzer1]
     Alive:   1/1
     Execs:   105 m
     Speed:   576.6 x/s
     Pend:    417/0
     Crashes: 291
    ...

#### 2\. 定制afl-whatsup

_afl-whatsup_ 是依靠读afl-fuzz输出目录中的 _fuzzer_stats_
文件来显示状态的，每次查看都要需要手动执行，十分麻烦。因此可以对其进行修改，让其实时显示fuzzer的状态。方法也很简答，基本思路就是在所有代码外面加个循环就好，还可以根据自己的喜好做些调整：

![img](https://images.seebug.org/content/images/2019/03/11/1552285575000-006tNbRwgy1fy9rn7xv9pj30tu0hcaio.jpg-w331s)

#### 3\. afl-plot

前面提到的都是基于命令行的工具，如果还想要更直观的结果，可以用 _afl-plot_ 绘制各种状态指标的直观变化趋势。

    
    
    #安装依赖工具gnuplot
    $ apt-get install gnuplot
    $ afl-plot afl_state_dir graph_output_dir

以测试libtiff的情况为例，进入afl-plot输出目录，打开 _index.html_ ，会看到下面三张图：

首先是路径覆盖的变化，当 **pending fav** 的数量变为零并且 **total paths**
数量基本上没有再增长时，说明fuzzer有新发现的可能性就很小了。

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNbRwgy1fy9i4n641dj30rs08c3yw.jpg-w331s)

接着是崩溃和超时的变化

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNbRwgy1fy9i50t25jj30rs05kdfw.jpg-w331s)

最后是执行速度的变化，这里要注意的是，如果随着时间的推移，执行速度越来越慢，有一种可能是因为fuzzer耗尽一些共享资源。

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNbRwgy1fy9i57wod8j30rs05kjs5.jpg-w331s)

#### 4\. PYTHIA

笔者在查阅资料的过程中，还发现了[pythia](https://github.com/mboehme/pythia)这个AFL的扩展项目，虽然不知道效果如何，但这里还是顺便提一提。其特色在于可以估算发现新crash和path概率，其运行界面相比原版的AFL多出了下面几个字段：
![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNbRwgy1fy9kgefs3sj314a0760wx.jpg-w331s)

correctness: 在没有发现crash时，发现一个导致crash输入的概率。 fuzzability:
表示在该程序中发现新路径的难度，该数值越高代表程序越容易Fuzz。 current paths: 显示当前发现的路径数。 path coverag:
路径覆盖率。

### 三、结束测试

#### 1.何时结束

检查 _afl-fuzz_ 工作状态的目的是为何时停止测试提供依据，通常来说符合下面几种情况时就可以停掉了。

(1) 状态窗口中”cycles
done”字段颜色变为绿色该字段的颜色可以作为何时停止测试的参考，随着周期数不断增大，其颜色也会由洋红色，逐步变为黄色、蓝色、绿色。当其变为绿色时，继续Fuzzing下去也很难有新的发现了，这时便可以通过Ctrl-C停止afl-fuzz。

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNc79gy1fytdcw01grj30ax05gq3k.jpg-w331s)

(2) 距上一次发现新路径（或者崩溃）已经过去很长时间了，至于具体多少时间还是需要自己把握，比如长达一个星期或者更久估计大家也都没啥耐心了吧。

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNc79gy1fytdd25h4uj30oq053q57.jpg-w331s)

(3) 目标程序的代码几乎被测试用例完全覆盖，这种情况好像很少见，但是对于某些小型程序应该还是可能的，至于如何计算覆盖率将在下面介绍。

(4)上面提到的pythia提供的各种数据中，一旦 **path covera**
达到99％（通常来说不太可能），如果不期望再跑出更多crash的话就可以中止fuzz了，因为很多crash可能是因为相同的原因导致的；还有一点就是
**correctness** 的值达到 **1e-08** ，根据pythia开发者的说法，这时从上次发现path/uniq
crash到下一次发现之间大约需要1亿次执行，这一点也可以作为衡量依据。

#### 2\. 输出结果

_afl-fuzz_ 的输出目录中存在很多文件，有时想要写一个辅助工具可能就要用到其中的文件。下面以多个fuzz实例并行测试时的同步目录为例：

    
    
    $ tree -L 3
    .
    ├── fuzzer1
    │   ├── crashes
    │   │   ├── id:000000,sig:06,src:000019+000074,op:splice,rep:2
    │   │   ├── ...
    │   │   ├── id:000002,sig:06,src:000038+000125,op:splice,rep:4
    │   │   └── README.txt
    │   ├── fuzz_bitmap
    │   ├── fuzzer_stats
    │   ├── hangs
    │   │   └── id:000000,src:000007,op:flip1,pos:55595
    │   ├── plot_data
    │   └── queue
    │       ├── id:000000,orig:1.png
    │       ├── ....    
    │       └── id:000101,sync:fuzzer10,src:000102
    └── fuzzer2
        ├── crashes
        ├── ...

queue：存放所有具有独特执行路径的测试用例。  
crashes：导致目标接收致命signal而崩溃的独特测试用例。  
crashes/README.txt：保存了目标执行这些crash文件的命令行参数。  
hangs：导致目标超时的独特测试用例。  
fuzzer_stats：afl-fuzz的运行状态。  
plot_data：用于afl-plot绘图。

### 四、处理测试结果

到了这里，我们可能已经跑出了一大堆的crashes，那么接下来的步骤，自然是确定造成这些crashes的bug是否可以利用，怎么利用？这是另一个重要方面。当然，个人觉得这比前面提到的内容都要困难得多，这需要对常见的二进制漏洞类型、操作系统的安全机制、代码审计和调试等内容都有一定深度的了解。但如果只是对crash做简单的分析和分类，那么下面介绍的几种方法都可以给我们提供一些帮助。

#### 1\. crash exploration mode

这是afl-fuzz的一种运行模式，也称为 **peruvian rabbit mode**
，用于确定bug的可利用性，具体细节可以参考[lcamtuf](https://lcamtuf.blogspot.com/2014/11/afl-fuzz-crash-exploration-mode.html)的博客。

    
    
    $ afl-fuzz -m none -C -i poc -o peruvian-were-rabbit_out -- ~/src/LuPng/a.out @@ out.png

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNc79gy1fyxyap52mpj31440sydwp.jpg-w331s)

举个例子，当你发现目标程序尝试写入\跳转到一个明显来自输入文件的内存地址，那么就可以猜测这个bug应该是可以利用的；然而遇到例如NULL pointer
dereferences这样的漏洞就没那么容易判断了。

将一个导致crash测试用例作为 _afl-fuzz_ 的输入，使用 _-C_ 选项开启crash
exploration模式后，可以快速地产生很多和输入crash相关、但稍有些不同的crashes，从而判断能够控制某块内存地址的长度。这里笔者在实践中没有找到适合的例子，但在一篇[文章](https://countuponsecurity.com/tag/peruvian-were-rabbit/)中发现了一个很不错的例子——tcpdump栈溢出漏洞，crash
exploration模式从一个crash产生了42个新的crash，并读取不同大小的相邻内存。

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNc79gy1fyy0z3rmftj30yu05r3yq.jpg-w331s)

#### 2\. triage_crashes

AFL源码的experimental目录中有一个名为 _triage_crashes.sh_
的脚本，可以帮助我们触发收集到的crashes。例如下面的例子中，11代表了SIGSEGV信号，有可能是因为缓冲区溢出导致进程引用了无效的内存；06代表了SIGABRT信号，可能是执行了abort\assert函数或double
free导致，这些结果可以作为简单的参考。

    
    
    $ ~/afl-2.52b/experimental/crash_triage/triage_crashes.sh fuzz_out ~/src/LuPng/a.out @@ out.png 2>&1 | grep SIGNAL
       +++ ID 000000, SIGNAL 11 +++
       +++ ID 000001, SIGNAL 06 +++
       +++ ID 000002, SIGNAL 06 +++
       +++ ID 000003, SIGNAL 06 +++
       +++ ID 000004, SIGNAL 11 +++
       +++ ID 000005, SIGNAL 11 +++
       +++ ID 000006, SIGNAL 11 +++
       ...

#### 3\. crashwalk

当然上面的两种方式都过于鸡肋了，如果你想得到更细致的crashes分类结果，以及导致crashes的具体原因，那么[crashwalk](https://github.com/bnagy/crashwalk)就是不错的选择之一。这个工具基于gdb的exploitable插件，安装也相对简单，在ubuntu上，只需要如下几步即可：

    
    
    $ apt-get install gdb golang
    $ mkdir tools
    $ cd tools
    $ git clone https://github.com/jfoote/exploitable.git
    $ mkdir go
    $ export GOPATH=~/tools/go
    $ export CW_EXPLOITABLE=~/tools/exploitable/exploitable/exploitable.py
    $ go get -u github.com/bnagy/crashwalk/cmd/...

crashwalk支持AFL/Manual两种模式。前者通过读取 **crashes/README.txt**
文件获得目标的执行命令（前面第三节中提到的），后者则可以手动指定一些参数。两种使用方式如下：

    
    
    #Manual Mode
    $ ~/tools/go/bin/cwtriage -root syncdir/fuzzer1/crashes/ -match id -- ~/parse @@
    #AFL Mode
    $ ~/tools/go/bin/cwtriage -root syncdir -afl

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNc79gy1fz0a6mtuf3j31cs0u01kx.jpg-w331s)

两种模式的输出结果都一样，如上图所示。这个工具比前面几种方法要详细多了，但当有大量crashes时结果显得还是十分混乱。

#### 4\. afl-collect

最后重磅推荐的工具便是 _afl-collect_ ，它也是 _afl-utils_
套件中的一个工具，同样也是基于exploitable来检查crashes的可利用性。它可以自动删除无效的crash样本、删除重复样本以及自动化样本分类。使用起来命令稍微长一点，如下所示：

    
    
    $ afl-collect -j 8 -d crashes.db -e gdb_script ./afl_sync_dir ./collection_dir --  /path/to/target --target-opts

但是结果就像下面这样非常直观：

![img](https://images.seebug.org/content/images/2019/03/11/1552285576000-006tNbRwgy1fyl8iay811j31he0t67wh.jpg-w331s)

### 五、代码覆盖率及其相关概念

代码覆盖率是模糊测试中一个极其重要的概念， **使用代码覆盖率可以评估和改进测试过程，执行到的代码越多，找到bug的可能性就越大**
，毕竟，在覆盖的代码中并不能100%发现bug，在未覆盖的代码中却是100%找不到任何bug的，所以本节中就将详细介绍代码覆盖率的相关概念。

#### 1\. 代码覆盖率（Code Coverage）

代码覆盖率是一种度量代码的覆盖程度的方式，也就是指源代码中的某行代码是否已执行；对二进制程序，还可将此概念理解为汇编代码中的某条指令是否已执行。其计量方式很多，但无论是GCC的GCOV还是LLVM的SanitizerCoverage，都提供函数（function）、基本块（basic-block）、边界（edge）三种级别的覆盖率检测，更具体的细节可以参考LLVM的[官方文档](https://clang.llvm.org/docs/SanitizerCoverage.html)。

#### 2\. 基本块（Basic Block）

缩写为BB，指一组顺序执行的指令，BB中第一条指令被执行后，后续的指令也会被全部执行，每个BB中所有指令的执行次数是相同的，也就是说一个BB必须满足以下特征：

  * 只有一个入口点，BB中的指令不是任何 **跳转指令** 的目标。
  * 只有一个退出点，只有最后一条指令使执行流程转移到另一个BB

例如下图中的代码就可以被切割为4个基本块，平时我们在IDA图形模式中看到的就是一个一个的基本块

![img](https://images.seebug.org/content/images/2019/03/11/1552285577000-006tNc79gy1fz1gm5zohnj30sj0ikahx.jpg-w331s)

将上面的程序拖进IDA，可以看到同样被划分出了4个基本块：

![img](https://images.seebug.org/content/images/2019/03/11/1552285577000-006tNc79gy1fz1g5ow0ogj30u00v7gru.jpg-w331s)

#### 3\. 边（edge）

AFL的[技术白皮书](http://lcamtuf.coredump.cx/afl/technical_details.txt)中提到fuzzer通过插桩代码捕获边（edge）覆盖率。那么什么是edge呢？我们可以将程序看成一个控制流图（CFG），图的每个节点表示一个基本块，而edge就被用来表示在基本块之间的转跳。知道了每个基本块和跳转的执行次数，就可以知道程序中的每个语句和分支的执行次数，从而获得比记录BB更细粒度的覆盖率信息。

![img](https://images.seebug.org/content/images/2019/03/11/1552285577000-006tNc79gy1fyt8g4hq6jj30xg0q443h.jpg-w331s)

#### 4\. 元组（tuple）

具体到AFL的实现中，使用二元组(branch_src, branch_dst)来记录 **当前基本块** \+ **前一基本块**
的信息，从而获取目标的执行流程和代码覆盖情况，伪代码如下：

    
    
    cur_location = <COMPILE_TIME_RANDOM>;            //用一个随机数标记当前基本块
    shared_mem[cur_location ^ prev_location]++;        //将当前块和前一块异或保存到shared_mem[]
    prev_location = cur_location >> 1;                //cur_location右移1位区分从当前块到当前块的转跳

实际插入的汇编代码，如下图所示，首先保存各种寄存器的值并设置ecx/rcx，然后调用`__afl_maybe_log`，这个方法的内容相当复杂，这里就不展开讲了，但其主要功能就和上面的伪代码相似，用于记录覆盖率，放入一块共享内存中。

![img](https://images.seebug.org/content/images/2019/03/11/1552285577000-006tNc79gy1fz2iunorubj312m0jsgsp.jpg-w331s)

### 六、计算代码覆盖率

了解了代码覆盖率相关的概念后，接下来看看如何计算我们的测试用例对前面测试目标的代码覆盖率。

这里需要用到的工具之一是 **GCOV** ，它随gcc一起发布，所以不需要再单独安装，和afl-gcc插桩编译的原理一样，gcc编译时生成插桩的程序，用于在执行时生成代码覆盖率信息。

另外一个工具是 **LCOV** ，它是GCOV的图形前端，可以收集多个源文件的gcov数据，并创建包含使用覆盖率信息注释的源代码HTML页面。

最后一个工具是[afl-cov](https://github.com/mrash/afl-cov)，可以快速帮助我们调用前面两个工具处理来自afl-fuzz测试用例的代码覆盖率结果。在ubuntu中可以使用`apt-get install afl-cov`安装afl-cov，但这个版本似乎不支持分支覆盖率统计，所以还是从Github下载最新版本为好，下载完无需安装直接运行目录中的Python脚本即可使用：

    
    
    $ apt-get install lcov
    $ git clone https://github.com/mrash/afl-cov.git
    $ ./afl-cov/afl-cov -V
    afl-cov-0.6.2

还是以Fuzz libtiff为例，计算Fuzzing过程的代码覆盖率流程如下：

第一步，使用gcov重新编译源码，在CFLAGS中添加`"-fprofile-arcs"`和`"-ftest-coverage"`选项，可以在`--prefix`中重新指定一个新的目录以免覆盖之前alf插桩的二进制文件。

    
    
    $ make clean
    $ ./configure --prefix=/root/tiff-4.0.10/build-cov CC="gcc" CXX="g++" CFLAGS="-fprofile-arcs -ftest-coverage" --disable-shared
    $ make
    $ make install

第二步，执行afl-cov。其中 _-d_ 选项指定afl-fuzz输出目录； _—live_ 用于处理一个还在实时更新的AFL目录，当afl-fuzz停止时，afl-cov将退出； _–enable-branch-coverage_ 用于开启边缘覆盖率（分支覆盖率）统计； _-c_
用于指定源码目录；最后一个 _-e_ 选项用来设置要执行的程序和参数，其中的 _AFL_FILE_ 和afl中的”@@”类似，会被替换为测试用例，
_LD_LIBRARY_PATH_ 则用来指定程序的库文件。

    
    
    $ cd ~/tiff-4.0.10
    $ afl-cov -d ~/syncdir --live --enable-branch-coverage -c . -e "cat AFL_FILE | LD_LIBRARY_PATH=./build-cov/lib ./build-cov/bin/tiff2pdf AFL_FILE"

成功执行的结果如下所示：

![img](https://images.seebug.org/content/images/2019/03/11/1552285578000-006tNbRwgy1fyl9dkjqtcj31fi0hidml.jpg-w331s)

我们可以通过 _—live_
选择，在fuzzer运行的同时计算覆盖率，也可以在测试结束以后再进行计算，最后会得到一个像下面这样的html文件。它既提供了概述页面，显示各个目录的覆盖率；也可以在点击进入某个目录查看某个具体文件的覆盖率。

![img](https://images.seebug.org/content/images/2019/03/11/1552285578000-006tNbRwgy1fyl9e8v4cmj31340u0tod.jpg-w331s)

点击进入每个文件，还有更详细的数据。每行代码前的数字代表这行代码被执行的次数，没有执行过的代码会被红色标注出来。

![img](https://images.seebug.org/content/images/2019/03/11/1552285578000-006tNbRwgy1fyl9esockxj31hz0u0wu1.jpg-w331s)

#### 参考资料

[1] [INTRO TO AMERICAN FUZZY LOP – FUZZING WITH ASAN AND
BEYOND](https://countuponsecurity.com/2018/04/24/intro-to-american-fuzzy-lop-fuzzing-with-asan-and-beyond/)

[2] [Fuzzing with
AFL](https://media.defcon.org/DEF%20CON%2026/DEF%20CON%2026%20workshops/DEFCON-26-Workshop-Jakub-Botwicz-and-Wojciech-Rauner-Fuzzing-with-AFL-\(American-Fuzzy-Lop\).pdf)

[3] [Clang 9 documentation –
SanitizerCoverage](https://clang.llvm.org/docs/SanitizerCoverage.html)

[4]
[honggfuzz漏洞挖掘技术深究系列](http://riusksk.me/2018/07/29/honggfuzz%E6%BC%8F%E6%B4%9E%E6%8C%96%E6%8E%98%E6%8A%80%E6%9C%AF1/)

[5] [How Much Test Coverage Is Enough For Your Testing
Strategy?](https://www.seguetech.com/how-much-test-coverage-enough-testing-strategy/)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/842/>

