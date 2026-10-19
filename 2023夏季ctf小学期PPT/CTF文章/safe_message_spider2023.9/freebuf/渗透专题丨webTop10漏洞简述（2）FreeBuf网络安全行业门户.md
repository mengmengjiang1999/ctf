## 文件包含漏洞

### 1、漏洞简述

程序在引用文件的时，引用的文件名，用户可控的情况，传入的文件名校验不严，从而操作了预想之外的文件，就有可能导致文件泄漏和恶意的代码注入。这是因为程序开发时候会把重复使用的函数写到归档在一起，用到哪个函数就可以直接进行调用，而为了代码更灵活，包含的文件会被设置为变量动态调用，这里就容易造成文件包含漏洞。

### 2、利用方法

$html='';  
if(isset($_GET['submit']) && $_GET['filename']!=nul1){  
($filename=$ GET[filename"];  
include"include/$filename";

因为对于$_GET['filename']没有任何过滤，直接代入到include中，如果包含这个文件，并成功引用，就会造成文件包含漏洞。

### 3、伪协议

file:// — 访问本地文件系统

http:// — 访问HTTP(s) 网址

ftp:// — 访问FTP(s) URLs

php:// — 访问各个输入/输出流（I/O streams）

zlib:// — 压缩流

data:// — </span><span lang="EN-US">数据（</span><span lang="EN-US">RFC
2397</span><span lang="EN-US">）</span><span lang="EN-US"><o:p></o:p></span></p><p><span lang="EN-US">glob:// — </span><span
lang="EN-US">查找匹配的文件路径模式</span><span lang="EN-US"><o:p></o:p></span></p><p><span lang="EN-US">phar:// — PHP </span><span
lang="EN-US">归档</span><span lang="EN-US"><o:p></o:p></span></p><p><span
lang="EN-US">ssh2:// — Secure Shell 2<o:p></o:p></span></p><p><span lang="EN-US">rar:// — RAR<o:p></o:p></span></p><p><span lang="EN-US">ogg:// —
</span><span lang="EN-US">音频流</span><span lang="EN-US"><o:p></o:p></span></p><p><span lang="EN-US">expect:// — </span><span
lang="EN-US">处理交互式的流</span><span lang="EN-US"><o:p></o:p></span></p><h4><span
lang="EN-US">php.ini</span><span lang="EN-US">参数</span><span lang="EN-US"><o:p></o:p></span></h4><p><span lang="EN-US">allow_url_fopen:</span><span
lang="EN-US">默认值是</span><span lang="EN-US"> ON</span><span lang="EN-US">。允许</span><span lang="EN-US"> url </span><span lang="EN-US">里的封装协议访问文件；</span><span lang="EN-US"><o:p></o:p></span></p><p><span
lang="EN-US">allow_url_include:</span><span lang="EN-US">默认值是</span><span
lang="EN-US"> OFF</span><span lang="EN-US">。不允许包含</span><span lang="EN-US">
url </span><span lang="EN-US">里的封装协议包含文件；</span><span lang="EN-US"><o:p></o:p></span></p><p><span tabindex="-1" contenteditable="false" data-cke-widget-wrapper="1" data-cke-filter="off" class="cke_widget_wrapper
cke_widget_inline cke_image_nocaption cke_widget_selected" data-cke-display-name="图像" data-cke-widget-id="0"><img alt="" data-cke-saved-src="/files/default/2023/06-13/1421382d90dc806513.png"
src="http://www.vultop.com/files/default/2023/06-13/1421382d90dc806513.png"
data-cke-widget-data="%7B%22hasCaption%22%3Afalse%2C%22src%22%3A%22%2Ffiles%2Fdefault%2F2023%2F06-13%2F1421382d90dc806513.png%22%2C%22alt%22%3A%22%22%2C%22width%22%3A%22%22%2C%22height%22%3A%22%22%2C%22lock%22%3Atrue%2C%22align%22%3A%22none%22%2C%22classes%22%3Anull%7D"
data-cke-widget-upcasted="1" data-cke-widget-keep-attr="0" data-widget="image"
class="cke_widget_element"><span class="cke_reset
cke_widget_drag_handler_container"><img class="cke_reset
cke_widget_drag_handler" data-cke-widget-drag-handler="1"
src="data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw=="
width="15" title="点击并拖拽以移动" height="15" draggable="true">

![](https://image.3001.net/images/20230614/1686739613_64899a9d378578b95f79b.png!small)

### 4、常用路径

#### 包含日志文件getshell：

/usr/local/apache2/logs/access_log

/logs/access_log

/etc/httpd/logs/access_log

/var/log/httpd/access_log

#### 读取网站配置文件：

dedecms 数据库配置文件data/common.inc.php,

discuz 全局配置文件config/config_global.php,

phpcms 配置文件caches/configs/database.php

phpwind 配置文件conf/database.php

wordpress 配置文件wp-config.php

#### windows：

C:/boot.ini//

C:/Windows/System32/inetsrv/MetaBase.xml//IIS 配置文件

C:/Windows/repairsam//存储系统初次安装的密码

C:/Program Files/mysql/my.ini//Mysql 配置

C:/Program Files/mysql/data/mysql/user.MYD//Mysql root

C:/Windows/php.ini//php 配置信息

C:/Windows/my.ini//Mysql 配置信息

#### linux：

/root/.ssh/authorized_keys

/root/.ssh/id_rsa

/root/.ssh/id_ras.keystore

/root/.ssh/known_hosts

/etc/passwd

/etc/shadow

/etc/my.cnf

/etc/httpd/conf/httpd.conf

/root/.bash_history

/root/.mysql_history

/proc/self/fd/fd[0-9]*(文件标识符)

/proc/mounts

/porc/config.gz

### 5、漏洞预防

• 设置allow_url_include 为Off

• 路径限制：限制被包含的文件只能在某一文件内，一定要禁止目录跳转字符，如："../"；

• 包含文件验证：验证被包含的文件是否是白名单中的一员；

• 尽量不要使用动态包含，可以在需要包含的页面固定写好，如：include('head.php')

• 严格判断包含中的参数是否外部可控，因为文件包含漏洞利用成功与否的关键点就在于被包含的文件是否可被外部控制。

## 命令执行漏洞

### 1、简述

程序开发需要去调用一些外部程序，当应用需要调用一些外部程序时就会用到一些执行系统命令的函数。应用在调用这些函数执行系统命令的时候，如果将用户的输入作为系统命令的参数拼接到命令行中，在没有过滤用户的输入的情况下，就会造成命令执行漏洞。

### 2、危害

• 反弹shell

• 控制服务器

• 控制网站

### 3、命令执行漏洞攻击

• ；命令按照顺序（从左到右）被执行，并且可以用分号进行分隔。当有一条命令执行失败时，不会中断其它命令的执行。例如：ping -c 1
127.0.0.1;whoami

• | 通过管理符可以将一个命令的标准输出管理为另外一个命令的标准输入，当它失败后，会执行另外一条命令。例如：ping -c 1
127.0.0.1|whoami

• & 命令按照顺序（从左到右）被执行，跟分号作用一样；此符号作用是后台任务符号使shell
在后台执行该任务，这样用户就可以立即得到一个提示符并继续其他工作，例如：ping -c 4 127.0.0.1&cat /etc/passwd&

• && 前后的命令的执行存在逻辑与关系，只有【&&】前面的命令执行成功后，它后面的命令才被执行，例如：ping -c 4
127.0.0.1&&whoami

• || 前后命令的执行存在逻辑或关系，只有【||】前面的命令执行失败后，它后面的命令才被执行；例如：ping -c ||whoami

• “ ` ”（反引号）当一个命令被解析时，它首先会执行反引号之间的操作。例如执行echols -a将会首先执行ls
并捕获其输出信息。然后再将它传递给echo，并将ls 的输出结果打印在屏幕上，这被称为命令替换例如：echo（反引号）whoami(反引号)

• $ 这是命令替换的不同符号。当反引号被过滤或编码时，可能会更有效。

ping -c 4 127.0.0.1 $(whoami)

• win 命令链接符| & || && 同上

### 4、命令执行漏洞防御

• 不执行外部的应用程序或命令，尽量使用自定义函数或函数库实现外部应用程序或命令的功能。在执行system、eval
等命令执行功能的函数前，要确认参数内容。

• 使用escapeshellarg 函数处理相关参数，escapeshellarg
函数会将用户引起参数或命令结束的字符进行转义，如单引号“’”会被转义为“’”，双引号“"”会被转义为“"”，分号“;”会被转义为“;”，这样escapeshellarg
会将参数内容限制在一对单引号或双引号里面，转义参数中包括的单引号或双引号，使其无法对当前执行进行截断，实现防范命令注入攻击的目的。

• 使用safe_mode_exec_dir 执行可执行的文件路径将php.ini 文件中的safe_mode
设置为On，然后将允许执行的文件放入一个目录，并使用safe_mode_exec_dir
指定这个可执行的文件路径。这样，在需要执行相应的外部程序时，程序必须在safe_mode_exec_dir 指定的目录中才会允许执行，否则执行将失败。

## 代码执行漏洞

### 1、漏洞简述

当程序在调用一些字符串转化为代码的函数时，没有考虑用户是否能控制这个字符串，将造成漏洞。

### 2、常见函数

• PHP ：eval()、assert()、preg_replace()

• python ：eval

### 3、漏洞代码示例

#### 3.1、动态代码执行漏洞

  
function m_print(){  
echo 'hello world';  
}  
$_GET['a']($_GET['b']);  
?>

#### 3.2、eval代码执行漏洞

  
$data = isset($_GET['data'])?$_GET['data']:'这是一个 eval 漏洞页面';  
@eval($ret = $data);  
echo $ret;#把字符串当做代码执行  
?>

#### 3.3、正则代码执行漏洞

  
$data = $_GET['data'];  
preg_replace('/(.*)<\/data>/e','$ret = "\\\1";',$data);  
?>

  
请输入  
  
  
  
{${phpinfo()}}

  

注释：preg_replace 使用了/e 模式，导致可以代码执行

### 4、代码执行防御方法

• 使用json 保存数组，当读取时就不需要使用eval

• 对于必须使用eval 的地方，一定严格处理用户数据（白名单、黑名单）

• 字符串使用单引号包括可控代码，插入前使用addslashes
转义（addslashes、魔数引号、htmlspecialchars、htmlentities、mysql_real_escape_string）

• 不要使用preg_replace 的e 修饰符，使用preg_replace_callback()替换（preg_replace_callback()）

• 若必须使用preg_replace 的e 修饰符，则必用单引号包裹正则匹配出的对象（preg_replace+正则）

## CSRF漏洞

### 1、简述

CSRF 定义：跨站请求伪造（英语：Cross-site request forgery），也被称为one-click attack 或者session
riding，通常缩写为CSRF ，是一种挟制用户在当前已登录的Web 应用程序上执行非本意的操作的攻击方法。

### 2、漏洞攻击原理

用户打开浏览器，访问登陆受信任的A 网站，在用户信息通过验证后，服务器会返回一个cookie 给浏览器，用户登陆网站A
成功，可以正常发送请求到网站A，随后用户未退出网站A，在同一浏览器中，打开一个危险网站B，而网站B
收到用户请求后，返回一些恶意代码，并发出请求要求访问网站A，浏览器收到这些恶意代码以后，在用户不知情的情况下，利用cookie 信息，向网站A
发送恶意请求，网站，最后A 会根据cookie 信息以用户的权限去处理该请求，导致来自网站B 的恶意代码被执行。

### 3、受攻击途径

• 受害者登录网站a后，没有退出的情况下，访问了网站b

• 在存在漏洞的网站，挖掘xss 漏洞，自动调用这poc.html

### 4、漏洞防御

• 增加Token 验证

• 不要在客户端保存敏感信息；退出、关闭浏览器时的会话过期机制，设置会话过机制，比如15 分钟无操作，则自动登录超时

• 敏感信息的修改时需要身份进行二次认证，比如修改账号密码，需要判断旧密码敏感信息的修改使用POST，而不是GET通过HTTP 头部中的REFERER
来限制原页面

• 增加验证码

## JSONP漏洞

### 1、简述

Jsonp(JSON with Padding) 是json
的一种"使用模式"，可以让网页从别的域名（网站）那获取资料，即跨域读取数据。为什么我们从不同的域（网站）访问数据需要一个特殊的技术(JSONP
)呢？这是因为同源策略，同源策略，它是由Netscape 提出的一个著名的安全策略，现在所有支持JavaScript
的浏览器都会使用这个策略。传入callback 值会在结果里面直接返回。因此，如果该参数过滤不严格。可以随便输入：callback
值为：alert('1');parseResponse 字符串，返回结果会打印个alert
窗口，然后也会正常执行。攻击者模拟用户向有漏洞的服务器发送JSONP 请求，然后就获取到了用户的某些信息，再将这些信息发送到攻击者可控的服务。

### 2、漏洞原理

动态添加一个< script >标签，而script 标签的src 属性是没有跨域的限制的。由于同源策略的限制，XmlHttpRequest
只允许请求当前源(域名、协议、端口都相同)的资源，如果要进行跨域请求，我们可以通过使用html 的script
标记来进行跨域请求，并在响应中返回要执行的script 代码，其中可以直接使用JSON 传递javascript 对象。考虑这样一种情况，存在两个网站A
和B，用户在网站B 上注册并且填写了自己的用户名，手机号，身份证号等信息，并且网站B 存在一个jsonp 接口，用户在访问网站B 的时候。这个jsonp
接口会返回用户的暗月内部文档请勿外出个人信息，并在网站B 的html 页面上进行显示。如果网站B 对此jsonp
接口的来源验证存在漏洞，那么当用户访问网站A 时，网站A 便可以利用此漏洞进行JSONP 劫持来获取用户的信息。

### 3、攻击手法

需要用户登录帐号，身份认证还没有被消除的情况下访问攻击者精心设计好的的页面。就会获取json 数据，把json 数据发送给攻击者。寻找敏感json
数据api 接口，构造恶意的代码。发送给用户，用户访问有恶意的页面，数据会被劫持发送到远程服务器。

### 4、攻击代码示例

  
if($_GET['file']){  
file_put_contents('json.txt',$_GET['file']);  
}  
?>  
jsonp 劫持代码

当用户访问这个页面时，会自动把接口user.php 的敏感信息发送到远程服务器上，如果获取到信息就会在远程服务器上生成json.txt。

### 5、漏洞防御

json 正确的http 头输出尽量避免跨域的数据传输，对于同域的数据传输使用xmlhttp 的方式作为数据获取的方式，依赖于javascript
在浏览器域里的安全性保护数据，如果是跨域的数据传输，必须要对敏感的数据获取做权限认证。

