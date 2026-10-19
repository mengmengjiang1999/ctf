## **DC-5靶机通关笔记**

这是DC-5的描述，从中得到一些关键信息。

![1608777125_5fe3fda531d4f82bc2b53.png!small?1608777127840](https://image.3001.net/images/20201224/1608777125_5fe3fda531d4f82bc2b53.png!small?1608777127840)

开始

nmap扫描![1608776634_5fe3fbba03ac237b2045e.png!small?1608776636555](https://image.3001.net/images/20201224/1608776634_5fe3fbba03ac237b2045e.png!small?1608776636555)

确定IP地址后端口扫描

![1608776834_5fe3fc82116c13e5534ed.png!small?1608776836634](https://image.3001.net/images/20201224/1608776834_5fe3fc82116c13e5534ed.png!small?1608776836634)

发现80端口

使用kali自带工具dirbuster遍历目录

![1608777237_5fe3fe15512911f64dda7.png!small?1608777240033](https://image.3001.net/images/20201224/1608777237_5fe3fe15512911f64dda7.png!small?1608777240033)

  

发现只有以下这个界面存在交互

![1608777304_5fe3fe58a40d376061745.png!small?1608777307298](https://image.3001.net/images/20201224/1608777304_5fe3fe58a40d376061745.png!small?1608777307298)

  

访问footer.php页面时发现了描述中会随着页面刷新改变的东西

  

![1608777572_5fe3ff642b7ff087a6ace.png!small?1608777574686](https://image.3001.net/images/20201224/1608777572_5fe3ff642b7ff087a6ace.png!small?1608777574686)

![1608777587_5fe3ff7334ea7b4229eed.png!small?1608777589818](https://image.3001.net/images/20201224/1608777587_5fe3ff7334ea7b4229eed.png!small?1608777589818)

我们猜测thankyou.php中include()包含了footer.php

这里就可能存在文件包含漏洞

### 什么是文件包含漏洞？

>
> 严格来说，文件包含漏洞是“代码注入”的一种。在“注入攻击”一章中，曾经提到过“代码注入”这种攻击，其原理就是注入一段用户能控制的脚本或代码，并让服务器端执行。“代码注入”的典型代表就是文件包含（File
> Inclusion）。文件包含可能会出现在JSP、PHP、ASP等语言中，常见的导致文件包含的函数如下。
>
> PHP：include(), include_once(), require(), re-quire_once(), fopen(),
> readfile(), ...
>
> JSP/Servlet：ava.io.File(), java.io.Fil-eReader(), ...
>
> ASP：include file, include virtual, ...
>
> 在互联网的安全历史中，PHP的文件包含漏洞已经臭名昭著了，因为黑客们在各种各样的PHP应用中挖出了数不胜数的文件包含漏洞，且后果都非常严重。
>
> 文件包含是PHP的一种常见用法，主要由4个函数完成：
>
> include()
>
> require()
>
> include_once()
>
> require_once()
>
>
> 当使用这4个函数包含一个新的文件时，该文件将作为PHP代码执行，PHP内核并不会在意该被包含的文件是什么类型。所以如果被包含的是txt文件、图片文件、远程URL，也都将作为PHP代码执行。这一特性，在实施攻击时将非常有用。比如以下代码：
>
> <?php
>
> include($_GET[test]);
>
> ?>
>
>  
>
>
> 要想成功利用文件包含漏洞，需要满足下面两个条件：
>
> （1）include()等函数通过动态变量的方式引入需要包含的文件；
>
> （2）用户能够控制该动态变量。

![1608777533_5fe3ff3d034d5b5eadda9.png!small?1608777535739](https://image.3001.net/images/20201224/1608777533_5fe3ff3d034d5b5eadda9.png!small?1608777535739)

我们用burpsuite遍历一下代码中动态变量名

![1608778509_5fe4030d4e2f03d6f7d6b.png!small?1608778511963](https://image.3001.net/images/20201224/1608778509_5fe4030d4e2f03d6f7d6b.png!small?1608778511963)

选择攻击字典

![1609983130_5ff6649ac955c07e7153b.png!small?1609983138361](https://image.3001.net/images/20210107/1609983130_5ff6649ac955c07e7153b.png!small?1609983138361)![1608778620_5fe4037c4c04caa490657.png!small?1608778622980](https://image.3001.net/images/20201224/1608778620_5fe4037c4c04caa490657.png!small?1608778622980)

得知是file

![1608778676_5fe403b49c5f613c7eebe.png!small?1608778679293](https://image.3001.net/images/20201224/1608778676_5fe403b49c5f613c7eebe.png!small?1608778679293)验证过确实存在LFI

![1608778823_5fe40447be2f4b2f606ba.png!small?1608778826433](https://image.3001.net/images/20201224/1608778823_5fe40447be2f4b2f606ba.png!small?1608778826433)

下面获取shell，前面得知服务nginx，

![1608778852_5fe40464b1b282195f552.png!small?1608778855309](https://image.3001.net/images/20201224/1608778852_5fe40464b1b282195f552.png!small?1608778855309)

  

access.log

访问日志主要记录客户端的请求。客户端向Nginx服务器发起的每一次请求都记录在这里。客户端IP，浏览器信息，referer，请求处理时间，请求URL等都可以在访问日志中得到。

利用日志写入一句话小马

![1609822945_5ff3f2e1305bbd54f9115.png!small?1609822952072](https://image.3001.net/images/20210105/1609822945_5ff3f2e1305bbd54f9115.png!small?1609822952072)

* * *

什么是一句话小马？

>
> 一句话木马就是只需要一行代码的木马，短短一行代码，就能做到和大马相当的功能。为了绕过waf的检测，一句话木马出现了无数中变形，但本质是不变的：木马的函数执行了我们发送的命令。
>
> * * *

  

打开蚁剑

添加数据

URL地址中内容是include本地包含Nginx日志，其中有我们写入的一句话小马，这样就触发了我们的一句话，就能成功连接了。

![1609823092_5ff3f374a2cc05a08a3b0.png!small?1609823099416](https://image.3001.net/images/20210105/1609823092_5ff3f374a2cc05a08a3b0.png!small?1609823099416)![1608812359_5fe48747a361b634283ad.png!small?1608812362688](https://image.3001.net/images/20201224/1608812359_5fe48747a361b634283ad.png!small?1608812362688)使用蚁剑进行连接

![1609823290_5ff3f43ac40fba2d568ad.png!small?1609823297512](https://image.3001.net/images/20210105/1609823290_5ff3f43ac40fba2d568ad.png!small?1609823297512)

  

写入反弹shell

右击弹出菜单

![1609823363_5ff3f4836c8849201fe9e.png!small?1609823370226](https://image.3001.net/images/20210105/1609823363_5ff3f4836c8849201fe9e.png!small?1609823370226)

利用NC工具反向连接我们kali

![1609825596_5ff3fd3ca85a9fa6b269f.png!small?1609825603330](https://image.3001.net/images/20210105/1609825596_5ff3fd3ca85a9fa6b269f.png!small?1609825603330)

kali端监听端口

![1608871507_5fe56e531ccce27f764d2.png!small?1608871509832](https://image.3001.net/images/20201225/1608871507_5fe56e531ccce27f764d2.png!small?1608871509832)

得到交互式shell

python -c 'import pty;pty.spawn("/bin/bash")'

###  **提权**

find / -perm /4000 2>/dev/null

/ 根目录  
-perm /4000 查找SUID权限  
2> 错误输出到空文件

查找具有SUID权限的命令

![1609209439_5fea965ff2acc56687943.png!small?1609209444411](https://image.3001.net/images/20201229/1609209439_5fea965ff2acc56687943.png!small?1609209444411)

![1609209977_5fea98799d9c1fc4a41d5.png!small?1609209982438](https://image.3001.net/images/20201229/1609209977_5fea98799d9c1fc4a41d5.png!small?1609209982438)

![1609212537_5feaa279a5e95c037f4d1.png!small?1609212542042](https://image.3001.net/images/20201229/1609212537_5feaa279a5e95c037f4d1.png!small?1609212542042)

将文件复制一份

查看文件

![1609212588_5feaa2ac1331988b984b5.png!small?1609212592617](https://image.3001.net/images/20201229/1609212588_5feaa2ac1331988b984b5.png!small?1609212592617)

![1609239315_5feb0b13ea95e8e730020.png!small?1609239320308](https://image.3001.net/images/20201229/1609239315_5feb0b13ea95e8e730020.png!small?1609239320308)

按照脚本将红框内内容保存为/tmp/libhax.c的文件

然后gcc编译为libhax.so文件

  

文件下半部分保存为/tmp/rootshell.c

gcc编译为rootshell

![1609239432_5feb0b88472fa76d826dd.png!small?1609239436634](https://image.3001.net/images/20201229/1609239432_5feb0b88472fa76d826dd.png!small?1609239436634)

  

然后把编译过（两个）的文件上传到受害者/tmp/目录下

![1609239716_5feb0ca400bb202cd9428.png!small?1609239720417](https://image.3001.net/images/20201229/1609239716_5feb0ca400bb202cd9428.png!small?1609239720417)

![1609239767_5feb0cd78c638f47d5eb1.png!small](https://image.3001.net/images/20201229/1609239767_5feb0cd78c638f47d5eb1.png!small)

执行脚本中以下的命令

![1609239606_5feb0c368313fc4fe9f37.png!small?1609239610840](https://image.3001.net/images/20201229/1609239606_5feb0c368313fc4fe9f37.png!small?1609239610840)

  

提权成功  
![1609212382_5feaa1de0e5fd787ab2c0.png!small?1609212386459](https://image.3001.net/images/20201229/1609212382_5feaa1de0e5fd787ab2c0.png!small?1609212386459)![1609212479_5feaa23f8feb52462cfa0.png!small?1609212484071](https://image.3001.net/images/20201229/1609212479_5feaa23f8feb52462cfa0.png!small?1609212484071)

完结撒花！

