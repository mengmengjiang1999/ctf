**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/LOf_W9QRDds_yHO1aVSg9Q>**

## **1.1** **简介**

XNU的内核内存分配器层次比较多， 因为它是一个混合的内核，bsd、mach层都有自己的内存分配器接口， 但最底层的都是调用zone
allocotr分配器。它的内存分配器设计非常简单，大概是我读过的众多主流os内核中无论数据结构还是分配算法都是最简单的一个。我时常在想XNU内核给MacOS提供了流畅的操作性，但是只从zone的内存分配器来看并不能支撑这个结论，或许慢慢随着笔者对XNU内核的深入理解，答案也会慢慢水落石出。不过本次我们将探讨下zone内存分配器的安全特性以及设计不足，值得肯定的是zone内存分配器在调试和安全特性上的支持已经远远甩出了FREEBSD内核，于linux的slab内存分配器也有过之而无不及，
各有春秋。

## **1.2** **zone分配器的基本结构**

Zone分配器的最基本管理结构为struct zone_page_metadata， 它相当于linux slab的slab管理结构体。

    
    
    struct zone_page_metadata {
            queue_chain_t           pages;
            union {
                    uint32_t                freelist_offset;
                    uint32_t                real_metadata_offset;
            };
    
            uint16_t                        free_count;
            unsigned                        zindex     : ZINDEX_BITS;   
            unsigned                        page_count : PAGECOUNT_BITS;
    };

结构成员中最重要的是freelist_offset, 它保存的是下一个空闲的item地址。 一个item在内存中的结构图为：

