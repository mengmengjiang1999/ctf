## Windows内核溢出漏洞提权

> Windows内核溢出漏洞提权通过系统本身存在的一些漏洞，未曾打相应的补丁而暴露出来的提权方法，依托可以提升权限的EXP和它们的补丁编号，进行提升权限

说白了，就是信息收集，收集一下看看有没有一些没有打补丁的历史漏洞。

### 使用 **Metasploit信息收集**

`post/windows/gather/enum_applications` 查看系统可能存在的可以利用的漏洞

![](./img/8227680282412993514.png)

`post/windows/gather/enum_patches` 查找系统中的补丁信息。

![](./img/557282441283375626.png)

但是我这里报错了，应该是系统问题。

### 手撸信息收集

拿shell

![](./img/1752403396402604391.png)

但是会乱码，非常影响观感  
`chcp 65001`

![](./img/6038275931142192483.png)

可以看到，目标并没有打补丁

![](./img/230045720398547198.png)

`Wmic qfe get Caption,Description,HotFixID,InstalledOn` //查看windows机器上安装了多少补丁

> WMIC是Windows Management Instrumentation Command-> line的简称，它是一款命令行管理工具，提供了从命令行接口到批命令脚本执行系统管理的支持，可以说是Windows平台下最有用的命令行工具。使用WMIC，我们不但可以管理本地计算机，还可以管理统一局域网内的所有远程计算机（需要必要的权限），而被管理的计算机不必事先安装WMIC

![](./img/1839816724083651945.png)

可以看到并没有安装补丁  
我的windows是这样的

![](./img/6962800148368794620.png)

### **Windows Exploit Suggester**

