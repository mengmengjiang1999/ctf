***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **出于对CPU相关漏洞的兴趣，我深入研究了下CVE-2018-3639（Spectre4，幽灵4），有不正确的地方欢迎指正。**

根据微软的一篇博客，已经发现的可用于揣测执行边信道攻击的分支（Speculation primitives）共有4种，分别是 **
_条件分支预测失误（_** ** _conditional branchmisprediction_** ** _）_** 、 **
_间接分支预测失误（_** ** _indirect branch misprediction_** ** _）_** 、 ** _异常传递或延期（_**
** _exception deliveryor deferral_** ** _）_** 以及今天的主角 ** _揣测存储绕过（_** **
_Speculative StoreBypass_** ** _）_** 。  

##  **详细分析**  

直接上代码的最重要部分，此代码经过个人添加了注释并修改过一些BUG， **可以在文章最后下载源码对照查看每个变量的含义** ：

![代码的最重要部分](https://image.3001.net/images/20180804/1533363411_5b6544d399c54.png!small)

**最重要的代码在** **115** **行和** **122** **行** ，在C语言层面看不出任何问题，请查看汇编代码：

![汇编代码](https://image.3001.net/images/20180804/1533363438_5b6544eee0197.png!small)

汇编代码中红色部分为115行代码，绿色部分为122行代码， **紫色部分即为出现问题的关键代码** 。

这两行代码出现问题的原因是 **执行当前代码的核心认为两条指令仅存在输出相关，因此可以使用寄存器重命名的方式并行执行**
，在《计算机体系结构：量化研究方法（第五版）》中可以找到相关解释：

![书籍中的相关解释](https://image.3001.net/images/20180804/1533363512_5b65453857156.png!small)

并行执行不一定会出问题，还 **需要让执行单元先执行** **testfun+138** **指令再执行** **test+135**
**指令，这样才能保证** **testfun+138** **会错误的影响** **cache** 。示例代码能够达成这个条件的原因是
**test+135** **指令与** **testfun+128** **指令相关，因此需要等待前面代码执行完毕，而** **test+138**
**则没有这个顾虑** 。

继续深入到核心内部的执行单元，查看其到底是如何完成并行执行的，下图是Intel的Sandy Bridge微架构执行单元：

![Intel的Sandy
Bridge微架构执行单元](https://image.3001.net/images/20180804/1533363468_5b65450c63ae8.png!small)

查询AMD的17代处理器微架构文档，查询到如下信息：

![image.png](https://image.3001.net/images/20180804/1533363477_5b654515be5b5.png!small)

![AMD的17代处理器微架构文档](https://image.3001.net/images/20180804/1533363489_5b654521d069a.png!small)

所以可以判断上述两条宏观指令分别被翻译为 ** _单条存储相关微指令_** 和 ** _单条加载相关微指令_** ，结合上述寄存器重命名技术，因此
**可以判断在此微架构中使用** **port2** **和** **port4** **来并行执行两条指令** ，真相大白。

虽然 **在** **test+135** **存储指令执行完毕后，** **test+138** **指令由于错误会回退，但是已经受到影响的**
**cache** **不会回退** ，所以可以结合rdtscp指令对cache lin 进行时间测试观察是否cache hit即可判断出到数据是多少。

不知读者还记得幽灵1不，它主要是由于 ** _错误的分支预测_** 导致的 cache line 缓存了错误的数据。而幽灵4，主要是由于错误的 **
_揣测执行_**
（暗自揣测圣意认为两条指令无关）造成的Meltdown，来源想不起来了。虽然AMD也有异常抑制技术，但是不受到该漏洞影响的原因是核心的执行单元有限，个人觉得应该是AMD的Store和load执行单元为同一个所以免疫，有待后续查证，附带上几个Intel和AMD的架构以供参考：

Intel Haswell微架构：

![Intel
Haswell微架构](https://image.3001.net/images/20180804/1533363557_5b654565a1b6a.png!small)

Intel Sandy Bridge微架构：

![Intel Sandy
Bridge微架构](https://image.3001.net/images/20180804/1533363568_5b65457076c41.png!small)

AMD 17th 架构：

![AMD 17th
架构](https://image.3001.net/images/20180804/1533363581_5b65457d2e5e4.png!small)

 **DEMO程序编译命令：**  

****

gcc -o Spec4 Speculative4.c -Wall-DHIT_THRESHOLD=50 -DNO_INTERRUPTS -ggdb

##  **参考文献**

 ****

> 漏洞PoC地址：<https://www.exploit-db.com/exploits/44695/>
>
>
> 微软针对CVE-2018-3639的解释：<https://blogs.technet.microsoft.com/srd/2018/05/21/analysis-> and-mitigation-of-speculative-store-bypass-cve-2018-3639/>
>
> Intel Sandy
> Bridge微架构详解：<https://en.wikichip.org/wiki/intel/microarchitectures/sandy_bridge_(client)#MSROM_.26_Stack_Engine>
>
> Intel Sandy
> Bridge微架构详解（中文）：<http://www.mouseos.com/arch/intel_microarchitecture.html>
>
> AMD
> 17代处理器优化说明：<https://developer.amd.com/wordpress/media/2013/12/55723_3_00.ZIP>
>
> 《计算机体系结构：量化研究方法（第五版）》
>
> Intel官方手册：64-ia-32-architectures-optimization-manual.pdf
>
> AMD开发手册：<https://developer.amd.com/resources/developer-guides-manuals/>
>
> 已知的CPU漏洞汇总：<https://wiki.osdev.org/CPU_Bugs>

 ***本文作者：创世之枪，转载请注明来自FreeBuf.COM**

