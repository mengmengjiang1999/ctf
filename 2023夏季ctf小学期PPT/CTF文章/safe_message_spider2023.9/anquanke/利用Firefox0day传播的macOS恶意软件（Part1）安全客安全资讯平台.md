# 利用Firefox 0day传播的macOS恶意软件（Part 1）

阅读量 **216574**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-06-28 14:30:26

 **x**

##### 译文声明

本文是翻译文章，文章原作者 objective-see，文章来源：objective-see.com

原文地址：<https://objective-see.com/blog/blog_0x43.html>

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00 前言

大概在一星期之前，我收到了某个用户发出的一封邮件：

> 上周三，攻击者通过尚未公开的一个Firefox 0day攻击了我，不知道用什么方法将一个程序释放到我的mac主机上（10.14.5）然后执行。
>
> 我觉得你可能对这个文件比较感兴趣，这可能是绕过gatekeeper的一种有趣方法，值得研究一下。

我当然很感兴趣，但当时我正在写另一篇文章（大家可以点击[此处](https://objective-see.com/blog/blog_0x42.html)阅读该文章），有点腾不出手来。

现在尘埃落定，我想借此机会深入研究这次攻击行为，分析其中涉及到的持久化恶意软件。

## 0x01 Firefox 0day

用户联系我时，我还没有太多掌握此次攻击中使用的Firefox 0day，然而现在我已经拿到了足够多信息。

一开始用户提供的邮件内容如下（翻译版）：

> XXX：
>
> 您好，我叫Neil Morris，是亚当斯奖（Adams Prize）组委会的一名成员。
>
>
> 每年我们都会更新独立专家团队成员，这些专家需要评审参选项目（[http://people.ds.cam.ac.uk/nm603/awards/Adams_Prize）的质量。](http://people.ds.cam.ac.uk/nm603/awards/Adams_Prize%EF%BC%89%E7%9A%84%E8%B4%A8%E9%87%8F%E3%80%82)
>
> 我的同事推荐您加入这一领域的专家团队中。
>
> 我们需要您参评竞争亚当斯奖的几个项目。
>
> 期待您的回复。
>
> 祝好，
>
> Neil Morris

这里提一下，即便攻击者拥有浏览器0day利用技术，他们仍需要找到方法将攻击payload投递给目标用户。

选定目标后，攻击者通常会选择电子邮件作为投递方式，邮件中包含指向恶意网站的链接（当用户访问该网站时可以投递漏洞利用payload）。

不幸的是，当时该链接（`people.ds.cam.ac.uk/nm603/awards/Adams_Prize`）已失效，返回`404 Not
Found`错误：

    
    
    $ curl http://people.ds.cam.ac.uk/nm603/awards/Adams_Prize
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL /nm603/awards/Adams_Prize was not found on this server.</p>
    <hr>
    <address>Apache/2.4.7 (Ubuntu) Server at people.ds.cam.ac.uk Port 80</address>
    </body></html>
    

当然有可能该站点只为该攻击活动提供服务，只有当用户通过存在漏洞的Firefox浏览器、或者通过特定IP地址等来访问时，才会触发攻击过程。也有可能攻击过程已经结束，攻击者关闭了该站点。

虽然我无法获得利用代码，但用户依然向我提供了攻击过程中安装在他系统中的恶意软件（名为`Finder.app`）。

本文将对这款恶意软件进行详细分析（哈希：`23017a55b3d25a2597b7148214fd8fb2372591a5`）。

    
    
    $ shasum -a 1 ~/Attack/Finder.app/Contents/MacOS/Finder 
    23017a55b3d25a2597b7148214fd8fb2372591a5  Finder
    

有趣的是，来自Coinbase的一名安全研究者（[Philip
Martin](https://twitter.com/SecurityGuyPhil)）在今天发表了一则比较有趣的[推文](https://twitter.com/SecurityGuyPhil/status/1141466339518767104)：

![](https://p2.ssl.qhimg.com/t01f9ef279852cef110.png)

Phil提供的哈希值（`23017a55b3d25a2597b7148214fd8fb2372591a5`）刚好与用户发给我的恶意文件相匹配。此外用户还提到一个信息，最近他“参与了加密货币交易事宜”。综合这些信息，很有可能我和Phil讨论的都是同一个Firefox
0day。

这个0day现在对应的编号为CVE-2019-11707，已经被修复，其他文章中也提到了这个漏洞：

  * “[Mozilla patches Firefox zero-day abused in the wild](https://www.zdnet.com/article/mozilla-patches-firefox-zero-day-abused-in-the-wild/)”
  * “[Mozilla Patches Firefox Critical Flaw Under Active Attack](https://threatpost.com/mozilla-patches-firefox-critical-flaw-under-active-attack/145814/)“

然而，关于攻击中使用的后门恶意软件资料较少（或者没有），因此我们可以深入分析一下。

## 0x02 Mac后门分析（OSX.NetWire.A）

前面提到过，受害者向我提供了攻击者（通过Firefox 0day）安装在系统上的恶意后门（`Finder.app`）。

![](https://p3.ssl.qhimg.com/t0171558b4e2d262494.png)

在VirusTotal上搜索对应的哈希后（`23017A55B3D25A2597B7148214FD8FB2372591A5`），我找到了一个匹配结果，显示这个文件已于2019-06-06提交，但目前只有一个反病毒引擎能够检测到：

![](https://p1.ssl.qhimg.com/t015f1b6430a5526b03.png)

> 备注：完整的应用程序包`Finder.app`今天才被提交到VirusTotal上，同样只有一个AV引擎能够检测。

有趣的是，这个反病毒引擎将其标记为`OSX.Netwire`。

`OSX.Netwire`（或者`OSX.Wirenet`）最早于2012年被Dr
Web发现。在这篇[研究文章](https://news.drweb.com/show/?i=2679&lng=en)中，Dr
Web表示这是“历史上第一款能够窃取Linux及MacOS X密码的后门”。

恶意软件通过键盘记录器以及/或者直接通过磁盘上的文件（比如已保存的浏览器登录信息）来窃取密码：

    
    
    $ strings malware/2012/OSX.Netwire
    
    %s/Library/Opera/wand.dat
    %s/.Library/Opera/wand.dat
    
    SeaMonkey
    Thunderbird
    
    %s/Library/Application Support/Firefox
    
    %s/signons.sqlite
    
    NSS_Init
    PK11_GetInternalKeySlot
    PK11_Authenticate
    NSSBase64_DecodeBuffer
    
    select *  from moz_logins
    

但这是2012年时的`OSX.Netwire`，现在这款恶意软件是否还是`OSX.Netwire`？我个人从2012年后再也没听到过关于`OSX.Netwire`的任何信息，因此决定研究一下。

首先，我们可以通过简单的字符串匹配方法，确认2012年的样本与2019年的样本有所关联。

比如，2012年样本中包含`\x03\x04\x15\x1A\r\nexit\r\n\r\nexit\n\n`字符串：

    
    
    esi = "/bin/sh";
    if(access(esi) != 0x0) {
       esi = "/bin/bash";
    }
    
    ...
    
    eax = write$UNIX2003(*0x140d0, "x03x04x15x1Arnexitrnrnexitnn", 0x15);
    

同样，2019年样本中也包含该特征：

    
    
    if(stat("/bin/sh", edi) != 0x0) {
       ebp = "/bin/bash";
    }
    
    ...
    
    write$UNIX2003(ebx, "x03x04x15x1Arnexitrnrnexitnn", 0x15)
    

此外还有一些特殊的字符串也能在两个样本中找到。

在与小伙伴（安全研究员）交流时，他注意到XProtect已经能够检测到这个新样本。

>
> XProtect是Apple在macOS中内置的反恶意软件系统，大家可以参考[此处](https://www.howtogeek.com/217043/xprotect-> explained-how-your-macs-built-in-anti-malware-works/)了解更多信息。

我对此有所怀疑（因为我记得XProtect最近并没有关于`OSX.Netwire`的任何更新），然而事实证明小伙伴是正确的。

2016年，Apple添加了一个Yara特征，用来检测`OSX.Netwire.A`。这个特征（参考`/System/Library/CoreServices/XProtect.bundle/Contents/Resources/XProtect.yara`）如下所示：

    
    
    rule NetwireA
    {
        meta:
            description = "OSX.Netwire.A"
        strings:
            $a = "exitexit"
            $b = "User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like GeckoAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        condition:
            all of them
    }
    

我们可以使用Digita的[UXProtect](https://digitasecurity.com/uxprotect/)工具以图形界面显示该特征：

![](https://p3.ssl.qhimg.com/t0104d00ef9930caeaf.png)

还可以利用[UXProtect](https://digitasecurity.com/uxprotect/)确认（2016年推出的）这个特征依然可以检测此次Firefox
0day攻击中使用的恶意软件：

![](https://p4.ssl.qhimg.com/t01453d9412e109b252.png)

Apple之前提供的特征竟然还能检测这个“新的”威胁！

有趣的是Apple的特征并不能检测2012年的样本（因为该样本不包含`User-Agent:
Mozilla...`）字符串，这表明虽然这两个样本有所关联，但也存在不同之处。

> 目前我还找不到有关于这个新样本的（公开）资料。
>
> 有趣的是，Intego在2016年曾发表过关于Apple XProtect的一篇小文章：[Apple Updates XProtect Malware
> Definitions for NetWeirdRC](https://www.intego.com/mac-security-blog/apple-> updates-xprotect-malware-definitions-for-netweirdrc/)。
>
> 然而，他们（以及其他人）引用的都是2012年的样本，而该样本并不能被Apple的`OSX.Netwire.A` YARA特征检测到。
>
> 通常情况下，这表明Apple已经知道一些信息，但不愿与大家分享，或者也有可能不愿意与我分享：
>
> ![](https://p2.ssl.qhimg.com/t01594a597819334fd0.png)

虽然2012年和2019年的样本明显有关联，但也有很多不同点。我们会在Part
2中透露更多细节，深入分析（新版）恶意软件样本的功能。简而言之，2012年及2019年样本的目标完全不同。我猜测这两款恶意软件都由同一个开发者（或者团队）编写，但服务于不同的目的（比如2012年的样本只关心密码窃取）。

在总结Part 1之前，我们来看一下新版`OSX.NetWire.A`如何实现本地驻留。

快速查看恶意软件的反汇编代码后，我们可以找到其中内置的一个启动代理plist：

    
    
    memcpy(esi, "<?xml version="1.0" encoding="UTF-8"?>n<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//ENnt"http://www.apple.com/DTDs/PropertyList-1.0.dtd">n<plist version="1.0">n<dict>n    <key>Label</key>n    <string>%s</string>n    <key>ProgramArguments</key>n<array>n        <string>%s</string>n    </array>n    <key>RunAtLoad</key>n    <true/>n    <key>KeepAlive</key>n    <%s/>n</dict>n</plist>");
    
    ...        
    eax = getenv("HOME");
    eax = __snprintf_chk(&var_6014, 0x400, 0x0, 0x400, "%s/Library/LaunchAgents/", eax);
    
    ...
    eax = __snprintf_chk(edi, 0x400, 0x0, 0x400, "%s%s.plist", &var_6014, 0xe5d6);
    

因此有理由推测该恶意软件会以启动代理方式实现驻留。

然而，恶意软件中还包含以登录项实现驻留的代码逻辑（注意其中调用了`LSSharedFileListInsertItemURL` API）:

    
    
    eax = __snprintf_chk(&var_6014, 0x400, 0x0, 0x400, "%s%s.app", &var_748C, &var_788C);
    eax = CFURLCreateFromFileSystemRepresentation(0x0, &var_6014, eax, 0x1);
    ...
    
    eax = LSSharedFileListCreate(0x0, **_kLSSharedFileListSessionLoginItems, 0x0);
    
    ...
    eax = LSSharedFileListInsertItemURL(eax, **_kLSSharedFileListItemLast, 0x0, 0x0, edi, 0x0, 0x0);
    

在虚拟机中运行恶意软件后，我们发现恶意软件同时采用了这两种方法。首先是作为启动代理（`com.mac.host.plist`），然后是作为登录项：

    
    
    $ cat ~/Library/LaunchAgents/com.mac.host.plist
    {
        KeepAlive = 0;
        Label = "com.mac.host";
        ProgramArguments =     (
            "/Users/user/.defaults/Finder.app/Contents/MacOS/Finder"
        );
        RunAtLoad = 1;
    }
    

由于这个启动代理（`com.mac.host.plist`）设置了`RunAtLoad`键（值为`1`），因此每次用户登录时，系统会自动运行指定的程序（`.defaults/Finder.app/Contents/MacOS/Finder`）。

登录项也可以确保恶意软件能被运行。然而登录项会显示在UI界面中，这显然不利于恶意软件实现隐蔽驻留：

![](https://p1.ssl.qhimg.com/t017efab8428bc41732.png)

采用两种驻留机制是不是比一种机制更好？不一定，如果大家使用了Objective-See提供的[BlockBlock](https://objective-see.com/products/blockblock.html)工具，就能轻松检测到这两种驻留机制：

![](https://p5.ssl.qhimg.com/t015ea0b2bb3f9a0a99.png)

>
> 关于以登录项（以及`backgroundTaskManagementAgent`角色）实现驻留，大家可以参考我最近的一篇[文章](https://objective-> see.com/blog/blog_0x31.html)了解更多细节。

我们也可以使用[KnockKnock](https://objective-see.com/products/knockknock.html)，通过探测恶意软件的驻留方式来检测系统是否已被感染。

可能恶意软件开发者需要确保自己能万无一失实现驻留，才采用这种攻击方式。

## 0x03 总结

在本文中，我们讨论了针对加密货币交易的一种较为复杂的持久化payload。攻击者利用Firefox 0day将恶意软件部署到目标macOS中。

有趣的是，这个恶意软件为`OSX.NetWire.A`，与2012年同名的样本有一定联系，并且Apple于2016年部署的检测特征能成功发现这款恶意软件，但其实事情没那么简单。

在受害者的原始邮件中，曾提到这款恶意软件可以绕过Gatekeeper。这一点其实很正常，因为恶意软件采用的是远程0day漏洞进行投递。Gatekeeper只会扫描带有隔离属性集的应用程序，而只有当应用程序通过常见方式进行下载时（比如通过用户点击），浏览器等应用或者操作系统才会在下载的程序中添加这些属性集。通过漏洞利用代码下载的payload（比如恶意应用）并不会设置隔离属性（或者可以移除这些属性），因此就不会触发Gatekeeper。

我曾经在2016年的一次[演讲](https://speakerd.s3.amazonaws.com/presentations/9e724ea233434f9fb083bff26bc7fb4b/ShmooCon_2016.pdf)中提到过这一点。

![](https://p3.ssl.qhimg.com/t017c4115c93c7b286f.png)

> 同样，XProtect只会对设置了隔离属性的文件进行操作。然而，macOS
> 10.15（Catalina）可能会[修改](https://eclecticlight.co/2019/06/12/grokking-> gatekeeper-in-catalina/)这种机制。

由于攻击者采用的特殊感染方式（通过Firefox
0day），Gatekeeper以及XProtect都无法保护用户。因此，单纯依赖系统提供的安全保护机制永远都不是明智之举。

本文翻译自objective-see.com [原文链接](https://objective-see.com/blog/blog_0x43.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/181074](/post/id/181074)

安全客 - 有思想的安全新媒体

本文转载自: [objective-see.com](https://objective-see.com/blog/blog_0x43.html)

如若转载,请注明出处： <https://objective-see.com/blog/blog_0x43.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [macOS](/tag/macOS)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

