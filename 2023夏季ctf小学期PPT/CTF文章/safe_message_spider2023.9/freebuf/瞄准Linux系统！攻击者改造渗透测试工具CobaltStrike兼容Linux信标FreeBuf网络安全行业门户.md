9月13日，安全研究人员发现了一个由未知黑客组织制作的Cobalt Strike Beacon Linux版本，以在全球范围内扩大目标攻击。
**这些攻击针对的是电信公司、政府机构、IT公司、金融机构和咨询公司。**

代号为Vermilion的威胁行为者修改了Cobalt Strike的一个版本 ，Cobalt Strike是一种合法的渗透测试工具，被用作红队的攻击框架。

Cobalt
Strike还被威胁行为者(通常在勒索软件攻击中删除)用于部署所谓的信标后的后利用任务，这些信标提供对受感染设备的持久远程访问。使用信标，攻击者可以晚些访问被破坏的服务器以收集数据或部署更多的恶意软件负载。

虽然开发该工具是为了帮助安全公司进行渗透测试，模拟威胁参与者使用的技术， **但该工具的高级功能也使其成为网络犯罪组织的最爱。**

随着时间的推移，Cobalt Strike的破解副本已被威胁行为者获取并共享，成为数据盗窃和勒索软件的网络攻击中最常用的工具之一。但 **此前Cobalt
Strike 一直有一个弱点，它只支持Windows设备，不包括Linux信标。**

## Cobalt Strike Beacon移植到Linux

在安全公司Intezer的一份新报告中，研究人员解释了 **威胁行为者如何自行创建与 Cobalt Strike兼容的Linux信标。**
使用这些信标，攻击者现在可以在Windows和Linux机器上获得持久性和远程命令执行。

研究人员表示，为了避免恶意软件被检测到，Vermilion组织开发了Vermilion Strike，这是Cobalt Strike
Beacon后门的独一无二的Linux版本。此外，该组织还重新编写了Beacon后门的原始Windows 版本，目前完全未被杀毒软件检测到。

Vermilion Strike带有与官方Windows 信标相同的配置格式，可以与所有Cobalt Strike 服务器对话，但不使用任何Cobalt
Strike的代码。

这种新的Linux恶意软件还具有技术上的重叠(相同的功能和命令和控制服务器)，Windows DLL文件提示同一个开发人员。

![](https://image.3001.net/images/20210915/1631673657_61415d3910b5dfb6c3657.png!small)

Intezer说:“隐形样本在与C2服务器通信时使用了Cobalt
Strike的命令和控制(C2)协议，并具有远程访问功能，如上传文件、运行shell命令和写入文件。”

在发文时，病毒查杀工具中完全没有检测到该恶意软件，该恶意软件是从马来西亚上传的。

Vermilion Strike一旦部署在受感染的Linux系统上就可以执行以下任务：

> 更改工作目录
>
> 获取当前工作目录
>
> 附加/写入文件
>
> 上传文件到C2
>
> 通过 popen 执行命令
>
> 获取磁盘分区
>
> 列出文件

## 自8月以来部署在持续攻击中

通过数据监测，Intezer还发现自2021年8月以来，来自全球电信公司和政府机构、IT
公司、金融机构和咨询公司等各个行业的多个组织成为使用Vermilion Strike目标。

还值得一提的是，Vermilion Strike并不是唯一一个将Cobalt
Strike的Beacon移植到Linux的端口，它使用了geacon，一个基于go的开源实现，在过去的两年中已经公开。

然而， **这是第一个用于真正攻击的Linux实现。**
目前没有关于攻击者用来针对Linux系统的初始攻击向量的信息。但通过对其复杂性和活动意图以及该代码从未在其他攻击中出现这些情况进行分析，这种恶意软件是由熟练的威胁行为者开发的。

通过对勒索事件的分析可以发现，这些勒索软件不但一直在更新技术能力，而且对实体造成的破坏严重超出公众认知，每个行业对于勒索软件攻击都不应存在侥幸心理。

 **参读链接：**

>
> [https://www.bleepingcomputer.com/](https://www.bleepingcomputer.com/news/security/hacker-> made-linux-cobalt-strike-beacon-used-in-ongoing-attacks/)
>
> [https://therecord](https://therecord.media/threat-actor-ports-cobalt-> strike-beacon-to-linux-uses-it-in-> attacks/?__cf_chl_jschl_tk__=pmd_DDUNpqFPzYr3jdnyVn5Z8n54_bHvVSF7mf6wt38wm04-1631591457-0-gqNtZGzNAmWjcnBszQy9)

