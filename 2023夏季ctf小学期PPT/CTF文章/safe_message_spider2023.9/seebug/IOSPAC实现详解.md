**作者： wzt  
本文为作者投稿，Seebug Paper 期待你的分享，凡经采用即有礼品相送！ 投稿邮箱：paper@seebug.org**

## 内核pac key初始化

    
    
    common_start
    
    mrs   x0, S3_4_C15_C0_4
    
    and   x1, x0, #0x2
    
    cbz   x1, 0xfffffff0081384d0
    
    orr   x0, x0, #0x1
    
    orr   x0, x0, #0x4
    
    msr   S3_4_C15_C0_4, x0
    
    Isb

首先探测下`S3_4_C15_C0_4`寄存器的第2个bit是否为0， 如果为0，
则一直等待下去，否则把其第1个和第3个比特位置1，结合后面对`_ml_set_kernelkey_enabled`的分析，可以推测出`S3_4_C15_C0_4`寄存器是苹果公司为增强pac而加入的控制寄存器。

    
    
    LDR       X0, =0xFEEDFACEFEEDFACF
    
    MSR       #0, c2, c1, #2, X0 ; APIBKeyLo_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c1, #3, X0 ; APIBKeyHi_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c2, #2, X0 ; APDBKeyLo_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c2, #3, X0 ; APDBKeyHi_EL1
    
    ADD       X0, X0, #1
    
    MSR       #4, c15, c1, #0, X0; ???
    
    ADD       X0, X0, #1
    
    MSR       #4, c15, c1, #1, X0; ???
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c1, #0, X0 ; APIAKeyLo_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c1, #1, X0 ; APIAKeyHi_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c2, #0, X0 ; APDAKeyLo_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c2, #1, X0 ; APDAKeyHi_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c3, #0, X0 ; APGAKeyLo_EL1
    
    ADD       X0, X0, #1
    
    MSR       #0, c2, c3, #1, X0 ; APGAKeyHi_EL1

Iphone12使用固定值0xFEEDFACEFEEDFACF依次初始化`APIAKey_EL1`、`APIBKey_EL1`、`APDAKey_EL1`、`APDBKey_EL1`、`APGAKey_EL1`寄存器。高版本的Iphone内核是否也使用固定值有待确认。

    
    
    MOVK       X0, #0,LSL#48
    
    MOVK       X0, #0,LSL#32
    
    MOVK       X0, #0x3454,LSL#16
    
    MOVK       X0, #0x593D ; 0x3454593d
    
    ORR       X0, X0, #0x40000000 ; 0x7454593d
    
    MSR       #0, c1, c0, #0, X0 ; SCTLR_EL1

很奇怪这里`sctlr_el1`只设置了EnIB位（笔者翻遍了代码，也没发现对`sctlr_el1`其他pac比特位的使用）。

## 用户进程pac key初始化

通过execve执行一个binary时，XNU内核会进行新进程pac key的初始化，XNU将每个进程的pac key保存在一个叫做shared
region的进程内存区域，这个区域可以被其他进程共享代码和数据，用来加快进程的启动速度，通常情况下一个进程只有一个shared
region区域，但是在支持pac的情况下，shared region根据不同的`shared_region_id`会有不同的shared
region区域，通过一个队列`_shared_region_jop_key_queue`链接起来，每个节点是一个`struct
shared_region_jop_key_map`类型的结构体，xnu source code有如下定义：

    
    
    typedef struct shared_region_jop_key_map {
    
        queue_chain_t  srk_queue;
    
       char      *srk_shared_region_id;
    
       uint64_t    srk_jop_key;
    
        os_refcnt_t   srk_ref_count;     /* count of tasks active with this shared_region_id */
    
    } *shared_region_jop_key_map_t;

成员`srk_jop_key`保存的是这个region所使用的pac key。下面我们来看下pac key是如何被初始化的。

    
    
    /*
    
    void
    
    shared_region_key_alloc(char *shared_region_id, bool inherit, uint64_t inherited_key)
    
     */
    
    exec_mach_imgact->_shared_region_key_alloc
    
    LDR       X8, [X24] ; _shared_region_jop_key_queue
    
    CMP       X8, X24
    
    B. EQ       loc_FFFFFFF007B33338 ;

