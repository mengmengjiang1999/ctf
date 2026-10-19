# Javascript Deobfuscator：JavaScript反混淆工具更新

阅读量 **269504**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-01-11 14:08:34

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://www.kahusecurity.com/2016/javascript-deobfuscator-updated-2/>

译文仅供参考，具体内容表达以及含义原文为准。

这个程序在最初编写的时候，我并没有想到这个程序的实用性是如此的高。所以我决定要为这个程序添加几个新的功能，使其变得更加强大和实用。而且对于那些使用[Revelo](http://www.kahusecurity.com/tools)工具的程序员来说，我的这款软件目前仍然无法对复杂的Javascript脚本进行处理。

为了给大家介绍我所添加的功能，我从[Dynammo的pastebin站点](http://pastebin.com/u/dynamoo)中选取了几个实例，并通过这些实例来给大家进行一一介绍。

**实例一（**[ **pastebin原地址**](http://pastebin.com/L4qeh1k2) **）**

在该程序的最新版本中，在点击了“Clues（线索）”按钮之后，程序将会把文本信息中的一些“线索”高亮显示，这些“线索”可以为你反混淆JavaScript脚本的处理过程提供帮助。如果脚本代码非常多，程序将需要一些时间来对其进行处理。

在下图中你可以看到，“eval”是高亮显示的。如果我只对“eval”进行反混淆处理，是不会成功的，因为我们还需要考虑到该脚本的编写方式。现在，我需要找出到底是哪一个函数调用了“szkmYVRfAFZYusP”。

点击“Reset（重置）”按钮之后，去掉了文本的高亮效果。然后，我在输入框中输入了“szkmYVRfAFZYusP”，再次点击“Highlight（高亮）”按钮，我们就可以在整个脚本代码中找到所有的“szkmYVRfAFZYusP”字符串。将窗口右侧的拖动条拖到最底部，你就可以看到到底是哪一个函数调用了它。

我双击了字符串“szkmYVRfAFZYusP”，然后点击“Convert（转换）”按钮。在这一操作之后，脚本就反混淆成功了。

**实例二（**[ **pastebin原地址**](http://pastebin.com/PTzRiBPU) **）**

从某种程度上来说，这个脚本的处理过程就有些困难了。你需要找出“eval”在哪里被调用了。首先，我尝试寻找“eval”。不幸的是，我什么也没有找到。然后我又尝试搜索“this”，这一次没有失败，我在代码的前端找到了它。

现在，我尝试搜索变量名为“mek”的变量。我在代码段的二分之三处发现了这个变量。

最后，我尝试搜索“wozv”。然后我发现它调用了变量“mhnW”。

我推测，“wozv”会对“mhnW”中的链接脚本进行验证（事实证明也确实是这样）。现在，我将“wozv”作为函数名和变量来进行高亮显示。使用这个方法的变量名必须是由单括号括起的。

由于文本输入框实际上是一个富文本框，所以选择文本可能会有些麻烦。按住Alt键，然后使用你的鼠标来选取文本。或者你也可以点击你所要选取的第一个字母，然后按住Shift键，然后使用小键盘的移位箭头来选取文本。

**实例三（**[ **pastebin原地址**](http://pastebin.com/hw2dbPn7) **）**

在这段脚本代码中，我首先搜索“eval”，我在代码段的五分之一处找到了它。

发现在这个脚本中，我无法对“eval”进行反混淆处理。那么让我来试试使用变量名来进行查询，果然成功了。

你可以点击[这里](http://www.kahusecurity.com/tools)获取最新版的Javascript
Deobfuscator。请记住，一定要在虚拟机中使用这个工具，并且关闭所有的安全防护软件。

本文翻译自360安全播报 [原文链接](http://www.kahusecurity.com/2016/javascript-deobfuscator-updated-2/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **WisFree** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83275](/post/id/83275)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://www.kahusecurity.com/2016/javascript-deobfuscator-updated-2/)

如若转载,请注明出处： <http://www.kahusecurity.com/2016/javascript-deobfuscator-updated-2/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t014c3fa13dce6c85dd.png) WisFree

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

