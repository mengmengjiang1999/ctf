最近在做主机侧网络连接相关的调研，发现通过 linux
自带的`netlink`能实时获取网络连接五元组信息，可以用于网络活动可视化、异常连接检测、安全策略优化以及审计等功能，但网络上找到的相关文章不多，因此在此分析下`netlink`实时获取网络连接信息的原理。

# netlink 是什么

`netlink`是什么？官方文档是这样描述的：

> Netlink is used to transfer information between the kernel and user-space
> processes. It consists of a standard sockets-based interface for user space
> processes and an internal kernel API for kernel modules.  
> Netlink用于在内核和用户空间进程之间传输信息。它由一个面向用户空间进程的标准套接字接口和一个面向内核模块的内部内核API组成。  
> https://man7.org/linux/man-pages/man7/netlink.7.html

简单来讲`netlink`实现了一套用户态和内核态通信的机制，通过`netlink`能和很多内核模块通信，例如`ss`命令通过 netlink
更快的获取网络信息、hids通过`netlink`获取进程创建信息、`iptables`通过`netlink`配置网络规则等。

关于如何使用`netlink`官方提供了如下使用样例：

    
    
    ...
    fd = socket(AF_NETLINK, SOCK_RAW, protocol);
    bind(fd, (struct sockaddr *) &sa, sizeof(sa));
    ...
    sendmsg(fd, &msg, 0);
    ...
    len = recvmsg(fd, &msg, 0);
    ...
    

`socket()`的参数`protocol`指定了创建的套接字对应的`netlink`协议，不同的协议可以和不同的内核模块通信，`netlink`支持的协议可以在`include/linux/netlink.h`文件中看到：

    
    
    // include/linux/netlink.h
    #define NETLINK_INET_DIAG	4	/* INET socket monitoring*/
    #define NETLINK_AUDIT		9	/* auditing */
    #define NETLINK_CONNECTOR	11
    #define NETLINK_NETFILTER	12	/* netfilter subsystem */
    

这里列举了几个安全常用的协议，通过`NETLINK_INET_DIAG`可以获取网络连接数据，通过`NETLINK_AUDIT`可以获取内核`auditd`数据，通过`NETLINK_CONNECTOR`可以获取进程创建数据。而`NETLINK_NETFILTER`正是本文后续要介绍的能实时获取网络连接信息的协议。

# netlink 初始化

为什么`socket()`指定`AF_NETLINK`之后就能和`netlink`通信了? 需要结合`netlink`的初始化过程来看。

    
    
    // net/netlink/af_netlink.c
    core_initcall(netlink_proto_init);
    

`core_initcall`将`netlink_proto_init`注册为一个核心初始化函数，并在内核启动时自动调用，也就是说`netlink`内核模块是默认开启的。我们再来看看`netlink_proto_init`做了什么：

    
    
    // net/netlink/af_netlink.c
    static int __init netlink_proto_init(void)
    {
        ...
        nl_table = kcalloc(MAX_LINKS, sizeof(*nl_table), GFP_KERNEL);
        ...
    	sock_register(&netlink_family_ops);
    }
    
    struct netlink_table {
    	struct nl_pid_hash hash; // 存储sk_node 单播时会用
    	struct hlist_head mc_list; // 存储sk_bind_node 广播时会用
    	unsigned long *listeners; // 记录当前加入广播组的客户端
    	unsigned int nl_nonroot;
    	unsigned int groups; // 广播上限
    	struct mutex *cb_mutex;
    	struct module *module;
    	int registered; // 当前netlink协议是否注册
    };
    static struct netlink_table *nl_table;
    

`netlink_proto_init`过程需要关注两点：`nl_table`和`sock_register`：`nl_table`记录了`netlink`协议的配置和状态，我们后续讲到注册`netlink`时会再用到`nl_table`；`sock_register`则是将`netlink_family_ops`加入`net_families`中：

    
    
    // net/netlink/af_netlink.c
    static struct net_proto_family netlink_family_ops = {
    	.family = PF_NETLINK,
    	.create = netlink_create,
    	.owner	= THIS_MODULE,	/* for consistency 8) */
    };
    
    // net/socket.c
    int sock_register(const struct net_proto_family *ops)
    {
        ...
    	net_families[ops->family] = ops;
        ...
    }
    
    static const struct net_proto_family *net_families[NPROTO] __read_mostly;
    struct net_proto_family {
    	int		family;
    	int		(*create)(struct net *net, struct socket *sock, int protocol);
    	struct module	*owner;
    };
    

