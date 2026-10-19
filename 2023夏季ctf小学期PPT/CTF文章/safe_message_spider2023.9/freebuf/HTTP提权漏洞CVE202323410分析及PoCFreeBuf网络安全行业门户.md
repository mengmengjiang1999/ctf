![](https://image.3001.net/images/20230426/1682487996_6448babccc61734f7aebf.png!small)

2023年3月，HTTP协议被发现存在两个漏洞：本地提权漏洞和远程代码执行漏洞。本文将主要探讨本地提权漏洞[CVE-2023-23410](https://www.numencyber.com/cve-2023-23410-analysis/)。

## 漏洞补丁分析

根据ZDI BLOG对这个月补丁的汇总，我们知道这个http提权漏洞是由研究人员提交给ZDI的一个整数溢出的漏洞。
对比更新前后的http代码，的确发现一个比较明显的整数溢出判断修补代码， 如下图所示：

![](https://image.3001.net/images/20230426/1682488009_6448bac9c0fa5dc09688e.png!small)

初步分析该函数，发现这是一个循环保存ServiceName到内存的函数。并且ServiceName个数最多为0x40。然后补丁的作用是把单个ServiceName的长度限制为小于
0xfffc。

在之后的UlpAddServiceNameToContainer函数中有一个小疑惑：这里已经有一个另外的判断ServiceName长度小于0xFFFFFFE8。可以理解这里的判断是为了防止内存申请溢出，但这里的判断和本次补丁修补的判断0xfffc似乎差距太大。

分析代码路径，大方向上这里似乎有两种触发到漏洞补丁函数的途径。
一是通过对本地http服务的设置使用UlSetConfigGroupProperty或者UlSetServerSessionProperty都可以。
另外一种则是通过远程客户端的身份验证响应包，即UlCaptureHttpResponse获取UlExtractAndAppendAuthenticationResponseInfo中的ChannelBindConfig数据。

通常，如果http服务绑定一个对外的本地网络端口，则需要具备高系统权限。 在这里，我们尝试本地的http服务设置来触发漏洞函数补丁的代码路径。

## 构造PoC

参考微软对http
API的一些说明，我们通过HttpSetUrlGroupProperty函数，将其第二个参数设置为HttpServerChannelBindProperty，然后逆向分析其中的一些数据结构以通过检查，我们可以自由设置UlCaptureChannelBindConfig函数中补丁限制的ServiceName长度。但这似乎并不能立即导致更严重的后果。

根据ChannelBindConfig这个关键字，我们注意到UlCopyChannelBindConfigToIrp函数。该函数会具体解析并复制结构体里面所有数据并拷贝到用户提供的缓冲区。并且在其内部函数UlpComputeChannelBindConfigSize中，存在其计算结果溢出的情况。这导致在之后的复制ChannelBindConfig中ServiceName的内容时触发崩溃。崩溃堆栈如下：

![](https://image.3001.net/images/20230426/1682488023_6448bad7050beb96d6dd3.png!small)

虽然此时已经有了一个明确的poc代码路径。但在分析补丁时的那个小疑惑似乎更大了。如果只考虑计算ServiceName时的溢出，为什么补丁修补的是小于一个WORD级别的长度0xfffc，而不是一个DWORD级别的长度即((0xffffffff-otherlenth)/0x40)?

我们参考关键字ServiceName，然后发现在http其他的地方的确总是以WORD的长度来设定ServiceName长度，如UlFindServiceNameInContainer，以及另外一个相关函数UlpIsServiceContainerEquivalent。可以发现http协议整体上都是设定ServiceName长度为WORD。

虽然此次我们构造的溢出是UlpComputeChannelBindConfigSize中产生的，但根本原因是因为UlCaptureChannelBindConfig中，对ServiceName的原始输入长度判断出现错误。

 **PoC链接** ：<https://github.com/numencyber/Vulnerability_PoC.git>

## Exp构造问题

在目前的poc中，最终发生内存损坏的地方是HTTP映射到内核（MmMapLockedPagesSpecifyCache）的用户层缓冲区内存(如下图)，这似乎限制了我们构造利用。

![](https://image.3001.net/images/20230426/1682488037_6448bae56b616bef14970.png!small)

上面的V12是MDL的指针，目前通过本地http服务直接设置HttpQueryUrlGroupProperty的调用路径似乎并不能控制MDL->flags的标志包含MDL_MAPPED_TO_SYSTEM_VA（0x01）或MDL_SOURCE_IS_NONPAGED_POOL(0x04)。

除此之外，似乎只能再尝试找到http服务中其他存在处理ChannelBindConfig或者ServiceName内存长度的代码流程。

## 总结

回顾上面的流程，我们目前的方式都是从 http本地设置的过程中去触发溢出。
另外一种从UlCaptureHttpResponse中的UlExtractAndAppendAuthenticationResponseInfo（这里必须使用Kerberos身份验证方式）去调用UlCaptureChannelBindConfig的路径应该也是可行的。

不过之后要从客户端向服务端触发一个类似UlCopyChannelBindConfigToIrp的流程（触发计算servicename长度导致溢出）。这种调用方式可能需要进一步的分析。在目前分析到的UlpCompleteAuthInfo中的UlFindServiceNameInContainer或者UlpIsServiceContainerEquivalent似乎并不会直接引起内存损坏。

不过即使我们以客户端的方式从远程触发了某种溢出流程，但最终还有一个关键的问题，即最后被溢出损坏的内存最好是系统内核的内存如:分页内存或者非分页内存而不是锁定的用户层内存。

 **参考链接**

  * <https://www.zerodayinitiative.com/blog/2023/3/14/the-march-2023-security-update-review>

  * <https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-23410>

