**作者：深信服千里目安全实验室**  
**相关阅读：  
1、[【Rootkit 系列研究】序章：悬顶的达摩克利斯之剑](https://paper.seebug.org/1867/ "【Rootkit
系列研究】序章：悬顶的达摩克利斯之剑")  
2、[【Rootkit 系列研究】Windows平台的高隐匿、高持久化威胁](https://paper.seebug.org/1868/
"【Rootkit 系列研究】Windows平台的高隐匿、高持久化威胁")  
3、[【Rootkit 系列研究】Linux平台的高隐匿、高持久化威胁](https://paper.seebug.org/1870/
"【Rootkit系列研究】Linux平台的高隐匿、高持久化威胁")  
4、[【Rootkit 系列研究】Rootkit检测技术发展现状](https://paper.seebug.org/1871/
"【Rootkit系列研究】Rootkit检测技术发展现状")  
5、[【Rootkit 系列研究】Windows平台的高隐匿、高持久化威胁（二）](https://paper.seebug.org/1872/
"【Rootkit 系列研究】Windows平台的高隐匿、高持久化威胁（二）")**

## 摘要

Rootkit这一概念最早出现于上个世纪九十年代初期，CERT Coordination
Center(CERT/CC)于1994年在CA-1994-01这篇安全咨询报告中使用了Rootkit这个词汇。在这之后Rootkit技术发展迅速，这种快速发展的态势在2000年达到了顶峰。2000年后，Rootkit技术的发展也进入了低潮期，但是对于Rootkit技术的研究却并未停滞。在APT攻击日益流行的趋势下，Rootkit攻击和检测技术也同样会迎来新的发展高潮。

在往期的Rootkit系列文章里面，我们分别介绍了Rootkit技术的发展历程和Windows、Linux平台下的Rootkit攻击技术。本期Rootkit系列文章将会给大家介绍当前主流的Rootkit防御技术以及一些非常规Rootkit的可实施检测方案。

## 被滥用的Rootkit技术

长期以来，Rootkit检测一直是一个非常大的痛点，这些具有高度定制化的恶意程序集合隐藏在服务器上，以高权限访问计算机和网络。虽然Rootkit并没有成为大新闻中的主角，但是它们一直都过得很安逸，并且持续性的造成损害。对于安全从业者而言，这不应该是一个被忽视的地方。

APT通常和Rootkit齐头并进。从西方 APT 组织的攻击历史及已经泄露的网络武器看，高隐匿、高持久化(Low&Slow)是其关键特征，而
Rootkit 则是达成此目的的重要技术之一，因此Rootkit一直以来和APT配合的很好。

让人遗憾的是，几乎任何脚本小子都可以轻易在被攻击成功的目标主机上植入Rootkit。比起这个，更让人痛心的是，一些挖矿木马和广告木马都开始使用Rootkit技术了，黑产都卷成这个样子了吗？H2Miner挖矿家族开始使用新的Rootkit样本，该Rootkit使用LD_PRELOAD技术劫持动态链接过程。LD_PRELOAD是一个非常古老的C库技巧，但它今天仍然被成功使用和滥用。

## 当前主流Rootkit检测技术分析

当前主要的Rootkit检测的方法包括但不限于以下几种类型。

**1\. 基于Rootkit运行的效果进行检测**  
例如: 发现隐藏的端口、进程、内核模块、网络连接、被篡改的内核代码。

缺陷: 该检测方案对预设的检测场景的依赖程度较高，一旦恶意软件出现检测场景之外的行为，则难以做到有效检测。

**2\. 静态文件特征检测**  
例如: 扫描磁盘上的文件，将文件与特征库进行匹配，通过该方式检测可能存在的Rootkit。

缺陷: 该检测方案对特征库依赖程度较高，能够有效发现已知特征的Rootkit，难以发现未知特征的Rootkit。

**3\. 动态行为分析检测**  
例如: 对系统运行过程中的行为进行审计，通过行为规则匹配的方式发现系统中的异常行为，通过该方式发现可能存在的Rootkit。

缺陷: 对行为规则的依赖程度较高，只能匹配已知行为特征的Rootkit，难以匹配未知行为特征的Rootkit。

**4\. 数据完整性检测**  
例如: 对系统关键的数据结构进行监控，通过监控关键数据结构的异常篡改，以发现系统中的恶意行为。

缺陷: 完整性检测依赖于受信任的源数据，如果源数据被篡改或者不可信的情况下，则完整性检测也很难奏效。

当前的开源社区的Rootkit检测技术 **主要以Rootkit运行效果检测和静态文件特征检测为主**
，动态行为分析和数据完整性保护的Rootkit检测项目相对较少。

## 当前主流Rootkit检测项目分析

**Chkrootkit:**
检测/proc/kallsyms的内容并匹配相对应的文件名和目录来检测是否存在Rootkit，通过该方式，chkrootkit能够在一定程度上发现Rootkit执行的恶意行为，诸如文件隐藏，网络连接隐藏，进程信息隐藏。但是该检测方案对Rootkit指纹库依赖度较高，并且严重依赖于/proc/目录下的文件，一旦该文件不可信任，则很容易被绕过。

**Rkhunter:**
这个Rootkit检测工具会扫描相应的文件目录、文件、符号表，通过该方式检测是否存在Rootkit恶意家族。同样的，该检测方案对特征库的依赖度较高，且难以发现指纹没有覆盖到的Rootkit。

**Kjackal:**
该Rootkit检测工具通过遍历内核中的系统调用表syscall_table，注意检查例程的入口是否存在内核空间，如果不存在，就意味着发生了syscall劫持。发现了存在syscall_table的劫持之后，该工具会进行反向追踪，以确定劫持系统调用的是哪一个恶意LKM模块。Kjackal会枚举/proc/net/tcp的读写句柄是否存在于内核态中，如果不存在，则发生了劫持。该工具还会枚举modules
kset以检测隐藏的内核模块。该检测方案也同样存在被绕过的可能性，一旦Rootkit通过删除kobject数据结构的方式隐藏Rootkit，那么这将很难检测，不过这种删除kobject数据结构的方式也同样会影响Rootkit正常使用。

**Tyton:**
该项目检测Rootkit的方式和kjackal非常相似，通过枚举内核空间的module_list，中断向量表、网络连接读写句柄、系统调用表、netfilter
hook等方式发现可能存在的Rootkit，发现Rootkit之后，通过get_module_from_addr函数反向溯源恶意的内核模块。

**Elkeid:**
该项目是字节跳动的一个开源的HIDS项目，该hids检测Rootkit的方式继承的tyton的检测方案。除了这个之外，elkeid还在行为检测方面做出了突破，
**使用kprobe**
对关键的系统调用进行hook，持续监控系统运行过程中的进程行为，网络行为、文件行为等相关信息并保存到日志中，再使用字节跳动于近期开源的Elkeid
Hub的行为日志检测引擎和规则集，能够对系统运行过程中的日志进行自动化分析，以发现可能存在的未知威胁。不得不说这是一个非常勇敢的突破，业界普遍都对kprobe持保留态度，敢于直接上车的并不多见。不过这种日志采集方式也存在一个缺陷，一旦攻击者控制了/sys/kernel/debug/kprobes/enabled文件，就可以使这种日志采集功能失效。再补充一句，该项目更新频率较高，并且社区支持非常友好。

**stmichael-lkm:** 该项目能够为内核提供一定的完整性保护，能够在一定程度上发现 **针对内核的篡改**
，通过这种方式发现可能存在的Rootkit。一旦检测到Rootkit篡改内核，StMichael尝试通过将所做的更改回滚到先前已知的良好状态来恢复内核的完整性。不得不说这是一个非常大胆的尝试，比使用kprobe更加激进，这种方案的致命缺陷就是很容易为系统引入未知的问题，导致系统的不稳定。

**Qiling:**
该项目是一个高级二进制仿真框架，能够模拟多平台，多架构的运行环境，通过类似于沙箱的环境运行Rootkit，并且记录Rootkit运行过程中的行为。这为恶意Rootkit的检测和分析提供了一种全新的思路。传统沙箱对恶意软件的检测很难达到这种细粒度的监控效果。

## 非常规Rootkit以及检测方案

#### 使用了命名空间技术的HorsePILL

在讲述该Rootkit之前，有必要简单介绍一下命名空间的含义。命名空间是Linux的一个非常重要的系统特性，Linux的命名空间机制提供了一种资源隔离的解决方案。PID,IPC,Network等系统资源不再是全局性的，而是属于特定的Namespace，不同命名空间的资源是
**互相隔离** 的，在一个命名空间所做的事情不会影响另一个命名空间。各命名空间在Linux的引入版本如下:

![](https://images.seebug.org/content/images/2022/03/e4c25ae9-2e34-4a76-870e-b1c1b05385fa.png-w331s)

由于命名空间的隔离特性，这给恶意文件的隐藏提供了新的思路。将恶意文件和恶意文件运行过程中的进程、网络置于一个 **与系统不同命名空间的环境中**
，可以非常有效的隐藏自身，在一定程度上来说，难以发现。

HorsePILL这个Rootkit就利用了这种命名空间的特性，该Rootkit会感染系统的initramfs，被感染的系统在启动过程中加载initramfs就会执行Rootkit的恶意代码。恶意代码执行之后，会将整个系统置于一个新创建的子命名空间之中，而恶意代码本身运行于更上级的命名空间。这种Rootkit隐藏方式可谓是别具一格，对系统的性能影响可以说忽略不计。是一个非常棒的Rootkit，美中不足的是该Rootkit需要重启系统才能够执行其恶意代码。

这种Rootkit也是有非常有效的运行时检测方案，首先，该Rootkit需要感染initramfs，基于这一点可以修改grub，给grub新增一个
**启动过程中校验initramfs和vmlinuz文件完整性**
的功能，避免启动不受信任的系统。当系统不幸感染了这种基于命名空间的Rootkit，整个系统用户空间的数据已经不在可信的情况下，可以
**从内核态中测绘各个命名空间的信息** ，并且从中发现异常的命名空间数据。

感染horsepill，攻击者拿到了设备的shell，攻击者视角下真实的1号进程的命名空间数据如下:

![](https://images.seebug.org/content/images/2022/03/d4bd7e3d-2393-4a3f-a5aa-6fab1e7673be.png-w331s)

感染horsepill之后设备管理员视角下，可以非常直观的看到命名空间信息已经出现了异常，而这种异常信息通常是被人忽略的。

![](https://images.seebug.org/content/images/2022/03/de1d28ec-f48f-4bb7-97c7-d32ded3cac68.png-w331s)

对于这种Rootkit，受害主机运行时可以通过命名空间测绘的方式发现Rootkit的存在。

#### 使用kprobe技术的Rootkit

在上文中讲Elkeid的时候提到了kprobe这个机制，这个机制可以用来采集系统的行为信息，当然也可以用来编写Rootkit。Kprobe、jprobe以及kretprobe可以在内核符号的函数序言和函数尾声插桩，一旦内核符号注册了kprobe，就会修改函数序言，被修改的函数序言会执行一个跳转指令，跳转到一个新的内核符号trace_spurious_interrupt，然后由trace机制跳转到中断处理函数，中断处理函数再调用kprobe的回调函数，使用kprobe技术可以
**篡改部分内核符号的入参和返回值** ，这能够非常容易的达到隐藏恶意程序相关信息的目的，并且这种Rootkit隐蔽性也同样很强。

这类Rootkit的检测方法也是同样不同于前面的方案的。最简单的判断方法就是查看/sys/kernel/debug/kprobes/list这个文件的内容。
![](https://images.seebug.org/content/images/2022/03/be8baf21-94b9-474e-9a76-80ad8ef03ac3.png-w331s)

但是该方案有一个非常致命的缺陷，系统感染了kprobe的Rootkit之后，/sys/kernel/debug/kprobes/list文件的内容已经是不可信的了，因此需要从其他途径获取Rootkit检测的线索。

内核中有这么一个数据结构kprobe_table，该数据结构维护了所有注册的kprobe的表，遍历这张表，可以发现感染这类Rootkit的kprobe数据结构。

内核符号在vmlinuz、挂载kprobe之前和挂载kprobe之后其数据都是存在非常明显的差异性的。例如:
内核符号SyS_ptrace经过kprobe挂载前后的内存数据对比如下图:

![](https://images.seebug.org/content/images/2022/03/28753778-f848-4179-a29c-4261894d376b.png-w331s)

左边是挂载kprobe之后的内存数据，右边是挂载kprobe之前的内存数据，根据两者对比，可以发现前4个字节存在差异。同样也是这个内核符号，在/boot/vmlinuz文件中的二进制数据也和上面两者不同，相关数据如下图所示:

![](https://images.seebug.org/content/images/2022/03/56817190-c95f-42e3-a83c-102d2831846a.png-w331s)

其差异同样体现在符号的前4个字节。这三者之间的差异主要由两方面因素所导致。首先是
**vmlinuz加载到内存时，会动态的修改其代码内容，这种修改主要通过.altinstructions这个段中的数据完成的。**
加载到内存之后，再对其挂载kprobe，修改的同样是前4个字节，将这部分差异性较强的代码进行反汇编，可以得出其汇编代码。

**Vmlinuz：**  
![](https://images.seebug.org/content/images/2022/03/37f6cdf8-8480-4e81-ad10-c05c4b0f4188.png-w331s)
**Before kprobe:**  
![](https://images.seebug.org/content/images/2022/03/3762553c-0f19-4a9e-90cd-7452bd66e0c6.png-w331s)
**After kprobe:**  
![](https://images.seebug.org/content/images/2022/03/63252e45-669a-4c69-8e5b-d420a300b276.png-w331s)

反汇编这部分数据，可以看到其具体的操作码也有较强差异。首先，符号SyS_ptrace的内存地址为0xffffffff8108a1b0，挂载kprobe之后，其执行的第一个指令为call
0x5bd300。因此可以计算，其跳转地址为:'0xffffffff816474b0'。查询该地址对应的符号如下:
![](https://images.seebug.org/content/images/2022/03/65fcfd36-e37d-4656-97af-1e2ab1b2d80c.png-w331s)

根据上述分析内容，kprobe Rootkit会在执行过程中修改内核符号的函数序言，因此要检测这种类型的Rootkit，还可以对
**运行时的内核代码进行完整性检测。**

#### 基于ebpf的rootkit

基于bpf的Rootkit并不是什么新鲜事物，bpf技术于1993年就被提出，bpf的指令集并非是一种图灵完全的指令集，因此使用bpf指令开发Rootkit似乎是一种天方夜谭。但是APT组织Equation
Group做到了，在shadow brokers于2016年公开方程式的工具包中，有这么一个不太引人瞩目的Rootkit
DewDrops。这么长时间以来，大多数人眼里看到的可能只有永恒系列漏洞利用和doublepulsar后门，而对于其中的Dewdrops
Rootkit，却是很少有人关注。尽管他的知名度并不高，但并不影响我对这个Rootkit设计者的佩服。

但是DewDrops并非此次的主要内容，这一段的主角rootkit是ebpfkit，这个Rootkit于2021年在多个世界顶级安全会议上亮相。该Rootkit可以hook内核态函数，篡改内核态返回用户态缓冲区数据，达到用户态欺骗的目的。用户态进程拿到被篡改的数据，从而被骗通过认证。在此过程，不改变任何文件、进程、网络行为，不产生日志。
**常规HIDS、HIPS产品无法感知。**
eBPF还支持kprobe/kretprobe、uprobe/uretprobe、XDP、TC、socket、cgroup等程序类型，覆盖文件、网络、socket、syscall等事件，都是可以被黑客利用的地方。

面对这么复杂的威胁，从安全防御的视角，该怎样处理这种类型的威胁呢？这个Rootkit的作者给出了这么一份答卷(业界良心啊)。作者开源了针对这种Rootkit的检测工具ebpfkit-monitor。该工具可用于 **静态分析eBPF字节码** 或在 **运行时监控可疑的eBPF活动**
，尽管当前该检测工具仅仅针对ebpfkit，但是这无疑给研究基于ebpf技术的Rootkit检测工具的人提供了良好的思路。

## 结语

在攻防对抗愈加激烈的时代，在APT攻击逐渐进入大众视野的当下，Rootkit的攻防也将会愈加激烈，而安全从业者乃至安全企业，也需要重新审视一下，是否已经具备了针对未知威胁的检测能力，是否已经具备了针对新型攻击技术的检测防御能力。

## 参考资料

1.<https://github.com/Gui774ume/ebpfkit-monitor>

2.<https://github.com/Gui774ume/ebpfkit>

3.<https://github.com/qilingframework/qiling>

4.<https://defcon.org/html/defcon-29/dc-29-speakers.html#fournier>

5.<https://github.com/bytedance/Elkeid>

6.<https://github.com/bytedance/Elkeid-HUB>

7.<https://github.com/qilingframework/qiling>

8.<https://www.cnxct.com/container-escape-in-linux-kernel-space-by-ebpf/>

9.<https://reverse.put.as/2021/12/17/knock-knock-whos-there/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1871/>

