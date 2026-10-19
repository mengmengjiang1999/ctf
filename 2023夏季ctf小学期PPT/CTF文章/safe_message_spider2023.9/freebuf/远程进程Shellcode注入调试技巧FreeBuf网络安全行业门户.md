**在病毒分析的过程中，时常会遇到很多病毒为了躲避杀软的检测，使用进程注入的方式，将shellcode注入到系统进程中执行，本文将介绍一些在遇到shellcode注入进程时所使用的调试技巧。**

##  **情形一：P** **E** **进程远程注入shellcode到其它进程**

PE类文件在进行进程注入的时候，可能会注入一个PE文件，也有可能是注入一段shellcode，但注入的流程通常是一样的。

注入已有进程:

> OpenProcess —> WriteProcessMemory —> CreateRemoteThread；

创建进程注入:

> CreateProcess —> WriteProcessMemory —> GetThreadContext —> SetThreadContext
> —> ResumeThread；

上面一种是注入已有进程，下面一种是自己创建一个进程进行注入，不过需要关注的点是一样的，就是远程线程启动时的context（上下文）。

如果是遇到CreateRemoteThread的情况，就比较直观，只要直接找到该函数的第四个参数lpStartAddress，就是我们要找的context值，下图是一个示例：

![](https://image.3001.net/images/20190823/1566520027_5d5f32dbad1b7.png!small)

如果是遇到ResumeThread情形，就稍稍麻烦一些，需要先查看GetThreadContext的第二个参数lpContext，获取到的进程上下文会放在该指针结构中，然后代码对其中的地址值进行修改，再调用SetThreadContext：

![](https://image.3001.net/images/20190823/1566520036_5d5f32e4a3b2a.png!small)

找到上下文地址后，只需要断在CreateRemoteThread或ResumeThread函数上，使用WinHex打开程序要注入的进程，将该上下文地址处的代码修改为JMP到当前地址（或0xCC，此处可以发散一下，只要是能够想办法断下来即可），再单步步过（F8）CreateRemoteThread/ResumeThread，使用OD附加到注入的进程，断在上下文地址处，再将代码修改回原来的代码即可继续执行。

##  **情形二：脚本病毒/宏病毒远程注入shellcode到其它进程**

脚本病毒/宏病毒注入shellcode时所使用的函数与PE类略有不同，下面以一个宏病毒的分析过程为例来进行说明。

调试宏代码，该样本的宏代码没有经过混淆，可以清晰的看到其将shellcode硬编码赋值给一个数组，这里的数据长这样：

![](https://image.3001.net/images/20190823/1566520052_5d5f32f4cc077.png!small)

需要把它转化成C++能够认识的类型，不过别着急，先继续往下看，代码创建了一个rundll32.exe进程并挂起，然后申请一块shellcode长度大小内存，依次将数据写入进程内存，最后启动进程：

![](https://image.3001.net/images/20190823/1566520067_5d5f33030f641.png!small)

这里需要关注的函数是最后用来启动进程的CreateStuff，这个函数是前面代码自定义的函数，对应是CreateRemoteThread：

    
    
    Private Declare Function CreateStuff Lib "kernel32" Alias "CreateRemoteThread" (ByVal hProcess As Long, ByVal lpThreadAttributes As Long, ByVal dwStackSize As Long, ByVal lpStartAddress As Long, lpParameter As Long, ByVal dwCreationFlags As Long, lpThreadID As Long) As Long

再看函数参数：

    
    
    CreateStuff(pInfo.hProcess, 0, 0, rwxpage, 0, 0, 0)

pInfo.hProcess是进程句柄，rwxpage是启动进程需要给出执行的上下文，于是在这一条语句下个断点，print一下rwxpage参数的值：

![](https://image.3001.net/images/20190823/1566520080_5d5f3310b58d3.png!small)

589824，转换成十六进制为0x90000，应该就是要找的上下文地址，接下来就是到进程内存中去找到这一段数据了，使用WinHex打开对应进程的内存，找到0x90000这个地址：

![](https://image.3001.net/images/20190823/1566520089_5d5f331961306.png!small)

可以看到这一段数据中有明文显示的可疑字符串了，看起来像是网络连接相关的，到这一步就要想办法来调试这段shellcode，这里有两种调试的思路。

**思路一：** 像调试PE类注入那样，把执行上下文地址处的代码修改为0xCC或jmp当前地址的代码：

![](https://image.3001.net/images/20190823/1566520133_5d5f3345adab8.png!small)

如果修改为0xCC，需要注意，应该把调试器的实时调试设置选成“附加前无需确认”，这样进程启动后才会自动附加到OD进行调试（记得将内存修改回原值，如果没有自动附加，就手动附加一下进程）：

![](https://image.3001.net/images/20190823/1566520140_5d5f334cad1de.png!small)

如果修改成jmp当前地址，那么需要手动打开OD，选择要附加的进程，然后跳转到执行上下文的地址下断点，断下来后把内存地址修改为原值，再继续调试：

![](https://image.3001.net/images/20190823/1566520149_5d5f33555f663.png!small)

**思路二：** 在WinHex中找到这段shellcode后，将其选中，右键->Edit->Copy Block->C
Source，这样就能将数据拷贝成C++能够识别的形式：

![](https://image.3001.net/images/20190823/1566520158_5d5f335e09a75.png!small)

然后用Visual studio新建一个C++控制台应用项目，定义一个数组，内容为我们拷贝的C Source数据：

![](https://image.3001.net/images/20190823/1566520165_5d5f33656c6b2.png!small)

然后在main函数中定义函数指针指向shellcode的首地址，然后调用这个shellcode首地址的这个函数，读起来很绕，但实际上一条指令就能够完成：

![](https://image.3001.net/images/20190823/1566520172_5d5f336c9be1e.png!small)

当然，这里的写法并不局限于一种，只要理解其中的原理即可。随后生成Release版的EXE文件，就能够使用OD或IDA对shellcode进行分析了，用IDA加载出来的Main函数如下：

![](https://image.3001.net/images/20190823/1566520183_5d5f33773a125.png!small)

本文使用了几个示例，讲解了在恶意代码分析过程中遇到远程进程注入时的一些调试方法，虽然调试技巧有很多种，但万变不离其宗，在调试过程中可以根据自己的需要选择不同的调试思路，也可以根据原理开发一些工具，如shellcode生成EXE文件工具等。

 ***本文作者： 深信服千里目安全实验室，转载须注明来自FreeBuf.COM**  

