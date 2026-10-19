***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 写在前面的话

 **近日Trustlook
Labs发现了一个恶意安卓应用程序，它使用社会工程手法诱骗用户安装。这个应用程序（MD5：eb9d394c1277372f01e36168a8587016）使用Bangle
packer打包。**

触发该安装应用程序的主要活动为“com.goplaycn.googleinstall.activity.SplashActivity.”但是，神奇的是在反编译代码中的任何位置都找不到该行为：![](https://image.3001.net/images/20180726/1532612218_5b59ce7a1b7ad.jpg!small)

接下来就跟这我们一起来研究研究吧！

## 审计代码

我们从类SecAppWrapper开始审计，其中有一个“System.loadLibrary”调用load to
load”secShell.“模块中的本机层代码，他主要负责从“assets\secData0.jar”中解密和加载应用程序的主要负载，并经过解密的压缩DEX文件。![](https://image.3001.net/images/20180726/1532612226_5b59ce82630ca.jpg!small)![](https://image.3001.net/images/20180726/1532612380_5b59cf1cb62c1.jpg!small)

其中我们发现“secShell”模块中的大多数方法名称都经过混淆，并且在使用时会对其字符串进行解密。![](https://image.3001.net/images/20180726/1532612465_5b59cf71e0934.png!small)

该应用程序会检测手机中是否安装了框架，如Xposed。Xposed是一个用于在运行时操纵Android应用程序流的框架。![](https://image.3001.net/images/20180726/1532612477_5b59cf7d367f5.png!small)

![](https://image.3001.net/images/20180726/1532612485_5b59cf85d70bc.png!small)该应用程序还会分离子进程并调用“ptrace”来附加到父进程，以防止调试器进行任何附加尝试。多个进程相互跟踪以确保子进程存活![](https://image.3001.net/images/20180726/1532612493_5b59cf8d9b435.jpg!small)![](https://image.3001.net/images/20180726/1532612499_5b59cf938288b.jpg!small)![](https://image.3001.net/images/20180726/1532612506_5b59cf9a601c0.jpg!small)该应用程序并且会监视/proc文件系统中的值以检查进程的状态。![](https://image.3001.net/images/20180726/1532612524_5b59cfac0e2cb.jpg!small)要说得一点是“secShell”模块中的JNI_OnLoad函数具有两个分支。一个分支负责反调试，另一个分支（位于下面的0x7543EAE4）将主要的DEX模块进行解密。  
![](https://image.3001.net/images/20180726/1532612538_5b59cfba1becb.png!small)以下是解密函数：![](https://image.3001.net/images/20180726/1532612545_5b59cfc14a3b2.png!small)![](https://image.3001.net/images/20180726/1532612552_5b59cfc8ac986.png!small)在绕过反调试后，功能为“p34D946B85C4E13BE6E95110517F61C41”的模块将解密数据。其中寄存器R0包含文件位置，由标题字节“PK\x03\x04”标识.R1存储文件的大小。![](https://image.3001.net/images/20180726/1532612568_5b59cfd86fd8b.png!small)![](https://image.3001.net/images/20180726/1532612573_5b59cfdddb45e.png!small)我们可以转储内存：![](https://image.3001.net/images/20180726/1532612585_5b59cfe921d54.png!small)解压缩文件后，我们得到可以正常查看的DEX文件：![](https://image.3001.net/images/20180726/1532612593_5b59cff10814d.png!small)

## 总结

Android packers是保护合法移动应用开发者知识产权的有价值的工具。然而，它们也可以用于恶意目的，并使分析恶意应用程序更加困难。Trustlook
Labs继续致力于识别恶意应用程序以保护我们的客户和移动生态系统。

 ***参考来源：[trustlook](https://blog.trustlook.com/2018/07/19/bangle-android-app-packer-unpacking-analysis/)，由周大涛编译，转载请注明来自FreeBuf.COM**

