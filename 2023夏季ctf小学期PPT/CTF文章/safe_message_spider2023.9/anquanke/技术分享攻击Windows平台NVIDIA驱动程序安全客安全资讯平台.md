# 【技术分享】攻击Windows平台NVIDIA驱动程序

阅读量 **128296**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-02-20 09:57:12

 **x**

##### 译文声明

本文是翻译文章，文章来源：googleprojectzero.blogspot.tw

原文地址：<http://googleprojectzero.blogspot.tw/2017/02/attacking-widows-nvidia-driver.html>

译文仅供参考，具体内容表达以及含义原文为准。

****

翻译：[overXsky](http://bobao.360.cn/member/contribute?uid=858486419)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**前言**

现代图形驱动程序是十分复杂的，它提供了大量有希望被利用的攻击面，可以使用具有访问GPU权限的进程（比如Chrome的GPU进程）进行提权和沙箱逃逸。在这篇文章中，你们将看到如何攻击NVIDIA内核模式的Windows驱动程序，以及在此期间我发现的一些bug。我的这项研究是Project
Zero的一个20％项目的一部分，在此期间我总共发现了[16个漏洞](https://bugs.chromium.org/p/project-zero/issues/list?can=1&q=vendor%3ANVIDIA+finder%3Aochang&colspec=ID+Type+Status+Priority+Milestone+Owner+Summary&cells=ids)。

  

**内核WDDM接口**

图形驱动程序的内核模式组件被称为显示微端口驱动程序。微软的[官方文档](https://msdn.microsoft.com/en-us/library/windows/hardware/ff570589\(v=vs.85\).aspx)为我们提供了一个很好的结构图，总结了各个组件之间的关系：

在显示微端口驱动程序
的DriverEntry()函数中，[DRIVER_INITIALIZATION_DATA](https://msdn.microsoft.com/en-us/library/windows/hardware/ff556169\(v=vs.85\).aspx)结构被由厂商实现的函数（实际上与硬件进行交互）的回调进行填充，该函数通过DxgkInitialize()传递给dxgkrnl.sys（DirectX的子系统）。这些回调要么由DirectX内核子系统调用，要么在某些情况下直接从用户模式代码调用。

  

**DxgkDdiEscape**

一个众所周知的潜在漏洞的入口点是 DxgkDdiEscape
接口。它可以直接在用户模式下被调用，并且可以接受任意数据，该数据以厂商指定的方式（本质上是IOCTL）解析和处理。在后文中，我们将使用术语“逃逸”来表示由DxgkDdiEscape
函数支持的特定命令。

截止写作时，NVIDIA有着数量惊人的400多个逃逸，所以这里也是我花费了绝大部分时间的地方（这些逃逸中的绝大多数是否有必要处在内核空间中是一个问题）：

    
    
    // (这些结构体的名称是我命名的)
    // 表示一组逃逸代码
    struct NvEscapeRecord {
      DWORD action_num;
      DWORD expected_magic;
      void *handler_func;
      NvEscapeRecordInfo *info;
      _QWORD num_codes;
    };
     
    // 有关特定逃逸代码的信息
    struct NvEscapeCodeInfo {
      DWORD code;
      DWORD unknown;
      _QWORD expected_size;
      WORD unknown_1;
    };

NVIDIA为每一个逃逸都单独实现了其私有数据（DXGKARG_ESCAPE
结构体中的pPrivateDriverData），格式为“头部+数据”。头部格式如下：

    
    
    struct NvEscapeHeader {
      DWORD magic;
      WORD unknown_4;
      WORD unknown_6;
      DWORD size;
      DWORD magic2;
      DWORD code;
      DWORD unknown[7];
    };

这些逃逸由32位代码（上面NvEscapeCodeInfo结构体的第一个成员）标识，并根据它们的最高有效字节进行分组（从1到9）。

在处理每个逃逸代码之前都会做一些验证。具体来说，每个 NvEscapeCodeInfo
应当包含头部后面的逃逸数据的预期大小。这将根据NvEscapeHeader中的大小来验证，NvEscapeHeader自身又通过传递给
DxgkDdiEscape的PrivateDriverDataSize字段进行验证。但是，预期大小有时可能为0（通常当逃逸数据为可变大小时），这意味着逃逸处理程序负责进行自身的验证。这将导致一些bug（[1](https://bugs.chromium.org/p/project-zero/issues/detail?id=936)，[2](https://bugs.chromium.org/p/project-zero/issues/detail?id=940)）。

在逃逸处理程序中发现的大多数漏洞（总共[13](https://bugs.chromium.org/p/project-zero/issues/list?can=1&q=reporter%3Aochang+escape&colspec=ID+Type+Status+Priority+Milestone+Owner+Summary&cells=ids)个）都是些非常基本的bug，例如盲目地向用户提供的指针进行写入操作，向用户模式公开未初始化的内核内存以及不正确的边界检查。还有许多我发现的问题（例如OOB读取）没有报告出去，因为它们似乎没有可以利用的地方。

  

**DxgkDdiSubmitBufferVirtual**

另一个有趣的入口点是DxgkDdiSubmitBufferVirtual函数，它首次在Windows 10和WDDM
2.0中被引入，主要用来支持GPU虚拟内存（而旧的 DxgkDdiSubmitBuffer / DxgkDdiRender
函数已被弃用）。这个函数相当复杂，并且还接受来自用户模式驱动程序提交的每一个由厂商特定的数据。我在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=1012)找到了一个bug。

  

**其他**

还有[一些其他](https://msdn.microsoft.com/en-us/library/windows/hardware/ff570147\(v=vs.85\).aspx)WDDM函数接受厂商特定的数据，但快速浏览后没有发现任何有趣的东西。

  

**暴露的设备**

NVIDIA暴露了可由任何用户打开的一些其他设备：

    
    
    \. NvAdminDevice

似乎用于
[NVAPI](https://developer.nvidia.com/nvapi)。很多ioctl处理程序似乎都会调用DxgkDdiEscape。

    
    
    \. UVMLite {Controller，Process *}

可能与NVIDIA的“统一内存”相关。在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=880)找到1个bug。

    
    
    \. NvStreamKms

作为GeForce
Experience的一部分默认选择安装，但也可以在安装期间选择停用。不是很明白为什么这个驱动程序是必要的。在[这里](https://bugs.chromium.org/p/project-zero/issues/detail?id=918)也发现了1个bug。

  

**更多有趣的Bug**

我发现的大多数bug是通过手动逆向和分析得到的，并且使用了一些自定义的IDA脚本。我还写了一个模糊工具。最终结果成功得有点令人惊讶，这也说明了这些bug的简单性。

虽然大多数bug相当无聊（缺乏验证之类的简单案例），但也有一些比较有意思。

  

**NvStreamKms**

此驱动程序使用 PsSetCreateProcessNotifyRoutineEx
函数注册进程创建通知回调。该回调检查系统上创建的新进程是否和先前通过发送IOCTL设置的映像名称相匹配。

这个创建通知的例程包含一个bug：

（简化的反编译输出）

    
    
    wchar_t Dst[BUF_SIZE];
     
    ...
     
    if ( cur->image_names_count > 0 ) {
      // info_是传递给例程的PPS_CREATE_NOTIFY_INFO
      image_filename = info_->ImageFileName;
      buf = image_filename->Buffer;
      if ( buf ) {
        filename_length = 0i64;
        num_chars = image_filename->Length / 2;
        // 通过扫描反斜杠来查找文件名
        if ( num_chars ) {
          while ( buf[num_chars - filename_length - 1] != '\' ) {
            ++filename_length;
            if ( filename_length >= num_chars )
              goto DO_COPY;
          }
          buf += num_chars - filename_length;
        }
    DO_COPY:
        wcscpy_s(Dst, filename_length, buf);
        Dst[filename_length] = 0;
        wcslwr(Dst);

此例程通过向后搜索反斜杠（''）的方法从PS_CREATE_NOTIFY_INFO的ImageFileName 成员中提取映像名称，然后使用
wcscpy_s 将其复制到堆栈缓冲区（Dst），但传递的长度是计算出的名称长度，而不是目标缓冲区的长度。

即使 Dst
是大小固定的缓冲区，这也不能被视为一个直接溢出。因为它的大小大于255个wchar长度，并且对于大多数Windows文件系统路径组件来说其不能超过255个字符。而因为ImageFileName
是规范化的路径，所以扫描反斜杠在大多数情况下也是有效的。

然而，上述规则可以通过如下方式绕过：对于一个符合通用命名规约（UNC）的路径，其规范化后保持以正斜杠（'/'）作为路径分隔符（感谢James
Forshaw向我指出这一点）。这便意味着我们可以得到一个“aaa / bbb / ccc / …”形式的文件名从而引发溢出。

例如：

    
    
    CreateProcessW(L"\\?\UNC\127.0.0.1@8000\DavWWWRoot\aaaa/bbbb/cccc/blah.exe", …)

另一个有趣的关注点是，跟随受损副本的wcslwr实际上并不限制溢出的内容（唯一的要求是有效的UTF-16编码）。因为计算的filename_length不包含null终止符，所以wcscpy_s
会认为目的地太小，然后以在开始处写入null字节的方式来清除目的地字符串（发生在内容复制到 filename_length
字节之后，因此溢出仍然发生）。这意味着 wcslwr是无用的，因为对 wcscpy_s的调用和一部分的代码从来没有工作过。

利用这个漏洞就不那么复杂了，因为驱动程序没有使用堆栈cookie编译过。在[以前的漏洞](https://bugs.chromium.org/p/project-zero/issues/detail?id=918)中附加过一个本地特权提升漏洞利用程序，它配置了一个伪造的WebDAV服务器来利用漏洞（ROP，从主堆栈到用户缓冲区，再次ROP来分配
读写执行内存，用来存放shellcode并跳转进去）。

  

**UVMLiteController中错误的验证**

NVIDIA的驱动程序还在 \\. UVMLiteController路径中暴露了一个可以由任何用户打开的设备（包括从沙箱中的Chrome
GPU进程）。该设备的IOCTL处理程序直接将结果写入Irp->UserBuffer中，作为将要传递给 DeviceIoControl 的输出指针
（微软的[文档](https://msdn.microsoft.com/en-us/library/windows/hardware/ff550694\(v=vs.85\).aspx)中指出不要这样做）。IO控制代码指定使用METHOD_BUFFERED，这意味着在Windows内核检查地址提供的范围并将其传递给驱动器之前，用户具有写操作的权限。

然而，这些处理程序还缺少对输出缓冲区的边界检查，这意味着用户模式上下文可以通过任何任意地址传递值为0的长度（可以绕过ProbeForWrite的检查），
这样做的结果是创造出一个受限的Write-what-where情景（这里的“what“仅限于一些特定的值：包括32位0xffff，32位0x1f，32位0和8位0）。

在[原始问题](https://bugs.chromium.org/p/project-zero/issues/detail?id=880)中附加了简单的提权漏洞利用 。

  

**远程攻击途径？**

考虑到已发现的bug数量如此之众，我做了一个调查，是否可以在不必首先破坏沙盒进程的前提下，完全从远程环境中访问其中任意一个bug（例如通过浏览器中的WebGL或通过视频加速）。

幸运的是结果似乎并非如此。但这并不令人惊讶，因为这里的易受攻击的API是非常底层的，只有经过许多层才能访问得到（对于Chrome而言，需要经历libANGLE
-> Direct3D运行时和用户模式驱动程序 ->内核模式驱动程序），并且通常需要在用户模式驱动程序中构造有效的参数才能调用。

  

**NVIDIA的回应**

发现的bug的性质表明NVIDIA仍有很多工作要做。他们的驱动程序包含的很多可能不必出现在内核中的代码，而发现的大多数错误是非常基本的错误。事到如今，他们的驱动程序（NvStreamKms.sys）仍然缺乏非常基本的缓解措施（堆栈cookie）。

不过，他们的反应倒是快速且积极的。大多数bug在截止日期之前已经修复好了，并且他们自己内部也在做一些寻找bug的工作。他们还表示，他们一直在努力重构他们内核驱动程序的安全性，但还没有准备好分享任何具体的细节。

  

**时间线**

  

**补丁间隔**

NVIDIA的第一个补丁，其中包括我报告的6个bug的修复，但是没有在公告中详细说明（[发布说明](http://us.download.nvidia.com/Windows/372.90/372.90-win10-win8-win7-desktop-release-notes.pdf)称作“安全更新“）。他们原本计划在补丁发布后一个月再公布详细信息。我们注意到了这一点并告诉他们这样做并不恰当，因为黑客可以通过逆向补丁来找到之前的漏洞，而当大众意识到这些漏洞细节的时候已经晚了。

虽然前6个bug修复后在30多天内都没有发布修复的详细信息，但剩余的8个bug的修复补丁发布后5天内就发布了细节公告。看上去NVIDIA也一直在尝试减少这种差距，但是就最近的公告来看两者的发布仍有很大的不一致性。

  

**结论**

鉴于内核中的图形驱动程序所暴露出来的巨大攻击面，以及第三方厂商的低质量代码，它似乎是挖掘沙箱逃逸和特权提升漏洞的一个非常丰富的目标。GPU厂商应该尽快将其驱动代码从内核中转移出去，从而缩小攻击面使得这种情况得以限制。

本文翻译自googleprojectzero.blogspot.tw
[原文链接](http://googleprojectzero.blogspot.tw/2017/02/attacking-widows-nvidia-driver.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **overXsky** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/85515](/post/id/85515)

安全客 - 有思想的安全新媒体

本文转载自:
[googleprojectzero.blogspot.tw](http://googleprojectzero.blogspot.tw/2017/02/attacking-widows-nvidia-driver.html)

如若转载,请注明出处： <http://googleprojectzero.blogspot.tw/2017/02/attacking-widows-nvidia-driver.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t01484ec090964be218.jpg) overXsky

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

