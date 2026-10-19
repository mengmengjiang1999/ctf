**作者：菜丝@蚂蚁安全实验室  
公众号：[蚂蚁安全实验室](https://mp.weixin.qq.com/s/oUp99tATgNNVu0uyZSD9FA)**

## 1.前 言

相信读者对 XSS 早已不陌生。通常谈论 XSS 的时候大多是针对 Web 安全领域的攻防和利用，而在客户端中也可能出现对输入处理不当而造成的
XSS。蚂蚁安全光年实验室近日在 BlackHat EU 2020 上发表的议题 Cross-Site Escape: Pwning macOS
Safari Sandbox the Unusual Way 就展示了一种针对 Safari 浏览器沙箱的绕过思路，将 Web
安全老生常谈的攻击方式移植到一个看上去毫不相干的领域，将进程间通信（IPC）的安全问题转化成跨组件的 js
脚本注入，最后完全绕过浏览器沙箱获得完整的代码执行权限。

由于浏览器功能复杂、迭代迅速，很容易出现内存安全相关的漏洞，因此沙箱（sandbox）成为了现代浏览器的标准配置。简单来说就是把渲染引擎等逻辑装进一个被“笼子”关起来的进程，即使攻击者利用漏洞获得了任意代码执行，接下来仍然要做额外的工作从沙箱里逃逸出来，才能真正访问到有价值的信息。常规的沙箱逃逸多是利用进程间通信机制，或可访问到的内核、驱动等组件，在权限更高的进程或者直接内核当中触发其他内存安全问题，从而关闭沙箱或者启动一个不受限制的进程，形成完整的攻击链条（fullchain
exploit）。

而我们的议题富有创意地在 XSS
的老树上开出了新花，嫁接到沙箱逃逸的场景中实现了稳定的利用，而且完全避开当下系统针对内存安全漏洞所引入的各种缓解措施（mitigation）。因为这些缓解措施并不是针对此类问题而设计的，两者不在同一个战场上。

## 2.跨进程 XSS？

通常 XSS 指的是通过 HTTP 协议等输入向量，将恶意代码（如 Javascript 或者 HTML
片段）注入到本不应该受攻击者控制的站点内容当中，从而绕过同源策略（Same-Origin
Policy）窃取用户凭据的攻击手法。这种攻击可以追溯到二十世纪九十年代，常年雄踞 OWASP 的十大 Web 安全威胁榜单。

结合浏览器漏洞的场景，又有 UXSS（Universal XSS）的攻击方式。XSS 通常出现在服务器后端或者网页前端脚本，而 UXSS
主要基于客户端浏览器（或扩展）的漏洞，从而篡改浏览器预定的行为和绕过安全限制。通常在没有启用站点隔离（Site-Isolation，Chrome
的安全特性）的浏览器中，同一个渲染器进程可以同时处理多个域名，因此同源策略是在进程内通过特定的访问控制策略保证的。

有时浏览器在处理特定的 DOM
或者网络接口存在逻辑缺陷，可能导致不同站点的数据可以相互访问，或注入脚本到不同的域名上下文中；有时特定的浏览器上下文配置会默认允许关闭同源策略检测，例如
Android系统WebView可以使用 setAllowUniversalAccessFromFileURLs 等配置对 file
域开启同源策略例外，对应的 iOS 下 UIWebView 则直接默认启用了类似的策略，只要是 file://
域下的页面，一律不限制同源策略；而在出现了内存破坏漏洞，导致恶意网页具有内存读写权限的前提下，攻击者的脚本可以修改进程内的特定标志位实现 UXSS。

在这篇议题当中借鉴了 XSS 注入 javascript 的思路，但输入向量不是 Web 协议，而是本地进程之间的跨进程通信（IPC）。例如反射型 XSS
通常会将恶意的脚本或者 HTML 直接附在 GET 请求的 query string 当中，让脚本在目标站点域执行；而类似的，本文的一些案例通过
XPC（macOS 和 iOS 下的进程通信）接口，从浏览器的沙箱进程内发起调用，诱导其他高权限系统服务渲染攻击 HTML，从而在没有沙箱限制的
WebView 里运行恶意脚本，最终获得完整权限的本地代码执行（即沙箱逃逸）。和 UXSS 相比，虽然都是本地的攻击，但 UXSS
仍然在进程内，而本文的思路则实现了跨进程、跨安全边界的代码注入。

以下表格简单比较了这种攻击的特点：

| XSS | 跨进程 js 注入  
---|---|---  
输入向量 | HTTP 协议 | 跨进程通信  
对象 | 其他域名 | 高权限本地进程  
载荷 | 提取登录凭据或直接发起请求伪造 | 在高权限 WebView 执行本地代码  
最终目的 | 绕过同源策略 | 浏览器渲染器沙箱逃逸  
  
**因此这种攻击的思路大体如下：**

1.拥有一个完整的 WebKit 远程代码执行漏洞，用以触发后续逃逸操作。

2.找到浏览器沙箱可以交互的系统服务，使用系统服务当中的逻辑缺陷向其他本地进程注入 js 代码。

3.被注入 js 的进程和存在逻辑缺陷的系统服务不一定是同一个。

4.在高权限进程当中通过再次利用 WebKit 漏洞，甚至进程自身的特殊功能，获得无沙箱限制的命令执行。

## 3.WebView

既然要在不同上下文当中运行 js 脚本，就得在高权限进程当中找到可以渲染 HTML 和执行 js 的地方。

macOS 上支持 HTML 渲染的组件非常多。像 Finder、Spotlight、Dictionary、HelpViewer、iBooks 甚至
iMessage 当中都用到了 WebView 组件。WebView 分为两种，历史遗留（legacy）的 WebView 和 macOS 10.10
后引入的 WKWebView。前者不支持进程隔离（没有 sandbox），不支持 JIT（即时编译），在 SDK 中标记为已废弃。而 WKWebView
是目前推荐的嵌入 Web 内容的方式。因为使用了多进程，从攻击角度来说和 Safari 完全一致。

两种 WebView 都提供了一些机制来实现 Objective-C 和 javascript 互相调用，但实现上不同。WKWebView 因为用了
IPC，就只支持异步的 messageHandler 委托；历史遗留的 WebView 则提供更强大的接口，可以直接把 Objective-C
的对象、方法暴露给 js，也支持同步调用。其实 WKWebView 提供了一种叫做 InjectedBundle
的机制，可以在渲染器进程里直接加载二进制插件，从而暴露更多的 JSContext 功能。但由于系统签名机制，沙箱进程 WebContent
不允许载入第三方签名的模块，因此只有 Apple 自己用到了这项功能，也没有在开发者文档中提到。

这些不是 Safari，本身又用到了 HTML 渲染的进程，便是本议题的攻击目标。一些 WebView 使用的老式的接口，没有进程隔离。假设我们有一个非
JIT 的浏览器漏洞，直接通过客户端 xss 在这些 WebView 里运行利用，即可获得没有限制的任意代码执行；更有甚者，一些 WebView 本身向
js 暴露了接口，使得我们不需要重复使用 WebKit 的漏洞，而是简单调用便可以执行任意本地代码。

**如果上面的描述让人昏昏欲睡，话不多说，我们直接来看漏洞案例。**

**cfprefsd TOCTOU 沙箱逃逸**

这个问题没有分配 CVE。笔者在 10.13 上发现，但在当时的 10.14 开发者测试版上已经被修复了。复现很简单：

  1. 在 macOS <= 10.13.6 系统上。

  2. 关闭 SIP，以便可以调试系统自带应用。

  3. 附加到任意一个 WebContent 进程，输入 po (id)CFPreferencesCopyAppValue(@"CFBundleGetInfoString", @"/Applications/Calculator.app/Contents/Info")。

  4. 灵异事件发生了。按照沙箱规则，这个路径本该无法读取，却成功地返回了内容。不仅可以读，换成写操作也没有问题。

漏洞成因在于 CoreFoundation 当中的一段逻辑问题。Preferences 系列 API 用来持久化程序偏好信息，通过 plist 格式将
Objective C 当中的数据类型和键值对等信息保存到路径。但实际上对路径的读写操作不是在进程内完成的，而是通过一个 cfprefsd
进程作为代理，将读写操作使用 XPC 传递。cfprefsd 服务本身对读写操作有权限检查，但问题出在沙箱的状态的判定上。一个进程在访问过
Preferences 之后，如果进程没有 sandbox，那么 cfprefsd 会对其做一个标记。在此之后，所有的权限检查都会优先判断这个标记。

    
    
    void __cdecl ___CFPrefsMessageSenderIsSandboxed_block_invoke(Block_layout_1D3750 *block, _CFPrefsClientContext *ctx)
    
    {
    
      if ( ctx->_sandboxed != NULL ) {
    
        *(*(block->lvar1 + 8) + 24) = ctx->_sandboxed == kCFBooleanTrue;
    
      } else {
    
        *(*(block->lvar1 + 8) + 24) = sandbox_check(block->pid, 0, SANDBOX_CHECK_NO_REPORT) != 0;
    
        ctx->_sandboxed = *(*(block->lvar1 + 8) + 24LL) ? &kCFBooleanTrue : &kCFBooleanFalse;
    
      }
    
    }

这就造成了一个 Time-of-check-time-of-use（TOCTOU）的问题。

在 mac 系统下，一个进程可以动态地给自身加上沙箱锁定状态。这个 API
是单向的，即进入沙箱之后就无法解除这个状态（除非有内核漏洞）。假设一个进程先访问了 Preferences，然后进入沙箱，此时在 cfprefsd
服务的眼里，进程仍然是之前缓存的那个“没有沙箱”的状态，从而畅通无阻。

而 WebKit 的渲染器进程不巧在默认情况下就满足这个条件。

在初始化阶段，WebKit 不会加载任何第三方的内容，因此这时候不需要沙箱也是合理的。WebKit 当中引用到了一个 AppKit
的库，这个库在进程初始化的时候会读取一些 Preferences 信息，也就在 cfprefsd 留下了访问记录。接着 WebKit 调用
sandbox_init_with_paramaters 进入锁定状态并加载网页。这时候攻击者通过渲染引擎漏洞获得了在 sandbox
内执行任意代码的能力，访问 Preferences API。cfprefsd 仍然认为渲染器是一个正常进程，允许读写任意路径的 plist
文件，除非对应路径需要 root 权限。

![](https://images.seebug.org/content/images/2021/01/cbc12c0b-0d37-4d43-9aff-36052c2012e5.png-w331s)

到这一步其实已经可以通过修改 plist 在 sandbox 外触发代码执行了。macOS 在开机时会加载 ~/Library/LaunchAgents
当中的启动项，使用这个漏洞添加启动项便可同时实现逃逸沙箱和持久化。但是缺点显而易见，就是需要一次注销或者重启。

借助跨进程 XSS，我们找到了一种立即执行任意命令的方法。

![](https://images.seebug.org/content/images/2021/01/4fee335e-855a-45d2-bc4b-0d2ecb7a3cef.png-w331s)

macOS 曾经有一个叫 Dashboard 的功能，在一个独立的桌面上运行一些 HTML 编写的小组件（widget）。这个功能在 10.15
当中被删除，由桌面右侧的“今天”视图（Today Widgets）替代。

回到当时的系统中。

Dashboard Widgets 保存在如下路径：

· /Library/Widgets 系统预装

· ~/Library/Widgets 用户下载安装

一个 widget 是一个包（bundle），也就是带有特定结构的目录，目录的扩展名为 .wdgt。它由元数据 Info.plist、图标和至少一个
HTML 文件作为主体。WebContent 进程沙箱提供了一个可以写入文件的临时目录，可以释放一个完整的 wdgt 包。再通过前面提到的cfprefsd
漏洞篡改 com.apple.dashboard 域下的设置，从而让 Dashboard 加载来自临时路径的恶意 widget，实现从 WebKit 沙箱到
Dashboard 的跨进程 xss。

Dashboard 的 WebView 是一个典型的遗留组件，没有沙箱隔离，因此任何一个非 JIT 的漏洞都可以直接利用后拿到
shell。但当我们可以注入任意小插件的时候，事情变得更简单了。在 .wdgt 的 Info.plist 当中有一个 AllowSystem
属性，一旦设置为 true，js 的上下文中便会提供一个 window.widget.system 的函数。顾名思义，就是执行任意系统命令：

    
    
    window.onload = function () {
    
      widget.onshow = function () {
    
        widget.system('/usr/bin/open -a Calculator');
    
      }
    
    }

接下来还有一些问题亟待解决。假如系统把 Dashboard 关闭了怎么办？还有在通过漏洞安装了任意 widget 之后，如何才能激活代码执行的事件？

通过分析 WebContent 沙箱，我们发现这样一个系统服务允许访问：

    
    
    (global-name "com.apple.dock.server")

这个 Dock 服务正好通过 MIG 提供了启用 Dashboard 和切换桌面的功能。更方便的是，在 HIServices.framework
当中提供了一些私有函数，可以帮助构造并发送具体的 Mach Message。

使用如下两行代码便可以强制开启 Dashboard（即使之前被系统设置禁用），然后模拟用户手势滑动到 Dashboard 的桌面：

    
    
    CoreDockSetPreferences((__bridge CFDictionaryRef) @{@"enabledState" : @2});
    
    CoreDockSendNotification(CFSTR("com.apple.dashboard.awake"));

## 4.HelpViewer 的又一次陷落

这个案例的发现颇有一些喜剧色彩。

在距离 2019 年的天府杯还有一个多月，笔者突然发现 mac 10.15
开发者测试版中将准备好的沙箱逃逸漏洞的其中一环修补掉了（这个利用链条将在稍后分析），只能在极短时间内再争取一个新的方案。

这时笔者盯上了 Project Zero 之前的一个经典案例 CVE-2017-2361。在 issue 1040 中，lokihardt 通过特殊的
URL scheme 打开本地预装应用 HelpViewer，触发一个反射型 xss，从而得到特权上下文中执行 Apple Script 的能力，只用一个
xss 实现了完整的远程代码执行。这个漏洞当时也由 redrain 独立发现，被撞掉了。

![](https://images.seebug.org/content/images/2021/01/5a0e8402-b934-4122-bbab-503bd7331b32.png-w331s)

既然时间所剩无几，不如看看有没有找到变种的机会。

Safari 在跳转本地应用的时候需要弹窗确认。但通过逆向发现，浏览器内部维护了一个信任名单列表：

    
    
    @"itms-books",@"itms-bookss", @"ibooks", @"macappstore", @"macappstores",
    
      @"radr", @"radar", @"udoc", @"ts", @"st", @"x-radar", @"icloud-sharing",
    
      @"help", @"x-apple-helpbasic" count:19];

只要目标 URL 的 scheme 在其中，而且数字签名来自 Apple，就不会询问用户而直接跳转过去。其中的 x-apple-helpbasic
引起了笔者的注意。这个 URL 仍然链接到 HelpViewer，由函数 -[HVBasicURLHandler process:] 处理。

    
    
    if ([url.scheme isEqualToString:@"x-apple-helpbasic"] &&
    
      [url.host hasSuffix:@".apple.com"] &&
    
      [HelpApplication
    sharedApplication].isOnline)

只要 URL 的域名满足 *.apple.com，就会打开对应的 https 页面。例如x-apple-helpbasic://www.apple.com/aaa，将访问 <https://www.apple.com/aaa>

![](https://images.seebug.org/content/images/2021/01/37544b83-aa1b-48ac-bda6-ed5ebd4adc0c.png-w331s)

由于用到了加密，我们无法通过 Wi-Fi 劫持的方式篡改返回的内容，从而寄希望于真正意义上的 xss 或者 open redirection
问题。在找到这段代码的时候距离比赛仅有不到一星期，凭着碰运气的心态开始手工挖掘 Web 漏洞。

苹果官网有一个叫 Apple web server notifications
的页面，罗列了服务端相关的修复公告和致谢，包括具体的域名。这其实给前期的信息收集带来了很大方便。运气爆棚的是，笔者仅靠 Google Dork 和 F12
的原始办法，不到一天时间便找到了一个符合要求的 DOM xss。

通过这个客户端和服务端结合的问题，我们从浏览器直接跳转到了 HelpViewer 应用当中。很可惜，正如这个 URL
名字所暗示的那样，这是一个仅具备基本功能的界面，此前的 Apple Script 功能并不能使用。其实到这一步已经结束了，沙箱确实没了。只要再来一个 DOM
浏览器漏洞，即可实现 fullchain exploit。

那么逻辑的方式还有没有做其他事的可能？

在 -[HVBasicWindowController
webView:decidePolicyForNewWindowAction:request:newFrameName:decisionListener:]
里，遇到无法处理的 URL，就会调用 -[NSWorkspace openURL:] 打开文件，也就相当于运行本地程序。很可惜一开始注入 xss 的页面是
https:// 协议，按照 WebKit 的同源策略限制，是不允许直接跳转到 file:/// 域下的，否则我们就可以直接将 location 指向
Calculator.app 直接运行计算器了。不过弹其他的 URL 没有限制，例如 ssh:/// 可以打开一个终端应用尝试连接远程服务器。

**另外在 HelpViewer 当中实现了数个 NSURLProtocol 的子类：**

· HVHelpTopicsURLProtocol (x-help-topics:)

· HVHelpContentURLProtocol (apple-help-content:)

· HVHelpURLProtocol (help:)

请不要和之前提到的应用跳转 URL 混淆。虽然都是 help: 开头，但这里的 URL 是用来处理资源加载，调用对应的 URLProtocol
类当中的方法，将 HTTP 响应内容替换成自定义的返回值。在方法 -[HVHelpURLProtocol startLoading] 当中，会将 URL 的
pathname 转换成本地的路径，直接读取文件进行返回。例如 help://anything/etc/passwd 会替换成对 /etc/passwd
的访问。

之前提到我们不能跳转到 file:/// 域下，而 help:// 就没有这个限制。可以结合其他条件，让 macOS
将远程文件挂在到一个本地可预测的路径，通过访问这个 help://anything/some/path.html，即可获得全盘文件读取的能力。在 macOS
<= 10.14 的系统上可以用 /net/hostname/pathname 这样的路径自动挂载远程服务器上的
NFS，完成利用。正是因为这个特性的安全风险，mac 在 10.15 之后默认注释掉了 /etc/auto_master 当中挂载 NFS 的能力。

笔者做了另一种尝试。之前提到这个 WebView 可以不受限制地打开除 file:/// 之外的本地 URL scheme，可以使用
smb://user:passwd@host/path 让 Finder 加载一个远程 samba 资源。假设成功后，会使用 /Volumes/path
作为挂载点，也就完成了从 https:// 到 help:// 域的转换，从而读取全盘本地文件。不过实际操作过程中 Finder
会弹出一个确认框询问是否打开 samba 路径，需要一次额外的用户确认。

还是直接 DOM RCE 好使……

## 5.Dictionary XSS 到命令执行

mac 系统有一个自带的词典应用，词条的界面实际上是基于 WebView 渲染的 HTML。通常情况下 Dictionary
不会随意加载第三方网页，除了这一次。这一串漏洞利用便是前文提到的，在天府杯前两个月被修补掉的问题。

在 Safari 的沙箱配置文件中有这样一个服务：

    
    
    (global-name "com.apple.mobileassetd")

服务访问的对象是 mobileassetd 进程。其实除了系统软件版本更新之外，一些资源文件（assets）会定期从 apple 官方网站通过 OTA
的方式更新。这些文件存在 /System/Library/Assets(V2?) 目录下，通常受到 SIP 保护，即使有 root 权限也无法修改，只有
mobileassetd 等特殊权限的进程才可以更新。这类资源包括词典、字体等不可执行的文件，访问它们要用到私有 API 框架 MobileAsset
当中的 ASAssetQuery 和 ASAsset 类。

首先我们创造一个查询实例，获得其 results 数组，当中便是所有的 ASAsset 对象：

    
    
    const static NSString *kVictim = @"com.apple.dictionary.AppleDictionary";
    
    [[ASAssetQuery alloc] initWithAssetType:kType];
    
    [query runQueryAndReturnError:&err];
    
    NSArray *results = [query results];

通过修改 ASAsset 对象的如下属性，并执行其 beginDownloadWithOptions: 方法，可以诱导 mobileassetd
从任意网址下载资源并替换本地的文件：

· __BaseURL

· __RelativePath

· __RemoteURL

· _DownloadSize（压缩包的大小）

· _UnarchivedSize（解压后的大小）

· _Measurement（校验值）

到这一步我们正好可以在 Safari 的沙箱内通过强制 OTA 的方式，让系统下载任意的词典资源，我们便有机会向 Dictionary.app 当中注入任意
js 代码了。

来看看 Dictionary 里可以干什么。

    
    
    a = document.createElement('a');
    
    a.href = 'file:///Applications/Calculator.app';
    
    a.click()

![](https://images.seebug.org/content/images/2021/01/e2252d1b-1824-4e23-bf06-84626d88c355.png-w331s)

这一段代码匪夷所思地可以从 Dictionary 的 WebView 里直接运行计算器。而 location 赋值跳转的方式并不起作用，为什么？

让我们来到这个函数 -[DictionaryController
webView:decidePolicyForNavigationAction:request:frame:decisionListener:]:

    
    
    element = action[WebActionElementKey];
    
    url = element[WebElementLinkURLKey];
    
    if (!url)
    
      url = action[WebActionOriginalURLKey];
    
    ...
    
    [[NSWorkspace sharedWorkspace] openURL:url];

这个方法处理 WebView 的跳转事件，真对 WebActionElementKey 的情况来取出 URL，最后用 -[NSWorkspace
openURL:] 方法执行本地应用，也就是只处理了表单提交、链接点击等事件，而不管 location 的跳转。如果只熟悉
XSS，而不对程序进行逆向，就可能错过这个点。

再看前面 mobileassetd 的漏洞可以在后台下载解压任意文件。一个很有利的点在于，通过 OTA 方式下载的文件和浏览器下载不同，不会给文件打上“来自
Internet”的标记。假如里面包含可执行的应用，运行的时候不会触发 GateKeeper 检查，直接运行。因此直接编译一个可执行的 .app
文件包含在词典的包当中，再通过这个跳转漏洞直接打开即可绕过沙箱执行任意命令。

在 macOS 10.15 开发者测试版上，这个打开 URL 的操作被修复过了，只有 http 和 https URL
才会允许打开，也导致了我们之前的利用代码栽在了最后一步命令执行上。假设仍然在 10.14
存在问题的版本，这中间显然还有一段缺口没解决。我们可以在沙箱里任意下载替换词典，那么怎么样才可以从浏览器沙箱里直接打开词典？

虽然 dict:///apple 的 URL scheme 可以直接跳转到某个词条，但 dict:
不在我们前文提到的信任名单中，浏览器会询问用户。这时候就要请出一个小功能的帮忙了。

![](https://images.seebug.org/content/images/2021/01/ea3adee8-c775-431b-b824-78c835dcc3c1.png-w331s)

如图所示，mac 下的浏览器可以直接通过 ForceTouch 的方式打开一个浮动窗口，就是一个精简版的 Dictionary 界面。这个界面来自
LookupViewService 进程，也是一个 WebView。

通过阅读 WebView 的源代码，笔者找到一个叫做
WebKit::WebPage::performDictionaryLookupOfCurrentSelection() 的方法。这个方法可以在
WebProcess（沙箱中）通过 WebKit 内置的进程间通信发送给主进程，接着主进程就会打开 LookupViewService
界面载入指定单词的解释。这个过程不需要用户确认，因此我们获得了第一个跨进程 XSS。

在 LookupViewService 中注入任意 js 代码之后，通过一行简单的 location 跳转即可打开 Dictionary，触发第二次跨进程
XSS：

    
    
    location = "dict://ExploitStage2"

这时用前文提到的漏洞执行词典当中包含的恶意 app 即可。

有趣的是，在这个漏洞链条当中用到的三个中间进程——mobileassetd、LookupViewService 和 Dictionary.app
全都是有各自的沙箱的。这又得说到 NSWorkspace 启动进程的特点上。通过 openURL 这种方式运行的 app，最后会调用
LaunchService，启动出来的应用和调用者并不存在父进程子进程的关系，也不会继承前者的 sandbox profile，只要求调用者有 lsopen
权限。而 Dictionary.app 正好满足。

这个 MobileAsset 的漏洞还有一个神奇的副作用。在 mac 上这个 XSS 影响本地的词典应用，而在 iOS
上问题同样存在。在覆盖了本地词典之后，被攻击的 iPhone 在桌面上查询英文单词的定义时，会在 SpringBoard 进程里打开一个词典界面。

![](https://images.seebug.org/content/images/2021/01/b0ca3c54-2cda-468f-a0e1-0ef1095eca76.png-w331s)

![](https://images.seebug.org/content/images/2021/01/30eb30ce-cb8c-40a1-88a7-320eabfed0dc.png-w331s)

由于这个界面所在的进程 SpringBoard 没有沙箱，而且使用到了 UIWebView
进行网页渲染，可以导致恶意脚本可以无限制地使用绝对路径读取本地文件并上传，例如相册和所有的联系人、通话记录和短信。此外，只要有不涉及到 JIT 的
WebKit 浏览器引擎漏洞，攻击者便可以获得沙箱外完整的代码执行权限。这是一个潜在的持久化攻击向量。

我们把这个问题作为附加分析一同报告给了苹果，在 iOS 12 之后换成了更安全的 WKWebView。

## 6.总 结

本议题提出了一种特殊的思路来完成 Safari 浏览器沙箱逃逸，将大家熟悉不过的 XSS 从 Web
领域迁移到跨进程通信的场景上，得到了“老树开新花”的效果。结合其他浏览器渲染引擎漏洞，可实现全链路的利用。

相比流行的思路，纯逻辑漏洞可以获得百发百中的稳定性，以及完全无视针对内存安全问题设计的各种缓解措施。不过，这些漏洞虽然都可以完美利用，但由于涉及跨 App
的跳转等操作，会出现肉眼可感知的现象，对攻击者而言不是最理想的方案。

本文也带来了一些启示。对于开发维护者，历史遗留组件可能拖累整个系统的安全性。如何在保证系统可用性的同时，尽可能地抛弃历史包袱，是一个需要考虑的问题。而对于攻击者来说，跨组件之间小问题的有机结合常常会带来让人意想不到的效果。

## 关于作者

**蚂蚁安全光年实验室** 隶属于蚂蚁安全九大实验室之一，通过对基础软件及设备的安全研究，达到全球顶尖破解能力，致力于保障蚂蚁集团及行业金融级基础设施安全。
因发现并报告行业系统漏洞，蚂蚁安全光年实验室上百次获得Google、Apple等国际厂商致谢。

![](https://images.seebug.org/content/images/2021/01/1310595e-3c6e-4440-9f9f-83f73ee0f5bb.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1453/>

