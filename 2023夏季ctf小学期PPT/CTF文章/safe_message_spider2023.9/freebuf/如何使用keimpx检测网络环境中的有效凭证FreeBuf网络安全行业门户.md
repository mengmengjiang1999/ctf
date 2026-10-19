![](https://image.3001.net/images/20210924/1632492692_614ddc94c82eb73a819d6.jpg!small)

## 关于keimpx

keimpx是一款功能强大的开源工具，该工具可以帮助广大研究人员快速检测网络环境中跟SMB相关的有效凭证。这些凭证可以是下列内容之一：

> 用户/明文密码组合；
>
> 用户/NTLM哈希组合；
>
> 用户/NTLM登录会话令牌组合；

如果工具检测到了目标网络系统内的任意有效凭证，研究人员就可以选择需要连接的主机以及需要使用的有效凭证。接下来，我们将会拿到一个交互式SMB
Shell，此时我们可以做到下列内容：

> 生成一个交互式命令行窗口；
>
> 浏览远程SMB共享：枚举、上传、下载文件、创建、删除文件等；
>
> 部署和取消部署自己的服务，比如说，在TCP端口上侦听传入连接的后门等；
>
> 列出用户详细信息、域和密码策略；

## 依赖组件

当前版本的keimpx使用[ _Python 3.8_](https://www.python.org/)开发，并且基于[
_Impacket_](https://github.com/SecureAuthCorp/impacket)库实现了大部分功能。除此之外，keimpx还使用了[
_PyCryptodome_](https://github.com/Legrandin/pycryptodome)来实现加密功能。

## 工具安装

如需安装keimpx，首先需要在本地设备上安装并配置好Python 3.8环境。在Windows上，你可以直接点击【[
_这里_](https://www.python.org/downloads/release/python-382/)】下载安装包。对于Linux用户，大多数发行版都已经预置了Python
3。

在Linux系统上，你需要先安装好pip，并使用包管理器安装好openssl-dev。

接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/nccgroup/keimpx.git

安装好Python 3.8之后，你就可以使用下列命令并通过pip来安装工具所需的依赖组件：

    
    
    pip install -r requirements.txt

我们可以使用下列命令在Linux系统上运行keimpx：

    
    
    ./keimpx.py [options]

或者，如果上述命令无法使用的话，可以尝试下列命令：

    
    
    python keimpx.py [options]
    
    python3 keimpx.py [options]

在Windows系统上，你可能需要指定Python 3.8源码的完整路径，样例命令如下：

    
    
    C:\Python37\bin\python.exe keimpx.py [options]

## 工具使用

假设你现在需要在一个大型网络中执行渗透测试任务，并且你拥有一台Windows工作站，然后将你的权限提升为“Administrator”或“LOCAL
SYSTEM”，并导出密码哈希。

你还需要使用“net”命令枚举Windows域中的所有设备，并执行ARP扫描和网络流量嗅探。

现在，如果你想检测导出哈希的有效性，就可以直接启动keimpx了。

## 工具帮助信息

    
    
    keimpx 0.5.1-rc
    
    by Bernardo Damele A. G. <bernardo.damele@gmail.com>
    
        
    
    Usage: keimpx.py [options]
    
     
    
    Options:
    
      --version        显示程序版本信息
    
      -h, --help        显示帮助信息
    
      -v VERBOSE      Verbose等级：0-2 (默认: 0)
    
      -t TARGET       目标地址
    
      -l LIST          目标地址列表文件
    
      -U USER         用户
    
      -P PASSWORD     密码 
    
      --nt=NTHASH     NT哈希
    
      --lm=LMHASH     LM哈希
    
      -c CREDSFILE      凭证列表文件
    
      -D DOMAIN       域
    
      -d DOMAINSFILE   域列表文件
    
      -p PORT          SMB 端口: 139或445 (默认: 445)
    
      -n NAME         本地主机名
    
      -T THREADS       最大同时连接数 (默认: 10)
    
      -b               Batch模式
    
      -x EXECUTELIST    针对所有主机执行的命令列表

## 许可证协议

本项目的开发与发布遵循Apache-2.0开源许可证协议。

## 项目地址

 **Keimpx：** 【[ _GitHub传送门_](https://github.com/nccgroup/keimpx)】

## 参考资料

> [ _http://bernardodamele.blogspot.com/2009/11/abuse-citrix-and-own-> domain.html_](http://bernardodamele.blogspot.com/2009/11/abuse-citrix-and-> own-domain.html)
>
> [ _http://technet.microsoft.com/en-> us/sysinternals/bb664922.aspx_](http://technet.microsoft.com/en-> us/sysinternals/bb664922.aspx)
>
> [
> _http://bernardodamele.blogspot.com/search/label/dump﻿_](http://bernardodamele.blogspot.com/search/label/dump)

