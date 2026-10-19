## 前情提要

[逆向分析教程（一）——调试代码](articles/system/316425.html)  
[逆向分析教程（二）——大本营](articles/system/317284.html)  

>
> 该系列文章以《逆向工程核心原理》为原型，调整其中对于新手需要耗费大量时间解决之处，更方便于新手入门。也同时解决互联网上扫描件电子书版本的阅读障碍（如截图模糊等）。

调试代码的时候，main()函数并不是直接位于可执行文件的EP位置上，出现在此的是开发工具（Visual
C++）生成的启动函数。我们需要查看的main()函数距离EP代码很远，如果有一种方法可以帮助我们快速查找到main()函数，那么必定会为调试带来极大帮助。

每个人在调试中快速查找所需代码时都有不同的方法，但是最基本最常用的有下面4种。

> 学习这4种方法前我们需要思考一个问题。根据前两章内容，我们已经知道，运行HelloWorld.exe程序会弹出一个消息框，显示“Hello
> World!”信息。固然是因为我们编写了代码，可在这种情形下，只要运行一下程序，不论是谁都能轻松意识到这一点。
>
> 如果你熟悉win32 api的开发，看到弹出的消息框就会想到，这是调用MessageBox()
> API的结果。应用程序的功能非常明确，只要运行一下程序，就能大致推测出其内部结构。不过前提是你已经具备了开发和分析代码的经验。

## 1.代码执行法

我们需要查找的是main()函数中调用MessageBox()函数的代码。在调试器中调试HelloWorld.exe（F8）时，main（）函数的MessageBox()函数在某个时刻就会被调用执行，弹出消息对话框，显示“Hello
World!”这条信息。

上面就是代码执行法的基本原理，当程序功能非常明确时，我们可以逐条执行指令来查找需要查找的位置。但是代码执行法仅适用于被调试的代码量不大、且程序功能明确的情况。倘若被调试的代码量很大且比较复杂时，此种方法就不再适用了。下面使用代码执行法来查找代码中的main()函数。从“大本营”（40104F）开始，按F8键逐行执行命令，在某个时刻弹出消息对话框，显示“Hello
World！”信息。按Ctrl+F2键再次载入待调试的可执行文件并重新调试，不断按F8键，某个时刻一定会弹出消息对话框。弹出消息对话框时调用的函数即为main（）函数。如图2-20所示，地址401144处有一条函数调用指令“CALL00401000”，被调用的函数地址为401000，按F7键（Step
Into）进入被调用的函数，可以发现该函数就是我们要查找的main()函数。

