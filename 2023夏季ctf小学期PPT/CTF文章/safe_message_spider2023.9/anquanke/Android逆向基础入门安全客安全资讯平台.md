# Android逆向：基础入门

阅读量 **357077**

|评论 **1**

发布时间 : 2022-05-19 14:30:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t016d38ea5139303bb2.jpg)

## 前言

随着app的广泛应用，使用过程中，难免会遇到些很不友好的功能，比如：游戏充值、间断性弹窗广告、续费解锁下一回等等。

如何将这些功能给XX掉？Android逆向就可以做到，纵向丝滑。

当然这只是安卓逆向的 **非专业性作用** 之一，安卓逆向的作用不仅限于此，之所以以此引入，是因为激发学习最大的动力——兴趣，有了兴趣，你们想不学都不行。

网上教程上都这样讲，学习安卓逆向，不可避免的需要掌握一定的java基础、等等这就话虽说没错，但对于零基础的小白，难道要先学这些编程语言再去入手逆向吗？

我的想法是，采用理论实践相结合，边练边学，这样印象才更加深入人心啊

当然此观念是在经过两节框架式知识铺垫的前提下，想了解andorid逆向，没有提前做功课可不行。接下来这篇文章呢，大家就当科普内容，先了解下andnroid系统的运行机制、框架及andorid应用程序的相关知识。

## 目录

  1. **android系统架构**
  2. **Dalvik虚拟机与ART虚拟机**
  3. **android应用程序架构**
  4. **android应用编译流程**
  5. **android应用反编译流程及工具利用**
  6. **android逆向概述**

## android系统架构

### android系统

安卓（Android）是一种 **基于Linux内核** （不包含GNU组件）的自由及开放源代码的操作系统。主要使用于移动设备，如智能手机和平板电脑，
**由美国Google公司和开放手机联盟领导及开发** 。

### android系统架构

左边的就是android系统框架了，右边我加了备注，这样更加明了，我们可以看到，android系统架构共 **分四层** ， **从下往上** 分别是：
**Linux内核层** 、 **系统运行库层** （程序库+android运行库）、 **应用程序框架层** 、 **应用层** 。

**大家重点关注下Android Runtime这一部分，其他的简单了解下就可以涉及到后面的讲解** ：

  1. **Llnux内核层：** Android系统是基于Linux内核的,它提供了基本的系统功能及与硬件交互的驱动，像图中Display Driver（显示驱动）、Camera Driver（摄像头驱动）、WiFi Driver（WiFi驱动）等， **简单了解下就可以** 。
  2. **系统运行库层：** 像图中内核的上一层就是系统运行库层，它由 **程序库（绿色部分）** 和 **Android运行库（黄色部分）** 组成。
  3. **Librares（程序库）：** 由C、C++编写，一系列程序库的集合，供Android系统的各个组件使用。其中包括:

系统类库名称 | 说明  
---|---  
Surface Manager | 执行多个应用程序时，管理子系统的显示，另外也对2D和3D图形提供支持  
Media Framework |
基PacketVideoOpenCore的多媒体库，支持多种常用的音频和视频格式的录制和回放，所支持的编码格式包括MPEG4，MP3，H264，AAC，ARM  
SQLite | 本地小型关系数据库，Android提供了一些新的SQLite数据库API，以替代传统的耗费资源的JDBC API  
OpenGL/ES | 基于OpenGL ES 1.0API标准实现的3D跨平台图形库  
FreeType | 用于显示位图和矢量字体  
WebKit | Web浏览器的软件引擎  
SGL | 底层的2D图形引擎  
Libc（bionic l ibc） | 继承自BSD的C函数库bionic libc，更适合基于嵌入式Linux的移动设备  
SSL | 安全套接层，是为网络通信提供安全及数据完整性的一种安全协议  
  
  1. **Android runtime（Core Librares + Dalvik虚拟机）：** 翻译过来就是Android运行时，Android应用程序时采用Java语言编写， **程序在Android运行时中执行** ，其运行时分为 **核心库** 和 **Dalvik虚拟机** 两部分。
  2. **Dalvik虚拟机（DVM）：**
  3. 而 Dalvik虚拟机又是什么鬼？
  4.   5. 它呢就类似java虚拟机，所有Android应用程序基本是在Dalvik虚拟机环境下运行的。下面会有单独一章给大家介绍。
  6. **Core Librares（核心库）：** 由于DVM也是兼容java语言的，所以Android核心库，它里面都集成了支持JAVA语言的jar包，
  7. **application Framework（应用程序框架层）：** 这一层呢主要是提供一些组件，搭建框架，方便app开发人用再次基础上快速开发开发应用程序。而实际上就是一些AndroidAPI, **简单了解下就可以**

