## 前言

**星期一的晚上像往常一样我通过观看电视节目来打发时间，但并没有什么有趣的节目。于是我决定在手机上寻找乐趣，我开始漫无目的在Twitter上翻看各种推文，一条Fox
News的推送内容引起了我的关注。**

![Fox新闻](https://image.3001.net/images/20181108/1541631650_5be36ea28fc86.png!small)

有人为特朗普的支持者开发了一个名为“唐纳德约会者”（Donald
Daters）的软件，并配以“让美国人再次约会”的响亮口号！这顿时激起了我的斗志，我决定拿它来练练手~

## 初步侦察

我立马从PlayStore下载了这个应用程序，并以普通使用者的身份对它的可用功能进行了初步的了解。

这是一款约会app，通过对象匹配的方式与陌生人进行对话。

## 静态分析

>
> 1）首先，我将APK文件从我的手机导入到了电脑上。你可以[使用这款软件](https://play.google.com/store/apps/details?id=com.ses.app.apkexport&hl=en)来帮助你完成这个过程。
>
> 2）APK是一个ZIP文件，解压缩并提取DEX文件。
>
> 3）你可以使用[jadx](https://github.com/skylot/jadx)这款工具，从提取的DEX文件中获取反编译的源码。
>
> 4）使用[apktool](https://ibotpeaches.github.io/Apktool/)获取应用程序的resources文件。

一切准备就绪，现在让我们来分析这些获取的文件，通过查看AndroidManifest.xml文件，我们可以知道：

> 该应用当前使用的是Firebase数据库；
>
> 这是一个React
> Native应用程序，com/donalddaters文件夹几乎为空可以证明这一点。这种应用程序的代码位于assets/index.android.bundle文件中；
>
> 该应用会要求授权许多敏感权限。

接着，我查看了values/strings.xml文件。

![alues/strings.xml文件](https://image.3001.net/images/20181108/1541631689_5be36ec9574bf.jpeg!small)

可以看到ID和密钥都被硬编码在了该文件中。此外，我们还可以看到他们正在使用Firebase数据库。让我们看看他们是否正确配置了数据库。我在Chrome中粘贴访问了<https://donalddaters2018.firebaseio.com/.json>：

![配置数据库](https://image.3001.net/images/20181108/1541631708_5be36edc5d800.png!small)

他们竟然保留了数据库的开发设置。这意味着任何人都可以访问他们的数据库......现在，我可以查看到数据库中所有用户信息（包括姓名，头像，身份，平台，通知），甚至是使用他们的token，查看所有私人消息等。

该应用仅上线了几小时，因此只有1607个注册用户和128个rooms。 有趣的是，其中最长的一个讨论（62条消息），来自于应用程序开发者之间。

如以下截图中所示，这里有一个指向数据库中用户头像的链接。

![用户头像的链接](https://image.3001.net/images/20181108/1541631739_5be36efb593cd.png!small)

多亏了这个简单的小脚本，帮我下载了所有可用的头像，我已将部分头像发布在了Twitter上。

这是一小部分配置文件图片。<https://t.co/GxIr5Mtf8d>：

![小部分配置文件图片](https://image.3001.net/images/20181108/1541631761_5be36f112ef20.png!small)

## 漏洞利用

我创建了一个新的Android应用并添加了Firebase。具体操作可以[参阅本指南](https://firebase.google.com/docs/android/setup)。

在我的项目中有一个google-services.json文件，其中存储了所有Firebase设置。为了与Donald
Daters的Firebase数据库进行通信，我需要找到他们的Firebase设置（api密钥，数据库URL以及storage
bucket）并将它们替换到我的google-services.json文件中。

前面我们已从values/strings.xml文件中，获取到了数据库URL和storage bucket。那么，api密钥又在哪获取呢？

在静态分析那部分我提到过，React Native应用程序的代码位于assets/index.android.bundle文件中。让我们来逆向它！

通过使用[binwalk](https://github.com/ReFirmLabs/binwalk)，我提取出了一堆的javascript文件。

![javascript文件](https://image.3001.net/images/20181108/1541631789_5be36f2da42fa.png!small)

使用grep命令，我很快就找到了api key。

现在，google-services.json文件中的所有必要设置我们都已填写完成。让我们来创建了一个用于读/写Donald
Daters数据库的activity。

![读/写Donald
Daters数据库](https://image.3001.net/images/20181108/1541631815_5be36f4707114.png!small)

这段代码将会读取数据库的所有“rooms”，即“匹配”。

这里我编写了一个PoC，可用于验证Donald Daters应用程序数据库的脆弱性。有了这个POC，我可以查看所有私人消息 - 用户信息 -或是删除：消息，用户，甚至是整个数据库中的内容。<https://t.co/7doErhzYdY>：

![POC](https://image.3001.net/images/20181108/1541631835_5be36f5bf0dac.png!small)

我是一个有操守的白帽子，但我可以告诉你添加这一小行“myRef.setValue(“”)”，你将会清空整个数据库。

## 缓解措施

> 发布应用时，不要使用Firebase数据库的开发设置；
>
> 聘请有能力的开发人员，这会带来很大的帮助。

## 时间线

### 1）在Twitter上发布

Hi[@FoxNews](http://twitter.com/FoxNews)和[@realDonaldTrump](http://twitter.com/realDonaldTrump)支持者，我可以在5分钟内获取所有注册用户的：名称
- 照片 - 个人消息 - 令牌等。你们应该立即停止它的使用，并修复这个漏洞，<https://t.co/72KdNJTrmk>。

![在Twitter上发布](https://image.3001.net/images/20181108/1541631872_5be36f809d0d6.png!small)

### 2）相关媒体进行了及时的报道

> <https://motherboard.vice.com/en_us/article/mbdwb3/the-donald-daters-trump-> dating-app-exposed-a-load-of-its-users-data>
>
> [techcrunch.com/2018/10/15/donald-daters-a-dating-app-for-trump-supporters-> leaked-its-users-data/](http://techcrunch.com/2018/10/15/donald-daters-a-> dating-app-for-trump-supporters-leaked-its-users-data/)

### 3）Donald Daters更改了他们数据库的设置

### 4）报告回复

感谢你的关注和报告！我们已修复了这个安全问题，并正在为DonaldDaters社区的发展持续努力！希望你继续关注我们，第一时间反馈你所发现的问题。再次感谢！<https://t.co/EBIOggrh8K>

![报告回复](https://image.3001.net/images/20181108/1541631910_5be36fa612d41.png!small)

 ***参考来源：[medium](https://medium.com/@fs0c131y/how-i-found-the-database-of-the-donald-daters-app-af88b06e39ad)，FB小编secist编译，转载请注明来自FreeBuf.COM**

