**译者：知道创宇404实验室翻译组  
原文链接：<https://intel471.com/blog/privateloader-malware>**

长久以来，安装付费(PPI)恶意软件服务已经成为网络犯罪生态系统不可分割的一部分。恶意软件运营者提供支付、恶意有效载荷和目标信息，负责运行服务的人把分发和传播部分外包出去。可访问性和合适的成本使得恶意软件运营商可以利用这些服务作为一种武器，用于快速、批量和地理定位的恶意软件感染。

通过了解这些服务是如何扩散的，防御者可以更好地识别这些活动，并阻止它们对组织的 IT 堆栈造成严重破坏。本报告重点介绍了 PrivateLoader
模块化下载程序，该下载程序由 C++程式语言编写，连接到一个未经确认的 PPI 服务。PrivateLoader
位于此操作的前端，并与其后端基础设施通信，以检索 url，从而将恶意有效负载“安装”到受感染的主机上。正如与 PPI
服务绑定的下载一样，PrivateLoader 传送了各种数据，比如哪些有效载荷被下载并成功启动。

分发活动通常依靠搜索引擎优化(SEO)增强的网站网络，吸引毫无防备的搜索盗版软件的受害者下载并执行恶意软件。它通常会发送一个密码保护的存档，其中包含一个安装文件，该文件在受感染的主机上嵌入并执行多个恶意有效负载，如GCleaner、PrivateLoader、Raccoon、Redline、Smokeloader和Vidar恶意软件。我们估计，这些攻击活动从2021年5月起开始纳入PrivateLoader。

本报告调查了其背后的 PPI 服务和运营商使用的获取“安装”的方法，并提供了服务提供的恶意软件组的详细信息。

### PrivateLoader 运作原理

这个 PrivateLoader PPI 活动背后的服务及其运营商尚不清楚，因为在本报告发布时，将下载程序与特定的地下 PPI
服务联系起来并不容易。然而，我们观察到 PrivateLoader 的主命令和控制(C2)服务器也承载了基于 AdminLTE
3仪表板模板的管理面板。下面的图片显示了认证页面:

![](https://images.seebug.org/content/images/2022/02/66ddef65-ac95-4ed4-85cd-67e18d65f4fd.webp-w331s)
图1: 这张图片描述了 PrivateLoader 认证页面

使用 Javascript 库 app.js 的前端脚本似乎公开了提供给面板用户的功能。下面的表格描述了脚本中有趣的 JavaScript 函数:

![](https://images.seebug.org/content/images/2022/02/abbab92f-45e9-48a8-8669-43ddaa546b23.png-w331s)

### 传送 PrivateLoader 下载程序

PrivateLoader 是通过一个网络传送的，这些网站声称提供“破解”软件，也就是人们常用的流行合法应用程序的破解版本。这些网站经过 SEO
优化，通常出现在搜索查询的顶部，包含关键字，如“破解”或“破解下载”，前面是软件名称。

例如，搜索“ Malwarebytes crack”会出现以下网站，位列第四和第五个结果:

![](https://images.seebug.org/content/images/2022/02/a48cf60c-771a-4658-9d73-865e194de1b7.png-w331s)
“ Malwarebytes crack”搜索结果

访问者被引导点击“下载破解”或“立即下载”按钮，以获得据称已破解的软件版本。下载按钮的 JavaScript 是从远程服务器检索的。

![](https://images.seebug.org/content/images/2022/02/cecbbb67-52ba-41c4-b4e7-024b63abba71.png-w331s)
一个据称可以下载破解版软件的选项

经过几次重定向之后，最终的有效负载作为密码保护的压缩文件(.Zip)存档。下面的截图是实际的下载页面:

![](https://images.seebug.org/content/images/2022/02/1bba103f-2fbb-4b81-ba48-a04a0e06e628.png-w331s)
下载页面

在我们的示例中，归档文件名为“PASSWORD_IS_324325____Malwarebytes-Pr.zip.”它包含一个名为“
setup_x86_x64_install.exe”的Nullsoft脚本安装系统，该安装程序嵌入并执行大量恶意有效负载，如 GCleaner、
PrivateLoader 和 Redline。

SophosLabs 的研究人员之前调查了这个传输网络，并将其中的一些基础设施与 InstallUSD PPI 服务关联起来。

### 恶意软件组

针对 PrivateLoader 的自动恶意软件覆盖和跟踪始于2021年9月初。从那以后，我们收集了大量的数据，帮助我们更多地了解了这项服务。

下面的图表显示了我们的恶意软件情报系统检测到的PrivateLoader为每个恶意软件下载的唯一散列数量。这项 PPI 服务最多的恶意软件是
Smokeloader、 Redline 和 Vidar:

![](https://images.seebug.org/content/images/2022/02/b6b2c72a-64ee-41fa-9112-f36dec26aa49.png-w331s)
恶意软件情报系统检测到的每个恶意软件家族的 PrivateLoader 下载的唯一散列数量

每个 PrivateLoader 示例嵌入一个区域代码，该区域代码与自动程序的
c2服务器和国家进行通信。下面的图表显示了在覆盖期间每个区域代码下载的唯一散列数。我们认为，这些区域代码中的“
WW”前缀代表“世界范围”，因为它于样本中经常出现。在面板方面，我们怀疑这段代码代表了前面表中描述的“link_geo”参数。

![](https://images.seebug.org/content/images/2022/02/60ee5c03-0545-4f7e-b65f-7058f7209eca.png-w331s)
每个区域代码下载的唯一散列数

然而，当我们通过自动程序的国家代码查询唯一散列的数量时，我们观察到了一个与上图不同的分布(见下图)。这不难猜到，因为流行的世界各地的区域代码封装多个国家。

![](https://images.seebug.org/content/images/2022/02/6657a9eb-8f30-43e1-8473-89ad81e6a13c.png-w331s)
每个国家代码下载的唯一散列数

### Smokeloader

在我们看到的由 PrivateLoader 推动的有效载荷中，最常见的是 Smokeloader。下面的图表显示了从我们的恶意软件情报系统检测到的所有单独的
Smokeloader 样本中提取的附属 id (或缺少的) :

![](https://images.seebug.org/content/images/2022/02/dbcc743c-c410-41fe-ac89-47d67337b2cc.png-w331s) 我们检测到的Smokeloader 样本中提取的附属 id 的百分比

排名前10的用于传输 Smokeloader 的域名包括:

HOST NAME | UNIQUE SAMPLES DOWNLOADED  
---|---  
privacytoolz123foryou[.]top | 321  
threesmallhills[.]com | 296  
privacy-toolz-for-you-5000[.]top | 264  
privacytoolzforyou-7000[.]top | 231  
privacytoolzforyou-7000[.]com | 212  
privacytoolzforyou7000[.]top | 200  
privacytoolzforyou-6000[.]top | 179  
privacy-toolz-for-you-403[.]top | 177  
privacy-tools-for-you-777[.]com | 150  
privacytoolzforyou6000[.]top | 136  
  
很明显，运行“隐私工具”域名的运营商严重依赖 PrivateLoader 提供
Smokeloader。对活动分发网址的检查显示，这些域名拥有一个声称提供“隐私工具”的网站。这个网站很可能是在仿冒真正的PrivacyTools[.]io网站，而这个网站是由提倡数据隐私的志愿者运营的。

![](https://images.seebug.org/content/images/2022/02/9edffad6-a643-42f3-bc9f-29af337095e4.png-w331s)
一个“Privacy tools”域的登陆页

这些网站将 Smokeloader 有效载荷分为“ pab1”、“ pab2”和“ pab3”三类。这些并不一定与类似的“pub * ”附属ID
相关联，因为我们已经看到一些“ pab2”有效负载具有“555”附属ID。在跟踪 PrivateLoader 时，我们只收到从这些网站下载“
pab2”有效载荷的链接。这些运营商很可能使用其他方法或 PPI 服务来分发 Smokeloader。

2021年10月22日，PrivateLoader从其中一个网站下载的Smokeloader样本提供了Qbot银行木马。这是一个Qbot的不寻常的分发方法为，揭示了新的僵尸网络
ID star01。

### 银行木马

整个地下组织中还有其他人利用 PrivateLoader 进行银行木马分发。

2021年10月31日，欧洲国家的 PrivateLoader 机器人被要求从以下网址下载并执行 Kronos 木马:

`xxp://2.56.59[.]42/EU/Yandex1500[.]exe`

下载的示例还执行了 Vidar 信息窃取器。此示例的下载和执行命令在第二天停止。

2021年11月1日，PrivateLoader 自动程序下载了与10444僵尸网络相关的 Dridex 样本，而 Danabot
的附属标识是40。同一天，自动程序还下载了带有组标签 lip * 、 tot * 和 top * 的 Trickbot
样本。在所有情况里，这些样本都嵌入了其他恶意软件，如其他银行木马、信息窃取器或勒索软件。

样本 HASH | 恶意软件组 | 首次出现(UTC) | 最后出现(UTC) | 其他被发现的恶意软件组  
---|---|---|---|---  
14e7cc2eadc7c9bac1930f37e25303212c8974674b21ed052a483727836a5e43 | Trickbot:
top142 | 2021-11-01 17:19:30 | 2021-11-01 18:39:25 |
Nanocore，RAT，Smokeloader，Redline  
4554dc95f99d6682595812b677fb131a7e7c51a71daf461a57a57a0d903bb3fa | Trickbot:
tot160 160Trickbot: top141 Dridex: 10444 | 2021-11-01 11:20:11 | 2021-11-02
07:17:40 | Tofsee，Redline  
4ed7609cbb86ea0b7607b8a002e7f85b316903c3b6801240c9576aae8b3052ff | Trickbot:
lip143 Trickbot: top142 | 2021-11-01 17:27:39 | 2021-11-02 07:46:21 |
njRAT，STOP Djvu，Redline，Vidar  
5adbe8d0375d6531f1a523085f4df4151ad1bd7ae539692e2caa3d0d73301293 | Trickbot:
lip142 Dridex: 10444 | 2021-11-01 15:56:02 | 2021-11-02 02:03:00 2:03:00 |
Remcos，Tofsee  
6abbd89e6ab5e1b63c38a8f78271a97d19bafff4959ea9d5bd5da3b185eb61e6 | Trickbot:
top141 | 2021-11-01 12:51:32 | 2021-11-02 02:02:59 | Redline  
929a591331bdc1972357059d451a651d575166f676ea51daaeb358aa2a1064b7 | Dridex:
10444 | 2021-11-01 17:29:03 | 2021-11-01 18:41:08 | Smokeloader，Redline  
aae0553b761e8bb3e58902a46cd98ee68310252734d1f8d9fd3b862aab8ed5c9 | Trickbot:
lip142 | 2021-11-01 16:14:42 | 2021-11-02 16:54:50 | Redline  
bf7b5f72b2055cfc8da01bb48cf5ae8e45e523860e0b23a65b9f14dbdbb7f4ee | Trickbot:
lip141 Trickbot: top141 Trickbot: top142 Dridex: 10444 Danabot: affid 40 |
2021-11-01 11:14:58 | 2021-11-01 18:41:14 | Redline，QuasarRAT  
eef15f6416f756693cbfbfd8650ccb665771b54b4cc31cb09aeea0d13ec640cf | Trickbot:
lip141 Trickbot: lip142 Trickbot: lip143 Trickbot: top141 | 2021-11-01
15:01:07 | 2021-11-02 02:03:33 | Smokeloader，Lockbit，Redline  
f9246be51464e71ff6b37975cd44359e8576f2bf03cb4028e536d7cfde3508fc | Trickbot:
lip141 Trickbot: lip142 | 2021-11-01 15:09:14 | 2021-11-02 07:17:30 | Redline  
fcc49c9be5591f241ffd98db0752cb9e20a97e881969537fba5c513adbd72814 | Trickbot:
lip142 Dridex: 10444 | 2021-11-01 17:27:43 | 2021-11-01 18:41:04 | Redline  
  
具有
hash`929a591331bdc1972357059d451a651d575166f676ea51daaeb358aa2a1064b7`的样本从以下
URL 下载:

    
    
    hxxp://privacytoolzfor-you6000[.]top/downloads/toolspab2.exe

在前面的小节中，我们将“隐私工具”网站和Smokeloader 操作者关联起来。目前尚不清楚这些网站背后的操作者是否操作了 Dridex
10444僵尸网络，或者只是作为传递链中的一环。不过，我们可以假设“隐私工具”网站是参与分发环节，因为在这段时间内，在不同的Hash和发送网址中可以看到同一个
Dridex 僵尸网络标识符和控制器。

这是第一次看到 Danabot、 Dridex、 Kronos 和 Trickbot
在同一时间段内下载，很难说是巧合。此外，这些木马经常被同时出现。因此，我们猜测，当时有一个单独的实体可能正在使用 PrivateLoader PPI
服务来操作这些僵尸网络。

在2021年11月14日，PrivateLoader 自动程序开始下载 Danabot的样本，并附带 ID 4，持续一天。

基于这些持续时间不超过一天的短暂爆发，我们怀疑银行木马操作者在试验这种 PPI 服务，检测作为他们恶意软件的另一种传递机制的可能性。

### 勒索软件

地下PPI服务通常建议不要在目标机器上部署勒索软件，因为这会使机器无法使用。然而，网络犯罪分子向来不遵守规则，爱部署勒索软件。

我们唯一一次检测到 PrivateLoader 下载的勒索软件样本是在2021年11月初，当时 PrivateLoader
植入了银行木马。上一小节中的表格显示了 LockBit 和 STOP Djvu 勒索软件组的下载。

在分析 PrivateLoader 下载的有效载荷时，我们识别出了一个新的装载器，我们称之为“Discoloader”。Discoloader使用 .NET
框架，并使用 Discord 内容传递网路(CDN)托管其有效负载。虽然不是直接来自 PrivateLoader，但我们观察到这个恶意软件组的样本直接将
Conti 勒索软件植入受感染的主机，这是一种非典型的传输机制，因为这个软件组通常只是在企业网络完全破坏后才部署。

### 总结

PPI服务几十年来一直是网络犯罪的支柱。就像普罗大众争取好处一样，犯罪分子将会涌向那些为他们提供了一系列的选择的软件，可以很容易地实现他们的目标。正如我们所详述的，犯罪分子已经使用
PrivateLoader 发起了各种各样的计划。通过强调这种恶意软件的多功能性，我们希望帮助防御者来开展独特的策略来阻止 PrivateLoader
授权的恶意软件攻击。

### MITRE ATT&CK 技术

本报告采用了 MITRE 对抗性战术、技术和常识(ATT&CK)框架。

**技术** | **ID** | **使用**  
---|---|---  
|  |  
**Resource Development [TA0042]** |  |  
stage 能力: 上传恶意软件 | T1608.001 | PrivateLoader 经常在 Discord CDN
上托管恶意的有效载荷。我们发现最近的控制器只从 ID
891006172130345095、905701898806493199和896617596772839426下载附件。  
|  |  
**Persistence [TA0003]** |  |  
创建或修改系统进程: Windows 服务 | T1543.003 | PrivateLoader可以作为启动服务持久化，并安装以下属性: ♦服务名称:
PowerControl ♦服务显示名称: “设备的电源监视服务”♦服务启动类型: 在系统启动时 ♦服务二进制路径: C:\Program Files
(x86)\PowerControl\PowerControl_Svc.exe.  
计划任务/工作: 计划任务 | T1053.005 | PrivateLoader 服务模块始终作为计划任务持续存在，每小时执行一次。当不使用
Windows 服务时，还可以将其持久化为登录计划任务  
浏览器扩展 | T1176 | PrivateLoader可以在 Google Chrome 和微软 Edge 浏览器上下载并安装恶意扩展。  
|  |  
**权限提升 [TA0004]** |  |  
滥用提升控制机制: 绕过用户帐户控制 | T1548.002 | PrivateLoader 核心模块使用 Windows
10用户帐户控制(UAC)绕过技术来提升权限。这种绕过使用了一种被多次记录的技术，涉及到 ComputerDefaults.exe
系统可执行(.exe)文件，其中有自动提升选项设置  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1829/>

