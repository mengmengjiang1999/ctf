**作者：启明星辰ADLab  
公众号：<https://mp.weixin.qq.com/s/DGWuSdB2DvJszom0C_dkoQ>**

### **漏洞介绍**

2019年1月11日，ThinkPHP团队发布了一个补丁更新，修复了一处由于不安全的动态函数调用导致的远程代码执行漏洞。该漏洞危害程度非常高，默认条件下即可执行远程代码。启明星辰ADLab安全研究员对ThinkPHP的多个版本进行源码分析和验证后，确认具体受影响的版本为ThinkPHP5.0-5.0.23完整版。

### **漏洞复现**

本地环境采用ThinkPHP 5.0.22完整版+PHP5.5.38+Apache进行复现。安装环境后执行POC即可执行系统命令，如图：

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44B7.tmp.jpg-w331s)

### **漏洞分析**

以官网下载的5.0.22完整版进行分析， **首先定位到漏洞关键点：**

thinkphp/library/think/Request.php:518

    
    
      public function method($method = false)
        {
            if (true === $method) {
                // 获取原始请求类型
                return $this->server('REQUEST_METHOD') ?: 'GET';
            } elseif (!$this->method) {
                if (isset($_POST[Config::get('var_method')])) {
                    $this->method = strtoupper($_POST[Config::get('var_method')]);
                    $this->{$this->method}($_POST);
                } elseif (isset($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE'])) {
                    $this->method = strtoupper($_SERVER['HTTP_X_HTTP_METHOD_OVERRIDE']);
                } else {
                    $this->method = $this->server('REQUEST_METHOD') ?: 'GET';
                }
            }
            return $this->method;
        }

在method函数的第二个if分支中，引入了一个外部可控的数据`$_POST[Config::get[‘var_method’]`。而`var_method`的值为`_method`。

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44B8.tmp.jpg-w331s)

取得`$_POST[‘_method’]`的值并将其赋值给`$this->method`，然后动态调用`$this->{$this->method}($_POST)`。这意味着攻击者可以调用该类任意函数并以`$_POST`作为第一个参数。如果动态调用`__construct`函数，则会导致代码执行。

Request类的`__construct`函数如下：

    
    
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

由于`$options`参数可控，攻击者可以覆盖该类的filter属性、method属性以及get属性的值。而在Request类的param函数中：

    
    
    public function param($name = '', $default =  null, $filter = '')
        {
             if (empty($this->mergeParam)) {
                 $method = $this->method(true);
                 // 自动获取请求变量
                 switch ($method) {
                    case 'POST':
                        $vars =  $this->post(false);
                        break;
                    case 'PUT':
                    case 'DELETE':
                    case 'PATCH':
                        $vars =  $this->put(false);
                        break;
                    default:
                        $vars = [];
                 }
                 // 当前请求参数和URL地址中的参数合并
                 $this->param      = array_merge($this->param,  $this->get(false), $vars, $this->route(false));
                 $this->mergeParam = true;
             }
             if (true === $name) {
                 // 获取包含文件上传信息的数组
                 $file = $this->file();
                 $data = is_array($file) ? array_merge($this->param, $file) :  $this->param;
                 return $this->input($data, '', $default, $filter);
             }
             return $this->input($this->param, $name, $default, $filter);
        }

当`$this->mergeParam`为空时，这里会调用`$this->get(false)`。跟踪`$this->get`函数：

    
    
     public  function get($name = '', $default = null, $filter = null)
        {
             if (empty($this->get)) {
                 $this->get = $_GET;
             }
             if (is_array($name)) {
                 $this->param      = [];
                 return $this->get = array_merge($this->get, $name);
             }
             return  $this->input($this->get, $name, $default, $filter);
        }

该函数末尾调用了`$this->input`函数，并将`$this->get`传入，而`$this->get`的值是攻击者可控的。跟踪`$this->input`函数：

    
    
    public  function input($data = [], $name = '', $default = null, $filter = '')
        {
             if (false === $name) {
                 // 获取原始数据
                 return $data;
             }
             $name = (string) $name;
            if ('' != $name) {
                 // 解析name
                 if (strpos($name, '/')) {
                    list($name, $type) =  explode('/', $name);
                 } else {
                    $type = 's';
                 }
                 // 按.拆分成多维数组进行判断
                 foreach (explode('.', $name) as $val) {
                    if (isset($data[$val])) {
                        $data = $data[$val];
                    } else {
                        // 无输入数据，返回默认值
                        return $default;
                    }
                 }
                 if (is_object($data)) {
                    return $data;
                 }
             }
    
             // 解析过滤器
            $filter = $this->getFilter($filter,  $default);
    
             if (is_array($data)) {
                 array_walk_recursive($data,  [$this, 'filterValue'], $filter);
                 reset($data);
             } else {
                 $this->filterValue($data, $name, $filter);
             }
    
             if (isset($type) && $data !== $default) {
                 // 强制类型转换
                 $this->typeCast($data, $type);
             }
             return $data;
        }

