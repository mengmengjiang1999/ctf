**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/Ua4CV3Vn8piw6z6BrpJyCQ>**

Ios13增加了判断对象是否属于zone的安全检查，这将导致以前通过伪造内核对象的漏洞利用手段变得困难了很多，比如ipc_port，伪造的对象通常来自于用户空间，那么在引用这个对象时，xnu引入了zone_require、zone_id_require、zone_owns三个函数来做对象合法性检查。

    
    
    osfmk/kern/zalloc.c：
    void
    zone_require(zone_t zone, void *addr)
    {
            if (__probable(from_general_submap(addr, zone_elem_size(zone)) &&[1]
                (zone_has_index(zone, zone_native_meta_from_addr(addr)->zm_index)))) {  [2]
                    return;
            }
    
    #if CONFIG_GZALLOC
            if (__probable(gzalloc_enabled())) {
                    return;
            }
    #endif
            zone_require_panic(zone, addr);[3]
    }

[1]处的from_general_submap判断对象的地址是否在整个大的有效范围内。

    
    
    #define from_general_submap(addr, size) \
            zone_range_contains(&zone_info.zi_general_range, (vm_offset_t)(addr), size)
    
    #define zone_range_load(r, rmin, rmax) \
            ({ rmin = (r)->min_address; rmax = (r)->max_address; })
    #endif
    
    __header_always_inline bool
    zone_range_contains(const struct zone_map_range *r, vm_offset_t addr, vm_offset_t size)
    {
            vm_offset_t rmin, rmax;
    
            zone_range_load(r, rmin, rmax);
            return (addr >= rmin) & (addr + size >= rmin) & (addr + size <= rmax);
    }

[2]
处的zone_has_index才是判断对象是否属于某个特定的zone。通过zone_native_meta_from_addr函数将对象地址转为对应的meta数据结构，meta的zm_index指示的是meta对应的zone在zone_array数组里的索引，这样通过索引加上zone_array数组地址就能判断是否指向了正确的zone地址。

    
    
    static inline bool
    
    zone_has_index(zone_t z, zone_id_t zid)
    {
            return zone_array + zid == z;
    }
    
    __abortlike
    static void
    zone_require_panic(zone_t zone, void *addr)
    {
            uint32_t zindex;
            zone_t other;
    
            if (!from_zone_map(addr, zone_elem_size(zone))) {
                    panic("zone_require failed: address not in a zone (addr: %p)", addr);
            }
    
            zindex = zone_native_meta_from_addr(addr)->zm_index;
            other = &zone_array[zindex];
            if (zindex >= os_atomic_load(&num_zones, relaxed) || !other->z_self) {
                    panic("zone_require failed: invalid zone index %d "
                        "(addr: %p, expected: %s%s)", zindex,
                        addr, zone_heap_name(zone), zone->z_name);
            } else {
                    panic("zone_require failed: address in unexpected zone id %d (%s%s) "
                        "(addr: %p, expected: %s%s)",
                        zindex, zone_heap_name(other), other->z_name,
                        addr, zone_heap_name(zone), zone->z_name);
            }
    }

当比对失败时，[3]处调用了zone_require_panic来试图分析是哪种情况造成的并panic系统。

zone_require是zalloc内存分配器提供的kpi接口，
当其他内核子系统需要判断某个object是否合法时要主动调用，因为如果在内存分配器的alloc或free路径里在去判断对象合法性时为时已晚，漏洞攻击已经完成了。

Ios13也是类似的逻辑：

