# FIX

## Sql Injection

1、常见的SQL注入漏洞主要是由于程序开发过程中不注意规范书写Sql语句以及对特殊字符的不严格过滤，从而导致客户端可以通过全局变量POST和GET提交恶意代码。

2、Fix：基于黑名单、转义、报错

### 黑名单

  * SQL Filter

php

    
    
    $filter = "regexp|from|count|procedure|and|ascii|substr|substring|left|right|union|if|case|pow|exp|order|sleep|benchmark|into|load|outfile|dumpfile|load_file|join|show|select|update|set|concat|delete|alter|insert|create|union|or|drop|not|for|join|is|between|group_concat|like|where|user|ascii|greatest|mid|substr|left|right|char|hex|ord|case|limit|conv|table|mysql_history|flag|count|rpad|\&|\*|\.|-";
    
    if((preg_match("/".$filter."/is",$username)== 1) || (preg_match("/".$filter."/is",$password)== 1)){
        die();
    }
    

### 转义

  * php.ini

php

    
    
    magic_quotes_gpc=on     #php5.4的更高版本中，这个选项被去掉了。
    

magic_quotes_gpc
函数在php中的作用是判断解析用户提示的数据，如包括有:post、get、cookie过来的数据增加转义字符“\”{单引号（’）、双引号（”）与
NULL（NULL 字符）等字符都会被加上反斜线。}，以确保这些数据不会引起程序，特别是数据库语句因为特殊字符引起的污染而出现致命的错误。

  * addslashes() 函数

php

    
    
    addslashes(string) 
    
    addslashes() 函数返回在预定义字符之前添加反斜杠的字符串。
    预定义字符是：单引号（'）双引号（"）反斜杠（\）NULL
    

PS：PHP 5.4 之前 PHP 指令 magic_quotes_gpc 默认是 on， 实际上所有的 GET、POST 和 COOKIE 数据都用被
addslashes() 了。 不要对已经被 magic_quotes_gpc 转义过的字符串使用 addslashes()，因为这样会导致双层转义。
遇到这种情况时可以使用函数 get_magic_quotes_gpc() 进行检测。

### 报错

  * 控制错误信息

php

    
    
    php代码开头添加语句：error_reporting(0);
    

## Unserialize

### PHP

  * PHP7 新特性 为 unserialize() 提供过滤

这个特性旨在提供更安全的方式解包不可靠的数据。它通过白名单的方式来防止潜在的代码注入。

