#
![1.png](https://image.3001.net/images/20180808/1533715424_5b6aa3e0e44ae.png!small)  

在Linux内核处理特定TCP数据包的方式中发现了一个名为 **SegmentSmack**
的漏洞。远程攻击者可以利用这一缺陷通过TCP请求触发耗时耗CPU的tcp_collapse_ofo_queue()
和tcp_prune_ofo_queue()系统调用，可能导致CPU跑满。维持拒绝服务条件需要连续的双向TCP会话到可达的开放端口，因此无法使用欺骗的IP地址执行攻击。

# 概述

在Linux内核处理特制TCP数据包的方式中发现了一个名为SegmentSmack的漏洞。远程攻击者可以利用这一缺陷触发耗时大量计算的tcp_collapse_ofo_queue（）和tcp_prune_ofo_queue（）调用使得CPU耗尽。该漏洞无需传入大量网络流量就可以导致系统CPU耗尽从而造成Dos攻击。在最坏的情况下，攻击者可使小于2
kpps攻击流量的对攻击主机产生影响主机和停顿。

# 漏洞详情

Juha-Matti Tilli发布的一封电子邮件消息报告了Linux内核中另一个与安全相关的问题。
CVE-2018-5390咨询是一个新发布的安全公告，其中提供了有关Linux内核漏洞的详细信息。该文档显示4.9+版本可能受特定服务条件的影响，这些条件可能导致DOS（拒绝服务）攻击。问题的确切性质与用户对行为的修改有关。可以强制内核为每个传入的数据包调用两个函数：

 **tcp_collapse_ofo_queue()**
，只要接收队列的内存配额已满，此例程就会释放无序队列，以便为到达的数据段腾出空间。这用于缓冲控制。

![2.png](https://image.3001.net/images/20180808/1533715434_5b6aa3eae2158.png!small)  

 **tcp_prune_ofo_queue()** ，这是网络数据包的修剪功能。它在队列操作期间使用。

![3.png](https://image.3001.net/images/20180808/1533715442_5b6aa3f2ac1dd.png!small)  

每个传入的数据包都可以修改为通过这两个函数。这可能导致行为模式导致拒绝服务的可能性。攻击者可以通过在正在进行的TCP网络会话中发送修改的数据包来诱导此类情况。分析表明，维护此状态需要通过目标计算机上的可访问开放端口进行连续的双向TCP会话。这意味着攻击只能通过真实IP地址执行，不能使用欺骗地址。

远程攻击者能够针对具有可用开放端口的系统触发拒绝服务条件。

因为维持拒绝服务条件需要连续的双向TCP会话到可达的开放端口，因此无法使用欺骗的IP地址执行攻击。

如下图使用4 TCP流进行攻击的结果就可以使得4 CPU内核的完全饱和以及导致网络数据包处理的延迟：

  
![4.png](https://image.3001.net/images/20180808/1533715450_5b6aa3fac4e75.png!small)  

# 受影响的产品

由于 **SegmentSmack** 攻击基于Linux内核网络堆栈中使用的算法，红帽官方文档指出对其产品具有中等新Linux内核版本产品都会受到影响：

· Red Hat Enterprise Linux 6

· Red Hat Enterprise Linux 7

· Red Hat Enterprise Linux 7 for Real Time

· Red Hat Enterprise Linux 7 for ARM64

· Red Hat Enterprise Linux 7 for Power

· Red Hat Enterprise Linux Atomic Host

Ubuntu官方指出受影响的版本有：

Ubuntu 12.04 ESM (Precise Pangolin)

Ubuntu 14.04 LTS (Trusty Tahr)

Ubuntu 16.04 LTS (Xenial Xerus)

Ubuntu 18.10 (Cosmic Cuttlefish)

其他厂商，请查询对应厂商的漏洞说明。

# 解决

目前还不知道除了固定内核之外没有有效的解决方法/缓解措施。 linux内核团队已经对该漏洞发布了代码补丁的commit

![5.png](https://image.3001.net/images/20180808/1533715463_5b6aa40766dc0.png!small)  

在撰写本文时，设备供应商尚未发布任何补丁。准备好后，将向最终用户和设备所有者发布相应的公告和更新。可以使用补丁系列，它通过将cpu周期限制到某个限制来实现对问题的修复，最终使得错误非关键。在未来，开发人员可能会继续进行进一步的修复，例如断开连接或黑洞验证的恶意流。

# 致谢

感谢来自阿尔托大学，通信与网络部和诺基亚贝尔实验室的Juha-Matti Tilli报告此漏洞。

## 参考文档  

<https://nvd.nist.gov/vuln/detail/CVE-2018-5390>

<https://people.canonical.com/>~ubuntu-security/cve/2018/CVE-2018-5390.html

<https://access.redhat.com/security/cve/cve-2018-5390>

