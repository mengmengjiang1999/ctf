# afl-fuzz源码分析

## GCC编译流程

![image](https://image.3001.net/images/20230728/1690553246_64c3cb9ee56bbbc08f2b7.png!small)

  1. 预处理（Preprocessing）：对源代码进行预处理，如宏替换、条件编译等，生成经过预处理的源代码。预处理可以通过`gcc -E`命令单独执行。

  2. 编译（Compilation）：将预处理后的源代码翻译成汇编代码（Assembly code），生成`.s`文件。编译可以通过`gcc -S`命令单独执行。

  3. 汇编（Assembly）：将汇编代码翻译成机器语言的二进制指令（Object code），生成`.o`文件。汇编可以通过`as`程序单独执行。

  4. 链接（Linking）：将多个`.o`文件或库文件（如`.a`或`.so`）链接成可执行程序或共享库文件，生成最终的二进制文件。链接可以通过`ld`程序单独执行，但通常由GCC自动调用。

## 1.afl-gcc

afl-gcc本身是gcc编译器的封装,通过afl的一些环境变量,设置一些gcc的编译选项,如asan,msan,编译器优化等,指定汇编器为afl-as,生成ob code.

###  **全局变量**

    
    
    static u8*  as_path;                /* Path to the AFL 'as' wrapper      */
    static u8** cc_params;              /* Parameters passed to the real CC  */
    static u32  cc_par_cnt = 1;         /* Param count, including argv0      */
    static u8   be_quiet,               /* Quiet mode                        */
                clang_mode;             /* Invoked as afl-clang*?            */
    

as_path:afl-as的路径

cc_params:调用gcc或者clang的参数

cc_par_cnt:gcc clang参数数量

be_quiet:静默模式

clang_mode:是否使用afl-clang

###  **main**

    
    
    int main(int argc, char** argv) {
    
      if (isatty(2) && !getenv("AFL_QUIET")) {
    
        SAYF(cCYA "afl-cc " cBRI VERSION cRST " by <lcamtuf@google.com>\n");
    
      } else be_quiet = 1;
    
      if (argc < 2) {
    
        SAYF("\n"
             "This is a helper application for afl-fuzz. It serves as a drop-in replacement\n"
             "for gcc or clang, letting you recompile third-party code with the required\n"
             "runtime instrumentation. A common use pattern would be one of the following:\n\n"
    
             "  CC=%s/afl-gcc ./configure\n"
             "  CXX=%s/afl-g++ ./configure\n\n"
    
             "You can specify custom next-stage toolchain via AFL_CC, AFL_CXX, and AFL_AS.\n"
             "Setting AFL_HARDEN enables hardening optimizations in the compiled code.\n\n",
             BIN_PATH, BIN_PATH);
    
        exit(1);
    
      }
    
      find_as(argv[0]);
    
      edit_params(argc, argv);
    
      execvp(cc_params[0], (char**)cc_params);
    
      FATAL("Oops, failed to execute '%s' - check your PATH", cc_params[0]);
    
      return 0;
    
    }
    

be_quiet为1时,不会打印程序输出信息

主要功能集中在find_as,edit_params函数,最后执行execvp

### find_as

函数功能是寻找伪造的gcc-as(afl-as)汇编程序,实际上是通过环境变量"AFL_PATH"或者afl-gcc的当前执行目录寻找afl-as的路径.

### edit_params

函数功能是,将argv的参数复制到cc_params,以及做一些参数的处理.

首先alloc给cc_params一个(argc+128)*8字节大小的内存

1.检查当前执行程序名是否为afl-clangxx,如果是

clang_mode=1,表示使用afl-clang模式

如果是clang++

尝试获取AFL_CXX环境变量.或者使用默认值"clang++",赋值给cc_params[0]

如果不是clang++

尝试获取AFL_CC环境变量.或者使用默认值"clang",赋值给cc_params[0]

如果不是afl-clangxx,会认为是apple平台并做一些处理,这里不做赘述.

2.while循环,遍历argv[1]和之后的参数,做一些处理.

参数:-B是否指定了汇编器afl-as的路径,如果是默认模式,直接跳过.

参数:-integrated-as和-pipe 直接跳过不做处理.

参数:-fsanitize=address和-fsanitize=memory,gcc的编译选项,LLVM的组件Asan,将asan_set=1,这两个参数是Asan用于检测内存访问越界,内存泄露问题的.如果编译时插入一些安全检查,需要记录和跟踪信息,可以加上.

参数:FORTIFY_SOURCE,将fortify_set =
1,gcc编译时会在一些容易出现漏洞的函数插入一些安全检查,如memcpy,strcpy...

3.while结束,对前面做的一些标记做参数处理.

-B as_path,find_as里面寻找到的afl-as路径.

clang_mode为1 设置-no-integrated-as

如果环境变量存在AFL_HARDEN.设置gcc -fstack-protector-all和-D_FORTIFY_SOURCE=2,这个afl的编译选项,会开启一些编译时的安全保护.  
如果asan_set为1,设置了些编译时的内存错误检测,设置环境变量AFL_USE_ASAN为1

编译选项asan和msan相关,添加这些编译选项,利于内存错误的分析

获取环境变量AFL_USE_ASAN,AFL_USE_MSAN,AFL_HARDEN,设置了一些-U_FORTIFY_SOURCE和-fsanitize=memory参数,只是此处AFL_USE_ASAN和AFL_USE_MSAN不能同时设置,因为使用asan和msan编译同一源代码时,会对运行速度造成影响,afl-fuzz可能会觉得对效率有影响

编译器优化相关,添加这些编译选项,禁止编译优化,利于afl-fuzz更好的探测一些漏洞,但是程序会变慢,可能会对fuzz效率造成影响.

获取环境变量AFL_DONT_OPTIMIZE,存在

设置gcc编译选项-g -O3 -funroll-loops -D__AFL_COMPILER=1
-DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1

编译器内置函数优化相关的一些编译选项,内置函数可能不安全,禁用可能会导致程序变慢.

获取环境变量AFL_NO_BUILTIN,存在

一些函数不使用编译器内置的,如下:

    
    
    cc_params[cc_par_cnt++] = "-fno-builtin-strcmp";
     cc_params[cc_par_cnt++] = "-fno-builtin-strncmp";
     cc_params[cc_par_cnt++] = "-fno-builtin-strcasecmp";
     cc_params[cc_par_cnt++] = "-fno-builtin-strncasecmp";
     cc_params[cc_par_cnt++] = "-fno-builtin-memcmp";
     cc_params[cc_par_cnt++] = "-fno-builtin-strstr";
     cc_params[cc_par_cnt++] = "-fno-builtin-strcasestr";
    

### execvp(cc_params[0], (char**)cc_params);

afl-fuzz目录下会有一个as的连接,指向afl-as,gcc编译时,汇编器指定了afl-fuzz目录,会自动寻找as,从而执行afl-as,简而言之,就是代替了系统的汇编器as

执行gcc, 指定汇编器为afl-fuzz目录下的as(afl-as)进行汇编,,带上设置好的参数.

    
    
    for (int i = 0; i < sizeof(cc_params); ++i) {
            SAYF("%s ", *(cc_params + i));
        }
    
    
    
    gcc ../testc.c -o ../testc -B /home/ash/code/afl-fuzz -g -O3 -funroll-loops -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1
    

## 2.afl-as

afl-as是gas汇编器的封装.

### 全局变量

    
    
    static u8** as_params;          /* Parameters passed to the real 'as'   */
    
    static u8*  input_file;         /* Originally specified input file      */
    static u8*  modified_file;      /* Instrumented file for the real 'as'  */
    
    static u8   be_quiet,           /* Quiet mode (no stderr output)        */
                clang_mode,         /* Running in clang mode?               */
                pass_thru,          /* Just pass data through?              */
                just_version,       /* Just show version?                   */
                sanitizer;          /* Using ASAN / MSAN                    */
    
    static u32  inst_ratio = 100,   /* Instrumentation probability (%)      */
                as_par_cnt = 1;     /* Number of params to 'as'             */
    

as_params:gcc传递给as的参数

input_file:指定输入文件

modified_file:afl-as输出的插桩后的汇编文件

be_quiet:静默模式

clang_mode:clang编译模式

pass_thru:是否在汇编时不做插桩.

just_version:只显示版本

sanitizer:使用asan/msan

inst_ratio:插桩代码的比例.

as_par_cnt:指定线程运行afl-as

### main

gcc传递过来的参数

    
    
    /home/ash/code/afl-fuzz/as --gdwarf-5 --64 -o /tmp/ccQwLzYy.o /tmp/ccw6hnjr.s
    

首先从环境变量中获取AFL_INST_RATIO,赋值给inst_ratio_str,这个变量代表插桩频率,如果为100,则在每个块中都会插入插桩代码,如果为0,则只插桩函数入口的块.

获取当前时间,pid,计算成一个rand_seed,生成随机数.

edit_params函数对参数进行处理

获取环境变量AS_LOOP_ENV_VAR,这个环境变量是afl-as重复汇编的次数,默认设置为1.为了解决插桩可能会导致的执行异常情况,多次通过随机值插桩,避免程序出现异常.

通过检查环境变量AFL_USE_ASAN,AFL_USE_MSAN,判断是否存在这些编译选项,将sanitizer设置为1,并将inst_ratio/3,这里做了处理原因如果开启了asan或者msan会导致程序的分支增多,在插桩到这些分支,然后执行,是没有意义的.所以这里直接做了除3处理,将比例减小.

执行add_instrumentation函数,开始插桩

fork一个子进程执行gas进行汇编,参数

    
    
    as --gdwarf-5 --64 -o /tmp/ccQwLzYy.o /tmp/.afl-1040-1683019150.s
    

gas执行结束后,检测环境变量AFL_KEEP_ASSEMBLY,如果没有就删除掉插桩的汇编文件.

### edit_params

主要是做as的参数处理,构造汇编文件名参数,架构,赋值input_file=汇编文件.

### add_instrumentation

插桩函数

首先获取需要插桩的汇编文件赋值于inputfile,而后在本地创建插桩文件modified_file,并打开赋值于outf.

逐行读取至line数组中,然后做一些条件判断,跳过标签,宏,注释这些不需要插桩的地方,这里是通过一些标志位判断的.

输入代码到modified_file.

对当前读取到的区段进行判断,如果为.text相关的区段,将标志位instr_ok修改为1,表示将对代码分支进行插桩.

如果为bss,data这些数据段,标志为0,不会进行插桩.

如果为p2align宏,将标志位skip_next_label更改为1.

    
    
    if (line[0] == '\t' && line[1] == '.') {
    
                /* OpenBSD puts jump tables directly inline with the code, which is
                   a bit annoying. They use a specific format of p2align directives
                   around them, so we use that as a signal. */
    
                if (!clang_mode && instr_ok && !strncmp(line + 2, "p2align ", 8) &&
                    isdigit(line[10]) && line[11] == '\n')
                    skip_next_label = 1;
    
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
    

检测是否为.code段,如果为.code32,需要跳过,.code64不跳过.

如果为.intel_syntax,需要跳过,.att_syntax不跳过.

检测和跳过ad-hoc ___asm___代码块,#APP表示,进入代码块,需要跳过,#NO_APP表示结束,需要插桩.

这里做的处理是跳过一些不需要插桩的部分,确保程序不会出错.

    
    
    if (strstr(line, ".code")) {
    
                if (strstr(line, ".code32")) skip_csect = use_64bit;
                if (strstr(line, ".code64")) skip_csect = !use_64bit;
    
            }
    
            /* Detect syntax changes, as could happen with hand-written assembly.
               Skip Intel blocks, resume instrumentation when back to AT&T. */
    
            if (strstr(line, ".intel_syntax")) skip_intel = 1;
            if (strstr(line, ".att_syntax")) skip_intel = 0;
    
            /* Detect and skip ad-hoc __asm__ blocks, likewise skipping them. */
    
            if (line[0] == '#' || line[1] == '#') {
    
                if (strstr(line, "#APP")) skip_app = 1;
                if (strstr(line, "#NO_APP")) skip_app = 0;
    
            }
    

afl-fuzz插桩的范围

^main: - 函数入口点  
^.L0: - GCC分支标签  
^.LBB0_0: - clang分支标签（但只在clang模式下）。  
^tjnz foo - 条件跳转分支

总之,是主要的main函数,和条件分支指令前进行插桩,以此实现fuzz的路径覆盖率检测,其中又包含了对插桩比例的计算,随机数小于inst_ratio才会进行插桩.

而后将插桩指令写入至outfd,这里通过对架构进行了判断,以插入不同的桩代码,并生成了一个随机数写入R(MAP_SIZE),作为桩的编号,然后将ins_lines,插桩计数+1.

    
    
    /* If we're in the right mood for instrumenting, check for function
               names or conditional labels. This is a bit messy, but in essence,
               we want to catch:
    
                 ^main:      - function entry point (always instrumented)
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
    
               Additionally, clang and GCC on MacOS X follow a different convention
               with no leading dots on labels, hence the weird maze of #ifdefs
               later on.
    
             */
    
            if (skip_intel || skip_app || skip_csect || !instr_ok ||
                line[0] == '#' || line[0] == ' ')
                continue;
    
            /* Conditional branch instruction (jnz, etc). We append the instrumentation
               right after the branch (to instrument the not-taken path) and at the
               branch destination label (handled later on). */
    
            if (line[0] == '\t') {
    
                if (line[1] == 'j' && line[2] != 'm' && R(100) < inst_ratio) {
    
                    fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32,
                            R(MAP_SIZE));
    
                    ins_lines++;
    
                }
    
                continue;
    
            }
    

而后判断是否为`:`的判断,下个字符是否为`.`,如果不是,afl-as默认当作一个function.,将instrument_next更改为1.

如果是继续判断,是否为`.L`和`.LBB`这种需要插桩的跳转目标标签.

gnu编译器,通常以`.L0`开头,clang编译下,以`.LBB`开头,计算inst_ratio通过后,将instrument_next更改为1.

    
    
    #ifdef __APPLE__
    
            /* Apple: L<whatever><digit>: */
    
            if ((colon_pos = strstr(line, ":"))) {
    
              if (line[0] == 'L' && isdigit(*(colon_pos - 1))) {
    
    #else
    
            /* Everybody else: .L<whatever>: */
    
            if (strstr(line, ":")) {
    
                if (line[0] == '.') {
    
    #endif /* __APPLE__ */
    
                    /* .L0: or LBB0_0: style jump destination */
    
    #ifdef __APPLE__
    
                    /* Apple: L<num> / LBB<num> */
    
                    if ((isdigit(line[1]) || (clang_mode && !strncmp(line, "LBB", 3)))
                        && R(100) < inst_ratio) {
    
    #else
    
                    /* Apple: .L<num> / .LBB<num> */
    
                    if ((isdigit(line[2]) || (clang_mode && !strncmp(line + 1, "LBB", 3)))
                        && R(100) < inst_ratio) {
    
    #endif /* __APPLE__ */
    
                        /* An optimization is possible here by adding the code only if the
                           label is mentioned in the code in contexts other than call / jmp.
                           That said, this complicates the code by requiring two-pass
                           processing (messy with stdin), and results in a speed gain
                           typically under 10%, because compilers are generally pretty good
                           about not generating spurious intra-function jumps.
    
                           We use deferred output chiefly to avoid disrupting
                           .Lfunc_begin0-style exception handling calculations (a problem on
                           MacOS X). */
    
                        if (!skip_next_label) instrument_next = 1; else skip_next_label = 0;
    
                    }
    
                } else {
    
                    /* Function label (always instrumented, deferred mode). */
    
                    instrument_next = 1;
    
                }
    
            }
    
        }
    

最后,结束while循环.

判断ins_lines插桩数量不为0,则根据架构插入main_payload64或main_payload_32

而后释放资源.

### afl-as桩代码分析

    
    
    lea     rsp, [rsp-98h]
    mov     [rsp+0A0h+var_A0], rdx
    mov     [rsp+0A0h+var_98], rcx
    mov     [rsp+0A0h+var_90], rax
    mov     rcx, 0D8FEh
    call    __afl_maybe_log
    mov     rax, [rsp+0A0h+var_90]
    mov     rcx, [rsp+0A0h+var_98]
    mov     rdx, [rsp+0A0h+var_A0]
    lea     rsp, [rsp+98h]
    

保存rdc,rcx,rax寄存器状态

传入一个随机数至rcx,这个随机数是之前R(MAP_SIZE)产生的,调用__afl_maybe_log

恢复寄存器

    
    
    .lcomm   __afl_area_ptr, 8
    .lcomm   __afl_prev_loc, 8
    .lcomm   __afl_fork_pid, 4
    .lcomm   __afl_temp, 4
    .lcomm   __afl_setup_failure, 1
    .comm    __afl_global_area_ptr, 8, 8
    

通过`.comm`,`.lcomm`在bss段初始化的一些变量.

__afl_area_ptr:一块内存的指针,记录当前代码块的执行信息

__afl_prev_loc:记录上一个插桩的路径信息.

_afl_maybe_log首次执行流程:

    
    
    .text:00005555555554F0 lahf
    .text:00005555555554F1 seto    al
    .text:00005555555554F4 mov     rdx, cs:__afl_area_ptr
    .text:00005555555554FB test    rdx, rdx
    .text:00005555555554FE jz      short __afl_setup
    

首先执行lahf和 seto al将eflags寄存器的低8位(SF,ZF,AF,PF,CF)和OF保存到ax中.

判断`__afl_area_ptr`是否为0,为0执行`__afl_setup`

    
    
    .text:0000555555555528 __afl_setup: 
    .text:0000555555555528 cmp     cs:__afl_setup_failure, 0
    .text:000055555555552F jnz     short __afl_return
    .text:000055555555552F
    .text:0000555555555531 lea     rdx, __afl_global_area_ptr
    .text:0000555555555538 mov     rdx, [rdx]
    .text:000055555555553B test    rdx, rdx
    .text:000055555555553E jz      short __afl_setup_first
    

继续判断`__afl_setup_failure`是否为0,不为0说明afl初始化时发生了错误,直接调用`__afl_return`还原,结束.

继续判断`afl_global_area_ptr`中指针指向的内存是否为0,如果为0,说明afl是首次执行,执行`__afl_setup_first`

    
    
    .text:0000555555555549 __afl_setup_first:                      ; CODE XREF: __afl_maybe_log+4E↑j
    .text:0000555555555549 lea     rsp, [rsp-160h]
    .text:0000555555555551 mov     [rsp+160h+var_160], rax
    .text:0000555555555555 mov     [rsp+160h+var_158], rcx
    .text:000055555555555A mov     [rsp+160h+var_150], rdi
    .text:000055555555555F mov     [rsp+160h+var_140], rsi
    .text:0000555555555564 mov     [rsp+160h+var_138], r8
    .text:0000555555555569 mov     [rsp+160h+var_130], r9
    .text:000055555555556E mov     [rsp+160h+var_128], r10
    .text:0000555555555573 mov     [rsp+160h+var_120], r11
    .text:0000555555555578 movq    [rsp+160h+var_100], xmm0
    .text:000055555555557E movq    [rsp+160h+var_F0], xmm1
    .text:0000555555555584 movq    [rsp+160h+var_E0], xmm2
    .text:000055555555558D movq    [rsp+160h+var_D0], xmm3
    .text:0000555555555596 movq    [rsp+160h+var_C0], xmm4
    .text:000055555555559F movq    [rsp+160h+var_B0], xmm5
    .text:00005555555555A8 movq    [rsp+160h+var_A0], xmm6
    .text:00005555555555B1 movq    [rsp+160h+var_90], xmm7
    .text:00005555555555BA movq    [rsp+160h+var_80], xmm8
    .text:00005555555555C4 movq    [rsp+160h+var_70], xmm9
    .text:00005555555555CE movq    [rsp+160h+var_60], xmm10
    .text:00005555555555D8 movq    [rsp+160h+var_50], xmm11
    .text:00005555555555E2 movq    [rsp+160h+var_40], xmm12
    .text:00005555555555EC movq    [rsp+160h+var_30], xmm13
    .text:00005555555555F6 movq    [rsp+160h+var_20], xmm14
    .text:0000555555555600 movq    [rsp+160h+var_10], xmm15
    .text:000055555555560A push    r12
    .text:000055555555560C mov     r12, rsp
    .text:000055555555560F sub     rsp, 10h
    .text:0000555555555613 and     rsp, 0FFFFFFFFFFFFFFF0h
    .text:0000555555555617 lea     rdi, _AFL_SHM_ENV               ; "__AFL_SHM_ID"
    .text:000055555555561E call    _getenv
    .text:000055555555561E
    .text:0000555555555623 test    rax, rax
    .text:0000555555555626 jz      __afl_setup_abort
    .text:0000555555555626
    .text:000055555555562C mov     rdi, rax                        ; nptr
    .text:000055555555562F call    _atoi
    .text:000055555555562F
    .text:0000555555555634 xor     rdx, rdx                        ; shmflg
    .text:0000555555555637 xor     rsi, rsi                        ; shmaddr
    .text:000055555555563A mov     rdi, rax                        ; shmid
    .text:000055555555563D call    _shmat
    .text:000055555555563D
    .text:0000555555555642 cmp     rax, 0FFFFFFFFFFFFFFFFh
    .text:0000555555555646 jz      __afl_setup_abort
    .text:0000555555555646
    .text:000055555555564C mov     byte ptr [rax], 1
    .text:000055555555564F mov     rdx, rax
    .text:0000555555555652 mov     cs:__afl_area_ptr, rax
    .text:0000555555555659 lea     rdx, __afl_global_area_ptr
    .text:0000555555555660 mov     [rdx], rax
    .text:0000555555555663 mov     rdx, rax
    

`__afl_setup_first`中开辟了160字节的栈帧,保存当前寄存器的状态.

获取环境变量`__AFL_SHM_ID`的值.该值是一个共享内存id,用于fuzz时不同进程之间的通信.

如果失败执行`__afl_setup_abort`:`__afl_setup_failure`自增,还原寄存器状态,释放栈,调用`__afl_return`还原,结束.

执行shmat获取`__AFL_SHM_ID`对应的共享内存,附加后,获取在本进程空间可以访问的地址.如果失败,则执行`__afl_setup_abort`

在共享内存中写入1.将地址写入`_afl_area_ptr`和`_afl_global_area_ptr`

而后开始执行`__afl_forkserver`

    
    
    pushq %rdx
    pushq %rdx
    movq $4, %rdx               					/* length    */
    leaq __afl_temp(%rip), %rsi 					/* data      */
    movq $" STRINGIFY((FORKSRV_FD + 1)) ", %rdi       /* file desc */
    CALL_L64("write")
    cmpq $4, %rax
    jne  __afl_fork_resume
    
    
    
    /* Designated file descriptors for forkserver commands (the application will
       use FORKSRV_FD and FORKSRV_FD + 1): */
    
    #define FORKSRV_FD          198
    

将`__afl_temp`的值写入到指定的通信描述符中.`__afl_temp`实质上存储的是后面fork
server的状态.这里如果写入失败将会跳转到`__afl_fork_resume`->`__afl_store`->`__afl_return`

`__afl_fork_resume`:释放资源,恢复寄存器状态

    
    
    .text:0000555555555531 48 8D 15 00 2B 00 00          lea     rdx, __afl_global_area_ptr
    .text:0000555555555538 48 8B 12                      mov     rdx, [rdx]
    .text:000055555555553B 48 85 D2                      test    rdx, rdx
    .text:000055555555553E 74 09                         jz      short __afl_setup_first
    .text:000055555555553E
    .text:0000555555555540 48 89 15 D1 2A 00 00          mov     cs:__afl_area_ptr, rdx
    .text:0000555555555547 EB B7                         jmp     short __afl_store
    
    
    
    .text:0000555555555500                               __afl_store:                            ; CODE XREF: __afl_maybe_log+57↓j
    .text:0000555555555500                                                                       ; __afl_maybe_log+314↓j
    .text:0000555555555500 48 33 0D 19 2B 00 00          xor     rcx, cs:__afl_prev_loc
    .text:0000555555555507 48 31 0D 12 2B 00 00          xor     cs:__afl_prev_loc, rcx
    .text:000055555555550E 48 D1 2D 0B 2B 00 00          shr     cs:__afl_prev_loc, 1
    .text:0000555555555515 80 04 0A 01                   add     byte ptr [rdx+rcx], 1
    .text:0000555555555519 80 14 0A 00                   adc     byte ptr [rdx+rcx], 0
    

`__afl_store`:

首先将当前桩的值(R(MAPSIZE))异或先前桩的值,然后右移1位.再将`__afl_prev_loc`异或这个值,然后将rcx中的值作为偏移`__afl_global_area_ptr`中指向的内存作为偏移,将此位置+1.

实际上在内存中形成了一个map结构,记录了分支执行次数,右移的目的是为了如果当前分支和上一个分支是一样的,xor的结果是0的情况.

还有一种情况时2个分支如果相互都存在执行关系的话,xor结果是一样的,右移后就可以区分了.

`__afl_return`:恢复eflags寄存器状态

    
    
    .text:000055555555568C                               __afl_fork_wait_loop:                   ; CODE XREF: __afl_maybe_log+22F↓j
    .text:000055555555568C 48 C7 C2 04 00 00 00          mov     rdx, 4                          ; nbytes
    .text:0000555555555693 48 8D 35 92 29 00 00          lea     rsi, __afl_temp                 ; buf
    .text:000055555555569A 48 C7 C7 C6 00 00 00          mov     rdi, 0C6h                       ; status
    .text:00005555555556A1 E8 CA FA FF FF                call    _read
    .text:00005555555556A1
    .text:00005555555556A6 48 83 F8 04                   cmp     rax, 4
    .text:00005555555556AA 0F 85 59 01 00 00             jnz     __afl_die
    .text:00005555555556AA
    .text:00005555555556B0 E8 2B FB FF FF                call    _fork
    .text:00005555555556B0
    .text:00005555555556B5 48 83 F8 00                   cmp     rax, 0
    .text:00005555555556B9 0F 8C 4A 01 00 00             jl      __afl_die
    .text:00005555555556B9
    .text:00005555555556BF 74 63                         jz      short __afl_fork_resume
    .text:00005555555556BF
    .text:00005555555556C1 89 05 61 29 00 00             mov     cs:__afl_fork_pid, eax
    .text:00005555555556C7 48 C7 C2 04 00 00 00          mov     rdx, 4                          ; n
    .text:00005555555556CE 48 8D 35 53 29 00 00          lea     rsi, __afl_fork_pid             ; buf
    .text:00005555555556D5 48 C7 C7 C7 00 00 00          mov     rdi, 0C7h                       ; fd
    .text:00005555555556DC E8 6F FA FF FF                call    _write
    .text:00005555555556DC
    .text:00005555555556E1 48 C7 C2 00 00 00 00          mov     rdx, 0                          ; options
    .text:00005555555556E8 48 8D 35 3D 29 00 00          lea     rsi, __afl_temp                 ; stat_loc
    .text:00005555555556EF 48 8B 3D 32 29 00 00          mov     rdi, qword ptr cs:__afl_fork_pid ; pid
    .text:00005555555556F6 E8 B5 FA FF FF                call    _waitpid
    .text:00005555555556F6
    .text:00005555555556FB 48 83 F8 00                   cmp     rax, 0
    .text:00005555555556FF 0F 8E 04 01 00 00             jle     __afl_die
    .text:00005555555556FF
    .text:0000555555555705 48 C7 C2 04 00 00 00          mov     rdx, 4                          ; n
    .text:000055555555570C 48 8D 35 19 29 00 00          lea     rsi, __afl_temp                 ; buf
    .text:0000555555555713 48 C7 C7 C7 00 00 00          mov     rdi, 0C7h                       ; fd
    .text:000055555555571A E8 31 FA FF FF                call    _write
    .text:000055555555571A
    .text:000055555555571F E9 68 FF FF FF                jmp     __afl_fork_wait_loop
    

接着会执行`__afl_fork_wait_loop`的流程,中间如果遇到系统调用失败的问题,会跳转至`__afl_die`直接退出进程.

首先会阻塞读取指定的通信描述符`FORKSRV_FD`的值,,读取失败会结束进程,然后__fork一个子进程,它的作用在afl-fuzz.c中会体现,用于控制fork server.

子进程执行`__afl_fork_resume`

当前进程:

当前进程将子进程id记录到`__afl_fork_pid`,将子进程id写入共享内存当中.

waitpid等待子进程执行完毕,并将status存储至`__afl_temp`

然后将status信息写入共享内存.而后继续循环`__afl_fork_wait_loop`的流程.

子进程:

释放资源,恢复状态,继续向下执行代码

## 4.afl-clang-fast

afl-fast-clang与之前的afl-gcc实现思路是一样的,它是clang的一层封装

与afl-gcc不同的是,afl-fast-clang使用了llvm pass进行了插桩.

这也是afl-fuzz推荐的一种插桩和编译方式,因为llvm是模块化的,使用llvm pass可扩展性比较强.

之前分析过afl-gcc,afl-fast-clang与它功能一致,这里一些基本的函数就简单概述下,主要是分析下llvm pass的代码

### 全局变量

    
    
    static u8*  obj_path;               //LLVM PASS程序路径
    static u8** cc_params;              //clang参数
    static u32  cc_par_cnt = 1;         //clang参数数量
    

### find_obj

从环境变量`AFL_PATH`寻找`afl-llvm-rt.o`,或者从当前目录找,最后从AFL_PATH宏去找,找到后赋值obj_path.找不到报错.

### edit_params

主要是设置clang的参数

通过当前执行afl-clang-fast/afl-clang-fast++设置参数clang/clang++,并设置环境变量AFL_CXX/AFL_CC

而后load llvm pass插件afl-llvm-pass.so编译目标,传入插桩参数

根据传入参数,设置bit_mode,x_set,asan_set的值.

如果x_set的值为1,则设置参数为-x none

根据bit_mode的值,设置参数obj_path/afl-llvm-rt-32.o或obj_path/afl-llvm-rt-64.o,

默认为obj_path/afl-llvm-rt.o

然后设置AFL运行时库`afl-llvm-rt.o`的一些宏.

### main

main函数在执行find_obj设置obj_path和调用edit_params设置参数后,执行execvp,参数如下

    
    
    clang -Xclang -load -Xclang /home/ash/code/afl-fuzz/afl-llvm-pass.so -Qunused-arguments ../testc.c -o ../testc.o -g -O3 -funroll-loops -D__AFL_HAVE_MANUAL_CONTROL=1 -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1 -D__AFL_LOOP(_A)=({ static volatile char *_B __attribute__((used));  _B = (char*)"##SIG_AFL_PERSISTENT##"; __attribute__((visibility("default"))) int _L(unsigned int) __asm__("__afl_persistent_loop"); _L(_A); }) -D__AFL_INIT()=do { static volatile char *_A __attribute__((used));  _A = (char*)"##SIG_AFL_DEFER_FORKSRV##"; __attribute__((visibility("default"))) void _I(void) __asm__("__afl_manual_init"); _I(); } while (0) /home/ash/code/afl-fuzz/afl-llvm-rt.o
    

### llvm-pass代码分析

    
    
    namespace {
    
      class AFLCoverage : public ModulePass {
    
        public:
    
          static char ID;
          AFLCoverage() : ModulePass(ID) { }
    
          bool runOnModule(Module &M) override;
    
          // StringRef getPassName() const override {
          //  return "American Fuzzy Lop Instrumentation";
          // }
    
      };
    
    }
    

afl-fuzz编写的pass名为AFLCoverage,以模块为单位对IR进行处理.重点看下runOnModule,看看是怎么对模块进行处理的.

    
    
    bool AFLCoverage::runOnModule(Module &M) {
    
      LLVMContext &C = M.getContext();
    
      IntegerType *Int8Ty  = IntegerType::getInt8Ty(C);
      IntegerType *Int32Ty = IntegerType::getInt32Ty(C);
    
      /* Show a banner */
    
      char be_quiet = 0;
    
      if (isatty(2) && !getenv("AFL_QUIET")) {
    
        SAYF(cCYA "afl-llvm-pass " cBRI VERSION cRST " by <lszekeres@google.com>\n");
    
      } else be_quiet = 1;
    
      /* Decide instrumentation ratio */
    
      char* inst_ratio_str = getenv("AFL_INST_RATIO");
      unsigned int inst_ratio = 100;
    
      if (inst_ratio_str) {
    
        if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || !inst_ratio ||
            inst_ratio > 100)
          FATAL("Bad value of AFL_INST_RATIO (must be between 1 and 100)");
    
      }
    
      /* Get globals for the SHM region and the previous location. Note that
         __afl_prev_loc is thread-local. */
    
      GlobalVariable *AFLMapPtr =
          new GlobalVariable(M, PointerType::get(Int8Ty, 0), false,
                             GlobalValue::ExternalLinkage, 0, "__afl_area_ptr");
    
      GlobalVariable *AFLPrevLoc = new GlobalVariable(
          M, Int32Ty, false, GlobalValue::ExternalLinkage, 0, "__afl_prev_loc",
          0, GlobalVariable::GeneralDynamicTLSModel, 0, false);
    
      /* Instrument all the things! */
    

首先获取LLVM上下文对象,这个上下文对象LLVMContext时llvm用于管理一些信息和状态的,比如常量,函数,类型定义等.

然后通过上下文对象获取了2个整数类型的对象,分别是8为和32位的.

而后通过环境变量`AFL_QUIET`设置是否启用静默模式`be_quiet`

读取环境变量`AFL_INST_RATIO`,设置插桩概率`inst_ratio`的值,默认为100.

而后通过LLVM的`GlobalVariable`类创建了2个全局变量

`__afl_area_ptr`:8位,共享内存,记录桩执行信息

`__afl_prev_loc`:32位,记录先前代码块

    
    
    int inst_blocks = 0;
    
      for (auto &F : M)
        for (auto &BB : F) {
    
          BasicBlock::iterator IP = BB.getFirstInsertionPt();
          IRBuilder<> IRB(&(*IP));
    
          if (AFL_R(100) >= inst_ratio) continue;
    

通过`inst_blocks`变量记录插桩的基本块数量.

然后遍历每个基本块进行处理.

而后通过`BB.getFirstInsertionPt();`从基本块头部开始获取可插入点位置,而后作为构造参数创建了`IRBuilder`对象,用于后面创建和插入指令.

首先生成100内的随机数是否大于`inst_ratio`,大于则跳过不做处理.

    
    
    /* Make up cur_loc */
    
          unsigned int cur_loc = AFL_R(MAP_SIZE);
    
          ConstantInt *CurLoc = ConstantInt::get(Int32Ty, cur_loc);
    
          /* Load prev_loc */
    
          LoadInst *PrevLoc = IRB.CreateLoad(AFLPrevLoc);
          PrevLoc->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
          Value *PrevLocCasted = IRB.CreateZExt(PrevLoc, IRB.getInt32Ty());
    

而后获取了一个随机数,并通过`ConstantInt::get`将这个随机数创建为常量.

然后创建了读取指令用于读取`AFLPrevLoc`的值,获取前一个基本块的编号,并将这个这个指令设置了一个`nosanitize`的属性,并且后面的一些读取指令都加了这个属性,作用应该是编译时,跳过对该指令的一些安全检查,提高fuzz速度.然后创建零扩展指令,对结果进行零扩展.

    
    
    /* Load SHM pointer */
    
          LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
          MapPtr->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
          Value *MapPtrIdx =
              IRB.CreateGEP(MapPtr, IRB.CreateXor(PrevLocCasted, CurLoc));
    

而后创建如下获取共享内存中指定内存地址的操作指令:

创建读取指令读取`AFLMapPtr`,也就是共享内存,然后通过当前基本块id
xor前一个基本块id的结果作为偏移,以`AFLMapPtr`作为基址,获取对应的内存地址.

    
    
    /* Update bitmap */
          LoadInst *Counter = IRB.CreateLoad(MapPtrIdx);
          Counter->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
          Value *Incr = IRB.CreateAdd(Counter, ConstantInt::get(Int8Ty, 1));
          IRB.CreateStore(Incr, MapPtrIdx)
              ->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    

而后创建向上一步获取的内存地址中的数据进行自增的操作指令:

获取内存里的数据,自增之后,再写入.

    
    
    /* Set prev_loc to cur_loc >> 1 */
    
          StoreInst *Store =
              IRB.CreateStore(ConstantInt::get(Int32Ty, cur_loc >> 1), AFLPrevLoc);
          Store->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
    
          inst_blocks++;
    

然后将当前的基本块id右移1位,写入至`AFLPrevLoc`,插桩的基本块计数+1.

右移的目的是为了解决出现以下两种情况存在的问题:

1.如果当前基本块和上一个基本块是一样的,xor的结果是0的情况.

2.如果2个基本块相互存在控制流关系的话,无论从哪个基本块执行到目标基本块,xor结果是一样的,右移后就可以进行区分了.

与前面的afl-as中插桩的代码一样,都是对插桩的基本块执行次数进行了记录,实现覆盖率的反馈.

### afl-llvm-rt.o.c 分析

    
    
    clang -Xclang -load -Xclang /home/ash/code/afl-fuzz/afl-llvm-pass.so -Qunused-arguments ../testc.c -o ../testc.o -g -O3 -funroll-loops -D__AFL_HAVE_MANUAL_CONTROL=1 -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1 -D__AFL_LOOP(_A)=({ static volatile char *_B __attribute__((used));  _B = (char*)"##SIG_AFL_PERSISTENT##"; __attribute__((visibility("default"))) int _L(unsigned int) __asm__("__afl_persistent_loop"); _L(_A); }) -D__AFL_INIT()=do { static volatile char *_A __attribute__((used));  _A = (char*)"##SIG_AFL_DEFER_FORKSRV##"; __attribute__((visibility("default"))) void _I(void) __asm__("__afl_manual_init"); _I(); } while (0) /home/ash/code/afl-fuzz/afl-llvm-rt.o
    

这是afl-clang-fast最终传至clang的参数,包含AFL的运行时库,和一些宏,可以使用llvm mode下的一些额外功能,这部分代码在afl-llvm-rt.o.c中.

首先是初始化的代码

    
    
    __attribute__((constructor(CONST_PRIO))) void __afl_auto_init(void) {
    
      is_persistent = !!getenv(PERSIST_ENV_VAR);
    
      if (getenv(DEFER_ENV_VAR)) return;
    
      __afl_manual_init();
    
    }
    

被`__attribute__((constructor(CONST_PRIO)))`所修饰的函数会在程序启动时优先调用,可以确定的是它是在main函数之前调用,可以定义多个这种类型的函数,其中`CONST_PRIO`表示执行的优先级,

首先获取环境变量`PERSIST_ENV_VAR`,赋值给`is_persistent`,用于标识`persistent
mode`模式,然后获取环境变量`DEFER_ENV_VAR`,如果为true,直接return,这个标志的作用是标识是否延迟fork server

否则执行`__afl_manual_init();`函数,这个函数内部会初始化共享内存和fork server,下面会详细分析.

这样设计的目的是因为在`deferred instrumentation`模式下,需要延迟fork
server,所以会自己定义初始化的位置.不需要自动初始化.

所以这段代码是为了兼容额外模式做的处理.

afl的文档中介绍了3种额外功能模式

#### 1.deferred instrumentation

afl会只执行一次目标二进制文件,在执行某个位置之前停止,然后克隆进程进行持续而稳定的fuzz,这种fuzz的方式减少了大部分操作系统的链接和libc成本,据官方所说,某些情况下可以将性能提高10倍以上.

使用方法:

在代码中找到需要进行暂停,然后克隆进程的位置,需要注意的是,这个位置尽量避免访问和创建一些资源,比如创建线程进程,定时器,临时文件,网络套接字等.

在选好合适的位置后,添加如下代码,然后再使用afl-clang-fast重新编译,它是不支持afl-gcc和afl-clang的.

    
    
    #ifdef __AFL_HAVE_MANUAL_CONTROL
      __AFL_INIT();
    #endif
    
    
    
    cc_params[cc_par_cnt++] = "-D__AFL_INIT()="
                                  "do { static volatile char *_A __attribute__((used)); "
                                  " _A = (char*)\"" DEFER_SIG "\"; "
                                  #ifdef __APPLE__
                                  "__attribute__((visibility(\"default\"))) "
        "void _I(void) __asm__(\"___afl_manual_init\"); "
                                  #else
                                  "__attribute__((visibility(\"default\"))) "
                                  "void _I(void) __asm__(\"__afl_manual_init\"); "
                                  #endif /* ^__APPLE__ */
                                  "_I(); } while (0)";
    

在之前的afl-clang-fast.c中可以看到`__AFL_INIT();`实际执行的函数应是`__afl_manual_init`

    
    
    void __afl_manual_init(void) {
    
      static u8 init_done;
    
      if (!init_done) {
    
        __afl_map_shm();
        __afl_start_forkserver();
        init_done = 1;
    
      }
    
    }
    

如果没有进行初始化就会执行`__afl_map_shm();`,`__afl_start_forkserver();`进行初始化.

`__afl_map_shm`

    
    
    static void __afl_map_shm(void) {
    
      u8 *id_str = getenv(SHM_ENV_VAR);
    
      /* If we're running under AFL, attach to the appropriate region, replacing the
         early-stage __afl_area_initial region that is needed to allow some really
         hacky .init code to work correctly in projects such as OpenSSL. */
    
      if (id_str) {
    
        u32 shm_id = atoi(id_str);
    
        __afl_area_ptr = shmat(shm_id, NULL, 0);
    
        /* Whooooops. */
    
        if (__afl_area_ptr == (void *)-1) _exit(1);
    
        /* Write something into the bitmap so that even with low AFL_INST_RATIO,
           our parent doesn't give up on us. */
    
        __afl_area_ptr[0] = 1;
    
      }
    
    }
    

这个函数是获取共享内存的,前面afl-as中桩代码中也有这部分逻辑,就不会赘述了.

`__afl_start_forkserver();`

    
    
    static void __afl_start_forkserver(void) {
    
      static u8 tmp[4];
      s32 child_pid;
    
      u8  child_stopped = 0;
    
      /* Phone home and tell the parent that we're OK. If parent isn't there,
         assume we're not running in forkserver mode and just execute program. */
    
      if (write(FORKSRV_FD + 1, tmp, 4) != 4) return;
    
      while (1) {
    
        u32 was_killed;
        int status;
    
        /* Wait for parent by reading from the pipe. Abort if read fails. */
    
        if (read(FORKSRV_FD, &was_killed, 4) != 4) _exit(1);
    
        /* If we stopped the child in persistent mode, but there was a race
           condition and afl-fuzz already issued SIGKILL, write off the old
           process. */
    
        if (child_stopped && was_killed) {
          child_stopped = 0;
          if (waitpid(child_pid, &status, 0) < 0) _exit(1);
        }
    
        if (!child_stopped) {
    
          /* Once woken up, create a clone of our process. */
    
          child_pid = fork();
          if (child_pid < 0) _exit(1);
    
          /* In child process: close fds, resume execution. */
    
          if (!child_pid) {
    
            close(FORKSRV_FD);
            close(FORKSRV_FD + 1);
            return;
    
          }
    
        } else {
    
          /* Special handling for persistent mode: if the child is alive but
             currently stopped, simply restart it with SIGCONT. */
    
          kill(child_pid, SIGCONT);
          child_stopped = 0;
    
        }
    
        /* In parent process: write PID to pipe, then wait for child. */
    
        if (write(FORKSRV_FD + 1, &child_pid, 4) != 4) _exit(1);
    
        if (waitpid(child_pid, &status, is_persistent ? WUNTRACED : 0) < 0)
          _exit(1);
    
        /* In persistent mode, the child stops itself with SIGSTOP to indicate
           a successful run. In this case, we want to wake it up without forking
           again. */
    
        if (WIFSTOPPED(status)) child_stopped = 1;
    
        /* Relay wait status to pipe, then loop back. */
    
        if (write(FORKSRV_FD + 1, &status, 4) != 4) _exit(1);
    
      }
    
    }
    

首先设置child_stopped为0.

向通信描述符`FORKSRV_FD + 1`中写入数据,实质上这里存储的是后面fork server的状态.

然后开始循环

从`FORKSRV_FD`中阻塞读取,读取到数据继续向下执行.

这里的`FORKSRV_FD`和`FORKSRV_FD + 1`在afl-fuzz.c的init_forkserver函数进行了初始化,将st_pipe和ctl_pipe两个管道分别复制给了`FORKSRV_FD`和`FORKSRV_FD
+ 1`.

`FORKSRV_FD`是用于控制fork server的通信管道.

`FORKSRV_FD + 1`内写入了一些fork server的状态信息,afl-fuzz.c内会进行读取.

这两个管道的作用会在afl-fuzz.c中体现.

判断`child_stopped`和`was_killed`不为0,这两个值表示子进程是否停止和子进程是否被杀死.

如果为true,则表示子进程已经停止,并且之前被杀死,然后将`child_stopped`复位为0,并等待子进程退出状态.

继续判断`child_stopped`状态.

如果为0,则fork一个子进程,进行fuzz,释放当前管道资源,return.

如果为1,这是persistent mode的特殊处理,此时子进程处于暂停状态,通过`kill(child_pid, SIGCONT);`函数对
子进程进行重启.然后将`child_stopped`复位为0.

向`FORKSRV_FD + 1`中写入子进程id,然后等待子进程结束.

对`persistent
mode`下进行特殊处理,该模式下,子进程会通过sigstop自行停止指示运行成功,这种情况下需要唤醒它进行fuzz,所以将child_stopped状态更改为1,会执行到之前的步骤,继续运行.

将状态写入至`FORKSRV_FD + 1`至,继续循环.

#### 2.persistent mode

`persistent
mode`模式在单个进程中通过测试用例进行fuzz,通过使用一些不影响上下文状态的api,和处理输入文件进行fuzz时,进行状态的重置,可以重用一个进程进行持续的fuzz,不需要fork新的进程,节省了资源的开销,提高了效率.

使用方式是通过下面的宏.

需要读取测试用例,调用目标模块,然后恢复一些状态,这些代码都要自己实现.

    
    
    while (__AFL_LOOP(1000)) {
      /* Read input data. */
      /* Call library code to be fuzzed. */
      /* Reset state. */
    }
    /* Exit normally */
    

这种模式之前在一篇adobe漏洞挖掘的文章里见到过,使用该模式挖掘Jp2k类型图片的解析模块,挖掘者逆向了adobe解析jp2k图片的一个最底层的函数,逆向了该函数的参数,然后进行模拟构造,再进行调用,最大限度的提高效率,挖出了大量漏洞.

在afl-fuzz的文档说明循环次数最好为1000,目的是减少内存泄漏和一些其他问题带来的影响.

    
    
    cc_params[cc_par_cnt++] = "-D__AFL_LOOP(_A)="
                                  "({ static volatile char *_B __attribute__((used)); "
                                  " _B = (char*)\"" PERSIST_SIG "\"; "
                                  #ifdef __APPLE__
                                  "__attribute__((visibility(\"default\"))) "
        "int _L(unsigned int) __asm__(\"___afl_persistent_loop\"); "
                                  #else
                                  "__attribute__((visibility(\"default\"))) "
                                  "int _L(unsigned int) __asm__(\"__afl_persistent_loop\"); "
                                  #endif /* ^__APPLE__ */
                                  "_L(_A); })";
    

这里`__AFL_LOOP(_A)`对应的函数是`__afl_persistent_loop`

    
    
    int __afl_persistent_loop(unsigned int max_cnt) {
    
      static u8  first_pass = 1;
      static u32 cycle_cnt;
    
      if (first_pass) {
    
        /* Make sure that every iteration of __AFL_LOOP() starts with a clean slate.
           On subsequent calls, the parent will take care of that, but on the first
           iteration, it's our job to erase any trace of whatever happened
           before the loop. */
    
        if (is_persistent) {
    
          memset(__afl_area_ptr, 0, MAP_SIZE);
          __afl_area_ptr[0] = 1;
          __afl_prev_loc = 0;
        }
    
        cycle_cnt  = max_cnt;
        first_pass = 0;
        return 1;
    
      }
    
      if (is_persistent) {
    
        if (--cycle_cnt) {
    
          raise(SIGSTOP);
    
          __afl_area_ptr[0] = 1;
          __afl_prev_loc = 0;
    
          return 1;
    
        } else {
    
          /* When exiting __AFL_LOOP(), make sure that the subsequent code that
             follows the loop is not traced. We do that by pivoting back to the
             dummy output region. */
    
          __afl_area_ptr = __afl_area_initial;
    
        }
    
      }
    
      return 0;
    
    }
    

这块代码需要结合之前的代码整体看下,

执行顺序是`afl_auto_init->__afl_manual_init->__afl_start_forkserver->__afl_persistent_loop`

初始化共享内存,然后进行fork server

然后执行到这个函数`__afl_persistent_loop`:

函数参数是`max_cnt`,最大循环次数.

首先定义了两个变量

`first_pass`初始化为1,表示是否为第一次执行.

`cycle_cnt`表示剩余循环次数.

如果是第一次执行会,清空`__afl_area_ptr`,`__afl_area_ptr[0]`设置为1,然后将`__afl_prev_loc`设置为0.

然后将初始化`cycle_cnt`设置为最大循环次数.first_pass修改为0,return 1.

如果不是第一次执行.

判断`is_persistent`当前是否为`persistent mode`,不是return 0.

然后`cycle_cnt`减1,判断剩余次数是否为0.

如果不为0,则通过`raise(SIGSTOP)`,让当前进程暂停,`__afl_area_ptr[0]`设置为1,然后将`__afl_prev_loc`设置为0.return
1.此时在fork server会设置child_stopped标志位,然后再下次时,会恢复之前的子进程执行.

如果为0,则将`__afl_area_ptr`指向`__afl_area_initial`,它是空的.

## 5.af-fuzz

