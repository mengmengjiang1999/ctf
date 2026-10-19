**Burpsuite Scanner介绍**

Burp Scanner的功能主要是用来自动检测web系统的各种漏洞，我们可以使用Burp
Scanner代替我们手工去对系统进行普通漏洞类型的渗透测试，从而能使得我们把更多的精力放在那些必须要人工去验证的漏洞上。

进一步解放我们的生产力，提高我们的工作效率

![image](https://image.3001.net/images/20211128/1638070089_61a2f749cc52f29041b4d.png!small)

 **Burpsuite Scanner介绍**

扫描队列中包含了扫描进度。

![image](https://image.3001.net/images/20211128/1638070130_61a2f772179721fdcf5c1.png!small)

存在的问题以及发送的时间以及插入点等等

 **Burpsuite Scanner介绍**

扫描配置 live scanning

![image](https://image.3001.net/images/20211128/1638070181_61a2f7a5a2ad9de414b51.png!small)

分为主动扫描和被动扫描，主动扫描一般是不开起来的

 **Burpsuite Scanner介绍**

issue definitions 查看支持的漏洞扫描。

![image](https://image.3001.net/images/20211128/1638070194_61a2f7b207c21fddd6899.png!small)

选择漏洞，可以直接查看漏洞的类型等等详细信息

 **Burpsuite Scanner介绍**

设定探测位置

![image](https://image.3001.net/images/20211128/1638070205_61a2f7bd2d74627772651.png!small)

所有的探测都是插入特定的payload到指定的位置，然后进行探测

同时也可以改变参数的位置，来造成更多的扫描请求

 **Burpsuite Scanner介绍**

加快主动扫描速度

![image](https://image.3001.net/images/20211128/1638070218_61a2f7ca3077d59efea25.png!small)

throttle：节制

两个请求之间的时间

有一些防护机制，比如WAF，防火墙，发包机制过快，会导致IPS、IDS的预警报告，为了避免触发报警机制，我们可以减缓两次请求之间的时间间隔

 **Burpsuite Scanner介绍**

设定探测漏洞

![image](https://image.3001.net/images/20211128/1638070228_61a2f7d4d3422f3656f3e.png!small)

可以指定我们要扫描那些漏洞

也可以指定订制版的，对我们的具体内容进行探测，速度会更快

使用默认化的探测，使我们的结果更加准确

 **Burpsuite Scanner介绍**

设定静态代码分析

![image](https://image.3001.net/images/20211128/1638070263_61a2f7f766883a1fb9f92.png!small)

通过这些分析，会让我们得到更多的漏洞信息，从而使我们的扫描更加准确

 **主动扫描漏洞**

针对存在漏洞的Web应用程序进行主动扫描，分析漏洞，并导出漏洞报告。

![image](https://image.3001.net/images/20211128/1638070274_61a2f802b06f0131616ae.png!small)

打印出一个HTML文件

 **实战演示**

在浏览器当中打开一个要探测的网站

![image](https://image.3001.net/images/20211128/1638070286_61a2f80eaa47fda2cb54d.png!small)

设置截断

![image](https://image.3001.net/images/20211128/1638070298_61a2f81a2154b86bb15ec.png!small)

这个时候Burpsuit就会抓取对应的数据包

![image](https://image.3001.net/images/20211128/1638070307_61a2f823d0ee4013856eb.png!small)

将这个数据包发送到爬虫页面，点两个Yes

![image](https://image.3001.net/images/20211128/1638070317_61a2f82d880c46295c98a.png!small)

发送到爬虫页面后，就会爬取网站根目录下的所有文件

Target>Site map

![image](https://image.3001.net/images/20211128/1638070336_61a2f84078029cc664a40.png!small)

选择域名，发送到Scanner，做一个主动的扫描

![image](https://image.3001.net/images/20211128/1638070347_61a2f84b2239883205b29.png!small)

勾选最后一条，Next

![image](https://image.3001.net/images/20211128/1638070356_61a2f854406f0d06b72d6.png!small)

点击OK

![image](https://image.3001.net/images/20211128/1638070368_61a2f86037c2ebb5b595e.png!small)

Scanner就会进行探测

Scanner>Issue activity选其中一条进行观察

![image](https://image.3001.net/images/20211128/1638070391_61a2f8773b36c77a0960d.png!small)

可以打开链接，进行观察

![image](https://image.3001.net/images/20211128/1638070399_61a2f87fe3f8b19956e01.png!small)

有些文件是可下载的，也可以下载下来进行对应的查看

![image](https://image.3001.net/images/20211128/1638070413_61a2f88d3cbcf8b0049d0.png!small)

漏洞扫描完之后，就要把它导出来，Target>Site map

选择域名，issues>Report issues for this host

![image](https://image.3001.net/images/20211128/1638070428_61a2f89c74d0985119710.png!small)

选择HTML，点击next

![image](https://image.3001.net/images/20211128/1638070440_61a2f8a817f98c1c94f8e.png!small)

next

![image](https://image.3001.net/images/20211128/1638070450_61a2f8b29f2592adfbbf7.png!small)

next

![image](https://image.3001.net/images/20211128/1638070461_61a2f8bd1e99f6f887062.png!small)

next

点Select file，保存到桌面的文件，文件命名为test

![image](https://image.3001.net/images/20211128/1638070472_61a2f8c8216801bfb6af6.png!small)

点击保存

![image](https://image.3001.net/images/20211128/1638070482_61a2f8d2e6ad8786d5bdc.png!small)

点击next

![image](https://image.3001.net/images/20211128/1638070492_61a2f8dc57fbce84a03db.png!small)

close，最小化回到桌面进行查看

![image](https://image.3001.net/images/20211128/1638070501_61a2f8e55c6255c133213.png!small)

更该文件后缀名为.html

![image](https://image.3001.net/images/20211128/1638070512_61a2f8f0c000dbcbec1f7.png!small)

双击即可打开

![image](https://image.3001.net/images/20211128/1638070523_61a2f8fb25811c948a817.png!small)

通过这样，我们可以很清楚的看到对应的弱点以及对应的信息，并且这里也都有对应的引用，来进行参考

如果我们发现存在一些漏洞，我们可以结合一些漏洞利用工具、POC来进行一下概念的验证，来证明是否真实存在

 **总结**

1、掌握Burpsuite Scanner配置。

2、掌握Burpsuite漏洞扫描技术。

先用爬虫进行爬取，然后再扫描