`net_families`是`net_proto_family`类型的数据，此时`net_families[PF_NETLINK]->create ==
netlink_create`，到此也就完成了模块初始化过程。

系统调用`socket`时会调用`net_families`中的`netlink_create`：

    
    
    // net/socket.c
    SYSCALL_DEFINE3(socket, int, family, int, type, int, protocol)
    {
        ...
    	retval = sock_create(family, type, protocol, &sock);
    	...
    }
    
    int sock_create(int family, int type, int protocol, struct socket **res)
    {
    	return __sock_create(current->nsproxy->net_ns, family, type, protocol, res, 0);
    }
    
    static int __sock_create(struct net *net, ...)
    {
        ...
    	pf = rcu_dereference(net_families[family]);
    	err = pf->create(net, sock, protocol);
        ...
    }
    

可以看到系统调用`socket`最终会调用`net_families[family]->create`，而官方样例中我们是这样`fd =
socket(AF_NETLINK, SOCK_RAW, netlink_family)`创建`netlink socket
`的，`include/linux/socket.h`文件中定义`#define PF_NETLINK
AF_NETLINK`，因此`net_families[family]->create`调用的正是`netlink_create`！我们再来看看`netlink_create`做了什么：

    
    
    // net/netlink/af_netlink.c
    static int netlink_create(struct net *net, struct socket *sock, int protocol)
    {
    	...
    	err = __netlink_create(net, sock, cb_mutex, protocol);
        ...
    }
    
    static int __netlink_create(struct net *net, ...)
    {
    	...
    	sock->ops = &netlink_ops;
        // 将sk与netlink_proto结构体关联
        sk = sk_alloc(net, PF_NETLINK, GFP_KERNEL, &netlink_proto);
    	...
    }
    
    // net/netlink/af_netlink.c
    // netlink_socket 对应的 ops 函数
    static const struct proto_ops netlink_ops = {
    	...
    	.bind =		netlink_bind,
        .setsockopt =	netlink_setsockopt,
    	.sendmsg =	netlink_sendmsg,
    	.recvmsg =	netlink_recvmsg,
        ...
    };
    // netlink类型socket的sock结构体
    struct netlink_sock {
    	struct sock		sk;
    	u32			pid;
    	u32			dst_pid;
    	u32			dst_group;
    	u32			flags;
    	u32			subscriptions;
    	u32			ngroups;
    	unsigned long		*groups;
    	unsigned long		state;
    	wait_queue_head_t	wait;
    	struct netlink_callback	*cb;
    	struct mutex		*cb_mutex;
    	struct mutex		cb_def_mutex;
    	void			(*netlink_rcv)(struct sk_buff *skb);
    	struct module		*module;
    };
    

