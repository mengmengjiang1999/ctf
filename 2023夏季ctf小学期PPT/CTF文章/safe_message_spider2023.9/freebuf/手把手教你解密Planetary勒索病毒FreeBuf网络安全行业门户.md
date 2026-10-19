## **一、背景概述**  

**近日，国外安全研究人员曝光了一种名为Planetary的勒索病毒家族，该勒索病毒家族最早于2018年12月被发现，使用AES-256加密算法加密文件，通常通过RDP爆破或垃圾邮件进行传播，重点攻击对象是使用英语的用户群体，但在中国和日本地区都发现了遭到攻击的用户。**  

该勒索软件家族在2019年进行过几次变种，加密后缀变化如下：

日期  |  后缀  
---|---  
2019.2.7  |  .pluto  
2019.2.10  |  .mecury  
2019.3.4  |  .Neptune  
2019.3.12  |  .yum  
2019.3.21  |  .mira  
  
2019年4月，EMSISOFT发布出Planetary勒索病毒的解密工具，该工具可以针对".mira", ".yum", ".Neptune",
".Pluto"后缀的变种进行解密。深信服安全团队对最新的Planetary样本进行了详细的技术分析，并对解密工具进行测试。

解密工具下载链接：

    
    
    https://decrypter.emsisoft.com/planetary

##  **二、勒索特征**

1.加密后文件后缀以“.mira”结尾：

