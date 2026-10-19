## 前言

前段时间读了读徐哥的《内网安全攻防》，并复现了部分知识点，写篇文章记录下学习内容。

## 环境搭建

首先搭建一个小型的域环境供我们测试使用:

域环境拓扑图：

![QQ图片20210523194615.png](https://image.3001.net/images/20210525/1621930321_60acb15120aef2aa1845c.png!small)

下面先介绍一下环境搭建的过程

![QQ图片20210522154759.png](https://image.3001.net/images/20210525/1621930327_60acb15774aa377975bf3.png!small)

配置域控

首先进入域控机，设置固定IP：192.168.1.1

子网掩码：255.255.255.0

![QQ图片20210522154915.png](https://image.3001.net/images/20210525/1621930334_60acb15ea25a42f410062.png!small)

设置计算机名：DomainControl  
![QQ图片20210522155501.png](https://image.3001.net/images/20210525/1621930339_60acb1634662ab7fda59e.png!small)

接下来安装作为域控制器（DNS服务器）所必需的服务

开始之前保持默认

![QQ图片20210522155838.png](https://image.3001.net/images/20210525/1621930350_60acb16e6f53c3fc71178.png!small)  
![QQ图片20210522155854.png](https://image.3001.net/images/20210525/1621930353_60acb171d27e654381ae7.png!small)

安装类型选择基于角色或基于功能的安装

![QQ图片20210522155923.png](https://image.3001.net/images/20210525/1621930370_60acb182d9862885e5878.png!small)

服务器选择：选择从服务器池中选择服务器并选择本机

![QQ图片20210522155958.png](https://image.3001.net/images/20210525/1621930378_60acb18a8e964fc41a0db.png!small)

选择服务器角色：选择DNS服务器和Active Directory域服务

![QQ图片20210522160021.png](https://image.3001.net/images/20210525/1621930389_60acb1957a0cc408e717a.png!small)

功能：保持默认

![QQ图片20210522160055.png](https://image.3001.net/images/20210525/1621930394_60acb19a3adf4c098db59.png!small)

Active Directory域服务：保持默认

![QQ图片20210522160107.png](https://image.3001.net/images/20210525/1621930398_60acb19e86cd75abc959a.png!small)

DNS服务器：保持默认

![QQ图片20210522160126.png](https://image.3001.net/images/20210525/1621930402_60acb1a26d3b5a686e142.png!small)

确认：选择如果需要，自动重新启动服务器

接下来点击安装

![QQ图片20210522160510.png](https://image.3001.net/images/20210525/1621930409_60acb1a90105c085dce59.png!small)

在仪表盘的黄色感叹号中选择将此服务器提升为域控制器

![QQ图片20210522160641.png](https://image.3001.net/images/20210525/1621930413_60acb1adaece6ef67b3d2.png!small)

部署配置：选择添加新林并在根域名中输入haixian.test

![QQ图片20210522161030.png](https://image.3001.net/images/20210525/1621930417_60acb1b1dc89163a24c00.png!small)

域控制器选项：输入还原模式密码

![QQ图片20210522161111.png](https://image.3001.net/images/20210525/1621930426_60acb1ba457c84bf24164.png!small)

DNS选项：可能会报警告，忽略即可

剩下的步骤全部保持默认即可，点击安装

接下来为成员机创建域控制器账户

WIN+R->输入dsa.msc->选择User目录并单击右键新建一个用户，如图

![QQ图片20210522165817.png](https://image.3001.net/images/20210525/1621930434_60acb1c269b4d71b9b64e.png!small)![QQ图片20210522165950.png](https://image.3001.net/images/20210525/1621930446_60acb1ce9272220a6b566.png!small)

接下来配置两台成员机加入域

配置成员机

![QQ图片20210522170128.png](https://image.3001.net/images/20210525/1621930453_60acb1d50b0c5a2d6d334.png!small)

配置win server2008 IP:192.168.1.2

子网掩码：255.255.255.0

![QQ图片20210522170243.png](https://image.3001.net/images/20210525/1621930457_60acb1d9260bfb53a8c31.png!small)

配置隶属域

![QQ图片20210522170637.png](https://image.3001.net/images/20210525/1621930462_60acb1dec478b65fac344.png!small)

注意这里输入的账户密码是域控的管理员账号密码

![QQ图片20210522170659.png](https://image.3001.net/images/20210525/1621930466_60acb1e2f413621c722f3.png!small)

若前面的配置的没有问题，那么此时的win server2008已经成功地加入了haixian.test这个域

接下来WIN7 的设置大同小异，不再赘述，注意IP设置为192.168.1.3即可

在域内任意主机的CMD中输入

    
    
    net view /domain:haixian
    

![image](https://image.3001.net/images/20210525/1621931029_60acb415da559c9e74194.png!small)出现如图所示回显即说明域环境搭建成功

（PS：若命令报6118错误可以尝试关闭防火墙）

## 信息收集

当我们成功的取得了域中某一主机的权限后，面对的是一个完全未知的域环境，要想进行下一步的渗透就必须要尽可能地获得有关于此域的信息，而这些信息就是整个内网渗透的基础；

在信息收集阶段，渗透测试人员通常要解决如下三个问题：

本机角色是什么？

例如web服务器，备份服务器等

本机所在内网的拓扑图？

对已获得权限主机所处内网的拓扑环境进行分析和判断，尽可能详细的绘制出网络拓扑图

本机所在区域？

例如办公区，核心区等

###### 本次信息收集测试假设已经取得了成员机win2008管理员权限

### 本机信息收集

手动命令收集信息

1.网络配置信息

    
    
    ipconfig /all
    

![QQ图片20210523203406.png](https://image.3001.net/images/20210525/1621930562_60acb24212b9edf9407c8.png!small)

2.查询操作系统及软件信息

查看操作系统以及版本

    
    
    systeminfo | findstr /B /C:"OS 名称" /C:"OS 版本"
    

![QQ图片20210523203919.png](https://image.3001.net/images/20210525/1621930568_60acb2480d8a3015b8faa.png!small)

查看系统体系结构

    
    
    echo %PROCESSOR_ARCHITECTURE%
    

![QQ图片20210523204053.png](https://image.3001.net/images/20210525/1621930572_60acb24c7d9d999fef750.png!small)

查看安装的软件及其版本、路径等

    
    
    wmic product get name,version
    或者
    powershell "Get-WmiObject -class Win32_Product |Select-Object -Property name,version"
    

![QQ图片20210523205110.png](https://image.3001.net/images/20210525/1621930580_60acb254391755dbaafb2.png!small)![QQ图片20210523205255.png](https://image.3001.net/images/20210525/1621930582_60acb256cc663d7c2005c.png!small)

3.查询本机信息

    
    
    wmic service list brief
    

![QQ图片20210523205459.png](https://image.3001.net/images/20210525/1621930589_60acb25dc63131623e94a.png!small)

4.查询正在运行的进程

    
    
    tasklist
    

![QQ图片20210523205607.png](https://image.3001.net/images/20210525/1621930595_60acb263bc8bd8ac687b2.png!small)

5.查看开机自启的程序信息

    
    
    wmic  startup get command,caption
    

![QQ图片20210523205841.png](https://image.3001.net/images/20210525/1621930600_60acb268ac4c062b8e390.png!small)

6.查看计划任务

    
    
    schtasks /query
    

如果这里运行命令报错的话输入

    
    
    chcp 437
    

调整下CMD编码为美国编码即可

![QQ图片20210524151245.png](https://image.3001.net/images/20210525/1621930606_60acb26eaceee7ac83fe8.png!small)

7.查看主机开机时间

    
    
    net statistics workstation
    

![QQ图片20210524151623.png](https://image.3001.net/images/20210525/1621930612_60acb2741119301a6a3e6.png!small)

8.查看用户列表

    
    
    net user
    

![QQ图片20210524151747.png](https://image.3001.net/images/20210525/1621930618_60acb27a057c9fa72ce68.png!small)

9.查看本地管理员用户组

    
    
    net localgroup Administrators
    

![QQ图片20210524152017.png](https://image.3001.net/images/20210525/1621930622_60acb27e277823a9841a8.png!small)

10.查看当前在线用户

    
    
    query user || qwinsta
    

![QQ图片20210524152146.png](https://image.3001.net/images/20210525/1621930626_60acb28237d6a0afac25e.png!small)

11.列出本地计算机与所连接的客户端的会话

    
    
    net session
    

![QQ图片20210524152344.png](https://image.3001.net/images/20210525/1621930630_60acb286877d0e3840a97.png!small)

12.查询端口列表

    
    
    netstat -ano
    

![QQ图片20210524152624.png](https://image.3001.net/images/20210525/1621930634_60acb28ac2d26713f1de4.png!small)

13.查看本机补丁

    
    
    systeminfo
    或者
    wmic qfe get Caption,Description,HotFixID
    

![QQ图片20210524153426.png](https://image.3001.net/images/20210525/1621930642_60acb2925981def839b55.png!small)![QQ图片20210524153515.png](https://image.3001.net/images/20210525/1621930644_60acb294a7558a16553c2.png!small)

14.查看共享列表

    
    
    net share 
    或者
    wmic share get name,path,status
    

![QQ图片20210524153743.png](https://image.3001.net/images/20210525/1621930649_60acb2996c137992f2e00.png!small)

15.查询路由表及所有可用接口的API缓存表

    
    
    route print
    apr -a
    

![QQ图片20210524154000.png](https://image.3001.net/images/20210525/1621930654_60acb29ed49696a067b53.png!small)  
![QQ图片20210524154024.png](https://image.3001.net/images/20210525/1621930661_60acb2a512a3cdaa080ca.png!small)

16.查看防火墙相关配置

    
    
    netsh firewall show config
    

![QQ图片20210524154151.png](https://image.3001.net/images/20210525/1621930672_60acb2b043adfe21d20e0.png!small)

17.查看系统代理

    
    
    reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    

![QQ图片20210524154333.png](https://image.3001.net/images/20210525/1621930680_60acb2b86de4e4aa3eb2b.png!small)

18.查看并开启远程桌面连接服务

查看：

    
    
    REG QUERY "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp" /V PortNumber
    

![QQ图片20210524154523.png](https://image.3001.net/images/20210525/1621930688_60acb2c05cd9fee2693b0.png!small)

开启：

    
    
    wmic /namespace:\\root\CIMV2\TerminalServices PATH Win32_TerminalServiceSetting WHERE (__CLASS !="") CALL SetAllowTSConnections 1
    

![QQ图片20210524154842.png](https://image.3001.net/images/20210525/1621930693_60acb2c576a01fb550410.png!small)

利用脚本自动化收集信息

1.在命令行中运行bat脚本，生成结果out.html

![QQ图片20210524194303.png](https://image.3001.net/images/20210525/1621930697_60acb2c9a566a424638df.png!small)

out.html:

![QQ图片20210524194441.png](https://image.3001.net/images/20210525/1621930702_60acb2ce23fb349b5a551.png!small)

查看当前会话权限

1.我是谁？

    
    
    whoami
    

![QQ图片20210524194624.png](https://image.3001.net/images/20210525/1621930710_60acb2d62b330be399b93.png!small)

可以看到当前会话权限为管理员administrator

2.获取域SID

    
    
    whoami /all
    

![QQ图片20210524194808.png](https://image.3001.net/images/20210525/1621930714_60acb2dab09bcba65818c.png!small)

3.查看指定用户的详细信息

    
    
    net user 用户名
    

![QQ图片20210524195227.png](https://image.3001.net/images/20210525/1621930719_60acb2dfd7a7c0eade589.png!small)

### 域有关信息收集

1.判断是否存在域环境

    
    
    net config workstation
    

![QQ图片20210524195536.png](https://image.3001.net/images/20210525/1621930729_60acb2e90956f89186506.png!small)

2.判断主域

    
    
    net time /domain
    

![QQ图片20210524204048.png](https://image.3001.net/images/20210525/1621930735_60acb2ef76a5816de7096.png!small)

注意这条命令只适用于当前登录的用户是域用户的情况下

可以看到主域就是haixian.test

3.查询域内用户列表

    
    
    net group /domain
    

![QQ图片20210525145759.png](https://image.3001.net/images/20210525/1621930742_60acb2f69082afb7d8885.png!small)

4.查询所有域成员(主机)

    
    
    net group "domain computers" /domain
    

![QQ图片20210525145922.png](https://image.3001.net/images/20210525/1621930747_60acb2fb944138fa4f852.png!small)

5.获取域内密码设置规则

    
    
    net accounts /domain
    

![QQ图片20210525150039.png](https://image.3001.net/images/20210525/1621930753_60acb30149e66e300f45c.png!small)

6.获取域内信任信息

    
    
    nltest /domain_trusts
    

![QQ图片20210525150218.png](https://image.3001.net/images/20210525/1621930761_60acb3097f162ef79cfff.png!small)

7.查找域控

    
    
    nltest /DCLIST:test
    或者
    net time /domain
    或者
    Nslookup -type=SRV _ldap._tcp
    或者
    net group "Domain Controllers" /domain
    或者
    netdom query pdc
    

![QQ图片20210525150414.png](https://image.3001.net/images/20210525/1621930767_60acb30fe9b5a0de527a0.png!small)

8.获取域内用户与管理员信息

    
    
    查询本地管理员组用户
    net localgroup administrators
    
    查询所有用户详细信息
    wmic useraccount get /all
    
    查询域管理员用户组
    net group "domain admins" /domain
    
    查询管理员用户组
    net group "Enterprise Admins" /domain
    

![QQ图片20210525150654.png](https://image.3001.net/images/20210525/1621930777_60acb3191ed9cece9ebe1.png!small)![QQ图片20210525150821.png](https://image.3001.net/images/20210525/1621930779_60acb31bca4d75eaae4dd.png!small)![QQ图片20210525150911.png](https://image.3001.net/images/20210525/1621930782_60acb31e2b6d3ba1897af.png!small)![QQ图片20210525150943.png](https://image.3001.net/images/20210525/1621930784_60acb320c01ce92825695.png!small)

8.定位域管

在取得了域中的普通权限后，想要进行横向移动，就一定要知道域用户所登陆的位置以及相对应的权限，能够定位域用户的工具有许多，这里介绍两种

(1).psloggedon.exe

下载地址：https://docs.microsoft.com/zh-cn/sysinternals/downloads/psloggedon

    
    
    psloggedon.exe \\主机名
    

这条命令可以查看目标主机上正在登录的用户并可以列出他们的身份

![QQ图片20210525151817.png](https://image.3001.net/images/20210525/1621930793_60acb32920e25b3bb5c6a.png!small)

(2).Netview

下载地址：https://github.com/mubix/netview/releases/tag/latest

Netview是一个枚举工具，可以枚举共享，用户等信息

    
    
    netview.exe -d
    

![QQ图片20210525153856.png](https://image.3001.net/images/20210525/1621930797_60acb32d44ae7ae24cda4.png!small)

### 探测域内其他主机信息

1.利用nbtscan扫描内网(工具需下载)

进入工具所在目录后

    
    
    nbtscan.exe 192.168.1.1/24
    

![QQ图片20210524204936.png](https://image.3001.net/images/20210525/1621930818_60acb342e9ecdf3e0246f.png!small)

2.利用ping命令探测内网

    
    
    for /L %I in (1,1,5) DO @ping -w 1 -n 1 192.168.1.%I | findstr "TTL"
    

![QQ图片20210524205425.png](https://image.3001.net/images/20210525/1621930826_60acb34a16012afc199b6.png!small)

这个方法探测比较慢，所以这里就设置了5个IP意思意思。。。

3.使用ARP探测内网(工具需要自己下载)

    
    
    arp-scan -t 192.168.1.1/24
    

![QQ图片20210525085255.png](https://image.3001.net/images/20210525/1621930832_60acb35089a2c189eddb6.png!small)

4.使用telnet扫描端口

    
    
    telnet 192.168.1.3 22
    

![QQ图片20210525090751.png](https://image.3001.net/images/20210525/1621930839_60acb357b9b102cef853a.png!small)

5.使用MSF进行端口扫描

    
    
    search scanner/portscan/tcp
    use 0 
    show options
    set port 1-1000
    set rhosts 192.168.1.1
    set threads 10
    run
    

![QQ图片20210525093620.png](https://image.3001.net/images/20210525/1621930846_60acb35e01fc6d944ff0f.png!small)

这里因为是实验演示所以就选了1-1000端口

以上就是初入内网时对本机，域内其他主机，本机用户，域内用户各方面信息的收集方法，若有遗漏还望过路大佬补充

## 写在后面

下一篇文章讲隐藏通信隧道技术，敬请期待~

 **参考资料：《内网安全攻防：渗透测试指南》 徐焱、贾晓璐**

