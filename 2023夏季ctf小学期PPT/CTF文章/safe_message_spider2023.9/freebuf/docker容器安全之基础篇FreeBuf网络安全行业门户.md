> 虚拟化是云计算中关键技术之一，随着PaaS服务模式的发展，以docker为主的容器技术受到更多关注

相比于传统的虚拟化技术，docker容器有着更高效的系统资源利用率、更快速的启动时间，但利用Linux内核特性实现隔离的容器技术也面临着更为严峻的安全问题。

传统的虚拟化技术中，虚拟机通过管理程序实现对硬件的虚拟化，并且每个虚拟机都有自己的操作系统，在启动速度和资源利用率以及性能上都有比较大的开销。Docker取消了虚拟机中的Hypervisor层和Guest
OS层，使用容器引擎进行调度，因此更为便捷，启动速度更快，资源利用率更高。但相比较于传统虚拟化技术借助封闭的Guest
OS隔离不同用户的进程，容器这种仅依赖于底层操作系统内核的隔离机制还面临一系列安全风险，二者架构对比如下图所示。  
![虚拟机与容器技术架构对比](https://image.3001.net/images/20210430/1619751435_608b720b8a56c60f23cac.png!small)

近些年，对于容器安全的研究已经成为安全领域的一个研究热点，基于Docker容器平台的CVE漏洞层出不穷，越来越多的安全从业人员加入了对Docker容器安全的分析与研究。本文先对docker容器安全机制进行基础介绍，为之后docker容器攻击利用及防御分析进行铺垫。

## 1 docker架构及组件

Docker采用的是Client/Server架构，客户端向服务器发送请求，服务器负责构建、运行和分发容器。客户端和服务器可以运行同一个Host上，客户端也可以通过socket或REST
API与远程的服务器进行通信。  
Docker组件主要包含Docker引擎、Docker容器和Docker仓库三个部分。Docker引擎是Docker运行时的服务提供者，为整个Docker提供支持。其中包含了Docker使用的各种安全技术，比如Namespace、ControlGroup等。Docker容器是用户需要运行提供生产力的服务包，这里面运行着许多自定义的应用程序。Docker仓库是用户集中存放管理镜像的地方，当用户需要时Docker将会从这里下载指定容器或镜像。具体架构图如下。  
![Docker系统架构及其主要组件](https://image.3001.net/images/20210430/1619751484_608b723c3edd29b09187c.png!small)

## 2 docker安全机制

每个虚拟机都有自己的GuestOS，从而保证了虚拟机之间的隔离，进而达到同一宿主机上不同虚拟机间互不干扰的目的。Docker容器则是借助系统内核来进行安全性隔离，即通过namespace进行隔离、cgroup进行资源限制、capability进行权限限制。但同一台宿主机的系统内核却是共享的，多个容器的系统调用均是通过宿主机的内核处理，这为容器留下了一定的安全隐患。

### 2.1 NameSpace

Docker容器的隔离是基于Linux的namespace实现的。当启动一个容器时，Docker为容器新建了一系列的namespace来实现资源隔离。namespace提供了最基础也是最直接的隔离，在容器中运行的进程不会被运行在主机上的进程和其它容器发现和作用。Docker环境中目前可支持六种不同的Namespace，它们分别对系统资源的不同方面进行了隔离，具体资源隔离情况如下。  
![Namespace](https://image.3001.net/images/20210430/1619751501_608b724d2ecc520605285.jpg!small)

### 2.2 Cgroup

Cgroup（Control
Group）是linux内核提供的一种机制，负责实现资源的审计和限制。Cgroups可以通过使用其各子系统对组内进程资源供给进行灵活组合限制，解决了多租户容器平台中差别化的系统资源分配问题，减少了资源耗尽型DoS攻击的攻击面。

### 2.3 内核能力机制

能力机制（Capability）是Linux内核一个强大的特性，可以提供细粒度的权限访问控制。默认情况下，Docker采用白名单机制，禁用必需功能之外的其它权限。用户也可根据实际需要在运行时添加或减少能力特权。docker默认开启的capability权限列表如下。

名称| 功能  
---|---  
AUDIT_WRITE| 将记录写入内核审计日志  
CHOWN| 对文件uid和gid进行任意更改  
DAC_OVERRIDE| 绕过文件的自主访问控制  
FOWNER| 绕过对操作的权限检查，设置任意文件的访问控制列表  
FSETID| 当文件被修改时，不清除set-user-ID和set-group-ID权限位  
KILL| 允许对不属于自己的进程发送信号  
MKNOD| 允许使用mknod()系统调用  
NET_BIND_SERVICE| 将套接字绑定到小于1024的端口  
NET_RAW| 允许使用原始套接字  
SETFCAP| 为文件设置任意的capability权限  
SETGID| 允许改变进程的组ID  
SETPCAP| 允许向其他进程转移capability权限以及删除其他进程的capability权限  
SETUID| 允许改变进程的用户ID  
SYS_CHROOT| 允许使用chroot()以及使用setns更改挂载的namespace  
  
### 2.4 其他安全特性

Docker当前默认只启用了能力机制，用户还可以利用一些现有的安全机制来增强使用Docker的安全性，例如TOMOYO、AppArmor、SELinux、GRSEC等。跟其它添加到Docker容器的第三方工具一样（比如网络拓扑和文件系统共享），有很多类似的机制，在不改变Docker内核情况下就可以加固现有的容器。

## 3 容器漏洞报告总结

另外，笔者总结了[2017-2020
CVE中关于容器的漏洞报告](https://github.com/XiaoXiaoGuaiXiaShi/Container-security-papers.git)，后续攻击分析中也会以其中某个CVE为例进行利用介绍。

