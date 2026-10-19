**攻击者使用了未知的SQL注入漏洞针对Sophos防火墙发起攻击，该漏洞可通过防火墙远程代码执行。攻击中使用了一系列Linux
Shell脚本，下载了为防火墙操作系统编译的恶意软件。该漏洞分析针对的是Sophos产品，旨在从防火墙窃取敏感信息。**

## 漏洞分析

攻击者发现并利用了零日SQL注入远程代码执行漏洞，利用此漏洞攻击者能够在数据库表中插入单行命令。

![image.png](https://image.3001.net/images/20200525/1590367959_5ecb16d7e7278.png!small)

注入命令触发受影响设备漏洞，从恶意域sophosfirewallupdate.com下载名为Install.sh的Linux
Shell脚本。该命令还将此Shell脚本写入/tmp目录，使用chmod指定为可执行文件并执行。该脚本（以x.sh形式写入设备）运行了一系列SQL命令，并将其他文件植入到虚拟文件系统中。

最初Install.sh脚本运行了许多Postgres
SQL命令，修改数据库中某些表值或将这些表归零，其中的一个表记录了管理IP地址，从而掩盖攻击。但是在某些设备上，shell脚本的活动导致攻击者的SQL命令显示在防火墙管理面板上。

![image.png](https://image.3001.net/images/20200525/1590368275_5ecb1813320a9.png!small)该脚本还会把其他Shell脚本放入/tmp目录，并修改防火墙操作系统的Shell脚本，在脚本末尾添加一组命令，确保它在每次防火墙启动时都能运行。  

##
![image.png](https://image.3001.net/images/20200525/1590368357_5ecb186542ee6.png!small)技术分析

安装程序脚本x.sh植入了两个新的Shell脚本，并修改了操作系统的脚本。植入脚本之一为.lp.sh，其主要功能是连接到恶意的sophosfirewallupdate，下载在防火墙操作系统上运行的Linux
ELF可执行文件。 脚本将下载的文件写入/tmp中，名为b。

![image.png](https://image.3001.net/images/20200525/1590368696_5ecb19b8988c3.png!small)b程序在运行时会从设备的文件系统中删除自身，它仅存在于内存中。
它会出现在进程列表中，进程名为cssconf.bin与正常运行在防火墙的cscconf.bin合法进程相差一个字符。
它列出了其父进程ID为1，这是合法cscconf.bin不会做的。  

![image.png](https://image.3001.net/images/20200525/1590368800_5ecb1a2059558.png!small)

当b处于内存中时，它每3到6个小时重复执行任务，第一次运行时会随机选择一个延迟间隔。首先，b检查是否可与43.229.55.44建立连接。
如果无法与该IP地址建立连接，它会尝试解析恶意域sophosproductupdate.com的IP地址。

![image.png](https://image.3001.net/images/20200525/1590368885_5ecb1a75749c1.png!small)

如果它解析了该域的IP，并且DNS结果没有返回值127.0.0.1，它会下载另一个名为Sophos.dat的Linux ELF可执行文件。

Install.sh/x.sh脚本植入的第二个Shell脚本以.pg.sh的文件名写入/tmp目录。它的主要目的是下载ELF可执行文件，该文件在Web服务器上称为bk，并以.post_MI名称写入文件系统。  

第一阶段的dropper Install.sh运行了许多Postgres
SQL命令。这些命令修改了特定的服务值，每当执行该服务时都会执行.post_MI，在每次重新启动时都会启动恶意软件。该可执行文件的功能有限，它检查是否已将名为.a.PGSQL的文件写入/tmp目录，如果找不到，则会下载ragnarokfromasgard.com上托管的patch.sh脚本。在对攻击进行分析时，该服务器没有响应。

![image.png](https://image.3001.net/images/20200525/1590369142_5ecb1b7637fe4.png!small)

第三个脚本用来修改防火墙内部操作系统，名为generate_curl_ca_bundle.sh。在修改原始脚本之前，Install.sh/x.sh脚本对原始文件备份（在文件名.generate_curl_ca_bundle.sh之前加了点）。该代码会植入了另一个shell脚本/tmp/I。

脚本I具有两个主要功能：首先它新建/tmp/.a.PGSQL文件。然后从sophosfirewallupdate域中检索了一个名为lc的脚本文件，并将其以.n.sh写入/tmp目录并执行。该脚本复制了与.lp.sh脚本，并尝试从恶意的sophosfirewallupdate网站下载并执行b
ELF可执行文件。

## 数据泄露

恶意软件下载并执行在远程服务器上名为Sophos.dat的文件，并以2own保存到文件系统。  

![image.png](https://image.3001.net/images/20200525/1590369411_5ecb1c830a93f.png!small)

该恶意软件的主要任务是数据盗窃，它会检索防火墙中存储的各种数据库表内容并运行操作系统命令。
每个步骤中恶意软件都会收集信息，然后将其临时存储在防火墙的Info.xg文件中。

首先会尝试搜索防火墙外部IP地址，先通过网站ifconfig.me来查询，如果该网站无法访问，它会尝试通过checkip.dyndns.org查询。接下来查询防火墙数据存储区域，检索防火墙及其用户的信息。下图显示了恶意软件入侵能力。

![image.png](https://image.3001.net/images/20200525/1590369595_5ecb1d3b5efc6.png!small)

该恶意软件搜集防火墙信息包括：

1、防火墙的许可证和序列号  

2、设备上存储的用户邮件列表，管理员帐户电子邮件

3、防火墙用户名称，用户名，密码以及管理员帐户密码。密码不是以纯文本格式存储。

4、将防火墙用于SSL VPN的用户ID和使用“clientless” VPN连接的帐户列表。

该恶意软件还查询了防火墙的内部数据库，检索防火墙用户的IP地址分配权限列表，以及设备本身的信息：操作系统版本，CPU的类型以及内存，自上次重启以来已运行了多长时间，ifconfig和ARP表。  

![image.png](https://image.3001.net/images/20200525/1590369827_5ecb1e23468b0.png!small)恶意软件将所有信息写入Info.xg，使用tar压缩工具对其进行压缩，然后使用OpenSSL加密文件。
攻击者使用Triple-DES算法对文件进行加密，使用“GUCCI”一词作为密码，上传到IP为38.27.99.69的服务器上，然后删除在收集信息时临时创建的文件。  

##
![image.png](https://image.3001.net/images/20200525/1590369925_5ecb1e858c66e.png!small)IOCs

##
![image.png](https://image.3001.net/images/20200525/1590369988_5ecb1ec44b6be.png!small)Network
indicators  

### URLs  

> hxxps://sophosfirewallupdate.com/sp/Install.sh
>
> hxxp://sophosfirewallupdate.com/sh_guard/lc
>
> hxxps://sophosfirewallupdate.com/bk
>
> hxxps://sophosfirewallupdate.com/sp/lp
>
> hxxps://ragnarokfromasgard.com/sp/patch.sh
>
> hxxps://sophosfirewallupdate.com/sp/sophos.dat
>
> hxxps://sophosfirewallupdate.com/in_exit
>
> hxxps://sophosfirewallupdate.com/sp/lpin
>
> hxxp://sophosfirewallupdate.com/bkin
>
> hxxp://filedownloaderservers.com/bkin
>
> hxxps://sophosfirewallupdate.com/sp/p.sh
>
> hxxps://sophosfirewallupdate.com/sp/ae.sh

### Domains  

> sophosfirewallupdate.com
>
> filedownloaderservers.com
>
> ragnarokfromasgard.com
>
> sophosenterprisecenter.com
>
> sophoswarehouse.com
>
> sophosproductupdate.com
>
> sophostraining.org

### Additional suspicious domains  

> filedownloaderserverx.com
>
> filedownloaderserver.com
>
> updatefileservercross.com

### IPs  

> 43.229.55.44
>
> 38.27.99.69

### Filesystem paths  

> /tmp/x.sh
>
> /var/newdb/global/.post_MI
>
> /scripts/vpn/ipsec/generate_curl_ca_bundle.sh (modified)
>
> /scripts/vpn/ipsec/.generate_curl_ca_bundle.sh (original)
>
> /tmp/I
>
> /tmp/.a.PGSQL
>
> /tmp/.n.sh
>
> /tmp/.pg.sh
>
> /tmp/.lp.sh
>
> /tmp/b
>
> /tmp/2own
>
> /tmp/Info.xg
>
> /tmp/%s_.xg.rel
>
> /tmp/%s_.xg.salt
>
> /tmp/ip (result of <http://checkip.dyndns.org/ip_dyn>)
>
> /tmp/ip_dyn (result of <https://ifconfig.me/ip>)

 ***参考来源：[sophos](https://news.sophos.com/en-us/2020/04/26/asnarok/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

