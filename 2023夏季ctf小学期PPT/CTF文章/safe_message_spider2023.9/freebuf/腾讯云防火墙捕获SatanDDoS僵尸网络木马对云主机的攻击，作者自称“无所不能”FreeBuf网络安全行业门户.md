# 摘要

本次攻击具备以下特点：

1.攻击者通过Shiro1.2.4反序列化漏洞攻击云主机；

2.Satan DDoS僵尸网络木马具备DDoS、挖矿、后门能力；

3.作者自称支持可攻击多平台，木马支持多架构，可利用多个漏洞攻击传播，包括通过FTP、IPC、SMB、WMI、MSSQL、EternalBlue、Eternalromance、CVE-2017-8464、Thinkphp、HFS、phpstudy、Laravel、durpal、Shareddisk、sharedirectory............等等多种漏洞利用方式攻击传播。相关能力已被国外安全厂商告证实；

4.挖矿时会清除竞品木马；

5.具备tcp，udp，http，icmp，syn等多种流量攻击模式。

# 一、概述

腾讯安全威胁情报中心发现，有攻击者通过Shiro1.2.4反序列化漏洞对云主机发起攻击活动，意图植入名为Satan
DDoS的僵尸网络木马程序。该僵尸网络木马此前主要攻击Windows系统，作者在恶意代码中自称“可攻击多平台，木马支持多架构，可利用多个漏洞攻击传播”。已安装腾讯云防火墙的云主机成功拦截此轮攻击，而未部署云防火墙系统的则可能失陷。

分析其Linux版本的ELF格式x86-64指令集木马样本可知，Satan
DDoS僵尸网络木马除进行DDoS攻击以外，还会同时下载执行XMR（门罗币）矿工。Satan DDoS僵尸网络木马同时具备文件执行、命令执行等系统后门能力。

