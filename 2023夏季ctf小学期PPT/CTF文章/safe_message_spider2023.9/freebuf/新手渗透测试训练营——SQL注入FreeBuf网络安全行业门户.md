学习渗透测试，一定要掌握各种漏洞的检测和利用方法。今天我们分析一下dvwa环境中sql注入从低级到高级的渗透步骤。

手动挖掘Sql注入，首先要发现注入点。以low级别为例，发现一个可以输入内容的文本框时，首先测试一下是不是存在sql注入。

## Low Level  

分别在文本框中输入1和1’进行测试。输入1时，回显正常，如下：

![1.png](https://image.3001.net/images/20180912/1536750348_5b98f30cd9231.png!small)  

输入1’时，提示错误。此外，我们可以看到，我们在文本框中输入的内容会显示在url中，也就是说id参数通过get 方式传递。

![2.png](https://image.3001.net/images/20180912/1536750359_5b98f3174771b.png!small)  

确定了存在注入的点，就开始尝试注入。通过union select 1,2……测试该注入点可以显示的字段数。union select
1,unionselect1,2 均正常。union select1,2,3时出现报错，说明该注入点最多可以显示两个不同的字段。

![3.png](https://image.3001.net/images/20180912/1536750373_5b98f32570f9a.png!small)![4.png](https://image.3001.net/images/20180912/1536750393_5b98f339ab738.png!small)  

确定该注入点可以显示的字段数之后，通过database()函数，获取当前数据库名称。当前数据库名称时“dvwa”

![5.png](https://image.3001.net/images/20180912/1536750413_5b98f34dc42ed.png!small)

特别需要注意的是：直接用1’union
selectdatabase(),user()进行注入，查看当前数据库和用户时，会报错，提示有三个单引号。这三个单引号是系统自动加上的，只要用“--”注释掉，就可以正常执行了。'--'是mysql数据库的单行注释符，而且第二个'-'后面一定要有一个空格(下面构造的SQL语句也是如此)，这里它把后台添加的单引号注释掉了。用#注释时，会把submit注释掉。  

![6.png](https://image.3001.net/images/20180912/1536750453_5b98f375b58c4.png!small)  

  

知道当前数据库名称后，可以利用information_schema数据库获取当前数据库中存在的表。如下图所示，dvwa数据库中有两个表，分别为：guestbook和users。

![7.png](https://image.3001.net/images/20180912/1536750478_5b98f38ee0acc.png!small)

知道当前数据库以及数据库中的表的名称之后，就可以猜解每个表中的有那些列。如下所示们可以dvwa.users表中有user和password这两组非常重要的数据。获得这个两组数据，就可以明确知道登陆用户以及该用户对用的密码。

![8.png](https://image.3001.net/images/20180912/1536750509_5b98f3add76ff.png!small)

用1’union select password,user fromdvwa.users -- 命令查看password和
user这两列中的数据。两列中的数据如下：

##
![9.png](https://image.3001.net/images/20180912/1536750568_5b98f3e80c07c.png!small)Medium
Level

ID通过下拉菜单进行选择。选择不同ID时，URL并没有任何变化。

![10.png](https://image.3001.net/images/20180912/1536750624_5b98f42016543.png!small)

那么参数id并不是通过get方式传递的。通过burpsuit抓包，看一下抓取的请求包，发现参数使用post方式传递。可以看到我们上传的id参数如下：

![11.png](https://image.3001.net/images/20180912/1536750670_5b98f44e02418.png!small)  

通过修改参数id后面的注入语句进行注入尝试。具体可参考low级别的渗透过程。

在用1 union select1，table_name from information_schema.table
wheretable_schem=dvwa命令，尝试查找dvwa数据库中的表时提示Unknown column 'dvwa' in 'where
clause'。所以改用database()函数获取数据库名。Database()函数获取数据库名称时，没有出现报错。该命令显示，dvwa数据库中有两张表，分别是：guestbook和users。

![12.png](https://image.3001.net/images/20180912/1536750698_5b98f46ae9fe2.png!small)

知道dvwa中是的两个表的名字之后，继续查看每个表中包含那几个列：1 union select table_name,column_name from
information-schema.columns where table_schema=database() and
table_name=table_name。  

![13.png](https://image.3001.net/images/20180912/1536750719_5b98f47f69fc4.png!small)

由上一句注入测试，可以看到users表中有user和password两列。将这两列内容导出，我们就可以得到用户登录数据库。用select
password,user from dvwa.users命令，查看password和user两列的内容。

![14.png](https://image.3001.net/images/20180912/1536750734_5b98f48e4a8a5.png!small)

## High Level

先测试是否存在注入点。Id=1正常，id=1’时报错。可以确定存在sql注入漏洞。

![15.png](https://image.3001.net/images/20180912/1536750778_5b98f4ba9d65c.png!small)

利用union selectdatabase（）,user()进行注入，发现只能显示一行内容，那么可以猜测源代码中，对回显的数量，做了限制。

![16.png](https://image.3001.net/images/20180912/1536750824_5b98f4e87f3c8.png!small)在sql命令中，用#注释,发现可以回显多行内容。那么源代码中，应该是在id参数之后，对显示的内容做了限制。#注释掉id参数后面的命令，把对回显的限制注释掉了。

![17.png](https://image.3001.net/images/20180912/1536750836_5b98f4f4720d8.png!small)

可以回显之后，后面的注入操作与low级别相同。

反过来，我们查看一下源码，可以发现，在id之后，利用limit语句限制select语句返回的数据数量。

![18.png](https://image.3001.net/images/20180912/1536750860_5b98f50c3c1d8.png!small)

  

*本文作者：EVA。本文属丁牛科技原创，如需转载请标明出处。  

