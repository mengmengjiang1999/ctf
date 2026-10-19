![](https://image.3001.net/images/20210826/1629966908_6127523c87b178c7eec68.jpg!small)

## 关于Allsafe

Allsafe是一款包含大量安全漏洞的Android应用程序，跟其他包含漏洞的Android应用不同，Allsafe的设计更像是那些使用了大量现代库和新型技术的真实应用程序，而且Allsafe的设计理念跟CTF比赛也是不一样的。

除此之外，我们还提供了一些基于Frida的安全挑战，广大研究人员可以根据自己的需求自行研究。

## 有用的Firda脚本

我在另一个代码库【[
_传送门_](https://github.com/t0thkr1s/frida)】中给大家提供了大量有用的Frida脚本（或模板），广大研究人员可以将其用于跟Firda相关的安全任务之中。

## 任务/漏洞

### 1、不安全的日志

简单的信息披露漏洞，可以使用logcat命令行工具来发现敏感信息。

 **相关资源：**

[ _Logcat工具_](https://developer.android.com/studio/command-line/logcat)

[ _Coinbase OAuth响应代码泄露_](https://hackerone.com/reports/5314)

### 2、硬编码凭证

某些凭证数据会遗留在代码中，你的任务就是对应用程序进行逆向工程分析，并寻找到敏感信息。

 **相关资源** ：

[ _Zomato硬编码凭证_](https://hackerone.com/reports/246995)

[ _8x8硬编码凭证_](https://hackerone.com/reports/412772)

[ _Reverb硬编码API密钥_](https://hackerone.com/reports/351555)

### 3、Root检测

这是一个纯Frida任务，你需要让代码相信你的设备没有root过。

### 4、任意代码执行

使用第三方应用安全地加载模块，并不是一件容易的事。你需要编写一个PoC应用，并成功利用该漏洞。

 **相关资源：**

[ _通过第三方代码包上下文实现任意代码执行_](https://blog.oversecured.com/Android-arbitrary-code-execution-via-third-party-package-contexts/)

### 5、安全标识绕过

这是另一个Frida任务，它并非一个真正意义上的漏洞，只是一个安全标识绕过挑战。

 **相关资源：**

 _Android FLAG_SECURE_

### 6、证书绑定绕过

证书绑定是通过OkHttp库实现的，你需要绕过它以使用BurpSuite查看流量。

 **相关资源：**

[ _证书和公钥绑定_](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)

[ _Coinbase漏洞_](https://hackerone.com/reports/5786)

### 7、不安全的广播接收器

应用程序中有一个存在漏洞的广播接收器，你需要使用正确的数据来触发它。

 **相关资源：**

[ _Android广播机制概述_](https://developer.android.com/guide/components/broadcasts)

[ _ok.ru广播接收器漏洞利用_](https://hackerone.com/reports/97295)

[ _Bitwarden存在漏洞的广播接收器_](https://hackerone.com/reports/289000)

### 8、深度链接利用

类似于不安全的广播接收器，你需要提供正确的查询参数来完成这个任务。

 **相关资源：**

[ _Android深度链接_](https://developer.android.com/training/app-links/deep-linking)

[ _获取不安全的深度链接﻿_](https://hackerone.com/reports/401793)

[ _Periscope深度链接CSRF_](https://hackerone.com/reports/583987)

### 9、SQL注入

这是一个常规的SQL注入，跟Web应用的SQL注入类似。你不需要逆向代码来绕过登录机制。

 **相关资源：**

[ _内容提供器中的SQL注入漏洞_](https://hackerone.com/reports/291764)

### 10、存在漏洞的WebView

你还可以在无需对应用程序进行反编译的情况下完成这个任务，弹出一个警告对话框并实现文件读取即可。

 **相关资源：**

[ _ownClod WebView XSS_](https://hackerone.com/reports/87835)

### 11、Smali修复

在这个任务中，你需要通过修改Smali代码来改变程序的执行流。最后，重新构建APK并对其签名。

 **相关资源：**

[ _Uber APK签名器_](https://github.com/patrickfav/uber-apk-signer)

### 12、原生库

应用程序使用了一个原生库来验证用户输入的密码，你需要对代码库进行逆向分析，并找到密码，然后使用Frida来挂钩原生方法。

 **相关资源：**

[ _Ghidra_](https://github.com/NationalSecurityAgency/ghidra)

[ _Cutter﻿_](https://github.com/rizinorg/cutter)

## 许可证协议

本项目的开发与发布遵循GPLv3开源许可证协议。

## 项目地址

 **Allsafe：** 【[ _GitHub传送门_](https://github.com/t0thkr1s/allsafe)】

