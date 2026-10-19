***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 漏洞名称  

> ES File Explorer Open Port Vulnerability - CVE-2019-6447  
>

## 漏洞简介

**ES文件浏览器在启动时创建了一个HTTP服务器，在本地打开了59777端口。攻击者通过构造指定的payload可以获取用户手机文件，安装apk等操作。**

## 影响范围  

4.1.9.7.4 and below（部分版本可能不支持，也可能和应用市场有关）

## 漏洞分析  

从fs0c131y所给出的信息来说CVE-2019-6447影响的ES应用版本为4.1.9.7.4以下，但是在某些版本的应用该漏洞却无法利用，例如从华为和google
play商店下载的ES就无法顺利复现该漏洞，向59777端口发送payload一直会回复500 ERROR报错，下面将详细对该漏洞进行分析。

### 4.1.9.4版本应用分析

以下是选择了4.1.9.4版本的ES文件浏览器进行了分析，该版本ES能够成功利用该漏洞。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548331946_5c49abaa191b8.png!small)

首先对APK解包后发现存在三个DEX文件。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332072_5c49ac283fd2e.png!small)

先简单看了下lib中的库发现应用没有加壳，用grep筛查以下59777确定相关代码可能在classes2.dex中。

把classses2.dex反编译后，全局搜索command发现存在漏洞的类在com/estrongs/android/f/a之中,而触发漏洞的函数为com/estrongs/android/f/a.a。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332159_5c49ac7fdc8be.png!small)

简单看下来a.class,b.class,c.class可能都和该漏洞的服务相关，其中a.class继承了c.class。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332186_5c49ac9a8f529.png!small)

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332192_5c49aca013e9e.png!small)

下面来看下整个漏洞的触发过程，由于混淆代码不管是丢进jeb中还是smali阅读起来都比较费力，为此我们可以先动态的将程序跑一边后记录trace，分析android
trace文件来查看函数调用栈（利用TraceReader读取）。

记录trace的方法如下：

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332250_5c49acda6e893.png!small)

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332349_5c49ad3da46c6.png!small)

在DDMS上成功打开Trace之后，我们就要去构造payload去触发该漏洞，漏洞具体利用payload见github（<https://github.com/fs0c131y/ESFileExplorerOpenPortVuln>）。  

    
    
    curl --header "Content-Type: application/json" --request POST --data "{\"command\":getDeviceInfo}" http://192.168.13 7.10:59777 -vvv

把tracer文件丢到TraceReader查看调用栈，可以发现程序进入com/estrongs/android/f/c$a.run()V来处理了我们的请求，注意这里的类的实例化对象其实是a.class而不是c.class。：

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332420_5c49ad84195df.png!small)

首先接受socket然后读到buffer中提取数据

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332534_5c49adf6c51f0.png!small)

然后判断是不是post数据，如果是post请求则对content-type进行解析，当所有的前置解析完成后最后程序会来到label_189处  

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332550_5c49ae066df6e.png!small)

label_189中，执行了v2_7 = this.a.a_parse_url_other_data(v9, v10, v11, v6,
v7);来进一步解析并执行相应的command。  

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332559_5c49ae0f6900a.png!small)

这里有一个问题，如果JEB直接双击来跟踪函数会跳转到自己类中的函数，而实际真正调用的是a.class(com/com/estrongs/android/f/a)中的函数a_parse_url_other_data（这里我对混淆函数名重命名了实际上原本的函数名是a）。  

下图是JEB错误跳转到函数的位置，实际上我们应该分析的是a.class中的a_parse_url_other_data：

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332578_5c49ae22c2661.png!small)

继续追踪下去来到就来到了我们一开始漏洞触发的地方（com/estrongs/android/f/a.a）：  

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332631_5c49ae5726eb0.png!small)

关于这个地方的分析其实有很多文章以及做过了，这里就不再过多提及了。  

解析对应的command调用对应的功能函数后返回json：

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332803_5c49af0382568.png!small)

最后进入com/estrongs/android/f/c$a.a(Ljava/lang/String;Ljava/lang/String;Ljava/util/Properties;Ljava/io/InputStream;)V将response写回。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332812_5c49af0ccdffc.png!small)

该函数将输出的结果写入到OutputStream中然后将其返回。  
![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548332817_5c49af11eea6e.png!small)

该ES版本整个漏洞的触发流程大致就如上所示。

