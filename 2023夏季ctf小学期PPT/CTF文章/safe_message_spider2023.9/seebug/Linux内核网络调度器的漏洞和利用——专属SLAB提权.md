**作者： 360漏洞研究院 王晓东 刘永  
原文链接：<https://vul.360.net/archives/600>**

## 背景

### The u32 filter Overview

所在模块：

    
    
    net/sched/cls_u32.c

Ugly (or Universal) 32bit key Packet Classifier.

#### Linux TC(traffic control) 流量控制介绍

Linux TC 对多个特定的ip施加不同的吞吐量throughput以及延迟delay限制

![img](https://images.seebug.org/content/images/2022/12/26/1672039338000-1fsxva.png-w331s)

##### netlink与TC

TC是基于Netlink协议实现的。

![img](https://images.seebug.org/content/images/2022/12/26/1672039339000-2ajwrb.png-w331s)

默认的Qdisc

![img](https://images.seebug.org/content/images/2022/12/26/1672039340000-3ojwcu.png-w331s)

多队列默认Qdisc

![img](https://images.seebug.org/content/images/2022/12/26/1672039340000-4jrdlg.png-w331s)

一个定制的qdisc设置

![img](https://images.seebug.org/content/images/2022/12/26/1672039340000-5hpewb.png-w331s)

##### 一个例子

传输质量控制，传输的带宽和延时

![img](https://images.seebug.org/content/images/2022/12/26/1672039340000-6eiqwb.png-w331s)

使用一些SHELL命令就可以实现对TC的使用。也可以通过Netlink编程实现。

## 漏洞挖掘

为了2021年天府杯比赛，我整理了syzkaller之前本地打出来的漏洞。发现一个UAF在专属SLAB上的漏洞，因为这种漏洞之前没有过利用，但报着试试看的心态给

![](https://images.seebug.org/content/images/2022/12/b73998a0-42e4-4093-8fd6-5227ec19ae77.png-w331s)

漏洞给刘永进行分析，发现这个UAF在专属SLAB上的漏洞，可能可以实现提权。大概在10月左右实现漏洞利用。又因为还有其它漏洞可以参加比赛，而这个漏洞的隐蔽性和提权成功率相对比较好，而且一个漏洞可以完成信息泄漏和提权，所以予以保留。

    
    
    [  203.112091] ==================================================================
    [  203.112113] BUG: KASAN: use-after-free in sock_prot_inuse_add+0x80/0x90
    [  203.112121] Read of size 8 at addr ffff888106660188 by task poc/6597
    
    [  203.112134] CPU: 0 PID: 6597 Comm: poc Tainted: G                 ---------r-  - 4.18.0+ #32
    [  203.112138] Hardware name: VMware, Inc. VMware Virtual Platform/440BX Desktop Reference Platform, BIOS 6.00 07/22/2020
    [  203.112140] Call Trace:
    [  203.112148]  dump_stack+0xa4/0xea
    [  203.112164]  print_address_description.constprop.5+0x1e/0x230
    [  203.112197]  __kasan_report.cold.7+0x37/0x82
    [  203.112210]  kasan_report+0x3b/0x50
    [  203.112217]  sock_prot_inuse_add+0x80/0x90
    [  203.112224]  netlink_release+0x97f/0x1190
    [  203.112257]  __sock_release+0xd3/0x2b0
    [  203.112262]  sock_close+0x1e/0x30
    [  203.112267]  __fput+0x2d4/0x840
    [  203.112275]  task_work_run+0x16e/0x1d0
    [  203.112284]  exit_to_usermode_loop+0x207/0x230
    [  203.112290]  do_syscall_64+0x3f5/0x470
    [  203.112302]  entry_SYSCALL_64_after_hwframe+0x65/0xca
    [  203.112308] RIP: 0033:0x7fee34abd1a8
    [  203.112315] Code: 07 02 00 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 44 00 00 f3 0f 1e fa 48 8d 05 b5 44 2d 00 8b 00 85 c0 75 17 b8 03 00 00 00 0f 05 <48> 3d 00 f0 ff ff 77 40 c3 0f 1f 80 00 00 00 00 53 89 fb 48 83 ec
    [  203.112318] RSP: 002b:00007ffdb62366c8 EFLAGS: 00000246 ORIG_RAX: 0000000000000003
    [  203.112323] RAX: 0000000000000000 RBX: 0000000000000000 RCX: 00007fee34abd1a8
    [  203.112327] RDX: 0000000000000000 RSI: 00000000200001c0 RDI: 0000000000000004
    [  203.112330] RBP: 00007ffdb62366e0 R08: 00007ffdb62366e0 R09: 00007ffdb62366e0
    [  203.112333] R10: 00007ffdb62366e0 R11: 0000000000000246 R12: 0000000000400f50
    [  203.112337] R13: 00007ffdb6236820 R14: 0000000000000000 R15: 0000000000000000
    
    [  203.112345] Allocated by task 6247:
    [  203.112353]  kasan_save_stack+0x1d/0x80
    [  203.112359]  __kasan_kmalloc.constprop.10+0xc1/0xd0
    [  203.112367]  slab_post_alloc_hook+0x43/0x280
    [  203.112377]  kmem_cache_alloc+0x131/0x280
    [  203.112386]  copy_net_ns+0xec/0x330
    [  203.112395]  create_new_namespaces+0x583/0x9a0
    [  203.112404]  unshare_nsproxy_namespaces+0xcb/0x200
    [  203.112414]  ksys_unshare+0x468/0x8d0
    [  203.112423]  __x64_sys_unshare+0x36/0x50
    [  203.112432]  do_syscall_64+0xe4/0x470
    [  203.112443]  entry_SYSCALL_64_after_hwframe+0x65/0xca
    
    [  203.112453] Freed by task 59:
    [  203.112487]  kasan_save_stack+0x1d/0x80
    [  203.112510]  kasan_set_track+0x20/0x30
    [  203.112535]  kasan_set_free_info+0x1f/0x30
    [  203.112557]  __kasan_slab_free+0x108/0x150
    [  203.112578]  kmem_cache_free+0x83/0x430
    [  203.112593]  net_drop_ns+0x7d/0x90
    [  203.112604]  cleanup_net+0x6ee/0x960
    [  203.112619]  process_one_work+0x742/0x1030
    [  203.112632]  worker_thread+0x95/0xce0
    [  203.112643]  kthread+0x32c/0x3f0
    [  203.112654]  ret_from_fork+0x35/0x40
    
    [  203.112686] The buggy address belongs to the object at ffff888106660000
                    which belongs to the cache net_namespace of size 8000
    [  203.112698] The buggy address is located 392 bytes inside of
                    8000-byte region [ffff888106660000, ffff888106661f40)
    [  203.112704] The buggy address belongs to the page:
    [  203.112739] page:ffffea0004199800 refcount:1 mapcount:0 mapping:00000000306a7880 index:0xffff888106664080 head:ffffea0004199800 order:3 compound_mapcount:0 compound_pincount:0
    [  203.112752] flags: 0x17ffffc0008100(slab|head)
    [  203.112774] raw: 0017ffffc0008100 dead000000000100 dead000000000200 ffff88810b6ff600
    [  203.112792] raw: ffff888106664080 0000000080030002 00000001ffffffff ffff888101f819c1
    [  203.112798] page dumped because: kasan: bad access detected
    [  203.112803] pages's memcg:ffff888101f819c1
    
    [  203.112814] Memory state around the buggy address:
    [  203.112831]  ffff888106660080: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
    [  203.112857]  ffff888106660100: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
    [  203.112868] >ffff888106660180: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
    [  203.112873]                       ^
    [  203.112884]  ffff888106660200: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
    [  203.112894]  ffff888106660280: fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb fb
    [  203.112900] =================================================================

但是在2022/04/12在syzbot上与打出了类似的漏洞，是一个Warning，随后被社区修复。最后这个漏洞利用输出到国内的安全大赛。

![img](https://images.seebug.org/content/images/2022/12/26/1672039341000-8igskz.png-w331s)

## 漏洞原理

### 原始PoC

syzkaller自动转化的PoC可以稳定地触发漏洞。

分配

    
    
    unshare
    |-> __x64_sys_unshare
     |-> ksys_unshare
      |-> unshare_nsproxy_namespaces
       |-> copy_net_ns
        |-> kmem_cache_alloc

释放

    
    
    exit_process
     |-> ret_from_fork
      |-> kthread
       |-> worker_thread
        |-> process_one_work
         |-> cleanup_net
          |-> net_drop_ns
           |-> kmem_cache_free

UAF

    
    
    sock_close
     |-> exit_to_usermode_loop
      |-> task_work_run
       |-> __fput
        |-> sock_close
         |-> __sock_release
          |-> sock_prot_inuse_add

分配net的源代码

    
    
    net/core/net_namespace.c
    445 struct net *copy_net_ns(unsigned long flags,
     446                         struct user_namespace *user_ns, struct net *old_net)
     447 {
     448         struct ucounts *ucounts;
     449         struct net *net;
     450         int rv;
     451 
     452         if (!(flags & CLONE_NEWNET))
     453                 return get_net(old_net);
     454 
     455         ucounts = inc_net_namespaces(user_ns);
     456         if (!ucounts)
     457                 return ERR_PTR(-ENOSPC);
     458 
     459         net = net_alloc();    <---     460         if (!net) {
     461                 rv = -ENOMEM;
     462                 goto dec_ucounts;
     463         }
     464         refcount_set(&net->passive, 1);
     465         net->ucounts = ucounts;
     466         get_user_ns(user_ns);
    ....
     487         return net;
     488 }
     395 static struct net *net_alloc(void)
     396 {
     397         struct net *net = NULL;
     398         struct net_generic *ng;
     399 
     400         ng = net_alloc_generic();
     401         if (!ng)
     402                 goto out;
     403 
     404         net = kmem_cache_zalloc(net_cachep, GFP_KERNEL);    <---     405         if (!net)
     406                 goto out_free;
     407 
    ....
     427 }
    $ sudo cat /sys/kernel/slab/net_namespace/object_size 
    4928
    $ sudo cat /sys/kernel/slab/net_namespace/order 
    3

释放函数

    
    
    437 void net_drop_ns(void *p)
     438 {
     439         struct net *net = (struct net *)p;
     440 
     441         if (net)
     442                 net_free(net);
     443 }       
     444

UAF的结构（下文将net_namespace统称为net结构）

    
    
     56 struct net {
     57         /* First cache line can be often dirtied.
     58         |* Do not place here read-mostly fields.
     59         |*/
     60         refcount_t              passive;        /* To decide when the network
     61                                                 |* namespace should be freed.
     62                                                 |*/
     63         spinlock_t              rules_mod_lock;
     64 
     65         unsigned int            dev_unreg_count;
     66 
     67         unsigned int            dev_base_seq;   /* protected by rtnl_mutex */
     68         int                     ifindex;
     69 
     70         spinlock_t              nsid_lock;
     71         atomic_t                fnhe_genid;
     72 
     73         struct list_head        list;           /* list of network namespaces */
     74         struct list_head        exit_list;      /* To linked to call pernet exit
     75                                                 |* methods on dead net (
     76                                                 |* pernet_ops_rwsem read locked),
     77                                                 |* or to unregister pernet ops
     78                                                 |* (pernet_ops_rwsem write locked).
     79                                                 |*/
     80         struct llist_node       cleanup_list;   /* namespaces on death row */
     81 
     82 #ifdef CONFIG_KEYS
     83         struct key_tag          *key_domain;    /* Key domain of operation tag */
     84 #endif
     85         struct user_namespace   *user_ns;       /* Owning user namespace */
     86         struct ucounts          *ucounts;
     87         struct idr              netns_ids;
     88 
     89         struct ns_common        ns;    <---/*现实任意地址读*/
     90 
     91         struct list_head        dev_base_head;
     92         struct proc_dir_entry   *proc_net;
     93         struct proc_dir_entry   *proc_net_stat;
     94 
     95 #ifdef CONFIG_SYSCTL
     96         struct ctl_table_set    sysctls;
     97 #endif
     98 
     99         struct sock             *rtnl;                  /* rtnetlink socket */
    100         struct sock             *genl_sock;
    101 
    102         struct uevent_sock      *uevent_sock;           /* uevent socket */
    103 
    104         struct hlist_head       *dev_name_head;
    105         struct hlist_head       *dev_index_head;
    106         struct raw_notifier_head        netdev_chain;
    107 
    108         /* Note that @hash_mix can be read millions times per second,
    109         |* it is critical that it is on a read_mostly cache line.
    110         |*/
    111         u32                     hash_mix;
    112 
    113         struct net_device       *loopback_dev;          /* The loopback */
    114 
    115         /* core fib_rules */
    116         struct list_head        rules_ops;
    117 
    118         struct netns_core       core;
    119         struct netns_mib        mib;
    120         struct netns_packet     packet;
    121         struct netns_unix       unx;
    122         struct netns_nexthop    nexthop;
    123         struct netns_ipv4       ipv4;
    124 #if IS_ENABLED(CONFIG_IPV6)
    125         struct netns_ipv6       ipv6;
    126 #endif
    127 #if IS_ENABLED(CONFIG_IEEE802154_6LOWPAN)
    128         struct netns_ieee802154_lowpan  ieee802154_lowpan;
    129 #endif
    130 #if defined(CONFIG_IP_SCTP) || defined(CONFIG_IP_SCTP_MODULE)
    131         struct netns_sctp       sctp;
    132 #endif
    133 #ifdef CONFIG_NETFILTER
    134         struct netns_nf         nf;
    135 #if defined(CONFIG_NF_CONNTRACK) || defined(CONFIG_NF_CONNTRACK_MODULE)
    136         struct netns_ct         ct;
    137 #endif
    138 #if defined(CONFIG_NF_TABLES) || defined(CONFIG_NF_TABLES_MODULE)
    139         struct netns_nftables   nft;
    140 #endif
    141 #endif
    142 #ifdef CONFIG_WEXT_CORE
    143         struct sk_buff_head     wext_nlevents;
    144 #endif
    145         struct net_generic __rcu        *gen;
    146 
    147         /* Used to store attached BPF programs */
    148         struct netns_bpf        bpf;
    149 
    150         /* Note : following structs are cache line aligned */
    151 #ifdef CONFIG_XFRM
    152         struct netns_xfrm       xfrm;
    153 #endif
    154 
    155         u64                     net_cookie; /* written once */
    156 
    157 #if IS_ENABLED(CONFIG_IP_VS)
    158         struct netns_ipvs       *ipvs;
    159 #endif
    160 #if IS_ENABLED(CONFIG_MPLS)
    161         struct netns_mpls       mpls;
    162 #endif
    163 #if IS_ENABLED(CONFIG_CAN)
    164         struct netns_can        can;
    165 #endif
    166 #ifdef CONFIG_XDP_SOCKETS
    167         struct netns_xdp        xdp;
    168 #endif
    169 #if IS_ENABLED(CONFIG_MCTP)
    170         struct netns_mctp       mctp;
    171 #endif
    172 #if IS_ENABLED(CONFIG_CRYPTO_USER)
    173         struct sock             *crypto_nlsk;
    174 #endif
    175         struct sock             *diag_nlsk;
    176 #if IS_ENABLED(CONFIG_SMC)
    177         struct netns_smc        smc;
    178 #endif
    179 } __randomize_layout;

### PoC改写

经过进一步的分析，是因为u32_change函数会错误地减少nets的引用计数，从而导致UAF的逻辑问题。从此出发，优化了PoC的触发路径。

    
    
    u32_change()
     |--> u32_destroy_key()
      |--> tcf_exts_put_net()
       |--> put_net()

同时构造出对net上引用计数减1的逻辑原语。

![img](https://images.seebug.org/content/images/2022/12/26/1672039342000-9ktmem.png-w331s)

优化后的触发流程如下：

    
    
    [  253.623920] ------------[ cut here ]------------    [  253.623929] refcount_t: underflow; use-after-free.
    [  253.623984] WARNING: CPU: 0 PID: 4009 at lib/refcount.c:28 refcount_warn_saturate+0x10c/0x1f0
    [  253.624026] Modules linked in: act_police cls_u32 ip6_gre gre ip6_tunnel tunnel6 uas usb_storage binfmt_misc snd_seq_dummy snd_hrtimer vsock_loopback vmw_vsock_virtio_transport_common vmw_vsock_vmci_transport vsock snd_ens1371 snd_ac97_codec gameport ac97_bus snd_pcm snd_seq_midi snd_seq_midi_event snd_rawmidi intel_rapl_msr intel_rapl_common nls_iso8859_1 snd_seq crct10dif_pclmul ghash_clmulni_intel sch_fq_codel aesni_intel snd_seq_device crypto_simd snd_timer cryptd snd vmw_balloon joydev rapl input_leds soundcore vmw_vmci serio_raw vmwgfx ttm drm_kms_helper mac_hid cec rc_core fb_sys_fops syscopyarea sysfillrect sysimgblt ipmi_devintf ipmi_msghandler msr parport_pc ppdev lp drm parport ip_tables x_tables autofs4 hid_generic crc32_pclmul psmouse usbhid ahci mptspi hid libahci mptscsih e1000 mptbase scsi_transport_spi i2c_piix4 pata_acpi floppy
    [  253.624306] CPU: 0 PID: 4009 Comm: apparmor_parser Tainted: G    B             5.15.30+ #2
    [  253.624330] Hardware name: VMware, Inc. VMware Virtual Platform/440BX Desktop Reference Platform, BIOS 6.00 07/22/2020
    [  253.624338] RIP: 0010:refcount_warn_saturate+0x10c/0x1f0
    [  253.624351] Code: 1d 6d 3a 1d 03 31 ff 89 de e8 90 f1 18 ff 84 db 75 a0 e8 47 f6 18 ff 48 c7 c7 e0 f0 65 85 c6 05 4d 3a 1d 03 01 e8 f2 76 57 01 <0f> 0b eb 84 e8 2b f6 18 ff 0f b6 1d 36 3a 1d 03 31 ff 89 de e8 5b
    [  253.624361] RSP: 0000:ffff888137fafc90 EFLAGS: 00010282
    [  253.624369] RAX: 0000000000000000 RBX: 0000000000000000 RCX: 0000000000000000
    [  253.624376] RDX: ffff88810caf0000 RSI: 0000000000000100 RDI: ffffed1026ff5f84
    [  253.624383] RBP: ffff888137fafca0 R08: 0000000000000100 R09: ffff8881e183098b
    [  253.624390] R10: 0000000000000000 R11: 0000000000000001 R12: ffff888120ec008c
    [  253.624397] R13: ffff888105f42000 R14: ffff888120ec0000 R15: ffff888120ec008c
    [  253.624404] FS:  00007fc64fc8d740(0000) GS:ffff8881e1800000(0000) knlGS:0000000000000000
    [  253.624414] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    [  253.624421] CR2: 000055893f3fadf9 CR3: 0000000135002001 CR4: 00000000003706f0
    [  253.624445] Call Trace:
    [  253.624451]  <TASK>
    [  253.624458]  __sk_destruct+0x693/0x790
    [  253.624478]  sk_destruct+0xd3/0x100
    [  253.624494]  __sk_free+0xfe/0x400
    [  253.624509]  sk_free+0x88/0xc0
    [  253.624524]  deferred_put_nlk_sk+0x170/0x320
    [  253.624544]  rcu_core+0x51a/0x1250
    [  253.624607]  rcu_core_si+0xe/0x10
    [  253.624618]  __do_softirq+0x189/0x536
    [  253.624631]  irq_exit_rcu+0xec/0x130
    [  253.624641]  sysvec_apic_timer_interrupt+0x40/0x90
    [  253.624664]  asm_sysvec_apic_timer_interrupt+0x12/0x20
    [  253.624675] RIP: 0033:0x55893f2e92d2
    [  253.624685] Code: c3 0f 1f 80 00 00 00 00 48 39 cb 74 3b 48 8b 7d 10 49 89 d8 4c 89 ee 48 8b 07 48 89 54 24 68 44 89 f2 48 89 4c 24 60 4c 89 e1 <48> 8b 40 38 48 83 c4 28 5b 5d 41 5c 41 5d 41 5e 41 5f ff e0 66 2e
    [  253.624694] RSP: 002b:00007ffc26b6c960 EFLAGS: 00000202
    [  253.624703] RAX: 000055893f3ec3a0 RBX: 0000558940c048d0 RCX: 000055893f3eb588
    [  253.624710] RDX: 0000000000000006 RSI: 0000000000000000 RDI: 000055893f3eb510
    [  253.624717] RBP: 000055893f3eb528 R08: 0000558940c048d0 R09: 000055893f3eb4a0
    [  253.624723] R10: 0000558940e14270 R11: 00007fc64fea9ce0 R12: 000055893f3eb588
    [  253.624730] R13: 0000000000000000 R14: 0000000000000006 R15: 000055893f3a48e8
    [  253.624740]  </TASK>
    [  253.624743] ---[ end trace ddbeecae4d8b2b8c ]---    [  253.626421] ------------[ cut here ]------------    [  253.626431] refcount_t: saturated; leaking memory.
    [  253.626489] WARNING: CPU: 3 PID: 309 at lib/refcount.c:19 refcount_warn_saturate+0x1bd/0x1f0
    [  253.626513] Modules linked in: act_police cls_u32 ip6_gre gre ip6_tunnel tunnel6 uas usb_storage binfmt_misc snd_seq_dummy snd_hrtimer vsock_loopback vmw_vsock_virtio_transport_common vmw_vsock_vmci_transport vsock snd_ens1371 snd_ac97_codec gameport ac97_bus snd_pcm snd_seq_midi snd_seq_midi_event snd_rawmidi intel_rapl_msr intel_rapl_common nls_iso8859_1 snd_seq crct10dif_pclmul ghash_clmulni_intel sch_fq_codel aesni_intel snd_seq_device crypto_simd snd_timer cryptd snd vmw_balloon joydev rapl input_leds soundcore vmw_vmci serio_raw vmwgfx ttm drm_kms_helper mac_hid cec rc_core fb_sys_fops syscopyarea sysfillrect sysimgblt ipmi_devintf ipmi_msghandler msr parport_pc ppdev lp drm parport ip_tables x_tables autofs4 hid_generic crc32_pclmul psmouse usbhid ahci mptspi hid libahci mptscsih e1000 mptbase scsi_transport_spi i2c_piix4 pata_acpi floppy
    [  253.626837] CPU: 3 PID: 309 Comm: kworker/u256:28 Tainted: G    B   W         5.15.30+ #2
    [  253.626851] Hardware name: VMware, Inc. VMware Virtual Platform/440BX Desktop Reference Platform, BIOS 6.00 07/22/2020
    [  253.626859] Workqueue: netns cleanup_net
    [  253.626874] RIP: 0010:refcount_warn_saturate+0x1bd/0x1f0
    [  253.626888] Code: 03 31 ff 89 de e8 e3 f0 18 ff 84 db 0f 85 ef fe ff ff e8 96 f5 18 ff 48 c7 c7 e0 ef 65 85 c6 05 9f 39 1d 03 01 e8 41 76 57 01 <0f> 0b e9 d0 fe ff ff e8 77 f5 18 ff 48 c7 c7 40 f1 65 85 c6 05 7c
    [  253.626899] RSP: 0000:ffff8881032ff688 EFLAGS: 00010282
    [  253.626908] RAX: 0000000000000000 RBX: 0000000000000000 RCX: 0000000000000000
    [  253.626915] RDX: ffff888103093380 RSI: 0000000000000000 RDI: ffffed102065fec3
    [  253.626922] RBP: ffff8881032ff698 R08: 0000000000000000 R09: ffff8881e19b098b
    [  253.626930] R10: 0000000000000000 R11: 0000000000000001 R12: ffff888120ec008c
    [  253.626936] R13: ffff88812dc76500 R14: dffffc0000000000 R15: 00000000c0000000
    [  253.626944] FS:  0000000000000000(0000) GS:ffff8881e1980000(0000) knlGS:0000000000000000
    [  253.626954] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    [  253.626961] CR2: 00007f2ede8e1024 CR3: 00000001736a6006 CR4: 00000000003706e0
    [  253.626993] Call Trace:
    [  253.626997]  <TASK>
    [  253.627006]  u32_clear_hnode+0x4c7/0x680 [cls_u32]
    [  253.627058]  u32_destroy_hnode.isra.0+0xa4/0x240 [cls_u32]
    [  253.627069]  u32_destroy+0x2da/0x390 [cls_u32]
    [  253.627080]  tcf_proto_destroy+0x85/0x300
    [  253.627091]  tcf_proto_put+0x9c/0xd0
    [  253.627101]  tcf_chain_flush+0x1c0/0x310
    [  253.627112]  __tcf_block_put+0x158/0x2e0
    [  253.627123]  tcf_block_put+0xe3/0x130
    [  253.627178]  fq_codel_destroy+0x3c/0xb0 [sch_fq_codel]
    [  253.627189]  qdisc_destroy+0xb1/0x2a0
    [  253.627200]  qdisc_put+0xe0/0x100
    [  253.627211]  dev_shutdown+0x253/0x390
    [  253.627224]  unregister_netdevice_many+0x7e0/0x1720
    [  253.627282]  ip6gre_exit_batch_net+0x36b/0x450 [ip6_gre]
    [  253.627367]  ops_exit_list+0x115/0x160
    [  253.627378]  cleanup_net+0x475/0xb40
    [  253.627403]  process_one_work+0x8bf/0x11d0
    [  253.627416]  worker_thread+0x60b/0x1340
    [  253.627441]  kthread+0x388/0x470
    [  253.627461]  ret_from_fork+0x22/0x30
    [  253.627476]  </TASK>
    [  253.627480] ---[ end trace ddbeecae4d8b2b8d ]---
### 漏洞补丁

在u32_change函数中，不应该执行tcf_exts_put_net函数（使得nets上的引用计数减少1）。

    
    
    author Eric Dumazet <edumazet@google.com> 2022-04-13 10:35:41 -0700
    committer Jakub Kicinski <kuba@kernel.org> 2022-04-15 14:26:11 -0700
    commit 3db09e762dc79584a69c10d74a6b98f89a9979f8 (patch)
    tree 1a269d290124f61d42c2cb059de92a0661f818a5
    parent f3226eed54318e7bdc186f8f7ed27bcd3cb8b681 (diff)
    download linux-3db09e762dc79584a69c10d74a6b98f89a9979f8.tar.gz
    net/sched: cls_u32: fix netns refcount changes in u32_change()
    We are now able to detect extra put_net() at the moment
    they happen, instead of much later in correct code paths.
    
    u32_init_knode() / tcf_exts_init() populates the ->exts.net
    pointer, but as mentioned in tcf_exts_init(),
    the refcount on netns has not been elevated yet.
    
    The refcount is taken only once tcf_exts_get_net()
    is called.
    
    So the two u32_destroy_key() calls from u32_change()
    are attempting to release an invalid reference on the netns.
    
    syzbot report:
    
    refcount_t: decrement hit 0; leaking memory.
    WARNING: CPU: 0 PID: 21708 at lib/refcount.c:31 refcount_warn_saturate+0xbf/0x1e0 lib/refcount.c:31
    Modules linked in:
    CPU: 0 PID: 21708 Comm: syz-executor.5 Not tainted 5.18.0-rc2-next-20220412-syzkaller #0
    Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/01/2011
    RIP: 0010:refcount_warn_saturate+0xbf/0x1e0 lib/refcount.c:31
    Code: 1d 14 b6 b2 09 31 ff 89 de e8 6d e9 89 fd 84 db 75 e0 e8 84 e5 89 fd 48 c7 c7 40 aa 26 8a c6 05 f4 b5 b2 09 01 e8 e5 81 2e 05 <0f> 0b eb c4 e8 68 e5 89 fd 0f b6 1d e3 b5 b2 09 31 ff 89 de e8 38
    RSP: 0018:ffffc900051af1b0 EFLAGS: 00010286
    RAX: 0000000000000000 RBX: 0000000000000000 RCX: 0000000000000000
    RDX: 0000000000040000 RSI: ffffffff8160a0c8 RDI: fffff52000a35e28
    RBP: 0000000000000004 R08: 0000000000000000 R09: 0000000000000000
    R10: ffffffff81604a9e R11: 0000000000000000 R12: 1ffff92000a35e3b
    R13: 00000000ffffffef R14: ffff8880211a0194 R15: ffff8880577d0a00
    FS:  00007f25d183e700(0000) GS:ffff8880b9c00000(0000) knlGS:0000000000000000
    CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    CR2: 00007f19c859c028 CR3: 0000000051009000 CR4: 00000000003506f0
    DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
    DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
    Call Trace:
     <TASK>
     __refcount_dec include/linux/refcount.h:344 [inline]
     refcount_dec include/linux/refcount.h:359 [inline]
     ref_tracker_free+0x535/0x6b0 lib/ref_tracker.c:118
     netns_tracker_free include/net/net_namespace.h:327 [inline]
     put_net_track include/net/net_namespace.h:341 [inline]
     tcf_exts_put_net include/net/pkt_cls.h:255 [inline]
     u32_destroy_key.isra.0+0xa7/0x2b0 net/sched/cls_u32.c:394
     u32_change+0xe01/0x3140 net/sched/cls_u32.c:909
     tc_new_tfilter+0x98d/0x2200 net/sched/cls_api.c:2148
     rtnetlink_rcv_msg+0x80d/0xb80 net/core/rtnetlink.c:6016
     netlink_rcv_skb+0x153/0x420 net/netlink/af_netlink.c:2495
     netlink_unicast_kernel net/netlink/af_netlink.c:1319 [inline]
     netlink_unicast+0x543/0x7f0 net/netlink/af_netlink.c:1345
     netlink_sendmsg+0x904/0xe00 net/netlink/af_netlink.c:1921
     sock_sendmsg_nosec net/socket.c:705 [inline]
     sock_sendmsg+0xcf/0x120 net/socket.c:725
     ____sys_sendmsg+0x6e2/0x800 net/socket.c:2413
     ___sys_sendmsg+0xf3/0x170 net/socket.c:2467
     __sys_sendmsg+0xe5/0x1b0 net/socket.c:2496
     do_syscall_x64 arch/x86/entry/common.c:50 [inline]
     do_syscall_64+0x35/0xb0 arch/x86/entry/common.c:80
     entry_SYSCALL_64_after_hwframe+0x44/0xae
    RIP: 0033:0x7f25d0689049
    Code: ff ff c3 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 40 00 48 89 f8 48 89 f7 48 89 d6 48 89 ca 4d 89 c2 4d 89 c8 4c 8b 4c 24 08 0f 05 <48> 3d 01 f0 ff ff 73 01 c3 48 c7 c1 b8 ff ff ff f7 d8 64 89 01 48
    RSP: 002b:00007f25d183e168 EFLAGS: 00000246 ORIG_RAX: 000000000000002e
    RAX: ffffffffffffffda RBX: 00007f25d079c030 RCX: 00007f25d0689049
    RDX: 0000000000000000 RSI: 0000000020000340 RDI: 0000000000000005
    RBP: 00007f25d06e308d R08: 0000000000000000 R09: 0000000000000000
    R10: 0000000000000000 R11: 0000000000000246 R12: 0000000000000000
    R13: 00007ffd0b752e3f R14: 00007f25d183e300 R15: 0000000000022000
     </TASK>
    
    Fixes: 35c55fc156d8 ("cls_u32: use tcf_exts_get_net() before call_rcu()")
    Signed-off-by: Eric Dumazet <edumazet@google.com>
    Reported-by: syzbot <syzkaller@googlegroups.com>
    Cc: Cong Wang <xiyou.wangcong@gmail.com>
    Cc: Jiri Pirko <jiri@resnulli.us>
    Acked-by: Jamal Hadi Salim <jhs@mojatatu.com>
    Signed-off-by: Jakub Kicinski <kuba@kernel.org>
    Diffstat
    -rw-r--r-- net/sched/cls_u32.c 16 
    1 files changed, 10 insertions, 6 deletions
    diff --git a/net/sched/cls_u32.c b/net/sched/cls_u32.c
    index cf5649292ee00..fcba6c43ba509 100644
    --- a/net/sched/cls_u32.c
    +++ b/net/sched/cls_u32.c
    @@ -386,14 +386,19 @@ static int u32_init(struct tcf_proto *tp)
      return 0;
     }
    
    -static int u32_destroy_key(struct tc_u_knode *n, bool free_pf)
    +static void __u32_destroy_key(struct tc_u_knode *n)
     {
      struct tc_u_hnode *ht = rtnl_dereference(n->ht_down);
    
      tcf_exts_destroy(&n->exts);
    - tcf_exts_put_net(&n->exts);
      if (ht && --ht->refcnt == 0)
       kfree(ht);
    + kfree(n);
    +}
    +
    +static void u32_destroy_key(struct tc_u_knode *n, bool free_pf)
    +{
    + tcf_exts_put_net(&n->exts);
     #ifdef CONFIG_CLS_U32_PERF
      if (free_pf)
       free_percpu(n->pf);
    @@ -402,8 +407,7 @@ static int u32_destroy_key(struct tc_u_knode *n, bool free_pf)
      if (free_pf)
       free_percpu(n->pcpu_success);
     #endif
    - kfree(n);
    - return 0;
    + __u32_destroy_key(n);
     }
    
     /* u32_delete_key_rcu should be called when free'ing a copied
    @@ -900,13 +904,13 @@ static int u32_change(struct net *net, struct sk_buff *in_skb,
             extack);
    
       if (err) {
    -   u32_destroy_key(new, false);
    +   __u32_destroy_key(new);
        return err;
       }
    
       err = u32_replace_hw_knode(tp, new, flags, extack);
       if (err) {
    -   u32_destroy_key(new, false);
    +   __u32_destroy_key(new);
        return err;
       }

### 问题引入

    
    
    commit 35c55fc156d85a396a975fc17636f560fc02fd65
    Author: Cong Wang <xiyou.wangcong@gmail.com>
    Date:   Mon Nov 6 13:47:30 2017 -0800
    
        cls_u32: use tcf_exts_get_net() before call_rcu()
    
        Hold netns refcnt before call_rcu() and release it after
        the tcf_exts_destroy() is done.
    
        Note, on ->destroy() path we have to respect the return value
        of tcf_exts_get_net(), on other paths it should always return
        true, so we don't need to care.
    
        Cc: Lucas Bates <lucasb@mojatatu.com>
        Cc: Jamal Hadi Salim <jhs@mojatatu.com>
        Cc: Jiri Pirko <jiri@resnulli.us>
        Signed-off-by: Cong Wang <xiyou.wangcong@gmail.com>
        Signed-off-by: David S. Miller <davem@davemloft.net>
    
    diff --git a/net/sched/cls_u32.c b/net/sched/cls_u32.c
    index dadd1b344497..b58eccb21f03 100644
    --- a/net/sched/cls_u32.c
    +++ b/net/sched/cls_u32.c
    @@ -399,6 +399,7 @@ static int u32_destroy_key(struct tcf_proto *tp, struct tc_u_knode *n,
                               bool free_pf)
     {
            tcf_exts_destroy(&n->exts);
    +       tcf_exts_put_net(&n->exts);
            if (n->ht_down)
                    n->ht_down->refcnt--;
     #ifdef CONFIG_CLS_U32_PERF
    @@ -476,6 +477,7 @@ static int u32_delete_key(struct tcf_proto *tp, struct tc_u_knode *key)
                                    RCU_INIT_POINTER(*kp, key->next);
    
                                    tcf_unbind_filter(tp, &key->res);
    +                               tcf_exts_get_net(&key->exts);
                                    call_rcu(&key->rcu, u32_delete_key_freepf_rcu);
                                    return 0;
                            }

所以，漏洞影响的时间范围2017年11月6日~2022年4月13日，持续4年半。

### 时间轴

时间 |  
---|---  
2021年7月27日 | 确认漏洞  
2021年10月 | 完成漏洞利用  
2022年4月12日 | syzbot打出类似漏洞  
2022年4月13日 | 社区修补  
2022年8月 | 参加国内比赛  
  
## 漏洞利用

漏洞利用的步骤分为：

1.通过信息泄漏，过地址随机化；

2.通过run_cmd提升权限。

### 信息泄漏

第一步：堆布局

![img](https://images.seebug.org/content/images/2022/12/26/1672039343000-10muosx.png-w331s)

1: 填充SLAB中空闲的net

将cache中的net专属SLAB的页全部吃掉，为了让新分配的net使用系统新分配出来的页。图中黄色区域代表堆喷的net objects，如图中的SLAB
1和SLAB 2。

2: 再从新分配的slab中创建victim net

图中红色区域所示。

3:再把victim所在的slab全部吃掉；

如图中的slab A和slab B，其中都用net对象将该8个页大小的slab填满；

第二步：mount net name space

为了后面通过该文件访问victim的引用。

    
    
    mount("/proc/self/ns/net", "./mynetns", "nsfs", MS_BIND, NULL)

第三步：把victim所在的页还到伙伴系统

通过u32_destroy_key将Victim的引用计数减少1

第四步：用户态mmap堆喷victim所在的物理页

将刚刚第三步还回系统的物理页，通过mmap分配得到。

第五步：构造任意地址读

在之前通过mount得到的文件上，调用ioctl(NS_GET_NSTYPE)，用户态就可以得到ns->ops->type的值，因为ops的值可控，所以就能实现任意地址读。

第六步：读取cpu_area_entry，绕过Kaslr

因为系统中cpu_area_entry的虚拟地址(0xfffffe0000000000)是固定的，
而该地址里含有一个被Kaslr后的内核代码段地址。所以可以计算出偏移，进而绕过Kaslr。

![img](https://images.seebug.org/content/images/2022/12/26/1672039344000-11afbnf.png-w331s)

fs/nsfs.c

    
    
    88 static long ns_ioctl(struct file *filp, unsigned int ioctl,
    189                         unsigned long arg)
    190 {        
    191         struct user_namespace *user_ns;
    192         struct ns_common *ns = get_proc_ns(file_inode(filp));
    193         uid_t __user *argp;
    194         uid_t uid;
    195 
    196         switch (ioctl) {
    197         case NS_GET_USERNS:
    198                 return open_related_ns(ns, ns_get_owner);
    199         case NS_GET_PARENT:
    200                 if (!ns->ops->get_parent)
    201                         return -EINVAL;
    202                 return open_related_ns(ns, ns->ops->get_parent);
    203         case NS_GET_NSTYPE:
    204                 return ns->ops->type;    <---/*现实任意地址读*/
    205         case NS_GET_OWNER_UID:
    206                 if (ns->ops->type != CLONE_NEWUSER)
    207                         return -EINVAL;
    208                 user_ns = container_of(ns, struct user_namespace, ns);
    209                 argp = (uid_t __user *) arg;
    210                 uid = from_kuid_munged(current_user_ns(), user_ns->owner);
    211                 return put_user(uid, argp);
    212         default:
    213                 return -ENOTTY;
    214         }
    215 }

include/linux/ns_common.h

    
    
      9 struct ns_common {
     10         atomic_long_t stashed;
     11         const struct proc_ns_operations *ops;    <---     12         unsigned int inum;
     13         refcount_t count;
     14 };

![img](https://images.seebug.org/content/images/2022/12/26/1672039344000-12srbnr.png-w331s)

### 通过run_cmd提权

在绕过地址随机化后，就可以进行下一步的提权。

第一步：读取victim net的地址

通过task_list读取中当前的task_struct结构，再读取task_struct上的nsproxy的地址，再读取nsproxy上的net指针来实现。

第二步：在用户态构造fake ops

将ops指针指向fake ops

![img](https://images.seebug.org/content/images/2022/12/26/1672039345000-13nghno.png-w331s)

第三步：劫持PC

    
    
    147 int open_related_ns(struct ns_common *ns,
    148                 |  struct ns_common *(*get_ns)(struct ns_common *ns))
    149 {
    150         struct path path = {};
    151         struct file *f;
    152         int err;
    153         int fd;
    154 
    155         fd = get_unused_fd_flags(O_CLOEXEC);
    156         if (fd < 0)
    157                 return fd;
    158 
    159         do {
    160                 struct ns_common *relative;
    161 
    162                 relative = get_ns(ns);
    163                 if (IS_ERR(relative)) {
    164                         put_unused_fd(fd);
    165                         return PTR_ERR(relative);
    166                 }
    167 
    168                 err = __ns_get_path(&path, relative);
    169         } while (err == -EAGAIN);
    170 
    171         if (err) {
    172                 put_unused_fd(fd);
    173                 return err;
    174         }
    175 
    176         f = dentry_open(&path, O_RDONLY, current_cred());
    177         path_put(&path);
    178         if (IS_ERR(f)) {
    179                 put_unused_fd(fd);
    180                 fd = PTR_ERR(f);
    181         } else
    182                 fd_install(fd, f);
    183 
    184         return fd;
    185 }

owner就是最后劫持的PC，而且ns的数据也可以控制，所以就可以执行run_cmd完成提权。

    
    
    1371 struct ns_common *ns_get_owner(struct ns_common *ns)
    1372 {
    1373         struct user_namespace *my_user_ns = current_user_ns();
    1374         struct user_namespace *owner, *p;
    1375 
    1376         /* See if the owner is in the current user namespace */
    1377         owner = p = ns->ops->owner(ns);    <---/*劫持PC*/
    1378         for (;;) {
    1379                 if (!p)
    1380                         return ERR_PTR(-EPERM);
    1381                 if (p == my_user_ns)
    1382                         break;
    1383                 p = p->parent;
    1384         }
    1385 
    1386         return &get_user_ns(owner)->ns;
    1387 }
    16 struct proc_ns_operations {
     17         const char *name;
     18         const char *real_ns_name;
     19         int type;
     20         struct ns_common *(*get)(struct task_struct *task);
     21         void (*put)(struct ns_common *ns);
     22         int (*install)(struct nsset *nsset, struct ns_common *ns);
     23         struct user_namespace *(*owner)(struct ns_common *ns);    <---     24         struct ns_common *(*get_parent)(struct ns_common *ns);
     25 } __randomize_layout;

![img](https://images.seebug.org/content/images/2022/12/26/1672039345000-14jtfvr.png-w331s)

## 参考链接

[1] <https://github.com/xdp-project/bpf-examples/tree/master/tc-basic-classifier>

[2]
<https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3db09e762dc79584a69c10d74a6b98f89a9979f8>

[3]
<https://syzkaller.appspot.com/bug?id=0ca897284a4e1bbc149ad96f15917e8b31a85d70>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2036/>

