**Google采取多种措施保护其应用商店并阻止恶意软件进入，但黑客仍在寻找渗透应用商店和访问用户设备的方法。数百万手机用户无意间下载了恶意应用程序，这些应用程序可以访问用户数据，凭据，电子邮件，文本消息和地理位置。例如，在2020年2月，Haken恶意软件家族通过8种不同的恶意应用安装在50,000多台Android设备中。**

近期Check
Point的研究人员发现了一个新的恶意软件家族“Tekya”，该家族可在56个应用程序中运行，已在全球范围内下载了近100万次。恶意软件模仿用户的操作，点击来自Google
AdMob，AppLovin，Facebook和Unity等机构的广告和横幅。恶意应用程序中有二十四款针对儿童（从拼图到赛车游戏），其余为实用程序（例如烹饪应用程序，计算器，下载器，翻译器等）。

## 综述

Tekya恶意软件进行了代码混淆，避免被Google Play Protect检测，并利用Android中的“
MotionEvent”机制（于2019年推出）来模仿用户的操作点击。VirusTotal和Google Play
Protect未检测到Tekya恶意软件家族，可从Google Play下载相关的56个应用程序。

恶意软件克隆了合法应用程序来吸引用户，其中大多数是儿童，因为Tekya恶意软件大多数是儿童游戏，目前这些应用程序已全部从Google
Play中删除。但是，这再次凸显了Google
Play商店仍然可以托管恶意应用。商店提供了将近300万个应用程序，每天有数百个新应用程序上传，很难检查每个应用程序是否安全。用户不能仅依靠Google
Play的安全措施来确保下载软件的安全性。

下面为恶意应用程序示例，全部恶意软件列表见附录：

![](https://image.3001.net/images/20200325/1585122312_5e7b0c08b4acc.png!small)

![](https://image.3001.net/images/20200325/1585122286_5e7b0bee13bed.png!small)

## 技术分析

从Google Play安装此应用程序后，将执行以下多项操作：

> “BOOT_COMPLETED”允许设备启动时运行代码
>
> “USER_PRESENT”检测用户何时正在使用设备
>
> “QUICKBOOT_POWERON”允许设备重启后运行代码

![](https://image.3001.net/images/20200325/1585129412_5e7b27c468eb2.png!small)

接收器在.apk文件中的libraries文件夹加载本地“ libtekya.so”文件。

![](https://image.3001.net/images/20200325/1585129619_5e7b28934f2ca.png!small)

在“ Tekya”库的构造函数中，创建“ Validator”对象列表。

![](https://image.3001.net/images/20200325/1585129905_5e7b29b12340b.png!small)

在每个“ Validator”中都会有调用方法运行来自本地库“ libtekya.so”的内部函数。“
AdmobValidator”调用c函数，然后运行z函数，该函数又从本机库中调用“ zzdtxq”函数。

![](https://image.3001.net/images/20200325/1585130032_5e7b2a3072dc2.png!small)

在“ libtekya.so”库中，Validator调用的函数负责多种操作：

> “ffnrsv”负责解析配置文件
>
> “getWindow”和“getDecorView”获取所需的句柄
>
> “ sub_AB2C”负责处理上述功能的结果

![](https://image.3001.net/images/20200325/1585130189_5e7b2acd4c842.png!small)

最后“ sub_AB2C”创建并调度触摸事件，通过“ MotionEvent”模仿点击：

![](https://image.3001.net/images/20200325/1585130230_5e7b2af67ae75.png!small)

VirusTotal对恶意软件测试结果：

![](https://image.3001.net/images/20200325/1585130280_5e7b2b28b8b38.png!small)

## 如何防护

如果怀疑自己的设备上装有这些恶意应用程序之一，请执行以下操作：

> 从设备上卸载恶意应用程序
>
> 安装安全解决方案以防止感染
>
> 将操作系统和应用程序更新到最新版本

## 附录

![](https://image.3001.net/images/20200325/1585147079_5e7b6cc7a44d0.png!small)

![](https://image.3001.net/images/20200325/1585147079_5e7b6cc7a7244.png!small)

![](https://image.3001.net/images/20200325/1585147079_5e7b6cc7a87c7.png!small)

![](https://image.3001.net/images/20200325/1585147079_5e7b6cc7e7008.png!small)

 ***参考来源：[checkpoint](https://research.checkpoint.com/2020/google-play-store-played-again-tekya-clicker-hides-in-24-childrens-games-and-32-utility-apps/)，由Kriston编译，转载请注明来自FreeBuf.COM**

