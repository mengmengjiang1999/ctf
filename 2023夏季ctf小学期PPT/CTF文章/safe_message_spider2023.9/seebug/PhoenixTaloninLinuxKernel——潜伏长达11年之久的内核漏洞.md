作者: **启明星辰ADLab**

#### 1\. About“Phoenix Talon”

2017年5月9日，启明星辰ADLab发现 Linux 内核存在远程漏洞 “Phoenix Talon”（取凤凰爪四趾之意），涉及
CVE-2017-8890、CVE-2017-9075、CVE-2017-9076、CVE-2017-9077，可影响几乎所有 Linux kernel
2.5.69 ~Linux kernel 4.11 的内核版本、对应的发行版本以及相关国产系统。可导致远程 DOS，且在符合一定利用条件下可导致
RCE，包括传输层的 TCP、DCCP、SCTP 以及网络层的 IPv4 和 IPv6 协议均受影响。实际上该漏洞在 Linux 4.11-rc8
版本中已经被启明星辰ADLab发现，且后来的 Linux 4.11 stable 版同样存在此问题。经研究这些漏洞在 Linux
内核中至少已经潜伏了11年之久，影响极为深远。

启明星辰ADLab已第一时间将 “Phoenix Talon” 漏洞反馈给了 Linux 内核社区，漏洞上报后 Linux 社区在 Linux
4.12-rc1 中合并了修复该问题的补丁。

这些漏洞中以 CVE-2017-8890 最为严重（达到 Linux 内核漏洞两个评分标准的历史最高分，CVSS V2 评分达到满分 10.0，CVSS
V3 评分是历史最高分9.8，NVD 上搜索历史上涉及 Linux 内核漏洞这样评分的漏洞不超过 20 个），以下分析以该漏洞为例，引用官方描述如下：

“The inet_csk_clone_lock function in net/ipv4/inet_connection_sock.c in the
Linux kernel through 4.10.15 allows attackers to cause a denial of service
(double free) or possibly have unspecified other impact by leveraging use of
the accept system call.”

#### 2\. The Vulnerability

CVE-2017-8890 本身是一个 double free 的问题，使用 `setsockopt()` 函数中
`MCAST\_JOIN\_GROUP`选项，并调用 `accept()` 函数即可触发该漏洞。

接着先看看几个组播相关的数据结构：

    
    
    include/uapi/linux/in.h
    struct ip_mreq  {
            struct in_addr imr_multiaddr;   /* IP multicast address of group */
            struct in_addr imr_interface;   /* local IP address of interface */
    };

该结构体的两个成员分别用于指定所加入的多播组的组IP地址和所要加入组的本地接口IP地址。 `ip_setsockopt()` 实现了该功能，它通过调用
`ip_mc_join_group()` 把 socket 加入到多播组。

    
    
    include/net/inet_sock.h
    struct inet_sock {
        /* sk and pinet6 has to be the first two members of inet_sock */
        struct sock     sk;
    #if IS_ENABLED(CONFIG_IPV6)
        struct ipv6_pinfo   *pinet6;
    #endif
        /* Socket demultiplex comparisons on incoming packets. */
    #define inet_daddr      sk.__sk_common.skc_daddr
    #define inet_rcv_saddr  sk.__sk_common.skc_rcv_saddr   
    #define inet_dport      sk.__sk_common.skc_dport
    #define inet_num        sk.__sk_common.skc_num
    [...]
        __u8            tos;
        __u8            min_ttl;
        __u8            mc_ttl;                 
        __u8            pmtudisc;
        __u8            recverr:1,
                    is_icsk:1,
                    freebind:1,
                    hdrincl:1,                   
                    mc_loop:1,                   
    [...]
        int         uc_index;                     
        int         mc_index;                     
        __be32          mc_addr;                 
        struct ip_mc_socklist __rcu *mc_list;     
        struct inet_cork_full   cork;
    };

其中 `sk.__sk_common.skc_rcv_saddr`
对于组播而言，只接收该地址发来的组播数据，对于单播而言，只从该地址所代表的网卡接收数据；`mc_ttl` 为组播的 `ttl` ；`mc_loop`
表示组播是否发向回路；`mc_index` 表示组播使用的本地设备接口的索引；`mc_addr` 表示组播源地址；`mc_list` 为组播列表。

    
    
    include/linux/igmp.h
    /* ip_mc_socklist is real list now. Speed is not argument;
       this list never used in fast path code
     */
    struct ip_mc_socklist {
            struct ip_mc_socklist __rcu *next_rcu;
            struct ip_mreqn         multi;
            unsigned int            sfmode;         /* MCAST_{INCLUDE,EXCLUDE} */
            struct ip_sf_socklist __rcu     *sflist;
            struct rcu_head         rcu;
    };

