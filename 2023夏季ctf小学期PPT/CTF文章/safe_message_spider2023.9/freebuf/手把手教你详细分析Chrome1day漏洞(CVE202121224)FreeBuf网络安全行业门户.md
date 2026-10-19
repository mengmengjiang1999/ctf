## 一、时间线

2021年4月4日 - tr0y4 在 Chromium issue tracker 中提交该漏洞；

2021年4月12日 - Chromium 修复该漏洞，除了补丁外还公开了相关的poc；

2021年4月14日 - 国内的研究员 frust93717815 公开了此漏洞的exp[1][2]，影响未开沙箱的稳定版 Chrome 浏览器；

2021年4月20日 - Chrome发布更新及致谢，对应的CVE编号为 CVE-2021-21224。

## 二、背景

该漏洞发生在v8的优化编译器 TurboFan 中，具体发生在 JIT 的 Simplified-Lowering 阶段。关于TurboFan的介绍可以参考
”Introduction to TurboFan”[3]。有关 Simplefied-Lowering 阶段的具体细节可以参考
CVE-2020-16040 的分析[4]。此外，本文使用Turbolizer 展示 TurboFan 不同优化阶段的 sea of nodes
graph。

下面简单介绍一下sea of
nodes，它是TurboFan运行时的程序表示形式。TurboFan在优化代码时，整个代码是以graph的形式存储的，每个节点就是一个node，包括数学运算、加载、存储、调用、常数等形式。每个node的具体信息如下：

