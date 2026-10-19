## 前言

**网络犯罪分子正在利用一个在2018年12月被发现和已修补的ThinkPHP漏洞传播Yowai（Mirai变种）和Hakai（Gafgyt变种）两种僵尸网络病毒。**

 **网络犯罪分子利用字典攻击破坏使用PHP框架创建网站的Web服务器，并获得这些路由器的控制，以实现分布式拒绝服务攻击（DDoS）。**

## Yowai

Yowai（[BACKDOOR.LINUX.YOWAI.A](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/Backdoor.Linux.YOWAI.A?_ga=2.130091983.1121408999.1549076183-1991156975.1541925994)，由趋势科技检测）具有与其他Mirai变体类似的配置表。其配置表使用相同的过程进行解密，并将ThinkPHP漏洞利用添加到感染列表中。

Yowai侦听端口6以接收来C＆C服务器的命令。在感染路由器后，它会使用字典攻击来尝试感染其他设备。受影响的路由器现在成为僵尸网络的一部分，使其运营商能够使用受影响的设备发起DDoS攻击。

Yowai利用许多其他漏洞来补充字典攻击，它在执行后会在用户控制台上显示一条消息。分析发现它还包含一个竞争的僵尸网络列表，它将从系统中清除这些竞争的僵尸网络。

![](https://image.3001.net/images/20190212/15499611534104.png!small)

字典攻击的用户名/密码 | 竞争僵尸网络名单  
---|---  
OxhlwSG8  
defaulttlJwpbo6S2fGqNFsadmin  
daemon  
12345  
guest  
support  
4321  
root  
vizxv  
t0talc0ntr0l4!  
bin  
adm  
synnet | dvrhelper, mirai, light, apex, Tsunami, hoho, nikki, miori, hybrid,
sora, yakuza, kalon, owari, gemini, lessie, senpai, apollo, storm, Voltage,
horizon, meraki, Cayosin, Mafia, Helios, Sentinel, Furasshu, love, oblivion,
lzrd, yagi, dark, blade, messiah, qbot, modz, ethereal, unix, execution,
galaxy, kwari, okane, osiris, naku, demon, sythe, xova, tsunami, trinity,
BUSHIDO, IZ1H9, daddyl33t, KOWAI-SAD, ggtr, QBotBladeSPOOKY, SO190Ij1X,
hellsgate, sysupdater, Katrina32  
  
表1. Yowai用于字典攻击的默认用户名和密码列表以及从系统中删除竞争僵尸网络的列表

除了ThinkPHP漏洞，Yowai还利用了以下漏洞：CVE-2014-8361，a Linksys RCE，CVE-2018-10561，CCTV-DVR
RCE。

![](https://image.3001.net/images/20190212/15499611718693.jpg!small)

## Hakai

Gafgytd变种Hakai（[BACKDOOR.LINUX.HAKAI.AA](https://www.trendmicro.com/vinfo/us/threat-encyclopedia/malware/Backdoor.Linux.HAKAI.AA?_ga=2.196749932.1121408999.1549076183-1991156975.1541925994)，由趋势科技检测）僵尸网络病毒感染物联网（IoT）设备并依赖路由器漏洞进行传播。

![](https://image.3001.net/images/20190212/15499611918167.png!small)

![](https://image.3001.net/images/20190212/15499612021298.jpg!small)

有趣的是，Hakai的样本包含从Mirai复制的代码，特别是用于加密其配置表的函数。但是，该函数无法运行，怀疑telnet字典攻击的代码是故意删除的，以使Hakai更加隐蔽。

由于Mirai的变种通常会杀死竞争僵尸网络，Hakai避免攻击使用默认密码的IoT设备从而更有生存的优势。与暴力破解telnet相比，单独利用漏洞传播的方法更难以检测。

![](https://image.3001.net/images/20190212/15499612137735.png!small)

![](https://image.3001.net/images/20190212/1549961237260.png!small)

## 结论

鉴于ThinkPHP是一个免费的开源PHP框架，因其简化的功能和易用性而受到开发人员和公司的欢迎，很容易被Hakai和Yowai这样的恶意程序滥用，进而破坏Web服务器和攻击网站。随着更多的僵尸网络代码可以在线获得和交换，可以预见相互竞争的僵尸网络具有相似的代码。

此外，网络犯罪分子会继续研究类似Mirai的僵尸网络，开发更多Mirai变种，并增加恶意软件的适应性，攻击越来越多的使用默认密码的IoT设备。物联网设备用户应将其设备固件更新到制造商发布的最新版本，修补漏洞。用户还应经常更新设备密码，以防止未经授权的登录。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/thinkphp-vulnerability-abused-by-botnets-hakai-and-yowai/)，fengbin8606编译整理，转载请注明来自 FreeBuf.COM。**

