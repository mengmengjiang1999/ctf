**作者：wzt  
原文链接：<https://mp.weixin.qq.com/s/3jnbdStYFuTldf0uEz_bpA>**

## **1.1** **进程栈、代码段地址随机化**

这里指的是进程的用户态栈，记住一个进程实际拥有两个栈，
一个用于跑用户态的代码，一个用于请求系统调用时在内核中使用的栈空间。在前面分析BSD进程随机化时，我们注意到bsd并没有给进程的用户态栈加入地址随机化，
XNU虽然继承了BSD进程模型，但作为一个商业操作系统没有栈的随机化功能显然是说不过去的， 自然给其进程加入了随机化功能。

    
    
    bsd/kern/mach_loader.c
    
    load_return_t
    load_machfile(
            struct image_params     *imgp,
            struct mach_header      *header,
            thread_t                thread,
            vm_map_t                *mapp,
            load_result_t           *result
    )
    {
            if (!(imgp->ip_flags & IMGPF_DISABLE_ASLR)) {
                    vm_map_get_max_aslr_slide_section(map, &aslr_section_offset, &aslr_section_size); [1]
                    aslr_section_offset = (random() % aslr_section_offset) * aslr_section_size;[2]
                    aslr_page_offset = random();[3]
                    aslr_page_offset %= vm_map_get_max_aslr_slide_pages(map);
                    aslr_page_offset <<= vm_map_page_shift(map);
    
                    dyld_aslr_page_offset = random();[4]
                    dyld_aslr_page_offset %= vm_map_get_max_loader_aslr_slide_pages(map);
                    dyld_aslr_page_offset <<= vm_map_page_shift(map);
    
                    aslr_page_offset += aslr_section_offset;[5]
            }
    }

除了mmap，进程的栈、代码段以及共享库的地址随机化都是在内核从磁盘加载二进制文件时完成的。[1]处vm_map_get_max_aslr_slide_section函数选取了随机化的范围，

    
    
    void
    
    vm_map_get_max_aslr_slide_section(
                    vm_map_t                map __unused,
                    int64_t                 *max_sections,
                    int64_t                 *section_size)
    {
    #if defined(__arm64__)
            *max_sections = 3;
            *section_size = ARM_TT_TWIG_SIZE;
    #else
            *max_sections = 1;
            *section_size = 0;
    #endif
    }

aslr_section_offset表示的随机几个页面大小，aslr_section_size表示每个页面的大小，对于不同的CPU体系架构拥有不同的值，在arm64下
aslr_section_offset设定为3，页面大小设置为0x0000000000200000ULL，其他架构下aslr_section_offset设为1，
页面大小设为0。[2]处使用random函数生成了一个临时随机范围aslr_section_offset。[3]处的aslr_page_offset表示栈和代码段使用的随机范围，没错xnu的栈和text代码使用的是同一个随机范围，
而linux使用的都是不同的。Xnu这样做提升了一点性能，但安全性也会降低一些。vm_map_get_max_aslr_slide_pages函数选取了要随机多少个页面大小，在arm64下为1<<12，在其他架构的64位下为1<<16，32位为1<<8。

    
    
    uint64_t
    
    vm_map_get_max_aslr_slide_pages(vm_map_t map)
    {
    #if defined(__arm64__)
            /* Limit arm64 slide to 16MB to conserve contiguous VA space in the more
             * limited embedded address space; this is also meant to minimize pmap
             * memory usage on 16KB page systems.
             */
            return (1 << (24 - VM_MAP_PAGE_SHIFT(map)));
    #else
            return (1 << (vm_map_is_64bit(map) ? 16 : 8));
    #endif
    }

最后aslr_page_offset在左移12位，那么在arm64下其随机化的范围就为0-16MB，其实随机化的范围并不大，而且都是以页面对齐的，所以只需暴力才解4096次就能猜到offset。即使加上[5]处的临时offset，也提高不了多少安全等级。

[4]
处的vm_map_get_max_loader_aslr_slide_pages计算的是共享库的地址随机化范围，与上述类似，最终随机范围为0-4MB。

Win10进程栈在64位下可以做到上TB的随机化范围，
笔者也给linux扩展了栈的随机化范围，通过打入AKSP补丁，栈的随机化也可以做到上TB的范围。如此来看，XNU进程的栈地址随机化未免有点小家子气了。

对栈基地址的设置是在load_unixthread里设置的：

    
    
    static
    
    load_return_t
    load_unixthread(
            struct thread_command   *tcp,
            thread_t                thread,
            int64_t                         slide,
            load_result_t           *result
    )
    {
            ret = load_threadstack(thread,
                                    (uint32_t *)(((vm_offset_t)tcp) +
                                            sizeof(struct thread_command)),
                                    tcp->cmdsize - sizeof(struct thread_command),
                                    &addr, &customstack, result);
            result->user_stack = addr;
            result->user_stack -= slide;
    }