![00.png](https://image.3001.net/images/20190409/1554797173_5cac527532df2.png!small)

2.勒索信息文件“!!!READ_IT!!!.txt”：

![01.png](https://image.3001.net/images/20190409/1554797176_5cac5278d8e7f.png!small)

##  **三、解密工具使用**

1.在被加密的主机上运行解密工具，会弹出许可条款，确认同意许可条款后点击“yes”按钮进入解密器：

![02.png](https://image.3001.net/images/20190409/1554797181_5cac527d59fa3.png!small)

2.点击“Browse”按钮选择一个释放勒索信息文件（”!!!READ_IT!!!.txt”），然后点击”start”按钮：

![03.png](https://image.3001.net/images/20190409/1554797184_5cac52806472a.png!small)

3.弹出风险提示，建议先尝试对少量文件进行解密，若能够成功解密再全盘使用：

![04.png](https://image.3001.net/images/20190409/1554797188_5cac52849614e.png!small)

4.选择需要解密的目录，”Addfolder”添加目录、“Remove objects”移除目录、“Clear object list”清空目录列表：

![05.png](https://image.3001.net/images/20190409/1554797191_5cac52877d4b1.png!small)

5.确认目录后，建议第一次尝试时在”Options”窗口中选择”Keep encrypted
files”选项，该选项的作用是解密时不删除被加密的文件，以防万一：

![06.png](https://image.3001.net/images/20190409/1554797195_5cac528b3e5dd.png!small)

6.解密完成后会在”Results”窗口输出解密日志，完成后即可查看文件是否成功解密，经测试，该工具对”.mira”后缀的Planetary勒索病毒能够成功解密：

![07.png](https://image.3001.net/images/20190409/1554797198_5cac528e4c21f.png!small)

##  **四、详细分析**

1.将病毒体通过注册表添加到自启动：

![08.png](https://image.3001.net/images/20190409/1554797201_5cac5291b5fdc.png!small)

2.设置对象属性，其中包含加密后的后缀名“.mira”，勒索信息文件名以及不进行加密的路径：

![09.png](https://image.3001.net/images/20190409/1554797205_5cac52951fdd1.png!small)

总共包含以下几项：

    
    
    buildHash："QAzNd93S1AE="
    
    extension：".mira"
    
    readmeFileName："!!!READ_IT!!!.txt"
    
    targetURL："<https://www.example.com/write.php?info=>"
    
    priorityDirs："Mercury4444"
    
    blacklistProcs："svchost"、"^explorer\\.exe$" 

**blacklistDirs** ：

    
    
    Common Files、InternetExplorer、Windows Defender、WindowsMail、Windows Media Player、WindowsMultimedia Platform、Windows NT、WindowsPhoto Viewer、Windows Portable Devices、WindowsPowerShell、Microsoft.NET、Windows Photo Viewer、Windows Security、Embedded Lockdown    Manager、Windows Journal、MSBuild、Reference Assemblies、Windows Sidebar、Windows Defender AdvancedThreat Protection、Users\\.*\\Microsoft$、Users\\.*\\Package Cache$、Users\\.*\\MicrosoftHelp$

 **blacklistFiles** ：

    
    
    "NTUSER\\.DAT.*"、"page.*\\.sys"、"swap.*\\.sys"、"\\.sys$"、"\\.dll$"

 **importantFiles** ：

    
    
    "\\.bak$"、"\\.4dd$"、"\\.4dl$"、"\\.accdb$"、"\\.accdc$"、"\\.accde$"、"\\.accdr$"、"\\.accdt$"、"\\.accft$"、"\\.adb$"、"\\.adb$"、"\\.ade$"、"\\.adf$"、"\\.adp$"、"\\.alf$"、"\\.ask$"、"\\.btr$"、"\\.cat$"、"\\.cdb$"、"\\.cdb$"、"\\.cdb$"、"\\.ckp$"、"\\.cma$"、"\\.cpd$"、"\\.crypt12$"、"\\.crypt8$"、"\\.crypt9$"、"\\.dacpac$"、"\\.dad$"、"\\.dadiagrams$"、"\\.daschema$"、"\\.db$"、"\\.db$"、"\\.db-shm$"、"\\.db-wal$"、"\\.db3$"、"\\.dbc$"、"\\.dbf$"、"\\.dbs$"、"\\.dbt$"、"\\.dbv$"、"\\.dbx$"、"\\.dcb$"、"\\.dct$"、"\\.dcx$"、"\\.ddl$"、"\\.dlis$"、"\\.dp1$"、"\\.dqy$"、"\\.dsk$"、"\\.dsn$"、"\\.dtsx$"、"\\.dxl$"、"\\.eco$"、"\\.ecx$"、"\\.edb$"、"\\.edb$"、"\\.epim$"、"\\.fcd$"、"\\.fdb$"、"\\.fic$"、"\\.fm5$"、"\\.fmp$"、"\\.fmp12$"、"\\.fmpsl$"、"\\.fol$"、"\\.fp3$"、"\\.fp4$"、"\\.fp5$"、"\\.fp7$"、"\\.fpt$"、"\\.frm$"、"\\.gdb$"、"\\.gdb$"、"\\.grdb$"、"\\.gwi$"、"\\.hdb$"、"\\.his$"、"\\.ib$"、"\\.idb$"、"\\.ihx$"、"\\.itdb$"、"\\.itw$"、"\\.jet$"、"\\.jtx$"、"\\.kdb$"、"\\.kexi$"、"\\.kexic$"、"\\.kexis$"、"\\.lgc$"、"\\.lwx$"、"\\.maf$"、"\\.maq$"、"\\.mar$"、"\\.marshal$"、"\\.mas$"、"\\.mav$"、"\\.mdb$"、"\\.mdf$"、"\\.mpd$"、"\\.mrg$"、"\\.mud$"、"\\.mwb$"、"\\.myd$"、"\\.ndf$"、"\\.nnt$"、"\\.nrmlib$"、"\\.ns2$"、"\\.ns3$"、"\\.ns4$"、"\\.nsf$"、"\\.nv$"、"\\.nv2$"、"\\.nwdb$"、"\\.nyf$"、"\\.odb$"、"\\.odb$"、"\\.oqy$"、"\\.ora$"、"\\.orx$"、"\\.owc$"、"\\.p96$"、"\\.p97$"、"\\.pan$"、"\\.pdb$"、"\\.pdb$"、"\\.pdm$"、"\\.pnz$"、"\\.qry$"、"\\.qvd$"、"\\.rbf$"、"\\.rctd$"、"\\.rod$"、"\\.rod$"、"\\.rodx$"、"\\.rpd$"、"\\.rsd$"、"\\.sas7bdat$"、"\\.sbf$"、"\\.scx$"、"\\.sdb$"、"\\.sdb$"、"\\.sdb$"、"\\.sdb$"、"\\.sdc$"、"\\.sdf$"、"\\.sis$"、"\\.spq$"、"\\.sql$"、"\\.sqlite$"、"\\.sqlite3$"、"\\.sqlitedb$"、"\\.te$"、"\\.teacher$"、"\\.tmd$"、"\\.tps$"、"\\.trc$"、"\\.trc$"、"\\.trm$"、"\\.udb$"、"\\.udl$"、"\\.usr$"、"\\.v12$"、"\\.vis$"、"\\.vpd$"、"\\.vvv$"、"\\.wdb$"、"\\.wmdb$"、"\\.wrk$"、"\\.xdb$"、"\\.xld$"、"\\.xmlff$"、"\\.bson$"、"\\.json$"、"\\.ldf$"、"\\.arm$"、"\\.cnf$"、"\\.dbs$"、"\\.ddl$"、"\\.frm$"、"\\.ibd$"、"\\.ism$"、"\\.mrg$"、"\\.myd$"、"\\.myi$"、"\\.mysql$"、"\\.opt$"、"\\.phl$"、"\\.sal$"、"\\.sqr$"、"\\.tmd$"、"\\.arz$"、"\\.ibz$"、"\\.ibc$"、"\\.qbquery$"、"\\.rul$"

 **readmeText** ：

    
    
    "                   ALL YOUR DATA WASENCRYPTED\r\n\r\nIf you want to recover your data:\r\n\r\n1.Send your personalID to our emails.\r\n2.You can send us 1 small    file for test decryption.\r\n3.After payment you will get decryption tool and opportunity to recover allyour data.\r\n\r\n\r\n To avoid file loss, do not try to rename or modifyencrypted files.\r\n \r\n Our contacts:\r\n\r\nrecoverymydata@protonmail.com\r\nrecoverydata@india.com\r\n\r\n                      Your personalID:\r\n\t\t\t\t   \r\n";

3.在遍历的每个目录下释放勒索信息文件“!!!READ_IT!!!.txt”：

![10.png](https://image.3001.net/images/20190409/1554797223_5cac52a76b49f.png!small)

4.设置加密模式：

![11.png](https://image.3001.net/images/20190409/1554797227_5cac52ab3aca2.png!small)

5.遍历除指定目录外的所有路径：

![12.png](https://image.3001.net/images/20190409/1554797231_5cac52af5b954.png!small)

6.加密文件：

![13.png](https://image.3001.net/images/20190409/1554797234_5cac52b29e332.png!small)

##  **五、解决方案**

针对已经出现勒索现象的用户，建议尽快对感染主机进行断网隔离，下载解密工具进行解密，解密工具下载链接如下：

    
    
    https://decrypter.emsisoft.com/planetary

深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

##  **病毒防御**

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.及时给电脑打补丁，修复漏洞。

2.对重要的数据文件定期进行非本地备份。

3.不要点击来源不明的邮件附件，不从不明网站下载软件。

4.尽量关闭不必要的文件共享权限。

5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。

6.如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！

7.深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。

8.深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果。

9.使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

