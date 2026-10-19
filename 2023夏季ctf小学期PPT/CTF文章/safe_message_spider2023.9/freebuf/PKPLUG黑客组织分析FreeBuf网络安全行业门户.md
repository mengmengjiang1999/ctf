**三年来，研究人员发现并追踪了一组遍布亚洲的网络间谍攻击活动，攻击中同时使用了公开和自定义恶意软件，研究人员将该黑客组织命名为PKPLUG。但还不能确定这是一个黑客组织，还是多个黑客组织在使用相同的工具并有相同的任务。**

PKPLUG来自于将plugx恶意软件作为dll放入zip存档文件中的策略，zip文件格式的头中包含ascii字节“pk”，因此是pkplug。

在研究过程中，研究人员将其与6年前的攻击活动联系起来。关于PKKPUT的最终目标还不完全清楚，但是根据安装在目标系统上的后门木马，推断跟踪目标和收集信息是该组织目的之一。

受害者主要分布在亚洲东南沿海国家，尤其是缅甸、越南和印度尼西亚，在亚洲的其他地区也有出现，如**、新疆和蒙古。

## 目标分析

基于PKPULTE活动情况收集，受害者主要分布在南洋地区和周边地区。具体而言，目标国家（地区）/省份包括，缅甸和中国台湾，越南和印度尼西亚。亚洲其他地区的目标包括蒙古、**和新疆。

印度尼西亚、缅甸和越南是东盟成员国；蒙古，特别是独立国家，又称外蒙古；**和新疆是中国的自治区。该地区的进一步紧张可以归因于对南海的所有权要求，包括捕捞配额和尚未被证实的石油和天然气储量。

## 时间线

本节记录了有关pkplug的网络攻击的先前工作。下图说明了样本出现的时间顺序，突出显示了每个样本的关键发现。

PKPACK已经活跃了六年或更长时间，有各种各样的目标和攻击手法。

![](https://image.3001.net/images/20191006/1570374553_5d9a0399cec4a.jpeg!small)

上图中的水平时间线显示的日期与发布日期有关，而不是活动攻击日期。

### 首次发现

2013年11月，Blue
Brand实验室发布了一份[报告](https://web.archive.org/web/20161017235500/https://www.bluecoat.com/security-blog/2013-11-25/plugx-used-against-mongolian-targets)，描述了攻击者使用Plurx恶意软件攻击蒙古目标的情况。与过去十年或更长时间里许多其他攻击一样，Blue
Blue将DLL加载技术用于合法的、签名的应用程序来启动恶意有效负载，报告还记录了该组织利用Microsoft Office中的软件漏洞进行攻击的情况。

### 第二次发现

Abor于2016年4月发布的一份[报告](https://web.archive.org/web/20160618095613/https://www.arbornetworks.com/blog/asert/recent-poison-iv/)详细说明了近十二个月来缅甸和亚洲其他国家遭受恶意软件攻击情况。

他们注意到攻击者利用东盟成员国身份、经济和民主等相关话题的制作钓鱼邮件，dll加载也是此次攻击活动中恶意软件采用的加载方法。

### 第三次发现

Unit 42发表了一项[研究](https://unit42.paloaltonetworks.com/unit-42-attack-delivers-9002-trojan-through-google-drive/)，分析了通过谷歌硬盘传播的9002木马的网络攻击。

下载源于鱼叉式钓鱼邮件，其中包含一个短链接，在下载谷歌硬盘上的ZIP文件之前多次重定向。zip文件包含一个dll加载包，利用合法的播放器来加载9002木马。

### 第四次发现

2017年3月，研究人员发布了一份[报告](https://blog.0day.jp/p/english-report-of-fhappi-freehosting.html)描述了香港网络安全公司VKRL检测到的攻击——通过日本GeurCube公司传播带有恶意URL的鱼叉式钓鱼邮件。恶意网站包含VBScript，从同一站点下载Word文档，以及PuffScript脚本。另外还发现一份针对蒙古的诱饵文件，诱骗目标下载恶意软件并通过Windows来执行恶意载荷。

### 第五次发现

在2018年初，研究人员发现了一个新的Android恶意软件家族，名为“[Hebox](https://unit42.paloaltonetworks.com/unit42-henbox-chickens-come-home-roost/)”，该恶意家族活动可追溯到2015年底，现已经发现了400个样本。

HenBox经常伪装成合法的Android应用程序，其主要目标为Uyghurs，也将中国制造商小米制造的设备设为攻击目标。一旦安装HenBox，恶意软件将从设备上窃取个人信息，收集目标电话号码，访问设备麦克风和相机。

### 第六次发现

根据进一步的调查和围绕Henbox基础结构的分析，研究人员发现了一个以前未知的Windows木马[Farseer](https://unit42.paloaltonetworks.com/farseer-previously-unknown-malware-family-bolsters-the-chinese-armoury/)，Farseer使用DLL加载技术来安装有效载荷。

## 关联分析

通过Maltego图显示了已发现的活动中恶意软件和已知的与pkplug相关的恶意软件样本的关联，随着发现增多图表也在持续增长。图片的索引与上图时间线发现相对应。

![](https://image.3001.net/images/20191007/1570422210_5d9abdc241d1e.jpeg!small)

下图再次显示了六次发现的简化视图，使用了恶意软件精简的基础架构来突出一些核心重叠。

![](https://image.3001.net/images/20191007/1570422623_5d9abf5f9a7a5.jpeg!small)

## 总结

因为没有完全看到黑客组织每一次攻击，无法描述黑客组织攻击的全貌，但可以利用现有相关数据（如网络基础设施、恶意软件行为等）有助于我们更好地了解对手。

根据所收集到的数据可知，PKPACK是一个持续活动的黑客组织，在过去的六年中使用了多个恶意软件家族——Poison Ivy、 PlugX、 and
Zupdax、9002、Hebox和FaSEER。其目标包括东盟国家组织的成员国、中国自治区、中国一带一路倡议有关的国家和地区，以及南海国家和地区。

Playbook
Viewer有助于突出显示的PKPLUG恶意软件的相似之处，该组织倾向于使用鱼叉式钓鱼邮件向受害者发送恶意软件和链接，一些电子邮件附件包含Office漏洞，诱使受害者打开附件。dll加载作为安装或运行其有效负载的方法几乎无处不在。

Android恶意软件的使用表明，PKPLUG的目标可能发生了变化。

 ***本文作者：Kriston，转载请注明来自FreeBuf.COM**

