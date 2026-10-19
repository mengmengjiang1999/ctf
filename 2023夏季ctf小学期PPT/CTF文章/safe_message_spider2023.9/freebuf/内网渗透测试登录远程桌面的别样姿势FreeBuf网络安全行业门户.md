![image-20210613011023770](https://image.3001.net/images/20210705/1625453858_60e27522d6eb2ace5872e.png!small)

系列文章：

> [《内网渗透测试：初探远程桌面的安全问题》](../articles/network/276242.html)
>
> [《内网渗透测试：基于文件传输的 RDP
> 反向攻击》](https://www.freebuf.com/articles/network/280818.html)
>
> [《内网渗透测试：获取远程桌面连接记录与 RDP
> 凭据》](https://www.freebuf.com/articles/network/280819.html)

## 前言

远程桌面在内网渗透中可以说是再常见不过了，在渗透测试中，拿下一台主机后有时候会选择开 3389
进远程桌面查看一下对方主机内有无一些有价值的东西可以利用。但如果我们仅拿到了目标服务器的特权却抓不出用户密码，或者只能抓取密码哈希，在这两种情况下我们还能登录远程桌面吗？当然可以，本篇文章就对这两种情况提出了响应的应对方案。

## 利用 RDP 劫持未授权登录远程桌面

### RDP 劫持的原理

> 系统管理员和用户通常可以通过 RDP 远程桌面登录指定服务器 3389 远程桌面，而攻击者可以通过可以特权提升至 SYSTEM
> 权限的用户，可以在不知道其他用户登录凭据的情况下，用来劫持其他用户的 RDP 会话，该漏洞在 2017 年由以色列安全研究员 Alexander
> Korznikov 在个人博客中披露。利用条件只需要获取机器 SYSTEM 权限执行 tscon 命令。

对于开启远程桌面服务的 Windows 系统，当有多个用户登录该系统时，会产生多个会话，如下图：

![image-20210523173030619](https://image.3001.net/images/20210705/1625453865_60e275290d62ae795766c.png!small)

其中，管理员用户 Administrator 为本地登录，用户 bunny 为通过远程桌面服务（RDP）连接 3389 端口的远程桌面登录。接下来，如果用户
Administrator 想要切换至用户 bunny 的远程桌面，可通过右键—> 连接（Connect）进行连接，接着输入密码即可切换到 bunny
用户：

![image-20210523173120796](https://image.3001.net/images/20210705/1625453865_60e275296f38bc1bbac73.png!small)

![image-20210523173145771](https://image.3001.net/images/20210705/1625453865_60e27529ca7aa2f65ad39.png!small)

点击确定后，如下图所示，成功切换到了 bunny 用户的远程桌面：

![image-20210523172737212](https://image.3001.net/images/20210705/1625453866_60e2752a2e161396f25f0.png!small)

而且，在 Windows 中有一个 tscon 命令，是命令行下使用的工具，也可以实现与上述相同的功能。

首先执行如下命令获取用户对应的会话 ID：

    
    
    query user

![image-20210523173320885](https://image.3001.net/images/20210705/1625453866_60e2752a7188355f2202a.png!small)

可以看到用户 bunny 对应的会话 ID 为 2，然后通过执行 tscon 命令即可成功切换至用户 bunny 的远程桌面，命令如下：

    
    
    tscon 2 /PASSWORD:Bunny2021

/PASSWORD：bunny 用户的密码

![image-20210523172737212](https://image.3001.net/images/20210705/1625453866_60e2752ab2e64a6cc1c04.png!small)

可见，tscon
命令提供了一个切换用户会话的功能，并且，在正常情况下，切换会话时需要提供目标用户的登录密码。但这并不能完全确保会话安全，攻击者通过特殊的利用方法完全能够绕过验证，不输入密码即可切换到目标会话，从而实现目标用户的未授权登录。

而这里所讲的特殊的利用方法便是在 SYSTEM 权限下直接执行 tscon 会话切换命令：

    
    
    tscon ID

此时攻击者可以在不提供其他用户登录凭据的情况下自由切换会话桌面，实现劫持其他用户的 RDP 会话。

RDP 会话劫持在特定情况下可以大显身手，比如对于较新的 Windows 系统，默认情况下是无法通过 Mimikatz
导出用户明文口令的，此时我们通过常规方法无法切换至另一用户的桌面，那么我们便可以借助上文提到的方法，先提权至 SYSTEM 权限，再劫持目标用户的 RDP
并切换过去。

特别注意的是，即使远程连接的用户关闭了远程连接窗口，也不会劫持该回话，只是在后台显示 “已断开连接”（Disconnected）：

![image-20210523181120642](https://image.3001.net/images/20210705/1625453867_60e2752b0b6bd41e0195c.png!small)

此时，仍能在 SYSTEM 权限下通过`tscon`实现未授权连接。

### 高权限用户劫持低权限用户的 RDP

高权限用户劫持低权限用户的 RDP 会话利用起来比较简单，由于具有管理员权限，可以直接通过创建服务等方式获取 SYSTEM 权限。

创建劫持用户会话的服务：

    
    
    sc create rdp binpath= "cmd.exe /k tscon 2 /dest:console"  
    sc start rdp

![image-20210523174510831](https://image.3001.net/images/20210705/1625453867_60e2752b56d81fc24fcee.png!small)

执行`sc start rdp`后，我们创建的劫持会话的服务将会启动，由于 Windows 是以 SYSTEM 权限运行服务的，所以我们`tscon
2`命令也会以 SYSTEM 权限运行，此时便可以在不提供目标用户密码的情况下成功劫持目标用户的会话：

![image-20210523174727394](https://image.3001.net/images/20210705/1625453867_60e2752ba038502a9365b.png!small)

其实也可以使用 Psexec 来获得一个 SYSTEM 权限的 cmd（Psexec 获得的 shell 是 SYSTEM 权限的），然后再这个
SYSTEM 权限的 cmd 中直接执行`tscon 2`劫持命令：

    
    
    psexec -s -i cmd    # 获得一个 SYSTEM 权限的 cmd  
    ​  
    quser user    # 在新获得的 SYSTEM 权限的 cmd 中执行劫持命令  
    tscon 2 /dest:console

### 低权限用户劫持高权限用户的 RDP

低权限用户劫持高权限用户的 RDP 会话利用起来没有前者那么简单，因为权限太低，所以无法执行创建服务，执行 Psexec
等高权限的命令。所以如果低权限用户想要劫持高权限用户的 RDP 的话需要想办法提权，即将自己的权限提升至 SYSTEM。

实验环境如下：

