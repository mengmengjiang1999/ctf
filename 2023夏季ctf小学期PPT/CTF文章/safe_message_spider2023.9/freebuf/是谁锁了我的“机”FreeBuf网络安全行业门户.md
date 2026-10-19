## 前言

锁机一直是个值得长期讨论的话题，许多安卓用户被某些特殊的应用名称或图标所吸引（如某些游戏外挂、xx神器、刷赞等），从而被诱导下载安装，授权后导致手机屏幕被锁，用户无法正常使用手机，并通过这种方式威胁用户支付一定的赎金来解锁。接下来我们通过一个示例，来聊聊锁机软件到底是通过哪些方式进入我们的生活中的。

## 分析

### 1\. 取证样本与环境

样本: 被恶意修改的文件管理APK，以下称MT.APK 通过MT_APK下载的恶意锁屏APK，以下简称S.APK 反编译软件: jadx
测试环境:夜神模拟器 Android 5 APK加壳：百度加固

样本信息如下： 文件名称 :MT.apk

文件大小 :7493493 byte

MD5:8754a0151875fd5b01d5d1e7a8eeace2

SHA1:2d7942dd7e135144fa5703f1dfbf70ee857c5a98

文件名称 :S.apk

文件大小 :29519 byte

MD5:05dbdc18e51dd72ae7ccda76406316d3

SHA1:d690fdafc37794f64719a19fd47e21e375574a92

### 2\. 取证样本测试

首先，在测试环境中安装MT.APK，从表面来看，这个锁机软件是依附在MT管理器中的，这是由于MT管理器的特殊性导致的。
因为MT管理器是一个比较方便的文件管理工具和逆向修改工具，既可以当做文件管理器使用，又可以以此来修改替换APK中的资源文件等，甚至可以去除签名，修改应用布局等。
所以如果我们下载了一些包含锁机软件的游戏破解神器，刚好这些锁机软件依附在MT管理器，同时再获取了用户的系统授权，那么用户就会在没有防备的情况下中招了。