![](https://image.3001.net/images/20210425/1619315292_6084ca5cdbef1e0184fec.jpg!small)

每个 node 都有一个 restriction type 和一个 feedback
type，前者可以理解为节点初始化后的类型，后者则是在实际优化过程中反馈的真实类型。Node 的representation
则表示节点的表示类型，具体如下：  
![](https://image.3001.net/images/20210425/1619315330_6084ca820967e75c187b4.jpg!small)

## 三、漏洞及补丁分析

根据commit信息得知，漏洞发生在 RepresentationChanger:: GetWord32RepresentationFor
函数内。该函数的调用栈如图 1，对该函数的调用主要发生在 Simplified-Lowering 阶段：

![1619315379_6084cab3aedc6565edcfb.png!small?1619315380389](https://image.3001.net/images/20210425/1619315379_6084cab3aedc6565edcfb.png!small?1619315380389)

图1. GetWord32RepresentationFor 调用栈

具体补丁如图 2，output_rep 为传入节点的 Representation 类型， output_type 为当前节点的 feedback
type，use_info 为当前节点的后继节点信息（主要用于区分32位或64位）。所以修复之前的逻辑是满足两种情况之一可以更新op：一是当前节点的
feedback type 是 Signed32 或者 UnSigned32；二是当前节点 feedback type 为 SafeInteger
且其后继节点被用作32位使用（IsUsedAsWord32）。

修复后的逻辑则是满足以下三个条件之一便可以更新：一是当前节点的 feedback type是Signed32；二是当前节点feedback
type是UnSigned32并且后继节点类型是None；三是当前节点为SafeInteger并且后继节点被用作32位使用。

![1619315397_6084cac51d111098a1bc7.png!small?1619315397376](https://image.3001.net/images/20210425/1619315397_6084cac51d111098a1bc7.png!small?1619315397376)

图2. 补丁信息

对比修复前后的逻辑可以发现，在当前节点的 feedback type 为UnSinged32时，并不能直接修改op，需要保证后继节点类型为 None
才能修改。漏洞正是利用了这一条件，在当前节点满足UnSigned32时，其后继节点类型不为None（exp中后继节点类型如图 3所示，为
SingdeSmall，是一个有符号数），最后 op 被赋值为 TruncateInt64ToInt32。

因此，所有传入到当前 TruncateInt64ToInt32
节点的数字都会直接转为一个有符号32位数，如果传入的数字恰好使用到了对应32位数的符号位（比如 exp 中使用的
0xffffffff），那么就会发生整数下溢。

![1619315410_6084cad2b88b29934d732.png!small?1619315411115](https://image.3001.net/images/20210425/1619315410_6084cad2b88b29934d732.png!small?1619315411115)

图3. 后继节点的 use_info

##  **漏洞复现**

为了验证漏洞，本文使用补丁发布前一个版本的v8代码进行实验，commit 哈希为
f87baad0f8b3f7fda43a01b9af3dd940dd09a9a3。为了便于理解，本文简化了 exp 中的 foo 函数如下：

![](https://image.3001.net/images/20210425/1619315505_6084cb312d6c5c5b10def.jpg!small)

这里我们通过对比 Simplified Lowering 及其前一阶段 EscapeAnalysis 的graph结果来展示修复前后turbolizer
graph的变化。如图 1所示，在EscapeAnalysis
阶段70号节点对应到Max的返回结果，它作为51号节点的输入，继续进行下一步的减法操作（SpeculativeSafeIntegerSubtract）。而经过Simplified
Lowering 阶段后，70号节点和51号节点之间被插入了一个新的95号节点
TruncateInt64ToInt32，直接将70号节点的输出转为一个32位有符号数，再进行减法操作。

此时再来看本节使用的例子，Max的返回值是
0xffffffff，即y=0xffffffff，经过TruncateInt64ToInt32节点后，y被转成32位有符号数，也就是-1，发生了整数下溢。因此z最后经过
sign 函数得出的结果是1。

![1619315458_6084cb02c7a32e4a62bbe.png!small?1619315459142](https://image.3001.net/images/20210425/1619315458_6084cb02c7a32e4a62bbe.png!small?1619315459142)

图 4. 修复前EscapeAnalysis阶段的turbolizer graph

![1619315520_6084cb40682a2235b416f.png!small?1619315520660](https://image.3001.net/images/20210425/1619315520_6084cb40682a2235b416f.png!small?1619315520660)

图 5. 修复前Simplified Lowering阶段的turbolizer graph

修复之后得到的 turbolizer graph如图 6，可以看出原本的TruncateInt64ToInt32 节点现在变成了
CheckedUint64ToInt32，在将64位无符号数转为32位有符号数时会进行检查，避免了整数溢出。

![1619315536_6084cb505f9e8a8938b77.png!small?1619315536726](https://image.3001.net/images/20210425/1619315536_6084cb505f9e8a8938b77.png!small?1619315536726)

图6. 修复后Simplified Lowering阶段的turbolizer graph

## 四、漏洞利用分析

###

###  **1\. 漏洞利用**

单独的整数溢出并不能实现 RCE，与之前 CVE-2020-16040[5]和CVE-2021-21220[6]的exploit类似，该 exploit
的作者结合 shift 函数获得一个长度为-1的数组，实现 OOB。

exp 中触发漏洞的地方在 foo 函数，下面的代码只保留了原始 exp 中获取长度为 -1
数组的部分。注释中标注出了每一行代码执行后的结果，可以看到最后声明的 arr 数组实际长度为 1，但是经过 shift 操作后长度直接变成了-1：

![](https://image.3001.net/images/20210425/1619315434_6084caeaacc605d360183.jpg!small)

下面通过对 turbolizer graph（Simplified-Lowering阶段）中各个节点的分析来详细说明产生上述情况的原因。

图7是2-4行代码中包含的关键节点，首先，前两行代码决定x的范围是(-1,4294967295)，接着到Math.max函数中，x首先和0比较取最大值，所以更新后的范围是(0,
4294967295)，然后再与-1比较取最大值，范围没有变化，仍然是(0, 4294967295)。

![1619315565_6084cb6d535372f92ecbc.png!small?1619315565622](https://image.3001.net/images/20210425/1619315565_6084cb6d535372f92ecbc.png!small?1619315565622)

图7. Math.max函数输出结果

在此之后90号节点的值会先被转为 Int32
然后进行一个减法操作，对应代码就是第5行中的0-y，对应的范围是(-4294967295,0)。需要注意的是这里的范围并不是真实的范围，后续还会有
feedback type 的更新会进一步更新这个范围，但是这里对后续的结果并没有影响。Math.sign
函数会根据根据参数的正负，返回+1/-1，此外还有+0/-0/NaN，由于这里+-0并不会对最终结果有影响，所以本文不做过多讨论。由于0-y的值小于等于零，所以该函数输出结果只能是(-1,0)，即z的范围是(-1,0)。接着到第6行代码声明数组，会对数组的边界做检查（长度必须要大于零），所以把z的范围和0取交集得到最后数组长度的范围是(0,0)。

Shift 操作会移除数组中的一个元素，并把数组长度减一。由于数组的长度只能是0，所以 jit 在优化过程中直接把shift之后数组的长度固定为0-1 =
-1，这就是为什么 shift
之前数组长度是1，shift之后长度直接变成了-1。这里其实利用了shift函数中存在的一个bug，即该函数未对数组的边界做检查，无论原始数组的长度如何都直接进行减一操作。由于数组长度为0，所以shift之后长度固定为-1，这一值被直接写入到jit优化后的代码中（在图
9中，长度被直接赋值为0xfffffffe，也就是-2，经过调试发现 jsarry
在内存中存储的长度数值左移了1位，这是为了保证其内存中所有的数字都是以0结尾，指针以1结尾，具体可以参考JS类型对象的内存布局[8]），因此最终得到数组的长度为-1。

![1619315580_6084cb7ca5092ff72d720.png!small?1619315580988](https://image.3001.net/images/20210425/1619315580_6084cb7ca5092ff72d720.png!small?1619315580988)

图 8. 边界检查结果

还有一点需要注意的是，由于shift
操作还会移除数组中的的一个元素，所以如果第6行声明的数组中不包含任何元素，则移除元素操作会导致v8直接崩溃。exp中利用溢出恰好声明了一个长度为1的数组，满足了这一限制条件。这也解释了另一个问题，如果不利用整数溢出漏洞，直接声明一个长度为0的数组，那么根据优化后的jit代码是不是也能得到一个长度为-1的数组呢。实际上jit代码中在shift之前对长度做了验证，如图
9所示，rdi为数组的长度，如果长度为0的话会直接跳过数组长度更新而直接返回，所以无法获得一个长度-1的数组。

![1619315595_6084cb8b2d1fd36aca4c9.png!small?1619315595430](https://image.3001.net/images/20210425/1619315595_6084cb8b2d1fd36aca4c9.png!small?1619315595430)

图9. 调用shift前的边界检查及长度赋值操作

当然，谷歌也在4月15日的更新中修复了该bug[7]。在该补丁中，shift以及类似的pop函数在计算出新的数组长度后会首先进行边界检查，基本上杜绝了类似的利用方式。

![1619315608_6084cb9888283b76a56b7.png!small?1619315608826](https://image.3001.net/images/20210425/1619315608_6084cb9888283b76a56b7.png!small?1619315608826)

图 10. [turbofan] Harden ArrayPrototypePop and ArrayPrototypeShift补丁

###  **2\. 内存读写**

 **1) 越界访问rwarr数组**

exp在 arr
数组之后又声明了一个长度为2的数组和一个长度为0x1000的ArrayBuffer，接着修改了corrput_arr[12]的值，这里其实就是利用溢出修改了rwarr数组的长度。

![](https://image.3001.net/images/20210425/1619315629_6084cbad56cdb7c0ab624.jpg!small)

根据调试信息可以得知，corrput_arr中元素的位置在0x18b80828216c，每个元素的长度是4字节，rwarr中元素的位置在0x18b8082821a8，根据二者之间的距离，减去corrput_arr前八个字节（分别为元素的map和长度），就可以计算出corrput_arr数组第13个元素对应的就是rwarr数组的长度。通过将该长度修改为一个较大的值（比如0x22444），可以实现对rwarr数组的越界访问。

![](https://image.3001.net/images/20210425/1619315655_6084cbc7e6f9cf6f664b4.jpg!small)

``

 **2) 越界访问corrupt_buff**

setbackingStore 就是设置 corrput_buf 中 backing_store 的值，leakObjLow则是泄露地址o处的信息。

![](https://image.3001.net/images/20210425/1619315672_6084cbd8cdc2bf080a7b1.jpg!small)

rwarr设置的第一个元素值为5.1，长度8字节，所以数组中元素都是8字节，因此rwarr[4]的位置在0x18b8082821a98+8+4*8=0x18b8082821ac0，该地址再加4便是corrupt_buff的backing_store的地址，
因此这里还需要用到rwarr[5]，分别修改rwarr[4]的高四个字节和rwarr[5]的低4个字节，就可以实现对backing_store的修改。后续exp会从corrupt_buff中生声明一个Dataview，而backing_store记录的就是实际DataView的内存地址。如果我们将这个backing_store指针修改为我们想要写入的内存地址，那么我们再调用view.setUint32(0,
poc, true) 类似指令时，实际上就是向指定内存地址处写入了poc，从而达到任意地址写。

leakObjLow函数使用corrupt_buff的slot属性，修改该属性为某一对象o，那么o的地址就会被写入到corrupt_buff所在的内存区间中，然后利用rwarr的溢出访问该值，实现泄露。

###
![](https://image.3001.net/images/20210425/1619315699_6084cbf3e6afe76d08fae.jpg!small)

###  **3\. 代码执行**

代码执行的方法利用了WASM的RWX段。通过泄露该RWX段的地址，将shellcode写入，最后调用WASM的导出函数即可实现代码执行。

![](https://image.3001.net/images/20210425/1619315761_6084cc317cc8bb8939f9e.jpg!small)

## 五、参考资料

[1]. avboy1337 (April 4, 2021). 1195777-chrome1day.
https://github.com/avboy1337/1195777-chrome0day

[2]. frust (Arp 15, 2021). Chromium V8
JavaScript引擎远程代码执行漏洞分析讨论。http://noahblog.360.cn/chromium_v8_remote_code_execution_vulnerability_analysis/

[3]. Jeremy (Jan 28, 2019) Introduction to TurboFan.

https://doar-e.github.io/blog/2019/01/28/introduction-to-turbofan

[4]. Faith (Jan, 2021). Analyzing CVE-2020-16040.
https://faraz.faith/2021-01-07-cve-2020-16040-analysis/

[5]. r4j0x00 (Apr 5, 2021). Exploit of CVE-2020-16040.
https://github.com/r4j0x00/exploits/tree/master/CVE-2020-16040

[6]. r4j0x00 (Apr 13, 2021). Exploit of CVE-2021-21220.
https://github.com/r4j0x00/exploits/tree/master/chrome-0day

[7]. Sergei Glazunov (Apr 15, 2021). [turbofan] Harden ArrayPrototypePop and
ArrayPrototypeShift https://chromium-review.googlesource.com/c/v8/v8/+/2823707[8]. Stanko Jankovic (Jun 10, 2019).
V8 Bug Hunting Part 2: Memory representation of JS types.
https://medium.com/@stankoja/v8-bug-hunting-part-2-memory-representation-of-js-types-ea37571276b8

题图：Pixabay License

