![](https://image.3001.net/images/20210825/1629882540_612608acc767dbf978aeb.png!small)

## 概述

近期，安全研究人员发现了一种针对Microsoft
Exchange服务器的恶意软件，而且这款恶意软件甚至还可以执行Windows域加密。这款恶意软件名为LockFile，本质上它是一款勒索软件，当前变种主要利用的是ProxyShell漏洞。

## 关于LockFile勒索软件

根据研究人员透露的信息，七月份出现了一份与LockFile勒索软件有关的勒索信息，这份勒索信息其名称已标识为“LOCKFILE-README.hta”，但并没有其他的明显标记了。而这个勒索软件团伙从上周开始改变了他们的策略，并开始使用带有Logo的勒索信息，并自称他们名为LockFile。

“[victim_name]-LOCKFILE-README.hta”这种命名规范是网络犯罪分子在特定勒索信息中所采用的惯用命名约定，并在勒索信息中告知目标用户如何参与和进行赎金谈判。LockFile勒索软件团伙使用的邮件地址如下：contact@contipauper.com。

![](https://image.3001.net/images/20210825/1629882550_612608b6dfc0f0d0a1a16.png!small)

我们可以看到，勒索信息中所采用的颜色样式和电子邮件地址名称与Conti勒索软件相似。尽管如此，从攻击策略和写作方法来看，LockFile和Conti其实并无关联。

因为，LockFile不仅显示出与Conti的相似性，而且还显示出了与LockBit勒索软件的相似性。

新型的LockFile勒索软件使用了“.lockfile”作为被加密文件的后缀名。

那么，LockFile是如何使用ProxyShell漏洞的呢？根据赛门铁克的说法，网络犯罪分子可以利用ProxySheel漏洞访问Microsoft
Exchange的内部部署服务器，并利用[
_PetitPotam漏洞_](https://heimdalsecurity.com/blog/petitpotam-vulnerability-windows-domains/)接管目标Windows域。

## ProxyShell到底是什么？

ProxyShell实际上是由三个漏洞组成的，分为别[
_CVE-2021-34473_](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34473)、[
_CVE-2021-34523_](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2021-34523)和[
_CVE-2021-31207_](https://msrc.microsoft.com/update-guide/en-US/vulnerability/CVE-2021-31207)。前两个漏洞分别在4月份由[
_KB5*001779_](https://support.microsoft.com/en-us/topic/description-of-the-security-update-for-microsoft-exchange-server-2019-2016-and-2013-april-13-2021-kb5001779-8e08f3b3-fc7b-466c-bbb7-5d5aa16ef064)修复，最后一个漏洞在5月份由[
_KB5*003435_](https://support.microsoft.com/en-us/topic/description-of-the-security-update-for-microsoft-exchange-server-2019-2016-and-2013-may-11-2021-kb5003435-028bd051-b2f1-4310-8f35-c41c9ce5a2f1)修补。攻击者可以利用这些漏洞攻击Microsoft
Exchange，并在目标服务器上实现远程代码执行。

 **这三个漏洞所带来的危害如下：**

> 通过这些漏洞，攻击者可以绕过ACL检测；
>
> 攻击者可以在Exchange PowerShell后端实现提权；
>
> 攻击者可以在目标设备上实现任意代码执行；

通过利用这些ProxyShell漏洞，攻击者能够扫描并攻击Microsoft Exchange服务器，并在目标服务器上投放Web
Shell，然后实现恶意软件感染。

![](https://image.3001.net/images/20210825/1629882568_612608c811bf3e3f71227.png!small)

除此之外，研究人员还[ _发现_](https://doublepulsar.com/multiple-threat-actors-including-a-ransomware-gang-exploiting-exchange-proxyshell-vulnerabilities-c457b1655e9c)Lockfile勒索软件使用了ProxyShell漏洞和Windows
PetitPotam漏洞来在Windows域上执行加密任务。广大用户可以通过以下查询来扫描ProxyShell漏洞：

![](https://image.3001.net/images/20210825/1629882578_612608d2be182dd211e3a.png!small)

## 如何抵御Lockfile勒索软件？

为了缓解ProxyShell漏洞所带来的安全风险，我们建议广大用户尽快[ _更新自己的Microsoft
Exchange版本_](https://docs.microsoft.com/en-us/exchange/new-features/build-numbers-and-release-dates?view=exchserver-2019)。

为了缓解PetitPotam漏洞的影响，广大用户可以使用[
_0patch的补丁_](https://www.bleepingcomputer.com/news/security/new-unofficial-windows-patch-fixes-more-petitpotam-attack-vectors/)（这是一种非官方的漏洞环节措施）。

## 参考资料

> [ _https://www.bleepingcomputer.com/news/security/microsoft-exchange-> servers-being-hacked-by-new-lockfile-> ransomware/_](https://www.bleepingcomputer.com/news/security/microsoft-> exchange-servers-being-hacked-by-new-lockfile-ransomware/)
>
> [ _https://twitter.com/demonslay335_](https://twitter.com/demonslay335)
>
> [ _https://heimdalsecurity.com/blog/petitpotam-vulnerability-windows-> domains/_](https://heimdalsecurity.com/blog/petitpotam-vulnerability-> windows-domains/)
>
> [ _https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-34473_](https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-34473)
>
> [ _https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-34523_](https://msrc.microsoft.com/update-> guide/vulnerability/CVE-2021-34523)
>
> [ _https://msrc.microsoft.com/update-guide/en-> US/vulnerability/CVE-2021-31207_](https://msrc.microsoft.com/update-> guide/en-US/vulnerability/CVE-2021-31207)
>
> [ _https://support.microsoft.com/en-us/topic/description-of-the-security-> update-for-microsoft-exchange-> server-2019-2016-and-2013-april-13-2021-kb5*001779-8e08f3b3-fc7b-466c-bbb7-5d5aa16ef064_](https://support.microsoft.com/en-> us/topic/description-of-the-security-update-for-microsoft-exchange-> server-2019-2016-and-2013-april-13-2021-kb5001779-8e08f3b3-fc7b-466c-bbb7-5d5aa16ef064)
>
> [ _https://support.microsoft.com/en-us/topic/description-of-the-security-> update-for-microsoft-exchange-> server-2019-2016-and-2013-may-11-2021-kb5*003435-028bd051-b2f1-4310-8f35-c41c9ce5a2f1_](https://support.microsoft.com/en-> us/topic/description-of-the-security-update-for-microsoft-exchange-> server-2019-2016-and-2013-may-11-2021-kb5003435-028bd051-b2f1-4310-8f35-c41c9ce5a2f1)
>
> [ _https://www.bleepingcomputer.com/news/security/researchers-> earn-1-2-million-for-exploits-demoed-at-> pwn2own-2021/_](https://www.bleepingcomputer.com/news/security/researchers-> earn-1-2-million-for-exploits-demoed-at-pwn2own-2021/)
>
> [ _https://twitter.com/buffaloverflow_](https://twitter.com/buffaloverflow)
>
> [ _https://doublepulsar.com/multiple-threat-actors-including-a-ransomware-> gang-exploiting-exchange-proxyshell-> vulnerabilities-c457b1655e9c_](https://doublepulsar.com/multiple-threat-> actors-including-a-ransomware-gang-exploiting-exchange-proxyshell-> vulnerabilities-c457b1655e9c)
>
> [ _https://twitter.com/GossiTheDog_](https://twitter.com/GossiTheDog)
>
> [ _https://docs.microsoft.com/en-us/exchange/new-features/build-numbers-and-> release-dates?view=exchserver-2019_](https://docs.microsoft.com/en-> us/exchange/new-features/build-numbers-and-release-> dates?view=exchserver-2019)
>
> [ _https://www.bleepingcomputer.com/news/security/new-unofficial-windows-> patch-fixes-more-petitpotam-attack-> vectors/_](https://www.bleepingcomputer.com/news/security/new-unofficial-> windows-patch-fixes-more-petitpotam-attack-vectors/)
>
> [ _https://www.bleepingcomputer.com/news/microsoft/windows-petitpotam-> attacks-can-be-blocked-using-new-> method/﻿_](https://www.bleepingcomputer.com/news/microsoft/windows-> petitpotam-attacks-can-be-blocked-using-new-method/)

