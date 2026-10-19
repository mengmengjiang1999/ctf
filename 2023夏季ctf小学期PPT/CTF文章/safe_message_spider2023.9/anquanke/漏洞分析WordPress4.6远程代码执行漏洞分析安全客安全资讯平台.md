# 【漏洞分析】WordPress 4.6 远程代码执行漏洞分析

阅读量 **175583**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-05 11:02:13

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

****

**传送门**

[**【漏洞预警】WordPress <4.7.1
远程代码执行漏洞（非插件无需认证，附Poc,演示视频）**](http://bobao.360.cn/news/detail/4146.html)

**0x00 漏洞概述**

**WordPress 4.6
版本远程代码执行漏洞是一个非常严重的漏洞，未经授权的攻击者利用该漏洞就能实现远程代码执行，针对目标服务器实现即时访问，最终导致目标应用服务器的完全陷落。**
无需插件或者非标准设置，就能利用该漏洞。Dawid Golunski ([
**@dawid_golunski**](https://twitter.com/dawid_golunski)) 还在poc中为我们展示了精彩的替换 ／
和 “ ”(表示空格)的技巧。

  

**0x01 漏洞分析**

整个过程利用了 WordPress 未对请求的 Host 字段进行校验和 PHPMailer 在 小于 5.2.20
版本存在的代码执行漏洞。对以上两个不安全点进行利用，导致远程代码执行。

POC地址为： [WordPress-Exploit-4-6-RCE-CODE-EXEC-CVE-2016-10033](https://exploitbox.io/vuln/WordPress-Exploit-4-6-RCE-CODE-EXEC-CVE-2016-10033.html)

我们测试的命令为

    
    
    /usr/bin/touch /tmp/manning.test

我们看下POC发出的请求

Host 字段构造如下

    
    
     Host: target(any -froot@localhost -be ${run{${substr{0}{1}{$spool_directory}}usr${substr{0}{1}{$spool_directory}}bin${substr{0}{1}{$spool_directory}}touch${substr{10}{1}{$tod_log}}${substr{0}{1}{$spool_directory}}tmp${substr{0}{1}{$spool_directory}}manning.test}} null)

这点跟我们认知中的Host完全不一样。

接下来的流程非常简单。

在 wp-login.php 中，首先根据请求中的 action 进行路由

接着进入函数 retrieve_password

接着进入 wp_mail 函数，位于文件 pluggable.php

在 wp_mail 中，WordPress 会把 _SERVER['SERVER_NAME'] 变量拼接到 from_email 变量中。

经过一系列的邮件内容拼接，把类对象 phpmailer 的类变量都进行了赋值，之后进入调用了 Send 函数

这里把最关键的 mailSend 函数贴出来，mailSend 函数负责最终调用，关键在 mailPassthru 函数，该函数会把带有恶意的 params
变量交给 PHPMailer。

    
    
    protected function mailSend($header, $body)
    {
        $toArr = array();
        foreach ($this->to as $toaddr) {
            $toArr[] = $this->addrFormat($toaddr);
        }
        $to = implode(', ', $toArr);
        if (empty($this->Sender)) {
            $params = ' ';
        } else {
            $params = sprintf('-f%s', $this->Sender);
        }
        if ($this->Sender != '' and !ini_get('safe_mode')) {
            $old_from = ini_get('sendmail_from');
            ini_set('sendmail_from', $this->Sender);
        }
        $result = false;
        if ($this->SingleTo && count($toArr) > 1) {
            foreach ($toArr as $toAddr) {
                $result = $this->mailPassthru($toAddr, $this->Subject, $body, $header, $params);
                $this->doCallback($result, array($toAddr), $this->cc, $this->bcc, $this->Subject, $body, $this->From);
            }
        } else {
            $result = $this->mailPassthru($to, $this->Subject, $body, $header, $params);
            $this->doCallback($result, $this->to, $this->cc, $this->bcc, $this->Subject, $body, $this->From);
        }
        if (isset($old_from)) {
            ini_set('sendmail_from', $old_from);
        }
        if (!$result) {
            throw new phpmailerException($this->lang('instantiate'), self::STOP_CRITICAL);
        }
        return true;
    }

动态调试，在 mailPassthru 调用时，整个变量如图所示。

最终在 mailPassthru 内调用了 @mail。

最终我们在 tmp 目录看到了 manning.test 文件

  

**0x02 补丁分析**

WordPress 4.7.1 版本

1，升级phpmailer的版本到5.2.22

2，在 mailSend 修改，对变量 params 进行了过滤。

    
    
    protected function mailSend($header, $body)
    {
        $toArr = array();
        foreach ($this->to as $toaddr) {
            $toArr[] = $this->addrFormat($toaddr);
        }
        $to = implode(', ', $toArr);
        $params = null;
        //This sets the SMTP envelope sender which gets turned into a return-path header by the receiver
        if (!empty($this->Sender) and $this->validateAddress($this->Sender)) {
            // CVE-2016-10033, CVE-2016-10045: Don't pass -f if characters will be escaped.
            if (self::isShellSafe($this->Sender)) {
                $params = sprintf('-f%s', $this->Sender);
            }
        }
        if (!empty($this->Sender) and !ini_get('safe_mode') and $this->validateAddress($this->Sender)) {
            $old_from = ini_get('sendmail_from');
            ini_set('sendmail_from', $this->Sender);
        }
        $result = false;
        if ($this->SingleTo and count($toArr) > 1) {
            foreach ($toArr as $toAddr) {
                $result = $this->mailPassthru($toAddr, $this->Subject, $body, $header, $params);
                $this->doCallback($result, array($toAddr), $this->cc, $this->bcc, $this->Subject, $body, $this->From);
            }
        } else {
            $result = $this->mailPassthru($to, $this->Subject, $body, $header, $params);
            $this->doCallback($result, $this->to, $this->cc, $this->bcc, $this->Subject, $body, $this->From);
        }
        if (isset($old_from)) {
            ini_set('sendmail_from', $old_from);
        }
        if (!$result) {
            throw new phpmailerException($this->lang('instantiate'), self::STOP_CRITICAL);
        }
        return true;
    }

**0x03 防护建议**

升级 WordPress 至最新版本。

  

**0x04 调试总结**

调试过程中需要注意：

sendmail 需要装 exim4扩展

需要更改poc中的账户，poc中填写的是admin

poc运行环境需要有python环境

**本次调试环境是：**

Server version: Apache/2.4.18 (Ubuntu)

PHP 7.0.15-0ubuntu0.16.04.4 (cli) ( NTS )

sendmail 和 exim4扩展

其他注意事项可以参考 [**@Tomato菜的要死**](http://weibo.com/tomato4web) 和
[**@廖新喜1**](http://weibo.com/u/1900013681) 的微博。

  

**0x05 参考文章**

<https://exploitbox.io/vuln/WordPress-Exploit-4-6-RCE-CODE-EXEC-CVE-2016-10033.html>

  

**传送门**

* * *

[**【漏洞预警】WordPress <4.7.1
远程代码执行漏洞（非插件无需认证，附Poc,演示视频）**](http://bobao.360.cn/news/detail/4146.html)

  

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86022](/post/id/86022)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

