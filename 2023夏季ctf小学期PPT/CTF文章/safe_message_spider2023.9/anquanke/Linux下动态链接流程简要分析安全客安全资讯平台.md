# Linux下动态链接流程简要分析

阅读量 **311292**

|评论 **16**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-15 11:00:40

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

在CTF
PWN中对于Linux底层的考察是很多的，而应用程序如何进行动态链接对于新手来说算是一个小考验，本篇文章主要记录Linux下动态链接的过程以及CTF中关于动态链接的注意点，还有Glibc版本不兼容的坑

## 内核加载ELF

我们都知道应用程序要从C语言代码变成机器可以直接执行的代码要经过编译链接的步骤。在链接中有两种方式，一种是静态链接，一种是动态链接。

  * 1.静态链接指的就是程序在链接的过程中，将需要用到的库文件的二进制代码拷贝到程序二进制文件的映像中。
  * 2.动态链接指的就是程序在链接的时候并不把库函数链接进程序的映像而是将库函数的映像一起交给用户，用户在运行的时候使用一个叫解释器的东西形如：ld.linux.so的文件进行动态的加载库函数  
Linux下编译链接过程：  

在Linux中，启动和加载ELF文件必须在内核中完成，而动态链接在用户空间（glibc），所以我们第一步就是看Linux内核空间如何加载ELF

###  可执行文件类型的注册机制

内核对所支持的每种可执行的程序类型都有个struct linux_binfmt的结构体

    
    
    /*
      * This structure defines the functions that are used to load the binary formats that
      * linux accepts.
      */
    struct linux_binfmt {
        struct list_head lh;
        struct module *module;
        int (*load_binary)(struct linux_binprm *);
        int (*load_shlib)(struct file *);
        int (*core_dump)(struct coredump_params *cprm);
        unsigned long min_coredump;     /* minimal dump size */
     };
    

在上面的代码中我们可以看到Linux内核提供了3种方法来加载和执行可执行程序

函数 | 描述  
---|---  
load_binary | 通过读存放在可执行文件中的信息为当前进程建立一个新的执行环境  
load_shlib | 用于动态的把一个共享库捆绑到一个已经在运行的进程, 这是由uselib()系统调用激活的  
core_dump | 在名为core的文件中, 存放当前进程的执行上下文. 这个文件通常是在进程接收到一个缺省操作为”dump”的信号时被创建的,
其格式取决于被执行程序的可执行类型  
  
要支持ELF文件的运行，则必须向内核登记注册elf_format这个linux_binfmt类型的数据结构

    
    
    static struct linux_binfmt elf_format = {
        .module      = THIS_MODULE,
        .load_binary = load_elf_binary,
        .load_shlib      = load_elf_library,
        .core_dump       = elf_core_dump,
        .min_coredump    = ELF_EXEC_PAGESIZE,
        .hasvdso     = 1
    };
    

> 结构体名称前加小数点是一种对结构体初始化的方法，还有一些别的初始化方法，但是在内核中广泛使用的是这种方法

内核提供两个函数来完成这个功能，一个注册，一个注销，即：

    
    
    int register_binfmt(struct linux_binfmt * fmt)
    int unregister_binfmt(struct linux_binfmt * fmt)
    

当需要运行一个程序时，则扫描这个队列，依次调用各个数据结构所提供的load处理程序来进行加载工作，ELF中加载程序即为load_elf_binary，内核中已经注册的可运行文件结构linux_binfmt会让其所属的加载程序load_binary逐一前来认领需要运行的程序binary，如果某个格式的处理程序发现相符后，便执行该格式映像的装入和启动.

###  load_elf_binary函数

load_elf_binary函数处理的流程主要有以下几步：

  * 填充并且检查目标程序ELF头部
  * load_elf_phdrs加载目标程序的程序头表
  * 如果需要动态链接, 则寻找和处理解释器段
  * 检查并读取解释器的程序表头
  * 装入目标程序的段segment
  * create_elf_tables填写目标文件的参数环境变量等必要信息
  * start_kernel宏准备进入新的程序入口

