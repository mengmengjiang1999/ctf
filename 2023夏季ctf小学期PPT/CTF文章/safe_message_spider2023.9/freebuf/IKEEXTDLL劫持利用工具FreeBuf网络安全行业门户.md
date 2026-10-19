## ****什么是IKEEXT提权****

IKEEXT提权是一种属于windows配置错误的提权方式,IKEEXT是一种windows服务、

IKEEXT 服务BAI托管 Internet 密钥交换(IKE)和身份验证 Internet 协议du(AuthIP)键控模块。这些键控模块用于zhi
Internet 协议安全(IPSec)中的身份验证和密钥交换。停止或dao禁用 IKEEXT 服务将禁用与对等计算机的 IKE/AuthIP
密钥交换。通常将 IPSec 配置为使用 IKE 或 AuthIP

## ****原理****

IKEEXT的服务(IKE和AuthIP IPsec
Keyring模块)，它作为系统运行，并尝试加载不存在的DLL。Windows默认的DLL搜索顺序包括几个系统目录，并以路径文件夹结束。简单地说，如果这些文件夹中的一个配置了弱权限，任何经过身份验证的用户都可以植入一个恶意DLL来作为SYSTEM
an执行代码

****为了更高效的使用IKEEXT提权，我们可以用IKEEXTDLL提权工具****

****下载地址：****[ ** _ **https://github.com/securycore/Ikeext-Privesc**_**](https://github.com/securycore/Ikeext-Privesc)

此工具用于自动检测和利用IKE和AuthIP IPsec Keyring模块服务(IKEEXT)丢失的DLL漏洞。

## 描述

在Windows Vista, 7,8, Server 2008, Server 2008 R2和Server
2012中存在一个主要的弱点，它允许任何经过身份验证的用户在某些情况下获得系统特权。

在Windows中，有一个名为IKEEXT的服务(IKE和AuthIP IPsec
Keyring模块)，它作为系统运行，并尝试加载不存在的DLL。Windows默认的DLL搜索顺序包括几个系统目录，并以路径文件夹结束。简单地说，如果这些文件夹中的一个配置了弱权限，任何经过身份验证的用户都可以植入一个恶意DLL来作为系统执行代码，从而提高他/她的特权。

试图加载“wlbsctr .dll”:

## 用法

这个PowerShell脚本由2个cmdlet组成:

Invoke-IkeextCheck—只检查机器是否有漏洞。

invoker - ikeextexploit——如果机器是易受攻击的，通过将一个特别制作的DLL放到第一个弱文件夹来利用它。

## 检测

Invoke-IkeextCheck Cmdlet执行以下检查:

操作系统版本-如果操作系统是windowsvista /7/8，那么机器有潜在的弱点。

IKEEXT状态和启动类型——如果启用了服务，那么机器可能会受到攻击(默认情况下)。

具有弱权限的路径文件夹-如果至少找到一个文件夹，计算机可能会受到攻击。

wlbsctrl.dll是否已经存在于某个系统文件夹中(即dll可以被加载的文件夹)?-如果wlbsctr .dll不存在，机器是潜在的脆弱(默认)。

语法:

> Invoke-IkeextCheck [- verbose)

例子:

> psc:\temp> . .\Ikeext-Privesc.ps1
>
> psc:\temp>调用- ikeextcheck -Verbose

![](https://image.3001.net/images/20200807/1596790682.png!small)

## 利用

如果机器是有漏洞的，Invoke-IkeextExploit Cmdlet将执行以下操作:

根据IKEEXT开始类型:

AUTO -如果在命令行中设置了“- force”开关(安全覆盖)，漏洞文件将被放到第一个弱路径文件夹。

手动-利用文件将被拖放到第一个弱路径文件夹。然后，通过尝试打开虚拟VPN连接(使用rasdial)，将触发服务启动。

以下攻击文件将被放到第一个易受攻击的文件夹:

DLL -一个特别制作的DLL(32和64位)，用来启动一个新的CMD进程并执行一个批处理文件。

bat—将要执行的批处理文件。

批处理载荷:

Default—此脚本中包含默认批处理有效负载。它将使用net user和net
localgroup创建一个新用户(hacker，密码为SuperP@ss123)，并将其添加到本地administrators组(该脚本自动检索组的名称)。

Custom -可以使用参数- payload .\Path\To\ file .txt指定一组自定义命令，并使用每行包含一个命令的文件。

日志文件——每个有效负载命令的输出被重定向到与DLL文件位于同一文件夹中的日志文件。它的名称将类似于wlbsctrl_xxxxxxxxx
.txt。因此，如果未创建此文件，则意味着未执行有效负载。

语法:

> Invoke-IkeextExploit [-Verbose] [-Force] [[-Payload] <String>]

例子:

> psc:\temp> . .\Ikeext-Privesc.ps1
>
> p C: \ temp > Invoke-IkeextExploit

高科技桥梁——Frederic
Bourla，他最初发现了这个漏洞并在2012年10月9日披露了它。——https://www.htbridge.com/advisory/HTB23108

## 修复

首先，需要注意的是，这个漏洞在Windows 8.1及以上版本中被修补过。在这些版本的Windows中，wlbsctr
.dll搜索被限制为c:windows失败。

如果你被困在Windows 7 / Server 2008R2因为兼容性问题，例如，几个应对措施可以应用:

权限较弱的路径文件夹——有些应用程序直接安装在C:\中，并将它们自己添加到PATH环境变量中。默认情况下，在C:\中创建的文件夹是任何经过身份验证的用户都可以写的，因此请确保删除这些特权。

禁用IKEEXT——在大多数情况下，可以通过应用GPO禁用IKEEXT。对于服务器来说，这可能是一个很好的解决方案，但不建议用于工作站。

部署你自己的DLL
-部署一个虚拟的wlbsctrl.dll在c::windowssystem32\例如，是一个有效的解决方案，因为这个目录比路径文件夹有更高的优先级。

