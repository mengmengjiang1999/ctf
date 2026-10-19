**作者： knaithe@天玄安全实验室  
原文链接：<https://mp.weixin.qq.com/s/gu6O-ZSIiVpNJP1I9O94wQ>**

> **漏洞描述**
> ：漏洞位于/net/packet/af_packet.c文件，rx_owner_map引用了pg_vec，切换到TPACKET_V3协议版本中，在packet_set_ring()函数的末尾，对pg_vec释放了一次，并未对rx_owner_map指针置为NULL，导致rx_owner_map成为悬空指针，直到从TPACKET_V3协议版本切换到TPACKET_V2协议版本后，在次到达packet_set_ring()函数的末尾，bitmap_free()函数对rx_owner_map指针进行释放，触发double
> free漏洞。
>
> **影响版本** ：Linux Kernel v5.8.0 - v5.15.0
>
> **测试版本** ：Linux #5.13.0
>
> **保护机制** ：SMEP/SMAP/KASLR/KPTI

## 1.漏洞分析

### 1.1.AF_PACKET套接字协议族

**协议简介：**
AF_PACKET是原始套接字协议，是一种特殊的套接字协议，可以是数据链路层原始套接字，也可以是网络层原始套接字。如果是数据链路层原始套接字，可以直接发送和接收位于数据链路层的以太帧，比如Ethernet
II协议，如果是网络层原始套接字，就只能发送和接收位于网络层的数据报文，比如IP协议。

**快速使用：** 我们这里可以通过如下函数快速的创建一个 AF_PACKET协议的原始套接字：

    
    
    socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));

通过setsockopt就可以设置该套接字相关操作，比如设置当前AF_PACKET套接字协议版本为TPACKET_V3：

    
    
    int version = TPACKET_V3;
    setsockopt(s, SOL_PACKET, PACKET_VERSION, &version, sizeof(version));

创建ring buffer：

    
    
    struct tpacket_req3 req3;
    memset(&req3, 0, sizeof(req3));
    req3.tp_block_size = block_size;
    req3.tp_block_nr = block_nr;
    req3.tp_frame_size = frame_size;
    req3.tp_frame_nr = frame_nr;
    req3.tp_retire_blk_tov = retire_blk_tov;
    req3.tp_sizeof_priv = 0;
    req3.tp_feature_req_word = 0;
    setsockopt(recv_fd, SOL_PACKET, PACKET_RX_RING, &req3, sizeof(req3));

### 1.2.漏洞触发

