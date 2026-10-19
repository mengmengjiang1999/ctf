## MYSQL长字符截断

##### 即使没有任何注入漏洞，攻击者也可能登录到后台管理页面

### 1、相关资料

![image.png](https://image.3001.net/images/20210227/1614430690_603a41e27cb7a57e64f0d.png!small)  
![image.png](https://image.3001.net/images/20210227/1614430788_603a4244486c9af0bf30c.png!small)

### 2、sql-mode的各项设置

MySQL5.0以上版本支持三种sql_mode模式：ANSI、TRADITIONAL和STRICT_TRANS_TABLES。

1、ANSI模式：宽松模式，更改语法和行为，使其更符合标准SQL。对插入数据进行校验，如果不符合定义类型或长度，对数据类型调整或截断保存，报warning警告。对于本文开头中提到的错误，可以先把sql_mode设置为ANSI模式，这样便可以插入数据，而对于除数为0的结果的字段值，数据库将会用NULL值代替。

2、TRADITIONAL模式：严格模式，当向mysql数据库插入数据时，进行数据的严格校验，保证错误数据不能插入，报error错误，而不仅仅是警告。用于事物时，会进行事物的回滚。
注释：一旦发现错误立即放弃INSERT/UPDATE。如果你使用非事务存储引擎，这种方式不是你想要的，因为出现错误前进行的数据更改不会“滚动”，结果是更新“只进行了一部分”。

3、STRICT_TRANS_TABLES模式：严格模式，进行数据的严格校验，错误数据不能插入，报error错误。如果不能将给定的值插入到事务表中，则放弃该语句。对于非事务表，如果值出现在单行语句或多行语句的第1行，则放弃该语句。

 **STRICT_TRANS_TABLES：**  
在该模式下，如果一个值不能插入到一个事务表中，则中断当前的操作，对非事务表不做限制。必须设置，以后各项可能依赖于该项的设置  
 **NO_ENGINE_SUBSTITUTION：**  
如果需要的存储引擎被禁用或未编译，那么抛出错误。不设置此值时，用默认的存储引擎替代，并抛出一个异常  
 **ONLY_FULL_GROUP_BY：**  
对于GROUP BY操作，如果在SELECT中出现的单独的列，没有在GROUP BY子句中出现，那么这个SQL是不合法的  
 **NO_AUTO_VALUE_ON_ZERO：**  
该值影响自增长列的插入。默认设置下，插入0或NULL代表生成下一个自增长值。如果用户希望插入的值为0，而该列又是自增长的，那么这个选项就有用了  
 **NO_ZERO_IN_DATE：**  
在严格模式下，不允许日期和月份为零  
 **NO_ZERO_DATE：**  
设置该值，mysql数据库不允许插入零日期，插入零日期会抛出错误而不是警告  
 **ERROR_FOR_DIVISION_BY_ZERO：**  
在INSERT或UPDATE过程中，如果数据被零除，则产生错误而非警告。如果未给出该模式，那么数据被零除时MySQL返回NULL  
 **NO_AUTO_CREATE_USER：**  
禁止GRANT语句创建密码为空的用户  
 **PIPES_AS_CONCAT：**  
将“||”视为字符串的连接操作符而非或运算符，这和Oracle数据库是一样的，也和字符串的拼接函数Concat相类似  
 **ANSI_QUOTES：**  
启用ANSI_QUOTES后，不能用双引号来引用字符串，因为它被解释为识别符  
也可以在命令行查看和设置sql_mode变量

### 3、产生原因：(1)在sql-mode里没有加上STRICT_TRANS_TABLES或者TRADITIONAL (2)加上的是ANSI

这里username为varchar(5)，即最大规定长度为5，而输入的值为‘admsddsff’，长度为9，超过规定长度，可是并没有报错。通过查询可知被截断了。那么我们可以利用这个漏洞，像相关资料第二张里被红笔圈的那句话一样  
![image.png](https://image.3001.net/images/20210227/1614430870_603a429626cb573a58f4c.png!small)

### 4、预防方法：在sql-mode里加STRICT_TRANS_TABLES或者TRADITIONAL

加上”STRICT_TRANS_TABLES“或者”TRADITIONAL“后，输入的数据超过规定长度就会报错，不能输入  
![image.png](https://image.3001.net/images/20210227/1614430935_603a42d72c7a90c039758.png!small)