![](https://image.3001.net/images/20211227/1640586343_61c95c678fcf18dae19a6.png!small)![](https://image.3001.net/images/20211227/1640586359_61c95c774413e4db49af4.png!small)

如上图，地址40100E处有一条调用MessageBox()
API的语句。401002与401007处分别有一条PUSH语句，他把消息对话框的标题与显示字符串（Title =
"[www.reversecore.com](www.reversecore.com)", Text = "Hello
World!"）保存到栈（Stack）中，并作为参数传递给MessageBox W()函数。

这样我们就准确的查找到了main()函数。

>
> win32应用程序中，API函数的参数是通过栈传递的。VC++中默认字符串是使用Unicode码表示的，并且，处理字符串的API函数也全部变更为Unicode系列函数。

## 2.字符串检索法

右键菜单-search for-all referenced text strings

OllyDbg初次载入待调试的程序时，都会先经历一个预分析过程。此过程中会查看进程内存，程序中引用的字符串和调用的API都会被摘录出来，整理到另外的一个列表中，这样的列表对调试时相当有用的。使用all
referenced text strings命令会弹出一个窗口，其中列出了程序代码引用的字符串。

![](https://image.3001.net/images/20211227/1640586393_61c95c9914e0df97dbb5b.png!small)

地址401007处有一条PUSH 004092A0命令，该命令中引用的004092A0处即是字符串“Hello
World!”。双击字符串，光标定位到main()函数中调用MessageBox W（）函数的代码处。

在OllyDbg的value窗口，然后按Ctrl+G命令，可以进一步查看位于内存4092A0地址处的字符串。首先使用鼠标单击value窗口，然后按Ctrl+G快捷键，打开Enter
expression to follow in Dump窗口。（如果你的数据窗口不是这样的，右键单机选择HEX）

![](https://image.3001.net/images/20211227/1640586421_61c95cb5682f2f60f1996.png!small)

ascii前两行即使“Hello
World!”字符串，它是以unicode码形式表示的，并且字符串的后面被填充上了NULL值（记住这块null值的区域，我们以后还会再讲的）。

> VC++中，static字符串会被默认保存为Unicode码形式，static字符串是指在程序内部被硬编码的字符串。

上图我们还需要注意的是4092A0这个地址，它与我们之前看到的代码区域地址比如401XXX是不一样的。在HelloWorld进程中，409XXX地址空间被用来保存程序使用的数据。大家要清楚一点：代码和数据所在的区域是彼此分开的。

> 我们后面会慢慢学习代码和数据在文件里是怎么保存，以及怎么加载到内存的，这些是windows PE文件格式的相关内容，我们暂时先不管他。

## 3.API检索法

### 3.1在调用代码中设置断点

右键单击-search for-all intermodular calls

windows
编程中，如果想让显示器显示内容，则需要使用win32API向OS请求显示输出。换句话说，应用程序向显示器输出内容时，需要在程序内部调用win32
API。认真观察一个程序的功能后，我们能够大致推测出它在运行时调用的WIN32
API，则会为程序调式带来极大便利。以HelloWorld.exe为例，它在运行时会弹出一个消息窗口，由此我们可以推断出该程序调用了user_32.MessageBox
W() API。(敏感词所以加了下划线)

在OllyDbg的预分析中，不仅可以分析出程序中使用的字符串，还可以摘录出程序运行时调用的API函数列表。如果只想查看程序代码中调用了哪些API函数，可以直接使用all
intermodular calls命令。如下图窗口列出了程序中调用的所有API。

![](https://image.3001.net/images/20211227/1640586453_61c95cd58a254ccd16e71.png!small)

可以看到调用MessageBox W()的代码，该函数位于40100E地址处，他是user_32.MessageBox W()
API。双击它，光标就会定位到调用它的地址处（40100E）。观察一个程序的行为特征，若能事先推测出代码中使用的API,则使用上述方法能够帮助我们快速查找到需要的部分。

>
> 对于程序中调用的API，OllyDbg如何准确摘录出他们的名称呢？首先，他不是通过查看源代码来摘取的，如果想要了解其中的原理，我们需要理解PE文件格式的IAT（Import
> Address Table，导入地址表）结构。我们会在后面的文章中提到这些内容。

### 3.2在API代码中设置断点

鼠标右键菜单-search for - name in all calls

OllyDbg并不能为所有可执行文件都列出API函数调用列表。使用压缩器、保护器工具对可执行文件进行压缩或保护之后，文件结构就会改变，此时OllyDbg就无法列出API调用列表了（甚至连调试都会变得十分困难）。

> 压缩器（Run time Packer，运行时压缩器）
>
> 压缩器是一个实用压缩工具，能够压缩可执行文件的代码、数据、资源等，与普通压缩不同，它压缩后的文件本身就是一个可执行文件。
>
> 保护器
>
> 保护器不仅具有压缩功能，还添加了反调试、反模拟、反转储等功能，能够有效保护进程。如果想仔细分析保护器，我们还需要具有更高级的逆向知识。

这种情况下，DLL代码库被加载到进程内存后，我们可以直接向DLL代码库添加断点。API是操作系统对用户应用程序提供的一系列函数，他们实现于C:\Windows\system32文件夹中的
*.dll文件（如kernel32.dll、user_32.dll、gdi32.dll、advapi32.dll、ws2_32.dll等）内部。简单的说，我们编写的应用程序执行某种操作时（如各种I/O操作），必须使用OS提供的API向OS提出请求，然后与被调用API对应的系统DLL文件就会被加载到应用程序的进程内存。

在OllyDbg菜单中选择 View-Memory菜单（Alt+M）,打开内存映射窗口。如下图，内存映射窗口中显示了一部分HelloWorld.exe进程内存。在图底部可以看到user_32库被加载到了内存。

![](https://image.3001.net/images/20211227/1640586480_61c95cf0a07fc51ce690d.png!small)

使用OllyDbg中的Name in all modules命令可以列出被加载的DLL文件中提供的所有API。使用Name in all
moudules命令打开All names窗口，单机Name栏目按名称排序，通过键盘敲出MessageBox W后，光标会自动定位到MessageBox
W上。

![](https://image.3001.net/images/20211227/1640586514_61c95d120c0817cb3454b.png!small)

USER_32模块中有一个Export类型的MessageBoxW函数（不同环境下函数地址不同）。双击MessageBoxW函数后就会显示其代码，它实现于USER_32.dll库中，如图

![](https://image.3001.net/images/20211227/1640586547_61c95d3381995e6a7c4ac.png!small)

观察MessageBoxW函数的地址空间可以发现，它与HelloWorld.exe使用的地址空间完全不同。在函数起始地址上按F2键，设置好断点后按F9继续执行。

![](https://image.3001.net/images/20211227/1640586573_61c95d4d34b6c5e2ece73.png!small)

> 如果HelloWorld.exe应用程序中调用了MessageBoxW() API,则调试时程序运行到该处就会暂停。

与预测的一样，程序执行到MessageBoxW代码的断点处就停了下来，此时寄存器窗口中的ESP值为19FF18

![](https://image.3001.net/images/20211227/1640586597_61c95d65192e40e07f95a.png!small)

它是进程栈的地址。在右下角的栈窗口中可以看到更详细的信息

![](https://image.3001.net/images/20211227/1640586625_61c95d8114dfc638b1225.png!small)

> 我们会在后面的教程中详细说明函数调用以及站动作原理，现在可以暂时忽略

如上图，ESP值的12FF18处对应一个返回地址401014，HelloWorld.exe的main()函数调用完MessageBoxW函数后，程序执行流将返回到该地址处。按Ctrl+F9快捷键使程序运行到MessageBoxW函数的RETN命令处，然后按F7键也可以返回到401014地址处。地址401014的上方就是地址40100E,它正是调用MessageBoxW函数的地方。

![](https://image.3001.net/images/20211227/1640586651_61c95d9b56ac67b3e465c.png!small)

以上就是快速查找代码的4种方法。今天你又学废了嘛！

