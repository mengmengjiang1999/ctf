## **0x0** **背景**

**近日，深信服安全团队接到客户本地的安全感知报警，提示有恶意的CC访问连接报警，访问恶意域名down.mys2018.xyz达到了1057次、访问my2018.zxy达到了490次主机直接被标记为了已失陷，经过较多的杀毒软件查杀均未查杀出异常，后续经过相关的排查发现服务器存在较大的安全隐患，与Myking团伙有较大的关联。**

##  **0x1** **总体情况**

多方面的分析发现，客户本地存在较多的恶意脚本与病毒文件根据现象情况梳理与日志分析、结合对一些进程内存的分析等多方面检测定义为多次恶意入侵的安全事件。

##  **0x2** **进程检查**

进程当中发现了大量恶意的wscript.exe的进程数量约为30多个调用，均为 **最高权限**
通过系统命令调用参数文件为C:\users\public\documents\1.vbs的执行脚本，且该进程的父进程为本地运行sqlserver.exe数据库进程。

![3.png](https://image.3001.net/images/20181123/1542964371_5bf7c49325482.png!small)

打开1.vbs的内容进行代码分析发现此脚本是通过调用本地的wscript.exe 从互联网上下载恶意的挖矿组件进行虚拟挖矿的程序。

核心代码如下：

![4.png](https://image.3001.net/images/20181123/1542964379_5bf7c49bee625.png!small)

url路径为：[http://q.112adfdae.tk/&wenjian](http://q.112adfdae.tk/&wenjian)；

powered.exe为挖矿的主要进程，config.json为挖矿的配置文件；之前有分析过类似的文件这里不多做介绍。

##  **0x3** **开机启动项**

通过对开机启动项目的检查也通用发现了一个叫fuckyoumm2_consumerde的WMI项目：

![5.png](https://image.3001.net/images/20181123/1542964391_5bf7c4a754a4d.png!small)

启动内容如下主要是从<http://down.mys2018.xyz:280/psa.jpg>下载内容并保存为指定路径下C:\windows\ps.exe并执行：

![6.png](https://image.3001.net/images/20181123/1542964401_5bf7c4b195f7e.png!small)

在注册表里面的开机启动项目发现了一个clean.vbs的异常项目：

![7.png](https://image.3001.net/images/20181123/1542964414_5bf7c4be95da0.png!small)

通过对内容的分析发现此为一个针对redis入侵的一个payload：

![8.png](https://image.3001.net/images/20181123/1542964429_5bf7c4cde796b.png!small)

通过对注册表的检查一个诡异的bat文件出现在眼前，路径为：

    
    
    C:\windows\system32\wbem\123.bat

![9.png](https://image.3001.net/images/20181123/1542964440_5bf7c4d8a464d.png!small)

主要内容如下主要功能也是从远端下载样本回来并执行：

![10.png](https://image.3001.net/images/20181123/1542964452_5bf7c4e43c656.png!small)

##  **0x4** **攻击溯源**

通过对sqlserver的检查发现该数据库一直遭受到来自互联网的暴力破解攻击主要用户为sa且xp_shell功能已经处于开启状态，由于日志不全面暂时无法确认是具体时间点开启。

![11.png](https://image.3001.net/images/20181123/1542964464_5bf7c4f0072a4.png!small)

![12.png](https://image.3001.net/images/20181123/1542964479_5bf7c4ff27b1c.png!small)

同时在web系统的目录下面发现了一个多功能的大马webshell为sqzr.jsp上传时间为2018年6月6日。

![13.png](https://image.3001.net/images/20181123/1542964492_5bf7c50c2d393.png!small)

![14.png](https://image.3001.net/images/20181123/1542964502_5bf7c5166af85.png!small)

在redis的目录下面也发现黑客上传的SSH登录的Key，这个操作可以说很6了毕竟这是windows系统。

![15.png](https://image.3001.net/images/20181123/1542964512_5bf7c520001d9.png!small)

通过对本地的端口开放情况进行检查发现redis的进程一直保持着较多的通信，同时检查了配置文件发现未开启授权访问。

![16.png](https://image.3001.net/images/20181123/1542964521_5bf7c52957953.png!small)

##  **0x5** **清理**

1.删除系统目录下的1.vbs 123.bat clean.vbs等恶意脚本；

2.删除web系统目录下的helloworld.jar 与helloworld目录的webshell后门；

3.删除黑客上传的root文件；

4.删除fuckyoumm2_consumerde、clean.vbs、123.bat的开机启动项。

##  **0x6** **加固与建议**

1.添加redis的访问密码、同时设置redis的访问控制；

2.修复Openfire的安全漏洞升级到最新版本或者更新补丁包；

3.添加sqlserver的安全加固设置强密码策略与访问控制策略，关闭危险的xp_shell的命令执行功能；

4.深信服EDR产品、下一代防火墙等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测。其中EDR产品，采用深信服SAVE智能安全检测引擎，通过人工智能自主学习自动识别未知威胁，无需任何升级即可自主检测查杀病毒最新变种。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**

