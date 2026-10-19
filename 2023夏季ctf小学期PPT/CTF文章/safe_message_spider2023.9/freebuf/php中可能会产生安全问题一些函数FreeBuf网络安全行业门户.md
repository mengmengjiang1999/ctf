php中可能会产生安全问题的一些函数

本文章适合正在学习代码审计的朋友，或者准备学习安全的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于php函数的理解，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇有自己的理解，如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏  

## 1：in_array函数  

in_array ：(PHP 4, PHP 5, PHP 7)

功能 ：检查数组中是否存在某个值

定义 ： bool in_array ( mixed $needle , array $haystack [, bool $strict = FALSE ]
)

 **可能会产生安全问题的场景：**

1：对于sql语句参数的检查，如果仅仅使用没有true参数的in_array()函数去检测整数类型，那么很有可能会被绕过

2：利用in_array 函数检测文件后缀

为了便于大家的理解，下面准备几个例子  

Demo1：  

    
    
    <?php
        $xiaobao = $_POST['xiaobao'];
        $dic['xiaobao_items'] = array(0,1,2,3,4,5,6);
        if (in_array($xiaobao,$dic['xiaobao_items']))
        {
            echo 'success1';
        }
        else
        {
            echo 'false1';
        }
    ?>  
    

![image.png](https://image.3001.net/images/20200429/1588148022_5ea9373627103.png!small)这里由于没有对i[n_array
](http://php.net/manual/zh/function.in-array.php)的第三个参数进行设置，导致了数据类型的转换，从而成功绕过了if的判断语句。  

![image.png](https://image.3001.net/images/20200429/1588148087_5ea93777aa43d.png!small)正确使用方法  

Demo2：  

这一次我们设置第三个参数为True，强制让其不进行数据类型转换

    
    
    <?php
        $xiaobao = $_POST['xiaobao'];
        $dic['xiaobao_items'] = array(0,1,2,3,4,5,6);
        if (in_array($xiaobao,$dic['xiaobao_items'],true))
        {
            echo 'success2';
        }
        else
        {
            echo 'false2';
        }
    ?>  
    

![image.png](https://image.3001.net/images/20200429/1588148284_5ea9383c0039f.png!small)  

##
![image.png](https://image.3001.net/images/20200429/1588148169_5ea937c903267.png!small)2：filter_var函数  

filter_var ： (PHP 5 >= 5.2.0, PHP 7)

功能 ：使用特定的过滤器过滤一个变量

定义 ：mixed filter_var ( mixed $variable [, int $filter = FILTER_DEFAULT [,
mixed $options ]] )

 **可能会产生安全问题的场景** ：

1:使用filter_var来判断url，导致伪协议绕过问题

### filter_var绕过

Demo：  

    
    
    <?php
        $xiaobao_url = filter_var($_GET['url'],FILTER_VALIDATE_URL);
        var_dump($xiaobao_url);
        $xiaobao_url1 = htmlspecialchars($xiaobao_url);
        var_dump($xiaobao_url1);
        echo "<a href='$xiaobao_url'>xiaobao</a>";
    ?>  
    

![image.png](https://image.3001.net/images/20200429/1588148853_5ea93a75232fd.png!small)![image.png](https://image.3001.net/images/20200429/1588148857_5ea93a798c1b4.png!small)这里的//是为了满足filter_var($_GET['url'],FILTER_VALIDATE_URL);对于url的判断，但是在js当中//表示注释，因此需要加入%0a，利用换行符去绕过注释的限制，同时对%进行url编码。最后的payload就是  

    
    
    http://127.0.0.1/testphp/flitervar.php?url=javascript://xiaobao%250aalert(1)

这对XSS漏洞，最好的解决方案就是过滤关键词，将特殊字符进行HTML实体编码替换，这个网上已经有提供了很多防御的方法了。

##  **3：** parse_str()函数

parse_str

功能 ：parse_str的作用就是解析字符串并且注册成变量，它在注册变量之前不会验证当前变量是否存在，所以会直接覆盖掉当前作用域中原有的变量。

定义 ：void parse_str( string $encoded_string [, array &$result ] )

如果 encoded_string 是 URL 传入的查询字符串（query string），则将它解析为变量并设置到当前作用域（如果提供了 result
则会设置到该数组里 ）。

 **可能会产生安全问题的场景：**

1：parse_str函数导致的变量覆盖问题

###  **parse_str** **函数导致的变量覆盖问题**

Domo1：  

    
    
    <?php
     $xiaobao = "xiaobao";
     parse_str('xiaobao=baobao');
     var_dump($xiaobao);
     ?>  
    

![image.png](https://image.3001.net/images/20200429/1588149216_5ea93be0278c1.png!small)![image.png](https://image.3001.net/images/20200429/1588149220_5ea93be488bcf.png!small)在调试过程我们可以清楚的看到之前定义的$xiaoboa变量被后面的parse_str函数中的给覆盖掉了。

![image.png](https://image.3001.net/images/20200429/1588149236_5ea93bf40821f.png!small)再来看个例子加深理解  

Domo2：  

    
    
    <?php
        $xiaobao = 'fail';
        parse_str($_GET['baobao']);
        echo $xiaobao;
    ?>  
    

![image.png](https://image.3001.net/images/20200429/1588149260_5ea93c0c49501.png!small)![image.png](https://image.3001.net/images/20200429/1588149264_5ea93c109129c.png!small)![image.png](https://image.3001.net/images/20200429/1588149269_5ea93c15648f5.png!small)实际上php中造成变量覆盖的情形远不止这么一种，大家下去可以自行研究。  

## 4：strpos()函数  

strpos — 查找字符串首次出现的位置

作用：主要是用来查找字符在字符串中首次出现的位置。

结构：int strpos ( string $haystack , mixed $needle [, int $offset = 0 ] )

 **可能会产生安全问题的场景：**

1：利用数组绕过判断条件

2：第一次匹配字符下标为0去绕过判断条件

###  **利用数组绕过判断条件**

Demo1：  

    
    
    <
    ?php
        $flag = "{xiaobao success}";
            if(strpos($_GET["url"],"secxiaobao") !== FALSE)
        {
            echo $flag;
        }
        else
        {
            echo 'fail';
        }
    ?>

strpos()函数需要的是一个字符串,如果传一个数组给它会发生什么呢？strpos()会出错返回null,而判断条件null!==false,所以符合我们的要求。成功得到flag。  

![image.png](https://image.3001.net/images/20200429/1588151497_5ea944c987070.png!small)![image.png](https://image.3001.net/images/20200429/1588151501_5ea944cd72c3f.png!small)  

###  **利用匹配下标去绕过**

Demo2：  

这次我们再看另一种绕过情况，先来看一下strpos()正常使用方法  

    
    
    <?php
    echo strpos("I love liebao, I love liebao too!","liebao");
    ?>  
    

执行结果为7，也就是去匹配liebao字符串首次出现的位置下标。  

我们试一下下标不为0的情况

    
    
    <?php
        $flag = "{xiaobao success}";
        $a = strpos($_GET["url"],"secxiaobao");
        if(!$a == true)
        {
            echo $flag;
        }
        else
        {
            echo 'fail';
        }
    ?>
    
    
    http://127.0.0.1/testphp/strops.php?url=123secxiaobao

![image.png](https://image.3001.net/images/20200429/1588151711_5ea9459f131f1.png!small)![image.png](https://image.3001.net/images/20200429/1588151714_5ea945a26a68a.png!small)看到获得的下标为3，非运算之后当然和true不相等了  

那么，首次出现位置的下标为0又会发生什么？  

    
    
    http://127.0.0.1/testphp/strops.php?url=secxiaobao  
    

![image.png](https://image.3001.net/images/20200429/1588151738_5ea945ba95e2c.png!small)![image.png](https://image.3001.net/images/20200429/1588151742_5ea945be363de.png!small)这里获得的下标为0，非运算之后等于true，成功的输出flag。  

## 5：MD5函数

提到php中的MD5函数小豹会想起几个字符串，ffifdyop和129581926211651571912466741651878684928，QNKCDZO，240610708

这些字符串有什么神奇的地方？小豹先留个悬念，我们接着往下看

首先是php中MD5函数官方释义

md5 — 计算字符串的 MD5 散列值

string md5 ( string $str [, bool $raw_output = false ]）

 **可能会产生安全问题的场景：**

1：MD5函数true绕过

2：MD5函数==弱比较绕过

###  **MD5函数true绕过**

Demo1：  

    
    
    <?php
    $password = $_POST['password'];
    $sql = "SELECT * FROM xiaobao WHERE username = 'baobao' and password  = '".md5($password,true)"'";
    $result = mysql_query($link,$sql);
    	if(mysql_num_rows(($result)>0){
    		echo 'success';
    	}
    	else{
    		echo 'login fail'
    	}
    ?>  
    

这部分代码是模拟对数据库进行操作的真实情景。

从代码中我们可以看出，只有查询后的sql数据不为空也就是大于0的时候，才会输出success。同时这部分代码里出现了需要关注的MD5函数，当$raw_output设置为true的时候，md5函数会返回前16字节长度的原始二进制，并会将二进制转换成字符串。而在这个转换为字符串的过程中是否可能带来问题？例如原始的二进制转换为字符串后会不会影响本来的sql语句？答案当然是会的，这里已经有大佬帮我们找到了，小豹在前边也提到了，不过这次可以了解他们的真实面貌：

    
    
    ffifdyop
    129581926211651571912466741651878684928  
    

接下来看下实际效果：  

    
    
    <?php
    	$password = md5("ffifdyop",true);
    	echo $password;
    	$password1 = md5("129581926211651571912466741651878684928",true);
    	echo "</br>";
    	echo $password1;
    	$sql = "SELECT * FROM xiaobao WHERE username = 'baobao' and password  = '$password'";
    	$sql1 = "SELECT * FROM xiaobao WHERE username = 'baobao' and password  = '$password1'";
    	var_dump($sql);
    	var_dump($sql1);
    ?>  
    

![image.png](https://image.3001.net/images/20200429/1588151911_5ea94667bd3d6.png!small)回到上面的问题，我们的sql语句变成了  

    
    
    SELECT * FROM xiaobao WHERE username = 'baobao' and password = ''or'xxxx'  
    

前边的条件执行后会与后边的or 'xxxx'进行或运算，导致整个where条件为真，从而绕过了密码的限制。  

  

###  **MD5函数==弱比较绕过**

Demo1：  

    
    
    <?php
    $flag = 'flag{xiaobao}';
    $p = '/^[A-Za-z0-9]{6,12}$/';
    $a = $_POST['password'];
    if (preg_match($p, $_POST['password'])) {
    if(md5($_POST['password'])=="0")
        {
            echo $flag;
        }
        else
        {
            echo 'fail';
        }
    }
    else
    {
        echo 'Password format is wrong';
    }
    ?>  
    

从上面的代码中可以看出对post形式获取到的password进行了限制，只能是6-12位由数字和大小写字母组成的字符串。对满足条件的参数值进行MD5

加密，加密后与字符0进行比较，如果相等，就会输出flag。

    
    
    http://127.0.0.1/testphp/MD5test.php
    Post数据分别为：
    password =240610708
    password =QNKCDZO  
    

![image.png](https://image.3001.net/images/20200429/1588151997_5ea946bdbebfb.png!small)![image.png](https://image.3001.net/images/20200429/1588152001_5ea946c1a7409.png!small)

为什么MD5加密后的这两个特殊字符会与字符0相等？

来看一下这两个特殊字符串MD5加密后的样子

![image.png](https://image.3001.net/images/20200429/1588152011_5ea946cb93b79.png!small)因为==对比的时候会进行数据转换，0eXXXXXXXXXX
被转换成了字符0。  

