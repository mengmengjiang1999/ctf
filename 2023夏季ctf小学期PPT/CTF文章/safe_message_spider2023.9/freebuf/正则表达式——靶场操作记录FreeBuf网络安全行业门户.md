——————————————分析flag代码————————————  
//告诉这是PHP咯  
<?php  
$key=’flag{ ****** }’;  
$Regular= preg_match(“/zkaq.key.{2,9}:\/.\/(keykey)/i”, trim($_GET[“id”]),
$match);  
if( $Regular ){  
die(‘key: ‘.$key);  
} //if结尾咯（但是为什么没有‘？>’结尾呢）  
——————————————分析flag代码2————————————  
$key=’flag{ ****** }’;  
定义一个变量$key等于这一串32个字符咯（flag长度是32还是？）  
继续  
——————————————分析flag代码3————————————  
$Regular= preg_match(“/zkaq.key.{2,9}:\/.\/(keykey)/i”, trim($_GET[“id”]),
$match);  
preg_match_all()学了preg_match是啥搜一下  
preg_match 只匹配一次，preg_match_all是全文匹配，即所有跟表达式一致的都找出来。

以下我们看案例

1、取出符号里的字符。preg_match_all(“/(\w)+/“,”abc”,$search);

  1. `print_r($search);`

显示结果为

Array  
(  
[0] => Array  
(  
[0] => abc  
)

  1. `[1] => Array`
  2. `(`
  3. `[0] => c`
  4. `)`

)

2、preg_match(“/(\w)+/“,”abc”,$search);print_r($search);

显示结果

Array( [0] = a [1] = a)

总结：

两个函数的区别就是：preg_match_all()搜索匹配全部情况；preg_match()搜索匹配到一个后终止。

preg_match() 返回 pattern 所匹配的次数。要么是 0 次（没有匹配）或 1 次，因为 preg_match()
在第一次匹配之后将停止搜索。preg_match_all() 则相反，会一直搜索到 subject 的结尾处。如果出错 preg_match() 返回
FALSE。

_all就是多次  
没有all就是一次或0次咯

——————————————分析flag代码4————————————  
“/zkaq.key.{2,9}:\/.\/(keykey)/i”怎么匹配的  
看总体内容/zkaq.key.{2,9}:\/.\/(keykey)/i（i不区分大小写可以不看）  
/zkaq.key.{2,9}:\/.\/(keykey)/看里面的内容  
zkaq.key.{2,9}:\/.\/(keykey)  
z就是匹配z k就是k a就是a q就是q 咯!q.是什么（搜一下  
![](https://image.3001.net/images/20210928/1632814091_6152c40bd4911d135b6f1.png!small)所以.对于他前面的没有任何作用！毛都没有）  
所以q还是q  
zkaq  
.是任意字符那就随便填  
是尽可能多的匹配  
那.就是尽可能多的任意字符咯  
k就是K e就是e y就是y  
目前解析得：（zkaq尽可能多的任意字符key）  
继续  
.任意字符 .{区间数量字符} {2，9}两次到九次  
.{2,9}任意字符两个或九个之间如123456789 12 123 等等。  
：（顿号是个什么毛线？搜一下  
![](https://image.3001.net/images/20210928/1632814092_6152c40c723796359e422.png!small)没有单独的：出现那应该是其本身或者  
：的编码是什么  
![](https://image.3001.net/images/20210928/1632814093_6152c40d537f7c3b06f07.png!small)  
那就是：或者65306咯还或者是二进制  
![](https://image.3001.net/images/20210928/1632814093_6152c40de7ce4386dbb50.png!small)  
-1）  
继续  
目前解析得：（zkaq尽可能多的任意字符key任意字符两个或九个之间“ ：/65306/-1” ）  
继续  
\转义字符 \/得到/  
.尽可能多的字符（贪婪）  
\转义字符 \/得到/  
/尽可能多的字符/  
再继续（keykey）  
()代表里面是个整体  
ke就是ke y*匹配尽可能多的y 如y yy yyyyy。  
key就是key  
得到：（zkaq尽可能多的任意字符key任意字符两个或九个之间“ ：/65306/-1” /尽可能多的字符/key‘多个y’key）  
zkaq723key723:/723/keyyykey  
zkaq723key72365306/723/keyyykey  
zkaq723key723-1/723/keyyykey

——————————————分析flag代码5————————————  
trim($_GET[“id”])  
上面匹配的内容来自哪里  
trim()是什么（搜一下  
![](https://image.3001.net/images/20210928/1632814094_6152c40e6cc7821dc9412.png!small)此处为移除空白字符没有预定义）  
$_GET[“id”]  
以get的方式传参内容来自id  
$match  
执行正则匹配

if( $Regular ){  
die(‘key: ‘.$key);

如果$Regular==id==  
![](https://image.3001.net/images/20210928/1632814094_6152c40edcc484751c6f7.png!small)  
die(‘key: ‘.$key); 代码执行中断并输出  
key:(内容)

————————————————尝试验证——————————————  
zkaq723key723:/723/keyyykey (可 行)  
zkaq723key72365306/723/keyyykey（不可行 没有：6后面加上：可行 前面72365306共八位数未超过九位可行）  
zkaq723key723-1/723/keyyykey（不可行 加上：不可行 加上：去掉负号可行 ）

得出s  
flag{regular_god_code}

