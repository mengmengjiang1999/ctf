# 命令执行底层原理探究-PHP（四）

阅读量 **864811**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-30 10:30:44

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01065e3f9c22565868.jpg)

## 前言

针对不同平台/语言下的命令执行是不相同的，存在很大的差异性。因此，这里对不同平台/语言下的命令执行函数进行深入的探究分析。

文章开头会对不同平台(Linux、Windows)下：终端的指令执行、语言(PHP、Java、Python)的命令执行进行介绍分析。后面，主要以PHP语言为对象，针对不同平台，对命令执行函数进行底层深入分析，这个过程包括：环境准备、PHP内核源码的编译、运行、调试、审计等，其它语言分析原理思路类似。

该系列分析文章主要分为四部分，如下：

  * 第一部分：命令执行底层原理探究-PHP (一)

针对不同平台(Linux、Windows)下：终端的指令执行、语言(PHP、Java、Python)的命令执行进行介绍分析。

  * 第二部分：命令执行底层原理探究-PHP (二)

主要以PHP语言为对象，针对不同平台，进行环境准备、PHP内核源码的编译、运行、调试等。

  * 第三部分：命令执行底层原理探究-PHP (三)

针对Windows平台下，PHP命令执行函数的底层原理分析。

  * 第四部分：命令执行底层原理探究-PHP (四)

针对Linux平台下，PHP命令执行函数的底层原理分析。

本文 **《 命令执行底层原理探究-PHP (四) 》** 主要讲述的是第四部分：针对Linux平台下，PHP命令执行函数的底层原理分析。

## PHP for Linux

针对Linux平台下：PHP命令执行函数的底层分析。

###  命令执行底层分析

同样，针对命令执行函数的底层分析，这里主要采用两种手段去分析：静态审计(静态审计内核源码)、动态审计(动态调试内核源码)。

####  静态审计

接着`PHP for
Windows->命令执行底层分析->静态审计`部分，里面写到`system、exec、passthru、shell_exec`这类命令执行函数原理相同，底层都调用了相同函数`VCWD_POPEN()`去执行系统指令，`VCWD_POPEN()`函数由`virtual_popen()`函数实现。

同时，`virtual_popen()`函数是作为不同平台的分割点，那么针对Linux平台下的PHP命令执行函数底层实现就可以从这里继续分析。

由于`VCWD_POPEN`函数为`virtual_popen`实现，直接进入`virtual_popen()`函数实现：`Zend\zend_virtual_cwd.c:1831`

    
    
    #ifdef ZEND_WIN32
    CWD_API FILE *virtual_popen(const char *command, const char *type) /* {{{ */
    {
        return popen_ex(command, type, CWDG(cwd).cwd, NULL);
    }
    /* }}} */
    #else /* Unix */
    CWD_API FILE *virtual_popen(const char *command, const char *type) /* {{{ */
    {
        size_t command_length;
        int dir_length, extra = 0;
        char *command_line;
        char *ptr, *dir;
        FILE *retval;
    
        command_length = strlen(command);
    
        dir_length = CWDG(cwd).cwd_length;
        dir = CWDG(cwd).cwd;
        while (dir_length > 0) {
            if (*dir == '\'') extra+=3;
            dir++;
            dir_length--;
        }
        dir_length = CWDG(cwd).cwd_length;
        dir = CWDG(cwd).cwd;
    
        ptr = command_line = (char *) emalloc(command_length + sizeof("cd '' ; ") + dir_length + extra+1+1);
        memcpy(ptr, "cd ", sizeof("cd ")-1);
        ptr += sizeof("cd ")-1;
    
        if (CWDG(cwd).cwd_length == 0) {
            *ptr++ = DEFAULT_SLASH;
        } else {
            *ptr++ = '\'';
            while (dir_length > 0) {
                switch (*dir) {
                case '\'':
                    *ptr++ = '\'';
                    *ptr++ = '\\';
                    *ptr++ = '\'';
                    /* fall-through */
                default:
                    *ptr++ = *dir;
                }
                dir++;
                dir_length--;
            }
            *ptr++ = '\'';
        }
    
        *ptr++ = ' ';
        *ptr++ = ';';
        *ptr++ = ' ';
    
        memcpy(ptr, command, command_length+1);
        retval = popen(command_line, type);
    
        efree(command_line);
        return retval;
    }
    /* }}} */
    #endif
    

不难发现，针对`virtual_popen()`函数实现，存在于不同平台，这里主要分析Linux平台。

针对Linux平台分析，可发现`virtual_popen()`函数不像WIN平台那样直接调用`popen_ex()`函数，而是自身进行了很多处理，事实上看过`PHP
for
Windows->命令执行底层分析->静态审计`部分，就会发现Linux平台下的`virtual_popen()`函数实现和windows中`TSRM\tsrm_win32.c`下的`popen_ex()`函数实现功能类似，都是对命令参数、当前工作空间等进行处理(分配空间、赋值)，然后去启动相应的进程来完成命令执行过程。

继续向后跟进分析`virtual_popen()`函数，最终会调用`popen(command_line,
type)`函数来执行命令。到了这里可能会有人疑惑，这里的`popen()`函数是谁实现的：是平常php里面用的`popen()`函数吗、是`TSRM\tsrm_win32.c:467`中的`TSRM_API
FILE *popen(const char *command, const char
*type)`函数吗，答案都是否定的，下面来看一下这几种猜想为什么是错误的。

第一种：php中的`popen()`函数。首先你要明白，你现在审计的是PHP内核源码，而不是在编写php程序代码。在PHP内核源码中，里面大部分都是定义与实现的PHP各种函数。

有关php中的`popen()`函数定义与实现在源码`ext\standard\file.c:927`中

    
    
    /* {{{ proto resource popen(string command, string mode)
       Execute a command and open either a read or a write pipe to it */
    PHP_FUNCTION(popen)
    {
        char *command, *mode;
        size_t command_len, mode_len;
        FILE *fp;
        php_stream *stream;
        char *posix_mode;
    
        ZEND_PARSE_PARAMETERS_START(2, 2)
            Z_PARAM_PATH(command, command_len)
            Z_PARAM_STRING(mode, mode_len)
        ZEND_PARSE_PARAMETERS_END();
    
        posix_mode = estrndup(mode, mode_len);
    #ifndef PHP_WIN32
        {
            char *z = memchr(posix_mode, 'b', mode_len);
            if (z) {
                memmove(z, z + 1, mode_len - (z - posix_mode));
            }
        }
    #endif
    
        fp = VCWD_POPEN(command, posix_mode);
        if (!fp) {
            php_error_docref2(NULL, command, posix_mode, E_WARNING, "%s", strerror(errno));
            efree(posix_mode);
            RETURN_FALSE;
        }
    
        stream = php_stream_fopen_from_pipe(fp, mode);
    
        if (stream == NULL)    {
            php_error_docref2(NULL, command, mode, E_WARNING, "%s", strerror(errno));
            RETVAL_FALSE;
        } else {
            php_stream_to_zval(stream, return_value);
        }
    
        efree(posix_mode);
    }
    /* }}} */
    

第二种：`TSRM\tsrm_win32.c:467`中的`*popen()`函数。细心的话你会发现在Linux平台编译下，根本不会去加载编译`TSRM\tsrm_win32.c:467`文件。

继续分析为什么，首先`*popen()`函数定义是在`TSRM\tsrm_win32.h:104`头文件中，那么查看`TSRM\tsrm_win32.c`文件是否包含该头文件

