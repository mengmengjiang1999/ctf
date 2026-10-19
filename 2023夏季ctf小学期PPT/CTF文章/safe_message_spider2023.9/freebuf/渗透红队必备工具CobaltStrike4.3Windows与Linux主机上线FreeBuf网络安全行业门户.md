***本工具仅供技术分享、交流讨论，严禁用于非法用途。**

## 前言

几天前和朋友在泡茶的时候，谈起了渗透工程师的面试，当时HR问他，CS怎么上线Linux呢，这时他反问我，我说我不知道，他在纸上写下CrossC2后，嘴里说着”小菜鸡“，转身离开了。

CrossC2简而言之，就是上线Linux系统的拓展插件

初步搭建服务器及启动CS就跳过了，主要是为了记录自己学习CS的笔记，有哪个地方需要补充的，各位师傅们可以留言。毕竟拿下蓝队才是我们的终极目标。

## 工具下载

CobaltStrike4.3

链接：https://pan.baidu.com/s/1nj8vm6EKqWJ-O_Ah7DAsRw  
提取码：10px

CrossC2  
链接：https://pan.baidu.com/s/1lLARpBSfGA_aUaXnS5kJjA  
提取码：wj7s

## CS功能及模块介绍

### 1.1 **Cobalt Strike 模块**

