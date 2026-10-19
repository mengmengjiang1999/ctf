## CORS跨域资源共享漏洞

### 1、名词解释

• CORS：跨域资源共享是一种放宽同源策略的机制，它允许浏览器向跨源服务器，发出XMLHttpRequest 请求，从而克服了AJAX
只能同源使用的限制，以使不同的网站可以跨域获取数据。

• CORS过程：简单跨域请求就是使用设定的请求方式请求数据，而非简单跨域请求则是在使用设定的请求方式请求数据之前，先发送一个OPTIONS
预检请求，验证请求源是否为服务端允许源。只有"预检"通过后才会再发送一次请求用于数据传输。当我们需要发送一个跨域请求的时候，浏览器会首先检查这个请求，如果它是简单跨域请求，浏览器就会立刻发送这个请求。如果它是非简单跨域请求，这时候浏览器不会马上发送这个请求，而是有一个跟服务器预检验证的过程。

• CORS运行机制：在浏览器进行请求时，自动在请求头中添加Origin 字段，服务端通过验证Origin
字段来判断请求是否被允许，从而实现浏览器进行跨源访问。

### 2、漏洞代码

  
  
  
  
  
  
  

### 4、防御方案

• 不要配置"Access-Control-Allow-Origin" 为通配符“*”,而且更重要的是，要严格效验来自请求数据包中的"Origin"
的值。当收到跨域请求的时候，要检查"Origin" 的值是否是一个可信的源，还要检是否为null

• 避免使用"Access-Control-Allow-Credentials: true"

• 减少Access-Control- Allow-Methods 所允许的方法

## 越权漏洞

### 1、简述

越权访问（Broken Access Control，简称BAC）是Web 应用程序中一种常见的漏洞，由于其存在范围广、危害大，被OWASP 列为Web
应用十大安全隐患的第二名。该漏洞是指应用在检查授权时存在纰漏，使得攻击者在获得低权限用户账户后，利用一些方式绕过权限检查，访问或者操作其他用户或者更高权限。越权漏洞的成因主要是因为开发人员在对数据进行增、删、改、查询时对客户端请求的数据过分相信而遗漏了权限的判定，一旦权限验证不充分，就易致越权漏洞。

### 2、越权漏洞分类

• 水平越权：指相同权限下不同的用户可以互相访问

• 垂直越权：垂直越权是不同级别之间或不同角色之间的越权，一般是低权限用户往高权限越权。

### 3、漏洞防御

1、基础安全架构，完善用户权限体系。要知道哪些数据对于哪些用户，哪些数据不应该由哪些用户操作；

2、鉴权，服务端对请求的数据和当前用户身份做校验；

3、不要直接使用对象的实名或关键字。

4、对于可控参数进行严格的检查与过滤。

## SSRF漏洞

### 1、简述

SSRF (Server-Side Request
Forgery,服务器端请求伪造)是一种由攻击者构造请求，由服务端发起请求的安全漏洞。一般情况下，SSRF
攻击的目标是外网无法访问的内部系统(正因为请求是由服务端发起的，所以服务端能请求到与自身相连而与外网隔离的内部系统)。

### 2、漏洞原理

SSRF 的形成大多是由于服务端提供了从其他服务器应用获取数据的功能且没有对目标地址做过滤与限制。例如，黑客操作服务端从指定URL
地址获取网页文本内容，加载指定地址的图片等，利用的是服务端的请求伪造。SSRF 利用存在缺陷的Web 应用作为代理攻击远程和本地的服务器。

### 3、主要攻击手段

• 对外网、服务器所在内网、本地进行端口扫描，获取一些服务的banner 信息。

• 攻击运行在内网或本地的应用程序。

• 对内网Web 应用进行指纹识别，识别企业内部的资产信息。

• 攻击内外网的Web 应用，主要是使用HTTP GET 请求就可以实现的攻击(比如struts2、SQli 等)。

• 利用file 协议读取本地文件等。

### 4、支持协议

ftp

