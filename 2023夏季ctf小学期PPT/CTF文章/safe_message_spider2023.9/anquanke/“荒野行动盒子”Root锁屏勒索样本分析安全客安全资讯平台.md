# “荒野行动盒子”Root锁屏勒索样本分析

阅读量 **216825**

|评论 **8**

发布时间 : 2017-12-22 10:02:22

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t018a5509abcab01186.jpg)

作者：0xgg@四叶草

> 这是一篇非反病毒工程师的非专业分析，写完发现更像逆向教程，文中如果有疏漏，欢迎批评指正。

## 0x00 前言

最近在吾爱破解论坛病毒救援区看到一个锁机样本，说是root锁，虽然帖子好几天了但还没人分析，楼主应该线刷系统了，打算就以这个练练手吧。很久也没分析锁屏App了，之前有个王者荣耀辅助的样本，不过没root锁，想看看最近勒索App有什么新花样。话说，现在恶意软件都喜欢蹭热度，什么游戏流行就伪装什么外挂。

![](https://p4.ssl.qhimg.com/t01483d95c96cdbd3fb.png)

## 0x01 信息收集

先安装样本到模拟器里看看（模拟器万一搞坏了，大不了卸载重新安装），安装完成后会有一个“荒野行动盒子”的图标,运行后发现App申请Root权限，（很多外挂都需要Root权限，勒索软件以外挂为名倒是很容易让人放松警惕）:

![](https://p3.ssl.qhimg.com/t01ee31c9742f30a4de.png)

这里点击“永久记住选择“，然后点击”允许“，看看勒索软件搞什么鬼。发现这个勒索App还做了一个外挂界面：

![](https://p4.ssl.qhimg.com/dm/1024_576_/t0180366df258536893.png)

等一会模拟器自动重启了。重启完成后，发现如愿以偿，模拟器被锁了，锁屏界面如下（锁屏界面忒丑了）：

![](https://p4.ssl.qhimg.com/t01630ed031715e22a8.png)

随便输入“123456“，点击”解锁“发现没有反应，点击高亮的”解锁20元“，发现有提示：

![](https://p0.ssl.qhimg.com/t0121299c50871b108d.png)

意思是点100次就会解锁，这种都是调戏人的。要是可以免费解锁，那还怎么勒索那20块钱？

## 0x02 反编译分析

接下来祭出神器jadx反编译分析，反编译后发现资源里面的结构有点不一样：

![](https://p5.ssl.qhimg.com/t010ed8516e0d6be372.png)

正常情况下，apk反编译后应该是下面这种结构：

![](https://p2.ssl.qhimg.com/t01a3f0a07561ec0978.png)

原来res目录下的drawable、layout等资源全部被混淆了。打开r下的0文件发现其实就是编译后的layout文件：

![](https://p0.ssl.qhimg.com/t015f4298a84879ac75.png)

这个样本其实是使用了MT管理器的”RES资源混淆“功能。（MT管理器是一个可以在安卓手机上修改apk文件、反编译dex、修改smali、修改xml、重打包的App，功能很强大）。

代码的入口是MainActivity：

![](https://p2.ssl.qhimg.com/t01cf0c5038025202e4.png)

代码简洁的不得了，LogCatBroadcaster看着很眼熟吧，进去看看代码：

![](https://p2.ssl.qhimg.com/dm/1024_713_/t01c2c2f404e9cd1b5e.png)

这就是AIDE的特征（AIDE是一款可以在安卓手机上编写安卓App的开发工具，分析过勒索App的应该都很熟悉了） 。

再来看看e.busybox函数,发现代码混淆了，那还是使用JEB接着分析吧，分析完混淆函数，然后重命名一下，看着还不是很清楚：

![](https://p2.ssl.qhimg.com/dm/1024_138_/t01854dc4262fbba248.png)

尤其是下面一大堆的StringBuffer：

![](https://p1.ssl.qhimg.com/dm/1024_177_/t01ba05415881fbc63e.png)

先把函数拷贝出来，精简掉StringBuffer，代码清晰多了：

![](https://p1.ssl.qhimg.com/dm/1024_425_/t01009beeb17c267ce8.png)

这部分代码功能很清晰：复制libjiagu.so到App私有目录的a/k.bat文件中，再复制lib2jiagu.so到App私有目录的a/libStarEngine.so文件中，然后解密k.bat得到key.bat文件，再获取key.bat文件的包名保存到e.packageName中，这里可以看出来key.bat（即libjiagu.so文件）是一个apk文件。继续看下面代码：

![](https://p1.ssl.qhimg.com/t0153da00c9ccf073bd.png)

接着执行“ls data“命令，安卓App中要执行系统命令，必须申请root权限，代码执行到这里就需要申请root权限。不过这里执行这个命令没起到什么作用。

这里根据安卓系统版本分别进行处理，如果小于5.0，先把key.bat释放到/system/app/并改名为time.apk,然后释放libStarEngine.so到/system/lib/libStarEngine.so，
判断是否安装了com.example.xphuluxia,如果安装了就卸载，最后重启手机，安装激活勒索App。补充一下，com.example.xphuluxia是一个名为防锁侠的App，据说可以查杀锁屏勒索App，个人还没测试过。

继续看后面代码：

![](https://p2.ssl.qhimg.com/dm/1024_674_/t01268dc965ea25db62.png)

从大段重复代码可以看出作者很擅长CVM模式（ctrl+c、ctrl+v、modify）（个人猜想写病毒维护应该很少吧）。

这里需要用到e.packageName,我们先来获取一下包名,使用命令行获取一下模拟器的当前Activity即可：

![](https://p4.ssl.qhimg.com/t016d19f3065b4036f8.png)

即e.packageName=”com.hl.app”。现在来分析勒索App在5.0及其以上系统时的操作：释放key.bat到/system/priv-app/com.hl.app/并改名为com.hl.app.ap；释放libStarEngine.so到 /system/priv-app/com.hl.app/lib/arm/libStarEngine.so;重启手机，系统重启后会自动安装/system/priv-app/com.hl.app/com.hl.app.apk，激活勒索App。

分析到这里，现在清楚了，这是一个字母型的勒索App，母App任务应该完成了，可以通过Manifest.xml文件再确认一下：

![](https://p4.ssl.qhimg.com/dm/1024_191_/t017945020ca0144ea4.png)

这里没有申请任何权限，所以母App就是个壳，已经不需要继续分析了。

## 0x03分析子包

接下来分析真正的锁屏勒索子包代码，我的模拟器系统是4.4,使用adb先导出病毒文件到电脑：

![](https://p2.ssl.qhimg.com/t01d0c528ac1abaa7a1.png)

然后使用jadx反编译，这里同样是使用MT管理器做了资源混淆：

![](https://p3.ssl.qhimg.com/t016dce4a3461e7e87c.png)

查看AndroidManifest.xml，入口还是MainActivity:

![](https://p1.ssl.qhimg.com/t01943646053f5bc489.png)

LogCatBroadcaster就不用看了，还是AIDE的特征，没什么作用。主要是启动了com.hl.app.MyApp服务。继续看看这个服务代码：

![](https://p2.ssl.qhimg.com/t01d3a18302204017ac.png)

代码混淆了，那用JEB继续分析，先看看a类：

![](https://p5.ssl.qhimg.com/t01fd9767a02b994868.png)

很明显这是一个DES的加密解密算法类，所以a类被重命名为a_Cryptor。再看hx1:

![](https://p0.ssl.qhimg.com/t01878ed3ae79a86eec.png)

很明显，创建全屏的浮动窗口，遮挡其他App导致无法操作，达到锁屏效果。那么重命名为hx1_showLockView1，重命名变量、函数名称后，添加注释代码如下：

![](https://p5.ssl.qhimg.com/t01e759f77be46d6926.png)

这里初始化了加密密钥，然后创建了全屏浮动窗口达到锁屏效果，继续看代码：

![](https://p0.ssl.qhimg.com/dm/1024_367_/t01d3365e3400dbc064.png)

这里更新了a_crypt的密钥，然后生成随机数保存在lock1xlh中，设置点击响应函数，其中100000000是假的，骗人点100次的函数，最后的100000001才是真的解锁判断函数，继续看100000001的onClick代码：

![](https://p1.ssl.qhimg.com/dm/1024_347_/t01286f7dee1c1459dd.png)

Try代码块是一堆解密、转换代码，最后关键的是if语句，判断输入和随机码计算后的结果是不是相同，相同则进入第二层锁屏界面。所以，解锁密码就是这一堆代码计算后再与随机码计算的结果。这里b类代码被重命名为b_AES，set函数被重命名为set_replaceAndReverse。解密的代码就不用看了，我们写解密算法时直接copy过来用就行了，这时候就要发挥CVM模式(ctrl+c、ctrl+v、modify)的长处。

## 0x04解密第一层锁屏

接下来写计算第一层解密密码的算法，创建java工程，把100000001的onClick代码复制过来，中间需要依赖的类：
a_Cryptor、b_AES、c以及其他相关函数全部从JEB复制过来，修改错误后，把onClick函数改成getLockView1Pass，主要代码如下（记得前面有a_crypt更新密钥的相关代码，要复制过来）：

![](https://p2.ssl.qhimg.com/dm/1024_682_/t0167e05bd1422491c3.png)

lock1xlh就是锁屏界面上的随机码，运行后你就可以得到解锁密码了。我的随机码是477042，计算后得到解锁密码：1200556544，在模拟器中输入后，点击解锁，然后进入第二层锁屏，作者还是那么嚣张，界面依然奇丑无比：

![](https://p2.ssl.qhimg.com/t01d8868e59b2d3ab5b.png)

## 0x05分析第二层锁屏

接下来继续JEB分析第二层锁屏。查看hx2代码，这里改名为hx2_showLockView2:

![](https://p2.ssl.qhimg.com/dm/1024_167_/t0186213afca665dfc5.png)

还是一样的配方，随机码保存在lock2xlh中，创建全屏浮动窗口达到锁屏效果，解锁按钮点击响应函数是100000002，继续看代码：

![](https://p4.ssl.qhimg.com/dm/1024_200_/t0198a5c560b29a727c.png)

代码有点乱，拷贝出来精简一下：

![](https://p0.ssl.qhimg.com/dm/1024_381_/t01bbbfd802ec4cf3a7.png)

注释都写清楚了，关键是理解最后代码，输入的解锁码v2前3位经过sha、md5之后就应该等于“9fd09fe7fd77ab118ef78795668bc8a1”，后9位等于随机码经过md5、sha之后保留数字位的前9位。下面就可以写代码计算了。

## 0x06解密第二层锁屏

由于解锁码都是数字，前3位经过sha、md5之后就应该等于“9fd09fe7fd77ab118ef78795668bc8a1”，这个可以写代码爆破。算法很简单，如下所示：

![](https://p2.ssl.qhimg.com/t01945152d6b48ec5f6.png)

lock2xlh就是第二层锁屏界面上的随机码，运行后你就可以得到解锁密码了。我的随机码是498691，计算后得到解锁密码：187360012293，在模拟器中输入后，点击解锁，锁屏终于解除了。

之前还有个libStarEngine.so，在app代码中并没有发现加载该库文件的代码，IDA查看也没有发现什么，经过搜索发现是一个3d引擎，在这里也没有什么实际作用。

到这里，锁屏App已经分析完了。

## 0x07总结

结合之前分析，总结一下：

  1. 这是一个子母型的勒索App，母App主要完成解密、释放子病毒文件。病毒文件在0以下系统是/system/app/time.apk、 /system/lib/libStarEngine.so；5.0及其以上系统是/system/priv-app/com.hl.app/com.hl.app.apk 、/system/priv-app/com.hl.app/lib/arm/libStarEngine.so。
  2. 子病毒文件被加密后放在母App中，主要目的应该是绕过杀毒软件检测,效果如何见后文。
  3. 子病毒文件被释放到系统App目录中，系统双清是无法删除病毒文件的。
  4. 如果手机没有root，或者没有给勒索App授予root权限，那么是不会受影响的，只要卸载该“荒野行动盒子”即可。
  5. 病毒代码中虽然写了很多加密算法：AES、DES、md5、sha及字符替换等等，但还是很容易写出解密算法的。
  6. 另外，这个样本中可以看到使用了AIDE、MT管理器，这两个工具可以完成病毒App的开发、修改，也就是说，你只要有个安卓手机，就可以完成病毒的制作、修改过程，可以不用PC来完成，这个变化是值得注意和警惕的。

这里我简单写了一个计算解锁码的程序，需要java环境支持，用法很简单：

java -jar unlock_hyhz.jar,然后按照提示输入屏幕解锁码即可，执行效果如下图所示：

![](https://p0.ssl.qhimg.com/t0172e8a09f4ae41c01.png)

下载地址：<https://share.weiyun.com/46ffd85b4467fa564819262cbe32df5a>

Hash校验：

CRC32: 346A9DCB

MD5: 6BC24E74AA3C80FE2C85F0ADD84F5772

SHA-1: E0D693064D2A4350A4FC4B4B700F891420ED446C

## 0x08清除

分析完了该清除文件了。启用USB调试, 执行adb shell进入shell环境。

5.0以下系统执行：

![](https://p3.ssl.qhimg.com/t012674ffe05f3fdb36.png)

5.0及以上系统执行：

![](https://p5.ssl.qhimg.com/t01afb235e306bc2855.png)

最后所有系统上需要卸载母包：

![](https://p0.ssl.qhimg.com/t0121602466b3db6096.png)

## 0x09测试一下杀毒软件

最后把样本上传到virustotal.com上看了一下，有17款杀毒软件检测出来问题：

![](https://p4.ssl.qhimg.com/dm/1024_510_/t018148ec5e8c6a2a81.png)

<https://www.virustotal.com/#/file/bf3637f7ed48732404eaaf74abc6eca0a628def264a20d86fa044db04b6abce4/detection>

如果把子包直接放上去再看看，检测率还降低了：

![](https://p1.ssl.qhimg.com/dm/1024_420_/t01906c08cadebde864.png)

<https://www.virustotal.com/#/file/f426e208bbb8ed720d0200b28d1969c8eeb0ebaf841e63f8258d4c3fc428af88/detection>

总体感觉，这个检测率还是偏低的。这个检测结果可能也无法代表安卓手机端的检测率。

## 0x010 后记

个人感觉，自从5月份
wannacry爆发之后，不管是PC还是安卓系统，国内勒索病毒也越来越多了。而且现在安卓手机端的病毒可以使用安卓手机App开发、修改，那么分发、传播起来会更快，变种也会更多，这些都是PC上病毒没有的特点,需要引起重视。

最后，对于普通用户来说，防范措施非常简单，只要保持良好的使用习惯即可避免被锁屏勒索：

  1. 不要root手机！（除非你非常懂安全，即使被锁也能自己搞定）
  2. 不要下载、安装来历不明的App！
  3. 安装一个杀毒软件。

最重要的还是前两个习惯，因为“安全问题很多时候都是人的问题”。

## 0x011 附录

样本来源：<https://www.52pojie.cn/thread-672111-1-1.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **四叶草安全** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/91827](/post/id/91827)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安卓](/tag/安卓)
  * [勒索软件](/tag/勒索软件)
  * [移动安全](/tag/移动安全)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t01f34e4a309a455a3e.jpg) 四叶草安全

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

