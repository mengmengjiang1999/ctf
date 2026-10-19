***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、前言

 **CVE-2017-11826 据说是 360 在 2017 年 9 月底发现的一个关于 XML 格式解析的一个漏洞，之后微软在 10 月份发布了关于
CVE-2017-11826 的补丁。** **该漏洞的成因是由于在解析闭合元素时，没有对元素的完整性做出判断，导致将当前元素的嵌套关系加上 1。这样的话
wwlib 模块在处理闭合标签时，会错误的使用父级元素 w:name 属性 +44 的地址进行虚函数调用，攻击者通过修改 w:name
属性，就可以进行任意地址调用。**

![](https://image.3001.net/images/20190808/15652564738980.jpeg!small)

受影响的 Office 版本。

![](https://image.3001.net/images/20190729/1564393835_5d3ec16be548f.png!small)

## 二、调试环境

操作系统：Windows 7 + VMware

调试工具：x64dbg

漏洞样本：POC

补丁地址：<https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-11826>

## 三、调试分析

从 GitHub 上下载关于 CVE-2017-11826 漏洞的文件夹，解压后发现包括解压过的 docx 文件、README
文件、俄文文档，俄文文档没有仔细看，好像是关于漏洞利用的。

![](https://image.3001.net/images/20190729/1564393941_5d3ec1d5bed2a.png!small)

包含漏洞的 XML 文件为 document.xml，文件在 `word` 路径下。打开 document.xml 文件，分析后发现 <w:font>
标签使用了 </o:idmap> 标签进行闭合，而 <w:font> 标签的 w:name 属性有点奇怪，可能是用于控制某一个地址的值。

![](https://image.3001.net/images/20190729/1564393958_5d3ec1e66228b.png!small)

将解压过的 docx文档重新压缩，之后使用注册表附加调试器准备调试。

![](https://image.3001.net/images/20190729/1564393968_5d3ec1f01aba5.png!small)

附加完成之后打开含有漏洞的文档，运行后触发异常，其中 call [ecx+4] 指令是利用虚函数表调用虚函数，而 ecx 为虚函数表指针，通过
wwlib.41249DA0 函数返回。

![](https://image.3001.net/images/20190729/1564393988_5d3ec2046067d.png!small)

查看堆栈调用，发现用于处理 XML 格式的 msxml 模块，msxml 模块通过间接调用 wwlib 模块去协助解析 XML 格式。暂且将
wwlib.3161309E 函数定为漏洞函数。

![](https://image.3001.net/images/20190729/1564393999_5d3ec20f2f6e9.png!small)

对漏洞函数下记录断点后查看日志内容，发现漏洞函数被调用了 6 次，结合 document.xml
文件中的标签元素分析漏洞函数很有可能是用于解析元素标签的，至于解析的是什么，目前还不清楚。

![](https://image.3001.net/images/20190729/1564394019_5d3ec22322368.png!small)

![](https://image.3001.net/images/20190729/1564394033_5d3ec231ba923.png!small)

选取最后一次调用漏洞函数的 esp 下条件断点，分析漏洞函数处理流程。

![](https://image.3001.net/images/20190729/1564394051_5d3ec243c090b.png!small)

函数断下后从传入的参数可以发现，esi 可能是储存标签信息的数据结构。

![](https://image.3001.net/images/20190729/1564394068_5d3ec2540515d.png!small)

单步进入该函数，在如图所示的位置会取出元素的嵌套关系，此时 <o:idmap> 标签已经插到了 <w:font> 标签的后面（以 ":" 符号为分隔符）。而
<w:font> 标签在未闭合的情况插入了 <o:idmap> 标签，说明嵌套关系已经被错误的解析。

![](https://image.3001.net/images/20190729/1564394086_5d3ec2664d67b.png!small)

调试到 0x31613084 地址时发现会调用 wwlib.31249DA0
函数，经过分析后发现该函数的返回值和异常处的虚函数表调用有关，所以进入这个函数看看。

![](https://image.3001.net/images/20190729/1564394112_5d3ec280d13a8.png!small)

通过分析发现该函数对 ecx 和 edx 做了一些简单的计算，算法为[[ecx]+8]*edx + [[ecx]+C] + [ecx]，计算结果为
0x0751D140；而 ecx 是由 esi 传入，edx 又等于[[esi]]，所以算法变为[[esi]+8]*([[esi]]-2) +
[[esi]+C] + [esi]，由传入的 esi 控制，经过后面的分析可以得出[[esi]]其实就是当前元素的嵌套等级。

![](https://image.3001.net/images/20190729/1564394131_5d3ec2933e51b.png!small)

调用完 wwlib.31249DA0
后会将[[0x0751D140+44]+44]地址的值作为虚函数表指针进行虚函数调用，进而触发异常。如图所示可以看出[0x0751D140+44]地址被覆盖成了
<w:font> 元素的 w:name 属性，所以攻击者通过修改 <w:font> 标签的 w:name 属性就可以做到调用任意地址。

![](https://image.3001.net/images/20190729/1564394318_5d3ec34ed908a.png!small)

![](https://image.3001.net/images/20190729/1564394375_5d3ec38747677.png!small)

接下来更改样本中的 document.xml 文件，手动添加 </w:font> 闭合标签，看看是否会触发异常。

![](https://image.3001.net/images/20190729/1564394477_5d3ec3ede6b50.png!small)

在漏洞函数处断下，这时的嵌套等级为 5。

![](https://image.3001.net/images/20190729/1564394502_5d3ec406711d0.png!small)

之后通过 wwlib.31249DA0 计算虚函数调用地址为 0x075098F4。由于嵌套等级为 5，所以计算出的结果为 F4（4C*(5 - 2) +
10），之前的为 140（4C*(6 - 2) + 10）。由于嵌套等级由 5 变为 6，导致计算结果出现偏差。

![](https://image.3001.net/images/20190729/1564394556_5d3ec43c01d15.png!small)

虚函数调用后程序并没有触发异常。

![](https://image.3001.net/images/20190729/1564394584_5d3ec4582d294.png!small)

## 四、分析 msxml 模块处理步骤

为了快速了解 msxml 模块的处理流程，对调用堆栈中的所有 msxml 模块函数下记录断点，查看日志。

![](https://image.3001.net/images/20190729/1564394636_5d3ec48c7334a.png!small)

从日志中可以发现漏洞函数的调用都是通过 sub_78887830 函数中的 call [ebx+200]
的指令实现的，但是倒数第二个漏洞函数的调用却没有经过 call [ebx+200] 而是直接跳到了 MSO 模块。

![](https://image.3001.net/images/20190729/1564394652_5d3ec49c4ff4e.png!small)

对倒数第二个漏洞函数下断点。断下后分析堆栈调用，发现 msxml.78887830 函数中的 call [ecx+20] 的指令也会调用漏洞函数。

![](https://image.3001.net/images/20190729/1564394733_5d3ec4edaf38a.png!small)

![](https://image.3001.net/images/20190729/1564399584_5d3ed7e0c5475.png!small)

这样的话函数调用流程图就能分析出来了，函数调用流程如下图所示：

![](https://image.3001.net/images/20190729/1564399596_5d3ed7ecc965f.png!small)

下面根据 msxml.78887830 函数的最后一次调用，简单分析 call [ebx+200] 下的函数链调用。

![](https://image.3001.net/images/20190729/1564399610_5d3ed7fa4acd8.png!small)

![](https://image.3001.net/images/20190729/1564399634_5d3ed81259d8c.png!small)

在 msxml.78887830 函数开头会将元素标签对象储存在 ebx 中，元素标签对象储存当前解析元素的信息，主要是元素的嵌套关系，嵌套等级等。

![](https://image.3001.net/images/20190729/1564399648_5d3ed82021db5.png!small)

向下调试后发现 msxml.788872F7 函数会获取 <w:font> 元素的 w:name 属性字符的指针。

![](https://image.3001.net/images/20190729/1564399664_5d3ed83034891.png!small)

而下面的 msxml.78887335 函数会获取 o:idmap 元素字符的指针

![](https://image.3001.net/images/20190729/1564399680_5d3ed840654a5.png!small)

获取完 o:idmap 元素字符的指针后，调用 msxml.788872F7 函数解析 o:idmap 元素，在内存窗口可以看出字符指针已经指向了
incer 的位置，说明已经把 idmap 标签解析出来了。

![](https://image.3001.net/images/20190729/1564399699_5d3ed853643a3.png!small)

之后调用 msxml.788873F0 计算元素的嵌套等级，可以看出元素的嵌套等级计算出为 6，但此时元素的嵌套等级依旧是 5，还没有更新为 6。

![](https://image.3001.net/images/20190729/1564399711_5d3ed85fbceee.png!small)

在将 [ebx+1e8] 赋值给 eax 之后，发生了跳转，从而跳过了 call [ecx+20] 的调用转而进行 call [ebx+200] 的调用。

![](https://image.3001.net/images/20190729/1564399727_5d3ed86faf29b.png!small)

![](https://image.3001.net/images/20190729/1564399746_5d3ed88225223.png!small)

![](https://image.3001.net/images/20190729/1564399758_5d3ed88ecaba5.png!small)

调用的函数为 mso.32751CAA，其实 MSO 模块的函数调用没有太大的作用，只是给后面 wwlib 模块的做间接处理。

![](https://image.3001.net/images/20190729/1564399774_5d3ed89e0be2d.png!small)

到达 0x32751D5C 的位置后执行 call [ecx+20] 指令调用 sub_3277FAC0 函数，此时 esi = [esi+60]。

![](https://image.3001.net/images/20190729/1564399785_5d3ed8a95a96d.png!small)

接着 sub_3277FAC0 函数中会执行 call [eax+10] 指令调用 wwlib.3127D3FB。

![](https://image.3001.net/images/20190729/1564399802_5d3ed8ba32708.png!small)

进入 wwlib.3127D3FB 函数之后继续向下调试，此时 [[esi+b14]] 的地址中储存着元素的嵌套关系。

![](https://image.3001.net/images/20190729/1564399812_5d3ed8c4d9bf4.png!small)

![](https://image.3001.net/images/20190729/1564399826_5d3ed8d25888f.png!small)

之后调用完 wwlib.3127E6B3 函数后会进行一个判断，如果 ebx 等于 0x80004001 就跳转。

![](https://image.3001.net/images/20190729/1564399835_5d3ed8dbdd2ae.png!small)

跳转完成之后调用漏洞函数，下面的流程刚刚已经分析过了。

![](https://image.3001.net/images/20190729/1564399846_5d3ed8e6e5589.png!small)

根据上面调试分析的结果对其中几个位置下记录断点。查看日志可以发现 msxml.78887830 函数会逐一对元素进行解析，当解析到 <idmap>
标签时嵌套关系为 5。

![](https://image.3001.net/images/20190729/1564399871_5d3ed8ff0cab4.png!small)

![](https://image.3001.net/images/20190729/1564399905_5d3ed921f3615.png!small)

但是在异常处嵌套关系为 6，对最后一次调用 msxml.78887830 函数下断点，查看嵌套关系是何时变为 6 的。

![](https://image.3001.net/images/20190729/1564399961_5d3ed959e5182.png!small)

重新运行后断下，此时嵌套关系为 5。

![](https://image.3001.net/images/20190729/1564400063_5d3ed9bfb3b2e.png!small)

当调试到 wwlib.3127D3FB 函数中的 0x3128E3AD 位置时，嵌套等级变为了 6，说明 wwlib.312C6142 函数更新了嵌套等级。

![](https://image.3001.net/images/20190729/1564400081_5d3ed9d1e73ca.png!small)

接着分析一下 w:name 属性是何时被复制的。通过对漏洞异常处的分析发现 w:name 属性储存在元素对象中，通过对元素对象储存 w:name
位置下写入断点发现在 WWLIB.sub_3127D3FB 函数中会调用 wwlib.3127E773 函数复制 w:name
到元素对象当中，之后漏洞函数中会把 w:name 属性取出来进行虚函数表调用。

![](https://image.3001.net/images/20190729/1564400126_5d3ed9fe2870f.png!small)

![](https://image.3001.net/images/20190729/1564400175_5d3eda2f7961a.png!small)

![](https://image.3001.net/images/20190729/1564400187_5d3eda3b469ec.png!small)

需要注意的是再上面的分析中该跳转并没有实现，也就是说这里在复制完 w:name 属性之后直接返回了。而判断跳转的值是由 wwlib.3127E6B3
返回的，进入该函数，分析后发现在函数末尾处会将 0x80004001 赋值给 eax，在这之前会以 0x3149BFA3 作为基址，以 eax * 4
做为偏移地址进行调用，而 eax 是通过 [ebp-1c] 传进来的，对该位置下记录断点后查看日志。

![](https://image.3001.net/images/20190729/1564400219_5d3eda5b185dc.png!small)

根据日志可以发现当 [ebp+1c] 的值为 0xFFFF 时才会调用漏洞函数。而且解析 <w:font> 标签前调用一次，解析 <o:idmap>
标签后调用一次。

![](https://image.3001.net/images/20190729/1564400246_5d3eda766b1af.png!small)

之后把 <o:idmap> 标签删除，再对比日志信息。

![](https://image.3001.net/images/20190729/1564400257_5d3eda81719ea.png!small)

可以发现只有在 <w:font> 标签解析前才会将此值设置为 0xFFFF，所以这一个值可能是用于判断元素是否闭合。

![](https://image.3001.net/images/20190729/1564400292_5d3edaa44fa36.png!small)

最后总结得出 msxml.78887830 处理标签元素的流程。当 msxml.78887830 函数解析到 <w:font>
标签时，会误以为标签已经闭合（跳转值：0xFFFF），从而将 <o:idmap> 标签插入到 <w:font> 标签后，接着会把 <w:font> 标签的
w:name 属性（假如有的话）添加到对象之中，同时更新元素的嵌套关系（嵌套关系变为 6），导致最后使用 call [ecx+4]
进行虚函数表调用时虚表指针被错误的覆盖成了 w:name 属性中的数据触发了异常。

![](https://image.3001.net/images/20190729/1564400333_5d3edacd0c8bd.png!small)

一些关键的数据及函数调用。

![](https://image.3001.net/images/20190729/1564402037_5d3ee175397a7.png!small)

> 关于 CVE-2017-11826
> 的漏洞分析到此结束，由于是第一次分析类型混淆漏洞并且在写这篇文章前已经分析了一遍，所以有些地方不是很详细，可也能有一些错误。

 ***本文作者：护花使者cxy，转载请注明来自FreeBuf.COM**

