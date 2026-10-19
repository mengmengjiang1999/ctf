REvil（又名Sodinokibi）勒索病毒团伙近期活跃度非常高，上个月才加密并窃取了某计算机巨头企业机密数据的REvil，在本月又入侵了苹果代工厂要价5000万美元，堪称勒索病毒界的“劳模”。

[《3.25 亿！REvil 勒索团伙又出动，深信服 EDR
来给用户打个“勒索病毒预防针”》](https://mp.weixin.qq.com/s/bpJkQVT1iE6YBCOfXyv8Vg "3.25
亿！REvil 勒索团伙又出动，深信服 EDR 来给用户打个“勒索病毒预防针”")

深信服终端安全团队一直对REvil勒索病毒团伙的技术应用和模式发展进行深度追踪，同时捕获到了本次攻击事件中的勒索病毒母体，通过技术分析发现，REvil在免杀技术上做了部分改进，
**母体和组件都伪造了数字签名，通过文件释放和DLL调用的方式分级触发，并通过多层payload解密才得到功能代码。**

除此以外分析人员发现，本次的病毒文件与此前针对国内企业的病毒文件还存在一些细节差异， **排除加密的目录关键字中不再包含"tencent
fies","wechat files"等中国普遍使用的软件目录。**

##  ** **技术分析****

REvil勒索病毒母体分为EXE和DLL两个部分，都先封装在一个名为svchost.exe的可执行文件中，三个文件都伪造了数字签名，其中svchost.exe和MpSvc.dll用了同样的伪造签名，而MsMpEng.exe则伪造了微软的签名：

![](https://image.3001.net/images/20210429/1619685164_608a6f2c3bca4f88bdd37.png!small)

双击运行svchost.exe后，会从资源中读取MsMpEng.exe和MpSvc.dll：

![](https://image.3001.net/images/20210429/1619685370_608a6ffa2cf6aef7784cc.png!small)

将两个文件释放到temp目录下，并调用cmd，利用/c参数后台执行MsMpEng.exe：

![](https://image.3001.net/images/20210429/1619685384_608a700854b65545a5678.png!small)

而MsMpEng.exe也没有实质性的恶意功能，只是加载了MpSvc.dll中的导出函数ServiceCrtMain()：

![](https://image.3001.net/images/20210429/1619685394_608a7012f35664423a4e3.png!small)

MpSvc.dll中解密了两层payload后开始执行恶意功能，首先从内存中解密出需要用到的字符资源合集：

![](https://image.3001.net/images/20210429/1619685415_608a7027b6f750f7b6dbe.png!small)

分别在HKEY_LOCAL_MACHINE\SOFTWARE和HKEY_LOCAL_USER\SOFTWARE下查找注册表项BlackLivesMatter的x4WHjRs值，若不存在该值，则生成7位加密后缀，随后创建该键值，值设置为加密后缀：

![](https://image.3001.net/images/20210429/1619685426_608a703294696819dc644.png!small)

采集基本的主机信息，包括用户名、主机名、磁盘类型以及注册表项的值：

    
    
    hKey = HKEY_LOCAL_MACHINE
    Subkey = "SYSTEM\CurrentControlSet\services\Tcpip\Parameters"
    ValueName = "Domain"
    
    
    hKey = HKEY_CURRENT_USER
    Subkey = "Control Panel\International"
    ValueName = "LocaleName"
    
    
    hKey = HKEY_LOCAL_MACHINE
    Subkey = "SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    ValueName = "productName"

创建互斥体，防止重复执行：

![](https://image.3001.net/images/20210429/1619685451_608a704b598fc5e805b07.png!small)

使用函数SHEmptyRecycleBinW清空回收站，并使用SetThreadExecutionState防止主机进入休眠状态：

![](https://image.3001.net/images/20210429/1619685467_608a705bd360454ac26d4.png!small)

为自身进程提权：

![](https://image.3001.net/images/20210429/1619685480_608a70688305c63768afd.png!small)

枚举出终端上的服务，查看服务名是否在以下列表中，有则进行删除：

    
    
    "svc": ["sophos",  "svc$", "sql", "mepocs", "vss", "backupбмукшефы", "veeam", "memtas"]

![](https://image.3001.net/images/20210429/1619685492_608a707435edb7d0aeae1.png!small)

遍历进程，查看是否存在以下进程，如有则终止：

    
    
    "prc":["allegro","steam","xtop","ocssd","xfssvccon","onenote","isqlplussvc","msaccess","powerpnt","cad","sqbcoreservice","thunderbird","oracle","infopath","dbeng50","pro_comm_msg","agntsvc","thebat","firefox","ocautoupds","winword","synctime","tbirdconfig","mspub","visio","sql","ocomm","orcad","mydesktopservice","dbsnmp","outlook","cadence","excel","wordpad","creoagent","encsvc","mydesktopqos"]

![](https://image.3001.net/images/20210429/1619685605_608a70e5840204723af06.png!small)

遍历目录进行加密，同时排除以下目录；与针对中国用户不同的是，排除的目录关键字中不再包含"tencent fies","wechat
files"等中国普遍使用的软件目录：

    
    
    "wht":{"fld":["google","windows.old","programdata","system volume information","application data","program files (x86)","intel","boot","$windows.~bt","tor browser","program files","windows","perflogs","$windows.~ws","msocache","appdata","mozilla"]

排除以下文件：

    
    
    "fls":["ntuser.ini","ntldr","bootmgr","ntuser.dat.log","ntuser.dat","thumbs.db","autorun.inf","bootfont.bin","desktop.ini","boot.ini","iconcache.db","bootsect.bak"]

排除以下后缀：

    
    
    "ext":["ldf","adv","shs","cmd","ico","msc","hlp","drv","lock","nls","theme","lnk","nomedia","diagcab","ics","bat","rtp","spl","wpx","idx","icl","dll","themepack","scr","msi","key","mpa","cab","prf","ps1","bin","msstyles","msu","cpl","ani","386","sys","diagpkg","exe","mod","rom","icns","hta","msp","ocx","diagcfg","cur","com","deskthemepack"]

在每个目录下释放勒索信息txt文件：

![](https://image.3001.net/images/20210429/1619685557_608a70b5aeebba5b33293.png!small)

加密后修改主机桌面为标志性的蓝色背景：

![](https://image.3001.net/images/20210429/1619685546_608a70aac22e4a01e26b8.png!small)

如果NET字段配置为True的时候（默认为false），将向C&C端发送受害主机基本信息和生成的Key，域名配置包含了1229个域名字符：

![](https://image.3001.net/images/20210429/1619685637_608a710533d536b48567c.png!small)

##  ** **加固建议****

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

