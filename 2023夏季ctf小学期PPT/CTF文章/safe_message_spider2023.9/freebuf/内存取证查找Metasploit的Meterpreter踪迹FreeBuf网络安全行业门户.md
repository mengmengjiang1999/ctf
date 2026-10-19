**Metasploit是一个非常受欢迎的渗透测试框架，被视为安全测试人员手中的一把利器。但在另一方面由于他过于强大，因此也常常被一些恶意攻击者所利用。当然，在本文我们主要讨论的是关于内存取证，这对于我们来说是至关重要的。因为我们（受害者）的机器极有可能会被恶意攻击者，注入Meterpreter（一种先进的，可动态扩展的Metasploit有效载荷），这是一种完全驻留在内存中的shell，并且不会向受害者的驱动器写入任何内容。下面，我将向你展示如何使用取证框架Volatility来找出Metasploit的蛛丝马迹。**

在分析内存镜像时，首先我们应该收集有关操作系统的信息，以选择正确的Volatility配置文件。最佳做法是在内存镜像时记录系统版本，因为Volatility检测结果可能会有误。如果你是从第三方获得的镜像并且版本未知，那么我建议你使用
**imageinfo** 插件：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234095862221.png!small)  

以上的检测结果显示，该镜像的系统版本为Windows 7 SP1 x86，这次的结果非常准确我的系统版本确实为该版本。我们使用 **pslist**
插件，来查看下进程列表：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/1523409609848.png!small)  

你有发现什么不对的地方吗？一个PID 3000的进程，用户可能启动了防病毒更新进程？但奇怪的是，该进程在启动42秒后退出。让我们使用 **netscan**
插件进一步的查下网络连接情况：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234096262378.png!small)  

可以看到，一个未知的进程与192.168.1.39:4444建立了连接。有经验的人一眼就能反应出，4444端口Metasploit的默认回连端口。Meterpreter注入目标系统进程，让我们尝试使用
**malfind** 插件找到它：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234096432557.png!small)  

这看起来Meterpreter像是被迁移到了PID为3312的svchost.exe上。让我们将它转储到一个文件，并使用杀毒软件查杀看是否能被正确识别：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234096632924.png!small)![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234096631015.png!small)  

从检测结果中我们可以看到，虽然不是百分百的免杀，但大部分杀毒软件包括许多主流的杀毒软件，如McAfee，Malwarebytes，DrWeb等，竟然都没有检测出该恶意进程。

如果你喜欢使用YARA规则进行恶意软件检测，那么你可以编写自己的规则或在线查找一些规则，然后使用 **yarascan** 插件：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234096903047.png!small)  

在这里我写了一个非常简易的规则：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234097604628.png!small)  

现在让我们回到之前的pslist输出，可以看到这里唯一运行的Web浏览器是Internet Explorer（iexplore.exe，PID
2568和2640）。我们使用 **iehistory** 插件来查看下历史浏览记录：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234097864051.png!small)  

没错！受害者使用我们看到的URL从服务器下载了一个名为 **antivirus_update.exe**
的程序。但这里我有个疑惑，是什么促使他们这么做的呢？让我们用 **memdump** 插件转储Internet Explorer的进程内存并搜索“
**antivirus** ”字符串：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234098115667.png!small)  

正如你所看到的，攻击者利用了一些社工技巧以及将地址做了短网址处理，从而使受害者被骗。当受害者下载并运行文件后，攻击者就会获得一个meterpreter
session。为了更加的隐蔽，攻击者将其迁移到了svchost.exe（PID 3312）。

这里我还有个疑问，受害者真的运行了它吗?让我们找到执行的证据！首先，我们使用 **shimcache**
插件，它可以跟踪应用程序的最近修改时间，文件完整路径和执行标志：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234098353123.png!small)  

可以看到文件确实被执行了！让我们继续，运行 **userassist** 插件获取注册表上的证据：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234098567096.png!small)  

除了以上的办法，还有一些其它手段例如，预取文件。当然，你也可以在内存中找到这些证据，Volatility甚至有一个插件--**prefetchparser** 。

不幸的是，受害者系统禁用了预取，所以我们没有办法获得任何证据。

好了我们已经收集了很多的证据，但还有一件事需要我们检查 - 持久性！这里有一个非常好用的插件可以帮助我们检测一些常用的权限维持技术 –
**autoruns** ：

![内存取证：查找Metasploit的Meterpreter踪迹](https://image.3001.net/images/20180411/15234098793906.png!small)  

从检测结果可以看到，受害者无需再执行该恶意程序，每次重启系统它都会自动运行。

***参考来源：[forensicfocus](https://articles.forensicfocus.com/2018/04/03/finding-metasploits-meterpreter-traces-with-memory-forensics/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

