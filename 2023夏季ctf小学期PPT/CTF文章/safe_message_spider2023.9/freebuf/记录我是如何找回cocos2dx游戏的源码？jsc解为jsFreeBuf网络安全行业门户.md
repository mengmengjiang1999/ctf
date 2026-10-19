首先推荐我的小助手：lab-robot她不但兼职社交电商的机器人工作，还可以接待渴望破解游戏的顾客。

接下来，我介绍一下如何快速获取cocos2dx的游戏源码。

  

获得APK之后，第一步是将它解压。

  

解压之后，找到里面的assets文件夹里面的src文件夹里面的jsc文件。

  

如果你想要的是js文件，重点就是破解这个文件。

  

我找到了官网的说辞，引用：<https://discuss.cocos2d-x.org/t/compiled-javascript-jsc-file-is-it-secure-enough-and-cannot-be-decompiled/8493/2>

其中有一个人回复：

“I have tested it, the result was that using **jsc** is safe for protecting
your game sources.”

  

然而这并没有让我停止探索的脚步。最终我通过阅读多个大佬的文章，结合自己的理解，写了一段代码，可以找到加密的密码，从而成功破解了jsc。

  

但是，看到源码之后，却发现还有更大的问题需要破解。

  

于是又Google了一下，发现了一个神器Hydra。

  

为了让各位读者不扫兴而归，我提供以下线索，希望你们能通过自己的研究，也找到相同的破解方法。

准备这些工具：adb，xxtea，zip，apktool，jarsigner，字节码分析工具（自己写代码分析二进制流）

步骤：apktool解包 -> 字节码分析工具找到密码 -> xxtea解密文件 -> zip解压 -> 【获得js源码】 -> zip压缩 ->
xxtea加密文件 -> apktool打包 -> jarsigner签名 -> 【获得新apk】-> adb push到安卓 -> 【完成】

  

第一次写文章，多谢各位捧场。

我的助手：lab-robot 微笑

