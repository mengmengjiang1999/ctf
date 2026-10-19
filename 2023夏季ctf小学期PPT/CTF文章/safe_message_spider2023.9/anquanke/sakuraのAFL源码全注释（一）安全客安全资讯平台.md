# sakuraのAFL源码全注释（一）

阅读量 **364487**

|评论 **6**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-10 16:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)

## afl-gcc小叙

###  核心函数

####  find_as

这个函数用来寻找`afl-as`的位置。

  * 它首先检查是否存在AFL_PATH这个环境变量，如果存在就赋值给afl_path，然后检查`afl_path/as`这个文件是否可以访问，如果可以访问，就将afl_path设置为as_path。
  * 如果不存在AFL_PATH这个环境变量，则检查argv0，例如（”/Users/sakura/gitsource/AFL/cmake-build-debug/afl-gcc”）中是否存在’/‘，如果有就找到最后一个’/‘所在的位置，并取其前面的字符串作为dir，然后检查`dir/afl-as`这个文件是否可以访问，如果可以访问，就将dir设置为as_path
  * 如果上述两种方式都失败，则抛出异常。

####  edit_params

这个函数主要是将argv拷贝到`u8 **cc_params`中，并做必要的编辑。

  * 它首先通过ck_alloc来为cc_params分配内存，分配的长度为`(argc+128)*8`，相当大的内存了。
  * 然后检查argv[0]里有没有’/‘，如果没有就赋值’argv[0]’到name，如果有就找到最后一个’/‘所在的位置，然后跳过这个’/‘，将后面的字符串赋值给name。
  * 将name和`afl-clang`比较 
    * 如果相同，则设置clang_mode为1，然后设置环境变量CLANG_ENV_VAR为1。 
      * 然后将name和`afl-clang++`比较 
        * 如果相同，则获取环境变量`AFL_CXX`的值，如果该值存在，则将cc_params[0]设置为该值，如果不存在，就设置为clang++
        * 如果不相同，则获取环境变量`AFL_CC`的值，如果该值存在，则将cc_params[0]设置为该值，如果不存在，就设置为clang
    * 如果不相同，则将name和`afl-g++`比较 
      * 如果相同，则获取环境变量`AFL_CXX`的值，如果该值存在，则将cc_params[0]设置为该值，如果不存在，就设置为g++
      * 如果不相同，则获取环境变量`AFL_CC`的值，如果该值存在，则将cc_params[0]设置为该值，如果不存在，就设置为gcc
  * 然后遍历从argv[1]开始的argv参数 
    * 跳过`-B/integrated-as/-pipe`
    * 如果存在`-fsanitize=address`或者`-fsanitize=memory`，就设置asan_set为1;
    * 如果存在`FORTIFY_SOURCE`，则设置fortify_set为1
    * `cc_params[cc_par_cnt++] = cur`;
  * 然后开始设置其他的cc_params参数 
    * 取之前计算出来的`as_path`，然后设置`-B as_path`
    * 如果是clang_mode,则设置`-no-integrated-as`
    * 如果存在AFL_HARDEN环境变量，则设置`-fstack-protector-all`
    * sanitizer 
      * 如果asan_set在上面被设置为1，则使`AFL_USE_ASAN`环境变量为1
      * 如果存在AFL_USE_ASAN环境变量，则设置`-fsanitize=address`
      * 如果存在AFL_USE_MSAN环境变量，则设置`-fsanitize=memory`，但不能同时还指定`AFL_HARDEN`或者`AFL_USE_ASAN`，因为这样运行时速度过慢。
    * 如果不存在AFL_DONT_OPTIMIZE环境变量，则设置`-g -O3 -funroll-loops -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1`
    * 如果存在AFL_NO_BUILTIN环境变量，则设置`-fno-builtin-strcmp`等
  * 最后`cc_params[cc_par_cnt] = NULL;`终止对cc_params的编辑

####  main函数

实际上看到这里，我们就知道afl-gcc就是找到as所在的位置，将其加入搜索路径，然后设置必要的gcc参数和一些宏，然后调用gcc进行实际的编译，仅仅只是一层wrapper

    
    
    /* Main entry point */
    
    int main(int argc, char **argv) {
    
        if (isatty(2) && !getenv("AFL_QUIET")) {
    
            SAYF(cCYA "afl-cc " cBRI VERSION cRST " by <lcamtuf@google.com>\n");
    
        } else be_quiet = 1;
    
        if (argc < 2) {
            ...
            exit(1);
        }
        //查找fake GNU assembler
        find_as(argv[0]);
        // 设置CC的参数
        edit_params(argc, argv);
        // 调用execvp来执行CC
    
        // 这里我们在CC之前打印一下参数看看。
        for (int i = 0; i < sizeof(cc_params); i++) {
          printf("\targ%d: %s\n",i,cc_params[i]);
        }
    
        execvp(cc_params[0], (char **) cc_params);
    
        FATAL("Oops, failed to execute '%s' - check your PATH", cc_params[0]);
    
        return 0;
    
    }
    

