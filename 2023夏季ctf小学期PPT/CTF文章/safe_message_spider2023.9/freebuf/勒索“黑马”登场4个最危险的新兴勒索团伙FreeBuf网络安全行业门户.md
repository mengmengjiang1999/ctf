> **最新研究揭露了4个新兴勒索软件团伙，这些团伙不仅正在影响全球组织，而且未来很可能会成长为更具威胁的存在。**

![1629880186_6125ff7a1f7ac2d1dd6c6.jpg!small?1629880183803](https://image.3001.net/images/20210825/1629880186_6125ff7a1f7ac2d1dd6c6.jpg!small?1629880183803)

近日，Palo Alto Networks公司Unit 42的最新研究已经确定了4个新兴勒索软件组织，并表示未来它们完全有潜力成为更大的麻烦。这些组织分别为
**Avoslocker、Hive Ransomware、Hellokitty以及Lockbit 2.0** 。

## 新兴勒索软件威胁组织

安全公司Palo Alto Networks在其最新报告《值得注意的勒索软件组织：新兴威胁》中表示，

> “随着REvil以及Darkside等主要勒索软件组织瓦解或重组以逃避执法机构和媒体的目光，新群体将不断涌现，以取代那些不再积极锁定受害者的组织。”

在该研究中，威胁情报分析师Doel Santos以及主要威胁研究人员Ruchna Nigam就4个勒索软件组织的行为进行了详细阐述。

### AvosLocker

AvoSlocker首次出现于2021年7月，它是一个“勒索软件即服务”（RaaS）组织，由Avos控制，主要通过暗网讨论论坛Dread宣传其服务。其赎金通知中包括用于识别受害者的信息和ID，以及指导感染者访问Avoslocker
Tor站点进行恢复和数据复原的指南。该研究指出，AvoSlocker的赎金要求从50,000美元到75,000美元（以门罗币形式）不等，并且已经在全球7个组织中发现了感染案例。

### Hive Ransomware

研究称，Hive Ransomware于2021年6月开始运营，主要针对医疗保健组织以及其他配置薄弱无法抵御网络攻击的企业。该组织在其泄露网站Hive
Leaks上公布了首个受害者信息后，又陆续发布了另外28个受害者的详细信息。研究人员称，

>
> “当执行该勒索软件时，它会drop两个批处理脚本，第一个脚本hive.bat会尝试删除自身，而第二个脚本负责删除系统的影子副本（Shadow.bat）。Hive
> RansomWare将[随机字符].hive
> extension添加到加密文件中并留下标题为‘HOW_TO_DECRYPT.txt’的赎金通知，其中包含防止数据丢失的说明和操作指南。”

受害者通过赎金通知中的操作指南与攻击者讨论解密细节。研究人员无法确定该勒索软件的确切交付方式，但他们认为诸如凭证暴力破解或鱼叉式钓鱼等传统手段应该都有发挥作用。

### HelloKitty：Linux版本勒索软件

Hellokitty家族最早出现于2020年，主要针对Windows系统。它以使用Hellokittyex而得名。2021年，Palo
Alto检测到一个Linux（ELF）样本，名为“funny_linux.elf”其中包含一个赎金通知，该赎金通知的措辞与之后发现的HelloKitty
for Windows样本相匹配。3月份，该勒索软件组织开始瞄准ESXi，这也是最近Linux勒索软件变体的选择目标。研究人员表示，

> “奇怪的是，攻击者在不同样本的赎金通知中共享的首选通信模式是Tor
> URL和特定于受害者的ProtonMail电子邮件地址间的混合。这可能表示不同的攻击活动甚至完全不同的威胁行为者使用了相同的恶意软件代码库。”

研究观察到，该勒索软件组织使用椭圆曲线数字签名算法（ECDSA）加密文件，而从该团体观察到的最高赎金要求为1000万美元（以门罗币形式）。

### LockBit 2.0

LockBit 2.0以前名为ABCD ransomware，同样是以勒索软件即服务（RssS）模式运行的组织。虽然早在2019年就开始活跃，但Palo
Alto最近发现其攻击方法已经发生了变化，而且其运营者还声称，他们当前的变体是操作中最快的加密软件。自6月以来，该组织已经攻击了全球52个组织。研究人员表示，

> “威胁行为者在泄漏网站上的所有帖子中都放置了倒计时，直到保密信息发布给公众，这为受害者制造了额外的压力。”

一旦执行操作，Lockbit 2.0就会立即开始文件加密并附加.lockbit扩展。加密完成后，标题为Restore-My-files.txt的赎金通知会告知受害者攻击事实并提供有关解密步骤的建议。

## 参考

> [csoonline](https://www.csoonline.com/article/3630391/4-most-dangerous-> emerging-ransomware-threat-groups-to-watch.html)

