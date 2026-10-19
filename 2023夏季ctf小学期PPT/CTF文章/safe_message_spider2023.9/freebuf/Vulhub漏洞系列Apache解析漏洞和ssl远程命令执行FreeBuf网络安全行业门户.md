# Apache换行解析、多后缀解析、以及ssl远程命令执行漏洞分析

**本文章适合正在利用vulhub进行漏洞复现的朋友，或者准备学习漏洞复现的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于vulhub的使用技巧和一些漏洞原理，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇文章解决了一个困扰了我很多天的问题，那一刻真的很开心。复现的过程有时候真的很痛苦，希望大家一定要坚持住！本文如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏。**  

##  1.Apache简介：

Apache HTTP Server（简称 ）是 的一个开放源码的网页服务器，可以在大多数计算机操作系统中运行，由于其多平台和安全性 Apache
Apache软件基金会
被广泛使用，是最流行的Web服务器端软件之一。它快速、可靠并且可通过简单的API扩展，将Perl/Python等解释器编译到服务器中。 [2] Apache
HTTP服务器是一个模块化的服务器，源于NCSAhttpd服务器，经过多次修改，成为世界使用排名第一的 软件。

## 2.漏洞描述：

### Apache换行解析漏洞：

Apache
HTTPD是一款HTTP服务器，它可以通过mod_php来运行PHP网页。其2.4.0~2.4.29版本中存在一个解析漏洞，在解析PHP时，1.php\x0A将被按
照PHP后缀进行解析，导致绕过一些服务器的安全策略。

###  **Apache多后缀解析漏洞：**

在有多个后缀的情况下，只要一个文件含有.php后缀的文件即将被识别成PHP文件，没必要是最后一个后缀。利用这个特性，将会造成一个可以绕过上传白
名单的解析漏洞。

###  **Apache ssl远程命令执行漏洞：**

在测试任意文件上传漏洞的时候，目标服务端可能不允许上传php后缀的文件。如果目标服务器开启了SSI与CGI支持，我们可以上传一个shtml文件，并利用<!--#exec
cmd="id" --> 语法执行任意命令。

## 3.漏洞原理：

### Apache换行解析漏洞  

apache这次解析漏洞的根本原因就是这个
$，正则表达式中，我们都知道$用来匹配字符串结尾位置，我们来看看$符号在正则表达式中的含义：匹配输入字符串的结尾位置。 **如果设置了 RegExp 对象的
Multiline 属性，则 $ 也匹配 '\n' 或 '\r'。** 要匹配 $ 字符本身，请使用 \$。  

因此产生这个漏洞的根本原因就是 **设置了 RegExp 对象的 Multiline 属性，从而使得$可以匹配换行符。**

那我们进入docker环境中看一看apache2是如何配置的  

