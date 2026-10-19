在本文中，我们将介绍在基于Linux的设备上进行初始访问后，可用于后渗透阶段漏洞利用和枚举的一些自动化脚本。

#  ** **介绍****

大多数时候，当攻击者攻击Linux操作系统时，他们将获得基本的Shell，可以将其转换为TTY
Shell或meterpreter会话。但是此shell程序可以执行的操作常常受到限制。因此，为了提权，我们需要枚举不同的文件，目录，权限，日志和/etc/passwd文件。

一般来说，提权是在攻击者入侵受害者的计算机之后进行的阶段，在该计算机上，攻击者试图收集与系统有关的关键信息，例如隐藏的密码和脆弱配置的服务或应用程序等。所有这些信息都有助于攻击者在后渗透阶段攻击机器来获得更高特权的shell。

##  ** **特权提升维度****

操作系统版本

任何已安装或正在运行的易受攻击的软件包

具有完全控制或修改访问权限的文件和文件夹

映射驱动器

可能有趣的文件

网络信息（接口，ARP）

防火墙状态和规则

运行过程

存储的凭证

sudo权限

路径变量

Docker

…

渗透测试中通常使用了如下脚本来快速识别Linux系统上潜在的特权提升维度

##  ** **1.LinPEAS****

GitHub链接：

https://github.com/carlospolop/privilege-escalation-awesome-scripts-suite/tree/master/linPEAS

它是由Carlos
P创建的，目的是列举在Linux系统上提升特权的所有可能方法。关于LinPEAS的比较好的一点是它不需要其它依赖项。这使它能够运行现有二进制文件支持的任何内容。

LinPEAS支持Debian，CentOS，FreeBSD和OpenBSD。

LinPEAS不会将任何内容直接写入磁盘，并且在默认情况下运行时，它不会尝试通过su命令以其他用户身份登录。LinPEAS执行花费的时间从2分钟到10分钟不等，具体取决于请求的检查次数。

如果要在CTF比赛中运行LinPEAS，请尽量使用-a参数，它将激活所有检查。LinPEAS监视进程以查找非常频繁的cron任务，但是要执行此操作，您将需要添加-a参数，并且此检查将在文件中写入一些信息，该信息稍后将被删除，这使得我们执行完它不会留下痕迹。

-s（超快和隐身）：这将绕过一些耗时的检查，并且不会留下任何痕迹。

-P（密码）：传递将与sudo -l和Bruteforcing其他用户一起使用的密码

-h帮助

-o仅执行选定的检查

-d <IP/NETMASK>使用fping或ping查找主机

ip <端口> -d <IP/NETMASK>使用nc查找正在寻找TCP开放端口的主机

它在执行期间导出并取消设置一些环境变量，因此在会话期间执行的任何命令都不会保存在历史记录文件中，如果您不想使用此功能，只需在利用它时添加-n参数即可。LinPEAS可以使用curl命令直接从GitHub执行。

curl https://raw.githubusercontent.com/carlospolop/privilege-escalation-awesome-scripts-suite/master/linPEAS/linpeas.sh | sh

