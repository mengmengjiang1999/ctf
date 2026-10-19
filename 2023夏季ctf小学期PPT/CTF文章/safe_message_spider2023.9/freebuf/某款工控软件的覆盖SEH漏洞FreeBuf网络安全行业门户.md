## ****01.前言****

在工业控制行业中使用的软件种类繁多，这里可以简单给它分为几类，用于PLC（控制器）编程的软件、用于上位组态的软件以及用于触摸屏编程的软件等。由于这些软件的专用性、专业性以及权限控制等原因，信息安全专业人员很难接触到，不容易掌握软件的操作使用，从而增加了工控软件漏洞挖掘的难度。在这里分享一次横河PLC编程软件WideField2代码执行漏洞的挖掘经验。

##  ** **02.实验环境****

软件版本:

> WideField2 Version:R5.02
>
> 操作系统: XP Professional SP3英文版

##  ** **03.漏洞描述****

横河PLC编程软件WideField2是由横河电机集团开发的一款PLC编程软件，主要用于FA-M3V Range-free(无需测距)多功能控制器的功能强化，通过该软件，用户可以实现对FA-M3V Range-free的实时逻辑分析功能的同步逻辑分析仪，有效的对程序的运行状况进行监控，使产品能够更好的运用于生产与开发。在工控领域有广泛使用。

WideField2存在代码执行漏洞，该软件的组件WideField2.exe未对用户输入做严格检查限制，攻击者可通过构造特殊字符串触发漏洞，引起程序崩溃，在程序上下文中执行任意代码。

##  ** **04.步骤****

1）下载软件并在XPSP3英文版虚拟机中，安装时采用默认安装；

2）在软件安装的目录下找到组件WideField2.exe，如下图所示：

![1607164137_5fcb60e9cdabcb6091129.png!small](https://image.3001.net/images/20201205/1607164137_5fcb60e9cdabcb6091129.png!small)

3）双击运行该组件，如下图所示：

![1607164147_5fcb60f35b0d0de63975f.png!small](https://image.3001.net/images/20201205/1607164147_5fcb60f35b0d0de63975f.png!small)

组件进程如下图所示：

![1607164155_5fcb60fb377d7951741fd.png!small](https://image.3001.net/images/20201205/1607164155_5fcb60fb377d7951741fd.png!small)

4）在file下新建一个工程，工程名任意，如下图所示:

![1607164161_5fcb610121032c47c7296.png!small](https://image.3001.net/images/20201205/1607164161_5fcb610121032c47c7296.png!small)

![1607164199_5fcb6127df92f934f705e.png!small](https://image.3001.net/images/20201205/1607164199_5fcb6127df92f934f705e.png!small)

5）在Block List下新建一个块，文件名名任意，如下图所示:

![1607164207_5fcb612f04ac39fdb3144.png!small](https://image.3001.net/images/20201205/1607164207_5fcb612f04ac39fdb3144.png!small)

6）在重命名刚建立的块的名称，在输入框输入，如下图所示:

![1607164237_5fcb614d5ccf28101a2ed.png!small](https://image.3001.net/images/20201205/1607164237_5fcb614d5ccf28101a2ed.png!small)

7）执行python脚本，在会产生 5000 个 A 组成的 test.txt 文件，将5000A字符输入上一步的rename
File输入框，采用windbg捕获异常，如下图：

![1607164247_5fcb6157a3f331e7c249c.png!small](https://image.3001.net/images/20201205/1607164247_5fcb6157a3f331e7c249c.png!small)

我们利用超长字符串成功覆盖了 SEH

8）接下来就是定位溢出点了，也就是多少个字符可以覆盖到 SEH，首先我们用ImmunityDebugger 的 mona.py 插件产生 5000
个随机字符，如下图：

![1607164256_5fcb6160082bfe87409cf.png!small](https://image.3001.net/images/20201205/1607164256_5fcb6160082bfe87409cf.png!small)

9）将5000个mona.py 插件产生 5000 个随机字符，输入Rename File输入框，同时用windbg捕获异常，如下图：

![1607164262_5fcb6166642e369d053af.png!small](https://image.3001.net/images/20201205/1607164262_5fcb6166642e369d053af.png!small)

可以看到 Pointer to next SHE record 被覆盖为 0x396e4138，也就是字符串 9nA8 因

为这是小序存放，所以反过来就是 8An9

10）通过!mona pattern_offset 8An9，我们可以得到我们填充 416 个字符就可以覆盖到 Pointer to next SHE
record 了，定位完成。

![1607164274_5fcb6172951e870a267e7.png!small](https://image.3001.net/images/20201205/1607164274_5fcb6172951e870a267e7.png!small)

11）接下来寻找pop pop retn 指令序列地址，首先我们寻找没有保护模块。

![1607164282_5fcb617a9a9b687bbe27b.png!small](https://image.3001.net/images/20201205/1607164282_5fcb617a9a9b687bbe27b.png!small)

12）在SafeSEH值为false的模块中查找具有跳转到ESP的模块，如下图：

![1607164289_5fcb6181be02ad531e466.png!small](https://image.3001.net/images/20201205/1607164289_5fcb6181be02ad531e466.png!small)

13）经过多次尝试，0x69b3d734就是我们想要的 pop pop retn 指令序列地址。当然我们还需要根据需要完成坏字节的排除，这里我们忽略。

14）编写POC如下，完成让程序执行弹出一个计算器。

![1607164297_5fcb61891803ae000f315.png!small](https://image.3001.net/images/20201205/1607164297_5fcb61891803ae000f315.png!small)

15）执行POC后在生成的evil.txt中复制内容，粘贴如下的输入框中：

![1607164302_5fcb618e75bbe71f2560a.png!small](https://image.3001.net/images/20201205/1607164302_5fcb618e75bbe71f2560a.png!small)

16）实现计算器的弹出：

![1607164309_5fcb6195d123b6cfd3e8a.png!small](https://image.3001.net/images/20201205/1607164309_5fcb6195d123b6cfd3e8a.png!small)

![1607945097_5fd74b89b7ceeec521ce0.png!small?1607945099833](https://image.3001.net/images/20201214/1607945097_5fd74b89b7ceeec521ce0.png!small?1607945099833)

##  ** **05.总结****

由于工控系统的相对封闭性，工控系统漏洞暴露的机会比较小，但随着社会对工控信息安全的重视，会有越来越多的工控系统漏洞被挖掘出，促进企业的工控信息安全防护意识的提高。

