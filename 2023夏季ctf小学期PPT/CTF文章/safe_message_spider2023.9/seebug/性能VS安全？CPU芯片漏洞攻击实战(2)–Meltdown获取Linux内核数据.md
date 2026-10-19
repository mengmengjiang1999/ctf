作者：[白小龙，蒸米](https://weibo.com/ttarticle/p/show?id=2309404192925885035405
"白小龙，蒸米")

#### 0x00 序

1月4号的早上，突然就被Meltdown和Spectre这两个芯片漏洞刷屏了，但基本上都是一些新闻报道，对漏洞的分析和利用的信息基本为0。作为安全研究者，不能只浮在表面，还是要深入了解一下漏洞才行，于是开始研究这方面的资料。

研究后，发现其实这个硬件漏洞的影响非常广，不光是Intel，
ARM和AMD也受影响，因此基本上所有的操作系统（Windows，macOS，Linux，iOS,
Android等）都有被攻击的风险。虽然苹果已经发布了公告说全系产品（包括使用ARM的iOS设备）都会受到影响[1]，不过发现者声称还没有看到针对AMD和ARM的攻击。大家猜测原因是AMD和ARM对预测执行实现的效率略差，导致很难通过时间差来进行侧信道攻击（真是傻人有傻福，有时候笨一点反而能躲过一劫，哈哈）。

另外，根据我们分析，在操作系统层面只能够修复Meltdown攻击（在用户态调用syscall的时候对页表的进行限制），但因为Spectre是跑在内核态的，所以除了硬件上升级，暂时没法修复。那么这篇文章就来讲一下什么是Meltdown攻击，以及实战一下利用Meltdown获取Linux内核的数据。

#### 0x01 漏洞分析

Meltdown攻击的雏形其实在2017年7月就已经出现了，由Anders Fogh发表于cyber.wtf
[5]。直到最近爆出完整的利用攻击，一石激起千层浪。该攻击之所以被称之为Meltdown（熔毁），其主要原因在于它可以破坏用户态应用程序和内核态操作系统之间最根本的防护隔离措施，使得攻击者在用户态就可以任意读取系统内核中的数据，造成内核信息泄露。这种攻击方式借助于硬件特性，无视现代操作系统KASLR等保护机制，甚至无视SMAP、SMEP、NX和PXN等CPU硬件保护机制，能够像熔浆一样将用户态和内核态之间的隔离墙熔掉，故而得名。

如下所示，Meltdown攻击代码的基本形式非常简单。需要注意的是，与Spectre攻击不同，Meltdown攻击的代码只需要在用户态运行即可，不需要任何特权，也不需要在内核里执行任何代码。

