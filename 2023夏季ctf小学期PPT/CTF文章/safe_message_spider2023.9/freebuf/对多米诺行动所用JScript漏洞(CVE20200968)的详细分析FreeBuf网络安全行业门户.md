## **01** **前言**

本文是对多米诺行动(Operation
Domino)中涉及的jscript漏洞样本的详细分析，里面用到了一个之前未被公开讨论过的漏洞，通过补丁分析，笔者可以确认这个jscript漏洞出现在CVE-2020-0674双星漏洞之后，并且在2020年4月的补丁中被修复。

查询4月补丁公告可以发现，当月确实曾有一个被标注为已被利用的IE脚本引擎漏洞：CVE-2020-0968(后又被微软修改为未被利用)。

综合以上信息，笔者推断这个漏洞就是CVE-2020-0968，这份利用的出现也表明CVE-2020-0968漏洞已被利用。下面跟随笔者一起来分析一下这个漏洞。

##  **02** **漏洞成因**

jscript在处理两个对象(type=0x81)的相加操作时，CScriptRuntime::Run会连续两次调用VAR::GetValue获取对应的值，如果对象实现了自定义toString方法，VAR::GetValue内部会进一步调用NameTbl::InvokeInternal函数，这个函数可以调用自定义的toString回调。

第一次VAR::GetValue调用后会将返回结果保存到栈上的一个variant指针，开发者没有将其加入GC追踪列表，在第二个VAR::GetValue导致的toString回调中，可以手动释放相关variant，回调函数返回时，CScriptRuntime::Run会再次引用已被释放的variant指针，造成UAF。

##  **03** **PoC**

笔者构造了这个漏洞的最简poc，如下：

