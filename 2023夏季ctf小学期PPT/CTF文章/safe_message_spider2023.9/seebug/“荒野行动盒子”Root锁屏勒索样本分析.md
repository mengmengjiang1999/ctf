作者： [0xgg@CloverSec实验室](http://mp.weixin.qq.com/s/HPfHMdxmZJoYdwzCeVLDFw
"0xgg@CloverSec实验室")

这是一篇非反病毒工程师的非专业分析，写完发现更像逆向教程，文中如果有疏漏，欢迎批评指正。

#### 0x00 前言

最近在吾爱破解论坛病毒救援区看到一个锁机样本，说是root锁，虽然帖子好几天了但还没人分析，楼主应该线刷系统了，打算就以这个练练手吧。很久也没分析锁屏App了，之前有个王者荣耀辅助的样本，不过没root锁，想看看最近勒索App有什么新花样。话说，现在恶意软件都喜欢蹭热度，什么游戏流行就伪装什么外挂。

![](https://images.seebug.org/content/images/2017/12/85d1b0c6-cd45-46de-853c-ec36b1f49ee7.jpg-w331s)

#### 0x01 信息收集

先安装样本到模拟器里看看（模拟器万一搞坏了，大不了卸载重新安装），安装完成后会有一个“荒野行动盒子”的图标,运行后发现App申请Root权限，（很多外挂都需要Root权限，勒索软件以外挂为名倒是很容易让人放松警惕）:

![](https://images.seebug.org/content/images/2017/12/16d08e5a-e786-42a6-9252-bf3351da3bfc.jpg-w331s)

这里点击“永久记住选择“，然后点击”允许“，看看勒索软件搞什么鬼。发现这个勒索App还做了一个外挂界面：

![](https://images.seebug.org/content/images/2017/12/0682b52d-f1a8-4380-9ebe-ff354d6a0d2c.jpg-w331s)

等一会模拟器自动重启了。重启完成后，发现如愿以偿，模拟器被锁了，锁屏界面如下（锁屏界面忒丑了）：

![](https://images.seebug.org/content/images/2017/12/81327ebb-e9ea-4c3b-a73b-f1f823b806cd.jpg-w331s)

随便输入“123456“，点击”解锁“发现没有反应，点击高亮的”解锁20元“，发现有提示：

![](https://images.seebug.org/content/images/2017/12/a1075747-fa19-4d6f-bf96-ecd72093c415.jpg-w331s)

意思是点100次就会解锁，这种都是调戏人的。要是可以免费解锁，那还怎么勒索那20块钱？

#### 0x02 反编译分析

接下来祭出神器jadx反编译分析，反编译后发现资源里面的结构有点不一样：

![](https://images.seebug.org/content/images/2017/12/6e6d0bff-b0df-4ebd-86c2-c18acd40097d.jpg-w331s)

正常情况下，apk反编译后应该是下面这种结构：

![](https://images.seebug.org/content/images/2017/12/339c94a5-5ff2-48d8-bbf5-024359ae9100.jpg-w331s)

原来res目录下的drawable、layout等资源全部被混淆了。打开r下的0文件发现其实就是编译后的layout文件：

![](https://images.seebug.org/content/images/2017/12/29f0b729-a87c-41dc-860b-052aa924dd5a.jpg-w331s)

这个样本其实是使用了MT管理器的”RES资源混淆“功能。（MT管理器是一个可以在安卓手机上修改apk文件、反编译dex、修改smali、修改xml、重打包的App，功能很强大）。

代码的入口是MainActivity：

![](https://images.seebug.org/content/images/2017/12/b466cb81-d90f-4810-9497-3c8907e146ea.jpg-w331s)

代码简洁的不得了，LogCatBroadcaster看着很眼熟吧，进去看看代码：

![](https://images.seebug.org/content/images/2017/12/3eb00dc5-7ca0-48f7-8e52-69ba2df0ad7f.jpg-w331s)

这就是AIDE的特征（AIDE是一款可以在安卓手机上编写安卓App的开发工具，分析过勒索App的应该都很熟悉了） 。

再来看看e.busybox函数,发现代码混淆了，那还是使用JEB接着分析吧，分析完混淆函数，然后重命名一下，看着还不是很清楚：

![](https://images.seebug.org/content/images/2017/12/8ddc71b9-8edf-4765-9756-40220c663b5f.jpg-w331s)

尤其是下面一大堆的StringBuffer：

![](https://images.seebug.org/content/images/2017/12/4d559ac6-c79b-4afe-9e24-7ec6f2102c55.jpg-w331s)

先把函数拷贝出来，精简掉StringBuffer，代码清晰多了：

![](https://images.seebug.org/content/images/2017/12/ae033efc-d809-4363-8d40-f786decd5cac.jpg-w331s)

这部分代码功能很清晰：复制`libjiagu.so`到App私有目录的a/k.bat文件中，再复制`lib2jiagu.so`到App私有目录的`a/libStarEngine.so`文件中，然后解密k.bat得到key.bat文件，再获取key.bat文件的包名保存到`e.packageName`中，这里可以看出来key.bat（即libjiagu.so文件）是一个apk文件。继续看下面代码：

![](https://images.seebug.org/content/images/2017/12/5e156058-0762-418d-8da1-73ddf4d25ca7.jpg-w331s)

接着执行“ls data“命令，安卓App中要执行系统命令，必须申请root权限，代码执行到这里就需要申请root权限。不过这里执行这个命令没起到什么作用。

这里根据安卓系统版本分别进行处理，如果小于5.0，先把key.bat释放到`/system/app/`并改名为time.apk,然后释放`libStarEngine.so`到`/system/lib/libStarEngine.so`，
判断是否安装了`com.example.xphuluxia`,如果安装了就卸载，最后重启手机，安装激活勒索App。补充一下，`com.example.xphuluxia`是一个名为防锁侠的App，据说可以查杀锁屏勒索App，个人还没测试过。

继续看后面代码：

![](https://images.seebug.org/content/images/2017/12/80be0812-e8cc-4f00-b2ef-9e09294de80e.jpg-w331s)

从大段重复代码可以看出作者很擅长CVM模式（ctrl+c、ctrl+v、modify）（个人猜想写病毒维护应该很少吧）。

这里需要用到e.packageName,我们先来获取一下包名,使用命令行获取一下模拟器的当前Activity即可：

![](https://images.seebug.org/content/images/2017/12/1ded604a-63b7-4c3f-94a2-84dc50589794.jpg-w331s)

即e.packageName=”com.hl.app”。现在来分析勒索App在5.0及其以上系统时的操作：释放key.bat到/system/priv-app/com.hl.app/并改名为com.hl.app.ap；释放libStarEngine.so到 /system/priv-app/com.hl.app/lib/arm/libStarEngine.so;重启手机，系统重启后会自动安装/system/priv-app/com.hl.app/com.hl.app.apk，激活勒索App。

分析到这里，现在清楚了，这是一个字母型的勒索App，母App任务应该完成了，可以通过Manifest.xml文件再确认一下：

![](https://images.seebug.org/content/images/2017/12/5d38a430-0809-413e-8492-dbfc1a7c5a80.jpg-w331s)

这里没有申请任何权限，所以母App就是个壳，已经不需要继续分析了。

#### 0x03分析子包

接下来分析真正的锁屏勒索子包代码，我的模拟器系统是4.4,使用adb先导出病毒文件到电脑：

![](https://images.seebug.org/content/images/2017/12/a98ec816-3ede-49b9-b3b3-3c4f78fb4bab.jpg-w331s)

然后使用jadx反编译，这里同样是使用MT管理器做了资源混淆：

![](https://images.seebug.org/content/images/2017/12/fe40e864-ad02-4c9a-ab05-b586f3c0eb47.jpg-w331s)

查看AndroidManifest.xml，入口还是MainActivity：

![](https://images.seebug.org/content/images/2017/12/bb627fec-9f3f-4e58-8300-b4f7bb5e602a.jpg-w331s)

LogCatBroadcaster就不用看了，还是AIDE的特征，没什么作用。主要是启动了com.hl.app.MyApp服务。继续看看这个服务代码：

![](https://images.seebug.org/content/images/2017/12/3a593110-eb68-439e-a6ae-91de0af11844.jpg-w331s)

代码混淆了，那用JEB继续分析，先看看a类：

![](https://images.seebug.org/content/images/2017/12/77df1023-d450-44cb-a5f6-872ab8c143bb.jpg-w331s)

很明显这是一个DES的加密解密算法类，所以a类被重命名为a_Cryptor。再看hx1：

![](https://images.seebug.org/content/images/2017/12/a98b0c56-b2d2-41ac-819e-47f709b564cd.jpg-w331s)

很明显，创建全屏的浮动窗口，遮挡其他App导致无法操作，达到锁屏效果。那么重命名为hx1_showLockView1，重命名变量、函数名称后，添加注释代码如下：

![](https://images.seebug.org/content/images/2017/12/56a5c942-ed3b-44b3-bb4f-7a38fdb1e5f1.jpg-w331s)

这里初始化了加密密钥，然后创建了全屏浮动窗口达到锁屏效果，继续看代码：

![](https://images.seebug.org/content/images/2017/12/76bb4cd9-04a5-4009-bd9a-a18206f5ad76.jpg-w331s)

这里更新了a_crypt的密钥，然后生成随机数保存在lock1xlh中，设置点击响应函数，其中100000000是假的，骗人点100次的函数，最后的100000001才是真的解锁判断函数，继续看100000001的onClick代码：

![](https://images.seebug.org/content/images/2017/12/5936e439-d4b1-44c0-bb32-89b09754c392.jpg-w331s)

Try代码块是一堆解密、转换代码，最后关键的是if语句，判断输入和随机码计算后的结果是不是相同，相同则进入第二层锁屏界面。所以，解锁密码就是这一堆代码计算后再与随机码计算的结果。这里b类代码被重命名为b_AES，set函数被重命名为set_replaceAndReverse。解密的代码就不用看了，我们写解密算法时直接copy过来用就行了，这时候就要发挥CVM模式(ctrl+c、ctrl+v、modify)的长处。

#### 0x04解密第一层锁屏

接下来写计算第一层解密密码的算法，创建java工程，把100000001的onClick代码复制过来，中间需要依赖的类：
a_Cryptor、b_AES、c以及其他相关函数全部从JEB复制过来，修改错误后，把onClick函数改成getLockView1Pass，主要代码如下（记得前面有a_crypt更新密钥的相关代码，要复制过来）：

![](https://images.seebug.org/content/images/2017/12/03b0ce87-ec85-44aa-b1c5-d22b0f23f32f.jpg-w331s)

lock1xlh就是锁屏界面上的随机码，运行后你就可以得到解锁密码了。我的随机码是477042，计算后得到解锁密码：1200556544，在模拟器中输入后，点击解锁，然后进入第二层锁屏，作者还是那么嚣张，界面依然奇丑无比：

![](https://images.seebug.org/content/images/2017/12/65c23223-1822-4784-8902-76314291a605.jpg-w331s)

#### 0x05分析第二层锁屏

接下来继续JEB分析第二层锁屏。查看hx2代码，这里改名为hx2_showLockView2：

![](https://images.seebug.org/content/images/2017/12/8e01857c-58f4-4d9d-ae7e-7e475786cb2c.jpg-w331s)

还是一样的配方，随机码保存在lock2xlh中，创建全屏浮动窗口达到锁屏效果，解锁按钮点击响应函数是100000002，继续看代码：

![](https://images.seebug.org/content/images/2017/12/5ee1386a-0a11-4d8c-a761-7e80d904e428.jpg-w331s)

代码有点乱，拷贝出来精简一下：

![](https://images.seebug.org/content/images/2017/12/65226288-844f-40d0-8336-d496bc837227.jpg-w331s)

注释都写清楚了，关键是理解最后代码，输入的解锁码v2前3位经过sha、md5之后就应该等于“9fd09fe7fd77ab118ef78795668bc8a1”，后9位等于随机码经过md5、sha之后保留数字位的前9位。下面就可以写代码计算了。

#### 0x06 解密第二层锁屏

由于解锁码都是数字，前3位经过sha、md5之后就应该等于“9fd09fe7fd77ab118ef78795668bc8a1”，这个可以写代码爆破。算法很简单，如下所示：

![](https://images.seebug.org/content/images/2017/12/b0b1b4f3-e7a1-4e1a-a3de-d4b453f94369.jpg-w331s)

lock2xlh就是第二层锁屏界面上的随机码，运行后你就可以得到解锁密码了。我的随机码是498691，计算后得到解锁密码：187360012293，在模拟器中输入后，点击解锁，锁屏终于解除了。

之前还有个`libStarEngine.so`，在app代码中并没有发现加载该库文件的代码，IDA查看也没有发现什么，经过搜索发现是一个3d引擎，在这里也没有什么实际作用。

到这里，锁屏App已经分析完了。

#### 0x07 总结

结合之前分析，总结一下：

  1. 这是一个子母型的勒索App，母App主要完成解密、释放子病毒文件。病毒文件在5.0以下系统是`/system/app/time.apk`、 `/system/lib/libStarEngine.so`；5.0及其以上系统是`/system/priv-app/com.hl.app/com.hl.app.apk` 、`/system/priv-app/com.hl.app/lib/arm/libStarEngine.so`。
  2. 子病毒文件被加密后放在母App中，主要目的应该是绕过杀毒软件检测,效果如何见后文。
  3. 子病毒文件被释放到系统App目录中，系统双清是无法删除病毒文件的。
  4. 如果手机没有root，或者没有给勒索App授予root权限，那么是不会受影响的，只要卸载该“荒野行动盒子”即可。
  5. 病毒代码中虽然写了很多加密算法：AES、DES、md5、sha及字符替换等等，但还是很容易写出解密算法的。
  6. 另外，这个样本中可以看到使用了AIDE、MT管理器，这两个工具可以完成病毒App的开发、修改，也就是说，你只要有个安卓手机，就可以完成病毒的制作、修改过程，可以不用PC来完成，这个变化是值得注意和警惕的。

这里我简单写了一个计算解锁码的程序，需要java环境支持，用法很简单：

java -jar unlock_hyhz.jar,然后按照提示输入屏幕解锁码即可，执行效果如下图所示：

![](https://images.seebug.org/content/images/2017/12/856a463d-6787-4290-a43f-1f8049248fb5.jpg-w331s)

下载地址：<https://share.weiyun.com/46ffd85b4467fa564819262cbe32df5a>

Hash校验：CRC32: 346A9DCB

MD5: 6BC24E74AA3C80FE2C85F0ADD84F5772

SHA-1: E0D693064D2A4350A4FC4B4B700F891420ED446C

![](https://images.seebug.org/content/images/2017/12/87118c83-673d-4ef8-8eaf-ee57dbad0aff.jpg-w331s)

5.0及以上系统执行：

![](https://images.seebug.org/content/images/2017/12/d5105455-5f12-4082-9ed3-05ea1dc9705c.jpg-w331s)

最后所有系统上需要卸载母包：

![](https://images.seebug.org/content/images/2017/12/60659546-4773-4a16-8419-c3383bcc9a1b.jpg-w331s)

#### 0x09 测试一下杀毒软件

最后把样本上传到virustotal.com上看了一下，有17款杀毒软件检测出来问题：

![](https://images.seebug.org/content/images/2017/12/4607ac39-ebaa-497e-b0a0-2bc549ffbb17.jpg-w331s)

国产的阿里、360、腾讯、瑞星都可以检测出来。附[链接](https://www.virustotal.com/#/file/bf3637f7ed48732404eaaf74abc6eca0a628def264a20d86fa044db04b6abce4/detection
"链接")。

如果把子包直接放上去再看看，检测率还降低了：

![](https://images.seebug.org/content/images/2017/12/02e328fd-ba84-4443-83b3-bca12e4231a9.jpg-w331s)

我也是醉了，不知道国外那几个是怎么检测的，不过国产的阿里、360、腾讯、瑞星还是可以检测出来的，附[链接](https://www.virustotal.com/#/file/f426e208bbb8ed720d0200b28d1969c8eeb0ebaf841e63f8258d4c3fc428af88/detection
"链接")。

总体感觉，这个检测率还是偏低的。这个检测结果可能也无法代表安卓手机端的检测率。

#### 0x010 后记

个人感觉，自从5月份
wannacry爆发之后，不管是PC还是安卓系统，国内勒索病毒也越来越多了。而且现在安卓手机端的病毒可以使用安卓手机App开发、修改，那么分发、传播起来会更快，变种也会更多，这些都是PC上病毒没有的特点,需要引起重视。

最后，对于普通用户来说，防范措施非常简单，只要保持良好的使用习惯即可避免被锁屏勒索：

  1. 不要root手机！（除非你非常懂安全，即使被锁也能自己搞定）
  2. 不要下载、安装来历不明的App！
  3. 安装一个杀毒软件。

最重要的还是前两个习惯，因为“安全问题很多时候都是人的问题”。

#### 0x011 附录

样本来源：<https://www.52pojie.cn/thread-672111-1-1.html>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/486/>

