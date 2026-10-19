原创xiaoyuer合天智汇

  1. 木马分析入门  

大家好，我最近从Web安全开始学习二进制安全，分享一下自己学习过程的收获和心得体会。由于是入门的内容，所以对于二进制大佬来说这很简单，所以本文主要面向的对象主要是和我一样一直做Web安全，又想入门二进制安全的人。本次我学习的案例是木马和病毒常用的一个技术：确保只有一个病毒或者木马在系统中运行，即运行单一实例。对于病毒和木马而言，如果多次重复运行，会增加暴露的风险。所以要确保系统中只运行一个病毒或木马的进程。

  1. 正向编写C代码  

要实现运行单一实例，一种常见且简单的方法是通过创建系统命名互斥对象实现的，这种方法主要是利用CreateMutex函数，通过该函数我们也可以查看是否已经有一个进程运行了。那么，如果通过CreateMutex函数得知是否已经有一个在运行的进程了呢？

下面简要介绍下CreateMutex函数，它的功能是创建或者打开一个已命名或者未命名的互斥对象。

关于它的返回值，如果函数成功，则返回值是新创建的互斥对象的句柄。如果函数失败，则返回值为NULL。要获得扩展的错误信息，请调用GetLastError。如果互斥锁是一个已命名的互斥锁，并且该对象在此函数调用之前就存在，则返回值是现有对象的句柄，GetLastError返回ERROR_ALREADY_EXISTS。

简单点来说，就是如果CreateMutex函数的返回值不是NULL，并且调用GetLastError函数后，返回值是ERROR_ALREADY_EXISTS，那么可以判定已经存在了一个在运行的进程。用C语言代码实现如下：

