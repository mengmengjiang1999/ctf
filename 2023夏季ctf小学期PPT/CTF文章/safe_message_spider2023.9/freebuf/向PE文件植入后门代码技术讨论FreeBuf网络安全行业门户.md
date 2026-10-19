## 写在前面的话

**这篇文章将介绍使用codecaves对PE文件植入后门代码。有几个很好的工具可以帮到你了。比如BackdoorFactory和Shelter将完成相同的工作，甚至绕过一些静态分析几个防病毒。**

## 开始

让我们理解一些术语：

### PE文件：

> 可移植可执行文件（PE）格式是可执行文件，目标代码和DLL的文件格式，用于32位和64位版本的Windows操作系统。

### Code Cave：

根据维基百科介绍 ：

> “`Code Cave`是进程内存中的一系列空字节。进程内存中的`Code
> Cave`通常是对代码的脚本函数一部分的引用，这些函数具有注入自定义指令的能力。例如，如果脚本的内存允许5个字节并且只使用3个字节，则剩余的2个字节可用于向脚本添加外部代码。“

### Shellcode：

根据维基百科介绍：

>
> “shellcode是具有payload的一小段代码。它被称为`”shellcode“`，因为它通常启动一个命令shell，攻击者可以通过该shell控制被入侵的机器，所以任何执行类似任务的代码都可以称为`shellcode`“  
>

让我们开始吧 ....你可以从这里下载我用过的Putty版本。我将使用Immunity
Debugger进行调试。您可以使用任何其他调试器，如Ollydbg。首先，我们需要找到可用的Code
Cave，然后插入恶意代码。您可以添加一个部分或修改现有的部分来使用Code Cave。我使用cave-miner脚本来定位可用的未使用字节。![1.PNG](https://image.3001.net/images/20180803/1533275804_5b63ee9c99e20.png!small)可以看到cave从`00445CD5`开始。我将从`00445CD6`注入我的shellcode。接下来，我将劫持程序的入口点并将执行流程重定向到我们的shellcode。首先，我们必须使用Lord
PE或任何PE头编辑器工具使`.data`部分可执行。完成后，我们复制入口点的前几条指令并将其保存在记事本中。![2.PNG](https://image.3001.net/images/20180803/1533275814_5b63eea6217d3.png!small)插入第一条指令`JMP
00445CD6`，这可以将执行流程重定向到我们新发现的`code
cave`。通过JMP指令回复入口点之后，我们需要记录下哪些指令被覆盖，因为这些指令需要在以后恢复。现在，让我们来了解部分指令：

    
    
    1.PUSHAD
    2.PUSHFD
    3.Shellcode
    4.Stack Allignment(堆栈对齐)
    5.POPFD
    6.POPAD
    7.RETORE instructions
    8.JMP to next instruction(JMP到下一条指令PUSHAD指令)
    

PUSHAD的用法与写作是一样的：

    
    
    Push EAXPush ECXPush EDXPush EBXPush ESPPush EBPPush ESIPush EDI
    

`POPAD`以相反的顺序从堆栈中弹出值，从而恢复所有寄存器值。`PUSHAD`和`POPAD`可用于执行通用寄存器的保存和恢复，而无需按下每个寄存器的PUSH和POP。同样，`PUSHFD`和`POPFD`用于保存和恢复`EFLAGS`寄存器。在PUSHFD指令在
code cave中以十六进制格式和二进制的方式从mstoxic生成一个反向tcp shell代码。
![3.PNG](https://image.3001.net/images/20180803/1533275825_5b63eeb1bd18d.png!small)在shellcode执行之前和shellcode执行之后记下ESP值，以找出差异并对齐堆栈。shellcode执行之前
：![4.PNG](https://image.3001.net/images/20180803/1533275832_5b63eeb809d9d.png!small)shellcode执行之后
-![5.PNG](https://image.3001.net/images/20180803/1533275838_5b63eebe8471f.png!small)差值=
`0018FF68`\-`0018FD6C`![6.PNG](https://image.3001.net/images/20180803/1533275844_5b63eec411f7e.png!small)现在通过将此值添加到esp来对齐堆栈。![7.PNG](https://image.3001.net/images/20180803/1533275851_5b63eecb861ef.png!small)![8.PNG](https://image.3001.net/images/20180803/1533275856_5b63eed0a171b.png!small)恢复后保存新修改的可执行文件并监听netcat上的反向连接。![9.PNG](https://image.3001.net/images/20180803/1533275862_5b63eed6aac2d.png!small)一旦我开始putty，它就卡住了，除非我关上反向连接。这是问题是因为在msfvenom
shellcode中使用了一个名为`WaitforSingleObject`的函数。

这有一篇很好的文章关于如何解决这个问题 <https://simonuvarov.com/msfvenom-reverse-tcp-waitforsingleobject/>

Msfvenom
shellcode使用`INFINITE`作为`dwMilliseconds`参数的值。通过将`dwMilliseconds`参数值从`-1`设置为`0`来修复waitforsingleobject问题（由于我使用NOP替换的dec
esi指令）。![10.PNG](https://image.3001.net/images/20180803/1533275869_5b63eedd726ee.png!small)最后把它修复并保存可执行文件，大功告成
!!!!!!!!!!!!!!!!

## POC

![11.PNG](https://image.3001.net/images/20180803/1533275876_5b63eee4507b4.png!small)

## 最后

一旦打开putty.exe，它就会产生一个反向shell。..Happy Hacking .. :)

***参考来源：[theanuragsrivastava](http://www.theanuragsrivastava.in/2018/07/backdoring-pe-files-using-code-caves.html)，由周大涛编译，转载请注明来自FreeBuf.COM**

