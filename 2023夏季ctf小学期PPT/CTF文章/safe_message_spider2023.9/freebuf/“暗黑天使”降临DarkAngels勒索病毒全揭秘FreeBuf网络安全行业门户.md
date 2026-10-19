## **恶意文件分析**

###  **恶意文件描述**

近期，深信服深盾终端实验室在运营工作中发现了一种 ELF 格式的勒索软件，该勒索软件近期开始出现，其释放的勒索信中的 Onion
链接似乎已关闭，这表明该勒索软件可能仍在开发中。

经过分析，发现该勒索软件与今年5月出现的 DarkAngels 勒索信内容非常相似。而 DarkAngels 与 Babuk 勒索软件也存在相似之处。
**本文主要分析最新捕获的针对 Linux 平台的 ELF 格式的勒索软件以及针对 Windows 平台的 DarkAngels
两种格式的样本，探究其中的相似与不同之处。**

左图为针对 Linux 系统下的勒索信内容，右图为针对 Windows 系统下的勒索信内容。

![](https://image.3001.net/images/20220921/1663724738_632a6cc2c6a016bc59500.png!small)

###  **恶意文件分析**

## （一）Windows 版本分析

总体功能框架

  

![图片](https://image.3001.net/images/20220921/1663724776_632a6ce83cc74bdb7871a.png!small)

使用静态分析，发现恶意文件是基于 32 位 GUI （图形用户界面）的二进制文件。

![](https://image.3001.net/images/20220921/1663724792_632a6cf8ebb6623d785c2.png!small)

获取命令行参数，通过调用 SetProcessShutdownParameters(0,0) ,恶意软件为指定进程设置它相对于其它程序的关闭顺序，参数为
0，意味着较其他进程关闭得最迟。

![](https://image.3001.net/images/20220921/1663724804_632a6d04d45fcb87f19b1.png!small)

 **终止服务**

为了确保在系统加密过程中不中断其加密过程，恶意软件会枚举和检索受害者机器上所有可用的服务，在加密系统之前尝试终止服务。

打开服务控制管理器数据库 (0xF003F = SC_MANAGER_ALL_ACCESS)。

![](https://image.3001.net/images/20220921/1663724817_632a6d1186f7419fd47ea.png!small)

调用 OpenServiceA，打开一个目标服务(0x2c = SERVICE_STOP )。

![](https://image.3001.net/images/20220921/1663724844_632a6d2caa860eb366f5c.png!small)

查询服务状态，判断上一步骤参数是否正确传递。

![](https://image.3001.net/images/20220921/1663724856_632a6d387a3e36d2e4532.png!small)

检索每个依赖于指定服务的服务的名称和状态;也就是说，在依赖服务能够运行之前，指定的服务必须运行 (0x1 =
SERVICE_ACTIVE)。![](https://image.3001.net/images/20220921/1663724868_632a6d446765733253a26.png!small)

终止服务 (0x1 = SERVICE_CONTROL_STOP)。

![](https://image.3001.net/images/20220921/1663724879_632a6d4fc219a17293f13.png!small)

终止的服务列表

![](https://image.3001.net/images/20220921/1663725235_632a6eb3da95195aeb146.png!small)

 **终止进程**

函数 CreateToolhelp32Snapshot() 获得当前运行进程的快照后，我们可以利用 process32First
函数来获得第一个进程的句柄。![](https://image.3001.net/images/20220921/1663725255_632a6ec7d97ea3332fed6.png!small)

将当前进程与硬编码中的进程表对比，如果当前进程句柄与表中匹配。则打开指定进程的句柄，并传入 0x1 参数(0x1 =
PROCESS_TERMINATE)，随后终止进程，最后关闭该进程句柄。

![](https://image.3001.net/images/20220921/1663725563_632a6ffbb720091cf1ad4.png!small)

继续枚举下一个进程。

![](https://image.3001.net/images/20220921/1663725584_632a701046a0bd7804c6a.png!small)

重复上述操作，直至遍历完所有进程。

终止进程列表

![](https://image.3001.net/images/20220921/1663725621_632a70358493bf9dc454c.png!small)

 **防止恢复**

（1）删除卷影

![](https://image.3001.net/images/20220921/1663725638_632a704605ec1da09395c.png!small)

（2）清空回收站

使用 SHEmptyRecycleBinA() API，恶意软件会从回收站中删除所有项目，以确保加密后不会恢复已删除的文件。

![](https://image.3001.net/images/20220921/1663725659_632a705b4e120f8c5c184.png!small)

 **最大化执行加密操作**

首先创建互斥变量 DarkAngels：

![](https://image.3001.net/images/20220921/1663725697_632a7081c5118e56c5aaf.png!small)

（1）当命令行参数中包含"shares"

使用 NetShareEnum () API 检索有关服务器上每个共享资源的信息。

![](https://image.3001.net/images/20220921/1663725714_632a709262ef85019ed82.png!small)

检查 $ADMIN 共享并开始加密文件：

![](https://image.3001.net/images/20220921/1663725725_632a709db1d7f40f55dce.png!small)

（2）当命令行参数中包含 "path"

勒索软件会调用 GetDriveTypeW() API 来找出连接到受感染机器的网络驱动器。一旦识别出网络驱动器，勒索软件就会开始加密文件。

![](https://image.3001.net/images/20220921/1663725745_632a70b14aa654e2ec8ea.png!small)

（3）当命令行参数中既不包含 "shares"又不包含 "paths"

勒索软件会递归遍历所有本地驱动器并加密所有目标文件。加密后，文件被赋予 .crypt 扩展名。

遍历所有本地驱动器![图片](https://image.3001.net/images/20220921/1663725805_632a70edb25ede1d3f8e2.png!small)

枚举卷及本地磁盘

获取驱动器类型，判断路径是否有效GetDriveTypeW(0x1)，如果路径有效，则对卷进行枚举。调用
GetVolumePathNamesForVolumeName 获取路径信息，查看该卷是否被安装，若未被安装，则调用SetVolumeMountPointW
安装未被安装的卷。

![](https://image.3001.net/images/20220921/1663725820_632a70fc6e6b3d46424d4.png!small)

枚举网络资源

![](https://image.3001.net/images/20220921/1663725837_632a710d7514a3885123c.png!small)![](https://image.3001.net/images/20220921/1663725855_632a711f68bf56c6c3530.png!small)

文件加密

（1）被加密文件添加扩展

调用 SetFileAttributesW(0x80 = FILE_ATTRIBUTE_NORMAL )
设置文件属性，取消文档的只读、隐藏、系统、存档权限。调用 MoveFileExW 函数，被加密文件添加扩展 .crypt。

![](https://image.3001.net/images/20220921/1663725868_632a712cb0e7f45ab50a9.png!small)

调用CreateFileW(0xC0000000 = GENERIC_READ | GENERIC_WRITE,0x3 =
OPEN_EXISTING)，打开一个已经存在的文件。

![](https://image.3001.net/images/20220921/1663725878_632a71368fe6686b10303.png!small)

（2）处理密钥

调用 CryptGenRadom 随机生成 AES 密钥，之后使用Session Key 中的 RSA 公钥对 AES 密钥进行加密。

![](https://image.3001.net/images/20220921/1663725888_632a7140f1b800befbc5b.png!small)

（3）文件加密大小

从文件头部开始遍历文件，先加密 0-64，接着加密 64-5242880，其次加密 5242880-20971520，最后加密20971520 之后的字符。

![](https://image.3001.net/images/20220921/1663725905_632a715184eee0501bb8d.png!small)

（3）不进行加密的文件、目录及扩展

不进行加密的目录：

AppData

|

Boot  
  
---|---  
  
Windows

|

Windows.old  
  
不进行加密的文件：

autorun.inf

|

boot.ini

|

bootfont.bin  
  
---|---|---  
  
不进行加密的文件扩展：

.babyk 是著名的 Babuk 勒索软件扩展名，表明 DarkAngels 与 Babuk 勒索软件可能存在关联。

.exe

|

.dll

|

.babyk  
  
---|---|---  
  
DarkAngels 在加密文件的末尾附加了一个签名 "choung dong looks like hot dog！！"，表明该勒索软件与 Babuk
相关。

![](https://image.3001.net/images/20220921/1663725993_632a71a91f9ca778ce761.png!small)

## （二）Linux版本分析

总体功能框架![](https://image.3001.net/images/20220921/1663726246_632a72a68af47e2a0c923.png!small)

1、定制化加密路径

该勒索软件二进制文件需要一个文件夹作为加密参数。给定文件夹路径后，DarkAngels 会加密文件夹中的文件并将 .crypted
扩展名附加到加密文件中。如果没有添加需要加密的路径，则会显示 Usage:%s [-m (10-20-25-33-50) ] Start Path 。

![图片](https://image.3001.net/images/20220921/1663726306_632a72e2ae4e9d317dd4f.png!small)

该恶意程序使用 pthread_create 函数创建了一个新的线程，新的线程通过调用 start_routine 执行主模块。

![图片](https://image.3001.net/images/20220921/1663726317_632a72ed5bbd580a7d38b.png!small)

start_routine 函数为该勒索软件主要功能模块，分析内容如下所示：

（1）被加密文件添加文件扩展 .crypted

  

![图片](https://image.3001.net/images/20220921/1663726342_632a73069a45555c8bc5f.png!small)

（2）将添加过 .crypted 扩展的文件设置写锁

调用 open64 函数打开目标文件，并且使用 fcnt 函数将目标文件设置为 F_WDLCK 写锁，随后 close 关闭目标文件。

![图片](https://image.3001.net/images/20220921/1663726353_632a7311c6f9c77ae022c.png!small)

（3）终止进程

终止 pid>10 且占用文件的进程，尽可能多的加密文件且避免在加密过程中造成文件的损坏。

![图片](https://image.3001.net/images/20220921/1663726364_632a731c75e2b193d57fc.png!small)

（4）将进程的工作目录修改为"/"根目录，创建守护进程。

![图片](https://image.3001.net/images/20220921/1663726375_632a7327961d42f6b472b.png!small)

（5）勒索信

打开另一个与目标文件同名但附加了README_TO_RESTORE 扩展的文件，写入了勒索信内容并关闭文件。

![图片](https://image.3001.net/images/20220921/1663726385_632a733158784b323cd99.png!small)

写入的勒索信内容如下所示：

![图片](https://image.3001.net/images/20220921/1663726397_632a733dc0e91b4b751ed.png!small)

（6）避免加密的文件扩展、目录、文件

不进行加密的文件扩展：

![图片](https://image.3001.net/images/20220921/1663726409_632a7349b70005aeb5e42.png!small)

不进行加密的目录：

![图片](https://image.3001.net/images/20220921/1663726421_632a73557cf8ced28b9e4.png!small)

不进行加密的文件：

![图片](https://image.3001.net/images/20220921/1663726528_632a73c0a58b9fe007f63.png!small)

（7）加密

打开被添加 .crypted 扩展的文件，调用 lseek 和 write 函数写入已加密的内容。

![图片](https://image.3001.net/images/20220921/1663726436_632a736482c7f4c6a59ee.png!small)

（8）加密记录

所有被加密文件存储在 wrkman.log.0 文件中。

![图片](https://image.3001.net/images/20220921/1663726453_632a73754bcfe26786c0e.png!small)

 **IOCs**

 **Windows 版本**

Sha256 38e05d599877bf18855ad4d178bcd76718cfad1505328d0444363d1f592b0838

 **Linux 版本**

Sha256 3b56cea72e8140a7044336933cf382d98dd95c732e5937a0a61e0e7296762c7b

##  **处置建议**

1\. 避免将重要服务在外网开放，若一定要开放，需增加口令复杂度，避免使用弱口令。

2\. 避免打开可疑或来历不明的邮件，尤其是其中的链接和附件等，如一定要打开未知文件，请先使用杀毒软件进行扫描。

3\. 安装信誉良好的防病毒/反间谍软件，定期进行系统全盘扫描，并删除检测到的威胁，按时升级打补丁。

4\. 使用官方和经过验证的下载渠道，使用正版开发人员提供的工具/功能激活和更新产品，不建议使用非法激活工具和第三方下载器，因为它们通常用于分发恶意内容。

5.重要的数据最好双机备份或云备份。

