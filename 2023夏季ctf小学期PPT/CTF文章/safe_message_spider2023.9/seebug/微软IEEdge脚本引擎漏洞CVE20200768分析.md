**作者：启明星辰ADLab**  
**原文链接：<https://mp.weixin.qq.com/s/kMPbnUpxBbgTExUC38GNRg>**

微软在近日发布的补丁公告中，修复了一个由启明星辰ADLab安全研究员提交的漏洞，漏洞编号为CVE-2020-0768。漏洞位于ChakraCore引擎代码库中，可同时影响Internet
Explorer 11和Microsoft Edge (基于EdgeHTML)
浏览器。该漏洞是一个内存破坏型漏洞，有远程代码执行的风险，因此微软将其评级为“严重”，并致谢ADLab。

**应对措施**

使用Windows自动更新或手动下载补丁包修复漏洞。

# 漏洞和补丁分析

## PART 1

本漏洞是ChakraCore引擎在JIT编译过程中，单一指令的数据流分析错误，导致的变量活跃性分析和寄存器分配出错。首先从漏洞样本的控制流图开始：

![](https://images.seebug.org/content/images/2020/03/3dad95f9-285e-4e21-88a7-27cdd514f91c.png-w331s)

其中，在Block 4有如下的字节码：

![](https://images.seebug.org/content/images/2020/03/7adc90f7-88b7-44bd-8a2a-efd523b9658d.png-w331s)

符号s10代表[1337]，s6代表const修饰的arr。按照编译原理的术语，变量获取定义值称为def，变量值被使用称为use，在InitConst指令中s6被def，s10被use，随后在StElemC这条指令下，s6被use。可以看到s6与s10关系密切，s6可以看作s10按照另一种方法对同一变量的引用，ChakraCore称为copy-prop符号对原始符号的引用。但调试显示，这里发生了错误：

![](https://images.seebug.org/content/images/2020/03/6c54ff0c-9886-4f7b-81ed-9a59b7e71385.png-w331s)

如此一来形成了原始符号为s10，copy-prop符号为s6，即s6->s10的键值对。其栈回溯位于：

![](https://images.seebug.org/content/images/2020/03/e211aaba-073f-4fd1-822c-f66b0e9e1fee.jpg-w331s)

错误键值对是根据数据流分析的错误结果得出的。随后，这个键值对被加入了Block
4中blockOptData->capturedValues->copyPropSyms，其栈回溯位于：

![](https://images.seebug.org/content/images/2020/03/89059826-e14b-4c31-8b0c-514489fc99c3.png-w331s)

随后，在JIT ForwardPass这样从前向后的优化过程中，Block 4的blockOptData->capturedValues被合并给Block
5，其中包含s6->s10这一键值对，其栈回溯位于：

![](https://images.seebug.org/content/images/2020/03/b908aa13-ef76-4109-88ee-56e0dcabf526.png-w331s)

再之后，在JIT BackwardPass这样从后向前的优化过程中，Block
5的upwardExposedUses通过访问blockOptData->capturedValues->copyPropSyms，把s6->s10这一键值对加入。其栈回溯位于：

![](https://images.seebug.org/content/images/2020/03/5bb6f1d1-6b00-49b8-bd03-c627403936c3.png-w331s)

upwardExposedUses在编译原理中被称为“向上暴露的使用”，它是变量活跃性分析的对称过程。随后在反向传播的过程中，含有上述键值对的upwardExposedUses被传递给Block
4、Block 3和Block 2。而作为Loop Header的Block 2将其upwardExposedUses用于活跃性分析和后续的寄存器分配过程。

![](https://images.seebug.org/content/images/2020/03/45d1a62c-cc65-4a6d-9cd5-31c964ee5e1d.png-w331s)

上述过程可以通过下图来表示。可以看到，错误的数据经过了正向传播和反向传播，最终在循环体的全部范围都被污染。

![](https://images.seebug.org/content/images/2020/03/db5daa98-d3cc-49a9-abd9-e04812e56ebf.jpg-w331s)

随后，由于上述错误数据，在JIT的寄存器分配过程为s10计算出了错误的生命周期，其生命周期横跨循环的开始到结束。于是阴差阳错，JIT插入了一个MOV指令，形如MOV
labelReg,
mem，但并没有初始化其instr->src->m_offset，该值始终为0。在最后生成机器码的时候，生成了一个指向栈帧指针、偏移为0的读内存操作，表示为[EBP+0x0]或[RBP+0x0]。

![](https://images.seebug.org/content/images/2020/03/a1f375c9-7f00-43ab-9c43-b021a6a1f66c.png-w331s)

这样，一个非预期的内存访问把非法的数据读入了JavaScript引擎上下文，随后在BailOut或其他情况会引用到，这样的非法数据将会造成类型混淆。

## PART 2

造成上述错误数据传播的原因在于InitConst这一指令其实没有在ChakraCore的JIT代码中得到正确的数据流分析，因此在微软的修复中，在JIT刚开始介入的时候，InitConst指令就被替换成Ld_A指令。

![](https://images.seebug.org/content/images/2020/03/68159f8c-cc3e-4b91-8101-d6b949932f2e.png-w331s)

ChakraCore完整实现了对Ld_A指令的数据流分析。此时，在分析Forward Pass中，发现Block
4中的键值对不再是s6->s10，而是s10->s6，也就是说s10是原始符号，s6是引用s10的copy-prop符号。如此一来，自然不会造成错误数据的传播。微软在IE11浏览器中使用了相同的代码来修补这个漏洞。

事实上，在ECMAScript
6标准中，const修饰符用来表示一个变量在定义之后不可再被赋值，是语法层次的约束；而JavaScript引擎中的JIT过程始终发生在解释执行之后，如果const修饰符的约束在解释执行阶段被违反，将会立即退出，不会优化执行JIT过程。因此，JIT过程只需要考虑数据流问题，而不必考虑const修饰符的约束。由于ChakraCore在JIT的优化阶段与解释执行阶段使用同一套中间语言，不管是Ld_A还是InitConst都兼容JIT的全过程，本漏洞可以明确认为是一个业务逻辑漏洞。

**参考链接**

  1. <https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments>

  2. <https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-0768>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1146/>

