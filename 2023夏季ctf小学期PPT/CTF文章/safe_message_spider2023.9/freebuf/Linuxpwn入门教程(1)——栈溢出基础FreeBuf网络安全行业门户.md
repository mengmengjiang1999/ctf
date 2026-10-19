作者：[Tangerine@SAINTSEC](https://bbs.ichunqiu.com/thread-42241-1-1.html?from=beef)

原文来自：[https://bbs.ichunqiu.com/thread-42241-1-1.html](https://bbs.ichunqiu.com/thread-42241-1-1.html?from=beef)

## 0x00 函数的进入与返回

要想理解栈溢出，首先必须理解在汇编层面上的函数进入与返回。首先我们用一个简单执行一次回显输入的程序hello开始。用IDA加载hello，定位到main函数后我们发现这个程序的逻辑十分简单，调用函数hello获取输入，然后输出“hello,”加上输入的名字后退出。使用F5看反汇编后的C代码可以非常方便的看懂逻辑。  
![image.png](https://image.3001.net/images/20180629/15302613526488.png!small)我们选中IDA-View窗口或者按Tab键切回到汇编窗口，在main函数的`call
hello`一行下断点，开启32位的docker环境，启动调试服务器后直接按F9进行调试。  

  

如图，这是当前IDA的界面。在这张图中我们需要重点注意到的东西有栈窗口，EIP寄存器，EBP寄存器和ESP寄存器。

首先我们可以看到EIP寄存器始终指向下一条将要执行的指令，也就是说如果我们可以通过某种方式修改EIP寄存器的值，我们就可以控制整个程序的执行，从而”pwn”掉程序(要验证这一点，我们可以在EIP后面的数字上点击右键选择`Modify
value.......`把数值改成`080484DE`然后F9继续执行，从而跳过`call hello`一行)。

剩下的东西都和栈相关。顾名思义，栈就是一个数据结构中的栈结构，遵循先入后出的规则。这个栈的最小单位是函数栈帧。一个函数栈帧的结构如图所示：

![image.png](https://image.3001.net/images/20180629/15302613851496.png!small)  

局部变量1  
---  
.......  
......  
.......  
局部变量m  
局部变量n  
EBP  
EIP  
参数1  
.......  
参数n  
  
栈的生长方式是向低地址生长，也就是说这张图的方向和IDA中栈窗口的方向是一样的，越往上地址值越小。同样的，新入栈的栈帧在IDA的窗口中会把原来的栈帧“压”在下面。ESP和EBP两个寄存器负责标定当前栈帧的范围。图中标黑的部分即为实际上ESP和EBP中间的最大区域（为了方便讲解，我们把EIP和参数也列入一个函数的函数栈帧）。图中的局部变量和参数很好理解，但EBP和EIP又是什么意思呢？我们回到IDA调试窗口。按照程序的逻辑，接下来应该是执行call
hello这行指令调用hello这个函数，函数执行完后回到下一行的mov eax,
0，其地址为080484DE.然后我们再把当前ESP和EBP的值记下来(受地址空间随机化ASLR的影响，每台电脑每次运行到此处的ESP和EBP值不一定相同)，然后按F7进入hello函数。

如图，执行完`call
hello`这一行指令后发生了如下改变。由此我们可以得知call指令是可以改变EIP“始终指向下一条指令地址”的行为的，且call指令会把call下一条指令地址压栈。我们可以理解为call
hello等价于`push eip; mov eip,
[hello]`。所以我们的第一个问题“栈帧中的EIP是什么意思”的回答就是：栈帧中的EIP是call指令的下一条指令的地址。我们继续F8单步执行。

![image.png](https://image.3001.net/images/20180629/1530261419935.png!small)![image.png](https://image.3001.net/images/20180629/15302614241519.png!small)![image.png](https://image.3001.net/images/20180629/15302614381514.png!small)如图，通过依次执行三条指令，程序为hello函数开辟了新的栈帧，同时把原来的栈帧，即执行了call
hello函数的main函数的栈帧的栈底EBP保存到栈中。继续往下执行到read函数，然后随便输入一些比较有标志性的内容，比如12345678，我们就会发现存储输入的局部变量buf就在这片新开辟的栈帧中。

![image.png](https://image.3001.net/images/20180629/15302614539629.png!small)  

我们已经接触到了栈帧的开辟与被使用情况，接下来我们再通过调试继续学习栈帧的销毁。继续F8到leave一行，此时我们会发现栈帧再次回到了刚执行完`sub
esp, 18h`的状态。

执行完leave一行指令后栈帧被销毁，整体状态回到了call hello执行前的状态。即leave指令相当于`add esp, xxh; mov esp,
ebp; pop ebp`

  

![image.png](https://image.3001.net/images/20180629/15302614887652.png!small)![image.png](https://image.3001.net/images/20180629/15302614977864.png!small)再次F8，发现EIP指向了call
hello的下一行指令，同时栈中保存的EIP值被弹出，栈顶地址+4. 即retn等同于`pop eip`

##
![image.png](https://image.3001.net/images/20180629/1530261509300.png!small)0x01
栈溢出实战  

通过上一节的调试，我们大概理解了函数栈的初始化和销毁过程。我们发现随着我们的输入变多，输入的内容离栈上保存的EIP地址越来越近，那么我们可不可以通过输入修改掉栈上的EIP地址，从而在retn指令执行完后“pwn”掉程序呢？我们按Ctrl+F2结束掉当前的调试，再试一次。为了节约时间，这回我们直接把断点下在hello函数里的`call
_read`一行。

启动调试，程序中断后界面如下

![image.png](https://image.3001.net/images/20180629/15302615248619.png!small)通过观察read函数的参数和栈中的保存的EIP地址，我们计算出两者的偏移是0x16个字节，也就是说输入0x16=22个字节的数据，我们的输入就会和栈中的EIP“接上”，输入22+4=26个字节，我们的输入就会覆盖掉EIP。那么我们构造payload为`‘A’*22+‘B’*4`，即`AAAAAAAAAAAAAAAAAAAAAABBBB`，根据我们的推测，在EIP寄存器指向retn指令所在地址时，栈顶应该是‘BBBB’。即retn执行完之后，EIP里的值将不再是图中框起来的080484DE，而是42424242（BBBB的ASCII值），按F8使IDA挂起，在docker环境中输入payload  

![image.png](https://image.3001.net/images/20180629/15302615342067.png!small)栈中的EIP果然按照我们的推测被修改成42424242了。显然，这是一个非法的内存地址，它所在的内存页此时对我们来说并没有访问权限，所以我们运行完retn后程序将会报错。  

![image.png](https://image.3001.net/images/20180629/1530261545488.png!small)选择OK，继续F8并且选择将错误传递给系统，这个进程接收到信号后将会结束，调试结束。我们通过一个程序本身的bug构造了一个特殊输入结束掉了它。

## 0x02 结合pwntools打造一个远程代码执行漏洞exp

通过上一节的内容，我们已经可以做到远程使一个程序崩溃。不要小看这个成果。如果我们能挖掘到安全软件或者系统的漏洞从而使其崩溃，我们就可以让某些保护失效，从而使后面的入侵更加轻松。当然，我们也不应该满足于这个成果，如果可以继续扩大这个漏洞的利用面，制造一个著名的RCE（远程代码执行），为所欲为，岂不是更好？当然，CTF中的绝大部分pwn题也同样需要通过暴露给玩家的一个IP地址和端口号的组合，通过对端口上运行的程序进行挖掘，使用挖掘到的漏洞使程序执行不该执行的代码，从而获取到flag，这也是我们学习的目标。

为了降低难度，我在编写hello这个小程序的时候已经预先埋了一个后门——位于`0804846B`的名为getShell的函数。

![image.png](https://image.3001.net/images/20180629/15302615679024.png!small)如图，这个函数唯一的作用就是调用system("/bin/sh")打开一个bash
shell，从而可以执行shell命令与系统本身进行交互  

![image.png](https://image.3001.net/images/20180629/15302615761536.png!small)  

正常的程序流程并不会调用这个函数，所以我们将会利用上一节中发现的漏洞劫持程序执行流程，从而执行getShell函数。

首先我们把hello的IO转发到10001端口上

![image.png](https://image.3001.net/images/20180629/15302615866592.png!small)  

然后我们从docker环境中获取其ip地址（我的是172.17.0.2，不同环境下可能不同）

然后在kali中启动python，导入pwntools库并且打开一个与docker环境10001端口（即hello程序）的连接

![image.png](https://image.3001.net/images/20180629/15302615985959.png!small)此时我们可以像上一篇文章一样打开IDA进行附加调试，在这里我就不再次演示了。从上一节的分析我们知道payload的组成应该是22个任意字符+地址。但是我们要怎么把16进制数表示的地址转换成4个字节的字符串呢？我们可以选用structs库，当然pwntools提供了一个更方便的函数p32()（即pack32位地址，同样的还有unpack32位地址的u32()以及不同位数的p16(),p64()等等），所以我们的payload就是`22*'A'+p32(0x0804846B)`。  

![image.png](https://image.3001.net/images/20180629/15302616139666.png!small)由于读取输入的函数是read，我们在输入时不需要以回车作为结束符(printf，getc，gets等则需要)，我们使用代码io.send(payload)向程序发送payload  

![image.png](https://image.3001.net/images/20180629/15302616254808.png!small)  

由于我在这里没有设置IDA附加调试，显然程序也不会被断点中断，那么这个时候hello回显我们的输入之后应该成功地被payload劫持，跳转到getShell函数上了。为了与被pwn掉的hello进行交互，我们使用io.interactive()  

![image.png](https://image.3001.net/images/20180629/15302616354414.png!small)可以看到我们已经成功地pwn掉了这个程序，取得了其所在环境的控制权。为了增加一点气氛，我们在/home下面放了一个flag文件。让我们来看一下flag是啥  

如图，我们成功地做出了第一个pwn题。为了加深对栈溢出的理解，我选了几个真实的CTF赛题作为作业，注意不要将思维固定在获取shell上哦。  

有问题大家可以留言哦也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)

