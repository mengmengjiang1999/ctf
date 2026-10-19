## 背景概述

**近日，深信服安全团队捕获到一起绕过杀毒软件的无文件攻击事件，被入侵的主机或服务器会被安装Mykings、Mirai、暗云等多种僵尸网络木马及挖矿程序，并且难以彻底清除。经分析排查，该木马通过弱口令爆破SQL
Server服务器后，利用sqlserver Transact-SQL存储C#编译恶意代码，通过MSSQL作业定时执行存储过程，在受害主机下载恶意程序。**

## 排查过程

排查主机上的恶意文件、启动项等，发现执行恶意脚本的WMI，功能是下载文件到本地执行：

![](https://image.3001.net/images/20190507/1557210107_5cd123fbe3cf0.png!small)

![](https://image.3001.net/images/20190507/1557210122_5cd1240a04a4b.png!small)

排查注册表启动项，存在一个BGClients，执行c:\windows\system32\wbem\123.bat，看起来十分可疑：

![](https://image.3001.net/images/20190507/1557210138_5cd1241a60347.png!small)

查看123.bat的内容，其中比较关键的操作是创建了几个隐藏目录，并且通过RegSvr32/Scrobj.dll来执行远程SCT脚本：

![](https://image.3001.net/images/20190507/1557210144_5cd12420a8987.png!small)

顺手逛一下查杀到恶意exe文件的目录，发现两个dvr后缀的文件，打开一看果不其然，包含了用于下载恶意文件的命令：

![](https://image.3001.net/images/20190507/1557210189_5cd1244d9eeea.png!small)

![](https://image.3001.net/images/20190507/1557210194_5cd124521166b.png!small)

启动项、注册表、WMI、进程、服务、计划任务都找了一圈，再没发现其他问题，于是把以上发现的问题项统统删除，结案！

那是不可能的。

cab.exe又出现了。

而且手动删掉的一堆乱七八糟全都回来了。

没辙了，只能放大招，通过安装监控，在恶意文件生成的时间节点附近排查监控日志。终于在恶意文件被实时监控拦截的时间节点发现了两条通过数据库进程执行了可疑的cmd命令日志，用于运行c:\windows\debug和c:\progra~1目录下的exe文件，由此推测数据库中存在恶意的执行计划：

![](https://image.3001.net/images/20190507/1557210512_5cd12590e13d7.png!small)

![](https://image.3001.net/images/20190507/1557210519_5cd125978c79b.png!small)

对数据库作业进行排查，果然存在一大堆奇怪的计划：

![](https://image.3001.net/images/20190507/1557210525_5cd1259d643e8.png!small)

逐条查看作业步骤，这功能丰富啊，由于内容过多，下面将部分作业对应的命令或功能整理出来：

![](https://image.3001.net/images/20190507/1557210544_5cd125b0e26d1.png!small)

可以看到，上一次排查时发现的恶意文件、WMI、注册表等项都可以在表格中找到生成语句，并且还有一些没有排查到的文件，可能被防病毒软件识别清除了。这回可算是结案了吧，先对比作业中的语句将主机上可能存在的残留项都排查一遍，然后删除这些作业。

事情果然没有想象中那么简单，某一个风轻云淡的下午四点，cabs.exe又双叒叕回来了，堪称病毒界的灰太狼。

四点，这个时间点好像似曾相识，每次防病毒软件弹出查杀到cabs.exe的时间好像都是四点，监控日志中数据库进程执行了恶意cmd命令的时间也是四点，直觉告诉我们，SQL作业中肯定还有问题，于是把目光投向了上一次漏掉的数据库作业，在sqlrc中发现了一条执行存储过程的命令，运行一下：

![](https://image.3001.net/images/20190507/1557210565_5cd125c554de3.png!small)

这不就是我们苦苦寻找的cabs.exe么！原来是隐藏在存储过程中，执行了ExecCode对象的内容：

![](https://image.3001.net/images/20190507/1557210580_5cd125d42a95d.png!small)

![](https://image.3001.net/images/20190507/1557210705_5cd126516dd52.png!small)

通过查询Transact-SQL中的项，发现执行的对象ExecCode：

![](https://image.3001.net/images/20190507/1557210594_5cd125e20d5c5.png!small)

再通过对象名称查询sys.assembly_files表，找到ExecCode对应的content内容，从“4D5A”来看，这应该就是我们要找的目标：

![](https://image.3001.net/images/20190507/1557210600_5cd125e843cea.png!small)

## 病毒文件分析

将十六进制数据拷贝出来转换为PE文件，是一个用C#编写的DLL文件，通过MyDownloadFile方法读取指定URL网页的内容：

![](https://image.3001.net/images/20190507/1557210692_5cd12644f0a12.png!small)

该URL的内容如下，也是两个下载链接以及对应保存的完整路径，其中ok.exe地址已失效，ups.rar就是我们发现的cabs.exe：

![](https://image.3001.net/images/20190507/1557210709_5cd12655922cc.png!small)

MyDownloadFile方法的执行过程如下：

![](https://image.3001.net/images/20190507/1557210738_5cd1267280652.png!small)

下载的cabs.exe是一个下载器，会下载Mykings、Mirai、暗云、挖矿等多个恶意模块到受害主机，功能十分复杂：

![](https://image.3001.net/images/20190507/1557210752_5cd1268037bb0.png!small)

## 解决方案

1.删除SQL Server中的恶意作业和存储过程；

2.删除主机中存在的恶意程序、WMI、注册表项等，详见下表：

![](https://image.3001.net/images/20190507/1557210764_5cd1268c34b68.png!small)

3\. SQL Server使用强密码；

4.深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

> 64位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>
>
> 32位系统下载链接：<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**

