**作者：王铁磊**  
**原文链接：<https://mp.weixin.qq.com/s/Lj8c5PLzLGIfdBoDzairsQ>**

## 1 引言

虚拟内存 (Virtual Memory, VM)
⼦系统是现代操作系统基础核⼼组件，不仅负责虚拟地址和物理内存的映射关系，管理调度物理内存的使⽤，为程序开发提供统⼀透明的地址空间，同时也要为不同执⾏环境提供隔离，管控物理页⾯读、写、执⾏等权限，是系统安全的基⽯。由于VM⼦系统需要同时兼顾性能、效率、透明性和安全等⽬标，导致VM⼦系统在实现过程中逻辑⼤多异常复杂，VM⼦系统中的各种优化策略也就成了"逻辑错误"类型漏洞的重灾区。

本⽂以iOS、macOS操作系统的内核XNU为例，回顾⼀些与XNU
VM⼦系统相关的历史漏洞；通过分析这些漏洞的成因，梳理VM⼦系统逻辑漏洞的脉络，希望能给其他安全研究带来⼀些启发。

## 2 未预期的破坏

VM⼦系统的⼀个经典功能是Swap，是指在调度物理页⾯时，VM系统可能会将部分物理页⾯转储⾄磁盘从⽽获得⾜够的物理空间；当这些转储的物理页⾯被真正访问时，VM⼦系统再从Swap⽂件中恢复原始物理页⾯内容。

2017年，Google Project 0研究员Ian Beer与Jann
Horn在头脑风暴中，想到⼀个问题，这个Swap⽂件能否被篡改破坏？与其百思不解，不如简单⼀试。macOS系统上，Swap⽂件路径是/private/var/vm/swapfifile0。Ian
Beer简单粗暴的⽤随机数据覆盖了该⽂件：

![](https://images.seebug.org/content/images/2022/04/becbca26-055b-4f23-95cd-18c2c6f30bc8.png-w331s)

结果也⽐较粗暴，内核直接崩溃了[1]。这意味着macOS上在SIP[2]
保护机制并没有保护这个Swap⽂件。在处理被破坏的Swap⽂件时，内核出现了内存错误。⼤胆思考，勇于尝试，是亘古不变的道理。

## 3 未预期的共享

共享内存 (Shared Memory)
是操作系统中实现进程间通信的重要⽅式，通过把相同的物理页⾯映射在不同执⾏体的虚拟地址空间，使双⽅都能访问同样的物理页⾯，不仅能减少物理页⾯的使⽤，也能避免通信过程中传输⼤块数据，从⽽提⾼通信的效率。不过，如果多⽅对同⼀块内存都具有写权限时，维护内存⼀致性变得很困难，"竞争写"也容易引发很多安全问题。

共享内存的双取 (Double Fetch)
是⼀类⾮常典型的安全漏洞成因。下表展⽰了⼀个简单的双取漏洞：第⼀个⾏调⽤strlen计算共享内存中⼀个字符串的长度；第⼆⾏根据该长度分配⼀个本地堆内存；第三⾏调用strcpy把共享内存中的字符串复制到新分配的本地内存中。这三⾏代码的问题在于，因为C
string以\0为截⽌符，strlen扫描字符串时以第⼀次遇到的\0计算当前字符串的长度，同样， strcpy
复制字符串时，直到遇到的\0才会终⽌复制。⽽共享内存另⼀端控制者，可以在strlen和strcpy之间，把第⼀个\0修改为⾮零字符，这导致strcpy会复制过多字符到
local_buffer 中，造成堆溢出。

![](https://images.seebug.org/content/images/2022/04/5c376421-f5e4-432c-aac6-80374319fe38.png-w331s)

随着系统复杂性的增⾼、系统通信层级越来越多，底层开发者与应⽤开发者针对数据传输和使⽤的视⾓很难统⼀，导致很多情况下数据是以⾮预期的共享内存形式传递的，造成很多安全问题。接下来，我们来看⼏个⾮预期共享的案例。

### 3.1 CVE-2017-7047：xpc_data共享内存传输

XNU提供了基于Mach Port和Mach
Message的灵活通信机制。在MachMessage基础上，⽤户态进⼀步封装了libxpc框架，提供了字典、队列、字符串、纯数据等常见数据结构的封装；在libxpc基础上，又封装了NSXPC框架，重点⽀持远程对象和⽅法调⽤。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883721000-3cxtnh.png-w331s)
XNU通信架构

2017年，Ian Beer发现，libxpc在传输xpc_data时，如果数据长度超过0x4000，会调⽤
mach_make_memory_entry_64创建虚拟内存的mach port，然后将mach port发送出去；接收⽅收到这个mach
port后，调⽤mach_vm_map将port对应的虚拟内存再映射到本地。具体流程如下图所⽰。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883721000-4zbovw.png-w331s)
大块xpc_data传递 (发送方使用MAP_MEM_VM_COPY标志)

