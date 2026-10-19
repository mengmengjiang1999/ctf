## 写在前面的话

 **随着移动设备的快速发展，我们日常生活中的许多应用程序正在迁移到云部署，从JavaScript浏览器框架到支持移动设备的前端，例如Apple
iOS上的Objective-C，或基于Android的Java。这也促进了手机应用的发展，与Apple不同，Android市场是一种开放的方式，允许任何人为商店做出贡献，而且占据了移动市场份额的大部分。**

此外，还有各种第三方网站可以直接下载Android应用程序包文件（APK）。Metasploit允许测试人员使用meterpreter生成Android
payload，并且可以安装到Android设备上。Android应用程序是用Java编写的，它编译成称为DEX的Dalvik可执行格式。应用程序的编译版本是DEX字节码文件的ZIP文件。

Android上的Dalvik虚拟机最近被Android RunTime（ART）取代，后者增加了优化并将DEX字节码编译为本地汇编代码。Dalvik
VM主要执行大部分字节码的即时（JIT）解释。ART比Dalvik虚拟机具有更高的性能，Dalvik虚拟机仅优化应用程序的频繁执行部分的字节码部分。

Smali/baksmali是Android DEX字节码的汇编程序/反汇编程序。另一个名为“apktool”
的Android工具可以将压缩的DEX（APK文件）反汇编成smali文件，并将smali文件重新组合回DEX，然后再其重新组合为APK格式。我们可以使用此工具来反汇编和修改现有的APK文件。

接下来的文章中，我们可以使用该工具进行反汇编，并在初始Android
Activity的smali代码中添加一个额外的静态入口点，以启动我们的Meterpreter。总的来说，将Meterpreter嵌入一个APK文件的步骤如下：

1.在“apkmonk.com”或类似的镜像站点上查找现有的有趣APK应用程序。

2.生成Metasploit APK文件。

3.用“apktool”反汇编Metasploit APK文件，以及我们打算修改的APK文件。

4.将所有Meterpreter smali代码复制到新的APK smali目录。

5.通过查找具有以下行的intent-filter，在APK应用程序的AndroidManifest.xml文件中找到代码的入口点 ：`<action
android：name =“android.intent.action.MAIN”/>`包含此intent-filter的活动名称将是您要搜索的入口点。

6.修改`“.smali”`文件以包含启动Meterpreter阶段的代码。

7.将`Meterpreter
AndroidManifest.xml`中的所有Meterpreter权限复制到修改后的`APK的AndroidManifest.xml`中。

8.重新组装成DEX压缩格式。

9.使用`“jarsigner”`为新创建的APK文件签名，然后将其加载到目标Android设备上。接下来我会用一个具体的例子来解释下上述步骤，我从apkmonk.com下载了一个名为Cowboy
Shooting Game的游戏的APK文件。

