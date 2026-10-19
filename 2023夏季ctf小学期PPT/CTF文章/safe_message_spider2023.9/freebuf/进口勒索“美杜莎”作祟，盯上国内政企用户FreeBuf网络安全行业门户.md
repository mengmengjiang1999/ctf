**近日，深信服安全团队接到一起勒索病毒入侵事件反馈，用户发现web服务器业务中断，立刻重启服务器后使用深信服EDR查杀隔离病毒，结束加密进程，及时止损。**

经分析，该勒索病毒名为Medusa Ransom，最早于2018年在国外活动，加密后会修改桌面背景为古希腊神话中蛇发女妖“美杜莎”的图片：  

![image001.png](https://image.3001.net/images/20190719/1563506076_5d31359c10cee.png!small)

加密文件的同时也加密文件名，并以.[medusa-decryptor@pm.me]作为后缀，释放勒索信息#DECRYPT MY FILES#.TXT：

![image002.png](https://image.3001.net/images/20190719/1563506085_5d3135a5c2218.png!small)

![image003.png](https://image.3001.net/images/20190719/1563506092_5d3135acac56f.png!small)

分析发现，该勒索病毒加密时是 **从Z** **-A** **遍历目录，并且优先加密数据库相关目录**
，正是由于这一特点，用户在发现WEB目录被加密，业务出现中断后立即进行响应查杀，成功避免服务器被全盘加密。

## **一、情报关联**

“美杜莎”是古希腊的蛇发女妖，传说凡看见她的眼睛者皆会被石化，国外勒索病毒作者喜好取其“石化”的含义来作为病毒的名称，早在今年2月，深信服安全团队曾报道过一款攻击政企用户的Gorgon勒索，也同样运用了“美杜莎”来作为标志：[《FilesLocker变种：Gorgon(蛇发女妖)勒索病毒感染政企系统》](https://mp.weixin.qq.com/s/X-vOWUe1HtCSJ-ygnY2vMg)

通过威胁情报关联，本次捕获的Medusa
Ransom最早于2018年10月就被编译，但相关的攻击活动却很少，仅在2018年11月国外论坛上出现过一例被勒索的求助信息：

![image004.png](https://image.3001.net/images/20190719/1563506100_5d3135b43dcce.png!small)

直至2019年7月，再次在国内某安全论坛上发现一例该勒索病毒的求助，由此推测，该勒索病毒的运营者很可能将目标转向了中国用户：

![image005.png](https://image.3001.net/images/20190719/1563506112_5d3135c02d57a.png!small)

本次攻击事件中与勒索病毒一同被发现的还有一枚后门程序，与勒索病毒一样在C:\Windows目录下伪装成“svchost.exe”，在对受害服务器进行排查时，排除了RDP暴力破解入侵的途径，推测该勒索病毒有通过后门投递的可能性:

![image006.png](https://image.3001.net/images/20190719/1563506125_5d3135cd3d0b3.png!small)

## **二、后门文件分析**

该文件采用动态解密数据和获取API的方式试图躲避检测，解密DLL文件释放到内存进行调用：

![image007.png](https://image.3001.net/images/20190719/1563506134_5d3135d68d155.png!small)

拷贝自身到C:\Windows目录，文件名以六个随机字母命名：

![image008.png](https://image.3001.net/images/20190719/1563506140_5d3135dc734c8.png!small)

创建服务，通过服务启动：

![image009.png](https://image.3001.net/images/20190719/1563506146_5d3135e2dbbe4.png!small)

该后门程序包含键盘记录功能：

![image010.png](https://image.3001.net/images/20190719/1563506153_5d3135e980ece.png!small)

连接域名“speedhacker.vicp.net”，端口2016，接收指令和传输数据：

![image011.png](https://image.3001.net/images/20190719/1563506169_5d3135f9cfc16.png!small)

同时在后门程序中发现一个C2域名为3600hk.no-ip.org，但并没有使用到，通过对该域名一顿“人肉”，在一条远控去后门的帖子中发现该域名的踪迹，原来是马中马的控制端：

![image012.png](https://image.3001.net/images/20190719/1563506176_5d31360070ac8.png!small)

##  **三、Medusa勒索病毒分析**

解密两次payload，第二次解密出来的是一个Delphi写的PE文件，跳转到入口点开始执行。该PE文件首先会调用cmd.exe将自身复制到%appdata%、svchost.exe：

![image013.png](https://image.3001.net/images/20190719/1563506307_5d3136836b135.png!small)

调用mshta.exe进程执行一段javascript，功能是将svchost.exe添加到注册表自启动：

![image014.png](https://image.3001.net/images/20190719/1563506313_5d313689103f0.png!small)

终止可能影响加密文件的进程：

    
    
    taskmgr.exe;ccleaner.exe;ccleaner64.exe;regedit.exe;anvir.exe;anvir64.exe;cscript.exe;wscript.exe;powershell.exe;procexp.exe;far.exe;agntsvc.exe;agntsvc.exeagntsvc.exe;agntsvc.exeencsvc.exe;agntsvc.exeisqlplussvc.exe;dbeng50.exe;dbsnmp.exe;excel.exe;firefoxconfig.exe;infopath.exe;isqlplussvc.exe;msaccess.exe;msftesql.exe;mspub.exe;mydesktopqos.exe;mydesktopservice.exe;mysqld.exe;mysqld-nt.exe;mysqld-opt.exe;ncsvc.exe;ocautoupds.exe;ocomm.exe;ocssd.exe;onenote.exe;oracle.exe;outlook.exe;powerpnt.exe;sqbcoreservice.exe;sqlagent.exe;sqlbrowser.exe;sqlserver.exe;sqlservr.exe;sqlwriter.exe;steam.exe;synctime.exe;tbirdconfig.exe;thebat.exe;thebat64.exe;thunderbird.exe;visio.exe;winword.exe;wordpad.exe;xfssvccon.exe;

跳过下列系统相关目录不进行加密：

    
    
    \$RECYCLE.BIN\;\All Users\;\AppData\;\Application Data\;:\System Volume Information\;:\Windows\; ALLUSERSPROFILE;APPDATA;ProgramData;WINDIR;

从Z开始向前遍历磁盘，优先遍历根目录下的下列目录进行加密：

    
    
    Microsoft\Exchange Server\;Microsoft SQL Server\;Firebird\;MSSQL.1\;Microsoft SQL Server Compact Edition\;Adobe\;Oracle\;Archive;Backup;Reserv;Restore;

遍历目录加密文件，并在每个目录释放勒索信息#DECRYPT MY FILES#.TXT：

![image015.png](https://image.3001.net/images/20190719/1563506318_5d31368ee03ec.png!small)

##  **四、解决方案**

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

###  **病毒防御**

再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.及时给电脑打补丁，修复漏洞。

2.对重要的数据文件定期进行非本地备份。

3.不要点击来源不明的邮件附件，不从不明网站下载软件。

4.尽量关闭不必要的文件共享权限。

5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6.如果业务上无需使用RDP的，建议关闭RDP。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