`next_rcu` 指向链表的下一个节点；`multi` 表示组信息，即在哪一个本地接口上，加入到哪一个多播组；`sfmode` 是过滤模式，取值为
`MCAST_INCLUDE` 或 `MCAST_EXCLUDE` ，分别表示只接收 `sflist` 所列出的那些源的多播数据报和不接收 `sflist`
所列出的那些源的多播数据报；`sflist` 是源列表。

下面分别从该漏洞内存分配的关键代码及二次释放的关键代码进行分析。

  * The Allocate

内存分配调用链：

1.用户态

    
    
    setsockopt() -> 
    
                …

2.内核态:

    
    
    -> entry_SYSCALL_64_fastpath() -> SyS_setsockopt() -> SYSC_setsockopt() -> sock_common_setsockopt() -> tcp_setsockopt() -> ip_setsockopt() -> do_ip_setsockopt() -> do_ip_setsockopt() -> ip_mc_join_group() -> sock_kmalloc() -> [...]

使用 `setsockopt()` 函数中的 `MCAST_JOIN_GROUP` 选项。

**net/socket.c**

    
    
    1777 SYSCALL_DEFINE5(setsockopt, int, fd, int, level, int, optname,
    1778                 char __user *, optval, int, optlen)
    1779 {
    1780         int err, fput_needed;
    1781         struct socket *sock;
    1782
    1783         if (optlen < 0)
    1784                 return -EINVAL;
    1785
    1786         sock = sockfd_lookup_light(fd, &err, &fput_needed);
    1787         if (sock != NULL) {
    1788                 err = security_socket_setsockopt(sock, level, optname);
    1789                 if (err)
    1790                         goto out_put;
    1791
    1792                 if (level == SOL_SOCKET)
    1793                         err =
    1794                             sock_setsockopt(sock, level, optname, optval,
    1795                                             optlen);
    1796                 else
    1797                         err =
    1798                             sock->ops->setsockopt(sock, level, optname, optval,
    1799                                                   optlen);
    1800 out_put:
    1801                 fput_light(sock->file, fput_needed);
    1802         }
    1803         return err;
    1804 }

进入内核调用 `SyS_setsockopt()` 函数，level 设置的不为 SOL_SOCKET 即可，一般设置为 SOL_IP ，在1798
行处被调用。紧接着调用 `sock_common_setsockopt()` 函数。

**net/ipv4/ip_sockglue.c**

    
    
    1256 int ip_setsockopt(struct sock *sk, int level,
    1257                 int optname, char __user *optval, unsigned int optlen)
    1258 {
    1259         int err;
    1260
    1261         if (level != SOL_IP)
    1262                 return -ENOPROTOOPT;
    1263
    1264         err = do_ip_setsockopt(sk, level, optname, optval, optlen);
    1265 #ifdef CONFIG_NETFILTER
    1266         /* we need to exclude all possible ENOPROTOOPTs except default case */
    1267         if (err == -ENOPROTOOPT && optname != IP_HDRINCL &&
    1268                         optname != IP_IPSEC_POLICY &&
    1269                         optname != IP_XFRM_POLICY &&
    1270                         !ip_mroute_opt(optname)) {
    1271                 lock_sock(sk);
    1272                 err = nf_setsockopt(sk, PF_INET, optname, optval, optlen);
    1273                 release_sock(sk);
    1274         }
    1275 #endif
    1276         return err;
    1277 }

然后进入 `ip_setsockopt()` 函数，调用 `do_ip_setsockopt()` 函数（1264行代码）。

