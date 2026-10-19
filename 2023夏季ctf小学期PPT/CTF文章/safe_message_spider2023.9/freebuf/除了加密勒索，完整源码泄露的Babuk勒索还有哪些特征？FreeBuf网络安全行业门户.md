## **背景介绍**

近期Babuk勒索软件的完整源代码被泄露，据泄露源代码的黑客自称是想要改过自新，但是这一公开源代码的举动反而拉低了其他潜在犯罪团伙制作勒索软件的成本，后续是否会因此涌现更多的勒索软件不得而知。

Babuk勒索最早曝光于2021年初，让他们“一跃成名”的是在今年的4月份攻击了华盛顿大都会警察局，威胁不提交赎金将公开警方线人和其他敏感数据，并持续瞄准FBI、CSA等部门。但他们也并不是只针对执法机构，此前已攻击了多家大型企业和组织，如包括西班牙连锁手机零售商PhoneHouse和NBA休斯顿火箭队，一度成为2021年最活跃的勒索家族之一。![](https://image.3001.net/images/20210922/1632280332_614a9f0c4a4703819279a.jpg!small)图源于网络：Babuk公开的华盛顿大都会警察局被窃取的数据文件

##  **Babuk勒索软件特点**

深信服终端安全团队长期跟踪全球范围内的高级威胁，在海外攻击场景中捕获最新的Babuk勒索样本，在对该勒索软件进一步分析后，发现Babuk勒索软件除了会跟其他勒索家族一样加密文件外，还会窃取被攻击目标的数据，以威胁受害者支付赎金。

相比于其他勒索团伙，Babuk的使用了更加多样的攻击手法，包括：

1、利用APT攻击中常见的 **“白加黑”手段** 绕过静态检测；

2、使用 **自动化安装脚本批量投放** ，替代手动投放执行勒索；

3、运维 **不同平台的勒索病毒代码** ，具有针对Linux系统的勒索功能。

同时，该团伙的攻击过程非常有耐心， **潜伏时间相当长**
，可能达到两个月以上，因此在实施最后的攻击后往往会对受害者造成相当大的影响，目前深信服终端检测平台EDR已支持该勒索病毒的防护查杀。

##  **入侵手法：**

###  **C2连接工具**

C2连接工具由三个文件构成：![](https://image.3001.net/images/20210922/1632280400_614a9f5016aada7c35fe2.png!small)

其中GoogleUpdate.exe是带有Google数字签名的可执行程序，GoogleUpdate运行过程会加载goopdate.dll文件；![](https://image.3001.net/images/20210922/1632280418_614a9f62420e43f500b78.png!small)

而goopdate.dll则是被劫持的shellcode加载器，读取thumb.db中的shellcode并解码运行；![](https://image.3001.net/images/20210922/1632280441_614a9f79d8b063224b088.png!small)

安全专家对通过调试发现C2服务器地址为 103.79.77.242/Inform/registration/Q0FNEMDCNR9
，但该地址目前已无法连接。![](https://image.3001.net/images/20210922/1632280460_614a9f8cdff942ff4d117.png!small)![](https://image.3001.net/images/20210922/1632280469_614a9f952a062fabaaec0.png!small)

GoogleUpdate.exe+goopdate.dll属于利用白文件加载恶意程序以躲避杀毒软件检测的操作，可以从网上搜索到诸多案例。（注：海莲花APT也用过同样的手法）

##  **勒索批量安装脚本**

安全专家还发现一组勒索软件批量安装脚本，有下面三个文件：![](https://image.3001.net/images/20210922/1632280492_614a9fac23d8a0be8dda4.png!small)

e.txt中储存的是被勒索的主机IP地址![](https://image.3001.net/images/20210922/1632280501_614a9fb596325cd2f4721.png!small)

e.bat调用了e.vbs实现批量远程执行命令：![](https://image.3001.net/images/20210922/1632280517_614a9fc56381add8e83f9.png!small)

e.vbs的功能列表如下：![](https://image.3001.net/images/20210922/1632280532_614a9fd49441f992e0f4a.png!small)

e.vbs的脚本内容比较简单，首先使用net use
连接目标主机；![](https://image.3001.net/images/20210922/1632280547_614a9fe32c7bde3b5b233.png!small)

然后远程执行命令；![](https://image.3001.net/images/20210922/1632280563_614a9ff37a16b92d08525.png!small)

值得注意的是，该脚本还会将受害主机中的 C:/Windows/Temp
目录共享出去，方便传输文件等操作。![](https://image.3001.net/images/20210922/1632280585_614aa00960a21a25044d6.png!small)![](https://image.3001.net/images/20210922/1632280592_614aa010443dccba3128a.png!small)

##  **样本分析**

###  **Windows:**

程序首先执行勒索加密前准备，包括：

1.停止相关服务

2.结束相关进程

3.删除卷影副本

4.清空回收站![](https://image.3001.net/images/20210922/1632280615_614aa027bfee2e0b8db73.png!small)

Babuk勒索软件首先停止如下服务以保障加密顺利进行：

vss、sql、svc$、memtas、mepocs、sophos、veeam、backup、GxVss、GxBlr、GxFWD、GxCVD、GxCIMgr、DefWatch、ccEvtMgr、ccSetMgr、SavRoam、RTVscan、QBFCService、QBIDPService、Intuit、QuickBooks、FCS、QBCFMonitorService、YooBackup、YooIT、zhudongfangyu、sophos、stc_raw_agent、VSNAPVSS、VeeamTransportSvc、VeeamDeploymentService、VeeamNFSSvc、veeam、PDVFSService、BackupExecVSSProvider、BackupExecAgentAccelerator、BackupExecAgentBrowser、BackupExecDiveciMediaService、BackupExecJobEngine、BackupExecManagementService、BackupExecRPCService、AcrSch2Svc、AcronisAgent、CASAD2DWebSvc、CAARCUpdateSvc![](https://image.3001.net/images/20210922/1632280632_614aa038ce11296cb6d9e.png!small)

结束如下进程，避免数据文件被占用而无法加密：

sql.exe、oracle.exe、ocssd.exe、dbsnmp.exe、synctime.exe、agntsvc.exe、isqlplussvc.exe、xfssvccon.exe、mydesktopservice.exe、ocautoupds.exe、encsvc.exe、firefox.exe、tbirdconfig.exe、mydesktopqos.exe、ocomm.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe、notepad.exe![](https://image.3001.net/images/20210922/1632280648_614aa048d178c015a8d6e.png!small)

删除卷影副本：![](https://image.3001.net/images/20210922/1632280664_614aa058b15ded1940b99.png!small)

获取系统信息，然后根据处理器数量创建对应数量的加密线程：![](https://image.3001.net/images/20210922/1632280674_614aa0624983f8ce1a8ee.png!small)

跳过如下文件及文件夹：

AppData、Boot、Windows、Windows.old、Tor Browser、Internet
Explorer、Google、Opera、Opera Software、Mozilla、Mozilla
Firefox、$Recycle.Bin、ProgramData、All
Users、autorun.inf、boot.ini、bootfont.bin、bootsect.bak、bootmgr、bootmgr.efi、bootmg**.efi、desktop.ini、iconcache.db、ntldr、ntuser.dat、ntuser.dat.log、ntuser.ini、thumbs.db、Program
Files、Program Files
(x86)、#recycle、..、.![](https://image.3001.net/images/20210922/1632280707_614aa0833bf1fa932462c.png!small)

跳过".exe"、".dll"、".babyk"后缀的文件：![](https://image.3001.net/images/20210922/1632280717_614aa08def700bb29b86d.png!small)

将文件加上“.babyk”后缀后对其进行加密，加密算法采用了ECDH+HC-128：![](https://image.3001.net/images/20210922/1632280731_614aa09b3f651ebd7416f.png!small)

为了避免文件因被进程占用而无法加密，除了结束特定进程及服务外，Babuk还使用了Windows Restart Manager。Windows
Restart
Manager允许除关键系统服务外的所有程序或服务关闭和重启，从而可以减少或避免程序安装或者更新过程中需要重启的次数，Babuk利用其使文件可以被顺利加密。![](https://image.3001.net/images/20210922/1632280761_614aa0b9b02ab2dc6c0b4.png!small)

写入勒索信息：![](https://image.3001.net/images/20210922/1632280783_614aa0cf46ad3b0165be8.png!small)

###  **Linux:**

Linux版需要需要加上参数指定加密路径，加密结束后会输出不加密的文件、加密的文件、跳过的文件以及所有文件的数量和加密文件的数据量：![](https://image.3001.net/images/20210922/1632280803_614aa0e3b29b158708844.png!small)

对".log"、".vmdk"、".vmem"、".vswp"、".vmsn"后缀文件进行加密：![](https://image.3001.net/images/20210922/1632280814_614aa0ee62159c4b08384.png!small)

加密文件后加上".babyk"后缀，加密算法为ECDH+Sosemanuk：![](https://image.3001.net/images/20210922/1632280843_614aa10b90a3101f74313.png!small)

勒索信息与windows版相同：![](https://image.3001.net/images/20210922/1632280861_614aa11d358c8918e9198.png!small)

##  **日常加固**

1.日常生活工作中的重要的数据文件资料设置相应的访问权限，关闭不必要的文件共享功能并且定期进行非本地备份；

2.使用高强度的主机密码，并避免多台设备使用相同密码，不要对外网直接映射3389等端口，防止暴力破解；

3.避免打开来历不明的邮件、链接和网址附件等，尽量不要在非官方渠道下载非正版的应用软件，发现文件类型与图标不相符时应先使用安全软件对文件进行查杀；

4.定期检测系统漏洞并且及时进行补丁修复。