应用程序框架层类库名称 | 功能  
---|---  
活动管理器（Activity Mananger） | 管理各个应用程序生命周期并提供常用的导航回退功能，为所有程序的窗口提供交互的接口  
窗口管理器（Window Manager） | 对所有开启的窗口程序进行管理  
内容提供器（Content Provider） | 提供一个应用程序访问另一个应用程序数据的功能，或者实现应用程序之间的数据共享视图系统（View
System）创建应用程序的基本组件，包括列表（lists），网格（grids），文本框（text
boxes），按钮（buttons），还有可嵌入的web浏览器。  
通知管理器（Notification Manager） | 使应用程序可以在状态栏中显示自定义的客户提示信息  
包管理器（Package Manager） | 对应用程序进行管理，提供的功能诸如安装应用程序，卸载应用程序，查询相关权限信息等。  
资源管理器（Resource Manager） | 提供各种非代码资源供应用程序使用，如本地化字符串，图片，音频等  
位置管理器（Location Manager） | 提供位置服务  
电话管理器（Telephony Manager） | 管理所有的移动设备功能XMPP服务是Google在线即时交流软件中一个通用的进程，提供后台推送服务  
  
  1. **Applications（应用层）：** 顶层中有所有的 Android 应用程序，如手机中的：电话、文件管理、信息等。

## Dalvik虚拟机与ART虚拟机

### Dalvik虚拟机

Dalvik是google专门为Android操作系统设计的一个虚拟机, **简称DVM** 。 **在Android 4.4及以前的版本，**
所有的Android程序都是在Dalvik虚拟机环境下去运行的。DVM的指令是 **基于寄存器** 的，运行的是经过转换的 **.dex文件**
（.dex是专为Dalvik设计的一种压缩格式，适合内存和处理器速度有限的系统）,Dalvik虚拟机每次应用运行的时候，将代码编译成机器语言执行。

而DVM与JVM的区别:

  1. **JVM运行的是Java字节码,DM运行的是 Dalvik字节码。**
  2. 传统java程序经过编译，生成java字节码保存在class文件中，java虚拟机通过解码class文件来运行程序，而 Dalvik虚拟机运行的是Dalvik字节码，所有的Dalvik字节码都由java字节码转换而来，并打包到一个dex可执行文件（.dex）,Dalvik虚拟机通过解释DEX文件来执行字节码。
  3. **DVM是基于寄存器的虚拟机 而JVM执行是基于虚拟栈的虚拟机。**
  4. 寄存器存取速度比栈快的多，dvm可以根据硬件实现最大的优化，比较适合移动设备。
  5. 以下是同段代码经反编译形成的java字节码与Dalvik字节码对比
  6. java字节码
  7.   8. Dalvik字节码
  9.   10. **dvm执行的是.dex格式文件，jvm执行的是.class文件**
  11. .dex文件，是DVM独有的执行文件格式，体积更小，速度跟快，占用空间更少
  12. **运行环境的区别**
  13. Dalvik 经过优化，允许在有限的内存中同时运行多个虚拟机的实例，并且每一个Dalvik 应用作为一个独立的Linux 进程执行。独立的进程可以防止在虚拟机崩溃的时候所有程序都被关闭。

### ART虚拟机

前面说到，当我们使用手机每运行一个程序，Dalvik虚拟机都会产生一个实例，互不影响，这就可能会出现占用资源过多等问题，随着人们日益增长的需求，dalvik无法满足人们对软件运行效率的需要。这是就诞生了ART虚拟机。

在 **Android4.4及以上版本** ，应运而生的ART（Android Run
Time）虚拟机替代了Dalvik虚拟机，其处理机制根本上的区别是它采用AOT(Ahead of TIme)技术，
**会在应用程序安装时就转换成机器语言，不再在执行时解释**
，从而优化了应用运行的速度。在内存管理方面，ART也有比较大的改进，对内存分配和回收都做了算法优化，降低了内存碎片化程度，回收时间也得以缩短。

**DVM与ART的区别：**
虽说ART替换了Dalvik虚拟机，并不意味着，其应用程序开发上也要发生改变，像android应用程序安装包（apk）中，仍然还是可执行的.dex文件。

  1. **执行方式：运行效率提高**
  2. DVM是在每当程序运行时，通过解释器来执行Davlik字节码，进而转化成快速运行的机器码；而ART是在程序安装时将字节码预先编译成机器码，这样运行程序就不用再次编译
  3. **预装时间：增加**
  4. ART安装程序的时间会长一些，但是每次运行程序会快一点；dvm相反
  5. **占用存储空间：增加**
  6. art由于预编译，所以所占的存储空间会大一些
  7. **支持64位 CPU**
  8. DVM是为32位CPU设计的，而ART是支持64位并且兼容32位CPU

## Android应用程序架构

