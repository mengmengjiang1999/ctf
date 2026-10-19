# 【技术分享】如何绕过Windows上的VirtualBox进程保护机制

阅读量 **235585**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-29 13:59:11

 **x**

##### 译文声明

本文是翻译文章，文章来源：googleprojectzero.blogspot.hk

原文地址：<https://googleprojectzero.blogspot.hk/2017/08/bypassing-virtualbox-process-hardening.html>

译文仅供参考，具体内容表达以及含义原文为准。

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**一、前言**

Windows上的进程属于一种安全的对象，可以阻止已登录Windows主机的某个用户危害其他用户的进程。至少从非管理员的用户角度来看，这是一种非常重要的安全特性。在这种安全特性下，非管理员用户无法破坏任何进程的完整性。然而，这种安全屏障在针对管理员、特别是具有调试（Debug）权限的管理员时会显得捉襟见肘，因为启用这种权限后，管理员就可以无视进程拥有的安全属性，打开任意进程。

在某些情况下，应用程序或者操作系统希望能够保护进程免受用户的影响，这些用户包括管理员用户，甚至在某些情况下，包括当前进程对应的具有完全访问权限的同一个用户。因此，许多解决方案使用了内核支持的（kernel
support）特性来实现这种保护机制。在大多数情况下，这种实现方案仍然会存在缺陷，我们可以利用这些缺陷来突破“受保护”的进程。

在本文中，我们会介绍Oracle的VirtualBox在进程保护方面的具体实现方法，也会详细介绍如何通过三种方法绕过这种保护机制，将任意代码注入到进程中（这三种方法目前已被修复）。本文所展示的技术同样可以应用在类似的进程“保护”机制上。

  

**二、Oracle VirtualBox进程防护机制**

****

