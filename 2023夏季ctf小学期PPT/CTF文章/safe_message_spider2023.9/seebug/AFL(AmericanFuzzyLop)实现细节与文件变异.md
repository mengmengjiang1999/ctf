作者：[rk700](https://rk700.github.io/)

## Part 1：AFL内部实现细节小记

AFL(American Fuzzy Lop)是一款开源的fuzzing工具。最近我对其代码进行了简要的阅读，大致总结了一些AFL的实现细节，在此记录整理。

#### 代码插桩

使用AFL，首先需要通过afl-gcc/afl-clang等工具来编译目标，在这个过程中会对其进行插桩。

我们以afl-gcc为例。如果阅读文件afl-gcc.c便可以发现，其本质上只是一个gcc的wrapper。我们不妨添加一些输出，从而在调用`execvp()`之前打印全部命令行参数，看看afl-gcc所执行的究竟是什么：

    
    
    gcc /tmp/hello.c -B /root/src/afl-2.52b -g -O3 -funroll-loops -D__AFL_COMPILER=1 -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION=1

可以看到，`afl-gcc`最终调用`gcc`，并定义了一些宏，设置了一些参数。其中最关键的就是`-B
/root/src/afl-2.52b`这条。根据`gcc
--help`可知，`-B`选项用于设置编译器的搜索路径，这里便是设置成`/root/src/afl-2.52b`(是我设置的环境变量`AFL_PATH`的值，即AFL目录，因为我没有make
install)。

如果了解编译过程，那么就知道把源代码编译成二进制，主要是经过”源代码”->”汇编代码”->”二进制”这样的过程。而将汇编代码编译成为二进制的工具，即为汇编器assembler。Linux系统下的常用汇编器是`as`。不过，编译完成AFL后，在其目录下也会存在一个`as`文件，并作为符号链接指向`afl-as`。所以，如果通过`-B`选项为gcc设置了搜索路径，那么`afl-as`便会作为汇编器，执行实际的汇编操作。

所以，AFL的代码插桩，就是在将源文件编译为汇编代码后，通过`afl-as`完成。

接下来，我们继续阅读文件afl-as.c。其大致逻辑是处理汇编代码，在分支处插入桩代码，并最终再调用`as`进行真正的汇编。具体插入代码的部分如下：

    
    
    fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32, R(MAP_SIZE));

这里通过`fprintf()`将格式化字符串添加到汇编文件的相应位置。篇幅所限，我们只分析32位的情况，`trampoline_fmt_32`的具体内容如下：

    
    
    static const u8* trampoline_fmt_32 =
    
      "\n"
      "/* --- AFL TRAMPOLINE (32-BIT) --- */\n"
      "\n"
      ".align 4\n"
      "\n"
      "leal -16(%%esp), %%esp\n"
      "movl %%edi, 0(%%esp)\n"
      "movl %%edx, 4(%%esp)\n"
      "movl %%ecx, 8(%%esp)\n"
      "movl %%eax, 12(%%esp)\n"
      "movl $0x%08x, %%ecx\n"
      "call __afl_maybe_log\n"
      "movl 12(%%esp), %%eax\n"
      "movl 8(%%esp), %%ecx\n"
      "movl 4(%%esp), %%edx\n"
      "movl 0(%%esp), %%edi\n"
      "leal 16(%%esp), %%esp\n"
      "\n"
      "/* --- END --- */\n"
      "\n";

这一段汇编代码，主要的操作是：

  * 保存`edi`等寄存器
  * 将`ecx`的值设置为`fprintf()`所要打印的变量内容
  * 调用方法`__afl_maybe_log()`
  * 恢复寄存器

`__afl_maybe_log`作为插桩代码所执行的实际内容，会在接下来详细展开，这里我们只分析`"movl $0x%08x,
%%ecx\n"`这条指令。

回到`fprintf()`命令：

    
    
    fprintf(outf, use_64bit ? trampoline_fmt_64 : trampoline_fmt_32, R(MAP_SIZE));

可知`R(MAP_SIZE)`即为上述指令将`ecx`设置的值，即为。根据定义，宏`MAP_SIZE`为64K，我们在下文中还会看到他；`R(x)`的定义是`(random()
% (x))`，所以`R(MAP_SIZE)`即为0到MAP_SIZE之间的一个随机数。

因此，在处理到某个分支，需要插入桩代码时，`afl-as`会生成一个随机数，作为运行时保存在`ecx`中的值。而这个随机数，便是用于标识这个代码块的key。在后面我们会详细介绍这个key是如何被使用的。

#### fork server

编译target完成后，就可以通过`afl-fuzz`开始fuzzing了。其大致思路是，对输入的seed文件不断地变化，并将这些mutated
input喂给target执行，检查是否会造成崩溃。因此，fuzzing涉及到大量的fork和执行target的过程。

