## 前言

本次文章只用于技术讨论，学习，切勿用于非法用途，用于非法用途与本人无关！

所有环境均为本地环境分析，且在本机进行学习。

这个会写成一个系列，目前暂定为18篇文章，主要是对C/C++语言生成为可执行程序对其进行逆向分析，学习其在汇编语言中的特征，为逆向分析打好基础，如寻找主函数、数据类型、三大结构（顺序结构、选择结构、循环结构）和C++特色（继承、多态、类）等等...。在想要往漏洞挖掘、游戏安全、恶意代码分析、Android逆向方向学习，这系列知识必须非常熟悉，他就如盖楼前的地基，如果地基不牢之后一定会出现问题。文章结构我会以C++编程由浅入深去写，每章会以Debug
x64、Debug x32、Release x64、Release x32去分析。作者：rkabyss

# 分析环境准备

### 1、Visual Studio 2022

下载链接：<https://visualstudio.microsoft.com/zh-hans/downloads/>

个人觉的目前VS2017、VS2019、VS2022都可以满足学习和工作需求，主要还是看个人习惯，用久了就不愿意换了，我一直用的是VS2017，后来玩崩了，重装完系统换成VS2022了，VS的功能就不多介绍了。

![1654489920_629d83404760b89c6ea79.png!small?1654489920465](https://image.3001.net/images/20220606/1654489920_629d83404760b89c6ea79.png!small?1654489920465)

### 2、Microsoft Visual C++ 6.0

下载链接： <https://pan.baidu.com/s/19sjWjIMdfuc-ScgB7lApPQ>提取码: ua7b

Microsoft Visual
C++，是Microsoft公司推出的以C++语言为基础的开发Windows环境程序，面向对象的可视化集成编程系统。目前已经被Visual
Studio和Visual Studio
code等工具替代，但是还是有很多程序是在VC++上写的，所以在之后分析中也会分析VC++生成的程序，因为不同平台生成的会有所不同。

![1654489938_629d8352edda7d28428ba.png!small?1654489939407](https://image.3001.net/images/20220606/1654489938_629d8352edda7d28428ba.png!small?1654489939407)

### 3、x64dbg/x32dbg调试工具

下载链接：<https://sourceforge.net/projects/x64dbg/files/snapshots/>

x64_dbg和x32_dbgs是Windows 下的 32/64 位调试器，类似 ollydbg。x64 dbg 采用 QT
平台编写，官方包含简体中文语言。因为ollydbg工具作者已停止更新，所以ollydbg只能调试32位程序。

![1654489961_629d83697646aee86c7fb.png!small?1654489961932](https://image.3001.net/images/20220606/1654489961_629d83697646aee86c7fb.png!small?1654489961932)

![1654489973_629d83757f46f11306b0e.png!small?1654489973915](https://image.3001.net/images/20220606/1654489973_629d83757f46f11306b0e.png!small?1654489973915)

### 4、静态分析工具IDA Pro

下载链接: <https://pan.baidu.com/s/1ejoF78bRQB-MYxF7f50Tyw>提取码: v4n2

交互式反汇编器专业版（Interactive Disassembler Professional），人们常称其为IDA
Pro，或简称为IDA。是最棒的一个静态反编译软件，为众多[0day](https://baike.baidu.com/item/0day/4885829)世界的成员和[ShellCode](https://baike.baidu.com/item/ShellCode)安全分析人士不可缺少的利器！

![1654489989_629d838577bb91af6c9ff.png!small?1654489995115](https://image.3001.net/images/20220606/1654489989_629d838577bb91af6c9ff.png!small?1654489995115)

### 5、WinDbg

Windbg是在windows平台下，强大的用户态和[内核](https://baike.baidu.com/item/%E5%86%85%E6%A0%B8/108410)态调试工具。相比较于Visual
Studio，它是一个轻量级的调试工具，所谓轻量级指的是它的安装文件大小较小，但是其调试功能，却比VS更为强大。它的另外一个用途是可以用来分析dump数据。

![1654490008_629d83986f18accebac73.png!small?1654490008655](https://image.3001.net/images/20220606/1654490008_629d83986f18accebac73.png!small?1654490008655)

# 总结

这篇文章没有任何知识点，主要是介绍一下接下来逆向分析中将要用到的几个工具，话就不多说了，为的就是水一篇。

