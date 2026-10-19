Nokoyawa 是今年新出现的 Windows 勒索软件，Fortinet 最早捕获的样本是在 2022 年 2 月编译的，并且与 Karma
勒索软件存在大量的相似之处。Karma 可以通过一系列变种追溯到名为 Nemty 的勒索软件，后者为在 2019 年被发现的勒索软件。

近期发现的 Nokoyawa 变种，重用了大量公开源码来改进自身。本文将会介绍 Nokoyawa 勒索软件的及基本情况。

## Nokoyawa 勒索软件

与 Karma 能够在 32 位/ 64 位 Windows 运行不同，只发现了在 64 位 Windows 上运行的 Nokoyawa 样本。

Nokoyawa 提供了几个命令行参数：

> help：打印命令行选项列表
>
> network：加密所有驱动器和卷上的文件（本地和网络）
>
> file：加密单个文件
>
> dir：加密指定目录和子目录中的所有文件

如果没有提供参数，Nokoyawa 默认加密所有本地驱动器和卷。

为了保持加密速度，Nokoyawa 创建了多个线程来加密不以 .exe、.dll 或 .lnk 为扩展名的文件。文件名中带有 NOKOYAWA
的文件也会被跳过。此外，一些目录及其子目录通过将其名称的哈希与样本中硬编码的哈希列表进行对比也会被跳过。

攻击者为每个样本都生成一对新的椭圆曲线加密公私钥对，然后将公钥嵌入文件中。这样，攻击者消除了受害者可以使用相同密钥解密的可能性，因为每个受害者都是独立的。

被勒索软件加密的文件会附加 `.NOKOYAWA`的扩展名，赎金勒索信息被写入每个加密目录中的 `NOKOYAWA_readme.txt`中。

## 抄袭能力

2022 年 4 月发现的样本中增加了三个新功能，都为了让 Nokoyawa 可以更多的加密文件。这些功能在勒索软件中广为使用，但 Nokoyawa
才开始将其引入，尝试在技术能力上追赶其他攻击者。

研究人员能够确认，新增的功能都是从公开源码中复制而来的，包括 2021 年 9 月泄露的 Babuk 勒索软件源码。

举个例子，终止进程与服务以减少被其他程序锁定文件的数量。这一点上，Nokoyawa 的代码与 Babuk 的代码完全一致。

![image.png-764.3kB](https://image.3001.net/images/20220526/1653564328_628f63a82478e2a0a7278.png!small)代码比对

受到影响的进程如下所示：

> sql.exe  
> oracle.exe  
> ocssd.exe  
> dbsnmp.exe  
> synctime.exe  
> agntsvc.exe  
> isqlplussvc.exe  
> xfssvccon.exe  
> mydesktopservice.exe  
> ocautoupds.exe  
> encsvc.exe  
> firefox.exe  
> tbirdconfig.exe  
> mydesktopqos.exe  
> ocomm.exe  
> dbeng50.exe  
> sqbcoreservice.exe  
> excel.exe  
> infopath.exe  
> msaccess.exe  
> mspub.exe  
> onenote.exe  
> outlook.exe  
> powerpnt.exe  
> steam.exe  
> thebat.exe  
> thunderbird.exe  
> visio.exe  
> winword.exe  
> wordpad.exe  
> notepad.exe

受到影响的服务如下所示：

> vss  
> sql  
> svc$  
> memtas  
> mepocs  
> sophos  
> veeam  
> backup  
> GxVss  
> GxBlr  
> GxFWD  
> GxCVD  
> GxCIMgr  
> DefWatch  
> ccEvtMgr  
> ccSetMgr  
> SavRoam  
> RTVscan  
> QBFCService  
> QBIDPService  
> Intuit.QuickBooks.FCS  
> QBCFMonitorService  
> YooBackup  
> YooIT  
> zhudongfangyu  
> sophos  
> stc_raw_agent  
> VSNAPVSS  
> VeeamTransportSvc  
> VeeamDeploymentService  
> VeeamNFSSvc  
> veeam  
> PDVFSService  
> BackupExecVSSProvider  
> BackupExecAgentAccelerator  
> BackupExecAgentBrowser  
> BackupExecDiveciMediaService  
> BackupExecJobEngine  
> BackupExecManagementService  
> BackupExecRPCService  
> AcrSch2Svc  
> AcronisAgent  
> CASAD2DWebSvc  
> CAARCUpdateSvc

样本中还使用 IOCTL_VOLSNAP_SET_MAX_DIFF_AREA_SIZE (0x53c028) 控制代码的 DeviceIoControl
API 将卷影副本快照的空间大小调整为 1 字节，以此删除卷影副本快照。该技术实现似乎是从公开的 POC 中复制而来，旧样本中没有删除卷影副本快照的功能。

不过，以上功能想要正常执行都是需要管理员权限的。在样本中未观察到 Windows UAC 绕过的实现，攻击者可能通过其他方式获取的管理员权限。

## 勒索信息

在 2022 年 2 月的样本中，受害者要求通过电子邮件联系攻击者。

![image.png-193.5kB](https://image.3001.net/images/20220526/1653564329_628f63a99cc2e69830e16.png!small)勒索信息

在 2022 年 4 月 的样本中，电子邮件被替换成了通过 Tor 的 URL。尽管使用的都是相同的 .onion 域名，但每个样本的标识 ID 是唯一的。

![image.png-198.6kB](https://image.3001.net/images/20220526/1653564330_628f63aa8ea9c1debabc4.png!small)勒索信息

## 赎金支付

访问暗网网站会进入在线聊天页面，受害者可以与攻击者沟通协商并支付赎金。研究人员观察到潜在受害者与攻击者的对话，攻击者表示可以提供最多三个文件的免费解密，证明能够解密：

![image.png-143.4kB](https://image.3001.net/images/20220526/1653564331_628f63ab17d2fc9cafa4b.png!small)在线聊天

页面标注了赎金金额，本例中为 150 万美元。支持比特币与门罗币支付，付款后攻击者提供解密工具：

![image.png-132.4kB](https://image.3001.net/images/20220526/1653564331_628f63ab977d5ae6b72ec.png!small)支付赎金

勒索软件的专业化程度越来越高，这种网站可能是另一种改进尝试。

值得注意的是，攻击者威胁会将数据泄露出去。但研究人员并未发现 Nokoyawa 样本具备这种能力。这很可能是攻击者虚张声势，迫使受害者支付赎金。

## 结论

Nokoyawa 勒索软件的新变种也在持续更新改进，利用公开源码更新自身功能，以小的代价为恶意软件提高技术水平。

## IOC

> A32b7e40fc353fd2f13307d8bfe1c7c634c8c897b80e72a9872baa9a1da08c46  
> 304e01db6da020fc1e0e02fdaccd60467a9e01579f246a8846dcfc33c1a959f8

## 参考来源

> [Fortinet](https://www.fortinet.com/blog/threat-research/nokoyawa-variant-> catching-up)

