## **1.文件包含**

A、本地文件包含

include() 向上包含，向下包含，如果包含出错继续向下执行

include_once() 同上，只进行包含一次

require() 向上包含，向下包含，如果包含出错不下向下执行

require_once() 同上，只进行包含一次

B、远程文件包含:

在php.ini文件中

allow_url_include = on

C、文件包含截断

a、%00截断(php版本小于5.3)

b、问号截断(问号后面相当于请求的参数，伪截断)

c、英文(.) 反斜杠(/) 截断

##  **2、文件读取（下载）漏洞：**

搜索关键函数:

    
    
    file_get_contents()
    
    highlight_file()
    
    fopen() 打开文件
    
    read file() 读取文件
    
    fread()
    
    fgetss()
    
    fgets()
    
    parse_ini_file()
    
    show_source()
    
    file()

##  **3.文件上传漏洞：**

搜索关键函数:

move_uploaded_file() 接着看调用这个函数的代码是否存在为限制上传格式或者可以绕过

(1) 未过滤或本地过滤：

服务器端未过滤，直接上传PHP格式的文件即可利用

(2) 黑名单扩展名过滤：

限制不够全面：IIS默认支持解析.asp,.cdx, .asa,.cer等

扩展名可绕过：

(3)空格绕过

不被允许的文件格式.php，但是我们可以上传文件名为1.php(注意后面有一个空格)

(4)文件头 content-type验证绕过：

getimagesize()函数：验证文件头只要为GIF89a，就会返回真

限制$_FILES["file"]["type"]的值 就是人为限制content-type为可控变量。

防范：

使用in_array()或 利用三等于===对比扩展名

保存上传文件是重命名，规则采用时间戳拼接随机数：md5(time() + rand(1,1000))

##  **4.文件删除漏洞（不常见）**

搜索关键函数：

unlink()利用回溯变量的方式

老版本下的session_destroy()，可以删除文件，现已基本被修复

Metinfo的任意文件删除漏洞$action = delete即可删除.sql的文件，如果文件不是sql直接删除提交的文件名

target.com/recovery.php?&action=delete&filename=../../index.php

##  **5、代码执行**

常规函数：

    
    
    eval()
    
    assert()
    
    preg_replace(), 
    
    call_user_func(), 
    
    call_user_func_array(), 
    
    array_map()

array_filter 依次将array数组中的每个值传递到callbach函数。如果callback函数返回true，则array数组的当前值会被包含

create_function

usort:使用自定一函数对数组进行排序

${}:中间的php代码将会被解析

执行函数：

preg_replace()函数：

mixed preg_replace ( mixed $pattern , mixed $replacement , mixed $subject [,
int $limit = -1 [, int &$count ]] )

当$pattern处存在e修饰符时，$replacement 会被当做php代码执行

##  **6.命令执行**

搜索关键函数：

    
    
    system()
    
    exec()
    
    shell_exec()
    
    passthru()
    
    pcntl_exec()
    
    popen()
    
    proc_open()

