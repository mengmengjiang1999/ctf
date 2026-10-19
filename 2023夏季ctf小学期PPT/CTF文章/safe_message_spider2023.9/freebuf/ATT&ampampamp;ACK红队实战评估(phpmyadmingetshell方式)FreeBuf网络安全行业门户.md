## ATT&ACK红队实战评估

目标环境：  
![image-20211031133005136](https://image.3001.net/images/20211031/1635681856_617e8640a347be2e6b181.png!small)访问Web服务器的80端口发现时PHP探针存在信息泄露的隐患,并且在页面最下方存在可以测试Mysql账号密码的功能。  
然后使用dirb进行目录的扫描,扫描到存在phpmyadmin站点管理工具。  
![image-20211031133254048](https://image.3001.net/images/20211031/1635681857_617e8641643fa0b95af67.png!small)![image-20211031133504379](https://image.3001.net/images/20211031/1635681858_617e8642182a968f55866.png!small)

进入到phpmyadmin中可以查看到MySQL数据库中的所有表和数据库。  
然后查看到有一个newxycms库,推测有一个使用xycms搭建的网站，  
然后直接访问url`10.7.33.125/yxcms`发现成功访问。  
![image-20211031151805064](https://image.3001.net/images/20211031/1635681859_617e864317e8f796b4466.png!small)查看网站,发现网站的公告信息存在信息泄露。  
![image-20211031151915935](https://image.3001.net/images/20211031/1635681860_617e864434ff93a874a1b.png!small)然后按照公告信息访问网站,直接进入了网站的后台.进入后台尝试使用文件上传上传一句话木马文件进行getshell,但是发现后台存在上传过滤,检测文件的内容.没有成功绕过。  
但是yxcms的后台还存在一个漏洞,前台模板任意写文件漏洞。  
![image-20211031170458743](https://image.3001.net/images/20211031/1635681860_617e8644f1c875271c342.png!small)修改文件中的内容,将原本文件中的内容替换为PHP的一句话木马,然后使用菜刀进行连接。  
![image-20211031174002229](https://image.3001.net/images/20211031/1635681861_617e8645b85a052e6413e.png!small)然后查找模板的URL地址,但是发现网站上并没有任何信息发现信息有关于模板(大概是我没有找到),然后百度了一波，发现yxcms的路径是固定的,模板的url路径为`http://IP地址/protected/apps/default/view/default/文件名`  
然后使用蚁剑进行连接,然后输入`whoami`命令查看自身权限为最高权限。  
![image-20211031174659170](https://image.3001.net/images/20211031/1635681862_617e86466cdf5514072cd.png!small)然后创建一个新的用户为hack密码为H@cker005,并且加入管理组然后开启3389端口进行远程桌面连接。  
![image-20211031175138594](https://image.3001.net/images/20211031/1635681863_617e86474e532a8ce8d5d.png!small)然后开启CS生成一个后门木马,传输到第一台出网靶机上,使得靶机在CS上线,然后新建一个监听器,其作用是为了能够让kali获得一个shell。  
![image-20211031175444462](https://image.3001.net/images/20211031/1635681864_617e86482199f85d7604d.png!small)kali获得shell之后,可以使用meterpreter工具集进行自动添加路由,并且使用metasploit中自带的socks代理工具进行一个内网的代理。  
ATT&ACK红队实战评估(一)的第一个靶机就彻底拿下了然后就是对内网进行进一步的渗透。  
补充前面getshell的方式:

### 1.phpmyadmin general.log漏洞:

进入phpmyadmin的首页,可以进入一个执行SQL语句的页面,然后查询General_log是否开启,输入语句`show variables like
'general_log';`查看是否开启,如果没有开启的话,可以输入语句`set global general_log=on;`开启日志功能。  
![image-20211031190730450](https://image.3001.net/images/20211031/1635681864_617e8648f24f4be6d6963.png!small)发现日志已经开启,因为不是一句话木马需要用php来进行解析,所以我们需要重新设置日志的位置,并且把日志的格式设置为php。  
![image-20211031191159325](https://image.3001.net/images/20211031/1635681865_617e8649c8aa67ab6eba4.png!small)然后写入一句话木马到general.log文件也就是rxxy.php中。  
![image-20211031192057889](https://image.3001.net/images/20211031/1635681866_617e864a95eaa8432f495.png!small)然后就可以使用蚁剑进行连接。

### 2.phpmyadmin慢查询漏洞:

首先查看慢日志是否开启`show variables like '%slow_query_log%';`,如果没有开启慢查询的话,就使用sql语句`set
global slow_query_log=1`开启慢查询日志。  
![image-20211031192558461](https://image.3001.net/images/20211031/1635681867_617e864b6dc2398663a78.png!small)因为一般来说慢查询日志文件的路径和文件名(一句话木马解析不了)我们通过网站是访问不到的,所以我们需要伪造一下慢查询的路径和文件名。  
将路径和文件名伪造成为我们可以访问到的路径和解析的了的文件名.然后将一句话木马写入到慢查询的日志中。  
![image-20211031193427904](https://image.3001.net/images/20211031/1635681868_617e864c4456f03f28fee.png!small)然后就可以通过蚁剑等进行连接，

成功连接进入远程桌面之后,进入cmd窗口模式,输入ipconfig查看自己的地址,并且收集内网的地址。  
![image-20211031194005889](https://image.3001.net/images/20211031/1635681869_617e864d21b6c71f0a09a.png!small)发现内网的网段,因为是Windows,所以第一时间想到用ping去发现主机，  
`for /L %I in (1,1,254) DO @ping -w 1 -n 1 192.168.75.%I | findstr
"TTL="`进行了一波主机发现  
探测到得主机IP为。![image-20211031195424264](https://image.3001.net/images/20211031/1635681869_617e864de6520772fb92c.png!small)至此，ATT&ACK的红队实战评估(一)第一步已经完成。

