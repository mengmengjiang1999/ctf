## 综述

卡巴斯基披露[1]该在野0day提权漏洞是一个越界写入（增量）漏洞，当目标系统试图扩展元数据块时被利用来获取system权限———Windows中最高的用户权限级别。该漏洞允许改变基础日志文件，作为回报，迫使系统将基础日志文件中的假元素视为真实元素。其通过改变指向内存中一个特定的公共日志文件系统（CLFS）结构的偏移值，使之指向一个恶意结构。此外其在用户层面提供一个指向受控内存的指针，以获得内核的读/写权限。CLFS结构是Windows操作系统使用的CLFS通用日志系统的一部分，它由物理日志文件、日志流、日志记录等组成。

该在野0day提权漏洞已被Nokoyawa 勒索团伙使用，以用于部署勒索软件前获取目标系统的system权限。

Microsoft 在四月补丁日修复该漏洞[2]，并将其标记为CVE-2023-28252（Windows
通用日志文件系统驱动程序特权提升漏洞）。下图是在打补丁前系统上的运行截图，通过漏洞利用完成提权。![1684723079_646ad587899976d328a2f.png!small?1684723080200](https://image.3001.net/images/20230522/1684723079_646ad587899976d328a2f.png!small?1684723080200)

## 漏洞样本分析

该样本本身通过themida进行了保护，因此需要调试时过掉一开始的反调试，之后就和正常的样本分析差不多了，通过对exp样本的分析发现，该漏洞在利用及代码实现上和去年CVE-2022-37969非常相似。如下图所示，样本运行前首先清空对应的工作目录，之后调用fun_osVersioncheck/fun_osVersioncheck获取系统版本，并通过fun_osVersioncheck获取对应读取系统及当前进程的内核偏移，并初始化一系列内存。![1684723087_646ad58f5db5f931e7b4c.png!small?1684723087997](https://image.3001.net/images/20230522/1684723087_646ad58f5db5f931e7b4c.png!small?1684723087997)

这里 fun_osVersioncheck/fun_osVersioncheck 的实现和 CVE-2022-37969
基本保持一致，甚至初始化的关键数据结构也没有太大的变动，如下图所示，该图出自zscaler的安全研究员针对 CVE-2022-37969
的分析[3]。![1684723093_646ad59594cf62df80408.png!small?1684723094128](https://image.3001.net/images/20230522/1684723093_646ad59594cf62df80408.png!small?1684723094128)

通过动态地址获取的方式分别从 clfs.sys/ntoskrnl.exe 中获取函数
ClfsEarlierLsn，ClfsMgmtDeregisterManagedClient，RtlClearBit/
PoFxProcessorNotification，SeSetAccessStateGenericMapping，其中
ClfsMgmtDeregisterManagedClient 及 PoFxProcessorNotification 这两个工具函数在
CVE-2022-37969
中被没有使用。![1684723131_646ad5bb88a221e2d5762.png!small?1684723132117](https://image.3001.net/images/20230522/1684723131_646ad5bb88a221e2d5762.png!small?1684723132117)

在 0x5000000 位置分配 0x1000000 长度的内存，注意 0x5000000 这个地址的使用也和 CVE-2022-37969
一致。![1684723162_646ad5da5f3c54d9addc2.png!small?1684723162830](https://image.3001.net/images/20230522/1684723162_646ad5da5f3c54d9addc2.png!small?1684723162830)

接下来获取 NtFsControlFile 函数地址，并通过 ZwQuerySystimeInformation 获取 PipeAttributer
的内核对象地址，在 0xFFFFFFFF 上分配长度为 4096 的内存，并以此部署 system Process token，熟悉
CVCE-2022-37969 利用的话就知道这个位置使用于辅助 ClfsEarlierLsn/SeSetAccessStateGenericMapping
进行最终的内存写入。![1684723221_646ad6155000f50f45e48.png!small?1684723221864](https://image.3001.net/images/20230522/1684723221_646ad6155000f50f45e48.png!small?1684723221864)

进入该 exp 的核心部分，函数 fun_prepare 中通过 CreateLogFile 创建第一个 log file，这里称之为 trigger
clfs，之后循环调用 fun_trigger 再次创建 10 个 log file，这里称之为 spray
clfs[i]。![1684723238_646ad626c89e022c53cdc.png!small?1684723239381](https://image.3001.net/images/20230522/1684723238_646ad626c89e022c53cdc.png!small?1684723239381)

细看 fun_prepare/fun_trigger 这两个函数中的 log file 是如何构造的，首先是
fun_prepare，核心部分代码如下所示：![1684723268_646ad64458b2374279262.png!small?1684723269053](https://image.3001.net/images/20230522/1684723268_646ad64458b2374279262.png!small?1684723269053)

可以看到其主要是修改了 CLFS log Block Header Record offsets Array[12] 的位置，此外依次在 base
block 及 base block shadow 的 other data 中修改了16个字节的数据，这里注意 base block及base block
shadow
一致。![1684723285_646ad6551faa611706f4f.png!small?1684723285644](https://image.3001.net/images/20230522/1684723285_646ad6551faa611706f4f.png!small?1684723285644)

之后通过写入 clfs 文件，并修复对应的 crc 校验值，最后调用 AddLogContainer 增加一个 log container，需要注意对应的
trigger clfs base block 内核地址 para_clfsKerneladdress 通过 ZwQuerySystemInforation
搜索的方式获取，其原理是通过搜索 0x7a00 大小标志位 clfs 的 pool，类似包括 pipeAttribute
的内核地址也是通过该方式获取。![1684723344_646ad690e0143ead60adb.png!small?1684723345478](https://image.3001.net/images/20230522/1684723344_646ad690e0143ead60adb.png!small?1684723345478)

Spray clfs[i]
中修改的位置就比较分散了![1684723360_646ad6a00436a4c219792.png!small?1684723360644](https://image.3001.net/images/20230522/1684723360_646ad6a00436a4c219792.png!small?1684723360644)

这里注意 Spray clfs[i] 生成之后，在这个位置并没有调用
AddLogContainer![1684723370_646ad6aa2757e79ed9624.png!small?1684723371186](https://image.3001.net/images/20230522/1684723370_646ad6aa2757e79ed9624.png!small?1684723371186)

Spray clfs[i] 中响应的结构如下所示，重点需要注意的位置是 control block 及 control blok shadow
两个对应的位置做了修改，control blok shadow 中被修改为了 0x13，此外 base block 中的cbsyblozone
被设置为0x65c8，其对应的 base block
位置保持一致。![1684723383_646ad6b77d0785d97be3b.png!small?1684723384025](https://image.3001.net/images/20230522/1684723383_646ad6b77d0785d97be3b.png!small?1684723384025)

之后，代码进行了一系列内存 spray 的操作。首先 trigger clfs 对应的内核 base block 内核地址 +0x30
的位置被循环赋值到一个数组 v93 中，然后两次调用函数 fun_pipeSpray，对应的参数分别为 0x5000 及
0x4000。![1684723412_646ad6d4d4b246fd99eeb.png!small?1684723413396](https://image.3001.net/images/20230522/1684723412_646ad6d4d4b246fd99eeb.png!small?1684723413396)

fun_pipeSpray 为一个 pipe 的 spray，其根据参数传入的数量生成指定数量对数的 pipe(read/write)，第一次
fun_pipeSpray 调用传入 0x5000，因此生成了 0x5000 对 pipe(read/write)，这里统一将这 0x5000 对 pipe
称之为 pipeA，第二次的 0x4000 对称之为
pipeB。![1684723443_646ad6f3f2bce45be68ba.png!small?1684723444638](https://image.3001.net/images/20230522/1684723443_646ad6f3f2bce45be68ba.png!small?1684723444638)

遍历 0x5000 对 pipA，并调用其 writepipe 写入包含 trigger clfs base block + 0x30 的数组
v93，遍历结束，从 pipeA(0x2000偏移)，第 174 对 pipe 开始释放，一共释放 0x667 对 pipe
对。![1684723512_646ad73825e68b00c3fb9.png!small?1684723512652](https://image.3001.net/images/20230522/1684723512_646ad73825e68b00c3fb9.png!small?1684723512652)

  

释放结束后，紧接着通过前面的 spray[i] clfs 循环调用 CreateLogFiles，这里大概率就是一处内存占位，用
CreateLogFiles 调用中某一处内存对象占据前面 pipeA 中释放的 pipe 对。

CreateLogFiles 循环占位结束后，遍历 0x4000 对 pipB，并调用其 writepipe 写入前面数组
v93。![1684725106_646add7264211578286f8.png!small?1684725106974](https://image.3001.net/images/20230522/1684725106_646add7264211578286f8.png!small?1684725106974)

  

这一系列操作结束后的内存结构如下

start of pipA(trigger clfs + 0x30) ... spray clfs[i] ....pipB(trigger clfs +
0x30)..end of pipA(trigger clfs + 0x30)  
  
---  
  
完成内存 spray 之后，遍历 spray clfs[i]，为每一个 spray clfs 调用 AddLogContainer 以增加一个 log
container，之后布局 0x5000000中
的内存空间。![1684725138_646add9218d742041727c.png!small?1684725138632](https://image.3001.net/images/20230522/1684725138_646add9218d742041727c.png!small?1684725138632)

完成 0x5000000 的内存布局后，调用 CreateLogFile，此时调用的 clfs 对象是 trigger clfs，CreateLogFile
调用完成即可通过 fun_NtFsControlFile 读取 system process 的 token，从这里就可以看到 CreateLogFile
调用之后应该就触发了漏洞，完成了和之前 CVE-2022-36979 一样的操作，即执行了内存 0x50000000 中的内容，完成了对
PipeAttribute 内核对象的修改，从而使得 fun_NtFsControlFile
能实现任意地址读取。![1684725175_646addb796e33af4a1a7f.png!small?1684725176136](https://image.3001.net/images/20230522/1684725175_646addb796e33af4a1a7f.png!small?1684725176136)

  

之后重复调用 CreateLogFile 触发漏洞，完成进程 token
的替换。![1684725188_646addc42b6939185f636.png!small?1684725189124](https://image.3001.net/images/20230522/1684725188_646addc42b6939185f636.png!small?1684725189124)

  

此外样本中同样也支持修改
priviousMod，实现任意地址读写来提权的方式。![1684725197_646addcd9b9e2f2d005db.png!small?1684725198197](https://image.3001.net/images/20230522/1684725197_646addcd9b9e2f2d005db.png!small?1684725198197)

  

通过分析以上的利用代码可以发现，该漏洞在利用上和之前的 CVE-2022-36979 有很多类似的地方，关键在于通过漏洞疑似修改了container
pointer，在该漏洞中 container pointer 疑似被指向 0x5000000，攻击通过布局
0x5000000，依赖以下工具函数实现任意地址写入，这里同样和 CVE-2022-36979 类似，但是，该工具链中增加了函数：

PoFxProcessorNotification

ClfsMgmtDeregisterManagedClient。

  

最终的调用链为：

PoFxProcessorNotification

ClfsMgmtDeregisterManagedClient

ClfsEarlierLsn

SeSetAccessStateGenericMapping

  

该漏洞利用和 CVE-2022-36979 的不同之处在于，CVE-2022-36979
中漏洞本身的触发很简单，但在触发前进行更为复杂的操作，这里我们将其触发前的代码操作进行一下总结。

1\. Fun_prepare 中生成一个 trigger clfs，其中对应的位置被设定为 0x5000000，并调用 AddLogContainer；

2\. CreateLogFile 创建 10 个 spray clfs[i]；

3\. trigger clfs 的 base block address+0x30 被 pipe spray，具体如下：

3-1. 0x5000对 pipeA(read/write)

3-2. 0x4000对 pipeB(read/write)

3-3. pipeA写入包含12个trigger clfs base block address+0x30地址的数组

3-4. pipeA(0x2000偏移)，第174对pipe开始释放，一共释放0x667对

3-5. 10个spray clfs再次调用CreateLogFile，这里应该是为了占位前一步中释放的0x667对pipe

3-6. 遍历pipeB写入包含12个trigger clfs base block address+0x30地址的数组

spray 完毕后大致的内存如下：

pipA

0x2000

...

spray clfs[n] size 0f 7a00 + 0xDB对pipB

...

0xACDA(0x2000 + 0x667 * 16)

end

4\. 遍历针对第 n 个 spray clfs[i] 调用 AddLogContainer

5\. 针对 trigger clfs 调用 CreateLogFile

  

结合上述的流程，这里猜测第四步中第 n 个 spray clfs[i] 调用 AddLogContainer 将会导致下述内存结构中 spray
clfs[i] 通过相邻的 pipB(trigger clfs + 0x30) 对 trigger clfs base block
内存进行破坏，从而导致之后第五步 trigger clfs 调用 CreateLogFile 时调用了错误的 container pointer，该
pointer 指向 0x500000，最终进入攻击者控制的内存中，并通过一系列辅助函数链最终达成任意地址写。

start of pipA(trigger clfs + 0x30) ... **spray clfs[i]**....pipB(trigger clfs
+ 0x30)..end of pipA(trigger clfs + 0x30)  
  
---  
  
  

## 漏洞原理分析

第一步需要确认我们的猜测是否正确，即是否是调用了错误的 container pointer，该 pointer 指向
0x500000，这里最简单的方法就是针对 CLFS!ClfsEarlierLsn 下断点，因为该函数是 0x500000
这段内存函数调用链的开始，通过它可以找到漏洞触发时是如何进入到该地址执行的。

针对函数 CLFS!ClfsEarlierLsn 下断点，CreatelogFile 函数调用完毕之后，内核中触发进入了
CLFS!ClfsEarlierLsn调用。![1684725948_646ae0bc55cc4a5da527e.png!small?1684725949213](https://image.3001.net/images/20230522/1684725948_646ae0bc55cc4a5da527e.png!small?1684725949213)

  

往上回溯，CLFS!ClfsEarlierLsn 是通过 0x500000 这个位置进入，且这里从代码上看，大概率是破坏了对应的container
pointer。![1684725966_646ae0ce2b2a5a3acfeec.png!small?1684725966742](https://image.3001.net/images/20230522/1684725966_646ae0ce2b2a5a3acfeec.png!small?1684725966742)

  

进入 CLFS!ClfsEarlierLsn
调用。![1684725971_646ae0d34b348ca170930.png!small?1684725972095](https://image.3001.net/images/20230522/1684725971_646ae0d34b348ca170930.png!small?1684725972095)

  

触发 0x500000 内存代码执行的函数为 CLFS!CClfsBaseFilePersisted::CheckSecureAccess，可以看到恶意的
container pointer 来自 v29，而 v29 来自于函数
CLFS!CClfsBaseFile::GetSymbol。![1684725995_646ae0eb43fb28e0c61f6.png!small?1684725995947](https://image.3001.net/images/20230522/1684725995_646ae0eb43fb28e0c61f6.png!small?1684725995947)

  

CLFS!CClfsBaseFile::GetSymbol 中 v29 的值来自于 v17，v17 由 BaseLogRecord + v6 共同决定，这里
BaseLogRecord 是一个固定的值，因此需要看看 v6 来自于哪里，通过代码可知，v6 的值为函数
CLFS!CClfsBaseFile::GetSymbol
的第二个参数传入。![1684726021_646ae105c63916a1a5bb8.png!small?1684726022639](https://image.3001.net/images/20230522/1684726021_646ae105c63916a1a5bb8.png!small?1684726022639)

  

因此返回 CLFS!CClfsBaseFilePersisted::CheckSecureAccess，可以看到
CLFS!CClfsBaseFile::GetSymbol 的第二个参数为 poi(BaseLogRecord +
0xCA)。![1684726028_646ae10c0844f8cc7d66a.png!small?1684726028576](https://image.3001.net/images/20230522/1684726028_646ae10c0844f8cc7d66a.png!small?1684726028576)

  

这里在 CLFS!CClfsBaseFilePersisted::CheckSecureAccess下断，可以看到传入
CLFS!CClfsBaseFile::GetSymbol 前 poi(BaseLogRecord + 0xCA) 的值是
0x1570。![1684726048_646ae120a3992acac89f9.png!small?1684726049571](https://image.3001.net/images/20230522/1684726048_646ae120a3992acac89f9.png!small?1684726049571)

  

作为 CLFS!CClfsBaseFile::GetSymbol
的第二个参数传入。![1684726070_646ae136e5678748f2089.png!small?1684726071502](https://image.3001.net/images/20230522/1684726070_646ae136e5678748f2089.png!small?1684726071502)

  

计算返回对应的 v29，如下所示，返回指针的 0x18 位置就指向 0x5000000，细心的读者可以发现该指针指向的位置其实就是 trigger clfs
中 other data
域中构造的内容。![1684726093_646ae14d2ab30da83d2d3.png!small?1684726093865](https://image.3001.net/images/20230522/1684726093_646ae14d2ab30da83d2d3.png!small?1684726093865)

  

之后代码会依次检测该指针附近的几个值是否符合规定，这些检测的字段也都是 trigger clfs
一开始构造的部分。![1684726104_646ae1586e021035ba9c1.png!small?1684726106016](https://image.3001.net/images/20230522/1684726104_646ae1586e021035ba9c1.png!small?1684726106016)

  

对应的检测代码如下所示![1684726110_646ae15eac2182d79e2ab.png!small?1684726111219](https://image.3001.net/images/20230522/1684726110_646ae15eac2182d79e2ab.png!small?1684726111219)

  

之后返回 CLFS!CClfsBaseFilePersisted::CheckSecureAccess，通过 v29 指向的 0x5000000
进行寻址。![1684726129_646ae17197a7319ec2c59.png!small?1684726130417](https://image.3001.net/images/20230522/1684726129_646ae17197a7319ec2c59.png!small?1684726130417)

  

获取对应的 0x5010000 地址指向的指针，这些都是由攻击者控制，因此最终进入 0x5010000 上由攻击者部署的
CLFS!ClfsEarlierLsn
地址执行。![1684726161_646ae191d92a7e24efd38.png!small?1684726162771](https://image.3001.net/images/20230522/1684726161_646ae191d92a7e24efd38.png!small?1684726162771)

  

从上文中可知代码执行的关键在于 0x1570，该值导致 container poiner 的寻址错误，直接将攻击者构造的 other data
字段中数据作为 container pointer 处理，因此我们需要知道 0x1570 来自何处。

Exp 中调用 AddLogContainer，对应内核中的函数为
CLFS!CClfsLogFcbPhysical::AllocContainer，该函数的 this 指针指向对象
CClfsLogFcbPhysical。![1684726205_646ae1bd900e465223607.png!small?1684726207090](https://image.3001.net/images/20230522/1684726205_646ae1bd900e465223607.png!small?1684726207090)

  

CClfsLogFcbPhysical 对象 0x2b0 的位置指向 CClfsBaseFilePersisted 对象，该对象 0x30
的位置保存一个指针，该指针指向一段 0x90 大小的 heap 内存，这里称之为 clfsheap，clfsheap 0x30 保存指向 base
block
的指针。![1684726240_646ae1e02052ed0ce91b6.png!small?1684726240853](https://image.3001.net/images/20230522/1684726240_646ae1e02052ed0ce91b6.png!small?1684726240853)

  

Clfheap 可以理解为如下的形式，其保存了各个 block 的指针，该图出自 zscaler 的安全研究员针对 CVE-2022-37969
的分析[3]。![1684726274_646ae20229ef421af91aa.png!small?1684726274993](https://image.3001.net/images/20230522/1684726274_646ae20229ef421af91aa.png!small?1684726274993)

  

base block 是一个大小为 0x7a00 的 pool，exp 中就是通过该 pool 的固定大小及 clfs 标记，通过函数
ZQuerySystemInformation
在内核中搜索出该pool的地址。![1684726298_646ae21abb50492a8a8fe.png!small?1684726299210](https://image.3001.net/images/20230522/1684726298_646ae21abb50492a8a8fe.png!small?1684726299210)

  

结合上图中 base block fffa409cb25e000 及 clfs 的结构可知，trigger clfs 中构造的 0x68 处的 0x369
对应了 record offset array[12]，该图出自 zscaler 的安全研究员针对 CVE-2022-37969
的分析[3]。![1684726338_646ae2424fe9d29bbbae7.png!small?1684726338935](https://image.3001.net/images/20230522/1684726338_646ae2424fe9d29bbbae7.png!small?1684726338935)

  

而导致 0x5000000 处调用的 0x1570 位于 base block 0x398 的位置，即 reContainers，该图出自 zscaler
的安全研究员针对 CVE-2022-37969
的分析[3]。![1684726382_646ae26edb7f970aca6c6.png!small?1684726383673](https://image.3001.net/images/20230522/1684726382_646ae26edb7f970aca6c6.png!small?1684726383673)

  

因此这里分别对 trigger clfs base block 这两个偏移下读写断点，如下所示，写断点首先触发，0x398 处被写入
0x1470。![1684726399_646ae27fd331efcb46044.png!small?1684726401173](https://image.3001.net/images/20230522/1684726399_646ae27fd331efcb46044.png!small?1684726401173)

  

此时的调用堆栈如下，可以看到还是在 AllocContaioner
函数中![1684726414_646ae28e696d96622ccd6.png!small?1684726415313](https://image.3001.net/images/20230522/1684726414_646ae28e696d96622ccd6.png!small?1684726415313)

  

向下执行到 spray[i] 触发时的 AddLogContainer，其对应的内核函数调用，对应的
CClfsLogFcbPhysical/CClfsBaseFilePersisted/base block
如下：![1684726457_646ae2b94bc381ba566c4.png!small?1684726459197](https://image.3001.net/images/20230522/1684726457_646ae2b94bc381ba566c4.png!small?1684726459197)

  

再次执行可以看到读断点断下，读取了 spray[i] clfs base block + 0x68 处的
0x369。![1684726472_646ae2c88cb050aa380b1.png!small?1684726473772](https://image.3001.net/images/20230522/1684726472_646ae2c88cb050aa380b1.png!small?1684726473772)

  

紧接着 0x369+r15 (该值为 trigger clfs base block + 0x30)，并将该处的数据++，从而触发之前配置的写断点，即将
trigger clfs base block 0x398 处的 0x1470 成功修改为
0x1570。![1684726547_646ae3135232810635942.png!small?1684726548424](https://image.3001.net/images/20230522/1684726547_646ae3135232810635942.png!small?1684726548424)

  

此时的调用堆栈如下所示，可以看到依然在 AddContainer
中。![1684726560_646ae320603c29cfeb06f.png!small?1684726561646](https://image.3001.net/images/20230522/1684726560_646ae320603c29cfeb06f.png!small?1684726561646)

  

同理可以看到 trigger clfs base 中如果按 0x1470 寻址最后找到的其实是合法的 container pointer，而如果按
0x1570 寻址，最终则指向了攻击者布置的
0x5000000。![1684726588_646ae33c3a0d8e7b04af8.png!small?1684726589976](https://image.3001.net/images/20230522/1684726588_646ae33c3a0d8e7b04af8.png!small?1684726589976)

  

回到触发写入断点的函数
CClfsBaseFilePersisted::WriteMetadataBlock，通过前面的调试可知，触发读写的两个断点直接相邻，且需要注意的是，此时调用
AddLogContainer 的是 spray[i] clfs，即此时
CClfsBaseFilePersisted::WriteMetadataBlock 函数 的 this 指针应该指向 spray[i] clfs 的
CClfsBaseFilePersisted 对象，而实际上通过 spray[i] clfs 的 CClfsBaseFilePersisted 对象获取的
v9 的位置却是 trigger clfs +0x30，这明显是不符合常理，正因为获取到的 v9 指向 trigger clfs +0x30，从而导致之后
poi(poi(trigger clfs + 0x30) + 0x369)++ 的操作，将 trigger clfs +398 处的 0x1470 修改为
0x1570。最终导致后续 trigger clfsc AddLogContainer 调用中寻址 contianer ponter 错误，进入到
0x5000000
的攻击者布局内存中。![1684726721_646ae3c18e36bf309cb7d.png!small?1684726722090](https://image.3001.net/images/20230522/1684726721_646ae3c18e36bf309cb7d.png!small?1684726722090)

  

那这里 v9 是如何生成的，如上图所示 *(_QWORD *)(*((_QWORD *)this + 6) + 24 * v4)，取
CClfsBaseFilePersisted 对象 0x30 位置的指针 +24*v4，该计算中除了 v4 其余数值都是正常，而 v4 来自于
CClfsBaseFilePersisted::WriteMetadataBlock 的第二个参数，同时需要注意的是
CClfsBaseFilePersisted 对象 0x30 位置的指针指向的内容是前面的分析中提到，一段长度为 0x90 的 clfsheap，而在这里
*(_QWORD *)(*((_QWORD *)this + 6) + 24 * v4)，需要计算 24*v4，如果 v4 的值过大将导致 heap
上的越界读取，这也符合我们一开始总结的 exp 中 spray 的内存结构。

start of pipA(trigger clfs + 0x30) ... spray clfs[i] ....pipB(trigger clfs +
0x30)..end of pipA(trigger clfs + 0x30)  
  
---  
  
![1684726847_646ae43f0e64997c06200.png!small?1684726847721](https://image.3001.net/images/20230522/1684726847_646ae43f0e64997c06200.png!small?1684726847721)

  

至此，我们需要看看这个导致越界的 a2 来自何处，回到 CClfsBaseFilePersisted::WriteMetadataBlock 的引用函数
CClfsBaseFilePersisted::ExtendMetadataBlock。![1684726922_646ae48a2afaca73be304.png!small?1684726923494](https://image.3001.net/images/20230522/1684726922_646ae48a2afaca73be304.png!small?1684726923494)

  

可以看到 v5 来自于 CClfsBaseFile::GetControlRecord
的第二个参数。![1684726937_646ae499c4cdeef0edf93.png!small?1684726938324](https://image.3001.net/images/20230522/1684726937_646ae499c4cdeef0edf93.png!small?1684726938324)

  

通过 ida 可以看到 CClfsBaseFile::GetControlRecord 第二个参数是名为 CLFS_CONTROL_RECORD
的结构，其生成方式如下所示![1684726970_646ae4ba9759a6bc0668f.png!small?1684726971231](https://image.3001.net/images/20230522/1684726970_646ae4ba9759a6bc0668f.png!small?1684726971231)

  

CClfsBaseFile::GetControlRecord 第一个参数为 CClfsBaseFilePersisted，如上述分析，其偏移 0x30
指向一段长度为 0x90 大小的
clfsheap。![1684726988_646ae4cc641d64d4d81e6.png!small?1684726989301](https://image.3001.net/images/20230522/1684726988_646ae4cc641d64d4d81e6.png!small?1684726989301)

  

继续往下执行获取 clfsheap 偏移 0x0 处的指针，该指针实际对应了 clfs 的 control block，而 0x30 处就是前面提到的
base
block。![1684727025_646ae4f14ad25e1874711.png!small?1684727026147](https://image.3001.net/images/20230522/1684727025_646ae4f14ad25e1874711.png!small?1684727026147)

  

获取 control block 偏移 0x28 处的数值，并和 control block 相加计算得到返回的 CLFS_CONTROL_RECORD

CClfsBaseFilePersisted

+0x30 heap block

0x0 _CLFS_CONTROL_RECORD

CLFS_METADATA_RECORD_HEADER(size 0x70)

这里 CLFS_CONTROL_RECORD 结构如下所示：

typedef struct _CLFS_CONTROL_RECORD

{

CLFS_METADATA_RECORD_HEADER hdrControlRecord; 70

ULONGLONG ullMagicValue;

UCHAR Version;

CLFS_EXTEND_STATE eExtendState;

USHORT iExtendBlock;

USHORT iFlushBlock;

ULONG cNewBlockSectors;

ULONG cExtendStartSectors;

ULONG cExtendSectors;

CLFS_TRUNCATE_CONTEXT cxTruncate;

USHORT cBlocks;

ULONG cReserved;

CLFS_METADATA_BLOCK rgBlocks[ANYSIZE_ARRAY];

} CLFS_CONTROL_RECORD, *PCLFS_CONTROL_RECORD;  
  
---  
  
  

可以看到该返回的数据实际是 CLFS_CONTROL_RECORD 中跳过 hdrControlRecord(0x70) 之后的位置，该位置偏移 0x10
开始就是 spray[i] clfs
构造时设置的数据。![1684727120_646ae5502a35c20194d60.png!small?1684727120978](https://image.3001.net/images/20230522/1684727120_646ae5502a35c20194d60.png!small?1684727120978)

  

继续向下执行到 CClfsBaseFilePersisted::WriteMetadataBlock，此时通过返回的指针寻址到 0x1a 处的数据，正好就是
spray[i] clfs 中构造的数据 0x13，对应上文 CLFS_CONTROL_RECORD 结构, 这里 ullMagicValue 固定为
0xc1f5c1f500005f1c，因此这个位置应是
iFlushBlock。![1684727153_646ae571284e43cbda984.png!small?1684727153937](https://image.3001.net/images/20230522/1684727153_646ae571284e43cbda984.png!small?1684727153937)

  

这里需要遍历到符合触发结构的 spray[i]，此时该 spray[i] 对应的 CClfsBaseFilePersisted 地址为
ffff9087fbd87000。![1684727170_646ae582db18d17c06180.png!small?1684727171444](https://image.3001.net/images/20230522/1684727170_646ae582db18d17c06180.png!small?1684727171444)

  

该 spray[i] clfs CClfsBaseFilePersisted 对应的 clfsheap
如下所示：![1684727185_646ae591f20f50f323bc1.png!small?1684727186613](https://image.3001.net/images/20230522/1684727185_646ae591f20f50f323bc1.png!small?1684727186613)

  

通过传入的参数 2(0x13) 计算偏移，最终得出偏移 0x1c8，并获取 clfsheap+0x1c8
处的数据。![1684727212_646ae5acc480962f837a5.png!small?1684727213443](https://image.3001.net/images/20230522/1684727212_646ae5acc480962f837a5.png!small?1684727213443)

  

但是这里需要注意实际上 clfsheap 的长度只有 0xa0，因此按 0x1c8
去寻址一定会导致越界读取。![1684727237_646ae5c5476a47179c3a2.png!small?1684727238009](https://image.3001.net/images/20230522/1684727237_646ae5c5476a47179c3a2.png!small?1684727238009)

  

而 0x1c8 处的数据正好就是我们之前 spray 时通过 pipeB 占据写入的数组，而该数组中保存了 12 个 trigger clfs base
block +0x30
的地址，因此直接越界读取了该数据。![1684727260_646ae5dc6800a6db33035.png!small?1684727261815](https://image.3001.net/images/20230522/1684727260_646ae5dc6800a6db33035.png!small?1684727261815)

  

之后代码中通过 trigger clfs + 0x30 按公式 (poi(poi(trigger clfs + 0x30) + 0x369)++)
进行运算，导致 triger clfs base block 原本偏移 0x398 处的 0x1470 被修改为 0x1570。并最终在 triger
clfs 调用 AddLogContainer 时，通过 0x1570 寻址到错误的 container poiner，直接执行到攻击者布局的恶意内存
0x5000000
中。![1684727295_646ae5ffe86f10363d9f7.png!small?1684727296892](https://image.3001.net/images/20230522/1684727295_646ae5ffe86f10363d9f7.png!small?1684727296892)

  

## 总结

fun_trigger 函数中关键的位置在于修改了 spray clfs[i] control block 中的对应 iFlushBlock，导致之后针对
spray clfs[i] 调用 AddLogContain时CClfsBaseFilePersisted::WriteMetadataBlock 超过
clfsheap 0x90 大小的越界读取。通过 spray pip，形成以下内存布局。

start of pipA(trigger clfs + 0x30) ... spray clfs[i] ....pipB(trigger clfs +
0x30)..end of pipA(trigger clfs + 0x30)  
  
---  
  
  

越界读取对应 spray clfs[i] clfsheap 结构后 pipB 数组中的 trigger clfs + 0x30，trigger clfs 中
0x58 的位置被 log 初始化时设置为 0x369，WriteMetadataBlock 继续向下执行，通过越界读取的 trigger clfs +
0x30，执行以下代码运算：

poi(trigger clfs + 0x30 + poi(trigger clfs + 0x30 + 0x28))++

  

这最终导致 trigger clfs rgcontainer[0] 中的值由 0x1470 被修改为 0x1570。

之后通过 trigger clfs 调用 CreateLogFile, CClfsBaseFilePersisted::CheckSecureAccess
中调用 Getsymbol，trigger clfs 通过 rgcontainer[0] 获取对应的 container pointer，由于
rgcontainer[0] 的 0x1470 已经被修改为 0x1570，导致获取的 container pointer 为攻击者在 trigger
clfs 初始化 log 时设置的恶意 container，其对应的指针为 0x5000000。最终 eip 执行到
0x5000000，进入攻击者布局的函数调用链中。![1684727422_646ae67ecc2e320b7602c.png!small?1684727423556](https://image.3001.net/images/20230522/1684727422_646ae67ecc2e320b7602c.png!small?1684727423556)

  

最终的提权样本提供了两种方式，通过在 0x5000000 上部署以下的函数序列来实现导致任意地址写入

(ClfsEarlierLsn/PoFxProcessorNotification/ClfsMgmtDeregisterManagedClient/SeSetAccessStateGenericMap)，任意写入修改了
pipe Attribute，通过 NtFsControlFileread 实现任意地址读取，从而替换当前进程 token 实现提权。

  

这里的核心其实是 ClfsEarlierLsn 和 SeSetAccessStateGenericMap。

ClfsEarlierLsn 执行完毕后会将 rdx 赋值为 0xffffffff，而该地址上部署了 pipe Attributer
内核对象。![1684727480_646ae6b81eeb2e7ad9390.png!small?1684727480904](https://image.3001.net/images/20230522/1684727480_646ae6b81eeb2e7ad9390.png!small?1684727480904)

  

SeSetAccessStateGenericMap 会将 rcx+48 部署的恶意数据写入到 rdx 指向的指针中，即 pipe Attributer 的
AttributeValueSize 字段，从而可以通过 NtFsControlFileread
实现任意地址读取。![1684727509_646ae6d5635bb7c3a66c6.png!small?1684727509902](https://image.3001.net/images/20230522/1684727509_646ae6d5635bb7c3a66c6.png!small?1684727509902)

  

该利用不像之前 CVE-2022-36979 简单直接通过 ClfsEarlierLsn/SeSetAccessStateGenericMap
的组合进行调用，而是在这之间还插入两个函数。首先是 PoFxProcessorNotification，该函数会以第一个参数偏移 0x68
位置为函数指针，偏移 0x48
为参数进行调用。![1684727538_646ae6f2a1295c34b164b.png!small?1684727539269](https://image.3001.net/images/20230522/1684727538_646ae6f2a1295c34b164b.png!small?1684727539269)

  

插入的第二个函数为 ClfsMgmtDeregisterManagedClient，该函数会通过第一个参数偏移 8/0x28
的位置进行调用，参数本身作为第一个参数，该漏洞利用进入 0x5000000 的主要调用流程是

PoFxProcessorNotification -> ClfsMgmtDeregisterManagedClient，并在
ClfsMgmtDeregisterManagedClient 中依次调用
ClfsEarlierLsn/SeSetAccessStateGenericMap![1684727588_646ae72446fac8202b6bb.png!small?1684727588885](https://image.3001.net/images/20230522/1684727588_646ae72446fac8202b6bb.png!small?1684727588885)

  

而实际触发代码执行也是在红框部分，而不是在(**v15)(v15)这里。![1684727596_646ae72c7df55cadb6f38.png!small?1684727597063](https://image.3001.net/images/20230522/1684727596_646ae72c7df55cadb6f38.png!small?1684727597063)

  

样本中第二种提权方式是通过在 0x5000000 上部署函数序列 ClfsMgmtDeregisterManagedClient/RtlClearBit
来修改 PriviousMod，最后通过NtWriteVirtualMemory/ NtReadVirtualMemory实现全局内存读写。

  

## 补丁对比

补丁中主要对以下两个函数

CClfsBaseFilePersisted::WriteMetadataBlock/CClfsBaseFile::GetControlRecord进行了处理。![1684727642_646ae75a96f506d374b94.png!small?1684727643275](https://image.3001.net/images/20230522/1684727642_646ae75a96f506d374b94.png!small?1684727643275)

  

首先 CClfsBaseFile::GetControlRecord 中判断返回的 _CLFS_CONTROL_RECORD，防止返回错误的偏移导致越界读取
clfsheap。![1684727658_646ae76ac482a1ef89928.png!small?1684727659534](https://image.3001.net/images/20230522/1684727658_646ae76ac482a1ef89928.png!small?1684727659534)

  

其次 CClfsBaseFilePersisted::WriteMetadataBlock 中对返回的 v9
进行了判断，以防止越界取到攻击者构造的数据。![1684727671_646ae7772fd1d160be265.png!small?1684727671758](https://image.3001.net/images/20230522/1684727671_646ae7772fd1d160be265.png!small?1684727671758)

  

具体的判断逻辑如下所示：

![1684727679_646ae77f5d6dd57b1e035.png!small?1684727679911](https://image.3001.net/images/20230522/1684727679_646ae77f5d6dd57b1e035.png!small?1684727679911)

  

## 参考链接:

[1] https://securelist.com/nokoyawa-ransomware-attacks-with-windows-zero-day/109483/

[2] https://msrc.microsoft.com/update-guide/vulnerability/CVE-2023-28252

[3] https://www.zscaler.com/blogs/security-research/technical-analysis-windows-clfs-zero-day-vulnerability-cve-2022-37969-part

[4] https://www.zscaler.com/blogs/security-research/technical-analysis-windows-clfs-zero-day-vulnerability-cve-2022-37969-part2-exploit-analysis

  

  