为了更高效地进行上述过程，AFL实现了一套fork server机制。其基本思路是：启动target进程后，target会运行一个fork
server；fuzzer并不负责fork子进程，而是与这个fork server通信，并由fork
server来完成fork及继续执行目标的操作。这样设计的最大好处，就是不需要调用`execve()`，从而节省了载入目标文件和库、解析符号地址等重复性工作。如果熟悉Android的话，可以将fork
server类比为zygote。

接下来，我们来看看fork
server的具体运行原理。首先，fuzzer执行`fork()`得到父进程和子进程，这里的父进程仍然为fuzzer，子进程则为target进程，即将来的fork
server。

    
    
    forksrv_pid = fork();

而父子进程之间，是通过管道进行通信。具体使用了2个管道，一个用于传递状态，另一个用于传递命令：

    
    
    int st_pipe[2], ctl_pipe[2];

对于子进程（fork server），会进行一系列设置，其中包括将上述两个管道分配到预先指定的fd，并最终执行target：

    
    
      if (!forksrv_pid) {
    ...
        if (dup2(ctl_pipe[0], FORKSRV_FD) < 0) PFATAL("dup2() failed");
        if (dup2(st_pipe[1], FORKSRV_FD + 1) < 0) PFATAL("dup2() failed");
    ...
        execv(target_path, argv);

对于父进程（fuzzer），则会读取状态管道的信息，如果一切正常，则说明fork server创建完成。

    
    
      fsrv_st_fd  = st_pipe[0];
    ...
      rlen = read(fsrv_st_fd, &status, 4);
    ...
      /* If we have a four-byte "hello" message from the server, we're all set.
    Otherwise, try to figure out what went wrong. */
    
      if (rlen == 4) {
        OKF("All right - fork server is up.");
        return;
      }

接下来，我们来分析fork server是如何与fuzzer通信的。

fork server侧的具体操作，也是在之前提到的方法`__afl_maybe_log()`中。首先，通过写入状态管道，fork
server会通知fuzzer，其已经准备完毕，可以开始fork了，而这正是上面提到的父进程等待的信息：

    
    
      "__afl_forkserver:\n"
      "\n"
      " /* Enter the fork server mode to avoid the overhead of execve() calls. */\n"
      "\n"
      " pushl %eax\n"
      " pushl %ecx\n"
      " pushl %edx\n"
      "\n"
      " /* Phone home and tell the parent that we're OK. (Note that signals with\n"
      " no SA_RESTART will mess it up). If this fails, assume that the fd is\n"
      " closed because we were execve()d from an instrumented binary, or because\n"
      " the parent doesn't want to use the fork server. */\n"
      "\n"
      " pushl $4 /* length */\n"
      " pushl $__afl_temp /* data */\n"
      " pushl $" STRINGIFY((FORKSRV_FD + 1)) " /* file desc */\n"
      " call write\n"
      " addl $12, %esp\n"
      "\n"
      " cmpl $4, %eax\n"
      " jne __afl_fork_resume\n"

接下来，fork server进入等待状态`__afl_fork_wait_loop`，读取命令管道，直到fuzzer通知其开始fork：

    
    
      "__afl_fork_wait_loop:\n"
      "\n"
      " /* Wait for parent by reading from the pipe. Abort if read fails. */\n"
      "\n"
      " pushl $4 /* length */\n"
      " pushl $__afl_temp /* data */\n"
      " pushl $" STRINGIFY(FORKSRV_FD) " /* file desc */\n"
      " call read\n"

一旦fork server接收到fuzzer的信息，便调用`fork()`，得到父进程和子进程：

    
    
      " call fork\n"
      "\n"
      " cmpl $0, %eax\n"
      " jl __afl_die\n"
      " je __afl_fork_resume\n"

子进程是实际执行target的进程，其跳转到`__afl_fork_resume`。在这里会关闭不再需要的管道，并继续执行：

    
    
      "__afl_fork_resume:\n"
      "\n"
      " /* In child process: close fds, resume execution. */\n"
      "\n"
      " pushl $" STRINGIFY(FORKSRV_FD) "\n"
      " call close\n"
      "\n"
      " pushl $" STRINGIFY((FORKSRV_FD + 1)) "\n"
      " call close\n"
      "\n"
      " addl $8, %esp\n"
      "\n"
      " popl %edx\n"
      " popl %ecx\n"
      " popl %eax\n"
      " jmp __afl_store\n"

父进程则仍然作为fork
server运行，其会将子进程的pid通过状态管道发送给fuzzer，并等待子进程执行完毕；一旦子进程执行完毕，则再通过状态管道，将其结束状态发送给fuzzer；之后再次进入等待状态`__afl_fork_wait_loop`：

    
    
      " /* In parent process: write PID to pipe, then wait for child. */\n"
      "\n"
      " movl %eax, __afl_fork_pid\n"
      "\n"
      " pushl $4 /* length */\n"
      " pushl $__afl_fork_pid /* data */\n"
      " pushl $" STRINGIFY((FORKSRV_FD + 1)) " /* file desc */\n"
      " call write\n"
      " addl $12, %esp\n"
      "\n"
      " pushl $0 /* no flags */\n"
      " pushl $__afl_temp /* status */\n"
      " pushl __afl_fork_pid /* PID */\n"
      " call waitpid\n"
      " addl $12, %esp\n"
      "\n"
      " cmpl $0, %eax\n"
      " jle __afl_die\n"
      "\n"
      " /* Relay wait status to pipe, then loop back. */\n"
      "\n"
      " pushl $4 /* length */\n"
      " pushl $__afl_temp /* data */\n"
      " pushl $" STRINGIFY((FORKSRV_FD + 1)) " /* file desc */\n"
      " call write\n"
      " addl $12, %esp\n"
      "\n"
      " jmp __afl_fork_wait_loop\n"

以上就是fork server的主要逻辑，现在我们再回到fuzzer侧。在fork
server启动完成后，一旦需要执行某个测试用例，则fuzzer会调用`run_target()`方法。在此方法中，便是通过命令管道，通知fork
server准备fork；并通过状态管道，获取子进程pid：

    
    
        s32 res;
    
        /* In non-dumb mode, we have the fork server up and running, so simply
    tell it to have at it, and then read back PID. */
    
        if ((res = write(fsrv_ctl_fd, &prev_timed_out, 4)) != 4) {
    ...
        if ((res = read(fsrv_st_fd, &child_pid, 4)) != 4) {
    ...

随后，fuzzer再次读取状态管道，获取子进程退出状态，并由此来判断子进程结束的原因，例如正常退出、超时、崩溃等，并进行相应的记录。

    
    
        if ((res = read(fsrv_st_fd, &status, 4)) != 4) {
    ...
      /* Report outcome to caller. */
    
      if (WIFSIGNALED(status) && !stop_soon) {
    
        kill_signal = WTERMSIG(status);
    
        if (child_timed_out && kill_signal == SIGKILL) return FAULT_TMOUT;
    
        return FAULT_CRASH;
    
      }

#### 共享内存

作为fuzzer，AFL并不是像无头苍蝇那样对输入文件无脑地随机变化（其实也支持这种方式，即dumb模式），其最大特点就是会对target进行插桩，以辅助mutated
input的生成。具体地，插桩后的target，会记录执行过程中的分支信息；随后，fuzzer便可以根据这些信息，判断这次执行的整体流程和代码覆盖情况。

AFL使用共享内存，来完成以上信息在fuzzer和target之间的传递。具体地，fuzzer在启动时，会执行`setup_shm()`方法进行配置。其首先调用`shemget()`分配一块共享内存，大小`MAP_SIZE`为64K:

    
    
    shm_id = shmget(IPC_PRIVATE, MAP_SIZE, IPC_CREAT | IPC_EXCL | 0600);

分配成功后，该共享内存的标志符会被设置到环境变量中，从而之后fork()得到的子进程可以通过该环境变量，得到这块共享内存的标志符：

    
    
    shm_str = alloc_printf("%d", shm_id);
    if (!dumb_mode) setenv(SHM_ENV_VAR, shm_str, 1);

并且，fuzzer本身，会使用变量`trace_bits`来保存共享内存的地址：

    
    
    trace_bits = shmat(shm_id, NULL, 0);

在每次target执行之前，fuzzer首先将该共享内容清零：

    
    
    memset(trace_bits, 0, MAP_SIZE); 

接下来，我们再来看看target是如何获取并使用这块共享内存的。相关代码同样也在上面提到的方法`__afl_maybe_log()`中。首先，会检查是否已经将共享内存映射完成：

    
    
      " /* Check if SHM region is already mapped. */\n"
      "\n"
      " movl __afl_area_ptr, %edx\n"
      " testl %edx, %edx\n"
      " je __afl_setup\n"

`__afl_area_ptr`中保存的就是共享内存映射到target的内存空间中的地址，如果其不是NULL，便保存在ebx中继续执行；否则进一步跳转到`__afl_setup`。

`__afl_setup`处会做一些错误检查，然后获取环境变量`AFL_SHM_ENV`的内容并将其转为整型。查看其定义便可知，这里获取到的，便是之前fuzzer保存的共享内存的标志符。

    
    
      "__afl_setup:\n"
      "\n"
      " /* Do not retry setup if we had previous failures. */\n"
      "\n"
      " cmpb $0, __afl_setup_failure\n"
      " jne __afl_return\n"
      "\n"
      " /* Map SHM, jumping to __afl_setup_abort if something goes wrong.\n"
      " We do not save FPU/MMX/SSE registers here, but hopefully, nobody\n"
      " will notice this early in the game. */\n"
      "\n"
      " pushl %eax\n"
      " pushl %ecx\n"
      "\n"
      " pushl $.AFL_SHM_ENV\n"
      " call getenv\n"
      " addl $4, %esp\n"
      "\n"
      " testl %eax, %eax\n"
      " je __afl_setup_abort\n"
      "\n"
      " pushl %eax\n"
      " call atoi\n"
      " addl $4, %esp\n"

最后，通过调用`shmat()`，target将这块共享内存也映射到了自己的内存空间中，并将其地址保存在`__afl_area_ptr`及`edx`中。由此，便完成了fuzzer与target之间共享内存的设置。

    
    
      " pushl $0 /* shmat flags */\n"
      " pushl $0 /* requested addr */\n"
      " pushl %eax /* SHM ID */\n"
      " call shmat\n"
      " addl $12, %esp\n"
      "\n"
      " cmpl $-1, %eax\n"
      " je __afl_setup_abort\n"
      "\n"
      " /* Store the address of the SHM region. */\n"
      "\n"
      " movl %eax, __afl_area_ptr\n"
      " movl %eax, %edx\n"
      "\n"
      " popl %ecx\n"
      " popl %eax\n"

注记：如果使用了fork server模式，那么上述获取共享内存的操作，是在fork
server中进行；随后fork出来的子进程，只需直接使用这个共享内存即可。

#### 分支信息的记录

现在，用于通信的共享内存已准备完毕，接下来我们看看具体通信的是什么。

由官网文档可知，AFL是根据二元tuple(跳转的源地址和目标地址)来记录分支信息，从而获取target的执行流程和代码覆盖情况，其伪代码如下：

    
    
    cur_location = <COMPILE_TIME_RANDOM>;
    shared_mem[cur_location ^ prev_location]++; 
    prev_location = cur_location >> 1;

我们再回到方法`__afl_maybe_log()`中。上面提到，在target完成准备工作后，共享内存的地址被保存在寄存器`edx`中。随后执行以下代码：

    
    
      "__afl_store:\n"
      "\n"
      " /* Calculate and store hit for the code location specified in ecx. There\n"
      " is a double-XOR way of doing this without tainting another register,\n"
      " and we use it on 64-bit systems; but it's slower for 32-bit ones. */\n"
      "\n"
    #ifndef COVERAGE_ONLY
    
      " movl __afl_prev_loc, %edi\n"
      " xorl %ecx, %edi\n"
      " shrl $1, %ecx\n"
      " movl %ecx, __afl_prev_loc\n"
    #else
    
      " movl %ecx, %edi\n"
    #endif /* ^!COVERAGE_ONLY */
    
      "\n"
    #ifdef SKIP_COUNTS
    
      " orb $1, (%edx, %edi, 1)\n"
    #else
    
      " incb (%edx, %edi, 1)\n"

这里对应的便正是文档中的伪代码。具体地，变量`__afl_prev_loc`保存的是前一次跳转的”位置”，其值与`ecx`做异或后，保存在`edi`中，并以`edx`（共享内存）为基址，对`edi`下标处进行加一操作。而`ecx`的值右移1位后，保存在了变量`__afl_prev_loc`中。

那么，这里的`ecx`，保存的应该就是伪代码中的`cur_location`了。回忆之前介绍代码插桩的部分：

    
    
    static const u8* trampoline_fmt_32 = 
    ...
      "movl $0x%08x, %%ecx\n"
      "call __afl_maybe_log\n"

在每个插桩处，afl-as会添加相应指令，将`ecx`的值设为0到MAP_SIZE之间的某个随机数，从而实现了伪代码中的`cur_location =
<COMPILE_TIME_RANDOM>;`。

因此，AFL为每个代码块生成一个随机数，作为其“位置”的记录；随后，对分支处的”源位置“和”目标位置“进行异或，并将异或的结果作为该分支的key，保存每个分支的执行次数。用于保存执行次数的实际上是一个哈希表，大小为`MAP_SIZE=64K`，当然会存在碰撞的问题；但根据AFL文档中的介绍，对于不是很复杂的目标，碰撞概率还是可以接受的：

    
    
       Branch cnt | Colliding tuples | Example targets
      ------------+------------------+-----------------            1,000 | 0.75%            | giflib, lzo
            2,000 | 1.5%             | zlib, tar, xz
            5,000 | 3.5%             | libpng, libwebp
           10,000 | 7%               | libxml
           20,000 | 14%              | sqlite
           50,000 | 30%              | -
如果一个目标过于复杂，那么AFL状态面板中的map_density信息就会有相应的提示：

    
    
    ┬─ map coverage ─┴───────────────────────┤
    │    map density : 3.61% / 14.13%        │
    │ count coverage : 6.35 bits/tuple       │
    ┼─ findings in depth ────────────────────┤

这里的map
density，就是这张哈希表的密度。可以看到，上面示例中，该次执行的哈希表密度仅为3.61%，即整个哈希表差不多有95%的地方还是空的，所以碰撞的概率很小。不过，如果目标很复杂，map
density很大，那么就需要考虑到碰撞的影响了。此种情况下的具体处理方式可见官方文档。

另外，比较有意思的是，AFL需要将`cur_location`右移1位后，再保存到`prev_location`中。官方文档中解释了这样做的原因。假设target中存在`A->A`和`B->B`这样两个跳转，如果不右移，那么这两个分支对应的异或后的key都是0，从而无法区分；另一个例子是`A->B`和`B->A`，如果不右移，这两个分支对应的异或后的key也是相同的。

由上述分析可知，之前提到的共享内存，被用于保存一张哈希表，target在这张表中记录每个分支的执行数量。随后，当target执行结束后，fuzzer便开始对这张表进行分析，从而判断代码的执行情况。

#### 分支信息的分析

首先，fuzzer对`trace_bits`（共享内存）进行预处理：

    
    
    classify_counts((u32*)trace_bits);

具体地，target是将每个分支的执行次数用1个byte来储存，而fuzzer则进一步把这个执行次数归入以下的buckets中：

    
    
    static const u8 count_class_lookup8[256] = {
    
      [0]           = 0, 
      [1]           = 1, 
      [2]           = 2, 
      [3]           = 4, 
      [4 ... 7]     = 8, 
      [8 ... 15]    = 16,
      [16 ... 31]   = 32,
      [32 ... 127]  = 64,
      [128 ... 255] = 128
    
    };

举个例子，如果某分支执行了1次，那么落入第2个bucket，其计数byte仍为1；如果某分支执行了4次，那么落入第5个bucket，其计数byte将变为8，等等。

这样处理之后，对分支执行次数就会有一个简单的归类。例如，如果对某个测试用例处理时，分支A执行了32次；对另外一个测试用例，分支A执行了33次，那么AFL就会认为这两次的代码覆盖是相同的。当然，这样的简单分类肯定不能区分所有的情况，不过在某种程度上，处理了一些因为循环次数的微小区别，而误判为不同执行结果的情况。

随后，对于某些mutated
input来说，如果这次执行没有出现崩溃等异常输出，fuzzer还会检查其是否新增了执行路径。具体来说，是对`trace_bits`计算hash并来实现：

    
    
    u32 cksum = hash32(trace_bits, MAP_SIZE, HASH_CONST);

通过比较hash值，就可以判断trace_bits是否发生了变化，从而判断此次mutated
input是否带来了新路径，为之后的fuzzing提供参考信息。

#### 总结

以上便是对AFL内部细节的一些分析整理，其实还有很多地方值得进一步深入去研究，例如AFL是如何判断一条路径是否是favorite的、如何对seed文件进行变化，等等。如果只是使用AFL进行简单的fuzzing，那么这些细节其实不需要掌握太多；但是如果需要在AFL的基础上进一步针对特定目标进行优化，那么了解AFL的内部工作原理就是必须的了。

## Part 2：AFL文件变异一览

[上一部分](https://rk700.github.io/2017/12/28/afl-internals/)主要对AFL的一些实现细节进行了分析，但正如最后所说，还有很多细节讲到。所以我又另外写了这篇，专门介绍AFL是如何对输入文件进行变异的。

总的来讲，AFL维护了一个队列(queue)，每次从这个队列中取出一个文件，对其进行大量变异，并检查运行后是否会引起目标崩溃、发现新路径等结果。变异的主要类型如下：

  * bitflip，按位翻转，1变为0，0变为1
  * arithmetic，整数加/减算术运算
  * interest，把一些特殊内容替换到原文件中
  * dictionary，把自动生成或用户提供的token替换/插入到原文件中
  * havoc，中文意思是“大破坏”，此阶段会对原文件进行大量变异，具体见下文
  * splice，中文意思是“绞接”，此阶段会将两个文件拼接起来得到一个新的文件

其中，前四项bitflip, arithmetic, interest, dictionary是非dumb
mode（`-d`）和主fuzzer（`-M`）会进行的操作，由于其变异方式没有随机性，所以也称为deterministic
fuzzing；havoc和splice则存在随机性，是所有状况的fuzzer（是否dumb mode、主从fuzzer）都会执行的变异。

以下将对这些变异类型进行具体介绍。

#### bitflip

拿到一个原始文件，打头阵的就是bitflip，而且还会根据翻转量/步长进行多种不同的翻转，按照顺序依次为：

  * bitflip 1/1，每次翻转 **1** 个bit，按照每 **1** 个bit的步长从头开始
  * bitflip 2/1，每次翻转相邻的 **2** 个bit，按照每 **1** 个bit的步长从头开始
  * bitflip 4/1，每次翻转相邻的 **4** 个bit，按照每 **1** 个bit的步长从头开始
  * bitflip 8/8，每次翻转相邻的 **8** 个bit，按照每 **8** 个bit的步长从头开始，即依次对每个byte做翻转
  * bitflip 16/8，每次翻转相邻的 **16** 个bit，按照每 **8** 个bit的步长从头开始，即依次对每个word做翻转
  * bitflip 32/8，每次翻转相邻的 **32** 个bit，按照每 **8** 个bit的步长从头开始，即依次对每个dword做翻转

作为精妙构思的fuzzer，AFL不会放过每一个获取文件信息的机会。这一点在bitflip过程中就体现的淋漓尽致。具体地，在上述过程中，AFL巧妙地嵌入了一些对文件格式的启发式判断。

###### 自动检测token

在进行bitflip 1/1变异时，对于每个byte的最低位(least significant
bit)翻转还进行了额外的处理：如果连续多个bytes的最低位被翻转后，程序的执行路径都未变化，而且与原始执行路径不一致(检测程序执行路径的方式可见上篇文章中[“分支信息的分析”](https://rk700.github.io/2017/12/28/afl-internals/#%E5%88%86%E6%94%AF%E4%BF%A1%E6%81%AF%E7%9A%84%E5%88%86%E6%9E%90)一节)，那么就把这一段连续的bytes判断是一条token。

例如，PNG文件中用`IHDR`作为起始块的标识，那么就会存在类似于以下的内容：

    
    
    ........IHDR........

当翻转到字符`I`的最高位时，因为`IHDR`被破坏，此时程序的执行路径肯定与处理正常文件的路径是不同的；随后，在翻转接下来3个字符的最高位时，`IHDR`标识同样被破坏，程序应该会采取同样的执行路径。由此，AFL就判断得到一个可能的token：`IHDR`，并将其记录下来为后面的变异提供备选。

AFL采取的这种方式是非常巧妙的：就本质而言，这实际上是对每个byte进行修改并检查执行路径；但集成到bitflip后，就不需要再浪费额外的执行资源了。此外，为了控制这样自动生成的token的大小和数量，AFL还在`config.h`中通过宏定义了限制：

    
    
    /* Length limits for auto-detected dictionary tokens: */
    
    #define MIN_AUTO_EXTRA      3
    #define MAX_AUTO_EXTRA      32
    
    /* Maximum number of auto-extracted dictionary tokens to actually use in fuzzing
       (first value), and to keep in memory as candidates. The latter should be much
       higher than the former. */
    
    #define USE_AUTO_EXTRAS     10
    
    #define MAX_AUTO_EXTRAS     (USE_AUTO_EXTRAS * 10)

对于一些文件来说，我们已知其格式中出现的token长度不会超过4，那么我们就可以修改`MAX_AUTO_EXTRA`为4并重新编译AFL，以排除一些明显不会是token的情况。遗憾的是，这些设置是通过宏定义来实现，所以不能做到运行时指定，每次修改后必须重新编译AFL。

###### 生成effector map

在进行bitflip 8/8变异时，AFL还生成了一个非常重要的信息：effector map。这个effector
map几乎贯穿了整个deterministic fuzzing的始终。

具体地，在对每个byte进行翻转时，如果其造成执行路径与原始路径不一致，就将该byte在effector
map中标记为1，即“有效”的，否则标记为0，即“无效”的。

这样做的逻辑是：如果一个byte完全翻转，都无法带来执行路径的变化，那么这个byte很有可能是属于"data"，而非"metadata"（例如size,
flag等），对整个fuzzing的意义不大。所以，在随后的一些变异中，会参考effector map，跳过那些“无效”的byte，从而节省了执行资源。

由此，通过极小的开销（没有增加额外的执行次数），AFL又一次对文件格式进行了启发式的判断。看到这里，不得不叹服于AFL实现上的精妙。

不过，在某些情况下并不会检测有效字符。第一种情况就是dumb mode或者从fuzzer，此时文件所有的字符都有可能被变异。第二、第三种情况与文件本身有关：

    
    
    /* Minimum input file length at which the effector logic kicks in: */
    
    #define EFF_MIN_LEN         128
    
    /* Maximum effector density past which everything is just fuzzed
       unconditionally (%): */
    
    #define EFF_MAX_PERC        90

即默认情况下，如果文件小于128
bytes，那么所有字符都是“有效”的；同样地，如果AFL发现一个文件有超过90%的bytes都是“有效”的，那么也不差那10%了，大笔一挥，干脆把所有字符都划归为“有效”。

#### arithmetic

在bitflip变异全部进行完成后，便进入下一个阶段：arithmetic。与bitflip类似的是，arithmetic根据目标大小的不同，也分为了多个子阶段：

  * arith 8/8，每次对 **8** 个bit进行加减运算，按照每 **8** 个bit的步长从头开始，即对文件的每个byte进行整数加减变异
  * arith 16/8，每次对 **16** 个bit进行加减运算，按照每 **8** 个bit的步长从头开始，即对文件的每个word进行整数加减变异
  * arith 32/8，每次对 **32** 个bit进行加减运算，按照每 **8** 个bit的步长从头开始，即对文件的每个dword进行整数加减变异

加减变异的上限，在`config.h`中的宏`ARITH_MAX`定义，默认为35。所以，对目标整数会进行+1, +2, ..., +35, -1, -2,
..., -35的变异。特别地，由于整数存在大端序和小端序两种表示方式，AFL会贴心地对这两种整数表示方式都进行变异。

此外，AFL还会智能地跳过某些arithmetic变异。第一种情况就是前面提到的effector
map：如果一个整数的所有bytes都被判断为“无效”，那么就跳过对整数的变异。第二种情况是之前bitflip已经生成过的变异：如果加/减某个数后，其效果与之前的某种bitflip相同，那么这次变异肯定在上一个阶段已经执行过了，此次便不会再执行。

#### interest

下一个阶段是interest，具体可分为：

  * interest 8/8，每次对 **8** 个bit进替换，按照每 **8** 个bit的步长从头开始，即对文件的每个byte进行替换
  * interest 16/8，每次对 **16** 个bit进替换，按照每 **8** 个bit的步长从头开始，即对文件的每个word进行替换
  * interest 32/8，每次对 **32** 个bit进替换，按照每 **8** 个bit的步长从头开始，即对文件的每个dword进行替换

而用于替换的"interesting values"，是AFL预设的一些比较特殊的数：

    
    
    static s8  interesting_8[]  = { INTERESTING_8 };
    static s16 interesting_16[] = { INTERESTING_8, INTERESTING_16 };
    static s32 interesting_32[] = { INTERESTING_8, INTERESTING_16, INTERESTING_32 };

这些数的定义在`config.h`文件中：

    
    
    /* List of interesting values to use in fuzzing. */
    
    #define INTERESTING_8 \
      -128,          /* Overflow signed 8-bit when decremented  */ \
      -1,            /*                                         */ \
       0,            /*                                         */ \
       1,            /*                                         */ \
       16,           /* One-off with common buffer size         */ \
       32,           /* One-off with common buffer size         */ \
       64,           /* One-off with common buffer size         */ \
       100,          /* One-off with common buffer size         */ \
       127           /* Overflow signed 8-bit when incremented  */
    
    #define INTERESTING_16 \
      -32768,        /* Overflow signed 16-bit when decremented */ \
      -129,          /* Overflow signed 8-bit                   */ \
       128,          /* Overflow signed 8-bit                   */ \
       255,          /* Overflow unsig 8-bit when incremented   */ \
       256,          /* Overflow unsig 8-bit                    */ \
       512,          /* One-off with common buffer size         */ \
       1000,         /* One-off with common buffer size         */ \
       1024,         /* One-off with common buffer size         */ \
       4096,         /* One-off with common buffer size         */ \
       32767         /* Overflow signed 16-bit when incremented */
    
    #define INTERESTING_32 \
      -2147483648LL, /* Overflow signed 32-bit when decremented */ \
      -100663046,    /* Large negative number (endian-agnostic) */ \
      -32769,        /* Overflow signed 16-bit                  */ \
       32768,        /* Overflow signed 16-bit                  */ \
       65535,        /* Overflow unsig 16-bit when incremented  */ \
       65536,        /* Overflow unsig 16 bit                   */ \
       100663045,    /* Large positive number (endian-agnostic) */ \
       2147483647    /* Overflow signed 32-bit when incremented */

可以看到，用于替换的基本都是可能会造成溢出的数。

与之前类似，effector map仍然会用于判断是否需要变异；此外，如果某个interesting
value，是可以通过bitflip或者arithmetic变异达到，那么这样的重复性变异也是会跳过的。

#### dictionary

进入到这个阶段，就接近deterministic fuzzing的尾声了。具体有以下子阶段：

  * user extras (over)，从头开始，将 **用户提供** 的tokens依次 **替换** 到原文件中
  * user extras (insert)，从头开始，将 **用户提供** 的tokens依次 **插入** 到原文件中
  * auto extras (over)，从头开始，将 **自动检测** 的tokens依次 **替换** 到原文件中

其中，用户提供的tokens，是在词典文件中设置并通过`-x`选项指定的，如果没有则跳过相应的子阶段。

###### user extras (over)

对于用户提供的tokens，AFL先按照长度从小到大进行排序。这样做的好处是，只要按照顺序使用排序后的tokens，那么后面的token不会比之前的短，从而每次覆盖替换后不需要再恢复到原状。

随后，AFL会检查tokens的数量，如果数量大于预设的`MAX_DET_EXTRAS`（默认值为200），那么对每个token会根据概率来决定是否进行替换：

    
    
        for (j = 0; j < extras_cnt; j++) {
    
          /* Skip extras probabilistically if extras_cnt > MAX_DET_EXTRAS. Also
             skip them if there's no room to insert the payload, if the token
             is redundant, or if its entire span has no bytes set in the effector
             map. */
    
          if ((extras_cnt > MAX_DET_EXTRAS && UR(extras_cnt) >= MAX_DET_EXTRAS) ||
              extras[j].len > len - i ||
              !memcmp(extras[j].data, out_buf + i, extras[j].len) ||
              !memchr(eff_map + EFF_APOS(i), 1, EFF_SPAN_ALEN(i, extras[j].len))) {
    
            stage_max--;
            continue;
    
          }

这里的`UR(extras_cnt)`是运行时生成的一个`0`到`extras_cnt`之间的随机数。所以，如果用户词典中一共有400个tokens，那么每个token就有`200/400=50%`的概率执行替换变异。我们可以修改`MAX_DET_EXTRAS`的大小来调整这一概率。

由上述代码也可以看到，effector map在这里同样被使用了：如果要替换的目标bytes全部是“无效”的，那么就跳过这一段，对下一段目标执行替换。

###### user extras (insert)

这一子阶段是对用户提供的tokens执行插入变异。不过与上一个子阶段不同的是，此时并没有对tokens数量的限制，所以全部tokens都会从原文件的第1个byte开始，依次向后插入；此外，由于原文件并未发生替换，所以effector
map不会被使用。

这一子阶段最特别的地方，就是变异不能简单地恢复。之前每次变异完，在变异位置处简单取逆即可，例如bitflip后，再进行一次同样的bitflip就恢复为原文件。正因为如此，之前的变异总体运算量并不大。

但是，对于 **插入**
这种变异方式，恢复起来则复杂的多，所以AFL采取的方式是：将原文件分割为插入前和插入后的部分，再加上插入的内容，将这3部分依次复制到目标缓冲区中（当然这里还有一些小的优化，具体可阅读代码）。而对每个token的每处插入，都需要进行上述过程。所以，如果用户提供了大量tokens，或者原文件很大，那么这一阶段的运算量就会非常的多。直观表现上，就是AFL的执行状态栏中，"user
extras (insert)"的总执行量很大，执行时间很长。如果出现了这种情况，那么就可以考虑适当删减一些tokens。

###### auto extras (over)

这一项与"user extras
(over)"很类似，区别在于，这里的tokens是最开始bitflip阶段自动生成的。另外，自动生成的tokens总量会由`USE_AUTO_EXTRAS`限制（默认为10）。

#### havoc

对于非dumb mode的主fuzzer来说，完成了上述deterministic fuzzing后，便进入了充满随机性的这一阶段；对于dumb
mode或者从fuzzer来说，则是直接从这一阶段开始。

havoc，顾名思义，是充满了各种随机生成的变异，是对原文件的“大破坏”。具体来说，havoc包含了对原文件的多轮变异，每一轮都是将多种方式组合（stacked）而成：

  * 随机选取某个bit进行翻转
  * 随机选取某个byte，将其设置为随机的interesting value
  * 随机选取某个word，并随机选取大、小端序，将其设置为随机的interesting value
  * 随机选取某个dword，并随机选取大、小端序，将其设置为随机的interesting value
  * 随机选取某个byte，对其减去一个随机数
  * 随机选取某个byte，对其加上一个随机数
  * 随机选取某个word，并随机选取大、小端序，对其减去一个随机数
  * 随机选取某个word，并随机选取大、小端序，对其加上一个随机数
  * 随机选取某个dword，并随机选取大、小端序，对其减去一个随机数
  * 随机选取某个dword，并随机选取大、小端序，对其加上一个随机数
  * 随机选取某个byte，将其设置为随机数
  * 随机删除一段bytes
  * 随机选取一个位置，插入一段随机长度的内容，其中75%的概率是插入原文中随机位置的内容，25%的概率是插入一段随机选取的数
  * 随机选取一个位置，替换为一段随机长度的内容，其中75%的概率是替换成原文中随机位置的内容，25%的概率是替换成一段随机选取的数
  * 随机选取一个位置，用随机选取的token（用户提供的或自动生成的）替换
  * 随机选取一个位置，用随机选取的token（用户提供的或自动生成的）插入

怎么样，看完上面这么多的“随机”，有没有觉得晕？还没完，AFL会生成一个随机数，作为变异组合的数量，并根据这个数量，每次从上面那些方式中随机选取一个（可以参考高中数学的有放回摸球），依次作用到文件上。如此这般丧心病狂的变异，原文件就大概率面目全非了，而这么多的随机性，也就成了fuzzing过程中的不可控因素，即所谓的“看天吃饭”了。

#### splice

历经了如此多的考验，文件的变异也进入到了最后的阶段：splice。如其意思所说，splice是将两个seed文件拼接得到新的文件，并对这个新文件继续执行havoc变异。

具体地，AFL在seed文件队列中随机选取一个，与当前的seed文件做对比。如果两者差别不大，就再重新随机选一个；如果两者相差比较明显，那么就随机选取一个位置，将两者都分割为头部和尾部。最后，将当前文件的头部与随机文件的尾部拼接起来，就得到了新的文件。在这里，AFL还会过滤掉拼接文件未发生变化的情况。

#### cycle

于是乎，一个seed文件，在上述的全部变异都执行完成后，就...抱歉，还没结束。

上面的变异完成后，AFL会对文件队列的下一个进行变异处理。当队列中的全部文件都变异测试后，就完成了一个"cycle"，这个就是AFL状态栏右上角的"cycles
done"。而正如cycle的意思所说，整个队列又会从第一个文件开始，再次进行变异，不过与第一次变异不同的是，这一次就不需要再进行deterministic
fuzzing了。

当然，如果用户不停止AFL，那么seed文件将会一遍遍的变异下去。

#### 总结

从以上介绍内容来看，AFL的文件变异，既有看天吃饭的成分，也有随着fuzzing启发式的判断，结合了这么多种方式和巧妙的思路，不愧是大名鼎鼎的AFL。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/496/>