php

    
    
    <?php
    
    // 将所有的对象都转换为 __PHP_Incomplete_Class 对象
    $data = unserialize($foo, ["allowed_classes" => false]);
    
    // 将除 MyClass 和 MyClass2 之外的所有对象都转换为 __PHP_Incomplete_Class 对象
    $data = unserialize($foo, ["allowed_classes" => ["MyClass", "MyClass2"]);
    
    // 默认情况下所有的类都是可接受的，等同于省略第二个参数
    $data = unserialize($foo, ["allowed_classes" => true]);
    
    ?>
    

  * 限制 Session 反序列化

php_serialize 在5.5版本后新加的一种规则，5.4及之前版本，如果设置成php_serialize会报错。

php

    
    
    正确设置序列化及反序列化时使用的处理器
    
    ini_set(‘session.serialize_handler’, ‘php_serialize’); 
    ini_set(‘session.serialize_handler’, ‘php’); 
    
    两者处理session的方式不同，错误使用会形成基于session的反序化漏洞
    

  * 限制 phar 拓展 php 反序列化

php

    
    
    $filter = "phar|zip|compress.bzip2|compress.zlib";
    
    if(preg_match("/".$filter."/is",$name)== 1){
        die();
    }
    

PS：如果不将 compress.bzip2 伪协议进行过滤，有时候漏洞代码仅将phar过滤，但是可以被 compress.bzip2 绕过。

下面举一个具有漏洞代码的栗子

php

    
    
    <?php
    error_reporting(0);
    highlight_file("file_contrary.php");
    $filename=$_GET['filename'];
    if (preg_match("/\bphar\b/A", $filename)) {
        echo "stop hacking!\n";
    }
    else {
        class comrare
        {
            public $haha = 'xxxx';
    
            function __wakeup()
            {
                eval($this->haha);
            }
    
        }
        imagecreatefromjpeg($_GET['filename']);
    }
    ?>
    
    compress.bzip2 绕过
    payload：file_contrary.php?filename=compress.bzip2://phar://upload_file/shell.gif.gif/a
    

  * 配置php.ini禁用特殊函数

特殊函数主要是基于魔法函数、phar拓展php利用函数、序列函数。

    
    
    disable_functions=fileatime,filectime,file_exists,file_get_contents,file_put_content,filegroup,fileinode,filemtime,fileowner,fileperms,is_dir,is_executable,is_file,is_link,is_readable,is_writable,is_writeable,fopen,readfile,unlink,parse_ini_file,file,copy,stat,serialize,unserialize,__construct,__destruct,__toString,__sleep,__wakeup,__get,__set,__isset,__unset,__invoke,

### JAVA

  * 类的白名单校验机制

对所有传入的反序列化对象，在反序列化过程开始前，对类型名称做一个检查，不符合白名单的类不进行反序列化操作。

  * 禁止 JVM 执行外部命令 Runtime.exec

Java 一般来说安全性问题较少，出现的一些问题大部分是利用反射，最终用Runtime.exec(String cmd)函数来执行外部命令的。

java

    
    
    SecurityManager originalSecurityManager = System.getSecurityManager();
            if (originalSecurityManager == null) {
                // 创建自己的SecurityManager
                SecurityManager sm = new SecurityManager() {
                    private void check(Permission perm) {
                        // 禁止exec
                        if (perm instanceof java.io.FilePermission) {
                            String actions = perm.getActions();
                            if (actions != null && actions.contains("execute")) {
                                throw new SecurityException("execute denied!");
                            }
                        }
                        // 禁止设置新的SecurityManager，保护自己
                        if (perm instanceof java.lang.RuntimePermission) {
                            String name = perm.getName();
                            if (name != null && name.contains("setSecurityManager")) {
                                throw new SecurityException("System.setSecurityManager denied!");
                            }
                        }
                    }
    
                    @Override
                    public void checkPermission(Permission perm) {
                        check(perm);
                    }
    
                    @Override
                    public void checkPermission(Permission perm, Object context) {
                        check(perm);
                    }
                };
    
                System.setSecurityManager(sm);
            }
    

## File Upload

### Upload Limit

  * 后端代码限制上传的文件类型（类型&后缀）和大小

php

    
    
    if (($_FILES["Up10defile"]["type"]=="image/gif")&&(substr($_FILES["Up10defile"]["name"], strrpos($_FILES["Up10defile"]["name"], '.')+1))=='gif')&&($_FILES["file"]["size"]<1024000){
    
    }
    else{
      die();
    }
    

  * 强制给上传的文件添加后缀名

在不存在文件包含漏洞的情况下，该方法能最有效的防御攻击者上传执行木马

php

    
    
    if (file_exists("upload_file/" . $_FILES["Up10defile"]["name"]))
    {
        echo $_FILES["Up10defile"]["name"] . " already exists. ";
    }
    else
    {
        move_uploaded_file($_FILES["Up10defile"]["tmp_name"],
        "upload_file/" .$_FILES["Up10defile"]["name"].".gif");
        echo "Stored in: " . "upload_file/" . $_FILES["Up10defile"]["name"].".gif";
    }
    

## File Include

### LFI

  * 本地路径包含限制

php

    
    
    $filename  = $_GET['filename'];
    
    $pattern = "\/|\.\.\/|\.\/|etc|var|php|jpg|jpeg|png|bmp|gif";
    
    if(preg_match("/".$pattern."/is",$filename)== 1){
        echo "die00000000000000000000000000000";
        die();
    }
    
    include($filename);
    

### RFI

  * 远程路径包含限制

php

    
    
    $filename  = $_GET['filename'];
    
    $pattern = "\/|\.\.\/|\.\/|etc|var|php|jpg|jpeg|png|bmp|gif";
    
    if(preg_match("/".$pattern."/is",$filename)== 1){
        echo "die00000000000000000000000000000";
        die();
    }
    
    include($filename);
    

  * 限制环境

php

    
    
    allow_url_fopen = off  （是否允许打开远程文件）  
    allow_url_include = off（是否允许include/require远程文件）
    

### php 伪协议

  * 协议过滤 & 路径访问限制

php

    
    
    $filename  = $_GET['filename'];
    
    $pattern = "\/|\.\.\/|\.\/|etc|var|php|jpg|jpeg|png|bmp|gif|file|http|ftp|php|zlib|data|glob|phar|ssh2|rar|ogg|expect|zip|compress|filter|input";
    
    if(preg_match("/".$pattern."/is",$filename)== 1){
        echo "die00000000000000000000000000000";
        die();
    }
    
    include($filename);
    

## Arbitrary File Reading

### Defense

  * 常见文件读取函数

php

    
    
    file_get_contents()、highlight_file()、fopen()、readfile()、fread()、fgetss()、fgets()、parse_ini_file()、show_source()、file()
    

  * 读取限制

基于目录 & 伪协议

php

    
    
    <?php
    
        $filename = $_GET['filename'];
    
        $pattern = "\/|\.\.\/|\.\/|etc|var|file|http|ftp|php|zlib|data|glob|phar|ssh2|rar|ogg|expect|zip|compress|filter|input";
    
        if(preg_match("/".$pattern."/is",$filename)== 1){
          echo "die00000000000000000000000000000";
          die();
        }
    
        echo file_get_contents($filename);
    
    ?>
    

  * open_basedir

限定文件访问范围

php

    
    
    open_basedir="/var/www/html"
    

## Code (Command) Execution

### Cause

tex

    
    
    # 代码执行函数
    eval()、assert()、call_user_func()、call_user_func_array()、array_map()等
    
    # 正则处理
    mixed preg_replace ( mixed $ pattern , mixed $ replacement , mixed $ subject [, int $ limit = -1 [, int &$ count ]] )
    preg_replace() 参数/e修饰符问题
    
    # 调用函数过滤不严
    call_user_func()和array_map()
    

### Defense

  * PHP7 新特性

preg_replace() 函数不再支持 “\e” (PREG_REPLACE_EVAL). 应当使用 preg_replace_callback()
替代。

  * preg_replace()

修补 preg_replace() 漏洞需要将修饰符/e去掉

漏洞代码

php

    
    
    <?php
    
    preg_replace("/ \[(.*)\]/e",'strtolower("\\1")',$_GET['str']);
    
    ?>
    

  * 调用函数过滤不严

call_user_func()和array_map()等函数具有调用其他函数的功能，多用在框架里面动态调用函数，所以比较小的程序出现这种方式的代码执行会比较少  
用call_user_func()函数来举例，函数的作用是调用第一个参数(函数)，将第二个参数作为要调用的函数的参数  
call_user_func ( callable $callback [, mixed $parameter [, mixed $… ]] )

修补 call_user_func() 和 array_map() 等函数漏洞需要将其调用函数的参数进行严格过滤

漏洞代码

php

    
    
    <?php
    
    $a=$_GET['a'];
    $b="phpinfo()";
    call_user_func($a,$b);
    
    ?>
    
    payload：a=assert
    

调用函数参数过滤

php

    
    
    <?php
    
    $a=$_GET['cc'];
    
    $pattern = "eval|assert|passthru|pcntl_exec|exec|system|escapeshellcmd|popen|chroot|scandir|chgrp|chown|shell_exec|proc_open|proc_get_status|ob_start";
    
    if(preg_match("/".$pattern."/is",$cc)== 1){
        die();
    }
    
    $bb="phpinfo()";
    call_user_func($cc,$bb);
    
    ?>
    

  * 禁用或过滤代码执行函数

php

    
    
    disable_functions=call_user_func,call_user_func_array,array_map,array_filter,ob_start,phpinfo,eval,assert,passthru,pcntl_exec,exec,system,escapeshellcmd,popen,chroot,scandir,chgrp,chown,shell_exec
    

php

    
    
    $a=$_GET['db'];
    
    $pattern = "call_user_func|call_user_func_array|array_map|array_filter|ob_start|phpinfo|eval|assert|passthru|pcntl_exec|exec|system|escapeshellcmd|popen|chroot|scandir|chgrp|chown|shell_exec|proc_open|proc_get_status|ob_start";
    
    if(preg_match("/".$pattern."/is",$db)== 1){
        die();
    }
    

## XSS

### Defense

XSS 防御基本都是对用户输入以及客户端显示进行过滤转义

  * HttpOnly 的使用

HttpOnly 最早是由微软提出，并在 IE6
中实现的，至今已经逐渐成为一个标准。浏览器将禁止页面的Javascript访问带有HttpOnly属性的Cookie。

HttpOnly 主要是为了解决XSS中的Cookie劫持攻击。

  * htmlspecialchars() 转义函数

php

    
    
    <?php
    if( array_key_exists( "name", $_GET ) && $_GET[ 'name' ] != NULL ) 
    { 
        checkToken( $_REQUEST[ 'user_token' ], $_SESSION[ 'session_token' ], 'index.php' ); 
    
        $name = htmlspecialchars( $_GET[ 'name' ] ); 
    
        echo "<pre>Hello ${name}</pre>"; 
    } 
    ?>
    

使用htmlspecialchars函数把预定义的字符 &、””、’、<、>、/ 转换为 HTML 实体，防止浏览器将其作为HTML元素。

txt

    
    
    & --> &
     < --> <
     > --> >
     " --> "
     ' --> '   
     / --> /

它的语法如下：

txt

    
    
    htmlspecialchars(string,flags,character-set,double_encode)
    
    其中第二个参数flags需要重要注意，很多开发者就是因为没有注意到这个参数导致使用htmlspecialchars()函数过滤XSS时被绕过。因为flags参数对于引号的编码如下：
    可用的引号类型：
    ENT_COMPAT - 默认。仅编码双引号。
    ENT_QUOTES - 编码双引号和单引号。
    ENT_NOQUOTES - 不编码任何引号。
    默认是只编码双引号的

使用htmlspecialchars函数，解决了XSS，但是要注意的是，如果htmlspecialchars函数使用不当，攻击者就可以通过编码的方式绕过函数进行XSS注入，尤其是DOM型的XSS。

  * JavaScript 编码

JavascriptEncode 与 HtmlEncode 的编码方式不同，它需要使用（\）对特殊字符进行转义。

PS：在对不可信数据做编码的时候，不能图方便使用反斜杠`\` 对特殊字符进行简单转义，比如将双引号 `”`转义成
`\”`，这样做是不可靠的，因为浏览器在对页面做解析的时候，会先进行HTML解析，然后才是JavaScript解析，所以双引号很可能会被当做HTML字符进行HTML解析，这时双引号就可以突破代码的值部分，使得攻击者可以继续进行XSS攻击；另外，输出的变量的时候，变量值必须在引号内部，避免安全问题；更加严格的方式，对除了数字和字母以外的所有字符，使用十六进制\xhh
的方式进行编码。

## CSRF

### Defense

  * 验证 HTTP Referer 字段
  * 添加 Token 验证
  * 添加验证码验证
  * 利用Cookie安全策略：samesite属性

## XXE

Defense：使用开发语言提供的禁用外部实体的方法

### PHP

    
    
    libxml_disable_entity_loader(true);

### JAVA

    
    
    DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
    
     dbf.setExpandEntityReferences(false);

### Python

    
    
    from lxml import etree
    xmlData = etree.parse(xmlSource,etree.XMLParser(resolve_entities=False))

