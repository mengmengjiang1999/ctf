![24.jpg](https://image.3001.net/images/20181025/1540439804_5bd13efc8c7d5.jpg!small)  

**900万熊迈摄像机，DVR广泛攻击**

 **  
**

中国制造商杭州雄迈科技公司的视频监控设备中发现了一些关键漏洞，发现的漏洞包括默认管理员密码（即无密码，无需在初始设置阶段设置一个密码），硬编码“默认”帐户的不安全默认凭据，多个未加密的通信通道以及无法检查完整性固件更新，未签名。

研究人员补充说，允许用户连接到公司的“XMEye P2P
Cloud”并与其设备进行交互的ID很容易从设备的MAC地址中获得，以及与云服务器提供商的连接（默认情况下已启用）没有加密。还没有关于谁运行这些服务器及其所在位置的信息。

最后，最重要的是，他们发现P2P云功能可以绕过防火墙并允许远程连接到专用网络。

详文阅读：

<https://www.helpnetsecurity.com/2018/10/10/vulnerable-xiongmai-cameras/>

  

 **亚马逊修复智能家居13个漏洞：防止黑客完全控制设备**

 **  
**

曝光本次漏洞的Zimperium发现FreeRTOS的TCP/IP协议栈和AWS安全连接模块中的多个漏洞，受到影响系统对应FreeRTOS版本V10.0.1及其以下，AWS
FreeRTOS版本V1.3.1及其以下。而且由WITTENSTEIN公司维护的SafeRTOS（经过安全认证的版本）竟也存在相同的TCP/IP协议栈漏洞。这些漏洞允许攻击者使设备崩溃，从设备内存泄漏信息，并远程执行设备上的代码，从而完全破坏设备。

详文阅读：

<https://mp.weixin.qq.com/s/JDW-qiLLPMsnbG1WV_jaiA>

  

 **物联网僵尸网络“捉迷藏”新变种发现：Android 设备成新受害者**

  

继今年1月发现首个物联网僵尸网络Hide and Seek（HNS，捉迷藏）之后，近日Bitdefender
Labs发布报告称已经发现新型变种。利用Android开发者调试之用的Android Debug Bridge
(ADB)功能中所存在的漏洞，该变种通过WiFi网络连接来感染Android设备，使之成为僵尸网络的一员。

虽然并非所有Android都默认启用ADB功能，但部分Android手机厂商会默认自动启用，可以通过5555端口使用WiFi
ADB远程连接就能轻松进行攻击。在连接至默认激活ADB的Android系统之后，允许攻击者以root级别获得shell访问，可以在受感染设备上运行和安装任何东西。

详文阅读：

<http://hackernews.cc/archives/24232>

  

 **最新Chalubo僵尸网络来袭，目标指向服务器和物联网设备**

 **  
**

网络安全公司Sophos旗下SophosLabs在本周一（10月22日）发表的一篇博文中指出，他们近两个月一直在持续关注一场开始于9月初的网络攻击活动，目标是开启了SSH服务器的Linux服务器。而在这场攻击活动中，攻击者的主要目的在于传播一种被他们称之为“Chalubo”的最新自动化DDos攻击工具。

SophosLabs的分析表明，攻击者使用了ChaCha流密码来加密Chalubo的主组件以及相应的Lua脚本，而在最新的版本中，攻击者已经采用了更常见的Windows恶意软件原理来阻止对Chalubo的检测。不变的是，最新版本的Chalubo同样整合了来自Xor.DDoS和Mirai恶意软件家族的代码。

详文阅读：

<https://www.hackeye.net/threatintelligence/16905.aspx>

  
  

 **D-Link路由器三个未修补漏洞 可被攻击者远程控制，且暂无修复补丁可用**

 **  
**

相关报道指出，由西里西亚工业大学研究小组发现的三个安全漏洞包括一个目录遍历漏洞（CVE-2018-10822）、一个密码明文保存漏洞（CVE-2018-10824）和一个Shell命令注入漏洞（CVE-2018-10823），将它们结合起来使用可以获得对易受攻击路由器的完全控制权限。

详文阅读：

<https://securityaffairs.co/wordpress/77201/hacking/d-link-routers.html>

