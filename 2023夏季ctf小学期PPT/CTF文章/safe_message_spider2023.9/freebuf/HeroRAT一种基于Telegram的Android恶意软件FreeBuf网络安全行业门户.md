## 简介

 **在今年6月份，安全公司ESET的研究人员发现了一种名为Hero RAT的新型Android远程访问木马（RAT），它利用Telegram BOT
API与攻击者进行通信。**

Telegram API的使用可以被认为是Android RAT领域的一个新趋势，因为在HeroRAT之前，已经有其他一些使用Telegram
API的RAT家族在实际攻击活动中被发现，如Tele RAT和IR RAT。

Hero RAT在伊朗变现得尤为活跃，主要通过第三方应用程序商店上的受感染社交媒体和消息应用程序进行传播。

ESET的研究人员认为，Hero RAT可能借用了于2018年3月被发布在黑客论坛上的一个恶意软件的源代码。不过，它也具有一些区别于IR RAT和Tele
RAT的特性。其中一个特性是，它是使用Xamarin框架和TeleSharp库所开发的。

Hero RAT
的开发者在一个专用的Telegram频道上对其进行出售，并根据不同的功能配备提供了三个不同版本的变种：青铜版（25美元）、白银版（50美元）和黄金版（100美元）。另外，它的开发者还发布了一个演示视频，用于详细介绍这个RAT的功能。下面是一张该演示视频的截图，展示了三个变种之间的差异。