为避免共享内存的隐患，发送⽅调⽤ mach_make_memory_entry_64时，使⽤了
MAP_MEM_VM_COPY标志。结合XNU中的注释，不难理解使⽤这个标志位创建mach
port过程中，会创建数据的副本。这样接收⽅通过mach_vm_map再次映射后，获得的也是数据副本。这其实是⼀种将xpc_data以写时复制(Copy-on-Write, COW)形式传递的实现⽅式，避免了xpc_data的完全共享。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883722000-5moyyx.png-w331s)

然⽽，Ian Beer敏锐地发现，这种COW依赖于发送⽅创建mach
port时指定MAP_MEM_VM_COPY标志。对于"恶意"发送⽅，完全可以创建⼀个全共享内存的port，然后发送给接收⽅。这样通过mach_vm_map简单映射获得的虚拟地址，会和发送⽅完全共享物理页⾯。这样⼀来，接收⽅使⽤xpc_data时就可能存在双取问题。

Ian
Beer继续追踪系统中对xpc_data的不安全使⽤。NSXPC是在libxpc基础上，在进程间通信中⽀持远程对象和远程⽅法调⽤。在实现中，这些远程对象和⽅法调⽤经序列化后由xpc_data发送。Ian
Beer在这个反序列化过程中，把⼀个双取问题转换成了堆溢出，实现了针对任意NSXPC服务的原型攻击 [4]。

Apple的漏洞修复⽅案也很清晰。在传输xpc_data过程中，不再信任发送⽅，⽽是在接收⽅调⽤mach_vm_map时，强制开启copy选项，也就是以COW形式映射。这样发送⽅对
xpc_data 的任何修改都不会传递到接收⽅，避免了双取问题。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883722000-6zoopw.png-w331s)
大块xpc_data传递 (接收方强制mach_vm_map使用copy选项)

### 3.2 IOKit Out-of-line数据

IOKit是XNU的驱动开发框架，提供了⽤户态程序、内核、设备之间的通信接口。其中，⽤户态程序可以通过 IOConnectCallMethod
接口与内核驱动传递数据。当⽤户态传⼊⼤块数据时（Out-of-line, OOL），系统会创建
IOMemoryDescriptor，将该段数据映射到内核供驱动使⽤。然⽽XNU-3789.31.2版本之前，IOKit开发者没有意识到，这段数据实际是以共享内存形式存在的。IOKit框架和具体驱动开发者之间并没有清晰界定OOL数据的存在形态，以⾄于很多驱动实现中都有双取漏洞。更多漏洞细节可以参考Flanker的blog
[5]。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883722000-7fdqxp.png-w331s)
OOL 双取漏洞实例

例如，在macOS显卡驱动中， IOAccelDisplayPipePostCSCGammaVID::init
函数在处理OOL输⼊时，会根据OOL内的⼀个整数调⽤ IOMalloc 分配内存，然后再次读取该整数⽤于 memcpy
。这种典型的双取漏洞造成极容易利⽤的堆溢出[6]。

鉴于太多驱动开发者都没有意识到OOL数据是通过共享内存传递的，逐⼀纠正驱动开发者的代价太⼤，Apple在XNU-3789.31.2中，直接将OOL数据以COW形式映射。相应的补丁如下。通过使⽤
kIOMemoryMapCopyOnWrite 标志，确保内核获得的数据副本不会存在双取问题。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883722000-8vaaho.png-w331s)
OOL COW映射补丁

### 3.3 Apple Neural Engine共享内存问题

IOKit处理OOL时犯过的错误，也会反应在单独的驱动中。除了直接使⽤OOL数据，IOKit驱动也可以⾃⾏映射⽤户态内存⾄内核使⽤。2018年，Apple推出了A12仿⽣芯⽚，搭载了强⼤的神经⽹络引擎。相应地，iOS内核中也增加⼀个H11ANEIn驱动，⽤于处理神经⽹络引擎的相关计算请求。H11ANEIn需要⼤量异步处理，IOKit框架提供的OOL数据并不适合其计算需求，因此H11ANEIn直接根据⽤户态提供的地址创建了
IOMemoryDescriptor 。

不幸的是，H11ANEIn开发者显然不清楚IOKit的历史旧账，在创建IOMemoryDescriptor时，仅使⽤了
kIODirectionOutIn参数，也就是“读写”权限。H11ANEIn在使⽤这段数据时更加肆意，直接把⼀个Port指针保存在这段内存。因为这段内存被内核和⽤户态共享，⽤户态不仅可以直接获取这个Port指针造成内核地址空间的信息泄漏，也能直接任意替换这个Port指针，通过伪造Port指针获取内核控制权[7]。这个漏洞⾃iOS
12版本引⼊，直到iOS 13.6才被修复；上⽂IOKit框架处理OOL数据的问题隐藏的更久，这些也印证了⾮预期共享问题的隐蔽性。

