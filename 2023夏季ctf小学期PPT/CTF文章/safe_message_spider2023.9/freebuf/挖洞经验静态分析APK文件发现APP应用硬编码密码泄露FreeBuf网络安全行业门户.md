**![afe61b8b3e79eb6a46fc85d2ee1a780a.png](https://image.3001.net/images/20200226/1582722778_5e566eda90270.png!small)**

**今天给大家分享的Writeup是一篇关于安卓APP的静态分析，由于该APP存在不安全存储和硬编码密码泄露问题，导致可以登录其短信管理系统，劫持其短信接口配置，以下为相关分析研究，希望能对大家有一些参考借鉴作用。**

## 着手开始

由于众测项目范围涉及到相关厂商的某款安卓APP，所以我就在我的安卓手机中下载了这款APP应用，并把其APK文件拿出来做静态分析。在此推荐两个原生快速的APK下载网址：

> <https://apk.support/apk-downloader>
>
> <https://apkpure.com/>

获得了APK文件之后，我们需要对它进行反编译找到其中的Java类文件进行分析，这里可以安装以下两个工具：

> <https://github.com/pxb1988/dex2jar>
>
> <https://mac.filehorse.com/download-jd-gui-java-decompiler/>

安装了上述工具后，我们把目标APP的APK文件放到另一个单独文件夹中，把其后缀由.apk更改为.zip，然后解压zip文件，之后我们就可以看到一些xml文档、路径文件、模板资源文件等，在这些文件中我们的目标是classes.dex文件，解压后一般会发现一个或多个classes.dex文件。接着，我们用dex2jar把dex文件转换为java文件，使用以下命令：

> dex2jar classes.dex

如果该命令不管用，那么可以用dex2jar的另外一个版本命令：

> d2j-dex2jar classes.dex

![01.png](https://image.3001.net/images/20200226/1582722558_5e566dfed2c21.png!small)运行上述命令之后会在文件夹内生成如classes_dex2jar.jar的java文件，有了该文件后，我们就要用另一个好用的工具来对它反编译了，这里我个人喜欢用的是JD-GUI，<https://github.com/java-decompiler/jd-gui>，用它打开生成的jar文件后我们就能看到很多java资源文件，还能把这些不同资源文件进行保存阅读。

![02.png](https://image.3001.net/images/20200226/1582722580_5e566e146b5b7.png!small)![03.png](https://image.3001.net/images/20200226/1582722588_5e566e1c4e605.png!small)有了保存的资源文件代码，我们要尽量从中找出一些问题来，这里我推荐一个工具-动化移动安全渗透测试框架： [Mobile Security
Framework（MobSF）](https://github.com/MobSF)，它是一款智能、一体化的开源移动应用(Android/iOS)自动渗透测试框架，支持二进制文件(APK
& IPA)和源码压缩包，用它可以进行静态和动态的分析。  

## 代码分析

做好了上述工作后，我们就可以认真分析安卓APP中的代码了，回到我们的目标APP中。当我坐下来按照我的检查列表分析时，不久我就发现其中一个叫Constant.java的文件，它位于APP的SMS路径下，包含了一些零散的信息，如
Username、Loacation、Password等硬编码服务信息以及短信发送接口（SMS API）的URL路径。大概情况如下：

![3-sms-jv.png](https://image.3001.net/images/20200226/1582722658_5e566e62b1597.png!small)进一步分析发现，该APP使用了reson8公司的短信即时发送平台进行商业化推广，<https://www.reson8.ae/>，我浏览了reson8公司网站，发现其具备用户登录接口，所以我就想到了上述静态分析中泄露的Username和Password信息，直接把它拿来这里登录用看看，果然一输入提交我就进入了目标APP公司的短信发送管理系统了：

![login.png](https://image.3001.net/images/20200226/1582722676_5e566e743242c.png!small)![04.png](https://image.3001.net/images/20200226/1582722685_5e566e7d76139.png!small)

该管理系统就是一个SMS API网关，通过它可以实现短信定向发送设置，营销升级和充值等管理操作，更关键的是可以下载用户的手机号码。

## 总结

在对APP做动态和其它分析之前，建议对其做一些静态分析，可以按照自己的检查列表依次进行，从中或许可以获取到一些意想不到的零散信息。对于APP应用公司来说，千万要避免在APP中存储一些密码凭据相关的信息，即使有必要也需要进行一些恰当的加密处理。

***参考来源：[securitybreached](https://blog.securitybreached.org/2020/02/19/hacking-sms-api-service-provider-of-a-company-android-app-static-security-analysis-bug-bounty-poc/)，clouds 编译整理，转载请注明来自 FreeBuf.COM**  