![l1.jpg](https://image.3001.net/images/20180806/1533527967_5b67c79f09340.jpg!small)

图1.三个变种之间的差异

## 样本分析

在这一章节中，我们将展示所有的样本。

### “63a22d065e16ac022910fe1cad6360ecc8539c0b.apk”

MD5：896ffa6cb6d7789662acedc3f9c024a0

SHA-1：63a22d065e16ac022910fe1cad6360ecc8539c0b

SHA-256：92edbf20549bad64202654bc51cc581f706a31bd8d877812b842d96406c835a1

文件大小：7.02 MB

包名：System.OS

图标：

![A1.jpg](https://image.3001.net/images/20180806/1533527977_5b67c7a98e856.jpg!small)

### “3605476181c935413436f0a1cd0e4ecaca72dc7d.apk”

MD5：0e6fdbdf1fb1e758d2352407d4dbf91e

SHA-1：3605476181c935413436f0a1cd0e4ecaca72dc7d

SHA-256：a002fca557e33559db6f1d5133325e372dd5689e44422297406e8337461e1548

文件大小：7.01 MB

包名：FreeInterNet.OS

图标：

![a2.jpg](https://image.3001.net/images/20180806/1533527989_5b67c7b57f65a.jpg!small)

### “a155e06cb4890e6d4f4802278f5408335395f39c.apk”

MD5：e16349e8bb8f76dcff973cb71e9ea59e

SHA-1：a155e06cb4890e6d4f4802278f5408335395f39c

SHA-256：3b40b5081c2326f70e44245db9986f7a2f07a04c9956d27b198b6fc0ae51b3a2

文件大小：9.49 MB

包名：Andro.OS

图标：

![A3.jpg](https://image.3001.net/images/20180806/1533528002_5b67c7c27ab31.jpg!small)

## 能够隐蔽运行的恶意软件

这三个变种实质上都是同一个RAT，只是使用了不同的包名、图标和僵尸主控机（botmaster）用户名来进行重新封装。因此，我们只需要深入分析其中一个样本即可。

首先，恶意应用会请求目标设备上的所有权限，如下图所示：

![l2.jpg](https://image.3001.net/images/20180806/1533528019_5b67c7d3a344e.jpg!small)

图2.RAT请求的权限

在安装完成之后，恶意应用将显示一条诸如“This application can’t run on your
device（此应用程序无法在你的设备上运行）”这样的消息，并显示一个虚假的卸载进程。

![l3.jpg](https://image.3001.net/images/20180806/1533528026_5b67c7dad337c.jpg!small)

图3. RAT假装正在卸载

在这个虚假的卸载进程结束之后，恶意应用的图标的确会从设备的主面板上移除，但RAT实质上会一直在后台处于活跃状态，那怕是设备进入工程模式，如下图所示。

![l4.jpg](https://image.3001.net/images/20180806/1533528037_5b67c7e57b4b9.jpg!small)

图4.在虚假的卸载进程结束后，RAT一直处于活跃状态

为了隐藏恶意应用的图标并让RAT隐蔽地运行，攻击者将方法“setcomponentenabledsettings”设置为了“Disabled”。不过，指定的参数却是“DontKillApp”，如下图所示：

![l5.jpg](https://image.3001.net/images/20180806/1533528047_5b67c7efcbb7c.jpg!small)

图5.用来隐藏恶意应用图标的代码

## 使用Xamarin编写的恶意软件

解包apk文件，我们注意到存在一个名为“assemblie”的文件夹，它包含了一些dll：

![l6.jpg](https://image.3001.net/images/20180806/1533528059_5b67c7fbdae67.jpg!small)
图6.使用Xamarin编写的DLL

这些库文件均是在Xamarin框架下编写的，该框架允许恶意软件开发者使用C#语言来开发Android应用程序。

在上面的列表中，我们可以看到Telesharp的存在。它是一个使用C#创建Telegram
bot的库，可以免费在GitHub上获取。它提供的一些RAT功能直接基于Telesharp API（如“发送位置”），因此编写Hero
RAT对于开发者来说特别简单。

![l7.jpg](https://image.3001.net/images/20180806/1533528072_5b67c8086076e.jpg!small)

图7.TeleSharp库

由于Xamarin框架的使用，所有使用特定工具提取的Java源代码文件实际上只包含经封装后的代码，而真实的代码则包含在“android.os.dll”中。通过使用一些专门为分析.NET可执行文件而设计的工具，我们可以轻松地反编译dll，以获得真实的源代码。

## Hero RAT的功能和特性

在探索源代码的过程中，我们发现Hero RAT具备典型RAT的所有功能。例如，读取SMS短信和调用日志，获取位置，关闭或打开、下载其他文件等：

![l8.jpg](https://image.3001.net/images/20180806/1533528090_5b67c81a14b54.jpg!small)

图8. Hero RAT的功能

Telegram bot的main token，被用作RAT的命令和控制（C2C），出现在一个类的源代码中：

![l9.jpg](https://image.3001.net/images/20180806/1533528100_5b67c824497ee.jpg!small)

图9.Telegram bot的main token

因此，我们可以通过查询Telegram REST API来获取bot的用户名，并尝试向它发送命令:

![l10.jpg](https://image.3001.net/images/20180806/1533528114_5b67c83288603.jpg!small)

图10.与bot相关的信息

![l11.jpg](https://image.3001.net/images/20180806/1533528132_5b67c84467372.jpg!small)

图11.尝试联系bot

不幸的是，bot并不会接受我们的命令，但回复了这样一条消息“You Cant Use Of Bot Before Register In This
Bot（在bot注册之前你不能使用这个bot）”。这条消息表明，bot只接受来自特定用户的命令（即与特定用户名相关联的用户）。

源代码的内容证实了这一论点，它包含了将命令发送者的ID与“Manager（管理员）”的ID进行比较的功能。在我们分析的三个样本中，“Manager”的ID和bot的main
token是它们唯一的区别。

![l12.jpg](https://image.3001.net/images/20180806/1533528144_5b67c85089911.jpg!small)

图12.检查命令发送者的ID

![l13.jpg](https://image.3001.net/images/20180806/1533528156_5b67c85cd63b0.jpg!small)

图13. Manager的用户名

通过使用这个用户名，我们在Telegram上找到了“manager”（或botmaster）的账户信息：

![l14.jpg](https://image.3001.net/images/20180806/1533528169_5b67c86916427.jpg!small)

图14. Manager的帐户信息

## Yara规则

    
    
    rule HeroRAT { meta: description = "Yara Rule to individuate some samples of HeroRATAndroid malware" author = "CSE CybSec Enterprise - ZLab" last_updated = "2018-07-31" tlp = "white" category = "informational" strings: $a = "assemblies/TeleSharp.dll" $b = "assemblies/Mono.Android.dll"$c = {49 64 00 67 65 74 5F 4D 79 4D 61 6E 61 67 65 72} $d = {52 65 70 6C 79 4D 65 73 73 49 64 00 73 65 74 5F 43 68 61 74 4964} condition: $a and $b and ($c or $d) }
    

***本文作者：Hydralab，转载请注明来自FreeBuf.COM**

