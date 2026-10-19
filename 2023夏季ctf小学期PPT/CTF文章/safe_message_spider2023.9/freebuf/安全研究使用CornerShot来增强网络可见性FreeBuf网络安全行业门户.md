![](https://image.3001.net/images/20210310/1615362907_60487b5b19ee6aae3d89e.jpg!small)

## CornerShot是什么？

如果在战场上，CornerShot将是一种强有力的武器，可以帮助士兵穿过各种“障碍”，而无需担心暴露自己的行踪。对于网络安全来说，CornerShot可以帮助广大研究人员查看远程主机的网络访问，而不用获取到针对目标主机的任何特殊权限。

通过使用CornerShot，我们可以通过一个源（具备网络访问权）来判断特定端口p和目标之间是否存在网络访问关联。

比如说，假设一个红队正试图从一个“已入侵”的源主机A到一个目标主机X，而主机A对其没有访问权限。如果此时尝试通过主机B来访问，则会发现主机B和X之间没有网络访问。通过使用CornerShot，团队可以发现主机C实际上可以访问目标X，因此向目标X的网络传播应该首先通过主机C。

![](https://image.3001.net/images/20210310/1615362920_60487b680014d70efb759.png!small)

跟[ _Nmap_](https://nmap.org/)类似，CornerShot可以区分端口的以下状态：打开、关闭、过滤和未知（如果无法确定）。

## 工具演示样例

下面的工具演示样例演示了针对两台运营商主机172.0.1.12和172.0.1.13运行CornerShot，以确定网络是否可以访问192.168.200.1：

![](https://image.3001.net/images/20210310/1615362930_60487b72902aa68a3ba49.gif!small)

## 开始使用

CornerShot能够以软件包或单独模块的形式来使用。唯一的要求就是主机需要配置好Python 3环境和impacket包。

### 工具安装

    
    
    pip install cornershot

### 单独使用

工具的基础使用方式需要从有效域用户获取凭证，以及FQDN域和目标IP等等：

    
    
    python -m cornershot <user> <password> <domain> <carrier> <target>

如需扫描大量目标、子网或IP范围，则需要用逗号分隔列表：

    
    
    python -m cornershot <user> <password> <domain> 192.168.1.10-192.168.1.20 192.168.5.0/24,192.168.6.0/24

默认情况下，CornerShot将尝试扫描下列端口：135, 445, 3389, 5985, 5986。用户可以提供端口列表或端口范围，需用逗号隔开：

    
    
    python -m cornershot -tp 22,8080,45000-45005 <user> <password> <domain> <carrier> <target>

### 以软件包使用

在代码中，需要用到有效域用户的用户名、密码和域名实例化CornerShot对象。首先需要通过add_shots方法来添加目标及端口信息，然后调用open_fire方法，它将根据所需的端口执行相关的RPC调用。

    
    
    from cornershot import CornerShot
    
    cs = CornerShot("username", "password", "fqdn")
    
    cs.add_shots(carriers=["192.168.1.1"],targets=["192.168.1.2","192.168.1.3"])
    
    results = cs.open_fire()

open_fire方法的执行结果输出格式如下：

    
    
    {'carrier_1':
    
    {'target_1':
    
    {135: 'unknown', 445: 'filtered', 3389: 'filtered', 5986: 'filtered', 5985: 'filtered'},
    
    'target_2':
    
    {135: 'unknown', 445: 'open', 5985: 'unknown', 5986: 'filtered', 3389: 'open'}
    
    },
    
    'carrier_2':
    
    {'target_1':
    
    {3389: 'filtered', 135: 'filtered', 5985: 'filtered', 445: 'filtered', 5986: 'unknown'},
    
    'target_2':
    
    {5985: 'filtered', 5986: 'filtered', 445: 'filtered', 135: 'filtered', 3389: 'open'}
    
    }
    
    }

## 工具使用场景

### 完整的网络可见性

识别网络中的某个主机B是否可以访问主机C，这一看似简单的任务可能需要大量部署网络传感器、设备代理或收集大量防火墙规则、路由器配置和主机策略。

CornerShot可以通过使用一个（或很少几个）代理，即可查询网络中其他主机并确定它们对远程主机的访问，从而简化此过程。

### 验证BloodHound路径

安全团队经常会利用BloodHound来查找并减少在目标网络中的提权路径，但通常会发现他们需要跟BloodHound所找到的数百万条逻辑路径进行“抗争”。

[ _ShotHound_](https://github.com/zeronetworks/BloodHound-Tools/tree/main/ShotHound)是一款可以跟CornerShot配合使用的工具，可以更好地发现网络访问支持的实用路径。

## 操作系统支持

![](https://image.3001.net/images/20210310/1615363000_60487bb88f051d301355d.png!small)

## 许可证协议

本项目的开发与发布遵循[ _Apache
v2.0开源许可证协议_](https://github.com/zeronetworks/cornershot/blob/expansion_doc/LICENSE.txt)。

## 项目地址

CornerShot：【[ _GitHub传送门_](https://github.com/zeronetworks/cornershot)】

## 参考资料

> [ _https://zeronetworks.com/blog/adversary-resilience-via-least-privilege-> networking-part-1/_](https://zeronetworks.com/blog/adversary-resilience-via-> least-privilege-networking-part-1/)
>
> [ _https://nmap.org/_](https://nmap.org/)
>
> [ _https://github.com/zeronetworks/BloodHound-> Tools/tree/main/ShotHound_](https://github.com/zeronetworks/BloodHound-> Tools/tree/main/ShotHound)

