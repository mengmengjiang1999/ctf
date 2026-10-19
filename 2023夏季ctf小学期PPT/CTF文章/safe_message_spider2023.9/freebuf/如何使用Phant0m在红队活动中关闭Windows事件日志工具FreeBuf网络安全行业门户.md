## 关于Phant0m

Phant0m是一款针对红队研究人员设计的安全测试工具，在该工具的帮助下，广大红队研究人员可以在渗透测试活动中轻松关闭Windows事件日志工具。

Svchost在所谓的共享服务进程的实现中至关重要，在共享服务进程中，许多服务可以共享一个进程以减少资源消耗。将多个服务组合到一个进程中可以节省计算资源，这一点对于NT设计人员来说尤为重要，因为创建Windows进程比其他操作系统（例如Unix系统）需要更多的时间，而且还会消耗更多的内存。

简而言之，这意味着，在Windows操作系统上，svchost.exe负责管理服务，而这些服务实际上是在svchost.exe之下的线程中运行的。Phant0m主要针对的是事件日志服务，并且能够找到事件日志服务所对应的进程，然后检测并终止负责事件日志服务的线程。因此，虽然事件日志服务似乎在系统中运行（因为Phant0m没有终止进程），但它实际上并不运行（因为Phant0m终止了线程），此时的系统也不会再收集日志了。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/hlldz/Phant0m.git

## 工具机制

![](https://image.3001.net/images/20220331/1648736118_6245b7766aefbb3897a18.png!small)

### 检测和终止线程

Phant0m使用了两种技术来检测和终止事件日志服务的线程。

 **技术1**

在运行Windows
Vista或更高版本的计算机上注册每个服务时，服务控制管理器（SCM）会为该服务分配一个唯一的数字标记（升序）。然后，在服务创建时，将标记分配给主服务线程的TEB。接下来，该标记将被发送到主服务线程创建的每个线程。例如，如果Foo服务线程创建了一个RPC工作线程（注意：RPC工作线程稍后不再使用线程池机制），那么该线程将具有Foo服务的服务标签。

因此，在这种技术中，Phant0m将使用NtQueryInformationThread
API检测事件日志服务的线程，以获取线程的TEB地址，并从TEB读取子进程标记。然后，它会终止与事件日志服务相关的线程。

 **技术2**

在技术2中，Phant0m将检测与线程关联的DLL名称。Windows事件日志服务会使用wevtsvc.dll，其完整路径为“%WinDir%\System32\wevtsvc.dll”。如果线程正在使用该DLL，那么它就是Windows事件日志服务的线程，然后Phant0m会终止该线程。

### 检测事件日志服务

Phant0m使用两个不同的选项来检测事件日志服务的进程ID。第一种是通过SCM（服务控制管理器）进行检测，第二种是通过WMI（Windows
Management Instrumentation）进行检测。如需选择哪种方法来检测事件日志服务的进程ID，可以修改main.cpp文件中的对应内容。

比如说，如果希望通过SCM检测进程ID，则应按照下列样例进行编辑（一次只能使用一种技术，不可同时使用两种）：

    
    
    // PID检测和配置
    
    #define PID_FROM_SCM 1 // 如果设置为1，将通过SCM获取事件日志服务的PID
    
    #define PID_FROM_WMI 0 // 如果设置为1，将通过WMI获取事件日志服务的PID

或者，如果你想终止线程，可以参照下列配置方式（一次只能使用一种技术，不可同时使用两种）：

    
    
    // TID检测和配置
    
    #define KILL_WITH_T1 1 // 如果设置为1，则使用上述的技术1
    
    #define KILL_WITH_T2 0 // 如果设置为1，则使用上述的技术2

## 工具使用

我们可以将Phant0m以单独的exe可执行程序或反射型DLL来使用。在Microsoft Visual
Studio中打开该项目，进行设置（选择对应的工具技术）并编译。除此之外，我们还可以将反射型DLL与Cobalt
Stikei一起使用，具体可参考phant0m.cna脚本文件。

![](https://image.3001.net/images/20220331/1648736349_6245b85d05268a8b99d31.png!small)

当然了，我们甚至还可以使用Donut将相关脚本代码转换为DLL和Shellcode。

## 项目地址

 **Phant0m：** 【[ _GitHub传送门_](https://github.com/hlldz/Phant0m)】

## 参考资料

> [ _https://azure.microsoft.com/tr-tr/blog/detecting-in-memory-attacks-with-> sysmon-and-azure-security-center/_](https://azure.microsoft.com/tr-> tr/blog/detecting-in-memory-attacks-with-sysmon-and-azure-security-center/)
>
> [
> _http://www.insomniacsecurity.com/2017/08/27/phant0m.html_](http://www.insomniacsecurity.com/2017/08/27/phant0m.html)
>
> [ _https://medium.com/@7a616368/event-log-tampering-part-1-disrupting-the-> eventlog-service-8d4b7d67335c_](https://medium.com/@7a616368/event-log-> tampering-part-1-disrupting-the-eventlog-service-8d4b7d67335c)
>
> [ _https://www.exploit-db.com/docs/english/45898-flying-under-the-> radar.pdf?rss_](https://www.exploit-db.com/docs/english/45898-flying-under-> the-radar.pdf?rss)
>
> [ _https://gallery.technet.microsoft.com/Denetim-ve-Loglamann-Elli-> cbed0000_](https://gallery.technet.microsoft.com/Denetim-ve-Loglamann-Elli-> cbed0000)
>
> [ _https://www.ired.team/offensive-security/defense-evasion/disabling-> windows-event-logs-by-suspending-eventlog-service-> threads_](https://www.ired.team/offensive-security/defense-> evasion/disabling-windows-event-logs-by-suspending-eventlog-service-threads)
>
> [ _https://blog.cybercastle.io/event-log-service-between-offensive-and-> defensive/_](https://blog.cybercastle.io/event-log-service-between-> offensive-and-defensive/)
>
> [ _https://malwarenailed.blogspot.com/2017/10/update-to-hunting-mimikatz-> using-sysmon.html_](https://malwarenailed.blogspot.com/2017/10/update-to-> hunting-mimikatz-using-sysmon.html)
>
> [ _https://hacker.observer/defense-evasion-windows-event-> logging-t1562-002/_](https://hacker.observer/defense-evasion-windows-event-> logging-t1562-002/)
>
> [ _https://labs.jumpsec.com/pwning-windows-event-logging-with-yara-> rules/_](https://labs.jumpsec.com/pwning-windows-event-logging-with-yara-> rules/)
>
> [ _https://hannahsuarez.github.io/2019/IncidentResponseNotes-Attackers-> EventLog/_](https://hannahsuarez.github.io/2019/IncidentResponseNotes-> Attackers-EventLog/)