这里有一个需要注意的地方，如果是不存在漏洞的ES应用v2_7是为null的也就会进入this.a("500 Internal Server Error",
"SERVER INTERNAL ERROR: Serve() returned a null
response.");中，这也是很多应用市场上的ES应用都会到报500错误的原因。

### 4.1.6.6.1版本应用分析

以下将对4.1.6.6.1版本ES文件管理器进行分析，该版本的ES文件管理器没有顺利触发漏洞。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333041_5c49aff185a54.png!small)

直接curl个看看，500报错了。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333090_5c49b022b1432.png!small)

拆包静态看一遍，代码基本上还是在f包中，但是多了很多其他的类，a.class依然是ESHttpServer实现的地方。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333101_5c49b02d9324e.png!small)

![image.pngES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333107_5c49b033d3ab1.png!small)

再curl一个包抓取一下调用栈。

    
    
    curl --header "Content-Type: application/json" --request POST --data "{\"command\":getDeviceInfo}" http://192.168.0. 122:59777 -vvv

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333122_5c49b042872c6.png!small)

错略比对发现在这个版本的ES中多了一些函数，可能是做了某一些的校验逻辑。

静态分析代码，发现前面的逻辑和之前app差不多，但是在执行完com.estrongs.android.f.h.a(Ljava/lang/String;Ljava/util/Properties;)V后又调用了bJ。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333200_5c49b090d613a.png!small)

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333207_5c49b097796f7.png!small)

跟入bJ，bJ验证了了url并且ap.a()方法检测当前环境是否处于WIFI环境下。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333211_5c49b09bd566d.png!small)

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333217_5c49b0a17a448.png!small)

继续往下跟踪，我们来到问题点!bp.q() || !f.e(v8)) && !f.a(v8,
v2_5)这里返回了true导致flag_object为null值所以服务器返回了500。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333231_5c49b0af208fd.png!small)

bq.q()为true或者f.e以及f.a为true才能进入逻辑

跟踪进入bq.q()，要满足bp.p()和cw.e()都为true。

而FexApplication.a().getSystemService("uimode").getCurrentModeType() ==
4成立的时候bp.p()才能为true，根据官方文档4的uimode为UI_MODE_TYPE_TELEVISION。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333248_5c49b0c09f65d.png!small)

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333275_5c49b0db15fef.png!small)

在cw.e中需要满足一定的界面长宽需求

boolean v0_1 = Math.sqrt(Math.pow((((double)v0.heightPixels)) * 1 /
(((double)v0.densityDpi)), 2) + Math.pow((((double)v0.widthPixels)) * 1 /
(((double)v0.densityDpi)), 2)) >= 20 ? true : false;

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333282_5c49b0e215adb.png!small)

而另外的f.e(v8)，f.a(v8, v2_5)函数则负责校验了我们的ip。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333286_5c49b0e6b44c5.png!small)

此外存在另外一种情况是当我们的ip为127.0.0.1时候flag_object能不为null，但首先你要满足v4=null这个先觉条件。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333346_5c49b122df6f8.png!small)

查看v4 = as.bJ(v9)，之前已经说过bJ函数负责校验了url，我们再重新回到bJ发现return
null好像不太可能，v9不管uri如何构造都会以'/'开始。

![ES文件浏览器CVE-2019-6447漏洞分析](https://image.3001.net/images/20190124/1548333455_5c49b18f4382b.png!small)

也就是说在应用市场上的ES版本不管是走if((!bp.q() || !f.e(v8)) && !f.a(v8, v2_5))还是走if(v4 != null
&& as.I(v4) != 0)似乎都不能出发到flag_object = v8_1.a(v9, v10, v11, v6,
v7)的逻辑，这样该漏洞就没法触发，但说不定还有其他的绕过方法，希望大家能够多多补充。  

## 参考资料

>
> [https://www.chainnews.com/articles/873565939043.htm](https://www.chainnews.com/articles/873565939043.htm)
>
>
> [https://www.52pojie.cn/thread-856993-1-1.html](https://www.52pojie.cn/thread-856993-1-1.html)
>
>
> [https://blog.csdn.net/caiqiiqi/article/details/86558862](https://blog.csdn.net/caiqiiqi/article/details/86558862)
>
> <https://bbs.ichunqiu.com/thread-49689-1-1.html>

 ***本文作者：xcy_merlin；转载请注明来自 FreeBuf.COM**

