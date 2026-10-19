## 简介

**PivotSuite是一个可移植，独立于平台且功能强大的网络pivoting工具包，可帮助红队/渗透测试人员使用受损的系统在网络内部横向移动。它是一个独立的实用程序，因此可以作为服务器或客户端使用。**

## 作为服务器

如果受损的主机可以从我们的攻击机直接访问（正向连接），那么我们则可以在受损的主机上运行pivotsuite作为服务器，并从我们的攻击机访问只能从受损的主机访问的不同的子网主机。

## 作为客户端

如果受损的主机位于防火墙/NAT后，并且无法直接通过我们的攻击机访问，那么我们可以在攻击机上运行pivotsuite作为服务器，并在受损的主机上作为客户端来建立一个反向隧道（反向连接）。通过它，我们可以从我们的攻击机到达只能从受损的主机访问的不同的子网主机。

## 主要特性

> 支持正向和反向TCP隧道
>
> 支持转发和反向socks5代理服务器
>
> 支持UDP over TCP和TCP over TCP协议
>
> 支持企业代理身份验证（NTLM）
>
> 内置网络枚举功能，例如主机发现，端口扫描，OS命令执行
>
> PivotSuite允许同时访问不同的受损主机及其网络（充当C&C服务器）
>
> 在PivotSuite的帮助下可以执行1个2个或多个Pivoting。
>
> PivotSuite还可以作为SSH动态端口转发，但方向相反。

 **在以下方面优于其他工具：**

> 在受损主机上不需要admin/root用户访问权限
>
> 在仅允许反向连接或受损主机位于防火墙/NAT后时，PivotSuite也可以工作。
>
> 除了python标准库之外没有任何依赖。
>
> 无需安装
>
> UDP端口可通过TCP访问

## 安装

你可以通过克隆Git存储库或PyPI包下载最新版本的pivotsuite。

    
    
    git clone https://github.com/RedTeamOperations/PivotSuite.git
         
               OR
               
     pip install PivotSuite

在任何Python version 2.7.x和3.6.x的平台上PivotSuite都是开箱即用的。

PivotSuite的独立可执行文件可以从Github Release部分下载

    
    
    https://github.com/RedTeamOperations/PivotSuite/releases

没有任何额外的安装要求，也不需要python解释器

 **只需满足：**

> 仅需要Python标准库
>
> 兼容Python 2.7.x和Python 3.6.x
>
> 已在Windows和Linux上进行测试。

## 使用

    
    
    $ pivotsuite.py [options] SERVER-IP SERVER-PORT

选项：

    
    
    --version             显示版本号并退出
    
    -h, --help            显示帮助信息并退出
    
    -S, --server          运行PivotSuite作为服务器
    
    -C, --client          运行PivotSuite作为客户端
    
     - -server-ip=SERVER_IP
    
                        服务器侦听/连接IP地址，默认为0.0.0.0
                        
     --server-port=SERVER_PORT
    
                        服务器侦听/连接端口，默认为7777

PivotSuite Server选项：

    
    
    -F, --forward-connection
    
                        转发网络流量
                        
    --server-option=SP/PF
    
                        将服务器作为Socks_Proxy(SP)/Port_Forward(PF)，
                        默认为SP
                        
    --network-protocol=T/U
    
                        选择端口转发协议TCP(T)/ UDP(U)，
                        默认为T
                        
    --forward-ip=Remote-Host-IP
    
                        用于端口转发的远程主机IP
                        
    --forward-port=Remote-Host-Port
    
                        用于端口转发的远程主机端口
                        
    -W, --reverse-connection
    
                        反向网络流量

PivotSuite Client选项：

    
    
    -O SP/PF/NE, --option=SP/PF/NE
                        使用客户端作为Socks_Proxy(SP)/ Port_Forwarding(PF)/
                        Network_Enumeration(NE)，默认为SP
                        
    -L, --local-forward
    
                        使用本地端口转发
                        
    -R, --remote-forward
    
                        使用远程端口转发
                        
    -P T/U, --protocol=T/U
    
                        选择用于端口转发的协议TCP(T)/ UDP(U)，
                        默认为T
                        
    --local-ip=LOCAL_IP
    
                        用于端口转发的本地IP
                        
    --local-port=LOCAL_PORT
    
                        用于端口转发的本地端口
                        
    --remote-ip=REMOTE_IP
    
                        用于端口转发的远程IP
                        
    --remote-port=REMOTE_PORT
    
                        用于端口转发的远程端口

NTLM代理验证选项：

    
    
    --ntlm-proxy-ip=NTLM_PROXY_IP
    
                        NTLM代理的IP地址
                        
    --ntlm-proxy-port=NTLM_PROXY_PORT
    
                        NTLM代理的端口
                        
    --username=USERNAME
    
                        使用NTLM代理进行身份验证的用户名
                        
    --domain=DOMAIN     要用NTLM代理进行身份验证的域
    
    --password=PASSWORD
    
                        使用NTLM代理进行身份验证的密码
                        
    --hashes=HASHES     使用哈希而不是密码进行身份验证
                        格式 - LMHASH:NTHASH

## 文档

 **案例1：（TCP隧道转发）**

如果可以通过我们的攻击机直接访问受损主机。

    
    
    然后根据我们的要求在受损机器上运行PivotSuite作为服务器：
    
        a. 受损主机上的动态端口转发（socks5代理服务器）：
    
             $  python pivotsuite.py -S -F --server-option SP --server-ip IP --server-port PORT
    
    
        b. 受损主机上的单端口转发（TCP/UDP 中继）：
    
            $ python pivotsuite.py -S -F --server-option PF --network-protocol T/U --remote-ip IP --remote-port PORT 
              --server-ip IP (local-ip) --server-port PORT (local-port)

 **案例2：（反向TCP隧道）**

如果受损主机位于防火墙/NAT后面，并且无法从我们的攻击机直接访问。

    
    
    然后在攻击机上以服务器的形式运行PivotSuite，在受损主机上以客户机的形式运行PivotSuite。
    
      i. 在攻击机上运行PivotSuite作为服务器：
    
          $ python pivotsute.py -S -W 
    
    
      ii. 根据我们的要求在受损主机上运行PivotSuite作为客户端：
    
          a. 攻击机上的动态端口转发（socks5代理服务器）：
    
              $ python pivotsuite.py -C -O SP --server-ip IP --server-port PORT
    
          b. 攻击机上的本地/远程端口转发：
    
               $ python pivotsuite.py -C -O PF  - L / -R (local or remote port forwarding) -P T/U  --local-ip IP 
                  --local-port PORT --remote-ip IP --remote-port PORT  --server-ip IP --server-port PORT
    
          c. 受损主机网络枚举：
    
                $ python pivotsuite.py -C -O NE --server-ip IP --server-port PORT

如果在受损主机上进行反向连接，则需要企业代理身份验证（NTLM）：

    
    
    $ python pivotsuite.py -C -O SP --ntlm-proxy-ip IP --ntlm-proxy-port PORT --username USERNAME --password PASSWORD 
       --server-ip IP --server-port PORT

***参考来源：[GitHub](https://github.com/RedTeamOperations/PivotSuite)，FB小编secist编译，转载请注明来自FreeBuf.COM**

