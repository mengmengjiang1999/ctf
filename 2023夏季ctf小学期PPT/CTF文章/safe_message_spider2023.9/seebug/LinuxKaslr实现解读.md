**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/qGQ-_uDD3Umn-7bbRGf7pA>**

# 1 地址随机化与PIE

## 1.1 pie简介

gcc
的pie选项可以生成对符号的引用变为与位置无关的代码。之前对符号的绝对地址引用变为相对于PC指令或相对于二进制某固定位置的偏移引用。当内核被随机的加载到任意内存地址时，可以简化对符号重定位的处理。

## 1.2 pie验证

我们通过反汇编vmlinux来验证经过pie编译后产生的一些代码是否可以做到位置无关。

### 1.2.1 块间全局变量引用 bss段引用

    
    
    1    104  /root/kernel/linux-4.5/kernel/fork.c <<total_forks>>
    unsigned long total_forks;
    static int show_stat(struct seq_file *p, void *v)
    fs/proc/stat.c
    
    ffffffff81291960 <show_stat>:
    ffffffff81291f5a:       4c 8b 05 87 3b d4 00    mov    0xd43b87(%rip),%r8        # ffffffff81fd5ae8 <total_forks>
    [root@localhost build-4.5]# readelf -r vmlinux|grep ffffffff81291f5d
    ffffffff81291f5d  efc100000002 R_X86_64_PC32     ffffffff81fd5ae8 total_forks - 4

R_X86_64_PC32 &&非percpu变量， 不需要重定位。

### 1.2.2 模块内全局变量引用 bss段引用

    
    
    int max_threads;                /* tunable limit on nr_threads */
    
    ffffffff81087ce0 <set_max_threads>:
    ffffffff81087d43:       89 3d 97 dd f4 00       mov    %edi,0xf4dd97(%rip)        # ffffffff81fd5ae0 <max_threads>
      [56] .bss              NOBITS           ffffffff81f2e000  0132e000
           000000000031b000  0000000000000000  WA       0     0     4096
    76199: ffffffff81fd5ae0     4 OBJECT  GLOBAL DEFAULT   56 max_threads
    [root@localhost build-4.5]# readelf -r vmlinux|grep ffffffff81087d45
    ffffffff81087d45  129a700000002 R_X86_64_PC32     ffffffff81fd5ae0 max_threads - 4

R_X86_64_PC32 &&非percpu变量， 不需要重定位。

### 1.2.3 模块间函数调用 text段引用

    
    
    ffffffff81088890 <free_task>:
    ffffffff810888c5:       e8 56 87 0c 00          callq  ffffffff81151020 <ftrace_graph_exit_task>
    [root@localhost build-4.5]# readelf -r vmlinux|grep ffffffff810888c6
    Offset          Info           Type           Sym. Value    Sym. Name + Addend
    ffffffff810888c6  11e8900000002 R_X86_64_PC32     ffffffff81151020 ftrace_graph_exit_task - 4

R_X86_64_PC32 &&非percpu变量，不需要重定位。

### 1.2.4 模块内函数调用 text段引用

    
    
    ffffffff810888f0 <__put_task_struct>:
    ffffffff8108898a:       e8 01 ff ff ff          callq  ffffffff81088890 <free_task>
    [root@localhost build-4.5]# readelf -r vmlinux|grep ffffffff8108898b
    ffffffff8108898b  15fc700000002 R_X86_64_PC32     ffffffff81088890 free_task - 4

R_X86_64_PC32 &&非percpu变量， 不需要重定位。

### 1.2.5 Percpu 变量引用 data段引用

    
    
    static DEFINE_PER_CPU(struct task_struct *, idle_threads);
    
    struct task_struct *idle_thread_get(unsigned int cpu)
    {
            struct task_struct *tsk = per_cpu(idle_threads, cpu);
    
            if (!tsk)
                    return ERR_PTR(-ENOMEM);
    
            init_idle(tsk, cpu);
            return tsk;
    }
    
    
    ffffffff810ada80 <idle_thread_get>:
    ffffffff810ada80:       e8 bb b2 63 00          callq  ffffffff816e8d40 <__fentry__>
    ffffffff810ada85:       89 fa                   mov    %edi,%edx
    ffffffff810ada87:       55                      push   %rbp
    ffffffff810ada88:       48 c7 c0 48 de 00 00    mov    $0xde48,%rax
    ffffffff810ada8f:       48 8b 14 d5 40 52 d4    mov    -0x7e2badc0(,%rdx,8),%rdx
    ffffffff810ada96:       81
    ffffffff810ada97:       48 89 e5                mov    %rsp,%rbp
    ffffffff810ada9a:       53                      push   %rbx
    ffffffff810ada9b:       48 8b 1c 10             mov    (%rax,%rdx,1),%rbx
    
    
    [root@localhost build-4.5]# readelf -r vmlinux|grep ffffffff810ada93
    ffffffff810ada93  122e20000000b R_X86_64_32S      ffffffff81d45240 __per_cpu_offset + 0

