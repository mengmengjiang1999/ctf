## 恶意文件简述

BlackCat 是第一个广为人知的用 Rust
编写的勒索病毒，该病毒带有一个加密配置，其中包含要终止的服务/进程列表、避免加密的目录/文件/文件扩展名列表以及来自受害者环境的被盗凭证列表。
**它会删除所有卷影副本，使用 CMSTPLUA COM 接口执行权限提升，并在受害者机器上启用“远程到本地”和“远程到远程”符号链接。**

##  **恶意文件分析**

###  **1.恶意文件描述**

近期，深信服深盾终端实验室在运营工作中发现一起勒索病毒事件，样本隶属家族 BlackCat。该家族最近几个月动作频频，下文将针对该样本进行详细分析。

BlackCat（又名 ALPHV）是一个勒索软件家族，BlackCat 采用勒索软件即服务 (RaaS)
商业模式，在已知的网络犯罪论坛中招揽附属公司，允许附属公司利用勒索软件并保留 80-90% 的赎金，其余部分将支付给 BlackCat
作者。其恶意软件本身是用 Rust 编程语言编写的。

 **BlackCat
采用三重勒索模式，不仅会加密数据、感染网络和系统，还会通过其他的工具进行窃取敏感数据，然后使用被盗数据勒索受害者支付要求的赎金，还会在他们的泄密网站上列出了部分受害者，如果不支付赎金，攻击者将在数据泄露站点上泄露被盗数据。而且如果受害者没有在最后期限支付赎金，他们还会进行分布式拒绝服务
(DDoS) 攻击。**

###  **2.恶意文件分析**

通过分析发现该样本使用 32
位不唯一的访问令牌进行启动，在程序启动初始阶段便会对参数进行强校验，样本通过正确参数启动后便会进行加密勒索操作，为加密后的文件添加后缀名
“.7dulptm”，提示信息文件名为 “RECOVER-7dulptm-FILES”，内容如下，通过该样本的勒索信息可以锁定勒索解密页面，当前还未有任何交互信息。

