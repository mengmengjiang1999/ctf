**研究人员发现勒索软件Snatch可使Windows重新启动到安全模式来绕过安全保护。**

10月中旬，研究人员发现名为Snatch的勒索软件将自身设置为一个服务，并在安全模式引导期间运行。它可以快速地将计算机重新启动到安全模式，并在大多数软件（包括安全软件）不运行的安全模式环境中加密受害者的硬盘驱动器。

![](https://image.3001.net/images/20191212/1576121170_5df1b3523de2b.jpg!small)

 ** _点击图片查看原图_**

Snatch勒索软件自2018年夏天以来一直很活跃，该恶意软件的安全模式启动是一个新增加的功能。恶意软件包括一个勒索软件组件和一个单独的数据窃取器，这两个工具显然都是由网络罪犯开发的，此外还有几个公开的工具，这些工具本身并不是恶意的，通常被渗透测试人员、系统管理员或技术人员使用。Snatch勒索软件不支持多平台，该软件可以运行在最常见的Windows版本上，从7到10，32位和64位版本。发现的样本是使用开源打包程序UPX打包，进行了内容混淆。

  

## Snatch工作方式

恶意软件采用主动自动攻击模式，他们通过对易存在漏洞的服务进行自动暴力攻击来渗透企业网络，并在目标组织的网络内部进行传播。恶意软件在勒索的同时能够一直从目标组织窃取大量信息。

Snatch小组成员曾经在线进行技术讨论与寻找合作伙伴，并免费培训其他人使用恶意软件，允许潜在伙伴使用其基础设施，提供运行Metasploit的服务器。

![1.PNG](https://image.3001.net/images/20191212/1576118573_5df1a92db8cfb.png!small)![1.PNG](https://image.3001.net/images/20191212/1576118613_5df1a9550e66d.png!small)

## Snatch行为分析

在其中一起针对一家大型国际公司的攻击事件中，MTR设法从目标公司获得勒索软件无法加密的详细日志。攻击者最初通过强行将密码强制输入到Microsoft
Azure服务器上的管理员帐户来访问公司的内部网络，并能够使用远程桌面（RDP）登录到服务器。

攻击者使用Azure服务器作为渗透立足点，利用该管理员帐户登录到同一网络上的域控DC，然后在数周内对目标网络执行监视任务。查询有权登录的用户列表，并将结果写入文件。此外还将WMIC系统用户数据、进程列表，Windows
LSASS服务的内存内容存储到文件中，然后上传到c2服务器。

![1.PNG](https://image.3001.net/images/20191212/1576118650_5df1a97abb8fa.png!small)

 **User information stolen by Snatch**

![1.PNG](https://image.3001.net/images/20191212/1576118715_5df1a9bb6800f.png!small)
**Snatch dumps lsass from memory then uploads the dump**

攻击者设置了一次性Windows服务来部署特定任务。这些服务有很长的随机文件名，可从tasklist程序查询正在运行的进程的列表，将其输出到temp目录中的一个文件，然后运行一个批处理文件（也位于temp目录中），将tasklist文件上传到C2服务器。

![1.PNG](https://image.3001.net/images/20191212/1576118868_5df1aa54504bb.png!small)

它使用同样的方法将大量信息上传到C2服务器。例如，它使用此命令把提取的用户帐户和其他配置文件信息（.txt文件）发送回C2，然后执行它在Windows临时目录中创建的批处理。

![1.PNG](https://image.3001.net/images/20191212/1576118891_5df1aa6b6b06f.png!small)

攻击者在大约200台计算机上安装了监视软件，占组织内部计算机数量的5%。攻击者安装了几个恶意文件；其中一组文件是为了让攻击者能够远程访问这些计算机，而不必依赖Azure服务器。攻击者还安装了一个名为“高级端口扫描程序”的Windows程序，使用该工具在网络上发现他们其他潜在目标计算机。

![1.PNG](https://image.3001.net/images/20191212/1576118917_5df1aa8502113.png!small)

研究人员还发现一个名为Update_Collector.exe的恶意软件，该工具利用WMI收集的数据寻找网络上其他计算机和用户帐户的更多信息，随后将该信息转储到文件中，上传到攻击者的服务器。还发现了一系列其他合法的工具，包括
[Process Hacker](https://processhacker.sourceforge.io/),  [IObit
Uninstaller](https://www.iobit.com/en/advanceduninstaller.php),
[PowerTool](https://www.microsoft.com/en-us/p/power-tool/9nblggh0cfd6?activetab=pivot:overviewtab), 和
[PsExec](https://docs.microsoft.com/en-us/sysinternals/downloads/psexec)。在其他几起攻击中使用了完全相同的工具集，攻击者针对世界各地组织的进行攻击，包括美国、加拿大和几个欧洲国家。受害组织至少有一台或多台带有RDP的计算机暴露在internet上。

在攻击过程中的某个时间点（可能是在初始网络攻击后几天到几周），攻击者将勒索软件组件下载到目标计算机。此组件名称包括每个受害者唯一五个字符代码和“_pack.exe”。

![1.PNG](https://image.3001.net/images/20191212/1576118956_5df1aaaca54bd.png!small)下载勒索软件并通过PSEXEC启动

当恶意软件调用PSEXEC服务来执行勒索软件时，它已将自己解压缩到Windows文件夹中，并使用相同的五个字符和“unpack.exe”。

![1.PNG](https://image.3001.net/images/20191212/1576118993_5df1aad199251.png!small)The
“unpack” version ends up in the Windows directory

勒索软件将自己安装为一个名为SuperBackupMan的Windows服务。服务描述文本“This service make backup copy
every day,”有助于其在服务列表中隐藏。此注册表项在计算机开始重新启动之前立即设置。

![1.PNG](https://image.3001.net/images/20191212/1576119338_5df1ac2ace473.png!small)SuperBackupMan服务可组织用户停止或暂停。

![1.PNG](https://image.3001.net/images/20191212/1576119897_5df1ae591dafd.png!small)

恶意软件将此key添加到Windows注册表中，以便在安全模式引导期间启动。

>
> HKLM\SYSTEM\CurrentControlSet\Control\SafeBoot\Minimal\SuperBackupMan:Default:Service

![1.PNG](https://image.3001.net/images/20191212/1576119927_5df1ae7770597.png!small)

使用Windows上的BCDEDIT工具发出命令，将Windows操作系统设置为以安全模式启动，然后立即强制重新启动受感染的计算机。

> bcdedit.exe /set {current} safeboot minimal
>
> shutdown /r /f /t 00

当计算机在重新启动后进入安全模式，恶意软件使用Windows组件net.exe停止SuperBackupMan服务，然后使用Windows组件vssadmin.exe删除系统上的所有Volume
Shadow副本，可阻止技术人员对勒索软件加密的文件进行取证恢复。

> net stop SuperBackupMan
>
> vssadmin delete shadows /all /quiet

勒索软件然后开始加密受感染机器的本地硬盘上的文件。

## Snatch影响分析

勒索软件在加密文件中会附加一个由五个字母数字字符组成的伪随机字符串。此字符串出现在勒索软件可执行文件名和勒索通知中，并且对于每个目标组织都是唯一的。例如，如果勒索软件名为abcdex64.exe，则加密的文件将文件扩展名.abcde附加到原始文件名后，勒索信息使用诸如README_abcde_files.txt或DECRYPT_abcde_DATA.txt之类的命名规范。

![1.PNG](https://image.3001.net/images/20191212/15761314014975.png!small)

一家专门从事勒索受害者和攻击者之间的谈判的公司称，从7月到10月，他们已经代表客户12次与罪犯谈判。赎金从2000美元到35000美元不等，四个月内呈上升趋势。

与许多其他勒索软件一样，
Snatch对于某些文件和文件夹位置列表不会加密。通常勒索软件这样做是为了维护系统的稳定性，将目标集中在工作文档或个人文件上。它跳过的位置包括：

> **C:\**
>
> windows
>
> recovery
>
> $recycle.bin
>
> perflogs
>
> **C:\ ProgramData**
>
> start menu
>
> microsoft
>
> templates
>
> favorites
>
> **C:\Program Files\**
>
> windows
>
> perflogs
>
> $recycle.bin
>
> system volume information
>
> common files
>
> dvd maker
>
> internet explorer
>
> microsoft
>
> mozilla firefox
>
> reference assemblies
>
> tap-windows
>
> windows defender
>
> windows journal
>
> windows mail
>
> windows media player
>
> windows nt
>
> windows photo viewer

![1.PNG](https://image.3001.net/images/20191212/1576120183_5df1af77d55eb.png!small)

在其中一个样本中发现攻击者在监控运行其代理的系统。当分析员意外注销时，分析员怀疑攻击者将机器识别为安全研究平台，于是他给攻击者写了一条消息，并将其留在了测试机器的桌面上。片刻之后，攻击者再次将分析员计算机注销，阻止分析员使用的IP地址重新连接到C2服务器。

![1.PNG](https://image.3001.net/images/20191212/1576120242_5df1afb2d6180.png!small)

还发现勒索软件正在使用OpenPGP，二进制文件将PGP公钥块硬编码到文件中。

## 预防与监测

### 预防

建议任何组织都不要将远程桌面界面暴露在不受保护的互联网上，应将它们置于VPN后，没有VPN凭据的人都无法访问。

攻击者还表示希望寻找其他的合作伙伴，能够使用其他类型远程访问工具（如VNC和TeamViewer）以及Web外壳或SQL注入技术。

组织应立即为具有管理权限的用户实现多因素身份验证，使攻击者更难强行利用这些帐户凭据。

### 检测

大多数初始访问和立足点都在未受保护和未受监视的设备上。组织应定期检测设备确保网络上没有被疏忽的设备机器。

勒索软件的勒索行为发生在攻击者进入网络后的几天。在勒索软件执行之前，需要一个成熟的威胁搜索程序识别攻击者的软件。

### 检测详细信息

通过以下签名检测Snatch的各种组件和此攻击中使用的文件：

> Troj/Snatch-H
>
> Mal/Generic-R
>
> Troj/Agent-BCYI
>
> Troj/Agent-BCYN
>
> HPmal/GoRnSm-A
>
> HPmal/RansMaz-A
>
> PUA Detected: ‘PsExec’

 ***参考来源：[sophos](https://news.sophos.com/en-us/2019/12/09/snatch-ransomware-reboots-pcs-into-safe-mode-to-bypass-protection/)，由Kriston编译，转载请注明来自FreeBuf.COM**