![](https://p3.ssl.qhimg.com/t01c2f381ee9e18f7db.png)

从包含结果可以发现，`TSRM\tsrm_win32.c`文件只在Windows平台下才会去包含`TSRM\tsrm_win32.h`头文件，这就说明在Linux平台下无法加载`TSRM\tsrm_win32.c:467`中的函数。

既然这两种猜想都不对那么`*virtual_popen()`中的`poen()`函数是由谁实现的，如果你对Linux平台熟悉的话，就会知道这里的`poen()`函数是在Linux下共享链接库`glibc`中实现的。

借助Windows平台下源码审查工具`Source Insight`【导入`glibc-2.31`源码项目】进行底层函数`poen()`跟踪分析

![](https://p5.ssl.qhimg.com/t0104cf62770b220946.png)

搜索整个项目定位`popen()`函数定义与实现位置：`libio\iopopen.c:321`

    
    
    strong_alias (_IO_new_popen, __new_popen)
    versioned_symbol (libc, _IO_new_popen, _IO_popen, GLIBC_2_1);
    versioned_symbol (libc, __new_popen, popen, GLIBC_2_1);
    versioned_symbol (libc, _IO_new_proc_open, _IO_proc_open, GLIBC_2_1);
    versioned_symbol (libc, _IO_new_proc_close, _IO_proc_close, GLIBC_2_1);
    

从上代码片段可以看出，`popen()`最终的实现为`_IO_new_popen()`，向上索引找到`_IO_new_popen()`函数实现：`libio\iopopen.c:220`

    
    
    FILE *
    _IO_new_popen (const char *command, const char *mode)
    {
      struct locked_FILE
      {
        struct _IO_proc_file fpx;
    #ifdef _IO_MTSAFE_IO
        _IO_lock_t lock;
    #endif
      } *new_f;
      FILE *fp;
    
      new_f = (struct locked_FILE *) malloc (sizeof (struct locked_FILE));
      if (new_f == NULL)
        return NULL;
    #ifdef _IO_MTSAFE_IO
      new_f->fpx.file.file._lock = &new_f->lock;
    #endif
      fp = &new_f->fpx.file.file;
      _IO_init_internal (fp, 0);
      _IO_JUMPS (&new_f->fpx.file) = &_IO_proc_jumps;
      _IO_new_file_init_internal (&new_f->fpx.file);
      if (_IO_new_proc_open (fp, command, mode) != NULL)
        return (FILE *) &new_f->fpx.file;
      _IO_un_link (&new_f->fpx.file);
      free (new_f);
      return NULL;
    }
    

在`_IO_new_popen()`函数中，除了变量的定义与处理，核心的地方是将command指令参数传给`_IO_new_proc_open (fp,
command, mode)`函数去实现，所以跟进`_IO_new_proc_open()`函数实现：`libio\iopopen.c:109`

    
    
    FILE *
    _IO_new_proc_open (FILE *fp, const char *command, const char *mode)
    {
      int read_or_write;
      /* These are indexes for pipe_fds.  */
      int parent_end, child_end;
      int pipe_fds[2];
      int child_pipe_fd;
      bool spawn_ok;
    
      int do_read = 0;
      int do_write = 0;
      int do_cloexec = 0;
      while (*mode != '\0')
        switch (*mode++)
          {
          case 'r':
        do_read = 1;
        break;
          case 'w':
        do_write = 1;
        break;
          case 'e':
        do_cloexec = 1;
        break;
          default:
          errout:
        __set_errno (EINVAL);
        return NULL;
          }
    
      if ((do_read ^ do_write) == 0)
        goto errout;
    
      if (_IO_file_is_open (fp))
        return NULL;
    
      /* Atomically set the O_CLOEXEC flag for the pipe end used by the
         child process (to avoid leaking the file descriptor in case of a
         concurrent fork).  This is later reverted in the child process.
         When popen returns, the parent pipe end can be O_CLOEXEC or not,
         depending on the 'e' open mode, but there is only one flag which
         controls both descriptors.  The parent end is adjusted below,
         after creating the child process.  (In the child process, the
         parent end should be closed on execve, so O_CLOEXEC remains set
         there.)  */
      if (__pipe2 (pipe_fds, O_CLOEXEC) < 0)
        return NULL;
    
      if (do_read)
        {
          parent_end = 0;
          child_end = 1;
          read_or_write = _IO_NO_WRITES;
          child_pipe_fd = 1;
        }
      else
        {
          parent_end = 1;
          child_end = 0;
          read_or_write = _IO_NO_READS;
          child_pipe_fd = 0;
        }
    
      posix_spawn_file_actions_t fa;
      /* posix_spawn_file_actions_init does not fail.  */
      __posix_spawn_file_actions_init (&fa);
    
      /* The descriptor is already the one the child will use.  In this case
         it must be moved to another one otherwise, there is no safe way to
         remove the close-on-exec flag in the child without creating a FD leak
         race in the parent.  */
      if (pipe_fds[child_end] == child_pipe_fd)
        {
          int tmp = __fcntl (child_pipe_fd, F_DUPFD_CLOEXEC, 0);
          if (tmp < 0)
        goto spawn_failure;
          __close_nocancel (pipe_fds[child_end]);
          pipe_fds[child_end] = tmp;
        }
    
      if (__posix_spawn_file_actions_adddup2 (&fa, pipe_fds[child_end],
          child_pipe_fd) != 0)
        goto spawn_failure;
    
    #ifdef _IO_MTSAFE_IO
      _IO_cleanup_region_start_noarg (unlock);
      _IO_lock_lock (proc_file_chain_lock);
    #endif
      spawn_ok = spawn_process (&fa, fp, command, do_cloexec, pipe_fds,
                    parent_end, child_end, child_pipe_fd);
    #ifdef _IO_MTSAFE_IO
      _IO_lock_unlock (proc_file_chain_lock);
      _IO_cleanup_region_end (0);
    #endif
    
      __posix_spawn_file_actions_destroy (&fa);
    
      if (!spawn_ok)
        {
        spawn_failure:
          __close_nocancel (pipe_fds[child_end]);
          __close_nocancel (pipe_fds[parent_end]);
          __set_errno (ENOMEM);
          return NULL;
        }
    
      _IO_mask_flags (fp, read_or_write, _IO_NO_READS|_IO_NO_WRITES);
      return fp;
    }
    

可以看到`_IO_new_proc_open()`函数代码开始部分对`mode`参数进行了处理，接着后面核心代码处调用了`spawn_process
(&fa, fp, command, do_cloexec, pipe_fds, parent_end, child_end,
child_pipe_fd)`函数，这个函数很明显看起来和进程有关系，不出意外后续代码的实现与调用肯定是创建command进程相关，进入`spawn_process()`函数实现：`libio\iopopen.c:71`

    
    
    /* POSIX states popen shall ensure that any streams from previous popen()
       calls that remain open in the parent process should be closed in the new
       child process.
       To avoid a race-condition between checking which file descriptors need to
       be close (by transversing the proc_file_chain list) and the insertion of a
       new one after a successful posix_spawn this function should be called
       with proc_file_chain_lock acquired.  */
    static bool
    spawn_process (posix_spawn_file_actions_t *fa, FILE *fp, const char *command,
               int do_cloexec, int pipe_fds[2], int parent_end, int child_end,
               int child_pipe_fd)
    {
    
      for (struct _IO_proc_file *p = proc_file_chain; p; p = p->next)
        {
          int fd = _IO_fileno ((FILE *) p);
    
          /* If any stream from previous popen() calls has fileno
         child_pipe_fd, it has been already closed by the adddup2 action
         above.  */
          if (fd != child_pipe_fd
          && __posix_spawn_file_actions_addclose (fa, fd) != 0)
        return false;
        }
    
      if (__posix_spawn (&((_IO_proc_file *) fp)->pid, _PATH_BSHELL, fa, 0,
                 (char *const[]){ (char*) "sh", (char*) "-c",
                 (char *) command, NULL }, __environ) != 0)
        return false;
    
      __close_nocancel (pipe_fds[child_end]);
    
      if (!do_cloexec)
        /* Undo the effects of the pipe2 call which set the
           close-on-exec flag.  */
        __fcntl (pipe_fds[parent_end], F_SETFD, 0);
    
      _IO_fileno (fp) = pipe_fds[parent_end];
    
      ((_IO_proc_file *) fp)->next = proc_file_chain;
      proc_file_chain = (_IO_proc_file *) fp;
    
      return true; 
    }
    

这里很明显`spawn_process()`函数的实现是由`__posix_spawn()`函数来完成的

    
    
      if (__posix_spawn (&((_IO_proc_file *) fp)->pid, _PATH_BSHELL, fa, 0,
                 (char *const[]){ (char*) "sh", (char*) "-c",
                 (char *) command, NULL }, __environ) != 0)
    

查看`_PATH_BSHELL`预定义参数值：`sysdeps\unix\sysv\linux\paths.h:41`

    
    
    #define    _PATH_BSHELL    "/bin/sh"
    

不难看出PHP命令执行函数传入的系统指令参数，底层将调用`/bin/sh`可执行程序来执行

    
    
    /bin/sh -c command
    

注意：这里的`/bin/sh`在不同平台中所指向的链接不同。

Linux系统，主要分为debian系（主要有Debian，Ubuntu，Mint等及其衍生版本）和redhat系（主要有RedHat，Fedora，CentOs等），还有其它自由的发布版本。debian系默认`/bin/sh`指向`/bin/dash`；redhat系默认`/bin/sh`指向`/bin/bash`。

Debian Almquist Shell 简称 dash，主要存在于debian类别的Linux系统中。

> 最初，bash是GNU/Linux 操作系统中 /bin/sh 的符号链接，但由于bash过于复杂，有人把 bash 从 NetBSD 移植到
> Linux 并更名为 dash，且/bin/sh符号连接到dash。Dash Shell 比 Bash Shell
> 小的多（ubuntu16.04上，bash大概1M，dash只有150K），符合POSIX标准。Ubuntu 6.10开始默认是Dash。

跟进`__posix_spawn()`函数实现：`posix\spawn.c:25`

    
    
    /* Spawn a new process executing PATH with the attributes describes in *ATTRP.
       Before running the process perform the actions described in FILE-ACTIONS. */
    int
    __posix_spawn (pid_t *pid, const char *path,
               const posix_spawn_file_actions_t *file_actions,
               const posix_spawnattr_t *attrp, char *const argv[],
               char *const envp[])
    {
      return __spawni (pid, path, file_actions, attrp, argv, envp, 0);
    }
    

`__posix_spawn()`函数直接调用`__spawni()`函数来实现，根据`__posix_spawn()`函数注释描述可知，该函数功能为创建一个新的可执行程序进程也就是`/bin/sh`进程。

进入`__spawni()`函数实现：`sysdeps\unix\sysv\linux\spawni.c:424`

    
    
    /* Spawn a new process executing PATH with the attributes describes in *ATTRP.
       Before running the process perform the actions described in FILE-ACTIONS. */
    int
    __spawni (pid_t * pid, const char *file,
          const posix_spawn_file_actions_t * acts,
          const posix_spawnattr_t * attrp, char *const argv[],
          char *const envp[], int xflags)
    {
      /* It uses __execvpex to avoid run ENOEXEC in non compatibility mode (it
         will be handled by maybe_script_execute).  */
      return __spawnix (pid, file, acts, attrp, argv, envp, xflags,
                xflags & SPAWN_XFLAGS_USE_PATH ? __execvpex :__execve);
    }
    

可以看到`__spawni()`函数的实现，直接调用`__spawnix()`函数返回。

查看`__spawnix()`函数的实现：`sysdeps\unix\sysv\linux\spawni.c:312`

    
    
    /* Spawn a new process executing PATH with the attributes describes in *ATTRP.
       Before running the process perform the actions described in FILE-ACTIONS. */
    static int
    __spawnix (pid_t * pid, const char *file,
           const posix_spawn_file_actions_t * file_actions,
           const posix_spawnattr_t * attrp, char *const argv[],
           char *const envp[], int xflags,
           int (*exec) (const char *, char *const *, char *const *))
    {
      pid_t new_pid;
      struct posix_spawn_args args;
      int ec;
    
      /* To avoid imposing hard limits on posix_spawn{p} the total number of
         arguments is first calculated to allocate a mmap to hold all possible
         values.  */
      ptrdiff_t argc = 0;
      /* Linux allows at most max (0x7FFFFFFF, 1/4 stack size) arguments
         to be used in a execve call.  We limit to INT_MAX minus one due the
         compatiblity code that may execute a shell script (maybe_script_execute)
         where it will construct another argument list with an additional
         argument.  */
      ptrdiff_t limit = INT_MAX - 1;
      while (argv[argc++] != NULL)
        if (argc == limit)
          {
        errno = E2BIG;
        return errno;
          }
    
      int prot = (PROT_READ | PROT_WRITE
             | ((GL (dl_stack_flags) & PF_X) ? PROT_EXEC : 0));
    
      /* Add a slack area for child's stack.  */
      size_t argv_size = (argc * sizeof (void *)) + 512;
      /* We need at least a few pages in case the compiler's stack checking is
         enabled.  In some configs, it is known to use at least 24KiB.  We use
         32KiB to be "safe" from anything the compiler might do.  Besides, the
         extra pages won't actually be allocated unless they get used.  */
      argv_size += (32 * 1024);
      size_t stack_size = ALIGN_UP (argv_size, GLRO(dl_pagesize));
      void *stack = __mmap (NULL, stack_size, prot,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_STACK, -1, 0);
      if (__glibc_unlikely (stack == MAP_FAILED))
        return errno;
    
      /* Disable asynchronous cancellation.  */
      int state;
      __libc_ptf_call (__pthread_setcancelstate,
                       (PTHREAD_CANCEL_DISABLE, &state), 0);
    
      /* Child must set args.err to something non-negative - we rely on
         the parent and child sharing VM.  */
      args.err = 0;
      args.file = file;
      args.exec = exec;
      args.fa = file_actions;
      args.attr = attrp ? attrp : &(const posix_spawnattr_t) { 0 };
      args.argv = argv;
      args.argc = argc;
      args.envp = envp;
      args.xflags = xflags;
    
      __libc_signal_block_all (&args.oldmask);
    
      /* The clone flags used will create a new child that will run in the same
         memory space (CLONE_VM) and the execution of calling thread will be
         suspend until the child calls execve or _exit.
    
         Also since the calling thread execution will be suspend, there is not
         need for CLONE_SETTLS.  Although parent and child share the same TLS
         namespace, there will be no concurrent access for TLS variables (errno
         for instance).  */
      new_pid = CLONE (__spawni_child, STACK (stack, stack_size), stack_size,
               CLONE_VM | CLONE_VFORK | SIGCHLD, &args);
    
      /* It needs to collect the case where the auxiliary process was created
         but failed to execute the file (due either any preparation step or
         for execve itself).  */
      if (new_pid > 0)
        {
          /* Also, it handles the unlikely case where the auxiliary process was
         terminated before calling execve as if it was successfully.  The
         args.err is set to 0 as default and changed to a positive value
         only in case of failure, so in case of premature termination
         due a signal args.err will remain zeroed and it will be up to
         caller to actually collect it.  */
          ec = args.err;
          if (ec > 0)
        /* There still an unlikely case where the child is cancelled after
           setting args.err, due to a positive error value.  Also there is
           possible pid reuse race (where the kernel allocated the same pid
           to an unrelated process).  Unfortunately due synchronization
           issues where the kernel might not have the process collected
           the waitpid below can not use WNOHANG.  */
        __waitpid (new_pid, NULL, 0);
        }
      else
        ec = -new_pid;
    
      __munmap (stack, stack_size);
    
      if ((ec == 0) && (pid != NULL))
        *pid = new_pid;
    
      __libc_signal_restore_set (&args.oldmask);
    
      __libc_ptf_call (__pthread_setcancelstate, (state, NULL), 0);
    
      return ec;
    }
    

忽略`__spawnix()`函数内部变量处理外，核心代码在于调用`CLONE()`函数，作用为克隆父进程以创建新的子进程。

    
    
      /* The clone flags used will create a new child that will run in the same
         memory space (CLONE_VM) and the execution of calling thread will be
         suspend until the child calls execve or _exit.
    
         Also since the calling thread execution will be suspend, there is not
         need for CLONE_SETTLS.  Although parent and child share the same TLS
         namespace, there will be no concurrent access for TLS variables (errno
         for instance).  */
      new_pid = CLONE (__spawni_child, STACK (stack, stack_size), stack_size,
               CLONE_VM | CLONE_VFORK | SIGCHLD, &args);
    

`CLONE()`函数实现通常位于`sysdeps\unix\sysv\linux\平台架构(arm、i386、x86、x86_64等)\clone.S`汇编代码文件中。

由于这里测试的平台为`x86_64`，所以`CLONE()`函数实现位置为：`sysdeps\unix\sysv\linux\x86_64\clone.S`

    
    
    /* Copyright (C) 2001-2020 Free Software Foundation, Inc.
       This file is part of the GNU C Library.
    
       The GNU C Library is free software; you can redistribute it and/or
       modify it under the terms of the GNU Lesser General Public
       License as published by the Free Software Foundation; either
       version 2.1 of the License, or (at your option) any later version.
    
       The GNU C Library is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
       Lesser General Public License for more details.
    
       You should have received a copy of the GNU Lesser General Public
       License along with the GNU C Library; if not, see
       <https://www.gnu.org/licenses/>.  */
    
    /* clone() is even more special than fork() as it mucks with stacks
       and invokes a function in the right context after its all over.  */
    
    #include <sysdep.h>
    #define _ERRNO_H    1
    #include <bits/errno.h>
    #include <asm-syntax.h>
    
    /* The userland implementation is:
       int clone (int (*fn)(void *arg), void *child_stack, int flags, void *arg),
       the kernel entry is:
       int clone (long flags, void *child_stack).
    
       The parameters are passed in register and on the stack from userland:
       rdi: fn
       rsi: child_stack
       rdx:    flags
       rcx: arg
       r8d:    TID field in parent
       r9d: thread pointer
    %esp+8:    TID field in child
    
       The kernel expects:
       rax: system call number
       rdi: flags
       rsi: child_stack
       rdx: TID field in parent
       r10: TID field in child
       r8:    thread pointer  */
    
    
            .text
    ENTRY (__clone)
        /* Sanity check arguments.  */
        movq    $-EINVAL,%rax
        testq    %rdi,%rdi        /* no NULL function pointers */
        jz    SYSCALL_ERROR_LABEL
        testq    %rsi,%rsi        /* no NULL stack pointers */
        jz    SYSCALL_ERROR_LABEL
    
        /* Insert the argument onto the new stack.  */
        subq    $16,%rsi
        movq    %rcx,8(%rsi)
    
        /* Save the function pointer.  It will be popped off in the
           child in the ebx frobbing below.  */
        movq    %rdi,0(%rsi)
    
        /* Do the system call.  */
        movq    %rdx, %rdi
        movq    %r8, %rdx
        movq    %r9, %r8
        mov    8(%rsp), %R10_LP
        movl    $SYS_ify(clone),%eax
    
        /* End FDE now, because in the child the unwind info will be
           wrong.  */
        cfi_endproc;
        syscall
    
        testq    %rax,%rax
        jl    SYSCALL_ERROR_LABEL
        jz    L(thread_start)
    
        ret
    
    L(thread_start):
        cfi_startproc;
        /* Clearing frame pointer is insufficient, use CFI.  */
        cfi_undefined (rip);
        /* Clear the frame pointer.  The ABI suggests this be done, to mark
           the outermost frame obviously.  */
        xorl    %ebp, %ebp
    
        /* Set up arguments for the function call.  */
        popq    %rax        /* Function to call.  */
        popq    %rdi        /* Argument.  */
        call    *%rax
        /* Call exit with return value from function call. */
        movq    %rax, %rdi
        movl    $SYS_ify(exit), %eax
        syscall
        cfi_endproc;
    
        cfi_startproc;
    PSEUDO_END (__clone)
    
    libc_hidden_def (__clone)
    weak_alias (__clone, clone)
    

审计`CLONE()`函数实现的`clone.S`汇编代码，由`weak_alias (__clone,
clone)`可知，`clone()`函数别名为`__clone()`函数。

跟进分析`__clone()`函数的实现

    
    
    ENTRY (__clone)
        /* Sanity check arguments.  */
        movq    $-EINVAL,%rax
        testq    %rdi,%rdi        /* no NULL function pointers */
        jz    SYSCALL_ERROR_LABEL
        testq    %rsi,%rsi        /* no NULL stack pointers */
        jz    SYSCALL_ERROR_LABEL
    
        /* Insert the argument onto the new stack.  */
        subq    $16,%rsi
        movq    %rcx,8(%rsi)
    
        /* Save the function pointer.  It will be popped off in the
           child in the ebx frobbing below.  */
        movq    %rdi,0(%rsi)
    
        /* Do the system call.  */
        movq    %rdx, %rdi
        movq    %r8, %rdx
        movq    %r9, %r8
        mov    8(%rsp), %R10_LP
        movl    $SYS_ify(clone),%eax
    
        /* End FDE now, because in the child the unwind info will be
           wrong.  */
        cfi_endproc;
        syscall
    
        testq    %rax,%rax
        jl    SYSCALL_ERROR_LABEL
        jz    L(thread_start)
    
        ret
    

`__clone()`函数核心代码为系统调用部分

    
    
        /* Do the system call.  */
        movq    %rdx, %rdi
        movq    %r8, %rdx
        movq    %r9, %r8
        mov    8(%rsp), %R10_LP
        movl    $SYS_ify(clone),%eax
    
        /* End FDE now, because in the child the unwind info will be
           wrong.  */
        cfi_endproc;
        syscall
    

事实上这里`clone()`函数是一个系统调用函数，内核入口为`sys_clone()`，系统调用号为`0x38`，主要作用是创建子进程：克隆父进程。

有关Linux下系统调用号的查询，根据不同平台查看不同文件：unistd.h（x86）、unistd_64.h（x86_64），针对该Linux系统平台存储在：`/usr/include/x86_64-linux-gnu/asm/unistd_64.h`

    
    
    #ifndef _ASM_X86_UNISTD_64_H
    #define _ASM_X86_UNISTD_64_H 1
    
    #define __NR_read 0
    #define __NR_write 1
    #define __NR_open 2
    #define __NR_close 3
    #define __NR_stat 4
    #define __NR_fstat 5
    #define __NR_lstat 6
    #define __NR_poll 7
    #define __NR_lseek 8
    #define __NR_mmap 9
    #define __NR_mprotect 10
    #define __NR_munmap 11
    #define __NR_brk 12
    #define __NR_rt_sigaction 13
    #define __NR_rt_sigprocmask 14
    #define __NR_rt_sigreturn 15
    #define __NR_ioctl 16
    #define __NR_pread64 17
    #define __NR_pwrite64 18
    #define __NR_readv 19
    #define __NR_writev 20
    #define __NR_access 21
    #define __NR_pipe 22
    #define __NR_select 23
    #define __NR_sched_yield 24
    #define __NR_mremap 25
    #define __NR_msync 26
    #define __NR_mincore 27
    #define __NR_madvise 28
    #define __NR_shmget 29
    #define __NR_shmat 30
    #define __NR_shmctl 31
    #define __NR_dup 32
    #define __NR_dup2 33
    #define __NR_pause 34
    #define __NR_nanosleep 35
    #define __NR_getitimer 36
    #define __NR_alarm 37
    #define __NR_setitimer 38
    #define __NR_getpid 39
    #define __NR_sendfile 40
    #define __NR_socket 41
    #define __NR_connect 42
    #define __NR_accept 43
    #define __NR_sendto 44
    #define __NR_recvfrom 45
    #define __NR_sendmsg 46
    #define __NR_recvmsg 47
    #define __NR_shutdown 48
    #define __NR_bind 49
    #define __NR_listen 50
    #define __NR_getsockname 51
    #define __NR_getpeername 52
    #define __NR_socketpair 53
    #define __NR_setsockopt 54
    #define __NR_getsockopt 55
    #define __NR_clone 56
    #define __NR_fork 57
    #define __NR_vfork 58
    #define __NR_execve 59
    #define __NR_exit 60
    #define __NR_wait4 61
    #define __NR_kill 62
    #define __NR_uname 63
    #define __NR_semget 64
    #define __NR_semop 65
    #define __NR_semctl 66
    #define __NR_shmdt 67
    #define __NR_msgget 68
    #define __NR_msgsnd 69
    #define __NR_msgrcv 70
    #define __NR_msgctl 71
    #define __NR_fcntl 72
    #define __NR_flock 73
    #define __NR_fsync 74
    #define __NR_fdatasync 75
    #define __NR_truncate 76
    #define __NR_ftruncate 77
    #define __NR_getdents 78
    #define __NR_getcwd 79
    #define __NR_chdir 80
    #define __NR_fchdir 81
    #define __NR_rename 82
    #define __NR_mkdir 83
    #define __NR_rmdir 84
    #define __NR_creat 85
    #define __NR_link 86
    #define __NR_unlink 87
    #define __NR_symlink 88
    #define __NR_readlink 89
    #define __NR_chmod 90
    #define __NR_fchmod 91
    #define __NR_chown 92
    #define __NR_fchown 93
    #define __NR_lchown 94
    #define __NR_umask 95
    #define __NR_gettimeofday 96
    #define __NR_getrlimit 97
    #define __NR_getrusage 98
    #define __NR_sysinfo 99
    #define __NR_times 100
    #define __NR_ptrace 101
    #define __NR_getuid 102
    #define __NR_syslog 103
    #define __NR_getgid 104
    #define __NR_setuid 105
    #define __NR_setgid 106
    #define __NR_geteuid 107
    #define __NR_getegid 108
    #define __NR_setpgid 109
    #define __NR_getppid 110
    #define __NR_getpgrp 111
    #define __NR_setsid 112
    #define __NR_setreuid 113
    #define __NR_setregid 114
    #define __NR_getgroups 115
    #define __NR_setgroups 116
    #define __NR_setresuid 117
    #define __NR_getresuid 118
    #define __NR_setresgid 119
    #define __NR_getresgid 120
    #define __NR_getpgid 121
    #define __NR_setfsuid 122
    #define __NR_setfsgid 123
    #define __NR_getsid 124
    #define __NR_capget 125
    #define __NR_capset 126
    #define __NR_rt_sigpending 127
    #define __NR_rt_sigtimedwait 128
    #define __NR_rt_sigqueueinfo 129
    #define __NR_rt_sigsuspend 130
    #define __NR_sigaltstack 131
    #define __NR_utime 132
    #define __NR_mknod 133
    #define __NR_uselib 134
    #define __NR_personality 135
    #define __NR_ustat 136
    #define __NR_statfs 137
    #define __NR_fstatfs 138
    #define __NR_sysfs 139
    #define __NR_getpriority 140
    #define __NR_setpriority 141
    #define __NR_sched_setparam 142
    #define __NR_sched_getparam 143
    #define __NR_sched_setscheduler 144
    #define __NR_sched_getscheduler 145
    #define __NR_sched_get_priority_max 146
    #define __NR_sched_get_priority_min 147
    #define __NR_sched_rr_get_interval 148
    #define __NR_mlock 149
    #define __NR_munlock 150
    #define __NR_mlockall 151
    #define __NR_munlockall 152
    #define __NR_vhangup 153
    #define __NR_modify_ldt 154
    #define __NR_pivot_root 155
    #define __NR__sysctl 156
    #define __NR_prctl 157
    #define __NR_arch_prctl 158
    #define __NR_adjtimex 159
    #define __NR_setrlimit 160
    #define __NR_chroot 161
    #define __NR_sync 162
    #define __NR_acct 163
    #define __NR_settimeofday 164
    #define __NR_mount 165
    #define __NR_umount2 166
    #define __NR_swapon 167
    #define __NR_swapoff 168
    #define __NR_reboot 169
    #define __NR_sethostname 170
    #define __NR_setdomainname 171
    #define __NR_iopl 172
    #define __NR_ioperm 173
    #define __NR_create_module 174
    #define __NR_init_module 175
    #define __NR_delete_module 176
    #define __NR_get_kernel_syms 177
    #define __NR_query_module 178
    #define __NR_quotactl 179
    #define __NR_nfsservctl 180
    #define __NR_getpmsg 181
    #define __NR_putpmsg 182
    #define __NR_afs_syscall 183
    #define __NR_tuxcall 184
    #define __NR_security 185
    #define __NR_gettid 186
    #define __NR_readahead 187
    #define __NR_setxattr 188
    #define __NR_lsetxattr 189
    #define __NR_fsetxattr 190
    #define __NR_getxattr 191
    #define __NR_lgetxattr 192
    #define __NR_fgetxattr 193
    #define __NR_listxattr 194
    #define __NR_llistxattr 195
    #define __NR_flistxattr 196
    #define __NR_removexattr 197
    #define __NR_lremovexattr 198
    #define __NR_fremovexattr 199
    #define __NR_tkill 200
    #define __NR_time 201
    #define __NR_futex 202
    #define __NR_sched_setaffinity 203
    #define __NR_sched_getaffinity 204
    #define __NR_set_thread_area 205
    #define __NR_io_setup 206
    #define __NR_io_destroy 207
    #define __NR_io_getevents 208
    #define __NR_io_submit 209
    #define __NR_io_cancel 210
    #define __NR_get_thread_area 211
    #define __NR_lookup_dcookie 212
    #define __NR_epoll_create 213
    #define __NR_epoll_ctl_old 214
    #define __NR_epoll_wait_old 215
    #define __NR_remap_file_pages 216
    #define __NR_getdents64 217
    #define __NR_set_tid_address 218
    #define __NR_restart_syscall 219
    #define __NR_semtimedop 220
    #define __NR_fadvise64 221
    #define __NR_timer_create 222
    #define __NR_timer_settime 223
    #define __NR_timer_gettime 224
    #define __NR_timer_getoverrun 225
    #define __NR_timer_delete 226
    #define __NR_clock_settime 227
    #define __NR_clock_gettime 228
    #define __NR_clock_getres 229
    #define __NR_clock_nanosleep 230
    #define __NR_exit_group 231
    #define __NR_epoll_wait 232
    #define __NR_epoll_ctl 233
    #define __NR_tgkill 234
    #define __NR_utimes 235
    #define __NR_vserver 236
    #define __NR_mbind 237
    #define __NR_set_mempolicy 238
    #define __NR_get_mempolicy 239
    #define __NR_mq_open 240
    #define __NR_mq_unlink 241
    #define __NR_mq_timedsend 242
    #define __NR_mq_timedreceive 243
    #define __NR_mq_notify 244
    #define __NR_mq_getsetattr 245
    #define __NR_kexec_load 246
    #define __NR_waitid 247
    #define __NR_add_key 248
    #define __NR_request_key 249
    #define __NR_keyctl 250
    #define __NR_ioprio_set 251
    #define __NR_ioprio_get 252
    #define __NR_inotify_init 253
    #define __NR_inotify_add_watch 254
    #define __NR_inotify_rm_watch 255
    #define __NR_migrate_pages 256
    #define __NR_openat 257
    #define __NR_mkdirat 258
    #define __NR_mknodat 259
    #define __NR_fchownat 260
    #define __NR_futimesat 261
    #define __NR_newfstatat 262
    #define __NR_unlinkat 263
    #define __NR_renameat 264
    #define __NR_linkat 265
    #define __NR_symlinkat 266
    #define __NR_readlinkat 267
    #define __NR_fchmodat 268
    #define __NR_faccessat 269
    #define __NR_pselect6 270
    #define __NR_ppoll 271
    #define __NR_unshare 272
    #define __NR_set_robust_list 273
    #define __NR_get_robust_list 274
    #define __NR_splice 275
    #define __NR_tee 276
    #define __NR_sync_file_range 277
    #define __NR_vmsplice 278
    #define __NR_move_pages 279
    #define __NR_utimensat 280
    #define __NR_epoll_pwait 281
    #define __NR_signalfd 282
    #define __NR_timerfd_create 283
    #define __NR_eventfd 284
    #define __NR_fallocate 285
    #define __NR_timerfd_settime 286
    #define __NR_timerfd_gettime 287
    #define __NR_accept4 288
    #define __NR_signalfd4 289
    #define __NR_eventfd2 290
    #define __NR_epoll_create1 291
    #define __NR_dup3 292
    #define __NR_pipe2 293
    #define __NR_inotify_init1 294
    #define __NR_preadv 295
    #define __NR_pwritev 296
    #define __NR_rt_tgsigqueueinfo 297
    #define __NR_perf_event_open 298
    #define __NR_recvmmsg 299
    #define __NR_fanotify_init 300
    #define __NR_fanotify_mark 301
    #define __NR_prlimit64 302
    #define __NR_name_to_handle_at 303
    #define __NR_open_by_handle_at 304
    #define __NR_clock_adjtime 305
    #define __NR_syncfs 306
    #define __NR_sendmmsg 307
    #define __NR_setns 308
    #define __NR_getcpu 309
    #define __NR_process_vm_readv 310
    #define __NR_process_vm_writev 311
    #define __NR_kcmp 312
    #define __NR_finit_module 313
    #define __NR_sched_setattr 314
    #define __NR_sched_getattr 315
    #define __NR_renameat2 316
    #define __NR_seccomp 317
    #define __NR_getrandom 318
    #define __NR_memfd_create 319
    #define __NR_kexec_file_load 320
    #define __NR_bpf 321
    #define __NR_execveat 322
    #define __NR_userfaultfd 323
    #define __NR_membarrier 324
    #define __NR_mlock2 325
    #define __NR_copy_file_range 326
    #define __NR_preadv2 327
    #define __NR_pwritev2 328
    #define __NR_pkey_mprotect 329
    #define __NR_pkey_alloc 330
    #define __NR_pkey_free 331
    #define __NR_statx 332
    #define __NR_io_pgetevents 333
    #define __NR_rseq 334
    #define __NR_pidfd_send_signal 424
    #define __NR_io_uring_setup 425
    #define __NR_io_uring_enter 426
    #define __NR_io_uring_register 427
    #define __NR_open_tree 428
    #define __NR_move_mount 429
    #define __NR_fsopen 430
    #define __NR_fsconfig 431
    #define __NR_fsmount 432
    #define __NR_fspick 433
    #define __NR_pidfd_open 434
    #define __NR_clone3 435
    #define __NR_close_range 436
    #define __NR_openat2 437
    #define __NR_pidfd_getfd 438
    #define __NR_faccessat2 439
    
    
    #endif /* _ASM_X86_UNISTD_64_H */
    

或者通过在线平台进行查询：[各种平台下的系统调用号](https://fedora.juszkiewicz.com.pl/syscalls.html)

这里系统调用之后仅仅是克隆了一个父进程，要想将一个子进程正真启动起来，还需要去调用`__spawni_child()`函数。

    
    
        /* Set up arguments for the function call.  */
        popq    %rax        /* Function to call.  */
        popq    %rdi        /* Argument.  */
        call    *%rax
        /* Call exit with return value from function call. */
        movq    %rax, %rdi
        movl    $SYS_ify(exit), %eax
        syscall
        cfi_endproc;
    

这里`L(thread_start):`中的call指令会调用最初CLONE()函数的第一个参数：`__spawni_child()`函数。

定位`__spawni_child()`函数的实现：`sysdeps\unix\sysv\linux\spawni.c:121`

    
    
    /* Function used in the clone call to setup the signals mask, posix_spawn
       attributes, and file actions.  It run on its own stack (provided by the
       posix_spawn call).  */
    static int
    __spawni_child (void *arguments)
    {
      struct posix_spawn_args *args = arguments;
      const posix_spawnattr_t *restrict attr = args->attr;
      const posix_spawn_file_actions_t *file_actions = args->fa;
    
      /* The child must ensure that no signal handler are enabled because it shared
         memory with parent, so the signal disposition must be either SIG_DFL or
         SIG_IGN.  It does by iterating over all signals and although it could
         possibly be more optimized (by tracking which signal potentially have a
         signal handler), it might requires system specific solutions (since the
         sigset_t data type can be very different on different architectures).  */
      struct sigaction sa;
      memset (&sa, '\0', sizeof (sa));
    
      sigset_t hset;
      __sigprocmask (SIG_BLOCK, 0, &hset);
      for (int sig = 1; sig < _NSIG; ++sig)
        {
          if ((attr->__flags & POSIX_SPAWN_SETSIGDEF)
          && __sigismember (&attr->__sd, sig))
        {
          sa.sa_handler = SIG_DFL;
        }
          else if (__sigismember (&hset, sig))
        {
          if (__is_internal_signal (sig))
            sa.sa_handler = SIG_IGN;
          else
            {
              __libc_sigaction (sig, 0, &sa);
              if (sa.sa_handler == SIG_IGN)
            continue;
              sa.sa_handler = SIG_DFL;
            }
        }
          else
        continue;
    
          __libc_sigaction (sig, &sa, 0);
        }
    
    #ifdef _POSIX_PRIORITY_SCHEDULING
      /* Set the scheduling algorithm and parameters.  */
      if ((attr->__flags & (POSIX_SPAWN_SETSCHEDPARAM | POSIX_SPAWN_SETSCHEDULER))
          == POSIX_SPAWN_SETSCHEDPARAM)
        {
          if (__sched_setparam (0, &attr->__sp) == -1)
        goto fail;
        }
      else if ((attr->__flags & POSIX_SPAWN_SETSCHEDULER) != 0)
        {
          if (__sched_setscheduler (0, attr->__policy, &attr->__sp) == -1)
        goto fail;
        }
    #endif
    
      if ((attr->__flags & POSIX_SPAWN_SETSID) != 0
          && __setsid () < 0)
        goto fail;
    
      /* Set the process group ID.  */
      if ((attr->__flags & POSIX_SPAWN_SETPGROUP) != 0
          && __setpgid (0, attr->__pgrp) != 0)
        goto fail;
    
      /* Set the effective user and group IDs.  */
      if ((attr->__flags & POSIX_SPAWN_RESETIDS) != 0
          && (local_seteuid (__getuid ()) != 0
          || local_setegid (__getgid ()) != 0))
        goto fail;
    
      /* Execute the file actions.  */
      if (file_actions != 0)
        {
          int cnt;
          struct rlimit64 fdlimit;
          bool have_fdlimit = false;
    
          for (cnt = 0; cnt < file_actions->__used; ++cnt)
        {
          struct __spawn_action *action = &file_actions->__actions[cnt];
    
          switch (action->tag)
            {
            case spawn_do_close:
              if (__close_nocancel (action->action.close_action.fd) != 0)
            {
              if (!have_fdlimit)
                {
                  __getrlimit64 (RLIMIT_NOFILE, &fdlimit);
                  have_fdlimit = true;
                }
    
              /* Signal errors only for file descriptors out of range.  */
              if (action->action.close_action.fd < 0
                  || action->action.close_action.fd >= fdlimit.rlim_cur)
                goto fail;
            }
              break;
    
            case spawn_do_open:
              {
            /* POSIX states that if fildes was already an open file descriptor,
               it shall be closed before the new file is opened.  This avoid
               pontential issues when posix_spawn plus addopen action is called
               with the process already at maximum number of file descriptor
               opened and also for multiple actions on single-open special
               paths (like /dev/watchdog).  */
            __close_nocancel (action->action.open_action.fd);
    
            int ret = __open_nocancel (action->action.open_action.path,
                           action->action.
                           open_action.oflag | O_LARGEFILE,
                           action->action.open_action.mode);
    
            if (ret == -1)
              goto fail;
    
            int new_fd = ret;
    
            /* Make sure the desired file descriptor is used.  */
            if (ret != action->action.open_action.fd)
              {
                if (__dup2 (new_fd, action->action.open_action.fd)
                != action->action.open_action.fd)
                  goto fail;
    
                if (__close_nocancel (new_fd) != 0)
                  goto fail;
              }
              }
              break;
    
            case spawn_do_dup2:
              /* Austin Group issue #411 requires adddup2 action with source
             and destination being equal to remove close-on-exec flag.  */
              if (action->action.dup2_action.fd
              == action->action.dup2_action.newfd)
            {
              int fd = action->action.dup2_action.newfd;
              int flags = __fcntl (fd, F_GETFD, 0);
              if (flags == -1)
                goto fail;
              if (__fcntl (fd, F_SETFD, flags & ~FD_CLOEXEC) == -1)
                goto fail;
            }
              else if (__dup2 (action->action.dup2_action.fd,
                       action->action.dup2_action.newfd)
                   != action->action.dup2_action.newfd)
            goto fail;
              break;
    
            case spawn_do_chdir:
              if (__chdir (action->action.chdir_action.path) != 0)
            goto fail;
              break;
    
            case spawn_do_fchdir:
              if (__fchdir (action->action.fchdir_action.fd) != 0)
            goto fail;
              break;
            }
        }
        }
    
      /* Set the initial signal mask of the child if POSIX_SPAWN_SETSIGMASK
         is set, otherwise restore the previous one.  */
      __sigprocmask (SIG_SETMASK, (attr->__flags & POSIX_SPAWN_SETSIGMASK)
             ? &attr->__ss : &args->oldmask, 0);
    
      args->exec (args->file, args->argv, args->envp);
    
      /* This is compatibility function required to enable posix_spawn run
         script without shebang definition for older posix_spawn versions
         (2.15).  */
      maybe_script_execute (args);
    
    fail:
      /* errno should have an appropriate non-zero value; otherwise,
         there's a bug in glibc or the kernel.  For lack of an error code
         (EINTERNALBUG) describing that, use ECHILD.  Another option would
         be to set args->err to some negative sentinel and have the parent
         abort(), but that seems needlessly harsh.  */
      args->err = errno ? : ECHILD;
      _exit (SPAWN_ERROR);
    }
    

审计`__spawni_child()`函数，核心代码位于

    
    
      args->exec (args->file, args->argv, args->envp);
    

该部分为动态函数调用，那么`args->exec`为什么呢，回头向上追溯该值的传递过程：首先`__spawni_child (void
*arguments)`中`arguments`的参数由`clone()`函数传递

    
    
    new_pid = CLONE (__spawni_child, STACK (stack, stack_size), stack_size,
               CLONE_VM | CLONE_VFORK | SIGCHLD, &args);
    

而`CLONE()`中的`args`参数由`__spawnix()`函数传递

    
    
    __spawnix (pid_t * pid, const char *file,
           const posix_spawn_file_actions_t * file_actions,
           const posix_spawnattr_t * attrp, char *const argv[],
           char *const envp[], int xflags,
           int (*exec) (const char *, char *const *, char *const *)){
        、、、、、
      args.err = 0;
      args.file = file;
      args.exec = exec;
      args.fa = file_actions;
      args.attr = attrp ? attrp : &(const posix_spawnattr_t) { 0 };
      args.argv = argv;
      args.argc = argc;
      args.envp = envp;
      args.xflags = xflags;
        、、、、、、
      new_pid = CLONE (__spawni_child, STACK (stack, stack_size), stack_size,CLONE_VM | CLONE_VFORK | SIGCHLD, &args);
    
    }
    

在`__spawnix()`函数参数中发现`exec`参数，继续向上追溯到`__spawni()`的函数调用

    
    
    __spawni (pid_t * pid, const char *file,
          const posix_spawn_file_actions_t * acts,
          const posix_spawnattr_t * attrp, char *const argv[],
          char *const envp[], int xflags)
    {
      /* It uses __execvpex to avoid run ENOEXEC in non compatibility mode (it
         will be handled by maybe_script_execute).  */
      return __spawnix (pid, file, acts, attrp, argv, envp, xflags,
                xflags & SPAWN_XFLAGS_USE_PATH ? __execvpex :__execve);
    }
    

在`__spawni()`函数调用`__spawnix()`函数的传参过程中，可追溯到exec的参数值，其值由一个三目运算表达式来决定

    
    
    xflags & SPAWN_XFLAGS_USE_PATH ? __execvpex :__execve
    

表达式的核心在于：`与`运算，所以分别追溯`xflags` 与 `SPAWN_XFLAGS_USE_PATH`的参数值。

追溯`xflags`：`__spawni()`函数由`__posix_spawn()`函数传参调用，得到`xflags`参数的值为`0`

    
    
    __posix_spawn (pid_t *pid, const char *path,
               const posix_spawn_file_actions_t *file_actions,
               const posix_spawnattr_t *attrp, char *const argv[],
               char *const envp[])
    {
      return __spawni (pid, path, file_actions, attrp, argv, envp, 0);
    }
    

追溯`SPAWN_XFLAGS_USE_PATH`：`SPAWN_XFLAGS_USE_PATH`参数的预定义位于：`posix\spawn_int.h:66`

    
    
    #define SPAWN_XFLAGS_USE_PATH    0x1
    

知道两个参数值后：与运算的结果为0，exec参数赋值为`__execve()`。

继续回到上面动态调用部分，可知`__spawni_child()`函数实现会调用`__execve()`函数

    
    
      args->exec (args->file, args->argv, args->envp);
    

`__execve()`函数为`execve()`函数的别名

    
    
    weak_alias (__execve, execve)
    

此时`execve()`函数接收的参数：file为`/bin/sh`、argv为`sh -c whoami`。

`execve()`函数主要用于创建进程，第一个参数为要启动的程序完整路径，第二个参数为要执行的程序指令。当`execve()`函数把`/bin/sh`进程启动起来后，然后由`sh`来执行系统指令(内部|外部)，即可完成PHP命令执行函数的整个调用过程。

事实上这里`execve()`函数为系统调用函数，内核入口为`sys_execve()`，系统调用号为`0x3b`，而在C语言的程序库中则又在此基础上向应用程序提供一整套的库函数，包括execl()、execle()、execlp()、execv()、execve()和execvp()。

在Linux
C语言编程里面常用exec()函数族来启动程序进程：execl、execle、execlp、execv、execve和execvp函数，exec()函数族的6个成员函数语法如下：

所需头文件 | 函数说明 | 函数原型 | 函数返回值  
---|---|---|---  
`#include <unistd.h>` | 执行程序 |  `int execl(const char *pathname, const char
*arg, ..., (char *)0)`<br/>`int execv(const char *pathname, char *const
argv[])`<br/>`int execle(const char *pathname, const char *arg, ..., (char
*)0, char *const envp[])`<br>`int execve(const char *pathname, char *const
argv[], char *const envp[])`<br/>`int execlp(const char *filename, const char
*arg, ..., (char *)0)`<br/>`int execvp(const char *filename, char *const
argv[])` | 成功：函数不会返回<br/>出错：返回-1，失败原因记录在error中  
  
这里以`execve()`函数为例简单编写一个Demo进行演示：CommandExec1.c

    
    
    #include <stdio.h>
    #include <unistd.h>
    
    int main(int argc, char *argv[], char *env[])  
    {  
            char *argvs[] = {"sh", "-c", "whoami"};
            execve("/bin/sh", argvs, env); 
            return 0;  
    }
    

编译运行

    
    
    ┌──(root💀toor)-[~/桌面/CodeDebug/c]
    └─# gcc CommandExec1.c -o CommandExec1                                                                                                                                          
    ┌──(root💀toor)-[~/桌面/CodeDebug/c]
    └─# ./CommandExec1  
    root
    
    ┌──(root💀toor)-[~/桌面/CodeDebug/c]
    └─#
    

同理，按照上述整个审计思路，可整理出PHP常见命令执行函数在Linux平台下的底层调用链

![](https://p1.ssl.qhimg.com/t015673e68fdb1f728b.png)

####  动态审计

除了枯燥静态审计PHP内核源码外，还可以使用更加直观的动态审计方式去动态审计PHP命令执行函数的实现原理与底层调用过程。

这里使用的调试工具为：`Visual Studio
Code`、`GDB`，针对PHP内核源码的调试，VSCode动态调试原理使用的是GDB调试器，可以理解为使用图形化界面去操作GDB来调试；而GDB调试器为纯命令行调试工具，其调试原理为通过一个`ptrace()`系统调用函数`SYS_ptrace()`来完成，系统调用号为`0x65`。

由于动态调试PHP内核源码会调用到Glibc库，所以我们也需要对Glibc进行源码调试，然而我们使用的是系统自带的Glibc。那怎么才能调试Glibc呢，比较麻烦的是以调试模式编译一份Glibc，不过我们不必这么麻烦。其实有一种很简单的方法，下载和系统Glibc相同版本的源码项目，然后在GDB配置文件中声明Glibc的源码目录，之后就可以在PHP内核源码动态调试过程中对Glibc源码进行断点调试。

这里测试的Linux系统Glibc版本为2.31，所以下载配置`glibc-2.31`源码项目即可，下面是我使用的GDB配置信息：

    
    
    └─# cat ~/.gdbinit
    #source /mnt/hgfs/QSec/Binary/PWN/Tools/GDB/peda/peda.py
    source /mnt/hgfs/QSec/Binary/PWN/Tools/GDB/pwndbg/gdbinit.py
    #source /mnt/hgfs/QSec/Binary/PWN/Tools/GDB/gef/gdbinit-gef.py
    directory /mnt/hgfs/QSec/Code-Audit/glibc/glibc-2.31/
    

**Visual Studio Code**

由于VSCode相比GDB调试简单，所以这里直接给出一些关键断点，然后给出动态调试命令执行函数的底层实现调用链。具体动态调试过程会在下面GDB调试部分叙述。

关键断点：`BreakPoints`

![](https://p3.ssl.qhimg.com/t016954ac5024be473a.png)

![](https://p4.ssl.qhimg.com/t011b71ef695b7f12ce.png)

程序完整的调用栈：`CallStack`，程序入口到底层调用

![](https://p1.ssl.qhimg.com/t012bb3a20158344d15.png)

**GDB**

启动GDB调试，加载程序

    
    
    └─# gdb --args ./php -r "system('whoami');"                                                                                            1 ⚙
    GNU gdb (Debian 10.1-1+b1) 10.1
    Copyright (C) 2020 Free Software Foundation, Inc.                                                                                          
    License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.
    Type "show copying" and "show warranty" for details.
    This GDB was configured as "x86_64-linux-gnu".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    <https://www.gnu.org/software/gdb/bugs/>.
    Find the GDB manual and other documentation resources online at:
        <http://www.gnu.org/software/gdb/documentation/>.
    
    For help, type "help".
    Type "apropos word" to search for commands related to "word"...
    pwndbg: loaded 188 commands. Type pwndbg [filter] for a list.
    pwndbg: created $rebase, $ida gdb functions (can be used with print/break)
    Reading symbols from ./php...
    pwndbg>
    

开始运行到主函数入口

    
    
    pwndbg> start
    

`system()`在PHP内核源码实现：

    
    
    /* {{{ proto int system(string command [, int &return_value])
       Execute an external program and display output */
    PHP_FUNCTION(system)
    {
        php_exec_ex(INTERNAL_FUNCTION_PARAM_PASSTHRU, 1);
    }
    /* }}} */
    

首次，对`php_exec_ex()`函数下断点

    
    
    pwndbg> b php_exec_ex
    Breakpoint 2 at 0x5555557a4942: file /mnt/hgfs/QSec/Code-Audit/PHP/PHP-Source-Code/php-7.2.9-linux-debug/ext/standard/exec.c, line 213.
    pwndbg>
    

运行至断点处：`php_exec_ex()`函数实现

    
    
    pwndbg> c
    

![](https://p1.ssl.qhimg.com/t012b6710649072daec.png)

查看`php_exec_ex()`函数源码

    
    
    pwndbg> l 209,248
    209     static void php_exec_ex(INTERNAL_FUNCTION_PARAMETERS, int mode)
    210     {
    211             char *cmd;
    212             size_t cmd_len;
    213             zval *ret_code=NULL, *ret_array=NULL;
    214             int ret;
    215
    216             ZEND_PARSE_PARAMETERS_START(1, (mode ? 2 : 3))
    217                     Z_PARAM_STRING(cmd, cmd_len)
    218                     Z_PARAM_OPTIONAL
    219                     if (!mode) {
    220                             Z_PARAM_ZVAL_DEREF(ret_array)
    221                     }
    222                     Z_PARAM_ZVAL_DEREF(ret_code)
    223             ZEND_PARSE_PARAMETERS_END_EX(RETURN_FALSE);
    224
    225             if (!cmd_len) {
    226                     php_error_docref(NULL, E_WARNING, "Cannot execute a blank command");
    227                     RETURN_FALSE;
    228             }
    229             if (strlen(cmd) != cmd_len) {
    230                     php_error_docref(NULL, E_WARNING, "NULL byte detected. Possible attack");
    231                     RETURN_FALSE;
    232             }
    233
    234             if (!ret_array) {
    235                     ret = php_exec(mode, cmd, NULL, return_value);
    236             } else {
    237                     if (Z_TYPE_P(ret_array) != IS_ARRAY) {
    238                             zval_ptr_dtor(ret_array);
    239                             array_init(ret_array);
    240                     } else if (Z_REFCOUNT_P(ret_array) > 1) {
    241                             zval_ptr_dtor(ret_array);
    242                             ZVAL_ARR(ret_array, zend_array_dup(Z_ARR_P(ret_array)));
    243                     }
    244                     ret = php_exec(2, cmd, ret_array, return_value);
    245             }
    246             if (ret_code) {
    247                     zval_ptr_dtor(ret_code);
    248                     ZVAL_LONG(ret_code, ret);
    pwndbg>
    

单步调试至`php_exec()`函数

    
    
    pwndbg> n
    

![](https://p0.ssl.qhimg.com/t016e1c2f4dcdef3947.png)

打印有关参数的值

    
    
    pwndbg> p mode
    $3 = 1
    pwndbg> p cmd
    $4 = 0x7ffff7a6eb98 "whoami"
    pwndbg>
    

进入`php_exec()`函数实现

    
    
    pwndbg> s
    

![](https://p4.ssl.qhimg.com/t01c9564026f868acba.png)

查看源码信息

    
    
    pwndbg> l
    96       */
    97      PHPAPI int php_exec(int type, char *cmd, zval *array, zval *return_value)
    98      {
    99              FILE *fp;
    100             char *buf;
    101             size_t l = 0;
    102             int pclose_return;
    103             char *b, *d=NULL;
    104             php_stream *stream;
    105             size_t buflen, bufl = 0;
    pwndbg> l
    106     #if PHP_SIGCHILD
    107             void (*sig_handler)() = NULL;
    108     #endif
    109
    110     #if PHP_SIGCHILD
    111             sig_handler = signal (SIGCHLD, SIG_DFL);
    112     #endif
    113
    114     #ifdef PHP_WIN32
    115             fp = VCWD_POPEN(cmd, "rb");
    pwndbg> 
    116     #else
    117             fp = VCWD_POPEN(cmd, "r");
    118     #endif
    119             if (!fp) {
    120                     php_error_docref(NULL, E_WARNING, "Unable to fork [%s]", cmd);
    121                     goto err;
    122             }
    123
    124             stream = php_stream_fopen_from_pipe(fp, "rb");
    125
    pwndbg>
    

结合源码及汇编代码，可知`VCWD_POPEN(cmd, "r");`函数实现为`popen[@plt](https://github.com/plt
"@plt") <popen[@plt](https://github.com/plt "@plt")>`，即glibc库函数`popen()`

单步调试汇编至call调用处

    
    
    pwndbg> si
    

![](https://p4.ssl.qhimg.com/t01fae8ccb3c74f8317.png)

进入call函数调用体：`popen[@plt](https://github.com/plt "@plt")
<popen[@plt](https://github.com/plt "@plt")>`

    
    
    pwndbg> si
    pwndbg> s
    

glibc中`popen()`函数的实现即调用`_IO_new_popen()`函数

![](https://p5.ssl.qhimg.com/t01bd39e161e7a1a6f5.png)

查看`_IO_new_popen()`函数源码

    
    
    pwndbg> l
    226         _IO_lock_t lock;
    227     #endif
    228       } *new_f;
    229       FILE *fp;
    230
    231       new_f = (struct locked_FILE *) malloc (sizeof (struct locked_FILE));
    232       if (new_f == NULL)
    233         return NULL;
    234     #ifdef _IO_MTSAFE_IO
    235       new_f->fpx.file.file._lock = &new_f->lock;
    pwndbg> l
    236     #endif
    237       fp = &new_f->fpx.file.file;
    238       _IO_init_internal (fp, 0);
    239       _IO_JUMPS (&new_f->fpx.file) = &_IO_proc_jumps;
    240       _IO_new_file_init_internal (&new_f->fpx.file);
    241       if (_IO_new_proc_open (fp, command, mode) != NULL)
    242         return (FILE *) &new_f->fpx.file;
    243       _IO_un_link (&new_f->fpx.file);
    244       free (new_f);
    245       return NULL;
    pwndbg>
    

观察`_IO_new_popen()`函数，末尾会调用`_IO_new_proc_open()`函数来执行处理系统指令，可对`_IO_new_proc_open()`函数下断点，然后运行进入`_IO_new_proc_open()`函数的实现。

    
    
    pwndbg> b _IO_new_proc_open
    Breakpoint 2 at 0x7ffff7d010f0: file iopopen.c, line 110.
    pwndbg>
    

![](https://p1.ssl.qhimg.com/t016e024dbecb7a44c2.png)

继续单步调试，`_IO_new_proc_open()`函数会调用`spawn_process()`函数

    
    
    pwndbg> l
    195       _IO_lock_lock (proc_file_chain_lock);
    196     #endif
    197       spawn_ok = spawn_process (&fa, fp, command, do_cloexec, pipe_fds,
    198                                 parent_end, child_end, child_pipe_fd);
    199     #ifdef _IO_MTSAFE_IO
    200       _IO_lock_unlock (proc_file_chain_lock);
    201       _IO_cleanup_region_end (0);
    202     #endif
    203
    204       __posix_spawn_file_actions_destroy (&fa);
    pwndbg>
    

单步调试进入`spawn_process()`函数实现

![](https://p1.ssl.qhimg.com/t015880e9ed2053df82.png)

`spawn_process()`函数会调用`__posix_spawn()`函数

    
    
    pwndbg> l
    81               child_pipe_fd, it has been already closed by the adddup2 action
    82               above.  */
    83            if (fd != child_pipe_fd
    84                && __posix_spawn_file_actions_addclose (fa, fd) != 0)
    85              return false;
    86          }
    87
    88        if (__posix_spawn (&((_IO_proc_file *) fp)->pid, _PATH_BSHELL, fa, 0,
    89                           (char *const[]){ (char*) "sh", (char*) "-c",
    90                           (char *) command, NULL }, __environ) != 0)
    pwndbg>
    

单步汇编调试至`__posix_spawn()`函数调用处

    
    
    pwndbg> si
    

![](https://p2.ssl.qhimg.com/t014d5e4219ee2e911e.png)

可以看到`__posix_spawn()`函数被传入的参数：`sh -c
command`，可以判断php命令执行函数，底层会调用`sh`来执行系统指令，进入`__posix_spawn()`函数实现

    
    
    pwndbg> si
    

![](https://p3.ssl.qhimg.com/t01b93838e6653baa0d.png)

`__posix_spawn()`函数实现直接调用的`__spawni()`函数，单步步入调试进入`__spawni()`函数

    
    
    pwndbg> s
    

![](https://p5.ssl.qhimg.com/t013751dfca9d06b6c2.png)

`__spawni()`函数实现调用`__spawnix()`函数，单步步入调试进入`__spawnix()`函数

![](https://p4.ssl.qhimg.com/t015f210542fafd93b4.png)

`__spawnix()`函数的核心代码：克隆父进程，为后续`/bin/sh`子进程的创建做准备

    
    
    pwndbg> l
    382       new_pid = CLONE (__spawni_child, STACK (stack, stack_size), stack_size,
    383                        CLONE_VM | CLONE_VFORK | SIGCHLD, &args);
    384
    385       /* It needs to collect the case where the auxiliary process was created
    386          but failed to execute the file (due either any preparation step or
    387          for execve itself).  */
    388       if (new_pid > 0)
    389         {
    390           /* Also, it handles the unlikely case where the auxiliary process was
    391              terminated before calling execve as if it was successfully.  The
    pwndbg>
    

在`CLONE()`函数处下断点，并进入`CLONE()`函数的实现：函数的实现为汇编代码

![](https://p3.ssl.qhimg.com/t016326651673a8f928.png)

对`clone()`函数汇编代码进行单步汇编调试：`clone()`函数是一个系统调用函数，内核入口为`sys_clone()`，调用号为`0x38`

![](https://p0.ssl.qhimg.com/t01c85830329c9a65bf.png)

继续单步汇编步入，执行系统调用

    
    
    pwndbg> si
    [Attaching after process 48284 vfork to child process 48289]
    [New inferior 2 (process 48289)]
    [Switching to process 48289]
    clone () at ../sysdeps/unix/sysv/linux/x86_64/clone.S:79
    79              jl      SYSCALL_ERROR_LABEL
    LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
    ─────────────────────────────────────────────────────────[ REGISTERS ]─────────
     RAX  0x0
     RBX  0x4
     RCX  0x7ffff7d88d81 (clone+49) ◂— test   rax, rax
     RDX  0xffffffff
     RDI  0x4111
     RSI  0x7ffff7c14ff0 —▸ 0x7ffff7d789d0 (__spawni_child) ◂— push   rbp
     R8   0x0
     R9   0x0
     R10  0x7ffff7e15156 ◂— 0x68732f6e69622f /* '/bin/sh' */
     R11  0x306
     R12  0x7ffff7c0c000 ◂— 0x0
     R13  0x7fffffffc480 —▸ 0x7ffff7e1515b ◂— 0x2074697865006873 /* 'sh' */
     R14  0x7fffffffc190 ◂— 0x0
     R15  0x7ffff7d56660 (execve) ◂— mov    eax, 0x3b
     RBP  0x9000
     RSP  0x7ffff7c14ff0 —▸ 0x7ffff7d789d0 (__spawni_child) ◂— push   rbp
     RIP  0x7ffff7d88d84 (clone+52) ◂— jl     0x7ffff7d88d99
    ─────────────────────────────────────────────────[ DISASM ]───────────────────────────
       0x7ffff7d88d72 <clone+34>    mov    r8, r9
       0x7ffff7d88d75 <clone+37>    mov    r10, qword ptr [rsp + 8]
       0x7ffff7d88d7a <clone+42>    mov    eax, 0x38
       0x7ffff7d88d7f <clone+47>    syscall 
       0x7ffff7d88d81 <clone+49>    test   rax, rax
     ► 0x7ffff7d88d84 <clone+52>    jl     clone+73 <clone+73>
    
       0x7ffff7d88d86 <clone+54>    je     clone+57 <clone+57>
        ↓
       0x7ffff7d88d89 <clone+57>    xor    ebp, ebp
       0x7ffff7d88d8b <clone+59>    pop    rax
       0x7ffff7d88d8c <clone+60>    pop    rdi
       0x7ffff7d88d8d <clone+61>    call   rax
    ──────────────────────────────────────────────────[ SOURCE (CODE) ]─────────────────────────
    In file: /mnt/hgfs/QSec/Code-Audit/glibc/glibc-2.31/sysdeps/unix/sysv/linux/x86_64/clone.S
       74      wrong.  */
       75   cfi_endproc;
       76   syscall
       77 
       78   testq   %rax,%rax
     ► 79   jl      SYSCALL_ERROR_LABEL
       80   jz      L(thread_start)
       81 
       82   ret
       83 
       84 L(thread_start):
    

clone函数作用，创建子进程：克隆父进程

![](https://p5.ssl.qhimg.com/t01952ca588b18b8063.png)

接着clone函数内部会调用`__spawni_child()`函数，将克隆的子进程给真正起起来

![](https://p3.ssl.qhimg.com/t0159f2b923d22b4143.png)

单步汇编步入`__spawni_child`函数实现

![](https://p4.ssl.qhimg.com/t018b193f1172f09b86.png)

`__spawni_child`函数内部会动态调用`execve()`函数，最终来将子进程给启动起来

![](https://p5.ssl.qhimg.com/t01dceb893e6540e6fc.png)

步入`execve()`函数的实现：函数实现为汇编代码`sysdeps/unix/syscall-template.S`。`execve()`函数为系统调用函数，内核入口为`sys_execve()`，系统调用号为`0x3b`

![](https://p5.ssl.qhimg.com/t01d64dfae9625bc328.png)

这里如果继续单步汇编步入，就会导致执行`execve()`函数系统调用，成功创建子进程，同时GDB调试就会完成，输出程序的执行结果。因为，这里并没有捕捉创建子进程这一事件，无法对创建的子进程进行调试，从而导致程序的执行完毕。

为了避免这一结果发生，我们可以在`execve()`函数系统调用前，设置捕捉点用来补捉程序运行时的一些事件：这里捕捉系统调用事件`execve`

    
    
    pwndbg> catch syscall execve
    

捕捉点设置完毕后，就可以步入执行`execve()`函数系统调用，查看此时的所有进程的栈调用情况

![](https://p3.ssl.qhimg.com/t0108f2ad1f43d1448a.png)

执行`execve()`函数系统调用：成功创建子进程`/bin/sh->/bin/dash`

![](https://p5.ssl.qhimg.com/t0191a7f53cfb1d708a.png)

此时GDB调试已进入`/bin/sh`进程中

![](https://p5.ssl.qhimg.com/t0113628e27adfe8241.png)

后续工作执行未执行完的`sh -c
Command`，在`/bin/sh`进程中执行`Command`指令（内部|外部），外部指令则会在`/bin/sh`进程下启动相应的子进程。

最后，这里也可以通过Linux下`strace`工具来追踪PHP命令执行函数的底层调用执行情况：

  * PHP命令执行函数底层系统调用函数统计

    
    
    └─# strace -f -c ./php -r "system('whoami');"      
    strace: Process 48432 attached
    strace: Process 48433 attached
    root
    % time     seconds  usecs/call     calls    errors syscall
    ------ ----------- ----------- --------- --------- ----------------      0.00    0.000000           0        14           read
      0.00    0.000000           0         2           write
      0.00    0.000000           0        23           close
      0.00    0.000000           0         7         4 stat
      0.00    0.000000           0        24           fstat
      0.00    0.000000           0        10           lstat
      0.00    0.000000           0         5         3 lseek
      0.00    0.000000           0        49           mmap
      0.00    0.000000           0        17           mprotect
      0.00    0.000000           0        12           munmap
      0.00    0.000000           0        14           brk
      0.00    0.000000           0       206           rt_sigaction
      0.00    0.000000           0         5           rt_sigprocmask
      0.00    0.000000           0         1           rt_sigreturn
      0.00    0.000000           0         4         3 access
      0.00    0.000000           0         1           madvise
      0.00    0.000000           0         1           dup2
      0.00    0.000000           0         1           getpid
      0.00    0.000000           0         2           socket
      0.00    0.000000           0         2         2 connect
      0.00    0.000000           0         2           clone
      0.00    0.000000           0         3           execve
      0.00    0.000000           0         2           wait4
      0.00    0.000000           0         1           fcntl
      0.00    0.000000           0         2           getcwd
      0.00    0.000000           0         1           getuid
      0.00    0.000000           0         1           getgid
      0.00    0.000000           0         3           geteuid
      0.00    0.000000           0         1           getegid
      0.00    0.000000           0         1           getppid
      0.00    0.000000           0         3           arch_prctl
      0.00    0.000000           0        20         4 openat
      0.00    0.000000           0         1           pipe2
      0.00    0.000000           0         3           prlimit64
    ------ ----------- ----------- --------- --------- ----------------    100.00    0.000000                   444        16 total
    
    └─#
    

  * PHP命令执行函数底层创建进程情况

    
    
    └─# strace -f -e execve php -r "system('whoami');"
    execve("/usr/bin/php", ["php", "-r", "system('whoami');"], 0x7ffe259e22c8 /* 53 vars */) = 0
    strace: Process 48440 attached
    [pid 48440] execve("/bin/sh", ["sh", "-c", "whoami"], 0x56260233beb0 /* 53 vars */) = 0
    strace: Process 48441 attached
    [pid 48441] execve("/usr/bin/whoami", ["whoami"], 0x563b845c2ed8 /* 53 vars */) = 0
    root
    [pid 48441] +++ exited with 0 +++
    [pid 48440] --- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=48441, si_uid=0, si_status=0, si_utime=0, si_stime=0} ---    [pid 48440] +++ exited with 0 +++
    --- SIGCHLD {si_signo=SIGCHLD, si_code=CLD_EXITED, si_pid=48440, si_uid=0, si_status=0, si_utime=0, si_stime=0} ---    +++ exited with 0 +++
    

## 总结

该系列文章主要是讲述不同平台下PHP语言命令执行函数的底层实现与分析。而有关其它语言(Python、Java等)这里不在讲述分析，因为针对不同语言的分析思路都是一样的，归结到系统底层调用：大差不差（PHP和Python底层调用原理类似；Java与PHP和Python相比，少了一步系统可执行终端调用）。

## 参考链接

  * [Build your own PHP on Windows](https://wiki.php.net/internals/windows/stepbystepbuild_sdk_2)
  * [Visual Studio docs](https://visualstudio.microsoft.com/zh-hans/vs/)
  * [Visual Studio Code docs](https://code.visualstudio.com/docs)
  * [《PHP 7底层设计与源码实现+PHP7内核剖析》](https://item.jd.com/28435383700.html)
  * [深入理解 PHP 内核](https://www.bookstack.cn/books/php-internals)
  * [WINDOWS下用VSCODE调试PHP7源代码](https://www.jianshu.com/p/29bc0443b586)
  * [调式PHP源码](https://gywbd.github.io/posts/2016/2/debug-php-source-code.html)
  * [用vscode调试php源码](https://blog.csdn.net/Dont_talk/article/details/107719466)
  * [GDB: The GNU Project Debugger](http://www.gnu.org/software/gdb)
  * [CreateProcessW function](https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)
  * [命令注入成因小谈](https://xz.aliyun.com/t/6542)
  * [浅谈从PHP内核层面防范PHP WebShell](https://paper.seebug.org/papers/old_sebug_paper/pst_WebZine/pst_WebZine_0x05/0x07_%E6%B5%85%E8%B0%88%E4%BB%8EPHP%E5%86%85%E6%A0%B8%E5%B1%82%E9%9D%A2%E9%98%B2%E8%8C%83PHP_WebShell.html)
  * [Program execution Functions](https://www.php.net/manual/en/ref.exec.php)
  * [linux系统调用](http://huhaipeng.top/2019/04/20/linux%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8/)
  * [system calls](https://fedora.juszkiewicz.com.pl/syscalls.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Qftm** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/226295](/post/id/226295)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [命令执行](/tag/命令执行)
  * [PHP](/tag/PHP)
  * [系统安全](/tag/系统安全)
  * [内核源码](/tag/内核源码)

 **+1** __8赞

 __收藏

![](https://p1.ssl.qhimg.com/t01c308d93cb785d60b.png) Qftm

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