![](https://image.3001.net/images/20210121/1611195385_6008e3f9ed075bbcad151.png!small)

在IE中用jscript兼容模式加载上述js脚本，在第1次VAR::GetValue前后下断点，可以发现调用前后[ebp-68]处的variant指针指向的内容保存了“[L]”字符串。

![](https://image.3001.net/images/20210121/1611195574_6008e4b6d82de3baa489a.png!small)

  * 0:014> dd poi(ebp-68) L4

18db9ea0 00000082 00000000 14028c38 1402bff8

0:014> du 14028c38

14028c38 "[L]"

对0x18db9ea0的前2字节下内存访问断点，观察其type域在什么时候被更改。

第1次是在CollectGarbage函数导致的GcAlloc::SetMark阶段，GC的标志位被置位(|0x800)。

  * 0:014> g

18db9ea0 00000882 00000000 14028c38 1402bff8

# ChildEBP RetAddr

00 11c20880 14adc786 jscript!GcAlloc::SetMark+0x38

01 11c20890 14adc54b jscript!GcContext::SetMark+0x37

02 11c208b0 14adc4f1 jscript!GcContext::CollectCore+0x3b

03 11c208c0 14b0899c jscript!GcContext::Collect+0x1b

04 11c208c4 14ab2378 jscript!JsCollectGarbage+0x1c

05 11c2092c 14ac7f0e jscript!NatFncObj::Call+0xd8

06 11c209cc 14ac8275 jscript!NameTbl::InvokeInternal+0x16e

07 11c20ad0 14acb7f0 jscript!VAR::InvokeByDispID+0x95

08 11c20ca8 14ac77eb jscript!CScriptRuntime::Run+0x2e60

09 11c20d34 14afd85a jscript!ScrFncObj::PerformCall+0x3db

0a 11c20d64 14ac7fce jscript!ScrFncObj::Call+0x365da

0b 11c20e04 14ac8275 jscript!NameTbl::InvokeInternal+0x22e

0c 11c20f0c 14ae24a5 jscript!VAR::InvokeByDispID+0x95

0d 11c20f88 14ac80cc jscript!NameTbl::GetValDef+0x145

0e 11c2101c 14abb722 jscript!NameTbl::InvokeInternal+0x32c

0f 11c21064 14ac9794 jscript!VAR::GetValue+0x92

eax=00000882 ebx=0000008a ecx=18db9ea0 edx=00000010 esi=18dba000 edi=18db99b8

eip=14adc7c8 esp=11c20878 ebp=11c208b0 iopl=0 nv up ei pl nz na po nc

cs=001b ss=0023 ds=0023 es=0023 fs=003b gs=0000 efl=00000202

jscript!GcAlloc::SetMark+0x38:

14adc7c8 03ca add ecx,edx

第2次是在CollectGarbage函数导致的GcAlloc::ReclaimGarbage阶段，可以看到GC标志位在回收过程中被清除(&7ff)。

  * 0:014> g

18db9ea0 00000082 00000000 14028c38 1402bff8

# ChildEBP RetAddr

00 11c20868 14ab4445 jscript!GcAlloc::ReclaimGarbage+0xb7

01 11c2088c 14adc6fe jscript!GcContext::Reclaim+0x89

02 11c208b0 14adc4f1 jscript!GcContext::CollectCore+0x1ee

03 11c208c0 14b0899c jscript!GcContext::Collect+0x1b

04 11c208c4 14ab2378 jscript!JsCollectGarbage+0x1c

05 11c2092c 14ac7f0e jscript!NatFncObj::Call+0xd8

06 11c209cc 14ac8275 jscript!NameTbl::InvokeInternal+0x16e

07 11c20ad0 14acb7f0 jscript!VAR::InvokeByDispID+0x95

08 11c20ca8 14ac77eb jscript!CScriptRuntime::Run+0x2e60

09 11c20d34 14afd85a jscript!ScrFncObj::PerformCall+0x3db

0a 11c20d64 14ac7fce jscript!ScrFncObj::Call+0x365da

0b 11c20e04 14ac8275 jscript!NameTbl::InvokeInternal+0x22e

0c 11c20f0c 14ae24a5 jscript!VAR::InvokeByDispID+0x95

0d 11c20f88 14ac80cc jscript!NameTbl::GetValDef+0x145

0e 11c2101c 14abb722 jscript!NameTbl::InvokeInternal+0x32c

0f 11c21064 14ac9794 jscript!VAR::GetValue+0x92

eax=0000008a ebx=18dba000 ecx=00000082 edx=00000131 esi=18db9ea0 edi=000002c1

eip=14adc057 esp=11c20828 ebp=11c20868 iopl=0 nv up ei pl nz na pe nc

cs=001b ss=0023 ds=0023 es=0023 fs=003b gs=0000 efl=00000206

jscript!GcAlloc::ReclaimGarbage+0xb7:

14adc057 ba01000000 mov edx,1

第3次是在CollectGarbage函数导致的jscript!GcAlloc::ReclaimGarbage阶段，可以看到此时该变量的type域已被置为0。在jscript中，抹去type域即表明清除了该variant。

  * 0:014> g

18db9ea0 00000000 00000000 14028c38 1402bff8

# ChildEBP RetAddr

00 11c20868 14ab4445 jscript!GcAlloc::ReclaimGarbage+0x13e

01 11c2088c 14adc6fe jscript!GcContext::Reclaim+0x89

02 11c208b0 14adc4f1 jscript!GcContext::CollectCore+0x1ee

03 11c208c0 14b0899c jscript!GcContext::Collect+0x1b

04 11c208c4 14ab2378 jscript!JsCollectGarbage+0x1c

05 11c2092c 14ac7f0e jscript!NatFncObj::Call+0xd8

06 11c209cc 14ac8275 jscript!NameTbl::InvokeInternal+0x16e

07 11c20ad0 14acb7f0 jscript!VAR::InvokeByDispID+0x95

08 11c20ca8 14ac77eb jscript!CScriptRuntime::Run+0x2e60

09 11c20d34 14afd85a jscript!ScrFncObj::PerformCall+0x3db

0a 11c20d64 14ac7fce jscript!ScrFncObj::Call+0x365da

0b 11c20e04 14ac8275 jscript!NameTbl::InvokeInternal+0x22e

0c 11c20f0c 14ae24a5 jscript!VAR::InvokeByDispID+0x95

0d 11c20f88 14ac80cc jscript!NameTbl::GetValDef+0x145

0e 11c2101c 14abb722 jscript!NameTbl::InvokeInternal+0x32c

0f 11c21064 14ac9794 jscript!VAR::GetValue+0x92

eax=00000000 ebx=18dba000 ecx=00000082 edx=00000001 esi=18db9ea0 edi=000002c2

eip=14adc0de esp=11c20828 ebp=11c20868 iopl=0 nv up ei pl zr na pe nc

cs=001b ss=0023 ds=0023 es=0023 fs=003b gs=0000 efl=00000246

jscript!GcAlloc::ReclaimGarbage+0x13e:

14adc0de 8b4df4 mov ecx,dword ptr [ebp-0Ch] ss:0023:11c2085c=13ffcfe0

从上面的过程可以很明显地看到上述variant变量没有被Scavenge操作进行捡拾，这意味着它没有被加入GC追踪列表。而在第2次VAR::GetValue中可以在toString回调中调用CollectGarbage手动释放内存，回调返回后程序产生UAF崩溃：

![](https://image.3001.net/images/20210121/1611195788_6008e58cc3670c362712d.png!small)

由于jscript中GCBlock中的缓存机制，GCBlock缓存链中的GCBlock数量大于50时才会将接下来被回收的GCBlock直接释放，所以回收之前需要申请大量variant变量并进行释放来布控内存。

最终，回调前保存到栈上的0x18db9ea0指针指向的内容在toString回调中经由CollectGarbage被释放，通过递归可以生成连续被释放的variant变量：

![](https://image.3001.net/images/20210121/1611195832_6008e5b862a6d564c1309.png!small)

##  **04** **利用分析**

这个漏洞的利用手法和之前出现过的jscript UAF漏洞整体一致，但在一些细节方面又有所不同。

整体来说，这份漏洞利用依旧是通过漏洞泄露一个RegExpObj的指针，随后借助RegExpObj，构造一个可以越界读取的BSTR。具备越界读取能力后，将整个RegExpObj的内存读入一个数组并对相关成员进行修改，目的是将精心设计的RegExpExec替换为RegExpObj原有的RegExpExec，随后转换得到一个伪造的RegExpObj，并在伪造的RegExpObj基础上实现任意地址写原语，然后借助任意地址写和伪造的RegExpObj内的成员域实现任意地址读。具备任意地址读写能力后，利用代码泄露一个jscript模块内的指针，获得jscript模块基址，然后通过IAT查找得到kernel32模块的一个地址，进一步得到kernel32的基地址，接着从kernel32的EAT中查找得到VirtualProtect等功能函数，泄露Native栈的一个指针，覆盖栈上的返回地址，实现代码执行。

原始的漏洞利用样本经过混淆，笔者对其进行了解混淆，为便于读者理解，以下的分析所涉及代码是笔者解混淆后的版本。

##  **05** **与之前的jscript漏洞利用的不同之处**

与之前出现过的jscript UAF漏洞利用代码的差异处在本次泄露RegExpObj指针的方式，下面跟随笔者一起来看一下。

![](https://image.3001.net/images/20210121/1611195857_6008e5d1e27f96908e93f.png!small)

从上面的poc分析可知，被释放的variant是func1的toString回调完成后，保存到栈上的variant。但如何索引这些variant呢？利用代码采取的方式是将两个对象相加的结果保存到一个str变量，随后将其保存到nrefs数组，最终是通过对nrefs数组的遍历找到被重用的variant，从而泄露一个RegExpObj指针。

笔者在内存中对每次调用typeof传入的variant进行了输出，可以看到nrefs数组中保存的variant类型有object、string和其他类型，值得注意的是最后位于0xaba0b90处的variant，这是一个string类型的variant，其+8处存储了一个BSTR指针，这个BSTR保存着一个十进制数组字符串，将该字符串转为为16进制后可以看到是一个内存地址0xabf7360：

![](https://image.3001.net/images/20210121/1611195877_6008e5e5e1968da6095d7.png!small)

而该0xabf7360c正是一个RegExpObj指针：

![](https://image.3001.net/images/20210121/1611195896_6008e5f8a7bda303843f9.png!small)

笔者同时下断点打印出了VAR::GetValue阶段每次导致的悬垂指针地址，重点关注0xab9c458这个variant指针：

![](https://image.3001.net/images/20210121/1611195912_6008e6089abb7bb123369.png!small)

利用代码第1次对UAF占位所用的字符串如下：

![](https://image.3001.net/images/20210121/1611195926_6008e616b546a5789cb7f.png!small)

并在obj2的回调函数中进行占位：

![](https://image.3001.net/images/20210121/1611195954_6008e632ca70eea28f458.png!small)

在第1次占位之后，悬垂指针0xab9c458处的内存已被重用：

![](https://image.3001.net/images/20210121/1611195970_6008e6422eaa9fa50ab44.png!small)

可以看到第1次内存重用后将一个RegExp对象的type改为了number(3)，此处保存的正好对应上面nrefs数组其中某个variant保存的字符串内容：

![](https://image.3001.net/images/20210121/1611195985_6008e6515347ecf7b6cec.png!small)

递归结束后，通过以下代码从nrefs数组中解析出被泄露的RegExpObj指针，将RegExpObj+2传入第2次占位的字符串，目的是为了再次进行UAF构造超长BSTR。

![](https://image.3001.net/images/20210121/1611196000_6008e660a5742037feb6c.png!small)

后续利用过程和之前出现的几个jscript UAF漏洞利用完全一致，本文不再重复描述，感兴趣的读者可以阅读笔者之前的一篇文章《谈谈两年来的4个Jscript
ITW 0day》中的“CVE-2019-1367利用代码分析”部分。

最终，利用代码覆盖Native栈上的一个返回地址劫持了控制流，实现了ShellCode执行：

![](https://image.3001.net/images/20210121/1611196016_6008e67078d3a3a4ece38.png!small)

 **参考链接**

> https://bbs.pediy.com/thread-261581.htm

