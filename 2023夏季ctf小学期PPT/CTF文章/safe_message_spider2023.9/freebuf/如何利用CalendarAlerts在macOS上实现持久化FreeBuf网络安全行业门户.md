![](https://image.3001.net/images/20201022/1603378501_5f919d45a9f476bda35e1.jpg!small)

## 写在前面的话

在这篇文章中，我们将介绍如何利用Calendar
Alerts在macOS上实现持久化，并深入讨论如何在渗透测试行动中使用这项技术。其中包括如何对Automator.app进行逆向工程分析以找到一个未记录的API来启用该技术。除此之外，我们还会提供一个针对Aotumation（JXA）代码的JavaScript来实现持久化。

PS：本文仅用于技术讨论和研究，严禁用于任何非法用途，违者后果自负，与平台及作者无关。

## Calendar.app

macOS种的一项重要功能就是Calendar
Alerts，也就是日历行程提醒，它可以根据用户设置的事件来提醒信息或执行一款应用程序。我们可以在如下图所示的GUI界面中设置一个新的事件：

![](https://image.3001.net/images/20201022/1603378537_5f919d6955c85548ec755.png!small)

在这里，我们关注的是持久化技术。研究人员Andy曾对此进行了深入分析，其中还包括针对代码执行和数据过滤方面的研究。除此之外，他还讨论了在尝试使用AppleScript以编程方式插入事件来执行此任务时遇到的问题，以及日历应用程序忽略请求的情况。还有一种方法，就是修改驱动应用程序的SQLite数据库，这种方法非常好，因为这样可以帮助我们为所有的事件都设置默认的警报，但是这种修改方式在现实场景中很难实现。

## 技术分析

在进行技术研究过程中，我还对Automator.app进行了分析，即苹果通过拖放应用程序来构建重复任务执行所使用的技术。Automator中包含了一个内置模板，可以用于构建日历警报：

![](https://image.3001.net/images/20201022/1603378594_5f919da236e5113f2272e.png!small)

通过GUI进行配置并保存之后，我们就可以看到日历中添加了一个新的事件，接下来我们就有可能通过编程的方式来执行自动化任务了。

为此，我开始深入研究EventKit的苹果开发人员文档，该框架负责与日历事件继续宁交互，但我没有发现任何关于API的说明，不过这个API允许我们通过添加警报来执行我们的应用程序。所以，我觉得有必要仔细研究一下Automator，看看它是如何做到这一点的。

首先，我使用了FileMonitor和ProcessMonitor来对Automator背后的工作机制进行了分析。它没有修改日历数据库，也没有修改任何其他文件。所以，我转而使用LLVM调试器lldb来分析。在剔除一些EventKit函数后，最后我找到了一个函数：[AMICalPluginWorkflowPersonality
finishSavingWorkflow:forOperation:atURL:error:]。分析该函数的反汇编代码后，我们可以看到一系列EventKit函数，这些函数跟苹果官方文档中提供的函数非常相似：

    
    
    <+735>:  movq   0x58d6ff62(%rip), %rdi    ; (void *)0x00007fff90b872b0: AMEventKitSoftLinking
    
    <+742>:  movq   0x58d6eb8b(%rip), %rsi    ; "EKEvent"
    
    <+749>:  callq  *%r14
    
    <+752>:  movq   0x58d6ec69(%rip), %rsi    ; "eventWithEventStore:"
    
    <+759>:  movq   %rax, %rdi
    
    <+762>:  movq   %r12, %rdx
    
    <+765>:  callq  *%r14
    
    <+768>:  movq   %rax, %rdi
    
    <+771>:  callq  0x7fff37e3e744            ; symbol stub for: objc_retainAutoreleasedReturnValue
    
    <+776>:  movq   %rax, %rbx
    
    <+779>:  movq   0x58d6898e(%rip), %rsi    ; "setTitle:"
    
    <+786>:  movq   %rax, %rdi
    
    <+789>:  movq   -0x98(%rbp), %rdx
    
    <+796>:  callq  *%r14
    
    <+799>:  movq   0x58d6ec42(%rip), %rsi    ; "setStartDate:"
    
    <+806>:  movq   %rbx, %rdi
    
    <+809>:  movq   %r15, %rdx
    
    <+812>:  callq  *%r14
    
    <+815>:  movq   0x58d6ec3a(%rip), %rsi    ; "setEndDate:"
    
    <+822>:  movq   %rbx, %rdi
    
    <+825>:  movq   %r15, -0xd0(%rbp)
    
    <+832>:  movq   %r15, %rdx
    
    <+835>:  callq  *%r14

我们可以看到，代码会使用EKEvent类来创建一个新的事件，设置事件标题、以及开始和结束的日期时间。这里有一个很有意思的函数，即[EKAlarm
procedureAlarmWithBookmark]，其部分反汇编代码如下：

    
    
    <+876>:  movq   0x58d6ec05(%rip), %rsi    ; "bookmarkDataWithOptions:includingResourceValuesForKeys:relativeToURL:error:"
    
    <+883>:  xorl   %r12d, %r12d
    
    <+886>:  movl   $0x200, %edx              ; imm = 0x200
    
    <+891>:  xorl   %ecx, %ecx
    
    <+893>:  xorl   %r8d, %r8d
    
    <+896>:  movq   %r13, %r9
    
    <+899>:  callq  *0x58cd7f17(%rip)         ; (void *)0x00007fff723f3800: objc_msgSend
    
    <+905>:  movq   %rax, %rdi
    
    <+908>:  callq  0x7fff37e3e744            ; symbol stub for: objc_retainAutoreleasedReturnValue
    
    <+913>:  movq   %rax, %r15
    
    <+916>:  movq   (%r13), %rdi
    
    <+920>:  callq  *0x58cd7f12(%rip)         ; (void *)0x00007fff723f36d0: objc_retain
    
    <+926>:  movq   %rax, %r13
    
    <+929>:  testq  %r15, %r15
    
    <+932>:  je     0x7fff37e1138a            ; <+1034>
    
    <+934>:  movq   0x58d6fe9b(%rip), %rdi    ; (void *)0x00007fff90b872b0: AMEventKitSoftLinking
    
    <+941>:  movq   0x58d6ebcc(%rip), %rsi    ; "EKAlarm"
    
    <+948>:  callq  *%r14
    
    <+951>:  movq   0x58d6ebca(%rip), %rsi    ; "procedureAlarmWithBookmark:"
    
    <+958>:  movq   %rax, %rdi
    
    <+961>:  movq   %r15, %rdx
    
    <+964>:  callq  *%r14

我们可以看到，Automator会创建一个新的书签，它是一个数据结构，指向的是磁盘中的一个特定文件。接下来，它还会创建一个EKAlarm类的新实例，并通过传入书签数据来调用该类中的procedureAlarmWithBookmark函数。

## 技术实现

接下来，我们需要通过编程的方式实现持久化攻击，然后利用这种攻击技术，将新的日历事件添加到特定的日历中。除此之外，我们还可以利用JXA代码来通过现有事件来植入后门，或者修改用户日历。【[
_参考代码_](https://github.com/FSecureLABS/CalendarPersist)】

首先，我们需要配置Mythic，然后获取Apfell
Payload。Mythic提供了比较详细的配置文档，具体请参考这篇【文档】。接下来，我们需要使用jsimport命令将功能导入到Apfell中：

![](https://image.3001.net/images/20201022/1603378701_5f919e0d11cfdf59d9cc8.png!small)

此时，我们的脚本代码已经嵌入到了Apfell
Payload中了。现在，我们需要枚举用户的日历，这里可以使用list_calendars函数来实现，不过这个操作需要用户[
_授权_](https://developer.apple.com/documentation/eventkit/ekeventstore/1507547-requestaccesstoentitytype)：

![](https://image.3001.net/images/20201022/1603378708_5f919e146e1e015eb98d4.png!small)

这里我们选择Automator日历，记录下对应的UID。接下来，我们使用JXA中的persist_calalert函数来创建新的事件。该函数调用方式如下所示：

    
    
    persist_calalert(
    
        "My Event",                                                           // Title
    
        "/Users/rookuu/Library/Apfell.app",                      // Target App
    
        60,                                                                        // Delay in seconds
    
        "daily",                                                                  // Frequency of recurrence
    
        1,                                                                          // Interval of recurrence
    
        3,                                                                          // Number of events
    
        "711CE045-7778-4633-A6FA-27E18ADD0C17" // UID of the calendar
    
    )

接下来，进程将会创建新的事件，然后将其插入到日历中。Delay in
seconds参数表示第一个事件被触发的时间，后面的参数分别代表持久化操作触发的频率、间隔以及事件数量。在我们的演示样例中，我们将连续三天每天创建一个新的事件，事件触发时便会执行我们的恶意软件：

![](https://image.3001.net/images/20201022/1603378725_5f919e259886f43d6da3a.png!small)

在Apfell中开始攻击后，我们可以在日历中看到操作结果。首次事件将在2020年10月9日
18:53触发，执行指定的应用程序。在这个演示样例中，我们将执行Apfell Payload，并且在指定的时间段内拿到Shell，实现持久化感染。

## macOS沙箱

至此，我们并没有考虑到macOS系统上的沙箱机制，因此我们还要想办法在Calendar沙箱外执行代码。

![](https://image.3001.net/images/20201022/1603378738_5f919e32c2923facbe5ce.png!small)

但是经过分析之后，我们发现我们并不需要关心沙箱逃逸的问题，因为我们一开始就没有在沙箱里面。虽然Calendar是一个沙箱化进程，但通过警报方式执行的应用并没有被沙箱化处理。如上图所示，我们执行的应用CalendarAlarmSandboxTest并没有在沙箱中。

## 参考资料

> [ _https://research.nccgroup.com/2020/05/05/exploring-macos-calendar-alerts-> part-1-attempting-to-execute-> code/)_](https://research.nccgroup.com/2020/05/05/exploring-macos-calendar-> alerts-part-1-attempting-to-execute-code/\))
>
> [
> _https://github.com/FSecureLABS/CalendarPersist﻿_](https://github.com/FSecureLABS/CalendarPersist)

