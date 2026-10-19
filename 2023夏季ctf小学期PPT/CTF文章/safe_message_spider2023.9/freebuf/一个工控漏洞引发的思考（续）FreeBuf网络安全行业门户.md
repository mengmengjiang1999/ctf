***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、概述

阿基米德曾经说过：给我一个支点，我就能撬起地球。”那么，在漏洞挖掘的过程中，如果给你一个支点（pivot），能否快速发掘更多漏洞呢？上一篇分析了研华公司（Advantech）HMI/SCADA软件AdvantechWebAccess的一个远程代码执行漏洞（传送门：<https://www.freebuf.com/vuls/205987.html>），这一篇尝试以该漏洞为支点，发掘更多高危漏洞。

从ZDI上关注到Mat_Powell大神提交了大量CVE，其中很多漏洞具有相似性，暂且对比看：CVE-2019-6550、CVE-2018-7499两个漏洞：

![图片.png](https://image.3001.net/images/20190719/1563467098_5d309d5a6d796.png!small)

![图片.png](https://image.3001.net/images/20190719/1563467107_5d309d6323ba0.png!small)![图片.png](https://image.3001.net/images/20190719/1563467187_5d309db35cf26.png!small)

漏洞对应的相关组件分别为：bwthinfl.exe、bwaccrts.exe、upandpr.exe；入口分支均为0x2711
IOCTL；漏洞描述几乎完全相同，漏洞成因均为：未对用户输入的数据做合适验证从而导致栈溢出。暂且我们可以推测次两个漏洞为同类漏洞，接下来的问题是造成漏洞的相关函数是什么呢？

## 二、漏洞分析

仔细查看上述第三张截图，漏洞详情中似乎已“道破天机”，“罪魁祸首”是大家熟知的scanf函数？接下来唯有上IDA对此三个组件逆向求证了：

![图片.png](https://image.3001.net/images/20190719/1563467223_5d309dd7dc1c1.png!small)![图片.png](https://image.3001.net/images/20190719/1563467239_5d309de76b8b3.png!small)
![图片.png](https://image.3001.net/images/20190719/1563467245_5d309dedd0b57.png!small)

果然三个组件中均使用了sscanf函数，而这个函数是微软在安全编程中禁止使用的函数之一：<https://docs.microsoft.com/en-us/previous-versions/bb288454(v=msdn.10)>  

![图片.png](https://image.3001.net/images/20190719/1563467271_5d309e07ee1b9.png!small)

下一步需要思考的就是如何以上篇的RCE漏洞为支点（pivot），来触发上述组件中的scanf函数了，进而形成漏洞利用。

## 三、PoC改造

下载AdvantechWebAccess V.8.0软件，在Win7x64虚拟机中安装，查看端口开放情况，确认软件运行正常：

![图片.png](https://image.3001.net/images/20190719/1563467300_5d309e246ce1a.png!small)

![图片.png](https://image.3001.net/images/20190719/1563503060_5d3129d4b7f9a.png!small)

以组件upandpr.exe为例进行PoC改造和调试，上一篇中分析到最终代码执行通过lpCommandLine参数传入一个文件名或路径给CreateProcessA函数（于是可以指向任何文件了），则可以通过合理构造参数：将执行的目标指向upandpr.exe组件并执行scanf函数，PoC改造部分如下所示：![图片.png](https://image.3001.net/images/20190719/1563467333_5d309e457b913.png!small)

由于整个漏洞利用执行（函数调用）的基本流程是webvrpcs.exe->drawsrv.dll->upandpr.exe（sscanf）,当用户提供的输入数据覆盖了堆栈，函数返回时候将发生异常。上调试器进行调试运行吧，目标当然是upandpr.exe（sscanf），此时涉及一个问题是：当upandpr.exe启动、发生异常时，调试器自动被加载，可参考：<https://www.52pojie.cn/thread-196194-1-1.html>，进行一番设置之后，便可观察改造后的PoC能否能够按照既定的思路运行了：  

![图片.png](https://image.3001.net/images/20190719/1563467352_5d309e5829df6.png!small)

PoC执行后，upandpr.exe被加载，F9继续执行后异常发生，如下图所示：

![图片.png](https://image.3001.net/images/20190719/1563467372_5d309e6caa1b9.png!small)

接下来是最熟悉的场景：

![图片.png](https://image.3001.net/images/20190719/1563467386_5d309e7aa5739.png!small)

进一步IDA查看sscanf函数处伪码：

![图片.png](https://image.3001.net/images/20190719/1563467405_5d309e8d34852.png!small)

可精确推算出覆盖堆栈需要的junk长度只需0x4D0，再次改造一下PoC进行测试：

![图片.png](https://image.3001.net/images/20190719/1563467417_5d309e9908c80.png!small)

![图片.png](https://image.3001.net/images/20190719/1563467488_5d309ee0432ff.png!small)

可见EIP被精确劫持。那么再下一步，即可继续根据堆栈情况设计布局shellcode了，对于shellcode编写一个更有利的消息便是WebAccess软件的模块代码编写中几乎未启用Windows系统的相关安全机制，如ASLR、DEP：  

![图片.png](https://image.3001.net/images/20190719/1563467513_5d309ef91b03b.png!small)

## 四、总结

从上述分析可知，由软件的一个漏洞收获了其他大量漏洞，攻击面由此进一步扩大，小伙伴们可以借题发挥大量收割CVE啦（不过之前版本的CVE貌似都被Mat大神给收割了）。另外，基本的安全编程的思想对于码农来说尤为重要，微软早已禁用函数还是不用为好。  

***本文作者：ww5466064，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