![](https://images.seebug.org/content/images/2021/01/85c13d02-a9d4-4f1c-b4af-faf1070a0271.png-w331s)

## **1.3 堆溢出检测**

业界常用的检测堆溢出的算法为在一个item前后填充若干redzone值，申请或释放内存时对redzone值进行检测，以发现是否有溢出行为的发生。XNU内核只有在打开KASAN_ZALLOC内核选项时才会填充redzone。

    
    
    osfmk/kern/zalloc.c：
    
    static inline vm_offset_t
    try_alloc_from_zone(zone_t zone,
                            vm_tag_t tag __unused,
                        boolean_t* check_poison)
    {
    #if KASAN_ZALLOC
            kasan_poison_range(element, zone->elem_size, ASAN_VALID);
    #endif
    }
    
    kasan_poison_range->kasan_poison
    kasan_poison(vm_offset_t base, vm_size_t size, vm_size_t leftrz, vm_size_t rightrz, uint8_t flags)
    {
            uint8_t *shadow = SHADOW_FOR_ADDRESS(base);
            uint8_t partial = size & 0x07;
            vm_size_t total = leftrz + size + rightrz;
            vm_size_t i = 0; 
    
            if (!kasan_enabled || !kasan_poison_active(flags)) {
                    return;
            }
    
            leftrz /= 8;
            size /= 8;
            total /= 8;
    
            uint8_t l_flags = flags;
            uint8_t r_flags = flags;
    
            if (flags == ASAN_STACK_RZ) {
                    l_flags = ASAN_STACK_LEFT_RZ;
                    r_flags = ASAN_STACK_RIGHT_RZ;
            } else if (flags == ASAN_HEAP_RZ) {
                    l_flags = ASAN_HEAP_LEFT_RZ;
                    r_flags = ASAN_HEAP_RIGHT_RZ;
            }
            for (; i < leftrz; i++) {
                    shadow[i] = l_flags;
            }
    
            for (; i < leftrz + size; i++) {
                    shadow[i] = ASAN_VALID; /* XXX: should not be necessary */
            }
    
            if (partial && (i < total)) {
                    shadow[i] = partial;
                    i++;
            }
    
            for (; i < total; i++) {
                    shadow[i] = r_flags;
            }
    }

Zone依据内存分配器的不同阶段，调用kasan_poison时构造的item前后redzone填充值也不相同。

    
    
    san/kasan.h
    
    #define ASAN_VALID          0x00
    #define ASAN_HEAP_RZ        0xe9
    #define ASAN_HEAP_LEFT_RZ   0xfa
    #define ASAN_HEAP_RIGHT_RZ  0xfb
    #define ASAN_HEAP_FREED     0xfd

Redzone的填充值与其他OS的实现一样都使用了默认值， exploit程序很容易对其绕过，在笔者给linux
slab开发的内核加固补丁AKSP中，堆redzone使用了随机值，进一步提升了安全性。

## **1.4 DOUBLE FREE检测**

Zone内存分配器可以做简单的double free检测。

    
    
    osfmk/kern/zalloc.c：
    
    static inline void
    free_to_zone(zone_t      zone,
                 vm_offset_t element,
                 boolean_t   poison)
    {
    page_meta = get_zone_page_metadata((struct zone_free_element *)element, FALSE); [1]
        old_head = (vm_offset_t)page_metadata_get_freelist(page_meta);              [2]
        if (__improbable(old_head == element))                 [3]
             panic("zfree: double free of %p to zone %s\n",
                  (void *) element, zone->zone_name);
    }

[1] 处通过参数element获取struct zone_page_metadata管理体地址，然后获取其保存的下一个空闲item地址old_head,
在[3]进行比对， 如果相等说明有重复释放的行为。

这种算法只能检测简单的double free操作，也就是连续释放两次相同的item地址。

Free(addr1);

Free(addr1);

对于下面这种情况就检测不到了。

Free(addr1);

Free(addr2);

Free(addr1);

在笔者给linux slab开发的内核加固补丁AKSP中，可以检测上述或者更复杂的多重释放问题。

## **1.5 UAF检测**

业界常用的UFA检测算法是给item填充固定的poison值，在申请内存时检测posion是否改变以此来发现UAF的行为。

    
    
    osfmk/kern/zalloc.c
    
    static void *
    zalloc_internal(
            zone_t  zone,
            boolean_t canblock,
            boolean_t nopagewait,
            vm_size_t
    #if !VM_MAX_TAG_ZONES
        __unused
    #endif
        reqsize,
            vm_tag_t  tag)
    {
            zalloc_poison_element(check_poison, zone, addr);
    }
    
    void
    zalloc_poison_element(boolean_t check_poison, zone_t zone, vm_offset_t addr)
    {
            vm_offset_t     inner_size = zone->elem_size;
    
            if (__improbable(check_poison && addr)) {
                    vm_offset_t *element_cursor  = ((vm_offset_t *) addr) + 1;       [1]
                    vm_offset_t *backup  = get_backup_ptr(inner_size, (vm_offset_t *) addr);[2]
    
                    for ( ; element_cursor < backup ; element_cursor++)[3]
                            if (__improbable(*element_cursor != ZP_POISON))
                                    zone_element_was_modified_panic(zone,
                                                                    addr,
                                                                    *element_cursor,
                                                                    ZP_POISON,
                                                                    ((vm_offset_t)element_cursor) - addr);
            }
    }

[1] 处首先取得poison的首地址，注意item的第一个地址为加密后的next
pointer值，它是与zp_nopoison_cookie异或计算的结果，所以要跳过第一个地址，
[2]处取得posion的最后一个地址，在前面的item内存结构视图中可以看到item的最后一个地址保存的是next_pointer的值，它是与zp_poisoned_cookie或者zp_nopoison_cookie异或计算的结果。

zp_poisoned_cookie与zp_nopoison_cookie是在zone子系统初始化时动态随机生成的，所有的zone共用同一个值。[3]处与默认填充的poison值进行比对,
如果比对失败，说明这个item在分配之前已经被改写过了。

前面分析过item的第一个地址保存的是next pointer的一个混淆值， 在item的最后还保存了一个next
pointer的混淆值副本。所以除了填充poison的方法， zone内存分配器还可以使用next pointer和其副本的对比，来发现UAF的行为。

    
    
    static inline vm_offset_t
    try_alloc_from_zone(zone_t zone,
                            vm_tag_t tag __unused,
                        boolean_t* check_poison)
    {
            if (__improbable(next_element != (next_element_backup ^ zp_nopoison_cookie))) {
                    if (__improbable(next_element != (next_element_backup ^ zp_poisoned_cookie)))
                            /* Neither cookie is valid, corruption has occurred */
                            backup_ptr_mismatch_panic(zone, element, next_element_primary, next_element_backup);
            }
    }

由于next pointer的副本根据是否需要填充poison使用不同的xor值，所以分别进行了两次比对。

在进行完UAF检查后，zalloc_poison_element还会堆next
pointer进行擦除，以后防止地址泄露，并且从泄露的地址推测zp_nopoison_cookie随机值。

    
    
    void
    zalloc_poison_element(boolean_t check_poison, zone_t zone, vm_offset_t addr)
    {
            if (addr) {
                    vm_offset_t *primary  = (vm_offset_t *) addr;
                    vm_offset_t *backup   = get_backup_ptr(inner_size, primary);
    
                    *primary = ZP_POISON;
                    *backup  = ZP_POISON;
            }
    }

## **1.6 item地址随机化**

内核堆的攻击技术链中，item的地址初始化顺序十分重要， exploit以此来精确控制要覆盖的item地址， linux
slab使用了洗牌算法将slab里item的初始化顺序完全打乱。但是XNU内核使用的item随机化只有两种情况，
正向顺序或逆向顺序，这只能在一定程度上缓解地址随机化问题，相比linux的洗牌算法会变弱了很多。

    
    
    random_free_to_zone(
                            zone_t          zone,
                            vm_offset_t     newmem,
                            vm_offset_t     first_element_offset,
                            int             element_count,
                            unsigned int    *entropy_buffer)
    {
            assert(element_count && element_count <= ZONE_CHUNK_MAXELEMENTS);
    
            elem_size = zone->elem_size;
            last_element_offset = first_element_offset + ((element_count * elem_size) - elem_size);
            for (index = 0; index < element_count; index++) {
                    assert(first_element_offset <= last_element_offset);
                    if (
    #if DEBUG || DEVELOPMENT
                    leak_scan_debug_flag || __improbable(zone->tags) ||
    #endif /* DEBUG || DEVELOPMENT */
                    random_bool_gen_bits(&zone_bool_gen, entropy_buffer, MAX_ENTROPY_PER_ZCRAM, 1)) {[1]
                            element_addr = newmem + first_element_offset;
                            first_element_offset += elem_size;
                    } else {[2]
                            element_addr = newmem + last_element_offset;
                            last_element_offset -= elem_size;
                    }
    
                    if (element_addr != (vm_offset_t)zone) {
                            zone->count++;  /* compensate for free_to_zone */
                            free_to_zone(zone, element_addr, FALSE);
                    }
    
                    zone->cur_size += elem_size;
            }
    
    }

random_bool_gen_bits产生一些随机的0或1，从而选择是正向顺序分配还是逆向顺序分配item地址。

## **1.7 内存拷贝检查**

Zone内存分配器提供了一个启动参数-no-copyio-zalloc-check,
当发生从用户空间向内核空间拷贝数据时，会检测内核空间是否属于zone的空间，如果属于那么拷贝的字节数就不能大于zone的item
size，这是一个非常棒的安全检测功能。有点类似linux slab的hardened user copy算法，
只不过它防止的是从内核向用户空间拷贝敏感的数据，限制了拷贝的范围。

## **1.8 双向安全链表**

尽管针对内核堆溢出的攻击中， 很少见到改写双向链表节点的攻击手段。但是为了防患于未然，或者说养成良好的安全编程习惯，
NT和linux内核都使用了安全双向链表检查，而XNU未提供此能力。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1455/>

