# Windows调试——从0开始的异常处理（上）

阅读量 **568690**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-28 14:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0163fe78263af4ce59.jpg)

windows调试艺术主要是记录我自己学习的windows知识，并希望尽可能将这些东西在某些实际方面体现出来。

ps:本篇文章中的内容涉及到上次文章刚提到过的一些知识点，如果中间有不懂的地方可以参考上一篇文章<https://www.anquanke.com/post/id/173586>

再ps：所有文中提到另外会写的……尽量不鸽（咕咕咕）

windows的异常处理一直是大家关心的重点，不管是对操作系统的学习还是windows的漏洞利用，都逃不过异常处理，这篇文章将会从windows异常的基础、维护异常信息的结构、异常的详细处理、SEH和VEH等方面来详细讨论Windows下的异常处理机制并通过《格蠹汇编》一书中的几个课后实验来说明异常在调试中的实际应用。

## 什么是异常？

简单来说异常就是对于非预期状况的处理，当我们在运行某个程序时出现了异常状况，就会进入异常处理流程

    
    
    发现异常 -> 寻找处理异常的方法 -> 恢复执行或者发生错误
    

异常又可以分为软件异常（由操作系统或应用程序引发的）、硬件异常（由cpu产生），其中硬件异常又和中断、系统调用等行为有着密切的联系，下面就来具体讨论一下。

###  硬件异常

硬件异常可以分为三种：

  * fault，在处理此类异常时，操作系统会将遭遇异常时的“现场”保存下来（比如EIP、CS等寄存器的值），然后将调用相应的异常处理函数，如果对异常的处理成功了（没成功的情况会在下文中提到），那就恢复到原始现场，继续执行。最经典的fault例子莫过于Page Fault了，在分页机制下，当我们读到某个还未载入到内存的页时，就会触发该异常，操作系统会将该页载入内存，然后重新执行读取该页的指令，这是分页机制实现的重要机制。
  * trap，在处理此类异常时，操作系统会将异常的“下文”保存，在处理异常后，直接执行导致异常的指令的下一条指令。我们在调试过程中常用的断点操作就是基于这类异常的，当我们在某处下断点时调试器会将原本此处的指令对应的十六进制保存下来，然后替换第一个字节替换为0xCC的，也就是int 3，造成断点异常，中断（此处的中断用的是break，而我们一般说的中断是interrupt，请读者务必区分清楚）到调试器，程序在运行到此处就会停止等待下一步的指令，而当我们继续执行时调试器就会将该指令替换为原来的指令，程序也就恢复正常执行了。不知道大家有没有注意过，在进行程序调试时经常会看见hex界面显示大量的“烫烫烫”，这其实是0xcc对应的中文字符，因为这些地址的内容程序并不想让我们访问，一旦我们访问这些地址，就会读到0xcc，程序也就“中断”了。
  * abort，中止异常，主要是处理严重的硬件错误等，这类异常不会恢复执行，会强制性退出。