**触发过程详解：**

  1. 首先调用socket函数创建AF_PACKET套接字。
  2. 然后调用setsockopt设置协议版本为TPACKET_V3。
  3. 接着调用setsockopt设置RX_RING，正常给tpacket_req3配置参数，在执行packet_set_ring()函数过程中，pg_vec指向alloc_pg_vec()函数分配的内存，并且调用init_prb_bdqc函数，导致pg_vec被sock->rx_ring->prb_bdqc->pkbdq引用，然后调用swap函数将pg_vec和sock->rx_ring->pg_vec交换，函数最后pg_vec指向NULL，没有调用free。
  4. 再次调用setsockopt设置RX_RING，将tpacket_req3参数的tp_block_nr和tp_frame_nr字段设置为0，然后调用swap函数将pg_vec和sock->rx_ring->pg_vec交换，此时sock->rx_ring->pg_vec为NULL，pg_vec指向上一步骤分配的内存，函数结尾调用free_pg_vec()释放pg_vec，此时packet_ring_buffer->prb_bdqc->pkbdq成为悬空指针。
  5. 到此才可以再次调用setsockopt设置协议版本为TPACKET_V2，sock->rx_ring->pg_vec为NULL，所以该套接字切换协议TPACKET_V2成功。
  6. 最后调用setsockopt设置RX_RING，此时tpacket_req参数的tp_block_nr字段必须为0，再次进入packet_set_ring()函数，由于已经是TPACKET_V2协议，所以调用了swap函数交换了rx_owner_map和sock->rx_ring->rx_owner_map，由于packet_ring_buffer结构体的rx_owner_map成员和tpacket_kbdq_core成员属于联合体，所以sock->rx_ring->rx_owner_map和sock->rx_ring->prb_bdqc->pkbdq的值相同，在第4步骤packet_ring_buffer->prb_bdqc->pkbdq成为悬空指针，所以在函数结尾调用bitmap_free(rx_owner_map)，等同于free掉sock->rx_ring->prb_bdqc->pkbdq这个悬空指针，造成double free。

    
    
    /net/packet/af_packet.c
    
    static int packet_set_ring(struct sock *sk, union tpacket_req_u *req_u,
      int closing, int tx_ring)
    {
     struct pgv *pg_vec = NULL;
     struct packet_sock *po = pkt_sk(sk);
     unsigned long *rx_owner_map = NULL;
     int was_running, order = 0;
     struct packet_ring_buffer *rb;
     struct sk_buff_head *rb_queue;
     __be16 num;
     int err;
     /* Added to avoid minimal code churn */
     struct tpacket_req *req = &req_u->req;
    
     rb = tx_ring ? &po->tx_ring : &po->rx_ring;
     rb_queue = tx_ring ? &sk->sk_write_queue : &sk->sk_receive_queue;
    
     err = -EBUSY;
     if (!closing) {
      if (atomic_read(&po->mapped))
       goto out;
      if (packet_read_pending(rb))
       goto out;
     }
    
     if (req->tp_block_nr) {   // 上述第4、6步，tp_block_nr字段必须为0，只允许步骤3进入
      unsigned int min_frame_size;
    
      /* Sanity tests and some calculations */
      err = -EBUSY;
      if (unlikely(rb->pg_vec))
       goto out;
    
      switch (po->tp_version) {
      case TPACKET_V1:
       po->tp_hdrlen = TPACKET_HDRLEN;
       break;
      case TPACKET_V2:
       po->tp_hdrlen = TPACKET2_HDRLEN; 
       break;
      case TPACKET_V3:
       po->tp_hdrlen = TPACKET3_HDRLEN; //  TPACKET3_HDRLEN = 0x44
       break;
      }
    
      err = -EINVAL;
      if (unlikely((int)req->tp_block_size <= 0))
       goto out;
      if (unlikely(!PAGE_ALIGNED(req->tp_block_size))) // 注意tp_block_size必须与PAGE_SIZE对齐
       goto out;
      min_frame_size = po->tp_hdrlen + po->tp_reserve;
      if (po->tp_version >= TPACKET_V3 &&
          req->tp_block_size <
          BLK_PLUS_PRIV((u64)req_u->req3.tp_sizeof_priv) + min_frame_size)
       goto out;
      if (unlikely(req->tp_frame_size < min_frame_size))
       goto out;
      if (unlikely(req->tp_frame_size & (TPACKET_ALIGNMENT - 1)))
       goto out;
    
      rb->frames_per_block = req->tp_block_size / req->tp_frame_size;
      if (unlikely(rb->frames_per_block == 0))
       goto out;
      if (unlikely(rb->frames_per_block > UINT_MAX / req->tp_block_nr))
       goto out;
      if (unlikely((rb->frames_per_block * req->tp_block_nr) !=
         req->tp_frame_nr))
       goto out;
    
      err = -ENOMEM;
      order = get_order(req->tp_block_size);
      pg_vec = alloc_pg_vec(req, order); // 步骤3进入pg_vec分配内存
      if (unlikely(!pg_vec))
       goto out;
      switch (po->tp_version) {
      case TPACKET_V3:
       /* Block transmit is not supported yet */
       if (!tx_ring) {   //  只能是RX_RING
        init_prb_bdqc(po, rb, pg_vec, req_u); // 步骤3 rb->prb_bdqc->pkbdq引用了pg_vec
       } else {
        struct tpacket_req3 *req3 = &req_u->req3;
    
        if (req3->tp_retire_blk_tov ||
            req3->tp_sizeof_priv ||
            req3->tp_feature_req_word) {
         err = -EINVAL;
         goto out_free_pg_vec;
        }
       }
       break;
      default:
       if (!tx_ring) {
        rx_owner_map = bitmap_alloc(req->tp_frame_nr,
         GFP_KERNEL | __GFP_NOWARN | __GFP_ZERO);
        if (!rx_owner_map)
         goto out_free_pg_vec;
       }
       break;
      }
     }
     /* Done */
     else {
      err = -EINVAL;
      if (unlikely(req->tp_frame_nr))  // 上述第4、6步，tp_frame_nr字段必须为0，不能直接goto out 
       goto out;
     }
    
    
     /* Detach socket from network */
     spin_lock(&po->bind_lock);
     was_running = po->running; //release调用时，此值为0
     num = po->num;
     if (was_running) {
      WRITE_ONCE(po->num, 0);
      __unregister_prot_hook(sk, false);
     }
     spin_unlock(&po->bind_lock);
    
     synchronize_net();
    
     err = -EBUSY;
     mutex_lock(&po->pg_vec_lock);
     if (closing || atomic_read(&po->mapped) == 0) {  // closing字段一直为0，但是po->mapped字段一直等于0
      err = 0;
      spin_lock_bh(&rb_queue->lock);
      swap(rb->pg_vec, pg_vec); // 步骤3 pg_vec和rb->pg_vec交换，pg_vec为NULL，步骤4被换回来
      if (po->tp_version <= TPACKET_V2) //  只有在上述第6步，协议版本才等于TPACKET_V2，才会进入if
       swap(rb->rx_owner_map, rx_owner_map); // 步骤6 rx_owner_map指向同rb->prb_bdqc->pkbdq
      rb->frame_max = (req->tp_frame_nr - 1);
      rb->head = 0;
      rb->frame_size = req->tp_frame_size;
      spin_unlock_bh(&rb_queue->lock);
    
      swap(rb->pg_vec_order, order);
      swap(rb->pg_vec_len, req->tp_block_nr);
    
      rb->pg_vec_pages = req->tp_block_size/PAGE_SIZE;
      po->prot_hook.func = (po->rx_ring.pg_vec) ?
          tpacket_rcv : packet_rcv;
      skb_queue_purge(rb_queue);
      if (atomic_read(&po->mapped))
       pr_err("packet_mmap: vma is busy: %d\n",
              atomic_read(&po->mapped));
     }
     mutex_unlock(&po->pg_vec_lock);
    
     spin_lock(&po->bind_lock);
     if (was_running) {
      WRITE_ONCE(po->num, num);
      register_prot_hook(sk);
     }
     spin_unlock(&po->bind_lock);
     if (pg_vec && (po->tp_version > TPACKET_V2)) {
      /* Because we don't support block-based V3 on tx-ring */
      if (!tx_ring)
       prb_shutdown_retire_blk_timer(po, rb_queue);
     }
    
    out_free_pg_vec:
     bitmap_free(rx_owner_map);  // 步骤6 free掉rx_owner_map等于free rb->prb_bdqc->pkbdq，造成double free
     if (pg_vec)   // 步骤3由于pg_vec等于NULL为进入free,步骤4pg_vec不为NULL
      free_pg_vec(pg_vec, order, req->tp_block_nr);  // 步骤4由于释放pg_vec，同时rb->prb_bdqc->pkbdq变为悬空指针
    out:
     return err;
    }

