![xxxxxx.png](https://image.3001.net/images/20180611/15287092073407.png!small)

**两个月以前，我在ITsec公司开始了我大学最后一年的实习生涯。ITsec是一家全方位的信息安全评估公司，我的实习工作就是开发一个以供公司内部使用的安卓APP。通常，我在检查程序Bug时总是会把关注点放在Web层面，而忽视了安卓APP的安全问题。所以，经过我一段时间针对安卓应用的安全研究之后，有所收获，简单写在这里和大家分享。**

这里最直接的方式就是通过一些漏洞众测网站来学习，如 Hackerone 和 Bugcrowd
上就有好多众测厂商在项目里标明的一些需要安全测试的Android 或 iOS
应用。有很多种测试.apk应用程序的方法，本文我要介绍的是如何利用这些厂商提供的apk文件，来发现其中涉及的服务端，进一步扩大攻击测试面。

## 部署测试环境

当然先要来搭建测试环境了，我这里用的操作系统是Fedora
27，因为我注意到与Windows相比，Fedora的速度有很大的提高，兼容性问题也相对较少。当然，作为一个安全小白，我现在正在为MacBook
Pro而奋斗中。

首先，我们要来搭建的就是 [Android Studio](https://developer.android.com/studio/index.html)
这个官方的集成开发环境：

> 针对各类安卓设备，Android Studio
> 内置了能快速开发生成相关安卓APP的工具，这是一个优秀的代码编辑、调试和优化环境，能即时构建/部署独特且可靠高效的APP应用，非常灵活。

具体安装步骤我就不一一赘述了，有问题联系我就好。在 Android Studio
中内置了一个虚拟机或者叫一个模拟器，我们可以利用这个模拟的安卓环境来测试.apk文件，这样就不需要额外购买一个安卓手机进行实测了，而且这种模拟环境还具备便利的系统恢复功能。虽然这种在模拟器和物理机之间的测试方法，也会存在一些明显的利弊因素，但暂且不管那么多了，接下来我们还是用模拟器来进行一些测试。

这有一个不启动Android Studio就可以运行模拟器的脚本：  

    
    
    # android.sh
    
    #!/bin/bash
    
    cd ~/Android/Sdk/tools && ./emulator -avd x1m-demo-avd1 -no-snapshot-load

该脚本会涉及模拟器的一些初始设置，你可以在Android Studio -> AVD Manager中来完成。

![02.png](https://image.3001.net/images/20180611/15287083666809.png!small)另外，我们还需要一个Java开发套件，你可以在你的系统终端上用命令
java -version 来检查你当前的java版本，如果没有，只能安装了。我Fedora系统中的安装命令如下：

    
    
    sudo dnf install java-1.8.0-openjdk-devel

对工具要求上来说，我们会用到 Java 7 或更高版本的 JRE
1.7环境，貌似所有的Linux发行版本都默认安装了这个版本的运行环境。环境准备就绪，我们就开始测试吧。

## 测试

测试Android应用程序不同于测试web应用程序，它需要逆向工程、Java、API等方面的技能。如果你在这些方面欠缺经验，可能就有点麻烦了。我现在也正在努力地啃学这各方面的东西，所以坚持的耐性在这里就显得尤为重要了。你可以通过一些使用指南和自述文件，并尝试开发自己的移动应用APP。在此我们先来看一下apk文件的反编译，通过这种方式来在前期侦查和漏洞挖掘中发现一些“简单”的问题。

我们需要一个反编译程序，用它可以把一个.apk文件转换为原始代码。在反编译过程中，我们能对应用的输出作一些检查，从中可以发现一些API密钥甚至是Web端密码等隐藏字符串信息。

### 所需工具  

我们需要一个反编译程序。反编译程序尝试转换。apk文件到它的原始源代码。在反编译之后，我们可以检查输出，以查找隐藏的字符串，比如API键，甚至某些web服务的凭据。这样的工具有：  

>
> [jadx](https://github.com/skylot/jadx)：这是一个Dex到Java文件的反编译器，也是我最喜欢用的安卓APPdecompiler之一。它使用非常简单，能从Android
> Dex文件或从apk文件中，通过命令行和界面接口两种方式生成源代码。  
>

![03.png](https://image.3001.net/images/20180611/15287085791243.png!small)

>
> [Apktool](https://ibotpeaches.github.io/Apktool/)：这是一个可用于逆向安卓APP的工具，它能把资源还原成几乎原始的形式，并可进行一些修改后再重新构建。由于具备文件结构项目和构建Apk等某些重复性操作的自动执行功能，所以它能让APP的使用变得更简单容易。

![04.png](https://image.3001.net/images/20180611/15287086178039.png!small)

以上这两个工具都很好，我个人比较喜欢用 jadx ，后续的测试中我会用它来进行。

> [APK Downloader (Ruby)](http://apps.evozi.com/apk-downloader)：用它可直接从网页下载
> Google Play 应用商店中的 APK 文件，省去了多余的步骤，只需提交相应APP的 URL 下载地址即可。

### 测试开始

我们先来反编译一个 .apk 文件吧：

![05.png](https://image.3001.net/images/20180611/15287087138221.png!small)  

就用 Imgur 官方的安卓APP来试试吧，它可以被正常下载，下载好之后，我们就要用jadx对它进行一些反编译操作：

    
    
    ./jadx -d ~/bugbounty/Imgur/ ~/bugbounty/Imgur/imgur_mobile_v4.0.1.6893.apk 

我没有在其中插入一些标志，其实也可这么做。有时候当源码非常混淆，则可以用 Jadx 的某些选项来还原出很多具备可读性的源码，具体大家可以查看
--help选项说明。

如果我们去到 Jadx 反编译后的目标APP目录，可以发现其apk文件已经被转换为了源码文件。我们可以看到两个目录：Resources 和 Sources。

> Resources：其中包含了如AndroidManifest.xml、字符串等所有的静态文件
>
> Sources：包含了所有的开发代码和APP运行所需的第三方代码

![06.png](https://image.3001.net/images/20180611/15287087672519.png!small)  

我们一起来看看这些静态文件，先以这个AndroidManifest.xml文件开始，这个文件在每个安卓APP中都扮演了重要作用，在此文件中，开发人员确定了APP所需的各种权限，以及APP操作会产生的各种行为活动。AndroidManifest.xml
一般位于 /resources/AndroidManifest.xml 。

![07.png](https://image.3001.net/images/20180611/15287088247798.png!small)  

## AndroidManifest.xml 检查清单

调试模式：这是开发人员通常会忽视的一个错误，他们会经常忘记把 android:debuggable="true" 设置为
android:debuggable="false"，安全起见，这标签在APP发布之前都应该设置为false的：

    
    
    <application>
    
    android:debuggable="false"
    
    </application>

备份允许：如果你的APP运行之后会存储有密码、信用卡等敏感数据信息，可以把这里设置为"false" ：

    
    
    <application>
    
    android:allowBackup="false"
    
    </application>

外部存储：该功能为有权限把数据拷贝到SD卡等外部载体中进行存储，这里也需要明确存储数据是否存在一些敏感信息：

    
    
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>

权限：在安卓APP的android:protectionLevel属性中，有normal、dangerous、signature和signatureOrSystem
四种权限值可以赋予：

    
    
    <permission>
    
    android:protectionLevel="signature"
    
    </permission>

意图: 也就是各种函数的具体执行目的，如用于发起行为的、发送给广播接收器组件的或与后台某个服务进行通信的，等等：

    
    
    <intent-filter>
    
    <action android:name="sting" />
    
    <category android:name="string" />
    
    </intent-filter>

我们在测试一个安卓APP时，经常要涉及到以上各项的安全检查。在前期侦测阶段我们就要选好突破口，尤其是这里的 AndroidManifest.xml
就是一个很好的选择。

## 深挖分析

另外，我还会看一下安卓APP的硬编码字符串，几乎所有可见的安卓应用文本内容都是存储在/values/strings.xml
文件中的，当然如果幸运的话，会发现一些未经编码的硬编码信息。

通常我们都会认为，APP开发人员应该不会把一些敏感信息存留在一些更编码数据中，但是，也有例外啊，我就曾多次通过这种strings.xml发现了一些APP敏感信息。

在strings.xml中可能会包含一些API密钥、密码和其它有用信息，在HackerOne今年3月的[H1-202
CTF](https://www.hackerone.com/blog/h1-202-CTF-Winners-Announced)中就有一道题的flag涉及这种硬编码方式。

    
    
    <string name ="first_flag">flag{easier_th4n_voting_4_pr3z}</string>

你能很快定位到这种strings.xml文件，可以在你随便一个编辑器中找到APP应用的/res/values/strings.xml，ctrl + f
来查看相关有有信息，或者直接用grep命令来进行查找：

    
    
    grep -Hrn 'juicystring' ~/bugbounty/Imgur/resources/res/values

好吧，这就算是我们的第一部分文章吧，希望你能理解消化。下一节中，我会讲解一些逆向技巧，以及一些外部链接查找和相关的工具使用，敬请关注。

 ***参考来源：[x1m](https://x1m.nl/posts/android-app-testing-part-1/)，FreeBuf 小编
clouds 编译，转载请注明来自 FreeBuf.COM**  