![1.png](https://image.3001.net/images/20181106/1541474334_5be1081ee2f17.png!small)

## 生成恶意软件APK

然后，我使用“msfvenom”命令生成Metasploit APK，如下所示。

![2.png](https://image.3001.net/images/20181106/1541474343_5be1082729939.png!small)

## 反汇编APK文件

然后使用“apktool” 对这两个文件进行反汇编，如下所示：

![3.png](https://image.3001.net/images/20181106/1541474351_5be1082f0ebf0.png!small)

![4.png](https://image.3001.net/images/20181106/1541474357_5be1083532293.png!small)

## 将恶意软件代码复制到游戏中

一个简单的方法是将目录更改为Metasploit
APK目录，然后将“smali”目录下的所有文件复制到“com.CowboyShootingGames_2018-09-22”目录中。我从系统管理员那里学到的使用“tar”命令，你可以将tar的输出传输到第二个命令，该命令改变目录并“解压缩”生成的文件。

![5.png](https://image.3001.net/images/20181106/1541474364_5be1083c7210b.png!small)

## 找到Activity EntryPoint

下面我们可以看到输入活动被列为“com.CowboyShootingGames.MainActivity”。我们知道这一点，因为XML中包含一个带有“android.intent.action.MAIN”的intent-filter。

![6.png](https://image.3001.net/images/20181106/1541474371_5be10843a0520.png!small)

## 修改Activity EntryPoint Smali文件

从上面可以看出，在这种情况下，文件将被命名为“MainActivity.smali”，并且完全限定类路径中的`“com/CowboyShootingGames”
directory as per the periods (“.”)`目录中。

![7.png](https://image.3001.net/images/20181106/1541474378_5be1084a3a514.png!small)

在`“MainActivity.smali”`文件中，我们正在寻找`“onCreate（）”`方法。

![8.png](https://image.3001.net/images/20181106/1541474386_5be1085226c17.png!small)

我们需要在“onCreate（）”方法调用的正下方添加一行“smali”代码来调用我们的Meterpreter。`invoke-static {p0},
Lcom/metasploit/stage/Payload;->start(Landroid/content/Context;)V`请注意，上面是一行代码。使用与“payload”目录中包含的所有“smali”文件中的所有路径引用都必须修改，并更改目录名称本身。这可以手工完成，但容易出错。继续没有任何混淆片刻，修改后的最终结果将像下面的截图一样。

![9.png](https://image.3001.net/images/20181106/1541474393_5be10859eb770.png!small)

## 向修改的APK“AndroidManifest.xml”文件添加权限

下一步，使用“grep”搜索Metasploit“AndroidManfest.xml”文件中包含字符串“uses-permission”和“uses-feature”到修改后的APK的AndroidManiest.xml文件中.

![10.png](https://image.3001.net/images/20181106/1541474401_5be108615e784.png!small)

您需要使用编辑器在新的“AndroidManifest.xml”文件中的适当位置插入权限。搜索现有的“use-permission”行作为插入文本的位置的参考。

![11.png](https://image.3001.net/images/20181106/1541474408_5be10868338a7.png!small)

您最终可能会获得一些重复的权限。您可以选择删除它们，它没什么卵用。

## 构建新的APK包文件

现在 再次使用“apktool”
重新组合生成的APK包文件。最终结果将写入APK目录本身的“dist”目录中。![12.png](https://image.3001.net/images/20181106/1541474421_5be10875393d5.png!small)

## 重新签名生成的包文件

对于重新签名，一种简单的方法是使用安装Android studio时构建的Android调试密钥库。调试密钥库位于UN *
X系统上主目录中的“.android”隐藏目录中。

![13.png](https://image.3001.net/images/20181106/1541474429_5be1087d22079.png!small)

另一种方法是使用Java“keytool”生成您自己的自签名密钥库，并使用“jarsigner”工具对其进行签名，如下面的截图所示。

![14.png](https://image.3001.net/images/20181106/1541474436_5be1088479b0c.png!small)

![15.png](https://image.3001.net/images/20181106/1541474444_5be1088c1649b.png!small)

此时，“final.apk”文件已准备好了，可以使用“adb”安装到Android系统上。

![16.png](https://image.3001.net/images/20181106/1541474455_5be1089723bd0.png!small)

在演示中，我使用“GenyMotion”的虚拟机，这是一个基于x86的模拟器，它使用VirtualBox可以进行非常高性能的Android模拟。您可能会遇到的问题是x86仿真本身不支持ARM处理器。有一个解决方法，可以在线获得一些ARM翻译库。您需要搜索“
Genymotion-ARM-Translation_v1.1.zip ”，然后将ZIP文件拖到正在运行的GenyMotion
Android系统上。这不是100％可靠，并且仍可能导致一些应用程序崩溃。我发现Nexus
6系列设备非常适合，因为“rooting”套件相当可靠，并且通过USB电缆连接进行测试并不是太麻烦。

![17.png](https://image.3001.net/images/20181106/1541474462_5be1089ed0d28.png!small)

最后一步当然是尝试我们新感染的游戏。我们很快发现，在我们安装完游戏的那一刻，我们在KALI系统上获得了一个Meterpreter shell。

![18.png](https://image.3001.net/images/20181106/1541474489_5be108b9906e7.png!small)

![19.png](https://image.3001.net/images/20181106/1541474495_5be108bfb0b2e.png!small)

那么问题来了，在执行了上述所有必要步骤后。我发现出错的可能性非常高。所以我决定使用Python脚本来自动执行此过程。我称它为“android_embedit.py”，无需花费太多精力，就可以完成工作。

![20.png](https://image.3001.net/images/20181106/1541474506_5be108ca04ca4.png!small)

“android_embedit.py”的原理是，只要您提供Metasploit生成的APK文件，和要修改的原始APK和密钥库，它将以自动方式执行所有步骤并为您生成结果。以下是运行该工具的示例。所有临时文件和输出都将存储在“〜/
.ae”目录中。

![21.png](https://image.3001.net/images/20181106/1541474514_5be108d2374cd.png!small)

该工具还将删除“metasploit”目录名称，并自动使用随机字符串目录名称对其进行模糊处理。您可以在下面的截图中看到此结果，其中列出了APK“smali
/ com”目录的内容。名为“ dbarpubw ”的目录实际上包含Metasploitstager代码。

![22.png](https://image.3001.net/images/20181106/1541474521_5be108d9b7fe0.png!small)

我想你现在可能想玩了吧，你可以通过问<https://github.com/yoda66/AndroidEmbedIT>从我的github下载

***参考来源[blackhillsinfosec](a%20href=)，由周大涛编译，转载请注明来自FreeBuf.COM**

