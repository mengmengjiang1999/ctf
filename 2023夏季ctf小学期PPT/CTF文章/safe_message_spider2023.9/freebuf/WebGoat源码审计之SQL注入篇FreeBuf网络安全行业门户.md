WebGoat是一个基于java写的开源漏洞靶场，本期斗哥带来WebGoat的SQL注入攻击例子及相对应的JAVA源码审计。

 **0x01 String SQL Injection**

这个注入页面是<http://10.10.10.35/WebGoat/start.mvc#lesson/SqlInjection.lesson/6>页面，该页面的主要功能是让我们输入用户名从而获取用户名的信息，此处存在SQL注入。

![注入.png](https://image.3001.net/images/20180425/15246217095582.png!small)

输入Smith得到Smith用户的账户信息。

![账户 信息.png](https://image.3001.net/images/20180425/1524621734300.png!small)

输入Smith' and 1=1 --+页面为正常查询结果。

![结果.png](https://image.3001.net/images/20180425/15246217577694.png!small)

输入Smith' and 1=2 --+页面显示 No results matched，由此判断存在SQL注入。

![sql.png](https://image.3001.net/images/20180425/15246217904445.png!small)

输入Smith' or 1=1 --+得到所有用户信息，完成实验要求。

![shiyan.png](https://image.3001.net/images/20180425/15246218173167.png!small)

进一步去利用这个SQLi，此处后端数据库使用的是HSQLDB，根据sqlmap的提示得到了更多的注入手段。

把请求的数据包保存成一个txt文件，叫url.txt。

![URL.png](https://image.3001.net/images/20180425/15246218494876.png!small)

python sqlmap.py -r url.txt

![TXT.png](https://image.3001.net/images/20180425/15246219631484.png!small)

python sqlmap.py -r url.txt -D "PUBLIC" -T USER_DATA -C
"USERID,FIRST_NAME,LAST_NAME,CC_NUMBER,CC_TYPE" --dump

![dump.png](https://image.3001.net/images/20180425/1524622121467.png!small)

该漏洞链接 ：

<http://10.10.10.35/WebGoat/SqlInjection/attack5a>

漏洞文件 ：

D:\myjava\WebGoat-8.0.0.M14\webgoat-lessons\sql-injection\src\main\java\org\owasp\webgoat\plugin\introduction\SqlInjectionLesson5a.java

该文件开头导入了sql的相关包。

![xiangguanbao.png](https://image.3001.net/images/20180425/15246225879249.png!small)

在该文件的第48~67行，可以看到用到了该文件先是获取POST请求中文中account的值拼接到SQL语句，由executeQuery函数执行了该语句。

![yuju.png](https://image.3001.net/images/20180425/15246226132899.png!small)

由于从获取值，到拼接查询整个过程，代码并未对用户输入做任何处理，导致输入用户可控从而造成SQL注入漏洞，另外此处的注入类型为字符型注入，由语句String
query = "SELECT * FROM user_data WHERE last_name = '" + accountName +
"'";便可知晓。

 **0x02 Numeric SQL Injection**

这个注入页面是<http://10.10.10.35/WebGoat/start.mvc#lesson/SqlInjection.lesson/7>页面，该页面的主要功能是通过用户ID来获取用户信息。

![xinxi.png](https://image.3001.net/images/20180425/15246226641552.png!small)

输入101得到该ID账户的信息。

![101.png](https://image.3001.net/images/20180425/15246232123384.png!small)

输入101 or 1=1得到该所有账户的信息。

![suoyou.png](https://image.3001.net/images/20180425/15246232447592.png!small)

此处为数字型的SQL注入，漏洞代码和字符型的代码漏洞几乎没什么区别。

漏洞文件 。

D:\myjava\WebGoat-8.0.0.M14\webgoat-lessons\sql-injection\src\main\java\org\owasp\webgoat\plugin\introduction\SqlInjectionLesson5b.java

![wenjian.png](https://image.3001.net/images/20180425/15246233116852.png!small)

 **0x03 Advanced SQL Injection**

这个注入页面是<http://10.10.10.35/WebGoat/start.mvc#lesson/SqlInjectionAdvanced.lesson/2>页面，该页面的主要目的是让我们执行union查询获得Dave这个账号的密码。

![mima.png](https://image.3001.net/images/20180425/1524623414369.png!small)

根据所给的信息。

![xinxi.png](https://image.3001.net/images/20180425/15246234859978.png!small)

可知存在密码的表名为user_system_data，列为password

Smith' order by 7--为正常页面。

![zhengchang.png](https://image.3001.net/images/20180425/15246235242714.png!small)

Smith' order by 8--报错，说明列数为7。

![列数.png](https://image.3001.net/images/20180425/1524623552335.png!small)

Smith' union select null,null,null,null,null,null,null from user_system_data
--联合查询判断数据回显列位置。

![回显.png](https://image.3001.net/images/20180425/15246235763961.png!small)

Smith' union select null,user_name,password,null,null,null,null from
user_system_data --获取用户名密码，得到dave密码是dave。

![dave.png](https://image.3001.net/images/20180425/15246236316994.png!small)

  

 **0x04 Blind SQL Injection**

这个注入页面是<http://10.10.10.35/WebGoat/start.mvc#lesson/SqlInjectionAdvanced.lesson/4>页面，该页面有两个功能，一处是登陆，一处是注册功能。

![功能
1.png](https://image.3001.net/images/20180425/15246236844106.png!small)![功能
2.png](https://image.3001.net/images/20180425/15246237051080.png!small)

此处文件为D:\myjava\WebGoat-8.0.0.M14\webgoat-lessons\sql-injection\src\main\java\org\owasp\webgoat\plugin\advanced\SqlInjectionChallenge.java

在代码的77~87行处，是对于登陆的后端代码处理。

![后端.png](https://image.3001.net/images/20180425/15246237388375.png!small)

先是获取POST请求正文username_login和password_login的值，然后使用prepareStatement()来预编译处理SQL语句，该函数可以防止SQL攻击。

该处PreparedStatement的使用说明

• 使用了connection的prepareStatement(String_sql)即创建时与一条SQL模版绑定。

• 调用PreparedStatement的setString()方法为?设置值。

• 调用executeQuery()方法执行。

在代码的40~63行处，是对于注册的后端代码处理。

![63.png](https://image.3001.net/images/20180425/15246237798026.png!small)

可以发现，在注册之前做了一个用户名是否注册的判断，而该操作执行的是checkUserQuery这条拼接的SQL语句，此处存在SQL注入，注入参数为username_req。

username_reg=test提示用户创建。

![创建.png](https://image.3001.net/images/20180425/15246238162012.png!small)

username_reg=test再次发送提示用户已创建。

![再次.png](https://image.3001.net/images/20180425/15246238452404.png!small)

即构造语句为假，则创建用户，提示用户创建；构造语句为真，则提示用户已经创建。

username_reg=retest_01'and '1'='1语句为假提示用户创建。

![假.png](https://image.3001.net/images/20180425/15246238893213.png!small)

username_reg=retest_01'and '1'='1再次发送语句为真，提示用户存在。

![真.png](https://image.3001.net/images/20180425/15246239234103.png!small)

username_reg=retest_01'and '1'='2构造语句为真，始终提示用户创建。

![始终.png](https://image.3001.net/images/20180425/1524623955135.png!small)

此处存在SQL盲注，需要了解HSQLDB的语句，进一步获取注入出更多的数据，下面是Sqlmap的POC建议。

![poc.png](https://image.3001.net/images/20180425/15246239876440.png!small)

  

 **0x05 Order by 绕过预编译**

![order.png](https://image.3001.net/images/20180425/15246241187994.png!small)

预编译的语句并不是能够防御住所有的SQL注入攻击，这边是HSQLDB的order by 语句的语法规范。

![规范.png](https://image.3001.net/images/20180425/15246241541405.png!small)

这意味这orderExpression可以是一个selectExpression也可以是一个函数。

例如使用一个case语句。

select * from users order by (case when (true) then lastname else firstname)

因此可以用任何布尔类型来替代when(...)的一部分，从而判断语句是否起作用。

这个我搭建了一个简单的HSQLDB的环境，根据这个<http://how2j.cn/k/hsqldb/hsqldb-client/1129.html>
地址教程搭建的。

select * from category

![ry.png](https://image.3001.net/images/20180425/15246241978763.png!small)

select * from category order by(case when (true) then NAME end)

![end.png](https://image.3001.net/images/20180425/15246242425964.png!small)

在页面<http://10.10.10.35/WebGoat/start.mvc#lesson/SqlInjectionMitigations.lesson/7>存在类似的漏洞。

![类似.png](https://image.3001.net/images/20180425/15246242844586.png!small)

发起排序请求：

![paixu.png](https://image.3001.net/images/20180425/15246243429785.png!small)

按照ID来排序：

![ID.png](https://image.3001.net/images/20180425/15246245682817.png!small)

按照IP来排序：

![IP.png](https://image.3001.net/images/20180425/15246246098167.png!small)

相对应的源代码文件是D:\myjava\WebGoat-8.0.0.M14\webgoat-lessons\sql-injection\src\main\java\org\owasp\webgoat\plugin\mitigation\Servers.java

在代码44~54行规定这个排序功能，采用的仍然是预编译的方式。

![fangshi.png](https://image.3001.net/images/20180425/15246246571308.png!small)

(case when (true) then id else ip end)的URL编码是：

%28case%20when%20%28true%29%20then%20id%20else%20ip%20end%29

![URL 1.png](https://image.3001.net/images/20180425/15246246945875.png!small)

(case when (false) then id else ip end)的URL编码是：

%28case%20when%20%28false%29%20then%20id%20else%20ip%20end%29

![url  2.png](https://image.3001.net/images/20180425/15246247262560.png!small)

进一步了解HSQLDB的语法就可以利用order by 获取更多的数据了。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180425/15246247532345.jpg!small)