## 4 复杂的COW

对于⾮预期共享类型的问题，⼀个直接的修复⽅案就是以写时复制(Copy-on-Write,
COW)分享数据。COW是VM⼦系统的⼀个经典优化策略，其核⼼思想是同⼀个物理页⾯可以同时映射在不同进程的虚拟地址空间内，任意⼀⽅试图修改物理页⾯内容时，系统会为其分配⼀个原物理页⾯的副本页⾯，这样写操作最终作⽤在副本页⾯，⽽不会影响原始页⾯，从⽽这个写操作也不会被另⼀⽅所感知。COW原理简单⽽实现复杂。很多操作系统在COW的实现上出现过问题，例如2016年Linux系统中的脏⽜
(Dirty COW) 漏洞。下⾯我们看⼏个XNU中COW相关的安全问题。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883723000-9jwugk.png-w331s)
COW 意图

### 4.1 既共享又COW (CVE-2017-2456)

COW通常把⼀个物理页⾯以read-only权限映射到两个虚拟地址，然后任意⼀个虚拟地址发⽣写操作的时候，系统会捕获页⾯写异常，在异常处理过程中复制新的物理页⾯并更新映射关系。如果虚拟地址VA和虚拟地址VB是COW关系，⽽虚拟地址VA和虚拟地址VC是完全共享关系，即同⼀个物理页⾯被映射到三个（甚⾄更多）虚拟地址时，系统如何处理通过虚拟地址VC发⽣的写操作呢？这并不是⼀个容易回答的问题。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883723000-10twcly.png-w331s)
COW 和完全共享同时存在

带着这个疑虑，Lokihardt做了⼀个测试 [2]。他创建了⼀个Memory
entryport后，通过完全共享的形式把这个内存页⾯映射在两个不同的虚拟地址VA和VC。然后将VA通过复杂消息 Mach
Message发送到另⼀个进程。根据MachMessage的传递规则，消息接收⽅会以COW的形式映射VA对应的物理内存⾄虚拟地址VB。但是，Lokihardt发现此时在发送⽅修改VC内容，并不会触发系统的COW语意；换⽽⾔之，通过VC的所有写，在VB端全部可见。Lokihardt基于这个思路，在libxpc反序列过程中发现了内存双问题，利⽤双取引发的内存溢出，实现了对任意libxpc服务的攻击
(CVE-2017-2456)。在修复这个漏洞时，XNU严格检查了物理页⾯是否多重映射，确保COW的⼀致性。

