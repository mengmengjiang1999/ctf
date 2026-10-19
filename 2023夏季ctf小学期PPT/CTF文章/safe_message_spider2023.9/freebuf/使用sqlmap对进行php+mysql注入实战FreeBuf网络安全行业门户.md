[作者：陈小兵](https://bbs.ichunqiu.com/thread-41020-1-1.html?from=beef)  
一般来讲一旦网站存在sql注入漏洞，通过sql注入漏洞轻者可以获取数据，严重的将获取webshell以及服务器权限，但在实际漏洞利用和测试过程中，也可能因为服务器配置等情况导致无法获取权限。

  
  
1.1php注入点的发现及扫描  

1.使用漏洞扫描工具进行漏洞扫描

将目标url地址放在wvs中进行漏洞扫描，如图1所示，扫描结果显示存在SQL盲注和SQL注入，其漏洞存在的参数为同一页面。

  

![image.png](https://image.3001.net/images/20180531/15277522444642.png!small)  

图1使用wvs扫描目标网站

  

2.使用sqlmap工具对注入点进行漏洞验证

如图2所示，使用sqlmap注入检查命令进行验证：  

![image.png](https://image.3001.net/images/20180531/15277522622513.png!small)

验证结果显示该url确实存在sql注入漏洞，且数据库为mysql。

![image.png](https://image.3001.net/images/20180531/15277522736265.png!small)

  

图2使用sqlmap工具对注入点进行漏洞验证

  
1.2使用sqlmap进行sql注入测试  

1.sql注入payload

如图3所示，通过sqlmap或者该注入点存在boolean-based blind、 AND/OR time-based blind 、UNION
query三种类型漏洞，跟wvs扫描结果一致。sqlmap漏洞测试完毕后会自动给出相应的payload，例如对第一个可以在浏览器中进行测试：

![image.png](https://image.3001.net/images/20180531/15277523012544.png!small)

![image.png](https://image.3001.net/images/20180531/15277523077733.png!small)

  

图3 sql注入payload

  

2.获取当前数据库名称

![image.png](https://image.3001.net/images/20180531/15277523185450.png!small)

获取当前数据库为xbase，如图4所示。  

![image.png](https://image.3001.net/images/20180531/15277523824934.png!small)

  

图4获取当前数据库名称

  

3.获取当前用户

![image.png](https://image.3001.net/images/20180531/15277523975897.png!small)

命令直接获取当前数据库账号为root@localhost，如图5所示。

![image.png](https://image.3001.net/images/20180531/15277524136341.png!small)  

图5获取当前数据库用户账号

  

4.查看数据库用户及密码

由于本例注入点是mysql
root账号，因此可以通过sqlmap命令来查看数据库用户（--users）及数据库密码(--password)，如图6所示，执行命令如下：

![image.png](https://image.3001.net/images/20180531/15277524361091.png!small)

  
![image.png](https://image.3001.net/images/20180531/15277524437415.png!small)  

图6查看数据库用户及密码

  

5.破解并获取数据库明文密码

  

（1）在线破解并整理数据库密码

将密码哈希值去掉前面的“*”号，将其复制到[www.cmd5.com](http://www.cmd5.com/)及somd5.com进行破解，注意该值需要选择密码类型mysql5，整理查询结果如下所示：

![image.png](https://image.3001.net/images/20180531/15277524542226.png!small)  

（2）还可以通过--sql-shell直接查询数据库用户及密码

![image.png](https://image.3001.net/images/20180531/15277524678700.png!small)

执行上面命令后，通过查询命令来获取密码，如图7所示：

![image.png](https://image.3001.net/images/20180531/15277524787750.png!small)![image.png](https://image.3001.net/images/20180531/15277524877910.png!small)

图7查询mysql数据库host、user及密码

  

（3）对服务器端口进行扫描

masscan -p 3306 114.**.***.***

如果开放数据库端口，则可以直接进行连接，扫描结果显示仅仅开放80端口。

  

6.一些常用的sqlmap命令总结

![image.png](https://image.3001.net/images/20180531/15277525048816.png!small)

  
1.3php网站webshell获取  

![image.png](https://image.3001.net/images/20180531/15277525208493.png!small)

（4）后台文件上传漏洞利用及获取

通过注入点获取管理员密码及后台地址，登录后台寻找上传地址及上传漏洞来获取webshell。

（5）文件包含漏洞来获取webshell

2.直接获取webshell失败

对于root账号而言，一般情况都可以通过--os-shell命令来获取webshell，如图8所示，执行命令后，并未获取shell。

![image.png](https://image.3001.net/images/20180531/15277525534238.png!small)

  

图8获取shell失败

  

3.获取真实物理路径

通过测试，在网站根目录下发现存在phpinfo页面，如图9所示，在该页面中可以看到数据库为内网IP地址192.168.77.88，真实物理路径为/usr/local/apache/htdocs

![image.png](https://image.3001.net/images/20180531/15277525636392.png!small)

  

图9获取网站正式路径

  

4.写入文件测试

知道物理路径，可以通过sqlmap进行文件读取和写入命令，执行命令：

sqlmap.py -u <http://www.>***.com.cn/happystudy/happystudy_info.php?idnow=34
--file-write="C:\tools\sqlmap\1.php" --file-dest="/usr/local/apache/htdocs/happystudy/shell.php"  

如图10所示，sqlmap执行命令成功，通过url对文件进行访问测试，页面不存在。

![image.png](https://image.3001.net/images/20180531/15277525816754.png!small)

  

图10写入文件测试

  

5.本地搭建环境测试写入文件

前面写入文件执行成功，怀疑是命令有问题，因此在本地搭建环境进行测试，测试命令为：

  
sqlmap.py -d mysql://root:123456@172.17.26.16:3306/mysql --file-write="C:\tools\sqlmap\1.php" --file-dest="C:\ComsenzEXP\wwwroot\shell.php"  

结果在C:\ComsenzEXP\wwwroot\目录下成功写入shell.php文件，为此分析原因可能为：

（1）该目录无写入权限

（2）magic_quotes_gpc值为on

6.尝试general_log文件获取webshell方法

（1）查看genera文件配置情况

  
![image.png](https://image.3001.net/images/20180531/15277526113064.png!small)

（2）关闭general_log

  
![image.png](https://image.3001.net/images/20180531/15277526203980.png!small)  

（3）通过general_log选项来获取webshell

  
![image.png](https://image.3001.net/images/20180531/15277526315672.png!small)  

由于以上命令需要在mysql客户端命令行或者phpmyadmin中进行执行，本案例中不具备，通过--sql-shell以及--sql-query命令均未能实现。

7.使用pangolin工具进行导出webshell

如图11所示，通过pangolin对该sql注入地址进行测试，尝试将webshell导出到网站根目录/usr/local/apache/htdocs/xxx.php文件，结果显示跟前面的分析情况一致。

![image.png](https://image.3001.net/images/20180531/15277526395889.png!small)

  

图11使用pangolin工具进行导出webshell失败

  

8.读取文件测试

（1）读取文件

如图12所示，依次执行命令，分别读取/etc/passwd、/usr/local/apache/htdocs/index.php等文件

  
  

sqlmap.py -u <http://www.>***.com.cn/happystudy/happystudy_info.php?idnow=34
--file-read="/usr/local/apache/htdocs/index.php"[/align]

[align=left]sqlmap.py -u
<http://www.>***.com.cn/happystudy/happystudy_info.php?idnow=34 --file-read="/etc/passwd" [/align]

[align=left]

  

![image.png](https://image.3001.net/images/20180531/15277526562871.png!small)  

图12读取系统文件及其他文件

  

（2）获取数据库密码

sqlmap会将获取的文件自动保存到当前系统用户下C:\Users\john\\.sqlmap\output\www.****.com.cn\files，如图13所示，读取conn.php文件的内容，成功获取数据库root账号密码。

![image.png](https://image.3001.net/images/20180531/15277526648823.png!small)

  

图13读取源代码获取root密码

  
  
1.4艰难的后台地址获取  

1.使用havij对后台进行扫描

如图14所示，通过havij等工具对目标后台地址进行获取，在本例中获取的是普通用户的登录地址，未获取真正的后台地址。

![image.png](https://image.3001.net/images/20180531/15277526753031.png!small)

  
图14使用havij对后台地址进行扫描

  

2.通过google成功获取后台地址

后面使用百度对该url地址进行查询“site:somesite.com
后台管理”未能获取相关信息，但在google中成功获取其后台地址，如图15所示。有时候google[黑客技术](http://bbs.ichunqiu.com/forum-41-1.html)还是挺管用的。从url中可以看到该管理地址很难扫描获取。

![image.png](https://image.3001.net/images/20180531/15277526838422.png!small)

  

图15成功获取后台管理地址

  

3.获取真正的管理表

通过sqlmap对该数据库中所有的表进行查询，发现存在多个涉及密码的表，admin、admin_files、admin_groups、tb_admin，依次进行和密码破解，将其进行后台登陆，均为成功登录。后面通过读取登录地址的源代码成功获取，其真正的管理员表为tygb，如图16所示，通过sql-shell进行查询：select * from tygb

  

![image.png](https://image.3001.net/images/20180531/15277526901359.png!small)  

图16获取真正的管理表

  

4.登录后台管理

如图17所示，登录成功后，可以看到其cms系统存在多个系统，对每个管理入口进行查看和测试，虽然某些模块存在上传，经过测试，无写入权限。

  

![image.png](https://image.3001.net/images/20180531/15277526971768.png!small)  

图17登录后台进行管理

  

5.fckeditor漏洞验证

在后台中发现其使用了fckeditor编辑器，成功找到其fckeditor编辑器文件测试页面，并对其进行测试，如图18，有无文件权限问题，该漏洞无法利用。

  
![image.png](https://image.3001.net/images/20180531/15277527101848.png!small)

![image.png](https://image.3001.net/images/20180531/15277527165561.png!small)

  

图18文件上传漏洞无法利用

  

6.网站旁注漏洞利用失败

后面对该目标网站进行同IP地址域名反查，发现该IP下存在多个域名，通过仔细的核对，发现前面的sql注入点可以读取其数据库，通过获取后台密码，成功进入后台，但也无用，系统存在错误，fckeditor无法上传文件，也无法写入文件。

  

1.5php网站sql注入防御及总结  

1.渗透总结

（1）本次渗透主要在于对mysql+php架构下sql注入点注入漏洞sqlmap的利用

（2）利用sqlmap的文件读取和写入功能写入webshell

（3）有些情况下即使存在漏洞，也可能无法获取webshell

  

2.php网站sql注入防御

（1）过滤一些常见的数据库操作关键字,例如对select
,insert,update,delete,and,*等或通过系统函数addslashes对内容进行过滤。

（2）php配置文件php.ini中register_globals=off;设置为关闭状态

（3）对于sql语句加以封装,避免直接暴漏SQL语句

（4）开启PHP安全模式safe_mode=on

（5）打开magic_quotes_gpc来防止SQL注入,默认为关闭,开启后自动把用户提交sql查询语句进行转换把"'"转换成"\'"

（6）控制错误信息输出，关闭错误信息提示，将错误信息写到系统日志。

（7）网站安装waf防护软件

有问题大家可以留言哦，也欢迎大家到春秋论坛中来耍一耍
[>>>点击跳转](https://bbs.ichunqiu.com/portal.php?from=beef)  

