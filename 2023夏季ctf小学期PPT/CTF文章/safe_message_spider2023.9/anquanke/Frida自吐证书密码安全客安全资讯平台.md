# Frida自吐证书密码

阅读量 **169038**

发布时间 : 2022-05-10 14:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0137f979f3683fcb83.jpg)

## 双向认证APP自吐密码

在许多业务非常聚焦比如行业应用、银行、公共交通、游戏等行业，C/S架构中服务器高度集中，对应用的版本控制非常严格，这时候就会在服务器上部署对app内置证书的校验代码。

抓包出现如下提示时，我们确定出此APP为服务器校验app客户端证书

![](https://p2.ssl.qhimg.com/t0127486068e2154476.jpg)

对于此类APP抓包而言通常需要完成两项内容：

找到证书文件

找到证书密码

服务器对客户端进行校验过程中，客户端将证书公钥发送给服务器，以及从服务器获取session和私钥解密过程中，需要API进行操作，API存在于java层框架内，所以hook框架层代码`java.security.KeyStore`，使密码自吐

# frida -U -f cn.soulapp.android -l ssl.js –no-pause

![](https://p3.ssl.qhimg.com/t01ed4bc5067ffc5f91.jpg)

密码}%2R+\OSsjpP!w%X

然后首先使用常规方式解压搜索app包里的证书文件。一般apk进行解包，直接过滤搜索后缀名为p12的文件即可，一般常用的命令为tree -NCfhl
|grep -i p12，直接打印出p12文件的路径.

![](https://p4.ssl.qhimg.com/t011015b1c6ec6c2b04.jpg)

如果在安装包内找不到证书的话，也可以进行hook`java.io.File`

# android hooking watch class_method java.io.File.$

init

![](https://p2.ssl.qhimg.com/t01429360a7e0359b0a.jpg)

通过hook也可以找到该证书文件。

# objection -g cn.soulapp.android explore –startup-command “android hooking
watch class_method java.io.File.$init –dump-args”

使用抓包工具点击导入证书

![](https://p4.ssl.qhimg.com/t01fc5a2e40de04523c.jpg)

密码随意设置

然后进去之后导入p12证书和密码（自吐出的密码），host和port输入*

![](https://p3.ssl.qhimg.com/t01af121dad23c13fc9.jpg)

可以看到可以成功抓到了数据包

![](https://p0.ssl.qhimg.com/t014e26412e85bf3ff8.jpg)

## hook抓包

1、首先确定使用的框架，主流框架okhttp、HttpURLconnection

使用objection打印内存中所有的类

# android hooking list classes

然后搜索过滤类文件中值得怀疑的框架

.objection # cat objection.log |grep -i volley

.objection # cat objection.log |grep -i okhttp

.objection # cat objection.log |grep -i

![](https://p0.ssl.qhimg.com/t0147d1a82848968750.jpg)

![](https://p1.ssl.qhimg.com/t0113987987d098b16e.jpg)

![](https://p5.ssl.qhimg.com/t01047b858a1ad99db1.jpg)

找到APP使用的框架后，最后通过frida加载js脚本来进行绕过。

## ZenTracer

批量hook查看调用轨迹的工具ZenTracer

# git clone https://github.com/hluwa/ZenTracer

点击Action之后，会出现匹配模板（Match RegEx）和过滤模板（Black
RegEx）,将`M:java.net.HttpURLConnection`填入后会将该类的所有方法进行hook并运行

![](https://p1.ssl.qhimg.com/t01c290554221259298.jpg)

同时手机点击登录、注册等功能模块时，发现经过了该方法`java.net.HttpURLConnection.getFollowRedirects()`：

![](https://p0.ssl.qhimg.com/t01b07845f372bcc7e5.jpg)

然后使用`objection`hook该方法

# android hooking watch class_method
java.net.HttpURLConnection.getFollowRedirects –dump

-args –dump-return –dump-backtrace

![](https://p4.ssl.qhimg.com/t01d078f508634b6301.jpg)

根据打印出的`com.cz.babySister.c.a.a(HttpClients.java:22)`

直接定位到了收发包函数的地址，然后查看收发包的内容如下：

# android hooking watch class_method com.cz.babySister.c.a.a –dump-args –dump-backtrace –dump-return

![](https://p0.ssl.qhimg.com/t01c070a25b165d7829.jpg)

## 强混淆APP

使用工具OkHttpLogger-Frida

1、首先将okhttpfind.dex 拷贝到手机 /data/local/tmp/目录下

# adb push okhttpfind.dex /data/local/tmp/

# chmod 777 *

2、执行命令启动frida -U -l okhttp_poker.js -f com.example.demo –no-pause 可追加 -o
[output filepath]保存到文件

# frida -U -l okhttp_poker.js -f org.sfjboldyvukzzlpp –no-pause

![](https://p3.ssl.qhimg.com/t01587170449cc98704.jpg)

然后复制被混淆后的类名，粘贴到okhttp_poker.js文件中，重新运行后运行`hold()`开启hook拦截，然后操作App后，会出现拦截的内容如下

# nano okhttp_poker.js

![](https://p4.ssl.qhimg.com/t013f52bd142ff52f41.jpg)

当然除了ZenTracer，也可以直接使用objection工具进行批量hook，

首先将怀疑的类复制保存到文件中，并在保存内容前加上`android hooking watch class`

# android hooking list classes

# objection -g com.cz.babySister explore -c “/root/Desktop/2.txt”

## 参考资料

<https://www.anquanke.com/post/id/197657>

<https://bbs.pediy.com/thread-258776.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Tide安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/272672](/post/id/272672)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [frida](/tag/frida)
  * [网络安全](/tag/网络安全)

 **+1** __1赞

 __收藏

![](https://p5.ssl.qhimg.com/t013dca47abc465f8d2.png) Tide安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

