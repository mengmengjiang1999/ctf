## **背景**

近日，深信服安全团队捕获到针对国内企业的新型勒索病毒攻击事件，攻击者通过爆破获得跳板机权限后， **利用全套黑客工具包对内网主机进行渗透**
**，人工投放勒索病毒进行加密**
，该勒索病毒加密邮箱与后缀为硬编码的字符串“.[DeAdmin@cock.li].DEADMIN”，并在勒索信息文件中自命名为DEADMIN
LOCKER，该勒索暂无公开解密工具。

![病毒1.png](https://image.3001.net/images/20191017/1571280406_5da7d6162b965.png!small)  

在被勒索的主机上获取到攻击者留下的 **全套黑客工具包**
，包含从密码收集到远程登录等一系列内网渗透工具，可谓是一应俱全，其中包含较为小众的AutoMIMI、Lazy、rdp_con、gmer等工具，甚至包含名为!RDP的快捷方式，用于启动本地远程桌面连接：

![病毒2.png](https://image.3001.net/images/20191017/1571280473_5da7d6594cbcd.png!small)  

>  **密码抓取** ：AutoMIMI、mimi、netpass64.exe、Lazy  
>
>
>  **内网扫描** ：masscan、!PortScan、Advanced_Port_Scanner、NetworkShare
>
>  **密码爆破** ：NLBrute
>
>  **远程工具** ：psexec、!RDP、rdp_con
>
>  **反杀软工具** ：gmer、PCHunter64、PowerTool、PowerTool_64、ProcessHacker64

##  **入侵溯源分析案例**  

1.在捕获的某次攻击事件中，安全专家对多台加密主机的安全日志进行了分析排查，发现其中主机在勒索信息文件生成的时间节点，都存在内网某台主机（后文称为跳板机）的登录记录：  

![病毒3.png](https://image.3001.net/images/20191017/1571280634_5da7d6faeff6a.png!small)  

2.于是将调查的目标转向了跳板机，使用everything进行搜索排查，在该主机上发现了攻击者留下的工具包，其中包含大量内网扫描和远程工具：  

![病毒4.png](https://image.3001.net/images/20191017/1571280671_5da7d71fcddf6.png!small)3.根据跳板机的勒索信息生成时间，对安全日志进行分析，在安全日志中排查到一个公网IP：92.246.76.125，在深信服威胁情报中该IP被标记为恶意：  

![病毒5.png](https://image.3001.net/images/20191017/1571280690_5da7d7324b559.png!small)4.在这之前，跳板机一直有遭到外网发起的爆破攻击，并且在日志中找到了十余个成功登陆的IP地址，其中大部分根据威胁情报判断为恶意IP，由此看来，该主机早沦为黑产的攻击目标：  

![病毒6.png](https://image.3001.net/images/20191017/1571280741_5da7d7659f743.png!small)

##  **渗透工具分析**  

本地模拟还原黑客内网渗透行为画像：

1\. 本地提权后，使用mimikatz抓取主机密码，黑客也写了个自动化脚本launch.vbs来简化抓取密码的步骤。

![病毒7.png](https://image.3001.net/images/20191017/1571280822_5da7d7b6dc9e3.png!small)2\.
黑客将抓取到的密码加入后续的爆破字典中，原因是管理员一般会将多个服务器的密码设置成相同的，将本机密码加入字典，可以增大爆破的成功率。  

![病毒8.png](https://image.3001.net/images/20191017/1571280848_5da7d7d0efe5d.png!small)3\.
使用端口扫描器扫描内网中存活的IP，并筛选开放了445和3389端口的主机。  

![病毒9.png](https://image.3001.net/images/20191017/1571280872_5da7d7e85c26b.png!small)4.
对于开放了3389端口的主机，黑客直接使用NLBrute进行爆破用户名和密码。  

![病毒10.png](https://image.3001.net/images/20191017/1571280909_5da7d80d6f302.png!small)5\.
对于只开放了445端口的主机，黑客会首先会通过爆破的方式获取这些主机的账号密码。  

![病毒11.png](https://image.3001.net/images/20191017/1571280978_5da7d852da904.png!small)6\.
然后使用psexec上传一个脚本至目标主机并运行，开启RDP服务。  

![病毒12.png](https://image.3001.net/images/20191017/1571281075_5da7d8b3298fb.png!small)7\.
获取到以上爆破成功的主机后，就可以使用rdp_con工具来批量连接了。  

![病毒13.png](https://image.3001.net/images/20191017/1571281107_5da7d8d31bdec.png!small)RDP连接到受害主机后，黑客就会上传一系列反杀软工具，关闭杀毒软件，最后运行勒索病毒进行勒索，至此，整个勒索入侵的流程就完成了。  

##  **勒索病毒详细分析**  

1.勒索病毒文件使用UPX加壳，运行后首先调用了Winexec执行命令行删除磁盘卷影，用于防止用户恢复数据：  

![病毒14.png](https://image.3001.net/images/20191017/1571281206_5da7d9366d41f.png!small)

2.关闭以下服务，避免影响加密：

>
> vmickvpexchange、vmicguestinterface、vmicshutdown、vmicheartbeat、vmicrdv、storflt、vmictimesync、vmicvss、MSSQLFDLauncher、MSSQLSERVER、SQLSERVERAGENT、SQLBrowser、SQLTELEMETRY、MsDtsServer130、SSISTELEMETRY130、SQLWriter、MSSQL、SQLAgent、MSSQLServerADHelper100、MSSQLServerOLAPService、MsDtsServer100、ReportServer、TMBMServer、postgresql-x64-9.4、UniFi、vmms、sql-x64-9.4、UniFi、vmms

3.遍历进程，结束下列进程，防止进程占用文件影响加密：

>
> sqlbrowser.exe、sqlwriter.exe、sqlservr.exe、msmdsrv.exe、MsDtsSrvr.exe、sqlceip.exe、fdlauncher.exe、Ssms.exe、sqlserv.exe、oracle.exe、ntdbsmgr.exe、ReportingServecesService.exe、fdhost.exe、SQLAGENT.exe、ReportingServicesService.exe、msftesql.exe、pg_ctl.exe、postgres.exe、UniFi.exe、sqlagent.exe、ocssd.exe、dbsnmp.exe、synctime.exe、mydesctopservice.exe、ocautoupds.exe、agntsvc.exe、agntsvc.exe、agntsvc.exe、encsvc.exe、firefoxconfig.exe、tbirdconfig.exe、ocomm.exe、mysqld.exe、mysqld-> nt.exe、mysqld-> opt.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thebat64.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe、erbird.exe、visio.exe、winword.exe、wordpad.exe

4.生成秘钥，使用RSA算法加密AES秘钥，再使用AES算法加密文件：

![病毒15.png](https://image.3001.net/images/20191017/1571281243_5da7d95bae1cc.png!small)5.首先在桌面创建一个勒索信息TXT文件，然后遍历加密时在每个根目录下释放一个勒索信息TXT文件：  

![病毒16.png](https://image.3001.net/images/20191017/1571281268_5da7d974c53b8.png!small)

6.遍历磁盘进行加密，并且对C盘下的目录单独进行判断，跳过系统目录：  

![病毒17.png](https://image.3001.net/images/20191017/1571281306_5da7d99a3642e.png!small)7.加密完成后进行自删除：  

![病毒18.png](https://image.3001.net/images/20191017/1571281342_5da7d9be96d4a.png!small)

##  **解决方案**  

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

 ****病毒检测查杀**** **  
**

1、深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![病毒4-1.png](https://image.3001.net/images/20191017/1571281407_5da7d9ff8151e.png!small)

2、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：
>
> http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z
>
> 32位系统下载链接：
>
> http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z

**病毒防御**

1、及时给电脑打补丁，修复漏洞；

2、对重要的数据文件定期进行非本地备份；

3、不要点击来源不明的邮件附件，不从不明网站下载软件；

4、尽量关闭不必要的文件共享权限；

5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃；

6、如果业务上无需使用RDP的，建议关闭RDP；

7、当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散；

8、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御；

9、深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果；

10、深信服终端检测响应平台（EDR）支持识别市面上大多数的流行黑客工具，并具备主动拦截和禁止运行功能；深信服EDR客户，建议开启勒索防护功能，精准拦截勒索病毒；

11、使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁；

12、深信服推出安全运营服务，通过以“人机共智”的服务模式帮助用户快速扩展安全能力，针对此类威胁安全运营服务提供设备安全设备策略检查、安全威胁检查、相关漏洞检查等服务，确保第一时间检测风险以及更新策略，防范此类威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

  

![勒索病毒搜索指引.gif](https://image.3001.net/images/20191017/1571281467_5da7da3b3c2fe.gif!small)  

