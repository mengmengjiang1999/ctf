***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **该漏洞的潜在原因是类型混淆。攻击者通过构造XML数据包(XDP)模板并在XML Forms Architecture
(XFA)对象上执行特定的JavaScript操作，可以迫使Reader跳出模板对象的范围来引用数据。如果成功，就会在沙盘渲染程序中执行代码执行。**

## 漏洞分析

触发该漏洞所需的XDP模板代码相当简单：  
![XDP模板代码](https://image.3001.net/images/20181028/1540693726_5bd51ede9b9b6.png!small)该漏洞由两个JavaScript指令触发。通过将一个子表单附加到另一个子表单，我们可以触发对底层模板对象的超界(OOB)读取。在这种情况下，当附加一个xfa引用的子表单时，就会出现漏洞。然后调用
`<object>.presence = “inactive”;.`  
![由两个JavaScript指令触发](https://image.3001.net/images/20181028/1540693735_5bd51ee7b684e.png!small)启用PageHeap后，在读取模板对象的OOB时，CMP指令上发生崩溃。虽然对象看起来只有0x140字节大小，但是我们在偏移量0x1d0处取消了对缓冲区边界以外数据的引用：  
![启用PageHeap](https://image.3001.net/images/20181028/1540693743_5bd51eefe8f39.png!small)根据崩溃情况，我们知道唯一对象的类型是0x7c00。通过观察`acroform.api`的符号化版本。在Solaris
9.4.1中，我们可以看到这个特定类型的id属于XFATemplateModelImpl对象，它只是底层XDP的“模板”对象：![底层XDP的“模板”对象](https://image.3001.net/images/20181028/1540693751_5bd51ef727d15.jpg!small)回到非符号化的Windows版本的`acroform.api`,我们可以确认模板对象的大小为0x140字节，这是上面引用的OOB对象的大小。我们可以通过几个简单的步骤找到:在`XFATemplateModelImpl::Type
method`中`Acroform.api`可以找到静态变量`0x7c00`。  
![找到静态变量](https://image.3001.net/images/20181028/1540693759_5bd51effbe6e2.jpg!small)Xref提供XFATemplateModelImpl
vtable：  
![Xref提供XFATemplateModelImpl
vtable](https://image.3001.net/images/20181028/1540693767_5bd51f07711be.jpg!small)  
-Xref到vtable start提供构造函数。-Xref到构造函数并向上滚动几行显示对象的大小，即0x140字节：  
![-Xref到vtable
start提供构造函数](https://image.3001.net/images/20181028/1540693774_5bd51f0e7a97c.jpg!small)由于我们导致了对模板对象的OOB读取，所以我们可以推测代码预期的是一个不同的、更大的对象，而不是模板对象，这也表明这是一个类型混淆错误。最有可能的是，类型混淆发生在xfa模板和xfa表单对象之间。而xfa模板大小为0x140字节，即xfa表单对象的大小为0x270字节。

##
Exploit我们不能在模板对象被实例化之前执行JavaScript代码，要知道控制崩溃不是件小事。要实现这一点，需要在PDF解析过程或XDP解析之前的任何其他受控数据处理过程中求助于可控制的分配和释放。控制崩溃的另一种方法是构造一个PDF，其中包含一个附加的PDF，这会触发漏洞。`Heap
feng
shui`将发生在“外部”PDF中，触发“内部”(附件)PDF中的vuln。然后，以使其执行JavaScript代码的方式打开附加的PDF需要更高的权限，因此它可能对大多数用户无效。通过执行“poc.pdg”可以观察到这种崩溃是可以控制的。即使没有PageHeap。由于要读取Unicode字符串的某些部分并将其用作指针，因此最终会发生崩溃。下面是一个没有PageHeap的崩溃输出：  
![没有PageHeap的崩溃输出](https://image.3001.net/images/20181028/1540693783_5bd51f179a6d6.png!small)

## 结论

如果你想亲自测试一下，PoC就在[这里](a%20href=)。它可以在2018.011.20040之前在adobereader版本上起作用。看看我们今年发布的建议，你会发现很多pdf相关的案例。adobereader可能是最流行的，但是Foxit
Reader中也存在大量bug。在操作系统中加入内置的PDF渲染器，就可以理解为什么如此多的研究人员研究这种攻击表面。

 ***参考来源[thezdi](https://www.thezdi.com/blog/2018/9/18/cve-2018-12794-using-type-confusion-to-get-code-execution-in-adobe-reader)，由周大涛编译，转载请注明来自FreeBuf.COM。**