R_X86_64_32S && 非percpu变量，需要重定位。

    
    
    [root@localhost build-4.5]# readelf -s  vmlinux|grep   __per_cpu_offset
    
    
    74466: ffffffff81d45240 65536 OBJECT  GLOBAL DEFAULT   30 __per_cpu_offset
      [30] .data             PROGBITS         ffffffff81c00000  00e00000
           0000000000165d80  0000000000000000  WA       0     0     4096
      [33] .data..percpu     PROGBITS         0000000000000000  01000000
           0000000000018098  0000000000000000  WA       0     0     4096
    
    
    [root@localhost build-4.5]# readelf -s vmlinux|grep percpu|grep 33
    
    
    9758: ffffffff810e63b0   337 FUNC    LOCAL  DEFAULT    1 __free_percpu_irq
    11209: 000000000000f1c0   728 OBJECT  LOCAL  DEFAULT   33 tick_percpu_dev

### 1.2.6 引用rodata变量

[root@localhost build-4.5]# readelf -S vmlinux|grep text

    
    
    [ 1] .text             PROGBITS         ffffffff81000000  00200000
    [root@localhost build-4.5]# readelf -S vmlinux|grep rodata
      [ 7] .rodata           PROGBITS         ffffffff81800000  00a00000
    ffffffff81d80c98 <start_kernel>:
    ffffffff81d80d76:       48 c7 c6 e0 00 80 81    mov    $0xffffffff818000e0,%rsi

[root@localhost build-4.5]# readelf -r vmlinux|grep `ffffffff81d80d79`

    
    
    ffffffff81d80d79  10f420000000b R_X86_64_32S      ffffffff818000e0 linux_banner + 0

R_X86_64_32S && 非percpu变量，需要重定位。

    
    
    rodata:FFFFFFFF818000E0                 public linux_banner
    .rodata:FFFFFFFF818000E0 linux_banner    db 'Linux version 4.5.0 (root@localhost.localdomain) (gcc version 4.8'
    .rodata:FFFFFFFF818000E0                                         ; DATA XREF: start_kernel+DE↓o
    .rodata:FFFFFFFF818000E0                 db '.5 20150623 (Red Hat 4.8.5-28) (GCC) ) #1 SMP Tue Aug 28 12:48:38'
    .rodata:FFFFFFFF818000E0                 db ' CST 2018',0Ah,0

# 2\. Linux kaslr 实现原理

## 2.1 vmlinux 是如何生成的

由于内核是要把内核符号表一同链接进vmlinux里， 因此需要分三步进行链接： Scripts/ link-vmlinux.sh

第一步：

    
    
           ld               nm                   
       *.o---->.tmp_vmlinux1---->.tmp_kallsyms1.o

第二步：

    
    
                                  ld                nm
    .tmp_vmlinux1 + .tmp_kallsyms1.o ---->.tmp_vmlinux2-----à.tmp_kallsyms2.o

第三步：

    
    
                                      ld
        .tmp_vmlinux2 + .tmp_kallsyms2.o ---->vmlinux

由各种.o文件链接成临时内核 `.tmp_vmlinux1`，然后利用nm提取出内核符号导入到 `.tmp_kallsyms1.o` 文件，在把
`.tmp_vmlinux1` 和 `.tmp_kallsyms1.o` 一起链接为临时内核 `.tmp_vmlinux2`，此时新增了一个
**kallsyms section，里面保存的就是nm导出的内核符号值， 注意对于** kallsyms
section自身产生的符号并没有提取出来，需要在重复上一步的链接处理，此时得到的 `tmp_kallsyms2.o` 已经包含了完整的符号，将其与
`.tmp_vmlinux2` 链接，产生最终的vmlinux。如果内核配置文件开启了
KALLSYMS_EXTRA_PASS，为了避免产生align对齐的一些bug，还需在重复上述步骤一次，产生 `.tmp_vmlinux3`。

## 2.2 vmlinuz 是如何产生的