![1621840499_60ab52738a7f2f8ba2b44.png!small?1621840462226](https://image.3001.net/images/20210524/1621840499_60ab52738a7f2f8ba2b44.png!small?1621840462226)

![1621842083_60ab58a382bd5f8044786.png!small?1621842046290](https://image.3001.net/images/20210524/1621842083_60ab58a382bd5f8044786.png!small?1621842046290)

主机的网络信息

![1621842120_60ab58c86e516ed4bebb3.png!small?1621842083193](https://image.3001.net/images/20210524/1621842120_60ab58c86e516ed4bebb3.png!small?1621842083193)

主机安装的软件信息，还有更多的信息，请自行测试，不再一一展示。

2.LinEnum

GitHub链接：

[
_https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh_](https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh)

它是由Rebootuser创建的。LinEnum是一个Shell脚本，其工作原理是从目标计算机中提取有关提升特权的信息。它支持实验报告功能，可以帮助以可读的报告格式导出扫描结果。一些参数，例如：

-k输入关键字

-e输入导出位置

-t包括详尽的测试

-s提供当前用户密码以检查sudo权限（不安全）

-r输入报告名称

-h显示帮助文本

它检查下面提到的各种资源或详细信息：

内核和发行版本的详细信息

系统信息：

主机名，网络详细信息，当前IP，默认路由详细信息，DNS服务器信息

用户信息：

当前用户详细信息，“最近登录的用户”，显示登录到主机的用户，列出所有用户，包括uid/
gid信息，列出根帐户，提取密码策略和哈希存储方法信息，检查umask值，检查密码哈希是否存储在/中etc/passwd，提取“默认”uid的完整详细信息，例如0、1000、1001等，尝试读取受限制的文件（例如/etc/shadow），列出当前用户的历史文件（即.bash_history，.nano_history等），基本的SSH检查。

![1621842305_60ab59815b0c9ed9aa0f2.png!small?1621842267944](https://image.3001.net/images/20210524/1621842305_60ab59815b0c9ed9aa0f2.png!small?1621842267944)

特权访问：

会列举哪些用户最近使用过sudo，确定/ etc /
sudoers是否可访问，确定当前用户是否具有不带密码的Sudo访问，通过Sudo提供的已知较好突破二进制文件（nmap，vim等），是root用户可访问主目录，列出/home/的权限

环境的：

显示当前的$ PATH，显示环境信息

![1621842318_60ab598e3bddf5552879b.png!small?1621842281048](https://image.3001.net/images/20210524/1621842318_60ab598e3bddf5552879b.png!small?1621842281048)

工作/任务：

列出所有cron作业，找到所有本地写入的cron作业，找到系统其他用户拥有的cron作业，列出活动和不活动的systemd计时器

服务：

列出网络连接（TCP和UDP），列出正在运行的进程，查找和列出进程二进制文件及相关的权限，列出Netconf或隐秘的内容和相关的二进制文件权限，列出init.d二进制权限

以下软件的版本信息：

Sudo，MYSQL，Postgres，Apache（检查用户配置，显示启用的模块，检查htpasswd文件，查看www目录）

默认/弱凭证：

检查默认/弱口令的Postgres帐户，检查默认/弱口令的MYSQL帐户

![1621842336_60ab59a093a3d48badc20.png!small?1621842299443](https://image.3001.net/images/20210524/1621842336_60ab59a093a3d48badc20.png!small?1621842299443)

截图只展示部分获取的主机信息。

3.Bashark

GitHub链接：

https://raw.githubusercontent.com/redcode-labs/Bashark/master/bashark.sh

它是由RedCode Labs创建的。Bashark旨在帮助渗透测试人员和安全研究人员在Linux，OSX或Solaris
Server的安全评估的后开发阶段。

Bashark比较好的一点是它一个bash脚本，这意味着它可以直接从终端运行而无需任何安装。它速度快，不会使目标计算机过载。它也不需要任何特定依赖项，由于它在执行后抹去了它的存在，因此执行后很难被检测到。在这里，我们使用wget命令下载了Bashark，该命令在攻击者计算机上本地托管。然后使用chmod提供执行权限，然后运行Bashark脚本。它将升级您的Shell，使其能够执行不同的命令。

![1621842352_60ab59b01e63d4384de25.png!small?1621842315029](https://image.3001.net/images/20210524/1621842352_60ab59b01e63d4384de25.png!small?1621842315029)

在这里，我们使用getperm -c命令查找。Bashark还使用getconf命令枚举了所有常见的配置文件路径。

![1621842361_60ab59b9a5dbb974f7f0b.png!small?1621842324328](https://image.3001.net/images/20210524/1621842361_60ab59b9a5dbb974f7f0b.png!small?1621842324328)

除了以上一些功能，输入help命令，可以根据个人需求进一步利用。

![1621842369_60ab59c1c73016e607e8c.png!small?1621842332499](https://image.3001.net/images/20210524/1621842369_60ab59c1c73016e607e8c.png!small?1621842332499)

4.LES：Linux Exploit Suggester

GitHub链接：

https://raw.githubusercontent.com/mzet-/linux-exploit-suggester/master/linux-exploit-suggester.sh

它是由Z-Labs创建的。与本文中的其他脚本一样，该工具还旨在帮助安全测试人员或分析人员测试Linux计算机的潜在漏洞和提升特权的方式。LES的设计方式使其可以跨Linux的不同版本运行。Z-Labs广泛的研究和改进使该工具变得功能强大，且误报率极低。LES的基本工作始于根据检测到的内核版本生成初始漏洞利用列表，然后检查每种漏洞利用的特定标签。它收集所有积极结果，然后根据潜在风险对它们进行排名，最后将其显示给用户。我们可以看到我的本地计算机容易受到CVE
2021-3156，CVE 2019-18634，CVE 2017-5618等的漏洞攻击。

![1621842464_60ab5a20eb70897d91045.png!small?1621842427654](https://image.3001.net/images/20210524/1621842464_60ab5a20eb70897d91045.png!small?1621842427654)

5.LinuxPrivChecker

GitHub链接：

https://raw.githubusercontent.com/sleventyeleven/linuxprivchecker/master/linuxprivchecker.py

它是由Mike Czumak创建的，并由Michael
Contino维护。这是一个可在Linux系统上运行的python脚本。它搜索可写文件，错误配置和明文密码以及可应用的漏洞利用。它还提供了一些有趣的位置，这些位置可以在提升特权的同时发挥关键作用。它从基本系统信息开始，然后我们可以得到内核版本，主机名，操作系统，网络信息，运行服务等信息。

python linuxprivchecker.py

![1621842550_60ab5a766293b6c7c6da7.png!small?1621842513155](https://image.3001.net/images/20210524/1621842550_60ab5a766293b6c7c6da7.png!small?1621842513155)

LinuxPrivChecker还可以检查/etc/passwd/文件以及其他信息，例如组信息或对可能感兴趣的不同文件的写权限。

![1621842560_60ab5a80e82b2d980730b.png!small?1621842523750](https://image.3001.net/images/20210524/1621842560_60ab5a80e82b2d980730b.png!small?1621842523750)

6.Linux Private-i

GitHub链接：

https://raw.githubusercontent.com/rtcrowley/linux-private-i/master/private-i.sh

它是由creosote创建的。可以将Linux Private-i定义为Linux枚举或特权升级工具，该工具执行基本的枚举步骤并以易于阅读的格式显示结果。该脚本有一个非常冗长的选项，其中包括重要的检查，例如操作系统信息和对通用文件的权限，在检查版本，文件权限和可能的用户凭据时搜索通用应用程序，通用应用程序：Apache
/
HTTPD，Tomcat，Netcat，Perl，Ruby，Python，WordPress，Samba，数据库应用程序：SQLite，Postgres，MySQL/MariaDB，MongoDB，Oracle，Redis，CouchDB，邮件应用程序：Postfix，Dovecot，Exim，Squirrel
Mail，Cyrus，Sendmail，Courier，检查网络信息–netstat，ifconfig，基本安装信息，crontab和bash历史记录。这是运行“全范围”时的代码段。我们看到目标机器具有可读的/etc/passwd文件。我们还被告知，Netcat，Perl，Python等已安装在目标计算机上。

![1621842577_60ab5a91707d30cae33b9.png!small?1621842540346](https://image.3001.net/images/20210524/1621842577_60ab5a91707d30cae33b9.png!small?1621842540346)

Private-i还提取了cronjob内部的脚本，该脚本在设置的持续时间后执行，还有挂载信息。

![1621842604_60ab5aac527545c2a41fb.png!small?1621842567187](https://image.3001.net/images/20210524/1621842604_60ab5aac527545c2a41fb.png!small?1621842567187)

7.Linux Smart Enumeration

GitHub链接：

https://raw.githubusercontent.com/diego-treitos/linux-smart-enumeration/master/lse.sh

它是由Diego Blanco创建的。Linux Smart
Enumeration是受我们之前讨论的LinEnum脚本启发改进的脚本。该脚本的目的与提到的所有其他脚本相同。该脚本具有3个详细级别，因此用户可以控制您看到的信息量。它使用颜色来区分警报类型，例如绿色，这意味着可以使用它来提升目标计算机上的特权。它询问用户是否知道用户密码，以便检查sudo特权。它会检查用户组，路径变量，Sudo权限和其他有趣的文件。

![1621842618_60ab5abacd3c391b08b2c.png!small?1621842581465](https://image.3001.net/images/20210524/1621842618_60ab5abacd3c391b08b2c.png!small?1621842581465)

![1621842629_60ab5ac5a31bfda1fcb83.png!small?1621842592463](https://image.3001.net/images/20210524/1621842629_60ab5ac5a31bfda1fcb83.png!small?1621842592463)

8.Linux Exploit Suggester 2

Github链接：

https://github.com/jondonas/linux-exploit-suggester-2

它很大程度上基于第一个版本。有些不错的变化包括更多漏洞利用，并且可以选择直接从漏洞利用数据库下载检测到的漏洞利用代码。它具有更准确的通配符匹配。它扩大了可搜索漏洞的范围。chmod
777 linux-exploit-suggester-2.pl

./linux-exploit-suggester-2.pl -k 3

![1621842642_60ab5ad2cf94c3234b803.png!small?1621842605507](https://image.3001.net/images/20210524/1621842642_60ab5ad2cf94c3234b803.png!small?1621842605507)

