***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **在这篇文章中，我们将跟大家分析Linux平台中create_elf_tables函数的一个整型溢出漏洞（CVE-2018-14634）。**

![777777777777777777.png](https://image.3001.net/images/20181221/1545380051_5c1ca0d35a118.png!small)

## 概述

在近期的一次安全分析过程中，我们在64位Linux系统内核里的create_elf_tables()函数中发现了一个整型溢出漏洞，本地攻击者将可以通过一份SUID-root代码来利用这个漏洞，并获取到目标设备的完整root权限。

目前，受该漏洞影响的Linux发行版有Red Hat Linux企业版、CentOS和Debian 8。

## 漏洞分析

    
    
    150#define STACK_ROUND(sp, items) \
    
     151         (((unsigned long) (sp - items)) &~15UL)
    
     ...
    
     165 create_elf_tables(struct linux_binprm*bprm, struct elfhdr *exec,
    
     ...
    
     169        int argc = bprm->argc;
    
     170        int envc = bprm->envc;
    
     171        elf_addr_t __user *sp;
    
     ...
    
     178        int items;
    
     ...
    
     190        p = arch_align_stack(p);
    
     ...
    
     287        items = (argc + 1) + (envc + 1) + 1;
    
     288        bprm->p = STACK_ROUND(sp, items);
    
     ...
    
     295        sp = (elf_addr_t __user *)bprm->p;

“argc”表示传递给execve()系统调用的命令行参数个数，个数受fs/exec.c中MAX_ARG_STRINGS的限制；“envc”表示传递给execve()的环境变量个数，个数同样受到MAX_ARG_STRINGS的限制；但是由于MAX_ARG_STRINGS为0x7FFFFFFF，所以我们可以让整数“items”发生溢出并让程序失效。

此时，我们就可以以增加用户态的栈指针，然后将用户态栈指针指向我们的参数和环境变量字符串，最终在用户模式执行SUID-root代码时重写这些字符串。

## 漏洞利用

在使用execve()运行SUID-root代码时，我们的“items”值为0x80000000，参数指针的大小约为0x80000000 *
sizeof(char *) = 16GB，参数字符串为16GB，环境字符串也为16GB，因此我们的漏洞利用环境“只”需要2 * 16GB =
32GB内存，而并非3 * 16GB = 48GB或者更多，因为我们使用了一些小技巧来减少内存指纹。

下面这个图表代表了SUID-root代码开始执行后，我们的用户态栈结构：

![888888888888.png](https://image.3001.net/images/20181221/1545380144_5c1ca130b6d59.png!small)

> -“A”（“alpha”）为create_elf_tables()分配的栈空间大小（代码190-287行），大约为512字节。
>
> -“sprand”是create_elf_tables()分配的随机栈空间大小（代码190行），大小范围在0-8192字节之间。
>
> -“protect”参数字符串是一个非常重要的命令行参数&选项，这个参数必须不能受到内存崩溃的影响。
>
> -“padding”参数字符串大约需要占用16GB栈空间。
>
> -“protect”环境字符串是一个重要的环境变量，必须必须不能受到内存崩溃的影响。
>
> -“scratch”环境字符串为1MB。
>
> -“onebyte”环境字符串为256KB，其部分数据会被fname[]缓冲区覆盖。
>
> -“B”（“beta”）为ld.so分配的栈空间数量。

此时，ld.so会使用handle_ld_preload()中fname[]缓冲区的数据重写“onebyte”环境变量中的部分数据，并让process_envvars()中的UNSECURE_ECVVARS等过滤器失效。

我们的POC代码能够利用create_elf_tables()中的这个整型溢出漏洞，演示样例如下：

    
    
    # gcc-O0 -o poc-suidbin poc-suidbin.c
    
    #chown root poc-suidbin
    
    #chmod 4555 poc-suidbin
    
     
    
    $ gcc-o poc-exploit poc-exploit.c
    
    $time ./poc-exploit
    
    ...
    
    ERROR:ld.so: object 'LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.' fromLD_PRELOAD cannot be preloaded: 
    
    ignored.
    
    ERROR:ld.so: object 'LD_LIBRARY_PATH=.0LD_LIBRARY_PATH=.' from LD_PRELOAD cannot bepreloaded: ignored.
    
    ERROR:ld.so: object 'LD_LIBRARY_PATH=.' from LD_PRELOAD cannot be preloaded: ignored.
    
    argc2147090419
    
    stack0x7ffbe115008f < 0x7ffbe1150188 < 0x7fffe0e50128 < 0x7ff7e11503ea <0x7ffbe102cdea
    
    getenv0x7ffbe114d83b .
    
    0x7ffbe114d82bLD_LIBRARY_PATH=.
    
    0x7ffbe114df60LD_LIBRARY_PATH=.
    
    0x7ffbe114df72LD_LIBRARY_PATH=.
    
    ...
    
    0x7ffbe114e69eLD_LIBRARY_PATH=.
    
    0x7ffbe114e6b0LD_LIBRARY_PATH=.
    
    0x7ffbe114e6c2LD_LIBRARY_PATH=.
    
     
    
    real    5m38.666s
    
    user    0m0.049s
    
    sys     1m57.828s

### 附件

> poc-> suidbin.c：【[点我下载](https://seclists.org/fulldisclosure/2018/Sep/att-54/poc-> suidbin_c.bin)】
>
> poc-> exploit.c：【[点我下载](https://seclists.org/fulldisclosure/2018/Sep/att-54/poc-> exploit_c.bin)】

***参考来源：[seclists](https://seclists.org/fulldisclosure/2018/Sep/54)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

