**近日，深信服安全团队捕获到针对国内企业的新型勒索病毒攻击事件，攻击者通过爆破获得跳板机权限后，利用全套黑客工具包对内网主机进行渗透，人工投放勒索病毒进行加密，该勒索病毒加密邮箱与后缀为硬编码的字符串“.[DeAdmin@cock.li].DEADMIN”，并在勒索信息文件中自命名为DEADMIN
LOCKER，该勒索暂无公开解密工具。**

![a.jpg](https://image.3001.net/images/20191016/15712211812365.jpg!small)

加密完成后在桌面及加密根目录释放勒索信息文件

> **病毒名称：** DEADMIN LOCKER
>
> **病毒性质：** 勒索病毒
>
> **影响范围：** 目前国内已有感染案例
>
> **危害等级：** 高危
>
> **传播方式：** 通过社会工程、RDP暴力破解入侵，并使用黑客工具包内网渗透

##  **病毒描述**

该勒索病毒主要利用全套黑客工具包对内网主机进行渗透，人工投放勒索病毒进行加密。在被勒索的主机上获取到攻击者留下的全套黑客工具包，包含从密码收集到远程登录等一系列内网渗透工具，可谓是一应俱全，其中包含较为小众的AutoMIMI、Lazy、rdp_con、gmer等工具，甚至包含名为!RDP的快捷方式，用于启动本地远程桌面连接：

![b.jpg](https://image.3001.net/images/20191016/15712212274387.jpg!small)

黑客工具包包含：

>  **密码抓取：** AutoMIMI、mimi、netpass64.exe、Lazy
>
> **内网扫描：** masscan、!PortScan、Advanced_Port_Scanner、NetworkShare
>
> **密码爆破：** NLBrute
>
> **远程工具：** psexec、!RDP、rdp_con
>
> **反杀软工具：** gmer、PCHunter64、PowerTool、PowerTool_64、ProcessHacker64

##  **勒索病毒入侵攻击流程：**

**1** **、** 本地提权后，使用mimikatz抓取主机密码，在此过程中，黑客写了自动化脚本launch.vbs来简化抓取密码的步骤。

![c.jpg](https://image.3001.net/images/20191016/15712213204534.jpg!small)

 **2** **、**
黑客将抓取到的密码加入后续的爆破字典中，原因是管理员一般会将多个服务器的密码设置成相同的，将本机密码加入字典，可以增大爆破的成功率。

![d.jpg](https://image.3001.net/images/20191016/15712213356639.jpg!small)

 **3** **、** 使用端口扫描器扫描内网中存活的IP，并筛选开放了445和3389端口的主机。

![e.jpg](https://image.3001.net/images/20191016/15712213492933.jpg!small)

 **4** **、** 对于开放了3389端口的主机，黑客直接使用NLBrute进行爆破用户名和密码。  

![f.jpg](https://image.3001.net/images/20191016/15712213643042.jpg!small)

 **5** **、** 对于只开放了445端口的主机，黑客通过爆破的方式获取主机的账号密码。  

![g.jpg](https://image.3001.net/images/20191016/15712213782555.jpg!small)

 **6** **、** 然后使用psexec上传脚本至目标主机并运行，开启RDP服务。  

![h.jpg](https://image.3001.net/images/20191016/15712213968744.jpg!small)

 **7** **、** 获取到以上爆破成功的主机后，使用rdp_con工具进行批量连接。  

![i.jpg](https://image.3001.net/images/20191016/15712214089797.jpg!small)

RDP连接到受害主机后，黑客会上传一系列反杀软工具，kill杀毒软件，最后运行勒索病毒进行勒索，至此，整个勒索入侵的流程完成。

##  **勒索病毒详细分析**

**1** **、** 勒索病毒文件使用UPX加壳，运行后首先调用了Winexec执行命令行删除磁盘卷影，用于防止用户恢复数据：

![j.jpg](https://image.3001.net/images/20191016/15712214257879.jpg!small)

**2** **、** 关闭如下服务，避免影响加密：

>
> vmickvpexchange、vmicguestinterface、vmicshutdown、vmicheartbeat、vmicrdv、storflt、vmictimesync、vmicvss、MSSQLFDLauncher、MSSQLSERVER、SQLSERVERAGENT、SQLBrowser、SQLTELEMETRY、MsDtsServer130、SSISTELEMETRY130、SQLWriter、MSSQL、SQLAgent、MSSQLServerADHelper100、MSSQLServerOLAPService、MsDtsServer100、ReportServer、TMBMServer、postgresql-x64-9.4、UniFi、vmms、sql-x64-9.4、UniFi、vmms

**3** **、** 遍历进程，结束下列进程，防止进程占用文件影响加密：

>
> sqlbrowser.exe、sqlwriter.exe、sqlservr.exe、msmdsrv.exe、MsDtsSrvr.exe、sqlceip.exe、fdlauncher.exe、Ssms.exe、sqlserv.exe、oracle.exe、ntdbsmgr.exe、ReportingServecesService.exe、fdhost.exe、SQLAGENT.exe、ReportingServicesService.exe、msftesql.exe、pg_ctl.exe、postgres.exe、UniFi.exe、sqlagent.exe、ocssd.exe、dbsnmp.exe、synctime.exe、mydesctopservice.exe、ocautoupds.exe、agntsvc.exe、agntsvc.exe、agntsvc.exe、encsvc.exe、firefoxconfig.exe、tbirdconfig.exe、ocomm.exe、mysqld.exe、mysqld-> nt.exe、mysqld-> opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thebat64.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe、erbird.exe、visio.exe、winword.exe、wordpad.exe

**4** **、** 生成秘钥，使用RSA算法加密AES秘钥，再使用AES算法加密文件：

![k.jpg](https://image.3001.net/images/20191016/15712214538780.jpg!small)

**5** **、** 在桌面创建一个勒索信息TXT文件，然后通过遍历在每个加密文件的根目录下释放一个勒索信息TXT文件：

![l.jpg](https://image.3001.net/images/20191016/15712214652249.jpg!small)

**6** **、** 遍历磁盘进行加密，并且对C盘下的目录单独进行判断，跳过系统目录：

![m.jpg](https://image.3001.net/images/20191016/15712214766870.jpg!small)

**7** **、** 加密完成后进行自删除：

![n.jpg](https://image.3001.net/images/20191016/1571221491457.jpg!small)

##  **解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。此外，小编提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

###  **1** **、** **病毒检测查杀：**

> （1）深信服终端检测响应平台（EDR）、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测。
>
> （2）深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

> <http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

###  **2** **、** **日常防御措施**

> （1）及时给电脑打补丁，修复漏洞；
>
> （2）对重要的数据文件定期进行非本地备份；
>
> （3）不要点击来源不明的邮件附件，不从不明网站下载软件；
>
> （4）尽量关闭不必要的文件共享权限；
>
> （5）更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃；
>
> （6）如果业务上无需使用RDP的，建议关闭RDP。

***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