输出如下

    
    
    sakura@sakuradeMacBook-Pro:~/gitsource/AFL/cmake-build-debug$ ./afl-gcc ../test-instr.c -o test
    afl-cc 2.57b by <lcamtuf@google.com>
            arg0: gcc
            arg1: ../test-instr.c
            arg2: -o
            arg3: test
            arg4: -B
            arg5: .
            arg6: -g
            arg7: -O3
    

## afl-as小叙

###  核心函数

####  edit_params

检查并修改参数以传递给`as`。请注意，文件名始终是GCC传递的最后一个参数，因此我们利用这个特性使代码保持简单。  
 **主要是设置变量as_params的值，以及use_64bit/modified_file的值。**

  * 首先为as_params分配空间，大小为`(argc+32)*8`
  * `u8 *tmp_dir`
    * 依次检查是否存在TMPDIR/TEMP/TMP环境变量，如果存在就设置，如果都不存在就设置tmp_dir为”/tmp”
  * `u8 *afl_as`
    * 读取AFL_AS环境变量，如果存在就设置为afl_as的值
    * 因为apple的一些原因，所以如果我们定义了`__APPLE__`宏，且当前是在clang_mode且没有设置AFL_AS环境变量，就设置use_clang_as为1，并设置afl_as为AFL_CC/AFL_CXX/clang中的一种。
  * 如果afl_as不为空，就设置`as_params[0]`为`afl_as`，否则设置为`as`
  * 设置`as_params[argc]`为0,as_par_cnt初始值为1。
  * 然后遍历从argv[1]开始,到`argv[argc-1]`(也就是最后一个参数)之前的argv参数 
    * 如果存在`--64`，设置use_64bit为1，如果存在`--32`，设置use_64bit为0;如果是apple,则如果存在`-arch x86_64`,设置use_64bit为1,并跳过`-q`和`-Q`选项
    * `as_params[as_par_cnt++] = argv[i]`;设置as_params的值为argv对应的参数值
  * 然后开始设置其他的as_params参数 
    * 如果use_clang_as为1，则设置`-c -x assembler`选项
    * 读取`argv[argc - 1]`的值,赋给input_file的值,也就是传递的最后一个参数的值作为input_file
    * 比较input_file和tmp_dir/`/var/tmp/`/`/tmp/`的前strlen(tmp_dir)/9/5个字节是否相同，如果不相同，就设置pass_thru为1
    * 设置modified_file的值为`alloc_printf("%s/.afl-%u-%u.s", tmp_dir, getpid(),(u32) time(NULL));`,简单的说就是`tmp_dir/.afl-pid-time.s`这样的字符串。
    * 设置`as_params[as_par_cnt++] = modified_file`
    * `as_params[as_par_cnt] = NULL;`

####  add_instrumentation

处理输入文件，生成modified_file，将instrumentation插入所有适当的位置。

  * 如果input_file不为空，则尝试打开这个文件，如果打开失败就抛出异常，如果为空，则读取标准输入，最终获取FILE* 指针inf
  * 然后打开modified_file对应的临时文件，并获取其句柄outfd，再根据句柄通过fdopen函数拿到FILE*指针outf
  * 通过fgets从inf中逐行读取内容保存到line数组里，每行最多读取的字节数是MAX_LINE(8192),这个值包括’\0’,所以实际读取的有内容的字节数是MAX_LINE-1个字节。从line数组里将读取的内容写入到outf对应的文件里。

**接下来是真正有趣的部分，首先我们要确定的是，我们只在.text部分进行插桩，但因为这部分涉及到多平台以及优化后的汇编文件格式，这里我只会描述最核心的逻辑**