该函数调用了`$this->getFileter`取得过滤器。函数体如下：

    
    
    protected function getFilter($filter,  $default)
        {
             if (is_null($filter)) {
                 $filter = [];
             } else {
                 $filter = $filter ?:  $this->filter;
                 if (is_string($filter) && false === strpos($filter, '/')) {
                    $filter = explode(',',  $filter);
                 } else {
                    $filter = (array) $filter;
                 }
             }
    
             $filter[] = $default;
             return $filter;
        }

`$this->filter`的值是攻击者通过调用构造函数覆盖控制的，将该值返回后将进入到input函数:

    
    
     if  (is_array($data)) {
                 array_walk_recursive($data, [$this, 'filterValue'], $filter);
                 reset($data);
             }

查看filterValue函数如下：

    
    
    private function filterValue(&$value,  $key, $filters)
        {
            $default = array_pop($filters);
             foreach ($filters as $filter) {
                 if (is_callable($filter)) {
                    // 调用函数或者方法过滤
                     $value = call_user_func($filter, $value);
                 } elseif (is_scalar($value)) {
                    if (false !== strpos($filter, '/'))  {
                        // 正则过滤
                        if (!preg_match($filter,  $value)) {
                            // 匹配不成功返回默认值
                            $value = $default;
                            break;
                        }
                    } elseif (!empty($filter)) {
                        // filter函数不存在时, 则使用filter_var进行过滤
                        // filter为非整形值时, 调用filter_id取得过滤id
                        $value =  filter_var($value, is_int($filter) ? $filter : filter_id($filter));
                        if (false === $value) {
                            $value = $default;
                            break;
                        }
                    }
                 }
             }
             return $this->filterExp($value);
        }

在`call_user_func`函数的调用中，`$filter`可控，`$value`可控。因此，可致代码执行。

#### **漏洞触发流程：**

从ThinkPHP5的入口点开始分析：