安卓应用程序使用JAVA语言编写。安卓的SDK工具负责将你编写的代码，用到的数据和资源文件编译进APK文件中，APK：android
package（应用程序安装包）。apk文件包含了一个安卓应用程序的所有内容，并且被安卓设备用来安装应用程序。

而apk实际上就是一个标准的zip格式，修改后缀名，进行解压就可以看到内部结构

而每个文件夹都有各自不同的作用，大家可以了解下

  1. **assets文件夹：** 保存一些额外的资源文件，如游戏的声音文件，字体文件等等，在代码中可以用AssetManager获取assets文件夹的资源。
  2. **lib文件夹：** 存放用C/C++编写的，用NDK编译生成的so文件，供java端调用。
  3. **META-INF文件夹：** 存放apk签名信息，用来保证apk包的完整性和系统的安全。
  4. 在IDE编译生成一个apk包时，会对里面所有的文件做一个校验计算，并把计算结果存放在META-INF文件夹内，apk在安装的时候，系统会按照同样的算法对apk包里面的文件做校验，如果结果与META-INF里面的值不一样，系统就不会安装这个apk，这就保证了apk包里的文件不能被随意替换。比如拿到一个apk包后，如果想要替换里面的一幅图片，一段代码， 或一段版权信息，想直接解压缩、替换再重新打包，基本是不可能的。如此一来就给病毒感染和恶意修改增加了难度，有助于保护系 统的安全。
  5. **res文件夹：** 存放资源文件，包括icon，xml文件
  6. **res/layout/:** 存放被编译为屏幕布局（或屏幕的一部分）的XML文件
  7. **res/values/:** 存放可以被编译成很多类型的资源文件
  8. **array.xml:** 定义数组
  9. **string.xml:** 定义字符串（string）值
  10. **AndroidManifest.xml文件：** 应用程序配置文件，每个应用都必须定义和包含的，它描述了应用的名字、版本、权限、引用的库文件等信息。
  11. **classes.dex文件：** 传统 Class 文件是由一个 Java 源码文件生成的 .Class 文件，而 Android 是把所有 Class 文件进行合并优化，然后生成一个最终的 class.dex 文件。它包含 APK 的可执行代码，是分析 Android 软件时最常见的目标。由于dex文件很难看懂，可通过apktool反编译得到.smali文件，smali文件是对Dalvik虚拟机字节码的一种解释（也可以说是翻译），并非一种官方标准语言。通过对smali文件的解读可以获取源码的信息。
  12. **resources.arsc文件：** 二进制资源文件，包括字符串等。
  13. **smali:** smali是将Android字节码用可阅读的字符串形式表现出来的一种语言,可以称之为Android字节码的反汇编语言。利用apktool或者Android Killer，反编classes.dex文件，就可以得到以smali为后缀的文件，这些smali文件就是Dalvik的寄存器语言。

## Android应用编译流程

Android应用编译流程按图中的例子就是一个app应用的生成过程。在应用程序上架的时候都需要程序经过编译、签名
、生成一个后缀为apk的文件才能发布到应用市场。

下面给大家简单讲解下：

  1. **第一步：打包资源文件，生成R.java文件**
  2. 通过利用aapt资源打包工具，将文件目录中的Resource文件（就是工程中res中的文件）、Assets文件、AndroidManifest.xml文件、Android基础类库（Android.jar文件）进行打包，生成R.java
  3. **第二步：aidl生成Java文件**
  4. AIDL是Android Interface Definition Language的简称， 是Android跨进程通讯的一种方式。 检索工程里所有的aidl文件，并转换为对应的Java文件
  5. **第三步：编译Java文件，生成对应的.class文件**
  6. 将R.java、aidl生成的Java文件、Java源文件通过JDK携带的Javac编译生成.class文件
  7. **第四步：把.class文件转化成Davik VM支持的.dex文件**
  8. 通过dx工具将.class文件生成为classes.dex
  9. **第五步：打包生成未签名的.apk文件**
  10. 利用apkbuilder工具，将resources.arsc、res目录、AndroidManifest.xml、assets目录、dex文件打包成未签名的apk
  11. **第六步：对未签名.apk文件进行签名**
  12. 使用apksigner为安装包添加签名信息。
  13. **第七步：对签名后的.apk文件进行对齐处理**
  14. 使用zipalign工具对签名包进行内存对齐操作， 即优化安装包的结构。

## Android应用反编译流程及工具利用

而Android应用反编译流程就是上面所讲的app生成过程的逆过程。Android应用程序的反编译，算是我们入手Android逆向展开实践的第一步。

下面给大家简单讲解下流程：

首先可以看到最左边的目标unsigned apk，即未签名apk。整体可以看出有两条反编译路线。

