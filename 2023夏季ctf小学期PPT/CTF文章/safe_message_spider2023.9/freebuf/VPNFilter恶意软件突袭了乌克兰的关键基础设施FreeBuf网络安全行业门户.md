**就在今天，乌克兰安全局（SBU）对外声称，乌克兰境内的关键基础设施遭到了VPNFilter恶意软件的攻击，而这款恶意软件据说来源于俄罗斯情报机构。**  

![11.png](https://image.3001.net/images/20180716/15317231286741.png!small)

根据SBU的描述，安全研究人员在乌克兰的第聂伯罗彼得罗夫斯克市（Dnipropetrovsk）Aulska氯气站的工控系统中检测到了这款恶意软件，而该组织是乌克兰国内的重要基础设施之一，因为它主要负责向乌克兰境内的污水处理厂提供用于清洁水处理的氯原料。

据报道，该恶意软件主要针对的是工控系统中的技术处理流程以及安全保护系统，但是乌克兰安全局表示，他们的安全专家迅速检测到了VPNFilter的存在，并屏蔽了它想要尝试进行的恶意操作。SBU表示，此次攻击如果成功的话，将会让Aulska氯气站的工控系统终止运行，并让受影响的系统发生崩溃，甚至还有可能对设备造成物理损害，从而导致“灾难性”的事件发生。安全研究人员认为，此次攻击的主要目标很可能是为了破坏该基础设施的正常运作。

SBU[表示](https://ssu.gov.ua/ua/news/1/category/21/view/5037#.j5G0mWMm.dpbs)，虽然此次攻击主要针对的是氯气站，但这也有可能是巧合，因为VPNFilter已经成功入侵了至少50万台路由器和网络附加存储设备（NAS）了，而乌克兰就是这款恶意软件的主要目标。

### 下图显示的是VPNFilter的攻击机制：

![22.png](https://image.3001.net/images/20180716/15317231398860.png!small)

在此之前，美国当局曾尝试通过[拿下VPNFilter其中的一个命令控制域名](https://www.securityweek.com/us-disrupts-russian-botnet-500000-hacked-routers)来破坏攻击者的活动，但研究人员表示VPNFilter目前[仍在威胁乌克兰境内的关键基础设施](https://www.securityweek.com/vpnfilter-continues-targeting-routers-ukraine)。

实际上，乌克兰把此次事件的罪魁祸首怪罪到俄罗斯身上其实并不令人惊讶，甚至连美国政府都认为此次攻击活动跟[克林姆林宫赞助的一些网络间谍组织](https://www.securityweek.com/fbi-attribution-vpnfilter-attack-raises-questions)有关。

VPNFilter僵尸网络于今年五月份被曝光出来，当时的VPNFilter就已经能够入侵超过50款路由器和NAS设备了，受影响的厂商包括Linksys、MikroTik、网件、TP-Link、QNAP、华硕、D-Link、华为、UBiQuTI、Upple、和中兴等在内。

研究人员表示，这款恶意软件不仅能够拦截被入侵设备发送和接收的数据，而且还可以监控那些采用Modbus
SCADA协议进行通信的网络系统。除此之外，它还可以让受感染设备无法正常工作。

当然了，乌克兰已经不是第一次把网络攻击活动怪罪到俄罗斯身上了，在此之前，俄罗斯曾被指控对[乌克兰电力网络系统](https://www.securityweek.com/blackenergy-group-uses-destructive-plugin-ukraine-attacks)发起过[NotPetya攻击](https://www.securityweek.com/us-canada-australia-attribute-notpetya-attack-russia)活动。

 *** 参考来源：[securityweek](https://www.securityweek.com/vpnfilter-malware-hits-critical-infrastructure-ukraine)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

