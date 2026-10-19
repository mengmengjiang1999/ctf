## [phpcms2008远程代码执行漏洞](https://bbs.ichunqiu.com/thread-48298-1-1.html)  

## 描述：

近日，互联网爆出PHPCMS2008代码注入漏洞（CVE-2018-19127）。攻击者利用该漏洞，可在未授权的情况下实现对网站文件的写入。该漏洞危害程度为高危(High)。目前，漏洞利用原理已公开，厂商已发布新版本修复此漏洞。

## 影响范围：

PHPCMS2008 sp4及以下版本

## POC github地址：

<https://github.com/ab1gale/phpcms-2008-CVE-2018-19127>

## 漏洞分析：

在type.php中：  
包含/include/common.inc.php 其作用是对$_GET,$_POST等全局变量进行注册。

![image.png](https://image.3001.net/images/20181129/1543480966_5bffa686cd670.png!small)

extract函数大家都明白，将数组的项注册为变量。可以对任意变量进行注册。  
在type.php第30行调用template函数

![image.png](https://image.3001.net/images/20181129/1543480980_5bffa69481fa8.png!small)

template函数定义在global.func.php

![image.png](https://image.3001.net/images/20181129/1543481004_5bffa6ac414fd.png!small)

![image.png](https://image.3001.net/images/20181129/1543481019_5bffa6bb41f34.png!small)![image.png](https://image.3001.net/images/20181129/1543481024_5bffa6c0d8e82.png!small)  

$template变量在这里是完全可控的，且默认开启模版缓存自动刷新。当template变量输入为template=tag_(){};@unlink(FILE);assert($_POST[1]);{//../rss时，$compiledtplfile="data/cache_template/phpcmstag(){};@unlink(FILE);assert($_POST[1]);{//../rss.tpl.php"
.此时，可自然进入判断 ，调用template_compile函数，次函数定义在include/template.func.php

![image.png](https://image.3001.net/images/20181129/1543481033_5bffa6c97ec43.png!small)

在templatecompile函数中，$template变量是我们可控的，而$content变量当我们的输入为"template=tag(){};@unlink(FILE);assert($_POST[1]);{//../rss"自然会选择前者，而content内容中$template变量可控，最后file_put_contents函数写入任意代码，需要注意的是，file_put_contents路径为data/cache_template/phpcmstag(){};@unlink(FILE);assert($_POST[1]);  
{//../rss.tpl.php时，php会将其路径解析为data/cache_template/rss.tpl.php。

![image.png](https://image.3001.net/images/20181129/1543481072_5bffa6f08b50b.png!small)

## 总结一下：

type.php 包含common.inc.php
任意变量注册-》$template变量可控->template函数变量$template可控->template_compile函数变量$template可控-》file_put_contents函数由$template影响两个参数变量可控，借助php此函数解析文件特性，将一句话写入文件。

## 漏洞修复：

升级至最新版本

## REFERECE:

<https://github.com/ab1gale/phpcms-2008-CVE-2018-19127>

<http://cve.mitre.org/cgi-bin/cvename.cgi?name=2018-19127>

#  

