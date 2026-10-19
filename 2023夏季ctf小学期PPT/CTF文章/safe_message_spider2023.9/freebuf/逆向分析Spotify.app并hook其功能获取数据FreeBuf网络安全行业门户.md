**在开始本文的正式内容之前我想先来吐槽下。大多数的软件开发人员可能都有着这样一个烦恼，就是由于工作和其他责任，不得不搁置自己的一些个人项目甚至是最终完全的遗忘和埋没。而本文的所述的就是一个被我遗忘已久的项目，而我写这篇文章的目的就是希望能迫使我自己最终完成这个项目。好了，介绍就到这了让我们开始吧。**

## 项目

该项目的目标是构建一个Spotify客户端，让它能够学习我的听曲习惯并跳过一些我通常会跳过的歌曲。不得不承认，这种需求来自于我的懒惰。我不想在当我有心情想要听某些音乐时，创建或查找播放列表。我希望的是在我的库中选择一首歌，然后可以随机播放其他歌曲，并从队列中删除不“flow（节奏与旋律的流畅）”的歌曲。

为了实现这一点，我需要学习某种能够执行此任务的模型（在未来的帖子中可能更多）。但是为了能够训练一个模型，我首先需要数据来训练它。

## 数据

我需要完整的听歌历史记录，包括我跳过的那些歌曲。获取历史记录很简单。虽然Spotify API仅允许获取最近50首播放的歌曲，但我们可以设置一个cron
job来重复轮询该端点。完整代码已经发布在此处：<https://gist.github.com/SamL98/c1200a30cdb19103138308f72de8d198>

最困难的部分是跟踪跳过。Spotify Web API并没有为此提供任何的端点。之前我使用Spotify AppleScript
API创建了一些控制播放的服务（本文的其余部分将涉及到MacOS
Spotify客户端）。我可以使用这些服务来跟踪跳过的内容，但这感觉像是在回避挑战。我怎么能完成它呢？

## Hooking

我最近学习了解了有关hooking的技术，你可以在其中“拦截”从目标二进制文件生成的函数调用。我认为这将是跟踪跳过的最佳方法。

最常见的钩子类型是interpose hook。这种类型的钩子会覆盖PLT中的重定位，但这究竟意味着什么呢？

PLT或过程链接表允许你的代码引用外部函数（想想libc）而不知道该函数在内存中的位置，你只需引用PLT中的一个条目。链接器在运行时为PLT中的每个函数或符号执行“重定位”。这种方法的一个好处是，如果外部函数在不同的地址加载，则只需要更改PLT中的重定位，而不是每次对代码中该函数的引用。

因此，当我们为printf创建一个interpose
hook时，每当我们hooking的进程调用printf时，我们将调用printf的实现而不是libc（我们的自定义库通常也会调用标准实现）。

在对钩子有了一些基本的知识背景后，下面我们准备尝试在Spotify中插入一个钩子。但首先我们需要弄清楚我们想要hook的是什么。

## 寻找 hook 的位置

如前所述，只能为外部函数创建一个interpose hook，因此我们将在libc或Objective-C runtime中查找函数。

在研究在哪hook时，我认为一个开始hooking的好地方是Spotify处理“media control
keys”或我MacBook上的F7-F9。假设这些键的处理程序在spotify应用程序中单击Next按钮被调用时会调用函数。我最终在：<https://github.com/nevyn/spmediakeytap>上找到了SPMediaKeyTap库。我想我可以试一试，看看Spotify是否复制并粘贴了这个库中的代码。在SPMediaKeyTap库中，有一个方法startWatchingMediaKeys。我在Spotify二进制文件上运行了strings命令，看看他们是否有这个方法，果然：

