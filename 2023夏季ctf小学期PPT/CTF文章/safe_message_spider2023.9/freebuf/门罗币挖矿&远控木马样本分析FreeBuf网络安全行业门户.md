**近日，威胁情报小组在对可疑下载类样本进行分析时，发现一起门罗币挖矿+木马的双功能样本。该样本回在执行挖矿的同时，通过C2配置文件，到指定站点下载具有远控功能的样本，获取受害主机信息，并进一步控制受害主机。**

##  **详细分析过程**

###  **样本主体**

样本主体文件采用的是360杀软的图标，并且文件描述信息为 “360主动防御服务模块”，诱导用户点击执行。

![image.png](https://image.3001.net/images/20190413/1555137260_5cb182ec9cb2c.png!small)

主体在执行时会释放拷贝自身到C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\SQLAGENTSA.exe，并继续执行。

![image.png](https://image.3001.net/images/20190413/1555137317_5cb18325343fe.png!small)

拷贝自身并继续执行

SQLAGENTSA.exe
会在本地释放并执行名称为“VBS.vbs”和“AutoRun.vbs”的两个vbs脚本，同时还会联网下载挖矿程序，并读取C2配置文件，下载木马文件继续执行。

![image.png](https://image.3001.net/images/20190413/1555137342_5cb1833eaea43.png!small)

VBS.vbs脚本内容

该脚本的目的就是为了确保进程“SQLAGENTSN.exe”会一直在运行。“AutoRun.vbs”脚本的内容和“VBS.vbs”脚本的内容很相似，目的也是为了确保进程“SQLAGENTSN.exe”会一直在运行。

###  **挖矿行为**

样本中存在如下硬编码文件路径：

![image.png](https://image.3001.net/images/20190413/1555137456_5cb183b065258.png!small)
登录站点可以发现，该站点为一个HFS下载站点：

![image.png](https://image.3001.net/images/20190413/1555137471_5cb183bf42d64.png!small)

针对cpu32.exe的文件进行分析，发现该文件实际是利用了开源代码XMRig2.11版本的门罗币挖矿程序。

![image.png](https://image.3001.net/images/20190413/1555137496_5cb183d8cdfeb.png!small)

该文件在下载到本地之后，本重命名为sqlagentc.exe，存放于C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\目录下，并被启动执行。

启动参数为：

    
    
    --donate-level 1 --max-cpu-usage 75 -o x.huineng.co:80 -u x.0309C -p x -k

![image.png](https://image.3001.net/images/20190413/1555137511_5cb183e78cd59.png!small)

sqlagentc.exe启动参数

同时在C:\DOCUME~1\ADMINI~1\LOCALS~1\Temp\目录下也发现了程序运行日志：

![image.png](https://image.3001.net/images/20190413/1555137526_5cb183f664ac3.png!small)

挖矿日志

其中CPU_log.txt 即为挖矿日志。

![image.png](https://image.3001.net/images/20190413/1555137543_5cb18407da5d9.png!small)由日志可以确认，矿池地址为
x.huineng.co:80 ip地址为 154.92.19.164。

###  **木马行为**

该样本主体除了载挖矿程序进行挖矿之外，还会直接读取<http://a.owwwa.com/mm/SQL.txt>文件的内容，从中获取木马文件地址，然后下载木马文件到本地继续执行。

![image.png](https://image.3001.net/images/20190413/1555137561_5cb1841953c69.png!small)

样本中硬编码的配置文件路径

![image.png](https://image.3001.net/images/20190413/1555137567_5cb1841f03093.png!small)

SQL.txt的内容

登录到站点上之后，发现该站点也是一个HFS下载站点，文件列表如下：

![image.png](https://image.3001.net/images/20190413/1555137577_5cb18429aca6e.png!small)

其中 **startas.bat** 脚本负责将SQLAGENTSON.exe创建为服务，并且以“System”账户运行。

![image.png](https://image.3001.net/images/20190413/1555137587_5cb18433afa83.png!small)

 **sqlbrowsers.exe** 会首先检查当前进程是不是以管理员权限运行，如果不是的话就以管理员权限再次启动进程，否则就解密并加载内存PE。

![image.png](https://image.3001.net/images/20190413/1555137595_5cb1843b5fcf1.png!small)

判断是不是管理员权限运行

![image.png](https://image.3001.net/images/20190413/1555137604_5cb18444b78f4.png!small)

加载内存DLL

内存DLL有一个导出函数StartAsFrameProcess，该DLL的主要功能都集中在这个函数中。

![image.png](https://image.3001.net/images/20190413/1555137613_5cb1844d56359.png!small)

该函数内会首先禁用UAC：

![image.png](https://image.3001.net/images/20190413/1555137627_5cb1845bf161f.png!small)

禁用UAC

然后下载新样本到磁盘根目录，并启动新样本。

![image.png](https://image.3001.net/images/20190413/1555137638_5cb184663ad25.png!small)
然后再次以服务的方式自启动，执行主要功能。

![image.png](https://image.3001.net/images/20190413/1555137648_5cb1847026df4.png!small)
主要功能有：监听、记录本机键盘数据并解密写入磁盘文件，获取本机安装的杀软信息，修改本级Host文件，解析、删除本机日志信息等。

![image.png](https://image.3001.net/images/20190413/1555137668_5cb1848400999.png!small)

![image.png](https://image.3001.net/images/20190413/1555137678_5cb1848e07424.png!small)

键盘记录并加密存储

![image.png](https://image.3001.net/images/20190413/1555137689_5cb1849982ef1.png!small)

获取主机杀软情况

 **关心的杀软列表如下：**

"360tray.exe"、"360安全卫士"、"360sd.exe"、"360杀毒"、"kxetray.exe"、"金山毒霸"、"KSafeTray.exe"、"金山安全卫士"、"QQPCRTP.exe"、"QQ电脑管家"、"BaiduSd.exe"、"百度杀毒"、;
"baiduSafeTray.exe"、"百度卫士"、"KvMonXP.exe"、"江民"、"RavMonD.exe"、"瑞星"、"QUHLPSVC.EXE"、"QuickHeal"、"mssecess.exe"、"微软MSE"、"cfp.exe"、"Comodo杀毒"、"SPIDer.exe"、"DR.WEB"、"acs.exe"、"Outpost"、"V3Svc.exe"、"安博士V3"、"AYAgent.aye"、"韩国胶囊"、"avgwdsvc.exe"、"AVG"、"f-secure.exe"、"F-Secure"、"avp.exe"、"卡巴"、Mcshield.exe"、"麦咖啡"、"egui.exe"、"NOD32"、"knsdtray.exe"、"可牛"、"TMBMSRV.exe"、"趋势"、"avcenter.exe"、"小红伞"、"ashDisp.exe"、"Avast网络安全"、"rtvscan.exe"、"诺顿"、"remupd.exe"、"熊猫卫士"、"vsserv.exe"、"BitDefender"、"PSafeSysTray.exe"、"PSafe反病毒"、"ad-watch.exe"、"Ad-watch反间谍"、"K7TSecurity.exe"、"K7杀毒"、"UnThreat.exe"、"UnThreat"。

![image.png](https://image.3001.net/images/20190413/1555137701_5cb184a56a0fb.png!small)修改主机Host文件

![image.png](https://image.3001.net/images/20190413/1555137722_5cb184ba22d04.png!small)![image.png](https://image.3001.net/images/20190413/1555137729_5cb184c1ee05c.png!small)

解析、删除操作系统日志

**SQLIOSIM** **.exe**
会在入口处使用RC4算法解密出内存PE，然后执行不同的功能，在执行的时候，会加载名为“Consys21.dll”的DLL文件，传入具体的功能描述信息，最后执行。

这些功能涉及：文件、注册表、进程、shell、音频、视频、屏幕、窗口、弹框、代理、DDOS开启，关闭等操作。

内存PE解密部分：

![image.png](https://image.3001.net/images/20190413/1555137746_5cb184d2e4a7f.png!small)

![image.png](https://image.3001.net/images/20190413/1555137754_5cb184dab78fb.png!small)

使用RC4解密内存PE

**主要功能部分：**

![image.png](https://image.3001.net/images/20190413/1555137761_5cb184e1ddda5.png!small)

文件操作

![image.png](https://image.3001.net/images/20190413/1555137768_5cb184e87484e.png!small)

注册表操作

![image.png](https://image.3001.net/images/20190413/1555137776_5cb184f078163.png!small)

进程操作

![image.png](https://image.3001.net/images/20190413/1555137787_5cb184fb09692.png!small)

shell操作

![image.png](https://image.3001.net/images/20190413/1555137792_5cb18500f1038.png!small)

音频操作

![image.png](https://image.3001.net/images/20190413/1555137800_5cb185086f164.png!small)

视频操作

![image.png](https://image.3001.net/images/20190413/1555137808_5cb18510cf978.png!small)

屏幕操作

![image.png](https://image.3001.net/images/20190413/1555137816_5cb185182f0ae.png!small)

窗口操作

![image.png](https://image.3001.net/images/20190413/1555137823_5cb1851fb4c9b.png!small)

弹框操作

![image.png](https://image.3001.net/images/20190413/1555137832_5cb18528898af.png!small)

代理操作

![image.png](https://image.3001.net/images/20190413/1555137840_5cb1853018e1e.png!small)

DDOS开启

![image.png](https://image.3001.net/images/20190413/1555137847_5cb18537b0343.png!small)

DDOS关闭

![image.png](https://image.3001.net/images/20190413/1555137854_5cb1853e902dd.png!small)

**SQLIOSIMSA** **.exe**
也是会加载内存PE，且PE为一个Dll文件，然后调用Dll文件的“DllFuUpgradrs”的导出函数执行主要功能，功能有：结束指定进程、修改硬盘MBR、删除指定文件、为系统添加账户，开启3389等。

![image.png](https://image.3001.net/images/20190413/1555137870_5cb1854e18cf4.png!small)

加载内存PE

![image.png](https://image.3001.net/images/20190413/1555137879_5cb18557319ae.png!small)

![image.png](https://image.3001.net/images/20190413/1555137887_5cb1855fa0aed.png!small)

调用导出函数“DllFuUpgradrs”

以导出函数“DllFuUpgradrs”为入口，执行相应的功能。

![image.png](https://image.3001.net/images/20190413/1555137904_5cb185709b575.png!small)

结束指定进程

 **进程名称列表：**

    
    
    IEXPLORE.exe、360SE.exe、sogouexplorer.exe、Chrome.exe、Firefox.exe、Maxthon.exe、taskmgr.exe、regedit.exe、mmc.exe、mstsc.exe、QQ.exe、s.exe、cmd.exe。

![image.png](https://image.3001.net/images/20190413/1555137916_5cb1857cd94c7.png!small)

修改硬盘MBR

![image.png](https://image.3001.net/images/20190413/1555137927_5cb18587409f9.png!small)

删除指定文件

![image.png](https://image.3001.net/images/20190413/1555137933_5cb1858dbfe40.png!small)

为系统添加账户

![image.png](https://image.3001.net/images/20190413/1555137944_5cb18598beff3.png!small)

开启3389

##  **IOC**

### 样本主体：

    
    
    F7FFF1F9F7CB0D2E6A1F532515F1787A

> <http://owwwa.com/mm/cpu32.exe>
>
> <http://owwwa.com/mm/cpu64.exe>
>
> <http://owwwa.com/mm/amd32.exe>
>
> <http://owwwa.com/mm/amd64.exe>
>
> <http://owwwa.com/mm/nvidia.exe>
>
> <http://a.owwwa.com/mm/SQL.txt>
>
> <http://mingtian2016.gnway.cc:7089/ma/startas.bat>
>
> <http://mingtian2016.gnway.cc:7089/ma/sqlbrowsers.exe>
>
> <http://mingtian2016.gnway.cc:7089/ma/SQLIOSIMS.exe>
>
> <http://mingtian2016.gnway.cc:7089/ma/SQLIOSIMSA.exe>
>
> <http://124.112.49.52:7089/mm/starta.bat>
>
> <http://124.112.49.52:7089/mm/SqlWtsnt.exe>
>
> <http://124.112.49.52:7089/mm/MsDtsSrvs.exe>
>
> x.huineng.co:80

##  **关联分析**

###  **样本关联分析**

在样本分析过程中，依据一些代码特征可以断定远控部分为“大灰狼远控”修改而来，但代码那种依然留下了很多痕迹，主要有以下几点：

样本在内存PE解密部分使用的是RC4算法，而且初始字符串为“Mother360”，这一点和大灰狼远控一模一样。

![image.png](https://image.3001.net/images/20190413/1555137966_5cb185aeaa84d.png!small)

大灰狼远控源码

样本在监控键盘内容，加密写入磁盘时使用的加密算法是与0x62亦或，该方式也与大灰狼远控部分一模一样。

![image.png](https://image.3001.net/images/20190413/1555137975_5cb185b7b8374.png!small)

![image.png](https://image.3001.net/images/20190413/1555137979_5cb185bbbf034.png!small)

大灰狼远控源码

样本中使用了Consys21.dll模块，并且调用了该模块的导出函数实现关键功能，而大灰狼远控中也有该模块，而且均含有关键导出函数。

![image.png](https://image.3001.net/images/20190413/1555137985_5cb185c1e2d13.png!small)

大灰狼远控模块导出函数

### **关系人关联**

样本多次出现了一个邮箱EMail:xxxx@sina.com（但在实际通信中未见使用）

![image.png](https://image.3001.net/images/20190413/1555139648_5cb18c40b2e33.png!small)

样本中的邮箱信息

依据此邮箱可以关联到具体的个人信息：

![image.png](https://image.3001.net/images/20190413/1555139926_5cb18d560b4cf.png!small)

由其个人经历可以看出，此人是个工作比较久的windows开发人员，对Windows系统也比较了解，所以该远控有可能是该人在大灰狼远控的基础之上修改而来。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

