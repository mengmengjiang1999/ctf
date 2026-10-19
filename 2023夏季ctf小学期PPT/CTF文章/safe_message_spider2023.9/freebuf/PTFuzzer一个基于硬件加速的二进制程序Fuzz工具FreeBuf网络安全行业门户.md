## 简介

 **PTFuzzer是基于AFL框架实现的一款开源fuzz工具，它采用了Intel Processor
Trace硬件部件来收集程序执行的路径信息，改进了原来AFL通过编译插桩方式获取程序执行路径信息的方法。和AFL相比，硬件收集的路径信息更加丰富，同时可以直接对目标程序进行fuzz，无需源码支持。**

## 技术背景

### 1.1 AFL

Fuzz（也叫模糊测试）是自动化挖掘软件漏洞的一种有效方法。基于反馈的fuzz技术是目前学术界和工业界的研究热点，而其中的代表就是AFL。但是AFL存在一个问题，即需要对被测试的程序进行编译插桩后才能fuzz。这也意味着必须要有目标程序的源代码，而且必须是C代码才行。AFL的Qemu模式采用动态二进制翻译的手段获取反馈信息，但是这种基于模拟仿真的方法开销太大（5倍以上的开销很常见），基本上不实用。

### 1.2 Intel Processor Trace

Intel Processor
Trace（PT）是Intel在其第五代CPU之后引入的一个硬件部件。该硬件部件的作用是记录程序执行中的分支信息，从而帮助构建程序运行过程中的控制流图。在默认情况下CPU的PT部件是处于关闭状态，这意味着CPU不会记录程序的分支信息，因此也不会产生任何开销。通过写MSR寄存器可以打开PT开关。在打开PT开关后，CPU开始记录分支指令信息，所记录的信息以压缩数据包的形式存储在内存中。由于分支信息记录完全由硬件完成，因此开销非常小，一般在5%以下，这个开销对于大多数应用来讲基本上可以忽略不计。PT部件最初被设计用来重构程序的控制流图，目的是为了帮助调试和分析。最早利用PT做fuzz的工具是kAFL，其结果发表在安全领域的四大顶级学术会议之一的USENIX
Security上。但是kAFL是一个针对内核的fuzz工具，而PTFuzzer是针对应用程序的fuzz工具，这两者的设计会有很多不同。

## 特点和限制

### 2.1特点

PTFuzzer最大的特点是不需要目标程序有源码，这在很多方法是非常有用的。首先，对于很多闭源程序的测试很有优势。例如，某公司对外公布了一个二进制程序的发行版。这时拿不到程序的源代码用AFL就无法测试，而用PTFuzzer就可以。另外，即便是对于一些有源码的程序，可能由于其编译环境极为复杂，用AFL来进行编译插桩变得非常繁琐和耗时，有时也会出现不成功的情况。还有一种情况是对于那些非C语言编写的二进制程序，AFL就无能为力了。例如自己在测试pandoc程序时，发现pandoc是用Haskell语言编写的。这时用AFL就无法进行编译插桩，而使用PTFuzzer进行测试，只需要简单通过apt-get安装一个pandoc可执行程序就OK了。

### 2.2 限制

目前PTFuzzer只支持Linux操作系统，并且要求Linux内核的版本至少是4.13.0.
我们测试过Ubuntu16.04.4和Ubuntu17.10，都是没有问题的。另外，因为使用了PT硬件部件，PTFuzzer要求5代以上的CPU。

## 使用方法

### 3.1 从github上下载源码

    
    
    git clone [https://github.com/hunter-ht-2018/ptfuzzer.git](https://github.com/hunter-ht-2018/ptfuzzer.git3.2)

### [3.2](https://github.com/hunter-ht-2018/ptfuzzer.git3.2) 编译安装

编译之前先安装依赖项，ptfuzzer依赖的程序和库包括python，capstone，cle以及msr-tools。在源码目录下有个check_dep.sh脚本，可以直接运行安装这些依赖项。Ptfuzzer采用CMake编译：

    
    
    cd ptfuzzer/
    mkdir build
    cd build
    cmake ../ -DPREFIX=.
    make
    make install

以上命令会在build目录下生成bin目录，其中包括了运行ptfuzzer所需的所有程序。afl-ptfuzz：核心fuzz二进制程序ptfuzzer.py：对alf-ptfuzz的python封装，主要用来处理参数，解析目标二进制程序。

### 3.3 运行

在运行之前需要打开一些开关，这个和AFL是相同的，可以通过运行config-run.sh来实现。以测试pandoc程序为例，首先安装

pandoc：apt install pandoc

然后准备一个docx的种子放入in_dir中，最后运行ptfuzzer开始测试：

    
    
    sudo python ./bin/ptfuzzer.py "-i ./in_dir -o ./out_dir" "/usr/bin/pandoc -f docx -t html"   
    

运行状态如图所示：  

![fuzz_pandoc.png](https://image.3001.net/images/20180715/15316218937446.png!small)

注意：运行ptfuzzer需要root权限。

### 3.4 参数配置

ptfuzzer有一些运行时参数可以配置，这些参数包括： **BRANCH_MODE，MEM_LIMIT，PERF_AUX_BUFFER_SIZE** 。

其中 **BRANCH_MODE**
是指分支收集模式，其值可以是TIP_MODE或者TNT_MODE。如果采用TIP_MODE，那么ptfuzzer只解析PT收集到的TIP包（一般为非条件跳转），如果采用TNT_MODE，则不但解析TIP包，而且解析TNT包（条件跳转）。TNT_MODE更加精确，开销也较大一些。默认情况下ptfuzzer采用TNT_MODE。

 **MEM_LIMIT** 是只目标测试程序的最大内存限制，单位为MB。这个相当于AFL的-m参数。如果目标程序由于使用了太大的内存而不能运行，需要考虑增大MEM_LIMIT的设置。

 **PERF_AUX_BUFFER_SIZE**
是指存储PT数据包的缓存大小，单位为MB。如果目标程序一次运行时间太长，可能会产生特别多的分支跳转信息，导致缓存不够，这时可以考虑增大PERF_AUX_BUFFER_SIZE的设置。在当前运行目录

下编辑一个ptfuzzer.conf的文件可以配置这些参数，参考形式为：

    
    
    #BRANCH_MODE=TNT_MODE
    BRANCH_MODE=TIP_MODE
    MEM_LIMIT=100            # afl -m argument
    PERF_AUX_BUFFER_SIZE=32  # the size of buffer used to store PT packets.
    

## 总结

PTFuzzer采用Intel CPU最新的PT部件来收集分支信息，解决了AFL需要源码支持的问题，能够方面的挖掘Linux中的二进制程序漏洞。

 ***本文作者：hunterx，转载请注明来自FreeBuf.COM**  

