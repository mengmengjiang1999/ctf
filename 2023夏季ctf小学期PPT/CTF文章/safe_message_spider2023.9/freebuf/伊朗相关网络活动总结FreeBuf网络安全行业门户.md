**随着中东地区局势紧张，人们十分关注伊朗是否会发动网络攻击。以下威胁总结包含与伊朗活动有关的历史攻击摘要，以及自2020年1月3日事件以来发生的任何新的威胁或攻击。自2010年以来伊朗在全世界的网络活动中一直很活跃。目前已经命名和发布了许多组织团体和活动，但是许多情况下仍然缺乏直接指向伊朗政府的证据，大多数判断都依赖于针对目标和潜在动机的战术证据。**

其中一些当前活跃的组织团体和活动有：

> OilRig (AKA APT34/Helix Kitten)
>
> MagicHound (AKA APT35/Newscaster/Cobalt Gypsy)
>
> APT33 (AKA Refined Kitten/Elfin)
>
> DarkHydrus
>
> Shamoon
>
> MuddyWater (AKA Static Kitten)

这些组织团体有两种不同的动机：间谍活动和破坏活动。大多数攻击活动都与间谍活动有关，相关的组织团体正在继续尝试进入目标组织访问敏感数据，同时也观察到了少量高度集中的破坏性攻击，从2012年的Shamoon攻击以及最近的StoneDrill和ZeroCleare。

总体而言，过去十年来源自伊朗的网络攻击一直持续存在，其目标已经遍及全球所有主要行业。虽然在不久的将来可能会发生报复性行动，但极大程度上会与正在进行的攻击活动结合在一起。

以下是常用的战术、技术及其相关的ATT＆CK ID列表：

