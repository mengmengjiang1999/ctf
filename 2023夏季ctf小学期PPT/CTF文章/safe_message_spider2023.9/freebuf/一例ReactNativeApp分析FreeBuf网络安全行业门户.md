## 前言

最近工作中碰到一个app，发现传参是加密的，需要解密，按照之前常规的做法发现没有hook到对应的加密逻辑，最后才发现是基于ReactNative开发的，借此来浅浅地学习下ReactNative的逆向。

介绍下ReactNative，RN是Facebook开源的一个跨平台移动应用开发框架，是Facebook开源的JS框架React在原生移动应用平台的衍生产物，支持iOS和安卓两大平台。RN使用Javascript语言，类似于HTML的JSX，以及CSS来开发移动应用。

## 分析App

首先分析它的登录协议，登录界面长这样。  
![image](https://image.3001.net/images/20230818/1692337751_64df0657406f6fd451f3b.png!small)

随便输入手机发送验证码，抓个包发现是加密的。  
![image](https://image.3001.net/images/20230818/1692337764_64df0664108cbc5e558e1.png!small)  
这里就要开始分析它的算法了。

## Java层分析

直接frida-dexdump一下，拖进工具看看java层代码，直接搜接口找了对应的接口。  
![image](https://image.3001.net/images/20230818/1692337781_64df067509e59355e4922.png!small)

找到对应的调用方法。  
![image](https://image.3001.net/images/20230818/1692337795_64df06838eda3e1425676.png!small)

我一开始直接对应的方法，没有输出，然后hook
HashMap的put方法，发现也没有输出，这里卡了很久，后面记起来他UA是ok3，又hook了一下ok3,终于有输出了，打印了一下堆栈：  
![image](https://image.3001.net/images/20230818/1692337814_64df0696cc5cfd612d97a.png!small)

发现调用栈压根没有走过我之前测试hook的那些方法，打印出了一堆react相关的调用，这里开始意识到这个app是基于ReactNative开发的。

验证下猜想，解压查看了下对应的lib目录，确实是基于ReactNative开发的。  
![image](https://image.3001.net/images/20230818/1692337830_64df06a6e835ab9fda7b3.png!small)

确定了那就简单了。

## 分析JS代码

解压apk,在assets目录下，可以看到index.android.bundle文件。  
这里面包含了应用主要的业务逻辑代码，我改个后缀直接放编辑器里格式化查看。  
![image](https://image.3001.net/images/20230818/1692337848_64df06b8a491dcf3cb461.png!small)

里面基本主要业务的接口调用代码都在了。  
![image](https://image.3001.net/images/20230818/1692337862_64df06c6b01463a691748.png!small)

继续全局搜加解密代码，发现了一处国密调用。  
![image](https://image.3001.net/images/20230818/1692337873_64df06d1a973dc45d9560.png!small)

这个应用并不复杂，基本都是靠js去实现对应的加解密，里面写的比较清楚，直接把key iv拿过来进行加解密测试，发现已经能看到明文了。  
![image](https://image.3001.net/images/20230818/1692337887_64df06df24d1773879e20.png!small)

## 总结

总体来看，安卓ReactNative应用分析没有那么复杂，主要的业务逻辑（index.android.bundle文件）能很容易进行分析，虽然可以混淆，但是还是能有一定的可读性。二来应用运行时不校验JS代码，可以通过hook替换JS文件实现代码注入，具备了可调试能力。

