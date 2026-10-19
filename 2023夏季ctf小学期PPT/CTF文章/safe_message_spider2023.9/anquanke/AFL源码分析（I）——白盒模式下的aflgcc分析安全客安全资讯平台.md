# AFL源码分析（I）——白盒模式下的afl-gcc分析

阅读量 **313813**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-21 10:00:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)

## 0x00 写在前面

###  本文所用目标文件

  1. 使用`sudo apt-get install autoconf`安装工具包
  2. 准备待测文件，本文使用`ctf-wiki`中的`ret2text.c`作为目标文件
  3. 执行`autoscan ./`生成`configure.scan`文件如果在此步骤中收到了错误信息，形如： 
    
        Unescaped left brace in regex is deprecated, passed through in regex; marked by <-- HERE in m/\${ <-- HERE [^\}]*}/ at /usr/bin/autoscan line 361.
    

请执行`sudo vi
/usr/bin/autoscan`，编辑`/usr/bin/autoscan`文件，将第`361`行的`s/\${[^\}]*}//g;`变更为`s/\$\{[^\}]*\}//g;`

  4. 接下来将`configure.scan`重命名为`configure.ac`，并修改相关内容 
    
        #                                               -*- Autoconf -*-    # Process this file with autoconf to produce a configure script.
    
    AC_PREREQ([2.69])
    AC_INIT([ret2text], [1.0], [[lanjing@furry.com](mailto:lanjing@furry.com)])
    AM_INIT_AUTOMAKE
    AC_CONFIG_SRCDIR([ret2text.c])
    AC_CONFIG_HEADERS([config.h])
    
    # Checks for programs.
    AC_PROG_CC
    
    # Checks for libraries.
    
    # Checks for header files.
    AC_CHECK_HEADERS([stdlib.h])
    
    # Checks for typedefs, structures, and compiler characteristics.
    
    # Checks for library functions.
    
    AC_OUTPUT(Makefile)
    