####  填充并且检查目标程序ELF头部

    
    
    struct pt_regs *regs = current_pt_regs();
    struct {
        struct elfhdr elf_ex;
        struct elfhdr interp_elf_ex;
    } *loc;
    struct arch_elf_state arch_state = INIT_ARCH_ELF_STATE;
    
    loc = kmalloc(sizeof(*loc), GFP_KERNEL);
    if (!loc) {
        retval = -ENOMEM;
        goto out_ret;
    }
    
    /* Get the exec-header
        使用映像文件的前128个字节对bprm->buf进行了填充  */
    loc->elf_ex = *((struct elfhdr *)bprm->buf);
    
    retval = -ENOEXEC;
    /* First of all, some simple consistency checks
        比较文件头的前四个字节
        。*/
    if (memcmp(loc->elf_ex.e_ident, ELFMAG, SELFMAG) != 0)
        goto out;
    /*  还要看映像的类型是否ET_EXEC和ET_DYN之一；前者表示可执行映像，后者表示共享库  */
    if (loc->elf_ex.e_type != ET_EXEC && loc->elf_ex.e_type != ET_DYN)
        goto out;
    

####  通过load_elf_phdrs加载目标程序的程序头表

    
    
    elf_phdata = load_elf_phdrs(&loc->elf_ex, bprm->file);
    if (!elf_phdata)
        goto out;
    
    
    
    /**
     * load_elf_phdrs() - load ELF program headers
     * @elf_ex:   ELF header of the binary whose program headers should be loaded
     * @elf_file: the opened ELF binary file
     *
     * Loads ELF program headers from the binary file elf_file, which has the ELF
     * header pointed to by elf_ex, into a newly allocated array. The caller is
     * responsible for freeing the allocated data. Returns an ERR_PTR upon failure.
     */
    static struct elf_phdr *load_elf_phdrs(struct elfhdr *elf_ex,
                                       struct file *elf_file)
    {
        struct elf_phdr *elf_phdata = NULL;
        int retval, size, err = -1;
    
        /*
         * If the size of this structure has changed, then punt, since
         * we will be doing the wrong thing.
         */
        if (elf_ex->e_phentsize != sizeof(struct elf_phdr))
                goto out;
    
        /* Sanity check the number of program headers... */
        if (elf_ex->e_phnum < 1 ||
                elf_ex->e_phnum > 65536U / sizeof(struct elf_phdr))
                goto out;
    
        /* ...and their total size. */
        size = sizeof(struct elf_phdr) * elf_ex->e_phnum;
        if (size > ELF_MIN_ALIGN)
                goto out;
    
        elf_phdata = kmalloc(size, GFP_KERNEL);
        if (!elf_phdata)
                goto out;
    
        /* Read in the program headers */
        retval = kernel_read(elf_file, elf_ex->e_phoff,
                             (char *)elf_phdata, size);
        if (retval != size) {
                err = (retval < 0) ? retval : -EIO;
                goto out;
        }
    
        /* Success! */
        err = 0;
    out:
        if (err) {
                kfree(elf_phdata);
                elf_phdata = NULL;
        }
        return elf_phdata;
    }
    

####  如果需要动态链接, 则寻找和处理解释器段

    
    
    for (i = 0; i < loc->elf_ex.e_phnum; i++) {
            /*  3.1  检查是否有需要加载的解释器  */
            if (elf_ppnt->p_type == PT_INTERP) {
                /* This is the program interpreter used for
                 * shared libraries - for now assume that this
                 * is an a.out format binary
                 */
    
                /*  3.2 根据其位置的p_offset和大小p_filesz把整个"解释器"段的内容读入缓冲区  */
                retval = kernel_read(bprm->file, elf_ppnt->p_offset,
                             elf_interpreter,
                             elf_ppnt->p_filesz);
    
                if (elf_interpreter[elf_ppnt->p_filesz - 1] != '')
                    goto out_free_interp;
                /*  3.3 通过open_exec()打开解释器文件 */
                interpreter = open_exec(elf_interpreter);
    
    
    
                /* Get the exec headers 
                   3.4  通过kernel_read()读入解释器的前128个字节，即解释器映像的头部。*/
                retval = kernel_read(interpreter, 0,
                             (void *)&loc->interp_elf_ex,
                             sizeof(loc->interp_elf_ex));
    
    
                break;
            }
            elf_ppnt++;
        }
    

