**作者：360 Core Security  
博客：[http://blogs.360.cn/post/VBScript_vul_CH.html?from=timeline&isappinstalled=0](http://blogs.360.cn/post/VBScript_vul_CH.html?from=timeline&isappinstalled=0)**

### 前言

近日，360核心安全事业部高级威胁应对团队又发现若干vbscript漏洞的在野利用。其中包括CVE-2016-0189、CVE-2018-8373和另一个此前不为人所知的漏洞(我们暂未确定它的cve编号)。这三个漏洞，加上我们在今年4月发现的CVE-2018-8174，一共是4个vbscript在野利用。经过分析，我们发现这4个文件的混淆和利用手法都高度一致，我们怀疑背后有一个写手(或团队)，一直在开发vbscript的0day利用并用于攻击。

如下为我们抓到的4个漏洞的在野利用：

![
](https://images.seebug.org/content/images/2018/11/6535e7b4-71ee-425d-bdc9-479d74a02397.png-w331s)

### 被遗漏的0day？

由于其他三个漏洞都已出现过分析文章，本文我们将重点分析未被公开过的第四个vbscript 0day。

该漏洞利用一直隐藏得非常隐蔽，我们发现该漏洞在2017年3月更新中被修复，微软修复时没有提到该漏洞被利用，我们推测这个漏洞可能是微软并未发现利用而修复。可以定位到的最后一个可以触发该漏洞的版本是
vbscript.dll 5.8.9600.18538，在vbscript.dll 5.8.9600.18616
中，该漏洞被修复。有意思的是，我们发现相关利用的出现时间早于2017年3月，这也意味着该漏洞在当时是一个0day。遗憾的是，我们并未找到其他厂商对该漏洞的分析文章。

下面我们将和大家分享该漏洞的成因和利用方式。

### 漏洞分析

#### 概述

这个漏洞位于vbscript!rtJoin函数。当执行vbscript的join语句时，VbsJoin函数会调用rtJoin，rtJoin首先遍历传入的数组中的每个元素，并计算拼接后的字符串总长度(包括拼接字符，默认为unicode空格0x0020)。然后调用SysAllocStringLen分配相应的空间，用于保存拼接后的字符串。

实际分配的空间大小 = (要分配的字节数 + 0x15) & 0xfffffff0
(参见oleaut32!SysAllocStringLen及oleaut32!CbSysStringSize的实现)

字符串起始地址前4字节为字符串的字节长度(参见BSTR结构)。上述整个过程的伪代码如下所示：

![
](https://images.seebug.org/content/images/2018/11/26001cee-41a3-4706-868e-4cb007e4994d.png-w331s)

相应的栈回溯如下：

![
](https://images.seebug.org/content/images/2018/11/8ef3921e-15e6-4c9a-8c73-f92c2dbb7465.png-w331s)

随后解析流程会逐个拷贝字符串到新分配的空间，这个过程中会使用保存在栈上的字符串地址获取每个字符串的长度，以作为memcpy的size参数。当数组元素里面有类对象时，会触发类对象的Default
Property
Get回调获取默认属性，在回调中可以对数组中的其他成员进行操作，例如更改字符串大小。只要精确控制更改前后的字符串大小，通过(下图中第一个)memcpy拷贝的数据大小就有可能超出前面由SysAllocStringLen分配的空间，从而导致堆溢出。上述整个过程的伪代码如下所示：

![
](https://images.seebug.org/content/images/2018/11/35861c28-bb98-4356-8ac2-d19f499995f0.png-w331s)

PoC 我们构造了一个该漏洞的poc，供研究人员分析使用：

![
](https://images.seebug.org/content/images/2018/11/d3f93d54-c1ad-4e7f-a91b-809bab4e82d7.png-w331s)

#### 代码分析

##### 内存布局

原利用代码首先进行内存布局(prepare)，然后第一次利用漏洞(exp_1)，覆盖一个BSTR对象的长度域，得到一个超长BSTR对象，并借助该BSTR去获取一块之前准备好的内存地址；成功后，再次利用漏洞(exp_2)去覆盖一个伪造的字符串的对象类型为数组(200c)，从而得到一个数据起始地址为0，元素大小为1，元素个数为0x7fffffff的超长一维数组。

随后借助第一次获得的内存地址和第二次获得的超长数组实现任意地址读取，后续的利用方式和之前被披露的细节基本一致。

![
](https://images.seebug.org/content/images/2018/11/83ad38cc-1631-4381-b6ab-7841093478d3.png-w331s)

prepare上半部分代码如下图所示。

![
](https://images.seebug.org/content/images/2018/11/5e2576a7-c271-4d90-845d-8e3325f4cef2.png-w331s)

在这部分代码中，str_h的字符串长度为0x4fec字节，SysAllocStringLen实际分配的空间为0x5000字节((0x4fec+0x15) &
0xfffffff0 =
0x5000)，str_o的字符串长度为0x4ff6字节，SysAllocStringLen实际分配的空间为0x5000字节((0x4ff6+0x15) &
0xfffffff0 = 0x5000)。array_a和array_b是2个数组，每个数组的实际数据区域占的空间为0xa00*0x10 =
0xa000字节(每个元素为一个VAR结构体)。

需要注意的是，0x4fec2 + 0x18 + 0x22 = 0x9ff4，(0x9ff4+0x15) & 0xfffffff0 = 0xa000,
这些值在下文会提到。

prepare下半部分如下图所示。

![
](https://images.seebug.org/content/images/2018/11/8e8446be-62a6-433f-bdf3-51f725607dc2.png-w331s)

str_left_0大小为0x4ffa字节(get_left_str_a_by_size会将传入的参数减6字节)，SysAllocStringLen分配的空间为0x5000字节((0x4ffa
+ 0x15) & 0xfffffff0 = 0x5000)；
str_left_1大小为0x9ffa字节，SysAllocStringLen分配的空间为0xa000字节((0x9ffa + 0x15) &
0xfffffff0 = 0x5000)。

随后将array2数组的每一个元素都赋值为str_left_1(实际内存大小为0xa000)，将array3数组的每一个元素都赋值为实际内存大小为0xa000的array_b(见上文)。

到这里内存布局便完成了，之后只要先将array2(在exp_1中操作)或array3(在exp_2中操作)的部分元素进行释放，就会有大量0xa000的内存空洞，此时立即申请0xa000字节大小就有可能对释放的内存进行重用。

只要保证rtJoin函数中的SysAllocStringLen申请的大小为0xa000字节，结合上述漏洞就可实现对array2某个str_left_1对象或array3数组中某个array_b对象的数据覆盖，这些会在后面详细描述。

##### 改写BSTR长度

在exp_1中，第一次触发漏洞，改写一个BSTR对象的长度为0xfffffffe。

首先给array_c第1个和第2个元素赋值为str_h(字符串长度为0x4fec字节，实际占用的空间为0x5000字节，见上文)，给第3个元素赋值为class_a的对象，而class_a的Default
Property Get会返回一个长度为0x18字节的长度(0x1a-0x6+0x4 =
0x18),这样array的三个元素加上分隔字符拼接后占用的长度为0x9ff4(0x4fec+0x4fec+0x18+0x2+0x2 = 0x9ff4)

![
](https://images.seebug.org/content/images/2018/11/517acd7d-6ef3-43e3-8235-8beabb3d31bb.png-w331s)

在触发漏洞前先调用make_hole_of_array2前释放array2中的一半元素，以生成足够的大小为0xa000的内存空洞。

![
](https://images.seebug.org/content/images/2018/11/035ff7f1-9892-41fb-822e-cb615c491126.png-w331s)

make_hole_of_array2调用前后后对应的内存布局如下，可以发现array2中一半字符串内存均被释放，对于下标在0x00-0x7F区间内的元素，偶数部分被释放；对于下标在0x80-0xFF区间的元素，奇数部分被释放：

![
](https://images.seebug.org/content/images/2018/11/5c2c876b-cb79-4e92-8bf7-41dd07ba5e42.png-w331s)

随后在rtJoin中的SysAllocStringLen会申请分配一个总长度为0xa000字节的BSTR((0x9ff4 + 0x15) &
0xfffffff0 = 0xa000)。由于windows的堆分配算法，该内存会从上图右边的空闲堆块中重用一个。

在class的Default Property
Get中，先释放array_c的第1、2个元素(设为Nothing)，并立即将它们赋值为str_o(字符串长度为0x4ff6字节，实际占用的空间为0x5000字节)。

![
](https://images.seebug.org/content/images/2018/11/86182b9c-65e5-4e02-a30e-1ce8036f70bd.png-w331s)

这里需要注意两点:

  1. 2次赋值为str_o的操作会重用刚释放的2个0x5000内存块(即原先两个str_h占据的内存)。
  2. 重用后，相同地址处的字符串长度和内容发生了变化(一开始是str_h，长度为0x4fec字节，现在是str_o，长度为0x4ff6)，所以在rtJoin中进行memcpy前重新获取的字符串长度分别为0x4ff6，0x4ff6，0x18，再加上2次分隔字符的大小0x4，memcpy总共复制的数据长度为0xa008，相比0x9ff4字节多出了0x14字节，多出的字节中的最后4字节则会覆盖array2中相邻str_left_1对象的长度域，在利用代码中，攻击者将原str_left_1的长度覆写为了0xfffffffe。

错位过程如下图所示：

![
](https://images.seebug.org/content/images/2018/11/0052d9b1-f7de-4488-92bc-947a5c0956a7.png-w331s)

随后，借助超长字符串获取前面准备的字符串地址，用于后续使用。

![
](https://images.seebug.org/content/images/2018/11/d3193e17-842c-4051-9eed-9e0ce7c3b602.png-w331s)

下图为在prepare中准备的字符串：

![
](https://images.seebug.org/content/images/2018/11/e1acb337-eb3a-4e02-b9e5-74fbedc4826b.png-w331s)

##### 构造超长数组

在exp_2中，第二次触发漏洞，将fake_array对应字符串的类型改为0x200c，方法同覆盖字符串长度一致，此处不再重复描述。

![
](https://images.seebug.org/content/images/2018/11/20d41e8a-8f32-4a0d-adff-3788bcf78763.png-w331s)

fake_array是个字符串，它实际为一份伪造的tagSAFEARRAY结构。

![
](https://images.seebug.org/content/images/2018/11/f746967d-12b6-4b0e-9cbe-3791cdeb7de8.png-w331s)

以下为寻找类型混淆后的超长数组，用于后面使用：

![
](https://images.seebug.org/content/images/2018/11/9f8a3170-1346-4fe5-8cdc-438ba895ea53.png-w331s)

##### 任意地址读

随后样本借助前面获得的字符串地址和超长数组封装了一组任意地址读取的功能函数，供后面使用。

![ ](https://images.seebug.org/content/images/2018/11/50ff41c4-1fd6-42da-aaba-08a27dde1995.png-w331s)

##### 构造辅助函数

具备了任意地址读取能力后，利用封装了若干辅助函数：

![
](https://images.seebug.org/content/images/2018/11/0c788e9c-99d9-4d41-9aba-0d046c92395e.png-w331s)

随后通过以下方式泄露CScriptEntryPoint对象的虚表地址

![
](https://images.seebug.org/content/images/2018/11/f1cb10c6-6076-4f0e-948c-1e92e2b5e9e4.png-w331s)

随后借助封装好的辅助函数获取vbscript.dll基地址，再通过遍历vbscript.dll导入表获取msvcrt.dll基地址,
msvcrt.dll又引入了kernelbase.dll、ntdll.dll，最后获取了NtContinue、VirtualProtect等函数地址，整个过程如下：

![
](https://images.seebug.org/content/images/2018/11/2d15db44-1349-4b91-92a3-1f2b49d7a980.png-w331s)

##### 执行shellcode

原利用代码在windows 7和windows 8环境中，执行shellcode的方式与之前CVE-2018-8174相同。在windows
8.1和windows 10环境中所用的方式与低版本系统中略有不同。

#### 动态调试

##### 内存布局

prepare函数中内存布局完成后array2、array3和array_c的pvData分别如下所示。

![
](https://images.seebug.org/content/images/2018/11/9b681830-f82f-4910-a0b0-5740cd1690da.png-w331s)
![
](https://images.seebug.org/content/images/2018/11/4117acc0-0a50-4def-b1e4-6ca064dd8088.png-w331s)
![
](https://images.seebug.org/content/images/2018/11/24a4682e-c44b-46a8-a7fc-8eb0486a31bf.png-w331s)

##### 内存重用

首先是Public Default Property Get回调中str_o字符串对str_h字符串内存的重用。重用后整体内存大小不变，字符串长度发生变化。

![
](https://images.seebug.org/content/images/2018/11/9e4c88f5-0227-4a37-b103-12a88613f8be.png-w331s)

然后是SysAllocStringLen申请0xa000大小内存时对array2中某个被释放的0xa000字符串的重用。从下图中可以看到，第一次触发漏洞前重用的内存是刚被释放的array2(0x81)。随后array2(0x82)对应字符串的长度将被覆写。

![
](https://images.seebug.org/content/images/2018/11/931cdead-3ca5-4cdf-8ebc-b343ee75a4f8.png-w331s)

##### 改写BSTR长度

在exp_1中第一次触发漏洞，改写某个str_left_1字符串的长度域。

![
](https://images.seebug.org/content/images/2018/11/10b29165-84f3-40df-93e3-1dc91f7b13ce.png-w331s)

##### 构造超长数组

在exp_2中再次进行内存重用，此时的SysAllocStringLen申请的0xa000内存重用的是array3(0x81)刚释放的内存(释放方式与array2相同)，随后array3(0x82)相关内存的首部将被改写。

![
](https://images.seebug.org/content/images/2018/11/879c421b-2280-4bf1-aef5-488339a3375b.png-w331s)

第二次触发漏洞，将精心准备的fake_array字符串的type由0008改写为200c，从而得到一个超长一维数组。

![
](https://images.seebug.org/content/images/2018/11/822a4673-deea-4add-99f6-a89137e2da65.png-w331s)

##### 执行shellcode

在windows 7和windows 8下的shellcode执行细节可参考我们之前写的CVE-2018-8174分析文章。 在window
8.1和windows 10环境中，样本用了一些其他技巧来Bypass CFG(在我们的测试中，该方式可以在早期版本的windows 8.1和windows
10中成功)。关于这部分的更多细节，我们会在后面的文章中进行披露。

### 补丁分析

以下是补丁前后Bindiff工具的比对结果。

![
](https://images.seebug.org/content/images/2018/11/795e097f-fc2d-4a41-9179-04a0c8675885.png-w331s)

可以看到，补丁文件中在拷贝每个数组元素到join_list之前，会先通过SysAllocString将字符串数据保存一份，这样即使在后面回调中更改了初始的字符串长度，在执行memcpy进行内存拷贝时也会使用SysAllocString函数拷贝的那份数据，从而使SysAllocStringLen申请的内存大小和memcpy拷贝的数据大小相同，从而修复了漏洞。

### 与APT-C-06的关联分析

我们对四个vbscript漏洞的shellcode进行了关联分析，我们发现cve-2016-0189、本次漏洞和cve-2018-8174所用的shellcode除配置的CC外基本一致，cve-2018-8373的shellcode略有不同，但也非常相似。我们推测本次漏洞也是APT-C-06(又名Darkhotel)武器库中的一个。

### 福利

读者有没有发现rtJoin函数中还存在一处整数溢出点，如下：

![
](https://images.seebug.org/content/images/2018/11/009fe51a-573b-4e08-b431-fb75200cb6b0.png-w331s)

我们查找了vbscript里面join系列函数相关的整数溢出漏洞，发现有一个漏洞是CVE-2017-11869，我们对该漏洞修复前后的vbscript.dll做了一次补丁比对，并且发现了一些有意思的修改点，如下：

![
](https://images.seebug.org/content/images/2018/11/2a287fe6-c701-48bb-96f8-3f3d1d3f8ea9.png-w331s)

有兴趣的读者可以深入研究一下CVE-2017-11869。

### 结论

本文我们分享了本年度发现的第三个vbscript的漏洞细节，其利用手法和之前几个同样精彩。我们相信vbscript里面还有其他类似问题，同时推测相关开发团伙手上还有其他类似的漏洞利用，请广大用户提高警惕。

### 参考链接

<http://blogs.360.cn/post/cve-2018-8174.html>

<https://www.zerodayinitiative.com/advisories/ZDI-17-916/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/743/>