遍历`_shared_region_jop_key_queue`，如果队列为空，跳转到后面去申请一个新的`shared_region`节点。

    
    
    MOV       X9, X8
    
    LDR       X10, [X9,#0x10]
    
    MOV       X11, X22
    
    LDRB       W12, [X10]
    
    LDRB       W13, [X11]
    
    CMP       W12, W13
    
    B.NE       loc_FFFFFFF007B3332C
    
    ADD       X11, X11, #1
    
    ADD       X10, X10, #1
    
    CBNZ       W12, loc_FFFFFFF007B3330C
    
    B        loc_FFFFFFF007B33450 ; srk_ref_count
    
    LDR       X9, [X9]
    
    CMP       X9, X24
    
    C. NE       loc_FFFFFFF007B33304

循环遍历每个`shared_region`节点，如果节点名与第一个参数相同，证明存在一个要匹配的节点。

    
    
    __TEXT_EXEC:__text:FFFFFFF007B33450
    
    E ADD       X0, X9, #0x20 ; ' ' ; srk_ref_count
    
    MOV       W8, #1__TEXT_EXEC:__text:FFFFFFF007B33458         LDADD      W8, W8, [X0] ; srk_ref_count++

将引用计数`srk_ref_count`加1.

    
    
    CBZ       W8, loc_FFFFFFF007B33554
    
    MOV       W10, #0xFFFFFFF
    
    CMP       W8, W10
    
    B. CS       loc_FFFFFFF007B33558

判断引用计数是否溢出

    
    
    MOV       X22, X21 ; x21 == 0
    
    MOV       X21, X9
    
    CBZ       W20, loc_FFFFFFF007B33488 ; inherit == 0
    
    LDR       X8, [X21,#0x18] ; inherit == 1 -> srk_jop_key
    
    LDR       X9, [SP,#0x70+var_60]
    
    CMP       X8, X9  ; arg3: inherited_key
    
    C. NE       loc_FFFFFFF007B3356C

如果第二个参数inherit为1，并且此`shared_region`保存的pac key与第三个参数不相同，则panic，否则直接返回，不需要更新pac
key。

下面看下队列如果为空，或者没有找到要匹配到的`shared_region_id`的后续处理流程。

    
    
    ADRL       X0, _KHEAP_DEFAULT
    
    MOV       W1, #0x28 ; '('
    
    MOV       W2, #0
    
    ADRL       X3, _shared_region_key_alloc.site
    
    BL        _kalloc_ext

分配一个新的`struct shared_region_jop_key_map`结构体

    
    
    MOV       X21, X0 ; new struct shared_region_jop_key_map
    
    MOV       X0, X22 ; __s
    
    BL        _strlen ; shared_region_id

计算参数`1shared_region_id`的长度

    
    
    ADD       W28, W0, #1
    
    ADRL       X0, _KHEAP_DATA_BUFFERS
    
    MOV       X1, X28
    
    MOV       W2, #0
    
    ADRL       X3, _shared_region_key_alloc.site.3
    
    BL        _kalloc_ext ; alloc shared_region_id buffer

分配`shared_region_id`内存

    
    
    STR       X0, [X21,#0x10] ; set srk_shared_region_id

保存`shared_region_id`到`struct shared_region_jop_key_map`对应成员。

    
    
    MOV       X1, X22 ; __source
    
    MOV       X2, X28 ; __size
    
    LDR       X23, [SP,#0x70+var_60]
    
    BL        _strlcpy ; strlcpy(srk_shared_region_id, shared_region_id, size);

拷贝`shared_region_id`。

    
    
    MOV       W8, #1
    
    STR       W8, [X21,#0x20] ; srk_ref_count = 1

引用计数`srk_ref_count`初始化为1。

    
    
    ADRP       X8, #_diversify_user_jop@PAGE
    
    LDR       W9, [X8,#_diversify_user_jop@PAGEOFF]
    
    CMP       W9, #0
    
    CSET       W8, NE
    
    TST       W8, W20 ; arg2: inherit
    
    MOV       X8, #0xFEEDFACEFEEDFAD5
    
    CSEL       X8, X23, X8, NE ; x23: arg3 inherit

如果`diversify_user_jop`为1并且第2个参数inherit也为1，x8被设置为第三个参数inherit，否则设置为0xFEEDFACEFEEDFAD5。

    
    
    ADRL       X24, _shared_region_jop_key_queue
    
    CBZ       W9, loc_FFFFFFF007B33444
    
    TBNZ       W20, #0, loc_FFFFFFF007B33444
    
    MOV       X0, X22 ; __s
    
    BL        _strlen
    
    CBZ       X0, loc_FFFFFFF007B33434 ; strlen(shared_region_id) == 0

如果`shared_region_id`长度为0， x8设置为0xFEEDFACEFEEDFAD5。我们看到用户进程的pac key居然和内核的pac
key0xFEEDFACEFEEDFACF值很接近！

    
    
    __TEXT_EXEC:__text:FFFFFFF007B333FC
    
    LDR       X8, [X19]
    
    LDR       X0, [X26,#_prng_ctx@PAGEOFF]
    
    BLRAA      X8, X28
    
    LDR       X8, [X19,#(qword_FFFFFFF0076E7760 - 0xFFFFFFF0076E7758)]
    
    LDR       X0, [X26,#_prng_ctx@PAGEOFF]
    
    MRS       X9, #0, c13, c0, #4 ; TPIDR_EL1
    
    LDR       X9, [X9,#0x4F8]
    
    LDRH       W1, [X9]
    
    ADD       X3, SP, #0x70+var_58
    
    MOV       W2, #8
    
    BLRAA      X8, X25
    
    LDR       X8, [SP,#0x70+var_58]
    
    CBZ       X8, loc_FFFFFFF007B333FC

获取一个随机数，赋值给x8。

    
    
    STR       X8, [X21,#0x18]

X8为要保存的pac key值。

总结以下，一个进程可以继承父进程的pac key，可以是个随机值，还可以是固定值0xFEEDFACEFEEDFAD5。

这里还存在另一个安全问题，虽然把生成随机数的两个函数指针都使用pac签名过，但是pac计算过程中使用的context值居然是个固定的4个字节值：0x2ABE和0x9BF6。这会弱化随机数生成函数的安全性。

## 进程之间切换pac

由于每个进程的pac key可能不同，所以在进程切换的时候，也需要切换pac key。

    
    
    _Switch_context
    
    STR       XZR, [X3,#0x78] ; SS64_KERNEL_PC
    
    MOV       W4, #0x100004 ; PSR64_KERNEL_POISON
    
    STR       W4, [X3,#0x80] ; SS64_KERNEL_CPSR
    
    STP       X0, X1, [SP,#var_10]!
    
    STP       X2, X3, [SP,#0x10+var_20]!
    
    STP       X4, X5, [SP,#0x20+var_30]!
    
    MOV       X0, X3
    
    MOV       X1, #0
    
    MOV       W2, W4
    
    MOV       X3, X30
    
    MOV       X4, X16
    
    MOV       X5, X17
    
    BL        _ml_sign_kernel_thread_state ; compute old thread pac code.

在进程切换前，首先计算处当前进程的thread state pac值。linux内核也提供了pac服务，但是没有对thread状态做校验。

    
    
    __TEXT_EXEC:__text:FFFFFFF008139A8C _ml_sign_kernel_thread_state       ; CODE PACGA      X1, X1, X0
    
    AND       X2, X2, #0xFFFFFFFFDFFFFFFF
    
    PACGA      X1, X2, X1
    
    PACGA      X1, X3, X1
    
    PACGA      X1, X4, X1
    
    PACGA      X1, X5, X1
    
    STR       X1, [X0,#0x88] ; struct arm_kernel_saved_state->jophash
    
    RET

Pacga指令用于计算大块的内存区域，可以看到XNU使用pacga指令依次对x0: The ARM context pointer、x1: PC value
to sign、x2: CPSR value to sign、x3: LR to sign、x16、x17做计算生成pac。

X0是一个`struct arm_kernel_save_state`的数据结构：

    
    
     struct arm_kernel_saved_state {
    
    uint64_t x[12];   /* General purpose registers x16-x28 */
    
    uint64_t fp;     /* Frame pointer x29 */
    
    uint64_t lr;     /* Link register x30 */
    
    uint64_t sp;     /* Stack pointer x31 */
    
    uint64_t pc;     /* Program counter */
    
    uint32_t cpsr;    /* Current program status register */
    
    uint64_t jophash;
    
    } __attribute__((aligned(16)));

在生成当前进程的thread state pac后，开始校验下要切换的进程thread
state状态，如果校验不过，证明要切换的进程状态被篡改过，系统直接panic。

    
    
    LDR       X3, [X2,#0x498] ; new TH_KSTACKPTR
    
    MOV       X20, X0
    
    MOV       X21, X1
    
    MOV       X22, X2
    
    MOV       X0, X3
    
    LDR       W2, [X0,#0x80] ; new SS64_KERNEL_CPSR
    
    DMB       LD
    
    LDR       X1, [X0,#0x78] ; new SS64_KERNEL_PC
    
    LDP       X16, X17, [X0]
    
    MOV       X25, X3
    
    MOV       X26, X4
    
    MOV       X27, X5
    
    MOV       X23, X1
    
    MOV       X24, X2
    
    LDR       X3, [X0,#0x68]
    
    MOV       X4, X16
    
    MOV       X5, X17
    
    BL        _ml_check_kernel_signed_state ; check new thread pac code.
    
    __TEXT_EXEC:__text:FFFFFFF008139AEC _ml_check_kernel_signed_state      ; CODE PACGA      X1, X1, X0
    
    AND       X2, X2, #0xFFFFFFFFDFFFFFFF
    
    PACGA      X1, X2, X1
    
    PACGA      X1, X3, X1
    
    PACGA      X1, X4, X1
    
    PACGA      X1, X5, X1
    
    LDR       X2, [X0,#0x88]

从`struct arm_kernel_saved_state`结构体提取pac code。

    
    
    CMP       X1, X2
    
    B.NE       loc_FFFFFFF008139B14
    
    RET

相同返回上层函数。

    
    
    __TEXT_EXEC:__text:FFFFFFF008139B14 ;
    
    PACIBSP
    
    STP       X29, X30, [SP,#var_10]!
    
    MOV       X29, SP
    
    BL        _panic

不相同则panic系统。

    
    
    LDR       X5, [X2,#0x4F8]
    
    MOV       W6, #0
    
    LDR       X3, [X2,#0x508]
    
    LDR       X4, [X5,#0x200]
    
    CMP       X3, X4
    
    B.EQ       loc_FFFFFFF008138B48
    
    STR       X3, [X5,#0x200]
    
    MSR       #0, c2, c1, #2, X3 ; APIBKeyLo_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c1, #3, X3 ; APIBKeyHi_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #2, X3 ; APDBKeyLo_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #3, X3 ; APDBKeyHi_EL1

加载新进程的pac key到对应的系统寄存器。

## 内核pac与用户进程pac切换

### 进入内核

进程每次通过系统调用进入内核或者发生错误进入内核异常处理流程时，需要把进程的pac key切换为内核的pac key。

    
    
    __TEXT_EXEC:__text:FFFFFFF008131410 fleh_dispatch64
    
    MOVK       X2, #0xFEED,LSL#48
    
    MOVK       X2, #0xFACE,LSL#32
    
    MOVK       X2, #0xFEED,LSL#16
    
    MOVK       X2, #0xFAD5 ; 0xFEEDFACEFEEDFAD5
    
    MRS       X3, #0, c13, c0, #4 ; TPIDR_EL1
    
    LDR       X3, [X3,#0x4F8]
    
    LDR       X4, [X3,#0x208]
    
    CMP       X2, X4
    
    B.EQ       loc_FFFFFFF0081314F0
    
    MSR       #0, c2, c1, #0, X2 ; APIAKeyLo_EL1
    
    ADD       X4, X2, #1
    
    MSR       #0, c2, c1, #1, X4 ; APIAKeyHi_EL1
    
    ADD       X4, X4, #1
    
    MSR       #0, c2, c2, #0, X4 ; APDAKeyLo_EL1
    
    ADD       X4, X4, #1
    
    MSR       #0, c2, c2, #1, X4 ; APDAKeyHi_EL1
    
    STR       X2, [X3,#0x208]

在进入内核时，首先要更新`APIAKey_EL1`和`APDAKey_EL1`为固定值0xFEEDFACEFEEDFAD5极其增值。

    
    
    MOV       X21, X1
    
    MOV       X20, X30
    
    MOV       X1, X22
    
    MOV       W2, W23
    
    MOV       X3, X20
    
    MOV       X4, X16
    
    MOV       X5, X17
    
    BL        _ml_sign_thread_state

更新完pac key值，马上对当前进程的thread state进行签名。

### 退出内核

    
    
    __TEXT_EXEC:__text:FFFFFFF00813197C exception_return_unint_tpidr_x3_dont_trash_x18
    
    MOV       X0, SP
    
    LDR       W2, [X0,#arg_110]
    
    LDR       X1, [X0,#arg_108]
    
    LDP       X16, X17, [X0,#arg_88]
    
    MOV       X22, X3
    
    MOV       X23, X4
    
    MOV       X24, X5
    
    MOV       X20, X1
    
    MOV       X21, X2
    
    LDR       X3, [X0,#arg_F8]
    
    MOV       X4, X16
    
    MOV       X5, X17
    
    BL        _ml_check_signed_state

在退出内核到用户态前，需要再次校验下当前进程的thread state，如果发生错误，则panic系统。

    
    
    LDR       X1, [X2,#0x510]
    
    LDR       X2, [X2,#0x4F8]
    
    LDR       X3, [X2,#0x208]
    
    CMP       X1, X3
    
    B.EQ       loc_FFFFFFF008131A3C
    
    MSR       #0, c2, c1, #0, X1 ; APIAKeyLo_EL1
    
    ADD       X3, X1, #1
    
    MSR       #0, c2, c1, #1, X3 ; APIAKeyHi_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #0, X3 ; APDAKeyLo_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #1, X3 ; APDAKeyHi_EL1
    
    STR       X1, [X2,#0x208]

恢复进程使用的pac key。

## 进程thread state pac的初始化

前面提到在进程切换时，需要验证进程的thread state pac，那么它是在何时初始化的呢？

答案在进程初始化stack时进行thread state的pac计算。

    
    
    _machine_stack_attach
    
    STR       X1, [X0,#0x78] ; struct arm_kernel_saved_state->pc
    
    MOV       X2, #0x100004
    
    STR       W2, [X0,#0x80] ; struct arm_kernel_saved_state->cpsr
    
    ADRL       X3, _thread_continue
    
    STR       X3, [X0,#0x68] ; struct arm_kernel_saved_state->lr
    
    MOV       X4, XZR
    
    MOV       X5, XZR
    
    STP       X4, X5, [X0]
    
    MOV       X6, X30
    
    BL        _ml_sign_kernel_thread_state ; sign thread state.

## Ppl相关

Ppl提供了两个服务用来给用户进程数据进行签名与验签。

### _pmap_sign_user_ptr

    
    
    __TEXT_EXEC:__text:FFFFFFF007B609A0 _pmap_sign_user_ptr
    
    ADD       X29, SP, #0x30
    
    MOV       X19, X0
    
    MRS       X23, #3, c4, c2, #1 ; DAIFSet
    
    TBNZ       W23, #7, loc_FFFFFFF007B609D0 ; TPIDR_EL1
    
    MSR       #6, #7

关闭DAIF中断

    
    
    MRS       X8, #0, c13, c0, #4 ; TPIDR_EL1
    
    LDR       X8, [X8,#0x4F8]
    
    LDR       X20, [X8,#0x208]
    
    MOV       W0, #0
    
    MOV       X1, X3
    
    BL        _ml_set_kernelkey_enabled

将0作为参数传递给`_ml_set_kernelkey_enabled`。

    
    
    __TEXT_EXEC:__text:FFFFFFF008139374 _ml_set_kernelkey_enabled        
    
    MRS       X2, #0, c13, c0, #4 ; TPIDR_EL1
    
    LDR       X2, [X2,#0x4F8]
    
    LDR       X3, [X2,#0x208]
    
    CMP       X1, X3
    
    B. EQ       loc_FFFFFFF0081393A8 ; S3_4_C15_C0_4

如果当前进程的pac key和用户传递进来的pac key相等，则直接跳转到后面。

    
    
    MSR       #0, c2, c1, #0, X1 ; APIAKeyLo_EL1
    
    ADD       X3, X1, #1
    
    MSR       #0, c2, c1, #1, X3 ; APIAKeyHi_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #0, X3 ; APDAKeyLo_EL1
    
    ADD       X3, X3, #1
    
    MSR       #0, c2, c2, #1, X3 ; APDAKeyHi_EL1
    
    STR       X1, [X2,#0x208]

依次切换系统寄存器`APIAKey_EL1`、`APDAKey_EL1`，可以看到ppl只用key A来签名用户代码或数据。

    
    
    MRS       X1, #4, c15, c0, #4 ; S3_4_C15_C0_4
    
    ORR       X3, X1, #4
    
    AND       X2, X1, #0xFFFFFFFFFFFFFFFB
    
    CMP       W0, #0
    
    CSEL       X1, X2, X3, EQ
    
    MSR       #4, c15, c0, #4, X1 ; S3_4_C15_C0_4
    
    ISB
    
    RET

如果传递给`_ml_set_kernelkey_enabled`函数的第一个参数为0，那么将`S3_4_C15_C0_4`的第3个bit置0，否则置1。

回到`_pmap_sign_user_ptr`

    
    
    CMP       W22, #2
    
    B.EQ       loc_FFFFFFF007B609FC
    
    CBNZ       W22, loc_FFFFFFF007B60A34
    
    PACIA      X19, X21
    
    B        loc_FFFFFFF007B60A00
    
    PACDA      X19, X21

如果第2个参数为2，则使用pacda对第1个参数签名，如果为0，使用pacia进行签名，如果不是0，也不是2， 则panic系统。

    
    
    MOV       W0, #1
    
    MOV       X1, X20
    
    BL        _ml_set_kernelkey_enabled

将1作为参数传递给`_ml_set_kernelkey_enabled`。

    
    
    _ml_set_kernelkey_enabled(0, pac_key)
    
    ...
    
    Pacia/pacib
    
    ...
    
    _ml_set_kernelkey_enabled(1, pac_key)

因此我们可以推测出`S3_4_C15_C0_4`的第2个bit为上锁功能， 0代表上锁，1代表解锁。

### _pmap_auth_user_ptr

    
    
    AUTIA      X19, X21
    
    B        loc_FFFFFFF007B60AD4
    
    AUTDA      X19, X21
    
    B        loc_FFFFFFF007B60AD4
    
    AUTDB      X19, X21
    
    B        loc_FFFFFFF007B60AD4
    
    AUTIB      X19, X21

这里我们看到`_pmap_auth_user_ptr`在验签的时候还使用了key b，而`_ml_set_kernelkey_enabled`只设置了key
a， 说明了key a是进程相关的，而key b是进程不相关的， XNU源码里定义了以下几种类型的pac key：

    
    
    EXTERNAL_HEADERS/ptrauth.h
    
    typedef enum {
    
     ptrauth_key_asia = 0,
    
     ptrauth_key_asib = 1,
    
     ptrauth_key_asda = 2,
    
     ptrauth_key_asdb = 3,
    
    
    
     /* A process-independent key which can be used to sign code pointers.
    
       Signing and authenticating with this key is a no-op in processes
    
       which disable ABI pointer authentication. */
    
     ptrauth_key_process_independent_code = ptrauth_key_asia,
    
    
    
     /* A process-specific key which can be used to sign code pointers.
    
       Signing and authenticating with this key is enforced even in processes
    
       which disable ABI pointer authentication. */
    
     ptrauth_key_process_dependent_code = ptrauth_key_asib,
    
    
    
     /* A process-independent key which can be used to sign data pointers.
    
       Signing and authenticating with this key is a no-op in processes
    
       which disable ABI pointer authentication. */
    
     ptrauth_key_process_independent_data = ptrauth_key_asda,
    
    
    
     /* A process-specific key which can be used to sign data pointers.
    
       Signing and authenticating with this key is a no-op in processes
    
       which disable ABI pointer authentication. */
    
     ptrauth_key_process_dependent_data = ptrauth_key_asdb,
    
    
    
     /* The key used to sign C function pointers.
    
       The extra data is always 0. */
    
     ptrauth_key_function_pointer = ptrauth_key_process_independent_code,
    
    
    
     /* The key used to sign return addresses on the stack.
    
       The extra data is based on the storage address of the return address.
    
       On ARM64, that is always the storage address of the return address plus 8
    
       (or, in other words, the value of the stack pointer on function entry) */
    
     ptrauth_key_return_address = ptrauth_key_process_dependent_code,
    
    
    
     /* The key used to sign frame pointers on the stack.
    
       The extra data is based on the storage address of the frame pointer.
    
       On ARM64, that is always the storage address of the frame pointer plus 16
    
       (or, in other words, the value of the stack pointer on function entry) */
    
     ptrauth_key_frame_pointer = ptrauth_key_process_dependent_data,
    
    
     /* The key used to sign block function pointers, including:
    
        invocation functions,
    
        block object copy functions,
    
        block object destroy functions,
    
        __block variable copy functions, and
    
        __block variable destroy functions.
    
       The extra data is always the address at which the function pointer
    
       is stored.
    
    
    
       Note that block object pointers themselves (i.e. the direct
    
       representations of values of block-pointer type) are not signed. */
    
     ptrauth_key_block_function = ptrauth_key_asia,
    
    
    
     /* The key used to sign C++ v-table pointers.
    
       The extra data is always 0. */
    
     ptrauth_key_cxx_vtable_pointer = ptrauth_key_asda,
    
    
    
     /* Other pointers signed under the ABI use private ABI rules. */
    
    
    
    } ptrauth_key;

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1777/>

