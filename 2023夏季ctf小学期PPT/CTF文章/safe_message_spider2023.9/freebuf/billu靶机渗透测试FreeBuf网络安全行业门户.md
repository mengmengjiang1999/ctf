老规矩，主机发现、端口扫描、子目录扫描先走一遍

![](https://image.3001.net/images/20200811/1597123064.png!small)![](https://image.3001.net/images/20200811/1597123118.png!small)  
![](https://image.3001.net/images/20200811/1597123238.png!small)

我们现在登录主目录和扫描到的各个子目录，找找有没有什么可疑信息。

![1602648383_5f86793fd1aa0f1ed7965.png!small](https://image.3001.net/images/20201014/1602648383_5f86793fd1aa0f1ed7965.png!small)

主页是一个登录页面

![1602648424_5f867968b45b745a20059.png!small](https://image.3001.net/images/20201014/1602648424_5f867968b45b745a20059.png!small)

add目录是一个文件上传页面，上传之后并不知道传到了哪里。

![1602648568_5f8679f87a670a4076982.png!small](https://image.3001.net/images/20201014/1602648568_5f8679f87a670a4076982.png!small)

还有堡塔的数据库管理页面。

![1602648676_5f867a648a24c524d852e.png!small](https://image.3001.net/images/20201014/1602648676_5f867a648a24c524d852e.png!small)

当进入test目录时，发现上图中的提示：file字符是空的。

根据一个成熟渗透狗的经验（滑稽），可以断定这是一个文件读取/文件下载的页面。

先试一个路径叭！

![1602655750_5f8696063939e0202f09b.png!small](https://image.3001.net/images/20201014/1602655750_5f8696063939e0202f09b.png!small)

果不其然，存在文件下载漏洞。这样就可以看看代码中有没有什么有用的信息。

![1602656097_5f86976140cbcd3ab3ef5.png!small](https://image.3001.net/images/20201014/1602656097_5f86976140cbcd3ab3ef5.png!small)

在c.php中，存在以上几行代码，一看就是堡塔数据库的账号和密码。登录堡塔试试。

![1602656328_5f86984895451a9f60c23.png!small](https://image.3001.net/images/20201014/1602656328_5f86984895451a9f60c23.png!small)

这里拿到了靶机管理员的账号密码，登录试试看。

![1602656618_5f86996aeb00648d50039.png!small](https://image.3001.net/images/20201014/1602656618_5f86996aeb00648d50039.png!small)

登录成功之后，看见又文件上传点，还有一个show users的选项。立即推：上传反弹马+文件包含=getshell！！！

现在上传点找到了，我们来找找包含点。先抓个包看看。

![1602656864_5f869a607a89a6b37823a.png!small](https://image.3001.net/images/20201014/1602656864_5f869a607a89a6b37823a.png!small)

POST请求中有一个show，结合前文中add目录的格式，猜测这个页面是否是文件包含页面。

看看能否访问其他文件。

![1602656969_5f869ac90cb18921b9c10.png!small](https://image.3001.net/images/20201014/1602656969_5f869ac90cb18921b9c10.png!small)

果然！！！

那么现在就可以了。

一顿操作猛如虎！！

![1602662931_5f86b213bc7a411394baf.png!small](https://image.3001.net/images/20201014/1602662931_5f86b213bc7a411394baf.png!small)

成功getshell！

接下来是提权。

按照普通提权的思路，一般先查看suid，常见的suid提权有/bin/bash、php、nmap、vim、git等，如果无法使用suid提权，再查看无需root密码的命令，如果两种都不行，可以查看源代码（/var/www中）或者uname
-a使用内核漏洞提权。

![1602663260_5f86b35c0aae17667880f.png!small](https://image.3001.net/images/20201014/1602663260_5f86b35c0aae17667880f.png!small)

看起来并没有什么可用的。

![1602663296_5f86b380b8a2407814212.png!small](https://image.3001.net/images/20201014/1602663296_5f86b380b8a2407814212.png!small)

也需要输入密码。

![1602663377_5f86b3d14715e2e6a1189.png!small](https://image.3001.net/images/20201014/1602663377_5f86b3d14715e2e6a1189.png!small)

查看系统内核版本，发现是ubuntu 13.3.0 系统较老，看看能不能使用内核提权。

![1602663542_5f86b476363610fd088ee.png!small](https://image.3001.net/images/20201014/1602663542_5f86b476363610fd088ee.png!small)

搜索exp之后，发现开头两个本地提权exp。先看37292.c

![1602663943_5f86b607ac43caeb56943.png!small](https://image.3001.net/images/20201014/1602663943_5f86b607ac43caeb56943.png!small)

将exp上传至靶机之后编译并运行，提权成功！（没想到这么顺利嘻嘻）

