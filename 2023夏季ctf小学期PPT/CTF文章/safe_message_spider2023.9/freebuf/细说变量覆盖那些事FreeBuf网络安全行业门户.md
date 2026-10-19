**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

## 前言

最近在挖洞和看一些`ctf`题目中可以看到一些变量覆盖的知识点，之前对这个方面学习的有点不全面，虽然网上有这方面的文章，但是感觉讲的不是很全面，所以就决定写一篇文章来总结这方面的知识。

本文涉及相关实验：PHP安全之变量覆盖漏洞【https://www.hetianlab.com/expc.do?ec=ECID3ec0-232d-4e11-8cb0-52a8620c51ee&pk_campaign=freebuf-wemedia】（通过该实验，详细了解PHP中变量覆盖漏洞相关的知识。如：$$使用不当，extract()函数使用不当，parse_str()函数使用不当，import_request_variables()使用不当，开启了全局变量注册等。）

## 漏洞原理

变量覆盖是指可以用自己的传参值代替程序原有的变量值。

## 漏洞寻找

例如下面的函数或者语法使用不当时就会出现漏洞。

> `$$`
>
> `extract()`
>
> `parse_str()`
>
> `import_request_variables()`
>
> `mb_parse_str`
>
> `register_globals`

## 漏洞解析

这里先分析函数，再分析漏洞。

### `extract()`

 **原理**

`extract()`函数从数组中将变量导入到当前的符号表。

例如

    
    
    <?php  
    $a = "eeknight";  
    $my_array = array("a" => "C","b" => "T", "c" => "F");  
    extract($my_array);  
    echo "\$a = $a; \$b = $b; \$c = $c";  
    ?>  
    ​  
    输出：  
    $a = C; $b = T; $c = F

 **攻击手段**

这里先举个例子

    
    
    <?php  
    $a="echo 'eeknight';";  
    echo $a;  
    echo "\n";  
    eval($a);  
    ?>  
    输出：  
    echo 'eeknight';  
    eeknight

在上面双引号包裹了单引号，然后通过`eval`去利用他，就可以直接输出单引号里的东西了。

为什么要说这个东西，因为当你单引号里的东西可以被利用，是不是就可以写什么执行什么了。

怎么利用呢，这时候刚才介绍的`extract`就发挥作用了。

把上面的例子简单改一下

    
    
    <?php  
    $a="echo 'eeknight';";  
    extract($_GET);  
    eval($a);  
    ?>

![headImg.action?news=bcc496fd-da63-4309-9888-9d8dc3607974.png](https://image.3001.net/images/20210326/1616747496_605d9be8625bed45d573c.png!small)

### `$$`

 **原理**

`$$`产生的漏洞主要是因为`foreach`遍历数组的值，然后将获取的数组键名作为变量，数组中的值作为变量的值。

在这先简单介绍一下`foreach`和`$$`。

`foreach`循环只适用于数组，并用于遍历数组中的每个键/值对。

    
    
    <?php   
    $colors = array("red","green","blue","yellow");   
    ​  
    foreach ($colors as $value) {  
    echo "$value \n";  
    }  
    ?>  
    输出：red  
    green  
    blue  
    yellow 

`$$`这里举个栗子

在PHP中，`$var`表示一个名为`var`的普通变量，它存储字符串、整数、浮点等任何值。而`$$var`是一个引用变量，用于存储`$var`的值。

在我看来就是套娃。

![headImg.action?news=5dd746dc-b9a2-49a6-8fbc-1d85f457d0d2.png](https://image.3001.net/images/20210326/1616747497_605d9be92d1a04c16bfe9.png!small)

    
    
    <?php  
    $var = "ee";  
    $$var = "eeknight";  
    echo $var ;  
    echo "\n";  
    echo $$var;  
    echo "\n";  
    echo "$ee";  
    ?>  
    输出：ee  
    eeknight  
    eeknight

### `parse_str()`

`parse_str()`把查询字符串解析到变量中。

    
    
    parse_str(string,array)  
    string  必需。规定要解析的字符串。  
    array   可选。规定存储变量的数组的名称。该参数指示变量将被存储到数组中。
    
    
    <?php  
    parse_str("name=eeknight&age=20");  
    echo $name."\n";  
    echo $age;  
    ?>  
    输出：eeknight  
    20

 **攻击方式**

通过上面的例子，可以想到，如果`parse_str()`括号是`GET`,`PSOT`等之类的，我们是不是就可以直接执行我们要的函数。

![headImg.action?news=16c78c87-79fe-4b34-bc63-5b9ff963294c.jpg](https://image.3001.net/images/20210326/1616747497_605d9be9ed82872264a7c.jpg!small)

### `mb_parse_str`

`mb_parse_str`— 解析 GET/POST/COOKIE 数据并设置全局变量

具体的用法和上面的`parse_str()`一样。

这里就不多说明了。

### `import_request_variables()`

`import_request_variables()`函数将 GET／POST／Cookie 变量导入到全局作用域中。

![headImg.action?news=deeff8f5-fc1a-4828-a91a-4cc5bafa8a68.png](https://image.3001.net/images/20210326/1616747498_605d9bea8d4e67ddd9f38.png!small)

    
    
    <?php  
    import_request_variables("gP", "ee_");  
    echo $ee_knight;  
    ?>

![headImg.action?news=aff7cb83-e35f-429d-ad5c-87e9fc59ac90.png](https://image.3001.net/images/20210326/1616747499_605d9beb1d0bad73691d8.png!small)

 **攻击方式**

只要利用了这个函数，就可以直接对里面的变量进行赋值。

### `register_globals`

`register_globals`的意思就是注册为全局变量

当`php.ini`中`register_globals`=`On`时，传递过来的值会被直接注册为全局变量，当为`off`时，需要到特定的数组中去得到

例子

    
    
    <?php  
    echo "Register_globals: ".(int)ini_get("register_globals")."<br/>";  
      
    if ($auth){  
    echo "hello!";  
    }  
    ?>

#### ON

![headImg.action?news=94c102e2-58ba-473b-9d93-6a13f1138098.png](https://image.3001.net/images/20210326/1616747499_605d9bebba85d91758659.png!small)

 **OFF**

![headImg.action?news=e3bfeb5e-781f-441d-a755-375fcc332ab6.png](https://image.3001.net/images/20210326/1616747500_605d9bec7e013b7dc8cde.png!small)

这里`ON-->OFF`的转换时记得重启一下`apache`。

## 一些附加说明

1.为什么`echo "\$a = $a; \$b = $b; \$c = $c";`这里要加上`\`呢

解：这些斜杠的的意思就是，让后面的变量失去意义。那么写的是什么就是什么。

`2.parse_str()`

`php.ini`文件中的`magic_quotes_gpc`设置影响该函数的输出。如果已启用，那么在`parse_str()`解析之前，变量会被`addslashes()`转换。

`3.import_request_variables()`

该函数在最新版本的 PHP 中已经不支持。

支持的版本：PHP 4 >= 4.1.0, PHP 5 < 5.4.0。

`4.register_globals`

`register_globals`从php5.3.0起废弃，并从php5.4.0时移除。

## 漏洞防御

`1.addslashes()`

`addslashes()`在每个双引号（"）前添加反斜杠。

2.使用原始变量，不进行变量注册；

3.验证变量存在，如果一定要进行变量注册，可以在注册变量前先判断变量是否存在。

