##  概述

周末在家正在独自看电影的我，突然收到朋友发来的一张图片，就是下图展示的这个

![](https://image.3001.net/images/20191128/1574955152_5ddfe890a4c4a.jpg!small)

知名学习网站有打折！还终身会员！在强大的学习动力的驱使下我打开了浏览器，google了一下这个”学习网站”（完全不懂这是什么），打开一看，什(zheng)么(he)玩(ci)意(yi)，此处略去两个小时……

当我在搜索这个网站时，我还发现了一些其他的类似的“学习网站”，强大的好奇心再次驱使我“学习”。作为一名下载党，点击了页面上的一些按钮。当我去看下载的视频的时候，就发现怎么多了几个文件呢，也没多想，就双击了。但是双击后怎么没有反应呢，连续双击也不行，看了下后面的类型
--应用程序！蒙圈了三秒钟，还好是在虚拟机里。

看个视频还差点把我电脑沦陷了，想想就生气，所以务必得看看这个文件是什么东西。

在分析前，我习惯性把文件上传到微步的云沙箱简单看看，发现文件判定为恶意，还有创建可执行文件，自启动等行为

![](https://image.3001.net/images/20191129/1574994225_5de081313c0ed.png!small)![](https://image.3001.net/images/20191129/1574994231_5de081379149b.png!small)

使用PEid看了下，没有加壳，ida反编译也挺顺利，那干脆就调一调吧

##
![](https://image.3001.net/images/20191128/1574955180_5ddfe8acdf4c7.png!small)流程图

##
![](https://image.3001.net/images/20191128/1574955357_5ddfe95d172de.png!small)行为分析

样本首先获取系统版本号，并判断是否为win 2000以上的版本

![](https://image.3001.net/images/20191128/1574955402_5ddfe98ae703d.png!small)接着创建三个线程，循环执行一些恶意的操作

![](https://image.3001.net/images/20191128/1574955426_5ddfe9a22067b.png!small)

下面依次介绍一下这三个线程

###  线程一：StartAddress

枚举窗口，调用回调函数EnumFunc

![](https://image.3001.net/images/20191128/1574955457_5ddfe9c102b99.png!small)在回调函数中获取窗口名称，并判断是否在黑名单中，如果在就结束进程。黑名单进程大部分为反病毒软件。

![](https://image.3001.net/images/20191128/1574955476_5ddfe9d426f07.png!small)黑名单部分截图如下，详细信息请查看附录部分

![](https://image.3001.net/images/20191128/1574955497_5ddfe9e92212f.png!small)

###  线程二：DeleteService_4026B0

枚举服务，删除处于黑名单中的服务

![](https://image.3001.net/images/20191128/1574955518_5ddfe9fe1da2b.png!small)

###  线程三：TerminateProc_402830

遍历系统进程，同样结束处于黑名单中的进程

![](https://image.3001.net/images/20191128/1574955539_5ddfea13b359e.png!small)![](https://image.3001.net/images/20191128/1574955556_5ddfea24d2959.png!small)创建守护进程，如果子进程少于两个就创建自身进程

![](https://image.3001.net/images/20191128/1574955581_5ddfea3dddc5d.png!small)创建三个线程后，启动服务”Messenger”

![](https://image.3001.net/images/20191128/1574955608_5ddfea5805d44.png!small)接下来就是重头戏了，先检测文件mssrv.exe是否已经存在，通过判断能否找到此可执行文件和自启动项中是否存在来判断

![](https://image.3001.net/images/20191128/1574955628_5ddfea6c3701f.png!small)如果不存在就创建mssrv.exe并写入自身数据，然后实现持久化

![](https://image.3001.net/images/20191128/1574955652_5ddfea8403e99.png!small)

细节如下图所示：

写入mssrv.exe

![](https://image.3001.net/images/20191128/1574955676_5ddfea9c3bbc9.png!small)

创建自启动项

![](https://image.3001.net/images/20191128/1574955711_5ddfeabfd4679.png!small)遍历系统磁盘，将磁盘类型存放在数组中

![](https://image.3001.net/images/20191128/1574955731_5ddfead3dc405.png!small)接着会挨个检测磁盘的类型，如果磁盘类型为DRIVE_FIXED,DRIVE_REMOTE,
DRIVE_RAMDISK就进行感染行为，此感染行为包含本地感染和网络感染

![](https://image.3001.net/images/20191128/1574955753_5ddfeae96e74a.png!small)感染共享磁盘

![](https://image.3001.net/images/20191128/1574955777_5ddfeb01a3820.png!small)

感染本地磁盘，就是在这个环节，释放了令人面红耳赤的文件。样本会递归的遍历磁盘文件夹，并判断文件夹是否包含如下字符：tmp,download,temp,share,p2p,incoming，如果包含的话就拼接文件名，然后写入数据。

拼接文件名代码片段如下：

![](https://image.3001.net/images/20191128/1574955797_5ddfeb151e7ed.png!small)拼接所需的名称在文件中存储着，截取片段展示如下：

![](https://image.3001.net/images/20191128/1574955817_5ddfeb29ae209.png!small)在我的电脑上释放了一些如下名称的文件

![](https://image.3001.net/images/20191128/1574955837_5ddfeb3d1fc64.png!small)

由于本人英语不好，所以就google翻译了一下，这里我就不写了（免得发表不出来）。

系统默认是不展示文件后缀的，所以在关闭显示文件后缀的情况下，恶意文件是这么展示的

![](https://image.3001.net/images/20191128/1574955861_5ddfeb55a1bf5.png!small)

我个人觉得这个样本的作者不是一个完美主义的人，这里有一个瑕疵，就是文件的图标，这也太low了吧，稍微用点心，比如替换为类似下面这样的图标，那成功率不就稳稳上升了嘛。

![](https://image.3001.net/images/20191128/1574955888_5ddfeb7086773.png!small)言归正传，遍历完磁盘后，又将魔爪对准了网络资源，先是枚举网络资源

![](https://image.3001.net/images/20191128/1574955912_5ddfeb8848f52.png!small)如果找到目标，就进行感染，感染的方式和上述的一样

![](https://image.3001.net/images/20191128/1574955942_5ddfeba69e869.png!small)接下来还会感染互联网中的其他主机，样本在一个无限循环中生成随机数，然后将随机数拼接为ip![](https://image.3001.net/images/20191128/1574955961_5ddfebb9c5756.png!small)动态获取ICMP相关函数，使用这些函数来检测连通性

![](https://image.3001.net/images/20191128/1574955991_5ddfebd735ed9.png!small)如果可以连通，就利用老办法进行感染。

##
![](https://image.3001.net/images/20191128/1574956012_5ddfebeccadae.png!small)清理建议

清理方法也就是删除样本释放的可执行文件并清理系统驻留项，既然微步的云沙箱有了处置建议这个功能，我就直接贴图片了

![](https://image.3001.net/images/20191129/1574994290_5de08172444ab.png!small)

##  小结

至此，样本的行为已基本分析完成，从技术上讲，不是很难，但作者利用了一个最大的漏洞，那就是人性，一看就知道此乃性情中人。在此奉劝广大网友，珍爱生命，健康上网。

这个样本不是很难，感兴趣的朋友可以[下载](https://s.threatbook.cn/report/file/ae7839f4f21a19a829d57f0dec68b2c0e565d6694a9eb261ac156744f4bb302e/?sign=history&env=win7_sp1_enx86_office2013)分析练手

##  附录

"AGENTSVR","ANTI-TROJAN","ANTIVIRUS","ANTS","APIMONITOR","APLICA32","APVXDWIN","ATCON","ATGUARD",,"ATRO55EN",,"ATUPDATER",,"ATWATCH",,"**GUARD",,"**GNT","AUPDATE","AUTODOWN","AUTOTRACE","AUTOUPDATE","**CONSOL","**GSERV9","**LTMAIN","**PUPD","**SYNMGR","**WUPD32","**XQUAR","**protect9X","**WUPSRV","**WIN","BD_PROFESSIONAL","BIDEF","BIDSERVER","BIPCP","BIPCPEVALSETUP","BISP","BLACKD","BLACKICE","BOOTWARN","BORG","BORG2","BS120","CCAPP","CFGWIZ","CFIADMIN","CFIAUDIT","CFINET","CFINET32","CLEAN","CLEANER","CLEANER3","CLEANPC","CMGRDIAN","CMON016","CPF9X206","CPFNT206","CWNB181","CWNTDWMO","D3DUPDATE","DEFWATCH","DEPUTY","DPFSETUP","DRWATSON","DRWEBUPW","ESCANH95","ESCANHNT","ETrust","ESCANV95","FIREWALL",  
"FLOWPROTECTOR","FP-WIN_TRIAL","FS**","F-PROT","FPROT","FS**53","FS**95","GBMENU","GBPOLL","GUARD","HACKTRACERSETUP","HTLOG","HWPE","IAMAPP","IAMSERV","ICLOAD95","ICLOADNT","ICMON","ICSSUPPNT","ICSUPP95","ICSUPPNT","IFW2000","IPARMOR","IRIS","JAMMER","K**LITE","K**PERS","KERIO","KILLPROCESS","LOCKDOWN","LSETUP","LUALL","LUCOMSERVER","LUINIT","MCAGENT","MCUPDATE","MFW2EN","MFWENG3","MINILOG","MOOLIVE","MRFLUX","MSCONFIG","MSINFO32","N**80TRY","N**APW32","N**DX","N**STUB","N**W32","NC2000","NCINST4","NEOMONITOR","NETARMOR","NETINFO","NETMON","NETSCANPRO","NETSPYHUNTER","NETSTAT","NISSERV","NISUM","NORTON","NPFMESSENGER","NPROTECT","NSCHED32","NTVDM","NUPGRADE","NVARCH16","NWINST4","NWTOOL16","OSTRONET","OUTPOST","OUTPOSTINSTALL","OUTPOSTPROINSTALL","PADMIN","PANIXK","P**PROXY","PCC2K","PCCIOMON","PCDSETUP","PCFWALLICON","PDSETUP","PERISCOPE","PERSFW","PFWADMIN","PINGSCAN","POPROXY","POPSCAN","PORTDETECTIVE","PPINUPDT","PPTBC","PPVSTOP","PROCEXPLORERV","PROPORT","PROTECTX","PURGE","PVIEW","QCONSOLE","QSERVER","R**8WIN32ENG","RESCUE","RESCUE32","RRGUARD","RSHELL","RTVSCN95","RULAUNCH","SAFEWEB","SBSERV","SETUPVAMEEVAL","FLOWPROTECTOR","SGSSFW32","**SERVE","SHELLSPYINSTALL","SOFI","SPHINX","SPYXX","SS3EDIT","ST2","SUPFTRL","SUPPORTER5","SYMPROXYSVC","SYSEDIT","TASKMGR","TASKMON","TAUMON","TAUSCAN","TDS2-NT","TFAK5","TGBOB","TITANIN","TITANINXP","TRACERT","TRJSCAN","TRJSETUP","TROJANTRAP","UNDOBOOT","UPDATE","VBCMSERV","VBCONS","VBUST","VBWIN9X","VBWINNTW","VCSETUP","VFSETUP","VNLAN300","VNPC3000","VP**2","VPFW30S","VPTRAY","VSCENU6","VSECOMR","VSHWIN32","VSISETUP","VSMAIN","VSMON","VSSTAT","VSWIN9XE","VSWINNTSE","VSWINPERSE","W32DSM89","WATCHDOG","WEBSCANX","WHOSWATCHINGME","WINRECON","WRADMIN","WRCTRL","WSBGATE","XPF202EN","ZAPRO","ZAPSETUP3001","ZATUTOR","ZAUINST","ZONALM","ZONEALARM","ZLCLIENT","ANTIVIR","PANDA","KAPERSKY","CAISAFE","VETEBOOT","VETEFILE","VET-FILT","VETMONNT","VETMSGNT","VET-REC","MCAFEE","PROCESS  
VIEWER","BITDEFENDER","BIT-DEFENDER"  
---  
  
***本文原创作者：JustPlay，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

