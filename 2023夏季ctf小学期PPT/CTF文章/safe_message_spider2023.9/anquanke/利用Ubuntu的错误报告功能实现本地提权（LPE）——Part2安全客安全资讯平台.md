# 利用Ubuntu的错误报告功能实现本地提权（LPE）——Part2

阅读量 **1274266**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-12-31 16:00:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 github，文章来源：securitylab.github.com

原文地址：<https://securitylab.github.com/research/ubuntu-apport-CVE-2019-7307>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01cd34f92ae310e7ca.jpg)

在第二篇文章中，我将重点介绍 CVE-2019-730，apport的TOCTOU漏洞，它允许本地攻击者在错误报告中包含系统上任何文件的内容。

## 漏洞

Apport允许在主目录下放一个名为 `~/.apport-ignore.xml`
的文件。它允许你指定一个可执行程序的自定义列表，但是，如果将`~/.apport-ignore.xml`符号链接替换为一个不属于你的文件(如/etc/shadow)，会发生什么情况呢?处理的代码在[report.py](https://git.launchpad.net/ubuntu/+source/apport/tree/apport/report.py?h=applied/ubuntu/bionic-devel&id=2fc8fb446c78e950d643bf49bb7d4a0dc3b05429#n962)第962行：

    
    
    if not os.access(ifpath, os.R_OK) or os.path.getsize(ifpath) == 0:
        # create a document from scratch
        dom = xml.dom.getDOMImplementation().createDocument(None, 'apport', None)
    else:
        try:
            dom = xml.dom.minidom.parse(ifpath)
        except ExpatError as e:
            raise ValueError('%s has invalid format: %s' % (_ignore_file, str(e)))
    

如上所见，它用`os.access`检查用户是否有权访问文件。如果权限检查通过，则它将调用`xml.dom.minidom.parse`来解析XML。这是“time
of check to time of use”（[TOCTOU](https://en.wikipedia.org/wiki/Time-of-check_to_time-of-use)）漏洞的经典示例。如果这个文件在`os.access`检查时是有效的，但是在调用`xml.dom.minidom`之前，我迅速替换其文件的符号链接指向其他文件。则可以欺骗其使用提升的特权来读取我没有权限访问的文件

## apport中取消特权的技巧

你可能想知道为什么`os.access`检查会失败，因为apport是一个root进程。原因是apport在执行过程中分两个阶段取消了特权。  
第一阶段发生在
[Apport](https://git.launchpad.net/ubuntu/+source/apport/tree/data/apport?h=applied/ubuntu/bionic-devel&id=2fc8fb446c78e950d643bf49bb7d4a0dc3b05429#n455)的455行：

    
    
    # Partially drop privs to gain proper os.access() checks
    drop_privileges(True)
    

第二阶段发生在
[601行](https://git.launchpad.net/ubuntu/+source/apport/tree/data/apport?h=applied/ubuntu/bionic-devel&id=2fc8fb446c78e950d643bf49bb7d4a0dc3b05429#n601)：

    
    
    # Totally drop privs before writing out the reportfile.
    drop_privileges()
    

“取消部分特权”和“完全取消特权”是什么意思？这与 进程的 真实、有效和保存的用户ID有关：

| RUID(真实用户ID) | EUID(有效用户ID) | EUID(保存的用户ID)  
---|---|---|---  
root 进程 | 0 | 0 | 0  
“partially drop privs”(取消部分特权) | 1001 | 0 | 0  
read files safely(安全读取文件) | 1001 | 1001 | 0  
“totally drop privs”(完全取消特权) | 1001 | 1001 | 1001  
  
RUID（实际用户id）确定进程的所有者，EUID（有效用户id）确定进程可以读写哪些文件。这表示apport处于“partial drop
privs(取消部分特权)”状态时，它仍然可以读取系统上的任何文件。

要确保apport不会意外地使用root权限来读取或写入文件，正确的方法是首先进入我在表格中命名为“read files
safely(安全读取文件)”的状态。由于保存的用户ID（SUID）仍然是root用户，因此该过程可以暂时进入”read files
safely”(安全读取文件)状态，然后在读取文件完成后恢复为”partially drop privs”(取消部分特权)。注意，向”totally
drop privs”(完全取消特权)的转换是不可逆的。

``os.access`检查是不一样的，因为它使用RUID而不是EUID来检查真实用户是否有权访问文件。这就是为什么存在TOCTOU漏洞的原因，调用`os.access`时，Apport处于”partially
drop
privs”(取消部分特权)状态。也就是说，它将拒绝不属于我的文件，但是如果我可以绕过`os.access`检查，那么后续调用的`xml.dom.minidom.parse`将能够读取任何文件，因为EUID仍然是root。我可以在调用`os.access`之后替换`~/.apport-ignore.xml`的符号链接。

## 与CVE-2019-11481对比

我在[fileutils.py](https://git.launchpad.net/ubuntu/+source/apport/tree/apport/fileutils.py?h=applied/ubuntu/bionic-devel&id=20c98691144e843bf1ab8428603beedd34e993ad#n335)的第335行发现了一个类似的Bug:

    
    
    def get_config(section, setting, default=None, path=None, bool=False):
        '''Return a setting from user configuration.
    
        This is read from ~/.config/apport/settings or path. If bool is True, the
        value is interpreted as a boolean.
        '''
        if not get_config.config:
            get_config.config = ConfigParser()
            if path:
                get_config.config.read(path)
            else:
                get_config.config.read(os.path.expanduser(_config_file))
    

这段代码使用root(EUID)打开文件`~/.config/apport/settings`。大概看，由于`os.access`处不存在检查，以为比其他漏洞更容易利用。经过进一步审查，我发现不是，原因在于错误处理的方式不同。例如，如果我想使用这个漏洞来读取`/var/shadow`的内容，它不是一个有效的XML文件，而且它的格式也不正确，不能作为apport文件解析。因此，无论哪种情况，都会在apport中触发一个解析错误。在`~/.config/apport/settings`的情况下，将导致apport立即中止。但是在`~/.apport-ignore.xml`的情况下，格式不正确的文件将被忽略，apport将继续运行。因此，我发现`~/.apport-ignore.xml`更容易利用。

我向Ubuntu报告了`~/.config/apport/settings`漏洞: [bug
1830862](https://bugs.launchpad.net/ubuntu/+source/apport/+bug/1830862)。此问题已修复并分配到[CVE-2019-11481](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-11481)。

## 漏洞利用方案

这个漏洞让我可以通过替换`~/.apport-ignore.xml`的符号链接来欺骗apport加载系统上的任何文件。但是，我感兴趣的文件几乎都不会是有效的XML文件，因此它将导致解析错误，而apport将忽略它。这如何让我访问禁止的信息？

这是我巧妙的方案：

![](https://securitylab.github.com/static/23f21d79d9f3e425720c9d07ea9c9e5e/ubuntu_apport_exploit_plan_CVE-2019-7307.svg)

主要思路是，即使被禁止的文件将触发解析错误并被忽略，但它仍然会加载到apport的堆中。这意味着如果apport崩溃，那文件的内容也将包含在错误报告中。这是方案中事件的顺序：

  1. 1.通过启动`/bin/sleep`来发送使其崩溃`SIGSEGV`。
  2. 2.启动Apport，为`/bin/sleep`生成错误报告。
  3. 3.在合适的时机替换`~/.apport-ignore.xml`符号链接，让apport将禁止的文件加载到内存中。
  4. 4.通过发送一个`SIGSEGV`来造成apport崩溃。
  5. 5.启动第二个apport来生成第一个apport崩溃的错误报告。
  6. 6.第二个apport为第一个apport创建一个错误报告，其中包含核心转储中禁止的文件副本。

###  阻碍

事情不是那么容易。我遇到了几个问题。比较明显的是，符号链接切换的时机至关重要，所以我预计很难正确做到，但也有一些意想不到的问题，我将在下面的章节中介绍。

Apport有两个缓解机制来防止其自身运行。在apport第30行的评论中注释，这是为了避免“如果发生一系列崩溃将会导致系统瘫痪”。

第一个缓解机制是一个名为`/var/crash/.lock`的文件锁。当apport启动时，它使用lockf在该文件上设置一个锁，以防止另一个apport同时运行。

有趣的是，lockf文件锁只是建议!实际上，正如Victor
Gaydov在这篇优秀的[文章](https://gavv.github.io/articles/file-locks/#posix-record-locks-fcntl%5D)中解释，锁实际上与一个`[i-node,
pid]`相关联。这意味着如果在第一个apport设置了锁之后，用一个新文件替换`/var/crash/.lock`，那么第二个apport将看到一个不同的I节点，因此两个apport就可以同时持有锁`/var/crash/.lock!

用新文件替换/var/crash/.lock的技巧依赖于是否有删除或移动该文件的权限。由于/var/crash目录设置了sticky
(粘滞位)，这表示着必须拥有该文件。幸运的是，/var/crash可以写入，因此只要/var/crash/.lock不存在就可以创建。当我在5月29日第一次向Ubuntu提交漏洞报告时，我认为这会使漏洞无法利用。那是因为在我工作的笔记本电脑上，/var/crash/.lock几乎总是存在并且属于root。后来我发现/var/crash/.lock每天被一个计划任务:/etc/cron.daily/apport删除。锁文件经常存在于我的工作笔记本电脑上，是因为我经常故意让应用程序崩溃。但是在典型的Ubuntu系统上，由于日常计划任务，它不可能在任何给定时间存在。

在我的漏洞报告中，我建议/var/crash/.lock应始终被root拥有，以缓解这种类型的漏洞利用。虽然我自己并不认为它是一个漏洞，但是Sander
Bos提交了一个关于这个问题的漏洞报告。为它分配到CVE-2019-11485，并通过更改锁文件存储的目录来修复。

第二个缓解机制是基于内核中的`RLIMIT_CORE`。`RLIMIT_CORE`是限制core文件（核心转储文件）大小，`RLIMIT_CORE ==
1`用作一个特殊的值，表示该进程是一个错误报告程序，在它崩溃时不应该生成核心转储文件(以防止递归)。在此[评论](https://bugs.launchpad.net/ubuntu/+source/linux/+bug/498525/comments/3)中，我找到了对此缓解机制的解释。

我为`RLIMIT_CORE`缓解机制感到幸运。原来可以使用prlimit修改另一个进程的`RLIMIT_CORE`！当然，需要有合适的权限才能这样做，我发现只要apport进入”totally
drop
privs”(完全取消特权)状态，它就会起作用。不幸的是，不可能使用prlimit来增加`RLIMIT_CORE`的值，但是可以将它降低到0，这就可以利用此漏洞了。

###  信号处理

我方案的一部分是通过发送一个`SIGSEGV`来破坏apport。但这不起作用,因为apport为`SIGSEGV`设置了一个信号处理程序:

    
    
    def setup_signals():
        '''Install a signal handler for all crash-like signals, so that apport is
        not called on itself when apport crashed.'''
    
        signal.signal(signal.SIGILL, _log_signal_handler)
        signal.signal(signal.SIGABRT, _log_signal_handler)
        signal.signal(signal.SIGFPE, _log_signal_handler)
        signal.signal(signal.SIGSEGV, _log_signal_handler)
        signal.signal(signal.SIGPIPE, _log_signal_handler)
        signal.signal(signal.SIGBUS, _log_signal_handler)
    

这样做的动机是防止对自己进行递归操作。对我来说幸运的是，`setup_signals`设置处理程序的信号列表不够完整。[signal手册](https://manpages.ubuntu.com/manpages/bionic/man7/signal.7.html)的第7页部分有一个名为“Standard
signals”的表。以下是一段摘录:

信号 | 值 | Action | 含义  
---|---|---|---  
SIGINT | 2 | Term | 键盘中断  
SIGQUIT | 3 | Core | 从键盘退出  
SIGILL | 4 | Core | 非法指令  
… | … | … | …  
  
在“Action”列中包含“Core”的任何信号都将触发一个Core Dump(核心转储)。Apport的信号处理程序列表包括最常见的`core-generating`信号，但它还不够完整，还有好几种可供选择，我的exploit使用了`SIGTRAP`。

## 实施漏洞攻击

我已经在[GitHub](https://github.com/github/security-lab/blob/8a4842917730357bf43d3148fb4fb0b3a7d5b9d6/SecurityExploits/Ubuntu/Apport_TOCTOU_get_ignore_dom_CVE-2019-7307/gencrashreport.cpp)上公布了我的POC(proof-of-concept)的源代码。它主要根据我上面描述的方案执行，但有一些调整来解释上面讨论的阻碍。这是修改后的方案中的事件顺序：

  1. 1.启动`/bin/sleep`。
  2. 2.创建`/var/crash/.lock`，方便后面可以删除它。
  3. 3.使用`SIGINT`(程序终止信号)Kill掉`/bin/sleep`。
  4. 4.启动Apport，为`/bin/sleep`生成错误报告。
  5. 5.在合适的时机替换`~/.apport-ignore.xml`符号链接，让apport将禁止的文件加载到内存中。
  6. 6.用一个新文件替换`/var/crash/.lock`，来绕过文件锁并使第二个apport与第一个apport同时运行。
  7. 7.使用prlimit将apport的`RLIMIT_CORE`设置为零。
  8. 8.通过发送一个`SIGTRAP`来造成apport崩溃。
  9. 9.启动第二个apport来生成第一个apport崩溃的错误报告。
  10. 10.第二个apport为第一个apport写出一个错误报告，其中包含核心转储中禁止文件的副本。

接下要讨论的是我如何计算切换符号链接的时间。最初，我认为很难这个程序的漏洞，因为 os.access
对文件的调用与打开之间存在非常短的时间间隔。但是事实证明，如果使用c语言编程，赢得与Python的比赛是非常容易的。在PoC中，发生切换时的关键时机在[第155行](https://github.com/github/security-lab/blob/8a4842917730357bf43d3148fb4fb0b3a7d5b9d6/SecurityExploits/Ubuntu/Apport_TOCTOU_get_ignore_dom_CVE-2019-7307/gencrashreport.cpp#L155)  
。我用inotify来计时。通过运行`sudo strace -e file -tt -p <apport
PID>`，我发现一个名为`expatbuilder.cpython-36.pyc`的文件总是在`~/.apport-ignore.xml`解析之前打开。通过观察该文件上的`IN_OPEN`事件，我可以非常精确地设置切换时间。

当我终于能够利用这个漏洞时，我很兴奋地查看了错误报告，并在/var/crash中看到了以下内容：

    
    
    kev@constellation:~$ ls -al /var/crash/
    total 4492
    drwxrwsrwt  2 root whoopsie   12288 Nov  5 12:26 .
    drwxr-xr-x 17 root root        4096 Jul 17 19:31 ..
    -rw-r-----  1 root whoopsie 4583201 Nov  5 12:26 _usr_share_apport_apport.0.crash
    

该文件属于root，发生了什么？我确信它将属于我，因为我的PoC直到第一个apport进入”totally drop
privs”(完全取消特权)状态后才发送SIGTRAP。当apport进程在崩溃时完全归我所有，所以我应该能够查看错误报告吗?这个问题是由apport如何确定崩溃进程的所有者引起的。这发生在get_pid_info中，通过os.stat运行`/proc/[pid]/stat`。在源代码中分散了一些注释，例如[此处](https://git.launchpad.net/ubuntu/+source/apport/tree/data/apport?h=applied/ubuntu/bionic-devel&id=2fc8fb446c78e950d643bf49bb7d4a0dc3b05429#n70)和[此处](https://git.launchpad.net/ubuntu/+source/apport/tree/data/apport?h=applied/ubuntu/bionic-devel&id=2fc8fb446c78e950d643bf49bb7d4a0dc3b05429#n171)，对此进行了解释。`/proc/[pid]/stat`即使是在过渡到”totally
drop privs”(完全取消特权)状态之后，apport还是作为root进程启动的，因此归root所有。我还没有找到任何方法来破坏这种保护。

当我查看文件的内容时，这就是我看到的内容：

![](https://p0.ssl.qhimg.com/t011f3cb61213ae0daa.png)

另一个好消息是该exploit非常短暂和稳定。我以为符号链接切换的时间安排可能会使它不稳定，但是我发现它每次都能完美运行。

因此，一切都不会丢失。尽管错误报告是由root拥有的，但是whoopsie依然可以读取它，这说明，如果我可以在whoopsie守护程序中找到漏洞，我也就可以读取错误报告的内容。

本文翻译自GitHub Security Lab

本文翻译自securitylab.github.com
[原文链接](https://securitylab.github.com/research/ubuntu-apport-CVE-2019-7307)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **qwert** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/195752](/post/id/195752)

安全客 - 有思想的安全新媒体

本文转载自:
[securitylab.github.com](https://securitylab.github.com/research/ubuntu-apport-CVE-2019-7307)

如若转载,请注明出处： <https://securitylab.github.com/research/ubuntu-apport-CVE-2019-7307>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [LPE](/tag/LPE)

 **+1** __5赞

 __收藏

![](https://p2.ssl.qhimg.com/t01de37baca165a5b78.png) qwert

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