上述步骤3中，进入init_prb_bdqc()函数增加了sock->rx_ring->prb_bdqc->pkbdq引用了pg_vec。

    
    
    /net/packet/af_packet.c
    
    static void init_prb_bdqc(struct packet_sock *po,
       struct packet_ring_buffer *rb,
       struct pgv *pg_vec,
       union tpacket_req_u *req_u)
    {
     struct tpacket_kbdq_core *p1 = GET_PBDQC_FROM_RB(rb);
     struct tpacket_block_desc *pbd;
    
     memset(p1, 0x0, sizeof(*p1));
    
     p1->knxt_seq_num = 1;
     p1->pkbdq = pg_vec;   // 步骤3 sock->rx_ring->prb_bdqc->pkbdq引用了pg_vec，造成漏洞的关键行为
     pbd = (struct tpacket_block_desc *)pg_vec[0].buffer;
     p1->pkblk_start = pg_vec[0].buffer;
     p1->kblk_size = req_u->req3.tp_block_size;
     p1->knum_blocks = req_u->req3.tp_block_nr;
     p1->hdrlen = po->tp_hdrlen;
     p1->version = po->tp_version;
     p1->last_kactive_blk_num = 0;
     po->stats.stats3.tp_freeze_q_cnt = 0;
     if (req_u->req3.tp_retire_blk_tov)
      p1->retire_blk_tov = req_u->req3.tp_retire_blk_tov;
     else
      p1->retire_blk_tov = prb_calc_retire_blk_tmo(po,
          req_u->req3.tp_block_size);
     p1->tov_in_jiffies = msecs_to_jiffies(p1->retire_blk_tov);
     p1->blk_sizeof_priv = req_u->req3.tp_sizeof_priv;
     rwlock_init(&p1->blk_fill_in_prog_lock);
    
     p1->max_frame_len = p1->kblk_size - BLK_PLUS_PRIV(p1->blk_sizeof_priv);
     prb_init_ft_ops(p1, req_u);
     prb_setup_retire_blk_timer(po);
     prb_open_block(p1, pbd);
    }

