# 看我如何通过Linux Rootkit实现文件隐藏

阅读量 **266591**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-12-06 13:59:29

 **x**

##### 译文声明

本文是翻译文章，文章原作者 jordan9001，文章来源：0x00sec.org

原文地址：<https://0x00sec.org/t/hiding-with-a-linux-rootkit/4532>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0132a6e668a96c8db8.jpg)

译者：[eridanus96](https://www.anquanke.com/member/125661)

预估稿费：180RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

## 前言

一直以来，我希望能深入了解Linux内核内部是如何工作的。为实现这一点，有一个比较好的思路是写一个小的Rootkit
PoC。大家可以在[这里](https://github.com/jordan9001/superhide)找到相关Rootkit代码。

这是一个非常简单的Rootkit。其功能是，隐藏特定前缀的文件使其不可见。然而，假如我们知道这些文件或文件夹的位置，就仍然可以访问它们。但通过“ls
-a”命令以及文件管理器是无法看到的。此外，通过lsmod或者/proc/modules也无法将它们列出。

## 关于ls

我们首先尝试一下如何借助ls来找到这些文件。我们知道，当某个程序需要借助网络、文件系统或其他系统特定活动进行工作时，它就必须经过内核。也就是说，在此时它将使用系统调用。我们可以在这个表格中，查到64位Linux系统的系统调用。

为了找出ls所使用的系统调用，我们使用了一个名为[Strace](https://linux.die.net/man/1/strace)的工具。Strace将会列出程序所使用的系统调用。当我们执行strace
ls后，会出现很多程序连接产生的杂项，但如果我们继续向下查看， 会发现有以下几行：

    
    
    openat(AT_FDCWD, ".", O_RDONLY|O_NONBLOCK|O_DIRECTORY|O_CLOEXEC) = 3
    
    getdents(3, /* 11 entries */, 32768) = 344
    
    getdents(3, /* 0 entries */, 32768) = 0
    
    close(3) = 0

由此看来，我们需要重点分析的系统调用是getdents。在执行后，ls可能会调用libc函数、readdir，但最终还是会调用getdents。

在具体分析getdents之前，首先让我们来讨论一下如何进入内核。

## 可装载内核模块（LKM）

在Linux系统中，如果我们想在内核中运行代码，我们可以借助于可装载内核模块（LKM）。本文将不会花用太多篇幅阐述它是如何工作的，大家可以参考这一篇文章（链接）。我们的思路是将自定义的模块加载到内核。一些有用的内核符号就会被内核导出，我们便能够去使用它们，或者也可以通过kallsyms_lookup_name函数来获取。在内核中，我们需要拦截getdents调用，并对它返回的值进行更改。此外，我们也希望可以稍微隐藏一下自己的行为，由于该模块是在系统中，因此就不会那么明显。

那么，接下来要解决的问题就是我们要如何Hook getdents，以及Linux内核会如何响应系统调用。

## 系统调用表

在内核之中，存在一个系统调用表。其中的系统调用编号（系统调用发生时rax的值）是其Handler在其表中的偏移量。在Windows系统中，由于[PatchGuard内核保护系统](https://en.wikipedia.org/wiki/Kernel_Patch_Protection)的存在，系统调用表是无法接触到的。但在Linux系统中，我们就可以避开它。

需要注意的是，如果我们将系统调用表弄乱，将会造成非常严重的问题，这样的PoC无疑是愚蠢的，所以还是要考虑将Hook放置在其他地方。

系统调用表位于sys_call_table，它是系统内核的一块区间，其作用是将调用号和服务连接起来，当系统调用某一个进程时，就会通过sys_call_table查找到该程序。然而，它并不是一个可导出并供使用的Linux内核符号，因此，我们有下面这4种方式可供选择：

  1. **暴力搜索。** 这种方式更适用于32位系统上，但在64位系统上也是理论上可行的。
  2. **找到使用系统调用表的函数。** 有几个使用sys_call_table符号的函数，如果我们通过这些函数进行解析，就可以找到它们的引用。
  3. **在其他地方寻找。** 其实，如果不在内核中寻找，也是非常容易找到的。
  4. **不使用系统调用表。** 这是一个最好的方案，如果我们不在系统调用表上Hook，我们还可以将Hook放在Handler上。

针对这个简单的模块，我们会选择上面的第3种方式。不使用系统调用表的方式也比较有趣，我将会在后续另写一篇文章进行讲解。对于第3种方式，我们只需要读取并分析[/boot/System.map-$(uname
-r)文](https://en.wikipedia.org/wiki/System.map)件即可。我们的这一操作，可以在将自身添加到内核的同时进行，由此就确保会得到正确的地址。在我的代码中，build_and_install.sh进行了这项工作。我生成了一个将使用可装载内核模块（LKM）编译的头文件。

    
    
    smap="/boot/System.map-$(uname -r)"
    echo -e "#pragma once" &gt; ./sysgen.h
    echo -e "#include <linux/fs.h>" >> ./sysgen.h
    symbline=$(cat $smap | grep '\Wsys_call_table$')
    set $symbline
    echo -e "void** sys_call_table = (void**)0x$1;" >> ./sysgen.h

## 关于Hook

系统调用表是只读的，但当我们在内核中的时候，这并不会成为较大的阻碍因素。在内核中，[CR0](https://en.wikipedia.org/wiki/Control_register#CR0)是一个控制寄存器，可以修改处理器的操作方式。其中的第16位是写保护标志所在的位置，如果该标志为0，CPU就可以让内核写入只读页。Linux为我们提供了两个很有帮助的函数，可以用于修改CR0寄存器，分别是write_cr0和read_cr0。

在我的代码中，我通过 write_cr0(read_cr0() & (~WRITE_PROTECT_FLAG)); 关闭了写保护机制，随后在 #define
WRITE_PROTECT_FLAG (1<<16)通过 write_cr0(read_cr0() |
WRITE_PROTECT_FLAG)；将其重新打开。

随后，将当前getdents Handler的入口保存，这样我就可以在删除模块时恢复原样。之后，我们使用
sys_call_table[GETDENTS_SYSCALL_NUM] = sys_getdents_new;写了一个新的Handler。

其中的sys_getdents_new函数，只负责运行原始处理程序，并检查其结果，删除任何以我们指定前缀开头或是与我们模块有关的条目。

## 从/proc/modules实现隐藏

在Linux系统中，/proc/文件系统作为用户空间与内核之间的接口。它们并不是传统意义上的文件，在打开、写入或读取proc文件时，它会调用内核中的处理程序，动态地得到所需信息并进行相应操作。通过Hook
/proc/modules文件的Read
Handler，我们可以筛选出任何引用到我们模块的相应行。为了实现这一点，首先需要知道/proc/modules在内核中注册的位置。

我在Github上搜索了[“proc_create(“modules”)“的源代码](https://github.com/torvalds/linux/blob/ef0010a30935de4e0211cbc7bdffc30446cdee9b/kernel/module.c#L4227)，并找到了以下几行：

    
    
    static int __init proc_modules_init(void){
    
    proc_create("modules", 0, NULL, &proc_modules_operations);
    
    return 0;
    
    }

由此看来，proc_modules_operations是一个包含Handler函数的结构。尽管它并不是一个导出的符号，但我们已经在使用System.map文件了，就不妨再使用一次它。

一旦它被导入，放置Hook的过程就会非常简单，proc_modules_operations->read =
proc_modules_read_new;。在proc_modules_read_new中，我们还进行和之前一样的读取，并筛选出我们需要的相应行。

## 结论

至此，我们就拥有了第一个Linux rootkit。此后，我们还可以通过在系统调用表之外进行Hook，以及通过在内核中隐藏模块来改进。

希望上述内容已经讲解得足够清楚明白，如果大家有任何问题，或者发现我的代码中存在任何Bug，请随时提出。我也期待能有更多人提出Rootkit方面的更深入分析并相互学习。

本文翻译自0x00sec.org [原文链接](https://0x00sec.org/t/hiding-with-a-linux-rootkit/4532)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **P!chu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/89215](/post/id/89215)

安全客 - 有思想的安全新媒体

本文转载自: [0x00sec.org](https://0x00sec.org/t/hiding-with-a-linux-rootkit/4532)

如若转载,请注明出处： <https://0x00sec.org/t/hiding-with-a-linux-rootkit/4532>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [linux](/tag/linux)
  * [rootkit](/tag/rootkit)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01bd1dba67fe13cdc6.png) P!chu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

