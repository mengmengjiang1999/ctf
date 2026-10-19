## 前言

在渗透测试工作中，渗透测试人员会被授权地去测试互联网的所有业务，换言之只要业务上云就有存在的安全风险，因此得到一个词语
—`万物皆可渗透`，于是当我遇到被授权去测试Android
APP项目的时候，我尝试使用过国内的各大公司的安卓模拟器，例如某神、某遥、某讯手游模拟器、某Mu等等，感觉这些模拟器上手体验并不友好，因为安卓系统本身也是需要处理器和内存的支持才能运行的，电脑运行模拟器的时候除了电脑正常运行时候使用处理器和内存外还要分一部分CPU的使用率和内存大小给安卓模拟器，所以电脑运行起来就会更吃力，但是我们渗透测试人员使用安卓模拟器主要是为了在一个安卓环境来对客户提供的APK进行渗透而已，占用的资源也不会太大，因此我就选择Android
Studio 的 Android Virtual Devices

>
> 注:在一年前我尝试使用过它来进行测试使用，发现当时不管是在模拟器里面的应用中心还是从电脑拖APK进去安装互联网的任何APK，两者都是无法安装的。而目前我已经得到了解决这个问题的方式，下面我会附上一条文章的链接。  
> https://juejin.cn/post/6844904000408518663

## 探索Android Studio

