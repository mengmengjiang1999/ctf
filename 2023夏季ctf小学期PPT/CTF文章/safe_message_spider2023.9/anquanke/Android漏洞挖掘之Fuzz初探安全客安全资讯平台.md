# Android漏洞挖掘之Fuzz初探

阅读量 **1486282**

|评论 **10**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-01-15 14:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01f3a6d620877a53e5.jpg)

本文是关于android漏洞挖掘的fuzz初探，主要工具是IntentFuzzer，对其进行详细的分析。

## android设备的攻击面

  * 远程攻击面 
    * 网络协议
    * 暴露的网络服务
    * 移动技术
    * 客户端
    * 浏览器
    * web引擎
  * 物理邻接攻击面 
    * GPS
    * 基带
    * 蓝牙
    * wifi
    * nfc
  * 本地攻击面 
    * 文件系统
    * sockets
    * binder
    * 系统安全方面的攻击方式都可以考虑
  * 物理攻击面 
    * usb
    * adb等

## android设备上的模糊测试

相对于整个信息安全社区，模糊测试在Android生态圈中并没有受到太多关注，尽管有人公开表示对模糊测试Android系统，但很少有人公开谈论他们具体做了哪些相关的工作，为数不多的公开演讲也仅仅关注单一且有限的攻击面。且直接针对android的高效模糊测试框架尚未建立。整体来讲，android设备上的大量攻击面还未被深入挖掘。

对目标应用做一次成功的模糊测试，大致需要一下4步：

  1. 选定目标
  2. 生成输入
  3. 传递测试用例
  4. 监控崩溃

这四步基本上是模糊测试的一个通用思路，其中涉及到的常见方法网络上有大量的文献可查，这里就不再累述。

## android fuzz的难点

android系统上的模糊测试和其他linux系统上的十分相似，利用unix工具如ptrace，管道，信号以及其他POSIX工具，对于开发出带有集成调试器的高级模糊测试工具时有利的，但很多其他因素又限制了Android上的模糊测试，如非linux组件带来的复杂性，软硬件的看门狗可能会使设备重启，Android系统中程序的依赖性可能会导致系统锁定或者程序故障，同时android设备还面临这一个问题：性能，不论是arm架构的物理设备还是sdk中的仿真器，其较低的性能依然会影响测试效率，除此之外通信速度也会带来问题，总而言之，android系统上有效的模糊测试相较于linux系统上的要难以实现的多，下文具体涉及到的难点再依次展开讲解。

## 选定目标

  1. android Intent
  2. android RIL无线接口层

**测试目标选择理由**
：由于android的攻击面很广，其牵扯到的知识点又繁杂，涉及kernel的模糊测试需要对linux等底层系统足够了解，而对物理接口等设备的模糊测试又或多或少会牵扯到硬件的一些基本知识，本文只是对android的一些攻击面做一个探索，所以暂不选定较为复杂的测试对象。

选择android
Intent的理由：Intent相对与android设备来说，是属于较高层次的ipc机制。在写android程序的时候，可以直接设置intent的相关操作和相应参数，且通过intent构造畸形数据去攻击android设备也是黑客常用的手段之一。

