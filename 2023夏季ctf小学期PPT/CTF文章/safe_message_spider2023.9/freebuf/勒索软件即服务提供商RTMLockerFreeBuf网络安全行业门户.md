RTM Locker
此前以电子犯罪攻击而闻名，现在又转而使用勒索软件攻击公司。该勒索软件团伙有着非常严格的组织规范，要求所有附属机构一定要保持活跃，即使散伙也要告知 RTM
Locker。这表明该团伙的组织成熟度较高，这一点在 Conti 勒索软件团伙中也是如此。

该勒索软件团伙的核心目标只有一个：低调行事。RTM Locker
不想登上热搜与头条，而是希望能够闷声发大财。该团伙的勒索信息提供俄文与英文两个版本，俄文版的行文质量更高。毫不意外的，东欧与独联体国家是被禁止攻击的。

## 解开 RTM Locker 的面纱

RTM Locker 对行事规则、攻击目标与作案手法进行了规范，这对分析人员了解其工作方式提供了帮助，并且能够猜测该组织成员所在地理位置。

### 控制面板

控制面板通过用户名与密码进行登录，还增加了验证码防止其他人进行暴力破解。

![image.png-393kB](https://image.3001.net/images/20230424/1682347799_64469717dee7b145f98b9.png!small)控制面板登录页面

控制面板中可以增加受害者，该团伙也是使用双重勒索来攻击受害者的。一次通过加密文件，一次通过发布被盗数据。添加受害者的页面如下所示，数据公开时限也可以一同设置：

![image.png-45.9kB](https://image.3001.net/images/20230424/1682347802_6446971a1b05bd3dd027b.png!small)新增攻击目标

勒索信息中也提供了佐证：“你所有的文件、照片、报告、客户和员工数据、数据库和其他重要文件都被加密，你自己是无法解密的，这些文件也在我们的服务器上！”。

### 附属机构规范

每个附属机构都必须保持活跃，否则账户就会被删除。任何十天内没有提前告知 RTM Locker 的非活跃用户，都会被禁止登录。

![image.png-84.3kB](https://image.3001.net/images/20230424/1682347802_6446971abd3aebf4f103f.png!small)提示信息

这样做不仅避免有研究人员潜伏在团伙内部，也说明该团伙的专业性。为了避免吸引过多的注意，独联体国家、太平间、医院与疫苗相关公司都不在攻击范畴。但特别指出的是，牙医诊所可以攻击，并不与其他类型的医院相同。

攻击者在极力避免攻击重要的基础设施、执法部门或者其他大公司，这都会引起对该组织不必要的关注。如果发生了此类事件，RTM Locker
会删除所有痕迹并且通过单独的平台进行谈判。攻击者希望能够通过秘密渠道提供解密工具，使受害者能悄无声息地恢复正常。尽管使用了解密工具，组织也不能很快恢复正常，造成的影响可能会持续数月。

RTM Locker
十分谨慎，不仅严禁任何公开谈判，还将被窃的数据存储在不同的服务器上。引起媒体巨大关注的勒索软件团伙，将会被执法部门与安全研究人员格外关注。最典型的例子就是
2021 年的 DarkSide 勒索软件团伙，攻击 Colonial Pipeline 引起了全球的关注。

RTM Locker
勒索软件的构建是保密的，攻击者希望能确保长期不被分析。一旦设备加密完成，样本将会删除自身，这进一步加强了该团伙的隐蔽性。并且根据样本中附属机构的
ID，泄露样本的附属机构也会被踢出局。外包给其他附属机构也是被严格禁止的，进一步控制获取样本的范围。

与 RTM Locker 勒索软件团伙的所有沟通都是通过 TOX 完成的，不支持其他方式。

![image.png-433.9kB](https://image.3001.net/images/20230424/1682347803_6446971bb6492355d2105.png!small)组织规范

### 地理位置

由于俄乌冲突，RTM Locker 内部也出现了分歧。在最新的消息中，攻击者表示有一台服务器下线，正在进行数据传输与恢复工作。

![image.png-170kB](https://image.3001.net/images/20230424/1682347805_6446971db94d201142cf0.png!small)

攻击者消息

研究人员推断，RTM Locker 内部对俄乌冲突也存在分歧。并不是所有攻击者都位于俄罗斯，攻击者也尽力避免在独联体国家中寻找受害者。

## 技术分析

尽管勒索软件没有被混淆，但也不包含各种符号信息。勒索软件遵循清晰的执行流程，如下所示：

![image.png-58.5kB](https://image.3001.net/images/20230424/1682347806_6446971e9788bab64fe8b.png!small)执行流

### 权限提升

RTM Locker 为了尽可能多地加密文件，会检查它是否对内置系统域具有管理权限，从而获得对设备的无限制访问权限。

RTM Locker
并没有利用漏洞来进行提权，而是弹出用户账户控制对话框，让受害者来批准执行。如果受害者不同意，勒索软件就会不断弹出请求对话框，直到用户授予权限。

![image.png-530.4kB](https://image.3001.net/images/20230424/1682347807_6446971f504e09a74b5cf.png!small)请求权限代码

### 调试控制台

提权完成后，检查命令行参数。如果只有 debug 参数，会将调试数据打印到控制台。

![image.png-76.3kB](https://image.3001.net/images/20230424/1682347809_644697212ff7bc4060145.png!small)调试参数

### 进程终止

终止各种可能影响到加密的进程，以确保影响的最大化。遍历所有进程，并且将指定的进程终止如下所示：

![image.png-401.8kB](https://image.3001.net/images/20230424/1682347810_644697223d66a0e2fda92.png!small)进程检测

勒索软件之前获得的高权限，有助于其终止那些会影响加密过程的进程。要终止的进程包括
sql.exe、oracle.exe、ocssd.exe、dbsnmp.exe、synctime.exe、agntsvc.exe、isqlplussvc.exe、xfssvccon.exe、mydesktopservice.exe、ocautoupds.exe、encsvc.exe、firefox.exe、tbirdconfig.exe、mydesktopqos.exe、ocomm.exe、dbeng50.exe、sqbcoreservice.exe、excel.exe、infopath.exe、msaccess.exe、mspub.exe、onenote.exe、outlook.exe、powerpnt.exe、steam.exe、thebat.exe、thunderbird.exe、visio.exe、winword.exe、wordpad.exe
和 notepad.exe。

紧接着终止各种相关服务，代码如下所示：

![image.png-339.2kB](https://image.3001.net/images/20230424/1682347811_6446972377d6cce4166fb.png!small)服务检测

主要针对各种反病毒服务与数据备份服务，包括
vss、sql、svc$、memtas、mepocs、sophos、veeam、backup、GxVss、GxBlr、GxFWD、GxCVD、GxCIMgr、DefWatch、ccEvtMgr、ccSetMgr、SavRoam、RTVscan、QBFCService、QBIDPService、Intuit.QuickBooks.FCS、QBCFMonitorService、YooBackup、YooIT、zhudongfangyu、stc_raw_agent、VSNAPVSS、VeeamTransportSvc、VeeamDeploymentService、VeeamNFSSvc、PDVFSService、BackupExecrowExgentA、BackupExecVSSAgentAccerator、BackupExecDiveciMediaService、BackupExecJobEngine、BackupExecManagementService、BackupExecRPCService、ArcSch2Svc、AcronisAgent、CASAD2DWebSvc
和 CAARCUpdateSvc。

另一项检查是确定 CPU 执行 SSE2 指令的能力，方便后续进行加密。

### 加密准备工作

开始加密前，勒索软件会清空回收站并删除卷影副本。确保受害者不能恢复文件，如下所示：

![image.png-48.7kB](https://image.3001.net/images/20230424/1682347812_644697247c93debf5970c.png!small)删除文件代码

随后遍历卷设备，未使用的卷号会被分配一个挂载点，用于所有卷上的未挂载分区。最多使用 26
个驱动器编号，如下所示。值得注意的是，驱动器编号顺序是按照键盘布局而来，并非是传统字母表顺序。

![image.png-365.8kB](https://image.3001.net/images/20230424/1682347813_64469725434659ab42c1f.png!small)盘符编号

检查所有驱动器类型，如果给定驱动器没有安装任何卷，将会存储在不同的数组中。下面代码中名为 unmountedDrives：

![image.png-144.1kB](https://image.3001.net/images/20230424/1682347814_64469726e8bd408a452f1.png!small)未映射驱动器盘符列表

数组的迭代从末尾开始，这意味着要创建的第一个新驱动器盘符是 M：

![image.png-455.5kB](https://image.3001.net/images/20230424/1682347817_6446972918cea8e79faed.png!small)将卷安装到未映射的字母

所有附加卷都会被迭代，直到所有驱动器号都在使用中，以此来增加加密文件的数量。

### 文件加密

针对远程驱动器与本地驱动器，调用文件夹解析函数：

![image.png-248.8kB](https://image.3001.net/images/20230424/1682347818_6446972a5dd2b67f576c1.png!small)加密远程驱动器

如果检查的是文件夹，将会递归调用检查函数，对每个子文件夹进行检查。如果文件名不是勒索信息的文件名，也没有 65
个字符长的扩展名，就会调用加密函数。代码如下所示：

![image.png-591.5kB](https://image.3001.net/images/20230424/1682347819_6446972b75e312c1dcc69.png!small)文件迭代加密

例外的文件名为：windows、appdata、application data、boot、google、mozilla、program
files、program files (x86)、programdata、system volume
information、tor、browser、windows.old、intel、msocache、perflogs、x64dbg、public、all
users、default。

加密文件根据 32 个随机生成的字节获得一个随机的 64 字符扩展名，每个字节使用两个字符显示。65 个字符的扩展名检查，使用
PathFindExtensionW 的返回值。

样本利用 SystemFunction036 通过 advapi32 手动解析 RtlGenRandom 函数，随机数据生成的代码如下所示：

![image.png-83.6kB](https://image.3001.net/images/20230424/1682347821_6446972d2b7b216094956.png!small)解析
RtlGenRandom 函数

文件加密以多线程进行，但并不只是简单的在多线程中迭代与加密文件。而是使用 IOCP 利用多个线程同时处理一个文件，代码如下所示：

![image.png-796kB](https://image.3001.net/images/20230424/1682347822_6446972e220cfb4795260.png!small)多线程加密文件

通过 GetSystemInfo 获取系统相关信息，这些信息会被多处使用。创建的 IOCP 线程数量等于 CPU 数量的两倍，创建的加密线程等于 CPU
数量。处理器数量存储在全局变量中，该变量用于原子地跟踪运行加密线程数量。

如果文件小于 512 字节，则不会进行加密。随后设置用于加密和 IOCP 线程对之间通信的自定义结构，支持的操作如下所示：

Value| 行动  
---|---  
0xa1| 处理读取的文件  
0xa2| 写入加密数据  
0xa3| 移动并重命名文件  
  
上述操作的代码如下所示：

![image.png-472.8kB](https://image.3001.net/images/20230424/1682347824_644697309f1bc003f9be1.png!small)创建结构

原始文件名与新文件名都存储在自定义结构中，创建 IOCP 后会告知配对的 IOCP 线程。

![image.png-179kB](https://image.3001.net/images/20230424/1682347825_64469731a81ed3a9a3925.png!small)将创建的结构发送到
IOCP

在 IOCP 线程中，可以进行多个操作。读取文件的代码如下所示：

![image.png-69.2kB](https://image.3001.net/images/20230424/1682347826_644697329b32e3f1c2095.png!small)读取文件

下一步就是将加密文件的数据写入文件：

![image.png-144.9kB](https://image.3001.net/images/20230424/1682347827_644697334f79560bff7c5.png!small)加密并写入文件

最后操作是重命名并移动文件：

![image.png-67.9kB](https://image.3001.net/images/20230424/1682347828_6446973448b4ea7061a81.png!small)重命名文件

最终的加密线程将会修改机器的壁纸，向受害者表明文件已经被加密。修改壁纸的代码如下所示：

![image.png-356.2kB](https://image.3001.net/images/20230424/1682347829_644697351823f3bf8bcab.png!small)修改壁纸

新壁纸如下所示：

![image.png-464.9kB](https://image.3001.net/images/20230424/1682347830_644697362a9e3f09ff67a.png!small)新壁纸

### 加密完成

main 函数会调用睡眠循环，等待所有线程运行，直到所有线程运行完成。

![image.png-80.8kB](https://image.3001.net/images/20230424/1682347832_6446973820d8253dccc93.png!small)等待加密完成

### 清除日志

最后清除所有的系统日志、应用程序日志与安全日志，未配置备份文件确保完全清除。

![image.png-175.7kB](https://image.3001.net/images/20230424/1682347832_64469738d31619f08f076.png!small)清除日志

### 自我销毁

执行的最后一个命令为 `cmd.exe /c PING -n 5 127.0.0.1 > NUL && del
"[path]"`。在样本文件进程停止运行后，样本就会被直接删除。代码如下所示：

![image.png-240.9kB](https://image.3001.net/images/20230424/1682347833_64469739d4e695858a4f4.png!small)异步自我删除

## 结论

多线程加密可以保证加密速度极快，将所有驱动器盘符下的文件尽快加密。但只有样本文件在获取高权限后才能正常工作，因此难以不依赖用户进行自我传播。攻击者可能是通过钓鱼邮件、垃圾邮件、存在漏洞的系统以及购买访问权限的方式来实现恶意软件的投递，并且要尽可能地保持低调。该团伙的主要目的是获取经济利益，而非出于政治动机。

## 勒索信息

    
    
    Your personal ID: [VICTIM-ID]!!! Your network is infected by the RTM Locker command!!!All your documents, photos, reports, customer and employee data, databases and other important files are encrypted and you cannot decrypt them yourself. They are also on our servers! But don't worry, we will help you recover all your files!The only way to recover your files is to buy our dedicated software. Only we can provide you with this software, and only we can recover your files!You can contact us by downloading and installing the TOR browser (https://www.torproject.org/download/languages/)We value our reputation. If we do not fulfill our work and obligations, no one will pay us. It's not in our interest.All of our decryption software is perfectly tested and will decrypt your data. We will also provide support in case of problems.===============================================================================================Login link:http://nvfutdbq3ubteaxj4m2jyihov5aa4akfudsj5h7vhyrvfarfra26ksyd.onion/1D85262A4B3F59090972E7EE7804FC641E9CBB6D65E5F4B376DF37D6180CD1/connectFor authorization you need to enter your ID.!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Warning!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!If you do not contact the support team within 48 hours, your data will be published in the public domain, and data compromising you will be sent to your competitors, as well as to the relevant regulatory authorities.===============================================================================================DO NOT ATTEMPT TO RECOVER THE FILES YOURSELF!DO NOT MODIFY ENCRYPTED FILES!OTHERWISE YOU MAY LOSE ALL YOUR FILES FOREVER!﻿

## 参考来源

> [Trellix](https://www.trellix.com/en-> us/about/newsroom/stories/research/read-the-manual-locker-a-private-raas-> provider.html)

