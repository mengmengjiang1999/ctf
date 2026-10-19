***本文原创作者：ForrestX386，本文属FreeBuf原创奖励计划，未经许可禁止转载**

##  **0x00 前言**  

**在我最近的一些安全应急响应经历中，遇到了入侵者利用一些小的有意思tricks——将自己的ssh登录痕迹隐匿于w和last命令中，这对于一些经验不足或者没有相关意识的运维管理人员来说，可能不会发现这些已经发生的非法登录行为，亦或者既使觉察出有点异常，但却不理解为啥能将ssh登录痕迹隐匿于w和last命令（这种隐匿不涉及修改相关日志文件）。**

 **本文将会为大家介绍和阐述这种隐匿登录痕迹的手法以及如何确切的发现他们的痕迹。**

##  **0x01 正文**

###  **1、现象及原理解释**

首先有一个正常的登录(bastion 登录至code-audit)，从pts/0登录 ( 14:31分正常登录)。

在code-audit 上输入 w 命令显示。

![pts_0.png](https://image.3001.net/images/20180831/1535727795_5b8958b30c98d.png!small)

在code-audit 上输入 last 命令显示。

![pts_0_last.png](https://image.3001.net/images/20180831/1535727806_5b8958be7f668.png!small)

然后我利用一个小trick 将我的ssh登录痕迹隐匿于w 和last 命令中，且看下图。

![hide_ssh_connect1.png](https://image.3001.net/images/20180831/1535727823_5b8958cf33f06.png!small)

在code-audit 上输入 w 命令显示。

![same_pts_w.png](https://image.3001.net/images/20180831/1535727837_5b8958ddcc442.png!small)

在code-audit 上输入 last 命令显示。

![same_last.png](https://image.3001.net/images/20180831/1535727846_5b8958e67e485.png!small)

这时候，我们就会有以下疑问（黑人问号）。

 **1）为什么w和last都没有记录呢?**

这是因为w 命令显示信息来源于utmp，last 来源于wtmp，并不是所有程序登录的时候都会调用utmp 和wtmp
日志记录接口，只有交互式会话，才会调用utmp 和 wtmp的日志记录接口，比如 通过tty 或者pts或者图形界面登录的都会调用utmp 和wtmp
日志记录接口，然后我们在使用w 和last 命令的时候就会发现登录信息

 **2）ssh -lroot 192.168.12.51 /usr/bin/bash 为什么不属于交互式会话**

ssh -lroot 192.168.12.51 /usr/bin/bash
其实就相当于登录之后直接调用bash这个名，此时系统没有为其分配tty，不算一个完整交互式会话，只不过bash
接受输入，然后有输出，让我们误以为是交互式会话，其实不然，你可以将/usr/bin/bash 替换成/usr/bin/ls 试一下，就是简单执行以下就退出了

![ssh_ls.png](https://image.3001.net/images/20180831/1535727859_5b8958f3bdc15.png!small)

还有一种看起来更像是交互式会话的，但实际却不是的一种登录技巧，这种方式也会将登录行为隐匿于w 和 last 命令

![hide_ssh_connect2.png](https://image.3001.net/images/20180831/1535727881_5b89590972ada.png!small)

-T 表示不分配伪终端 （正常的会话，在分配伪终端之后才会调用utmp和wtmp的日志接口）

/usr/bin/bash -i 表示在登录之后 调用bash命令

-i 表示是交互式shell

### 2、如何发现隐匿的ssh登录行为

如果是隐匿的ssh正在进行，可以通过lsof 或者 netstat 或者ps 命令发现

 **1）通过lsof发觉异常ssh登录**

![lsof_ssh.png](https://image.3001.net/images/20180831/1535727969_5b89596126e7e.png!small)

两条已建立的连接，一条是通过pts/0正常登录的（前文已交代），一条就是隐匿于w和last的ssh登录

2）通过ps命令发现异常ssh登录

![ps_notty.png](https://image.3001.net/images/20180831/1535727981_5b89596d7c13f.png!small)

这里有个notty的 sshd 进程，说明就是通过上文所述的trick隐匿于w和last命令的ssh登录行为

如果是历史ssh 隐匿登录行为，如何找出历史登录行为呢

通过分析/var/log/secure 日志（有的系统是/var/log/auth.log）

![secure_ssh.png](https://image.3001.net/images/20180831/1535727994_5b89597a3a0d6.png!small)

从 Accepted publickey for root from 192.168.12.54 一行可以得出ssh的登录时间

从Disconnected from 192.168.12.54 port 43000 一行可以得出ssh的退出时间

如果从secure中的分析结果和 last 对不上，那么这些对不上的登录行为有可能就是通过本文所介绍的隐匿方式登录的

##  **0x02. 总结**

​ 其实像scp 、sftp 等也涉及到ssh登录，但却不会在w 和last中留下日志的程序，也都是因为他们不输入交互式会话。希望本文能给大家带来帮助

​ 本文涉及重要参考资料如下

> ​ <https://news.ycombinator.com/item?id=1937139>
>
> ​ <https://unix.stackexchange.com/questions/20070/user-logged-in-by-sftp-> does-not-show-up-in-w>

***本文原创作者：ForrestX386，本文属FreeBuf原创奖励计划，未经许可禁止转载**

