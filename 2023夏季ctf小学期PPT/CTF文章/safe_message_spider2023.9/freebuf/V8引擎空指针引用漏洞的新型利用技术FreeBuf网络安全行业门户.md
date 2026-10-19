![](https://image.3001.net/images/20201021/1603278402_5f901642efb4c1a4d10c6.png!small)

## 介绍

去年，英国国家网络安全中心（NCSC）报告了一个V8编译器中存在的安全漏洞，随后Google便悄悄修复了该漏洞。这个漏洞ID为1003286，漏洞的具体信息可以点击【[
_这里_](https://crbug.com/1003286)】获取。根据漏洞报告的描述，这是一个空指针解除引用DoS漏洞，这个漏洞是一个不可利用的漏洞，并且只能通过WASM代码来触发。在深入分析之后，我们发现这里还有另一种触发该漏洞的方式，并且能够通过V8
JIT编译器进程来利用该漏洞实现攻击。

在这篇文章中，我们将会介绍该漏洞的利用技术细节，并演示如何利用该漏洞实现远程代码执行。

## 漏洞成因

出于代码优化方面的考虑，V8
JIT编译器使用了节点图，并通过优化管道的几个阶段减少节点图来生成优化的本机代码。而且这个节点图也适用于WASM编译器，可以将WASM代码编译为本机代码。

节点在图中使用“Use”结构相互链接，如下所示：

![](https://image.3001.net/images/20201021/1603278413_5f90164d9943780fb01ce.png!small)

通过使用这种结构，节点可以指定自己的输入节点和用户节点来减少图的遍历。Use结构体重包含了用于保存多种信息的比特字段，如下所示：

![](https://image.3001.net/images/20201021/1603278420_5f901654043d679f8325a.png!small)

InputIndex字段表示这个Use结构输入节点的索引，它可以用来定位用户节点相应的输入节点。但是，这个字段仅提供了17比特的空间来存储索引，而且没有任何代码来检测这个限制是否正常执行。因此，我们就可以使用大量输入节点来构建一个图，让这些节点指向一个单一节点，以此来引起整型溢出。比如说，0x20002表示0x2为输入节点索引。

Use::input_ptr和Use::from函数都使用了这个InputIndex字段来定位用户节点以及对应的输入节点。

![](https://image.3001.net/images/20201021/1603278426_5f90165aa3acf280909c5.png!small)

这将导致节点、Use结构及其子字段之间出现类型混乱的情况。

NCSC的研究人员使用WebAssembly构建了一个PoC，并通过它来处罚空指针解引问题。WASM代码优化过程比JIT编译器的更加简单，因此控制过程与JIT编译器相比也更加难，所以它们无法避免空指针解引的情况。

在分析过程中，我们发现JIT代码可以让节点拥有大量输入节点：

![](https://image.3001.net/images/20201021/1603278439_5f9016672ebf695871896.png!small)

这个函数可以帮助我们构建一个跟NCSC代码不同的[
_PoC_](https://blog.br0vvnn.io/upload/poc-1003286.js)，并成功处罚漏洞，最终实现代码执行流的控制。

## 漏洞利用

虽然这个漏洞存在于V8
JIT编译器之中，但它跟其他常见的JIT编译器漏洞有很大不同。为了成功利用该漏洞，我们需要生成能够利用初始漏洞的漏洞代码，然后利用它们来实现远程代码执行。

节点、Use和Operator都是我们能够因此类型混乱的结构体，它们对应的结构如下：

![](https://image.3001.net/images/20201021/1603278448_5f901670ca680bcdb4a6d.png!small)

上面的Use::input_ptr和Use::from函数都是通过ReplaceWithValue函数来调用的，而这个函数是用来替换节点值的：

![](https://image.3001.net/images/20201021/1603278456_5f901678342ca4e7282cd.png!small)

这里的“old_to”并非节点类型，而是Use字段：

![](https://image.3001.net/images/20201021/1603278464_5f9016803eec6f28f423f.png!small)

如果use->prev为空，old_to->first_use则会被替换成use->next。由于“old_to”本质为Use，那么old_to->first_use就相当于CheckMap节点的Operator。如果old_to->first_use被替换成了use->next，那么CheckMapNode->op->opcode就会变成use->next->bit_field。此时，CheckMap节点的操作码opcode就会被其他opcode替换，并导致CheckMap节点失效。这也是漏洞利用第一步的主要攻击场景：

![](https://image.3001.net/images/20201021/1603278481_5f9016911cda73c711745.png!small)

根据这个模型，我们创建了下列代码：

![](https://image.3001.net/images/20201021/1603278487_5f90169703ac946376ae5.png!small)

在替换JSStrictEqual节点之前的节点图正好满足我们的要求：

![](https://image.3001.net/images/20201021/1603278492_5f90169c694e96643eeaf.png!small)

现在，我们就可以在PACKED_DOUBLE_ELEMENTS和DICTIONARY_ELEMENTS数组之间引起类型混乱问题，并获取任意读写/addrof原语来实现远程代码执行了。

广大研究人员可以在Chrome v77版本上进行完整的[
_漏洞利用测试_](https://blog.br0vvnn.io/upload/exploit-1003286.html.txt)。

