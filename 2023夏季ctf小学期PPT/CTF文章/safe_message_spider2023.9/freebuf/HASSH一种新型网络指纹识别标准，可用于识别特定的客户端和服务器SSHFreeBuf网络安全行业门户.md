## 前言

**今天给大家介绍的是一款名叫“HASSH”的工具。实际上，“HASSH”更像是一种新型的网络指纹识别标准，因为它可以用来识别特定的客户端或服务器端SSH的实现方式。由于HASSH在存储指纹时采用的是MD5指纹，这样就降低了数据存储、搜索和共享的开销。**

![页首配图](https://image.3001.net/images/20181121/1542814416_5bf57ad0597ba.png!small)

## HASSH的功能

> 1、 高度可控制，检测到任意指纹后会发出警报。
>
> 2、 可检测、控制和调查暴力破解/Cred Stuffing密码攻击尝试。
>
> 3、
> 检测客户端算法集中隐藏的数据提取组件，在这种情况下，特殊编码的SSH客户端可以通过受信环境和一系列SSH_MSG_KEXINIT数据包来发送带外数据，而这些行为或数据发送尝试都会被HASSH的分析监控系统捕捉到，并给用户发送警报。
>
> 4、
> 配合使用了其他的指标识别工具来检测网络扫描和横向渗透活动，可检测的工具列表包括Paramiko、Powershell、Ruby、Meterpreter和Empire。
>
> 5、 与其他用户共享HASSH中的入侵威胁指标。
>
> 6、 创建额外的客户端应用程序控制层，比如说，你可能需要屏蔽客户端对SSH服务器的全部连接等等。
>
> 7、 贡献数据取证信息，例如IP源等等，但这部分数据可能会受NAT或使用了多个IP源的情况影响。
>
> 8、 检测欺骗性应用程序。
>
> 9、 检测已知HASSH指纹的物联网嵌入式系统。例如摄像头、麦克风和键盘记录器等等。

## HASSH的工作机制

![HASSH的工作机制](https://image.3001.net/images/20181121/1542814435_5bf57ae36f97a.png!small)

“hassh”和“hasshServer”采用了通过特定算法集设计的MD5哈希结构，目前很多的SSH客户端以及服务器端应用程序都支持这样的架构。这些算法在初始的TCP三次握手完成之后会进行交换，对应的明文数据包为"SSH_MSG_KEXINIT"消息，这也是最终加密SSH信道配置的重要组成部分。由于这些算法的交换顺序是唯一的，所以它可以被当做网络指纹并用来识别底层的客户端以及服务器端应用程序，而且这样也避免了通过“Client”或“Server”字符串这种表面上的识别因素来判断底层实现。

## 工具下载

Hassh：【[GitHub下载地址](https://github.com/salesforce/hassh/)】

## 参考资料

1、 RFC4253-SSH传输层协议：【[传送门](https://www.ietf.org/rfc/rfc4253.txt)】

2、 Salesforce技术博文：【[传送门](https://engineering.salesforce.com/open-sourcing-hassh-abed3ae5044c)】

 *** 参考来源：[kitploit](https://www.kitploit.com/2018/11/hassh-network-fingerprinting-standard.html?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+PentestTools+%28PenTest+Tools%29)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

