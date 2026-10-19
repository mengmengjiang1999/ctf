某IP设备代码审计

[ H_00c8](https://www.jianshu.com/u/3cf70976a08b)关注赞赏支持

# 某IP设备代码审计

image

偶尔看到一个设备的漏洞挖掘。尝试也看了一下代码。如下：

参考：<https://www.jianshu.com/p/b489111c7c49>

# 漏洞一、任意文件上传

    
    
    <?php
    
    $error = false;
    $tmpFilePath = $_FILES['upload']['tmp_name'];
    $tmpFilePath = mb_convert_encoding($tmpFilePath, "GBK", "UTF-8");
    
    if ($tmpFilePath != ""){
        $newFilePath = "./files/" . $_FILES['upload']['name'];
    
        if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN'){
            $newFilePath = mb_convert_encoding($newFilePath, "GBK", "UTF-8"); 
        }
    
        if(!move_uploaded_file($tmpFilePath, $newFilePath)) {
            $error = true;
        }
    }
    
    ?>
    

URL：/upload/my_parser.php

>
> [**【点击查看学习资料·攻略】**](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.oschina.net%2Faction%2FGoToLink%3Furl%3Dhttps%253A%252F%252Fdocs.qq.com%252Fdoc%252FDVFNpaGJvRFJiQ2Ro)

参数为upload

image

访问URL：/upload/files/11.php

# 漏洞二、任意文件上传

URL:/php/addscenedata.php

    
    
    <?php
        require_once ('conversion.php');
    
        $arr['res'] = 0;
        $tmpFilePath = $_FILES['upload']['tmp_name'];   
        if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN') {
            $tmpFilePath = mb_convert_encoding($tmpFilePath, "GBK", "UTF-8");
        }
    
        if ($tmpFilePath != ""){
            $newFilePath = "../images/scene/" . $_FILES['upload']['name'];
            if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN') {
                $newFilePath = mb_convert_encoding($newFilePath, "GBK", "UTF-8");
            }
    
            if(move_uploaded_file($tmpFilePath, $newFilePath))
            {
                $arr['res'] = 1;
            }
        }
    
        echo JSON($arr);
    
    ?>
    
    

# 漏洞三、任意文件写入

URL:/php/uploadjson.php

    
    
    <?php
        require_once ('conversion.php');
    
        $arr['res'] = 0;
        $tmpFilePath = $_FILES['upload']['tmp_name'];   
        if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN') {
            $tmpFilePath = mb_convert_encoding($tmpFilePath, "GBK", "UTF-8");
        }
    
        if ($tmpFilePath != ""){
            $newFilePath = "../images/scene/" . $_FILES['upload']['name'];
            if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN') {
                $newFilePath = mb_convert_encoding($newFilePath, "GBK", "UTF-8");
            }
    
            if(move_uploaded_file($tmpFilePath, $newFilePath))
            {
                $arr['res'] = 1;
            }
        }
    
        echo JSON($arr);
    
    ?>
    
    

image

# 漏洞四、任意文件上传

URL:/php/addupdatefiles.php

    
    
    <?php
    
    $tmpFilePath = $_FILES['upload']['tmp_name'];
    $tmpFilePath = mb_convert_encoding($tmpFilePath, "GBK", "UTF-8");
    
    if ($tmpFilePath != ""){
        $newFilePath = dirname(dirname(dirname(dirname(__FILE__))))."/upload/" . $_FILES['upload']['name'];
    
        if (strtoupper(substr(PHP_OS, 0, 3)) == 'WIN'){
            $newFilePath = mb_convert_encoding($newFilePath, "GBK", "UTF-8");
        }
    
        if(!move_uploaded_file($tmpFilePath, $newFilePath)) {
            echo '{"res": "1"}';
        } else {
            echo '{"res": "0"}';
        }
    }
    ?>
    

任意文件读取

/php/getjson.php

    
    
    <?php
        require_once ('conversion.php');
    
        $res = '{"res":"0"}';
        $postData = $_POST['jsondata']; 
        if (isset($postData['filename']))
        {   
            $filename = $postData['filename'];      
            // WIN
            $fullpath = dirname(dirname(__FILE__))."\\lan\\".$filename; 
            // Linux
            if (strtoupper(substr(PHP_OS, 0, 3)) != 'WIN') {
                $fullpath = dirname(dirname(__FILE__))."/lan/".$filename; 
            }
    
            if (file_exists($fullpath))
            {
                $json_string = file_get_contents($fullpath);
                $res = '{"res":"1","data":'.$json_string.'}';
            }
        }
        echo $res;
    ?>
    

最重要的login.php 来了

    
    
    最重要的login.php 来了
    
    <?php
        require_once ('conversion.php');
    
        $postData = $_POST['jsondata'];
        $arr['res'] = 0;
    
        if (isset($postData['username'])) {
            $user = $postData['username'];
            $pass = $postData['password'];
    
            if ('800823' == $pass && 'administrator' == $user)
            {
                $arr['username'] = 'administrator';
                $arr['password'] = '800823';
                $arr['display'] = 'administrator';
                $arr['modules'] = '1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1';
                $arr['rights'] = '*';
                $arr['serverrights'] = '*';
                $arr['isadmin'] = '1';
                $arr['bindterminals'] = '';
                $arr['res'] = 1;
                $arr['mainurl'] = 'main';
                $arr['token'] = 'SESSION';
                echo JSON($arr);
            }
            else
            {
                $result = UdpSendAndRecvJson($postData, "login");
                echo $result;
            }
        }
    ?>
    

**最后**  
**有在学习网络安全的可以点击查看【[网络安全学习资料·攻略](https://links.jianshu.com/go?to=https%3A%2F%2Fwww.oschina.net%2Faction%2FGoToLink%3Furl%3Dhttps%253A%252F%252Fdocs.qq.com%252Fdoc%252FDVFNpaGJvRFJiQ2Ro)】**

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [【网络安全】php代码审计-sql注入进阶篇](https://www.jianshu.com/p/4406404784b5)

前言 经过上一篇文章我们已经大概的了解sql注入去怎样审计了。但是在实际的网站中和用户的输入输出接口不可能想那样没...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 114评论 0赞 1

  * [【安全漏洞】挖洞小记](https://www.jianshu.com/p/44596e7514e4)

前言：上个月月初开始，在那些项目结束之后进入了挖洞时期，每天的日常工作就是挖洞，除非有临时的项目才会停下，最近在整...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 540评论 0赞 6

  * [Web 文件管理器elFinder 的漏洞链分析](https://www.jianshu.com/p/8b7f2d483cf0)

应用程序与文件系统的交互始终是高度安全敏感的，因为较小的功能漏洞很容易成为可利用漏洞的来源。这种观察在web文件管...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 959评论 0赞 1

  * [【CTF大赛】100步getshell之就差一步——The MOVAPS issue](https://www.jianshu.com/p/da83768cac31)

SE版的前台sql注入漏洞。 此漏洞仅仅影响 骑士CMS人才系统SE版 在/application/index/c...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 172评论 0赞 1

  * [系统漏洞挖掘展示（SE版的前台sql注入漏洞）](https://www.jianshu.com/p/09e0e0b19e47)

SE版的前台sql注入漏洞。 此漏洞仅仅影响 骑士CMS人才系统SE版 在/application/index/c...

[H_00c8](https://www.jianshu.com/u/3cf70976a08b)阅读 121评论 0赞 1

 