**net/ipv4/ip_sockglue.c**

    
    
    599 static int do_ip_setsockopt(struct sock *sk, int level,
    600                             int optname, char __user *optval, unsigned int optlen)
    601 {
    602         struct inet_sock *inet = inet_sk(sk);
    603         struct net *net = sock_net(sk);
    604         int val = 0, err;
    605         bool needs_rtnl = setsockopt_needs_rtnl(optname);
    606
    607         switch (optname) {
          [...]
    1009         case MCAST_JOIN_GROUP:
    1011         {
    1012                 struct group_req greq;
    1013                 struct sockaddr_in *psin;
    1014                 struct ip_mreqn mreq;
    1015
    1016                 if (optlen < sizeof(struct group_req))
    1017                         goto e_inval;
    1018                 err = -EFAULT;
    1019                 if (copy_from_user(&greq, optval, sizeof(greq)))
    1020                         break;
    1021                 psin = (struct sockaddr_in *)&greq.gr_group;
    1022                 if (psin->sin_family != AF_INET)
    1023                         goto e_inval;
    1024                 memset(&mreq, 0, sizeof(mreq));
    1025                 mreq.imr_multiaddr = psin->sin_addr;
    1026                 mreq.imr_ifindex = greq.gr_interface;
    1027
    1028                 if (optname == MCAST_JOIN_GROUP)
    1029                         err = ip_mc_join_group(sk, &mreq);
    1030                 else
    1031                         err = ip_mc_leave_group(sk, &mreq);
    1032                 break;
    1033         }
    [...]

代码 1019～1021 行调用 `copy_from_user()` 将用户态的数据拷贝到内核态。之前已经将 option 设置为
`MCAST_JOIN_GROUP`，紧接着调用 `ip_mc_join_group()` 函数：

**net/ipv4/igmp.c**

    
    
    2094 int ip_mc_join_group(struct sock *sk, struct ip_mreqn *imr)
    2095 {
    2096         __be32 addr = imr->imr_multiaddr.s_addr;
    2097         struct ip_mc_socklist *iml, *i;
    2098         struct in_device *in_dev;
    2099         struct inet_sock *inet = inet_sk(sk);
    2100         struct net *net = sock_net(sk);
    2101         int ifindex;
    2102         int count = 0;
    2103         int err;
    2104
    2105         ASSERT_RTNL();
    2106
    2107         if (!ipv4_is_multicast(addr))
    2108                 return -EINVAL;
    2109
    2110         in_dev = ip_mc_find_dev(net, imr);
    2111
    2112         if (!in_dev) {
    2113                 err = -ENODEV;
    2114                 goto done;
    2115         }
    2116
    2117         err = -EADDRINUSE;
    2118         ifindex = imr->imr_ifindex;
    2119         for_each_pmc_rtnl(inet, i) {
    2120                 if (i->multi.imr_multiaddr.s_addr == addr &&
    2121                     i->multi.imr_ifindex == ifindex)
    2122                         goto done;
    2123                 count++;
    2124         }
    2125         err = -ENOBUFS;
    2126         if (count >= net->ipv4.sysctl_igmp_max_memberships)
    2127                 goto done;
    2128         iml = sock_kmalloc(sk, sizeof(*iml), GFP_KERNEL);
    2129         if (!iml)
    2130                 goto done;
    2131
    2132         memcpy(&iml->multi, imr, sizeof(*imr));
    2133         iml->next_rcu = inet->mc_list;
    2134         iml->sflist = NULL;
    2135         iml->sfmode = MCAST_EXCLUDE;
    2136         rcu_assign_pointer(inet->mc_list, iml);
    2137         ip_mc_inc_group(in_dev, addr);
    2138         err = 0;
    2139 done:
    2140         return err;
    2141 }

代码2128行 `sock_kmalloc()` 进行了内存分配。

  * The first free

在内核里无时无刻都在产生软中断，而此次漏洞涉及的软中断是由 `accept()` 系统调用引起的，由于该函数本身作用于进程上下文，并不会产生软中断。但是调用
`accept()` 时，会在内核中诱发某种软中断产生，该软中断会调用 `rcu_process_callbacks()` 函数：

**kernel/rcu/tree.c**

    
    
    3118 static __latent_entropy void rcu_process_callbacks(struct softirq_action *unused)
    3119 {
    3120         struct rcu_state *rsp;
    3121
    3122         if (cpu_is_offline(smp_processor_id()))
    3123                 return;
    3124         trace_rcu_utilization(TPS("Start RCU core"));
    3125         for_each_rcu_flavor(rsp)
    3126                 __rcu_process_callbacks(rsp);
    3127         trace_rcu_utilization(TPS("End RCU core"));
    3128 }

`__rcu_process_callbacks` 调用 `rcu_do_batch()` 函数，如下：

**kernel/rcu/tree.c**

    
    
    2840 static void rcu_do_batch(struct rcu_state *rsp, struct rcu_data *rdp)
    2841 {
    2842         unsigned long flags;
    2843         struct rcu_head *next, *list, **tail;
    2844         long bl, count, count_lazy;
    2845         int i;
    2846
    2847         /* If no callbacks are ready, just return. */
    2848         if (!cpu_has_callbacks_ready_to_invoke(rdp)) {
    2849                 trace_rcu_batch_start(rsp->name, rdp->qlen_lazy, rdp->qlen, 0);
    2850                 trace_rcu_batch_end(rsp->name, 0, !!READ_ONCE(rdp->nxtlist),
    2851                                     need_resched(), is_idle_task(current),
    2852                                     rcu_is_callbacks_kthread());
    2853                 return;
    2854         }
    [...]
    2874         count = count_lazy = 0;
    2875         while (list) {
    2876                 next = list->next;
    2877                 prefetch(next);
    2878                 debug_rcu_head_unqueue(list);
    2879                 if (__rcu_reclaim(rsp->name, list))
    2880                         count_lazy++;
    2881                 list = next;
    2882                 /* Stop only if limit reached and CPU has something to do. */
    2883                 if (++count >= bl &&
    2884                     (need_resched() ||
    2885                      (!is_idle_task(current) && !rcu_is_callbacks_kthread())))
    2886                         break;
    2887         }
    [...]

注意代码中第2879行，函数 `__rcu_reclaim()` 实现如下：

**kernel/rcu/rcu.h**

    
    
    106 static inline bool __rcu_reclaim(const char *rn, struct rcu_head *head)
    107 {
    108         unsigned long offset = (unsigned long)head->func;
    109
    110         rcu_lock_acquire(&rcu_callback_map);
    111         if (__is_kfree_rcu_offset(offset)) {
    112                 RCU_TRACE(trace_rcu_invoke_kfree_callback(rn, head, offset));
    113                 kfree((void *)head - offset);
    114                 rcu_lock_release(&rcu_callback_map);
    115                 return true;
    116         } else {
    117                 RCU_TRACE(trace_rcu_invoke_callback(rn, head));
    118                 head->func(head);
    119                 rcu_lock_release(&rcu_callback_map);
    120                 return false;
    121         }
    122 }

在113行调用 `kfree()` 进行了第一次释放。

  * The second free

当断开 TCP 连接时，内核通过 `sock\_close()` 函数直接调用 `sock\_release()` 来实现断开功能，该函数会清空
ops，更新全局 socket 数目，更新 inode 引用计数。随后进入到 `inet\_release()` 函数调用 `tcp\_close()`
函数来最终关闭 sock。

**net/ipv4/af_inet.c**

    
    
    403 int inet_release(struct socket *sock)
    404 {
    405         struct sock *sk = sock->sk;
    406
    407         if (sk) {
    408                 long timeout;
    409
    410                 /* Applications forget to leave groups before exiting */
    411                 ip_mc_drop_socket(sk);
    412
    413                 /* If linger is set, we don't return until the close
    414                  * is complete.  Otherwise we return immediately. The
    415                  * actually closing is done the same either way.
    416                  *
    417                  * If the close is due to the process exiting, we never
    418                  * linger..
    419                  */
    420                 timeout = 0;
    421                 if (sock_flag(sk, SOCK_LINGER) &&
    422                     !(current->flags & PF_EXITING))
    423                         timeout = sk->sk_lingertime;
    424                 sock->sk = NULL;
    425                 sk->sk_prot->close(sk, timeout);
    426         }
    427         return 0;
    428 }

用户程序断开 TCP 连接时，内核里使用 `ip\_mc\_drop\_socket()` 函数进行回收。

**net/ipv4/igmp.c**

    
    
    2592 void ip_mc_drop_socket(struct sock *sk)
    2593 {
    2594         struct inet_sock *inet = inet_sk(sk);
    2595         struct ip_mc_socklist *iml;
    2596         struct net *net = sock_net(sk);
    2597
    2598         if (!inet->mc_list)
    2599                 return;
    2600
    2601         rtnl_lock();
    2602         while ((iml = rtnl_dereference(inet->mc_list)) != NULL) {
    2603                 struct in_device *in_dev;
    2604
    2605                 inet->mc_list = iml->next_rcu;
    2606                 in_dev = inetdev_by_index(net, iml->multi.imr_ifindex);
    2607                 (void) ip_mc_leave_src(sk, iml, in_dev);
    2608                 if (in_dev)
    2609                         ip_mc_dec_group(in_dev, iml->multi.imr_multiaddr.s_addr);
    2610                 /* decrease mem now to avoid the memleak warning */
    2611                 atomic_sub(sizeof(*iml), &sk->sk_omem_alloc);
    2612                 kfree_rcu(iml, rcu);
    2613         }
    2614         rtnl_unlock();
    2615 }

代码2612行调用 `kfree_rcu()` 进行第二次释放。

#### 3.Affected

  * 受影响的内核版本

经研究，理论上 Linux kernel 2.5.69 ~ Linux kernel 4.11 的所有版本都受 “Phoenix Talon”
影响，且经开源社区验证 “Phoenix Talon” 漏洞影响的 Linux 内核版本部分列表如下：

![](https://images.seebug.org/content/images/2017/06/----_20170616095830.png-w331s)

经启明星辰ADLab测试 Linux kernel 4.11 亦受影响。

  * 受影响的发行版本

经开源社区验证部分受影响发行版本（不完整列表）如下：

Red Hat Enterprise MRG 2 Red Hat Enterprise Linux 7 Red Hat Enterprise Linux 6
Red Hat Enterprise Linux 5 SUSE Linux Enterprise Desktop 12 SP1 SUSE Linux
Enterprise Desktop 12 SP2 SUSE Linux Enterprise Server 11 SP3 LTSS SUSE Linux
Enterprise Server 11 SP4 SUSE Linux Enterprise Server 12 GA SUSE Linux
Enterprise Server 12 SP1 SUSE Linux Enterprise Server 12 SP2 SUSE Linux
Enterprise Server for SAP 11 SP3 SUSE Linux Enterprise Server for SAP 11 SP4
SUSE Linux Enterprise Server for SAP 12 GA SUSE Linux Enterprise Server for
SAP 12 SP1 SUSE Linux Enterprise Server for SAP 12 SP2

另外，启明星辰ADLab对下列的部分发行版本做了测试，确认均受 “Phoenix Talon” 漏洞影响：

Ubuntu 14.04 LTS (Trusty Tahr) Ubuntu 16.04 LTS (Xenial Xerus) Ubuntu 16.10
(Yakkety Yak) Ubuntu 17.04 (Zesty Zapus) Ubuntu 17.10 (Artful Aardvark)

#### 4\. Solution

  1. 官方已经发布了修复该问题的补丁，可通过升级Linux内核修复“Phoenix Talon”相关漏洞。
  2. 使用 Grsecurity/PaX 对内核加固。

#### 5\. Timeline

May 09 - Report sent to Linux Kernel Community May 09 - Linux Kernel Community
confirmed May 09 - Linux Kernel Community patched in linux upstream May 10 -Assgined CVE number

“Phoenix Talon”在 Linux 内核中潜伏长达11年之久，影响范围非常广泛（以上只是官方以及我们测试的部分结果，即使这些也足够看出
“Phoenix Talon” 波及之深之广），启明星辰ADLab提醒广大用户尽快采取相应的修复措施，避免引发漏洞相关的网络安全事件。

**Reference:**  
[1] https://people.canonical.com/~ubuntu-security/cve/2017/CVE-2017-8890.html  
[2] https://security-tracker.debian.org/tracker/CVE-2017-8890  
[3] https://www.suse.com/security/cve/CVE-2017-8890/  
[4] https://bugzilla.redhat.com/show_bug.cgi?id=1450973  
[5] https://bugzilla.suse.com/show_bug.cgi?id=1038544  
[6] https://www.mail-archive.com/netdev@vger.kernel.org/msg167626.html  
[7] https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-8890  
[8] https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-9075  
[9] https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-9076  
[10] https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-9077  
[11]
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=657831ffc38e30092a2d5f03d385d710eb88b09a  
[12] http://www.securityfocus.com/bid/98562/info  
[13] http://www.openwall.com/lists/oss-security/2017/05/30/24  
[14] https://www.kernel.org  
[15] Linux Kernel Documentation

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近300个，持续保持亚洲领先并确立了其在国际网络安全领域的核心地位。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/327/>

