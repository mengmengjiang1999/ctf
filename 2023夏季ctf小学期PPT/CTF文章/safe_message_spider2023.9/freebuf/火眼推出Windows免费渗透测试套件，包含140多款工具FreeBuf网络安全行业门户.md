>
> 2019年3月28日，火眼发布了一个包含超过140个开源Windows渗透工具包，红队渗透测试员和蓝队防御人员均拥有了顶级侦察与漏洞利用程序集。该工具集名为“CommandoVM”。  
>

**安全工作者在对系统环境进行渗透测试时常常会自己配置虚拟机，如果是Linux的话还好，还有Kali
Linux可以用。但是碰上Windows环境就惨了，往往配置虚拟机环境就要好几个小时。一边要维护自定义的虚拟机环境，一边还要时常升级集成的工具套件，花费的时间成本颇高。最近火眼推出了一款面向红队的Commando
VM渗透测试套件，有需要的小伙伴可以看一看，免费又好用。**  

![command-vm-kali-alternative-for-windows-world.png](https://image.3001.net/images/20190410/15548644702117.png!small)

火眼旗下麦迪安网络安全公司顾问以及Commando VM套件的联合创建者 Jake Barteaux 表示：

>
> 在进行内部渗透测试时，我身边的大部分渗透测试工程师都会先自行配置一个Windows测试环境。能不能把这个环境配置好，配得有多快，已然成为了衡量渗透测试工程师手艺高低的标准了。其中很多人都会再自己配置的环境中集成Commando中也有的工具，不过在对Windows进行渗透测试时大家并没有形成一个标准的工具集。

这一次火眼推出的标准化工具套件解决了两个最关键的问题。其一是整合了最优秀的渗透测试工具，无需再花很多时间去寻觅。其二则是2013年发布的Kali
Linux继承了超过600款安全、取证和探索工具，Commando选取了其中适用于Windows平台的精华工具，其中很多还是Windows平台原生支持的。

而渗透测试人员面临的第二个问题就是工具集的维护。Commando VM将所有工具打包到一个发行版中可以加快维护速度，修补和更新都更加简单。

## 关于Commando VM

火眼本次推出的Commando VM套件面向Windows平台构建，属于此前发布的[FLARE
VM](https://www.fireeye.com/blog/threat-research/2018/11/flare-vm-update.html)套件的全新迭代版本，后者专攻逆向工程和恶意软件分析，Commando
VM功能更加全面，是Windows环境中内部渗透测试的首选平台。

使用基于Windows平台构建的虚拟机环境有以下几点明显优势：

> 1、原生支持Windows和Active Directory；
>
> 2、可作为C2框架的临时工作区；
>
> 3、更便捷的共享和交互式操作支持；
>
> 4、支持PowerView和BloodHound等工具；
>
> 5、对测试目标不产生任何影响。

![Figure6a.png](https://image.3001.net/images/20190410/15548654763709.png!small)
_ **工具列表（详见文末GitHub地址）**_

Commando
VM使用Boxstarter、Chocolatey和MyGet软件包来安装所有软件，并提供多种用于渗透测试的工具和实用程序，共计140多款，涵盖以下领域：

> [Nmap](https://nmap.org/)
>
> [Wireshark](https://www.wireshark.org/)
>
> [Covenant](https://github.com/cobbr/Covenant)
>
> [Python](https://www.python.org/)
>
> [Go](https://golang.org/)
>
> [Remote ](https://support.microsoft.com/en-us/help/2693643/remote-server-> administration-tools-rsat-for-windows-operating-systems)
>
> [Server Administration Tools](https://support.microsoft.com/en-> us/help/2693643/remote-server-administration-tools-rsat-for-windows-> operating-systems)
>
> [Sysinternals](https://docs.microsoft.com/en-us/sysinternals/)
>
> [Mimikatz](https://github.com/gentilkiwi/mimikatz)
>
> [Burp-Suite](https://portswigger.net/)
>
> [x64dbg](https://x64dbg.com/)
>
> [Hashcat](https://hashcat.net/)

红蓝对抗中的双方都可以从Commando VM获益，对于蓝队而言该套件提供了高性能的网络审计和检测能力。

![Picture1.png](https://image.3001.net/images/20190410/15548625206228.png!small)

## 安装

建议在虚拟机中部署Commando VM，使用虚拟机软件的快照功能减少重新配置环境所需的时间，虚拟机环境要满足以下最低要求：

> 60GB磁盘空间
>
> 2GB内存

在完成虚拟机的基本配置后安装Windows镜像，支持：

> Windows 7 Service Pack 1
>
> Windows 10
>
> 建议使用Windows 10镜像以支持更多功能。

系统安装完成后建议添加配套的虚拟机工具（例如VMware
Tools）以支持复制/粘贴、屏幕显示调整等其他设置。虚拟机环境配置成功后，以下所有的步骤均在该环境中操作。

1、运行Windows Update确保系统已更新至最新版。建议更新完成后重启系统再次检查。

2、确保系统为最新版本后建立快照，万一需要重新配置的话可省去安装系统的时间。

3、下载[GitHub上的Commando VM](https://github.com/fireeye/commando-vm)文件并解压缩。

4、找到解压缩后的文件夹目录，使用管理员权限打开PowerShell会话（安装Commando VM需要修改系统设置）。

5、键入以下命令将PowerShell的执行策略更改为不受限制，并在PowerShell提示时回答“ Y ”：Set-ExecutionPolicy
unrestricted

6、执行install.ps1安装脚本。系统将提示输入当前用户的密码。Commando
VM需要当前用户的密码才能在重启后自动登录。可以通过命令行“-password ”来指定当前用户的密码。

![](https://image.3001.net/images/20190410/15548621768129.png!small)

7、剩下的安装过程需要联网并自动执行，根据网络速度可能需要2至3小时完成。期间虚拟机系统会重启多次。安装完成后，PowerShell保持打开状态，键入任意键可退出，完成后的桌面如下：

![2.png](https://image.3001.net/images/20190410/15548621892645.png!small)

8、看到这个桌面后再次重启系统保证所有配置生效。重启后再次建立快照以便不时之需。

## 传送门

> Commando VM 页面：<https://www.fireeye.com/blog/threat-> research/2019/03/commando-vm-windows-offensive-distribution.html>
>
> Commando VM 项目地址：<https://github.com/fireeye/commando-vm>

 ***参考来源：[FireEye](https://www.fireeye.com/blog/threat-research/2019/03/commando-vm-windows-offensive-distribution.html)，由Freddy编译，转载请注明来自FreeBuf.COM**