ssrf.php?url=ftp://evil.com:12345/TEST

file://

ssrf.php?url=file:///etc/password

Dict://

dict://@:/d:

ssrf.php?url=dict://attacker:11111/

SFTP://

ssrf.php?url=sftp://example.com:11111/

TFTP://

ssrf.php?url=tftp://example.com:12346/TESTUDPPACKET

LDAP://

ssrf.php?url=ldap://localhost:11211/%0astats%0aquit

Gopher://

ssrf.php?url=gopher://127.0.0.1:3306

### 5、防御手段

1.禁止跳转

2.过滤返回信息，验证远程服务器对请求的响应是比较容易的方法。如果web
应用是去获取某一种类型的文件。那么在把返回结果展示给用户之前先验证返回的信息是否符合标准。

3.禁用不需要的协议，仅仅允许http 和https 请求。可以防止类似于file://, gopher://, ftp:// 等引

起的问题

4.设置URL 白名单或者限制内网IP（使用gethostbyname()判断是否为内网IP）

5.限制请求的端口为http 常用的端口，比如80、443、8080、8090

6.统一错误信息，避免用户可以根据错误信息来判断远端服务器的端口状态

## 反序列化漏洞

### 1、简述

反序列化又叫对象注入，序列化在内部没有漏洞，漏洞产生是应该程序在处理对象、魔术函数以及序列化相关的问题导致的当传给unserialize()的参数可控时，那么用户就可以注入payload,进行反序列化的时候就可能触发对象中的一些魔术方法。

### 2、名词解释

序列化：对象的状态信息转换为可以存储或传输的形式的过程在序列化期间，对象将当前的状态写入到临时或持久性的存储区，将状态信息保存为字符串。

反序列化：将序列化后的字符串还原成对象。

### 3、反序列化魔法函数

• __construct() 当一个对象创建时被调用

• __destruct() 当一个对象销毁前被调用

• __sleep() 在对象被序列化前被调用

• __wakeup 将在反序列化之后立即被调用

• __toString 当一个对象被当做字符串使用时被调用

• **get(),** set() 当调用或设置一个类及其父类方法中未定义的属性时

• __invoke() 调用函数的方式调用一个对象时的回应方法

• **call** **和** callStatic 前者是调用类不存在的方法时执行，而后者是调用类不存在的静态方式方法时执行。

### 4、魔术方法实例

  
class 123{  
public $var1 = 'abc';  
public $var2 = '123';  
public function echoP(){  
echo $this->var1.'  
';  
}  
public function __construct(){  
echo "__construct  
";  
}  
public function __destruct(){  
echo "__destruct  
";  
}  
public function __toString(){  
return "__toString  
";  
}  
public function __sleep(){  
echo "__sleep  
";  
// 注意返回带类中所有变量名称的数组  
return array('var1', 'var2');  
}  
public function __wakeup(){  
echo "__wakeup  
";  
}  
}  
// 创建对象，输出__construct  
$obj = new 123();  
// 调用 echoP 方法  
$obj->echoP();  
// 把类当做字符串输出，输出__toString  
echo $obj;  
// 序列化对象，输出__sleep  
$s = serialize($obj);  
// O:6:"123":2:{s:4:"var1";s:3:"abc";s:4:"var2";s:3:"123";}  
echo $s.'  
';  
// 反序列对象，输出__wakeup  
unserialize($s);  
// 脚本结束，对象被销毁，输出两个 __destruct，还有一个是 unserialize 恢复的对象  
?>

### 4、漏洞防御

不要把用户的输入或者是用户可控的参数直接放进反序列化的操作中去

## 任意文件读取与下载漏洞

### 1、简述

任意文件读取与下载又名不安全的文件下载，一些网站的业务需要，可能提供文件查看或下载的功能，如果对用户查看或下载的文件不做限制，就能够查看或下载任意的文件，可以是源文件，敏感文件等等。通过任意文件下载，可以下载服务器的任意文件，web
业务的代码，服务器和系统的具体配置信息，也可以下载数据库的配置信息，以及对内网的信息探测等等。

