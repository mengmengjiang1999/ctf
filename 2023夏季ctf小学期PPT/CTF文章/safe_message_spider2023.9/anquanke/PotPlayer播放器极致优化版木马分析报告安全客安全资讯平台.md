# PotPlayer播放器极致优化版木马分析报告

阅读量 **265609**

|评论 **2**

发布时间 : 2018-01-03 11:50:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

>
> 近期360安全卫士在软件下载站拦截到了利用PotPlayer播放器传播的远控木马，该木马巧妙的利用了正常文件和加密脚本，通过内存解密载入恶意代码，进行远控。通过检测多个安全进程，改变自身运行流程，对抗杀软查杀。主要功能是：记录键盘输入，盗取用户的账号信息以及远程下载其他木马，隐蔽性非常高，而且通过下载站大量的传播。

## 木马传播

木马文件通过下载站和论坛传播，经常以“精简”，“优化”和“破解”等标题吸引用户下载。

![](https://p5.ssl.qhimg.com/t01379ab5343deabd1c.jpg)

## 木马行为详解

木马利用了白加黑技术来躲避查杀，并且采用了多个脚本文件和多次加密，具体流程如下：

![](https://p5.ssl.qhimg.com/t01184b4c029de5e753.jpg)

### **木马脚本部分：**

  1. 木马安装包释放的桌面快捷方式指向一个名称为PotPlayerMinis.exe的正常程序。

![](https://p1.ssl.qhimg.com/t0140d1580b1a762ceb.jpg)

  2. 该程序会默认自动读取同目录下gamepatch文件夹下的config.ini配置文件。

![](https://p0.ssl.qhimg.com/t01bedbc7c3cdc217c9.jpg)

  3. PotPlayerMinis.exe读取gamepatch中的config.ini配置文件。以配置项InstParam指定的参数运行InstFile配置项指定的程序suchost.exe（其实是NirCmd.exe），从而实现把PotPlayerMinis.exe拷贝到配置文件所在路径下，重命名为svhost.exe，启动配置项mainExe指定的程序的目的。

![](https://p3.ssl.qhimg.com/t01169b7be5a8031188.jpg)

  4. svhost.exe以相同的方式读取同路径下的\gamepatch\config.ini，依次执行配置文件中指定的程序。

![](https://p0.ssl.qhimg.com/t01f312c22a00ef8db0.jpg)

  5. svhost.exe通过cmd.exe运行C:\PotPlayer\gamepatch\gamepatch\gamepatch\config.ini指定的脚本C:\PotPlayer\gamepatch\gamepatch\updete.bat。

![](https://p2.ssl.qhimg.com/t01ac532b6ec060b630.jpg)

  6. C:\PotPlayer\gamepatch\gamepatch\updete.bat文件经过简单的混淆。该脚本主要功能是为后续木马程序的运行准备相关文件并启动主要脚本qiaoi.bat。

![](https://p1.ssl.qhimg.com/t01f20e06834867bce5.jpg)

**具体功能包括** ：

重命名PotPlayer\gamepatch\gamepatch\config.xml为config.ini，并把该文件拷贝到PotPlayer\gamepatch\路径下。为后续启动PotPlayer的正常播放器功能做准备。

![](https://p0.ssl.qhimg.com/t01fc6d9221fd21b257.jpg)

判断%TEMP%\下是否存在bug0.txt，如果不存在就创建bug0.txt并保存脚本当前路径到bug0.txt。

创建C:\HTEMP0文件夹，创建%TEMP%\qr.tmp保存字符串Rar文件头，并与
\gamepatch\gamepatch\update.tmp文件重新组建成一个完整的RAR压缩包，拷贝到C:\HTEMP0\路径下，重命名为uqdate.dat

拷贝gconfig.ini到%APPDATA%下，重命名为payerss.ini。拷贝cfwd.dat到%TEMP%下。拷贝updatej.tmp到C:\HTEMP0\下。（updatej.tmp其实是winrar.exe的命令行程序）

调用updatej.tmp解压缩C:\HTEMP0\uqdate.dat中的 qiaoi.bat到C:\HTEMP0\路径下。（解压密码是p（小写））

![](https://p2.ssl.qhimg.com/t01bf784b1c03304c22.jpg)

最终运行C:\HTEMP0\qiaoi.bat脚本。

文件bat同样是经过简单混淆的脚本。该脚本功能比较复杂，包括解压配置文件，重组PE文件，判断正在运行的杀软进程，根据不同杀软改变运行流程等。

![](https://p2.ssl.qhimg.com/t0191e031581dae24a9.jpg)

### **重要功能包括：**

从dat中解压缩 ForceLibrary.tmp，恢复文件的MZ标志，组成一个完整PE文件。这个PE文件名是随机的，暂且叫xx.DLL。

![](https://p1.ssl.qhimg.com/t0198e1bbbbc05926cc.jpg)

判断杀软同时判断用户是否感染其他木马，改变后续程序运行流程。

![](https://p1.ssl.qhimg.com/t011f787f480346b904.jpg)

![](https://p2.ssl.qhimg.com/t0146639730dc378250.jpg)

脚本qiaoi.bat会依次检测360tray.exe、QQPCTray.exe、ns.exe和kxetray.exe是否存在，如果全都不存在，脚本会直接启动rundll32，来加载C:\HTEMP0\xx.dll（脚本随机dll名称），调用导出函数TrapEntry。TrapEntry会解压缩C:\HTEMP0\uqdate.dat中的bhdll.dat到%TEMP%路径下，然后内存解密该文件。该文件就是1号傀儡进程的寄生程序。

![](https://p0.ssl.qhimg.com/t01568c643f10139c48.jpg)

## 可执行程序部分

### **主要功能：**

运行随机名称的xx.Dll，启动后续远控木马运行流程，xx.dll主要是通过配置文件%APPDATA%\payerss.ini来获取远控木马资源的保存路径并进行傀儡进程数据的解密。

创建的傀儡进程还会连接网络下载其他木马资源，同时枚举进程，判断当前进程链中的有没有敏感进程名，如Aliimsafe.exe，360netman.exe，HRsword.exe和电脑管家等。如果存在敏感进程，就会改变远控木马的加载运行流程，对抗杀软。

获取payerss.ini配置信息，主要是木马其他资源的保存路径

![](https://p0.ssl.qhimg.com/t01e05b48da2faf47da.jpg)

![](https://p1.ssl.qhimg.com/t011235b2bd7d3fe29f.jpg)

读取%APPDATA%\winst\bhdll.dat文件，通过解密bhdll.dat，获取PE然后创建1号傀儡进程svchost.exe。1号傀儡进程还会解密数据，创建2号傀儡进程。

读取bhdll.dat

![](https://p0.ssl.qhimg.com/t0190ad3daa9945bfb8.jpg)

![](https://p2.ssl.qhimg.com/t0158befa316c975e7d.jpg)

![](https://p0.ssl.qhimg.com/t017f6a6c532c25b912.jpg)

使用aticdxxfwd.dat和qq333666666生成解密秘钥。

![](https://p5.ssl.qhimg.com/t01b8ecb7fdb23b6106.jpg)

![](https://p3.ssl.qhimg.com/t017e072a6fba88d7e5.jpg)

使用生成的秘钥，解密bhdat数据，最终生成1号傀儡进程的PE文件：

![](https://p2.ssl.qhimg.com/t01d8c141ab5dd52691.jpg)

![](https://p2.ssl.qhimg.com/t01a9d6c9b3d5d7f50e.jpg)

经过多次拷贝和检查PE文件格式后，创建傀儡进程svchost.exe

![](https://p0.ssl.qhimg.com/t01bda755c3e0f21de9.jpg)

![](https://p2.ssl.qhimg.com/t01055e0d3b23ff8771.jpg)

完成创建后，1号傀儡进程会枚举进程，判断当前进程链中是否含有敏感进程，这里我是用WinHex的进程充当aliimsafe.exe的进程进行试验。

1号傀儡进程，如果发现存在aliimsafe.exe进程就会结束该进程，并删除aliimsafe.exe文件，然后在aliimsafe.exe所在目录下创建一个同名文件夹，阻止aliimsafe.exe进程重新创建。

![](https://p0.ssl.qhimg.com/t01b01903477619244d.jpg)

在aliimsafe.exe的路径下创建的同名文件夹

![](https://p5.ssl.qhimg.com/t01fa8048d78c027c5d.jpg)

![](https://p1.ssl.qhimg.com/t01d6c4bfe8058ae216.jpg)

该傀儡进程还会创建一个傀儡进程2号，被解密文件是%APPDATA%\winst\cfwd.txt。这个傀儡进程2号就是远控木马的主体。

![](https://p4.ssl.qhimg.com/t0103afb441d045db3d.jpg)

1号傀儡进程还会访问网络信息im361.top/4441.txt，同时通过bkw888.bokee.com获取其他木马资源。

![](https://p4.ssl.qhimg.com/t01045639e126a0eb99.jpg)

![](https://p1.ssl.qhimg.com/t01f1c3e9d830ea6b5d.jpg)

**远控木马：**

该远控木马和11月30号的分析报告《伪装迅雷破解版网银盗号木马深度追踪》
（<https://www.anquanke.com/post/id/87775>）
中提到的远控木马属于同一款，只有导出函数名称不一样，但是木马主体功能和代码高度相似。

键盘记录功能函数代码逻辑：

![](https://p0.ssl.qhimg.com/t0126d2aad9314be23e.jpg)

流程控制函数代码逻辑：

![](https://p3.ssl.qhimg.com/t01f7f0370b2f2d4a96.jpg)

![](https://p1.ssl.qhimg.com/t019e703a92020adaed.jpg)

## 杀毒提示

该木马利用多种途径进行传播，盗取用户的账户信息，并且远程控制用户电脑，带来了严重的危害。360已经第一时间查杀该类木马文件。建议网友们选择安全的网站下载文件，安装包及时扫描查杀，避免使用来源未知的可疑软件。

![](https://p4.ssl.qhimg.com/t01672fe0092699fc26.jpg)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360安全卫士** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/93227](/post/id/93227)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [木马](/tag/木马)
  * [分析报告](/tag/分析报告)
  * [PotPlayer](/tag/PotPlayer)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t01cc856584b7ed76c0.jpg) 360安全卫士

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