漏洞触发，引发panic：
![](https://images.seebug.org/content/images/2022/08/5fe12b3c-9712-41a2-b743-ddaf4b26db1e.png-w331s)

## 2.漏洞利用

### 2.1.绕过KASLR

**泄露内核地址思路：**
通过漏洞篡改msg_msg->m_ts成员，增大msg_msg消息大小，然后再读取该msg_msg，泄露邻近timerfd_ctx->tmr->function这个函数指针指向的timerfd_tmrproc内核函数地址来计算内核基地址，从而绕过KASLR。

**泄露内核地址详细步骤：**

1.先耗尽kmalloc-256的per_cpu上的freelist里的空闲块，然后布局PAGE大小的dummy ringbuf；

![](https://images.seebug.org/content/images/2022/08/d2a040ff-b2e2-49be-83bd-b31f2f252d7b.png-w331s)

2.第一次堆喷，首先释放dummy
ringbuf偶数下标的ringbuf，让这些free掉的PAGE都返还给伙伴系统的order-0。然后再用pg_vec去堆喷kmalloc-256的slab，并从伙伴系统的order-0取出PAGE分成16个kmalloc-256给pg_vec；

![](https://images.seebug.org/content/images/2022/08/8b47c64b-4123-4a9a-b1ba-014415845d5a.png-w331s)

3.第二次堆喷，释放dummy
ringbuf奇数下标的ringbuf，让这些free掉的PAGE都返还给伙伴系统的order-0。然后用timerfd_ctx去喷kmalloc-256的slab，并从伙伴系统的order-0取刚刚归还的PAGE分成16个kmalloc-256给timerfd_ctx；

![](https://images.seebug.org/content/images/2022/08/15a9691c-ef98-4728-8edd-ee0b91ee9cc1.png-w331s)

4.第三次堆喷，通过pg_vec的漏洞释放掉所有的第一次堆喷中的pg_vec对象，这些kmalloc-256的pg_vec不会归还给伙伴系统，而是进入到了对应slab的空闲链表，接着用msg_msg从空闲链表再次申请出刚释放掉的kmalloc-256的slab；

![](https://images.seebug.org/content/images/2022/08/a8ef8cb0-108c-4ad4-a9bf-1635ae98581b.png-w331s)

5.第四次堆喷，这时，触发部分pg_vec的double
free漏洞，然后用msg_msgseg再次将刚释放的msg_msg从freelist里分配出来并篡改msg_msg->m_ts，这时读取所有第三步中申请的msg_msg，即可读取包含被篡改msg_msg->m_ts的msg_msg，从而造成OOB读，泄露出相邻PAGE的timerfd_ctx->tmr->function这个函数指针指向的timerfd_tmrproc内核函数地址，从而计算出当前内核基址的相对偏移。

![](https://images.seebug.org/content/images/2022/08/34246eea-1314-4e3c-8390-a3d7fe86abe7.png-w331s)

### 2.2.利用方式一：篡改modprobe_path

> **提权思路：** 通过msg_msg +
> fuse的方式提权，篡改modprobe_path指向的字符串，modprobe_path默认指向"/sbin/modprobe"，修改modprobe_path指向"/tmp/w"，然后再执行一个非法的二进制文件，这样便会触发"/tmp/w"这个文件以root权限执行，从而拿到root权限。
>
> **提权原理：**
> 篡改modprobe_path提权的原理，想必大家也不陌生，这里还是简单介绍一下，当execve函数执行一个非法的二进制文件时，执行到search_binary_handler()函数时，会遍历formats链表，formats链表包含所有注册的二进制文件，挨个调用load_elf_binary()函数，判断当前执行文件格式是否是注册的二进制文件，如果不是注册的二进制文件，再调printable宏判断当前执行文件前4个字节是否是可打印的字符，如果当前执行文件既不是注册的二进制文件，前4个字节也不是可打印的字符，则调用request_module()函数。
    
    
    static int search_binary_handler(struct linux_binprm *bprm)
    {
     bool need_retry = IS_ENABLED(CONFIG_MODULES);
     struct linux_binfmt *fmt;
     int retval;
    
     retval = prepare_binprm(bprm);
     if (retval < 0)
      return retval;
    
     retval = security_bprm_check(bprm);
     if (retval)
      return retval;
    
     retval = -ENOENT;
     retry:
     read_lock(&binfmt_lock);
     list_for_each_entry(fmt, &formats, lh) { // 遍历注册了二进制格式的formats链表
      if (!try_module_get(fmt->module))
       continue;
      read_unlock(&binfmt_lock);
    
      retval = fmt->load_binary(bprm);  // 检查二进制文件
    
      read_lock(&binfmt_lock);
      put_binfmt(fmt);
      if (bprm->point_of_no_return || (retval != -ENOEXEC)) {
       read_unlock(&binfmt_lock);
       return retval;
      }
     }
     read_unlock(&binfmt_lock);
    
     if (need_retry) {
      if (printable(bprm->buf[0]) && printable(bprm->buf[1]) &&
          printable(bprm->buf[2]) && printable(bprm->buf[3]))  // 检查是否是打印字符
       return retval;
      if (request_module("binfmt-%04x", *(ushort *)(bprm->buf + 2)) < 0)
       return retval;
      need_retry = false;
      goto retry;
     }
    
     return retval;
    }

request_module()函数是__request_module()的宏定义。

    
    
    #define request_module(mod...) __request_module(true, mod)

__request_module()函数是一个尝试加载内核模块的函数，主要调用call_modprobe()，定义于kernel/kmod.c。

    
    
    static int call_modprobe(char *module_name, int wait)
    {
     struct subprocess_info *info;
     static char *envp[] = {
      "HOME=/",
      "TERM=linux",
      "PATH=/sbin:/usr/sbin:/bin:/usr/bin",
      NULL
     };
    
     char **argv = kmalloc(sizeof(char *[5]), GFP_KERNEL);
     if (!argv)
      goto out;
    
     module_name = kstrdup(module_name, GFP_KERNEL);
     if (!module_name)
      goto free_argv;
    
     argv[0] = modprobe_path;  // 是我们需要篡改的全局变量
     argv[1] = "-q";
     argv[2] = "--";
     argv[3] = module_name; /* check free_modprobe_argv() */
     argv[4] = NULL;
    
     info = call_usermodehelper_setup(modprobe_path, argv, envp, GFP_KERNEL,
          NULL, free_modprobe_argv, NULL);
     if (!info)
      goto free_module_name;
    
     return call_usermodehelper_exec(info, wait | UMH_KILLABLE); 
    
    free_module_name:
     kfree(module_name);
    free_argv:
     kfree(argv);
    out:
     return -ENOMEM;
    }

call_usermodehelper_exec()函数将modprobe_path作为可执行程序路径，以root权限执行，modprobe_path是一个全局变量，指向"/sbin/modprobe"。

    
    
    /kernel/kmod.c
    
    /*
     modprobe_path is set via /proc/sys.
    */
    char modprobe_path[KMOD_PATH_LEN] = CONFIG_MODPROBE_PATH;
    
    /init/Kconfig
    config MODPROBE_PATH
     string "Path to modprobe binary"
     default "/sbin/modprobe"
     help
       When kernel code requests a module, it does so by calling
       the "modprobe" userspace utility. This option allows you to
       set the path where that binary is found. This can be changed
       at runtime via the sysctl file
       /proc/sys/kernel/modprobe. Setting this to the empty string
       removes the kernel's ability to request modules (but
       userspace can still load modules explicitly).

**任意写：**
在绕过KASLR后，就能计算出modprobe_path的地址，再通过修改msg_msg的成员变量next指向modprobe_path-8，再配合fuse用户文件系统向msg_msg->next指向的msg_msgseg数据部分写入我们自定义程序的字符串路径，即完成任意写。

篡改前：modprobe_path指向"/sbin/modprobe"

![1661134889142](https://images.seebug.org/content/images/2022/08/29/1661742883000-1afkyg.png-w331s)

篡改后：modprobe_path指向"/tmp/w"

![1661135078798](https://images.seebug.org/content/images/2022/08/29/1661742883000-2tftju.png-w331s)

**提权流程：**

1.堆风水，先耗尽kmalloc-4096的空闲块，然后布局8 PAGE的内存，也是通过ringbuf申请大量的8 PAGE大小的内存块；

![](https://images.seebug.org/content/images/2022/08/d76396d9-9caf-4746-97a3-9a899056a097.png-w331s)

2.第一次堆喷，释放掉偶数位下标的8 PAGE的ringbuf，然后用大量的pg_vec去堆喷kmalloc-4096大小的slab；

![](https://images.seebug.org/content/images/2022/08/12ad1aff-1c44-4683-a027-eead5511fdc6.png-w331s)

3.第二次堆喷，触发first free释放掉2个kmalloc-4096的pg_vec，然后先创建一个线程A，用2个大于PAGE_SIZE小于2
PAGE_SIZE的msg_msgA去堆喷占位刚释放的两个kmalloc-4096空闲块，此时load_msg()在kmalloc完成后，会因为在copy_from_user的时候，触发fuse文件系统的读函数，通过读pipe数据而使线程A阻塞。

![](https://images.seebug.org/content/images/2022/08/e262261b-c025-4d2a-85f0-19727ccf3238.png-w331s)

4.第三次堆喷，然后再创建第二线程B，继续释放刚才被first free的2个kmalloc-4096的pg_vec内存，触发double
free，再用1个大于PAGE_SIZE小于2
PAGE_SIZE的msg_msgB去堆喷这两块刚被回收的2个kmalloc-4096内存块，用msg_msgsegB去篡改第二次堆喷中msg_msgA->next指针为modprobe-8，并通过pipe发送信号给第三步中阻塞的线程A，fuse
read接受到信号后完成对msg_msgsegA内容的篡改，并返回，这样线程A完成对modprobe_path指向字符串内容的篡改为我们自定义的"/tmp/w"。

![1660287345065](https://images.seebug.org/content/images/2022/08/29/1661742890000-3hkduz.png-w331s)

5.最后执行一个非法的二进制文件，便能触发我们自定义"/tmp/w"的执行，从而完成提权。

![图片](https://images.seebug.org/content/images/2022/08/29/1661745955000-13sknwk.png-w331s)

### 2.3.利用方式二：USMA(用户态映射攻击)

> **USMA简介** ：USMA（User-Space-Mmaping-Attack）又称作是 **用户态映射攻击**
> ，是360漏洞研究院的安全研究员提出的利用手法。
>
> **提权思路** ：利用packet漏洞模块的packet_mmap函数能将漏洞对象pg_vec映射到用户空间的这个特性，再利用double
> free的漏洞原理，将漏洞对象pg_vec篡改为内核代码 **__sys_setresuid** 内核函数的地址，这样就能把
> **__sys_setresuid**
> 内核函数的代码映射到用户空间，通过硬编码改变代码逻辑，即可让普通用户进程调用setresuid函数绕过权限检查，修改cred提升权限。
    
    
    /kernel/sys.c
    
    /*
     * This function implements a generic ability to update ruid, euid,
     * and suid.  This allows you to implement the 4.4 compatible seteuid().
     */
    long __sys_setresuid(uid_t ruid, uid_t euid, uid_t suid)
    {
     struct user_namespace *ns = current_user_ns();
     const struct cred *old;
     struct cred *new;
     int retval;
     kuid_t kruid, keuid, ksuid;
    
     kruid = make_kuid(ns, ruid);
     keuid = make_kuid(ns, euid);
     ksuid = make_kuid(ns, suid);
    
     if ((ruid != (uid_t) -1) && !uid_valid(kruid))
      return -EINVAL;
    
     if ((euid != (uid_t) -1) && !uid_valid(keuid))
      return -EINVAL;
    
     if ((suid != (uid_t) -1) && !uid_valid(ksuid))
      return -EINVAL;
    
     new = prepare_creds();
     if (!new)
      return -ENOMEM;
    
     old = current_cred();
    
     retval = -EPERM;
     //通过硬编码修改，让普通用户调用setresuid()函数不会进入if判断，从而修改cred提权
     if (!ns_capable_setid(old->user_ns, CAP_SETUID)) {
      if (ruid != (uid_t) -1        && !uid_eq(kruid, old->uid) &&
          !uid_eq(kruid, old->euid) && !uid_eq(kruid, old->suid))
       goto error;
      if (euid != (uid_t) -1        && !uid_eq(keuid, old->uid) &&
          !uid_eq(keuid, old->euid) && !uid_eq(keuid, old->suid))
       goto error;
      if (suid != (uid_t) -1        && !uid_eq(ksuid, old->uid) &&
          !uid_eq(ksuid, old->euid) && !uid_eq(ksuid, old->suid))
       goto error;
     }
    
     if (ruid != (uid_t) -1) {
      new->uid = kruid;
      if (!uid_eq(kruid, old->uid)) {
       retval = set_user(new);
       if (retval < 0)
        goto error;
      }
     }
     if (euid != (uid_t) -1)
      new->euid = keuid;
     if (suid != (uid_t) -1)
      new->suid = ksuid;
     new->fsuid = new->euid;
    
     retval = security_task_fix_setuid(new, old, LSM_SETID_RES);
     if (retval < 0)
      goto error;
    
     return commit_creds(new);
    
    error:
     abort_creds(new);
     return retval;
    }
    
    SYSCALL_DEFINE3(setresuid, uid_t, ruid, uid_t, euid, uid_t, suid)
    {
     return __sys_setresuid(ruid, euid, suid);
    }

**映射原理** ：packet_mmap函数通过对当前套接字对应的pg_vec数组里buffer映射到用户层，可以让用户态修改并同步内核态的内存。

    
    
    static int packet_mmap(struct file *file, struct socket *sock,
      struct vm_area_struct *vma)
    {
     struct sock *sk = sock->sk;
     struct packet_sock *po = pkt_sk(sk);
     unsigned long size, expected_size;
     struct packet_ring_buffer *rb;
     unsigned long start;
     int err = -EINVAL;
     int i;
    
     if (vma->vm_pgoff)
      return -EINVAL;
    
     mutex_lock(&po->pg_vec_lock);
    
     expected_size = 0;
     for (rb = &po->rx_ring; rb <= &po->tx_ring; rb++) {
      if (rb->pg_vec) {
     // 计算当前套接字对应ringbuf所有大小的和，间接等于ring buf的block_nr * block_size。
       expected_size += rb->pg_vec_len  // 等于block_nr
          * rb->pg_vec_pages  // 等于block_size/PAGE_SIZE
          * PAGE_SIZE;
      }
     }
    
     if (expected_size == 0)
      goto out;
    
     size = vma->vm_end - vma->vm_start;  // 用户层映射内存大小
     if (size != expected_size)
      goto out;
    
     start = vma->vm_start;    // 用户层映射内存起始地址
     for (rb = &po->rx_ring; rb <= &po->tx_ring; rb++) { //目前就一个ring buf
      if (rb->pg_vec == NULL)
       continue;
    
      for (i = 0; i < rb->pg_vec_len; i++) { // 循环block_nr次
       struct page *page;
       void *kaddr = rb->pg_vec[i].buffer; // kaddr地址基本都是页对齐的
       int pg_num;
       // 循环block_size/PAGE_SIZE次
       for (pg_num = 0; pg_num < rb->pg_vec_pages; pg_num++) {
        page = pgv_to_page(kaddr);
        // 映射的主要函数，通过该函数将pg_vec数组里buffer映射到用户层
        err = vm_insert_page(vma, start, page); 
        if (unlikely(err))
         goto out;
        start += PAGE_SIZE;
        kaddr += PAGE_SIZE;
       }
      }
     }
    
     atomic_inc(&po->mapped);
     vma->vm_ops = &packet_mmap_ops;
     err = 0;
    
    out:
     mutex_unlock(&po->pg_vec_lock);
     return err;
    }

正如[360的USMA](https://vul.360.net/archives/391)的描述，在vm_insert_page()函数里调用了validate_page_before_insert()函数做页检查，validate_page_before_insert()函数对映射的pg_vec数组里的buffer所属page的类型进行了判断，过滤了匿名页、属于slab对象的页、属于buddy系统的页、属于交换内存的页、属于分页管理中页表的页、属于内存屏障的页，以上页类型都不能映射，恰好我们要映射的是内核代码段，是可以映射到用户态的。

    
    
    /mm/memory.c
    
    static int validate_page_before_insert(struct page *page)
    {
     if (PageAnon(page) || PageSlab(page) || page_has_type(page))
      return -EINVAL;
     flush_dcache_page(page);
     return 0;
    }

**硬编码篡改** ： __sys_setresuid函数被映射到用户态后，读取一个PAGE_SIZE大小的内核内存

考虑到需要篡改call ns_capable_setid调用之后的判断，对test al,al jnz short
loc_FFFFFFFF810BE1C4的汇编作一番篡改，最简单的方法就是将jnz/jne改为jz/je，由机器码，0x75改为0x74，由于映射的内存范围很大，所以我将0x84
0xC0 0x75 0x59作为特征进行搜索定位。

![1660702474261](https://images.seebug.org/content/images/2022/08/29/1661742892000-4opbzq.png-w331s)

这段机器码由0x84 0xC0 0x75 0x59变为0x84 0xC0 0x74 0x59，jne变为je。

篡改前：

![1660703547438](https://images.seebug.org/content/images/2022/08/29/1661742893000-5cfhfn.png-w331s)

篡改后：

![1660703431605](https://images.seebug.org/content/images/2022/08/29/1661742894000-6bacpg.png-w331s)

**提权**
：经过上述对内核函数__sys_setresuid的篡改，再通过调用setresuid(0,0,0);即可将普通用户进程提权至root用户权限。

![](https://blog-1257303866.cos.ap-guangzhou.myqcloud.com/img/1660120980411.gif)

## 3.总结

上述两种提权方式，经过实现与调试，篡改modprobe_path提权和USMA(用户态映射攻击)两者都是通过任意写完成的提权，不用一堆gadget，相比ROP的提权方式而言，适配效率更高，限制更小，让任意写提权相对显得更加"高大上"。篡改modprobe_path提权相比于USMA利用，前者相较而言更加通用。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1952/>