![](https://image.3001.net/images/20210608/1623155898_60bf64ba9b93ad6da3a67.png!small)

Satan
DDoS僵尸网络木马去年5月被国外安全厂商关注，为与Satan勒索病毒区分，国外厂商将其命名为“Lucifer”木马，当时主要利用多个高危漏洞攻击Windows系统。从目前的发现看，该团伙已转向对云主机的进攻，其牟利方式为：控制目标主机组建僵尸网络，进行门罗币挖矿和DDoS攻击。

## 清理&加固

腾讯安全专家建议企业运维人员使用腾讯主机安全对云主机进行文件扫描，亦可排查以下条目，以检测清除威胁。

 **进程：**

排查以下可疑进程：

Linux*

spreadMvwxya*

 **文件：**

排查以下可疑文件：

/tmp/linux*

/tmp/spreadMvwxya*

 **启动项：**

排查以下位置是否存在可疑启动项：

/etc/rc.local

/etc/crontab

 **加固建议：**

腾讯安全专家建议企业运维人员升级shiro 组件到无漏洞版本（高于1.2.4）。

# 二、样本分析

腾讯云防火墙拦截到有攻击者利用shiro1.2.4反序列化漏洞攻击云上主机，传播Satan
DDoS僵尸网络木马（载荷地址：hxxp://116.202.251.12/linux64）

![](https://image.3001.net/images/20210608/1623155947_60bf64eb6439281953140.png!small)

分析恶意载荷为ELF文件格式，基于x86-64指令集，分析其代码发现，该僵尸网络木马自称为“Satan
DDos木马”，自称支持可攻击多平台，木马支持多架构，可利用多个漏洞攻击传播，包括通过FTP、IPC、SMB、WMI、MSSQL、EternalBlue、Eternalromance、CVE-2017-8464、Thinkphp、HFS、phpstudy、Laravel、durpal、Shareddisk、sharedirectory............等等多种漏洞利用方式攻击传播。

![](https://image.3001.net/images/20210608/1623155957_60bf64f5ae78090d5ccac.png!small)

进一步分析可知Satan DDos木马通过设置/etc/rc.local、crontab两种方式实现持久化。Satan
DDos僵尸网络用的一些关键配置信息经加密存储，对其进行解密后可知其中包含了一系列挖矿所需配置，配置相关信息如下：

僵尸网络C2：116.202.251.12

矿工使用配置信息：

矿池&钱包：

-o stratum+tcp://pool.supportxmr.com:5555 -u 44ygo7VfwEYdEbe1ruyZNLfrV19snk3REQpfb5LU9Yxf98z7Ws9EZPPbUgvozZyfYXCb3vsRJRT8wTGe3FipsLb93NaDULN -p X

-o stratum+tcp://pool.supportxmr.com:5555 -a cn/r -u 44ygo7VfwEYdEbe1ruyZNLfrV19snk3REQpfb5LU9Yxf98z7Ws9EZPPbUgvozZyfYXCb3vsRJRT8wTGe3FipsLb93NaDULN -p X

矿工保存路径：

/tmp/spreadMvwxya

矿工恶意载荷下载地址：

hxxp://116.202.251.12/X64

![](https://image.3001.net/images/20210608/1623155969_60bf65017f4df3512cf42.png!small)

![](https://image.3001.net/images/20210608/1623155979_60bf650b8f4db8a6df0f3.png!small)

同时Satan DDoS僵尸网络会创建线程作为Miner的守护进程，当检测到矿工文件或进程不存在时，会重新下载、执行，以保护挖矿模块正常运转。

![](https://image.3001.net/images/20210608/1623155989_60bf65154889ba270f94c.png!small)

同时也会创建线程结束一些疑似和自己同名，或疑似为挖矿相关的进程，以清除竞品挖矿木马，独占系统资源。

![](https://image.3001.net/images/20210608/1623155997_60bf651dd334d1817be90.png!small)

作为DDoS木马，Satan 同时具备tcp，udp，http，icmp，syn等多种流量攻击模式，攻击方式丰富齐全。

![](https://image.3001.net/images/20210608/1623156007_60bf6527425858b504f7e.png!small)

除DDoS攻击外，Satan僵尸网络木马同时具备一系列的后门指令相关功能，包括了下载执行、命令执行、矿工配置等操作功能。收包前4字节为指令控制码，无加密。涉及指令具体功能信息如下：

 **控制码**

|

 **功能**  
  
---|---  
  
0x4

|

开启DDoS攻击  
  
0x5

|

停止DDoS攻击  
  
0x6

|

下载执行  
  
0x7

|

命令执行  
  
0x8

|

矿工运行状态暂停C2更新  
  
0x9

|

矿工运行状态开始C2更新  
  
0xA

|

矿工配置（矿池 钱包）更新  
  
0xB

|

开始挖矿  
  
0xC

|

停止挖矿  
  
# 四、威胁视角看攻击行为

 **ATT &CK** **阶段**

|

 **行为**  
  
---|---  
  
 **侦察**

|

扫描端口，确认可攻击目标存在的Shiro等服务  
  
 **资源开发**

|

注册C2服务器  
  
 **初始访问**

|

利用对外开放的Shiro服务，植入恶意命令执行恶意命令进而入侵系统  
  
 **执行**

|

利用漏洞植入恶意命令，随后下载植入Satan DDoS木马，XMR挖矿矿工  
  
 **持久化**

|

通过写/etc/rc.local和crontab实现持久化驻留  
  
 **防御规避**

|

通过僵尸进程作为Guarder，监控矿工Miner意外终止情况下对其下载再次拉起，保护顺利挖矿不中断。  
  
 **发现**

|

通过扫描目标开放Shiro服务确认后续漏洞攻击方式  
  
 **影响**

|

驻留的僵尸木马具备下载执行，命令执行等后门功能。将给服务器带来不可预料的各类型网络风险。门罗币矿机模块不间断的工作，会导致系统CPU负载过大，大量消耗主机CPU资源，严重影响主机正常服务运行，导致主机有系统崩溃风险。  
  
# IOCs

 **MD5:**

b8f0f26296f41a5a7995febbca90c5f1

2ef2a33995c299e3bb51a7f3f4cab010

 **C2:**

116.202.251.12

 **URL:**

hxxp://116.202.251.12/X64

hxxp://116.202.251.12/linux64

 **矿池 &钱包**

pool.supportxmr.com

44ygo7VfwEYdEbe1ruyZNLfrV19snk3REQpfb5LU9Yxf98z7Ws9EZPPbUgvozZyfYXCb3vsRJRT8wTGe3FipsLb93NaDULN

# 参考链接：

<https://unit42.paloaltonetworks.com/lucifer-new-cryptojacking-and-ddos-hybrid-malware/>

<https://digital.nhs.uk/cyber-alerts/2020/cc-3526>