> Phishing ([T1193
> ](https://attack.mitre.org/techniques/T1193/)[T1192](https://attack.mitre.org/techniques/T1192/))
>
> Credential harvesting
> ([T1078](https://attack.mitre.org/techniques/T1078/),[T1003](https://attack.mitre.org/techniques/T1003/),[T1503](https://attack.mitre.org/techniques/T1053/),[T1081](https://attack.mitre.org/techniques/T1081/),[T1214](https://attack.mitre.org/techniques/T1214/))
>
> DNS Tunneling ([T1071](https://attack.mitre.org/techniques/T1071/))
>
> DNS Hijacking ([T1326](https://attack.mitre.org/techniques/T1326/))
>
> EldoS RawDisk driver
> ([T1485](https://attack.mitre.org/techniques/T1485/),[T1488](https://attack.mitre.org/techniques/T1488/),[T1487](https://attack.mitre.org/techniques/T1487/),[S0364](https://attack.mitre.org/software/S0364/))
>
> Malicious macros ([T1204](https://attack.mitre.org/techniques/T1204/))
>
> Weaponized Excel and Word documents
> ([T1204](https://attack.mitre.org/techniques/T1204/),[T1221](https://attack.mitre.org/techniques/T1221/),[T1173](https://attack.mitre.org/techniques/T1173/))
>
> Script based backdoors
> ([T1064](https://attack.mitre.org/techniques/T1064/),[T1027](https://attack.mitre.org/techniques/T1027/))
>
> Webshell deployment
> ([T1108](https://attack.mitre.org/techniques/T1108/),[T1133](https://attack.mitre.org/techniques/T1133/),[T1190](https://attack.mitre.org/techniques/T1190/),[T1027](https://attack.mitre.org/techniques/T1027/))
>
> Domain masquerading ([T1328](https://attack.mitre.org/techniques/T1328/))
>
> Scheduled tasks ([T1053](https://attack.mitre.org/techniques/T1053/))
>
> Use of Mimikatz
> ([T1003](https://attack.mitre.org/techniques/T1003/),[T1207](https://attack.mitre.org/techniques/T1027/),[T1098](https://attack.mitre.org/techniques/T1098/),[T1081](https://attack.mitre.org/techniques/T1081/),[S0002](https://attack.mitre.org/software/S0002/))
>
> Exploitation of enterprise VPN Software
> ([T1133](https://attack.mitre.org/techniques/T1133/),[T1210](https://attack.mitre.org/techniques/T1210/))

缓解措施建议如下：

> 提高对网络钓鱼攻击的教育和认识
>
> 在整个组织中启用多因素身份验证
>
> 在网络安全设备中启用凭据盗窃检测功能
>
> 启用异常DNS行为检测/预防功能
>
> 将EldoS RawDisk驱动程序列入黑名单
>
> 执行查看宏文档的安全策略
>
> 限制在终端上执行脚本文件
>
> 查看所有网络应用程序并部署最新补丁
>
> 在网络安全设备中启用URL分类功能
>
> 扫描终端查找新的或未知的计划任务
>
> 检测Mimikatz相关的行为
>
> 尽快修补远程公开软件漏洞

## 相关组织详情

### [OilRig](https://www.freebuf.com/wp-admin/post.php?post=225149&action=edit)(AKA APT34/Helix Kitten)

OilRig于2016年5月被发现命名。该组织活动非常持久，依赖鱼叉式网络钓鱼作为其初始攻击媒介，也有其他更复杂的攻击例如凭据收集和DNS劫持。在鱼叉式网络钓鱼攻击中，OilRig使用Microsoft
Office（Word和Excel）宏来安装其自定义有效负载，这些有效负载可执行PE文件，PowerShell和VBScripts。
OilRig的自定义有效载荷经常将DNS隧道用作命令和控制（C2）通道。

获得了访问端点的权限，攻击者就可以使用Mimikatz等工具收集帐户凭据，横向移动到网络上的其他系统中。OilRig会安装一个Webshel​​l作为另一个入口点，维护对网络的访问。

相关参考：

> <https://unit42.paloaltonetworks.com/behind-the-scenes-with-oilrig/>
>
> <https://unit42.paloaltonetworks.com/dns-tunneling-in-the-wild-overview-of-> oilrigs-dns-tunneling/>
>
> <https://unit42.paloaltonetworks.com/unit42-analyzing-oilrigs-ops-tempo-> testing-weaponization-delivery/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-uses-updated-bondupdater-> target-middle-eastern-government/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-targets-middle-eastern-> government-adds-evasion-techniques-oopsie/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-targets-technology-> service-provider-government-agency-quadagent/>
>
> <https://unit42.paloaltonetworks.com/unit42-oopsie-oilrig-uses-threedollars-> deliver-new-trojan/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-uses-rgdoor-iis-backdoor-> targets-middle-east/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-performs-tests-twoface-> webshell/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-deploys-alma-> communicator-dns-tunneling-trojan/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-group-steps-attacks-new-> delivery-documents-new-injector-trojan/>
>
> <https://unit42.paloaltonetworks.com/unit42-striking-oil-closer-look-> adversary-infrastructure/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-uses-ismdoor-variant-> possibly-linked-greenbug-threat-group/>
>
> <https://unit42.paloaltonetworks.com/unit42-oilrig-actors-provide-glimpse-> development-testing-efforts/>
>
> <https://unit42.paloaltonetworks.com/the-oilrig-campaign-attacks-on-saudi-> arabian-organizations-deliver-helminth-backdoor/>

### [Magic Hound ](https://attack.mitre.org/groups/G0059/)(AKA
APT35/Newscaster/Cobalt Gypsy)

“Magic Hound”以鱼叉式网络钓鱼邮件为传递手段，主要目标为能源，政府和技术组织。附件中启用宏Microsoft
Office文档和PE文件，文档和可执行文件将安装各种工具，包括可移植的PE文件，.NET Framework PE文件，Meterpreter，IRC
bot，开源Meterpreter模块以及Pupy的开源Python RAT。

Magic Hound中使用的自定义工具显示了该组织与其他活动的关联，例如IRC Bot，它与NEWSCASTER的Parastoo工具非常相似。

相关参考：

> <https://unit42.paloaltonetworks.com/unit42-magic-hound-campaign-attacks-> saudi-targets/>

### [APT33](https://attack.mitre.org/groups/G0064/)(AKA Refined Kitten/Elfin)

APT33对航空和能源领域有浓厚兴趣， 他们使用带有域伪装技术的鱼叉式钓鱼进行攻击，将自定义工具与各种黑客论坛中出售的公共后门结合使用。
最近的一份报告发现该组织的攻击基础设施，该基础设施利用了商业VPN以及受感染的系统作为代理，以进一步掩盖其来源。

相关参考：

> <https://www.fireeye.com/blog/threat-research/2017/09/apt33-insights-into-> iranian-cyber-espionage.html>
>
> <https://blog.trendmicro.com/trendlabs-security-intelligence/more-than-a-> dozen-obfuscated-apt33-botnets-used-for-extreme-narrow-targeting/>

### [DarkHydrus](https://attack.mitre.org/groups/G0079/)

DarkHydrus以鱼叉式钓鱼攻击和凭据收集为主要手段，其目标为政府和教育机构。
该组织的工具集和TTP显示出更高的技能水平，除了可公开的红队工具（如Phishery）外，DarkHydrus还使用了自定义工具，
还发现他们使用Google云盘。

相关参考：

> <https://unit42.paloaltonetworks.com/unit42-new-threat-actor-group-> darkhydrus-targets-middle-east-government/>
>
> <https://unit42.paloaltonetworks.com/unit42-darkhydrus-uses-phishery-> harvest-credentials-middle-east/>
>
> <https://unit42.paloaltonetworks.com/darkhydrus-delivers-new-trojan-that-> can-use-google-drive-for-c2-communications/>

### Shamoon

Shamoon攻击起始于2012年，其主要针对能源领域的两个特定组织，目标是通过破坏磁盘使计算机系统无法运行。
攻击软件包括驱动程序（用于执行擦除任务），一个蠕虫组件，该组件可以自动在目标组织内传播。自最初的2012年攻击以来，在2016年和2018年发现了Shamoon的另外两个攻击实例。

相关参考：

> <https://securelist.com/shamoon-the-wiper-copycats-at-work/57854/>
>
> <https://unit42.paloaltonetworks.com/unit42-shamoon-2-return-disttrack-> wiper/>
>
> <https://unit42.paloaltonetworks.com/unit42-second-wave-shamoon-2-attacks-> identified/>
>
> <https://unit42.paloaltonetworks.com/unit42-shamoon-2-delivering-disttrack/>
>
> <https://unit42.paloaltonetworks.com/shamoon-3-targets-oil-gas-> organization/>
>
> <https://unit42.paloaltonetworks.com/shamoon-3-modified-open-source-wiper-> contains-verse-from-the-quran/>

### MuddyWater (AKA Static Kitten)

MuddyWater成立于2017年，该组织使用开源工具，以经济利益为主要目标。
进一步的调查显示，MuddyWater可能是独立进行的网络活动，其通常将鱼叉式网络钓鱼与宏Office文档一起使用以传递其有效负载。有效负载可以直接嵌入宏中，也可以托管在第一阶段C2服务器上。
MuddyWater工具集的很大一部分包括开源的红队工具，例如Invoke-Obfuscation，Lazagne，Mimikatz等。

相关参考：

> <https://unit42.paloaltonetworks.com/unit42-muddying-the-water-targeted-> attacks-in-the-middle-east/>
>
> <https://securelist.com/muddywater/88059/>
>
> <https://www.clearskysec.com/muddywater2/>
>
> <https://blog.trendmicro.com/trendlabs-security-intelligence/muddywater-> resurfaces-uses-multi-stage-backdoor-powerstats-v3-and-new-post-> exploitation-tools/>

## 总结

假设这些组织团体确实属于伊朗，他们的活动已有据可查且各个团体经常使用相似的战术和技术来进行攻击，例如大量使用鱼叉式网络钓鱼和证书收集。

在过去的十年中活动一直持续存在，随着最近的地缘政治事件，这种活动应该会继续增加。
相对简单的安全策略可以帮助抵御这些攻击者的恶意行为，包括启用多因素身份验证（MFA），适当地对网络进行分段，限制启用宏文档等。

## IOCs

> [Link to IOCs on GitHub](https://github.com/pan-> unit42/iocs/tree/master/iran_linked_operators)

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/threat-brief-iranian-linked-cyber-operations/)，由Kriston编译，转载请注明来自FreeBuf.COM**