由于vmlinux即使没有采用pie，所产生的二进制文件仍然很大，所以采用了将vmlinux进行压缩的方案，在bootloader加载内核时，在对其进行解压，有点类似于加壳程序的执行流程。
Linux在链接阶段会产生如下文件： `vmlinux.bin` 经过strip后的二进制，去掉了debug和comment信息。
`vmlinux.bin.all`
由`vmlinux.bin`和`vmlinux.relocs`组成，`vmlinux.relocs`保存的是需要重定位的地址数组。
`vmlinux.bin.(gz|bz2|lzma|...)` 由`vmlinux.bin.all` \+ `u32 size`,
size是一个四字节的数值，保存的是`vmlinux.bin.all`的文件大小，最后由gzip等压缩工具压缩。
举例`vmlinux.bin.gz`是由gzip压缩后的二进制文件。 而vmlinuz则由以下几个部分组成：

    
    
      |--------------------piggy.s---------------|
    ----------------------------------------------------------    | uncompress code| asm globals |         vmlinux.bin.gz        |
    ----------------------------------------------------------    | vmlinux.bin | vmlinux.relocs | size |
    ------------------------------
## 2.3 vmlinux.relocs 是什么

Linux没有选择在bootloader阶段对内核进行复杂的重定位工作，
由于内核是pie编译产生的，我们从最前面的反汇编信息来看，大部分符号的重定位工作只需加上内核被随机化产生的偏移值即可完成重定位，而不需要解析x86定义的各种重定位类型。因此只需要在重定位时提供给bootloader需要被重定位的地址即可，这些地址保存在vmlinux.relocs里。
在vmlinux生成后，通过arch/x86/tools/relocs来提取vmlinux rela保存的信息，它的结构如下：

    
    
    --------------------------------------------------------------------------       | 0 | 64bit relocation address …| 0 | 32 bit inverse relocation …| 0 | 32 bit relocation …|
    --------------------------------------------------------------------------