核心逻辑如下,我抽取了最重要的代码出来。

    
    
                 ^func:      - function entry point (always instrumented)
                 ^.L0:       - GCC branch label
                 ^.LBB0_0:   - clang branch label (but only in clang mode)
                 ^\tjnz foo  - conditional branches
    
               ...but not:
    
                 ^# BB#0:    - clang comments
                 ^ # BB#0:   - ditto
                 ^.Ltmp0:    - clang non-branch labels
                 ^.LC0       - GCC non-branch labels
                 ^.LBB0_0:   - ditto (when in GCC mode)
                 ^\tjmp foo  - non-conditional jumps
    
    
    
    while (fgets(line, MAX_LINE, inf)) {
        if(instr_ok && instrument_next && line[0] == '\t' && isalpha(line[1])){
            fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32,
                        R(MAP_SIZE));
    
            instrument_next = 0;
            ins_lines++;
        }
        ...
        if (line[0] == '\t' && line[1] == '.') {
            if (!strncmp(line + 2, "text\n", 5) ||
                !strncmp(line + 2, "section\t.text", 13) ||
                !strncmp(line + 2, "section\t__TEXT,__text", 21) ||
                !strncmp(line + 2, "section __TEXT,__text", 21)) {
                instr_ok = 1;
                continue;
            }
    
            if (!strncmp(line + 2, "section\t", 8) ||
                !strncmp(line + 2, "section ", 8) ||
                !strncmp(line + 2, "bss\n", 4) ||
                !strncmp(line + 2, "data\n", 5)) {
                instr_ok = 0;
                continue;
            }
        }
        ...
        if (line[0] == '\t') {
                if (line[1] == 'j' && line[2] != 'm' && R(100) < inst_ratio) {
                    fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32,
                            R(MAP_SIZE));
    
                    ins_lines++;
                }
                continue;
    
            }
        ...
        if (strstr(line, ":")) {
            if (line[0] == '.') {
                if ((isdigit(line[2]) || (clang_mode && !strncmp(line + 1, "LBB", 3)))
                            && R(100) < inst_ratio) {
                                instrument_next = 1;
                            }
            }
            else {
                /* Function label (always instrumented, deferred mode). */
                instrument_next = 1;
            }
        }
    }
    

  * 检查`instr_ok && instrument_next && line[0] == '\t' && isalpha(line[1])`即判断instrument_next和instr_ok是否都为1，以及line是否以`\t`开始，且`line[1]`是否是字母 
    * 如果都满足，则设置`instrument_next = 0`,并向outf中写入`trampoline_fmt`，并将插桩计数器`ins_lines`加一。
    * 这其实是因为我们想要插入instrumentation trampoline到所有的标签，宏，注释之后。
  * 首先要设置instr_ok的值，这个值其实是一个flag，只有这个值被设置为1，才代表我们在`.text`部分，否则就不在。于是如果instr_ok为1，就会在分支处执行插桩逻辑，否则就不插桩。 
    * 如果line的值为`\t.[text\n|section\t.text|section\t__TEXT,__text|section __TEXT,__text]...`其中之一，则设置instr_ok为1，然后跳转到while循环首部，去读取下一行的数据到line数组里。
    * 如果不是上面的几种情况，且line的值为`\t.[section\t|section |bss\n|data\n]...`，则设置instr_ok为0，并跳转到while循环首部，去读取下一行的数据到line数组里。
  * 插桩`^\tjnz foo`条件跳转指令 
    * 如果line的值为`\tj[!m]...`,且`R(100) < inst_ratio`，R(100)会返回一个100以内的随机数，inst_ratio是我们之前设置的插桩密度，默认为100，如果设置了asan之类的就会默认设置成30左右。
    * `fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32, R(MAP_SIZE));`根据use_64bit来判断向outfd里写入trampoline_fmt_64还是trampoline_fmt_32。 
      * `define R(x) (random() % (x))`，可以看到R(x)是创建的随机数除以x取余，所以可能产生碰撞
      * 这里的R(x)实际上是用来区分每个桩的，也就是是一个标识。后文会再说明。
    * 将插桩计数器`ins_lines`加一。
  * 首先检查该行中是否存在`:`，然后检查是否以`.开始`
    * 如果以`.`开始，则代表想要插桩`^.L0:`或者`^.LBB0_0:`这样的branch label，即style jump destination 
      * 然后检查`line[2]`是否为数字 或者 如果是在clang_mode下，比较从line[1]开始的三个字节是否为LBB. 前述所得结果和`R(100) < inst_ratio)`相与。 
        * 如果结果为真，则设置`instrument_next = 1`
    * 否则代表这是一个function，插桩`^func:`function entry point 
      * 直接设置`instrument_next = 1`
  * 如果插桩计数器ins_lines不为0，就在完全拷贝input_file之后，依据架构，像outf中写入main_payload_64或者main_payload_32，然后关闭这两个文件
  * **至此我们可以看出afl的插桩相当简单粗暴，就是通过汇编的前导命令来判断这是否是一个分支或者函数，然后插入instrumentation trampoline。**
  * **关于instrumentation trampoline，后文叙述**

####  main函数

