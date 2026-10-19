## 0x00 前言

    
    
    前段时间在github上发现dedeCMS又爆出了CVE-2022-23337漏洞，于是就赶快去复现了一下，该漏洞是由于后台某处功能点验证存在缺失导致的。接下来我们去分析下漏洞产生的原理。  
    DedeCms(织梦CMS)是一款国内流行的内容管理系统,在DeDeCMS v5.7.87版本article_coonepage_ruel.php存在SQL注入漏洞，该漏洞于2022.1.18日公布于CVE官网，并且官网已发布漏洞补丁。 

## 0x01 漏洞分析

漏洞点在于`article_coonepage_ruel.php`文件中最开始包含了`config.php`文件这个文件中主要是对登录状态以及csrf、xss等进行判断过滤，而在该文件的最上面又包含了`include/common.inc.php`文件。  

![](https://image.3001.net/images/20220901/1662014331_6310537bb74088ca9d377.png!small)![](https://image.3001.net/images/20220901/1662014359_63105397c6016eecdb0a5.png!small)

在`common.inc.php`中108行接收我们通过GET、POST、COOKIE传递的参数，并将参数带入到`CheckRequest()`、`_RunMagicQuotes()`函数中进行检测。

在`CheckRequest()`函数中检测传入的参数值是否为cfg、GLOBALS、GET等，如果是直接退出。

![](https://image.3001.net/images/20220901/1662014465_6310540118119d41b9b0a.png!small)而在`_RunMagicQuotes()`函数中70行处，首先使用`get_magic_quotes_gpc()`检测php.ini中
`magic_quotes_gpc`是否开启((当 magic_quotes_gpc 打开时，所有的 ‘ (单引号), ” (双引号), (反斜线) and
空字符会自动转为含有反斜线的溢出字符。 )，如不开启则在82行处，使用`addslashes()`函数对 ‘ (单引号), ” (双引号),
(反斜线)进行转义。

![](https://image.3001.net/images/20220901/1662014544_63105450aef899fac990e.png!small)返回来查看存在漏洞的`article_coonepage_ruel.php`文件，`$ids`参数是通过36行的else
if语句这里进入的，想要触发SQL注入，这里的`$action ==
'del'`，在38行处，判断传入的参数是多个还是一个，如果是一个则走if，如果是多个则走else。

![](https://image.3001.net/images/20220901/1662014584_63105478cc206826c1b20.png!small)

通过上面分析单双引号将被转义，所以走if的话不能将SQL语句逃逸出来，就不能造成SQL注入，只能走42行的else。

![](https://image.3001.net/images/20220901/1662014689_631054e18832f52dcf5ac.png!small)else中由于没有对`()`进行过滤我们就可以成功闭合`)`并使用#注释掉后面的`)`，从而执行sleep()。

![](https://image.3001.net/images/20220901/1662014721_631055017c8b14a935281.png!small)`ExecuteNoneQuery()`函数将一些列mysqli()封装起来包括数据库连接、选择数据库以及一些SQL检测，方便直接调用。最后在227行处通过mysqli_query()执行我们传入的SQL语句，造成SQL注入。

![](https://image.3001.net/images/20220901/1662014753_63105521cbef40d4b5751.png!small)![](https://image.3001.net/images/20220901/1662014772_6310553415890a5111522.png!small)

## 0x02 漏洞利用

路由：

    
    
    dede/article_coonepage_rule.php

通过上述分析，我们只有删除多个才能触发else，点击删除burp抓包。

![](https://image.3001.net/images/20220901/1662014915_631055c3bf33ee52e04e9.png!small)paylaod：

    
    
    15,14)%20and%20sleep(3)%23

![](https://image.3001.net/images/20220901/1662014981_631056056569c31f88422.png!small)

## 0x03 总结

    
    
    对于开发而言，由于后台的功能点更为繁杂，可能在某些功能点处就忘记其安全性的问题，没有做到很好的过滤或者说压根就没有做过滤。站在攻击者的角度就可以很好利用这一点来对某些系统进行攻击。

