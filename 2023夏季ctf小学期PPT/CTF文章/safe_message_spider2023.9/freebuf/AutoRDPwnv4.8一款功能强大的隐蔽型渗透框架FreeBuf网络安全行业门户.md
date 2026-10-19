**今天给大家介绍的是一款名叫AutoRDPwn的隐蔽型渗透框架，实际上AutoRDPwn是一个PowerShell脚本，它可以实现对Windows设备的自动化攻击。这个[漏洞](https://www.kitploit.com/search/label/Vulnerability)允许远程攻击者在用户毫不知情的情况下查看用户的桌面，甚至还可以通过恶意请求来实现桌面的远程控制。**

![](https://image.3001.net/images/20190320/15530616369136.png!small)

## 环境要求

PowerShell4.0或更高版本。

### 新版本v 4.8增加的功能

> 兼容PowerShell 4.0
>
> 自动复制粘贴剪切板中的内容（密码、哈希等）
>
> 自动屏蔽Windows Defender（采用了四种不同的方法）
>
> 无需密码即可利用PSexec、WMI和Invoke-Command实现远程代码执行
>
> 新增攻击方式：DCOM无密码执行
>
> 新增攻击模块：远程访问/Metasploit Web传送
>
> 新增攻击模块：远程VNC服务器（针对遗留环境）
>
> 自动填写主机名、用户名和密码域
>
> 可使用-noadmin参数在没有管理员权限的情况下运行攻击模块

## 工具使用

这款应用程序可以直接在本地使用，也可以远程使用，或者是在两台设备间使用。在引入了额外功能模块之后，该工具甚至还可以导出哈希或密码，获取远程Shell，上传或下载文件，甚至是破解无线网络的密码以及恢复RDP连接历史记录等等。

### 一行命令即可执行

    
    
    powershell -ep bypass "cd $env:temp ; iwr https://darkbyte.net/autordpwn.php -outfileAutoRDPwn.ps1 ; .\AutoRDPwn.ps1"

![２.png](https://image.3001.net/images/20190319/1553007702_5c910456e0235.png!small)

我们可以在程序的主菜单中查看和选择需要使用或加载的攻击模块：

    
    
    [1] –PsExec
    
    [2] –Pass the Hash
    
    [3] –Windows Management Instrumentation
    
    [4] –Schedule Task / PSSession
    
    [5] –Windows Remote Assistance

工具的详细使用文档：【[传送门](https://darkbyte.net/autordpwn-la-guia-definitiva)】

## 工具截图

![３.png](https://image.3001.net/images/20190319/1553007719_5c910467d3d29.png!small)![４.png](https://image.3001.net/images/20190319/1553007720_5c91046805bc9.png!small)

### 项目地址

AutoRDPwn：【[GitHub传送门](https://github.com/JoelGMSec/AutoRDPwn)】

***参考来源：[arthastang](https://github.com/JoelGMSec/AutoRDPwn)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

