# 使用Ghidra P-Code进行辅助逆向分析

阅读量 **1288858**

发布时间 : 2020-01-08 16:29:20

 **x**

##### 译文声明

本文是翻译文章，文章原作者 galaxylab，文章来源：galaxylab.com.cn

原文地址：<https://galaxylab.com.cn/%E4%BD%BF%E7%94%A8ghidra-p-code%E8%BF%9B%E8%A1%8C%E8%BE%85%E5%8A%A9%E9%80%86%E5%90%91%E5%88%86%E6%9E%90/>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01ebf449f8043913e3.png)

Ghidra是美国NSA开源的一款跨平台软件逆向工具, 目前支持的平台有Windows,
macOS及Linux并提供了反汇编、汇编、反编译等多种功能。由于Ghidra是开源项目，目前目前已经有大量的安全研究人员为其编写插件来不断扩展功能，此外Ghidra还支持多种CPU架构的反编译功能，例如PowerPC,
MIPS等在IoT领域比较常见的CPU类型。

## 2\. P-Code 介绍

  * Ghidra P-Code是专为逆向工程设计的寄存器传输语言，能够对许多不同的处理器进行建模。
  * P-Code会将单个处理器指令转化为一系列的P-Code操作, 这些操作将处理器状态的一部分作为输入和输出变量(VarNodes)。
  * 通过分析原始P-Code，可以了解代码中寄存器的控制流，从而帮助我们辅助分析代码。
  * 具体说明可以参考P-Code相关文档: Ghidra安装目录下的docs/languages/html/pcoderef.html 。

简单来说就是Ghidra将各种不同的处理器汇编代码转换为了统一的P-Code中间语言并提供了API接口，通过这些API接口我们可以在一定程度上实现一些跨CPU架构的自定义的辅助分析功能。

下图是VxWorks系统中初始化bss段数据的代码，我们可以看到这段代码调用了bzero函数去初始化bss段。