在windows系统中，硬件异常和中断被不加区分的存放在了一个向量表中，也就是我们常说的IDT（interruption descriptor
table），我们可以使用windbg（注意要在内核调试状态，笔者打印的是64位的情况）的!idt指令来查看IDT，不过windbg打印出的并不是真正的IDT结构，而是经过“解析”后的，更易于我们查看。表中前面的序号代表着它对应的是第几个中断或异常，后面的函数则是对这种异常或中断的处理函数，也叫做异常处理例程。

    
    
    lkd> !idt
    Dumping IDT: fffff80743286000
    00:    fffff80740dd5100 nt!KiDivideErrorFaultShadow
    01:    fffff80740dd5180 nt!KiDebugTrapOrFaultShadow    Stack = 0xFFFFF8074328A9E0
    02:    fffff80740dd5200 nt!KiNmiInterruptShadow    Stack = 0xFFFFF8074328A7E0
    03:    fffff80740dd5280 nt!KiBreakpointTrapShadow
    04:    fffff80740dd5300 nt!KiOverflowTrapShadow
    05:    fffff80740dd5380 nt!KiBoundFaultShadow
    06:    fffff80740dd5400 nt!KiInvalidOpcodeFaultShadow
    07:    fffff80740dd5480 nt!KiNpxNotAvailableFaultShadow
    08:    fffff80740dd5500 nt!KiDoubleFaultAbortShadow    Stack = 0xFFFFF8074328A3E0
    09:    fffff80740dd5580 nt!KiNpxSegmentOverrunAbortShadow
    0a:    fffff80740dd5600 nt!KiInvalidTssFaultShadow
    0b:    fffff80740dd5680 nt!KiSegmentNotPresentFaultShadow
    0c:    fffff80740dd5700 nt!KiStackFaultShadow
    0d:    fffff80740dd5780 nt!KiGeneralProtectionFaultShadow
    0e:    fffff80740dd5800 nt!KiPageFaultShadow
    0f:    fffff80740dd62f8 nt!KiIsrThunkShadow+0x78
    10:    fffff80740dd5880 nt!KiFloatingErrorFaultShadow
    11:    fffff80740dd5900 nt!KiAlignmentFaultShadow
    12:    fffff80740dd5980 nt!KiMcheckAbortShadow    Stack = 0xFFFFF8074328A5E0
    13:    fffff80740dd5a80 nt!KiXmmExceptionShadow
    14:    fffff80740dd5b00 nt!KiVirtualizationExceptionShadow
    15:    fffff80740dd5b80 nt!KiControlProtectionFaultShadow
    

真正的IDT实际上是维护了多个门描述符（GD），每一项大小为8（64位为16），IDRT寄存器中保存着IDT的基地址，我们想具体找某个GD的话直接利用IDTR+8*offset即可。门描述符结构如下：

