在逆向的世界中，有一个工具叫做IDA，它被称为神器，但是它的价格实在让人望而生畏(土豪例外)。正版的全平台下来估计要20w/年，貌似还是美元。当然了，网上有很多破解版的，这个看个人喜好，我不太习惯使用破解版的，一方面功能不全，另一方面，很不稳定。于是我就找到了一个替代IDA的工具-Radare2。个人认为除了在F5(decompiler)功能上有差距之外，其他地方两者很接近了。

### Radare2

在
[破解工具Radare2](https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247483720&idx=1&sn=f95ef690ead08dfed6abd6eb9000d25f&chksm=ea2a3782dd5dbe94a6444a3f586cde0eca42b376990c089a29ca663be2e07796175b2b280548&token=507946728&lang=zh_CN#rd)中多Radare2进行了介绍，在
[深入理解GOT覆写技术](https://mp.weixin.qq.com/s?__biz=MzI1NjEyMzgxMw==&mid=2247483959&idx=1&sn=fb61273c571feef8b5a3e55d4fdb4291&chksm=ea2a34fddd5dbdebec72fd386abab0cb832bcde458945f4b15a92401af9e4b1cd4caef425168&token=507946728&lang=zh_CN#rd)系列文章中对Radare2在Linux平台的使用有所介绍。这篇文章主要介绍使用Radare2对apk进行静态分析。

### 查看dex文件信息

本文选择某东的apk。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)从这里可以看出京东的apk应该是使用了Kotlin，不过无所谓，dex文件
**反汇编** 的结果还是smali的。 使用Radare2分析其中的主dex文件classes.dex。

> icq # 枚举类名 iiq # imports (external methods) ic # 枚举类和方法 izq # 列出程序中所有的字符串

举个例子，我想查找带有vip样式的字符串，`izq~vip`![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

#### 检测系统API使用

检查应用程序使用了什么系统API.

  1. `rabin2 -qi classes.dex |grep -i -e sms -e bluetooth -e install -e PackageManager-e Datagram-e Telephony-e nfc`

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

#### 查找引用

查找第一个vip字符串在哪里使用。很遗憾，在当前的dex中没有找到引用的地方。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)如果有引用的话，会是这个样子:
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

#### 过滤字符串

Radare2使用~作为过滤符号，相当于grep。 有意思的字符串如下(仅共参考):

  * /system /data /bin/su …
  * http://
  * https://
  * .apk
  * %d.%d.%d.%d
  * Install
  * SMS
  * DexClassLoader InjectCall (used for Dalvik code injection)
  * application/vnd.android (mimetype used to spawn .apk installations)
  * == (embedded base64 resources)

在dex文件中，一些字符串会使用base64编码，使用环境变量RABIN2_DEBASE64或者`rax-D`在每个字符串上面就可以实现自动解密。

  1. `RABIN2_DEBASE64=1rabin2 -qzz classes.dex`

#### 过滤方法

Radare2’s visual mode also supports an interactive heads-up display that will
filter out all **string, method, and class names** from the .dex file. 通过
**V_** 命令可以进入这种模式。

你可能感兴趣的文本如下:

  * onReceive (used by event handlers)
  * Init (all classes have one of them)
  * Password
  * Install
  * Dex
  * SMS

![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

#### 反汇编

通过afl命令列出所有的函数。通过v命令进入可视化界面。包括流程图、汇编代码、函数、符号等信息。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

### 写在最后

What's the meaning of following command:

  1. `dexdump -d |grep ‘“android.’|cut -d ,-f 2|sort -u`

### 公众号

更多内容，欢迎关注我的微信公众号:无情剑客。
![在这里插入图片描述](https://image.3001.net/images/20200701/1593550745.png!small)

  