[Windows Exploit Suggester](https://github.com/AonCyberLabs/Windows-Exploit-Suggester)

>
> 描述此工具将目标补丁级别与Microsoft漏洞数据库进行比较，以便检测目标上潜在的缺失补丁。如果有公开的漏洞，它还会通知用户，并为缺失的公告提供Metasploit模块。它需要来自Windows主机的'systeminfo'命令输出，以便比较Microsoft安全公告数据库并确定主机的补丁级别。它可以自动从微软下载带有——update标志的安全公告数据库，并将其保存为Excel电子表格。在查看命令输出时，一定要注意，它假设所有漏洞，然后根据热修复数据有选择地删除它们。这可能会导致许多误报，了解目标主机上实际运行的软件是非常关键的。例如，如果已知存在IIS漏洞，即使IIS没有在目标主机上运行，它也会对其进行标记。输出显示公共漏洞(E)或由字符值指定的Metasploit模块(M)。它很大程度上受到了Pentura的Linux_Exploit_Suggester的启发。博客文章:“介绍Windows利用建议者”，<https://blog.gdssecurity.com/labs/2014/7/11/introducingwindows-> exploit-suagester.html>
    
    
    python windows-exploit-suggester.py --update  //更新漏洞数据库
    将systeminfo 另存为一个文件
    systeminfo > sysinfo.txt
    python windows-exploit-suggester.py -d 2020-11-11-mssb.xls -i sysinfo.txt
    //对比漏洞库，查看是否存在历史提权漏洞
    ps：需要安装xlrd库

### 实战

将session保存

![](./img/8671065850243011342.png)

使用cve-2018-8120

![](./img/5899185314084844199.png)

设置session

![](./img/6015139031933686056.png)

可以看到拿到system权限  
当然，不止这一个cve，有别的常用`MS16-032、MS15-051 和 MS14-058 、MS18-8120等`  
windows系统溢出漏洞提权汇总：<https://github.com/SecWiki/windows-kernel-exploits>

## UAC提权

> 用户帐户控制(UAC)，它是Windows的一个安全功能，它支持防止对操作系统进行未经授权的修改，UAC确保仅在管理员授权的情况下进行某些更改。  
>
> UAC通过阻止程序执行任何涉及有关系统更改/特定任务的任务来运行。除非尝试执行这些操作的进程以管理员权限运行，否则这些操作将无法运行。如果您以管理员身份运行程序，则它将具有更多权限，因为它将被“提升权限”，而不是以管理员身份运行的程序。  
>  UAC不会自动阻止恶意软件，其目的不是确定程序是否是恶意软件，而是在没有用户许可下对恶意软件的未授权行为进行掌控。

把session放入后台 返回session编号

![](./img/7396276070930721095.png)

`set session 1`

然后尝试拿下system权限

![](./img/8512851303431871966.png)

## 令牌窃取

>
> 简介：令牌(token)是系统的临时秘钥，相当于账号和密码，用来决定是否允许这次请求和判断这次请求是属于哪一个用户的。它允许你在不提供密码或其他凭证的前提下，访问网络和系统资源，这些令牌将持续存在于系统中，除非系统重新启动。  
>  令牌有很多种：  
>  访问令牌(Access Token)：表示访问控制操作主体的系统对象 。  
>  会话令牌(Session Token)：是交互会话中唯一的身份标识符。  
>  密保令牌(Security Token)：又叫做认证令牌或硬件令牌，是一种计算机身份校验的物理设备，例如U盾。

![](./img/4811342257179068420.png)

    
    
    use incognito //进入incognito模块
    list_tokens -u //列出令牌
    impersonate_token "WIN-HN02RO8B2OU\86158"  //模仿令牌（它没有扫描处我的靶机里面的system权限的用户，所以我将就模仿）
    cs等也有窃取令牌的功能。

当然，这只是极其简单的说明原理罢了，如果提权失败的话，比这种好得多的还有 **msf烂土豆提权/多汁土豆提权。**  
优点就是，比较可靠，而且版本通杀。  
具体参考：<https://blog.csdn.net/god_zzZ/article/details/106334702>

## windows 系统配置错误提权

>
> Windows在系统启动时，会伴随着一些高权服务启动(windows服务是以system权限运行的)倘若某些服务存在一些漏洞，那么就能够借此服务进行权限劫持，例如DLL劫持

### 系统服务权限配置错误

>
> windows系统服务文件在操作系统启动时加载执行，并在后台调用可执行文件。如果一个低权限的用户对此类系统服务调用的可执行文件拥有写权限，那么就可以替换该文件，并随着系统启动获得控制权限。

#### Metasploit

`use exploit/windows/local/service_permissions`

> service_permissions模块会使用 两种方式获取system权限  
>  如果以管理员权限运行 会尝试创建并运行一个新的服务  
>  如果当前权限不允许创建服务 会判断哪些服务的文件或文件夹的权限有问题 并对其进行劫持  
>  在劫持服务时会创建一个可执行程序 其文件名和安装路径都是随机的

![](./img/5465258209740464046.png)

#### PowerUp

[PowerUp](https://github.com/PowerShellMafia/PowerSploit/blob/master/Privesc/PowerUp.ps1)

> PowerUp 所做的事是寻找可能存在弱点的地方，从而帮助提权

具体参考：[此链接](https://blog.csdn.net/qq_37683287/article/details/107550139#:~:text=%E5%88%A9%E7%94%A8%20PowerUp%20%E8%BF%9B%E8%A1%8C%E6%8F%90%E6%9D%83%E9%9C%80%E8%A6%81%E9%A6%96%E5%85%88%E5%AF%BC%E5%85%A5%20ps1%20%E6%96%87%E4%BB%B6%20powershell-import,PowerUp.ps1%20%EF%BC%8C%E5%86%8D%E6%89%A7%E8%A1%8C%20powershell%20Invoke-AllChecks%20%E5%91%BD%E4%BB%A4%EF%BC%8C%E4%BD%BF%E7%94%A8%20PowerUp%20%E8%84%9A%E6%9C%AC%E5%8F%AF%E4%BB%A5%E5%BF%AB%E9%80%9F%E7%9A%84%E5%B8%AE%E5%8A%A9%E6%88%91%E4%BB%AC%E5%8F%91%E7%8E%B0%E7%B3%BB%E7%BB%9F%E5%BC%B1%E7%82%B9%EF%BC%8C%E4%BB%8E%E8%80%8C%E5%AE%9E%E7%8E%B0%E6%8F%90%E6%9D%83%E7%9A%84%E7%9B%AE%E7%9A%84%E3%80%82)

### **注册表键AlwaysInstallElevated**

> 允许低权限用户以System权限安装文件。如果启用此策略设置项，那么任何权限的用户都以NT Authority\System权限来安装恶意的MSI文件。

**防御方法** ： 只要禁用注册表键AlwaysInstallElevated 就可以阻止攻击者通过MSI文件进行提权

#### Metasploit

`exploit/windows/local/always_install_elevated`模块

> 该模块会创建一个文件名随机的MSI文件 并在提权后删除所有已部署的文件

![](./img/4195488763163985329.png)

只需要设置session即可

![](./img/2250527771584133876.png)

但是我的失败了，说明这种方法成功的几率非常小

#### PowerUp

> powerup下的Get-RegistryAlwaysInstallElevated模块检查注册表键是否被设置  
>  如果被设置则意味MSI文件是以system权限下能运行

### 自动安装配置文件

>
> 网络管理员在内网中给多台机器配置同一个环境时，通常不会逐个配置，而是使用脚本批量部署。在这个过程中，会使用安装配置文件。这些文件中包含所有的安装配置信息，其中一些还可能包含管理员账号和密码

`post/windows/gather/enum_unattend` 模块

![](./img/4474591435232048175.png)

些许鸡肋

![](./img/6899809859308388900.png)

## 组策略首选项提权

**组策略首选项**

> Windows 2008
> Server引入了一项新功能：策略首选项，组策略首选项使管理员可以部署影响域中计算机/用户的特定配置，通过在组策略管理控制台中配置的组策略首选项，管理员可以推出多种策略，例如，当用户登录其计算机时自动映射网络驱动器，更新内置管理员帐户的用户名或对注册表进行更改。

**sysvol**

>
> SYSVOL是AD(活动目录)里面一个存储域公共文件服务器副本的共享文件夹，所有的认证用户都可以读取。SYSVOL包括登录脚本，组策略数据，以及其他域控所需要的域数据，这是因为SYSVOL能在所有域控里进行自动同步和共享。  
>  所有组策略均存储在： **\ <domain>\SYSVOL\<domain>\Policies\</domain></domain>**

**组策略偏好GPP**

> win2008发布了GPP，其中GPP最有用的特性，是在某些场景存储和使用凭据，其中包括：映射驱动
> ，创建本地用户数据源，打印机配置，创建/更新服务，计划任务，更改本地Administrator密码

此处的漏洞就是：为方便管理，网络管理员会使用域策略进行统一的配置和管理，那么所有机器的本地管理员密码就是一样的，造成了即使不知道密码的情况下也能修改组策略首选项的密码，也可以通过脚本破解组策略首选项文件中密码的漏洞。  
`post/windows/gather/credentials/gpp`

> 此模块可以获取组策略中的密码。注意，我们只需要获取域内任何一台以域用户权限登录的机器的权限即可。

因为我没有对靶机进行任何配置和管理，所以提权失败

![](./img/4534199268847235523.png)

PowerSploit中的Get-GPPPassword.ps1脚本可以获取组策略中的密码。  
`Import-Module .\Get-GPPPassword.ps1;Get-GPPPassword`

**防御策略** ：

  * 设置共享文件夹SYSVOL的访问权限
  * 将包含组策略密码的 XML 文件从 SYSVOL 目录中删除
  * 不要把密码放在所有域用户都有权访问的文件中
  * 如果需要更改域中机器的本地管理员密码，建议使用LAPS

值得一提的是微软在2014年修复了组策略首选项提权漏洞，使用的方法就是不再将密码保存在组策略首选项中。

## 总结

学习过windows提权之后，发现，好像提权使用的那么多工具和技巧，基本上都是基于msfconsole和PowerUp，其中，虽然系统配置的东西较多，但是我个人感觉都是比较鸡肋，利用条件比较苛刻。

## 参考

<https://cloud.tencent.com/developer/article/1771226>、  
<https://netsecurity.51cto.com/article/640572.html>  
<https://www.freebuf.com/articles/system/254836.html>  
<https://blog.csdn.net/god_zzZ/article/details/106334702>