![](https://p0.ssl.qhimg.com/t0190821b8f86c006f4.png)

## 目标一：android Intent

IntentFuzzer工具简介：这个工具是针对Intent的Fuzzer。它通该工具能够针对一个简单组件或者是所有安装组件进行fuzz测试。它也适用于BroadcastReceiver，但针对Service只有较少的覆盖，Service通常更加广泛地应用Binder接口而不是针对IPC的Intent。原版的工具只能针对一个Activity进行fuzz测试，一次不能针对所有的Activity进行测试。MindMac在此基础上进行了一些修改，使其能够针对一个应用的一个简单组件或者是所有组件进行fuzz测试，同时具有区分系统应用和非系统应用的能力。MindMac修改后的版本仅针对Activity、BroadcastReceiver、Service。

但是代码本身却并不复杂，下面简单的介绍下：

整个fuzzer的核心代码如下：

![](https://p2.ssl.qhimg.com/t010f53a28734fcbe9b.png)

其原理是列举出系统上所有公开的、能够从应用获取到的Activity、BroadcastReceiver、Service、Instrumentation、ContentProvider。工具将通过Intent尝试启动所有可以获取到的组件，从而触发某些难以发掘的漏洞。触发一般有两类漏洞，一类是拒绝服务，一类的权限提升。拒绝服务危害性比较低，更多的只是影响应用服务质量；而权限提升将使得没有该权限的应用可以通过Intent触发拥有该权限的应用，从而帮助其完成越权行为。如果该工具能够轻易从外部启动特定应用的内部组件，尤其是有较高权限的组件时，很可能在此处发现漏洞。

下面来细致的分析原有代码以理解整个项目的框架，以便后续对其扩展和改进：

为了方便起见，我们先对util包中的Appinfo.java, Componentinfo.java, SerizlizableTest.java,
Untils.java四个文件进行基本的分析

  * Appinfo.java  

  * Componentinfo.java  

  * SerizlizableTest.java  

可以看到这三份代码分别实现了APPinfo类，Componentinfo类，和继承了Serializable接口的SerizlizableTest类，代表的含义又分别是每个app的信息，组件的信息和序列化测试

  * Untils.java  

Untils类中有如上图的两个主要方法和一些区分组件类型的标识符，其中getPackageInfo函数的逻辑是调用了content自带的函数去获取已安装的package信息，然后再根据是否是系统app，非系统app和其他，调用fillAppInfo将其信息装入Appinfo类型的数组中

  * MainActivity.java  

主体逻辑很简单，就是根据不同选择去获取相应app的信息或者选项3输出dialog信息

所以在startActivity后我们顺着程序的思路就应该转到AppInfoActivity.java了

  * AppInfoActivity.java  
  

可以看到AppInfoActivity的逻辑先是检测是否是属于app，并另起线程pkgInfoRunnable获取所有app的信息，并设置好相应的Adapter，准备完成之后，发送消息使相应的控件展示出信息，代码最后又是对点击进行监控，然后通过intent转到FuzzerActivity.java。（这里就不再累述AppinfoAdapter类了，就是一个普通的“展示”类）

  * FuzzerActivity.java  

其实FuzzerActivity的逻辑也很清晰，首先是获取当前所有的组件类型，然后再调用initView和initTypeSpinner。

![](https://p0.ssl.qhimg.com/t0130a491fa85d6da09.png)

![](https://p4.ssl.qhimg.com/t01d56c6261a66d6573.png)

initView的逻辑是针对cmpListView组件中的单个条目，短按发送NULL intent，长按发送Serializeable
Intent；针对两个按键fuzzAllNullBtn和fuzzAllSeBtn，分别对应发送NULL intent和Serializeable
Intent，

而具体的发送方式，可见也就是调用了系统函数而已。

![](https://p3.ssl.qhimg.com/t01ceef9d67b4301963.png)

initTypeSpinner是负责初始化Spinner组件的列表的，也就是组件选择列表

至此，基本已将代码主题逻辑分析完毕，具体细节请读者直接阅读源码。可以看到，作者只是大致写了个框架，代码并不复杂。但正当我决定继续深入探究时我发现了IntentFuzzer的论文原作，收录在ASIA
CCS论文集中，其引用数也有64，不幸的是这篇论文是收费的。。。。于是我决定适当地对其进行扩展，毕竟我觉得这个工具仍然具有很大的扩展空间，作者还是保持了它的简洁性。

**可以扩展的点**

  1. 发送的intent所包含的数据
  2. 发送的方式（Serizlizable或者其他）
  3. 效率，并行，自动化
  4. 处理错误机制
  5. 搜集组件的方式  
除了这些，扩展点可以从官方文档等地方去寻找，如下面几张从官方文档上截取下来的图：

![](https://p4.ssl.qhimg.com/t0175ba6b71a18e6366.png)

![](https://p1.ssl.qhimg.com/t01c1d94987d547c8ca.png)

![](https://p4.ssl.qhimg.com/t014443f6c085df8bdb.png)

![](https://p1.ssl.qhimg.com/t01e9a542182d7167a9.png)

可以看出，一些文档中提醒开发者注意避免的点往往是模糊测试可以考虑去深入的地方

**扩展举例** ：

由于时间比较有限，我暂时是对第一项进行了扩展，即对发送的intent变量进行填充，但是因为一开始没有严密考虑intent携带数据之间的联系，以及针对不同app，具有不同的intent接受属性（包括是否是隐式intent等），致使出现了多次intent
send
failed的状态。这一点可能需要构造更加合理的数据，甚至使用以往的poc以及exploits（据初步调研已经有不少公布了关于intent的poc），后续完善并注意实现扩展点后会将代码放到我的github上,
这里只放出我第一部分的主要代码逻辑，其实也很容易理解，就是增加intent包含的数据。

![](https://p5.ssl.qhimg.com/t01bf964c58bc099a2b.png)

![](https://p4.ssl.qhimg.com/t01cc2fa93b65c6623c.png)

![](https://p0.ssl.qhimg.com/t01328a2b86621528db.jpg)

**实验截图** ：

IntentFuzzer主界面

![](https://p0.ssl.qhimg.com/t0111b84e1de4e977d3.jpg)

相应的选择一类app进行fuzz，这里也可以看到alipay app的内部组件的封装隐蔽性做的还是很好的，只侦察到内部少数组件。

![](https://p3.ssl.qhimg.com/t01fcfb6b99e904ee4d.jpg)

![](https://p0.ssl.qhimg.com/t01f16318ac5cb1f4ac.jpg)

可以看到夸克的组件就要略差些，发送序列化intent和空intent都有可能导致夸克app停止运行。

![](https://p2.ssl.qhimg.com/t016685c439d7642b6d.jpg)

![](https://p2.ssl.qhimg.com/t01b1dc4b227b1583e6.jpg)

![](https://p3.ssl.qhimg.com/t01c6a70245528d0381.jpg)

当然我们测试的对象怎么能少了铁路12306呢？可以看到发送的intent甚至可以触发其达到其他的组件显示出的界面，让我比较惊讶的是竟然还有H5测试页面和微信支付测试等界面出现，感觉可能是12306官方app自己为了下次测试省力，而没有删去或者隐蔽好支付等相关的测试组件。

![](https://p2.ssl.qhimg.com/t01e21648be585c9a14.jpg)

![](https://p0.ssl.qhimg.com/t01b9d34123474018d9.jpg)

![](https://p1.ssl.qhimg.com/t01f75675c29f95ca9e.jpg)

![](https://p4.ssl.qhimg.com/t01f1d9aa5d684cfe06.jpg)

![](https://p2.ssl.qhimg.com/t0165b9ef3178fa73e2.jpg)

![](https://p3.ssl.qhimg.com/t01953d3018c97bb9e0.jpg)

这些是实验的部分截图，但可惜的是IntentFuzzer并没有建立完善的错误处理机制，所以一开始对其分析的时候，只能借助于本地的Android
Studio等其他工具进行栈回溯之类的操作，效率比较低，这里就不贴图了，但这是一个很值得进行扩展的点，需要自己去编写合理的处理机制，或者调用外部工具API来实现错误分析。

## 这里再放一个目标二的研究

选择android
RIL无线接口层的理由：android设备接入网络的底层模块是基带，基带是蜂窝调制解调器制造商使用的固件，用于智能设备连接到蜂窝网络，发送和接收数据，并进行语音通话。而RIL为蜂窝调制解调器提供接口，是Android设备平台中负责移动通信的核心组件。

  * RIL简介： 负责移动通信中所有具体的业务，是android中极少数可以直接从外界接触到的代码之一，其攻击面可类比服务器上部署的网络服务，从移动网络发送到android设备的所有数据都会经过设备中的RIL，最好的例子便是短信（sms）的接收处理过程。  
智能手机通用架构图：可以看到分为主处理器和蜂窝调制解调器两个子系统  
  
android电话栈图：可分为应用程序，应用程序框架，RIL守护程序和内核级设备驱动四个部分  

目标二做到一半停止了，主要原因是做之前没有先进行初步测试，蜂窝调制解调技术早在多年前就已经出现，但是我在新型的4g，5g手机扫描时并没有发现相应的rild进程，或者只有些许，猜测可能是厂商做了更好的封装或者替代？如果要对此拓展的话可能会涉及到各个公司使用的相关协议栈等设计实验。总之，感觉且工程性较大，就暂时搁置了。

## 参考文献

《Android安全攻防权威指南》

<https://developer.android.google.cn/guide/components/intents-filters?hl=zh_cn#java>

<https://developer.android.google.cn/reference/android/content/Intent.html#putExtra(java.lang.String,%20android.os.Parcelable>)

<https://github.com/MindMac/IntentFuzzer>

阅读以及翻译的一些论文可以参考我的博客或者一个大佬建的仓库：

<https://dawuge.github.io/>

<https://github.com/bsauce/Some-Papers-About-Fuzzing>

and 欢迎交流或者带带弟弟。。。。

## 总结

总的来说，时间比较紧迫，大致花了一天半的时间去阅读源码和搭建环境，感觉收获还是挺多的。这里大致说一下自己的一些想法：

首先fuzz这一项技术的考虑，这一次阅读到7 Things to Consider Before Fuzzing a Large Open Source
Project这一篇文章，感觉还是写的还是挺实在的，在fuzz之前需要明确自己的目标，fuzz终究是一项工具，应该将其作为我们加快效率的一种手段，就像神经网络一样，是为了更好的完成任务而去做的。其次，明确需要检测什么样的错误，然后根据错误特征去设计处理机制甚至是种子样本的构建。接下来是确定地分类你需要的fuzz工具类型以，尽可能地寻找现有的工具，去生成新的fuzz工具或者新的fuzz思路，当完成一个阶段后，学会考虑现阶段fuzz工具的价值，具体分析后再去重新编写fuzz模块也好，尝试人工挖掘也行，总之一切为了效率：）
最后，学会学习前辈们的思路，站在巨人的肩膀上可以让你前进的更快。

然后是另一方面的看法，个人认为fuzz本质说到底只是一个为了提高效率的自动化工具，它的前景是可以预估的，可能最终的效果是安全大脑类型的一种智能化漏洞挖掘技术，其根本上的创新性可能没有太多其他的亮点，这是由fuzz这一项技术本身的性质所决定的，但是在达到这个目标之前，我们还是有很长的路要走，当世界甚至万物开始产生更多人为的联系时，fuzz技术可探寻以及运用的领域也在逐渐增多。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Dawuge** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197083](/post/id/197083)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android](/tag/Android)
  * [移动安全](/tag/移动安全)
  * [Fuzz](/tag/Fuzz)

 **+1** __15赞

 __收藏

![](https://p2.ssl.qhimg.com/t01845a44b584369f66.png) Dawuge

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