load_threadstack选取了栈基地址，然后减去slide。Slide为上述的aslr_page_offset，但是它的使用还有个前提条件：

    
    
    static
    
    load_return_t
    parse_machfile(
            struct vnode            *vp,
            vm_map_t                map,
            thread_t                thread,
            struct mach_header      *header,
            off_t                   file_offset,
            off_t                   macho_size,
            int                     depth,
            int64_t                 aslr_offset,
            int64_t                 dyld_aslr_offset,
            load_result_t           *result,
            load_result_t           *binresult,
            struct image_params     *imgp
    )
    {
            int64_t                 slide = 0;
    
            if ((header->flags & MH_PIE) || is_dyld) {
                    slide = aslr_offset;
            }
    }

Slide初始化为0，只有当二进制为PIE编译或者为动态连接器才会被设置为aslr_offset，这样对于普通的二进制程序栈并没有地址随机化能力！

## **1.2** **mmap地址随机化**

XNU提供了posix标准的mmap函数，对于匿名映射的内存地址随机化是在mach层的vm_map_enter函数来设置的。

    
    
    osfmk/vm/vm_map.c
    
    kern_return_t
    vm_map_enter(
            vm_map_t                map,
            vm_map_offset_t         *address,       /* IN/OUT */
            vm_map_size_t           size,
            vm_map_offset_t         mask,
            int                     flags,
            vm_map_kernel_flags_t   vmk_flags,
            vm_tag_t                alias,
            vm_object_t             object,
            vm_object_offset_t      offset,
            boolean_t               needs_copy,
            vm_prot_t               cur_protection,
            vm_prot_t               max_protection,
            vm_inherit_t            inheritance)
    {
            boolean_t               random_address = ((flags & VM_FLAGS_RANDOM_ADDR) != 0);[1]
    
            if (anywhere) {
                    vm_map_lock(map);
                    map_locked = TRUE; 
    
                    if (entry_for_jit) {[2]
    #if CONFIG_EMBEDDED
                            if (map->jit_entry_exists) {
                                    result = KERN_INVALID_ARGUMENT;
                                    goto BailOut;
                            }
    
                            random_address = TRUE;
    #endif
                    }
    
                    if (random_address) {
                            result = vm_map_random_address_for_size(map, address, size); [3]
                            if (result != KERN_SUCCESS) {
                                    goto BailOut;
                            }
                            start = *address;
                    }
    }

对于主动提供了VM_FLAGS_RANDOM_ADDR标志或者在CONFIG_EMBEDDED下开启了jit
code条件下都会使用[3]处的vm_map_random_address_for_size函数选取一块包含了随机化范围的起始地址。

    
    
    #define MAX_TRIES_TO_GET_RANDOM_ADDRESS 1000
    
    kern_return_t
    vm_map_random_address_for_size(
            vm_map_t        map,
            vm_map_offset_t *address,
            vm_map_size_t   size)
    {
    addr_space_size = vm_map_max(map) - vm_map_min(map);[1]
    
            while (tries < MAX_TRIES_TO_GET_RANDOM_ADDRESS) {
                    random_addr = ((vm_map_offset_t)random()) << PAGE_SHIFT; [2]
                    random_addr = vm_map_trunc_page(
                            vm_map_min(map) +(random_addr % addr_space_size),
                            VM_MAP_PAGE_MASK(map));
    
                    if (vm_map_lookup_entry(map, random_addr, &prev_entry) == FALSE) {
                            if (prev_entry == vm_map_to_entry(map)) {
                                    next_entry = vm_map_first_entry(map);
                            } else {
                                    next_entry = prev_entry->vme_next;
                            }
                            if (next_entry == vm_map_to_entry(map)) {
                                    hole_end = vm_map_max(map);
                            } else {
                                    hole_end = next_entry->vme_start;
                            }
    
                            vm_hole_size = hole_end - random_addr;
                            if (vm_hole_size >= size) {
                                    *address = random_addr;
                                    break;
                           }
                    }
                    tries++;
            } 
    
            if (tries == MAX_TRIES_TO_GET_RANDOM_ADDRESS) {
                    kr = KERN_NO_SPACE;
            }
    
            return kr;
    }

这个函数比较奇葩， 尝试循环1000次找到带有随机化范围的vm_map_entry，[1]处首先计算当前进程还剩的虚拟内存空间大小，
[2]处使用random函数产生了一个页面对齐的随机数，然后与addr_space_size取模，在64位下，addr_space_size的取值可能非常大，
所以xnu尝试最多1000次循环来找到一个合适的地址空间。使用这样的算法，offset的可控性很差，
还有可能因为随机数的问题导致整个mmap动作失败，我觉得后续xnu的内核工程师应该会改进这个算法。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1475/>

