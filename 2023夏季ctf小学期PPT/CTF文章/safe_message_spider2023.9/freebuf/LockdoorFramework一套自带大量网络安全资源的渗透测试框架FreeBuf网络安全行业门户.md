![](https://image.3001.net/images/20191012/1570858787_5da16723638f8.gif!small)

## 博客&文章

> Reddit：【[
> _传送门_](https://www.reddit.com/r/cybersecurity/comments/d4hthh/lockdoor_a_penetration_testing_framework_with/)】
>
> Medium.com：【[ _传送门_](https://medium.com/@SofianeHamlaoui/lockdoor-framework-> a-penetration-testing-framework-with-cyber-security-resources-> sofiane-22fbb7942378)】
>
> Xploit Lab：【[ _传送门_](https://xploitlab.com/lockdoor-framework-penetration-> testing-framework-with-cyber-security-resources/)】
>
> Station X：【[ _传送门_](https://www.stationx.net/threat-intelligence-17th-> september/)】
>
> Kelvin Security ；【[
> _传送门_](https://blog.kelvinsecurity.com/2019/09/12/lookdoor-framework-a-> penetration-testing-framework-with-cyber-security-resources/)】
>
> All About hacking：【[ _传送门_](https://www.allabouthack.com/2019/09/lookdoor-> framework-penetration-testing.html)】
>
> Wired Intel ；【[
> _传送门_](http://wiredintel.bravehost.com/wired/2019/09/15/%F0%9F%94%90-lockdoor-> a-penetration-testing-framework-with-cyber-security-resources)】
>
> 油管频道：【[ _传送门_](https://www.%2A%2A%2A%2A%2A%2A%2A.com/watch?v=_agvb29FQrs)】

## 版本介绍

该项目目前仍处于v1.0 BETA测试版本开发阶段，因此使用过程中可能会出现bug，广大用户可以直接将问题反馈到项目的GitHub主页。

### 09/2019 :1.0 Beta

> -信息收集工具（21）
>
> -Web攻击工具（15）
>
> -逆向工程工具（15）
>
> -漏洞利用工具（6）
>
> -渗透测试&安全评估发现报告模板（6）
>
> -密码攻击工具（4）
>
> -Shell工具+Blackarch的Webshell**（4）
>
> -渗透测试辅助工具（3）
>
> -加密/解密工具（2）
>
> -社会工程学工具（1）
>
> -提权脚本&漏洞利用脚本
>
> -可在Kali、Ubuntu、Arch、Fedora、Opensuse和Windows（Cygwin）等平台上运行

![](https://image.3001.net/images/20191012/1570858799_5da1672fc5170.jpg!small)

### 09/2019:0.6

> -信息收集工具（13）
>
> -Web攻击工具（9）
>
> -修复了部分Bug
>
> -可在Kali、Ubuntu、Arch、Fedora、Opensuse和Windows（Cygwin）等平台上运行

![](https://image.3001.net/images/20191012/1570858820_5da1674412866.gif!small)

  

## 工具概述

LockDoor是一款自带大量网络安全资源的渗透测试框架，主要针对的用户群是渗透测试人员、漏洞赏金猎人以及网络安全工程师。该工具可以在Debian/Ubuntu/ArchLinux等基于Linux的发行版系统平台上运行，并且提供了大量目前社区热门或常用的渗透测试工具，以辅助研究人员完成渗透测试任务。对于渗透测试人员来说，很多人都有他们自己最中意的“/pentest”工具箱，而LockDoor这款框架同样可以帮助我们去构建这样的一个“军火库”。总而言之，LockDoor可以帮助我们以最高效的方式完成渗透测试任务。

## 工具安装

### 自动安装

    
    
    git clone <https://github.com/SofianeHamlaoui/Lockdoor-Framework.git> && cd Lockdoor-Framework
    
    chmod +x ./install.sh
    
    ./install.sh

### 手动安装

安装依赖组件：

    
    
    python python-pip python-requests python2 python2-pip gcc ruby php git wget bc curl netcat subversion jre-openjdk make automake gcc linux-headers gzip

安装Go环境：

    
    
    wget <https://dl.google.com/go/go1.13.linux-amd64.tar.gz>
    
    tar -xvf go1.13.linux-amd64.tar.gz
    
    mv go /usr/local
    
    export GOROOT=/usr/local/go
    
    export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
    
    rm go1.13.linux-amd64.tar.gz

安装LockDoor：

    
    
    # Clonnig
    
    git clone <https://github.com/SofianeHamlaoui/Lockdoor-Framework.git> && cd Lockdoor-Framework
    
    # Create the config file
    
    # INSTALLDIR = where you want to install Lockdoor (Ex：/opt/sofiane/pentest)
    
    echo "Location:"$installdir > $HOME"/.config/lockdoor/lockdoor.conf"
    
    # Moving the resources folder
    
    mv ToolsResources/* INSTALLDIR
    
    # Installing Lockdoor from PyPi
    
    pip3 install lockdoor

## LockDoor工具清单

###  **信息收集**

 **工具：**

> dirsearch：Web路径扫描器
>
> brut3k1t：暴力破解框架
>
> gobuster：采用Go开发的DNS和VHost农具
>
> Enyx：SNMP IPv6枚举工具
>
> Goohak：针对目标域名发起Google Hacking查询
>
> Nasnum：NAS枚举器
>
> Sublist3r：针对渗透测试的快速子域名枚举工具
>
> wafw00f：Web应用防火墙指纹识别工具identify
>
> Photon：针对开源情报收集的快速爬虫
>
> Raccoon：网络侦查与漏洞扫描工具
>
> DnsRecon：DNS枚举脚本
>
> Nmap：端口扫描&网络漏洞利用工具
>
> sherlock：社交网络用户名搜索工具
>
> snmpwn：SNMPv3用户枚举与攻击工具
>
> Striker：攻击信息与漏洞扫描器
>
> theHarvester：电子邮件、子域名与用户名收集工具
>
> URLextractor：信息收集&网站侦查工具
>
> denumerator.py：子域名枚举工具

 **框架:**

> ReconDog：网络侦查瑞士**
>
> RED_HAWK：多合一信息收集、漏洞扫描和网络爬取工具
>
> Dracnmap：信息收集框架

### Web攻击

 **工具：**

> Spaghetti：Spaghetti - Web应用安全扫描器
>
> CMSmap：针对CMS的扫描工具
>
> BruteXSS：XSS漏洞扫描器
>
> J-dorker：可从Bing爬取网站列表
>
> droopescan：针对CMS的扫描工具
>
> Optiva：Web应用程序扫描器
>
> V3n0M：采用Python 3.6开发的 SQLi/XSS/LFI/RFI漏洞扫描器
>
> AtScan：高级Dorck搜索与漏洞利用扫描器
>
> WPSeku：Wordpress安全扫描器
>
> Wpscan：采用Python开发的Wordpress扫描器
>
> XSStrike：高级XSS扫描器
>
> Sqlmap：SQL注入漏洞与数据库接管工具
>
> WhatWeb：下一代Web扫描器
>
> joomscan：Joomla漏洞扫描器

 **框架：**

> Dzjecter：服务器检测工具

### 权限提升

 **Linux脚本：**

> linux_checksec.sh
>
> linux_enum.sh
>
> linux_gather_files.sh
>
> linux_kernel_exploiter.pl
>
> linux_privesc.py
>
> linux_privesc.sh
>
> linux_security_test
>
> Linux_exploits folder

 **Windows Windows工具:**

> windows-privesc-check.py
>
> windows-privesc-check.exe

 **MySql工具:**

> raptor_udf.c
>
> raptor_udf2.c

### 逆向工程

> Radare2：类Unix逆向工程框架
>
> VirtusTotal：VirusTotal工具
>
> Miasm：逆向工程框架
>
> Mirror：文件字节分析工具
>
> DnSpy：.NET调试器和汇编器
>
> AngrIo：分析二进制代码的Python框架
>
> DLLRunner：智能DLL脚本执行工具
>
> Fuzzy Server：使用预制Spike脚本的服务器攻击工具
>
> yara：恶意软件样本分类工具
>
> Spike：一款协议模糊测试工具

### 漏洞利用

> Findsploit：本地/在线数据库漏洞扫描工具
>
> Pompem：漏洞利用与扫描工具
>
> rfix：RFI漏洞利用工具
>
> InUrlBr：高级搜索引擎
>
> Burpsuite：网络安全测试与扫描工具
>
> linux-exploit-suggester2：下一代Linux内核漏洞利用工具

### Shell

> WebShells：BlackArch的Webshell**
>
> ShellSum：本地Webshell防御检测工具
>
> Weevely：Web Shell武器库
>
> python-pty-shells：Python PTY后门

### 密码攻击

> crunch：字典生成器
>
> CeWL：自定义字典生成器
>
> patator：多功能爆破工具

### 加密&解密

> Codetective：判断加密算法和编码算法的工具
>
> findmyhash：利用在线服务破解哈希

### 社会工程学

> scythe：用户账户枚举工具

## 项目地址

> LockDoor：【[ _GitHub传送门_](https://www.freebuf.com/wp-> admin/post.php?post=216511&action=edit#id12)】

## 参考资料

> 1、Lockdoor Wiki主页：【[ _传送门_](https://github.com/SofianeHamlaoui/Lockdoor-> Framework/wiki)】
>
> 2、Lockdoor演示样例：【[ _传送门_](https://github.com/SofianeHamlaoui/Lockdoor-> Framework/wiki/Demos)】
>
> 3、Lockdoor工具截图：【[ _传送门_](https://github.com/SofianeHamlaoui/Lockdoor-> Framework/wiki/Screenshots)】

 *** 参考来源：[ _SofianeHamlaoui_](https://github.com/SofianeHamlaoui/Lockdoor-Framework)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**  