“解释器”段实际上只是一个字符串，即解释器的文件名，如”/lib/ld-linux.so.2”, 或者64位机器上对应的叫做”/lib64/ld-linux-x86-64.so.2”。有了解释器的文件名以后，就通过open_exec()打开这个文件，再通过kernel_read()读入其开关128个字节，即解释器映像的头部  
我在自己的Ubuntu18上做一个演示

![](https://p0.ssl.qhimg.com/dm/1024_560_/t01334c4c25a9d63661.png)

其中INTERP段标识了我们程序所需要的解释器

####  检查并读取解释器的程序表头

需要加载解释器, 前面的for循环已经找到了需要的解释器信息elf_interpreter, 解释器同样是一个ELF文件, 因此跟目标可执行程序一样,
我们需要load_elf_phdrs加载解释器的程序头表program header table

    
    
    /* Some simple consistency checks for the interpreter */
    
    if (elf_interpreter) {
    retval = -ELIBBAD;
    /* Not an ELF interpreter */
    
    /* Load the interpreter program headers */
    interp_elf_phdata = load_elf_phdrs(&loc->interp_elf_ex,
                       interpreter);
    if (!interp_elf_phdata)
        goto out_free_dentry;
    

####  装入目标程序的段segment

先遍历每个段，找到类型为PT_LOAD的段，检查地址和页面的信息，确定装入地址后，通过elf_map()建立用户空间虚拟地址与目标映像文件中某个连续区间的映射，返回值就是实际映射的起始地址。

    
    
    for(i = 0, elf_ppnt = elf_phdata;
        i < loc->elf_ex.e_phnum; i++, elf_ppnt++) {
    
        /*  5.1   搜索PT_LOAD的段, 这个是需要装入的 */
        if (elf_ppnt->p_type != PT_LOAD)
            continue;
    
    
            /* 5.2  检查地址和页面的信息  */
            ////////////
            // ......
            ///////////
    
         /*  5.3  虚拟地址空间与目标映像文件的映射
         确定了装入地址后，
         就通过elf_map()建立用户空间虚拟地址空间
         与目标映像文件中某个连续区间之间的映射，
         其返回值就是实际映射的起始地址 */
        error = elf_map(bprm->file, load_bias + vaddr, elf_ppnt,
                elf_prot, elf_flags, total_size);
    
        }
    

####  填写程序的入口地址

如果需要动态链接，就通过load_elf_interp装入解释器映像,
并把将来进入用户空间的入口地址设置成load_elf_interp()的返回值，即解释器映像的入口地址。  
而若不需要装入解释器，那么这个入口地址就是目标映像本身的入口地址

    
    
    if (elf_interpreter) {
        unsigned long interp_map_addr = 0;
    
        elf_entry = load_elf_interp(&loc->interp_elf_ex,
                    interpreter,
                    &interp_map_addr,
                    load_bias, interp_elf_phdata);
        /*  入口地址是解释器映像的入口地址  */
        } else {
        /*  入口地址是目标程序的入口地址  */
        elf_entry = loc->elf_ex.e_entry;
        }
    }
    

####  填写目标文件的参数环境变量等必要信息

通过create_elf_tables，为目标映像和解释器准备一些有关的信息，包括argc、envc等，这些信息需要复制到用户空间，使它们在CPU进入解释器或目标映像的程序入口时出现在用户空间堆栈上。

    
    
        install_exec_creds(bprm);
        retval = create_elf_tables(bprm, &loc->elf_ex,
                  load_addr, interp_load_addr);
        if (retval < 0)
            goto out;
        /* N.B. passed_fileno might not be initialized? */
        current->mm->end_code = end_code;
        current->mm->start_code = start_code;
        current->mm->start_data = start_data;
        current->mm->end_data = end_data;
        current->mm->start_stack = bprm->p;
    

####  start_thread宏准备进入新的程序入口

start_thread()这个宏操作会将eip和esp改成新的地址，就使得CPU在返回用户空间时就进入新的程序入口。如果存在解释器映像，那么这就是解释器映像的程序入口，否则就是目标映像的程序入口。那么什么情况下有解释器映像存在，什么情况下没有呢？如果目标映像与各种库的链接是静态链接，因而无需依靠共享库、即动态链接库，那就不需要解释器映像；否则就一定要有解释器映像存在。

## 解释器完成动态链接

前面的工作都是在内核完成的，接下来会回到用户空间。  
接下来按照解释器的工作流程进行分析

###  1.解释器检查可执行程序所依赖的共享库

根据上文讲的内核会读取ELF文件头部的INTERP字段，这里面存储着程序所需要的解释器名称

![](https://p1.ssl.qhimg.com/dm/1024_98_/t018d8ea2ecffa0459b.png)

ELF 文件有一个特别的段：
.dynamic，它存放了和动态链接相关的很多信息，比如依赖于哪些共享对象，动态链接符号表的位置，动态链接重定位表的位置，共享对象初始化代码的地址等，动态链接器通过它找到该文件使用的动态链接库。

![](https://p3.ssl.qhimg.com/dm/1024_137_/t011bb76a8204e61c8d.png)

Linux下可以用ldd命令查看文件所需要的共享库信息

###  2.解释器对程序的外部引用进行重定位

解释器对程序的外部引用进行重定位，并告诉程序其引用的外部变量/函数的地址，此地址位于共享库被加载在内存的区间内。动态链接还有一个延迟定位的特性，即只有在“真正”需要引用符号时才重定位，这对提高程序运行效率有极大帮助。延迟定位有些地方也叫延迟绑定，这个在后面讲PLT和GOT的时候再详细讲。  
符号，也就是可执行程序代码段中的变量名、函数名等。重定位是将符号引用与符号定义进行链接的过程，对符号的引用本质是对其在内存中具体地址的引用，所以本质上来说，符号重定位要解决的是当前编译单元如何访问外部符号这个问题。动态链接是在程序运行时对符号进行重定位，也叫运行时重定位（而静态链接则是在编译时进行，也叫链接时重定位）

####  动态符号表：

为了表示动态链接这些模块之间的符号导入导出关系，ELF专门有个动态符号表.dynsym。它只保存与动态链接相关的符号，对于哪些模块内部的符号，比如模块私有变量则不保存。很多动态链接模块同时拥有.symtab和.dynsym。.symtab保存了所有符号，包含.dynsym中的符号。  
对应还有动态符号字符串表.dynstr和为了加快符号查找的符号哈希表。

![](https://p0.ssl.qhimg.com/dm/1024_368_/t012d47adb0dd96348f.png)

![](https://p5.ssl.qhimg.com/dm/995_1024_/t01196200692e1a2c85.png)

###  3.延迟绑定

前面已经讲过了动态链接和静态链接的定义。动态链接比静态链接灵活，但牺牲了性能，优点就是二进制文件的体积明显减小了，而动态链接速度慢的主要原因是，动态链接下对于全局和静态数据的访问都要进行复杂的GOT定位，然后间接寻址，对于模块间的调用也要先定位GOT，然后进行间接跳转。  
另外，动态链接的链接过程是在运行时完成的，动态链接器会寻找并转载所需要的对象，然后进行符号查找地址重定位等工作。  
因为很多函数可能在程序执行完时都不会被用到，比如错误处理函数或一些用户很少用到的功能模块等，那么一开始就把所有函数都链接好实际是一种浪费，因此ELF采用了一种延迟绑定（Lazy
Binding），就是在当函数第一次被用到时才进行绑定（符号查找，重定位等），如果没有用到则不进行绑定。  
我使用一个简单的小程序演示一下延迟绑定

    
    
    #include<stdio.h>
    int main()
    {
        int a;
        scanf("%d",&a);
        printf("%dn",a);
        int b = 1;
        printf("%dn",b);
    }
    
    
    
    gcc -o test a.c
    

ELF使用PLT（Procedure Linkage Table）的方法来实现延迟绑定，使用一些很精妙的指令序列来完成。

![](https://p4.ssl.qhimg.com/dm/1024_737_/t018311dcf85c751a48.png)

先使用objdump查看二进制的汇编，我们可以看到在scanf,printf位置call指令的操作数明显不是一个函数的地址，这是因为程序还没有运行起来，所有还不知道具体的函数位置，先放一个符号在这里。  
那么程序在运行的时候就可以将这里的符号修改成真正的地址，就要用到两个表，存放函数地址的数据表，称为重局偏移表（GOT, Global Offset
Table），而那个额外代码段表，称为程序链接表（PLT，Procedure Link Table）。

我们使用GDB来调试下

![](https://p5.ssl.qhimg.com/dm/1024_133_/t01e470e54440773a44.png)

这时候程序运行到了scanf函数的位置，这里显示的是scanf_plt这就说明了这其实不是真正的scanf函数地址，而是scanf_plt的地址，那我们看看这个plt里面有什么  
简单来说就是两个跳转一个压栈，第一个跳转实质是跳转到了GOT

![](https://p0.ssl.qhimg.com/dm/1024_176_/t01c930fdfc36791486.png)

我们可以看到这个时候GOT里面存的就是PLT跳转时下一条指令的地址，也就是压栈的地址

![](https://p0.ssl.qhimg.com/dm/1024_70_/t01406cd58be3e24d2e.png)

然后程序跳转到了0x8048300的位置

![](https://p0.ssl.qhimg.com/dm/1024_139_/t01c393e5f5644ca6db.png)

这里是为了执行_dl_runtime_resolve函数，_dl_runtime_resolve会讲真正的scanf函数的地址写到scanf函数GOT的位置  
所以根据上面的分析，程序第一次执行一个函数的时候流程如下  
  
继续向下执行，程序会同样进行延迟绑定第一次执行的printf函数，当我们第二次来到printf函数的时候，情况就会和上面的不同

![](https://p5.ssl.qhimg.com/dm/1024_52_/t012835342b979e7d2b.png)

我们看到GOT表里已经存储了printf函数真正的位置  
下面我来说下我在实际调试时遇到的坑  
首先我使用的环境是Ubuntu18.04 可以看到下面这个图

如果我直接使用gcc这个命令，程序的保护是全开的，所以就会遇到下面这个情况

![](https://p1.ssl.qhimg.com/t01ed2f1247ce9d26b3.png)

第一次执行scanf的时候就会发现GOT里填写的就已经是真正的地址了  
所以我在上面的调试中，加入了不开启任何保护的这个命令，就可以验证延迟绑定

    
    
    gcc -o test -fno-stack-protector -z execstack -no-pie -z norelro -m32 a.c
    

![](https://p3.ssl.qhimg.com/dm/1024_299_/t01d23165b8f56525d0.png)

## CTF 中的延迟绑定考点

###  不开启RELRO

如果没有开启RELRO，就代表我们可以对GOT表进行修改，所以就有了很多常见的攻击方式，比如GOT表劫持，实现的方法可以是触发堆中的漏洞，实现任意地址写任意内容，我们可以将一些函数的GOT表里填写system函数的地址

###  开启RELRO

如果开启了RELRO，GOT表字段就是只读的，我们就不能再用上面的方法，常用的方法是修改malloc_hook或者free_hook，将这两个中的一个修改成one_gadget的地址

## 任意切换程序libc版本

因为在CTF题中，可能有的题是使用glibc2.27有的题是使用2.23还有使用2.26的，不同版本对一些细节是不一样的，有时候这些细节就是考点，比如teache等，但是如果现在只有Ubuntu18的环境，要想同时进行上面那么多版本的调试是很困难的，通常就要搭好几个环境。我在这里介绍一个很方便的方法  
GitHub上有一个​ gfree-libc的项目

###  安装

    
    
    1，git clone git@github.com:dsyzy/gfree-libc.git
    2，cd gfree-libc
    3，sudo sh ./install.sh
    

###  添加想要源码级别调试的libc版本

    
    
    build 2.27(2.27可以换成你需要的版本)
    

这个过程很慢，因为需要在本地编译好整个libc环境，通常要等5-10分钟

###  指定加载版本

    
    
    gclibc 程序名 libc版本 [指定libc]
    其中，指定libc需放在和程序一样目录下
    
    示例
    gclibc test 2.24
    这样test就加载了libc-2.24版本，并且是libc-2.24版本的源代码
    
    如果需要指定libc，如libc.so,前提你已经知道libc版本
    示例
    gclibc test 2.24 libc.so
    

## 参考

  * [1] <https://cloud.tencent.com/developer/article/1351964>
  * [2] [https://blog.csdn.net/chrisnotfound/article/details/80082289?depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2&utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2](https://blog.csdn.net/chrisnotfound/article/details/80082289?depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2&utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-2)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hack_Pluto** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/203792](/post/id/203792)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Pwn](/tag/Pwn)
  * [CTF](/tag/CTF)

 **+1** __11赞

 __收藏

![](https://p0.ssl.qhimg.com/t0140bb461bf0455e30.jpg) Hack_Pluto

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

