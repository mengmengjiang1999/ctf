原创： Ash 合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

Smarty是一个PHP的模板引擎，提供让程序逻辑与页面显示（HTML/CSS）代码分离的功能。对于该框架的SSTI漏洞很多文章往往只是一笔带过，讲解的重心往往在flask等框架上。本篇文章结合一道CTF题目对Smarty的SSTI漏洞进行了一定的分析。题目地址：https://buuoj.cn/challenges
CISCN2019华东南赛区Web11

## 基本信息  

题目模拟了一个获取IP的API，并且可以在最下方看到“Build With Smarty
!”可以确定页面使用的是Smarty模板引擎。题目中显示的API的URL由于环境的原因无法使用，但是我们的IP依旧显示在了页面的右上角。很容易猜测出这个IP的值受XFF头控制
。将XFF头改为{2-1}会发现该位置的值变为了1，便可以确定这里存在SSTI。

## Smarty SSTI利用  

Smarty是基于PHP开发的，对于Smarty的SSTI的利用手段与常见的flask的SSTI有很大区别。

## 漏洞确认  

一般情况下输入{$smarty.version}就可以看到返回的smarty的版本号。该题目的Smarty版本是3.1.30

## 常规利用方式  

Smarty支持使用{php}{/php}标签来执行被包裹其中的php指令，最常规的思路自然是先测试该标签。但就该题目而言，使用{php}{/php}标签会报错：

![v2-a24770cd727d793d93abd89d5025ad41_hd.j](https://pic3.zhimg.com/80/v2-a24770cd727d793d93abd89d5025ad41_hd.jpg)

在Smarty3的官方手册里有以下描述:

> Smarty已经废弃{php}标签，强烈建议不要使用。在Smarty 3.1，{php}仅在SmartyBC中可用。  
>

该题目使用的是Smarty类，所以只能另寻它路。

{literal} 标签

官方手册这样描述这个标签：

> {literal}可以让一个模板区域的字符原样输出。这经常用于保护页面上的Javascript或css样式表，避免因为Smarty的定界符而错被解析。  
>

那么对于php5的环境我们就可以使用

<script language="php">phpinfo();</script>

来实现PHP代码的执行，但这道题的题目环境是PHP7，这种方法就失效了。

## 静态方法  

通过self获取Smarty类再调用其静态方法实现文件读写被网上很多文章采用。

Smarty类的getStreamVariable方法的代码如下：

public function getStreamVariable($variable){ $_result = ''; $fp =
fopen($variable, 'r+'); if ($fp) { while (!feof($fp) && ($current_line =
fgets($fp)) !== false) { $_result .= $current_line; } fclose($fp); return
$_result; } $smarty = isset($this->smarty) ? $this->smarty : $this; if
($smarty->error_unassigned) { throw new SmartyException('Undefined stream
variable "' . $variable . '"'); } else { return null; } }

可以看到这个方法可以读取一个文件并返回其内容，所以我们可以用self来获取Smarty对象并调用这个方法，很多文章里给的payload都形如：{self::getStreamVariable("file:///etc/passwd")}。然而使用这个payload会触发报错如下：

> Fatal error: Uncaught --> Smarty Compiler: Syntax error in template
> "string:<meta http-equiv="...">Current
> IP:{self::getStreamVariable(‘file:///etc/passwd’)}" static class 'self' is
> undefined or not allowed by security setting <\-- thrown in
> /var/www/html/smarty/libs/sysplugins/smarty_internal_templatecompilerbase.php
> on line 12  
>

可见这个旧版本Smarty的SSTI利用方式并不适用于新版本的Smarty。而且在3.1.30的Smarty版本中官方已经把该静态方法删除。对于那些文章提到的利用
Smarty_Internal_Write_File 类的writeFile方法来写shell也由于同样的原因无法使用。

{if}标签

官方文档中看到这样的描述：

> Smarty的{if}条件判断和PHP的if 非常相似，只是增加了一些特性。每个{if}必须有一个配对的{/if}. 也可以使用{else} 和
> {elseif}. 全部的PHP条件表达式和函数都可以在if内使用，如*||*, or, &&, and, is_array(), 等等  
>

既然全部的PHP函数都可以使用，那么我们是否可以利用此来执行我们的代码呢？

将XFF头改为{if phpinfo()}{/if}，可以看到题目执行了phpinfo()

![v2-bddead1f721c42eed678d9db9527c0e7_hd.j](https://pic4.zhimg.com/80/v2-bddead1f721c42eed678d9db9527c0e7_hd.jpg)

用同样的方法可以轻松获得flag

题目漏洞代码

通过getshell之后的文件读取，本题中引发SSTI的代码简化后如下：

<?phprequire_once('./smarty/libs/' . 'Smarty.class.php');$smarty = new
Smarty();$ip =
$_SERVER['HTTP_X_FORWARDED_FOR'];$smarty->display("string:".$ip);}

可以看到这里使用字符串代替smarty模板，导致了注入的Smarty标签被直接解析执行，产生了SSTI。

## 参考资料  

Smarty3的官方手册 https://www.smarty.net/docs/

https://portswigger.net/research/server-side-template-injection

实验时间：

Flask服务端模板注入漏洞：http://www.hetianlab.com/expc.do?ec=ECID87ed-2223-40e5-8083-f5c55d69af28（通过该实验了解服务端模板注入漏洞的危害与利用。）点击阅读原文做实验吧。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

