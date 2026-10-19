## 前言

 **Process
Hacker是一款针对高级用户的安全分析工具，它可以帮助研究人员检测和解决软件或进程在特定操作系统环境下遇到的问题。除此之外，它还可以检测恶意进程，并告知我们这些恶意进程想要实现的功能。**

![1.png](https://image.3001.net/images/20181123/1542988753_5bf823d13f2ea.png!small)

## 背景信息

Process Hacker是一个开源项目，可能大家第一眼看过去，会觉得Process
Hacker跟[ProcessExplorer](https://blog.malwarebytes.com/101/2016/05/process-explorer-an-introduction/)有些相似，但是Process
Hacker提供了更多的功能以及选项。而且由于它是完全开源的，所以我们还可以根据自己的需要来自定义其他功能。

### 工具地址

Process Hacker：【[下载地址](https://processhacker.sourceforge.io/)】

## 工具安装

如果你想使用这款工具的话，你只需要下载并运行安装工具即可：

![运行安装工具](https://image.3001.net/images/20181123/1542988770_5bf823e257077.png!small)

在安装过程中，你需要勾选一些配置选项：

![勾选一些配置选项](https://image.3001.net/images/20181123/1542988778_5bf823ea785e3.png!small)![勾选一些配置选项](https://image.3001.net/images/20181123/1542988778_5bf823ea87df6.png!small)

选择你需要使用到的组件，因为这些组件并不会占用太多空间，所以我建议大家直接全部勾选：

![直接全部勾选](https://image.3001.net/images/20181123/1542988786_5bf823f2a8892.png!small)![直接全部勾选](https://image.3001.net/images/20181123/1542988786_5bf823f2af1cf.png!small)![直接全部勾选](https://image.3001.net/images/20181123/1542988786_5bf823f2c8554.png!small)

到这一步就已经安装完成啦！

## 工具主界面

当你运行Process Hacker之后，你将会看到如下图所示的主界面：

![工具主界面](https://image.3001.net/images/20181124/1542988800_5bf82400727b4.png!small)

默认配置下，它会在Processes标签页中以树形图的形式显示所有当前正在运行的进程列表：

> -进程标识符（PID）
>
> -CPU使用占比（CPU）
>
> -I/O总速率
>
> -私有字节
>
> -运行进程的用户名
>
> -进程简单描述

点击特定的进程名之后，你可以查看到更多详细的信息：

![查看到更多详细的信息](https://image.3001.net/images/20181124/1542988814_5bf8240ea54da.png!small)

Services标签页主要显示当前服务和驱动的详细列表，Network标签页和Disk标签页分别显示的是各个进程对应的网络使用情况和磁盘使用情况。

![网络使用情况和磁盘使用情况](https://image.3001.net/images/20181124/1542988822_5bf8241652e03.png!small)大家可以在Hacker>Options设置中的Highlighting标签下修改标记颜色：

![修改标记颜色](https://image.3001.net/images/20181124/1542988831_5bf8241f3e0b9.png!small)

### 释放控制

Process Hacker给你提供的每一个选项都可以帮助你删掉那些原本删不掉的文件，之所以删不掉，是因为有其他的进程在使用它们…

Process Hacker可以帮助我们识别目标进程，并切断进程跟文件之间的关联，整个处理过程如下：

> 1、 在主菜单中点击“Find handles orDLLs”；
>
> 2、 在Filter栏中输入完整或部分文件名，然后点击“Find”；
>
> 3、 在结果中找到正确的文件名，然后点击那一行；
>
> 4、 点击鼠标右键，从菜单栏中选择“Go toowning process”；
>
> 5、 Processes窗口中会高亮标记这个进程；
>
> 6、 右键点击高亮进程，选择“Terminate”；
>
> 7、 终止进程之后，你就可以尝试删除之前被锁定的文件了；

### 浏览网络信息

在Process Hacker的帮助下，大家还可以浏览特定进程的网络通信情况，即使你关闭了某些进程，你还可以启用“Restore previous
session”功能来查看所有的进程通信数据：

![查看所有的进程通信数据](https://image.3001.net/images/20181124/1542988866_5bf8244251d89.png!small)

### 从内存中导出字符串信息

你可以使用Process
Hacker来导出内存中的进程数据，分析人员可以使用这些导出数据来搜索内存中的字符串信息，然后使用脚本或[Yara规则](https://blog.malwarebytes.com/security-world/technology/2017/09/explained-yara-rules/)来对目标进程进行初始分类。如果目标应用是恶意软件，那我们很快就会发现它们。

右键点击正在运行的目标进程，选择“Create dump
file…”，选择导出数据的保存路径。ProcessHacker从内存中导出的数据文件带有.dmp后缀，大家可以使用十六进制编辑器或文本编辑器（或[mimikatz](https://www.offensive-security.com/metasploit-unleashed/mimikatz/)）来浏览这些文件。

### 多功能多用途

ProcessHacker是一款“多才多艺”的工具，它跟Process Explorer非常相似，但是它的功能又比Process
Explorer强大得多。高级用户可能会更喜欢Process
Hacker，如果你在使用中遇到了问题，你可以直接在【[论坛](https://wj32.org/processhacker/forums/index.php)】上寻求帮助。

 ***参考来源：[malwarebytes](https://blog.malwarebytes.com/101/how-tos/2018/11/advanced-tools-process-hacker/?utm_source=twitter&utm_medium=social&utm_campaign=q3fy19)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

