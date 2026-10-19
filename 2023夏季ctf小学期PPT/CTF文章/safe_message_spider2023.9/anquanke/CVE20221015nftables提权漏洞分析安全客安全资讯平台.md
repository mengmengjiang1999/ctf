# CVE-2022-1015 nf_tables 提权漏洞分析

阅读量 **237968**

发布时间 : 2023-02-06 16:45:35

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

author: 莫兴远 of [IceSword Lab](https://www.iceswordlab.com/about/)

## 一、简介

CVE-2022-1015 是 Linux 内核 nf_tables 模块的一个漏洞，其成因为没有合理限制整数范围导致栈越界读写。

受该漏洞影响的内核版本范围为 5.12 ~ 5.16 。

该漏洞为此
[commit](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6e1acfa387b9ff82cfc7db8cc3b6959221a95851)
所修复。

## 二、漏洞相关知识

Netfilter 是 Linux
内核一个非常庞大的子系统，它在内核的网络栈中置入多个钩子，并允许其他模块在这些钩子处注册回调函数，当内核执行到钩子处时，所有被注册的回调函数都会被执行。

nf_tables 则是隶属于 Netfilter 子系统的一个模块，它在 Netfitler
的某些钩子处注册了回调函数，以提供网络数据包过滤功能，通常被用于实现防火墙等功能。本文所分析的漏洞就位于 nf_tables 模块中。

在用户态与 nf_tables 交互则是通过 netlink。netlink 是常见的用户态与内核态进行交互的手段，它通过向 AF_NETLINK 类型的
socket 发送数据向内核传递信息，类似地，还可通过从该类型 socket 接收数据以获取内核传递回来的信息。

###  2.1 nf_tables实现

nf_tables 允许用户向其注册处理网络数据包的 rule，以决定针对不同类型的数据包该采取哪种行动。多条 rule 被组织在一条 chain 中，多条
chain 则被组织在一个 table 中。不同类型的 chain 会与不同的 Netfilter hook 绑定在一起。当网络数据包到达后，经过内核不同的
hook 时，所有绑定在该 hook 处的 chain 都会被执行，以完成对数据包的处理。在这里，chain 的执行是指其中所有的 rule
被依次执行，rule 的执行则又是指数据包会根据其中拟定的规则确定被采取什么行动，是丢弃、拒绝还是接受。

向 nf_tables 注册 rule 的方式是通过 netlink。由于通过 netlink
向内核发送的数据包过于底层，用户使用起来不方便，开发者提供了用户态工具 nft，方便用户通过更高级的语法拟定规则。

**2.1.1 rule**

rule 包含如何处理数据包的逻辑，比如检查数据包的协议、源地址、目标地址、端口等，以分别采取不同的行动。每条 rule 都和一个 verdict
绑定，即每条 rule 都有一个默认的裁定，决定对数据包采取何种行为，是丢弃、拒绝还是接受。举个例子：

    
    
    udp dport 50001 drop
    

drop 就是该 rule 的 verdict，表示所有目标端口为 50001 的 udp 数据包都会被丢弃。

**2.1.2 chain**

chain 是将 rule 组织起来的结构，一条 chain 可包含多条 rule。chain 分为 base chain 和 non-base
chain，base chain 是直接绑定到 Netfilter hook 上面的，执行流只会从 base chain 开始。chain 中的 rule
一般都是依次执行完，有时候某条 rule 的 verdict 会让执行流跳转到其他的 chain，从而越过该 chain 中剩下的 rule，但只能跳转到
non-base chain。跳转分两种，一种是跳转后到某条 chain 后就不可以返回了，另一种则是跳转后还可以返回继续执行原来的 chain 剩下的
rule。

**2.1.3 table**

table 是 nf_tables 最顶层的结构，它包含多条 chain。chain 只能跳转到同一 table 中的其他 chain。

每个 table 都会从属于某个族，族决定了该 table 会处理哪些种类的数据包。族包括 ip、 ip6、 inet、 arp、 bridge 和
netdev。

属于 ip 族的 table 只负责处理 IPv4 数据包，属于 ip6 族的 table 只负责处理 IPv6 数据包，属于 inet 族的 table
则既可处理 IPv4 又可处理 IPv6 数据包。

**2.1.4 expression**

事实上，rule 在层次结构上还可以细分为多个 expression，expression 相当于一条条应用在数据包上的具体指令。用户态工具一般不会涉及到
expression 这个抽象表示，只有内核代码会涉及到。

对于 udp dport 50001 drop 这个规则，需要先通过一个 expression 检查协议是不是 udp，再通过一个 expression
检查端口是不是 50001，如果前面的 expression 都通过了，最后再通过一个 expression 将 verdict 设置为
drop，以将数据包丢弃。

每种 expression 会和一个 struct nft_expr_ops 实例绑定，比如 immediate 这个 expression：

    
    
    static const struct nft_expr_ops nft_imm_ops = {
        .type        = &nft_imm_type, // expression 类型
        .size        = NFT_EXPR_SIZE(sizeof(struct nft_immediate_expr)),
        .eval        = nft_immediate_eval, // 当 expression 被执行时调用
        .init        = nft_immediate_init, // 当 expression 被初始化时调用
        .activate    = nft_immediate_activate,
        .deactivate    = nft_immediate_deactivate,
        .destroy    = nft_immediate_destroy,
        .dump        = nft_immediate_dump,
        .validate    = nft_immediate_validate,
        .reduce        = nft_immediate_reduce,
        .offload    = nft_immediate_offload,
        .offload_action    = nft_immediate_offload_action,
    };
    

每次当一条 rule 被添加进来，其所有 expression 的 init 函数都会被调用。

当某个 expression 被执行时，其 eval 函数会被调用。

**2.1.5 register**

expression 在操作数据包时，需要内存来记录一些数据，这部分内存就是 register。在内核的实现中，所有 register
都在栈上，且在内存地址上是连续的。

expression 可以读取或修改 register 的数据，单次访问的对象既可以是单个 register，也可以是连续的多个 register，因此
register 可以看做是一块连续的缓冲区。

register 可通过 index 索引，以下是内核中定义的 register 的 index：

    
    
    enum nft_registers {
        NFT_REG_VERDICT,
        NFT_REG_1,
        NFT_REG_2,
        NFT_REG_3,
        NFT_REG_4,
        __NFT_REG_MAX,
    
        NFT_REG32_00    = 8,
        NFT_REG32_01,
        NFT_REG32_02,
        ...
        NFT_REG32_13,
        NFT_REG32_14,
        NFT_REG32_15,
    };
    

register 有两种索引方式。NFT_REG_1 到 NFT_REG_4 是一种，共 4 个 register，每个 16
字节；NFT_REG32_00 到 NFT_REG32_15 是另一种，共 16 个 reigster，每个 4
字节。在两种索引方式中，NFT_REG_VERDICT 都指向 verdict register，大小为 16
字节。两种索引方式针对的都是同一片内存，因此内存总数都是 16 + 4 _16 = 16 + 16_ 4 = 80 字节。

![](https://p3.ssl.qhimg.com/t01f8182033bef8e46c.png)

verdict register 在内存上位于最前，每条 rule 执行完后都会设置好 verdict
register，以决定下一步该怎么执行。verdict register 可以设置成以下值：

verdict | 作用  
---|---  
NFT_CONTINUE | 默认 verdict，继续执行下一个 expression。  
NFT_BREAK | 跳过该 rule 剩下的 expression，继续执行下一条 rule。  
NF_DROP | 丢弃数据包，停止执行。  
NF_ACCEPT | 接受数据包，停止执行。  
NFT_GOTO | 跳转到另一条 chain，且不再返回。  
NFT_JUMP | 跳转到另一条 chain，执行完该 chain 后，若 verdict 为 NFT_CONTINUE，则返回原本的 chain
继续执行。  
  
**2.1.6 nft_do_chain**

nft_do_chain 实现了依次执行所有 base chain 中所有 rule 的所有 expression
的逻辑，以下是添加了许多说明性注释的该函数的代码：

    
    
    unsigned int
    nft_do_chain(struct nft_pktinfo *pkt, void *priv)
    {
        const struct nft_chain *chain = priv, *basechain = chain;
        const struct nft_rule_dp *rule, *last_rule;
        const struct net *net = nft_net(pkt);
        const struct nft_expr *expr, *last;
        struct nft_regs regs;
        unsigned int stackptr = 0;
        struct nft_jumpstack jumpstack[NFT_JUMP_STACK_SIZE];
        bool genbit = READ_ONCE(net->nft.gencursor);
        struct nft_rule_blob *blob;
        struct nft_traceinfo info;
    
        info.trace = false;
        if (static_branch_unlikely(&nft_trace_enabled))
            nft_trace_init(&info, pkt, &regs.verdict, basechain);
    do_chain:
        if (genbit)
            blob = rcu_dereference(chain->blob_gen_1);
        else
            blob = rcu_dereference(chain->blob_gen_0);
    
        rule = (struct nft_rule_dp *)blob->data;
        /* 获取最后一条 rule 的位置，以确定循环的停止条件 */
        last_rule = (void *)blob->data + blob->size;
    next_rule: // 执行到一条新的 chain，或返回到原来的 chain，都从这里开始
        regs.verdict.code = NFT_CONTINUE; // the default verdict code = NFT_CONTINUE
        for (; rule < last_rule; rule = nft_rule_next(rule)) { // iterate through the rules
            /* iterate through the expressions */
            nft_rule_dp_for_each_expr(expr, last, rule) {
                // execute the expression
                if (expr->ops == &nft_cmp_fast_ops)
                    nft_cmp_fast_eval(expr, &regs);
                else if (expr->ops == &nft_cmp16_fast_ops)
                    nft_cmp16_fast_eval(expr, &regs);
                else if (expr->ops == &nft_bitwise_fast_ops)
                    nft_bitwise_fast_eval(expr, &regs);
                else if (expr->ops != &nft_payload_fast_ops ||
                     !nft_payload_fast_eval(expr, &regs, pkt))
                    expr_call_ops_eval(expr, &regs, pkt);
                /* 如果 verdict 不是 NFT_CONTINUE， 停止执行该 rule 接下来的 expression */
                if (regs.verdict.code != NFT_CONTINUE) 
                    break;
            }
    
            // 已执行完一条 rule，检查 verdict，
        // 如果不是 NFT_BREAK 或 NFT_CONTINUE，停止执行该 chain 剩下的 rule
            switch (regs.verdict.code) { 
            case NFT_BREAK: 
                // 若为 NFT_BREAK，则将 verdict 设置回 NFT_CONTINUE。
                // NFT_BREAK 和 NFT_CONTINUE 类似，都会执行下一条 rule，
          // 只是 NFT_BREAK 会跳过当前 rule 剩下的 expression。
                regs.verdict.code = NFT_CONTINUE;
                nft_trace_copy_nftrace(pkt, &info);
                continue;
            case NFT_CONTINUE:
                // 执行到这里代表执行完了当前 rule 的所有 expression，
          // 继续执行下一条 rule 即可。
                nft_trace_packet(pkt, &info, chain, rule,
                         NFT_TRACETYPE_RULE);
                continue;
            }
            // 若 verdict 不是 NFT_BREAK 或 NFT_CONTINUE，
        // 代表即将跳过该 chain 剩下的 rule，停止该 chain 的执行。
            break;
        }
    
        nft_trace_verdict(&info, chain, rule, &regs);
    
        // 执行到这里代表执行完了某条 chain，
      // 将根据 verdict 决定采取的行动
        switch (regs.verdict.code & NF_VERDICT_MASK) {
        case NF_ACCEPT:
        case NF_DROP:
        case NF_QUEUE:
        case NF_STOLEN:
            // 已经决定好对当前数据包的处理，退出函数即可。
            return regs.verdict.code;
        }
    
        // 尚未决定好对数据包的处理，继续执行。
        switch (regs.verdict.code) {
        case NFT_JUMP: 
            // 跳转到另一条 chain，将返回时需要的信息保存到 jumpstack 上
        // 返回后，执行的是当前 rule 的下一条 rule
            if (WARN_ON_ONCE(stackptr >= NFT_JUMP_STACK_SIZE))
                return NF_DROP;
            jumpstack[stackptr].chain = chain;
            jumpstack[stackptr].rule = nft_rule_next(rule);
            jumpstack[stackptr].last_rule = last_rule;
            stackptr++;
            fallthrough;
        case NFT_GOTO:
            // 跳转到另一条 chain，不再返回
            chain = regs.verdict.chain;
            goto do_chain;
        case NFT_CONTINUE: // 执行下一条 chain
        case NFT_RETURN: // 返回到上一次跳转前的 chain
            break;
        default:
            WARN_ON_ONCE(1);
      }
    
      // ...
    
        return nft_base_chain(basechain)->policy;
    }
    

每执行完一个 expression、一条 rule 或 一条 chain 时，都会检查 verdict register。

执行完一个 expression 时，非 NFT_CONTINUE 的 verdict 会阻止该条 rule 剩下的 expression 的执行。

执行完一条 rule 时，非 NFT_BREAK 或 NFT_CONTINUE 的 verdict 会阻止该 chain 剩下的 rule 的执行。

执行完一条 chain 时，如果已经决定对数据包的处理，则停止执行。否则，根据 verdict 决定流程如何跳转。

**2.1.7 expression种类**

以下是常见的一些 expression 类型及其功能的简单描述：

类型 | 功能  
---|---  
nft_immediate_expr | 将一个常数保存进 register。  
nft_payload | 从数据包提取数据保存进 register。  
nft_payload_set | 将数据包的某部分数据设置成 register 中的数据。  
nft_cmp_expr | 比较 register 中的数据和某个常数，根据结果决定是否修改执行流。  
nft_bitwise | 对 register 中数据进行位操作，比如左移、亦或。  
nft_range_expr | 和 nft_cmp_expr 类似，但比较的是更大范围的数据，可跨越多个 register。  
  
###  2.2 netlink

和 nf_table 进行交互需要通过 netlink。netlink 是 Linux
系统中和内核通信的常用方式，特别是在网络模块中使用率很高，它的设计是为了克服 ioctl 的一些缺点。

和 netlink 通信需要利用 AF_NETLINK 族的 socket。所有需要使用 netlink 的内核模块都要实现一个
protocal，nf_tables 则是实现了 NETLINK_NETFILTER 这一 protocal。因此，为了和 nf_tables
通信，只需要创建以下 socket：

    
    
    int fd = socket(AF_NETLINK, SOCK_DGRAM, NETLINK_NETFILTER);
    

当创建相应的 netlink socket 时，netlink 还会自动加载相应的模块，只要 modprobe 和 .ko 文件存放在合适的位置。

创建 socket 之后，就可通过 sendmsg 向 socket 发送消息，通过 recvmsg 从 socket 接收消息，从而实现和
nf_tables 通信。

sendmsg 的消息格式是：

    
    
    struct msghdr {
       void         *msg_name;       /* Optional address */
       socklen_t     msg_namelen;    /* Size of address */
       struct iovec *msg_iov;        /* Scatter/gather array */
       size_t        msg_iovlen;     /* # elements in msg_iov */
       void         *msg_control;    /* Ancillary data, see below */
       size_t        msg_controllen; /* Ancillary data buffer len */
       int           msg_flags;      /* Flags (unused) */
    };
    

消息的内容存放在 msg_iov 字段指向的 iovec 数组中。

发送 netlink 消息时，iovec 数组指向 struct nlmsghdr 结构：

    
    
    struct nlmsghdr {
        __u32        nlmsg_len;    /* Length of message including header */
        __u16        nlmsg_type;    /* Message content */
        __u16        nlmsg_flags;    /* Additional flags */
        __u32        nlmsg_seq;    /* Sequence number */
        __u32        nlmsg_pid;    /* Sending process port ID */
    };
    

struct nlmsghdr 之后通常紧跟特定 protocol 定义的协议头部，不同 protocal 的协议头部差异很大。

协议头部之后是多个属性，属性的头部是以下结构：

    
    
    struct nlattr {
        __u16           nla_len;
        __u16           nla_type;
    };
    

属性的实际内容则紧跟在头部之后。

## 三、漏洞成因

漏洞类型是整形溢出导致的栈溢出，同时存在于 nft_validate_register_store 及 nft_validate_register_load
两个函数，以下仅通过 nft_validate_register_load 进行解释，nft_validate_register_store
处的情况大同小异。

    
    
    /* net/netfilter/nf_tables_api.c */
    int nft_validate_register_load(enum nft_registers reg, unsigned int len)
    {
        // 这里检查是否在读取 verdict register， 这是不被允许的
        if (reg < NFT_REG_1 * NFT_REG_SIZE / NFT_REG32_SIZE)
            return -EINVAL;
        if (len == 0) // len 不可以是 0
            return -EINVAL;
      // 由于 reg 的范围没有限制好，导致整形溢出
        if (reg * NFT_REG32_SIZE + len > sizeof_field(struct nft_regs, data))
            return -ERANGE;
    
        return 0;
    }
    

由于 reg 的范围没有限制好，导致 reg * NFT_REG32_SIZE + len 整形溢出。

reg 的取值范围分析可以看 nft_validate_register_load 的调用处：

    
    
    /* net/netfilter/nf_tables_api.c */
    int nft_parse_register_load(const struct nlattr *attr, u8 *sreg, u32 len)
    {
        u32 reg; // 4 byte register variable
        int err;
    
        reg = nft_parse_register(attr); // gets the register index from an attribute
        err = nft_validate_register_load(reg, len); // calls the validating function
        if (err < 0) // if the validating function didn't return an error everything is fine
            return err;
    
        *sreg = reg; // save the register index into sreg (a pointer that is provided as an argument)
        // sreg = source register -> the register from which we read
        return 0;
    }
    EXPORT_SYMBOL_GPL(nft_parse_register_load);
    

可以看到 reg 来自 netlink 属性 attr，通过 nft_parse_register 函数解析出来，再传递给
nft_validate_register_load 函数。

    
    
    /* net/netfilter/nf_tables_api.c */
    /**
     *    nft_parse_register - parse a register value from a netlink attribute
     *
     *    @attr: netlink attribute
     *
     *    Parse and translate a register value from a netlink attribute.
     *    Registers used to be 128 bit wide, these register numbers will be
     *    mapped to the corresponding 32 bit register numbers.
     */
    static unsigned int nft_parse_register(const struct nlattr *attr)
    {
        unsigned int reg;
    
        // from include/uapi/linux/netfilter/nf_tables.h
        // NFT_REG_SIZE = 16 (16 bytes)
        // NFT_REG32_SIZE = 4 (4 bytes)
        reg = ntohl(nla_get_be32(attr));
        switch (reg) {
        case NFT_REG_VERDICT...NFT_REG_4:
            return reg * NFT_REG_SIZE / NFT_REG32_SIZE; 
        default:
            return reg + NFT_REG_SIZE / NFT_REG32_SIZE - NFT_REG32_00;
        }
    }
    

在 nft_parse_register 中，明显没有对 reg 范围做任何限制，传入在 NFT_REG_VERDICT…NFT_REG_4
之外的值，函数最终都会返回 reg + NFT_REG_SIZE / NFT_REG32_SIZE – NFT_REG32_00，也就是 reg – 4。

最终，nft_parse_register_load 传回的 reg 会作为 index 用于访问 nft_do_chain 函数中的 nft_regs
局部变量，导致栈溢出。由于 nft_validate_register_store 及 nft_validate_register_load
两个函数都存在漏洞，因此可以同时越界读和写 nft_regs 之后的栈内存。

## 四、EXP思路

EXP 中存在大量的算术运算计算各种地址位移，所针对的是特定的漏洞及特定的内核映像，在此谈论这些意义不大，因此本文只谈通用的思路。想要更细致研究的话可以参考
EXP 仓库：

<https://github.com/pqlx/CVE-2022-1015>

<https://github.com/ysanatomic/CVE-2022-1015>

通常，由于 canary 的存在，memcpy 等函数引发的栈内存越界写会难以利用，因为 memcpy
的起始地址通常是某个局部变量，要覆写到返回地址则必定会覆写 canary。这个漏洞可以利用的原因就是越界读写的起始地址可以通过传入的 reg
值设定，因此可以越过 canary，从 canary 之后、返回地址之前的地址开始覆写。

###  4.1 泄露内核地址

首先通过动态调试寻找栈上的内核地址，再通过 nft_bitwise 这一 expression 越界读取该范围的内存，保存进 nft_regs
的正常范围内存内，这样才能通过 nft_payload_set 将 nft_regs 正常范围内存的内容复制到数据包中，经由用户态的 socket
接收该数据包获取到内核地址，以绕过 KASLR 保护。

###  4.2 代码执行

通过 nft_payload 将通过数据包发送的 ROP 链复制到 nft_regs 的正常范围内存内，再通过 nft_bitwise
越界写以覆盖到返回地址。为了不覆写到 canary，起始地址必须限制在 canary 之后，返回地址之前。

ROP 链的构造如下：

    
    
    int offset = 0;
    // clearing interrupts
    payload[offset++] = kbase + cli_ret;
    
    // preparing credentials
    payload[offset++] = kbase + pop_rdi_ret; 
    payload[offset++] = 0x0; // first argument of prepare_kernel_cred
    payload[offset++] = kbase + prepare_kernel_cred;
    
    // commiting credentials
    payload[offset++] = kbase + mov_rdi_rax_ret;
    payload[offset++] = kbase + commit_creds;
    
    // switching namespaces
    payload[offset++] = kbase + pop_rdi_ret;
    payload[offset++] = process_id;
    payload[offset++] = kbase + find_task_by_vpid;
    payload[offset++] = kbase + mov_rdi_rax_ret;
    payload[offset++]    = kbase + pop_rsi_ret;
    payload[offset++] = kbase + ini;
    payload[offset++] = kbase + switch_task_namespaces;
    
    // returning to userland
    payload[offset++] = kbase + swapgs_restore_regs_and_return_to_usermode;
    payload[offset++] = (unsigned long)spawnShell;
    payload[offset++] = user_cs;
    payload[offset++] = user_rflags;
    payload[offset++] = user_sp;
    payload[offset++] = user_ss;
    

先清空 interrupt 标志位，屏蔽可屏蔽中断，防止 ROP 被打断。

之后通过调用 prepare_kernel_cred(0) 准备权限为 root 的进程 cred。prepare_kernel_cred
是内核中专门用来准备进程 cred 的，进程 cred 代表了进程的各种权限。当对 prepare_kernel_cred 传入的参数为 0 时，返回的就是
root 权限的进程 cred。

再通过调用 switch_task_namespaces(find_task_by_vpid(process_id), &init_nsproxy) 将
EXP 进程的名称空间切换到 init_nsproxy。其中 process_id 为 EXP 进程的
pid，有许多办法可在用户态获取并保存下来，find_task_by_vpid 则会返回指定 pid 的 task_struct，init_nsproxy
为 init 进程也就是第一个进程的名称空间。由于使用 nf_tables 需要切换到新的 user + network
名称空间，所以这一步是必要的。当然，也可以在获得 root 权限后返回到用户态时再切换。

最后是返回到用户态，通过 swapgs; iret; 这一 gadget。需要在栈上依次准备好 IP、CS、EFLAGS、SP、SS
寄存器的内容，其中，IP 指向可弹出一个 shell 的函数，该函数通过调用 system(“/bin/sh”) 获得 shell。

###  4.3 离开 softirq 上下文

在漏洞发现者的 [EXP](https://github.com/pqlx/CVE-2022-1015) 中，在上一节的清空 interrupt
标志位操作后，还增加了一步离开 softirq 上下文的操作，这是因为在 EXP 作者的利用环境中，nft_do_chain 在
NET_RX_SOFTIRQ 类型 irqsoft 上下文中被调用。这一步不是必须的，但不执行这一步会让系统变得不稳定。

进入 softirq 的逻辑实现在 do_softirq 函数中：

    
    
    /*
     * Macro to invoke __do_softirq on the irq stack. This is only called from
     * task context when bottom halves are about to be reenabled and soft
     * interrupts are pending to be processed. The interrupt stack cannot be in
     * use here.
     */
    #define do_softirq_own_stack()                        \
    {                                    \
        __this_cpu_write(hardirq_stack_inuse, true);            \
        call_on_irqstack(__do_softirq, ASM_CALL_ARG0);            \
        __this_cpu_write(hardirq_stack_inuse, false);            \
    }
    
    ---    
    asmlinkage __visible void do_softirq(void)
    {
        __u32 pending;
        unsigned long flags;
    
        if (in_interrupt())
            return;
    
        local_irq_save(flags);
    
        pending = local_softirq_pending();
    
        if (pending && !ksoftirqd_running(pending))
            do_softirq_own_stack();
    
        local_irq_restore(flags);
    }
    
    
    
    asmlinkage __visible void __softirq_entry __do_softirq(void)
    {
    
        unsigned long end = jiffies + MAX_SOFTIRQ_TIME;
        unsigned long old_flags = current->flags;
        int max_restart = MAX_SOFTIRQ_RESTART;
        struct softirq_action *h;
        bool in_hardirq;
        __u32 pending;
        int softirq_bit;
    
        /*
         * Mask out PF_MEMALLOC as the current task context is borrowed for the
         * softirq. A softirq handled, such as network RX, might set PF_MEMALLOC
         * again if the socket is related to swapping.
         */
        current->flags &= ~PF_MEMALLOC;
        pending = local_softirq_pending();
    
        softirq_handle_begin();
        in_hardirq = lockdep_softirq_start();
    
        account_softirq_enter(current);
    
        restart:
        /* Reset the pending bitmask before enabling irqs */
        set_softirq_pending(0);
    
        local_irq_enable();
    
        h = softirq_vec;
    
        while ((softirq_bit = ffs(pending))) {
            unsigned int vec_nr;
            int prev_count;
    
            h += softirq_bit - 1;
    
            vec_nr = h - softirq_vec;
            prev_count = preempt_count();
    
            kstat_incr_softirqs_this_cpu(vec_nr);
    
            trace_softirq_entry(vec_nr);
            h->action(h); // <---------- net_rx_action is called here
            trace_softirq_exit(vec_nr);
            if (unlikely(prev_count != preempt_count())) {
                pr_err("huh, entered softirq %u %s %p with preempt_count %08x, exited with %08x?\n",
                        vec_nr, softirq_to_name[vec_nr], h->action,
                        prev_count, preempt_count());
                preempt_count_set(prev_count);
            }
            h++;
            pending >>= softirq_bit;
        }
    
        if (!IS_ENABLED(CONFIG_PREEMPT_RT) &&
            __this_cpu_read(ksoftirqd) == current)
            rcu_softirq_qs();
    
        local_irq_disable();
    
        pending = local_softirq_pending();
        if (pending) {
            if (time_before(jiffies, end) && !need_resched() &&
                --max_restart)
                goto restart;
    
            wakeup_softirqd();
        }
    
        account_softirq_exit(current);
        lockdep_softirq_end(in_hardirq);
        softirq_handle_end();
        current_restore_flags(old_flags, PF_MEMALLOC);
    }
    

在 soft_irq 处理完毕后，通过 local_irq_disable() 关中断，再通过 softirq_handle_end() 调整
preempt_count，原来的系统调用栈在 do_softirq 函数中通过调用 do_softirq_own_stack 宏恢复，最后重新打开中断。

由于 softirq _handle_end() 被内联在 \_ _do _softirq()
中，在此[EXP](https://github.com/pqlx/CVE-2022-1015) 中，作者仅通过 ROP 将控制流引导至
\__do_softirq() 调用 softirq_handle_end() 处，调整了 preempt_count，并称可以无副作用地离开
softirq 的上下文，回到进程上下文。

## 参考

[How The Tables Have Turned: An analysis of two new Linux vulnerabilities in
nf_tables](https://blog.dbouman.nl/2022/04/02/How-The-Tables-Have-Turned-CVE-2022-1015-1016/)

[CVE-2022-1015: A validation flaw in Netfilter leading to Local Privilege
Escalation](https://ysanatomic.github.io/cve-2022-1015/)

[Dissecting the Linux Firewall: Introduction to Netfilter’s
nf_tables](https://ysanatomic.github.io/netfilter_nf_tables/)

[A Deep Dive into Iptables and Netfilter
Architecture](https://www.digitalocean.com/community/tutorials/a-deep-dive-into-iptables-and-netfilter-architecture)

[Connection Tracking (conntrack): Design and Implementation Inside Linux
Kernel](https://arthurchiao.art/blog/conntrack-design-and-implementation/)

[Introduction to Netlink — The Linux Kernel
documentation](https://www.kernel.org/doc/html/latest/userspace-api/netlink/intro.html)

[netlink(7) – Linux manual page](https://man7.org/linux/man-pages/man7/netlink.7.html)

[Portal:DeveloperDocs/nftables internals – nftables
wiki](https://wiki.nftables.org/wiki-nftables/index.php/Portal:DeveloperDocs/nftables_internals)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360冰刃实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/286079](/post/id/286079)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE-2022-1015](/tag/CVE-2022-1015)
  * [nf_tables](/tag/nf_tables)

 **+1** __3赞

 __收藏

![](https://p1.ssl.qhimg.com/t016d438783a0ea493a.png) 360冰刃实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

