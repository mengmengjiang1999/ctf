![](https://image.3001.net/images/20201011/1602430667_5f8326cb2ca9b54c9e82d.png!small)

## 背景介绍

近期，我一直在研究macOS上的一些持久化技术，尤其是如何利用低等级用户权限来修改文件以影响用户交互。对于macOS终端用户来说，交互最频繁的当属Dock了。

在我的研究过程中，我发现了一个plist文件，它可以控制Apple D 对于macOS终端用户来说，交互最频繁的当属Dock了。
ock应用程序是否可见。在检查plist文件中的值时，我就想判断是否可以通过修改这些值来将合法程序替换成我们的恶意程序，并执行恶意代码。

最终，我开发出了一个包含[
_PersistentJXA项目_](https://github.com/D00MFist/PersistentJXA)的DockPersist.js脚本文件，并且能够将Dock中最常见的Safari和Chrome替换成我们的恶意程序，不过这种方法适用于其他任何应用程序。一旦用户点击了Safari或Chrome图标，我们的恶意软件就会运行，因为这里的Dock图标充当了实际应用程序的[
_快捷方式_](https://attack.mitre.org/techniques/T1547/009/)。

接下来，我们将在这篇文章中介绍这项技术的实现方式。

## 环境配置

这种持久化方法需要将恶意程序上传到目标设备中，不过我们有很多中方法绕过Gatekeeper保护机制，并实现恶意程序的上传：

  * 压缩应用程序Bundle，在Mythic代理中使用上传命令，然后解压至目标路径；
  * 压缩应用程序Bundle，使用curl命令在目标设备中拉取程序，然后解压至目标路径；
  * 压缩应用程序Bundle，进行base64编码，然后在目标设备中解码，并解压至目标路径；

在这里，首先使用Automator创建一个应用程序，这个应用程序会在后台打开Safari，然后运行我们的Apfell Payload：

![](https://image.3001.net/images/20201011/1602430682_5f8326da63cb536f99429.png!small)

为了不引起终端用户的察觉，我用Safari罗盘图标替换掉了Automator图标。当然了，我们也可以使用Xcode来生成更加复杂的应用程序。

![](https://image.3001.net/images/20201011/1602430689_5f8326e1cc6c82db926d8.png!small)

接下来，压缩应用程序Bundle并上传至目标系统，然后解压至/Users/Shared/路径下，此时我们就可以调用持久化方法了。

这里需要注意的是，考虑到plist文件的格式，这里要求伪造的应用程序命名为“Google
Chrome”或“Safari”，并且存储路径为/Users/Shared/，然后修改Safari64和Chrome64变量来指向该地址。

## 调用持久化方法

将脚本导入至Apfell代理中：

![](https://image.3001.net/images/20201011/1602430699_5f8326eb2ff13aa42ec30.png!small)

调用DockPersist函数，该函数可以接收三个参数：

  * 应用程序名称；
  * 应用程序Bundle ID；
  * 重载Dock选项；

Bundle ID存在于Info.plist文件中，可以使用下列命令直接获取：

    
    
    /usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' ~/FakeApp/Safari.app/Contents/Info.plist

![](https://image.3001.net/images/20201011/1602430711_5f8326f79bbb57a4727e8.png!small)

## 检测技术

Crescendo是一款在单主机中快速捕捉事件的优秀工具，Crescendo也是macOS上的一款实时事件查看器，它可以利用苹果的终端安全框架ESF来实现其功能。ESF能够监控系统事件，并识别潜在的恶意活动，它相当于Windows中的ETW。

在Crescendo的帮助下，我们可以轻松查看持久化执行所生成的文件和进程事件。

比如说，下列ESF事件将会被映射至Crescendo中：

    
    
    ES_EVENT_TYPE_AUTH_EXEC = process::exec
    
    ES_EVENT_TYPE_NOTIFY_EXIT = process::exit
    
    ES_EVENT_TYPE_NOTIFY_CREATE = file::create
    
    ES_EVENT_TYPE_NOTIFY_KEXTLOAD = process:kext::load
    
    ES_EVENT_TYPE_NOTIFY_MOUNT = file::mount
    
    ES_EVENT_TYPE_NOTIFY_UNLINK = file::unlink
    
    ES_EVENT_TYPE_NOTIFY_RENAME = file::rename
    
    ES_EVENT_TYPE_NOTIFY_UIPC_CONNECT = network::ipcconnect
    
    ES_EVENT_TYPE_NOTIFY_FORK = process::fork

ES_EVENT_TYPE_NOTIFY_EXEC可以捕捉这种持久化方法的各种事件，如果还需要覆盖其他事件，我强烈推荐使用Xorrior的[
_Appmon_](https://bitbucket.org/xorrior/appmon/src/master/)。

以下几个因素针对的是持久化方法的运行，因为实际的恶意应用程序组件将根据攻击者开发的内容而有所不同。

首先，plutil可以将Dock plist转换为XML，XML格式可以轻松修改：

![](https://image.3001.net/images/20201011/1602430731_5f83270b7e7123cff6c74.png!small)

除此之外，temp9876文件的创建也会被记录到日志中。

DockPersist.js会在/private/tmp/目录下创建一个随机名称的文件，该脚本将修改plist文件的XML版本，并将其存储至这个随机文件名中。在这里，temp0wsn4p包含了XML格式的恶意plist，所以我们可以使用正确的格式来修改代码格式版本，并在Dock中正确加载：

![](https://image.3001.net/images/20201011/1602430738_5f8327129a1128cfac6c6.png!small)

接下来，DockPersist.js会删除~/Library/Preferences/com.apple.dock.plist路径下的plist文件：

![](https://image.3001.net/images/20201011/1602430744_5f83271887f4f092137fa.png!small)

ESF会捕捉到我们存储新的恶意plist文件的行为：

    
    
    ~/Library/Preferences/com.apple.dock.plist

![](https://image.3001.net/images/20201011/1602430754_5f8327220185462d132fc.png!small)

最后，因为我们在函数调用中重载了Dock，因此killall命令将会被调用：

![](https://image.3001.net/images/20201011/1602430761_5f8327290cf87850ea0eb.png!small)

这些事件都可以作为构建检测机制的入口点，这里最重要的就是plutil和killall了。除此之外，还可以利用文件创建、删除和修改事件进行检测。

## 正常执行

我们已经知道了如何使用ESF来捕捉恶意行为了，那么我们如何让ESF来显示正常执行行为呢？

在正常操作中，cfprefsd会触发com.apple.dock.plist上的file::rename（文件重写）事件，当用户通过GUI手动修改Dock时同样会触发这些事件：

![](https://image.3001.net/images/20201011/1602430770_5f83273291ae8beb026a3.png!small)

## 防护绕过

攻击者可以在目标设备外执行plist修改操作，然后再上传到目标Dock
plist路径下，这样可以降低被检测到的风险。但是，这同样会触发file::rename事件，不过它不会使用到cfprefsd进程。

![](https://image.3001.net/images/20201011/1602430778_5f83273a56f1f481c3157.png!small)

## 可视化指标

我们的PoC应用程序执行之后，会在Dock中出现两个Safari图标：

![](https://image.3001.net/images/20201011/1602430786_5f83274214c836ae32141.png!small)

第一个Safari是恶意程序，它存在于plist文件中的persistent-apps字段，第二个就是真实的Safari了，它存在于plist文件中的recent-apps字段。

## 总结

在这篇文章中，我们介绍了一种在macOS上的持久化机制，它有点类似于在Windows中利用.LNK文件实现持久化的方法。更重要的是，我们希望通过这篇文章来帮助广大研究人员开发出相应的检测技术。

## 参考资料

  * [ _https://posts.specterops.io/detection-engineering-using-apples-endpoint-security-framework-affdbcb18b02_](https://posts.specterops.io/detection-engineering-using-apples-endpoint-security-framework-affdbcb18b02)
  * [ _https://medium.com/red-teaming-with-a-blue-team-mentaility/taking-the-macos-endpoint-security-framework-for-a-quick-spin-802a462dba06_](https://medium.com/red-teaming-with-a-blue-team-mentaility/taking-the-macos-endpoint-security-framework-for-a-quick-spin-802a462dba06)
  * [ _https://attack.mitre.org/techniques/T1547/009/_](https://attack.mitre.org/techniques/T1547/009/)
  * [ _https://developer.apple.com/documentation/endpointsecurity?language=objc_](https://developer.apple.com/documentation/endpointsecurity?language=objc)
  * [ _https://github.com/SuprHackerSteve/Crescendo_](https://github.com/SuprHackerSteve/Crescendo)
  * [ _https://bitbucket.org/xorrior/appmon/src/master/_](https://bitbucket.org/xorrior/appmon/src/master/)
  * [ _https://sqlitebrowser.org/_](https://sqlitebrowser.org/)
  * [ _https://eclecticlight.co/2017/07/06/sticky-preferences-why-trashing-or-editing-them-may-not-change-anything/_](https://eclecticlight.co/2017/07/06/sticky-preferences-why-trashing-or-editing-them-may-not-change-anything/)

