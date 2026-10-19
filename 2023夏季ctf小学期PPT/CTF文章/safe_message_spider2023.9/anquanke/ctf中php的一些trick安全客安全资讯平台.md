# ctf中php的一些trick

阅读量 **326494**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-23 15:30:17

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01494c1e0de499424b.png)

获取http请求的变量值过程

对于php获取http请求的值的变量`$_GET,$_POST,$_COOKIE,$_SERVER,$_ENV,$_REQUEST,$_FILES`，在初始化请求时就注册了这么多的超全局变量
，这里从php的源代码就可以看出：

![](https://p2.ssl.qhimg.com/t01a99bca56a40ec553.png)

在看看php的官方文档怎么说

![](https://p3.ssl.qhimg.com/t01d543ecd32021c77f.png)

这里重点关照一下`$_REQUEST`，明明写的默认是包含`$_GET，$_POST 和
$_COOKIE`的数组，但是实际上却是只包含了`$_GET，$_POST`

![](https://p3.ssl.qhimg.com/t0159428e1bea4a3aef.png)

`<?php  
var_dump($_GET);  
var_dump($_POST);  
var_dump($_COOKIE);  
var_dump($_REQUEST);  
?>  
`

![](https://p3.ssl.qhimg.com/t011a561b4038e5325b.png)

这是为什么呢？底层代码也解释了：

![](https://p4.ssl.qhimg.com/t01876e316f2d209b61.png)

<a name=”然后看看php.ini里面的默认值是多少，由于首先会选择赋值为`request_order`的值，所以就只有GP了”
class=”reference-link”>然后看看php.ini里面的默认值是多少，由于首先会选择赋值为`request_order`的值，所以就只有GP了

![](https://p4.ssl.qhimg.com/t01144d5439413f3649.png)

<a
name=”好了，现在就明白了`$_REQUEST`的值是根据`request_order`的值来先后合并的，所以这里就会出现`$_REQUEST`里面的key先被`$_GET`赋值，再被`$_POST`赋值，这样就post的值就覆盖了get在request里面注册的值了，这个点印象中已经考过几次了”
class=”reference-link”>好了，现在就明白了`$_REQUEST`的值是根据`request_order`的值来先后合并的，所以这里就会出现`$_REQUEST`里面的key先被`$_GET`赋值，再被`$_POST`赋值，这样就post的值就覆盖了get在request里面注册的值了，这个点印象中已经考过几次了

![](https://p0.ssl.qhimg.com/t01d62981f9fc03d5ce.png)

现在继续看看php对于`$_GET，$_POST 和
$_COOKIE`的处理部分是在`php_register_variable_ex`这里主要关注3个地方：

![](https://p2.ssl.qhimg.com/t010635297d4e2918c5.png)

![](https://p0.ssl.qhimg.com/t01c897356485097667.png)

![](https://p5.ssl.qhimg.com/t017444703d917123d9.png)

那么怎么才能获取到`$_GET`真正的变量名呢？那就是通过`$_SERVER`来获取

![](https://p3.ssl.qhimg.com/t015740aa656610bc9a.png)

post的可以通过伪协议来得到真正的变量名，`php://input`

php读取文件或者获取文件的特性

<a
name=”先说一下php底层对于处理获取文件数据流是用的2个不同的方法，所以导致了`readfile("/e/../../etc/passwd")`可以成功，而`is_file("/e/../../etc/passwd")`为false”
class=”reference-link”>先说一下php底层对于处理获取文件数据流是用的2个不同的方法，所以导致了`readfile("/e/../../etc/passwd")`可以成功，而`is_file("/e/../../etc/passwd")`为false

![](https://p4.ssl.qhimg.com/t015eee58e3e1faeef7.png)

![](https://p0.ssl.qhimg.com/t01572bccea48b0449b.png)

![](https://p3.ssl.qhimg.com/t013780de4c551a39ac.png)

![](https://p5.ssl.qhimg.com/t017e5273aca30bbd5c.png)

![](https://p4.ssl.qhimg.com/t01cbf8bcea4c406ea6.png)

然后就是php的伪协议了：`php://stdin,php://stdout,php://stderr,php://input,php://output,php://fd,php://memory,php://temp,php://filter`，这些里面最常用到的就是`php://filter`了，关于这个的一系列trick网上一大把，这里主要讲一下`include,require,include_once,require_once`，这4个语法关键词实际上都是调用的同一个函数，只是选择的模式不同

![](https://p5.ssl.qhimg.com/t0132771074388a0964.png)

![](https://p5.ssl.qhimg.com/t0104d5fa6ca6b39e63.png)

可以发现include和readfile这些文件读取的函数又是走的不同路线，那这样会不会出现什么差异呢？跟着源码看了一下发现，是否解析`data://和http://`实现的文件包含关键代码如下：

` if (wrapper && wrapper->is_url &&  
(options & STREAM_DISABLE_URL_PROTECTION) == 0 &&  
(!PG(allow_url_fopen) ||  
(((options & STREAM_OPEN_FOR_INCLUDE) ||  
PG(in_user_include)) && !PG(allow_url_include)))) {  
if (options & REPORT_ERRORS) {  
/* protocol[n] probably isn't '\0' */  
if (!PG(allow_url_fopen)) {  
php_error_docref(NULL, E_WARNING, "%.*s:// wrapper is disabled in the server
configuration by allow_url_fopen=0", (int)n, protocol);  
} else {  
php_error_docref(NULL, E_WARNING, "%.*s:// wrapper is disabled in the server
configuration by allow_url_include=0", (int)n, protocol);  
}  
}  
return NULL;  
}  
`

拆开来理解一下，第一层是`wrapper && wrapper->is_url`就是判断这个数据流是否有url模式，第二层`(options &
STREAM_DISABLE_URL_PROTECTION) ==
0`通过运算判断数据流是否是url，第三层`!PG(allow_url_fopen)`判断php的配置里面是否启用了`allow_url_fopen`，`((options
& STREAM_OPEN_FOR_INCLUDE)
||PG(in_user_include))`大概是判断数据流是不是用于include，`!PG(allow_url_include)`判断php是否配置了`allow_url_include`，所以可以发现这里对include和readfile这些文件操作函数处理流程是不一样的，写个测试代码：

`<?php`

readfile($_GET[‘file’]);  
include $_GET[‘file’];  
?>

![](https://p1.ssl.qhimg.com/t01c3f7233ef6b82099.png)

可以发现爆了3个错误，第一个是说配置文件里面禁用了data的数据流，第二是不能打开data的数据流，第三个是显示的不能打开文件，在include_path下面没有发现文件，所以就很明显在linux下面可以利用readfile不能读取文件，而include可以包含文件的特性了

![](https://p3.ssl.qhimg.com/t01deec36809d813482.png)

![](https://p1.ssl.qhimg.com/t01a438e533a85e2ed1.png)

![](https://p4.ssl.qhimg.com/t011fe87d2e606a178c.png)

![](https://p2.ssl.qhimg.com/t01a155bb483009cbf0.png)

phar的一些特性和底层处理可以参考(因为之前和师傅套路过，所以就不在写了):

<https://guokeya.github.io/post/uxwHLckwx/>

unserialize的一些特性

先看看文档，这里写了就接受一个字符串的参数，但是实际上是2个参数，还有一个callback的例子也不错

![](https://p1.ssl.qhimg.com/t012d4843b8c021a33b.png)

![](https://p3.ssl.qhimg.com/t018b005f3d3fb6ce60.png)

然后来看看php的源码怎么写的吧

![](https://p3.ssl.qhimg.com/t016602a3961d45eb54.png)

![](https://p2.ssl.qhimg.com/t011052ea0d73060bf3.png)

测试代码：

`<?php  
class A{  
function __destruct(){  
echo "ok\n";  
}  
}  
var_dump(unserialize('O:1:"A":0:{}',["allowed_classes"=>true]));  
var_dump(unserialize('O:1:"A":0:{}',["allowed_classes"=>false]));  
var_dump(unserialize('O:1:"A":0:{}',["allowed_classes"=>["A"]]));  
var_dump(unserialize('O:1:"A":0:{}',["allowed_classes"=>["B"]]));  
?>  
`

![](https://p2.ssl.qhimg.com/t01e74ff92efe89e2e5.png)

<a
name=”然后看看php处理反序列化的细节吧，具体流程在`php_var_unserialize`里面，而且可以发现反序列化失败后直接抛的error，而不是异常，抛error就不会继续后面的代码了”
class=”reference-link”>然后看看php处理反序列化的细节吧，具体流程在`php_var_unserialize`里面，而且可以发现反序列化失败后直接抛的error，而不是异常，抛error就不会继续后面的代码了

![](https://p4.ssl.qhimg.com/t011ced6ddc8d69e748.png)

这个开启动态调试方便一点，首先配置vscode解析.re后缀的为c

![](https://p1.ssl.qhimg.com/t01cadc48316406c9aa.png)

![](https://p3.ssl.qhimg.com/t01cb9016440aa703ea.png)

先看看解析的时候，可以发现开始对”和:作为结尾进行了验证，但是取出类名后对于:和{没有验证，所以可以直接不写，也可以成功反序列化

![](https://p5.ssl.qhimg.com/t01a34581d8ba7de598.png)

![](https://p3.ssl.qhimg.com/t01dbf2c6fa304b4b7f.png)

`<?php  
class A{  
function __destruct(){  
echo "ok";  
}  
}  
unserialize('O:1:"A":0:{}');  
unserialize('O:1:"A":0aa}');  
?>  
`

![](https://p3.ssl.qhimg.com/t01c47810da4cecfd56.png)

然后看看字符串的s判断吧，就验证了后面2个字符是不是”和;所以字符这里就没有什么问题了

![](https://p0.ssl.qhimg.com/t01be49850568e6937c.png)

然后就是字符串的S时判断是先经过处理后在进行判断的

![](https://p5.ssl.qhimg.com/t016300472add2d5334.png)

然后看看`unserialize_str`的主要处理逻辑，其实这里就是为了把`\74`变为t，其实大概的思想就是利用16进制和2进制的特性，因为16进制的第一个数字只影响对应二进制的前4位，第二个数字就只影响后4位

![](https://p5.ssl.qhimg.com/t0100b6fec7514e7294.png)

<a
name=”其他几个类型的判断也没有什么特别的了，然后就是在类解析的最后还有一个解析类似魔术方法的东西`__unserialize`，而且当`__unserialize`存在时`__wakeup`是不会触发的”
class=”reference-link”>其他几个类型的判断也没有什么特别的了，然后就是在类解析的最后还有一个解析类似魔术方法的东西`__unserialize`，而且当`__unserialize`存在时`__wakeup`是不会触发的

![](https://p4.ssl.qhimg.com/t0158f49e5b57991d26.png)

![](https://p1.ssl.qhimg.com/t01944013b55f66dfba.png)

<a
name=”然后就是`__destruct`的魔术方法调用了，即使反序列化失败，但是还是会触发cleanup，来进行清理，所以也就可以触发`__destruct`的魔术方法了”
class=”reference-link”>然后就是`__destruct`的魔术方法调用了，即使反序列化失败，但是还是会触发cleanup，来进行清理，所以也就可以触发`__destruct`的魔术方法了

![](https://p2.ssl.qhimg.com/t017cb23b952abc71df.png)

还有就是当`__wakeup`里面出现了zend级别的错误，`__destruct`也不会触发了

![](https://p2.ssl.qhimg.com/t01bb149a22fe27f466.png)

所以我们也就可以适当的利用unserialize的报错来即执行了`__destruct`，但是又不执行后面的代码

`<?php  
class A{  
public $ttt;  
function __destruct(){  
echo "destruct";  
}  
}`

unserialize(‘a:2:{i:0;O:1:”A”:1:{s:3:”ttt”;N;}i:1;O:3:”PDO”:0:{}}’);  
readfile(“/etc/passwd”);  
?>

![](https://p3.ssl.qhimg.com/t0135510ed6cc4882f4.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **123qwer** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/244494](/post/id/244494)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=PCGUeYx0xXvaXeCPiceiauNA&s=40&t=1557114336)
123qwer

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