![](https://image.3001.net/images/20201110/1604995177_5faa4869c293855b328d3.png!small)

首先，我们正常打开MT.APP，发现其开始请求获取系统超级管理员权限

![](https://image.3001.net/images/20201110/1604995194_5faa487a3774eb05a0695.png!small)

允许其申请的权限后，模拟器环境迅速卡顿并自动重启，然后出现下图中的锁屏界面，且除此之外不能进行其他的操作。![](https://image.3001.net/images/20201110/1604995207_5faa48874e4feeb987120.png!small)由于我们是直接在模拟器上进行的，且可以直接对它进行逆向分析，所以上图的解锁QQ群也没什么必要加。

### 3\. 锁屏流程分析

  * 启动MT.APP时，该恶意APK会向用户申请超级用户访问权限，并在后台向open.bmob.cn（云端代码托管平台）发送请求包。![](https://image.3001.net/images/20201110/1604995219_5faa4893ea153424a11b2.png!small)![](https://image.3001.net/images/20201110/1604995228_5faa489cddc043645df15.png!small)

  * 当用户允许了该恶意APK请求超级用户访问权限的请求时，该APK就会通过调用在云端托管的代码访问<http://fantasy-1259727437.cos.ap-chengdu.myqcloud.com/fantasyH.apk>下载恶意锁屏APK- S.apk

![](https://image.3001.net/images/20201110/1604995243_5faa48ab4fe64edca580e.png!small)

  * 以上请求会在系统后台下载并安装S.APK，S.APK会释放一个无图标的安装程序APK到系统应用路径里，并会在系统后台自动运行安装，S.APK成功安装后，会使手机迅速重启，最终导致手机被恶意锁屏![](https://image.3001.net/images/20201110/1604995256_5faa48b8a7085c01c37fc.png!small)下面我们来反编译下载回来的APK文件

### 4\. 反编译APK

![](https://image.3001.net/images/20201110/1604995269_5faa48c5887b3ebbd51a6.png!small)我们通常先从AndroidManifest入手，可以看到主入口为MainActivity，并且为隐藏的应用。
所以我们从MainActivity文件开始进行分析。![](https://image.3001.net/images/20201110/1604995283_5faa48d3c7552fe8c53e3.png!small)可以看到其中只是调用startService函数启动了“com.af.qq1689644519.Lock”这个service。下面我们继续看Lock这个service都做了哪些事情。![](https://image.3001.net/images/20201110/1604995298_5faa48e2357a7fd994e2d.png!small)从这段代码可以看出当应用的包名为“com.af.qq1689644519“时才启动锁屏。我们接着往下看，看到这里有一个frist()函数，那我们猜测可能不止一层锁屏。
“不止一层锁屏”指的是先通过转账等方式，从勒索者手里拿到解密秘钥后，会进入下一层勒索界面，然后对受害用户进行层层剥削。
所以我们还是继续往下看看吧![](https://image.3001.net/images/20201110/1604995309_5faa48ed6e25b2465baf0.png!small)从代码中可以看到最主要的逻辑在“AnonymousClass100000000”这个类中，![](https://image.3001.net/images/20201110/1604995401_5faa49491179bc821ad62.png!small)![](https://image.3001.net/images/20201110/1604995436_5faa496c760148b69d76f.png!small)  
获取界面输入框获取的值与PWD.get("Heart", this.val$mxlh))这个函数调用的结果进行比较，如果相等，则移除当前显示的view。
原来，当你以为结束了的时候，才发现，这只是个开始--我们还需要第二个密码才能进行解锁![](https://image.3001.net/images/20201110/1604995447_5faa4977e9b493a6a2118.png!small)下面我们继续看this.this$0.caonima();这个函数![](https://image.3001.net/images/20201110/1604995457_5faa49815e497ab364cce.png!small)发现和first()函数非常的像，有了前面的经验，我们直接看AnonymousClass100000001这个类![](https://image.3001.net/images/20201110/1604995465_5faa498939e0850cc4a9e.png!small)这也是直接获取根据输入的信息，调用三次Lock.get进行MD5。。。![](https://image.3001.net/images/20201110/1604995473_5faa4991af41679b49cdd.png!small)这直接起个线程去执行AnonymousClass100000000这个任务![](https://image.3001.net/images/20201110/1604995482_5faa499ac8b01b1343310.png!small)从上面代码发现有两种方式进行解锁，一种是联网情况进行解锁，另一种是本地解锁。
我们通过浏览器访问请求地址，发现返回的数据与本地的数据是相同的。但是他收取的费用却不同

![](https://image.3001.net/images/20201110/1604995502_5faa49ae3d878bd03a829.png!small)请求数据如下：![](https://image.3001.net/images/20201110/1604995524_5faa49c4a6a146ea2d6dd.png!small)然后调用shluder函数。![](https://image.3001.net/images/20201110/1604995534_5faa49ce486ce14a4a28a.png!small)这个函数的主要作用就是通过handler机制，将传递过来的字符串传递出去与前面三次MD5后的值进行比较。

![](https://image.3001.net/images/20201110/1604995631_5faa4a2f94f3584c620b1.png!small)

从这可以看到BroadcastReceiver.get(this)函数调用，下面我们来看下这个函数干了什么。

![](https://image.3001.net/images/20201110/1604995653_5faa4a450c818cacf0d59.png!small)

发现竟然直接是读取的文件名为“MODEL”的SharedPreference文件，从中获取unlock的值，如果在破解的角度出发可以直接修改这个值尝试绕过。
我们继续往下看第三次锁屏界面如下，

![](https://image.3001.net/images/20201110/1604995663_5faa4a4f881af093df69b.png!small)下面我们继续分析gu()这个函数

![](https://image.3001.net/images/20201110/1604995676_5faa4a5c71b934ff80f0e.png!small)

![](https://image.3001.net/images/20201110/1604995686_5faa4a66d8dd004a5f119.png!small)  
根据上面两层分析的经验可以看出来，在这一层中主要是以DES算法为主，将输入的数据进行两次加密，然后再做四次MD5后与"³∏io∨l²²‖∏³∏∏≠¤il0∩m¤mlo‖∩∨³‖p¹i"进行比较。相等就会进入下一层的锁机界面。

![](https://image.3001.net/images/20201110/1604995726_5faa4a8e3990cb0ff0174.png!small)

从界面上看到最后一层的界面，终于看到了希望，下面我们来看看代码。![](https://image.3001.net/images/20201110/1604995737_5faa4a9935ca27fb3b623.png!small)![](https://image.3001.net/images/20201110/1604995745_5faa4aa19341bf8e9df7f.png!small)这里可以看到又调用到了PWD的get函数，只是参数发生了变化。具体看下代码![](https://image.3001.net/images/20201110/1604995756_5faa4aac551bbf81ebd6a.png!small)![](https://image.3001.net/images/20201110/1604995765_5faa4ab56a241add9aab8.png!small)到此就是这款锁机软件的所有加解密逻辑了，除此之外，这其中还有个保活机制，依赖于宿主应用，如果感兴趣的可以分析下。

## 总结

锁机软件花样很多，有些比较“良心”的，等你交了钱之后会直接发你一个解密秘钥，当然也有一些没有底线的，正如文中所示，变着法的坑钱，甚至有更没有道德的作者，完全做一个随机的秘钥，打着收钱的名义干着坑人的活。
所以我们在平时下载软件，首先肯定要去正规的应用商店下载，其次一些所谓的破解软件、破解神器或者一些充满诱惑的软件都不要点击下载，才能从根本上防止遇到这些勒索软件。
而本文中的这款锁机软件，也有比较多的绕过方式，比如： 我们可以直接在宿主APP请求下载锁机APP的时候，将它Patch掉；
或者使用Hook插件将equals函数hook掉，判断如果参数为“com.af.qq1689644519“直接返回false，这样就可以直接绕过锁屏。

