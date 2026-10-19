*为了方便表达，本文将采用第一人称的方式叙述。

**本文讲述了我在苹果的macOS系统内核中发现的几个堆栈和缓冲区溢出漏洞，苹果官方将这几个漏洞归类为内核中的远程代码执行漏洞，因此这些漏洞的威胁级别非常高。攻击者可以通过这些漏洞远程入侵Mac，也可以在通过物理的方式访问计算机时，仅需要以访客身份登录（无需密码），就可以通过这些漏洞从而获取权限并控制计算机。**

这些漏洞基本都存在于NFS协议中，就是用来将网络驱动安装至Mac的文件系统时使用的，类似于NAS。

## 漏洞相关内容

苹果公司在2018年7月9日发布的MacOS
10.13.6版本更新中修复了这些漏洞。但是当时他们要求我们先不要公布这些漏洞，因为他们需要再做一些调查，看看其他平台上有没有类似的问题或者是否需要解决。当然，现在我们可以敞开说了。

NFS这个东西，现在的使用范围已经非常广，特别是在一些大型企业中，它主要用于共享驱动或联网设备的主目录等内容。当然，也可以在家庭设备中使用，通常会用作媒体服务器。

在macos中，安装NFS不需要特殊的权限，因此任何级别的用户都可以触发这些漏洞，甚至是不需要密码的访客账户。此外许多计算机（尤其是企业环境中的）会配置为在启动时自动挂载NFS共享。

这意味着这些漏洞至少存在两个攻击媒介：

 **1.可能被用于在使用NFS文件管理器的企业中快速传播病毒。**

想要做到这一点，攻击者只需要在其文件管理器上安装具备恶意代码的NFS服务器软件即可，或者通过将恶意文件管理器放在网络上去拦截NFS流量来达成目的。

 **2.用于提权。**

比如，有些人会使用Guest身份登录，然后发出一系列命令连接到NFS服务器（可能存在于网络的任何位置），就可能在计算机上获取内核级别的访问权限。

苹果公司为这五个漏洞分配了CVE分别是：CVE-2018-4259，CVE-2018-4286，CVE-2018-4287，CVE-2018-4288和CVE-2018-4291。我在2018年5月21日发给苹果的漏洞报告中，分别在源码中列出了14条不确定的点。但由于苹果最近才发布了更新，所以我也没有来得及完成对全部源代码的审核。因此，为避免意外泄露任何可能未修复的错误，本文中我只谈及其中两个已经得到验证和修复的漏洞。

## 漏洞复现