### 2、常见的敏感文件

Win：

• C:\boot.ini //查看系统版本

• C:\Windows\System32\inetsrv\MetaBase.xml //IIS 配置文件

• C:\Windows\repair\sam //存储系统初次安装的密码

• C:\Program Files\mysql\my.ini //Mysql 配置

• C:\Program Files\mysql\data\mysql\user.MYD //Mysql root

• C:\Windows\php.ini //php 配置信息

• C:\Windows\my.ini

Linux：

• /etc/passwd

• /etc/shadow

• /etc/hosts

• /root/.bash_history

• //root 的bash 历史记录

• /root/.ssh/authorized_keys

• /root/.mysql_history //mysql 的bash 历史记录

• /root/.wget-hsts

• /opt/nginx/conf/nginx.conf //nginx 的配置文件

• /var/www/html/index.html

• /etc/my.cnf

• /etc/httpd/conf/httpd.conf //httpd 的配置文件

• /proc/self/fd/fd[0-9]*(文件标识符)

• /proc/mounts

• /porc/config.gz

• /proc/sched_debug // 提供cpu 上正在运行的进程信息，可以获得进程的pid 号，可以配合后面需要pid的利用

• /proc/mounts // 挂载的文件系统列表

• /proc/net/arp //arp 表，可以获得内网其他机器的地址

• /proc/net/route //路由表信息

• /proc/net/tcp and /proc/net/udp // 活动连接的信息

• /proc/net/fib_trie // 路由缓存

• /proc/version // 内核版本

• /proc/[PID]/cmdline // 可能包含有用的路径信息

• /proc/[PID]/environ // 程序运行的环境变量信息，可以用来包含getshell

• /proc/[PID]/cwd // 当前进程的工作目录

• /proc/[PID]/fd/[#] // 访问file descriptors，某写情况可以读取到进程正在使用的文件，比如access.log

### 3、漏洞防御

• 过滤点(.)使用户在url 中不能回溯上级目录

• 正则严格判断用户输入参数的格式

• php.ini 配置open_basedir 限定文件访问范围

## 目录遍历漏洞

### 1、简述

在web
功能设计中，很多时候我们会要将需要访问的文件定义成变量，从而让前端的功能变的更加灵活。当用户发起一个前端的请求时，便会将请求的这个文件的值(比如文件名称)传递到后台，后台再执行其对应的文件。在这个过程中，如果后台没有对前端传进来的值进行严格的安全考虑，则攻击者可能会通过“../”这样的手段让后台打开或者执行一些其他的文件。从而导致后台服务器上其他目录的文件结果被遍历出来，形成目录遍历漏洞。

### 2、代码分析

  
$dir_path=$_REQUEST['path'];  
$filename=scandir($dir_path);  
var_dump($filename);  
?>

path 可控传入scandir 函数再进行输出，会造成目录遍历漏洞。

### 3、攻击分类

• web目录遍历攻击：目录遍历可以输入../返回上级目录/遍历根目录./当前目录c:\访问c 盘，~/
当前用户目录。遍历网站或系统结构，寻找敏感文件，配合其他漏洞造成严重的安全隐患。

• 中间件目录遍历攻击：中间件如果设置不当的时，也会造成目录遍历，如apache ngnix iis
目录浏览，均可造成目录遍历，但是这种目录遍历，只能遍历网站根目录，除非有特殊设置。通过遍历目录或文件，寻找敏感文件，如session
登录验证文件，数据库备份等。对网站构成重大安全隐患。

### 4、预防手段

1.对用户的输入进行验证，特别是路径替代字符如“../”和“~/”。

2.尽可能采用白名单的形式，验证所有的输入。

3.合理配置Web 服务器的目录权限。

4.当程序出错时，不要显示内部相关配置细节。

5.对用户传过来的文件名参数进行统一编码，对包含恶意字符或者空字符的参数进行拒绝。

