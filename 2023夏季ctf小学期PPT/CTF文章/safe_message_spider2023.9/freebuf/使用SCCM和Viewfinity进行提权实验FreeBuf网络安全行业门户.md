**如今越来越多的公司开始限制用户以本地管理员的身份来运行软件，随之带来的问题是，如何允许用户执行某些管理行为，例如安装已批准的软件。市场上有一些工具旨在解决这个问题。但我也发现了一个问题，即当用户被允许与安装程序进行交互时，他们通常可以提升他们当前在计算机上的权限。本文我将为大家演示，如何使用SCCM和Viewfinity进行提权。**

## SCCM Software Center

系统中心配置管理器（SCCM）支持管理员将软件安装程序发布到Software Center，或当前登录的用户，更常见的是以NT
Authority\System权限运行。 有关SCCM部署类型的更多信息，[请参阅此处](https://docs.microsoft.com/en-us/sccm/apps/deploy-use/create-applications#specify-user-experience-options-for-the-deployment-type)。

根据安装程序命令的部署方式，恶意用户可能会使用这些列入白名单的安装程序来提升其计算机上的权限。通常，如果允许用户与安装程序进行交互，这将是可能的。下面是一个场景的示例。

可以看到Software Center发布的应用程序“Flowdock”可用于安装，并被标记为“Attended Install”。

![image1.png](https://image.3001.net/images/20180609/15285042598038.png!small)

安装程序运行，并允许我们设置安装路径，这对于此攻击（通常）是必不可少的条件。因为如果程序被安装到Program Files，低权限用户将无法写入安装目录。
相反，如果我们可以控制安装路径，则可以将安装路径更改至我们拥有足够权限的位置。这里，我选择将该程序安装到我的桌面。

![image2.png](https://image.3001.net/images/20180609/15285042758515.png!small)

继续安装进程，直至看到完成按钮的界面。接着，我们启动PowerShell。

![image4.png](https://image.3001.net/images/20180609/15285042947017.png!small)

在PowerShell中备份flowdock.exe程序，并将cmd.exe复制到flowdock.exe。然后，我们选中“Launch
Flowdock”复选框完成安装。

![image3.png](https://image.3001.net/images/20180609/15285043091976.png!small)

cmd.exe启动后，我们键入whoami命令，可以看到当前我正以NT Authority\System权限运行。

![image5.png](https://image.3001.net/images/20180609/15285043269324.png!small)

## Viewfinity

在为某客户做测试时，我使用owerUp等工具进行初始探测后并没有任何的发现。因此，我决定开始手动查看。根据以往的经验，我首先观察的就是当前运行的进程。或许我能找到一个0day，因为我有足够的时间和耐心去一一的测试这些服务。一番浏览后，一个Viewfinity的进程引起了我的注意。这是一个权限管理软件，与Software
Center有些不同，因为它可以用于黑名单、白名单和特权提升。

起初，我并不知道这个软件，当我浏览文件系统时，我看到一个名为vf_elevate.exe的可执行文件。经过一番研究后，我找到了配置文件，并试图弄清楚这个程序是如何工作的。下图是该配置文件的片段截图。

![image6.png](https://image.3001.net/images/20180609/15285043527944.png!small)

由于在多个位置引用了组和权限，因此XML难以导航，我决定信任程序组名称。我下载了Sysinternals Process
Explorer，以及在配置文件中引用的Wireshark版本。这里，我没有使用上述SCCM中描述的方法。而是按照通常的做法，安装Wireshark并立即启动了它。

![image7.png](https://image.3001.net/images/20180609/15285043736346.png!small)

通过Process Explorer我们可以看到，该进程的Integrity
Level为high，这说明它具有完整的管理员权限，但当前仍以低权限用户身份运行。这与Software
Center的行为方式不同。我无法确定Viewfinity使用什么机制来提升权限（如果你知道，可以在Twitter上告诉我）。

![image8.png](https://image.3001.net/images/20180609/15285043937074.png!small)

在捣鼓Wireshark时，我几乎尝试了所有的可能性，例如使用打开或导出对话框启动cmd。我发现从这些对话框中启动的任何内容都将以medium等级运行，并且不会继承Wireshark的权限。幸运的是，这里有一个Lua脚本控制台被内置在Wireshark中。我使用Lua启动了cmd，可以看到它的进程启动级别为high，这相当于我获取了一个具有管理员权限的shell。

![image9.png](https://image.3001.net/images/20180609/15285044321868.png!small)![image12.png](https://image.3001.net/images/20180609/15285044325852.png!small)

为了验证我当前的运行身份，我创建了一个用户，并将他们添加到本地管理员组中。

![image10.png](https://image.3001.net/images/20180609/15285044632317.png!small)

使用net user命令查看用户列表，可以看到新创建的用户以成功被添加至管理员组。

![image11.png](https://image.3001.net/images/20180609/15285044865138.png!small)

 ***参考来源：[ninja](https://ninja.style/post/privesc/)，FB小编 secist
编译，转载请注明来自FreeBuf.COM**

