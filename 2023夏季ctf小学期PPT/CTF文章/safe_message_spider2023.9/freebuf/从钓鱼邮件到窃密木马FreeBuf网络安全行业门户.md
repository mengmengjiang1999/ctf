## 0x00 前言

在做样本分析的时候，通常都是针对恶意软件进行分析。这种属于样本分析，是安全分析中的一部分，但也是比较关键的一部分。样本分析是安全分析人员与恶意软件开发/投放人员沟通最直接的桥梁。

但是很明显，攻击并不是直接就是从恶意软件开始的。

我们拿到的恶意软件，可能是鱼叉类钓鱼邮件攻击精准投放，也有可能是水坑类攻击下发。

作为分析人员，除了分析看到的这个恶意样本，也应该关注整个攻击事件和攻击背景的分析。

## 0x01 样本背景

笔者在app.any.run上看到了如下的样本：

![](https://image.3001.net/images/20200830/1598752527.png!small)

样本链接为：<https://app.any.run/tasks/6b9baf15-be08-4446-a07c-b1308130dd01/>

样本md5：183960d220750086595d8591041bd3e7

样本原始名称：ExternalRetrievedPlată restantă.msg

根据多家翻译引擎显示，这个邮件的名称应该是罗马尼亚语。

![](https://image.3001.net/images/20200830/1598752600.png!small)

标题跟付款、金额相关。目前只知道应该是针对罗马尼亚地区的攻击，具体的受害人信息未知。

并且目前该样本VT上没有相关信息，只被投递到了app.any.run。

![](https://image.3001.net/images/20200830/1598752623.png!small)

## 0x02 邮件诱饵

邮件内容如下![](https://image.3001.net/images/20200830/1598752645.png!small)

翻译之后邮件内容如下：

> External：[已检索]剩余付款
>
> 早上好。
>
> 我希望你身体健康，生意兴隆。
>
> 附件中的证据是你方确认的逾期付款，因此我们将通知银行立即付款。
>
> 热烈的问候
>
> 玛丽安娜·普拉斯卡。
>
> 财务总监

这就是一个非常普通的钓鱼邮件，目标没有针对性，应该是批量下发的。

最下面的pdf是一个下载链接，下载地址如下。

hxxp[:]//www.mediafire.com/file/m3mcxobpymp9dy5/Plata+restanta[.]7z/file

![](https://image.3001.net/images/20200830/1598752670.png!small)

需要注意的是，这里的mediafire并不是恶意地址，而是一个免费的托管机构，有点类似于我们所使用的百度云盘

![](https://image.3001.net/images/20200830/1598752691.png!small)

这里很明显，攻击者是将后续的payload放到了第三方平台中，然后通过URL链接去下载回来执行。

这样做的好处是，可以节约一定的攻击成本，且不容易被溯源。

如果没有猜错的话，后面的木马应该也是用的邮件的方式来传数据，也是攻击者免费申请的邮箱。

这个地址还可以正常访问，下载了一个7z文件回来。

![](https://image.3001.net/images/20200830/1598752712.png!small)

解压缩后的文件是一个exe

![](https://image.3001.net/images/20200830/1598752729.png!small)

文件命名为Plata restanta.exe

将罗马尼亚语翻译为中文是：重新付款.exe

![](https://image.3001.net/images/20200830/1598752752.png!small)

从钓鱼邮件来看，钓鱼的手法并不高级，就是靠大众心理，散发这种可能会有人感兴趣的邮件。

## 0x03 第一阶段payload

原始样本是带了一定混淆的，但这里的混淆很好解，就直接de4dot去混淆即可

![](https://image.3001.net/images/20200830/1598752774.png!small)

去混淆之后，样本名还是乱序韩文，但类名和方法名已经显示正常了

![](https://image.3001.net/images/20200830/1598752789.png!small)

这里需要注意，样本执行的时候，首先执行的不是70行的Main函数的内容。

而是95行的public static byte[] Bytes = Class0.smethod_0();

原因很简单，静态变量的初始化会在正式的代码执行之前完成。

所以当程序运行的时候，会首先将各个静态变量赋值，这里95行处，程序就会通过Class0类的Smethod_0方法给Bytes变量赋值。

Smethod_0方法是直接返回了一个大的数组。

![](https://image.3001.net/images/20200830/1598752804.png!small)

分别在95行这里和Main函数里面new GClass0().method_0();进来的地方设置断点

![](https://image.3001.net/images/20200830/1598752825.png!small)

![](https://image.3001.net/images/20200830/1598752837.png!small)

然后程序跑起来，选择不要中断，程序会首先命中95行的断点

![](https://image.3001.net/images/20200830/1598752870.png!small)

![](https://image.3001.net/images/20200830/1598752883.png!small)

F10直接跑过这一行，拿到结果

![](https://image.3001.net/images/20200830/1598752897.png!small)

然后继续F5，让程序中断在smethod_0中

![](https://image.3001.net/images/20200830/1598752912.png!small)

这里可以看到，程序进来之后，直接就是通过一个循环对刚才拿到的Bytes变量进行操作。

![](https://image.3001.net/images/20200830/1598752927.png!small)

操作完成之后，可以看到这类Bytes已经被解密成了一个PE文件，这里将这个PE文件给赋值出来

![](https://image.3001.net/images/20200830/1598752943.png!small)

该文件看起来像是一个C#的DLL。

这里基本可以知道，最外层的这个程序是一个loader。用于解密PE并加载执行。

加载的方式就在smethod_0后面，使用反射委托加载：

![](https://image.3001.net/images/20200830/1598752984.png!small)

## 0x04 第二阶段dll

通过调试，这里可以知道，程序调用dll的时候，会调用awrfsdg类下面的aj方法

![](https://image.3001.net/images/20200830/1598753005.png!small)

加载dll后如下

![](https://image.3001.net/images/20200830/1598753037.png!small)

aj()函数的调用逻辑是这样的。

  1. 通过Abs(-3) 给switch case的初始值设置为3，执行case 3分支
  2. 将num赋值为2，跳转到IL_02重新执行switch ，执行case 0分支。
  3. 跳转到IL_4A执行b.a()
  4. 如果b.a()执行失败，则跳转到最后执行f.a()
  5. 如果b.a()执行成，这num赋值为2，退出程序。

![](https://image.3001.net/images/20200830/1598753064.png!small)

所以这里就是两个关键函数，一个是b.a()

一个是f.a()

程序过来之后，首先会在实例函数这里解密一个字符串，然后等待25s

![](https://image.3001.net/images/20200830/1598753086.png!small)

然后过来，看看b.a()函数

![](https://image.3001.net/images/20200830/1598753103.png!small)

这里的 <Ai>.a是一个解密函数，解密算法如下，这里是解密了exe后缀

![](https://image.3001.net/images/20200830/1598753120.png!small)

然后进入f.a()开始执行关键功能。

首先是解密出了一个资源名称

![](https://image.3001.net/images/20200830/1598753141.png!small)

根据从这个资源中拿到的数据解密得到原始文件的资源名

![](https://image.3001.net/images/20200830/1598753160.png!small)

从原始文件的资源中解密出第二段数据

![](https://image.3001.net/images/20200830/1598753178.png!small)

同时准备释放一个InstallUtil.exe到TEMP目录，这个InstallUtil.exe就是微软官方提供的注册和卸载服务的

![](https://image.3001.net/images/20200830/1598753196.png!small)

解密出最终阶段的payload

![](https://image.3001.net/images/20200830/1598753215.png!small)

最后，程序通过Involve的方式加载到最终木马去。调用InstallUtil.exe创建了一个服务

![](https://image.3001.net/images/20200830/1598753266.png!small)

## 0x05 最终阶段payload

最后的这个payload进来就可以发现是AgentTesla的商业窃密马。

关于AgentTesla网上分析文章很多，这里就大概提一下关键点。

程序进来之后，首先是调用了一个q函数，这个函数没有什么实际用，就是干扰分析的，根据参数计算出一个sleep时间

![](https://image.3001.net/images/20200830/1598753725.png!small)

程序获取了一些基本信息，然后设置了几个Timer

![](https://image.3001.net/images/20200830/1598753766.png!small)

![](https://image.3001.net/images/20200830/1598754045.png!small)

![](https://image.3001.net/images/20200830/1598754060.png!small)

![](https://image.3001.net/images/20200830/1598754077.png!small)

![](https://image.3001.net/images/20200830/1598754091.png!small)

分别对这几个timer执行的函数设置断点，然后跑起来

最后发现程序会在 Passwords这个函数里面，尝试获取浏览器存储的密码。

![](https://image.3001.net/images/20200830/1598754110.png!small)

![](https://image.3001.net/images/20200830/1598754125.png!small)

程序会尝试获取一些主流浏览器中存储的账号密码

![](https://image.3001.net/images/20200830/1598754179.png!small)

直到获取成功，程序才会执行下一步的操作，包括收集用户本地主机的信息，特别是浏览器存储的账号密码，以邮件的方式发送到攻击者的邮箱中。

