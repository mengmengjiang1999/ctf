上个月末无聊的划水时间段内，在推上看到有人发了一篇关于如何结合去年新发布的符号执行Symcc与模糊测试引擎AFL，以提升Fuzz效率的视频贴。打开这个链接后才发现是个卖课的，emmm....
, 看价格 **£1499** 果断打扰了，果然没钱的都不配学安全吗23333；原技术文章看来是看不到了，只能靠公开的一段视频还原操作。

## 背景介绍

虽然有很多大佬肯定已经十分熟悉模糊测试和符号执行了，还是简单介绍一下背景知识，这样更有连贯性。

### 模糊测试 AFL

模糊测试（fuzz testing, fuzzing）是一种软件测试技术。
其核心思想是將自动或半自动生成的随机数据输入到一个程序中，并监视程序异常，如崩溃，断言（assertion）失败，以发现可能的程序错误，比如内存泄漏。
模糊测试常常用于检测软件或计算机系统的安全漏洞。

模糊测试诞生于1988年秋季的一个黑暗暴风雨之夜 [[Takanen et al,
2008.](http://us.artechhouse.com/Fuzzing-for-Software-Security-Testing-and-Quality-Assurance-Second-Edition-P1930.aspx)]。巴顿·米勒教授坐在麦迪逊威斯康星州的公寓里，通过一条1200波特的电话线连接到他所属大学的计算机。阵阵的雷暴在线路上造成噪音，这些噪音又导致两端的UNIX命令获得错误的输入，并导致崩溃。频繁的崩溃使他感到惊讶—我们编写的程序不是应该十分强大吗？作为一名科学家，他想探究该问题的严重程度及其原因。因此，他为威斯康星大学麦迪逊分校的学生编写了一个编程练习，而该练习将使他的学生创建第一个模糊测试器。

这项作业的原文描述是这样的：

> The goal of this project is to evaluate the robustness of various UNIX
> utility programs, given an unpredictable input stream. [...] First, you will
> build a fuzz generator. This is a program that will output a random
> character stream. Second, you will take the fuzz generator and use it to
> attack as many UNIX utilities as possible, with the goal of trying to break
> them.
>
>
> 该项目的目标是在给定不可预测的输入流的情况下评估各种UNIX实用程序的健壮性。[...]首先，您将构建一个模糊发生器。这是一个将输出随机字符流的程序。其次，您将使用模糊发生器，并使用它来攻击尽可能多的UNIX实用程序，以试图破坏它们。

这个作业在不经意间抓住了模糊测试的本质：创建随机的输入，并持续性观察它是否会破坏目标应用程序，理论上只要运行足够长的时间，我们就会看到错误的发生。

`AFL`（american fuzzy lop）最初由Michał Zalewski开发，和libFuzzer等一样是基于覆盖引导（Coverage-guided）的模糊测试工具，它通过记录输入样本的代码覆盖率，从而调整输入样本以提高覆盖率，增加发现漏洞的概率。其工作流程大致如下：

> 1.从源码编译程序时进行插桩，以记录代码覆盖率（Code Coverage）
>
> 2.选择一些输入文件，作为初始测试集加入输入队列（queue）
>
> 3.将队列中的文件按一定的策略进行“突变”
>
> 4.如果经过变异文件更新了覆盖范围，则将其保留添加到队列中
>
> 5.上述过程会一直循环进行，期间触发了crash的文件会被记录下来

![image-20210319132122277](https://image.3001.net/images/20210319/1616138021_60544f259a40a254a9d5f.png!small)

### 符号执行 Symcc

符号执行简单来说是在目标程序的执行过程中跟踪中间值是如何计算的，每一个中间值都可以表示为程序输入的一个公式。在任何点，系统都会使用这个公式查看这个点是否可达，这个指针是否为空等。如果答案是确定的，那么符号执行引擎将会提供测试用例，一个新的输入例子来触发对应的行为。所以符号执行可以被方便的用来探测程序路径以及触发bug。

新的符号执行Symcc发表于去年顶会USENIX’20，论文名称为Symbolic execution with SYMCC: Don’t
interpret, compile!

那么Symcc和它的前辈们又有什么不同呢？论文作者Aurélien Francillon认为传统符号执行主要分为两类： **IR-based** 和
**IR-less** 。

 **IR-based**
是指无论测试对象如何，先把目标的二进制程序给转换到IR层（中间表达形式）再进行抽象解释，其缺点是特别容易路径爆炸。常见用此方法的符号执行有angr、KLEE和Mayhem，主要过程如下图所示：

![image-20210319094028131](https://image.3001.net/images/20210319/1616138029_60544f2d1345ce46932ea.png!small)

 **IR-less**
是指符号执行引擎通过动态插桩技术（利用PIN插桩框架等）先对二进制程序插桩，执行部分指令后再构造符号表达式。其优点是快，缺点是插入的代码函数可能无法生成正确的符号表达式，且较依赖于指令集。常见用此方法的符号执行有Triton、QSYM、SAGE和Driller，主要过程如下图所示：

![image-20210319094624987](https://image.3001.net/images/20210319/1616138034_60544f320f23c8d9413d3.png!small)

作者提出的SymCC不同点在于，直接在编译期就开始在生成的IR上植入符号执行相关代码，进一步提升性能；其流程大致如下：

![image-20210319094919700](https://image.3001.net/images/20210319/1616138040_60544f388c76df9720b3b.png!small)

## 开始结合

整体的结合流程没什么新花样，基本是按照 安装各种包环境—> 编译简单的后端/功能更强的qsym后端 —> 用symcc编译llvm的libcxx —>
开始尝试fuzz 的过程循序渐进。

### 安装各种环境

先安装各种包和依赖：

    
    
    sudo apt-get install -y cargo \
                            clang-10 \
                            cmake \
                            g++ \
                            git \
                            libz3-dev  \
                            llvm-10-dev \
                            llvm-10-tools \
                            ninja-build \
                            python3-pip \
                            zlib1g-dev 
    pip3 install lit
    

这里的LLVM 要求是 8, 9, 10 或者11 ，C++编译器要支持 C++17。实际安装过程中有些unbuntu版本可能无法直接apt-get，使用llvm官方https://apt.llvm.org/ 的包支持。

随后安装Z3，要求版本号大于4.5

    
    
    git clone https://github.com/Z3Prover/z3 
    cd z3 
    python scripts/mk_make.py 
    cd build 
    make 
    sudo make install
    

这里有点小坑，用该方式安装的z3可能在后面编译时llvm无法找到路径。如果报此类似错误的，该步可用cmake的Ninja进行编译，指路链接：https://github.com/Z3Prover/z3/blob/master/README-CMake.md

然后安装afl，没什么可说的先安原版

    
    
    git clone -b v2.56b https://github.com/google/AFL.git afl 
    cd afl && make
    

下载symcc的源码做好之后编译backend的准备

    
    
    git clone https://github.com/eurecom-s3/symcc symcc_source 
    cd symcc_source 
    git submodule init 
    git submodule update
    

### 编译backend

symcc带了两种后端，一种是功能简单（simple）的；另一种是qsym的后端，与前者相比功能性更强，我们两种都编译一下。在配置构建时，选项都将通过“
-D”传递给CMake，常见选项如下表所示：

选项| 作用  
---|---  
\- QSYM_BACKEND=ON/OFF (default OFF)|
是否编译QSYM后端，若否即为编译simple后端；每次执行时可以使用LD_LIBRARY_PATH在后端之间切换  
\- TARGET_32BIT=ON/OFF (default OFF)| 启用64位主机对32位编译的支持  
\- LLVM_DIR/LLVM_32BIT_DIR (default empty)| 提供编译时llvm的位置  
\- Z3_DIR/Z3_32BIT_DIR (default empty)| 提供编译时Z3的位置  
\- Z3_TRUST_SYSTEM_VERSION (default OFF)|
信任系统版本的Z3，不检查Z3版本的兼容性；如果Z3的安装版本太旧，则可能发生编译错误。  
  
首先编译简单的后端，这里的LLVM_DIR指向你所用版本llvm位置

    
    
    mkdir symcc_build_simple 
    cd symcc_build_simple 
    CC=clang-10 CXX=clang++-10 cmake -G Ninja \
        -DQSYM_BACKEND=OFF \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo \
        -DZ3_TRUST_SYSTEM_VERSION=on \
        -DLLVM_DIR=/usr/lib/llvm-10/cmake \
        ../symcc_source \
        && ninja check
    

![907a1b17-80d4-4011-88c9-85d94c051ca7](https://image.3001.net/images/20210319/1616138047_60544f3fa51a59f747ced.gif!small)

后面在ninja check时会有8个错误，不影响后面的正常执行。（参考视频的编译过程中也有错误）

下面编译qsym的后端，与前者相比区别就是把DQSYM_BACKEND改成ON

    
    
    mkdir symcc_build_qsym 
    cd symcc_build_qsym
    cmake -G Ninja \
                -DQSYM_BACKEND=ON \
                -DCMAKE_BUILD_TYPE=RelWithDebInfo \
                -DZ3_TRUST_SYSTEM_VERSION=on \
                -DLLVM_DIR=/usr/lib/llvm-10/cmake \
                -DZ3_DIR=/home/fstark/symcc_afl/z3/build \
                ../symcc_source \
                && ninja check \
                && cargo install --path ../symcc_source/util/symcc_fuzzing_helper
    

check时也会有一些错误，问题不大。

![1ead03ab-dfe6-43d1-ac59-a8ccaf4b041a](https://image.3001.net/images/20210319/1616138055_60544f473b0aeef36b2ad.gif!small)

### 用symcc编译llvm的libcxx

对于更加复杂的C++代码，symcc提供了两种解决方法。一种是使用系统提供的C
++标准库。这是最简单的不需要额外的编译，但是它有一个重要的缺点：会影响符号执行的过程。另一种方法是自己编译一个检测的C
++标准库，这样就可以通过库跟踪数据，但这需要构建库并针对它编译所有代码。

建立C ++标准库是一项一次性的工作，建一次后可以在所有后续的C ++编译中使用，每当我们使用libc++就会自动使用我们编译的llvm标准库实现。  
编译过程如下：

    
    
    git clone -b llvmorg-10.0.1 --depth 1 https://github.com/llvm/llvm-project.git llvm_source 
    mkdir libcxx_symcc_install 
    mkdir libcxx_symcc_build 
    cd libcxx_symcc_build 
    export SYMCC_REGULAR_LIBCXX=yes SYMCC_NO_SYMBOLIC_INPUT=yes \
        && cmake -G Ninja ../llvm_source/llvm \
            -DLLVM_ENABLE_PROJECTS="libcxx;libcxxabi" \
            -DLLVM_TARGETS_TO_BUILD="X86" \
            -DLLVM_DISTRIBUTION_COMPONENTS="cxx;cxxabi;cxx-headers" \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX=$BASE/libcxx_symcc_install \
            -DCMAKE_C_COMPILER=$BASE/symcc_build_simple/symcc \
            -DCMAKE_CXX_COMPILER=$BASE/symcc_build_simple/sym++ \
        && ninja distribution && ninja install-distribution
    

请自己手动把$BASE指向之前准备工作的文件位置

![752a8d34-5777-4da8-87c7-ac26acc6047a](https://image.3001.net/images/20210319/1616138073_60544f597b0d6a3f1f46a.gif!small)

### 开始尝试Fuzz！

这里我们准备一个特殊的苛刻例子

    
    
    #include <stdio.h>
    #include <stdint.h> 
    #include <unistd.h> 
    #include <string.h> 
    #include <stdlib.h> 
    
    int foo(char *arr, int t1){ 
        int i = 0;
    
        if (arr[i++] == 'c') return 0; 
        if (arr[i++] == 'd') return 1; 
        if (arr[i++] == 'c') return 2; 
        if (arr[i++] == 'c') return 3; 
        if (arr[i++] == 's') return 4; 
        if (arr[i++] == 'b') return 5; 
        if (arr[i++] == 's') return 6; 
        if (arr[i++] == 'g') return 7; 
    
        if (*(int*)arr != 0xdeadbeef )return 0; 
    
        //Can we trigger this code?
        return (int)(20 / t1); 
    }
    
    int main(int argc, char* argv[]){ 
        //open file
        FILE *f = fopen(argv[1],"rb"); 
    
        // get file size 
        fseek(f, 0, SEEK_END);
        long fsize = ftell(f);
    
        // read file contents 
        fseek(f, 0, SEEK_SET);
        char *string = malloc(fsize + 1);
        fread(string, 1, fsize, f);
        fclose(f); 
    
        // pass string to foo 
        int retval = foo(string, argc-2);
    
        free(string); 
        return retval;
    }
    

根据这段源码，我们可以判断出当且仅当文件输入为0xdeadbeef 时，return (int)(20 /
t1)会出现除零错误，而该例子单纯使用afl是难以发现错误的。

我们分别使用qsym编译出的后端symcc和afl对其进行编译，并且创建一个样例AAAAAAA

    
    
    afl-clang -O0 int_check.c -o afl_int_check
    ../symcc_build_qsym/symcc -O0 int_check.c -o symcc_int_check
    
    
    mkdir corpus
    echo "AAAAAAAAAAAAAAAAAAAAAAAA" > corpus/seed
    

![image-20210316201931648](https://image.3001.net/images/20210319/1616138106_60544f7a5c81f38bcbc16.png!small)

之后就开始运行吧，我们使用afl的并行模式

    
    
    afl-fuzz -M fuzz1 -i corpus/ -o out -m none -- ./afl_int_check @@
    
    afl-fuzz -S fuzz2 -i corpus/ -o out -m none -- ./afl_int_check @@
    
    ~/.cargo/bin/symcc_fuzzing_helper -o out -a fuzz2 -n symcc -- ./symcc_int_check @@
    

这里symcc_fuzzing_helper的参数中-o指向afl的out目录，-a指向要辅助的afl进程名字，如上所示这里我就是fuzz2.

symcc_fuzzing_helper其实就是在使用afl生产的testcase进行符号执行，如果它认为样例有趣就会生成新的，并将它传送到正在执行的afl队列里，afl就能够使用该新生成样例进行测试，这一流程辅助了afl能够到达一些之前无法到达的路径。

这里有个小坑，单纯执行afl时afl-fuzz命令后面的--可带也可不带，但是symcc_fuzzing_helper是通过检测afl-fuzz里--后面命令执行的，所以如果我们在afl-fuzz后习惯性不加--就可能导致symcc无有效的输出结果。

一切准备就绪，开始运行吧！

![](https://image.3001.net/images/20210319/1616148700_605478dcb10e3928901df.gif!small)

我们惊喜的发现单纯fuzz难以找到的漏洞，在symcc_fuzzing_helper的协助下，直接就找到了crash。

![81de9aff-f7eb-449c-984c-72881a98fac1](https://image.3001.net/images/20210319/1616138141_60544f9d165d9e703f8a8.gif!small)

简单分析一下，用Hexdump看到crash真的是0xdeadbeef，symcc辅助AFL找到了使目标程序崩溃的testcase。

## 总结

使用符号执行Symcc与模糊测试引擎Afl的简单验证成功了，之后可以就试一试现实中的一些项目，比如论文中提的Tcpdump之类的；还可以考虑将Symcc与其他模糊测试引擎相结合，比如Afl++，在各种算法加持下的Afl++再结合符号执行可能会有更好的效果。

最后特别感谢Symcc发明人和论文的原作者 Aurélien Francillon 与 ADALogics 的安全研究员David
Korczynski，它们在推特上帮助了我很多，同时感谢Discord的Fuzzing板块讨论让我有兴趣进行各种新的尝试，我仍有很多需要学习的地方。

![image-20210319120238731](https://image.3001.net/images/20210319/1616138146_60544fa2c1bf5e525acf5.png!small)

## 参考资料

> 带你搞懂符号执行的前世今生与最近技术
>
> https://www.anquanke.com/post/id/231413
>
> G.O.S.S.I.P 学术论文推荐
>
> https://wemp.app/posts/40a16228-7a86-4985-b7c2-b3507e3fc161
>
> Symcc源码  
> https://github.com/eurecom-s3/symcc/
>
> 入门afl
>
> https://i-m.dev/posts/20191001-225746.html