Android Studio 是用于开发 Android 应用的官方集成开发环境 (IDE)，以[IntelliJ
IDEA](https://www.jetbrains.com/idea/)为基础构建而成。除了 IntelliJ
强大的代码编辑器和开发者工具，Android Studio 还提供更多可提高 Android 应用构建效率的功能，例如：

  * 基于 Gradle 的灵活构建系统

  * 快速且功能丰富的模拟器

  * 统一的环境（供您开发适用于所有 Android 设备的应用）

  * Apply Changes 功能可将代码和资源更改推送到正在运行的应用，而无需重启应用

  * 代码模板和 GitHub 集成，可协助您打造常见的应用功能及导入示例代码

  * 大量的测试工具和框架

  * Lint 工具，能够找出性能、易用性和版本兼容性等方面的问题

  * C++ 和 NDK 支持

  * 内置对[Google Cloud Platform](https://cloud.google.com/tools/android-studio/docs/?hl=zh-cn)的支持，可轻松集成 Google Cloud Messaging 和 App Engine

简单的搬了官方部分文档内容来让大家快速了解Android Studio这款强大的软件

## 在 Android 模拟器上运行应用（Android Virtual Devices）

  * Android 模拟器可在您的计算机上模拟 Android 设备，这样您就可以在各种设备上以及各个 Android API 级别测试您的应用，而无需拥有每个实体设备。

  * 模拟器几乎可以提供真正的 Android 设备所具备的所有功能。 您可以模拟来电和短信、指定设备的位置、模拟不同的网速、模拟旋转及其他硬件传感器、访问 Google Play 商店，等等。

  * 从某些方面来看，在模拟器上测试应用比在实体设备上测试要更快、更容易。例如，将数据传输到模拟器的速度比传输到通过 USB 连接的设备更快。

  * 模拟器随附了针对各种 Android 手机、平板电脑、Wear OS 和 Android TV 设备的预定义配置。

在文章后部分我会写Android Virtual Devices 配置的教程，但是这里我就先不详细写一个如何安装Android Studio +
Android Virtual Devices
配置的教程了，我这里附上一条网上的一个大佬写的一篇文章吧，虽然这个文章是在Mac环境的，其实在Windows里面安装也是差不多一样的，可以自行百度、Google

> https://blog.csdn.net/qq_38436214/article/details/106658550

## 解决在 Android Virtual Devices 的 Android 9.0 以上获得root权限并安装Magisk

#### 这里我列出我在网上找到了关于AVD Android 9.0以上不能直接获取root权限的部分原因的两篇文章

文章一：  
问题：

  * 在控制台输入adb shell 进入设备终端，然后输入su, 发现报su命令找不到的错误

  * 直接输入adb root，无反应，查看文件目录， 依然无权限  
分析问题：模拟器的问题，当然去找谷歌问问了,经过查询发现了这句话:  
![image](https://image.3001.net/images/20211104/1635990077_61833a3d466ca6c84a7cf.jpg!small)

中文翻译大意：这是个带Google Play商店的系统镜像，你可以安装app；但不能获取root权限，因为这是个生产版本而不是调试版本。  
这里有一个解决方案：  
`新建模拟器选择系统镜像的时候，会发现有的系统镜像Target会带有Google Play而有些不带Google
Play；因此我们只需要选择不带Google`

![image](https://image.3001.net/images/20211021/1634809042_617134d250225d42e5284.png!small)

这方法我尚未尝试过，因为在Mac版的Android Studio并没有这个Google Play，而在Windows版的Android
Studio是有的，如果有小伙伴是用Win的话也不妨尝试一下，看看是否能成功。

由于版权原因，我这里附上原作者的文章链接。

> https://zhuanlan.zhihu.com/p/148067746

文章二：

![image](https://image.3001.net/images/20211021/1634809485_6171368deba66efc374f3.png!small)

由于版权原因，我这里附上原作者的文章链接：

> http://www.soolco.com/post/50823_1_1.html

### 然后这里我使用另一个方式去获取AVD的ROOT

> 环境：Mac Android Studio 2020.3.1 + Java 8  
> 工具：https://github.com/newbit1/rootAVD

这里我演示选择Pixel 3 XL （都是可以自定义选择的）

![image](https://image.3001.net/images/20211021/1634810103_617138f73fb4111ed549f.png!small)  
点击下载镜像，这里我选择第一个API 30

![image](https://image.3001.net/images/20211021/1634810205_6171395d10dff5423929e.png!small)

这里下载完之后会显示一条镜像下载存储到计算机里面的路径目录，这里要复制一下，点击Finish返回系统镜像界面

![image](https://image.3001.net/images/20211021/1634810295_617139b7242ff97228c8c.png!small)

选择Next就可以进去修改模拟器的配置情况，这里可以自由发挥

![image](https://image.3001.net/images/20211021/1634810324_617139d4ec691c7104b2e.png!small)![image](https://image.3001.net/images/20211021/1634810342_617139e6d6407c0260fa3.png!small)

点击绿色按钮进行启动模拟器

![image](https://image.3001.net/images/20211021/1634810428_61713a3cd7a36fcb0d81d.png!small)

模拟器启动之后，打开终端窗口，用CD命令切换到开始在Github下载的那个工具解压的目录里 —
[rootAVD](https://github.com/newbit1/rootAVD)

这里注意一下，Mac电脑是不能运行Bat文件的，但是这个工具很人性化，提供了一个Shell脚本，而Mac是可以运行Shell脚本的，`这里的红色框是终端当前切换的目录位置`，至于Window用户的师傅们可以用Bat那个文件就可以了，`Shell脚本文件和bat文件功能是一样的`

> ./rootAVD.sh InstallApps

这个命令就是为了安装[rootAVD](https://github.com/newbit1/rootAVD)里面的`Magisk`工具，至于师傅们想去了解它，我这里附上一条链接

> https://sspai.com/post/53043/

![image](https://image.3001.net/images/20211021/1634819408_61715d5073bfaf9cec2b6.png!small)

出现这种情况，说明我电脑还没配置`adb`环境，于是这里写一下教程  
在终端切换到用户目录里面，输入以下两条命令，创建`.bash_profile`文件并编辑它

> touch .bash_profile  
> open -e .bash_profile

这里的export ANDROID_HOME=就是你的电脑安装安卓SDK的路径，注意`XXX`是随便写的一个用户名，师傅们要根据自己的实际情况来填

    
    
    export ANDROID_HOME=/Users/XXX/Downloads/Android/Android_SDK
    export PATH=${PATH}:${ANDROID_HOME}/tools
    export PATH=${PATH}:${ANDROID_HOME}/platform-tools
    

![image](https://image.3001.net/images/20211021/1634819519_61715dbf1c7f47db71689.png!small)

输入如下命令能使该配置文件立即生效，并输入`adb version`  
这时再次输入`adb`时没有出现提示adb: command not found就代表环境配置成功啦

> source .bash_profile

![image](https://image.3001.net/images/20211021/1634819759_61715eaf2e7f6811bad24.png!small)

然后可以直接把那个`Magisk.zip `改为`Magisk.apk`并把它拖进去直接安装，或者直接用命令直接安装就默认后缀名`zip`就可以了

> ./rootAVD.sh InstallApps

![image](https://image.3001.net/images/20211021/1634819837_61715efdcfb0cf7a938fb.png!small)看到有Success的字眼，就代表成功安装`Magisk
APK`，接下来就可以进行提权了，使用以下命令（小Tips：建议这里挂全局代理，速度会友好很多）

> ./rootAVD.sh /Users/XXX/Downloads/Android/Android_SDK/system-> images/android-30/google_apis/x86/ramdisk.img

注意`XXX`是随便写的一个用户名和`ramdisk.img`这个文件，师傅们要根据自己的实际情况来填

![image](https://image.3001.net/images/20211021/1634820048_61715fd08dbc316893a2b.png!small)

当出现下面有`Success`字眼，代表成功获得root权限了，但是这里有一个小细节，它成功`root`了之后，模拟器会自动关闭的，这里要手动重新启动一下就可以了

![image](https://image.3001.net/images/20211021/1634820094_61715ffec49dd55fc7eb2.png!small)

直接`su root`来一波，点击右边的那个`GRANT`按钮就直接进入root的用户

![image](https://image.3001.net/images/20211021/1634820137_61716029ad44634d2a11b.png!small)

如果师傅们出现了下面这种情况可以直接进去`Magisk APP`，点击这个盾牌标志进去开启root授权

![image](https://image.3001.net/images/20211021/1634820404_617161343f6926626b150.png!small)  
![image](https://image.3001.net/images/20211021/1634820425_617161497d7909ae68efa.png!small)  
![image](https://image.3001.net/images/20211021/1634820443_6171615bb6b711fff9d51.png!small)

如果师傅们想要在手机里面进入查看Root身份的文件夹里面的内容，可以去下载这个软件`Root Explorer`

`https://www.apkhere.com/app/com.speedsoftware.rootexplorer`

![image](https://image.3001.net/images/20211021/1634820494_6171618e356f9aa0b98db.png!small)  
![image](https://image.3001.net/images/20211021/1634820518_617161a6b5fba818b4bb2.png!small)

这里补充一下，`Magisk`这个强大软件有一些强大的模块，下面我附上两条链接，有兴趣研究一下的师傅们可以去玩一玩

> https://github.com/NVISOsecurity/MagiskTrustUserCerts  
> https://github.com/ViRb3/magisk-frida

## MobiHok RAT 工具的简单使用教程

#### 这里由于敏感原因，故不会放下载链接，请遵守国家网络安全法律，本人仅此在本地进行实验测试编写文章，请不要在互联网乱使用该工具，否则后果自负。

> 环境：MobiHok v6 + Java 8

1、 打开软件，会让你输入一个端口号，我这里以6666端口号来演示，密码那里可以不用填，默认就可以了，然后点击OK

![image](https://image.3001.net/images/20211021/1634820619_6171620be833c02e118c2.png!small)

2、点击红色箭头指向的那个安卓图标

![image](https://image.3001.net/images/20211021/1634820668_6171623c7f6f2275052b2.png!small)

3、这里输入当前攻击机的IP地址和开始运行该工具的端口号，并勾选右边的四个功能选项，最后点击`add
apk`按钮去添加一个正常的APK，这里我使用`root-explorer`这个APK来进行演示

![image](https://image.3001.net/images/20211021/1634820700_6171625ce0de8a88661de.png!small)

4、成功添加一个正常的APK

![image](https://image.3001.net/images/20211021/1634820726_61716276abc8a572b8756.png!small)

5、点击`Build`生成嵌套到正常APK里面的一个新木马的APK

![image](https://image.3001.net/images/20211021/1634820768_617162a052614d49a6918.png!small)

6、但是这里会有个小问题，就是在生成新的APK里面会出现上面红色框圈住的问题，这里提供一个解决办法，就是`C:\BuildingMH\apktool`目录下打开CMD（因为这里MobiHok我安装在C盘里面，师傅们可以根据自己的实际情况操作），把下图蓝色选中部分在cmd输入，这里要把`client.apk`前面写的目录删掉，直接写它就可以了，效果图如下图二

> java -jar C:\BuildingMH\apktool\SignApk.jar
> C:\BuildingMH\apktool\certificate.pem C:\BuildingMH\apktool\key.pk8
> C:\BuildingMH\apktool\app-release\dist\app-release.apk client.apk

![image](https://image.3001.net/images/20211021/1634820827_617162db3dfa12f1c7703.png!small)![image](https://image.3001.net/images/20211021/1634820847_617162ef36986267c3971.png!small)

7、这样就代表成功生成，就可以在Android Studio进行测试上线

![image](https://image.3001.net/images/20211021/1634820904_61716328d8de05d5e260a.png!small)

8、成功上线，下图二的红色框的那些操作就可以随便操作了

![image](https://image.3001.net/images/20211021/1634820928_617163403596c1c99e706.png!small)![image](https://image.3001.net/images/20211021/1634820961_61716361b947d4d86f24f.png!small)

## APK手机管家绕过

在真机测试的时候会遇到手机自带的安全管家进行查杀扫描，这里我提供一下网上找到的一个免杀工具链接，因为我本地环境有点问题，正在修复当中，至于该工具是否能成功进行免杀绕过，就由大家自行测试。

> https://github.com/chixiaome/520apkhook

#### 小Tips：

如果上面的那个工具运行不成功，建议使用Apk Easy
Tool进行手动编译，亲测能成功，这里附上一张图，我用本地的一个旧手机小米5S进行测试，安装之后点击打开，APK就会自动隐藏（能在进程看到是正在运行中）能正常上线的。

![image](https://image.3001.net/images/20211021/1634823097_61716bb94804814d6ea3b.png!small)

❗️❗️❗️法律免责声明：未经双方事先同意，使用此工具攻击目标是非法的。最终用户有责任遵守国家网络安全法。作者对本程序造成的任何误用或损坏不承担任何责任。

参考资料:  
https://developer.android.google.cn/studio/intro?hl=zh-cn  
https://developer.android.google.cn/studio/run/emulator?hl=zh-cn  
https://zhuanlan.zhihu.com/p/148067746  
https://www.jianshu.com/p/db3298ca0a32  
https://ti.qianxin.com/blog/articles/arab-trojan-successfully-localized-many-apps-were-mimicked-for-attack/  
https://blog.csdn.net/z895749744/article/details/113760751  
https://blog.csdn.net/u010164190/article/details/81012259