![](https://image.3001.net/images/20220823/1661222421_63043e15431b6b285b157.png!small)

 **网络行为**

暂未发现网络行为

 **行为分析**

该样本的行为如下所示

![](https://image.3001.net/images/20220823/1661222437_63043e2571bcbd4897790.png!small)

BlackCat
是一个命令行启动的勒索程序，该样本采用定制化的参数选项帮助攻击者轻松地配置程序执行过程。这些配置包括以子进程方式运行、拖拽启动、记录日志、是否探索
Windows 系统的共享网络、是否在 Windows 上繁殖传播、是否传播到未定义的服务器上、是否关闭 ESXI 虚拟机、是否删除 ESXI
虚拟机快照、是否更新 Windows桌面等等。

其中大多数参数是可选项，但是 --access-token 参数是必选的，用来绕过沙箱自动执行的动态分析。

![](https://image.3001.net/images/20220823/1661222454_63043e36e6963559a788a.png!small)

当该样本无参数启动或者以一个无效的 access token 启动时，控制台均会输出错误信息。

![](https://image.3001.net/images/20220823/1661222467_63043e4339e1f60a6f1c0.png!small)

根据配置，该样本使用 ChaCha20Aes 或 Aes 加密算法对文件进行加密。在自动模式下，软件会检测是否有 AES
硬件支持（存在于所有现代处理器中）并使用它。如果没有 AES 支持，软件会对文件进行 ChaCha20 加密。

![](https://image.3001.net/images/20220823/1661222479_63043e4fa67da44561d6c.png!small)

 **前期准备工作**

允许“远程到远程”文件共享：

fsutil behavior set SymlinkEvaluation R2R:1

![](https://image.3001.net/images/20220823/1661222620_63043edcd6c3a54ec98be.png!small)

关闭系统所有 Internet 服务：

![](https://image.3001.net/images/20220823/1661222572_63043eac53bda265c009b.png!small)

将注册表中网络请求服务器服务的值修改为最大即65535，这样能够避免在加密过程中因同时访问太多文件而出现的问题。

![](https://image.3001.net/images/20220823/1661222640_63043ef00a503381e9873.png!small)

 **信息收集**

1、通过注册表 SOFTWARE\\\Microsoft\\\Cryptography 来查询机器 Guid

![](https://image.3001.net/images/20220823/1661222653_63043efdbb941a63ec09d.png!small)

2、调用 WMI 获取主机目标设备的通用唯一标识符 UUID

![](https://image.3001.net/images/20220823/1661222665_63043f09533bffcc0d162.png!small)

3、在缓存中读取 IP 地址和 mac 地址的对应关系表

![](https://image.3001.net/images/20220823/1661222678_63043f167fc4e692fe6fa.png!small)

4、枚举磁盘驱动器

![](https://image.3001.net/images/20220823/1661222697_63043f297f5a72de0ee3b.png!small)

检索磁盘驱动器

![](https://image.3001.net/images/20220823/1661222712_63043f38ec23f97086247.png!small)

5、查询受害者系统的计算机名

![](https://image.3001.net/images/20220823/1661222724_63043f4423c02d21542eb.png!small)

6、查询计算机用户名

![](https://image.3001.net/images/20220823/1661222737_63043f51a64e0e20faab2.png!small)

7、查询 AD 域名

调用 SHTestTokenMenbership 函数，判断当前用户是否属于本域中的管理员组(0x220 =
DOMAIN_ALIAS_RID_ADMINS)，识别当前用户是否具有域管理员权限，以便加密更多的设备。

![](https://image.3001.net/images/20220823/1661222752_63043f60917eaa41b59c9.png!small)

调用 NtQueryInformationToken 函数检索与当前令牌 (0x2 = TOKEN_GROUPS )
关联的组账号，并且检查TOKEN_GROUPS 中是否包含管理员组：

![](https://image.3001.net/images/20220823/1661222763_63043f6b4931ba60327c4.png!small)

8、使用 net use 控制共享网络连接

![](https://image.3001.net/images/20220823/1661222775_63043f77d9a877dfd2567.png!small)

9、枚举文件

![](https://image.3001.net/images/20220823/1661222789_63043f85832e069c87948.png!small)

 **防御规避**

该样本为了避免数据的恢复及取证溯源工作，做了如下的工作：

1、该样本使用了 TLS 回调函数

![](https://image.3001.net/images/20220823/1661222800_63043f909d3db23f6673f.png!small)

2、命令行参数启动

该样本通过 GetCommandLineW 函数获取该程序的命令行参数

![](https://image.3001.net/images/20220823/1661222812_63043f9c1694042e72646.png!small)

3、关闭某些进程和服务

为了尽可能多得加密文件，避免文件被占用，勒索程序还会关闭一些进程和服务。配置中设置了需要关闭的进程列表和服务列表：

![](https://image.3001.net/images/20220823/1661222823_63043fa70ff1568aa78a8.png!small)

（1）关闭服务

调用 OpenScManagerW 查询服务控制管理数据库

![](https://image.3001.net/images/20220823/1661222836_63043fb4a6fd82f275bf9.png!small)

枚举服务存活状态的服务 (0x1 = SERVICE_ACTIVE)

![](https://image.3001.net/images/20220823/1661222856_63043fc86f66a8220d44c.png!small)

终止目标服务器 (0x1 = SERVICE_CONTROL_STOP)

![](https://image.3001.net/images/20220823/1661222870_63043fd6347bd72e0c5cd.png!small)

（2）关闭进程

枚举所有进程

![](https://image.3001.net/images/20220823/1661222886_63043fe6bd724c9285dcb.png!small)  
![](https://image.3001.net/images/20220823/1661222899_63043ff33c41999e6d410.png!small)

中断进程

![](https://image.3001.net/images/20220823/1661222910_63043ffe63a4feca0bf4e.png!small)

4、调用 vssadmin.exe 和 wmic 删除系统备份

![](https://image.3001.net/images/20220823/1661222923_6304400be4756d10528c4.png!small)

![](https://image.3001.net/images/20220823/1661222934_63044016235cca54c4ba0.png!small)

5、关闭系统 BCDedit 中的自动修复功能

![](https://image.3001.net/images/20220823/1661222946_6304402249d7b43f4b16a.png!small)

6、枚举服务器/客户端中所有的事件日志列表，然后清除系统中所有的事件日志

![](https://image.3001.net/images/20220823/1661222957_6304402d8b408191a66a1.png!small)

 **提权**

1、绕过 UAC

该恶意软件尝试使用 CMSTPLUA COM 接口绕过 UAC，如调用 CoInitializeEx 函数来初始化当前线程的COM 库 (0x2 =
COINIT_APARTMENTTHREADED)

![](https://image.3001.net/images/20220823/1661222972_6304403cb9ae36f966cbe.png!small)

调用 CoGetObject 函数，将显示名称修改并绑定为一个自提权 CMSTPLUA
的接口interfaceElevation:Administrator!new:{3E5FC7F9-9A51-4367-9063-A120244FBEC7}

![](https://image.3001.net/images/20220823/1661222984_63044048a4fd8fc58cd58.png!small)

从下图可以看出，初始低权限样本启动了一个提权后的“自己”，随后退出程序

![](https://image.3001.net/images/20220823/1661222996_630440541fa398d8e362d.png!small)

2、API 提权

获取当前进程的令牌句柄 (0x80000000 = GENERIC_READ)

![](https://image.3001.net/images/20220823/1661223010_6304406299b51c587765f.png!small)

查看系统权限 SeTakeOwnershipPriviledge 的特权值

![](https://image.3001.net/images/20220823/1661223021_6304406d6559406b500fc.png!small)

在指定的访问令牌 SeTakeOwnershipPriviledge 上启动该权限

![](https://image.3001.net/images/20220823/1661223032_63044078335d39156502e.png!small)

所有提升的权限如下所示：

SeIncreaseQuotaPrivilege,SeSecurityPrivilege,SeTakeOwnershipPrivilege,SeLoadDriverPrivilege,SeSystemProfilePrivilege,SeSystemtimePrivilege,SeProfileSingleProcessPrivilege,SeIncreaseBasePriorityPrivilege,SeCreatePagefilePrivilege,SeBackupPrivilege,SeRestorePrivilege,SeShutdownPrivilege,SeDebugPrivilege,SeSystemEnvironmentPrivilege,SeChangeNotifyPrivilege,SeRemoteShutdownPrivilege,SeUndockPrivilege,SeManageVolumePrivilege,SeImpersonatePrivilege,SeCreateGlobalPrivilege,SeIncreaseWorkingSetPrivilege,SeTimeZonePrivilege,SeCreateSymbolicLinkPrivilege,SeDelegateSessionUserImpersonatePrivilege

 **持久化**

为了避免影响系统和勒索软件的正常运行，对一些关键的系统、应用程序文件夹和一些关键组件不进行加密操作

1、配置中包含避免加密的文件扩展列表

themepack,nls,diagpkg,msi,Ink,exe,cab,scr,bat,drv",rtp","msp","prf","msc","ico","key","ocx","diagcab","diagcfg","pdb","wpx","hlp","icns","rom",dll","msstyles","mod","ps1","ics","hta","bin","cmd","ani","386","lock","cur","idx","sys","com",deskthemepack","shs","Idf","theme","mpa","nomedia","spl","cpl","adv","icl","msu

2、避免加密的文件夹，包括但不限于

systemvolume information, intel, $windows.~ws, application data, $recycle.bin,
mozilla, $windows.~bt, public, msocache, windows, default, all users, tor
browser, programdata, boot, config.msi, google, perflogs, appdata, windows.old

3、避免加密的文件名，包括但不限于

desktop.ini, autorun.inf, ntldr, bootsect.bak, thumbs.db, boot.ini,
ntuser.dat, iconcache.db, bootfont.bin, ntuser.ini, ntuser.dat.log

 **文件加密**

调用 BCryptGenRandom 函数生成 16 个随机字节，用来生成 AES 密钥

![](https://image.3001.net/images/20220823/1661223048_63044088bd1d5e6445f6e.png!small)

![](https://image.3001.net/images/20220823/1661223059_630440939f28dbab3967e.png!small)

从文件头开始遍历文件

![](https://image.3001.net/images/20220823/1661223072_630440a0cd29c23cf22f2.png!small)

被加密文件添加后缀

![](https://image.3001.net/images/20220823/1661223082_630440aa3e559d83f8e7a.png!small)

写入勒索信

![](https://image.3001.net/images/20220823/1661223093_630440b5be06e9d0cc7c6.png!small)

Json 格式文件包含 AES 加密算法，用于加密文件的 AES密钥，调用 BCryptGenRandom 函数生成 0x82(130)个随机字节，与
json 配置文件中的密钥总共占用缓冲区大小为256 字节

![](https://image.3001.net/images/20220823/1661223105_630440c1195a45daafb97.png!small)

调用 bcryptGenRandom 生成随机四字节，将被加密文件的内容与 AES 密钥使用四字节分开

![](https://image.3001.net/images/20220823/1661223116_630440cc39201f97f93dd.png!small)

包含 AES 密钥的缓冲区被配置文件中的 RSA 公钥加密，加密密钥大小为 0x100，写入文件，文件内容使用 aesenc and aesenclast
命令进行 AES-128 算法加密，使用writeFile 将加密后的内容写入文件

![](https://image.3001.net/images/20220823/1661223127_630440d7ab8c68f1e4829.png!small)

内嵌配置信息

![](https://image.3001.net/images/20220823/1661223143_630440e75e14be0fa64a1.png!small)

Json 配置中包含：

1、 被加密文件的扩展

2、 被AES密钥加密的RSA公钥

3、 勒索信名称和内容

4、 受害者环境被盗的凭据

5、 AES加密算法

6、 终止的服务和进程列表

7、 避免加密的文件夹、文件和文件扩展

8、 网络发现、横向移动、桌面壁纸设置、终止VMware ESXI虚拟机、清除VMware ESXI虚拟机快照、从终端中排除VMware ESXI

 **横向移动**

枚举所有连接到网络中的服务器，该进程首先会广播 NetBIOS 名称服务 (NBNC)
消息来检查这些附加的设备，然后试图通过PsExec使用配置文件中的凭据复制自身到响应的服务器中。

调用 SHTestTokenMenbership 函数，判断当前用户是否属于本域中的管理员组(0x220 =
DOMAIN_ALIAS_RID_ADMINS)，识别当前用户是否具有域管理员权限，以便加密更多的设备。

![](https://image.3001.net/images/20220823/1661223158_630440f603a1f82f27651.png!small)

调用 NtQueryInformationToken 函数检索与当前令牌(0x2 = TOKEN_GROUPS )关联的组账号，并且检查
TOKEN_GROUPS 中是否包含管理员组：

![](https://image.3001.net/images/20220823/1661223179_6304410b5ae293e2d79c7.png!small)

