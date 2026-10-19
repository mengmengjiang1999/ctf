# 在OSX上编译非osx ida pro插件

阅读量 **110509**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-26 16:19:52

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://www.surrendercontrol.com/2016/01/compiling-non-osx-ida-pro-plugins-on-os.html>

译文仅供参考，具体内容表达以及含义原文为准。

爱因斯坦曾经说过:一遍又一遍地做同一件事情,以期待得到不同的结果。

最近,我发现越来越多的人喜欢在OS X平台上使用IDA
Pro(交互式反汇编器专业版,是一个世界顶级的交互式反汇编工具)了,所以我决定对这款编译软件的主题文件进行研究和测试。在研究过程中,我发现了一款名为[IDASkins](https://github.com/zyantific/IDASkins)的主题,大家可以看到,github代码库中已经有大量预编译完成的Windows版IDA主题,但是却没有能够适用于OS
X平台的。

在OS
X平台上,IDASkins中的cmake文件标明的是“未测试”,实际上,这些编译文件是存在一些问题的。在此,认为还需要给大家介绍一下有关cmake的内容。CMake是一个跨平台的安装(编译)工具,可以用简单的语句来描述所有平台的安装(编译过程)。他能够输出各种各样的makefile或者project文件,能测试编译器所支持的C++特性,类似UNIX下的automake。Cmake
并不会直接建构出最终的软件,而是产生标准的建构档(如 Unix 的 Makefile 或 Windows Visual C++ 的
projects/workspaces),然后再依一般的建构方式使用。这使得熟悉某个集成开发环境(IDE)的开发者可以用标准的方式建构他的软件,这种可以使用各平台的原生建构系统的能力是
CMake 和 SCons 等其他类似系统的区别之处。

在我对文件进行了一些修改之后,编译文件就能够正常工作了。但是其中还有一个插件(适用于IDA
64位)在运行过程中却一直会崩溃,我也不知道为什么:)。我甚至对32位的ARM处理器进行了分析, 却仍然没有办法找到原因,但一个插件也已经足够我使用了。

在整个编译过程中,我们需要的信息可以在github中的这个库([gist](https://gist.github.com/agelastic/bfb3d8c3d00f7a93ea99))中获取到。它可以对IDA的操作界面进行修改,如果苹果公司能够对cmake编译文件提供更好的支持,那么这些插件肯定能够运行得更好!

适用于32位OS X IDA Pro 6.8的插件链接地址如下:

[https://drive.google.com/file/d/0BwfeEfhaN–RMTRBdzRnTldsTk0/view?usp=sharing](https://drive.google.com/file/d/0BwfeEfhaN
--RMTRBdzRnTldsTk0/view?usp=sharing)

除此之外,当我在编译插件时,我还发现了两个适用于6.8版本IDA
Pro的WWDC插件(预编译完成)。在对插件源代码进行编译的过程中,我们并没有多少便捷的方法,我们只能将其放入IDA
SDK的“插件”目录下,然后对其进行编译。

本文翻译自360安全播报 [原文链接](http://www.surrendercontrol.com/2016/01/compiling-non-osx-ida-pro-plugins-on-os.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **lazy--nms** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83385](/post/id/83385)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://www.surrendercontrol.com/2016/01/compiling-non-osx-ida-pro-plugins-on-os.html)

如若转载,请注明出处： <http://www.surrendercontrol.com/2016/01/compiling-non-osx-ida-pro-plugins-on-os.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) lazy--nms

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