我编写了一个PoC去验证漏洞的可用性，可以使用0覆盖4096个字节的堆内存从而导致内核崩溃。我做了一个简短的[视频](https://www.youtube.com/watch?v=UftF80iy8MY)来证明这一点。

4096是一个随机选择，事实上我可以随意修改来发送尽可能多的数据，任何大于128字节的数都会触发缓冲区溢出，我也能够完全控制写入的字节值。因此，尽管这些动作只破坏了内核，但是实际上是可以通过这些缓冲区溢出来实现远程代码执行以及本地提权的操作。

在我第一次发现这个漏洞时，几乎不敢想象我会为了PoC去自己编写NFS服务器。但是在我学了一些[NFS](https://www.ietf.org/rfc/rfc1813.txt)相关知识以及了解到如何使用[rpcgen](http://manpages.ubuntu.com/manpages/bionic/man1/rpcgen.1.html)之后，我就发现其实想要实现也非常简单。用来验证这个漏洞的PoC，仅包含46行C语言以及63行
[RPC](https://tools.ietf.org/html/rfc5531#section-12)语言代码。当然，这些源代码会在苹果官方完成全部修复之后再放出。

## 漏洞详解

在我写的[PoC](https://github.com/apple/darwin-xnu/blob/0a798f6738bc1db01281fc08ae024145e84df927/bsd/nfs/nfs_vfsops.c#L4151)中，这两个漏洞都需要通过这一行看似无害的代码来实现：

    
    
    nfsm_chain_get_fh(error, &nmrep, nfsvers, fh);

这行代码的作用是读取NFS服务器发送回Mac的回复消息（nmrep）中的文件句柄（fh）。这个文件句柄是NFS共享的文件或目录中的不透明标识符。NFSv3中的文件句柄最多64个字节，NFSv4中最多128个字节，XNU中的fhandle_t类型则有足够的空间容纳128字节的文件句柄，但是他们却忽略了去检查nfsm_chain_get_fh宏中的缓冲区溢出情况：

    
    
    /* get the size of and data for a file handle in an mbuf chain */
    #define nfsm_chain_get_fh(E, NMC, VERS, FHP) \
      do { \
        if ((VERS) != NFS_VER2) \
          nfsm_chain_get_32((E), (NMC), (FHP)->fh_len); \
        else \
          (FHP)->fh_len = NFSX_V2FH;\
        nfsm_chain_get_opaque((E), (NMC), (uint32_t)(FHP)->fh_len, (FHP)->fh_data);\
        if (E) \
          (FHP)->fh_len = 0;\
      } while (0)

由于宏命令的大量使用，想理解这段代码可能有些难，但它的实际作用却非常简单：它能够从消息中读取一个32为无符号整数到(FHP)->fh_len，然后读取该字节数，从消息直接进入(FHP)->fh_data。由于没有边界检查，因此攻击者可以选择任何字节序列覆盖任意数量的内核堆。被覆盖的文件句柄在内存中的nfs_socket.c:1401中分配。

这个PoC中，第二个bug是nfsm_chain_get_opaque中的整数溢出：

    
    
    /* copy the next consecutive bytes of opaque data from an mbuf chain */
    #define nfsm_chain_get_opaque(E, NMC, LEN, PTR) \
      do { \
        uint32_t rndlen; \
        if (E) break; \
        rndlen = nfsm_rndup(LEN); \
        if ((NMC)->nmc_left >= rndlen) { \
          u_char *__tmpptr = (u_char*)(NMC)->nmc_ptr; \
          (NMC)->nmc_left -= rndlen; \
          (NMC)->nmc_ptr += rndlen; \
          bcopy(__tmpptr, (PTR), (LEN)); \
        } else { \
          (E) = nfsm_chain_get_opaque_f((NMC), (LEN), (u_char*)(PTR)); \
        } \
      } while (0)

这段代码使用bfsn_rndup将LEN移动至4的下一个倍数处。但它在调用bcopy时会使用LEN的原始值。如果其初值为0xFFFFFFFF，则nfsm_rndup中将出现加法溢出，renlen的值为0，这意味着能够与(NMC)->nmc_left比较成功，并且使用0xFFFFFFFF作为size参数调用bcopy。这便会导致内核崩溃，因此它被用作拒绝服务攻击。

## 使用QL查找错误

QL的一大优势是能够找到已知错误的变种。今年早些时候，我的同事Jonas
Jensen在苹果的NFS启动中发现了两个漏洞：CVE-2018-4136和CVE-2018-4160。我们当时也发布了一篇关于这些漏洞的文章，主要就是针对对bcopy的调用，这个调用可能存在为负的用户控制的大小参数。最简单的方法就是查找用户控制源缓冲区中对bcopy的调用。这很有趣，因为它们可以将用户的数据复制到内核中。

    
    
    /**
     * @name bcopy of network data
     * @description Copying a variable-sized network buffer into kernel memory
     * @kind path-problem
     * @problem.severity warning
     * @id apple-xnu/cpp/bcopy-negative-size
     */
    
    import cpp
    import semmle.code.cpp.dataflow.DataFlow
    import semmle.code.cpp.rangeanalysis.SimpleRangeAnalysis
    import DataFlow::PathGraph
    
    class MyCfg extends DataFlow::Configuration {
      MyCfg() {
        this = "MyCfg"
      }
    
      override predicate isSink(DataFlow::Node sink) {
        exists (FunctionCall call
        | sink.asExpr() = call.getArgument(1) and
          call.getTarget().getName() = "__builtin___memmove_chk" and
          not call.getArgument(2).isConstant())
      }
    
      override predicate isSource(DataFlow::Node source) {
        source.asExpr().(FunctionCall).getTarget().getName() = "mbuf_data"
      }
    }
    
    from DataFlow::PathNode sink, DataFlow::PathNode source, MyCfg dataFlow
    where dataFlow.hasFlowPath(source, sink)
    select sink, source, sink, "bcopy of network data"

上面这条查询相当简单，因为它查找的是对bcopy的任何调用，该调用过程是将数据从mbuf复制到内核中。只要正确检查size参数的边界，这样的调用就没有错误。然而事实证明，很大一部分使用nfsm_chain_get_fh的情况中，不会进行任何边界检查。因此，尽管查询方式很简单，但却很有效，发现了很多重要的漏洞。

实现边界检查的常用方法，一般是：

    
    
    if (n < limit) {
      bcopy(src, dst, n);
    }

我又写了一段来对上面这步进行检测：

    
    
    /**
     * Holds if `guard` is a bounds check which ensures that `size` is less than
     * `limit`. For example:
     * 
     *   if (size < limit) {
     *     ... size ...
     *   }
     */
    predicate guardedSize(GuardCondition guard, Expr size, Expr limit,
                          RelationStrictness strict) {
      exists (boolean branch, Expr sz, BasicBlock block
      | guard.controls(block, branch) and
        block.contains(size) and
        globalValueNumber(size) = globalValueNumber(sz) and
        relOpWithSwapAndNegate(guard, sz, limit, Lesser(), strict, branch))
    }

这段代码使用Guards库来查找在guard控制的控制流位置中使用的大小表达式，然后使用globalValueNumber库来检查条件本身是否出现相同大小的表达式。GlobalValueNumbering库可以提供预测功能，以检测有效短语的权重：

    
    
    if (packet.data.size < limit) {
      ... packet.data.size ...
    }

最后，它使用名为relOpWithSwapAndNegate的程序来检查size表达式是否小于限制：

    
    
    if (packet.data.size >= limit) {
      return -1;
    } else {
      ... packet.data.size ...
    }

当然，有时候也可以通过另一种方式实现边界检查，例如调用min：

    
    
    /**
     * Holds if `size` is bounds checked with a call to `min`:
     * 
     *    size = min(n, limit);
     *
     *    ... size ...
     */
    predicate minSize(Expr size) {
      exists (DataFlow::Node source, DataFlow::Node sink
      | DataFlow::localFlow(source, sink) and
        source.asExpr().(FunctionCall).getTarget().getName() = "min" and
        size = sink.asExpr())
    }

我简单的组合了一下：

    
    
    /**
     * Holds if `size` has been bounds checked.
     */
    predicate checkedSize(Expr size) {
      lowerBound(size) >= 0 and
      (guardedSize(_, size, _, _) or minSize(size))
    }

注意一点，我使用了lowerBound来确保不出现负整数溢出的情况。需要做的就是在isSink方法中使用checkedSize，以减少误报的数量。语句如下：

    
    
    /**
     * @name bcopy of network data
     * @description Copying a variable-sized network buffer into kernel memory
     * @kind path-problem
     * @problem.severity warning
     * @id apple-xnu/cpp/bcopy-negative-size
     */
    
    import cpp
    import semmle.code.cpp.valuenumbering.GlobalValueNumbering
    import semmle.code.cpp.controlflow.Guards
    import semmle.code.cpp.dataflow.DataFlow
    import semmle.code.cpp.dataflow.TaintTracking
    import semmle.code.cpp.rangeanalysis.RangeAnalysisUtils
    import semmle.code.cpp.rangeanalysis.SimpleRangeAnalysis
    import DataFlow::PathGraph
    
    /**
     * Holds if `guard` is a bounds check which ensures that `size` is less than
     * `limit`. For example:
     * 
     *   if (size < limit) {
     *     ... size ...
     *   }
     */
    predicate guardedSize(GuardCondition guard, Expr size, Expr limit,
                          RelationStrictness strict) {
      exists (boolean branch, Expr sz, BasicBlock block
      | guard.controls(block, branch) and
        block.contains(size) and
        globalValueNumber(size) = globalValueNumber(sz) and
        relOpWithSwapAndNegate(guard, sz, limit, Lesser(), strict, branch))
    }
    
    /**
     * Holds if `size` is bounds checked with a call to `min`:
     * 
     *    size = min(n, limit);
     *
     *    ... size ...
     */
    predicate minSize(Expr size) {
      exists (DataFlow::Node source, DataFlow::Node sink
      | DataFlow::localFlow(source, sink) and
        source.asExpr().(FunctionCall).getTarget().getName() = "min" and
        size = sink.asExpr())
    }
    
    /**
     * Holds if `size` has been bounds checked.
     */
    predicate checkedSize(Expr size) {
      lowerBound(size) >= 0 and
      (guardedSize(_, size, _, _) or minSize(size))
    }
    
    class MyCfg extends DataFlow::Configuration {
      MyCfg() {
        this = "MyCfg"
      }
    
      override predicate isSink(DataFlow::Node sink) {
        exists (FunctionCall call
        | sink.asExpr() = call.getArgument(1) and
          call.getTarget().getName() = "__builtin___memmove_chk" and
          not checkedSize(call.getArgument(2)))
      }
    
      override predicate isSource(DataFlow::Node source) {
        source.asExpr().(FunctionCall).getTarget().getName() = "mbuf_data"
      }
    }
    
    from DataFlow::PathNode sink, DataFlow::PathNode source, MyCfg dataFlow
    where dataFlow.hasFlowPath(source, sink)
    select sink, source, sink, "bcopy of network data"

以上就是关于漏洞的所有内容，在这个测试过程中，要多亏Jeremy
Andrus的[文章](https://kernelshaman.blogspot.com/2018/01/building-xnu-for-macos-high-sierra-1013.html)，给予了我莫大的帮助。

## 漏洞时间线

2018-05-21：将漏洞信息及验证过程私信给苹果。

2018-05-22：得到苹果官方的确认。

2018-07-09：收到苹果的通知表示他们需要在其他平台上解决相似问题，要求我不要透露漏洞相关信息。

2018-07-09：苹果官方发布MacOS 10.13.6版本，漏洞被修复。

2018-09-13：向苹果官方咨询能否发布漏洞相关信息。

2018-09-13：苹果方面表示漏洞细节信息会在11月发出。

2018-10-30：漏洞发布。

***参考来源：[lgtm](https://lgtm.com/blog/apple_xnu_nfs_vfsops_CVE-2018-4259)，Karunesh91编译，转载请注明来自FreeBuf.COM**