![](https://images.seebug.org/content/images/2021/02/a608d061-03c2-49c1-971d-d57304bb28ea.jpg-w331s)
![](https://images.seebug.org/content/images/2021/02/f8502078-f301-4842-9edd-877a3aad0058.jpg-w331s)
同时还可以发现， 最新的xnu内存分配器对对象、meta、zone的合法性做了极其严格的检查，这些优秀的漏洞缓解方法需要移植到linux中去。

    
    
    static struct zone_page_metadata *
    
    zone_allocated_element_resolve(zone_t zone, vm_offset_t addr,
        vm_offset_t *pagep, zone_addr_kind_t *kindp)
    {
            struct zone_page_metadata *meta;
            zone_addr_kind_t kind;
            vm_offset_t page;
            vm_offset_t esize = zone_elem_size(zone); 
    
            kind = zone_addr_kind(addr, esize);
            page = trunc_page(addr);
            meta = zone_meta_from_addr(addr, kind); 
    
            if (kind == ZONE_ADDR_NATIVE) {
                    if (meta->zm_secondary_page) {
                            if (meta->zm_percpu) {
                                    zone_invalid_element_addr_panic(zone, addr);
                            }
                            page -= ptoa(meta->zm_page_count);
                            meta -= meta->zm_page_count;
                    }
    
            } else if (!zone->allows_foreign) {
                    zone_page_metadata_foreign_confusion_panic(zone, addr);
    #if __LP64__
            } else if (!from_foreign_range(addr, esize)) {
                    zone_invalid_foreign_addr_panic(zone, addr);
    #else
            } else if (!pmap_kernel_va(addr)) {
                    zone_invalid_element_addr_panic(zone, addr);
    #endif
            }
    
            if (!zone_allocated_element_offset_is_valid(zone, addr, page, kind)) {
                    zone_invalid_element_addr_panic(zone, addr);
            }
    
            if (!zone_has_index(zone, meta->zm_index)) {
                    zone_page_metadata_index_confusion_panic(zone, addr, meta);
            }
            if (kindp) {
                    *kindp = kind;
            }
    
            if (pagep) {
                    *pagep = page;
            }
    
            return meta;
    }
    
    zone_metadata_corruption(zone_t zone, struct zone_page_metadata *meta,
        const char *kind)
    {
            panic("zone metadata corruption: %s (meta %p, zone %s%s)",
                kind, meta, zone_heap_name(zone), zone->z_name);
    }
    
    zone_invalid_element_addr_panic(zone_t zone, vm_offset_t addr)
    {
            panic("zone element pointer validation failed (addr: %p, zone %s%s)",
                (void *)addr, zone_heap_name(zone), zone->z_name);
    }
    
    zone_page_metadata_index_confusion_panic(zone_t zone, vm_offset_t addr,
        struct zone_page_metadata *meta)
    {
            panic("%p not in the expected zone %s%s (%d != %d)",
                (void *)addr, zone_heap_name(zone), zone->z_name,
                meta->zm_index, zone_index(zone));
    }
    
    zone_page_metadata_native_queue_corruption(zone_t zone, zone_pva_t *queue)
    {
            panic("foreign metadata index %d enqueued in native head %p from zone %s%s",
                queue->packed_address, queue, zone_heap_name(zone),
                zone->z_name);
    }
    
    zone_page_metadata_list_corruption(zone_t zone, struct zone_page_metadata *meta)
    {
            panic("metadata list corruption through element %p detected in zone %s%s",
                meta, zone_heap_name(zone), zone->z_name);
    }
    
    zone_page_metadata_foreign_queue_corruption(zone_t zone, zone_pva_t *queue)
    {
            panic("native metadata index %d enqueued in foreign head %p from zone %s%s",
                queue->packed_address, queue, zone_heap_name(zone), zone->z_name);
    }
    
    zone_page_metadata_foreign_confusion_panic(zone_t zone, vm_offset_t addr)
    {
            panic("manipulating foreign address %p in a native-only zone %s%s",
                (void *)addr, zone_heap_name(zone), zone->z_name);
    }
    
    zone_invalid_foreign_addr_panic(zone_t zone, vm_offset_t addr)
    {
            panic("addr %p being freed to foreign zone %s%s not from foreign range",
                (void *)addr, zone_heap_name(zone), zone->z_name);
    }
    
    zone_page_meta_accounting_panic(zone_t zone, struct zone_page_metadata *meta,
        const char *kind)
    {
            panic("accounting mismatch (%s) for zone %s%s, meta %p", kind,
                zone_heap_name(zone), zone->z_name, meta);
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1486/>

