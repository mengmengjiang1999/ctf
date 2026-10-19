2021年4月12日，开源浏览器内核Chromium的一处改动提交[1]引起了关注。这是Chromium
Javascript引擎v8的一处漏洞bugfix。同时针对该bugfix的回归测试样本regress-1196683.js也被提交。基于该回归测试，有安全研究员公布了完整的利用代码。由于Chromium开发流程，该漏洞于4月13日Chrome的release版中才被修复[2]。无独有偶，4月15日Chromium代码仓库另一处改动提交[3]也包含了回归测试样本regress-1195777.js。基于该样本，完整的利用代码再次被公布。由于最新的Chrome
release版没有引入该bugfix，利用代码仍可以在最新的Chrome浏览器的渲染进程稳定利用。当受影响版本的Chormium内核浏览器在没有开启沙箱的情况下（--no-sandbox），访问攻击者构造的恶意链接时，将会触发该漏洞，造成远程代码执行。

##  ** **I**** ** **ssue 1196683**** ** **原理分析****

该issue的bugfix代码如下：

![](https://image.3001.net/images/20210421/1618986870_607fc776454c074efc725.png!small)

bugfix修复了v8
TurboFan在指令选择阶段针对ChangeInt32ToInt64节点的指令选择错误问题。改动前根据ChangeInt32ToInt64节点的输入节点类型选择指令。如果输入节点类型为有符号整数，则选择指令X64Movsxlq先做符号扩展，否则选择X64Movl做零扩展。Bugfix后则无论输入类型，一律选择X64Movsxlq做符号扩展。根据修复代码可以猜测，这里应该是ChangeInt32ToInt64节点输入类型为无符号整数，导致指令选择阶段错误选择X64Movl指令引发的安全问题。

首先通过regress-1196683.js分析漏洞根因：

![](https://image.3001.net/images/20210421/1618986886_607fc786217ca6fce3920.png!small)

触发JIT的foo函数只有一行代码，重点关注 (arr[0] ^ 0) + 1在TurboFan中关键阶段的优化过程：

###  ** **1) TyperPhase****

![](https://image.3001.net/images/20210421/1618986900_607fc794bf2d2c8f56d5e.png!small)

异或操作符对应32节点，其两个输入分别为常量0（24节点）和arr[0]（80节点）。

###  ** **2) SimplifiedLoweringPhase****

![](https://image.3001.net/images/20210421/1618986915_607fc7a3d8bf996d98c4a.png!small)

原32节点SpeculativeNumberBitwiseXor被优化成Word32Xor，并加入后继节点ChangeInt32ToInt64。此时ChangeInt32ToInt64节点的输入节点Word32Xor类型为Signed32。

###  ** **3) EarlyOptimizationPhase****

![](https://image.3001.net/images/20210421/1618986931_607fc7b3ae7d6356968fe.png!small)

可以看到原32节点被删除，并用80节点替代作为110节点ChangeInt32ToInt64的输入。此时ChangeInt32ToInt64节点的输入节点LoadTypedElement类型为
** **U**** ** **ns**** ** **igned**** ** **32**** 。

这段逻辑对应的v8代码如下：

![](https://image.3001.net/images/20210421/1618986950_607fc7c6549b36188f5f5.png!small)

如上所示，对于x ^ 0 => x的情况，使用左节点替换当前节点，从而引入了错误的数据类型。

###  ** **4) InstructionSelectionPhase****

根据前面的分析，指令选择阶段，ChangeInt32ToInt64节点的输入节点LoadTypedElement类型为Unsigned32，最终选择X64Movl指令替换ChangeInt32ToInt64节点：

![](https://image.3001.net/images/20210421/1618986967_607fc7d709af3f9217514.png!small)

因为错误选择了零扩展指令X64Movl，导致(arr[0] ^ 0)返回错误的值：0x0000000080000000。

最终利用该漏洞，通过如下代码可以得到一个JIT中非预期值为1的变量x（预期值应为0）：

![](https://image.3001.net/images/20210421/1618986985_607fc7e9ecc88c92eb62c.png!small)

##  ** **2**** ** **.**** ** **I**** ** **ssue 1195777**** ** **原理分析****

该issue的bugfix代码如下：

![](https://image.3001.net/images/20210421/1618987010_607fc802adfb16b014c04.png!small)

bugfix修复了v8
TurboFan在SimplifiedLowering阶段，对64位整数转为32位整数的数据类型转换节点生成错误的问题。改动前对于当前节点的输出类型为Signed32或Unsigned32均生成TruncateInt64ToInt32节点（截断）；改动后，对于当前节点的输出类型为Unsigned32的情况，还需要检查use_info的类型，只有在use_info.type_check()
== TypeCheckKind::kNone的情况下，才会生成TruncateInt64ToInt32节点。

首先通过regress- 1195777.js分析漏洞根因：

![](https://image.3001.net/images/20210421/1618987025_607fc81134e7a2a23ee47.png!small)

触发JIT的foo函数中关键代码为return -1 < Math.max(0, x, -1)。重点关注 Math.max(0, x,
-1)在TurboFan中关键阶段的优化过程：

###  ** **1) TyperPhase****

![](https://image.3001.net/images/20210421/1618987038_607fc81e01a791676ed41.png!small)

Math.max(0, x, -1)对应了56，58节点，58节点输出作为41节点SpeculativeNumberLessThan（<）的输入。

###  ** **2) TypedLoweringPhase****

![](https://image.3001.net/images/20210421/1618987057_607fc831652098a4caf3d.png!small)

Math.max(0, x, -1)两个常量参数0，-1（54，55节点）被替换成了常量节点32和14。

###  ** **3) SimplifiedLoweringPhase****

![](https://image.3001.net/images/20210421/1618987074_607fc8429b0b31eef6244.png!small)

原56，58的NumberMax节点，被Int64LessThan +
Select节点替换；原41节点SpeculativeNumberLessThan被替换为Int32LessThan。在处理SpeculativeNumberLessThan输入节点的时候，因为输入节点（Select）的输出类型为Unsigned32，从而触发漏洞，导致76节点TruncateInt64ToInt32被错误生成。从而将Math.max(0,
x, -1)的结果截断为Signed32。因此，当Math.max(0, x,
-1)中的x为Unsigned32时，会被TruncateInt64ToInt32错误截断为Signed32。

最终利用该漏洞，通过如下代码可以得到一个JIT中非预期值为1的变量x（预期值应为0）：

![](https://image.3001.net/images/20210421/1618987091_607fc85344dda24dc0ae0.png!small)

##  ** **3\. 漏洞利用分析****

根据上面对这两个漏洞的分析可以知道：这两个漏洞是TurboFan在做整型数据类型转换（扩展、截断）时发生的错误。利用这两个漏洞，通过如下代码可以得到一个JIT中非预期值为1的变量x。接下来根据在野利用样本[4][5]，分析如何根据这个错误数值为1的变量x，实现远程代码执行。

具体利用步骤为：

 ** **1**** ** **）借助这个错误数值为1的变量x，构造一个长度为**** ** **1**** ** **的Array；****

 ** **2**** ** **）通过Array**** ** **.prototype.shift()**** ** **获得一个长度为0x****
** **FFFFFFFF**** ** **的越界数组；****

关键代码如下：

![](https://image.3001.net/images/20210421/1618987113_607fc8696cc5146197cdc.png!small)

其中var arr = new Array(x);对应的JIT代码：

![](https://image.3001.net/images/20210421/1618987134_607fc87eec2f8cf64e1ff.png!small)

这里rdi为数组的长度，即x的值1。指针压缩后，左移一位（rdi+rdi），存放在JSArray.length属性（+0xC）。

arr.shift();对应的JIT代码：

![](https://image.3001.net/images/20210421/1618987150_607fc88e35f36921af059.png!small)

这里可以看到，arr.shift()后，数组的长度直接由常量0xFFFFFFFE赋值，其优化过程：

（1）TyperPhase![](https://image.3001.net/images/20210421/1618987165_607fc89d4351d7d27b771.png!small)

这里数组长度赋值操作主要由152，153节点组成。其中152节点做Array.length-1计算操作。153节点将计算结果保存在Array.length（+0xC）处。

（2）LoadEliminationPhase![](https://image.3001.net/images/20210421/1618987178_607fc8aa1b22e2763583c.png!small)

这里可以看到，由于在Ignition执行过程中收集的x值为0，这里做了常量折叠（0-1=-1），从而得到常量0xFFFFFFFF。左移一位后为0xFFFFFFFE，存放在Array.length（+0xC）处。从而得到一个长度为0xFFFFFFFF的越界数组。

得到越界数组后，后面的利用方法就比较通用了，一般为：

 ** **3**** ** **）借助这个越界数组，实现**** ** **addrof/fakeobj**** ** **；****

 ** **4**** ** **）借助**** ** **addrof/fakeobj**** ** **，伪造一个**** **
**JSArray**** ** **，实现任意地址读写；****

样本中利用arr和cor实现任意地址读写的内存布局为：

 **
**![](https://image.3001.net/images/20210421/1618987191_607fc8b7e5faa35712f5e.png!small)****

（1）首先利用漏洞获得一个长度为0xFFFFFFFF的arr（红框）

（2）利用越界的arr和cor实现addrof/fakeobj（绿框）

（3）利用越界的arr修改cor的长度（黄框）

（4）利用越界的cor，泄露cor的map和properties属性（蓝框），构造一个fake JSArray，借助这个fake
JSArray实现任意地址读写

 ** **5**** ** **）借助**** ** **WebAssembly**** ** **执行shell**** ** **code****
** **；****

最后借助WebAssembly创建一个RWX属性的内存页，拷贝shellcode至该内存页，执行shellcode。

完整的利用演示：

![](https://image.3001.net/images/20210421/1618987207_607fc8c7ed5204050b717.png!small)

##  ** **4**** ** **.**** ** **结论****

经分析，这两个v8
JIT的漏洞触发容易且利用简单，在没有开启沙箱的Chromium内核浏览器中可以稳定利用。考虑到这两个漏洞只是Chromium内核浏览器渲染进程的远程代码执行漏洞，无法穿透浏览器沙箱（默认开启），建议用户不要关闭Chromium内核浏览器的沙箱，且不要点击不明链接。

##  ** **5**** ** **.**** ** **参考**** ** **链接****

[1] https://chromium-review.googlesource.com/c/v8/v8/+/2820971

[2] https://chromereleases.googleblog.com/2021/04/stable-channel-update-for-desktop.html

[3] https://chromium-review.googlesource.com/c/v8/v8/+/2826114

[4] https://github.com/r4j0x00/exploits/blob/master/chrome-0day/exploit.js

[5] https://github.com/avboy1337/1195777-chrome0day/blob/main/1195777.html