![](https://p1.ssl.qhimg.com/dm/1024_344_/t01b2621b1412e4f05f.png)

在开启了P-Code View配置后，我们就可以对应的查看每条汇编指令所对应的Pcode指令流了。如下图所示，我们可以通过P-Code来逐条分析寄存器的变化。

![](https://p2.ssl.qhimg.com/dm/1024_464_/t01ce85d7f713264e6f.png)

## 3\. P-Code 应用案例 – 对函数调用参数进行静态追踪

在进行逆向分析时IDA或Ghidra等逆向工具通常会帮我们完成CALL参数实际值的追踪分析，然而当我们想要进行自动化分析时，却发现无法简单的通过一个API来直接获取这些函数调用的参数值。此时我们就可以使用Ghidra
P-Code来进行辅助分析，通过追踪P-Code流来计算出函数调用参数的实际值。

我们还是以sysStart这个函数中来对P-Code相关的API进行说明。如下图所示，为了获取函数代码的P-Code,
我们首先要调用decomplib.decompileFunction对函数进行反编译获取dRes，接着调用dRes.getHighFunction获取反编译后的hfunction之后即可通过hfunction.getPcodeOps来获取目标函数的P-Code流。

![](https://p0.ssl.qhimg.com/dm/1024_557_/t0127403fd7d48f10ff.png)

在上图的例子中，可以看到一条指令为CALL的P-Code，CALL指令的相关说明如下图所示。我们可以通过分析input0来获取跳转地址，input1及input2则作为CALL的2个参数。此处的input0~2就是前面所说的输入和输出变量(VarNodes)。

![](https://p5.ssl.qhimg.com/dm/1024_230_/t010088438062306b45.png)

现在我们继续分析这条P-Code指令，通过getInput函数可以方便的获取P-Code的input参数。如下图所示:此时input0是一个内存地址，input1是一个unique对象，unique对象不属于即时值需要再进一步的追踪分析而input2是const对象属于即时值此时input2参数的值就是0x54cb0。PS:
具体的VarNode对象类型可参考P-Code相关文档。

![](https://p5.ssl.qhimg.com/dm/1024_282_/t012f3205809fad4c25.png)

如下图所示，Ghidra在此处提供了一个很方便的函数，我们可以通过调用VarNode的getDef函数来对该VarNode的赋值流进行追踪。通过分析我们会发现该VarNode是由一条PTRSUB指令进行赋值的。

![](https://p1.ssl.qhimg.com/dm/1024_282_/t010924b695f1249e2e.png)

通过阅读文档，我们会发现PTRSUB实际上就是input0 + input1 的值赋值给output，至此我们就通过P-Code成功追踪到了参数的具体值。

![](https://p3.ssl.qhimg.com/dm/1024_207_/t01923696d6a29f2a96.png)

在实际使用中我们会遇到一个参数需要向上多次追踪赋值的情况，此时我们则需要进行多次追踪计算直到算出结果或遇到动态值出现无法计算的情况。

使用P-Code来分析的一个好处是跨CPU架构，不管是MIPS、ARM、X86或是PowerPC Ghidra都会将其转换成同样的P-Code中间语言进行处理，因此基于P-Code编写的工具就具备了一定的跨平台分析能力，这在分析IoT设备时能够为我们提供一些便利。

## 4\. 基于函数参数静态追踪的一些扩展

利用P-Code来追踪函数参数的脚本我们已经开源，大家感兴趣的话，可以下载测试玩玩。

<https://github.com/PAGalaxyLab/ghidra_scripts/blob/master/trace_function_call_parm_value.py>

基于函数参数分析的这个轮子，可以实现一些比较有趣的功能下面是几个小例子。

### 4.1 遍历Goahead websFormDefine

Goahead是在IoT设备中非常常见的一款嵌入式web server，websFormDefine函数则用于向web
server注册各类Form的handler。

因此我们可以在测试由器时通过dump所有websFormDefine函数的引用来获取所有websForm的Handler，从而快速的去定位可疑的Handler发现后门等(CVE-2019-10040)。

![](https://p3.ssl.qhimg.com/dm/1024_641_/t0116afbbacad56043d.png)

### 4.2 基于函数报错信息来修复无法识别的函数名

下图是某基于VxWorks系统的路由器设备函数异常报错代码，通过分析代码我们可以得知在执行TaskSuspend挂起Task之前会将错误日志进行打印输出，而这个错误日志就包含了当前函数的函数名。

![](https://p3.ssl.qhimg.com/dm/1024_352_/t0158f494d6d610cfac.png)

因此我们可以考虑如下方法来修复函数。首先找到所有TaskSuspend的引用，之后向上追踪一个P-Code
CALL指令后判断是否为print函数，是print函数则追踪函数的参数值从而获取函数名进行修复。在之前的脚本上进行一些少量修改即可实现基于异常报错的函数名修复脚本。

![](https://p3.ssl.qhimg.com/dm/1024_631_/t019743c52d996a998a.png)

### 4.3 寻找命令注入漏洞

在某路由器设备中doSystem实际是system函数的一层封装，通过dump所有doSystem函数的调用可以帮助我们快速的发现命令注入漏洞。

![](https://p4.ssl.qhimg.com/dm/1024_621_/t0154d91ee74f9dc4d7.png)

![](https://galaxylab.org/wp-content/themes/mnews/images/post-loading.gif)

## 5\. 总结

本文对Ghidra P-Code进行了简单的介绍，通过分析P-Code能够帮助我们编写一些定制化的分析工具，而函数调用参数追踪仅仅是其中一个使用场景，希望通过阅读这篇文章大家能够对Ghidra
P-Code有一个简单的了解，也希望能够帮助到那些有类似分析需求同学们。

PS: 文章开始的那张图片中龙喷出的二进制火焰到底是什么呢？有兴趣的同学们可以去分析下^ ^。

## 6\. 引用

  1. <https://github.com/PAGalaxyLab/ghidra_scripts>
  2. <https://github.com/NationalSecurityAgency/ghidra>
  3. <https://github.com/0xAlexei/INFILTRATE2019/tree/master/PCodeMallocDemo>

本文由 Galaxy Lab 作者：[小黑猪](https://galaxylab.com.cn/author/64/) 发表，其版权均为 Galaxy
Lab 所有，文章内容系作者个人观点，不代表 Galaxy Lab 对观点赞同或支持。如需转载，请注明文章来源。

本文翻译自galaxylab.com.cn
[原文链接](https://galaxylab.com.cn/%E4%BD%BF%E7%94%A8ghidra-p-code%E8%BF%9B%E8%A1%8C%E8%BE%85%E5%8A%A9%E9%80%86%E5%90%91%E5%88%86%E6%9E%90/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **平安银河安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/196851](/post/id/196851)

安全客 - 有思想的安全新媒体

本文转载自: [galaxylab.com.cn](https://galaxylab.com.cn/%E4%BD%BF%E7%94%A8ghidra-p-code%E8%BF%9B%E8%A1%8C%E8%BE%85%E5%8A%A9%E9%80%86%E5%90%91%E5%88%86%E6%9E%90/)

如若转载,请注明出处： <https://galaxylab.com.cn/%E4%BD%BF%E7%94%A8ghidra-p-code%E8%BF%9B%E8%A1%8C%E8%BE%85%E5%8A%A9%E9%80%86%E5%90%91%E5%88%86%E6%9E%90/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [逆向工程](/tag/逆向工程)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhimg.com/t01e5bc10efebdf248c.png) 平安银河安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