最后我们回来看一下main函数

  * 读取环境变量AFL_INST_RATIO的值，设置为inst_ratio_str
  * 设置srandom的随机种子为`rand_seed = tv.tv_sec ^ tv.tv_usec ^ getpid();`
  * 设置环境变量AS_LOOP_ENV_VAR的值为1
  * 读取环境变量AFL_USE_ASAN和AFL_USE_MSAN的值，如果其中有一个为1，则设置sanitizer为1，且将inst_ratio除3。 
    * 这是因为AFL无法在插桩的时候识别出ASAN specific branches，所以会插入很多无意义的桩，为了降低这种概率，粗暴的将整个插桩的概率都除以3
  * edit_params(argc, argv)
  * add_instrumentation()
  * fork出一个子进程，让子进程来执行`execvp(as_params[0], (char **) as_params);`
    * 这其实是因为我们的execvp执行的时候，会用`as_params[0]`来完全替换掉当前进程空间中的程序，如果不通过子进程来执行实际的as，那么后续就无法在执行完实际的as之后，还能unlink掉modified_file
    * [exec系列函数](https://www.cnblogs.com/mickole/p/3187409.html)
    * [fork出的子进程和父进程](https://blog.csdn.net/THEONE10211024/article/details/13774669)
  * `waitpid(pid, &status, 0)`等待子进程结束
  * 读取环境变量AFL_KEEP_ASSEMBLY的值，如果没有设置这个环境变量，就unlink掉modified_file。

稍微打印一下参数

    
    
    for (int i = 0; i < sizeof(as_params); i++) {
        printf("as_params[%d]:%s\n", i, as_params[i]);
    }
        ...
    [+] Instrumented 5 locations (64-bit, non-hardened mode, ratio 100%).
    as_params[0]:as
    as_params[1]:/Users/sakura/gitsource/AFL/cmake-build-debug/tmp/afl-8427-1595314986.s
    

## afl-fast-clang中叙

因为AFL对于上述通过`afl-gcc`来插桩这种做法已经属于不建议，并提供了更好的工具afl-clang-fast，通过llvm pass来插桩。

###  clang wrapper

`afl-clang-fast.c`这个文件其实是clang的一层wrapper，和之前的`afl-gcc`一样，只是定义了一些宏，和传递了一些参数给真正的clang。  
我们还是依次来看一下核心函数。

####  find_obj

  * 获取环境变量`AFL_PATH`的值，如果存在，就去读取`AFL_PATH/afl-llvm-rt.o`是否可以访问，如果可以就设置这个目录为`obj_path`，然后直接返回
  * 如果没有设置这个环境变量，就检查arg0中是否存在`/`，例如我们可能是通过`/home/sakura/AFL/afl-clang-fast`去调用afl-clang-fast的，所以它此时就认为最后一个`/`之前的`/home/sakura/AFL`是AFL的根目录，然后读取其下的`afl-llvm-rt.o`文件，看是否能够访问，如果可以就设置这个目录为`obj_path`，然后直接返回。
  * 最后如果上面两种都找不到，因为默认的AFL的MakeFile在编译的时候，会定义一个名为`AFL_PATH`的宏，其指向`/usr/local/lib/afl`,会到这里找是否存在`afl-llvm-rt.o`，如果存在设置`obj_path`并直接返回。
  * 如果上述三种方式都找不到，那么就会抛出异常`Unable to find 'afl-llvm-rt.o' or 'afl-llvm-pass.so'. Please set AFL_PATH`

####  edit_params

  * 首先根据我们执行的是`afl-clang-fast`还是`afl-clang-fast++`来决定`cc_params[0]`的值是clang++还是clang。 
    * 如果执行的是`afl-clang-fast++`，读取环境变量`AFL_CXX`，如果存在，就将其值设置为`cc_params[0]`，如果不存在，就直接设置成`clang++`
    * 如果执行的是`afl-clang-fast`，读取环境变量`AFL_CC`，如果存在，就将其值设置为`cc_params[0]`，如果不存在，就直接设置成`clang`
  * 默认情况下，我们通过`afl-llvm-pass.so`来注入instrumentation，但是现在也支持`trace-pc-guard`模式，可以参考[llvm的文档](http://clang.llvm.org/docs/SanitizerCoverage.html#tracing-pcs-with-guards)
  * 然后如果定义了`USE_TRACE_PC`宏，就将`-fsanitize-coverage=trace-pc-guard -mllvm -sanitizer-coverage-block-threshold=0`添加到参数里
  * 如果没有定义，就依次将`-Xclang -load -Xclang obj_path/afl-llvm-pass.so -Qunused-arguments`
  * 依次读取我们传给`afl-clang-fast`的参数，并添加到cc_params里，不过这里会做一些检查和设置。 
    * 如果传入参数里有`-m32`或者`armv7a-linux-androideabi`，就设置`bit_mode`为32
    * 如果传入参数里有`-m64`，就设置`bit_mode`为64
    * 如果传入参数里有`-x`，就设置`x_set`为1
    * 如果传入参数里有`-fsanitize=address`或者`-fsanitize=memory`，就设置asan_set为1
    * 如果传入参数里有`-Wl,-z,defs`或者`-Wl,--no-undefined`，就直接pass掉，不传给clang。
  * 读取环境变量`AFL_HARDEN`，如果存在，就在cc_params里添加`-fstack-protector-all`
  * 如果参数里没有`-fsanitize=address/memory`，即asan_set是0，就读取环境变量`AFL_USE_ASAN`，如果存在就添加`-fsanitize=address`到cc_params里，环境变量`AFL_USE_MSAN`同理
  * 如果定义了`USE_TRACE_PC`宏，就检查是否存在环境变量`AFL_INST_RATIO`，如果存在就抛出异常`AFL_INST_RATIO not available at compile time with 'trace-pc'.`
  * 读取环境变量`AFL_DONT_OPTIMIZE`，如果 **不存在** 就添加`-g -O3 -funroll-loops`到参数里
  * 读取环境变量`AFL_NO_BUILTIN`，如果存在就添加`-fno-builtin-strcmp`等。
  * 添加参数`-D__AFL_HAVE_MANUAL_CONTROL=1 -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1`，定义一些宏
  * 这里定义了如下两个宏`__AFL_LOOP`,`__AFL_INIT()`,宏展开是类似这样的，为简化我去掉了和编译器优化相关的东西。

    
    
    #define __AFL_LOOP() \
      do { \
          static char *_B; \
          _B = (char*)"##SIG_AFL_PERSISTENT##"; \
          __afl_persistent_loop(); \
      }while (0)
    
    #define __AFL_INIT() \
      do { \
          static char *_A;  \
          _A = (char*)"##SIG_AFL_DEFER_FORKSRV##"; \
          __afl_manual_init(); \
      } while (0)
    

  * 如果x_set为1，则添加参数`-x none`
  * 根据`bit_mode`的值选择`afl-llvm-rt`
    * 如果为0，即没有`-m32`和`-m64`选项，就向参数里添加`obj_path/afl-llvm-rt.o`
    * 如果为32，添加`obj_path/afl-llvm-rt-32.o`
    * 如果为64，添加`obj_path/afl-llvm-rt-64.o`

####  main

  * 寻找obj_path路径
  * 编辑参数cc_params
  * 替换进程空间，执行要调用的clang和为其传递参数 
    * `execvp(cc_params[0], (char**)cc_params);`

###  afl-llvm-pass

关于llvm不懂的可以看CSCD70，顺便可以学一下优化，这里放一下我之前抽空做的[笔记](https://github.com/eternalsakura/sakura_llvm_opt),
以及[这篇文章](https://blog.csdn.net/qq_23599965/article/details/88538590)可以列为查询和参考.  
afl-llvm-pass里只有一个Transform pass
AFLCoverage，其继承自ModulePass，所以我们主要分析一下它的`runOnModule`函数，这里简单的介绍一下llvm里的一些层次关系，粗略理解就是Module相当于你的程序，里面包含所有Function和全局变量，而Function里包含所有BasicBlock和函数参数，BasicBlock里包含所有Instruction,Instruction包含Opcode和Operands。

![](https://sakura-1252236262.cos.ap-beijing.myqcloud.com/2020-08-03-083346.png)

####  注册pass

    
    
    static void registerAFLPass(const PassManagerBuilder &,
                                legacy::PassManagerBase &PM) {
    
      PM.add(new AFLCoverage());
    
    }
    
    static RegisterStandardPasses RegisterAFLPass(
        PassManagerBuilder::EP_ModuleOptimizerEarly, registerAFLPass);
    
    static RegisterStandardPasses RegisterAFLPass0(
        PassManagerBuilder::EP_EnabledOnOptLevel0, registerAFLPass);
    

这些都是向PassManager来注册新的pass，每个pass彼此独立，通过PM统一注册和调度，更加模块化。  
具体的可以参考定义，我摘取了必要的代码和注释，请仔细阅读。  
简单的理解就是当我创建了一个类RegisterStandardPasses之后，就会调用它的构造函数，然后调用`PassManagerBuilder::addGlobalExtension`，这是一个静态函数，这个函数会创建一个tuple保存
**Ty和Fn还有一个id** ，并将其添加到一个静态全局vector里，以供PassManagerBuilder在需要的时候，将其添加到PM里。  
而这个添加的时机就是`ExtensionPointTy`来指定的。

    
    
    /// Registers a function for adding a standard set of passes.  This should be
    /// used by optimizer plugins to allow all front ends to transparently use
    /// them.  Create a static instance of this class in your plugin, providing a
    /// private function that the PassManagerBuilder can use to add your passes.
    class RegisterStandardPasses {
      PassManagerBuilder::GlobalExtensionID ExtensionID;
    
    public:
      RegisterStandardPasses(PassManagerBuilder::ExtensionPointTy Ty,
                             PassManagerBuilder::ExtensionFn Fn) {
        ExtensionID = PassManagerBuilder::addGlobalExtension(Ty, std::move(Fn));
      }
    
      ~RegisterStandardPasses() {
      ...
      }
    };
    
    ...
    /// PassManagerBuilder - This class is used to set up a standard optimization
    /// sequence for languages like C and C++, allowing some APIs to customize the
    /// pass sequence in various ways. A simple example of using it would be:
    ///
    ///  PassManagerBuilder Builder;
    ///  Builder.OptLevel = 2;
    ///  Builder.populateFunctionPassManager(FPM);
    ///  Builder.populateModulePassManager(MPM);
    ///
    /// In addition to setting up the basic passes, PassManagerBuilder allows
    /// frontends to vend a plugin API, where plugins are allowed to add extensions
    /// to the default pass manager.  They do this by specifying where in the pass
    /// pipeline they want to be added, along with a callback function that adds
    /// the pass(es).  For example, a plugin that wanted to add a loop optimization
    /// could do something like this:
    ///
    /// static void addMyLoopPass(const PMBuilder &Builder, PassManagerBase &PM) {
    ///   if (Builder.getOptLevel() > 2 && Builder.getOptSizeLevel() == 0)
    ///     PM.add(createMyAwesomePass());
    /// }
    ///   ...
    ///   Builder.addExtension(PassManagerBuilder::EP_LoopOptimizerEnd,
    ///                        addMyLoopPass);
    ///   ...
    class PassManagerBuilder {
    public:
      /// Extensions are passed to the builder itself (so they can see how it is
      /// configured) as well as the pass manager to add stuff to.
      typedef std::function<void(const PassManagerBuilder &Builder,
                                 legacy::PassManagerBase &PM)>
          ExtensionFn;
      typedef int GlobalExtensionID;
    
      enum ExtensionPointTy {
        /// EP_ModuleOptimizerEarly - This extension point allows adding passes
        /// just before the main module-level optimization passes.
        EP_ModuleOptimizerEarly,
        ...
        /// EP_EnabledOnOptLevel0 - This extension point allows adding passes that
        /// should not be disabled by O0 optimization level. The passes will be
        /// inserted after the inlining pass.
        EP_EnabledOnOptLevel0,
        ...
        }
        ...
        ...
      /// Adds an extension that will be used by all PassManagerBuilder instances.
      /// This is intended to be used by plugins, to register a set of
      /// optimisations to run automatically.
      ///
      /// \returns A global extension identifier that can be used to remove the
      /// extension.
      static GlobalExtensionID addGlobalExtension(ExtensionPointTy Ty,
                                                  ExtensionFn Fn);
        ...
      }
    ...
    ...
    /// PassManagerBase - An abstract interface to allow code to add passes to
    /// a pass manager without having to hard-code what kind of pass manager
    /// it is.
    class PassManagerBase {
    public:
      virtual ~PassManagerBase();
    
      /// Add a pass to the queue of passes to run.  This passes ownership of
      /// the Pass to the PassManager.  When the PassManager is destroyed, the pass
      /// will be destroyed as well, so there is no need to delete the pass.  This
      /// may even destroy the pass right away if it is found to be redundant. This
      /// implies that all passes MUST be allocated with 'new'.
      virtual void add(Pass *P) = 0;
    };
    

####  runOnModule

  * 通过getContext来获取LLVMContext，其保存了整个程序里分配的类型和常量信息。
  * 通过这个Context来获取type实例Int8Ty和Int32Ty 
    * Type是所有type类的一个超类。 **每个Value都有一个Type** ，所以这经常被用于寻找指定类型的Value。Type不能直接实例化，只能通过其子类实例化。某些基本类型(VoidType、LabelType、FloatType和DoubleType)有隐藏的子类。之所以隐藏它们，是因为除了Type类提供的功能之外，它们没有提供任何有用的功能，除了将它们与Type的其他子类区分开来之外。所有其他类型都是DerivedType的子类。Types可以被命名，但这不是必需的。一个给定Type在任何时候都只存在一个实例。这允许使用Type实例的地址相等来执行type相等。也就是说，给定两个Type*值，如果指针相同，则types相同。
  * 读取环境变量`AFL_INST_RATIO`给变量inst_ratio，其值默认为100，这个值代表一个插桩概率，本来应该每个分支都必定插桩，而这是一个随机的概率决定是否要在这个分支插桩。
  * 获取全局变量中指向共享内存的指针，以及上一个基础块的编号

    
    
    GlobalVariable *AFLMapPtr =
            new GlobalVariable(M, PointerType::get(Int8Ty, 0), false,
                                GlobalValue::ExternalLinkage, 0, "__afl_area_ptr");
    
    GlobalVariable *AFLPrevLoc = new GlobalVariable(
            M, Int32Ty, false, GlobalValue::ExternalLinkage, 0, "__afl_prev_loc",
            0, GlobalVariable::GeneralDynamicTLSModel, 0, false);
    

  * 遍历每个基本块，找到此基本块中适合插入instrument的位置，后续通过初始化IRBuilder的一个实例进行插入。 
    
        BasicBlock::iterator IP = BB.getFirstInsertionPt();
    IRBuilder<> IRB(&(*IP));
    

  * 随机创建一个当前基本块的编号，并通过插入load指令来获取前一个基本块的编号。 
    
        unsigned int cur_loc = AFL_R(MAP_SIZE);
    ConstantInt *CurLoc = ConstantInt::get(Int32Ty, cur_loc);
    LoadInst *PrevLoc = IRB.CreateLoad(AFLPrevLoc);
    PrevLoc->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    Value *PrevLocCasted = IRB.CreateZExt(PrevLoc, IRB.getInt32Ty());
    

  * 通过插入load指令来获取共享内存的地址，并通过CreateGEP函数来获取共享内存里指定index的地址，这个index通过cur_loc和prev_loc取xor计算得到。 
    
        LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
    MapPtr->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    Value *MapPtrIdx =
          IRB.CreateGEP(MapPtr, IRB.CreateXor(PrevLocCasted, CurLoc));
    

  * 通过插入load指令来读取对应index地址的值，并通过插入add指令来将其加一，然后通过创建store指令将新值写入，更新共享内存。 
    
        LoadInst *Counter = IRB.CreateLoad(MapPtrIdx);
    Counter->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    Value *Incr = IRB.CreateAdd(Counter, ConstantInt::get(Int8Ty, 1));
    IRB.CreateStore(Incr, MapPtrIdx)
          ->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    

  * 将当前cur_loc的值右移一位，然后通过插入store指令，更新`__afl_prev_loc`的值。 
    
        StoreInst *Store = IRB.CreateStore(ConstantInt::get(Int32Ty, cur_loc >> 1), AFLPrevLoc);
    Store->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    

  * 总结  
总的来说就是通过遍历每个基本块，向其中插入实现了如下伪代码功能的instruction ir来进行插桩。

    
        cur_location = <COMPILE_TIME_RANDOM>; 
    shared_mem[cur_location ^ prev_location]++; 
    prev_location = cur_location >> 1;
    

看一个例子

  * 源程序

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(int argc, char** argv) {
    
      char buf[8];
    
      if (read(0, buf, 8) < 1) {
        printf("Hum?\n");
        exit(1);
      }
    
      if (buf[0] == '0')
        printf("Looks like a zero to me!\n");
      else
        printf("A non-zero value? How quaint!\n");
    
      exit(0);
    
    }
    

  * 插桩前的ir

    
    
    ; ModuleID = 'nopt_test-instr.ll'
    source_filename = "test-instr.c"
    target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
    target triple = "x86_64-apple-macosx10.15.0"
    
    @.str = private unnamed_addr constant [6 x i8] c"Hum?\0A\00", align 1
    @.str.1 = private unnamed_addr constant [26 x i8] c"Looks like a zero to me!\0A\00", align 1
    @.str.2 = private unnamed_addr constant [31 x i8] c"A non-zero value? How quaint!\0A\00", align 1
    
    ; Function Attrs: noinline nounwind ssp uwtable
    define i32 @main(i32 %0, i8** %1) #0 {
      %3 = alloca [8 x i8], align 1
      %4 = getelementptr inbounds [8 x i8], [8 x i8]* %3, i64 0, i64 0
      %5 = call i64 @"\01_read"(i32 0, i8* %4, i64 8)
      %6 = icmp slt i64 %5, 1
      br i1 %6, label %7, label %9
    
    7:                                                ; preds = %2
      %8 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str, i64 0, i64 0))
      call void @exit(i32 1) #3
      unreachable
    
    9:                                                ; preds = %2
      %10 = getelementptr inbounds [8 x i8], [8 x i8]* %3, i64 0, i64 0
      %11 = load i8, i8* %10, align 1
      %12 = sext i8 %11 to i32
      %13 = icmp eq i32 %12, 48
      br i1 %13, label %14, label %16
    
    14:                                               ; preds = %9
      %15 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([26 x i8], [26 x i8]* @.str.1, i64 0, i64 0))
      br label %18
    
    16:                                               ; preds = %9
      %17 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([31 x i8], [31 x i8]* @.str.2, i64 0, i64 0))
      br label %18
    
    18:                                               ; preds = %16, %14
      call void @exit(i32 0) #3
      unreachable
    }
    
    declare i64 @"\01_read"(i32, i8*, i64) #1
    
    declare i32 @printf(i8*, ...) #1
    
    ; Function Attrs: noreturn
    declare void @exit(i32) #2
    
    attributes #0 = { noinline nounwind ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #2 = { noreturn "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #3 = { noreturn }
    
    !llvm.module.flags = !{!0, !1}
    !llvm.ident = !{!2}
    
    !0 = !{i32 1, !"wchar_size", i32 4}
    !1 = !{i32 7, !"PIC Level", i32 2}
    !2 = !{!"clang version 10.0.0 "}
    

  * 插桩后的ir

    
    
    ; ModuleID = 'm2r_nopt_test-instr.ll'
    source_filename = "test-instr.c"
    target datalayout = "e-m:o-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
    target triple = "x86_64-apple-macosx10.15.0"
    
    @.str = private unnamed_addr constant [6 x i8] c"Hum?\0A\00", align 1
    @.str.1 = private unnamed_addr constant [26 x i8] c"Looks like a zero to me!\0A\00", align 1
    @.str.2 = private unnamed_addr constant [31 x i8] c"A non-zero value? How quaint!\0A\00", align 1
    @__afl_area_ptr = external global i8*
    @__afl_prev_loc = external thread_local global i32
    
    ; Function Attrs: noinline nounwind ssp uwtable
    define i32 @main(i32 %0, i8** %1) #0 {
      %3 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %4 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %5 = xor i32 %3, 17767
      %6 = getelementptr i8, i8* %4, i32 %5
      %7 = load i8, i8* %6, !nosanitize !3
      %8 = add i8 %7, 1
      store i8 %8, i8* %6, !nosanitize !3
      store i32 8883, i32* @__afl_prev_loc, !nosanitize !3
      %9 = alloca [8 x i8], align 1
      %10 = getelementptr inbounds [8 x i8], [8 x i8]* %9, i64 0, i64 0
      %11 = call i64 @"\01_read"(i32 0, i8* %10, i64 8)
      %12 = icmp slt i64 %11, 1
      br i1 %12, label %13, label %21
    
    13:                                               ; preds = %2
      %14 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %15 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %16 = xor i32 %14, 9158
      %17 = getelementptr i8, i8* %15, i32 %16
      %18 = load i8, i8* %17, !nosanitize !3
      %19 = add i8 %18, 1
      store i8 %19, i8* %17, !nosanitize !3
      store i32 4579, i32* @__afl_prev_loc, !nosanitize !3
      %20 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([6 x i8], [6 x i8]* @.str, i64 0, i64 0))
      call void @exit(i32 1) #3
      unreachable
    
    21:                                               ; preds = %2
      %22 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %23 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %24 = xor i32 %22, 39017
      %25 = getelementptr i8, i8* %23, i32 %24
      %26 = load i8, i8* %25, !nosanitize !3
      %27 = add i8 %26, 1
      store i8 %27, i8* %25, !nosanitize !3
      store i32 19508, i32* @__afl_prev_loc, !nosanitize !3
      %28 = getelementptr inbounds [8 x i8], [8 x i8]* %9, i64 0, i64 0
      %29 = load i8, i8* %28, align 1
      %30 = sext i8 %29 to i32
      %31 = icmp eq i32 %30, 48
      br i1 %31, label %32, label %40
    
    32:                                               ; preds = %21
      %33 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %34 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %35 = xor i32 %33, 18547
      %36 = getelementptr i8, i8* %34, i32 %35
      %37 = load i8, i8* %36, !nosanitize !3
      %38 = add i8 %37, 1
      store i8 %38, i8* %36, !nosanitize !3
      store i32 9273, i32* @__afl_prev_loc, !nosanitize !3
      %39 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([26 x i8], [26 x i8]* @.str.1, i64 0, i64 0))
      br label %48
    
    40:                                               ; preds = %21
      %41 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %42 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %43 = xor i32 %41, 56401
      %44 = getelementptr i8, i8* %42, i32 %43
      %45 = load i8, i8* %44, !nosanitize !3
      %46 = add i8 %45, 1
      store i8 %46, i8* %44, !nosanitize !3
      store i32 28200, i32* @__afl_prev_loc, !nosanitize !3
      %47 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([31 x i8], [31 x i8]* @.str.2, i64 0, i64 0))
      br label %48
    
    48:                                               ; preds = %40, %32
      %49 = load i32, i32* @__afl_prev_loc, !nosanitize !3
      %50 = load i8*, i8** @__afl_area_ptr, !nosanitize !3
      %51 = xor i32 %49, 23807
      %52 = getelementptr i8, i8* %50, i32 %51
      %53 = load i8, i8* %52, !nosanitize !3
      %54 = add i8 %53, 1
      store i8 %54, i8* %52, !nosanitize !3
      store i32 11903, i32* @__afl_prev_loc, !nosanitize !3
      call void @exit(i32 0) #3
      unreachable
    }
    
    declare i64 @"\01_read"(i32, i8*, i64) #1
    
    declare i32 @printf(i8*, ...) #1
    
    ; Function Attrs: noreturn
    declare void @exit(i32) #2
    
    attributes #0 = { noinline nounwind ssp uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "min-legal-vector-width"="0" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #1 = { "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #2 = { noreturn "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "frame-pointer"="all" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="penryn" "target-features"="+cx16,+cx8,+fxsr,+mmx,+sahf,+sse,+sse2,+sse3,+sse4.1,+ssse3,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
    attributes #3 = { noreturn }
    
    !llvm.module.flags = !{!0, !1}
    !llvm.ident = !{!2}
    
    !0 = !{i32 1, !"wchar_size", i32 4}
    !1 = !{i32 7, !"PIC Level", i32 2}
    !2 = !{!"clang version 10.0.0 "}
    !3 = !{}
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **sakura** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/213430](/post/id/213430)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞挖掘](/tag/漏洞挖掘)
  * [Fuzz](/tag/Fuzz)
  * [AFL](/tag/AFL)

 **+1** __8赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/44110799D419F015C1D87EF97B55B122/40)
sakura

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

