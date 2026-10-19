# Linux kernel 4.20 BPF 整数溢出-堆溢出漏洞及其利用

阅读量 **347301**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-29 16:09:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01ed9fb915a41f6eeb.png)

## 内容简介

近日，我发现Linux内核BPF模块中一个质量较高linux内核堆溢出漏洞([已向linux社区提交漏洞补丁](https://www.mail-archive.com/netdev@vger.kernel.org/msg256054.html)）。

我们可以100%稳定触发这个漏洞，并且可以利用它来进行本地提权获得root权限。这篇文章主要分析漏洞的成因以及基本漏洞利用方法。

## 漏洞模块

BPF(Berkeley Packet
Filter)模块[1]是用于支持用户态自定义包过滤方法的内核模块，目前各大Linux发行版都默认开启了bpf支持，关于bpf官方文档的介绍如下：

> Linux Socket Filtering (LSF) is derived from the Berkeley Packet Filter.  
>  Though there are some distinct differences between the BSD and Linux  
>  Kernel filtering, but when we speak of BPF or LSF in Linux context, we  
>  mean the very same mechanism of filtering in the Linux kernel.
>
> BPF allows a user-space program to attach a filter onto any socket and  
>  allow or disallow certain types of data to come through the socket. LSF  
>  follows exactly the same filter code structure as BSD’s BPF, so referring  
>  to the BSD bpf.4 manpage is very helpful in creating filters.

## 漏洞分析

###  引入时间

该漏洞位于kernel/bpf/queue_stack_maps.c文件中，于2018-10-19在commit

[f1a2e44a3aeccb3ff18d3ccc0b0203e70b95bd92](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/kernel/bpf?id=f1a2e44a3aeccb3ff18d3ccc0b0203e70b95bd92)中为bpf模块引入了名为queue/stack
map的新功能。

> Queue/stack maps implement a FIFO/LIFO data storage for ebpf programs.  
>  These maps support peek, pop and push operations that are exposed to eBPF  
>  programs through the new bpf_map[peek/pop/push] helpers. Those operations  
>  are exposed to userspace applications through the already existing  
>  syscalls in the following way:
>
> BPF_MAP_LOOKUP_ELEM -> peek
>
> BPF_MAP_LOOKUP_AND_DELETE_ELEM -> pop
>
> BPF_MAP_UPDATE_ELEM -> push

###  影响范围

该漏洞影响Linux Kernel 4.20rc1-4.20rc4，主要Linux发行版并不受其影响。

###  整数溢出

这枚漏洞的根本成因是在创建queue_stack_map时发生的整数溢出导致申请出的对象偏小，函数调用链如下：

    
    
    __x64_sys_bpf() 
      ->map_create()
        ->find_and_alloc_map()
          ->queue_stack_map_alloc()
    

漏洞函数queue_stack_map_alloc如下：

    
    
    static struct bpf_map *queue_stack_map_alloc(union bpf_attr *attr)
    {
        int ret, numa_node = bpf_map_attr_numa_node(attr);
        struct bpf_queue_stack *qs;
        u32 size, value_size;
        u64 queue_size, cost;
        size = attr->max_entries + 1; //整数溢出漏洞点
        value_size = attr->value_size;
        queue_size = sizeof(*qs) + (u64) value_size * size;
        cost = queue_size;
        if (cost >= U32_MAX - PAGE_SIZE)
            return ERR_PTR(-E2BIG);
        cost = round_up(cost, PAGE_SIZE) >> PAGE_SHIFT;
        ret = bpf_map_precharge_memlock(cost);
        if (ret < 0)
            return ERR_PTR(ret);
        qs = bpf_map_area_alloc(queue_size, numa_node); //申请过小的堆块
        if (!qs)
            return ERR_PTR(-ENOMEM);
        memset(qs, 0, sizeof(*qs));
        bpf_map_init_from_attr(&qs->map, attr);
        qs->map.pages = cost;
        qs->size = size;
        raw_spin_lock_init(&qs->lock);
        return &qs->map;
    }
    

上述函数在计算size时，使用了用户传入的参数attr->max_entries。由于size的类型是u32,
如果attr->max_entries=0xffffffff，那么attr->max_entries+1时就会发生整数溢出使得size=0。后续在bpf_map_area_alloc函数中会申请一块大小为queue_size的堆内存，queue_size的大小由以下表达式计算：

    
    
    sizeof(*qs) + (u64) value_size * size; // value_size 和 size我们都可控
    

可以看出，由于`size`在之前的计算过程中发生整数溢出变成了0，分配的大小只有`sizeof(*qs)`。

###  堆溢出

之后，可以在另一个bpf系统调用update这块map过程中，向这块过小的queue stack区域拷入数据，导致内核堆溢出。调用链如下：

    
    
    __x64_sys_bpf()
      ->map_update_elem()
        ->queue_stack_map_push_elem()//堆溢出
    

其中发生溢出的是queue_stack_map_hash_elem()函数中的memcpy调用。由源码可知，memcpy的dst就是上面申请的queue
stack区域，src是由用户态拷入的大小为qs->map.value_size的buffer,
拷贝长度由创建queue_stack时用户提供的attr.value_size决定，因此拷贝长度用户可控。

queue_stack_map_push_elem()函数如下：

    
    
    static int queue_stack_map_push_elem(struct bpf_map *map, void *value,
                         u64 flags)
    {
        struct bpf_queue_stack *qs = bpf_queue_stack(map);
        unsigned long irq_flags;
        int err = 0;
        void *dst;
    
    
        bool replace = (flags & BPF_EXIST);
    
        if (flags & BPF_NOEXIST || flags > BPF_EXIST)
            return -EINVAL;
    
        raw_spin_lock_irqsave(&qs->lock, irq_flags);
    
        if (queue_stack_map_is_full(qs)) {
            if (!replace) {
                err = -E2BIG;
                goto out;
            }
            if (unlikely(++qs->tail >= qs->size))
                qs->tail = 0;
        }
    
        dst = &qs->elements[qs->head * qs->map.value_size];
        memcpy(dst, value, qs->map.value_size); //堆溢出
    
        if (unlikely(++qs->head >= qs->size))
            qs->head = 0;
    
    out:
        raw_spin_unlock_irqrestore(&qs->lock, irq_flags);
        return err;
    }
    

可以看出`memcpy(dst, value, qs->map.value_size);
//堆溢出`处是一个明显的堆溢出漏洞。由于`dst`堆块在之前计算堆块分配大小的过程中发生了整数溢出大小只有`sizeof(struct
bpf_queue_stack)`也就是256个字节，如果`value_size > 256 - (&qs->elements -&qs)`，就会发生越界拷贝。

## 漏洞利用：

利用之前，我们先来总结一下该漏洞提供的基本能力：现在我们有一个整数溢出导致的堆溢出漏洞，溢出的长度完全可控，溢出的内容也完全可控，发生溢出的堆块(struct
bpf_queue_stack)大小是256个字节。

漏洞关键数据结构`struct bpf_queue_stack`定义如下：

    
    
    struct bpf_queue_stack {
        struct bpf_map map;
        raw_spinlock_t lock;
        u32 head, tail;
        u32 size; 
    
        char elements[0] __aligned(8);
    };
    struct bpf_map {
        const struct bpf_map_ops *ops ____cacheline_aligned; //虚表
        struct bpf_map *inner_map_meta;
        void *security;
        enum bpf_map_type map_type;
        u32 key_size;
        u32 value_size;
        u32 max_entries;
        u32 map_flags;
        u32 pages;
        u32 id;
        int numa_node;
        u32 btf_key_type_id;
        u32 btf_value_type_id;
        struct btf *btf;
        bool unpriv_array;
        struct user_struct *user ____cacheline_aligned;
        atomic_t refcnt;
        atomic_t usercnt;
        struct work_struct work;
        char name[BPF_OBJ_NAME_LEN];
    };
    

我们需要在溢出之前完成堆风水，将一个包含函数指针或写指针的敏感指针“受害者”对象放在发生溢出的堆块后面。

Linux内核的堆分配机制在分配堆块时，倾向于为相近种类，相同大小的堆块申请一块大内存，在这篇内存里存放的都是相同大小和相近类型的堆块。

对于这个漏洞来说，虽然不能使用常见的`struct file_struct`来充当受害者对象，但漏洞对象本身就可以充当受害者对象。这是因为`struct
bpf_queue_stack`的第一个成员`bpf_map_ops`就是一个包含许多函数指针的虚表指针，我们只需要连续申请两个`bpf_queue_stack`，就可以让第一个`bpf_queue_stack`发生溢出，改写后一个`bpf_queue_stack`的虚表指针。

在`bpf_map_ops`这个虚表里面有许多的函数指针：

    
    
    const struct bpf_map_ops queue_map_ops = {
        .map_alloc_check = queue_stack_map_alloc_check,
        .map_alloc = queue_stack_map_alloc,
        .map_free = queue_stack_map_free,
        .map_lookup_elem = queue_stack_map_lookup_elem,
        .map_update_elem = queue_stack_map_update_elem,
        .map_delete_elem = queue_stack_map_delete_elem,
        .map_push_elem = queue_stack_map_push_elem,
        .map_pop_elem = queue_map_pop_elem,
        .map_peek_elem = queue_map_peek_elem,
        .map_get_next_key = queue_stack_map_get_next_key,
    };
    

如果我们能通过堆溢出将ops指向一块伪造的虚表，那么就可能通过dereference这些函数指针中的任何一个实现控制流劫持，获得rip的控制权。为了找到使用这些函数指针的方法，我们既可以去仔细阅读相关的代码手动编写漏洞利用，也可以使用[2]中提到的under-context fuzzing+symbolic
execution的半自动技术，通过fuzzing找到dereference这些函数指针的系统调用，并辅助生成后续的利用。

本次发布的利用代码[4]使用close()一个bpf map的方法来获得控制流劫持的机会：

    
    
    /* called from workqueue */
    static void bpf_map_free_deferred(struct work_struct *work)
    {
        struct bpf_map *map = container_of(work, struct bpf_map, work);
    
        bpf_map_release_memlock(map);
        security_bpf_map_free(map);
        /* implementation dependent freeing */
        map->ops->map_free(map);
    }
    /* decrement map refcnt and schedule it for freeing via workqueue
     * (unrelying map implementation ops->map_free() might sleep)
     */
    static void __bpf_map_put(struct bpf_map *map, bool do_idr_lock)
    {
        if (atomic_dec_and_test(&map->refcnt)) {
            /* bpf_map_free_id() must be called first */
            bpf_map_free_id(map, do_idr_lock);
            btf_put(map->btf);
            INIT_WORK(&map->work, bpf_map_free_deferred);
            schedule_work(&map->work);
        }
    }
    

在`close()`受害者BPF
map时，会将`bpf_map_free_deferred()`添加到队列并随后执行，通过将map->ops指向用户态可控位置，并且将ops.map_free设为任意值，我们就可以在执行`map->ops->map_free(map);`语句时将rip设置为任意值。

在获得控制流劫持的机会后，对于SMEP, SMAP,
KASLR等内核漏洞缓解机制的绕过仍然是漏洞利用的巨大挑战。我们仅公布绕过SMEP的利用代码，并对其他缓解机制的绕过作一些讨论。

在公布的利用代码中我们针对仅有SMEP的防御的情况，选择了一种最基础的利用流程[3]：

  1. 堆风水
  2. 触发堆溢出
  3. 控制流劫持
  4. stack pivoting到用户态
  5. commit_cred(prepare_kernel_cred(0))提权
  6. swapgs
  7. 修复页表(针对KPTI(Kernel Page Table Isolation)在kernel页表中移除了用户态可执行代码)(optional)
  8. iretq
  9. get_shell().

利用效果如下图所示：

![](https://p5.ssl.qhimg.com/t01b513c5336b4c46d5.png)

###  SMAP绕过讨论

SMAP防止ring 0代码访问用户态数据，Linux下的传统的绕过SMAP提权的方法包括以下几种：

  1. 利用JOP改写CR4寄存器关闭SMAP防御
  2. 利用call_usermodehelper 以root身份执行binary
  3. 通过内存任意读写直接改写当前进程cred。

关于利这一个单个漏洞SMAP, KPTI, KASLR等其他防御机制的绕过，将在后续文章中进行详解。

###  KASLR绕过讨论

Linux下的传统的绕过KASLR提权的方法包括以下几种：

  1. 近年来，有许多通过硬件侧信道绕过KASLR的工作，如prefetch, meltdown等
  2. 利用漏洞构造信息泄露
  3. 配合一个信息泄露漏洞

## 时间线

2018-10-19 漏洞引入

2018-11-21 漏洞发现

2018-11-22 漏洞利用

2018-11-22 漏洞修补

## 总结

本文对一个Linux内核4.20中新引入的BPF模块整数溢出-堆溢出漏洞进行了分析，并介绍了其利用方法，本漏洞利用代码发布在[4]。不得不说新功能/新feature的添加是漏洞的一大来源。如果没有大量针对新功能code
review和fuzzing来提升新功能的安全性，那么新的代码的安全性无法保证。安全不是一朝一夕，而是需要整个社区的长期投入。

对于这个漏洞的分析和利用过程如有其它问题，欢迎联系我。

e-mail: [wuwei@iie.ac.cn](mailto:wuwei@iie.ac.cn) QQ: 544536427

## 参考文献

  1. <https://www.kernel.org/doc/Documentation/networking/filter.txt>
  2. [FUZE: Towards Facilitating Exploit Generation for Kernel Use-After-Free Vulnerabilities.](https://www.usenix.org/system/files/conference/usenixsecurity18/sec18-wu_0.pdf)
  3. [https://www.trustwave.com/Resources/SpiderLabs-Blog/Linux-Kernel-ROP—Ropping-your-way-to—(Part-1)/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Linux-Kernel-ROP---Ropping-your-way-to---\(Part-1\)/)
  4. [漏洞利用代码与对应内核 (exploit code and kernel image)](https://github.com/ww9210/kernel4.20_bpf_LPE)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ww9210** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/166819](/post/id/166819)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [exploit](/tag/exploit)
  * [系统安全](/tag/系统安全)
  * [Linux Kernel](/tag/Linux Kernel)

 **+1** __26赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) ww9210

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