![image.png](https://image.3001.net/images/20200109/1578540240_5e169cd09d620.png!small)  

很明显这里使用了$符号

我们再来看一看其他版本apaceh的模块中对于php的配置文件：

    
    
    <FilesMatch ".+\.ph(p[3457]?|t|tml)$">
        SetHandler application/x-httpd-php
    </FilesMatch>
    <FilesMatch ".+\.phps$">
        SetHandler application/x-httpd-php-source
        # Deny access to raw php sources by default
        # To re-enable it's recommended to enable access to the files
        # only in specific virtual host or directory
        Require all denied
    </FilesMatch>
    # Deny access to files without filename (e.g. '.php')
    <FilesMatch "^\.ph(p[3457]?|t|tml|ps)$">
        Require all denied
    </FilesMatch>
    
    # Running PHP scripts in user directories is disabled by default
    #
    # To re-enable PHP in user directories comment the following lines
    # (from <IfModule ...> to </IfModule>.) Do NOT set it to On as it
    # prevents .htaccess files from disabling it.
    <IfModule mod_userdir.c>
        <Directory /home/*/public_html>
            php_admin_flag engine Off
        </Directory>
    </IfModule>  
    

可以看到这里相对docker环境中的多了几种php后缀的识别,如果这里的$设置过RegExp 对象的 Multiline
属性,那么该版本的apache也将存在换行解析漏洞。  

 **php php3 php4 php5 php7 pht phtml**  

 **  
**

### Apache多后缀解析漏洞：

配置文件内容  
---  
AddType text/html . html  
AddLanguage zh-CN .c  
  
  
其给.html后缀增加了media-type，值为text/html；给.cn后缀增加了语言，值为zh-CN。此时，如果用户请求文件 .html
index.cn ，他将返回一个中 文的html页面。

那么，在有多个后缀的情况下，只要一个文件含有.php后缀的文件即将被识别成PHP文件，没必要是最后一个后缀。利用这个特性，将会造成一个可以绕过
上传白名单的解析漏洞。

我们会在漏洞利用部分做一个实验。

###  **Apache ssl远程命令执行漏洞：**

SSI（服务器端包含）是放置在HTML页面中的指令，并在服务页面时在服务器上对其进行评估。它们使您可以将动态生成的内容添加到现有的HTML页面，
而不必通过CGI程序或其他动态技术来提供整个页面。

其实apache的ssl更像是flask的jinjia2，用来实现和前端实现一种动态交互，只不过在配置ssl之后，如果上传接口没有过滤掉.shtml文件，那么就可以就其中
包含我们要执行的命令。

<!--#exec cmd="ls -al" -->  

## 4.漏洞利用：  

### Apache换行解析漏洞：

 **实验1** ：

这里有一个小知识就是如何进入docker容器内部：

查看镜像资源  
---  
docker ps  
  
  
为容器打开一个shell环境  
---  
docker exec -it containerID /bin/bash  
  
  
  

**![image.png](https://image.3001.net/images/20200109/1578540789_5e169ef5281ca.png!small)**为了方便起见我们docker容器内部装一个vim  

安装命令  
---  
 **apt-get update  
apt-get install vim**  
  
  
  

在上传利用之前，我们先在var/www/html目录下创建一个带有换行标志的文件  

vim
hack.php$'\n'![image.png](https://image.3001.net/images/20200109/1578540845_5e169f2d5844b.png!small)接下来用浏览器访问该文件![image.png](https://image.3001.net/images/20200109/1578540860_5e169f3cafda6.png!small)验证成功。说明该版本的apache是存在此漏洞的。  

 **实验2：**

接下来我们通过上传的方式再次去验证一下漏洞（ **注意：这里有个很大的坑** ）

我们先来看一下docker环境中index.php的内容

index.php

    
    
    <?php
    if(isset($_FILES['file'])) {
        $name = basename($_POST['name']);
        $ext = pathinfo($name,PATHINFO_EXTENSION);
        if(in_array($ext, ['php', 'php3', 'php4', 'php5', 'phtml', 'pht'])) {
            exit('bad file');
        }
        move_uploaded_file($_FILES['file']['tmp_name'], './' . $name);
    }
    ?>  
    

注意这里只给了一个index.php文件，复现到这，我以为vulhub作者忘掉了一个上传的html页面，我特意的写了上去

    
    
    <html>
        <head>upload</head>
        <body>
            <form action="index.php" method='post' enctype='multipart/form-data'>
                <input type='file' name='file'>
                <input type='text' name='name'>
                <input type='submit'>
            </form>
        </body>
    </html>

打开上传页面

![image.png](https://image.3001.net/images/20200109/1578561582_5e16f02ef0c5a.png!small)  

![image.png](https://image.3001.net/images/20200109/1578561593_5e16f039f0cc3.png!small)

![image.png](https://image.3001.net/images/20200109/1578562441_5e16f389770d0.png!small)  
这之后就是无尽的报错之路，百度、Google、改目录、修权限。从复现到放弃。缓了好几天之后，下决心要解决这个问题。搜了好多文章没有一个解释这个问题。

我先写了一个正常的上传PHP文件

    
    
    <?php
    if(isset($_FILES['file'])) {
        $temp = explode(".", $_FILES["file"]["name"]);
        $extension = end($temp);
        echo $name;
        if(in_array($extension, ['php', 'php3', 'php4', 'php5', 'phtml', 'pht'])) {
            exit('bad file');
        }
        move_uploaded_file($_FILES['file']['tmp_name'], 'upload/' . $_FILES["file"]["name"]);
        echo "123";
    }
    ?>  
    

和之前的进行对比之后，终于知道哪里出问题了。

通过自己写的html文件进行上传name的地方没有文件名（注意：这里我们一定要自己补上）为什么要这样做？因为vulhub给出的

php文件是通过$_POST['name']获取文件名的。

    
    
     $name = basename($_POST['name']);

 **注意：下边这种方式获取文件名是会自动去掉换行符的。所以该漏洞不能使用该方法获取文件名。**

    
    
    $_FILES["file"]["name"]

  

![image.png](https://image.3001.net/images/20200109/1578562367_5e16f33f08bb8.png!small)  

可以看到我们上传成功了。

![image.png](https://image.3001.net/images/20200109/1578559606_5e16e8766aa33.png!small)  
  
![image.png](https://image.3001.net/images/20200109/1578562713_5e16f499e7243.png!small)  
![image.png](https://image.3001.net/images/20200109/1578562671_5e16f46f4601b.png!small)

  

  

### Apache多后缀解析漏洞：  

**![image.png](https://image.3001.net/images/20200109/1578540894_5e169f5e9b0e2.png!small)  
**

![image.png](https://image.3001.net/images/20200109/1578540997_5e169fc57e26e.png!small)![image.png](https://image.3001.net/images/20200109/1578541026_5e169fe2aa8a2.png!small)接下来我们做个实验，修改一下该配置文件让其可以识别我们自定义后缀文件为PHP文件。

![image.png](https://image.3001.net/images/20200109/1578541205_5e16a09524608.png!small)

要注意修改完配置文件，一定要重启apache服务但是在docker环境中我们如何做到重启服务又不会退出容器呢？就是这条命令了  
![image.png](https://image.3001.net/images/20200109/1578541241_5e16a0b93888f.png!small)
**service apache2 reload**  

**![image.png](https://image.3001.net/images/20200109/1578541270_5e16a0d6a34f1.png!small)**可以看到我们的info.hacker.xxx.jpg成功的按照php格式执行

###  Apache ssl远程命令执行漏洞：

![image.png](https://image.3001.net/images/20200109/1578541345_5e16a121e44b7.png!small)![image.png](https://image.3001.net/images/20200109/1578541366_5e16a1363e62a.png!small)![image.png](https://image.3001.net/images/20200109/1578541382_5e16a1463dc05.png!small)  

## 5.总结

Apache的漏洞大部分都是配置错误问题，很多程序员不熟悉这些配置或者说不熟悉安全配置问题，故而写出有问题的代码或灾难性的配置文件，这才给黑客可趁之机，造成严重后果。而有的配置问题是apache自带的，那后果将更加严重。所以编写安全的配置文件同样重要。

  
  

  

