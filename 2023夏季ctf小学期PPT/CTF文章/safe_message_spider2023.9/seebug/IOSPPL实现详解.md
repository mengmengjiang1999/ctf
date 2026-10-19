**作者： wzt  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## Ppl代码初始化

### ppl物理内存初始化

内核在启动阶段调用pmap_bootstrap函数初始化物理内存布局。

    
    
    pmap_bootstrap：
    
    LDR       X20, [X27,#_avail_start@PAGEOFF]
    
    MOV       X0, X20
    
    BL        _phystokv
    
    MOV       X21, X0
    
    ADRP       X8, #_pmap_array_begin@PAGE
    
    STR       X0, [X8,#_pmap_array_begin@PAGEOFF]
    
    ADRP       X19, #_pmap_array@PAGE
    
    STR       X0, [X19,#_pmap_array@PAGEOFF]
    
    ADRP       X24, #_pmap_max_asids@PAGE
    
    LDR       W8, [X24,#_pmap_max_asids@PAGEOFF]
    
    MOV       W9, #0x108
    
    MOV       W10, #0x3FFF
    
    MADD       X8, X8, X9, X10
    
    AND       X8, X8, #0x3FFFFFFC000
    
    ADD       X0, X8, X20
    
    STR       X0, [X27,#_avail_start@PAGEOFF]
    
    BL        _phystokv
    
    ADRP       X8, #_pmap_array_end@PAGE
    
    STR       X0, [X8,#_pmap_array_end@PAGEOFF]

`_avail_start`保存的是当前空闲物理内存的物理地址，转换成虚拟地址后，保存在`_pmap_array_begin`和`_pmap_array`变量中，然后从此物理地址划出`_pmap_max_asids`字节大小的区域给`_pmap_array`，它是一个struct
pmap数组，在ppl的实现中，内核以及每个进程都有单独的一个struct pmap结构。在非ppl的版本中，只有内核使用struct map。

    
    
    ADRP       X8, #_pmap_array_count@PAGE
    
    ADRL       X10, _pmap_free_list_lock
    
    STR       X9, [X8,#_pmap_array_count@PAGEOFF]
    
    STR       X23, [X10,#(qword_FFFFFFF00981CA88 - 0xFFFFFFF00981CA80)]
    
    STR       XZR, [X10]
    
    LDR       X9, [X8,#_pmap_array_count@PAGEOFF]

计算`_pmap_array_count`大小。

    
    
    MOV       X9, #0
    
    MOV       X10, #0
    
    MOV       X12, #0
    
    LDR       X11, [X19,#_pmap_array@PAGEOFF]
    
    STR       X12, [X11,X9]
    
    LDR       X11, [X19,#_pmap_array@PAGEOFF]
    
    ADD       X12, X11, X9
    
    ADD       X10, X10, #1
    
    LDR       X13, [X8,#_pmap_array_count@PAGEOFF]
    
    ADD       X9, X9, #0x108
    
    CMP       X10, X13
    
    B.CC       loc_FFFFFFF007B5E820
    
    ADD       X8, X11, X9
    
    SUB       X8, X8, #0x108
    
    B        loc_FFFFFFF007B5E850
    
    MOV       X8, #0
    
    ADRP       X9, #_pmap_free_list@PAGE
    
    STR       X8, [X9,#_pmap_free_list@PAGEOFF]

初始化`_pmap_free_list`链表，循环让`_pmap_array`数组中的每个元素依次指向前一个节点，以后ppl为每个进程分配struct
pmap结构体时就从这个链表分配。

下面用类似的算法初始化`_pmap_ledger_ptr_array`数组，这里不在赘述。

然后开始初始化ppl使用的stack信息：

    
    
    ADRP       X8, #_pmap_stacks_start@PAGE
    
    LDR       X8, [X8,#_pmap_stacks_start@PAGEOFF]
    
    ADD       X26, X8, #4,LSL#12
    
    ADRP       X8, #_pmap_stacks_start_pa@PAGE
    
    STR       X20, [X8,#_pmap_stacks_start_pa@PAGEOFF]

`_pmap_stacks_startv`保存的是stack的虚拟地址，`_pmap_stacks_start_pa`保存的是stack的物理地址，后面修改`kernel_map->tte`的l3页表，进行虚拟地址到物理地址的映射。

    
    
    MOV       X28, #0x20000000000603
    
    ADRL       X21, _pmap_cpu_data_array
    
    MOV       W25, #0xFFFFFFFF
    
    B        loc_FFFFFFF007B5E92C
    
    MOV       W8, #0x180
    
    MADD       X8, X19, X8, X21
    
    STR       W25, [X8,#0x40]
    
    STR       WZR, [X8,#0x18]
    
    STR       X24, [X8,#8]
    
    ADD       X26, X26, #8,LSL#12
    
    ADD       X19, X19, #1
    
    CMP       X19, #6
    
    B.EQ       loc_FFFFFFF007B5E9B8
    
    ADD       X24, X26, #4,LSL#12
    
    MOV       X23, X26
    
    MOV       X8, #0xFFFFFFFFFFFFBFFF
    
    CMP       X26, X8
    
    B. HI       loc_FFFFFFF007B5E908

依次设置每个cpu的`_pmap_cpu_data`结构体，STR X24, [X8,#8]，将栈地址保存在0x8偏移处。每个cpu的ppl
stack都是4k，之间在隔离着一个4k的guard page。

后面的代码继续初始化`_ppl_cpu_save_area`，它保存的是ppl进入`EL1_Guard level`异常处理时保存的全部寄存器区域。

下面给出xnu物理内存布局图，请原谅我的懒惰，不想画漂亮的图形。

![图片](https://images.seebug.org/content/images/2021/11/26/1637910095000-1qoyac.png-w331s)

### pp_attr_table与pv_head_table

XNU的物理内存管理模型，增加了两个结构体用于辅助物理页的管理。

`pp_attr_t`代表的是一个物理页的属性，在XNU的source code里可以看到其定义：

    
    
    osfmk/arm/pmap.c
    
    typedef u_int16_t pp_attr_t;
    
    
    
    \#define PP_ATTR_WIMG_MASK        0x003F
    
    \#define PP_ATTR_WIMG(x)         ((x) & PP_ATTR_WIMG_MASK)
    
    
    
    \#define PP_ATTR_REFERENCED        0x0040
    
    \#define PP_ATTR_MODIFIED         0x0080
    
    
    
    \#define PP_ATTR_INTERNAL         0x0100
    
    \#define PP_ATTR_REUSABLE         0x0200
    
    \#define PP_ATTR_ALTACCT         0x0400
    
    \#define PP_ATTR_NOENCRYPT        0x0800
    
    
    
    \#define PP_ATTR_REFFAULT         0x1000
    
    \#define PP_ATTR_MODFAULT         0x2000
    
    
    
    \#if XNU_MONITOR
    
    /*
    
     \* Denotes that a page is owned by the PPL.  This is modified/checked with the
    
     \* PVH lock held, to avoid ownership related races.  This does not need to be a
    
     \* PP_ATTR bit (as we have the lock), but for now this is a convenient place to
    
     \* put the bit.
    
     */
    
    \#define PP_ATTR_MONITOR         0x4000
    
    
    
    /*
    
     \* Denotes that a page *cannot* be owned by the PPL.  This is required in order
    
     \* to temporarily 'pin' kernel pages that are used to store PPL output parameters.
    
     \* Otherwise a malicious or buggy caller could pass PPL-owned memory for these
    
     \* parameters and in so doing stage a write gadget against the PPL.
    
     */
    
    \#define PP_ATTR_NO_MONITOR        0x8000

对于ppl来讲，增加了两个属性`PP_ATTR_MONITOR`和`PP_ATTR_NO_MONITOR`，ios使用相同的值，后面会看到。

每个物理页在内核中有两种用处，第一个物理页保存的是页表内容，第二个就是保存内核用到的其他数据结构，在XNU的物理内存管理模型中，使用`struct
pv_entry`结构体保存l3页表项的地址，可以提高物理内存与虚拟内存相互转化的效率。使用`struct
pt_desc`结构体描述一个页表属性，比如l1、l2、l3table的属性。对于ppl，会用到`pv_head_table`对给定的一个物理页上锁。

`Pv_head_table`的内存布局如下，请再次原谅我的懒惰。

![图片](https://images.seebug.org/content/images/2021/11/26/1637910096000-2kzikm.png-w331s)

### EL1_Guard level初始化

在初始化完ppl的物理内存布局后，内核在启动的下一阶段会调用`_bootstrap_instructions`继续执行`EL1_Guard
level`的初始化。

    
    
    __start->_start_first_cpu->_arm_init->_arm_vm_init->_bootstrap_instructions
    
    _bootstrap_instructions:

关闭mmu

    
    
    S3_6_C15_C1_00x1
    
    S3_6_C15_C1_10x1
    
    S3_6_C15_C1_50x2010000030100000
    
    S3_6_C15_C1_60x2020000030200000
    
    S3_6_C15_C1_70x2020a500f020f000
    
    S3_6_C15_C3_00x2020a505f020f0f0
    
    
    S3_6_C15_C1_20x1
    
    S3_6_C15_C8_1_gxf_bootstrap_handler(虚拟地址)
    
    S3_6_C15_C8_2_gtr_deadloop(虚拟地址)
    
    S3_6_C15_C1_20x0

开启mmu

在这个函数里，可以看到苹果cpu加入了几个新的系统寄存器，
通过分析代码逻辑可以推测出`S3_6_C15_C1_2`寄存器应该是个执行上锁和解锁的功能。`gxf_bootstrap_handler`函数地址存入了`S3_6_C15_C8_1`寄存器，`_gtr_deadloop`函数存入了`S3_6_C15_C8_2`寄存器。在整个kernelcache代码段里都没有搜索到对`_gxf_bootstrap_handler`函数的直接引用，因此可以推断出`S3_6_C15_C8_1`寄存器保存的地址应该是cpu进入`EL1_Guard
level`时首先要执行的函数。在另外一个初始化路径中也可以看到相同的ppl初始化代码。

    
    
    __start->_start_first_cpu->_arm_init->_cpu_machine_idle_init->_start_cpu->start_cpu
    
    start_cpu:
    
    S3_6_C15_C1_00x1
    
    S3_6_C15_C1_10x1
    
    S3_6_C15_C3_00x2020a506f020f0e0
    
    S3_6_C15_C1_50x2010000030100000
    
    S3_6_C15_C1_60x2020000030200000
    
    S3_6_C15_C1_70x2020a500f020f000
    
    
    S3_6_C15_C1_20x1
    
    S3_6_C15_C8_1_gxf_bootstrap_handler(虚拟地址)
    
    S3_6_C15_C8_2_gtr_deadloop(虚拟地址)
    
    S3_6_C15_C1_20x0

注意这两个初始化函数只是对`S3_6_C15_C8_1`寄存器进行了设置，并没有调用它。在内核启动的最后阶段有如下调用代码：

    
    
    _kernel_bootstrap_thread->machine_lockdown
    
    ADRP       X8, #_pmap_ppl_locked_down@PAGE
    
    MOV       W19, #1
    
    STR       W19, [X8,#_pmap_ppl_locked_down@PAGEOFF]
    
    BL        _gxf_enable

首先对`_pmap_ppl_locked_down`变量设置为1，这个状态表示ppl已经初始化完毕，el1代码可以向`EL1_Guard
level`请求服务了。然后调用`_gxf_enable`：

    
    
    _gxf_enable:
    
    fffffff008131e90     mov   x0, #0x1
    
    fffffff008131e94     msr   S3_6_C15_C1_2, x0
    
    fffffff008131e98     .long  0x00201420

在对`S3_6_C15_C1_2`寄存器赋值后，出现了0x00201420这个反汇编器无法识别的指令。那么这个有可能的两种情况，第一个假设0x00201420不是苹果cpu的新增指令，那么当cpu进行执行时，会产生exception异常，历史上，PAX团队曾经在异常处理代码里模拟了NX在32位处理器上的软件实现，但笔者翻遍了异常处理逻辑的所有代码，也没有发现对0x00201420这个数据或指令的特殊处理，因此可以断定0x00201420是苹果cpu新增的指令，在后面的reverse中，可以发现它是进入`EL1_Guard
level`的指令，0x00201400则是退出`EL1_Guard level`的指令。

在前面的分析中讲到`S3_6_C15_C8_1`寄存器保存的地址是进入`EL1_Guard
level`时首先要执行的地址，在前面的初始化时被设置为了`_gxf_bootstrap_handler`。

    
    
     _gxf_bootstrap_handler          ; DATA XREF: _bootstrap_instructions+9C↑o
    
    MRS       X0, #6, c15, c8, #3
    
    TBNZ       W0, #0, loc_FFFFFFF009811660
    
    ADRL       X0, _gxf_ppl_entry_handler ;
    
    MSR       #6, c15, c8, #1, X0
    
    ADRL       X0, _GuardedExceptionVectorsBase
    
    MSR       #0, c12, c0, #0, X0

首先判断`S3_6_C15_C8_3`寄存器的值是否为0，如果为0，就一直处于循环之中，可以推测出`S3_6_C15_C8_3`寄存器作用是进入`EL1_Guard
level`的锁机制。然后将`_gxf_ppl_entry_handler`函数重新存入了`S3_6_C15_C8_1`寄存器，也就是说下次进入`EL1_Guard
level`时将会执行`_gxf_ppl_entry_handler`函数。将`_GuardedExceptionVectorsBase`地址写入`VBAR_EL1`寄存器，也就是说当cpu在`EL1_Guard
level`时，`_GuardedExceptionVectorsBase`函数负责其异常处理逻辑。

    
    
    MRS       X1, #0, c0, c0, #5
    
    UBFX       X2, X1, #8, #8
    
    ADRL       X3, _cluster_offsets
    
    LDR       X2, [X3,X2,LSL#3]
    
    AND       X1, X1, #0xFF
    
    ADD       X1, X1, X2
    
    ADRL       X2, _pmap_cpu_data_array
    
    CMP       X1, #6
    
    B.CS       loc_FFFFFFF0098116A8
    
    MOV       X3, #0x180
    
    MADD       X1, X1, X3, X2

首先从`MPIDR_EL1`寄存器提取了cpu的cluster id和cpu
id，算出在`_pmap_cpu_data_array`数组中的索引。`_pmap_cpu_data_array`是一个`struct
pmap_cpu_data`类型的数组。在XNU的source code中有如下定义：

    
    
    struct pmap_cpu_data {
    
    \#if XNU_MONITOR
    
    void * ppl_kern_saved_sp;
    
    void * ppl_stack;
    
    arm_context_t * save_area;
    
    unsigned int ppl_state;
    
    \#endif
    
    }
    
    LDR       X1, [X1,#0x10]
    
    MOV       SP, X1

X1保存的是当前cpu的`struct
pmap_cpu_data`结构体指针，0x10偏移为`save_area`，它指向了`arm_context_t`类型的内存区域，将这个内存区域设置为`EL1_Guard
level`的sp地址。在从el1进入`EL1_Guard level`时，将全部的寄存器保存在这个区域。

    
    
    ADRP       X1, #_pmap_ppl_locked_down@PAGE
    
    LDR       X2, [X1,#_pmap_ppl_locked_down@PAGEOFF]
    
    CBZ       X2, loc_FFFFFFF0098116C0

接着判断`_pmap_ppl_locked_down`值是否为0，如果为0，则一直循环检查下去。在前面的`machine_lockdown`函数中已经将`_pmap_ppl_locked_down`设置为了1，所以会继续运行下面的代码：

    
    
    MOVK       X0, #0x2020,LSL#48
    
    MOVK       X0, #0xA506,LSL#32
    
    MOVK       X0, #0xF020,LSL#16
    
    MOVK       X0, #0xF0E0
    
    MSR       #6, c15, c3, #0, X0
    
    MOVK       X0, #0,LSL#48
    
    MOVK       X0, #0,LSL#32
    
    MOVK       X0, #0,LSL#16
    
    MOVK       X0, #5
    
    MSR       #6, c15, c1, #2, X0
    
    ADRL       X0, _invalid_ttep
    
    LDR       X0, [X0]
    
    MSR       #0, c2, c0, #0, X0

将0x2020a506f020f0e0赋值给了`S3_6_C15_C3_0`寄存器，将0x5赋值给了`S3_6_C15_C1_2`寄存器，将`_invalid_ttep`页表地址赋值给了`TTBR0_EL1`。

    
    
    SYS       #0, c8, c3, #0
    
    DSB       ISH
    
    ISB
    
    DCD 0x201400

执行0x201400指令，退出`EL1_Guard level`。

至此ppl全部初始化已经完成， el1代码可以请求`EL1_Guard level`的服务了。

## Ppl进入与退出

Ppl给el1代码提供了`_gxf_ppl_enter`接口用于请求其服务。

    
    
    _arm_fast_fault_ppl:
    
    mov   x15, #0x0
    
    b    _gxf_ppl_enter
    
    _arm_force_fast_fault_ppl:
    
    mov   x15, #0x1
    
    b    _gxf_ppl_enter
    
    _mapping_free_prime_ppl:
    
    mov   x15, #0x2
    
    b    _gxf_ppl_enter

这里只罗列部分函数，x15保存的是ppl服务表的索引。

    
    
    _gxf_ppl_enter:
    
    fffffff008131c3c     pacibsp
    
    fffffff008131c40     stp   x20, x21, [sp, #-0x20]! ; Latency: 6
    
    fffffff008131c44     stp   x29, x30, [sp, #0x10]  ; Latency: 6
    
    fffffff008131c48     add   x29, sp, #0x10
    
    fffffff008131c4c     mrs   x9, TPIDR_EL1
    
    fffffff008131c50     ldr   w10, [x9, #0x500]    ; Latency: 4
    
    fffffff008131c54     add   w10, w10, #0x1
    
    fffffff008131c58     str   w10, [x9, #0x500]    ; Latency: 4
    
    fffffff008131c5c     adrp   x14, 5867 ; _pmap_ppl_locked_down
    
    fffffff008131c60     add   x14, x14, #0x130
    
    fffffff008131c64     ldr   x14, [x14]        ; Latency: 4
    
    fffffff008131c68     cbz   x14, _ppl_bootstrap_dispatch
    
    fffffff008131c6c     mrs   x14, S3_6_C15_C8_0
    
    fffffff008131c70     cmp   x14, #0x0
    
    fffffff008131c74     b.ne   0xfffffff008131c74
    
    fffffff008131c78     mov   w10, #0x0
    
    fffffff008131c7c     .long  0x00201420

首先检查`_pmap_ppl_locked_down`是否为0，如果为0，说明ppl并没有初始化完成，直接跳转到`_ppl_bootstrap_dispatch`函数：

    
    
    CMP       X15, #0x47 ; 'G'
    
    B.CS       loc_FFFFFFF008131DD4
    
    ADRL       X9, _ppl_handler_table
    
    ADD       X9, X9, X15,LSL#3

X15保存的是`_ppl_handler_table`的索引，如果大于0x47,会触发panic。

    
    
    LDR       X10, [X9]
    
    BLRAA      X10, X9

跳转到`_ppl_handler_table[x15<<3]`去执行具体的服务函数。

    
    
    MOV       X20, X0
    
    BL        __enable_preemption
    
    MOV       X0, X20
    
    LDP       X29, X30, [SP,#arg_10]
    
    LDP       X20, X21, [SP+arg_0],#0x20
    
    RETAB

在没有进入`EL1_Guard level`情况下，直接通过ret返回。

如果`_pmap_ppl_locked_down`为1，则继续如下代码：

    
    
    fffffff008131c78     mov   w10, #0x0
    
    fffffff008131c7c     .long  0x00201420

将w10设置为0， 这个很重要，后面会讲到。

执行0x00201420进入`EL1_Guard level`, 前面在初始化时讲到cpu进入`EL1_Guard
level`时，会执行`S3_6_C15_C8_1`寄存器指定的地址，也就是`_gxf_ppl_entry_handler`。

    
    
    MSR       #5, #0
    
    MRS       X9, #6, c15, c8, #3 ; S3_6_C15_C8_3
    
    TBNZ       W9, #0, loc_FFFFFFF008131C88
    
    MRS       X12, #6, c15, c9, #1 ; S3_6_C15_C9_1
    
    MSR       #0, c13, c0, #4, X12 ; TPIDR_EL1
    
    MRS       X20, #0, c4, c0, #0 ; SPSR_EL1
    
    AND       X20, X20, #0x3C0 ; mask FIQ; SET EL3t
    
    B        _ppl_trampoline_start

首先将SPSel设置为0，然后判断`S3_6_C15_C8_3`是否为1，否则一直循环等待，这再次证明`S3_6_C15_C8_3`寄存器为进入`EL1_Guard
level`的锁机制。然后将`S3_6_C15_C9_1`寄存器的值写入`TPIDR_EL1`，说明它保存的是请求服务时的线程信息。将`SPSR_EL1`设置为`mask
FIQ; SET EL3t`，为何是EL3t？ 接着跳入`_ppl_trampoline_start`：

    
    
    MOVK       X14, #0x2020,LSL#48
    
    MOVK       X14, #0xA506,LSL#32
    
    MOVK       X14, #0xF020,LSL#16
    
    MOVK       X14, #0xF0E0 ; 0x2020a506f020f0e0
    
    MRS       X21, #6, c15, c3, #0
    
    CMP       X14, X21
    
    B. NE       loc_FFFFFFF00980D9AC

首先判断`S3_6_C15_C3_0`寄存器的值是否为0x2020a506f020f0e0，这个寄存器的作用笔者尚未搞清楚。

    
    
    CMP       X15, #0x47 ; 'G'
    
    B.CS       loc_FFFFFFF00980D9AC

再次判断x15合法范围。

    
    
    MRS       X12, #0, c0, c0, #5 ; MPIDR_EL1
    
    UBFX       X13, X12, #8, #8 ; get cluster id
    
    ADRL       X14, _cluster_offsets
    
    LDR       X13, [X14,X13,LSL#3] ; _cluster_offsets[index<<3]
    
    AND       X12, X12, #0xFF
    
    ADD       X12, X12, X13
    
    ADRL       X13, _pmap_cpu_data_array
    
    CMP       X12, #6
    
    C. CS       loc_FFFFFFF00980D92C
    
    MOV       X14, #0x180
    
    MADD       X12, X12, X14, X13

得到当前cpu的`struct pmap_cpu_data`结构体指针。

    
    
    LDR       W9, [X12,#0x18] ; _pmap_cpu_data->ppl_state

W9保存的是ppl的当前状态`ppl_state`，ppl的状态有3个定义：

    
    
    PPL_STATE_KERNEL
    
    PPL_STATE_DISPATCH
    
    PPL_STATE_EXCEPTION

`_ppl_trampoline_start`这个函数可以由`ppl_enter`由el1代码主动调用，也可以由`EL1_Guard
level`的异常处理调用，在后面会分析到。

    
    
    CMP       W9, #0  ; PPL_STATE_KERNEL
    
    B. EQ       loc_FFFFFFF00980D970

W9为0，即`PPL_STATE_KERNEL`，表示可以请求ppl服务。

    
    
    loc_FFFFFFF00980D970           ; CODE XREF: _ppl_trampoline_start+60↑j
    
    CMP       W10, #0

判断w10是否为0，注意在前面的`ppl_enter`路径中，已经将w10设置为了0，所以代码可以进行前进。

    
    
    B.NE       loc_FFFFFFF00980D9AC
    
    MOV       W13, #1
    
    STR       W13, [X12,#0x18] ; enter PPL_STATE_DISPATCH mode

更改`ppl_state`状态为1，即 `PPL_STATE_DISPATCH`，表示ppl正处在服务派发状态中。

    
    
    LDR       X9, [X12,#8] ; _pmap_cpu_data->ppl_stack
    
    MOV       X21, SP
    
    MOV       SP, X9

`_pmap_cpu_data->ppl_stack`保存的是ppl服务要使用的stack区域。注意`_pmap_cpu_data->save_area`保存的是进入`EL1_Guard
level`异常处理时保存全部寄存器用的栈区域。

    
    
    STR       X21, [X12] ; save old el1 sp

保存el1原来的sp到`_pmap_cpu_data->ppl_kern_saved_sp`，以后退出ppl服务时还要恢复原来的stack指针。

    
    
    ADRL       X9, _ppl_handler_table
    
    ADD       X9, X9, X15,LSL#3 ; _ppl_handler_table[index<<3]
    
    LDR       X10, [X9]
    
    B        _ppl_dispatch

X10保存了具体的服务函数地址`_ppl_handler_table[x15<<3]``，然后跳转到_ppl_dispatch`执行，在屏蔽了一些列中断后，进行执行：

    
    
    BLRAA      X10, X9

调用具体的ppl服务函数。

    
    
    __PPLTEXT:__text:FFFFFFF00980D9B8
    
    MOV       X15, #0
    
    MOV       SP, X21
    
    MOV       X10, X20
    
    STR       XZR, [X12]
    
    LDR       W9, [X12,#0x18] ; _pmap_cpu_data->ppl_state
    
    CMP       W9, #1  ; PPL_STATE_DISPATCH
    
    B.NE       loc_FFFFFFF00980D9D0
    
    MOV       W9, #0
    
    STR       W9, [X12,#0x18] ; PPL_STATE_KERNEL

服务执行完之后，要把`ppl_state`再次设置 `PPL_STATE_KERNEL`。

    
    
    B        ppl_return_to_kernel_mode

最后调用`ppl_return_to_kernel_mode`退出`EL1_Guard level`，返回el1代码。

    
    
    ADRL       X14, ppl_exit
    
    MSR       #0, c4, c0, #1, X14 ; ELR_EL1
    
    MRS       X14, #6, c15, c8, #3
    
    AND       X14, X14, #0xFFFFFFFFFFFFFFFE
    
    MSR       #6, c15, c8, #3, X14 ; S3_6_C15_C8_3
    
    MRS       X14, #0, c4, c0, #0 ; SPSR_EL1
    
    AND       X14, X14, #0xFFFFFFFFFFFFFC3F
    
    ORR       X14, X14, X10
    
    MSR       #0, c4, c0, #0, X14 ; SPSR_EL1 -> EL3h
    
    MRS       X14, #0, c13, c0, #4 ; TPIDR_EL1
    
    MSR       #6, c15, c9, #1, X14 ; S3_6_C15_C9_1
    
    DCQ 0x201400

首先将`ELR_EL1`设置为`ppl_exit`，然后将`S3_6_C15_C8_3`的最低位清0，然后将`SPSR_EL1`设置为
EL3h，注意`SPSR_EL1`的第2个bit设置为了1，在arm手册里这个bit是保留的，说明苹果处理器使用了这个bit代表ppl的执行状态，但是很奇怪为啥都设置为EL3h,而不是EL1h？随后将`TPIDR_EL1`值保存在了`S3_6_C15_C9_1`寄存器。

最后执行0x201400退出`EL1_Guard
level`，由于`ELR_EL1`寄存器保存的是`ppl_exit`，cpu跳转到`ppl_exit`继续执行,
`ppl_exit`恢复之前屏蔽的中断，然后使用ret指令返回。

上面分析的是一个正常通过`ppl_enter`请求ppl服务的路径。下面继续返回`_ppl_trampoline_start`代码。

    
    
    CMP       W9, #1  ; PPL_STATE_DISPATCH
    
    C. EQ       loc_FFFFFFF00980D9A4 ; _pmap_cpu_data_array->ppl_kern_saved_sp

如果当前`ppl_state`状态为`PPL_STATE_DISPATCH`，表示有其他cpu正在请求ppl服务，因此恢复之前通过`_pmap_cpu_data_array->ppl_kern_saved_sp`保存的栈，然后退出`EL1_Guard
level`，前面的路径已经分析过了。

    
    
    CMP       W9, #3  ; PPL_STATE_EXCEPTION
    
    B. NE       loc_FFFFFFF00980D9AC

如果`ppl_state`也不是`PPL_STATE_EXCEPTION`，则直接退出`EL1_Guard level`。

    
    
    CMP       W10, #3 ; PPL_STATE_EXCEPTION
    
    C. NE       loc_FFFFFFF00980D9AC
    
    MOV       W9, #1
    
    STR       W9, [X12,#0x18] ; PPL_STATE_DISPATCH
    
    LDR       X0, [X12,#0x10] ; _pmap_cpu_data_array->save_area
    
    MOV       SP, X0
    
    B        _return_to_ppl

将sp设置为`_pmap_cpu_data_array->save_area`，`_return_to_ppl`要使用这个栈恢复之前进入`EL1_Guard
level`异常处理时保存的全部寄存器值，恢复`cpsr, ELR_EL1`设置原来的调用地址，恢复bp,sp，通过eret返回原来的el1路径中。

为啥要判断w10的值是否为3？这个路径表示的是`EL1_Guard level`异常处理路径中要请求ppl服务。

`_GuardedExceptionVectorsBase`是`EL1_Guard
level`异常处理地址，我们看到它只对0x000的offset使用了有效函数，表明它只处理来自同层current
level的异常处理，再次证明`EL1_Guard level`也是在EL1 level上。

    
    
    __PPLTEXT:__text:FFFFFFF0098114B0 gtr_sync：
    
    MOV       X26, #1
    
    ADRL       X1, _fleh_synchronous ; ESR_EL1
    
    MSR       #0, c4, c0, #1, X1 ; ELR_EL1

可以看到`gtr_sync`把`_fleh_synchronous`赋值给了`ELR_EL1`， x26设置为1很关键，这是一个标识，后面会讲到。

    
    
    MOV       X0, SP
    
    DCD 0x201400

随后`gtr_sync`使用0x201400指令退出了`EL1_Guard level`，转而执行`el1
_fleh_synchronous`函数，这是el1内核异常处理的主要函数，这说明`EL1_Guard
level`的主要处理逻辑会使用el1内核代码，这也就解释了ppl为什么能保护内核态和用户态的数据。以前我们在使用el2做保护时，只能保护el1的数据，因为el1的使用的代码和数据都已经是映射好的，而el0层用户的代码和数据会涉及到很多缺页异常处理的逻辑，比如页表不存在，或者页表被交换到磁盘上，这会使el2的异常处理逻辑非常复杂。`EL1_Guard
level`使用el1内核代码的处理逻辑就简化了自身的代码逻辑，性能也会提升不少。

    
    
    __TEXT_EXEC:__text:FFFFFFF0081315CC _fleh_synchronous
    
    BL        _sleh_synchronous

`_fleh_synchronous`又调用了`_sleh_synchronous`，这个函数是异常处理逻辑的主要处理函数。

    
    
    CMP       X26, XZR
    
    B. EQ       loc_FFFFFFF00813161C

注意`_fleh_synchronous`是el1内核代码的处理逻辑，`EL1_Guard
level`是借用了它的代码，在前面看到`gtr_sync`把x26设置为了1，在`_fleh_synchronous`函数里表示此次请求来自`EL1_Guard
level`。

    
    
    MOV       X15, #0
    
    MOV       W10, #3
    
    DCB 0x20, 0x14, 0x20, 0

然后将x15设置为0，w10设置为3，最后调用0x201420再次进入`EL1_Guard
level`，此时就会跳转到`_ppl_trampoline_start`的异常处理请求路径里：

    
    
    CMP       W9, #3  ; PPL_STATE_EXCEPTION
    
    B.NE       loc_FFFFFFF00980D9AC
    
    CMP       W10, #3 ; PPL_STATE_EXCEPTION
    
    B.NE       loc_FFFFFFF00980D9AC
    
    MOV       W9, #1
    
    STR       W9, [X12,#0x18] ; PPL_STATE_DISPATCH
    
    LDR       X0, [X12,#0x10] ; _pmap_cpu_data_array->save_area
    
    MOV       SP, X0
    
    B        _return_to_ppl

`_return_to_ppl`恢复`EL1_Guard level`异常处理时保存的全部寄存器值，恢复cpsr,
`ELR_EL1`设置原来的调用地址，恢复bp,sp，通过eret返回原来的el1路径中。

## ppl服务

`_ppl_handler_table`数组保存的是ppl服务函数地址。

    
    
    _ppl_handler_table：
    
    _arm_force_fast_fault_internal
    
    _mapping_free_prime_internal
    
    _phys_attribute_clear_internal
    
    _phys_attribute_set_internal
    
    _pmap_batch_set_cache_attributes_internal
    
    _pmap_change_wiring_internal
    
    _pmap_create_options_internal
    
    _pmap_destroy_internal
    
    _pmap_enter_options_internal
    
    _pmap_find_pa_internal
    
    _pmap_insert_sharedpage_internal
    
    _pmap_is_empty_internal
    
    _pmap_map_cpu_windows_copy_internal
    
    _pmap_mark_page_as_ppl_page_internal
    
    _pmap_nest_internal
    
    _pmap_page_protect_options_internal
    
    _pmap_protect_options_internal
    
    _pmap_query_page_info_internal
    
    _pmap_query_resident_internal
    
    _pmap_reference_internal
    
    _pmap_remove_options_internal
    
    _pmap_return_internal
    
    _pmap_set_cache_attributes_internal
    
    _pmap_set_nested_internal
    
    _pmap_set_process_internal
    
    _pmap_switch_internal
    
    _pmap_switch_user_ttb_internal
    
    _pmap_clear_user_ttb_internal
    
    _pmap_unmap_cpu_windows_copy_internal
    
    _pmap_unnest_options_internal
    
    _pmap_footprint_suspend_internal
    
    _pmap_cpu_data_init_internal
    
    _pmap_release_ppl_pages_to_kernel_internal
    
    _pmap_set_jit_entitled_internal
    
    _pmap_load_legacy_trust_cache_internal
    
    _pmap_load_image4_trust_cache_internal
    
    _pmap_is_trust_cache_loaded_internal
    
    _pmap_lookup_in_static_trust_cache_internal
    
    _pmap_lookup_in_loaded_trust_caches_internal
    
    _pmap_cs_cd_register_internal
    
    _pmap_cs_cd_unregister_internal
    
    _pmap_cs_associate_internal
    
    _pmap_cs_lookup_internal
    
    _pmap_cs_check_overlap_internal
    
    _pmap_iommu_init_internal
    
    _pmap_iommu_iovmalloc_internal
    
    _pmap_iommu_map_internal
    
    _pmap_iommu_unmap_internal
    
    _pmap_iommu_iovmfree_internal
    
    _pmap_iommu_ioctl_internal
    
    _pmap_iommu_grant_page_internal
    
    _pmap_update_compressor_page_internal
    
    _pmap_trim_internal
    
    _pmap_ledger_alloc_init_internal
    
    _pmap_ledger_alloc_internal
    
    _pmap_ledger_free_internal
    
    _pmap_sign_user_ptr_internal
    
    _pmap_auth_user_ptr_internal
    
    _phys_attribute_clear_range_internal

可以看到ppl服务代码是非常复杂的，覆盖了物理内存和虚拟内存管理的方方面面。

### _pmap_mark_page_as_ppl_page_internal

我们先看下如何将一个物理页标记为ppl使用的物理页。

    
    
    _pmap_mark_page_as_ppl_page_internal：
    
    MOV       X19, X0
    
    ADRP       X23, #_vm_first_phys@PAGE ; x0(pa) > vm_first_phys && x0 < vm_last_phys
    
    LDR       X8, [X23,#_vm_first_phys@PAGEOFF]
    
    ADRP       X24, #_vm_last_phys@PAGE
    
    LDR       X9, [X24,#_vm_last_phys@PAGEOFF]
    
    CMP       X8, X0
    
    CCMP       X9, X0, #0, LS
    
    C. LS       loc_FFFFFFF0097FB5B0

X0保存的是要标记的物理地址pa，然后检查它是否在`_vm_first_phys与_vm_last_phys`之间，这是XNU管理的有效物理内存区间。

    
    
    LDR       X11, [X9,#_pp_attr_table@PAGEOFF]
    
    LDRSH      W10, [X11,X8,LSL#1]
    
    TBNZ       W10, #0x1F, loc_FFFFFFF0097FB580 ;
    
    ORR       W12, W10, #0x4000 ; pp_attr_table[pai] & 0x4000
    
    ADD       X11, X11, X8,LSL#1
    
    MOV       X13, X10
    
    CASALH      W13, W12, [X11]

`pp_attr_table[pai] &= 0x4000`，将pa对应的`pp_attr_table`进行标记。

    
    
    LDR       X9, [X21,#_pv_head_table@PAGEOFF]
    
    ADD       X8, X9, X8,LSL#3
    
    ADD       X8, X8, #4
    
    MOV       W9, #0x20000000
    
    LDCLRL      W9, W8, [X8] ;
    
    _pv_head_table[index] &= 0x20000000
    
    MOV       X0, X19
    
    BL        _phystokv
    
    ADD       X1, X0, #4,LSL#12
    
    MOV       W2, #3
    
    MOV       W3, #1
    
    BL        _pmap_set_range_xprr_perm

在对`pp_attr_table`和`_pv_head_table`进行标记后，调用`_pmap_set_range_xprr_perm`函数，这个函数作用是将虚拟地址va，到va
+
size之间的所有虚拟地址对应的页表属性进行转换，第三个参数代表的是原来页表的权限属性，第四个参数代表的是新的页表属性，这个函数用来在内核页表和ppl页表之间进行权限转换。

![图片](https://images.seebug.org/content/images/2021/11/26/1637910096000-3wwmhq.png-w331s)

![图片](https://images.seebug.org/content/images/2021/11/26/1637910096000-4qlikf.png-w331s)

![图片](https://images.seebug.org/content/images/2021/11/26/1637910097000-5emiui.png-w331s)

![图片](https://images.seebug.org/content/images/2021/11/26/1637910097000-6jjapz.png-w331s)

首先检查要进行转换的虚拟地址合法范围，只能在`physmap_base`和`physmap_end`或者gVirtBase和`static_memory_end`之间。接下来就是要循环遍历l3页表，l0页表基地址保存在`kernel_pmap->tte`，这个页表保存的是内核使用的页表地址，在内核启动时进行初始化。然后找到虚拟地址对应的l3
table地址，
循环遍历它的每个页表项，在这之前还需要将虚拟地址转换为物理地址，然后找到物理地址对应的`pv_head_table`表项，将其上锁。然后开始提取l3页表项的原始权限，请看如下代码逻辑：

    
    
    LDR       X8, [X20] ; 获得pte的内容
    
    TBZ       W8, #1, loc_FFFFFFF007B598C4 ;判断页表有效位
    
    TBNZ       X8, #0x34, loc_FFFFFFF007B598FC ; '4' ; ARM_PTE_HINT_MASK
    
    LSR       X9, X8, #4 
    
    AND       X9, X9, #0xC ; (*pte >> 4) & 0xc; 提取ap权限
    
    LSR       X10, X8, #0x35 ; '5' ; *pte >> 53，提取xn和pxn权限
    
    BFXIL      X9, X8, #0x35, #1 ; '5'
    
    AND       X10, X10, #2 ; (*pte >> 53) & 2
    
    ORR       X9, X9, X10
    
    CMP       X9, X26 ; 与函数的第三个参数expected_perm比较
    
    B. NE       loc_FFFFFFF007B59938

通过上面的提取后获得一个4bit的权限值，高2位代表ap权限，最低位代表pxn权限，第2bit代表xn权限。

所以可以推断出ppl新的权限模型为4个bit：

    
    
    new_perm
    
    X XXX
    
                /  /  \ \
    
    /  /     \ \
    
           54  53      7  6
    
    +-------------------------------------------------------    
    |      |xn|pxn| ...  |ap| |          |
    
    --------------------------------------------------------
El1和`EL1_Guard level`对应的权限关系可以参考m1n1的dock：

    
    
    HW: SPRR and GXF · AsahiLinux/docs Wiki · GitHub

![图片](https://images.seebug.org/content/images/2021/11/26/1637910097000-7yrvti.png-w331s)

通过搜索代码，发现有以下几个函数调用了`_pmap_set_range_xprr_perm`：

    
    
    _pmap_mark_page_as_kernel_page:
    
    MOV       W2, #1
    
    MOV       W3, #3
    
    B        _pmap_set_range_xprr_perm
    
    
    
    _pmap_mark_page_as_ppl_page_internal:
    
    MOV       W2, #3
    
    MOV       W3, #1
    
    BL        _pmap_set_range_xprr_perm

可以看到将普通的内核权限转化为ppl权限，是将3替换为1。反过来则是1替换为3。我们可以推测3为RW读写权限，1则为R只读权限。

    
    
    _pmap_static_allocations_done:
    
    MOV       W2, #3
    
    MOV       W3, #0xB
    
    BL        _pmap_set_range_xprr_perm

将`_bootstrap_pagetables`从0x3设置为0xb，`_bootstrap_pagetables`是内核启动时用到的临时页表。

    
    
    MOV       W2, #3
    
    MOV       W3, #1
    
    BL        _pmap_set_range_xprr_perm ;

将`_BootArgs`从0x3设置为0x1，`_BootArgs`是iboot加载内核时传给内核的参数。

    
    
    MOV       W2, #0x3
    
    MOV       W3, #1
    
    BL        _pmap_set_range_xprr_perm ;

将`_segPPLDATAB`从0x3设置为0x1，`_segPPLDATAB`为ppl的data段。

    
    
    MOV       W2, #0xA
    
    MOV       W3, #0x8
    
    BL        _pmap_set_range_xprr_perm ;

将`_segPPLTEXTB`从0xA设置为0x8，`_segPPLTEXTB`为ppl的text段。

    
    
    MOV       W2, #0xB
    
    MOV       W3, #0xB
    
    BL        _pmap_set_range_xprr_perm ;

将`_segPPLDATACONSTB`从0xB设置为0xB，`_segPPLDATACONSTB`为ppl的dataconst段。

    
    
    MOV       W2, #0x1
    
    MOV       W3, #0xB
    
    BL        _pmap_set_range_xprr_perm ;

将`_pmap_stacks_start_pa`从0x1设置为0xB，`_pmap_stacks_start_pa`为ppl使用的stack区域。

    
    
    _pmap_ledger_alloc_internal:
    
    MOV       W2, #1
    
    MOV       W3, #3
    
    BL        _pmap_set_range_xprr_perm ;
    
    
    
    _pmap_load_image4_trust_cache_internal:
    
    MOV       W2, #0xB
    
    MOV       W3, #1
    
    BL        _pmap_set_range_xprr_perm
    
    
    
    MOV       W2, #1
    
    MOV       W3, #0xB
    
    BL        _pmap_set_range_xprr_perm
    
    
    
    ### _pmap_release_ppl_pages_to_kernel_internal

它与`_pmap_mark_page_as_ppl_page_internal`是一个相反的操作，读者朋友可以自行阅读相关代码。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1768/>