想在用户模式下完全实现进程的保护几乎是不可能的一件事情，现在有很多方法可以将数据注入到某个进程中。特别是当你想要保护的进程正运行在你想要阻止的用户的上下文环境中时，进程保护更加难以实现。比如，攻击者可以使用
**PROCESS_CREATE_THREAD** 访问权限打开某个进程的句柄，然后直接插入一个新的线程，或者攻击者可以使用
**THREAD_SETCON_TEXT** 访问权限打开进程中的线程，然后直接修改指令指针（Instruction
Pointer）以跳转到任意地址，这些都是直接的攻击方式。攻击者也可以修改进程所处的注册表或者环境，强迫进程加载任意COM对象或者[Windows挂钩](https://msdn.microsoft.com/en-us/library/windows/desktop/ms644990\(v=vs.85\).aspx)（Hook）。攻击者能够做的修改操作可以说是不胜枚举的。

因此，VirtualBox（VBOX）借用了内核的帮助来保护它的进程。这种保护机制在源代码中对应的是 **进程加固** （Process
Hardening）技术。VBOX会尝试保护进程免受当前所属的同一用户的影响。我们可以在[源代码注释](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/SUPR3HardenedMain.cpp?rev=67954#L29)中找到详细的解释以及技术概述。在这段注释的开头部分详细描述了VBOX内核驱动方面的保护机制，VBOX内核驱动中包含大量方法，这些方法可以用来突破内核或者至少可以用来提升权限。这也是为什么VBOX要去保护其进程免受当前用户的修改，因为如果用户可以访问VBOX内核驱动，那么就可以以此为据点，获取内核或系统权限。虽然某些进程保护机制也会阻止管理员控制当前进程，但这并不是进程加固代码的目标。

我的同事Jann从设备访问角度开展研究，在Linux系统的VBOX驱动及保护机制上发现过[许多](https://bugs.chromium.org/p/project-zero/issues/detail?id=1091)[问题](https://bugs.chromium.org/p/project-zero/issues/detail?id=1141)。在Linux上，VBOX限制了只有 **root** 才能访问VBOX驱动，然后利用
**SUID**
二进制程序赋予VBOX用户进程访问驱动的权限。VBOX驱动在Windows系统没有使用SUID程序，而是使用内核API来尝试阻止用户以及管理员打开受保护的进程，阻止他们注入代码。

内核组件的核心位于[ **SupportwinSUPDrv-win.cpp**](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPDrv-win.cpp?rev=67954)文件中。这段代码注册了Windows内核支持的两种回调机制：

1、[ **PsSetCreateProcessNotifyRoutineEx**](https://msdn.microsoft.com/en-us/library/windows/hardware/ff559953\(v=vs.85\).aspx)。当新进程创建时，驱动就会得到通知。

2、[ **ObRegisterCallback**](https://msdn.microsoft.com/en-us/library/windows/hardware/ff558692\(v=vs.85\).aspx)。当进程以及线程句柄创建或者复制时，驱动就会得到通知。

从 **PsSetCreateProcessNotifyRoutineEx**
发出的通知可以用来配置新创建进程的保护结构。随后，当进程尝试打开VBOX驱动的句柄时，加固机制会调用[
**supHardenedWinVerifyProcess**](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPHardenedVerifyProcess-win.cpp?rev=67954#L2420)函数，确保如下验证步骤通过后才允许相应的访问动作：

1、确保没有调试器附加到进程上。

2、确保进程中只有一个线程，并且该线程是打开驱动的唯一线程，以避免出现进程内竞争（in-process races）问题。

3、确保除了一小部分允许的DLL之外，没有其他可执行的内存页面。

4、验证所有已加载的DLL的签名。

5、验证主执行文件的签名，确保该文件为允许的执行文件类型（如VirtualBox.exe）。

VBOX将自定义运行时代码编译到驱动中，依靠这部分代码完成内核中的签名校验工作。这个过程中，只有很少一部分可信根（Trusted
Roots）才能通过校验，主要包括微软的操作系统及代码签名（Authenticode）证书，以及用来签名所有VBOX程序的Oracle证书。你可以在官方的[代码仓库](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/Certificates?rev=67954)中找到可信的证书列表。

ObRegisterCallback通知用来限制系统上其他用户进程对被保护进程的访问权限范围。ObRegisterCallback
API主要是针对反病毒服务设计，以避免反病毒进程被恶意代码注入或者终止。VBOX使用了类似的方法，限制受保护进程的句柄只能具备如下访问权限：

PROCESS_TERMINATE

PROCESSVMREAD

PROCESSQUERYINFORMATION

PROCESSQUERYLIMITED_INFORMATION

PROCESSSUSPENDRESUME

DELETE

READ_CONTROL

SYNCHRONIZE

这些访问权限可以赋予用户通常需要的大多数权限，比如他们可以读取内存、同步进程以及结束进程，然而他们无法将新的代码注入到进程中。类似地，用户对线程的访问权限也被限制在如下范围，以阻止对线程上下文的修改或其他类似攻击：

THREAD_TERMINATE

THREADGETCONTEXT

THREADQUERYINFORMATION

THREADQUERYLIMITED_INFORMATION

DELETE

READ_CONTROL

SYNCHRONIZE

为了证实这一点，我们可以打开VirtualBox的进程或者其中某个线程，查看我们获得的访问权限。我们获得的有关进程以及线程的访问权限如下图高亮部分所示。

虽然内核回调能够阻止对进程的直接修改，也能阻止用户在进程启动时破坏进程的完整性，然而内核回调对运行时的DLL注入攻击（如通过COM实现的DLL注入）显得有点乏力。进程加固机制需要确定哪些模块可以被载入到进程中。对可载入模块的筛选主要是通过Authenticode代码签名来实现。

现在已经有一些方法可以确保只加载经过微软签名的二进制文件（比如[
**PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY**](https://msdn.microsoft.com/en-us/library/windows/desktop/mt706242\(v=vs.85\).aspx)方法），然而，这种策略不是特别灵活。因此，受保护的VBOX进程会安装一些钩子（hook），hook用户模式下的几个内部函数，以验证将要载入内存的DLL的完整性。被hook的函数为：

[LdrLoadDll](https://undocumented.ntinternals.net/index.html?page=UserMode%2FUndocumented%20Functions%2FExecutable%20Images%2FLdrLoadDll.html)。调用该函数来将DLL加载到内存中

[NtCreateSection](https://msdn.microsoft.com/en-us/library/windows/hardware/ff566428\(v=vs.85\).aspx)。调用该函数来为磁盘上的PE文件创建一个Image
Section对象。

[LdrRegisterDllNotification](https://msdn.microsoft.com/en-us/library/dd347461\(v=vs.85\).aspx)。这是一个准官方支持的回调函数，当新的DLL被加载或卸载时，该函数就会通知应用程序相关事件。

这些钩子扩大了可被加载的经过签名的DLL的范围。由于内核中只包含Oracle以及微软代码，因此可以通过签名验证，能够用来引导进程。然而，当运行某个较为特别的应用时（VirtualBox.exe显然是个特别的应用），我们可能就需要加载第三方签名的代码（比如GPU驱动）。由于这些钩子位于用户模式下，因此程序可以很方便地调用系统的[WinVerifyTrust](https://msdn.microsoft.com/en-us/library/windows/desktop/aa388208\(v=vs.85\).aspx)
API函数，使用系统证书库来验证证书链，也可以验证使用[Catalog](https://docs.microsoft.com/en-us/windows-hardware/drivers/install/catalog-files)（.cat）文件签名的那些文件。

如果正在加载的某个DLL无法满足VBOX预期的签名标准，那么用户模式下的钩子就会拒绝加载这个DLL。VBOX仍然没有完全信任该用户，WinVerifyTrust会将证书链接回用户的CA证书中的根证书。然而，VBOX只会信任系统的CA证书。由于非管理员用户无法将新的可信根证书添加到系统的CA证书列表中，因此使用这种方法就可以大大限制恶意DLL的注入攻击。

当然，你可以使用合法的经过认证的签名证书，这样应该就能被程序信任，但一般情况下恶意代码不会走这条路。即使代码经过签名，加载程序同样会验证这个DLL文件是否属于TrustedInstaller用户所有。这个验证过程由[supHardNtViCheckIsOwnedByTrustedInstallerOrSimilar](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPHardenedVerifyImage-win.cpp?rev=67954#L454)来实现。除了自己以外，普通用户无法将文件的所有者改成其他人，因此这样就能限制加载任意签名文件可能造成的危害。

VBOX代码中的确存在一个函数（[supR3HardenedWinIsDesiredRootCA](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPHardenedVerifyImage-win.cpp?rev=67954#L1901)），可以限制哪些证书能够成为根证书。在官方发行版中，虽然这个函数中与CA白名单有关的代码已经被注释掉，然而却存在一个黑名单列表，只要你的公司名不叫做“[U.S.
Robots and Mechanical Men,
Inc](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPHardenedVerifyImage-win.cpp?rev=67954#L2016)”，那么这个黑名单就不会影响到你。

即使存在这些保护机制，对管理员而言，进程仍然处于不安全的状态。虽然管理员无法绕过打开进程时存在的安全限制条件，但是他们可以在本地主机中安装一个Trusted
Root CA证书，签名一个DLL文件，设置DLL文件的所有者然后强制加载该DLL。这种方法可以绕过镜像验证机制，将镜像加载到经过验证的VBOX进程中。

稍微总结一下，VBOX加固机制尝试提供如下几种保护措施：

1、确保在受保护程序初始化过程中，没有任何代码可以插入进来。

2、阻止用户进程打开受保护进程或线程的“可写”句柄，因为这种句柄可以实现任意代码注入。

3、阻止不可信DLL通过常见的加载方法（如COM）进行注入。

整个保护过程很有可能会存在一些bug或者没考虑到的边缘情况。这个过程中，有这么多不同的验证检查操作，这些检查必须全部满足。因此，假如我们不想申请一个合法的代码签名证书，我们也不具备管理员权限，那么这种情况下，我们要如何才能实现在受保护VBOX进程中运行任意代码？我们会重点关注第三种保护措施，因为这可能是所有保护措施中最为复杂的一种，因此很有可能存在最多的问题。

  

**三、利用COM注册中的信任链（Chain-of-Trust）**

****

我想介绍的第一个[漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1103)为
**CVE-2017-3563** 漏洞，这个漏洞在VBOX 5.0.38/5.1.20版本中被修复。该漏洞利用了DLL加载中存在的信任链（chain-of-trust）问题，诱导VBOX加载经过微软签名的DLL，最终实现不可信任意的代码执行。

如果运行[ **Process Monitor**](https://docs.microsoft.com/en-us/sysinternals/downloads/procmon)来观察受保护的VBOX进程，你会发现该进程使用了COM，更具体来说，该进程使用了在
**VBoxC.dll** COM服务器中实现的VirtualBoxClient类。

从攻击者的角度来看，COM服务器注册最有用的地方，在于COM对象的注册操作可以在两个地方完成，即用户的注册表中或者本地主机（local
machine）注册表中。出于兼容性方面的考虑，系统会优先查找用户的注册表，然后再查找本地主机注册表。因此，在普通用户权限下，攻击者可以覆盖COM注册操作，此时当某个应用程序试图加载指定的COM对象时，就会加载我们刚刚覆盖的任意DLL。

劫持COM对象并不是一种新颖的技术，这种技术已经存在多年，许多恶意软件利用这种技术来[实现持久化](https://attack.mitre.org/wiki/Technique/T1122)目的。随着众人重拾对COM的兴趣，这种技术又再度出现在公众视野中。然而，除了UAC绕过之外，COM劫持很少用来权限提升场景中。

除此之外，UAC以及COM劫持之间还存在着联系，COM运行时会主动去防止劫持技术用于权限提升（EoP）场景，采用的具体方法是，如果当前进程处于高权限下，那么COM运行时就会禁用特定的用户注册表的读取。当然这种方法不是每次都能[成功](https://www.virusbulletin.com/uploads/pdf/conference_slides/2011/Larimer-VB2011.pdf)。只有当你将UAC当成一种安全防御屏障时，这种方法才行之有效，然而微软坚称他们从来没有也永远不会承认过这个观点。例如，2007年初的[这篇文章](https://blogs.msdn.microsoft.com/cjacks/2007/02/21/per-user-com-registrations-and-elevated-processes-with-uac-on-windows-vista/)就明确指出这种方法是用于阻止权限提升操作。在我看来，COM的这种查找行为清楚地表明，UAC的设计初衷就是想成为一道安全屏障，然而，它并没有实现这一目标，因此只好被重新[包装](https://technet.microsoft.com/en-us/library/2007.06.uac.aspx)，用来帮助“开发者”开发更好的代码。

如果我们可以将自己的代码替换COM注册，那么我们应该就能实现在受保护的进程中运行代码。从理论上讲，所有的加固签名检查步骤应该都会阻止我们加载不可信的代码。在实际的研究过程中，我们还是应当具体尝试一下我们觉得会失败的那些操作，万一梦想实现就会收获巨大惊喜。经过尝试后，我们至少可以了解保护机制的具体工作流程。我在用户注册表中注册了一个COM对象，来劫持VirtualBoxClient类，将其指向一个未签名的DLL（实际上我使用了某个管理员账户将DLL的所有者改成
**TrustedInstaller** ，当然这只是为了测试方便）。当我尝试启动虚拟机时，程序弹出了如下对话框。

可能我在COM注册时犯了点错误，然而在另一个独立的应用程序中测试这个COM对象时，却显示一切正常。因此，这个错误很有可能意味着程序无法加载DLL。幸运的是，VBOX非常慷慨，默认就提供了所有进程加固事件的日志。日志名为
**VBoxHardening.log**
，位于当前虚拟机目录中的Logs文件夹中。在日志中查找DLL的名字，我们得到如下日志条目（我做了大量精简操作，以方便说明）：

    
    
    supHardenedWinVerifyImageByHandle: -> -22900 (c:dummytestdll.dll) 
    supR3HardenedScreenImage/LdrLoadDll: c:dummytestdll.dll: Not signed. 
    supR3HardenedMonitor_LdrLoadDll: rejecting 'c:dummytestdll.dll' 
    supR3HardenedMonitor_LdrLoadDll: returns rcNt=0xc0000190

因此，可以确认的是我们的测试DLL没有签名，所以LdrLoadDll hook拒绝加载这个DLL。LdrLoadDll
hook返回了一个错误代码，这个代码会传递给COM DLL加载器，导致COM认为该类不存在。

虽然事情并不是简单通过指定自己的DLL就能完成（别忘了我们还修改了DLL的所有者属性），但这至少给了我们一丝希望，因为结果表明VBOX进程还是会使用我们劫持过的COM注册。因此，我们需要的就是满足以下条件的一个COM对象：

1、由可信证书进行签名。

2、所有者为TrustedInstaller。

3、当加载时，可以实现在进程中执行任意代码。

条件1以及条件2很容易就能满足，系统中所有的微软COM对象都经过可信证书签名（微软内置的某个发行商证书），并且大多对象的所有者为TrustedInstaller。然而，条件3看起来非常难以满足，COM对象通常是在DLL内部实现的，我们不能修改DLL文件，否则文件就会变成未签名状态。我们最终还是找到了这样一个文件，这是一个默认安装的经过微软签名的COM对象，可以帮助我们满足条件3，这就是[Windows脚本组件](https://technet.microsoft.com/en-us/library/ee692848.aspx)（Windows Script Components，WSC）。

WSC有时候也称之为Scriptlets（脚本小程序），是可以利用的优秀运行载体。从HTTP
URL加载时，我们可以使用WSC来[绕过AppLocker](http://subt0x10.blogspot.co.uk/2017/04/bypass-application-whitelisting-script.html)。在这里，最让我们感兴趣的是它们也可以注册为COM对象。

经过注册的WSC包含如下两个部分：

1、WSC运行时：scrobj.dll，承担进程内部的COM服务器角色。

2、包含Scriptlet实现的一个文件，由兼容的脚本语言编写而成。

当某个应用程序试图加载注册后的类时，scrobj.dll就会加载到内存中。这个COM运行时会请求对应类的一个新对象，导致WSC运行时会在注册表中查找与Scriptlet文件对应的那个URL。然后，WSC运行时会加载Scriptlet文件，在进程中执行文件内部包含的脚本。这里最关键的一点是，从VBOX角度来看，只要scrobj.dll（还有其他相关的脚本语言库，如JScript.dll）是合法的DLL签名文件，那么脚本代码就会得到运行机会，因为VBOX的加固代码永远不会去检查这些脚本代码。这样我们就能实现在加固进程内部运行任意代码的目的。首先，我们来确认scrobj.dll的确可以被VBOX加载。如下图所示，这个DLL经过微软的签名，并且其所有者为TrustedInstaller。

那么，有效的Scriptlet文件应该满足什么格式？Scriptlet文件是简单的XML文件，我不会去详细阐述每个XML元素所代表的含义，只会重点突出其中涉及任意JScript代码的脚本段。在这个例子中，当被加载时，Scriptlet会启动计算器（Calculator）进程：

    
    
    <scriptlet>
      <registration
        description ="Component"
        progid="Component"
        version="1.00"
        classid="{DD3FC71D-26C0-4FE1-BF6F-67F633265BBA}"
      />
      <public/>
      <script language = "JScript" >
      <![CDATA[
      new ActiveXObject('WScript.Shell').Exec('calc');
      ]]>
      </script>
    </scriptlet>

如果你在JScript或者VBScript语言方面造诣颇深，那么你可能会注意到一个问题，如果这些语言不是通过COM对象来实现，那么它们就无法达成我们的目的。在上面这个Scriptlet文件中，如果我们不加载WScript.Shell这个COM对象，然后调用其Exec方法，那么我们就不能创建新的进程。为了与VBOX驱动交流（这是注入代码的必经之地），我们必须需要能够提供该功能的一个COM对象。我们不能在另一个COM对象中实现具体代码，因为这样就无法绕过镜像签名检查过程。当然，脚本引擎中存在许多[内存破坏漏洞](https://bugs.chromium.org/p/project-zero/issues/list?can=1&q=javascript)，但我个人并不喜欢利用内存破坏漏洞，因此我们需要其他方法来实现任意代码执行。这时该轮到
.NET Framework上场了。

.NET运行时使用了常规的DLL加载方法来将代码加载到内存中。因此我们不能加载未签名的 .NET
DLL，因为VBOX加固代码会拦截这种行为。然而，.NET提供了一种[Assembly::Load](https://msdn.microsoft.com/en-us/library/h538bck7\(v=vs.110\).aspx)方法，利用这种方法可以通过内存中的数组来加载任意代码，并且一旦加载完成，这段代码看起来就如同原生代码（native
code）一样，可以调用任意API、检查或修改内存。由于
.NET平台经过微软的签名，因此我们需要做的就是从我们的Scriptlet文件中调用Load方法，然后我们就可以在进程内部获得完整的任意代码执行权限。

为了实现这个目标，我们应该从哪里开始呢？根据之[前一篇文章](https://googleprojectzero.blogspot.co.uk/2017/04/exploiting-net-managed-dcom.html)的研究结果，我们可以通过注册方式将.NET对象导出为COM对象，再通过二进制序列化（Binary
Serialization）方法，从字节数组中加载任意代码。许多.NET核心运行时类已经被自动注册为COM对象，脚本引擎可以加载并修改这些对象。现在，我们需要确定的是，BinaryFormatter究竟有没有导出为COM对象？

事实证明的确如此。BinaryFormatter是一个.NET对象，脚本引擎可以通过COM来加载这个对象并与之交互。现在，我们可以直接使用上一篇文章的二进制流，从内存中执行任意代码。在上一篇文章中，不可信代码的执行必须在反序列化过程中完成，在本文案例中，我们可以与脚本中的反序列化结果交互，这样一来，我们需要做的序列化操作就会大大简化。

最后我选择反序列化一个[Delegate](https://msdn.microsoft.com/en-us/library/system.delegate\(v=vs.110\).aspx)（委托）对象，当脚本引擎执行这个对象时，就会从内存中加载一个[Assembly](https://msdn.microsoft.com/en-us/library/system.reflection.assembly\(v=vs.110\).aspx)（程序集），并返回Assembly实例。然后，脚本引擎可以实例化Assembly中的一个Type实例，运行任意代码。原理上听起来很简单，实际操作起来还是有许多事项需要注意。我不想在这篇文章里面讲述具体的细节，以免打断整体节奏，你可以访问此链接获取[DotNetToJScript](https://github.com/tyranid/DotNetToJScript)这个工具，顺便了解工具的工作原理。此外，你可以访问[此链接](https://bugs.chromium.org/p/project-zero/issues/attachment?aid=268607)获取PoC代码。从JSciprt组件到调用VBOX驱动的过程大概如下所示：

现在你已经可以在受保护进程中运行任意代码，我不会详细介绍利用VBOX驱动可以做哪些事情，这是另一个话题。当然你可以参考Jann写的[另一篇文章](https://bugs.chromium.org/p/project-zero/issues/detail?id=1091)，其中介绍了这种情况下，你可以在Linux系统上做的一些操作。

Oracle如何修复这个问题？他们添加了一个DLL黑名单，在[黑名单](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPHardenedVerifyImage-win.cpp?rev=67954#L146)中的DLL无法被受保护的VBOX进程加载。目前，这个名单中仅包含scrobj.dll这个文件。当开始验证文件时，程序就会验证文件是否位于黑名单中，程序会对当前文件名及版本资源内部的原始文件名（Original
Filename）进行检查。这样就能防止用户通过重命名文件绕过黑名单，并且版本资源数据位于签名的PE数据中，攻击者无法在不破坏签名的前提下修改内部的原始文件名。坦诚说来，除了DLL黑名单机制，我也想不出来有其他较好的方法能够阻止这类攻击。

  

**四、利用用户模式下的DLL加载方式**

我想介绍的第二个[漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1257)为
**CVE-2017-10204** 漏洞，这个漏洞在VBOX 5.1.24版本中被修复。该漏洞利用了Windows
DLL加载器以及VBOX中的某些错误，诱导VBOX加固代码将未经验证的DLL加载到内存中并加以执行。

虽然这个漏洞不需要依赖前面描述过的COM加载逻辑，但用户模式下的COM加载技术的确非常好用，可以使用任意路径来调用[LoadLibrary](https://msdn.microsoft.com/en-us/library/windows/desktop/ms684175\(v=vs.85\).aspx)函数。因此我们会继续利用这种技术来劫持VirtualBoxClient
COM对象，利用进程内的服务器路径来加载DLL。

LoadLlibrary是一个Windows
API，该函数存在大量已知的非常奇怪的行为。就我们看来，其中最为有趣的一个行为就是该函数在文件扩展名方面的处理逻辑。根据具体扩展名的不同，LoadLibrary
API在加载文件之前，可能会添加或移除相应的扩展名。为此，我用一个表稍微总结了一下，表中显示了传递给LoadLibrary的具体扩展名以及该函数真正尝试加载的那个文件。

在上表中，我用绿色高亮了两种比较重要的情况。这两种情况下，传递给LoadLibrary的文件名与最终加载的文件名不一致。这里的问题在于，任何程序想在加载DLL之前验证该文件的话，就会用到CreateFile函数，而该函数并不会遵循我们高亮的那两种情况。因此在这两种情况下，如果我们使用原始文件名来打开文件并做签名校验，实际上我们最终加载的是另一个文件，因此我们要对另一个文件做签名校验。

在Windows中，普通代码与Kernel32代码之间通常 **存在明显的分离界限**
，Kernel32代码主要是负责处理Win32平台上已存在多年的许多奇怪行为，也负责处理内核通过 **NTDLL**
对外提供的“纯净”的NT逻辑层。由于LoadLibrary的实现位于Kernel32中，而LdrLoadDll的实现位于NTDLL中（LdrLoadDll也是VBOX加固代码所hook的那个函数），因此，前面提到的扩展名处理逻辑应该由前者来负责。我们可以分析一下简化版的LoadLibrary，看情况是否如此：

    
    
    HMODULE LoadLibrary(LPCWSTR lpLibFileName)
    {
      UNICODE_STRING DllPath;
      HMODULE ModuleHandle;
      ULONG Flags = // Flags;
      RtlInitUnicodeString(&DllPath, lpLibFileName);  
      if (NT_SUCCESS(LdrLoadDll(DEFAULT_SEARCH_PATH, 
          &Flags, &DllPath, &ModuleHandle))) {
        return ModuleHandle;
      }
      return NULL;
    }

从这段代码中可知，不论具体情况如何， **LoadLibrary** 只是 **LdrLoadDll**
的一个封装函数。虽然实际代码比上述代码更为复杂，但简而言之，当LdrLoadDll将文件路径传递给LdrLoadDll时，LoadLibrary并没有作修改，只是将其转换为
**UNICODE_STRING**
形式的字符串而已。因此，如果我们传入一个没有扩展名的DLL时，VBOX会检查无扩展名的文件的签名，而LdrLoadDll会使用.DLL扩展名来加载文件。

在我们开始测试之前，我们需要解决另一个问题，即文件的所有者需为 **TrustedInstaller**
。为了让VBOX检查我们所提供的文件的签名，我们只需要将某个已有的、经过合法签名的文件重命名即可，这个任务可以交给硬链接（hard
links）来完成。我们可以在某个可控的目录中创建一个不同的文件名，该文件实际上指向的是某个经过签名的系统文件，同时还可以维持文件的原始安全描述符属性（包括文件所有者属性）。正如我在两年前的[一篇文章](https://googleprojectzero.blogspot.co.uk/2015/12/between-rock-and-hard-link.html)中提到的那样，硬链接存在的问题是，虽然Windows支持创建指向系统文件的链接（当然你无法以写权限打开这些系统文件），然而Win32
API以及在CMD命令行中使用的“[mklink](https://technet.microsoft.com/en-us/library/cc753194\(v=ws.11\).aspx)”命令都需要以 **FILE_WRITE_ATTRIBUTES**
访问权限打开目标文件。我们不想使用其他程序来创建硬链接，因此我们复制了目标文件，但复制操作会修改文件的原始安全描述符，使得该文件所有者不再为TrustedInstaller。为了解决这一问题，我们来检查一下验证代码，看有没有方法能绕过这个难题。

文件所有者的检查主要在 **supHardenedWinVerifyImageByLdrMod** 函数中完成。这个函数做的第一件事情基本上就是调用
**supHardNtViCheckIsOwnedByTrustedInstallerOrSimilar**
函数，后者我们在之前已经见到过。然而，正如在源码中注释部分说明的那样，这段代码还允许使用System32以及WinSxS目录下所有者不为TrustedInstaller的那些文件。这些位置对检查过程来说简直是非常广阔的可利用点，我们要做的只是找到System32下可写入的一个目录。我们可以利用我开发的NtObjectManager
PS模块中的 **Get-AccessibleFile cmdlet** 来找到这些目录。

如上所述，有很多目录可以为我们所用，我们选择了Tasks目录作为目标，因为这个目录肯定会存在。因此，漏洞利用过程包含如下步骤：

1、将某个已签名的程序拷贝到 **%SystemRoot%System32TasksDummyABC**

2、将某个未签名的程序拷贝到 **%SystemRoot%System32TasksDummyABC.DLL**

3、注册COM劫持，将进程内的服务器指向步骤1中的已签名的文件路径。

如果你启动虚拟机，你会发现上述步骤的确能够成功。VBOX加固代码会检查ABC文件的签名，但LdrLoadDll最终加载的是ABC.DLL。为了确认我们没有利用涉及其他操作，我们来检查一下加固代码的日志：

    
    
    ..TasksdummyABC: Owner is not trusted installer 
    ..TasksdummyABC: Relaxing the TrustedInstaller requirement for this DLL (it's in system32).
    supHardenedWinVerifyImageByHandle: -> 0 (..TasksdummyABC) 
    supR3HardenedMonitor_LdrLoadDll: pName=c:..tasksdummyABC [calling]

前两行表明文件所有者属性的检查的确已被绕过，如我们预期的那样。接下来的两行表明程序验证通过ABC文件的签名，因此会调用LdrLoadDll，后者会添加文件的扩展名，尝试加载ABC.DLL。稍等，为什么NtCreateSection以及加载回调函数（Loader
Callback）没有捕捉到程序正在加载一个完全不同的文件？我们可以在加固日志中搜索ABC.DLL，看一下具体发生了什么：

    
    
    ..TasksdummyABC.dll: Owner is not trusted installer 
    ..TasksdummyABC.dll: Relaxing the TrustedInstaller requirement for this DLL (it's in system32). 
    supHardenedWinVerifyImageByHandle: -> 22900 (..TasksdummyABC.dll) 
    supR3HardenedWinVerifyCacheInsert: ..TasksdummyABC.dll 
    supR3HardenedDllNotificationCallback: c:..tasksdummyABC.DLL 
    supR3HardenedScreenImage/LdrLoadDll: cache hit (Unknown Status 22900) on ...TasksdummyABC.dll

前面两行依然说明，我们文件所处的位置使得我们绕过了文件所有者的检查。接下来的一行，有关
**supHardenedWinVerifyImageByHandle**
的日志显得更为有趣。这个函数用来验证镜像文件。我在上文展示的日志中提到过这个函数，当时这个函数返回的是-22900，这个值表明有错误发生。然而，在上面的日志中，这个函数返回的是22900，VBOX将任何大于等于0的返回值都当成成功的返回值，加固代码没见过这种返回值，因此也会认为这个文件为有效的文件。在源代码中，负值的错误代码为
**VERR_LDRVI_NOT_SIGNED** ，正值的“成功”代码为 **VINF_LDRVI_NOT_SIGNED** 。

貌似验证代码在调用[DLL Loader Lock](https://msdn.microsoft.com/en-us/library/windows/desktop/dn633971\(v=vs.85\).aspx)中的代码时存在错误，这与
**NtCreateSection**
中的hook情况类似。当代码尝试加载另一个DLL时，它就无法调用WinVerifyTrust，因此会发生死锁现象。通常情况下，内部签名检查代码会返回
**VINF_LDRVI_NOT_SIGNED**
。现有的代码实现只能处理具有内嵌签名的文件，因此如果某个文件没有经过签名，程序就会返回一个信息代码，促使验证代码来检查文件是否经过catalog（.cat）签名。正常情况下，
**WinVerifyTrust** 会被调用，如果文件仍然没有经过签名，那么该函数就会返回错误代码。然而，由于死锁问题，
**WinVerifyTrust** 无法被调用，因此信息代码会广播给调用者，作为成功代码加以使用。

最后一个问题，为什么最终的加载回调函数没有捕捉到未签名的文件？VBOX基于文件路径实现了一种签名文件缓存机制，以避免某个文件被多次检查。当程序认为
**supHardenedWinVerifyImageByHandle** 调用成功时，就会调用
**supR3HardenedWinVerifyCacheInsert**
，将该路径添加到缓存的“成功”结果中。我们可以观察到，在加载器回调函数中，程序尝试验证文件，但会从缓存中得到一个“成功”代码，因此会假设一切正常，从而加载过程可以顺利完成。

这一过程涉及到许多交互操作，那么Oracle如何修复这个问题？如果DLL文件没有扩展名，Oracle就会添加相应的[扩展名](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPR3HardenedMain-win.cpp?rev=67954#L1913)。此外，Oracle针对另一种文件名情况也作了相应处理（加载DLL时会删除文件名尾部的附加字符）。

  

**五、利用内核模式下的镜像加载方式**

****

我想介绍的最后一个[漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=1296)为CVE-2017-10129漏洞，这个漏洞在VBOX
5.1.24版本中被修复。该漏洞实际上并不算是VBOX的漏洞，因为它属于Windows的一种异常行为。

我们需要注意的是，加固代码中存在隐式的条件竞争现象，具体说来，我们可以在验证点以及文件映射点之间修改文件。从理论上讲，我们可以将这种操作应用于VBOX上，但可利用的时间窗口非常短。我们可以选择使用OPLOCK（机会锁）以及类似机制，但这类机制有点麻烦，还不如使用TOCTOU（time-of-check-to-time-of-use）攻击方法。

我们来看看镜像文件在内核中的处理过程。在Windows上执行镜像文件的映射操作是非常麻烦的一件事情，操作系统没有使用位置无关的代码，因此无法将DLL作为简单的文件直接映射到内存中。相反的是，DLL必须重新定位到特定的内存地址。这个过程需要修改DLL文件对应的内存页面，以确保任何相关的指针都被正确修复。当涉及到ASLR时，这个步骤显得更为重要，因为ASLR基本上都会强迫DLL在其基地址基础上进行重新定位。因此，只要条件允许，Windows就会缓存镜像映射的实例，这也是为什么DLL的加载地址在同一个系统的不同进程中不会发生变化的原因，因为它使用的是同一个缓存镜像数据。

缓存实际上位于文件系统驱动的控制之下。当某个文件被打开时，IO管理器会分配[FILE_OBJECT](https://msdn.microsoft.com/en-us/library/windows/hardware/ff545834\(v=vs.85\).aspx)结构体的一个新实例，将该实例传递给驱动的IRPMJCREATE处理程序。驱动可以初始化里面的SectionObjectPointer字段。这个字段对应的是SECTIONOBJECTPOINTERS结构体的一个实例，该结构体的定义如下所示：

    
    
    struct SECTION_OBJECT_POINTERS {
      PVOID DataSectionObject;
      PVOID SharedCacheMap;
      PVOID ImageSectionObject;
    };

这些字段本身由缓存管理器负责管理，但结构体本身必须由文件系统驱动来进行分配。更具体的是，每个文件在文件系统中都对应着不同的分配操作。虽然对某个文件而言，每个打开实例都具有不同的
**FILE_OBJECT**
实例，但SectionObjectPointer只有一个。这样一来，缓存管理器就可以填充结构体中的不同字段，当同一个文件的另一个实例需要映射时，缓存管理器就能重新使用这些字段。

这些字段中，比较重要的字段是 **ImageSectionObject**
，该字段包含映射镜像数据所对应的缓存数据。我不会去深入分析ImageSectionObject指针所包含的具体细节，因为这与文章主题关系不大。重要的是，如果某个FILE_OBJECT实例对应的SectionObjectPointer以及ImageSectionObject指针完全一致，那么将该文件映射为镜像的话，也会映射已缓存的相同镜像。然而，当读取某个文件时并没有用到ImageSectionObject指针，因此系统并没有去检查缓存与硬盘上的实际文件是否相匹配。

在NTFS卷环境下，想要取消SectionObjectPointer的文件数据同步是非常棘手的一件事，特别是当我们没有管理员权限时更是如此。在某种场景下，我们在访问网络共享时，可以借助SMB转向器（redirector）实现数据去同步目的。原理非常简单，当打开远程服务器上的文件时，需要由本地转向器来负责分配SectionObjectPointer结构体的实例。就转向器而言，如果它分两次打开服务器上的“
**ShareFile.dll**
”文件，那么它会认为这两个文件属于同一个文件。转向器没有额外的信息可以使用，无法判断文件的真实身份，因此只能靠猜测来执行具体操作。因此，你能想到的所有属性（比如对象ID（[Object
ID](https://msdn.microsoft.com/en-us/library/windows/hardware/ff540335\(v=vs.85\).aspx)）、修改时间等）都可能是虚假信息。你可以修改SAMBA的副本来实现欺骗目的。此外，转向器无法锁定文件，也无法确保文件处于锁定状态。因此，转向器似乎放弃了这个任务，如果它看到了同一个文件，那么它就会认为一切都处于正常状态。

然而，这种场景仅适用于SectionObjectPointer，如果调用者想读取文件的内容，那么SMB转向器就会退出这种场景，尝试去读取文件的当前状态。此时依然存在虚假信息的可能，因为服务器还是可以返回任意数据。这也是我们为什么能完成去同步化任务，如果我们从SMB服务器上映射某个镜像文件，修改文件底层数据，然后重新打开这个文件，再次映射这个镜像，那么被映射的镜像对应的是已缓存的那个镜像，但读取的数据来自于服务器上的当前文件。这样一来，我们可以先映射一个不可信的DLL，然后将这个文件替换为经过签名的有效文件（SMB支持读取文件的所有者信息，所以我们也能实现伪造所有者为TrustedInstaller的目的），当VBOX试图加载这个文件时，它会验证经过签名的文件，但会映射已缓存的不可信镜像，然而它自己却没有意识到这一点。

很多时候我们无法使用远程服务器，然而我们可以使用本地环回（loopback）SMB服务器，然后通过admin共享（admin$）来访问文件。admin共享其实名不副实，如果我们从本地主机来访问，那么除管理员之外的用户也可以访问这个共享资源。完成这一任务的关键是使用目录连接（Direcory
Junction）技术。Junction点由服务器负责解析，转向器无法获取Junction点的任何信息。因此，在客户端看来，如果客户端之前打开过“
**localhostc$DirFile.dll** ”这个文件，然后重新打开这个文件，那么这两次打开的文件可能是完全不同的文件，整个流程如下图所示：

幸运的是，根据前面两个问题的分析结果，我们知道VBOX的加固代码并不在意DLL文件的具体位置，只要能够满足两个条件即可，即文件所有者为TrustedInstaller且文件经过合法签名。我们可以将COM劫持指向本地系统中的某个SMB共享。因此，我们可以按照如下步骤实施攻击：

1、在C:盘上设置一个junction点，将其指向我们不可信文件所在的那个目录。

2、在c$ admin共享的junction点上使用LoadLibrary映射这个文件，在攻击过程结束之前，不要释放映射文件。

3、修改junction点，将其指向一个有效的经过签名的文件，文件名与我们不可信文件的文件名一致。

4、将COM劫持指向这个文件，然后启动VBOX。VBOX会读取文件，验证文件经过签名并且文件所有者为TrustedInstaller，然而当它使用这个文件时，实际上使用的是已缓存的不可信的镜像数据。

那么Oracle如何修复这个问题？Oracle会将文件路径与“[DeviceMup](https://www.virtualbox.org/browser/vbox/trunk/src/VBox/HostDrivers/Support/win/SUPR3HardenedMain-win.cpp?rev=67981#L1644)”前缀进行对比，以验证映射的文件是否位于网络共享中。

  

**六、总结**

****

VirtualBox中实现的进程加固机制非常复杂，因此也非常容易出错。我敢肯定的是，只要人们用心去寻找，还能找到其他方法来绕过进程保护机制。当然，如果Oracle不想保护VirtualBox内核驱动免受恶意攻击场景利用，那么这一切都不是问题，然而这属于设计理念问题，短时间内很难解决。

本文翻译自googleprojectzero.blogspot.hk
[原文链接](https://googleprojectzero.blogspot.hk/2017/08/bypassing-virtualbox-process-hardening.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86714](/post/id/86714)

安全客 - 有思想的安全新媒体

本文转载自:
[googleprojectzero.blogspot.hk](https://googleprojectzero.blogspot.hk/2017/08/bypassing-virtualbox-process-hardening.html)

如若转载,请注明出处： <https://googleprojectzero.blogspot.hk/2017/08/bypassing-virtualbox-process-hardening.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

