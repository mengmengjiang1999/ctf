# CVE-2020-1317：Windows组策略中的漏洞

阅读量 **276949**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-18 10:30:27

 **x**

##### 译文声明

本文是翻译文章，文章原作者 Eran Shimony，文章来源：cyberark.com

原文地址：<https://www.cyberark.com/resources/threat-research-blog/group-policies-going-rogue>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t017ebd1a522c410e78.jpg)

## 0x00 绪论

本文是一个为期一年的研究项目的一部分，该项目发现了各大供应商的60个不同漏洞。本文讨论Windows组策略对象（GPO）机制中的一个漏洞。此漏洞专门针对策略更新步骤，允许域环境中的标准用户执行文件系统攻击，进而允许攻击者躲过反病毒软件，绕过安全加固措施，并可能导致公司组织网络中的严重损失。此漏洞影响所有运行Windows的计算机（Windows
2008及以上），并可提升其在域环境中的权限。

如果您对本研究的其他发现感兴趣，请回顾[第1部分](https://www.cyberark.com/threat-research-blog/follow-the-link-exploiting-symbolic-links-with-ease/)和[第2部分](https://www.cyberark.com/threat-research-blog/lazy-privilege-escalation-abusing-dells-dup-framework-cve-2019-3726/)。

###  概述

GPSVC将所有加入域的Windows计算机暴露于提权漏洞。运行gpudate.exe就可以通过文件操纵攻击提升为特权用户。

Windows的组策略机制已经存在很久了。它被认为是在域环境中分发设置的相对安全的方法，不管是打印机设置、备份设备设置，还是其他什么设置。因此，组策略需要与许多组件交互。许多交互就意味着存在许多潜在的漏洞，这就是我们要讲的。

###  示意图

![](https://p2.ssl.qhimg.com/t01dd9b2750e3dbed2b.jpg)

## 0x01 分析

组策略或GPO对象最早是在Windows
2000开始使用的。距今已经有一段时间了，他们有点改变了，但基本上还是一样的。GPO被管理员用于在受管理的环境中强制执行其策略，功能非常强大。管理员可以用GPO做任何他们想做的事情，从禁用Windows
Defender和防火墙到安装软件和打印机。

在Windows中，每个用户都有一组本地组策略，可以由本地管理员修改，这允许他们为本地计算机设置规则。在加入域环境的计算机上，域管理员突发奇想应用于你的计算机的GPO常常会导致你的电脑出问题。

遵循最小特权原则是众所周知的安全最佳实践，这个原则将用户的特权级别限制在最低限度。对于组策略来说，也就是不允许域用户成为本地管理员组的一部分，因为本地管理员可以改变域管理员应用的任何组策略，使GPO无法在企业网络上有效地强制执行设置。

有趣的是，本地非特权用户可以手动请求组策略更新。因此，如果在组策略更新进程中发现bug，你可以随时自己触发这个bug，这就使潜在的攻击更容易了。不必等待约90分钟（在时间差为30分钟的域环境上推送组策略更新的默认时间段），管理员可以立即强制更新。

我们感兴趣的是本地组策略服务，其名为gpsvc。此服务需要特权才能执行其功能，因此它在NT
AUTHORITYSYSTEM的上下文中运行。这点很重要，因为如果我们能找到它执行的不安全文件操作，我们也许就可以使用文件操纵攻击将操作重解析到另一个文件。

毫无意外，gpsvc托管在Svchost.exe里，并且主要在C:WindowsSystem32gpsvc.dll中实现。这个DLL有一个RPC接口，我用James
Forshaw创建的这个好[工具](https://github.com/tyranid/WindowsRpcClients)将其反编译成C。其中，有几个有趣的方法可以由本地用户调用。

    
    
    uint Server_ProcessRefresh(string p0, sbyte p1, sbyte p2, sbyte p3, int p4, out Struct_0 p5)
    uint Server_RegisterForNotification(string p0, int p1, int p2, out int p3)
    uint Server_CheckRegisterForNotification(string p0, int p1)
    uint Server_LockPolicySection(string p0, int p1, int p2, out NtApiDotNet.Ndr.Marshal.NdrContextHandle p3)
    uint Server_UnLockPolicySection(ref NtApiDotNet.Ndr.Marshal.NdrContextHandle p0) uint Server_GetGroupPolicyObjectList(string p0, string p1, string p2, int p3, out Struct_2[] p4, out int p5)
    uint Server_GetAppliedGroupPolicyObjectList(int p0, string p1, string p2, string p3, out Struct_2[] p4, out int p5)
    uint Server_GenerateGroupPolicyNotification(int p0, string p1, int p2)
    

为了知道运行gpupdate命令的时候调用了gpsvc里的哪个方法，我打开了windbg，在所有暴露出的RPC例程上下断点，输入命令：

    
    
    bm gpsvc!Server_*
    

结果显示第一个函数是对我们有用的，即Server_ProcessRefresh()，它会启动更新过程。不过，在继续之前，请注意客户端通过RPC请求服务端服务的这个行为是导致许多bug的根源。倒霉的是，Windows不同组件间正是用RPC通信的，没有了RPC，Widows就无法正常运作了。（可以试试杀掉DCOM服务，体验下Windows怎样给你点蓝色看看）

Server_ProcessRefresh()从域控制器请求GPO对象，接收到结果后，就对每个组策略调用ProcessGPOList()。

这个方法反编译后超过600行代码，其中还使用了COM对象。如果我洋洋洒洒写下关于gpsvc.dll中COM对象的十页长篇大论，就没人爱看这篇文章了，所以我就对细节一笔带过，主要说重要部分。

看下方法的签名，就可以猜出它的功能：

    
    
    ProcessGPOList(
    struct _GPEXT *a1,
     struct _GPOINFO *a2,
     struct _GROUP_POLICY_OBJECTW *a3,
     struct _GROUP_POLICY_OBJECTW *a4, int a5,
     unsigned __int64 a6,
     struct CGPExtensionExecutionState *a7,
     int *a8
    

不是所有参数都有正式文档记载，叫人一如既往地失望。不过，`_GROUP_POLICY_OBJECTW`是有文档的，程序员可以在C++里创建这个对象：

    
    
    typedef struct _GROUP_POLICY_OBJECTW {
    DWORD dwOptions;
    DWORD dwVersion;
    LPWSTR lpDSPath;
    LPWSTR lpFileSysPath;
    LPWSTR lpDisplayName;
    WCHAR szGPOName[50];
    GPO_LINK GPOLink;
    LPARAM lParam;
    struct _GROUP_POLICY_OBJECTW *pNext;
    struct _GROUP_POLICY_OBJECTW *pPrev;
    LPWSTR lpExtensions;
    LPARAM lParam2;
    LPWSTR lpLink;
    } GROUP_POLICY_OBJECTW,*PGROUP_POLICY_OBJECTW;
    

可见_GROUP_POLICY_OBJECTW是个链表结构，有许多成员。其中两个成员*pPrev和*PNext是指向_GROUP_POLICY_OBJECTW的指针，这样就可以轻松遍历链表。本地服务会遍历该链表，根据对象中包含的是否为同类型的GPO对象决定是否要循着指针继续向下走。因此，对每个组策略都会调用ProcessGPOList()。

再看看GPOLink和szGPOName。参数GPOLink可以设置为五种值（复制自MSDN：[https://docs.microsoft.com/en-us/windows/win32/api/userenv/ns-userenv-group_policy_objectw）：](https://docs.microsoft.com/en-us/windows/win32/api/userenv/ns-userenv-group_policy_objectw%EF%BC%89%EF%BC%9A)

  * GPLinkUnknown – 没有关联信息。
  * GPLinkMachine – 该GPO关联到一台计算机（本地或远程的）。
  * GPLinkSite – 该GPO关联到一个站（site）。
  * GPLinkDomain – 该GPO关联到一个域。
  * GPLinkOrganizationalUnit – 该GPO关联到一个组织单位。

其实，这个参数的值决定着本地服务会把组策略写到哪里。如果你把GPO关联到一台计算机，那么会写到C:ProgramDataMicrosoftGroup
PolicyHistory{GUID}MachinePrefererncesApplied-ObjectApplied-Object.xml。

但是，如果GPOLink的值为GPLinkOrganizationalUnit，那么策略应用于域中 **所有**
用户和计算机，GPSVC会把策略复制到本地用户 **可访问**
的路径下。对此，Windows用了%localappdata%环境变量：C:UserseranAppDataLocalMicrosoftGroup
PolicyHistory{szGPOName}USER-SIDPreferencesApplied-ObjectApplied-Object.xml。其中Applied-ObjectApplied-Object.xml会替换为策略所应用的对象。比如，对打印机的策略会替换为
PrintersPrinters.xml。

我之前提过gpsvc以NT
AUTHORITYSYSTEM身份进行所有文件操作吗？这就表示如果服务没有模拟本地用户的话（也确实没有模拟），就可以通过符号链接攻击来利用目录的ACL。试图进行文件操纵攻击时，我们先要检查特权组件是否使用了模拟本地用户的API，例如：

  * RpcImpersonateClient
  * ImpersonateLoggedOnUser
  * CoImpersonateClient

大概有12次对这些API的调用，不包含对SetTokenInformation的调用。看来开发者还是懂得模拟用户的重要性的。但是，所有的代码路径都要正确进行模拟，这就麻烦了。在本漏洞中，问题之处位于模块gpprefcl.dll，这个DLL把载入到ProcessGPOList函数的那些组策略写入磁盘。

看看gpprefcl.dll的导出表就可以得到关于其作用的线索（节选）：

    
    
      7     4 0002E450 GenerateGroupPolicyApplications
      8     5 0002EE10 GenerateGroupPolicyDataSources
      9     6 0002F080 GenerateGroupPolicyDevices
      10    7 0002D820 GenerateGroupPolicyDrives
      11    8 0002D5B0 GenerateGroupPolicyEnviron
      12    9 0002DD00 GenerateGroupPolicyFiles
      13    A 0002F2F0 GenerateGroupPolicyFolderOptions
      14    B 0002DA90 GenerateGroupPolicyFolders
      15    C 0002DF70 GenerateGroupPolicyIniFile
      21   12 0002E6C0 GenerateGroupPolicyPrinters
      22   13 0002FCB0 GenerateGroupPolicyRegionOptions
      29   1A 0002EED0 ProcessGroupPolicyDataSources
      30   1B 0002F140 ProcessGroupPolicyDevices
      31   1C 0002D8E0 ProcessGroupPolicyDrives
      32   1D 0002D670 ProcessGroupPolicyEnviron
      33   1E 0002E5E0 ProcessGroupPolicyExApplications
      34   1F 0002EFA0 ProcessGroupPolicyExDataSources
      35   20 0002F210 ProcessGroupPolicyExDevices
      36   21 0002D9B0 ProcessGroupPolicyExDrives
      38   23 0002DE90 ProcessGroupPolicyExFiles
      39   24 0002F480 ProcessGroupPolicyExFolderOptions
      40   25 0002DC20 ProcessGroupPolicyExFolders
      41   26 0002E100 ProcessGroupPolicyExIniFile
      42   27 0002EAC0 ProcessGroupPolicyExInternet
      43   28 0002F6F0 ProcessGroupPolicyExLocUsAndGroups
      54   33 0002DDC0 ProcessGroupPolicyFiles
      55   34 0002F3B0 ProcessGroupPolicyFolderOptions
      56   35 0002DB50 ProcessGroupPolicyFolders
      59   38 0002F620 ProcessGroupPolicyLocUsAndGroups
      1    39 000407E0 ProcessGroupPolicyMitigationOptions
      60   3A 00030730 ProcessGroupPolicyNetShares
      61   3B 0002F890 ProcessGroupPolicyNetworkOptions
      62   3C 0002FB00 ProcessGroupPolicyPowerOptions
      63   3D 0002E780 ProcessGroupPolicyPrinters
      2    3E 00040AC0 ProcessGroupPolicyProcessMitigationOptions
      67   42 00030250 ProcessGroupPolicyServices
      68   43 0002EC60 ProcessGroupPolicyShortcuts
      69   44 000304C0 ProcessGroupPolicyStartMenu
    

所有导出函数都会返回一个apmCse::PolicyMain<apmClientProfessional>类型的新对象。

    
    
    return apmCse::PolicyMain<apmClientProfessional>(
    a1,
            (__int64)&`GetCseVersionPrinters'::`2'::s_wVersion,
            (__int64)L"GenerateGroupPolicyPrinters",
            (__int64)L"Group Policy Printers");
    

PolicyMain()函数的职责是应用GPO。对每个不同的Applied-Object，随方法的第三个参数不同，其行为会有些不同。内部随后的一个动态调用会使用之。gpprefcl.dll中有66个导出方法，几乎所有方法都是这样实现的，唯一的不同就是第三和第四个参数不同。

除此之外，PolicyMain()中还有几个函数调用，其中有一个调用用于初始化主对象apmCSE，有25个初始化参数。

这之后，又有个apmCse::StartClient<apmClientProfessional>()的调用，漏洞函数就在这里。我无意逆向apmCse类以及和它关联的方法。我们可以列出带有感兴趣的关键字的所有方法，比如Read、Write、Delete这些关键字。如果某个函数签名中有这些关键字，它就很可能会进行文件操作。可以用windbg的有用的[grep](https://github.com/long123king/grep)扩展来列出列表。

    
    
    !silent; x gpprefcl!apm*; !igrep "DeleteFile|WriteFile|textfile"
    

结果如下：

    
    
    00007ffd`ba4355f8 gpprefcl!apmDeleteFile(long __cdeclapmDeleteFile(unsigned short const *))
    00007ffd`ba4333cc gpprefcl!apmWriteTextFile (long __cdecl apmWriteTextFile(class apmString const &,unsigned short const *,bool))
    00007ffd`ba4332b8 gpprefcl!apmWriteFile (long __cdecl apmWriteFile(unsigned char *,unsigned long,unsigned short const *,bool))
    00007ffd`ba407d74 gpprefcl!apmConfigFile::deleteFiles (private: long __cdecl apmConfigFile::deleteFiles(unsigned short const *,bool))
    00007ffd`ba434008 gpprefcl!apmDeleteFileSystemItem (long __cdecl apmDeleteFileSystemItem(unsigned short const *,unsigned short const *,struct _WIN32_FIND_DATAW *,bool,bool,bool,bool))
    

得出列表后就可以在这些方法下断点了，因为很可能这些方法中进行了文件操作，这就给我们提供了文件系统攻击的好机会。

结果看来十分喜人，似乎每个方法里都有一个文件操作。除了下断点之外，还可以检查下有没有调用线程模拟API，如果没有，那就完美。

apmClientContext类中有一个对impersonateLoggedOnUser()的wrapper（包装）函数，叫做apmClientContext::impersonate()。因此，要检查上面提到的文件系统方法中有没有调用apmClientContext::impersonate()。

这个模拟函数在gpprefcl.dll中被多次调用，这也是应该的。但是，如果查看对这个函数的交叉引用，就发现没有来自上述方法的引用。还要再进一步继续检查方法的调用者，比如gpprefcl!apmWriteFile()和gpprefcl!apmDeleteFile()的调用者：

  * apmClient::cseApplyGpoPolicies() → apmClient::UpdateGph() → gpprefcl!apmWriteFile()
  * apmClient::cseRemoveLastGpoPolicies()→ apmClient::PurgeGph() → gpprefcl!apmDeleteFile()

这些方法里没有一个调用了apmClientContext::impersonate()。负责应用GPO的方法是apmClient::cseApplyGpoPolicies()和apmClient::cseRemoveLastGpoPolicies()。我是在Windbg于gpprefcl!apmWriteFile()断下时，查看调用栈意识到的：

    
    
    00 000000dd`d27fc3a8 00007ffd`ba3f413f gpprefcl!apmWriteFile01
     000000dd`d27fc3b0 00007ffd`ba3f2867 gpprefcl!apmClient::UpdateGph+0x13702
     000000dd`d27fc490 00007ffd`ba3f54ee
     gpprefcl!apmClient::cseApplyGpoPolicies+0x2a703 000000dd`d27fc5a0
     00007ffd`ba3f3e3a gpprefcl!apmClient::processGpoLists+0x4ca04
     000000dd`d27fc710 00007ffd`ba41d49a gpprefcl!apmClient::Main+0x1a05
     000000dd`d27fc740 00007ffd`ba41d310
     gpprefcl!apmCse::StartClient<apmClientProfessional>+0xee06 000000dd`d27fdc00
     00007ffd`ba41e911 gpprefcl!apmCse::PolicyMain<apmClientProfessional>+0x25007
     000000dd`d27fdf40 00007ffd`c9c89ce2
     gpprefcl!ProcessGroupPolicyExPrinters+0xc108 000000dd`d27fe010
     00007ffd`c9c50b25 gpsvc!ProcessGPOList+0x88209 000000dd`d27fe3d0
     00007ffd`c9c5caf5 gpsvc!ProcessGPOs+0x227c5
    

那么剩下的唯一的事就是利用漏洞了。

## 0x02 利用

利用过程如下：

  * 列出C:UsersuserAppDataLocalMicrosoftGroup PolicyHistory中的所有组策略GUID。
  * 如果有多个GUID，看看哪个目录最近更新了。
  * 进入该目录，再进入名为用户SID的子目录。
  * 找到最后修改的目录，每个人机器上不同，我这里是Printers。
  * 删除Printers目录里的xml文件。
  * 创建NTFS解析点，指向RPC Control，再创建由xml指向C:WindowsSystem32任意文件.dll的符号链接。
  * 打开命令行，运行gpupdate。

成功了，在任意位置创建任意文件。通过这个漏洞还可以删除修改系统保护的文件。根据GPO对象的不同，步骤有些许不同，但是都可以导致提权漏洞。

## 0x03 总结

组策略的结构很复杂。Windows支持许多老式代码和自定义选项，其中包括不同的GPOLink类型。尽管在几乎所有代码路径上都调用了线程模拟API，但还是有路径没调用的。当组策略应用于组织单位，而服务又将GPO写入磁盘时就发生漏洞。

数以百万计的Windows机器在未更新补丁的情况下都会受此漏洞影响，但是将来微软应该会提供缓解措施，在创建挂载点/目录链接时要求管理员权限。这将阻止整类文件系统攻击。

更多细节可以看这个演示：  
<https://cyberark.wistia.com/medias/owxm6nmb2v>

感谢队员Elyda Barak，他对组策略有广泛的认识，给我解释了组策略的许多细节，省了我很多时间。

## 0x04 漏洞披露时间线

2019年6月17日 – 漏洞报告给微软。

2019年6月17日 – 官方接收。

2019年9月18日 – 微软确认漏洞，说明了补丁的复杂度。

2020年1月9日 – 微软承诺2020年第二季度下发补丁。

2020年6月9日 – 补丁发布：CVE-2020-1317。

本文翻译自cyberark.com [原文链接](https://www.cyberark.com/resources/threat-research-blog/group-policies-going-rogue)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **hx1997** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/208437](/post/id/208437)

安全客 - 有思想的安全新媒体

本文转载自: [cyberark.com](https://www.cyberark.com/resources/threat-research-blog/group-policies-going-rogue)

如若转载,请注明出处： <https://www.cyberark.com/resources/threat-research-blog/group-policies-going-rogue>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CVE-2020-1317](/tag/CVE-2020-1317)

 **+1** __2赞

 __收藏

![](https://p5.ssl.qhimg.com/t01c4d2c10c5886a436.png) hx1997

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

