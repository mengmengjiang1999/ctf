# PHP文件包含小总结

阅读量 **570786**

|评论 **4**

发布时间 : 2021-04-30 12:00:13

 **x**

##### 译文声明

本文是翻译文章，文章原作者 酒仙桥6号部队，文章来源：酒仙桥6号部队

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t017fe4d379d53c5c49.png)

## 1.前言

最近在某个项目上天天挖洞，每天不是什么信息泄露就是xss，没有一个能getshell，愁的不行，感觉头顶都凉飕飕了。不知是早上出门时，没注意踩到狗屎，还是今天运气好，发现一处竟然有文件包含漏洞，百度一波getshell姿势，逐一尝试后，发现可以利用日志getshell。这里本地模拟一下当时情况，复现一下。同时就让我这个小菜鸡总结一下getshell方式，以便之后遇到文件包含漏洞更快的去拿shell。

![](https://p0.ssl.qhimg.com/t01c7d4d12189f06150.jpg)

### 1.1.本地复现

  1. 当时发现url中有一个参数file=/home/task.php，灵机一动，把/home/task.php替换成了../../../../../../etc/passwd
  2. 接着发送带有php代码的请求，先phpinfo试一试。
  3. 接着就是包含日志了，感觉马上就要起飞了，结果很突然，no such file了，又换了几个路径，还是这样。
  4. 没办法只是试试包含一下配置文件，结果….一样。
  5. 这可咋办，眼瞅着就要getshell了，没路径啊，突然想到还有一个ssh log可以尝试包含一下，立刻来了精神头，噼里啪啦一顿敲，食指放在回车键上，犹豫不决，豁出去了！只见我眼睛一闭，重重按下回车，当我慢慢睁开眼时，欣喜若狂，终于没有no such file 了
  6. 接下来就很简单了直接ssh连接：

> ssh ‘<?=eval($_REQUEST[1])?>’@remotehost

  7. 包含ssh log文件，然后执行下命令：id。成功！

![](https://p5.ssl.qhimg.com/t0115c2ef0bfbb4cd2b.png)

## 2.文件包含小知识

### 2.1.包含函数

1、PHP共有4个与文件包含相关的函数：

include

require

include_once

require_once

2、Include与include_once的区别：

（1）Include：会将指定的文件载入并执行里面的程序；重复引用的情况下加载多次。

例如：

![](https://p3.ssl.qhimg.com/t01e7907f8167f25a4b.png)

> 这里include两次1.php文件，所以就会包含1.php两次。

（2）Include_once：会将指定的文件载入并执行里面的程序；此行为和include语句类似，唯一区别是如果该文件中已经被包含过，则不会再次包含。

例如：

![](https://p4.ssl.qhimg.com/t017b4d11854a579092.png)

这里include_once了两次1.php文件，但只会包含1.php一次。

（3）require和requireonce的用途与上面两个一样，但区别就是require和requireonce会加载页面最开始执行。Include和include_once会按代码顺序执行。

### 2.2.支持的协议和封装协议

> File:// ——访问本地文件系统
>
> http(s):// ——访问HTTP（s）网址
>
> ftp:// ——访问FTP(s) URLs
>
> php:// ——访问各个输入/输出流（I/O streams）
>
> zlib:// ——压缩流
>
> data:// ——数据（RFC 2397）
>
> glob:// ——查找匹配的文件路径模式
>
> phar:// ——PHP归档
>
> ssh2:// ——Secure Shell 2
>
> rar:// ——RAR
>
> ogg:// ——音频流
>
> expect:// ——处理交互式的流

### 2.3.常用伪协议讲解：

1\. file://

（1）这个协议可以展现本地文件系统，默认目录是当前的工作目录。

（2）例如：file:///etc/passwd、file://key.txt

2\. php://

(1) php://input是个可以访问请求的原始数据的只读流，可以访问请求的原始数据的只读流，将post请求中的数据作为php代码执行。

(2) php://filter是一种元封装器，设计用于数据流打开时的筛选过滤应用。

![](https://p5.ssl.qhimg.com/t01c0ca3e21a951c093.png)

3、phar://

（1）phar://数据流包装器自PHP5.3.0起开始有效

（2）例如：phar://E:/phpstudy/www/1.zip/phpinfo.txt

phar://1.zip/phpinfo.txt

### 2.4.伪协议利用方式小总结:

![](https://p0.ssl.qhimg.com/t01336202e75375a8e1.png)

## 3.getshell总结

### 3.1.Getshell之session

条件：session文件路径已知，且session文件中内容部分可控。

获取session文件路径：

> 1、session文件的保存路径可以在phpinfo的session.save_path看到。

![](https://p0.ssl.qhimg.com/t01db9ad9b9c8b66ce2.png)

> 2、默认路径：
>
> /var/lib/php/sess_PHPSESSID
>
> /var/lib/php/sess_PHPSESSID
>
> /tmp/sess_PHPSESSID
>
> /tmp/sessions/sess_PHPSESSID
>
> session的文件名格式为sess_[phpsessid]。而phpsessid在发送的请求的cookie字段中可以看到。

![](https://p2.ssl.qhimg.com/t01ca56af391b2a1127.png)

利用：

1.要包含并利用的话，需要能控制部分sesssion文件的内容。可以先包含进session文件，观察里面的内容，然后根据里面的字段来发现可控的变量，从而利用变量来写入payload，并之后再次包含从而执行php代码。

2.例如现在有一个session.php可控用户会话信息值：

![](https://p4.ssl.qhimg.com/t015315eb45847d2ec0.png)

3.可以看到这个session.php文件中的用户会话信息username的值是用户可控制的，那我们就可以传入恶意代码进行攻击利用。

![](https://p2.ssl.qhimg.com/t01f4228b3d229cbb74.png)

4.将恶意代码传入以后，接下来就要利用文件包含漏洞去包含这个恶意代码。

![](https://p5.ssl.qhimg.com/t016b505c8b9e82ad1e.png)

5.从返回结果来看，我们的payload和恶意代码已经正常解析和执行。

### 3.2.Getshell之日志

**3.2.1.访问日志**

条件：需要知道服务器日志的存储路径，且日志文件可读。

日志存储默认路径：

> 1.apache+Linux日志默认路径：/etc/httpd/logs/accesslog或/var/log/httpd/accesslog
>
>
> 2.apache+win2003日志默认路径：D:xamppapachelogsaccess.log、D:xamppapachelogserror.log
>
> 3.IIS6.0+win2003默认日志文件：C:WINDOWSsystem32Logfiles
>
> 4.IIS7.0+win2003 默认日志文件：%SystemDrive%inetpublogsLogFiles
>
> 5.nginx
> 日志文件：日志文件在用户安装目录logs目录下,假设安装路径为/usr/local/nginx,那日志目录就是在/usr/local/nginx/logs下面

利用：

1.多数情况，web服务器会将请求写入到日志文件中，比如说apache。在用户发起请求时，会将请求写入access.log，当发生错误时将错误写入error.log。默认情况下，日志保存路径在/etc/httpd/logs/下。

2.但如果是直接发起请求，会导致一些符号被编码使得包含无法正确解析。可以使用burp截包后修改。

![](https://p5.ssl.qhimg.com/t01a3af36ffc6967a65.png)

3.正常的php代码已经写入了 /etc/httpd/logs/access.log。然后包含即可执行代码。

![](https://p1.ssl.qhimg.com/t01d6bb7a6af0406b66.png)

4.但有的时候，log的存放地址会被更改。这个时候可以通过读取相应的配置文件后，再进行包含。

中间件默认配置文件存放路径：

> 1.apache+linux 默认配置文件
>
> /etc/httpd/conf/httpd.conf或/etc/init.d/httpd
>
> 2\. IIS6.0+win2003 配置文件
>
> C:/Windows/system32/inetsrv/metabase.xml
>
> 3\. IIS7.0+WIN 配置文件
>
> C:WindowsSystem32inetsrvconfigapplicationHost.config

**3.2.2.SSH log**

条件：需要知道ssh-log的位置，且可读。

ssh日志默认路径：

1./var/log/auth.log

2./var/log/secure

利用：

1.用ssh连接：

> ssh ‘<?php phpinfo(); ?>’@remotehost
>
> 之后会提示输入密码，随便输入就可以。

![](https://p1.ssl.qhimg.com/t01eda30a9d222529dc.png)

2.然后利用文件包含，包含日志文件：

![](https://p5.ssl.qhimg.com/t0140a42777fbe2b3f6.png)

### 3.3.Getshell之environ

条件：

  1. php以cgi方式运行，这样environ才会保持UA头。
  2. environ文件存储位置已知，且有权限访问environ文件。

> environ文件默认位置：
>
> proc/self/environ

利用：

> 1.proc/self/environ中会保存user-agent头。如果在user-> agent中插入php代码，则php代码会被写入到environ中。之后再包含它，即可。
>
> 2.例如我们现在访问一个网站，使用burpsuite抓包，将恶意代码插入到user-agent中。

![](https://p3.ssl.qhimg.com/t010077ec6fbaf82357.png)

3.利用文件包含漏洞去包含proc/self/environ，成功执行php代码。

![](https://p1.ssl.qhimg.com/t017fbe8e5d58cfe6fa.png)

### 3.4.Getshell之利用phpinfo

条件：存在phpinfo页面并且存在文件包含漏洞

![](https://p0.ssl.qhimg.com/t0132e46dca8fdf379a.jpg)

原理：

  1. 当我们给PHP发送POST数据包时，如果数据包里包含文件区块，PHP就会将文件保存成一个临时文件，路径通常为：/tmp/php[6个随机字符],这个临时文件，在请求结束后就会被删除。
  2. 因为phpinfo页面会将请求上下文中的所有变量打出来，所以我们如果向phpinfo页面发送包含文件区块的数据包，就可以在返回包里找到临时文件名，也就是$_FILES变量中的内容。

利用：

  1. 首先我们使用vulhub的脚本（https://github.com/vulhub/vulhub/blob/master/php/inclusion/exp.py），他可以实现包含临时文件，而这个临时文件的内容是：<?php fileputcontents(‘/tmp/p’,'<?=eval($_REQUEST[1])?>’)?>。成功包含这个文件后就会生成新的文件/tmp/p，这个文件就会永久的留在目标机器上。
  2. 写入成功以后，我们利用文件包含来执行任意命令。

![](https://p0.ssl.qhimg.com/t018d9a829b2a655ec0.png)

原理：

那么为啥vulhub的脚本是如何做到在临时脚本文件删除前去包含的呢，其实就是用到了条件竞争，具体流程大致如下：

  1. 首先发送包含webshell的数据包给phpinfo页面，并用大量的垃圾数据将header和get等位置填满。
  2. 因phpinfo页面会将所有数据打印出来，第一个步骤中的垃圾数据就会将phpinfo页面撑的非常大。而php默认输出缓冲区大小为4096，也可以理解为php每次返回4096个字节给socket连接。
  3. 所以，这里直接操作原生socket，每次读取4096个字节。只要我们读取到字节里包含临时文件名，就立刻发送文件包含漏洞利用的数据包。因为第一个数据包的socket连接没有结束，所以临时文件还没有删除，我们就可以文件包含成功。

### 3.5.Getshell之上传文件

条件：有上传点，知道上传上去的文件名和存放目录。

利用：

  1. 这里用一个靶场简单演示一下，找个文件上传点，上传一个带有php恶意代码的图片。

![](https://p5.ssl.qhimg.com/t016ec965d97b6d681f.png)

  2. 我们现在已知文件名称和路径，可以利用文件包含漏洞去包含这个图片，就可以成功执行php代码了。

![](https://p3.ssl.qhimg.com/t018af5c59f487a0651.png)

## 4.应对措施

1、在很多场景中都需要去包含web目录之外的文件，如果php配置了open_basedir，则会包含失败。

2、对可以包含的文件进行限制，可以采用白名单的方式，或设置可以包含的目录。

3、对危险字符进行过滤。

4、尽量不使用动态包含等等

本文翻译自酒仙桥6号部队 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **酒仙桥六号部队** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/232358](/post/id/232358)

安全客 - 有思想的安全新媒体

本文转载自: [酒仙桥6号部队]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [渗透测试](/tag/渗透测试)

 **+1** __23赞

 __收藏

![](https://p3.ssl.qhimg.com/t0110bc5d794d277012.png) 酒仙桥六号部队

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