thinkphp/library/think/App.php:77

    
    
      public static function run(Request $request = null)
        {
            $request = is_null($request) ? Request::instance() : $request;
    
            try {
                $config = self::initCommon();
    
                // 模块/控制器绑定
                if (defined('BIND_MODULE')) {
                    BIND_MODULE && Route::bind(BIND_MODULE);
                } elseif ($config['auto_bind_module']) {
                    // 入口自动绑定
                    $name = pathinfo($request->baseFile(), PATHINFO_FILENAME);
                    if ($name && 'index' != $name && is_dir(APP_PATH . $name)) {
                        Route::bind($name);
                    }
                }
    
                $request->filter($config['default_filter']);
    
                // 默认语言
                Lang::range($config['default_lang']);
                // 开启多语言机制 检测当前语言
                $config['lang_switch_on'] && Lang::detect();
                $request->langset(Lang::range());
    
                // 加载系统语言包
                Lang::load([
                    THINK_PATH . 'lang' . DS . $request->langset() . EXT,
                    APP_PATH . 'lang' . DS . $request->langset() . EXT,
                ]);
    
                // 监听 app_dispatch
                Hook::listen('app_dispatch', self::$dispatch);
                // 获取应用调度信息
                $dispatch = self::$dispatch;
    
                // 未设置调度信息则进行 URL 路由检测
                if (empty($dispatch)) {
                    $dispatch = self::routeCheck($request, $config);
                }
    
                // 记录当前调度信息
                $request->dispatch($dispatch);
    
                // 记录路由和请求信息
                if (self::$debug) {
                    Log::record('[ ROUTE ] ' . var_export($dispatch, true), 'info');
                    Log::record('[ HEADER ] ' . var_export($request->header(), true), 'info');
                    Log::record('[ PARAM ] ' . var_export($request->param(), true), 'info');
                }
    
                // 监听 app_begin
                Hook::listen('app_begin', $dispatch);
    
                // 请求缓存检查
                $request->cache(
                    $config['request_cache'],
                    $config['request_cache_expire'],
                    $config['request_cache_except']
                );
    
                $data = self::exec($dispatch, $config);

run函数第一行便实例化了一个Request类，并赋值给了`$request`。然后调用`routeCheck($request,$config)`：

    
    
     public static function routeCheck($request, array $config)
        {
            $path   = $request->path();
            $depr   = $config['pathinfo_depr'];
            $result = false;
    
            // 路由检测
            $check = !is_null(self::$routeCheck) ? self::$routeCheck : $config['url_route_on'];
            if ($check) {
                // 开启路由
                if (is_file(RUNTIME_PATH . 'route.php')) {
                    // 读取路由缓存
                    $rules = include RUNTIME_PATH . 'route.php';
                    is_array($rules) && Route::rules($rules);
                } else {
                    $files = $config['route_config_file'];
                    foreach ($files as $file) {
                        if (is_file(CONF_PATH . $file . CONF_EXT)) {
                            // 导入路由配置
                            $rules = include CONF_PATH . $file . CONF_EXT;
                            is_array($rules) && Route::import($rules);
                        }
                    }
                }
    
                // 路由检测（根据路由定义返回不同的URL调度）
                $result = Route::check($request, $path, $depr, $config['url_domain_deploy']);
                $must   = !is_null(self::$routeMust) ? self::$routeMust : $config['url_route_must'];
    
                if ($must && false === $result) {
                    // 路由无效
                    throw new RouteNotFoundException();
                }
            }
    
            // 路由无效 解析模块/控制器/操作/参数... 支持控制器自动搜索
            if (false === $result) {
                $result = Route::parseUrl($path, $depr, $config['controller_auto_search']);
            }
    
            return $result;
        }

这里调用`Route::check`进行路由检测。函数如下：

    
    
    public static function check($request, $url, $depr = '/', $checkDomain = false)
        {
            //检查解析缓存
            if (!App::$debug && Config::get('route_check_cache')) {
                $key = self::getCheckCacheKey($request);
                if (Cache::has($key)) {
                    list($rule, $route, $pathinfo, $option, $matches) = Cache::get($key);
                    return self::parseRule($rule, $route, $pathinfo, $option, $matches, true);
                }
            }
    
            // 分隔符替换 确保路由定义使用统一的分隔符
            $url = str_replace($depr, '|', $url);
    
            if (isset(self::$rules['alias'][$url]) || isset(self::$rules['alias'][strstr($url, '|', true)])) {
                // 检测路由别名
                $result = self::checkRouteAlias($request, $url, $depr);
                if (false !== $result) {
                    return $result;
                }
            }
            $method = strtolower($request->method());
            // 获取当前请求类型的路由规则
            $rules = isset(self::$rules[$method]) ? self::$rules[$method] : [];
            // 检测域名部署
            if ($checkDomain) {
                self::checkDomain($request, $rules, $method);
            }
            // 检测URL绑定
            $return = self::checkUrlBind($url, $rules, $depr);
            if (false !== $return) {
                return $return;
            }
            if ('|' != $url) {
                $url = rtrim($url, '|');
            }
            $item = str_replace('|', '/', $url);
            if (isset($rules[$item])) {
                // 静态路由规则检测
                $rule = $rules[$item];
                if (true === $rule) {
                    $rule = self::getRouteExpress($item);
                }
                if (!empty($rule['route']) && self::checkOption($rule['option'], $request)) {
                    self::setOption($rule['option']);
                    return self::parseRule($item, $rule['route'], $url, $rule['option']);
                }
            }
    
            // 路由规则检测
            if (!empty($rules)) {
                return self::checkRoute($request, $rules, $url, $depr);
            }
            return false;
        }

注意红色字体部分。对应开头的第一个步骤，也就是调用method函数进行变量覆盖。这里需要覆盖的属性有`$this->filter`,`$this->method`,`$this->get`。因为`$request->method()`的返回值为`$this->method`，所以该值也需要被控制。这里返回值赋值给了`$method`，然后取出`self::$rules[$method]`的值给`$rules`。这里需要注意：
**THINKPHP5有自动类加载机制，会自动加载vendor目录下的一些文件。但是完整版跟核心版的vendor目录结构是不一样的。**

完整版的目录结构如下：

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44C9.tmp.jpg-w331s)

而核心版的目录结构如下：

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44CA.tmp.jpg-w331s)

可以看到完整版比核心版多出了几个文件夹。特别需要注意的就是`think-captcha/src`这个文件夹里有一个helper.php文件：

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44CB.tmp.jpg-w331s)

这里调用`\think\Route::get`函数进行路由注册的操作。而这步操作的影响就是改变了上文提到的`self::$rules`的值。有了这个路由，才能进行RCE，否则不成功。这也就是为什么只影响完整版，而不影响核心版的原因。此时的`self::$rules`的值为:

![img](https://images.seebug.org/content/images/2019/01/12/1547272918000-wps44CC.tmp.jpg-w331s)

那么，当攻击者控制返回的`$method`的值为get的时候，`$rules`的值就是这条路由的规则。然后回到上文取到`$rules`之后，根据传入的URL取得$item的值，使得`$rules[$item]`的值为captcha路由数组，就可以进一步调用到`self::parseRule`函数。函数体略长，这里取关键点：

    
    
    private static function parseRule($rule, $route, $pathinfo, $option = [], $matches = [], $merge = false)
        {
            // 解析路由规则
          ......
    ......
            if ($route instanceof \Closure) {
                // 执行闭包
                $result = ['type' => 'function', 'function' => $route];
            } elseif (0 === strpos($route, '/') || 0 === strpos($route, 'http')) {
                // 路由到重定向地址
                $result = ['type' => 'redirect', 'url' => $route, 'status' => isset($option['status']) ? $option['status'] : 301];
            } elseif (0 === strpos($route, '\\')) {
                // 路由到方法
                $method = strpos($route, '@') ? explode('@', $route) : $route;
                $result = ['type' => 'method', 'method' => $method];
            } elseif (0 === strpos($route, '@')) {
                // 路由到控制器
                $result = ['type' => 'controller', 'controller' => substr($route, 1)];
            } else {
                // 路由到模块/控制器/操作
                $result = self::parseModule($route);
            }
            return $result;
        }

此时传递进来的`$route`的值为`\think\captcha\CaptchaController@index`。因此进入的是标注红色的if分支中。在这个分支中，`$result`的’type’键对应的值为‘method’。然后将`$result`层层返回到run函数中，并赋值给了`$dispatch`。

    
    
         // 未设置调度信息则进行 URL 路由检测
                if (empty($dispatch)) {
                    $dispatch = self::routeCheck($request, $config);
                }
    
                // 记录当前调度信息
                $request->dispatch($dispatch);
    
                // 记录路由和请求信息
                if (self::$debug) {
                    Log::record('[ ROUTE ] ' . var_export($dispatch, true), 'info');
                    Log::record('[ HEADER ] ' . var_export($request->header(), true), 'info');
                    Log::record('[ PARAM ] ' . var_export($request->param(), true), 'info');
                }
    
                // 监听 app_begin
                Hook::listen('app_begin', $dispatch);
    
                // 请求缓存检查
                $request->cache(
                    $config['request_cache'],
                    $config['request_cache_expire'],
                    $config['request_cache_except']
                );
    
                $data = self::exec($dispatch, $config);

然后将`$dispatch`带入到`self::exec`函数中：

    
    
     protected static function exec($dispatch, $config)
        {
            switch ($dispatch['type']) {
                case 'redirect': // 重定向跳转
                    $data = Response::create($dispatch['url'], 'redirect')
                        ->code($dispatch['status']);
                    break;
                case 'module': // 模块/控制器/操作
                    $data = self::module(
                        $dispatch['module'],
                        $config,
                        isset($dispatch['convert']) ? $dispatch['convert'] : null
                    );
                    break;
                case 'controller': // 执行控制器操作
                    $vars = array_merge(Request::instance()->param(), $dispatch['var']);
                    $data = Loader::action(
                        $dispatch['controller'],
                        $vars,
                        $config['url_controller_layer'],
                        $config['controller_suffix']
                    );
                    break;
                case 'method': // 回调方法
                    $vars = array_merge(Request::instance()->param(), $dispatch['var']);
                    $data = self::invokeMethod($dispatch['method'], $vars);
                    break;
                case 'function': // 闭包
                    $data = self::invokeFunction($dispatch['function']);
                    break;
                case 'response': // Response 实例
                    $data = $dispatch['response'];
                    break;
                default:
                    throw new \InvalidArgumentException('dispatch type not support');
            }
    
            return $data;
        }

进入到红色标注的分支，该分支调用Request类的param方法。因此，满足了利用链的第三步，造成命令执行。

启明星辰ADLab安全研究员对ThinkPHP5.0-5.0.23每个版本都进行了分析，发现ThinkPHP5.0.2-5.0.23可以使用同一个POC，而ThinkPHP5.0-5.0.1需要更改一下POC，原因在于Route.php的rule函数的一个实现小差异。

ThinkPHP5.0-5.0.1版本的thinkphp/library/think/Route.php:235，将$type转换成了大写：

![img](https://images.seebug.org/content/images/2019/01/12/1547272919000-wps44CD.tmp.jpg-w331s)

在ThinkPHP5.0.2-5.0.23版本中，rule函数中却将`$type`转换成了小写：

![img](https://images.seebug.org/content/images/2019/01/12/1547272919000-wps44DD.tmp.jpg-w331s)

### **补丁分析**

在ThinkPHP5.0.24中，增加了对`$this->method`的判断，不允许再自由调用类函数。

![img](https://images.seebug.org/content/images/2019/01/12/1547272919000-wps44DE.tmp.jpg-w331s)

### **结论**

强烈建议用户升级到ThinkPHP5.0.24版本，并且不要开启debug模式，以免遭受攻击。

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/787/>