![](https://images.seebug.org/content/images/2018/01/c992cdbb-a560-4380-9d73-d14a75706a3c.jpg-w331s)

这段代码初看上去不会产生什么问题。因为在第一句的时候，用户态应用程序就会因访问内核态地址空间（[rcx]）而产生异常，使其既不能读取到rcx所指向的内核态地址空间，后面两条指令也不能得到执行。

但实际上，现代CPU处理器的特性（例如Intel的microarchitectures）使得这段代码的执行所产生的影响远超我们的想象，尤其是乱序执行（out-of-order execution）和推测执行（Speculative
execution）这两个特性。简单说来，在乱序执行和推测执行当中，指令的执行先后顺序可能被打乱，一条指令的后续指令可以在该指令没有完全产生效果之前就被执行。值得一提的是，现代CPU处理器所使用的乱序执行和推测执行算法思想在1967年就由Tomasulo[2]提出了。

而在上述Meltdown攻击代码当中，第一条MOV指令除了将rcx内核态地址内的数据放到al之中外，还会进行权限检查，检查进程是否有权限访问该地址。但是这种权限检查是一个相对耗费资源的操作，而乱序执行和推测执行使得CPU在al取到[rcx]内核数据后不会等待权限检查结束就继续执行第二条和第三条指令。在第二条指令计算了`rax=al*4096`之后，第三条指令会以`al*4096`作为索引来获取rbx用户态数组中的某一项数据。在第三条指令执行时，`rbx[al*4096]`会被加载到cache当中。

理论上讲，第一条指令的权限检查最终会失败而产生异常，导致寄存器状态回滚到第一条指令，使得第二、三条指令即使被乱序执行了也不会真正产生效果（即改变寄存器数据）。但实际上，正如前面所述的，第三条指令的执行使得用户态数组中的`rbx[al*4096]`被加载到了cache当中，影响了cache的状态，这就给了攻击者一个可以利用CPU
cache隐通道（covert channel）进行信息窃取的途径。

所谓的CPU
cache隐通道是指攻击者可以利用CPU加载某块地址空间的时间来推断这块内存最近是否被加载过，进而推测更多的数据。例如在上述攻击中，如果al的值是2，则`rbx[2*4096]`会被加载到cache当中。当攻击者以n（0<=n<=255）遍历加载`rbx[n*4096]`时，由于`rbx[2*4096]`被cache过了，则加载的时间会远小于加载其他`rbx[n*4096]`。由此可以推断出al是2，亦即最开始rcx所指向内核数据（byte
[rcx]）是2。

整个攻击流程如下图所示。经测试[4]，Meltdown中所使用到的这种隐通道其读取速率可以达到503KB/s。

![](https://images.seebug.org/content/images/2018/01/81fb9a00-cd0a-478b-b5d0-3ff8e45c02ba.jpg-w331s)

除了乱序执行和推测执行，Meltdown攻击使攻击者在用户态即可读取内核态数据的另外一个先决条件在于，在现代操作系统中，用户态应用程序和内核共享着相同的虚拟地址空间。因此，已有的针对Meltdown的防御手段（例如Linux的KPTI/KAISER[4]）将用户态和内核态的映射分开，使用户态的虚拟地址空间中没有内核内存的映射。

#### 0x02 芯片漏洞实战之利用Meltdown获取Linux内核数据

这个POC是今天早上在github上公布的[6]。POC可以在用户态获取到`linux_proc_banner`这个内核地址上的数据。不过，因为KASLR的原因，这个地址是不确定的，这里POC
cheat了一下，用`“sudo cat
/proc/kallsyms”`获取到了`linux_proc_banner`在内核内存中的位置。其实用我们上一篇讲到的破解KASLR的方法，也可以猜出来kslide。

![](https://images.seebug.org/content/images/2018/01/b5bfa85b-f256-43ea-be2e-1b7fff60c5f3.jpg-w331s)

接下来POC会去打开/proc/version这个文件。/proc/version并不是一个文本文件，如果我们的程序尝试去读这个文件，内核会从`linux_proc_banner`这个地址动态地读取系统的信息并返回给程序。这就意味着这个地址上的数据会被加载到cache里。

![](https://images.seebug.org/content/images/2018/01/35fb0370-5bc8-4e4f-a853-849aae3615d4.jpg-w331s)

因此POC会打开/proc/version这个文件，并每次在进行Meltdown攻击前，都调用pread()一次，保证内核会将这个地址上的数据读到cache中。接下来POC就开始尝试读取`linux_proc_banner`这个内核地址上的数据了。因为一个地址的数据是由8个bit组成的，POC里每次都是只猜一个bit，因此一个地址要猜8次才行。

![](https://images.seebug.org/content/images/2018/01/78f5812d-965d-4c04-be60-b4e3fc803c3c.jpg-w331s)
![](https://images.seebug.org/content/images/2018/01/7ed97bb0-c2c9-4d19-8f1f-e41eeb6ffd8e.jpg-w331s)

猜数据的攻击也就是Meltdown攻击。首先POC将用户态target_array的偏移地址传给rbx。然后进行一段rept循环操作，保证数据已经读入cache。接着，将addr上的数据读到al中，随后根据bit的值（也就是第几位）对rax进行位移和AND
1操作，从而得到目标地址上第bit位的值（0或1）。最后根据是rax的值0还是1，对target_array进行写入操作。虽然在实际情况下，执行到`"movb
(%[addr]),
%%al\n\t"`这一行的时候，CPU就会报出异常了，但因为推测执行的原因，随后的代码已经被执行了，虽然推测执行的结果会回滚，但是对cache的操作却是不可逆的。

![](https://images.seebug.org/content/images/2018/01/2a52b281-b041-493b-97e5-98f1e6c63485.jpg-w331s)

因为读cache的速度要比读内存快很多，因此我们可以通过访问target_array里数据的速度来判断哪个数据被放到了cache里，从而就能知道目标地址上某一位的数据是什么了。

![](https://images.seebug.org/content/images/2018/01/504e6cff-e9ac-43f4-ae6d-d1ab297c0524.jpg-w331s)

那么程序最终的执行结果如下，POC成功的读到了内核在`linux_proc_banner`地址上的数据：

![](https://images.seebug.org/content/images/2018/01/c5d14163-142f-4b43-b8b3-ace6ce00edcb.jpg-w331s)

#### 0x03 总结

本篇文章分析了Meltdown漏洞的原理，并介绍了利用Meltdown获取Linux内核的数据方法。我们随后还会有更多关于芯片漏洞的分析和利用实战，欢迎继续关注本系列的文章，谢谢。

#### 参考文献：

[1] <https://support.apple.com/en-us/HT208394>

[2] TOMASULO, R. M. An efficient algorithm for exploiting multi- ple
arithmetic units. IBM Journal of research and Development 11, 1 (1967), 25_33.

[3] LIPP, M., SCHWARZ, M., GRUSS, D., PRESCHER, T., HAAS, W., MANGARD, S.,
KOCHER, P., GENKIN, D., YAROM, Y., AND HAMBURG, M. Meltdown. Unpublished,
2018.

[4] <https://lwn.net/Articles/738975/>

[5] <https://cyber.wtf/2017/07/28/negative-result-reading-kernel-memory-from-user-mode/>

[6] <https://github.com/paboldin/meltdown-exploit/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/499/>