![1627005470_60fa221eaaaae871991d0.png!small](https://image.3001.net/images/20210723/1627005470_60fa221eaaaae871991d0.png!small)

New Connection：打开一个新的”Connect”窗口。在当前窗口中新建一个连接，即可同时连接不同的团队服务器( 便于团队之间的协作)

Preferences：偏好设置，首选项，用于设置Cobalt Strike主界面、控制台、TeamServer 连接记录、报告的样式

Visualization：将主机以不同的权限展示出来（主要以输出结果的形式展示）

VPN Interfaces：设置VPN接口

Listeners：创建监听器

Script Manager：查看和加载CNA脚本

Close：关闭当前与TeamServer的连接

### 1.2 View模块

![1627005640_60fa22c8a1143500e16ee.png!small?1627005642115](https://image.3001.net/images/20210723/1627005640_60fa22c8a1143500e16ee.png!small?1627005642115)

Applications：显示被控机器的应用信息

Credentials：通过HashDump或mimikatz获取的密码或者散列值都储存在这里

Downloads：从被控机器中下载的文件

Event Log：主机上线记录，以及与团队协作相关的聊天记录和操作记录

Keystrokes：键盘记录

Proxy Pivots：代理模块

Screenshots：屏幕截图模块

Script Console：控制台，在这里可以加载各种脚本（链接）

Targets：显示目标

Web Log：Web 访问日志

### 1.3.1 Attacks
Packages模块![1627006125_60fa24ad75896d390f68e.png!small?1627006126397](https://image.3001.net/images/20210723/1627006125_60fa24ad75896d390f68e.png!small?1627006126397)

HTML
Application：基于HTML应用的Payload模块，通过HTML调用其他语言的应用组件进行攻击测试，提供了可执行文件、PowerShell、
VBA三种方法

MS Office Macro：生成基于Office病毒的Payload 模块

Payload Generator：Payload 生成器，可以生成基于C、C#、COM Scriptlet、 Java、 Perl、
PowerShell、Python、 Ruby、 VBA等的Payload

Windows
Executable:可以生成32位或64位的EXE和基于服务的EXE、DLL等后门程序。在32位的Windows操作系统中无法执行64位的Payload,
而且对于后渗透测试的相关模块，使用32位和64位的Payload会产生不同的影响，因此在使用时应谨慎选择

Windows Executable (S):用于生成一个Windows
可执行文件，其中包含Beacon的完整Payload,不需要阶段性的请求。与Windows
Executable模块相比，该模块额外提供了代理设置，以便在较为苛刻的环境中进行渗透测试。该模块还支持PowerShell脚本，可用于将●Stageless
Payload注入内存

### 1.3.2 Attacks Web Drive-by模块

![1627006578_60fa26729f8a8f2a33087.png!small?1627006579429](https://image.3001.net/images/20210723/1627006578_60fa26729f8a8f2a33087.png!small?1627006579429)

Manage：管理器，用于对TeamServer上已经开启的Web服务进行管理，包括 Listener 及 Web Delivery模块

Clone Site：用于克隆指定网站的样式

Host File：用于将指定文件加载到Web目录中，支持修改Mime Type

Script Web Delivery：基于Web的攻击测试脚本，自动生成可执行的Payload

Signed Applet Attack：使用Java自签名的程序进行钓鱼攻击测试。如果用户有Applet 运行权限，就会执行其中的恶意代码

Smart Applet
Attack：自动检测Java的版本并进行跨平台和跨浏览器的攻击测试。该模块使用嵌入式漏洞来禁用Java的安全沙盒。可利用此漏洞的Java版本为1.6.0_45以下及1.7.0
_21以下

System Profiler：客户端检测工具，可以用来获取一些系统信息，例如系统版本、浏览器版本、Flash版本等

### 1.3.3 Attacks Spear Phish模块

### 1.4 **Reporting模块**

![1627006728_60fa2708931fa3d4b7f6d.png!small?1627006729364](https://image.3001.net/images/20210723/1627006728_60fa2708931fa3d4b7f6d.png!small?1627006729364)

activity report 活动报告生成

Hosts report 主机报告

Indicators opromisef com 目标报告

Sessions report 会话报告

Social engineering report 社会工程学报告

Reset Data 重置数据

Export data 数据出口

### 1.5 Help模块

## 主机上线

### 2.1 打开监听

![1627007191_60fa28d7317395a06b520.png!small?1627007191942](https://image.3001.net/images/20210723/1627007191_60fa28d7317395a06b520.png!small?1627007191942)

![1627007530_60fa2a2a749a211fd285d.png!small?1627007531228](https://image.3001.net/images/20210723/1627007530_60fa2a2a749a211fd285d.png!small?1627007531228)

![1627007591_60fa2a6736ffbbaed824f.png!small?1627007591954](https://image.3001.net/images/20210723/1627007591_60fa2a6736ffbbaed824f.png!small?1627007591954)Payload

Beacon DNS（以DNS协议流量建立Beacon连接）

![1627262659_60fe0ec30137bd0b8a194.png!small?1627262659534](https://image.3001.net/images/20210726/1627262659_60fe0ec30137bd0b8a194.png!small?1627262659534)

DNS Hosts：Beacon回连的主机，可以添加多个

Host Rotation Strategy：Beacon回连主机策略

HTTP Host (Stager)：配置Stager主机，仅当Payload明确需要Stager配合时有效

Profile：Malleable C2配置文件，用于自定义通信流量特征

DNS Port (Bind)：绑定监听端口，实现端口重定向

DNS Resolver：指定NS服务器

Beacon HTTP（以HTTP协议流量建立Beacon连接）

Beacon HTTPS（以HTTPS协议流量建立Beacon连接）

![1627262770_60fe0f320ce7ccd88ad99.png!small?1627262770652](https://image.3001.net/images/20210726/1627262770_60fe0f320ce7ccd88ad99.png!small?1627262770652)

HTTPS Hosts：Beacon回连的主机，可以添加多个

Host Rotation Strategy：Beacon回连主机策略

HTTPS Host (Stager)：配置Stager主机，仅当Payload明确需要Stager配合时有效

Profile：Malleable C2配置文件，用于自定义通信流量特征

HTTPS Port (C2)：Beacon回连的监听端口

HTTPS Port (Bind)：绑定监听端口，实现端口重定向

HTTPS Host Header：设置内层真实域名，在使用域前置技术时使用

HTTPS Proxy：为Payload指定代理

Beacon SMB（以SMB协议流量建立Beacon连接）

![1627262912_60fe0fc059cc34f1a7def.png!small?1627262912886](https://image.3001.net/images/20210726/1627262912_60fe0fc059cc34f1a7def.png!small?1627262912886)

使用命名管道通过父级Beacon进行通讯，当两个Beacon连接后，子Beacon从父Beacon获取任务执行，两者使用Windows命名管道通信，流量封装在SMB协议中，较为隐蔽

Beacon TCP（以TCP协议流量建立Beacon连接）

![1627263053_60fe104d86b04493621b2.png!small?1627263054041](https://image.3001.net/images/20210726/1627263053_60fe104d86b04493621b2.png!small?1627263054041)

External C2

External C2是一种通信规范

Foreign HTTP（以HTTP协议流量建立会话，适用于与外部程序联动）

Foreign
HTTPS（以HTTPS协议流量建立会话，适用于与外部程序联动）![1627263335_60fe1167d7de75d8b41c2.png!small?1627263336398](https://image.3001.net/images/20210726/1627263335_60fe1167d7de75d8b41c2.png!small?1627263336398)成功开启监听，接下来就是让主机上线

### 2.2 Windows主机上线

No.1

![1627263929_60fe13b9622588c6877e1.png!small?1627263930002](https://image.3001.net/images/20210726/1627263929_60fe13b9622588c6877e1.png!small?1627263930002)![1627264016_60fe1410cac962e56cb96.png!small?1627264017348](https://image.3001.net/images/20210726/1627264016_60fe1410cac962e56cb96.png!small?1627264017348)![1627264160_60fe14a08ef64918bcb95.png!small?1627264161110](https://image.3001.net/images/20210726/1627264160_60fe14a08ef64918bcb95.png!small?1627264161110)![1627264334_60fe154edd620386f9509.png!small?1627264335382](https://image.3001.net/images/20210726/1627264334_60fe154edd620386f9509.png!small?1627264335382)![1627264235_60fe14eb12ca8000e3135.png!small?1627264235632](https://image.3001.net/images/20210726/1627264235_60fe14eb12ca8000e3135.png!small?1627264235632)

No.2

![1627264553_60fe162933a84618eb8e8.png!small?1627264553892](https://image.3001.net/images/20210726/1627264553_60fe162933a84618eb8e8.png!small?1627264553892)![1627264577_60fe16419631859d9cbf3.png!small?1627264578100](https://image.3001.net/images/20210726/1627264577_60fe16419631859d9cbf3.png!small?1627264578100)![1627264585_60fe1649868028439b4ba.png!small?1627264586008](https://image.3001.net/images/20210726/1627264585_60fe1649868028439b4ba.png!small?1627264586008)![1627264601_60fe1659be89c9061ea26.png!small?1627264602258](https://image.3001.net/images/20210726/1627264601_60fe1659be89c9061ea26.png!small?1627264602258)![1627352751_60ff6eaf0ee0e485a2662.png!small?1627352750678](https://image.3001.net/images/20210727/1627352751_60ff6eaf0ee0e485a2662.png!small?1627352750678)![1627352761_60ff6eb9b0c8b3e52e83f.png!small?1627352761577](https://image.3001.net/images/20210727/1627352761_60ff6eb9b0c8b3e52e83f.png!small?1627352761577)Emmm，作者这个无法实现上线，具体思路是这样的

保存成一个带宏模板的办公文件，当受害人点击使用宏模板时，主机上线

大家可以试一试

No.3

![1627352837_60ff6f050d49f2e062515.png!small?1627352836742](https://image.3001.net/images/20210727/1627352837_60ff6f050d49f2e062515.png!small?1627352836742)![1627352906_60ff6f4ad02b1b0833ab1.png!small?1627352906457](https://image.3001.net/images/20210727/1627352906_60ff6f4ad02b1b0833ab1.png!small?1627352906457)这边举个栗子就好了，Powershell
Command
，会生成一个文件，保存下来，用powershell执行，这边的原理大致就是生成可执行木马文件，执行后，主机上线，但是只能上线Windows主机![1627353208_60ff7078214e2764939c8.png!small?1627353207771](https://image.3001.net/images/20210727/1627353208_60ff7078214e2764939c8.png!small?1627353207771)![1627353250_60ff70a2082dfedb1a002.png!small?1627353249886](https://image.3001.net/images/20210727/1627353250_60ff70a2082dfedb1a002.png!small?1627353249886)![1627353268_60ff70b4958e387c4f427.png!small?1627353272070](https://image.3001.net/images/20210727/1627353268_60ff70b4958e387c4f427.png!small?1627353272070)

No.4 Windows Executable 和 Windows Executable（S）用法相同  
![1627354771_60ff7693af23709817ab6.png!small?1627354771360](https://image.3001.net/images/20210727/1627354771_60ff7693af23709817ab6.png!small?1627354771360)![1627354785_60ff76a1556068c53bc4e.png!small?1627354784930](https://image.3001.net/images/20210727/1627354785_60ff76a1556068c53bc4e.png!small?1627354784930)![1627354793_60ff76a981e10b41d4d3e.png!small?1627354794729](https://image.3001.net/images/20210727/1627354793_60ff76a981e10b41d4d3e.png!small?1627354794729)![1627354809_60ff76b9835e96a51a02b.png!small?1627354812399](https://image.3001.net/images/20210727/1627354809_60ff76b9835e96a51a02b.png!small?1627354812399)

No.5

![1627442669_6100cdeddb11b30f39e17.png!small?1627442669073](https://image.3001.net/images/20210728/1627442669_6100cdeddb11b30f39e17.png!small?1627442669073)

生成一个Url，访问这个网站去下载，使被攻击机成功上线，目前也未能复现

No.6

![1627441852_6100cabc692e74cf68561.png!small?1627441851734](https://image.3001.net/images/20210728/1627441852_6100cabc692e74cf68561.png!small?1627441851734)![1627441899_6100caeb0b453cb8cd308.png!small?1627441898263](https://image.3001.net/images/20210728/1627441899_6100caeb0b453cb8cd308.png!small?1627441898263)

这儿的Type 类型
选择哪个都是没问题的，主要看是系统能不能执行，大致的意思就是生成一个Url，让受害者去带上7788的参数去访问这个Url，使被攻击机上线  
![1627441976_6100cb387d7b75198a8b2.png!small?1627441975767](https://image.3001.net/images/20210728/1627441976_6100cb387d7b75198a8b2.png!small?1627441975767)![1627441995_6100cb4bf3226bac6c50c.png!small?1627441995344](https://image.3001.net/images/20210728/1627441995_6100cb4bf3226bac6c50c.png!small?1627441995344)![1627442010_6100cb5a1a35755e09d47.png!small?1627442009426](https://image.3001.net/images/20210728/1627442010_6100cb5a1a35755e09d47.png!small?1627442009426)

还有其他上线的方法，可以告知一下，互相学习

### 2.3 Linux主机上线

要先安装CrossC2，具体得跳过了

设置一个监听端口，CrossC2目前只支持Beacon HTTPS

![1627542846_6102553e25b0f0669fc67.png!small?1627542845848](https://image.3001.net/images/20210729/1627542846_6102553e25b0f0669fc67.png!small?1627542845848)

![1627542916_61025584d87bfa6e60f57.png!small?1627542916618](https://image.3001.net/images/20210729/1627542916_61025584d87bfa6e60f57.png!small?1627542916618)

设置监听和Linux/Mac的型号x86/x64就Ok了![1627542938_6102559a705538f22175c.png!small?1627542938138](https://image.3001.net/images/20210729/1627542938_6102559a705538f22175c.png!small?1627542938138)

点击Build 就会生成这么个命令，把这个命令复制到要上线的Linux主机上  
![1627543020_610255ec5a8a20e61e761.png!small?1627543020058](https://image.3001.net/images/20210729/1627543020_610255ec5a8a20e61e761.png!small?1627543020058)

![1627543088_61025630ce24b0bb0340d.png!small?1627543088566](https://image.3001.net/images/20210729/1627543088_61025630ce24b0bb0340d.png!small?1627543088566)![1627543101_6102563d8bc14cc91f348.png!small?1627543101325](https://image.3001.net/images/20210729/1627543101_6102563d8bc14cc91f348.png!small?1627543101325)成功上线

网上还有个是利用命令

> ./genCrossC2.Linux 10.6.6.25（监听IP） 443（监听端口） null null Linux（Linux/Mac）
> x86（x86/x32） test

大家可以试试

## 结语

CS主机上线是后面进一步的基操，没有上线啥都免谈。

老生常谈的，各位师傅切勿进行无授权渗透