![图片](https://images.seebug.org/content/images/2022/04/02/1648883723000-11aytic.png-w331s)
CVE-2017-2456的修复

### 4.2 隐蔽的写操作

COW实现的⼀个关键点在于：捕获写操作。这个问题似乎很简单，将物理地址以只读权限映射，写操作⾃然就会触发异常。但是如果写操作并不是通过虚拟地址来实现，COW就可能出现问题。

iOS设备上配备了专门的协处理器⽀持快速图像缩放、⾊彩转换等操作。内核中通过⼀个名为AppleM2Scaler的驱动协调⽤户态和协处理器的通信。对于图像缩放，本质上是⽤户态指定⼀个⽬标内存区域和⼀个源内存区域，AppleM2Scaler通知协处理器通过DMA⽅式直接从源内存区域读取数据处理后写⼊⽬标区域。然⽽，AppleM2Scaler忽略了⽤户态内存的读写属性。这导致⽤户态应⽤可以通过AppleM2Scaler驱动修改任意只读内存。

这个漏洞⽐Linux上的脏⽜漏洞还要严重。2018年，陈良利⽤该漏洞
[8]，在应⽤程序内存空间内修改了⼀块只读内存；这块只读内存本来仅内核可写，内核在使⽤这些数据时不再进⾏验证；陈良利⽤AppleM2Scaler篡改这段只读内存后触发内核其他漏洞，实现iOS的越狱。

这个漏洞还有很多其他利⽤⽅式。iOS设备上动态链接库都被提前链接保存在⼀个shared cache⽂件中。这个shared
cache在设备启动之初，被加载映射到内存中。随后所有启动的进程，都会共享这个shared
cache内存。当然对于其中的代码页⾯，应⽤程序仅具有读+执⾏的权限。AppleM2Scaler这个漏洞可以直接篡改shared
cache代码页⾯，造成在⾼权限进程中的任意代码执⾏。值得⼀提的是，iOS设备上开启了强制代码签名机制。修改代码页⾯后，必须避免系统对页⾯再次进⾏签名验证。这需要通过其他⼀些技巧阻⽌被修改的页⾯触发page
fault。

除了DMA，系统还可能有其他“隐蔽写”操作。Jann Horn针对⽂件映射内存做了⼀些研究
[9,10]，发现了⼀些攻击路径。例如，把⽂件映射到内存后，以COW形式分享给另⼀个进程，此时⽂件内容缓存在物理内存页⾯。当系统内存吃紧时，⽂件内存页⾯会被交换出去；但是Jann
Horn发现，当这些内存页⾯再次被访问时，系统会从磁盘中重新读取⽂件恢复页⾯内容。这就造成了⼀个攻击窗口。如果⽂件来源于攻击者⾃⼰加载的⽂件系统镜像，攻击者可以直接修改(pwrite)
这个⽂件系统镜像从⽽修改相应⽂件内容。这样从⽂件中再次恢复物理页⾯内容时，物理页⾯内容不再与之前页⾯内容⼀致，破坏COW的语意。

### 4.3 危险的锁

2018年，Ian Beer 发现XNU在处理COW映射时，有这样⼀个优化策略：当⼀个进程通过mach
message把⼀个虚拟地址VA对应的内存以COW形式发送出去，并且在mach
message中指明消息发送后就在本地释放虚拟地址VA时，XNU会忽略COW⽽直接把
VA对应的内存项移到接收⽅，省掉了将内存变为COW所需的页⾯权限修改的过程。

然⽽，这个优化策略实现的过程中存在条件竞争
[11]，导致⼀个进程可以同时把VA发送给另⼀个进程和⾃⾝。这样另外⼀个进程和⾃⾝进程都作为这个VA的接收⽅，都会获取这个VA对应内存的访问权限；⽽根据优化策略，这两次接受都不会激活COW复制。Ian
Beer利⽤这个特性，在A12机型上重现了上⽂Lokihardt针对libxpc反序列化的双取漏洞攻击。

Ian Beer在2018年12⽉报告了这个问题，Apple在2019年初对该问题做了⼀次修复。差不多时隔⼀年后，2019年10⽉Ian
Beer再次分析这个漏洞时，发现由于条件竞争的复杂性，Apple的这次修复并不完整。Ian Beer再次提交了PoC。根据Ian Beer
的报告，Apple在2020年初再次对漏洞修复。

## 5 结语

本⽂回顾了XNU在VM管理层⾯的⼀些历史漏洞，尤其是围绕COW实现的各个环节，分析了各种的漏洞成因。尽管这些漏洞已经修复，其实还有很多开放性问题是本⽂没有解答的。例如，Apple针对这些漏洞的修复是否完备？有没有其他途径绕过这些修复？随着系统功能的不断变化，会不会再次引⼊未预期的共享？除了⽂件映射内存和DMA，系统中是否还存在隐蔽的写操作绕过COW？现有的COW实现是不是还有漏洞？希望这些问题能引发⼤家的思考，激发⼤家灵感去寻找新的安全问题。

## 6 参考文献

  1. MacOS uses an insecure swap file. <https://bugs.chromium.org/p/project-zero/issues/detail?id=1131>, 2017.

  2. About System Integrity Protection on your Mac. <https://support.apple.com/en-us/HT204899>

  3. macOS/IOS: mach_msg doesn't copy memory in a certain case. <https://bugs.chromium.org/p/project-zero/issues/detail?d=1083>. 2017.

  4. Many iOS/MacOS sandbox escapes due to unexpected shared memory-backed xpc_data object. <https://bugs.chromium.org/p/project-zero/issues/detail?id=1247>. 2017.

  5. Racing for everyone: descriptor describes TOCTOU in Apple’s core. <https://blog.flanker017.me/racing-for-everyone-escriptor-describestoctou/>

  6. Pwning the macOS Sierra Kernel Inside the Safari Sandbox. <https://github.com/wangtielei/Slides/blob/main/Shakacon_2017.pdf>

  7. Don’t place a port in shared memory. <https://blog.pangu.io/?p=221> .

  8. KeenLab iOS Jailbreak Internals. <https://i.blackhat.com/us-18/Wed-August-8/us-18-Chen-KeenLab-iOS-Jailbreak-Internals.pdf>

  9. XNU: copy-on-write behavior bypass via partial-page truncation of file. <https:// bugs.chromium.org/p/project-zero/issues/detail?id=1725. 2018.

  10. XNU: copy-on-write behavior bypass via mount of user-owned filesystem image. <https://bugs.chromium.org/p/project-zero/issues/detail?id=1726>.2018.

  11. XNU vm_map_copy optimization which requires atomicity isn't atomic. <https:// bugs.chromium.org/p/project-zero/issues/detail?id=1728>. 2018.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1875/>