**反编译方式一：**
图中上面这条路线是通过利用apktool这款工具，可直接对目标apk直接进行反编译，可以看到除apk本身的资源文件，还生成了smali文件，而smali文件里面包含的都是程序执行的核心代码。我们可以通过直接分析.smali文件中的smali代码，进而修改代码，改变其运行逻辑。

**apktool工具下载地址：**

<https://bitbucket.org/iBotPeaches/apktool/downloads/>

**利用方式：** cmd运行命令

apktool d target.apk

![](https://p0.ssl.qhimg.com/t011b9fa9e4edbe5fc0.png)

反编译完成后会生成文件夹

![](https://p1.ssl.qhimg.com/t015dc86ed92754c1d8.png)

**反编译方式二：**
图中下面这条路线是通过修改apk后缀名，对其解压后，将文件夹中的资源文件，通过利用AXMLPrinter2进行分析，进而反编译，而对于解压后的class.dex文件，利用Dex2jar反编译工具对其进行反编译得到jar文件。接着将生成的jar文件直接拖到JD-GUI文件中，可自动生成源码，我们可通过分析其源码，了解其程序的运行逻辑，但我们修改逻辑，最终还是需要在smali文件中进行修改。

**dex2jar下载地址：**<https://sourceforge.net/projects/dex2jar/files/>

**利用方式：** cmd运行命令

dex2jar.bat classes.dex

![](https://p5.ssl.qhimg.com/t01d10baf4398b20630.png)

目录生成新的jar

![](https://p3.ssl.qhimg.com/t016aaff75dc49094de.png)

而jd-gui反编译工具的使用方法，可直接将jar文件拖到工具中，会自动进行反编译出源码进行查看

**jd-gui下载地址：**<http://java-decompiler.github.io/>

### 工具推荐

以上就是传统的Android反编译流程，若想具体了解过程，可通过上述流程进行自我复现。

而在Android逆向的实际应用中，个人比较推荐 **Android killer** 与 **jadx-gui** 这两款工具

  1. **Android killer：** 是集 **Apk反编译** 、 **Apk打包** 、 **Apk签名** ， **编码互转** ， **ADB通信** （应用安装-卸载-运行-设备文件管理）、 **源码查看** 等特色功能于一身，支持logcat日志输出，语法高亮，基于关键字（支持单行代码或多行代码段）项目内搜索，可自定义外部工具；吸收融汇多种工具功能与特点，是一款可视化的安卓应用逆向工具。
  2. 可以说在Android逆向，这款工具可实现上述反编译流程一把梭，这大大节省了操作时间，也提高了我们的效率。
  3.   4. **AndroidKiller下载地址：**<https://down.52pojie.cn/Tools/Android_Tools/AndroidKiller_v1.3.1.zip>
  5. **jadx-gui：** 是一款可以将apk，dex，aar 和 zip 文件将 Dalvik 字节码反编译为 Java 类的JAVA反编译工具。
  6. 而它是支持apk、dex、aar、zip等格式，所以我们在使用过程中，可直接将待测apk拖入的工具中，会自动执行反编译
  7.   8. **jadx-gui下载地址：**<https://down.52pojie.cn/Tools/Android_Tools/jadx_v1.3.4.zip>

## Android逆向概述

ok，基本的知识框架体系已经啰嗦完了，现在开始我们的重点——Android逆向。

### 什么是Android逆向呢？

**官方话语：** Android逆向是对已经打包好的APP进行反编译、源码分析了解APP实现逻辑的一门技术。

**通俗理解呢:就是玩具（** app **）经过零件组装** （源码编译） **、加工刷漆** （打包、签名）
**生成成品的逆过程。我们把成品的app，再将它打回零件形态——源码，通过更改它的零件** （代码） **，再进行重组装** （重编译）
**，使它可以飞天、遁地等等** （改变运行逻辑）

当然，这里的更改零件，指的可不是app的源码，而是经反编译后的 **smali代码** 。

而在实际应用中，我们逆向的话，需要用到解密、反编译、解压缩等技术，想要100%还原APK的源码几乎是不可能的，所以在实际进行逆向分析的时候，一般都是根据想实现的目的，分析出APK的部分源码和实现逻辑，然后对这一部分源码进行修改后与原始的APK打包在一起，这样就获得了一个实现自己特定目的的APP。

## 总结与思考

以上文章就介绍的到这里,读到这里可能你们都觉得本篇涉及逆向的知识点并不多，而我也说过，了解Android逆向，要先了解Android，之所以这样说呢，是因为Android逆向的学习，最终还是要归到Android本身，有了前面的了解，相信会对接下来Android逆向分析上有着很大帮助。

后面要讲的就是逆向分析的手段以及具体流程，实践与理论结合的边练边学了，大家可以自己针对Android应用程序的反编译流程操练一番，备好工具，下一篇开搞。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/273348](/post/id/273348)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android](/tag/Android)
  * [逆向](/tag/逆向)

 **+1** __7赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