可以看到`netlink_create`进行了`sock->ops =
&netlink_ops`赋值操作，也就是说我们可以通过`socket(AF_NETLINK, SOCK_RAW,
netlink_family)`获得一个`socket`,此时该`socket`对应的`bind sendmsg
recvmsg`等函数都被替换成了`netlink`协议的对应函数。同时创建了`socket->sk`与`netlink_sock`结构体关联，`netlink_sock`中会存放`netlink`通信过程中需要的`dst_pid、dst_group`等数据。  
![image](https://image.3001.net/images/20230530/1685435550_6475b49e80487dfc45466.png!small)

# NETLINK_NETFILTER 初始化

各个内核模块注册`netlink`协议的流程基本相同，本节以后续要分析的`NETLINK_NETFILTER`协议为例分析一下注册`netlink`协议的流程：

    
    
    // net/netfilter/nfnetlink.c
    static int __init nfnetlink_init(void)
    {
        ...
    	nfnl = netlink_kernel_create(&init_net, NETLINK_NETFILTER, NFNLGRP_MAX,
    				     nfnetlink_rcv, NULL, THIS_MODULE);
        ...
    }
    
    module_init(nfnetlink_init);
    

可以看到`netfilter`并不是默认开启的内核模块，当该模块被加载时会调用`netlink_kernel_create`

    
    
    // net/netfilter/nfnetlink.c
    struct sock *
    netlink_kernel_create(struct net *net, int unit, unsigned int groups,
    		      void (*input)(struct sk_buff *skb),...)
    {
    	...
    	struct socket *sock;
    	struct sock *sk;
    	unsigned long *listeners = NULL;
        // 为内核模块创建socket
    	sock_create_lite(PF_NETLINK, SOCK_DGRAM, unit, &sock)
    	__netlink_create(&init_net, sock, cb_mutex, unit)
    	sk = sock->sk;
    	listeners = kzalloc(NLGRPSZ(groups) + sizeof(struct listeners_rcu_head),
    			    GFP_KERNEL);
        // 设置回调函数 netlink_rcv 为 nfnetlink_rcv
    	if (input)
    		nlk_sk(sk)->netlink_rcv = input;
        // 更新协议状态
        nl_table[unit].groups = groups;
        nl_table[unit].listeners = listeners;
        nl_table[unit].cb_mutex = cb_mutex;
        nl_table[unit].module = module;
        nl_table[unit].registered = 1;
    	...
    }
    

`netlink_kernel_create`返回给`netfilter`内核模块一个`socket`，并切设置了该`socket`的`netlink_rcv`函数为`nfnetlink_rcv`，最后还更新了`nl_table`设置`NETLINK_NETFILTER`协议为激活状态。

![image](https://image.3001.net/images/20230530/1685435569_6475b4b1ce9f1f4b9f882.png!small)

# 发送接收netlink消息

用户态可以通过`send`向内核态发送`netlink`消息，通过分析这个过程我们可以看到`nfnetlink_rcv`和`nl_table`的作用：

    
    
    // net/socket.c
    SYSCALL_DEFINE4(send, int, fd, ...)
    {
    	return sys_sendto(fd, buff, len, flags, NULL, 0);
    }
    
    SYSCALL_DEFINE6(sendto, int, fd,...)
    {
    	...
    	err = sock_sendmsg(sock, &msg, len);
    	...
    }
    
    int sock_sendmsg(struct socket *sock, struct msghdr *msg, size_t size)
    {
    	...
    	ret = __sock_sendmsg(&iocb, sock, msg, size);
    	...
    }
    
    static inline int __sock_sendmsg(struct kiocb *iocb,...)
    {
    	...
    	return sock->ops->sendmsg(iocb, sock, msg, size);
    }
    

`send`最终调用的是`sock->ops->sendmsg`也就是`netlink_sendmsg`

    
    
    // net/netlink/af_netlink.c
    static int netlink_sendmsg(struct kiocb *kiocb,...)
    {
        ...
        NETLINK_CB(skb).dst_group = dst_group;
        if (dst_group) {
    		atomic_inc(&skb->users);
    		netlink_broadcast(sk, skb, dst_pid, dst_group, GFP_KERNEL);
    	}
    	err = netlink_unicast(sk, skb, dst_pid, msg->msg_flags&MSG_DONTWAIT);
        ...
    }
    

而`netlink_sendmsg`会根据`dst_group`选择执行`netlink_broadcast`和`netlink_unicast`，`netlink`正是用这两个函数将数据单播、广播给发送给指定的进程或内核模块。用户态发送给内核进程的消息自然用的是单播`netlink_unicast`:

    
    
    // net/netlink/af_netlink.c
    int netlink_unicast(struct sock *ssk, ...)
    {
    	...
    	if (netlink_is_kernel(sk))
    		return netlink_unicast_kernel(sk, skb);
    	err = netlink_attachskb(sk, skb, &timeo, ssk);
    	return netlink_sendskb(sk, skb);
    }
    // 发送消息到内核
    static inline int netlink_unicast_kernel(struct sock *sk, struct sk_buff *skb)
    {
    	...
        struct netlink_sock *nlk = nlk_sk(sk);
    	nlk->netlink_rcv(skb);
        ...
    }
    

可以看到`netlink_unicast`单播时会通过`netlink_is_kernel`判断消息是否要发往内核，如果消息需要发送到内核则会调用内核模块初始化时注册的`input`函数`nfnetlink_rcv`，至此完成从用户态发送消息到指定内核模块的流程。

内核发送数据到用户态同样需要借助于`netlink_unicast netlink_broadcast`函数：

    
    
    // net/netlink/af_netlink.c
    int netlink_sendskb(struct sock *sk, struct sk_buff *skb)
    {
    	...
    	skb_queue_tail(&sk->sk_receive_queue, skb);
    	...
    }
    
    static inline int netlink_broadcast_deliver(struct sock *sk,
    					    struct sk_buff *skb)
    {
        ...
    	skb_queue_tail(&sk->sk_receive_queue, skb);
    	...
    }
    

`netlink_unicast
`和`netlink_broadcast`最终都会调用`skb_queue_tail`将数据写入`sk->sk_receive_queue `队列中。

用户态则可以使用`recvmsg`接收来自内核的消息：

    
    
    // net/socket.c
    SYSCALL_DEFINE3(recvmsg, int, fd, struct msghdr __user *, msg,
    		unsigned int, flags)
    {
        ...
        err = sock_recvmsg(sock, &msg_sys, total_len, flags);
        ...
    }
    
    int sock_recvmsg(struct socket *sock, struct msghdr *msg,
    		 size_t size, int flags)
    {
    	...
    	ret = __sock_recvmsg(&iocb, sock, msg, size, flags);
        ...
    }
    
    static inline int __sock_recvmsg(struct kiocb *iocb, ...)
    {
    	...
    	return sock->ops->recvmsg(iocb, sock, msg, size, flags);
    }
    

`recvmsg`最终调用的还是`sock->ops->recvmsg`即`netlink_rcvmsg`:

    
    
    // net/netlink/af_netlink.c
    static int netlink_recvmsg(struct kiocb *kiocb,...)
    {
        ...
        struct sock *sk = sock->sk;
        skb = skb_recv_datagram(sk, flags, noblock, &err);
        err = skb_copy_datagram_iovec(skb, 0, msg->msg_iov, copied);
        ...
    }
    // net/core/datagram.c
    struct sk_buff *__skb_recv_datagram(struct sock *sk, ...)
    {
        ...
        skb = skb_peek(&sk->sk_receive_queue);
        ...
    }
    

接收`netlink`消息的流程非常简单，就是从`socket->sk->sk_receive_queue`中拷贝消息到指定的`msghdr->msg_iov`中。

![image](https://image.3001.net/images/20230530/1685435586_6475b4c2cd87a669ea8c8.png!small)

# NETLINK_NETFILTER 实时监控网络连接

`netfilter`是一个内核框架，用于在 Linux
系统中进行网络数据包过滤、修改和网络地址转换等操作。为了实现这些功能`netfilter`在一些位置埋了钩子，例如在 IP
层的入口函数`ip_rcv`中，`netfilter`通过`NF_HOOK`处理数据包：

    
    
    // net/ipv4/ip_input.c
    int ip_rcv(struct sk_buff *skb, struct net_device *dev, struct packet_type *pt, struct net_device *orig_dev)
    {
    	...
    	return NF_HOOK(PF_INET, NF_INET_PRE_ROUTING, skb, dev, NULL,
    		       ip_rcv_finish);
    }
    // net/netfilter/core.c
    int nf_hook_slow(u_int8_t pf, unsigned int hook, struct sk_buff *skb,...)
    {
        ...
    	elem = &nf_hooks[pf][hook];
    	verdict = nf_iterate(&nf_hooks[pf][hook], skb, hook, indev,
    			     outdev, &elem, okfn, hook_thresh);
        ...
    }
    
    unsigned int nf_iterate(struct list_head *head,...)
    {
    	...
    	list_for_each_continue_rcu(*i, head) {
    		struct nf_hook_ops *elem = (struct nf_hook_ops *)*i;
    		verdict = elem->hook(hook, skb, indev, outdev, okfn);
        }
    }
    

可以看到`NF_HOOK`最终会进入`nf_iterate`遍历执行`nf_hooks[pf][hook]`中的`hook`，我们来看一下`nf_hooks`是怎么被初始化的：

    
    
    // net/ipv4/netfilter/nf_conntrack_l3proto_ipv4.c
    static int __init nf_conntrack_l3proto_ipv4_init(void)
    {
        ...
        ret = nf_register_hooks(ipv4_conntrack_ops,ARRAY_SIZE(ipv4_conntrack_ops));
        ...
    }
    // net/netfilter/core.c
    int nf_register_hooks(struct nf_hook_ops *reg, unsigned int n)
    {
    	...
    	for (i = 0; i < n; i++) {
    		err = nf_register_hook(&ampreg[i]);
    	}
        ...
    }
    

`nf_conntrack_l3proto_ipv4`内核模块实现了IPV4的连接追踪功能，可以看到其将`ipv4_conntrack_ops`注册到`nf_hooks`中，再来看一下`ipv4_conntrack_ops`做了什么：

    
    
    // net/ipv4/netfilter/nf_conntrack_l3proto_ipv4.c
    static struct nf_hook_ops ipv4_conntrack_ops[] __read_mostly = {
    	...
    	{
    		.hook		= ipv4_confirm,
    		.owner		= THIS_MODULE,
    		.pf		= NFPROTO_IPV4,
    		.hooknum	= NF_INET_LOCAL_IN,
    		.priority	= NF_IP_PRI_CONNTRACK_CONFIRM,
    	},
    };
    
    static unsigned int ipv4_confirm(unsigned int hooknum,...)
    {
        ...
        return nf_conntrack_confirm(skb);
    }
    // include/net/netfilter/nf_conntrack_core.h
    static inline int nf_conntrack_confirm(struct sk_buff *skb)
    {
    	...
    	nf_ct_deliver_cached_events(ct);
    	...
    }
    // net/netfilter/nf_conntrack_ecache.c
    void nf_ct_deliver_cached_events(struct nf_conn *ct)
    {
        ...
        notify = rcu_dereference(nf_conntrack_event_cb);
        ret = notify->fcn(events | missed, &item);
        ...
    }
    

`NF_HOOK`最终会通过`nf_hooks`执行`nf_conntrack_event_cb->fcn`，`nf_conntrack_event_cb`是一个全局指针，其中存储了网络连接跟踪事件的回调函数

    
    
    // net/netfilter/nf_conntrack_netlink.c
    static int __init ctnetlink_init(void)
    {
        ...
        ret = nf_conntrack_register_notifier(&ctnl_notifier);
        ...
    }
    // net/netfilter/nf_conntrack_ecache.c
    int nf_conntrack_register_notifier(struct nf_ct_event_notifier *new)
    {
        ...
        rcu_assign_pointer(nf_conntrack_event_cb, new);
        ...
    }
    

`nf_conntrack_event_cb`在`net/netfilter/nf_conntrack_netlink.c`中完成了注册指向了`ctnl_notifier`：

    
    
    // net/netfilter/nf_conntrack_netlink.c
    static struct nf_ct_event_notifier ctnl_notifier = {
    	.fcn = ctnetlink_conntrack_event,
    };
    
    static int
    ctnetlink_conntrack_event(unsigned int events, struct nf_ct_event *item)
    {
    	...
        // 不同类型的event会发送到不同的group
    	if (events & (1 << IPCT_DESTROY)) {
    		type = IPCTNL_MSG_CT_DELETE;
    		group = NFNLGRP_CONNTRACK_DESTROY;
    	} else  if (events & ((1 << IPCT_NEW) | (1 << IPCT_RELATED))) {
    		type = IPCTNL_MSG_CT_NEW;
    		flags = NLM_F_CREATE|NLM_F_EXCL;
    		group = NFNLGRP_CONNTRACK_NEW;
    	}
        ctnetlink_dump_master(skb, ct)
    	// netlink_broadcast
        err = nfnetlink_send(skb, item->pid, group, item->report, GFP_ATOMIC);
        ...
    }
    // item->ct->tuplehash->tuple
    // 五元组数据
    struct nf_conntrack_tuple
    {
    	struct nf_conntrack_man src;
    	struct {
    		union nf_inet_addr u3;
    		union {
    			__be16 all;
    			struct {
    				__be16 port;
    			} tcp;
    			...
    		} u;
    	} dst;
    };
    

`nf_conntrack_event_cb->fcn`会执行到`ctnl_notifier.fcn`也就是`ctnetlink_conntrack_event`，`ctnetlink_conntrack_event`会通过`ctnetlink_dump_xxx`系列函数将`item->ct`的数据拷贝至`skb`中，最后通过`nfnetlink_send`发送数据到指定的组。

显然如果我们加入`NETLINK_NETFILTER`的`NFNLGRP_CONNTRACK_NEW`组就能实时获取新网路连接信息了。可以使用`setsockopt`加入指定的组：`setsockopt(fd,
SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, &group, sizeof(group))`

    
    
    // net/socket.c
    SYSCALL_DEFINE5(setsockopt, int, fd, ...)
    {
        ...
    	err = sock->ops->setsockopt(sock, level, optname, optval, optlen);
        ...
    }
    // net/netlink/af_netlink.c
    static int netlink_setsockopt(struct socket *sock, ...)
    {
    	...
        switch (optname){
            case NETLINK_ADD_MEMBERSHIP:
            case NETLINK_DROP_MEMBERSHIP: {
            netlink_update_socket_mc(nlk, val,
    					 optname == NETLINK_ADD_MEMBERSHIP);
            }
        }
        ...
    }
    
    static void netlink_update_socket_mc(struct netlink_sock *nlk,...)
    {
    	int old, new = !!is_new, subscriptions;
    	old = test_bit(group - 1, nlk->groups);
    	subscriptions = nlk->subscriptions - old + new;
    	if (new)
    		__set_bit(group - 1, nlk->groups);
    	else
    		__clear_bit(group - 1, nlk->groups);
    	netlink_update_subscriptions(&nlk->sk, subscriptions);
    	netlink_update_listeners(&nlk->sk);
    }
    

用户态通过`setsockopt`即可调用`netlink_setsockopt`将`socket`加入指定的组用于接收来自指定内核模块的数据。

![image](https://image.3001.net/images/20230530/1685435606_6475b4d676bdf269bd157.png!small)

# 一些限制

`netfilter
conntrack`本身是一种成熟的网络连接状态信息跟踪方案，其功能正符合“新建网络连接监控”这一场景，使其在性能、实时性、兼容性方面都有不错的表现。可以通过`conntrack-tools`快速体验一下这个监控方案：

    
    
    yum install conntrack-tools -y
    conntrack -E -e NEW
    

但在测试过程中发现系统内核版本相同的机器，有的可以使用`netlink`获取实时网络连接信息，有的不行。分析源码不难发现`netlink`模块是通过`core_initcall(netlink_proto_init)`默认加载的，而`netfilter`的相关模块是不会默认加载的。通过`Makefile`也可以看到`nf_conntrack_ipv4`内核模块中包含了我们需要使用的`nf_conntrack_l3proto_ipv4`：

    
    
    # net/ipv4/netfilter/Makefile
    nf_conntrack_ipv4-objs  :=  nf_conntrack_l3proto_ipv4.o nf_conntrack_proto_icmp.o
    obj-$(CONFIG_NF_CONNTRACK_IPV4) += nf_conntrack_ipv4.o
    ...
    

因此如果要通过`netlink`获取实时网络连接信息需要加载这几个内核模块：`nfnetlink nf_conntrack nf_defrag_ipv4
nf_conntrack_netlink nf_conntrack_ipv4`，使用`modprobe`命令加载`nf_conntrack_netlink
nf_conntrack_ipv4`即可自动加载其他依赖模块。

# 参考

https://man7.org/linux/man-pages/man7/netlink.7.html  
https://github.com/torvalds/linux  
https://upload.wikimedia.org/wikipedia/commons/3/37/Netfilter-packet-flow.svg  
https://zhuanlan.zhihu.com/p/567556545  
https://github.com/ti-mo/netfilter  
https://blog.csdn.net/u010285974/article/details/107808108  
https://mp.weixin.qq.com/s/wThfD9th9e_-YGHJJ3HXNQ  
https://mp.weixin.qq.com/s/O084fYzUFk7jAzJ2DDeADg  
https://mp.weixin.qq.com/s/ZX8Jluh-RgJXcVh3OvycRQ  
https://www.netfilter.org/projects/conntrack-tools/downloads.html