![v2-98ca99a6eebef73f7611de4d915a3ac9_r.jp](https://pic3.zhimg.com/v2-98ca99a6eebef73f7611de4d915a3ac9_r.jpg)

使用VC++6.0完成编译链接后生成可执行文件，双击运行，显示如下:

![v2-376bcb2efe8922efd44a791f6bd608e3_r.jp](https://pic2.zhimg.com/v2-376bcb2efe8922efd44a791f6bd608e3_r.jpg)

在不关闭上述进程的前提下，再次双击生成的可执行文件，显示如下:

![v2-922ac88ebafa554bd1fbae436e2c0016_r.jp](https://pic4.zhimg.com/v2-922ac88ebafa554bd1fbae436e2c0016_r.jpg)

可以看出当系统中运行第二个进程的时候，输出了Already Run！！！！说明程序已经成功地判断出重复运行了。

  1. 逆向分析  

下面我们就对这个程序进行逆向分析，我们需要对主函数和子函数分别进行逆向分析，这次先分析主函数。

关于学习的方法，我的收获是在初学阶段，我们先分析自己写的代码，分析完之后再进行印证，慢慢地就可以脱离源码并尝试分析其他未公开源码的程序流程。

在学习过程中，十分重要的一点是：要分清主次。什么意思呢？

学习汇编语言和逆向，我们完全没有必要逐条指令去仔细阅读所有的代码，重要的是从整体上理解程序究竟做了哪些操作。汇编语言也是一种编程语言，平常大家也不会去一行一行地仔细阅读别人写的大量代码，除了必须要理解的重要部分花时间仔细读一读，剩下的部分基本都是一带而过，只要大体上理解程序在做什么事就好了。逆向工程也是一样，“重要的部分花时间仔细理解”“其余部分大概知道怎么回事就好”这两条原则同样适用。

那么哪些是重要的呢？在病毒木马分析中，其中一点比较重要的是分析call函数，只要将这个程序所调用的函数分析清楚了，那么就知道这个病毒木马在做什么了。与此同时要弄清楚它的逻辑结构，比如什么时候跳转到哪执行。

接下来我们首先对主函数进行分析：

  1. 主函数：  

主函数的C语言代码如下图所示:

![v2-2c418924b2b51807386228fa4393e9e5_r.jp](https://pic4.zhimg.com/v2-2c418924b2b51807386228fa4393e9e5_r.jpg)

下面对其汇编代码进行分析：

![v2-14d33ef2d33f0595905c988c198bbd41_r.jp](https://pic4.zhimg.com/v2-14d33ef2d33f0595905c988c198bbd41_r.jpg)

_main_0 proc near

var_40= byte ptr -40h

push ebp

mov ebp, esp

sub esp, 40h

push ebx

push esi

push edi

lea edi, [ebp+var_40]

mov ecx, 10h

mov eax, 0CCCCCCCCh

rep stosd

以上代码完成所有的函数入栈操作，每个函数开始时都会有这样的操作，这里我们无需过分细究，如感兴趣，对这段代码详细的分析可参考《C++反汇编与逆向分析技术揭秘》p150，我也将其主要的内容贴出来了：

![v2-84a9e08ee15de8b7cee502e4caa4a413_r.jp](https://pic4.zhimg.com/v2-84a9e08ee15de8b7cee502e4caa4a413_r.jpg)

![v2-3e1eb853616c55393dee7816c56e43ea_r.jp](https://pic4.zhimg.com/v2-3e1eb853616c55393dee7816c56e43ea_r.jpg)

关于这段内容中补充介绍两个指令，其中，xor
eax,eax直接会将eax的值设置为0，这是将寄存器设置为0最常见的方式，cmp指令是条件指令，详细内容如下图所示:

![v2-023ca5dcfa09e3393e1fec9be3743af7_r.jp](https://pic1.zhimg.com/v2-023ca5dcfa09e3393e1fec9be3743af7_r.jpg)

这段内容在这里暂时只需了解，无需深究，等需要的时候再去研究也不迟。

之后，到了需要认真理解的地方了，下一条的指令是

call sub_401005

它的意思是调用子函数sub_401005，在这里其实对应的是我们编写的IsAlreadyRun函数。

需要补充的是在函数调用时，如果有参数需要传递，需要在call指令之前，使用push先将参数从后往前入栈。这里因为无任何参数传递，所以在调用之前，无需使用push指令将参数入栈。后面还会详细介绍是如何从后往前入栈的，这里需要先记住这个知识点。

还有一个要记住的是在函数调用完成后，VC中，会使用eax寄存器来保存函数的返回值。

接下来的一条指令是

test eax, eax

关于test指令，只需记住若eax为0，则zf标志位会设置为1，此时eax中的值是上一条指令的返回值，若对test指令感兴趣可参考如下解释:

![v2-9d500339608372a929d07ba2021b6e89_r.jp](https://pic1.zhimg.com/v2-9d500339608372a929d07ba2021b6e89_r.jpg)

![v2-cd2537a59d7d400dae25fb8296743343_r.jp](https://pic1.zhimg.com/v2-cd2537a59d7d400dae25fb8296743343_r.jpg)

接下来的指令是

jz short loc_4010E0

jz是跳转指令，即jump zero，即当零标志位ZF=1的时候跳转到 loc_4010E0这个位置执行，此时也就是上一个指令test
eax，eax得到的操作使得ZF=1,也就是eax=0，由于eax保存的是子函数的返回值，所以我们得知子函数的返回值为0。由我们编写的C语言代码可知，此时对应的是IsAlreadyRun函数返回结果为false，和我们的分析相对应。

跳转到该位置后：

loc_4010E0: ; "NOT Already Run!\n"

push offset aNotAlreadyRun

call _printf

add esp, 4

可以看到的call _printf 指令，这将会调用printf输出函数。由于printf需要传递参数，所以在call
_printf之前，需要先执行push的操作。我们将鼠标放在aNotAlreadyRun上可以看到对应的字符串与loc_4010E0:后的备注信息"NOT
Already Run!\n"一样，如下图所示：

![v2-a7a78ee07378eca0b80b7f7935b495d0_r.jp](https://pic3.zhimg.com/v2-a7a78ee07378eca0b80b7f7935b495d0_r.jpg)

所以得出结论，若子函数sub_401005的返回值为0时，跳转到loc_4010E0位置，将会输出"NOT Already
Run!\n"。与我们编写的C语言代码相符合。

那么，若子函数sub_401005的返回值为1时，会怎么样呢？

![v2-7d82944c6384306be69066cadf7d6272_r.jp](https://pic3.zhimg.com/v2-7d82944c6384306be69066cadf7d6272_r.jpg)

此时，会走到左边的执行框内，不会跳转到右边。同理，这里将会输出"NOT Already Run!\n"字符串。

执行完成后，左右两边的内容都会到loc_4010ED这个位置继续执行：

![v2-dc2a29bc486f3098c7d4d84f675b602b_r.jp](https://pic3.zhimg.com/v2-dc2a29bc486f3098c7d4d84f675b602b_r.jpg)

这段内容看到有call ds:Sleep指令，此处是调用了Sleep函数，对应的是我们C代码中的Sleep(10000)：

![v2-296b6606bea4501ecbb678835d300993_r.jp](https://pic1.zhimg.com/v2-296b6606bea4501ecbb678835d300993_r.jpg)

由于要传递参数，所以需要先将参数入栈，即push操作，可以看到在call ds:Sleep指令之前，有push 186A0h
指令，将鼠标放置在186A0h上，右键可观察对应的十进制：

![v2-8ca13677599b8be1af8bbdc04842b4e5_r.jp](https://pic2.zhimg.com/v2-8ca13677599b8be1af8bbdc04842b4e5_r.jpg)

刚好也是100000，所以和我们编写的C代码也刚好符合。

之后，使用pop和call __chkesp等指令，完成出栈、检查栈平衡等函数返回工作。

![v2-9c2e664fabe8ee2fefd30e620e922ab6_r.jp](https://pic2.zhimg.com/v2-9c2e664fabe8ee2fefd30e620e922ab6_r.jpg)

目前，关于主函数的分析已经完成，下次我们一起进一步对子函数进行详细的分析。

参考书籍：

《Windows黑客编程技术详解》甘迪文著--北京：人民邮电出版社，2018年12月。

《C++反汇编与逆向分析技术揭秘》钱松林，赵海旭著--北京：机械工业出版社，2011年9月。

《恶意代码分析实战》 （美）Michael Sikorski / Andrew Honig 著，诸葛建伟，姜辉，张光凯译 --北京：电子工业出版社，2014年4月，原书名： Practical Malware Analysis: The Hands-On Guide to
Dissecting Malicious Software。

《汇编语言》王爽 著--2版，北京：清华大学出版社，2008年4月。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

#  