![](https://p4.ssl.qhimg.com/t01c8396fa686980387.png)

  5. 执行`aclocal`，生成`aclocal.m4`
  6. 执行`autoconf`，生成相关配置文件
  7. 执行`autoheader`，生成`config.h.in`
  8. 建立`Makefile.am`并修改其内容为： 
    
        AUTOMAKE_OPTIONS=foreign
    bin_PROGRAMS=ret2text
    ret2text_SOURCES=ret2text.c
    

  9. 最后执行`automake --add-missing`，生成`configure`

## 0x01 关于AFL白盒模式

当应用源代码可用时，可以通过使用配套的代码注入工具进行代码插桩，该工具可以在任何第三方代码的标准构建过程中替代`gcc`或`clang`使用。经过此工具进行代码的代码插桩对待测程序性能的影响相当小。结合`afl-fuzz`实现的其他优化，大多数程序可以比传统模式更快的被模糊测试。一个通用的代码编译方式是：

    
    
    CC=/path/to/afl/afl-gcc ./configure
    make clean all
    

## 0x02 afl-gcc源码分析

`afl-gcc`的`main`函数的起始进行了一系列的检查，包括调用`isatty(2)`检查`stderr`是否为终端环境、调用`getenv`检查`AFL_QUIET`环境变量是否存在、检查参数个数是否合法等。检查结束后，执行的是以下核心代码：

    
    
    find_as(argv[0]);
    edit_params(argc, argv);
    execvp(cc_params[0], (char**)cc_params);
    

###  `find_as`函数

此函数尝试在`AFL_PATH`或从`argv[0]`中找到所需的“伪” GNU汇编器。 **如果此步骤失败，将产生致命错误导致`afl-gcc`流程中止。**

  1. 检查`AFL_PATH`是否已经设置，若已设置，则将`as_path`设置为`$[AFL_PATH]/as`，随后检查`as_path`是否可以访问，若可访问， **返回上层函数** 。
  2. 若未设置`AFL_PATH`，寻找传入的路径中最后一个`/`之后的字符串，若找到，则将传入的路径之后拼接`/afl-as`，赋值给`as_path`，随后检查`as_path`是否可以访问，若可访问， **返回上层函数** 。
  3. 若未设置`AFL_PATH`且未找到目标字符串，使用默认路径`/usr/local/lib/afl/as`，赋值给`as_path`，随后检查`as_path`是否可以访问，若可访问， **返回上层函数** 。
  4. **引发致命错误`Unable to find AFL wrapper binary for 'as'. Please set AFL_PATH`，中断`afl-gcc`**

###  `edit_params`函数

此函数将参数传入`cc_params`，进行必要的编辑。`cc_params`的空间由`ck_alloc`分配，长度为`(argc + 128) *
sizeof(u8*)`

  1. 通过检查`argv[0]`的最后一个`/`后是否为`afl-clang`来检查是否为`clang`编译器模式，若是，将`clang_mode`置位。
  2. 修正主编译器路径，即将`afl-clang++`、`afl-clang`、`afl-g++`、`afl-gcj`、`afl-gcc`替换为正确的路径并将其作为`cc_params[0]`，若`AFL_CXX`、`AFL_CC`、`AFL_CXX`、`AFL_GCJ`、`AFL_CC`（注：`AFL_CXX`、`AFL_CC`同时生效于`clang++/g++`、`clang/gcc`，这两种编译器将在函数入口处进行区分）环境变量已被设置，则使用环境变量中的值。否则，直接替换为`clang++`、`clang`、`g++`、`gcj`、`gcc`关键字。
  3. 随后此函数开始遍历已设置的所有选项，当检测到`-B`选项存在时，将显示一个警告以提示此选项将被`afl`编译器覆盖， **随后继续遍历下一个选项** ，此选项将被忽略。 
    * `-B`选项表示编译器系列文件(包括编译器本身这个可执行文件、库文件、依赖文件、数据文件)所在目录，当使用`-B`参数指定一个自定义目录时，编译器将首先在指定的目录查找编译器所需要的文件，包括但不限于`cpp`(预处理程序，它是一种宏处理器，编译器会自动使用该宏处理器在编译之前对程序中的宏定义进行转换), `cc1`(编译器，用于将源代码文件转换为汇编码文件), `as`(汇编器，用于将汇编码文件转换为字节码文件) 以及`ld`(链接器，将程序所需的各种字节码文件汇总，链接到一起，输出可执行文件)，若`-B`不存在，编译器将会在默认路径`/usr/lib/gcc/`或`/usr/local/lib/gcc/`查找，若依然不存在，将在`PATH`(即环境变量)中的路径寻找。
  4. 当`-integrated-as`选项存在时， **继续遍历下一个选项** ，此选项将被忽略。 
    * `-integrated-as`选项表示`Clang`编译器将使用`LLVM`集成汇编器进行代码的编译工作。对于`Clang`编译器而言，既可以使用`LLVM`提供的集成汇编器进行汇编工作，也可以在`GNU`系统中使用`GNU`汇编器。
  5. 当`-pipe`选项存在时， **继续遍历下一个选项** ，此选项将被忽略。 
    * `-pipe`选项表示在编译的各个阶段之间使用管道而不是临时文件进行通信。 注意，在某些无法从管道读取数据的汇编器的系统上，这种方法无法正常工作，但是`GNU`汇编器可以使用此方式进行通信。
  6. 当`-fsanitize=address`或`-fsanitize=memory`选项存在时，将`asan_set`标志位进行置位。 
    * 这两个选项都是`Clang`编译器所使用的选项，`-fsanitize=address`代表启用`LLVM`的内存泄漏检测器，`-fsanitize=memory`代表启用`LLVM`的未初始化变量引用检测器。
  7. 当`FORTIFY_SOURCE`选项存在时，将`fortify_set`标志位进行置位。
  8. 将当前选项加入`cc_params`中， **继续遍历下一个选项** 。
  9. 遍历结束后，向`cc_params`中添加参数`-B <as_path>`(`as_path`由`find_as`函数获取并设置)。
  10. 如果`clang_mode`标志位置位，向`cc_params`中添加参数`-no-integrated-as`。
  11. 如果`AFL_HARDEN`环境变量被设置，向`cc_params`中添加参数`-fstack-protector-all`。 
    * `-fstack-protector-all`选项表示启用对所有函数的栈保护机制(`Canary`)。
  12. 如果`fortify_set`标志位未置位，向`cc_params`中添加参数`-D_FORTIFY_SOURCE=2`。 
    * `-D_FORTIFY_SOURCE`选项表示将开启缓冲区溢出保护，当此参数的级别为`2`时，代表启用了较强的保护。同时，此保护需要同时与`-O2`/`-O3`参数使用，否则将不会生效。
  13. 如果`asan_set`标志位置位，设置环境变量`AFL_USE_ASAN=1`。
  14. 如果`asan_set`标志位未置位，但是环境变量`AFL_USE_ASAN`已被设置，检查`AFL_USE_MSAN`或`AFL_HARDEN`环境变量是否被设置，如果两个环境变量之一被设置，则中断`afl-gcc`过程。若两个标志均未被设置，则向`cc_params`中添加参数`-U_FORTIFY_SOURCE`以及`-fsanitize=address`。
  15. 如果`asan_set`标志位未置位，环境变量`AFL_USE_ASAN`未被设置，但是环境变量`AFL_USE_MSAN`已被设置，检查`AFL_USE_ASAN`或`AFL_HARDEN`环境变量是否被设置，如果两个环境变量之一被设置，则中断`afl-gcc`过程。若两个标志均未被设置，则向`cc_params`中添加参数`-U_FORTIFY_SOURCE`以及`-fsanitize=memory`。 
    * 这里不允许同时设置`AFL_USE_MSAN`、`AFL_USE_ASAN`、`AFL_HARDEN`的原因是因为若同时设置将导致运行速度过慢。
  16. 若环境变量`AFL_DONT_OPTIMIZE`未被设置，向`cc_params`中添加参数`-g`、`-O3`、`-funroll-loops`、`-D__AFL_COMPILER=1`、`-DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1`。 
    * `-g`选项表示在编译过程中输出调试信息。
    * `-O3`选项表示启动最高等级的编译优化。
    * `-funroll-loops`选项表示进行循环的编译优化，即展开循环，以较小的恒定迭代次数完全除去循环。执行循环强度消除并消除在循环内部使用的变量。这是用简单而快速的操作(如加法和减法)替代耗时操作(如乘法和除法)的过程。
    * `-DXXXX`选项表示在编译时定义宏，在此例中相当于`#define __AFL_COMPILER 1`、`#define FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION 1`
  17. 若环境变量`AFL_NO_BUILTIN`被设置，向`cc_params`中添加参数`-fno-builtin-strcmp`、`-fno-builtin-strncmp`、`-fno-builtin-strcasecmp`、`-fno-builtin-strncasecmp`、`-fno-builtin-memcmp`、`-fno-builtin-strstr`、`-fno-builtin-strcasestr`。 
    * `-fno-builtin-*`选项表示不使用指定的内建函数。例如，`-fno-builtin-strcmp`表示不使用内建的`strcmp`函数，而是使用源代码中的`strcmp`函数。

###  `execvp`函数

此函数用于执行`cc_params[0] cc_params[1] cc_params[1]......`命令。

## 0x03 afl-gcc实例分析

使用`CC=/home/error404/AFL/afl-gcc
./configure`生成的`Makefile`与使用`./configure`生成的`Makefile`对比，主要有以下区别：

![](https://p4.ssl.qhimg.com/t016a6ce6bc0dfff7a8.png)

![](https://p4.ssl.qhimg.com/t0148f0751bfb195e7d.png)

此时我们可以修改`afl-gcc.c`用来打印出`cc_params`的内容

![](https://p1.ssl.qhimg.com/t010f5f1e7be5c8c0b9.png)

打印出内容后，可以看到`afl-gcc`按我们上文所预期的那样添加了部分参数。

    
    
    gcc -DHAVE_CONFIG_H -I. -g -O2 -MT ret2text.o -MD -MP -MF .deps/ret2text.Tpo -c -o ret2text.o ret2text.c -B /home/error404/AFL -g -O3 -funroll-loops -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1
    

此外，我们还发现在编译过程还调用了`afl-as`

![](https://p4.ssl.qhimg.com/t0191b37a0f8962add5.png)

这是因为`afl-gcc`使用了`-B`参数限定了编译器中汇编器的位置，并且通过我们的分析，`afl-gcc`并未进行代码的插桩，仅仅是针对`gcc`进行了参数的整理与优化，那么可以猜测`afl-as`是主要负担插桩工作的。

## 0x04 afl-as源码分析(第一部分)

与`afl-gcc`相同，`afl-as`也在程序入口点设计了一系列的代码检查操作。那么，其主逻辑如下所示：

    
    
    gettimeofday(&tv, &tz);
    rand_seed = tv.tv_sec ^ tv.tv_usec ^ getpid();
    srandom(rand_seed);
    
    edit_params(argc, argv);
    
    if (inst_ratio_str) {
        if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || inst_ratio > 100) 
          FATAL("Bad value of AFL_INST_RATIO (must be between 0 and 100)");
    }
    
    if (getenv(AS_LOOP_ENV_VAR))
        FATAL("Endless loop when calling 'as' (remove '.' from your PATH)");
    setenv(AS_LOOP_ENV_VAR, "1", 1);
    
    /* When compiling with ASAN, we don't have a particularly elegant way to skip
       ASAN-specific branches. But we can probabilistically compensate for 
       that... */
    
    if (getenv("AFL_USE_ASAN") || getenv("AFL_USE_MSAN")) {
        sanitizer = 1;
        inst_ratio /= 3;
    }
    
    if (!just_version) add_instrumentation();
    
    if (!(pid = fork())) {
        execvp(as_params[0], (char**)as_params);
        FATAL("Oops, failed to execute '%s' - check your PATH", as_params[0]);
    }
    
    if (pid < 0) PFATAL("fork() failed");
    
    if (waitpid(pid, &status, 0) <= 0) PFATAL("waitpid() failed");
    
    if (!getenv("AFL_KEEP_ASSEMBLY")) unlink(modified_file);
    
    exit(WEXITSTATUS(status));
    

###  生成随机数并设置种子

在整个主逻辑伊始，`afl-as`将生成一个与当前时间、`PID`相关的随机数种子并将其设置。

    
    
    gettimeofday(&tv, &tz);
    rand_seed = tv.tv_sec ^ tv.tv_usec ^ getpid();
    srandom(rand_seed);
    

随后进入`edit_params`函数逻辑

###  `edit_params`函数

  1. 将`TMPDIR`环境变量赋给`tmp_dir`，检查`tmp_dir`是否为`NULL`，若是，将`TEMP`环境变量赋给`tmp_dir`，检查`tmp_dir`是否为`NULL`，若是，将`TMP`环境变量赋给`tmp_dir`，检查`tmp_dir`是否为`NULL`，若是，将`tmp_dir`赋值为`/tmp`。
  2. 创建参数列表`as_params`，并检查`AFL_AS`环境变量的值是否设置，若已设置，则将其内部的路径作为`as_params[0]`；否则，将`as`关键字作为`as_params[0]`（即使用`PATH`环境变量中所定义的`as`汇编器）。
  3. 遍历传入的选项列表(从第二个参数开始，到倒数第二个参数为止)，检查当前参数，若参数为是`--64`，将`use_64bit`标志位置位；若参数为是`--32`，将`use_64bit`标志位清除。 
    * 这里避开第一个参数和最后一个参数是因为一般的调用格式为`afl-as <选项1> <选项2> <选项3> <选项4> <input-file>`。第一个参数一般是汇编器本身，已经在第二步处理；最后一个参数一般是输入文件，将在第五步处理；第三步第四步遍历处理的仅仅是选项。
  4. 随后，将当前参数加入`as_params`， **遍历下一个参数** 。
  5. 取最后一个参数，判断第一个字符是否为`-`。若是，继续判断后续字符是否为`-version`。若是，则将`just_version`标志位置位，随后将`--version`加入`as_params`，最后将`NULL`加入`as_params`， **函数结束** 。
  6. 若最后一个参数的第一个字符为`-`但后续字符不为`-version`且不为空，那么 **引发致命错误`Incorrect use (not called through afl-gcc?)`，中断`afl-gcc`**。
  7. 若最后一个参数的第一个字符为`-`但后续字符为空，那么将`<tmp_dir>/.afl-<PID>-<TIME>.s`(尖括号包围的内容用对应变量替换)加入`as_params`，最后将`NULL`加入`as_params`， **函数结束** 。
  8. 若最后一个参数的第一个字符不为`-`且最后一个参数不为`tmp_dir`的值、`/tmp`、`/var/tmp`三者之一，将`pass_thru`标志位置位。
  9. 将`<tmp_dir>/.afl-<PID>-<TIME>.s`(尖括号包围的内容用对应变量替换)加入`as_params`，最后将`NULL`加入`as_params`， **函数结束** 。

###  确认环境变量&相关设置

    
    
    if (inst_ratio_str) {
        if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || inst_ratio > 100) 
            FATAL("Bad value of AFL_INST_RATIO (must be between 0 and 100)");
    }
    
    if (getenv(AS_LOOP_ENV_VAR))
        FATAL("Endless loop when calling 'as' (remove '.' from your PATH)");
    
    setenv(AS_LOOP_ENV_VAR, "1", 1);
    
    /*  When compiling with ASAN, we don't have a particularly elegant way to skip
        ASAN-specific branches. But we can probabilistically compensate for
        that... */
    
    if (getenv("AFL_USE_ASAN") || getenv("AFL_USE_MSAN")) {
        sanitizer = 1;
        inst_ratio /= 3;
    }
    

  1. 首先检查`AFL_INST_RATIO`环境变量的值是否为空，若非空，将其以无符号数的形式写入`inst_ratio`中，并验证其是否小于等于`100`，若写入过程出错或其大于`100`， **引发致命错误`Bad value of AFL_INST_RATIO (must be between 0 and 100)`，中断`afl-gcc`**。
  2. 检查`__AFL_AS_LOOPCHECK`环境变量的值是否为空，若非空， **引发致命错误`Endless loop when calling 'as' (remove '.' from your PATH)`，中断`afl-gcc`**。
  3. 设置`__AFL_AS_LOOPCHECK`环境变量的值为`1`。
  4. 检查`AFL_USE_ASAN`或者`AFL_USE_MSAN`是否被设置，若二者之一被设置，则将`sanitizer`标志位置位，并将`inst_ratio`除三。 
    * `inst_ratio`代表插桩密度，密度越高插桩越多，对资源负担越大，当设置`AFL_USE_ASAN`或者`AFL_USE_MSAN`时，这个密度会被强制置为33左右。

接下来若`just_version`标志位未置位，进入`add_instrumentation`主逻辑

###  `add_instrumentation`函数(核心插桩函数)

####  检查文件权限

首先检查是否可以打开待插桩文件，以及确定可以将已插桩的文件写入目标位置

![](https://p5.ssl.qhimg.com/t01ca1cf2b700728231.png)

接下来进入插桩逻辑，打开待插桩文件 **循环** 读取一行(至多`8192`个字符)进`line`变量

#### 合法代码插桩——插入调用`__afl_maybe_log`的汇编码(Ⅰ)

若`pass_thru`、`skip_intel`、`skip_app`、`skip_csect`四个标志位均被清除，且`instr_ok`(这个标志位表征当前读入的行处于`.text`部分，将在后续设置，初始为清除状态)、`instrument_next`两个标志位均被设置，且
**当前行的第一个字符是`\t`且第二个字符是字母**，则向已插桩的文件写入`trampoline_fmt_64`/`trampoline_fmt_32`(取决于`use_64bit`标志位状态)

    
    
    static const u8* trampoline_fmt_32 =
      "\n"
      "/* --- AFL TRAMPOLINE (32-BIT) --- */\n"
      "\n"
      ".align 4\n"
      "\n"
      "leal -16(%%esp), %%esp\n"
      "movl %%edi,  0(%%esp)\n"
      "movl %%edx,  4(%%esp)\n"
      "movl %%ecx,  8(%%esp)\n"
      "movl %%eax, 12(%%esp)\n"
      "movl $0x%08x, %%ecx\n"
      "call __afl_maybe_log\n"
      "movl 12(%%esp), %%eax\n"
      "movl  8(%%esp), %%ecx\n"
      "movl  4(%%esp), %%edx\n"
      "movl  0(%%esp), %%edi\n"
      "leal 16(%%esp), %%esp\n"
      "\n"
      "/* --- END --- */\n"
      "\n";
    
    static const u8* trampoline_fmt_64 =
      "\n"
      "/* --- AFL TRAMPOLINE (64-BIT) --- */\n"
      "\n"
      ".align 4\n"
      "\n"
      "leaq -(128+24)(%%rsp), %%rsp\n"
      "movq %%rdx,  0(%%rsp)\n"
      "movq %%rcx,  8(%%rsp)\n"
      "movq %%rax, 16(%%rsp)\n"
      "movq $0x%08x, %%rcx\n"
      "call __afl_maybe_log\n"
      "movq 16(%%rsp), %%rax\n"
      "movq  8(%%rsp), %%rcx\n"
      "movq  0(%%rsp), %%rdx\n"
      "leaq (128+24)(%%rsp), %%rsp\n"
      "\n"
      "/* --- END --- */\n"
      "\n";
    

经过整理，最终插入的汇编码分别是：

    
    
    /* --- AFL TRAMPOLINE (32-BIT) --- */
    .align 4
    leal -16(%esp), %esp
    movl %edi,  0(%esp)
    movl %edx,  4(%esp)
    movl %ecx,  8(%esp)
    movl %eax, 12(%esp)
    movl $0x%08x, %ecx
    call __afl_maybe_log
    movl 12(%esp), %eax
    movl  8(%esp), %ecx
    movl  4(%esp), %edx
    movl  0(%esp), %edi
    leal 16(%esp), %esp
    /* --- END --- */
    
    /* --- AFL TRAMPOLINE (64-BIT) --- */
    .align 4
    leaq -(128+24)(%rsp), %rsp
    movq %rdx,  0(%rsp)
    movq %rcx,  8(%rsp)
    movq %rax, 16(%rsp)
    movq $0x%08x, %rcx
    call __afl_maybe_log
    movq 16(%rsp), %rax
    movq  8(%rsp), %rcx
    movq  0(%rsp), %rdx
    leaq (128+24)(%rsp), %rsp
    /* --- END --- */
    

⚠️：此处的`%08x`由`(random() % ((1 << 16)))`生成，在编译期确定。

插入结束后，将`instrument_next`标志位清除，桩代码计数器`ins_lines`加一。

最后将原始的汇编码（即`line`变量的内容），追加到插桩后文件中。

此时检查`pass_thru`标志位是否被置位，若已置位，则 **忽略以下流程，继续循环，读取下一行待插桩文件** 。

####  寻找合法有效的待插桩段

这里是真正的插桩函数的核心了，但是在这里我们真正感兴趣的事实上只有`.text`段，因此，执行以下操作：

若当前行的第一个字符是`\t`，第二个字符是`.`(即段标识符)执行以下判断处理逻辑：

  1. 若`clang_mode`标志位清除且`instr_ok`标志位置位且段标识符是`p2align`且段标识符后一位是数字且紧跟一个`\n`，则将`skip_next_label`标志位置位。 
    * `OpenBSD`将跳转表直接与代码内联，这很难被处理。 通常`.p2align`可以视为此种情况的标志，因此我们检测其用作信号。
  2. 若段标识符是`text\n`、`section\t.text`、`section\t__TEXT,__text`、`section __TEXT,__text`之一，则将`instr_ok`标志位置位， **忽略以下流程，继续循环，读取下一行待插桩文件** 。
  3. 若段标识符是`section\t`、`section`、`bss\n`、`data\n`之一，则将`instr_ok`标志位清除， **忽略以下流程，继续循环，读取下一行待插桩文件** 。

此时，有可能此行的的段标识符并不是以上所述的段。那么，就会有以下的几种特殊情况：

  1. 若存在`CSECT`指令，则需要想办法跳过，此类指令表示插入一段额外的可执行汇编代码块。特殊的，可以使用`.code32`/`.code64`指令来引导与当前程序位数不同的指令。此时`afl-as`将不能处理此情况，因此不进行插桩。检测处理逻辑如下： 
    1. 若当前行包含`.code32`，将`use_64bit`标志位的状态赋给`skip_csect`标志位。
    2. 若当前行包含`.code64`，将`use_64bit`标志位的状态 **取反** 赋给`skip_csect`标志位。
  2. 若存在`Intel`汇编指令，则需要想办法跳过，此类指令与当前的`AT&T`语法不符。此时`afl-as`将不能处理此情况，因此不进行插桩。检测处理逻辑如下： 
    1. 若当前行包含`.intel_syntax`，将`skip_intel`标志位置位。
    2. 若当前行包含`.att_syntax`，将`skip_intel`标志位清除。
  3. `afl-as`将不能处理内嵌汇编(C语言中由`__asm__`引导，汇编语言中由`#APP`与`#NO_APP`包围)语句，因此不进行插桩。检测处理逻辑如下： 
    1. 若当前行的第一个字符或第二个字符是`#`，且当前行包含`#APP`，将`skip_app`标志位置位。
    2. 若当前行的第一个字符或第二个字符是`#`，且当前行包含`#NO_APP`，将`skip_app`标志位清除。

若`skip_intel`、`skip_app`、`skip_csect`中的任何一个标志位置位或者`instr_ok`标志位被清除或者当前行第一个字母是`#`或`<空格>`（`#
BB#0`或`#
BB#0`在`Clang`中表示注释），表示当前行以及其下面的行不是一个有效的待插桩代码行，应当予以跳过，直到遇到结束标识使得对应标志位清除或置位。那么，`afl-as`将执行， **忽略以下流程，继续循环，读取下一行待插桩文件** 的操作。

#### 分支跳转代码插桩——插入调用`__afl_maybe_log`的汇编码

我们接下来检测条件跳转指令(例如：`jnz`、`jz`之类的语句)，`afl-as`为了标记此处将会有另一条分支并期望在后续的测试过程中覆盖另一条分支，将在跳转指令之后插入`trampoline_fmt_64`/`trampoline_fmt_32`(取决于`use_64bit`标志位状态)，关于这两段代码上文已分析过，此处不再赘述。

注意，`JMP`表示无条件跳转，因此其另一条分支将永远不会被运行到，那么将不会影响代码覆盖率，因此不在`JMP`指令后插桩。

那么，此处插桩逻辑为：若此行代码的第一个字符为`\t`，则再次检测第二个字符是不是`j`，若是，再检查第三个字符是不是`m`，若不是则进行插桩逻辑，插桩结束后将桩代码计数器`ins_lines`加一。无论第二个第三个字符为什么，只要第一个字符为`\t`，则
**忽略以下流程，继续循环，读取下一行待插桩文件**

#### 对标签段进行处理(`Label`)

若此行代码中有`:`字符但是第一个字符不是`.`字符，则将`instrument_next`置位(此标志位表示下一条语句是有效语句，将在`代码插桩——插入调用__afl_maybe_log的汇编码(Ⅰ)`过程中使用)，随后
**继续循环，读取下一行待插桩文件** 。

若此行代码中有`:`字符且第一个字符是`.`字符且满足下列情况之一：

  * 第三个字符是数字且`inst_ratio`大于`random(100)`
  * `clang_mode`置位且此行的前四个字符是`.LBB`且`inst_ratio`大于`random(100)`

则执行对`skip_next_label`的检查，若此标志位清除，则将`instrument_next`置位，随后 **继续循环，读取下一行待插桩文件**
。

若此行代码中有`:`字符且第一个字符是`.`字符但不满足上述情况之一， **继续循环，读取下一行待插桩文件** 。

至此，循环正式结束。

#### 末尾代码插桩——插入`AFL`主逻辑汇编码

最后，若桩代码计数器`ins_lines`不为0，那么将`main_payload_64`/`main_payload_32`(取决于`use_64bit`标志位状态)插入整个汇编文件末尾。

限于篇幅，此处的代码将在下一篇文章中予以说明。

## 0x05 后记

虽然网上有很多关于`AFL`源码的分析，但是绝大多数文章都是抽取了部分代码进行分析的，本文则逐行对源码进行了分析，下一篇文章将针对`afl-as`源码做下一步分析并给出相关实例。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ERROR404** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/240792](/post/id/240792)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [Fuzz](/tag/Fuzz)
  * [AFL](/tag/AFL)

 **+1** __4赞

 __收藏

![](https://p5.ssl.qhimg.com/t01fc6ae8fa56997fe6.jpg) ERROR404

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

