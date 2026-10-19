#### 0x01、 简述

Metasploit
Framework(MSF)是一款开源安全漏洞检测工具，他带有数千个已知的软件漏洞，目前人在持续更新。Metasploit可以用来信息收集、漏洞探测、漏洞利用等渗透测试的全流程，被安全社区冠以“可以黑掉整个宇宙”之名。在普通的Linux系统下需要自行下载安装，而Kali中自带此工具，在此工具中，msfconsole是整个框架中最受欢迎的模块，当然也是最强大的一个模块，接下来我们会详细讲解此模块。

![](https://image.3001.net/images/20230727/1690466215_64c277a78018e55a69ad2.png!small)

#### 0x02、msfconsole攻击模块

![](https://image.3001.net/images/20230727/1690466216_64c277a854cd847c77b03.png!small)

使用命令show exploits：列出metasploit框架中的所有EXP：

![](https://image.3001.net/images/20230727/1690466217_64c277a9342217b15e59e.png!small)

可以看到目前有2043个各种漏洞EXP，我们可以选择其中一个使用，当然也可以根据漏洞编号去查找。

#### 0x03、CVE-2010-3333 EXP查找使用

search cve-2010-3333：

![](https://image.3001.net/images/20230727/1690466218_64c277aa7bb36eb19db9a.png!small)

可以看到这里只有一条EXP，use 0使用此条，再通过show options查看配置：

![](https://image.3001.net/images/20230727/1690466219_64c277ab3a6ae9a32bbfd.png!small)

可以使用set 参数名 参数值 进行修改配置信息：

![](https://image.3001.net/images/20230727/1690466219_64c277abe2804c3d4a2e3.png!small)![](https://image.3001.net/images/20230727/1690466220_64c277acd596924589c79.png!small)

通过show targets查看漏洞目标：

![](https://image.3001.net/images/20230727/1690466221_64c277adc8c71d012e330.png!small)

在这里选择相应软件版本系统版本的EXP，进行选择，比如这里使用 Office2002 WinXP SP3这条，set target 1：

![](https://image.3001.net/images/20230727/1690466222_64c277ae7ffed754284f3.png!small)

最后下载：

![](https://image.3001.net/images/20230727/1690466223_64c277af85b8f90b62a6f.png!small)

这里就完成了一次漏洞EXP的下载，通过修改相应参数可以直接使用。

#### 0x04、msfconsole常用命令

• show exploit 列出metasploit框架中的所有渗透攻击模块。

• show payloads列出metasploit框架中的所有攻击载荷。

• show auxiliary列出metasploit框架中的所有辅助攻击载荷。

• search name查找metasploit框架中所有的渗透攻击和其他模块。

• info展示出制定渗透攻击或模块的相关信息。

• use name装载一个渗透攻击或模块。

• LHOST本地主机。

• RHOST远程主机或是目标主机。

• set function设置特定的配置参数。

• setg function以全局方式设置特定的配置参数（EG：设置本地或远程主机参数）。

• show options列出某个渗透攻击或模块中所有的配置参数。

• show targets列出渗透攻击所有支持的目标平台。

• set target num指定你所知道的目标的操作系统以及补丁版本类型。

• set payload name指定想要使用的攻击载荷。

• show advanced列出所有高级配置选项。

• check检测目标是否选定渗透攻击存在相应的安全漏洞。

• exploit执行渗透攻击或模块来攻击目标。

• exploit -j在计划任务下进行渗透攻击（攻击将在后台进行）。

• exploit -z渗透攻击完成后不与回话进行交互

#### 0x05、结束语

当然Metasploit Framework远不止这点操作，他还有很多其他实用强大的手段，后续会展示其他手段，Metasploit
Framework可谓黑客必备利器！

