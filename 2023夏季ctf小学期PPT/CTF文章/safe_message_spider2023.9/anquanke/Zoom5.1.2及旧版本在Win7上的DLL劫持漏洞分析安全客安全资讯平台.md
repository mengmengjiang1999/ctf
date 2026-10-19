# Zoom 5.1.2及旧版本在Win7上的DLL劫持漏洞分析

阅读量 **269860**

|评论 **2**

发布时间 : 2020-07-24 10:00:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01b573a03e82b0794d.png)

## 一、漏洞原因

Zoom 5.1.2及之前版本尝试加载了一个名为 shcore.dll的系统库文件来辅助设置显示 Dpi，但是这个库文件在 Win7 System32
下默认没有（在Win7旗舰版和专业版上进行了检索，确认在默认状态下没有此DLL），在 Win10 System32 下可以找到（经调研，发现此系统库确实自
Win8.1才开始引入），给 DLL 劫持提供了机会。

## 二、分析过程

### **2.1 分析方法**

Zoom 在国区已经暂停个人用户注册使用，启动软件后只能停留在 Zoom 的登录界面环节，故采用静态逆向分析程序文件的方式尝试挖掘程序的潜在漏洞。

公开资料显示 Zoom 自5.1.3版本起对曝光的问题进行了修复，这里采用对两个邻近版本的程序文件做差异比较的方法来推导存在问题的代码块。

### **2.2 分析对象**

  1. Zoom 5.1.2 (28642.0705)
  2. Zoom 5.1.3 (28656.0709)

### **2.3 分析工具**

  1. IDA 7.2
  2. bindiff 5
  3. ghidra 9.0.2
  4. duplicate cleaner pro 4

### **2.4 分析操作及结果**

**1、文件去重**

首先将两个版本的 Zoom 先后安装到系统中，并在User\XXX\AppData\Roaming\Zoom\ 路径下提取到各自展开的程序文件，再用
duplicate cleaner 基于文件 hash 将两个版本中内容完全相同的部分进行剔除。

**2、差异分析**

在IDA中启用 bindiff插件对两个版本中bin目录下的同名 .exe 和 .dll 文件逐个进行比对，发现存在函数代码变动的文件如下：

![](https://p4.ssl.qhimg.com/t012767cacd2047d98c.png)

通过 ghidra提供的逆向功能辅助查看DuiLib.dll下四个方法的代码，发现主要改动是将旧版中的
LoadLibraryW(L”Shcore.dll”) 接口调用改为LoadLibraryExW(L”Shcore.dll”,0x0,
0x800)，其余部分一致：

![](https://p5.ssl.qhimg.com/t010e59562b7ff1e022.png)

在IDA中对比分析 Zoom.exe 如下，可以看到 sub_4022EA函数的变化只是新增了一条 SetDllDirectoryW()
接口调用，其余功能代码保持一致：

![](https://p3.ssl.qhimg.com/t0160de76db6b764026.png)

在 IDA 中对比分析 DllSafeCheck.dll 如下，可以看到 sub_10002430函数的变化只是新增了一条
SetDllDirectoryW()接口调用，其余功能代码保持一致：

![](https://p3.ssl.qhimg.com/t019276dbfc09cf26da.png)

由上面两处细节调整可以推断出新版中主要是进一步明确了 DLL 的加载路径，但是受影响的 DLL 文件没有直接体现出来，不过在尝试在检索 DuiLib.dll
中所使用到的 Shcore.dll 库文件时发现了异常，这个 Shcore.dll 并未在 Zoom客户端中一起打包，说明应该是由系统提供的功能，在
Win10 中检索此文件得到结果如下：

![](https://p3.ssl.qhimg.com/t017e1db6a895beace2.png)

但尝试检索 Win7 旗舰版和专业版的 System32 目录时均未见到此文件（SysWow64下也没有）：

![](https://p3.ssl.qhimg.com/t01647482e97708901c.png)

（旗舰版检索结果）

![](https://p1.ssl.qhimg.com/t01526da8c47539ffff.png)

（专业版检索结果）

经调研得知，shcore.dll库文件在 Win 7系统中确实不存在，自Win 8.1 起成为系统库函数标配，并且在Zoom中确实对
GetDpiForMonitor 接口有调用，封装在自定义的 DuiLib.dll 库中：

https://stackoverflow.com/questions/37058349/shcore-dll-on-windows-7-does-it-exist

![](https://p5.ssl.qhimg.com/t01526c950970f0c890.png)

https://docs.microsoft.com/zh-cn/windows/win32/api/shellscalingapi/nf-shellscalingapi-getdpiformonitor?redirectedfrom=MSDN

![](https://p1.ssl.qhimg.com/t01b9b904b98f06a977.png)

## 三、小结

由于 Zoom 目前禁止国区个人用户登录使用，针对 Win 7 的 shcore.dll
劫持操作复现暂无法进行，但是根据静态逆向分析的结果与公开资料描述的问题来看，很大可能上是因为 Zoom
在代码中使用了win8.1及以后版本才有的系统库，导致在 Win7 系统上可以进行DLL劫持攻击，考虑到资料演示中针对的是视频功能，逆向分析中 Dpi
设置也与画面显示密切相关，基本上可以推断演示视频中的操作应该是在 Win7 系统上植入了攻击者自定义的 shcore.dll
库并重写了其中被调用的方法，然后在视频功能中进行点击触发。

参考链接：

https://www.bleepingcomputer.com/news/security/zoom-fixes-zero-day-rce-bug-affecting-windows-7-more-updates-soon/

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信代码卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/211615](/post/id/211615)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhimg.com/t015a32ce3696fa7636.png) 奇安信代码卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