在解析vmlinux
rela重定位表的时候需要做过滤，当需要被重定位的符号是绝对地址时，如果不在白名单内就要报错，提醒内核开发者需要将绝对地址的引用代码进行修改。

    
    
    static const char * const sym_regex_kernel[S_NSYMTYPES] = {
            [S_ABS] =
            "^(xen_irq_disable_direct_reloc$|"
            "xen_save_fl_direct_reloc$|"
            "VDSO|"
            "__crc_)",

白名单中的这些值都是经过内核开发者人工review过的，确认即使内核加载在不同的地址，这些符号地址仍然是不变的，
因此连接器生成的重定位表中包含这些符号时，可过滤掉，不进行重定位处理。
还有一些符号虽然被连接器标记为绝对地址，但是内核开发者人工review过也是相对地址引用的， 所以这些符号是需要被重定位的。

    
    
     [S_REL] =
            "^(__init_(begin|end)|"
            "__x86_cpu_dev_(start|end)|"
            "(__parainstructions|__alt_instructions)(|_end)|"
            "(__iommu_table|__apicdrivers|__smp_locks)(|_end)|"
            "__(start|end)_pci_.*|"
            "__(start|end)_builtin_fw|"
            "__(start|stop)___ksymtab(|_gpl|_unused|_unused_gpl|_gpl_future)|"
            "__(start|stop)___kcrctab(|_gpl|_unused|_unused_gpl|_gpl_future)|"
            "__(start|stop)___param|"
            "__(start|stop)___modver|"
            "__(start|stop)___bug_table|"
            "__tracedata_(start|end)|"
            "__(start|stop)_notes|"
            "__end_rodata|"
            "__initramfs_start|"
            "(jiffies|jiffies_64)|"
    #if ELF_BITS == 64
            "__per_cpu_load|"
            "init_per_cpu__.*|"
            "__end_rodata_hpage_align|"
    #endif
            "__vvar_page|"
            "_end)$"

还有一个需要特别处理的是内核.data..percpu这个section，当在x86_64
SMP下，连接器给这个section生成的虚拟地址是0，因此在解析重定位表时，如果碰到对.data..percpu的引用，需要首先修正引用的值，.data..percpu
可以通过定义在text段的__per_cpu_load变量进行修正，它的符号值在链接时是确定的。

    
    
    static void percpu_init(void)
    {
            int i;
            for (i = 0; i < ehdr.e_shnum; i++) {
                    ElfW(Sym) *sym;
                    if (strcmp(sec_name(i), ".data..percpu"))
                            continue;
    
                    if (secs[i].shdr.sh_addr != 0)  /* non SMP kernel */
                            return;
    
                    sym = sym_lookup("__per_cpu_load");
                    if (!sym)
                            die("can't find __per_cpu_load\n");
    
                    per_cpu_shndx = i;
                    per_cpu_load_addr = sym->st_value;
                    return;
            }
    }
    
    static int do_reloc64(struct section *sec, Elf_Rel *rel, ElfW(Sym) *sym,
                          const char *symname)
    {
            if (sec->shdr.sh_info == per_cpu_shndx)
                    offset += per_cpu_load_addr;
    }

## 2.4 bootloader 的重定位流程

### 2.4.1 随机偏移值的选取

内核被加载的物理地址起始值为PHYSICAL_START
0x1000000，随机化的意思是基于这个起始地址在向后偏移一段随机地址。而这个随机值不能为任意值，因为：
X86处理器内存分页机制有几种模式，每个模式定义的物理内存页的大小也不一样。

![](https://images.seebug.org/content/images/2021/06/6bbbef0a-7adf-48e2-9035-8e1c847a44ba.png-w331s)

如果一段内存由于没有基于物理页对齐的话，它会产生于两个物理页之间，而这两个物理页可能具有不同的权限，不如一个只读，一个可写，这样原本只想可读的那段内存就有一部分具有了可写的权限。Linux为了保持兼容性，64位下选择了2mb对齐，32位选择了8k对齐。

### 2.4.2 重定位处理逻辑

Bootloader在选取合适的偏移值后，会将内核二进制中的text和data段拷贝到PHYSICAL_START+offset的物理地址上，然后执行重定位处理，前面讲过vmlinuz中保存着vmlinux.relocs文件，它里面包含的就是需要重定位的地址，因此bootloader从个文件中提取出要重定位的地址。

    
    
    arch/x86/boot/compressed/misc.c
    
    static void handle_relocations(void *output, unsigned long output_len)
    {
            int *reloc;
            unsigned long delta, map, ptr;
            unsigned long min_addr = (unsigned long)output;
            unsigned long max_addr = min_addr + output_len;
    
            delta = min_addr - LOAD_PHYSICAL_ADDR;
            if (!delta) {
                    debug_putstr("No relocation needed... ");
                    return;
            }
            debug_putstr("Performing relocations... ");
            map = delta - __START_KERNEL_map;
            for (reloc = output + output_len - sizeof(*reloc); *reloc; reloc--) {
                    int extended = *reloc;
                    extended += map;
    
                    ptr = (unsigned long)extended;
                    if (ptr < min_addr || ptr > max_addr)
                            error("32-bit relocation outside of kernel!\n");
    
                    *(uint32_t *)ptr += delta;
            }
    #ifdef CONFIG_X86_64
            while (*--reloc) {
                    long extended = *reloc;
                    extended += map;
    
                    ptr = (unsigned long)extended;
                    if (ptr < min_addr || ptr > max_addr)
                            error("inverse 32-bit relocation outside of kernel!\n");
    
                    *(int32_t *)ptr -= delta;
            }
            for (reloc--; *reloc; reloc--) {
                    long extended = *reloc;
                    extended += map;
    
                    ptr = (unsigned long)extended;
                    if (ptr < min_addr || ptr > max_addr)
                            error("64-bit relocation outside of kernel!\n");
    
                    *(uint64_t *)ptr += delta;
            }

前面提到vmlinux.relocs的文件结构有三段，所以上面有三个循环来分别解析处理，我们已64位reloc信息的处理为例：

    
    
    for (reloc--; *reloc; reloc--) {
                    long extended = *reloc;
                    extended += map;
    
                    ptr = (unsigned long)extended;
                    *(uint64_t *)ptr += delta;
            }

笔者认为这段代码写的比较隐晦难懂，
_reloc保存的是vmlinux链接后的虚拟地址，本来内核是链接在PHYSICAL_START这个物理地址，虚拟地址和物理地址的映射关系是： 物理地址 =
虚拟地址 - START_KERNEL_map
START_KERNEL_map是内核起始的虚拟地址，在重定位阶段，内核还没启用分页机制，所以对地址的引用都是物理地址，而_
reloc保存的是链接后的虚拟地址，因此要利用上面的公式进行转换，同时也要把随机偏移值加上。 _ptr为最终要修正的物理地址：_`reloc` \-`START_KERNEL_map` \+ `delta`, 这个物理地址保存的值为**`reloc`+`delta`, delta为随机偏移值。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1610/>