![](https://ws4.sinaimg.cn/large/006tKfTcly1g1ahvf68xrj30to0r2n0p.jpg)

GD大致由segment
selector（段选择子）、offset（选定段后的偏移）、DPL（描述符特权级）、P（段是否存在）组成，在上一次的《windows调试艺术》中我已经详细的说明了如何通过该结构寻找GDT/IDT进而找到相应的内容，这里就不再展开说了。

当windows系统启动时，winLoad会在实模式下分配一块内存，使用CLI指令来禁止中断的使用，利用LIDT（Load
IDT）指令将IDT表的位置和长度等信息交给CPU，接着系统恢复保护模式，这时的执行权交还给了入口函数，调用SIDT（set
IDT）拿到之前存储的IDT的信息，并将其记录到PCR中，接着其他处理器也会进行初始化的操作，复制并修改自己的IDT，在一切准备就绪后，调用STL指令恢复中断的使用。调用的函数链如下：

    
    
    winLoad -> kiSystemStartup -> kiInitializePcr ->keStartAllProcessors -> kiInitProcessors
    

这里的PCR也就是上一次《windows调试艺术》中我们所说的Ring0下fs寄存器，我们可以使用内核调试状态下的windbg来查看相关的内容

![](https://ws2.sinaimg.cn/large/006tKfTcly1g1bdtjlm13j30kr09lmxd.jpg)

  * 第一个字段指向的是TIB，上一篇文章具体解释过了，我们重点关注的是第一个，exception的list的地址，也就是异常处理注册链表，是我们后面的重点。
  * Prcb是指Process Control Block，实际上在操作系统将IDT的信息交付给PCR的过程中，也会交给它。
  * IRQL也就是中断请求级别，0代表当前cpu的IRQL是内核态
  * IDT和GDT分别是前面提到的两个表的地址
  * TSS是任务段地址
  * CurrentThread也就是当前线程的EThread地址
  * NextThread是下一个准备执行的线程的地址
  * idleThread是一个优先级最低的线程，也可以把它叫做空闲线程，可以简单理解为它是个在“休息”的线程

在上述过程进行完成之后，实际上我们的异常还是仅仅被“处理了一部分”而已，大多数IDT中记录的函数都只是对异常进行了包装和描述，之后还要采用异常分发机制来进一步进行异常处理。

###  软件异常

软件异常是由操作系统或应用程序产生的，它又包含了windows为我们定义好的异常处理和我们自己写的异常处理（各种编程语言中的try-catch结构）。这类异常追根溯源都是基于RaiseException这个用户态API和NtRaiseException的内核服务建立起来的。RaiseException的函数原型：

    
    
    void RaiseException(DWORD dwExceptionCode , DWORD dwExceptionFlags,DWORD nNumberofArguments,const DWORD* lpArguments);
    

  * dwException是异常状态码，可以在NtStatus.h中找到，应用程序也可以有自己的异常状态码
  * nNumberofArguments和lpArguments是用来定义异常的数据

函数的功能十分简单，它会将异常的相关信息传入一个维护异常的结构，叫做EXCEPTION_RECORD，然后再去调用RtlRaiseException函数，该结构定义如下：

    
    
    typedef struct _EXCEPTION_RECORD {
      DWORD                    ExceptionCode;
      DWORD                    ExceptionFlags;
      struct _EXCEPTION_RECORD *ExceptionRecord;
      PVOID                    ExceptionAddress;
      DWORD                    NumberParameters;
      ULONG_PTR                ExceptionInformation[EXCEPTION_MAXIMUM_PARAMETERS];
    } EXCEPTION_RECORD;
    

  * ExceptionCode为异常状态码，可以在NtStatus.h中找到，RaiseException的dwException就对应此项
  * ExceptionFlags为异常的标志，16个bit中有一部分被拿出来当作标志位，包括像是8位的栈错误、1位的异常不可恢复等等，RaiseException的dwExceptionFlags对应此项
  * ExceptionRecord是指向下一个异常的指针
  * ExceptionAddress保存了异常的发生地址
  * NumberParameters是 ExceptionInformation数组中参数的个数，RaiseException的nNumberofArguments对应该项
  * ExceptionInformation也就是异常的描述信息，RaiseException的lpArguments对应该项

之后调用的RltRaiseException会将当前的上下文保存到CONTEXT结构中，此后调用的函数会维护一个TrapFrame（即栈帧的基址）和异常的处理次数的标志，这里不再赘述，调用链如下：

    
    
    用户：RaiseException -> RltRaiseException -> NtRaiseException -> KiRaiseException 
    内核：RtlRaiseException -> NtRaiseException -> KiRaiseException
    

## 异常的的分发处理

上面说到了硬件异常会通过IDT去调用异常处理例程（一般为KiTrap系列函数），而软件异常则是通过API的层层调用传递异常的信息，但这都是最基础的处理，实际上最后二者是殊途同归，都会走到KiDispatchException函数来进行异常的分发。

异常分发的简化流程图如下，笔者绘图能力有限……可以在看完后面的具体分析后大家自己加以完善。

![](https://ws3.sinaimg.cn/large/006tKfTcly1g1bq3ehmyaj30my126n0p.jpg)

首先来看看KiDisPatchException函数的函数原型

    
    
    void KiDispatchException (
        IN PEXCEPTION_RECORD ExceptionRecord,
        IN PKEXCEPTION_FRAME ExceptionFrame,
        IN PKTRAP_FRAME TrapFrame,
        IN KPROCESSOR_MODE PreviousMode,
        IN BOOLEAN FirstChance
        )
    

ExceptionRecord也就是前面提的描述异常的结构，TrapFrame指向的结构用来描述发生异常时候的上下文，PreviousMode来说明异常来自Kernel还是User，最后的FirstChance用来表示异常是不是第一次被处理，实际上这些结构的集合就形成了一个虚拟的、完整的“异常”结构，再去进行下面的处理。

进入上图，首先就要对异常的涞源进行判断，右边是内核的异常，右边是用户的异常，我们一个一个来看

###  Kernel

但PreviousMode为0时，就会进入Kernel的异常分发，系统会维护一个KiDebugRoutine的函数，当内核的调试器启动时，它就帮我们把异常送往了内核调试器，而在未启动时，它只是一个“存根”函数（stub），返回一个False。这一步也就是图中的debug

当第一次debug返回False后会接着调用RtlDispatchException，函数的原型如下：

    
    
    BOOLEAN RtlDispatchException(PEXCEPTION_RECORD ExceptionRecord,PCONTEXT ContextRecord)
    

两个参数就是异常的结构和上下文结构了，可以拿Windbg查看，函数的大致操作如下：

  * 取异常登记链表的头指针
  * 遍历异常登记记录
  * 检查异常登记记录的有效性，有效则执行 
    * 异常已处理，返回
    * 没有处理，返回并继续遍历
    * 如果是内嵌异常则进行特殊处理

取得异常登记链表的头指针的也就是上一篇文中提到的fs寄存器，fs:[00h]，fs指向了TEB结构，而TEB第一个offset又是一个TIB的结构，TIB的第一个也就是异常登记链表了

经过上面的处理后，如果异常已经被处理了那也就结束了，如果没有处理的话就会进行第二轮调试，重复上面的debug内容，如果依然是没有启用调试器的话就那么就会把这个异常当作UnhandleException，也就是我们常说的未处理异常，在kernel下未处理异常可是个大问题，毕竟这可是操作系统最最重要的也最最完善的内核，这样的未处理异常一般都不是小问题，为了防止异常引发更大的问题，这时候系统就会调用KeBugCheckEx中止系统运行显示蓝屏，并将导致异常的地址打印在屏幕上。

###  user

当PreviousMode==1时就进入了用户态的异常分发，相较于Kernel来说，user的异常处理还包括了我们自己在编写程序的过程中用到的try
catch，下面就具体来看看。

首先还是检查是否有调试器，具体的措施和Kernel相仿，不过找的函数是内核的DbgForwardException，这个函数涉及到了用户态的调试，以后要有机会还会单独写这个的知识点。简单点说就是找找用户态的调试器是不是要接手这个异常，如果成了就交给它处理，如果没有的话那就会通过KeUserExceptionDispatcher来找到KiUserExceptionDispatcher函数，要注意，此时已经返回到了用户态，且异常的相关信息（比如KTRAP_FRAME）已经被放入了用户态的栈上。之后会调用了RtlDispatchException（注意，该函数依然名字和作用都与Kernel的几乎相同，但是它是位于NTDLL的，而Kernel的则是位于NTOSKRNL）来遍历异常处理器的链表，但这次的链表又了“保底措施”，在链表的最末尾是UnhandledExceptionFilter（未处理异常过滤函数），一旦走到了这里，那就会出现“应用程序错误”的对话框并强制结束程序（之后会写这个函数的详细分析），异常也就算是处理完成了。

既然有了UnhandledExceptionFilter那岂不是所有的异常都会最终被直接处理了，那第二轮又是怎么回事？实际上如果在非调试状态下确实如此，用户态的异常如果在非调试状态下的话仅仅只有一轮的分发，而只有在调试状态下才会进行第二轮，再次判断调试器是否要接手异常。

## 格蠹汇编练习题

下面是我选择的几个需要涉及到异常知识的《格蠹汇编》一书的课后题，通过这些实际的例子来看看异常在程序调试中的重要性，源文件大家可以自行百度下载。

###  调试笔记之侦查广告插件

首先我们要windbg设置为windows的JIT（just in
time）调试器，最简单的方法是在管理员权限下cmd进入windbg所在的目录，直接运行下边的命令：

    
    
    WinDbg -I
    

当然如今这种命令一步实现的可能性不大……因为我们大部分人的pc都是64位的windows10，并且还都装了vs，这种情况下我们会有x86和x64两种JIT默认，且默认都为vs的调试器，我们上面的操作仅仅是注册了其中的一种而已，这个时候我们就需要修改注册表了

我们进入regedit后找到下面的两个路径（分别是64位和32位的）：

    
    
    HKEY_LOCAL_MACHINESOFTWAREWOW6432NodeMicrosoftWindows NTCurrentVersionAeDebug
    HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindows NTCurrentVersionAeDebug
    

里面有Auto和debuger两项，Auto的意思是在程序出错时是否会调用调试器，而Debuger则是保存了我们指定的调试器的路径，这里直接删除掉就好，接着分别在x86和x64的windbg目录下运行上面的命令就好了

再次打开程序发现直接打开了windbg

![](https://ws1.sinaimg.cn/large/006tKfTcly1g0yzbgb18wj315k072q4n.jpg)

我们可以看到Access
violation，意思是访问违例，而下面的汇编代码就是具体的情况。可以看到执行的指令是将0赋予ecx的地址，当然只看这里我们还是看不出什么问题，接下来就进入正题了

    
    
    .symfix 你的符号路径
    

set symbol store path的意思，也就是从微软那边将需要的符号信息下载到你指定的路径，便于调试

    
    
    kPL
    

k是用来展示给定的线程的栈帧并展示相关的信息，P能够显示每一个函数的所有的参数，包括参数的数据类型、名称和值，L的意思是隐藏source
lines（源文件路径的意思），注意 **它们是大小写敏感的**

![](https://ws3.sinaimg.cn/large/006tKfTcly1g0z32tvxr8j30po06k75m.jpg)

###  修复因误杀而瘫痪的系统

这一章节没有实验，但有一些很重要的知识点，简单总结一下

作者的朋友电脑出了问题，最开始是菜单不见了，再之后仅仅是进入启动界面几秒就黑屏了，通过双机调试得到了以下的错误信息：

![](https://ws2.sinaimg.cn/large/006tKfTcly1g10z9pmlg9j30zi02wgng.jpg)

第一串数字是Stop code（停止码，可通过帮助文档查询），大括号中第一串是有关进程的信息，第二串是错误码，可以通过!error指令查询。在这里Stop
Code的意思是系统进程终止，错误码的意思是对象不存在，也就是说尝试bug的原因是因为有些必要的东西没有了，我们利用db指令来查询一下进程的信息

![](https://ws3.sinaimg.cn/large/006tKfTcly1g10zh4wr1jj30qc04a40u.jpg)

发现有windows Logon
Process的信息，这是关系到用户登录的一个进程，在windows启动过程中，第一个创建的用户态进程是SMSS.exe（session manager
subsystem），之后的进程关系如下

    
    
    SMSS.exe -> winlogon.exe -> explore.exe
             -> CSRSS.exe
    

而最后的explore是资源管理器，开始菜单就是它来维护的，而当SMSS创建这两个进程时，如果创建失败，就会进行bug
check，如果有调试器的话就会调用系统中断连接到调试器，没有的话就会蓝屏重启。分析到这里，我们就有理由相信，电脑的重启很有可能是由于winlogon被删除而导致的。

但winlogon这么容易被删除吗？首先它作为系统文件，是有一定的保护机制的，其次，作为一个一直在运行的程序，它的虚拟内存文件不可能被直接删除。所谓虚拟内存文件是基于虚拟内存机制的一类文件，它有两种，一种是专用的页面文件，一般在磁盘的根目录，文件名叫做pagefile.sys；第二种是文件映射机制加载过的磁盘文件本身，比如用户态的dll文件和exe文件，加载后充当了虚拟内存文件的角色，而之后内存管理器会和文件系统会达成“协议”，不再允许删除该文件。这也就是病毒文件绞尽脑汁也要加载到内存的原因，一旦运行了，拿它在某种程度上就“无敌”了

作者根据电脑的故障时间进行了文件排查，最终将目光锁定在了一个名字中带有delay的反病毒软件的def文件，正是因为我们上面提到的问题，所以现在很多杀毒软件都支持“延时删除”的策略，但启动过程执行到SMSS.exe时会检查如下的注册表键执行操作

    
    
    HKEY_LOCAL_MACHINESYSTEMControlSet001ControlSession Manager PendingFileRenameOperations
    

该键的构造为srcFilePathdstFilePath，即移动文件，当我们将dstFilePath设置为0时，也就会将src文件删除了。经过作者修改该文件，也就解决了问题。

由于书的年代过于久远所以采取了延时删除的策略，实际上在windwos8中已经引入了一种新的技术 — ELAM（Early Launch Anti-Malware），反病毒的驱动在得到微软的特殊数字签名（Microsoft Windows Early Launch Anti-malware
Publisher）后可以在系统启动过程中优先加载并扫描接下来加载驱动的数字签名，如果判定为恶意代码的话就会在未启动前直接将其删除。

###  拯救发疯的Windows 7

题目背景是作者的朋友电脑window7的操作系统崩溃，最后给了个dump出的文件.

Windbg载入dump文件

![](https://ws2.sinaimg.cn/large/006tKfTcly1g0y1elp2dej31d003y750.jpg)

可以很明显的看到报了个stack buffer overrun的提示，也就是说导致系统出问题的很可能是栈溢出，我们利用以下的命令查看一下

    
    
    kn
    

k是用来展示给定的线程的栈帧并展示相关的信息，n是显示栈的编号

![](https://ws3.sinaimg.cn/large/006tKfTcly1g0z3ajhkifj30wu0fcn1t.jpg)

可以看到它调用了Werp开头的几个函数，全称是windows error
report，也就是错误报告的意思，往下看有UnhandleExceptionFilter（未处理异常过滤函数），它是处理未处理异常的关键函数，同时也是系统终止掉一个进程前做最后处理的地方，应用程序错误（application
error）和我们上面设置的JIT都是从这个函数发起的。根据栈回朔，往下就是引发这个未处理异常的函数了，也就是umpo模块里的某个函数。

    
    
    lmvm
    

lm的意思是list load
modules，v显示了详细的信息，m是要进行模块名称的匹配，在这的目的主要是看看是不是正常的（也就是官方的）一个模块，因为它之后就是错误处理了，所以我们有必要检查他一下，可以看到这个模块是没有问题的

![](https://ws2.sinaimg.cn/large/006tKfTcly1g0z3jshpabj31hi0d6diw.jpg)

继续看栈回朔，发现了问题，umpo模块中的SendPowerMessage函数的ret地址和其他函数的差距很大，并且windbg提醒我们这个地址不是在任何一个已知的模块中的，很有可能是发生了溢出错误，而report_gsfailure也正是cookie被覆盖所产生的异常处理信息（也就是GS机制，做pwn的应该是很熟悉了，这里不再多说）

    
    
    dd 009afb30-4
    

此处地址为ebp-4，实际上也就是cookie，我们检查一下cookie的内容，cookie和父函数的值都是00640064，明显不正常

![](https://ws3.sinaimg.cn/large/006tKfTcly1g0z40pgklzj30kw0283yj.jpg)

    
    
    db 009afb30-204 L220
    

我们查看该函数的变量空间来看看到底读取了什么导致了发生溢出，这里的204是由两个函数地址之差算出来的，记得还要减去cookie和ebp的大小（注意L要稍大一些，因为溢出了所以要想看到网站的读取信息就要多读几个字节）

![](https://ws3.sinaimg.cn/large/006tKfTcly1g0z498c157j30y00q4af1.jpg)

可以看到确实是溢出了，而产生的原因就是因为c:userspicturesSample
PicturesDesertddddd…d.jpg的文件路径字节数太多所导致的，我们手动改一下文件名就好了

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Asa9ao** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/175293](/post/id/175293)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Windows](/tag/Windows)
  * [系统安全](/tag/系统安全)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t01898082a58ca4c715.png) Asa9ao

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

