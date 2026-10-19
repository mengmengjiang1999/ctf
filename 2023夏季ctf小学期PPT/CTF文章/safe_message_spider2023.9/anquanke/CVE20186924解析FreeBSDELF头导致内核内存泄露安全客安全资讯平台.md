# CVE-2018-6924：解析FreeBSD ELF 头导致内核内存泄露

阅读量 **209495**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-07-23 16:45:50

 **x**

##### 译文声明

本文是翻译文章，文章原作者 quarkslab，文章来源：blog.quarkslab.com

原文地址：<https://blog.quarkslab.com/cve-2018-6924-freebsd-elf-header-parsing-kernel-memory-disclosure.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t013ab4b4a2ba5e4f91.png)

2018年9月，FreeBSD发布了安全公告 **FreeBSD-SA-18：12** ，修复了影响该操作系统所有版本的内核内存泄露漏洞。

此漏洞（标识为`CVE-2018-6924`）是由FreeBSD内核在执行二进制文件之前解析二进制文件的ELF头时验证不充分引起的，本地非特权用户可以用它泄露内核的内存内容。

## 0x01 介绍

2018年9月12日，FreeBSD发布了安全公告[FreeBSD-SA-18：12](https://www.freebsd.org/security/advisories/FreeBSD-SA-18:12.elf.asc)，修复了CVE-2018-6924，这是由Thomas Barabosch和Mark
Johnston发现的内核内存泄漏漏洞，由内核中错误的ELF头解析引起。如公告中所述，“执行恶意ELF二进制文件可能会导致内核崩溃或泄露内核内存”。有趣的是，所有受支持的FreeBSD版本都受到这个bug的影响，包括版本10,10.4,11,11.1和11.2。

这里提供的分析基于`FreeBSD 11.2-RELEASE x64`，运行`GENERIC`内核。

## 0x02 修复情况

安全公告中包含指向修复的源代码补丁[链接](https://security.FreeBSD.org/patches/SA-18:12/elf.patch)。让我们先来看看它：

    
    
    --- sys/kern/imgact_elf.c.orig
    +++ sys/kern/imgact_elf.c
    @@ -839,7 +839,8 @@
                break;
            case PT_INTERP:
                /* Path to interpreter */
    -                   if (phdr[i].p_filesz > MAXPATHLEN) {
    +                   if (phdr[i].p_filesz < 2 ||
    +                       phdr[i].p_filesz > MAXPATHLEN) {
                    uprintf("Invalid PT_INTERPn");
                    error = ENOEXEC;
                    goto ret;
    @@ -870,6 +871,11 @@
                } else {
                    interp = __DECONST(char *, imgp->image_header) +
                        phdr[i].p_offset;
    +                           if (interp[interp_name_len - 1] != '') {
    +                                   uprintf("Invalid PT_INTERPn");
    +                                   error = ENOEXEC;
    +                                   goto ret;
    +                           }
                }
                break;
            case PT_GNU_STACK:
    --- sys/kern/vfs_vnops.c.orig
    +++ sys/kern/vfs_vnops.c
    @@ -528,6 +528,8 @@
        struct vn_io_fault_args args;
        int error, lock_flags;
    
    +   if (offset < 0 && vp->v_type != VCHR)
    +           return (EINVAL);
        auio.uio_iov = &aiov;
        auio.uio_iovcnt = 1;
        aiov.iov_base = base;
    

此处有两个修改过的文件：`sys/kern/imgact_elf.c`和`sys/kern/vfs_vnops.c`。sys/kern/imgact_elf.c文件中包含内核用于在执行二进制文件之前解析二进制文件的ELF头的代码，修复后的函数是这样的：

    
    
    776 static int
    777 __CONCAT(exec_, __elfN(imgact))(struct image_params *imgp)
    778 {
        [...]
    

因此，影响函数的名称是由`__CONCAT`和`__elfN`宏生成的。[__CONCAT](https://svnweb.freebsd.org/base/release/11.2.0/sys/sys/cdefs.h?revision=335563&view=markup#l143)连接两个参数，而__elfN在[sys/sys/elf_generic.h](https://svnweb.freebsd.org/base/release/11.2.0/sys/sys/elf_generic.h?revision=335563&view=markup#l53)中定义如下：

    
    
    #define __elfN(x)       __CONCAT(__CONCAT(__CONCAT(elf,__ELF_WORD_SIZE),_),x)
    

因此，函数名`___CONCAT(exec_,
__elfN(imgact))`扩展为`exec_elf32_imgact`或`exec_elf64_imgact`，具体取决于`__ELF_WORD_SIZE`定义为32还是64。但是如果我们检查`sys/kern/`目录，会发现存在名为`imgact_elf32.c`和`imgact_elf64.c`的两个非常小的文件，它们是将`__ELF_WORD_SIZE`定义为正确的大小，包含（include）了`kern/imgact_elf.c`文件，该文件包含易受攻击的函数。因此，内核包含了`sys/kern/imgact_elf.c`中任何函数的两个版本，其名称用_`_elfN`宏构建：一个版本处理32位ELF二进制文件，另一个版本处理64位ELF文件。

`imgact_elf32.c`：

    
    
    #define __ELF_WORD_SIZE 32
    #include <kern/imgact_elf.c>
    

`imgact_elf64.c`：

    
    
    #define __ELF_WORD_SIZE 64
    #include <kern/imgact_elf.c>
    

继续观察补丁，很明显问题位于处理ELF文件`PT_INTERP`程序头的代码中：

    
    
    static int
    __CONCAT(exec_, __elfN(imgact))(struct image_params *imgp)
    {
        [...]
        for (i = 0; i < hdr->e_phnum; i++) {
            switch (phdr[i].p_type) {
            [...]
            case PT_INTERP:
                /* Path to interpreter */
                if (phdr[i].p_filesz > MAXPATHLEN) {
                    uprintf("Invalid PT_INTERPn");
                    error = ENOEXEC;
                    goto ret;
                }
                [...]
    

`PT_INTERP`程序头保存了程序解释器的路径名，该类型仅对可执行文件有意义。
`PT_INTERP`程序头引用的可执行文件用作动态链接器，负责为动态链接的可执行文件加载所需的共享库。通常，`FreeBSD`上的程序解释器设置为[/libexec/ld-elf.so.1](https://www.freebsd.org/cgi/man.cgi?query=ld-elf.so)。

作为参考，[这是](https://svnweb.freebsd.org/base/release/11.2.0/sys/sys/elf32.h?revision=335563&view=markup#l102)32位ELF文件`Elf_Phdr`结构的指定版本：

    
    
    typedef struct {
        Elf32_Word      p_type;         /*输入类型*/
        Elf32_Off       p_offset;       /*文件偏移量 */
        Elf32_Addr      p_vaddr;        /* 内存映像中的虚拟地址. */
        Elf32_Addr      p_paddr;        /* 物理地址（未使用） */
        Elf32_Word      p_filesz;       /* 文件中的内容大小*/
        Elf32_Word      p_memsz;        /* 内存中的内容大小 */
        Elf32_Word      p_flags;        /* 访问权限标志 */
        Elf32_Word      p_align;        /* 内存和文件中的对齐方式 */
    } Elf32_Phdr;
    

易受攻击的老版本仅检查`phdr [i] .p_filesz>
MAXPATHLEN`，即它检查`PT_INTERP`程序头文件中的内容的大小（即解释器路径的长度）是否比`MAXPATHLEN`（1024）大;如果大，该功能很快就会出现`ENOEXEC`错误。

另一方面，修复版本中添加了一个检查：当`phdr [i] .p_filesz
<2`时会报错，即`PT_INTERP`程序头文件中的内容小于2。这表明需要执行一个ELF文件来触发该错误，其文件头要指定一个长度为0或1个字节的非常短的解释器路径。

## 0x03 挖掘历史

一开始我不知道该如何利用具有非常短的解释器路径的`PT_INTERP`程序头的ELF文件，于是我看了一下受影响文件`sys/kern/imgact_elf.c`的[提交历史](https://svnweb.freebsd.org/base/release/11.2.0/sys/kern/imgact_elf.c?view=log)，希望找到一些与伪造解释器路径相关的漏洞,给我一些灵感。

2012年7月19日提交的修订版[238617](https://svnweb.freebsd.org/base?view=revision&revision=238617)中的消息非常有趣：

> Fix several reads beyond the mapped first page of the binary in the  
>  ELF parser. Specifically, do not allow note reader and interpreter  
>  path comparision in the brandelf code to read past end of the page.  
>  This may happen if specially crafter ELF image is activated.

这说明`sys/kern/imgact_elf.c`文件已经受到与解释器路径处理相关的漏洞的影响。具体来说，这个老版本的bug讲述了“特制的ELF镜像(specially
crafted ELF image)”触发“读取二进制文件超出映射第一页的内容(reads beyond the mapped first page of
the binary)”的内容。对我来说，这听起来像是在第一页末尾的那些内存读取可能导致内核内存的泄露，这激发了我的灵感！

## 0x04 建立概念验证

我们发现在版本238617上修复的较旧的漏洞是关于内存“读取二进制文件超出映射第一页的内容”。如果我们要触发读取超过二进制文件第一页末尾的内存，就要让我们的ELF文件适合单个页面（即4096字节），以便读取操作访问我们的ELF文件中超出文件结尾的内存，就有可能实现内存泄露。

为了使ELF文件适合单个页面，我做了一个像这样的小C程序：

    
    
    int main(int argc, char** argv){
        return argc;
    }
    

编译后的程序大小不得超过4096字节。使用`clang`及`-m32`参数生成32位可执行文件，可以轻松地实现这一目标。另外，我使用`clang`的命令行选项`-Oz`（优化代码生成,比-Os生成的代码小）和`-Wl`，`-s`（去除调试和符号信息）让文件尽可能的小。

    
    
    % clang -Oz -Wl,-s -m32 test.c -o test
    

最终生成了一个3560字节的32位ELF文件，满足单个内存页面的条件。

现在的问题是：如何设计解释器路径，使内核中的解析代码访问内存中超过二进制文件的第一页（也是唯一一页）的末尾的内容？显然要构造一个`PT_INTERP`程序头，使其中的`p_offset`（解释器路径字符串的文件偏移量）大于4096。但是这并不那么简单，因为`exec_elf32_imgact()`函数会对`p_offset`成员的值进行检查：

    
    
    840                 case PT_INTERP:
    [...]
    852                         interp_name_len = phdr[i].p_filesz;
    853                         if (phdr[i].p_offset > PAGE_SIZE ||
    854                             interp_name_len > PAGE_SIZE - phdr[i].p_offset) {
    855                                 VOP_UNLOCK(imgp->vp, 0);
    856                                 interp_buf = malloc(interp_name_len + 1, M_TEMP,
    857                                     M_WAITOK);
    858                                 vn_lock(imgp->vp, LK_EXCLUSIVE | LK_RETRY);
    859                                 error = vn_rdwr(UIO_READ, imgp->vp, interp_buf,
    860                                     interp_name_len, phdr[i].p_offset,
    861                                     UIO_SYSSPACE, IO_NODELOCKED, td->td_ucred,
    862                                     NOCRED, NULL, td);
    863                                 if (error != 0) {
    864                                         uprintf("i/o error PT_INTERPn");
    865                                         goto ret;
    866                                 }
    867                                 interp_buf[interp_name_len] = '';
    868                                 interp = interp_buf;
    869                         } else {
    870                                 interp = __DECONST(char *, imgp->image_header) +
    871                                     phdr[i].p_offset;
    872                         }
    873                         break;
    

如第853行和第854所示，如果解释器路径字符串的文件偏移量位于第一页（`phdr [i] .p_offset>
PAGE_SIZE`）之后，或者解释器路径足够长以使其超出第一页页面（`interp_name_len> PAGE_SIZE - phdr [i]
.p_offset`），将调用`vn_rdwr()`函数，从`interp_buf`缓冲区的`p_offset`偏移量处读取代表ELF文件的[vnode](https://www.freebsd.org/cgi/man.cgi?query=vnode)。我的猜测是，在可执行文件加载过程的早期，只有文件的第一页加载到内存中，因此访问超过第一页一定会触及磁盘。但由于我们的ELF文件小于`PAGE_SIZE`字节，因此`vn_rdwr()`无法读取偏移大于PAGE_SIZE的内容，从而将我们从函数中踢出。（顺便说一下，请注意在`sys/kern/vfs_vnops.c`中定义的`vn_rdwr()`函数是公告包含的补丁中另外修复的函数;补丁另外添加了拒绝向`vnode`提供负偏移量的检查。

相反，如果`p_offset`不大于0x1000并且解释器路径字符串的长度不大于`PAGE_SIZE -phdr[i].p_offset`，程序将进入第869行的else分支，其中`PT_INTERP`的内容程序头被认为是好的，因此`interp`变量将指向`image_header+phdr[i].p_offset`，即解释器路径字符串。

因此，触发漏洞的关键在于：
**我们需要构造一个`PT_INTERP`程序头，其中`p_offset`的值为0x1000，`p_filesz`的值为0**。p_offset的值能绕过第853行的检查，因为它不大于0x1000
;p_filesz的值绕过第854行的检查，因为`interp_name_len(0)`不大于`PAGE_SIZE - phdr[i].p_offset
== 0x1000 - 0x1000 ==
0`。使用这两个特殊值，程序将进入else分支第869行并且`interp`的值将最终指向我们的ELF镜像的0x1000偏移量处，也就是说，正好超过ELF文件开头一页;但由于我们的ELF文件只占用一个内存页面，`interp`会越界，指向我们的ELF文件之后的页面。

补丁的作用现在变得更加清晰：要求解释器的路径至少有2个字节，以避免在这种情况下导致触发漏洞。解释器路径应至少为1个字符再加上其终止符`null`（PT_INTERP的`p_filesz`字段的值必须考虑字符串的结尾的终止符null）。

为了构造正确的PT_INTERP程序头，我将之前编译的测试二进制文件加载到[Kaitai
WebIDE](https://ide.kaitai.io/)中，以便检查其ELF头。可以看到PT_INTERP程序头从0x54偏移处开始。确切地说，我们需要将偏移量为0x58处（`p_offset`，红色突出显示,原始值为0x134）的双字（DWORD）设置为0x1000，将偏移量为0x64的DWORD（`p_filesz`，绿色突出显示，原始值为0x15）设置为0。

![](https://p5.ssl.qhimg.com/t014d6b09e11aeb12fb.png)

![](https://p2.ssl.qhimg.com/t01da6f8864245b4064.png)

## 0x05 泄露内核内存

那么，当`interp`变量越界,指向ELF文件后面的页面上的任何数据的时会发生什么？在`exec_elf32_imgact（）`函数的第1059行，调用`elf32_load_file（）`函数加载解释器，其文件名由interp变量指定。不论`elf32_load_file（）`因任何原因无法加载解释器（例如找不到给定的文件），都会返回错误，并在第1064行调用[uprintf（）](https://www.freebsd.org/cgi/man.cgi?query=uprintf&sektion=9&n=1)函数,将错误消息打印到当前进程的控制端`tty`，包括interp指向的（伪造）解释器文件名：

    
    
    1036                if (interp != NULL) {
    1037                        have_interp = FALSE;
    [...]
    1058                        if (!have_interp) {
    1059                                error = __elfN(load_file)(imgp->proc, interp, &addr,
    1060                                    &imgp->entry_addr, sv->sv_pagesize);
    1061                        }
    1062                        vn_lock(imgp->vp, LK_EXCLUSIVE | LK_RETRY);
    1063                        if (error != 0) {
    1064                                uprintf("ELF interpreter %s not found, error %dn",
    1065                                    interp, error);
    1066                                goto ret;
    1067                        }
    

将interp指向的以null结尾的字符串打印到当前进程的`tty`作为错误消息的一部分使内存泄露成为可能的。

我们可以在`FreeBSD`测试机上多次运行修改过的ELF文件，看看它是如何通过内核产生的错误信息泄漏内核内存的内容的：

    
    
    francisco@freebsd112:~ % ./poc1
    ELF interpreter Ø3¤ not found, error 2
    Abort
    
    francisco@freebsd112:~ % ./poc1
    ELF interpreter  not found, error 2
    Abort
    
    francisco@freebsd112:~ % ./poc1
    ELF interpreter $ûÿÿl not found, error 2
    Abort
    
    francisco@freebsd112:~ % ./poc1
    ELF interpreter ^?ELF^A^A^A  not found, error 2
    Abort
    

请注意，如果越界内存读取未映射的页面，内核会崩溃。然而，经过几十次测试（包括重新启动以确保在运行中没有特别的内存布局）我从未遇到内核崩溃。

## 0x06 捕获不可打印字符的输出

`uprintf()`函数将伪造的`interp`指针视为指向以null结尾的字符串（％s）的指针，因此将打印相应的字符，直到遇到空字节。
由于打印的字符不一定在可打印范围内，因此捕获包含泄漏的内核数据的错误消息进行`hexdump`可能是个可行的方法。由于`uprintf()`写入当前进程的控制终端`tty`，我们可以使用将打印在终端上的所有内容保存到临时文件中的[脚本工具](https://www.freebsd.org/cgi/man.cgi?query=script&apropos=0&sektion=1&manpath=FreeBSD+12.0-RELEASE&arch=default&format=html)捕获其输出。

下面的代码段显示了利用此漏洞泄露的75字节内核内存的十六进制文件：

    
    
    francisco@freebsd112:~ % script -q capture1 ./poc1
    ELF interpreter ?^[(^[(?^[(?^[(^[(^Z(^Z(^Z(^Z(^[(17^[(5^[(^[(^[(^[(  not found, error 2
    
    francisco@freebsd112:~ % hexdump -C capture1
    00000000  70 6f 63 31 3a 0d 0a 45  4c 46 20 69 6e 74 65 72  |poc1:..ELF inter|
    00000010  70 72 65 74 65 72 20 c5  83 5e 5b 28 cc 83 5e 5b  |preter ..^[(..^[|
    00000020  28 d4 83 5e 5b 28 dc 83  5e 5b 28 98 83 5e 5b 28  |(..^[(..^[(..^[(|
    00000030  d8 d1 5e 5a 28 e2 d1 5e  5a 28 fe e5 5e 5a 28 9c  |..^Z(..^Z(..^Z(.|
    00000040  bf 5e 5a 28 e3 83 5e 5b  28 31 37 5e 5b 28 35 ba  |.^Z(..^[(17^[(5.|
    00000050  5e 5b 28 e6 83 5e 5b 28  e9 83 5e 5b 28 f2 83 5e  |^[(..^[(..^[(..^|
    00000060  5b 28 20 6e 6f 74 20 66  6f 75 6e 64 2c 20 65 72  |[( not found, er|
    00000070  72 6f 72 20 32 0d 0a 70  6f 63 31 3a 20 73 69 67  |ror 2..poc1: sig|
    00000080  6e 61 6c 20 36 0d 0a                              |nal 6..|
    00000087
    

## 0x06 结论

这一内核内存泄露漏洞影响了所有受支持的FreeBSD版本;我们的分析所使用的11.2版本分支，已在`FreeBSD
11.2-RELEASE-p3`版本上修复。没有权限的用户可以通过执行`size<0x1000`字节的ELF文件来触发内核中的越界内存访问，该文件包含构造的`PT_INTERP`程序头，字段为`p_offset
== 0x1000`和`p_filesz ==
0`。这将绕过内核处理`PT_INTERP`程序头时完整性检查，使其将ELF文件之后的页面的数据当作解释器路径字符串处理，有效地访问越界内存。

加载伪造的解释器失败后，内核将打印一条错误消息，其中包含无法找到的解释器路径，从而泄漏到用户模式。从ELF之后的页面开头的数据开始到下一个空字节结束，其中的内容都被解释为伪造的解释器路径。

上面显示的测试是在没有任何内核内存修饰的情况下执行的。如果您想获得可预测的内存布局，从而更好地控制通过此漏洞泄漏的内容，则可能需要此类技术。

细心的读者可能已经注意到除了设置`p_offset == 0x1000`和`p_filesz ==
0`之外，实际上有更多的方法来触发错误。例如：ELF文件大小== 0x1000，p_offset = 0xfff，p_filesz ==
1，文件的最后一个字节是非空的（即PT_INTERP指向文件的最后一个字节，解释器字符串缺少空终止符）。实际上，只要引用的解释器字符串位于页面的末尾且不是以null结尾的，`p_offset`和`p_filesz`就可以有其他值。

最后，我想强调根据两种不同的字符串表示来解释相同数据块的危险性：`PT_INTERP`程序头将解释器字符串存储为`指针+长度`表示，而解释器代码将其视为`null
-terminated`，不需要指示字符串长度。解释字符串数据方式的差异对此漏洞有直接影响，因为如果重视`p_filesz`字段中的长度为0的情况，则没有数据会泄漏到用户模式。

## 0x07 致谢

非常感谢Quarkslab的同事们对这篇文章进行校对。

本文翻译自blog.quarkslab.com
[原文链接](https://blog.quarkslab.com/cve-2018-6924-freebsd-elf-header-parsing-kernel-memory-disclosure.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fbird666** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/182233](/post/id/182233)

安全客 - 有思想的安全新媒体

本文转载自: [blog.quarkslab.com](https://blog.quarkslab.com/cve-2018-6924-freebsd-elf-header-parsing-kernel-memory-disclosure.html)

如若转载,请注明出处： <https://blog.quarkslab.com/cve-2018-6924-freebsd-elf-header-parsing-kernel-memory-disclosure.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [FreeBSD](/tag/FreeBSD)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t014755f870454f364b.png) fbird666

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

