![](https://image.3001.net/images/20220118/1642486143_61e6597f52ac11bb8e20f.jpeg!small)  

## 写在前面的话

RPC 全称 Remote Procedure
Call，即远程过程调用。RPC是一种功能强大的底层机制，被广泛应用于横向移动、网络侦查、中继攻击和针对RPC服务的漏洞利用活动中。除此之外，像DCSync、Remote
DCOM、WMIC、SharpHound、PetitPotam、PsExec和ZeroLogon等活动都是通过RPC来实现的。现在，想必大家已经明白了RPC的重要性了。

## RPC-Firewall适用场景

### 安全研究

安装好RPC-Firewall并将其配置为“审核所有远程RPC调用”之后，一旦主机上自信了任何远程攻击工具之后，我们将能看到恶意程序远程调用了哪些RPC
UUID和OPNUM。

### 远程RPC攻击检测

当RPC-Firewall配置为“审核模式”时，它会将事件写入Windows事件日志。接下来，RPC-Firewall会将此日志转发给SIEM，并使用它为服务器创建远程RPC通信的基线。一旦工具检测到了异常的RPC调用，便会触发安全警报。

### 远程RPC攻击保护

RPC-Firewall可以配置为“仅阻止和审核潜在的恶意RPC调用”，此时工具将不会审核所有其他RPC调用以减少噪音并提高性能。

一旦检测到潜在的恶意RPC调用，它将被RPC-Firewall屏蔽，并记录到日志中，这种方式不仅可以提醒我们潜在的安全事件发生，同时也可以保护服务器的安全。

## RPC-Firewall的架构

 **RPC-Firewall主要由三个组件构成：**

> 1、RpcFwManager.exe：负责管理RPC-Firewall;
>
> 2、RpcFirewall.dll：注入负责执行RPC调用安全审计和过滤的DLL；
>
> 3、RpcMessages.dll：一个常用库，提供了共享函数以及工具向Windows事件查看器写入数据时所采用的逻辑；

## 工具下载和安装

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/zeronetworks/rpcfirewall.git

接下来，将RPC-Firewall的DLL文件拷贝至“%SystemRoot%\System32”，并为Windows事件查看器配置RPCFWP应用日志。

确保在工具的安装或卸载过程中，Windows事件查看器处于关闭状态：

    
    
    RpcFwManager.exe /install

### 工具卸载

    
    
    RpcFwManager.exe /uninstall

## 工具使用

### 进程保护

通过进程ID（PID）保护单个进程的安全：

    
    
    RpcFwManager.exe /pid <pid>

通过进程名称保护单个进程的安全：

    
    
    RpcFwManager.exe /process <process name>

如需保护所有进程的安全，直接将参数留空即可：

    
    
    RpcFwManager.exe /process
    
    RpcFwManager.exe /pid

### 撤销进程保护

如需禁用RPC-Firewall，可以选择直接卸载工具，或使用下列撤销保护参数：

    
    
    RpcFwManager.exe /unprotect

上述命令将撤销所有进程的保护功能。

### 查看日志

> “Windows事件查看器”->“应用程序和服务日志”->“RPCFWP”

接下来，添加关键词列，该列将包含审计日志详情。

## 项目地址

 **RPC-Firewall：** 【[
_GitHub传送门_](https://github.com/zeronetworks/rpcfirewall)】

## 参考资料

> [
> _https://zeronetworks.com/blog/stopping_lateral_movement_via_the_rpc_firewall/_](https://zeronetworks.com/blog/stopping_lateral_movement_via_the_rpc_firewall/)