![1.png](https://image.3001.net/images/20190614/1560483307_5d0315eb5e602.png!small)

Bingo!！如果我们将Spotify二进制文件加载到IDA（当然是免费版本）并搜索此字符串，我们就会找到相应的方法：

![2.png](https://image.3001.net/images/20190614/1560483320_5d0315f8012e0.png!small)

如果我们查看这个函数对应的源码，我们会发现CGEventTapCreate函数的有趣参数tapEventCallback：

![3.png](https://image.3001.net/images/20190614/1560483334_5d031606c829b.png!small)

如果我们回顾一下反汇编，我们可以看到sub_10010C230子例程作为tapEventCallback参数传递。如果我们查看这个函数的源码或反汇编，我们看到只调用了一个库函数CGEventTapEnable：

![4.png](https://image.3001.net/images/20190614/1560483350_5d03161605fa3.png!small)

让我们尝试hook这个函数。

我们需要做的第一件事是创建一个库来定义我们的自定义CGEventTapEnable。代码如下：

    
    
    #include <CoreFoundation/CoreFoundation.h>
    #include <dlfcn.h>
    #include <stdlib.h>
    #include <stdio.h>
    void CGEventTapEnable(CFMachPortRef tap, bool enable) 
    {
      typeof(CGEventTapEnable) *old_tap_enable;
      printf(“I'm hooked!\n”);
      old_tap_enable = dlsym(RTLD_NEXT, “CGEventTapEnable”);
      (*old_tap_enable)(tap, enable);
    }

dlsym函数调用获取实际库CGEventTapEnable函数的地址。然后我们调用旧的实现，这样我们就不会意外地破坏任何东西。让我们像这样编译我们的库（<https://ntvalk.blogspot.com/2013/11/hooking-explained-detouring-library.html>）：

    
    
    gcc -fno-common -c <filename>.c 
    gcc -dynamiclib -o <library name> <filename>.o

现在，让我们尝试在插入钩子时运行Spotify：DYLD_FORCE_FLAT_NAMESPACE=1
DYLD_INSERT_LIBRARIES=<library name>
/Applications/Spotify.app/Contents/MacOS/Spotify。点击进入：

![5.png](https://image.3001.net/images/20190614/1560483384_5d03163803b05.png!small)

Spotify打开正常，但Apple的系统完整性保护（SIP）没有让我们加载未签名库:(。

幸运的是，我是Apple的reasonably priced
developer项目的成员，所以我可以对库进行代码签名。这个问题算是得到了解决。让我们用100美元证书签名我们的库，运行上一个命令，然后......

![6.png](https://image.3001.net/images/20190614/1560483399_5d031647848ea.png!small)

失败。这一点不奇怪，Apple不允许你插入使用任何旧标识签名的库，只允许使用签名原始二进制文件时使用的库。看起来我们必须要找到另一种方法来hook
Spotify了。

作为补充说明，细心的读者可能会注意到我们hook的函数CGEventTapEnable，只有在media key
event超时时才会被调用。因此，即使我们可以插入钩子，我们也可能不会看到任何的输出。本节的主要目的是详细说明我最初的失败（和疏忽），并作为一个学习经验。

## HookCase

经过一番挖掘，我发现了一个非常棒的库HookCase：<https://github.com/steven-michaud/HookCase>。HookCase让我们实现一种比插入钩子（ patch hook）更为强大的钩子类型。

通过修改你希望hook的函数触发中断插入Patch
hooks。然后，内核可以处理此中断，然后将执行转移到我们的个人代码中。对于那些感兴趣的人，我强烈建议你阅读HookCase文档，因为它更为详细。

Patch
hooks不仅允许我们对外部函数的hook调用，而且允许我们hook目标二进制文件内的任何函数（因为它不依赖于PLT）。HookCase为我们提供了一个框架来插入patch和/或interpose
hooks，以及内核扩展来处理patch hooks生成的中断，并运行我们的自定义代码。

## 寻找 sub_100CC2E20

既然我们已经有办法hook Spotify二进制文件中的任何函数了，那么只剩下最后一个问题......就是位置在哪？

让我们重新访问SPMediaKeyTap源码，看看如何处理媒体控制键。在回调函数中，我们可以看到如果按下F7，F8或F9（NX_KEYTYPE_PREVIOUS，NX_KEYTYPE_PLAY等），我们将执行handleAndReleaseMediaKeyEvent选择器：

![7.png](https://image.3001.net/images/20190614/1560483424_5d0316601c350.png!small)

然后在所述选择器中通知delegate：

![8.png](https://image.3001.net/images/20190614/1560483435_5d03166b4fb7b.png!small)

让我们看看repo中的这个delegate方法：

![9.png](https://image.3001.net/images/20190614/1560483447_5d03167737929.png!small)

事实证明它只是为处理keys设置了一个模板。让我们在IDA中搜索receiveMediaKeyEvent函数，并查看相应函数的图形视图：

![10.png](https://image.3001.net/images/20190614/1560483464_5d0316885435e.png!small)

看起来非常相似，不是吗？我们可以看到，对每种类型的键都调用了一个公共函数sub_10006FE10，只设置了一个整数参数来区分它们。让我们hook它，看看我们是否可以记录按下的键。

我们可以从反汇编中看到，sub_10006FE10获得了两个参数：1)指向SPTClientAppDelegate单例的playerDelegate属性的指针，以及2）指定发生了什么类型事件的整数（0表示暂停/播放，3表示下一个，4表示上一个）。

看看sub_10006FE10（我不会在这里包含它，但我强烈建议你自己检查一下），我们可以看到它实际上是sub_10006DE40的包装器，其中包含了大部分内容：

![11.png](https://image.3001.net/images/20190614/1560483479_5d0316976b779.png!small)

哇！这看起来很复杂。让我们试着把它分解一下。

从这个图的结构来看，有一个指向顶部的节点有许多outgoing edges：

![12.png](https://image.3001.net/images/20190614/1560483493_5d0316a59f9c2.png!small)

正如IDA所建议的那样，这是esi（前面描述的第二个整数参数）上的switch语句。看起来Spotify的处理的不仅仅是Previous，Pause/Play和Next。让我们把关注点集中到处理Next或3
block：

![13.png](https://image.3001.net/images/20190614/1560483505_5d0316b174841.png!small)

不可否认，为此我花了一些时间，但我想请你注意底部第四行的call
r12。如果你查看其他的一些情况，你会发现一个非常相似的调用寄存器的模式。这似乎是一个很好的函数，但我们如何知道它在哪呢？

让我们打开一个新工具：debugger（调试器）。我最初尝试调试Spotify时遇到了很多麻烦。现在可能是因为我对调试器不太熟悉的原因，但我认为我想出了一个相当聪明的解决方案。

我们首先在sub_10006DE40上设置一个hook，然后我们在代码中触发一个断点。我们可以通过执行汇编指令int
3来做到这一点（例如像GDB和LLDB之类的调试）。

以下是在HookCase框架中hook的样子：

![14.png](https://image.3001.net/images/20190614/1560483523_5d0316c3af1c9.png!small)

将此添加到HookCase模板库后，你还必须将其添加到user_hooks数组：

![15.png](https://image.3001.net/images/20190614/1560483535_5d0316cf3dcbf.png!small)

然后我们可以使用Makefile
HookCase提供的模板来编译它。然后可以使用以下命令将库插入Spotify：HC_INSERT_LIBRARY=<full path to hook
dylib> /Applications/Spotify.app/Contents/MacOS/Spotify。

然后我们可以运行LLDB并将其attach到正在运行的Spotify进程，如下所示：

![16.png](https://image.3001.net/images/20190614/1560483549_5d0316dd4da8d.png!small)

尝试按F9（如果Spotify不是活动窗口，它可能会打开iTunes）。钩子中的int $3行应该触发了调试器。

现在我们可以进入到sub_10006DE40入口点这步。请注意，PC将位于与IDA中显示的地址相对应的位置（我认为这是由于进程加载到内存的位置所导致的）。在我当前的进程中，push
r15指令位于0x10718ee44：

![17.png](https://image.3001.net/images/20190614/1560483563_5d0316eb30fab.png!small)

在IDA中，该指令的地址为0x10006DE44，它给了我们一个偏移量0x7121000。在IDA中，调用r12指令的地址为0x10006E234。然后我们可以将偏移量添加到该地址，并相应地设置一个断点，b
-a 0x10718f234，然后继续。

当我们点击目标指令时，我们可以打印出寄存器r12的内容：

![18.png](https://image.3001.net/images/20190614/1560483575_5d0316f7513f3.png!small)

我们要做的就是从这个地址减去偏移量，看，我们获取到了我们名义上的地址：0x100CC2E20。

## Hooking sub_100CC2E20

现在，让我们来hook这个函数：

![19.png](https://image.3001.net/images/20190614/1560483587_5d031703cac53.png!small)

将其添加到user_hooks数组，编译，运行，并观察：每次按F9或单击Spotify应用程序中的next按钮，都会记录我们的消息。

现在我们已经hook了skip功能，

![20.JPG](https://image.3001.net/images/20190614/1560483600_5d031710af69f.jpg!small)

我将发布剩余的代码，但我不会完成其余部分的逆向工作，因为这篇文章已经够长的了。

简而言之，我也hook了previous功能（如果你照着做的话，这会是一个很好的练习）。然后，在这两个钩子中，我首先检查当前的歌曲是否已经过了一半。如果是的话，我什么都不做，假设我只是对这首歌感到厌倦，而不是觉得它不合适。然后在backs
(F7)，我弹出last skip。

针对如何检查当前歌曲是否已经过了一半的方法我想说几句。我最初的方法是实际调用popen，然后运行相应的AppleScript命令，但感觉这不太对。

我在Spotify二进制文件上运行了class-dump，发现了两个类：SPAppleScriptObjectModel和SPAppleScriptTrack。这些方法公开了播放位置，持续时间和曲目ID所需的必要属性。然后，我为这些属性hook了getter，并使用next和back
hooks调用它们（我认为Swizzle更合理，但我无法让它正常工作）。

我使用一个文件来跟踪skips，其中第一行包含跳过次数，在跳过时我们增加这个计数器，并将跟踪ID和时间戳写入计数器指定行上的文件。在back按钮，我们只是减少这个计数器。这样，当我们按下back按钮时，我们只是将文件设置为对已回溯文件写入new
skips。无论如何，这里的代码是：<https://gist.github.com/SamL98/0cd20b00951b9a5cca6b5c9380ec5642>

## 总结

希望通过本文你可以学习到一些新的知识，至少在这个过程中我已学到了很多东西。另外，如果你有任何更好的想法或建议请将它告诉我！谢谢！

 ***参考来源：[medium](https://medium.com/@lerner98/skiptracing-reversing-spotify-app-3a6df367287d)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

