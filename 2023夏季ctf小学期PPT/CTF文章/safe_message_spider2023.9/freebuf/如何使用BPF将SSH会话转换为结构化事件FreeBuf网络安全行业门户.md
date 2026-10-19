![](https://image.3001.net/images/20200303/1583167724_5e5d38ec0cdfa.png!small)

##  写在前面的话

 **Teleport 4.2引入了一个名叫增强型会话记录（Enhanced Session
Recording）的新功能，该功能可以接收一个非结构化的SSH会话，并输出结构化事件的数据流。这是Teleport的一次进步，因为它使用了新技术（eBPF，或现在可以简称为BPF）来弥补Teleport审计能力的一些不足。接下来，我们将给大家介绍这个新功能，并讨论其中的一些技术细节。**

##  背景介绍

Teleport在最早的版本中就引入了会话记录功能，会话记录可以捕捉用户在终端中的打印信息，并可在之后的安全审计过程中以视频的方式提供回放记录。这个功能的优势就在于，这些记录很容易查看和理解，并且可以提供用户在会话建立期间的相关活动以及上下文，这对于安全审计活动来说是非常有价值的。

当然，它的不足之处就在于，用户可以通过多种方式来绕过会话记录。

1、混淆处理-比如说下列命令：

    
    
    echo Y3VybCBodHRwOi8vd3d3LmV4YW1wbGUuY29tCg== | base64 –decode | sh

当该命令解码后即为“curl
[http://www.example.com](http://www.example.com/)”，但是SSH会话记录中并不会包含curl命令。

2、Shell脚本-如果用户上传并执行了一个脚本，那么脚本中的命令将无法被会话记录捕捉到，而是直接将脚本文件输出。

3、终端控制-终端支持各种控制命令，最常用的应该是sudo了，禁用终端的echo将允许我们在运行命令的同时不会被SSH会话记录捕捉到。

##  技术实现

为了解决这个问题，Teleport需要一种方法来在会话持续的过程中将非结构化的SSH会话转换为结构化的事件流。那么这种结构化事件流中应该包含什么呢？

我们对多种方法进行了研究，我们研究的内容从诸如regex模式匹配之类的特殊方法到更复杂的尝试，比如自己解析原始SSH会话。我们还研究了Linux提供的各种API和系统，如Audit、fanotify和BPF。

###  在选择使用哪种技术来构建时，我们有以下几个关键的标准：

> 1、减小误报，理想情况下为0。如果你的系统误报率非常高，那么你对警报的关注度可能会因此而减少，这将导致关键问题被忽略。
>
> 2、减少由监控所引起的任何性能影响，理想情况下为0，这也能减轻向用户添加额外资源的负担。

这些特定的方法都会存在误报的问题。我们在解析和解释组成SSH会话的字节流时，无法在不引起错误警告的情况下保证数据的准确率。而且由于性能方面的原因，我们排除了[Linux
Audit](https://twitter.com/dinodaizovi/status/1171762209090953217)。

##  BPF是什么？

Brendan
Gregg，是BPF程序的开发人员，他经常将BPF描述为一种“[新型软件](http://www.brendangregg.com/blog/2019-12-02/bpf-a-new-type-of-software.html)”。BPF允许用户空间程序以安全和高效的方式在内核的某些位置设置钩子并发出事件。

安全和性能意味着什么？在这种情况下，“安全”意味着BPF程序不能陷入无限循环中，导致系统崩溃。BPF程序不太可能像内核模块那样使整个操作系统崩溃。BPF程序也有性能，如果不能足够快地使用事件，则会删除事件，而不是拖累整个系统的性能。

##  Teleport如何使用BPF

Teleport当前使用了三个BPF程序：[execsnoop](http://www.brendangregg.com/blog/2014-07-28/execsnoop-for-linux.html)用于捕捉程序执行，[opensnoop](http://www.brendangregg.com/blog/2014-07-25/opensnoop-for-linux.html)用来捕捉程序所打开的文件，[tcpconnect](http://www.brendangregg.com/blog/2015-10-31/tcpconnect-tcpaccept-bcc.html)用来捕捉程序建立的TCP链接。

为了更好地了解这三个BPF程序的功能，大家看看我们在运行“man ls”命令时，execsnoop捕捉到的内容：

    
    
    # ./execsnoop
    
        Tracing exec()s. Ctrl-C to end.
    
           PID   PPID ARGS
    
         20139  20135 mawk -W interactive -v o=1 -v opt_name=0 -v name= [...]
    
         20140  20138 cat -v trace_pipe
    
         20171  16743 man ls
    
         20178  20171 preconv -e UTF-8
    
         20181  20171 pager -s
    
         20180  20171 nroff -mandoc -rLL=173n -rLT=173n -Tutf8
    
         20179  20171 tbl
    
         20184  20183 locale charmap
    
         20185  20180 groff -mtty-char -Tutf8 -mandoc -rLL=173n -rLT=173n
    
         20186  20185 troff -mtty-char -mandoc -rLL=173n -rLT=173n -Tutf8
    
         20187  20185 grotty

现在你也许已经了解了BPF程序的功能了，简单的“man”命令，原来后面有这么多其他的程序在执行。

Teleport已将这三个程序的代码嵌入在了自己的库中，当我们启用了增强型会话记录功能之后，它便会执行这些程序。

![](https://image.3001.net/images/20200303/1583167787_5e5d392b6879b.png!small)

就其本身而言，这些程序都是用于调试和跟踪的优秀工具，因为它们可以告诉我们整个系统在执行哪些操作。事实上，这就是我们最开始选择这些工具的目的：我们使用它们来调试Teleport遇到的一些问题，而这些问题可能会导致它在某些场景中耗尽文件描述符。但是，我们使用Teleport的目的各有不同，我们有时需要将程序执行与SSH会话以及标识符关联起来。

为了将程序执行与特定的SSH会话关联起来，我们选择使用cgroup（cgroupv2）。当Teleport启动SSH会话时，它首先会重新启动并将自己放置在cgroup中。这将允许程序对当前进程以及Teleport将要启动的所有进程进行跟踪，并分配唯一标识ID。Teleport所运行的BPF程序还可以[发出执行它们的程序的cgroup
ID](https://github.com/torvalds/linux/commit/bf6fa2c893c5237b48569a13fa3c673041430b6c)，这允许我们将事件与特定的SSH会话和标识关联起来。

##  切入主题

了解了关于BPF的相关内容之后，你也可以将增强型会话记录功能引入你自己的程序之中，脚本代码已托管至GitHub【[传送门](https://gist.github.com/russjones/01fe0e5f0bfbabf73f***b93f4d119ed)】。

首先启动Ubuntu 19.04或RHEL/CentOS 8 VM并运行上面链接提供的脚本。该脚本只会安装内核头和bcc-tools，这些都是增强型会话记录运行的前提条件。除此之外，它还会安装jq，这样更有助于可视化查看结构化事件流。

###  安装命令如下：

    
    
    yum install -y kernel-headers bcc-tools

或

    
    
    apt install -y linux-headers-$(uname -r) bpfcc-tools

如需启用Teleport中的增强型会话记录功能，请将下列内容添加至配置文件中：

    
    
       ssh_service:
    
               enhanced_recording:
    
                  enabled: yes

当你以本文说明的方式在终端中执行“curl
[http://www.gravitational.com](http://www.gravitational.com/)”时，你将会看到下列输出内容：

    
    
    {
    
          "argv": [
    
            "[http://www.gravitational.com](http://www.gravitational.com/)"
    
          ],
    
          "cgroup_id": 4294967355,
    
          "code": "T4000I",
    
          "ei": 15,
    
          "event": "session.command",
    
          "login": "root",
    
          "namespace": "default",
    
          "path": "/bin/curl",
    
          "pid": 2315,
    
          "ppid": 2294,
    
          "program": "curl",
    
          "return_code": 0,
    
          "server_id": "e56dc762-0171-4d6e-aa56-24f2ae268c7f",
    
          "sid": "72aabcd8-38c8-11ea-af55-42010a800031",
    
          "time": "2020-01-17T01:27:05.07Z",
    
          "uid": "4b493296-7df2-4ec7-9282-a19c0d98e261",
    
          "user": "test-user"
    
        }
    
        {
    
          "cgroup_id": 4294967355,
    
          "code": "T4002I",
    
          "dst_addr": "104.24.97.116",
    
          "dst_port": 80,
    
          "ei": 0,
    
          "event": "session.network",
    
          "login": "root",
    
          "namespace": "default",
    
          "pid": 2315,
    
          "program": "curl",
    
          "server_id": "e56dc762-0171-4d6e-aa56-24f2ae268c7f",
    
          "sid": "72aabcd8-38c8-11ea-af55-42010a800031",
    
          "src_addr": "10.128.0.49",
    
          "time": "2020-01-17T01:27:05.145Z",
    
          "uid": "42831223-1da2-4b26-a783-08060fd8d7b1",
    
          "user": "test-user",
    
          "version": 4
    
        }

此时，我们可以看到用户将以两种方式运行curl程序。第一种就是程序执行本身，第二种方法就是程序的行为，curl将会发送一个网络请求。

当然了，你也可以尝试运行其他内容，比如说经过混淆处理的命令等等，你同样可以在日志中查看到执行结果。

##  执行演示

下面演示的是增强型会话记录如何将一个非结构化的SSH会话转换成了一个结构化事件流：

![](https://image.3001.net/images/20200303/1583167832_5e5d39584d480.gif!small)

***参考来源：[gravitational](https://gravitational.com/blog/enhanced-session-recording/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

